"""Link data models."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from core.constants import LinkType, LinkStatus


@dataclass
class Link:
    """Base class for network links."""
    id: str
    from_node: str
    to_node: str
    link_type: LinkType = field(init=False)
    vertices: List[Tuple[float, float]] = field(default_factory=list)
    comment: str = ""
    tag: str = ""
    
    # Computed results
    flow: float = 0.0
    velocity: float = 0.0
    headloss: float = 0.0
    quality: float = 0.0
    status: LinkStatus = LinkStatus.OPEN
    setting: float = 0.0
    
    def __post_init__(self):
        """Validate link data after initialization."""
        if not self.id:
            raise ValueError("Link ID cannot be empty")
        if not self.from_node or not self.to_node:
            raise ValueError("Link must have from_node and to_node")
    
    def add_vertex(self, x: float, y: float):
        """Add a vertex point to the link."""
        self.vertices.append((x, y))
    
    def reverse(self):
        """Reverse link direction."""
        self.from_node, self.to_node = self.to_node, self.from_node
        self.vertices.reverse()


@dataclass
class Pipe(Link):
    """Pipe link model."""
    length: float = 0.0
    diameter: float = 0.0
    roughness: float = 100.0  # Default for Hazen-Williams
    minor_loss: float = 0.0
    initial_status: LinkStatus = LinkStatus.OPEN
    
    # Reaction coefficients
    bulk_coeff: float = 0.0
    wall_coeff: float = 0.0
    
    # Check valve
    has_check_valve: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        if self.has_check_valve:
            self.link_type = LinkType.CVPIPE
        else:
            self.link_type = LinkType.PIPE


@dataclass
class Pump(Link):
    """Pump link model."""
    pump_curve: Optional[str] = None
    power: float = 0.0  # Constant horsepower
    speed: float = 1.0  # Speed setting
    speed_pattern: Optional[str] = None
    initial_status: LinkStatus = LinkStatus.OPEN
    
    # Energy parameters
    efficiency_curve: Optional[str] = None
    energy_price: float = 0.0
    price_pattern: Optional[str] = None
    
    # Computed energy
    energy_usage: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        self.link_type = LinkType.PUMP


@dataclass
class Valve(Link):
    """Valve link model."""
    diameter: float = 0.0
    valve_type: LinkType = LinkType.PRV
    valve_setting: float = 0.0
    minor_loss: float = 0.0
    initial_status: LinkStatus = LinkStatus.OPEN
    
    def __post_init__(self):
        super().__post_init__()
        # Validate valve type
        valid_types = [LinkType.PRV, LinkType.PSV, LinkType.PBV,
                      LinkType.FCV, LinkType.TCV, LinkType.GPV]
        if self.valve_type not in valid_types:
            raise ValueError(f"Invalid valve type: {self.valve_type}")
        self.link_type = self.valve_type
    
    def get_valve_type_name(self) -> str:
        """Get human-readable valve type name."""
        names = {
            LinkType.PRV: "Pressure Reducing Valve",
            LinkType.PSV: "Pressure Sustaining Valve",
            LinkType.PBV: "Pressure Breaker Valve",
            LinkType.FCV: "Flow Control Valve",
            LinkType.TCV: "Throttle Control Valve",
            LinkType.GPV: "General Purpose Valve"
        }
        return names.get(self.valve_type, "Unknown")
