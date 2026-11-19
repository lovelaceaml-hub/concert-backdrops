"""Song 11 v2: the music made visible (round 6, Anthony: "Every part of the song where there is the bass, the choir
singing, even the difference in tenor and soprano, and the instruments should be considered and have effects";
"I can hear the bases, and that should make the lights flicker").

Owned by the music fx thread. Imported by tools/s11_full2/s11_full2.py (the core) beside the other threads and
added LAST (its add(scene) looks at what the others have placed). No SHOTS: it rides every thread's shots.
No em dash or en dash anywhere in this file.

The music map work/s11_full2/music_fx.npz (made by tools/s11_full2/s11_music_map.py from the recording; never in
git; the render machines receive it beside features.npz; another path with S11_MUSIC_FX) gives, 60 times a
second, the bass and kick, the timpani, the strings and their swells, the brass, the choir, the high voices
(sopranos, altos) and the low voices (tenors, basses). If the file is missing the film still loads and renders,
with these effects off (every helper returns 0). S11_MUSIC_FX_OFF=1 turns them off too.

What moves with what (every effect gated by the kind of shot; dimmed while a phrase reads; held down where the
music is already blazing so nothing whites out):
  bass and kick   the sea's glitter, the lights floating on the water and the dust lights in the air pulse and
                  flicker; the mist glows low over the sea (or over the summit square in the choir shots); a ring
                  of shore lights round the foot of Mount Zion flickers; on the Earth its rim breathes
  timpani         a shockwave ring of light runs out across the sea or up the terraces from where the camera
                  looks (one per hit, gone within 1.6 s, never across a cut)
  strings         glitter waves: bands of fine silver light rolling out from Zion across the sea (across the
                  summit floor in the choir shots), brighter with the strings, faster on their swells
  brass           the strongest ray source flares; the comets' heads flare
  high voices     the stars and the constellations brighten; sparkles high in the sky
  low voices      a low warm glow at the base of Zion and on the ground (the plateau floor in the choir shots)
Helpers for other threads: fx(name, t), fx_bass(t), fx_kick(t), fx_pulse(t), fx_timp(t), fx_strings(t),
fx_swell(t), fx_brass(t), fx_choir(t), fx_high(t), fx_low(t), fx_beat(t), timp_hits(), fx_on().
"""
import os
import pathlib

import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H


# =========================================================================================================
# The music map
# =========================================================================================================
def _map_path():
    p = os.environ.get("S11_MUSIC_FX")
    if p:
        return pathlib.Path(p)
    f = os.environ.get("FEATURES")
    if f:
        return pathlib.Path(f).parent / "music_fx.npz"
    return REPO / "work/s11_full2/music_fx.npz"


def _load():
    if os.environ.get("S11_MUSIC_FX_OFF"):
        return None
    try:
        with np.load(_map_path()) as z:
            return {k: np.asarray(z[k], np.float64) for k in z.files}
    except Exception as e:  # noqa: BLE001  (missing or unreadable: the film renders without these effects)
        print(f"music fx: off ({_map_path()}: {type(e).__name__})", flush=True)
        return None


_M = _load()
_T = _M["times"] if _M else None


def fx_on():
    return _M is not None


def fx(name, t):
    """A series of the music map at t (0 when the map is missing or past the music)."""
    if _M is None or name not in _M or t > LIVE:
        return 0.0
    return float(np.interp(t, _T, _M[name], left=0.0, right=0.0))


def fx_bass(t):
    return fx("bass", t)


def fx_kick(t):
    return fx("kick", t)


def fx_pulse(t):
    """The low end as light: a jump on every kick (bigger when the bass is strong) over a soft bass level."""
    b = fx("bass", t)
    return float(min(1.0, fx("kick", t) * (0.45 + 0.55 * b) + 0.30 * b))


def fx_timp(t):
    return fx("timp", t)


def fx_strings(t):
    return fx("strings", t)


def fx_swell(t):
    return fx("swell", t)


def fx_brass(t):
    """Brass: its level plus a flare on each bright onset."""
    return float(min(1.0, 0.45 * fx("brass", t) + 0.8 * fx("brass_hit", t)))


def fx_choir(t):
    return fx("choir", t)


def fx_high(t):
    return fx("high", t)


def fx_low(t):
    return fx("low", t)


def fx_beat(t):
    return fx("beat", t)


def timp_hits(min_s=0.6):
    """The timpani hits [(t, strength)] (strong ones only)."""
    if _M is None:
        return []
    return [(float(a), float(s)) for a, s in zip(_M["timp_t"], _M["timp_s"]) if s >= min_s and a < LIVE]


