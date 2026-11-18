"""Song 04, I'm Sorry, Please Forgive Me: the full concert backdrop (concert item 5, Sunday December 6).

Design: project-docs/designs/04 I'm Sorry, Please Forgive Me.md ("The Thaw"), in the approved Revision 3 look
(warm gold glitter people, cream Cormorant serif phrases with coloured capsule labels, nine coloured comets,
warm heavenly light). Timeline on the real music: project-docs/backdrops/s04-full/TIMELINE.md.

A song file for the pinned Film 10 engine (commit d928ff9), loaded by tools/s04_full/render.py. The people
and the words come from Claude Final v1 (commit f43f451, package nine_reference_p3d), exactly as the
approved promo does (tools/nine_colours_minor/respect.py and expressions.py).

THE STORY (song seconds; 0 is the first sample of the reference audio, music ends 219.4, hold to 234.43)
    0      a frosted pearl morning lake, a low sun in haze, a thin line of light dividing the ice
    3.5    the title, melted out of the ice light, rests, then fades (no other text but the three words)
    16     two sisters of gold light form, one on each side of the line, half turned from each other
    31     the first one turns, sees her sister, lays a hand on her heart
    40.5   APOLOGY: she offers both open hands toward her sister (nothing else moves)
    52     she crosses first, warm pools melting under each step; she offers her hand
    61     she kneels, head bowed; the line in the ice fills with gold
    75     chorus 1: she rises; the two stand hand in hand facing the low sun; a golden breath of light rolls
           across the ice from the sun (Heavenly Mother's love, only as light) and gathers round them; the
           ice melts in a wide circle; a gold path runs from them to the horizon
    102    the drop: they dissolve into sparks; the camera glides round to the other side
    105.5  verse 2, the same story from the hurt sister's side. GRATITUDE: she lays a hand on her heart as her
           sister comes across to her
    117    the embrace. INCLUSIVENESS ("It's okay. I understand.") while they hold each other
    146    final chorus: the whole lake thaws; the two stand hand in hand on the gold path; lanterns rise;
           people of light gather on the water round them
    203    everyone dissolves into sparks that rise, the sisters last; one small warm light stays on the water
    219.4  calm warm hold, gently alive, never black
"""
import sys

import numpy as np

sys.modules.setdefault("song04", sys.modules[__name__])   # people.py reads this module by that name
import songs.s03_original as _base

MUSIC_END = 219.43            # the reference audio (SHA-256 a1fa529d...) is 219.43 s
HOLD = 15.0
TOTAL = 7033 / 30.0           # 234.433 s = 7033 frames at 30 fps (music, then 15 s of calm)
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_END
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # never a fade to black
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                  # the old 2D phrases are off
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

import theme  # noqa: E402,F401
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

import reference  # noqa: E402,F401  (tools/nine_colours_minor: registers nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401  (registers the refined gestures)

AUDIO_FILE = "work/s04/s04.wav"
NFRAMES = int(round(TOTAL * FPS))
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------------------
# The music, measured on the reference (TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
T = dict(
    title=(3.5, 4.6, 11.0, 12.6),          # t_in, t_read0, t_read1, t_out
    form=16.0,                             # the sisters gather out of sparks
    see=31.0,                              # she turns and sees
    apology=(39.8, 40.8, 50.4, 51.2),
    cross=51.8, arrive=55.6,               # she walks across first
    offer=56.4, kneel=61.0, bless=64.5,    # her hand offered; she kneels; the other's hand on her head
    seam=(63.0, 74.0),                     # the line in the ice fills with gold
    chorus1=75.0, rise=75.2,
    breath=(80.0, 92.0),                   # the golden breath rolls in and gathers (loudest 1:25)
    melt1=(82.0, 96.0),                    # the first thaw: a wide circle round them
    path=(90.0, 100.0),                    # the gold path to the horizon
    drop=102.2,                            # 1:42 the music breathes: they dissolve, the camera glides
    verse2=105.0,
    gratitude=(105.2, 106.2, 115.0, 115.8),
    hug=117.4,
    inclusive=(117.0, 118.0, 127.2, 128.0),
    final=145.5,                           # 2:25.5 the final chorus
    melt2=(146.0, 162.0),
    people=(166.0, 178.0),                 # people of light gather on the water
    lanterns=(156.0, 206.0),
    peaks=(162.0, 187.0, 197.5),
    leave=(203.0, 213.0),                  # all dissolve into rising sparks, the sisters last
    end=MUSIC_END,
)
HITS = (43.5, 83.9, 142.0)

