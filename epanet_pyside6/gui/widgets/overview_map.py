"""Overview Map widget for quick navigation."""

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

class OverviewMapWidget(QGraphicsView):
    """Overview map widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_map = None
        
        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.NoDrag)
        
        self.is_dragging = False
        
    def set_main_view(self, main_map):
        """Set the main map widget to track."""
        self.main_map = main_map
        self.setScene(main_map.scene)
        
        # Connect signals
        # Hook into main map's scrollbars and resize events
        self.main_map.horizontalScrollBar().valueChanged.connect(self.update_overview)
        self.main_map.verticalScrollBar().valueChanged.connect(self.update_overview)
        
        self.main_map.horizontalScrollBar().rangeChanged.connect(lambda min, max: self.update_overview())
        self.main_map.verticalScrollBar().rangeChanged.connect(lambda min, max: self.update_overview())
        
        # Initial update
        self.fit_network()
        
    def resizeEvent(self, event):
        """Handle resize to fit network."""
        super().resizeEvent(event)
        self.fit_network()
        
    def fit_network(self):
        """Fit the entire network in view."""
        if not self.scene():
            return
            
        # Get scene bounding rect or use a large fixed rect if empty
        rect = self.scene().itemsBoundingRect()
        if rect.isNull() or rect.width() == 0 or rect.height() == 0:
            rect = self.scene().sceneRect()
            
        # Add some margin
        margin = max(rect.width(), rect.height()) * 0.1
        rect.adjust(-margin, -margin, margin, margin)
        
        self.fitInView(rect, Qt.KeepAspectRatio)
        
    def update_overview(self):
        """Trigger update of the overview map."""
        self.viewport().update()
        
    def drawForeground(self, painter, rect):
        """Draw the viewport box."""
        super().drawForeground(painter, rect)
        
        if not self.main_map:
            return
            
        # Get visible rect of main map in scene coordinates
        viewport_rect = self.main_map.viewport().rect()
        scene_rect = self.main_map.mapToScene(viewport_rect).boundingRect()
        
        # Draw red box
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        painter.drawRect(scene_rect)
        
    def mousePressEvent(self, event):
        """Handle mouse press to center main map."""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.is_dragging = True
            self.center_main_map(scene_pos)
            
    def mouseMoveEvent(self, event):
        """Handle drag to pan main map."""
        if self.is_dragging:
            scene_pos = self.mapToScene(event.pos())
            self.center_main_map(scene_pos)
            
    def mouseReleaseEvent(self, event):
        """Stop dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
    def center_main_map(self, scene_pos):
        """Center the main map on the given scene position."""
        if self.main_map:
            self.main_map.centerOn(scene_pos)
            self.update_overview()

