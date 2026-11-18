"""Song 07 "May No One Ever Feel Lonely": full-length concert backdrop, version 2 (concert item 8, Sunday Dec 6).

Authored on the REFERENCE clock (the church's recording youtu.be/7piuHaCYnFM, measured: TIMELINE.md); the
stage video runs on the LIVE clock (238.0 s of music, then a 15 s calm hold) through tools/s07_full2/clock.py.
Built on the pinned Film 10 engine (d928ff9) with the approved Revision 3 craft: warm gold glitter people,
Claude Final v1 cream serif phrases with coloured capsule labels (f43f451), the arch of nine lights. No comets
(song 01 only). Signature effects of this song: footprints of light, the peace rings, the lost lights found,
Mother's lamp, the first stars coming out, the gate of the kingdom and the bridge of light home.

Design: project-docs/designs/07 May No One Ever Feel Lonely.md ("No Light Left Alone"); plan and checks:
project-docs/backdrops/s07-full2/. No em dash or en dash anywhere in this file.
"""
import numpy as np

import songs.s03_original as _base

import clock as _clock

MUSIC = _clock.REF_MUSIC            # the recording's music (reference clock); silent after 243.5 s
HOLD = _clock.HOLD                  # calm hold after the music
TOTAL = MUSIC + HOLD                # 258.5 s of reference clock = 253.0 s of stage video
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = MUSIC
_base.SONG_END = MUSIC
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
from p3d.camera import Move, Rig, fly  # noqa: E402

import reference  # noqa: E402,F401  (tools/nine_colours_minor: Claude Final v1 as nine_reference_p3d)
from nine_reference_p3d import words as PW  # noqa: E402

TOTAL = MUSIC + HOLD
NFRAMES = int(round(TOTAL * FPS))
MUSIC_END = MUSIC
SONG_END = MUSIC
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

# ---------------------------------------------------------------------------------------------------------
# The music (measured on the recording: TIMELINE.md)
# ---------------------------------------------------------------------------------------------------------
SEC = dict(intro=0.0, verse1=14.0, chorus1=53.0, soft2=77.5, full2=98.0, hush=137.5, soft3=149.0,
           final=174.5, ending=230.5, end=MUSIC)
HITS = [26.9, 31.9, 38.3, 53.4, 90.3, 96.8, 130.5, 161.4, 186.0, 198.2, 231.6]   # onset peaks, measured

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
PEARL = "#fff4e0"
GOLD = "#ffc664"
GOLD2 = "#fff0c8"
WARM = "#ffd9a0"


def _ss(a, b, x):
    a, b, x = (np.asarray(v, np.float64) for v in (a, b, x))
    d = b - a
    u = np.clip((x - a) / np.where(d > 0, d, 1.0), 0.0, 1.0)
    return np.where(d > 0, u * u * (3.0 - 2.0 * u), (x >= a).astype(np.float64))


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _win(t, a, b, c, d):
    """0 before a, rises to 1 at b, holds to c, falls to 0 at d."""
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0, the camera looks toward -z where the horizon star rests)
# ---------------------------------------------------------------------------------------------------------
STAR = _v(0.0, 4.0, -420.0)          # the warm horizon star: Heavenly Mother's presence
BENCH = _v(0.25, 0.0, -6.5)          # where the lonely traveler sits down
LAMP = _v(-0.6, 0.0, -22.0)          # where Heavenly Mother waits with Her lamp (verse 2)
SHORE = _v(0.0, 0.0, -14.0)          # where everyone gathers (hush, verse 3)
GATE = _v(0.0, 170.0, -560.0)        # the gate of the kingdom, high above the far hills

# ---------------------------------------------------------------------------------------------------------
# The camera: calm, slow and wide. Performers stand in front of this picture.
# ---------------------------------------------------------------------------------------------------------


class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _keys():
    k = []

    def add(t, p, q):
        k.append((float(t), _v(*p), _v(*q)))

    # opening (06's closing frame, low and wide at the near shore, big calm sky behind the opening card), then
    # eye level on the lake and a slow push down the long path toward the horizon star
    add(0.0, (0.0, 1.30, 9.5), (0.0, 7.0, -40.0))
    add(8.0, (0.0, 1.45, 8.8), (0.0, 5.4, -40.0))
    add(16.0, (0.2, 1.80, 6.6), (0.2, 1.25, -40.0))
    add(34.0, (0.4, 1.70, 5.4), (0.3, 1.10, -40.0))
    add(49.0, (0.6, 1.60, 3.6), (0.4, 0.95, -30.0))
    # chorus 1: a slow respectful half circle (about 25 degrees) round the two, never closer than full length
    add(58.0, (-0.3, 1.50, -0.4), (0.6, 1.25, -6.5))
    add(68.0, (-1.7, 1.50, -0.7), (0.6, 1.25, -6.5))
    add(77.0, (-2.2, 1.70, -1.2), (0.0, 1.30, -16.0))
    # verse 2: glide up behind Heavenly Mother, Her lamp in the centre of the frame
    add(89.0, (-0.4, 2.0, -8.0), (-0.6, 1.5, -60.0))
    add(97.0, (-0.3, 2.1, -9.0), (-0.6, 1.5, -60.0))
    # the search: a gentle rise over the river of lanterns, looking out level so the people stay in the
    # middle band (the first run looked down on them and filled the lower third, 1:38 to 2:17)
    add(110.0, (1.8, 3.6, -9.0), (-1.2, 2.6, -70.0))
    add(121.0, (2.2, 3.4, -11.0), (-1.4, 2.5, -70.0))
    # the reunions on the shore, then completely still for the hush
    add(131.0, (1.4, 2.9, -6.0), (-0.8, 2.4, -60.0))
    add(137.5, (1.2, 2.8, -5.5), (-0.8, 2.4, -60.0))
    add(149.0, (1.2, 2.8, -5.5), (-0.8, 2.4, -60.0))
    # verse 3: a slow tilt from the lake toward the sky where the kingdom appears
    add(163.0, (1.0, 2.5, -3.0), (-0.4, 5.0, -80.0))
    add(174.5, (0.8, 2.7, -2.5), (-0.2, 5.6, -80.0))
    # final chorus: wide and majestic, a slow crane up beside the procession
    # (low and level, so Heavenly Mother and the procession stay in the middle band, above the bottom third)
    add(192.0, (2.0, 2.3, -3.0), (0.0, 4.9, -80.0))
    add(210.0, (2.6, 2.2, -4.0), (0.0, 5.0, -80.0))
    add(226.0, (2.0, 2.2, -4.0), (0.0, 4.8, -80.0))
    # ending: down to the closing frame for song 08, wide at eye level just above the water
    add(240.0, (0.6, 2.4, 2.0), (0.0, 3.2, -80.0))
    add(248.0, (0.0, 1.55, 6.0), (0.0, 2.6, -80.0))
    add(TOTAL, (0.0, 1.50, 5.2), (0.0, 2.6, -80.0))
    return k


