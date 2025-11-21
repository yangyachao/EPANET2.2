"""Contour view for network data."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
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
        
        self.setup_ui()
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
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        
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
        
        # We need to get values for all nodes
        # If simulation results exist, use them. Otherwise use base properties if applicable.
        
        has_results = self.project.has_results()
        
        for node in self.project.network.nodes.values():
            x_coords.append(node.x)
            y_coords.append(node.y)
            
            val = 0.0
            if has_results:
                if param == NodeParam.ELEVATION:
                    val = node.elevation
                elif param == NodeParam.DEMAND:
                    val = node.demand
                elif param == NodeParam.HEAD:
                    val = node.head
                elif param == NodeParam.PRESSURE:
                    val = node.pressure
                elif param == NodeParam.QUALITY:
                    val = node.quality
            else:
                # Fallback for input parameters
                if param == NodeParam.ELEVATION:
                    val = node.elevation
                elif param == NodeParam.DEMAND:
                    if hasattr(node, 'base_demand'):
                        val = node.base_demand
                    else:
                        val = 0.0
                else:
                    val = 0.0
            
            values.append(val)
            
        if not x_coords:
            self.canvas.draw()
            return
            
        # Create triangulation
        triang = tri.Triangulation(x_coords, y_coords)
        
        # Plot contours
        try:
            cntr = self.ax.tricontourf(triang, values, levels=14, cmap="viridis")
            self.figure.colorbar(cntr, ax=self.ax, label=param.name)
            self.ax.set_title(f"Network {param.name} Contour")
            self.ax.set_aspect('equal')
            
            # Plot node locations
            self.ax.plot(x_coords, y_coords, 'ko', ms=3)
            
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error plotting contour: {str(e)}", 
                        ha='center', va='center', transform=self.ax.transAxes)
            
        self.canvas.draw()
