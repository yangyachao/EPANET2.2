"""About dialog."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

class AboutDialog(QDialog):
    """About dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About EPANET 2.2 PySide6")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("EPANET 2.2 PySide6")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "A modern cross-platform GUI for EPANET 2.2\n"
            "Built with Python and PySide6."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Credits
        credits_label = QLabel("Based on EPANET 2.2 by US EPA\nPowered by WNTR")
        credits_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits_label)
        
        layout.addStretch()
        
        # Button
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
