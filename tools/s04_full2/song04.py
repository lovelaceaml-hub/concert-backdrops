"""Song 04, I'm Sorry, Please Forgive Me: the full concert backdrop, version 2 (concert item 5, December 6).

Design: project-docs/designs/04 I'm Sorry, Please Forgive Me.md ("The Thaw"). Timeline, measurements and every
choice: project-docs/backdrops/s04-full2/TIMELINE.md. Rules checked: CHECKLIST.md beside it.

A song file for the pinned Film 10 engine (commit d928ff9), loaded by tools/s04_full2/render.py, with the people
and the words of Claude Final v1 (commit f43f451, package nine_reference_p3d) exactly as the approved Revision 3
promo uses them. Time is STAGE time: 0 is the first note, the music lasts exactly 220.0 s (the live length; the
reference recording is conformed to it), then a 15 s calm hold. 60 frames a second.

THE STORY (stage seconds; lyric moments measured on the conformed reference)
    0      a frozen pale winter morning: pearl ice, ice blue sky, a low cold sun in haze; the opening lockup
    8.4    the lockup crumbles to frost dust; the small signature rests in the top left to the very end
    14     two sisters of warm gold light form far apart on the ice, half turned from each other
    27.4   "I'm sorry": the first sister turns to her sister. APOLOGY (reads 29.0 to 38.6): head bowed, open hands
           low; the words fold into star 3 (relit: a flare and one new thin ring)
    39     she crosses first (each step melts a warm pool), takes her sister's hands (41.9) and kneels (43.4):
           "truly humbled" (fragment)
    46.7   "Father and Mother opened her heart": a warm beam from the low sun; a rose flower of light opens at
           the hurt sister's heart: "opened her heart" (fragment, petals open)
    52.6   "I thank you": acted only (no words): she lays a hand on her heart
    54.8   she lifts her sister to her feet; 59.3 "to embrace me": they embrace. INCLUSIVENESS (reads 58.8 to
           67.8) while they hold each other; the words fold into star 4 (lit for the first time)
    66     the line in the ice fills with gold from the middle out (mended)
    77.5   chorus 1: the golden breath of Heavenly Mother's love (only light) rolls from the sun and gathers round
           them (loudest 85); the ice melts in a wide circle; a gold path runs to the sun; the sky warms
    103    interlude: the two side by side on the gold path; song 03's petals, freed from the ice, rise
    125    they dissolve into rings of warm light that spread across the whole lake
    129.5  verse 3 ("we all practice"): people of light form in small groups on the thawing lake (families, friends;
           only a parent with a child holds hands). "with compassion" (fragment)
    155.5  chorus 2: the full thaw: the last ice melts, lanterns rise, warm rays, apricot and rose sky
    180    "beautiful unity": everyone gathers in a wide ring round the two sisters on the gold path
    201    "one in your love" (fragment, gathered out of the ring's light)
    210.5  everyone dissolves into rising sparks, the sisters last; one small warm light rests on the water
    220    calm warm hold, gently alive (the 04 to 05 hand-off frame), to 235.0
"""
import sys

import numpy as np

sys.modules.setdefault("song04", sys.modules[__name__])   # people.py reads this module by that name
import songs.s03_original as _base

MUSIC_END = 220.0             # the live length (DESIGN-SYSTEM 4); the reference is conformed to exactly this
HOLD = 15.0
TOTAL = MUSIC_END + HOLD      # 235.0 s = 14100 frames at 60 fps
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

import theme  # noqa: E402
from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402

import reference  # noqa: E402,F401  (tools/nine_colours_minor: registers nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401  (registers the refined gestures)

AUDIO_FILE = "work/s04v2/live.wav"
NFRAMES = int(round(TOTAL * FPS))
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
SKYLINE_LANTERN = 0.0

# ---------------------------------------------------------------------------------------------------------
# The music: stage seconds, measured on the reference conformed to 220.0 s (TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
T = dict(
    op_end=10.0,                           # the opening lockup: whole 0 to 8.4, crumbled by 10.0
    sig=9.4,                               # the signature fades in (rests to the last frame)
    form=14.0,                             # the sisters gather out of frost sparks
    see=26.4,                              # she turns toward her sister ("I'm sorry" 27.4)
    apology=(28.0, 29.0, 38.6, 40.2),      # t_in, t_read0, t_read1, t_out (folded into star 3)
    cross=39.4, arrive=41.4,               # she crosses first
    offer=41.0, take=41.9,                 # "When I held her hands"
    kneel=43.4,                            # "truly humbled myself"
    f_humbled=(42.4, 43.4, 47.0, 48.0),
    beam=(46.4, 53.0),                     # "Father and Mother opened her heart"
    bless=49.0,
    f_heart=(48.6, 49.8, 53.4, 54.4),
    thank=52.6,                            # "I thank you" (acted, no words)
    rise=54.8,                             # she lifts her sister up ("you came to me first")
    swap1=(56.0, 57.6),                    # the pair re-forms for the embrace inside the warm light
    hug=59.0,                              # "to embrace me" 59.3
    inclusive=(57.8, 58.8, 67.8, 69.2),
    seam=(66.0, 77.0),                     # "when she held my hands": the line fills with gold
    chorus1=77.5,
    breath=(81.0, 93.0),                   # loudest 85
    swap2=(84.0, 86.0),                    # inside the golden breath they turn to the sun, hand in hand
    melt1=(83.0, 98.0),
    path=(90.0, 101.0),
    interlude=103.0,
    petals=(104.0, 128.0),
    leave1=(124.5, 128.5),                 # the two become rings of light across the lake
    verse3=129.5,
    people=(131.0, 152.0),
    f_comp=(145.2, 146.4, 151.0, 152.2),   # "with compassion" 146.1
    chorus2=155.5,
    melt2=(156.0, 170.0),
    lanterns=(158.0, 214.0),
    final=180.0,
    ring=(183.0, 197.0),
    f_one=(200.6, 202.0, 208.0, 209.4),    # "one in your love" 202.7 and 207.4
    leave=(210.5, 216.5),
    end=MUSIC_END,
)
HITS = (27.4, 85.0, 162.0)

