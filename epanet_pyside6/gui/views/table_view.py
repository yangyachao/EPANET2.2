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
        
        # Define available columns for each type
        # Format: key -> (header_name, value_getter_func, unit_type)
        self.column_definitions = self._init_column_definitions()
        
        # Default visible columns
        self.visible_columns = {
            "Junctions": ["id", "elevation", "base_demand", "demand", "head", "pressure"],
            "Reservoirs": ["id", "total_head", "head_pattern", "head", "pressure"],
            "Tanks": ["id", "elevation", "init_level", "min_level", "max_level", "diameter", "head", "pressure"],
            "Pipes": ["id", "from_node", "to_node", "length", "diameter", "roughness", "flow", "velocity", "headloss"],
            "Pumps": ["id", "from_node", "to_node", "flow", "headloss"],
            "Valves": ["id", "from_node", "to_node", "diameter", "type", "flow", "velocity", "headloss"]
        }
        
        self.setup_ui()
        self.refresh_data()
        
    def _init_column_definitions(self):
        """Initialize column definitions."""
        return {
            "Junctions": {
                "id": ("ID", lambda n: n.id, None),
                "elevation": ("Elevation", lambda n: f"{n.elevation:.2f}", "elevation"),
                "base_demand": ("Base Demand", lambda n: f"{n.base_demand:.2f}", "demand"),
                "demand": ("Demand", lambda n: f"{n.demand:.2f}", "demand"),
                "head": ("Head", lambda n: f"{n.head:.2f}", "head"),
                "pressure": ("Pressure", lambda n: f"{n.pressure:.2f}", "pressure"),
                "quality": ("Quality", lambda n: f"{n.quality:.2f}", "quality")
            },
            "Reservoirs": {
                "id": ("ID", lambda n: n.id, None),
                "total_head": ("Total Head", lambda n: f"{n.total_head:.2f}", "head"),
                "head_pattern": ("Head Pattern", lambda n: str(n.head_pattern or ""), None),
                "head": ("Head", lambda n: f"{n.head:.2f}", "head"),
                "pressure": ("Pressure", lambda n: f"{n.pressure:.2f}", "pressure"),
                "quality": ("Quality", lambda n: f"{n.quality:.2f}", "quality")
            },
            "Tanks": {
                "id": ("ID", lambda n: n.id, None),
                "elevation": ("Elevation", lambda n: f"{n.elevation:.2f}", "elevation"),
                "init_level": ("Init Level", lambda n: f"{n.init_level:.2f}", "level"),
                "min_level": ("Min Level", lambda n: f"{n.min_level:.2f}", "level"),
                "max_level": ("Max Level", lambda n: f"{n.max_level:.2f}", "level"),
                "diameter": ("Diameter", lambda n: f"{n.diameter:.2f}", "diameter"),
                "min_vol": ("Min Vol", lambda n: f"{n.min_vol:.2f}", "volume"),
                "head": ("Head", lambda n: f"{n.head:.2f}", "head"),
                "pressure": ("Pressure", lambda n: f"{n.pressure:.2f}", "pressure"),
                "quality": ("Quality", lambda n: f"{n.quality:.2f}", "quality")
            },
            "Pipes": {
                "id": ("ID", lambda l: l.id, None),
                "from_node": ("From Node", lambda l: l.from_node, None),
                "to_node": ("To Node", lambda l: l.to_node, None),
                "length": ("Length", lambda l: f"{l.length:.2f}", "length"),
                "diameter": ("Diameter", lambda l: f"{l.diameter:.2f}", "diameter"),
                "roughness": ("Roughness", lambda l: f"{l.roughness:.2f}", "roughness"),
                "flow": ("Flow", lambda l: f"{l.flow:.2f}", "flow"),
                "velocity": ("Velocity", lambda l: f"{l.velocity:.2f}", "velocity"),
                "headloss": ("Headloss", lambda l: f"{l.headloss:.4f}", "headloss"),
                "status": ("Status", lambda l: l.status.name if hasattr(l, 'status') else "OPEN", None)
            },
            "Pumps": {
                "id": ("ID", lambda l: l.id, None),
                "from_node": ("From Node", lambda l: l.from_node, None),
                "to_node": ("To Node", lambda l: l.to_node, None),
                "flow": ("Flow", lambda l: f"{l.flow:.2f}", "flow"),
                "headloss": ("Headloss", lambda l: f"{l.headloss:.2f}", "headloss"),
                "status": ("Status", lambda l: l.status.name if hasattr(l, 'status') else "OPEN", None)
            },
            "Valves": {
                "id": ("ID", lambda l: l.id, None),
                "from_node": ("From Node", lambda l: l.from_node, None),
                "to_node": ("To Node", lambda l: l.to_node, None),
                "diameter": ("Diameter", lambda l: f"{l.diameter:.2f}", "diameter"),
                "type": ("Type", lambda l: l.link_type.name if hasattr(l, 'link_type') else "VALVE", None),
                "setting": ("Setting", lambda l: f"{l.valve_setting:.2f}", None),
                "flow": ("Flow", lambda l: f"{l.flow:.2f}", "flow"),
                "velocity": ("Velocity", lambda l: f"{l.velocity:.2f}", "velocity"),
                "headloss": ("Headloss", lambda l: f"{l.headloss:.2f}", "headloss"),
                "status": ("Status", lambda l: l.status.name if hasattr(l, 'status') else "OPEN", None)
            }
        }
        
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
        
        self.options_btn = QPushButton("Options...")
        self.options_btn.clicked.connect(self.show_options)
        controls_layout.addWidget(self.options_btn)
        
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
        """Get header with unit label."""
        if not param_type:
            return param_name
            
        flow_units = self.project.network.options.flow_units
        unit = get_unit_label(param_type, flow_units)
        if unit:
            return f"{param_name} ({unit})"
        return param_name
        
    def show_options(self):
        """Show table options dialog."""
        from gui.dialogs.table_options_dialog import TableOptionsDialog
        
        # Prepare available columns
        available_cols = []
        defs = self.column_definitions.get(self.current_type, {})
        for col_id, (name, _, _) in defs.items():
            available_cols.append((col_id, name))
            
        # Current visible columns
        visible_cols = self.visible_columns.get(self.current_type, [])
        
        dialog = TableOptionsDialog(
            available_cols, 
            visible_cols, 
            self.filter_edit.text(),
            self
        )
        
        if dialog.exec():
            options = dialog.get_options()
            self.visible_columns[self.current_type] = options['visible_columns']
            self.filter_edit.setText(options['filter_text'])
            self.refresh_data()
        
    def refresh_data(self):
        """Refresh table data."""
        # Disable sorting while updating
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        network = self.project.network
        
        # Get objects based on type
        objects = []
        if self.current_type == "Junctions":
            objects = network.get_junctions()
        elif self.current_type == "Reservoirs":
            objects = network.get_reservoirs()
        elif self.current_type == "Tanks":
            objects = network.get_tanks()
        elif self.current_type == "Pipes":
            objects = network.get_pipes()
        elif self.current_type == "Pumps":
            objects = network.get_pumps()
        elif self.current_type == "Valves":
            objects = network.get_valves()
            
        # Get visible columns
        visible_cols = self.visible_columns.get(self.current_type, [])
        col_defs = self.column_definitions.get(self.current_type, {})
        
        # Prepare headers
        headers = []
        for col_id in visible_cols:
            if col_id in col_defs:
                name, _, unit_type = col_defs[col_id]
                headers.append(self._get_header_with_unit(name, unit_type))
        
        # Populate table
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(objects))
        
        for row, obj in enumerate(objects):
            for col, col_id in enumerate(visible_cols):
                if col_id in col_defs:
                    _, getter, _ = col_defs[col_id]
                    try:
                        value = getter(obj)
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable) # Read-only
                        self.table.setItem(row, col, item)
                    except Exception:
                        self.table.setItem(row, col, QTableWidgetItem("Error"))
        
        # Apply filter if any
        if self.filter_edit.text():
            self.filter_rows(self.filter_edit.text())
            
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
                    if self.table.isRowHidden(row):
                        continue
                        
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
        # Find ID column index
        id_col = -1
        visible_cols = self.visible_columns.get(self.current_type, [])
        for i, col_id in enumerate(visible_cols):
            if col_id == 'id':
                id_col = i
                break
        
        if id_col == -1:
            return # No ID column visible
            
        for row in range(self.table.rowCount()):
            item = self.table.item(row, id_col)
            if not item:
                continue
                
            if text in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def copy_to_clipboard(self):
        """Copy selected rows (or all if none selected) to clipboard."""
        from PySide6.QtGui import QGuiApplication
        
        selected_ranges = self.table.selectedRanges()
        
        # If no selection, select all visible
        if not selected_ranges:
            self.table.selectAll()
            selected_ranges = self.table.selectedRanges()
            
        if not selected_ranges:
            return
            
        text = ""
        
        # Headers
        headers = []
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        text += "\t".join(headers) + "\n"
        
        # Data
        # Iterate over rows in the first range (assuming single selection mode or contiguous)
        # For multiple ranges, it's more complex. Let's assume full rows for simplicity or just selected cells.
        # Implementation for full rows of selection:
        
        rows = set()
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                if not self.table.isRowHidden(row):
                    rows.add(row)
                    
        for row in sorted(rows):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
            
        QGuiApplication.clipboard().setText(text)
        
    def print_table(self, printer):
        """Print table content."""
        from PySide6.QtGui import QTextDocument, QTextCursor, QTextTableFormat
        
        # Create HTML representation
        html = "<html><head><style>"
        html += "table { border-collapse: collapse; width: 100%; }"
        html += "th, td { border: 1px solid black; padding: 4px; text-align: center; }"
        html += "th { background-color: #f2f2f2; }"
        html += "</style></head><body>"
        
        html += f"<h2>{self.current_type} Report</h2>"
        html += "<table>"
        
        # Headers
        html += "<thead><tr>"
        for col in range(self.table.columnCount()):
            html += f"<th>{self.table.horizontalHeaderItem(col).text()}</th>"
        html += "</tr></thead>"
        
        # Body
        html += "<tbody>"
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
                
            html += "<tr>"
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                text = item.text() if item else ""
                html += f"<td>{text}</td>"
            html += "</tr>"
        html += "</tbody></table></body></html>"
        
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)
