"""Status report widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit
)

class StatusReport(QWidget):
    """Status report window."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Status Report")
        self.resize(600, 400)
        
        self.setup_ui()
        self.load_report()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Courier New")
        layout.addWidget(self.text_edit)
        
    def load_report(self):
        """Load status report from project."""
        # Ideally, we get the report file content from the engine or a temporary file
        # For now, let's assume the engine stores the last report path or content
        
        report_content = "No status report available."
        
        # Check if project has a report file path
        if hasattr(self.project, 'report_file') and self.project.report_file:
            try:
                with open(self.project.report_file, 'r') as f:
                    report_content = f.read()
            except Exception as e:
                report_content = f"Error reading report file: {e}"
        elif hasattr(self.project, 'engine') and hasattr(self.project.engine, 'model'):
             # WNTR might not keep the report file content in memory directly
             # We might need to rely on where we saved the report during run_simulation
             pass
             
        self.text_edit.setText(report_content)
