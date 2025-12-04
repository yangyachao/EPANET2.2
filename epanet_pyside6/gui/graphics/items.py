"""Graphics items for EPANET network components."""

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsSimpleTextItem, QGraphicsRectItem, QMenu
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter, QFont, QTransform, QPolygonF

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
        # self.shadow = QGraphicsDropShadowEffect()
        # self.shadow.setBlurRadius(5) # Fixed pixel blur
        # self.shadow.setOffset(0, 0)
        # self.shadow.setColor(QColor(255, 0, 0, 200))
        
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
                # self.setGraphicsEffect(self.shadow)
            else:
                self.setBrush(QBrush(self.normal_color))
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
        return super().itemChange(change, value)
        
    def set_highlight(self, active):
        """Set snap highlight state."""
        if active:
            # Cyan glow for snap
            self.setBrush(QBrush(QColor(0, 255, 255)))
            # Thicker cyan border
            pen = QPen(QColor(0, 255, 255), 2)
            pen.setCosmetic(True)
            self.setPen(pen)
            
            # Add glow effect
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(10)
            effect.setColor(QColor(0, 255, 255))
            effect.setOffset(0, 0)
            # self.setGraphicsEffect(effect)
        else:
            # Restore state based on selection
            if self.isSelected():
                self.itemChange(QGraphicsItem.ItemSelectedChange, True)
            else:
                self.setBrush(QBrush(self.normal_color))
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)

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
        super().__init__(node, radius=6.0)
        self.normal_color = QColor(0, 200, 0)  # Green
        self.setBrush(QBrush(self.normal_color))

    def paint(self, painter, option, widget):
        """Draw square for reservoir."""
        r = self.radius
        rect = QRectF(-r, -r, r*2, r*2)
        
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(rect)
        
    def shape(self):
        path = QPainterPath()
        r = self.radius
        path.addRect(-r, -r, r*2, r*2)
        return path

class TankItem(NodeItem):
    """Graphics item for Tank."""
    
    def __init__(self, node):
        super().__init__(node, radius=5.0)
        self.normal_color = QColor(255, 200, 0)  # Brighter yellow
        self.setBrush(QBrush(self.normal_color))

    def paint(self, painter, option, widget):
        """Draw symbol for tank."""
        r = self.radius
        # Draw a "U" shape or just a rectangle/cylinder
        rect = QRectF(-r, -r*1.2, r*2, r*2.4)
        
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(rect)
        
        # Draw top line to make it look like a tank?
        # painter.drawLine(-r, -r*1.2, r, -r*1.2)
        
    def shape(self):
        path = QPainterPath()
        r = self.radius
        path.addRect(-r, -r*1.2, r*2, r*2.4)
        return path

