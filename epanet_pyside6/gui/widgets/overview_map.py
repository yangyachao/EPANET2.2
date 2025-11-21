"""Overview map widget."""

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

class OverviewMapWidget(QGraphicsView):
    """Overview map widget showing the full network extent."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_view = None
        self.viewport_rect = QRectF()
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.NoDrag)
        
        # Optimization
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
    def set_main_view(self, view):
        """Set the main map view to track."""
        self.main_view = view
        # Handle case where scene is an attribute (shadowing method)
        if callable(view.scene):
            self.setScene(view.scene())
        else:
            self.setScene(view.scene)
        
        # Initial update
        self.update_extent()
        
    def update_extent(self):
        """Update the overview extent and viewport rectangle."""
        if not self.main_view or not self.scene():
            return
            
        # Fit the whole scene in this view
        # We use itemsBoundingRect to ensure we see everything
        scene_rect = self.scene().itemsBoundingRect()
        if not scene_rect.isNull():
            self.fitInView(scene_rect, Qt.KeepAspectRatio)
        
        # Calculate the visible rect of the main view in scene coordinates
        # mapToScene(viewport().rect()) gives a polygon, we take bounding rect
        self.viewport_rect = self.main_view.mapToScene(self.main_view.viewport().rect()).boundingRect()
        
        # Force redraw of foreground
        self.viewport().update()
        
    def drawForeground(self, painter, rect):
        """Draw the viewport rectangle."""
        if not self.viewport_rect.isValid():
            return
            
        painter.save()
        
        # Draw red rectangle representing main view
        pen = QPen(QColor(255, 0, 0, 200))
        pen.setWidth(2)
        # Scale pen width to remain constant size on screen? 
        # No, let's keep it simple for now. 
        # Actually, if we zoom out a lot in overview, 2 pixels might be too thin or thick relative to scene?
        # Since drawForeground is in scene coords, a fixed width pen will scale with the view.
        # To have a cosmetic pen (constant screen width), we use setCosmetic(True).
        pen.setCosmetic(True)
        
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        painter.drawRect(self.viewport_rect)
        
        painter.restore()
        
    def mousePressEvent(self, event):
        """Handle mouse press to center main view."""
        if event.button() == Qt.LeftButton:
            self._move_main_view(event.pos())
            
    def mouseMoveEvent(self, event):
        """Handle mouse drag to move main view."""
        if event.buttons() & Qt.LeftButton:
            self._move_main_view(event.pos())
            
    def _move_main_view(self, pos):
        """Move main view to center on the given position."""
        if not self.main_view:
            return
        
        # Map pos to scene coords
        scene_pos = self.mapToScene(pos)
        self.main_view.centerOn(scene_pos)
        
        # Update our rect immediately (though main view signals should also trigger it)
        self.update_extent()
