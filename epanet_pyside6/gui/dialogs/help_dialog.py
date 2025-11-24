"""Help dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser
)
from PySide6.QtCore import QUrl

class HelpDialog(QDialog):
    """Simple help browser dialog."""
    
    def __init__(self, title="EPANET Help", content=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        
        self.setup_ui()
        
        if content:
            self.browser.setHtml(content)
        else:
            self.load_default_help()
            
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Navigation
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.browser_back)
        nav_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("Forward")
        self.forward_btn.clicked.connect(self.browser_forward)
        nav_layout.addWidget(self.forward_btn)
        
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.load_default_help)
        nav_layout.addWidget(self.home_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        
    def browser_back(self):
        self.browser.backward()
        
    def browser_forward(self):
        self.browser.forward()
        
    def load_default_help(self):
        """Load default help content."""
        html = """
        <h1>EPANET 2.2 Help</h1>
        <p>Welcome to EPANET PySide6.</p>
        <ul>
            <li><a href="#intro">Introduction</a></li>
            <li><a href="#network">Network Components</a></li>
            <li><a href="#analysis">Running Analysis</a></li>
        </ul>
        <h2 id="intro">Introduction</h2>
        <p>EPANET performs extended period simulation of hydraulic and water quality behavior within pressurized pipe networks.</p>
        <h2 id="network">Network Components</h2>
        <p>A network consists of pipes, nodes (junctions), pumps, valves and storage tanks or reservoirs.</p>
        <h2 id="analysis">Running Analysis</h2>
        <p>To run a simulation, select <b>Project > Run Analysis</b> or press <b>F5</b>.</p>
        """
        self.browser.setHtml(html)
        
    def set_content(self, html):
        self.browser.setHtml(html)
