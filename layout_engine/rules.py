"""Window filtering, process matching rules, and exclusion filters."""

from typing import List, Set, Dict, Any
import re

DEFAULT_PROCESS_NAMES = [
    'poker',
    'Coral Poker',
    'Ladbrokes Poker',
    'partypoker',
    'CoinPoker',
    'Google Chrome',
    'Safari',
    'Brave Browser'
]

DEFAULT_LOBBY_SUBSTRINGS = [
    'settings',
    'lobby',
    'cashier',
    'my account',
    'deposit',
    'withdrawal',
    'tournament lobby',
    'preferences',
    'google',
    'reddit',
    'youtube',
    'github'
]

TABLE_INDICATORS = [
    'table #',
    'table -',
    'blinds:',
    'hand #',
    'paddy power poker',
    'instant play',
    'playtech',
    'tournament #'
]

class WindowFilterRule:
    """Evaluates whether a detected window is an active game table or an auxiliary/lobby window."""

    def __init__(
        self,
        allowed_processes: List[str] | None = None,
        ignore_substrings: List[str] | None = None,
        table_indicators: List[str] | None = None,
        min_width: int = 300,
        min_height: int = 200
    ):
        self.allowed_processes = set(p.lower() for p in (allowed_processes or DEFAULT_PROCESS_NAMES))
        self.ignore_substrings = set(s.lower() for s in (ignore_substrings or DEFAULT_LOBBY_SUBSTRINGS))
        self.table_indicators = [i.lower() for i in (table_indicators or TABLE_INDICATORS)]
        self.min_width = min_width
        self.min_height = min_height

    def is_target_process(self, process_name: str) -> bool:
        if not process_name:
            return False
        p_lower = process_name.lower()
        return any(target in p_lower for target in self.allowed_processes)

    def is_valid_table_window(self, app_name: str, title: str, width: int, height: int) -> bool:
        """Determines if a window represents an active playable session table."""
        if width < self.min_width or height < self.min_height:
            return False

        if not title:
            return False

        t_lower = title.lower().strip()
        app_lower = (app_name or '').lower().strip()

        # Check explicit ignore patterns
        if any(ign in t_lower for ign in self.ignore_substrings):
            return False

        # Browser processes require explicit table indicators in the title
        if any(b in app_lower for b in ['chrome', 'safari', 'brave', 'firefox', 'edge']):
            return any(ind in t_lower for ind in self.table_indicators)

        # Native poker client applications
        if any(p in app_lower for p in ['poker', 'coral', 'ladbrokes', 'partypoker', 'coinpoker']):
            # Filter out generic top-level standalone app titles that represent the main client window
            if t_lower in ['888poker', 'coral poker', 'coral poker lobby', 'ladbrokes poker', 'partypoker', 'coinpoker']:
                return False
            return True

        return False
