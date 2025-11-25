"""Dialog for configuring graph options."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QLabel, QSpinBox, 
    QDialogButtonBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt

class GraphOptionsDialog(QDialog):
    """Dialog for setting graph display options."""
    
    def __init__(self, parent=None, options=None):
        super().__init__(parent)
        self.setWindowTitle("Graph Options")
        self.options = options or {}
        self.setup_ui()
        self.load_options()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # General Options
        group = QGroupBox("Display Options")
        form = QFormLayout(group)
        
        self.show_grid_check = QCheckBox()
        form.addRow("Show Grid:", self.show_grid_check)
        
        self.show_legend_check = QCheckBox()
        form.addRow("Show Legend:", self.show_legend_check)
        
        self.white_bg_check = QCheckBox()
        form.addRow("White Background:", self.white_bg_check)
        
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 10)
        form.addRow("Line Width:", self.line_width_spin)
        
        layout.addWidget(group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_options(self):
        """Load current options."""
        self.show_grid_check.setChecked(self.options.get('show_grid', True))
        self.show_legend_check.setChecked(self.options.get('show_legend', True))
        self.white_bg_check.setChecked(self.options.get('white_background', True))
        self.line_width_spin.setValue(self.options.get('line_width', 2))
        
    def get_options(self):
        """Get selected options."""
        return {
            'show_grid': self.show_grid_check.isChecked(),
            'show_legend': self.show_legend_check.isChecked(),
            'white_background': self.white_bg_check.isChecked(),
            'line_width': self.line_width_spin.value()
        }
