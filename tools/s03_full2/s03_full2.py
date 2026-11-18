"""Song 03, I Reminisce About Your Love: the full-length concert backdrop, version 2 ("The Lake of Memory").

Concert item 4, Sunday December 6. Timed to the 5:13 live length (DESIGN-SYSTEM 12a.10): the reference upload
(355.09 s) conformed to 313.0 s by removing one repeated chorus 2 passage (tools/s03_full2/prepare.py), then a
15 second calm hold: 328.0 s at 60 fps. Timeline: project-docs/backdrops/s03-full2/TIMELINE.md.
Look (DESIGN-SYSTEM 6, row 03): indigo night of memory, rain, then a rose dawn; indigo, rose, warm gold; rain,
lanterns, aurora, petals; low over the water. No comets (song 01 only).

This is the pinned engine's song module (d928ff9, loaded as songs.s03_full2). The opening lockup, signature,
expressions, lyric fragments, hearts and symbols are drawn by tools/s03_full2/overlay2.py; the people of the two
expressions by tools/s03_full2/people.py. Everything is a pure function of time, so any frame renders alone.
No em dash or en dash anywhere in this file.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is tools/s03_full/)
ROOT = os.path.join(REPO, "work", "nine_colours_minor", "render1")   # the pinned engine snapshot (plates, fonts)
SONG_ID = os.path.splitext(os.path.basename(__file__))[0]
FEATURES = os.environ.get("FEATURES", os.path.join(REPO, "work", "s03_full2", "features.npz"))

FPS = 60
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 309.0      # last sounding moment (live seconds; the tail fades out by 309 s)
SONG_END = 313.0       # the live length
TOTAL = 328.0          # the song, then the 15 second calm hold
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.30         # water line, as a fraction of the height from the bottom

RIDGE_X0, RIDGE_W = 0.035, 0.93


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
        self.hi = _ar(np.interp(ft, t, np.clip((hi - lo_) / (hi_ - lo_), 0, 1), right=0.0), 0.04, 0.35)
        on = np.clip(d["onset"] / np.percentile(d["onset"], 99), 0.0, 1.4)
        # max-pool the onset envelope into video frames
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain skyline is the loudness of the whole song
        xs = np.linspace(0.0, 1.0, 2048)
        st = (xs - RIDGE_X0) / RIDGE_W * MUSIC_END
        base_t = _gauss(n_f, 2.3 * FPS)
        mid_t = _gauss(n_f, 1.0 * FPS)
        base = np.interp(st, ft, base_t)
        mid = np.interp(st, ft, mid_t) - base
        v = np.clip((base - 0.30) / 0.56, 0.0, 1.0) ** 1.6
        rng = np.random.default_rng(7)

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 20 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 16), (0.25, 35), (0.125, 78), (0.0625, 170), (0.03, 380))))
        inside = (st >= 0) & (st <= MUSIC_END)
        hgt = 0.020 + 0.150 * v + 0.075 * mid * (0.35 + v) + (0.012 + 0.034 * v) * (crag - 0.5)
        edge = 0.018 + 0.012 * (crag - 0.5)
        sh = np.clip(np.minimum(xs - 0.0, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.where(inside, hgt, edge) * (0.5 + 0.5 * sh)
        self.ridge = np.maximum(self.ridge, 0.006).astype("f4")
        # backdrop: a calm, fixed far range (not the song's loudness), lower in the middle where the sun will rise
        calm = 0.030 + 0.030 * crag + 0.020 * np.cos(np.pi * (xs - 0.5)) ** 2 * (1.0 - np.exp(-((xs - 0.5) / 0.12) ** 2))
        self.ridge = calm.astype("f4")
        # water rings: one per clear note onset, placed by a hash of its index
        ons = d["onsets"]
        strength = np.interp(ons, t, on)
        keep, last = [], -9.0
        for k, (ot, s) in enumerate(zip(ons, strength)):
            if s > 0.33 and ot - last > 0.30 and ot < MUSIC_END:
                r = np.random.default_rng(1000 + k).random(2)
                keep.append((float(ot), 0.06 + 0.88 * r[0], HORIZON * (0.12 + 0.70 * r[1] ** 1.3), float(min(s, 1.2))))
                last = ot
        self.rings = keep
        self.ring_t = np.array([k[0] for k in keep])

    def lantern(self, t):
        x = RIDGE_X0 + RIDGE_W * min(max(t / MUSIC_END, 0.0), 1.0)
        y = HORIZON + float(np.interp(x, np.linspace(0, 1, 2048), self.ridge))
        return x, y

    def rings_at(self, t, n=16, life=4.5):
        i1 = int(np.searchsorted(self.ring_t, t, side="right"))
        out = []
        for k in range(i1 - 1, -1, -1):
            age = t - self.rings[k][0]
            if age > life or len(out) >= n:
                break
            out.append((self.rings[k][1], self.rings[k][2], age, self.rings[k][3]))
        return out



# ----------------------------------------------------------------- timeline (stage video seconds = live seconds)

from track import Track   # noqa: E402

# Live landmarks (TIMELINE.md). Live time equals reference time up to the conform cut at 272.74 s; after it,
# live = reference - 42.05 s (the repeated chorus 2 passage is sung once).
SWELL = 15.5          # the introduction's swell (to 19)
VERSE1 = 25.0         # verse 1, quiet ("Mother, to save my life")
WELCOME = 73.5        # "With a warm and gentle smile": the music rises
CHORUS1 = 96.0        # chorus 1 arrives (soft, then full from 117.5)
LIFE = 134.8          # "Oh, Mother is my ev'rything": the memories light one by one
DROP = 173.5          # the sudden drop into verse 2
FREEZE = 186.0        # "Mother comforted my heart": time stops
HANDS = 198.0         # "I used to feel Her warm hands"
PRAYER = 222.0        # "Putting Her hands together"
SEED = 238.0          # "In my frail and feeble heart": the seed of courage, the crescendo
SUNRISE = 242.0       # chorus 2 arrives
CUT = 272.74          # the conform join (one repeated passage removed)
CLIMAX = 280.95       # the loudest moment (reference 5:23)
PAUSE = 289.95        # the grand pause (to 291.85)
TAG = 291.85          # the closing "I love You Mother"
NINTH = 1e9           # the whole arch does not glow in this song
TITLE_HIT = 1e9       # no end card (only song 11 has one)

APOLOGY_STAR = 40.6       # the Apology's words reach light 3 (first lit in the concert)
ENC_ARRIVE = 237.0        # the Encouragement's words reach light 7 (relit: a flare and one new thin ring)

BOTTOM_CALM = 1.0
HOME_X = 0.44
SKYLINE_LANTERN = Track([(0, 1.0), (88.0, 1.0), (96.0, 0.0), (TOTAL, 0.0)])
RINGS_AT_START = {6: 1}   # light 7 earned one ring when song 02 relit it
TEXT_SHADOW = 0.0          # nothing dark behind any text

# Sky and lake (the first 98 seconds are the engine's own night lake; later only seen around the plates)
PAL = {
    "night":   ("#0a0e34", "#1e2160", "#58407a", "#ffc9a0"),
    "memory":  ("#0b0e36", "#242462", "#62437a", "#ffc4a0"),
    "welcome": ("#0e1240", "#302a6a", "#925a78", "#ffd0a0"),
    "dusk":    ("#0e1240", "#30265e", "#925672", "#ffc8a0"),
    "storm":   ("#0a0e30", "#1a2050", "#36386e", "#d8b8f0"),
    "aurora":  ("#0a0c34", "#22225e", "#4e4284", "#e8c0ff"),
    "predawn": ("#0f1238", "#3c2e60", "#c4727a", "#ffc0a4"),
    "dawn":    ("#141c4c", "#584276", "#ec8c8a", "#ffd2a4"),
    "morning": ("#13265c", "#7d5086", "#f1a67c", "#ffe0b0"),
}
_pal_keys = [(0.0, "night"), (40.0, "night"), (50.0, "memory"), (70.0, "memory"), (82.0, "welcome"),
             (96.0, "dusk"), (172.0, "dusk"), (176.0, "storm"), (196.0, "storm"), (204.0, "aurora"),
             (232.0, "aurora"), (240.0, "predawn"), (244.0, "dawn"), (300.0, "dawn"), (316.0, "morning"),
             (TOTAL, "morning")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.20), (70, 0.22), (90, 0.32), (100, 0.16), (230, 0.12), (241, 0.30), (TOTAL, 0.30)])
SUN_Y = Track([(0, 0.27), (TOTAL, 0.30)])
SUN_SIZE = Track([(0, 0.10), (TOTAL, 0.11)])
STARS = Track([(0, 0.85), (40, 0.85), (60, 0.55), (90, 0.35), (100, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.25), (60, 0.22), (96, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])
# the indigo aurora of memory: faint in the introduction's swell, glowing behind the welcome
AURORA = Track([(0, 0.0), (9.5, 0.0), (14.0, 0.12), (17.5, 0.38), (22.0, 0.14), (26.0, 0.0), (76.0, 0.0), (84.0, 0.30),
                (96.0, 0.0), (TOTAL, 0.0)])
# Her hidden pain: a soft fine rain from the end of the introduction; it thins and stops while the Apology is
# read (the stillness: the lake becomes a mirror); the storm of verse 2 until time stops
RAIN = Track([(0, 0.0), (19.0, 0.0), (22.5, 0.26), (25.0, 0.26), (27.6, 0.0), (173.5, 0.0),
              (176.0, 0.36), (184.5, 0.34), (186.6, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.18), (25, 0.12), (40, 0.12), (47, 0.18), (96, 0.24), (118, 0.32), (172, 0.30), (176, 0.10),
               (200, 0.16), (222, 0.12), (236, 0.20), (244, 0.30), (300, 0.30), (312, 0.24), (TOTAL, 0.22)])
MOTE_SIZE = (2.4, 18.0)
LANTERNS = Track([(0, 0.0), (186.0, 0.0), (190.0, 0.55), (206.0, 0.65), (216.0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (160.0, 0.0), (166.0, 0.10), (173.0, 0.0), (244.0, 0.0), (248.0, 0.22),
                (CLIMAX - 4.0, 0.26), (PAUSE, 0.24), (PAUSE + 0.4, 0.06), (TAG + 1.0, 0.10), (310.0, 0.12),
                (TOTAL, 0.10)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 1.0), (TOTAL, 1.0)])           # never black: frame 0 is the night lake, the last the morning
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
LAKE_STARS = Track([(0, 0.30), (40, 0.30), (60, 0.15), (96, 0.0), (TOTAL, 0.0)])

# Painted scenes (the song's own plates, assets/plates/s03). 0 to 98: the engine's own night lake.
SCENES = [
    # chorus 1: the forgotten memories mend into the great moon held by gold seams
    dict(image="assets/plates/s03/mended_moon_predawn.jpg", t0=95.0, t1=176.5, fade_in=4.0, fade_out=3.0,
         transition="bloom", flash=0.2, zoom=(1.16, 1.04), pan=((0.0, -0.02), (0.0, 0.0)), water=True,
         water_line=0.34, water_strength=0.45, calm_gain=0.12,
         gain=Track([(0, 0.95), (TOTAL, 0.95)])),
    # verse 2: the storm, time stops, raindrops become lanterns
    dict(image="assets/plates/s03/frozen_rain_lanterns.jpg", t0=173.5, t1=201.0, fade_in=3.0, fade_out=3.0,
         transition="fade", zoom=(1.12, 1.05), pan=((-0.02, 0.0), (0.0, 0.0)), water=True, water_line=0.25,
         water_strength=0.5, calm_gain=0.25, gain=0.98),
    # Her warm hands: violet aurora, sky lanterns
    dict(image="assets/plates/s03/aurora_hands_night.jpg", t0=198.0, t1=224.5, fade_in=3.0, fade_out=3.0,
         transition="fade", zoom=(1.03, 1.10), pan=((0.0, 0.0), (0.0, 0.02)), water=True, water_line=0.31,
         water_strength=0.5, calm_gain=0.4, gain=1.0),
    # Her prayer: one column of light from the horizon into the arch, a mirror lake
    dict(image="assets/plates/s03/prayer_mirror.jpg", t0=221.5, t1=244.0, fade_in=3.0, fade_out=2.5,
         transition="fade", zoom=(1.14, 1.10), water=True, water_line=0.29, water_strength=0.5, calm_gain=0.4,
         gain=Track([(0, 1.0), (223.0, 1.0), (225.0, 0.90), (235.0, 0.90), (237.0, 1.0)])),
    # chorus 2 to the end: the rose dawn
    dict(image="assets/plates/s03/rose_dawn.jpg", t0=240.5, t1=TOTAL + 1.0, fade_in=2.5, fade_out=0.0,
         transition="bloom", flash=0.25, zoom=(1.12, 1.03), water=True, water_line=0.255, water_strength=0.45,
         calm_gain=0.25,
         gain=Track([(0, 0.95), (PAUSE - 0.4, 0.95), (PAUSE + 0.3, 0.88), (TAG + 0.5, 0.88), (TAG + 3.0, 0.92),
                     (TOTAL, 0.92)])),
]

# The sky breaks into forgotten memories after the Apology, drifts, and mends; gold seams heal it
SHARDS = Track([(0, 0.0), (47.0, 0.0), (51.0, 1.0), (60.0, 1.0), (68.0, 0.55), (84.0, 0.35), (92.0, 0.0), (TOTAL, 0.0)])
SHARDS_MEND = Track([(0, 0.0), (84.0, 0.0), (90.0, 0.9), (95.0, 0.9), (98.0, 0.0), (TOTAL, 0.0)])
SHARDS_Y = 0.70           # only high in the sky
SHARDS_COLOR = "#ffd27a"
FLASH = Track([(0, 0.0), (241.4, 0.0), (242.2, 0.16), (244.5, 0.0), (TOTAL, 0.0)])   # the sun breaks through

# The lake answers (the engine keeps rings out of the calm lower third; these sit at the far water)
RIPPLES = [(36.9, 0.50, 1.4, 0.27, 4.5), (85.0, 0.62, 1.4, 0.28, 4.8), (239.0, 0.50, 1.2, 0.28, 3.5),
           (240.4, 0.50, 1.2, 0.28, 4.0), (TAG + 0.3, 0.50, 0.8, 0.27, 3.5)]
RIPPLES.sort(key=lambda r: r[0])
RIPPLES_AUTO = Track([(0, 0.0), (TOTAL, 0.0)])
RIPPLE_COLOR = "#ffe2b8"
# the seed of courage falls from the closing prayer into the far water
FALLING_STARS = [(238.2, 0.50, 0.40, 0.50, 0.70, 2.0, 60)]

# Nine lights on an arch over the stage, one for each expression: a compact arch high in the middle of the
# sky, clear of the signature in the top left corner (x 0.30 to 0.70)
STAR_POS = []
for i in range(9):
    x = 0.30 + 0.05 * i
    y = 0.915 - 0.045 * ((x - 0.5) / 0.20) ** 2
    STAR_POS.append((x, y))

_OFF = dict(form=1e9, hold=1e9, star=1e9)       # not lit yet in the concert
_LIT = dict(form=1e9, hold=1e9, star=-100.0)    # lit before this song
# the engine's own words are off: the expressions are drawn in the Revision 3 style by overlay2.py; these
# entries keep only the arch's history (when each light is lit and relit)
PHRASES = [
    dict(label="Greeting", lines=["x"], size=100, **_OFF),
    dict(label="Gratitude", lines=["x"], size=100, **_OFF),
    dict(label="Apology", lines=["x"], size=100, form=1e9, hold=1e9, star=APOLOGY_STAR),
    dict(label="Inclusiveness", lines=["x"], size=100, **_OFF),
    dict(label="Concession", lines=["x"], size=100, **_OFF),
    dict(label="Respect", lines=["x"], size=100, **_OFF),
    dict(label="Encouragement", lines=["x"], size=100, form=1e9, hold=1e9, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["x"], size=100, **_OFF),
    dict(label="Compliment", lines=["x"], size=100, **_LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=1e9, hold=1e9, star=1e9)

# People: the two expressions are acted by warm gold glitter people of the 3D layer (people.py), laid over
# this picture. The engine's flat figures: only Heavenly Mother's cupped hands of light under "Her warm hands".
_SF = "assets/song_figures/"
FIGURES = [
    dict(poses=[_SF + "s03/mother_hands_cupped.png"], t0=204.5, gather=1.8, t1=210.5, x=(0.55, 0.56),
         y=(0.40, 0.44), move=(204.5, 212.5), height=(0.20, 0.19), dissolve=2.2, leave="drift", color="#ffe2c0",
         glow=0.6, particles=8000),
]

BEAM = Track([(0, 0.0), (TOTAL, 0.0)])

FRAGMENTS = []          # the three lyric fragments are drawn by overlay2.py, each with its own effect
TAGLINE = dict(text="", t0=1e9, t1=1e9 + 1)

AURORA_COOL = ("#6f7cff", "#a58cff")
AURORA_WARM = ("#ffa29a", "#ffcc8c")
PETAL_COLORS = ("#ff8fae", "#ffd6b0")
LANTERN_COLORS = ("#ffc070", "#ff9a5a")
MOTE_COLORS = ("#ffe0a8", "#ffa8b8")

# The engine's corner credit is off; overlay2.py draws the opening lockup and the signature.
CREDIT = dict(song="I Reminisce About Your Love", concert="The Words of Mother’s Love",
              t_in=1e9, t_full=1e9 + 1, t_move=1e9 + 2, t_rest=1e9 + 3, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_out=(1e9 + 4, 1e9 + 5))


def credit_state(t, bbox):
    x0, x1, y0, y1 = bbox
    return (0.5 * (x0 + x1), 0.5 * (y0 + y1), 1.0, 0.0), (0.5 * (x0 + x1), 0.5 * (y0 + y1))


# Waves of light across the sky: the Apology lighting light 3, the Encouragement relighting light 7, the sunrise
WAVES = [(APOLOGY_STAR, STAR_POS[2][0], STAR_POS[2][1], 0.5), (ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.5),
         (SUNRISE, 0.5, 0.33, 0.45)]


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    if t > MUSIC_END - 4.0:
        # after the music the scene keeps breathing gently on its own
        k = min((t - (MUSIC_END - 4.0)) / 6.0, 1.0)
        breath = 0.40 + 0.06 * np.sin(t * 0.55) + 0.04 * np.sin(t * 0.23 + 1.0)
        env = env * (1 - k) + breath * k
        envs = envs * (1 - k) + breath * k
        hi = hi * (1 - k) + (0.32 + 0.08 * np.sin(t * 0.8)) * k
        pulse = pulse * (1 - k)
    # the home star rests on the horizon just left of centre, where the sun will rise (song 02 hand-off)
    lx = HOME_X
    ly = HORIZON + float(np.interp(lx, np.linspace(0, 1, 2048), song.ridge)) - 0.004
    z = ZOOM(t)
    lsx, lsy = (lx - 0.5) / z + 0.5, (ly - HORIZON) / z + HORIZON
    waves = [(t - w[0], w[1], w[2], w[3]) for w in WAVES if 0.0 <= t - w[0] < 6.0]
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t) * (0.88 + 0.30 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t) * (0.7 + 0.6 * envs), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=1.0, rings=song.rings_at(t), waves=waves,
        star=star_state(t), link=link_state(t),
    )
