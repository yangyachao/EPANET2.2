"""Calibration Data dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
import os

class CalibrationDataDialog(QDialog):
    """Dialog for managing calibration data files."""
    
    PARAMETERS = [
        "Demand",
        "Head",
        "Pressure",
        "Quality",
        "Flow",
        "Velocity"
    ]
    
    def __init__(self, parent=None, calibration_data=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration Data")
        self.resize(600, 300)
        
        self.calibration_data = calibration_data or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Name of File"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        
        # Populate table
        self.table.setRowCount(len(self.PARAMETERS))
        for i, param in enumerate(self.PARAMETERS):
            # Parameter name (read-only)
            item_param = QTableWidgetItem(param)
            item_param.setFlags(item_param.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(i, 0, item_param)
            
            # File path
            file_path = self.calibration_data.get(param, "")
            item_file = QTableWidgetItem(file_path)
            item_file.setFlags(item_file.flags() ^ Qt.ItemIsEditable) # Make read-only, edit via Browse
            self.table.setItem(i, 1, item_file)
            
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        button_layout.addWidget(self.browse_button)
        
        self.edit_button = QPushButton("Edit...")
        self.edit_button.clicked.connect(self.edit_file)
        button_layout.addWidget(self.edit_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_file)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.help_button = QPushButton("Help")
        button_layout.addWidget(self.help_button)
        
        layout.addLayout(button_layout)
        
    def browse_file(self):
        """Browse for a calibration data file."""
        row = self.table.currentRow()
        if row < 0:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Calibration Data File", "", "Data Files (*.dat);;All Files (*.*)"
        )
        
        if file_path:
            self.table.item(row, 1).setText(file_path)
            
    def edit_file(self):
        """Open the selected file in default editor."""
        row = self.table.currentRow()
        if row < 0:
            return
            
        file_path = self.table.item(row, 1).text()
        if not file_path:
            return
            
        if os.path.exists(file_path):
            # Open file with default application
            import subprocess
            try:
                if os.name == 'nt': # Windows
                    os.startfile(file_path)
                elif os.name == 'posix': # macOS/Linux
                    subprocess.call(('open', file_path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")
        else:
            QMessageBox.warning(self, "Error", "File does not exist.")
            
    def clear_file(self):
        """Clear the file association for the selected parameter."""
        row = self.table.currentRow()
        if row < 0:
            return
            
        self.table.item(row, 1).setText("")
        
    def get_data(self):
        """Get the updated calibration data."""
        data = {}
        for i in range(self.table.rowCount()):
            param = self.table.item(i, 0).text()
            file_path = self.table.item(i, 1).text()
            if file_path:
                data[param] = file_path
        return data
