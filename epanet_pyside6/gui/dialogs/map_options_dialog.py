"""Map Options dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QPushButton, QWidget, QLabel, QSpinBox, QCheckBox, QGroupBox,
    QRadioButton, QButtonGroup, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class MapOptionsDialog(QDialog):
    """Dialog for configuring map display options."""
    
    options_updated = Signal(dict)  # Emits updated options
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Options")
        self.resize(600, 450)
        
        self.options_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QHBoxLayout(self)
        
        # Left side: Category list
        self.category_list = QListWidget()
        self.category_list.addItems([
            "Nodes",
            "Links",
            "Labels",
            "Notation",
            "Symbols",
            "Zoom Levels",
            "Background"
        ])
        self.category_list.setMaximumWidth(150)
        self.category_list.currentRowChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_list)
        
        # Right side: Stacked widget for pages
        self.pages = QStackedWidget()
        
        # Create pages
        self.pages.addWidget(self.create_nodes_page())
        self.pages.addWidget(self.create_links_page())
        self.pages.addWidget(self.create_labels_page())
        self.pages.addWidget(self.create_notation_page())
        self.pages.addWidget(self.create_symbols_page())
        self.pages.addWidget(self.create_zoom_levels_page())
        self.pages.addWidget(self.create_background_page())
        
        layout.addWidget(self.pages, 1)
        
        # Bottom buttons
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.help_button = QPushButton("Help")
        button_layout.addWidget(self.help_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # Select first category
        self.category_list.setCurrentRow(0)
        
    def create_nodes_page(self):
        """Create Nodes options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Node size
        size_group = QGroupBox("Node Size")
        size_layout = QVBoxLayout()
        
        size_control = QHBoxLayout()
        size_control.addWidget(QLabel("Size:"))
        self.node_size_spin = QSpinBox()
        self.node_size_spin.setRange(1, 10)
        self.node_size_spin.setValue(3)
        size_control.addWidget(self.node_size_spin)
        size_control.addStretch()
        size_layout.addLayout(size_control)
        
        self.size_nodes_by_value = QCheckBox("Size nodes by value")
        size_layout.addWidget(self.size_nodes_by_value)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Display options
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout()
        
        self.display_node_border = QCheckBox("Display node border")
        self.display_node_border.setChecked(True)
        display_layout.addWidget(self.display_node_border)
        
        self.display_junction_symbols = QCheckBox("Display junction symbols")
        self.display_junction_symbols.setChecked(True)
        display_layout.addWidget(self.display_junction_symbols)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        return widget
        
    def create_links_page(self):
        """Create Links options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Link size
        size_group = QGroupBox("Link Size")
        size_layout = QVBoxLayout()
        
        size_control = QHBoxLayout()
        size_control.addWidget(QLabel("Size:"))
        self.link_size_spin = QSpinBox()
        self.link_size_spin.setRange(1, 10)
        self.link_size_spin.setValue(2)
        size_control.addWidget(self.link_size_spin)
        size_control.addStretch()
        size_layout.addLayout(size_control)
        
        self.size_links_by_value = QCheckBox("Size links by value")
        size_layout.addWidget(self.size_links_by_value)
        
        self.display_link_border = QCheckBox("Display link border")
        size_layout.addWidget(self.display_link_border)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Arrow options
        arrow_group = QGroupBox("Arrows")
        arrow_layout = QVBoxLayout()
        
        arrow_layout.addWidget(QLabel("Arrow Style:"))
        self.arrow_style_group = QButtonGroup()
        
        self.arrow_none = QRadioButton("None")
        self.arrow_style_group.addButton(self.arrow_none, 0)
        arrow_layout.addWidget(self.arrow_none)
        
        self.arrow_open = QRadioButton("Open")
        self.arrow_style_group.addButton(self.arrow_open, 1)
        arrow_layout.addWidget(self.arrow_open)
        
        self.arrow_closed = QRadioButton("Closed")
        self.arrow_style_group.addButton(self.arrow_closed, 2)
        arrow_layout.addWidget(self.arrow_closed)
        
        self.arrow_filled = QRadioButton("Filled")
        self.arrow_style_group.addButton(self.arrow_filled, 3)
        arrow_layout.addWidget(self.arrow_filled)
        
        self.arrow_none.setChecked(True)
        
        arrow_size_layout = QHBoxLayout()
        arrow_size_layout.addWidget(QLabel("Arrow Size:"))
        self.arrow_size_spin = QSpinBox()
        self.arrow_size_spin.setRange(1, 10)
        self.arrow_size_spin.setValue(5)
        arrow_size_layout.addWidget(self.arrow_size_spin)
        arrow_size_layout.addStretch()
        arrow_layout.addLayout(arrow_size_layout)
        
        arrow_group.setLayout(arrow_layout)
        layout.addWidget(arrow_group)
        
        layout.addStretch()
        return widget
        
    def create_labels_page(self):
        """Create Labels options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label_group = QGroupBox("Label Options")
        label_layout = QVBoxLayout()
        
        self.display_labels = QCheckBox("Display labels")
        self.display_labels.setChecked(True)
        label_layout.addWidget(self.display_labels)
        
        self.labels_transparent = QCheckBox("Transparent labels")
        label_layout.addWidget(self.labels_transparent)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Label zoom level:"))
        self.label_zoom_spin = QSpinBox()
        self.label_zoom_spin.setRange(0, 100)
        self.label_zoom_spin.setValue(0)
        self.label_zoom_spin.setSuffix("%")
        zoom_layout.addWidget(self.label_zoom_spin)
        zoom_layout.addStretch()
        label_layout.addLayout(zoom_layout)
        
        label_group.setLayout(label_layout)
        layout.addWidget(label_group)
        
        layout.addStretch()
        return widget
        
    def create_notation_page(self):
        """Create Notation options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        notation_group = QGroupBox("Notation Options")
        notation_layout = QVBoxLayout()
        
        self.display_node_ids = QCheckBox("Display node IDs")
        notation_layout.addWidget(self.display_node_ids)
        
        self.display_node_values = QCheckBox("Display node values")
        notation_layout.addWidget(self.display_node_values)
        
        self.display_link_ids = QCheckBox("Display link IDs")
        notation_layout.addWidget(self.display_link_ids)
        
        self.display_link_values = QCheckBox("Display link values")
        notation_layout.addWidget(self.display_link_values)
        
        self.notation_transparent = QCheckBox("Transparent notation")
        notation_layout.addWidget(self.notation_transparent)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font size:"))
        self.notation_font_size = QSpinBox()
        self.notation_font_size.setRange(6, 24)
        self.notation_font_size.setValue(8)
        font_layout.addWidget(self.notation_font_size)
        font_layout.addStretch()
        notation_layout.addLayout(font_layout)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Notation zoom level:"))
        self.notation_zoom_spin = QSpinBox()
        self.notation_zoom_spin.setRange(0, 100)
        self.notation_zoom_spin.setValue(0)
        self.notation_zoom_spin.setSuffix("%")
        zoom_layout.addWidget(self.notation_zoom_spin)
        zoom_layout.addStretch()
        notation_layout.addLayout(zoom_layout)
        
        notation_group.setLayout(notation_layout)
        layout.addWidget(notation_group)
        
        layout.addStretch()
        return widget
        
    def create_symbols_page(self):
        """Create Symbols options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        symbol_group = QGroupBox("Symbol Display")
        symbol_layout = QVBoxLayout()
        
        self.display_tank_symbols = QCheckBox("Display tank symbols")
        self.display_tank_symbols.setChecked(True)
        symbol_layout.addWidget(self.display_tank_symbols)
        
        self.display_pump_symbols = QCheckBox("Display pump symbols")
        self.display_pump_symbols.setChecked(True)
        symbol_layout.addWidget(self.display_pump_symbols)
        
        self.display_valve_symbols = QCheckBox("Display valve symbols")
        self.display_valve_symbols.setChecked(True)
        symbol_layout.addWidget(self.display_valve_symbols)
        
        self.display_emitter_symbols = QCheckBox("Display emitter symbols")
        self.display_emitter_symbols.setChecked(True)
        symbol_layout.addWidget(self.display_emitter_symbols)
        
        self.display_source_symbols = QCheckBox("Display source symbols")
        self.display_source_symbols.setChecked(True)
        symbol_layout.addWidget(self.display_source_symbols)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Symbol zoom level:"))
        self.symbol_zoom_spin = QSpinBox()
        self.symbol_zoom_spin.setRange(0, 100)
        self.symbol_zoom_spin.setValue(0)
        self.symbol_zoom_spin.setSuffix("%")
        zoom_layout.addWidget(self.symbol_zoom_spin)
        zoom_layout.addStretch()
        symbol_layout.addLayout(zoom_layout)
        
        symbol_group.setLayout(symbol_layout)
        layout.addWidget(symbol_group)
        
        layout.addStretch()
        return widget
        
    def create_zoom_levels_page(self):
        """Create Zoom Levels options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Zoom levels control when elements become visible:"))
        
        zoom_group = QGroupBox("Zoom Level Settings")
        zoom_layout = QVBoxLayout()
        
        # Labels zoom
        label_zoom = QHBoxLayout()
        label_zoom.addWidget(QLabel("Labels:"))
        label_zoom.addWidget(self.label_zoom_spin)
        label_zoom.addStretch()
        zoom_layout.addLayout(label_zoom)
        
        # Symbols zoom
        symbol_zoom = QHBoxLayout()
        symbol_zoom.addWidget(QLabel("Symbols:"))
        symbol_zoom.addWidget(self.symbol_zoom_spin)
        symbol_zoom.addStretch()
        zoom_layout.addLayout(symbol_zoom)
        
        # Notation zoom
        notation_zoom = QHBoxLayout()
        notation_zoom.addWidget(QLabel("Notation:"))
        notation_zoom.addWidget(self.notation_zoom_spin)
        notation_zoom.addStretch()
        zoom_layout.addLayout(notation_zoom)
        
        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)
        
        layout.addStretch()
        return widget
        
    def create_background_page(self):
        """Create Background options page."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        bg_group = QGroupBox("Background Color")
        bg_layout = QVBoxLayout()
        
        self.bg_color_group = QButtonGroup()
        
        # Color options
        colors = [
            ("White", QColor(255, 255, 255)),
            ("Light Gray", QColor(224, 224, 224)),
            ("Gray", QColor(192, 192, 192)),
            ("Black", QColor(0, 0, 0))
        ]
        
        for i, (name, color) in enumerate(colors):
            color_layout = QHBoxLayout()
            
            radio = QRadioButton(name)
            self.bg_color_group.addButton(radio, i)
            color_layout.addWidget(radio)
            
            # Color preview
            preview = QFrame()
            preview.setFrameStyle(QFrame.Box | QFrame.Plain)
            preview.setFixedSize(40, 20)
            preview.setStyleSheet(f"background-color: {color.name()};")
            color_layout.addWidget(preview)
            
            color_layout.addStretch()
            bg_layout.addLayout(color_layout)
        
        # Default to white
        self.bg_color_group.button(0).setChecked(True)
        
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        layout.addStretch()
        return widget
        
    def on_category_changed(self, index):
        """Handle category selection change."""
        self.pages.setCurrentIndex(index)
        
    def load_options(self, options):
        """Load options into dialog."""
        self.options_data = options.copy()
        
        # Nodes
        self.node_size_spin.setValue(options.get('node_size', 3))
        self.size_nodes_by_value.setChecked(options.get('size_nodes_by_value', False))
        self.display_node_border.setChecked(options.get('display_node_border', True))
        self.display_junction_symbols.setChecked(options.get('display_junction_symbols', True))
        
        # Links
        self.link_size_spin.setValue(options.get('link_size', 2))
        self.size_links_by_value.setChecked(options.get('size_links_by_value', False))
        self.display_link_border.setChecked(options.get('display_link_border', False))
        
        arrow_style = options.get('arrow_style', 0)
        self.arrow_style_group.button(arrow_style).setChecked(True)
        self.arrow_size_spin.setValue(options.get('arrow_size', 5))
        
        # Labels
        self.display_labels.setChecked(options.get('display_labels', True))
        self.labels_transparent.setChecked(options.get('labels_transparent', False))
        self.label_zoom_spin.setValue(options.get('label_zoom', 0))
        
        # Notation
        self.display_node_ids.setChecked(options.get('display_node_ids', False))
        self.display_node_values.setChecked(options.get('display_node_values', False))
        self.display_link_ids.setChecked(options.get('display_link_ids', False))
        self.display_link_values.setChecked(options.get('display_link_values', False))
        self.notation_transparent.setChecked(options.get('notation_transparent', False))
        self.notation_font_size.setValue(options.get('notation_font_size', 8))
        self.notation_zoom_spin.setValue(options.get('notation_zoom', 0))
        
        # Symbols
        self.display_tank_symbols.setChecked(options.get('display_tank_symbols', True))
        self.display_pump_symbols.setChecked(options.get('display_pump_symbols', True))
        self.display_valve_symbols.setChecked(options.get('display_valve_symbols', True))
        self.display_emitter_symbols.setChecked(options.get('display_emitter_symbols', True))
        self.display_source_symbols.setChecked(options.get('display_source_symbols', True))
        self.symbol_zoom_spin.setValue(options.get('symbol_zoom', 0))
        
        # Background
        bg_color_index = options.get('background_color_index', 0)
        self.bg_color_group.button(bg_color_index).setChecked(True)
        
    def get_options(self):
        """Get current options from dialog."""
        return {
            # Nodes
            'node_size': self.node_size_spin.value(),
            'size_nodes_by_value': self.size_nodes_by_value.isChecked(),
            'display_node_border': self.display_node_border.isChecked(),
            'display_junction_symbols': self.display_junction_symbols.isChecked(),
            
            # Links
            'link_size': self.link_size_spin.value(),
            'size_links_by_value': self.size_links_by_value.isChecked(),
            'display_link_border': self.display_link_border.isChecked(),
            'arrow_style': self.arrow_style_group.checkedId(),
            'arrow_size': self.arrow_size_spin.value(),
            
            # Labels
            'display_labels': self.display_labels.isChecked(),
            'labels_transparent': self.labels_transparent.isChecked(),
            'label_zoom': self.label_zoom_spin.value(),
            
            # Notation
            'display_node_ids': self.display_node_ids.isChecked(),
            'display_node_values': self.display_node_values.isChecked(),
            'display_link_ids': self.display_link_ids.isChecked(),
            'display_link_values': self.display_link_values.isChecked(),
            'notation_transparent': self.notation_transparent.isChecked(),
            'notation_font_size': self.notation_font_size.value(),
            'notation_zoom': self.notation_zoom_spin.value(),
            
            # Symbols
            'display_tank_symbols': self.display_tank_symbols.isChecked(),
            'display_pump_symbols': self.display_pump_symbols.isChecked(),
            'display_valve_symbols': self.display_valve_symbols.isChecked(),
            'display_emitter_symbols': self.display_emitter_symbols.isChecked(),
            'display_source_symbols': self.display_source_symbols.isChecked(),
            'symbol_zoom': self.symbol_zoom_spin.value(),
            
            # Background
            'background_color_index': self.bg_color_group.checkedId()
        }
        
    def accept(self):
        """Save options and close dialog."""
        options = self.get_options()
        self.options_updated.emit(options)
        super().accept()