GOLD_A = ("#ffc664", "#fff0c8")      # the first sister (who apologises)
GOLD_B = ("#f2a640", "#ffdc96")      # the second sister (who was hurt): a deeper gold, rose later
ROSE = "#f6a38a"
WARM = "#fff1d8"


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


# ---------------------------------------------------------------------------------------------------------
# Geography: the lake is y = 0, the camera looks toward -z, the low sun stands a little left of centre
# ---------------------------------------------------------------------------------------------------------
SUN_AZ = 202.0
SUN_DIR = _v(np.sin(np.radians(SUN_AZ)), 0.0, np.cos(np.radians(SUN_AZ)))
A0 = _v(-1.35, 0.0, 0.0)            # the first sister's shore
B0 = _v(1.35, 0.0, 0.0)             # the second sister's shore
MEET = _v(0.75, 0.0, 0.0)           # where the first sister stops, a respectful step away
PAIR1 = _v(0.25, 0.0, 0.0)          # the two, hand in hand, chorus 1
HUB = _v(0.0, 0.0, 0.0)             # the sisters' place in verse 2 and the final chorus


# ---------------------------------------------------------------------------------------------------------
# The camera: calm, slow, centred; performers stand in front of the screen
# ---------------------------------------------------------------------------------------------------------
class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _glide(keys):
    """A path through (t, pos, target) keys, eased between keys (smooth, never a jump)."""
    ts = [k[0] for k in keys]

    def f(t):
        if t <= ts[0]:
            return keys[0][1], keys[0][2]
        if t >= ts[-1]:
            return keys[-1][1], keys[-1][2]
        i = int(np.searchsorted(ts, t, side="right")) - 1
        u = (t - ts[i]) / (ts[i + 1] - ts[i])
        u = u * u * (3.0 - 2.0 * u)
        return _lerp(keys[i][1], keys[i + 1][1], u), _lerp(keys[i][2], keys[i + 1][2], u)
    return f


def _orbit(t0, t1, a0, a1, r0, r1, h0, h1, look0, look1, c=HUB):
    def f(t):
        u = _sc(t0, t1, t)
        a = np.radians(a0 + (a1 - a0) * u)
        r = r0 + (r1 - r0) * u
        p = np.asarray(c) + _v(np.sin(a) * r, h0 + (h1 - h0) * u, np.cos(a) * r)
        return p, _lerp(look0, look1, u)
    return f


def _k(t, x, y, z, lx, lz):
    """A camera key: the lens at (x, y, z) looking at (lx, lz) on the lake, pitched so the horizon sits a
    little below the middle of the picture (the sky behind the words, the people in the middle band)."""
    d = float(np.hypot(x - lx, z - lz))
    return (t, _v(x, y, z), _v(lx, y + 0.037 * d, lz))


CAM_KEYS = [_k(0.0, 0.0, 1.5, 22.0, 0.0, 0.0), _k(16.0, -0.2, 1.1, 15.0, 0.0, 0.0),
            _k(31.0, -0.6, 0.95, 12.0, 0.0, 0.0), _k(51.5, -0.8, 0.9, 11.0, 0.1, 0.0),
            _k(61.0, -0.3, 0.85, 9.2, 0.6, 0.0), _k(74.5, 0.0, 0.85, 9.0, 0.5, 0.0),
            _k(86.0, 0.2, 1.2, 13.0, 0.2, -2.0), _k(101.5, 0.0, 1.4, 16.0, 0.0, -3.0)]
