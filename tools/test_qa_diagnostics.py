"""Focused QA diagnostics fixtures: python tools/test_qa_diagnostics.py."""
import unittest
from types import SimpleNamespace
import numpy as np
import qa_check as q


class Diagnostics(unittest.TestCase):
    def test_smooth_and_frozen(self):
        t = np.arange(300) / 60
        f = np.tile(np.arange(300, dtype=np.float32)[:, None, None] * .2, (1, 2, 2))
        issues = []
        q.motion_metrics(f, t, issues, [])
        self.assertEqual(issues, [])
        q.motion_metrics(np.zeros_like(f), t, issues, [])
        self.assertTrue(any(i['check'] == 'Frozen video' for i in issues))

    def test_strobe_and_declared_cut(self):
        t = np.arange(300) / 60
        f = np.tile((np.arange(300) % 2 * 100)[:, None, None], (1, 2, 2))
        issues = []
        q.motion_metrics(f, t, issues, [])
        self.assertTrue(any(i['check'] == 'Motion strobing' for i in issues))
        f[:150] = 0
        f[150:] = 100
        issues = []
        q.motion_metrics(f, t, issues, [], cuts=[2.5])
        self.assertFalse(any(i['check'] == 'Single-frame jump' for i in issues))

    def test_titles_reveal_not_hold(self):
        s = SimpleNamespace(NFRAMES=3720, FPS=60, TITLES={
            'opening': {'t_end': 8.6}, 'end_card': {'t_in': 53.4}})
        issues = []
        q.titles_checks(s, issues, [])
        self.assertEqual(issues, [])
        s.TITLES = {'opening': {'t_end': 7}, 'end_card': {'t_in': 55}}
        q.titles_checks(s, issues, [])
        self.assertEqual(len(issues), 2)

    def test_empty_audio(self):
        issues = []
        result = q.audio_metrics(np.array([]), 48000, issues, [])
        self.assertEqual(result["skipped"], "empty decoded audio")
        self.assertEqual(issues[0]["check"], "Audio decode")

    def test_audio_silence_clipping_and_stereo(self):
        issues = []
        q.audio_metrics(np.zeros(48000 * 5), 48000, issues, [], 2)
        self.assertEqual(issues, [])
        q.audio_metrics(np.column_stack([np.ones(48000 * 5), -np.ones(48000 * 5)]),
                        48000, issues, [], 2)
        self.assertGreaterEqual({i['check'] for i in issues},
                                {'Audio clipping', 'Opening silence', 'Abrupt audio ending'})


if __name__ == '__main__':
    unittest.main()
