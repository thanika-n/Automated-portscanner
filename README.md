# PortScan Pro 🔒

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A modern, full-featured web application for network port scanning with an intuitive UI, real-time results, and comprehensive scan history management.

![PortScan Pro Interface](https://via.placeholder.com/800x400/0a0e27/00ff88?text=PortScan+Pro+Interface)

## ✨ Features

- 🎯 **Dual Scan Modes**: Quick scan (18 common ports) or custom port selection
- 🌐 **IP & Hosting Detection**: Automatic resolution with provider and location info
- 📊 **Real-time Results**: Live scanning with open/closed port categorization
- 💾 **Scan History**: Persistent SQLite database with full CRUD operations
- 🎨 **Modern UI**: Dark cybersecurity theme with smooth animations
- ⚡ **Fast & Accurate**: Optimized 3s timeout with 20 concurrent workers
- 🛡️ **Error Handling**: Graceful handling of invalid domains and network errors
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/port-scanner.git
   cd port-scanner
   ```

2. **Install dependencies**

   **Using virtualenv**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the web interface**
   
   Open your browser and navigate to: `http://localhost:5000`

## 📖 Usage

### Quick Scan

1. Enter a target URL or domain (e.g., `google.com`)
2. Select **Quick Scan** (default)
3. Click **Start Scanning**
4. View results: IP address, hosting info, open/closed ports

### Custom Scan

1. Enter a target URL or domain
2. Select **Custom Scan**
3. Enter comma-separated port numbers (e.g., `80, 443, 8080, 3306`)
4. Click **Start Scanning**
5. View your custom port results

### Scan History

- Click **History** to view all previous scans
- Click any scan to view full details
- Delete scans using the trash icon
- Click the logo to return to the scanner

## 🛠️ Project Structure

```
port-scanner/
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── CHANGELOG.md           # Version history
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── styles.css         # CSS styling
│   └── script.js          # Frontend JavaScript
└── port_scanner.db        # SQLite database (auto-generated)
```

## 🔍 Port Reference

### Common Ports Scanned (Quick Scan)

| Port  | Service      | Description              |
|-------|--------------|--------------------------|
| 21    | FTP          | File Transfer Protocol   |
| 22    | SSH          | Secure Shell             |
| 25    | SMTP         | Email Sending            |
| 53    | DNS          | Domain Name System       |
| 80    | HTTP         | Web Traffic              |
| 110   | POP3         | Email Retrieval          |
| 143   | IMAP         | Email Access             |
| 443   | HTTPS        | Secure Web Traffic       |
| 3306  | MySQL        | MySQL Database           |
| 3389  | RDP          | Remote Desktop           |
| 5432  | PostgreSQL   | PostgreSQL Database      |
| 8080  | HTTP-Alt     | Alternative HTTP         |

Full list: 21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443

## ⚙️ Configuration

### Changing the Default Port

Edit `app.py` (line 165):
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your preferred port
```

### Adjusting Scan Timeout

Edit `app.py` (line 60):
```python
def scan_port(ip, port, timeout=3):  # Change timeout value (in seconds)
```

### Modifying Concurrent Workers

Edit `app.py` (line 68):
```python
def scan_ports(ip, ports, max_workers=20):  # Adjust worker count
```

### Adding Default Ports

Edit `app.py` (lines 18-36):
```python
IMPORTANT_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 143, 443,
    # Add your ports here
    27017,  # MongoDB
    6379,   # Redis
]
```

## 🔧 Troubleshooting

### Port Shows Closed But Should Be Open
- Check firewall settings
- Verify network connectivity
- Target may be blocking scans
- Increase timeout in `app.py` if needed

### Input Fields Turn White
Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R) to reload CSS.

## 🎨 Technical Stack

**Backend:**
- Flask 3.0.0
- Python Socket Library
- SQLite3
- Concurrent Futures (Threading)

**Frontend:**
- HTML5
- CSS3 (Custom Properties, Animations)
- Vanilla JavaScript (ES6+)
- Google Fonts (JetBrains Mono, Outfit)

**API:**
- ip-api.com (Geolocation & hosting info)

## 🚦 Performance

- **Quick Scan**: 3-8 seconds (18 ports)
- **Custom Scan**: 2-4 seconds (10 ports)
- **Timeout**: 3 seconds per port
- **Concurrency**: 20 simultaneous connections
- **Database**: Lightweight SQLite with instant queries

## 🔒 Security & Legal

### Important Notes

⚠️ **This tool is for educational and authorized testing only.**

- Only scan systems you own or have explicit permission to test
- Unauthorized port scanning may violate laws in your jurisdiction
- Some networks/ISPs may flag or block scanning activity
- Tool uses development mode - not suitable for production deployment
- No authentication implemented - do not expose publicly

### Best Practices

- Use in controlled environments
- Respect `robots.txt` and terms of service
- Rate limit your scans
- Scan during off-peak hours
- Document authorization before scanning

## 📊 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Opera (latest)
- ⚠️ Internet Explorer (not supported)

## 🐛 Known Issues

- Firewall may block outbound connections
- Cloudflare/CDN may show proxy results instead of origin
- Rate limiting may occur on hosting provider API
- Some ports may timeout on high-latency connections

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- IP data from [ip-api.com](https://ip-api.com/)
- Icons and fonts from [Google Fonts](https://fonts.google.com/)
- Inspired by modern cybersecurity tools

## 🌟 Star 

If you find this project useful, please consider giving it a ⭐️!

---

**Made with ❤️ for the security community**

**Remember: Scan responsibly and ethically! 🔐**
