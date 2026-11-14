"""Song 03, I Reminisce About Your Love: 1 minute promo of "The Lake of Memory" design.

Clip: studio recording 3:14 to 4:14 (audio/promo/s03.mp3). Verse 2 second half into chorus 2: the frozen storm's
lanterns, the aurora as Her warm hands, Her prayer (Encouragement, relit), the crescendo of the seed of courage,
and the sunrise of chorus 2. Arch state at this point of the song: 3 (Apology, lit earlier in this song), 7 and 9 lit.
Design: Google Doc "03 I Reminisce About Your Love - Video Design" in the project's Designs folder.

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


# Landmarks in the promo clip (seconds into the clip; studio time minus 194 s). Section steps are measured
# from the studio recording's loudness; line times are estimates.
HANDS = 4.0          # 3:18 "I used to feel Her warm hands" (measured step up)
PRAYER = 28.0        # 3:42 "Putting Her hands together" (measured step up)
CRESC = 38.0         # 3:52 crescendo, "sowed courage to go on"
SUNRISE = 50.0       # 4:04 chorus 2 arrives (measured)
NINTH = 1e9          # the whole arch does not glow in this song
TITLE_HIT = 51.0     # end card

# Scene palettes (top of sky, middle, horizon, glow of the low sun)
PAL = {
    "storm":   ("#020511", "#081638", "#1a335c", "#9cc2ff"),
    "aurora":  ("#040822", "#161d4c", "#3b3a6e", "#c7a8ff"),
    "warm":    ("#050820", "#221a48", "#6e4263", "#ffa58c"),
    "predawn": ("#080d2c", "#33265c", "#a85f6e", "#ffb48c"),
    "dawn":    ("#0f1b46", "#553b7c", "#e9836f", "#ffd08c"),
    "rise":    ("#12265c", "#7c4c84", "#f59a6c", "#ffe2ac"),
    "risepk":  ("#152b68", "#93578a", "#ffb873", "#ffecc4"),
}
_pal_keys = [
    (0.0, "storm"), (6.0, "storm"), (16.0, "aurora"), (27.0, "warm"), (38.0, "warm"), (45.0, "predawn"),
    (SUNRISE, "dawn"), (54.0, "rise"), (58.0, "risepk"), (TOTAL, "risepk"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.10), (27, 0.18), (CRESC, 0.30), (46, 0.55), (SUNRISE, 1.0), (55, 1.15), (TOTAL, 1.1)])
SUN_Y = Track([(0, 0.25), (CRESC, 0.26), (SUNRISE, 0.31), (TOTAL, 0.36)])
SUN_SIZE = Track([(0, 0.10), (SUNRISE, 0.115), (TOTAL, 0.125)])
STARS = Track([(0, 0.0), (0.4, 0.0), (2.5, 1.0), (27, 0.95), (44, 0.6), (SUNRISE, 0.3), (TOTAL, 0.15)])
MILKY = Track([(0, 0.0), (2.5, 0.7), (27, 0.55), (44, 0.15), (SUNRISE, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.55), (16, 0.35), (38, 0.35), (SUNRISE, 0.5), (TOTAL, 0.75)])
AURORA = Track([(0, 0.06), (HANDS, 0.12), (12, 0.45), (22, 0.62), (PRAYER, 0.72), (CRESC, 0.66), (46, 0.38),
                (SUNRISE, 0.26), (TOTAL, 0.24)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.18), (PRAYER, 0.28), (44, 0.5), (SUNRISE, 0.75), (TOTAL, 0.6)])
LANTERNS = Track([(0, 1.0), (16, 1.0), (PRAYER, 0.55), (CRESC, 0.15), (44, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (48.5, 0.0), (52, 0.55), (56, 0.85), (TOTAL, 0.75)])
TRAIL = Track([(0, 0.0), (1.2, 0.5), (PRAYER, 0.6), (SUNRISE, 0.95), (TOTAL, 0.9)])
ZOOM = Track([(0, 1.0), (PRAYER, 0.99), (SUNRISE, 0.98), (TOTAL, 0.965)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 1.6, 1.0), (TOTAL - 0.1, 0.0)])
RAYS = Track([(0, 0.0), (46, 0.0), (SUNRISE, 0.5), (55, 0.75), (TOTAL, 0.7)])
PART = Track([(0, 0.0), (48, 0.0), (52, 1.0), (56, 1.0), (TOTAL, 0.6)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

_OFF = dict(form=1e9, hold=1e9, star=1e9)       # not lit yet in the concert
_LIT = dict(form=1e9, hold=1e9, star=-100.0)    # lit before this minute
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **_OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **_OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **_LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **_OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **_OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **_OFF),
    # Her prayer: "Putting Her hands together, earnestly She prayed..." Lit in song 01, spoken again here.
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=PRAYER + 1.0, hold=PRAYER + 10.5, star=-100.0, arrive=PRAYER + 13.0),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **_OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **_LIT),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit in an earlier song: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
# A light lit earlier and spoken again in this song: star=-100.0 plus form, hold and arrive (when the words reach it).
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (never on screen with an expression). Times are estimates from the studio recording.
FRAGMENTS = [
    dict(text="Her warm hands", t0=8.0, t1=10.5, out=16.5, dy=0.0, size=84, glow="#ffb468"),
    dict(text="courage to go on", t0=42.0, t1=44.0, out=47.2, dy=0.0, size=78),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM · 6720 W Sahara Ave, Las Vegas", t0=53.5, t1=56.5)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="I Reminisce About Your Love", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.4, t_rest=6.4, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky (time, x, y, strength): Encouragement reaching its light, and the end card
WAVES = [(PHRASES[6]["arrive"], STAR_POS[6][0], STAR_POS[6][1], 0.6), (TITLE_HIT, 0.5, 0.62, 1.3)]


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
    """Lines of light only between two neighbouring lights that are both lit (none are neighbours in this song)."""
    out = []
    for i in range(8):
        a, b = PHRASES[i]["star"], PHRASES[i + 1]["star"]
        g = min(max((t - (max(a, b) - 1.2)) / 1.4, 0.0), 1.0) if max(a, b) < 1e8 else 0.0
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
    for tt in (0, 5, 10, 20, 30, 40, 50, 57):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
