"""Label model."""

from dataclasses import dataclass

@dataclass
class Label:
    """Map Label."""
    id: str
    x: float
    y: float
    text: str
    font_size: int = 10
    font_bold: bool = False
    font_italic: bool = False
