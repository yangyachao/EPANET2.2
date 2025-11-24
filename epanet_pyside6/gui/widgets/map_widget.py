"""Map widget for displaying and editing the network."""

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from gui.graphics.scene import NetworkScene
from .legend_widget import LegendWidget

class MapWidget(QGraphicsView):
    """Interactive map widget."""
    
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
        
        # Initial fit
        self.fit_network()
        
    def set_interaction_mode(self, mode: str):
        """Set interaction mode (select, pan)."""
        print(f"DEBUG: MapWidget.set_interaction_mode called with {mode}")
        if mode == 'pan':
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
        elif mode == 'select':
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.ArrowCursor)
            
    def mousePressEvent(self, event):
        print(f"DEBUG: MapWidget.mousePressEvent. DragMode: {self.dragMode()}")
        super().mousePressEvent(event)

    def fit_network(self):
        """Fit the view to the network extent."""
        rect = self.scene.itemsBoundingRect()
        print(f"DEBUG: fit_network. itemsBoundingRect: {rect}", flush=True)
        print(f"DEBUG: sceneRect: {self.scene.sceneRect()}", flush=True)
        
        if not rect.isNull():
            # Check for outliers if rect is unexpectedly large
            # Nodes are at X~104, Y~0. Rect is X~90, Y~-9.
            if rect.left() < 100 or rect.top() < -1:
                print("DEBUG: Found potential outliers. Scanning items...", flush=True)
                for item in self.scene.items():
                    br = item.sceneBoundingRect()
                    if br.left() < 100 or br.top() < -1:
                        print(f"DEBUG: Outlier Item: {item}", flush=True)
                        print(f"DEBUG:   BoundingRect: {br}", flush=True)
                        if hasattr(item, 'node'):
                            print(f"DEBUG:   Node ID: {item.node.id}, Pos: {item.pos()}", flush=True)
                        if hasattr(item, 'link'):
                            print(f"DEBUG:   Link ID: {item.link.id}", flush=True)
                            print(f"DEBUG:   From: {item.link.from_node} To: {item.link.to_node}", flush=True)
            
            self.fitInView(rect, Qt.KeepAspectRatio)
            # Zoom out a bit
            self.scale(0.9, 0.9)
            print("DEBUG: fitInView called", flush=True)
        else:
            print("DEBUG: itemsBoundingRect is null", flush=True)

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
