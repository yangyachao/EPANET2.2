"""Graphics scene for EPANET network map."""

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, Signal
from .items import JunctionItem, ReservoirItem, TankItem, PipeItem, PumpItem, ValveItem
from core.constants import NodeType, LinkType

class NetworkScene(QGraphicsScene):
    """Custom graphics scene for network editing."""
    
    selectionChanged = Signal(object)  # Emits the selected object (Node or Link) or None

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.node_items = {}
        self.link_items = {}
        
        self.selectionChanged.connect(self.on_selection_changed)
        self.load_network()

    def on_selection_changed(self):
        """Handle internal selection changes."""
        # This is just a placeholder if we need internal logic
        pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Check selection
        selected_items = self.selectedItems()
        if selected_items:
            # Prioritize nodes over links if multiple selected (though usually one)
            item = selected_items[0]
            if hasattr(item, 'node'):
                self.selectionChanged.emit(item.node)
            elif hasattr(item, 'link'):
                self.selectionChanged.emit(item.link)
        else:
            self.selectionChanged.emit(None)

    def load_network(self):
        """Load network objects into the scene."""
        self.clear()
        self.node_items.clear()
        self.link_items.clear()
        
        network = self.project.network
        
        # Add Nodes
        for node in network.nodes.values():
            if node.node_type == NodeType.JUNCTION:
                item = JunctionItem(node)
            elif node.node_type == NodeType.RESERVOIR:
                item = ReservoirItem(node)
            elif node.node_type == NodeType.TANK:
                item = TankItem(node)
            else:
                continue
                
            self.addItem(item)
            self.node_items[node.id] = item
            
        # Add Links
        for link in network.links.values():
            if link.from_node not in self.node_items or link.to_node not in self.node_items:
                continue
                
            from_pos = self.node_items[link.from_node].pos()
            to_pos = self.node_items[link.to_node].pos()
            
            if link.link_type == LinkType.PIPE:
                item = PipeItem(link, from_pos, to_pos)
            elif link.link_type == LinkType.PUMP:
                item = PumpItem(link, from_pos, to_pos)
            else: # Valve
                item = ValveItem(link, from_pos, to_pos)
                
            self.addItem(item)
            self.link_items[link.id] = item
            
            # Ensure nodes are on top of links
            item.setZValue(0)
            
        for item in self.node_items.values():
            item.setZValue(1)

    def update_connected_links(self, node_id):
        """Update links connected to a moving node."""
        if node_id not in self.node_items:
            return
            
        node_pos = self.node_items[node_id].pos()
        
        # Find links connected to this node
        # This is inefficient for large networks, should optimize later
        for link_id, item in self.link_items.items():
            if item.link.from_node == node_id:
                item.update_positions(node_pos, item.to_pos)
            elif item.link.to_node == node_id:
                item.update_positions(item.from_pos, node_pos)
