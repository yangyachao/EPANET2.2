"""Contour view for network data."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QSlider
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.tri as tri
import numpy as np
from core.constants import NodeParam

class ContourView(QWidget):
    """Widget for displaying contour plots of network data."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.simulation_times = []
        self.current_time_index = 0
        
        self.setup_ui()
        self.load_data()
        self.refresh_plot()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.param_combo = QComboBox()
        for param in NodeParam:
            self.param_combo.addItem(param.name, param)
        self.param_combo.currentTextChanged.connect(self.refresh_plot)
        
        controls_layout.addWidget(QLabel("Parameter:"))
        controls_layout.addWidget(self.param_combo)
        
        # Time Slider
        self.time_label = QLabel("Time: 0:00")
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(self.on_time_changed)
        
        controls_layout.addWidget(QLabel("   ")) # Spacer
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.time_slider)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        
    def set_parameter(self, param):
        """Set the parameter to display."""
        index = self.param_combo.findData(param)
        if index >= 0:
            self.param_combo.setCurrentIndex(index)
            
    def load_data(self):
        """Load simulation data if available."""
        if self.project.has_results():
            self.simulation_times = self.project.get_simulation_times()
            if self.simulation_times:
                self.time_slider.setEnabled(True)
                self.time_slider.setRange(0, len(self.simulation_times) - 1)
                self.time_slider.setValue(0)
                self.update_time_label(0)
            else:
                self.time_slider.setEnabled(False)
                self.time_label.setText("Time: N/A")
        else:
            self.time_slider.setEnabled(False)
            self.time_label.setText("Time: Base")
            
    def on_time_changed(self, value):
        """Handle time slider change."""
        self.current_time_index = value
        self.update_time_label(value)
        self.refresh_plot()
        
    def update_time_label(self, index):
        """Update time label text."""
        if 0 <= index < len(self.simulation_times):
            hours = self.simulation_times[index]
            self.time_label.setText(f"Time: {hours:.2f} hrs")
            
    def refresh_plot(self):
        """Refresh the contour plot."""
        # Clear the entire figure to remove old colorbars
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        param = self.param_combo.currentData()
        if not param:
            return
            
        # Get node data
        x_coords = []
        y_coords = []
        values = []
        
        has_results = self.project.has_results() and self.simulation_times
        
        # Get values for current time step if available
        current_values = {}
        if has_results:
            current_values = self.project.get_network_values_at_time(param, self.current_time_index)
        
        for node in self.project.network.nodes.values():
            x_coords.append(node.x)
            y_coords.append(node.y)
            
            val = 0.0
            if has_results and node.id in current_values:
                val = current_values[node.id]
            else:
                # Fallback for input parameters or no results
                if param == NodeParam.ELEVATION:
                    val = node.elevation
                elif param == NodeParam.DEMAND:
                    if hasattr(node, 'base_demand'):
                        val = node.base_demand
                elif param == NodeParam.HEAD:
                    val = node.head # Should be base head if no results
                elif param == NodeParam.PRESSURE:
                    val = node.pressure
                elif param == NodeParam.QUALITY:
                    val = node.quality
            
            values.append(val)
            
        if not x_coords:
            self.canvas.draw()
            return
            
        # Create triangulation
        triang = tri.Triangulation(x_coords, y_coords)
        
        # Plot contours
        try:
            # Use tricontourf
            # Determine levels based on value range
            min_val = min(values)
            max_val = max(values)
            if max_val == min_val:
                max_val += 0.1 # Avoid singular range
                
            levels = np.linspace(min_val, max_val, 15)
            
            cntr = self.ax.tricontourf(triang, values, levels=levels, cmap="viridis")
            self.figure.colorbar(cntr, ax=self.ax, label=param.name)
            
            title = f"Network {param.name}"
            if has_results:
                title += f" at {self.simulation_times[self.current_time_index]:.2f} hrs"
            self.ax.set_title(title)
            
            self.ax.set_aspect('equal')
            
            # Plot node locations
            self.ax.plot(x_coords, y_coords, 'ko', ms=2, alpha=0.5)
            
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error plotting contour: {str(e)}", 
                        ha='center', va='center', transform=self.ax.transAxes)
            
        self.canvas.draw()
