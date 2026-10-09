"""CLI entry point for macos-display-layout-engine."""

import argparse
import json
import logging
import sys
from .core import LayoutManager
from .rules import WindowFilterRule

def main():
    parser = argparse.ArgumentParser(
        description="High-performance macOS multi-display window layout engine and daemon."
    )
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background daemon mode")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds for daemon mode")
    parser.add_argument("--display", type=int, default=0, help="Target display index (default: 0)")
    parser.add_argument("--padding", type=int, default=8, help="Padding in pixels from screen edges")
    parser.add_argument("--gap", type=int, default=6, help="Gap in pixels between tiled windows")
    parser.add_argument("--dry-run", action="store_true", help="Calculate layout without moving windows")
    parser.add_argument("--list-displays", action="store_true", help="Print detected displays and exit")
    parser.add_argument("--list-windows", action="store_true", help="Print detected target windows and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s"
    )

    manager = LayoutManager()

    if args.list_displays:
        displays = manager.get_displays()
        print(f"Found {len(displays)} connected display(s):")
        for d in displays:
            print(f"  [{d.index}] {d.name} -> Bounds: x={d.bounds.x}, y={d.bounds.y}, w={d.bounds.w}, h={d.bounds.h} (UltraWide={d.is_ultrawide})")
        return

    if args.list_windows:
        windows = manager.get_windows()
        print(f"Found {len(windows)} active target window(s):")
        for w in windows:
            print(f"  PID {w['pid']} ({w['app']}): '{w['title']}' -> {w['bounds'].w}x{w['bounds'].h} at ({w['bounds'].x}, {w['bounds'].y})")
        return

    if args.daemon:
        manager.run_daemon(interval=args.interval, display_index=args.display)
    else:
        results = manager.tile_windows(
            display_index=args.display,
            padding=args.padding,
            gap=args.gap,
            dry_run=args.dry_run
        )
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
