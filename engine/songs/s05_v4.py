"""Song 05, God Bless You! (songbook 247): the 1 minute promo v4, in the ORIGINAL engine style.

Direction round 4 (Anthony): "I don't like the dark behind the text ... Make new versions", in the style of the first
engine version (engine/songs/s03_original.py), "according to the song". So: no painted plates, the engine's own
luminous world (sky, still lake, the mountain line and its mirror, the arch of nine lights), glowing gold words
with NOTHING dark behind them (TEXT_SHADOW = 0). Legibility comes from the glow and from keeping the sky behind
the words naturally deep: every palette below was chosen so the sky under the letters stays darker than the
engine's text cap, so the cap never has to dim anything.

Song 05's own look (DESIGN-SYSTEM.md section 6): a spring afternoon full of blessing, fresh green gold, cream and
soft rose, warm haze, blossom petals, pollen of light; no stars, Milky Way, aurora, rain or lanterns. Timed to
audio/promo/s05.mp3 (2:26 to 3:26 of the ver.3 recording: the sister verse, from the prayer for her to the climax).

Five scenes, each its own sky, light, objects and framing:
  1. 0 to 14: apricot late morning (song 04's hand-off) opening into a hazy afternoon over the still lake; pollen of
     light rising; the prayer for her (Encouragement shines again).
  2. 14 to 27: the blossom shore, closer to the water: a rose tinted afternoon, blossom petals drifting thickly,
     the lake perfectly still while the brother listens (Respect, first lit; a provisional exception awaiting
     Anthony, not an exact lyric match).
  3. 27 to 40: the open spring lake, wide and clear: green gold horizon, rays of the afternoon sun, pollen
     everywhere; the offer of help (Consideration, lit in the brother verse, shines again); a small pair of
     light carrying a load together crosses the far hills on the right and rises into light.
  4. 40 to 50: the sun breaks through: haze gathers, then parts in the middle, the sun surges with rays, a column
     of sunlight falls to the water on the left, and "God bless you!" forms of blossom petals, then the wind
     blows it away.
  5. 50 to 60: warm late afternoon (handed to song 06) under the three-line end card.
Line times inside the minute are estimates from loudness (the sung guide alignment is still to do).
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
HORIZON = 0.27         # water line: a little lower than other songs, for an open, airy sky

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
        # earnest prayer, careful listening and the offer of help: the lake falls still (no rings) under the words
        keep = [k for k in keep if not any(a <= k[0] < b for a, b in STILL)]
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

# Landmarks inside the promo minute (seconds; promo time = recording time minus 146).
# Measured: breaths near 12 to 15 and 24 to 26, climax 44 to 58 (loudest of the song), fade from 58.
# Reading time contract: formation takes about 3.75 s, so hold = form + 9.75 gives 6 s fully formed.
READ = 9.75
ENC_FORM = 2.6         # Encouragement: the prayer for her (lit in song 01, shines again)
RESPECT_FORM = 15.5    # Respect: the brother stops and listens to his sister (first lit; provisional exception)
CONS_FORM = 28.4       # Consideration: the offer of help to her (lit in the brother verse, shines again)
FRAG_T0 = 41.4         # "God bless you!" in blossom petals, as the sun begins to break through
SUNRISE = 42.0         # the climax: the afternoon sun breaks through the haze
NINTH = 1e9            # no whole-arch glow in this song
TITLE_HIT = 52.1       # end card: the lines are fully formed at 55.1 and hold 4.9 s before the fade
SKYLINE_LANTERN = 0.0  # no small light travelling along the drawn skyline
BOTTOM_CALM = 1.0      # calm lower third for the performers
TEXT_SHADOW = 0.0      # round 4: nothing dark behind any text (no veil, no halo, no band)
TEXT_PROTECT = 1.0     # petals and pollen still part round the letters (this only removes light, never darkens)
WORDS_Y = 0.35         # centre of the expressions, a little high, where the spring sky is deepest
# Star history before this minute (DESIGN-SYSTEM.md 12a): Apology lit in 03 and relit in 04 (one ring);
# Encouragement lit in 01, relit in 02, 03 and in this song's brother verse (three rings).
RINGS_AT_START = {2: 1, 6: 3}
# While prayer, listening and the offer of help are on screen the lake falls perfectly still
STILL = [(ENC_FORM - 0.5, ENC_FORM + 11.0), (RESPECT_FORM - 0.5, RESPECT_FORM + 11.0), (CONS_FORM - 0.5, CONS_FORM + 11.0)]

# Sky palettes (top, middle, horizon, glow of the sun). Spring afternoon, kept deep blue above the horizon band so
# gold words glow on it; the cream, rose and green gold live in the haze along the water.
PAL = {
    "apricot": ("#10285e", "#264680", "#d89874", "#ffd8a8"),   # song 04's apricot late morning, warming
    "haze":    ("#10295f", "#284882", "#c8a888", "#ffe2b8"),   # soft hazy afternoon
    "rose":    ("#16245e", "#33407e", "#c68a98", "#ffd0c0"),   # blossom shore: rose tint of blossoms in the haze
    "clear":   ("#0a2662", "#1e4a8e", "#a0b07c", "#fff2c8"),   # the open lake: clear spring blue, green gold haze
    "bless":   ("#10306e", "#28528e", "#d0bc90", "#fff6d8"),   # the sun breaks through: full blessing light
    "golden":  ("#122a60", "#28447a", "#7e5a4a", "#ffd8a0"),   # warm late afternoon, handed to song 06
}
_pal_keys = [(0.0, "apricot"), (6.0, "apricot"), (12.5, "haze"), (13.8, "haze"), (15.4, "rose"), (26.6, "rose"),
             (28.3, "clear"), (38.5, "clear"), (41.5, "bless"), (47.0, "bless"), (51.0, "golden"), (TOTAL, "golden")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# The sun rests low in the haze over the water; at the climax it surges and breaks through
SUN_INT = Track([(0, 0.45), (13.8, 0.42), (15.4, 0.32), (26.6, 0.32), (28.3, 0.42), (38.5, 0.42), (41.2, 0.30),
                 (42.2, 0.90), (44.5, 0.95), (47.5, 0.70), (51.0, 0.22), (TOTAL, 0.22)])
SUN_Y = Track([(0, 0.285), (TOTAL, 0.28)])
SUN_SIZE = Track([(0, 0.075), (41.0, 0.075), (43.5, 0.095), (48.5, 0.09), (51.5, 0.075), (TOTAL, 0.075)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
# haze: low and light under the words; thick just before the break through, then parted in the middle
CLOUDS = Track([(0, 0.35), (13.8, 0.30), (15.4, 0.40), (26.6, 0.40), (28.3, 0.12), (37.5, 0.12), (40.5, 0.75),
                (44.0, 0.70), (49.0, 0.35), (TOTAL, 0.30)])
PART = Track([(0, 0.0), (41.4, 0.0), (43.6, 1.0), (49.0, 1.0), (52.0, 0.6), (TOTAL, 0.6)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# pollen of light: gentle in the opening, everywhere on the open lake, a burst as the sun breaks through
MOTES = Track([(0, 0.10), (2.5, 0.28), (13.8, 0.28), (15.4, 0.14), (26.6, 0.14), (28.3, 0.55), (38.5, 0.55),
               (41.0, 0.30), (43.0, 0.65), (48.0, 0.55), (52.0, 0.30), (TOTAL, 0.28)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
# blossom petals: a few at first, thick on the blossom shore, swirling at the climax, slow under the end card
PETALS = Track([(0, 0.08), (13.8, 0.12), (15.6, 0.85), (26.4, 0.85), (28.4, 0.12), (39.0, 0.12), (42.0, 0.9),
                (47.5, 0.9), (51.0, 0.35), (TOTAL, 0.3)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
# framing: wide opening, closer to the water on the blossom shore, wide again for the open lake, a slow push in
# as the sun breaks through, settling wide for the end card
ZOOM = Track([(0, 1.0), (13.8, 1.0), (15.6, 1.09), (26.6, 1.11), (28.4, 1.0), (40.0, 1.0), (47.0, 1.05),
              (51.5, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (59.7, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.25), (13.8, 0.25), (15.4, 0.05), (26.6, 0.05), (28.3, 0.55), (38.5, 0.55), (41.0, 0.2),
              (42.5, 0.8), (47.5, 0.7), (51.5, 0.25), (TOTAL, 0.25)])
FLASH = Track([(0, 0.0), (41.9, 0.0), (42.4, 0.22), (44.0, 0.0), (TOTAL, 0.0)])
# spring colors: soft rose and cream blossom petals, green gold pollen of light drifting gently upward
PETAL_COLORS = ("#ffa9bf", "#fff0e2")
MOTE_COLORS = ("#f0f0a8", "#fff4d6")
MOTE_Y = (-0.05, 1.05)

# B. People of light: one brief appearance, small, always moving, never under the words: on the far hills at the
# right, a pair of light carrying a load together walks to the right (about 0.06 of the width per second, about
# 80 px per second at 720p), then rises from the hills and dissolves into light.
FIGURES = [
    dict(poses=["assets/figures/consideration_b.png"], t0=32.4, t1=36.0, gather=1.0, dissolve=1.8,
         leave="drift", x=(0.70, 0.96), move=(32.4, 36.6), ease="linear", bob=1.0,
         y=Track([(32.4, 0.345), (35.0, 0.345), (36.6, 0.46), (37.8, 0.52)]), height=0.10, color="#ffc8d4",
         glow=0.85),
]

# C. Signature moment: the afternoon sun breaking through. A column of sunlight falls through the parted haze onto
# the water at the left, well clear of the words, and is gone before the end card.
BEAM_FROM = (0.10, 1.04)
BEAM_TO = (0.27, 0.29)
BEAM_WIDTH = (0.04, 0.14)
BEAM = Track([(0, 0.0), (SUNRISE, 0.0), (43.5, 0.9), (47.0, 0.9), (49.5, 0.0), (TOTAL, 0.0)])
BEAM_COLOR = "#fff0c8"

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    # Lit before this minute (DESIGN-SYSTEM.md 12a): 3 Apology, 4 Inclusiveness, 7 Encouragement, 9 Compliment,
    # and 8 Consideration (first lit in this song's brother verse, before the promo minute starts).
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    # Respect, lit here for the first time: the brother stops and listens (provisional exception, see the doc)
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=120, y=WORDS_Y,
         form=RESPECT_FORM, hold=RESPECT_FORM + READ, star=RESPECT_FORM + READ + 1.2),
    # Encouragement: the prayer for her makes it shine again
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=112,
         y=WORDS_Y, form=ENC_FORM, hold=ENC_FORM + READ, star=-100.0, arrive=ENC_FORM + READ + 1.2),
    # Consideration: the offer of help to her; it shines again
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=120, y=WORDS_Y,
         form=CONS_FORM, hold=CONS_FORM + READ, star=-100.0, arrive=CONS_FORM + READ + 1.2),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
# the end card sits a little higher than usual so all three lines stay on deep sky
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9, y=0.275)
# D. Signature moment: the song's blessing, formed of blossom petals as the sun breaks through, then blown away
FRAGMENTS = [
    dict(text="God bless you!", t0=FRAG_T0, t1=FRAG_T0 + 3.0, out=FRAG_T0 + 6.0, dy=0.07, size=150,
         glow="#ffb070", style="petals", colors=("#ffa9bf", "#fff0e2")),
]

# The three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 3.0)

# Opening title card that then rests, small, in the top left corner (moved away before the first words)
CREDIT = dict(song="God Bless You!", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=0.8, t_move=1.4, t_rest=2.4, scale=0.34, alpha_rest=0.58,
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(39.6, 40.6, t))   # gone before the bright climax (no dark round it)
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of peace that cross the sky when a light is lit or shines again (time, x, y, strength):
# after each practiced word the scene visibly settles from unrest into stillness and warmth
WAVES = [(ENC_FORM + READ + 1.2, STAR_POS[6][0], STAR_POS[6][1], 0.6),
         (RESPECT_FORM + READ + 1.2, STAR_POS[5][0], STAR_POS[5][1], 0.8),
         (CONS_FORM + READ + 1.2, STAR_POS[7][0], STAR_POS[7][1], 0.85),
         (TITLE_HIT, 0.5, 0.62, 1.2)]


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
    for tt in (0, 3, 6, 12, 20, 30, 40, 46, 53, 58):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