CAM_V2 = [_k(102.2, 0.0, 1.4, 16.0, 0.0, -3.0), _k(106.5, -4.2, 0.95, 9.8, 0.3, 0.0),
          _k(117.0, -3.6, 0.9, 8.9, 0.1, 0.0), _k(129.0, -3.0, 0.9, 8.4, 0.0, 0.0),
          _k(145.0, -2.0, 1.0, 9.6, 0.0, 0.0)]
CAM_V3 = [_k(145.0, -2.0, 1.0, 9.6, 0.0, 0.0), _k(160.0, 0.0, 1.15, 11.0, 0.0, -1.0),
          _k(182.0, 0.0, 1.35, 13.5, 0.0, -1.5), _k(203.0, 0.0, 1.4, 14.0, 0.0, -2.0),
          _k(MUSIC_END, 0.0, 1.35, 14.5, 0.0, -3.0), _k(TOTAL, 0.0, 1.3, 14.0, 0.0, -3.0)]

CAMERA = Rig([
    Path(_glide(CAM_KEYS), 0.0, 102.2, blend=0.0, fov=40.0, aperture=0.012, focus="target"),
    Path(_glide(CAM_V2), 102.2, 145.0, blend=1.5, fov=40.0, aperture=0.012, focus="target"),
    Path(_glide(CAM_V3), 145.0, TOTAL, blend=1.5, fov=42.0, aperture=0.008, focus="target"),
], blend=1.5, fov=40.0, aperture=0.01, handheld=0.04, min_height=0.6)


# ---------------------------------------------------------------------------------------------------------
# The words: the three expressions in order (Apology, Gratitude, Inclusiveness), exact words.EXPRESSIONS
# wording and website colours; Claude Final v1 type (cream serif, capsule label), flat to the picture in
# the upper middle, large enough for the back of a hall, 9 to 10 s each. Plus the song title at the start.
# ---------------------------------------------------------------------------------------------------------
RIDE = (0.5, 0.665, 7.0)            # x, y (from the bottom), metres in front of the lens


def _width(frac, depth=RIDE[2], fov=40.0):
    return float(2.0 * depth * np.tan(np.radians(fov) * 0.5) * (16.0 / 9.0) * frac)


def _spec(expr, times, frac, **kw):
    t_in, r0, r1, t_out = times
    d = dict(expr=expr, ride=RIDE, face="screen", width=_width(frac), pill=True, arrive="pen", nib=False,
             leave="fade", t_in=t_in, t_read0=r0, t_read1=r1, t_out=t_out)
    d.update(kw)
    return d


_SPECS = [
    dict(label="", lines=["I’m Sorry, Please Forgive Me"], font="title", color="#ffe9c6", glow="#ffc98a",
         ride=(0.5, 0.70, 7.0), face="screen", width=_width(0.50), arrive="reveal", leave="fade",
         t_in=T["title"][0], t_read0=T["title"][1], t_read1=T["title"][2], t_out=T["title"][3], name="title"),
    _spec("Apology", T["apology"], 0.58),
    _spec("Gratitude", T["gratitude"], 0.66),
    _spec("Inclusiveness", T["inclusive"], 0.56),
]


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


WORDS = PW.Words(_SPECS, camera=CAMERA, reflect=False, drive=_clean_leave)


