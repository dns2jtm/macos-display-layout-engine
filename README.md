# macOS Display Layout Engine & Multi-Process Window Daemon

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://apple.com/macos)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

A high-performance macOS window management daemon and automated multi-display tiling engine built on native Cocoa, **Quartz (CoreGraphics)**, and Accessibility (`AXUIElement`) APIs. Engineered to dynamically detect, monitor, and tile active game sessions across multi-monitor setups (including 3440×1440 UltraWide and MacBook Retina displays) with sub-100ms response time and zero UI latency.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                   LayoutDaemon Loop                    │
└───────────────────────────┬────────────────────────────┘
                            │ (Polling / Event Taps)
              ┌─────────────▼─────────────┐
              │     NativeBridge (macOS)  │
              └──────┬─────────────┬──────┘
                     │             │
        ┌────────────▼──┐       ┌──▼────────────┐
        │  Quartz CG    │       │  Cocoa AX     │
        │ Window List   │       │ Accessibility │
        └────────────┬──┘       └──┬────────────┘
                     │             │
              ┌──────▼─────────────▼──────┐
              │    WindowFilterRule       │
              │  (Process / Title Match)  │
              └─────────────┬─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │    Geometry Engine        │
              │ (UltraWide 21:9 / Retina) │
              └─────────────┬─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │  AXUIElement Tiling Set   │
              └───────────────────────────┘
```

---

## Key Features

- **Hybrid Quartz & Accessibility Engine:** Uses `CGWindowListCopyWindowInfo` for high-speed hardware-level window metadata inspection and Cocoa `AXUIElement` for sub-100ms atomic window repositioning and resizing.
- **Multi-Display & Coordinate Space Translation:** Automatically detects connected displays via `CGGetActiveDisplayList`, scaling geometric layouts across primary 3440×1440 21:9 UltraWide screens and secondary MacBook Retina displays.
- **Dynamic Topology Calculation:** Automatically computes optimal grid configurations ($N \times M$), maintaining aspect-ratio preservation, cell gaps, and boundary padding.
- **Multi-Process Concurrency:** Intercepts and monitors window states across 7+ concurrent client processes (native apps and web-wrapped game clients) while ignoring lobbies, cashiers, settings, and auxiliary popups.
- **Resilient Background Daemon:** Runs with low CPU utilization (<0.5%), persisting state through dynamic display connect and disconnect events.

---

## Installation

### Prerequisites
- macOS 12 Monterey, macOS 13 Ventura, macOS 14 Sonoma, or macOS 15 Sequoia
- Python 3.10+
- macOS Accessibility Permissions (System Settings → Privacy & Security → Accessibility)

### Setup
```bash
git clone https://github.com/dns2jtm/macos-display-layout-engine.git
cd macos-display-layout-engine
pip install -r requirements.txt
```

---

## Quick Start & CLI Usage

### 1. Inspect Connected Displays
```bash
python -m layout_engine.cli --list-displays
```
```text
Found 2 connected display(s):
  [0] UltraWide (3440x1440) -> Bounds: x=0, y=0, w=3440, h=1440 (UltraWide=True)
  [1] Retina (1680x1050) -> Bounds: x=3440, y=0, w=1680, h=1050 (UltraWide=False)
```

### 2. Inspect Active Target Windows
```bash
python -m layout_engine.cli --list-windows
```

### 3. Tile Windows (One-Shot)
```bash
python -m layout_engine.cli --display 0 --padding 10 --gap 8
```

### 4. Run in Continuous Background Daemon Mode
```bash
python -m layout_engine.cli --daemon --interval 1.0 --display 0
```

---

## Configuration & Filtering Rules

Default target client processes and custom exclusion heuristics can be extended in `layout_engine/rules.py`:

```python
from layout_engine import LayoutManager, WindowFilterRule

custom_rules = WindowFilterRule(
    allowed_processes=["poker", "coral poker", "partypoker", "Google Chrome"],
    ignore_substrings=["lobby", "settings", "cashier", "deposit"],
    min_width=350,
    min_height=250
)

manager = LayoutManager(rule=custom_rules)
manager.tile_windows(display_index=0)
```

---

## Running Unit Tests

```bash
python -m unittest discover tests
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