def _reading(t):
    """1 while a phrase is on screen (most while it reads), so nothing bright crosses it."""
    v = 0.0
    for p in getattr(H, "PHRASE_LIST", []):
        ti, r0, r1, to = p[1]
        if ti - 0.4 <= t <= to + 0.4:
            v = max(v, 0.6 * _sc(ti - 0.4, ti, t) * (1.0 - _sc(to, to + 0.4, t)) + 0.4 * _sc(ti, r0, t) * (1.0 - _sc(r1, to, t)))
    return v


def room(t):
    """How much the effects may show: less under a phrase and where the music already blazes."""
    return (1.0 - 0.55 * _reading(t)) * (1.0 - 0.40 * intensity(t) ** 2)


# =========================================================================================================
# Places
# =========================================================================================================
def ground_y(x, z):
    """Height of the ground at (x, z): the sea (0) or the terrace of Mount Zion there."""
    r = np.hypot(np.asarray(x, np.float64) - ZC[0], np.asarray(z, np.float64) - ZC[2])
    k = np.clip(np.floor((tier_r(0) - r) / TIER_STEP), 0, N_TIER - 1)
    return np.where(r <= tier_r(0), SUMMIT * (k + 1) / N_TIER, 0.0)


def _ground_ahead(cam):
    """Where the camera's look meets the ground (the sea or a terrace), or a point 120 m ahead on the ground when
    it looks level or up."""
    p, q = np.asarray(cam.pos, np.float64), np.asarray(cam.target, np.float64)
    d = _unit(q - p)
    if d[1] > -0.05:
        x = p + 120.0 * _unit(_v(d[0], 0.0, d[2]))
        return _v(x[0], float(ground_y(x[0], x[2])), x[2])
    y = 0.0
    for _ in range(4):
        s = float(np.clip((p[1] - y) / -d[1], 8.0, 900.0))
        x = p + d * s
        y2 = float(ground_y(x[0], x[2]))
        if abs(y2 - y) < 1e-6 or y2 > p[1] - 0.5:
            break
        y = y2
    return _v(x[0], float(ground_y(x[0], x[2])), x[2])


# =========================================================================================================
# Bass and kick: the mist glows, the shore lights flicker, the Earth's rim breathes
# =========================================================================================================
class MistPulse:
    """Soft low glows in the mist over the sea (or over the summit square in the choir shots) that pulse with the
    bass and flicker on the kicks."""

    def __init__(self):
        r = np.random.default_rng(611)
        n = 110
        rr = 140.0 + 1300.0 * r.random(n) ** 1.3
        a = np.radians(180.0 + (r.random(n) - 0.5) * 300.0)
        self.sea = np.stack([ZC[0] + rr * np.sin(a) * 1.0, 2.0 + 5.0 * r.random(n), ZC[2] + 420.0 + rr * np.cos(a)], 1)
        far = np.hypot(self.sea[:, 0] - ZC[0], self.sea[:, 2] - ZC[2]) > tier_r(0) + 20.0
        self.sea = self.sea[far]
        self.sea_s = (24.0 + 0.05 * np.hypot(self.sea[:, 0], self.sea[:, 2] - ZC[2])) * (0.7 + 0.6 * r.random(len(self.sea)))
        m = 40
        ra = 10.0 + 70.0 * r.random(m)
        aa = 2 * np.pi * r.random(m)
        self.top = np.stack([SQUARE[0] + ra * np.sin(aa), SUMMIT + 0.8 + 1.5 * r.random(m), SQUARE[2] + ra * np.cos(aa)], 1)
        self.top_s = 7.0 + 8.0 * r.random(m)
        self.ph = r.random(max(len(self.sea), m))
        self.col = [lin("#7a5ab8"), lin("#ffb88a"), lin("#a8b8ff")]

    def sample(self, t):
        if _M is None or globe_view(t):
            return None
        k = fx_pulse(t) * room(t)
        if k <= 0.01:
            return None
        flick = 0.75 + 0.25 * np.cos(2 * np.pi * (self.ph + 3.1 * t))
        if stage_view(t):
            P, S, n = self.top, self.top_s, len(self.top)
        else:
            P, S, n = self.sea, self.sea_s, len(self.sea)
        cols = np.array([self.col[i % 3] for i in range(n)])
        return [dict(pos=P, size=S, color=cols, alpha=(0.045 * k * flick[:n]).astype(np.float32), kind="soft",
                     emit=1.4, reflect=False, dof=0.4)]