GOLD_A = ("#ffb84a", "#ffe9b8")      # the first sister (who apologises): warm gold
GOLD_B = ("#f4a640", "#ffdfa0")      # the second sister (who was hurt): a slightly deeper gold, rose later
ROSE = "#f6a38a"
NAVY = "#1f2a6b"


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


def _show(h, k=1.0):
    """The linear light that shows as this display colour after the tone curve (theme.display)."""
    return theme.display(h) * k


# ---------------------------------------------------------------------------------------------------------
# Geography: the lake is y = 0, the camera looks toward -z, the low sun stands left of centre
# ---------------------------------------------------------------------------------------------------------
SUN_AZ = 200.0
SUN_DIR = _v(np.sin(np.radians(SUN_AZ)), 0.0, np.cos(np.radians(SUN_AZ)))
A0 = _v(-1.25, 0.0, 0.0)            # the first sister's place
B0 = _v(1.25, 0.0, 0.0)             # the second sister's place
MEET = _v(0.70, 0.0, 0.0)           # where the first sister stops, a respectful step away
EMB = _v(0.98, 0.0, 0.0)            # the embrace
PAIR = _v(0.55, 0.0, 0.0)           # the two side by side, chorus 1 and the interlude
HUB = _v(0.0, 0.0, 0.0)             # the centre of the ring in the last section


# ---------------------------------------------------------------------------------------------------------
# The camera: calm, slow, always moving a little; performers stand in front of the screen. A key is
# (t, position, the point looked at). The people stay in the middle band, the bottom third is calm ice or
# water, the words read above the people.
# ---------------------------------------------------------------------------------------------------------
class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _glide(keys):
    """Through (t, pos, target) keys with a smooth curve (Catmull-Rom on positions and targets, eased time)."""
    ts = np.array([k[0] for k in keys])
    P = np.array([k[1] for k in keys])
    Q = np.array([k[2] for k in keys])

    def cr(A, i, u):
        p0 = A[max(i - 1, 0)]
        p1, p2 = A[i], A[i + 1]
        p3 = A[min(i + 2, len(A) - 1)]
        u2, u3 = u * u, u * u * u
        return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2
                      + (-p0 + 3 * p1 - 3 * p2 + p3) * u3)

    def f(t):
        if t <= ts[0]:
            return P[0], Q[0]
        if t >= ts[-1]:
            return P[-1], Q[-1]
        i = int(np.searchsorted(ts, t, side="right")) - 1
        u = (t - ts[i]) / (ts[i + 1] - ts[i])
        u = u * u * (3.0 - 2.0 * u)
        return cr(P, i, u), cr(Q, i, u)
    return f


def _k(t, pos, look):
    return (t, _v(*pos), _v(*look))


def _kk(t, x, y, z, lx, lz, up=0.0):
    """A key that looks at (lx, lz) on the lake, pitched about 6.6 degrees down (the horizon high, the people in
    the middle band below the words); up tilts the view up (the opening, so the lockup sits on calm sky)."""
    dist = float(np.hypot(x - lx, z - lz))
    return (t, _v(x, y, z), _v(lx, y - (0.116 - up) * dist, lz))


CAM_KEYS = [
    _kk(0.0, 0.0, 2.6, 26.0, 0.0, 0.0, up=0.24),         # the opening: the lockup on calm sky
    _kk(8.0, 0.0, 2.6, 25.0, 0.0, 0.0, up=0.22),
    _kk(18.0, -0.2, 2.4, 14.5, 0.0, 0.0),                 # the frozen lake; the two far apart
    _kk(27.0, -0.4, 2.3, 11.5, -0.1, 0.0),
    _kk(38.0, -0.3, 2.2, 10.0, 0.2, 0.0),                 # she crosses, kneels; the heart opens
    _kk(50.0, 0.2, 2.2, 9.2, 0.7, 0.0),
    _kk(62.0, 0.6, 2.2, 9.0, 0.98, 0.0),                  # the embrace
    _kk(74.0, 0.6, 2.4, 10.0, 0.8, -0.2),
    _kk(88.0, 0.6, 2.9, 12.5, 0.45, -0.6, up=-0.04),                # chorus 1: rise and pull back, the breath
    _kk(102.0, 0.4, 3.0, 12.5, 0.4, -0.6, up=-0.05),
    _kk(116.0, -0.9, 2.9, 11.0, 0.45, -0.4, up=-0.05),              # interlude: a slow glide round
    _kk(130.0, -0.8, 3.5, 15.0, 0.1, -1.0, up=-0.08),
    _kk(152.0, -0.3, 3.9, 14.5, 0.0, -1.0, up=-0.10),               # verse 3, chorus 2: rising, centred
    _kk(176.0, 0.0, 4.2, 14.0, 0.0, -1.0, up=-0.11),
    _kk(198.0, 0.0, 4.0, 13.5, 0.0, -1.0, up=-0.105),                # the ring
    _kk(MUSIC_END, 0.0, 3.9, 14.0, 0.0, -1.2, up=-0.10),
    _kk(TOTAL, 0.0, 3.85, 14.4, 0.0, -1.2, up=-0.10),
]

