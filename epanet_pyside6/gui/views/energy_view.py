"""Energy analysis view."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QHeaderView, QTabWidget, QRadioButton, QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import pyqtgraph as pg


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
        self.table.setHorizontalHeaderLabels([
            "Pump", "Percent\nUtilization", "Average\nEfficiency", 
            "Kw-hr\nper m³", "Average\nKwatts", "Peak\nKwatts", "Cost\nper day"
        ])
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
        self.radio_kwhr = QRadioButton("Kw-hr per m³")
        self.radio_avg_kw = QRadioButton("Average Kwatts")
        self.radio_peak_kw = QRadioButton("Peak Kwatts")
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
            # Get pump energy statistics
            energy_stats = self._calculate_energy_stats()
            
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
                self.table.setItem(i, 3, QTableWidgetItem(f"{stats['kwhr_per_m3']:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{stats['avg_kw']:.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{stats['peak_kw']:.2f}"))
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
            
            # Refresh chart
            self.refresh_chart()
            
        except Exception as e:
            print(f"Error refreshing energy data: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_energy_stats(self):
        """Calculate energy statistics for all pumps."""
        try:
            import wntr.metrics.economic
            
            wn = self.project.engine.wn
            results = self.project.engine.results
            
            if not wn or not results:
                return {}
            
            # Get simulation duration
            times = results.node['pressure'].index
            duration_hours = (times[-1] - times[0]) / 3600.0
            
            # Get pumps
            pumps = [link_name for link_name, link in wn.links() if link.link_type == 'Pump']
            
            if not pumps:
                return {}
            
            energy_stats = {}
            
            for pump_id in pumps:
                pump = wn.get_link(pump_id)
                
                # Calculate pump power over time
                try:
                    pump_power = wntr.metrics.economic.pump_power(wn, results, pump_id)
                    
                    if pump_power is None or len(pump_power) == 0:
                        continue
                    
                    # Calculate statistics
                    avg_power_w = pump_power.mean()  # Watts
                    peak_power_w = pump_power.max()  # Watts
                    avg_kw = avg_power_w / 1000.0
                    peak_kw = peak_power_w / 1000.0
                    
                    # Energy consumption (kWh)
                    energy_kwh = (avg_power_w * duration_hours) / 1000.0
                    
                    # Utilization (percentage of time pump was on)
                    flow_series = results.link['flowrate'].loc[:, pump_id]
                    utilization = (flow_series > 0).sum() / len(flow_series) * 100.0
                    
                    # Efficiency (use global efficiency if available)
                    efficiency = getattr(wn.options.energy, 'global_efficiency', 75.0)
                    
                    # Volume pumped (m³)
                    volume_m3 = flow_series.sum() * (times[1] - times[0])  # flow * timestep
                    
                    # kWh per m³
                    kwhr_per_m3 = energy_kwh / volume_m3 if volume_m3 > 0 else 0.0
                    
                    # Cost calculation
                    price_per_kwh = getattr(wn.options.energy, 'global_price', 0.0)
                    cost_per_day = (energy_kwh / duration_hours) * 24.0 * price_per_kwh
                    
                    # Demand charge (based on peak kW)
                    demand_charge_rate = getattr(wn.options.energy, 'demand_charge', 0.0)
                    demand_charge = peak_kw * demand_charge_rate
                    
                    energy_stats[pump_id] = {
                        'utilization': utilization,
                        'efficiency': efficiency,
                        'kwhr_per_m3': kwhr_per_m3,
                        'avg_kw': avg_kw,
                        'peak_kw': peak_kw,
                        'cost_per_day': cost_per_day,
                        'demand_charge': demand_charge
                    }
                    
                except Exception as e:
                    print(f"Error calculating energy for pump {pump_id}: {e}")
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
        stat_keys = ['utilization', 'efficiency', 'kwhr_per_m3', 'avg_kw', 'peak_kw', 'cost_per_day']
        stat_labels = [
            "Percent Utilization", "Average Efficiency", "Kw-hr per m³",
            "Average Kwatts", "Peak Kwatts", "Cost per day"
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
