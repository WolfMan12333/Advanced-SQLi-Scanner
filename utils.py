# utils.py
import os
import re
import json
import random
from urllib.parse import urlencode

# List of common User-Agent headers to help bypass WAFs and appear like different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Android 11; Mobile; rv:83.0)"
]

# Returns a random User-Agent header for each HTTP request
def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

# Extracts variable/parameter names from a source code file using regex patterns per language
def extract_parameters_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    patterns = [
        r'\$_(GET|POST|REQUEST)\[["\']?(\w+)["\']?\]',      # PHP
        r'request\.args\.get\(["\'](\w+)["\']\)',           # Flask (Python)
        r'request\.form\["(\w+)"\]',                        # Flask forms
        r'request\.GET\.get\(["\'](\w+)["\']\)',            # Django
        r'request\.POST\.get\(["\'](\w+)["\']\)',           # Django
        r'params\[:(\w+)\]',                                # Ruby on Rails
        r'req\.query\.(\w+)',                               # Node.js Express
        r'req\.body\.(\w+)',                                # Node.js Express body
        r'\$request->input\(["\'](\w+)["\']\)',             # Laravel
        r'\binput\s*\(\s*["\'](\w+)["\']\s*\)',             # General pattern
        r'name=["\'](\w+)["\']',                            # HTML form inputs
    ]

    parameters = set()
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                parameters.add(match[-1])
            else:
                parameters.add(match)
    return parameters

# Generates full SQLi payload URLs based on base URL, found parameters, and payload list
def generate_payloads(base_url, parameters, payloads):
    urls = []
    for param in parameters:
        for payload in payloads:
            query = {param: payload}
            url = f"{base_url}?{urlencode(query)}"
            urls.append(url)
    print(f"Generated {len(urls)} attack URLs for testing.")
    return urls

# Saves scan.log and HTML summary report with all payload URLs
def save_log_and_report(urls, project_name):
    project_dir = os.path.join("reports", project_name)
    os.makedirs(project_dir, exist_ok=True)

    log_path = os.path.join(project_dir, "scan.log")
    report_path = os.path.join(project_dir, "report.html")

    with open(log_path, 'w') as f:
        for url in urls:
            f.write(url + '\n')

    with open(report_path, 'w') as f:
        f.write("<html><body><h1>Payload URLs</h1><ul>")
        for url in urls:
            f.write(f"<li>{url}</li>")
        f.write("</ul></body></html>")

    return log_path, report_path
