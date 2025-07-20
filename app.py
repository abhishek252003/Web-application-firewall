from flask import Flask, render_template, jsonify
from datetime import datetime
import time

app = Flask(__name__)
start_time = time.time()
request_count = 0
recent_requests = []

@app.route('/')
def home():
    global request_count
    request_count += 1
    recent_requests.append({'path': '/', 'timestamp': datetime.now().isoformat()})
    if len(recent_requests) > 50:
        recent_requests.pop(0)
    return render_template('home.html', request_count=request_count)

@app.route('/<path:path>')
def catch_all(path):
    global request_count
    request_count += 1
    recent_requests.append({'path': path, 'timestamp': datetime.now().isoformat()})
    if len(recent_requests) > 50:
        recent_requests.pop(0)
    return render_template('path.html', path=path)

@app.route('/status')
def status():
    uptime_seconds = int(time.time() - start_time)
    return render_template('status.html', uptime=uptime_seconds, request_count=request_count)

@app.route('/api/requests')
def api_requests():
    return jsonify(recent_requests)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
