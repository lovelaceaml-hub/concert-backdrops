"""Song 08 "Out of Heaven, Favor From God": the version 2 concert backdrop (one continuous stage video).

Concert item 9, Sunday December 6. Orchestra only, nothing sung live, so the picture and the few words on screen
carry the meaning. Design: project-docs/designs/08 Out of Heaven, Favor From God.md ("The Embroidered Sky").
Timeline, cues and checks: project-docs/backdrops/s08-full2/. Every time below is video time in seconds; the
music is the live length, 210.0 s (the church's ensemble recording is 209.11 s, within 1 s, used as is and
padded with silence to 210.0 s), then a 15 s calm hold: 225.0 s in all, 60 fps, 1920x1080.

Built on the pinned Film 10 engine (d928ff9) with the approved Revision 3 craft: the Claude Final v1 cream serif
phrases with coloured capsule labels (f43f451), warm gold glitter people, smooth eased motion. Scenery and
signature effects are this song's own (DESIGN-SYSTEM 6: royal festival night, deep royal purple, crimson and
gold, gold aurora like embroidery, rays, sparkle, grand and symmetrical). No comets (song 01 only).
Loaded by tools/s08_full2/render.py as songs.s08_full2. No em dash or en dash anywhere in this file.
"""
import numpy as np

import songs.s03_original as _base

TOTAL = 225.0                       # 210.0 s live length, then a 15 s calm hold
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 205.4
_base.SONG_END = 210.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402,F401
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

import reference  # noqa: E402,F401  (registers nine_reference_p3d: Claude Final v1)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401
from nine_reference_p3d.body import Body  # noqa: E402