def _rig():
    return Rig([fly(_keys(), fov=lambda t: 52.0 - 2.0 * _sc(48.0, 56.0, t) + 4.0 * _sc(98.0, 112.0, t)
                    - 4.0 * _sc(124.0, 136.0, t) + 4.0 * _sc(174.5, 206.0, t) - 2.0 * _sc(230.0, 246.0, t),
                    aperture=0.0, focus=30.0, ease="linear")],
               blend=0.0, fov=52.0, aperture=0.0, handheld=0.0, min_height=0.3)


CAMERA = _rig()
_LAYOUT = CAMERA


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights (star history: 3 to 9 lit at the start, 1 lit by this song, 2 waits for song 08)
# ---------------------------------------------------------------------------------------------------------
# The arch keeps one place in the picture, whatever the calm camera does: across the top of the sky, its feet
# at about half the picture's height near the sides, its top above the words, every star clear of the
# signature in the top left (checked by check_layout.py over the whole video).
ARCH_D = 60.0            # metres ahead of the lens
ARCH_SCREEN = dict(x0=0.13, x1=0.87, foot=0.50, top=0.19)    # picture fractions (y from the top)


def _arch_frame(t):
    cam = PW._cam_at(_LAYOUT, t)
    f = np.asarray(cam.target, np.float64) - np.asarray(cam.pos, np.float64) if hasattr(cam, "target") else None
    if f is None:
        f = place(t, 0.5, 0.5, 10.0) - np.asarray(cam.pos, np.float64)
    yaw = float(np.degrees(np.arctan2(-f[0], -f[2])))
    foot = place(t, 0.5, 1.0 - ARCH_SCREEN["foot"], ARCH_D)
    top = place(t, 0.5, 1.0 - ARCH_SCREEN["top"], ARCH_D)
    span = _width_at(t, ARCH_D, ARCH_SCREEN["x1"] - ARCH_SCREEN["x0"])
    return foot, yaw, span, float(top[1] - foot[1])


def _arch_center(t):
    return _arch_frame(t)[0]


def _arch_yaw(t):
    return _arch_frame(t)[1]


def _arch_span(t):
    return _arch_frame(t)[2]


def _arch_height(t):
    return _arch_frame(t)[3]


def _arch_line(t):
    """The arc's own dust and lines stay faint behind the opening card (the stars themselves stay lit)."""
    return 0.08 + 0.62 * _sc(8.4, 11.5, t)


def arch_homes(t):
    """The nine places of the arch at t (as p3d.world.Arch.point)."""
    c, yaw, span, height = _arch_frame(t)
    th = np.radians(np.linspace(172.0, 8.0, 9))
    x, y = 0.5 * span * np.cos(th), height * np.sin(th)
    a = np.radians(yaw)
    return np.stack([c[0] + x * np.cos(a), c[1] + y, c[2] - x * np.sin(a)], axis=1)


STAR1_T = 64.8           # Greeting's light reaches star 1 (lit for the first time in the concert)
STAR8_T = 77.8           # Consideration's light reaches star 8 (relit: a brief flare and one new ring)


def _arch_lit(t):
    out = []
    for i in range(9):
        if i == GRAT:
            out.append((0.0, -1.0))
        elif i == GREET:
            age = t - STAR1_T
            if age < -0.35:
                out.append((0.0, -1.0))
            else:
                g = min(max((age + 0.35) / 0.35, 0.0), 1.0)
                out.append((0.62 * g + (1.5 * np.exp(-max(age, 0.0) * 1.2) if age >= 0 else 0.0), max(age, 0.0)))
        elif i == CONS:
            age = t - STAR8_T
            flare = 1.2 * np.exp(-max(age, 0.0) * 1.4) if age >= 0 else 0.0
            out.append((0.55 + flare, 30.0 + max(age, 0.0) if age < 0 else max(age, 0.0)))
        else:
            out.append((0.55, 30.0 + t))
    return out


# ---------------------------------------------------------------------------------------------------------
# The people of light (all warm gold glitter; built when the scene is set up)
# ---------------------------------------------------------------------------------------------------------
_BODIES = {}
G_LOOK = "glitter"


def _gold(k=0):
    pal = [("#ffc664", "#fff0c8"), ("#f2a640", "#ffdc96"), ("#ffd27a", "#fff4dc"), ("#f6b85a", "#ffe8b8")]
    return pal[k % len(pal)]


def _body(name, shape, **kw):
    from nine_reference_p3d.body import Body
    c, c2 = _gold(kw.pop("tone", 0))
    common = dict(look=kw.pop("look", G_LOOK), color=kw.pop("color", c), color2=kw.pop("color2", c2),
                  points=int(kw.pop("points", 30000) * 1.6), fade=kw.pop("fade", 0.8),
                  bright=kw.pop("bright", 1.35) * 1.7, size=kw.pop("size", 1.5))
    common.update(kw)
    b = Body(shape, **common)
    _BODIES[name] = b
    return b


def _palm(name, t, side="R"):
    return np.asarray(_BODIES[name].where(t, "palm." + side), np.float64)


def _raw(name, t, part):
    return np.asarray(_BODIES[name].where(t, part, raw=True), np.float64)


T_RISE = 67.2            # the traveler rises, pulled up by the helper's hand (Consideration)


def _grip(t):
    """Where the two right hands meet as the helper pulls the traveler up (as pairs.helped_up)."""
    pa, pb = _raw("helper", t, "shoulder.R"), _raw("traveler", t, "shoulder.R")
    g = 0.5 * (pa + pb)
    g[1] = 0.5 * (pa[1] + pb[1]) - 0.36
    return g