class Clear:
    """Dims a point set inside the reading box of any word on screen (nothing ever crosses a word)."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = []
        for word in WORDS:
            if word.t_in <= t <= word.t_out:
                x0, x1, y0, y1, front, *_ = PW.screen_box(word, cam, t)
                if front:
                    boxes.append((x0 - 0.03, x1 + 0.03, y0 - 0.05, y1 + 0.05))
        if not boxes:
            return got
        out = []
        for src in got if isinstance(got, (list, tuple)) else [got]:
            if src is None:
                continue
            b = dict(src)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            gain = np.ones(len(p))
            ends = [xy]
            if b.get("pos2") is not None:
                e, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
                ends = [xy * (1 - u) + e * u for u in np.linspace(0, 1, 7)]
            for q in ends:
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / 0.03 + 0.5, 0, 1)
                    gain = np.minimum(gain, 1 - 0.97 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1.0)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


# ---------------------------------------------------------------------------------------------------------
# The ice and its thaw
# ---------------------------------------------------------------------------------------------------------
def thaw_radius(t):
    """Metres of open water round the sisters: none, the first circle in chorus 1, back to the memory of ice
    in verse 2 (only a little), then everything in the final chorus."""
    r1 = 14.0 * _sc(T["melt1"][0], T["melt1"][1], t)
    mem = 1.0 - 0.75 * _sc(T["drop"] - 0.5, T["drop"] + 2.5, t)       # verse 2 remembers the frozen lake
    r2 = 160.0 * _sc(T["melt2"][0], T["melt2"][1], t) ** 1.6
    return max(r1 * mem, r2, 4.0 * _sc(T["hug"], T["hug"] + 10.0, t))


class Frost:
    """Frost glitter on the far ice: sparse pearl sparkles that warm and go out where the water opens. None
    in front of the people (the lower third stays calm)."""

    def __init__(self, n=9000):
        r = np.random.default_rng(41)
        x = (r.random(n) - 0.5) * 110.0
        z = -3.0 - 90.0 * r.random(n) ** 0.7
        self.p = np.stack([x, np.full(n, 0.015), z], 1)
        self.d = np.hypot(x - HUB[0], z - HUB[2])
        self.s = r.random((n, 3))

    def sample(self, t):
        R = thaw_radius(t)
        if R > 150.0:
            return None
        edge = np.clip((self.d - R) / 3.0, 0.0, 1.0)
        warm = _sc(T["chorus1"], 90.0, t) * (1.0 - 0.6 * _sc(T["drop"], T["drop"] + 3, t)) + _sc(T["final"], 160, t)
        warm = min(warm, 1.0)
        c = _lerp(lin("#f2e6ff"), lin("#ffe2b8"), warm)
        a = 0.30 * edge * (0.5 + 0.5 * self.s[:, 0]) * _sc(0.0, 3.0, t)
        keep = a > 0.01
        if not keep.any():
            return None
        return dict(pos=self.p[keep], size=0.05 + 0.06 * self.s[keep, 1], color=c, alpha=a[keep], emit=1.0,
                    kind="spark", twinkle=0.6, seed=self.s[keep, 2], reflect=False)


class Seam:
    """The thin line of light dividing the ice between the two sisters, running away to the horizon; from
    the kneeling it fills with gold from the middle out, like a mended crack, and stays as the gold path."""

    def __init__(self):
        r = np.random.default_rng(5)
        z = np.linspace(-0.6, -95.0, 240)
        x = 0.06 * np.cumsum(r.normal(size=len(z))) * 0.5
        x -= x[np.argmin(np.abs(z))]
        self.p = np.stack([x, np.full(len(z), 0.02), z], 1)
        self.z = z

    def sample(self, t):
        gold = _ss(0.0, 1.0, (t - T["seam"][0]) / (T["seam"][1] - T["seam"][0]) * 1.6 - np.abs(self.z) / 60.0)
        # verse 2 is a memory: the line cools a little, then the final chorus makes it gold for good
        gold = gold * (1.0 - 0.7 * _sc(T["drop"], T["drop"] + 2.5, t) * (1.0 - _sc(T["hug"], T["hug"] + 8, t)))
        gold = np.maximum(gold, _sc(T["final"], T["final"] + 6, t))
        cold = lin("#c9c4f2") * 0.55
        g = lin("#ffc46a") * 1.6
        col = cold[None, :] * (1 - gold)[:, None] + g[None, :] * gold[:, None]
        al = (0.45 + 0.25 * gold) * _sc(0.0, 2.0, t) * (1.0 - 0.6 * _sc(T["drop"], T["drop"] + 2.0, t)
                                                        * (1.0 - _sc(T["final"], T["final"] + 6.0, t)))
        al = al * np.clip((self.z + 95.0) / 25.0, 0, 1)
        from p3d.api import ribbon
        w = 0.03 + 0.025 * gold
        return [ribbon(self.p, width=w, color=col, alpha=al, emit=1.4)]


class Footprints:
    """Warm pools melted by the first sister's steps as she crosses first (and in verse 2, toward us)."""

    def __init__(self):
        self.a = []
        n1 = 9
        for k in range(n1):
            u = (k + 0.5) / n1
            self.a.append((_lerp(A0, MEET, u) + _v(0.0, 0.012, 0.11 * (-1) ** k), T["cross"] + 0.35 + u * 3.2))
        n2 = 8
        for k in range(n2):
            u = (k + 0.5) / n2
            self.a.append((_lerp(_v(2.1, 0, 0.0), _v(0.2, 0, 0.0), u) + _v(0.0, 0.012, 0.11 * (-1) ** k),
                           T["hug"] - 3.0 + u * 2.6))
        self.p = np.array([x[0] for x in self.a])
        self.b = np.array([x[1] for x in self.a])

    def sample(self, t):
        first = np.arange(len(self.b)) < 9
        life = np.where(first, (t < T["drop"] + 1.0), (t < T["final"] + 8.0)).astype(np.float64)
        age = t - self.b
        a = _ss(0.0, 0.6, age) * life * (1.0 - _ss(0.0, 1.5, t - np.where(first, T["drop"], T["final"] + 6)))
        if (a < 0.01).all():
            return None
        return [dict(pos=self.p, size=0.30, color=lin("#ffb46a"), alpha=0.4 * a, emit=1.0, kind="soft",
                     reflect=False),
                dict(pos=self.p + _v(0, 0.01, 0), size=0.06, color=lin("#fff0d0"), alpha=0.6 * a, emit=1.4,
                     kind="spark", reflect=False)]


