"""Analysis options model."""

from dataclasses import dataclass
from typing import Optional
from core.constants import FlowUnits, HeadLossType, QualityType


@dataclass
class Options:
    """Network analysis options."""
    
    # Hydraulics
    flow_units: FlowUnits = FlowUnits.LPS  # Default to metric (SI) units
    headloss_formula: HeadLossType = HeadLossType.HW
    specific_gravity: float = 1.0
    viscosity: float = 1.0
    trials: int = 40
    accuracy: float = 0.001
    unbalanced: str = "STOP"
    unbalanced_continue: int = 10
    checkfreq: int = 2
    maxcheck: int = 10
    damplimit: float = 0.0
    default_pattern: Optional[str] = None
    demand_multiplier: float = 1.0
    emitter_exponent: float = 0.5
    
    # Water Quality
    quality_type: QualityType = QualityType.NONE
    chemical_name: str = ""
    chemical_units: str = "mg/L"
    diffusivity: float = 1.0
    trace_node: Optional[str] = None
    quality_tolerance: float = 0.01
    
    # Reactions
    bulk_order: float = 1.0
    wall_order: float = 1.0
    tank_order: float = 1.0
    global_bulk_coeff: float = 0.0
    global_wall_coeff: float = 0.0
    limiting_concentration: float = 0.0
    roughness_correlation: float = 0.0
    
    # Times
    duration: int = 0  # seconds
    hydraulic_timestep: int = 3600  # seconds
    quality_timestep: int = 300  # seconds
    pattern_timestep: int = 3600  # seconds
    pattern_start: int = 0  # seconds
    report_timestep: int = 3600  # seconds
    report_start: int = 0  # seconds
    start_clocktime: int = 0  # seconds
    statistic: str = "NONE"
    
    # Energy
    global_efficiency: float = 75.0
    global_price: float = 0.0
    demand_charge: float = 0.0
    
    # Pressure Dependent Demand (PDA)
    demand_model: str = "DDA"  # or "PDA"
    minimum_pressure: float = 0.0
    required_pressure: float = 0.1
    pressure_exponent: float = 0.5
    
    # Report
    status_report: str = "NO"
    summary_report: bool = True
    energy_report: bool = False
    nodes_report: str = "NONE"
    links_report: str = "NONE"
    
    def __post_init__(self):
        """Validate options after initialization."""
        if self.trials < 1:
            raise ValueError("Trials must be at least 1")
        if self.accuracy <= 0:
            raise ValueError("Accuracy must be positive")
        if self.duration < 0:
            raise ValueError("Duration cannot be negative")
