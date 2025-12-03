"""Project Defaults dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QCheckBox, QHeaderView, QWidget,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QDoubleValidator, QIntValidator


class DefaultsDialog(QDialog):
    """Dialog for setting project defaults."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Defaults")
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_defaults()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: ID Prefixes
        self.id_tab = self.create_id_prefixes_tab()
        self.tab_widget.addTab(self.id_tab, "ID Prefixes")
        
        # Tab 2: Node/Link Defaults
        self.nodelink_tab = self.create_nodelink_tab()
        self.tab_widget.addTab(self.nodelink_tab, "Node/Link")
        
        # Tab 3: Hydraulic Options
        self.hydraulics_tab = self.create_hydraulics_tab()
        self.tab_widget.addTab(self.hydraulics_tab, "Hydraulics")
        
        layout.addWidget(self.tab_widget)
        
        # Checkbox to save as default
        self.save_default_check = QCheckBox("Use as default for all new projects")
        layout.addWidget(self.save_default_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def create_id_prefixes_tab(self):
        """Create ID Prefixes tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Default ID Prefixes for New Objects:"))
        
        self.id_table = QTableWidget()
        self.id_table.setColumnCount(2)
        self.id_table.setHorizontalHeaderLabels(["Object Type", "ID Prefix"])
        self.id_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.id_table.verticalHeader().setVisible(False)
        
        # Add rows for each object type
        object_types = [
            "Junctions",
            "Reservoirs", 
            "Tanks",
            "Pipes",
            "Pumps",
            "Valves",
            "Patterns",
            "Curves",
            "ID Increment"
        ]
        
        self.id_table.setRowCount(len(object_types))
        
        for i, obj_type in enumerate(object_types):
            # Object type (read-only)
            type_item = QTableWidgetItem(obj_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.id_table.setItem(i, 0, type_item)
            
            # Prefix (editable)
            prefix_item = QTableWidgetItem("")
            self.id_table.setItem(i, 1, prefix_item)
        
        layout.addWidget(self.id_table)
        
        return widget
        
    def create_nodelink_tab(self):
        """Create Node/Link defaults tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Default Property Values:"))
        
        self.nodelink_table = QTableWidget()
        self.nodelink_table.setColumnCount(2)
        self.nodelink_table.setHorizontalHeaderLabels(["Property", "Default Value"])
        self.nodelink_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.nodelink_table.verticalHeader().setVisible(False)
        
        # Add rows for properties
        properties = [
            ("Node Elevation", "m"),
            ("Tank Diameter", "m"),
            ("Tank Height", "m"),
            ("Pipe Length", "m"),
            ("Auto Length", ""),
            ("Pipe Diameter", "mm"),
            ("Pipe Roughness", "")
        ]
        
        self.nodelink_table.setRowCount(len(properties))
        
        for i, (prop_name, unit) in enumerate(properties):
            # Property name (read-only)
            name_item = QTableWidgetItem(f"{prop_name} ({unit})" if unit else prop_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.nodelink_table.setItem(i, 0, name_item)
            
            if prop_name == "Auto Length":
                from PySide6.QtWidgets import QComboBox
                combo = QComboBox()
                combo.addItems(["Off", "On"])
                self.nodelink_table.setCellWidget(i, 1, combo)
            else:
                # Default value (editable)
                value_item = QTableWidgetItem("")
                self.nodelink_table.setItem(i, 1, value_item)
        
        layout.addWidget(self.nodelink_table)
        
        return widget
        
    def create_hydraulics_tab(self):
        """Create Hydraulics options tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Default Hydraulic Options:"))
        
        self.hydraulics_table = QTableWidget()
        self.hydraulics_table.setColumnCount(2)
        self.hydraulics_table.setHorizontalHeaderLabels(["Option", "Default Value"])
        self.hydraulics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hydraulics_table.verticalHeader().setVisible(False)
        
        # Add rows for hydraulic options
        options = [
            "Flow Units",
            "Headloss Formula",
            "Specific Gravity",
            "Viscosity",
            "Maximum Trials",
            "Accuracy",
            "Unbalanced",
            "Pattern",
            "Demand Multiplier",
            "Emitter Exponent",
            "Status Report"
        ]
        
        self.hydraulics_table.setRowCount(len(options))
        
        from PySide6.QtWidgets import QComboBox
        
        for i, option in enumerate(options):
            # Option name (read-only)
            name_item = QTableWidgetItem(option)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.hydraulics_table.setItem(i, 0, name_item)
            
            # Setup widgets for specific rows
            if option == "Flow Units":
                combo = QComboBox()
                combo.addItems(["CFS", "GPM", "MGD", "IMGD", "AFD", "LPS", "LPM", "MLD", "CMH", "CMD"])
                self.hydraulics_table.setCellWidget(i, 1, combo)
            elif option == "Headloss Formula":
                combo = QComboBox()
                combo.addItems(["H-W", "D-W", "C-M"])
                self.hydraulics_table.setCellWidget(i, 1, combo)
            elif option == "Unbalanced":
                combo = QComboBox()
                combo.addItems(["STOP", "CONTINUE", "CONTINUE 10"])
                self.hydraulics_table.setCellWidget(i, 1, combo)
            elif option == "Status Report":
                combo = QComboBox()
                combo.addItems(["No", "Yes"])
                self.hydraulics_table.setCellWidget(i, 1, combo)
            else:
                # Default value (editable)
                value_item = QTableWidgetItem("")
                self.hydraulics_table.setItem(i, 1, value_item)
        
        layout.addWidget(self.hydraulics_table)
        
        return widget
        
    def load_defaults(self):
        """Load current default values."""
        # Load ID Prefixes
        prefixes = getattr(self.project, 'default_prefixes', {
            'Junction': 'J',
            'Reservoir': 'R',
            'Tank': 'T',
            'Pipe': 'P',
            'Pump': 'PU',
            'Valve': 'V',
            'Pattern': 'PAT',
            'Curve': 'C'
        })
        
        id_increment = getattr(self.project, 'id_increment', 1)
        
        self.id_table.item(0, 1).setText(prefixes.get('Junction', 'J'))
        self.id_table.item(1, 1).setText(prefixes.get('Reservoir', 'R'))
        self.id_table.item(2, 1).setText(prefixes.get('Tank', 'T'))
        self.id_table.item(3, 1).setText(prefixes.get('Pipe', 'P'))
        self.id_table.item(4, 1).setText(prefixes.get('Pump', 'PU'))
        self.id_table.item(5, 1).setText(prefixes.get('Valve', 'V'))
        self.id_table.item(6, 1).setText(prefixes.get('Pattern', 'PAT'))
        self.id_table.item(7, 1).setText(prefixes.get('Curve', 'C'))
        self.id_table.item(8, 1).setText(str(id_increment))
        
        # Load Node/Link defaults
        defaults = getattr(self.project, 'default_properties', {
            'node_elevation': '0',
            'tank_diameter': '15',
            'tank_height': '3',
            'pipe_length': '100',
            'auto_length': 'Off',
            'pipe_diameter': '300',
            'pipe_roughness': '100'
        })
        
        self.nodelink_table.item(0, 1).setText(defaults.get('node_elevation', '0'))
        self.nodelink_table.item(1, 1).setText(defaults.get('tank_diameter', '15'))
        self.nodelink_table.item(2, 1).setText(defaults.get('tank_height', '3'))
        self.nodelink_table.item(3, 1).setText(defaults.get('pipe_length', '100'))
        
        # Auto Length ComboBox
        auto_len = defaults.get('auto_length', 'Off')
        combo = self.nodelink_table.cellWidget(4, 1)
        if combo:
            combo.setCurrentText(auto_len)
            
        self.nodelink_table.item(5, 1).setText(defaults.get('pipe_diameter', '300'))
        self.nodelink_table.item(6, 1).setText(defaults.get('pipe_roughness', '100'))
        
        # Load Hydraulic options from project defaults
        hydraulics = getattr(self.project, 'default_hydraulics', {})
        
        # Helper to set combo or text
        def set_val(row, val):
            combo = self.hydraulics_table.cellWidget(row, 1)
            if combo:
                combo.setCurrentText(str(val))
            else:
                self.hydraulics_table.item(row, 1).setText(str(val))
                
        set_val(0, hydraulics.get('flow_units', 'LPS'))
        set_val(1, hydraulics.get('headloss_formula', 'H-W'))
        set_val(2, hydraulics.get('specific_gravity', 1.0))
        set_val(3, hydraulics.get('viscosity', 1.0))
        set_val(4, hydraulics.get('trials', 40))
        set_val(5, hydraulics.get('accuracy', 0.001))
        set_val(6, hydraulics.get('unbalanced', 'STOP'))
        set_val(7, hydraulics.get('pattern', ''))
        set_val(8, hydraulics.get('demand_multiplier', 1.0))
        set_val(9, hydraulics.get('emitter_exponent', 0.5))
        set_val(10, "Yes" if hydraulics.get('status_report', False) else "No")
        
    def accept(self):
        """Save defaults and close dialog."""
        # Validate and save ID prefixes
        prefixes = {
            'Junction': self.id_table.item(0, 1).text(),
            'Reservoir': self.id_table.item(1, 1).text(),
            'Tank': self.id_table.item(2, 1).text(),
            'Pipe': self.id_table.item(3, 1).text(),
            'Pump': self.id_table.item(4, 1).text(),
            'Valve': self.id_table.item(5, 1).text(),
            'Pattern': self.id_table.item(6, 1).text(),
            'Curve': self.id_table.item(7, 1).text()
        }
        
        try:
            id_increment = int(self.id_table.item(8, 1).text())
            if id_increment <= 0:
                raise ValueError("ID Increment must be positive")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"ID Increment: {str(e)}")
            return
        
        self.project.default_prefixes = prefixes
        self.project.id_increment = id_increment
        
        # Save Node/Link defaults
        auto_len_combo = self.nodelink_table.cellWidget(4, 1)
        auto_len = auto_len_combo.currentText() if auto_len_combo else "Off"
        
        defaults = {
            'node_elevation': self.nodelink_table.item(0, 1).text(),
            'tank_diameter': self.nodelink_table.item(1, 1).text(),
            'tank_height': self.nodelink_table.item(2, 1).text(),
            'pipe_length': self.nodelink_table.item(3, 1).text(),
            'auto_length': auto_len,
            'pipe_diameter': self.nodelink_table.item(5, 1).text(),
            'pipe_roughness': self.nodelink_table.item(6, 1).text()
        }
        
        self.project.default_properties = defaults
        
        # Save Hydraulic defaults
        def get_val(row):
            combo = self.hydraulics_table.cellWidget(row, 1)
            if combo:
                return combo.currentText()
            return self.hydraulics_table.item(row, 1).text()
            
        hydraulics = {
            'flow_units': get_val(0),
            'headloss_formula': get_val(1),
            'specific_gravity': get_val(2),
            'viscosity': get_val(3),
            'trials': get_val(4),
            'accuracy': get_val(5),
            'unbalanced': get_val(6),
            'pattern': get_val(7),
            'demand_multiplier': get_val(8),
            'emitter_exponent': get_val(9),
            'status_report': get_val(10) == "Yes"
        }
        
        self.project.default_hydraulics = hydraulics
        
        # Save to config if checkbox is checked
        if self.save_default_check.isChecked():
            self.save_to_config()
        
        super().accept()
        
    def save_to_config(self):
        """Save defaults to configuration file."""
        settings = QSettings("US EPA", "EPANET 2.2")
        
        # Save ID Prefixes
        settings.beginGroup("Defaults/IDPrefixes")
        for key, value in self.project.default_prefixes.items():
            settings.setValue(key, value)
        settings.endGroup()
        
        settings.setValue("Defaults/IDIncrement", self.project.id_increment)
        
        # Save Properties
        settings.beginGroup("Defaults/Properties")
        for key, value in self.project.default_properties.items():
            settings.setValue(key, value)
        settings.endGroup()
        
        # Save Hydraulics
        settings.beginGroup("Defaults/Hydraulics")
        for key, value in self.project.default_hydraulics.items():
            settings.setValue(key, value)
        settings.endGroup()
