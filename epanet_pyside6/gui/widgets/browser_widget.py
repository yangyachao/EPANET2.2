"""Browser widget for network components."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from core.project import EPANETProject
from .map_browser import MapBrowser


class ProjectTree(QTreeWidget):
    """Tree widget for browsing network components (internal)."""
    objectActivated = Signal(str, str)
    objectSelected = Signal(str, str)
    objectAdded = Signal(str)  # category
    objectDeleted = Signal(str, str)  # obj_type, obj_id
    
    def __init__(self, project: EPANETProject):
        super().__init__()
        self.project = project
        
        self.setHeaderLabel("Network Components")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.refresh()
        
    def on_item_clicked(self, item, column):
        """Handle single-click on item."""
        # Check if it's an object
        if item.parent():
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0]
            obj_type = self._get_type_from_category(category)
            
            if obj_type:
                object_id = item.text(0)
                self.objectSelected.emit(obj_type, object_id)
                return

        # Check if it's a category
        category_text = item.text(0)
        category = category_text.split(' (')[0]
        if category in ("Patterns", "Curves"):
            obj_type = 'Pattern' if category == "Patterns" else 'Curve'
            # For category selection, we might want to emit something else or nothing
            # The original code emitted objectSelected with the category name as ID?
            # "object_id = item.text(0)" which is "Patterns (N)"
            # Let's keep it simple: if it's a category, maybe we don't need to select an "object"
            pass

    def on_item_double_clicked(self, item, column):
        """Handle double-click on item."""
        # Check if it's an object
        if item.parent():
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0]
            obj_type = self._get_type_from_category(category)
            
            if obj_type:
                object_id = item.text(0)
                self.objectActivated.emit(obj_type, object_id)
                
    def _get_type_from_category(self, category):
        if category in ("Junctions", "Reservoirs", "Tanks"):
            return 'Node'
        elif category in ("Pipes", "Pumps", "Valves"):
            return 'Link'
        elif category == "Patterns":
            return 'Pattern'
        elif category == "Curves":
            return 'Curve'
        elif category in ("Simple Controls", "Rules"):
            return 'Control'
        return None
        
    def refresh(self):
        """Refresh the tree with current network data."""
        self.clear()
        
        # Nodes
        nodes_item = QTreeWidgetItem(self, ["Nodes"])
        nodes_item.setExpanded(True)
        
        self._add_category(nodes_item, "Junctions", self.project.network.get_junctions())
        self._add_category(nodes_item, "Reservoirs", self.project.network.get_reservoirs())
        self._add_category(nodes_item, "Tanks", self.project.network.get_tanks())
        
        # Links
        links_item = QTreeWidgetItem(self, ["Links"])
        links_item.setExpanded(True)
        
        self._add_category(links_item, "Pipes", self.project.network.get_pipes())
        self._add_category(links_item, "Pumps", self.project.network.get_pumps())
        self._add_category(links_item, "Valves", self.project.network.get_valves())
        
        # Others
        patterns_item = QTreeWidgetItem(self, ["Patterns"])
        for pid in self.project.network.patterns:
            QTreeWidgetItem(patterns_item, [pid])
        patterns_item.setText(0, f"Patterns ({len(self.project.network.patterns)})")
        
        curves_item = QTreeWidgetItem(self, ["Curves"])
        for cid in self.project.network.curves:
            QTreeWidgetItem(curves_item, [cid])
        curves_item.setText(0, f"Curves ({len(self.project.network.curves)})")
        
        # Controls & Rules
        controls_item = QTreeWidgetItem(self, ["Controls"])
        controls_item.setText(0, f"Controls ({len(self.project.network.controls) + len(self.project.network.rules)})")
        
        simple_item = QTreeWidgetItem(controls_item, ["Simple Controls"])
        simple_item.setText(0, f"Simple Controls ({len(self.project.network.controls)})")
        
        rules_item = QTreeWidgetItem(controls_item, ["Rules"])
        rules_item.setText(0, f"Rules ({len(self.project.network.rules)})")
        
    def _add_category(self, parent, name, items):
        item = QTreeWidgetItem(parent, [name])
        for obj in items:
            QTreeWidgetItem(item, [obj.id])
        item.setText(0, f"{name} ({len(items)})")
        
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item: return
        
        menu = QMenu(self)
        
        # Check if it's an object (has a parent which is a category)
        is_object = False
        obj_type = None
        object_id = None
        
        if item.parent():
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0]
            obj_type = self._get_type_from_category(category)
            if obj_type:
                is_object = True
                object_id = item.text(0)
        
        if is_object:
            edit_action = menu.addAction("Edit Properties")
            delete_action = menu.addAction("Delete")
            
            action = menu.exec_(self.mapToGlobal(position))
            
            if action == edit_action:
                self.on_item_double_clicked(item, 0)
            elif action == delete_action:
                self.objectDeleted.emit(obj_type, object_id)
                
        else:
            # Check if it's a category that supports adding
            category_text = item.text(0)
            category = category_text.split(' (')[0]
            
            if category in ("Patterns", "Curves"):
                add_action = menu.addAction("Add New...")
                action = menu.exec_(self.mapToGlobal(position))
                
                if action == add_action:
                    self.objectAdded.emit(category)


class BrowserWidget(QTabWidget):
    """Browser widget with Data and Map tabs."""
    
    objectActivated = Signal(str, str)
    object_selected = Signal(str, str)
    objectAdded = Signal(str)
    objectDeleted = Signal(str, str)
    
    def __init__(self, project: EPANETProject, parent=None):
        super().__init__(parent)
        self.project = project
        
        # Data Tab (Tree)
        self.tree = ProjectTree(project)
        self.tree.objectActivated.connect(self.objectActivated)
        self.tree.objectSelected.connect(self.object_selected)
        self.tree.objectAdded.connect(self.objectAdded)
        self.tree.objectDeleted.connect(self.objectDeleted)
        self.addTab(self.tree, "Data")
        
        # Map Tab
        self.map_browser = MapBrowser(project)
        self.addTab(self.map_browser, "Map")
        
    def refresh(self):
        """Refresh the data tree."""
        self.tree.refresh()
