"""The Words of Mother's Love Healing Concert: the epic promo (60 seconds, a trailer for the whole concert).

One continuous rise of light over one lake: night, dawn, morning, day. The arch of nine lights is the thread:
all dark at the start, complete at the peak. One hero image per movement; everything else stays quiet.
No plates, no lyrics, no faces, everyone clothed, Heavenly Mother only from behind, nothing dark behind any
text (TEXT_SHADOW = 0), calm lower third.

Audio: audio/promo/concert-medley.mp3 (four sections from songs 03, 09, 08 and 01; S1, S2, S3 below are its
section starts and BEATS its downbeats, as measured by the helper who cut it).

What happens (seconds; the hero of each movement is marked HERO):
 0 to 13.2    NIGHT. The camera cranes up from the dark water to a wide starry lake. A lone person of light
              walks on the water, a ripple under each step. The opening line forms as stars joining into
              letters. HERO (10.24): one star falls and lands on the lake at her feet; its ripple spreads, a
              thin column of light stands where it fell, and the middle light of the arch wakes.
 13.2 to 28.4 DAWN. HERO (13.21): the sun breaks the horizon and Heavenly Mother, only from behind, her veil
              flowing, opens her arms. The Greeting blooms letter by letter over her gesture; doves of light
              rise from her hand into the sunbeams (16.28). The walker reaches her and bows. Words, walker,
              Mother's light and the doves all rise to the Greeting light (25.45). The first people of light
              are already walking in along the far shore.
 28.4 to 43   THE MESSAGE SPREADS. HERO (28.35): a flame leaves the middle light of the arch, comes down, and
              from 31.23 is passed from hand to hand until everyone glows. The Encouragement is written in
              light above them. The lights of the arch wake one by one; the Encouragement light is the last
              (42.0), and the arch is complete.
 43 to 60     DAY. HERO (43.00): everyone lifts their light and the day begins to open from the horizon. The
              lights rise to the arch and the arch blazes; the hearts and globe emblem draws itself in light
              (45.81 to 48.71), is mirrored in the lake, and rises into the arch (51.55) while the sky opens
              into the bright campaign day (sky blue, cream and peach, bubbles, a few green leaves,
              butterflies). The end card arrives on a ribbon of light (coral title, navy lines), is whole
              before 54.4, where the arch reaches its peak, and holds through the music's decay.

Why the sky stays deep until about 47.8: people, flames and the emblem are light, and light reads weakly on a
bright sky (engine HOWTO, section S; in drafts 2 and 3 the rising lights nearly vanished on the pale sky of
46 to 49 s). So the day opens from the horizon at 43 and sweeps the whole sky only as the emblem rises into
the arch.

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

# The medley (measured by the helper who cut it): section starts and downbeats, in seconds. Crossfades run
# 12.21 to 14.21, 27.35 to 29.35 and 42.00 to 44.00; the loudest moment is about 54.4; the sound decays from
# 58.36. Every time below hangs off these.
S1, S2, S3 = 13.21, 28.35, 43.00
BEATS = [1.88, 4.67, 7.47, 10.24, 13.21, 16.28, 19.25, 22.38, 25.45, 28.35, 31.23, 34.22, 37.03, 39.96, 43.00,
         45.81, 48.71, 51.55, 54.43, 57.56]


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

# ---- key moments, on the medley's downbeats (BEATS) and section starts
STAR_FALL = BEATS[3]          # 10.24: the falling star touches the lake
ARCH_FIRST = STAR_FALL + 1.05   # the middle light of the arch wakes as the star's ripple spreads
ARMS_OPEN = S1                # 13.21: sunrise; Heavenly Mother begins to open her arms
G_FORM = S1 + 0.2             # Greeting: blooms over her gesture
G_HOLD = G_FORM + 10.04       # fully formed G_FORM + 3.75 to G_HOLD: 6.29 s
G_STAR = BEATS[8]             # 25.45: its light wakes
DOVES_UP = BEATS[5]           # 16.28: the doves rise from her hand into the sunbeams
CROWD_IN = S2 - 5.75          # the first people step in at the far edges, so one is in place when the flame comes
FLAME = S2                    # 28.35: the flame leaves the middle light of the arch
FLAME_DOWN = BEATS[10] - S2   # ... and is in the first hands on the next downbeat (31.23)
E_FORM = S2 + 0.65            # Encouragement: written in light; its middle is written after the flame has passed
E_HOLD = BEATS[13]            # 39.96: fully formed E_FORM + 3.75 to E_HOLD: 7.2 s
E_STAR = S3 - 1.0             # 42.0: the last light, the arch is complete one second before the peak
LIFT = S3                     # 43.00: everyone lifts their light
NINTH = BEATS[15]             # 45.81: the arch blazes as the risen lights reach it
EMBLEM = BEATS[15]            # 45.81: the emblem's pen of light starts
EMBLEM_DONE = BEATS[16]       # 48.71: the emblem is whole
EMBLEM_OUT = EMBLEM_DONE + 0.44
EMBLEM_FLY = BEATS[17] - EMBLEM_OUT   # ... and reaches the middle light of the arch at 51.55
DAY_OPENS = S3 + 4.8          # the whole sky begins to open (the horizon has been warming since the lift)
DAY_FULL = S3 + 10.0          # the campaign day
T_FORM = EMBLEM_OUT + 0.05    # the title's ribbon starts as the emblem lifts away; whole T_FORM + 3.75 = 52.95
TAG_T0, TAG_T1 = T_FORM + 3.2, T_FORM + 5.1   # the end card lines: whole by about 54.0
TITLE_HIT = BEATS[18]         # 54.43, the loudest moment: the peak of the fully lit arch (engine/arch.py)
FORM_DUR = 3.0

# ---- the sky: one continuous rise of light (top, middle, horizon, colour of the light). The upper sky stays
# deep until the day opens: white words and people of light need a deep sky behind them (QA on drafts 1 to 3:
# the words lost contrast once the sky at their height passed about 0.1 in linear light).
PAL = {
    "night":   ("#03061c", "#0a1440", "#262f6a", "#8ea4ff"),
    "first":   ("#060a2a", "#231d54", "#8f4f6e", "#ffb090"),
    "dawn":    ("#0a1238", "#33276a", "#c8646a", "#ffc88c"),
    "sunrise": ("#0c1a48", "#3d2f78", "#d87466", "#ffd49c"),
    "morning": ("#0e2052", "#443782", "#de8068", "#ffdcaa"),
    "opening": ("#112660", "#4b3e8c", "#f6a070", "#ffe6b8"),   # after the lift: the horizon turns to gold
}
DAY = ("#4aa3e6", "#a9d4f4", "#ffe3c4", "#fff4e0")   # the campaign day, as seen on screen
_DAY_SCALE = (0.92, 0.86, 0.78, 0.42)                 # theme.sky_tracks: the sun glow is added on top
_pal_keys = [(0.0, "night"), (STAR_FALL, "night"), (S1, "first"), (S1 + 4.0, "dawn"), (S2 - 2.0, "sunrise"),
             (S2 + 6.0, "morning"), (S3, "morning"), (DAY_OPENS, "opening"), (DAY_FULL, "day"), (TOTAL, "day")]


def _sky(k):
    def col(p):
        return theme.display(DAY[k]) * _DAY_SCALE[k] if p == "day" else lin(PAL[p][k])
    return Track([(t, col(p)) for t, p in _pal_keys])


SKY_TOP, SKY_MID, SKY_HOR, GLOW = (_sky(k) for k in range(4))
SKY_THEME = Track([(0, 0.0), (DAY_OPENS - 0.8, 0.0), (DAY_FULL + 1.0, 1.0), (TOTAL, 1.0)])   # hills turn to pale haze
# the sun: under the horizon at night, breaking it on S1, low and modest while people and the emblem are on
# screen, then climbing into the middle of the sky, where it becomes the soft white heart of the end card
SUN_Y = Track([(0, 0.290), (STAR_FALL, 0.300), (S1, 0.334), (S1 + 3.0, 0.352), (S2, 0.385), (S3, 0.410),
               (DAY_OPENS, 0.440), (TITLE_HIT, 0.600), (TOTAL, 0.620)])
SUN_INT = Track([(0, 0.08), (STAR_FALL, 0.10), (S1, 0.30), (S1 + 3.0, 0.48), (S2, 0.46), (S3, 0.50),
                 (S3 + 2.8, 0.66), (DAY_OPENS + 1.2, 0.60), (TITLE_HIT, 0.55), (TOTAL, 0.52)])
SUN_SIZE = Track([(0, 0.09), (S1 + 3.0, 0.11), (S3, 0.12), (DAY_OPENS, 0.13), (TITLE_HIT, 0.22), (TOTAL, 0.24)])
STARS = Track([(0, 0.0), (0.6, 0.0), (3.0, 0.95), (STAR_FALL, 0.92), (S1 + 3.0, 0.55), (S1 + 8.0, 0.25),
               (S2 + 2.0, 0.10), (S3, 0.06), (DAY_OPENS + 1.2, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (1.0, 0.0), (4.0, 0.60), (STAR_FALL, 0.55), (S1 + 3.0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (2.0, 0.0), (5.0, 0.10), (STAR_FALL - 1.0, 0.09), (S1 + 1.0, 0.0), (TOTAL, 0.0)])   # faint
CLOUDS = Track([(0, 0.06), (S1, 0.10), (S1 + 6.0, 0.22), (S2, 0.20), (S3, 0.18), (TOTAL, 0.12)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.0), (2.0, 0.08), (S1, 0.10), (S2, 0.12), (S3, 0.14), (DAY_FULL, 0.18), (TOTAL, 0.18)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.8, 1.0), (TOTAL - 0.6, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (S1, 0.0), (S1 + 3.0, 0.16), (S2, 0.12), (S3, 0.12), (S3 + 2.8, 0.20), (TOTAL, 0.08)])
# the lane of light at the sun: off. Draft 3 tested it (0 against 0.47, same sun): no change in the picture
# (centre to side brightness 1.137 and 1.134 at 0:39) or in the light round the words.
PART = Track([(0, 0.0), (TOTAL, 0.0)])
SKYLINE_LANTERN = 0.0      # no travelling light on the skyline: the falling star is the one star of this film


def MOTE_COLORS(t):
    return ("#ffe2a8", "#ffb48c") if t < DAY_OPENS + 2.0 else (theme.WHITE_GLOW, theme.GOLD)


# ---- sky and camera (UPGRADE-HOWTO O): a few soft moving clouds, short sunbeams, one slow camera gesture
CLOUDS3D = Track([(0, 0.14), (STAR_FALL, 0.18), (S1 + 3.0, 0.20), (S2, 0.18), (S3, 0.18), (DAY_FULL, 0.14),
                  (TOTAL, 0.14)])
CLOUDS_SPEED = 1.3
CLOUDS_LIGHT = 0.8
# short, gentle shafts round the sun. Draft 1 (rays 0.9, decay 0.988, clouds 0.46) washed the sky to cream and
# the white words lost their contrast (QA legibility 1.1; no dark halo was measured, ring/sky stayed above 1).
# Rays, clouds and sun were lowered together, so which of them washed the sky is not isolated.
GOD_RAYS = Track([(0, 0.0), (S1, 0.0), (DOVES_UP, 0.30), (S2, 0.18), (S3 - 1.0, 0.15), (S3 + 2.8, 0.36),
                  (DAY_OPENS + 1.2, 0.22), (DAY_FULL, 0.08), (TOTAL, 0.08)])
RAYS_DECAY = 0.968
# crane up from the water (0 to 9 s; level before the star falls, because its column of light is not moved by
# the camera), a slow push in through dawn and morning, then opening wide into the day. The engine moves the
# people, the crowd, the creatures and the emblem with the scenery and still lands every flight on the arch.
CAMERA_CRANE = Track([(0, -0.26), (1.5, -0.25), (9.0, 0.0), (TOTAL, 0.0)])
CAMERA_ZOOM = Track([(0, 1.0), (S1, 1.0), (S3 - 0.5, 1.07), (S3 + 9.5, 1.0), (TOTAL, 1.0)])
PARALLAX = 1.0
CAMERA_MOTES = Track([(0, 0.0), (3.0, 0.35), (S3, 0.35), (DAY_FULL, 0.15), (TOTAL, 0.15)])

# ---- music-reactive light, all gentle (UPGRADE-HOWTO P)
AUDIO_REACT = 1.0
REACT_GLOW = 0.35
REACT_SPARKLE = 0.30
REACT_ARCH = 0.6
REACT_AURORA = 0.5
REACT_CHORUS = 0.25

# ---- the lake responds (UPGRADE-HOWTO L)
STAR_X, STAR_LAND_Y = 0.5, 0.305
FALLING_STARS = [(STAR_FALL, STAR_X, STAR_LAND_Y)]
RIPPLES = [(STAR_FALL + 0.02, STAR_X, 1.3, STAR_LAND_Y), (STAR_FALL + 0.40, STAR_X, 0.9, STAR_LAND_Y),
           (STAR_FALL + 0.85, STAR_X, 0.6, STAR_LAND_Y), (STAR_FALL + 1.40, STAR_X, 0.4, STAR_LAND_Y)]
RIPPLES_AUTO = Track([(0, 1.0), (S2, 1.0), (S2 + 3.0, 0.5), (TOTAL, 0.5)])   # steps on the water, the star
RIPPLE_COLOR = "#ffe6c4"
# where the star touched the water a thin column of light stands for a moment and reaches the middle light of
# the arch as it wakes (UPGRADE-HOWTO C). Kept faint: in draft 2 at 0.34 it was the strongest thing in the frame.
BEAM = Track([(0, 0.0), (STAR_FALL, 0.0), (STAR_FALL + 0.9, 0.20), (ARCH_FIRST + 0.6, 0.18), (S1 + 0.6, 0.0),
              (TOTAL, 0.0)])
BEAM_FROM = (STAR_X, 0.895)
BEAM_TO = (STAR_X, STAR_LAND_Y + 0.01)
BEAM_WIDTH = (0.004, 0.012)
BEAM_COLOR = "#ffe9c4"

# ---- creatures of light (UPGRADE-HOWTO M)
M_X, M_Y, M_H = 0.82, 0.300, 0.39          # Heavenly Mother: where she stands (on the water, nearer to us)
FIREFLIES = Track([(0, 0.0), (1.5, 0.0), (5.0, 0.55), (STAR_FALL, 0.55), (S1 + 1.0, 0.0), (TOTAL, 0.0)])
FIREFLIES_Y = (0.30, 0.46)
FIREFLIES_BRIGHT = 1.0
DOVES = Track([(0, 0.0), (DOVES_UP - 0.1, 0.0), (DOVES_UP + 0.5, 1.0), (G_STAR + 1.6, 1.0), (G_STAR + 4.2, 0.0),
               (TOTAL, 0.0)])
DOVES_COUNT = 12
DOVES_FROM = (M_X - 0.085, M_Y + 0.80 * M_H)   # they rise from her open hand on the side of the sun
DOVES_PATH = [(DOVES_UP, (0.66, 0.60)), (DOVES_UP + 2.4, (0.50, 0.565)), (DOVES_UP + 5.0, (0.30, 0.60)),
              (G_STAR - 1.4, (0.17, 0.72)), (G_STAR, (0.12, 0.81)), (G_STAR + 4.5, (0.10, 0.86))]
DOVES_ORBIT = 0.08
DOVES_SIZE = 0.034
DOVES_SPEED = 1.0
DOVES_COLOR = "#fff1da"
DOVES_TRAIL = 0.7
BUTTERFLIES = Track([(0, 0.0), (DAY_FULL - 2.0, 0.0), (DAY_FULL + 2.0, 1.0), (TOTAL, 1.0)])
BUTTERFLIES_COUNT = 3
BUTTERFLIES_COLOR = ("#ffb0c8", "#ffd9a0")
BUTTERFLIES_SIZE = 0.024
BUTTERFLIES_AREA = (0.06, 0.94, 0.38, 0.56)

# ---- the campaign day (UPGRADE-HOWTO I); nothing new starts after 58 s, the picture settles with the music
BUBBLES = Track([(0, 0.0), (DAY_FULL - 3.0, 0.0), (DAY_FULL + 2.0, 0.30), (TOTAL, 0.30)])
BUBBLES_SPEED = 0.9
LEAVES = Track([(0, 0.0), (DAY_FULL - 1.5, 0.0), (DAY_FULL + 3.0, 0.22), (TOTAL, 0.22)])
LEAVES_COLORS = ("#3fb83a", "#9ccc40")   # truly green, like the poster

# ---- people of light (UPGRADE-HOWTO H): the lone walker, then Heavenly Mother from behind
W_Y, W_H = 0.322, 0.29     # the walker walks on the water, a ripple under each step
W_STOP1, W_STOP2 = 0.40, M_X - 0.195   # where she stops when the star falls; where she stops before Mother
_LEGS = [(3.0, STAR_FALL - 1.04, 0.02, W_STOP1), (STAR_FALL + 0.96, S1 + 2.2, W_STOP1, W_STOP2)]


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
    # the lone walker: crosses the night, looks up when the star falls at her feet, walks on toward the first
    # light, reaches Mother, bows, and rises with the words into the Greeting light
    dict(kind="rig", preset="person", t0=1.4, t1=G_HOLD - 0.4, gather=2.0, dissolve=2.4, facing="right",
         x=walker_x, y=W_Y, height=W_H,
         actions=[(1.4, "stand"), (STAR_FALL - 0.9, {"tilt": 0.32, "blend": 0.8}), (STAR_FALL + 0.96, {"tilt": 0.0}),
                  (DOVES_UP + 0.3, "bow", {"blend": 1.5}), (DOVES_UP + 3.0, "pray", {"blend": 1.6}),
                  (G_HOLD - 1.9, "rise", {"blend": 1.4})],
         color="#ffcf9a", glow=0.85, to_star=0),
    # Heavenly Mother, only from behind; her veil flows; her arms open on the sunrise, lift in blessing, and
    # come slowly down again as she turns to light (never still)
    dict(kind="rig", preset="person_back", t0=STAR_FALL + 0.5, t1=G_HOLD - 0.2, gather=2.2, dissolve=2.8,
         x=M_X, y=M_Y, height=M_H,
         actions=[(STAR_FALL + 0.5, "stand"), (ARMS_OPEN, "open", {"blend": 2.4}),
                  (DOVES_UP, "bless", {"blend": 4.2}), (G_HOLD - 3.2, "open", {"blend": 3.6})],
         color="#ffe0c0", glow=1.1, to_star=0),
]

# ---- the gathering and the passed light (UPGRADE-HOWTO K). The two halves of the crowd leave a gap in the
# middle, where the sun stands and the flame comes down.
GATHERING = dict(t0=CROWD_IN, t1=S3 + 2.4, dissolve=2.6, count=34, center=(0.5, 0.343), spread=(0.36, 0.030),
                 rows=2, hole=0.12, height=(0.17, 0.10), speed=1.15, arrive_by=S2 + 8.0, sides=("left", "right"),
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=FLAME, speed=0.17, hold=0.22, path="crowd", start="center", source="arch",
                  descent=FLAME_DOWN, color="#ffe2a0", lift=LIFT, rise=True, arch=1.0,
                  lift_spread=0.5, rise_delay=0.6, rise_spread=1.0, rise_dur=2.3)

# ---- the campaign emblem, drawn in light and mirrored in the lake (UPGRADE-HOWTO L)
SYMBOLS = [
    dict(kind="emblem", t0=EMBLEM, t1=EMBLEM_DONE, out=EMBLEM_OUT, x=0.5, y=0.555, size=0.29,
         leave="to_star", star=4, leave_dur=EMBLEM_FLY, reflect=True, glow=1.0),
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
         form=G_FORM, hold=G_HOLD, star=G_STAR, anim="bloom"),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         star=S2 + 10.15, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         star=S2 + 7.35, **OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, star=S2 + 4.35, **OFF),
    # the middle light: woken by the falling star, the flame comes down from it, the emblem rises into it
    dict(label="Concession", lines=["“Please, after you.”"], size=164, star=ARCH_FIRST,
         arrive=[EMBLEM_OUT + EMBLEM_FLY], **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         star=BEATS[11], **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=100,
         y=0.275, form=E_FORM, hold=E_HOLD, star=E_STAR, anim="ink"),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         star=BEATS[12], **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         star=BEATS[13], **OFF),
]
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
# the opening line: written for this film (not a lyric)
FRAGMENTS = [
    dict(text="Peace begins with a word", t0=BEATS[0], t1=BEATS[0] + 3.2, out=BEATS[0] + 6.4, dy=0.10, size=88,
         glow="#ffd9a0", anim="constellation"),
]
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
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


# soft waves of light when a light of the arch wakes, and at the peak
WAVES = [(ARCH_FIRST, STAR_POS[4][0], STAR_POS[4][1], 0.55), (G_STAR, STAR_POS[0][0], STAR_POS[0][1], 0.55),
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
