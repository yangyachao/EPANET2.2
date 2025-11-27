"""Map widget for displaying and editing the network."""

from PySide6.QtWidgets import QGraphicsView, QMenu, QGraphicsLineItem
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor
from gui.graphics.scene import NetworkScene
from gui.graphics.items import NodeItem
from .legend_widget import LegendWidget

class MapWidget(QGraphicsView):
    """Interactive map widget."""
    
    options_requested = Signal() # Forward signal from legend
    
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
        
        # Legend
        self.legend = LegendWidget("Legend", self)
        self.legend.hide()
        self.legend.options_requested.connect(self.options_requested.emit)
        
        # Link drawing state
        self.drawing_link_start_node = None
        self.temp_link_line = None
        
        # Initial fit
        self.fit_network()
        
        self.interaction_mode = 'select'
        
    def set_interaction_mode(self, mode: str):
        """Set interaction mode (select, pan, add_junction, etc.)."""
        self.interaction_mode = mode
        print(f"DEBUG: MapWidget.set_interaction_mode called with {mode}")
        
        if mode == 'pan':
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
        elif mode == 'select':
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
            
    def mousePressEvent(self, event):
        print(f"DEBUG: MapWidget.mousePressEvent. Mode: {self.interaction_mode}")
        
        if event.button() == Qt.LeftButton and self.interaction_mode.startswith('add_'):
            pos = self.mapToScene(event.pos())
            
            # Check if adding link
            if 'pipe' in self.interaction_mode or 'pump' in self.interaction_mode or 'valve' in self.interaction_mode:
                # Find node at position
                items = self.scene.items(pos)
                node_item = None
                for item in items:
                    if isinstance(item, NodeItem):
                        node_item = item
                        break
                
                if node_item:
                    if not self.drawing_link_start_node:
                        # Start drawing link
                        self.drawing_link_start_node = node_item
                        self.temp_link_line = QGraphicsLineItem(
                            node_item.pos().x(), node_item.pos().y(),
                            pos.x(), pos.y()
                        )
                        self.temp_link_line.setPen(QPen(Qt.black, 2, Qt.DashLine))
                        self.scene.addItem(self.temp_link_line)
                    else:
                        # Finish drawing link
                        if node_item != self.drawing_link_start_node:
                            link_type = 'Pipe'
                            if 'pump' in self.interaction_mode: link_type = 'Pump'
                            elif 'valve' in self.interaction_mode: link_type = 'Valve'
                            
                            link_id = self.project.add_link(link_type, self.drawing_link_start_node.node.id, node_item.node.id)
                            self.scene.add_link(link_id)
                            
                            # Reset state
                            self.scene.removeItem(self.temp_link_line)
                            self.temp_link_line = None
                            self.drawing_link_start_node = None
                            
                            # Refresh scene
                            self.scene.update_scene_rect()
                else:
                    # Clicked on empty space while drawing? Cancel? Or ignore?
                    # If start node is set, user might want to cancel by clicking empty space
                    if self.drawing_link_start_node:
                        self.scene.removeItem(self.temp_link_line)
                        self.temp_link_line = None
                        self.drawing_link_start_node = None
                
                return

            # Adding Node
            node_id = None
            
            # Convert to logical Y (EPANET coordinates)
            # Visual Y = max_y - Logical Y  =>  Logical Y = max_y - Visual Y
            logical_y = self.scene.max_y - pos.y()
            
            if self.interaction_mode == 'add_junction':
                node_id = self.project.add_node('Junction', pos.x(), logical_y)
            elif self.interaction_mode == 'add_reservoir':
                node_id = self.project.add_node('Reservoir', pos.x(), logical_y)
            elif self.interaction_mode == 'add_tank':
                node_id = self.project.add_node('Tank', pos.x(), logical_y)
            
            if node_id:
                self.scene.add_node(node_id)
            
            # Adding Label
            if self.interaction_mode == 'add_label':
                from PySide6.QtWidgets import QInputDialog
                text, ok = QInputDialog.getText(self, "Add Label", "Label Text:")
                if ok and text:
                    # Convert to logical Y
                    logical_y = self.scene.max_y - pos.y()
                    label_id = self.project.add_label(text, pos.x(), logical_y)
                    self.scene.add_label(label_id)
            
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

    def mouseMoveEvent(self, event):
        if self.temp_link_line:
            pos = self.mapToScene(event.pos())
            line = self.temp_link_line.line()
            line.setP2(pos)
            self.temp_link_line.setLine(line)
            
        super().mouseMoveEvent(event)

    def fit_network(self):
        """Fit the view to the network extent."""
        # Calculate bounds from node positions
        if not self.scene.node_items:
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
        # Position legend in top-left corner
        self.legend.move(10, 10)
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
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
