# Advanced SQLi Scanner (GUI-Based)

An advanced SQL injection vulnerability scanner with a clean PyQt6 interface. Designed for both **source code analysis** and **real-world testing**, it supports detection of input parameters in multiple languages and generates full SQLi payload URLs. The tools is till underconstruction as I have still lots of ideas to make it better.

## 🚀 Features

- 🔍 **Source Code Scanner**  
  Detects input parameters in:
  - PHP (`$_GET`, `$_POST`, `$_REQUEST`)
  - Python (Flask, Django)
  - Node.js (Express)
  - Ruby on Rails
  - HTML forms
  - Laravel
- 🧪 **Real Application Tester**  
  Sends payloads from the source scan to a live web application.
- 🧵 Multithreaded HTTP requests with delay configuration.
- 🧠 Randomized User-Agent headers for WAF evasion.
- 📄 Auto-generated `scan.log` and clean `report.html` per project.
- 🖥️ Simple, intuitive PyQt6 interface with logs and progress display.

## 1. Clone the repository
git clone https://github.com/yourusername/advanced-sqli-scanner.git
cd advanced-sqli-scanner

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Run the application
python sqli_scanner_gui.py


## 🖥️ GUI Overview

### Input Fields:
- **Project Name**: Directory name under `reports/`
- **Source Code Folder**: Folder containing app files to scan
- **Base URL**: Target application URL (e.g. `http://localhost:5000`)
- **Payloads File**: File with one SQLi payload per line
- **Delay (ms)**: Delay between HTTP requests (default: 200ms)
- **Threads**: Number of threads for testing (default: 1)

### Buttons:
- 🔎 **Start Source Code Scan**  
  Scans selected folder and generates payload URLs.
- 🧪 **Start Real Testing**  
  Sends requests to URLs from `scan.log`.

---

## ✅ Example Usage

1. Launch the GUI:
```bash
python sqli_scanner_gui.py