CAMERA = Rig([Path(_glide(CAM_KEYS), 0.0, TOTAL, blend=0.0, fov=40.0, aperture=0.008, focus="target")],
             blend=1.0, fov=40.0, aperture=0.008, handheld=0.02, min_height=0.8)


# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights (the engine's shared arch, across the top of the sky): 3, 7 and 9 lit at the start
# (songs 01 and 03), 3 relit by the Apology, 4 lit for the first time by Inclusiveness. It sits right of the
# signature (top left) so the two never meet.
# ---------------------------------------------------------------------------------------------------------
STAR_POS = []
for _i in range(9):
    _x = 0.40 + 0.064 * _i
    _y = 0.915 - 0.045 * ((_x - 0.656) / 0.256) ** 2
    STAR_POS.append((_x, _y))


def _ph(label, star, arrive=None):
    lines = PW.EXPRESSIONS[PW.LABELS.index(label)]["lines"]      # never drawn (form and hold stay off)
    d = dict(label=label, lines=list(lines), size=100, form=1e9, hold=1e9, star=star)
    if arrive is not None:
        d["arrive"] = arrive
    return d


STAR3 = T["apology"][3] - 0.3          # the Apology's words reach star 3
STAR4 = T["inclusive"][3] - 0.3        # Inclusiveness's words reach star 4 (lit for the first time)
PHRASES = [_ph("Greeting", 1e9), _ph("Gratitude", 1e9), _ph("Apology", -100.0, [STAR3]),
           _ph("Inclusiveness", STAR4), _ph("Concession", 1e9), _ph("Respect", 1e9),
           _ph("Encouragement", -100.0), _ph("Consideration", 1e9), _ph("Compliment", -100.0)]
RINGS_AT_START = {6: 2.0}              # star 7 was lit again in songs 02 and 03: two thin rings carried over


def params(song, t):
    """The base song's per-frame values with THIS song's arch (song.py installs star_state and link_state from
    engine/arch.py into this module; the base's own params would read the base's phrases)."""
    P = _base.params(song, t)
    P["star"] = star_state(t)  # noqa: F821  (installed by song.py)
    P["link"] = link_state(t)  # noqa: F821
    P["waves"] = []
    return P


# ---------------------------------------------------------------------------------------------------------
# The words (drawn by cards04.TextFX over the finished picture): the two expressions with their exact
# words.EXPRESSIONS wording and website colours, and four short lyric fragments, each with its own effect.
# Only one text is ever on screen. y: the block's centre from the bottom (a third of the way down).
# ---------------------------------------------------------------------------------------------------------
def _expr_spec(label, times, star):
    e = PW.EXPRESSIONS[PW.LABELS.index(label)]
    t_in, r0, r1, t_out = times
    return dict(name=label, kind="expr", label=e["label"], lines=list(e["lines"]), color=e["color"], star=star,
                t_in=t_in, r0=r0, r1=r1, t_out=t_out, y=0.69, style="pen")


def _frag_spec(text, times, style, spark, y=0.69, size=72):
    t_in, r0, r1, t_out = times
    return dict(name=text, kind="frag", lines=[text], t_in=t_in, r0=r0, r1=r1, t_out=t_out, y=y, style=style,
                spark=spark, size=size)


TEXTS = [
    _expr_spec("Apology", T["apology"], 2),
    _frag_spec("truly humbled", T["f_humbled"], "bow", "#dcebff"),
    _frag_spec("opened her heart", T["f_heart"], "bloom", "#ff9fb4"),
    _expr_spec("Inclusiveness", T["inclusive"], 3),
    _frag_spec("with compassion", T["f_comp"], "ripple", "#ffd9a0"),
    _frag_spec("one in your love", T["f_one"], "gather", "#ffd9a0"),
]
TEXT_BOXES = {}          # name -> (x0, x1, y0, y1), 0..1 from the left and from the bottom (filled by cards04)


def text_boxes(t, pad=0.0):
    out = []
    for sp in TEXTS:
        if sp["t_in"] - 0.3 <= t <= sp["t_out"] + 0.6 and sp["name"] in TEXT_BOXES:
            x0, x1, y0, y1 = TEXT_BOXES[sp["name"]]
            out.append((x0 - pad, x1 + pad, y0 - pad, y1 + pad))
    return out


