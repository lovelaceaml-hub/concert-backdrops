"""Song 02, The Rose: 1 minute promo, visual only (no recording of the trio exists yet).

Design: Google Doc "02 The Rose - Video Design" ("The Seed Under the Snow"). This promo is the heart of it in
60 seconds, drawn with the engine's current effects:
  0 to 7    home night lake, stars 9 and 7 already lit (from song 01), title card
  7 to 16   the home star sinks low (becomes the seed), the coldest, loneliest night; fragment "too lonely"
  16 to 22  the choir's small lights rise from the water, the trio's ribbons (aurora) gather
  22 to 34  Encouragement, full wording, about 9 seconds with nothing else competing; its words fly up and
            relight star 7 (a brief flare and one new thin ring)
  36 to 50  the seed wakes ("the seed"), dawn rises, rays, the rose's petals ("becomes the rose")
  50 to 60  end card: Healing Concert, The Words of Mother's Love, date and place
The signature effects of the design (snow, the frozen lake, the descent under the snow, the rose itself, Mother's
hands of light) need new engine work; they are not in this promo.

There is no music, so this file does not read the recording's measurements: the gentle breathing of the light,
the skyline and the "piano note" rings on the water are drawn from the timeline below. The workflow's audio file
is a near silent placeholder.
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
HORIZON = 0.30         # water line, as a fraction of the height from the bottom

RIDGE_X0, RIDGE_W = 0.035, 0.93


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


# The drawn "music": how strongly the light breathes through the minute (0 to 1)
BREATH = Track([(0, 0.30), (6, 0.30), (12, 0.20), (18, 0.18), (22, 0.34), (27, 0.52), (31, 0.55), (34, 0.48),
                (38, 0.34), (44, 0.58), (50, 0.74), (56, 0.62), (TOTAL, 0.55)])
# Piano notes drawn as rings on the water: on the open lake at the start and again after the thaw; none while
# the lake is frozen (the design's winter)
RING_SPANS = [(1.5, 11.0, 2.1), (44.0, 59.0, 1.5)]


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


# Landmarks (seconds into the promo)
STAR_SINKS = 9.0       # the home star goes down to the shore and becomes the seed
ENC_FORM = 22.0        # Encouragement starts forming
ENC_HOLD = 31.0        # its words begin to fly
ENC_ARRIVE = 33.5      # they reach star 7: a brief flare and one new thin ring
SEED_WAKES = 38.0
DAWN = 44.0
NINTH = 1e9            # the whole arch does not glow at the end of this song
TITLE_HIT = 53.0       # end card

# Scene palettes (top of sky, middle, horizon, glow of the low home star / sun)
PAL = {
    "home":    ("#02030b", "#080d2a", "#141a3a", "#ffc98a"),
    "cold":    ("#010208", "#050a1e", "#0e1a33", "#9fb8ff"),
    "deep":    ("#010106", "#03071a", "#080c1a", "#8ea4ff"),
    "violet":  ("#030419", "#110e36", "#262050", "#b293e7"),
    "predawn": ("#080d2c", "#33265c", "#a85f6e", "#ffb48c"),
    "dawn":    ("#0f1b46", "#553b7c", "#e9836f", "#ffd08c"),
    "rise":    ("#12265c", "#7c4c84", "#f4b6a0", "#ffe2ac"),
    "risepk":  ("#152b68", "#93578a", "#ffd3b0", "#ffecc4"),
}
_pal_keys = [
    (0.0, "home"), (6.0, "home"), (12.0, "cold"), (16.0, "deep"), (21.0, "deep"), (26.0, "violet"),
    (32.0, "violet"), (36.0, "deep"), (39.0, "deep"), (42.0, "predawn"), (46.0, "dawn"), (50.0, "rise"),
    (56.0, "risepk"), (TOTAL, "risepk"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.24), (6, 0.24), (STAR_SINKS, 0.14), (14, 0.05), (SEED_WAKES - 2, 0.05), (SEED_WAKES, 0.12),
                 (42, 0.35), (DAWN, 0.70), (48, 1.00), (53, 1.18), (TOTAL, 1.12)])
SUN_Y = Track([(0, 0.27), (6, 0.27), (12, 0.21), (SEED_WAKES - 2, 0.21), (41, 0.25), (46, 0.32), (53, 0.39),
               (TOTAL, 0.41)])
SUN_SIZE = Track([(0, 0.09), (12, 0.07), (SEED_WAKES, 0.075), (48, 0.12), (TOTAL, 0.13)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.0, 0.9), (10, 1.0), (36, 1.0), (42, 0.6), (48, 0.25), (TOTAL, 0.15)])
MILKY = Track([(0, 0.15), (8, 0.55), (14, 1.0), (34, 1.0), (40, 0.3), (44, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.15), (14, 0.08), (36, 0.12), (DAWN, 0.45), (TOTAL, 0.55)])
# the trio's three ribbons of light: dim in the lonely night, gathering as they come, strong while they speak
AURORA = Track([(0, 0.0), (4, 0.08), (10, 0.18), (15, 0.10), (19, 0.32), (ENC_FORM + 2, 0.55), (ENC_HOLD, 0.60),
                (ENC_ARRIVE + 1, 0.40), (40, 0.22), (46, 0.32), (TOTAL, 0.28)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.05), (3, 0.14), (12, 0.08), (20, 0.22), (30, 0.42), (36, 0.28), (DAWN, 0.55), (52, 0.78),
               (TOTAL, 0.6)])
# the choir's small lights rising from the water around the lonely one
LANTERNS = Track([(0, 0.0), (15.5, 0.0), (19.5, 0.30), (ENC_HOLD, 0.50), (36, 0.25), (41, 0.0), (TOTAL, 0.0)])
# the rose: its petals in the dawn
PETALS = Track([(0, 0.0), (43.0, 0.0), (46.0, 0.45), (49.0, 1.0), (56, 1.0), (TOTAL, 0.85)])
TRAIL = Track([(0, 0.0), (1.2, 0.35), (14, 0.25), (30, 0.55), (48, 0.9), (TOTAL, 0.8)])
ZOOM = Track([(0, 1.0), (20, 0.988), (ENC_HOLD, 0.976), (TOTAL, 0.952)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (58.6, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (41, 0.0), (DAWN, 0.30), (48, 0.70), (56, 0.80), (TOTAL, 0.72)])
PART = Track([(0, 0.0), (DAWN - 1, 0.0), (47, 1.0), (52, 1.0), (56, 0.3), (TOTAL, 0.3)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = 1e9
PHRASES = [
    # campaign order; full wording. Star history: song 01 lit 9 and 7; song 02 speaks Encouragement again.
    dict(label="Greeting", lines=["“How are you?”"], size=176, form=OFF, hold=OFF, star=OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=OFF, hold=OFF, star=OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, form=OFF, hold=OFF, star=OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, form=OFF, hold=OFF, star=OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, form=OFF, hold=OFF, star=OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, form=OFF, hold=OFF, star=OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, form=OFF, hold=OFF, star=OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=OFF, hold=OFF, star=-100.0),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (a few words each; the song is copyrighted). Never on screen with the expression.
FRAGMENTS = [
    dict(text="too lonely", t0=9.0, t1=11.0, out=14.0, dy=0.04, size=84, glow="#9fb8ff"),
    dict(text="the seed", t0=37.5, t1=39.5, out=42.5, dy=-0.02, size=84, glow="#ffb347"),
    dict(text="becomes the rose", t0=44.5, t1=46.5, out=48.6, dy=0.02, size=88, glow="#f7a889"),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM · 6720 W Sahara Ave, Las Vegas", t0=55.0, t1=57.5)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="The Rose", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=5.0, t_rest=7.0, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky (time, x, y, strength): the one new thin ring when star 7 shines again,
# and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.45), (TITLE_HIT, 0.5, 0.62, 1.1)]


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
        if t > TITLE_HIT:
            fin += 0.25 * np.exp(-(t - TITLE_HIT) * 0.25) + 0.10
        out.append((base + flash + fin, max(age, 0.0)))
    return out


def link_state(t):
    """A line of light joins two neighbouring lights only when both are lit (here 7 and 9 are not neighbours)."""
    out = []
    for i in range(8):
        t0, t1 = PHRASES[i]["star"], PHRASES[i + 1]["star"]
        tl = max(t0, t1)
        g = min(max((t - (tl - 1.2)) / 1.4, 0.0), 1.0)
        out.append(g * g * (3 - 2 * g))
    return out


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


if __name__ == "__main__":
    s = Song()
    print("frames", NFRAMES, "rings", len(s.rings))
    for tt in (0, 5, 12, 25, 33.5, 40, 48, 55, 59.9):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)},
              [round(x[0], 2) for x in p["star"]])
