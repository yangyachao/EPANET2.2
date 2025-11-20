"""Graph view for simulation results."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QPushButton, QFileDialog
import pyqtgraph as pg
from core.constants import NodeParam, LinkParam

class GraphView(QWidget):
    """Widget for displaying time series graphs."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.object_id = None
        self.object_type = None # 'Node' or 'Link'
        self.param_type = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Controls area
        controls_layout = QHBoxLayout()
        
        self.param_combo = QComboBox()
        self.param_combo.currentTextChanged.connect(self.refresh_plot)
        controls_layout.addWidget(QLabel("Parameter:"))
        controls_layout.addWidget(self.param_combo)
        
        self.export_data_btn = QPushButton("Export Data")
        self.export_data_btn.clicked.connect(self.export_data)
        controls_layout.addWidget(self.export_data_btn)
        
        self.export_img_btn = QPushButton("Export Image")
        self.export_img_btn.clicked.connect(self.export_image)
        controls_layout.addWidget(self.export_img_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Plot area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('bottom', 'Time (hours)')
        layout.addWidget(self.plot_widget)
        
    def set_object(self, obj_type, obj_id):
        """Set the object to plot."""
        self.object_type = obj_type
        self.object_id = obj_id
        
        # Update parameter combo
        self.param_combo.blockSignals(True)
        self.param_combo.clear()
        
        if obj_type == 'Node':
            for param in NodeParam:
                self.param_combo.addItem(param.name, param)
        elif obj_type == 'Link':
            for param in LinkParam:
                self.param_combo.addItem(param.name, param)
                
        self.param_combo.blockSignals(False)
        
        # Refresh
        self.refresh_plot()
        
    def refresh_plot(self):
        """Refresh the plot data."""
        self.plot_widget.clear()
        
        if not self.project.has_results():
            self.plot_widget.setTitle("No simulation results available")
            return
            
        if not self.object_id:
            return
            
        param = self.param_combo.currentData()
        if not param:
            return
            
        # Fetch data from engine
        # We need to implement a method in engine/project to get time series
        # For now, we'll try to get it from the results object directly via engine
        
        try:
            times, values = self.project.get_time_series(self.object_type, self.object_id, param)
            
            self.plot_widget.plot(times, values, pen=pg.mkPen(color='b', width=2))
            self.plot_widget.setTitle(f"{self.object_type} {self.object_id} - {param.name}")
            self.plot_widget.setLabel('left', param.name)
            
        except Exception as e:
            self.plot_widget.setTitle(f"Error: {str(e)}")

    def export_data(self):
        """Export graph data to CSV."""
        if not self.object_id:
            return
            
        param = self.param_combo.currentData()
        if not param:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            times, values = self.project.get_time_series(self.object_type, self.object_id, param)
            
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time (hours)", param.name])
                for t, v in zip(times, values):
                    writer.writerow([t, v])
                    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", str(e))
            
    def export_image(self):
        """Export graph as image."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Image", "", "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            # Use pyqtgraph exporter
            import pyqtgraph.exporters
            exporter = pyqtgraph.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(filename)
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", str(e))