class Clear:
    """Dims a point set inside the reading box of any word on screen (nothing ever crosses a word), near the
    signature (top left) and in the bottom third."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = text_boxes(t, 0.035)
        out = []
        for src in got if isinstance(got, (list, tuple)) else [got]:
            if src is None:
                continue
            b = dict(src)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            gain = np.ones(len(p))
            gain = np.minimum(gain, np.clip((xy[:, 1] - 0.27) / 0.07, 0.0, 1.0))
            sig = np.clip(np.minimum((0.36 - xy[:, 0]) / 0.03, (xy[:, 1] - 0.80) / 0.03), 0.0, 1.0)
            gain = np.minimum(gain, 1.0 - 0.9 * sig)
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
    """Metres of open water round the sisters: none, the first circle in chorus 1 that keeps spreading slowly,
    then everything in chorus 2."""
    r1 = 14.0 * _sc(T["melt1"][0], T["melt1"][1], t) + 10.0 * _sc(T["melt1"][1], T["chorus2"], t)
    r2 = 170.0 * _sc(T["melt2"][0], T["melt2"][1], t) ** 1.6
    return max(r1, r2)


class Frost:
    """Frost glitter on the ice: sparse pearl sparkles that warm and go out where the water opens."""

    def __init__(self, n=9000):
        r = np.random.default_rng(41)
        x = (r.random(n) - 0.5) * 120.0
        z = -2.0 - 95.0 * r.random(n) ** 0.7
        self.p = np.stack([x, np.full(n, 0.015), z], 1)
        self.d = np.hypot(x - PAIR[0], z - PAIR[2])
        self.s = r.random((n, 3))

    def sample(self, t):
        R = thaw_radius(t)
        if R > 160.0:
            return None
        edge = np.clip((self.d - R) / 3.0, 0.0, 1.0)
        warm = min(_sc(T["chorus1"], 92.0, t) + _sc(T["chorus2"], 165.0, t), 1.0)
        c = _lerp(lin("#eef4ff"), lin("#ffe6c2"), warm)
        a = 0.40 * edge * (0.5 + 0.5 * self.s[:, 0])
        keep = a > 0.01
        if not keep.any():
            return None
        return dict(pos=self.p[keep], size=0.05 + 0.06 * self.s[keep, 1], color=c, alpha=a[keep], emit=1.2,
                    kind="spark", twinkle=0.7, seed=self.s[keep, 2], reflect=False)


class Seam:
    """The thin line of cold light dividing the ice between the two sisters, running away toward the sun;
    as she is forgiven it fills with gold from the middle out, like mended pottery, and stays gold."""

    def __init__(self):
        r = np.random.default_rng(5)
        d = np.linspace(0.3, 95.0, 260)
        mid = 0.5 * (MEET + B0)
        side = 0.05 * np.cumsum(r.normal(size=len(d))) * 0.5
        perp = _v(-SUN_DIR[2], 0.0, SUN_DIR[0])
        self.p = mid[None, :] + SUN_DIR[None, :] * d[:, None] + perp[None, :] * side[:, None]
        self.p[:, 1] = 0.02
        self.d = d

    def sample(self, t):
        gold = _ss(0.0, 1.0, (t - T["seam"][0]) / (T["seam"][1] - T["seam"][0]) * 1.6 - self.d / 60.0)
        gold = np.maximum(gold, _sc(T["chorus2"], T["chorus2"] + 6, t))
        cold = lin("#8fb4ea") * 0.9
        g = lin("#ffc46a") * 1.6
        col = cold[None, :] * (1 - gold)[:, None] + g[None, :] * gold[:, None]
        al = (0.55 + 0.25 * gold) * _sc(2.0, 6.0, t) * np.clip((95.0 - self.d) / 25.0, 0, 1)
        al = al * (1.0 - _sc(T["melt2"][1], T["melt2"][1] + 6.0, t) * (1.0 - gold))
        from p3d.api import ribbon
        w = 0.03 + 0.025 * gold
        return [ribbon(self.p, width=w, color=col, alpha=al, emit=1.4)]


class Footprints:
    """Warm pools melted by the first sister's steps as she crosses first: the picture of reaching out first."""

    def __init__(self):
        n = 7
        a = []
        for k in range(n):
            u = (k + 0.5) / n
            a.append((_lerp(A0, MEET, u) + _v(0.0, 0.012, 0.10 * (-1) ** k), T["cross"] + 0.2 + u * 1.9))
        self.p = np.array([x[0] for x in a])
        self.b = np.array([x[1] for x in a])

    def sample(self, t):
        a = _ss(0.0, 0.6, t - self.b) * (1.0 - _sc(T["hug"] + 2.0, T["hug"] + 8.0, t))
        if (a < 0.01).all():
            return None
        return [dict(pos=self.p, size=0.34, color=lin("#ffb46a"), alpha=0.45 * a, emit=1.0, kind="soft",
                     reflect=False),
                dict(pos=self.p + _v(0, 0.01, 0), size=0.07, color=lin("#fff0d0"), alpha=0.7 * a, emit=1.4,
                     kind="spark", reflect=False)]


