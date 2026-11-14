"""Song 03, I Reminisce About Your Love: 1 minute promo v4 in the ORIGINAL style (Direction round 4).

The world of the first engine version (engine/songs/s03_original.py, the one Anthony loves): a deep sky full of
stars, a still lake with the mountain line drawn from the music's loudness and its mirror, the warm light that
travels along that skyline, aurora, motes, falling stars, rings on the water and the arch of nine lights across
the top. No painted plates, no people. Words are glowing gold light on the sky with nothing dark behind them.

Clip: studio recording 3:14 to 4:14 (audio/promo/s03.mp3), timings and star history as in s03_lake_of_memory.py:
Her warm hands, Her prayer (Encouragement, relit), the crescendo of courage, the rose sunrise of chorus 2.
Arch state at this point of the song: 3 (Apology, lit earlier in this song), 7 and 9 lit; light 7 carries one ring.
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

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402

# Promo v4 (original style). Five scenes, all from the engine's own layers, told by sky, light and framing:
#   1  0 to 9     The last rain: an indigo storm night low over the water, clouds and rain, rings on the lake,
#                 the title card. The rain thins and stops (studio 3:14).
#   2  8 to 24    Her warm hands: the clouds open on a violet night; a warm rose gold aurora rises like hands
#                 held over the lake, sky lanterns float up, "Her warm hands" rises out of the water.
#   3  22 to 40   Her prayer: the deepest, stillest night. The Milky Way, cool aurora only a thread, a low moon
#                 over the lake, the camera closer. ENCOURAGEMENT forms (about 7 s solid) and its words fly to
#                 light 7 (flare, wave, a new ring).
#   4  39 to 49   The mended sky: the sky above the words breaks into glass and drifts back together held by
#                 gold seams, the horizon turns rose; "courage to go on" written by a pen of light.
#   5  47 to 60   The rose dawn: the sun rises over the water with soft rays, rose petals, the camera wide again,
#                 the closing title and the three-line end card on a sky kept deep (sun low behind the hills) (fully formed by about 55.5, held to 60).

# Landmarks in the promo clip (seconds into the clip; studio time minus 194 s), as in s03_lake_of_memory.py
HANDS = 4.0          # 3:18 "I used to feel Her warm hands" (measured step up)
PRAYER = 28.0        # 3:42 "Putting Her hands together" (measured step up)
CRESC = 38.0         # 3:52 crescendo, "sowed courage to go on"
SUNRISE = 50.0       # 4:04 chorus 2 arrives (measured)
NINTH = 1e9          # the whole arch does not glow in this song
TITLE_HIT = 51.0     # end card

ENC_FORM, ENC_HOLD = 27.0, 37.8   # Encouragement: formed by 30.75, solid until 37.8 (about 7 seconds)
ENC_ARRIVE = 40.3                 # its words reach light 7

BOTTOM_CALM = 1.0         # calm lower third for the performers
RINGS_AT_START = {6: 1}   # light 7 earned one ring when song 02 spoke the Encouragement again

# Direction round 4: nothing dark behind any text. No veil, no halo, no band; the glow carries the words and the
# sky behind them is kept naturally deep.
TEXT_SHADOW = 0.0
TEXT_PROTECT = 0.0

# Palettes (top of sky, middle, horizon, glow of the low sun or moon). DESIGN-SYSTEM.md section 6, row 03:
# indigo night of memory, rain, then a rose dawn.
PAL = {
    "storm":   ("#020310", "#070a28", "#171c48", "#8e98e8"),
    "hands":   ("#04041a", "#151446", "#4a3474", "#ffb49a"),
    "prayer":  ("#01030d", "#050c2a", "#13244e", "#a8c4ff"),
    "predawn": ("#070a26", "#2a2152", "#9a5470", "#ffb894"),
    "dawn":    ("#0b1238", "#382a60", "#b25e70", "#ffcc98"),
}
_pal_keys = [(0.0, "storm"), (7.0, "storm"), (13.0, "hands"), (20.5, "hands"), (25.5, "prayer"), (38.5, "prayer"),
             (44.5, "predawn"), (49.0, "predawn"), (53.0, "dawn"), (TOTAL, "dawn")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the low light: hidden in the storm, a warm glow under the aurora, a cool moon at the prayer, then the sun
SUN_INT = Track([(0, 0.06), (8, 0.10), (14, 0.30), (21, 0.30), (25, 0.42), (38, 0.46), (44, 0.40), (48, 0.55),
                 (SUNRISE, 0.62), (54, 0.62), (TOTAL, 0.60)])
SUN_Y = Track([(0, 0.25), (21, 0.26), (25, 0.33), (38, 0.345), (44, 0.29), (48, 0.27), (54, 0.30), (TOTAL, 0.305)])
SUN_SIZE = Track([(0, 0.10), (25, 0.085), (38, 0.085), (46, 0.10), (54, 0.105), (TOTAL, 0.105)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.35), (8, 0.35), (13, 0.9), (24, 1.0), (38, 1.0), (45, 0.7),
               (50, 0.35), (54, 0.18), (TOTAL, 0.16)])
MILKY = Track([(0, 0.0), (20, 0.0), (26, 0.95), (38, 0.9), (44, 0.2), (48, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.85), (6, 0.8), (12, 0.25), (24, 0.15), (40, 0.15), (46, 0.45), (52, 0.55), (TOTAL, 0.5)])
AURORA = Track([(0, 0.0), (9, 0.0), (13, 0.42), (17, 0.58), (21, 0.42), (26, 0.10), (38, 0.10), (44, 0.22),
                (50, 0.30), (54, 0.20), (TOTAL, 0.18)])
RAIN = Track([(0, 0.75), (4.5, 0.6), (7.5, 0.15), (9.0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.06), (2, 0.14), (12, 0.30), (24, 0.24), (36, 0.30), (44, 0.42), (SUNRISE, 0.55), (54, 0.35),
               (TOTAL, 0.32)])
LANTERNS = Track([(0, 0.0), (9.0, 0.0), (12.0, 0.65), (19.0, 0.65), (23.5, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (47.0, 0.0), (50.0, 0.55), (52.5, 0.25), (TOTAL, 0.2)])
TRAIL = Track([(0, 0.0), (1.2, 0.55), (24, 0.6), (40, 0.8), (SUNRISE, 1.0), (TOTAL, 0.9)])
# framing: low over the water, closer for the prayer, wide again at dawn
ZOOM = Track([(0, 1.0), (8, 0.99), (22, 0.975), (28, 0.955), (38, 0.95), (46, 0.965), (54, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (59.0, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (48.0, 0.0), (51.0, 0.34), (55.0, 0.28), (TOTAL, 0.26)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

# Scene 4: the upper sky breaks into glass after the prayer and drifts back together, mended with gold
SHARDS = Track([(0, 0.0), (39.8, 0.0), (41.0, 1.0), (42.2, 1.0), (44.6, 0.0), (TOTAL, 0.0)])
SHARDS_MEND = Track([(0, 0.0), (41.5, 0.0), (43.5, 0.9), (46.5, 0.6), (49.0, 0.0), (TOTAL, 0.0)])
SHARDS_Y = 0.66           # only above the words
SHARDS_COLOR = "#ffd27a"

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
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **_LIT),   # lit earlier in 03
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **_OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **_OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **_OFF),
    # Her prayer: lit in song 01, spoken again here
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **_OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **_LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)

# Short lyric fragments (never on screen with an expression). Times are estimates from the studio recording.
FRAGMENTS = [
    # rises out of the lake under the warm aurora, then rests
    dict(text="Her warm hands", t0=10.4, t1=13.4, out=17.0, dy=0.11, size=92, glow="#ffb468",
         style="reflection", line=HORIZON),
    # under the mended sky
    dict(text="courage to go on", t0=40.4, t1=43.2, out=46.4, dy=-0.04, size=88, glow="#ffc070", style="write"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.2, t1=TITLE_HIT + 3.4)

# Colors: rose gold warm aurora (Her hands), indigo and violet cool aurora, rose petals, gold lanterns
AURORA_COOL = ("#6f7cff", "#a58cff")
AURORA_WARM = ("#ffa29a", "#ffcc8c")
PETAL_COLORS = ("#ff8fae", "#ffd6b0")
LANTERN_COLORS = ("#ffc070", "#ff9a5a")
MOTE_COLORS = ("#ffe0a8", "#ffa8b8")

# Opening title card that then rests, small, in the top left corner, and fades before the end card
CREDIT = dict(song="I Reminisce About Your Love", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.4, t_rest=6.4, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_out=(49.0, 50.6))


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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_out"][0], c["t_out"][1], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky (time, x, y, strength): Encouragement reaching its light, and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.6), (TITLE_HIT, 0.5, 0.62, 1.0)]


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
