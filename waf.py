import http.client
import re
import time
import sqlite3
from urllib.parse import urlparse, parse_qs, unquote
from collections import defaultdict
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from rules import is_malicious
from db import init_db, log_request, is_blacklisted, add_to_blacklist, remove_from_blacklist, get_blacklist, get_rules, add_rule, delete_rule

app = Flask(__name__)

# Rate limiting storage
request_counts = defaultdict(lambda: [0, time.time()])

def rate_limit(ip):
    now = time.time()
    count, last_reset = request_counts[ip]
    if now - last_reset > 60:
        request_counts[ip] = [0, now]
        count = 0
    request_counts[ip][0] += 1
    return count <= 50

def forward_request(method, path, headers, body):
    try:
        parsed = urlparse(path)
        conn = http.client.HTTPConnection('localhost', 5000)
        conn.request(method, parsed.path + (f'?{parsed.query}' if parsed.query else ''), body, headers)
        response = conn.getresponse()
        return response.status, response.read()
    except Exception as e:
        return 500, f"Server error: {str(e)}".encode()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def waf(path):
    ip = request.remote_addr
    method = request.method
    body = request.get_data(as_text=True) if method == 'POST' else ''
    # Decode query string for proper matching
    parsed = urlparse(request.full_path)
    query = unquote(parsed.query)
    request_data = f"{method} {parsed.path} {query} {body}".lower()

    init_db()

    if is_blacklisted(ip):
        log_request(ip, method, parsed.path, body, 'blocked', 'blacklisted')
        return jsonify({'error': 'Blocked: IP blacklisted'}), 403

    if not rate_limit(ip):
        log_request(ip, method, parsed.path, body, 'blocked', 'rate limit exceeded')
        add_to_blacklist(ip)
        return jsonify({'error': 'Blocked: Rate limit exceeded'}), 429

    attack_type = is_malicious(request_data)
    if attack_type:
        log_request(ip, method, parsed.path, body, 'blocked', f'malicious: {attack_type}')
        add_to_blacklist(ip)
        return jsonify({'error': f'Blocked: Malicious request ({attack_type})'}), 403

    status, response = forward_request(method, path, dict(request.headers), body)
    log_request(ip, method, parsed.path, body, 'allowed', '')
    if isinstance(response, bytes):
        return response, status
    return response, status

@app.route('/dashboard/<path:filename>')
def serve_dashboard(filename):
    return send_from_directory('dashboard', filename)

@app.route('/api/logs')
def get_logs():
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100')
    logs = [{'id': row[0], 'timestamp': row[1], 'ip': row[2], 'method': row[3],
             'path': row[4], 'body': row[5], 'status': row[6], 'reason': row[7]}
            for row in c.fetchall()]
    conn.close()
    return jsonify(logs)

@app.route('/api/blacklist', methods=['GET'])
def list_blacklist():
    return jsonify(get_blacklist())

@app.route('/api/blacklist', methods=['POST'])
def manage_blacklist():
    ip = request.json.get('ip')
    if ip:
        add_to_blacklist(ip)
        return jsonify({'status': f'IP {ip} blacklisted'})
    return jsonify({'error': 'Invalid IP'}), 400

@app.route('/api/blacklist/<ip>', methods=['DELETE'])
def remove_blacklist(ip):
    if is_blacklisted(ip):
        remove_from_blacklist(ip)
        return jsonify({'status': f'IP {ip} removed from blacklist'})
    return jsonify({'error': 'IP not found'}), 404

@app.route('/api/rules', methods=['GET'])
def list_rules():
    return jsonify(get_rules())

@app.route('/api/rules', methods=['POST'])
def create_rule():
    data = request.json
    pattern = data.get('pattern')
    description = data.get('description', '')
    if not pattern:
        return jsonify({'error': 'Pattern is required'}), 400
    try:
        re.compile(pattern)
        add_rule(pattern, description)
        return jsonify({'status': 'Rule added'})
    except re.error:
        return jsonify({'error': 'Invalid regex pattern'}), 400

@app.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def remove_rule(rule_id):
    delete_rule(rule_id)
    return jsonify({'status': 'Rule deleted'})

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('SELECT reason, COUNT(*) FROM logs WHERE reason != "" GROUP BY reason')
    attack_counts = {row[0]: row[1] for row in c.fetchall()}
    c.execute('SELECT status, COUNT(*) FROM logs GROUP BY status')
    status_counts = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return jsonify({
        'attacks': attack_counts,
        'status': status_counts
    })

if __name__ == '__main__':
    print("WAF running on port 8081...")
    app.run(port=8081)