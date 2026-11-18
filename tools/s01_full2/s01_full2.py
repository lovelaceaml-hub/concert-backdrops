"""Song 01, All You Stars of Zion: the full-length concert backdrop (pilot), on the church brass ensemble
recording (187.97 s, B-flat major) plus a 15 s calm morning hold: 203 s at 30 fps.

Built on the approved Nine Colours Revision 3 look: the pinned Film 10 engine (worlds, comets, glow, lake)
with Claude Final v1's cream serif phrases and coloured capsule labels and gold glitter people. The approved
promo files are not changed; this file is read into the pinned engine by tools/backdrop_s01/s01_render.py.

THE STORY: from starlight to sunrise (owner approved timeline, 2026-11-18; times refined to the measured
onsets: 7.11, 30.60, 77.18, 87.33, 106.39, 125.04, 131.54, 141.48, 147.77, 177.35)
  0      soft opening: a luminous starry lake, warm, a gold morning star on the horizon, nine dim seeds
  7.11   first brass hit: the title forms as a constellation; the arch of nine lights draws at about 11
  19.5   the title settles into the small signature; the nine coloured comets begin to fall
  25.5   they land on the shore as gold glitter people; the morning star flares on 30.60
  38     COMPLIMENT acted by two young women; words fully readable 42 to 52
  55     breath: the lake stills to a mirror; Compliment's star lights in the arch
  58     chorus: "like a torch"; the flame passes hand to hand; torches lift; beams of glory lean toward
         Heavenly Mother, far on the shore and seen only from behind; the sky flushes rose gold
  84     breath: light falls gently onto every torch
  87.33  chorus again: the young people walk out on the lake; peak 99 to 103: light spreads over the whole
         world and a golden net of light lands
  113    quiet interlude: blue hour, close on the shore, "dew of the dawn" written in light
  125    the tree of life grows from the dew; blossoms drift on the 141.48 hit
  147.77 the sun rises and "Arise" stands up out of the lake
  156    ENCOURAGEMENT acted, one young man helps another rise; words fully readable 161 to 172
  175    breath: the words become Encouragement's star in the arch
  177.35 final fanfare: the torch flames lift as sparks to the arch (the music fades from 183)
  188    calm radiant morning hold to 203: two lit stars, a still lake, gently alive. Never black.

Backdrop rules: calm camera (performers stand in front), calm bottom third, expression phrases readable from
the back of the hall, small signature, no lyrics beyond the three short fragments, same-gender touching,
no faces in detail, warm and never dark, no heavenly city.
"""
import numpy as np

import songs.s03_original as _base

TOTAL = 203.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 188.0
_base.SONG_END = 188.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d.api import ribbon  # noqa: E402
from p3d.camera import Move, Rig, fly  # noqa: E402

import reference  # noqa: E402,F401  (Claude Final v1 as the package nine_reference_p3d)
from nine_reference_p3d import words as CPW  # noqa: E402
from nine_reference_p3d import master_acting  # noqa: E402,F401  (registers the refined gestures)
from nine_reference_p3d import master_fx as FX  # noqa: E402

AUDIO_FILE = "s01-ensemble.mp3"            # kept in Drive only; tools/backdrop_s01/s01_prepare.py
TOTAL = 203.0
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = 188.0
SONG_END = 188.0
BOTTOM_CALM = 0.7                         # performers stand in front of the bottom third
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# measured on the ensemble recording (engine/analyze.py onsets)
HIT = dict(open=7.11, lift=30.60, c1=77.18, c2=87.33, run=106.39, tree=125.04, bloom=131.54, drift=141.48,
           sun=147.77, fan=177.35)

