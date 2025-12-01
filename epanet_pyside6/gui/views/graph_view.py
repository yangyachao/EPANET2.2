"""Graph view for simulation results."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QPushButton, QFileDialog
import pyqtgraph as pg
import pandas as pd
from core.constants import NodeParam, LinkParam

class GraphView(QWidget):
    """Widget for displaying time series graphs."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.object_id = None
        self.object_type = None # 'Node' or 'Link'
        self.param_type = None
        
        self.graph_options = {
            'show_grid': True,
            'show_legend': True,
            'white_background': True,
            'line_width': 2
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Controls area
        controls_layout = QHBoxLayout()
        
        self.param_combo = QComboBox()
        self.param_combo.currentTextChanged.connect(self.refresh_plot)
        controls_layout.addWidget(QLabel("Parameter:"))
        controls_layout.addWidget(self.param_combo)
        
        self.export_data_btn = QPushButton("Export Data")
        self.export_data_btn.clicked.connect(self.export_data)
        controls_layout.addWidget(self.export_data_btn)
        
        self.export_img_btn = QPushButton("Export Image")
        self.export_img_btn.clicked.connect(self.export_image)
        controls_layout.addWidget(self.export_img_btn)
        
        self.options_btn = QPushButton("Options...")
        self.options_btn.clicked.connect(self.show_options)
        controls_layout.addWidget(self.options_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Plot area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('bottom', 'Time (hours)')
        layout.addWidget(self.plot_widget)
        
    def set_data(self, graph_type, obj_type, obj_ids, param):
        """Set the data to plot."""
        self.graph_type = graph_type
        self.object_type = obj_type
        self.object_ids = obj_ids if isinstance(obj_ids, list) else [obj_ids]
        self.parameter = param
        
        # Update parameter combo
        self.param_combo.blockSignals(True)
        self.param_combo.clear()
        
        if graph_type == "System Flow":
            self.param_combo.addItem("System Flow", None)
            self.param_combo.setEnabled(False)
        else:
            self.param_combo.setEnabled(True)
            if obj_type == 'Node':
                for p in NodeParam:
                    self.param_combo.addItem(p.name, p)
            elif obj_type == 'Link':
                for p in LinkParam:
                    self.param_combo.addItem(p.name, p)
                    
            # Select current parameter
            if param:
                index = self.param_combo.findData(param)
                if index >= 0:
                    self.param_combo.setCurrentIndex(index)
            
        self.param_combo.blockSignals(False)
        
        # Refresh
        self.refresh_plot()
        
    def refresh_plot(self):
        """Refresh the plot data."""
        self.plot_widget.clear()
        
        # Apply options
        opts = self.graph_options
        self.plot_widget.setBackground('w' if opts['white_background'] else 'k')
        self.plot_widget.showGrid(x=opts['show_grid'], y=opts['show_grid'])
        
        if opts['show_legend']:
            self.plot_widget.addLegend()
        
        if not self.project.has_results():
            self.plot_widget.setTitle("No simulation results available")
            return
            
        try:
            if self.graph_type == "Time Series":
                self.plot_time_series()
            elif self.graph_type == "Profile":
                self.plot_profile()
            elif self.graph_type == "Frequency":
                self.plot_frequency()
            elif self.graph_type == "System Flow":
                self.plot_system_flow()
            else:
                self.plot_widget.setTitle(f"Unknown graph type: {self.graph_type}")
                
        except Exception as e:
            self.plot_widget.setTitle(f"Error: {str(e)}")
            print(f"Plot Error: {e}")
            import traceback
            traceback.print_exc()

    def get_pen(self, index):
        """Get pen for plotting."""
        colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
        if not self.graph_options['white_background']:
            colors = ['c', 'm', 'y', 'g', 'r', 'b', 'w']
        
        color = colors[index % len(colors)]
        width = self.graph_options['line_width']
        return pg.mkPen(color=color, width=width)

    def plot_time_series(self):
        """Plot time series."""
        if not self.object_ids: return
        param = self.param_combo.currentData()
        if not param: return
        
        self.plot_widget.setLabel('bottom', 'Time (hours)')
        self.plot_widget.setLabel('left', param.name)
        self.plot_widget.setTitle(f"{self.object_type} {param.name} - Time Series")
        
        for i, obj_id in enumerate(self.object_ids):
            times, values = self.project.get_time_series(self.object_type, obj_id, param)
            self.plot_widget.plot(times, values, pen=self.get_pen(i), name=f"{obj_id}")

    def plot_profile(self):
        """Plot profile along a path."""
        if len(self.object_ids) < 2: return
        start_node = self.object_ids[0]
        end_node = self.object_ids[1]
        param = self.param_combo.currentData()
        if not param: return
        
        # Find path
        import networkx as nx
        G = self.project.network.graph
        try:
            path = nx.shortest_path(G, start_node, end_node)
        except nx.NetworkXNoPath:
            self.plot_widget.setTitle(f"No path between {start_node} and {end_node}")
            return
            
        # Calculate distances and get values
        distances = [0]
        values = []
        current_dist = 0
        
        # Get current time step from project/engine if possible, otherwise use 0
        # For now, let's use time 0 or max? 
        # Ideally we should get the time from MainWindow.
        # But GraphView is standalone. Let's use the LAST time step for now, or 0.
        # Better: Average? Or maybe we can't easily get "current" time without passing it in.
        # Let's use the time step with maximum demand? Or just 0:00.
        # Let's default to 0 for now.
        t_idx = 0 
        
        # Get values for all nodes in path
        results = self.project.engine.results
        if not results: return
        
        # Map param to WNTR name
        param_map = {
            "ELEVATION": "elevation", "BASE_DEMAND": "base_demand", "DEMAND": "demand",
            "HEAD": "head", "PRESSURE": "pressure", "QUALITY": "quality",
            "INITIAL_QUALITY": "initial_quality"
        }
        wntr_param = param_map.get(param.name, param.name.lower())
        
        # Get node coordinates to calculate distance if link lengths not available?
        # WNTR graph edges have 'weight' which is length usually?
        # Let's calculate distance based on link lengths.
        
        node_res = results.node
        if wntr_param not in node_res:
            self.plot_widget.setTitle(f"Parameter {param.name} not found in results")
            return
            
        # Get values at t_idx
        # t_idx is index. times are in seconds.
        times = node_res[wntr_param].index
        t = times[t_idx]
        
        # Collect data
        x = []
        y = []
        
        for i, node in enumerate(path):
            # Value
            val = node_res[wntr_param].loc[t, node]
            y.append(val)
            
            # Distance
            if i > 0:
                prev_node = path[i-1]
                # Find link between prev_node and node
                link = self.project.network.get_link(prev_node, node) # This might not exist directly if not checking direction?
                # WNTR graph is undirected usually?
                # Actually self.project.network.get_link might search.
                # Let's try to get length from graph edge
                if G.has_edge(prev_node, node):
                    # Edge data might have length
                    # But WNTR MultiDiGraph...
                    # Let's just use coordinate distance if link length fails
                    dist = 0
                    # Try to find link object
                    link_name = None
                    # This is tricky in WNTR.
                    # Let's assume straight line distance if we can't find link length
                    n1 = self.project.network.nodes[prev_node]
                    n2 = self.project.network.nodes[node]
                    dx = n1.coordinates[0] - n2.coordinates[0]
                    dy = n1.coordinates[1] - n2.coordinates[1]
                    dist = (dx*dx + dy*dy)**0.5
                    current_dist += dist
            
            x.append(current_dist)
            
        self.plot_widget.setLabel('bottom', 'Distance')
        self.plot_widget.setLabel('left', param.name)
        self.plot_widget.setTitle(f"Profile: {start_node} to {end_node} - {param.name}")
        self.plot_widget.plot(x, y, pen=self.get_pen(0), symbol='o', name="Profile")

    def plot_frequency(self):
        """Plot cumulative frequency."""
        if not self.object_ids: return
        param = self.param_combo.currentData()
        if not param: return
        
        # Collect all values for all selected objects over all times
        all_values = []
        
        for obj_id in self.object_ids:
            _, values = self.project.get_time_series(self.object_type, obj_id, param)
            all_values.extend(values)
            
        if not all_values: return
        
        all_values.sort()
        n = len(all_values)
        y = [i/n * 100 for i in range(n)]
        
        self.plot_widget.setLabel('bottom', param.name)
        self.plot_widget.setLabel('left', 'Cumulative Frequency (%)')
        self.plot_widget.setTitle(f"Frequency Plot - {param.name}")
        self.plot_widget.plot(all_values, y, pen=self.get_pen(0), name="Frequency")

    def plot_system_flow(self):
        """Plot system flow (Produced, Consumed, Stored)."""
        results = self.project.engine.results
        if not results: return
        
        # 1. Total Consumption (Demand at Junctions)
        if 'demand' in results.node:
            demand = results.node['demand']
            junctions = [n.id for n in self.project.network.get_junctions()]
            if junctions:
                valid_junctions = [j for j in junctions if j in demand.columns]
                if valid_junctions:
                    consumed = demand[valid_junctions].sum(axis=1)
                else:
                    consumed = demand.sum(axis=1) * 0
            else:
                consumed = demand.sum(axis=1) * 0
        else:
            return

        # 2. Total Production (Net Outflow from Reservoirs)
        reservoirs = [n.id for n in self.project.network.get_reservoirs()]
        produced = pd.Series(0.0, index=consumed.index)
        
        if reservoirs and 'flowrate' in results.link:
            flow = results.link['flowrate']
            res_set = set(reservoirs)
            
            for link_id, link in self.project.network.links.items():
                if link_id not in flow.columns:
                    continue
                link_flow = flow[link_id]
                
                # If link starts at reservoir, it's outflow (production)
                if link.from_node in res_set:
                    produced += link_flow
                # If link ends at reservoir, it's inflow (negative production)
                if link.to_node in res_set:
                    produced -= link_flow

        # 3. Total Stored (Net Inflow to Tanks)
        tanks = [n.id for n in self.project.network.get_tanks()]
        stored = pd.Series(0.0, index=consumed.index)
        
        if tanks and 'flowrate' in results.link:
            flow = results.link['flowrate']
            tank_set = set(tanks)
            
            for link_id, link in self.project.network.links.items():
                if link_id not in flow.columns:
                    continue
                link_flow = flow[link_id]
                
                # If link ends at tank, it's inflow (storage)
                if link.to_node in tank_set:
                    stored += link_flow
                # If link starts at tank, it's outflow (negative storage/emptying)
                if link.from_node in tank_set:
                    stored -= link_flow
            
        times = consumed.index / 3600.0
        
        self.plot_widget.setLabel('bottom', 'Time (hours)')
        self.plot_widget.setLabel('left', 'Flow')
        self.plot_widget.setTitle("System Flow Balance")
        self.plot_widget.addLegend()
        
        self.plot_widget.plot(times, produced.values, pen=pg.mkPen('g', width=2), name="Produced")
        self.plot_widget.plot(times, consumed.values, pen=pg.mkPen('r', width=2), name="Consumed")
        self.plot_widget.plot(times, stored.values, pen=pg.mkPen('b', width=2), name="Stored")

    def show_options(self):
        """Show graph options dialog."""
        from gui.dialogs.graph_options_dialog import GraphOptionsDialog
        
        dialog = GraphOptionsDialog(self, self.graph_options)
        if dialog.exec():
            self.graph_options = dialog.get_options()
            self.refresh_plot()

    def export_data(self):
        """Export graph data to CSV."""
        if not self.object_ids:
            return
            
        param = self.param_combo.currentData()
        if not param:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                header = ["Time (hours)"]
                for obj_id in self.object_ids:
                    header.append(f"{obj_id} - {param.name}")
                writer.writerow(header)
                
                # Data
                # Get data for all objects
                all_data = []
                times = None
                for obj_id in self.object_ids:
                    t, v = self.project.get_time_series(self.object_type, obj_id, param)
                    if times is None:
                        times = t
                    all_data.append(v)
                
                # Write rows
                if times is not None:
                    for i, t in enumerate(times):
                        row = [t]
                        for data in all_data:
                            row.append(data[i] if i < len(data) else "")
                        writer.writerow(row)
                    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", str(e))
            
    def export_image(self):
        """Export graph as image."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Image", "", "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            # Use pyqtgraph exporter
            import pyqtgraph.exporters
            exporter = pyqtgraph.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(filename)
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", str(e))
