"""EPANET Project management."""

from typing import Optional, Callable, Any, Tuple, Dict
import wntr
from .engine import Engine
from .network import Network
from .constants import *
from models import Junction, Reservoir, Tank, Pipe, Pump, Valve


class EPANETProject:
    """EPANET project manager using WNTR."""
    
    def __init__(self):
        """Initialize project."""
        self.engine = Engine()
        self.network = Network()
        self.filename = ""
        self.modified = False
        self._has_results = False
        self.last_report = "No simulation run yet."
    
    def new_project(self):
        """Create a new empty project."""
        self.network.clear()
        self.engine.close_project()
        self.filename = ""
        self.modified = False
        self._has_results = False
    
    def open_project(self, filename: str):
        """Open a project from file."""
        try:
            self.engine.open_project(filename)
            self._load_network_from_wntr()
            self.filename = filename
            self.modified = False
            self._has_results = False
        except Exception as e:
            raise Exception(f"Failed to open project: {e}")
    
    def save_project(self, filename: Optional[str] = None):
        """Save project to file."""
        if filename is None:
            filename = self.filename
        if not filename:
            raise ValueError("No filename specified")
            
        try:
            # Sync network model back to WNTR object before saving
            self._sync_network_to_wntr()
            self.engine.save_project(filename)
            self.filename = filename
            self.modified = False
        except Exception as e:
            raise Exception(f"Failed to save project: {e}")

    def _sync_network_to_wntr(self):
        """Sync internal network model to WNTR model."""
        import wntr
        
        # Create WNTR model if it doesn't exist
        if not self.engine.wn:
            self.engine.wn = wntr.network.WaterNetworkModel()
            
        wn = self.engine.wn
            
        # Project Info
        if hasattr(wn, 'title'):
            wn.title = self.network.title
            
        # Nodes
        for node in self.network.nodes.values():
            # Add node if not exists
            if node.id not in wn.nodes:
                if node.node_type == NodeType.JUNCTION:
                    wn.add_junction(node.id, elevation=node.elevation, coordinates=(node.x, node.y))
                elif node.node_type == NodeType.RESERVOIR:
                    wn.add_reservoir(node.id, base_head=node.total_head, coordinates=(node.x, node.y))
                elif node.node_type == NodeType.TANK:
                    # WNTR uses meters for diameter, EPANET uses mm for metric units
                    wn.add_tank(node.id, elevation=node.elevation, init_level=node.init_level, 
                               min_level=node.min_level, max_level=node.max_level, 
                               diameter=node.diameter / 1000.0, coordinates=(node.x, node.y))  # Convert mm to m
            
            # Update properties
            if node.id in wn.nodes:
                wn_node = wn.nodes[node.id]
                wn_node.coordinates = (node.x, node.y)
                
                # Common properties
                if hasattr(wn_node, 'elevation') and hasattr(node, 'elevation'):
                    wn_node.elevation = node.elevation
                if hasattr(wn_node, 'tag'):
                    wn_node.tag = node.tag
                    
                # Junction specific
                if hasattr(wn_node, 'base_demand') and hasattr(node, 'base_demand'):
                    # WNTR base_demand is read-only, need to set via demand_timeseries_list
                    if hasattr(wn_node, 'demand_timeseries_list') and len(wn_node.demand_timeseries_list) > 0:
                        wn_node.demand_timeseries_list[0].base_value = node.base_demand
                    else:
                        # Fallback if no demand list exists (shouldn't happen for standard junctions)
                        pass
                if hasattr(wn_node, 'demand_pattern_name') and hasattr(node, 'demand_pattern'):
                    wn_node.demand_pattern_name = node.demand_pattern
                if hasattr(wn_node, 'emitter_coefficient') and hasattr(node, 'emitter_coeff'):
                    wn_node.emitter_coefficient = node.emitter_coeff
                    
                # Reservoir specific
                if hasattr(wn_node, 'base_head') and hasattr(node, 'total_head'):
                    wn_node.base_head = node.total_head
                if hasattr(wn_node, 'head_pattern_name') and hasattr(node, 'head_pattern'):
                    wn_node.head_pattern_name = node.head_pattern
                    
                # Tank specific
                if hasattr(wn_node, 'init_level') and hasattr(node, 'init_level'):
                    wn_node.init_level = node.init_level
                if hasattr(wn_node, 'min_level') and hasattr(node, 'min_level'):
                    wn_node.min_level = node.min_level
                if hasattr(wn_node, 'max_level') and hasattr(node, 'max_level'):
                    wn_node.max_level = node.max_level
                if hasattr(wn_node, 'diameter') and hasattr(node, 'diameter'):
                    wn_node.diameter = node.diameter / 1000.0  # Convert mm to m
                if hasattr(wn_node, 'min_volume') and hasattr(node, 'min_volume'):
                    wn_node.min_volume = node.min_volume
                if hasattr(wn_node, 'vol_curve_name') and hasattr(node, 'volume_curve'):
                    wn_node.vol_curve_name = node.volume_curve
                if hasattr(wn_node, 'mixing_model') and hasattr(node, 'mixing_model'):
                    wn_node.mixing_model = node.mixing_model.name if hasattr(node.mixing_model, 'name') else str(node.mixing_model)
                if hasattr(wn_node, 'mixing_fraction') and hasattr(node, 'mixing_fraction'):
                    wn_node.mixing_fraction = node.mixing_fraction
                if hasattr(wn_node, 'bulk_reaction_coefficient') and hasattr(node, 'bulk_coeff'):
                    wn_node.bulk_reaction_coefficient = node.bulk_coeff
                    
        # Links
        for link in self.network.links.values():
            # Add link if not exists
            if link.id not in wn.links:
                if link.link_type == LinkType.PIPE:
                    # WNTR uses meters for diameter, EPANET uses mm for metric units
                    wn.add_pipe(link.id, link.from_node, link.to_node, 
                               length=link.length, diameter=link.diameter / 1000.0, roughness=link.roughness)  # Convert mm to m
                elif link.link_type == LinkType.PUMP:
                    wn.add_pump(link.id, link.from_node, link.to_node)
                elif link.link_type in [LinkType.PRV, LinkType.PSV, LinkType.PBV, LinkType.FCV, LinkType.TCV, LinkType.GPV]:
                    # WNTR add_valve requires type
                    valve_type = "PRV" # Default
                    if link.link_type == LinkType.PRV: valve_type = "PRV"
                    elif link.link_type == LinkType.PSV: valve_type = "PSV"
                    elif link.link_type == LinkType.PBV: valve_type = "PBV"
                    elif link.link_type == LinkType.FCV: valve_type = "FCV"
                    elif link.link_type == LinkType.TCV: valve_type = "TCV"
                    elif link.link_type == LinkType.GPV: valve_type = "GPV"
                    
                    # WNTR uses meters for diameter, EPANET uses mm for metric units
                    wn.add_valve(link.id, link.from_node, link.to_node, diameter=link.diameter / 1000.0, valve_type=valve_type)  # Convert mm to m

            # Update properties
            if link.id in wn.links:
                wn_link = wn.links[link.id]
                
                # Common properties
                if hasattr(wn_link, 'tag'):
                    wn_link.tag = link.tag
                if hasattr(wn_link, 'status'):
                    status_map = {
                        LinkStatus.OPEN: 'OPEN',
                        LinkStatus.CLOSED: 'CLOSED',
                        LinkStatus.CV: 'CV'
                    }
                    new_status = status_map.get(link.status, 'OPEN')
                    
                    # WNTR Pipe status is read-only property that reflects current simulation state
                    # To set initial status, use initial_status
                    if hasattr(wn_link, 'initial_status'):
                        wn_link.initial_status = new_status
                    else:
                        # Try setting status directly if it's not read-only (e.g. for Pumps/Valves it might be settable)
                        try:
                            wn_link.status = new_status
                        except AttributeError:
                            pass
                
                # Pipe specific
                if hasattr(wn_link, 'length') and hasattr(link, 'length'):
                    wn_link.length = link.length
                if hasattr(wn_link, 'diameter') and hasattr(link, 'diameter'):
                    wn_link.diameter = link.diameter / 1000.0  # Convert mm to m
                if hasattr(wn_link, 'roughness') and hasattr(link, 'roughness'):
                    wn_link.roughness = link.roughness
                if hasattr(wn_link, 'minor_loss') and hasattr(link, 'minor_loss'):
                    wn_link.minor_loss = link.minor_loss
                if hasattr(wn_link, 'bulk_reaction_coefficient') and hasattr(link, 'bulk_coeff'):
                    wn_link.bulk_reaction_coefficient = link.bulk_coeff
                if hasattr(wn_link, 'wall_reaction_coefficient') and hasattr(link, 'wall_coeff'):
                    wn_link.wall_reaction_coefficient = link.wall_coeff
                    
                # Pump specific
                if hasattr(wn_link, 'pump_curve_name') and hasattr(link, 'pump_curve'):
                    wn_link.pump_curve_name = link.pump_curve
                if hasattr(wn_link, 'power') and hasattr(link, 'power'):
                    wn_link.power = link.power
                if hasattr(wn_link, 'speed_pattern_name') and hasattr(link, 'speed_pattern'):
                    wn_link.speed_pattern_name = link.speed_pattern
                    
                # Valve specific
                if hasattr(wn_link, 'setting') and hasattr(link, 'valve_setting'):
                    wn_link.setting = link.valve_setting
        
        # Sync Options to WNTR
        if hasattr(wn, 'options'):
            opts = self.network.options
            
            # Hydraulics
            if hasattr(wn.options.hydraulic, 'headloss'):
                if opts.headloss_formula == HeadLossType.HW:
                    wn.options.hydraulic.headloss = 'H-W'
                elif opts.headloss_formula == HeadLossType.DW:
                    wn.options.hydraulic.headloss = 'D-W'
                elif opts.headloss_formula == HeadLossType.CM:
                    wn.options.hydraulic.headloss = 'C-M'
            
            if hasattr(wn.options.hydraulic, 'viscosity'):
                wn.options.hydraulic.viscosity = opts.viscosity
            if hasattr(wn.options.hydraulic, 'specific_gravity'):
                wn.options.hydraulic.specific_gravity = opts.specific_gravity
            if hasattr(wn.options.hydraulic, 'trials'):
                wn.options.hydraulic.trials = opts.trials
            if hasattr(wn.options.hydraulic, 'accuracy'):
                wn.options.hydraulic.accuracy = opts.accuracy
            if hasattr(wn.options.hydraulic, 'demand_multiplier'):
                wn.options.hydraulic.demand_multiplier = opts.demand_multiplier
            if hasattr(wn.options.hydraulic, 'emitter_exponent'):
                wn.options.hydraulic.emitter_exponent = opts.emitter_exponent
            
            # Quality
            if hasattr(wn.options.quality, 'parameter'):
                if opts.quality_type == QualityType.NONE:
                    wn.options.quality.parameter = 'NONE'
                elif opts.quality_type == QualityType.CHEM:
                    wn.options.quality.parameter = 'CHEMICAL'
                elif opts.quality_type == QualityType.AGE:
                    wn.options.quality.parameter = 'AGE'
                elif opts.quality_type == QualityType.TRACE:
                    wn.options.quality.parameter = 'TRACE'
            
            if hasattr(wn.options.quality, 'diffusivity'):
                wn.options.quality.diffusivity = opts.diffusivity
            if hasattr(wn.options.quality, 'tolerance'):
                wn.options.quality.tolerance = opts.quality_tolerance
            
            # Reactions
            if hasattr(wn.options.reaction, 'bulk_order'):
                wn.options.reaction.bulk_order = opts.bulk_order
            if hasattr(wn.options.reaction, 'wall_order'):
                wn.options.reaction.wall_order = opts.wall_order
            if hasattr(wn.options.reaction, 'bulk_coeff'):
                wn.options.reaction.bulk_coeff = opts.global_bulk_coeff
            if hasattr(wn.options.reaction, 'wall_coeff'):
                wn.options.reaction.wall_coeff = opts.global_wall_coeff
            if hasattr(wn.options.reaction, 'limiting_potential'):
                wn.options.reaction.limiting_potential = opts.limiting_concentration
            if hasattr(wn.options.reaction, 'roughness_correlation'):
                wn.options.reaction.roughness_correlation = opts.roughness_correlation
            
            # Times
            if hasattr(wn.options.time, 'duration'):
                wn.options.time.duration = opts.duration
            if hasattr(wn.options.time, 'hydraulic_timestep'):
                wn.options.time.hydraulic_timestep = opts.hydraulic_timestep
            if hasattr(wn.options.time, 'quality_timestep'):
                wn.options.time.quality_timestep = opts.quality_timestep
            if hasattr(wn.options.time, 'pattern_timestep'):
                wn.options.time.pattern_timestep = opts.pattern_timestep
            if hasattr(wn.options.time, 'pattern_start'):
                wn.options.time.pattern_start = opts.pattern_start
            if hasattr(wn.options.time, 'report_timestep'):
                wn.options.time.report_timestep = opts.report_timestep
            if hasattr(wn.options.time, 'report_start'):
                wn.options.time.report_start = opts.report_start
            
            # Energy
            if hasattr(wn.options.energy, 'global_efficiency'):
                wn.options.energy.global_efficiency = opts.global_efficiency
            if hasattr(wn.options.energy, 'global_price'):
                wn.options.energy.global_price = opts.global_price
            if hasattr(wn.options.energy, 'demand_charge'):
                wn.options.energy.demand_charge = opts.demand_charge
    
    def close_project(self):
        """Close current project."""
        self.engine.close_project()
        self.network.clear()
        self.filename = ""
        self.modified = False
        self._has_results = False
    
    def run_simulation(self, progress_callback: Optional[Callable[[int], None]] = None):
        """Run simulation."""
        try:
            if progress_callback:
                progress_callback(10)
            
            self.engine.run_simulation()
            
            if progress_callback:
                progress_callback(90)
            
            self._load_results_from_engine()
            self._has_results = True
            
            if progress_callback:
                progress_callback(100)
                
            self._generate_report(True)
                
        except Exception as e:
            self._generate_report(False, str(e))
            raise Exception(f"Simulation failed: {e}")
            
    def _generate_report(self, success: bool, error_msg: str = ""):
        """Generate a status report."""
        import datetime
        
        lines = []
        lines.append("EPANET 2.2 - PySide6 Simulation Report")
        lines.append("======================================")
        lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Project: {self.filename or 'Untitled'}")
        lines.append("")
        
        if success:
            lines.append("Simulation Status: SUCCESSFUL")
            lines.append("")
            lines.append("Network Statistics:")
            lines.append(f"  Nodes: {len(self.network.nodes)}")
            lines.append(f"  Links: {len(self.network.links)}")
            
            if self.engine.results:
                res = self.engine.results
                lines.append("")
                lines.append("Simulation Details:")
                # lines.append(f"  Duration: {res.time[-1] / 3600.0:.2f} hours") # WNTR results might not have simple time attribute like this directly accessible in all versions, checking structure
                # WNTR results: node (dict of DF), link (dict of DF), network_name, time (index)
                if hasattr(res, 'node') and 'pressure' in res.node:
                     times = res.node['pressure'].index
                     duration = (times[-1] - times[0]) / 3600.0
                     lines.append(f"  Duration: {duration:.2f} hours")
                     lines.append(f"  Time Steps: {len(times)}")
        else:
            lines.append("Simulation Status: FAILED")
            lines.append(f"Error: {error_msg}")
            
        self.last_report = "\n".join(lines)
                

    
    def has_results(self) -> bool:
        return self._has_results
        
    def get_version(self) -> str:
        return self.engine.get_version()
    
    def _load_network_from_wntr(self):
        """Convert WNTR network to our internal data model."""
        self.network.clear()
        wn = self.engine.wn
        if not wn:
            return
            
        # Project Info
        if hasattr(wn, 'title'):
            self.network.title = wn.title
            
        # Nodes
        for name, node in wn.nodes():
            x, y = node.coordinates
            elevation = getattr(node, 'elevation', 0.0)
            
            if isinstance(node, wntr.network.Junction):
                new_node = Junction(
                    id=name,
                    x=x, y=y,
                    elevation=elevation,
                    base_demand=node.base_demand
                )
            elif isinstance(node, wntr.network.Reservoir):
                new_node = Reservoir(
                    id=name,
                    x=x, y=y,
                    elevation=getattr(node, 'head_pattern_name', 0.0) # Reservoir uses head_pattern_name for total head usually? 
                    # WNTR Reservoir has 'base_head' and 'head_pattern_name'
                )
                # Fix for reservoir head
                if hasattr(node, 'base_head'):
                    new_node.total_head = node.base_head
            elif isinstance(node, wntr.network.Tank):
                # WNTR uses meters for diameter, EPANET uses mm for metric units
                new_node = Tank(
                    id=name,
                    x=x, y=y,
                    elevation=elevation,
                    init_level=node.init_level,
                    min_level=node.min_level,
                    max_level=node.max_level,
                    diameter=node.diameter * 1000.0,  # Convert m to mm
                    min_volume=node.min_vol,
                    volume_curve=getattr(node, 'vol_curve_name', None)
                )
            else:
                continue
                
            self.network.add_node(new_node)
            
        # Update map bounds from WNTR options if available
        if hasattr(wn, 'options') and hasattr(wn.options, 'graphics') and hasattr(wn.options.graphics, 'map_extent'):
            extent = wn.options.graphics.map_extent
            if extent:
                # extent is usually (min_x, min_y, max_x, max_y) or similar
                # WNTR might store it as a list or tuple
                try:
                    if len(extent) == 4:
                        self.network.map_bounds['min_x'] = float(extent[0])
                        self.network.map_bounds['min_y'] = float(extent[1])
                        self.network.map_bounds['max_x'] = float(extent[2])
                        self.network.map_bounds['max_y'] = float(extent[3])
                except:
                    pass
            
        # Links
        for name, link in wn.links():
            from_node = link.start_node_name
            to_node = link.end_node_name
            
            if isinstance(link, wntr.network.Pipe):
                # WNTR uses meters for diameter, EPANET uses mm for metric units
                new_link = Pipe(
                    id=name,
                    from_node=from_node,
                    to_node=to_node,
                    length=link.length,
                    diameter=link.diameter * 1000.0,  # Convert m to mm
                    roughness=link.roughness
                )
            elif isinstance(link, wntr.network.Pump):
                new_link = Pump(
                    id=name,
                    from_node=from_node,
                    to_node=to_node
                )
            elif isinstance(link, wntr.network.Valve):
                # WNTR uses meters for diameter, EPANET uses mm for metric units
                new_link = Valve(
                    id=name,
                    valve_type=LinkType.PRV, # Default, need to check type
                    from_node=from_node,
                    to_node=to_node,
                    diameter=link.diameter * 1000.0  # Convert m to mm
                )
            else:
                continue
                
            self.network.add_link(new_link)
        
        # Load Options from WNTR
        if hasattr(wn, 'options'):
            opts = wn.options
            
            # Hydraulics
            if hasattr(opts.hydraulic, 'headloss'):
                headloss_str = str(opts.hydraulic.headloss).upper()
                if 'H-W' in headloss_str or 'HW' in headloss_str:
                    self.network.options.headloss_formula = HeadLossType.HW
                elif 'D-W' in headloss_str or 'DW' in headloss_str:
                    self.network.options.headloss_formula = HeadLossType.DW
                elif 'C-M' in headloss_str or 'CM' in headloss_str:
                    self.network.options.headloss_formula = HeadLossType.CM
            
            if hasattr(opts.hydraulic, 'viscosity'):
                self.network.options.viscosity = opts.hydraulic.viscosity
            if hasattr(opts.hydraulic, 'specific_gravity'):
                self.network.options.specific_gravity = opts.hydraulic.specific_gravity
            if hasattr(opts.hydraulic, 'trials'):
                self.network.options.trials = opts.hydraulic.trials
            if hasattr(opts.hydraulic, 'accuracy'):
                self.network.options.accuracy = opts.hydraulic.accuracy
            if hasattr(opts.hydraulic, 'unbalanced'):
                self.network.options.unbalanced = str(opts.hydraulic.unbalanced).upper()
            if hasattr(opts.hydraulic, 'demand_multiplier'):
                self.network.options.demand_multiplier = opts.hydraulic.demand_multiplier
            if hasattr(opts.hydraulic, 'emitter_exponent'):
                self.network.options.emitter_exponent = opts.hydraulic.emitter_exponent
            
            # Quality
            if hasattr(opts.quality, 'parameter'):
                qual_str = str(opts.quality.parameter).upper()
                if 'NONE' in qual_str:
                    self.network.options.quality_type = QualityType.NONE
                elif 'CHEMICAL' in qual_str or 'CHEM' in qual_str:
                    self.network.options.quality_type = QualityType.CHEM
                elif 'AGE' in qual_str:
                    self.network.options.quality_type = QualityType.AGE
                elif 'TRACE' in qual_str:
                    self.network.options.quality_type = QualityType.TRACE
            
            if hasattr(opts.quality, 'diffusivity'):
                self.network.options.diffusivity = opts.quality.diffusivity
            if hasattr(opts.quality, 'tolerance'):
                self.network.options.quality_tolerance = opts.quality.tolerance
            
            # Reactions
            if hasattr(opts.reaction, 'bulk_order'):
                self.network.options.bulk_order = opts.reaction.bulk_order
            if hasattr(opts.reaction, 'wall_order'):
                self.network.options.wall_order = opts.reaction.wall_order
            if hasattr(opts.reaction, 'bulk_coeff'):
                self.network.options.global_bulk_coeff = opts.reaction.bulk_coeff
            if hasattr(opts.reaction, 'wall_coeff'):
                self.network.options.global_wall_coeff = opts.reaction.wall_coeff
            if hasattr(opts.reaction, 'limiting_potential'):
                self.network.options.limiting_concentration = opts.reaction.limiting_potential
            if hasattr(opts.reaction, 'roughness_correlation'):
                self.network.options.roughness_correlation = opts.reaction.roughness_correlation
            
            # Times
            if hasattr(opts.time, 'duration'):
                self.network.options.duration = int(opts.time.duration)
            if hasattr(opts.time, 'hydraulic_timestep'):
                self.network.options.hydraulic_timestep = int(opts.time.hydraulic_timestep)
            if hasattr(opts.time, 'quality_timestep'):
                self.network.options.quality_timestep = int(opts.time.quality_timestep)
            if hasattr(opts.time, 'pattern_timestep'):
                self.network.options.pattern_timestep = int(opts.time.pattern_timestep)
            if hasattr(opts.time, 'pattern_start'):
                self.network.options.pattern_start = int(opts.time.pattern_start)
            if hasattr(opts.time, 'report_timestep'):
                self.network.options.report_timestep = int(opts.time.report_timestep)
            if hasattr(opts.time, 'report_start'):
                self.network.options.report_start = int(opts.time.report_start)
            if hasattr(opts.time, 'statistic'):
                self.network.options.statistic = str(opts.time.statistic).upper()
            
            # Energy
            if hasattr(opts.energy, 'global_efficiency'):
                self.network.options.global_efficiency = opts.energy.global_efficiency
            if hasattr(opts.energy, 'global_price'):
                self.network.options.global_price = opts.energy.global_price
            if hasattr(opts.energy, 'demand_charge'):
                self.network.options.demand_charge = opts.energy.demand_charge
            
    def _load_results_from_engine(self):
        """Load results into network objects."""
        # Nodes
        for node_id, node in self.network.nodes.items():
            node.demand = self.engine.get_node_result(node_id, NodeParam.DEMAND)
            node.head = self.engine.get_node_result(node_id, NodeParam.HEAD)
            node.pressure = self.engine.get_node_result(node_id, NodeParam.PRESSURE)
            node.quality = self.engine.get_node_result(node_id, NodeParam.QUALITY)
            
        # Links
        for link_id, link in self.network.links.items():
            link.flow = self.engine.get_link_result(link_id, LinkParam.FLOW)
            link.velocity = self.engine.get_link_result(link_id, LinkParam.VELOCITY)
            link.headloss = self.engine.get_link_result(link_id, LinkParam.HEADLOSS)

    def get_time_series(self, obj_type: str, obj_id: str, param: Any) -> Tuple[list, list]:
        """Get time series data."""
        return self.engine.get_time_series(obj_type, obj_id, param)

    def get_simulation_times(self) -> list:
        """Get simulation time steps in hours."""
        return self.engine.get_simulation_times()

    def get_network_values_at_time(self, param: NodeParam, time_index: int) -> Dict[str, float]:
        """Get values for all nodes at a specific time index."""
        return self.engine.get_network_values_at_time(param, time_index)

    def get_pump_energy(self, pump_id: str) -> float:
        """Get pump energy usage."""
        return self.engine.get_pump_energy(pump_id)
