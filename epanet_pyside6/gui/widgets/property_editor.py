"""Property editor widget."""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PySide6.QtCore import Qt, Signal
from core.project import EPANETProject
from core.units import get_unit_label
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
        
        # Get flow units for unit labels
        flow_units = self.project.network.options.flow_units
        
        # Helper for unit labels
        def u(param_type):
            return f" ({get_unit_label(param_type, flow_units)})"
        
        # Add properties based on object type
        from models import Junction, Reservoir, Tank, Pipe, Pump, Valve, Label
        
        # Common properties for Nodes and Links
        if hasattr(self.current_object, 'comment'):
            self.add_property("Description", self.current_object.comment)
        if hasattr(self.current_object, 'tag'):
            self.add_property("Tag", self.current_object.tag)
            
        if isinstance(self.current_object, Junction):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property(f"X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
            self.add_property(f"Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
            self.add_property(f"Elevation{u('elevation')}", f"{(self.current_object.elevation or 0.0):.2f}")
            self.add_property(f"Base Demand{u('flow')}", f"{(self.current_object.base_demand or 0.0):.2f}")
            self.add_property("Demand Pattern", self.current_object.demand_pattern or "")
            self.add_action_property("Demands", "...", self.edit_demands)
            self.add_property("Emitter Coeff.", f"{(self.current_object.emitter_coeff or 0.0):.2f}")
            self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property(f"Demand (Result){u('flow')}", f"{(self.current_object.demand or 0.0):.2f}", editable=False)
                self.add_property(f"Head (Result){u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
                self.add_property(f"Pressure (Result){u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
                self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)

        elif isinstance(self.current_object, Reservoir):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
            self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
            self.add_property(f"Total Head{u('head')}", f"{(self.current_object.total_head or 0.0):.2f}")
            self.add_property("Head Pattern", self.current_object.head_pattern or "")
            self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property(f"Head (Result){u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
                self.add_property(f"Pressure (Result){u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
                self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)

        elif isinstance(self.current_object, Tank):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
            self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
            self.add_property(f"Elevation{u('elevation')}", f"{(self.current_object.elevation or 0.0):.2f}")
            self.add_property(f"Initial Level{u('length')}", f"{(self.current_object.init_level or 0.0):.2f}")
            self.add_property(f"Min Level{u('length')}", f"{(self.current_object.min_level or 0.0):.2f}")
            self.add_property(f"Max Level{u('length')}", f"{(self.current_object.max_level or 0.0):.2f}")
            self.add_property(f"Diameter{u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
            self.add_property(f"Min Volume{u('volume')}", f"{(self.current_object.min_volume or 0.0):.2f}")
            self.add_property("Volume Curve", self.current_object.volume_curve or "")
            self.add_property("Mixing Model", str(self.current_object.mixing_model.name))
            self.add_property("Mixing Fraction", f"{(self.current_object.mixing_fraction or 0.0):.2f}")
            self.add_property("Reaction Coeff.", f"{(self.current_object.bulk_coeff or 0.0):.2f}")
            self.add_property("Initial Quality", f"{(self.current_object.init_quality or 0.0):.2f}")
            self.add_action_property("Source Quality", "...", self.edit_source_quality)
            
            if self.project.has_results():
                self.add_property(f"Head (Result){u('head')}", f"{(self.current_object.head or 0.0):.2f}", editable=False)
                self.add_property(f"Pressure (Result){u('pressure')}", f"{(self.current_object.pressure or 0.0):.2f}", editable=False)
                self.add_property("Quality (Result)", f"{(self.current_object.quality or 0.0):.2f}", editable=False)
        
        elif isinstance(self.current_object, Pipe):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property(f"Length{u('length')}", f"{(self.current_object.length or 0.0):.2f}")
            self.add_property(f"Diameter{u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
            self.add_property("Roughness", f"{(self.current_object.roughness or 0.0):.2f}")
            self.add_property("Loss Coeff.", f"{(self.current_object.minor_loss or 0.0):.2f}")
            self.add_property("Initial Status", str(self.current_object.status.name))
            self.add_property("Bulk Coeff.", f"{(self.current_object.bulk_coeff or 0.0):.2f}")
            self.add_property("Wall Coeff.", f"{(self.current_object.wall_coeff or 0.0):.2f}")
            # Check Valve (simulated by CVPIPE type or property)
            self.add_property("Check Valve", "Yes" if self.current_object.has_check_valve else "No")
            
            if self.project.has_results():
                self.add_property(f"Flow (Result){u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
                self.add_property(f"Velocity (Result){u('velocity')}", f"{(self.current_object.velocity or 0.0):.2f}", editable=False)
                self.add_property(f"Headloss (Result){u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)
        
        elif isinstance(self.current_object, Pump):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property("Pump Curve", self.current_object.pump_curve or "")
            self.add_property("Power", f"{(self.current_object.power or 0.0):.2f}")
            self.add_property("Speed", f"{(self.current_object.speed or 0.0):.2f}")
            self.add_property("Pattern", self.current_object.speed_pattern or "")
            self.add_property("Initial Status", str(self.current_object.status.name))
            self.add_property("Efficiency Curve", self.current_object.efficiency_curve or "")
            self.add_property("Energy Price", f"{(self.current_object.energy_price or 0.0):.4f}")
            self.add_property("Price Pattern", self.current_object.price_pattern or "")
            
            if self.project.has_results():
                self.add_property(f"Flow (Result){u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
                self.add_property(f"Headloss (Result){u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)

        elif isinstance(self.current_object, Valve):
            self.add_property("ID", self.current_object.id, editable=False)
            self.add_property("Type", str(self.current_object.link_type.name), editable=False)
            self.add_property("From Node", self.current_object.from_node)
            self.add_property("To Node", self.current_object.to_node)
            self.add_property(f"Diameter{u('diameter')}", f"{(self.current_object.diameter or 0.0):.2f}")
            self.add_property("Setting", f"{(self.current_object.valve_setting or 0.0):.2f}")
            self.add_property("Loss Coeff.", f"{(self.current_object.minor_loss or 0.0):.2f}")
            self.add_property("Fixed Status", str(self.current_object.fixed_status.name) if hasattr(self.current_object, 'fixed_status') else "OPEN")
            
            if self.project.has_results():
                self.add_property(f"Flow (Result){u('flow')}", f"{(self.current_object.flow or 0.0):.2f}", editable=False)
                self.add_property(f"Velocity (Result){u('velocity')}", f"{(self.current_object.velocity or 0.0):.2f}", editable=False)
                self.add_property(f"Headloss (Result){u('headloss')}", f"{(self.current_object.headloss or 0.0):.2f}", editable=False)

        elif isinstance(self.current_object, Label):
            self.add_property("Text", self.current_object.text)
            self.add_property("X Coordinate", f"{(self.current_object.x or 0.0):.2f}")
            self.add_property("Y Coordinate", f"{(self.current_object.y or 0.0):.2f}")
            self.add_property("Font Size", str(self.current_object.font_size))
            self.add_property("Font Bold", "Yes" if self.current_object.font_bold else "No")
            self.add_property("Font Italic", "Yes" if self.current_object.font_italic else "No")
        
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
        # Remove unit label from property name for matching
        # Assuming format "Name (Unit)"
        clean_name = property_name.split(' (')[0]
        
        new_value = item.text()
        
        # Update object property
        try:
            from models import Junction, Reservoir, Tank, Pipe, Pump, Valve, Label
            
            # Common properties
            if clean_name == "Description":
                self.current_object.comment = new_value
            elif clean_name == "Tag":
                self.current_object.tag = new_value
            
            if isinstance(self.current_object, Junction):
                if clean_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif clean_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif clean_name == "Elevation":
                    self.current_object.elevation = float(new_value)
                elif clean_name == "Base Demand":
                    self.current_object.base_demand = float(new_value)
                elif clean_name == "Demand Pattern":
                    self.current_object.demand_pattern = new_value
                elif clean_name == "Emitter Coeff.":
                    self.current_object.emitter_coeff = float(new_value)
                elif clean_name == "Initial Quality":
                    self.current_object.init_quality = float(new_value)
                    
            elif isinstance(self.current_object, Reservoir):
                if clean_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif clean_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif clean_name == "Total Head":
                    self.current_object.total_head = float(new_value)
                elif clean_name == "Head Pattern":
                    self.current_object.head_pattern = new_value
                elif clean_name == "Initial Quality":
                    self.current_object.init_quality = float(new_value)
                    
            elif isinstance(self.current_object, Tank):
                if clean_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif clean_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif clean_name == "Elevation":
                    self.current_object.elevation = float(new_value)
                elif clean_name == "Initial Level":
                    self.current_object.init_level = float(new_value)
                elif clean_name == "Min Level":
                    self.current_object.min_level = float(new_value)
                elif clean_name == "Max Level":
                    self.current_object.max_level = float(new_value)
                elif clean_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif clean_name == "Min Volume":
                    self.current_object.min_volume = float(new_value)
                elif clean_name == "Volume Curve":
                    self.current_object.volume_curve = new_value
                elif clean_name == "Mixing Fraction":
                    self.current_object.mixing_fraction = float(new_value)
                elif clean_name == "Reaction Coeff.":
                    self.current_object.bulk_coeff = float(new_value)
                elif clean_name == "Initial Quality":
                    self.current_object.init_quality = float(new_value)
                    
            elif isinstance(self.current_object, Pipe):
                if clean_name == "Length":
                    self.current_object.length = float(new_value)
                elif clean_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif clean_name == "Roughness":
                    self.current_object.roughness = float(new_value)
                elif clean_name == "Loss Coeff.":
                    self.current_object.minor_loss = float(new_value)
                elif clean_name == "Bulk Coeff.":
                    self.current_object.bulk_coeff = float(new_value)
                elif clean_name == "Wall Coeff.":
                    self.current_object.wall_coeff = float(new_value)
                elif clean_name == "Check Valve":
                    self.current_object.has_check_valve = (new_value.lower() in ['yes', 'true', '1'])
                    
            elif isinstance(self.current_object, Pump):
                if clean_name == "Power":
                    self.current_object.power = float(new_value)
                elif clean_name == "Speed":
                    self.current_object.speed = float(new_value)
                elif clean_name == "Pump Curve":
                    self.current_object.pump_curve = new_value
                elif clean_name == "Pattern":
                    self.current_object.speed_pattern = new_value
                elif clean_name == "Efficiency Curve":
                    self.current_object.efficiency_curve = new_value
                elif clean_name == "Energy Price":
                    self.current_object.energy_price = float(new_value)
                elif clean_name == "Price Pattern":
                    self.current_object.price_pattern = new_value
                    
            elif isinstance(self.current_object, Valve):
                if clean_name == "Diameter":
                    self.current_object.diameter = float(new_value)
                elif clean_name == "Setting":
                    self.current_object.valve_setting = float(new_value)
                elif clean_name == "Loss Coeff.":
                    self.current_object.minor_loss = float(new_value)
            
            elif isinstance(self.current_object, Label):
                if clean_name == "Text":
                    self.current_object.text = new_value
                elif clean_name == "X Coordinate":
                    self.current_object.x = float(new_value)
                elif clean_name == "Y Coordinate":
                    self.current_object.y = float(new_value)
                elif clean_name == "Font Size":
                    self.current_object.font_size = int(new_value)
                elif clean_name == "Font Bold":
                    self.current_object.font_bold = (new_value.lower() in ['yes', 'true', '1'])
                elif clean_name == "Font Italic":
                    self.current_object.font_italic = (new_value.lower() in ['yes', 'true', '1'])
            
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