class Beam:
    """The low warm beam from the sun that reaches the kneeling sister ("Father and Mother opened her heart"),
    and again, softer, through "her humbleness" at the end of the verse."""

    def __init__(self, n=900):
        r = np.random.default_rng(23)
        self.s = r.random((n, 4))

    def level(self, t):
        a, b = T["beam"]
        return _sc(a, a + 1.5, t) * (1.0 - _sc(b - 1.5, b + 1.0, t)) + 0.6 * _sc(71.5, 73.5, t) * (
            1.0 - _sc(T["chorus1"] + 1.0, T["chorus1"] + 4.0, t))

    def sample(self, t):
        g = self.level(t)
        if g < 0.004:
            return None
        s = self.s
        tgt = MEET + _v(0.15, 0.8, 0.0)
        src = PAIR + SUN_DIR * 80.0 + _v(0.0, 2.2, 0.0)
        u = np.mod(s[:, 0] + 0.08 * t, 1.0)
        p = _lerp(src[None, :], tgt[None, :], u[:, None]) + (s[:, 1:4] - 0.5) * (0.15 + 1.2 * (1 - u))[:, None]
        a = g * 0.35 * np.sin(np.pi * u) ** 0.5
        return dict(pos=p, size=0.05 + 0.08 * (1 - u), color=lin("#ffd28e"), alpha=a, emit=1.6, kind="spark",
                    twinkle=0.5, seed=s[:, 3], reflect=False)


class HeartFlower:
    """A small rose flower of light opening at the hurt sister's heart: her heart opens."""

    def __init__(self, n=420):
        r = np.random.default_rng(29)
        self.s = r.random((n, 4))
        self.petal = np.arange(n) % 6

    def sample(self, t):
        a0 = T["f_heart"][0] - 1.2
        g = _sc(a0, a0 + 2.5, t) * (1.0 - _sc(T["swap1"][0], T["swap1"][1], t))
        if g < 0.004:
            return None
        import people
        b = people.cast().get("sister b v1")
        heart = np.asarray(b.where(t, "heart"), np.float64) if b is not None else B0 + _v(0, 1.15, 0)
        s = self.s
        op = _sc(a0 + 0.5, a0 + 3.5, t)
        ang = self.petal * (2 * np.pi / 6) + 0.25 * t
        rr = (0.05 + 0.10 * op) * np.sqrt(s[:, 0])
        petal = np.abs(np.sin(3 * (ang + s[:, 1] * 0.5)))
        x = np.cos(ang + 0.5 * s[:, 1]) * rr * (0.4 + 0.6 * petal)
        y = np.sin(ang + 0.5 * s[:, 1]) * rr * (0.4 + 0.6 * petal)
        p = heart[None, :] + np.stack([x, y, np.full(len(x), 0.06)], 1)
        col = _lerp(lin("#9cc8ff"), lin("#ff9ab4"), op)
        return dict(pos=p, size=0.02 + 0.02 * s[:, 2], color=col, alpha=0.7 * g * (0.5 + 0.5 * s[:, 3]), emit=1.8,
                    kind="spark", twinkle=0.4, seed=s[:, 3], reflect=False)


class GoldPath:
    """The gold path from the sisters toward the low sun: it sets in chorus 1 and stays (a promise)."""

    def __init__(self, n=1000):
        r = np.random.default_rng(9)
        u = np.sort(r.random(n))
        d = 1.0 + 110.0 * u ** 1.4
        side = (r.random(n) - 0.5) * (0.6 + 0.03 * d)
        perp = _v(-SUN_DIR[2], 0.0, SUN_DIR[0])
        self.p = PAIR[None, :] + SUN_DIR[None, :] * d[:, None] + perp[None, :] * side[:, None]
        self.p[:, 1] = 0.02
        self.d = d
        self.s = r.random((n, 2))

    def sample(self, t):
        g = _sc(T["path"][0], T["path"][1], t)
        if g <= 0.002:
            return None
        reach = 115.0 * g
        a = np.clip((reach - self.d) / 6.0, 0, 1) * g * 0.32 * (0.4 + 0.6 * self.s[:, 1])
        return dict(pos=self.p, size=0.05 + 0.006 * self.d, color=lin("#ffcf7a"), alpha=a, emit=1.1, kind="spark",
                    twinkle=0.6, seed=self.s[:, 0], reflect=False)


