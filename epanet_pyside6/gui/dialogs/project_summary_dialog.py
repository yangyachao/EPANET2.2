"""Project Summary dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QGroupBox, QWidget
)

class ProjectSummaryDialog(QDialog):
    """Dialog for editing project summary (title and notes)."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Summary")
        self.resize(500, 400)
        
        self.title_lines = project.network.title or ["", "", ""]
        self.notes = project.network.notes or ""
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        from PySide6.QtWidgets import QTabWidget
        tab_widget = QTabWidget()
        
        # Tab 1: Description (Title & Notes)
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        
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
        desc_layout.addWidget(title_group)
        
        # Notes Group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlainText(self.notes)
        notes_layout.addWidget(self.notes_edit)
        
        notes_group.setLayout(notes_layout)
        desc_layout.addWidget(notes_group)
        
        tab_widget.addTab(desc_widget, "Description")
        
        # Tab 2: Statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        stats_table = QTableWidget()
        stats_table.setColumnCount(2)
        stats_table.setHorizontalHeaderLabels(["Item", "Count"])
        stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        stats_table.verticalHeader().setVisible(False)
        
        # Calculate stats
        network = self.project.network
        stats = [
            ("Junctions", len(network.get_junctions())),
            ("Reservoirs", len(network.get_reservoirs())),
            ("Tanks", len(network.get_tanks())),
            ("Pipes", len(network.get_pipes())),
            ("Pumps", len(network.get_pumps())),
            ("Valves", len(network.get_valves())),
            ("Patterns", len(network.patterns)),
            ("Curves", len(network.curves)),
            ("Controls", len(network.controls)),
            ("Rules", len(network.rules))
        ]
        
        stats_table.setRowCount(len(stats))
        for i, (name, count) in enumerate(stats):
            stats_table.setItem(i, 0, QTableWidgetItem(name))
            stats_table.setItem(i, 1, QTableWidgetItem(str(count)))
            
        stats_layout.addWidget(stats_table)
        tab_widget.addTab(stats_widget, "Statistics")
        
        layout.addWidget(tab_widget)
        
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
