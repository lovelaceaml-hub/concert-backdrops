"""Song 07, May No One Ever Feel Lonely: 1 minute promo v2 (0:24 to 1:24 of the studio recording).

Design: "No Light Left Alone", section 16 "Promo v2: scenes". Five painted scenes along the long path home at blue
dusk. An elderly traveler of light walks alone and sits on a bench; Mother's wish lights the way and a path of light
from Her star finds the lone light; a helper greets the traveler ("How are you?", star 1, its first light in the
concert) and offers a hand with the heavy bundle ("Can I give you a hand with anything?", star 8, lit in song 05,
spoken again); the village carries its lanterns home and Heavenly Mother, seen only from behind with a lamp raised,
leads the way up to the gate of light. Each time Her words are spoken, peace settles over the lake.
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

# Promo landmarks (seconds into the 60 second clip, which starts at 0:24 of the studio recording).
# Measured: first big lift at 29.0 (0:53), short gap at 54.0 (1:18).
# Estimated: Mother's first wish about 2 to 13, the earnest wish line about 14 to 28, the promise from 29,
# the care line about 41 to 53, verse 2 begins at 56.
# Reading time contract (PHASE2.md item 4): formation takes 3.75 s, then at least 6 s solid, a 1.6 s dissolve
# and a clean 0.5 s gap before the next text.
G_FORM, G_HOLD = 26.0, 35.8            # Greeting: solid 29.75 to 35.8 (6.05 s); dissolve ends 37.4
C_FORM, C_HOLD = 37.9, 47.7            # Consideration: solid 41.65 to 47.7 (6.05 s); dissolve ends 49.3
NINTH = 1e9                            # no whole-arch glow in this promo
TITLE_HIT = 52.8                       # title starts forming at 49.8; the end card is whole from about 56.2
SKYLINE_LANTERN = 0.0                  # every scene is a painted plate with its own mountains
BOTTOM_CALM = 1.0
TEXT_PROTECT = 1.0
TEXT_SHADOW = Track([(0, 0.9), (12.5, 0.9), (14.0, 1.2), (35.0, 1.2), (37.0, 1.6), (TOTAL, 1.7)])   # stronger on the bright village and gate

# Star history (CONTINUITY-BOARD.md): rings earned before song 07. Apology relit in song 04, Inclusiveness relit
# in song 06, Encouragement relit in songs 02, 03 and 05.
RINGS_AT_START = {2: 1, 3: 1, 6: 3}

# Look (DESIGN-SYSTEM.md section 6, song 07): blue dusk on a long path home. Twilight blue sky, a coral horizon,
# lantern gold lights, the first stars coming out one by one, soft mist. The plates carry the look; the procedural
# sky shows only for the first moment of the fade in.
PAL = {
    "evening": ("#14244c", "#3a4c80", "#d8946e", "#ffc48e"),
    "twilight": ("#0d1b42", "#26407a", "#b98089", "#ffb79c"),
}
_pal_keys = [(0.0, "evening"), (6.0, "twilight"), (TOTAL, "twilight")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.0), (TOTAL, 0.0)])          # the plates have their own horizon star
SUN_Y = Track([(0, 0.335), (TOTAL, 0.35)])
SUN_SIZE = Track([(0, 0.11), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.05), (13, 0.08), (27, 0.16), (40, 0.26), (51, 0.32), (TOTAL, 0.28)])
# lanterns are this song's light: they rise while Mother's wish lights the way, and the village carries them in
# a procession home (signature effect: the lantern procession)
LANTERNS = Track([(0, 0.20), (4.5, 0.30), (8.0, 0.75), (13, 0.75), (18, 0.40), (27, 0.25), (38, 0.30),
                  (42, 0.85), (51, 1.0), (TOTAL, 0.90)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.2, 1.0), (59.2, 1.0), (59.95, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = ("#ffd27a", "#ffb04f")      # lantern gold
MOTE_COLORS = ("#ffe6b0", "#ff9d86")         # gold and coral sparks
AURORA_WARM = ("#ff9a86", "#ffc88a")
AURORA_COOL = ("#7fa8ff", "#9fb8ff")

P = "assets/plates/s07/"
F = "assets/song_figures/s07/"
L = "assets/figures/"

# A. Five scenes (design section 16), each a different place on the long path home. The plates' lower thirds are
# calmed in the files themselves (darker, half the colour, reflections smeared; assets/plates/s07/calm_plate.py),
# so the engine's own lower-third darkening (calm_gain) is kept light.
VILLAGE_ZOOM = 1.08
SCENES = [
    # 1. The lone light at blue dusk: the long shore path, the bench under the lamp post
    dict(image=P + "path_at_dusk.jpg", t0=0.0, t1=14.5, fade_in=1.0, fade_out=2.0,
         zoom=(1.03, 1.0), calm_gain=0.85, water=True, water_line=0.40),
    # 2. Mother's wish lights the way: close on the line of lights running from Her star along the shore (bloom)
    dict(image=P + "the_lit_path.jpg", t0=12.5, t1=25.5, fade_in=2.0, fade_out=2.5, transition="bloom",
         flash=0.3, zoom=(1.38, 1.44), pan=((-0.14, 0.0), (-0.14, 0.0)), calm_gain=0.85, water=True, water_line=0.45),
    # 3. "How are you?": the bench by the shore (the camera pushes in)
    dict(image=P + "bench_by_the_shore.jpg", t0=23.0, t1=38.0, fade_in=2.5, fade_out=2.0, transition="push",
         zoom=(1.10, 1.08), calm_gain=0.85, water=True, water_line=0.21,
         gain=Track([(0, 1.0), (26.0, 1.0), (29.0, 0.88), (36.0, 0.88), (38.0, 1.0)])),
    # 4. The helping hand: the village path, its windows dark (a soft fade in); then
    # "answered from the windows" (this song's own effect): the windows light up one by one, from the near house
    # to the far end of the village, as the kindness spreads (assets/plates/s07/windows.py)
    dict(image=P + "village_w0.jpg", t0=36.0, t1=42.5, fade_in=2.0, fade_out=1.2, transition="fade",
         zoom=VILLAGE_ZOOM, calm_gain=0.85, water=True, water_line=0.27, gain=0.9),
    dict(image=P + "village_w1.jpg", t0=41.3, t1=44.5, fade_in=1.2, fade_out=1.2, zoom=VILLAGE_ZOOM,
         calm_gain=0.85, water=True, water_line=0.27, gain=0.9),
    dict(image=P + "village_w2.jpg", t0=43.3, t1=46.5, fade_in=1.2, fade_out=1.2, zoom=VILLAGE_ZOOM,
         calm_gain=0.85, water=True, water_line=0.27, gain=0.9),
    dict(image=P + "village_w3.jpg", t0=45.3, t1=48.5, fade_in=1.2, fade_out=1.2, zoom=VILLAGE_ZOOM,
         calm_gain=0.85, water=True, water_line=0.27, gain=0.9),
    dict(image=P + "village_path.jpg", t0=47.3, t1=52.5, fade_in=1.2, fade_out=2.0, zoom=VILLAGE_ZOOM,
         calm_gain=0.85, water=True, water_line=0.27, gain=0.9),
    # 5. Toward home: the lantern path up to the gate of light in the clouds
    dict(image=P + "gate_of_home.jpg", t0=50.5, t1=61.0, fade_in=2.0, fade_out=0.0, transition="fade",
         zoom=(1.04, 1.08), calm_gain=0.85, water=True, water_line=0.21,
         gain=Track([(0, 0.92), (52.0, 0.86), (54.0, 0.74), (TOTAL, 0.74)])),
]

# B. People of light (round 3, Anthony: people rare and always moving, never the focus). Only two brief
# appearances, each almost all gathering and flowing light: the traveler on the path at dusk, and Heavenly Mother,
# seen only from behind with her lamp raised, going on ahead along the path home. The expressions are carried by the
# words, the path of light, the windows answering and the star relights.
FIGURES = [
    # scene 1: the elderly traveler appears on the shore path and her light flows on into the lamp by the bench
    dict(poses=[F + "s07_traveler_walk.png"], t0=5.0, t1=7.8, gather=2.5, x=0.40, y=0.45, height=0.22, flip=True,
         color="#ffcf9a", to=(0.235, 0.56), dissolve=2.5),
    # scene 5: Heavenly Mother from behind leads the way; her light flows on along the lantern path, below the card
    dict(poses=[F + "s07_mother_lamp_behind.png"], t0=52.0, t1=55.0, gather=2.5, x=0.17, y=0.12, height=0.25,
         color="#fff0d2", glow=1.1, to=(0.46, 0.20), dissolve=3.0),
]

# C. Signature effects. The lone light found: a path of light from the horizon star along the shore to the bench
# (scene 2). The gate of light: a gentle beam from the gate down onto the upper path, right of the end card.
BEAM = Track([(0, 0.0), (15.5, 0.0), (19.0, 0.70), (23.0, 0.70), (25.0, 0.0), (52.5, 0.0), (54.5, 0.25),
              (TOTAL, 0.25)])


def BEAM_FROM(t):
    return (0.74, 0.556) if t < 40.0 else (0.79, 0.85)


def BEAM_TO(t):
    return (0.16, 0.46) if t < 40.0 else (0.75, 0.62)


def BEAM_WIDTH(t):
    return (0.03, 0.05) if t < 40.0 else (0.02, 0.04)


BEAM_COLOR = "#ffd9a8"

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
    dict(label="Greeting", lines=["“How are you?”"], size=124, y=0.29, form=G_FORM, hold=G_HOLD, star=G_HOLD + 2.0),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=NOT_YET, hold=NOT_YET, star=NOT_YET),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, form=NOT_YET, hold=NOT_YET, star=LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=NOT_YET, hold=NOT_YET, star=LIT),
    # Consideration: lit in song 05, spoken again here at the promise to care for brothers and sisters
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=100, y=0.30,
         form=C_FORM, hold=C_HOLD, star=LIT, arrive=C_HOLD + 2.0),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=NOT_YET, hold=NOT_YET, star=LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# D. Short lyric fragments: Mother's wish written by a pen of light, and the refrain rising out of the lake;
# never on screen together with an expression
FRAGMENTS = [
    dict(text="“on the path to heaven”", t0=4.2, t1=7.2, out=10.2, dy=0.10, size=84, glow="#ffe4c0", style="write"),
    dict(text="our Mother’s earnest wish", t0=15.5, t1=19.5, out=23.0, dy=0.04, size=78, glow="#ffd6b8",
         style="reflection", line=0.55),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.2, t1=TITLE_HIT + 3.4)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="May No One Ever Feel Lonely", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=3.4, t_rest=5.0, scale=0.34, alpha_rest=0.58,
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


# Waves of light when a light is lit, and the peace ring: a wave of stillness across the lake after each of
# Mother's words (unrest to stillness)
WAVES = [(PHRASES[0]["star"], STAR_POS[0][0], STAR_POS[0][1], 0.5),
         (PHRASES[7]["arrive"], STAR_POS[7][0], STAR_POS[7][1], 0.6),
         (G_HOLD + 2.6, 0.5, 0.45, 0.5),
         (TITLE_HIT, 0.5, 0.62, 1.1)]


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
