"""Status report view."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtGui import QFont

class StatusView(QWidget):
    """Widget for displaying simulation status report."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        
        self.setup_ui()
        self.refresh_report()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 12))
        layout.addWidget(self.text_edit)
        
    def refresh_report(self):
        """Refresh the report text."""
        self.text_edit.setText(self.project.last_report)
