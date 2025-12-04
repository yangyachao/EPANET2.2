"""Node data models."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from core.constants import NodeType, SourceType, MixingModel


@dataclass
class Node:
    """Base class for network nodes."""
    id: str
    node_type: NodeType = field(init=False)
    x: float = 0.0
    y: float = 0.0
    elevation: float = 0.0
    comment: str = ""
    tag: str = ""
    
    # Computed results
    demand: float = 0.0
    head: float = 0.0
    pressure: float = 0.0
    quality: float = 0.0
    
    def __post_init__(self):
        """Validate node data after initialization."""
        if not self.id:
            raise ValueError("Node ID cannot be empty")


@dataclass
class Junction(Node):
    """Junction node model."""
    base_demand: float = 0.0
    demand_pattern: Optional[str] = None
    emitter_coeff: float = 0.0
    init_quality: float = 0.0
    
    # Multiple demand categories
    demands: List[Dict] = field(default_factory=list)
    
    # Source quality
    source_quality: float = 0.0
    source_pattern: Optional[str] = None
    source_type: SourceType = SourceType.CONCEN
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = NodeType.JUNCTION
    
    def add_demand(self, base_demand: float, pattern: str = "", name: str = ""):
        """Add a demand category."""
        self.demands.append({
            'base_demand': base_demand,
            'pattern': pattern,
            'name': name
        })
    
    def get_total_demand(self) -> float:
        """Get total base demand from all categories."""
        total = self.base_demand
        for demand in self.demands:
            total += demand['base_demand']
        return total


@dataclass
class Reservoir(Node):
    """Reservoir node model."""
    total_head: float = 0.0
    head_pattern: Optional[str] = None
    init_quality: float = 0.0
    
    # Source quality
    source_quality: float = 0.0
    source_pattern: Optional[str] = None
    source_type: SourceType = SourceType.CONCEN
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = NodeType.RESERVOIR


@dataclass
class Tank(Node):
    """Tank node model."""
    init_level: float = 0.0
    min_level: float = 0.0
    max_level: float = 0.0
    diameter: float = 0.0
    min_volume: float = 0.0
    volume_curve: Optional[str] = None
    
    # Mixing model
    mixing_model: MixingModel = MixingModel.MIX1
    mixing_fraction: float = 1.0
    
    # Reaction
    bulk_coeff: float = 0.0
    init_quality: float = 0.0
    
    # Source quality
    source_quality: float = 0.0
    source_pattern: Optional[str] = None
    source_type: SourceType = SourceType.CONCEN
    
    # Overflow
    can_overflow: bool = False
    
    # Computed properties
    volume: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = NodeType.TANK
    
    def get_volume_at_level(self, level: float) -> float:
        """Calculate tank volume at given level.
        
        For cylindrical tanks: V = π * (D/2)² * H
        For tanks with volume curve: use curve lookup
        """
        if self.volume_curve:
            # Curve lookup requires external curve data not available here
            return 0.0
        else:
            # Cylindrical tank
            import math
            radius = self.diameter / 2.0
            height = level - self.elevation
            return math.pi * radius * radius * height
    
    def get_level_at_volume(self, volume: float) -> float:
        """Calculate tank level at given volume."""
        if self.volume_curve:
            # Curve lookup requires external curve data not available here
            return 0.0
        else:
            # Cylindrical tank
            import math
            radius = self.diameter / 2.0
            if radius > 0:
                height = volume / (math.pi * radius * radius)
                return self.elevation + height
            return self.elevation