class ShoreLights:
    """A ring of small lamps on the shore round the foot of Mount Zion, and lamps along the sea's edge in
    front of it: they flicker and pulse with the bass and the kick (silver, so they read against the gold)."""

    def __init__(self):
        r = np.random.default_rng(612)
        ring = _ring(ZC, tier_r(0) + 6.0, 0.35, 3.5)
        self.P = ring
        self.seed = r.random(len(ring))
        self.col = np.where(r.random(len(ring))[:, None] < 0.7, lin(CRYSTAL)[None, :], lin("#ffe2b8")[None, :])

    def sample(self, t):
        if _M is None or globe_view(t):
            return None
        k = fx_pulse(t)
        if k <= 0.01:
            return None
        k *= (1.0 - 0.4 * _reading(t))
        fl = np.clip(k * (0.6 + 0.8 * np.abs(np.sin(7.0 * self.seed + 9.0 * t))), 0.0, 1.0)
        return [dict(pos=self.P, size=0.55, color=self.col, alpha=(0.9 * fl).astype(np.float32), kind="spark",
                     emit=2.6, seed=self.seed, twinkle=0.6),
                dict(pos=self.P[::3], size=5.0, color=self.col[::3], alpha=(0.07 * fl[::3]).astype(np.float32),
                     kind="soft", emit=1.4, reflect=False)]


class EarthPulse:
    """On the Earth: its rim breathes with the bass and a ring of light runs round it on the timpani."""
    wants_camera = True

    def sample(self, t, cam=None):
        if _M is None or not globe_view(t) or cam is None:
            return None
        k = fx_pulse(t) + 0.8 * fx_timp(t)
        k *= room(t)
        if k <= 0.01:
            return None
        c, M, R = GLOBE._view(t, cam)
        e = np.asarray(cam.pos, np.float64)
        v = _unit(e - c)
        # round 7 (review f21: no blown-out Earth): a thin cool line just outside the edge, never over the face
        rim = _sphere_ring(v, np.pi / 2 * 0.995, 700)
        return [dict(pos=c + R * 1.045 * rim, size=0.55, color=lin("#9fb4ff"), alpha=0.07 * min(k, 1.0), kind="soft",
                     emit=1.4, reflect=False, dof=0.0)]


# =========================================================================================================
# Timpani: a shockwave ring across the sea or the terraces
# =========================================================================================================
class Shockwaves:
    wants_camera = True

    def __init__(self):
        self.hits = timp_hits(0.6)
        self.ht = np.array([h[0] for h in self.hits]) if self.hits else np.zeros(0)
        self.centre = {}
        self.ang = np.linspace(0.0, 2 * np.pi, 720, endpoint=False)
        self.seed = np.random.default_rng(613).random(720)

    def _c(self, th):
        """The ring's centre, its start radius and how far it runs: from where the camera looks on the sea; from
        the foot of Mount Zion when the camera looks at the mountain; on the summit floor in the choir shots."""
        c = self.centre.get(th)
        if c is None:
            cam = H.CAMERA.state(th)
            e = np.asarray(cam.pos, np.float64)
            g = _ground_ahead(cam)
            if stage_view(th):
                g = _v(g[0], SUMMIT, g[2])
                c = (g, 0.5, min(float(np.linalg.norm(e - g)), 60.0), R_TOP)
            elif float(ground_y(g[0], g[2])) > 0.0 or (e[1] - g[1]) > 0.5 * float(np.linalg.norm(e - g)):
                c = (None, 0.0, 0.0, 0.0)           # looking at the mountain or steeply down: no ring (it would float)
            else:
                d = float(np.linalg.norm(e - g))
                c = (g, 0.04 * d, d, 1e9)
            self.centre[th] = c
        return c

    def sample(self, t, cam=None):
        if _M is None or globe_view(t) or not len(self.ht):
            return None
        quiet = 1.0 - 0.95 * _reading(t)            # never across a phrase
        if quiet <= 0.05:
            return None
        i = int(np.searchsorted(self.ht, t))
        out = []
        for j in range(max(i - 3, 0), i):
            th, s = self.hits[j]
            u = t - th
            if not (0.0 <= u < 1.6) or shot_of(th) != shot_of(t):
                continue
            c, r0, d, rmax = self._c(th)
            if c is None:
                continue
            rad = r0 + 0.75 * d * (1.0 - np.exp(-u / 0.55))
            x = c[0] + rad * np.sin(self.ang)
            z = c[2] + rad * np.cos(self.ang)
            if rmax < 1e8:                          # the summit floor: only on the plateau
                on = np.hypot(x - ZC[0], z - ZC[2]) < rmax
                y = np.full(len(x), SUMMIT + 0.15)
            else:                                   # the sea: only off the mountain
                on = np.hypot(x - ZC[0], z - ZC[2]) > tier_r(0) + 2.0
                y = np.full(len(x), 0.2 + 0.001 * d)
            if not on.any():
                continue
            P = np.stack([x, y, z], 1)[on]
            a = s * np.exp(-u / 0.5) * room(t) * quiet * (1.0 - _sc(1.2, 1.6, u))
            w = 0.18 + 0.004 * d
            out.append(dict(pos=P, size=w, color=lin("#fff0d8") * 0.6 + lin(CRYSTAL) * 0.4, alpha=0.40 * a,
                            kind="spark", emit=2.4, seed=self.seed[on], twinkle=0.3, reflect=False))
            out.append(dict(pos=P[::4], size=w * 8.0, color=lin("#c8b8ff"), alpha=0.035 * a, kind="soft", emit=1.3,
                            reflect=False))
        return out or None


