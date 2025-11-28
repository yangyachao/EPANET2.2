"""Table Options Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QGroupBox, QLineEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt

class TableOptionsDialog(QDialog):
    """Dialog for configuring table columns and filters."""
    
    def __init__(self, available_columns, visible_columns, current_filter="", parent=None):
        super().__init__(parent)
        self.available_columns = available_columns # List of (id, name) tuples
        self.visible_columns = visible_columns     # List of ids
        self.current_filter = current_filter
        
        self.setWindowTitle("Table Options")
        self.resize(400, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Columns Selection
        col_group = QGroupBox("Select Columns")
        col_layout = QVBoxLayout()
        
        self.col_list = QListWidget()
        for col_id, col_name in self.available_columns:
            item = QListWidgetItem(col_name)
            item.setData(Qt.UserRole, col_id)
            # Check if visible
            if col_id in self.visible_columns:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.col_list.addItem(item)
            
        col_layout.addWidget(self.col_list)
        col_group.setLayout(col_layout)
        layout.addWidget(col_group)
        
        # Filter
        filter_group = QGroupBox("Filter")
        filter_layout = QVBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by ID (contains):"))
        self.filter_edit = QLineEdit(self.current_filter)
        filter_layout.addWidget(self.filter_edit)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_options(self):
        """Get selected options."""
        selected_cols = []
        for i in range(self.col_list.count()):
            item = self.col_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_cols.append(item.data(Qt.UserRole))
                
        return {
            'visible_columns': selected_cols,
            'filter_text': self.filter_edit.text()
        }
