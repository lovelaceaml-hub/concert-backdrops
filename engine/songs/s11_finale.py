"""Song 11, Almighty God Who Knows the Future (the finale): the 1 minute promo.

Design: Designs/11 Almighty God Who Knows the Future - Video Design (Google Doc, version 3), "The Gate of Mother's Love".
This minute is the heart of the finale: the morning hush after verse 1, Heavenly Mother telling her children to
trust Father and march ahead (Encouragement shines again in its light), the second lift as all nations run to Zion,
and the full arch of nine lights glowing as the glory of the finale. Promo audio: audio/promo/s11.mp3.

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
HORIZON = 0.38         # water line, high: grand framing with a wide golden lake (song 11 look)

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


# ---------------------------------------------------------------- promo timeline
# The promo is 1:59 to 2:59 of the studio recording (song second = promo second + 119.0). Lyric times are measured
# word times from a speech-to-text pass of the recording (2026-11-13), not estimates.
CLIP_START = 119.0
MOTHER = 121.2 - CLIP_START      # verse 2 begins: Mother, who planned the future
MARCH = 129.9 - CLIP_START       # her words to trust Father and march ahead
HOPE = 141.3 - CLIP_START        # hope engraved in every heart, now fulfilled
KINGS = 150.6 - CLIP_START       # all kings worship and run to the Church of God
LIFT = 160.5 - CLIP_START        # the second lift (measured step up in loudness)
JOY = 162.1 - CLIP_START         # joy of salvation
FOREVER = 165.5 - CLIP_START     # endures forever
TITLE_HIT = 52.4                 # end card
NINTH = LIFT                     # the whole arch glows from the second lift on: the finale's glory
ENC_FORM = MARCH + 0.6

# Song 11 look (DESIGN-SYSTEM.md section 6): a radiant full sunrise, the brightest scene of the night. White gold,
# sky blue and all nine colors; full rays; a clear sky; the complete arch; grand framing with a high horizon.
# Not first light (song 01) and not a blossom afternoon (song 05): a blazing white-gold sun on a wide golden lake.
NINE = ["#FF977C", "#FFD05F", "#FFAD69", "#F582AF", "#82B0ED", "#CE927E", "#B293E7", "#EF7A96", "#BE9CEB"]


def _nine_pair(rate, offset):
    def f(t):
        k = int(t * rate + offset) % 9
        return (NINE[k], NINE[(k + 4) % 9])
    return f


# Scene palettes (top of sky, middle, horizon, glow of the sun)
PAL = {
    "clear":   ("#123f86", "#3f7fc8", "#ffd6a2", "#fff1d6"),   # clear morning, the sun just risen
    "mother":  ("#143f88", "#4682cb", "#ffd9ad", "#fff3dc"),   # Mother speaks: the same clear blue, warmer horizon
    "radiant": ("#164a98", "#4f90d6", "#ffe2b6", "#fff6e6"),   # the road of light, full rays
    "glory":   ("#1a56a8", "#5a9ade", "#ffecc8", "#fffaf0"),   # second lift: full daylight glory, white gold
}
_pal_keys = [
    (0.0, "clear"), (MOTHER + 3.0, "clear"), (MARCH, "mother"), (MARCH + 9.0, "radiant"), (KINGS, "radiant"),
    (LIFT, "glory"), (TOTAL, "glory"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# a big white-gold sun that climbs clear of the mountains; softened while words are on screen so they stay readable
SUN_INT = Track([(0, 0.95), (MARCH, 1.00), (MARCH + 4, 1.05), (ENC_OUT := MARCH + 11.0, 1.10), (HOPE + 2, 1.30),
                 (KINGS, 1.40), (LIFT, 1.45), (JOY - 1.0, 1.15), (FOREVER + 3, 1.15), (TITLE_HIT - 2, 1.05), (TOTAL, 1.0)])
SUN_Y = Track([(0, 0.405), (MARCH, 0.42), (HOPE, 0.45), (KINGS, 0.47), (LIFT, 0.50), (TITLE_HIT, 0.53), (TOTAL, 0.54)])
SUN_SIZE = Track([(0, 0.14), (LIFT, 0.16), (TOTAL, 0.17)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.14), (TOTAL, 0.10)])                       # a clear sky
# a soft veil of all nine colors high in the sky
AURORA = Track([(0, 0.10), (MARCH, 0.14), (MARCH + 4, 0.24), (HOPE, 0.20), (LIFT, 0.30), (TITLE_HIT, 0.26), (TOTAL, 0.24)])
AURORA_WARM = _nine_pair(0.18, 0)
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.30), (MARCH, 0.40), (HOPE, 0.55), (KINGS, 0.70), (LIFT, 0.85), (TITLE_HIT, 0.60), (TOTAL, 0.55)])
MOTE_COLORS = ("#fff6e2", "#ffe2a0")                            # white gold
# lights in all nine colors rising from the land: the peoples of every nation streaming toward Zion
LANTERNS = Track([(0, 0.0), (HOPE, 0.0), (HOPE + 4, 0.45), (KINGS, 0.75), (LIFT, 0.95), (LIFT + 6, 0.80),
                  (TITLE_HIT, 0.35), (TOTAL, 0.25)])
LANTERN_COLORS = _nine_pair(0.5, 2)
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.5), (MARCH, 0.7), (LIFT, 1.0), (TOTAL, 0.9)])
ZOOM = Track([(0, 1.0), (MARCH, 0.99), (LIFT, 0.968), (TOTAL, 0.952)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 1.6, 1.0), (TOTAL - 0.2, 0.0)])
# full rays, eased back while words are on screen
RAYS = Track([(0, 0.35), (MARCH - 0.5, 0.40), (MARCH + 1.0, 0.30), (ENC_OUT, 0.32), (ENC_OUT + 3, 0.80), (KINGS, 0.95),
              (LIFT, 1.0), (JOY - 1.0, 0.50), (FOREVER + 3, 0.50), (TITLE_HIT - 3.4, 0.40), (TOTAL, 0.38)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = dict(form=1e9, hold=1e9, star=-100.0)     # lit in an earlier song (all nine are lit before the finale)
PHRASES = [
    # label, lines, max font px, form start, hold end, star time
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    # Encouragement shines again: Heavenly Mother tells her children to trust Father and march ahead
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_FORM + 9.0, star=-100.0, arrive=ENC_FORM + 11.0),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit in an earlier song: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
# A light lit earlier and spoken again in this song: star=-100.0 plus form, hold and arrive (when the words reach it).
# End card of the promo
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments (design fragment 3 in its two stages): text, t0, t1, out, dy, size
FRAGMENTS = [
    dict(text="Joy of salvation", t0=JOY - 0.3, t1=JOY + 1.2, out=FOREVER - 0.6, dy=0.0, size=150, alpha=1.0, glow="#ffb46a"),
    dict(text="endures forever", t0=FOREVER + 0.2, t1=FOREVER + 1.4, out=TITLE_HIT - 3.4, dy=0.0, size=150, alpha=1.0, glow="#ffb46a"),
]

TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nThe World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas", t0=TITLE_HIT + 1.5, t1=TITLE_HIT + 4.0)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Almighty God Who Knows the Future", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=5.2, t_rest=7.0, scale=0.34, alpha_rest=0.58,
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
# Encouragement reaching its light again, and the whole arch answering the second lift
WAVES.append((PHRASES[6]["arrive"], STAR_POS[6][0], STAR_POS[6][1], 0.7))
WAVES.append((LIFT, 0.5, 0.86, 0.9))


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
        t1 = PHRASES[i + 1]["star"]
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
    for tt in (0, 5, 12, 20, 30, 42, 50, 57):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
