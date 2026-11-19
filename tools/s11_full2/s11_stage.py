"""Song 11 v2: the heavenly choir (gold glitter) and the crystal orchestra on the square before the
church of light, their instruments, the light of their singing, and the snow of light in the breath.

Owned by the stage thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

SHOTS = [
    # the choir breathes in (cut-in)
    dict(name="choir_breath_in", kind="stage", t0=77.46, t1=82.08, fov=34.0, aperture=0.09, focus=_v(0.0, SUMMIT + 2.0, FACADE_Z + 3.0),
         keys=[(77.46, _v(-3.0, Y + 1.6, FZ + 12.0), _v(-1.0, Y + 3.4, FZ + 2.0)),
                        (82.08, _v(-1.5, Y + 1.7, FZ + 10.5), _v(-0.5, Y + 3.5, FZ + 2.0))]),
    # E. the first slam: the full choir and orchestra, the sunrise jumps behind them
    dict(name="slam1_stage", kind="stage", t0=82.08, t1=86.70, fov=50.0, aperture=0.09, focus=_v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0),
         keys=[(82.08, _v(0.0, Y + 6.0, FZ + 52.0), _v(0.0, Y + 8.0, FZ - 20.0)),
                        (86.70, _v(0.0, Y + 8.0, FZ + 44.0), _v(0.0, Y + 9.0, FZ - 20.0))]),
    # the breath: the choir still and glowing, light falling like snow
    dict(name="choir_snow", kind="stage", t0=117.0, t1=121.32, fov=34.0, aperture=0.09, focus=_v(0.0, SUMMIT + 2.0, FACADE_Z + 3.0),
         keys=[(117.0, _v(4.0, Y + 2.0, FZ + 15.0), _v(0.0, Y + 3.2, FZ + 2.0)),
                         (121.32, _v(2.5, Y + 2.0, FZ + 13.5), _v(0.0, Y + 3.2, FZ + 2.0))]),
    # verse 2 opens: the strings pulse (cut-in)
    dict(name="strings", kind="stage", t0=121.32, t1=125.92, fov=44.0, aperture=0.09, focus=_v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0),
         keys=[(121.32, _v(-14.0, Y + 3.0, FZ + 30.0), _v(-4.0, Y + 1.0, FZ + 14.0)),
                          (125.92, _v(-11.0, Y + 2.6, FZ + 27.0), _v(-3.0, Y + 1.0, FZ + 14.0))]),
    # the second slam: brass and timpani blaze (cut-in)
    dict(name="brass2", kind="stage", t0=162.86, t1=165.16, fov=42.0, aperture=0.09, focus=_v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0),
         keys=[(162.86, _v(12.0, Y + 3.2, FZ + 31.0), _v(4.0, Y + 1.4, FZ + 15.0)),
                          (165.16, _v(10.5, Y + 3.0, FZ + 29.5), _v(4.0, Y + 1.4, FZ + 15.0))]),
    # "wondrous love": brass and timpani (cut-in)
    dict(name="brass_love", kind="stage", t0=185.92, t1=188.27, fov=42.0, aperture=0.09, focus=_v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0),
         keys=[(185.92, _v(-12.0, Y + 3.2, FZ + 31.0), _v(-4.0, Y + 1.4, FZ + 15.0)),
                          (188.27, _v(-10.5, Y + 3.0, FZ + 29.5), _v(-4.0, Y + 1.4, FZ + 15.0))]),
    # home to everyone on Mount Zion: the final calls, the held breath, the last chord
    dict(name="home_stage", kind="stage", t0=238.8, t1=254.07, fov=50.0, aperture=0.09, focus=_v(0.0, SUMMIT + 1.0, FACADE_Z + 14.0),
         keys=[(238.8, _v(0.0, Y + 4.0, FZ + 40.0), _v(0.0, Y + 6.0, FZ - 10.0)),
                         (254.07, _v(0.0, Y + 5.0, FZ + 30.0), _v(0.0, Y + 7.0, FZ - 10.0))]),
]


def _choir_places():
    pts = []
    for i, (yy, zz) in enumerate(CHOIR_STEPS[:3]):
        n = 22 - i
        for j in range(n):
            x = (j - (n - 1) / 2.0) * 1.05 + (0.5 if i % 2 else 0.0)
            pts.append((x, yy, zz))
    return np.asarray(pts, np.float64)


ORCH = dict(strings_l=[], strings_r=[], cellos=[], harps=[], timpani=[], brass=[])


def _orch_places():
    """Seats in arcs on the square, facing the avenue (+z); sections: violins left, violas and cellos right,
    harps at the far left, brass and timpani at the back."""
    c = SQUARE + _v(0.0, 0.0, -2.0)
    pts = []
    for row, (r0, n) in enumerate(((7.0, 12), (10.0, 16), (13.0, 18))):
        for j in range(n):
            a = np.radians(-70.0 + 140.0 * j / (n - 1))
            p = c + _v(r0 * np.sin(a), 0.0, r0 * np.cos(a) * 0.55 - 6.0)
            pts.append(p)
            if row == 0:
                (ORCH["strings_l"] if a < 0 else ORCH["strings_r"]).append(p)
            elif row == 1:
                (ORCH["strings_l"] if a < -0.3 else ORCH["cellos"] if a > 0.3 else ORCH["strings_r"]).append(p)
            else:
                (ORCH["brass"] if abs(a) < 0.5 else ORCH["timpani"] if a > 0.9 else ORCH["strings_l"]).append(p)
    ORCH["harps"] = [c + _v(-15.5, 0.0, -2.0), c + _v(-17.0, 0.0, -5.0)]
    return np.asarray(pts, np.float64)


CHOIR_P = _choir_places()
ORCH_P = _orch_places()


def stage_k(t):
    """How present the choir and orchestra are: always there on the square (they show in the wide views of the
    city), formed in the intro (the orchestra wakes from 0:02.3, the choir out of the light from 0:21.5)."""
    return local_k(t)


def _instruments():
    """The orchestra's instruments drawn in crystal light (standing on the square, so they stay put)."""
    pts = []
    for h in ORCH["harps"]:
        a = np.linspace(0.0, 1.0, 40)
        col = _seg(h + _v(0.25, 0.0, 0.0), h + _v(0.25, 1.85, 0.0), 0.03)
        board = _seg(h + _v(-0.45, 0.15, 0.0), h + _v(0.22, 1.75, 0.0), 0.03)
        neck = np.stack([h[0] + 0.25 - 0.70 * a, h[1] + 1.85 - 0.25 * np.sin(np.pi * a) - 0.1 * a, np.full(40, h[2])], 1)
        strings = [_seg(h + _v(-0.45 + 0.67 * u, 0.15 + 1.60 * u, 0.0),
                        h + _v(-0.45 + 0.67 * u, 1.85 - 0.25 * np.sin(np.pi * (1 - u)) - 0.1 * (1 - u), 0.0), 0.04)
                   for u in np.linspace(0.05, 0.95, 16)]
        pts += [col, board, neck] + strings
    for p in ORCH["timpani"]:
        q = p + _v(0.0, 0.0, 0.9)
        pts.append(_ring(q, 0.55, q[1] + 0.85, 0.03))
        for el in np.linspace(0.2, 1.3, 5):
            pts.append(_ring(q, 0.55 * np.cos(el), q[1] + 0.85 - 0.5 * np.sin(el), 0.04))
    for p in ORCH["cellos"]:
        q = p + _v(0.0, 0.0, 0.45)
        a = np.linspace(0, 2 * np.pi, 60)
        pts.append(np.stack([q[0] + 0.22 * np.sin(a) * (1 + 0.15 * np.cos(2 * a)), q[1] + 0.48 + 0.36 * np.cos(a),
                             np.full(60, q[2])], 1))
        pts.append(_seg(q + _v(0.0, 0.84, 0.0), q + _v(0.0, 1.40, -0.05), 0.03))
    for p in ORCH["brass"]:
        q = p + _v(0.0, 0.92, 0.32)
        pts.append(_seg(q, q + _v(0.0, 0.0, 0.42), 0.03))
        pts.append(_ring(q + _v(0.0, 0.0, 0.42), 0.09, q[1], 0.02))
    return np.concatenate(pts)