class GoldPath:
    """The gold path from the sisters toward the low sun: it sets in chorus 1 and stays (a promise)."""

    def __init__(self, n=900):
        r = np.random.default_rng(9)
        u = np.sort(r.random(n))
        d = 2.0 + 110.0 * u ** 1.4
        side = (r.random(n) - 0.5) * (0.6 + 0.03 * d)
        perp = _v(-SUN_DIR[2], 0.0, SUN_DIR[0])
        self.p = HUB[None, :] + SUN_DIR[None, :] * d[:, None] + perp[None, :] * side[:, None]
        self.p[:, 1] = 0.02
        self.d = d
        self.s = r.random((n, 2))

    def sample(self, t):
        g = _sc(T["path"][0], T["path"][1], t)
        mem = 1.0 - 0.6 * _sc(T["drop"], T["drop"] + 2, t) * (1.0 - _sc(T["final"] - 2, T["final"] + 4, t))
        if g * mem <= 0.002:
            return None
        reach = 115.0 * _sc(T["path"][0], T["path"][1], t)
        a = np.clip((reach - self.d) / 6.0, 0, 1) * g * mem * 0.3 * (0.4 + 0.6 * self.s[:, 1])
        return dict(pos=self.p, size=0.05 + 0.006 * self.d, color=lin("#ffcf7a"), alpha=a, emit=1.1, kind="spark",
                    twinkle=0.6, seed=self.s[:, 0], reflect=False)


