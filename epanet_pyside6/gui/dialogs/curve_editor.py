"""Curve Editor Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QScatterSeries, QValueAxis
from PySide6.QtGui import QPainter, QColor
from typing import Optional, List, Tuple
import math


class CurveEditor(QDialog):
    """Dialog for editing X-Y curves."""
    
    curve_updated = Signal(str, str, list, str)  # id, curve_type, points, comment
    
    # Curve types
    CURVE_TYPES = ["Volume", "Pump", "Efficiency", "Headloss"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.curve_id = ""
        self.old_id = ""
        self.curve_type = "Pump"
        self.points = []
        self.comment = ""
        self.modified = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Curve Editor")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # ID, Type, and Comment section
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Curve ID:"), 0, 0)
        self.id_edit = QLineEdit()
        self.id_edit.setMaxLength(31)
        self.id_edit.textChanged.connect(self.on_modified)
        info_layout.addWidget(self.id_edit, 0, 1)
        
        info_layout.addWidget(QLabel("Curve Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.CURVE_TYPES)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        info_layout.addWidget(self.type_combo, 1, 1)
        
        info_layout.addWidget(QLabel("Comment:"), 2, 0)
        self.comment_edit = QLineEdit()
        self.comment_edit.textChanged.connect(self.on_modified)
        info_layout.addWidget(self.comment_edit, 2, 1)
        
        layout.addLayout(info_layout)
        
        # Data table
        self.table = QTableWidget()
        self.table.setRowCount(50)  # Max 50 points
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["X", "Y"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemChanged.connect(self.on_table_changed)
        layout.addWidget(self.table)
        
        # Chart
        self.chart = QChart()
        self.chart.setTitle("Curve Visualization")
        self.chart.legend().hide()
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(200)
        layout.addWidget(self.chart_view)
        
        # Pump curve equation label
        self.equation_label = QLabel("")
        self.equation_label.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
        layout.addWidget(self.equation_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load...")
        load_btn.clicked.connect(self.load_curve)
        button_layout.addWidget(load_btn)
        
        save_btn = QPushButton("Save...")
        save_btn.clicked.connect(self.save_curve)
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
        
    def load_data(self, curve_id: str, curve_type: str, points: List[Tuple[float, float]], comment: str = ""):
        """Load curve data into the dialog.
        
        Args:
            curve_id: Curve ID
            curve_type: Type of curve (Volume, Pump, Efficiency, Headloss)
            points: List of (x, y) tuples
            comment: Curve comment/description
        """
        self.curve_id = curve_id
        self.old_id = curve_id
        self.curve_type = curve_type
        self.points = points.copy()
        self.comment = comment
        
        # Update UI
        self.id_edit.setText(curve_id)
        self.comment_edit.setText(comment)
        
        # Set curve type
        if curve_type in self.CURVE_TYPES:
            self.type_combo.setCurrentText(curve_type)
        
        # Load points
        for i, (x, y) in enumerate(points):
            if i < self.table.rowCount():
                self.table.setItem(i, 0, QTableWidgetItem(str(x)))
                self.table.setItem(i, 1, QTableWidgetItem(str(y)))
        
        self.update_axis_labels()
        self.plot_data()
        self.modified = False
        
    def unload_data(self) -> tuple:
        """Get the current curve data.
        
        Returns:
            Tuple of (curve_id, curve_type, points, comment)
        """
        curve_id = self.id_edit.text().strip()
        curve_type = self.type_combo.currentText()
        comment = self.comment_edit.text()
        
        points = []
        for i in range(self.table.rowCount()):
            x_item = self.table.item(i, 0)
            y_item = self.table.item(i, 1)
            
            if x_item and y_item and x_item.text().strip() and y_item.text().strip():
                try:
                    x = float(x_item.text())
                    y = float(y_item.text())
                    points.append((x, y))
                except ValueError:
                    pass
        
        return curve_id, curve_type, points, comment
        
    def on_type_changed(self, curve_type: str):
        """Handle curve type change."""
        self.update_axis_labels()
        self.plot_data()
        self.on_modified()
        
    def update_axis_labels(self):
        """Update table headers based on curve type."""
        curve_type = self.type_combo.currentText()
        
        if curve_type == "Volume":
            self.table.setHorizontalHeaderLabels(["Height", "Volume"])
        elif curve_type == "Pump":
            self.table.setHorizontalHeaderLabels(["Flow", "Head"])
        elif curve_type == "Efficiency":
            self.table.setHorizontalHeaderLabels(["Flow", "Efficiency"])
        elif curve_type == "Headloss":
            self.table.setHorizontalHeaderLabels(["Flow", "Headloss"])
            
    def plot_data(self):
        """Plot the curve data on the chart."""
        self.chart.removeAllSeries()
        self.equation_label.setText("")
        
        # Get points from table
        points = []
        for i in range(self.table.rowCount()):
            x_item = self.table.item(i, 0)
            y_item = self.table.item(i, 1)
            
            if x_item and y_item and x_item.text().strip() and y_item.text().strip():
                try:
                    x = float(x_item.text())
                    y = float(y_item.text())
                    points.append((x, y))
                except ValueError:
                    continue
        
        if not points:
            return
        
        curve_type = self.type_combo.currentText()
        
        # For pump curves with 1 or 3 points, fit power function
        if curve_type == "Pump" and (len(points) == 1 or len(points) == 3):
            fitted_points = self.fit_pump_curve(points)
            if fitted_points:
                # Plot fitted curve
                line_series = QLineSeries()
                for x, y in fitted_points:
                    line_series.append(x, y)
                line_series.setColor(QColor(0, 0, 255))
                self.chart.addSeries(line_series)
                
                # Plot original points
                scatter_series = QScatterSeries()
                for x, y in points:
                    scatter_series.append(x, y)
                scatter_series.setMarkerSize(10)
                scatter_series.setColor(QColor(255, 0, 0))
                self.chart.addSeries(scatter_series)
                
                points_to_use = fitted_points
            else:
                points_to_use = points
        else:
            # Plot as line with points
            line_series = QLineSeries()
            for x, y in points:
                line_series.append(x, y)
            line_series.setColor(QColor(0, 0, 255))
            self.chart.addSeries(line_series)
            points_to_use = points
        
        # Create axes
        if points_to_use:
            x_values = [p[0] for p in points_to_use]
            y_values = [p[1] for p in points_to_use]
            
            axis_x = QValueAxis()
            x_label = self.table.horizontalHeaderItem(0).text()
            axis_x.setTitleText(x_label)
            axis_x.setRange(min(x_values), max(x_values))
            
            axis_y = QValueAxis()
            y_label = self.table.horizontalHeaderItem(1).text()
            axis_y.setTitleText(y_label)
            axis_y.setRange(min(0, min(y_values)), max(y_values) * 1.1)
            
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            
            for series in self.chart.series():
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)
                
    def fit_pump_curve(self, points: List[Tuple[float, float]]) -> Optional[List[Tuple[float, float]]]:
        """Fit pump curve to power function: Head = a + b * Flow^c
        
        Args:
            points: List of (flow, head) points (1 or 3 points)
            
        Returns:
            List of fitted points or None if fitting failed
        """
        TINY = 1e-6
        
        if len(points) == 1:
            q1, h1 = points[0]
            q0 = 0.0
            h0 = 1.33334 * h1
            q2 = 2.0 * q1
            h2 = 0.0
        elif len(points) == 3:
            q0, h0 = points[0]
            q1, h1 = points[1]
            q2, h2 = points[2]
        else:
            return None
        
        # Validate inputs
        if (h0 < TINY or h0 - h1 < TINY or h1 - h2 < TINY or 
            q1 - q0 < TINY or q2 - q1 < TINY):
            self.equation_label.setText("Illegal pump curve.")
            return None
        
        # Iterative fitting
        a = h0
        b = 0.0
        c = 1.0
        
        for iteration in range(5):
            h4 = a - h1
            h5 = a - h2
            
            try:
                c = math.log(h5 / h4) / math.log(q2 / q1)
            except (ValueError, ZeroDivisionError):
                self.equation_label.setText("Illegal pump curve.")
                return None
            
            if c <= 0.0 or c > 20.0:
                self.equation_label.setText("Illegal pump curve.")
                return None
            
            b = -h4 / (q1 ** c)
            
            if b >= 0.0:
                self.equation_label.setText("Illegal pump curve.")
                return None
            
            a1 = h0 - b * (q0 ** c)
            
            if abs(a1 - a) < 0.01:
                break
            
            a = a1
        
        # Generate fitted curve points
        h4 = -a / b
        h5 = 1.0 / c
        q_max = h4 ** h5
        
        fitted_points = []
        n_points = 25
        for i in range(n_points):
            q = (i / (n_points - 1)) * q_max
            h = a + b * (q ** c)
            fitted_points.append((q, h))
        
        # Display equation
        self.equation_label.setText(f"Head = {a:.2f} + {b:.4g}(Flow)^{c:.2f}")
        
        return fitted_points
        
    def on_table_changed(self, item):
        """Handle table cell changes."""
        self.plot_data()
        self.on_modified()
        
    def on_modified(self):
        """Mark the curve as modified."""
        self.modified = True
        
    def accept_changes(self):
        """Accept and validate changes."""
        curve_id = self.id_edit.text().strip()
        
        if not curve_id:
            QMessageBox.warning(self, "Invalid ID", "Curve ID cannot be empty.")
            return
        
        # Get points and validate
        _, _, points, _ = self.unload_data()
        
        if len(points) > 1:
            # Check if X values are in ascending order
            x_values = [p[0] for p in points]
            for i in range(1, len(x_values)):
                if x_values[i] <= x_values[i-1]:
                    QMessageBox.warning(
                        self,
                        "Invalid Data",
                        f"{self.table.horizontalHeaderItem(0).text()} values are not in ascending order."
                    )
                    return
        
        # For pump curves, validate
        if self.type_combo.currentText() == "Pump" and (len(points) == 1 or len(points) == 3):
            fitted = self.fit_pump_curve(points)
            if not fitted:
                reply = QMessageBox.question(
                    self,
                    "Invalid Pump Curve",
                    "Illegal pump curve. Continue editing?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    return
        
        # Emit signal with updated data
        curve_id, curve_type, points, comment = self.unload_data()
        self.curve_updated.emit(curve_id, curve_type, points, comment)
        
        self.accept()
        
    def load_curve(self):
        """Load curve from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Curve File",
            "",
            "Curve Files (*.CRV);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                
            if len(lines) < 3:
                QMessageBox.warning(self, "Invalid File", "Curve file format is invalid.")
                return
            
            # Line 0: Header (skip)
            # Line 1: Curve type
            curve_type = lines[1].strip()
            if curve_type in self.CURVE_TYPES:
                self.type_combo.setCurrentText(curve_type)
            
            # Line 2: Comment
            comment = lines[2].strip()
            self.comment_edit.setText(comment)
            
            # Clear existing data
            for i in range(self.table.rowCount()):
                self.table.setItem(i, 0, QTableWidgetItem(""))
                self.table.setItem(i, 1, QTableWidgetItem(""))
            
            # Load points
            row = 0
            for line in lines[3:]:
                parts = line.strip().split()
                if len(parts) >= 2 and row < self.table.rowCount():
                    self.table.setItem(row, 0, QTableWidgetItem(parts[0]))
                    self.table.setItem(row, 1, QTableWidgetItem(parts[1]))
                    row += 1
            
            self.plot_data()
            self.modified = True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load curve file:\n{str(e)}")
            
    def save_curve(self):
        """Save curve to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Curve File",
            "",
            "Curve Files (*.CRV);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write("EPANET Curve Data\n")
                f.write(f"{self.type_combo.currentText()}\n")
                f.write(f"{self.comment_edit.text()}\n")
                
                for i in range(self.table.rowCount()):
                    x_item = self.table.item(i, 0)
                    y_item = self.table.item(i, 1)
                    
                    if x_item and y_item and x_item.text().strip() and y_item.text().strip():
                        f.write(f"{x_item.text().strip()}  {y_item.text().strip()}\n")
            
            QMessageBox.information(self, "Success", "Curve saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save curve file:\n{str(e)}")
            
    def show_help(self):
        """Show help information."""
        QMessageBox.information(
            self,
            "Curve Editor Help",
            "Curve Editor allows you to create and edit X-Y curves.\n\n"
            "- Select curve type (Volume, Pump, Efficiency, Headloss)\n"
            "- Enter X-Y data points in the table\n"
            "- X values must be in ascending order\n"
            "- For pump curves, 1 or 3 points will be fitted to a power function\n"
            "- Use Load/Save to import/export curve files"
        )
