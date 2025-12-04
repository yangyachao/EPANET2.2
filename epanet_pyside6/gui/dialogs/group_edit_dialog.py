"""Dialog for group editing network objects."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QDialogButtonBox, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from core.constants import NodeType, LinkType

class GroupEditDialog(QDialog):
    """Dialog for editing properties of multiple objects."""
    
    def __init__(self, project, selected_items=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.selected_items = selected_items or []
        self.setWindowTitle("Group Edit")
        self.resize(400, 300)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Selection Info
        info_layout = QHBoxLayout()
        count = len(self.selected_items)
        info_layout.addWidget(QLabel(f"Selected Objects: {count}"))
        layout.addLayout(info_layout)
        
        # Object Type Selection (if mixed selection or no selection)
        # For now, assume we edit based on what's selected, or filter by type
        # If mixed selection, we force user to choose one type to edit
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("For Object Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Junctions", "Reservoirs", "Tanks", "Pipes", "Pumps", "Valves"])
        
        # Try to guess type from selection
        if self.selected_items:
            # Check first item
            first = self.selected_items[0]
            # Map item class to string
            # This requires importing items which might cause circular import if not careful
            # Better to check the underlying object type
            if hasattr(first, 'node'):
                ntype = first.node.node_type
                if ntype == NodeType.JUNCTION: self.type_combo.setCurrentText("Junctions")
                elif ntype == NodeType.RESERVOIR: self.type_combo.setCurrentText("Reservoirs")
                elif ntype == NodeType.TANK: self.type_combo.setCurrentText("Tanks")
            elif hasattr(first, 'link'):
                ltype = first.link.link_type
                if ltype == LinkType.PIPE: self.type_combo.setCurrentText("Pipes")
                elif ltype == LinkType.PUMP: self.type_combo.setCurrentText("Pumps")
                # Valve types are many, but mapped to Valves
                elif ltype >= LinkType.PRV: self.type_combo.setCurrentText("Valves")
                
        self.type_combo.currentTextChanged.connect(self.update_properties)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Property Selection
        prop_layout = QHBoxLayout()
        prop_layout.addWidget(QLabel("Edit Property:"))
        self.prop_combo = QComboBox()
        self.prop_combo.currentTextChanged.connect(self.update_operation_visibility)
        prop_layout.addWidget(self.prop_combo)
        layout.addLayout(prop_layout)
        
        # Operation
        op_group = QGroupBox("Operation")
        op_layout = QVBoxLayout()
        
        self.op_replace = QRadioButton("Replace")
        self.op_replace.setChecked(True)
        self.op_multiply = QRadioButton("Multiply")
        self.op_add = QRadioButton("Add")
        
        self.op_bg = QButtonGroup()
        self.op_bg.addButton(self.op_replace)
        self.op_bg.addButton(self.op_multiply)
        self.op_bg.addButton(self.op_add)
        
        op_layout.addWidget(self.op_replace)
        op_layout.addWidget(self.op_multiply)
        op_layout.addWidget(self.op_add)
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # Value
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Value:"))
        self.val_input = QLineEdit()
        val_layout.addWidget(self.val_input)
        layout.addLayout(val_layout)
        
        # Filter
        filter_group = QGroupBox("With")
        filter_layout = QHBoxLayout()
        
        self.filter_chk = QCheckBox("Filter by:")
        self.filter_chk.stateChanged.connect(self.toggle_filter)
        filter_layout.addWidget(self.filter_chk)
        
        self.filter_prop_combo = QComboBox()
        self.filter_prop_combo.setEnabled(False)
        filter_layout.addWidget(self.filter_prop_combo)
        
        self.filter_rel_combo = QComboBox()
        self.filter_rel_combo.addItems(["=", "<", ">", "<=", ">=", "<>"])
        self.filter_rel_combo.setEnabled(False)
        filter_layout.addWidget(self.filter_rel_combo)
        
        self.filter_val_input = QLineEdit()
        self.filter_val_input.setEnabled(False)
        filter_layout.addWidget(self.filter_val_input)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_and_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize
        self.update_properties(self.type_combo.currentText())
        
    def update_properties(self, obj_type):
        """Update available properties based on object type."""
        self.prop_combo.clear()
        self.filter_prop_combo.clear()
        
        common_props = ["Tag"]
        node_props = ["Elevation", "Base Demand", "Initial Quality"]
        tank_props = ["Elevation", "Initial Level", "Min Level", "Max Level", "Diameter", "Initial Quality"]
        pipe_props = ["Length", "Diameter", "Roughness", "Loss Coeff.", "Initial Status"]
        pump_props = ["Initial Status"] # Curve?
        valve_props = ["Diameter", "Setting", "Loss Coeff.", "Initial Status"]
        
        props = []
        if obj_type == "Junctions":
            props = common_props + node_props
        elif obj_type == "Reservoirs":
            props = common_props + ["Total Head", "Initial Quality"]
        elif obj_type == "Tanks":
            props = common_props + tank_props
        elif obj_type == "Pipes":
            props = common_props + pipe_props
        elif obj_type == "Pumps":
            props = common_props + pump_props
        elif obj_type == "Valves":
            props = common_props + valve_props
            
        self.prop_combo.addItems(props)
        self.filter_prop_combo.addItems(props)
        
    def update_operation_visibility(self, prop):
        """Enable/disable operations based on property."""
        # Tag and Status can only be replaced
        if prop in ["Tag", "Initial Status"]:
            self.op_replace.setChecked(True)
            self.op_multiply.setEnabled(False)
            self.op_add.setEnabled(False)
        else:
            self.op_multiply.setEnabled(True)
            self.op_add.setEnabled(True)
            
    def toggle_filter(self, state):
        """Enable/disable filter inputs."""
        enabled = state == Qt.Checked
        self.filter_prop_combo.setEnabled(enabled)
        self.filter_rel_combo.setEnabled(enabled)
        self.filter_val_input.setEnabled(enabled)

    def get_data(self):
        """Get dialog data."""
        data = {
            "type": self.type_combo.currentText(),
            "property": self.prop_combo.currentText(),
            "operation": "Replace" if self.op_replace.isChecked() else ("Multiply" if self.op_multiply.isChecked() else "Add"),
            "value": self.val_input.text(),
            "filter": None
        }
        
        if self.filter_chk.isChecked():
            data["filter"] = {
                "property": self.filter_prop_combo.currentText(),
                "relation": self.filter_rel_combo.currentText(),
                "value": self.filter_val_input.text()
            }
            
        return data
    def accept_and_save(self):
        """Save settings and accept."""
        self.save_settings()
        self.accept()

    def load_settings(self):
        """Load dialog settings."""
        settings = QSettings("US EPA", "EPANET 2.2")
        
        # Filter settings
        filter_prop = settings.value("GroupEditDialog/filter_prop")
        filter_rel = settings.value("GroupEditDialog/filter_rel")
        filter_val = settings.value("GroupEditDialog/filter_val")
        
        if filter_prop:
            index = self.filter_prop_combo.findText(filter_prop)
            if index >= 0:
                self.filter_prop_combo.setCurrentIndex(index)
                
        if filter_rel:
            index = self.filter_rel_combo.findText(filter_rel)
            if index >= 0:
                self.filter_rel_combo.setCurrentIndex(index)
                
        if filter_val:
            self.filter_val_input.setText(filter_val)

    def save_settings(self):
        """Save dialog settings."""
        settings = QSettings("US EPA", "EPANET 2.2")
        
        # Filter settings
        settings.setValue("GroupEditDialog/filter_prop", self.filter_prop_combo.currentText())
        settings.setValue("GroupEditDialog/filter_rel", self.filter_rel_combo.currentText())
        settings.setValue("GroupEditDialog/filter_val", self.filter_val_input.text())
