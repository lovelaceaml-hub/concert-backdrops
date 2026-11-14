"""Song 08, Out of Heaven, Favor From God: 1 minute promo ("The Embroidered Sky").

The minute of the 2:38 sung guide recording from 1:01.5 to 2:01.5 (audio/promo/s08.mp3): the princess line,
the Compliment (star 9 shines again), the bridegroom and bride, the Gratitude (star 2 lit for the first time,
so the arch of nine lights is complete), the pure soul coming home, and the lampstand giving light to the world.
Design: Designs/08 Out of Heaven, Favor From God - Video Design (Google Doc) in the shared Drive folder.

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
HORIZON = 0.31         # water line, as a fraction of the height from the bottom

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


# Landmarks in the promo minute (seconds from the start of the clip; guide recording time minus 61.5)
SISTER = 1.5          # "like a princess" line
COMPLIMENT = 10.0     # "swan on a lake" line: the Compliment
WEDDING = 19.0        # "bridegroom and bride meet"
THANKS = 28.0         # "praise and thanksgiving": the Gratitude
SOUL = 37.0           # "pure soul, come back"
LAMP = 46.0           # "lampstand and olive oil"
NINTH = 37.0          # star 2 arrives: all nine lights are lit, the whole arch glows from here
TITLE_HIT = 50.5      # end card

# Scene palettes (top of sky, middle, horizon, glow of the low light).
# Look for song 08 (DESIGN-SYSTEM.md section 6): a royal festival night in deep royal purple, crimson and gold,
# gold aurora like embroidery, rays and sparkle, grand and symmetrical framing.
PAL = {
    "royal":    ("#07020f", "#1c0833", "#3d1250", "#e8b860"),
    "royallav": ("#080314", "#251045", "#4e2468", "#e2c4ff"),
    "crimson":  ("#0c0214", "#3a0c42", "#7a1840", "#ffcf7a"),
    "gold":     ("#14051f", "#4a0f48", "#9a2a50", "#ffd56a"),
    "velvet":   ("#05010c", "#160626", "#3a0f3e", "#e0a860"),
    "festival": ("#100424", "#40104e", "#8c2550", "#ffd27a"),
    "rosegold": ("#1a0a30", "#4f1a58", "#b84a64", "#ffd9a0"),
}
_pal_keys = [
    (0.0, "royal"), (8.0, "royal"), (11.5, "royallav"), (18.5, "royallav"), (22.0, "crimson"), (27.0, "crimson"),
    (31.0, "gold"), (37.0, "gold"), (40.5, "velvet"), (45.5, "velvet"), (50.0, "festival"), (54.0, "festival"),
    (59.0, "rosegold"), (TOTAL, "rosegold"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the warm star at the center of the horizon (symmetrical framing): Mother's answering light at the thanksgiving
SUN_INT = Track([(0, 0.35), (9, 0.40), (14, 0.48), (19, 0.58), (27, 0.80), (31, 1.00), (36, 1.08), (40, 0.50),
                 (45, 0.48), (50, 0.85), (56, 0.92), (TOTAL, 0.9)])
SUN_Y = Track([(0, 0.27), (19, 0.28), (31, 0.34), (37, 0.35), (41, 0.28), (46, 0.28), (54, 0.32), (TOTAL, 0.33)])
SUN_SIZE = Track([(0, 0.10), (31, 0.13), (37, 0.135), (41, 0.105), (54, 0.125), (TOTAL, 0.125)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.0, 0.75), (18, 0.7), (28, 0.35), (36, 0.25), (40, 0.7), (46, 0.7),
               (52, 0.4), (TOTAL, 0.35)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.10), (19, 0.15), (28, 0.30), (37, 0.30), (41, 0.12), (50, 0.2), (TOTAL, 0.2)])
# gold aurora like embroidery across the whole night
AURORA = Track([(0, 0.0), (1.5, 0.14), (9, 0.16), (12, 0.22), (18, 0.24), (22, 0.18), (29, 0.26), (36, 0.30),
                (40, 0.16), (46, 0.16), (52, 0.26), (TOTAL, 0.24)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# festival sparkle
MOTES = Track([(0, 0.08), (2, 0.32), (10, 0.36), (19, 0.48), (28, 0.6), (33, 0.8), (37, 0.78), (40, 0.32),
               (46, 0.4), (52, 0.7), (TOTAL, 0.6)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.6), (19, 0.8), (31, 1.1), (37, 1.1), (40, 0.6), (50, 1.0), (TOTAL, 1.0)])
ZOOM = Track([(0, 1.0), (19, 0.99), (37, 0.975), (46, 0.97), (TOTAL, 0.96)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 1.5, 1.0), (TOTAL - 0.2, 0.0)])
# royal rays from the center star; heaven's light pours through the parted clouds at the thanksgiving
RAYS = Track([(0, 0.0), (2, 0.20), (12, 0.25), (20, 0.35), (30, 0.80), (36, 0.95), (40, 0.30), (48, 0.35),
              (53, 0.70), (TOTAL, 0.65)])
PART = Track([(0, 0.0), (28, 0.0), (32, 1.0), (38, 1.0), (42, 0.3), (TOTAL, 0.3)])

# Royal colors: gold embroidery aurora (warm pair) with a crimson and purple thread (cool pair, used with MILKY,
# which stays 0 here), and gold and rose-gold festival sparkle
AURORA_WARM = ("#ffd77a", "#e0607a")
AURORA_COOL = ("#c0406a", "#8a4ad0")
MOTE_COLORS = ("#ffe08a", "#ffb07a")

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT, NOT_YET = -100.0, 1e9
PHRASES = [
    # label, lines, max font px, form start, hold end, star time (campaign order, full wording)
    dict(label="Greeting", lines=["\u201cHow are you?\u201d"], size=176, form=NOT_YET, hold=NOT_YET, star=LIT),
    # Gratitude: lit for the first time in the concert, the last of the nine
    dict(label="Gratitude", lines=["\u201cThank you. It\u2019s all thanks to you.", "You\u2019ve worked hard.\u201d"], size=118,
         form=THANKS, hold=THANKS + 6.6, star=THANKS + 9.0),
    dict(label="Apology", lines=["\u201cI\u2019m sorry.", "It must have been hard on you.\u201d"], size=124, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Inclusiveness", lines=["\u201cIt\u2019s okay. I understand.\u201d"], size=150, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Concession", lines=["\u201cPlease, after you.\u201d"], size=164, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Respect", lines=["\u201cI\u2019d love to hear more", "about your thoughts.\u201d"], size=128, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Encouragement", lines=["\u201cI\u2019ll pray (or root) for you.", "Everything will go well.\u201d"], size=118, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Consideration", lines=["\u201cCan I give you a hand", "with anything?\u201d"], size=128, form=NOT_YET, hold=NOT_YET, star=LIT),
    # Compliment: first lit in song 01, spoken again here (flare and a new ring when the words arrive)
    dict(label="Compliment", lines=["\u201cYou\u2019re amazing.", "You\u2019re doing great!\u201d"], size=140,
         form=COMPLIMENT, hold=COMPLIMENT + 6.6, star=LIT, arrive=COMPLIMENT + 9.0),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit in an earlier song: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
# A light lit earlier and spoken again in this song: star=-100.0 plus form, hold and arrive (when the words reach it).
# End card
TITLE = dict(label="Healing Concert", lines=["The Words of Mother\u2019s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (never on screen with an expression): text, t0, t1, out, dy, size
FRAGMENTS = [
    dict(text="bridegroom and bride", t0=20.0, t1=21.8, out=25.6, dy=0.0, size=78, glow="#fff0d2"),
    dict(text="into our Mother\u2019s arms", t0=39.2, t1=41.0, out=44.8, dy=0.0, size=74, glow="#e2c4ff"),
]

TAGLINE = dict(text="Sunday, December 6 \u00b7 4:30 PM\nThe World Mission Society Church of God \u00b7 6720 W Sahara Ave, Las Vegas",
               t0=53.2, t1=56.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Out of Heaven, Favor From God", concert="The Words of Mother\u2019s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=5.4, t_rest=7.4, scale=0.34, alpha_rest=0.58,
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
WAVES = [
    (COMPLIMENT + 9.0, STAR_POS[8][0], STAR_POS[8][1], 0.7),   # star 9 shines again
    (THANKS + 9.0, STAR_POS[1][0], STAR_POS[1][1], 1.2),       # star 2 lit: the arch is complete
    (TITLE_HIT, 0.5, 0.62, 1.1),
]


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
        # a line appears only once both of its lights are lit (star 2 is dark until the thanksgiving)
        t1 = max(PHRASES[i]["star"], PHRASES[i + 1]["star"])
        # the line starts growing as the next light gathers and completes when it is lit
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
    for tt in (0, 5, 12, 22, 32, 38, 42, 50, 57):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
