"""Unit tests for geometry calculations and display tiling."""

import unittest
from layout_engine.geometry import Rect, DisplayInfo, compute_grid_layout

class TestGeometry(unittest.TestCase):
    def setUp(self):
        self.ultrawide = DisplayInfo(
            index=0,
            name="UltraWide",
            is_ultrawide=True,
            bounds=Rect(x=0, y=0, w=3440, h=1440)
        )
        self.retina = DisplayInfo(
            index=1,
            name="MacBook Retina",
            is_ultrawide=False,
            bounds=Rect(x=3440, y=0, w=1680, h=1050)
        )

    def test_rect_properties(self):
        r = Rect(10, 20, 100, 200)
        self.assertEqual(r.right, 110)
        self.assertEqual(r.bottom, 220)
        self.assertTrue(r.intersects(Rect(50, 50, 100, 100)))
        self.assertFalse(r.intersects(Rect(200, 300, 50, 50)))

    def test_empty_layout(self):
        tiles = compute_grid_layout(self.ultrawide, 0)
        self.assertEqual(tiles, [])

    def test_single_window_layout(self):
        tiles = compute_grid_layout(self.ultrawide, 1, padding=10)
        self.assertEqual(len(tiles), 1)
        self.assertEqual(tiles[0].x, 10)
        self.assertEqual(tiles[0].y, 10)
        self.assertEqual(tiles[0].w, 3420)
        self.assertEqual(tiles[0].h, 1420)

    def test_ultrawide_multi_window_tiling(self):
        # 4 windows on ultrawide should be 4x1 or 2x2
        tiles = compute_grid_layout(self.ultrawide, 4, padding=8, gap=6)
        self.assertEqual(len(tiles), 4)
        # Verify no overlapping tiles
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                self.assertFalse(tiles[i].intersects(tiles[j]))

    def test_retina_multi_window_tiling(self):
        # 4 windows on 16:10 retina should be 2x2 grid
        tiles = compute_grid_layout(self.retina, 4, padding=8, gap=6)
        self.assertEqual(len(tiles), 4)
        # All tiles must be within display bounds
        for t in tiles:
            self.assertGreaterEqual(t.x, self.retina.bounds.x)
            self.assertLessEqual(t.right, self.retina.bounds.right)
            self.assertGreaterEqual(t.y, self.retina.bounds.y)
            self.assertLessEqual(t.bottom, self.retina.bounds.bottom)

if __name__ == "__main__":
    unittest.main()
