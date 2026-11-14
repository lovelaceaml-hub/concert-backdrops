"""Song 11, Almighty God Who Knows the Future (the finale): the 1 minute promo, version 4 (original style).

Anthony, direction round 4: back to the engine's own luminous world of the first version (engine/songs/
s03_original.py): a deep sky with stars, a still lake with a mountain line and its mirror, aurora, motes and the arch
of nine lights; words of glowing gold light with nothing dark behind them (TEXT_SHADOW = 0); calm and magnificent;
and according to the song. Promo audio: audio/promo/s11.mp3 (1:59 to 2:59 of the studio recording).

No painted plates (the song 11 plates are near white and would need dark backing under the words) and no people.
Everything is built from the engine's own layers; the city is drawn in light by the figure layer from two line
drawings (assets/song_figures/s11/make_v4_shapes.py), and the nine glows on the water use the same layer.

Five scenes, each a different time of day, light and centre of attention:
1 the promise, 0 to 9 s: deep night, Milky Way, a faint silver outline of the city not yet built gathers on the
  mountain (the title card above it);
2 Mother's road, 9 to 24 s: violet before dawn, the first glow under the horizon lays a road of light across the
  lake to the city; at Mother's words to trust Father and march ahead, Encouragement forms in full and flies to its
  light;
3 all nations streaming in, 24 to 41 s: sunrise; the city fills with gold (the silver lines rise away as the gold
  city gathers, then its walls, windows and gate light up); lights in all nine colours rise from the lake into an
  aurora of all nine colours;
4 the sun through the gate, 41 to 48.5 s: the second lift; the sun rises into the open gate of the city with full
  rays, a flash of light, the whole arch glows; "Joy of salvation endures forever" is engraved high in the deep blue;
5 peace settled, from 48.5 s: deep warm starry night, the golden city glowing on the mountain, nine glows in the
  nine colours gather on the calm water beneath their lights; the three-line end card.
Signature moments: the city filling with gold (scenes 1 to 3), the nations streaming in (scene 3), the sun through
the gate (scene 4), the nine glows on the water (scene 5).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5       # last sounding moment of the promo clip
SONG_END = 60.0        # length of the promo clip
TOTAL = 60.0           # promo length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.35         # water line, high: grand framing with a wide lake (song 11 look)

RIDGE_X0, RIDGE_W = 0.035, 0.93
PLATEAU = 0.026        # height of the mountain top the city stands on (fraction of the screen above the water)


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
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain line: low distant ranges on both sides and a broad flat-topped mountain in the middle
        # (Mount Zion) with the city of light on it
        xs = np.linspace(0.0, 1.0, 2048)

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 20 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 9), (0.25, 22), (0.125, 50), (0.0625, 120), (0.03, 300))))
        side = 0.016 + 0.030 * crag * (0.6 + 0.4 * np.abs(xs - 0.5) / 0.5)
        dx = np.abs(xs - 0.5)
        top = np.clip((0.33 - dx) / 0.10, 0.0, 1.0)
        top = top * top * (3 - 2 * top)
        zion = PLATEAU + 0.0025 * (lattice(140, 9) - 0.5) * (dx > 0.22)
        self.ridge = np.maximum(side * (1 - top), zion * top + side * (1 - top) * 0.0)
        self.ridge = np.maximum(self.ridge, 0.006).astype("f4")
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


# ----------------------------------------------------------------- timeline

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402

# The promo is 1:59 to 2:59 of the studio recording (song second = promo second + 119.0). Lyric times are measured
# word times from a speech-to-text pass of the recording (2026-11-13), as in s11_finale.py.
CLIP_START = 119.0
MOTHER = 121.2 - CLIP_START      # verse 2 begins: Mother, who planned the future
MARCH = 129.9 - CLIP_START       # her words to trust Father and march ahead
HOPE = 141.3 - CLIP_START        # hope engraved in every heart, now fulfilled
KINGS = 150.6 - CLIP_START       # all kings worship and run to the Church of God
LIFT = 160.5 - CLIP_START        # the second lift (measured step up in loudness)
JOY = 162.1 - CLIP_START         # joy of salvation
FOREVER = 165.5 - CLIP_START     # endures forever
TITLE_HIT = 52.4                 # end card: title complete; the tagline is solid from 54.6 to the fade at 59.6
NINTH = LIFT                     # the whole arch glows from the second lift on: the finale's glory

# Reading-time contract: formation takes about 3.75 s, so hold >= form + 9.75.
ENC_FORM = MARCH + 0.6           # 11.5
ENC_HOLD = ENC_FORM + 9.9        # 21.4: fully formed and solid from about 15.25 to 21.4 (6.15 s)
ENC_ARRIVE = ENC_HOLD + 1.6      # 23.0: the words reach light 7 (flare and a fresh ring)
FRAG_T0, FRAG_T1, FRAG_OUT = LIFT, LIFT + 2.5, LIFT + 6.0
NIGHT = 48.5                     # scene 5 begins: the deep warm night of peace

SKYLINE_LANTERN = 0.0            # the city stands where the travelling skyline light would pass
BOTTOM_CALM = 1.0                # calm lower third
TEXT_SHADOW = 0.0                # direction round 4: nothing dark behind any text
# Rings each light carries into this minute (0 Greeting ... 8 Compliment): song 10's closing counts
# [1, 0, 1, 1, 0, 0, 5, 2, 1] plus one ring on light 2 Gratitude from this song's own relight at the thanks to
# Father (1:51), before the promo minute (1:59). Unchanged from s11_finale.py.
RINGS_AT_START = {0: 1, 1: 1, 2: 1, 3: 1, 6: 5, 7: 2, 8: 1}

# the nine expression colours (song 11 uses all nine)
NINE = ["#FF977C", "#FFD05F", "#FFAD69", "#F582AF", "#82B0ED", "#CE927E", "#B293E7", "#EF7A96", "#BE9CEB"]


def _nine_pair(rate, offset):
    def f(t):
        k = int(t * rate + offset) % 9
        return (NINE[k], NINE[(k + 4) % 9])
    return f


_nine_aur = _nine_pair(0.25, 0)


def AURORA_WARM(t):
    if t < 23.0:
        return ("#c9d2ff", "#b293e7")      # silver and violet before dawn
    if t < NIGHT:
        return _nine_aur(t)                # all nine colours as the nations stream in
    return ("#ffd27a", "#b293e7")          # gold and violet in the night of peace


# Sky palettes (top of sky, middle, horizon, glow of the sun). The middle stays deep where the words sit.
PAL = {
    "promise": ("#02040f", "#060c28", "#1a2350", "#b9c4ff"),
    "road":    ("#030720", "#131642", "#583d7a", "#ffb98f"),
    "rise":    ("#051844", "#123678", "#c98a5c", "#ffd9a0"),
    "glory":   ("#05194c", "#113b80", "#e8b676", "#fff0cf"),
    "rest":    ("#02040e", "#090f30", "#2c2142", "#ffc98a"),
}
_pal_keys = [(0.0, "promise"), (8.5, "promise"), (13.0, "road"), (23.5, "road"), (29.0, "rise"), (LIFT - 0.5, "rise"),
             (LIFT + 1.2, "glory"), (NIGHT - 1.0, "glory"), (NIGHT + 3.0, "rest"), (TOTAL, "rest")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the sun: under the horizon before dawn (its glow lays the road of light on the lake), up into the gate at the
# second lift, down again for the night
SUN_INT = Track([(0, 0.10), (8.5, 0.14), (13.0, 0.42), (23.5, 0.50), (29.0, 0.70), (LIFT - 0.5, 0.80),
                 (LIFT + 0.8, 1.25), (NIGHT - 1.0, 1.10), (NIGHT + 3.0, 0.16), (TOTAL, 0.14)])
SUN_Y = Track([(0, 0.30), (8.5, 0.31), (23.5, 0.335), (29.0, 0.350), (LIFT - 0.5, 0.362), (LIFT + 3.5, 0.392),
               (NIGHT - 1.0, 0.398), (NIGHT + 3.0, 0.32), (TOTAL, 0.32)])
SUN_SIZE = Track([(0, 0.09), (23.5, 0.095), (LIFT, 0.10), (TOTAL, 0.10)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 1.0), (9.0, 1.0), (14.0, 0.65), (23.5, 0.45), (29.0, 0.10),
               (NIGHT - 1.0, 0.05), (NIGHT + 3.0, 0.90), (TOTAL, 1.0)])
MILKY = Track([(0, 0.0), (4.0, 0.55), (9.0, 0.50), (16.0, 0.12), (24.0, 0.0), (NIGHT, 0.0), (NIGHT + 3.5, 0.5),
               (TOTAL, 0.55)])
CLOUDS = Track([(0, 0.06), (TOTAL, 0.06)])   # a clear sky
AURORA = Track([(0, 0.0), (3.0, 0.14), (9.0, 0.18), (11.0, 0.10), (21.5, 0.10), (24.5, 0.32), (29.0, 0.46),
                (LIFT - 1.0, 0.46), (LIFT + 1.0, 0.18), (NIGHT - 1.0, 0.12), (NIGHT + 3.0, 0.20), (TOTAL, 0.20)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])       # the city of light is drawn in screen space: the camera holds still
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
RAYS = Track([(0, 0.0), (24.0, 0.0), (29.0, 0.30), (LIFT - 0.5, 0.40), (LIFT + 1.0, 0.85), (NIGHT - 1.0, 0.75),
              (NIGHT + 2.5, 0.0), (TOTAL, 0.0)])
FLASH = Track([(0, 0.0), (LIFT - 0.3, 0.0), (LIFT + 0.25, 0.28), (LIFT + 2.2, 0.0), (TOTAL, 0.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 0.4, 1.0), (TOTAL - 0.02, 0.0)])
# white-gold motes in the air, quieter while words are on screen
MOTES = Track([(0, 0.20), (ENC_FORM, 0.20), (ENC_FORM + 2, 0.12), (ENC_ARRIVE, 0.12), (ENC_ARRIVE + 2, 0.40),
               (LIFT - 1, 0.55), (LIFT + 1, 0.25), (TITLE_HIT - 2, 0.25), (TOTAL, 0.22)])
MOTE_COLORS = ("#fff6e2", "#ffe2a0")
# the nations streaming in: lights in all nine colours rising from the lake
LANTERNS = Track([(0, 0.0), (24.5, 0.0), (28.5, 0.75), (KINGS, 0.90), (LIFT - 1.5, 0.90), (LIFT + 0.3, 0.10),
                  (LIFT + 2.0, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = _nine_pair(0.5, 2)

# The city of light on the mountain (white-on-black line drawings turned into light by the figure layer)
_F = "assets/song_figures/s11/"
CITY_H = 0.088                     # height of the drawing on screen (its aspect 8:1 makes it 0.40 of the width)
CITY_Y = HORIZON + PLATEAU - 0.003
FIGURES = [
    # 1 the promise: a faint silver outline gathers on the mountain; it rises away as sparks while the gold city
    # gathers in its place
    dict(poses=[_F + "s11v4_city_outline.png"], t0=1.2, t1=26.0, gather=5.0, dissolve=3.5, leave="drift",
         x=0.5, y=CITY_Y, height=CITY_H, color="#c4ccff", glow=0.55, glass=0.35, sparks=0.7, spark_size=0.8,
         particles=9000),
    # 3 the city filled with gold: the gold outline gathers, then walls, windows and the gate fill with light
    dict(poses=[_F + "s11v4_city_outline.png", _F + "s11v4_city_gold.png"], t0=24.5, t1=999.0, gather=4.0,
         pose_times=[30.5], morph=5.0, x=0.5, y=CITY_Y, height=CITY_H, color="#ffcf7a", glow=0.95, glass=1.0,
         sparks=0.9, spark_size=0.85, particles=16000),
]
# 5 nine glows on the calm water, one beneath each light of the arch, each in its expression's colour
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))
for i in range(9):
    FIGURES.append(dict(poses=[_F + "s11v4_glow.png"], t0=NIGHT + 1.0 + 0.22 * i, t1=999.0, gather=2.6,
                        x=STAR_POS[i][0], y=0.268, height=0.062, color=NINE[i], glow=0.9, glass=0.8, sparks=0.8,
                        spark_size=0.8, particles=700))

LIT = dict(form=1e9, hold=1e9, star=-100.0)     # lit in an earlier song (all nine are lit before the finale)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    # Encouragement shines again: Heavenly Mother tells her children to trust Father and march ahead
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=112, y=0.365,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)

# design fragment 3 in one piece, engraved in gold high in the deep blue above the sun in the gate
FRAGMENTS = [
    dict(text="Joy of salvation endures forever", t0=FRAG_T0, t1=FRAG_T1, out=FRAG_OUT, dy=0.175, size=100,
         glow="#ffcf7a", style="engrave"),
]

# the three-line end card
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.8, t1=TITLE_HIT + 2.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Almighty God Who Knows the Future", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=5.2, t_rest=7.0, scale=0.34, alpha_rest=0.58,
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(TITLE_HIT - 3.0, TITLE_HIT - 1.5, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light across the sky: Encouragement reaching its light again, the whole arch answering the second lift,
# and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.7),
         (LIFT, 0.5, 0.86, 0.9),
         (TITLE_HIT, 0.5, 0.62, 1.1)]


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    if t > MUSIC_END - 1.0:
        # after the music the scene keeps breathing gently on its own
        k = min((t - (MUSIC_END - 1.0)) / 3.0, 1.0)
        breath = 0.42 + 0.08 * np.sin(t * 0.55) + 0.05 * np.sin(t * 0.23 + 1.0)
        env = env * (1 - k) + breath * k
        envs = envs * (1 - k) + breath * k
        hi = hi * (1 - k) + (0.35 + 0.1 * np.sin(t * 0.8)) * k
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
        star=star_state(t), link=link_state(t),
    )
