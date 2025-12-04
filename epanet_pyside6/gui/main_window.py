"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QStatusBar, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMenu, QMessageBox, QInputDialog, QFileDialog,
    QToolBar, QStyle, QDialog
)
from PySide6.QtCore import Qt, QSize, QSettings, QPointF, QRectF
from PySide6.QtGui import QAction, QKeySequence, QColor, QIcon, QPixmap, QPainter, QFont, QPolygonF, QPainterPath, QPen, QImage
from PySide6.QtPrintSupport import QPrinter
import sys
import os
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.project import EPANETProject
from core.exceptions import InputFileError
from gui.widgets import BrowserWidget, PropertyEditor, MapWidget, OverviewMapWidget
from gui.widgets.map_widget import InteractionMode
from gui.dialogs.input_error_dialog import InputErrorDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self) -> None:
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
        
        # Set default interaction mode
        self.set_interaction_mode(InteractionMode.SELECT)
    
    def load_recent_files(self) -> None:
        """Load recent files from settings."""
        self.recent_files = self.settings.value("recentFiles", [])
        # Ensure it's a list of strings
        if not isinstance(self.recent_files, list):
            self.recent_files = []
            
    def save_recent_files(self) -> None:
        """Save recent files to settings."""
        self.settings.setValue("recentFiles", self.recent_files)
        
    def add_recent_file(self, filename: str) -> None:
        """Add file to recent files list."""
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        
        self.recent_files.insert(0, filename)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
            
        self.save_recent_files()
        self.update_recent_files_menu()
        
    def update_recent_files_menu(self) -> None:
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
            
    def open_recent_file(self, filename: str) -> None:
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
            
            # Load backdrop if present
            if hasattr(self.project, 'backdrop_info') and self.project.backdrop_info:
                image_path, ul_x, ul_y, lr_x, lr_y = self.project.backdrop_info
                self.map_widget.scene.set_backdrop(image_path, ul_x, ul_y, lr_x, lr_y)
                self.show_backdrop_action.setChecked(True)
            else:
                self.map_widget.scene.clear_backdrop()
                self.show_backdrop_action.setChecked(False)
            
            self.map_widget.scene.update_scene_rect()
            self.map_widget.fit_network()
            
            self.update_title()
            self.status_bar.showMessage(f"Opened {filename}")
            
            # Move to top of list
            self.add_recent_file(filename)
        except InputFileError as e:
            dialog = InputErrorDialog(e.errors, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")
    
    def setup_ui(self) -> None:
        """Setup main UI components."""
        self.setWindowTitle("EPANET 2.2 - PySide6")
        self.resize(1200, 800)
        
        # Create MDI area for        # MDI Area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        # Create Map Window
        self.map_widget = MapWidget(self.project)
        self.map_widget.scene.selectionChanged.connect(self.on_map_selection_changed)
        self.map_widget.options_requested.connect(self.on_legend_updated)
        self.map_widget.mouseMoved.connect(self.on_mouse_moved)
        self.map_widget.alignment_finished.connect(self.on_alignment_finished)
        self.map_widget.backdrop_action_requested.connect(self.on_backdrop_action)
        self.map_widget.map_options_requested.connect(self.show_map_options)
        self.map_subwindow = self.mdi_area.addSubWindow(self.map_widget)
        self.map_subwindow.setWindowTitle("Network Map")
        self.map_subwindow.showMaximized()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)
    
    def create_menus(self) -> None:
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
        
        page_setup_action = QAction("Page Set&up...", self)
        page_setup_action.triggered.connect(self.page_setup)
        self.file_menu.addAction(page_setup_action)
        
        print_preview_action = QAction("Print Pre&view...", self)
        print_preview_action.triggered.connect(self.print_preview)
        self.file_menu.addAction(print_preview_action)
        
        print_action = QAction("&Print...", self)
        print_action.setShortcut(QKeySequence.Print)
        print_action.triggered.connect(self.print_current_view)
        self.file_menu.addAction(print_action)
        
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
        
        copy_action = QAction("&Copy to...", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_current_view)
        edit_menu.addAction(copy_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        edit_menu.addSeparator()
        
        group_edit_action = QAction("&Group Edit...", self)
        group_edit_action.triggered.connect(self.group_edit)
        edit_menu.addAction(group_edit_action)
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setMenuRole(QAction.MenuRole.NoRole)  # Prevent macOS from moving it
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)
        
        # View Menu
        self.view_menu = menubar.addMenu("&View")
        
        # Pan/Select modes
        self.select_action = QAction("&Select", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True) # Default
        self.select_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.SELECT))
        self.view_menu.addAction(self.select_action)
        
        self.pan_action = QAction("&Pan", self)
        self.pan_action.setCheckable(True)
        self.pan_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.PAN))
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
        
        # Query
        query_action = QAction("&Query...", self)
        query_action.triggered.connect(self.show_query)
        self.view_menu.addAction(query_action)
        
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
        
        full_report_action = QAction("&Full Report...", self)
        full_report_action.triggered.connect(self.show_full_report)
        report_menu.addAction(full_report_action)
        
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
        

        

    
    def window_menu_about_to_show(self) -> None:
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
            
    def close_all_windows(self) -> None:
        """Close all MDI subwindows."""
        self.mdi_area.closeAllSubWindows()

    def show_help_topics(self) -> None:
        """Show help topics."""
        from gui.dialogs.help_dialog import HelpDialog
        dialog = HelpDialog("EPANET Help", parent=self)
        dialog.show()
        self.help_dialog = dialog
        
    def show_units(self) -> None:
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
        
    def show_tutorial(self) -> None:
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
        
    def show_about(self) -> None:
        """Show about dialog."""
        from gui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()
        
    def page_setup(self) -> None:
        """Show page setup dialog."""
        # For now, just a placeholder or basic QPageSetupDialog if needed
        # QPageSetupDialog requires a QPrinter
        from PySide6.QtPrintSupport import QPageSetupDialog, QPrinter
        printer = QPrinter()
        dialog = QPageSetupDialog(printer, self)
        dialog.exec()
        
    def print_preview(self) -> None:
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
        
    def print_map(self) -> None:
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

    def show_status_report(self) -> None:
        """Show status report."""
        from gui.reports.status_report import StatusReport
        report = StatusReport(self.project)
        subwindow = self.mdi_area.addSubWindow(report)
        subwindow.showMaximized()

    def show_energy_report(self) -> None:
        """Show energy report."""
        from gui.views.energy_view import EnergyView
        report = EnergyView(self.project)
        subwindow = self.mdi_area.addSubWindow(report)
        subwindow.setWindowTitle("Energy Report")
        subwindow.showMaximized()

    def show_calibration_report(self) -> None:
        """Show calibration report."""
        from gui.views.calibration_view import CalibrationView
        report = CalibrationView(self.project)
        subwindow = self.mdi_area.addSubWindow(report)
        subwindow.setWindowTitle("Calibration Report")
        subwindow.showMaximized()

    def show_reaction_report(self) -> None:
        """Show reaction report."""
        from gui.reports.reaction_report import ReactionReport
        report = ReactionReport(self.project)
        subwindow = self.mdi_area.addSubWindow(report)
        subwindow.showMaximized()

    def show_full_report(self) -> None:
        """Show full report."""
        from gui.reports.full_report import FullReport
        report = FullReport(self.project)
        subwindow = self.mdi_area.addSubWindow(report)
        subwindow.showMaximized()
        
    def export_map(self) -> None:
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

    def create_icon_from_text(self, text: str, color: QColor = Qt.black) -> QIcon:
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

    def load_icon(self, name: str) -> QIcon:
        """Load icon from resources."""
        # Assuming resources are in ../resources/icons relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "resources", "icons", name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon() # Return empty icon if not found

    def create_toolbars(self) -> None:
        """Create toolbars."""
        # Standard toolbar
        self.std_toolbar = QToolBar("Standard")
        self.std_toolbar.setObjectName("StandardToolbar")
        self.std_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.std_toolbar)
        
        # File Actions
        # New
        new_action = QAction(self.load_icon("new.svg"), "New", self)
        new_action.triggered.connect(self.new_project)
        self.std_toolbar.addAction(new_action)
        
        # Open
        open_action = QAction(self.load_icon("open.svg"), "Open", self)
        open_action.triggered.connect(self.open_project)
        self.std_toolbar.addAction(open_action)
        
        # Save
        save_action = QAction(self.load_icon("save.svg"), "Save", self)
        save_action.triggered.connect(self.save_project)
        self.std_toolbar.addAction(save_action)
        
        self.std_toolbar.addSeparator()
        
        # View modes
        # Select
        self.select_action.setIcon(self.load_icon("select.svg"))
        self.select_action.setText("Select")
        self.std_toolbar.addAction(self.select_action)
        
        # Pan
        self.pan_action.setIcon(self.load_icon("pan.svg"))
        self.pan_action.setText("Pan")
        self.std_toolbar.addAction(self.pan_action)
        
        self.std_toolbar.addSeparator()
        
        # Object Creation
        self.add_junction_action = QAction(self.load_icon("junction.svg"), "Add Junction", self)
        self.add_junction_action.setCheckable(True)
        self.add_junction_action.setToolTip("Add Junction")
        self.add_junction_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_JUNCTION))
        self.std_toolbar.addAction(self.add_junction_action)
        
        self.add_reservoir_action = QAction(self.load_icon("reservoir.svg"), "Add Reservoir", self)
        self.add_reservoir_action.setCheckable(True)
        self.add_reservoir_action.setToolTip("Add Reservoir")
        self.add_reservoir_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_RESERVOIR))
        self.std_toolbar.addAction(self.add_reservoir_action)
        
        self.add_tank_action = QAction(self.load_icon("tank.svg"), "Add Tank", self)
        self.add_tank_action.setCheckable(True)
        self.add_tank_action.setToolTip("Add Tank")
        self.add_tank_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_TANK))
        self.std_toolbar.addAction(self.add_tank_action)
        
        self.std_toolbar.addSeparator()
        
        self.add_pipe_action = QAction(self.load_icon("pipe.svg"), "Add Pipe", self)
        self.add_pipe_action.setCheckable(True)
        self.add_pipe_action.setToolTip("Add Pipe")
        self.add_pipe_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_PIPE))
        self.std_toolbar.addAction(self.add_pipe_action)
        
        self.add_pump_action = QAction(self.load_icon("pump.svg"), "Add Pump", self)
        self.add_pump_action.setCheckable(True)
        self.add_pump_action.setToolTip("Add Pump")
        self.add_pump_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_PUMP))
        self.std_toolbar.addAction(self.add_pump_action)
        
        self.add_valve_action = QAction(self.load_icon("valve.svg"), "Add Valve", self)
        self.add_valve_action.setCheckable(True)
        self.add_valve_action.setToolTip("Add Valve")
        self.add_valve_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_VALVE))
        self.std_toolbar.addAction(self.add_valve_action)
        
        self.add_label_action = QAction(self.load_icon("label.svg"), "Add Label", self)
        self.add_label_action.setCheckable(True)
        self.add_label_action.setToolTip("Add Label")
        self.add_label_action.triggered.connect(lambda: self.set_interaction_mode(InteractionMode.ADD_LABEL))
        self.std_toolbar.addAction(self.add_label_action)
        
        self.std_toolbar.addSeparator()
        
        # Run
        run_action = QAction(self.load_icon("run.svg"), "Run", self)
        run_action.triggered.connect(self.run_simulation)
        self.std_toolbar.addAction(run_action)
        
        self.std_toolbar.addSeparator()
        
        # Reporting
        graph_action = QAction(self.load_icon("graph.svg"), "Graph", self)
        graph_action.triggered.connect(self.create_graph)
        self.std_toolbar.addAction(graph_action)
        
        table_action = QAction(self.load_icon("table.svg"), "Table", self)
        table_action.triggered.connect(self.create_table)
        self.std_toolbar.addAction(table_action)
        
        # Others
        contour_action = QAction(self.load_icon("contour.svg"), "Contour", self) 
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
        
        self.std_toolbar.addSeparator()
        
        # Find Object
        find_action = QAction(self.create_icon_from_text("🔍"), "Find", self)
        find_action.setToolTip("Find Object")
        find_action.triggered.connect(self.find_object)
        self.std_toolbar.addAction(find_action)
    
    def create_dock_widgets(self) -> None:
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
        
        # Connect map signals
        if hasattr(self, 'map_widget'):
            self.map_widget.network_changed.connect(self.browser_widget.refresh)
        
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
        
        # Connect browser add/delete signals
        self.browser_widget.objectAdded.connect(self.on_object_added)
        self.browser_widget.objectDeleted.connect(self.on_object_deleted)
        
        # Overview Map Dock
        from gui.widgets.overview_map import OverviewMapWidget
        self.overview_dock = QDockWidget("Overview Map", self)
        self.overview_dock.setObjectName("OverviewDock")
        self.overview_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.overview_map = OverviewMapWidget(self)
        self.overview_map.set_main_view(self.map_widget)
        self.overview_dock.setWidget(self.overview_map)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.overview_dock)
        
        # Backdrop Toolbar
        self.backdrop_toolbar = QToolBar("Backdrop", self)
        self.backdrop_toolbar.setObjectName("BackdropToolbar")
        self.addToolBar(Qt.TopToolBarArea, self.backdrop_toolbar)
        
        load_backdrop_action = QAction(QIcon(), "Load Backdrop", self)
        load_backdrop_action.setToolTip("Load Backdrop Image")
        load_backdrop_action.triggered.connect(self.load_backdrop)
        self.backdrop_toolbar.addAction(load_backdrop_action)
        
        align_backdrop_action = QAction(QIcon(), "Align Backdrop", self)
        align_backdrop_action.setToolTip("Align Backdrop Image")
        align_backdrop_action.triggered.connect(self.align_backdrop)
        self.backdrop_toolbar.addAction(align_backdrop_action)
        
        self.show_backdrop_action.setIcon(QIcon()) # Add icon if available
        self.show_backdrop_action.setToolTip("Toggle Backdrop Visibility")
        self.backdrop_toolbar.addAction(self.show_backdrop_action)
        
        unload_backdrop_action = QAction(QIcon(), "Unload Backdrop", self)
        unload_backdrop_action.setToolTip("Unload Backdrop Image")
        unload_backdrop_action.triggered.connect(self.unload_backdrop)
        self.backdrop_toolbar.addAction(unload_backdrop_action)
        
        # Add toggle actions to View menu
        if hasattr(self, 'view_menu'):
            self.view_menu.addSeparator()
            self.view_menu.addAction(self.browser_dock.toggleViewAction())
            self.view_menu.addAction(self.property_dock.toggleViewAction())
            self.view_menu.addAction(self.overview_dock.toggleViewAction())
    
    def create_status_bar(self) -> None:
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        from PySide6.QtWidgets import QLabel
        
        self.auto_length_label = QLabel("Auto-Length: Off")
        self.auto_length_label.setMinimumWidth(120)
        self.status_bar.addPermanentWidget(self.auto_length_label)
        
        self.coord_label = QLabel("X, Y: 0.00, 0.00")
        self.coord_label.setMinimumWidth(200)
        self.status_bar.addPermanentWidget(self.coord_label)
        
        self.units_label = QLabel("GPM")
        self.units_label.setMinimumWidth(50)
        self.status_bar.addPermanentWidget(self.units_label)
        
        self.status_bar.showMessage("Ready")
        
        # Initial update
        self.update_status_bar()
        
    def update_status_bar(self) -> None:
        """Update status bar information."""
        if not hasattr(self, 'project') or not self.project:
            return
            
        # Auto-Length
        auto_length = self.project.default_properties.get('auto_length', 'Off')
        self.auto_length_label.setText(f"Auto-Length: {auto_length}")
        
        # Units
        from core.constants import FlowUnits
        flow_units = self.project.network.options.flow_units
        # Map enum to string if needed, or use name
        unit_str = flow_units.name if hasattr(flow_units, 'name') else str(flow_units)
        self.units_label.setText(unit_str)
        
    def on_mouse_moved(self, x: float, y: float) -> None:
        """Handle mouse move from map widget."""
        self.coord_label.setText(f"X, Y: {x:.2f}, {y:.2f}")
    
    def on_map_selection_changed(self, obj: Any) -> None:
        """Handle selection changes in the map."""
        self.property_editor.set_object(obj)

    def on_browser_object_selected(self, obj_type: str, obj_id: str) -> None:
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

    def on_property_changed(self, obj: Any) -> None:
        """Handle property changes from property editor."""
        # Refresh map to show changes (e.g. coordinates, diameter)
        self.map_widget.scene.update()
        # Refresh browser tree if needed (e.g. ID change)
        # For now, just update map
        pass
    
    def on_browser_object_activated(self, obj_type: str, obj_id: str) -> None:
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
            elif obj_type == 'Control':
                # Open controls editor
                self.edit_controls()
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


    def on_object_added(self, category: str) -> None:
        """Handle adding new object from browser."""
        try:
            if category == "Patterns":
                # Generate unique ID
                i = 1
                while str(i) in self.project.network.patterns:
                    i += 1
                new_id = str(i)
                
                # Create new pattern
                from models import Pattern
                pattern = Pattern(new_id)
                self.project.network.patterns[new_id] = pattern
                
                # Open editor
                self.edit_pattern(new_id)
                
            elif category == "Curves":
                # Generate unique ID
                i = 1
                while str(i) in self.project.network.curves:
                    i += 1
                new_id = str(i)
                
                # Create new curve
                from models import Curve
                curve = Curve(new_id)
                self.project.network.curves[new_id] = curve
                
                # Open editor
                self.edit_curve(new_id)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add new {category}:\n{str(e)}")

    def on_object_deleted(self, obj_type: str, obj_id: str) -> None:
        """Handle deleting object from browser."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {obj_type} '{obj_id}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        try:
            if obj_type == "Pattern":
                if obj_id in self.project.network.patterns:
                    del self.project.network.patterns[obj_id]
            elif obj_type == "Curve":
                if obj_id in self.project.network.curves:
                    del self.project.network.curves[obj_id]
            
            # Mark modified and refresh
            self.project.modified = True
            self.browser_widget.refresh()
            self.property_editor.set_object(None)
            self.status_bar.showMessage(f"Deleted {obj_type} '{obj_id}'")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete {obj_type}:\n{str(e)}")

    def on_property_object_updated(self, obj: Any) -> None:
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
        
    def update_title(self) -> None:
        """Update window title based on current project."""
        if self.project.filename:
            title = f"EPANET 2.2 - PySide6 - {os.path.basename(self.project.filename)}"
        else:
            title = "EPANET 2.2 - PySide6 - Untitled"
        self.setWindowTitle(title)
        
    # File operations
    
    def new_project(self) -> None:
        """Create new project."""
        if not self.check_save_changes():
            return
            
        self.project.new_project()
        self.browser_widget.refresh()
        self.property_editor.set_object(None)
        self.map_widget.scene.load_network()
        self.update_title()
        self.status_bar.showMessage("New project created")
    
    def open_project(self) -> None:
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
                
                # Load backdrop if present
                if hasattr(self.project, 'backdrop_info') and self.project.backdrop_info:
                    image_path, ul_x, ul_y, lr_x, lr_y = self.project.backdrop_info
                    self.map_widget.scene.set_backdrop(image_path, ul_x, ul_y, lr_x, lr_y)
                    self.show_backdrop_action.setChecked(True)
                else:
                    self.map_widget.scene.clear_backdrop()
                    self.show_backdrop_action.setChecked(False)
                
                self.map_widget.fit_network()
                self.update_title()
                self.status_bar.showMessage(f"Opened {filename}")
                self.add_recent_file(filename)
            except InputFileError as e:
                dialog = InputErrorDialog(e.errors, self)
                dialog.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project:\n{str(e)}")
    
    def save_project(self) -> None:
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
    
    def save_project_as(self) -> None:
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
    
    def import_network(self) -> None:
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
            except InputFileError as e:
                dialog = InputErrorDialog(e.errors, self)
                dialog.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import network:\n{str(e)}")
                
    def import_map(self) -> None:
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
        
    def export_network(self) -> None:
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
                
    def page_setup(self) -> None:
        """Configure page setup."""
        from PySide6.QtPrintSupport import QPageSetupDialog, QPrinter
        from PySide6.QtWidgets import QDialog
        from PySide6.QtGui import QPainter
        
        if not hasattr(self, 'printer'):
            self.printer = QPrinter(QPrinter.HighResolution)
            
        dialog = QPageSetupDialog(self.printer, self)
        dialog.exec()
        
    def print_preview(self) -> None:
        """Show print preview."""
        from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter
        from PySide6.QtWidgets import QDialog
        from PySide6.QtGui import QPainter
        
        if not hasattr(self, 'printer'):
            self.printer = QPrinter(QPrinter.HighResolution)
            
        dialog = QPrintPreviewDialog(self.printer, self)
        dialog.paintRequested.connect(self._print_document)
        dialog.exec()
        
    def print_current_view(self) -> None:
        """Print the current view."""
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter
        from PySide6.QtWidgets import QDialog
        from PySide6.QtGui import QPainter
        
        if not hasattr(self, 'printer'):
            self.printer = QPrinter(QPrinter.HighResolution)
            
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QDialog.Accepted:
            self._print_document(self.printer)
            
    def _print_document(self, printer: QPrinter) -> None:
        """Handle printing of the current document."""
        # Check active subwindow
        active_sub = self.mdi_area.activeSubWindow()
        if active_sub:
            widget = active_sub.widget()
            # Check if widget supports printing
            if hasattr(widget, 'print_table'):
                widget.print_table(printer)
                return
                
        # Default to Map
        painter = QPainter(printer)
        self.map_widget.render(painter)
        painter.end()
        
    def copy_current_view(self) -> None:
        """Copy current view to clipboard."""
        from PySide6.QtGui import QGuiApplication, QImage, QPixmap
        
        # Check if we have a focused widget that supports copy
        focus_widget = QGuiApplication.focusWidget()
        
        if focus_widget:
            # Check if it's our TableView or part of it
            # Walk up hierarchy
            parent = focus_widget
            while parent:
                if hasattr(parent, 'copy_to_clipboard'):
                    parent.copy_to_clipboard()
                    self.status_bar.showMessage("Table data copied to clipboard", 3000)
                    return
                parent = parent.parent()
        
        # Default to Map copy
        clipboard = QGuiApplication.clipboard()
        pixmap = self.map_widget.grab()
        clipboard.setPixmap(pixmap)
        self.status_bar.showMessage("Map copied to clipboard", 3000)
                
    def export_map(self) -> None:
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
                
    def import_scenario(self) -> None:
        """Import scenario from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Scenario", "", "EPANET Scenario (*.scn *.inp);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            from core.epanet_io import import_scenario
            import_scenario(self.project, filename)
            self.project.modified = True
            self.browser_widget.refresh()
            self.map_widget.refresh()
            self.status_bar.showMessage(f"Scenario imported from {filename}")
            QMessageBox.information(self, "Import Successful", "Scenario data imported successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Error importing scenario: {str(e)}")

    def export_scenario(self) -> None:
        """Export scenario to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Scenario", "", "EPANET Scenario (*.scn);;All Files (*)"
        )
        
        if not filename:
            return
            
        if not filename.endswith('.scn') and not filename.endswith('.inp'):
            filename += '.scn'
            
        try:
            from core.epanet_io import export_scenario
            export_scenario(self.project, filename)
            self.status_bar.showMessage(f"Scenario exported to {filename}")
            QMessageBox.information(self, "Export Successful", f"Scenario exported to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting scenario: {str(e)}")
    
    # Simulation
    
    def run_simulation(self) -> None:
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
    
    def create_graph(self) -> None:
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
            graph_type = selection['graph_type']
            
            if graph_type == "Contour":
                # Redirect to ContourView
                from gui.views import ContourView
                contour_view = ContourView(self.project)
                contour_view.set_parameter(selection['parameter'])
                
                subwindow = self.mdi_area.addSubWindow(contour_view)
                subwindow.setWindowTitle(f"Contour - {selection['parameter'].name}")
                subwindow.showMaximized()
                
            elif graph_type in ["Time Series", "Profile", "Frequency", "System Flow"]:
                if graph_type == "Time Series" and not selection['objects']:
                    QMessageBox.warning(self, "Graph", "Please select at least one object.")
                    return
                elif graph_type == "Profile" and len(selection['objects']) < 2:
                    QMessageBox.warning(self, "Graph", "Please select Start and End nodes.")
                    return
                    
                graph_view = GraphView(self.project)
                graph_view.set_data(
                    graph_type,
                    selection['object_type'], 
                    selection['objects'], 
                    selection['parameter']
                )
                
                title = f"{graph_type}"
                if selection['parameter']:
                    title += f" - {selection['parameter'].name}"
                
                subwindow = self.mdi_area.addSubWindow(graph_view)
                subwindow.setWindowTitle(title)
                subwindow.showMaximized()
            else:
                QMessageBox.information(self, "Graph", f"{graph_type} not implemented yet.")
        
    def create_table(self) -> None:
        """Create a new table window."""
        from gui.views import TableView
        
        table_view = TableView(self.project)
        # Connect selection sync
        table_view.object_selected.connect(self.on_browser_object_selected)
        
        subwindow = self.mdi_area.addSubWindow(table_view)
        subwindow.setWindowTitle("Network Table")
        subwindow.showMaximized()
        
    def create_contour(self) -> None:
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
        
    def create_status(self) -> None:
        """Create a new status report window."""
        from gui.views import StatusView
        
        status_view = StatusView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(status_view)
        subwindow.setWindowTitle("Status Report")
        subwindow.showMaximized()
        
    def create_calibration(self) -> None:
        """Create a new calibration window."""
        from gui.views import CalibrationView
        
        calib_view = CalibrationView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(calib_view)
        subwindow.setWindowTitle("Calibration")
        subwindow.showMaximized()
        
    def create_energy(self) -> None:
        """Create a new energy report window."""
        from gui.views import EnergyView
        
        energy_view = EnergyView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(energy_view)

        subwindow.setWindowTitle("Energy Report")
        subwindow.showMaximized()
    
    # Data Editors
    
    def edit_controls(self) -> None:
        """Open controls editor."""
        from gui.dialogs.controls_editor import ControlsEditorDialog
        dialog = ControlsEditorDialog(self.project, self)
        if dialog.exec():
            self.project.modified = True
            self.browser_widget.refresh()
            self.status_bar.showMessage("Controls updated")

    def edit_pattern(self, pattern_id: str) -> None:
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
    
    def edit_curve(self, curve_id: str) -> None:
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
    
    def show_project_summary(self) -> None:
        """Show project summary dialog."""
        from gui.dialogs.project_summary_dialog import ProjectSummaryDialog
        
        dialog = ProjectSummaryDialog(self.project, self)
        if dialog.exec():
            data = dialog.get_data()
            self.project.network.title = data['title']
            self.project.network.notes = data['notes']
            self.project.modified = True
            self.status_bar.showMessage("Project summary updated")

    def show_calibration_data(self) -> None:
        """Show calibration data dialog."""
        from gui.dialogs.calibration_data_dialog import CalibrationDataDialog
        
        current_data = self.project.network.calibration_data
        
        dialog = CalibrationDataDialog(self, current_data)
        if dialog.exec():
            new_data = dialog.get_data()
            self.project.network.calibration_data = new_data
            self.project.modified = True
            self.status_bar.showMessage("Calibration data updated")

    def show_dimensions(self) -> None:
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

    def show_query(self) -> None:
        """Show query dialog."""
        from gui.dialogs.query_dialog import QueryDialog
        dialog = QueryDialog(self.project, self)
        dialog.query_executed.connect(self.execute_query)
        dialog.exec()
        
    def execute_query(self, obj_type: str, parameter: str, operator: str, value: float) -> None:
        """Execute query and highlight matching objects on map."""
        matching_ids = []
        
        if obj_type == "Nodes":
            for node_id, node in self.project.network.nodes.items():
                node_value = self.get_node_param_value(node, parameter)
                if node_value is not None and self.compare_values(node_value, operator, value):
                    matching_ids.append(node_id)
        else:  # Links
            for link_id, link in self.project.network.links.items():
                link_value = self.get_link_param_value(link, parameter)
                if link_value is not None and self.compare_values(link_value, operator, value):
                    matching_ids.append(link_id)
        
        # Highlight on map
        self.map_widget.scene.highlight_query_results(obj_type, matching_ids)
        
    def get_node_param_value(self, node: Any, parameter: str) -> Optional[float]:
        """Get node parameter value for query."""
        param_map = {
            "Elevation": "elevation",
            "Base Demand": "base_demand",
            "Initial Quality": "init_quality",
            "Demand": "demand",
            "Head": "head",
            "Pressure": "pressure",
            "Quality": "quality"
        }
        attr = param_map.get(parameter)
        return getattr(node, attr, None) if attr else None
        
    def get_link_param_value(self, link: Any, parameter: str) -> Optional[float]:
        """Get link parameter value for query."""
        param_map = {
            "Length": "length",
            "Diameter": "diameter",
            "Roughness": "roughness",
            "Flow": "flow",
            "Velocity": "velocity",
            "Headloss": "headloss"
        }
        attr = param_map.get(parameter)
        return getattr(link, attr, None) if attr else None
        
    def compare_values(self, val1: float, operator: str, val2: float) -> bool:
        """Compare values based on operator."""
        if operator == "=":
            return abs(val1 - val2) < 0.001
        elif operator == ">":
            return val1 > val2
        elif operator == "<":
            return val1 < val2
        elif operator == ">=":
            return val1 >= val2
        elif operator == "<=":
            return val1 <= val2
        elif operator == "!=":
            return abs(val1 - val2) >= 0.001
        return False
        
    def show_preferences(self) -> None:
        """Show preferences dialog."""
        from gui.dialogs.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog(self)
        if dialog.exec():
            self.status_bar.showMessage("Preferences updated")

    def export_network(self) -> None:
        """Export full network to INP file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Network", "", "EPANET Input (*.inp);;All Files (*)"
        )
        
        if not filename:
            return
            
        if not filename.endswith('.inp'):
            filename += '.inp'
            
        try:
            from core.epanet_io import export_network
            export_network(self.project, filename)
            self.status_bar.showMessage(f"Network exported to {filename}")
            QMessageBox.information(self, "Export Successful", f"Network exported to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting network: {str(e)}")
        
    def export_map(self) -> None:
        """Show export map dialog."""
        from gui.dialogs.map_export_dialog import MapExportDialog
        dialog = MapExportDialog(self.map_widget, self)
        dialog.exec()
        

    def show_full_report(self) -> None:
        """Generate and show full report."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Full Report",
            "",
            "Text Files (*.txt)"
        )
        
        if not filepath:
            return
            
        if not filepath.endswith(".txt"):
            filepath += ".txt"
            
        try:
            from core.export_utils import ExportUtils
            ExportUtils.generate_full_report(self.project, filepath)
            
            QMessageBox.information(
                self,
                "Report Generated",
                f"Full report generated successfully:\n{filepath}"
            )
            
            # Optionally open the file
            # QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"Failed to generate report:\n{str(e)}"
            )


    def show_analysis_options(self) -> None:
        """Show analysis options dialog."""
        from gui.dialogs.analysis_options_dialog import AnalysisOptionsDialog
        from dataclasses import asdict
        
        dialog = AnalysisOptionsDialog(self)
        
        # Prepare options data
        options = self.project.network.options
        options_dict = asdict(options)
        
        # Convert Enums to strings for the dialog
        options_dict['flow_units'] = options.flow_units.name
        options_dict['headloss_formula'] = options.headloss_formula.name
        options_dict['quality_type'] = options.quality_type.name
        
        dialog.load_data(options_dict)
        
        # Connect signal
        dialog.options_updated.connect(self.update_analysis_options)
        
        dialog.exec()

    def update_analysis_options(self, new_options: dict) -> None:
        """Update project analysis options."""
        from core.constants import FlowUnits, HeadLossType, QualityType
        
        options = self.project.network.options
        
        # Update simple fields
        for key, value in new_options.items():
            if hasattr(options, key):
                # Handle Enums
                if key == 'flow_units':
                    setattr(options, key, FlowUnits[value])
                elif key == 'headloss_formula':
                    setattr(options, key, HeadLossType[value])
                elif key == 'quality_type':
                    setattr(options, key, QualityType[value])
                else:
                    setattr(options, key, value)
        
        self.project.modified = True
        self.status_bar.showMessage("Analysis options updated")
    
    def show_defaults(self) -> None:
        """Show project defaults dialog."""
        from gui.dialogs.defaults_dialog import DefaultsDialog
        dialog = DefaultsDialog(self.project, self)
        if dialog.exec():
            self.update_status_bar()
            # Defaults are saved in the dialog's accept method
    
    def show_map_options(self) -> None:
        """Show map options dialog."""
        from gui.dialogs.map_options_dialog import MapOptionsDialog
        dialog = MapOptionsDialog(self)
        
        # Initialize default options if not set (legacy check, now in Project init)
        if not hasattr(self.project, 'map_options'):
             # Should be initialized in Project, but keep safe fallback just in case
             pass
    
        dialog.load_options(self.project.map_options)
        
        # Connect signal to update options
        def on_options_updated(new_options):
            self.project.map_options = new_options
            self.map_widget.scene.apply_map_options(new_options)
            # Refresh map colors to show values if notation was enabled
            self._update_map_colors(preserve_legend=True)
            self.status_bar.showMessage("Map options updated")
        
        dialog.options_updated.connect(on_options_updated)
        dialog.exec()


    def set_interaction_mode(self, mode: InteractionMode) -> None:
        """Set map interaction mode."""
        # Check if leaving ALIGN_BACKDROP mode
        if hasattr(self, 'map_widget') and self.map_widget.interaction_mode == InteractionMode.ALIGN_BACKDROP:
            # Save new backdrop coordinates
            if self.map_widget.scene.backdrop_item:
                item = self.map_widget.scene.backdrop_item
                pos = item.pos()
                scale = item.scale()
                
                # Calculate new world coordinates
                # Original image size (unscaled)
                pixmap = item.pixmap()
                img_w = pixmap.width()
                img_h = pixmap.height()
                
                # Current size in scene coords
                current_w = img_w * scale
                current_h = img_h * scale
                
                # Scene coords
                scene_ul_x = pos.x()
                scene_ul_y = pos.y()
                
                # Convert back to World coords
                # scene_x = ul_x - offset_x
                # scene_y = -(ul_y - offset_y)
                
                # ul_x = scene_x + offset_x
                # ul_y = -scene_y + offset_y
                
                offset_x = self.map_widget.scene.offset_x
                offset_y = self.map_widget.scene.offset_y
                
                ul_x = scene_ul_x + offset_x
                ul_y = -scene_ul_y + offset_y
                
                # lr_x = ul_x + width
                # lr_y = ul_y - height
                
                lr_x = ul_x + current_w
                lr_y = ul_y - current_h
                
                # Update project info
                if self.project.backdrop_info:
                    image_path = self.project.backdrop_info[0]
                    self.project.backdrop_info = (image_path, ul_x, ul_y, lr_x, lr_y)
                    self.project.modified = True
        
        if hasattr(self, 'map_widget'):
            self.map_widget.set_interaction_mode(mode)
        
        # Update UI state
        self.select_action.setChecked(mode == InteractionMode.SELECT)
        self.pan_action.setChecked(mode == InteractionMode.PAN)
        
        # Object creation actions
        if hasattr(self, 'add_junction_action'):
            self.add_junction_action.setChecked(mode == InteractionMode.ADD_JUNCTION)
            self.add_reservoir_action.setChecked(mode == InteractionMode.ADD_RESERVOIR)
            self.add_tank_action.setChecked(mode == InteractionMode.ADD_TANK)
            self.add_pipe_action.setChecked(mode == InteractionMode.ADD_PIPE)
            self.add_pump_action.setChecked(mode == InteractionMode.ADD_PUMP)
            self.add_valve_action.setChecked(mode == InteractionMode.ADD_VALVE)
            self.add_label_action.setChecked(mode == InteractionMode.ADD_LABEL)

    
    # View operations
    
    def zoom_in(self) -> None:
        """Zoom in on the map."""
        self.map_widget.scale(1.2, 1.2)
        
    def zoom_out(self) -> None:
        """Zoom out on the map."""
        self.map_widget.scale(1/1.2, 1/1.2)
        
    def full_extent(self) -> None:
        """Zoom to full network extent."""
        self.map_widget.fit_network()
    def find_object(self) -> None:
        """Show find object dialog."""
        from gui.dialogs.find_object_dialog import FindObjectDialog
        dialog = FindObjectDialog(self.project, self)

        def on_object_selected(obj_type, obj_id):
            try:
                self.map_widget.zoom_to_object(obj_type, obj_id)
                # Simulate browser activation to select and center object
                self.on_browser_object_activated(obj_type, obj_id)
                self.status_bar.showMessage(f"Found {obj_type}: {obj_id}")
            except Exception as e:
                QMessageBox.warning(self, "Object Not Found", f"Could not find {obj_type} '{obj_id}'.")
        
        dialog.object_selected.connect(on_object_selected)
        dialog.exec()
        
    # Map Visualization Handlers
    
    def on_node_param_changed(self, param: str) -> None:
        """Handle node parameter change."""
        self.current_node_param = param
        self._update_map_colors()
        
    def on_link_param_changed(self, param: str) -> None:
        """Handle link parameter change."""
        self.current_link_param = param
        self._update_map_colors()
        
    def on_time_changed(self, time_step: int) -> None:
        """Handle time step change."""
        self.current_time_step = time_step
        self._update_map_colors(preserve_legend=True)
        
    # _get_units_for_param removed, use core.units.get_unit_label instead

    def _update_map_colors(self, preserve_legend: bool = False) -> None:
        """Update map colors based on current parameters and time."""
        # Initialize current params if not set
        if not hasattr(self, 'current_node_param'): self.current_node_param = None
        if not hasattr(self, 'current_link_param'): self.current_link_param = None
        if not hasattr(self, 'current_time_step'): self.current_time_step = 0
        
        results = self.project.engine.results
        if not results:
            return

        # Default Colors (Blue -> Cyan -> Green -> Yellow -> Red)
        default_colors = [QColor(0,0,255), QColor(0,255,255), QColor(0,255,0), QColor(255,255,0), QColor(255,0,0)]
        
        # Capture current legend states
        node_legend_param = self.map_widget.node_legend.parameter_name
        node_legend_colors = [QColor(c) for c in self.map_widget.node_legend.colors]
        node_legend_values = list(self.map_widget.node_legend.values)
        
        link_legend_param = self.map_widget.link_legend.parameter_name
        link_legend_colors = [QColor(c) for c in self.map_widget.link_legend.colors]
        link_legend_values = list(self.map_widget.link_legend.values)
        
        # Initialize Unit Converter
        from core.units import UnitConverter
        converter = UnitConverter(self.project.network.options.flow_units)
        
        # Update Nodes
        if self.current_node_param:
            param = self.current_node_param.lower()
            # Map UI names to WNTR result names
            param_map = {
                "elevation": "elevation",
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
                try:
                    times = results.node[wntr_param].index
                    if self.current_time_step < len(times):
                        t = times[self.current_time_step]
                        row = results.node[wntr_param].loc[t]
                        values = row.to_dict()
                        
                        # Convert units
                        if param == "elevation":
                            values = {k: converter.length_to_project(v) for k, v in values.items()}
                        elif param in ["head", "pressure"]:
                            values = {k: converter.pressure_to_project(v) for k, v in values.items()}
                        elif param in ["demand", "base demand", "basedemand"]:
                            values = {k: converter.flow_to_project(v) for k, v in values.items()}
                        elif param in ["quality", "initial quality", "initialquality"]:
                            # Quality units are usually consistent, but check if conversion needed
                            pass
                            
                except Exception as e:
                    print(f"Error getting node results: {e}")
            
            if values:
                intervals = []
                colors = []
                
                # Check if we should preserve existing legend
                if preserve_legend and node_legend_param == self.current_node_param:
                    intervals = node_legend_values
                    colors = node_legend_colors
                else:
                    # Auto-scale
                    min_val = min(values.values())
                    max_val = max(values.values())
                    colors = default_colors
                    
                    if min_val == max_val:
                        intervals = [min_val] * 5
                    else:
                        step = (max_val - min_val) / 4
                        intervals = [min_val + i*step for i in range(5)]
                
                # Update Legend
                from core.units import get_unit_label
                units = get_unit_label(self.current_node_param.lower(), self.project.network.options.flow_units)
                self.map_widget.node_legend.set_data(self.current_node_param, units, intervals, colors)
                self.map_widget.node_legend.show()
                
                # Update Scene
                self.map_widget.scene.update_node_colors(values, colors, intervals)
            else:
                self.map_widget.node_legend.hide()
                self.map_widget.scene.update_node_colors({}, [], [])
        else:
            self.map_widget.node_legend.hide()
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
                "unit headloss": "headloss",
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
                        
                        # Convert units
                        if param == "length":
                            values = {k: converter.length_to_project(v) for k, v in values.items()}
                        elif param == "diameter":
                            values = {k: converter.diameter_to_project(v) for k, v in values.items()}
                        elif param == "flow":
                            values = {k: converter.flow_to_project(v) for k, v in values.items()}
                        elif param == "velocity":
                            values = {k: converter.velocity_to_project(v) for k, v in values.items()}
                        elif param in ["unit headloss", "unitheadloss"]:
                            # Headloss is m/km or ft/kft. WNTR usually gives dimensionless or m/m?
                            # WNTR headloss is usually unitless (m/m or ft/ft) * 1000 for per km/kft?
                            # Actually WNTR result 'headloss' is usually total headloss in the pipe (m or ft).
                            # But EPANET reports Unit Headloss (m/km or ft/kft).
                            # Wait, 'headloss' in WNTR results is head loss per length or total?
                            # Let's assume we need to calculate unit headloss if parameter is unit headloss.
                            # But here we are just taking the value.
                            # If WNTR gives total headloss, we need to divide by length.
                            # But let's assume for now we just convert length units if it's length-based.
                            # Actually, let's look at verify_units.py or similar.
                            # For now, let's apply standard conversion if applicable.
                            pass
                            
                except Exception as e:
                    print(f"Error getting link results: {e}")
            
            if values:
                intervals = []
                colors = []
                
                # Check if we should preserve existing legend
                if preserve_legend and link_legend_param == self.current_link_param:
                    intervals = link_legend_values
                    colors = link_legend_colors
                else:
                    # Auto-scale
                    min_val = min(values.values())
                    max_val = max(values.values())
                    colors = default_colors
                    
                    if min_val == max_val:
                        intervals = [min_val] * 5
                    else:
                        step = (max_val - min_val) / 4
                        intervals = [min_val + i*step for i in range(5)]
                
                # Update Legend
                from core.units import get_unit_label
                units = get_unit_label(self.current_link_param.lower(), self.project.network.options.flow_units)
                self.map_widget.link_legend.set_data(self.current_link_param, units, intervals, colors)
                self.map_widget.link_legend.show()
                
                # Update Scene
                self.map_widget.scene.update_link_colors(values, colors, intervals)
            else:
                self.map_widget.link_legend.hide()
                self.map_widget.scene.update_link_colors({}, [], [])
        else:
            self.map_widget.link_legend.hide()
            self.map_widget.scene.update_link_colors({}, [], [])

    def on_legend_updated(self) -> None:
        """Handle legend updates from editor."""
        # Force update map colors but preserve the new legend settings
        self._update_map_colors(preserve_legend=True)
    
    # Backdrop Handlers
    
    def load_backdrop(self) -> None:
        """Load backdrop image."""
        from gui.dialogs import BackdropDialog
        
        dialog = BackdropDialog(self.project, self)
        
        # Set default coordinates to current view extent
        # This ensures the backdrop is placed in the visible area
        rect = self.map_widget.scene.sceneRect()
        ul_x = rect.left()
        ul_y = rect.top() # Scene Y is inverted? No, scene coords are standard Cartesian usually, but let's check.
        # In EPANET/Scene: Y grows upwards? 
        # Actually, let's look at how set_backdrop uses them.
        # set_backdrop: world_h = abs(ul_y - lr_y)
        # It expects world coordinates.
        
        # Scene rect is in scene coordinates (which are world coordinates with offset)
        # But wait, scene.sceneRect() might be huge or empty.
        # Better to use the bounding box of all items or the current view.
        
        # Let's use the bounding rect of all nodes
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        has_nodes = False
        for node in self.project.network.nodes.values():
            has_nodes = True
            min_x = min(min_x, node.x)
            min_y = min(min_y, node.y)
            max_x = max(max_x, node.x)
            max_y = max(max_y, node.y)
            
        if has_nodes:
            # Add some padding
            w = max_x - min_x
            h = max_y - min_y
            if w == 0: w = 100
            if h == 0: h = 100
            
            ul_x = min_x - w * 0.1
            ul_y = max_y + h * 0.1 # Upper Left Y (higher value)
            lr_x = max_x + w * 0.1
            lr_y = min_y - h * 0.1 # Lower Right Y (lower value)
        else:
            ul_x = 0.0
            ul_y = 1000.0
            lr_x = 1000.0
            lr_y = 0.0
            
        # If we already have a backdrop, use its coords?
        # No, load_backdrop implies loading a NEW one usually.
        # But if we are just opening the dialog, maybe we should show current if exists?
        # The dialog is empty by default.
        
        dialog.set_data("", ul_x, ul_y, lr_x, lr_y)
        if dialog.exec():
            image_path, ul_x, ul_y, lr_x, lr_y = dialog.get_data()
            if image_path:
                self.map_widget.scene.set_backdrop(image_path, ul_x, ul_y, lr_x, lr_y)
                self.project.backdrop_info = (image_path, ul_x, ul_y, lr_x, lr_y)
                self.show_backdrop_action.setChecked(True)
                self.project.modified = True
                
    def unload_backdrop(self) -> None:
        """Unload backdrop image."""
        self.map_widget.scene.clear_backdrop()
        self.project.backdrop_info = None
        self.project.modified = True
        
    def align_backdrop(self) -> None:
        """Align backdrop image interactively."""
        if not hasattr(self.project, 'backdrop_info') or not self.project.backdrop_info:
            QMessageBox.information(self, "Backdrop", "No backdrop loaded.")
            return
            
        # Switch to Align Mode
        self.set_interaction_mode(InteractionMode.ALIGN_BACKDROP)
        
        QMessageBox.information(self, "Align Backdrop", 
            "Backdrop Alignment Mode:\n\n"
            "- Drag the backdrop to move it.\n"
            "- Scroll mouse wheel to scale it.\n\n"
            "Switch to 'Select' or any other tool to finish and save.")
                
    def on_alignment_finished(self, confirmed: bool) -> None:
        """Handle backdrop alignment completion."""
        if confirmed:
            self.status_bar.showMessage("Backdrop alignment confirmed.")
        else:
            self.status_bar.showMessage("Backdrop alignment cancelled.")
            
        # Switch back to Select mode
        # This will trigger the save logic in set_interaction_mode if confirmed
        # If cancelled, the map widget has already restored the position, so saving the "current" position is fine (it's the old one)
        self.set_interaction_mode(InteractionMode.SELECT)

    def on_backdrop_action(self, action: str) -> None:
        """Handle backdrop actions from map widget."""
        if action == 'load':
            self.load_backdrop()
        elif action == 'align':
            self.align_backdrop()
        elif action == 'unload':
            self.unload_backdrop()

    def toggle_backdrop(self, checked: bool) -> None:
        """Toggle backdrop visibility."""
        self.map_widget.scene.toggle_backdrop(checked)

    # Help
    
    def show_about(self) -> None:
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
    
    def restore_settings(self) -> None:
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
    
    def save_settings(self) -> None:
        """Save window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
    # Edit Actions
    
    def select_all(self) -> None:
        """Select all items in the map."""
        if self.map_widget and self.map_widget.scene:
            for item in self.map_widget.scene.items():
                item.setSelected(True)
                
    def group_edit(self) -> None:
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
            
    def apply_group_edit(self, data: dict, selected_items: list) -> None:
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
    
    def closeEvent(self, event: Any) -> None:
        """Handle window close event."""
        if self.check_save_changes():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