# =========================================================================================================
# Strings: glitter waves rolling out from Zion across the sea (across the summit floor in the choir shots)
# =========================================================================================================
class GlitterWaves:
    wants_camera = True
    TILE = 360.0

    def __init__(self):
        r = np.random.default_rng(614)
        n = 900
        self.off = r.random((n, 2)) * self.TILE
        self.seed = r.random(n)
        k = r.random(n)
        self.col = np.where(k[:, None] < 0.5, lin(SILVER)[None, :],
                            np.where(k[:, None] < 0.8, lin(CRYSTAL)[None, :], lin(VIOLET)[None, :]))
        m = 1400
        ra = R_TOP * np.sqrt(r.random(m))
        aa = 2 * np.pi * r.random(m)
        self.top = np.stack([ZC[0] + ra * np.sin(aa), np.full(m, SUMMIT + 0.08), ZC[2] + ra * np.cos(aa)], 1)
        self.top_seed = r.random(m)
        self.top_col = np.where(r.random(m)[:, None] < 0.6, lin(SILVER)[None, :], lin(CRYSTAL)[None, :])
        self.phase = None

    def _phase(self, t):
        """The waves' travel: faster on the swells (integrated so they never jump)."""
        if self.phase is None:
            ts = np.arange(0.0, TOTAL + 1.0, 1.0 / 30.0)
            v = 0.35 + 1.4 * np.array([fx_swell(x) for x in ts]) + 0.4 * np.array([fx_strings(x) for x in ts])
            self.phase = (ts, np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) / 30.0)]))
        return float(np.interp(t, *self.phase))

    def sample(self, t, cam=None):
        if _M is None or globe_view(t) or cam is None:
            return None
        k = fx_strings(t) * (0.35 + 0.65 * min(1.0, fx_strings(t) + fx_swell(t))) * room(t)
        if k <= 0.02:
            return None
        ph = self._phase(t)
        lam = 22.0
        if stage_view(t):
            P, sd, col = self.top, self.top_seed, self.top_col
            r = np.hypot(P[:, 0] - ZC[0], P[:, 2] - ZC[2]) * 3.0
            size = 0.10
        else:
            e = np.asarray(cam.pos, np.float64)
            g = _ground_ahead(cam)
            cx = 0.5 * (e[0] + g[0])
            cz = 0.5 * (e[2] + g[2])
            T = self.TILE
            i0, j0 = int(np.floor(cx / T)), int(np.floor(cz / T))
            pts, sds, cols = [], [], []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    q = np.stack([(i0 + di) * T + self.off[:, 0], (j0 + dj) * T + self.off[:, 1]], 1)
                    pts.append(q)
                    sds.append(self.seed)
                    cols.append(self.col)
            q, sd, col = np.concatenate(pts), np.concatenate(sds), np.concatenate(cols)
            keep = np.hypot(q[:, 0] - ZC[0], q[:, 1] - ZC[2]) > tier_r(0) + 10.0
            q, sd, col = q[keep], sd[keep], col[keep]
            P = np.stack([q[:, 0], np.full(len(q), 0.14), q[:, 1]], 1)
            r = np.hypot(q[:, 0] - ZC[0], q[:, 1] - ZC[2])
            dist = np.linalg.norm(P - e[None, :], axis=1)
            size = 0.10 + 0.0022 * dist
        w = 0.5 + 0.5 * np.cos(2 * np.pi * (r / lam - ph))
        w = w ** 6 * (0.6 + 0.4 * np.cos(2 * np.pi * (r / (5.3 * lam) - 0.37 * ph)))
        a = np.clip(1.4 * k * w, 0.0, 1.0)
        on = a > 0.02
        if not on.any():
            return None
        return [dict(pos=P[on], size=size if np.ndim(size) == 0 else size[on], color=col[on],
                     alpha=a[on].astype(np.float32), kind="spark", emit=2.4, seed=sd[on], twinkle=0.8, reflect=False)]


