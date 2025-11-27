"""Graphics items for EPANET network components."""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter, QFont, QTransform

class NodeItem(QGraphicsEllipseItem):
    """Base class for node graphics items.
    
    Uses ItemIgnoresTransformations to maintain constant screen size.
    """
    
    def __init__(self, node, radius=3.0):
        # Radius is now in pixels, not world coordinates
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.node = node
        self.radius = radius
        self.normal_color = Qt.white
        
        # Cosmetic pen (width=0) - always 1 pixel regardless of zoom
        self.normal_pen = QPen(Qt.black, 0)
        
        # Flip Y coordinate: EPANET Y goes up, Qt Y goes down
        # Use simple negation for stability
        self.setPos(node.x, -node.y)
        
        # Critical: Ignore transformations (zoom) to keep fixed size
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Default style with cosmetic border
        self.setPen(self.normal_pen)
        self.setBrush(QBrush(self.normal_color))
        self.setToolTip(f"{node.id}\nElevation: {node.elevation}")
        
        # Add shadow effect for selected state
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(5) # Fixed pixel blur
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
        # Labels are in screen pixels relative to node center
        
        # ID Label (Top Left-ish or just Above)
        id_rect = self.id_label.boundingRect()
        offset = self.radius + 2 # Pixels
        
        # Center horizontally, place above
        self.id_label.setPos(
            -id_rect.width() / 2,
            -offset - id_rect.height()
        )
        
        # Value Label (Below)
        val_rect = self.value_label.boundingRect()
        self.value_label.setPos(
            -val_rect.width() / 2,
            offset
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
            self.node.y = -value.y()
            # Notify connected links to update
            if hasattr(self.scene(), "update_connected_links"):
                self.scene().update_connected_links(self.node.id)
        elif change == QGraphicsItem.ItemSelectedChange:
            # Highlight when selected
            if value:
                self.setBrush(QBrush(QColor(255, 255, 100)))
                # Thicker border
                pen = QPen(Qt.red, 2)
                pen.setCosmetic(True)
                self.setPen(pen)
                self.setGraphicsEffect(self.shadow)
            else:
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
    
    def __init__(self, node):
        super().__init__(node, radius=3.0)
        self.normal_color = QColor(0, 120, 255)  # Brighter blue
        self.setBrush(QBrush(self.normal_color))

class ReservoirItem(NodeItem):
    """Graphics item for Reservoir."""
    
    def __init__(self, node):
        super().__init__(node, radius=5.0)
        self.normal_color = QColor(0, 200, 0)  # Green
        self.setBrush(QBrush(self.normal_color))

class TankItem(NodeItem):
    """Graphics item for Tank."""
    
    def __init__(self, node):
        super().__init__(node, radius=4.0)
        self.normal_color = QColor(255, 200, 0)  # Brighter yellow
        self.setBrush(QBrush(self.normal_color))

class LinkItem(QGraphicsPathItem):
    """Base class for link graphics items."""
    
    def __init__(self, link, from_pos, to_pos):
        super().__init__()
        self.link = link
        self.from_pos = from_pos
        self.to_pos = to_pos
        
        # Cosmetic pen - fixed pixel width
        self.normal_pen = QPen(Qt.gray, 1, Qt.SolidLine, Qt.RoundCap)
        self.normal_pen.setCosmetic(True)
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Text labels
        self.id_label = QGraphicsSimpleTextItem(self.link.id, self)
        self.id_label.setBrush(QBrush(Qt.black))
        self.id_label.setFont(QFont("Arial", 8))
        self.id_label.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.id_label.setVisible(False)
        
        self.value_label = QGraphicsSimpleTextItem("", self)
        self.value_label.setBrush(QBrush(Qt.black))
        self.value_label.setFont(QFont("Arial", 8))
        self.value_label.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.value_label.setVisible(False)
        
        self.update_path()
        
        self.setPen(self.normal_pen)
        self.setToolTip(f"{link.id}\nType: {link.link_type.name}")
        
        self.update_label_positions()

    def update_label_positions(self):
        """Update positions of text labels."""
        # Position at midpoint of the link
        path = self.path()
        if path.elementCount() > 0:
            mid_point = path.pointAtPercent(0.5)
            
            self.id_label.setPos(mid_point)
            self.value_label.setPos(mid_point)
            
            id_rect = self.id_label.boundingRect()
            offset = 10 # Pixels
            
            # Adjust position to center text
            # Set position to the exact midpoint (Scene coordinates)
            self.id_label.setPos(mid_point)
            self.value_label.setPos(mid_point)
            
            # Use QTransform to offset in pixels (screen space)
            # This works because ItemIgnoresTransformations is set
            
            id_rect = self.id_label.boundingRect()
            offset = 10 # Pixels
            
            # Center horizontally, place above
            self.id_label.setTransform(QTransform().translate(
                -id_rect.width() / 2,
                -offset - id_rect.height()
            ))
            
            val_rect = self.value_label.boundingRect()
            # Center horizontally, place below
            self.value_label.setTransform(QTransform().translate(
                -val_rect.width() / 2,
                offset
            ))

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
                # Thicker red pen
                pen = QPen(Qt.red, 3)
                pen.setCosmetic(True)
                self.setPen(pen)
                
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(5)
                shadow.setOffset(0, 0)
                shadow.setColor(QColor(255, 0, 0, 220))
                self.setGraphicsEffect(shadow)
                
                self.setZValue(10)
            else:
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
                self.setZValue(0)
        return super().itemChange(change, value)
        
    def set_color(self, color):
        """Set the link color."""
        if color:
            pen = QPen(color, self.normal_pen.widthF())
            pen.setCosmetic(True)
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
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(Qt.darkGray, 1)
        self.normal_pen.setCosmetic(True)
        self.setPen(self.normal_pen)

class PumpItem(LinkItem):
    """Graphics item for Pump."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(QColor(255, 140, 0), 2)  # Thicker for pumps
        self.normal_pen.setCosmetic(True)
        self.setPen(self.normal_pen)

class ValveItem(LinkItem):
    """Graphics item for Valve."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(QColor(220, 20, 60), 2)  # Thicker for valves
        self.normal_pen.setCosmetic(True)
        self.setPen(self.normal_pen)

class LabelItem(QGraphicsSimpleTextItem):
    """Graphics item for Map Labels."""
    
    def __init__(self, label):
        super().__init__(label.text)
        self.label = label
        
        # Flip Y coordinate
        self.setPos(label.x, -label.y)
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        
        self.setBrush(QBrush(Qt.black))
        self.setFont(QFont("Arial", 10))
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Update label model coordinates
            self.label.x = value.x()
            self.label.y = -value.y()
        elif change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setBrush(QBrush(Qt.red))
            else:
                self.setBrush(QBrush(Qt.black))
        return super().itemChange(change, value)
