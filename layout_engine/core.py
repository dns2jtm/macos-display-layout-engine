"""Core LayoutEngine daemon and manager classes."""

import time
import logging
from typing import List, Dict, Any, Optional
from .geometry import Rect, DisplayInfo, compute_grid_layout
from .rules import WindowFilterRule
from .quartz_ax import NativeBridge

logger = logging.getLogger("layout_engine")

class LayoutManager:
    """Orchestrates display querying, window discovery, and layout execution."""

    def __init__(self, rule: Optional[WindowFilterRule] = None):
        self.rule = rule or WindowFilterRule()
        self.bridge = NativeBridge()

    def get_displays(self) -> List[DisplayInfo]:
        return self.bridge.get_displays()

    def get_windows(self) -> List[Dict[str, Any]]:
        return self.bridge.get_windows(self.rule)

    def tile_windows(
        self,
        display_index: int = 0,
        padding: int = 8,
        gap: int = 6,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Scans active target windows and repositions them into a balanced grid."""
        displays = self.get_displays()
        if not displays:
            logger.warning("No active displays found.")
            return []

        target_display = displays[0]
        for d in displays:
            if d.index == display_index:
                target_display = d
                break

        windows = self.get_windows()
        if not windows:
            logger.info("No matching target windows to tile.")
            return []

        grid = compute_grid_layout(target_display, len(windows), padding=padding, gap=gap)
        results = []

        for w, target_rect in zip(windows, grid):
            record = {
                "app": w["app"],
                "title": w["title"],
                "old_bounds": w["bounds"].to_dict(),
                "new_bounds": target_rect.to_dict()
            }
            if not dry_run:
                success = self.bridge.set_window_bounds(w, target_rect)
                record["applied"] = success
            else:
                record["applied"] = False
            results.append(record)

        return results

    def run_daemon(self, interval: float = 1.0, display_index: int = 0):
        """Continuously monitors and tiles windows when changes in window count occur."""
        logger.info(f"Starting LayoutDaemon (poll interval: {interval}s, display: {display_index})")
        last_count = -1

        try:
            while True:
                windows = self.get_windows()
                current_count = len(windows)
                if current_count != last_count and current_count > 0:
                    logger.info(f"Detected window count change ({last_count} -> {current_count}). Re-tiling...")
                    self.tile_windows(display_index=display_index)
                    last_count = current_count
                elif current_count == 0 and last_count > 0:
                    last_count = 0
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("LayoutDaemon terminated by user.")
