"""Time pattern model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Pattern:
    """Time pattern for demand or other time-varying parameters."""
    id: str
    multipliers: List[float] = field(default_factory=list)
    comment: str = ""
    
    def __post_init__(self):
        """Validate pattern data."""
        if not self.id:
            raise ValueError("Pattern ID cannot be empty")
    
    def add_multiplier(self, value: float):
        """Add a multiplier to the pattern."""
        self.multipliers.append(value)
    
    def set_multipliers(self, values: List[float]):
        """Set all multipliers at once."""
        self.multipliers = values.copy()
    
    def get_multiplier(self, period: int) -> float:
        """Get multiplier for a specific period.
        
        Args:
            period: Time period index (0-based)
        
        Returns:
            Multiplier value, or 1.0 if pattern is empty
        """
        if not self.multipliers:
            return 1.0
        
        # Wrap around if period exceeds pattern length
        index = period % len(self.multipliers)
        return self.multipliers[index]
    
    def get_average(self) -> float:
        """Get average multiplier value."""
        if not self.multipliers:
            return 1.0
        return sum(self.multipliers) / len(self.multipliers)
    
    def __len__(self) -> int:
        """Get number of multipliers in pattern."""
        return len(self.multipliers)

    def __bool__(self) -> bool:
        """Pattern object is always True."""
        return True
