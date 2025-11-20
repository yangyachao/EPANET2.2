"""Energy analysis view."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QHeaderView
)
from PySide6.QtCore import Qt

class EnergyView(QWidget):
    """Widget for displaying pump energy analysis."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Pump Energy Usage"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Pump ID", "Percent Utilization", "Avg. Efficiency",
            "Kw-hr/Mgal", "Avg. kW", "Peak kW"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
    def refresh_data(self):
        """Refresh energy data."""
        self.table.setRowCount(0)
        
        if not self.project.has_results():
            return
            
        pumps = self.project.network.get_pumps()
        self.table.setRowCount(len(pumps))
        
        for i, pump in enumerate(pumps):
            # TODO: Get actual energy stats from engine
            # Currently WNTR might not expose all these directly without calculation
            # We will show placeholders or basic energy if available
            
            energy = self.project.get_pump_energy(pump.id)
            
            self.table.setItem(i, 0, QTableWidgetItem(pump.id))
            self.table.setItem(i, 1, QTableWidgetItem("N/A")) # Utilization
            self.table.setItem(i, 2, QTableWidgetItem("N/A")) # Efficiency
            self.table.setItem(i, 3, QTableWidgetItem("N/A")) # Kw-hr/Mgal
            self.table.setItem(i, 4, QTableWidgetItem(f"{energy:.2f}")) # Avg kW (using energy as placeholder)
            self.table.setItem(i, 5, QTableWidgetItem("N/A")) # Peak kW
