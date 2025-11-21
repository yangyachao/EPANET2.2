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

    def fit_network(self):
        """Fit the view to the network extent."""
        rect = self.scene.itemsBoundingRect()
        if not rect.isNull():
            self.fitInView(rect, Qt.KeepAspectRatio)
            # Zoom out a bit
            self.scale(0.9, 0.9)

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
