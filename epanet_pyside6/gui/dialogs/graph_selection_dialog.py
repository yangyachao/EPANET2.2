"""Dialog for selecting graph options."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QRadioButton, QButtonGroup, QListWidget, QPushButton, 
    QDialogButtonBox, QGroupBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from core.constants import NodeParam, LinkParam

class GraphSelectionDialog(QDialog):
    """Dialog for selecting graph type, parameter, and objects."""
    
    def __init__(self, project, parent=None, initial_type="Time Series"):
        super().__init__(parent)
        self.project = project
        self.initial_type = initial_type
        self.setWindowTitle("Graph Selection")
        self.resize(400, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Graph Type Group
        type_group = QGroupBox("Graph Type")
        type_layout = QVBoxLayout()
        
        self.ts_radio = QRadioButton("Time Series")
        self.profile_radio = QRadioButton("Profile Plot")
        self.contour_radio = QRadioButton("Contour Plot")
        self.freq_radio = QRadioButton("Frequency Plot")
        self.flow_radio = QRadioButton("System Flow")
        
        if self.initial_type == "Time Series":
            self.ts_radio.setChecked(True)
        elif self.initial_type == "Profile":
            self.profile_radio.setChecked(True)
        elif self.initial_type == "Contour":
            self.contour_radio.setChecked(True)
        elif self.initial_type == "Frequency":
            self.freq_radio.setChecked(True)
        elif self.initial_type == "System Flow":
            self.flow_radio.setChecked(True)
        
        # Group buttons
        self.type_bg = QButtonGroup(self)
        self.type_bg.addButton(self.ts_radio)
        self.type_bg.addButton(self.profile_radio)
        self.type_bg.addButton(self.contour_radio)
        self.type_bg.addButton(self.freq_radio)
        self.type_bg.addButton(self.flow_radio)
        
        type_layout.addWidget(self.ts_radio)
        type_layout.addWidget(self.profile_radio)
        type_layout.addWidget(self.contour_radio)
        type_layout.addWidget(self.freq_radio)
        type_layout.addWidget(self.flow_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Parameter Selection
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Parameter:"))
        self.param_combo = QComboBox()
        param_layout.addWidget(self.param_combo)
        layout.addLayout(param_layout)
        
        # Object Type Selection (Nodes vs Links)
        obj_type_layout = QHBoxLayout()
        obj_type_layout.addWidget(QLabel("Object Type:"))
        
        self.node_radio = QRadioButton("Nodes")
        self.node_radio.setChecked(True)
        self.link_radio = QRadioButton("Links")
        
        self.obj_type_bg = QButtonGroup(self)
        self.obj_type_bg.addButton(self.node_radio)
        self.obj_type_bg.addButton(self.link_radio)
        
        self.obj_type_bg.buttonToggled.connect(self.on_object_type_changed)
        
        obj_type_layout.addWidget(self.node_radio)
        obj_type_layout.addWidget(self.link_radio)
        obj_type_layout.addStretch()
        layout.addLayout(obj_type_layout)
        
        # Object Selection List
        self.obj_list = QListWidget()
        self.obj_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(QLabel("Select Objects:"))
        layout.addWidget(self.obj_list)
        
        # Add/Remove buttons (simplified for now, just use list selection)
        # In full implementation, we might want "Add" button that lets you click on map
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize
        self.on_object_type_changed(self.node_radio, True)
        
    def on_object_type_changed(self, button, checked):
        """Handle object type change."""
        if not checked:
            return
            
        is_node = (button == self.node_radio)
        
        # Update parameters
        self.param_combo.clear()
        if is_node:
            for param in NodeParam:
                self.param_combo.addItem(param.name, param)
        else:
            for param in LinkParam:
                self.param_combo.addItem(param.name, param)
                
        # Update object list
        self.obj_list.clear()
        if is_node:
            items = sorted(self.project.network.nodes.keys())
        else:
            items = sorted(self.project.network.links.keys())
            
        self.obj_list.addItems(items)
        
    def get_selection(self):
        """Get the selected options."""
        # Graph Type
        if self.ts_radio.isChecked():
            graph_type = "Time Series"
        elif self.profile_radio.isChecked():
            graph_type = "Profile"
        elif self.contour_radio.isChecked():
            graph_type = "Contour"
        elif self.freq_radio.isChecked():
            graph_type = "Frequency"
        elif self.flow_radio.isChecked():
            graph_type = "System Flow"
        else:
            graph_type = "Other"
            
        # Object Type
        obj_type = "Node" if self.node_radio.isChecked() else "Link"
        
        # Parameter
        param = self.param_combo.currentData()
        
        # Selected Objects
        selected_items = self.obj_list.selectedItems()
        objects = [item.text() for item in selected_items]
        
        return {
            'graph_type': graph_type,
            'object_type': obj_type,
            'parameter': param,
            'objects': objects
        }
