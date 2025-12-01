"""Legend Editor Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QDialogButtonBox, QHeaderView,
    QColorDialog, QComboBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class LegendEditorDialog(QDialog):
    """Dialog for editing legend properties."""
    
    def __init__(self, legend_data, parent=None):
        super().__init__(parent)
        self.legend_data = legend_data
        # Create copies to avoid modifying original data in place
        self.colors = [QColor(c) for c in legend_data.get('colors', [])]
        self.values = list(legend_data.get('values', []))
        self.setWindowTitle("Legend Editor")
        self.resize(400, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Value", "Color"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)
        
        # Populate table
        self.populate_table()
        
        # Buttons
        btn_layout = QVBoxLayout()
        
        # Auto-Scale
        auto_scale_group = QGroupBox("Auto-Scale")
        auto_layout = QVBoxLayout()
        
        intervals_layout = QHBoxLayout()
        intervals_layout.addWidget(QLabel("Intervals:"))
        self.intervals_combo = QComboBox()
        self.intervals_combo.addItems(["Equal Intervals", "Quantiles"]) # Placeholder for logic
        intervals_layout.addWidget(self.intervals_combo)
        auto_layout.addLayout(intervals_layout)
        
        self.btn_equal = QPushButton("Equal Intervals")
        self.btn_equal.clicked.connect(self.equal_intervals)
        auto_layout.addWidget(self.btn_equal)
        
        auto_scale_group.setLayout(auto_layout)
        btn_layout.addWidget(auto_scale_group)
        
        # Color Ramp
        ramp_group = QGroupBox("Color Ramp")
        ramp_layout = QVBoxLayout()
        
        self.btn_reverse = QPushButton("Reverse Colors")
        self.btn_reverse.clicked.connect(self.reverse_colors)
        ramp_layout.addWidget(self.btn_reverse)
        
        # Simple ramp selection
        ramp_select_layout = QHBoxLayout()
        ramp_select_layout.addWidget(QLabel("Ramp:"))
        self.ramp_combo = QComboBox()
        self.ramp_combo.addItems(["Rainbow", "Blue-Red", "Grayscale"])
        self.ramp_combo.currentTextChanged.connect(self.apply_ramp)
        ramp_select_layout.addWidget(self.ramp_combo)
        ramp_layout.addLayout(ramp_select_layout)
        
        ramp_group.setLayout(ramp_layout)
        btn_layout.addWidget(ramp_group)
        
        layout.addLayout(btn_layout)
        
        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def populate_table(self):
        """Populate table with values and colors."""
        self.table.setRowCount(len(self.values))
        
        for i, (val, color) in enumerate(zip(self.values, self.colors)):
            # Value
            val_item = QTableWidgetItem(f"{val:.2f}")
            self.table.setItem(i, 0, val_item)
            
            # Color
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            color_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) # Not directly editable text
            self.table.setItem(i, 1, color_item)
            
    def on_item_double_clicked(self, item):
        """Handle double click to edit color."""
        if item.column() == 1:
            row = item.row()
            current_color = self.colors[row]
            color = QColorDialog.getColor(current_color, self, "Select Color")
            
            if color.isValid():
                self.colors[row] = color
                item.setBackground(color)
                
    def equal_intervals(self):
        """Apply equal intervals (placeholder logic)."""
        # In a real implementation, this would need data statistics
        # For now, just evenly space between min and max of current values
        if not self.values:
            return
            
        min_val = min(self.values)
        max_val = max(self.values)
        step = (max_val - min_val) / (len(self.values) - 1) if len(self.values) > 1 else 0
        
        for i in range(len(self.values)):
            self.values[i] = min_val + i * step
            
        self.populate_table()
        
    def reverse_colors(self):
        """Reverse the color list."""
        self.colors.reverse()
        self.populate_table()
        
    def apply_ramp(self, ramp_name):
        """Apply a predefined color ramp."""
        n = len(self.colors)
        if n < 2:
            return
            
        new_colors = []
        if ramp_name == "Rainbow":
            # Simple rainbow generation
            for i in range(n):
                hue = (1.0 - i / (n - 1)) * 240 / 360 # Blue to Red
                new_colors.append(QColor.fromHslF(hue, 1.0, 0.5))
        elif ramp_name == "Blue-Red":
            for i in range(n):
                ratio = i / (n - 1)
                new_colors.append(QColor(int(255 * ratio), 0, int(255 * (1 - ratio))))
        elif ramp_name == "Grayscale":
            for i in range(n):
                val = int(255 * (1 - i / (n - 1)))
                new_colors.append(QColor(val, val, val))
                
        self.colors = new_colors
        self.populate_table()
        
    def get_data(self):
        """Get updated legend data."""
        # Read values from table in case they were edited
        new_values = []
        for row in range(self.table.rowCount()):
            text = self.table.item(row, 0).text()
            try:
                val = float(text)
            except ValueError:
                val = self.values[row]
            new_values.append(val)
            
        return {
            'values': new_values,
            'colors': self.colors
        }
