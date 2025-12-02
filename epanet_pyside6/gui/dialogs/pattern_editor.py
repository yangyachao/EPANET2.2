"""Pattern Editor Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries, QValueAxis
from PySide6.QtGui import QPainter, QBrush, QColor
from typing import Optional, List
import os


class PatternEditor(QDialog):
    """Dialog for editing time patterns."""
    
    pattern_updated = Signal(str, list, str)  # id, multipliers, comment
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pattern_id = ""
        self.old_id = ""
        self.multipliers = []
        self.comment = ""
        self.modified = False
        self.pattern_timestep = 1.0  # hours
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Pattern Editor")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # ID and Comment section
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Pattern ID:"), 0, 0)
        self.id_edit = QLineEdit()
        self.id_edit.setMaxLength(31)
        self.id_edit.textChanged.connect(self.on_modified)
        info_layout.addWidget(self.id_edit, 0, 1)
        
        info_layout.addWidget(QLabel("Comment:"), 1, 0)
        self.comment_edit = QLineEdit()
        self.comment_edit.textChanged.connect(self.on_modified)
        info_layout.addWidget(self.comment_edit, 1, 1)
        
        layout.addLayout(info_layout)
        
        # Multipliers table
        self.table = QTableWidget()
        self.table.setRowCount(2)
        self.table.setColumnCount(24)  # Default 24 periods
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setFixedHeight(150)  # Increased height to ensure scrollbar visibility
        # Force scrollbar style
        self.table.setStyleSheet("""
            QScrollBar:horizontal {
                height: 15px;
                background: #f0f0f0;
            }
            QScrollBar::handle:horizontal {
                background: #cdcdcd;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Set row headers
        self.table.setVerticalHeaderLabels(["Time Period", "Multiplier"])
        
        # Initialize column headers
        for i in range(24):
            self.table.setItem(0, i, QTableWidgetItem(str(i + 1)))
            self.table.item(0, i).setFlags(Qt.ItemIsEnabled)  # Read-only
            self.table.setItem(1, i, QTableWidgetItem(""))
        
        self.table.itemChanged.connect(self.on_table_changed)
        layout.addWidget(self.table)
        
        # Chart
        self.chart = QChart()
        self.chart.setTitle("Pattern Visualization")
        self.chart.legend().hide()
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(400)
        layout.addWidget(self.chart_view)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load...")
        load_btn.clicked.connect(self.load_pattern)
        button_layout.addWidget(load_btn)
        
        save_btn = QPushButton("Save...")
        save_btn.clicked.connect(self.save_pattern)
        button_layout.addWidget(save_btn)
        
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
        
    def load_data(self, pattern_id: str, multipliers: List[float], comment: str = "", timestep: float = 1.0):
        """Load pattern data into the dialog.
        
        Args:
            pattern_id: Pattern ID
            multipliers: List of multiplier values
            comment: Pattern comment/description
            timestep: Pattern time step in hours
        """
        self.pattern_id = pattern_id
        self.old_id = pattern_id
        self.multipliers = multipliers.copy()
        self.comment = comment
        self.pattern_timestep = timestep
        
        # Update UI
        self.id_edit.setText(pattern_id)
        self.comment_edit.setText(comment)
        
        # Expand table if needed
        if len(multipliers) > self.table.columnCount():
            self.table.setColumnCount(len(multipliers))
            for i in range(24, len(multipliers)):
                self.table.setItem(0, i, QTableWidgetItem(str(i + 1)))
                self.table.item(0, i).setFlags(Qt.ItemIsEnabled)
                self.table.setItem(1, i, QTableWidgetItem(""))
        
        # Load multipliers
        for i, value in enumerate(multipliers):
            self.table.setItem(1, i, QTableWidgetItem(str(value)))
        
        self.plot_data()
        self.modified = False
        
    def unload_data(self) -> tuple:
        """Get the current pattern data.
        
        Returns:
            Tuple of (pattern_id, multipliers, comment)
        """
        pattern_id = self.id_edit.text().strip()
        comment = self.comment_edit.text()
        
        multipliers = []
        for i in range(self.table.columnCount()):
            item = self.table.item(1, i)
            if item and item.text().strip():
                try:
                    value = float(item.text())
                    multipliers.append(value)
                except ValueError:
                    pass
        
        return pattern_id, multipliers, comment
        
    def plot_data(self):
        """Plot the pattern data on the chart."""
        # Remove existing axes
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)
            
        self.chart.removeAllSeries()
        
        # Get multipliers from table
        multipliers = []
        for i in range(self.table.columnCount()):
            item = self.table.item(1, i)
            if item and item.text().strip():
                try:
                    value = float(item.text())
                    multipliers.append(value)
                except ValueError:
                    continue
        
        if not multipliers:
            return
        
        # Calculate average
        avg = sum(multipliers) / len(multipliers)
        
        # Create area series for pattern
        area_series = QAreaSeries()
        line_series = QLineSeries()
        
        # Add data points
        for i, value in enumerate(multipliers):
            time = i * self.pattern_timestep
            line_series.append(time, value)
        
        # Add final point to close the pattern
        time = len(multipliers) * self.pattern_timestep
        line_series.append(time, multipliers[-1])
        
        area_series.setUpperSeries(line_series)
        area_series.setColor(QColor(100, 149, 237, 128))  # Cornflower blue with transparency
        
        self.chart.addSeries(area_series)
        
        # Create average line
        avg_series = QLineSeries()
        avg_series.append(0, avg)
        avg_series.append(time, avg)
        avg_series.setColor(QColor(255, 0, 0))
        avg_series.setName(f"Avg. = {avg:.2f}")
        
        self.chart.addSeries(avg_series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText(f"Time (Time Period = {self.pattern_timestep:.1f} hrs)")
        axis_x.setRange(0, time)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Multiplier")
        
        # Auto-scale Y axis
        min_val = min(multipliers)
        max_val = max(multipliers)
        margin = (max_val - min_val) * 0.1 if max_val != min_val else 1.0
        axis_y.setRange(min(0, min_val - margin), max_val + margin)
        
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        
        area_series.attachAxis(axis_x)
        area_series.attachAxis(axis_y)
        avg_series.attachAxis(axis_x)
        avg_series.attachAxis(axis_y)
        
        self.chart.legend().setVisible(True)
        
    def on_table_changed(self, item):
        """Handle table cell changes."""
        if item.row() == 1:  # Multiplier row
            # Check if we need to add more columns
            col = item.column()
            if col == self.table.columnCount() - 1 and item.text().strip():
                # Add new column
                new_col = self.table.columnCount()
                self.table.setColumnCount(new_col + 1)
                self.table.setItem(0, new_col, QTableWidgetItem(str(new_col + 1)))
                self.table.item(0, new_col).setFlags(Qt.ItemIsEnabled)
                self.table.setItem(1, new_col, QTableWidgetItem(""))
            
            self.plot_data()
            self.on_modified()
            
    def on_modified(self):
        """Mark the pattern as modified."""
        self.modified = True
        
    def accept_changes(self):
        """Accept and validate changes."""
        pattern_id = self.id_edit.text().strip()
        
        if not pattern_id:
            QMessageBox.warning(self, "Invalid ID", "Pattern ID cannot be empty.")
            return
        
        # Check if ID changed and ask about updating references
        if pattern_id != self.old_id and self.old_id:
            reply = QMessageBox.question(
                self,
                "Update References",
                f"Replace all references to Pattern '{self.old_id}' with '{pattern_id}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            # Note: Actual reference updating would be handled by the parent
            # This is just the UI confirmation
        
        # Emit signal with updated data
        pattern_id, multipliers, comment = self.unload_data()
        self.pattern_updated.emit(pattern_id, multipliers, comment)
        
        self.accept()
        
    def load_pattern(self):
        """Load pattern from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Pattern File",
            "",
            "Pattern Files (*.PAT);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                
            if len(lines) < 2:
                QMessageBox.warning(self, "Invalid File", "Pattern file format is invalid.")
                return
            
            # Line 0: Header (skip)
            # Line 1: Comment
            comment = lines[1].strip()
            self.comment_edit.setText(comment)
            
            # Clear existing multipliers
            for i in range(self.table.columnCount()):
                item = self.table.item(1, i)
                if item:
                    item.setText("")
            
            # Load multipliers
            col = 0
            for line in lines[2:]:
                value = line.strip()
                if value:
                    if col >= self.table.columnCount():
                        new_col = self.table.columnCount()
                        self.table.setColumnCount(new_col + 1)
                        self.table.setItem(0, new_col, QTableWidgetItem(str(new_col + 1)))
                        self.table.item(0, new_col).setFlags(Qt.ItemIsEnabled)
                        self.table.setItem(1, new_col, QTableWidgetItem(""))
                    
                    self.table.setItem(1, col, QTableWidgetItem(value))
                    col += 1
            
            self.plot_data()
            self.modified = True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load pattern file:\n{str(e)}")
            
    def save_pattern(self):
        """Save pattern to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Pattern File",
            "",
            "Pattern Files (*.PAT);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write("EPANET Pattern Data\n")
                f.write(f"{self.comment_edit.text()}\n")
                
                for i in range(self.table.columnCount()):
                    item = self.table.item(1, i)
                    if item and item.text().strip():
                        f.write(f"{item.text().strip()}\n")
            
            QMessageBox.information(self, "Success", "Pattern saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save pattern file:\n{str(e)}")
            
    def show_help(self):
        """Show help information."""
        QMessageBox.information(
            self,
            "Pattern Editor Help",
            "Pattern Editor allows you to create and edit time patterns.\n\n"
            "- Enter multiplier values in the table\n"
            "- The chart shows the pattern visualization\n"
            "- Use Load/Save to import/export pattern files\n"
            "- The red line shows the average multiplier value"
        )
