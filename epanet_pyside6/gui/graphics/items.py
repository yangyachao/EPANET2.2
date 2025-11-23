"""Graphics items for EPANET network components."""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter, QFont

class NodeItem(QGraphicsEllipseItem):
    """Base class for node graphics items."""
    
    def __init__(self, node, radius=1.0, scale=1.0, max_y=0):
        # Apply scale to radius
        scaled_radius = radius * scale
        super().__init__(-scaled_radius, -scaled_radius, scaled_radius*2, scaled_radius*2)
        self.node = node
        self.radius = scaled_radius
        self.scale = scale
        self.max_y = max_y
        self.normal_color = Qt.white
        self.normal_pen = QPen(Qt.black, 0.05 * scale)
        # Flip Y coordinate: EPANET Y goes up, Qt Y goes down
        self.setPos(node.x, max_y - node.y)
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
        self.shadow.setBlurRadius(0.2 * scale)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(255, 0, 0, 200))
        
        # Text labels
        self.id_label = QGraphicsSimpleTextItem(self.node.id, self)
        self.id_label.setBrush(QBrush(Qt.black))
        self.id_label.setFont(QFont("Arial", 8))
        self.id_label.setVisible(False)
        
        self.value_label = QGraphicsSimpleTextItem("", self)
        self.value_label.setBrush(QBrush(Qt.black))
        self.value_label.setFont(QFont("Arial", 8))
        self.value_label.setVisible(False)
        
        # Position labels
        self.update_label_positions()

    def update_label_positions(self):
        """Update positions of text labels."""
        r = self.radius
        
        # ID label above node
        id_scale = self.id_label.scale()
        id_rect = self.id_label.boundingRect()
        self.id_label.setPos(
            -id_rect.width() * id_scale / 2, 
            -r - (id_rect.height() * id_scale) - (2 * self.scale)
        )
        
        # Value label below node
        val_scale = self.value_label.scale()
        val_rect = self.value_label.boundingRect()
        self.value_label.setPos(
            -val_rect.width() * val_scale / 2, 
            r + (2 * self.scale)
        )

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
            # Update node model coordinates (flip Y back to EPANET coordinate system)
            self.node.x = value.x()
            self.node.y = self.max_y - value.y()
            # Notify connected links to update
            if hasattr(self.scene(), "update_connected_links"):
                self.scene().update_connected_links(self.node.id)
        elif change == QGraphicsItem.ItemSelectedChange:
            # Highlight when selected - brighter, thicker border, shadow
            if value:
                # Bright yellow/orange fill for selected
                self.setBrush(QBrush(QColor(255, 255, 100)))
                # Much thicker and red border
                self.setPen(QPen(Qt.red, 0.08 * self.scale))
                # Add glow effect
                self.setGraphicsEffect(self.shadow)
            else:
                # Return to normal
                self.setBrush(QBrush(self.normal_color))
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
        return super().itemChange(change, value)
        
    def set_color(self, color):
        """Set the node color."""
        if color:
            self.setBrush(QBrush(color))
        else:
            self.setBrush(QBrush(self.normal_color))

class JunctionItem(NodeItem):
    """Graphics item for Junction."""
    
    def __init__(self, node, scale=1.0, max_y=0):
        super().__init__(node, radius=1.0, scale=scale, max_y=max_y)
        self.normal_color = QColor(0, 120, 255)  # Brighter blue
        self.setBrush(QBrush(self.normal_color))

class ReservoirItem(NodeItem):
    """Graphics item for Reservoir."""
    
    def __init__(self, node, scale=1.0, max_y=0):
        super().__init__(node, radius=1.5, scale=scale, max_y=max_y)
        self.normal_color = QColor(0, 200, 0)  # Green
        self.setBrush(QBrush(self.normal_color))
        r = 1.5 * scale
        self.setRect(-r, -r, r*2, r*2)

