"""Song 09, Let's Save the World (concert item 10, piano solo): the full-length concert backdrop, version 2.

The music part is exactly the live length, 4:36 (276.0 s; the church's "Soloist" reference is 275.74 s, within
1 s, so its section times are used as they are), then a 15 second calm hold: 291.0 s, 17460 frames at 60 fps.
The approved Revision 3 craft (warm gold glitter people, cream Cormorant serif with a coloured capsule label,
warm heavenly light, smooth eased motion) on song 09's own look: a misty sea dawn at Galilee where one warm word
at a time calms the water. The nine coloured comets belong to song 01 only and are not used here.

Design: project-docs/designs/09 Let's Save the World.md. Timeline: project-docs/backdrops/s09-full2/TIMELINE.md.
Everything here is a pure function of song time t in seconds (0 is the first sample of the recording).
Loaded by tools/s09_full2/render.py as songs.s09_full2 over the pinned Film 10 engine (commit d928ff9) and
Claude Final v1's words, bodies and crowds (commit f43f451), exactly as the approved Revision 3 does.
No em dash or en dash anywhere in this file.
"""
import numpy as np

import songs.s03_original as _base

MUSIC_END = 276.0           # the live length (4:36); the reference (275.736 s) is within 1 s, used as is
HOLD = 15.0                 # the calm hold after the music
TOTAL = 291.0               # 17460 frames at 60 fps
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 272.0
_base.SONG_END = MUSIC_END
MUSIC_END = 272.0   # (the engine name: where the last notes fade; SONG_END is the live length)
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import reference  # noqa: E402,F401   (registers nine_reference_p3d: Claude Final v1)
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.api import ribbon  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402
from nine_reference_p3d import words as PW  # noqa: E402

TOTAL = 291.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 272.0
SONG_END = 276.0
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------------------
# The music (measured on the recording; TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
SEC = dict(intro=0.0, call=47.0, sand=71.0, chorus1=108.0, interlude=133.0, verse2=150.0, enc=175.5,
           glory=189.0, joy=200.0, chorus2=214.0, pause=228.0, final=230.0, peak=242.0, outro=246.0,
           quiet=260.0, end=MUSIC_END)
ACCENTS = [43.9, 59.5, 73.5, 93.6, 99.2, 111.2, 129.0, 148.8, 156.3, 184.9, 191.3, 202.0, 222.8, 230.9,
           239.4, 242.0, 244.1, 246.2]

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
GOLD, GOLD2 = "#f6a838", "#ffd890"
LAMP = "#ffc27a"


def _ss(a, b, x):
    if b <= a:
        return float(np.asarray(x) >= a)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(t, a, b, c, d):
    """0 before a, rising to 1 at b, 1 until c, falling to 0 at d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _onsets():
    """The piano's notes (engine/analyze.py onsets) with their strength, for the beads of light."""
    try:
        d = np.load(FEATURES)
        times, env = d["times"], d["onset"]
        on = np.asarray(d["onsets"], np.float64)
        s = np.interp(on, times, env / max(float(env.max()), 1e-9))
        return on, s
    except Exception:
        return np.array(ACCENTS), np.ones(len(ACCENTS))


ONSETS, ONSET_S = _onsets()

# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0, the camera looks toward -z where the sun rises)
# ---------------------------------------------------------------------------------------------------------
BOATS = [_v(-7.0, 0.0, 0.0), _v(10.0, 0.0, -16.0), _v(-24.0, 0.0, -34.0)]
SHORE_Z = -14.0             # the sand bar of light where the called people stand
MOTHER1 = _v(0.0, 0.0, -13.0)
MOTHER2 = _v(0.0, 0.0, -14.0)
SAINT_Z = -40.0
PAIR = _v(1.2, 0.0, 5.0)    # the Encouragement pair on the near shore
ARCH = dict(span=380.0, height=80.0, z=-340.0)


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


# the camera: calm, slow, eased between resting places (performers stand in front of the screen)
CAM_KEYS = [                         # target heights put the horizon near 0.40 of the frame (song 09 look)
    (0.0, _v(0.0, 2.2, 52.0), _v(0.0, -6.0, -120.0)),
    (42.0, _v(0.4, 1.9, 34.0), _v(-2.0, -7.0, -120.0)),
    (54.0, _v(-1.5, 2.6, 19.0), _v(-6.0, 1.4, -2.0)),
    (66.0, _v(-2.5, 2.4, 17.0), _v(-5.0, -8.0, -100.0)),
    (80.0, _v(0.0, 8.0, 28.0), _v(0.0, -1.5, -40.0)),
    (100.0, _v(0.0, 11.0, 30.0), _v(0.0, -1.0, -40.0)),
    (112.0, _v(0.9, 2.8, 5.0), _v(0.0, -6.5, -120.0)),
    (130.0, _v(0.6, 2.8, 2.5), _v(0.0, -6.5, -120.0)),
    (148.0, _v(-3.0, 2.4, 4.0), _v(-1.0, -4.0, -80.0)),
    (168.0, _v(2.5, 2.6, 2.0), _v(1.0, -4.2, -80.0)),
    (176.0, _v(1.45, 1.95, 12.6), _v(1.2, 0.95, -30.0)),     # the Encouragement: eye just above the pair's
    (186.0, _v(1.45, 1.93, 12.4), _v(1.2, 0.97, -30.0)),     # heads, so they stand clearly below the words
    (192.0, _v(1.5, 1.5, 15.5), _v(1.2, 1.6, -30.0)),
    (200.0, _v(0.0, 3.0, 24.0), _v(0.0, -2.0, -120.0)),
    (214.0, _v(0.0, 3.0, 20.0), _v(0.0, -7.0, -120.0)),
    (228.0, _v(0.0, 3.4, 12.0), _v(0.0, -6.5, -120.0)),
    (246.0, _v(0.0, 4.6, 30.0), _v(0.0, -6.0, -120.0)),
    (TOTAL, _v(0.0, 5.0, 34.0), _v(0.0, -6.0, -120.0)),
]


