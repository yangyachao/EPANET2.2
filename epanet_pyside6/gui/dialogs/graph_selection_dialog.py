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
    
    def __init__(self, project, parent=None, initial_type="Time Series", initial_selection=None, initial_obj_type=None):
        super().__init__(parent)
        self.project = project
        self.initial_type = initial_type
        self.initial_selection = initial_selection or []
        self.initial_obj_type = initial_obj_type # "Node" or "Link"
        
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
        
        # Set initial check
        if self.initial_type == "Time Series": self.ts_radio.setChecked(True)
        elif self.initial_type == "Profile": self.profile_radio.setChecked(True)
        elif self.initial_type == "Contour": self.contour_radio.setChecked(True)
        elif self.initial_type == "Frequency": self.freq_radio.setChecked(True)
        elif self.initial_type == "System Flow": self.flow_radio.setChecked(True)
        else: self.ts_radio.setChecked(True)
        
        # Group buttons
        self.type_bg = QButtonGroup(self)
        self.type_bg.addButton(self.ts_radio)
        self.type_bg.addButton(self.profile_radio)
        self.type_bg.addButton(self.contour_radio)
        self.type_bg.addButton(self.freq_radio)
        self.type_bg.addButton(self.flow_radio)
        
        self.type_bg.buttonToggled.connect(self.on_graph_type_changed)
        
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
        self.obj_type_group = QWidget()
        obj_type_layout = QHBoxLayout(self.obj_type_group)
        obj_type_layout.setContentsMargins(0, 0, 0, 0)
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
        layout.addWidget(self.obj_type_group)
        
        # Object Selection List (for Time Series, Frequency)
        self.list_group = QWidget()
        list_layout = QVBoxLayout(self.list_group)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.addWidget(QLabel("Select Objects:"))
        self.obj_list = QListWidget()
        self.obj_list.setSelectionMode(QListWidget.MultiSelection)
        list_layout.addWidget(self.obj_list)
        layout.addWidget(self.list_group)
        
        # Profile Selection (Start/End Nodes)
        self.profile_group = QWidget()
        profile_layout = QVBoxLayout(self.profile_group)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Node:"))
        self.start_node_combo = QComboBox()
        start_layout.addWidget(self.start_node_combo)
        profile_layout.addLayout(start_layout)
        
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Node:"))
        self.end_node_combo = QComboBox()
        end_layout.addWidget(self.end_node_combo)
        profile_layout.addLayout(end_layout)
        
        self.find_path_btn = QPushButton("Find Path")
        # In a real app, this might preview the path. For now, just visual.
        profile_layout.addWidget(self.find_path_btn)
        
        layout.addWidget(self.profile_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize
        self.populate_nodes_links()
        
        # Trigger initial state update
        self.on_graph_type_changed(self.type_bg.checkedButton(), True)
        
        # Explicitly update list for the initial type
        self.update_list()
        
        # Apply initial selection if Time Series
        if self.initial_type == "Time Series" and self.initial_selection:
            if self.initial_obj_type == "Link":
                self.link_radio.setChecked(True)
            else:
                self.node_radio.setChecked(True)
            
            # Re-update list after setting radio button
            self.update_list()
                
            for i in range(self.obj_list.count()):
                item = self.obj_list.item(i)
                if item.text() in self.initial_selection:
                    item.setSelected(True)
                    
    def populate_nodes_links(self):
        """Populate combo boxes and lists."""
        nodes = sorted(self.project.network.nodes.keys())
        links = sorted(self.project.network.links.keys())
        
        self.start_node_combo.addItems(nodes)
        self.end_node_combo.addItems(nodes)
        
        # List is populated in update_list called during initialization
        
    def on_graph_type_changed(self, button, checked):
        """Handle graph type change."""
        if not checked: return
        
        graph_type = button.text()
        
        # Default visibility
        self.obj_type_group.setVisible(True)
        self.list_group.setVisible(True)
        self.profile_group.setVisible(False)
        self.param_combo.setEnabled(True)
        
        if graph_type == "Time Series":
            self.obj_list.setSelectionMode(QListWidget.MultiSelection)
            self.update_parameters()
            self.update_list()
            
        elif graph_type == "Profile Plot":
            self.obj_type_group.setVisible(False) # Always Nodes for profile path? Or links? Usually nodes.
            self.list_group.setVisible(False)
            self.profile_group.setVisible(True)
            # Profile is usually for Node parameters (Head, Pressure, Quality) along a path
            # But can also be Link parameters? EPANET usually does Node parameters for profile.
            self.update_parameters(force_type="Node")
            
        elif graph_type == "Contour Plot":
            self.obj_type_group.setVisible(False) # Usually just Node parameters
            self.list_group.setVisible(False) # No specific objects, it's the whole map
            self.update_parameters(force_type="Node")
            
        elif graph_type == "Frequency Plot":
            self.obj_list.setSelectionMode(QListWidget.ExtendedSelection) # Allow selecting subset or all
            self.update_parameters()
            self.update_list()
            
        elif graph_type == "System Flow":
            self.obj_type_group.setVisible(False)
            self.list_group.setVisible(False)
            self.param_combo.setEnabled(False) # Fixed parameter (Flow/Demand)
            self.param_combo.clear()
            self.param_combo.addItem("System Flow/Demand")
            
    def on_object_type_changed(self, button, checked):
        """Handle object type change."""
        if not checked: return
        self.update_parameters()
        self.update_list()
        
    def update_parameters(self, force_type=None):
        """Update parameter combo based on object type."""
        self.param_combo.clear()
        
        is_node = self.node_radio.isChecked()
        if force_type == "Node": is_node = True
        elif force_type == "Link": is_node = False
        
        if is_node:
            for param in NodeParam:
                self.param_combo.addItem(param.name, param)
            default = NodeParam.PRESSURE
        else:
            for param in LinkParam:
                self.param_combo.addItem(param.name, param)
            default = LinkParam.FLOW
            
        index = self.param_combo.findData(default)
        if index >= 0: self.param_combo.setCurrentIndex(index)
        
    def update_list(self):
        """Update object list."""
        self.obj_list.clear()
        if self.node_radio.isChecked():
            items = sorted(self.project.network.nodes.keys())
        else:
            items = sorted(self.project.network.links.keys())
        self.obj_list.addItems(items)
        
    def get_selection(self):
        """Get the selected options."""
        # Graph Type
        if self.ts_radio.isChecked(): graph_type = "Time Series"
        elif self.profile_radio.isChecked(): graph_type = "Profile"
        elif self.contour_radio.isChecked(): graph_type = "Contour"
        elif self.freq_radio.isChecked(): graph_type = "Frequency"
        elif self.flow_radio.isChecked(): graph_type = "System Flow"
        else: graph_type = "Other"
            
        # Object Type
        obj_type = "Node"
        if self.link_radio.isChecked():
            obj_type = "Link"
        # Force Node for Profile/Contour if needed, but the radio buttons are hidden so check state might be stale?
        # Actually, if hidden, we should rely on what makes sense for the plot type.
        if graph_type in ["Profile", "Contour"]:
            obj_type = "Node"
        
        # Parameter
        param = self.param_combo.currentData()
        
        # Selected Objects
        objects = []
        if graph_type == "Profile":
            objects = [self.start_node_combo.currentText(), self.end_node_combo.currentText()]
        elif graph_type in ["Time Series", "Frequency"]:
            selected_items = self.obj_list.selectedItems()
            objects = [item.text() for item in selected_items]
            # If Frequency and no selection, assume ALL?
            if graph_type == "Frequency" and not objects:
                # Return all items in list
                objects = [self.obj_list.item(i).text() for i in range(self.obj_list.count())]
        
        return {
            'graph_type': graph_type,
            'object_type': obj_type,
            'parameter': param,
            'objects': objects
        }