class Breath:
    """The golden breath of Heavenly Mother's love (only light, never a figure): warm mist that rolls low
    across the ice from the low sun, gathers round the two sisters like a hearth, then rises and thins."""

    def __init__(self, n=4200):
        r = np.random.default_rng(17)
        self.s = r.random((n, 6))
        self.g = r.normal(size=(n, 4))

    def sample(self, t):
        t0, t1 = T["breath"]
        if t < t0 or t > t1 + 9.0:
            return None
        s, g = self.s, self.g
        delay = 3.5 * s[:, 0]
        u = np.clip((t - t0 - delay) / 5.5, 0.0, 1.0)
        u = u * u * (3 - 2 * u)
        far = PAIR + SUN_DIR * 70.0
        start = far + np.stack([g[:, 0] * 6.0, 0.6 + np.abs(g[:, 1]) * 1.2, g[:, 2] * 3.0], 1)
        ang = 6.283 * s[:, 4] + 0.35 * t
        rad = np.abs(1.1 + 0.4 * g[:, 3])
        rise = _sc(t1 - 1.0, t1 + 8.0, t)
        h = 0.1 + 0.5 * np.abs(g[:, 1]) * (1 - rise) + rise * (1.0 + 3.5 * s[:, 3]) ** 1.2
        squeeze = 1 - 0.6 * rise * s[:, 3]
        cocoon = PAIR + np.stack([np.sin(ang) * rad * squeeze, h, np.cos(ang) * rad * squeeze], 1)
        mid = _lerp(start, cocoon, 0.5) + _v(0, 0.6, 0)
        p = (1 - u)[:, None] ** 2 * start + 2 * ((1 - u) * u)[:, None] * mid + (u * u)[:, None] * cocoon
        soft_edge = np.exp(-g[:, 3] ** 2 * 0.6) * np.exp(-np.abs(g[:, 1]) * 0.5)
        a = _ss(0.0, 0.15, u) * (1.0 - _sc(t1 + 2.0, t1 + 9.0, t)) * soft_edge * (1 - 0.7 * rise * s[:, 3])
        glow = _sc(t0 + 3.0, t0 + 7.0, t) * (1.0 - _sc(t1, t1 + 7.0, t))
        hearth = PAIR + _v(0.0, 0.9 + 1.5 * rise, 0.0)
        return [dict(pos=p, size=0.05 + 0.06 * s[:, 1], color=lin("#ffb44a"), alpha=0.95 * a, emit=2.2,
                     kind="spark", twinkle=0.7, seed=s[:, 3], reflect=False),
                dict(pos=hearth[None, :], size=4.5, color=lin("#ffb060"), alpha=0.22 * glow, kind="soft",
                     reflect=False)]


class Petals:
    """Song 03's rose petals, frozen under the ice at the start (faint, still), freed by the thaw: they lift
    off the open water and drift up and away (the one object carried from song 03)."""

    def __init__(self, n=260):
        r = np.random.default_rng(31)
        a = r.random(n) * 2 * np.pi
        rad = 2.0 + 16.0 * np.sqrt(r.random(n))
        self.p0 = np.stack([PAIR[0] + np.sin(a) * rad, np.full(n, 0.01), PAIR[2] - 3.0 + np.cos(a) * rad * 0.8], 1)
        self.s = r.random((n, 5))
        self.free = T["petals"][0] + (T["petals"][1] - T["petals"][0] - 6.0) * self.s[:, 0]

    def sample(self, t):
        s = self.s
        age = np.maximum(t - self.free, 0.0)
        up = age * (0.25 + 0.25 * s[:, 1])
        k = np.minimum(age, 4.0) / 4.0
        sway = np.stack([np.sin(0.7 * t + 6 * s[:, 2]) * 0.5 * k, up, np.cos(0.5 * t + 6 * s[:, 3]) * 0.3 * k], 1)
        p = self.p0 + sway
        frozen = 1.0 - _ss(0.0, 1.0, age)
        a = (0.30 * frozen * (1.0 - _sc(T["melt1"][0], T["melt1"][1], t))
             + 0.75 * _ss(0.0, 1.5, age) * (1.0 - _ss(9.0, 14.0, age)))
        if (a < 0.01).all():
            return None
        col = _lerp(lin("#f7a8b8"), lin("#ffd0c0"), s[:, 4][:, None])
        return dict(pos=p, size=0.10 + 0.05 * s[:, 4], color=col, alpha=a, emit=0.9, kind="petal",
                    seed=s[:, 2], reflect=False)


class Rings:
    """Rings of warm light that spread across the lake from the two sisters as they become light at the end
    of the interlude: the thaw spreading from one heart to many."""

    def __init__(self, m=240):
        self.ang = np.linspace(0, 2 * np.pi, m, endpoint=False)
        self.s = np.random.default_rng(13).random(m)

    def sample(self, t):
        out = []
        for j in range(4):
            t0 = T["leave1"][0] + 1.0 + 1.6 * j
            age = t - t0
            if age < 0 or age > 16:
                continue
            rad = 0.5 + 3.2 * age
            a = 0.45 * np.exp(-age / 6.0) * _ss(0.0, 0.5, age)
            p = np.stack([PAIR[0] + np.sin(self.ang) * rad, np.full(len(self.ang), 0.03),
                          PAIR[2] + np.cos(self.ang) * rad], 1)
            out.append(dict(pos=p, size=0.08 + 0.01 * rad, color=lin("#ffd9a0"), alpha=a, emit=1.3, kind="spark",
                            seed=self.s, twinkle=0.3, reflect=False))
        return out or None


def Symbol(name, kind, t0, pos, size, **kw):
    """An expression's symbol (brand_symbols: the website icons redrawn as strokes) traced IN the world in its
    colour around its moment, subtle, away from the words."""
    from p3d import brand  # noqa: F401  (brand first: it imports brand_symbols itself)
    from p3d import brand_symbols as BS
    return BS.recipe(kind, name, pos=pos, size=size, t0=t0, camera=CAMERA, **kw)


