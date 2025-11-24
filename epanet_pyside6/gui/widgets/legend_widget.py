"""Legend widget for displaying color scales."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen

class LegendWidget(QWidget):
    """Widget for displaying color legend."""
    
    options_requested = Signal()

    def __init__(self, title="Legend", parent=None):
        super().__init__(parent)
        self.title = title
        self.colors = [
            QColor(0, 0, 255),    # Blue
            QColor(0, 255, 255),  # Cyan
            QColor(0, 255, 0),    # Green
            QColor(255, 255, 0),  # Yellow
            QColor(255, 0, 0)     # Red
        ]
        self.values = [0.0, 25.0, 50.0, 75.0, 100.0]
        self.parameter_name = ""
        self.units = ""
        
        self._drag_start_pos = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        self.setMinimumWidth(150)
        self.setMinimumHeight(200)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200); border: 1px solid #ccc; border-radius: 5px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        layout.addWidget(self.title_label)
        
        # Custom paint widget for gradient
        self.scale_widget = LegendScale(self)
        layout.addWidget(self.scale_widget)
        
    def set_data(self, parameter_name, units, values, colors):
        """Set legend data."""
        self.parameter_name = parameter_name
        self.units = units
        self.values = values
        self.colors = colors
        
        self.title_label.setText(f"{parameter_name}\n({units})")
        self.scale_widget.update()
        
    def set_visible(self, visible):
        super().setVisible(visible)

    # Draggability
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start_pos:
            # Calculate new position
            delta = event.pos() - self._drag_start_pos
            new_pos = self.pos() + delta
            
            # Keep within parent bounds (optional but good)
            if self.parent():
                parent_rect = self.parent().rect()
                # Simple clamping
                x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
                y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
                new_pos.setX(x)
                new_pos.setY(y)
            
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)

    # Context Menu
    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        options_action = menu.addAction("Options...")
        options_action.triggered.connect(self.options_requested.emit)
        menu.exec(event.globalPos())


class LegendScale(QWidget):
    """Widget to draw the color scale."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_legend = parent
        self.setStyleSheet("border: none; background: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        x = 10
        y = 10
        w = 20
        h = rect.height() - 20
        
        # Draw color boxes
        num_intervals = len(self.parent_legend.colors)
        box_h = h / num_intervals
        
        for i, color in enumerate(self.parent_legend.colors):
            box_rect = (x, y + i * box_h, w, box_h)
            painter.fillRect(*box_rect, color)
            painter.drawRect(*box_rect)
            
            # Draw text
            if i < len(self.parent_legend.values):
                val = self.parent_legend.values[len(self.parent_legend.values) - 1 - i]
                text = f"{val:.2f}"
                painter.drawText(x + w + 10, int(y + i * box_h + box_h/2 + 5), text)
                
        # Draw < and > labels
        # This is a simplified version, real EPANET legend has intervals