# =========================================================================================================
# Brass: the strongest ray source flares, the comets' heads flare
# =========================================================================================================
_FLARE = {"busy": False}


def _best_other_ray(t):
    best, bk = None, 0.0
    for R in RAY_SOURCES:
        if R.get("music_fx"):
            continue
        k = float(_val_at(R["strength"], t))
        if k > bk:
            best, bk = R, k
    return best, bk


def _flare_strength(t):
    if _M is None or _FLARE["busy"]:
        return 0.0
    _FLARE["busy"] = True
    try:
        R, k = _best_other_ray(t)
    finally:
        _FLARE["busy"] = False
    if R is None or k <= 0.0:
        return 0.0
    return k * (1.0 + (0.32 * fx_brass(t)) * (1.0 - 0.6 * _reading(t)) * (1.0 - 0.5 * intensity(t)))


def _flare_pos(t):
    R, _ = _best_other_ray(t)
    return np.asarray(_val_at(R["pos"], t), np.float64) if R else np.array([0.0, -1000.0, 0.0])


def _flare_col(t):
    R, _ = _best_other_ray(t)
    return _val_at(R["color"], t) if R else "#fff1d8"


class CometFlares:
    """A bright flare on each comet's head on the brass (the comets other threads fly)."""

    def __init__(self, comets):
        self.c = comets

    def sample(self, t):
        if _M is None or local_k(t) <= 0.0 or not self.c:
            return None
        b = fx_brass(t) * room(t)
        if b <= 0.03:
            return None
        P, S, C, A = [], [], [], []
        for cm in self.c:
            k = cm.k(t)
            if k <= 0.0:
                continue
            P.append(np.asarray(cm.head(t), np.float64))
            S.append(cm.width)
            C.append(lin(cm.color) if isinstance(cm.color, str) else np.asarray(cm.color, np.float64))
            A.append(k)
        if not P:
            return None
        P, S, C, A = np.array(P), np.array(S), np.array(C), np.array(A)
        return [dict(pos=P, size=S * 9.0, color=C * 0.6 + lin(WHITE) * 0.4, alpha=(0.40 * b * A).astype(np.float32),
                     kind="soft", emit=2.6, dof=0.4),
                dict(pos=P, size=S * 2.0, color=lin(WHITE), alpha=(0.9 * b * A).astype(np.float32), kind="spark",
                     emit=5.0, dof=0.4)]


# =========================================================================================================
# High voices: sparkles high in the sky (the stars and constellations brighten in add below)
# =========================================================================================================
class HighSparkles:
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(615)
        n = 240
        az = 2 * np.pi * r.random(n)
        el = np.radians(24.0 + 50.0 * r.random(n) ** 0.8)
        self.dir = np.stack([np.cos(el) * np.sin(az), np.sin(el), np.cos(el) * np.cos(az)], 1)
        self.seed = r.random(n)
        k = r.random(n)
        self.col = np.where(k[:, None] < 0.45, lin(WHITE)[None, :],
                            np.where(k[:, None] < 0.75, lin(CRYSTAL)[None, :],
                                     np.asarray([lin(COL9[i]) for i in r.integers(0, 9, n)]) * 0.5 + lin(WHITE) * 0.5))
        self.size = 7.0 + 9.0 * r.random(n)

    def sample(self, t, cam=None):
        if _M is None or cam is None:
            return None
        h = fx_high(t) * (1.0 - 0.75 * _reading(t))
        if h <= 0.03:
            return None
        e = np.asarray(cam.pos, np.float64)
        P = e[None, :] + 3000.0 * self.dir
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * (self.seed * 7.0 + (0.8 + 1.6 * self.seed) * t))
        a = np.clip(h * (0.25 + 0.75 * tw ** 3), 0.0, 1.0)
        return [dict(pos=P, size=self.size, color=self.col, alpha=(0.85 * a).astype(np.float32), kind="spark",
                     emit=2.8, seed=self.seed, twinkle=0.9, dof=0.0, reflect=False)]


