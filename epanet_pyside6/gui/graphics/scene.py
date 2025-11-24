"""Graphics scene for EPANET network map."""

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPen, QColor, QBrush, QPixmap
from .items import JunctionItem, ReservoirItem, TankItem, PipeItem, PumpItem, ValveItem
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
        
        # Set scene background
        self.setBackgroundBrush(QBrush(Qt.white))
        
        self.selectionChanged.connect(self.on_selection_changed)
        self.node_scale = 1.0  # Will be calculated based on network bounds
        self.load_network()

    def update_scene_rect(self):
        """Update scene rectangle based on map dimensions."""
        bounds = self.project.network.map_bounds
        min_x = bounds.get('min_x', 0.0)
        min_y = bounds.get('min_y', 0.0)
        max_x = bounds.get('max_x', 10000.0)
        max_y = bounds.get('max_y', 10000.0)
        
        # Handle empty network or uninitialized bounds
        if min_x == float('inf'):
            min_x = 0.0
        if min_y == float('inf'):
            min_y = 0.0
        if max_x == float('-inf'):
            max_x = 10000.0
        if max_y == float('-inf'):
            max_y = 10000.0
            
        # Ensure valid dimensions
        if max_x <= min_x:
            max_x = min_x + 10000.0
        if max_y <= min_y:
            max_y = min_y + 10000.0
        
        width = max_x - min_x
        height = max_y - min_y
        
        # We use self.max_y to flip coordinates.
        if hasattr(self, 'max_y') and self.max_y != max_y:
            self.max_y = max_y
            self.load_network() # Reload to update positions
        
        self.setSceneRect(min_x, 0, width, height)

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
        
        if not network.nodes:
            return
        
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
        # EPANET coordinates: Y increases upwards
        # Qt coordinates: Y increases downwards
        # We need to map UL (x1, y1) and LR (x2, y2) from EPANET to Qt scene
        
        # Calculate width and height in world coordinates
        world_w = abs(lr_x - ul_x)
        world_h = abs(ul_y - lr_y) # y1 is top (max y), y2 is bottom (min y)
        
        if world_w == 0 or world_h == 0:
            return
            
        # Calculate scale factors
        img_w = pixmap.width()
        img_h = pixmap.height()
        
        scale_x = world_w / img_w
        scale_y = world_h / img_h
        
        # Apply transformation
        self.backdrop_item.resetTransform()
        
        # Position:
        # In our scene, we flip Y. So max_y (ul_y) corresponds to smaller scene Y (top).
        # Actually, our scene uses (x, max_y - y).
        # Let's assume the scene's coordinate system is already set up such that
        # we just need to place the image at the correct location.
        
        # Wait, the NodeItems are placed at (x, max_y - y).
        # So the scene origin (0,0) is at (0, max_y).
        # We need to find where (ul_x, ul_y) maps to.
        # scene_x = ul_x
        # scene_y = self.max_y - ul_y
        
        # We need self.max_y which is calculated in load_network.
        # But load_network might not have run or max_y might be different.
        # Let's use the max_y from the current network bounds if available.
        
        # For simplicity, let's assume the backdrop coordinates define the rect.
        # We place the pixmap at (ul_x, self.max_y - ul_y) and scale it.
        # But wait, the image needs to be flipped vertically? 
        # No, QGraphicsPixmapItem draws image normally (top-down).
        # Our scene is normal (top-down), but we position nodes by flipping their Y.
        # So the "World Top" (max Y) is at Scene Y = 0 (or small).
        # The "World Bottom" (min Y) is at Scene Y = large.
        
        # So UL corner of image (World x1, y1) should be at Scene (x1, max_y - y1).
        # LR corner of image (World x2, y2) should be at Scene (x2, max_y - y2).
        
        # However, we need to know 'max_y' of the coordinate system to do the flip.
        # The NodeItems use 'self.max_y' which is the max Y of the NETWORK nodes.
        # The backdrop might extend beyond the network.
        # This implies we should use a consistent reference.
        # If we use the same 'max_y' as the nodes, then:
        # Image Top (y1) -> Scene Y = self.max_y - y1
        # Image Bottom (y2) -> Scene Y = self.max_y - y2
        # Height in Scene = (self.max_y - y2) - (self.max_y - y1) = y1 - y2 = world_h
        # This matches!
        
        scene_x = ul_x
        scene_y = self.max_y - ul_y
        
        self.backdrop_item.setPos(scene_x, scene_y)
        
        # Now scale. 
        # We want the image width (img_w) to cover world_w.
        # We want the image height (img_h) to cover world_h.
        self.backdrop_item.setScale(scale_x) 
        # Note: We might need independent x/y scaling if aspect ratio differs
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
        print(f"DEBUG: NetworkScene.apply_map_options called. Options: {options}")
        if not options:
            print("DEBUG: Options empty")
            return
        
        # Apply node options
        node_size = options.get('node_size', 3)
        display_node_border = options.get('display_node_border', True)
        display_node_ids = options.get('display_node_ids', False)
        display_node_values = options.get('display_node_values', False)
        notation_font_size = options.get('notation_font_size', 8)
        
        print(f"DEBUG: Applying node_size={node_size}, display_node_border={display_node_border}")
        print(f"DEBUG: display_node_ids={display_node_ids}, display_node_values={display_node_values}")
        print(f"DEBUG: Node items count: {len(self.node_items)}")
        
        for node_id, item in self.node_items.items():
            # Update node size (scale the radius)
            # Base radius is 1.0 * item.scale (from __init__)
            # Default node_size is 3
            if hasattr(item, 'scale'):
                base_radius = 1.0 * item.scale
                scaled_radius = base_radius * (node_size / 3.0)
                item.setRect(-scaled_radius, -scaled_radius, scaled_radius*2, scaled_radius*2)
                item.radius = scaled_radius # Update radius property for label positioning
            
            # Update border visibility
            if display_node_border:
                pen = item.pen()
                # Border width proportional to size
                if hasattr(item, 'scale'):
                    pen.setWidthF(0.05 * item.scale * (node_size / 3.0))
                else:
                    pen.setWidthF(0.05)
                item.setPen(pen)
            else:
                item.setPen(QPen(Qt.NoPen))
                
            # Update ID label
            if hasattr(item, 'id_label'):
                item.id_label.setVisible(display_node_ids)
                if display_node_ids:
                    print(f"DEBUG: Setting node {node_id} ID label visible. Pos: {item.id_label.pos()}")
                
                # Scale font size based on item scale
                # Use a high-res base font and scale the item
                base_font_size = 48
                font = item.id_label.font()
                font.setPixelSize(base_font_size) # Use pixel size for consistent base
                item.id_label.setFont(font)
                
                if hasattr(item, 'scale'):
                    # Target height = item.scale * (notation_font_size / 4.0)
                    # Scale factor = target_height / base_font_size
                    # notation_font_size 8 -> factor 2.0 relative to scale
                    target_height = item.scale * (notation_font_size / 4.0)
                    # Ensure minimum visibility? No, let it scale.
                    scale_factor = target_height / base_font_size
                    item.id_label.setScale(scale_factor)
                else:
                    item.id_label.setScale(1.0)
            
            # Update Value label
            if hasattr(item, 'value_label'):
                item.value_label.setVisible(display_node_values)
                # TODO: Set actual value text based on current time step
                item.value_label.setText("0.00") 
                
                base_font_size = 48
                font = item.value_label.font()
                font.setPixelSize(base_font_size)
                item.value_label.setFont(font)
                
                if hasattr(item, 'scale'):
                    target_height = item.scale * (notation_font_size / 4.0)
                    scale_factor = target_height / base_font_size
                    item.value_label.setScale(scale_factor)
                else:
                    item.value_label.setScale(1.0)
                
            # Update label positions
            if hasattr(item, 'update_label_positions'):
                item.update_label_positions()
        
        # Apply link options
        link_size = options.get('link_size', 2)
        display_link_border = options.get('display_link_border', False)
        display_link_ids = options.get('display_link_ids', False)
        display_link_values = options.get('display_link_values', False)
        
        print(f"DEBUG: display_link_ids={display_link_ids}, display_link_values={display_link_values}")
        
        for link_id, item in self.link_items.items():
            # Update link width
            pen = item.pen()
            # Base width is 0.5 * item.scale (from __init__)
            # Default link_size is 2
            if hasattr(item, 'scale'):
                # 0.5 * scale is default for size 2
                # So factor is link_size / 2.0
                width = (0.5 * item.scale) * (link_size / 2.0)
                pen.setWidthF(width)
            else:
                pen.setWidthF(0.1 * link_size / 2.0)
            item.setPen(pen)
            
            # Update ID label
            if hasattr(item, 'id_label'):
                item.id_label.setVisible(display_link_ids)
                if display_link_ids:
                    print(f"DEBUG: Setting link {link_id} ID label visible")
                
                base_font_size = 48
                font = item.id_label.font()
                font.setPixelSize(base_font_size)
                item.id_label.setFont(font)
                
                if hasattr(item, 'scale'):
                    target_height = item.scale * (notation_font_size / 4.0)
                    scale_factor = target_height / base_font_size
                    item.id_label.setScale(scale_factor)
                else:
                    item.id_label.setScale(1.0)
                
            # Update Value label
            if hasattr(item, 'value_label'):
                item.value_label.setVisible(display_link_values)
                # TODO: Set actual value text based on current time step
                item.value_label.setText("0.00")
                
                base_font_size = 48
                font = item.value_label.font()
                font.setPixelSize(base_font_size)
                item.value_label.setFont(font)
                
                if hasattr(item, 'scale'):
                    target_height = item.scale * (notation_font_size / 4.0)
                    scale_factor = target_height / base_font_size
                    item.value_label.setScale(scale_factor)
                else:
                    item.value_label.setScale(1.0)
                
            # Update label positions
                
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


