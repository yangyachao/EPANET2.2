"""Browser widget for network components."""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Qt, Signal
from core.project import EPANETProject


class BrowserWidget(QTreeWidget):
    """Tree widget for browsing network components."""
    # Emits (obj_type, obj_id) where obj_type is 'Node' or 'Link'
    objectActivated = Signal(str, str)
    
    def __init__(self, project: EPANETProject):
        super().__init__()
        self.project = project
        
        self.setHeaderLabel("Network Components")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.refresh()
    
    def on_item_clicked(self, item, column):
        """Handle single-click on item: activate if it's a leaf object."""
        if item.parent() and item.parent().parent():
            # This is an object item (leaf node)
            object_id = item.text(0)
            category_text = item.parent().text(0)
            # Extract category name (remove count suffix like " (12)")
            category = category_text.split(' (')[0] if ' (' in category_text else category_text

            # Determine whether it's a node or link
            if category in ("Junctions", "Reservoirs", "Tanks"):
                obj_type = 'Node'
            else:
                obj_type = 'Link'

            # Emit signal so main window can respond (same as double-click)
            self.objectActivated.emit(obj_type, object_id)
    
    def refresh(self):
        """Refresh the tree with current network data."""
        self.clear()
        
        # Nodes
        nodes_item = QTreeWidgetItem(self, ["Nodes"])
        nodes_item.setExpanded(True)
        
        # Junctions
        juncs_item = QTreeWidgetItem(nodes_item, ["Junctions"])
        for junction in self.project.network.get_junctions():
            QTreeWidgetItem(juncs_item, [junction.id])
        juncs_item.setText(0, f"Junctions ({len(self.project.network.get_junctions())})")
        
        # Reservoirs
        reservs_item = QTreeWidgetItem(nodes_item, ["Reservoirs"])
        for reservoir in self.project.network.get_reservoirs():
            QTreeWidgetItem(reservs_item, [reservoir.id])
        reservs_item.setText(0, f"Reservoirs ({len(self.project.network.get_reservoirs())})")
        
        # Tanks
        tanks_item = QTreeWidgetItem(nodes_item, ["Tanks"])
        for tank in self.project.network.get_tanks():
            QTreeWidgetItem(tanks_item, [tank.id])
        tanks_item.setText(0, f"Tanks ({len(self.project.network.get_tanks())})")
        
        # Links
        links_item = QTreeWidgetItem(self, ["Links"])
        links_item.setExpanded(True)
        
        # Pipes
        pipes_item = QTreeWidgetItem(links_item, ["Pipes"])
        for pipe in self.project.network.get_pipes():
            QTreeWidgetItem(pipes_item, [pipe.id])
        pipes_item.setText(0, f"Pipes ({len(self.project.network.get_pipes())})")
        
        # Pumps
        pumps_item = QTreeWidgetItem(links_item, ["Pumps"])
        for pump in self.project.network.get_pumps():
            QTreeWidgetItem(pumps_item, [pump.id])
        pumps_item.setText(0, f"Pumps ({len(self.project.network.get_pumps())})")
        
        # Valves
        valves_item = QTreeWidgetItem(links_item, ["Valves"])
        for valve in self.project.network.get_valves():
            QTreeWidgetItem(valves_item, [valve.id])
        valves_item.setText(0, f"Valves ({len(self.project.network.get_valves())})")
        
        # Patterns
        patterns_item = QTreeWidgetItem(self, ["Patterns"])
        for pattern_id in self.project.network.patterns:
            QTreeWidgetItem(patterns_item, [pattern_id])
        patterns_item.setText(0, f"Patterns ({len(self.project.network.patterns)})")
        
        # Curves
        curves_item = QTreeWidgetItem(self, ["Curves"])
        for curve_id in self.project.network.curves:
            QTreeWidgetItem(curves_item, [curve_id])
        curves_item.setText(0, f"Curves ({len(self.project.network.curves)})")
    
    def on_item_double_clicked(self, item, column):
        """Handle double-click on item."""
        # Get the object ID
        if item.parent() and item.parent().parent():
            object_id = item.text(0)
            category_text = item.parent().text(0)
            # Extract category name (remove count suffix like " (12)")
            category = category_text.split(' (')[0] if ' (' in category_text else category_text

            # Determine whether it's a node or link
            if category in ("Junctions", "Reservoirs", "Tanks"):
                obj_type = 'Node'
            else:
                obj_type = 'Link'

            # Emit signal so main window can respond
            self.objectActivated.emit(obj_type, object_id)
    
    def show_context_menu(self, position):
        """Show context menu."""
        item = self.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # Add actions based on item type
        if item.parent() and item.parent().parent():
            # This is an object item
            edit_action = menu.addAction("Edit Properties")
            delete_action = menu.addAction("Delete")

            action = menu.exec_(self.mapToGlobal(position))

            if action == edit_action:
                self.on_item_double_clicked(item, 0)
            elif action == delete_action:
                # TODO: Implement delete
                pass
        else:
            # This is a category item
            add_action = menu.addAction("Add New...")
            menu.exec_(self.mapToGlobal(position))
