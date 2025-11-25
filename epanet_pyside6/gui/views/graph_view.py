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
        
        self.graph_options = {
            'show_grid': True,
            'show_legend': True,
            'white_background': True,
            'line_width': 2
        }
        
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
        
        self.options_btn = QPushButton("Options...")
        self.options_btn.clicked.connect(self.show_options)
        controls_layout.addWidget(self.options_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Plot area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('bottom', 'Time (hours)')
        layout.addWidget(self.plot_widget)
        
    def set_data(self, obj_type, obj_ids, param):
        """Set the data to plot."""
        self.object_type = obj_type
        self.object_ids = obj_ids if isinstance(obj_ids, list) else [obj_ids]
        
        # Update parameter combo
        self.param_combo.blockSignals(True)
        self.param_combo.clear()
        
        if obj_type == 'Node':
            for p in NodeParam:
                self.param_combo.addItem(p.name, p)
        elif obj_type == 'Link':
            for p in LinkParam:
                self.param_combo.addItem(p.name, p)
                
        # Select current parameter
        index = self.param_combo.findData(param)
        if index >= 0:
            self.param_combo.setCurrentIndex(index)
            
        self.param_combo.blockSignals(False)
        
        # Refresh
        self.refresh_plot()
        
    def refresh_plot(self):
        """Refresh the plot data."""
        self.plot_widget.clear()
        
        # Apply options
        opts = self.graph_options
        self.plot_widget.setBackground('w' if opts['white_background'] else 'k')
        self.plot_widget.showGrid(x=opts['show_grid'], y=opts['show_grid'])
        
        if opts['show_legend']:
            self.plot_widget.addLegend()
        
        if not self.project.has_results():
            self.plot_widget.setTitle("No simulation results available")
            return
            
        if not self.object_ids:
            return
            
        param = self.param_combo.currentData()
        if not param:
            return
            
        try:
            # Color cycle for multiple lines
            colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
            if not opts['white_background']:
                colors = ['c', 'm', 'y', 'g', 'r', 'b', 'w'] # Brighter colors for dark bg
            
            width = opts['line_width']
            
            for i, obj_id in enumerate(self.object_ids):
                times, values = self.project.get_time_series(self.object_type, obj_id, param)
                color = colors[i % len(colors)]
                self.plot_widget.plot(times, values, pen=pg.mkPen(color=color, width=width), name=f"{obj_id}")
            
            self.plot_widget.setTitle(f"{self.object_type} {param.name}")
            self.plot_widget.setLabel('left', param.name)
            
        except Exception as e:
            self.plot_widget.setTitle(f"Error: {str(e)}")

    def show_options(self):
        """Show graph options dialog."""
        from gui.dialogs.graph_options_dialog import GraphOptionsDialog
        
        dialog = GraphOptionsDialog(self, self.graph_options)
        if dialog.exec():
            self.graph_options = dialog.get_options()
            self.refresh_plot()

    def export_data(self):
        """Export graph data to CSV."""
        if not self.object_ids:
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
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                header = ["Time (hours)"]
                for obj_id in self.object_ids:
                    header.append(f"{obj_id} - {param.name}")
                writer.writerow(header)
                
                # Data
                # Get data for all objects
                all_data = []
                times = None
                for obj_id in self.object_ids:
                    t, v = self.project.get_time_series(self.object_type, obj_id, param)
                    if times is None:
                        times = t
                    all_data.append(v)
                
                # Write rows
                if times is not None:
                    for i, t in enumerate(times):
                        row = [t]
                        for data in all_data:
                            row.append(data[i] if i < len(data) else "")
                        writer.writerow(row)
                    
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
