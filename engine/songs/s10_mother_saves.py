"""Song 10, Our Mother Saves the World: 1 minute promo, VISUAL ONLY, NO MUSIC YET.

There is no recording and no lyrics for this song yet, so this promo is drawn to a calm 60 second timeline of its
own. The music features (loudness, onsets, the mountain skyline) are made here from that timeline instead of being
measured, so the silent audio file the workflow needs plays no part in the picture.

Design: "The Lamp on the Shore" (Designs/10 Our Mother Saves the World - Video Design). The warm star that rests on
the horizon in every song rises as Mother's lamp, and its light is Her words. All nine lights are already lit when
this song starts (star history, DESIGN-SYSTEM.md 12a). As a closing gift, three of Mother's words return in full
(Greeting, Consideration, Encouragement), then the other six lights flare in turn and the whole arch glows.
No lyric fragments: the lyrics are not available.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SONG_ID = os.path.splitext(os.path.basename(__file__))[0]

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5
SONG_END = 60.0
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.30
RIDGE_X0, RIDGE_W = 0.035, 0.93


def lin(hexs):
    h = hexs.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    return c ** 2.2


def _ar(x, attack, release):
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


# ----------------------------------------------------------------- the minute, scene by scene
# 0 to 6     title card over the restless night; one small warm star on the horizon
# 6 to 16    the lamp is lifted: the horizon star rises and brightens, a road of gold on the water,
#            Her mantle of light (soft gold and rose aurora) unfolds along the horizon
# 16 to 47   Mother's words go out: Greeting, Consideration, Encouragement, each about 9 to 10 seconds;
#            rescued lights rise as lanterns
# 47 to 50   the other six lights flare in turn and the whole arch glows (closing gift of the nine words)
# 48 to 60   end card and concert details over the dawn; calm hold, fade at the very end
LAMP = 6.0
WORDS1 = 16.5
WORDS2 = 26.5
WORDS3 = 36.5
SWEEP = 47.0
NINTH = 49.3
TITLE_HIT = 51.0

# Calm story curve that stands in for loudness (no recording yet)
_STORY = Track([(0, 0.30), (6, 0.33), (16, 0.44), (30, 0.50), (46, 0.60), (50, 0.68), (56, 0.60), (TOTAL, 0.55)])

# Moments that land like notes: early restless ripples, Mother's words arriving, the rescued lights, the sweep
_EVENTS = ([(t, 0.45) for t in (1.6, 3.9, 5.3, 7.8, 9.7, 11.4, 13.1, 14.6)]
           + [(t, 1.0) for t in (WORDS1 + 3.0, WORDS2 + 3.0, WORDS3 + 3.0)]
           + [(18.0 + 1.7 * k, 0.6) for k in range(17)]
           + [(SWEEP + 0.3 * k, 0.8) for k in range(6)]
           + [(TITLE_HIT, 1.1)])
_EVENTS.sort()


class Song:
    """Same interface as a measured song, built from the timeline above."""

    def __init__(self):
        ft = np.arange(NFRAMES) / FPS
        self.ft = ft
        story = np.array([_STORY(t) for t in ft])
        breath = 0.04 * np.sin(ft * 0.55) + 0.03 * np.sin(ft * 0.23 + 1.0)
        n_f = np.clip(story + breath, 0.0, 1.0)
        self.env = _ar(n_f, 0.07, 0.45)
        self.env_slow = _gauss(n_f, 1.4 * FPS)
        self.hi = np.clip(0.28 + 0.25 * story + 0.08 * np.sin(ft * 0.8), 0.0, 1.0)
        pooled = np.zeros(NFRAMES)
        for et, s in _EVENTS:
            pooled[min(int(et * FPS), NFRAMES - 1)] = max(pooled[min(int(et * FPS), NFRAMES - 1)], s)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain skyline, shaped by the story curve (the same method as a measured song)
        xs = np.linspace(0.0, 1.0, 2048)
        st = (xs - RIDGE_X0) / RIDGE_W * MUSIC_END
        base = np.interp(st, ft, _gauss(n_f, 2.3 * FPS))
        mid = np.interp(st, ft, _gauss(n_f, 1.0 * FPS)) - base
        v = np.clip((base - 0.22) / 0.56, 0.0, 1.0) ** 1.4

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 20 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 9), (0.25, 23), (0.125, 61), (0.0625, 150), (0.03, 340))))
        hgt = 0.030 + 0.120 * v + 0.07 * mid * (0.35 + v) + (0.014 + 0.034 * v) * (crag - 0.5)
        edge = 0.020 + 0.012 * (crag - 0.5)
        # blend smoothly into the low edge over the first and last 5 seconds (no hard step at the ends)
        taper = np.clip(np.minimum(st, MUSIC_END - st) / 5.0, 0.0, 1.0)
        taper = taper * taper * (3 - 2 * taper)
        sh = np.clip(np.minimum(xs, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.maximum((edge + (hgt - edge) * taper) * (0.5 + 0.5 * sh), 0.006).astype("f4")
        # rings on the water: soft early ripples, a clear ring where each word lands
        keep = []
        for k, (et, s) in enumerate(_EVENTS):
            r = np.random.default_rng(1000 + k).random(2)
            keep.append((float(et), 0.08 + 0.84 * r[0], HORIZON * (0.18 + 0.62 * r[1] ** 1.3), float(min(s, 1.2))))
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


# Palettes (top of sky, middle, horizon, glow of the low sun): deep night, the lamp's gold, pre-dawn rose, dawn
PAL = {
    "night":   ("#02030b", "#0b1026", "#1a2346", "#ffc46b"),
    "lamp":    ("#03050f", "#0e1530", "#3a2f4e", "#ffd9a0"),
    "predawn": ("#070b26", "#2b2356", "#a05d6c", "#ffb48c"),
    "rose":    ("#0d173e", "#4a3576", "#f2a08a", "#ffd08c"),
    "dawn":    ("#12245a", "#6c4a88", "#f5a070", "#ffe3a3"),
    "morning": ("#15295f", "#7d5086", "#f6b07e", "#ffe8bc"),
}
_pal_keys = [
    (0.0, "night"), (5.0, "night"), (12.0, "lamp"), (20.0, "lamp"), (30.0, "predawn"), (40.0, "rose"),
    (49.0, "dawn"), (56.0, "morning"), (TOTAL, "morning"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# The sun is the horizon star: small and low, then lifted as Mother's lamp
SUN_INT = Track([(0, 0.12), (LAMP, 0.16), (12, 0.55), (16, 0.80), (30, 0.88), (46, 0.98), (50, 1.06), (56, 1.02), (TOTAL, 1.0)])
SUN_Y = Track([(0, 0.25), (LAMP, 0.25), (16, 0.29), (30, 0.31), (46, 0.34), (52, 0.37), (TOTAL, 0.38)])
SUN_SIZE = Track([(0, 0.085), (LAMP, 0.09), (16, 0.11), (46, 0.12), (52, 0.135), (TOTAL, 0.135)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.95), (12, 1.0), (24, 0.7), (40, 0.35), (50, 0.18), (TOTAL, 0.15)])
MILKY = Track([(0, 0.0), (3, 0.35), (8, 0.3), (12, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.55), (10, 0.6), (18, 0.4), (34, 0.3), (50, 0.35), (TOTAL, 0.35)])
AURORA = Track([(0, 0.0), (9, 0.0), (14, 0.30), (20, 0.40), (34, 0.36), (46, 0.40), (50, 0.44), (56, 0.36), (TOTAL, 0.34)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.04), (3, 0.14), (12, 0.25), (24, 0.40), (46, 0.6), (50, 0.72), (56, 0.55), (TOTAL, 0.5)])
LANTERNS = Track([(0, 0.0), (18, 0.0), (22, 0.6), (30, 0.9), (46, 1.0), (52, 0.45), (58, 0.2), (TOTAL, 0.2)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.45), (16, 0.65), (46, 0.9), (52, 1.0), (TOTAL, 0.9)])
ZOOM = Track([(0, 1.0), (16, 0.99), (46, 0.972), (TOTAL, 0.955)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (57.0, 1.0), (59.8, 0.0)])
RAYS = Track([(0, 0.0), (10, 0.0), (16, 0.35), (30, 0.45), (46, 0.52), (50, 0.62), (56, 0.55), (TOTAL, 0.52)])
PART = Track([(0, 0.0), (12, 0.0), (17, 0.8), (24, 0.8), (30, 0.3), (TOTAL, 0.3)])

STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

FORM_DUR = 3.0
_OFF = 1e9
# All nine were lit in earlier songs (star=-100). Greeting, Consideration and Encouragement are spoken again here
# (form, hold, arrive); the other six flare in turn during the sweep (arrive only, no words).
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176,
         form=WORDS1, hold=WORDS1 + 7.6, arrive=WORDS1 + 9.6, star=-100.0),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.0, star=-100.0),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.3, star=-100.0),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.6, star=-100.0),
    dict(label="Concession", lines=["“Please, after you.”"], size=164,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.9, star=-100.0),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         form=_OFF, hold=_OFF, arrive=SWEEP + 1.2, star=-100.0),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=WORDS3, hold=WORDS3 + 7.6, arrive=WORDS3 + 9.6, star=-100.0),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         form=WORDS2, hold=WORDS2 + 7.6, arrive=WORDS2 + 9.6, star=-100.0),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         form=_OFF, hold=_OFF, arrive=SWEEP + 1.5, star=-100.0),
]

# End card
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
FRAGMENTS = []   # no lyrics yet
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=52.5, t1=56.0)

CREDIT = dict(song="Our Mother Saves the World", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.6, t_rest=6.6, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048)


def credit_state(t, bbox):
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


# Waves of light across the sky: one where each word reaches its light, softer ones in the sweep, one for the end card
WAVES = [(p["arrive"], STAR_POS[i][0], STAR_POS[i][1], 0.45 if p["form"] < _OFF else 0.28)
         for i, p in enumerate(PHRASES)]
WAVES.append((TITLE_HIT, 0.5, 0.62, 1.2))


# star_state and link_state come from engine/arch.py (installed by song.py), the same for every song.


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
    print("frames", NFRAMES, "rings", len(s.rings), "ridge", float(s.ridge.min()), float(s.ridge.max()))
    for tt in (0, 5, 12, 20, 30, 40, 47.5, 50, 57, 59.9):
        p = params(s, tt)
        print(tt, {k: round(v, 2) for k, v in p.items() if isinstance(v, float)})