class HeartDrift:
    """Small hearts in an expression's colour drifting up off its words (PHASEB 9.5), drawn as tiny heart
    outlines of sparks (this engine has no heart sprite)."""
    wants_camera = True

    def __init__(self, name, color, n=14, pts=26, seed=3):
        self.sp = [x for x in TEXTS if x["name"] == name][0]
        self.col = lin(color)
        r = np.random.default_rng(seed)
        self.s = r.random((n, 6))
        th = np.linspace(0, 2 * np.pi, pts, endpoint=False)
        self.hx = 16 * np.sin(th) ** 3 / 17.0
        self.hy = (13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)) / 17.0

    def sample(self, t, cam):
        sp = self.sp
        t0, t1 = sp["r1"] - 0.5, sp["t_out"] + 3.0
        if t < t0 or t > t1 + 6.0 or sp["name"] not in TEXT_BOXES:
            return None
        x0, x1, y0, y1 = TEXT_BOXES[sp["name"]]
        r, u, f = cam.basis()
        out_p, out_a = [], []
        for s in self.s:
            born = t0 + (t1 - t0) * s[0]
            age = t - born
            if age < 0 or age > 5.0:
                continue
            sx = x0 + (x1 - x0) * s[1]
            side = -1.0 if sx < 0.5 * (x0 + x1) else 1.0
            sx = sx + side * 0.03 * age
            sy = y1 + 0.02 + 0.045 * age
            c = PW.place(CAMERA, t, sx, sy, 7.5)
            size = 0.05 + 0.04 * s[2]
            rot = 0.4 * np.sin(1.3 * t + 6 * s[3])
            hx = self.hx * np.cos(rot) - self.hy * np.sin(rot)
            hy = self.hx * np.sin(rot) + self.hy * np.cos(rot)
            out_p.append(c[None, :] + size * (hx[:, None] * r[None, :] + hy[:, None] * u[None, :]))
            a = _ss(0.0, 0.6, age) * (1.0 - _ss(3.5, 5.0, age)) * 0.9
            out_a.append(np.full(len(hx), a))
        if not out_p:
            return None
        return dict(pos=np.concatenate(out_p), size=0.018, color=self.col, alpha=np.concatenate(out_a), emit=2.2,
                    kind="spark", reflect=False)


class Ember:
    """One small warm light resting on the water where the sisters' joined hands dissolved, sending a gentle
    ring every few seconds (the closing frame agreed with song 05)."""

    def __init__(self):
        r = np.random.default_rng(3)
        self.ring = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        self.s = r.random(160)

    def sample(self, t):
        g = _sc(T["leave"][1] - 2.0, T["leave"][1] + 1.5, t)
        if g <= 0:
            return None
        c = HUB + _v(0.0, 0.12, 0.0)
        out = [dict(pos=c[None, :], size=0.18, color=lin("#fff0d0"), alpha=g, emit=6.0, kind="spark"),
               dict(pos=c[None, :], size=1.6, color=lin("#ffbf70"), alpha=0.35 * g, kind="soft")]
        for j in range(3):
            age = np.mod(t + j * 2.0, 6.0)
            rad = 0.3 + 1.1 * age
            p = np.stack([c[0] + np.sin(self.ring) * rad, np.full(160, 0.02), c[2] + np.cos(self.ring) * rad], 1)
            a = g * 0.30 * np.exp(-age / 2.0)
            out.append(dict(pos=p, size=0.05, color=lin("#ffd9a0"), alpha=a, emit=1.4, kind="spark",
                            seed=self.s, twinkle=0.3, reflect=False))
        return out


# ---------------------------------------------------------------------------------------------------------
# The world: a frozen pale winter morning (ice blue, pearl, a low cold sun in haze, horizon high), the first
# warmth, the full warm apricot morning, the calm warm hold. Bright skies throughout, so every text is navy.
# ---------------------------------------------------------------------------------------------------------
_COMMON = dict(sun_az=SUN_AZ, hills=1.0, hill_height=0.7, stars=0.0, milky=0.0, ripple=0.0, dust=0.2,
               bokeh=0.15, sun_size=1.5, sun_disc=3.0, mist_height=1.6)


def _look(top, mid, hor, sun, hazec, hill, water, mistc, **kw):
    d = dict(base="day", sky_top=_show(top, 0.90), sky_mid=_show(mid, 0.84), sky_hor=_show(hor, 0.62),
             sun_color=_show(sun, 0.30), haze_color=_show(hazec, 0.55), hill_color=_show(hill, 0.55),
             water=_show(water, 0.42), mist_color=_show(mistc, 0.55), **_COMMON)
    d.update(kw)
    return d


