"""Map browser widget for controlling map visualization."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSlider, QToolButton, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

class MapBrowser(QWidget):
    """Widget for controlling map visualization parameters."""
    
    # Signals
    node_parameter_changed = Signal(str)  # parameter name
    link_parameter_changed = Signal(str)  # parameter name
    time_changed = Signal(int)  # time step index
    animate_toggled = Signal(bool)
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # View Selection Group
        view_group = QGroupBox("View")
        view_layout = QVBoxLayout(view_group)
        
        # Node parameter
        view_layout.addWidget(QLabel("Nodes:"))
        self.node_combo = QComboBox()
        self.node_combo.addItems([
            "NONE", "ELEVATION", "BASEDEMAND", "INITIALQUALITY",
            "DEMAND", "HEAD", "PRESSURE", "QUALITY"
        ])
        self.node_combo.currentTextChanged.connect(self.on_node_param_changed)
        self.node_combo.setCurrentText("PRESSURE")
        view_layout.addWidget(self.node_combo)
        
        # Link parameter
        view_layout.addWidget(QLabel("Links:"))
        self.link_combo = QComboBox()
        self.link_combo.addItems([
            "NONE", "LENGTH", "DIAMETER", "ROUGHNESS",
            "FLOW", "VELOCITY", "UNITHEADLOSS", "FRICTIONFACTOR",
            "REACTIONRATE", "QUALITY"
        ])
        self.link_combo.currentTextChanged.connect(self.on_link_param_changed)
        self.link_combo.setCurrentText("FLOW")
        view_layout.addWidget(self.link_combo)
        
        layout.addWidget(view_group)
        
        # Time Control Group
        time_group = QGroupBox("Time")
        time_layout = QVBoxLayout(time_group)
        
        # Time label
        self.time_label = QLabel("0:00 Hrs")
        self.time_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_label)
        
        # Slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 0) 
        self.time_slider.valueChanged.connect(self.on_time_slider_changed)
        time_layout.addWidget(self.time_slider)
        
        # Animation controls
        anim_layout = QHBoxLayout()
        
        self.rewind_btn = QToolButton()
        self.rewind_btn.setText("<<")
        self.rewind_btn.clicked.connect(self.rewind)
        anim_layout.addWidget(self.rewind_btn)
        
        self.back_btn = QToolButton()
        self.back_btn.setText("<")
        self.back_btn.clicked.connect(self.step_back)
        anim_layout.addWidget(self.back_btn)
        
        self.play_btn = QToolButton()
        self.play_btn.setText(">") # Play icon ideally
        self.play_btn.setCheckable(True)
        self.play_btn.toggled.connect(self.toggle_animation)
        anim_layout.addWidget(self.play_btn)
        
        self.forward_btn = QToolButton()
        self.forward_btn.setText(">|")
        self.forward_btn.clicked.connect(self.step_forward)
        anim_layout.addWidget(self.forward_btn)
        
        time_layout.addLayout(anim_layout)
        
        layout.addWidget(time_group)
        layout.addStretch()
        
        self.time_steps = [0]
        
    def set_time_steps(self, time_steps):
        """Set available time steps (in seconds)."""
        self.time_steps = time_steps
        self.time_slider.setRange(0, len(time_steps) - 1)
        self.time_slider.setValue(0)
        self.on_time_slider_changed(0)
        
    def on_node_param_changed(self, text):
        """Handle node parameter change."""
        param = None if text == "None" else text
        self.node_parameter_changed.emit(param)
        
    def on_link_param_changed(self, text):
        """Handle link parameter change."""
        param = None if text == "None" else text
        self.link_parameter_changed.emit(param)
        
    def on_time_slider_changed(self, value):
        """Handle time slider change."""
        if 0 <= value < len(self.time_steps):
            seconds = self.time_steps[value]
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) / 60)
            self.time_label.setText(f"{hours}:{mins:02d} Hrs")
            self.time_changed.emit(value)
        
    def rewind(self):
        self.time_slider.setValue(0)
        
    def step_back(self):
        self.time_slider.setValue(max(0, self.time_slider.value() - 1))
        
    def toggle_animation(self, checked):
        self.animate_toggled.emit(checked)
        if checked:
            self.play_btn.setText("||")
        else:
            self.play_btn.setText(">")
            
    def step_forward(self):
        self.time_slider.setValue(min(self.time_slider.maximum(), self.time_slider.value() + 1))
