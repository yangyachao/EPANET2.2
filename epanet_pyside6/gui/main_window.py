"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QStatusBar, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMenu, QMessageBox, QInputDialog, QFileDialog,
    QToolBar, QStyle, QDialog
)
from PySide6.QtCore import Qt, QSize, QSettings, QPointF, QRectF
from PySide6.QtGui import QAction, QKeySequence, QColor, QIcon, QPixmap, QPainter, QFont, QPolygonF, QPainterPath, QPen, QImage
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.project import EPANETProject
from gui.widgets import BrowserWidget, PropertyEditor, MapWidget, OverviewMapWidget


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.project = EPANETProject()
        self.settings = QSettings("US EPA", "EPANET 2.2")
        
        # Recent files
        self.recent_files = []
        self.max_recent_files = 5
        self.recent_file_actions = []
        self.load_recent_files()
        
        self.setup_ui()
        self.create_menus()
        self.create_toolbars()
        self.create_dock_widgets()
        self.create_status_bar()
        self.restore_settings()
        
        # Start with new project
        self.new_project()
    
    def load_recent_files(self):
        """Load recent files from settings."""
        self.recent_files = self.settings.value("recentFiles", [])
        # Ensure it's a list of strings
        if not isinstance(self.recent_files, list):
            self.recent_files = []
            
    def save_recent_files(self):
        """Save recent files to settings."""
        self.settings.setValue("recentFiles", self.recent_files)
        
    def add_recent_file(self, filename):
        """Add file to recent files list."""
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        
        self.recent_files.insert(0, filename)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
            
        self.save_recent_files()
        self.update_recent_files_menu()
        
    def update_recent_files_menu(self):
        """Update recent files menu items."""
        # Clear existing actions
        for action in self.recent_file_actions:
            self.file_menu.removeAction(action)
            
        self.recent_file_actions.clear()
        
        # Add separator if we have recent files
        if self.recent_files and self.exit_action:
            # Find position before exit action
            self.file_menu.insertSeparator(self.exit_action)
            
            for i, filename in enumerate(self.recent_files):
                text = f"&{i+1} {os.path.basename(filename)}"
                action = QAction(text, self)
                action.setData(filename)
                action.triggered.connect(lambda checked=False, f=filename: self.open_recent_file(f))
                self.file_menu.insertAction(self.exit_action, action)
                self.recent_file_actions.append(action)
                
            self.file_menu.insertSeparator(self.exit_action)
            
    def open_recent_file(self, filename):
        """Open a recent file."""
        if not self.check_save_changes():
            return
            
        if not os.path.exists(filename):
            QMessageBox.warning(self, "File Not Found", f"File not found:\n{filename}")
            self.recent_files.remove(filename)
            self.save_recent_files()
            self.update_recent_files_menu()
            return
            
        try:
            self.project.open_project(filename)
            self.browser_widget.refresh()
            self.property_editor.set_object(None)
            
            self.map_widget.scene.load_network()
            self.map_widget.scene.update_scene_rect()
            self.map_widget.fit_network()
            
            self.update_title()
            self.status_bar.showMessage(f"Opened {filename}")
            
            # Move to top of list
            self.add_recent_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")
    
    def setup_ui(self):
        """Setup main UI components."""
        self.setWindowTitle("EPANET 2.2 - PySide6")
        self.resize(1200, 800)
        
        # Create MDI area for        # MDI Area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        # Create Map Window
        self.map_widget = MapWidget(self.project)
        self.map_widget.scene.selectionChanged.connect(self.on_map_selection_changed)
        self.map_widget.options_requested.connect(self.show_map_options)
        self.map_subwindow = self.mdi_area.addSubWindow(self.map_widget)
        self.map_subwindow.setWindowTitle("Network Map")
        self.map_subwindow.showMaximized()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)
    
    def create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        self.file_menu = menubar.addMenu("&File")
        file_menu = self.file_menu
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        self.file_menu.addSeparator()
        
        # Import Submenu
        import_menu = self.file_menu.addMenu("&Import")
        
        import_network_action = QAction("&Network...", self)
        import_network_action.triggered.connect(self.import_network)
        import_menu.addAction(import_network_action)
        
        import_map_action = QAction("&Map...", self)
        import_map_action.triggered.connect(self.import_map)
        import_menu.addAction(import_map_action)
        
        import_scenario_action = QAction("&Scenario...", self)
        import_scenario_action.triggered.connect(self.import_scenario)
        import_menu.addAction(import_scenario_action)
        
        # Export Submenu
        export_menu = self.file_menu.addMenu("&Export")
        
        export_network_action = QAction("&Network...", self)
        export_network_action.triggered.connect(self.export_network)
        export_menu.addAction(export_network_action)
        
        export_map_action = QAction("&Map...", self)
        export_map_action.triggered.connect(self.export_map)
        export_menu.addAction(export_map_action)
        
        export_scenario_action = QAction("&Scenario...", self)
        export_scenario_action.triggered.connect(self.export_scenario)
        export_menu.addAction(export_scenario_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Initialize recent files menu
        self.update_recent_files_menu()
        
        # Project Menu
        project_menu = menubar.addMenu("&Project")
        
        summary_action = QAction("&Summary...", self)
        summary_action.triggered.connect(self.show_project_summary)
        project_menu.addAction(summary_action)
        
        calibration_action = QAction("&Calibration Data...", self)
        calibration_action.triggered.connect(self.show_calibration_data)
        project_menu.addAction(calibration_action)
        
        project_menu.addSeparator()
        
        analysis_options_action = QAction("Analysis &Options...", self)
        analysis_options_action.triggered.connect(self.show_analysis_options)
        project_menu.addAction(analysis_options_action)
        
        defaults_action = QAction("&Defaults...", self)
        defaults_action.triggered.connect(self.show_defaults)
        project_menu.addAction(defaults_action)
        
        project_menu.addSeparator()
        
        run_action = QAction("&Run Analysis", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_simulation)
        project_menu.addAction(run_action)
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        edit_menu.addSeparator()
        
        group_edit_action = QAction("&Group Edit...", self)
        group_edit_action.triggered.connect(self.group_edit)
        edit_menu.addAction(group_edit_action)
        
        # View Menu
        self.view_menu = menubar.addMenu("&View")
        
        # Pan/Select modes
        self.select_action = QAction("&Select", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True) # Default
        self.select_action.triggered.connect(lambda: self.set_interaction_mode('select'))
        self.view_menu.addAction(self.select_action)
        
        self.pan_action = QAction("&Pan", self)
        self.pan_action.setCheckable(True)
        self.pan_action.triggered.connect(lambda: self.set_interaction_mode('pan'))
        self.view_menu.addAction(self.pan_action)
        
        self.view_menu.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(zoom_out_action)
        
        full_extent_action = QAction("&Full Extent", self)
        full_extent_action.setShortcut("Home")
        full_extent_action.triggered.connect(self.full_extent)
        self.view_menu.addAction(full_extent_action)
        
        self.view_menu.addSeparator()
        
        dimensions_action = QAction("&Dimensions...", self)
        dimensions_action.triggered.connect(self.show_dimensions)
        self.view_menu.addAction(dimensions_action)
        
        self.view_menu.addSeparator()
        
        # Find Object
        find_action = QAction("&Find Object...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_object)
        self.view_menu.addAction(find_action)
        
        self.view_menu.addSeparator()
        
        self.view_menu.addSeparator()
        
        # Toolbars Submenu
        toolbars_menu = self.view_menu.addMenu("&Toolbars")
        
        # Standard Toolbar Toggle
        if hasattr(self, 'std_toolbar'):
            std_toolbar_action = self.std_toolbar.toggleViewAction()
            std_toolbar_action.setText("Standard")
            toolbars_menu.addAction(std_toolbar_action)
        
        self.view_menu.addSeparator()
        
        # Map Options
        options_action = QAction("选项", self)
        options_action.triggered.connect(self.show_map_options)
        self.view_menu.addAction(options_action)
        
        self.view_menu.addSeparator()
        
        # Backdrop Submenu
        backdrop_menu = self.view_menu.addMenu("&Backdrop")
        
        load_backdrop_action = QAction("&Load...", self)
        load_backdrop_action.triggered.connect(self.load_backdrop)
        backdrop_menu.addAction(load_backdrop_action)
        
        unload_backdrop_action = QAction("&Unload", self)
        unload_backdrop_action.triggered.connect(self.unload_backdrop)
        backdrop_menu.addAction(unload_backdrop_action)
        
        align_backdrop_action = QAction("&Align...", self)
        align_backdrop_action.triggered.connect(self.align_backdrop)
        backdrop_menu.addAction(align_backdrop_action)
        
        self.show_backdrop_action = QAction("&Show", self)
        self.show_backdrop_action.setCheckable(True)
        self.show_backdrop_action.setChecked(True)
        self.show_backdrop_action.triggered.connect(self.toggle_backdrop)
        backdrop_menu.addAction(self.show_backdrop_action)
        
        self.view_menu.addSeparator()
        
        # Window Menu
        self.window_menu = menubar.addMenu("&Window")
        self.window_menu.aboutToShow.connect(self.window_menu_about_to_show)
        
        cascade_action = QAction("&Cascade", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.window_menu.addAction(cascade_action)
        
        tile_action = QAction("&Tile", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        self.window_menu.addAction(tile_action)
        
        close_all_action = QAction("Close &All", self)
        close_all_action.triggered.connect(self.close_all_windows)
        self.window_menu.addAction(close_all_action)
        
        self.window_menu.addSeparator()
        
        # Report Menu
        report_menu = menubar.addMenu("&Report")
        
        status_report_action = QAction("&Status", self)
        status_report_action.triggered.connect(self.show_status_report)
        report_menu.addAction(status_report_action)
        
        energy_report_action = QAction("&Energy", self)
        energy_report_action.triggered.connect(self.show_energy_report)
        report_menu.addAction(energy_report_action)
        
        calibration_report_action = QAction("&Calibration", self)
        calibration_report_action.triggered.connect(self.show_calibration_report)
        report_menu.addAction(calibration_report_action)
        
        reaction_report_action = QAction("&Reaction", self)
        reaction_report_action.triggered.connect(self.show_reaction_report)
        report_menu.addAction(reaction_report_action)
        
        report_menu.addSeparator()
        
        graph_action = QAction("&Graph...", self)
        graph_action.triggered.connect(self.create_graph)
        report_menu.addAction(graph_action)
        
        table_action = QAction("&Table...", self)
        table_action.triggered.connect(self.create_table)
        report_menu.addAction(table_action)
        
        contour_action = QAction("&Contour...", self)
        contour_action.triggered.connect(self.create_contour)
        report_menu.addAction(contour_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        help_topics_action = QAction("&Help Topics", self)
        help_topics_action.setShortcut("F1")
        help_topics_action.triggered.connect(self.show_help_topics)
        help_menu.addAction(help_topics_action)
        
        units_action = QAction("&Units", self)
        units_action.triggered.connect(self.show_units)
        help_menu.addAction(units_action)
        
        tutorial_action = QAction("&Tutorial", self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About EPANET...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        

        
        # Add Print to File Menu
        # Insert before Exit (which is last)
        self.file_menu.insertSeparator(self.exit_action)
        
        page_setup_action = QAction("Page &Setup...", self)
        page_setup_action.triggered.connect(self.page_setup)
        self.file_menu.insertAction(self.exit_action, page_setup_action)
        
        print_preview_action = QAction("Print Pre&view...", self)
        print_preview_action.triggered.connect(self.print_preview)
        self.file_menu.insertAction(self.exit_action, print_preview_action)
        
        print_action = QAction("&Print...", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_map)
        self.file_menu.insertAction(self.exit_action, print_action)
        
        self.file_menu.insertSeparator(self.exit_action)
    
    def window_menu_about_to_show(self):
        """Update window menu with list of open windows."""
        # Clear existing window actions (keep first 4: Cascade, Tile, Close All, Separator)
        actions = self.window_menu.actions()
        for action in actions[4:]:
            self.window_menu.removeAction(action)
            
        # Add action for each subwindow
        subwindows = self.mdi_area.subWindowList()
        if not subwindows:
            return
            
        for i, subwindow in enumerate(subwindows):
            title = subwindow.windowTitle()
            action = QAction(f"{i+1} {title}", self)
            action.setCheckable(True)
            action.setChecked(subwindow == self.mdi_area.activeSubWindow())
            action.triggered.connect(lambda checked=False, s=subwindow: self.mdi_area.setActiveSubWindow(s))
            self.window_menu.addAction(action)
            
    def close_all_windows(self):
        """Close all MDI subwindows."""
        self.mdi_area.closeAllSubWindows()

    def show_help_topics(self):
        """Show help topics."""
        from gui.dialogs.help_dialog import HelpDialog
        dialog = HelpDialog("EPANET Help", parent=self)
        dialog.show()
        self.help_dialog = dialog
        
    def show_units(self):
        """Show units reference."""
        from gui.dialogs.help_dialog import HelpDialog
        html = """
        <h1>Units of Measurement</h1>
        <table border="1" cellpadding="5">
        <tr><th>Parameter</th><th>US Customary</th><th>SI Metric</th></tr>
        <tr><td>Flow</td><td>CFS, GPM, MGD</td><td>LPS, LPM, MLD, CMH</td></tr>
        <tr><td>Pressure</td><td>psi</td><td>meters</td></tr>
        <tr><td>Head</td><td>feet</td><td>meters</td></tr>
        <tr><td>Diameter</td><td>inches</td><td>millimeters</td></tr>
        </table>
        """
        dialog = HelpDialog("Units Reference", content=html, parent=self)
        dialog.show()
        self.units_dialog = dialog
        
    def show_tutorial(self):
        """Show tutorial."""
        from gui.dialogs.help_dialog import HelpDialog
        html = """
        <h1>EPANET Tutorial</h1>
        <p><b>Step 1:</b> Draw the network using the toolbar buttons.</p>
        <p><b>Step 2:</b> Edit properties of nodes and links.</p>
        <p><b>Step 3:</b> Run the analysis (F5).</p>
        <p><b>Step 4:</b> View results on the map or in reports.</p>
        """
        dialog = HelpDialog("Tutorial", content=html, parent=self)
        dialog.show()
        self.tutorial_dialog = dialog
        
    def show_about(self):
        """Show about dialog."""
        from gui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()
        
    def page_setup(self):
        """Show page setup dialog."""
        # For now, just a placeholder or basic QPageSetupDialog if needed
        # QPageSetupDialog requires a QPrinter
        from PySide6.QtPrintSupport import QPageSetupDialog, QPrinter
        printer = QPrinter()
        dialog = QPageSetupDialog(printer, self)
        dialog.exec()
        
    def print_preview(self):
        """Show print preview."""
        from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter
        printer = QPrinter()
        dialog = QPrintPreviewDialog(printer, self)
        dialog.paintRequested.connect(self._print_preview_paint)
        dialog.exec()
        
    def _print_preview_paint(self, printer):
        """Paint scene to printer for preview."""
        painter = QPainter(printer)
        # Render map scene
        scene = self.map_widget.scene
        rect = scene.itemsBoundingRect()
        scene.render(painter, target=QRectF(printer.pageRect(QPrinter.DevicePixel)), source=rect)
        painter.end()
        
    def print_map(self):
        """Print map."""
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.Accepted:
            painter = QPainter(printer)
            scene = self.map_widget.scene
            rect = scene.itemsBoundingRect()
            scene.render(painter, target=QRectF(printer.pageRect(QPrinter.DevicePixel)), source=rect)
            painter.end()

    def show_status_report(self):
        """Show status report."""
        from gui.reports.status_report import StatusReport
        report = StatusReport(self.project)
        report.show()
        self.status_report = report
        
    def show_energy_report(self):
        """Show energy report."""
        from gui.reports.energy_report import EnergyReport
        report = EnergyReport(self.project)
        report.show()
        self.energy_report = report

    def show_calibration_report(self):
        """Show calibration report."""
        from gui.reports.calibration_report import CalibrationReport
        report = CalibrationReport(self.project)
        report.show()
        # Keep reference to prevent garbage collection
        self.calibration_report = report
        
    def show_reaction_report(self):
        """Show reaction report."""
        from gui.reports.reaction_report import ReactionReport
        report = ReactionReport(self.project)
        report.show()
        self.reaction_report = report
        
    def export_map(self):
        """Export map to image file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Map", "", 
            "PNG Image (*.png);;JPEG Image (*.jpg);;PDF Document (*.pdf)"
        )
        
        if file_path:
            # Grab the scene content
            scene = self.map_widget.scene
            rect = scene.itemsBoundingRect()
            
            # Create image
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            
            painter = QPainter(image)
            scene.render(painter, target=QRectF(image.rect()), source=rect)
            painter.end()
            
            image.save(file_path)
            self.status_bar.showMessage(f"Map exported to {file_path}")

    def create_icon_from_text(self, text, color=Qt.black):
        """Create a QIcon from a text character."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(color)
        
        font = QFont("Arial", 24)
        painter.setFont(font)
        
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        
        return QIcon(pixmap)

    def create_toolbars(self):
        """Create toolbars."""
        # Standard toolbar
        self.std_toolbar = QToolBar("Standard")
        self.std_toolbar.setObjectName("StandardToolbar")
        self.std_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.std_toolbar)
        
        # File Actions
        # New
        new_action = QAction(self.create_icon_from_text("📄"), "New", self)
        new_action.triggered.connect(self.new_project)
        self.std_toolbar.addAction(new_action)
        
        # Open
        open_action = QAction(self.create_icon_from_text("📂"), "Open", self)
        open_action.triggered.connect(self.open_project)
        self.std_toolbar.addAction(open_action)
        
        # Save
        save_action = QAction(self.create_icon_from_text("💾"), "Save", self)
        save_action.triggered.connect(self.save_project)
        self.std_toolbar.addAction(save_action)
        
        self.std_toolbar.addSeparator()
        
        # View modes
        # Select (Arrow)
        self.select_action.setIcon(self.create_icon_from_text("↖️"))
        self.select_action.setText("Select")
        self.std_toolbar.addAction(self.select_action)
        
        # Pan (Hand)
        # Use a custom icon for Pan (Hand)
        self.pan_action.setIcon(self.create_icon_from_text("✋"))
        self.pan_action.setText("Pan")
        self.std_toolbar.addAction(self.pan_action)
        
        self.std_toolbar.addSeparator()
        
        # Run
        run_action = QAction(self.create_icon_from_text("▶️"), "Run", self)
        run_action.triggered.connect(self.run_simulation)
        self.std_toolbar.addAction(run_action)
        
        self.std_toolbar.addSeparator()
        
        # Reporting
        graph_action = QAction(self.create_icon_from_text("📈"), "Graph", self)
        graph_action.triggered.connect(self.create_graph)
        self.std_toolbar.addAction(graph_action)
        
        table_action = QAction(self.create_icon_from_text("📋"), "Table", self)
        table_action.triggered.connect(self.create_table)
        self.std_toolbar.addAction(table_action)
        
        # Others (keep text or find icons)
        contour_action = QAction(self.create_icon_from_text("🗺️"), "Contour", self) 
        contour_action.triggered.connect(self.create_contour)
        self.std_toolbar.addAction(contour_action)
        
        status_action = QAction(self.create_icon_from_text("ℹ️"), "Status", self)
        status_action.triggered.connect(self.create_status)
        self.std_toolbar.addAction(status_action)
        
        calib_action = QAction(self.create_icon_from_text("🎯"), "Calibration", self)
        calib_action.triggered.connect(self.create_calibration)
        self.std_toolbar.addAction(calib_action)
        
        energy_action = QAction(self.create_icon_from_text("⚡"), "Energy", self)
        energy_action.triggered.connect(self.create_energy)
        self.std_toolbar.addAction(energy_action)
        
        self.std_toolbar.addSeparator()
        
        # Map Options
        map_options_action = QAction(self.create_icon_from_text("⚙️"), "Map Options", self)
        map_options_action.triggered.connect(self.show_map_options)
        self.std_toolbar.addAction(map_options_action)
    
    def create_dock_widgets(self):
        """Create dock widgets."""
        # Browser dock
        self.browser_dock = QDockWidget("Browser", self)
        self.browser_dock.setObjectName("BrowserDock")
        self.browser_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.browser_widget = BrowserWidget(self.project, self)
        self.browser_widget.object_selected.connect(self.on_browser_object_selected)
        self.browser_widget.objectActivated.connect(self.on_browser_object_activated)
        
        # Connect map browser signals
        self.browser_widget.map_browser.node_parameter_changed.connect(self.on_node_param_changed)
        self.browser_widget.map_browser.link_parameter_changed.connect(self.on_link_param_changed)
        self.browser_widget.map_browser.time_changed.connect(self.on_time_changed)
        
        self.browser_dock.setWidget(self.browser_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.browser_dock)
        
        # Property Editor Dock
        self.property_dock = QDockWidget("Property Editor", self)
        self.property_dock.setObjectName("PropertyDock")
        self.property_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_editor = PropertyEditor(self.project, self)
        self.property_editor.objectUpdated.connect(self.on_property_changed)
        self.property_dock.setWidget(self.property_editor)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_dock)
        
        # Overview Map Dock
        from gui.widgets.overview_map import OverviewMapWidget
        self.overview_dock = QDockWidget("Overview Map", self)
        self.overview_dock.setObjectName("OverviewDock")
        self.overview_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.overview_map = OverviewMapWidget(self)
        self.overview_map.set_main_view(self.map_widget)
        self.overview_dock.setWidget(self.overview_map)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.overview_dock)
        
        # Connect map view changes to overview
        self.map_widget.horizontalScrollBar().valueChanged.connect(lambda: self.overview_map.update_extent())
        self.map_widget.verticalScrollBar().valueChanged.connect(lambda: self.overview_map.update_extent())
        
        
        # Add toggle actions to View menu
        if hasattr(self, 'view_menu'):
            self.view_menu.addSeparator()
            self.view_menu.addAction(self.browser_dock.toggleViewAction())
            self.view_menu.addAction(self.property_dock.toggleViewAction())
            self.view_menu.addAction(self.overview_dock.toggleViewAction())
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def on_map_selection_changed(self, obj):
        """Handle selection changes in the map."""
        self.property_editor.set_object(obj)

    def on_browser_object_selected(self, obj_type: str, obj_id: str):
        """Handle selection from browser widget: select object in property editor."""
        # Find object in network
        obj = None
        if obj_type == 'Node':
            obj = self.project.network.get_node(obj_id)
        elif obj_type == 'Link':
            obj = self.project.network.get_link(obj_id)
        elif obj_type == 'Pattern':
            obj = self.project.network.patterns.get(obj_id)
        elif obj_type == 'Curve':
            obj = self.project.network.curves.get(obj_id)
            
        if obj:
            self.property_editor.set_object(obj)

    def on_property_changed(self, obj):
        """Handle property changes from property editor."""
        # Refresh map to show changes (e.g. coordinates, diameter)
        self.map_widget.scene.update()
        # Refresh browser tree if needed (e.g. ID change)
        # For now, just update map
        pass
    
    def on_browser_object_activated(self, obj_type: str, obj_id: str):
        """Handle activation from browser widget: select object in property editor and map."""
        try:
            if obj_type == 'Pattern':
                # Open pattern editor
                self.edit_pattern(obj_id)
                return
            elif obj_type == 'Curve':
                # Open curve editor
                self.edit_curve(obj_id)
                return
            elif obj_type == 'Node':
                obj = self.project.network.get_node(obj_id)
            elif obj_type == 'Link':
                obj = self.project.network.get_link(obj_id)
            else:
                return

            if not obj:
                return

            # Update property editor
            self.property_editor.set_object(obj)

            # Clear existing selections on the scene
            self.map_widget.scene.clearSelection()

            # Select and highlight item on scene
            try:
                if obj_type == 'Node' and obj_id in self.map_widget.scene.node_items:
                    item = self.map_widget.scene.node_items[obj_id]
                    item.setSelected(True)
                    # Ensure item is visible and centered
                    self.map_widget.ensureVisible(item)
                    self.map_widget.centerOn(item)
                elif obj_type == 'Link' and obj_id in self.map_widget.scene.link_items:
                    item = self.map_widget.scene.link_items[obj_id]
                    item.setSelected(True)
                    # Center on link midpoint
                    mid_x = (item.from_pos.x() + item.to_pos.x()) / 2.0
                    mid_y = (item.from_pos.y() + item.to_pos.y()) / 2.0
                    from PySide6.QtCore import QPointF
                    mid_point = QPointF(mid_x, mid_y)
                    self.map_widget.ensureVisible(item)
                    self.map_widget.centerOn(mid_point)
            except Exception as e:
                # Log or silently ignore individual link centering issues
                pass

        except Exception:
            pass


    def on_property_object_updated(self, obj):
        """Handle updates from property editor: refresh map visuals and browser if needed."""
        try:
            # If it's a node, update its graphic position
            if hasattr(obj, 'node_type'):
                node_id = obj.id
                if node_id in self.map_widget.scene.node_items:
                    item = self.map_widget.scene.node_items[node_id]
                    # Update view position from model
                    item.setPos(obj.x, obj.y)
                    # Ensure connected links update
                    try:
                        self.map_widget.scene.update_connected_links(node_id)
                    except Exception:
                        pass

            # If it's a link, update link geometry
            if hasattr(obj, 'link_type'):
                link_id = obj.id
                if link_id in self.map_widget.scene.link_items:
                    link_item = self.map_widget.scene.link_items[link_id]
                    from_item = self.map_widget.scene.node_items.get(link_item.link.from_node)
                    to_item = self.map_widget.scene.node_items.get(link_item.link.to_node)
                    if from_item and to_item:
                        link_item.update_positions(from_item.pos(), to_item.pos())

            # Refresh browser labels/counts if necessary
            try:
                self.browser_widget.refresh()
            except Exception:
                pass

        except Exception:
            pass
        
    def update_title(self):
        """Update window title based on current project."""
        if self.project.filename:
            title = f"EPANET 2.2 - PySide6 - {os.path.basename(self.project.filename)}"
        else:
            title = "EPANET 2.2 - PySide6 - Untitled"
        self.setWindowTitle(title)
        
    # File operations
    
    def new_project(self):
        """Create new project."""
        if not self.check_save_changes():
            return
            
        self.project.new_project()
        self.browser_widget.refresh()
        self.property_editor.set_object(None)
        self.map_widget.scene.load_network()
        self.update_title()
        self.status_bar.showMessage("New project created")
    
    def open_project(self):
        """Open project from file."""
        if not self.check_save_changes():
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "EPANET Files (*.inp *.net);;All Files (*.*)"
        )
        
        if filename:
            try:
                self.project.open_project(filename)
                self.browser_widget.refresh()
                self.property_editor.set_object(None)
                self.map_widget.scene.load_network()
                self.map_widget.fit_network()
                self.update_title()
                self.status_bar.showMessage(f"Opened {filename}")
                self.add_recent_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")
    
    def save_project(self):
        """Save current project."""
        if not self.project.filename:
            self.save_project_as()
        else:
            try:
                self.project.save_project()
                self.status_bar.showMessage(f"Saved {self.project.filename}")
                self.add_recent_file(self.project.filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project:\n{str(e)}")
    
    def save_project_as(self):
        """Save project with new filename."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            "",
            "EPANET Network Files (*.net);;EPANET Input Files (*.inp);;All Files (*)"
        )
        
        if filename:
            try:
                self.project.save_project(filename)
                self.setWindowTitle(f"EPANET 2.2 - PySide6 - {os.path.basename(filename)}")
                self.status_bar.showMessage(f"Saved {filename}")
                self.add_recent_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project:\n{str(e)}")
    
    def check_save_changes(self) -> bool:
        """Check if user wants to save changes.
        
        Returns:
            True if OK to proceed, False if cancelled
        """
        if self.project.modified:
            reply = QMessageBox.question(
                self,
                "Save Changes",
                "Save changes to current project?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_project()
                return True
            elif reply == QMessageBox.No:
                return True
            else:
                return False
        return True
        
    # Import/Export
    
    def import_network(self):
        """Import network from INP file."""
        if not self.check_save_changes():
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Network", "", "EPANET Input Files (*.inp);;All Files (*.*)"
        )
        
        if filename:
            try:
                self.project.open_project(filename)
                self.browser_widget.refresh()
                self.property_editor.set_object(None)
                self.map_widget.scene.load_network()
                self.map_widget.fit_network()
                self.update_title()
                self.status_bar.showMessage(f"Imported network from {filename}")
                self.add_recent_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import network:\n{str(e)}")
                
    def import_map(self):
        """Import map file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Map", "", "Map Files (*.map);;EPANET Input Files (*.inp);;All Files (*.*)"
        )
        
        if not filename:
            return
            
        try:
            count = self.project.import_map(filename)
            self.map_widget.scene.load_network()
            self.map_widget.fit_network()
            self.status_bar.showMessage(f"Imported coordinates for {count} nodes from {filename}")
            QMessageBox.information(self, "Import Map", f"Updated coordinates for {count} nodes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import map:\n{str(e)}")
        
    def import_scenario(self):
        """Import scenario file."""
        QMessageBox.information(self, "Not Implemented", "Import Scenario functionality is coming soon.")
        
    def export_network(self):
        """Export network to INP file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Network", "", "EPANET Input Files (*.inp);;All Files (*.*)"
        )
        
        if filename:
            try:
                # Ensure extension
                if not filename.lower().endswith('.inp'):
                    filename += '.inp'
                    
                self.project.save_project(filename)
                self.status_bar.showMessage(f"Exported network to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export network:\n{str(e)}")
                
    def export_map(self):
        """Export map to image file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Map", "", "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*.*)"
        )
        
        if filename:
            try:
                # Grab map view as pixmap
                pixmap = self.map_widget.grab()
                pixmap.save(filename)
                self.status_bar.showMessage(f"Exported map to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export map:\n{str(e)}")
                
    def export_scenario(self):
        """Export scenario file."""
        QMessageBox.information(self, "Not Implemented", "Export Scenario functionality is coming soon.")
    
    # Simulation
    
    def run_simulation(self):
        """Run hydraulic and water quality simulation."""
        from gui.dialogs import SimulationStatusDialog
        from PySide6.QtWidgets import QApplication
        
        dialog = SimulationStatusDialog(self)
        dialog.show()
        
        try:
            dialog.set_status("Running simulation...")
            dialog.append_log("Initializing...")
            QApplication.processEvents()
            
            def update_progress(value):
                dialog.set_progress(value)
                QApplication.processEvents()
            
            # Run simulation
            dialog.append_log("Solving hydraulics...")
            self.project.run_simulation(update_progress)
            
            dialog.simulation_finished(True)
            
            # Update UI with results
            self.browser_widget.refresh()
            
            # Update map browser time steps
            if self.project.engine.results and self.project.engine.results.node:
                # Get time steps from any node result (e.g. pressure)
                # If pressure not available, try demand, etc.
                # Usually all node results have same time index
                for param in self.project.engine.results.node:
                    times = self.project.engine.results.node[param].index.tolist()
                    self.browser_widget.map_browser.set_time_steps(times)
                    break
            
            # Auto-update map values
            # Ensure we have current parameters set
            if not hasattr(self, 'current_node_param') or not self.current_node_param:
                self.current_node_param = self.browser_widget.map_browser.node_combo.currentText()
                if self.current_node_param == "NONE": self.current_node_param = None
                
            if not hasattr(self, 'current_link_param') or not self.current_link_param:
                self.current_link_param = self.browser_widget.map_browser.link_combo.currentText()
                if self.current_link_param == "NONE": self.current_link_param = None
            
            # Force update
            self._update_map_colors()
            
            self.status_bar.showMessage("Simulation completed successfully")
            
        except Exception as e:
            dialog.append_log(f"Error: {str(e)}")
            dialog.simulation_finished(False)
            self.status_bar.showMessage("Simulation failed")
            
    # Views
    
    def create_graph(self):
        """Create a new graph window."""
        from gui.views import GraphView
        from gui.dialogs.graph_selection_dialog import GraphSelectionDialog
        
        # Get current map selection
        selected_items = self.map_widget.scene.selectedItems()
        initial_selection = []
        initial_obj_type = "Node" # Default
        
        nodes = []
        links = []
        
        for item in selected_items:
            if hasattr(item, 'node'):
                nodes.append(item.node.id)
            elif hasattr(item, 'link'):
                links.append(item.link.id)
                
        if nodes:
            initial_selection = nodes
            initial_obj_type = "Node"
        elif links:
            initial_selection = links
            initial_obj_type = "Link"
        
        # Open selection dialog
        dialog = GraphSelectionDialog(self.project, self, 
                                    initial_selection=initial_selection,
                                    initial_obj_type=initial_obj_type)
        
        if dialog.exec():
            selection = dialog.get_selection()
            
            if selection['graph_type'] == "Time Series":
                if not selection['objects']:
                    QMessageBox.warning(self, "Graph", "Please select at least one object.")
                    return
                    
                graph_view = GraphView(self.project)
                graph_view.set_data(
                    selection['object_type'], 
                    selection['objects'], 
                    selection['parameter']
                )
                
                subwindow = self.mdi_area.addSubWindow(graph_view)
                subwindow.setWindowTitle(f"Graph - {selection['parameter'].name}")
                subwindow.showMaximized()
            else:
                QMessageBox.information(self, "Graph", f"{selection['graph_type']} not implemented yet.")
        
    def create_table(self):
        """Create a new table window."""
        from gui.views import TableView
        
        table_view = TableView(self.project)
        # Connect selection sync
        table_view.object_selected.connect(self.on_browser_object_selected)
        
        subwindow = self.mdi_area.addSubWindow(table_view)
        subwindow.setWindowTitle("Network Table")
        subwindow.showMaximized()
        
    def create_contour(self):
        """Create a new contour window."""
        from gui.views import ContourView
        from gui.dialogs.graph_selection_dialog import GraphSelectionDialog
        
        dialog = GraphSelectionDialog(self.project, self, initial_type="Contour")
        
        if dialog.exec():
            selection = dialog.get_selection()
            
            if selection['graph_type'] == "Contour":
                contour_view = ContourView(self.project)
                contour_view.set_parameter(selection['parameter'])
                
                subwindow = self.mdi_area.addSubWindow(contour_view)
                subwindow.setWindowTitle(f"Contour - {selection['parameter'].name}")
                subwindow.showMaximized()
            else:
                # If user changed mind and selected something else, handle it or warn
                # For now, just handle Contour
                QMessageBox.information(self, "Contour", "Please select Contour Plot type.")
        
    def create_status(self):
        """Create a new status report window."""
        from gui.views import StatusView
        
        status_view = StatusView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(status_view)
        subwindow.setWindowTitle("Status Report")
        subwindow.showMaximized()
        
    def create_calibration(self):
        """Create a new calibration window."""
        from gui.views import CalibrationView
        
        calib_view = CalibrationView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(calib_view)
        subwindow.setWindowTitle("Calibration")
        subwindow.showMaximized()
        
    def create_energy(self):
        """Create a new energy report window."""
        from gui.views import EnergyView
        
        energy_view = EnergyView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(energy_view)
        subwindow.setWindowTitle("Energy Report")
        subwindow.showMaximized()
    
    # Data Editors
    
    def edit_pattern(self, pattern_id: str):
        """Open pattern editor dialog."""
        from gui.dialogs import PatternEditor
        from models import Pattern
        
        pattern = self.project.network.get_pattern(pattern_id)
        if not pattern:
            QMessageBox.warning(self, "Pattern Not Found", f"Pattern '{pattern_id}' not found.")
            return
        
        dialog = PatternEditor(self)
        dialog.load_data(pattern_id, pattern.multipliers, pattern.comment)
        
        # Connect signal to update pattern
        def on_pattern_updated(new_id, multipliers, comment):
            try:
                # Update pattern data
                pattern.id = new_id
                pattern.multipliers = multipliers
                pattern.comment = comment
                
                # If ID changed, update the dictionary key
                if new_id != pattern_id:
                    self.project.network.patterns[new_id] = pattern
                    if pattern_id in self.project.network.patterns:
                        del self.project.network.patterns[pattern_id]
                
                # Mark project as modified
                self.project.modified = True
                
                # Refresh browser
                self.browser_widget.refresh()
                
                self.status_bar.showMessage(f"Pattern '{new_id}' updated")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update pattern:\n{str(e)}")
        
        dialog.pattern_updated.connect(on_pattern_updated)
        dialog.exec()
    
    def edit_curve(self, curve_id: str):
        """Open curve editor dialog."""
        from gui.dialogs import CurveEditor
        from models import Curve, CurveType
        
        curve = self.project.network.get_curve(curve_id)
        if not curve:
            QMessageBox.warning(self, "Curve Not Found", f"Curve '{curve_id}' not found.")
            return
        
        dialog = CurveEditor(self)
        
        # Convert curve type enum to string
        curve_type_str = "Pump"  # Default
        if curve.curve_type == CurveType.VOLUME:
            curve_type_str = "Volume"
        elif curve.curve_type == CurveType.PUMP:
            curve_type_str = "Pump"
        elif curve.curve_type == CurveType.EFFICIENCY:
            curve_type_str = "Efficiency"
        elif curve.curve_type == CurveType.HEADLOSS:
            curve_type_str = "Headloss"
        
        dialog.load_data(curve_id, curve_type_str, curve.points, curve.comment)
        
        # Connect signal to update curve
        def on_curve_updated(new_id, curve_type, points, comment):
            try:
                # Convert curve type string to enum
                type_map = {
                    "Volume": CurveType.VOLUME,
                    "Pump": CurveType.PUMP,
                    "Efficiency": CurveType.EFFICIENCY,
                    "Headloss": CurveType.HEADLOSS
                }
                
                # Update curve data
                curve.id = new_id
                curve.curve_type = type_map.get(curve_type, CurveType.PUMP)
                curve.points = points
                curve.comment = comment
                
                # If ID changed, update the dictionary key
                if new_id != curve_id:
                    self.project.network.curves[new_id] = curve
                    if curve_id in self.project.network.curves:
                        del self.project.network.curves[curve_id]
                
                # Mark project as modified
                self.project.modified = True
                
                # Refresh browser
                self.browser_widget.refresh()
                
                self.status_bar.showMessage(f"Curve '{new_id}' updated")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update curve:\n{str(e)}")
        
        dialog.curve_updated.connect(on_curve_updated)
        dialog.exec()
    
    def show_project_summary(self):
        """Show project summary dialog."""
        from gui.dialogs.project_summary_dialog import ProjectSummaryDialog
        
        # Get current title and notes
        title = self.project.network.title
        notes = self.project.network.notes
        
        dialog = ProjectSummaryDialog(self, title, notes)
        if dialog.exec():
            data = dialog.get_data()
            self.project.network.title = data['title']
            self.project.network.notes = data['notes']
            self.project.modified = True
            self.status_bar.showMessage("Project summary updated")

    def show_calibration_data(self):
        """Show calibration data dialog."""
        from gui.dialogs.calibration_data_dialog import CalibrationDataDialog
        
        current_data = self.project.network.calibration_data
        
        dialog = CalibrationDataDialog(self, current_data)
        if dialog.exec():
            new_data = dialog.get_data()
            self.project.network.calibration_data = new_data
            self.project.modified = True
            self.status_bar.showMessage("Calibration data updated")

    def show_dimensions(self):
        """Show dimensions dialog."""
        from gui.dialogs.dimensions_dialog import DimensionsDialog
        
        current_bounds = self.project.network.map_bounds
        current_units = self.project.network.map_units
        
        dialog = DimensionsDialog(self, current_bounds, current_units)
        if dialog.exec():
            data = dialog.get_data()
            self.project.network.map_bounds = data['bounds']
            self.project.network.map_units = data['units']
            self.project.modified = True
            
            # Update scene
            self.map_widget.scene.update_scene_rect()
            self.map_widget.fit_network()
            
            self.status_bar.showMessage("Map dimensions updated")

    def show_analysis_options(self):
        """Show analysis options dialog."""
        from gui.dialogs.analysis_options_dialog import AnalysisOptionsDialog
        dialog = AnalysisOptionsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Options are saved in the dialog's accept method
            pass
    
    def show_defaults(self):
        """Show project defaults dialog."""
        from gui.dialogs.defaults_dialog import DefaultsDialog
        dialog = DefaultsDialog(self.project, self)
        if dialog.exec() == QDialog.Accepted:
            # Defaults are saved in the dialog's accept method
            pass
    
    def show_map_options(self):
        """Show map options dialog."""
        from gui.dialogs.map_options_dialog import MapOptionsDialog
        dialog = MapOptionsDialog(self)
        
        # Initialize default options if not set
        if not hasattr(self.project, 'map_options'):
            self.project.map_options = {
                'node_size': 3,
                'size_nodes_by_value': False,
                'display_node_border': True,
                'display_junction_symbols': True,
                'link_size': 2,
                'size_links_by_value': False,
                'display_link_border': False,
                'arrow_style': 0,
                'arrow_size': 5,
                'display_labels': True,
                'labels_transparent': False,
                'label_zoom': 100,
                'display_node_ids': False,
                'display_node_values': False,
                'display_link_ids': False,
                'display_link_values': False,
                'notation_transparent': False,
                'notation_font_size': 8,
                'notation_zoom': 100,
                'display_tanks': True,
                'display_pumps': True,
                'display_valves': True,
                'display_emitters': True,
                'display_sources': True,
                'symbol_zoom': 100,
                'background_color': '#FFFFFF'
            }
    
        dialog.load_options(self.project.map_options)
        
        # Connect signal to update options
        def on_options_updated(new_options):
            self.project.map_options = new_options
            self.map_widget.scene.apply_map_options(new_options)
            self.status_bar.showMessage("Map options updated")
        
        dialog.options_updated.connect(on_options_updated)
        dialog.exec()


    def set_interaction_mode(self, mode: str):
        """Set map interaction mode."""
        self.map_widget.set_interaction_mode(mode)
        
        # Update UI state
        self.select_action.setChecked(mode == 'select')
        self.pan_action.setChecked(mode == 'pan')

    
    # View operations
    
    def zoom_in(self):
        """Zoom in on the map."""
        self.map_widget.scale(1.2, 1.2)
        
    def zoom_out(self):
        """Zoom out on the map."""
        self.map_widget.scale(1/1.2, 1/1.2)
        
    def full_extent(self):
        """Zoom to full network extent."""
        self.map_widget.fit_network()
        
    def find_object(self):
        """Show find object dialog."""
        from gui.dialogs import FindObjectDialog
        
        dialog = FindObjectDialog(self.project, self)
        
        # Connect signal to select object
        def on_object_selected(obj_type, obj_id):
            try:
                # Simulate browser activation to select and center object
                self.on_browser_object_activated(obj_type, obj_id)
                self.status_bar.showMessage(f"Found {obj_type}: {obj_id}")
            except Exception as e:
                QMessageBox.warning(self, "Object Not Found", f"Could not find {obj_type} '{obj_id}'.")
        
        dialog.object_selected.connect(on_object_selected)
        dialog.exec()
        
    # Map Visualization Handlers
    
    def on_node_param_changed(self, param):
        """Handle node parameter change."""
        self.current_node_param = param
        self._update_map_colors()
        
    def on_link_param_changed(self, param):
        """Handle link parameter change."""
        self.current_link_param = param
        self._update_map_colors()
        
    def on_time_changed(self, time_step):
        """Handle time step change."""
        self.current_time_step = time_step
        self._update_map_colors()
        
    def _update_map_colors(self):
        """Update map colors based on current parameters and time."""
        # Initialize current params if not set
        if not hasattr(self, 'current_node_param'): self.current_node_param = None
        if not hasattr(self, 'current_link_param'): self.current_link_param = None
        if not hasattr(self, 'current_time_step'): self.current_time_step = 0
        
        results = self.project.engine.results
        if not results:
            return

        # Colors for legend (Blue -> Cyan -> Green -> Yellow -> Red)
        colors = [QColor(0,0,255), QColor(0,255,255), QColor(0,255,0), QColor(255,255,0), QColor(255,0,0)]
        
        # Update Nodes
        if self.current_node_param:
            param = self.current_node_param.lower()
            # Map UI names to WNTR result names
            param_map = {
                "elevation": "elevation", # usually property, not result, but handled
                "base demand": "base_demand",
                "basedemand": "base_demand",
                "initial quality": "initial_quality",
                "initialquality": "initial_quality",
                "demand": "demand",
                "head": "head",
                "pressure": "pressure",
                "quality": "quality"
            }
            wntr_param = param_map.get(param, param)
            
            values = {}
            if wntr_param in results.node:
                # Get values for current time step
                # results.node[param] is a DataFrame, index is time
                try:
                    # Get the row for the current time step (index)
                    # Assuming time steps are sequential integers in slider matching result index
                    # But WNTR results index is time in seconds.
                    # We need to map slider index to time index.
                    times = results.node[wntr_param].index
                    if self.current_time_step < len(times):
                        t = times[self.current_time_step]
                        row = results.node[wntr_param].loc[t]
                        values = row.to_dict()
                except Exception as e:
                    print(f"Error getting node results: {e}")
            
            if values:
                # Calculate min/max for legend
                min_val = min(values.values())
                max_val = max(values.values())
                
                # Create 5 intervals
                if min_val == max_val:
                    intervals = [min_val] * 5
                else:
                    step = (max_val - min_val) / 4
                    intervals = [min_val + i*step for i in range(5)]
                
                # Update Legend
                # TODO: Handle multiple legends (node/link) - for now just show node if selected
                self.map_widget.legend.set_data(self.current_node_param, "", intervals, colors)
                self.map_widget.legend.show()
                
                # Update Scene
                self.map_widget.scene.update_node_colors(values, colors, intervals)
            else:
                self.map_widget.legend.hide()
                self.map_widget.scene.update_node_colors({}, [], [])
        else:
            if not self.current_link_param:
                self.map_widget.legend.hide()
            self.map_widget.scene.update_node_colors({}, [], [])

        # Update Links
        if self.current_link_param:
            param = self.current_link_param.lower()
            param_map = {
                "length": "length",
                "diameter": "diameter",
                "roughness": "roughness",
                "flow": "flowrate",
                "velocity": "velocity",
                "unit headloss": "headloss", # check this
                "unitheadloss": "headloss",
                "friction factor": "friction_factor",
                "frictionfactor": "friction_factor",
                "reaction rate": "reaction_rate",
                "reactionrate": "reaction_rate",
                "quality": "quality"
            }
            wntr_param = param_map.get(param, param)
            
            values = {}
            if wntr_param in results.link:
                try:
                    times = results.link[wntr_param].index
                    if self.current_time_step < len(times):
                        t = times[self.current_time_step]
                        row = results.link[wntr_param].loc[t]
                        values = row.to_dict()
                except Exception as e:
                    print(f"Error getting link results: {e}")
            
            if values:
                # Calculate min/max
                min_val = min(values.values())
                max_val = max(values.values())
                
                if min_val == max_val:
                    intervals = [min_val] * 5
                else:
                    step = (max_val - min_val) / 4
                    intervals = [min_val + i*step for i in range(5)]
                
                # Update Legend (Override node legend for now if link selected)
                # Ideally we need two legends or a switch
                self.map_widget.legend.set_data(self.current_link_param, "", intervals, colors)
                self.map_widget.legend.show()
                
                self.map_widget.scene.update_link_colors(values, colors, intervals)
            else:
                self.map_widget.scene.update_link_colors({}, [], [])
        else:
            self.map_widget.scene.update_link_colors({}, [], [])
    
    # Backdrop Handlers
    
    def load_backdrop(self):
        """Load backdrop image."""
        from gui.dialogs import BackdropDialog
        
        dialog = BackdropDialog(self.project, self)
        if dialog.exec():
            image_path, ul_x, ul_y, lr_x, lr_y = dialog.get_data()
            if image_path:
                self.map_widget.scene.set_backdrop(image_path, ul_x, ul_y, lr_x, lr_y)
                self.backdrop_info = (image_path, ul_x, ul_y, lr_x, lr_y)
                self.show_backdrop_action.setChecked(True)
                
    def unload_backdrop(self):
        """Unload backdrop image."""
        self.map_widget.scene.clear_backdrop()
        self.backdrop_info = None
        
    def align_backdrop(self):
        """Align backdrop image."""
        if not hasattr(self, 'backdrop_info') or not self.backdrop_info:
            QMessageBox.information(self, "Backdrop", "No backdrop loaded.")
            return
            
        from gui.dialogs import BackdropDialog
        
        dialog = BackdropDialog(self.project, self)
        image_path, ul_x, ul_y, lr_x, lr_y = self.backdrop_info
        dialog.set_data(image_path, ul_x, ul_y, lr_x, lr_y)
        
        if dialog.exec():
            image_path, ul_x, ul_y, lr_x, lr_y = dialog.get_data()
            if image_path:
                self.map_widget.scene.set_backdrop(image_path, ul_x, ul_y, lr_x, lr_y)
                self.backdrop_info = (image_path, ul_x, ul_y, lr_x, lr_y)
                
    def toggle_backdrop(self, checked):
        """Toggle backdrop visibility."""
        self.map_widget.scene.toggle_backdrop(checked)

    # Help
    
    def show_about(self):
        """Show about dialog."""
        try:
            version = self.project.get_version()
        except:
            version = "2.2.0"
        
        QMessageBox.about(
            self,
            "About EPANET",
            f"<h3>EPANET {version}</h3>"
            "<p>Water Distribution System Modeling Software</p>"
            "<p>PySide6 GUI Implementation</p>"
            "<p>© US Environmental Protection Agency</p>"
        )
    
    # Settings
    
    def restore_settings(self):
        """Restore window settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
            
        # Load Defaults
        self.project.default_prefixes = {}
        self.settings.beginGroup("Defaults/IDPrefixes")
        for key in self.settings.childKeys():
            self.project.default_prefixes[key] = self.settings.value(key)
        self.settings.endGroup()
        
        # If empty, set defaults
        if not self.project.default_prefixes:
            self.project.default_prefixes = {
                'Junction': 'J', 'Reservoir': 'R', 'Tank': 'T',
                'Pipe': 'P', 'Pump': 'PU', 'Valve': 'V',
                'Pattern': 'PAT', 'Curve': 'C'
            }
            
        self.project.id_increment = int(self.settings.value("Defaults/IDIncrement", 1))
        
        self.project.default_properties = {}
        self.settings.beginGroup("Defaults/Properties")
        for key in self.settings.childKeys():
            self.project.default_properties[key] = self.settings.value(key)
        self.settings.endGroup()
        
        if not self.project.default_properties:
            self.project.default_properties = {
                'node_elevation': '0', 'tank_diameter': '15', 'tank_height': '3',
                'pipe_length': '100', 'auto_length': 'Off',
                'pipe_diameter': '300', 'pipe_roughness': '100'
            }
    
    def save_settings(self):
        """Save window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
    # Edit Actions
    
    def select_all(self):
        """Select all items in the map."""
        if self.map_widget and self.map_widget.scene:
            for item in self.map_widget.scene.items():
                item.setSelected(True)
                
    def group_edit(self):
        """Open group edit dialog."""
        from gui.dialogs.group_edit_dialog import GroupEditDialog
        
        # Get selected items
        selected_items = self.map_widget.scene.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Group Edit", "Please select objects to edit.")
            return
            
        dialog = GroupEditDialog(self.project, selected_items, self)
        if dialog.exec():
            data = dialog.get_data()
            self.apply_group_edit(data, selected_items)
            
    def apply_group_edit(self, data, selected_items):
        """Apply group edit changes."""
        obj_type = data['type']
        prop = data['property']
        op = data['operation']
        val_str = data['value']
        
        try:
            value = float(val_str) if prop not in ["Tag", "Initial Status"] else val_str
        except ValueError:
            if prop not in ["Tag", "Initial Status"]:
                QMessageBox.warning(self, "Error", "Invalid numeric value.")
                return
                
        count = 0
        
        # Map property names to attribute names
        prop_map = {
            "Tag": "tag",
            "Elevation": "elevation",
            "Base Demand": "base_demand",
            "Initial Quality": "initial_quality",
            "Initial Level": "init_level",
            "Min Level": "min_level",
            "Max Level": "max_level",
            "Diameter": "diameter",
            "Length": "length",
            "Roughness": "roughness",
            "Loss Coeff.": "minor_loss",
            "Initial Status": "status",
            "Setting": "setting",
            "Total Head": "total_head"
        }
        
        attr = prop_map.get(prop)
        if not attr:
            return
            
        for item in selected_items:
            obj = None
            if hasattr(item, 'node'):
                obj = item.node
            elif hasattr(item, 'link'):
                obj = item.link
                
            if not obj:
                continue
                
            # Check type match (simple check)
            # Ideally strictly check against obj_type
            
            if hasattr(obj, attr):
                current_val = getattr(obj, attr)
                new_val = value
                
                if op == "Multiply" and isinstance(current_val, (int, float)):
                    new_val = current_val * value
                elif op == "Add" and isinstance(current_val, (int, float)):
                    new_val = current_val + value
                    
                setattr(obj, attr, new_val)
                count += 1
                
        if count > 0:
            self.project.modified = True
            self.browser_widget.refresh()
            self.status_bar.showMessage(f"Updated {count} objects.")
        else:
            self.status_bar.showMessage("No objects updated.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.check_save_changes():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