# =========================================================================================================
# Low voices: a low warm glow at the base of Zion and on the ground
# =========================================================================================================
class LowGlow:
    def __init__(self):
        self.base = _ring(ZC, tier_r(0) - 4.0, 4.0, 22.0)
        r = np.random.default_rng(616)
        m = 18
        x = np.linspace(-34.0, 34.0, m)
        self.floor = np.stack([SQUARE[0] + x, np.full(m, SUMMIT + 0.6), SQUARE[2] + 4.0 + 6.0 * r.random(m)], 1)

    wants_camera = True

    def sample(self, t, cam=None):
        if _M is None or globe_view(t) or cam is None:
            return None
        k = fx_low(t) * room(t)
        if k <= 0.02:
            return None
        col = lin("#ffb070")
        if stage_view(t):
            return [dict(pos=self.floor, size=9.0, color=col, alpha=0.05 * k, kind="soft", emit=1.5, reflect=False)]
        # a warm pool on the ground in the lower part of the picture, wherever the camera is
        e = np.asarray(cam.pos, np.float64)
        g = _ground_ahead(cam)
        foot = _v(e[0], float(ground_y(e[0], e[2])), e[2])
        p = foot + 0.55 * (g - foot)
        p[1] = float(ground_y(p[0], p[2])) + 0.3
        d = float(np.linalg.norm(p - e))
        pool = np.array([p, p + 0.25 * d * _unit(_v(1.0, 0.0, 0.3)), p - 0.25 * d * _unit(_v(1.0, 0.0, 0.3))])
        return [dict(pos=self.base, size=38.0, color=col, alpha=0.05 * k, kind="soft", emit=1.5, reflect=False),
                dict(pos=self.base[::2] + _v(0.0, -3.5, 0.0), size=60.0, color=lin("#ff9a6a"), alpha=0.03 * k,
                     kind="soft", emit=1.3, reflect=False),
                dict(pos=pool, size=np.array([0.55, 0.4, 0.4]) * d, color=col, alpha=0.035 * k, kind="soft", emit=1.4,
                     reflect=False, dof=0.3)]


# =========================================================================================================
CITY_SETS = ("city dim", "city gold", "zion dim", "zion gold", "zion gardens", "zion towers", "zion gates", "paths")


def _wrap_gain(scene, name, f):
    """Lets the music lift a set another part of the film placed (its own gain is kept and multiplied)."""
    try:
        ps = scene.get(name)
    except KeyError:
        return
    g0 = ps.gain if hasattr(ps, "gain") else (lambda t: 1.0)
    ps.gain = lambda t, g0=g0: float(g0(t)) * f(t)


