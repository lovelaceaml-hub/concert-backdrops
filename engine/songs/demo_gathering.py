"""Gathering demo (2026-11-15, branch engine-gathering): a 40 second clip to judge the crowd and the passed light.
Not a promo. Original v4 look (the engine's own luminous world), a deep dusk throughout. No plates, no lyrics, no
faces, everyone clothed, nothing dark behind any text, calm lower third.

What it shows (seconds):
 1 to 14   about 64 small people of light walk in from both sides along the far shore (legs stride, arms swing,
           robes sway), slow down, turn toward the centre and settle beneath the arch, breathing, never frozen
 14 to 29  a small flame comes down from the middle of the arch into the hands of the person nearest the centre;
           from there it is passed from hand to hand through the crowd (each giver turns and reaches out, the
           flame hops across with a spark trail, the receiver reaches to take it and begins to glow)
 29 to 36  everyone lifts their light; the lights rise to the arch, the nine lights come on and the arch brightens
 35 to 40  the end card
Audio: audio/test/s03-newsong-first-60s.mp3 (only its first 40 seconds are used).
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
MUSIC_END = 43.8       # this demo uses the first 44 seconds of the song 03 test clip
SONG_END = 44.0
TOTAL = 44.0           # demo length
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

NINTH = 1e9
TITLE_HIT = 39.4      # end card
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0     # nothing dark behind any text (Anthony, round 4)

# a deep dusk, slowly warming at the horizon as the light spreads
SKY_TOP = Track([(0, lin("#040822")), (TOTAL, lin("#081034"))])
SKY_MID = Track([(0, lin("#131845")), (20.0, lin("#161b4c")), (TOTAL, lin("#22265a"))])
SKY_HOR = Track([(0, lin("#4e3666")), (20.0, lin("#5a3c6a")), (TOTAL, lin("#7a4c70"))])
GLOW = Track([(0, lin("#f6a882")), (TOTAL, lin("#ffbc8e"))])
SUN_INT = Track([(0, 0.16), (20.0, 0.18), (32.0, 0.26), (TOTAL, 0.28)])
SUN_Y = Track([(0, 0.330), (TOTAL, 0.336)])
SUN_SIZE = Track([(0, 0.08), (TOTAL, 0.09)])
STARS = Track([(0, 0.0), (0.3, 0.0), (2.0, 0.85), (TOTAL, 0.85)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.08), (TOTAL, 0.10)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.08), (14, 0.12), (30, 0.22), (TOTAL, 0.25)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.40), (TOTAL, 0.45)])
ZOOM = Track([(0, 1.0), (TOTAL, 0.97)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (TOTAL - 0.5, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
SKYLINE_LANTERN = Track([(0, 1.0), (10.0, 1.0), (12.0, 0.25), (TOTAL, 0.25)])

# The crowd and the passed light (engine/UPGRADE-HOWTO.md section K)
GATHERING = dict(t0=1.0, t1=1e9, count=64, center=(0.5, 0.343), spread=(0.40, 0.035), hole=0.04, rows=2,
                 height=(0.15, 0.10), speed=1.0, arrive_by=13.5, sides=("left", "right"),
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=13.5, speed=0.15, path="crowd", start="center", source="arch", color="#ffe2a0",
                  lift=True, rise=True, arch=1.0)

# Nine lights on an arch over the stage: dark at first, they come on as the risen lights reach them
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

ARCH_ON = 32.8
OFF = dict(form=1e9, hold=1e9, star=1e9)
_lab = [("Greeting", "“How are you?”"), ("Gratitude", "“Thank you.”"), ("Apology", "“I’m sorry.”"),
        ("Inclusiveness", "“It’s okay.”"), ("Concession", "“Please, after you.”"), ("Respect", "“Tell me more.”"),
        ("Encouragement", "“I’ll pray (or root) for you.”"), ("Consideration", "“Can I give you a hand?”"),
        ("Compliment", "“You’re amazing.”")]
_order = [4, 3, 5, 2, 6, 1, 7, 0, 8]            # from the middle outward
PHRASES = [dict(label=l, lines=[s], size=150, form=1e9, hold=1e9, star=ARCH_ON + 0.35 * _order.index(i))
           for i, (l, s) in enumerate(_lab)]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
# a short phrase written for this demo (not lyrics)
FRAGMENTS = [
    dict(text="peace, passed from hand to hand", t0=18.0, t1=23.5, out=25.5, dy=0.17, size=84, glow="#ffc48c"),
]
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.4, t1=TITLE_HIT + 1.6)
CREDIT = dict(song="Gathering (engine demo)", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.1, t_move=2.4, t_rest=3.8, scale=0.34, alpha_rest=0.58,
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


WAVES = [(TITLE_HIT, 0.5, 0.62, 0.8)]


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
        star=star_state(t), link=link_state(t),
    )
