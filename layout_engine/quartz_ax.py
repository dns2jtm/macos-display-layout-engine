"""Native macOS Quartz (CoreGraphics) and Accessibility (AXUIElement) window management."""

import sys
from typing import List, Dict, Any, Optional
from .geometry import Rect, DisplayInfo

try:
    import Quartz
    import AppKit
    import ApplicationServices
    HAS_MACOS_APIS = True
except ImportError:
    HAS_MACOS_APIS = False

class NativeBridge:
    """Interfaces with macOS Cocoa, Quartz Window Services, and Accessibility APIs."""

    @staticmethod
    def get_displays() -> List[DisplayInfo]:
        """Queries active connected displays via Quartz."""
        if not HAS_MACOS_APIS:
            # Fallback mock for testing / non-macOS execution
            return [
                DisplayInfo(index=0, name="Simulated UltraWide (3440x1440)", is_ultrawide=True, bounds=Rect(0, 0, 3440, 1440)),
                DisplayInfo(index=1, name="Simulated MacBook Retina", is_ultrawide=False, bounds=Rect(3440, 0, 1680, 1050))
            ]

        err, active_displays, count = Quartz.CGGetActiveDisplayList(10, None, None)
        displays = []
        for i, d in enumerate(active_displays):
            b = Quartz.CGDisplayBounds(d)
            w = int(b.size.width)
            h = int(b.size.height)
            x = int(b.origin.x)
            y = int(b.origin.y)
            is_uw = w >= 2500
            name = f"UltraWide ({w}x{h})" if is_uw else f"Retina ({w}x{h})"
            displays.append(
                DisplayInfo(
                    index=i,
                    name=name,
                    is_ultrawide=is_uw,
                    bounds=Rect(x=x, y=y, w=w, h=h)
                )
            )
        return displays

    @staticmethod
    def get_windows(rule) -> List[Dict[str, Any]]:
        """Scans open windows across processes using hybrid AXUIElement + CGWindowList."""
        if not HAS_MACOS_APIS:
            return []

        windows = []
        ws = AppKit.NSWorkspace.sharedWorkspace()
        q_windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID)

        # 1. Cocoa Accessibility API scan
        for app in ws.runningApplications():
            app_name = app.localizedName() or ""
            if not rule.is_target_process(app_name):
                continue

            pid = app.processIdentifier()
            app_ref = ApplicationServices.AXUIElementCreateApplication(pid)
            err, wins = ApplicationServices.AXUIElementCopyAttributeValue(
                app_ref, ApplicationServices.kAXWindowsAttribute, None
            )
            if err == 0 and wins:
                for w in wins:
                    err_t, title = ApplicationServices.AXUIElementCopyAttributeValue(w, ApplicationServices.kAXTitleAttribute, None)
                    err_p, pos_val = ApplicationServices.AXUIElementCopyAttributeValue(w, ApplicationServices.kAXPositionAttribute, None)
                    err_s, sz_val = ApplicationServices.AXUIElementCopyAttributeValue(w, ApplicationServices.kAXSizeAttribute, None)
                    
                    x, y, width, height = 0, 0, 0, 0
                    if err_p == 0 and pos_val:
                        ok, pt = ApplicationServices.AXValueGetValue(pos_val, ApplicationServices.kAXValueCGPointType, None)
                        if ok: x, y = int(pt.x), int(pt.y)
                    if err_s == 0 and sz_val:
                        ok, sz = ApplicationServices.AXValueGetValue(sz_val, ApplicationServices.kAXValueCGSizeType, None)
                        if ok: width, height = int(sz.width), int(sz.height)

                    if rule.is_valid_table_window(app_name, title or "", width, height):
                        windows.append({
                            "pid": pid,
                            "app": app_name,
                            "title": title or "",
                            "bounds": Rect(x, y, width, height),
                            "ax_ref": w
                        })

        return windows

    @staticmethod
    def set_window_bounds(window: Dict[str, Any], target_rect: Rect) -> bool:
        """Applies position and size updates using AXUIElement."""
        if not HAS_MACOS_APIS or not window.get("ax_ref"):
            return False

        w_ref = window["ax_ref"]
        # Position
        pt = ApplicationServices.CGPoint(x=target_rect.x, y=target_rect.y)
        pos_val = ApplicationServices.AXValueCreate(ApplicationServices.kAXValueCGPointType, pt)
        ApplicationServices.AXUIElementSetAttributeValue(w_ref, ApplicationServices.kAXPositionAttribute, pos_val)

        # Size
        sz = ApplicationServices.CGSize(width=target_rect.w, height=target_rect.h)
        sz_val = ApplicationServices.AXValueCreate(ApplicationServices.kAXValueCGSizeType, sz)
        ApplicationServices.AXUIElementSetAttributeValue(w_ref, ApplicationServices.kAXSizeAttribute, sz_val)
        return True
