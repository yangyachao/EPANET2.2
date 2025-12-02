"""Energy analysis view."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QHeaderView, QTabWidget, QRadioButton, QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import pyqtgraph as pg
from core.constants import FlowUnits

class EnergyView(QWidget):
    """Widget for displaying pump energy analysis."""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Tab widget for Table and Chart views
        self.tab_widget = QTabWidget()
        
        # Table tab
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        # Headers will be set in refresh_data based on units
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.table)
        
        self.tab_widget.addTab(table_widget, "Table")
        
        # Chart tab
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        
        # Radio buttons for selecting statistic
        radio_group_box = QGroupBox("Compare")
        radio_layout = QVBoxLayout(radio_group_box)
        
        self.radio_group = QButtonGroup()
        self.radio_utilization = QRadioButton("Percent Utilization")
        self.radio_efficiency = QRadioButton("Average Efficiency")
        self.radio_kwhr = QRadioButton("Kw-hr per m³") # Will update label
        self.radio_avg_kw = QRadioButton("Average Kwatts") # Will update label
        self.radio_peak_kw = QRadioButton("Peak Kwatts") # Will update label
        self.radio_cost = QRadioButton("Cost per day")
        
        self.radio_group.addButton(self.radio_utilization, 0)
        self.radio_group.addButton(self.radio_efficiency, 1)
        self.radio_group.addButton(self.radio_kwhr, 2)
        self.radio_group.addButton(self.radio_avg_kw, 3)
        self.radio_group.addButton(self.radio_peak_kw, 4)
        self.radio_group.addButton(self.radio_cost, 5)
        
        radio_layout.addWidget(self.radio_utilization)
        radio_layout.addWidget(self.radio_efficiency)
        radio_layout.addWidget(self.radio_kwhr)
        radio_layout.addWidget(self.radio_avg_kw)
        radio_layout.addWidget(self.radio_peak_kw)
        radio_layout.addWidget(self.radio_cost)
        
        self.radio_kwhr.setChecked(True)
        self.radio_group.buttonClicked.connect(self.refresh_chart)
        
        # Chart
        self.chart = pg.PlotWidget()
        self.chart.setBackground('w')
        self.chart.showGrid(x=True, y=True, alpha=0.3)
        
        chart_h_layout = QHBoxLayout()
        chart_h_layout.addWidget(radio_group_box)
        chart_h_layout.addWidget(self.chart, stretch=1)
        chart_layout.addLayout(chart_h_layout)
        
        self.tab_widget.addTab(chart_widget, "Chart")
        
        layout.addWidget(self.tab_widget)
        
    def refresh_data(self):
        """Refresh energy data."""
        self.table.setRowCount(0)
        
        if not self.project.has_results():
            return
        
        try:
            # Determine units
            flow_units = self.project.network.options.flow_units
            is_si = flow_units in [
                FlowUnits.LPS, FlowUnits.LPM, FlowUnits.MLD, 
                FlowUnits.CMH, FlowUnits.CMD
            ]
            
            # Set labels
            vol_unit = "m³" if is_si else "Mgal"
            power_unit = "kW" if is_si else "HP"
            
            kwhr_label = f"Kw-hr per {vol_unit}"
            avg_power_label = f"Average {power_unit}"
            peak_power_label = f"Peak {power_unit}"
            
            # Update Table Headers
            self.table.setHorizontalHeaderLabels([
                "Pump", "Percent\nUtilization", "Average\nEfficiency", 
                kwhr_label.replace(" ", "\n"), avg_power_label.replace(" ", "\n"), 
                peak_power_label.replace(" ", "\n"), "Cost\nper day"
            ])
            
            # Update Radio Buttons
            self.radio_kwhr.setText(kwhr_label)
            self.radio_avg_kw.setText(avg_power_label)
            self.radio_peak_kw.setText(peak_power_label)
            
            # Get pump energy statistics
            energy_stats = self._calculate_energy_stats(is_si)
            
            if not energy_stats:
                return
            
            # Populate table
            num_pumps = len(energy_stats)
            self.table.setRowCount(num_pumps + 2)  # +2 for Total Cost and Demand Charge rows
            
            total_cost = 0.0
            demand_charge = 0.0
            
            for i, (pump_id, stats) in enumerate(energy_stats.items()):
                self.table.setItem(i, 0, QTableWidgetItem(pump_id))
                self.table.setItem(i, 1, QTableWidgetItem(f"{stats['utilization']:.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{stats['efficiency']:.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{stats['kwhr_per_vol']:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{stats['avg_power']:.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{stats['peak_power']:.2f}"))
                self.table.setItem(i, 6, QTableWidgetItem(f"{stats['cost_per_day']:.2f}"))
                
                total_cost += stats['cost_per_day']
                demand_charge += stats.get('demand_charge', 0.0)
            
            # Add summary rows
            total_row = num_pumps
            demand_row = num_pumps + 1
            
            # Total Cost row
            total_item = QTableWidgetItem("Total Cost")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(total_row, 0, total_item)
            for col in range(1, 6):
                empty_item = QTableWidgetItem("")
                empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(total_row, col, empty_item)
            cost_item = QTableWidgetItem(f"{total_cost:.2f}")
            cost_item.setFlags(cost_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(total_row, 6, cost_item)
            
            # Demand Charge row
            demand_item = QTableWidgetItem("Demand Charge")
            demand_item.setFlags(demand_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(demand_row, 0, demand_item)
            for col in range(1, 6):
                empty_item = QTableWidgetItem("")
                empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(demand_row, col, empty_item)
            demand_cost_item = QTableWidgetItem(f"{demand_charge:.2f}")
            demand_cost_item.setFlags(demand_cost_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(demand_row, 6, demand_cost_item)
            
            # Store stats for chart
            self.energy_stats = energy_stats
            self.current_units = {'vol': vol_unit, 'power': power_unit}
            
            # Refresh chart
            self.refresh_chart()
            
        except Exception as e:
            print(f"Error refreshing energy data: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_energy_stats(self, is_si):
        """Calculate energy statistics for all pumps."""
        try:
            wn = self.project.engine.wn
            results = self.project.engine.results
            
            if not wn or not results:
                return {}
            
            # Get simulation duration
            times = results.node['pressure'].index
            duration_hours = (times[-1] - times[0]) / 3600.0
            timestep_hours = (times[1] - times[0]) / 3600.0 if len(times) > 1 else 1.0
            
            # Get pumps
            pumps = [link_name for link_name, link in wn.links() if link.link_type == 'Pump']
            
            if not pumps:
                return {}
            
            energy_stats = {}
            
            # Constants
            # US: HP = GPM * ft / 3960 / efficiency
            # SI: kW = LPS * m * 9.81 / 1000 / efficiency (approx) or use rho*g*Q*H
            
            for pump_id in pumps:
                try:
                    pump = wn.get_link(pump_id)
                    
                    # Get flow rates (Project Units)
                    if 'flowrate' not in results.link:
                        continue
                    flow_series = results.link['flowrate'].loc[:, pump_id]
                    
                    # Get start and end nodes
                    start_node = pump.start_node_name
                    end_node = pump.end_node_name
                    
                    # Get heads at start and end nodes (Project Units)
                    if 'head' not in results.node:
                        continue
                    head_start = results.node['head'].loc[:, start_node]
                    head_end = results.node['head'].loc[:, end_node]
                    
                    # Calculate head gain
                    head_gain = head_end - head_start
                    
                    # Get efficiency (use global efficiency)
                    efficiency = getattr(wn.options.energy, 'global_efficiency', 75.0) / 100.0
                    if efficiency <= 0:
                        efficiency = 0.75
                    
                    # Calculate Power
                    if is_si:
                        # Assuming Flow is in LPS (most common SI) or similar. 
                        # Need to convert to m³/s for rho*g*Q*H
                        # But wait, we need to know EXACT flow unit.
                        flow_units = self.project.network.options.flow_units
                        
                        # Conversion to m³/s
                        q_conv = 1.0
                        if flow_units == FlowUnits.LPS: q_conv = 0.001
                        elif flow_units == FlowUnits.LPM: q_conv = 1.6667e-5
                        elif flow_units == FlowUnits.MLD: q_conv = 0.01157
                        elif flow_units == FlowUnits.CMH: q_conv = 0.0002778
                        elif flow_units == FlowUnits.CMD: q_conv = 1.157e-5
                        
                        # Power (kW) = (Q_m3s * H_m * 9810) / (1000 * efficiency)
                        #            = (Q_m3s * H_m * 9.81) / efficiency
                        power_series = (flow_series.abs() * q_conv * head_gain * 9.81) / efficiency
                        
                    else: # US Units
                        # Assuming Flow in GPM, Head in ft
                        # HP = (Q_gpm * H_ft) / (3960 * efficiency)
                        # Need to handle other US units?
                        flow_units = self.project.network.options.flow_units
                        
                        # Convert to GPM first if needed
                        q_conv = 1.0
                        if flow_units == FlowUnits.CFS: q_conv = 448.831
                        elif flow_units == FlowUnits.MGD: q_conv = 694.444
                        elif flow_units == FlowUnits.IMGD: q_conv = 833.333 # Imperial MGD -> US GPM? Or Imperial GPM?
                        elif flow_units == FlowUnits.AFD: q_conv = 226.286
                        
                        # Calculate HP
                        # Note: If flow is not GPM, we convert to GPM
                        q_gpm = flow_series.abs() * q_conv
                        power_series = (q_gpm * head_gain) / (3960.0 * efficiency)
                    
                    # Replace negative or NaN values with 0
                    power_series = power_series.fillna(0)
                    power_series[power_series < 0] = 0
                    
                    # Calculate statistics
                    avg_power = power_series.mean()
                    peak_power = power_series.max()
                    
                    # Energy consumption (kWh)
                    # If SI: Power is kW. Energy = Sum(kW * dt)
                    # If US: Power is HP. Convert to kW for energy. 1 HP = 0.7457 kW
                    kw_conversion = 1.0 if is_si else 0.7457
                    
                    energy_kwh = (power_series.sum() * timestep_hours) * kw_conversion
                    
                    # Utilization (percentage of time pump was on)
                    utilization = (flow_series.abs() > 1e-6).sum() / len(flow_series) * 100.0
                    
                    # Volume pumped
                    # SI: m³
                    # US: Mgal
                    
                    if is_si:
                        # Flow in Project Units. Convert to m³/s then * seconds -> m³
                        # Reuse q_conv from above (to m³/s)
                        flow_units = self.project.network.options.flow_units
                        q_conv = 1.0
                        if flow_units == FlowUnits.LPS: q_conv = 0.001
                        elif flow_units == FlowUnits.LPM: q_conv = 1.6667e-5
                        elif flow_units == FlowUnits.MLD: q_conv = 0.011574
                        elif flow_units == FlowUnits.CMH: q_conv = 1.0/3600.0
                        elif flow_units == FlowUnits.CMD: q_conv = 1.0/86400.0
                        
                        volume = flow_series.abs().sum() * q_conv * (times[1] - times[0]) # m³
                        
                    else:
                        # US: Convert to Mgal
                        # Flow in Project Units.
                        flow_units = self.project.network.options.flow_units
                        
                        # Convert to GPM first
                        q_conv_gpm = 1.0
                        if flow_units == FlowUnits.CFS: q_conv_gpm = 448.831
                        elif flow_units == FlowUnits.MGD: q_conv_gpm = 694.444
                        elif flow_units == FlowUnits.AFD: q_conv_gpm = 226.286
                        
                        total_gallons = flow_series.abs().sum() * q_conv_gpm * (times[1] - times[0]) / 60.0 # GPM * min
                        # Wait, timestep is seconds.
                        # GPM * (dt_sec / 60) = Gallons
                        
                        volume = total_gallons / 1000000.0 # Mgal
                    
                    # kWh per Volume
                    kwhr_per_vol = energy_kwh / volume if volume > 1e-6 else 0.0
                    
                    # Cost calculation
                    price_per_kwh = getattr(wn.options.energy, 'global_price', 0.0)
                    cost_per_day = (energy_kwh / duration_hours) * 24.0 * price_per_kwh
                    
                    # Demand charge (based on peak kW)
                    demand_charge_rate = getattr(wn.options.energy, 'demand_charge', 0.0)
                    peak_kw_val = peak_power if is_si else peak_power * 0.7457
                    demand_charge = peak_kw_val * demand_charge_rate
                    
                    energy_stats[pump_id] = {
                        'utilization': utilization,
                        'efficiency': efficiency * 100.0,
                        'kwhr_per_vol': kwhr_per_vol,
                        'avg_power': avg_power,
                        'peak_power': peak_power,
                        'cost_per_day': cost_per_day,
                        'demand_charge': demand_charge
                    }
                    
                except Exception as e:
                    print(f"Error calculating energy for pump {pump_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return energy_stats
            
        except Exception as e:
            print(f"Error in _calculate_energy_stats: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def refresh_chart(self):
        """Refresh the chart based on selected statistic."""
        self.chart.clear()
        
        if not hasattr(self, 'energy_stats') or not self.energy_stats:
            return
        
        # Get selected statistic
        selected_id = self.radio_group.checkedId()
        stat_keys = ['utilization', 'efficiency', 'kwhr_per_vol', 'avg_power', 'peak_power', 'cost_per_day']
        
        # Get labels from radio buttons
        stat_labels = [
            self.radio_utilization.text(),
            self.radio_efficiency.text(),
            self.radio_kwhr.text(),
            self.radio_avg_kw.text(),
            self.radio_peak_kw.text(),
            self.radio_cost.text()
        ]
        
        if selected_id < 0 or selected_id >= len(stat_keys):
            return
        
        stat_key = stat_keys[selected_id]
        stat_label = stat_labels[selected_id]
        
        # Prepare data
        pump_ids = list(self.energy_stats.keys())
        values = [self.energy_stats[pid][stat_key] for pid in pump_ids]
        
        # Filter out pumps with zero utilization
        filtered_data = [(pid, val) for pid, val in zip(pump_ids, values) 
                         if self.energy_stats[pid]['utilization'] > 0]
        
        if not filtered_data:
            return
        
        pump_ids, values = zip(*filtered_data)
        
        # Create bar chart
        x = list(range(len(pump_ids)))
        bar_graph = pg.BarGraphItem(x=x, height=values, width=0.6, brush='b')
        self.chart.addItem(bar_graph)
        
        # Set labels
        self.chart.setTitle(stat_label)
        self.chart.setLabel('bottom', 'Pump ID')
        self.chart.setLabel('left', stat_label)
        
        # Set x-axis labels
        ax = self.chart.getAxis('bottom')
        ax.setTicks([[(i, pid) for i, pid in enumerate(pump_ids)]])
