"""The Words of Mother's Love Healing Concert: the epic promo (60 seconds, a trailer for the whole concert).

One continuous rise of light over one lake: night, dawn, morning, day. The arch of nine lights is the thread:
all dark at the start, complete at the peak. One hero image per movement; everything else stays quiet.
No plates, no lyrics, no faces, everyone clothed, Heavenly Mother only from behind, nothing dark behind any
text (TEXT_SHADOW = 0).

Audio: audio/promo/concert-medley.mp3 (four sections from songs 03, 09, 08 and 01; S1, S2, S3 below are its
section starts and BEATS its downbeats, as measured by the helper who cut it).

What happens (seconds; the hero of each movement is marked HERO):
 0 to 13.2    NIGHT, vast. Out of black the camera cranes up from a lake that mirrors the stars to the Milky
              Way above it. One small person of light walks on the mirror, a soft ring of light under each
              step. The opening line forms as stars joining into letters. HERO (10.24): a star crosses the
              whole sky in one long diagonal streak and lands far out on the water; its ring of light spreads
              wide across the lake toward us, and the middle light of the arch answers it.
 13.2 to 28.4 DAWN. HERO (13.21): the sun breaks the horizon, its rays come through thin clouds, and Heavenly
              Mother, only from behind, at the water's edge, opens her arms low. Doves rise from her hands
              (14.6) and fly in a loose arc into the sunrise, always well below the words. The Greeting
              blooms on the next downbeat (16.28). The walker reaches her and bows. Words, walker, Mother's
              light and the doves rise to the Greeting light.
 28.4 to 43   THE MESSAGE SPREADS. The camera pushes in slowly on the far shore, where people have come in
              twos and threes. HERO (28.35): a flame leaves the middle light of the arch, comes down into the
              first hands (31.23) and is passed from hand to hand: a vigil of warm points of light, the ones
              still waiting cooler and dimmer. The Encouragement is written in light above them. The lights of
              the arch wake one by one; the Encouragement light is the last (42.0): the arch is complete.
 43 to 60     DAY. HERO (43.00): everyone lifts their light. The lights rise slowly like lanterns while the
              camera opens wide again, and as they rise the sky warms to day: the lights become the day. The
              hearts and globe emblem draws itself in light above the lake (45.81 to 48.71) and is mirrored in
              it; a ribbon of light reveals the title while the emblem rises into the middle light of the
              arch, where it arrives on the loudest moment (54.43) and the whole arch flares. The end card
              (coral title, navy date and place) is whole by then and holds through the music's decay, over a
              sky blue lake with pale mountains, bubbles and a few green leaves. Nothing new moves after 58.

Why the sky stays saturated until about 51: people, flames and the emblem are light, and light reads weakly
on a bright sky (engine HOWTO, section S). The day opens from the horizon at the lift and reaches the pale
campaign day only as the emblem leaves.

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
        hgt = 0.030 + 0.090 * v + 0.045 * mid * (0.35 + v) + (0.012 + 0.024 * v) * (crag - 0.5)
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

TEXT_SHADOW = 0.0      # nothing dark behind any text

# ---- key moments, on the medley's downbeats (BEATS) and section starts
STAR_FALL = BEATS[3]          # 10.24: the falling star touches the lake
STAR_AIR = 2.6                # ... after crossing the sky for this long
ARCH_FIRST = STAR_FALL + 1.6  # the middle light of the arch answers as the star's ring spreads
ARMS_OPEN = S1                # 13.21: sunrise; Heavenly Mother begins to open her arms
DOVES_UP = S1 + 1.4           # 14.61: the doves rise from her hands
G_FORM = BEATS[5]             # 16.28: the Greeting blooms after the release
G_HOLD = G_FORM + 9.8         # fully formed G_FORM + 3.75 to G_HOLD: 6.05 s
G_STAR = G_HOLD + 1.7         # 27.78: its light wakes
CROWD_IN = 20.4               # the first people step in at the far left; the right side follows later (side_delay)
FLAME = S2                    # 28.35: the flame leaves the middle light of the arch
FLAME_DOWN = BEATS[10] - S2   # ... and is in the first hands on the next downbeat (31.23)
E_FORM = S2 + 0.65            # Encouragement: written in light; its middle is written after the flame has passed
E_HOLD = BEATS[13]            # 39.96: fully formed E_FORM + 3.75 to E_HOLD: 7.2 s
E_STAR = S3 - 1.0             # 42.0: the last light, the arch is complete one second before the lift
LIFT = S3                     # 43.00: everyone lifts their light
NINTH = S3 + 4.9              # 47.9: the first risen lights reach the arch and all nine lights brighten (arch.py)
EMBLEM = BEATS[15]            # 45.81: the emblem's pen of light starts
EMBLEM_DONE = BEATS[16]       # 48.71: the emblem is whole
EMBLEM_OUT = BEATS[17]        # 51.55: it lifts away
TITLE_HIT = BEATS[18]         # 54.43, the loudest moment: the emblem enters the arch, the arch's peak (arch.py)
EMBLEM_FLY = TITLE_HIT - EMBLEM_OUT
FORM_DUR = 3.0
T_FORM = TITLE_HIT - FORM_DUR - 0.75          # 50.68: the title's ribbon starts; the title is whole on TITLE_HIT
TAG_T0, TAG_T1 = T_FORM + 1.6, T_FORM + 3.5   # the end card lines rise: 52.28 to 54.18
WARM, BLUE = S3 + 4.0, S3 + 8.0               # the sky on its way to the day: 47 warm, 51 blue, TITLE_HIT pale day

# The night lake is a mirror (stars, the walker's steps and the star's ring live on the water), so the lower
# third is let go at night and calmed from the sunrise on.
BOTTOM_CALM = Track([(0, 0.15), (S1, 0.15), (S1 + 3.5, 1.0), (TOTAL, 1.0)])

# ---- the sky: one continuous rise of light (top, middle, horizon, colour of the light). The upper sky stays
# deep while white words and people of light are on screen (QA on drafts 1 to 3: the words lost contrast once
# the sky at their height passed about 0.1 in linear light).
PAL = {
    "night":   ("#02041a", "#0a1444", "#283270", "#8ea4ff"),
    "first":   ("#060a2a", "#231d54", "#8f4f6e", "#ffb090"),
    "dawn":    ("#0a1238", "#33276a", "#c8646a", "#ffc88c"),
    "sunrise": ("#0c1a48", "#3d2f78", "#cc6c68", "#ffd49c"),
    "morning": ("#0d1e50", "#40347e", "#c0606c", "#ffd8a6"),   # a rose horizon: the vigil's flames read on it
    "warm":    ("#1b3f94", "#6a6cc0", "#f6a878", "#ffe6b8"),   # the lights rise: the horizon turns to gold
    "blue":    ("#2f7ed8", "#8cc0ee", "#ffd6ac", "#fff0d4"),   # a saturated morning blue behind the emblem
}
DAY = ("#4aa3e6", "#a9d4f4", "#ffe3c4", "#fff4e0")   # the campaign day, as seen on screen
_DAY_SCALE = (0.92, 0.86, 0.78, 0.42)                 # theme.sky_tracks: the sun glow is added on top
_pal_keys = [(0.0, "night"), (STAR_FALL, "night"), (S1, "first"), (S1 + 4.0, "dawn"), (S2 - 2.0, "sunrise"),
             (S2 + 6.0, "morning"), (S3, "morning"), (WARM, "warm"), (BLUE, "blue"), (TITLE_HIT, "day"),
             (TOTAL, "day")]


def _sky(k):
    def col(p):
        return theme.display(DAY[k]) * _DAY_SCALE[k] if p == "day" else lin(PAL[p][k])
    return Track([(t, col(p)) for t, p in _pal_keys])


SKY_TOP, SKY_MID, SKY_HOR, GLOW = (_sky(k) for k in range(4))
# the hills pale and the lake brightens for the day, but both stay in the picture to the very end
SKY_THEME = Track([(0, 0.0), (S3 + 3.0, 0.0), (TITLE_HIT - 1.0, 0.65), (TOTAL, 0.65)])
# the sun: under the horizon at night, breaking it on S1, low and modest while people and the emblem are on
# screen, and still low over the lake at the end, so the water keeps a cream sun path
SUN_Y = Track([(0, 0.290), (STAR_FALL, 0.305), (S1 - 1.2, 0.330), (S1, 0.365), (S1 + 3.0, 0.400), (S2, 0.415),
               (S3, 0.425), (WARM, 0.445), (TITLE_HIT, 0.500), (TOTAL, 0.510)])
SUN_INT = Track([(0, 0.06), (STAR_FALL, 0.08), (S1 - 0.8, 0.12), (S1 + 0.5, 0.42), (S1 + 3.0, 0.52), (S2, 0.46),
                 (S3, 0.48), (WARM, 0.50), (TITLE_HIT, 0.55), (TOTAL, 0.52)])
SUN_SIZE = Track([(0, 0.09), (S1 + 3.0, 0.11), (S3, 0.12), (TITLE_HIT, 0.16), (TOTAL, 0.17)])
STARS = Track([(0, 0.0), (0.5, 0.0), (2.6, 1.0), (STAR_FALL, 1.0), (S1 + 2.0, 0.60), (S1 + 7.0, 0.25),
               (S2 + 2.0, 0.10), (S3, 0.05), (WARM, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (0.8, 0.0), (3.5, 0.90), (STAR_FALL, 0.90), (S1 + 0.5, 0.35), (S1 + 3.5, 0.0), (TOTAL, 0.0)])
# the stars mirrored in the lake (engine/lake_stars.py): the night is a sea of stars
LAKE_STARS = Track([(0, 0.0), (0.4, 0.0), (2.4, 0.95), (STAR_FALL, 0.95), (S1, 0.60), (S1 + 3.0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.05), (S1, 0.10), (S1 + 6.0, 0.20), (S2, 0.18), (S3, 0.16), (TOTAL, 0.10)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# half as many floating motes as before, and small ones only (MOTE_SIZE): more empty sky
MOTES = Track([(0, 0.0), (2.0, 0.04), (S1, 0.05), (S2, 0.06), (S3, 0.07), (TITLE_HIT, 0.09), (TOTAL, 0.09)])
MOTE_SIZE = (2.0, 9.0)
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (2.4, 1.0), (TOTAL - 0.6, 1.0), (TOTAL - 0.05, 0.0)])   # out of black
# the sky's own soft sunbeams round the sun
RAYS = Track([(0, 0.0), (S1, 0.05), (S1 + 2.0, 0.45), (S2, 0.35), (S3, 0.35), (WARM, 0.30), (BLUE + 1.0, 0.12),
              (TOTAL, 0.10)])
# the lane of light at the sun: off. Draft 3 tested it (0 against 0.47, same sun): no change in the picture.
PART = Track([(0, 0.0), (TOTAL, 0.0)])
SKYLINE_LANTERN = 0.0      # no travelling light on the skyline: the falling star is the one star of this film


def MOTE_COLORS(t):
    return ("#ffe2a8", "#ffb48c") if t < BLUE else (theme.WHITE_GLOW, theme.GOLD)


# ---- sky and camera (UPGRADE-HOWTO O)
CLOUDS3D = Track([(0, 0.10), (STAR_FALL, 0.14), (S1 + 1.0, 0.30), (S2, 0.24), (S3, 0.20), (BLUE + 1.0, 0.14),
                  (TOTAL, 0.14)])
CLOUDS_SPEED = 1.3
CLOUDS_LIGHT = 0.8
# The sunrise: shafts of light through the thin clouds and past the hills, for the first seconds of the dawn
# only. In draft 4 the rays at 0.30 with the default contrast laid a tan haze over the upper sky, so here the
# contrast is high (distinct shafts, little even haze), the reach is short, and they ease away before the
# Greeting is whole and are off before the emblem.
GOD_RAYS = Track([(0, 0.0), (S1 - 0.3, 0.0), (S1 + 1.2, 0.55), (S1 + 3.0, 0.50), (G_FORM + 3.5, 0.20), (S2, 0.14),
                  (E_HOLD, 0.10), (S3 + 1.0, 0.0), (TOTAL, 0.0)])
RAYS_CONTRAST = 2.0
RAYS_DECAY = 0.975
RAYS_COLOR = "#ffd4a0"
# One slow camera gesture. A crane up from the mirror of stars to the wide night (level before the star lands);
# still through the dawn (the doves' goal is not moved by the camera); a slow push in on the far shore while the
# flame is passed; then wide again as the lights rise. The centre of the push in is the far shore, so the shore
# stays where it is on screen and out of the lower third.
CAMERA_CRANE = Track([(0, -0.28), (1.2, -0.275), (9.4, 0.0), (TOTAL, 0.0)])
CAMERA_ZOOM = Track([(0, 1.0), (19.0, 1.0), (S2, 1.10), (E_HOLD, 1.35), (S3 - 0.8, 1.35), (S3 + 4.5, 1.03),
                     (S3 + 7.0, 1.0), (TOTAL, 1.0)])
CAMERA_CENTER = (0.5, 0.35)
PARALLAX = 1.0
CREATURES_DEPTH = 0.0      # doves and butterflies keep their place on screen, so the doves reach their light

# ---- music-reactive light, all gentle (UPGRADE-HOWTO P)
AUDIO_REACT = 1.0
REACT_GLOW = 0.35
REACT_SPARKLE = 0.15
REACT_ARCH = 0.6
REACT_AURORA = 0.0
REACT_CHORUS = 0.25

# ---- the lake responds (UPGRADE-HOWTO L)
STAR_X, STAR_LAND_Y = 0.50, 0.315    # far out on the water, where the sun will rise
# one star, a long diagonal streak from the upper left (drawn twice so the thin streak reads)
_STAR = (STAR_FALL, STAR_X, STAR_LAND_Y, 0.04, 1.03, STAR_AIR, 180)
FALLING_STARS = [_STAR, _STAR]
# its ring of light spreads wide across the lake toward the camera (the fifth number: how fast a ring spreads);
# two small rings under the emblem as it is drawn and as it is whole
RIPPLES = [(STAR_FALL + 0.02, STAR_X, 2.2, STAR_LAND_Y, 4.5), (STAR_FALL + 0.02, STAR_X, 1.2, STAR_LAND_Y),
           (STAR_FALL + 0.50, STAR_X, 1.5, STAR_LAND_Y, 4.5), (STAR_FALL + 1.05, STAR_X, 1.0, STAR_LAND_Y, 4.5),
           (EMBLEM + 0.5, 0.5, 0.5, 0.22), (EMBLEM_DONE, 0.5, 0.6, 0.22)]
RIPPLES_AUTO = Track([(0, 1.4), (S1, 1.4), (S1 + 3.0, 0.8), (S2, 0.5), (TOTAL, 0.5)])   # steps on the water
RIPPLE_COLOR = "#ffe6c4"

# ---- creatures of light (UPGRADE-HOWTO M)
# Heavenly Mother: on the right third, at the water's edge. She stands to the right of the Greeting's last
# letter (about 0.73 of the width) and her head stays under the words' lower edge.
M_X, M_Y, M_H = 0.77, 0.335, 0.34
M_T0 = STAR_FALL + 0.76                    # she gathers while the star's ring spreads
# The doves: a larger flock, close to us. They rise from her hand on the side of the sun and fly a loose arc
# over the sunrise, low: the Greeting's letters reach down to about 0.68 of the height, and the goal stays at
# 0.50 or lower while the flock is under them. They climb only at the far left, to the Greeting light.
DOVES = Track([(0, 0.0), (DOVES_UP - 0.1, 0.0), (DOVES_UP + 1.2, 1.0), (G_STAR + 0.4, 1.0), (G_STAR + 2.4, 0.0),
               (TOTAL, 0.0)])
DOVES_COUNT = 14
DOVES_FROM = (0.715, 0.525)
DOVES_PATH = [(DOVES_UP, (0.66, 0.51)), (DOVES_UP + 2.2, (0.52, 0.485)), (DOVES_UP + 5.0, (0.36, 0.47)),
              (DOVES_UP + 8.0, (0.22, 0.49)), (G_HOLD - 0.8, (0.13, 0.60)), (G_STAR, (0.12, 0.80)),
              (G_STAR + 3.0, (0.11, 0.84))]
DOVES_ORBIT = 0.05
DOVES_SIZE = 0.054
DOVES_SPEED = 1.0
DOVES_COLOR = "#fff1da"
DOVES_TRAIL = 0.6
BUTTERFLIES = Track([(0, 0.0), (WARM + 0.5, 0.0), (WARM + 3.0, 1.0), (TOTAL, 1.0)])
BUTTERFLIES_COUNT = 2
BUTTERFLIES_COLOR = ("#ffb0c8", "#ffd9a0")
BUTTERFLIES_SIZE = 0.026
BUTTERFLIES_AREA = (0.10, 0.90, 0.355, 0.46)

# ---- the campaign day (UPGRADE-HOWTO I); nothing new starts after 58 s, the picture settles with the music
BUBBLES = Track([(0, 0.0), (BLUE - 1.5, 0.0), (TITLE_HIT, 0.26), (TOTAL, 0.26)])
BUBBLES_SPEED = 0.9
LEAVES = Track([(0, 0.0), (BLUE, 0.0), (TITLE_HIT + 0.5, 0.18), (TOTAL, 0.18)])
LEAVES_COLORS = ("#3fb83a", "#9ccc40")   # truly green, like the poster

# ---- people of light (UPGRADE-HOWTO H): the lone walker, then Heavenly Mother from behind
# The walker is small: one light crossing a sea of stars. She walks on the mirror, away from us and to the
# right, stops to watch the star cross the sky and land, walks on into the sunrise, and comes to Mother.
W_X0, W_XP, W_X1 = 0.07, 0.33, 0.62     # where she starts, where she stops for the star, where she stops
W_Y0, W_Y1 = 0.250, 0.318               # her feet line: on the water, rising toward the far shore
W_H0, W_H1 = 0.17, 0.15                 # ... and she grows a little smaller as she walks away
_LEGS = [(3.0, STAR_FALL - 0.7, W_X0, W_XP), (STAR_FALL + 1.2, S1 + 3.0, W_XP, W_X1)]


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


def _walk_u(t):
    return (walker_x(t) - W_X0) / (W_X1 - W_X0)


def walker_y(t):
    return W_Y0 + (W_Y1 - W_Y0) * _walk_u(t)


def walker_h(t):
    return W_H0 + (W_H1 - W_H0) * _walk_u(t)


# Mother's arms open low and stay low: about 40 degrees below the horizontal, forearms a little higher, then
# a breath up (about 30 degrees below) and down again. Never a flat T.
M_LOW = (0.82, 1.25, 0.96, 1.05)
M_MID = (0.93, 1.25, 1.06, 1.05)
FIGURES = [
    dict(kind="rig", preset="person", t0=1.2, t1=G_HOLD - 0.4, gather=2.0, dissolve=2.4, facing="right",
         x=walker_x, y=walker_y, height=walker_h,
         actions=[(1.2, "stand"), (STAR_FALL - 1.3, {"tilt": 0.35, "blend": 0.8}), (STAR_FALL + 1.2, {"tilt": 0.0}),
                  (S1 + 4.2, "bow", {"blend": 1.5}), (S1 + 6.8, "pray", {"blend": 1.6}),
                  (G_HOLD - 1.9, "rise", {"blend": 1.4})],
         color="#ffd9a8", glow=1.0, to_star=0),
    # Heavenly Mother, only from behind; her veil flows; her arms open on the sunrise (never still)
    dict(kind="rig", preset="person_back", t0=M_T0, t1=G_HOLD - 0.2, gather=2.0, dissolve=2.6,
         x=M_X, y=M_Y, height=M_H,
         actions=[(M_T0, "stand"), (ARMS_OPEN, "open", {"blend": 2.6, "arm_r": M_LOW, "arm_l": M_LOW}),
                  (S1 + 5.2, "open", {"blend": 3.4, "arm_r": M_MID, "arm_l": M_MID}),
                  (S1 + 9.4, "open", {"blend": 3.0, "arm_r": M_LOW, "arm_l": M_LOW})],
         color="#ffe0c0", glow=1.1, to_star=0),
]

# ---- the gathering and the passed light (UPGRADE-HOWTO K). People come in twos and threes with gaps between
# the groups (cluster), in one row, all grown ups of about the same height (0.13 to 0.15 of the screen once the
# camera has pushed in); the two halves leave the middle open, where the sun stands and the flame comes down.
# The people from the right come 4.8 s later (side_delay): Heavenly Mother stands there until G_HOLD.
# Their robes are cool and dim until the flame reaches them; then each holds a warm point of light.
GATHERING = dict(t0=CROWD_IN, t1=S3 + 3.6, dissolve=2.6, count=26, center=(0.5, 0.343), spread=(0.33, 0.02),
                 rows=1, hole=0.14, cluster=(2, 3), height=(0.112, 0.07), children=0.0, speed=1.5,
                 arrive_by=S2 + 7.5, sides=("left", "right"), side_delay=(0.0, 4.8), glow=1.5, detail=520,
                 colors=("#cfd6ff", "#d9ccff", "#c8dcff", "#e6dcff"))
# the flame comes down to the person nearest the middle on the left (start: the nearest to that point)
PASS_LIGHT = dict(t0=FLAME, speed=0.15, hold=0.22, path="crowd", start=(0.44, 0.34), source="arch",
                  descent=FLAME_DOWN, color="#ffcf8a", lift=LIFT, rise=True, arch=1.0,
                  lift_spread=0.6, rise_delay=0.7, rise_spread=2.0, rise_dur=3.6)

# ---- the campaign emblem, drawn in light and mirrored in the lake (UPGRADE-HOWTO L)
SYMBOLS = [
    dict(kind="emblem", t0=EMBLEM, t1=EMBLEM_DONE, out=EMBLEM_OUT, x=0.5, y=0.60, size=0.29,
         leave="to_star", star=4, leave_dur=EMBLEM_FLY, reflect=True, glow=1.6),
]

# ---- the arch of nine lights: dark at the start, complete at the peak
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9)
# The glow round the two expressions: a deeper gold than the engine's own (#ffc48c). With it the full quality
# stills of the earlier cut passed the legibility check; whether the colour is the reason was not isolated.
WORD_GLOW = "#f2aa62"
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=150, y=0.258,
         form=G_FORM, hold=G_HOLD, star=G_STAR, anim="bloom", glow=WORD_GLOW),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         star=S2 + 10.15, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         star=S2 + 7.35, **OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, star=S2 + 4.35, **OFF),
    # the middle light: woken by the falling star, the flame comes down from it, the emblem rises into it
    dict(label="Concession", lines=["“Please, after you.”"], size=164, star=ARCH_FIRST,
         arrive=[TITLE_HIT], **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         star=BEATS[11], **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=100,
         y=0.295, form=E_FORM, hold=E_HOLD, star=E_STAR, anim="ink", glow=WORD_GLOW),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         star=BEATS[12], **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         star=BEATS[13], **OFF),
]
# The end card. The title sits a little higher than the engine's own place for it (0.315), so that the three
# lines under it, now much larger, end above the far shore.
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.28,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
# the opening line: written for this film (not a lyric)
FRAGMENTS = [
    dict(text="Peace begins with a word", t0=BEATS[0], t1=BEATS[0] + 3.2, out=BEATS[0] + 6.4, dy=0.10, size=88,
         glow="#ffd9a0", anim="constellation"),
]
# date, church, address: each line more than 60 percent larger than the engine's own 48 (sizes)
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(80, 78), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
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


# The three lights with a story (the star's, the Greeting's, the Encouragement's) wake with the arch's usual
# expanding ring. The six that wake in the wave only flare: in draft 4 their rings crossed the label of the
# Encouragement again and again.
QUIET_LIGHTS = (1, 2, 3, 5, 7, 8)

# soft waves of light when a light of the arch wakes, and at the peak
WAVES = [(ARCH_FIRST, STAR_POS[4][0], STAR_POS[4][1], 0.55), (G_STAR, STAR_POS[0][0], STAR_POS[0][1], 0.55),
         (TITLE_HIT, 0.5, 0.62, 0.6)]

# the lake's own note rings: none at night (only the walker's steps and the star ring there) and none by day
NOTE_RINGS = Track([(0, 0.0), (S1, 0.0), (S1 + 3.0, 1.0), (S3, 1.0), (S3 + 3.0, 0.0), (TOTAL, 0.0)])


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    lx, ly = song.lantern(t)
    z = ZOOM(t)
    lsx, lsy = (lx - 0.5) / z + 0.5, (ly - HORIZON) / z + HORIZON
    waves = [(t - w[0], w[1], w[2], w[3]) for w in WAVES if 0.0 <= t - w[0] < 6.0]
    nr = NOTE_RINGS(t)
    rings = [(r[0], r[1], r[2], r[3] * nr) for r in song.rings_at(t)] if nr > 0 else []
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t) * (0.92 + 0.20 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=lx, rings=rings, waves=waves,
        star=[(s[0], -1.0, s[2]) if i in QUIET_LIGHTS else s
              for i, s in enumerate(star_state(t))],   # noqa: F821  (installed by engine/song.py from arch.py)
        link=link_state(t),   # noqa: F821
    )
