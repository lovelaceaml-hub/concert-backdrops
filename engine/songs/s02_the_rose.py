"""Song 02, The Rose: 1 minute promo v2, visual only (no recording of the trio exists yet).

Design: project-docs/designs/02 The Rose.md ("The Seed Under the Snow"), DESIGN-SYSTEM.md section 6 (the 02 look:
deep winter night with snowfall, a pale pink spring dawn; silver blue, white, blush pink; close and quiet framing).
No painted plates for song 02 are in the repository, so every scene is built from the engine's own layers.

Five scenes, each with its own framing and dominant object:
  0 to 9    1 FIRST SNOW: song 01's morning darkens into a winter night over open water (wide), the first snow
            falls; fragment "too lonely" rises out of the water as a reflection
  9 to 27   2 THE FROZEN LAKE AND THE LONG NIGHT: ice spreads over the lake, frost creeps in from the corners,
            the blizzard thickens (closer). People of light act out Encouragement: one kneels exhausted, the
            other prays over them, then cheers them up, and both stand with joined hands raised. The full words
            form as she prays and fly into star 7 (it shines again: a flare and one new thin ring)
  27 to 39  3 THE SEED UNDER THE SNOW: the snow stops, the darkest and closest frame; a violet thread of light
            falls from star 7 to the seed glowing gold under the ice; fragment "the seed" is written in light
  39 to 50  4 THE THAW AND THE ROSE: the ice thaws in pools with blush glowing edges, a pearl and blush dawn,
            soft rays, rose petals fall; fragment "becomes the rose" settles in petals
  50 to 60  5 SPRING DAWN: open water again, rings of piano notes, the three-line end card
Signature effects: falling snow in depth (SNOW), the frozen lake and its thaw (ICE, ICE_FRAME), the violet
thread of the words reaching the seed (BEAM), the rose's petals (PETALS and the petals fragment).

There is no music, so this file does not read the recording's measurements: the gentle breathing of the light,
the skyline and the "piano note" rings on the water are drawn from the timeline below. The workflow's audio file
is a silent placeholder (visual only, no music yet).
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
FREEZE = 9.0           # the ice starts to spread over the lake
FIG_IN = 12.0          # the people of light gather (Encouragement acted out)
ENC_FORM = 15.6        # the words start forming as she prays (fully formed at about 19.35)
ENC_HOLD = 26.0        # the words begin to fly (6.65 seconds fully formed and solid)
ENC_ARRIVE = 28.5      # they reach star 7: a flare and one new thin ring
SEED = 29.0            # scene 3: the seed under the snow
THAW = 39.0            # scene 4: the thaw and the rose
SPRING = 50.0          # scene 5: spring dawn and the end card
NINTH = 1e9            # the whole arch does not glow at the end of this song
TITLE_HIT = 53.8       # end card
SKYLINE_LANTERN = 0.0  # no light along the drawn skyline (its glowing trail read as a crack in the sky)
TEXT_PROTECT = 1.0
TEXT_SHADOW = Track([(0, 1.1), (THAW, 1.1), (41.0, 1.9), (48.5, 1.9), (51.0, 1.6), (TOTAL, 1.6)])   # deeper calm behind words at dawn

# Scene palettes (top of sky, middle, horizon, glow of the low home star / seed / sun).
PAL = {
    "morning": ("#173a74", "#8c7282", "#ffc47c", "#ffeacc"),   # song 01's closing frame (agreed hand-off)
    "dusk":    ("#101a33", "#3c4566", "#8a8fae", "#d9c9d6"),
    "winter":  ("#0b1424", "#1d2c45", "#5a6f8f", "#cfe0ff"),
    "deep":    ("#05080f", "#0e1828", "#2e3e58", "#b9cbe8"),
    "violet":  ("#0a0c1e", "#22204a", "#4e4c7c", "#c7b0f0"),
    "seed":    ("#03050b", "#0a1020", "#1b2440", "#ffc98a"),   # the seed glows gold under the ice
    "pearl":   ("#131a30", "#3c4364", "#9a879f", "#f0dbe4"),
    "blush":   ("#212c4c", "#5f6488", "#d9a7b6", "#ffe1e8"),
    "blushpk": ("#26325a", "#6a6d94", "#e2b3c0", "#ffe9ee"),
}
_pal_keys = [
    (0.0, "morning"), (1.2, "morning"), (4.5, "dusk"), (8.0, "winter"), (13.0, "deep"), (17.0, "violet"),
    (25.0, "violet"), (29.0, "seed"), (37.0, "seed"), (41.0, "pearl"), (46.0, "blush"), (52.0, "blushpk"),
    (TOTAL, "blushpk"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the home star sinks to the shore in the cold, rests as the seed (small, gold, at the waterline), then rises
# as the dawn
SUN_INT = Track([(0, 0.90), (1.2, 0.85), (4.5, 0.35), (FREEZE, 0.12), (14, 0.05), (ENC_ARRIVE, 0.05),
                 (31.0, 0.35), (34.0, 0.55), (37.0, 0.50), (41.0, 0.32), (45.0, 0.42), (50, 0.55), (54, 0.45),
                 (TOTAL, 0.42)])
SUN_Y = Track([(0, 0.41), (1.2, 0.40), (6, 0.30), (12, 0.25), (27.0, 0.25), (30.0, 0.368), (37.0, 0.368),
               (42.0, 0.30), (47, 0.36), (53, 0.43), (TOTAL, 0.45)])
SUN_SIZE = Track([(0, 0.13), (6, 0.08), (12, 0.07), (27.0, 0.06), (31.0, 0.045), (37.0, 0.05), (42.0, 0.08),
                  (48, 0.11), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (3, 0.15), (8, 0.55), (14, 0.45), (27, 0.40), (31, 0.60), (38, 0.55), (43, 0.25),
               (48, 0.08), (TOTAL, 0.05)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])          # no Milky Way: that belongs to song 01
CLOUDS = Track([(0, 0.25), (8, 0.55), (14, 0.70), (26, 0.65), (30, 0.25), (37, 0.20), (42, 0.40), (TOTAL, 0.30)])
# the three voices: only a faint silver-violet veil while the Encouragement is acted
AURORA = Track([(0, 0.0), (FIG_IN, 0.0), (17.0, 0.12), (ENC_HOLD, 0.14), (29.0, 0.03), (31.0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])            # no rain in this song
MOTES = Track([(0, 0.05), (8, 0.06), (20, 0.08), (30, 0.10), (37, 0.08), (44, 0.16), (52, 0.20), (TOTAL, 0.18)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])        # lanterns belong to songs 03 and 07
# the rose's blush petals only at dawn (the snow is the SNOW layer now)
PETALS = Track([(0, 0.0), (40.0, 0.0), (43.0, 0.16), (47.0, 0.24), (52, 0.18), (TOTAL, 0.14)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])            # no skyline trail
# framing: wide over open water, closer in the long night, closest on the seed, opening wide again at dawn
ZOOM = Track([(0, 0.98), (8.0, 0.95), (14.0, 0.90), (26.0, 0.88), (30.0, 0.80), (37.0, 0.77), (43.0, 0.90),
              (50.0, 0.97), (TOTAL, 0.95)])
EXPOSURE = Track([(0, 1.0), (44.0, 1.0), (48, 0.92), (54, 0.84), (TOTAL, 0.84)])
FADE = Track([(0, 0.0), (1.0, 1.0), (58.8, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (41, 0.0), (44.0, 0.12), (48, 0.22), (51, 0.22), (54, 0.14), (TOTAL, 0.13)])
PART = Track([(0, 0.0), (43.0, 0.0), (47, 0.45), (52, 0.4), (56, 0.2), (TOTAL, 0.2)])

PETAL_COLORS = ("#f6b3c4", "#fff1f3")             # the rose's petals: blush and pearl
MOTE_COLORS = ("#f4f8ff", "#cfe0ff")              # frost glints, white and silver blue
MOTE_Y = (1.05, -0.05)                            # motes fall slowly, like the finest snow
AURORA_WARM = ("#c9d8ff", "#e4d8ff")              # the trio's faint veil: silver and pale violet, never gold
AURORA_COOL = ("#c9d8ff", "#e4d8ff")

# ----------------------------------------------------------------- signature effects
# Falling snow in depth: first flakes, the blizzard of the long night, a hover while the words speak, then gone
SNOW = Track([(0, 0.0), (4.0, 0.0), (7.0, 0.22), (11.0, 0.55), (14.0, 0.60), (16.0, 0.30), (25.0, 0.28),
              (28.0, 0.12), (30.5, 0.0), (TOTAL, 0.0)])
SNOW_SPEED = Track([(0, 1.0), (14.0, 1.1), (16.5, 0.35), (25.0, 0.35), (28.0, 0.7), (TOTAL, 0.7)])
SNOW_WIND = Track([(0, 0.30), (11.0, 0.55), (14.0, 0.55), (16.5, 0.12), (TOTAL, 0.12)])
SNOW_COLOR = "#eef4ff"
# The frozen lake: the ice spreads, holds through the night and the seed, then thaws in pools with blush edges
ICE = Track([(0, 0.0), (FREEZE, 0.0), (15.0, 1.0), (THAW, 1.0), (48.0, 0.0), (TOTAL, 0.0)])
ICE_LINE = HORIZON
ICE_OPACITY = 0.88
ICE_COLOR = "#d4e2ff"
# the ice's moving edge: frost white while it freezes, blush while it thaws (02's dawn is pearl and blush)
THAW_COLOR = Track([(0, lin("#e6efff")), (THAW, lin("#e6efff")), (40.5, lin("#ffc2cf")), (TOTAL, lin("#ffc2cf"))])
ICE_FRAME = Track([(0, 0.0), (10.0, 0.0), (15.0, 0.38), (27.0, 0.38), (33.0, 0.22), (THAW, 0.22), (44.0, 0.0),
                   (TOTAL, 0.0)])
# The word reaches down: a violet thread of light from star 7 to the seed under the ice
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))
BEAM = Track([(0, 0.0), (28.6, 0.0), (29.6, 0.48), (31.6, 0.45), (32.8, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (STAR_POS[6][0], STAR_POS[6][1])
BEAM_TO = (0.5, HORIZON + 0.008)
BEAM_WIDTH = (0.006, 0.035)
BEAM_COLOR = "#c9a8ff"

# ----------------------------------------------------------------- people of light
# Encouragement acted out (shared library): a: one kneels exhausted, the other prays over them; b: a hand on
# their back and the other raised in cheer, they begin to rise; c: both stand and lift their joined hands
FIGURES = [
    dict(poses=["assets/figures/encouragement_a.png", "assets/figures/encouragement_b.png",
                "assets/figures/encouragement_c.png"],
         t0=FIG_IN, t1=ENC_HOLD - 0.5, pose_times=[19.0, 22.6], x=0.5, y=0.20, height=0.40, to_star=6,
         color="#d9c6ff"),
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
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=96, y=0.30,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (a few words each; the song is copyrighted). Never on screen with the expression.
FRAGMENTS = [
    dict(text="too lonely", t0=5.8, t1=9.6, out=12.6, dy=0.03, size=84, glow="#cfe0ff", style="reflection"),
    dict(text="the seed", t0=32.6, t1=35.4, out=38.6, dy=0.0, size=88, glow="#ffc98a", style="write"),
    dict(text="becomes the rose", t0=41.4, t1=44.6, out=47.8, dy=0.02, size=100, style="petals",
         colors=("#e98aa3", "#ffd3dd")),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.2, t1=TITLE_HIT + 3.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="The Rose", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.3, t_move=3.6, t_rest=5.4, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky (time, x, y, strength): star 7 shines again, and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.45), (TITLE_HIT, 0.5, 0.62, 1.1)]


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