LOOKS = dict(
    frost=_look("#a7c6e4", "#dbe4ee", "#f1e6e0", "#fff2e4", "#e6ecf2", "#a9bad0", "#6f8db8", "#e8eef4",
                sun_el=2.6, sun_int=0.55, sun_glow=0.7, haze=0.6, mist=0.2, mirror=0.3, mirror_min=0.2,
                rays=0.05, clouds=0.25, dust_color="#f4f8ff", dust_color2="#ffe8d0"),
    warm=_look("#92bce6", "#e8dcd8", "#f6c8a0", "#ffe2b8", "#ecd2c4", "#a0a8c4", "#5f80b2", "#ecdcd2",
               sun_el=3.6, sun_int=0.8, sun_glow=0.6, haze=0.45, mist=0.15, mirror=0.55, mirror_min=0.3,
               rays=0.35, clouds=0.3, dust_color="#fff0d8", dust_color2="#ffd8a8"),
    glory=_look("#80b2e6", "#f0d2bc", "#f7ac74", "#ffdcaa", "#ebc4ac", "#9ea2c0", "#4f74ad", "#ecd4c4",
                sun_el=5.0, sun_int=0.9, sun_glow=0.55, haze=0.42, mist=0.12, mirror=0.7, mirror_min=0.35,
                rays=0.6, clouds=0.35, dust_color="#fff0d0", dust_color2="#ffcfa0"),
    hold=_look("#86b6e8", "#f0d4c0", "#f7b07a", "#ffdeb0", "#ecc8b2", "#a0a6c2", "#5276ae", "#ecd6c8",
               sun_el=5.4, sun_int=0.85, sun_glow=0.55, haze=0.42, mist=0.12, mirror=0.7, mirror_min=0.35,
               rays=0.4, clouds=0.3, dust_color="#fff0d0", dust_color2="#ffd2a4"),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "frost"), (T["seam"][0], "frost"), (T["chorus1"] + 2.0, "warm", 14.0),
          (T["chorus2"], "glory", 14.0), (MUSIC_END - 6.0, "hold", 10.0)],
    light=dict(pos=tuple(PAIR + _v(0, 2.2, 1.5)), color="#ffe2b0",
               strength=Track([(0.0, 0.10), (T["chorus1"], 0.14), (85.0, 0.32), (100.0, 0.2), (T["chorus2"], 0.24),
                               (170.0, 0.32), (MUSIC_END, 0.2), (TOTAL, 0.2)]), size=0.5, rays=0.0),
    lantern_field=dict(count=200, center=(0.0, -30.0), radius=(10.0, 70.0)),
    lanterns=Track([(0.0, 0.0), (T["lanterns"][0], 0.0), (T["lanterns"][0] + 6.0, 0.8),
                    (T["lanterns"][1] - 6.0, 0.8), (T["lanterns"][1] + 4.0, 0.2), (MUSIC_END + 4.0, 0.15),
                    (TOTAL, 0.15)]),
    lantern_color="#ffb45e",
    react=dict(beat=0.08, level=0.12),
)


# ---------------------------------------------------------------------------------------------------------
# The scene
# ---------------------------------------------------------------------------------------------------------
def _setup(scene):
    import people
    scene.add("frost", Clear(Frost()), reflect=False)
    scene.add("seam", Seam(), reflect=False)
    scene.add("footprints", Footprints(), reflect=False)
    scene.add("petals", Clear(Petals()), reflect=False)
    scene.add("gold path", Clear(GoldPath()), reflect=False)
    scene.add("beam", Clear(Beam()), reflect=False)
    for name, body in people.cast().items():
        body.add(scene, name, reflect=False)
    scene.add("heart flower", HeartFlower(), reflect=False)
    scene.add("breath", Clear(Breath()), reflect=False)
    # the two expression symbols in the world, in their colours, subtle, beside (never over) the words
    scene.add("symbol apology", Clear(Symbol("Apology", "constellation", T["apology"][1] + 0.5,
                                             (-4.5, 4.2, -9.0), 1.6, hold=6.0, intensity=0.4, paint=0.6)),
              reflect=False)
    scene.add("symbol inclusiveness", Clear(Symbol("Inclusiveness", "petals", T["inclusive"][1] + 0.5,
                                                   (3.6, 2.6, -5.0), 1.4, hold=6.0, intensity=0.4, paint=0.6)),
              reflect=False)
    scene.add("hearts apology", HeartDrift("Apology", PW.COLORS["Apology"]), reflect=False)
    scene.add("hearts inclusiveness", HeartDrift("Inclusiveness", PW.COLORS["Inclusiveness"], seed=5), reflect=False)
    scene.add("ember", Ember(), reflect=False)


P3D = dict(
    camera=CAMERA,
    world=WORLD,
    setup=_setup,
    keep=("arch",),
    bursts=[dict(t=85.0, strength=0.12, rise=0.8, fall=1.8, color="#ffe2b0"),
            dict(t=162.0, strength=0.12, rise=0.8, fall=1.8, color="#ffe2b0")],
    motion_blur=0.4,
)

# the old 2D closing title and tagline are off; the opening lockup and the signature are cards04.py
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=1e9, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Healing Concert", sizes=(78, 77), t0=1e9, t1=1e9 + 1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FORM_DUR = 3.0
FRAGMENTS = []
TITLE_HIT = 1e9
NINTH = 1e9
CREDIT = _base.CREDIT
WAVES = []
SONG_TITLE = "I’m Sorry, Please Forgive Me"
TITLES = dict(opening=dict(t_end=T["op_end"], y=0.40, palette="day", dissolve=1.6),
              signature=dict(windows=[(T["sig"], TOTAL + 1.0, "tl", "day")], fade=1.2))