class Breath:
    """The golden breath of Heavenly Mother's love (only light, never a figure): warm mist that rolls low
    across the ice from the low sun, gathers round the two sisters like a hearth, then rises and thins."""

    def __init__(self, n=1800):
        r = np.random.default_rng(17)
        self.s = r.random((n, 6))
        self.g = r.normal(size=(n, 4))
        self.n = n

    def sample(self, t):
        t0, t1 = T["breath"]
        if t < t0 or t > t1 + 9.0:
            return None
        s, g = self.s, self.g
        delay = 3.5 * s[:, 0]
        u = np.clip((t - t0 - delay) / 5.5, 0.0, 1.0)
        u = u * u * (3 - 2 * u)
        far = HUB + SUN_DIR * 70.0
        start = far + np.stack([g[:, 0] * 6.0, 0.6 + np.abs(g[:, 1]) * 1.2, g[:, 2] * 3.0], 1)
        ang = 6.283 * s[:, 4] + 0.35 * t
        rad = np.abs(1.2 + 0.45 * g[:, 3])
        rise = _sc(t1 - 1.0, t1 + 8.0, t)
        h = 0.1 + 0.45 * np.abs(g[:, 1]) * (1 - rise) + rise * (1.0 + 3.5 * s[:, 3]) ** 1.2
        squeeze = 1 - 0.6 * rise * s[:, 3]
        cocoon = PAIR1 + np.stack([np.sin(ang) * rad * squeeze, h, np.cos(ang) * rad * squeeze], 1)
        mid = _lerp(start, cocoon, 0.5) + _v(0, 0.6, 0)
        p = (1 - u)[:, None] ** 2 * start + 2 * ((1 - u) * u)[:, None] * mid + (u * u)[:, None] * cocoon
        soft_edge = np.exp(-g[:, 3] ** 2 * 0.6) * np.exp(-np.abs(g[:, 1]) * 0.5)
        a = _ss(0.0, 0.15, u) * (1.0 - _sc(t1 + 2.0, t1 + 9.0, t)) * soft_edge * (1 - 0.7 * rise * s[:, 3])
        # fine warm motes only (soft sprites piled into a block of light): a glittering breath of gold
        return dict(pos=p, size=0.03 + 0.03 * s[:, 1], color=lin("#ffd08a"), alpha=0.5 * a, emit=1.5,
                    kind="spark", twinkle=0.7, seed=s[:, 3], reflect=True)


