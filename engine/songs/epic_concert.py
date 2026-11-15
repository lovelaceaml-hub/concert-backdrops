"""The Words of Mother's Love Healing Concert: the epic promo (60 seconds, a trailer for the whole concert).

One continuous rise of light over one lake: night, dawn, morning, day. The arch of nine lights is the thread:
all dark at the start, complete at the peak. One hero image per movement; everything else stays quiet.
No plates, no lyrics, no faces, everyone clothed, Heavenly Mother only from behind, nothing dark behind any
text (TEXT_SHADOW = 0), calm lower third.

Audio: audio/promo/concert-medley.mp3 (four sections; S1, S2, S3 below are its section starts).

What happens (seconds; the hero of each movement is marked HERO):
 0 to S1   NIGHT. The camera cranes up from the dark water to a wide starry lake. A lone person of light
           walks on the water, a ripple under each step. The opening line forms as stars joining into
           letters. HERO: one star falls and lands on the lake; its ripple spreads and, on the first beat of
           the next section, the middle light of the arch wakes.
 S1 to S2  DAWN. First light grows where the star fell. HERO: Heavenly Mother, only from behind, her veil
           flowing, opens her arms; the Greeting blooms letter by letter over her gesture; as the sun breaks
           the horizon, doves of light rise from her hands into the sunbeams. The walker reaches her and
           bows. Words, walker, Mother's light and the doves all rise to the Greeting light, which lights on S2.
 S2 to S3  THE MESSAGE SPREADS. People of light walk in along the far shore from both sides. HERO: a flame
           comes down from the middle light of the arch and is passed from hand to hand until everyone
           glows. The Encouragement is written in light above them. The lights of the arch wake one by one;
           the Encouragement light is the last, and the arch is complete.
 S3 to end DAY. HERO: everyone lifts their light; the lights rise to the arch, the arch blazes, and the
           sky opens into the bright campaign day (sky blue, cream and peach, bubbles, a few green leaves,
           butterflies). The hearts and globe emblem draws itself in light, is mirrored in the lake, and
           rises into the arch. The end card arrives on a ribbon of light (coral title, navy lines).

Text animations: constellation (opening line), bloom (Greeting), ink (Encouragement), ribbon (title),
rise (end card lines).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))
AUDIO_FILE = "audio/promo/concert-medley.mp3"

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.6
SONG_END = 60.0
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.34         # the water line

RIDGE_X0, RIDGE_W = -0.04, 1.08   # the skyline runs past both edges, so the camera never shows its end

# The medley's section starts (seconds). Every time below hangs off these three.
S1, S2, S3 = 13.0, 28.0, 44.0


def lin(hexs):
    h = hexs.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    return c ** 2.2


def _db(x):
    return 20.0 * np.log10(np.maximum(x, 1e-7))


def _ar(x, attack, release):
    """One-pole follower with separate attack and release times (seconds)."""
    a = np.exp(-1.0 / (FPS * max(attack, 1e-4)))
    r = np.exp(-1.0 / (FPS * max(release, 1e-4)))
    y = np.zeros_like(x)
    v = 0.0
    for i, s in enumerate(x):
        k = a if s > v else r
        v = k * v + (1.0 - k) * s
        y[i] = v
    return y


def _gauss(x, sigma_frames):
    n = int(sigma_frames * 4) + 1
    k = np.exp(-0.5 * (np.arange(-n, n + 1) / sigma_frames) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(x, n, mode="edge"), k, mode="valid")


class Song:
    def __init__(self):
        d = np.load(FEATURES)
        t = d["times"]
        ft = np.arange(NFRAMES) / FPS
        self.ft = ft
        n = np.clip((_db(d["rms"]) + 36.0) / 23.0, 0.0, 1.0)
        n_f = np.interp(ft, t, n, right=0.0)
        self.env = _ar(n_f, 0.07, 0.45)
        self.env_slow = _gauss(n_f, 1.4 * FPS)
        hi = _db(d["high"])
        lo_, hi_ = np.percentile(hi[t < MUSIC_END], [10, 98])
        self.hi = _ar(np.interp(ft, t, np.clip((hi - lo_) / max(hi_ - lo_, 1e-6), 0, 1), right=0.0), 0.04, 0.35)
        on = np.clip(d["onset"] / np.percentile(d["onset"], 99), 0.0, 1.4)
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain skyline is the loudness of the medley, kept low and long so the sky stays open
        xs = np.linspace(0.0, 1.0, 2048)
        st = (xs - RIDGE_X0) / RIDGE_W * MUSIC_END
        base_t = _gauss(n_f, 2.3 * FPS)
        mid_t = _gauss(n_f, 1.0 * FPS)
        base = np.interp(st, ft, base_t)
        mid = np.interp(st, ft, mid_t) - base
        v = np.clip((base - 0.30) / 0.56, 0.0, 1.0) ** 1.6

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 20 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 16), (0.25, 35), (0.125, 78), (0.0625, 170), (0.03, 380))))
        hgt = 0.018 + 0.085 * v + 0.045 * mid * (0.35 + v) + (0.012 + 0.024 * v) * (crag - 0.5)
        self.ridge = np.maximum(hgt, 0.006).astype("f4")
        # water rings: one per clear note onset, placed by a hash of its index
        ons = d["onsets"]
        strength = np.interp(ons, t, on)
        keep, last = [], -9.0
        for k, (ot, s) in enumerate(zip(ons, strength)):
            if s > 0.40 and ot - last > 0.45 and ot < MUSIC_END:
                r = np.random.default_rng(1000 + k).random(2)
                keep.append((float(ot), 0.06 + 0.88 * r[0], HORIZON * (0.12 + 0.70 * r[1] ** 1.3), float(min(s, 1.2))))
                last = ot
        self.rings = keep
        self.ring_t = np.array([k[0] for k in keep]) if keep else np.zeros(0)

    def lantern(self, t):
        x = RIDGE_X0 + RIDGE_W * min(max(t / MUSIC_END, 0.0), 1.0)
        y = HORIZON + float(np.interp(x, np.linspace(0, 1, 2048), self.ridge))
        return x, y

    def rings_at(self, t, n=16, life=4.5):
        if not len(self.ring_t):
            return []
        i1 = int(np.searchsorted(self.ring_t, t, side="right"))
        out = []
        for k in range(i1 - 1, -1, -1):
            age = t - self.rings[k][0]
            if age > life or len(out) >= n:
                break
            out.append((self.rings[k][1], self.rings[k][2], age, self.rings[k][3]))
        return out


# ----------------------------------------------------------------- timeline

from track import Track   # noqa: E402
import theme   # noqa: E402

BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0      # nothing dark behind any text

# ---- key moments (all relative to the medley's sections)
STAR_FALL = S1 - 1.0          # the falling star touches the lake; its ripple runs into the section start
ARMS_OPEN = S1 + 2.4          # Heavenly Mother begins to open her arms
G_FORM = S1 + 2.6             # Greeting: blooms over her gesture
G_HOLD = G_FORM + 10.0        # fully formed G_FORM + 3.75 to G_HOLD: 6.25 s
G_STAR = S2                   # its light wakes on the first beat of the third section
DOVES_UP = G_FORM + 3.6       # the doves rise as the last letter opens and the sun breaks the horizon
CROWD_IN = S2 - 2.6           # the first people step in at the far edges as Mother's light rises
FLAME = S2 + 3.4              # the flame leaves the arch (the crowd's own plan may shift this a little)
E_FORM = S2 + 3.5             # Encouragement: written in light, its middle after the flame has passed
E_HOLD = E_FORM + 9.8         # fully formed E_FORM + 3.75 to E_HOLD: 6.05 s
E_STAR = S3 - 1.0             # the last light: the arch is complete one second before the peak
LIFT = S3                     # everyone lifts their light
NINTH = S3 + 2.4              # the arch blazes as the risen lights reach it
EMBLEM = S3 + 1.8             # the emblem's pen of light starts
EMBLEM_DONE = EMBLEM + 3.0
EMBLEM_OUT = EMBLEM_DONE + 0.5
TITLE_HIT = S3 + 8.3          # the title is whole; the end card lines rise right after
FORM_DUR = 3.0

# ---- the sky: one continuous rise of light (top, middle, horizon, colour of the light)
PAL = {
    "night":   ("#03061c", "#0a1440", "#262f6a", "#8ea4ff"),
    "first":   ("#070c2e", "#2c2460", "#a25a74", "#ffb090"),
    "dawn":    ("#0c1642", "#4a3676", "#d9706a", "#ffc88c"),
    "sunrise": ("#102256", "#5d4486", "#e88868", "#ffd9a0"),
    "morning": ("#143070", "#6c5aa0", "#f09a72", "#ffe2b4"),
}
DAY = ("#4aa3e6", "#a9d4f4", "#ffe3c4", "#fff4e0")   # the campaign day, as seen on screen
_DAY_SCALE = (0.92, 0.86, 0.78, 0.42)                 # theme.sky_tracks: the sun glow is added on top
_pal_keys = [(0.0, "night"), (S1 - 1.0, "night"), (S1 + 3.5, "first"), (S1 + 7.5, "dawn"), (S2 - 1.0, "sunrise"),
             (S2 + 8.0, "morning"), (S3 + 0.5, "morning"), (S3 + 7.0, "day"), (TOTAL, "day")]


def _sky(k):
    def col(p):
        return theme.display(DAY[k]) * _DAY_SCALE[k] if p == "day" else lin(PAL[p][k])
    return Track([(t, col(p)) for t, p in _pal_keys])


SKY_TOP, SKY_MID, SKY_HOR, GLOW = (_sky(k) for k in range(4))
SKY_THEME = Track([(0, 0.0), (S3 - 0.5, 0.0), (S3 + 8.5, 1.0), (TOTAL, 1.0)])   # the hills turn to pale haze
# the sun: under the horizon at night, breaking it as the doves rise, then climbing all the way into the
# middle of the sky, where it becomes the soft white heart of the end card (the poster's circle of light)
# Draft 2 put the climbing, widening sun right behind the emblem while it was drawn (S3 + 1.8 to S3 + 5.3): the
# centre of the frame was the brightest thing in it and no emblem showed. Draft 3: the same sun up to S3, then
# low and modest until the emblem has left, rising and widening only after.
SUN_Y = Track([(0, 0.290), (S1, 0.300), (S1 + 4.5, 0.332), (S1 + 8.0, 0.362), (S2, 0.395), (S3, 0.450),
               (S3 + 5.5, 0.470), (S3 + 10.0, 0.600), (TOTAL, 0.630)])
SUN_INT = Track([(0, 0.08), (S1 - 1.0, 0.10), (S1 + 3.5, 0.30), (S1 + 8.0, 0.62), (S2, 0.60), (S3, 0.62),
                 (S3 + 5.5, 0.62), (S3 + 9.0, 0.55), (TOTAL, 0.52)])
SUN_SIZE = Track([(0, 0.09), (S1 + 8.0, 0.115), (S3, 0.13), (S3 + 5.5, 0.135), (S3 + 10.0, 0.22), (TOTAL, 0.24)])
STARS = Track([(0, 0.0), (0.6, 0.0), (3.0, 0.95), (S1 - 1.0, 0.92), (S1 + 4.0, 0.55), (S1 + 9.0, 0.20),
               (S2 + 2.0, 0.07), (S3, 0.04), (S3 + 4.0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (1.0, 0.0), (4.0, 0.60), (S1 - 1.0, 0.55), (S1 + 4.0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (2.0, 0.0), (5.0, 0.10), (S1 - 2.0, 0.09), (S1 + 3.0, 0.0), (TOTAL, 0.0)])   # faint
CLOUDS = Track([(0, 0.06), (S1, 0.10), (S1 + 6.0, 0.30), (S2, 0.26), (S3, 0.22), (TOTAL, 0.14)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.0), (2.0, 0.08), (S1, 0.10), (S2, 0.12), (S3, 0.14), (S3 + 6.0, 0.18), (TOTAL, 0.18)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.8, 1.0), (TOTAL - 0.65, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (S1 + 4.0, 0.0), (S1 + 8.0, 0.18), (S2, 0.14), (S3, 0.12), (S3 + 3.0, 0.20), (TOTAL, 0.08)])
# Draft 3 test: is the pale column up the middle of the morning this lane term, or the sun's own glow? PART is
# close to draft 2 until S2 + 6 (within 3 percent at 0:31, the control), 0 from S2 + 7 to S3 - 1.5, and exactly
# draft 2's again from S3 on, so the day differs from draft 2 in the sun alone. Compare 0:39 and 0:41 here with
# the same times of draft 2 (same sun, PART about 0.46 there). Not yet known which it is.
PART = Track([(0, 0.0), (S1 + 3.0, 0.0), (S1 + 8.0, 0.55), (S2 + 6.0, 0.488), (S2 + 7.0, 0.0), (S3 - 1.5, 0.0),
              (S3, 0.45), (TOTAL, 0.30)])
SKYLINE_LANTERN = 0.0      # no travelling light on the skyline: the falling star is the one star of this film


def MOTE_COLORS(t):
    return ("#ffe2a8", "#ffb48c") if t < S3 + 2.0 else (theme.WHITE_GLOW, theme.GOLD)


# ---- sky and camera (UPGRADE-HOWTO I7): soft moving clouds, sunbeams, one slow camera gesture
CLOUDS3D = Track([(0, 0.14), (S1 - 1.0, 0.20), (S1 + 6.0, 0.30), (S2, 0.28), (S3, 0.25), (S3 + 7.0, 0.15),
                  (TOTAL, 0.15)])
CLOUDS_SPEED = 1.3
CLOUDS_LIGHT = 0.8
# short, gentle shafts round the sun. Draft 1 (rays 0.9, decay 0.988, clouds 0.46) washed the sky to cream and
# the white words lost their contrast (QA legibility 1.1; no dark halo was measured, ring/sky stayed above 1).
# Rays, clouds and sun were lowered together, so which of them washed the sky is not isolated.
GOD_RAYS = Track([(0, 0.0), (S1 + 3.5, 0.0), (S1 + 8.0, 0.40), (S2, 0.24), (S3 - 2.0, 0.18), (S3 + 2.5, 0.45),
                  (S3 + 7.5, 0.10), (TOTAL, 0.08)])
RAYS_DECAY = 0.968
# crane up from the water (0 to 9 s), a slow push in (dawn and morning), then opening wide into the day
CAMERA_CRANE = Track([(0, -0.26), (1.5, -0.25), (9.5, 0.0), (S3, 0.0), (S3 + 8.0, 0.035), (TOTAL, 0.04)])
CAMERA_ZOOM = Track([(0, 1.0), (S1, 1.0), (S3 - 0.5, 1.09), (S3 + 8.5, 1.0), (TOTAL, 1.0)])
PARALLAX = 1.0
CAMERA_MOTES = Track([(0, 0.0), (3.0, 0.35), (S3, 0.35), (S3 + 5.0, 0.15), (TOTAL, 0.15)])

# ---- music-reactive light, all gentle (UPGRADE-HOWTO I1, engine-audio)
AUDIO_REACT = 1.0
REACT_GLOW = 0.35
REACT_SPARKLE = 0.30
REACT_ARCH = 0.6
REACT_AURORA = 0.5
REACT_CHORUS = 0.25

# ---- the lake responds (UPGRADE-HOWTO I8)
STAR_X, STAR_LAND_Y = 0.5, 0.305
FALLING_STARS = [(STAR_FALL, STAR_X, STAR_LAND_Y)]
RIPPLES = [(STAR_FALL + 0.02, STAR_X, 1.3, STAR_LAND_Y), (STAR_FALL + 0.40, STAR_X, 0.9, STAR_LAND_Y),
           (STAR_FALL + 0.85, STAR_X, 0.6, STAR_LAND_Y), (STAR_FALL + 1.40, STAR_X, 0.4, STAR_LAND_Y)]
# where the star touched the water a thin column of light stands for a moment and reaches the middle light of
# the arch, which wakes on the section start (UPGRADE-HOWTO C)
BEAM = Track([(0, 0.0), (STAR_FALL, 0.0), (STAR_FALL + 0.9, 0.34), (S1 + 0.5, 0.30), (S1 + 2.8, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (STAR_X, 0.895)
BEAM_TO = (STAR_X, STAR_LAND_Y + 0.01)
BEAM_WIDTH = (0.004, 0.012)
BEAM_COLOR = "#ffe9c4"
RIPPLES_AUTO = Track([(0, 1.0), (S2, 1.0), (S2 + 3.0, 0.5), (TOTAL, 0.5)])   # steps on the water, the star
RIPPLE_COLOR = "#ffe6c4"

# ---- creatures of light (UPGRADE-HOWTO I1, engine-creatures)
M_X, M_Y, M_H = 0.82, 0.300, 0.39          # Heavenly Mother: where she stands (on the water, nearer to us)
FIREFLIES = Track([(0, 0.0), (1.5, 0.0), (5.0, 0.55), (S1 - 1.0, 0.55), (S1 + 3.5, 0.0), (TOTAL, 0.0)])
FIREFLIES_Y = (0.30, 0.46)
FIREFLIES_BRIGHT = 1.0
DOVES = Track([(0, 0.0), (DOVES_UP - 0.1, 0.0), (DOVES_UP + 0.5, 1.0), (S2 + 1.6, 1.0), (S2 + 4.2, 0.0),
               (TOTAL, 0.0)])
DOVES_COUNT = 12
DOVES_FROM = (M_X - 0.085, M_Y + 0.80 * M_H)   # they rise from her open hand on the side of the sun
DOVES_PATH = [(DOVES_UP, (0.66, 0.60)), (DOVES_UP + 2.4, (0.50, 0.565)), (DOVES_UP + 5.0, (0.30, 0.60)),
              (S2 - 1.4, (0.17, 0.72)), (S2, (0.12, 0.81)), (S2 + 4.5, (0.10, 0.86))]
DOVES_ORBIT = 0.08
DOVES_SIZE = 0.034
DOVES_SPEED = 1.0
DOVES_COLOR = "#fff1da"
DOVES_TRAIL = 0.7
BUTTERFLIES = Track([(0, 0.0), (S3 + 4.0, 0.0), (S3 + 7.5, 1.0), (TOTAL, 1.0)])
BUTTERFLIES_COUNT = 3
BUTTERFLIES_COLOR = ("#ffb0c8", "#ffd9a0")
BUTTERFLIES_SIZE = 0.024
BUTTERFLIES_AREA = (0.06, 0.94, 0.38, 0.56)

# ---- the campaign day (UPGRADE-HOWTO I, engine-theme)
BUBBLES = Track([(0, 0.0), (S3 + 2.5, 0.0), (S3 + 8.0, 0.30), (TOTAL, 0.30)])
BUBBLES_SPEED = 0.9
LEAVES = Track([(0, 0.0), (S3 + 4.0, 0.0), (S3 + 9.0, 0.22), (TOTAL, 0.22)])
LEAVES_COLORS = ("#3fb83a", "#9ccc40")   # truly green, like the poster

# ---- people of light (UPGRADE-HOWTO H): the lone walker, then Heavenly Mother from behind
W_Y, W_H = 0.322, 0.29     # the walker walks on the water, a ripple under each step
W_STOP1, W_STOP2 = 0.40, M_X - 0.195   # where she stops when the star falls; where she stops before Mother
_LEGS = [(3.6, 11.0, 0.02, W_STOP1), (S1 + 0.2, S1 + 4.6, W_STOP1, W_STOP2)]


def walker_x(t):
    """A steady walk on each leg: the pace eases in and out over 1.2 s at its ends only."""
    x = _LEGS[0][2]
    for ta, tb, xa, xb in _LEGS:
        if t <= ta:
            break
        r = 1.2
        v = 1.0 / (tb - ta - r)                      # speed of the steady part (distance 1 over the leg)
        u = min(t, tb) - ta
        if u < r:
            d = 0.5 * v * u * u / r
        elif u > tb - ta - r:
            w = tb - ta - u
            d = 1.0 - 0.5 * v * w * w / r
        else:
            d = 0.5 * v * r + v * (u - r)
        x = xa + (xb - xa) * d
    return x


FIGURES = [
    # the lone walker: crosses the night, looks up when the star falls, walks on toward the first light,
    # reaches Mother, bows, and rises with the words into the Greeting light
    dict(kind="rig", preset="person", t0=1.8, t1=G_HOLD - 0.4, gather=2.2, dissolve=2.6, facing="right",
         x=walker_x, y=W_Y, height=W_H,
         actions=[(1.8, "stand"), (STAR_FALL - 0.9, {"tilt": 0.32, "blend": 0.8}), (S1 + 0.2, {"tilt": 0.0}),
                  (DOVES_UP + 0.2, "bow", {"blend": 1.5}), (DOVES_UP + 2.8, "pray", {"blend": 1.6}),
                  (G_HOLD - 1.8, "rise", {"blend": 1.4})],
         color="#ffcf9a", glow=0.85, to_star=0),
    # Heavenly Mother, only from behind; her veil flows; her arms open, then lift in blessing
    dict(kind="rig", preset="person_back", t0=S1 - 0.2, t1=G_HOLD - 0.2, gather=2.2, dissolve=2.8,
         x=M_X, y=M_Y, height=M_H,
         actions=[(S1 - 0.2, "stand"), (ARMS_OPEN, "open", {"blend": 2.4}), (DOVES_UP - 0.4, "bless", {"blend": 4.6})],
         color="#ffe0c0", glow=1.1, to_star=0),
]

# ---- the gathering and the passed light (UPGRADE-HOWTO I-G)
GATHERING = dict(t0=CROWD_IN, t1=S3 + 2.2, dissolve=2.6, count=34, center=(0.5, 0.343), spread=(0.36, 0.030),
                 rows=2, hole=0.06, height=(0.17, 0.10), speed=1.15, arrive_by=S2 + 8.5, sides=("left", "right"),
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=FLAME, speed=0.17, hold=0.22, path="crowd", start="center", source="arch", descent=2.2,
                  color="#ffe2a0", lift=LIFT, rise=True, arch=1.0,
                  lift_spread=0.5, rise_delay=0.6, rise_spread=1.0, rise_dur=2.3)

# ---- the campaign emblem, drawn in light and mirrored in the lake (UPGRADE-HOWTO I8)
SYMBOLS = [
    dict(kind="emblem", t0=EMBLEM, t1=EMBLEM_DONE, out=EMBLEM_OUT, x=0.5, y=0.555, size=0.29,
         leave="to_star", star=4, leave_dur=2.4, reflect=True, glow=1.0),
]

# ---- the arch of nine lights: dark at the start, complete at the peak
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=150, y=0.258,
         form=G_FORM, hold=G_HOLD, star=G_STAR, anim="bloom", glow="#ffd9a0"),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         star=S2 + 12.2, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         star=S2 + 9.2, **OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, star=S2 + 6.6, **OFF),
    # the middle light: woken by the falling star, the flame comes down from it, the emblem rises into it
    dict(label="Concession", lines=["“Please, after you.”"], size=164, star=S1,
         arrive=[EMBLEM_OUT + 2.4], **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         star=S2 + 7.4, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=100,
         y=0.275, form=E_FORM, hold=E_HOLD, star=E_STAR, anim="ink", glow="#ffd9a0"),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         star=S2 + 10.8, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         star=S2 + 13.6, **OFF),
]
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW,
             anim="ribbon")
# the opening line: written for this film (not a lyric)
FRAGMENTS = [
    dict(text="Peace begins with a word", t0=3.0, t1=6.4, out=9.8, dy=0.10, size=88, glow="#ffd9a0",
         anim="constellation"),
]
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.3, t1=TITLE_HIT + 2.3, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
# no corner credit in this film (the title is the end card); t_in never comes
CREDIT = dict(song="The Words of Mother’s Love", concert="Healing Concert",
              t_in=1e9, t_full=1e9 + 1.0, t_move=1e9 + 2.0, t_rest=1e9 + 3.0, scale=0.34, alpha_rest=0.0,
              margin_x=0.030, margin_top=0.048)


def credit_state(t, bbox):
    """Centre, scale and strength of the title block; bbox is its size at full card size."""
    c = CREDIT
    x0, x1, y0, y1 = bbox

    def ss(a, b, x):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    a_in = ss(c["t_in"], c["t_full"], t)
    m = ss(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m)
    return (cx, cy, scale, alpha), (cx0, cy0)


# soft waves of light when a light of the arch wakes on a section start
WAVES = [(S1, STAR_POS[4][0], STAR_POS[4][1], 0.55), (G_STAR, STAR_POS[0][0], STAR_POS[0][1], 0.55),
         (TITLE_HIT, 0.5, 0.62, 0.6)]


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    lx, ly = song.lantern(t)
    z = ZOOM(t)
    lsx, lsy = (lx - 0.5) / z + 0.5, (ly - HORIZON) / z + HORIZON
    waves = [(t - w[0], w[1], w[2], w[3]) for w in WAVES if 0.0 <= t - w[0] < 6.0]
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t) * (0.92 + 0.20 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=lx, rings=song.rings_at(t), waves=waves,
        star=star_state(t), link=link_state(t),   # noqa: F821  (installed by engine/song.py from arch.py)
    )
