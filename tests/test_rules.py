"""Unit tests for window and process filter rules."""

import unittest
from layout_engine.rules import WindowFilterRule

class TestRules(unittest.TestCase):
    def setUp(self):
        self.rule = WindowFilterRule()

    def test_process_matching(self):
        self.assertTrue(self.rule.is_target_process("Coral Poker"))
        self.assertTrue(self.rule.is_target_process("partypoker"))
        self.assertTrue(self.rule.is_target_process("Google Chrome"))
        self.assertFalse(self.rule.is_target_process("Slack"))
        self.assertFalse(self.rule.is_target_process("Spotify"))

    def test_lobby_exclusion(self):
        # Lobbies and settings must be excluded
        self.assertFalse(self.rule.is_valid_table_window("poker", "Settings", 800, 600))
        self.assertFalse(self.rule.is_valid_table_window("poker", "Tournament Lobby", 900, 700))
        self.assertFalse(self.rule.is_valid_table_window("Coral Poker", "Cashier", 800, 600))

    def test_size_thresholds(self):
        # Windows below minimum dimensions are rejected
        self.assertFalse(self.rule.is_valid_table_window("poker", "Table #1", 200, 150))

    def test_valid_game_tables(self):
        self.assertTrue(self.rule.is_valid_table_window("poker", "Table #12 - $1/$2 NLH", 800, 600))
        self.assertTrue(self.rule.is_valid_table_window("Google Chrome", "Paddy Power Poker - Table #4", 900, 650))
        self.assertFalse(self.rule.is_valid_table_window("Google Chrome", "Reddit - Home", 1200, 800))

if __name__ == "__main__":
    unittest.main()
