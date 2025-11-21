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
        if item.parent() and item.parent().parent():
            object_id = item.text(0)
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0] if ' (' in category_text else category_text
            
            obj_type = self._get_type_from_category(category)
            if obj_type:
                self.objectActivated.emit(obj_type, object_id)
        elif item.parent() and not item.parent().parent():
            # Category item
            object_id = item.text(0)
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0] if ' (' in category_text else category_text
            
            if category in ("Patterns", "Curves"):
                obj_type = 'Pattern' if category == "Patterns" else 'Curve'
                self.objectActivated.emit(obj_type, object_id)

    def on_item_double_clicked(self, item, column):
        """Handle double-click on item."""
        if item.parent() and item.parent().parent():
            object_id = item.text(0)
            category_text = item.parent().text(0)
            category = category_text.split(' (')[0] if ' (' in category_text else category_text
            
            obj_type = self._get_type_from_category(category)
            if obj_type:
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
        
    def _add_category(self, parent, name, items):
        item = QTreeWidgetItem(parent, [name])
        for obj in items:
            QTreeWidgetItem(item, [obj.id])
        item.setText(0, f"{name} ({len(items)})")
        
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item: return
        
        menu = QMenu(self)
        if item.parent() and item.parent().parent():
            edit_action = menu.addAction("Edit Properties")
            delete_action = menu.addAction("Delete")
            action = menu.exec_(self.mapToGlobal(position))
            if action == edit_action:
                self.on_item_double_clicked(item, 0)
        else:
            add_action = menu.addAction("Add New...")
            menu.exec_(self.mapToGlobal(position))


class BrowserWidget(QTabWidget):
    """Browser widget with Data and Map tabs."""
    
    objectActivated = Signal(str, str)
    
    def __init__(self, project: EPANETProject):
        super().__init__()
        self.project = project
        
        # Data Tab (Tree)
        self.tree = ProjectTree(project)
        self.tree.objectActivated.connect(self.objectActivated)
        self.addTab(self.tree, "Data")
        
        # Map Tab
        self.map_browser = MapBrowser(project)
        self.addTab(self.map_browser, "Map")
        
    def refresh(self):
        """Refresh the data tree."""
        self.tree.refresh()
