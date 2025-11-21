"""Analysis Options Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QComboBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any


class AnalysisOptionsDialog(QDialog):
    """Dialog for editing analysis options."""
    
    options_updated = Signal(dict)  # Emits updated options dictionary
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.options_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Analysis Options")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.hydraulics_tab = self.create_hydraulics_tab()
        self.quality_tab = self.create_quality_tab()
        self.reactions_tab = self.create_reactions_tab()
        self.times_tab = self.create_times_tab()
        self.energy_tab = self.create_energy_tab()
        
        self.tab_widget.addTab(self.hydraulics_tab, "Hydraulics")
        self.tab_widget.addTab(self.quality_tab, "Quality")
        self.tab_widget.addTab(self.reactions_tab, "Reactions")
        self.tab_widget.addTab(self.times_tab, "Times")
        self.tab_widget.addTab(self.energy_tab, "Energy")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_changes)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)
        
        layout.addLayout(button_layout)
        
    def create_hydraulics_tab(self) -> QWidget:
        """Create hydraulics options tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        row = 0
        
        # Flow Units
        layout.addWidget(QLabel("Flow Units:"), row, 0)
        self.flow_units_combo = QComboBox()
        self.flow_units_combo.addItems(["CFS", "GPM", "MGD", "IMGD", "AFD", "LPS", "LPM", "MLD", "CMH", "CMD"])
        layout.addWidget(self.flow_units_combo, row, 1)
        row += 1
        
        # Headloss Formula
        layout.addWidget(QLabel("Headloss Formula:"), row, 0)
        self.headloss_combo = QComboBox()
        self.headloss_combo.addItems(["Hazen-Williams", "Darcy-Weisbach", "Chezy-Manning"])
        layout.addWidget(self.headloss_combo, row, 1)
        row += 1
        
        # Specific Gravity
        layout.addWidget(QLabel("Specific Gravity:"), row, 0)
        self.specific_gravity_spin = QDoubleSpinBox()
        self.specific_gravity_spin.setRange(0.001, 10.0)
        self.specific_gravity_spin.setDecimals(3)
        self.specific_gravity_spin.setValue(1.0)
        layout.addWidget(self.specific_gravity_spin, row, 1)
        row += 1
        
        # Viscosity
        layout.addWidget(QLabel("Relative Viscosity:"), row, 0)
        self.viscosity_spin = QDoubleSpinBox()
        self.viscosity_spin.setRange(0.001, 10.0)
        self.viscosity_spin.setDecimals(3)
        self.viscosity_spin.setValue(1.0)
        layout.addWidget(self.viscosity_spin, row, 1)
        row += 1
        
        # Maximum Trials
        layout.addWidget(QLabel("Maximum Trials:"), row, 0)
        self.trials_spin = QSpinBox()
        self.trials_spin.setRange(1, 1000)
        self.trials_spin.setValue(40)
        layout.addWidget(self.trials_spin, row, 1)
        row += 1
        
        # Accuracy
        layout.addWidget(QLabel("Accuracy:"), row, 0)
        self.accuracy_spin = QDoubleSpinBox()
        self.accuracy_spin.setRange(0.00001, 1.0)
        self.accuracy_spin.setDecimals(6)
        self.accuracy_spin.setValue(0.001)
        layout.addWidget(self.accuracy_spin, row, 1)
        row += 1
        
        # Unbalanced
        layout.addWidget(QLabel("If Unbalanced:"), row, 0)
        self.unbalanced_combo = QComboBox()
        self.unbalanced_combo.addItems(["Stop", "Continue"])
        layout.addWidget(self.unbalanced_combo, row, 1)
        row += 1
        
        # Demand Multiplier
        layout.addWidget(QLabel("Demand Multiplier:"), row, 0)
        self.demand_mult_spin = QDoubleSpinBox()
        self.demand_mult_spin.setRange(0.0, 10.0)
        self.demand_mult_spin.setDecimals(2)
        self.demand_mult_spin.setValue(1.0)
        layout.addWidget(self.demand_mult_spin, row, 1)
        row += 1
        
        # Emitter Exponent
        layout.addWidget(QLabel("Emitter Exponent:"), row, 0)
        self.emitter_exp_spin = QDoubleSpinBox()
        self.emitter_exp_spin.setRange(0.0, 2.0)
        self.emitter_exp_spin.setDecimals(2)
        self.emitter_exp_spin.setValue(0.5)
        layout.addWidget(self.emitter_exp_spin, row, 1)
        row += 1
        
        layout.setRowStretch(row, 1)
        return widget
        
    def create_quality_tab(self) -> QWidget:
        """Create quality options tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        row = 0
        
        # Quality Parameter
        layout.addWidget(QLabel("Parameter:"), row, 0)
        self.quality_param_combo = QComboBox()
        self.quality_param_combo.addItems(["None", "Chemical", "Age", "Trace"])
        self.quality_param_combo.currentTextChanged.connect(self.on_quality_param_changed)
        layout.addWidget(self.quality_param_combo, row, 1)
        row += 1
        
        # Chemical Name
        layout.addWidget(QLabel("Chemical Name:"), row, 0)
        self.chemical_name_edit = QLineEdit()
        layout.addWidget(self.chemical_name_edit, row, 1)
        row += 1
        
        # Chemical Units
        layout.addWidget(QLabel("Mass Units:"), row, 0)
        self.chemical_units_edit = QLineEdit()
        self.chemical_units_edit.setText("mg/L")
        layout.addWidget(self.chemical_units_edit, row, 1)
        row += 1
        
        # Diffusivity
        layout.addWidget(QLabel("Relative Diffusivity:"), row, 0)
        self.diffusivity_spin = QDoubleSpinBox()
        self.diffusivity_spin.setRange(0.0, 10.0)
        self.diffusivity_spin.setDecimals(2)
        self.diffusivity_spin.setValue(1.0)
        layout.addWidget(self.diffusivity_spin, row, 1)
        row += 1
        
        # Trace Node
        layout.addWidget(QLabel("Trace Node:"), row, 0)
        self.trace_node_edit = QLineEdit()
        layout.addWidget(self.trace_node_edit, row, 1)
        row += 1
        
        # Quality Tolerance
        layout.addWidget(QLabel("Tolerance:"), row, 0)
        self.quality_tol_spin = QDoubleSpinBox()
        self.quality_tol_spin.setRange(0.0, 1.0)
        self.quality_tol_spin.setDecimals(4)
        self.quality_tol_spin.setValue(0.01)
        layout.addWidget(self.quality_tol_spin, row, 1)
        row += 1
        
        layout.setRowStretch(row, 1)
        return widget
        
    def create_reactions_tab(self) -> QWidget:
        """Create reactions options tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        row = 0
        
        # Bulk Reaction Order
        layout.addWidget(QLabel("Bulk Reaction Order:"), row, 0)
        self.bulk_order_spin = QDoubleSpinBox()
        self.bulk_order_spin.setRange(0.0, 2.0)
        self.bulk_order_spin.setDecimals(1)
        self.bulk_order_spin.setValue(1.0)
        layout.addWidget(self.bulk_order_spin, row, 1)
        row += 1
        
        # Wall Reaction Order
        layout.addWidget(QLabel("Wall Reaction Order:"), row, 0)
        self.wall_order_spin = QDoubleSpinBox()
        self.wall_order_spin.setRange(0.0, 2.0)
        self.wall_order_spin.setDecimals(1)
        self.wall_order_spin.setValue(1.0)
        layout.addWidget(self.wall_order_spin, row, 1)
        row += 1
        
        # Global Bulk Coefficient
        layout.addWidget(QLabel("Global Bulk Coeff.:"), row, 0)
        self.global_bulk_spin = QDoubleSpinBox()
        self.global_bulk_spin.setRange(-10.0, 10.0)
        self.global_bulk_spin.setDecimals(4)
        self.global_bulk_spin.setValue(0.0)
        layout.addWidget(self.global_bulk_spin, row, 1)
        row += 1
        
        # Global Wall Coefficient
        layout.addWidget(QLabel("Global Wall Coeff.:"), row, 0)
        self.global_wall_spin = QDoubleSpinBox()
        self.global_wall_spin.setRange(-10.0, 10.0)
        self.global_wall_spin.setDecimals(4)
        self.global_wall_spin.setValue(0.0)
        layout.addWidget(self.global_wall_spin, row, 1)
        row += 1
        
        # Limiting Concentration
        layout.addWidget(QLabel("Limiting Potential:"), row, 0)
        self.limiting_conc_spin = QDoubleSpinBox()
        self.limiting_conc_spin.setRange(0.0, 1000.0)
        self.limiting_conc_spin.setDecimals(2)
        self.limiting_conc_spin.setValue(0.0)
        layout.addWidget(self.limiting_conc_spin, row, 1)
        row += 1
        
        # Roughness Correlation
        layout.addWidget(QLabel("Roughness Correlation:"), row, 0)
        self.roughness_corr_spin = QDoubleSpinBox()
        self.roughness_corr_spin.setRange(0.0, 10.0)
        self.roughness_corr_spin.setDecimals(2)
        self.roughness_corr_spin.setValue(0.0)
        layout.addWidget(self.roughness_corr_spin, row, 1)
        row += 1
        
        layout.setRowStretch(row, 1)
        return widget
        
    def create_times_tab(self) -> QWidget:
        """Create times options tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        row = 0
        
        # Total Duration
        layout.addWidget(QLabel("Total Duration (hrs):"), row, 0)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.0, 100000.0)
        self.duration_spin.setDecimals(2)
        self.duration_spin.setValue(0.0)
        layout.addWidget(self.duration_spin, row, 1)
        row += 1
        
        # Hydraulic Time Step
        layout.addWidget(QLabel("Hydraulic Time Step (min):"), row, 0)
        self.hyd_timestep_spin = QDoubleSpinBox()
        self.hyd_timestep_spin.setRange(0.01, 1440.0)
        self.hyd_timestep_spin.setDecimals(2)
        self.hyd_timestep_spin.setValue(60.0)
        layout.addWidget(self.hyd_timestep_spin, row, 1)
        row += 1
        
        # Quality Time Step
        layout.addWidget(QLabel("Quality Time Step (min):"), row, 0)
        self.qual_timestep_spin = QDoubleSpinBox()
        self.qual_timestep_spin.setRange(0.01, 1440.0)
        self.qual_timestep_spin.setDecimals(2)
        self.qual_timestep_spin.setValue(5.0)
        layout.addWidget(self.qual_timestep_spin, row, 1)
        row += 1
        
        # Pattern Time Step
        layout.addWidget(QLabel("Pattern Time Step (hrs):"), row, 0)
        self.pattern_timestep_spin = QDoubleSpinBox()
        self.pattern_timestep_spin.setRange(0.01, 24.0)
        self.pattern_timestep_spin.setDecimals(2)
        self.pattern_timestep_spin.setValue(1.0)
        layout.addWidget(self.pattern_timestep_spin, row, 1)
        row += 1
        
        # Pattern Start Time
        layout.addWidget(QLabel("Pattern Start (hrs):"), row, 0)
        self.pattern_start_spin = QDoubleSpinBox()
        self.pattern_start_spin.setRange(0.0, 100000.0)
        self.pattern_start_spin.setDecimals(2)
        self.pattern_start_spin.setValue(0.0)
        layout.addWidget(self.pattern_start_spin, row, 1)
        row += 1
        
        # Report Time Step
        layout.addWidget(QLabel("Report Time Step (hrs):"), row, 0)
        self.report_timestep_spin = QDoubleSpinBox()
        self.report_timestep_spin.setRange(0.01, 1000.0)
        self.report_timestep_spin.setDecimals(2)
        self.report_timestep_spin.setValue(1.0)
        layout.addWidget(self.report_timestep_spin, row, 1)
        row += 1
        
        # Report Start Time
        layout.addWidget(QLabel("Report Start (hrs):"), row, 0)
        self.report_start_spin = QDoubleSpinBox()
        self.report_start_spin.setRange(0.0, 100000.0)
        self.report_start_spin.setDecimals(2)
        self.report_start_spin.setValue(0.0)
        layout.addWidget(self.report_start_spin, row, 1)
        row += 1
        
        # Start Clock Time
        layout.addWidget(QLabel("Start Clock Time:"), row, 0)
        self.clock_time_edit = QLineEdit()
        self.clock_time_edit.setText("12:00 AM")
        layout.addWidget(self.clock_time_edit, row, 1)
        row += 1
        
        # Statistic
        layout.addWidget(QLabel("Statistic:"), row, 0)
        self.statistic_combo = QComboBox()
        self.statistic_combo.addItems(["None", "Average", "Minimum", "Maximum", "Range"])
        layout.addWidget(self.statistic_combo, row, 1)
        row += 1
        
        layout.setRowStretch(row, 1)
        return widget
        
    def create_energy_tab(self) -> QWidget:
        """Create energy options tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        row = 0
        
        # Global Efficiency
        layout.addWidget(QLabel("Global Efficiency (%):"), row, 0)
        self.efficiency_spin = QDoubleSpinBox()
        self.efficiency_spin.setRange(0.0, 100.0)
        self.efficiency_spin.setDecimals(1)
        self.efficiency_spin.setValue(75.0)
        layout.addWidget(self.efficiency_spin, row, 1)
        row += 1
        
        # Global Price
        layout.addWidget(QLabel("Global Price (per kW-hr):"), row, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.0, 1000.0)
        self.price_spin.setDecimals(4)
        self.price_spin.setValue(0.0)
        layout.addWidget(self.price_spin, row, 1)
        row += 1
        
        # Demand Charge
        layout.addWidget(QLabel("Demand Charge (per max kW):"), row, 0)
        self.demand_charge_spin = QDoubleSpinBox()
        self.demand_charge_spin.setRange(0.0, 1000.0)
        self.demand_charge_spin.setDecimals(2)
        self.demand_charge_spin.setValue(0.0)
        layout.addWidget(self.demand_charge_spin, row, 1)
        row += 1
        
        layout.setRowStretch(row, 1)
        return widget
        
    def on_quality_param_changed(self, param: str):
        """Handle quality parameter change."""
        # Enable/disable fields based on parameter
        is_chemical = param == "Chemical"
        is_trace = param == "Trace"
        
        self.chemical_name_edit.setEnabled(is_chemical)
        self.chemical_units_edit.setEnabled(is_chemical)
        self.diffusivity_spin.setEnabled(is_chemical)
        self.trace_node_edit.setEnabled(is_trace)
        
    def load_data(self, options: Dict[str, Any]):
        """Load options data into the dialog."""
        self.options_data = options.copy()
        
        # Hydraulics tab
        flow_units_map = {
            "CFS": 0, "GPM": 1, "MGD": 2, "IMGD": 3, "AFD": 4,
            "LPS": 5, "LPM": 6, "MLD": 7, "CMH": 8, "CMD": 9
        }
        self.flow_units_combo.setCurrentIndex(flow_units_map.get(options.get("flow_units", "GPM"), 1))
        
        headloss_map = {"HW": 0, "DW": 1, "CM": 2}
        self.headloss_combo.setCurrentIndex(headloss_map.get(options.get("headloss_formula", "HW"), 0))
        
        self.specific_gravity_spin.setValue(options.get("specific_gravity", 1.0))
        self.viscosity_spin.setValue(options.get("viscosity", 1.0))
        self.trials_spin.setValue(options.get("trials", 40))
        self.accuracy_spin.setValue(options.get("accuracy", 0.001))
        
        unbalanced = options.get("unbalanced", "STOP")
        self.unbalanced_combo.setCurrentIndex(0 if unbalanced == "STOP" else 1)
        
        self.demand_mult_spin.setValue(options.get("demand_multiplier", 1.0))
        self.emitter_exp_spin.setValue(options.get("emitter_exponent", 0.5))
        
        # Quality tab
        quality_map = {"NONE": 0, "CHEMICAL": 1, "AGE": 2, "TRACE": 3}
        self.quality_param_combo.setCurrentIndex(quality_map.get(options.get("quality_type", "NONE"), 0))
        
        self.chemical_name_edit.setText(options.get("chemical_name", ""))
        self.chemical_units_edit.setText(options.get("chemical_units", "mg/L"))
        self.diffusivity_spin.setValue(options.get("diffusivity", 1.0))
        self.trace_node_edit.setText(options.get("trace_node", "") or "")
        self.quality_tol_spin.setValue(options.get("quality_tolerance", 0.01))
        
        # Reactions tab
        self.bulk_order_spin.setValue(options.get("bulk_order", 1.0))
        self.wall_order_spin.setValue(options.get("wall_order", 1.0))
        self.global_bulk_spin.setValue(options.get("global_bulk_coeff", 0.0))
        self.global_wall_spin.setValue(options.get("global_wall_coeff", 0.0))
        self.limiting_conc_spin.setValue(options.get("limiting_concentration", 0.0))
        self.roughness_corr_spin.setValue(options.get("roughness_correlation", 0.0))
        
        # Times tab (convert seconds to hours/minutes)
        self.duration_spin.setValue(options.get("duration", 0) / 3600.0)
        self.hyd_timestep_spin.setValue(options.get("hydraulic_timestep", 3600) / 60.0)
        self.qual_timestep_spin.setValue(options.get("quality_timestep", 300) / 60.0)
        self.pattern_timestep_spin.setValue(options.get("pattern_timestep", 3600) / 3600.0)
        self.pattern_start_spin.setValue(options.get("pattern_start", 0) / 3600.0)
        self.report_timestep_spin.setValue(options.get("report_timestep", 3600) / 3600.0)
        self.report_start_spin.setValue(options.get("report_start", 0) / 3600.0)
        
        statistic_map = {"NONE": 0, "AVERAGE": 1, "MINIMUM": 2, "MAXIMUM": 3, "RANGE": 4}
        self.statistic_combo.setCurrentIndex(statistic_map.get(options.get("statistic", "NONE"), 0))
        
        # Energy tab
        self.efficiency_spin.setValue(options.get("global_efficiency", 75.0))
        self.price_spin.setValue(options.get("global_price", 0.0))
        self.demand_charge_spin.setValue(options.get("demand_charge", 0.0))
        
        # Trigger quality parameter change to update field states
        self.on_quality_param_changed(self.quality_param_combo.currentText())
        
    def unload_data(self) -> Dict[str, Any]:
        """Get the current options data."""
        options = {}
        
        # Hydraulics
        flow_units_list = ["CFS", "GPM", "MGD", "IMGD", "AFD", "LPS", "LPM", "MLD", "CMH", "CMD"]
        options["flow_units"] = flow_units_list[self.flow_units_combo.currentIndex()]
        
        headloss_list = ["HW", "DW", "CM"]
        options["headloss_formula"] = headloss_list[self.headloss_combo.currentIndex()]
        
        options["specific_gravity"] = self.specific_gravity_spin.value()
        options["viscosity"] = self.viscosity_spin.value()
        options["trials"] = self.trials_spin.value()
        options["accuracy"] = self.accuracy_spin.value()
        options["unbalanced"] = "STOP" if self.unbalanced_combo.currentIndex() == 0 else "CONTINUE"
        options["demand_multiplier"] = self.demand_mult_spin.value()
        options["emitter_exponent"] = self.emitter_exp_spin.value()
        
        # Quality
        quality_list = ["NONE", "CHEMICAL", "AGE", "TRACE"]
        options["quality_type"] = quality_list[self.quality_param_combo.currentIndex()]
        options["chemical_name"] = self.chemical_name_edit.text()
        options["chemical_units"] = self.chemical_units_edit.text()
        options["diffusivity"] = self.diffusivity_spin.value()
        options["trace_node"] = self.trace_node_edit.text() or None
        options["quality_tolerance"] = self.quality_tol_spin.value()
        
        # Reactions
        options["bulk_order"] = self.bulk_order_spin.value()
        options["wall_order"] = self.wall_order_spin.value()
        options["global_bulk_coeff"] = self.global_bulk_spin.value()
        options["global_wall_coeff"] = self.global_wall_spin.value()
        options["limiting_concentration"] = self.limiting_conc_spin.value()
        options["roughness_correlation"] = self.roughness_corr_spin.value()
        
        # Times (convert hours/minutes to seconds)
        options["duration"] = int(self.duration_spin.value() * 3600)
        options["hydraulic_timestep"] = int(self.hyd_timestep_spin.value() * 60)
        options["quality_timestep"] = int(self.qual_timestep_spin.value() * 60)
        options["pattern_timestep"] = int(self.pattern_timestep_spin.value() * 3600)
        options["pattern_start"] = int(self.pattern_start_spin.value() * 3600)
        options["report_timestep"] = int(self.report_timestep_spin.value() * 3600)
        options["report_start"] = int(self.report_start_spin.value() * 3600)
        
        statistic_list = ["NONE", "AVERAGE", "MINIMUM", "MAXIMUM", "RANGE"]
        options["statistic"] = statistic_list[self.statistic_combo.currentIndex()]
        
        # Energy
        options["global_efficiency"] = self.efficiency_spin.value()
        options["global_price"] = self.price_spin.value()
        options["demand_charge"] = self.demand_charge_spin.value()
        
        return options
        
    def accept_changes(self):
        """Accept and validate changes."""
        options = self.unload_data()
        
        # Basic validation
        if options["trials"] < 1:
            QMessageBox.warning(self, "Invalid Value", "Maximum Trials must be at least 1.")
            return
            
        if options["accuracy"] <= 0:
            QMessageBox.warning(self, "Invalid Value", "Accuracy must be positive.")
            return
            
        if options["duration"] < 0:
            QMessageBox.warning(self, "Invalid Value", "Duration cannot be negative.")
            return
        
        # Emit signal with updated options
        self.options_updated.emit(options)
        self.accept()
        
    def show_help(self):
        """Show help information."""
        QMessageBox.information(
            self,
            "Analysis Options Help",
            "Analysis Options allows you to configure simulation parameters.\n\n"
            "**Hydraulics**: Flow units, headloss formula, solver parameters\n"
            "**Quality**: Water quality analysis settings\n"
            "**Reactions**: Chemical reaction coefficients\n"
            "**Times**: Simulation duration and time steps\n"
            "**Energy**: Pump energy cost parameters"
        )
