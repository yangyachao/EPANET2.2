"""Map Export Dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QPushButton, QFileDialog, QLabel, QMessageBox, QSpinBox,
    QCheckBox
)
from PySide6.QtCore import Qt

class MapExportDialog(QDialog):
    """Dialog for exporting network map as image."""
    
    def __init__(self, map_widget, parent=None):
        super().__init__(parent)
        self.map_widget = map_widget
        self.setWindowTitle("Export Map")
        self.resize(400, 300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Export the current network map view as an image file."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Form
        form = QFormLayout()
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "PDF", "SVG"])
        form.addRow("Image Format:", self.format_combo)
        
        # Resolution (for raster formats)
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(72, 600)
        self.resolution_spin.setValue(300)
        self.resolution_spin.setSuffix(" DPI")
        form.addRow("Resolution:", self.resolution_spin)
        
        # Quality (for JPEG)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(90)
        self.quality_spin.setSuffix("%")
        form.addRow("JPEG Quality:", self.quality_spin)
        
        layout.addLayout(form)
        
        # Options
        self.include_legend_check = QCheckBox("Include Legend")
        self.include_legend_check.setChecked(True)
        layout.addWidget(self.include_legend_check)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self.export_map)
        btn_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Connect format change to update UI
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.on_format_changed(self.format_combo.currentText())
        
    def on_format_changed(self, format_name):
        """Update UI based on selected format."""
        # Enable/disable quality for JPEG
        self.quality_spin.setEnabled(format_name == "JPEG")
        
        # Enable/disable resolution for raster formats
        is_raster = format_name in ["PNG", "JPEG"]
        self.resolution_spin.setEnabled(is_raster)
        
    def export_map(self):
        """Export map to image file."""
        format_name = self.format_combo.currentText()
        
        # Determine file filter
        filters = {
            "PNG": "PNG Images (*.png)",
            "JPEG": "JPEG Images (*.jpg *.jpeg)",
            "PDF": "PDF Documents (*.pdf)",
            "SVG": "SVG Images (*.svg)"
        }
        
        file_filter = filters.get(format_name, "All Files (*.*)")
        
        # Get save file path
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Map",
            "",
            file_filter
        )
        
        if not filepath:
            return
        
        # Ensure correct extension
        extensions = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "PDF": ".pdf",
            "SVG": ".svg"
        }
        ext = extensions.get(format_name, "")
        if not any(filepath.endswith(e) for e in [ext, ext.upper()]):
            filepath += ext
        
        try:
            self._export_to_file(filepath, format_name)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Map exported successfully to:\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export map:\n{str(e)}"
            )
    
    def _export_to_file(self, filepath, format_name):
        """Export map to file in specified format."""
        from PySide6.QtGui import QPainter, QImage, QPdfWriter
        from PySide6.QtSvg import QSvgGenerator
        from PySide6.QtCore import QRectF, QSizeF
        
        scene = self.map_widget.scene
        
        # Get scene rect
        scene_rect = scene.sceneRect()
        
        if format_name == "PNG":
            # Export as PNG
            dpi = self.resolution_spin.value()
            scale_factor = dpi / 96.0  # 96 DPI is default
            
            image = QImage(
                int(scene_rect.width() * scale_factor),
                int(scene_rect.height() * scale_factor),
                QImage.Format_ARGB32
            )
            image.fill(Qt.white)
            
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            scene.render(painter, QRectF(), scene_rect)
            painter.end()
            
            image.save(filepath, "PNG")
            
        elif format_name == "JPEG":
            # Export as JPEG
            dpi = self.resolution_spin.value()
            scale_factor = dpi / 96.0
            quality = self.quality_spin.value()
            
            image = QImage(
                int(scene_rect.width() * scale_factor),
                int(scene_rect.height() * scale_factor),
                QImage.Format_RGB32
            )
            image.fill(Qt.white)
            
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            scene.render(painter, QRectF(), scene_rect)
            painter.end()
            
            image.save(filepath, "JPEG", quality)
            
        elif format_name == "PDF":
            # Export as PDF
            pdf_writer = QPdfWriter(filepath)
            pdf_writer.setPageSize(QSizeF(scene_rect.size()))
            pdf_writer.setPageMargins(QMarginsF(0, 0, 0, 0))
            
            painter = QPainter(pdf_writer)
            scene.render(painter)
            painter.end()
            
        elif format_name == "SVG":
            # Export as SVG
            svg_gen = QSvgGenerator()
            svg_gen.setFileName(filepath)
            svg_gen.setSize(scene_rect.size().toSize())
            svg_gen.setViewBox(scene_rect)
            
            painter = QPainter(svg_gen)
            scene.render(painter)
            painter.end()