# =========================================================================================================
# Round 8 (Anthony: "there needs to be way more effects consistently happening to match each different sound in
# the song"): a layer that rides with the camera, so every sound answers visibly in every kind of shot (stage,
# Zion, procession, Earth, sky, church), not only where the world effects above happen to be in view. Kept to
# the frame's edges and lower band, out of every phrase's region (keep_out_of_words, and the calm boxes), held
# down where the music already blazes (room) so nothing whites out.
#   bass and kick   a row of soft lights along the bottom of the frame pulses; sparks flick on each kick
#   timpani         a ring of sparks opens in the lower frame on each hit (left and right in turn)
#   strings         three streams of fine glitter flow across the lower frame, faster on the swells
#   brass           rays burst from the upper corners on each brass onset
#   high voices     sparkles twinkle across the top of the frame
#   low voices      a warm low glow rises from the bottom corners
#   choir           (the core's exposure) the whole picture swells a little with the choir
# =========================================================================================================
class CameraMusic:
    wants_camera = True
    D = 70.0                                   # metres ahead: behind the words (30 m), in front of the world

    def __init__(self):
        r = np.random.default_rng(808)
        self.h = r.random((900, 4))
        self.hits = timp_hits(0.45)
        self.ht = np.array([h[0] for h in self.hits]) if self.hits else np.zeros(0)
        self.bo = []                       # brass onsets
        if _M is not None and "brass_hit" in _M:
            b = _M["brass_hit"]
            on = np.where((b[1:-1] > 0.45) & (b[1:-1] >= b[:-2]) & (b[1:-1] > b[2:]))[0] + 1
            last = -9.0
            for i in on:
                if _T[i] - last > 0.35 and _T[i] < LIVE:
                    self.bo.append(float(_T[i]))
                    last = _T[i]
        self.bo = np.array(self.bo)
        self.col9 = np.array([lin(c) for c in COL9])

    def _pts(self, cam, x, y, d=None):
        d = self.D if d is None else d
        r, u, f = (np.asarray(v, np.float64) for v in cam.basis())
        half = np.tan(np.radians(cam.fov) * 0.5) * d
        x, y = np.asarray(x, np.float64), np.asarray(y, np.float64)
        return (np.asarray(cam.pos, np.float64)[None, :] + f[None, :] * d
                + r[None, :] * ((x - 0.5) * 2.0 * half * cam.aspect)[:, None] + u[None, :] * ((y - 0.5) * 2.0 * half)[:, None])

    def _unit(self, cam, d=None):
        d = self.D if d is None else d
        return 2.0 * np.tan(np.radians(cam.fov) * 0.5) * d          # metres per frame height

    def sample(self, t, cam=None):
        if _M is None or cam is None or t > LIVE:
            return None
        room_k = room(t)
        if room_k <= 0.02:
            return None
        U = self._unit(cam)
        h = self.h
        out = []
        # bass and kick: a row of soft lights along the bottom, sparks on the kicks
        k = fx_pulse(t)
        if k > 0.02:
            n = 26
            x = (np.arange(n) + 0.5) / n
            y = 0.035 + 0.02 * np.sin(np.pi * x)
            c = self.col9[(np.arange(n) + int(t * 0.5)) % 9] * 0.6 + lin(WHITE) * 0.4
            out.append(dict(pos=self._pts(cam, x, y), size=np.full(n, 0.07 * U), color=c,
                            alpha=np.full(n, 0.11 * k * room_k), kind="soft", emit=1.6))
            kk = fx_kick(t)
            if kk > 0.05:
                m = 120
                xs, ys = h[:m, 0], 0.01 + 0.10 * h[:m, 1] ** 2
                out.append(dict(pos=self._pts(cam, xs, ys), size=0.0045 * U * (0.6 + h[:m, 2]),
                                color=lin("#fff0d8"), alpha=(0.9 * kk * room_k * (h[:m, 3] < 0.6 + 0.4 * kk)),
                                kind="spark", emit=2.6, twinkle=0.6, seed=h[:m, 3]))
        # timpani: a ring of sparks opening in the lower frame
        if len(self.ht):
            i = int(np.searchsorted(self.ht, t)) - 1
            if i >= 0 and t - self.ht[i] < 1.3:
                u_ = t - self.ht[i]
                s_ = self.hits[i][1]
                cx = 0.28 if i % 2 == 0 else 0.72
                hh = h[:220]
                ang = 2 * np.pi * hh[:, 0]
                # a burst of sparks thrown outward, not a drawn ring: each its own speed, a little gravity
                rad = (0.02 + (0.16 + 0.14 * hh[:, 1]) * (1.0 - np.exp(-u_ / 0.32)))
                xs = cx + rad * np.cos(ang) / cam.aspect
                ys = 0.20 + 0.75 * rad * np.sin(ang) - 0.05 * u_ * u_
                a = s_ * np.exp(-u_ / 0.45) * room_k
                vis = (ys > -0.02).astype(np.float64)
                col = self.col9[i % 9] * 0.5 + lin(WHITE) * 0.5
                out.append(dict(pos=self._pts(cam, xs, ys), size=0.004 * U * (0.6 + hh[:, 2]), color=col,
                                alpha=0.95 * a * vis, kind="spark", emit=2.8, twinkle=0.5, seed=hh[:, 3]))
                out.append(dict(pos=self._pts(cam, xs[::6], ys[::6]), size=np.full(len(ang[::6]), 0.03 * U),
                                color=col, alpha=0.05 * a * vis[::6], kind="soft", emit=1.4))
        # strings: three streams of glitter flowing across the lower frame
        st = fx_strings(t)
        if st > 0.04:
            sw = fx_swell(t)
            m = 300
            out_p, out_a, out_c = [], [], []
            for j in range(3):
                hh = h[j * m:(j + 1) * m]
                ph = np.mod(hh[:, 0] + t * (0.035 + 0.06 * sw) * (1 if j % 2 == 0 else -1), 1.0)
                xs = ph * 1.2 - 0.1
                ys = 0.12 + 0.07 * j + 0.035 * np.sin(2 * np.pi * (ph * 1.3 + 0.21 * t + j * 0.33)) + 0.012 * (hh[:, 1] - 0.5)
                out_p.append(self._pts(cam, xs, ys))
                out_a.append(st * room_k * (0.4 + 0.6 * hh[:, 2]) * np.sin(np.pi * np.clip(ph, 0, 1)))
                out_c.append(np.repeat((lin(CRYSTAL) * 0.6 + self.col9[(2 + 3 * j) % 9] * 0.4)[None, :], m, 0))
            out.append(dict(pos=np.concatenate(out_p), size=0.0042 * U * (0.6 + h[:3 * m, 3]),
                            color=np.concatenate(out_c), alpha=0.95 * np.concatenate(out_a), kind="spark", emit=2.6,
                            twinkle=0.5, seed=h[:3 * m, 3]))
        # brass: rays burst from the upper corners
        if len(self.bo):
            i = int(np.searchsorted(self.bo, t)) - 1
            if i >= 0 and t - self.bo[i] < 0.9:
                u_ = t - self.bo[i]
                a = np.exp(-u_ / 0.3) * min(1.0, 0.5 + fx_brass(self.bo[i])) * room_k
                pts, al = [], []
                for side in (0.0, 1.0):
                    for j in range(6):
                        ang = np.radians(-18.0 - 11.0 * j)
                        dx = np.cos(ang) * (1 if side == 0.0 else -1) / cam.aspect
                        dy = np.sin(ang)
                        q = np.linspace(0.0, 0.25 + 0.35 * (1.0 - np.exp(-u_ / 0.12)), 40)
                        pts.append(np.stack([side + dx * q, 1.0 + dy * q], 1))
                        al.append((1.0 - q / q[-1]) ** 1.5)
                P2 = np.concatenate(pts)
                out.append(dict(pos=self._pts(cam, P2[:, 0], P2[:, 1]), size=np.full(len(P2), 0.010 * U),
                                color=lin("#ffd9a0"), alpha=0.45 * a * np.concatenate(al), kind="soft", emit=2.0))
        # high voices: sparkles across the top of the frame
        hi = fx_high(t)
        if hi > 0.05:
            m = 160
            hh = h[400:400 + m]
            tw = 0.5 + 0.5 * np.sin(2 * np.pi * (hh[:, 2] * 3.0 + 1.7 * t))
            out.append(dict(pos=self._pts(cam, hh[:, 0], 0.86 + 0.13 * hh[:, 1]), size=0.0045 * U * (0.6 + hh[:, 3]),
                            color=lin("#f4f0ff"), alpha=1.0 * hi * room_k * tw, kind="spark", emit=2.6, twinkle=0.8,
                            seed=hh[:, 3]))
        # low voices: a warm low glow rising from the bottom corners
        lo = fx_low(t)
        if lo > 0.05:
            xs, ys = np.array([0.06, 0.16, 0.84, 0.94]), np.array([0.05, 0.02, 0.02, 0.05])
            out.append(dict(pos=self._pts(cam, xs, ys), size=np.full(4, 0.16 * U), color=lin("#ffb070"),
                            alpha=np.full(4, 0.06 * lo * room_k), kind="soft", emit=1.3))
        if not out:
            return None
        for b in out:            # never across a phrase
            m_ = H.keep_out_of_words(t, b["pos"])
            if m_ is not None:
                b["alpha"] = np.asarray(b["alpha"], np.float64) * m_
            b["alpha"] = np.asarray(b["alpha"], np.float32)
            b.update(reflect=False, dof=0.0, fog=0.0, streak=0.0)
        return out


