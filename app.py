from flask import Flask, render_template, request, jsonify
import socket
import concurrent.futures
from datetime import datetime
import sqlite3
import json
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Common important ports
IMPORTANT_PORTS = [
    21,    # FTP
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    80,    # HTTP
    110,   # POP3
    143,   # IMAP
    443,   # HTTPS
    465,   # SMTPS
    587,   # SMTP
    993,   # IMAPS
    995,   # POP3S
    3306,  # MySQL
    3389,  # RDP
    5432,  # PostgreSQL
    8080,  # HTTP Alternate
    8443,  # HTTPS Alternate
]

# Initialize database
def init_db():
    conn = sqlite3.connect('port_scanner.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT NOT NULL,
                  ip_address TEXT,
                  hosting_provider TEXT,
                  scan_type TEXT,
                  open_ports TEXT,
                  closed_ports TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_ip_address(url):
    """Get IP address from URL"""
    try:
        # Parse URL to get hostname
        parsed = urlparse(url)
        hostname = parsed.netloc if parsed.netloc else parsed.path
        # Remove port if present
        hostname = hostname.split(':')[0]
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception as e:
        return None

def get_hosting_provider(ip):
    """Get hosting provider information"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return {
                'org': data.get('org', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'Unknown')
            }
    except:
        pass
    return {'org': 'Unknown', 'isp': 'Unknown', 'country': 'Unknown', 'city': 'Unknown'}

def scan_port(ip, port, timeout=3):
    """Scan a single port with improved detection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Set socket options for better detection
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        result = sock.connect_ex((ip, port))
        sock.close()
        
        return port, result == 0
    except:
        return port, False

def scan_ports(ip, ports, max_workers=20):
    """Scan multiple ports concurrently"""
    open_ports = []
    closed_ports = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(scan_port, ip, port): port for port in ports}
        for future in concurrent.futures.as_completed(future_to_port):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)
            else:
                closed_ports.append(port)
    
    return sorted(open_ports), sorted(closed_ports)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.json
        url = data.get('url')
        scan_type = data.get('scan_type', 'default')
        custom_ports = data.get('custom_ports', [])
        
        # Get IP address
        ip = get_ip_address(url)
        if not ip:
            return jsonify({'error': 'Unable to resolve IP address'}), 400
        
        # Get hosting provider
        hosting_info = get_hosting_provider(ip)
        
        # Determine ports to scan
        if scan_type == 'default':
            ports_to_scan = IMPORTANT_PORTS
        else:
            ports_to_scan = custom_ports
        
        # Scan ports
        open_ports, closed_ports = scan_ports(ip, ports_to_scan)
        
        # Save to database
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('port_scanner.db')
        c = conn.cursor()
        c.execute('''INSERT INTO scans 
                     (url, ip_address, hosting_provider, scan_type, open_ports, closed_ports, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (url, ip, json.dumps(hosting_info), scan_type, 
                   json.dumps(open_ports), json.dumps(closed_ports), timestamp))
        scan_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'scan_id': scan_id,
            'url': url,
            'ip_address': ip,
            'hosting_provider': hosting_info,
            'open_ports': open_ports,
            'closed_ports': closed_ports,
            'timestamp': timestamp
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect('port_scanner.db')
        c = conn.cursor()
        c.execute('SELECT * FROM scans ORDER BY timestamp DESC')
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'url': row[1],
                'ip_address': row[2],
                'hosting_provider': json.loads(row[3]),
                'scan_type': row[4],
                'open_ports': json.loads(row[5]),
                'closed_ports': json.loads(row[6]),
                'timestamp': row[7]
            })
        
        return jsonify(history)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/<int:scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    try:
        conn = sqlite3.connect('port_scanner.db')
        c = conn.cursor()
        c.execute('DELETE FROM scans WHERE id = ?', (scan_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/<int:scan_id>', methods=['GET'])
def get_scan_details(scan_id):
    try:
        conn = sqlite3.connect('port_scanner.db')
        c = conn.cursor()
        c.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify({
            'id': row[0],
            'url': row[1],
            'ip_address': row[2],
            'hosting_provider': json.loads(row[3]),
            'scan_type': row[4],
            'open_ports': json.loads(row[5]),
            'closed_ports': json.loads(row[6]),
            'timestamp': row[7]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
