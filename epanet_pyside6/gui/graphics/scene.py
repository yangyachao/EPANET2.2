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
        self.node_scale = 1.0  # Will be calculated based on network bounds
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
        
        # Calculate adaptive node size based on network bounds
        self.node_scale = self._calculate_node_scale(network)
        
        # Calculate Y-axis flip (EPANET Y goes up, Qt Y goes down)
        if network.nodes:
            self.max_y = max(node.y for node in network.nodes.values())
        else:
            self.max_y = 0
        
        # Add Nodes (with Y-axis flipping)
        for node in network.nodes.values():
            if node.node_type == NodeType.JUNCTION:
                item = JunctionItem(node, scale=self.node_scale, max_y=self.max_y)
            elif node.node_type == NodeType.RESERVOIR:
                item = ReservoirItem(node, scale=self.node_scale, max_y=self.max_y)
            elif node.node_type == NodeType.TANK:
                item = TankItem(node, scale=self.node_scale, max_y=self.max_y)
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
                item = PipeItem(link, from_pos, to_pos, scale=self.node_scale)
            elif link.link_type == LinkType.PUMP:
                item = PumpItem(link, from_pos, to_pos, scale=self.node_scale)
            else: # Valve
                item = ValveItem(link, from_pos, to_pos, scale=self.node_scale)
                
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
                
    def update_node_colors(self, values, legend_colors, legend_values):
        """Update node colors based on values and legend."""
        if not values:
            # Reset to default
            for item in self.node_items.values():
                item.set_color(None)
            return
            
        for node_id, item in self.node_items.items():
            if node_id in values:
                val = values[node_id]
                color = self._get_color_for_value(val, legend_colors, legend_values)
                item.set_color(color)
            else:
                item.set_color(None)
                
    def update_link_colors(self, values, legend_colors, legend_values):
        """Update link colors based on values and legend."""
        if not values:
            # Reset to default
            for item in self.link_items.values():
                item.set_color(None)
            return
            
        for link_id, item in self.link_items.items():
            if link_id in values:
                val = values[link_id]
                color = self._get_color_for_value(val, legend_colors, legend_values)
                item.set_color(color)
            else:
                item.set_color(None)
                
    def _get_color_for_value(self, value, colors, intervals):
        """Get color for a value based on legend intervals."""
        # Simple interval matching
        # intervals: [0, 25, 50, 75, 100]
        # colors: [blue, cyan, green, yellow, red]
        # value < 0 -> blue
        # 0 <= value < 25 -> blue
        # 25 <= value < 50 -> cyan
        # ...
        
        if value <= intervals[0]:
            return colors[0]
        if value >= intervals[-1]:
            return colors[-1]
            
        for i in range(len(intervals) - 1):
            if intervals[i] <= value < intervals[i+1]:
                return colors[i]
                
        return colors[-1]
    
    def _calculate_node_scale(self, network):
        """Calculate appropriate node scale based on network bounds.
        
        Returns a scale factor that makes nodes ~1% of the smaller dimension.
        """
        if not network.nodes:
            return 1.0
        
        # Get network bounds
        min_x = min(node.x for node in network.nodes.values())
        max_x = max(node.x for node in network.nodes.values())
        min_y = min(node.y for node in network.nodes.values())
        max_y = max(node.y for node in network.nodes.values())
        
        # Calculate dimensions
        width = max_x - min_x
        height = max_y - min_y
        
        # Avoid division by zero
        if width == 0 or height == 0:
            return 1.0
        
        # Node size should be ~1% of the smaller dimension
        # This ensures nodes are visible but not too large
        smaller_dim = min(width, height)
        scale = smaller_dim * 0.01
        
        # Dynamic minimum scale based on coordinate range magnitude
        # For GPS coordinates (range < 1), use smaller scale for less overlap
        # For normal coordinates (range > 100), use larger minimum
        if smaller_dim < 1:
            min_scale = 0.0003  # GPS coordinates - reduced to avoid overlap
        elif smaller_dim < 100:
            min_scale = 0.3     # Medium range coordinates
        else:
            min_scale = 10.0    # Large range coordinates
        
        return max(scale, min_scale)
