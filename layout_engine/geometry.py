"""Geometry calculations, display boundary management, and multi-monitor coordinate translation."""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import math

@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.right <= other.x
            or self.x >= other.right
            or self.bottom <= other.y
            or self.y >= other.bottom
        )

    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}

@dataclass
class DisplayInfo:
    index: int
    name: str
    is_ultrawide: bool
    bounds: Rect

    @property
    def aspect_ratio(self) -> float:
        return self.bounds.w / max(1, self.bounds.h)

def compute_grid_layout(
    display: DisplayInfo,
    window_count: int,
    padding: int = 8,
    gap: int = 6,
    max_cols: int | None = None
) -> List[Rect]:
    """
    Computes a balanced, optimal geometric tile layout for N windows on a display.
    Optimized for high-density Ultrawide (21:9) and MacBook Retina (16:10) displays.
    """
    if window_count <= 0:
        return []

    # Available usable space inside display boundaries
    usable_w = display.bounds.w - (2 * padding)
    usable_h = display.bounds.h - (2 * padding)

    if usable_w <= 0 or usable_h <= 0:
        return [Rect(display.bounds.x, display.bounds.y, 100, 100) for _ in range(window_count)]

    # Determine optimal rows and columns based on aspect ratio and window count
    if display.is_ultrawide:
        # Ultrawide prioritizes 3 to 4 columns
        if window_count == 1:
            cols, rows = 1, 1
        elif window_count == 2:
            cols, rows = 2, 1
        elif window_count <= 4:
            cols, rows = window_count, 1
        elif window_count <= 6:
            cols, rows = 3, 2
        elif window_count <= 8:
            cols, rows = 4, 2
        else:
            cols = min(max_cols or 4, math.ceil(math.sqrt(window_count * display.aspect_ratio / 1.5)))
            rows = math.ceil(window_count / cols)
    else:
        # Standard / Retina display (16:10 or 16:9)
        if window_count == 1:
            cols, rows = 1, 1
        elif window_count == 2:
            cols, rows = 2, 1
        elif window_count <= 4:
            cols, rows = 2, 2
        elif window_count <= 6:
            cols, rows = 3, 2
        else:
            cols = min(max_cols or 3, math.ceil(math.sqrt(window_count)))
            rows = math.ceil(window_count / cols)

    cell_w = int((usable_w - (cols - 1) * gap) / cols)
    cell_h = int((usable_h - (rows - 1) * gap) / rows)

    tiles = []
    for i in range(window_count):
        r = i // cols
        c = i % cols
        x = display.bounds.x + padding + c * (cell_w + gap)
        y = display.bounds.y + padding + r * (cell_h + gap)
        tiles.append(Rect(x=x, y=y, w=cell_w, h=cell_h))

    return tiles