class TankItem(NodeItem):
    """Graphics item for Tank."""
    
    def __init__(self, node, scale=1.0, max_y=0):
        super().__init__(node, radius=1.2, scale=scale, max_y=max_y)
        self.normal_color = QColor(255, 200, 0)  # Brighter yellow
        self.setBrush(QBrush(self.normal_color))
        r = 1.2 * scale
        self.setRect(-r, -r, r*2, r*2)

class LinkItem(QGraphicsPathItem):
    """Base class for link graphics items."""
    
    def __init__(self, link, from_pos, to_pos, scale=1.0):
        super().__init__()
        self.link = link
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.scale = scale
        self.normal_pen = QPen(Qt.gray, 0.5 * scale)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Text labels
        self.id_label = QGraphicsSimpleTextItem(self.link.id, self)
        self.id_label.setBrush(QBrush(Qt.black))
        self.id_label.setFont(QFont("Arial", 8))
        self.id_label.setVisible(False)
        
        self.value_label = QGraphicsSimpleTextItem("", self)
        self.value_label.setBrush(QBrush(Qt.black))
        self.value_label.setFont(QFont("Arial", 8))
        self.value_label.setVisible(False)
        
        self.update_path()
        
        # Default style - much thicker lines (5x)
        self.setPen(self.normal_pen)
        self.setToolTip(f"{link.id}\nType: {link.link_type.name}")
        
        # Add shadow effect for selected state
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0.2 * scale)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(255, 0, 0, 220))
        
        # Position labels
        self.update_label_positions()

    def update_label_positions(self):
        """Update positions of text labels."""
        # Position at midpoint of the link
        path = self.path()
        if path.elementCount() > 0:
            mid_point = path.pointAtPercent(0.5)
            # Convert scene point to local coordinates if needed, but since LinkItem is a PathItem, 
            # its local coordinates match the path definition.
            # However, QGraphicsPathItem's origin is (0,0) usually.
            # Let's just use the midpoint of the bounding rect for simplicity or calculate from path.
            
            # Actually, for QGraphicsPathItem, the path is in local coordinates.
            
            # ID label slightly above midpoint
            id_scale = self.id_label.scale()
            id_rect = self.id_label.boundingRect()
            self.id_label.setPos(
                mid_point.x() - (id_rect.width() * id_scale / 2), 
                mid_point.y() - (id_rect.height() * id_scale) - (5 * self.scale)
            )
            
            # Value label slightly below midpoint
            val_scale = self.value_label.scale()
            val_rect = self.value_label.boundingRect()
            self.value_label.setPos(
                mid_point.x() - (val_rect.width() * val_scale / 2), 
                mid_point.y() + (5 * self.scale)
            )

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
                pen = QPen(Qt.red, 0.8 * self.scale)
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
        
    def set_color(self, color):
        """Set the link color."""
        if color:
            pen = QPen(color, 0.5 * self.scale)
            self.setPen(pen)
        else:
            self.setPen(self.normal_pen)

    def update_positions(self, from_pos, to_pos):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        path.moveTo(self.from_pos)
        path.lineTo(self.to_pos)
        self.setPath(path)
        self.update_label_positions()

class PipeItem(LinkItem):
    """Graphics item for Pipe."""
    def __init__(self, link, from_pos, to_pos, scale=1.0):
        super().__init__(link, from_pos, to_pos, scale=scale)
        self.normal_pen = QPen(Qt.darkGray, 0.5 * scale)
        self.setPen(self.normal_pen)

class PumpItem(LinkItem):
    """Graphics item for Pump."""
    def __init__(self, link, from_pos, to_pos, scale=1.0):
        super().__init__(link, from_pos, to_pos, scale=scale)
        self.normal_pen = QPen(QColor(255, 140, 0), 0.6 * scale)  # Darker orange
        self.setPen(self.normal_pen)

class ValveItem(LinkItem):
    """Graphics item for Valve."""
    def __init__(self, link, from_pos, to_pos, scale=1.0):
        super().__init__(link, from_pos, to_pos, scale=scale)
        self.normal_pen = QPen(QColor(220, 20, 60), 0.5 * scale)  # Crimson red
        self.setPen(self.normal_pen)