def _cam_path(t):
    ks = CAM_KEYS
    if t <= ks[0][0]:
        return ks[0][1], ks[0][2]
    for (t0, p0, q0), (t1, p1, q1) in zip(ks[:-1], ks[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            u = u * u * u * (u * (6.0 * u - 15.0) + 10.0)
            return p0 * (1 - u) + p1 * u, q0 * (1 - u) + q1 * u
    return ks[-1][1], ks[-1][2]


FOV = 42.0
CAMERA = Rig([Path(_cam_path, 0.0, TOTAL, blend=0.0, fov=FOV, aperture=0.004, focus=40.0)],
             blend=0.0, fov=FOV, aperture=0.004, handheld=0.03, min_height=0.4)
_LAYOUT = CAMERA

# ---------------------------------------------------------------------------------------------------------
# The words: one expression and short fragments the design names, cream serif, upper middle of the frame
# ---------------------------------------------------------------------------------------------------------
RIDE_Y = 0.655             # centre of the text block from the BOTTOM (0.345 from the top)
DEPTH = 7.0


def _width(frac):
    return float(2.0 * DEPTH * np.tan(np.radians(FOV) * 0.5) * (16.0 / 9.0) * frac)


def _star7(t):
    return np.asarray(_arch_geo().positions(t)[ENC], np.float64)


_ARCH_GEO = []


def _arch_geo():
    if not _ARCH_GEO:
        from p3d.world import Arch
        _ARCH_GEO.append(Arch(None, span=ARCH["span"], height=ARCH["height"], z=ARCH["z"]))
    return _ARCH_GEO[0]


_FRAG = dict(ride=(0.5, RIDE_Y, DEPTH), face="screen", label="", nib=False, font="tag", tint=0.30, bright=0.95,
             halo=1.2)
# on a bright sky the words are navy with a soft white glow (DESIGN-SYSTEM 7); on a night sky warm white and gold
# each fragment has its own effect, grown from the song's imagery (design section 8)
WORD_SPECS = [
    # 1. "God called us": written in one continuous line of handwriting by the thread of the lifted grain
    dict(_FRAG, name="called", lines=["God called us"], width=_width(0.36), arrive="pen", leave="fade",
         t_in=80.5, t_read0=82.5, t_read1=82.9, t_out=83.9),
    # 2. "hope for all humankind": the called people's small lights gather into the words (navy on the dawn)
    dict(_FRAG, name="hope", lines=["hope for all humankind"], width=_width(0.50), arrive="gather",
         leave="fade", t_in=112.5, t_read0=115.5, t_read1=115.9, t_out=116.9),
    # 3. "hardships as honor": the forge, sparks stitch the letters, which glow from ember red to gold
    dict(_FRAG, name="honor", lines=["hardships as honor"], width=_width(0.46), arrive="stitch", leave="fade",
         color="#ffb060", glow="#ff6a2a", tint=0.85, t_in=155.0, t_read0=157.5, t_read1=157.9, t_out=158.9),
    # the expression: cream serif, violet capsule label; its words collapse into star 7 of the arch
    dict(expr="Encouragement", ride=(0.5, RIDE_Y - 0.01, DEPTH), face="screen", width=_width(0.50), pill=True,
         arrive="gather", leave="arch", to=lambda t: _star7(t), tint=0.12, bright=0.95, halo=1.1,
         t_in=176.0, t_read0=178.5, t_read1=187.5, t_out=190.0),
    # 4. "Let's save the world": the net of light weaves the words across the sky (navy on the morning)
    dict(_FRAG, name="save", lines=["Let’s save the world"], width=_width(0.50), arrive="weave",
         leave="fade", t_in=230.0, t_read0=232.5, t_read1=232.9, t_out=233.9),
]
ENC_READ = (178.5, 187.5)

# On the bright dawn and morning skies the fragments read in navy with a soft white glow (DESIGN-SYSTEM 7):
# each fragment's own effect forms the words in light, and as it settles crisp navy letters take its place
# exactly (drawn by cards09.py over the finished picture) for the reading, then fade.
FRAG_TEXT = {"called": "God called us", "hope": "hope for all humankind", "honor": "hardships as honor",
             "save": "Let\u2019s save the world"}
FRAG_READ = {"called": (82.5, 91.5), "hope": (115.5, 124.5), "honor": (157.5, 165.5), "save": (232.5, 241.5)}
FRAG_GLOW = {"honor": (255, 168, 96)}      # the forge: navy letters still glowing ember gold round their edges
_FRAG_BOX = {}


def frag_box(name):
    if name not in _FRAG_BOX:
        w = [x for x in WORDS if x.name == name][0]
        t = FRAG_READ[name][0]
        _FRAG_BOX[name] = PW.screen_box(w, CAMERA.state(t), t)[:4]
    return _FRAG_BOX[name]


def frag_alpha(name, t):
    r0, r1 = FRAG_READ[name]
    return float(_ss(r0 - 0.5, r0 + 0.3, t) * (1.0 - _ss(r1, r1 + 1.2, t)))


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


WORDS = PW.Words(WORD_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)


def reading_boxes(t, cam):
    out = []
    for name, (r0, r1) in FRAG_READ.items():
        if r0 - 0.5 <= t <= r1 + 1.2:
            x0, x1, y0, y1 = frag_box(name)
            out.append((x0 - 0.03, x1 + 0.03, y0 - 0.05, y1 + 0.05))
    for w in WORDS:
        if w.t_in <= t <= w.t_out:
            x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            if front:
                out.append((x0 - 0.03, x1 + 0.03, y0 - 0.05, y1 + 0.05))
    return out


# the signature's corner (top left), kept clear of every person, word and burst (screen units, y up)
SIG_BOX = (0.0, 0.40, 0.80, 1.0)


class Clear:
    """Nothing crosses a word: points inside a reading box are dimmed to almost nothing."""
    wants_camera = True

    def __init__(self, inner, bottom=True, sig=True):
        self.inner = inner
        self.sig = sig
        self.bottom = bottom      # keep the lower third calm: no bright rings or particles there
        self.static = getattr(inner, "static", False)

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = reading_boxes(t, cam) + ([SIG_BOX] if self.sig else [])
        out = []
        for src in got if isinstance(got, (list, tuple)) else [got]:
            if src is None:
                continue
            b = dict(src)
            p = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            xy, z = cam.project(p)
            g = np.ones(len(p))
            if self.bottom:
                g = g * (0.05 + 0.95 * _ss(0.34, 0.44, xy[:, 1]))
            for x0, x1, y0, y1 in boxes:
                dx = np.minimum(xy[:, 0] - x0, x1 - xy[:, 0])
                dy = np.minimum(xy[:, 1] - y0, y1 - xy[:, 1])
                f = np.clip(np.minimum(dx, dy) / 0.02 + 0.5, 0, 1)
                g = np.minimum(g, 1 - 0.98 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1.0)) * g
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * g
            out.append(b)
        return out


# ---------------------------------------------------------------------------------------------------------
# Point sets of the world of song 09
# ---------------------------------------------------------------------------------------------------------
def _boat_rock(k, t, calm):
    a = (1.0 - calm) * 0.045 + 0.012
    return a * np.sin(0.9 * t + 1.7 * k), 0.06 * (1.0 - calm) * np.sin(1.3 * t + k)


def _calm(t):
    """0 restless water, 1 a mirror: the peace of the song grows."""
    return float(0.15 + 0.55 * _sc(108.0, 120.0, t) - 0.55 * _sc(133.0, 145.0, t) + 0.45 * _sc(180.0, 190.0, t)
                 + 0.4 * _sc(214.0, 246.0, t))


class Boats:
    """Three small fishing boats drawn in thin lines of warm light, each with a hanging lantern."""

    def __init__(self):
        r = np.random.default_rng(91)
        u = np.linspace(-1.0, 1.0, 120)
        hull = []
        for lvl, (half, depth) in enumerate(((2.3, 0.45), (2.0, 0.3), (1.6, 0.15))):
            x = u * half
            y = 0.55 - depth * (1.0 - u ** 2) + 0.18 * u ** 4
            hull.append(np.stack([x, y, 0.45 * (1 - lvl * 0.3) * np.sqrt(1 - u ** 2)], 1))
            hull.append(np.stack([x, y, -0.45 * (1 - lvl * 0.3) * np.sqrt(1 - u ** 2)], 1))
        mast = np.stack([np.full(40, 0.8), np.linspace(0.5, 2.4, 40), np.zeros(40)], 1)
        arm = np.stack([np.linspace(0.8, 1.6, 20), np.full(20, 2.35), np.zeros(20)], 1)
        self.shape = np.concatenate(hull + [mast, arm])
        self.seed = r.random(len(self.shape))
        self.lamp = _v(1.6, 1.95, 0.0)

    def place(self, k, t):
        roll, bob = _boat_rock(k, t, _calm(t))
        # in the morning the boats lie farther out, above the calm lower third
        c = BOATS[k] + _v(0.6 * np.sin(0.05 * t + k), bob, -14.0 * _sc(200.0, 215.0, t))
        return c, roll

    def _xf(self, k, t, p):
        c, roll = self.place(k, t)
        yaw = np.radians(25.0 + 40.0 * k)
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        y2 = y * np.cos(roll) + z * np.sin(roll)
        z2 = -y * np.sin(roll) + z * np.cos(roll)
        return c + np.stack([x * np.cos(yaw) + z2 * np.sin(yaw), y2, -x * np.sin(yaw) + z2 * np.cos(yaw)], 1)

    def lamp_at(self, k, t):
        return self._xf(k, t, self.lamp[None, :])[0]

    def alpha(self, t):
        return 1.0 - _win(t, 136.0, 142.0, 208.0, 216.0)

    def sample(self, t):
        a = self.alpha(t)
        if a <= 0.01:
            return None
        out = []
        for k in range(3):
            p = self._xf(k, t, self.shape)
            out.append(dict(pos=p, size=0.035, color=lin("#ffd9a0"), alpha=0.55 * a, emit=1.4, kind="spark",
                            twinkle=0.4, seed=self.seed))
            lp = self.lamp_at(k, t)
            fl = 0.9 + 0.1 * np.sin(t * 6.1 + k)
            out.append(dict(pos=lp[None], size=0.16, color=lin(LAMP), alpha=a * fl, emit=4.0, kind="spark"))
            out.append(dict(pos=lp[None], size=2.2, color=lin(LAMP), alpha=0.22 * a * fl, kind="soft"))
        return out


class Beads:
    """Each piano note drops a bead of light onto the water and a warm ring spreads from it; where the ring
    passes the water is comforted. Main accents ring wider and gold."""
    wants_camera = False

    def __init__(self):
        r = np.random.default_rng(7)
        keep = []
        last = -9.0
        for tt, s in zip(ONSETS, ONSET_S):
            if tt - last >= 0.55 and s > 0.18 and tt < MUSIC_END - 1.0:
                keep.append((tt, s))
                last = tt
        self.t = np.array([k[0] for k in keep] + list(np.arange(MUSIC_END + 2.0, TOTAL, 6.0)))
        self.s = np.array([k[1] for k in keep] + [0.5] * (len(self.t) - len(keep)))
        n = len(self.t)
        self.big = np.zeros(n, bool)
        for a in ACCENTS:
            i = int(np.argmin(np.abs(self.t - a)))
            if abs(self.t[i] - a) < 0.35:
                self.big[i] = True
        ang = r.uniform(-0.55, 0.55, n)
        dist = r.uniform(18.0, 70.0, n)
        self.x = np.sin(ang) * dist
        self.z = 14.0 - np.cos(ang) * dist
        self.x[self.big] *= 0.4
        self.z[self.big] = r.uniform(-60.0, -30.0, int(self.big.sum()))
        self.ring = np.linspace(0.0, 2 * np.pi, 160, endpoint=False)
        self.rs = r.random(160)

    def sample(self, t):
        i0 = np.searchsorted(self.t, t - 7.0)
        i1 = np.searchsorted(self.t, t)
        night = _win(t, 136.0, 141.0, 168.0, 176.0)
        out = []
        for i in range(i0, i1):
            age = t - self.t[i]
            big = self.big[i]
            life = 6.5 if big else 3.5
            if age > life:
                continue
            gain = (1.0 - age / life) ** 1.6 * (0.35 + 0.65 * self.s[i]) * (1.0 - 0.6 * night)
            c = _v(self.x[i], 0.03, self.z[i])
            if age < 0.35:
                drop = c + _v(0.0, 3.0 * (1.0 - age / 0.35) ** 2, 0.0)
                out.append(dict(pos=drop[None], size=0.12, color=lin("#fff1d0"), alpha=gain, emit=4.0,
                                kind="spark"))
            rad = (1.0 if big else 0.6) * (0.4 + 1.6 * age ** 0.7)
            p = c + np.stack([np.cos(self.ring) * rad, 0.0 * self.ring, np.sin(self.ring) * rad * 0.9], 1)
            col = lin("#ffcf7a" if big else "#ffe7bf")
            out.append(dict(pos=p, size=0.06 + 0.04 * self.rs, color=col, alpha=gain * (0.45 if big else 0.3),
                            emit=1.6, kind="soft", twinkle=0.5, seed=self.rs))
        return out or None


class CallingPath:
    """The call (about 0:59): a road of gold light across the restless water from the horizon star to the
    nearest boat, the water on it perfectly still. It stays faintly into the shore scene."""

    def __init__(self, boats):
        self.boats = boats
        r = np.random.default_rng(5)
        n = 5000
        self.u = r.random(n) ** 0.7
        self.w = r.normal(size=n)
        self.seed = r.random(n)

    def sample(self, t):
        a = _win(t, 57.5, 61.0, 96.0, 104.0)
        if a <= 0.0:
            return None
        end = self.boats.place(0, t)[0]
        start = _v(-1.0, 0.0, -360.0)
        reach = _sc(57.5, 61.5, t)
        u = self.u * reach
        p = start * (1 - u)[:, None] + end * u[:, None]
        width = 0.4 + 5.0 * (1.0 - u) ** 1.5
        p[:, 0] += self.w * width * 0.5
        p[:, 1] = 0.02
        sh = 0.5 + 0.5 * np.sin(t * 2.0 + 30.0 * self.seed)
        return dict(pos=p, size=0.07 + 0.25 * (1 - u), color=lin("#ffd890"), alpha=a * (0.35 + 0.4 * sh),
                    emit=1.6, kind="soft", seed=self.seed, twinkle=0.6)


class Shore:
    """The shore of light: countless warm grains, each alone and flickering; where people are joined the sand
    stops flickering and lies in a steady glow. It curves away to both horizons: the whole world's people."""
    static = False

    def __init__(self):
        r = np.random.default_rng(13)
        n = 26000
        x = r.uniform(-1.0, 1.0, n)
        X = x * 140.0
        z = SHORE_Z - 0.0018 * X ** 2 + r.normal(size=n) * (0.8 + 0.01 * np.abs(X))
        self.pos = np.stack([X, 0.06 + 0.04 * r.random(n), z], 1)
        self.seed = r.random(n)
        self.size = 0.05 + 0.06 * r.random(n) ** 3
        self.steady_t = 84.0 + np.abs(X) / 10.0 + 6.0 * r.random(n)

    def sample(self, t):
        a = _win(t, 66.0, 74.0, 136.0, 142.0) + 0.85 * _win(t, 210.0, 216.0, 1e9, 2e9)
        if a <= 0.0:
            return None
        steady = _ss(0.0, 2.5, t - self.steady_t)
        fl = 0.5 + 0.5 * np.sin(t * (2.0 + 3.0 * self.seed) + 40.0 * self.seed)
        # kept faint (fix 1): a quiet line of grains, never a bright band across the water
        al = 0.42 * a * (0.25 + 0.45 * fl * (1 - steady) + 0.45 * steady)
        col = lin("#ffd9a0")[None, :] * (1 - steady)[:, None] + lin("#ffc664")[None, :] * steady[:, None]
        return dict(pos=self.pos, size=self.size, color=col, alpha=al, emit=1.3, kind="spark", seed=self.seed)


class CalledGrain:
    """Fragment 1: on a clear note one thin beam of the calling light touches one grain and lifts it, the way
    a mother lifts a sleeping child; it hangs glowing, then floats back down to the shore."""

    def __init__(self):
        self.at = _v(-1.5, 0.08, SHORE_Z)

    def sample(self, t):
        a = _win(t, 79.0, 80.5, 94.0, 96.0)
        if a <= 0.0:
            return None
        lift = 3.2 * _sc(80.0, 84.0, t) * (1.0 - _sc(90.0, 94.5, t))
        g = self.at + _v(0.0, lift, 0.0)
        beam_a = a * (1.0 - _sc(88.0, 92.0, t))
        ys = np.linspace(0.0, 40.0, 200)
        beam = self.at[None, :] + np.stack([0.002 * ys ** 1.5, ys, -0.6 * ys], 1)
        out = [dict(pos=g[None], size=0.22, color=lin("#fff0c8"), alpha=a, emit=5.0, kind="spark"),
               dict(pos=g[None], size=1.8, color=lin("#ffd890"), alpha=0.25 * a, kind="soft")]
        if beam_a > 0.0:
            out.append(ribbon(beam, width=np.linspace(0.12, 0.6, 200), color=lin("#ffe2a8"),
                              alpha=np.linspace(0.35, 0.0, 200) * beam_a, emit=1.2))
        return out


class Threads:
    """Fine warm threads between people who have turned to each other (gold), which carry the colours of the
    Words of Mother's Love when the world wakes (3:34)."""

    def __init__(self, places, t_on):
        self.p = places
        self.t_on = t_on
        self.pairs = [(i, i + 1) for i in range(len(places) - 1)
                      if np.linalg.norm(places[i] - places[i + 1]) < 7.0]
        r = np.random.default_rng(4)
        self.col = r.integers(0, 9, len(self.pairs))

    def sample(self, t):
        a = _win(t, 84.0, 90.0, 132.0, 138.0) + _win(t, 214.0, 219.0, 1e9, 2e9)
        if a <= 0.0:
            return None
        colour = _sc(214.0, 220.0, t)
        out = []
        for k, (i, j) in enumerate(self.pairs):
            on = _sc(self.t_on[j], self.t_on[j] + 1.5, t)
            if on <= 0.0:
                continue
            p0, p1 = self.p[i] + _v(0, 1.0, 0), self.p[j] + _v(0, 1.0, 0)
            u = np.linspace(0.0, 1.0, 16)
            line = p0[None] * (1 - u)[:, None] + p1[None] * u[:, None]
            line[:, 1] += 0.25 * np.sin(np.pi * u)
            c = lin(GOLD) * (1 - colour) + lin(COL[self.col[k]]) * colour
            pulse = 0.75 + 0.25 * np.sin(t * 2.0 + k)
            out.append(ribbon(line, width=0.035, color=c, alpha=a * on * 0.6 * pulse, emit=1.4))
        return out or None


class Lamps:
    """The saints' small clay oil lamps: warm flames that flicker in the wind but never go out."""

    def __init__(self, crowd_walk, crowd_stand, places, t_start, speed, heading):
        self.places, self.t0, self.speed, self.h = places, t_start, speed, heading

    def where(self, t):
        d = np.minimum(np.maximum(t - self.t0, 0.0), STOP - self.t0) * self.speed
        p = self.places.copy()
        p[:, 0] += np.sin(np.radians(self.h)) * d
        p[:, 2] += np.cos(np.radians(self.h)) * d
        lift = 0.95 + 0.85 * _sc(STOP + 0.5, STOP + 2.2, t)
        p[:, 1] = lift
        p[:, 2] += 0.35
        p[:, 0] += 0.25
        return p

    def sample(self, t):
        a = _win(t, 146.0, 149.0, 206.0, 211.0)
        if a <= 0.0:
            return None
        p = self.where(t)
        n = len(p)
        fl = 0.8 + 0.2 * np.sin(t * 7.0 + np.arange(n) * 1.3) * np.sin(t * 3.1 + np.arange(n))
        bright = 1.0 + 0.6 * _sc(STOP + 0.5, STOP + 2.5, t)
        return [dict(pos=p, size=0.09, color=lin(LAMP), alpha=a * fl, emit=3.0 * bright, kind="spark"),
                dict(pos=p, size=1.1, color=lin(LAMP), alpha=0.18 * a * fl * bright, kind="soft")]


STOP = 162.0              # the saints stop and turn to us ("their souls call out to us")


class VioletFlames:
    """From each lamp a small violet flame drifts forward across the dark water, from their time to ours, and
    gathers above the two on the near shore (2:55.5 to 2:58)."""

    def __init__(self, lamps):
        self.lamps = lamps
        r = np.random.default_rng(17)
        self.jit = r.normal(size=(60, 3))

    def sample(self, t):
        a = _win(t, 174.5, 175.5, 178.0, 179.5)
        if a <= 0.0:
            return None
        src = self.lamps.where(174.5)
        u = _ss(174.8, 178.6, t + 0.08 * np.arange(len(src)))[:, None]
        goal = PAIR + _v(0.0, 2.8, 0.0)
        mid = 0.5 * (src + goal) + _v(0.0, 2.0, 0.0)
        p = (1 - u) ** 2 * src + 2 * (1 - u) * u * mid + u ** 2 * goal
        c = lin(PW.GLOWS["Encouragement"])
        return [dict(pos=p, size=0.10, color=c, alpha=a, emit=3.5, kind="spark"),
                dict(pos=p, size=0.9, color=c, alpha=0.2 * a, kind="soft")]


class StarRing:
    """Star 7, Encouragement, shines again: the words rise into it (3:07.5), it flares and gains one new
    thin ring."""

    def __init__(self):
        self.a = np.linspace(0.0, 2 * np.pi, 360, endpoint=False)
        self.s = np.random.default_rng(3).random(360)

    def sample(self, t):
        out = []
        g = _sc(190.0, 191.5, t)
        if g > 0.0:
            star = _star7(t)
            age = max(t - 190.0, 0.0)
            r = 7.0 + 3.0 * np.exp(-age * 0.8)
            p = star[None, :] + np.stack([np.cos(self.a) * r, np.sin(self.a) * r, 0.0 * self.a], 1)
            c = lin(COL[ENC]) * 0.6 + lin("#fff0e0") * 0.4
            out.append(dict(pos=p, size=0.55, color=c, alpha=g * (0.3 + 0.5 * np.exp(-age * 0.6)), emit=1.5,
                            kind="soft", twinkle=0.4, seed=self.s))
        return out or None


class City:
    """The faint outline of a city of light in the clouds above the mountains, its gates glowing softly:
    Heavenly Jerusalem, the day of glory the song looks toward (from 3:20, brighter in the morning)."""

    def __init__(self):
        r = np.random.default_rng(23)
        pts = []
        for k, (x, w, h) in enumerate(((-60, 16, 34), (-34, 14, 46), (-12, 20, 58), (12, 20, 58), (34, 14, 46),
                                       (60, 16, 34))):
            m = 500
            u = r.random(m)
            side = r.random(m)
            px = np.where(side < 0.33, x - w / 2, np.where(side < 0.66, x + w / 2, x - w / 2 + w * u))
            py = np.where(side < 0.66, h * u, h + 4.0 * np.sin(np.pi * u))
            pts.append(np.stack([px, py, np.zeros(m)], 1))
        u = r.random(900)
        gate = np.stack([14.0 * np.cos(np.pi * u), 30.0 + 14.0 * np.sin(np.pi * u), np.zeros(900)], 1)
        wall = np.stack([r.uniform(-75, 75, 1200), r.uniform(0.0, 3.0, 1200), np.zeros(1200)], 1)
        p = np.concatenate(pts + [gate, wall])
        self.pos = p * 1.6 + _v(0.0, 70.0, -560.0)
        self.seed = r.random(len(p))

    def sample(self, t):
        a = 0.1 * _win(t, 200.0, 208.0, 1e9, 2e9) + 0.06 * _win(t, 214.0, 224.0, 1e9, 2e9)
        if a <= 0.0:
            return None
        return dict(pos=self.pos, size=0.9, color=lin("#fff3d8"), alpha=a * 0.6, emit=1.2, kind="soft",
                    twinkle=0.5, seed=self.seed, fog=0.3)


CAST = 229.3              # the fisherman's cast (right after the pause at 3:48)


class Net:
    """The net of light cast across the sky (3:50 to 4:06): a shimmering mesh whose knots glow in the colours
    of the Words of Mother's Love; it flashes once on the peak (4:02), sends a thread of light down to the
    people on the shore, then softens and drifts down over the lake like dew."""

    def __init__(self):
        r = np.random.default_rng(31)
        nx, ny = 34, 9
        self.nx, self.ny = nx, ny
        gx, gy = np.meshgrid(np.linspace(-1, 1, nx), np.linspace(0, 1, ny))
        self.g = np.stack([gx.ravel(), gy.ravel()], 1)
        self.kcol = np.array([lin(COL[(i + j) % 9]) for j in range(ny) for i in range(nx)])
        self.seed = r.random(len(self.g))
        self.dew = r.random((3000, 3))

    def knots(self, t):
        # cast by the fisherman in the near boat's bow (229.3): it flies up from his hands and opens across the sky
        fly = _sc(CAST, CAST + 2.6, t)
        open_ = _sc(CAST + 0.8, 234.5, t)
        fall = _sc(244.0, 254.0, t)
        x = self.g[:, 0] * (40.0 + 120.0 * open_)
        y = 22.0 + self.g[:, 1] * (4.0 + 22.0 * open_) - 20.0 * fall + 2.0 * np.sin(0.5 * t + 3 * self.g[:, 0])
        z = -150.0 - 30.0 * (1 - open_) + 20.0 * self.g[:, 1]
        sky = np.stack([x, np.maximum(y, 3.0), z], 1)
        if fly >= 1.0:
            return sky
        bow = BOATS_SET.place(0, t)[0] + _v(0.0, 2.2, 0.0)
        hand = bow[None, :] + 1.6 * np.stack([self.g[:, 0], self.g[:, 1], 0.0 * self.g[:, 0]], 1)
        u = fly
        arc = _v(0.0, 18.0, 0.0) * np.sin(np.pi * u)
        return hand * (1 - u) + sky * u + arc

    def sample(self, t):
        a = _win(t, CAST - 0.2, CAST + 0.6, 250.0, 258.0)
        if a <= 0.0:
            return None
        k = self.knots(t)
        flash = 1.0 + 2.0 * np.exp(-max(t - 242.0, 0.0) * 2.0) * (t >= 241.9)
        out = []
        grid = k.reshape(self.ny, self.nx, 3)
        # while the bundle flies the knots overlap: keep it a faint gold bundle (no soft white blob), full only once open
        op = _sc(CAST + 0.8, 234.5, t)
        line_a = a * 0.16 * flash * op
        # a fisherman's diamond mesh: gold threads along both diagonals, each sagging a little between knots
        for sgn in (1, -1):
            for i0 in range(-self.ny, self.nx + self.ny, 2):
                idx = [(j, i0 + sgn * j) for j in range(self.ny) if 0 <= i0 + sgn * j < self.nx]
                if len(idx) < 2:
                    continue
                pts = np.array([grid[j, i] for j, i in idx])
                u = np.linspace(0.0, 1.0, 5)[:-1]
                seg = [pts[m] * (1 - x) + pts[m + 1] * x - _v(0.0, 0.5 * np.sin(np.pi * x), 0.0)
                       for m in range(len(pts) - 1) for x in u] + [pts[-1]]
                out.append(ribbon(np.array(seg), width=0.10, color=lin("#ffdca0"), alpha=line_a, emit=1.3))
        out.append(dict(pos=k, size=0.55, color=self.kcol * 0.6 + lin("#fff2dc") * 0.4, alpha=a * 0.85 * (0.06 + 0.94 * op),
                        emit=2.2 * flash, kind="spark", twinkle=0.5, seed=self.seed))
        out.append(dict(pos=k, size=3.0, color=self.kcol, alpha=a * 0.10 * flash * op, kind="soft"))
        # threads down to the shores on the peak
        th = _win(t, 241.8, 242.4, 245.0, 248.0)
        if th > 0.0:
            for i in range(0, len(k), 23):
                top = k[i]
                bot = _v(top[0] * 0.5, 0.2, SHORE_Z - 0.0018 * (top[0] * 0.5) ** 2)
                u = np.linspace(0, 1, 12)[:, None]
                out.append(ribbon(top[None] * (1 - u) + bot[None] * u, width=0.08, color=self.kcol[i],
                                  alpha=th * 0.35, emit=1.5))
        dew = _win(t, 246.0, 250.0, 262.0, 275.0) * 0.6 + 0.25 * _sc(262.0, 270.0, t)
        if dew > 0.0:
            d = self.dew
            u = np.mod(d[:, 0] + 0.02 * t, 1.0)
            pos = np.stack([(d[:, 1] - 0.5) * 220.0, 30.0 * (1 - u) + 0.1, -40.0 - 160.0 * d[:, 2]], 1)
            out.append(dict(pos=pos, size=0.18, color=lin("#ffe2b0"), alpha=dew * u * 0.6, emit=1.4,
                            kind="spark", twinkle=0.7, seed=d[:, 2]))
        return out


class NineLights:
    """The arch of nine lights, high in the sky the whole song, all nine lit (songs 01 to 08 lit them); drawn
    at the scale of this song's wide sea. Star 7 flares when the Encouragement rises into it."""

    def __init__(self):
        r = np.random.default_rng(41)
        self.du = r.random(4000)
        self.jit = r.normal(size=(4000, 3)) * 1.2
        self.ds = r.random(4000)

    def sample(self, t):
        g = _arch_geo()
        P = g.homes(t)
        st = _arch_lit(t)
        k = np.array([a for a, _ in st])
        cols = np.array([lin(c) for c in COL])
        u = np.mod(self.du + 0.004 * t, 1.0)
        grid = np.linspace(0.0, 1.0, 9)
        dc = np.stack([np.interp(u, grid, cols[:, j]) for j in range(3)], 1) * 0.5 + lin("#ffe6c0") * 0.5
        pulse = 1.0 + 0.08 * np.sin(1.3 * t + np.arange(9))
        return [dict(pos=g.point(u, t) + self.jit, size=0.9 + 0.8 * self.ds, color=dc, alpha=0.10, kind="soft",
                     twinkle=0.6, seed=self.ds, fog=0.2),
                dict(pos=P, size=3.2, color=cols, alpha=np.minimum(k * pulse, 1.6), emit=3.0, kind="spark",
                     lod=False, fog=0.2),
                dict(pos=P, size=26.0, color=cols * 0.6 + lin("#fff0d8") * 0.4, alpha=0.10 * np.minimum(k, 2.0),
                     kind="soft", lod=False, dof=0.0, fog=0.2)]


class Rising:
    """In the calm hold: a few sparks rise from the shore toward the arch, never more than a handful."""

    def __init__(self):
        r = np.random.default_rng(55)
        self.d = r.random((80, 4))

    def sample(self, t):
        a = _sc(250.0, 258.0, t)
        if a <= 0.0:
            return None
        d = self.d
        u = np.mod(d[:, 0] + t / (14.0 + 8.0 * d[:, 1]), 1.0)
        x = (d[:, 2] - 0.5) * 120.0
        pos = np.stack([x, 1.0 + 70.0 * u ** 1.3, SHORE_Z - 30.0 * d[:, 3] - 0.0018 * x ** 2], 1)
        return dict(pos=pos, size=0.3, color=lin("#ffdca0"), alpha=a * 0.6 * np.sin(np.pi * u), emit=2.0,
                    kind="spark", twinkle=0.5, seed=d[:, 3])


# ---------------------------------------------------------------------------------------------------------
# People of light (built when the scene is set up)
# ---------------------------------------------------------------------------------------------------------
LOOK = dict(name="glitter", seams=0.6)
_PEOPLE = {}


def _shore_places(n, seed=3, spread=34.0):
    r = np.random.default_rng(seed)
    x = np.sort(r.uniform(-spread, spread, n))
    z = SHORE_Z + 1.5 - 0.0018 * x ** 2 + r.uniform(-0.6, 0.6, n)
    return np.stack([x, np.zeros(n), z], 1)


def _people():
    if _PEOPLE:
        return _PEOPLE
    from nine_reference_p3d import master_acting  # noqa: F401   (refined gestures)
    from nine_reference_p3d import pairs
    from nine_reference_p3d.body import Body
    from nine_reference_p3d.crowd import Crowd

    P = _PEOPLE
    # the two fishermen in the nearest boat: one steadies the other; at the call he turns, rests a hand on
    # his companion's shoulder, and both lift their heads toward the light (two men)
    b0 = BOATS[0]
    refs = pairs.Refs()
    fa = dict(shape="man", at=(b0[0] - 0.45, b0[2] + 0.1), facing=200.0, motion="stand", garment="tunic",
              hair="short", look=LOOK, color="#f6b040", color2="#ffdc96", points=26000, show=(44.0, 76.0),
              fade=1.2, seed=21.0,
              gesture=[(45.0, 58.0, "cup", dict(ease=1.2)),
                       (61.5, 72.0, "hand_on_shoulder", dict(side="R", to=lambda t: refs["b"].where(t, "shoulder.L", raw=True))),
                       (60.0, 74.0, "look_up", dict(amount=10.0))])
    fb = dict(shape="man", at=(b0[0] + 0.5, b0[2] - 0.1), facing=195.0, motion="stand", garment="tunic",
              hair="cap", look=LOOK, color="#f2a640", color2="#ffdc96", points=26000, show=(44.0, 76.0),
              fade=1.2, seed=22.0, gesture=[(45.0, 61.0, "bow", dict(amount=14.0)),
                                            (62.5, 74.0, "look_up", dict(amount=12.0))])
    a, b = refs.build(("a", "b"), a=fa, b=fb)
    P["fisher_a"], P["fisher_b"] = a, b

    # the called: along the shore, one at a time on the piano's notes, a person rises from the grains and
    # turns to the next; they stay (and more come) for the dawn and again for the waking world
    places = _shore_places(26)
    order = np.argsort(np.abs(places[:, 0]) + np.random.default_rng(2).uniform(0, 5, len(places)))
    t_on = np.zeros(len(places))
    for k, i in enumerate(order):
        t_on[i] = 84.5 + 0.95 * k
    P["_shore"] = (places, t_on)
    P["called"] = Crowd(places=places[:, [0, 2]], facing=lambda x, z: 180.0 + 0.0 * x, kinds=("stand", "open"),
                        start=t_on, until=137.0, fade=1.0, flash=0.25, points=4200, color=GOLD, color2=GOLD2, bright=1.25,
                        people=dict(woman=1, man=1, elder=0.3, child=0.2), act=118.5, seed=4.0)
    # the waking world: thousands suggested by many small people along every shore
    wide = _shore_places(70, seed=8, spread=80.0)
    P["world"] = Crowd(places=wide[:, [0, 2]], facing=lambda x, z: 180.0, kinds=("stand", "wave", "heart", "open",
                                                                                    "bow", "child"),
                       start=dict(t=212.0, center=(0.0, SHORE_Z), speed=14.0), fade=1.2, flash=0.2, points=3600,
                       color=GOLD, color2=GOLD2, bright=1.25, act=dict(t=216.0, center=(0.0, SHORE_Z), speed=10.0), seed=6.0)
    # Heavenly Mother, only ever from behind: on a point of the shore facing the sunrise, her arms opening
    mother = dict(shape="woman", garment="robe", veil=True, look=LOOK, color="#f8bc50", color2="#ffe4a8",
                  points=42000, fade=1.5, seed=31.0, height=1.72, bright=1.5)
    P["mother1"] = Body(at=(MOTHER1[0], MOTHER1[2]), facing=180.0, show=(106.0, 135.0),
                        gesture=[(109.5, 131.0, "open_arms", dict(ease=2.5))], **mother)
    P["mother2"] = Body(at=(MOTHER2[0], MOTHER2[2]), facing=180.0, show=(212.0, 252.0),
                        gesture=[(216.0, 248.0, "open_arms", dict(ease=2.5))], **mother)

    # the early church saints: a procession walking slowly along the far water's edge with small lamps,
    # then they stop, turn to us, and lift their lamps
    r = np.random.default_rng(12)
    n = 11
    walk_x = -22.0 + np.arange(n) * 2.6 + r.uniform(-0.4, 0.4, n)
    walk_z = SAINT_Z + r.uniform(-0.8, 0.8, n)
    t0 = 146.0
    speed = 0.55
    places = np.stack([walk_x, np.zeros(n), walk_z], 1)
    stop = places.copy()
    stop[:, 0] += speed * (STOP - t0)
    P["saints_walk"] = Crowd(places=places[:, [0, 2]], facing=90.0, kinds=("walk",), walk=speed, start=t0,
                             until=STOP + 0.4, fade=1.0, flash=0.1, points=4200, color="#ffd08a", bright=1.25,
                             color2="#fff0d0", people=dict(woman=1, man=1, elder=0.4), seed=9.0, scale=(0.95, 1.05))
    P["saints_stand"] = Crowd(places=stop[:, [0, 2]], facing=lambda x, z: 180.0 + 0.6 * x, kinds=("light",),
                              start=STOP - 0.2, act=dict(t=STOP + 0.5, center=(0.0, SAINT_Z), speed=8.0),
                              until=206.0, fade=1.0, flash=0.05, points=4200, color="#ffd08a", color2="#fff0d0", bright=1.25,
                              people=dict(woman=1, man=1, elder=0.4), seed=9.0, light=LAMP)
    P["_lamps"] = Lamps(None, None, places, t0, speed, 90.0)

    # the Encouragement on the near shore: a tired woman sitting with head bowed at the end of a hard day;
    # a friend (another woman) kneels beside her and rests a hand on her shoulder; as the words complete she
    # lifts her head, her glow strengthens, and the two stand side by side (two women)
    refs2 = pairs.Refs()
    tired = dict(shape="woman", at=(PAIR[0] + 0.35, PAIR[2]), facing=-20.0, garment="robe", hair="long",
                 look=LOOK, color="#e8b064", color2="#ffe6bc", points=36000, show=(174.2, 197.0), fade=1.2,
                 seed=41.0, bright=1.35,
                 motion=[(-1e9, "kneel", dict(dur=0.01, hands="free")), (187.3, "rise_up", dict(dur=2.2))],
                 gesture=[(-1e9, 182.6, "bow", dict(amount=22.0)),
                          (183.0, 187.6, "look_to", dict(to=lambda t: refs2["b"].where(t, "head", raw=True))),
                          (189.6, 196.0, "look_up", dict(amount=14.0))])
    friend = dict(shape="woman", at=(PAIR[0] - 0.4, PAIR[2] + 0.15), facing=40.0, garment="dress", hair="bun",
                  look=LOOK, color="#f6b040", color2="#ffdc96", points=36000, show=(174.2, 197.0), fade=1.2,
                  seed=42.0, bright=1.6,
                  motion=[(-1e9, "stand"), (175.6, "kneel", dict(one=True, dur=1.8, hands="free")),
                          (187.4, "rise", dict(one=True, dur=2.0, blend=0.08)), (189.6, "stand", dict(blend=0.6))],
                  gesture=[(177.4, 187.2, "hand_on_shoulder",
                            dict(side="R", to=lambda t: refs2["a"].where(t, "shoulder.R", raw=True))),
                           (189.8, 196.0, "look_up", dict(amount=14.0))])
    ta, fr = refs2.build(("a", "b"), a=tired, b=friend)
    P["tired"], P["friend"] = ta, fr

    # the fisher of people casts the net of light from the near boat's bow (one man)
    P["caster"] = Body(shape="man", at=(BOATS[0][0] + 0.9, BOATS[0][2] - 0.3), facing=170.0, motion="stand",
                       garment="tunic", hair="short", look=LOOK, color="#f6b040", color2="#ffdc96", points=26000,
                       show=(224.0, 262.0), fade=1.5, seed=27.0,
                       gesture=[(CAST - 1.0, CAST + 1.6, "throw", dict(side="R", lead=1.0)),
                                (CAST + 1.2, 250.0, "look_up", dict(amount=16.0))])
    # the fishers of people at the bows of the boats in the peace
    bows = np.array([BOATS[k] + _v(0.0, 0.0, 0.0) for k in range(3)])
    P["bows"] = Crowd(places=bows[:, [0, 2]], facing=180.0, kinds=("stand",), start=246.0, fade=2.0, flash=0.1,
                      points=3600, color=GOLD, color2=GOLD2, bright=1.25, people=dict(woman=1, man=1), seed=12.0)
    return P


class DriftHearts:
    """Small hearts of violet light, each a fine outline of sparks, drift up and sway away from the words as
    they leave for star 7 (the pinned engine has no heart sprite, so each heart is drawn in points)."""

    def __init__(self, t0, t1, color, rate=6.0, life=3.4):
        from p3d.brand_hearts import heart_points
        r = np.random.default_rng(77)
        self.k = int((t1 - t0) * rate)
        self.birth = t0 + np.sort(r.uniform(0.0, t1 - t0, self.k))
        self.d = r.random((self.k, 4))
        hp = np.asarray(heart_points(28), np.float64)
        self.hp = hp[:, :2] if hp.ndim == 2 else hp
        self.life, self.col = life, lin(color) * 0.7 + lin("#fff0ff") * 0.3

    def sample(self, t):
        age = t - self.birth
        live = (age > 0) & (age < self.life)
        if not live.any():
            return None
        start = np.asarray(PW.place(_LAYOUT, t, 0.5, RIDE_Y, DEPTH), np.float64)
        cam = CAMERA.state(t)
        r, u, f = cam.basis()
        pts, al = [], []
        for i in np.nonzero(live)[0]:
            a = age[i] / self.life
            c = start + r * ((self.d[i, 0] - 0.5) * 2.6 + 0.25 * np.sin(2.0 * age[i] + 6 * self.d[i, 1])) \
                + u * (-0.2 + 0.55 * age[i]) + f * (self.d[i, 2] - 0.5)
            sz = 0.07 + 0.06 * self.d[i, 3]
            pts.append(c[None, :] + sz * (self.hp[:, 0:1] * r[None, :] + self.hp[:, 1:2] * u[None, :]))
            al.append(np.full(len(self.hp), np.sin(np.pi * a) ** 1.5))
        return dict(pos=np.concatenate(pts), size=0.012, color=self.col, alpha=0.9 * np.concatenate(al), emit=2.5,
                    kind="spark")


class TiredGlow:
    """The tired woman's glow strengthens from the centre outward as the words complete, like a fire
    catching; around the two of them the water goes still in a widening circle (world calm)."""

    def sample(self, t):
        a = _win(t, 181.0, 184.0, 192.0, 196.0)
        if a <= 0.0:
            return None
        p = _people()["tired"].where(t, "chest", raw=True)
        return [dict(pos=np.asarray(p)[None], size=0.9, color=lin("#ffcf7a"), alpha=0.12 * a, kind="soft")]


BOATS_SET = Boats()


def _setup(scene):
    P = _people()
    scene.add("beads", Beads(), reflect=False)
    scene.add("boats", Clear(BOATS_SET))
    scene.add("calling", Clear(CallingPath(BOATS_SET)), reflect=False)
    scene.add("shore", Clear(Shore()), reflect=False)
    scene.add("grain", Clear(CalledGrain()))
    places, t_on = P["_shore"]
    scene.add("threads", Clear(Threads(places, t_on)))
    scene.add("lamps", Clear(P["_lamps"]))
    scene.add("violet", Clear(VioletFlames(P["_lamps"])), reflect=False)
    scene.add("nine", Clear(NineLights(), bottom=False, sig=False), reflect=False)
    scene.add("star7", StarRing(), reflect=False)
    scene.add("city", City(), reflect=False)
    scene.add("net", Clear(Net()), reflect=False)
    scene.add("rising", Clear(Rising()))
    scene.add("glow", TiredGlow())
    # the Encouragement's symbol (praying hands) traced in the world by violet sparks over the saints' lamps,
    # just before its words, and violet hearts drifting off the words as they rise into star 7
    from p3d import brand  # noqa: F401   (loads brand_symbols and brand_hearts in their order)
    from p3d.brand_symbols import Traced
    scene.add("enc_symbol", Clear(Traced("Encouragement", style="fireflies", ride=(0.5, 0.60, 34.0), size=6.0,
                                         camera=CAMERA, t0=171.0, dur=1.8, hold=1.6, out=1.4, intensity=0.55)),
              reflect=False)
    scene.add("enc_hearts", Clear(DriftHearts(187.6, 190.6, COL[ENC]), bottom=True), reflect=False)
    # people are never mirrored in the water: their reflections would reach into the calm lower third
    for name in ("fisher_a", "fisher_b", "mother1", "mother2", "caster"):
        P[name].add(scene, name, reflect=False)
    for name in ("tired", "friend"):
        P[name].add(scene, name, reflect=False, fog=False)
    for name in ("called", "world", "saints_walk", "saints_stand", "bows"):
        scene.add(name, P[name], reflect=False)
    WORDS.add_to(scene)


# ---------------------------------------------------------------------------------------------------------
# The world: song 08's golden lake, cooling to a misty sea dawn at Galilee; the night of the early church;
# the glory; a pearl and pale gold morning over a mirror sea
# ---------------------------------------------------------------------------------------------------------
def _d(hexs, k):
    """A display colour scaled in linear light (bright skies stay under clipping)."""
    return lin(hexs) * k


LOOKS = dict(
    handoff=dict(base="dawn", sky_top="#24365e", sky_mid="#6c5a7c", sky_hor="#f0ad78", sun_el=-1.6,
                 sun_int=0.9, sun_color="#ffcf98", mist=0.35, mist_color="#a87a66", haze_color="#c4866a",
                 water="#0a0a12", ripple=0.15, stars=0.35, hill_color="#140e1c"),
    galilee=dict(base="night", sky_top="#173c48", sky_mid="#30646a", sky_hor="#d4bc8c", sun_az=180.0,
                 sun_el=-4.0, sun_int=0.55, sun_color="#ffd6a0", stars=0.45, milky=0.15, clouds=0.25,
                 haze=0.65, haze_color="#55807a", mist=0.55, mist_height=2.6, mist_color="#6a8c84",
                 hill_color="#0a1a20", water="#04121a", ripple=0.75, dust_color="#ffe2b0",
                 dust_color2="#cfe8de"),
    seagreen=dict(base="night", sky_top="#1e4652", sky_mid="#40807c", sky_hor="#e8d09c", sun_az=180.0,
                  sun_el=-2.6, sun_int=0.7, sun_color="#ffd8a0", stars=0.3, milky=0.05, clouds=0.3, haze=0.65,
                  haze_color="#6e9488", mist=0.5, mist_height=2.4, mist_color="#86a294", hill_color="#0e2228",
                  water="#06161c", ripple=0.55, dust_color="#ffe2b0", dust_color2="#e8f0dc"),
    firstdawn=dict(base="night", exposure=0.8, sky_top=_d("#2a5a6c", .5), sky_mid=_d("#6a9a90", .38), sky_hor=_d("#ffd496", .55),
                   sun_az=180.0, sun_el=2.2, sun_int=0.85, sun_color="#ffe0a8", sun_glow=0.7, sun_disc=6.0,
                   stars=0.05, milky=0.0, clouds=0.35, haze=0.45, haze_color=_d("#c8aa80", .45), mist=0.28,
                   mist_height=2.0, mist_color=_d("#d6be98", .42), hill_color="#22383e", water="#081a20",
                   ripple=0.18, rays=0.35, dust_color="#fff0d0", dust_color2="#ffe0b0"),
    # the early church: a luminous sea-green twilight in mist, warm at the horizon (never dark)
    church=dict(base="night", sky_top="#143a48", sky_mid="#2a5c64", sky_hor="#a68c66", sun_az=180.0,
                sun_el=-3.0, sun_int=0.55, sun_color="#ffd29a", stars=0.35, milky=0.05, clouds=0.4, haze=0.65,
                haze_color="#6e8a7c", mist=0.55, mist_height=2.6, mist_color="#7e9a8a", hill_color="#10262a",
                water="#0a1e22", ripple=0.6, dust_color="#ffd8a0", dust_color2="#ffe8c0"),
    glory=dict(base="night", exposure=0.8, sky_top=_d("#2c5664", .5), sky_mid=_d("#86ac9a", .38), sky_hor=_d("#ffe0aa", .55),
               sun_az=180.0, sun_el=4.5, sun_int=0.55, sun_color="#ffe8b8", sun_glow=0.6, sun_disc=6.0, stars=0.0,
               milky=0.0, clouds=0.3, haze=0.45, haze_color=_d("#d8c49c", .45), mist=0.25,
               mist_color=_d("#e0cca8", .42), hill_color="#263e42", water="#0e262c", ripple=0.25, rays=0.7,
               dust_color="#fff4d8", dust_color2="#ffe6b8"),
    morning=dict(base="night", exposure=0.8, sky_top=_d("#3c7690", .55), sky_mid=_d("#88b6aa", .38), sky_hor=_d("#ffe2b8", .55),
                 sun_az=180.0, sun_el=5.0, sun_int=0.36, sun_color="#ffe4b0", sun_glow=0.35, sun_disc=5.0,
                 stars=0.0, milky=0.0, clouds=0.3, haze=0.42, haze_color=_d("#dccca8", .42), mist=0.16,
                 mist_color=_d("#e8d8bc", .42), hill_color="#36565e", water="#0c262e", ripple=0.08, rays=0.25,
                 dust_color="#fff6e0", dust_color2="#ffe2b0"),
    mirror=dict(base="night", exposure=0.8, sky_top=_d("#3c7690", .55), sky_mid=_d("#88b6aa", .38), sky_hor=_d("#ffe0b4", .55),
                sun_az=180.0, sun_el=4.5, sun_int=0.36, sun_color="#ffe4b0", sun_glow=0.35, sun_disc=5.0,
                stars=0.0, milky=0.0, clouds=0.28, haze=0.42, haze_color=_d("#e0cca8", .42), mist=0.15,
                mist_color=_d("#ecdcc0", .42), hill_color="#36565e", water="#0c262e", ripple=0.0, rays=0.25,
                dust_color="#fff6e0", dust_color2="#ffe2b0"),
    evening=dict(base="night", exposure=0.8, sky_top=_d("#36607e", .55), sky_mid=_d("#a49a94", .4), sky_hor=_d("#ffc890", .55),
                 sun_az=180.0, sun_el=3.0, sun_int=0.65, sun_color="#ffdcaa", sun_glow=0.55, sun_disc=5.5,
                 stars=0.08, milky=0.0, clouds=0.3, haze=0.45, haze_color=_d("#e0b890", .45), mist=0.18,
                 mist_color=_d("#e8ccac", .42), hill_color="#30464e", water="#12303a", ripple=0.0, rays=0.3,
                 dust_color="#fff0d4", dust_color2="#ffd8a8"),
)


def _arch_lit(t):
    out = []
    for k in range(9):
        if k == ENC:
            age = t - 190.0
            if age >= 0:
                out.append((0.6 + 1.5 * np.exp(-age * 1.2), age))
                continue
        out.append((0.6, 30.0))
    return out


def _calm_discs(t):
    items = []
    enc = _win(t, 181.0, 186.0, 200.0, 206.0)
    if enc > 0.0:
        items.append(dict(center=(PAIR[0], PAIR[2] - 4.0), radius=2.0 + 26.0 * _sc(181.0, 190.0, t), ripple=0.0,
                          mirror=1.0, soft=6.0))
    call = _win(t, 58.0, 61.0, 98.0, 104.0)
    if call > 0.0:
        b = BOATS_SET.place(0, t)[0]
        items.append(dict(center=(b[0], b[2]), radius=4.0 + 6.0 * call, ripple=0.0, mirror=1.0))
    mo = _win(t, 109.0, 112.0, 132.0, 138.0)
    if mo > 0.0:
        items.append(dict(center=(MOTHER1[0], MOTHER1[2]), radius=3.0 + 90.0 * _sc(109.0, 124.0, t), ripple=0.0,
                          mirror=1.0, soft=14.0))
    return items


WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "handoff"), (14.0, "galilee", 20.0), (70.0, "seagreen", 14.0), (110.0, "firstdawn", 8.0),
          (140.0, "church", 12.0), (194.0, "glory", 10.0), (220.0, "morning", 12.0), (250.0, "mirror", 8.0),
          (281.0, "evening", 14.0)],
    ripple=lambda t: 0.75 * (1.0 - _calm(t)) + 0.0,
    light=dict(pos=_v(-1.0, 3.0, -360.0), color="#ffe2b0",
               strength=Track([(0.0, 0.6), (56.0, 0.6), (60.0, 1.05), (72.0, 0.8), (TOTAL, 0.8)]), size=1.2,
               rays=0.6),
    lights=[dict(pos=lambda t: BOATS_SET.lamp_at(0, t), color=LAMP, strength=lambda t: 0.6 * BOATS_SET.alpha(t),
                 radius=4.0),
            dict(pos=lambda t: BOATS_SET.lamp_at(1, t), color=LAMP, strength=lambda t: 0.5 * BOATS_SET.alpha(t),
                 radius=4.0),
            dict(pos=lambda t: PAIR + _v(0.0, 1.0, 0.6), color="#ffcf7a",
                 strength=lambda t: 0.25 * _win(t, 182.0, 186.0, 192.0, 197.0), radius=2.0)],
    calm=_calm_discs,
    react=dict(beat=0.0, level=0.15),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=59.5, strength=0.12, rise=0.8, fall=1.5, color="#ffd08a"),
            ],
    motion_blur=0.3,
)

TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(text="", t0=1e9, t1=1e9 + 1)
FRAGMENTS = []
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