def choir_swell(t):
    """The whole picture swells a little with the choir (the core multiplies its exposure by this)."""
    if _M is None:
        return 1.0
    return 1.0 + 0.08 * fx_choir(t) * (1.0 - 0.6 * intensity(t)) * (1.0 - 0.5 * _reading(t))


def add(scene):
    if _M is None:
        return
    # bass and kick: the sea's glitter, the floating lights and the dust lights in the air pulse and flicker
    _wrap_gain(scene, "sea glitter", lambda t: 1.0 + 0.9 * fx_pulse(t) * (1.0 - 0.4 * _reading(t)))
    _wrap_gain(scene, "_floats", lambda t: 1.0 + 0.8 * fx_pulse(t))
    _wrap_gain(scene, "_dust", lambda t: 1.0 + 0.45 * fx_pulse(t))
    # bass and kick: the city's lights flicker (a breath brighter on each kick; never a flash of gold)
    for name in CITY_SETS:
        _wrap_gain(scene, name, lambda t: 1.0 + 0.38 * fx_pulse(t) * (1.0 - 0.5 * _reading(t)) * (1.0 - 0.5 * intensity(t)))
    # high voices: the constellations and the stars brighten
    _wrap_gain(scene, "constellations", lambda t: 1.0 + 0.8 * fx_high(t) * (1.0 - 0.5 * _reading(t)))
    _wrap_gain(scene, "_stars", lambda t: 1.0 + 0.5 * fx_high(t))
    comets = [e.pointset for e in scene.entries() if isinstance(e.pointset, Comet) and e.pointset.width < 4.0]
    scene.add("music mist", MistPulse(), reflect=False)
    scene.add("music shore lights", ShoreLights())
    scene.add("music earth rim", EarthPulse(), reflect=False)
    scene.add("music timpani", Shockwaves(), reflect=False)
    scene.add("music strings", GlitterWaves(), reflect=False)
    scene.add("music comet flares", CometFlares(comets))
    scene.add("music high voices", HighSparkles(), reflect=False, fog=False)
    scene.add("music low voices", LowGlow(), reflect=False)
    scene.add("music in frame", CameraMusic(), reflect=False, depth_of_field=False, fog=False)
    add_rays(_flare_pos, _flare_strength, color=_flare_col)
    RAY_SOURCES[-1]["music_fx"] = True
