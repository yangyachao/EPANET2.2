"""Base class for report views."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, 
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

class ReportView(QWidget):
    """Base widget for displaying reports."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.report_title = "Report"
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export...")
        self.export_btn.clicked.connect(self.export_report)
        toolbar_layout.addWidget(self.export_btn)
        
        self.print_btn = QPushButton("Print...")
        self.print_btn.clicked.connect(self.print_report)
        toolbar_layout.addWidget(self.print_btn)
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        toolbar_layout.addWidget(self.copy_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Text Area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 10)) # Monospace for alignment
        layout.addWidget(self.text_edit)
        
    def set_text(self, text):
        """Set report text."""
        self.text_edit.setPlainText(text)
        
    def set_html(self, html):
        """Set report HTML."""
        self.text_edit.setHtml(html)
        
    def append_text(self, text):
        """Append text to report."""
        self.text_edit.append(text)
        
    def clear(self):
        """Clear report."""
        self.text_edit.clear()
        
    def export_report(self):
        """Export report to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "Text Files (*.txt);;HTML Files (*.html);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w') as f:
                if filename.endswith('.html'):
                    f.write(self.text_edit.toHtml())
                else:
                    f.write(self.text_edit.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
            
    def print_report(self):
        """Print report."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.Accepted:
            self.text_edit.print_(printer)
            
    def copy_to_clipboard(self):
        """Copy report content to clipboard."""
        self.text_edit.selectAll()
        self.text_edit.copy()
        # Deselect?
        cursor = self.text_edit.textCursor()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)
