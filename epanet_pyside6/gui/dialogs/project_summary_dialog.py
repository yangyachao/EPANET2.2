"""Project Summary dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QGroupBox
)

class ProjectSummaryDialog(QDialog):
    """Dialog for editing project summary (title and notes)."""
    
    def __init__(self, parent=None, title_lines=None, notes=""):
        super().__init__(parent)
        self.setWindowTitle("Project Summary")
        self.resize(500, 400)
        
        self.title_lines = title_lines or ["", "", ""]
        self.notes = notes
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Title Group
        title_group = QGroupBox("Title")
        title_layout = QVBoxLayout()
        
        self.title_edits = []
        # Ensure we have at least 3 lines
        while len(self.title_lines) < 3:
            self.title_lines.append("")
            
        for i in range(3):
            edit = QLineEdit()
            if i < len(self.title_lines):
                edit.setText(self.title_lines[i])
            self.title_edits.append(edit)
            title_layout.addWidget(edit)
            
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)
        
        # Notes Group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlainText(self.notes)
        notes_layout.addWidget(self.notes_edit)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def get_data(self):
        """Get dialog data."""
        return {
            'title': [edit.text() for edit in self.title_edits],
            'notes': self.notes_edit.toPlainText()
        }
