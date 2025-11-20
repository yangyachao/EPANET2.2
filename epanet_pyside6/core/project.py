"""EPANET Project management."""

from typing import Optional, Callable, Any, Tuple
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
            
        # Nodes
        for node in self.network.nodes.values():
            # Add node if not exists
            if node.id not in wn.nodes:
                if node.node_type == NodeType.JUNCTION:
                    wn.add_junction(node.id, elevation=node.elevation, coordinates=(node.x, node.y))
                elif node.node_type == NodeType.RESERVOIR:
                    wn.add_reservoir(node.id, base_head=node.total_head, coordinates=(node.x, node.y))
                elif node.node_type == NodeType.TANK:
                    wn.add_tank(node.id, elevation=node.elevation, init_level=node.init_level, 
                               min_level=node.min_level, max_level=node.max_level, 
                               diameter=node.diameter, coordinates=(node.x, node.y))
            
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
                    wn_node.diameter = node.diameter
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
                    wn.add_pipe(link.id, link.from_node, link.to_node, 
                               length=link.length, diameter=link.diameter, roughness=link.roughness)
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
                    
                    wn.add_valve(link.id, link.from_node, link.to_node, diameter=link.diameter, valve_type=valve_type)

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
                    wn_link.diameter = link.diameter
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
                new_node = Tank(
                    id=name,
                    x=x, y=y,
                    elevation=elevation,
                    init_level=node.init_level,
                    min_level=node.min_level,
                    max_level=node.max_level,
                    diameter=node.diameter
                )
            else:
                continue
                
            self.network.add_node(new_node)
            
        # Links
        for name, link in wn.links():
            from_node = link.start_node_name
            to_node = link.end_node_name
            
            if isinstance(link, wntr.network.Pipe):
                new_link = Pipe(
                    id=name,
                    from_node=from_node,
                    to_node=to_node,
                    length=link.length,
                    diameter=link.diameter,
                    roughness=link.roughness
                )
            elif isinstance(link, wntr.network.Pump):
                new_link = Pump(
                    id=name,
                    from_node=from_node,
                    to_node=to_node
                )
            elif isinstance(link, wntr.network.Valve):
                new_link = Valve(
                    id=name,
                    valve_type=LinkType.PRV, # Default, need to check type
                    from_node=from_node,
                    to_node=to_node,
                    diameter=link.diameter
                )
            else:
                continue
                
            self.network.add_link(new_link)
            
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

    def get_pump_energy(self, pump_id: str) -> float:
        """Get pump energy usage."""
        return self.engine.get_pump_energy(pump_id)
