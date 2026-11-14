"""Song 02, The Rose: 1 minute promo v2, visual only (no recording of the trio exists yet).

Design: project-docs/designs/02 The Rose.md ("The Seed Under the Snow"), DESIGN-SYSTEM.md section 6 (the 02 look:
deep winter night with snowfall, a pale pink spring dawn; silver blue, white, blush pink; close and quiet framing).
Painted plates from Assets/s02 (assets/plates/s02/) and the song's own people of light (assets/song_figures/s02/).

Four scenes, each with its own camera and main object:
  0 to 13   1 FIRST SNOW: a wide night lake, the home star low between the mountains, snow begins and thickens
            as the camera slowly closes in; fragment "too lonely"
  10.5 to 30 2 THE CANDLE FIELD: violet light pours onto the snowbound lake and small lights glow all over it;
            for about 5 seconds the women of light relight the kneeling traveler's lantern and the traveler
            rises with them, and they all go up as light; then the full Encouragement words form over the
            violet light and fly into star 7
  27.5 to 42 3 THE SEED UNDER THE SNOW: a high ceiling of snow and ice, the dark soil, the seed with gold roots;
            a violet thread of light falls to it; fragment "the seed" is written in light
  39.7 to 60 4 THE ROSE: a low close shot on the near shore, the rose of light at dawn; petals fall;
            fragment "becomes the rose" settles in petals; the three-line end card on the same close shore
Signature effects: falling snow in depth (SNOW), the seed under the snow (plate and BEAM), the rose and its
petals (plates, PETALS, the petals fragment). The freeze and thaw belong to song 04, so this file uses no ICE.

There is no music, so this file does not read the recording's measurements. The workflow's audio file is a
silent placeholder (visual only, no music yet).
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
HORIZON = 0.36         # water line, as a fraction of the height from the bottom ("horizon mid", the 02 look)

RIDGE_X0, RIDGE_W = 0.035, 0.93

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402


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
BREATH = Track([(0, 0.30), (6, 0.28), (12, 0.18), (16, 0.22), (21, 0.40), (26, 0.52), (29, 0.50), (33, 0.34),
                (38, 0.40), (44, 0.58), (50, 0.70), (56, 0.62), (TOTAL, 0.55)])
# Piano notes drawn as rings on the water: on the open lake at the start and again after the thaw; none while
# the lake is frozen (the design's winter)
RING_SPANS = [(1.5, 8.5, 2.1), (47.0, 59.0, 1.5)]


class Song:
    def __init__(self):
        ft = np.arange(NFRAMES) / FPS
        self.ft = ft
        base = np.array([BREATH(t) for t in ft])
        wob = 0.045 * np.sin(ft * 0.9) + 0.03 * np.sin(ft * 0.37 + 1.3)
        self.env = np.clip(base + wob, 0.0, 1.0)
        self.env_slow = np.clip(base + 0.5 * wob, 0.0, 1.0)
        self.hi = np.clip(0.30 + 0.5 * (base - 0.3) + 0.06 * np.sin(ft * 1.7), 0.0, 1.0)
        # rings: soft piano notes at an unhurried pace, placed by a hash of their index
        keep, k = [], 0
        for a, b, step in RING_SPANS:
            t = a
            while t < b:
                r = np.random.default_rng(2000 + k).random(4)
                keep.append((float(t), 0.08 + 0.84 * r[0], HORIZON * (0.14 + 0.66 * r[1] ** 1.3), 0.55 + 0.45 * r[2]))
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
        hgt = 0.022 + 0.135 * prof + (0.012 + 0.030 * prof) * (crag - 0.5)
        sh = np.clip(np.minimum(xs, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.maximum(hgt * (0.5 + 0.5 * sh), 0.006).astype("f4")

    def lantern(self, t):
        # the lonely traveler's lantern, crossing the long road of the skyline through the minute
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


# ----------------------------------------------------------------- the minute (seconds into the promo)
RING_SPANS = []        # no drawn piano rings: every scene is a painted plate with its own water
FIG_IN = 11.0          # one brief appearance: the trio and the traveler, about 5 seconds, always moving
ENC_FORM = 16.4        # the words start forming once the people have gone up as light (fully formed about 20.15)
ENC_HOLD = 26.3        # the words begin to fly (6.15 seconds fully formed and solid)
ENC_ARRIVE = 28.8      # they reach star 7: a flare and one new thin ring
NINTH = 1e9            # the whole arch does not glow at the end of this song
TITLE_HIT = 52.6       # end card
SKYLINE_LANTERN = 0.0  # all plates: no light along the drawn skyline
TEXT_PROTECT = 1.0
TEXT_SHADOW = Track([(0, 1.2), (39.5, 1.2), (41.0, 1.9), (TOTAL, 1.9)])   # deeper calm behind words on bright dawn

# Procedural sky and lake: only a fallback behind the plates (never seen on its own)
PAL = {
    "night": ("#0b1424", "#1d2c45", "#5a6f8f", "#cfe0ff"),
    "blush": ("#212c4c", "#5f6488", "#d9a7b6", "#ffe1e8"),
}
_pal_keys = [(0.0, "night"), (38.0, "night"), (44.0, "blush"), (TOTAL, "blush")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.0), (TOTAL, 0.0)])
SUN_Y = Track([(0, 0.30), (TOTAL, 0.30)])
SUN_SIZE = Track([(0, 0.08), (TOTAL, 0.08)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])            # no rain in this song
MOTES = Track([(0, 0.04), (20, 0.06), (27.0, 0.06), (29.0, 0.0), (38.0, 0.0), (44, 0.12), (52, 0.16), (TOTAL, 0.14)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])        # lanterns belong to songs 03 and 07
# the rose's blush petals only at dawn
PETALS = Track([(0, 0.0), (40.0, 0.0), (43.0, 0.12), (47.0, 0.18), (52, 0.14), (TOTAL, 0.12)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (59.4, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

PETAL_COLORS = ("#f6b3c4", "#fff1f3")             # the rose's petals: blush and pearl
MOTE_COLORS = ("#f4f8ff", "#cfe0ff")              # frost glints, white and silver blue
MOTE_Y = (1.05, -0.05)                            # motes fall slowly, like the finest snow
AURORA_WARM = ("#c9d8ff", "#e4d8ff")
AURORA_COOL = ("#c9d8ff", "#e4d8ff")

# ----------------------------------------------------------------- scenes (painted plates, assets/plates/s02/)
# Each scene has its own camera and main object:
#   1 wide night lake, first snow, the home star low between the mountains; the camera slowly closes in
#     as the night deepens (0 to 13)
#   2 the violet light on the ice and the field of candle lights: the trio passes briefly as light (10.5 to 30)
#   3 under the snow: high ice ceiling, the seed and its gold roots in the soil (27.5 to 42)
#   4 low close shot on the near shore: the rose of light, then the end card beside it (39.7 to 60)
# The plates were touched up for song 02 (plates_fix notes in project-docs/status/02.md): the top left star
# band of a_first_snow dimmed, the light column and pool of c_violet_ice darkened behind the people and the
# candles at its bottom edge calmed, the ice ceiling of d_seed darkened near the arch, the ice floes of
# e_thaw_rose painted out and its sky near the arch calmed.
P = "assets/plates/s02/"
SCENES = [
    dict(image=P + "a_first_snow.jpg", t0=0.0, t1=13.0, fade_in=1.0, fade_out=2.5,
         zoom=(1.0, 1.10), pan=((0.0, 0.0), (0.0, 0.015)), water=True, water_line=0.36,
         gain=Track([(0, 1.0), (9.0, 1.0), (14.0, 0.85), (TOTAL, 0.85)])),
    dict(image=P + "c_violet_ice.jpg", t0=10.5, t1=30.0, fade_in=2.5, fade_out=2.5, transition="fade",
         zoom=(1.10, 1.14), pan=((0.0, 0.04), (0.0, 0.05)),     # framed up: fewer candles at the bottom edge
         gain=Track([(0, 0.72), (27.0, 0.72), (30.0, 0.85)])),
    dict(image=P + "d_seed.jpg", t0=27.5, t1=42.2, fade_in=2.5, fade_out=2.5, transition="fade",
         zoom=(1.02, 1.12), pan=((0.0, 0.0), (0.0, 0.01)),
         gain=Track([(0, 1.0), (30.5, 1.0), (32.0, 0.82), (TOTAL, 0.82)])),
    # the rose shore holds to the end: the end card stands on the close dawn shore beside the rose
    dict(image=P + "e_thaw_rose.jpg", t0=39.7, t1=61.0, fade_in=2.5, fade_out=0.0, transition="fade",
         zoom=(1.10, 1.17), pan=((-0.05, 0.045), (-0.05, 0.045)),
         gain=Track([(0, 0.85), (41.0, 0.85), (42.0, 0.78), (47.0, 0.78), (49.0, 0.86), (51.0, 0.68),
                     (TOTAL, 0.68)])),
]

# ----------------------------------------------------------------- effect layers
# Falling snow in depth: first flakes, the lonely night, a hover while the words speak, then gone under the snow
SNOW = Track([(0, 0.0), (2.0, 0.0), (5.0, 0.22), (10.0, 0.45), (14.0, 0.45), (16.0, 0.20), (25.0, 0.18),
              (27.5, 0.0), (TOTAL, 0.0)])
SNOW_SPEED = Track([(0, 1.0), (14.0, 1.0), (16.5, 0.35), (TOTAL, 0.35)])
SNOW_WIND = Track([(0, 0.30), (10.0, 0.50), (14.0, 0.50), (16.5, 0.12), (TOTAL, 0.12)])
SNOW_COLOR = "#eef4ff"
# The word reaches down: a violet thread of light falls through the ice to the seed
BEAM = Track([(0, 0.0), (28.9, 0.0), (29.6, 0.40), (30.8, 0.36), (31.6, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.52)
BEAM_WIDTH = (0.006, 0.03)
BEAM_COLOR = "#c9a8ff"

STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# ----------------------------------------------------------------- people of light
# Anthony's round 3 direction: people are rare and always moving, never posing under the words.
# One brief appearance of song 02's own figures (assets/song_figures/s02/, outline art from Assets/s02/figures):
# out of the light the women gather round the kneeling traveler and relight the lantern (pose 2), the traveler
# rises with them (pose 3), and at once they all go up as light. About 5 seconds, in motion the whole time,
# gone before the Encouragement words form; the words, the violet light and the star carry the expression.
SF = "assets/song_figures/s02/"
FIGURES = [
    dict(poses=[SF + "trio_2_encourage.png", SF + "trio_3_rise.png"],
         t0=FIG_IN, t1=13.9, gather=2.0, pose_times=[12.6], morph=1.3, dissolve=2.2, leave="drift",
         x=0.40, y=0.34, height=0.32, color="#ffd9a8", glow=0.9),   # pale gold, beside the violet column
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
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=90,
         y=0.235, form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (a few words each; the song is copyrighted). Never on screen with the expression.
FRAGMENTS = [
    dict(text="too lonely", t0=4.6, t1=6.6, out=9.6, dy=0.03, size=84, glow="#cfe0ff"),
    dict(text="the seed", t0=31.0, t1=33.6, out=36.6, dy=0.13, size=88, glow="#ffc98a", style="write"),
    dict(text="becomes the rose", t0=41.2, t1=44.0, out=47.0, dy=0.02, size=100, style="petals",
         colors=("#e98aa3", "#ffd3dd")),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.2, t1=TITLE_HIT + 3.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="The Rose", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.3, t_move=3.0, t_rest=4.6, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky (time, x, y, strength): a small one when star 7 shines again, and the
# end card (before the tagline forms)
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.16), (TITLE_HIT, 0.5, 0.62, 0.8)]


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
