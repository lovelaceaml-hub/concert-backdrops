"""Song 07, May No One Ever Feel Lonely: 1 minute promo v4 in the ORIGINAL style (direction round 4).

Anthony (round 4): "I don't like the dark behind the text ... make new versions" in the style of the first engine
version (engine/songs/s03_original.py), "according to the song". So no painted plates and no dark behind any
words (TEXT_SHADOW = 0): the engine's own luminous world (deep sky, first stars, a still lake under a low line of
hills and its mirror, mist, motes, the arch of nine lights), in song 07's own look from DESIGN-SYSTEM.md section 6:
blue dusk on a long path home, twilight blue, coral, lantern gold, lanterns, first stars, mist, deep perspective.

The story is carried by light alone (no people of light in this version):
  1. The lone light (0 to 13): blue dusk, one small warm light on the dark hills, alone; the first stars come out.
  2. Mother's wish lights the way (13 to 26): Her star rises at the horizon, its rays reach out, and the path of
     light runs from the lone light along the whole line of hills toward home (the lit path).
  3. "How are you?" (26 to 38): deep blue night full of stars, framed close; star 1 is lit for the first time.
  4. "Can I give you a hand with anything?" (38 to 50): the windows answer one by one: warm lights wake one after
     another along the far hills while the village's lanterns rise; star 8 (lit in song 05) is relit.
  5. The gate of light (50 to 60): navy night, the lone light reaches the gate, a column of light from above
     lands on it, and the end card forms over the still lake.
Studio recording 0:24 to 1:24 (audio/promo/s07.mp3).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.path.splitext(os.path.basename(__file__))[0]
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))
_SONG = None

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5       # last sounding moment of the promo clip
SONG_END = 60.0        # length of the promo clip
TOTAL = 60.0           # promo length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.36         # water line: a higher horizon gives the long, deep view down the path home

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
        self.ridge = np.maximum(self.ridge, 0.006)
        # v4: keep the far hills low and broad (original look), so the sky behind the words stays open and deep
        r = self.ridge * 0.6
        self.ridge = (r / (1.0 + r / 0.06)).astype("f4")
        global _SONG
        _SONG = self
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

    def ridge_y(self, x):
        return HORIZON + float(np.interp(x, np.linspace(0, 1, 2048), self.ridge))

    def lantern(self, t):
        # v4: the lone light walks its own way along the hills (LANTERN_X), not at the speed of the clip
        x = float(LANTERN_X(t))
        return x, self.ridge_y(x)

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

# Promo landmarks (seconds into the 60 second clip, which starts at 0:24 of the studio recording).
# Measured: first big lift at 29.0 (0:53), short gap at 54.0 (1:18). Estimated: Mother's first wish about 2 to 13,
# the earnest wish line about 14 to 28, the promise from 29, the care line about 41 to 53.
# Reading time: formation takes 3.75 s, then at least 6 s solid, a 1.6 s dissolve before the next text.
G_FORM, G_HOLD = 26.0, 35.8            # Greeting: solid 29.75 to 35.8 (6.05 s)
C_FORM, C_HOLD = 37.9, 47.7            # Consideration: solid 41.65 to 47.7 (6.05 s)
NINTH = 1e9                            # no whole-arch glow in this promo
TITLE_HIT = 52.8                       # title forms from 49.8; the whole end card from about 55.4
BOTTOM_CALM = 1.0                      # calm lower third for the performers
TEXT_SHADOW = 0.0                      # round 4: nothing dark behind any text; legibility from glow and deep sky
# TEXT_PROTECT dims the floating lights (motes, lanterns, beam, star glow) behind letters before the glow is
# blurred. At full strength it cut a dark trail through the glow where words fly up to their light (stills r3,
# 38.5 s), so it is moderate while words are held and low while they fly to the arch.
TEXT_PROTECT = Track([(0, 0.6), (35.6, 0.6), (36.2, 0.15), (39.6, 0.15), (40.4, 0.6), (47.5, 0.6), (48.1, 0.15),
                      (50.4, 0.15), (51.2, 0.6), (TOTAL, 0.6)])

# Star history (CONTINUITY-BOARD.md): rings earned before song 07. Apology relit in song 04, Inclusiveness relit
# in song 06, Encouragement relit in songs 02, 03 and 05. Song 07 lights 1 (first time) and relights 8.
RINGS_AT_START = {2: 1, 3: 1, 6: 3}

# Scene palettes (top of sky, middle, horizon, glow of the horizon star). Kept deep at the height of the words.
PAL = {
    "dusk":    ("#0e1a3c", "#2a3a70", "#c98272", "#ffb98e"),   # 1. blue dusk, coral horizon
    "wish":    ("#0a1434", "#262c66", "#b7707c", "#ffd49a"),   # 2. Her star rises: violet blue, gold glow
    "night":   ("#03071a", "#0a1438", "#1e3266", "#a9c4ff"),   # 3. deep blue night, cool light
    "village": ("#060c26", "#151f4c", "#6e4a6a", "#ffbe72"),   # 4. night with warm lantern light low
    "home":    ("#0b1530", "#17255a", "#7c5470", "#ffe0a8"),   # 5. navy #0B1530 (agreed with 08), gate gold
}
_pal_keys = [
    (0.0, "dusk"), (11.5, "dusk"), (15.5, "wish"), (24.0, "wish"), (28.0, "night"), (36.5, "night"),
    (40.0, "village"), (48.5, "village"), (52.0, "home"), (TOTAL, "home"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# Mother's star at the horizon: faint at dusk, rises in scene 2, small and cool at night, the gate at the end
SUN_INT = Track([(0, 0.22), (11.0, 0.24), (15.0, 0.60), (19.0, 0.95), (24.0, 0.85), (28.0, 0.18), (37.0, 0.18),
                 (41.0, 0.32), (48.0, 0.40), (52.0, 0.75), (TOTAL, 0.70)])
SUN_Y = Track([(0, 0.345), (13.0, 0.35), (20.0, 0.385), (26.0, 0.38), (30.0, 0.36), (48.0, 0.36),
               (54.0, 0.37), (TOTAL, 0.37)])
SUN_SIZE = Track([(0, 0.09), (13.0, 0.10), (20.0, 0.125), (28.0, 0.08), (48.0, 0.09), (54.0, 0.11), (TOTAL, 0.11)])
# the first stars come out one by one; the night of scene 3 is full of them
STARS = Track([(0, 0.0), (0.5, 0.0), (5.0, 0.25), (12.0, 0.45), (20.0, 0.55), (27.0, 0.95), (37.0, 1.0),
               (44.0, 0.85), (52.0, 0.75), (TOTAL, 0.75)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
# soft mist: dusk haze that clears as night falls (lit night clouds left patchy shapes near the words in stills r2)
CLOUDS = Track([(0, 0.45), (12.0, 0.40), (20.0, 0.22), (26.0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.05), (10.0, 0.08), (16.0, 0.20), (24.0, 0.22), (28.0, 0.12), (38.0, 0.16), (44.0, 0.34),
               (52.0, 0.36), (TOTAL, 0.30)])
# the village's lanterns rise as the windows answer (scene 4) and keep floating up toward the gate
LANTERNS = Track([(0, 0.0), (40.5, 0.0), (44.0, 0.55), (48.0, 0.85), (53.0, 0.60), (TOTAL, 0.45)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
# the lit path: dark behind the lone light at first, then Mother's wish lights the whole line of hills ahead
TRAIL = Track([(0, 0.0), (15.5, 0.0), (18.0, 1.7), (26.0, 1.6), (30.0, 1.2), (40.0, 1.3), (47.0, 1.8),
               (TOTAL, 1.8)])
# framing: wide at dusk, a slow push toward Her star, close in the night of the Greeting, wide again over the
# village, a gentle push home at the end
ZOOM = Track([(0, 1.0), (12.0, 0.985), (24.0, 0.955), (27.5, 0.93), (36.5, 0.915), (40.5, 0.99), (48.0, 0.985),
              (TOTAL, 0.975)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.2, 1.0), (59.2, 1.0), (59.95, 0.0)])
RAYS = Track([(0, 0.0), (14.0, 0.0), (18.0, 0.55), (24.0, 0.45), (28.0, 0.0), (51.0, 0.0), (55.0, 0.18),
              (TOTAL, 0.18)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = ("#ffd27a", "#ffb04f")      # lantern gold
MOTE_COLORS = ("#ffe6b0", "#ff9d86")         # gold and coral sparks

# The lone light: where it walks along the hills (fraction of the width). Alone and slow at dusk, onward on the
# lit path, at the centre under the Greeting, on through the village, and home to the gate at the right.
LANTERN_X = Track([(0, 0.10), (13.0, 0.20), (26.0, 0.32), (38.0, 0.48), (48.0, 0.66), (53.2, 0.895),
                   (TOTAL, 0.90)])
SKYLINE_LANTERN = Track([(0, 1.0), (13.0, 1.0), (18.0, 1.35), (TOTAL, 1.35)])
# how far the path of light reaches along the hills: just behind the lone light, then (Mother's wish, 16 to 21.5)
# ahead to Her star at the centre; then (the windows answer, 41 to 47) on to the far end, one stretch at a time
WINDOWS = [(41.2, 0.60), (42.4, 0.68), (43.6, 0.76), (44.8, 0.84), (46.0, 0.92)]
_prog = [(0, 0.10), (16.0, 0.205), (21.5, 0.53)]
for _tw, _x in WINDOWS:
    _prog += [(_tw - 0.35, _prog[-1][1]), (_tw + 0.25, _x)]
_prog += [(47.5, 0.975), (TOTAL, 0.975)]
PROG = Track(_prog)

# The gate of light: a column of light from above onto the lone light at the end of the path, right of the card
BEAM = Track([(0, 0.0), (49.0, 0.0), (51.5, 0.55), (53.5, 0.55), (55.5, 0.24), (TOTAL, 0.24)])
GATE_X = 0.90   # right of the end card's widest line (0.17 to 0.83)


def BEAM_FROM(t):
    return (GATE_X + 0.02, 0.80)


def BEAM_TO(t):
    y = _SONG.ridge_y(GATE_X) if _SONG is not None else HORIZON + 0.03
    return (GATE_X, y + 0.004)


BEAM_WIDTH = (0.02, 0.04)
BEAM_COLOR = "#ffdcaa"

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = -100.0
NOT_YET = 1e9
PHRASES = [
    # Greeting: lit for the first time in the concert, at the first big lift (the answer to Mother's wish)
    dict(label="Greeting", lines=["“How are you?”"], size=164, form=G_FORM, hold=G_HOLD, star=G_HOLD + 2.0),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=NOT_YET, hold=NOT_YET, star=NOT_YET),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=NOT_YET, hold=NOT_YET, star=LIT),
    # Consideration: lit in song 05, spoken again here at the promise to care for brothers and sisters
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         form=C_FORM, hold=C_HOLD, star=LIT, arrive=C_HOLD + 2.0),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=NOT_YET, hold=NOT_YET, star=LIT),
]
FORM_DUR = 3.0
# y=0.272 (engine default 0.315) lifts the whole end card a little, so its last line clears the lit hills
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.272, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments: Mother's wish written by a pen of light, and the refrain rising out of the lake;
# never on screen together with an expression
FRAGMENTS = [
    dict(text="“on the path to heaven”", t0=5.4, t1=8.4, out=11.2, size=92, glow="#ffe4c0", style="write"),
    dict(text="our Mother’s earnest wish", t0=15.5, t1=19.5, out=23.2, size=84, glow="#ffd6b8",
         style="reflection"),
]

# the three-line end card
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.8, t1=TITLE_HIT + 2.6)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="May No One Ever Feel Lonely", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=3.8, t_rest=5.4, scale=0.34, alpha_rest=0.58,
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


# Waves of light: star 1 lit (soft: it sits beside the corner credit), star 8 relit, the title. Signature "the
# windows answer one by one": at each WINDOWS time a warm light wakes on the far hills and the path of light runs
# on to it (PROG above), stretch by stretch, to the far end.
WAVES = [(PHRASES[0]["star"], STAR_POS[0][0], STAR_POS[0][1], 0.18),
         (PHRASES[7]["arrive"], STAR_POS[7][0], STAR_POS[7][1], 0.6),
         (TITLE_HIT, 0.5, 0.62, 0.3)]   # soft: a strong bloom behind the card brightens the sky under it


def _windows(t, song):
    out = []
    for tw, x in WINDOWS:
        if 0.0 <= t - tw < 3.1:   # at most 4 waves draw at once: keep each window short
            y = song.ridge_y(x) + 0.012
            out.append((t - tw, x, y, 0.32))
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
    waves = [(t - w[0], w[1], w[2], w[3]) for w in WAVES if 0.0 <= t - w[0] < 6.0] + _windows(t, song)
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t) * (0.88 + 0.30 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=float(max(PROG(t), lx)), rings=song.rings_at(t), waves=waves,
        star=star_state(t), link=link_state(t),
    )