def _bodies():
    if _BODIES:
        return _BODIES
    import nine_reference_p3d.master_acting  # noqa: F401  (Final v1 refined acting)
    # the elderly traveler (a man): walks in slowly along the shore and stands alone, a little stooped. GREETING:
    # he and the helper face each other and each gives a slight warm bow. Weary, he sinks onto one knee;
    # CONSIDERATION: the helper reaches down a hand and pulls him up to standing; they walk on together.
    _body("traveler", "man", at=(BENCH[0] - 2.94, BENCH[2]),
          facing=[(0.0, 90.0), (70.2, 90.0), (71.6, 180.0)],
          motion=[(7.0, "walk", dict(speed=0.42)), (14.0, "stand", dict(blend=1.4)),
                  (62.9, "kneel", dict(one=True, dur=1.6, blend=0.3)),
                  (T_RISE, "rise", dict(dur=1.7, one=True, blend=0.05)),
                  (71.4, "walk", dict(speed=0.42)), (88.0, "stand", dict(blend=1.5))],
          gesture=[(14.5, 52.0, "bow", dict(amount=16.0)), (53.4, 59.8, "bow", dict(amount=18.0)),
                   (T_RISE - 0.8, T_RISE + 2.6, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.6)),
                   (T_RISE + 2.4, 70.8, "hand_on_shoulder",
                    dict(side="L", to=lambda t: _raw("helper", t, "shoulder.R"), ease=0.9))],
          stoop=0.4, garment="coat", tone=1, seed=21.0, show=(6.0, 86.0), fade=2.5, points=34000)
    # the helper (a man): passes by behind, stops, turns back, walks to him and faces him (Greeting), steps
    # close and reaches down his hand (Consideration), then walks on beside him at his pace
    _body("helper", "man", at=(-9.0, BENCH[2] - 1.6),
          facing=[(0.0, 90.0), (39.0, 90.0), (41.5, -52.0), (49.0, -52.0), (50.2, -90.0), (70.2, -90.0),
                  (71.6, 180.0)],
          motion=[(16.5, "walk", dict(speed=1.0)), (29.0, "stand", dict(blend=1.4)),
                  (41.3, "walk", dict(speed=0.36)), (49.2, "stand", dict(blend=1.0)),
                  (62.4, "walk", dict(speed=0.15)), (64.0, "stand", dict(blend=0.8)),
                  (71.4, "walk", dict(speed=0.42)), (88.0, "stand", dict(blend=1.5))],
          gesture=[(38.6, 41.2, "look_up", dict(amount=-4.0, turn=-28.0)), (53.2, 59.6, "bow", dict(amount=18.0)),
                   (T_RISE - 1.0, T_RISE + 2.6, "handshake", dict(side="R", to=_grip, grip=1.0, ease=0.7))],
          tone=0, seed=22.0, show=(15.6, 86.0), fade=2.5, garment="tunic", points=34000)
    # two busy passers-by going the other way, after the opening card (not unkind, just not noticing): men
    _body("passer1", "man", at=(7.0, BENCH[2] - 3.0), facing=270.0, motion=[(8.5, "walk", dict(speed=1.15))],
          garment="coat", tone=2, seed=23.0, show=(8.5, 20.5), fade=1.5, points=20000)
    _body("passer2", "man", at=(9.5, BENCH[2] - 4.5), facing=270.0, motion=[(10.5, "walk", dict(speed=1.2))],
          garment="tunic", tone=3, seed=24.0, show=(10.5, 23.0), fade=1.5, points=20000)
    # Heavenly Mother, only ever seen from behind: Her lamp held up toward the misty water, then leading home
    _body("mother", "woman", at=(LAMP[0], LAMP[2]), facing=180.0,
          motion=[(0.0, "stand"), (196.0, "walk", dict(speed=0.6)), (229.0, "stand", dict(blend=2.0))],
          gesture=[(90.0, 230.0, "raise_hand", dict(side="R", palm="fwd"))],
          garment="robe", veil=dict(length=1.5, wide=1.1), color="#ffe6b0", color2="#fff6e0", seed=30.0,
          show=(88.0, 236.0), fade=2.5, points=40000, bright=1.55)
    # the two lantern-bearers at the front of the search (the male duet): men side by side, lights held high
    for k, x0 in enumerate((-2.5, -1.3)):
        _body(f"bearer{k}", "man", at=(x0, LAMP[2] - 2.5 - 0.4 * k),
              facing=[(0.0, 180.0), (125.5, 180.0), (127.0, 0.0)],
              motion=[(99.5 + 0.5 * k, "walk", dict(speed=0.7)), (121.6, "stand", dict(blend=1.4)),
                      (127.2 + 0.3 * k, "walk", dict(speed=0.5)), (137.0, "stand", dict(blend=1.5))],
              gesture=[(98.5, 123.0, "raise_hand", dict(side="R", palm="fwd")),
                       (123.0, 126.0, "handshake", dict(side="R", to=lambda t, k=k: _palm(f"lost{k}", t))),
                       (127.0, 176.0, "raise_hand", dict(side="R", palm="fwd"))],
              garment="tunic" if k else "coat", tone=k, seed=40.0 + k, show=(97.0, 176.0), points=24000)
    # two who were lost (men), reached by the bearers' offered hands, walking home with them
    for k, x0 in enumerate((-2.5, -1.3)):
        _body(f"lost{k}", "man", at=(x0, LAMP[2] - 21.0 - 0.4 * k), facing=0.0,
              motion=[(0.0, "stand"), (127.6 + 0.3 * k, "walk", dict(speed=0.5)), (137.0, "stand", dict(blend=1.5))],
              gesture=[(123.2, 126.0, "offer", dict(side="R"))],
              garment="coat" if k else "tunic", tone=2 + k, seed=50.0 + k, show=(116.0, 176.0), fade=3.0,
              points=22000)
    # the shore: two women embrace (one who has come home); a mother holds her child close (parent and child)
    _body("sister0", "woman", at=(2.6, LAMP[2] - 5.5), facing=90.0, motion="stand", garment="dress",
          hair="bun", tone=0, seed=60.0, show=(126.0, 176.0), fade=1.6, points=22000,
          gesture=[(129.5, 137.5, "embrace", dict(to=_v(3.32 + 0.12, 1.25, LAMP[2] - 5.55), head="L"))])
    _body("sister1", "woman", at=(3.32, LAMP[2] - 5.55), facing=270.0, motion="stand", garment="robe",
          hair="bob", tone=1, seed=61.0, show=(126.0, 176.0), fade=1.6, points=22000,
          gesture=[(129.8, 137.5, "embrace", dict(to=_v(2.6 - 0.12, 1.25, LAMP[2] - 5.5), head="L"))])
    _body("parent", "woman", at=(-4.6, LAMP[2] - 6.0), facing=120.0, motion="stand", garment="dress",
          hair="bun", tone=2, seed=62.0, show=(126.0, 176.0), fade=1.6, points=22000,
          gesture=[(130.0, 174.0, "arm_round", dict(side="L", to=lambda t: _BODIES["child"].where(t, "shoulder.R")))])
    _body("child", "child", at=(-4.12, LAMP[2] - 5.78), facing=300.0, motion="stand", garment="tunic",
          tone=3, seed=63.0, show=(126.0, 176.0), fade=1.6, points=16000,
          gesture=[(150.5, 174.0, "look_up", dict(amount=30.0))])
    return _BODIES


# ---------------------------------------------------------------------------------------------------------
# The words: the two expressions (exact wording from words.EXPRESSIONS) and the five named fragments
# ---------------------------------------------------------------------------------------------------------
WORD_Y = 0.655              # centre of a text block, from the BOTTOM (0.345 from the top: the upper middle)
WORD_DEPTH = 7.0


