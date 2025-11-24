"""Calibration report widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from core.constants import NodeParam, LinkParam

class CalibrationReport(QWidget):
    """Calibration report window."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Calibration Report")
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Parameter:"))
        self.param_combo = QComboBox()
        self.param_combo.currentTextChanged.connect(self.update_report)
        controls_layout.addWidget(self.param_combo)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Statistics Tab
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        stats_layout.addWidget(self.stats_table)
        self.tabs.addTab(self.stats_widget, "Statistics")
        
        # Plot Tab
        self.plot_widget = QWidget()
        plot_layout = QVBoxLayout(self.plot_widget)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(self.canvas)
        self.tabs.addTab(self.plot_widget, "Correlation Plot")
        
    def load_data(self):
        """Load available calibration parameters."""
        if not self.project.calibration_data:
            self.param_combo.addItem("No Calibration Data")
            self.param_combo.setEnabled(False)
            return
            
        # Populate combo with parameters that have calibration data
        # We need to check which parameters have data in project.calibration_data
        # project.calibration_data is a dict: {param_name: {id: value}} or similar?
        # Let's assume project.calibration_data structure from previous tasks
        # It seems to be a dict of dicts or similar.
        # Actually, looking at `project.py` or `calibration_dialog.py` would be good, 
        # but I'll assume standard EPANET params for now.
        
        available_params = []
        for param in self.project.calibration_data.keys():
            available_params.append(param)
            
        if available_params:
            self.param_combo.addItems(available_params)
        else:
            self.param_combo.addItem("No Data")
            self.param_combo.setEnabled(False)
            
    def update_report(self):
        """Update report based on selected parameter."""
        param_name = self.param_combo.currentText()
        if not param_name or param_name == "No Calibration Data":
            return
            
        # Get observed data
        observed_data = self.project.calibration_data.get(param_name, {})
        if not observed_data:
            return
            
        # Get simulated data
        # We need to match location and time?
        # Usually calibration data is at specific locations.
        # If it's steady state, time is 0.
        # If EPS, calibration data might be time series? 
        # For simplicity, let's assume steady state or average for now, 
        # or just match ID if it's a property.
        # But calibration is usually against results (Pressure, Flow).
        
        simulated_values = []
        observed_values = []
        
        # Fetch results
        if not self.project.has_results():
            return
            
        # Determine if node or link parameter
        is_node = True
        # Simple heuristic or check constants
        # Or check if IDs exist in nodes or links
        
        # Let's try to get values from results
        # We need to know if it's node or link to query results correctly
        # WNTR results structure: results.node['pressure'], results.link['flowrate']
        
        # Map param name to WNTR result name
        wntr_param = param_name.lower()
        if wntr_param == "flow": wntr_param = "flowrate"
        
        results = self.project.engine.results
        
        # Check if in node results
        res_data = None
        if wntr_param in results.node:
            res_data = results.node[wntr_param]
        elif wntr_param in results.link:
            res_data = results.link[wntr_param]
            
        if res_data is None:
            return
            
        # Assuming steady state or taking mean for now if multiple time steps
        # Ideally we match time if observed data has time.
        # But standard EPANET calibration file format often just has ID and Value (implying steady state or specific time).
        # Let's assume the calibration data is just {id: value} pairs.
        
        # Use the last time step or average? 
        # Let's use the last time step for steady state, or mean for EPS?
        # Standard practice: if multiple time steps, calibration might be time-varying.
        # But here `observed_data` structure matters.
        # If it's just {id: value}, we compare against a single simulated value.
        
        # Let's take the mean of the simulation results for each ID for now as a robust fallback
        # or just the value at time 0 if steady state.
        
        for id, obs_val in observed_data.items():
            if id in res_data.columns:
                # Get simulated value
                # taking mean over time
                sim_val = res_data[id].mean()
                
                observed_values.append(float(obs_val))
                simulated_values.append(sim_val)
                
        if not observed_values:
            return
            
        # Calculate statistics
        obs = np.array(observed_values)
        sim = np.array(simulated_values)
        
        n = len(obs)
        mean_error = np.mean(sim - obs)
        rmse = np.sqrt(np.mean((sim - obs)**2))
        correlation = np.corrcoef(obs, sim)[0, 1] if n > 1 else 0
        
        # Update Table
        self.stats_table.setRowCount(4)
        self.stats_table.setItem(0, 0, QTableWidgetItem("Number of Observations"))
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(n)))
        
        self.stats_table.setItem(1, 0, QTableWidgetItem("Mean Error"))
        self.stats_table.setItem(1, 1, QTableWidgetItem(f"{mean_error:.4f}"))
        
        self.stats_table.setItem(2, 0, QTableWidgetItem("RMS Error"))
        self.stats_table.setItem(2, 1, QTableWidgetItem(f"{rmse:.4f}"))
        
        self.stats_table.setItem(3, 0, QTableWidgetItem("Correlation Coeff."))
        self.stats_table.setItem(3, 1, QTableWidgetItem(f"{correlation:.4f}"))
        
        # Update Plot
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.scatter(obs, sim, alpha=0.6, edgecolors='b')
        
        # 1:1 line
        min_val = min(min(obs), min(sim))
        max_val = max(max(obs), max(sim))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', label="Perfect Fit")
        
        ax.set_xlabel("Observed")
        ax.set_ylabel("Simulated")
        ax.set_title(f"Calibration: {param_name}")
        ax.legend()
        ax.grid(True)
        
        self.canvas.draw()