class VertexHandleItem(QGraphicsRectItem):
    """Handle for editing link vertices."""
    
    def __init__(self, link_item, index, x, y):
        size = 6
        # Pass link_item as parent
        super().__init__(-size/2, -size/2, size, size, link_item)
        self.link_item = link_item
        self.index = index
        
        self.setPos(x, y)
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        # self.setFlag(QGraphicsItem.ItemIsSelectable) # Don't select handle, keep link selected
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black, 1))
        self.setCursor(Qt.SizeAllCursor)
        self.setZValue(20) # Above links
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Update vertex in link model
            # Value is the new position (scene coordinates)
            self.link_item.update_vertex(self.index, value)
            
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        """Show context menu to delete vertex."""
        menu = QMenu()
        delete_action = menu.addAction("Delete Vertex")
        action = menu.exec_(event.screenPos())
        
        if action == delete_action:
            self.link_item.delete_vertex(self.index)

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
        
        self.update_path()
        
        self.setPen(self.normal_pen)
        self.setToolTip(f"{link.id}\nType: {link.link_type.name}")
        
        self.handles = []
        self.update_label_positions()

    def show_handles(self):
        """Show vertex editing handles."""
        self.hide_handles()
        
        if hasattr(self.link, 'vertices') and self.link.vertices:
            for i, (vx, vy) in enumerate(self.link.vertices):
                # Logical to Scene
                handle = VertexHandleItem(self, i, vx, -vy)
                # handle is now a child, no need to add to scene explicitly
                self.handles.append(handle)
                
    def hide_handles(self):
        """Hide vertex editing handles."""
        if self.handles:
            scene = self.scene()
            if scene:
                for handle in self.handles:
                    scene.removeItem(handle)
            self.handles = []

    def update_vertex(self, index, pos):
        """Update vertex position from handle."""
        if hasattr(self.link, 'vertices') and 0 <= index < len(self.link.vertices):
            # Scene to Logical
            self.link.vertices[index] = (pos.x(), -pos.y())
            self.update_path()
            
    def delete_vertex(self, index):
        """Delete a vertex."""
        if hasattr(self.link, 'vertices') and 0 <= index < len(self.link.vertices):
            self.link.vertices.pop(index)
            self.update_path()
            # Re-create handles to update indices
            if self.isSelected():
                self.show_handles()
                
    def add_vertex(self, pos):
        """Add a vertex at the given position (scene coords)."""
        if not hasattr(self.link, 'vertices') or self.link.vertices is None:
            self.link.vertices = []
            
        # Find best insertion index based on distance to segments
        # Simple approach: find nearest segment
        best_index = len(self.link.vertices)
        min_dist = float('inf')
        
        # Construct full point list: Start -> V1 -> V2 -> ... -> End
        points = [self.from_pos]
        for vx, vy in self.link.vertices:
            points.append(QPointF(vx, -vy))
        points.append(self.to_pos)
        
        # Check each segment
        from PySide6.QtCore import QLineF
        for i in range(len(points) - 1):
            line = QLineF(points[i], points[i+1])
            # Distance from point to line segment
            # Project point onto line
            # This is a bit complex to do perfectly, but we can just insert based on projection
            pass 
            
        # Simplified: Just append for now, or use a spatial check?
        # Better: We need to insert it where the user clicked.
        # Let's iterate segments and find which one is closest to the click
        
        insert_idx = -1
        min_dist = float('inf')
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            line = QLineF(p1, p2)
            
            # Distance from pos to segment
            # Using simple perpendicular distance if projection falls on segment
            # Or distance to endpoints
            
            # Helper to get dist to segment
            # ...
            # For now, let's assume the user clicked ON the line, so we just check which segment is closest
            
            # Simple check: if point is roughly on the segment
            # We can check distance to p1 + distance to p2 vs length of p1-p2
            d1 = QLineF(p1, pos).length()
            d2 = QLineF(pos, p2).length()
            len_seg = line.length()
            
            # If d1 + d2 is close to len_seg, then pos is on segment
            diff = (d1 + d2) - len_seg
            if diff < min_dist:
                min_dist = diff
                insert_idx = i
        
        if insert_idx != -1:
            # insert_idx corresponds to the segment index.
            # Segment 0 is Start -> V0. Insert at 0.
            # Segment 1 is V0 -> V1. Insert at 1.
            # Segment N is VN -> End. Insert at N.
            
            self.link.vertices.insert(insert_idx, (pos.x(), -pos.y()))
            self.update_path()
            if self.isSelected():
                self.show_handles()

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
                # self.setGraphicsEffect(shadow)
                
                self.setZValue(10)
                self.setZValue(10)
                self.show_handles()
            else:
                self.setPen(self.normal_pen)
                self.setGraphicsEffect(None)
                self.setZValue(0)
                self.hide_handles()
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
        
        # Add vertices if present
        if hasattr(self.link, 'vertices') and self.link.vertices:
            for vx, vy in self.link.vertices:
                # Vertices are in logical coordinates (EPANET Y up)
                # Convert to scene coordinates (Qt Y down)
                path.lineTo(vx, -vy)
                
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
        
        self.symbol = PumpSymbolItem(self)
        self.update_symbol_position()
        
    def update_path(self):
        super().update_path()
        if hasattr(self, 'symbol'):
            self.update_symbol_position()
            
    def update_symbol_position(self):
        path = self.path()
        if path.elementCount() > 0:
            mid = path.pointAtPercent(0.5)
            self.symbol.setPos(mid)

class ValveItem(LinkItem):
    """Graphics item for Valve."""
    def __init__(self, link, from_pos, to_pos):
        super().__init__(link, from_pos, to_pos)
        self.normal_pen = QPen(QColor(220, 20, 60), 2)  # Thicker for valves
        self.normal_pen.setCosmetic(True)
        self.setPen(self.normal_pen)
        
        self.symbol = ValveSymbolItem(self)
        self.update_symbol_position()
        
    def update_path(self):
        super().update_path()
        if hasattr(self, 'symbol'):
            self.update_symbol_position()
            
    def update_symbol_position(self):
        path = self.path()
        if path.elementCount() > 0:
            mid = path.pointAtPercent(0.5)
            self.symbol.setPos(mid)

class PumpSymbolItem(QGraphicsItem):
    """Symbol for Pump."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.radius = 6.0
        
    def boundingRect(self):
        r = self.radius
        return QRectF(-r, -r, r*2, r*2)
        
    def paint(self, painter, option, widget):
        r = self.radius
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(QPointF(0,0), r, r)
        
        # Draw triangle
        painter.setBrush(QBrush(Qt.black))
        triangle = QPolygonF([
            QPointF(-r/2, r/2),
            QPointF(r/2, r/2),
            QPointF(0, -r/2)
        ])
        painter.drawPolygon(triangle)

class ValveSymbolItem(QGraphicsItem):
    """Symbol for Valve."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.radius = 6.0
        
    def boundingRect(self):
        r = self.radius
        return QRectF(-r, -r, r*2, r*2)
        
    def paint(self, painter, option, widget):
        r = self.radius
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(Qt.white))
        
        # Draw bowtie
        path = QPainterPath()
        path.moveTo(-r, -r/2)
        path.lineTo(r, r/2)
        path.lineTo(r, -r/2)
        path.lineTo(-r, r/2)
        path.closeSubpath()
        
        painter.drawPath(path)

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
