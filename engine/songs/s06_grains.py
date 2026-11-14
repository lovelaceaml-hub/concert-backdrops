"""Song 06, Heavenly Mother Tells Us to Be Grains: the 1 minute promo (design "The Field That Grew From One Grain").
Timed to audio/promo/s06.mp3, which is 62.0 to 122.0 s of the 2:06 guide recording (end of verse 1 through the end
of the song). Concession is lit for the first time and Inclusiveness shines again.

Song features and the visual timeline for the backdrop.

Everything the renderer needs is a pure function of time, so any frame can be
rendered on its own (which lets several workers render in parallel).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.path.splitext(os.path.basename(__file__))[0]
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5       # last sounding moment of the promo clip
SONG_END = 60.0        # length of the promo clip
TOTAL = 60.0           # promo length
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


# Musical landmarks in the promo clip (seconds; clip time = guide recording time - 62.0)
PEAK_V1 = 2.0          # loudest point of verse 1 (guide 63.5 to 64.5)
INTERLUDE = 3.0        # softer gap between the verses (guide 65 to 70.5)
VERSE2 = 8.5           # verse 2, the grains line (guide 70.5)
HUSH = 16.0            # quietest, most tender stretch (guide 78 to 85.5)
WATER = 27.0           # living water (guide 89)
FRAGRANCE = 35.0       # fragrance (guide 97)
REFRAIN = 40.5         # final refrain (guide 102.5)
PEAK_END = 57.0        # loudest point of the song (guide 119 to 120.5)
NINTH = 1e9            # the whole arch does not glow as one in this song
TITLE_HIT = 50.0

# Scene palettes (top of sky, middle, horizon, glow of the horizon star)
PAL = {
    "dawn1":     ("#0f1b46", "#553b7c", "#e9a06f", "#ffd08c"),
    "dusk":      ("#050820", "#2a2a55", "#5e4a78", "#ffb48c"),
    "night":     ("#02030b", "#0b1026", "#2a2448", "#ffc890"),
    "hush":      ("#020309", "#0a0d22", "#3a2440", "#ff9fbf"),
    "water":     ("#081436", "#2c3a6a", "#a8786a", "#ffd27a"),
    "fragrance": ("#0f1a48", "#5a3f7e", "#f4b6a6", "#ffd6c0"),
    "rise":      ("#152b68", "#93578a", "#ffb873", "#ffecc4"),
    "glory":     ("#142a62", "#7a4f86", "#f0a06e", "#ffe2b4"),
}
_pal_keys = [
    (0.0, "dawn1"), (3.0, "dawn1"), (7.0, "dusk"), (10.0, "night"), (17.0, "night"), (19.0, "hush"), (27.0, "hush"),
    (30.0, "water"), (35.0, "water"), (38.0, "fragrance"), (42.0, "rise"), (52.0, "glory"), (TOTAL, "glory"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.90), (3, 0.80), (8, 0.35), (17, 0.30), (19, 0.22), (27, 0.25), (30, 0.60), (36, 0.80), (42, 0.90),
                 (50, 1.00), (PEAK_END, 1.10), (TOTAL, 1.00)])
SUN_Y = Track([(0, 0.31), (6, 0.27), (17, 0.26), (28, 0.27), (42, 0.32), (PEAK_END, 0.40), (TOTAL, 0.41)])
SUN_SIZE = Track([(0, 0.115), (8, 0.10), (28, 0.10), (42, 0.12), (PEAK_END, 0.135), (TOTAL, 0.135)])
STARS = Track([(0, 0.4), (5, 0.6), (9, 1.0), (27, 1.0), (32, 0.6), (42, 0.3), (52, 0.15), (TOTAL, 0.15)])
MILKY = Track([(0, 0.0), (5, 0.2), (10, 0.7), (27, 0.7), (32, 0.2), (40, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.6), (8, 0.3), (27, 0.3), (32, 0.55), (45, 0.75), (TOTAL, 0.7)])
AURORA = Track([(0, 0.35), (6, 0.15), (10, 0.10), (18, 0.18), (27, 0.20), (32, 0.30), (45, 0.45), (PEAK_END, 0.55), (TOTAL, 0.5)])
RAIN = Track([(0, 0.0), (28, 0.0), (29.5, 0.35), (33.5, 0.35), (35.5, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.5), (6, 0.3), (10, 0.2), (18, 0.12), (27, 0.15), (30, 0.35), (36, 0.5), (45, 0.7), (PEAK_END, 0.85), (TOTAL, 0.7)])
LANTERNS = Track([(0, 0.8), (4, 0.6), (8, 0.0), (41, 0.0), (45, 0.9), (PEAK_END, 1.0), (TOTAL, 0.9)])
PETALS = Track([(0, 0.0), (35, 0.0), (37, 0.45), (41, 0.55), (50, 0.6), (TOTAL, 0.5)])
TRAIL = Track([(0, 0.8), (8, 0.5), (28, 0.5), (42, 0.9), (TOTAL, 1.0)])
ZOOM = Track([(0, 0.99), (17, 0.985), (27, 0.97), (42, 0.975), (TOTAL, 0.955)])
EXPOSURE = Track([(0, 1.0), (18, 0.92), (27, 0.92), (30, 1.0), (46, 1.0), (52, 0.88), (TOTAL, 0.88)])
FADE = Track([(0, 0.0), (0.8, 1.0), (58.6, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.4), (6, 0.1), (10, 0.0), (28, 0.0), (32, 0.3), (42, 0.5), (52, 0.55), (TOTAL, 0.5)])
PART = Track([(0, 0.25), (40, 0.25), (44, 0.6), (52, 0.6), (TOTAL, 0.4)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# Lit before song 06 (concert star history): 3 Apology, 4 Inclusiveness, 6 Respect, 7 Encouragement, 8 Consideration,
# 9 Compliment. This song lights 5 Concession for the first time and Inclusiveness shines again.
OFF = 1e9
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, form=OFF, hold=OFF, star=OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=OFF, hold=OFF, star=OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, form=OFF, hold=OFF, star=-100.0),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, form=18.0, hold=27.0, star=-100.0,
         arrive=28.5),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, form=8.8, hold=15.8, star=17.3),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, form=OFF, hold=OFF, star=-100.0),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=OFF, hold=OFF, star=-100.0),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, form=OFF, hold=OFF, star=-100.0),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=OFF, hold=OFF, star=-100.0),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit in an earlier song: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
# A light lit earlier and spoken again in this song: star=-100.0 plus form, hold and arrive (when the words reach it).
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments: never on screen together with an expression
FRAGMENTS = [
    dict(text="waters this wilderness", t0=29.5, t1=31.0, out=34.0, dy=0.0, size=74, glow="#ffd27a"),
    dict(text="the fragrance of Her love", t0=36.0, t1=37.5, out=40.6, dy=0.0, size=74, glow="#f4b6a6"),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM · 6720 W Sahara Ave, Las Vegas", t0=52.0, t1=55.0)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Heavenly Mother Tells Us to Be Grains", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=1.2, t_move=4.8, t_rest=6.8, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky when a light is lit or shines again (time, x, y, strength)
WAVES = []
for i, p in enumerate(PHRASES):
    if 0.0 <= p["star"] < TOTAL:
        WAVES.append((p["star"], STAR_POS[i][0], STAR_POS[i][1], 1.0))
    if "arrive" in p:
        WAVES.append((p["arrive"], STAR_POS[i][0], STAR_POS[i][1], 0.45))   # a relit light: one new thin ring
WAVES.append((TITLE_HIT, 0.5, 0.62, 1.3))



def star_state(t):
    """Brightness and time since lighting for each of the nine lights."""
    out = []
    for i, p in enumerate(PHRASES):
        age = t - p["star"]
        if age < -0.2:
            out.append((0.0, -1.0))
            continue
        gather = min(max((age + 0.2) / 0.2, 0.0), 1.0)
        base = 0.55 * gather
        flash = np.exp(-max(age, 0.0) * 1.1) * 1.3 if age >= 0 else 0.0
        if "arrive" in p and t >= p["arrive"]:
            # a light that was lit in an earlier song shines again: a softer flare
            flash += np.exp(-(t - p["arrive"]) * 1.1) * 0.9
        fin = 0.0
        if t > NINTH:
            fin = 0.35 * min((t - NINTH) / 2.0, 1.0)
        if t > TITLE_HIT:
            fin += 0.35 * np.exp(-(t - TITLE_HIT) * 0.25) + 0.15
        out.append((base + flash + fin, max(age, 0.0)))
    return out


def link_state(t):
    """How far the line of light has grown between light i and light i+1 (0..1)."""
    out = []
    for i in range(8):
        # a line joins two lights only once both are lit (Greeting and Gratitude are still dark in this song)
        t1 = max(PHRASES[i]["star"], PHRASES[i + 1]["star"])
        # the line starts growing as the later light gathers and completes when it is lit
        g = min(max((t - (t1 - 1.2)) / 1.4, 0.0), 1.0)
        out.append(g * g * (3 - 2 * g))
    return out


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


if __name__ == "__main__":
    s = Song()
    print("frames", NFRAMES, "rings", len(s.rings))
    for tt in (0, 2, 6, 12, 20, 30, 40, 50, 57):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
