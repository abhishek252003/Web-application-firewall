from datetime import datetime
import sqlite3

def init_db():
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  ip TEXT,
                  method TEXT,
                  path TEXT,
                  body TEXT,
                  status TEXT,
                  reason TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist
                 (ip TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  pattern TEXT NOT NULL,
                  description TEXT)''')
    conn.commit()
    conn.close()

def log_request(ip, method, path, body, status, reason):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''INSERT INTO logs (timestamp, ip, method, path, body, status, reason)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (timestamp, ip, method, path, body, status, reason))
    conn.commit()
    conn.close()

def is_blacklisted(ip):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('SELECT ip FROM blacklist WHERE ip = ?', (ip,))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_to_blacklist(ip):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO blacklist (ip) VALUES (?)', (ip,))
    conn.commit()
    conn.close()

def remove_from_blacklist(ip):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('DELETE FROM blacklist WHERE ip = ?', (ip,))
    conn.commit()
    conn.close()

def get_blacklist():
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('SELECT ip FROM blacklist')
    blacklist = [row[0] for row in c.fetchall()]
    conn.close()
    return blacklist

def add_rule(pattern, description):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('INSERT INTO rules (pattern, description) VALUES (?, ?)', (pattern, description))
    conn.commit()
    conn.close()

def get_rules():
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('SELECT id, pattern, description FROM rules')
    rules = [{'id': row[0], 'pattern': row[1], 'description': row[2]} for row in c.fetchall()]
    conn.close()
    return rules

def delete_rule(rule_id):
    conn = sqlite3.connect('waf.db')
    c = conn.cursor()
    c.execute('DELETE FROM rules WHERE id = ?', (rule_id,))
    conn.commit()
    conn.close()