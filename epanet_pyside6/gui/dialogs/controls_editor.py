"""Controls editor dialog for simple and rule-based controls."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QPushButton, QMessageBox, QLabel, QSplitter, QListWidget,
    QListWidgetItem, QToolBar, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
import re
from models.control import SimpleControl, Rule


class ControlSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for EPANET controls and rules."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))
        keyword_format.setFontWeight(QFont.Bold)
        
        keywords = [
            "LINK", "NODE", "IF", "THEN", "ELSE", "AND", "OR",
            "RULE", "PRIORITY", "AT", "TIME", "CLOCKTIME",
            "ABOVE", "BELOW", "OPEN", "CLOSED", "ACTIVE"
        ]
        
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlighting_rules.append((re.compile(pattern, re.IGNORECASE), keyword_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(255, 0, 0))
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))
        
        # Comments (if any)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(0, 128, 0))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r';.*'), comment_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_obj in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format_obj)


class ControlsEditorDialog(QDialog):
    """Dialog for editing simple controls and rule-based controls."""
    
    controls_changed = Signal()
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Controls Editor")
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_controls()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Simple Controls Tab
        self.simple_controls_widget = self.create_simple_controls_tab()
        self.tab_widget.addTab(self.simple_controls_widget, "Simple Controls")
        
        # Rule-Based Controls Tab
        self.rules_widget = self.create_rules_tab()
        self.tab_widget.addTab(self.rules_widget, "Rule-Based Controls")
        
        # Button box
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_changes)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)
        
        layout.addLayout(button_layout)
    
    def create_simple_controls_tab(self):
        """Create the simple controls tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(
            "Simple controls use the format:\n"
            "LINK <linkid> <status> IF NODE <nodeid> <operator> <value>\n"
            "LINK <linkid> <status> AT TIME <time>\n"
            "LINK <linkid> <status> AT CLOCKTIME <clocktime>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Text editor for simple controls
        self.simple_controls_edit = QTextEdit()
        self.simple_controls_edit.setFont(QFont("Courier New", 10))
        self.simple_controls_edit.setPlaceholderText(
            "Enter simple controls, one per line...\n\n"
            "Example:\n"
            "LINK P1 OPEN IF NODE N1 ABOVE 100\n"
            "LINK P2 CLOSED AT TIME 10:00"
        )
        
        # Apply syntax highlighting
        self.simple_highlighter = ControlSyntaxHighlighter(self.simple_controls_edit.document())
        
        layout.addWidget(self.simple_controls_edit)
        
        # Validation button
        validate_button = QPushButton("Validate Syntax")
        validate_button.clicked.connect(self.validate_simple_controls)
        layout.addWidget(validate_button)
        
        return widget
    
    def create_rules_tab(self):
        """Create the rule-based controls tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(
            "Rule-based controls use the format:\n"
            "RULE <ruleid>\n"
            "IF <condition>\n"
            "THEN <action>\n"
            "ELSE <action> (optional)\n"
            "PRIORITY <value> (optional)"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Text editor for rules
        self.rules_edit = QTextEdit()
        self.rules_edit.setFont(QFont("Courier New", 10))
        self.rules_edit.setPlaceholderText(
            "Enter rule-based controls...\n\n"
            "Example:\n"
            "RULE 1\n"
            "IF NODE N1 PRESSURE BELOW 20\n"
            "THEN PUMP P1 STATUS IS OPEN\n"
            "ELSE PUMP P1 STATUS IS CLOSED\n"
            "PRIORITY 1"
        )
        
        # Apply syntax highlighting
        self.rules_highlighter = ControlSyntaxHighlighter(self.rules_edit.document())
        
        layout.addWidget(self.rules_edit)
        
        # Validation button
        validate_button = QPushButton("Validate Syntax")
        validate_button.clicked.connect(self.validate_rules)
        layout.addWidget(validate_button)
        
        return widget
    
    def load_controls(self):
        """Load controls from the project."""
        try:
            # Load simple controls
            simple_controls = []
            for control in self.project.network.controls:
                simple_controls.append(control.to_string())
            
            self.simple_controls_edit.setPlainText('\n'.join(simple_controls))
            
            # Load rules
            rules = []
            for rule in self.project.network.rules:
                rules.append(rule.to_string())
            
            self.rules_edit.setPlainText('\n\n'.join(rules))
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Error loading controls: {str(e)}"
            )
    
    def validate_simple_controls(self):
        """Validate simple controls syntax."""
        text = self.simple_controls_edit.toPlainText()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        errors = []
        for i, line in enumerate(lines, 1):
            if not self.is_valid_simple_control(line):
                errors.append(f"Line {i}: Invalid syntax")
        
        if errors:
            QMessageBox.warning(
                self,
                "Validation Errors",
                "Syntax errors found:\n\n" + '\n'.join(errors)
            )
        else:
            QMessageBox.information(
                self,
                "Validation",
                "All simple controls are valid!"
            )
    
    def validate_rules(self):
        """Validate rule-based controls syntax."""
        text = self.rules_edit.toPlainText()
        
        # Split into individual rules
        rules = []
        current_rule = []
        for line in text.split('\n'):
            line = line.strip()
            if line.upper().startswith('RULE') and current_rule:
                rules.append('\n'.join(current_rule))
                current_rule = [line]
            elif line:
                current_rule.append(line)
        
        if current_rule:
            rules.append('\n'.join(current_rule))
        
        errors = []
        for i, rule in enumerate(rules, 1):
            if not self.is_valid_rule(rule):
                errors.append(f"Rule {i}: Invalid syntax")
        
        if errors:
            QMessageBox.warning(
                self,
                "Validation Errors",
                "Syntax errors found:\n\n" + '\n'.join(errors)
            )
        else:
            QMessageBox.information(
                self,
                "Validation",
                "All rules are valid!"
            )
    
    def is_valid_simple_control(self, line):
        """Check if a simple control line is valid."""
        # Basic validation - check for required keywords
        upper_line = line.upper()
        
        if not upper_line.startswith('LINK'):
            return False
        
        # Check for IF NODE, AT TIME, or AT CLOCKTIME
        if 'IF' in upper_line and 'NODE' in upper_line:
            # IF NODE control
            required = ['LINK', 'IF', 'NODE']
            return all(keyword in upper_line for keyword in required)
        elif 'AT' in upper_line and ('TIME' in upper_line or 'CLOCKTIME' in upper_line):
            # AT TIME or AT CLOCKTIME control
            return True
        
        return False
    
    def is_valid_rule(self, rule_text):
        """Check if a rule is valid."""
        # Basic validation - check for required keywords
        upper_text = rule_text.upper()
        
        if not upper_text.startswith('RULE'):
            return False
        
        # Must have IF and THEN
        if 'IF' not in upper_text or 'THEN' not in upper_text:
            return False
        
        return True
    
    def accept_changes(self):
        """Accept and save changes."""
        try:
            # Validate before accepting
            simple_text = self.simple_controls_edit.toPlainText()
            rules_text = self.rules_edit.toPlainText()
            
            # Basic validation
            simple_lines = [line.strip() for line in simple_text.split('\n') if line.strip()]
            for line in simple_lines:
                if not self.is_valid_simple_control(line):
                    QMessageBox.warning(
                        self,
                        "Validation Error",
                        f"Invalid simple control syntax:\n{line}"
                    )
                    return
            
            # Save to project
            self.project.network.controls.clear()
            self.project.network.rules.clear()
            
            # Parse simple controls
            simple_lines = [line.strip() for line in simple_text.split('\n') if line.strip()]
            for line in simple_lines:
                control = SimpleControl.from_string(line)
                if control:
                    self.project.network.controls.append(control)
            
            # Parse rules
            # Split into individual rules
            current_rule = []
            for line in rules_text.split('\n'):
                line = line.strip()
                if line.upper().startswith('RULE') and current_rule:
                    rule_str = '\n'.join(current_rule)
                    rule = Rule.from_string(rule_str)
                    if rule:
                        self.project.network.rules.append(rule)
                    current_rule = [line]
                elif line:
                    current_rule.append(line)
            
            if current_rule:
                rule_str = '\n'.join(current_rule)
                rule = Rule.from_string(rule_str)
                if rule:
                    self.project.network.rules.append(rule)
            
            self.project.modified = True
            self.controls_changed.emit()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving controls: {str(e)}"
            )
    
    def show_help(self):
        """Show help information."""
        help_text = """
        <h2>Controls Editor Help</h2>
        
        <h3>Simple Controls</h3>
        <p>Simple controls allow you to control link status based on:</p>
        <ul>
            <li><b>Node conditions:</b> LINK linkid status IF NODE nodeid operator value</li>
            <li><b>Time:</b> LINK linkid status AT TIME time</li>
            <li><b>Clock time:</b> LINK linkid status AT CLOCKTIME clocktime</li>
        </ul>
        
        <p><b>Operators:</b> ABOVE, BELOW</p>
        <p><b>Status:</b> OPEN, CLOSED, or numeric setting</p>
        
        <h3>Rule-Based Controls</h3>
        <p>Rule-based controls use IF-THEN-ELSE logic:</p>
        <pre>
RULE ruleid
IF condition
AND/OR condition
THEN action
ELSE action
PRIORITY value
        </pre>
        
        <p><b>Conditions:</b> Can test node/link properties</p>
        <p><b>Actions:</b> Set link status or settings</p>
        <p><b>Priority:</b> Optional priority value (higher = more important)</p>
        
        <h3>Examples</h3>
        <p><b>Simple Control:</b></p>
        <pre>LINK P1 OPEN IF NODE N1 ABOVE 100</pre>
        
        <p><b>Rule:</b></p>
        <pre>
RULE LowPressure
IF NODE N1 PRESSURE BELOW 20
THEN PUMP P1 STATUS IS OPEN
PRIORITY 1
        </pre>
        """
        
        QMessageBox.information(self, "Help", help_text)
