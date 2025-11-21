"""Find Object Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal


class FindObjectDialog(QDialog):
    """Dialog for finding network objects."""
    
    object_selected = Signal(str, str)  # Emits (object_type, object_id)
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Find Object")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Object type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Object Type:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Junctions", "Reservoirs", "Tanks",
            "Pipes", "Pumps", "Valves",
            "Patterns", "Curves"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # Search field
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter ID to search...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Results list
        layout.addWidget(QLabel("Results:"))
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.results_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        find_btn = QPushButton("Find")
        find_btn.clicked.connect(self.find_object)
        find_btn.setDefault(True)
        button_layout.addWidget(find_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Initial population
        self.populate_results()
        
    def on_type_changed(self, type_name: str):
        """Handle object type change."""
        self.search_edit.clear()
        self.populate_results()
        
    def on_search_changed(self, text: str):
        """Handle search text change."""
        self.populate_results(text)
        
    def populate_results(self, filter_text: str = ""):
        """Populate results list based on selected type and filter."""
        self.results_list.clear()
        
        type_name = self.type_combo.currentText()
        network = self.project.network
        
        # Get objects based on type
        objects = []
        if type_name == "Junctions":
            objects = [n.id for n in network.nodes.values() if hasattr(n, 'node_type') and n.node_type.name == 'JUNCTION']
        elif type_name == "Reservoirs":
            objects = [n.id for n in network.nodes.values() if hasattr(n, 'node_type') and n.node_type.name == 'RESERVOIR']
        elif type_name == "Tanks":
            objects = [n.id for n in network.nodes.values() if hasattr(n, 'node_type') and n.node_type.name == 'TANK']
        elif type_name == "Pipes":
            objects = [l.id for l in network.links.values() if hasattr(l, 'link_type') and l.link_type.name == 'PIPE']
        elif type_name == "Pumps":
            objects = [l.id for l in network.links.values() if hasattr(l, 'link_type') and l.link_type.name == 'PUMP']
        elif type_name == "Valves":
            objects = [l.id for l in network.links.values() if hasattr(l, 'link_type') and l.link_type.name == 'VALVE']
        elif type_name == "Patterns":
            objects = list(network.patterns.keys())
        elif type_name == "Curves":
            objects = list(network.curves.keys())
        
        # Filter objects
        if filter_text:
            filter_lower = filter_text.lower()
            objects = [obj for obj in objects if filter_lower in obj.lower()]
        
        # Add to list
        for obj_id in sorted(objects):
            self.results_list.addItem(obj_id)
            
    def on_item_double_clicked(self, item):
        """Handle double-click on result item."""
        self.find_object()
        
    def find_object(self):
        """Find and select the current object."""
        current_item = self.results_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select an object from the list.")
            return
            
        obj_id = current_item.text()
        type_name = self.type_combo.currentText()
        
        # Map type name to object type
        type_map = {
            "Junctions": "Node",
            "Reservoirs": "Node",
            "Tanks": "Node",
            "Pipes": "Link",
            "Pumps": "Link",
            "Valves": "Link",
            "Patterns": "Pattern",
            "Curves": "Curve"
        }
        
        obj_type = type_map.get(type_name, "Node")
        
        # Emit signal
        self.object_selected.emit(obj_type, obj_id)
        
        # Close dialog
        self.accept()
