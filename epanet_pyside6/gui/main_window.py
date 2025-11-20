"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QDockWidget, QToolBar, QStatusBar,
    QMenuBar, QFileDialog, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
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
        
        self.setup_ui()
        self.create_menus()
        self.create_toolbars()
        self.create_dock_widgets()
        self.create_status_bar()
        self.restore_settings()
        
        # Start with new project
        self.new_project()
    
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
        file_menu = menubar.addMenu("&File")
        
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
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Project Menu
        project_menu = menubar.addMenu("&Project")
        
        run_action = QAction("&Run Analysis", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_simulation)
        project_menu.addAction(run_action)
        
        # View Menu (will be populated with dock toggle actions when docks are created)
        self.view_menu = menubar.addMenu("&View")
        
        # Window Menu
        window_menu = menubar.addMenu("&Window")
        
        cascade_action = QAction("&Cascade", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_action)
        
        tile_action = QAction("&Tile", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbars(self):
        """Create toolbars."""
        # Standard toolbar
        std_toolbar = QToolBar("Standard")
        std_toolbar.setObjectName("StandardToolbar")
        self.addToolBar(std_toolbar)
        
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        std_toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        std_toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_project)
        std_toolbar.addAction(save_action)
        
        std_toolbar.addSeparator()
        
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_simulation)
        std_toolbar.addAction(run_action)
        
        std_toolbar.addSeparator()
        
        graph_action = QAction("Graph", self)
        graph_action.triggered.connect(self.create_graph)
        std_toolbar.addAction(graph_action)
        
        table_action = QAction("Table", self)
        table_action.triggered.connect(self.create_table)
        std_toolbar.addAction(table_action)
        
        contour_action = QAction("Contour", self)
        contour_action.triggered.connect(self.create_contour)
        std_toolbar.addAction(contour_action)
        
        status_action = QAction("Status", self)
        status_action.triggered.connect(self.create_status)
        std_toolbar.addAction(status_action)
        
        calib_action = QAction("Calibration", self)
        calib_action.triggered.connect(self.create_calibration)
        std_toolbar.addAction(calib_action)
        
        energy_action = QAction("Energy", self)
        energy_action.triggered.connect(self.create_energy)
        std_toolbar.addAction(energy_action)
    
    def create_dock_widgets(self):
        """Create dock widgets."""
        # Browser dock
        self.browser_dock = QDockWidget("Browser", self)
        self.browser_dock.setObjectName("BrowserDock")
        self.browser_widget = BrowserWidget(self.project)
        self.browser_dock.setWidget(self.browser_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.browser_dock)
        # Connect browser activation signal to handler
        try:
            self.browser_widget.objectActivated.connect(self.on_browser_object_activated)
        except Exception:
            pass
        
        # Property editor dock
        self.property_dock = QDockWidget("Property Editor", self)
        self.property_dock.setObjectName("PropertyDock")
        self.property_editor = PropertyEditor(self.project)
        self.property_dock.setWidget(self.property_editor)
        self.addDockWidget(Qt.RightDockWidgetArea, self.property_dock)
        # Connect property editor updates to handler so map/browser refresh
        try:
            self.property_editor.objectUpdated.connect(self.on_property_object_updated)
        except Exception:
            pass

        # Overview (mini) map dock
        try:
            self.ovmap_dock = QDockWidget("Overview Map", self)
            self.ovmap_dock.setObjectName("OVMapDock")
            self.ovmap_widget = OverviewMapWidget(self.map_widget)
            self.ovmap_dock.setWidget(self.ovmap_widget)
            # Put overview dock near the top-right by default
            self.addDockWidget(Qt.RightDockWidgetArea, self.ovmap_dock)
            # Add toggle to View menu
            if hasattr(self, 'view_menu') and self.view_menu is not None:
                self.view_menu.addAction(self.ovmap_dock.toggleViewAction())
        except Exception:
            pass

        # Add toggle actions to View menu so closed docks can be reopened
        try:
            if hasattr(self, 'view_menu') and self.view_menu is not None:
                # toggleViewAction returns a QAction that reflects dock visibility
                self.view_menu.addAction(self.browser_dock.toggleViewAction())
                self.view_menu.addAction(self.property_dock.toggleViewAction())
        except Exception:
            # Fail silently; view menu may not exist in some initialization orders
            pass
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def on_map_selection_changed(self, obj):
        """Handle selection changes in the map."""
        self.property_editor.set_object(obj)

    def on_browser_object_activated(self, obj_type: str, obj_id: str):
        """Handle activation from browser widget: select object in property editor and map."""
        try:
            if obj_type == 'Node':
                obj = self.project.network.get_node(obj_id)
            else:
                obj = self.project.network.get_link(obj_id)

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
            self.status_bar.showMessage("Simulation completed successfully")
            
        except Exception as e:
            dialog.append_log(f"Error: {str(e)}")
            dialog.simulation_finished(False)
            self.status_bar.showMessage("Simulation failed")
            
    # Views
    
    def create_graph(self):
        """Create a new graph window."""
        from gui.views import GraphView
        from core.constants import NodeType, LinkType
        
        # Get selected object from property editor or map
        # For now, we'll use the property editor's current object
        obj = self.property_editor.current_object
        
        if not obj:
            QMessageBox.warning(self, "Graph", "Please select a node or link first.")
            return
            
        # Determine type
        if hasattr(obj, 'node_type'):
            obj_type = 'Node'
        elif hasattr(obj, 'link_type'):
            obj_type = 'Link'
        else:
            return
            
        graph_view = GraphView(self.project)
        graph_view.set_object(obj_type, obj.id)
        
        subwindow = self.mdi_area.addSubWindow(graph_view)
        subwindow.setWindowTitle(f"Graph - {obj_type} {obj.id}")
        subwindow.show()
        subwindow.resize(600, 400)
        
    def create_table(self):
        """Create a new table window."""
        from gui.views import TableView
        
        table_view = TableView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(table_view)
        subwindow.setWindowTitle("Network Table")
        subwindow.show()
        subwindow.resize(800, 500)
        
    def create_contour(self):
        """Create a new contour window."""
        from gui.views import ContourView
        
        contour_view = ContourView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(contour_view)
        subwindow.setWindowTitle("Network Contour")
        subwindow.show()
        subwindow.resize(600, 500)
        
    def create_status(self):
        """Create a new status report window."""
        from gui.views import StatusView
        
        status_view = StatusView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(status_view)
        subwindow.setWindowTitle("Status Report")
        subwindow.show()
        subwindow.resize(500, 600)
        
    def create_calibration(self):
        """Create a new calibration window."""
        from gui.views import CalibrationView
        
        calib_view = CalibrationView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(calib_view)
        subwindow.setWindowTitle("Calibration")
        subwindow.show()
        subwindow.resize(900, 600)
        
    def create_energy(self):
        """Create a new energy report window."""
        from gui.views import EnergyView
        
        energy_view = EnergyView(self.project)
        
        subwindow = self.mdi_area.addSubWindow(energy_view)
        subwindow.setWindowTitle("Energy Report")
        subwindow.show()
        subwindow.resize(600, 400)
    
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
    
    def save_settings(self):
        """Save window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.check_save_changes():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
