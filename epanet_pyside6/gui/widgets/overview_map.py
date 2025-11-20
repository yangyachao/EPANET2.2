"""Overview (mini) map widget that shows full network extent and current view."""

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QPen, QColor


class OverviewMapWidget(QGraphicsView):
    """A small read-only view of the network scene showing current viewport."""

    def __init__(self, main_map_view, parent=None):
        super().__init__(parent)
        # Share the same scene so items stay in sync
        self.setScene(main_map_view.scene)
        self.main_map_view = main_map_view

        # Make it read-only and compact
        self.setInteractive(False)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedSize(240, 240)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)

        # Periodically refresh the overlay rectangle
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(200)

    def fit_to_scene(self):
        rect = self.scene().itemsBoundingRect()
        if not rect.isNull():
            # Add small margin
            margin = 0.05
            w = rect.width() or 1.0
            h = rect.height() or 1.0
            rect = QRectF(rect.x()-w*margin, rect.y()-h*margin, w*(1+2*margin), h*(1+2*margin))
            self.fitInView(rect, Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Handle clicks on the overview map: center main map on clicked scene point."""
        try:
            # Map the click position to scene coordinates
            scene_pt = self.mapToScene(event.pos())
            # Center the main map view on this point
            if hasattr(self, 'main_map_view') and self.main_map_view is not None:
                self.main_map_view.centerOn(scene_pt)
        except Exception:
            pass
        # Accept the event so parent doesn't try to drag
        event.accept()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """Draw a rectangle showing the main map's current viewport."""
        try:
            # Ensure overview is fitted
            if self.scene() and self.scene().items():
                # If the overview hasn't been fitted yet, do it once
                # (fit_to_scene is cheap when scene is empty or unchanged)
                self.fit_to_scene()

            # Get main view viewport in scene coordinates
            viewport_rect = self.main_map_view.mapToScene(self.main_map_view.viewport().rect()).boundingRect()

            # Map scene rect to this view's viewport coordinates
            top_left = self.mapFromScene(viewport_rect.topLeft())
            bottom_right = self.mapFromScene(viewport_rect.bottomRight())

            x = top_left.x()
            y = top_left.y()
            w = bottom_right.x() - x
            h = bottom_right.y() - y

            pen = QPen(QColor(255, 0, 0, 200))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(x, y, w, h)

        except Exception:
            # Fail silently; overview should never crash main UI
            pass
