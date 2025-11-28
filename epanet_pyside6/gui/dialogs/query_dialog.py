"""Query Dialog for finding objects based on conditions."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, 
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal

class QueryDialog(QDialog):
    """Dialog for querying network objects based on conditions."""
    
    query_executed = Signal(str, str, str, float)  # obj_type, parameter, operator, value
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Query")
        self.resize(400, 250)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Define a condition to find and highlight objects on the map.\n"
            "Example: Find all nodes where Pressure < 20"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Form
        form = QFormLayout()
        
        # Object Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Nodes", "Links"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form.addRow("Object Type:", self.type_combo)
        
        # Parameter
        self.param_combo = QComboBox()
        form.addRow("Parameter:", self.param_combo)
        
        # Operator
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["=", ">", "<", ">=", "<=", "!="])
        form.addRow("Operator:", self.operator_combo)
        
        # Value
        self.value_edit = QLineEdit()
        form.addRow("Value:", self.value_edit)
        
        layout.addLayout(form)
        
        # Result label
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.execute_query)
        btn_layout.addWidget(submit_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initialize parameters
        self.on_type_changed("Nodes")
        
    def on_type_changed(self, obj_type):
        """Update parameter list based on object type."""
        self.param_combo.clear()
        
        if obj_type == "Nodes":
            # Check if we have results
            if self.project.has_results():
                self.param_combo.addItems([
                    "Elevation", "Base Demand", "Initial Quality",
                    "Demand", "Head", "Pressure", "Quality"
                ])
            else:
                self.param_combo.addItems([
                    "Elevation", "Base Demand", "Initial Quality"
                ])
        else:  # Links
            if self.project.has_results():
                self.param_combo.addItems([
                    "Length", "Diameter", "Roughness",
                    "Flow", "Velocity", "Headloss"
                ])
            else:
                self.param_combo.addItems([
                    "Length", "Diameter", "Roughness"
                ])
                
    def execute_query(self):
        """Execute the query and emit signal."""
        obj_type = self.type_combo.currentText()
        parameter = self.param_combo.currentText()
        operator = self.operator_combo.currentText()
        
        try:
            value = float(self.value_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value.")
            return
            
        # Emit signal with query parameters
        self.query_executed.emit(obj_type, parameter, operator, value)
        
        # Count matching objects
        count = self.count_matches(obj_type, parameter, operator, value)
        self.result_label.setText(f"Found {count} matching objects")
        
    def count_matches(self, obj_type, parameter, operator, value):
        """Count objects matching the query."""
        count = 0
        
        if obj_type == "Nodes":
            for node in self.project.network.nodes.values():
                node_value = self.get_node_value(node, parameter)
                if node_value is not None and self.compare(node_value, operator, value):
                    count += 1
        else:  # Links
            for link in self.project.network.links.values():
                link_value = self.get_link_value(link, parameter)
                if link_value is not None and self.compare(link_value, operator, value):
                    count += 1
                    
        return count
        
    def get_node_value(self, node, parameter):
        """Get node parameter value."""
        param_map = {
            "Elevation": "elevation",
            "Base Demand": "base_demand",
            "Initial Quality": "init_quality",
            "Demand": "demand",
            "Head": "head",
            "Pressure": "pressure",
            "Quality": "quality"
        }
        
        attr = param_map.get(parameter)
        if attr and hasattr(node, attr):
            return getattr(node, attr)
        return None
        
    def get_link_value(self, link, parameter):
        """Get link parameter value."""
        param_map = {
            "Length": "length",
            "Diameter": "diameter",
            "Roughness": "roughness",
            "Flow": "flow",
            "Velocity": "velocity",
            "Headloss": "headloss"
        }
        
        attr = param_map.get(parameter)
        if attr and hasattr(link, attr):
            return getattr(link, attr)
        return None
        
    def compare(self, val1, operator, val2):
        """Compare two values based on operator."""
        if operator == "=":
            return abs(val1 - val2) < 0.001
        elif operator == ">":
            return val1 > val2
        elif operator == "<":
            return val1 < val2
        elif operator == ">=":
            return val1 >= val2
        elif operator == "<=":
            return val1 <= val2
        elif operator == "!=":
            return abs(val1 - val2) >= 0.001
        return False
