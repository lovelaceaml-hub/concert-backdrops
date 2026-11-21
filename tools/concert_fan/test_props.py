"""Small deterministic checks for held fan and silk dynamics.

Run from the repository root with:
PYTHONPATH=engine:. .venv/bin/python -m unittest tools.concert_fan.test_props
"""
import tempfile
import unittest

import numpy as np

from tools.concert_fan.props import FanSilk


class _MovingPalm:
    """Analytic final hand used to isolate prop constraints from the actor rig."""
    def where(self, t, name, normal=False):
        p = np.array([0.29 * np.sin(t * 2.3), 1.5 + 0.15 * np.sin(t * 1.8),
                      0.12 * np.sin(t * 1.3)])
        theta = 0.38 * np.sin(t * 1.1)
        forward = np.array([np.sin(theta), np.cos(theta), 0.0])
        if name.startswith("fingertips"):
            p = p + forward * 0.12
        return (p, np.array([0.0, 0.0, 1.0])) if normal else p


class FanSilkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.body = _MovingPalm()
        cls.kwargs = dict(duration=2.0, rows=17, cols=9, point_count=500,
                          preroll=0.5, cache_dir=cls.temp.name, collide=False)
        cls.fan = FanSilk(cls.body, **cls.kwargs).prebake()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_attachment_and_seek_order(self):
        for t in (1.73, 0.0, 1.007, 2.0, 0.31):
            a = self.fan.positions(t)
            self.fan.positions(1.5)
            np.testing.assert_array_equal(a, self.fan.positions(t))
            expected = self.fan._pins_from_frame(self.fan.hand_frame(t))
            np.testing.assert_allclose(a[0], expected, atol=2e-7)
            self.assertTrue(np.isfinite(a).all())
        self.assertFalse(self.fan._snaps.flags.writeable)

    def test_finite_sheet_and_floor(self):
        d = self.fan.diagnostics()
        self.assertLess(d["max_pin_error_m"], 2e-7)
        self.assertLess(d["floor_penetration_m"], 1e-7)
        self.assertLess(d["p99_structural_strain"], 0.15)
        for t in (0.1, 0.9, 1.7):
            grid = self.fan.positions(t)
            distance = np.linalg.norm(grid - grid[:1], axis=-1)
            self.assertLess(float(distance.max()), self.fan.length * 1.10)
            self.assertGreater(np.linalg.norm(grid[0, -1] - grid[0, 0]), 0.6)

    def test_cache_and_render_batches(self):
        again = FanSilk(self.body, **self.kwargs).prebake()
        self.assertTrue(again.diagnostics()["cache_hit"])
        np.testing.assert_array_equal(self.fan.positions(1.3), again.positions(1.3))
        batches = again.sample(1.3)
        self.assertTrue(any(b["kind"] == "soft" and len(b["pos"]) == 500 for b in batches))
        self.assertTrue(any(b["kind"] == "line" and len(b["pos"]) == again.ribs for b in batches))
        for batch in batches:
            self.assertTrue(np.isfinite(batch["pos"]).all())
            self.assertTrue(np.all(np.asarray(batch["alpha"]) >= 0))
        changed = FanSilk(self.body, **(self.kwargs | {"length": 1.3})).prebake()
        self.assertNotEqual(again.diagnostics()["identity"], changed.diagnostics()["identity"])


if __name__ == "__main__":
    unittest.main()
