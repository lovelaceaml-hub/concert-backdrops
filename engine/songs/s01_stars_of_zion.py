"""Song 01, All You Stars of Zion: the 1 minute promo (design "From Starlight to Sunrise").

The minute is 3:01 to 4:01 of the studio recording: the final chorus, from the last stars of the night to the
first sunrise of the concert. The morning star flares, "dew of the dawn" and "Arise" appear as short fragments,
the sun rises, and Encouragement is lit for the first time in the concert (Compliment was lit earlier in the song).
Audio: audio/promo/s01.mp3 (60 s clip). Live the song is a 3:08 brass version with no singing.
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
MUSIC_END = 59.3       # last sounding moment of the clip (final chord at 4:00 of the recording)
SONG_END = 60.0        # length of the clip
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


# Landmarks in the promo minute (seconds of the clip; add 181 for the recording). Measured loudness:
# rise 4 to 9, loudest moment 9, lift 21, sunbeam pocket 32, full plateau 41 to 58, final chord ends 59.
RISE = 4.0
PEAK = 9.0
SUNRISE = 21.0
BEAMS = 32.0
PLATEAU = 41.0
NINTH = 1e9            # the whole arch does not glow in song 01
TITLE_HIT = 53.5       # end card

# Scene palettes (top of sky, middle, horizon, glow of the low sun): the last of the night to the first morning
PAL = {
    "lastnight": ("#040820", "#141a46", "#3c3466", "#c79ab0"),
    "blush":     ("#071030", "#2a2a62", "#8c5a78", "#ffb092"),
    "dawn":      ("#0e1c4c", "#4c3d7e", "#d98274", "#ffcf96"),
    "rise":      ("#14306a", "#6e5a92", "#f5a070", "#ffe0a8"),
    "gold":      ("#1d3f7c", "#8a6f9e", "#ffbf7e", "#fff0c8"),
    "morning":   ("#22508c", "#9584a8", "#ffd09a", "#fff4d8"),
}
_pal_keys = [
    (0.0, "lastnight"), (4.0, "lastnight"), (10.0, "blush"), (17.0, "dawn"), (22.0, "rise"), (33.0, "gold"),
    (44.0, "gold"), (52.0, "morning"), (TOTAL, "morning"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the sun: below the mountains until "Arise", then rising behind the word
SUN_INT = Track([(0, 0.30), (4, 0.38), (9, 0.62), (14, 0.55), (19, 0.75), (21, 0.95), (26, 1.20), (32, 1.15),
                 (41, 1.25), (50, 1.40), (TOTAL, 1.30)])
SUN_Y = Track([(0, 0.24), (12, 0.25), (19, 0.27), (21, 0.29), (26, 0.32), (33, 0.355), (45, 0.39), (TOTAL, 0.41)])
SUN_SIZE = Track([(0, 0.10), (21, 0.11), (33, 0.125), (TOTAL, 0.13)])
# the last stars: the morning star moment at the peak, then the stars fade into day
STARS = Track([(0, 0.0), (0.2, 0.0), (1.8, 0.95), (6, 1.0), (9, 1.0), (13, 0.7), (21, 0.35), (30, 0.14), (TOTAL, 0.10)])
MILKY = Track([(0, 0.0), (1.5, 0.30), (8, 0.25), (14, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.25), (12, 0.45), (21, 0.55), (40, 0.6), (TOTAL, 0.55)])
AURORA = Track([(0, 0.06), (8, 0.18), (10, 0.30), (20, 0.22), (32, 0.30), (41, 0.40), (50, 0.38), (TOTAL, 0.30)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (4, 0.25), (9, 0.55), (15, 0.40), (21, 0.60), (32, 0.55), (41, 0.80), (50, 0.95), (TOTAL, 0.70)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.55), (9, 0.8), (21, 0.95), (41, 1.05), (TOTAL, 1.0)])
ZOOM = Track([(0, 1.0), (21, 0.985), (41, 0.968), (TOTAL, 0.955)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.2, 1.0), (58.6, 1.0), (59.9, 0.0)])
RAYS = Track([(0, 0.0), (19, 0.0), (22, 0.35), (28, 0.55), (32, 0.75), (41, 0.70), (50, 0.85), (TOTAL, 0.75)])
PART = Track([(0, 0.0), (20, 0.0), (23, 1.0), (30, 1.0), (36, 0.3), (TOTAL, 0.3)])

# Nine lights on an arch over the stage, one for each expression (campaign order, left to right)
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

_NOT_YET = dict(form=1e9, hold=1e9, star=1e9)
PHRASES = [
    # label, lines, max font px, form start, hold end, star time
    dict(label="Greeting", lines=["“How are you?”"], size=176, **_NOT_YET),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **_NOT_YET),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **_NOT_YET),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **_NOT_YET),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **_NOT_YET),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **_NOT_YET),
    # lit for the first time in the concert, on the final "Now let us arise" (the full plateau)
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=39.5, hold=48.5, star=50.0),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **_NOT_YET),
    # lit earlier in this song (verse 1, "faithful and beautiful work"), already shining in this minute
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=1e9, hold=1e9, star=-100.0),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit before this minute: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (never on screen together with an expression)
FRAGMENTS = [
    dict(text="dew of the dawn", t0=10.0, t1=11.8, out=17.0, dy=0.0, size=84),
    dict(text="Arise", t0=21.0, t1=22.6, out=29.5, dy=0.0, size=150),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM · 6720 W Sahara Ave, Las Vegas", t0=55.0, t1=57.0)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="All You Stars of Zion", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=6.0, t_rest=8.0, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky when a light is lit (time, x, y, strength)
WAVES = [(p["star"], STAR_POS[i][0], STAR_POS[i][1], s) for i, (p, s) in enumerate(
    zip(PHRASES, [0.35, 0.3, 0.3, 1.0, 0.45, 0.5, 0.35, 0.4, 1.1]))]
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
    """Lines of light only join two neighbouring lights that are both lit (song 01 lights 9 and 7, not neighbours)."""
    out = []
    for i in range(8):
        t0, t1 = PHRASES[i]["star"], PHRASES[i + 1]["star"]
        g = min(max((t - (max(t0, t1) - 1.2)) / 1.4, 0.0), 1.0)
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
    d = np.load(FEATURES)
    t = d["times"]
    db = _db(d["rms"])
    for a, b in ((56.5, 59.0), (173.5, 176.0), (246.5, 249.0)):
        m = (t >= a) & (t <= b)
        print("fine rms", a, b, " ".join(f"{x:.0f}" for x in db[m][::4]))
    for tt in (0, 5, 30, 60, 112, 140, 200, 230, 260):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
