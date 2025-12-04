"""Map widget for displaying and editing the network."""

from enum import Enum, auto
from PySide6.QtWidgets import QGraphicsView, QMenu, QGraphicsLineItem, QGraphicsPathItem, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from gui.graphics.scene import NetworkScene
from gui.graphics.items import NodeItem
from .legend_widget import LegendWidget

class InteractionMode(Enum):
    SELECT = auto()
    PAN = auto()
    ADD_JUNCTION = auto()
    ADD_RESERVOIR = auto()
    ADD_TANK = auto()
    ADD_PIPE = auto()
    ADD_PUMP = auto()
    ADD_VALVE = auto()
    ADD_LABEL = auto()

class MapWidget(QGraphicsView):
    """Interactive map widget."""
    
    options_requested = Signal() # Forward signal from legend
    mouseMoved = Signal(float, float) # Emits x, y coordinates
    network_changed = Signal() # Emitted when network structure changes
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.scene = NetworkScene(project, self)
        self.setScene(self.scene)
        
        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        
        # Legends
        self.node_legend = LegendWidget("Node Legend", self)
        self.node_legend.hide()
        self.node_legend.options_requested.connect(self.options_requested.emit)
        
        self.link_legend = LegendWidget("Link Legend", self)
        self.link_legend.hide()
        self.link_legend.options_requested.connect(self.options_requested.emit)
        
        # Link drawing state
        self.drawing_link_start_node = None
        self.drawing_link_start_node = None
        self.temp_link_path = None
        self.current_link_vertices = []
        
        # Initial fit state
        self._first_resize = True
        
        self.interaction_mode = InteractionMode.SELECT
        
        # Ghost item for preview
        self.ghost_item = None
        
    def set_interaction_mode(self, mode: InteractionMode):
        """Set interaction mode (select, pan, add_junction, etc.)."""
        self.interaction_mode = mode
        print(f"DEBUG: MapWidget.set_interaction_mode called with {mode}")
        
        if mode == InteractionMode.PAN:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
        elif mode == InteractionMode.SELECT:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
            
        # Handle ghost item
        self._update_ghost_item()
        
    def _update_ghost_item(self):
        """Update ghost item based on interaction mode."""
        # Remove existing ghost
        if self.ghost_item:
            self.scene.removeItem(self.ghost_item)
            self.ghost_item = None
            
        # Create new ghost if in add node mode
        if self.interaction_mode in [InteractionMode.ADD_JUNCTION, InteractionMode.ADD_RESERVOIR, InteractionMode.ADD_TANK]:
            from gui.graphics.items import JunctionItem, ReservoirItem, TankItem
            from models.node import Junction, Reservoir, Tank
            
            # Create dummy node for visualization
            dummy_id = "Ghost"
            
            if self.interaction_mode == InteractionMode.ADD_JUNCTION:
                node = Junction(dummy_id)
                self.ghost_item = JunctionItem(node)
            elif self.interaction_mode == InteractionMode.ADD_RESERVOIR:
                node = Reservoir(dummy_id)
                self.ghost_item = ReservoirItem(node)
            elif self.interaction_mode == InteractionMode.ADD_TANK:
                node = Tank(dummy_id)
                self.ghost_item = TankItem(node)
                
            if self.ghost_item:
                self.ghost_item.setOpacity(0.5) # Semi-transparent
                self.ghost_item.setZValue(100) # On top
                self.scene.addItem(self.ghost_item)
                # Position at mouse cursor (will be updated in mouseMove)
                # We need last mouse pos? Or just wait for move.
                # Ideally, set at current mouse pos if available.
                pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
                self.ghost_item.setPos(pos.x(), pos.y())
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.interaction_mode != InteractionMode.SELECT and self.interaction_mode != InteractionMode.PAN:
            pos = self.mapToScene(event.pos())
            
            # Check if adding link
            if self.interaction_mode in [InteractionMode.ADD_PIPE, InteractionMode.ADD_PUMP, InteractionMode.ADD_VALVE]:
                # Find nearest node within snap distance
                node_item = self.find_nearest_node(pos)
                
                if node_item:
                    if not self.drawing_link_start_node:
                        # Start drawing link
                        self.drawing_link_start_node = node_item
                        self.current_link_vertices = []
                        
                        self.temp_link_path = QGraphicsPathItem()
                        pen = QPen(QColor(0, 120, 255), 2, Qt.SolidLine)
                        pen.setCosmetic(True)
                        self.temp_link_path.setPen(pen)
                        self.scene.addItem(self.temp_link_path)
                        
                        # Initial path
                        path = QPainterPath()
                        path.moveTo(node_item.pos())
                        path.lineTo(pos)
                        self.temp_link_path.setPath(path)
                        
                    else:
                        # Finish drawing link
                        if node_item != self.drawing_link_start_node:
                            link_type = 'Pipe'
                            if self.interaction_mode == InteractionMode.ADD_PUMP: link_type = 'Pump'
                            elif self.interaction_mode == InteractionMode.ADD_VALVE: link_type = 'Valve'
                            
                            # Convert vertices to logical coordinates
                            logical_vertices = []
                            for vx, vy in self.current_link_vertices:
                                logical_vertices.append((vx, -vy))
                            
                            link_id = self.project.add_link(link_type, self.drawing_link_start_node.node.id, node_item.node.id, vertices=logical_vertices)
                            self.scene.add_link(link_id)
                            
                            # Reset state
                            self.scene.removeItem(self.temp_link_path)
                            self.temp_link_path = None
                            self.drawing_link_start_node = None
                            self.current_link_vertices = []
                            
                            # Clear highlight
                            if hasattr(self, 'last_highlighted_node') and self.last_highlighted_node:
                                self.last_highlighted_node.set_highlight(False)
                                self.last_highlighted_node = None
                            
                            # Refresh scene
                            self.scene.update_scene_rect()
                            self.network_changed.emit()
                else:
                    # Clicked on empty space while drawing -> Add Vertex
                    if self.drawing_link_start_node:
                        # Add vertex point (scene coordinates)
                        self.current_link_vertices.append((pos.x(), pos.y()))
                        
                        # Update path visualization
                        path = QPainterPath()
                        path.moveTo(self.drawing_link_start_node.pos())
                        for vx, vy in self.current_link_vertices:
                            path.lineTo(vx, vy)
                        path.lineTo(pos) # Current mouse pos
                        self.temp_link_path.setPath(path)
                
                return

            # Adding Node
            node_id = None
            # Convert visual Y (Qt) to logical Y (EPANET)
            # Qt Y = -EPANET Y  =>  EPANET Y = -Qt Y
            logical_y = -pos.y()
            
            if self.interaction_mode == InteractionMode.ADD_JUNCTION:
                node_id = self.project.add_node('Junction', pos.x(), logical_y)
            elif self.interaction_mode == InteractionMode.ADD_RESERVOIR:
                node_id = self.project.add_node('Reservoir', pos.x(), logical_y)
            elif self.interaction_mode == InteractionMode.ADD_TANK:
                node_id = self.project.add_node('Tank', pos.x(), logical_y)
            
            if node_id:
                self.scene.add_node(node_id)
                self.network_changed.emit()
            
            # Adding Label
            if self.interaction_mode == InteractionMode.ADD_LABEL:
                text, ok = QInputDialog.getText(self, "Add Label", "Label Text:")
                if ok and text:
                    # Convert to logical Y
                    logical_y = -pos.y()
                    label_id = self.project.add_label(text, pos.x(), logical_y)
                    self.scene.add_label(label_id)
                    self.network_changed.emit()
            
            # Refresh scene
            self.scene.update_scene_rect()
            return

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)
            
    def delete_selected_items(self):
        """Delete selected items."""
        from PySide6.QtWidgets import QMessageBox
        
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(self, "Delete Objects", 
                                   f"Delete {len(selected_items)} selected object(s)?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            for item in selected_items:
                if hasattr(item, 'node'):
                    try:
                        self.project.delete_node(item.node.id)
                        self.scene.removeItem(item)
                        # Also remove connected links from scene?
                        # Scene update might be needed or manual removal
                        # For now, let's just refresh scene completely or handle individually
                    except Exception as e:
                        print(f"Error deleting node: {e}")
                elif hasattr(item, 'link'):
                    try:
                        self.project.delete_link(item.link.id)
                        self.scene.removeItem(item)
                    except Exception as e:
                        print(f"Error deleting link: {e}")
                elif hasattr(item, 'label'):
                    try:
                        self.project.delete_label(item.label.id)
                        self.scene.removeItem(item)
                    except Exception as e:
                        print(f"Error deleting label: {e}")
            
            # Refresh scene to clean up any artifacts
            self.scene.update()
            self.network_changed.emit()

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        
        # Emit logical coordinates (Y is flipped)
        self.mouseMoved.emit(pos.x(), -pos.y())
        
        # Update ghost position
        if self.ghost_item:
            self.ghost_item.setPos(pos)
        
        # Snapping logic for link drawing
        if self.interaction_mode in [InteractionMode.ADD_PIPE, InteractionMode.ADD_PUMP, InteractionMode.ADD_VALVE]:
            nearest_node = self.find_nearest_node(pos)
            
            # Update cursor and highlight
            if nearest_node:
                self.setCursor(Qt.CrossCursor)
                if hasattr(self, 'last_highlighted_node') and self.last_highlighted_node != nearest_node:
                    if self.last_highlighted_node:
                        self.last_highlighted_node.set_highlight(False)
                
                nearest_node.set_highlight(True)
                self.last_highlighted_node = nearest_node
            else:
                self.setCursor(Qt.ArrowCursor)
                if hasattr(self, 'last_highlighted_node') and self.last_highlighted_node:
                    self.last_highlighted_node.set_highlight(False)
                    self.last_highlighted_node = None
                
            if self.temp_link_path:
                path = QPainterPath()
                path.moveTo(self.drawing_link_start_node.pos())
                
                for vx, vy in self.current_link_vertices:
                    path.lineTo(vx, vy)
                
                if nearest_node:
                    # Snap to node center
                    path.lineTo(nearest_node.pos())
                else:
                    # Follow mouse
                    path.lineTo(pos)
                    
                self.temp_link_path.setPath(path)
            
        # Tooltip logic
        item = self.scene.itemAt(pos, self.transform())
        if item:
            tooltip_text = ""
            if hasattr(item, 'node'):
                tooltip_text = f"Node {item.node.id}"
                # Add value if parameter selected
                if hasattr(self.scene, 'current_node_param') and self.scene.current_node_param:
                    val = self.project.engine.get_node_result(item.node.id, self.scene.current_node_param)
                    tooltip_text += f"\n{self.scene.current_node_param.name}: {val:.2f}"
            elif hasattr(item, 'link'):
                tooltip_text = f"Link {item.link.id}"
                if hasattr(self.scene, 'current_link_param') and self.scene.current_link_param:
                    val = self.project.engine.get_link_result(item.link.id, self.scene.current_link_param)
                    tooltip_text += f"\n{self.scene.current_link_param.name}: {val:.2f}"
            
            if tooltip_text:
                self.setToolTip(tooltip_text)
            else:
                self.setToolTip("")
        else:
            self.setToolTip("")

        super().mouseMoveEvent(event)

    def find_nearest_node(self, pos, threshold=15):
        """Find the nearest node within threshold distance."""
        nearest_item = None
        min_dist = float('inf')
        
        # Check all node items
        # Optimization: Use scene.items(rect) for spatial query if performance is an issue
        # For now, iterating is fine for small/medium networks
        # Better: query scene for items near pos
        
        # Create a small rect around pos
        rect = QRectF(pos.x() - threshold, pos.y() - threshold, threshold*2, threshold*2)
        items = self.scene.items(rect)
        
        for item in items:
            if isinstance(item, NodeItem):
                # Calculate distance
                dist = (item.pos() - pos).manhattanLength() # Approximation is fine
                if dist < min_dist:
                    min_dist = dist
                    nearest_item = item
                    
        return nearest_item

    def fit_network(self):
        """Fit the view to the network extent."""
        # Calculate bounds from node positions
        if not self.scene.node_items:
            # Fallback to scene rect (which is now initialized to 10000x10000)
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            return
            
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        has_nodes = False
        
        for item in self.scene.node_items.values():
            if item.isVisible():
                pos = item.pos()
                min_x = min(min_x, pos.x())
                min_y = min(min_y, pos.y())
                max_x = max(max_x, pos.x())
                max_y = max(max_y, pos.y())
                has_nodes = True
        
        if has_nodes:
            rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
            
            # Add 5% margin on all sides
            # Ensure rect has some size
            if rect.width() == 0:
                rect.adjust(-10, 0, 10, 0)
            if rect.height() == 0:
                rect.adjust(0, -10, 0, 10)
                
            margin = max(rect.width(), rect.height()) * 0.05
            if margin == 0: margin = 10
            
            rect.adjust(-margin, -margin, margin, margin)
            self.fitInView(rect, Qt.KeepAspectRatio)
        elif not self.scene.itemsBoundingRect().isNull():
            # Fallback
            rect = self.scene.itemsBoundingRect()
            self.fitInView(rect, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel."""
        zoom_in = event.angleDelta().y() > 0
        factor = 1.1 if zoom_in else 0.9
        self.scale(factor, factor)
        event.accept()
        
    def resizeEvent(self, event):
        """Handle resize to position legend."""
        super().resizeEvent(event)
        # Position legends
        self.node_legend.move(10, 10)
        # Position link legend below node legend (approximate height + margin)
        # Or we can let them be draggable and just set initial pos
        self.link_legend.move(10, 220)
        
        if self._first_resize:
            self._first_resize = False
            self.fit_network()
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
        # Check for item under mouse
        item = self.scene.itemAt(self.mapToScene(event.pos()), self.transform())
        
        # Object Actions
        if item and (hasattr(item, 'node') or hasattr(item, 'link') or hasattr(item, 'label') or hasattr(item, 'link_item')):
            # Select it if not already selected
            if not item.isSelected():
                self.scene.clearSelection()
                item.setSelected(True)
                
            props_action = menu.addAction("Properties")
            props_action.triggered.connect(lambda: self.selectionChanged.emit(
                item.node if hasattr(item, 'node') else 
                item.link if hasattr(item, 'link') else 
                item.label
            ))
            
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self.delete_selected_items)
            
            if hasattr(item, 'link'):
                menu.addSeparator()
                add_vertex_action = menu.addAction("Add Vertex")
                # Capture position for adding vertex
                pos = self.mapToScene(event.pos())
                add_vertex_action.triggered.connect(lambda: item.add_vertex(pos))
            
            if hasattr(item, 'link_item') and hasattr(item, 'index'):
                menu.addSeparator()
                delete_vertex_action = menu.addAction("Delete Vertex")
                delete_vertex_action.triggered.connect(lambda: item.link_item.delete_vertex(item.index))
            
            menu.addSeparator()
            
        # Map Options action
        options_action = menu.addAction("⚙️ Map Options...")
        options_action.triggered.connect(self._show_map_options)
        
        menu.addSeparator()
        
        # Zoom actions
        zoom_in_action = menu.addAction("🔍 Zoom In")
        zoom_in_action.triggered.connect(lambda: self.scale(1.2, 1.2))
        
        zoom_out_action = menu.addAction("🔍 Zoom Out")
        zoom_out_action.triggered.connect(lambda: self.scale(0.8, 0.8))
        
        fit_action = menu.addAction("📐 Fit to Window")
        fit_action.triggered.connect(self.fit_network)
        
        menu.exec_(event.globalPos())
    
    def _show_map_options(self):
        """Show map options dialog (called from context menu)."""
        # Get main window and call its show_map_options method
        main_window = self.window()
        if hasattr(main_window, 'show_map_options'):
            main_window.show_map_options()

    def zoom_to_object(self, obj_type, obj_id):
        """Zoom to and highlight a specific object."""
        item = None
        if obj_type == "Node":
            item = self.scene.node_items.get(obj_id)
        elif obj_type == "Link":
            item = self.scene.link_items.get(obj_id)
            
        if item:
            # Center view on item
            self.centerOn(item)
            
            # Select and highlight
            self.scene.clearSelection()
            item.setSelected(True)
            
            # Optional: Zoom in if too far out?
            # self.scale(1.5, 1.5) # Maybe not force zoom, just center
            
            print(f"DEBUG: Zoomed to {obj_type} {obj_id}")
