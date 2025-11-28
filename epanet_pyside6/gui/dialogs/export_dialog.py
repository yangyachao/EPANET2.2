"""Export Dialog for network data."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QFileDialog, QLabel, QMessageBox, QRadioButton,
    QButtonGroup
)
from PySide6.QtCore import Qt

class ExportDialog(QDialog):
    """Dialog for exporting network data."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Export Network Data")
        self.resize(400, 350)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Select the data to export and choose the output format."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Data selection group
        data_group = QGroupBox("Data to Export")
        data_layout = QVBoxLayout()
        
        self.export_nodes_check = QCheckBox("Nodes (Junctions, Reservoirs, Tanks)")
        self.export_nodes_check.setChecked(True)
        data_layout.addWidget(self.export_nodes_check)
        
        self.export_links_check = QCheckBox("Links (Pipes, Pumps, Valves)")
        self.export_links_check.setChecked(True)
        data_layout.addWidget(self.export_links_check)
        
        self.export_patterns_check = QCheckBox("Patterns")
        self.export_patterns_check.setChecked(True)
        data_layout.addWidget(self.export_patterns_check)
        
        self.export_curves_check = QCheckBox("Curves")
        self.export_curves_check.setChecked(True)
        data_layout.addWidget(self.export_curves_check)
        
        self.export_controls_check = QCheckBox("Controls and Rules")
        self.export_controls_check.setChecked(True)
        data_layout.addWidget(self.export_controls_check)
        
        self.export_results_check = QCheckBox("Simulation Results")
        self.export_results_check.setChecked(self.project.has_results())
        self.export_results_check.setEnabled(self.project.has_results())
        data_layout.addWidget(self.export_results_check)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Format selection group
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()
        
        self.format_group = QButtonGroup(self)
        
        self.text_radio = QRadioButton("Text Report (.txt)")
        self.text_radio.setChecked(True)
        self.format_group.addButton(self.text_radio)
        format_layout.addWidget(self.text_radio)
        
        self.csv_radio = QRadioButton("CSV Spreadsheet (.csv)")
        self.format_group.addButton(self.csv_radio)
        format_layout.addWidget(self.csv_radio)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self.export_data)
        btn_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def export_data(self):
        """Export data to file."""
        # Determine file extension
        if self.text_radio.isChecked():
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        else:
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        
        # Get save file path
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Network Data",
            "",
            file_filter
        )
        
        if not filepath:
            return
        
        # Ensure correct extension
        if not filepath.endswith(default_ext):
            filepath += default_ext
        
        try:
            from core.export_utils import ExportUtils
            
            if self.text_radio.isChecked():
                # Export as text report
                ExportUtils.export_network_data(
                    self.project,
                    filepath,
                    include_results=self.export_results_check.isChecked()
                )
            else:
                # Export as CSV
                if self.export_results_check.isChecked():
                    ExportUtils.export_results_csv(self.project, filepath)
                else:
                    # For CSV without results, use text export
                    ExportUtils.export_network_data(
                        self.project,
                        filepath,
                        include_results=False
                    )
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data exported successfully to:\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data:\n{str(e)}"
            )
