"""Property editor widget."""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PySide6.QtCore import Qt, Signal
from core.project import EPANETProject
from gui.dialogs.demand_editor import DemandEditorDialog
from gui.dialogs.source_editor import SourceEditorDialog


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
        
        # Add properties based on object type
        from models import Junction, Reservoir, Tank, Pipe, Pump, Valve
        
        if isinstance(self.current_object, Junction):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("X Coordinate", f"{self.current_object.x:.2f}")
            self.add_property("Y Coordinate", f"{self.current_object.y:.2f}")
            self.add_property("Elevation", f"{self.current_object.elevation:.2f}")
            self.add_property("Base Demand", f"{self.current_object.base_demand:.2f}")
            self.add_property("Demand Pattern", self.current_object.demand_pattern or "")
            self.add_action_property("Demands", "...", self.edit_demands)
            self.add_property("Emitter Coeff.", f"{self.current_object.emitter_coeff:.2f}")
            self.add_property("Initial Quality", f"{self.current_object.init_quality:.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property("Demand (Result)", f"{self.current_object.demand:.2f}", editable=False)
                self.add_property("Head (Result)", f"{self.current_object.head:.2f}", editable=False)
                self.add_property("Pressure (Result)", f"{self.current_object.pressure:.2f}", editable=False)
                self.add_property("Quality (Result)", f"{self.current_object.quality:.2f}", editable=False)

        elif isinstance(self.current_object, Reservoir):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("X Coordinate", f"{self.current_object.x:.2f}")
            self.add_property("Y Coordinate", f"{self.current_object.y:.2f}")
            self.add_property("Total Head", f"{self.current_object.total_head:.2f}")
            self.add_property("Head Pattern", self.current_object.head_pattern or "")
            self.add_property("Initial Quality", f"{self.current_object.init_quality:.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property("Head (Result)", f"{self.current_object.head:.2f}", editable=False)
                self.add_property("Pressure (Result)", f"{self.current_object.pressure:.2f}", editable=False)
                self.add_property("Quality (Result)", f"{self.current_object.quality:.2f}", editable=False)

        elif isinstance(self.current_object, Tank):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("X Coordinate", f"{self.current_object.x:.2f}")
            self.add_property("Y Coordinate", f"{self.current_object.y:.2f}")
            self.add_property("Elevation", f"{self.current_object.elevation:.2f}")
            self.add_property("Initial Level", f"{self.current_object.init_level:.2f}")
            self.add_property("Min Level", f"{self.current_object.min_level:.2f}")
            self.add_property("Max Level", f"{self.current_object.max_level:.2f}")
            self.add_property("Diameter", f"{self.current_object.diameter:.2f}")
            self.add_property("Min Volume", f"{self.current_object.min_volume:.2f}")
            self.add_property("Volume Curve", self.current_object.volume_curve or "")
            self.add_property("Mixing Model", str(self.current_object.mixing_model.name))
            self.add_property("Mixing Fraction", f"{self.current_object.mixing_fraction:.2f}")
            self.add_property("Reaction Coeff.", f"{self.current_object.bulk_coeff:.2f}")
            self.add_property("Initial Quality", f"{self.current_object.init_quality:.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property("Head (Result)", f"{self.current_object.head:.2f}", editable=False)
                self.add_property("Pressure (Result)", f"{self.current_object.pressure:.2f}", editable=False)
                self.add_property("Quality (Result)", f"{self.current_object.quality:.2f}", editable=False)
        
        elif isinstance(self.current_object, Pipe):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property("Length", f"{self.current_object.length:.2f}")
            self.add_property("Diameter", f"{self.current_object.diameter:.2f}")
            self.add_property("Roughness", f"{self.current_object.roughness:.2f}")
            self.add_property("Loss Coeff.", f"{self.current_object.minor_loss:.2f}")
            self.add_property("Initial Status", str(self.current_object.status.name))
            self.add_property("Bulk Coeff.", f"{self.current_object.bulk_coeff:.2f}")
            self.add_property("Wall Coeff.", f"{self.current_object.wall_coeff:.2f}")
            
            if self.project.has_results():
                self.add_property("Flow (Result)", f"{self.current_object.flow:.2f}", editable=False)
                self.add_property("Velocity (Result)", f"{self.current_object.velocity:.2f}", editable=False)
                self.add_property("Headloss (Result)", f"{self.current_object.headloss:.2f}", editable=False)
        
        elif isinstance(self.current_object, Pump):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property("Pump Curve", self.current_object.pump_curve or "")
            self.add_property("Power", f"{self.current_object.power:.2f}")
            self.add_property("Speed", f"{self.current_object.speed:.2f}")
            self.add_property("Pattern", self.current_object.speed_pattern or "")
            self.add_property("Initial Status", str(self.current_object.status.name))
            
            if self.project.has_results():
                self.add_property("Flow (Result)", f"{self.current_object.flow:.2f}", editable=False)
                self.add_property("Headloss (Result)", f"{self.current_object.headloss:.2f}", editable=False)

        elif isinstance(self.current_object, Valve):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("Type", str(self.current_object.link_type.name), editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property("Diameter", f"{self.current_object.diameter:.2f}")
            self.add_property("Setting", f"{self.current_object.valve_setting:.2f}")
            self.add_property("Loss Coeff.", f"{self.current_object.minor_loss:.2f}")
            self.add_property("Fixed Status", str(self.current_object.fixed_status.name))
            
            if self.project.has_results():
                self.add_property("Flow (Result)", f"{self.current_object.flow:.2f}", editable=False)
                self.add_property("Velocity (Result)", f"{self.current_object.velocity:.2f}", editable=False)
                self.add_property("Headloss (Result)", f"{self.current_object.headloss:.2f}", editable=False)
        
        # Re-enable signals
        self.blockSignals(False)
    
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
    
    def on_item_changed(self, item):
        """Handle property value change."""
        if not self.current_object or item.column() != 1:
            return
        
        property_name = self.item(item.row(), 0).text()
        new_value = item.text()
        
        # Update object property
        try:
            from models import Junction, Reservoir, Tank, Pipe, Pump, Valve
            
            if isinstance(self.current_object, Junction):
                if property_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif property_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif property_name == "Elevation":
                    self.current_object.elevation = float(new_value)
                elif property_name == "Base Demand":
                    self.current_object.base_demand = float(new_value)
                elif property_name == "Demand Pattern":
                    self.current_object.demand_pattern = new_value
                    
            elif isinstance(self.current_object, Reservoir):
                if property_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif property_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif property_name == "Total Head":
                    self.current_object.total_head = float(new_value)
                elif property_name == "Head Pattern":
                    self.current_object.head_pattern = new_value
                    
            elif isinstance(self.current_object, Tank):
                if property_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif property_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif property_name == "Elevation":
                    self.current_object.elevation = float(new_value)
                elif property_name == "Initial Level":
                    self.current_object.init_level = float(new_value)
                elif property_name == "Min Level":
                    self.current_object.min_level = float(new_value)
                elif property_name == "Max Level":
                    self.current_object.max_level = float(new_value)
                elif property_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif property_name == "Min Volume":
                    self.current_object.min_volume = float(new_value)
                    
            elif isinstance(self.current_object, Pipe):
                if property_name == "Length":
                    self.current_object.length = float(new_value)
                elif property_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif property_name == "Roughness":
                    self.current_object.roughness = float(new_value)
                elif property_name == "Minor Loss":
                    self.current_object.minor_loss = float(new_value)
                    
            elif isinstance(self.current_object, Pump):
                if property_name == "Power":
                    self.current_object.power = float(new_value)
                elif property_name == "Speed":
                    self.current_object.speed = float(new_value)
                elif property_name == "Curve":
                    self.current_object.pump_curve = new_value
                    
            elif isinstance(self.current_object, Valve):
                if property_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif property_name == "Setting":
                    self.current_object.valve_setting = float(new_value)
                elif property_name == "Minor Loss":
                    self.current_object.minor_loss = float(new_value)
            
            # Mark project as modified
            self.project.modified = True
            # Emit update signal so map/browser can refresh
            try:
                self.objectUpdated.emit(self.current_object)
            except Exception:
                pass
        except ValueError:
            # Invalid input, maybe revert or show error
            # For now, just ignore
            pass
    
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
