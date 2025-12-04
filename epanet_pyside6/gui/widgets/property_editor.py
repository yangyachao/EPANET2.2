"""Property editor widget."""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QWidget, QHBoxLayout, QLineEdit, QToolButton
from PySide6.QtCore import Qt, Signal
from core.project import EPANETProject
from core.units import get_unit_label
from gui.dialogs.demand_editor import DemandEditorDialog
from gui.dialogs.source_editor import SourceEditorDialog
from gui.dialogs.curve_editor import CurveEditor
from gui.dialogs.pattern_editor import PatternEditor


class PropertyEditor(QTableWidget):
    """Table widget for editing object properties."""
    # Emits the object (model instance) after it has been updated
    objectUpdated = Signal(object)
    
    def __init__(self, project: EPANETProject, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_object = None
        
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Property", "Value"])
        self.horizontalHeader().setStretchLastSection(True)
        
        # Signals
        self.itemChanged.connect(self.on_item_changed)
    
    def clear(self):
        """Clear the property editor."""
        self.setRowCount(0)
        self.current_object = None
    
    def set_object(self, obj):
        """Set the object to edit."""
        self.current_object = obj
        self.populate_properties()
    
    def populate_properties(self):
        """Populate properties for current object."""
        self.setRowCount(0)
        
        if not self.current_object:
            return
        
        # Block signals while populating
        self.blockSignals(True)
        
        # Get flow units for unit labels
        self.flow_units = self.project.network.options.flow_units
        
        # Common properties for Nodes and Links
        if hasattr(self.current_object, 'comment'):
            self.add_property("Description", self.current_object.comment)
        if hasattr(self.current_object, 'tag'):
            self.add_property("Tag", self.current_object.tag)
            
        # Dispatch to specific handler
        from models import Junction, Reservoir, Tank, Pipe, Pump, Valve, Label
        
        handlers = {
            Junction: self._add_junction_properties,
            Reservoir: self._add_reservoir_properties,
            Tank: self._add_tank_properties,
            Pipe: self._add_pipe_properties,
            Pump: self._add_pump_properties,
            Valve: self._add_valve_properties,
            Label: self._add_label_properties
        }
        
        handler = handlers.get(type(self.current_object))
        if handler:
            handler()
        
        # Re-enable signals
        self.blockSignals(False)

    def u(self, param_type):
        """Helper for unit labels."""
        return f" ({get_unit_label(param_type, self.flow_units)})"

    def _add_junction_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property(f"X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
        self.add_property(f"Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
        self.add_property(f"Elevation{self.u('elevation')}", f"{(self.current_object.elevation or 0.0):.2f}")
        self.add_property(f"Base Demand{self.u('flow')}", f"{(self.current_object.base_demand or 0.0):.2f}")
        self.add_editable_action_property("Demand Pattern", self.current_object.demand_pattern or "", "...", lambda: self.edit_pattern("Demand Pattern"))
        self.add_action_property("Demands", "...", self.edit_demands)
        self.add_property("Emitter Coeff.", f"{(self.current_object.emitter_coeff or 0.0):.2f}")
        self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
        self.add_action_property("Source Quality", "...", self.edit_source_quality)
        
        if self.project.has_results():
            self.add_property(f"Demand (Result){self.u('flow')}", f"{(self.current_object.demand or 0.0):.2f}", editable=False)
            self.add_property(f"Head (Result){self.u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
            self.add_property(f"Pressure (Result){self.u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
            self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)

    def _add_reservoir_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
        self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
        self.add_property(f"Total Head{self.u('head')}", f"{(self.current_object.total_head or 0.0):.2f}")
        self.add_editable_action_property("Head Pattern", self.current_object.head_pattern or "", "...", lambda: self.edit_pattern("Head Pattern"))
        self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
        self.add_action_property("Source Quality", "...", self.edit_source_quality)
        
        if self.project.has_results():
            self.add_property(f"Head (Result){self.u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
            self.add_property(f"Pressure (Result){self.u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
            self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)

    def _add_tank_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
        self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
        self.add_property(f"Elevation{self.u('elevation')}", f"{(self.current_object.elevation or 0.0):.2f}")
        self.add_property(f"Initial Level{self.u('length')}", f"{(self.current_object.init_level or 0.0):.2f}")
        self.add_property(f"Min Level{self.u('length')}", f"{(self.current_object.min_level or 0.0):.2f}")
        self.add_property(f"Max Level{self.u('length')}", f"{(self.current_object.max_level or 0.0):.2f}")
        self.add_property(f"Diameter{self.u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
        self.add_property(f"Min Volume{self.u('volume')}", f"{(self.current_object.min_volume or 0.0):.2f}")
        self.add_editable_action_property("Volume Curve", self.current_object.volume_curve or "", "...", lambda: self.edit_curve("Volume Curve"))
        self.add_property("Mixing Model", str(self.current_object.mixing_model.name))
        self.add_property("Mixing Fraction", f"{(self.current_object.mixing_fraction or 0.0):.2f}")
        self.add_property("Reaction Coeff.", f"{(self.current_object.bulk_coeff or 0.0):.2f}")
        self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
        self.add_action_property("Source Quality", "...", self.edit_source_quality)
        
        if self.project.has_results():
            self.add_property(f"Head (Result){self.u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
            self.add_property(f"Pressure (Result){self.u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
            self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)

    def _add_pipe_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property("From Node", self.current_object.from_node)
        self.add_property("To Node", self.current_object.to_node)
        self.add_property(f"Length{self.u('length')}", f"{(self.current_object.length or 0.0):.2f}")
        self.add_property(f"Diameter{self.u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
        self.add_property("Roughness", f"{(self.current_object.roughness or 0.0):.2f}")
        self.add_property("Loss Coeff.", f"{(self.current_object.minor_loss or 0.0):.2f}")
        self.add_property("Initial Status", str(self.current_object.status.name))
        self.add_property("Bulk Coeff.", f"{(self.current_object.bulk_coeff or 0.0):.2f}")
        self.add_property("Wall Coeff.", f"{(self.current_object.wall_coeff or 0.0):.2f}")
        self.add_property("Check Valve", "Yes" if self.current_object.has_check_valve else "No")
        
        if self.project.has_results():
            self.add_property(f"Flow (Result){self.u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
            self.add_property(f"Velocity (Result){self.u('velocity')}", f"{(self.current_object.velocity or 0.0):.2f}", editable=False)
            self.add_property(f"Headloss (Result){self.u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)

    def _add_pump_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property("From Node", self.current_object.from_node)
        self.add_property("To Node", self.current_object.to_node)
        self.add_editable_action_property("Pump Curve", self.current_object.pump_curve or "", "...", lambda: self.edit_curve("Pump Curve"))
        self.add_property("Power", f"{(self.current_object.power or 0.0):.2f}")
        self.add_property("Speed", f"{(self.current_object.speed or 0.0):.2f}")
        self.add_editable_action_property("Pattern", self.current_object.speed_pattern or "", "...", lambda: self.edit_pattern("Pattern"))
        self.add_property("Initial Status", str(self.current_object.status.name))
        self.add_editable_action_property("Efficiency Curve", self.current_object.efficiency_curve or "", "...", lambda: self.edit_curve("Efficiency Curve"))
        self.add_property("Energy Price", f"{(self.current_object.energy_price or 0.0):.4f}")
        self.add_editable_action_property("Price Pattern", self.current_object.price_pattern or "", "...", lambda: self.edit_pattern("Price Pattern"))
        
        if self.project.has_results():
            self.add_property(f"Flow (Result){self.u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
            self.add_property(f"Headloss (Result){self.u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)

    def _add_valve_properties(self):
        self.add_property("ID", self.current_object.id, editable=False)
        self.add_property("Type", str(self.current_object.link_type.name), editable=False)
        self.add_property("From Node", self.current_object.from_node)
        self.add_property("To Node", self.current_object.to_node)
        self.add_property(f"Diameter{self.u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
        self.add_property("Setting", f"{(self.current_object.valve_setting or 0.0):.2f}")
        self.add_property("Loss Coeff.", f"{(self.current_object.minor_loss or 0.0):.2f}")
        self.add_property("Fixed Status", str(self.current_object.fixed_status.name) if hasattr(self.current_object, 'fixed_status') else "OPEN")
        
        if self.project.has_results():
            self.add_property(f"Flow (Result){self.u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
            self.add_property(f"Velocity (Result){self.u('velocity')}", f"{(self.current_object.velocity or 0.0):.2f}", editable=False)
            self.add_property(f"Headloss (Result){self.u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)

    def _add_label_properties(self):
        self.add_property("Text", self.current_object.text)
        self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
        self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
        self.add_property("Font Size", str(self.current_object.font_size))
        self.add_property("Font Bold", "Yes" if self.current_object.font_bold else "No")
        self.add_property("Font Italic", "Yes" if self.current_object.font_italic else "No")
    
    def add_property(self, name: str, value: str, editable: bool = True):
        """Add a property row."""
        row = self.rowCount()
        self.insertRow(row)
        
        # Property name (not editable)
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.setItem(row, 0, name_item)
        
        # Property value
        value_item = QTableWidgetItem(value)
        if not editable:
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            value_item.setBackground(Qt.lightGray)
        self.setItem(row, 1, value_item)

    def add_action_property(self, name: str, button_text: str, callback):
        """Add a property with a button action."""
        row = self.rowCount()
        self.insertRow(row)
        
        # Property name
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.setItem(row, 0, name_item)
        
        # Button
        button = QPushButton(button_text)
        button.clicked.connect(callback)
        self.setCellWidget(row, 1, button)

    def add_editable_action_property(self, name: str, value: str, button_text: str, callback):
        """Add a property with an editable line edit and a button action."""
        row = self.rowCount()
        self.insertRow(row)
        
        # Property name
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.setItem(row, 0, name_item)
        
        # Container widget
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Line Edit
        line_edit = QLineEdit(value)
        # Handle text changes manually since itemChanged won't fire
        line_edit.editingFinished.connect(lambda: self.on_custom_widget_changed(row, line_edit.text()))
        layout.addWidget(line_edit)
        
        # Button
        button = QToolButton()
        button.setText(button_text)
        button.clicked.connect(callback)
        layout.addWidget(button)
        
        self.setCellWidget(row, 1, widget)
        
    def on_custom_widget_changed(self, row, value):
        """Handle changes from custom widgets."""
        if not self.current_object:
            return
            
        property_name = self.item(row, 0).text()
        # Create a dummy item to reuse on_item_changed logic
        # But on_item_changed expects item.column() == 1
        # And it gets value from item.text()
        # So we can't easily reuse it without refactoring.
        # Let's just call the update logic directly or refactor.
        
        # Refactoring on_item_changed to update_property(name, value) is better.
        self.update_property(property_name, value)
    
    def on_item_changed(self, item):
        """Handle property value change."""
        if not self.current_object or item.column() != 1:
            return
        
        property_name = self.item(item.row(), 0).text()
        new_value = item.text()
        
        self.update_property(property_name, new_value)
        
    def update_property(self, property_name, new_value):
        """Update object property."""
        # Remove unit label from property name for matching
        # Assuming format "Name (Unit)"
        clean_name = property_name.split(' (')[0]
        
        # Update object property
        try:
            from models import Junction, Reservoir, Tank, Pipe, Pump, Valve, Label
            
            # Common properties
            if clean_name == "Description":
                self.current_object.comment = new_value
            elif clean_name == "Tag":
                self.current_object.tag = new_value
            
            handlers = {
                Junction: self._update_junction_property,
                Reservoir: self._update_reservoir_property,
                Tank: self._update_tank_property,
                Pipe: self._update_pipe_property,
                Pump: self._update_pump_property,
                Valve: self._update_valve_property,
                Label: self._update_label_property
            }
            
            handler = handlers.get(type(self.current_object))
            if handler:
                handler(clean_name, new_value)
            
            # Mark project as modified
            self.project.modified = True
            # Emit update signal so map/browser can refresh
            try:
                self.objectUpdated.emit(self.current_object)
            except Exception:
                pass
        except ValueError:
            # Invalid input, maybe revert or show error
            pass

    def _update_junction_property(self, name, value):
        if name == "X Coordinate":
            self.current_object.x = float(value)
        elif name == "Y Coordinate":
            self.current_object.y = float(value)
        elif name == "Elevation":
            self.current_object.elevation = float(value)
        elif name == "Base Demand":
            self.current_object.base_demand = float(value)
        elif name == "Demand Pattern":
            self.current_object.demand_pattern = value
        elif name == "Emitter Coeff.":
            self.current_object.emitter_coeff = float(value)
        elif name == "Initial Quality":
            self.current_object.init_quality = float(value)

    def _update_reservoir_property(self, name, value):
        if name == "X Coordinate":
            self.current_object.x = float(value)
        elif name == "Y Coordinate":
            self.current_object.y = float(value)
        elif name == "Total Head":
            self.current_object.total_head = float(value)
        elif name == "Head Pattern":
            self.current_object.head_pattern = value
        elif name == "Initial Quality":
            self.current_object.init_quality = float(value)

    def _update_tank_property(self, name, value):
        if name == "X Coordinate":
            self.current_object.x = float(value)
        elif name == "Y Coordinate":
            self.current_object.y = float(value)
        elif name == "Elevation":
            self.current_object.elevation = float(value)
        elif name == "Initial Level":
            self.current_object.init_level = float(value)
        elif name == "Min Level":
            self.current_object.min_level = float(value)
        elif name == "Max Level":
            self.current_object.max_level = float(value)
        elif name == "Diameter":
            self.current_object.diameter = float(value)
        elif name == "Min Volume":
            self.current_object.min_volume = float(value)
        elif name == "Volume Curve":
            self.current_object.volume_curve = value
        elif name == "Mixing Fraction":
            self.current_object.mixing_fraction = float(value)
        elif name == "Reaction Coeff.":
            self.current_object.bulk_coeff = float(value)
        elif name == "Initial Quality":
            self.current_object.init_quality = float(value)

    def _update_pipe_property(self, name, value):
        if name == "Length":
            self.current_object.length = float(value)
        elif name == "Diameter":
            self.current_object.diameter = float(value)
        elif name == "Roughness":
            self.current_object.roughness = float(value)
        elif name == "Loss Coeff.":
            self.current_object.minor_loss = float(value)
        elif name == "Bulk Coeff.":
            self.current_object.bulk_coeff = float(value)
        elif name == "Wall Coeff.":
            self.current_object.wall_coeff = float(value)
        elif name == "Check Valve":
            self.current_object.has_check_valve = (value.lower() in ['yes', 'true', '1'])

    def _update_pump_property(self, name, value):
        if name == "Power":
            self.current_object.power = float(value)
        elif name == "Speed":
            self.current_object.speed = float(value)
        elif name == "Pump Curve":
            self.current_object.pump_curve = value
        elif name == "Pattern":
            self.current_object.speed_pattern = value
        elif name == "Efficiency Curve":
            self.current_object.efficiency_curve = value
        elif name == "Energy Price":
            self.current_object.energy_price = float(value)
        elif name == "Price Pattern":
            self.current_object.price_pattern = value

    def _update_valve_property(self, name, value):
        if name == "Diameter":
            self.current_object.diameter = float(value)
        elif name == "Setting":
            self.current_object.valve_setting = float(value)
        elif name == "Loss Coeff.":
            self.current_object.minor_loss = float(value)

    def _update_label_property(self, name, value):
        if name == "Text":
            self.current_object.text = value
        elif name == "X Coordinate":
            self.current_object.x = float(value)
        elif name == "Y Coordinate":
            self.current_object.y = float(value)
        elif name == "Font Size":
            self.current_object.font_size = int(value)
        elif name == "Font Bold":
            self.current_object.font_bold = (value.lower() in ['yes', 'true', '1'])
        elif name == "Font Italic":
            self.current_object.font_italic = (value.lower() in ['yes', 'true', '1'])
    
    def edit_demands(self):
        """Open demand editor."""
        if not self.current_object: 
            return
        
        dialog = DemandEditorDialog(self.current_object, self)
        if dialog.exec():
            # Update demands
            demands = dialog.get_data()
            if demands:
                # First demand is primary
                self.current_object.base_demand = demands[0]['base_demand']
                self.current_object.demand_pattern = demands[0]['pattern']
                
                # Rest are secondary
                self.current_object.demands = demands[1:]
            else:
                self.current_object.base_demand = 0.0
                self.current_object.demand_pattern = ""
                self.current_object.demands = []
                
            self.project.modified = True
            self.populate_properties()
            
    def edit_source_quality(self):
        """Open source quality editor."""
        if not self.current_object: 
            return
        
        dialog = SourceEditorDialog(self.current_object, self)
        if dialog.exec():
            data = dialog.get_data()
            self.current_object.source_type = data['source_type']
            self.current_object.source_quality = data['source_quality']
            self.current_object.source_pattern = data['source_pattern']
            
            self.project.modified = True
            self.populate_properties()

    def edit_curve(self, property_name):
        """Open curve editor."""
        if not self.current_object:
            return
            
        # Determine curve ID from property
        curve_id = ""
        curve_type = "Pump" # Default
        
        if property_name == "Volume Curve":
            curve_id = self.current_object.volume_curve
            curve_type = "Volume"
        elif property_name == "Pump Curve":
            curve_id = self.current_object.pump_curve
            curve_type = "Pump"
        elif property_name == "Efficiency Curve":
            curve_id = self.current_object.efficiency_curve
            curve_type = "Efficiency"
             
        # Get existing curve data
        points = []
        comment = ""
        if curve_id:
            curve = self.project.network.get_curve(curve_id)
            if curve:
                points = curve.points
                comment = curve.comment
                curve_type = curve.curve_type # Use existing type
        
        dialog = CurveEditor(self)
        dialog.load_data(curve_id or "", curve_type, points, comment)
        
        if dialog.exec():
            new_id, new_type, new_points, new_comment = dialog.unload_data()
            
            if not new_id:
                return

            # Update or create curve
            from models import Curve
            curve = self.project.network.get_curve(new_id)
            if not curve:
                curve = Curve(new_id)
                self.project.network.add_curve(curve)
            
            curve.curve_type = new_type
            curve.points = new_points
            curve.comment = new_comment
            
            # Update object reference
            if property_name == "Volume Curve":
                self.current_object.volume_curve = new_id
            elif property_name == "Pump Curve":
                self.current_object.pump_curve = new_id
            elif property_name == "Efficiency Curve":
                self.current_object.efficiency_curve = new_id
                
            self.project.modified = True
            self.populate_properties()
            
    def edit_pattern(self, property_name):
        """Open pattern editor."""
        if not self.current_object:
            return
            
        # Determine pattern ID from property
        pattern_id = ""
        
        if property_name == "Demand Pattern":
            pattern_id = self.current_object.demand_pattern
        elif property_name == "Head Pattern":
            pattern_id = self.current_object.head_pattern
        elif property_name == "Pattern": # Pump speed pattern
            pattern_id = self.current_object.speed_pattern
        elif property_name == "Price Pattern":
            pattern_id = self.current_object.price_pattern
            
        # Get existing pattern data
        multipliers = []
        comment = ""
        if pattern_id:
            pattern = self.project.network.get_pattern(pattern_id)
            if pattern:
                multipliers = pattern.multipliers
                comment = pattern.comment
        
        dialog = PatternEditor(self)
        dialog.load_data(pattern_id or "", multipliers, comment)
        
        if dialog.exec():
            new_id, new_multipliers, new_comment = dialog.unload_data()
            
            if not new_id:
                return

            # Update or create pattern
            from models import Pattern
            pattern = self.project.network.get_pattern(new_id)
            if not pattern:
                pattern = Pattern(new_id)
                self.project.network.add_pattern(pattern)
            
            pattern.multipliers = new_multipliers
            pattern.comment = new_comment
            
            # Update object reference
            if property_name == "Demand Pattern":
                self.current_object.demand_pattern = new_id
            elif property_name == "Head Pattern":
                self.current_object.head_pattern = new_id
            elif property_name == "Pattern":
                self.current_object.speed_pattern = new_id
            elif property_name == "Price Pattern":
                self.current_object.price_pattern = new_id
                
            self.project.modified = True
            self.populate_properties()
