"""Dimensions dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QComboBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt

class DimensionsDialog(QDialog):
    """Dialog for setting map dimensions and units."""
    
    def __init__(self, parent=None, bounds=None, units="None"):
        super().__init__(parent)
        self.setWindowTitle("Map Dimensions")
        self.resize(350, 250)
        
        self.bounds = bounds or {
            'min_x': 0.0, 'min_y': 0.0,
            'max_x': 10000.0, 'max_y': 10000.0
        }
        self.units = units
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Coordinates Group
        coord_group = QGroupBox("Coordinates")
        coord_layout = QVBoxLayout()
        
        # Lower Left
        ll_layout = QHBoxLayout()
        ll_layout.addWidget(QLabel("Lower Left:"))
        
        self.min_x_spin = QDoubleSpinBox()
        self.min_x_spin.setRange(-1e9, 1e9)
        self.min_x_spin.setDecimals(2)
        self.min_x_spin.setValue(self.bounds.get('min_x', 0.0))
        ll_layout.addWidget(QLabel("X:"))
        ll_layout.addWidget(self.min_x_spin)
        
        self.min_y_spin = QDoubleSpinBox()
        self.min_y_spin.setRange(-1e9, 1e9)
        self.min_y_spin.setDecimals(2)
        self.min_y_spin.setValue(self.bounds.get('min_y', 0.0))
        ll_layout.addWidget(QLabel("Y:"))
        ll_layout.addWidget(self.min_y_spin)
        
        coord_layout.addLayout(ll_layout)
        
        # Upper Right
        ur_layout = QHBoxLayout()
        ur_layout.addWidget(QLabel("Upper Right:"))
        
        self.max_x_spin = QDoubleSpinBox()
        self.max_x_spin.setRange(-1e9, 1e9)
        self.max_x_spin.setDecimals(2)
        self.max_x_spin.setValue(self.bounds.get('max_x', 10000.0))
        ur_layout.addWidget(QLabel("X:"))
        ur_layout.addWidget(self.max_x_spin)
        
        self.max_y_spin = QDoubleSpinBox()
        self.max_y_spin.setRange(-1e9, 1e9)
        self.max_y_spin.setDecimals(2)
        self.max_y_spin.setValue(self.bounds.get('max_y', 10000.0))
        ur_layout.addWidget(QLabel("Y:"))
        ur_layout.addWidget(self.max_y_spin)
        
        coord_layout.addLayout(ur_layout)
        
        coord_group.setLayout(coord_layout)
        layout.addWidget(coord_group)
        
        # Map Units
        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Map Units:"))
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Feet", "Meters", "Degrees", "None"])
        self.units_combo.setCurrentText(self.units)
        units_layout.addWidget(self.units_combo)
        units_layout.addStretch()
        layout.addLayout(units_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.auto_size_button = QPushButton("Auto-Size")
        self.auto_size_button.clicked.connect(self.auto_size)
        button_layout.addWidget(self.auto_size_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.help_button = QPushButton("Help")
        button_layout.addWidget(self.help_button)
        
        layout.addLayout(button_layout)
        
    def auto_size(self):
        """Signal to parent to auto-size, or just close with a flag?
        Better to let the dialog return a flag or handle it if we pass the network.
        But dialogs usually just return data.
        Let's emit a signal or just return a special value?
        Actually, we can pass the network to the dialog if we want it to calculate.
        Or simpler: The dialog just returns the values. The 'Auto-Size' button
        can calculate immediately if we pass the node coordinates or the network object.
        """
        # For now, let's assume the parent handles it or we pass the network.
        # To keep it decoupled, let's emit a signal or just set a flag.
        # But wait, Auto-Size should update the spinboxes immediately.
        # So we need access to the network or node coordinates.
        if hasattr(self.parent(), 'project') and self.parent().project.network.nodes:
            nodes = self.parent().project.network.nodes.values()
            if not nodes:
                return
                
            min_x = min(n.x for n in nodes)
            max_x = max(n.x for n in nodes)
            min_y = min(n.y for n in nodes)
            max_y = max(n.y for n in nodes)
            
            # Add some margin (e.g. 5%)
            width = max_x - min_x
            height = max_y - min_y
            margin_x = width * 0.05 if width > 0 else 10.0
            margin_y = height * 0.05 if height > 0 else 10.0
            
            self.min_x_spin.setValue(min_x - margin_x)
            self.max_x_spin.setValue(max_x + margin_x)
            self.min_y_spin.setValue(min_y - margin_y)
            self.max_y_spin.setValue(max_y + margin_y)
        
    def get_data(self):
        """Get dialog data."""
        return {
            'bounds': {
                'min_x': self.min_x_spin.value(),
                'min_y': self.min_y_spin.value(),
                'max_x': self.max_x_spin.value(),
                'max_y': self.max_y_spin.value()
            },
            'units': self.units_combo.currentText()
        }
