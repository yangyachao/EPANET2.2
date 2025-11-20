"""Graphics items for EPANET network components."""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter

class NodeItem(QGraphicsEllipseItem):
    """Base class for node graphics items."""
    
    def __init__(self, node, radius=3):
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.node = node
        self.setPos(node.x, node.y)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Default style
        self.setPen(QPen(Qt.black, 1))
        self.setBrush(QBrush(Qt.white))
        self.setToolTip(f"{node.id}\nElevation: {node.elevation}")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Update node model coordinates
            self.node.x = value.x()
            self.node.y = value.y()
            # Notify connected links to update
            if hasattr(self.scene(), "update_connected_links"):
                self.scene().update_connected_links(self.node.id)
        return super().itemChange(change, value)

class JunctionItem(NodeItem):
    """Graphics item for Junction."""
    
    def __init__(self, node):
        super().__init__(node, radius=3)
        self.setBrush(QBrush(QColor(0, 100, 255)))  # Blue

class ReservoirItem(NodeItem):
    """Graphics item for Reservoir."""
    
    def __init__(self, node):
        super().__init__(node, radius=6)
        self.setBrush(QBrush(QColor(0, 200, 0)))  # Green
        self.setRect(-6, -6, 12, 12)  # Square-ish for reservoir usually, but circle is fine for now

class TankItem(NodeItem):
    """Graphics item for Tank."""
    
    def __init__(self, node):
        super().__init__(node, radius=5)
        self.setBrush(QBrush(QColor(200, 200, 0)))  # Yellow
        self.setRect(-5, -5, 10, 10)

class LinkItem(QGraphicsPathItem):
    """Base class for link graphics items."""
    
    def __init__(self, link, from_pos, to_pos):
        super().__init__()
        self.link = link
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        self.update_path()
        
        # Default style
        self.setPen(QPen(Qt.gray, 2))
        self.setToolTip(f"{link.id}\nType: {link.link_type.name}")

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
        self.setPen(QPen(Qt.darkGray, 2))

class PumpItem(LinkItem):
    """Graphics item for Pump."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.setPen(QPen(QColor(255, 165, 0), 3))  # Orange

class ValveItem(LinkItem):
    """Graphics item for Valve."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.setPen(QPen(Qt.red, 2))
