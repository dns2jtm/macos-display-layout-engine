"""High-performance macOS window management daemon and automated multi-display tiling engine."""

__version__ = "1.0.0"

from .geometry import Rect, DisplayInfo, compute_grid_layout
from .rules import WindowFilterRule
from .core import LayoutManager

__all__ = [
    "Rect",
    "DisplayInfo",
    "compute_grid_layout",
    "WindowFilterRule",
    "LayoutManager",
]
