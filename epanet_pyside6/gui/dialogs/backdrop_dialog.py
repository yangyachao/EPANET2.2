"""Dialog for configuring backdrop image."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QGroupBox, QDialogButtonBox
)
from PySide6.QtCore import Qt

class BackdropDialog(QDialog):
    """Dialog for loading and aligning backdrop image."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.image_path = ""
        self.setWindowTitle("Backdrop Selection")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Image File Selection
        file_group = QGroupBox("Backdrop Image File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(self.file_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_group)
        
        # Alignment Coordinates
        coord_group = QGroupBox("Map Alignment")
        coord_layout = QVBoxLayout(coord_group)
        
        # Upper Left
        ul_layout = QHBoxLayout()
        ul_layout.addWidget(QLabel("Upper Left X:"))
        self.ul_x = QLineEdit()
        ul_layout.addWidget(self.ul_x)
        ul_layout.addWidget(QLabel("Y:"))
        self.ul_y = QLineEdit()
        ul_layout.addWidget(self.ul_y)
        coord_layout.addLayout(ul_layout)
        
        # Lower Right
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel("Lower Right X:"))
        self.lr_x = QLineEdit()
        lr_layout.addWidget(self.lr_x)
        lr_layout.addWidget(QLabel("Y:"))
        self.lr_y = QLineEdit()
        lr_layout.addWidget(self.lr_y)
        coord_layout.addLayout(lr_layout)
        
        layout.addWidget(coord_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Backdrop Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        if filename:
            self.image_path = filename
            self.file_edit.setText(filename)
            
    def get_data(self):
        """Return (image_path, ul_x, ul_y, lr_x, lr_y)."""
        try:
            ul_x = float(self.ul_x.text()) if self.ul_x.text() else 0.0
            ul_y = float(self.ul_y.text()) if self.ul_y.text() else 0.0
            lr_x = float(self.lr_x.text()) if self.lr_x.text() else 0.0
            lr_y = float(self.lr_y.text()) if self.lr_y.text() else 0.0
            return self.image_path, ul_x, ul_y, lr_x, lr_y
        except ValueError:
            return self.image_path, 0.0, 0.0, 0.0, 0.0
            
    def set_data(self, path, ul_x, ul_y, lr_x, lr_y):
        """Set initial data."""
        self.image_path = path
        self.file_edit.setText(path)
        self.ul_x.setText(str(ul_x))
        self.ul_y.setText(str(ul_y))
        self.lr_x.setText(str(lr_x))
        self.lr_y.setText(str(lr_y))
