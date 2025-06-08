import os
import re
import json
import random
import requests
from urllib.parse import urlencode, urljoin
from utils import extract_parameters_from_file, generate_payloads, save_log_and_report, random_headers

# Analyze source code to generate attack URLs and scan log
# This function processes files in a given folder, extracts parameters,
# and creates a list of potential SQLi attack URLs using given payloads

def analyze_source_code(folder_path, base_url, payload_file, project_name):
    parameters = set()
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.php', '.html', '.js', '.py', '.rb', '.java', '.asp', '.aspx')):
                file_path = os.path.join(root, file)
                params = extract_parameters_from_file(file_path)
                parameters.update(params)

    with open(payload_file, 'r') as f:
        payloads = [line.strip() for line in f if line.strip()]

    #urls = generate_payloads(base_url, parameters, payloads)
    urls = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.php', '.html', '.js', '.py', '.rb', '.java', '.asp', '.aspx')):
                file_path = os.path.join(root, file)
                params = extract_parameters_from_file(file_path)
                relative_path = os.path.relpath(file_path, folder_path).replace("\\", "/")
                full_url = urljoin(base_url + "/", relative_path)

                for param in params:
                    for payload in payloads:
                        query = urlencode({param: payload})
                        urls.append(f"{full_url}?{query}")

    log_path, report_path = save_log_and_report(urls, project_name)
    return log_path, report_path

# Run real application testing using the attack URLs from scan.log
# This function sends requests to the URLs and saves responses for reporting

def test_real_application(log_path, delay, threads, project_name):
    from time import sleep
    from concurrent.futures import ThreadPoolExecutor

    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Scan log not found: {log_path}")

    with open(log_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    results = []

    def send_request(url):
        try:
            headers = random_headers()
            r = requests.get(url, headers=headers, timeout=10)
            status = r.status_code
            content = r.text[:300]
            results.append({"url": url, "status": status, "snippet": content})
        except Exception as e:
            results.append({"url": url, "status": "ERROR", "error": str(e)})
        sleep(delay / 1000)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(send_request, urls)

    results_path = os.path.join("reports", project_name, "results.json")
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    html_path = os.path.join("reports", project_name, "report.html")
    with open(html_path, 'w') as f:
        f.write("<html><body><h1>Scan Results</h1><ul>")
        for r in results:
            f.write(f"<li><b>{r['url']}</b> - Status: {r.get('status')}<br>")
            if 'snippet' in r:
                f.write(f"<pre>{r['snippet']}</pre>")
            elif 'error' in r:
                f.write(f"<i>{r['error']}</i>")
            f.write("</li><hr>")
        f.write("</ul></body></html>")

    return results_path, html_path