AUDIO_FILE = "audio/promo/s08.mp3"   # not used for the picture; the review copy joins the real file
TOTAL = 225.0
LIVE = 210.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 205.4
SONG_END = 210.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------------------
# The music (measured on the recording, TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
M = dict(
    sound=2.9,          # first sound
    full1=14.0,         # the full entry: Heaven opens
    breath=41.5,        # quiet breath
    hit1=43.24,         # the hit after the breath: the soft middle begins
    dip1=78.4,          # a short dip
    build=83.0,         # building to the peak 86 to 90
    soft2=90.5,         # soft again
    hit2=109.18,        # the hit after the quiet at 108.5: the soul reaches Mother's arms
    quiet2=112.0,       # quiet
    rise3=116.4,        # rising
    full3=123.0,        # full
    mid3=134.0,         # medium
    soft3=150.0,        # softer
    finale=163.0,       # the finale
    chord=202.28,       # the final chord: the curtain opens
    end=205.4,          # the music has gone
)

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
GOLD = "#ffd05f"
WARM = "#fff4dc"


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(t, a, b, c, d):
    """0 before a, rising to 1 by b, 1 to c, falling to 0 by d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _soft(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0, the camera looks toward -z)
# ---------------------------------------------------------------------------------------------------------
STAR = _v(0.0, 7.0, -420.0)         # the warm star at the exact centre of the horizon
SEAM = _v(0.0, 70.0, -150.0)        # the opening in the sky
LEFT = _v(-3.1, 0.0, -1.0)          # the brother's shore
RIGHT = _v(3.1, 0.0, -1.0)          # the sister's shore
MEET = _v(0.0, 0.0, -1.0)           # where the bridegroom and the bride meet
LAMP = _v(0.0, 0.0, -24.0)          # the lampstand
MOTHER = _v(0.0, 0.0, -95.0)       # Heavenly Mother at the horizon, seen only from behind
ARCH = dict(span=150.0, height=15.0, z=0.0, ahead=95.0, lift=21.0)
_ARCH_TH = np.radians(np.linspace(172.0, 8.0, 9))

# ---------------------------------------------------------------------------------------------------------
# The camera: eased holds between keys (still while words are read), slow and stately
# ---------------------------------------------------------------------------------------------------------
KEYS = [
    # t        position                 target
    (0.0, _v(0.0, 2.6, 40.0), _v(0.0, 8.0, -100.0)),      # song 07's closing frame: wide, eye level
    (8.0, _v(0.0, 2.6, 39.6), _v(0.0, 8.6, -100.0)),      # still while the opening is read
    (16.0, _v(0.0, 3.2, 36.0), _v(0.0, 14.0, -100.0)),    # the ascent toward the opening sky
    (24.0, _v(0.0, 2.7, 30.0), _v(0.0, 11.0, -100.0)),
    (40.0, _v(0.0, 2.0, 20.0), _v(0.0, 6.0, -100.0)),     # the glide over the gold rings
    (47.0, _v(-2.3, 1.3, 5.0), _v(-3.2, 0.95, -1.0)),     # the brother's shore
    (52.5, _v(-1.6, 1.3, 4.8), _v(-2.4, 0.95, -1.0)),
    (57.0, _v(0.0, 1.2, 5.3), _v(0.0, 1.28, -1.0)),       # both shores, close, for the Compliment
    (71.5, _v(0.0, 1.2, 5.3), _v(0.0, 1.28, -1.0)),
    (78.5, _v(0.0, 1.3, 6.8), _v(0.0, 1.05, -1.4)),       # the meeting
    (85.0, _v(0.0, 1.5, 7.6), _v(0.0, 2.0, -4.0)),        # the pair and the congregation, for the Gratitude
    (98.6, _v(0.0, 1.5, 7.6), _v(0.0, 2.0, -4.0)),
    (104.0, _v(0.0, 2.8, 28.0), _v(0.0, 8.0, -150.0)),    # out to the horizon: Mother's arms
    (112.0, _v(0.0, 2.8, 27.0), _v(0.0, 8.0, -150.0)),
    (118.0, _v(0.0, 2.6, 14.0), _v(0.0, 5.0, -24.0)),     # the lampstand
    (130.0, _v(0.0, 2.6, 12.0), _v(0.0, 6.0, -24.0)),
    (140.0, _v(0.0, 2.8, 18.0), _v(0.0, 13.0, -60.0)),    # the linen over the sky
    (186.0, _v(0.0, 3.2, 44.0), _v(0.0, 14.0, -100.0)),   # the long reveal of the embroidered sky
    (199.0, _v(0.0, 3.0, 44.0), _v(0.0, 13.0, -100.0)),
    (214.0, _v(0.0, 2.6, 40.0), _v(0.0, 9.0, -100.0)),    # the calm hold, wide at eye level (song 09's start)
    (TOTAL, _v(0.0, 2.6, 39.6), _v(0.0, 9.0, -100.0)),
]


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _keyed(t):
    ks = KEYS
    if t <= ks[0][0]:
        return ks[0][1], ks[0][2]
    for (t0, p0, q0), (t1, p1, q1) in zip(ks[:-1], ks[1:]):
        if t <= t1:
            u = _soft((t - t0) / (t1 - t0))
            return p0 + (p1 - p0) * u, q0 + (q1 - q0) * u
    return ks[-1][1], ks[-1][2]


def _fov(t):
    return 50.0 - 4.0 * _win(t, 44.0, 47.0, 52.0, 56.5)


def _rig(focus):
    return Rig([Path(_keyed, 0.0, TOTAL, blend=0.0, fov=_fov, aperture=0.0,
                     focus=focus if focus is not None else "target")],
               blend=0.0, fov=50.0, aperture=0.0, handheld=0.0, min_height=0.3)


_LAYOUT = _rig(None)


def _arch_center(t):
    """The arch rides with the camera (a crown of light across the top of the sky in every shot)."""
    p, q = _keyed(t)
    return _v(p[0], p[1] + ARCH["lift"] - 2.6, p[2] - ARCH["ahead"])


def star_pos(k, t):
    """The place of star k (0 is star 1) on the arch at t."""
    c = _arch_center(t)
    th = _ARCH_TH[k]
    return c + _v(0.5 * ARCH["span"] * np.cos(th), ARCH["height"] * np.sin(th), 0.0)


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


CAMERA = _rig(None)

# ---------------------------------------------------------------------------------------------------------
# The words: the opening title, the two expressions (exact campaign wording, website colours) and the three
# fragments the design names. All ride flat to the picture in the upper middle, never in the water.
# ---------------------------------------------------------------------------------------------------------
WT = dict(
    gold=dict(t_in=17.0, t_read0=18.6, t_read1=24.6, t_out=26.6),           # "bright as gold"
    Compliment=dict(t_in=57.8, t_read0=59.6, t_read1=69.4, t_out=71.2),     # readable 9.8 s
    bride=dict(t_in=74.6, t_read0=76.2, t_read1=81.4, t_out=82.8),         # "bridegroom and bride"
    Gratitude=dict(t_in=85.2, t_read0=87.0, t_read1=96.8, t_out=98.6),      # readable 9.8 s
    zion=dict(t_in=185.0, t_read0=188.2, t_read1=207.5, t_out=211.5),       # "the glory of Zion"
)
EXPR = ("Compliment", "Gratitude")
Y_TEXT = 0.57            # centre of a phrase block from the bottom (0.36 of the height from the top)
DEPTH = 7.0


def _ride(y=Y_TEXT):
    return (0.5, y, DEPTH)


def _spec(name, frac, **kw):
    tt = WT[name]
    mid = 0.5 * (tt["t_read0"] + tt["t_read1"])
    d = dict(ride=_ride(), face="screen", width=_width(mid, DEPTH, frac), name=name, reflect=False, **tt)
    d.update(kw)
    return d


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


_SPECS = [
    _spec("gold", 0.36, label="", lines=["bright as gold"], color=GOLD, glow="#ffbf4a", tint=0.55,
          arrive="petals", leave="sink", petals=0.0),
    _spec("Compliment", 0.40, expr="Compliment", pill=True, arrive="pen", nib=False, leave="arch",
          to=lambda t: star_pos(8, t)),
    _spec("bride", 0.46, label="", lines=["bridegroom and bride"], color="#fff0dc", glow="#ffe2b0",
          tint=0.35, ride=_ride(0.67), arrive="pen", nib=False, leave="fade"),
    _spec("Gratitude", 0.46, expr="Gratitude", pill=True, arrive="pen", nib=False, leave="arch",
          to=lambda t: star_pos(1, t)),
    _spec("zion", 0.40, label="", lines=["the glory of Zion"], color="#ffe2a0", glow="#ffb84a", tint=0.6, halo=1.2,
          ride=_ride(0.71),
          arrive="stitch", leave="fade"),
]
WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)

# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights: stars 1 and 3 to 9 lit from the start (earlier songs); star 9 (Compliment) flares
# again with a new thin ring as its words fold away; star 2 (Gratitude) lights for the first time, the last
# star of the concert, and the whole arch glows together.
# ---------------------------------------------------------------------------------------------------------
T_STAR9 = WT["Compliment"]["t_out"] - 0.4
T_STAR2 = WT["Gratitude"]["t_out"] - 0.4


def _arch_lit(t):
    out = []
    whole = 0.45 * np.exp(-max(t - T_STAR2 - 0.6, 0.0) * 0.5) * float(t > T_STAR2 + 0.3)
    for k in range(9):
        if k == GRAT:
            age = t - T_STAR2
            if age < -0.35:
                out.append((0.0, -1.0))
                continue
            g = min(max((age + 0.35) / 0.35, 0.0), 1.0)
            out.append((0.62 * g + 1.5 * np.exp(-max(age, 0.0) * 1.0) * float(age >= 0) + whole, max(age, 0.0)))
            continue
        b = 0.62 + whole
        age = 40.0 + t
        if k == COMP and t >= T_STAR9:
            b += 1.1 * np.exp(-(t - T_STAR9) * 1.1)
            age = t - T_STAR9
        out.append((b, age))
    return out


# ---------------------------------------------------------------------------------------------------------
# Point sets of this song
# ---------------------------------------------------------------------------------------------------------
def _rng(s):
    return np.random.default_rng(s)


class Seam:
    """The opening in the sky: a thin gold seam that parts like curtains on the full entry, a far radiance
    beyond it; later it is where the heavenly light pours through again."""

    def __init__(self):
        r = _rng(1)
        self.n = 2600
        self.u = r.random((self.n, 4))

    def sample(self, t):
        crack = _sc(8.0, 12.5, t)
        wide = _sc(M["full1"] - 0.5, M["full1"] + 3.0, t)
        a = crack * (1.0 - _sc(40.0, 47.0, t)) + 0.45 * _win(t, 196.0, M["chord"], 207.0, 216.0)
        if a <= 0.002:
            return None
        u = self.u
        h = 46.0
        y = SEAM[1] + (u[:, 0] - 0.5) * h
        half = (0.6 + 5.0 * wide) * np.cos((u[:, 0] - 0.5) * np.pi) ** 1.5
        side = np.where(u[:, 1] > 0.5, 1.0, -1.0)
        x = side * half * np.abs(np.tan(1.2 * (u[:, 2] - 0.5))) * 1.4   # a soft glow, densest at the centre
        pos = np.stack([x, y, np.full(self.n, SEAM[2]) + (u[:, 3] - 0.5) * 4.0], axis=1)
        out = [dict(pos=pos, size=2.4 + 2.4 * u[:, 2], color=lin("#ffd98a"), alpha=0.16 * a, emit=1.8, kind="soft",
                    twinkle=0.4, seed=u[:, 3], reflect=False, fog=0.3),
               dict(pos=_v(0.0, SEAM[1], SEAM[2] - 6.0)[None, :], size=30.0 + 30.0 * wide,
                    color=lin("#ffe6b0"), alpha=0.22 * a * (0.4 + 0.6 * wide), kind="soft", reflect=False, fog=0.0,
                    dof=0.0, lod=False)]
        return out


class GoldColumn:
    """Favor coming down: a slow, heavy, glittering column of gold dust from the opening to the lake."""

    def __init__(self, n=9000):
        r = _rng(2)
        self.n = n
        self.s = r.random((n, 5))

    def gain(self, t):
        return _win(t, M["full1"] - 0.5, M["full1"] + 2.5, 40.0, 46.0) + 0.45 * _win(t, 85.0, 87.5, 97.0, 100.0)

    def sample(self, t):
        g = self.gain(t)
        if g <= 0.002:
            return None
        s = self.s
        top, bot = SEAM[1] - 8.0, 0.2
        speed = 3.5 + 2.5 * s[:, 0]
        y = top - np.mod(s[:, 1] * (top - bot) + speed * t, top - bot)
        spread = 2.0 + 12.0 * (1.0 - (y - bot) / (top - bot)) ** 0.5 * (0.5 + 0.5 * _sc(18.0, 26.0, t))
        a = s[:, 2] * 2.0 * np.pi
        rad = spread * np.sqrt(s[:, 3])
        z = SEAM[2] + 60.0 * (1.0 - (y - bot) / (top - bot))        # the column slants toward us as it falls
        pos = np.stack([np.cos(a) * rad + 0.6 * np.sin(0.7 * t + 9 * s[:, 4]), y, z + np.sin(a) * rad], axis=1)
        al = g * (0.35 + 0.65 * s[:, 4]) * _ss(0.0, 6.0, y)
        return dict(pos=pos, size=0.10 + 0.22 * s[:, 4], color=lin(GOLD) * (0.8 + 0.4 * s[:, 0:1]), alpha=al,
                    emit=2.2, kind="spark", twinkle=0.9, seed=s[:, 1], vel=np.tile([0.0, -4.0, 0.0], (self.n, 1)))


class Rings:
    """Rings of light blooming on the water: where the gold lands, after every word spoken, on the hits."""

    def __init__(self):
        rings = []
        # where the gold column lands (one ring every 1.3 s while it falls)
        for k, t0 in enumerate(np.arange(M["full1"] + 1.0, 42.0, 1.3)):
            r = _rng(100 + k).random(2)
            rings.append((t0, (-12.0 + 24.0 * r[0], -60.0 - 40.0 * r[1]), GOLD, 0.6, 9.0))
        # "bright as gold" falls into the lake as a row of rings
        for k in range(7):
            rings.append((WT["gold"]["t_read1"] + 0.6 + 0.12 * k, (-7.5 + 2.5 * k, -32.0), GOLD, 0.9, 7.0))
        # peace settling after each word, the meeting, the hits, the final chord
        rings += [
                  (M["hit2"], (MOTHER[0], MOTHER[2] + 6.0), "#ffe6c0", 1.0, 30.0),
                  (M["full3"], (LAMP[0], LAMP[2]), "#ffb64a", 0.9, 16.0),
                  (M["finale"], (0.0, -40.0), "#ffd8a0", 0.8, 24.0),
                  (M["chord"], (0.0, -40.0), "#ffe2b0", 0.6, 11.0)]
        self.rings = rings
        self.ang = np.linspace(0.0, 2.0 * np.pi, 360, endpoint=False)

    def sample(self, t):
        out = []
        for t0, (x, z), c, s, life in self.rings:
            age = t - t0
            if age < 0.0 or age > life:
                continue
            r = 0.5 + 2.6 * s * age ** 0.8 * (1.0 + 0.04 * abs(z))
            a = (1.0 - age / life) ** 1.6 * _sc(0.0, 0.3, age) * 0.75 * s
            p = np.stack([x + r * np.cos(self.ang), np.full_like(self.ang, 0.03), z + 0.7 * r * np.sin(self.ang)],
                         axis=1)
            out.append(dict(pos=p, size=0.10 + 0.012 * abs(z) ** 0.7, color=lin(c), alpha=a, emit=1.6, kind="soft",
                            reflect=False))
        return out or None


class Ribbons:
    """Soft wind and sweet fragrance: translucent rose and peach ribbons rising from the lake and carried by
    the wind across the screen, past the mountains, where small warm lights bloom like windows."""

    def __init__(self):
        r = _rng(4)
        self.k = 5
        self.ph = r.random((self.k, 3))
        r2 = _rng(5)
        n = 150
        self.win = np.stack([-150.0 + 300.0 * r2.random(n), 1.0 + 9.0 * r2.random(n) ** 2,
                             -230.0 - 50.0 * r2.random(n)], axis=1)
        self.wt = 30.0 + 11.0 * ((self.win[:, 0] + 150.0) / 300.0) + 1.5 * r2.random(n)
        self.ws = r2.random(n)

    def sample(self, t):
        from p3d.api import ribbon
        out = []
        g = _win(t, 26.0, 29.0, 40.0, 44.0)
        if g > 0.002:
            for k in range(self.k):
                ph = self.ph[k]
                u = np.linspace(0.0, 1.0, 60)
                x0 = -70.0 + 140.0 * ((t - 26.0) / 16.0 + ph[0] * 0.5) - 90.0 * u
                y = 1.0 + 26.0 * u * (0.7 + 0.5 * ph[1]) + 3.0 * np.sin(5.0 * u + 1.3 * t + 6 * ph[2])
                z = -60.0 - 30.0 * ph[2] + 8.0 * np.sin(3.0 * u + 0.8 * t)
                pts = np.stack([x0, y, z + 0 * u], axis=1)
                c = lin("#f6c1a8") * (1.0 - ph[0]) + lin("#e8869a") * ph[0]
                b = ribbon(pts, width=2.2 + 1.5 * ph[1], color=c, alpha=g * 0.22 * np.sin(np.pi * u) ** 1.2, emit=1.0)
                b["reflect"] = False
                out.append(b)
        lit = _ss(0.0, 1.2, t - self.wt) * (1.0 - _sc(206.0, 220.0, t) * 0.4)
        if t > 29.0:
            out.append(dict(pos=self.win, size=0.35 + 0.4 * self.ws, color=lin("#ffcf8a"),
                            alpha=0.5 * lit * (1.0 - 0.8 * _win(t, 99.0, 102.0, 112.0, 116.0)), emit=2.0, kind="spark", twinkle=0.5, seed=self.ws, fog=0.4))
        return out or None


class Shore:
    """The small lights on both shores: the brother kindles them one by one along the left shore, the sister
    warms one flickering light on the right; at the thanksgiving they rise as lights released to Mother."""

    def __init__(self):
        n = 7
        self.left = np.stack([np.linspace(-4.2, -9.8, n), np.full(n, 0.06), np.linspace(-0.4, -5.5, n)], axis=1)
        self.lt = 45.0 + np.arange(n) * 1.1
        m = 7
        self.right = np.stack([np.linspace(4.4, 10.0, m), np.full(m, 0.06), np.linspace(-0.6, -5.8, m)], axis=1)
        self.rs = _rng(6).random(m)

    def sample(self, t):
        if t < 44.0 or t > 104.0:
            return None
        rise = _ss(92.0, 98.0, t)
        lift = _v(0.0, 1.0, 0.0) * (9.0 * rise ** 1.5)
        gone = 1.0 - _sc(97.0, 101.0, t)
        lk = _ss(0.0, 0.5, t - self.lt)
        L = self.left + lift
        out = [dict(pos=L, size=0.08, color=lin("#ffcf7a"), alpha=(0.12 + 0.88 * lk) * gone, emit=2.5,
                    kind="spark", twinkle=0.3, reflect=True),
               dict(pos=L, size=0.3, color=lin("#ffb45e"), alpha=0.18 * lk * gone, kind="soft")]
        warm = _sc(52.0, 55.5, t)
        flick = 0.55 + 0.45 * np.sin(17.0 * t + 6.0 * self.rs) * (1.0 - warm)
        rk = np.full(len(self.right), 1.0) * _sc(44.0, 46.0, t)
        rk[0] = flick[0] * _sc(44.0, 46.0, t) * (0.6 + 0.4 * warm)
        R = self.right + lift
        out += [dict(pos=R, size=0.10, color=lin("#ffe2b8"), alpha=rk * gone, emit=2.5, kind="spark",
                     twinkle=0.3),
                dict(pos=R, size=0.3, color=lin("#ffc8a0"), alpha=0.18 * rk * gone, kind="soft")]
        return out


class Lampstand:
    """A tall golden seven-branched lampstand of light rising from the centre of the lake; its seven lamps
    catch flame from the centre outward on the full entry."""

    def __init__(self):
        r = _rng(7)
        pts = []
        H = 6.0
        y = np.linspace(0.0, H, 700)
        pts.append(np.stack([0 * y, y, 0 * y], axis=1))
        for k, rad in enumerate((1.0, 2.0, 3.0)):
            # each pair of branches is the lower half of a circle round the top of the stem
            a = np.linspace(np.pi, 2.0 * np.pi, 260)
            pts.append(np.stack([rad * np.cos(a), (H - 0.15) + rad * np.sin(a), 0 * a], axis=1))
            for sgn in (-1.0, 1.0):
                yy = np.linspace(H - 0.15, H, 30)
                pts.append(np.stack([np.full(30, sgn * rad), yy, np.zeros(30)], axis=1))
        foot = np.linspace(-1.0, 1.0, 120)
        pts.append(np.stack([foot, np.zeros(120) + 0.05, 0 * foot], axis=1))
        P = np.concatenate(pts)
        self.P = P + r.normal(size=P.shape) * 0.025
        self.s = r.random(len(P))
        self.cups = np.array([[x, H + 0.15, 0.0] for x in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)])
        self.light_t = M["full3"] + np.array([0.9, 0.6, 0.3, 0.0, 0.3, 0.6, 0.9])

    def sample(self, t):
        g = _win(t, M["rise3"] - 1.0, M["rise3"] + 2.5, 150.0, 160.0)
        if g <= 0.002:
            return None
        grow = _ss(M["rise3"] - 1.0, M["rise3"] + 5.0, t)
        P = self.P * np.array([1.0, grow, 1.0]) + LAMP
        out = [dict(pos=P, size=0.05 + 0.04 * self.s, color=lin("#ffc864"), alpha=g * 0.8, emit=1.6,
                    kind="spark", twinkle=0.5, seed=self.s)]
        fl = _ss(0.0, 0.6, t - self.light_t) * g
        if fl.max() > 0.0:
            C = self.cups + LAMP + _v(0.0, 0.12 * np.sin(9.0 * t), 0.0)
            out += [dict(pos=C, size=0.32, color=lin("#ffe0a0"), alpha=fl, emit=4.0, kind="spark", lod=False),
                    dict(pos=C, size=2.6, color=lin("#ffb64a"), alpha=0.12 * fl, kind="soft", lod=False)]
        return out


class Linen:
    """Fine linen clean and bright: the lampstand's light becomes a vast sheet that unfurls across the sky,
    a satin sheen gliding over it; good deeds rise as gold points and stay on it; later the sapphire, crimson
    and gold threads embroider it, and on the final chord it parts at the centre on the heavenly light."""

    def __init__(self):
        r = _rng(8)
        nu, nv = 150, 46
        u, v = np.meshgrid(np.linspace(-1.0, 1.0, nu), np.linspace(0.0, 1.0, nv))
        self.u = u.ravel() + r.normal(size=u.size) * 0.002
        self.v = v.ravel()
        self.s = r.random(self.u.size)
        # embroidery: vines with loops and pomegranates, stitched from both sides toward the centre
        threads = []
        cols = []
        births = []
        for k, (c, y0, amp, ph) in enumerate((("#3d5fd9", 0.28, 0.07, 0.0), ("#c8364b", 0.48, 0.08, 1.7),
                                               ("#ffc84a", 0.68, 0.06, 3.1), ("#3d5fd9", 0.84, 0.05, 4.2),
                                               ("#c8364b", 0.14, 0.05, 2.4))):
            for side in (-1.0, 1.0):
                s = np.linspace(0.0, 1.0, 2200)
                uu = side * (1.0 - s * 0.98)
                vv = y0 + amp * np.sin(3.0 * np.pi * s + ph)
                # a gentle curl of the vine at every crest
                cr = 0.022 * np.exp(-((np.mod(1.5 * s + ph / (2 * np.pi), 1.0) - 0.5) / 0.08) ** 2)
                uu = uu + cr * side * np.cos(40.0 * np.pi * s)
                vv = vv + cr * np.sin(40.0 * np.pi * s)
                threads.append(np.stack([uu, vv], axis=1))
                cols.append(np.tile(lin(c), (s.size, 1)))
                t0 = 152.0 + 6.0 * k
                births.append(t0 + s * 34.0)
        self.th = np.concatenate(threads)
        self.tc = np.concatenate(cols)
        self.tb = np.concatenate(births)
        self.ts = r.random(len(self.th))
        # pomegranates: small rings of gold at the crests of the vines
        self.ga = np.linspace(0.0, 2.0 * np.pi, 24, endpoint=False)
        self.deeds_xy = np.stack([-1.0 + 2.0 * r.random(160), 0.05 + 0.9 * r.random(160)], axis=1)
        self.deeds_t = 141.0 + 9.0 * r.random(160)
        self.deeds_from = np.stack([-60.0 + 120.0 * r.random(160), np.zeros(160) + 0.2,
                                    -10.0 - 60.0 * r.random(160)], axis=1)

    def where(self, u, v, t):
        """The sheet in the sky: u -1..1 across, v 0..1 bottom to top; it ripples like a sail."""
        x = 150.0 * u
        y = 22.0 + 70.0 * v + 3.0 * np.sin(2.2 * u + 0.35 * t) * np.sin(np.pi * v)
        z = -140.0 + 20.0 * (1.0 - u * u) + 6.0 * np.sin(1.7 * v + 0.5 * t + 2.0 * u)
        return np.stack([x, y, z], axis=-1)

    def part(self, u, t):
        """How far the curtain has parted at the centre on the final chord (outward shift of u)."""
        o = _ss(M["chord"] - 0.6, M["chord"] + 5.0, t)
        return u + np.sign(u) * 0.62 * o * np.clip(1.0 - np.abs(u), 0.0, 1.0) ** 0.35

    def sample(self, t):
        g = _win(t, 132.5, 140.0, 206.0, 221.0)
        if g <= 0.002:
            return None
        unf = _ss(132.5, 141.0, t)
        u = self.part(self.u, t)
        show = (np.abs(self.u) < unf + 0.02).astype(np.float64)
        P = self.where(u, self.v, t)
        sheen = np.exp(-((self.u - (-1.4 + 2.8 * np.mod((t - 133.0) / 11.0, 1.0))) / 0.18) ** 2)
        edge = np.sin(np.pi * np.clip(self.v, 0, 1)) ** 1.5 * np.clip(1.0 - np.abs(self.u), 0.0, 1.0) ** 0.7
        a = g * show * (0.012 + 0.07 * sheen) * edge * (1.0 - 0.6 * _sc(195.0, 210.0, t))
        # the sheet itself is only a fine shimmer of light points; the sheen glides across it
        a = a * 3.0 * (self.s > 0.55)
        out = [dict(pos=P, size=0.16 + 0.12 * self.s, color=lin("#fff0d8"), alpha=a, emit=1.8, kind="spark",
                    reflect=False, fog=0.2, twinkle=0.7, seed=self.s)]
        # the good deeds: gold points rise from the shores and the windows and stay on the linen
        dk = _ss(0.0, 3.0, t - self.deeds_t)
        if t > 140.0:
            dst = self.where(self.part(self.deeds_xy[:, 0], t), self.deeds_xy[:, 1], t)
            Pd = self.deeds_from + (dst - self.deeds_from) * dk[:, None]
            out.append(dict(pos=Pd, size=0.5, color=lin("#ffd068"), alpha=g * _sc(140.0, 141.0, t) * 0.9,
                            emit=2.2, kind="spark", twinkle=0.6, reflect=False))
        # the embroidery, stitched from both sides; it loosens into stars in the hold
        if t > 151.0:
            uu = self.part(self.th[:, 0], t)
            Pt = self.where(uu, self.th[:, 1], t) + _v(0.0, 0.0, 1.5)
            loose = _ss(209.0, 222.0, t)
            if loose > 0:
                rs = _rng(9).normal(size=Pt.shape)
                Pt = Pt + rs * np.array([14.0, 10.0, 6.0]) * loose + _v(0.0, 18.0 * loose, 0.0)
            out.append(dict(pos=Pt, size=0.22 + 0.12 * self.ts, color=self.tc * 1.3, alpha=g * 0.7,
                            birth=self.tb, fade=0.5, flash=3.0, emit=1.8, kind="spark", twinkle=0.35,
                            seed=self.ts, reflect=False, fog=0.15))
            # the needle points of light that lead each thread
            needles = []
            for k in range(len(self.tb) // 2200):
                sl = slice(k * 2200, (k + 1) * 2200)
                b = self.tb[sl]
                if b[0] <= t <= b[-1]:
                    i = int(np.searchsorted(b, t))
                    needles.append(Pt[sl][min(i, 2199)])
            if needles:
                out.append(dict(pos=np.array(needles), size=0.9, color=lin("#fff6e4"), alpha=g, emit=5.0,
                                kind="spark", lod=False, reflect=False))
        return out


class HeavenLight:
    """The heavenly light: Mother's answer to the thanksgiving flowing down as a warm gold wave, and on the
    final chord the light that pours through the opened curtain and floods over the lake."""

    def __init__(self):
        r = _rng(11)
        self.n = 3000
        self.s = r.random((self.n, 3))
        k = 1400
        v = r.random((k, 3))
        gx = (v[:, 0] - 0.5) * 2.0
        self.gate = dict(pos=np.stack([gx * 14.0 * (1.0 - 0.5 * np.abs(gx)), 24.0 + 62.0 * v[:, 1], 6.0 * v[:, 2]], 1),
                         size=2.0 + 4.0 * v[:, 2], a=(1.0 - np.abs(gx)) ** 1.5, seed=v[:, 2])
        e = r.random((600, 2))
        side = np.where(e[:, 0] > 0.5, 1.0, -1.0)
        self.gate["edge"] = np.stack([side * (16.0 + 2.0 * e[:, 1]), 24.0 + 62.0 * e[:, 1],
                                      np.zeros(600)], 1)
        self.gate["eseed"] = e[:, 1]

    def sample(self, t):
        out = []
        wave = _win(t, 89.5, 92.0, 96.5, 99.0)
        if wave > 0.002:
            s = self.s
            u = np.clip((t - 89.5) / 8.0, 0.0, 1.0)
            x = -14.0 + 28.0 * s[:, 0]
            z = -60.0 + 50.0 * u - 6.0 * s[:, 1]
            y = 0.6 + 7.0 * s[:, 2] * (1.0 - 0.6 * u)
            out.append(dict(pos=np.stack([x, y, z], axis=1), size=0.25 + 0.3 * s[:, 2], color=lin("#ffc86a"),
                            alpha=0.30 * wave * s[:, 0], emit=1.5, kind="soft", twinkle=0.4, seed=s[:, 1], reflect=False,
                            dof=0.0))
            out.append(dict(pos=_v(0.0, 6.0, -30.0)[None, :], size=40.0, color=lin("#f2b25e"),
                            alpha=0.16 * wave, kind="soft", lod=False, dof=0.0, fog=0.0, reflect=False))
        flood = _ss(M["chord"] - 0.4, M["chord"] + 3.5, t) * (1.0 - _sc(206.0, 215.0, t))
        if flood > 0.002:
            out.append(dict(pos=_v(0.0, 30.0, -142.0)[None, :], size=70.0 + 70.0 * flood,
                            color=lin("#ffd9a0"), alpha=0.16 * flood, kind="soft", lod=False, dof=0.0, fog=0.0,
                            reflect=False))
            # the gate of light: a tall warm column where the curtain has parted, gold edges either side
            g = self.gate
            out.append(dict(pos=g["pos"] * _v(0.6 + 1.2 * flood, 1.0, 1.0) + _v(0.0, 0.0, -141.0),
                            size=g["size"] * 1.8, color=lin("#ffd29a"), alpha=0.16 * flood * g["a"], emit=1.3, kind="soft",
                            twinkle=0.3, seed=g["seed"], reflect=False, fog=0.0))
            out.append(dict(pos=g["edge"] * _v(1.0 + 0.9 * flood, 1.0, 1.0) + _v(0.0, 0.0, -140.0),
                            size=0.5, color=lin("#ffc864"), alpha=0.45 * flood * (1.0 - 0.9 * _sc(206.0, 214.0, t)),
                            emit=2.5, kind="spark",
                            twinkle=0.6, seed=g["eseed"], reflect=False, fog=0.0))
        return out or None


# ---------------------------------------------------------------------------------------------------------
# The people of light (Claude Final v1 bodies in the Revision 3 warm gold glitter)
# ---------------------------------------------------------------------------------------------------------
_BODIES = {}
GLITTER = dict(look=dict(name="glitter", seams=0.6), bright=1.45)


def _bodies():
    if _BODIES:
        return _BODIES
    # the brother of light (the prince): kindles the lights of the left shore, then praises the sister's
    # work with an open hand; at the meeting he walks to the centre and bows; at the thanksgiving he bows
    # toward the horizon star.
    _BODIES["brother"] = Body(
        # the walk carries the body itself (speed in metres a second along the facing), so the place is
        # only where he starts: 2.3 m along the shore (44.5 to 51), then 2.5 m to the meeting (73 to 77)
        "man", at=(-1.3, 0.2),
        facing=[(44.0, 240.0), (55.5, 240.0), (57.5, 100.0), (73.0, 100.0), (73.6, 90.0), (79.5, 90.0),
                (81.5, 160.0), (100.0, 160.0)],
        motion=[(43.0, "stand"), (44.5, "walk", dict(speed=0.35)), (51.0, "stand"), (73.0, "walk", dict(speed=0.63)),
                (77.0, "stand")],
        gesture=[(46.0, 52.0, "reach", dict(side="R")), (59.9, 65.6, "clap", dict(period=0.62, height=0.25)),
                 (65.8, 69.6, "offer", dict(side="R")),
                 (77.4, 79.6, "greet_bow", dict(amount=1.0)), (86.6, 90.2, "hand_on_heart", dict(side="R")),
                 (90.2, 95.6, "greet_bow", dict(amount=1.3, hold=2.0))],
        garment="robe", color="#ffc664", color2="#fff0c8", points=90000, show=(43.6, 103.0), fade=1.2, seed=21.0,
        effects=[dict(kind="form", t=43.6, dur=2.2)], **GLITTER)
    # the sister of light (the princess): warms one flickering light on the right shore, then lays a hand on
    # her heart and returns the honour; at the meeting she walks to the centre and bows.
    _BODIES["sister"] = Body(
        "woman", at=(RIGHT[0], RIGHT[2]),
        facing=[(44.0, 200.0), (55.0, 200.0), (57.5, 260.0), (73.0, 260.0), (73.6, 270.0), (79.5, 270.0),
                (81.5, 200.0), (100.0, 200.0)],
        motion=[(43.0, "stand"), (49.5, "kneel"), (55.0, "stand"), (73.0, "walk", dict(speed=0.59)), (77.0, "stand")],
        gesture=[(49.8, 54.5, "cup"), (60.2, 63.4, "hand_on_heart", dict(side="R")),
                 (63.6, 69.4, "clap", dict(period=0.66, height=0.25)),
                 (77.4, 79.6, "greet_bow", dict(amount=1.0)), (86.8, 90.4, "hand_on_heart", dict(side="R")),
                 (90.4, 95.8, "greet_bow", dict(amount=1.3, hold=2.0))],
        garment="robe", veil=True, color="#f2a640", color2="#ffdc96", points=90000, show=(43.6, 103.0), fade=1.2,
        seed=22.0, effects=[dict(kind="form", t=43.6, dur=2.2)], **GLITTER)
    # Heavenly Mother at the horizon, seen only from behind, arms slowly opening to receive a returning soul
    _BODIES["mother"] = Body(
        "woman", at=(MOTHER[0], MOTHER[2]), facing=180.0, motion="stand",
        gesture=[(102.0, 116.0, "open_arms")], garment="robe", veil=dict(length=1.5, wide=1.2),
        color="#ffd690", color2="#fff4e0", points=110000, scale=11.0, show=(100.5, 116.5), fade=2.5, seed=23.0,
        look=dict(name="glitter", seams=0.6), bright=1.2)
    return _BODIES


class Soul:
    """One small light low over the dark water, travelling home into Mother's arms (on the hit at 1:49.2)."""

    def sample(self, t):
        if t < 102.5 or t > 113.0:
            return None
        u = _soft((t - 103.0) / (M["hit2"] - 103.0))
        dst = MOTHER + _v(0.0, 12.0, 2.0)
        src = _v(-6.0, 0.8, 8.0)
        p = src + (dst - src) * u + _v(0.0, 2.5 * np.sin(np.pi * u), 0.0)
        a = _sc(102.5, 103.5, t) * (1.0 - _sc(M["hit2"] + 0.2, M["hit2"] + 1.4, t))
        bloom = np.exp(-max(t - M["hit2"], 0.0) / 1.6) * float(t > M["hit2"])
        out = [dict(pos=p[None, :], size=0.45 + 1.2 * u, color=lin("#fff2d8"), alpha=a, emit=7.0, kind="spark",
                    lod=False),
               dict(pos=p[None, :], size=2.5 + 8.0 * u, color=lin("#ffd8a0"), alpha=0.18 * a, kind="soft", lod=False)]
        if bloom > 0.01:
            out.append(dict(pos=dst[None, :], size=40.0, color=lin("#ffd8a0"), alpha=0.25 * bloom, kind="soft",
                            lod=False, dof=0.0))
        return out


