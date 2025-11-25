"""Table view for network data and results."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLabel, QHBoxLayout, QHeaderView, QPushButton, QFileDialog, QLineEdit
from PySide6.QtCore import Qt, Signal
from core.constants import NodeType, LinkType
from core.units import get_unit_label

class TableView(QWidget):
    """Widget for displaying network data in tables."""
    
    object_selected = Signal(str, str) # type, id
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_type = "Junctions"
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Junctions", "Reservoirs", "Tanks",
            "Pipes", "Pumps", "Valves"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        controls_layout.addWidget(QLabel("Object Type:"))
        controls_layout.addWidget(self.type_combo)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        controls_layout.addWidget(self.export_btn)
        
        controls_layout.addStretch()
        
        # Filter
        controls_layout.addWidget(QLabel("Filter ID:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Enter ID...")
        self.filter_edit.textChanged.connect(self.filter_rows)
        controls_layout.addWidget(self.filter_edit)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True) # Enable sorting
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
    def on_type_changed(self, text):
        """Handle object type change."""
        self.current_type = text
        self.refresh_data()
        
    def on_selection_changed(self):
        """Handle table selection change."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
            
        # Get ID from first column (index 0) of the selected row
        row = selected_items[0].row()
        obj_id = self.table.item(row, 0).text()
        
        # Determine object type for signal
        # Map plural names to singular types used in browser/main window
        type_map = {
            "Junctions": "Node",
            "Reservoirs": "Node", 
            "Tanks": "Node",
            "Pipes": "Link",
            "Pumps": "Link",
            "Valves": "Link"
        }
        
        obj_type = type_map.get(self.current_type, "Node")
        self.object_selected.emit(obj_type, obj_id)
    
    def _get_header_with_unit(self, param_name: str, param_type: str) -> str:
        """Get header with unit label.
        
        Args:
            param_name: Display name of parameter
            param_type: Type for unit lookup
            
        Returns:
            Header string with unit label
        """
        flow_units = self.project.network.options.flow_units
        unit = get_unit_label(param_type, flow_units)
        if unit:
            return f"{param_name} ({unit})"
        return param_name
        
    def refresh_data(self):
        """Refresh table data."""
        # Disable sorting while updating
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        network = self.project.network
        data = []
        headers = []
        
        if self.current_type == "Junctions":
            headers = [
                "ID",
                self._get_header_with_unit("Elevation", "elevation"),
                self._get_header_with_unit("Base Demand", "demand"),
                self._get_header_with_unit("Demand", "demand"),
                self._get_header_with_unit("Head", "head"),
                self._get_header_with_unit("Pressure", "pressure")
            ]
            for node in network.get_junctions():
                data.append([
                    node.id,
                    f"{node.elevation:.2f}",
                    f"{node.base_demand:.2f}",
                    f"{node.demand:.2f}",
                    f"{node.head:.2f}",
                    f"{node.pressure:.2f}"
                ])
        elif self.current_type == "Reservoirs":
            headers = [
                "ID",
                self._get_header_with_unit("Total Head", "head"),
                "Head Pattern",
                self._get_header_with_unit("Head", "head"),
                self._get_header_with_unit("Pressure", "pressure")
            ]
            for node in network.get_reservoirs():
                data.append([
                    node.id,
                    f"{node.total_head:.2f}", # Using total_head instead of elevation for reservoir base head
                    str(node.head_pattern or ""),
                    f"{node.head:.2f}",
                    f"{node.pressure:.2f}"
                ])
        elif self.current_type == "Tanks":
            headers = [
                "ID",
                self._get_header_with_unit("Elevation", "elevation"),
                self._get_header_with_unit("Init Level", "level"),
                self._get_header_with_unit("Min Level", "level"),
                self._get_header_with_unit("Max Level", "level"),
                self._get_header_with_unit("Diameter", "diameter"),
                self._get_header_with_unit("Head", "head"),
                self._get_header_with_unit("Pressure", "pressure")
            ]
            for node in network.get_tanks():
                data.append([
                    node.id,
                    f"{node.elevation:.2f}",
                    f"{node.init_level:.2f}",
                    f"{node.min_level:.2f}",
                    f"{node.max_level:.2f}",
                    f"{node.diameter:.2f}",
                    f"{node.head:.2f}",
                    f"{node.pressure:.2f}"
                ])
        elif self.current_type == "Pipes":
            headers = [
                "ID", "From Node", "To Node",
                self._get_header_with_unit("Length", "length"),
                self._get_header_with_unit("Diameter", "diameter"),
                self._get_header_with_unit("Roughness", "roughness"),
                self._get_header_with_unit("Flow", "flow"),
                self._get_header_with_unit("Velocity", "velocity"),
                self._get_header_with_unit("Headloss", "headloss")
            ]
            for link in network.get_pipes():
                data.append([
                    link.id,
                    link.from_node,
                    link.to_node,
                    f"{link.length:.2f}",
                    f"{link.diameter:.2f}",
                    f"{link.roughness:.2f}",
                    f"{link.flow:.2f}",
                    f"{link.velocity:.2f}",
                    f"{link.headloss:.4f}"
                ])
        elif self.current_type == "Pumps":
            headers = [
                "ID", "From Node", "To Node",
                self._get_header_with_unit("Flow", "flow"),
                self._get_header_with_unit("Headloss", "headloss")
            ]
            for link in network.get_pumps():
                data.append([
                    link.id,
                    link.from_node,
                    link.to_node,
                    f"{link.flow:.2f}",
                    f"{link.headloss:.2f}"
                ])
        elif self.current_type == "Valves":
            headers = [
                "ID", "From Node", "To Node",
                self._get_header_with_unit("Diameter", "diameter"),
                "Type",
                self._get_header_with_unit("Flow", "flow"),
                self._get_header_with_unit("Velocity", "velocity"),
                self._get_header_with_unit("Headloss", "headloss")
            ]
            for link in network.get_valves():
                data.append([
                    link.id,
                    link.from_node,
                    link.to_node,
                    f"{link.diameter:.2f}",
                    link.valve_type.name if hasattr(link, 'valve_type') else "VALVE",
                    f"{link.flow:.2f}",
                    f"{link.velocity:.2f}",
                    f"{link.headloss:.2f}"
                ])
                
        # Populate table
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable) # Read-only for now
                self.table.setItem(row, col, item)
                
        # Re-enable sorting
        self.table.setSortingEnabled(True)

    def export_to_csv(self):
        """Export current table data to CSV."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
            
        import csv
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", str(e))

    def filter_rows(self, text):
        """Filter rows by ID."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0) # ID is always column 0
            if not item:
                continue
                
            if text in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
