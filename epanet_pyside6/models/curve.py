"""Curve model."""

from dataclasses import dataclass, field
from typing import List, Tuple
from enum import IntEnum


class CurveType(IntEnum):
    """Curve types."""
    VOLUME = 0
    PUMP = 1
    EFFICIENCY = 2
    HEADLOSS = 3
    GENERIC = 4


@dataclass
class Curve:
    """Data curve for pumps, tanks, etc."""
    id: str
    curve_type: CurveType = CurveType.GENERIC
    points: List[Tuple[float, float]] = field(default_factory=list)
    comment: str = ""
    
    def __post_init__(self):
        """Validate curve data."""
        if not self.id:
            raise ValueError("Curve ID cannot be empty")
    
    def add_point(self, x: float, y: float):
        """Add a point to the curve."""
        self.points.append((x, y))
    
    def set_points(self, points: List[Tuple[float, float]]):
        """Set all curve points at once."""
        self.points = points.copy()
    
    def get_value(self, x: float) -> float:
        """Interpolate curve value at given x.
        
        Args:
            x: X-coordinate
        
        Returns:
            Interpolated Y value
        """
        if not self.points:
            return 0.0
        
        # Sort points by x if not already sorted
        sorted_points = sorted(self.points, key=lambda p: p[0])
        
        # Handle edge cases
        if x <= sorted_points[0][0]:
            return sorted_points[0][1]
        if x >= sorted_points[-1][0]:
            return sorted_points[-1][1]
        
        # Linear interpolation
        for i in range(len(sorted_points) - 1):
            x1, y1 = sorted_points[i]
            x2, y2 = sorted_points[i + 1]
            
            if x1 <= x <= x2:
                if x2 == x1:
                    return y1
                # Linear interpolation formula
                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)
        
        return 0.0
    
    def __len__(self) -> int:
        """Get number of points in curve."""
        return len(self.points)
