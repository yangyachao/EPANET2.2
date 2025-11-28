"""Preferences Dialog for program settings."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QLineEdit, QPushButton, QCheckBox, QFileDialog, QTabWidget, QWidget
)
from PySide6.QtCore import Qt

class PreferencesDialog(QDialog):
    """Dialog for setting program preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_preferences()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Formats tab
        formats_tab = self.create_formats_tab()
        tabs.addTab(formats_tab, "Formats")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def create_general_tab(self):
        """Create general preferences tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        form = QFormLayout()
        
        # Temporary directory
        temp_layout = QHBoxLayout()
        self.temp_dir_edit = QLineEdit()
        temp_layout.addWidget(self.temp_dir_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_temp_dir)
        temp_layout.addWidget(browse_btn)
        
        form.addRow("Temporary Directory:", temp_layout)
        
        # Auto-backup
        self.auto_backup_check = QCheckBox("Enable automatic backup")
        form.addRow("", self.auto_backup_check)
        
        # Confirm deletions
        self.confirm_delete_check = QCheckBox("Confirm object deletions")
        self.confirm_delete_check.setChecked(True)
        form.addRow("", self.confirm_delete_check)
        
        # Blinking map highlighter
        self.blink_check = QCheckBox("Blink map highlighter")
        self.blink_check.setChecked(True)
        form.addRow("", self.blink_check)
        
        layout.addLayout(form)
        layout.addStretch()
        
        return widget
        
    def create_formats_tab(self):
        """Create number formats tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        form = QFormLayout()
        
        # Flow units
        self.flow_units_combo = QComboBox()
        self.flow_units_combo.addItems([
            "CFS", "GPM", "MGD", "IMGD", "AFD",
            "LPS", "LPM", "MLD", "CMH", "CMD"
        ])
        form.addRow("Flow Units:", self.flow_units_combo)
        
        # Pressure units
        self.pressure_units_combo = QComboBox()
        self.pressure_units_combo.addItems(["PSI", "Meters", "KPA"])
        form.addRow("Pressure Units:", self.pressure_units_combo)
        
        # Decimal places
        self.decimals_combo = QComboBox()
        self.decimals_combo.addItems(["0", "1", "2", "3", "4", "5"])
        self.decimals_combo.setCurrentText("2")
        form.addRow("Decimal Places:", self.decimals_combo)
        
        layout.addLayout(form)
        layout.addStretch()
        
        return widget
        
    def browse_temp_dir(self):
        """Browse for temporary directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Temporary Directory",
            self.temp_dir_edit.text()
        )
        if directory:
            self.temp_dir_edit.setText(directory)
            
    def load_preferences(self):
        """Load preferences from settings."""
        from PySide6.QtCore import QSettings
        settings = QSettings("US EPA", "EPANET 2.2")
        
        # General
        self.temp_dir_edit.setText(settings.value("tempDir", "/tmp"))
        self.auto_backup_check.setChecked(settings.value("autoBackup", False, type=bool))
        self.confirm_delete_check.setChecked(settings.value("confirmDelete", True, type=bool))
        self.blink_check.setChecked(settings.value("blinkHighlight", True, type=bool))
        
        # Formats
        self.flow_units_combo.setCurrentText(settings.value("flowUnits", "GPM"))
        self.pressure_units_combo.setCurrentText(settings.value("pressureUnits", "PSI"))
        self.decimals_combo.setCurrentText(settings.value("decimals", "2"))
        
    def save_preferences(self):
        """Save preferences to settings."""
        from PySide6.QtCore import QSettings
        settings = QSettings("US EPA", "EPANET 2.2")
        
        # General
        settings.setValue("tempDir", self.temp_dir_edit.text())
        settings.setValue("autoBackup", self.auto_backup_check.isChecked())
        settings.setValue("confirmDelete", self.confirm_delete_check.isChecked())
        settings.setValue("blinkHighlight", self.blink_check.isChecked())
        
        # Formats
        settings.setValue("flowUnits", self.flow_units_combo.currentText())
        settings.setValue("pressureUnits", self.pressure_units_combo.currentText())
        settings.setValue("decimals", self.decimals_combo.currentText())
        
    def accept(self):
        """Save preferences and close."""
        self.save_preferences()
        super().accept()
