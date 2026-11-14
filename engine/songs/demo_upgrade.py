"""Engine upgrade demo (60 seconds, to the song 04 promo clip): shows every new feature working together.

Not a concert video. It shows the eleven song sessions what the upgrade can do (engine/UPGRADE-HOWTO.md):
three painted scenes that crossfade (dissolve, bloom, ripple) with slow zoom and pan and a shimmering lake;
two pairs of people of light acting out Apology and Inclusiveness with their full campaign words, then rising
into their lights; snow, ice that thaws, a sky that breaks into glass and is mended with gold, a beam of light,
a golden field and a net of light; lyric fragments in the reflection and engrave styles.
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
HORIZON = 0.40         # water line, high: more of the (frozen) lake shows

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

class Track:
    def __init__(self, keys):
        self.t = np.array([k[0] for k in keys], dtype=np.float64)
        self.v = np.array([np.atleast_1d(np.asarray(k[1], dtype=np.float64)) for k in keys])

    def __call__(self, t):
        if t <= self.t[0]:
            v = self.v[0]
        elif t >= self.t[-1]:
            v = self.v[-1]
        else:
            i = int(np.searchsorted(self.t, t, side="right")) - 1
            u = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
            u = u * u * (3 - 2 * u)
            v = self.v[i] * (1 - u) + self.v[i + 1] * u
        return float(v[0]) if v.shape[0] == 1 else v



# ----------------------------------------------------------------- the demo minute
# The clip is the song 04 promo (voice from about 5 s, first chorus at 49 s).
NINTH = 1e9
TITLE_HIT = 51.0
SKYLINE_LANTERN = 0.0     # the plates have their own mountains, so the light along the drawn skyline is hidden

# Procedural sky and lake: only seen for a moment before the first plate (and anywhere no plate is shown)
PAL = {
    "frost": ("#22385c", "#5f7da6", "#b9cbe0", "#eef4ff"),
    "warm":  ("#4a6c9c", "#d2aea8", "#ffc994", "#ffe2b4"),
}
_pal_keys = [(0.0, "frost"), (28.0, "frost"), (44.0, "warm"), (TOTAL, "warm")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.30), (28, 0.36), (44, 0.95), (TOTAL, 1.05)])
SUN_Y = Track([(0, 0.40), (TOTAL, 0.47)])
SUN_SIZE = Track([(0, 0.14), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.4), (TOTAL, 0.3)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (26, 0.16), (36, 0.26), (48, 0.40), (TOTAL, 0.34)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.2, 1.0), (TOTAL - 2.6, 1.0), (TOTAL - 0.2, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])


def MOTE_COLORS(t):
    return ("#eef6ff", "#b9d2f2") if t < 34.0 else ("#ffe4bf", "#ffb98c")


# A. three painted scenes (assets/plates/demo/), each moving slowly; the lake in each one shimmers
SCENES = [
    dict(image="assets/plates/demo/winter_lake.jpg", t0=0.0, t1=28.0, fade_in=1.0, fade_out=3.5,
         zoom=(1.12, 1.04), pan=((0.0, 0.02), (0.0, 0.0)), water=True, water_line=0.36),
    dict(image="assets/plates/demo/thaw_dawn.jpg", t0=24.5, t1=49.0, fade_in=3.5, fade_out=3.0,
         transition="dissolve", zoom=(1.04, 1.13), pan=((0.0, 0.0), (0.0, 0.015)), water=True, water_line=0.36),
    dict(image="assets/plates/demo/golden_morning.jpg", t0=46.0, t1=61.0, fade_in=3.0, fade_out=0.0,
         transition="ripple", ripple_from=(0.5, 0.30), zoom=(1.12, 1.05), water=True, water_line=0.36),
]

# B. two pairs of people of light (the shared figure library in assets/figures/)
FIGURES = [
    dict(poses=["assets/figures/apology_a.png", "assets/figures/apology_b.png", "assets/figures/apology_c.png"],
         t0=4.0, t1=19.0, pose_times=[8.5, 13.0], x=0.5, y=0.24, height=0.33, to_star=2, color="#ffc78f"),
    dict(poses=["assets/figures/inclusiveness_a.png", "assets/figures/inclusiveness_b.png",
                "assets/figures/inclusiveness_c.png"],
         t0=31.0, t1=45.0, pose_times=[35.0, 39.0], x=0.5, y=0.24, height=0.33, to_star=3, color="#ffb7cf"),
]

# C. effect layers
SNOW = Track([(0, 0.55), (20, 0.6), (27, 0.2), (30, 0.0)])
SNOW_WIND = 0.4
ICE = Track([(0, 1.0), (28, 1.0), (44, 0.0)])          # the lake is frozen, then thaws with glowing edges
ICE_LINE = 0.30
ICE_FRAME = Track([(0, 0.55), (24, 0.55), (32, 0.0)])  # frost in the corners of the frame
SHARDS = Track([(0, 0.0), (17.5, 0.0), (20.5, 1.0), (26.0, 1.0), (31.0, 0.0)])
SHARDS_MEND = Track([(0, 0.0), (28.0, 0.0), (31.0, 1.0), (40.0, 0.8), (45.0, 0.0)])
SHARDS_Y = 0.52
BEAM = Track([(0, 0.0), (31.0, 0.0), (34.0, 0.85), (44.0, 0.85), (48.0, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.26)
BEAM_WIDTH = (0.018, 0.10)
GOLDEN_FIELD = Track([(0, 0.0), (47.0, 0.0), (51.0, 0.8), (TOTAL, 0.8)])
FIELD_LINE = 0.22
NET = Track([(0, 0.0), (49.0, 0.0), (57.0, 1.0), (TOTAL, 1.0)])
NET_ORIGIN = (0.5, 0.86)
NET_Y0 = 0.50
NET_BRIGHT = Track([(0, 0.0), (49.0, 0.7), (TOTAL, 0.7)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=96, y=0.30,
         form=11.5, hold=19.5, star=22.0),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=112, y=0.29,
         form=38.5, hold=45.5, star=48.0),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)

# D. lyric fragments in two of the new styles (and the classic one)
FRAGMENTS = [
    dict(text="the pain you held inside", t0=22.5, t1=26.5, out=30.0, dy=0.0, size=88, glow="#bcd6ff",
         style="reflection"),
    dict(text="truly humbled", t0=31.0, t1=33.8, out=37.2, dy=0.02, size=96, style="engrave"),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=53.0, t1=56.0)

CREDIT = dict(song="Engine Upgrade Demo", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.3, t_move=3.4, t_rest=5.4, scale=0.34, alpha_rest=0.58,
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


WAVES = [(PHRASES[2]["star"], STAR_POS[2][0], STAR_POS[2][1], 0.9),
         (PHRASES[3]["star"], STAR_POS[3][0], STAR_POS[3][1], 1.0),
         (TITLE_HIT, 0.5, 0.62, 1.2)]


def params(song, t):
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    if t > MUSIC_END - 1.0:
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
