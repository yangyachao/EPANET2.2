"""Demand Editor Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt

class DemandEditorDialog(QDialog):
    """Dialog for editing junction demands."""
    
    def __init__(self, junction, parent=None):
        super().__init__(parent)
        self.junction = junction
        self.setWindowTitle(f"Demands for Junction {junction.id}")
        self.resize(400, 300)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Base Demand", "Time Pattern", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_row)
        btn_layout.addWidget(add_btn)
        
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_row)
        btn_layout.addWidget(del_btn)
        
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def load_data(self):
        """Load demands from junction."""
        # Add primary demand
        self.add_row_data(self.junction.base_demand, self.junction.demand_pattern or "", "")
        
        # Add secondary demands
        for demand in self.junction.demands:
            self.add_row_data(
                demand.get('base_demand', 0.0),
                demand.get('pattern', ""),
                demand.get('name', "")
            )
            
    def add_row_data(self, base_demand, pattern, category):
        """Add a row with data."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(str(base_demand)))
        self.table.setItem(row, 1, QTableWidgetItem(pattern))
        self.table.setItem(row, 2, QTableWidgetItem(category))
        
    def add_row(self):
        """Add a new empty row."""
        self.add_row_data(0.0, "", "")
        
    def delete_row(self):
        """Delete selected row."""
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            
    def get_data(self):
        """Get data from table."""
        demands = []
        for row in range(self.table.rowCount()):
            try:
                base = float(self.table.item(row, 0).text())
            except ValueError:
                base = 0.0
                
            pattern = self.table.item(row, 1).text()
            category = self.table.item(row, 2).text()
            
            demands.append({
                'base_demand': base,
                'pattern': pattern,
                'name': category
            })
        return demands
