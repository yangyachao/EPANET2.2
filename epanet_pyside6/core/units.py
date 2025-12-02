"""Unit conversion utilities for EPANET."""

from enum import Enum
from core.constants import FlowUnits

class UnitSystem(Enum):
    US = 0  # US Customary
    SI = 1  # Metric

class UnitConverter:
    """Handles conversion between WNTR internal units (SI) and Project units."""
    
    def __init__(self, flow_units: FlowUnits):
        self.flow_units = flow_units
        self.system = self._get_unit_system(flow_units)
        
    def _get_unit_system(self, flow_units: FlowUnits) -> UnitSystem:
        """Determine unit system from flow units."""
        if flow_units in [
            FlowUnits.CFS, FlowUnits.GPM, FlowUnits.MGD, 
            FlowUnits.IMGD, FlowUnits.AFD
        ]:
            return UnitSystem.US
        return UnitSystem.SI

    # Length / Elevation / Head
    # WNTR: meters
    # US: feet
    # SI: meters
    def length_to_project(self, value_si: float) -> float:
        """Convert length from SI (m) to Project units (ft or m)."""
        if self.system == UnitSystem.US:
            return value_si * 3.28084
        return value_si

    def length_to_si(self, value_project: float) -> float:
        """Convert length from Project units (ft or m) to SI (m)."""
        if self.system == UnitSystem.US:
            return value_project / 3.28084
        return value_project

    # Diameter
    # WNTR: meters
    # US: inches
    # SI: millimeters
    def diameter_to_project(self, value_si: float) -> float:
        """Convert diameter from SI (m) to Project units (in or mm)."""
        if self.system == UnitSystem.US:
            return value_si * 39.3701
        return value_si * 1000.0

    def diameter_to_si(self, value_project: float) -> float:
        """Convert diameter from Project units (in or mm) to SI (m)."""
        if self.system == UnitSystem.US:
            return value_project / 39.3701
        return value_project / 1000.0

    # Pressure
    # WNTR: meters (pressure head)
    # US: psi
    # SI: meters
    def pressure_to_project(self, value_si: float) -> float:
        """Convert pressure from SI (m) to Project units (psi or m)."""
        if self.system == UnitSystem.US:
            # 1 m = 1.42197 psi (assuming specific gravity = 1.0)
            # Note: EPANET calculates pressure = (Head - Elev) * 0.433 * SG (for US)
            # WNTR returns pressure in meters of head?
            # Actually WNTR results.node['pressure'] is in meters of water for SI, and... ?
            # Wait, WNTR documentation says:
            # "Pressure is the fluid pressure at the node (m)."
            # If WNTR normalizes everything to SI (meters), then:
            # 1 m head = 1.4219702 psi (for water SG=1)
            # Let's assume SG=1 for now as per standard WNTR behavior unless we access options.
            # Ideally we should use specific gravity from options.
            return value_si * 1.4219702
        return value_si

    def pressure_to_si(self, value_project: float) -> float:
        """Convert pressure from Project units (psi or m) to SI (m)."""
        if self.system == UnitSystem.US:
            return value_project / 1.4219702
        return value_project

    # Velocity
    # WNTR: m/s
    # US: ft/s (fps)
    # SI: m/s
    def velocity_to_project(self, value_si: float) -> float:
        """Convert velocity from SI (m/s) to Project units (fps or m/s)."""
        if self.system == UnitSystem.US:
            return value_si * 3.28084
        return value_si

    def velocity_to_si(self, value_project: float) -> float:
        """Convert velocity from Project units (fps or m/s) to SI (m/s)."""
        if self.system == UnitSystem.US:
            return value_project / 3.28084
        return value_project
        
    # Flow
    # WNTR: m³/s (CMS)
    # Project: Depends on FlowUnits
    def flow_to_project(self, value_si: float) -> float:
        """Convert flow from SI (CMS) to Project units."""
        # Conversion factors from CMS (m3/s) to Target
        factors = {
            FlowUnits.CFS: 35.3147,
            FlowUnits.GPM: 15850.3,
            FlowUnits.MGD: 22.8245,
            FlowUnits.IMGD: 19.0053,
            FlowUnits.AFD: 70.0456,
            FlowUnits.LPS: 1000.0,
            FlowUnits.LPM: 60000.0,
            FlowUnits.MLD: 86.4,
            FlowUnits.CMH: 3600.0,
            FlowUnits.CMD: 86400.0
        }
        return value_si * factors.get(self.flow_units, 1.0)

    def flow_to_si(self, value_project: float) -> float:
        """Convert flow from Project units to SI (CMS)."""
        factors = {
            FlowUnits.CFS: 35.3147,
            FlowUnits.GPM: 15850.3,
            FlowUnits.MGD: 22.8245,
            FlowUnits.IMGD: 19.0053,
            FlowUnits.AFD: 70.0456,
            FlowUnits.LPS: 1000.0,
            FlowUnits.LPM: 60000.0,
            FlowUnits.MLD: 86.4,
            FlowUnits.CMH: 3600.0,
            FlowUnits.CMD: 86400.0
        }
        return value_project / factors.get(self.flow_units, 1.0)

def get_unit_label(param_type: str, flow_units: FlowUnits) -> str:
    """Get unit label for a parameter type."""
    # Determine system
    is_si = flow_units not in [
        FlowUnits.CFS, FlowUnits.GPM, FlowUnits.MGD, 
        FlowUnits.IMGD, FlowUnits.AFD
    ]
    
    if param_type in ["elevation", "head", "length", "level"]:
        return "m" if is_si else "ft"
        
    elif param_type == "diameter":
        return "mm" if is_si else "in"
        
    elif param_type == "pressure":
        return "m" if is_si else "psi"
        
    elif param_type == "velocity":
        return "m/s" if is_si else "fps"
        
    elif param_type in ["flow", "demand"]:
        return flow_units.name if flow_units else ""
        
    elif param_type == "volume":
        return "m3" if is_si else "ft3"
        
    elif param_type == "headloss":
        # Unit headloss: m/km or ft/kft
        return "m/km" if is_si else "ft/kft"
        
    elif param_type == "quality":
        # This is tricky as it depends on QualityType options
        # For now return generic or empty, or assume mg/L
        return "" 
        
    return ""