INSTR_P = None


class Instruments:
    """Crystal instruments; bows of light that move with the beat; light bursting from the brass and timpani
    on the hits (bows and breath move with the beat: Anthony's choice)."""

    def __init__(self, offset=_v(0.0, 0.0, 0.0), gain=None):
        self.P = _instruments() + offset
        self.off = offset
        self.g = gain or stage_k
        r = np.random.default_rng(5)
        self.bp = np.asarray(ORCH["strings_l"] + ORCH["strings_r"], np.float64) + offset
        self.ph = r.random(len(self.bp))
        self.hitters = np.asarray(ORCH["brass"] + ORCH["timpani"], np.float64) + offset
        self.s = r.random((len(self.hitters), 60, 3))

    def sample(self, t):
        g = self.g(t)
        if g <= 0.0:
            return None
        out = [dict(pos=self.P, size=0.035, color=lin(CRYSTAL), alpha=0.9 * g, emit=2.2, kind="spark",
                    twinkle=0.3)]
        # bows: a short line above each string player, drawn back and forth with the beat
        i = np.searchsorted(BEATS, t)
        b0 = BEATS[max(i - 1, 0)] if i > 0 else 0.0
        b1 = BEATS[min(i, len(BEATS) - 1)]
        ph = np.clip((t - b0) / max(b1 - b0, 1e-3), 0.0, 1.0)
        sw = np.cos(np.pi * (ph + self.ph * 0.25)) * (0.22 if t > 2.0 else 0.0)
        c = self.bp + _v(0.18, 0.86, 0.2)
        d = _unit(_v(1.0, -0.35, 0.2))
        a = c + d[None, :] * (sw[:, None] - 0.3)
        b = c + d[None, :] * (sw[:, None] + 0.3)
        out.append(dict(pos=a, pos2=b, size=0.018, color=lin("#f4fbff"), alpha=0.9 * g, emit=2.4, kind="line"))
        # light bursts from the brass and timpani on the big hits
        hits = [HIT["glory"], HIT["stream"], SLAM1, SLAM2, HIT["love"], SLAM3, HIT["devotion"], LAST_CHORD]
        k = 0.0
        last = None
        for h in hits:
            if 0.0 <= t - h < 1.6:
                k, last = np.exp(-(t - h) / 0.45), h
        if k > 0.01:
            u = t - last
            dirs = self.s - 0.5
            dirs /= np.linalg.norm(dirs, axis=2, keepdims=True)
            pos = self.hitters[:, None, :] + _v(0.0, 1.0, 0.4) + dirs * (0.2 + 2.2 * u)
            out.append(dict(pos=pos.reshape(-1, 3), size=0.06, color=lin("#fff1cf"), alpha=k * g, emit=4.0,
                            kind="spark"))
            out.append(dict(pos=self.hitters + _v(0.0, 1.0, 0.4), size=1.6, color=lin(GOLD), alpha=0.5 * k * g,
                            kind="soft", emit=2.0))
        return out


