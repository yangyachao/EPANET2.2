"""Energy report widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

class EnergyReport(QWidget):
    """Energy report window."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Energy Report")
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Table Tab
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Pump", "Percent Utilization", "Avg. Efficiency", 
            "Kw-hr/Mgal", "Avg. Kw", "Peak Kw"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.table)
        self.tabs.addTab(self.table_widget, "Table")
        
        # Chart Tab
        self.chart_widget = QWidget()
        chart_layout = QVBoxLayout(self.chart_widget)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.tabs.addTab(self.chart_widget, "Chart")
        
    def load_data(self):
        """Load energy data from results."""
        if not self.project.has_results():
            return
            
        results = self.project.engine.results
        
        # WNTR energy results are usually in results.link['energy'] if computed?
        # Actually WNTR provides energy usage in a specific way.
        # Let's check if 'energy' is in results.link
        
        energy_data = {}
        
        if 'energy' in results.link:
             # This might be instantaneous energy.
             # We need aggregated stats.
             # WNTR might not compute these aggregates automatically in the basic result object.
             # We might need to compute them or check if WNTR has a specific energy report function.
             pass
             
        # For now, let's mock or try to compute basic stats if possible, 
        # or just show what we have.
        # If we can't get real energy stats easily without re-running with specific flags,
        # we'll show a placeholder or basic instantaneous values averaged.
        
        # Placeholder logic for now to prevent crash and show structure
        # In a real implementation, we'd parse the EPANET report file for this section
        # or compute it from time series.
        
        # Let's assume we can get pumps
        pumps = self.project.network.pumps
        self.table.setRowCount(len(pumps))
        
        for i, (pump_id, pump) in enumerate(pumps.items()):
            self.table.setItem(i, 0, QTableWidgetItem(pump_id))
            # Placeholders
            self.table.setItem(i, 1, QTableWidgetItem("N/A"))
            self.table.setItem(i, 2, QTableWidgetItem("N/A"))
            self.table.setItem(i, 3, QTableWidgetItem("N/A"))
            self.table.setItem(i, 4, QTableWidgetItem("N/A"))
            self.table.setItem(i, 5, QTableWidgetItem("N/A"))
            
        # Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, "Energy Chart - Data Not Available", 
               ha='center', va='center', transform=ax.transAxes)
        self.canvas.draw()
