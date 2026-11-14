"""Song 08, Out of Heaven, Favor From God: 1 minute promo v4, in the original engine style (Anthony, round 4).

The minute of the 2:38 sung guide recording from 1:01.5 to 2:01.5 (audio/promo/s08.mp3). Built from the engine's
own luminous world, as engine/songs/s03_original.py: deep sky with stars, a still lake with the mountain line and
its mirror, aurora, motes, the arch of nine lights, words of glowing gold light with nothing dark behind them.
No painted plates. Five scenes of the royal festival night:
  1. the royal night lake: the swan of light glides in; the Compliment's words form and star 9 shines again;
  2. the festival under the embroidered veil (crimson and gold aurora): the fragment "bridegroom and bride";
  3. heaven opens: golden clouds gather and part, the Gratitude's words, then a column of gold pours down as
     star 2, the last dark star, is lit and the arch of nine is complete;
  4. the velvet night: the seven-branched lampstand of light rises from the lake;
  5. rose gold dawn under a quiet embroidered aurora, with the three-line end card.
Design: project-docs/designs/08 Out of Heaven, Favor From God.md.

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

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402

# Landmarks in the promo minute (seconds from the start of the clip; guide recording time minus 61.5).
# Reading contract: formation about 3.75 s, at least 6 s solid, dissolve about 1.6 s.
COMP_FORM = 7.6        # the Compliment words form as the praise is given
COMP_HOLD = 17.4       # fully formed from about 11.35 to 17.4 (6.05 s solid)
COMP_ARRIVE = 19.2     # the words reach star 9, which shines again (flare and a fresh ring)
GRAT_FORM = 28.9       # "praise and thanksgiving": the Gratitude
GRAT_HOLD = 38.7       # fully formed from about 32.65 to 38.7 (6.05 s solid)
GRAT_STAR = 40.5       # star 2 lit for the first time: all nine lights are lit, the arch is complete
NINTH = GRAT_STAR
TITLE_HIT = 53.1       # end card (title forms from 50.1)

# Original look (Anthony, round 4): the engine's own luminous world, no painted plates, nothing dark behind any
# text. Legibility comes from the glow and from keeping the sky behind the words deep.
TEXT_SHADOW = 0.0
BOTTOM_CALM = 1.0
# Star history before this minute (DESIGN-SYSTEM.md): rings carried from relights in songs 02 to 07.
# star 3 (Apology) relit in 04; star 4 (Inclusiveness) relit in 06; star 7 (Encouragement) relit in 02, 03, 05;
# star 8 (Consideration) relit in 07. Star 9 (Compliment) has no relight before this song.
RINGS_AT_START = {2: 1, 3: 1, 6: 3, 7: 1}

# Five scenes of the royal festival night (DESIGN-SYSTEM.md section 6: deep royal purple, crimson and gold, gold
# aurora like embroidery, rays and sparkle, grand symmetrical framing):
#   1.  0 to 19.5   royal night lake: stars, the warm star low at the centre, the swan of light glides in
#   2. 19.5 to 28.5 the festival under the embroidered veil: crimson and gold aurora, festival sparkle
#   3. 28.5 to 43   heaven opens: golden clouds gather and part in the centre, rays, then a column of gold pours
#                   down as star 2 completes the arch
#   4. 43 to 49.5   the velvet night and the seven-branched lampstand of light rising from the lake
#   5. 49.5 to 60   rose gold dawn under a quiet embroidered aurora, the three-line end card
# (top of sky, middle, horizon, glow of the low sun); the tops stay deep so the arch of nine reads clearly
PAL = {
    "royal":    ("#030109", "#110626", "#34124a", "#e8b860"),
    "crimson":  ("#060112", "#2a0832", "#6a1640", "#ffc4b4"),
    "gold":     ("#07021a", "#2e0c3c", "#7a2a4c", "#ffd49a"),
    "heaven":   ("#0a0420", "#36104a", "#8c3a58", "#ffe2a8"),
    "velvet":   ("#020007", "#0c0318", "#261034", "#e0a860"),
    "dawn":     ("#080320", "#2c1046", "#9a4462", "#ffd8a8"),
}
_pal_keys = [(0.0, "royal"), (18.5, "royal"), (21.5, "crimson"), (27.5, "crimson"), (31.0, "gold"),
             (38.0, "gold"), (40.5, "heaven"), (42.0, "heaven"), (44.5, "velvet"), (49.0, "velvet"),
             (52.5, "dawn"), (TOTAL, "dawn")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.22), (18, 0.30), (22, 0.40), (28, 0.40), (32, 0.55), (38.5, 0.62), (40.5, 0.95),
                 (42.5, 0.70), (45, 0.18), (49, 0.20), (53, 0.55), (TOTAL, 0.62)])
SUN_Y = Track([(0, 0.26), (18, 0.27), (28, 0.28), (38.5, 0.31), (41, 0.33), (44.5, 0.25), (49, 0.25),
               (53, 0.29), (TOTAL, 0.305)])
SUN_SIZE = Track([(0, 0.09), (38, 0.10), (41, 0.12), (45, 0.09), (TOTAL, 0.11)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.95), (18, 0.95), (22, 0.55), (28, 0.5), (32, 0.22), (40, 0.18),
               (44.5, 0.95), (49, 0.95), (53, 0.45), (TOTAL, 0.38)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])       # the Milky Way belongs to another song
CLOUDS = Track([(0, 0.08), (27.5, 0.08), (31.5, 0.75), (40, 0.80), (43.5, 0.25), (45, 0.0), (TOTAL, 0.0)])
# heaven opens: the clouds part in the centre lane (behind the Gratitude words the sky stays clear and deep)
PART = Track([(0, 0.0), (28.5, 0.0), (31.5, 0.7), (38.5, 0.85), (40.5, 1.0), (43.5, 1.0), (45, 0.0), (TOTAL, 0.0)])
# the embroidered veil: crimson and gold aurora (strong for the festival, quiet under the end card)
AURORA = Track([(0, 0.0), (18.5, 0.0), (21.5, 0.62), (27.0, 0.62), (30.0, 0.12), (40.0, 0.10), (43.0, 0.0),
                (49.0, 0.0), (53.0, 0.30), (TOTAL, 0.32)])
AURORA_WARM = ("#ffd77a", "#e0607a")
AURORA_COOL = ("#c0406a", "#8a4ad0")
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# festival sparkle: gold motes
MOTES = Track([(0, 0.04), (2, 0.20), (18, 0.24), (21.5, 0.40), (27.5, 0.40), (31, 0.22), (39.5, 0.30),
               (41.5, 0.55), (44.5, 0.18), (49, 0.18), (53, 0.30), (TOTAL, 0.30)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.55), (TOTAL, 0.8)])
# framing: a slow push in through the night, a step back for the festival and heaven, close for the lampstand
ZOOM = Track([(0, 1.0), (18.5, 0.985), (22, 1.0), (40, 0.975), (44, 0.965), (49.5, 0.955), (TOTAL, 0.945)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 0.55, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (28.5, 0.0), (32, 0.35), (38.5, 0.45), (40.5, 0.9), (42.5, 0.6), (44.5, 0.0), (50, 0.0),
              (54, 0.35), (TOTAL, 0.4)])
FLASH = Track([(0, 0.0), (39.9, 0.0), (40.6, 0.16), (42.0, 0.0), (TOTAL, 0.0)])


def MOTE_COLORS(t):
    return ("#ffe08a", "#ffb07a") if t < 43.0 or t > 50.0 else ("#e8d4ff", "#ffd8a8")


# Heaven opens: a column of gold pours down as star 2 lights (after the Gratitude words have flown, gone before
# the fragment forms)
BEAM = Track([(0, 0.0), (39.4, 0.0), (40.5, 0.55), (41.4, 0.50), (42.6, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, HORIZON + 0.005)
BEAM_WIDTH = (0.02, 0.07)
BEAM_COLOR = "#ffd88a"

SF = "assets/song_figures/s08/"
FIGURES = [
    # the swan of light gathers on the far lake and glides toward the centre, then drifts away upward as light
    # (about 0.8 to 6.4 s, gone before the Compliment's words form); about 75 px per second at 720p
    dict(poses=[SF + "swan_glide.png"], t0=0.8, t1=3.8, gather=2.0, dissolve=2.6, x=(0.84, 0.52), move=(0.8, 6.4),
         ease="linear", flip=True, y=0.275, height=0.15, color="#f1e8ff", glow=0.9, particles=6000, leave="drift"),
    # the seven-branched lampstand of light rises out of the lake under the velvet night (an object, not a
    # person), its sparks flowing back into the horizon light before the end card
    dict(poses=[SF + "lampstand.png"], t0=43.0, t1=47.0, gather=2.6, dissolve=2.4, x=0.5, y=(0.29, 0.335),
         height=(0.30, 0.31), move=(43.0, 47.5), ease="out", color="#ffd890", glow=1.0, particles=9000,
         to=(0.5, HORIZON + 0.01)),
]

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    # Gratitude: lit for the first time in the concert, the last of the nine
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"],
         size=118, form=GRAT_FORM, hold=GRAT_HOLD, star=GRAT_STAR),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
         size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    # Compliment: first lit in song 01, spoken again here (flare and a new ring when the words arrive)
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         form=COMP_FORM, hold=COMP_HOLD, star=-100.0, arrive=COMP_ARRIVE),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
# Short lyric fragments (never on screen with an expression; each about 3 s solid)
FRAGMENTS = [
    # written by a pen of light, like a thread of embroidery, under the festival aurora
    dict(text="bridegroom and bride", t0=21.3, t1=23.8, out=26.8, dy=0.06, size=96, glow="#fff0d2", style="write"),
    # soft words of light above the lampstand
    dict(text="into our Mother’s arms", t0=43.2, t1=45.6, out=48.4, dy=0.17, size=84, glow="#ffe2b8"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.2, t1=TITLE_HIT + 2.4)

# Opening title card that then rests, small, in the top left corner; it fades away from 36 to 40 s so star 2
# lights in the clear and the end card stands alone
CREDIT = dict(song="Out of Heaven, Favor From God", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=5.4, t_rest=7.4, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_gone0=36.0, t_gone1=40.0)


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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_gone0"], c["t_gone1"], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky when a light is lit or shines again (time, x, y, strength)
WAVES = [
    (COMP_ARRIVE, STAR_POS[8][0], STAR_POS[8][1], 0.35),   # star 9 shines again
    (GRAT_STAR, STAR_POS[1][0], STAR_POS[1][1], 0.70),     # star 2 lit: the arch is complete
]


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
