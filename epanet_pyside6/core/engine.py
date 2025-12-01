"""EPANET Engine wrapper using WNTR."""

import wntr
import pandas as pd
import os
import tempfile
from typing import Optional, Dict, Any, Tuple
from .constants import NodeType, LinkType, NodeParam, LinkParam
from .exceptions import InputFileError

class Engine:
    """Wrapper for WNTR engine."""
    
    def __init__(self):
        """Initialize engine."""
        self.wn: Optional[wntr.network.WaterNetworkModel] = None
        self.results: Optional[wntr.sim.SimulationResults] = None
        self.report_text: str = ""
    
    def open_project(self, filename: str):
        """Open an EPANET project file."""
        try:
            self.wn = wntr.network.WaterNetworkModel(filename)
            self.results = None
            self.report_text = ""
        except Exception as e:
            # The error 'e' from wntr might contain detailed information.
            # We are wrapping it in a custom exception to be caught by the UI.
            # The str(e) often contains the formatted error messages from EPANET.
            # We can parse this string if needed to get more structured error data.
            errors = str(e).split('\n')
            raise InputFileError(f"Failed to open project: {e}", errors=errors)
            
    def save_project(self, filename: str):
        """Save project to file."""
        if self.wn:
            wntr.network.write_inpfile(self.wn, filename)
            
    def close_project(self):
        """Close current project."""
        self.wn = None
        self.results = None
        self.report_text = ""
        
    def run_simulation(self):
        """Run hydraulic and water quality simulation."""
        if not self.wn:
            raise RuntimeError("No project opened")
        
        # Save current working directory
        original_cwd = os.getcwd()
        
        # Create a temporary directory for simulation files
        temp_dir = tempfile.mkdtemp(prefix='epanet_sim_')
        
        try:
            # Change to temp directory so WNTR writes temp files there
            os.chdir(temp_dir)
            
            # Use EpanetSimulator
            sim = wntr.sim.EpanetSimulator(self.wn)
            # WNTR's EpanetSimulator writes a file named 'temp.inp' and produces 'temp.rpt' usually
            # We can specify a prefix or check the directory
            self.results = sim.run_sim()
            
            # Try to find the report file
            # WNTR usually names it based on the input file name provided to run_sim, 
            # or defaults to 'temp.rpt' if passing object.
            # Let's check for any .rpt file
            rpt_file = None
            for f in os.listdir(temp_dir):
                if f.endswith('.rpt'):
                    rpt_file = f
                    break
            
            if rpt_file:
                with open(rpt_file, 'r') as f:
                    self.report_text = f.read()
            else:
                self.report_text = "Report file not found."
            
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            
            # Clean up temp directory
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
    def get_version(self) -> str:
        """Get WNTR/EPANET version."""
        return f"WNTR {wntr.__version__}"
        
    # Data Access Methods
    
    def get_nodes(self) -> Dict[str, Any]:
        """Get all nodes from the network."""
        if not self.wn:
            return {}
        return dict(self.wn.nodes())
        
    def get_links(self) -> Dict[str, Any]:
        """Get all links from the network."""
        if not self.wn:
            return {}
        return dict(self.wn.links())
        
    def get_node_result(self, node_id: str, param: NodeParam) -> float:
        """Get simulation result for a node."""
        if not self.results:
            return 0.0
            
        try:
            if param == NodeParam.DEMAND:
                return self.results.node['demand'].loc[:, node_id].iloc[-1]
            elif param == NodeParam.HEAD:
                return self.results.node['head'].loc[:, node_id].iloc[-1]
            elif param == NodeParam.PRESSURE:
                return self.results.node['pressure'].loc[:, node_id].iloc[-1]
            elif param == NodeParam.QUALITY:
                return self.results.node['quality'].loc[:, node_id].iloc[-1]
        except KeyError:
            pass
        return 0.0
        
    def get_link_result(self, link_id: str, param: LinkParam) -> float:
        """Get simulation result for a link."""
        if not self.results:
            return 0.0
            
        try:
            if param == LinkParam.FLOW:
                return self.results.link['flowrate'].loc[:, link_id].iloc[-1]
            elif param == LinkParam.VELOCITY:
                return self.results.link['velocity'].loc[:, link_id].iloc[-1]
            elif param == LinkParam.HEADLOSS:
                return self.results.link['headloss'].loc[:, link_id].iloc[-1]
        except KeyError:
            pass
        return 0.0

    def get_time_series(self, obj_type: str, obj_id: str, param: Any) -> Tuple[list, list]:
        """Get time series data for an object."""
        if not self.results:
            return [], []
            
        try:
            if obj_type == 'Node':
                df = self.results.node
                if param == NodeParam.DEMAND:
                    series = df['demand'].loc[:, obj_id]
                elif param == NodeParam.HEAD:
                    series = df['head'].loc[:, obj_id]
                elif param == NodeParam.PRESSURE:
                    series = df['pressure'].loc[:, obj_id]
                elif param == NodeParam.QUALITY:
                    series = df['quality'].loc[:, obj_id]
                else:
                    return [], []
            elif obj_type == 'Link':
                df = self.results.link
                if param == LinkParam.FLOW:
                    series = df['flowrate'].loc[:, obj_id]
                elif param == LinkParam.VELOCITY:
                    series = df['velocity'].loc[:, obj_id]
                elif param == LinkParam.HEADLOSS:
                    series = df['headloss'].loc[:, obj_id]
                else:
                    return [], []
            else:
                return [], []
                
            # Convert time index (seconds) to hours
            times = series.index / 3600.0
            values = series.values
            return times.tolist(), values.tolist()
            
        except KeyError:
            return [], []
            
    def get_simulation_times(self) -> list:
        """Get simulation time steps in hours."""
        if not self.results:
            return []
        try:
            # Assume all node results have same time index
            return (self.results.node['pressure'].index / 3600.0).tolist()
        except:
            return []

    def get_network_values_at_time(self, param: NodeParam, time_index: int) -> Dict[str, float]:
        """Get values for all nodes at a specific time index."""
        if not self.results:
            return {}
            
        try:
            df = None
            if param == NodeParam.DEMAND:
                df = self.results.node['demand']
            elif param == NodeParam.HEAD:
                df = self.results.node['head']
            elif param == NodeParam.PRESSURE:
                df = self.results.node['pressure']
            elif param == NodeParam.QUALITY:
                df = self.results.node['quality']
            
            if df is not None:
                # Get row at time_index
                if 0 <= time_index < len(df.index):
                    return df.iloc[time_index].to_dict()
                    
        except KeyError:
            pass
        return {}

    def get_pump_energy(self, pump_id: str) -> float:
        """Get pump energy usage (kWh)."""
        if not self.results:
            return 0.0
            
        try:
            # WNTR results structure for energy might vary
            # Usually it's in link['energy'] if available, or calculated
            # For EPANET 2.2, energy is often reported in a separate table or needs calculation
            # Let's check if 'energy' is a valid column in link results
            # If not, we might need to compute it from power/flow/head
            
            # In WNTR, energy is sometimes available as 'energy' in link results
            if 'energy' in self.results.link:
                return self.results.link['energy'].loc[:, pump_id].iloc[-1]
            
            # Fallback: if not directly available, return 0 for now
            # Real calculation would require integrating power over time
            return 0.0
        except KeyError:
            return 0.0
