"""Map widget for displaying and editing the network."""

from PySide6.QtWidgets import QGraphicsView, QMenu
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
        if not rect.isNull():
            # Add 10% margin on all sides
            margin = max(rect.width(), rect.height()) * 0.1
            rect.adjust(-margin, -margin, margin, margin)
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
