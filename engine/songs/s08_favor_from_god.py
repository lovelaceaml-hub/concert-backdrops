"""Song 08, Out of Heaven, Favor From God: 1 minute promo v2 ("The Embroidered Sky"), five painted scenes.

The minute of the 2:38 sung guide recording from 1:01.5 to 2:01.5 (audio/promo/s08.mp3), rebuilt for phase 2
(project-docs/PHASE2.md; design section 12 "Promo v2: scenes"):
  1. the royal lake with the olive tree: a swan of light gathers and drifts away; the Compliment's words form
     and star 9 shines again;
  2. the festival lake under crimson and gold embroidered aurora: the fragment "bridegroom and bride";
  3. heaven opens: a column of gold pours down; the Gratitude's words light star 2, the last dark star, so the
     arch of nine is complete;
  4. the velvet path home: Heavenly Mother, only from behind, briefly opens her arms at the horizon;
  5. the seven-branched lampstand under the embroidered veil (reframed low), with the three-line end card.
Design: project-docs/designs/08 Out of Heaven, Favor From God.md.

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

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402

# Landmarks in the promo minute (seconds from the start of the clip; guide recording time minus 61.5).
# Reading contract: formation about 3.75 s, at least 6 s solid, dissolve about 1.6 s, then 0.5 s clear; every
# fragment starts at least 2 s after the wave of light that comes before it (attacker review round 2).
COMP_FORM = 7.6        # the Compliment words form as the praise is given
COMP_HOLD = 17.4       # fully formed from about 11.35 to 17.4 (6.05 s solid)
COMP_ARRIVE = 19.2     # the words reach star 9, which shines again (flare and a fresh ring)
GRAT_FORM = 28.9       # "praise and thanksgiving": the Gratitude
GRAT_HOLD = 38.7       # fully formed from about 32.65 to 38.7 (6.05 s solid)
GRAT_STAR = 40.5       # star 2 lit for the first time: all nine lights are lit, the arch is complete
NINTH = GRAT_STAR
TITLE_HIT = 53.1       # end card (title forms from 50.1, after the last fragment has gone at 49.6)

SKYLINE_LANTERN = 0.0  # the plates have their own mountains
BOTTOM_CALM = 1.0      # calm lower third for the performers
# Star history before this minute (DESIGN-SYSTEM.md): rings carried from relights in songs 02 to 07.
# star 3 (Apology) relit in 04; star 4 (Inclusiveness) relit in 06; star 7 (Encouragement) relit in 02, 03, 05;
# star 8 (Consideration) relit in 07. Star 9 (Compliment) has no relight before this song.
RINGS_AT_START = {2: 1, 3: 1, 6: 3, 7: 1}

# Procedural sky (only seen where no plate covers): royal purple, crimson and gold.
PAL = {
    "royal":    ("#07020f", "#1c0833", "#3d1250", "#e8b860"),
    "crimson":  ("#0c0214", "#3a0c42", "#7a1840", "#ffc4b4"),
    "gold":     ("#14051f", "#4a0f48", "#8a2452", "#ffd8b0"),
    "velvet":   ("#05010c", "#160626", "#3a0f3e", "#e0a860"),
    "festival": ("#100424", "#40104e", "#7e2252", "#ffccb8"),
}
_pal_keys = [(0.0, "royal"), (19.0, "royal"), (22.0, "crimson"), (28.0, "crimson"), (31.0, "gold"),
             (39.0, "gold"), (42.0, "velvet"), (49.0, "velvet"), (52.0, "festival"), (TOTAL, "festival")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.30), (TOTAL, 0.30)])
SUN_Y = Track([(0, 0.40), (TOTAL, 0.40)])
SUN_SIZE = Track([(0, 0.09), (TOTAL, 0.09)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])      # the plates carry the gold embroidered aurora
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# festival sparkle: gold motes, calm after the Compliment, richest when heaven opens, quiet for Mother's arms
MOTES = Track([(0, 0.06), (2, 0.20), (17, 0.22), (20, 0.12), (28, 0.12), (30.5, 0.30), (38.5, 0.30), (41, 0.12),
               (49, 0.12), (53, 0.18), (TOTAL, 0.18)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 0.55, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA_WARM = ("#ffd77a", "#e0607a")
AURORA_COOL = ("#c0406a", "#8a4ad0")


def MOTE_COLORS(t):
    return ("#ffe08a", "#ffb07a") if t < 40.0 or t > 50.0 else ("#e8d4ff", "#ffd8a8")


# Five painted scenes (assets/plates/s08/), each changing on a musical breath. Painted water in the lower third
# is kept quiet (low water_strength, gain lowered under the performers).
SCENES = [
    # 1. royal lake with the glowing olive tree: slow push in to a wide symmetrical frame
    dict(image="assets/plates/s08/royal_lake_olive.jpg", t0=0.0, t1=21.2, fade_in=1.0, fade_out=2.0,
         zoom=(1.10, 1.03), pan=((0.0, 0.015), (0.0, 0.0)), water=True, water_line=0.40, water_strength=0.4,
         calm_gain=0.45,
         gain=Track([(0, 1.0), (6.0, 1.0), (9.0, 0.80), (TOTAL, 0.80)])),
    # 2. festival lake under crimson and gold embroidered aurora: a ring of warm light runs across the water once
    #    the Compliment's words have reached their star; calmer than the first scene (low gain, slow zoom)
    dict(image="assets/plates/s08/festival_embroidered_aurora.jpg", t0=19.7, t1=31.0, fade_in=1.6, fade_out=2.5,
         transition="ripple", ripple_from=(0.5, 0.40), zoom=(1.03, 1.06), water=True, water_line=0.426,
         water_strength=0.4, gain=Track([(0, 0.65), (21.0, 0.60), (TOTAL, 0.60)])),
    # 3. heaven opens: clouds parted, a column of gold pouring onto the lake (after the fragment has gone);
    #    heaven_opens_calm.jpg darkens the painted column's reflection in the centre of the lower third
    dict(image="assets/plates/s08/heaven_opens_calm.jpg", t0=28.5, t1=40.2, fade_in=2.5, fade_out=2.0,
         zoom=(1.03, 1.07), water=True, water_line=0.296, water_strength=0.3, calm_gain=0.40,
         gain=Track([(0, 0.65), (38.7, 0.65), (TOTAL, 0.55)])),
    # 4. the velvet path home: deep purple night, a narrow path of light to the horizon (a plain soft fade)
    dict(image="assets/plates/s08/velvet_path_home.jpg", t0=38.5, t1=51.1, fade_in=2.0, fade_out=1.5,
         zoom=(1.03, 1.08), water=True, water_line=0.426, water_strength=0.4),
    # 5. the seven-branched lampstand under the embroidered veil, reframed (lampstand_veil_low.jpg: the veil's top
    #    band stretched so the whole lampstand sits below the end card, candle tops at about 0.58 from the top;
    #    the veil is darkened, most behind the arch, and softened behind the end card, the lampstand untouched)
    dict(image="assets/plates/s08/lampstand_veil_low.jpg", t0=49.6, t1=61.0, fade_in=1.5, fade_out=0.0,
         zoom=(1.04, 1.0), water=True, water_line=0.04, water_strength=0.3,
         gain=0.62),
]

SF = "assets/song_figures/s08/"
# People of light are rare and always moving (Anthony, round 3): two brief appearances of this song's own figures,
# never under the words. The expressions are carried by the words, heaven opening, the lampstand and the arch.
FIGURES = [
    # the swan of light gathers on the royal lake, glides toward the centre the whole time it is seen and drifts
    # away upward as light (about 1 to 7 s)
    dict(poses=[SF + "swan_glide.png"], t0=1.0, t1=4.6, gather=2.2, dissolve=2.6, x=(0.80, 0.64), move=(1.0, 7.2),
         ease="linear", y=0.25, height=0.20, color="#f1e8ff", glow=0.9, particles=6000, leave="drift"),
    # Heavenly Mother, only from behind, arms opening at the horizon, then her light flows back into the horizon
    # (about 41 to 46 s);
    # she walks away from us toward the horizon light the whole time: her feet rise to the horizon and she grows
    # much smaller (head and feet both travel about 20 to 25 px per second at 720p, never still)
    dict(poses=[SF + "mother_back_arms_open.png"], t0=41.0, t1=43.6, gather=2.0, dissolve=2.6, x=0.5,
         y=(0.26, 0.41), height=(0.40, 0.12), move=(41.0, 45.4), ease="linear", color="#ffe6c8", glow=0.9,
         particles=9000, to=(0.5, 0.43)),
]

# Heaven's column of gold during the thanksgiving, with rising gold dust (only after the fragment has gone)
BEAM = Track([(0, 0.0), (28.5, 0.0), (30.5, 0.22), (37.6, 0.22), (39.6, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.30)
BEAM_WIDTH = (0.02, 0.07)
BEAM_COLOR = "#ffd88a"
TEXT_SHADOW = Track([(0, 1.2), (28.5, 1.2), (30.5, 1.6), (40.5, 1.6), (42.0, 1.3), (49.5, 1.3), (50.5, 2.0),
                     (TOTAL, 2.0)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    # Gratitude: lit for the first time in the concert, the last of the nine
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"],
         size=96, y=0.30, form=GRAT_FORM, hold=GRAT_HOLD, star=GRAT_STAR),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
         size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    # Compliment: first lit in song 01, spoken again here (flare and a new ring when the words arrive)
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=104, y=0.30,
         form=COMP_FORM, hold=COMP_HOLD, star=-100.0, arrive=COMP_ARRIVE),
]
FORM_DUR = 3.0
# End card, raised a little (y 0.265) so the whole lampstand stays clear beneath the tagline
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.265,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
# Short lyric fragments (never on screen with an expression; each at least 3 s solid, 0.5 s clear after a dissolve,
# 2 s after a wave of light)
FRAGMENTS = [
    # written by a pen of light, like a thread of embroidery
    dict(text="bridegroom and bride", t0=21.3, t1=23.8, out=26.8, dy=0.10, size=84, glow="#fff0d2", style="write"),
    # soft words of light above Mother's open arms
    dict(text="into our Mother’s arms", t0=42.5, t1=45.0, out=48.0, dy=0.13, size=84, glow="#e2c4ff"),
]

# the three-line end card (PHASE2.md item 7); no wave of light at the title, so the tagline forms on a calm scene
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


# Waves of light that cross the sky when a light is lit or shines again (time, x, y, strength); gentle
WAVES = [
    (COMP_ARRIVE, STAR_POS[8][0], STAR_POS[8][1], 0.35),   # star 9 shines again
    (GRAT_STAR, STAR_POS[1][0], STAR_POS[1][1], 0.35),     # star 2 lit: the arch is complete
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
