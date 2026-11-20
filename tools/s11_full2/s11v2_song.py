"""Song 11, Almighty God Who Knows the Future (the finale): the full-length concert backdrop, VERSION 2
("The Morning That Was Foretold", design: project-docs/designs/11 Almighty God Who Knows the Future.md).

Built on the approved Nine Colours Revision 3 craft (pinned Film 10 engine d928ff9 for the world, the camera and
the renderer; Claude Final v1, commit f43f451, for the serif words with coloured capsule labels and the warm gold
glitter people), with song 11's own scenery and signature effects. Version 2 rebuilds the first run (branch
backdrop/s11-full, a night picture timed to the 4:28 file) to the project rules: the live length, 60 fps, the
radiant full sunrise look, navy words on the bright sky, no comets, relights only, the opening lockup and the top
left signature, the call to action and the official end card with the closing tagline.

CLOCK. Every time in this file is REFERENCE time in seconds: 0 is the first sample of the church choir upload
(268.224 s file; first sound 0.60 s, last chord rung out 262.60 s). The stage video plays 0.60 to 262.60 in exactly
the live length, 260.0 s (tools/s11_full2/render.py: ref = 0.60 + v * 262 / 260), then holds 15 s (ref 262.6 to
277.6), calm and alive, never black. Timeline and cues: project-docs/backdrops/s11-full2/TIMELINE.md and CUES.md.

SIGNATURE EFFECTS (design sections 5 to 8; none used in another song)
  THE PROMISE FULFILLED  a heavenly city drawn ahead of time in faint silver lines on the far shore (terraces,
                         towers, one great arched gate whose curve is the arch of nine lights); the gate and the
                         towers catch the glory first, then it fills with gold from the bottom up
  ALL NATIONS            two rivers of light in many soft colours flow in across the lake from both edges and warm
                         into gold as they reach the city
  WAVES OF PRAISE        gold rings roll out from the city on the choral accents; at "endures forever" they circle
                         the city and stay
  MOTHER'S ROAD          a violet-gold road unrolls across the water from Heavenly Mother's feet to the city
  THE GATE               the arch of nine lights comes down out of the sky and settles on the city's gate, nine
                         jewels in its curve; the gate opens and the sun rises inside it; at the end the nine
                         lights rise back into the sky

No em dash or en dash anywhere in this file.
"""
import os
import sys

import numpy as np

import songs.s03_original as _base

MUSIC_FILE_END = 262.60           # the last chord has rung out (reference clock)
MUSIC_END = 262.60
HOLD = 15.0
TOTAL = MUSIC_FILE_END + HOLD     # 277.6 reference seconds = 275.0 s of stage video (16,500 frames at 60 fps)
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = MUSIC_END
_base.SONG_END = MUSIC_FILE_END
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
from p3d.camera import Move, Rig  # noqa: E402
from p3d.world import _day  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "nine_colours_minor"))
import reference  # noqa: E402,F401  (registers nine_reference_p3d: Claude Final v1 words and bodies)
from nine_reference_p3d import words as PW  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley.mp3"     # not used for the picture (FEATURES are this song's)
NFRAMES = int(round(TOTAL * FPS))
SONG_END = MUSIC_FILE_END
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE
FRAGMENTS = []
WAVES = []

# ---------------------------------------------------------------------------------------------------------
# The measured music (TIMELINE.md), reference seconds
# ---------------------------------------------------------------------------------------------------------
CALLS = (21.7, 31.3)                          # the choir's opening calls
FATHER = 40.7                                 # Father, who knows the future
GLORY = 53.9                                  # the glory of Jerusalem
FULFIL = (61.0, 69.5)                         # prophecy fulfilled
NATIONS = (62.5, 80.0)                        # all nations stream in
PRAISE = (74.7, 79.3, 82.0, 85.9, 90.9)       # the choral accents: waves of praise
FIRM1 = (90.9, 100.0)                         # standing firm on Mount Zion
BREATH = (117.0, 121.5)                       # the morning hush between the verses
MOTHER_T = (121.5, 153.0)                     # Mother, who planned the future; her words; the road
KINGS = (155.5, 171.0)                        # kings run in; the second lift
FOREVER = 160.1                               # joy that endures forever
FIRM2 = (171.6, 179.0)
CLIMAX = 179.0                                # Her sacrifice and wondrous love: the arch blazes
DESCENT = (184.0, 199.0)                      # the arch comes down onto the gate
GATE_OPEN = 199.8                             # the gate opens, the sun rises in it
LIFT_HANDS = 224.2                            # the coda's thanks: hands lifted
FINAL_RISE = 249.6                            # the final rise
ARCH_HOME = (251.0, 259.0)                    # the nine lights rise back into their arch
CTA = (247.4, 248.6, 259.6, 260.5)            # the call to action: in, read, read end, out
END_CARD = 260.7                              # the official end card sweeps in (readable 261.4 to the end)
HITS = dict(call=21.7, father=40.7, glory=53.9, accent=74.7, gate=199.8, rise=249.6)

LABELS = PW.LABELS
COL = [PW.COLORS[k] for k in LABELS]
GREET, GRAT, APOL, INCL, CONC, RESP, ENC, CONS, COMP = range(9)
NAVY, WHITE = "#1f2a6b", "#ffffff"


def _ss(a, b, x):
    if b <= a:
        return (np.asarray(x, np.float64) >= a).astype(np.float64)
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _sc(a, b, x):
    return float(_ss(a, b, x))


def _bump(t, a, b, c, d):
    return _sc(a, b, t) * (1.0 - _sc(c, d, t))


