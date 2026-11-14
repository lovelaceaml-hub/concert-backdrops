"""Song 02, The Rose: 1 minute promo v4 in the ORIGINAL style (Anthony's direction round 4), visual only, no music
yet (no recording of the trio exists; the workflow's audio file audio/promo/s02.mp3 is a silent placeholder).

The engine's own luminous world, as in engine/songs/s03_original.py: a deep sky with stars, a still lake with the
mountain line and its mirror, a faint aurora, falling frost glints, the traveler's light along the skyline and the
arch of nine lights. Words are glowing gold light straight on the sky; nothing dark behind any text
(TEXT_SHADOW = 0, no painted plates). The 02 look (DESIGN-SYSTEM.md section 6): deep winter night with snowfall,
a pale pink spring dawn; silver blue, white, blush pink; close and quiet framing; no Milky Way, no lanterns, no
rain, no ice (song 04 owns ice and thaw). Song 02 owns snow, the seed and the rose.

Four scenes, each with its own sky, light, objects and framing:
  0 to 14   1 FIRST SNOW: the last warm dusk sinks into a silver-blue winter night over the wide lake; the first
            flakes fall and thicken; fragment "too lonely" rises out of the water
  14 to 30  2 THE VIOLET VEIL: the snow eases, a silver-violet aurora veil opens over the mountains and the
            camera closes in; the full Encouragement words glow on the night sky and fly into star 7 (a flare
            and one new ring)
  30 to 40  3 THE SEED UNDER THE SNOW: the deepest, clearest night, close framing, the sky full of stars and
            soft snow; a thread of light falls from star 7 to the near shore and a seed of light gathers there;
            fragment "the seed" is written in light
  40 to 60  4 THE ROSE AT DAWN: a pearl and blush dawn; the snow turns into the rose's petals; the seed grows
            into a bud and opens into a rose of light; fragment "becomes the rose" settles in petals; the
            three-line end card on the dawn sky; at the very end the rose lets go and drifts up as light
Signature moments: falling snow in depth (SNOW) turning into blush petals (PETALS), the thread of light to the
seed (BEAM), the rose of light growing from seed to bud to bloom (FIGURES with the song's own drawings in
assets/song_figures/s02/, not people). No people of light in this version.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.path.splitext(os.path.basename(__file__))[0]
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))  # not used (no music)

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5       # the drawn timeline (no music yet)
SONG_END = 60.0
TOTAL = 60.0           # promo length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.36         # water line ("horizon mid", the 02 look)

RIDGE_X0, RIDGE_W = 0.035, 0.93

from track import Track   # noqa: E402


def lin(hexs):
    h = hexs.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    return c ** 2.2


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


# The drawn "music": how strongly the light breathes through the minute (0 to 1)
BREATH = Track([(0, 0.30), (6, 0.28), (12, 0.20), (16, 0.26), (21, 0.42), (26, 0.52), (29, 0.50), (33, 0.34),
                (38, 0.40), (44, 0.58), (50, 0.66), (56, 0.60), (TOTAL, 0.55)])
# Soft piano notes drawn as rings on the lake: at the start and again at dawn; none in the deep winter
RING_SPANS = [(1.5, 11.0, 2.2), (44.0, 59.0, 1.8)]


class Song:
    def __init__(self):
        ft = np.arange(NFRAMES) / FPS
        self.ft = ft
        base = np.array([BREATH(t) for t in ft])
        wob = 0.045 * np.sin(ft * 0.9) + 0.03 * np.sin(ft * 0.37 + 1.3)
        self.env = np.clip(base + wob, 0.0, 1.0)
        self.env_slow = np.clip(base + 0.5 * wob, 0.0, 1.0)
        self.hi = np.clip(0.30 + 0.5 * (base - 0.3) + 0.06 * np.sin(ft * 1.7), 0.0, 1.0)
        keep, k = [], 0
        for a, b, step in RING_SPANS:
            t = a
            while t < b:
                r = np.random.default_rng(2000 + k).random(4)
                keep.append((float(t), 0.08 + 0.84 * r[0], HORIZON * (0.30 + 0.60 * r[1]), 0.55 + 0.45 * r[2]))
                t += step * (0.7 + 0.6 * r[3])
                k += 1
        self.rings = keep
        self.ring_t = np.array([x[0] for x in keep])
        pooled = np.zeros(NFRAMES)
        for (rt, _, _, s) in keep:
            pooled[min(int(rt * FPS), NFRAMES - 1)] = s
        self.pulse = _ar(pooled, 0.001, 0.35)
        # the mountain skyline: one long calm range, higher on the left, a soft saddle, a second rise on the right
        xs = np.linspace(0.0, 1.0, 2048)

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        prof = (0.95 * np.exp(-0.5 * ((xs - 0.27) / 0.13) ** 2) + 0.55 * np.exp(-0.5 * ((xs - 0.50) / 0.10) ** 2)
                + 0.80 * np.exp(-0.5 * ((xs - 0.74) / 0.12) ** 2) + 0.25 * np.exp(-0.5 * ((xs - 0.92) / 0.06) ** 2))
        prof = np.clip(prof, 0.0, 1.0)
        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 40 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 16), (0.25, 35), (0.125, 78), (0.0625, 170), (0.03, 380))))
        hgt = 0.014 + 0.046 * prof + (0.010 + 0.020 * prof) * (crag - 0.5)   # low and calm: the words stay on open sky
        sh = np.clip(np.minimum(xs, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.maximum(hgt * (0.5 + 0.5 * sh), 0.006).astype("f4")

    def lantern(self, t):
        # the lonely traveler's light, crossing the long road of the skyline through the minute; it stops short of
        # the rose's shore on the right
        x = RIDGE_X0 + 0.70 * min(max(t / MUSIC_END, 0.0), 1.0)
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


# ----------------------------------------------------------------- the minute (seconds into the promo)
ENC_FORM = 16.0        # Encouragement starts forming (fully formed about 19.75)
ENC_HOLD = 26.0        # the words begin to fly (6.25 seconds fully formed and solid)
ENC_ARRIVE = 28.6      # they reach star 7: a flare and one new thin ring
SEED_T = 31.0          # the seed of light gathers on the near shore under the thread of light
BUD_T = 40.5           # the seed grows into a bud
BLOOM_T = 43.0         # the bud opens into the rose
NINTH = 1e9            # the whole arch does not glow at the end of this song
TITLE_HIT = 51.0       # end card (title from 48, three lines fully formed about 54.2, held to the fade at 59.4)

# Nothing dark behind any text (direction round 4): no veil, no halo, no band. Legibility comes from the glow and
# a naturally deep sky where the words stand.
TEXT_SHADOW = 0.0
# and no light is cut out around the words either (snow and petals may pass behind them, as in the original)
TEXT_PROTECT = 0.0
# The engine still darkens bright sky behind text above a fixed level and always darkens a little round the corner
# credit. So the sky under every line is kept below that level (deep dawn, low sun), and the corner credit fades
# out before the end card.
# the traveler's light on the skyline dims under the end card so nothing bright sits just below its lines
SKYLINE_LANTERN = Track([(0, 1.0), (47.0, 1.0), (51.0, 0.3), (TOTAL, 0.3)])

# Sky palettes (top, middle, horizon, glow of the low sun)
PAL = {
    "dusk":   ("#0c1736", "#2c2c52", "#a07070", "#ffd8b0"),   # the last warm light of song 01's day
    "snow":   ("#060c1c", "#101c36", "#3a4c6e", "#cfe0ff"),   # silver-blue winter night
    "violet": ("#070818", "#141434", "#3e3a68", "#d9c8ff"),   # the aurora veil night
    "deep":   ("#020410", "#070e26", "#1a2848", "#a9c4ff"),   # the clearest, coldest hour
    "pearl":  ("#0b122c", "#20264c", "#5e5478", "#ffe6ee"),   # first pearl light
    "blush":  ("#0d1432", "#24284e", "#62485e", "#ffd6e0"),   # pale pink spring dawn, kept deep behind words
}
_pal_keys = [(0.0, "dusk"), (3.0, "dusk"), (10.0, "snow"), (14.0, "snow"), (19.0, "violet"), (28.0, "violet"),
             (32.0, "deep"), (39.0, "deep"), (44.0, "pearl"), (49.0, "blush"), (TOTAL, "blush")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.55), (4, 0.40), (10, 0.06), (14, 0.0), (38, 0.0), (44, 0.16), (50, 0.20), (TOTAL, 0.20)])
SUN_Y = Track([(0, 0.35), (10, 0.30), (14, 0.28), (38, 0.28), (50, 0.33), (TOTAL, 0.335)])
SUN_SIZE = Track([(0, 0.09), (TOTAL, 0.09)])
STARS = Track([(0, 0.25), (6, 0.70), (12, 0.80), (16, 0.85), (28, 0.80), (32, 1.0), (39, 1.0), (45, 0.45),
               (50, 0.22), (TOTAL, 0.18)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])            # the Milky Way is song 01's
CLOUDS = Track([(0, 0.30), (8, 0.45), (13, 0.40), (18, 0.15), (28, 0.10), (31, 0.0), (40, 0.0), (46, 0.30),
                (TOTAL, 0.30)])
AURORA = Track([(0, 0.0), (14, 0.0), (19, 0.17), (27, 0.19), (31, 0.08), (36, 0.04), (42, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])            # no rain in this song
MOTES = Track([(0, 0.05), (8, 0.12), (16, 0.14), (28, 0.12), (32, 0.18), (39, 0.18), (44, 0.10), (TOTAL, 0.08)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])        # lanterns belong to songs 03 and 07
PETALS = Track([(0, 0.0), (40.0, 0.0), (44.0, 0.20), (49.0, 0.24), (54.0, 0.16), (TOTAL, 0.14)])
TRAIL = Track([(0, 0.22), (14, 0.28), (30, 0.30), (44, 0.30), (49, 0.18), (TOTAL, 0.16)])
ZOOM = Track([(0, 0.95), (14, 0.93), (28, 0.905), (34, 0.880), (40, 0.875), (50, 0.915), (TOTAL, 0.925)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (59.4, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (43.0, 0.0), (50.0, 0.22), (TOTAL, 0.22)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

PETAL_COLORS = ("#f6b3c4", "#fff1f3")             # the rose's petals: blush and pearl
MOTE_COLORS = ("#f4f8ff", "#cfe0ff")              # frost glints, white and silver blue
MOTE_Y = (1.05, -0.05)                            # the glints fall slowly, like the finest snow
AURORA_WARM = ("#c9d8ff", "#dccaff")              # silver-violet veil
AURORA_COOL = ("#b8c8ff", "#d0c0ff")

# ----------------------------------------------------------------- effect layers
# Falling snow in depth: first flakes, the lonely night, a hush under the words, soft snow over the seed, then
# the snow turns into the rose's petals at dawn
SNOW = Track([(0, 0.0), (2.5, 0.0), (6.0, 0.25), (10.0, 0.50), (14.0, 0.50), (17.0, 0.16), (27.0, 0.14),
              (31.0, 0.26), (38.0, 0.26), (42.0, 0.06), (45.0, 0.0), (TOTAL, 0.0)])
SNOW_SPEED = Track([(0, 1.0), (14.0, 1.0), (17.0, 0.45), (TOTAL, 0.45)])
SNOW_WIND = Track([(0, 0.30), (10.0, 0.50), (14.0, 0.50), (17.0, 0.15), (TOTAL, 0.15)])
SNOW_COLOR = "#eef4ff"

STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# The word reaches down: a thin thread of light falls from star 7 to the near shore, where the seed gathers
ROSE_X, ROSE_FEET = 0.885, 0.285
BEAM = Track([(0, 0.0), (29.6, 0.0), (30.8, 0.42), (34.5, 0.36), (37.5, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (STAR_POS[6][0], STAR_POS[6][1] - 0.02)
BEAM_TO = (ROSE_X, ROSE_FEET + 0.03)
BEAM_WIDTH = (0.004, 0.022)
BEAM_COLOR = "#d6c2ff"

# ----------------------------------------------------------------- the rose of light (not a person)
# The song's own drawings (assets/song_figures/s02/rose_seed, rose_bud, rose_bloom: white line art made for this
# file) become sparks of light: the seed gathers under the thread of light, grows into a bud and opens into the
# rose, rising a little as it grows; at the very end it lets go and drifts up as light (song 03 takes the petal).
# It stands on the near right shore, under star 7 and clear of every line of text.
FIGURES = [
    dict(poses=["assets/song_figures/s02/rose_seed.png", "assets/song_figures/s02/rose_bud.png",
                "assets/song_figures/s02/rose_bloom.png"],
         t0=SEED_T, t1=58.0, gather=2.6, pose_times=[BUD_T, BLOOM_T], morph=2.2, dissolve=2.0, leave="drift",
         x=ROSE_X, y=Track([(0.0, ROSE_FEET), (BUD_T, ROSE_FEET), (47.0, ROSE_FEET + 0.02), (TOTAL, ROSE_FEET + 0.025)]),
         height=0.27, color="#ffc8d6", glow=0.75, glass=0.8, sparks=0.8, particles=7000),
]

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    # campaign order; full wording. Star history: song 01 lit 9 and 7; song 02 speaks Encouragement again.
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9, y=0.27)   # a little higher than the default 0.315: all three lines stay on open sky
# Short lyric fragments (a few words each). Never on screen with the expression or the end card.
FRAGMENTS = [
    dict(text="too lonely", t0=6.0, t1=9.8, out=12.4, dy=0.0, size=96, glow="#cfe0ff", style="reflection"),
    dict(text="the seed", t0=33.4, t1=36.4, out=39.0, dy=0.03, size=100, glow="#ffd9a0", style="write"),
    dict(text="becomes the rose", t0=42.6, t1=45.8, out=47.2, dy=0.02, size=104, style="petals",
         colors=("#f2a0b6", "#ffe0e8")),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.0, t1=TITLE_HIT + 3.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="The Rose", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=3.6, t_rest=5.4, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_out0=45.5, t_out1=47.8)


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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_out0"], c["t_out1"], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky (time, x, y, strength): star 7 shines again, and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.30), (TITLE_HIT, 0.5, 0.62, 0.8)]


# star_state and link_state come from engine/arch.py (song.py installs them when the engine loads this file)
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
        sun_int=SUN_INT(t) * (0.88 + 0.30 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=lx, rings=song.rings_at(t), waves=waves,
        star=star_state(t), link=link_state(t),  # noqa: F821 (installed by song.py)
    )
