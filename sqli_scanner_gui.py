import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QSpinBox, QTabWidget, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from advanced_sqli_scanner import analyze_source_code, test_real_application

class ScanThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)

    def __init__(self, source_folder, base_url, payload_file, project_name):
        super().__init__()
        self.source_folder = source_folder
        self.base_url = base_url
        self.payload_file = payload_file
        self.project_name = project_name

    def run(self):
        try:
            log_path, report_path = analyze_source_code(self.source_folder, self.base_url, self.payload_file, self.project_name)
            self.finished.emit(log_path, report_path)
        except Exception as e:
            self.finished.emit("", f"Error: {e}")

class TestThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)

    def __init__(self, log_path, delay_ms, threads, project_name):
        super().__init__()
        self.log_path = log_path
        self.delay_ms = delay_ms
        self.threads = threads
        self.project_name = project_name

    def progress_callback(self, val):
        self.progress.emit(val)

    def run(self):
        try:
            log_path, report_path = test_real_application(self.log_path, self.delay_ms, self.threads, self.project_name, self.progress_callback)
            self.finished.emit(log_path, report_path)
        except Exception as e:
            self.finished.emit("", f"Error: {e}")

class SQLiScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced SQLi Scanner MVP")
        self.setGeometry(100, 100, 900, 600)

        self.project_name_input = QLineEdit()
        self.project_name_input.setText("default_project")

        self.source_folder_input = QLineEdit()
        self.source_folder_btn = QPushButton("Browse")
        self.source_folder_btn.clicked.connect(self.browse_source_folder)

        self.base_url_input = QLineEdit()
        self.base_url_input.setText("http://localhost")

        self.payload_file_input = QLineEdit()
        self.payload_file_btn = QPushButton("Browse")
        self.payload_file_btn.clicked.connect(self.browse_payload_file)

        self.delay_input = QSpinBox()
        self.delay_input.setRange(0, 10000)
        self.delay_input.setValue(200)

        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 50)
        self.threads_input.setValue(1)

        self.scan_btn = QPushButton("Start Source Code Scan")
        self.scan_btn.clicked.connect(self.start_scan)

        self.test_btn = QPushButton("Start Real Testing")
        self.test_btn.clicked.connect(self.start_test)
        self.test_btn.setEnabled(False)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()

        # Project name
        pn_layout = QHBoxLayout()
        pn_layout.addWidget(QLabel("Project Name:"))
        pn_layout.addWidget(self.project_name_input)
        layout.addLayout(pn_layout)

        # Source folder
        sf_layout = QHBoxLayout()
        sf_layout.addWidget(QLabel("Source Code Folder:"))
        sf_layout.addWidget(self.source_folder_input)
        sf_layout.addWidget(self.source_folder_btn)
        layout.addLayout(sf_layout)

        # Base URL
        bu_layout = QHBoxLayout()
        bu_layout.addWidget(QLabel("Base URL:"))
        bu_layout.addWidget(self.base_url_input)
        layout.addLayout(bu_layout)

        # Payload file
        pf_layout = QHBoxLayout()
        pf_layout.addWidget(QLabel("Payloads File:"))
        pf_layout.addWidget(self.payload_file_input)
        pf_layout.addWidget(self.payload_file_btn)
        layout.addLayout(pf_layout)

        # Delay and Threads
        dt_layout = QHBoxLayout()
        dt_layout.addWidget(QLabel("Delay (ms):"))
        dt_layout.addWidget(self.delay_input)
        dt_layout.addWidget(QLabel("Threads:"))
        dt_layout.addWidget(self.threads_input)
        layout.addLayout(dt_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.test_btn)
        layout.addLayout(btn_layout)

        # Log view
        layout.addWidget(QLabel("Log / Output:"))
        layout.addWidget(self.log_view)

        self.setLayout(layout)

        self.scan_thread = None
        self.test_thread = None

        self.latest_scan_log = None

    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Code Folder")
        if folder:
            self.source_folder_input.setText(folder)

    def browse_payload_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Payloads File")
        if file:
            self.payload_file_input.setText(file)

    def start_scan(self):
        project_name = self.project_name_input.text().strip()
        source_folder = self.source_folder_input.text().strip()
        base_url = self.base_url_input.text().strip()
        payload_file = self.payload_file_input.text().strip()

        if not all([project_name, source_folder, base_url, payload_file]):
            self.log_view.append("Please fill all input fields before scanning.")
            return

        self.log_view.append("Starting source code scan...")
        self.scan_btn.setEnabled(False)
        self.test_btn.setEnabled(False)

        self.scan_thread = ScanThread(source_folder, base_url, payload_file, project_name)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.start()

    def on_scan_finished(self, log_path, report_path):
        if not log_path:
            self.log_view.append(f"Scan error: {report_path}")
        else:
            self.log_view.append(f"Scan completed. Log saved: {log_path}")
            self.log_view.append(f"Report saved: {report_path}")
            self.latest_scan_log = log_path
            self.test_btn.setEnabled(True)
        self.scan_btn.setEnabled(True)

    def start_test(self):
        if not self.latest_scan_log:
            self.log_view.append("No scan log available. Run scan first.")
            return

        delay = self.delay_input.value()
        threads = self.threads_input.value()
        project_name = self.project_name_input.text().strip()

        self.log_view.append("Starting real application testing...")
        self.test_btn.setEnabled(False)
        self.scan_btn.setEnabled(False)

        self.test_thread = TestThread(self.latest_scan_log, delay, threads, project_name)
        self.test_thread.progress.connect(self.on_test_progress)
        self.test_thread.finished.connect(self.on_test_finished)
        self.test_thread.start()

    def on_test_progress(self, val):
        self.log_view.append(f"Testing progress: {val}%")

    def on_test_finished(self, log_path, report_path):
        if not log_path:
            self.log_view.append(f"Test error: {report_path}")
        else:
            self.log_view.append(f"Testing completed. Log saved: {log_path}")
            self.log_view.append(f"Report saved: {report_path}")
        self.test_btn.setEnabled(True)
        self.scan_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    gui = SQLiScannerGUI()
    gui.show()
    sys.exit(app.exec())
