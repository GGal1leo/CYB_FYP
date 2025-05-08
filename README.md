# AI-Powered Cyber Incident Monitoring Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A comprehensive threat monitoring system leveraging AI and threat intelligence to automate cyber incident analysis.

## Features

- **Automated Threat Data Collection** from NewsNow and RSS feeds
- **AI-Powered IOC Analysis** using Google Gemini
- **Threat Intelligence Integration** with ThreatFox API
- **MITRE ATT&CK® Framework Mapping**
- **Real-time Web Dashboard** with WebSocket updates
- **PCAP Analysis** for IOC detection
- **Automated HTML Reporting**
- **Command Line Interface (CLI)** support

## Installation

### Prerequisites

- Python 3.8+
- [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) (Wireshark CLI)
- Google Gemini API key

### Setup

```bash
# Clone repository
git clone https://github.com/GGal1leo/CYB_FYP.git
cd CYB_FYP

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Gemini API key
```

## Usage

### Web Interface

```bash
uvicorn web_monitor:app --reload
```

Access dashboard at: <http://localhost:8000>

### CLI Monitoring

```bash
# NewsNow monitoring
python cyber_monitor.py

# RSS feed monitoring
python rss_monitor.py
```

## Project Structure

```text
CYB_FYP/
├── cyber_monitor.py       # Article monitoring and processing
├── ioc_analyzer.py        # Core analysis engine
├── web_monitor.py         # Web interface and API
├── rss_monitor.py         # RSS feed monitoring
├── templates/             # Web interface templates
├── static/                # CSS/JS assets
├── cache/                 # MITRE ATT&CK® data cache
└── requirements.txt       # Dependencies
```

## Contributing

Contributions are welcome! Please open an issue first to discuss proposed changes.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/your-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin feature/your-feature)
5. Open a Pull Request

License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details
