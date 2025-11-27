from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTabWidget, QListWidget, 
                               QDialogButtonBox, QWidget)
from PySide6.QtCore import Qt, Signal

class FindObjectDialog(QDialog):
    """Dialog to find nodes or links by ID."""
    
    object_selected = Signal(str, str) # type (Node/Link), id
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Find Object")
        self.resize(300, 400)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Nodes Tab
        self.nodes_list = QListWidget()
        self.nodes_list.itemDoubleClicked.connect(self.accept_selection)
        self.tabs.addTab(self.nodes_list, "Nodes")
        
        # Links Tab
        self.links_list = QListWidget()
        self.links_list.itemDoubleClicked.connect(self.accept_selection)
        self.tabs.addTab(self.links_list, "Links")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Ok).setText("Find")
        layout.addWidget(button_box)
        
    def load_data(self):
        """Load nodes and links into lists."""
        self.nodes_list.clear()
        self.links_list.clear()
        
        # Load Nodes
        if self.project.network.nodes:
            # Sort by ID for easier finding
            sorted_nodes = sorted(self.project.network.nodes.keys())
            self.nodes_list.addItems(sorted_nodes)
            
        # Load Links
        if self.project.network.links:
            sorted_links = sorted(self.project.network.links.keys())
            self.links_list.addItems(sorted_links)
            
    def apply_filter(self, text):
        """Filter the current list."""
        current_list = self.nodes_list if self.tabs.currentIndex() == 0 else self.links_list
        
        for i in range(current_list.count()):
            item = current_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def accept_selection(self):
        """Handle selection and emit signal."""
        current_list = self.nodes_list if self.tabs.currentIndex() == 0 else self.links_list
        selected_items = current_list.selectedItems()
        
        if selected_items:
            obj_id = selected_items[0].text()
            obj_type = "Node" if self.tabs.currentIndex() == 0 else "Link"
            self.object_selected.emit(obj_type, obj_id)
            self.accept()
