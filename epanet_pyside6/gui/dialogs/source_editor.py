"""Source Quality Editor Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout
)
from core.constants import SourceType

class SourceEditorDialog(QDialog):
    """Dialog for editing source quality."""
    
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle(f"Source Quality for Node {node.id}")
        self.resize(300, 200)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Source Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["CONCEN", "MASS", "FLOWPACED", "SETPOINT"])
        form.addRow("Source Type:", self.type_combo)
        
        # Quality
        self.quality_edit = QLineEdit()
        form.addRow("Source Quality:", self.quality_edit)
        
        # Pattern
        self.pattern_edit = QLineEdit()
        form.addRow("Time Pattern:", self.pattern_edit)
        
        layout.addLayout(form)
        
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
        
    def load_data(self):
        """Load data from node."""
        # Map SourceType enum to index
        type_map = {
            SourceType.CONCEN: 0,
            SourceType.MASS: 1,
            SourceType.FLOWPACED: 2,
            SourceType.SETPOINT: 3
        }
        
        # Handle case where source_type might be string or enum
        current_type = self.node.source_type
        if isinstance(current_type, str):
            # Try to match string
            idx = self.type_combo.findText(current_type.upper())
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        else:
            self.type_combo.setCurrentIndex(type_map.get(current_type, 0))
            
        self.quality_edit.setText(str(self.node.source_quality))
        self.pattern_edit.setText(self.node.source_pattern or "")
        
    def get_data(self):
        """Get data from dialog."""
        type_str = self.type_combo.currentText()
        
        # Map string back to SourceType
        if type_str == "CONCEN":
            source_type = SourceType.CONCEN
        elif type_str == "MASS":
            source_type = SourceType.MASS
        elif type_str == "FLOWPACED":
            source_type = SourceType.FLOWPACED
        else:
            source_type = SourceType.SETPOINT
            
        try:
            quality = float(self.quality_edit.text())
        except ValueError:
            quality = 0.0
            
        pattern = self.pattern_edit.text()
        
        return {
            'source_type': source_type,
            'source_quality': quality,
            'source_pattern': pattern
        }