def _width_at(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _width(t, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * WORD_DEPTH * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _spec(name, t_in, r0, r1, t_out, frac, **kw):
    s = dict(name=name, ride=(0.5, WORD_Y, WORD_DEPTH), face="screen", width=_width(0.5 * (r0 + r1), frac),
             t_in=t_in, t_read0=r0, t_read1=r1, t_out=t_out, reflect=False, sharp=1.0)
    s.update(kw)
    return s


_SPECS = [
    # Mother's three wishes: pearl italic between quotation marks (design section 6)
    _spec("path", 26.9, 28.3, 36.4, 37.8, 0.50, lines=["\u201con the path to heaven\u201d"], color=PEARL,
          glow="#ffe2a8", tint=0.2, arrive="stitch", leave="sink"),
    _spec("wish", 39.0, 40.4, 47.6, 49.0, 0.50, lines=["our Mother\u2019s earnest wish"], font="tag",
          color="#ffe2a8", glow=GOLD, tint=0.35, arrive="gather", leave="rise"),
    # the two expressions: exact wording from words.EXPRESSIONS, website colours, capsule labels
    _spec("Greeting", 52.6, 54.0, 63.2, 64.8, 0.36, expr="Greeting", pill=True, arrive="pen", nib=False,
          leave="stream", to=arch_homes(64.8)[GREET]),
    _spec("Consideration", 65.0, 66.4, 75.8, 77.8, 0.40, expr="Consideration", pill=True, arrive="pen",
          nib=False, leave="stream", to=arch_homes(77.8)[CONS], ride=(0.5, WORD_Y - 0.025, WORD_DEPTH)),
    _spec("return", 79.2, 80.5, 88.8, 90.6, 0.40, lines=["\u201cplease return\u201d"], color=PEARL,
          glow="#ffe2a8", tint=0.2, arrive="reveal", leave="wind"),
    _spec("kingdom", 150.4, 152.0, 160.6, 162.2, 0.52, lines=["\u201cthe eternal kingdom\u201d"], color=PEARL,
          glow="#ffe2a8", tint=0.2, arrive="rays", leave="rise"),
    _spec("home", 207.4, 209.0, 217.6, 219.6, 0.50, lines=["my heavenly home"], font="tag", color="#ffe2a8",
          glow=GOLD, tint=0.35, arrive="weave", leave="doors"),
]
WORDS = PW.Words(_SPECS, camera=_LAYOUT)


def _reading_boxes(t, cam):
    """Screen boxes (x0, x1, y0, y1; y from the bottom) of every word on screen at t, with a margin."""
    out = []
    for w in WORDS:
        if w.t_in - 0.3 <= t <= w.t_out + 0.3:
            try:
                x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            except Exception:
                continue
            if front:
                out.append((x0 - 0.03, x1 + 0.03, y0 - 0.05, y1 + 0.05))
    return out


BOTTOM = 0.37             # the calm bottom third (screen height from the bottom): no light effects in it


class Clear:
    """Keeps every light out of the words while they are on screen (nothing ever crosses a word), and, with
    calm=True, out of the bottom third of the picture, where the performers stand."""
    wants_camera = True

    def __init__(self, inner, calm=True, words=True):
        self.inner = inner
        self.calm = calm
        self.words = words
        for k in ("static", "dome"):
            if hasattr(inner, k):
                setattr(self, k, getattr(inner, k))

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1.0

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = _reading_boxes(t, cam) if self.words else []
        if not boxes and not self.calm:
            return got
        out = []
        for src in (got if isinstance(got, (list, tuple)) else [got]):
            if src is None:
                continue
            b = dict(src)
            p = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            if len(p) == 0:
                out.append(b)
                continue
            xy, z = cam.project(p)
            gain = np.ones(len(p))
            ends = [xy]
            if b.get("pos2") is not None:
                e2, _ = cam.project(np.asarray(b["pos2"], np.float64).reshape(-1, 3))
                ends = [xy * (1 - u) + e2 * u for u in np.linspace(0, 1, 7)]
            if self.calm:
                gain = gain * np.where(z > 0, _ss(BOTTOM - 0.05, BOTTOM + 0.02, xy[:, 1]), 1.0)
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
# Effects: peace rings, footprints of light, the lost lights, lamps, the kingdom, bridge, procession
# ---------------------------------------------------------------------------------------------------------
# (start, centre, reach in metres, slow): a slow ring spreads at a steady 3.5 m/s (the hush and the ending)
RINGS = [(54.0, BENCH, 70.0, False), (64.0, BENCH, 70.0, False), (76.4, BENCH, 70.0, False),
         (126.5, LAMP + _v(-1.9, 0, -18.0), 60.0, False), (137.6, LAMP, 80.0, True),
         (231.6, _v(0.0, 0.0, -30.0), 110.0, True)]


class PeaceRings:
    """A slow ring of golden stillness spreading across the lake from where one of Mother's words is spoken.
    The ring fades out before it reaches the camera, so it never sweeps through the lens as a flash."""
    wants_camera = True

    def __init__(self, n=1800):
        r = np.random.default_rng(71)
        self.a = r.random(n) * 2.0 * np.pi
        self.j = r.normal(size=n) * 0.35
        self.s = r.random(n)

    def sample(self, t, cam):
        out = []
        eye = np.asarray(cam.pos, np.float64)
        for t0, c, rmax, slow in RINGS:
            u = t - t0
            if u < 0.0 or u > (12.0 if slow else 11.0):
                continue
            if slow:
                rad = 3.5 * u + 0.3
                al = _sc(0.0, 0.8, u) * (1.0 - _sc(7.0, 12.0, u))
            else:
                rad = rmax * (1.0 - np.exp(-u / 4.0)) + 0.3
                al = _sc(0.0, 0.6, u) * (1.0 - _sc(6.0, 11.0, u))
            pos = np.stack([c[0] + np.sin(self.a) * (rad + self.j * (0.3 + 0.03 * rad)), np.full_like(self.a, 0.04),
                            c[2] + np.cos(self.a) * (rad + self.j * (0.3 + 0.03 * rad))], axis=1)
            near = _ss(6.0, 16.0, np.linalg.norm(pos - eye, axis=1))
            al = al * near
            out.append(dict(pos=pos, size=0.10 + 0.012 * rad * (0.5 + self.s), color=lin("#ffcf86"),
                            alpha=0.55 * al * (0.4 + 0.6 * self.s), emit=1.2, kind="soft", reflect=False,
                            seed=self.s, twinkle=0.4))
            out.append(dict(pos=pos[::6], size=0.05 + 0.004 * rad, color=lin("#fff0cc"), alpha=0.7 * al[::6],
                            emit=2.0, kind="spark", reflect=False, seed=self.s[::6], twinkle=0.6))
        return out or None


class Footprints:
    """Mother's wish lights the way: footprints of light from the horizon star along the water to the one who
    sits alone, as if someone has already walked this way to find him (26 to 36 s)."""

    def __init__(self, n=64):
        self.n = n
        k = np.arange(n)
        u = (k / (n - 1.0)) ** 1.6                       # spaced closer near the far end (perspective)
        far = _v(0.0, 0.0, -150.0)
        near = BENCH + _v(0.3, 0.0, 1.0)
        base = far[None, :] * (1 - u)[:, None] + near[None, :] * u[:, None]
        side = np.where(k % 2 == 0, 1.0, -1.0) * 0.16
        base[:, 0] += side
        self.pos = base
        self.birth = 26.0 + 9.5 * (k / (n - 1.0))
        r = np.random.default_rng(81)
        self.s = r.random(n)
        # each footprint is a small oval of a few soft points
        m = 7
        off = np.stack([np.cos(np.linspace(0, 2 * np.pi, m, endpoint=False)) * 0.07, np.zeros(m),
                        np.sin(np.linspace(0, 2 * np.pi, m, endpoint=False)) * 0.13], axis=1)
        self.pts = (self.pos[:, None, :] + off[None, :, :]).reshape(-1, 3) + _v(0, 0.03, 0)
        self.pb = np.repeat(self.birth, m)

    def sample(self, t):
        if t < 25.5 or t > 92.0:
            return None
        age = t - self.pb
        lit = _ss(0.0, 0.4, age) * (1.0 - _ss(30.0, 60.0, age))
        flash = 1.0 + 2.0 * np.exp(-np.maximum(age, 0.0) / 0.5) * (age >= 0)
        return [dict(pos=self.pts, size=0.11, color=lin("#ffd894"), alpha=0.75 * lit, emit=1.4 * flash,
                     kind="soft", reflect=False, twinkle=0.3),
                dict(pos=self.pos + _v(0, 0.04, 0), size=0.5, color=lin("#ffc070"),
                     alpha=0.10 * lit[::7], kind="soft", reflect=False)]


LOST = [(-2.5, -43.0, 123.4), (-1.3, -43.4, 123.4), (-14.0, -60.0, 128.0), (11.0, -55.0, 129.0),
        (-24.0, -80.0, 131.0), (20.0, -78.0, 132.5), (4.0, -95.0, 134.0)]


class LostLights:
    """Seven small lights alone on the water, drifting in the mist; each is found and turns warm, and the ones
    still far away come home to the shore."""

    def __init__(self):
        self.base = np.array([[x, 0.9, z] for x, z, _ in LOST])
        self.found = np.array([f for _, _, f in LOST])
        self.home = np.array([[-9.0 + 3.0 * k, 0.9, LAMP[2] - 9.0 - (k % 2) * 1.5] for k in range(len(LOST))])

    def sample(self, t):
        if t < 78.0 or t > 180.0:
            return None
        drift = np.stack([0.6 * np.sin(0.13 * t + np.arange(7)), 0.12 * np.sin(0.7 * t + 2 * np.arange(7)),
                          -0.03 * np.maximum(t - 80.0, 0.0) * (t < self.found)], axis=1)
        f = _ss(self.found - 0.5, self.found + 1.5, t)
        go = _ss(self.found + 3.0, self.found + 14.0, t)
        go[:2] = 0.0                                    # the first two became the two who walk home
        pos = self.base + drift
        pos = pos * (1 - go)[:, None] + self.home * go[:, None]
        cool, warm = lin("#9fb2e6"), lin("#ffd08a")
        col = cool[None, :] * (1 - f)[:, None] + warm[None, :] * f[:, None]
        vis = _sc(78.0, 84.0, t) * (1.0 - _sc(172.0, 180.0, t))
        fade_body = np.ones(7)
        fade_body[:2] = 1.0 - _ss(self.found[:2], self.found[:2] + 2.0, t)
        al = vis * (0.35 + 0.65 * f) * fade_body
        return [dict(pos=pos, size=0.16 + 0.10 * f, color=col, alpha=al, emit=2.2, kind="spark", twinkle=0.3),
                dict(pos=pos, size=1.6 + 0.8 * f, color=col, alpha=0.14 * al, kind="soft")]


class Lamps:
    """Heavenly Mother's lamp (it grows brighter with every one who comes home) and the bearers' lights."""
    wants_camera = False

    def sample(self, t):
        b = _bodies()
        out = []
        if 89.0 < t < 236.0:
            m = b["mother"]
            joy = 1.0 + 0.25 * sum(_sc(f, f + 1.5, t) for _, _, f in LOST)
            vis = _sc(90.0, 92.5, t) * (1.0 - _sc(229.0, 235.0, t))
            p = np.asarray(m.where(t, "palm.R"), np.float64) + _v(0.0, 0.16, 0.0)
            out.append(dict(pos=p[None, :], size=0.16 * joy, color=lin("#fff1d0"), alpha=vis, emit=5.0, kind="spark"))
            out.append(dict(pos=p[None, :], size=2.2 * joy, color=lin("#ffd38a"), alpha=0.22 * vis, kind="soft"))
        for k in range(2):
            if 98.0 < t < 176.0:
                vis = _sc(98.6, 100.0, t) * (1.0 - _win(t, 123.0, 123.6, 126.4, 127.0) * 0.85) * \
                    (1.0 - _sc(173.0, 176.0, t))
                p = np.asarray(b[f"bearer{k}"].where(t, "palm.R"), np.float64) + _v(0.0, 0.14, 0.0)
                out.append(dict(pos=p[None, :], size=0.12, color=lin("#fff0c8"), alpha=vis, emit=4.0, kind="spark"))
                out.append(dict(pos=p[None, :], size=1.5, color=lin("#ffc070"), alpha=0.2 * vis, kind="soft"))
        return out or None


class Gate:
    """The gate of the kingdom of heaven, high above the far hills: an arched doorway of light with terraces of
    a city of light round it. It appears in verse 3, opens fully on the loudest moment and fades out in the
    calm hold, so song 08 opens on a plain night sky."""

    def __init__(self):
        r = np.random.default_rng(91)
        w, h = 30.0, 44.0
        n = 2600
        u = r.random(n)
        # outline: two pillars and a round top
        pts = []
        side = np.where(r.random(n) > 0.5, 1.0, -1.0)
        on_top = u > 0.55
        a = np.pi * (u - 0.55) / 0.45
        x = np.where(on_top, np.cos(a) * w * 0.5, side * w * 0.5)
        y = np.where(on_top, h - w * 0.5 + np.sin(a) * w * 0.5, (u / 0.55) * (h - w * 0.5))
        pts.append(np.stack([x, y, np.zeros(n)], axis=1) + r.normal(size=(n, 3)) * 0.35)
        self.outline = np.concatenate(pts) + GATE + _v(0.0, -h * 0.5, 0.0)
        self.os = r.random(len(self.outline))
        # the doorway's inner light
        m = 1800
        ix = (r.random(m) - 0.5) * w * 0.9
        iy = r.random(m) * (h - 2.0)
        keep = (iy < h - w * 0.5) | (ix ** 2 + (iy - (h - w * 0.5)) ** 2 < (w * 0.45) ** 2)
        self.inner = (np.stack([ix, iy, np.full(m, -2.0)], axis=1)[keep] + GATE + _v(0.0, -h * 0.5, 0.0))
        self.isd = r.random(len(self.inner))
        # terraces of the city of light
        rows = []
        for k, (ww, yy) in enumerate(((210.0, -30.0), (160.0, -16.0), (110.0, -2.0), (70.0, 12.0))):
            q = int(ww * 6)
            xs = (r.random(q) - 0.5) * ww
            rows.append(np.stack([xs, np.full(q, yy) + r.normal(size=q) * 0.6,
                                  np.full(q, 20.0 + 12.0 * k) + r.normal(size=q) * 4.0], axis=1))
        self.city = np.concatenate(rows) + GATE
        self.cs = r.random(len(self.city))

    def level(self, t):
        return _sc(149.5, 162.0, t) * (1.0 - _sc(238.0, 252.0, t))

    def sample(self, t):
        g = self.level(t)
        if g <= 0.002:
            return None
        open_ = _sc(196.0, 217.0, t)
        build = _sc(149.5, 160.0, t)
        oa = g * np.clip((build * 1.3 - self.os * 0.3), 0, 1)
        warm = lin("#ffe2a8")
        out = [dict(pos=self.outline, size=0.9, color=warm, alpha=0.9 * oa, emit=2.4, kind="spark", seed=self.os,
                    twinkle=0.5, fog=0.3, reflect=False),
               dict(pos=self.outline[::4], size=6.0, color=lin("#ffc880"), alpha=0.06 * oa[::4], kind="soft",
                    fog=0.3, reflect=False),
               dict(pos=self.inner, size=2.2, color=lin("#fff2d6"), alpha=g * (0.08 + 0.22 * open_) * self.isd,
                    kind="soft", fog=0.3, reflect=False),
               dict(pos=self.city, size=1.4, color=lin("#ffd9a0"), alpha=0.55 * g * build * (0.4 + 0.6 * self.cs),
                    emit=1.4, kind="soft", seed=self.cs, twinkle=0.4, fog=0.4, reflect=False)]
        return out


def _bridge_pt(u):
    """The bridge of light: from the shore at Mother's feet up through the sky to the open gate."""
    u = np.asarray(u, np.float64)[..., None]
    p0 = LAMP + _v(0.0, 0.05, -40.0)
    p1 = _v(0.0, 8.0, -220.0)
    p2 = GATE + _v(0.0, -21.0, 0.0)
    return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * p1 + u * u * p2


class Bridge:
    """The path's reflection lifts into the sky as a bridge of light from the shore to the gate; a procession of
    countless small lights walks it home (final chorus)."""

    def __init__(self):
        r = np.random.default_rng(101)
        n = 5000
        self.u = np.sort(r.random(n))
        self.w = r.normal(size=(n, 2))
        self.s = r.random(n)
        m = 1400
        self.pu = r.random(m)
        self.pw = (r.random(m) - 0.5) * 2.0
        self.ps = r.random(m)

    def sample(self, t):
        rise = _sc(196.0, 207.0, t)
        g = rise * (1.0 - _sc(236.0, 248.0, t))
        if g <= 0.002:
            return None
        width = 2.2 + 8.0 * self.u
        pos = _bridge_pt(self.u) + np.stack([self.w[:, 0] * width * 0.5, self.w[:, 1] * 0.15 * width,
                                             np.zeros_like(self.u)], axis=1)
        grow = np.clip((rise * 1.15 - self.u) / 0.15, 0, 1)
        out = [dict(pos=pos, size=0.25 + 0.5 * self.u, color=lin("#ffdca0"), alpha=0.5 * g * grow,
                    emit=1.3, kind="soft", seed=self.s, twinkle=0.5, reflect=True, fog=0.4)]
        # the procession: lights walking up the bridge into the gate
        walk = _sc(200.0, 206.0, t) * (1.0 - _sc(232.0, 240.0, t))
        if walk > 0.002:
            uu = np.mod(self.pu + 0.010 * (t - 200.0), 1.0)
            ok = uu < rise * 1.1
            wid = 2.0 + 8.0 * uu
            pp = _bridge_pt(uu) + np.stack([self.pw * wid * 0.4, np.full_like(uu, 0.6 + 2.0 * uu),
                                            np.zeros_like(uu)], axis=1)
            al = walk * ok * (1.0 - _ss(0.92, 1.0, uu)) * (0.5 + 0.5 * self.ps)
            out.append(dict(pos=pp, size=0.18 + 0.9 * uu, color=lin("#fff0c8"), alpha=al, emit=2.6,
                            kind="spark", seed=self.ps, twinkle=0.6, fog=0.4))
        return out


class FirstStars:
    """The first stars of the evening come out one by one, each with a soft glint as it is born, until the dusk
    sky is full (the look of this song: blue dusk, first stars). High in the sky, clear of the bottom third."""

    def __init__(self, n=150):
        r = np.random.default_rng(111)
        az = np.radians((r.random(n) - 0.5) * 150.0)
        el = np.radians(9.0 + 46.0 * r.random(n) ** 0.8)
        d = 900.0
        self.pos = np.stack([np.sin(az) * np.cos(el) * d, np.sin(el) * d, -np.cos(az) * np.cos(el) * d], axis=1)
        self.birth = np.sort(4.0 + 150.0 * r.random(n) ** 1.3)
        r.shuffle(self.pos)
        self.s = r.random(n)
        self.size = (1.2 + 2.6 * self.s ** 3)

    def sample(self, t):
        age = t - self.birth
        on = _ss(0.0, 1.8, age)
        if not on.any():
            return None
        glint = 1.0 + 2.2 * np.exp(-np.maximum(age, 0.0) / 0.9) * (age >= 0)
        warm = lin("#fff1d8") * (1 - self.s[:, None] * 0.3) + lin("#ffd2a0") * (self.s[:, None] * 0.3)
        return [dict(pos=self.pos, size=self.size, color=warm, alpha=0.85 * on, emit=1.6 * glint, kind="spark",
                     seed=self.s, twinkle=0.5, reflect=False, fog=0.0, dof=0.0),
                dict(pos=self.pos, size=self.size * 6.0, color=lin("#ffd8b0"), alpha=0.05 * on * glint,
                     kind="soft", reflect=False, fog=0.0, dof=0.0)]


class HeartSparks:
    """The engine's hearts (p3d/brand_hearts.py, HeartDrift: hearts drift off each expression in its colour)
    drawn with the pinned engine's points: each heart is a small outline of sparks facing the camera."""
    wants_camera = True

    def __init__(self, inner, k=18):
        self.inner = inner
        th = np.linspace(0.0, 2.0 * np.pi, k, endpoint=False)
        x = 16.0 * np.sin(th) ** 3
        y = 13.0 * np.cos(th) - 5.0 * np.cos(2 * th) - 2.0 * np.cos(3 * th) - np.cos(4 * th)
        self.h = np.stack([x, y + 2.0], axis=1) / 34.0
        self.k = k

    def gain(self, t):
        return self.inner.gain(t)

    def sample(self, t, cam):
        got = self.inner.sample(t)
        if not got:
            return None
        fwd = _unit(np.asarray(cam.target, np.float64) - np.asarray(cam.pos, np.float64)) \
            if hasattr(cam, "target") else _v(0, 0, -1)
        right = _unit(np.cross(fwd, _v(0, 1, 0)))
        up = np.cross(right, fwd)
        out = []
        for b in got:
            if b.get("kind") != "heart":
                continue
            p = np.asarray(b["pos"], np.float64)
            n = len(p)
            sz = np.asarray(b["size"], np.float64).reshape(-1)
            sz = np.broadcast_to(sz, (n,))
            rot = np.asarray(b.get("rot", np.zeros((n, 2))))[:, 0]
            c, si = np.cos(rot), np.sin(rot)
            hx = c[:, None] * self.h[None, :, 0] - si[:, None] * self.h[None, :, 1]
            hy = si[:, None] * self.h[None, :, 0] + c[:, None] * self.h[None, :, 1]
            pts = (p[:, None, :] + sz[:, None, None] * (hx[..., None] * right + hy[..., None] * up)).reshape(-1, 3)
            al = np.repeat(np.broadcast_to(np.asarray(b["alpha"], np.float64).reshape(-1), (n,)), self.k)
            col = np.asarray(b["color"], np.float64)
            col = np.repeat(np.broadcast_to(col, (n, 3)), self.k, axis=0) if col.ndim == 2 else col
            out.append(dict(pos=pts, size=np.repeat(sz * 0.11, self.k), color=col, alpha=al, emit=1.6,
                            kind="spark", reflect=False, twinkle=0.2))
            out.append(dict(pos=p, size=sz * 2.2, color=col if col.ndim == 1 else col[::self.k],
                            alpha=np.asarray(b["alpha"]) * 0.08, kind="soft", reflect=False))
        return out or None


def _hearts_and_symbols(scene):
    """PHASEB 9.4 and 9.5: each expression's symbol appears IN the world, subtly, in its colour, around its
    moment (never over the words), and hearts in its colour drift off it."""
    from p3d import brand  # noqa: F401  (loads brand_hearts and brand_symbols in the right order)
    from p3d import brand_hearts as BH
    from p3d import brand_symbols as BS
    b = _bodies()
    # GREETING: the waving hand drawn as a constellation of the first stars, high on the right, as the two bow
    # (each placed in the world where the picture has room beside the words at that moment)
    scene.add("symbol Greeting", Clear(BS.Constellation("Greeting", pos=tuple(place(58.0, 0.80, 0.56, 300.0)),
                                                        size=_width_at(58.0, 300.0, 0.10),
                                                        face="camera", camera=CAMERA, t0=55.0, dur=2.4,
                                                        hold=6.5, out=2.5, intensity=0.55, stars=26)),
              reflect=False)
    # CONSIDERATION: the two open hands holding a heart, traced by rose fireflies low over the far water
    scene.add("symbol Consideration", Clear(BS.Traced("Consideration", pos=tuple(place(70.0, 0.15, 0.58, 40.0)),
                                                      size=_width_at(70.0, 40.0, 0.085),
                                                      face="camera", camera=CAMERA, t0=67.5, dur=2.2, hold=6.0,
                                                      out=2.0, intensity=0.5)), reflect=False)
    # hearts drift up from between the two men while each expression is spoken, and off its words as they go
    mid = lambda t: 0.5 * (_raw("helper", t, "shoulder.R") + _raw("traveler", t, "shoulder.R"))
    scene.add("hearts Greeting", Clear(HeartSparks(BH.HeartDrift(mid, 55.0, 63.0, color=COL[GREET], rate=3.0,
                                                                 life=3.2, rise=0.45, spread=0.5,
                                                                 size=(0.10, 0.18), seed=71))), reflect=False)
    scene.add("hearts Consideration", Clear(HeartSparks(BH.HeartDrift(mid, 67.5, 76.0, color=COL[CONS],
                                                                      rate=3.0, life=3.2, rise=0.45, spread=0.5,
                                                                      size=(0.10, 0.18), seed=72))),
              reflect=False)
    for nm, k, t0 in (("Greeting", GREET, 63.2), ("Consideration", CONS, 75.8)):
        w = [x for x in WORDS if x.name == nm][0]
        scene.add(f"hearts off {nm}", Clear(HeartSparks(BH.HeartDrift(w, t0, t0 + 1.6, color=COL[k], rate=14.0,
                                                                      life=2.6, rise=0.35, spread=0.8,
                                                                      size=(0.12, 0.22), seed=73 + k)), words=False),
                  reflect=False)
    return b


def _crowds(scene):
    from nine_reference_p3d.crowd import Crowd
    gold = dict(color="#ffc664", color2="#fff0c8", bright=2.2, size=1.6, points=4200)
    # villagers who carry their lights out over the water into the mist (verse 2)
    scene.add("crowd search", Clear(Crowd(n=10, area=dict(center=(LAMP[0], LAMP[2] - 4.0), radius=(3.0, 11.0),
                                                          arc=(130.0, 230.0)),
                                          facing=lambda x, z: 180.0 + 0.6 * x, kinds=("light",), walk=0.55,
                                          start=dict(t=101.0, dur=5.0), until=138.0, fade=1.6, seed=7, **gold)), reflect=False)
    # the whole family gathered on the shore round Mother's lamp (hush and verse 3), arms raised to the kingdom
    scene.add("crowd shore", Clear(Crowd(n=24, area=dict(center=(LAMP[0], LAMP[2] - 7.0), radius=(5.0, 16.0),
                                                         arc=(115.0, 245.0)),
                                         facing=lambda x, z: 180.0 - 1.2 * x, kinds=("stand", ("raise", 0.35)),
                                         act=dict(t=162.0, dur=6.0), start=dict(t=131.0, dur=6.0), until=200.0,
                                         fade=2.0, seed=8, **gold)), reflect=False)
    # the family walking home behind Mother over the water (final chorus)
    scene.add("crowd home", Clear(Crowd(n=26, area=dict(center=(LAMP[0], LAMP[2] + 3.0), radius=(2.0, 12.0),
                                                        arc=(120.0, 240.0)),
                                        facing=180.0, kinds=("walk",), walk=0.6, start=dict(t=197.0, dur=5.0),
                                        until=234.0, fade=2.5, seed=9, **gold)), reflect=False)


def _setup(scene):
    for name, body in _bodies().items():
        body.add(scene, name, reflect=False)      # no people mirrored into the calm bottom third
    scene.add("first stars", FirstStars(), reflect=False)
    scene.add("footprints", Clear(Footprints()), reflect=False)
    scene.add("peace rings", Clear(PeaceRings()), reflect=False)
    scene.add("lost lights", Clear(LostLights()), reflect=False)
    scene.add("lamps", Clear(Lamps()), reflect=False)
    scene.add("gate", Clear(Gate()), reflect=False)
    scene.add("bridge", Clear(Bridge()), reflect=False)
    _hearts_and_symbols(scene)
    _crowds(scene)
    for e in scene.entries():
        if e.name in ("_dust", "_lanterns", "_floats", "_arch"):
            e.pointset = Clear(e.pointset)
        if e.name == "_arch":
            e.reflect = False                     # the arch is never mirrored (it would cross the bottom third)
    WORDS.add_to(scene, reflect=False)


# ---------------------------------------------------------------------------------------------------------
# The world: blue dusk on a long path home, warming with every word of love; navy night for song 08
# ---------------------------------------------------------------------------------------------------------
LOOKS = dict(
    amber06=dict(base="dusk", sky_top="#2a3a78", sky_mid="#8a6a96", sky_hor="#ffb070", sun_color="#ffc070",
                 sun_int=0.9, sun_el=-0.8, sun_az=180.0, stars=0.12, milky=0.0, clouds=0.3, haze=0.5,
                 haze_color="#c08070", mist=0.12, mist_color="#a07080", hill_color="#1a1430", water="#0c0c24",
                 dust=0.9, dust_color="#ffd9a0", dust_color2="#ffb070", ripple=0.25),
    dusk07=dict(base="dusk", sky_top="#0a1c5e", sky_mid="#28479c", sky_hor="#ee9a78", sun_color="#ffb48a",
                sun_int=0.55, sun_el=-2.5, sun_az=180.0, stars=0.45, milky=0.15, clouds=0.22, haze=0.45,
                haze_color="#5a6cae", mist=0.25, mist_color="#6a7ab6", hill_color="#0c0e26", water="#050820",
                dust=0.8, dust_color="#ffd9a0", dust_color2="#ffb48a", ripple=0.45),
    warm07=dict(base="dusk", sky_top="#0e2262", sky_mid="#2f50a4", sky_hor="#f4a478", sun_color="#ffc08a",
                sun_int=0.7, sun_el=-2.0, sun_az=180.0, stars=0.55, milky=0.2, clouds=0.22, haze=0.45,
                haze_color="#6a74b0", mist=0.22, mist_color="#7884ba", hill_color="#0e0e26", water="#060820",
                dust=1.0, dust_color="#ffd9a0", dust_color2="#ffb48a", ripple=0.12),
    mist07=dict(base="dusk", sky_top="#0c1f5e", sky_mid="#3254a0", sky_hor="#e0a08e", sun_color="#ffc49a",
                sun_int=0.5, sun_el=-2.5, sun_az=180.0, stars=0.5, milky=0.2, clouds=0.25, haze=0.6,
                haze_color="#7f82aa", mist=0.75, mist_height=3.2, mist_color="#8e95c0", hill_color="#10122c",
                water="#060a22", dust=0.7, dust_color="#ffd9a0", dust_color2="#c8d0ff", ripple=0.35),
    search07=dict(base="dusk", sky_top="#0e2262", sky_mid="#3658a6", sky_hor="#eea67e", sun_color="#ffc89a",
                  sun_int=0.65, sun_el=-2.2, sun_az=180.0, stars=0.6, milky=0.25, clouds=0.25, haze=0.55,
                  haze_color="#7884b6", mist=0.5, mist_height=2.8, mist_color="#a89cba", hill_color="#10122c",
                  water="#060a22", dust=1.0, dust_color="#ffd9a0", dust_color2="#ffc08a", ripple=0.25),
    mirror07=dict(base="night", sky_top="#0b1642", sky_mid="#26357a", sky_hor="#9a7290", sun_color="#ffc49a",
                  sun_int=0.45, sun_el=-2.5, sun_az=180.0, stars=1.0, milky=0.6, clouds=0.08, haze=0.25,
                  haze_color="#5a5a8a", mist=0.0, hill_color="#0c0e28", water="#03061a", ripple=0.0,
                  mirror=1.0, dust=0.6, dust_color="#ffd9a0", dust_color2="#ffc08a"),
    dawn07=dict(base="dawn", sky_top="#16265e", sky_mid="#6a508a", sky_hor="#eea684", sun_color="#ffd8a0",
                sun_int=0.5, sun_el=-1.0, sun_az=180.0, stars=0.3, milky=0.08, clouds=0.3, haze=0.5,
                haze_color="#c48a84", mist=0.3, mist_color="#c09090", hill_color="#161430", water="#0a0a20",
                rays=0.25, ripple=0.1, dust=0.9, dust_color="#ffe2a8", dust_color2="#ffc4a8"),
    glory07=dict(base="dawn", sky_top="#1c2a64", sky_mid="#6a4f86", sky_hor="#f0a874", sun_color="#ffd89a",
                 sun_int=0.5, sun_el=0.5, sun_az=180.0, stars=0.3, milky=0.05, clouds=0.3, haze=0.45,
                 haze_color="#a8707a", mist=0.22, mist_color="#a0707a", hill_color="#1a1430", water="#08081c",
                 rays=0.25, ripple=0.15, dust=1.1, dust_color="#ffe0a0", dust_color2="#ffc890"),
    night07=dict(base="night", sky_top="#0b1530", sky_mid="#1a2c62", sky_hor="#2e3e78", sun_color="#ffcf8a",
                 sun_int=0.6, sun_el=-1.8, sun_az=180.0, stars=1.0, milky=0.55, clouds=0.08, haze=0.3,
                 haze_color="#1e2c64", mist=0.12, mist_color="#24306a", hill_color="#05071a", water="#02040f",
                 ripple=0.12, dust=0.7, dust_color="#ffd9a0", dust_color2="#ffc08a"),
)

STAR_LIGHT = Track([(0.0, 0.9), (25.0, 0.9), (27.0, 1.5), (36.0, 1.5), (39.0, 1.0), (78.5, 1.0), (80.5, 1.45),
                    (89.0, 1.45), (92.0, 1.1), (149.0, 1.1), (152.0, 1.25), (161.0, 1.25), (174.5, 1.15),
                    (217.0, 1.3), (232.0, 1.2), (246.0, 0.95), (TOTAL, 0.95)])

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "amber06"), (3.0, "dusk07", 12.0), (50.0, "warm07", 5.0), (77.5, "mist07", 7.0), (98.0, "search07", 5.0),
          (131.0, "mirror07", 7.0), (149.0, "dawn07", 12.0), (174.5, "glory07", 10.0), (232.0, "night07", 16.0)],
    light=dict(pos=STAR, color="#ffd8a0", strength=STAR_LIGHT, size=0.6, rays=0.6),
    float_field=dict(count=600, center=(0.0, -45.0), radius=(8.0, 160.0)),
    floats=Track([(0.0, 0.0), (98.0, 0.0), (106.0, 0.85), (137.0, 0.85), (149.0, 0.4), (185.0, 0.4),
                  (198.0, 0.9), (232.0, 0.9), (246.0, 0.25), (TOTAL, 0.25)]),
    lantern_field=dict(count=220, center=(0.0, -160.0), radius=(40.0, 220.0)),
    lanterns=Track([(0.0, 0.0), (200.0, 0.0), (208.0, 0.6), (230.0, 0.6), (240.0, 0.0), (TOTAL, 0.0)]),
    lantern_color="#ffc070",
    arch=dict(lit=_arch_lit, colors=COL, span=_arch_span, height=_arch_height, z=0.0, center=_arch_center,
              yaw=_arch_yaw, line=_arch_line, bright=1.5),
    react=dict(beat=0.12, level=0.12),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=53.3, strength=0.35, rise=0.4, fall=1.2, color="#ffb08a"),
            dict(t=161.4, strength=0.18, rise=0.6, fall=1.5, color="#ffd8a8"),
            dict(t=217.0, strength=0.18, rise=1.2, fall=2.5, color="#ffe2b0")],
    motion_blur=0.3,
)

TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(_base.TAGLINE, t0=1e9, t1=1e9 + 1)
# LIVE clock (render.py draws the cards on the stage video's own time): the opening is whole from frame 0 to
# 7.3 s, crumbles away by 8.6 s; the signature fades in from 8.0 s and stays to the last frame
TITLES = dict(opening=dict(t_end=8.6, dissolve=1.3, build=0.0, y=0.37, palette="night"),
              signature=dict(windows=[(8.0, 1e9, "tl", "night")], fade=0.9))
FRAGMENTS = []
WAVES = []
