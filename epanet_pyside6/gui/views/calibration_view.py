"""Calibration view for comparing simulation results with observed data."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QComboBox, QLabel, QHeaderView, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from core.constants import NodeParam, LinkParam

class CalibrationView(QWidget):
    """Widget for calibration analysis."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.observed_data = [] # List of dicts: {type, id, param, value}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QHBoxLayout(self)
        
        # Left side: Data Input
        left_panel = QVBoxLayout()
        
        # Controls
        controls_group = QGroupBox("Data Input")
        controls_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Node", "Link"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        controls_layout.addRow("Object Type:", self.type_combo)
        
        self.param_combo = QComboBox()
        self.update_params()
        controls_layout.addRow("Parameter:", self.param_combo)
        
        self.id_input = QComboBox() # Should be editable or a list
        self.id_input.setEditable(True)
        controls_layout.addRow("Object ID:", self.id_input)
        
        self.value_input = QComboBox() # Reusing combo for simple text input look, but QLineEdit is better
        from PySide6.QtWidgets import QLineEdit
        self.value_input = QLineEdit()
        controls_layout.addRow("Observed Value:", self.value_input)
        
        add_btn = QPushButton("Add Observation")
        add_btn.clicked.connect(self.add_observation)
        controls_layout.addRow(add_btn)
        
        controls_group.setLayout(controls_layout)
        left_panel.addWidget(controls_group)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Type", "ID", "Param", "Observed", "Simulated"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_panel.addWidget(self.table)
        
        # Actions
        action_layout = QHBoxLayout()
        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.import_csv)
        action_layout.addWidget(import_btn)
        
        clear_btn = QPushButton("Clear Data")
        clear_btn.clicked.connect(self.clear_data)
        action_layout.addWidget(clear_btn)
        
        update_btn = QPushButton("Update Comparison")
        update_btn.clicked.connect(self.update_comparison)
        action_layout.addWidget(update_btn)
        
        left_panel.addLayout(action_layout)
        
        # Statistics
        self.stats_label = QLabel("Statistics:\nRMSE: N/A\nCorrelation: N/A")
        left_panel.addWidget(self.stats_label)
        
        layout.addLayout(left_panel, stretch=1)
        
        # Right side: Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('bottom', 'Observed')
        self.plot_widget.setLabel('left', 'Simulated')
        self.plot_widget.setTitle("Observed vs Simulated")
        
        # Add diagonal line
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=45, pen=pg.mkPen('g', style=Qt.DashLine)))
        
        layout.addWidget(self.plot_widget, stretch=2)
        
    def update_params(self):
        """Update parameter combo based on type."""
        self.param_combo.clear()
        if self.type_combo.currentText() == "Node":
            for param in NodeParam:
                self.param_combo.addItem(param.name, param)
        else:
            for param in LinkParam:
                self.param_combo.addItem(param.name, param)
                
    def on_type_changed(self, text):
        """Handle type change."""
        self.update_params()
        
    def add_observation(self):
        """Add single observation."""
        obj_type = self.type_combo.currentText()
        obj_id = self.id_input.currentText()
        param = self.param_combo.currentData()
        
        try:
            value = float(self.value_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Value must be a number")
            return
            
        self.observed_data.append({
            'type': obj_type,
            'id': obj_id,
            'param': param,
            'value': value,
            'simulated': 0.0
        })
        
        self.refresh_table()
        self.value_input.clear()
        self.id_input.setFocus()
        
    def import_csv(self):
        """Import observations from CSV."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Observations", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
            
        import csv
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                # Expected columns: Type, ID, Parameter, Value
                for row in reader:
                    # Basic validation and conversion
                    obj_type = row.get('Type', 'Node')
                    obj_id = row.get('ID', '')
                    param_name = row.get('Parameter', '')
                    value_str = row.get('Value', '0')
                    
                    # Map param name to enum
                    param = None
                    if obj_type == 'Node':
                        for p in NodeParam:
                            if p.name == param_name:
                                param = p
                                break
                    else:
                        for p in LinkParam:
                            if p.name == param_name:
                                param = p
                                break
                                
                    if obj_id and param:
                        self.observed_data.append({
                            'type': obj_type,
                            'id': obj_id,
                            'param': param,
                            'value': float(value_str),
                            'simulated': 0.0
                        })
            self.refresh_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))
            
    def clear_data(self):
        """Clear all data."""
        self.observed_data = []
        self.refresh_table()
        self.plot_widget.clear()
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=45, pen=pg.mkPen('g', style=Qt.DashLine)))
        self.stats_label.setText("Statistics:\nRMSE: N/A\nCorrelation: N/A")
        
    def refresh_table(self):
        """Refresh table display."""
        self.table.setRowCount(len(self.observed_data))
        for i, data in enumerate(self.observed_data):
            self.table.setItem(i, 0, QTableWidgetItem(data['type']))
            self.table.setItem(i, 1, QTableWidgetItem(data['id']))
            self.table.setItem(i, 2, QTableWidgetItem(data['param'].name))
            self.table.setItem(i, 3, QTableWidgetItem(f"{data['value']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{data['simulated']:.2f}"))
            
    def update_comparison(self):
        """Update simulated values and plot."""
        if not self.project.has_results():
            QMessageBox.warning(self, "No Results", "Please run a simulation first.")
            return
            
        simulated_values = []
        observed_values = []
        
        for data in self.observed_data:
            # Get simulated value
            sim_val = 0.0
            if data['type'] == 'Node':
                sim_val = self.project.engine.get_node_result(data['id'], data['param'])
            else:
                sim_val = self.project.engine.get_link_result(data['id'], data['param'])
                
            data['simulated'] = sim_val
            simulated_values.append(sim_val)
            observed_values.append(data['value'])
            
        self.refresh_table()
        
        # Plot
        self.plot_widget.clear()
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=45, pen=pg.mkPen('g', style=Qt.DashLine)))
        
        if observed_values:
            self.plot_widget.plot(observed_values, simulated_values, pen=None, symbol='o', symbolBrush='b')
            
            # Statistics
            obs = np.array(observed_values)
            sim = np.array(simulated_values)
            
            rmse = np.sqrt(np.mean((obs - sim)**2))
            if len(obs) > 1:
                corr = np.corrcoef(obs, sim)[0, 1]
            else:
                corr = 0.0
                
            self.stats_label.setText(f"Statistics:\nRMSE: {rmse:.4f}\nCorrelation: {corr:.4f}")