LABELS = CPW.LABELS
COL = [CPW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
GOLD, GOLD2 = "#ffc664", "#fff0c8"
CREAM = "#fff1dc"


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(a, b, c, d, t):
    """0 before a, rising to 1 at b, holding, falling to 0 from c to d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0). The camera looks toward -z, the sun rises at azimuth 180.
# ---------------------------------------------------------------------------------------------------------
MSTAR = _v(110.0, 4.0, -700.0)           # the morning star on the horizon
MOTHER_AT = _v(4.5, 0.0, -16.0)           # Heavenly Mother, far on the shore, seen only from behind
TREE_AT = _v(-9.0, 0.0, -17.0)             # where the dew falls and the tree of life grows
ARCH_GEO = dict(span=96.0, height=30.0, z=-70.0, center=(0.0, 2.0, 0.0))
LIT_AT = {COMP: 58.0, ENC: 177.0}         # the words lane hands off here         # the two stars this song lights


def arch_homes(t=0.0):
    th = np.radians(np.linspace(172.0, 8.0, 9))
    c = np.asarray(ARCH_GEO["center"], np.float64)
    return np.stack([c[0] + 0.5 * ARCH_GEO["span"] * np.cos(th), c[1] + ARCH_GEO["height"] * np.sin(th),
                     np.full(9, c[2] + ARCH_GEO["z"])], axis=1)


READS = [(42.0, 52.0), (62.0, 67.0), (117.0, 122.0), (147.8, 151.8), (161.0, 171.0)]   # words lane times


def _reading(t):
    return max(_win(a - 1.5, a, b, b + 1.5, t) for a, b in READS)


def arch_line(t):
    return (0.9 * _sc(10.6, 13.2, t) - 0.3 * _sc(14.0, 17.0, t)) * (1.0 - 0.8 * _reading(t))


def arch_states(t):
    """Nine (brightness, age): dim seeds from frame 0, a little fuller when the arch is drawn, two lit."""
    quiet = 1.0 - 0.6 * _reading(t)              # nothing bright behind words while they are read
    seed = (0.09 + 0.07 * _sc(10.6, 13.0, t)) * quiet
    out = []
    for k in range(9):
        tl = LIT_AT.get(k)
        if tl is not None and t > tl - 0.35:
            age = t - tl
            gather = min(max((age + 0.35) / 0.35, 0.0), 1.0)
            flash = 1.2 * np.exp(-max(age, 0.0) * 1.0) if age >= 0 else 0.0
            out.append((max(seed, 1.1 * gather) + flash, max(age, 0.0)))
        else:
            out.append((seed, 30.0))
    return out


# ---------------------------------------------------------------------------------------------------------
# The people of light (all warm gold glitter; Claude Final v1 bodies with the refined acting)
# ---------------------------------------------------------------------------------------------------------
LAND = 25.5                                             # the first comet lands
# name, shape, place (x, z), facing, hair, gold, landing comet
CAST_LIST = [("w1", "woman", (-0.45, 0.0), 90.0, "bun", "#ffc664", COMP),       # Compliment: she praises
        ("w2", "woman", (0.45, 0.0), 270.0, "bob", "#f2a640", RESP),       # and she is praised
        ("m1", "man", (-3.3, -1.0), 140.0, "default", "#ffcf7a", GREET),
        ("m2", "man", (3.2, -0.8), 220.0, "default", "#f6b856", CONS),
        ("w3", "woman", (-5.4, -2.6), 150.0, "long", "#ffd88a", GRAT),
        ("m3", "man", (5.6, -2.2), 210.0, "default", "#f0b050", CONC)]
LAND_T = {name: LAND + 0.62 * i for i, (name, *_r) in enumerate(CAST_LIST)}
TORCH_ORDER = ["w3", "m1", "w1", "w2", "m2", "m3"]      # the flame passes left to right
TORCH_T = {n: 59.4 + 1.15 * i for i, n in enumerate(TORCH_ORDER)}
WALK = (HIT["c2"] + 0.4, 104.0, 9.0)                    # the walk out on the lake: from, to, metres
PAIR_AT = (0.6, -2.2)                                   # Encouragement: one young man helps another rise
RISE_T = 164.6

_BODIES = {}


def _walk_keys(x, z):
    t0, t1, d = WALK
    return [(0.0, (x, z)), (t0, (x, z)), (t1, (x, z - d))]


def _bodies():
    if _BODIES:
        return _BODIES
    from nine_reference_p3d.body import Body
    from nine_reference_p3d import pairs
    common = dict(garment="dress", points=52000, look=dict(name="glitter", seams=0.6), bright=1.35, fade=0.6)
    for i, (name, shape, (x, z), facing, hair, gold, k) in enumerate(CAST_LIST):
        kw = dict(common)
        if shape == "man":
            kw.update(garment="tunic")
            hair = "default"
        t_land = LAND_T[name]
        gest = [(t_land + 1.0, 37.0, "sway", dict(period=5.0 + 0.7 * i, amount=0.5))]
        if name == "w1":           # she tells her friend her effort shows (Compliment)
            gest = [(t_land + 1.0, 38.0, "sway", dict(period=5.6, amount=0.4)),
                    (38.2, 53.5, "explain", dict(side="R", period=3.4)),
                    (45.5, 53.5, "soft_clap", dict(period=1.6, height=0.2))]
        elif name == "w2":         # her friend's word warms her: a hand on her heart
            gest = [(t_land + 1.0, 39.0, "sway", dict(period=6.1, amount=0.4)),
                    (39.6, 54.0, "hand_on_heart", dict(side="R")),
                    (40.2, 54.0, "nod", dict(period=2.8, amount=0.5))]
        # the torches: held low when lit, lifted on the chorus, lifted again on the fanfare
        tl = TORCH_T[name]
        side = "R"
        gest += [(tl - 0.6, 74.8, "offer", dict(side=side)),
                 (74.8, 113.0, "soft_raise", dict(side=side, period=6.0 + 0.5 * i)),
                 (176.6, TOTAL + 5.0, "soft_raise", dict(side=side, period=7.0 + 0.4 * i))]
        motion = [(0.0, "stand"), (WALK[0], "walk", dict(speed=WALK[2] / (WALK[1] - WALK[0]))), (WALK[1], "stand")]
        body = Body(shape, at=_walk_keys(x, z), facing=facing if name in ("w1", "w2") else
                    [(0.0, facing), (WALK[0] - 1.5, 180.0)],
                    motion=motion, hair=hair, color=gold, color2="#fff0c8", seed=20.0 + i,
                    gesture=gest, show=(t_land - 0.1, 113.5),
                    effects=[dict(kind="form", t=t_land - 0.1, dur=1.8)], **kw)
        _BODIES[name] = body
    # Heavenly Mother: far on the shore, facing the morning, seen only from behind (never a face)
    _BODIES["mother"] = Body("woman", at=(MOTHER_AT[0], MOTHER_AT[2]), facing=180.0, motion="stand", garment="robe",
                             veil=True, hair="long", look=dict(name="glitter", seams=0.4), color="#fff0d0",
                             color2="#ffffff", bright=1.7, points=60000, seed=40.0, show=(60.0, 113.0), fade=2.5,
                             gesture=[(66.0, 112.0, "open_arms", dict(amount=0.35))])
    # Encouragement: two young men; one has sunk to one knee, worn out; his friend lays a hand on his shoulder,
    # then offers his hand and helps him rise
    helper, tired = pairs.helped_up(
        RISE_T, at=PAIR_AT, facing=270.0, rise=2.0, reach=1.2,
        a=dict(shape="man", garment="tunic", look=dict(name="glitter", seams=0.6), color="#f4a838",
               color2="#ffd890", bright=1.45, points=56000, seed=50.0, show=(153.0, TOTAL + 5.0), fade=0.8,
               gesture=[(158.0, 163.2, "comfort", dict(side="L", to=lambda t: _BODIES["tired"].where(t, "shoulder.R")))],
               effects=[dict(kind="form", t=153.0, dur=2.2)]),
        b=dict(shape="man", garment="tunic", look=dict(name="glitter", seams=0.6), color="#ec9a30",
               color2="#ffd080", bright=1.4, points=56000, seed=51.0, show=(153.0, TOTAL + 5.0), fade=0.8,
               effects=[dict(kind="form", t=153.2, dur=2.2)]))
    _BODIES["helper"], _BODIES["tired"] = helper, tired
    # the morning companions round them (back again after the walk), torches low, lifted on the fanfare
    for i, (name, shape, (x, z), facing) in enumerate([("e1", "woman", (-5.4, -4.2), 120.0),
                                                       ("e2", "man", (-2.6, -5.6), 150.0),
                                                       ("e3", "woman", (4.2, -4.6), 230.0),
                                                       ("e4", "man", (6.8, -3.4), 240.0)]):
        kw = dict(common)
        kw.pop("bright")
        if shape == "man":
            kw.update(garment="tunic")
        _BODIES[name] = Body(shape, at=(x, z), facing=facing, motion="stand",
                             hair="bun" if shape == "woman" else "default",
                             color=["#f6b04a", "#f2a63c", "#eea040", "#ea9a34"][i], color2="#ffd890", bright=1.4,
                             seed=60.0 + i, show=(152.0 + 0.5 * i, TOTAL + 5.0),
                             gesture=[(153.0, 165.0, "offer", dict(side="R")),
                                      (165.0, 176.6, "soft_raise", dict(side="R", period=6.0 + i)),
                                      (176.6, TOTAL + 5.0, "soft_raise", dict(side="R", period=7.5 + 0.5 * i))],
                             effects=[dict(kind="form", t=152.0 + 0.5 * i, dur=2.0)], **kw)
    return _BODIES


def _torch_names(t):
    if t < 140.0:
        return [n for n in TORCH_ORDER]
    return ["e1", "e2", "e3", "e4", "helper", "tired"]


def _torch_tip(name, t):
    b = _bodies()[name]
    return np.asarray(b.where(t, "palm.R"), np.float64) + _v(0.0, 0.16, 0.0)


def _torch_lit(name, t):
    if name in TORCH_T:
        return _win(TORCH_T[name], TORCH_T[name] + 0.5, 112.0, 113.4, t)
    if name in ("helper", "tired"):
        on = RISE_T + 1.4 if name == "tired" else 157.0
        return _sc(on, on + 0.8, t)
    i = ["e1", "e2", "e3", "e4"].index(name)
    return _sc(153.5 + 0.5 * i, 154.5 + 0.5 * i, t)


# ---------------------------------------------------------------------------------------------------------
# The camera: calm, wide, eye level; slow drifts only (the performers stand in front of the screen)
# ---------------------------------------------------------------------------------------------------------
class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


SKYQ = _v(0.0, 14.0, -60.0)
CAM_KEYS = [
    (0.0, _v(0.0, 1.30, 19.0), _v(0.0, 13.4, -60.0)),
    (19.0, _v(0.0, 1.30, 17.2), _v(0.0, 12.6, -60.0)),
    (25.0, _v(0.3, 1.30, 12.6), _v(0.0, 10.2, -60.0)),
    (38.0, _v(0.4, 1.30, 8.6), _v(0.0, 9.8, -60.0)),
    (55.0, _v(0.1, 1.30, 8.4), _v(0.0, 9.8, -60.0)),
    (58.0, _v(0.0, 1.30, 9.0), _v(0.0, 10.0, -60.0)),
    (84.0, _v(-0.6, 1.35, 10.6), _v(0.0, 10.4, -60.0)),
    (87.3, _v(-0.6, 1.40, 10.6), _v(0.0, 10.4, -60.0)),
    (104.0, _v(0.0, 1.9, -1.0), _v(0.0, 10.0, -60.0)),
    (112.8, _v(0.4, 1.9, -1.6), _v(0.0, 10.0, -60.0)),
]
CAM_CLOSE = [
    (113.0, _v(-6.6, 0.70, -6.0), _v(-9.0, 2.6, -24.0)),
    (125.0, _v(-6.4, 0.80, -4.6), _v(-9.0, 3.2, -24.0)),
    (138.0, _v(-4.6, 1.10, 2.0), _v(-6.0, 4.6, -24.0)),
    (147.4, _v(-0.6, 1.25, 8.0), _v(-1.2, 6.0, -40.0)),
]
CAM_MORNING = [
    (147.5, _v(0.0, 1.30, 15.0), _v(0.0, 11.8, -60.0)),
    (156.0, _v(0.5, 1.30, 6.6), _v(0.4, 9.6, -60.0)),
    (175.0, _v(0.6, 1.30, 6.0), _v(0.4, 9.6, -60.0)),
    (188.0, _v(0.2, 1.35, 14.5), _v(0.0, 12.6, -60.0)),
    (TOTAL, _v(0.0, 1.35, 15.4), _v(0.0, 12.8, -60.0)),
]


def _rig(focus=None):
    return Rig([
        fly(CAM_KEYS, fov=48.0, aperture=0.0, focus=30.0),
        fly(CAM_CLOSE, blend=0.0, fov=46.0, aperture=0.012, focus=lambda t: 11.0 + 8.0 * _sc(125.0, 138.0, t)),
        fly(CAM_MORNING, blend=0.0, fov=48.0, aperture=0.0, focus=30.0),
    ], blend=1.0, fov=48.0, aperture=0.0, handheld=0.04, min_height=0.3)


CAMERA = _rig()
_LAYOUT = CAMERA


def _width(t, depth, frac):
    cam = CPW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


# ---------------------------------------------------------------------------------------------------------
# The words: the title, the two expressions (Claude Final v1 type), three short fragments
# ---------------------------------------------------------------------------------------------------------
READ = (0.5, 0.64, 7.0)                    # upper middle, flat to the picture (handbook: centred near 0.35)


def _spec(t_in, t_read0, t_read1, t_out, **kw):
    mid = 0.5 * (t_read0 + t_read1)
    frac = kw.pop("frac")
    ride = kw.pop("ride", READ)
    d = dict(ride=ride, face="screen", width=_width(mid, ride[2], frac), t_in=t_in, t_read0=t_read0,
             t_read1=t_read1, t_out=t_out, nib=False)
    d.update(kw)
    return d


_SPECS = []          # version 2: the title is the opening lockup and the signature (render.py)


def _clean_leave(t, info):
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)


def _lane_words():
    """The words lane (tools/s01_full/words.py): Compliment and Encouragement gather into their own stars of
    the arch (the real arch places, not a guess on screen), the torch letters burn, the dew is stitched in
    light, "Arise" stands up out of the lake on the 2:27.8 sunrise hit."""
    import importlib.util
    import sys as _sys
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("s01_lane_words", root / "tools/s01_full2/words.py")
    mod = importlib.util.module_from_spec(spec)
    _sys.modules["s01_lane_words"] = mod
    spec.loader.exec_module(mod)
    homes = arch_homes()
    # the morning sky behind Arise and Encouragement is bright: keep the letters' colour, a deeper glow and
    # a stronger halo so they stand out from the pale sky (see also the deeper morning looks below)
    style = {"Arise": dict(color="#ffb347", glow="#c85a10", tint=.85, bright=1.0, halo=1.9),
             "Encouragement": dict(tint=.85, bright=1.0, halo=1.9)}
    return mod.build(camera=_LAYOUT, stars={"Compliment": tuple(homes[COMP]), "Encouragement": tuple(homes[ENC])},
                     style=style, centre_y=.36, widths={"Compliment": .42, "Encouragement": .54})


_LANE = _lane_words()
_TIMES = _LANE.timeline
WORDS = CPW.Words(_SPECS + list(_LANE), camera=_LAYOUT, reflect=False, drive=_clean_leave)



# ---------------------------------------------------------------------------------------------------------
# Light: the morning star, the nine falling comets, torches, beams, the net, sparks to the arch
# ---------------------------------------------------------------------------------------------------------
class MorningStar:
    """The gold morning star on the horizon; it flares on the verse lift and fades into the sunrise."""

    def sample(self, t):
        g = 1.0 - 0.85 * _sc(147.0, 150.0, t)
        flare = 1.0 + 1.6 * np.exp(-max(t - HIT["lift"], 0.0) / 1.4) * float(t >= HIT["lift"] - 0.05)
        pulse = 1.0 + 0.06 * np.sin(1.3 * t)
        return [dict(pos=MSTAR[None, :], size=9.0 * pulse * (0.8 + 0.2 * flare), color=lin("#ffe2a0"),
                     alpha=g * min(flare, 2.2), emit=6.0, kind="spark", lod=False),
                dict(pos=MSTAR[None, :], size=110.0 * flare, color=lin("#ffc070"), alpha=0.16 * g, kind="soft",
                     lod=False, dof=0.0)]


def _bez(p0, p1, p2, p3, u):
    v = 1.0 - u
    return (v ** 3)[..., None] * p0 + (3 * v * v * u)[..., None] * p1 + (3 * v * u * u)[..., None] * p2 + \
        (u ** 3)[..., None] * p3


class FallingComets:
    """The nine coloured comets fall from the seeds of the arch to the shore; six become people."""
    T0 = 19.6

    def __init__(self):
        homes = arch_homes()
        names = [c[0] for c in CAST_LIST]
        land = {c[6]: c for c in CAST_LIST}
        self.paths = []
        for k in range(9):
            if k in land:
                name, _s, (x, z), *_r = land[k]
                end = _v(x, 0.9, z)
                t1 = LAND_T[name]
            else:          # the three others fall into the lake and wake its glints
                end = _v([-14.0, 11.0, 16.0][[CONC, RESP, ENC].index(k) if k in (CONC, RESP, ENC) else 0],
                         0.05, -16.0 - 3.0 * k)
                t1 = LAND + 0.5 + 0.5 * k
            t0 = self.T0 + 0.45 * k
            p0 = homes[k]
            p1 = p0 + _v(0.0, -8.0, 22.0)
            p2 = end + _v(0.6 * (k - 4), 10.0, -10.0)
            self.paths.append((t0, t1, p0, p1, p2, end))
        self.sp = np.random.default_rng(11).random((9, 90, 4))

    def sample(self, t):
        if t < self.T0 - 0.1 or t > LAND + 9.0:
            return None
        out = []
        for k, (t0, t1, p0, p1, p2, p3) in enumerate(self.paths):
            if t < t0 or t > t1 + 1.2:
                continue
            u_head = np.clip((t - t0) / (t1 - t0), 0.0, 1.0)
            u_head = u_head * u_head * (3.0 - 2.0 * u_head)
            us = np.linspace(max(u_head - 0.22, 0.0), u_head, 36)
            pts = _bez(p0, p1, p2, p3, us)
            fade = 1.0 - _sc(t1, t1 + 1.2, t)
            kk = np.linspace(0.0, 1.0, len(us))
            c = lin(COL[k])
            core = 0.35 * c + 0.65 * lin("#fff6e6")
            out.append(ribbon(pts, width=1.5 * (0.1 + 0.9 * kk), color=c * 1.3, alpha=0.7 * fade * kk, emit=1.8))
            out.append(ribbon(pts, width=0.35 * (0.1 + 0.9 * kk), color=core, alpha=0.95 * fade * kk, emit=2.8))
            out.append(dict(pos=pts[-1:], size=0.55, color=core, alpha=fade, emit=6.0, kind="spark"))
            out.append(dict(pos=pts[-1:], size=4.5, color=c, alpha=0.14 * fade, kind="soft"))
            sp = self.sp[k]
            f = np.mod(sp[:, 0] + t * 1.1, 1.0)
            idx = (f * (len(pts) - 1)).astype(int)
            pos = pts[idx] + (sp[:, 1:4] - 0.5) * 1.6 * (1.0 - f)[:, None]
            out.append(dict(pos=pos, size=0.08 + 0.08 * sp[:, 2], color=0.5 * c + 0.5 * core, alpha=fade * f ** 1.5,
                            emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return out or None


class Torches:
    """A small flame of light at each torch; on the chorus it passes hand to hand; beams of glory lean from the
    torches toward Heavenly Mother; on the fanfare the flames lift as sparks to the arch."""

    def __init__(self):
        r = np.random.default_rng(21)
        self.s = r.random((10, 40, 4))
        self.fs = r.random((10, 160, 4))

    def sample(self, t):
        out = []
        names = _torch_names(t)
        tops = arch_homes()
        for j, n in enumerate(names):
            lit = _torch_lit(n, t)
            if lit <= 0.002:
                continue
            tip = _torch_tip(n, t)
            s = self.s[j]
            flick = 1.0 + 0.12 * np.sin(9.0 * t + 7.0 * j) + 0.06 * np.sin(23.0 * t + j)
            rise = np.mod(s[:, 0] + t * (0.9 + 0.5 * s[:, 1]), 1.0)
            pos = tip + np.stack([(s[:, 2] - 0.5) * 0.08 * (1.0 - rise), 0.32 * rise, (s[:, 3] - 0.5) * 0.08 * (1.0 - rise)], 1)
            col = lin("#ffd890")[None] * (1.0 - rise[:, None]) + lin("#ff9a5a")[None] * rise[:, None]
            out.append(dict(pos=pos, size=0.05 * (1.0 - 0.6 * rise), color=col, alpha=lit * (1.0 - rise) * 0.9,
                            emit=3.0, kind="spark", seed=s[:, 1]))
            out.append(dict(pos=tip[None, :] + _v(0, 0.08, 0), size=0.10 * flick, color=lin("#fff2d0"), alpha=lit,
                            emit=6.0, kind="spark"))
            out.append(dict(pos=tip[None, :] + _v(0, 0.1, 0), size=1.1 * flick, color=lin("#ffb060"),
                            alpha=0.12 * lit, kind="soft"))
            # the flame passes: a little arc of light from the previous torch
            if n in TORCH_T and j > 0:
                a = TORCH_T[n] - 0.9
                u = (t - a) / 0.9
                if 0.0 <= u <= 1.25:
                    prev = _torch_tip(names[j - 1], t)
                    us = np.linspace(max(min(u, 1.0) - 0.35, 0.0), min(u, 1.0), 16)
                    mid = 0.5 * (prev + tip) + _v(0.0, 0.9, 0.0)
                    pts = ((1 - us) ** 2)[:, None] * prev + (2 * (1 - us) * us)[:, None] * mid + (us ** 2)[:, None] * tip
                    out.append(ribbon(pts, width=0.05, color=lin("#ffd890"), alpha=0.8 * (1.0 - _sc(1.0, 1.25, u)),
                                      emit=2.5))
            # the fanfare: the flames lift as sparks to the arch (Compliment and Encouragement first)
            lift = _win(HIT["fan"], HIT["fan"] + 1.0, 186.0, 189.0, t)
            if lift > 0.002:
                fs = self.fs[j]
                k = [COMP, ENC, GREET, CONS, GRAT, CONC, RESP, APOL, INCL][j % 9]
                goal = tops[k]
                f = np.mod(fs[:, 0] + (t - HIT["fan"]) * (0.10 + 0.05 * fs[:, 1]), 1.0)
                ctrl = tip + _v(0.0, 18.0 + 10.0 * fs[:, 2].mean(), -20.0)
                pos = ((1 - f) ** 2)[:, None] * tip + (2 * (1 - f) * f)[:, None] * ctrl + (f ** 2)[:, None] * goal
                pos += (fs[:, 1:4] - 0.5) * (0.3 + 3.0 * f[:, None])
                out.append(dict(pos=pos, size=0.06 + 0.25 * f, color=lin("#ffd890") * (1 - f[:, None]) +
                                lin(COL[k]) * f[:, None], alpha=lift * lit * 0.85 * np.sin(np.pi * f) ** 0.6,
                                emit=2.4, kind="spark", twinkle=0.5, seed=fs[:, 3]))
        return out or None


class Beams:
    """Chorus 1: soft beams of glory leaning from the torches toward Heavenly Mother, and her gentle light."""
    wants_camera = False

    def sample(self, t):
        beam = _win(68.0, 74.0, 82.5, 86.0, t)
        glow = _win(60.0, 63.0, 110.0, 113.0, t)
        if glow <= 0.002:
            return None
        out = [dict(pos=(MOTHER_AT + _v(0.0, 1.0, 0.0))[None], size=4.0, color=lin("#fff0d0"), alpha=0.10 * glow,
                    kind="soft", lod=False),
               dict(pos=(MOTHER_AT + _v(0.0, 1.0, 0.0))[None], size=12.0, color=lin("#ffd8a0"), alpha=0.04 * glow,
                    kind="soft", lod=False)]
        if beam > 0.002:
            goal = MOTHER_AT + _v(0.0, 7.0, -2.0)
            us = np.linspace(0.0, 1.0, 24)
            for n in TORCH_ORDER:
                tip = _torch_tip(n, t)
                lean = tip + (goal - tip) * (us ** 0.8)[:, None] + _v(0.0, 0.8, 0.0) * np.sin(np.pi * us)[:, None]
                out.append(ribbon(lean, width=0.06 + 0.5 * us, color=lin("#ffe6b8"),
                                  alpha=0.10 * beam * _torch_lit(n, t) * (1.0 - 0.85 * us), emit=1.2))
        return out


class LightFall:
    """Breath at 1:24: gentle light falling onto every torch (power and strength)."""

    def __init__(self):
        self.s = np.random.default_rng(23).random((6, 220, 3))

    def sample(self, t):
        g = _win(83.6, 84.6, 86.6, 88.0, t)
        if g <= 0.002:
            return None
        out = []
        for j, n in enumerate(TORCH_ORDER):
            tip = _torch_tip(n, t)
            s = self.s[j]
            f = np.mod(s[:, 0] + 0.45 * t, 1.0)
            pos = tip + np.stack([(s[:, 1] - 0.5) * 0.9 * f, 12.0 * f, (s[:, 2] - 0.5) * 0.9 * f], 1)
            out.append(dict(pos=pos, size=0.03 + 0.03 * s[:, 2], color=lin("#fff0c8"), alpha=g * 0.8 * (1 - f) ** 0.5,
                            emit=2.4, kind="spark", twinkle=0.4, seed=s[:, 1]))
            out.append(dict(pos=(tip + _v(0, 5.0, 0))[None], size=_v(0, 0, 0)[0] + 0.9, color=lin("#fff0c8"),
                            alpha=0.03 * g, kind="soft"))
        return out


class GoldenNet:
    """At the peak a golden net of light drifts down far ahead and settles on the lake: fine irregular threads
    with glints at the knots, lit where it lands (light spreading to the whole world)."""

    def __init__(self, n=20, size=64.0):
        r = np.random.default_rng(17)
        u = np.linspace(-0.5, 0.5, n) * size
        X, Z = np.meshgrid(u, u)
        self.x = X + r.normal(size=X.shape) * 0.9
        self.z = Z - 72.0 + r.normal(size=Z.shape) * 0.9
        self.ph = r.random(X.shape) * 6.28
        self.size = size

    def _surface(self, t):
        u = _sc(98.2, 102.8, t)
        h = 9.0 * (1.0 - u) + 0.05
        r2 = np.clip((self.x ** 2 + (self.z + 72.0) ** 2) / (0.5 * self.size) ** 2, 0, 1)
        y = h + (1.0 - u) * 3.0 * (1.0 - r2) + (1.0 - u) * 0.6 * np.sin(0.8 * t + self.ph)
        return np.stack([self.x, y, self.z], -1)

    def sample(self, t):
        g = _win(97.8, 99.4, 108.5, 112.6, t)
        if g <= 0.002:
            return None
        P = self._surface(t)
        a = np.concatenate([P[:, :-1].reshape(-1, 3), P[:-1, :].reshape(-1, 3)])
        b = np.concatenate([P[:, 1:].reshape(-1, 3), P[1:, :].reshape(-1, 3)])
        landed = _sc(101.8, 103.2, t)
        knots = P.reshape(-1, 3)
        return [dict(pos=a, pos2=b, size=0.03, size2=0.03, color=lin("#ffd27a"), alpha=0.13 * g, emit=1.4,
                     kind="line"),
                dict(pos=knots, size=0.12, color=lin("#fff0c8"), alpha=0.75 * g * (0.6 + 0.4 * landed), emit=3.0,
                     kind="spark", twinkle=0.7, seed=(self.ph.ravel() / 6.28))]


class GrowingTree:
    """The tree of life (Claude Final v1's TreeOfLight) growing from where the dew lands."""

    def __init__(self):
        self.tree = FX.TreeOfLight(TREE_AT, height=6.2, t_bloom=HIT["bloom"], seed=77)
        self.t0, self.t1 = HIT["tree"] - 0.4, HIT["bloom"] + 1.0
        self.maxo = float(self.tree.so.max())

    def sample(self, t):
        if t < self.t0:
            return None
        rows = self.tree.sample(t)
        if not rows:
            return None
        grow = (self.maxo + 1.0) * _sc(self.t0, self.t1, t)
        keep = self.tree.so <= grow
        part = np.clip(grow - self.tree.so, 0.0, 1.0)
        out = []
        for i, r in enumerate(rows):
            r = dict(r)
            if i < 2:      # trunk and boughs: each segment grows out from its start
                a, b = r["pos"][keep], r["pos2"][keep]
                b = a + (b - a) * part[keep][:, None]
                r.update(pos=a, pos2=b)
                for key in ("size", "size2"):
                    if np.ndim(r.get(key)) > 0:
                        r[key] = np.asarray(r[key])[keep]
            out.append(r)
        g = 1.0 - _sc(151.0, 156.5, t) + 0.8 * _sc(176.0, 181.0, t)   # out of the way of the Encouragement
        if g <= 0.002:
            return None
        for r in out:
            r["alpha"] = np.asarray(r.get("alpha", 1.0)) * g
        return out


class DewDrops:
    """Fine silver dew falling from the dawn web to the lake where the tree will grow (blue hour)."""

    def __init__(self):
        self.s = np.random.default_rng(31).random((500, 4))

    def sample(self, t):
        g = _win(118.0, 121.0, 125.0, 127.0, t)
        if g <= 0.002:
            return None
        s = self.s
        f = np.mod(s[:, 0] + 0.22 * t, 1.0)
        pos = TREE_AT + np.stack([(s[:, 1] - 0.5) * 3.0, 7.0 * (1.0 - f), (s[:, 2] - 0.5) * 3.0], 1)
        return [dict(pos=pos, size=0.025 + 0.02 * s[:, 3], color=lin("#e8f0ff"), alpha=g * 0.8, emit=2.6,
                     kind="spark", twinkle=0.6, seed=s[:, 3])]


class Blossoms:
    def __init__(self):
        path = np.array([TREE_AT + _v(0.0, 6.5, 0.0), TREE_AT + _v(4.0, 5.0, 3.0), TREE_AT + _v(10.0, 4.0, 4.0),
                         TREE_AT + _v(18.0, 5.0, 2.0)])
        self.p = FX.PetalStream(path, HIT["drift"] - 0.2, 150.5, n=900, speed=2.6, spread=0.9)

    def sample(self, t):
        if t < HIT["drift"] - 0.4 or t > 156.0:
            return None
        rows = self.p.sample(t)
        g = 1.0 - _sc(151.0, 155.5, t)
        if not rows:
            return None
        rows = rows if isinstance(rows, list) else [rows]
        return [dict(r, alpha=np.asarray(r.get("alpha", 1.0)) * g) for r in rows]


class Dim:
    def __init__(self, inner, k):
        self.inner, self.k = inner, k

    def sample(self, t):
        rows = self.inner.sample(t)
        if not rows:
            return rows
        rows = rows if isinstance(rows, list) else [rows]
        return [dict(r, alpha=np.asarray(r.get("alpha", 1.0)) * self.k) for r in rows if r is not None]


class ExprHearts:
    """Small hearts in each expression's colour drift off it (PHASEB 9.5): from the words as they loosen and
    rise into their star, and from the two people who acted it. Each heart is a tiny outline of light. They
    start only when the reading ends, so nothing crosses the words while they are read."""
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(91)
        th = np.linspace(0.0, 2.0 * np.pi, 22, endpoint=False)
        hx = 16 * np.sin(th) ** 3
        hy = 13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)
        self.shape = np.stack([hx, hy], 1) / 17.0
        self.waves = []
        for t0, t1, n, src, k in ((52.0, 56.0, 14, "words", COMP), (52.5, 61.0, 20, ("w1", "w2"), COMP),
                                  (171.0, 175.0, 14, "words", ENC), (171.5, 182.0, 22, ("helper", "tired"), ENC)):
            self.waves.append((t0, t1, src, k, r.random((n, 7))))

    def _src(self, src, t, s):
        if src == "words":
            return np.asarray(CPW.place(_LAYOUT, t, 0.5 + (s[0] - 0.5) * 0.4, 0.62 + 0.06 * s[1], 7.0), np.float64)
        b = _bodies()[src[int(s[6] * 2) % 2]]
        return np.asarray(b.where(t, "heart"), np.float64) + _v((s[0] - 0.5) * 0.3, 0.1 * s[1], 0.0)

    def sample(self, t, cam=None):
        out = []
        for t0, t1, src, k, S in self.waves:
            if t < t0 or t > t1 + 6.0:
                continue
            col = lin(_toward_white(COL[k], 0.3))
            born = t0 + (t1 - t0) * S[:, 0]
            for i in range(len(S)):
                age = t - born[i]
                if age < 0.0 or age > 5.5:
                    continue
                s = S[i]
                p0 = self._src(src, born[i], s[1:])
                rise = (0.16 if src != "words" else 0.22) * age
                sway = 0.12 * np.sin(age * (1.4 + s[3]) + 6.28 * s[4])
                c = p0 + _v(sway, rise, 0.0)
                size = (0.05 if src != "words" else 0.06) * (0.7 + 0.6 * s[5])
                a = _sc(0.0, 0.5, age) * (1.0 - _sc(3.6, 5.5, age)) * 0.9
                pts = c[None, :] + np.stack([self.shape[:, 0] * size, self.shape[:, 1] * size,
                                             np.zeros(len(self.shape))], 1)
                out.append(dict(pos=pts, size=size * 0.16, color=col * 1.3 + 0.1, alpha=np.full(len(pts), a),
                                emit=2.2, kind="spark"))
                out.append(dict(pos=c[None, :], size=size * 2.2, color=col, alpha=a * 0.10, kind="soft"))
        return out or None


def _symbols():
    """The two expression symbols IN the world, never over the words (PHASEB 9.4). Compliment (clapping hands
    with confetti): traced in sparks high in the night sky to the right while the two women speak. Encouragement
    (praying hands): a flock of morning birds that, for a moment as they pass, stands in its shape."""
    from p3d import brand  # noqa: F401  (brand imports brand_symbols; importing it first avoids a cycle)
    from p3d import brand_symbols as BS
    comp = BS.Traced("Compliment", heads=3, style="sparks", pos=(50.0, 31.0, -100.0), size=15.0, face="camera",
                     camera=CAMERA, color=_toward_white(COL[COMP], 0.45), t0=40.0, dur=2.2, hold=10.5, out=3.0,
                     intensity=0.6, reflect=False)
    enc = BS.Flock("Encouragement", carrier="bird", heading=(0.55, 0.85), travel=2.0, pos=(46.0, 27.0, -100.0),
                   size=17.0, face="camera", camera=CAMERA, color=_toward_white(COL[ENC], 0.15), t0=162.0, dur=7.0,
                   intensity=0.6, reflect=False)
    return comp, enc


def _setup(scene):
    from expressions import Clear
    scene.add("star", MorningStar(), reflect=True)
    falling = FallingComets()
    scene.add("comets", Clear(falling, WORDS), reflect=False)
    for name, body in _bodies().items():
        body.add(scene, name, reflect=False)      # no bright reflections in the bottom third
    scene.add("torches", Clear(Torches(), WORDS), reflect=False)
    scene.add("beams", Clear(Beams(), WORDS), reflect=False)
    scene.add("lightfall", LightFall(), reflect=False)
    scene.add("net", Clear(GoldenNet(), WORDS), reflect=False)
    scene.add("dew", DewDrops(), reflect=False)
    scene.add("tree", Clear(GrowingTree(), WORDS), reflect=False)
    scene.add("blossoms", Clear(Blossoms(), WORDS), reflect=False)
    scene.add("hearts", Clear(ExprHearts(), WORDS), reflect=False)
    scene.add("symbol compliment", Clear(_SYM_COMP, WORDS), reflect=False)
    scene.add("symbol encouragement", Clear(_SYM_ENC, WORDS), reflect=False)
    WORDS.add_to(scene, reflect=False)


# ---------------------------------------------------------------------------------------------------------
# The world: one night turning into one glorious morning, warm and never dark
# ---------------------------------------------------------------------------------------------------------
LOOKS = dict(
    lake=dict(base="night", sky_top="#101a4c", sky_mid="#2e3678", sky_hor="#c08a84", haze=0.5,
              haze_color="#6a5078", exposure=1.12, mist=0.30, mist_color="#3c3a70", water="#050a1e", stars=1.0, milky=0.85,
              dust=0.8, dust_color="#ffe2a8", dust_color2="#ffc8a0", bokeh=0.8, ripple=0.55, sun_int=0.0),
    verse=dict(base="night", sky_top="#121c50", sky_mid="#32387c", sky_hor="#c88a84", haze=0.55,
               haze_color="#7a5878", exposure=1.12, mist=0.32, mist_color="#4a3c70", water="#060a1e", stars=0.9, milky=0.7,
               dust=0.8, dust_color="#ffe2a8", dust_color2="#ffc8a0", ripple=0.5, sun_int=0.0),
    mirror=dict(base="night", sky_top="#121c50", sky_mid="#30387c", sky_hor="#b48090", haze=0.55,
                haze_color="#7a5878", exposure=1.12, mist=0.25, mist_color="#4a3c70", water="#060a1e", stars=0.9, milky=0.7,
                dust=0.6, dust_color="#ffe2a8", dust_color2="#ffc8a0", ripple=0.0, sun_int=0.0),
    rose=dict(base="predawn", sky_top="#18225a", sky_mid="#5a3f84", sky_hor="#e6a08a", sun_el=-3.5,
              sun_int=0.55, haze_color="#a8687a", mist_color="#8a5a78", stars=0.55, milky=0.25, dust=0.9,
              dust_color="#ffd9a0", dust_color2="#ffb8b0", ripple=0.35),
    glory=dict(base="predawn", sky_top="#1c2862", sky_mid="#6a4a8a", sky_hor="#f0a868", sun_el=-2.5,
               sun_int=0.6, haze=0.32, haze_color="#a8704a", mist=0.18, mist_color="#8a5a6a", stars=0.45,
               milky=0.2, dust=0.8, dust_color="#ffd890", dust_color2="#ffc070", ripple=0.3, exposure=0.95),
    bluehour=dict(base="dawn", sky_top="#16245a", sky_mid="#3c4c90", sky_hor="#9a90c0", sun_el=-4.0,
                  sun_int=0.35, haze=0.6, haze_color="#6a78b0", mist=0.5, mist_color="#7a84bc", stars=0.35,
                  milky=0.0, clouds=0.15, water="#0a1030", dust=0.6, dust_color="#e8eeff", dust_color2="#ffe0c0",
                  ripple=0.15, rays=0.0),
    dawnwarm=dict(base="dawn", sky_top="#1a2a64", sky_mid="#6a5a9a", sky_hor="#f0a07a", sun_el=-1.5,
                  sun_int=0.8, clouds=0.2, stars=0.15, mist=0.45, mist_color="#b08090", ripple=0.15),
    sunrise=dict(base="sunrise", sky_top="#12306c", sky_mid="#64528a", sky_hor="#f2a060", sun_el=1.0,
                 sun_int=0.7, sun_glow=0.45, clouds=0.25, haze_color="#d0906a", mist_color="#c09080", ripple=0.25,
                 exposure=0.85),
    morning=dict(base="golden", sky_top="#12306c", sky_mid="#5e5c98", sky_hor="#f4b070", sun_el=5.5,
                 sun_int=0.55, sun_glow=0.35, sun_disc=3.0, sun_color="#ffe8c0", clouds=0.2, haze=0.28, haze_color="#c89070",
                 mist=0.10, mist_color="#d0a080", water="#141c3a", ripple=0.25, rays=0.15, dust=0.6,
                 dust_color="#fff0d0", dust_color2="#ffd8a0", exposure=0.82),
    still=dict(base="golden", sky_top="#173a74", sky_mid="#8c7282", sky_hor="#ffc47c", sun_el=6.5,
               sun_int=0.55, sun_glow=0.35, sun_disc=3.0, sun_color="#ffe8c0", clouds=0.2, haze=0.28, haze_color="#c89070",
               mist=0.10, mist_color="#d0a080", water="#141c3a", ripple=0.05, rays=0.15, dust=0.45,
               dust_color="#fff0d0", dust_color2="#ffd8a0", exposure=0.82),
)

def _toward_white(hexs, k):
    c = [int(hexs[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02x" % int(round(v + (255 - v) * k)) for v in c)


_SYM_COMP, _SYM_ENC = _symbols()

# the arch lights glow in the website colours, lifted toward white so the deep ones (Compliment's navy)
# still read as lit stars on a bright morning sky
ARCH_COL = [_toward_white(c, 0.35) for c in COL]

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "lake"), (24.0, "verse", 4.0), (54.6, "mirror", 2.5), (58.4, "rose", 8.0), (84.0, "glory", 3.0),
          (112.6, "bluehour", 2.0), (125.0, "dawnwarm", 10.0), (146.6, "sunrise", 2.0), (152.0, "morning", 5.0),
          (186.0, "still", 6.0)],
    sun_az=180.0,
    light=dict(pos=MSTAR, color="#ffe2a0", strength=Track([(0.0, 0.8), (HIT["lift"], 0.8), (HIT["lift"] + 0.3, 1.6),
                                                          (HIT["lift"] + 3.0, 0.8), (146.0, 0.8), (150.0, 0.0),
                                                          (TOTAL, 0.0)]), size=0.6, rays=0.6),
    arch=dict(lit=arch_states, colors=ARCH_COL, span=ARCH_GEO["span"], height=ARCH_GEO["height"], z=ARCH_GEO["z"],
              center=ARCH_GEO["center"], line=arch_line),
    react=dict(beat=0.15, level=0.15),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD) if hasattr(WORDS, "world") else WORLD,
    setup=_setup,
    bursts=[dict(t=HIT["open"], strength=0.35, rise=0.15, fall=0.8, color="#fff4e0", at=tuple(MSTAR)),
            dict(t=HIT["lift"], strength=0.25, rise=0.15, fall=0.9, color="#ffe2a0", at=tuple(MSTAR)),
            dict(t=99.0, strength=0.14, rise=0.5, fall=1.5, color="#ffc870"),
            dict(t=HIT["sun"], strength=0.22, rise=0.6, fall=1.6, color="#ffe8c0")],
    motion_blur=0.25,
)

# no 2D engine title or end card: the backdrop ends on its calm morning hold
FORM_DUR = 3.0
TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(_base.TAGLINE, t0=1e9, t1=1e9 + 1.0)
FRAGMENTS = []
TITLE_HIT = 1e9
_base.TITLE_HIT = TITLE_HIT
PHRASES = _base.PHRASES
CREDIT = _base.CREDIT
WAVES = []