def _smoother(u):
    u = min(max(float(u), 0.0), 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


def _rgb(hexs, k=1.0):
    return lin(hexs) * k


# ---------------------------------------------------------------------------------------------------------
# Geography (metres, y up, the lake is y = 0; we look toward -z, where the city stands on the far shore)
# ---------------------------------------------------------------------------------------------------------
CITY_Z = -120.0                    # the front of the city (the gate's plane)
GATE_SPAN, GATE_H = 24.0, 21.0     # the gate's arc: exactly the Arch formula (so the arch of nine lights fits it)
ARCH = dict(span=110.0, height=50.0, z=-70.0)
MOTHER = _v(-3.2, 0.0, 22.0)       # Heavenly Mother on the near shore, left (seen from behind)
ENC_AT = _v(1.5, 0.0, 19.6)        # the Encouragement pair, before her on the road
GRAT_AT = _v(0.0, 0.0, -40.0)      # the Gratitude pair, on the shining water before the city
ROAD0, ROAD1 = _v(-2.6, 0.02, 19.5), _v(0.0, 0.02, CITY_Z + 6.0)
GATE_MOTHER = _v(0.0, 0.0, CITY_Z - 3.0)     # Heavenly Mother inside the open gate (from behind)


def _arc(u, span, height):
    th = np.radians(172.0 - 164.0 * np.asarray(u, np.float64))
    return 0.5 * span * np.cos(th), height * np.sin(th)


# ---------------------------------------------------------------------------------------------------------
# The camera: one grand steady view with a high horizon, slow purposeful moves, and two held medium shots for
# the two expressions (performers stand in front: never fast, no orbits)
# ---------------------------------------------------------------------------------------------------------
OPEN = (_v(0.0, 6.0, 62.0), _v(0.0, 48.0, -100.0), 46.0)          # the opening: horizon low, the lockup on sky
HOME = (_v(0.0, 7.0, 62.0), _v(0.0, 15.0, -100.0), 46.0)          # horizon about 0.56 from the top
HOME_IN = (_v(0.0, 7.2, 40.0), _v(0.0, 15.5, -120.0), 45.0)        # verse 1: a gentle push toward the city
MOTHER_SHOT = (_v(-0.8, 2.4, 30.2), _v(0.4, 2.2, 0.0), 42.0)    # behind Heavenly Mother, the road ahead
MOTHER_B = (_v(-0.7, 2.45, 29.6), _v(0.3, 2.25, 0.0), 41.0)
ROAD_SHOT = (_v(0.0, 6.0, 30.0), _v(0.0, 2.0, -100.0), 46.0)     # after the words: the walkers on the road
LIFT = (_v(0.0, 17.0, 70.0), _v(0.0, 17.0, -120.0), 50.0)          # the second lift: the whole world in view
GATE_SHOT = (_v(0.0, 6.0, -56.0), _v(0.0, 10.0, -120.0), 44.0)    # the glide toward the gate
GATE_B = (_v(0.0, 6.2, -62.0), _v(0.0, 10.4, -120.0), 44.0)
END = (_v(0.0, 7.2, 58.0), _v(0.0, 15.5, -100.0), 46.0)


def _medium(at, yaw=0.0, d=9.4, h=1.95, ty=1.30, fov=36.0):
    a = np.radians(yaw)
    back = _v(np.sin(a), 0.0, np.cos(a))
    return at + back * d + _v(0.0, h, 0.0), at + _v(0.0, ty, 0.0), fov


GRAT_SHOT = _medium(GRAT_AT, yaw=0.0, d=8.6, h=1.7, ty=2.35)

# (time, pose, move seconds): the camera holds a pose until the next key's move starts; a key with a move
# duration eases from the previous pose to its own over that many seconds, ending at its time.
SHOTS = [
    (0.0, OPEN, 0.0),
    (9.0, OPEN, 0.0),
    (30.0, HOME, 21.0),                       # the sky lowers to the city as the sun comes
    (40.0, HOME, 0.0),
    (100.0, HOME_IN, 58.0),                   # verse 1: a slow push toward the city
    (106.0, GRAT_SHOT, 6.0),                  # down to the Gratitude pair on the shining water
    (121.0, GRAT_SHOT, 0.0),
    (127.0, MOTHER_SHOT, 6.0),                # behind Heavenly Mother on the near shore
    (142.5, MOTHER_B, 15.5),
    (150.0, ROAD_SHOT, 7.5),                  # the walkers go out along the road
    (158.0, LIFT, 8.0),                       # the second lift: one majestic slow rise
    (180.0, LIFT, 0.0),
    (198.0, GATE_SHOT, 18.0),                 # the glide toward the gate as the arch comes down
    (236.0, GATE_B, 38.0),
    (252.0, END, 16.0),                       # a slow settle back to the home view
    (TOTAL + 1.0, END, 0.0),
]


def _pose(t):
    prev = SHOTS[0][1]
    for tk, pose, dur in SHOTS:
        if t < tk - dur:
            return prev, prev, 0.0
        if t < tk:
            return prev, pose, _smoother((t - (tk - dur)) / max(dur, 1e-6))
        prev = pose
    return prev, prev, 0.0


def _cam_raw(t):
    a, b, u = _pose(t)
    p = a[0] * (1.0 - u) + b[0] * u
    da, db = a[1] - a[0], b[1] - b[0]
    la, lb = float(np.linalg.norm(da)), float(np.linalg.norm(db))
    d = _unit(_unit(da) * (1.0 - u) + _unit(db) * u) * (la * (1.0 - u) + lb * u)
    fov = a[2] * (1.0 - u) + b[2] * u
    p = p + _v(0.05 * np.sin(0.21 * t), 0.03 * np.sin(0.17 * t + 1.0), 0.0)     # gently alive
    return p, p + d, fov


class Path(Move):
    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q, _ = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


def _focus_dist(t):
    p, q, _ = _cam_raw(t)
    return float(np.linalg.norm(q - p))


CAMERA = Rig([Path(_cam_raw, -1.0, TOTAL + 2.0, blend=0.0, fov=lambda t: _cam_raw(t)[2], roll=0.0,
                   aperture=0.0, focus=_focus_dist)],
             blend=0.0, fov=46.0, aperture=0.0, handheld=0.0, min_height=0.3)
_LAYOUT = CAMERA


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# ---------------------------------------------------------------------------------------------------------
# The arch of nine lights: lit from the start (songs 01 to 08 lit all nine); song 11 lights nothing new. It
# blazes at the climax, comes down onto the gate, and rises back into the sky at the end.
# ---------------------------------------------------------------------------------------------------------
def _descent(t):
    """0 in the sky, 1 settled on the gate."""
    return _smoother((t - DESCENT[0]) / (DESCENT[1] - DESCENT[0])) * (1.0 - _smoother(
        (t - ARCH_HOME[0]) / (ARCH_HOME[1] - ARCH_HOME[0])))


def _arch_span(t):
    k = _descent(t)
    return ARCH["span"] * (1.0 - k) + GATE_SPAN * k


def _arch_height(t):
    k = _descent(t)
    return ARCH["height"] * (1.0 - k) + GATE_H * k


def _arch_center(t):
    k = _descent(t)
    return (0.0, 0.0, (CITY_Z - ARCH["z"]) * k)


def _flare(t, t0, amp=0.9, tau=1.6):
    if t < t0 - 0.4:
        return 0.0
    if t < t0:
        return amp * _sc(t0 - 0.4, t0, t)
    return amp * float(np.exp(-(t - t0) / tau))


EXPR_T = dict(Gratitude=(109.4, 111.2, 120.4, 122.6), Encouragement=(130.6, 132.3, 141.6, 143.8))
ARCH_FLARE = {GRAT: EXPR_T["Gratitude"][3] - 0.2, ENC: EXPR_T["Encouragement"][3] - 0.2}


def _arch_lit(t):
    out = []
    blaze = 0.55 * _bump(t, CLIMAX, CLIMAX + 4.0, 196.0, 201.0)            # each star sings its own colour
    home = 0.30 * _bump(t, ARCH_HOME[0], ARCH_HOME[1], 268.0, 276.0)     # brighter than ever, back in the sky
    for k in range(9):
        b = 0.95 + blaze + home + 0.12 * _sc(GATE_OPEN, GATE_OPEN + 3.0, t)
        # the choir's calls: a wave of light along the arch, star to star
        for c in CALLS:
            b += 0.45 * _flare(t, c + 0.30 * k, 1.0, 0.9)
        # Father's voice: the nine ring in turn, left to right
        b += 0.40 * _flare(t, FATHER + 1.2 + 0.35 * k, 1.0, 1.2)
        age = 30.0
        if k in ARCH_FLARE:
            b += _flare(t, ARCH_FLARE[k], 0.85)
            if t >= ARCH_FLARE[k]:
                age = min(age, t - ARCH_FLARE[k])
        out.append((b, age))
    return out


ARCH_CFG = dict(lit=_arch_lit, colors=COL, bright=1.7, span=_arch_span, height=_arch_height, z=ARCH["z"], center=_arch_center,
                line=lambda t: (0.55 + 0.35 * _descent(t)) * _sc(8.6, 12.0, t))


def arch_positions(t):
    from p3d.world import Arch
    return Arch(None, **{k: v for k, v in ARCH_CFG.items() if k not in ("lit",)}).positions(t)


# ---------------------------------------------------------------------------------------------------------
# The words: two of the nine (exact campaign wording, navy letters with a soft white glow on the bright sky,
# the capsule label in the expression's colour) and five short fragments of the song, each with its own way in
# ---------------------------------------------------------------------------------------------------------
DEPTH = 7.0
RIDE_Y = .625                      # block centre about .345 of the height from the top


def _width(t, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * DEPTH * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


# Each word is made in three steps, so that every reading is crisp navy on the bright sky (DESIGN-SYSTEM 7):
#   ARRIVE  the particle word (warm light) forms with its own effect and holds for a moment;
#   READ    crisp navy letters with a soft white glow (drawn over the finished picture by titles_s11v2.py, in
#           the same place and size) fade in as the particles dissolve, and are read 8 to 10 s (expressions)
#           or about 5 s (fragments);
#   LEAVE   a second particle copy forms under the navy letters as they fade, and leaves with its own effect
#           (an expression collapses into its own star of the arch).
_LIGHT = dict(color="#fff4e0", glow="#ffe2a8", tint=0.25, bright=0.9, halo=1.0)
_FRAG = dict(ride=(0.5, RIDE_Y, DEPTH), face="screen", label="", nib=False, font="tag", **_LIGHT)
FRAG_T = {
    "glory": (54.0, 56.2, 61.4, 63.0),
    "nations": (70.4, 72.4, 77.0, 78.6),
    "joy": (81.4, 83.0, 88.0, 89.6),
    "zion": (94.4, 96.0, 101.0, 102.6),
    "forever": (160.2, 162.2, 168.0, 169.8),
}
FRAG_LINES = {"glory": ["The glory of Jerusalem"], "nations": ["All nations"], "joy": ["Joy of salvation"],
              "zion": ["Mount Zion"], "forever": ["Joy of salvation", "endures forever"]}
FRAG_WIDTH = {"glory": 0.50, "nations": 0.28, "joy": 0.38, "zion": 0.30, "forever": 0.38}
# arrive, leave (each fragment its own effect, grown from the song's imagery; design section 8)
FRAG_FX = {"glory": ("pen", "fade"),          # written by the first ray from the gate, a stroke of a golden pen
           "nations": ("gather", "stream"),   # many small lights from every side come together; pour into the rivers
           "joy": ("lake", "sink"),           # rises out of the shining water like spray; falls back as drops
           "zion": ("reveal", "sink"),        # steady and heavy, then sinks back into the ridge
           "forever": ("stitch", "rise")}     # stitched in gold sparks while the rings circle the city; rises
EXPR_WIDTH = {"Gratitude": 0.52, "Encouragement": 0.50}
EXPR_FX = {"Gratitude": "gather",             # the sparks of thanks rising from everyone gather into the words
           "Encouragement": "reveal"}         # written left to right, the direction of walking
READS = {}                                    # name: (read start, read end) of the navy letters


def _pair(base, a, b, c, d, arrive, leave, **kw):
    """The arriving and the leaving particle words of one reading (a, b, c, d: in, read, read end, out)."""
    READS[base["name"]] = (b, c)
    w = base["width"]
    one = dict(base, t_in=a, t_read0=b, t_read1=b + 0.6, t_out=b + 1.6, arrive=arrive, leave="fade", width=w)
    two = dict(base, name=base["name"] + " out", t_in=c - 0.7, t_read0=c - 0.05, t_read1=c + 0.15, t_out=d,
               arrive="reveal", leave=leave, width=w, **kw)
    return [one, two]


WORD_SPECS = []
for _n, (_a, _b, _c, _d) in FRAG_T.items():
    WORD_SPECS += _pair(dict(_FRAG, name=_n, lines=FRAG_LINES[_n], width=_width(0.5 * (_b + _c), FRAG_WIDTH[_n])),
                        _a, _b, _c, _d, *FRAG_FX[_n])
for _n, _k in (("Gratitude", GRAT), ("Encouragement", ENC)):
    _a, _b, _c, _d = EXPR_T[_n]
    WORD_SPECS += _pair(dict(expr=_n, name=_n, ride=(.5, RIDE_Y, DEPTH), face="screen", nib=False,
                             width=_width(0.5 * (_b + _c), EXPR_WIDTH[_n]), pill=PW.COLORS[_n], **_LIGHT),
                        _a, _b, _c, _d, EXPR_FX[_n], "arch", to=lambda t, k=_k: arch_positions(t)[k])

WORDS = PW.Words(WORD_SPECS, camera=_LAYOUT, reflect=False)
_BOX = {}


def read_box(name):
    """The navy letters' place: the particle word's own screen box (x0, x1, y0, y1; 0..1, y up) at its reading."""
    if name not in _BOX:
        w = [x for x in WORDS if x.name == name][0]
        t = READS[name][0]
        x0, x1, y0, y1 = (float(v) for v in PW.screen_box(w, CAMERA.state(t), t)[:4])
        # the words ride the screen: centre the box on the ride point (the size is the word's own)
        hw, hh = 0.5 * (x1 - x0), 0.5 * (y1 - y0)
        _BOX[name] = (0.5 - hw, 0.5 + hw, RIDE_Y - hh, RIDE_Y + hh)
    return _BOX[name]


def read_alpha(name, t):
    r0, r1 = READS[name]
    return float(_ss(r0 - 0.2, r0 + 0.8, t) * (1.0 - _ss(r1 - 0.25, r1 + 0.55, t)))


def read_text(name):
    """(label, lines, label colour) of a reading."""
    if name in FRAG_LINES:
        return "", FRAG_LINES[name], None
    e = PW.EXPRESSIONS[PW.LABELS.index(name)]
    return e["label"], e["lines"], e["color"]


def word_boxes(t, cam):
    out = []
    for name in READS:
        if read_alpha(name, t) > 0.0:
            x0, x1, y0, y1 = read_box(name)
            out.append((x0 - .03, x1 + .03, y0 - .045, y1 + .045))
    for w in WORDS:
        if w.t_in - 0.3 <= t <= w.t_out + 0.3:
            x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            if front and t <= w.t_read1 + 0.6:
                out.append((x0 - .03, x1 + .03, y0 - .045, y1 + .045))
    return out


# the signature's box (top left, screen units, y up) with its 40 px of clear space; nothing passes over it
SIG_T0 = 8.2
SIG_BOX = (0.0, 0.38, 0.76, 1.0)


def _cta_box(t):
    if CTA[0] - 0.5 <= t <= CTA[3] + 0.3:
        return [(0.10, 0.90, 0.50, 0.86)]
    return []


def _bottom_gain(y):
    """The bottom third stays calm: nothing bright below a third of the height (performers stand there)."""
    return _ss(0.27, 0.40, y)


class Clear:
    """Light dims inside the reading boxes (nothing crosses a word), inside the signature's corner, and in the
    bottom third (calm for the performers). bottom=False leaves the bottom third to the source (people)."""
    wants_camera = True

    def __init__(self, inner, bottom=True, words=True):
        self.inner = inner
        self.bottom = bottom
        self.words = words

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1

    def __getattr__(self, name):
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = (word_boxes(t, cam) + _cta_box(t)) if self.words else []
        if t >= SIG_T0 - 1.0:
            boxes = boxes + [SIG_BOX]
        if not boxes and not self.bottom:
            return got
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            if len(p) == 0:
                continue
            xy, z = cam.project(p)
            end = None
            if b.get("pos2") is not None:
                end, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
            gain = np.ones(len(p))
            for u in (np.linspace(0, 1, 5) if end is not None else [0]):
                q = xy if end is None else xy * (1 - u) + end * u
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / .025 + .5, 0, 1)
                    gain = np.minimum(gain, 1 - .98 * f * (z > 0))
                if self.bottom:
                    gain = gain * np.where(z > 0, _bottom_gain(q[:, 1]), 1.0)
            b["alpha"] = np.asarray(b.get("alpha", 1)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


# ---------------------------------------------------------------------------------------------------------
# THE PROMISE FULFILLED: the heavenly city on the far shore
# ---------------------------------------------------------------------------------------------------------
def _segs(a, b, n):
    u = np.linspace(0.0, 1.0, n)[:, None]
    return a[None, :] * (1.0 - u) + b[None, :] * u


class City:
    """Terraces, soft domes, slender towers and one great arched gate, drawn as lines of light. Silver and faint
    from the first frame (the promise); the gate and the towers catch the glory first; at "fulfilled" it fills
    with gold from the bottom up; its windows are warm; its towers breathe with the music."""

    def __init__(self):
        r = np.random.default_rng(1111)
        z0 = CITY_Z
        lines = []          # outline segments (a, b) with a height for the fill order
        fill = []           # glowing points of walls and windows
        tiers = [(-44.0, 44.0, 0.0, 5.0, z0 - 4.0), (-32.0, 32.0, 5.0, 10.0, z0 - 12.0),
                 (-20.0, 20.0, 10.0, 15.0, z0 - 20.0)]
        gx0 = GATE_SPAN * 0.55
        for x0, x1, y0, y1, zz in tiers:
            # the terrace edge, open where the gate looks through (the kingdom's light is seen there)
            lines += [(_v(x0, y1, zz), _v(-gx0, y1, zz)), (_v(gx0, y1, zz), _v(x1, y1, zz)),
                      (_v(x0, y0, zz), _v(x0, y1, zz)), (_v(x1, y0, zz), _v(x1, y1, zz))]
            # windows: rows of warm points along each terrace
            for yy in np.arange(y0 + 1.6, y1 - 0.8, 2.2):
                xs = np.arange(x0 + 1.5, x1 - 1.0, 2.1)
                xs = xs[np.abs(xs) > GATE_SPAN * 0.55]
                for x in xs:
                    fill.append((x + 0.3 * r.normal(), yy, zz + 0.2, 0.0))
            # gardens of light on the terrace top
            for x in np.linspace(x0 + 1.0, x1 - 1.0, int((x1 - x0) / 1.4)):
                if abs(x) < gx0:
                    continue
                fill.append((x, y1 + 0.35 + 0.4 * r.random(), zz - 1.0 - 2.0 * r.random(), 1.0))
        # towers with domes on the upper terraces
        towers = [(-38.0, 5.0, 9.0, z0 - 6.0), (38.0, 5.0, 9.0, z0 - 6.0), (-27.0, 10.0, 9.0, z0 - 14.0),
                  (27.0, 10.0, 9.0, z0 - 14.0), (-15.0, 15.0, 9.0, z0 - 22.0), (15.0, 15.0, 9.0, z0 - 22.0),
                  (-8.0, 15.0, 7.0, z0 - 24.0), (8.0, 15.0, 7.0, z0 - 24.0)]
        self.tower_top = []
        for x, yb, h, zz in towers:
            w = 1.3
            yt = yb + h
            lines += [(_v(x - w, yb, zz), _v(x - w, yt, zz)), (_v(x + w, yb, zz), _v(x + w, yt, zz))]
            th = np.linspace(0.0, np.pi, 9)
            dome = np.stack([x + w * np.cos(th), yt + 1.6 * w * np.sin(th), np.full(9, zz)], axis=1)
            for i in range(8):
                lines.append((dome[i], dome[i + 1]))
            lines.append((_v(x, yt + 1.6 * w, zz), _v(x, yt + 1.6 * w + 2.2, zz)))
            self.tower_top.append(_v(x, yt + 1.6 * w + 2.2, zz))
            for yy in np.arange(yb + 1.5, yt, 2.4):
                fill.append((x, yy, zz + 0.1, 0.0))
        self.tower_top = np.array(self.tower_top)
        # the gate: the arch of nine lights' own curve, on two posts to the water
        u = np.linspace(0.0, 1.0, 41)
        gx, gy = _arc(u, GATE_SPAN, GATE_H)
        gate = np.stack([gx, gy, np.full(41, z0)], axis=1)
        for i in range(40):
            lines.append((gate[i], gate[i + 1]))
        lines += [(_v(gx[0], 0.0, z0), gate[0]), (_v(gx[-1], 0.0, z0), gate[-1])]
        a = np.array([s[0] for s in lines])
        b = np.array([s[1] for s in lines])
        self.la, self.lb = a, b
        self.lh = np.minimum(a[:, 1], b[:, 1])
        self.gate_line = np.zeros(len(lines), bool)
        self.gate_line[-42:] = True
        self.tall = (np.maximum(a[:, 1], b[:, 1]) > 16.0) & ~self.gate_line
        f = np.array(fill)
        self.fp = f[:, :3]
        self.ftop = f[:, 3] > 0.5
        self.fs = r.random((len(f), 3))
        # the river of light flowing from beneath the gate down into the lake
        self.rv = r.random((900, 3))
        # the gate's two doors (pearl light), closed until the sunrise; inside, the kingdom's light
        n = 2600
        q = r.random((n, 2))
        x = (q[:, 0] - 0.5) * GATE_SPAN * 0.98
        ymax = np.interp(np.abs(x), np.abs(gx[:21][::-1]), gy[:21][::-1])
        y = q[:, 1] * ymax
        self.door = np.stack([x, y, np.full(n, z0 - 0.4)], axis=1)
        self.dseed = r.random(n)

    @staticmethod
    def silver(t):
        return 0.22 + 0.10 * _bump(t, CALLS[0], CALLS[0] + 0.6, CALLS[0] + 1.5, CALLS[0] + 3.5) \
            + 0.10 * _bump(t, CALLS[1], CALLS[1] + 0.6, CALLS[1] + 1.5, CALLS[1] + 3.5) \
            + 0.15 * _bump(t, FATHER + 0.5, FATHER + 1.5, FATHER + 2.5, FATHER + 5.0)

    @staticmethod
    def level(t):
        """The gold fill: metres of the city filled, from the bottom up."""
        return 32.0 * _smoother((t - FULFIL[0]) / (FULFIL[1] - FULFIL[0]))

    def sample(self, t):
        out = []
        silver = _rgb("#c8d6ff")
        gold = _rgb("#ffd27a")
        lv = self.level(t)
        catch = _sc(GLORY - 0.5, GLORY + 3.0, t)
        g_line = np.clip((lv - self.lh) / 3.0, 0.0, 1.0)
        g_line = np.maximum(g_line, catch * (self.gate_line | self.tall))
        breath = 1.0 + 0.10 * np.sin(0.9 * t)
        glow = 0.75 + 0.25 * _sc(GATE_OPEN, GATE_OPEN + 4.0, t)
        col = silver[None, :] * (1.0 - g_line)[:, None] + gold[None, :] * g_line[:, None]
        al = self.silver(t) * (1.0 - g_line) + 0.75 * g_line * breath * glow
        out.append(dict(pos=self.la, pos2=self.lb, size=np.where(self.gate_line, 0.30, 0.13), color=col,
                        alpha=al, emit=1.8 + 1.6 * g_line, kind="line"))
        # windows and gardens: warm when filled
        gf = np.clip((lv - self.fp[:, 1]) / 2.5, 0.0, 1.0)
        tw = 0.8 + 0.2 * np.sin(t * (0.6 + self.fs[:, 0]) + 6.0 * self.fs[:, 1])
        garden = np.where(self.ftop, 1.0, 0.0)
        fcol = np.where(garden[:, None] > 0.5, (0.55 * gold + 0.45 * _rgb("#fff1d6"))[None, :],
                        _rgb("#ffcf86")[None, :])
        out.append(dict(pos=self.fp, size=0.30, color=fcol, alpha=(0.05 + 0.85 * gf) * tw * glow, emit=2.2,
                        kind="spark", seed=self.fs[:, 2], twinkle=0.3))
        if lv > 1.0:
            out.append(dict(pos=self.fp[::3], size=2.6, color=gold, alpha=0.035 * gf[::3] * glow, kind="soft"))
            # the river of light from beneath the gate into the lake
            s = self.rv
            f = np.mod(s[:, 0] + 0.06 * t, 1.0)
            x = (s[:, 1] - 0.5) * (3.0 + 9.0 * f)
            z = CITY_Z + 1.0 + 60.0 * f
            p = np.stack([x, np.full(len(f), 0.06), z], axis=1)
            k = _sc(FULFIL[0] + 4.0, FULFIL[1] + 2.0, t)
            out.append(dict(pos=p, size=0.22, color=0.5 * gold + 0.5 * _rgb("#fff4dc"),
                            alpha=k * 0.55 * (1.0 - f) * (0.6 + 0.4 * s[:, 2]), emit=2.0, kind="spark",
                            seed=s[:, 2], twinkle=0.5))
        # the doors: pearl light, closed; they part at the sunrise
        op = _smoother((t - GATE_OPEN) / 3.2)
        if op < 0.999:
            d = self.door.copy()
            sx = np.sign(d[:, 0])
            d[:, 0] = d[:, 0] + sx * op * GATE_SPAN * 0.52
            vis = np.abs(d[:, 0]) < GATE_SPAN * 0.5
            dk = (0.10 + 0.35 * catch * (1.0 - _sc(FULFIL[0], FULFIL[1], t)) + 0.40 * _sc(FULFIL[0], FULFIL[1], t))
            pearl = 0.6 * _rgb("#fff3e6") + 0.4 * _rgb("#ffe0b0")
            out.append(dict(pos=d[vis], size=0.20, color=pearl, alpha=dk * (1.0 - op) * np.ones(int(vis.sum())),
                            emit=1.4, kind="spark", seed=self.dseed[vis]))
        # inside the open gate: the kingdom of heaven, more light than the eye can hold (warm, never white-out)
        if t > GATE_OPEN - 0.5:
            k = _sc(GATE_OPEN, GATE_OPEN + 4.0, t)
            inner = self.door[::2].copy()
            inner[:, 2] -= 6.0
            out.append(dict(pos=inner, size=0.5, color=0.6 * _rgb("#fff6e0") + 0.4 * gold,
                            alpha=0.045 * k * np.ones(len(inner)), emit=1.0, kind="soft"))
        return out


# ---------------------------------------------------------------------------------------------------------
# ALL NATIONS: two rivers of light in many colours flow in from both edges and warm into gold at the city
# ---------------------------------------------------------------------------------------------------------
class Rivers:
    def __init__(self, n=2600):
        r = np.random.default_rng(2222)
        self.s = r.random((n, 4))
        self.side = np.where(np.arange(n) % 2 == 0, -1.0, 1.0)
        self.col = np.array([lin(COL[i % 9]) for i in r.integers(0, 9, n)])

    @staticmethod
    def _curve(u, side):
        p0 = np.stack([side * 150.0, np.zeros_like(u), np.full_like(u, -40.0)], axis=-1)
        p1 = np.stack([side * 55.0, np.zeros_like(u), np.full_like(u, -45.0)], axis=-1)
        p2 = np.stack([side * 12.0, np.zeros_like(u), np.full_like(u, CITY_Z + 8.0)], axis=-1)
        uu = u[:, None]
        return (1 - uu) ** 2 * p0 + 2 * (1 - uu) * uu * p1 + uu * uu * p2

    def amount(self, t):
        return max(_bump(t, NATIONS[0], NATIONS[0] + 6.0, 102.0, 112.0),
                   _bump(t, KINGS[0] - 1.0, KINGS[0] + 4.0, 196.0, 203.0))

    def sample(self, t):
        k = self.amount(t)
        if k <= 0.0:
            return None
        s = self.s
        # the head of each river advances from the edge (filling), then flows steadily
        head = max(_sc(NATIONS[0], NATIONS[0] + 9.0, t), _sc(KINGS[0] - 1.0, KINGS[0] + 6.0, t))
        u = np.mod(s[:, 0] + 0.035 * t * (0.7 + 0.6 * s[:, 1]), 1.0)
        vis = u <= head
        p = self._curve(u, self.side)
        p[:, 0] += (s[:, 2] - 0.5) * 7.0 * (1.0 - 0.6 * u)
        p[:, 2] += (s[:, 3] - 0.5) * 6.0
        p[:, 1] = 0.12
        warm = _ss(0.55, 0.95, u)
        gold = lin("#ffd27a")
        col = self.col * (1.0 - warm)[:, None] * 0.85 + gold[None, :] * warm[:, None]
        al = k * vis * (0.55 + 0.45 * s[:, 3]) * _ss(0.0, 0.06, u)
        return [dict(pos=p, size=0.55, color=col, alpha=al, emit=1.8, kind="spark", seed=s[:, 1], twinkle=0.6),
                dict(pos=p[::6], size=4.0, color=col[::6], alpha=0.05 * al[::6], kind="soft")]


# ---------------------------------------------------------------------------------------------------------
# WAVES OF PRAISE: gold rings from the city on the choral accents; at "endures forever" they circle and stay
# ---------------------------------------------------------------------------------------------------------
class Praise:
    def __init__(self):
        self.ang = np.linspace(0.0, 2.0 * np.pi, 220, endpoint=False)
        r = np.random.default_rng(3333)
        self.j = r.random(220)

    def sample(self, t):
        out = []
        c = _v(0.0, 0.1, CITY_Z + 4.0)
        gold = 0.7 * lin("#ffd27a") + 0.3 * lin("#fff4dc")
        for t0 in PRAISE:
            age = t - t0
            if age < 0.0 or age > 9.0:
                continue
            rad = 6.0 + 26.0 * age
            al = _sc(0.0, 0.4, age) * (1.0 - _sc(4.0, 9.0, age)) * 0.6
            ring = c + np.stack([rad * np.cos(self.ang), np.zeros(220), 0.55 * rad * np.sin(self.ang)], axis=1)
            front = np.sin(self.ang) > -0.2                   # the near half fades before the calm bottom third
            out.append(dict(pos=ring, size=0.35, color=gold, alpha=al * (0.6 + 0.4 * self.j) * front, emit=2.0,
                            kind="spark", seed=self.j, twinkle=0.6))
        # the rings that stay, circling the city slowly
        k = _bump(t, FOREVER - 0.5, FOREVER + 3.0, 200.0, 206.0)
        if k > 0.0:
            for i, rad in enumerate((22.0, 34.0, 46.0)):
                a = self.ang + 0.08 * t * (1 if i % 2 == 0 else -1)
                grow = _sc(FOREVER + 0.8 * i - 0.5, FOREVER + 0.8 * i + 2.5, t)
                ring = c + np.stack([rad * np.cos(a), np.full(220, 0.5 + 1.5 * i), 0.5 * rad * np.sin(a)], axis=1)
                out.append(dict(pos=ring, size=0.28, color=gold, alpha=0.5 * k * grow * (0.5 + 0.5 * self.j),
                                emit=2.0, kind="spark", seed=self.j, twinkle=0.7))
        return out or None


# ---------------------------------------------------------------------------------------------------------
# Father's voice: one deep pulse of warm light from the horizon across the sky, like a great bell
# ---------------------------------------------------------------------------------------------------------
class FatherPulse:
    def __init__(self):
        self.ang = np.linspace(0.0, np.pi, 260)
        self.j = np.random.default_rng(4444).random(260)

    def sample(self, t):
        age = t - FATHER
        if age < 0.0 or age > 7.0:
            return None
        rad = 8.0 + 55.0 * (1.0 - np.exp(-age / 1.8))
        al = _sc(0.0, 0.3, age) * (1.0 - _sc(2.0, 7.0, age)) * 0.7
        c = _v(0.0, 0.0, -200.0)
        p = c + np.stack([rad * 1.6 * np.cos(self.ang), rad * np.sin(self.ang), np.zeros(260)], axis=1)
        col = 0.7 * lin("#ffcf86") + 0.3 * lin("#fff4dc")
        # the lake: one long ripple
        rp = _v(0.0, 0.05, -60.0) + np.stack([rad * 1.6 * np.cos(2 * self.ang), np.zeros(260),
                                              0.35 * rad * np.sin(2 * self.ang)], axis=1)
        return [dict(pos=p, size=0.9, color=col, alpha=al * (0.6 + 0.4 * self.j), emit=2.0, kind="spark"),
                dict(pos=rp, size=0.25, color=col, alpha=0.5 * al * (0.6 + 0.4 * self.j), emit=1.5, kind="spark")]


# ---------------------------------------------------------------------------------------------------------
# The people of the nations on the city's terraces (small and far: lights in the shape of people standing
# shoulder to shoulder), lifting their hands; the sparks of thanks rising from them
# ---------------------------------------------------------------------------------------------------------
def _glyph():
    """A tiny standing person (1.8 m) as points: head, robe, and two arms that can be lifted."""
    r = np.random.default_rng(5)
    pts = []
    for _ in range(14):
        a = r.random() * 2 * np.pi
        pts.append((0.10 * np.cos(a), 1.62 + 0.10 * np.sin(a), 0.0, 0))
    for _ in range(26):
        y = r.random() * 1.45
        w = 0.12 + 0.16 * (1.45 - y) / 1.45
        pts.append(((r.random() - 0.5) * 2 * w, y, 0.0, 0))
    for side in (-1, 1):
        for i in range(6):
            pts.append((side * (0.18 + 0.07 * i), 1.38 - 0.10 * i, 0.0, side))
    return np.array(pts)


class Terraces:
    def __init__(self):
        r = np.random.default_rng(6666)
        g = _glyph()
        self.g = g
        people = []
        for x0, x1, y, zz in [(-42.0, 42.0, 5.0, CITY_Z - 2.0), (-30.0, 30.0, 10.0, CITY_Z - 10.0),
                              (-18.0, 18.0, 15.0, CITY_Z - 18.0), (-58.0, 58.0, 0.0, CITY_Z + 6.0)]:
            for x in np.arange(x0 + 1.0, x1 - 1.0, 1.25):
                if abs(x) < GATE_SPAN * 0.58:
                    continue
                people.append((x + 0.2 * r.normal(), y, zz))
        self.p = np.array(people)
        self.s = r.random((len(self.p), 3))
        self.col = np.array([lin(COL[i % 9]) for i in r.integers(0, 9, len(self.p))])
        self.spark = r.random((1800, 4))

    def amount(self, t):
        return max(_bump(t, FIRM1[0] - 1.0, FIRM1[0] + 3.0, 196.0, 202.0) * 1.0,
                   _sc(GATE_OPEN + 4.0, GATE_OPEN + 9.0, t) * (1.0 - _sc(250.0, 256.0, t)))

    def sample(self, t):
        k = self.amount(t)
        if k <= 0.0:
            return None
        g = self.g
        n, m = len(self.p), len(g)
        lift = max(_bump(t, LIFT_HANDS - 0.5, LIFT_HANDS + 1.5, 236.0, 240.0), _bump(t, 104.0, 106.0, 116.0, 118.0))
        off = g[:, :3].copy()
        arm = g[:, 3] != 0
        # lifted hands: the arm points swing up
        ang = np.radians(-30.0 + 150.0 * lift)
        base = np.array([0.18, 1.38])
        d = np.stack([np.abs(g[arm, 0]) - 0.18, g[arm, 1] - 1.38], axis=1)
        L = np.linalg.norm(d, axis=1)
        off[arm, 0] = np.sign(g[arm, 3]) * (base[0] + L * np.cos(ang))
        off[arm, 1] = base[1] + L * np.sin(ang)
        scale = 1.25
        pos = (self.p[:, None, :] + scale * off[None, :, :]).reshape(-1, 3)
        firm = 0.35 * _bump(t, 94.0, 95.0, 97.0, 100.0) + 0.35 * _bump(t, 174.0, 175.0, 177.0, 180.0)
        warm = _sc(FIRM1[0], FIRM1[0] + 6.0, t)
        gold = lin("#ffd890")
        col = (self.col * 0.5 + 0.5 * gold) * (1.0 - warm) + gold * warm
        col = np.repeat(col, m, axis=0)
        al = np.repeat(k * (0.55 + 0.25 * self.s[:, 0]) * (1.0 + firm), m)
        out = [dict(pos=pos, size=0.14, color=col, alpha=al, emit=1.8, kind="spark")]
        # thousands of sparks of thanks rising together (1:40 to 1:57, and the coda's thanks)
        ks = max(_bump(t, 101.0, 104.0, 116.0, 121.0), _bump(t, LIFT_HANDS, LIFT_HANDS + 2.0, 236.0, 242.0))
        if ks > 0.0:
            sp = self.spark
            src = self.p[(sp[:, 0] * n).astype(int) % n]
            age = np.mod(sp[:, 1] * 6.0 + t, 6.0)
            q = src + np.stack([0.4 * np.sin(age + 6 * sp[:, 2]), 2.6 + 4.2 * age, 0.3 * np.cos(age + 6 * sp[:, 3])],
                               axis=1)
            a = ks * _ss(0.0, 0.6, age) * (1.0 - _ss(4.0, 6.0, age)) * (0.5 + 0.5 * sp[:, 3])
            out.append(dict(pos=q, size=0.30, color=0.6 * gold + 0.4 * lin("#fff4dc"), alpha=a, emit=2.4,
                            kind="spark", seed=sp[:, 2], twinkle=0.7))
        return out


# ---------------------------------------------------------------------------------------------------------
# MOTHER'S ROAD: a violet-gold road unrolls across the water from Her feet to the city; footsteps stay lit
# ---------------------------------------------------------------------------------------------------------
class Road:
    def __init__(self, n=5000):
        r = np.random.default_rng(7777)
        self.s = r.random((n, 3))

    def sample(self, t):
        s = self.s
        unroll = _smoother((t - 132.0) / 5.0)
        promise = 0.10 * _sc(BREATH[0] - 1.0, BREATH[1], t) * (1.0 - unroll)
        k = unroll * (1.0 - 0.6 * _sc(160.0, 170.0, t))
        if promise <= 0.0 and k <= 0.0:
            return None
        u = s[:, 0]
        p = ROAD0[None, :] * (1.0 - u[:, None]) + ROAD1[None, :] * u[:, None]
        width = 1.0 + 1.6 * u
        p[:, 0] += (s[:, 1] - 0.5) * width
        drawn = u <= unroll
        blaze = _bump(t, 151.0, 152.5, 154.0, 160.0)
        warm = np.clip(0.35 + 0.65 * u + blaze, 0.0, 1.0)
        col = lin("#b48cff")[None, :] * (1.0 - warm)[:, None] + lin("#ffd27a")[None, :] * warm[:, None]
        al = np.where(drawn, k, promise) * (0.35 + 0.35 * s[:, 2]) * (1.0 + 0.8 * blaze)
        silver = np.where(drawn, 0.0, 1.0)
        col = col * (1.0 - silver[:, None]) + lin("#c8d6ff")[None, :] * silver[:, None]
        return [dict(pos=p, size=0.07 + 0.16 * u, color=col, alpha=0.75 * al, emit=1.6, kind="spark", seed=s[:, 2],
                     twinkle=0.4)]


# ---------------------------------------------------------------------------------------------------------
# Small things: the relight rings, hearts in the expression colours, the symbols traced in the world
# ---------------------------------------------------------------------------------------------------------
class Relight:
    """A light of the arch shines again: one new thin ring opens round it and stays as a faint halo."""

    def __init__(self, times):
        self.times = times
        self.ang = np.linspace(0.0, 2.0 * np.pi, 72, endpoint=False)

    def sample(self, t):
        out = []
        P = arch_positions(t)
        for k, t0 in self.times.items():
            if t < t0:
                continue
            age = t - t0
            rad = 0.4 + 1.5 * (1.0 - np.exp(-age / 0.7))
            al = 0.85 * np.exp(-age / 0.9) + 0.22 * _sc(0.0, 1.2, age)
            ring = P[k][None, :] + rad * np.stack([np.cos(self.ang), np.sin(self.ang), np.zeros(72)], axis=1)
            out.append(dict(pos=ring, size=0.07, color=0.6 * lin(COL[k]) + 0.4 * lin("#fff1dc"),
                            alpha=al * np.ones(72), emit=2.0, kind="spark", lod=False, dof=0.0))
        return out or None


class SparkHearts:
    """Small hearts of light (each a heart outline drawn in sparks) that drift up off an expression in its
    colour while the words go home to the arch."""

    def __init__(self, items):
        th = np.linspace(0.0, 2.0 * np.pi, 22, endpoint=False)
        x = 16 * np.sin(th) ** 3
        y = 13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)
        self.shape = np.stack([x, y], axis=1) / 34.0
        r = np.random.default_rng(55)
        self.items = []
        for at, k, t1 in items:
            for i in range(9):
                self.items.append((at, k, t1 + 0.1 + 0.35 * i, r.random(4)))

    def sample(self, t):
        pos, al, col = [], [], []
        for at, k, t0, s in self.items:
            age = t - t0
            if age < 0.0 or age > 4.0:
                continue
            a = _sc(0.0, 0.6, age) * (1.0 - _sc(2.6, 4.0, age))
            c = at + _v((s[0] - 0.5) * 1.6 + 0.25 * np.sin(1.3 * age + 6 * s[1]), 1.5 + 0.55 * age,
                        (s[2] - 0.5) * 0.8)
            size = 0.16 + 0.10 * s[3]
            q = c[None, :] + size * np.stack([self.shape[:, 0], self.shape[:, 1], np.zeros(22)], axis=1)
            pos.append(q)
            al.append(np.full(22, 0.85 * a))
            col.append(np.tile(0.8 * lin(COL[k]) + 0.2 * lin("#fff1dc"), (22, 1)))
        if not pos:
            return None
        return [dict(pos=np.concatenate(pos), size=0.035, color=np.concatenate(col), alpha=np.concatenate(al),
                     emit=2.2, kind="spark")]


def _symbols():
    """Each expression's symbol traced in its colour by sparks in the world near its people (subtle, never over
    the words: it forms as the words go home to the arch)."""
    from p3d import brand as BS
    return [BS.Traced("Gratitude", pos=tuple(GRAT_AT + _v(2.9, 1.9, -0.6)), size=0.75, face="camera",
                      camera=CAMERA, t0=EXPR_T["Gratitude"][2] + 0.2, dur=1.6, hold=2.2, out=1.4, intensity=0.26,
                      reflect=False),
            BS.Traced("Encouragement", pos=tuple(ENC_AT + _v(2.8, 1.9, -0.8)), size=0.75, face="camera",
                      camera=CAMERA, t0=EXPR_T["Encouragement"][2] + 0.2, dur=1.6, hold=2.2, out=1.4,
                      intensity=0.26, reflect=False)]


# ---------------------------------------------------------------------------------------------------------
# The people of light (warm gold glitter only; every touch between two of the same gender, or Mother and
# her children)
# ---------------------------------------------------------------------------------------------------------
GOLD = dict(look="glitter", color="#f09a30", color2="#ffd27a", bright=2.1)
GOLD2 = dict(look="glitter", color="#f4a83c", color2="#ffdc90", bright=2.1)


def _view(at, cam_pos):
    d = np.asarray(cam_pos, np.float64) - np.asarray(at, np.float64)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _toward(a, b):
    d = np.asarray(b, np.float64) - np.asarray(a, np.float64)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _mother():
    """Heavenly Mother on the near shore, only from behind: fully robed, veiled to the ground, facing the city.
    She stands with her children, raises her right hand toward the city as the road unrolls, then walks out
    along it ahead of them and dissolves into sparks that run on to the gate."""
    from nine_reference_p3d.body import Body
    city = _v(0.0, 10.0, CITY_Z)
    face = _toward(MOTHER, ROAD1)
    hand = MOTHER + _v(0.55, 2.55, -0.9)
    return Body("woman", at=(MOTHER[0], MOTHER[2]), facing=face, garment="robe", veil=dict(length=1.5),
                look=dict(name="glitter", seams=0.3), color="#f8b040", color2="#ffe2a0", bright=2.2, points=70000,
                show=(122.0, 153.5), fade=2.0, seed=3.3, wind=(0.15, 0.0, 0.05),
                motion=[(-1e9, "stand"), (143.6, "walk", dict(speed=0.8))],
                gesture=[(130.2, 141.2, "raise_hand", dict(side="R", to=hand, palm="fwd", fingers="open",
                                                           ease_in=1.6, ease_out=1.8))],
                effects=[dict(kind="form", t=122.0, dur=2.6)])


def _encouragement():
    """ENCOURAGEMENT, two women before Mother on the road: a hand on the shoulder of a friend kneeling in prayer,
    both heads bowed (the campaign: sincere support for someone in a hard time)."""
    from nine_reference_p3d import acting
    t0, t1 = EXPR_T["Encouragement"][1] - 1.0, EXPR_T["Encouragement"][2]
    view = _view(ENC_AT, MOTHER_SHOT[0]) % 360.0
    sa = dict(shape="woman", garment="dress", **GOLD2)
    sb = dict(shape="woman", garment="dress", hair="bun", **GOLD)
    return list(acting.perform("Encouragement", t0, t1, at=(ENC_AT[0], ENC_AT[2]), view=view, variant="shoulder",
                               style=dict(points=70000, fade=0.8), style_a=sa, style_b=sb, pre=4.0, post=2.0,
                               seed=8.0))


def _gratitude():
    """GRATITUDE, two men on the shining water before the city: one clasps the other's offered hand in both
    hands and bows; the other lays a hand on his heart (thanks named for a kindness, all thanks to you)."""
    from nine_reference_p3d import acting
    t0, t1 = EXPR_T["Gratitude"][1] - 1.0, EXPR_T["Gratitude"][2]
    view = _view(GRAT_AT, GRAT_SHOT[0]) % 360.0
    sa = dict(shape="man", garment="tunic", **GOLD2)
    sb = dict(shape="man", garment="coat", **GOLD)
    return list(acting.perform("Gratitude", t0, t1, at=(GRAT_AT[0], GRAT_AT[2]), view=view, variant="clasp",
                               style=dict(points=70000, fade=0.8), style_a=sa, style_b=sb, pre=2.5, post=2.0,
                               seed=3.0))


def _gate_family():
    """Inside the open gate, small and far but unmistakable: Heavenly Mother from behind, her arms opening to
    receive her children home; two children run the last steps to her."""
    from nine_reference_p3d.body import Body
    m = GATE_MOTHER
    sc = 6.0
    l_hand = m + _v(-1.25 * sc / 1.6 * 1.0, 1.30 * sc, 0.25)
    r_hand = m + _v(1.25 * sc / 1.6 * 1.0, 1.30 * sc, 0.25)
    mother = Body("woman", at=(m[0], m[2]), facing=180.0, garment="robe", veil=dict(length=1.5),
                  look=dict(name="glitter", seams=0.3), color="#f6a838", color2="#ffe8b0", bright=3.0, points=80000,
                  scale=sc, show=(202.5, 250.5), fade=2.5, seed=4.4,
                  gesture=[(205.5, 247.0, "raise_hand", dict(side="L", to=l_hand, palm="fwd", fingers="open",
                                                             ease_in=2.6, ease_out=2.0)),
                           (205.5, 247.0, "raise_hand", dict(side="R", to=r_hand, palm="fwd", fingers="open",
                                                             ease_in=2.6, ease_out=2.0))],
                  effects=[dict(kind="form", t=202.5, dur=3.0)])
    kids = []
    for i, x in enumerate((-2.2, 2.4)):
        start = m + _v(x * sc, 0.0, 9.0 * sc / 1.6)
        kids.append(Body("child", at=(start[0], start[2]), facing=180.0 + (8.0 if x < 0 else -8.0),
                         motion=[(-1e9, "stand"), (209.0 + 1.2 * i, "run", dict(speed=0.55)),
                                 (215.5 + 1.2 * i, "stand")],
                         gesture=[(216.0 + 1.2 * i, 247.0, "raise_hand", dict(side="R" if x < 0 else "L",
                                                                              to=m + _v(0.0, 1.0 * sc, 0.0),
                                                                              ease_in=1.2))],
                         garment="tunic", scale=sc, points=26000, show=(207.0, 250.5), fade=2.0, seed=5.0 + i,
                         effects=[dict(kind="form", t=207.0, dur=2.0)], **GOLD2))
    return [mother] + kids


_CAST = {}


def cast():
    if _CAST:
        return _CAST
    from nine_reference_p3d import master_acting  # noqa: F401  (greet_bow, sway, comfort...)
    _CAST["mother"] = [_mother()]
    _CAST["encouragement"] = _encouragement()
    _CAST["gratitude"] = _gratitude()
    _CAST["gate"] = _gate_family()
    return _CAST


def _setup(scene):
    for e in scene.entries():
        if e.name in ("_arch", "_floats", "_lanterns", "_dust"):
            e.pointset = Clear(e.pointset, bottom=(e.name != "_arch"))
        if e.name in ("_stars", "_arch", "_lanterns", "_dust", "_floats"):
            e.reflect = False                  # no bright reflections or glints in the calm bottom third
    scene.add("city", Clear(City()), reflect=False)
    scene.add("rivers", Clear(Rivers()), reflect=False)
    scene.add("praise", Clear(Praise()), reflect=False)
    scene.add("father", Clear(FatherPulse()), reflect=False)
    scene.add("terraces", Clear(Terraces()), reflect=False)
    scene.add("road", Clear(Road()), reflect=False)
    scene.add("relight rings", Clear(Relight(ARCH_FLARE), bottom=False), reflect=False)
    scene.add("hearts", Clear(SparkHearts([(GRAT_AT, GRAT, EXPR_T["Gratitude"][2]),
                                           (ENC_AT, ENC, EXPR_T["Encouragement"][2])])), reflect=False)
    for i, fx in enumerate(_symbols()):
        scene.add(f"symbol {i}", Clear(fx), reflect=False)
    for group, bodies in cast().items():
        for i, b in enumerate(bodies):
            if hasattr(b, "add"):
                b.add(scene, f"{group} {i}", reflect=False)
            else:
                scene.add(f"{group} {i}", Clear(b, bottom=False))
    WORDS.add_to(scene, reflect=False)
    for e in scene.entries():
        if e.name.startswith("word "):
            e.pointset = Clear(e.pointset, bottom=False, words=False)   # a leaving word never crosses the signature


# ---------------------------------------------------------------------------------------------------------
# The world: the hand-off night of song 10, a sunrise through the opening calls, then the brightest morning of
# the concert (white gold, sky blue, all nine colours), the sun rising inside the gate at the climax
# ---------------------------------------------------------------------------------------------------------
SUN_HIDDEN = 0.3                  # the sun held back behind the city until the gate opens


def _sun_el(t):
    if t < GATE_OPEN - 1.0:
        return SUN_HIDDEN
    u = _smoother((t - (GATE_OPEN - 1.0)) / 6.0)
    up = _smoother((t - 236.0) / 22.0)
    return SUN_HIDDEN * (1.0 - u) + 5.6 * u + 6.4 * up


LOOKS = dict(
    handoff=dict(base="night", sky_top="#03051a", sky_mid="#0d1442", sky_hor="#3a3260", sun_az=180.0,
                 sun_el=-3.0, sun_color="#ffd08c", sun_int=0.45, sun_size=0.8, sun_disc=4.0, sun_glow=0.35,
                 stars=0.9, milky=0.0, clouds=0.0, hills=0.85, hill_color="#05060f", haze=0.45,
                 haze_color="#2a2c5e", mist=0.15, mist_color="#22285a", water="#01030a", ripple=0.05,
                 dust=0.4, dust_color="#ffd9a0", dust_color2="#ffcf8a", bokeh=0.4, rays=0.0),
    dawn11=dict(base="night", sky_top="#0f1b46", sky_mid="#4a3a80", sky_hor="#f09a78", sun_az=180.0, sun_el=-2.0,
                sun_color="#ffd08c", sun_int=0.9, sun_size=0.9, sun_disc=4.0, sun_glow=0.7, stars=0.35, milky=0.0,
                clouds=0.0, hills=0.85, hill_color="#1a1430", haze=0.65, haze_color="#c98a7e", mist=0.35,
                mist_color="#a87878", water="#08081a", ripple=0.15, rays=0.4, dust=0.5, dust_color="#ffd9a0",
                dust_color2="#ffc4b0", bokeh=0.5),
    sunrise11=dict(base="day", sky_top=_day("#1f4ea8", 0.86), sky_mid=_day("#7aaee0", 0.84), sky_hor=_day("#ffc878", 0.82),
        sun_az=180.0, sun_el=SUN_HIDDEN, sun_color="#fff0cc", sun_int=1.1, sun_size=1.1, sun_disc=3.0,
        sun_glow=1.0, stars=0.0, clouds=0.0, hills=0.85, hill_color=_day("#46508c", 0.50), haze=0.25,
        haze_color=_day("#f0a860", 0.6), mist=0.05, mist_color=_day("#f8d8a0", 0.5), water=_day("#1a447f", 0.42),
        mirror=0.7, mirror_min=0.35, exposure=0.92, ripple=0.25, rays=0.7, dust=0.5, dust_color="#fff8ec",
        dust_color2="#ffd27a", bokeh=0.5),
    radiant=dict(base="day", sky_top=_day("#1d5bb5", 0.86), sky_mid=_day("#7cbcea", 0.84), sky_hor=_day("#ffe0a0", 0.82),
        sun_az=180.0, sun_el=SUN_HIDDEN, sun_color="#fff0cc", sun_int=1.1, sun_size=1.1, sun_disc=3.0,
        sun_glow=1.0, stars=0.0, clouds=0.0, hills=0.85, hill_color=_day("#4a5a98", 0.50), haze=0.25,
        haze_color=_day("#f6c880", 0.6), mist=0.05, mist_color=_day("#f8d8a0", 0.5), water=_day("#1a4a8c", 0.42),
        mirror=0.7, mirror_min=0.35, exposure=0.92, ripple=0.2, rays=0.8, dust=0.5, dust_color="#fff8ec",
        dust_color2="#ffd27a", bokeh=0.5),
    hush=dict(base="day", sky_top=_day("#2a6cc4", 0.86), sky_mid=_day("#8cc4ee", 0.84), sky_hor=_day("#fbecc8", 0.82),
        sun_az=180.0, sun_el=SUN_HIDDEN, sun_color="#fff0cc", sun_int=0.9, sun_size=1.1, sun_disc=3.0,
        sun_glow=0.8, stars=0.0, clouds=0.0, hills=0.85, hill_color=_day("#5468a4", 0.50), haze=0.25,
        haze_color=_day("#f4e2c0", 0.6), mist=0.05, mist_color=_day("#f8d8a0", 0.5), water=_day("#1f5296", 0.42),
        mirror=0.7, mirror_min=0.35, exposure=0.92, ripple=0.0, rays=0.4, dust=0.5, dust_color="#fff8ec",
        dust_color2="#ffd27a", bokeh=0.5),
    glory=dict(base="day", sky_top=_day("#1d62c0", 0.86), sky_mid=_day("#80c0ee", 0.84), sky_hor=_day("#fff0c0", 0.82),
        sun_az=180.0, sun_el=2.6, sun_color="#fff0cc", sun_int=1.15, sun_size=1.4, sun_disc=6.0,
        sun_glow=0.6, stars=0.0, clouds=0.0, hills=0.85, hill_color=_day("#4e62a0", 0.50), haze=0.25,
        haze_color=_day("#fbd890", 0.6), mist=0.05, mist_color=_day("#f8d8a0", 0.5), water=_day("#1d4e92", 0.42),
        mirror=0.7, mirror_min=0.35, exposure=0.92, ripple=0.15, rays=0.6, dust=0.5, dust_color="#fff8ec",
        dust_color2="#ffd27a", bokeh=0.5),
    pastel=dict(base="day", sky_top=_day("#3a86d6", 0.86), sky_mid=_day("#94c6ee", 0.84), sky_hor=_day("#ffe0b8", 0.82),
        sun_az=180.0, sun_el=9.0, sun_color="#fff0cc", sun_int=1.0, sun_size=1.1, sun_disc=3.0,
        sun_glow=0.9, stars=0.0, clouds=0.0, hills=0.85, hill_color=_day("#5c74b0", 0.50), haze=0.25,
        haze_color=_day("#f8e0c0", 0.6), mist=0.05, mist_color=_day("#f8d8a0", 0.5), water=_day("#2a62a6", 0.42),
        mirror=0.7, mirror_min=0.35, exposure=0.92, ripple=0.05, rays=0.5, dust=0.5, dust_color="#fff8ec",
        dust_color2="#ffd27a", bokeh=0.5),
)

WORLD = dict(
    looks=LOOKS,
    look=[(0.0, "handoff"), (8.0, "dawn11", 7.0), (15.0, "sunrise11", 10.0), (30.0, "radiant", 12.0),
          (BREATH[0], "hush", 4.0), (MOTHER_T[0] + 2.0, "radiant", 6.0), (GATE_OPEN - 1.0, "glory", 5.0),
          (252.0, "pastel", 9.0)],
    sun_el=_sun_el,
    ripple=Track([(0.0, 0.05), (20.0, 0.15), (60.0, 0.25), (100.0, 0.18), (117.0, 0.0), (125.0, 0.05),
                  (160.0, 0.15), (250.0, 0.1), (262.0, 0.03), (TOTAL, 0.03)]),
    arch=ARCH_CFG,
    react=dict(beat=0.10, level=0.10),
)

P3D = dict(
    camera=CAMERA,
    world=WORDS.world(WORLD),
    setup=_setup,
    bursts=[dict(t=GATE_OPEN, strength=0.10, rise=0.8, fall=2.4, color="#ffe2a0", at=(0.0, 14.0, CITY_Z))],
    motion_blur=0.0,
)

TITLE = dict(_base.TITLE, form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(_base.TAGLINE, t0=1e9, t1=1e9 + 1)
# the signature: warm white on the night of the opening, navy on the bright sky from the sunrise on (a slow
# 3 s crossfade, never a flash); the end card: the official campaign card (tools/nine_colours_minor/cards.py
# style, titles.py N6) with the closing tagline, over the bright pastel morning
TITLES = dict(
    opening=dict(t_end=8.9, dissolve=.5, build=0, y=.33),
    signature=dict(windows=[(SIG_T0, 20.0, "tl", "night"), (17.0, TOTAL + 10.0, "tl", "day")], fade=3.0),
    end_card=dict(t_in=END_CARD, fade=.7, scale=.86, veil=.9, backdrop=False, y=.50),
)