class Comets:
    """The nine coloured comets of Revision 3, calm for a backdrop: far up in the sky, slow wide circles,
    brighter in the choruses, quiet in the verses; they never cross a word (Clear)."""

    def __init__(self):
        r = np.random.default_rng(10)
        self.sp = r.random((9, 60, 4))
        self.r = [62.0 + 7.0 * k for k in range(9)]
        self.y = [16.0 + 3.0 * ((k * 3) % 7) for k in range(9)]
        self.w = [(0.045 + 0.006 * (k % 3)) * (1 if k % 2 == 0 else -1) for k in range(9)]
        self.a0 = [k * 0.70 for k in range(9)]
        self.c = _v(0.0, 0.0, -55.0)
        self.col = [PW.COLORS[k] for k in PW.LABELS]

    def head(self, k, t):
        a = self.a0[k] + self.w[k] * t
        return self.c + _v(np.sin(a) * self.r[k], self.y[k] + 3.0 * np.sin(0.21 * t + k), -abs(np.cos(a)) * 30.0
                           + np.cos(a) * 8.0)

    def level(self, t):
        verse = 0.38
        chorus = 0.85
        v = verse + (chorus - verse) * (_sc(73.0, 78.0, t) * (1 - _sc(101.0, 104.0, t)) + _sc(143.0, 148.0, t))
        return v * _sc(0.0, 3.0, t) * (1.0 - 0.45 * _sc(MUSIC_END, MUSIC_END + 5.0, t))

    def sample(self, t):
        from p3d.api import ribbon
        lv = self.level(t)
        out = []
        for k in range(9):
            ts = np.linspace(t - 4.0, t, 30)
            pts = np.array([self.head(k, float(x)) for x in ts])
            kk = np.linspace(0, 1, 30)
            c = lin(self.col[k])
            m = float(c.max())
            deep = m * (c / m) ** 1.35
            core = 0.35 * c + 0.65 * lin("#fff6e6")
            out.append(ribbon(pts, width=0.9 * (0.15 + 0.85 * kk), color=deep, alpha=lv * 0.5 * kk, emit=1.5))
            out.append(ribbon(pts, width=0.22 * (0.15 + 0.85 * kk), color=core, alpha=lv * 0.9 * kk, emit=2.4))
            out.append(dict(pos=pts[-1:], size=0.6, color=core, alpha=lv, emit=6.0, kind="spark"))
            out.append(dict(pos=pts[-1:], size=4.0, color=c, alpha=lv * 0.14, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * 0.5, 1.0)
            idx = (f * 29).astype(int)
            pos = pts[idx] + (sp[:, 1:4] - 0.5) * 2.0 * (1 - f)[:, None]
            out.append(dict(pos=pos, size=0.15, color=0.5 * c + 0.5 * core, alpha=lv * 0.8 * f ** 1.5, emit=2.0,
                            kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return out


class Ember:
    """One small warm light resting on the water where the sisters' joined hands dissolved, sending a gentle
    ring every few seconds (the closing frame agreed with song 05)."""

    def __init__(self):
        r = np.random.default_rng(3)
        self.ring = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        self.s = r.random(160)

    def sample(self, t):
        g = _sc(T["leave"][1] + 1.0, T["leave"][1] + 4.0, t)
        if g <= 0:
            return None
        c = HUB + _v(0.0, 0.12, 0.0)
        out = [dict(pos=c[None, :], size=0.16, color=lin("#fff0d0"), alpha=g, emit=6.0, kind="spark"),
               dict(pos=c[None, :], size=1.6, color=lin("#ffbf70"), alpha=0.35 * g, kind="soft")]
        for j in range(3):
            age = np.mod(t - 0.0 + j * 2.0, 6.0)
            rad = 0.3 + 1.1 * age
            p = np.stack([c[0] + np.sin(self.ring) * rad, np.full(160, 0.02), c[2] + np.cos(self.ring) * rad], 1)
            a = g * 0.35 * np.exp(-age / 2.0)
            out.append(dict(pos=p, size=0.05, color=lin("#ffd9a0"), alpha=a, emit=1.4, kind="spark",
                            seed=self.s, twinkle=0.3, reflect=False))
        return out


# ---------------------------------------------------------------------------------------------------------
# The world: a frosted pearl morning (warm, never cold), the golden thaw, the hurt sister's softer memory,
# the full warm morning, and the calm warm hold
# ---------------------------------------------------------------------------------------------------------
_COMMON = dict(sun_az=SUN_AZ, hills=1.0, hill_height=0.8, stars=0.0, milky=0.0, mirror=1.0, ripple=0.25,
               mirror_min=0.5, dust=0.5, bokeh=0.4, sun_size=1.4, sun_disc=4.0, exposure=0.86)
LOOKS = dict(
    frost=dict(base="night", sky_top="#1e1c4c", sky_mid="#54457c", sky_hor="#d8957f", sun_color="#ffe2c4",
               sun_el=3.2, sun_int=0.5, sun_glow=0.6, haze=0.6, haze_color="#8c6c8c", mist=0.32,
               mist_color="#90738e", water="#0c0a1c", hill_color="#2c2448", rays=0.1, clouds=0.25,
               dust_color="#f2e2ff", dust_color2="#ffdcbc", **_COMMON),
    thaw=dict(base="night", sky_top="#241c56", sky_mid="#704478", sky_hor="#ee9660", sun_color="#ffe8c8",
              sun_el=4.5, sun_int=0.68, sun_glow=0.6, haze=0.58, haze_color="#a8685e", mist=0.3,
              mist_color="#9a6260", water="#100a16", hill_color="#34224a", rays=0.3, clouds=0.3,
              dust_color="#ffe2a8", dust_color2="#ffcf9a", **_COMMON),
    memory=dict(base="night", sky_top="#211e52", sky_mid="#5e4880", sky_hor="#e09a84", sun_color="#ffe4c8",
                sun_el=3.8, sun_int=0.55, sun_glow=0.6, haze=0.6, haze_color="#906e8c", mist=0.32,
                mist_color="#94748e", water="#0c0a1a", hill_color="#2c2448", rays=0.15, clouds=0.25,
                dust_color="#ffe8cc", dust_color2="#f4dcff", **_COMMON),
    glory=dict(base="night", sky_top="#222a66", sky_mid="#7a4c7e", sky_hor="#f4a462", sun_color="#ffecd0",
               sun_el=6.0, sun_int=0.72, sun_glow=0.6, haze=0.55, haze_color="#ad6e5e", mist=0.28,
               mist_color="#a06a5e", water="#120a16", hill_color="#3a2648", rays=0.35, clouds=0.35,
               dust_color="#ffe6b0", dust_color2="#ffd09a", **_COMMON),
    hold=dict(base="night", sky_top="#222a64", sky_mid="#784c7c", sky_hor="#f0a266", sun_color="#ffeccf",
              sun_el=5.6, sun_int=0.64, sun_glow=0.6, haze=0.55, haze_color="#a86c5e", mist=0.3,
              mist_color="#9c6a5e", water="#120a16", hill_color="#382648", rays=0.25, clouds=0.3,
              dust_color="#ffe6b0", dust_color2="#ffd09a", **_COMMON),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "frost"), (T["chorus1"] + 4.0, "thaw", 8.0), (T["drop"], "memory", 3.5),
          (T["hug"], "thaw", 10.0), (T["final"], "glory", 10.0), (MUSIC_END, "hold", 6.0)],
    light=dict(pos=tuple(HUB + _v(0, 2.2, 1.5)), color="#ffe2b0",
               strength=Track([(0.0, 0.12), (T["chorus1"], 0.15), (84.0, 0.35), (100.0, 0.2), (T["final"], 0.25),
                               (170.0, 0.35), (MUSIC_END, 0.22), (TOTAL, 0.22)]), size=0.5, rays=0.0),
    lantern_field=dict(count=220, center=(0.0, -30.0), radius=(10.0, 70.0)),
    lanterns=Track([(0.0, 0.0), (T["lanterns"][0], 0.0), (T["lanterns"][0] + 6.0, 0.85),
                    (T["lanterns"][1] - 6.0, 0.85), (T["lanterns"][1] + 4.0, 0.25), (MUSIC_END + 4.0, 0.2),
                    (TOTAL, 0.2)]),
    lantern_color="#ffb45e",
    react=dict(beat=0.12, level=0.15),
)


# ---------------------------------------------------------------------------------------------------------
# The scene
# ---------------------------------------------------------------------------------------------------------
def _setup(scene):
    import people
    scene.add("frost", Frost(), reflect=False)
    scene.add("seam", Seam(), reflect=False)
    scene.add("footprints", Footprints(), reflect=False)
    scene.add("gold path", Clear(GoldPath()), reflect=False)
    for name, body in people.cast().items():
        body.add(scene, name)
    if not __import__("os").environ.get("S04_NO_BREATH"):
        scene.add("breath", Clear(Breath()))
    scene.add("comets", Clear(Comets()), reflect=False)
    scene.add("ember", Ember(), reflect=False)
    WORDS.add_to(scene)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=83.9, strength=0.2, rise=0.6, fall=1.6, color="#ffe2b0"),
            dict(t=T["drop"], strength=0.25, rise=0.5, fall=1.5, color="#ffe8cc"),
            dict(t=162.0, strength=0.18, rise=0.8, fall=1.8, color="#ffe2b0")],
    motion_blur=0.4,
)

# the old 2D closing title and tagline are off; the small signature comes from engine/titles.py
TITLE = dict(label="Healing Concert", lines=["The Words of Mother\u2019s Love"], size=150, y=0.27, label_size=48, form=1e9, hold=1e9, star=1e9,
             color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6", sizes=(78, 77), t0=1e9, t1=1e9 + 1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FORM_DUR = 3.0
FRAGMENTS = []
TITLE_HIT = 1e9
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
TITLES = dict(signature=dict(windows=[(13.0, TOTAL + 1.0, "bl", "night")], fade=1.2))