class ChoirLight:
    """Light rising from the choir as they sing: more with the loudness, nothing while they are silent."""

    def __init__(self, places, gain=None):
        self.p = places
        r = np.random.default_rng(9)
        self.s = r.random((len(places) * 6, 4))
        self.g = gain or stage_k

    def sample(self, t):
        g = self.g(t)
        sing = 0.0
        for a, b, w in PERFORM:
            if a <= t < b and w.startswith("Choir"):
                sing = 1.0
        k = g * sing * _sc(21.4, 22.6, t) * (0.35 + 0.65 * loud(t))
        if k <= 0.01:
            return None
        s = self.s
        base = np.repeat(self.p, 6, axis=0) + _v(0.0, 1.55, 0.25)
        age = np.mod(t * (0.25 + 0.2 * s[:, 0]) + s[:, 1], 1.0)
        pos = base + np.stack([0.4 * (s[:, 2] - 0.5), 4.0 * age, 0.3 * (s[:, 3] - 0.5)], 1)
        return dict(pos=pos, size=0.05 + 0.05 * s[:, 2], color=lin("#ffe6b0"), alpha=k * (1 - age) ** 1.5,
                    emit=2.5, kind="spark", twinkle=0.7, seed=s[:, 3])


PERFORM = [(0.0, 21.5, "Orchestra (faint choir hum)"), (21.5, 29.8, "Choir and orchestra"), (29.8, 31.0, "Orchestra"),
           (31.0, 39.0, "Choir and orchestra"), (39.0, 41.0, "Orchestra"), (41.0, 247.5, "Choir and orchestra"),
           (247.5, 249.5, "Held breath"), (249.5, 259.95, "Choir and orchestra"), (259.95, 275.0, "Silence")]


class Snow:
    """The breath (1:57 to 2:01.3): light falls like snow round the still, glowing choir."""

    def __init__(self):
        r = np.random.default_rng(101)
        self.s = r.random((1400, 5))

    def sample(self, t):
        if not (116.5 <= t < 121.9) or local_k(t) <= 0.0:
            return None
        k = _env(t, 116.8, 121.8, 0.6, 0.8)
        s = self.s
        y = SUMMIT + 13.0 - np.mod(t * (0.5 + 0.5 * s[:, 2]) + 13.0 * s[:, 3], 13.0)
        x = -16.0 + 32.0 * s[:, 0] + 0.3 * np.sin(t * 0.8 + 6.0 * s[:, 4])
        z = FACADE_Z - 4.0 + 22.0 * s[:, 1]
        return dict(pos=np.stack([x, y, z], 1), size=0.025 + 0.03 * s[:, 4], color=lin("#fff1d8"), alpha=0.6 * k,
                    emit=1.8, kind="soft", twinkle=0.5, seed=s[:, 4])


def add(scene):
    choir = Crowd(places=CHOIR_P, facing=0.0, kinds=("stand",), people=dict(woman=1.0, man=1.0),
                  start=dict(t=21.3, center=(0.0, FACADE_Z), speed=9.0), color="#ffb84a", color2="#ffe9b8",
                  bright=1.7, points=2400, flash=1.2, glints=0.004, seed=3.0)
    scene.add("choir", choir)
    orch = Crowd(places=ORCH_P, facing=0.0, kinds=("sit",), people=dict(woman=1.0, man=1.0),
                 start=dict(t=2.2, dur=7.0), color=CRYSTAL, color2="#ffffff", bright=1.15, points=2200,
                 glints=0.006, seed=4.0)
    scene.add("orchestra", orch)
    scene.add("instruments", Instruments())
    scene.add("choir light", ChoirLight(CHOIR_P))
    scene.add("snow", Snow())
