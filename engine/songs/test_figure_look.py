"""Figure look test (2026-11-15, branch engine-figure-look): a 20 second close-up clip to judge the silk look of the
people of light (engine/figure_look.py, UPGRADE-HOWTO section H5). Not a promo. The engine's own luminous world,
from a deep night through dawn into the bright campaign day, so the look can be judged on all three skies and at
three sizes (large: half the screen height; medium: a fifth; crowd: a tenth). No plates, no lyrics, no faces,
everyone clothed, Heavenly Mother only from behind, nothing dark behind any text, calm lower third.

What it shows (seconds):
 0 to 7    night: a walker crosses, large, on the edge of the lake (robe, sleeves and streamlines trail behind
           her; she stops, turns a little and opens her arms low); a second, medium person walks in from the
           right; a crowd of 24 walks in on the far shore
 7 to 13   dawn: the walker's light rises to the arch; Heavenly Mother, from behind, large, her long veil flowing,
           opens her arms low and lifts them a little in blessing; a flame comes down from the arch and passes
           through the crowd from hand to hand
 13 to 20  bright day: Mother stays into the day; the crowd lifts its lights and they rise to the arch; two hands
           open and offer a light
Audio: audio/test/silent-60s.mp3 (only its first 20 seconds are used).
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
MUSIC_END = 19.8       # a silent clip: the look is judged, not the music
SONG_END = 20.0
TOTAL = 20.0           # test length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.34         # water line: the people of light stand on the far shore, just above the calm lower third

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
        self.hi = _ar(np.interp(ft, t, np.clip((hi - lo_) / max(hi_ - lo_, 1e-6), 0, 1), right=0.0), 0.04, 0.35)
        on = np.clip(d["onset"] / np.percentile(d["onset"], 99), 0.0, 1.4)
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain skyline is the loudness of the clip
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
        inside = (st >= 0) & (st <= MUSIC_END)
        hgt = 0.020 + 0.120 * v + 0.060 * mid * (0.35 + v) + (0.012 + 0.030 * v) * (crag - 0.5)
        edge = 0.018 + 0.012 * (crag - 0.5)
        sh = np.clip(np.minimum(xs - 0.0, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.where(inside, hgt, edge) * (0.5 + 0.5 * sh)
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

from track import Track   # noqa: E402
import theme   # noqa: E402

NINTH = 1e9
TITLE_HIT = 1e9       # no end card in this test
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0     # nothing dark behind any text

# Sky: a deep night, then dawn in peach and sky blue, then the bright cream and sky-blue campaign day
PAL = {
    "night": ("#040819", "#0e1542", "#3a3468", "#ffc0a0"),
    "dawn": ("#1d3f7c", "#6b94c9", "#f2c4a6", "#ffdcb4"),
    "day":  ("#4f9bd8", "#9ccbee", "#fcecd6", "#fff2dc"),
}
_pal_keys = [(0.0, "night"), (6.2, "night"), (8.6, "dawn"), (12.4, "dawn"), (14.8, "day"), (TOTAL, "day")]
SKY_TOP, SKY_MID, SKY_HOR, GLOW = (Track([(t, lin(PAL[p][k])) for t, p in _pal_keys]) for k in range(4))
SKY_THEME = Track([(0, 0.0), (12.4, 0.0), (15.0, 1.0), (TOTAL, 1.0)])   # the pale hills of the campaign day
SUN_INT = Track([(0, 0.10), (6.2, 0.14), (8.6, 0.45), (12.4, 0.48), (15.0, 0.50), (TOTAL, 0.50)])
SUN_Y = Track([(0, 0.300), (6.2, 0.320), (8.6, 0.360), (12.4, 0.385), (15.0, 0.42), (TOTAL, 0.43)])
SUN_SIZE = Track([(0, 0.09), (8.6, 0.11), (15.0, 0.13), (TOTAL, 0.13)])
STARS = Track([(0, 0.0), (0.3, 0.0), (1.5, 0.95), (6.2, 0.9), (8.6, 0.25), (12.4, 0.06), (TOTAL, 0.0)])
MILKY = Track([(0, 0.25), (6.2, 0.25), (8.6, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.08), (6.2, 0.10), (8.6, 0.28), (15.0, 0.36), (TOTAL, 0.36)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.08), (3, 0.14), (TOTAL, 0.14)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.4, 1.0), (TOTAL - 0.4, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (8.0, 0.0), (10.0, 0.10), (TOTAL, 0.12)])
PART = Track([(0, 0.0), (8.6, 0.0), (12.0, 0.4), (TOTAL, 0.5)])
SKYLINE_LANTERN = 0.0
WIND = Track([(0, 0.30), (8.0, 0.36), (11.0, 0.50), (14.0, 0.34), (TOTAL, 0.34)])   # a gust passes at 11 s

# ---- the silk look (UPGRADE-HOWTO section H5): every rigged figure and the crowd
FIGURE_LOOK = "silk"
FIGURE_SILK = dict(light_from="sun")

WALK = (1.0, 6.2)
FIGURES = [
    # 1. large: a walker crosses on the edge of the lake, stops, turns a little toward us and opens her arms low
    dict(kind="rig", preset="person", t0=0.2, t1=7.4, gather=1.0, dissolve=2.2, x=(0.07, 0.44), move=WALK,
         ease="linear", y=0.333, height=0.50, facing="right",
         actions=[(0.2, "stand"), (WALK[0] - 0.2, "walk"), (WALK[1], "stand"), (6.3, "turn", {"yaw": 0.85}),
                  (6.4, "open")],
         color="#ffcf9a", to_star=2),
    # 2. medium: a second person walks in from the right and stays through the dawn and the day
    dict(kind="rig", preset="person", veil=True, t0=0.8, t1=19.2, gather=1.2, dissolve=1.0, x=(0.66, 0.525),
         move=(1.2, 5.4), y=0.345, height=0.20, facing="left", leave="drift",
         actions=[(0.8, "stand"), (1.1, "walk"), (5.4, "stand"), (9.0, "pray", {"blend": 2.0}),
                  (13.0, "stand", {"blend": 2.0}), (15.5, "open", {"blend": 2.2})],
         color="#ffd9b8"),
    # 3. large: Heavenly Mother, only from behind; her long veil flows; her arms open low, then lift in blessing
    dict(kind="rig", preset="person_back", t0=7.0, t1=17.0, gather=1.6, dissolve=2.2, x=0.20, y=0.333,
         height=0.50, actions=[(7.0, "stand"), (8.6, "open", {"blend": 2.2}), (11.2, "bless", {"blend": 2.4}),
                               (14.6, "open", {"blend": 2.6})],
         color="#ffe0c0", to_star=1),
    # 4. two hands cup, open with moving fingers and offer a light, on the bright day sky
    dict(kind="rig", preset="hands", t0=14.0, t1=19.3, gather=1.2, dissolve=0.9, x=0.40, y=0.40, height=0.40,
         actions=[(14.0, "cup"), (15.2, "open", {"blend": 1.2}), (16.6, "offer", {"blend": 1.2}),
                  (18.2, "release", {"blend": 0.9})],
         color="#ffc98a", leave="drift"),
]

# ---- crowd size: 24 people gather on the far shore and pass the light (UPGRADE-HOWTO K)
GATHERING = dict(t0=0.6, count=24, center=(0.775, 0.345), spread=(0.185, 0.030), rows=2, height=(0.105, 0.16),
                 speed=1.15, arrive_by=6.2, sides="right",
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=7.4, speed=0.30, hold=0.15, path="crowd", start="center", source="arch", descent=1.5,
                  color="#ffe2a0", lift=14.4, rise=True, arch=1.0, lift_spread=0.8, rise_delay=1.6)

# Nine lights on an arch over the stage
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
_lab = ["Greeting", "Gratitude", "Apology", "Inclusiveness", "Concession", "Respect", "Encouragement",
        "Consideration", "Compliment"]
PHRASES = [dict(label=n, lines=["“How are you?”"], size=150, **OFF) for n in _lab]
PHRASES[1]["star"] = 17.6    # Mother's light arrives
PHRASES[2]["star"] = 9.4     # the walker's light arrives
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=1e9, hold=1e9, star=1e9)
FRAGMENTS = []
TAGLINE = dict(text="Figure look test", t0=1e9, t1=1e9 + 1.0)
CREDIT = dict(song="Figure look (engine test)", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=0.6, t_move=0.7, t_rest=1.6, scale=0.34, alpha_rest=0.58,
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


WAVES = []


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    lx, ly = song.lantern(t)
    z = ZOOM(t)
    lsx, lsy = (lx - 0.5) / z + 0.5, (ly - HORIZON) / z + HORIZON
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=lx, rings=song.rings_at(t), waves=[],
        star=star_state(t), link=link_state(t),
    )
