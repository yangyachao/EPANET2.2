"""Graphics scene for EPANET network map."""

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPen, QColor, QBrush, QPixmap, QFont
from .items import JunctionItem, ReservoirItem, TankItem, PipeItem, PumpItem, ValveItem, LabelItem
from core.constants import NodeType, LinkType

class NetworkScene(QGraphicsScene):
    """Graphics scene for network display."""
    
    selectionChanged = Signal(object)  # Emits the selected object (Node or Link) or None

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.node_items = {}
        self.link_items = {}
        self.backdrop_item = None
        self.max_y = 0
        
        # Set scene background
        self.setBackgroundBrush(QBrush(Qt.white))
        
        self.selectionChanged.connect(self.on_selection_changed)
        self.load_network()

    def update_scene_rect(self):
        """Update scene rectangle based on map dimensions."""
        bounds = self.project.network.map_bounds
        min_x = bounds.get('min_x', 0.0)
        min_y = bounds.get('min_y', 0.0)
        max_x = bounds.get('max_x', 10000.0)
        max_y = bounds.get('max_y', 10000.0)
        
        # Handle empty network or uninitialized bounds
        if min_x == float('inf'): min_x = 0.0
        if min_y == float('inf'): min_y = 0.0
        if max_x == float('-inf'): max_x = 10000.0
        if max_y == float('-inf'): max_y = 10000.0
            
        # Ensure valid dimensions
        if max_x <= min_x: max_x = min_x + 10000.0
        if max_y <= min_y: max_y = min_y + 10000.0
        
        # Convert to Qt coordinates (Y flipped)
        # EPANET: min_y (bottom) to max_y (top)
        # Qt: -max_y (top) to -min_y (bottom)
        
        qt_min_y = -max_y
        qt_max_y = -min_y
        
        width = max_x - min_x
        height = qt_max_y - qt_min_y
        
        self.setSceneRect(min_x, qt_min_y, width, height)

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
            elif hasattr(item, 'label'):
                self.selectionChanged.emit(item.label)
        else:
            self.selectionChanged.emit(None)

    def load_network(self):
        """Load network objects into the scene."""
        self.clear()
        self.node_items.clear()
        self.link_items.clear()
        
        network = self.project.network
        
        network = self.project.network
        
        # Add Nodes (with Y-axis flipping handled in Item)
        if network.nodes:
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
            
        # Add Labels
        if hasattr(network, 'labels'):
            for label in network.labels.values():
                item = LabelItem(label)
                self.addItem(item)
                
        self.update_scene_rect()

    def add_node(self, node_id):
        """Add a specific node to the scene."""
        if node_id not in self.project.network.nodes:
            return
            
        node = self.project.network.nodes[node_id]
        
        if node.node_type == NodeType.JUNCTION:
            item = JunctionItem(node)
        elif node.node_type == NodeType.RESERVOIR:
            item = ReservoirItem(node)
        elif node.node_type == NodeType.TANK:
            item = TankItem(node)
        else:
            return
            
        self.addItem(item)
        self.node_items[node.id] = item
        item.setZValue(1)
        
    def add_link(self, link_id):
        """Add a specific link to the scene."""
        if link_id not in self.project.network.links:
            return
            
        link = self.project.network.links[link_id]
        
        if link.from_node not in self.node_items or link.to_node not in self.node_items:
            return
            
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
        item.setZValue(0)

    def add_label(self, label_id):
        """Add a specific label to the scene."""
        if not hasattr(self.project.network, 'labels') or label_id not in self.project.network.labels:
            return
            
        label = self.project.network.labels[label_id]
        item = LabelItem(label)
        self.addItem(item)

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
                
                # Update value label text
                if hasattr(item, 'value_label'):
                    item.value_label.setText(f"{val:.2f}")
                    # Update position to ensure centering
                    if hasattr(item, 'update_label_positions'):
                        item.update_label_positions()
            else:
                item.set_color(None)
                # Reset label text if needed, or keep last known? 
                # Better to clear or show default if no value
                if hasattr(item, 'value_label'):
                    item.value_label.setText("0.00")
                    if hasattr(item, 'update_label_positions'):
                        item.update_label_positions()
                
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
                
                # Update value label text
                if hasattr(item, 'value_label'):
                    item.value_label.setText(f"{val:.2f}")
                    # Update position to ensure centering
                    if hasattr(item, 'update_label_positions'):
                        item.update_label_positions()
            else:
                item.set_color(None)
                if hasattr(item, 'value_label'):
                    item.value_label.setText("0.00")
                    if hasattr(item, 'update_label_positions'):
                        item.update_label_positions()
                
    def _get_color_for_value(self, value, colors, intervals):
        """Get color for a value based on legend intervals."""
        if value <= intervals[0]:
            return colors[0]
        if value >= intervals[-1]:
            return colors[-1]
            
        for i in range(len(intervals) - 1):
            if intervals[i] <= value < intervals[i+1]:
                return colors[i]
                
        return colors[-1]
    
    def set_backdrop(self, image_path, ul_x, ul_y, lr_x, lr_y):
        """Set backdrop image."""
        from PySide6.QtWidgets import QGraphicsPixmapItem
        
        if self.backdrop_item:
            self.removeItem(self.backdrop_item)
            self.backdrop_item = None
            
        if not image_path:
            return
            
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return
            
        self.backdrop_item = QGraphicsPixmapItem(pixmap)
        self.addItem(self.backdrop_item)
        self.backdrop_item.setZValue(-100) # Ensure it's at the bottom
        
        # Scale and position
        world_w = abs(lr_x - ul_x)
        world_h = abs(ul_y - lr_y)
        
        if world_w == 0 or world_h == 0:
            return
            
        # Calculate scale factors
        img_w = pixmap.width()
        img_h = pixmap.height()
        
        scale_x = world_w / img_w
        scale_y = world_h / img_h
        
        # Apply transformation
        self.backdrop_item.resetTransform()
        
        scene_x = ul_x
        scene_y = self.max_y - ul_y
        
        self.backdrop_item.setPos(scene_x, scene_y)
        
        self.backdrop_item.setScale(scale_x) 
        self.backdrop_item.setTransform(self.backdrop_item.transform().scale(1, scale_y/scale_x))
        
    def clear_backdrop(self):
        """Remove backdrop image."""
        if self.backdrop_item:
            self.removeItem(self.backdrop_item)
            self.backdrop_item = None
            
    def toggle_backdrop(self, visible):
        """Toggle backdrop visibility."""
        if self.backdrop_item:
            self.backdrop_item.setVisible(visible)
    
    def apply_map_options(self, options):
        """Apply map display options to the scene."""
        if not options:
            return
        
        # Apply node options
        node_size = options.get('node_size', 3)
        display_node_border = options.get('display_node_border', True)
        display_node_ids = options.get('display_node_ids', False)
        display_node_values = options.get('display_node_values', False)
        notation_font_size = options.get('notation_font_size', 8)
        
        for node_id, item in self.node_items.items():
            # Update node size (radius in pixels)
            # Default radius is 3.0 (from items.py)
            # node_size is an integer, let's use it directly as radius or scale factor
            # Delphi: Size 0-10? 
            # Let's map node_size (e.g. 5) to radius.
            # Base radius = node_size
            radius = float(node_size)
            item.setRect(-radius, -radius, radius*2, radius*2)
            item.radius = radius
            
            # Update border visibility
            if display_node_border:
                pen = item.pen()
                pen.setWidth(1) # Cosmetic pen width 1
                item.setPen(pen)
            else:
                item.setPen(QPen(Qt.NoPen))
                
            # Update ID label
            if hasattr(item, 'id_label'):
                item.id_label.setVisible(display_node_ids)
                font = item.id_label.font()
                font.setPointSize(notation_font_size)
                item.id_label.setFont(font)
            
            # Update Value label
            if hasattr(item, 'value_label'):
                item.value_label.setVisible(display_node_values)
                # TODO: Set actual value text based on current time step
                item.value_label.setText("0.00") 
                font = item.value_label.font()
                font.setPointSize(notation_font_size)
                item.value_label.setFont(font)
                
            # Update label positions
            if hasattr(item, 'update_label_positions'):
                item.update_label_positions()
        
        # Apply link options
        link_size = options.get('link_size', 1)
        display_link_border = options.get('display_link_border', False)
        display_link_ids = options.get('display_link_ids', False)
        display_link_values = options.get('display_link_values', False)
        
        for link_id, item in self.link_items.items():
            # Update link width (pixels)
            pen = item.pen()
            pen.setWidth(link_size)
            item.setPen(pen)
            
            # Update ID label
            if hasattr(item, 'id_label'):
                item.id_label.setVisible(display_link_ids)
                font = item.id_label.font()
                font.setPointSize(notation_font_size)
                item.id_label.setFont(font)
                
            # Update Value label
            if hasattr(item, 'value_label'):
                item.value_label.setVisible(display_link_values)
                # TODO: Set actual value text based on current time step
                item.value_label.setText("0.00")
                font = item.value_label.font()
                font.setPointSize(notation_font_size)
                item.value_label.setFont(font)
                
            # Update label positions
            if hasattr(item, 'update_label_positions'):
                item.update_label_positions()
        
        # Update the scene
        self.update()
