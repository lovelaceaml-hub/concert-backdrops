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
# star_state and link_state below are replaced by engine/arch.py when the engine loads this file
TITLE_HIT = 51.6       # end card

# Scene palettes (top of sky, middle, horizon, glow of the low home star / sun).
# The 02 look (DESIGN-SYSTEM.md section 6): deep winter night with snowfall, a pale pink spring dawn at the end;
# silver blue, white, blush pink; close and quiet framing.
PAL = {
    "morning": ("#173a74", "#8c7282", "#ffc47c", "#ffeacc"),   # song 01's closing frame (agreed hand-off)
    "dusk":    ("#101a33", "#3c4566", "#8a8fae", "#d9c9d6"),
    "winter":  ("#0b1424", "#1d2c45", "#5a6f8f", "#cfe0ff"),
    "deep":    ("#05080f", "#0e1828", "#2e3e58", "#b9cbe8"),
    "violet":  ("#0a0c1e", "#22204a", "#5b5a8c", "#b293e7"),
    "pearl":   ("#172038", "#4a5274", "#b49cb2", "#f0dbe4"),
    "blush":   ("#212c4c", "#5f6488", "#d9a7b6", "#ffe1e8"),
    "blushpk": ("#26325a", "#6a6d94", "#e2b3c0", "#ffe9ee"),
}
_pal_keys = [
    (0.0, "morning"), (1.5, "morning"), (5.0, "dusk"), (9.0, "winter"), (16.0, "deep"), (21.0, "deep"),
    (26.0, "violet"), (32.0, "violet"), (36.0, "deep"), (39.0, "deep"), (42.0, "pearl"), (46.0, "blush"),
    (52.0, "blushpk"), (TOTAL, "blushpk"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.90), (1.5, 0.85), (5.0, 0.35), (STAR_SINKS, 0.14), (14, 0.05), (SEED_WAKES - 2, 0.05),
                 (SEED_WAKES, 0.12), (42, 0.25), (DAWN, 0.40), (48, 0.55), (51, 0.60), (54, 0.45), (TOTAL, 0.42)])
SUN_Y = Track([(0, 0.41), (1.5, 0.40), (6, 0.30), (12, 0.25), (SEED_WAKES - 2, 0.25), (41, 0.29), (46, 0.36),
               (53, 0.43), (TOTAL, 0.45)])
SUN_SIZE = Track([(0, 0.13), (6, 0.08), (12, 0.07), (SEED_WAKES, 0.075), (48, 0.11), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (3, 0.15), (8, 0.55), (14, 0.45), (36, 0.45), (42, 0.25), (48, 0.08), (TOTAL, 0.05)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])          # no Milky Way: that belongs to song 01
# snow clouds over the winter night, thinning at dawn
CLOUDS = Track([(0, 0.25), (8, 0.55), (16, 0.70), (36, 0.65), (DAWN, 0.40), (TOTAL, 0.30)])
# the trio's ribbons: only a faint veil while they speak (aurora is song 03's and 08's texture)
AURORA = Track([(0, 0.0), (19, 0.0), (ENC_FORM + 2, 0.14), (ENC_HOLD, 0.16), (ENC_ARRIVE + 2, 0.05), (40, 0.0),
                (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])            # no rain in this song
# faint frost glints in the air
MOTES = Track([(0, 0.06), (8, 0.08), (20, 0.10), (30, 0.14), (36, 0.10), (DAWN, 0.16), (52, 0.20), (TOTAL, 0.18)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])        # lanterns belong to songs 03 and 07
# falling snow through the night (white), easing while Encouragement speaks, then the rose's blush petals at dawn
PETALS = Track([(0, 0.0), (5.0, 0.0), (8.0, 0.18), (13.0, 0.32), (19.0, 0.30), (ENC_FORM, 0.12), (ENC_HOLD, 0.12),
                (36, 0.22), (40, 0.18), (43.0, 0.10), (46.0, 0.22), (49.0, 0.28), (52, 0.20), (TOTAL, 0.18)])
TRAIL = Track([(0, 0.0), (1.2, 0.30), (14, 0.22), (30, 0.45), (48, 0.6), (TOTAL, 0.55)])
# close and quiet framing, moving slowly closer
ZOOM = Track([(0, 0.93), (20, 0.91), (ENC_HOLD, 0.895), (TOTAL, 0.875)])
EXPOSURE = Track([(0, 1.0), (DAWN, 1.0), (48, 0.92), (54, 0.84), (TOTAL, 0.84)])
FADE = Track([(0, 0.0), (1.0, 1.0), (58.6, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (41, 0.0), (DAWN, 0.12), (48, 0.24), (51, 0.24), (54, 0.15), (TOTAL, 0.14)])
PART = Track([(0, 0.0), (DAWN - 1, 0.0), (47, 0.5), (52, 0.4), (56, 0.2), (TOTAL, 0.2)])


def _mix_hex(a, b, u):
    ca = [int(a[k:k + 2], 16) for k in (1, 3, 5)]
    cb = [int(b[k:k + 2], 16) for k in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x * (1 - u) + y * u)):02x}" for x, y in zip(ca, cb))


def PETAL_COLORS(t):
    """Snow (white and silver blue) through the night; the rose's blush petals at dawn. Used by the engine when it
    supports song colors for petals; otherwise the engine's own petal colors apply."""
    u = min(max((t - 42.0) / 4.0, 0.0), 1.0)
    u = u * u * (3 - 2 * u)
    return _mix_hex("#ffffff", "#f6b3c4", u), _mix_hex("#d6e4ff", "#fff1f3", u)


MOTE_COLORS = ("#f4f8ff", "#cfe0ff")              # frost glints, white and silver blue
MOTE_Y = (1.05, -0.05)                            # motes fall slowly, like the finest snow
AURORA_WARM = ("#c9d8ff", "#e4d8ff")              # the trio's faint veil: silver and pale violet, never gold
AURORA_COOL = ("#c9d8ff", "#e4d8ff")

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
    dict(text="too lonely", t0=9.0, t1=11.0, out=14.0, dy=0.04, size=84, glow="#cfe0ff"),
    dict(text="the seed", t0=37.5, t1=39.5, out=42.5, dy=-0.02, size=84, glow="#ffb347"),
    dict(text="becomes the rose", t0=44.0, t1=45.5, out=47.0, dy=0.02, size=88, glow="#f6b3c4"),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=53.0, t1=55.0)

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