def _congregation():
    from nine_reference_p3d.crowd import Crowd
    common = dict(kinds=(("light", 1.0), ("heart", 0.6), ("bow", 0.6)), color="#ffc664", color2="#fff0c8",
                  points=5200, start=dict(t=85.0, center=(0.0, -2.0), speed=7.0),
                  act=dict(t=89.0, center=(0.0, -2.0), speed=5.0), until=101.5, fade=1.4, seed=31,
                  light="#ffcf8a", people=dict(woman=1, man=1, elder=0.3, child=0.35))
    left = Crowd(n=18, area=dict(center=(-5.6, -6.5), radius=(0.6, 3.6)), facing=lambda x, z: 160.0, **common)
    right = Crowd(n=18, area=dict(center=(5.6, -6.5), radius=(0.6, 3.6)), facing=lambda x, z: 200.0,
                  **dict(common, seed=32))
    return left, right


SIG_BOX = (-0.05, 0.47, 0.76, 1.05)   # the signature's corner (screen 0..1, y up), with its 40 px margin


class Clear:
    """Dim the light of a point set inside the reading bounds of the words (nothing crosses a word); after
    tools/nine_colours_minor/expressions.py Clear, without that film's own near-lens cleanup."""
    wants_camera = True

    def __init__(self, inner, words, bottom=True):
        self.inner, self.words, self.bottom = inner, list(words), bottom

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = []
        for word in self.words:
            if word.t_in <= t <= word.t_out:
                x0, x1, y0, y1, front, *_ = PW.screen_box(word, cam, t)
                if front:
                    boxes.append((x0 - .03, x1 + .03, y0 - .045, y1 + .045))
        boxes.append(SIG_BOX)
        if not boxes and not self.bottom:
            return got
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            gain = np.ones(len(p))
            if self.bottom:          # the calm bottom third: nothing bright there (performers stand in front)
                gain = gain * (0.08 + 0.92 * _ss(0.27, 0.37, xy[:, 1]))
            ends = [xy]
            if b.get("pos2") is not None:
                e, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
                ends = [xy * (1 - u) + e * u for u in np.linspace(0, 1, 9)]
            for q in ends:
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / .03 + .5, 0, 1)
                    gain = np.minimum(gain, 1 - .97 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


class Hearts:
    """Small hearts of light (points on a heart's outline) released from places in an expression's colour,
    rising and swaying away: hearts drift off each expression (PHASEB 9.5). Made of sparks, since the pinned
    engine has no heart sprite."""

    def __init__(self, sources, t0, t1, color, rate=3.0, life=4.5, size=(0.16, 0.28), rise=0.55, seed=3):
        from p3d import brand  # noqa: F401
        from p3d.brand_hearts import heart_points
        r = _rng(seed)
        self.sources = sources
        self.k = max(int((t1 - t0) * rate), 1)
        self.birth = t0 + (np.arange(self.k) + 0.7 * r.random(self.k)) / rate
        self.src = r.integers(0, len(sources), self.k)
        self.s = r.random((self.k, 5))
        self.hp = heart_points(22)
        self.col = lin(color)
        self.life, self.size, self.rise = life, size, rise
        self.t0, self.t1 = t0, t1

    def gain(self, t):
        return 1.0 if self.t0 - 0.1 <= t <= self.t1 + self.life else 0.0

    def sample(self, t):
        age = t - self.birth
        on = (age > 0.0) & (age < self.life)
        if not on.any():
            return None
        pos, al = [], []
        for i in np.nonzero(on)[0]:
            a, s = age[i], self.s[i]
            src = self.sources[self.src[i]]
            base = np.asarray(src(t - a) if callable(src) else src, np.float64)
            c = base + _v((s[0] - 0.5) * 0.5 + 0.18 * np.sin(1.3 * a + 6 * s[1]), self.rise * a, (s[2] - 0.5) * 0.3)
            h = self.size[0] + (self.size[1] - self.size[0]) * s[3]
            ang = 0.35 * np.sin(0.9 * a + 5 * s[4])
            q = self.hp @ np.array([[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]])
            pos.append(c + np.stack([q[:, 0] * h, q[:, 1] * h, np.zeros(len(q))], 1))
            al.append(np.full(len(q), _sc(0.0, 0.6, a) * (1.0 - _sc(self.life - 1.4, self.life, a))))
        return dict(pos=np.concatenate(pos), size=0.035, color=self.col * 1.25, alpha=np.concatenate(al) * 0.9,
                    emit=2.6, kind="spark", twinkle=0.3, reflect=False)


def _symbols():
    from p3d import brand  # noqa: F401  (loads the symbols and hearts in their order)
    from p3d import brand_symbols as BS
    comp = BS.Constellation("Compliment", ride=(0.86, 0.60, 60.0), size=9.0, camera=_LAYOUT, t0=62.0, dur=2.0,
                            hold=6.0, out=2.0, intensity=0.5, reflect=False)
    grat = BS.Traced("Gratitude", ride=(0.12, 0.56, 60.0), size=5.0, camera=_LAYOUT, t0=89.5, dur=2.0,
                     hold=6.0, out=2.0, intensity=0.4, style="fireflies", reflect=False)
    return comp, grat


def _setup(scene):
    for name in ("_arch", "_stars"):       # no arch ellipse or star field mirrored into the calm bottom third
        e = scene._entries[name]
        scene.add(name, e.pointset, reflect=False, depth_of_field=e.depth_of_field, mask=e.mask, fog=e.fog,
                  lod=e.lod)
    words = list(WORDS)
    scene.add("seam", Clear(Seam(), words), reflect=False)
    scene.add("column", Clear(GoldColumn(), words), reflect=False)
    scene.add("rings", Clear(Rings(), words), reflect=False)
    scene.add("ribbons", Clear(Ribbons(), words))
    scene.add("shore", Clear(Shore(), words))
    scene.add("lamp", Clear(Lampstand(), words), reflect=False)
    scene.add("linen", Clear(Linen(), words), reflect=False)
    scene.add("heaven", Clear(HeavenLight(), words))
    scene.add("soul", Clear(Soul(), words))
    B = _bodies()
    for name, body in B.items():
        body.add(scene, name)
    comp, grat = _symbols()
    scene.add("symbol compliment", Clear(comp, words), reflect=False)
    scene.add("symbol gratitude", Clear(grat, words), reflect=False)
    heart = lambda b: (lambda t: B[b].where(t, "heart"))          # noqa: E731
    scene.add("hearts compliment", Clear(Hearts([heart("brother"), heart("sister")], 61.0, 70.0, COL[COMP],
                                                 rate=2.2, seed=4), words), reflect=False)
    grat_src = [heart("brother"), heart("sister")] + [_v(x, 1.4, z) for x, z in
                                                       ((-4.5, -5.0), (-6.5, -7.5), (4.5, -5.0), (6.5, -7.5))]
    scene.add("hearts gratitude", Clear(Hearts(grat_src, 89.0, 98.0, COL[GRAT], rate=4.0, seed=5), words),
              reflect=False)
    left, right = _congregation()
    scene.add("crowd left", Clear(left, words))
    scene.add("crowd right", Clear(right, words))
    WORDS.add_to(scene, reflect=False)


# ---------------------------------------------------------------------------------------------------------
# The world: the colour journey of the design, warm throughout, never black
# ---------------------------------------------------------------------------------------------------------
LOOKS = dict(
    navy=dict(base="night", sky_top="#04081a", sky_mid="#0b1530", sky_hor="#1c2a52", haze=0.35,
              haze_color="#1a2448", mist=0.18, mist_color="#1c2552", stars=1.0, milky=0.6, ripple=0.15,
              dust_color="#ffe2a8", dust_color2="#ffd0a0"),
    royal=dict(base="night", sky_top="#0a0418", sky_mid="#1c0833", sky_hor="#5a1a3c", haze=0.4,
               haze_color="#3a1438", mist=0.22, mist_color="#3a1a40", stars=0.9, milky=0.5, ripple=0.3,
               dust_color="#ffd68a", dust_color2="#ffb87a"),
    gold=dict(base="night", sky_top="#1a0c26", sky_mid="#4a2a3a", sky_hor="#c8864a", haze=0.5,
              haze_color="#8a5a3a", mist=0.32, mist_color="#7a5236", stars=0.55, milky=0.2, ripple=0.4,
              dust=0.9, dust_color="#ffd68a", dust_color2="#ffc070", water="#0a0604"),
    rose=dict(base="night", sky_top="#1a0820", sky_mid="#4a1a3a", sky_hor="#b8606a", haze=0.5,
              haze_color="#8a3a4c", mist=0.3, mist_color="#7a3a4a", stars=0.6, milky=0.3, ripple=0.35,
              dust_color="#ffd0b0", dust_color2="#f6c1a8"),
    purple=dict(base="night", sky_top="#0c0418", sky_mid="#251045", sky_hor="#5a2a5e", haze=0.4,
                haze_color="#40204e", mist=0.22, mist_color="#3c2050", stars=0.9, milky=0.6, ripple=0.06,
                dust=0.7, dust_color="#ffd690", dust_color2="#e6c8ff"),
    wedding=dict(base="night", sky_top="#160c22", sky_mid="#36223e", sky_hor="#a8785c", haze=0.32,
                 haze_color="#7a5a48", mist=0.18, mist_color="#6a4e44", stars=0.4, milky=0.2, ripple=0.15,
                 dust=0.9, dust_color="#fff0c8", dust_color2="#ffd890"),
    velvet=dict(base="night", sky_top="#0a0414", sky_mid="#1e0a30", sky_hor="#4a2048", haze=0.4,
                haze_color="#381a40", mist=0.2, mist_color="#341a44", stars=1.0, milky=0.7, ripple=0.05,
                dust=0.55, dust_color="#ffd8a0", dust_color2="#ffc8b0"),
    amber=dict(base="night", sky_top="#140a1a", sky_mid="#3a2030", sky_hor="#c87a3a", haze=0.5,
               haze_color="#8a5030", mist=0.3, mist_color="#7a4a30", stars=0.5, milky=0.2, ripple=0.2,
               dust=0.8, dust_color="#ffd08a", dust_color2="#ffb64a"),
    linen=dict(base="night", sky_top="#16122c", sky_mid="#3a3050", sky_hor="#c89878", haze=0.4,
               haze_color="#7a6058", mist=0.18, mist_color="#6a5450", stars=0.35, milky=0.1, ripple=0.2,
               dust=0.8, dust_color="#fff4e0", dust_color2="#ffe0b0"),
    embroid=dict(base="night", sky_top="#0c1034", sky_mid="#321c4a", sky_hor="#c87a62", haze=0.4,
                 haze_color="#7a4450", mist=0.18, mist_color="#6a3a48", stars=0.5, milky=0.2, ripple=0.25,
                 sun_az=180.0, sun_el=-2.0, sun_color="#ffc890", sun_int=0.32, rays=0.2,
                 dust=0.9, dust_color="#ffe0b0", dust_color2="#ffc0a0"),
    glory=dict(base="night", sky_top="#121436", sky_mid="#4a2c5c", sky_hor="#e8a878", haze=0.42,
               haze_color="#8a5e58", mist=0.2, mist_color="#7a5250", stars=0.25, milky=0.0, ripple=0.2,
               sun_az=180.0, sun_el=-1.2, sun_color="#ffd098", sun_int=0.5, rays=0.3,
               dust=1.0, dust_color="#fff0d0", dust_color2="#ffd8a8", water="#120a08"),
    hold=dict(base="night", sky_top="#141638", sky_mid="#4a325c", sky_hor="#eaae78", haze=0.42,
              haze_color="#9a6a50", mist=0.2, mist_color="#8a5a48", water="#1c120a", stars=0.45, milky=0.1, ripple=0.04,
              sun_az=180.0, sun_el=-1.5, sun_color="#ffd0a0", sun_int=0.6, rays=0.25,
              dust=0.8, dust_color="#ffe8c8", dust_color2="#ffd0a8"),
)

for _lk in LOOKS.values():
    _lk.setdefault("mirror_min", 0.10)
    _lk.setdefault("mirror", 0.42)
    _lk["dust"] = 0.35 * _lk.get("dust", 0.6)
    _lk.setdefault("floats", 0.0)
LOOKS["wedding"].update(sky_hor="#d08a48", haze_color="#9a6a3a", mist_color="#8a5a36", dust_color="#ffe2a0",
                        dust_color2="#f2b25e")

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "navy"), (3.0, "royal", 9.0), (M["full1"], "gold", 4.0), (27.0, "rose", 5.0),
          (41.0, "purple", 3.0), (74.0, "wedding", 4.0), (100.0, "velvet", 4.0), (115.0, "amber", 4.0),
          (133.0, "linen", 5.0), (150.0, "embroid", 8.0), (M["finale"], "glory", 20.0),
          (M["chord"] + 3.0, "hold", 10.0)],
    light=dict(pos=STAR, color="#ffe2b0",
               strength=Track([(0.0, 0.9), (14.0, 1.2), (60.0, 1.0), (90.0, 1.5), (100.0, 1.0), (109.2, 1.7),
                               (115.0, 1.1), (202.3, 1.35), (210.0, 1.2), (TOTAL, 1.3)]),
               size=0.9, rays=0.6),
    lights=[dict(pos=lambda t: _v(0.0, 3.0, -8.0), color="#ffd8a0",
                 strength=lambda t: 0.3 * _win(t, 84.0, 88.0, 97.0, 101.0), radius=9.0),
            dict(pos=lambda t: LAMP + _v(0.0, 6.4, 0.0), color="#ffb64a",
                 strength=lambda t: 0.8 * _win(t, M["full3"], M["full3"] + 1.5, 148.0, 156.0), radius=10.0)],
    arch=dict(lit=_arch_lit, colors=COL, span=ARCH["span"], height=ARCH["height"], z=ARCH["z"], center=_arch_center,
              line=0.7),
    react=dict(beat=0.12, level=0.15),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=M["full1"], strength=0.25, rise=0.6, fall=1.4, color="#ffe6b0", at=tuple(SEAM)),
            dict(t=M["hit2"], strength=0.2, rise=0.3, fall=1.6, color="#ffe0b0", at=tuple(MOTHER + _v(0, 12, 0))),
            dict(t=M["chord"], strength=0.12, rise=0.8, fall=2.5, color="#ffd9a0", at=tuple(SEAM))],
    motion_blur=0.25,
)

# the engine's 2D titles are not used (the signature is drawn by tools/s08_full/render.py)
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=1e9, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="", sizes=(78, 77), t0=1e9, t1=1e9 + 1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []
TITLE_HIT = 1e9
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
