"""Graphics items for EPANET network components."""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter

class NodeItem(QGraphicsEllipseItem):
    """Base class for node graphics items."""
    
    def __init__(self, node, radius=60):
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.node = node
        self.radius = radius
        self.normal_color = Qt.white
        self.normal_pen = QPen(Qt.black, 8)
        self.setPos(node.x, node.y)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Default style with thicker border
        self.setPen(self.normal_pen)
        self.setBrush(QBrush(self.normal_color))
        self.setToolTip(f"{node.id}\nElevation: {node.elevation}")
        
        # Add shadow effect for selected state
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(25)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(255, 0, 0, 200))

    def hoverEnterEvent(self, event):
        """Change cursor to pointing hand when hovering."""
        self.setCursor(Qt.PointingHandCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Restore default cursor when leaving."""
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Update node model coordinates
            self.node.x = value.x()
            self.node.y = value.y()
            # Notify connected links to update
            if hasattr(self.scene(), "update_connected_links"):
                self.scene().update_connected_links(self.node.id)
        elif change == QGraphicsItem.ItemSelectedChange:
            # Highlight when selected - brighter, thicker border, shadow
            if value:
                # Bright yellow/orange fill for selected
                self.setBrush(QBrush(QColor(255, 255, 100)))
                # Much thicker and red border
                self.setPen(QPen(Qt.red, 12))
                # Add glow effect
                self.setGraphicsEffect(self.shadow)
            else:
                # Return to normal
                self.setBrush(QBrush(self.normal_color))
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
        return super().itemChange(change, value)

class JunctionItem(NodeItem):
    """Graphics item for Junction."""
    
    def __init__(self, node):
        super().__init__(node, radius=60)
        self.normal_color = QColor(0, 120, 255)  # Brighter blue
        self.setBrush(QBrush(self.normal_color))

class ReservoirItem(NodeItem):
    """Graphics item for Reservoir."""
    
    def __init__(self, node):
        super().__init__(node, radius=100)
        self.normal_color = QColor(0, 200, 0)  # Green
        self.setBrush(QBrush(self.normal_color))
        self.setRect(-100, -100, 200, 200)

class TankItem(NodeItem):
    """Graphics item for Tank."""
    
    def __init__(self, node):
        super().__init__(node, radius=90)
        self.normal_color = QColor(255, 200, 0)  # Brighter yellow
        self.setBrush(QBrush(self.normal_color))
        self.setRect(-90, -90, 180, 180)

class LinkItem(QGraphicsPathItem):
    """Base class for link graphics items."""
    
    def __init__(self, link, from_pos, to_pos):
        super().__init__()
        self.link = link
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.normal_pen = QPen(Qt.gray, 30)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self.update_path()
        
        # Default style - much thicker lines (5x)
        self.setPen(self.normal_pen)
        self.setToolTip(f"{link.id}\nType: {link.link_type.name}")
        
        # Add shadow effect for selected state
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(255, 0, 0, 220))

    def hoverEnterEvent(self, event):
        """Change cursor to pointing hand when hovering."""
        self.setCursor(Qt.PointingHandCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Restore default cursor when leaving."""
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        """Handle selection highlight."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                # Much thicker and bright red when selected, plus glow
                pen = QPen(Qt.red, 50)
                self.setPen(pen)
                self.setGraphicsEffect(self.shadow)
                # Raise z-value to draw on top
                self.setZValue(10)
            else:
                # Reset to default
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
                self.setZValue(0)
        return super().itemChange(change, value)

    def update_positions(self, from_pos, to_pos):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        path.moveTo(self.from_pos)
        path.lineTo(self.to_pos)
        self.setPath(path)

class PipeItem(LinkItem):
    """Graphics item for Pipe."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(Qt.darkGray, 30)
        self.setPen(self.normal_pen)

class PumpItem(LinkItem):
    """Graphics item for Pump."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(QColor(255, 140, 0), 40)  # Darker orange
        self.setPen(self.normal_pen)

class ValveItem(LinkItem):
    """Graphics item for Valve."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(QColor(220, 20, 60), 30)  # Crimson red
        self.setPen(self.normal_pen)
