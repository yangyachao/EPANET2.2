"""Simulation status dialog."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QProgressBar, QLabel
from PySide6.QtCore import Qt, QTimer
import time

class SimulationStatusDialog(QDialog):
    """Dialog to show simulation status and progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Status")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
    def append_log(self, message: str):
        """Append message to log."""
        self.log_text.append(message)
        # Scroll to bottom
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    def set_progress(self, value: int):
        """Set progress value."""
        self.progress_bar.setValue(value)
        
    def set_status(self, status: str):
        """Set status text."""
        self.status_label.setText(status)
        
    def simulation_finished(self, success: bool):
        """Handle simulation completion."""
        self.close_btn.setEnabled(True)
        if success:
            self.set_status("Simulation completed successfully.")
            self.set_progress(100)
            self.append_log("Run Successful.")
        else:
            self.set_status("Simulation failed.")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            self.append_log("Run Failed.")
