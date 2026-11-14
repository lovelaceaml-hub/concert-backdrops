"""Song 10, Our Mother Saves the World: 1 minute promo v2, VISUAL ONLY, NO MUSIC YET.

There is no recording and no lyrics for this song yet, so this promo is drawn to a calm 60 second timeline of its
own. The music features (loudness, onsets, the mountain skyline) are made here from that timeline instead of being
measured, so the silent audio file the workflow needs plays no part in the picture.

Design: "The Lamp on the Shore" (project-docs/designs/10 Our Mother Saves the World.md, "Promo v2: scenes").
The warm star that rests on the horizon in every song is lifted as Mother's great lamp, and its light is Her words:
gold threads run out from it across the dark world to cold, lonely lights, and where they arrive, people of light
act out the words and the night grows still and warm. Six scenes, each one of Anthony's painted plates (Assets/s10):
  1  the restless night (0 to 7 s): a small warm star alone on the horizon, cold blue lights, uneasy water; title
  2  the great lamp is lifted (4.5 to 20.5 s): Heavenly Mother, from behind and fully robed, at the lamp; one thread
     of light runs from the lamp to a pair of people of light: Greeting
  3  Her words go out (18 to 33 s): gold threads from the lantern on the water; a thread reaches a pair: Consideration
  4  circles of peace (30.5 to 46.5 s): still mirror circles where the words arrived: Encouragement at the centre
  5  peace across the world (44 to 52.4 s): the night Earth laced with gold paths, the whole arch glows
  6  night of peace (49.8 to 60 s): the home lake a perfect mirror, the lamp set back down; end card
All nine lights are already lit (star history, DESIGN-SYSTEM.md 12a). The three expressions are ILLUSTRATIVE
placements, pending the lyrics (Astra round 1, finding 14). No lyric fragments: the lyrics are not available.
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
HORIZON = 0.33         # a little more lake, so the great lamp's road of light runs down the centre
RIDGE_X0, RIDGE_W = 0.035, 0.93

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402


def lin(hexs):
    h = hexs.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    return c ** 2.2


def _mix_hex(a, b, k):
    ca = np.array([int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)
    cb = np.array([int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)
    c = np.clip(np.round(ca * (1 - k) + cb * k), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


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


# ----------------------------------------------------------------- the minute (reading-time contract, PHASE2.md 4)
# Formation takes about 3.75 s from form; hold = form + 10.0 gives 6.25 s fully formed; the dissolve takes 1.6 s
# and the next words start at least 0.5 s after it ends.
G_FORM = 8.3           # Greeting, on the great lamp scene      (dissolve ends 19.9)
C_FORM = 20.4          # Consideration, on the threads scene   (dissolve ends 32.0)
E_FORM = 32.5          # Encouragement, on the circles of peace (dissolve ends 44.1)
HOLD = 10.0
EARTH = 44.0           # scene 5: peace across the world, 4.5 s clear of words before the end card forms
NINTH = 46.0           # the whole arch glows (a flare without new rings)
TITLE_HIT = 51.6       # end card: the title forms from 48.6
HOME = 49.8            # scene 6: the night of peace ripples in under the forming title

# Calm story curve that stands in for loudness (no recording yet)
_STORY = Track([(0, 0.30), (6, 0.33), (12, 0.44), (30, 0.50), (44, 0.60), (48, 0.66), (56, 0.58), (TOTAL, 0.52)])

# Moments that land like notes: restless ripples that thin out as each word arrives, then the card
_EVENTS = ([(0.8 + 0.75 * k, 0.45) for k in range(9)]
           + [(G_FORM + HOLD + 1.1, 1.0), (C_FORM + HOLD + 1.1, 1.0), (E_FORM + HOLD + 1.1, 1.0)]
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
            i = min(int(et * FPS), NFRAMES - 1)
            pooled[i] = max(pooled[i], s)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # still, centred framing: a symmetrical far range, highest at the sides, with a low saddle at the centre
        # where the great lamp rests (no recording, so it is not drawn from loudness)
        xs = np.linspace(0.0, 1.0, 2048)
        st = (xs - RIDGE_X0) / RIDGE_W * MUSIC_END
        base = 0.30 + 0.42 * np.abs(2.0 * xs - 1.0) ** 1.3
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
        hgt = 0.030 + 0.120 * v + (0.014 + 0.034 * v) * (crag - 0.5)
        edge = 0.020 + 0.012 * (crag - 0.5)
        taper = np.clip(np.minimum(st, MUSIC_END - st) / 5.0, 0.0, 1.0)
        taper = taper * taper * (3 - 2 * taper)
        sh = np.clip(np.minimum(xs, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.maximum((edge + (hgt - edge) * taper) * (0.5 + 0.5 * sh), 0.006).astype("f4")
        # rings on the water, far out near the horizon (the calm lower third fades any that come nearer)
        keep = []
        for k, (et, s) in enumerate(_EVENTS):
            r = np.random.default_rng(1000 + k).random(2)
            keep.append((float(et), 0.10 + 0.80 * r[0], HORIZON * (0.70 + 0.27 * r[1]), float(min(s, 1.2))))
        self.rings = keep
        self.ring_t = np.array([k[0] for k in keep])

    def lantern(self, t):
        x = 0.5   # the carried light rests at the centre: it is the great lamp itself
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


# ----------------------------------------------------------------- look
# Song 10 (DESIGN-SYSTEM.md section 6): pre-dawn under a great lamp. Midnight blue and deep gold, one strong golden
# light at the centre of the horizon, quiet stars, still and centred. No aurora, rain, petals or lanterns.

# ----------------------------------------------------------------- look
# Song 10 (DESIGN-SYSTEM.md section 6): pre-dawn under a great lamp. Midnight blue and deep gold, one strong golden
# light at the centre of the horizon, quiet stars, still and centred. No aurora, rain, petals or lanterns.
# Every second is a painted plate (assets/plates/s10/), so the engine's own sky and lake only show under them.
SKYLINE_LANTERN = 0.0
BOTTOM_CALM = 1.0
# relights earned in songs 02 to 09 (DESIGN-SYSTEM.md 12a). At the end of this minute (after Greeting, Consideration
# and Encouragement are relit once each) the counts are [1, 0, 1, 1, 0, 0, 5, 2, 1].
RINGS_AT_START = [0, 0, 1, 1, 0, 0, 4, 1, 1]

PAL = {
    "night": ("#010207", "#050a20", "#101935", "#ffb347"),
    "peace": ("#020414", "#0a1238", "#1d2350", "#ffe3a3"),
}
_pal_keys = [(0.0, "night"), (44.0, "night"), (52.0, "peace"), (TOTAL, "peace")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.2), (TOTAL, 0.2)])
SUN_Y = Track([(0, 0.33), (TOTAL, 0.33)])
SUN_SIZE = Track([(0, 0.07), (TOTAL, 0.07)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.30), (TOTAL, 0.30)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (3, 0.14), (20, 0.16), (32, 0.18), (44, 0.24), (52, 0.16), (TOTAL, 0.12)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (59.0, 1.0), (59.95, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

# The drifting lights: cold slate at first (people who are tired, hurt or alone), warming to gold as each of Her
# words arrives (the unrest becoming warmth)
_WARM = Track([(0, 0.0), (8.0, 0.0), (19.4, 0.35), (31.5, 0.70), (43.6, 1.0), (TOTAL, 1.0)])


def MOTE_COLORS(t):
    k = _WARM(t)
    return (_mix_hex("#a7b6cc", "#ffe2a8", k), _mix_hex("#5a6a80", "#ffb066", k))


# Soft fades only: bloom and ripple changes washed the frame or drew a ring across the words (stills check).
# ----------------------------------------------------------------- A. six scenes (Anthony's plates from Assets/s10,
# the lower third calmed by assets/plates/s10/calm_lower_third.py)
_P = "assets/plates/s10/"
SCENES = [
    # 1 the restless night: one small warm star alone on the horizon, cold blue lights, the water uneasy
    dict(image=_P + "restless_night.jpg", t0=0.0, t1=7.0, fade_in=1.0, fade_out=2.5, zoom=(1.07, 1.03),
         water=True, water_line=0.415, water_strength=1.9),
    # 2 the great lamp is lifted: Heavenly Mother (from behind) at the lamp; Greeting
    dict(image=_P + "great_lamp.jpg", t0=4.5, t1=20.5, fade_in=2.5, fade_out=2.5, transition="fade",
         zoom=(1.0, 1.04), water=True, water_line=0.495, water_strength=0.7,
         gain=Track([(0, 1.0), (7.5, 1.0), (9.0, 0.80), (TOTAL, 0.80)])),
    # 3 Her words go out: gold threads from the lantern to the lights on the water; Consideration
    dict(image=_P + "threads.jpg", t0=18.0, t1=33.0, fade_in=2.5, fade_out=2.5, transition="fade",
         zoom=(1.04, 1.0), water=True, water_line=0.575, water_strength=0.45,
         gain=0.85),
    # 4 circles of peace: wherever a word reached, the water settles into a still mirror; Encouragement
    dict(image=_P + "circles_of_peace.jpg", t0=30.5, t1=46.5, fade_in=2.5, fade_out=2.5, transition="fade",
         zoom=(1.0, 1.04), water=True, water_line=0.61, water_strength=0.15,
         gain=0.85),
    # 5 peace across the world: the night Earth laced with gold paths, the arch glows (no words for 4.5 s)
    dict(image=_P + "earth_web.jpg", t0=EARTH, t1=52.4, fade_in=2.5, fade_out=2.6, transition="fade",
         zoom=(1.0, 1.05), water=False, gain=Track([(0, 1.0), (48.0, 1.0), (49.5, 0.65), (TOTAL, 0.65)])),
    # 6 night of peace: the home lake a perfect mirror, the lamp set back down; end card
    dict(image=_P + "mirror_night.jpg", t0=HOME, t1=61.0, fade_in=2.6, fade_out=0.0, transition="fade",
         zoom=(1.03, 1.0), water=True, water_line=0.46, water_strength=0.12,
         gain=0.85),
]

# ----------------------------------------------------------------- B. people of light
# Heavenly Mother, seen only from behind and fully robed, holding the lamp low at the centre of the great lamp's
# light; when Her first word has gone out, Her sparks return into the lamp. The three pairs act at different places:
# centre-left, right, centre.
FIGURES = [
    dict(poses=["assets/figures/s10_mother_lamp_a.png"], t0=4.8, t1=16.0, x=0.5, y=0.35, height=0.24,
         to=(0.5, 0.495), color="#ffd796", glow=0.55, glass=0.5, sparks=0.8),
    # Greeting: the left person walks up and waves; the lonely one places their hands in the offered hands
    dict(poses=["assets/figures/greeting_a.png", "assets/figures/greeting_b.png"],
         t0=G_FORM - 2.3, t1=G_FORM + HOLD - 0.5, pose_times=[G_FORM + 3.2], x=0.25, y=0.23, height=0.36,
         to_star=0, color="#ffbfa6", glass=1.3),
    # Consideration: one bends under a heavy bundle; the other comes with open hands and they carry it together
    dict(poses=["assets/figures/consideration_a.png", "assets/figures/consideration_b.png"],
         t0=C_FORM - 2.4, t1=C_FORM + HOLD - 0.5, pose_times=[C_FORM + 3.4], x=0.74, y=0.23, height=0.36,
         to_star=7, color="#f8b3c2", glass=1.3),
    # Encouragement: one kneels, exhausted, the other prays over them; a hand on the back; both rise in hope
    dict(poses=["assets/figures/encouragement_a.png", "assets/figures/encouragement_b.png",
                "assets/figures/encouragement_c.png"],
         t0=E_FORM - 2.4, t1=E_FORM + HOLD - 0.5, pose_times=[E_FORM + 2.8, E_FORM + 6.2], x=0.5, y=0.23,
         height=0.36, to_star=6, color="#d3c0f4", glass=1.3),
]

# ----------------------------------------------------------------- C. signature effects
# The great lamp and its threads: as each act begins, one thread of light runs from the lamp to that pair (a narrow
# BEAM path with a small pool where it lands), then fades when the words rise
_THREADS = [  # (start, end, from (the lamp in that plate), to (the pair))
    (G_FORM - 1.3, G_FORM + HOLD - 0.3, (0.5, 0.495), (0.33, 0.40)),
    (C_FORM - 0.9, C_FORM + HOLD - 0.3, (0.5, 0.555), (0.66, 0.40)),
    (E_FORM - 0.9, E_FORM + HOLD - 0.3, (0.5, 0.605), (0.5, 0.47)),
]
BEAM = Track([(0, 0.0)] + [k for a, b, _, _ in _THREADS
                           for k in ((a, 0.0), (a + 1.5, 0.55), (b - 1.0, 0.55), (b, 0.0))] + [(TOTAL, 0.0)])


def _thread(t):
    for a, b, f, to in _THREADS:
        if t < b + 0.6:
            return f, to
    return _THREADS[-1][2], _THREADS[-1][3]


def BEAM_FROM(t):
    return _thread(t)[0]


def BEAM_TO(t):
    return _thread(t)[1]


BEAM_WIDTH = (0.003, 0.008)
BEAM_COLOR = "#ffd98a"
# deeper calm behind the words over the bright Earth plate and the end card
TEXT_SHADOW = Track([(0, 1.0), (44.0, 1.0), (48.0, 1.45), (TOTAL, 1.4)])

# ----------------------------------------------------------------- the arch and the words
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

FORM_DUR = 3.0
_OFF = 1e9
LIT = -100.0
# All nine were lit in earlier songs (star=-100). Greeting, Consideration and Encouragement are spoken again here
# (illustrative placements, pending the lyrics) and each relights its star once (arrive: a flare and one ring).
# The other six only glow with the whole arch from NINTH (no relight, no new ring).
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=112, y=0.30,
         form=G_FORM, hold=G_FORM + HOLD, arrive=G_FORM + HOLD + 1.1, star=LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=_OFF, hold=_OFF, star=LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         form=_OFF, hold=_OFF, star=LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150,
         form=_OFF, hold=_OFF, star=LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164,
         form=_OFF, hold=_OFF, star=LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         form=_OFF, hold=_OFF, star=LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=96, y=0.31,
         form=E_FORM, hold=E_FORM + HOLD, arrive=E_FORM + HOLD + 1.1, star=LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=100, y=0.31,
         form=C_FORM, hold=C_FORM + HOLD, arrive=C_FORM + HOLD + 1.1, star=LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         form=_OFF, hold=_OFF, star=LIT),
]

# End card (PHASE2.md item 7: three lines), the tagline solid from 54.8 to 59.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
FRAGMENTS = []   # no lyrics yet
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=53.0, t1=54.8)

CREDIT = dict(song="Our Mother Saves the World", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.4, t_rest=6.4, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_gone0=46.5, t_gone1=47.8)


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
    # the corner credit leaves before the arch glows and the end card comes (nothing crosses it)
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_gone0"], c["t_gone1"], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Small waves of light where a spoken word reaches its light (none for Greeting: its light is next to the corner
# credit), and a soft one for the end card
WAVES = [(PHRASES[7]["arrive"], STAR_POS[7][0], STAR_POS[7][1], 0.22),
         (PHRASES[6]["arrive"], STAR_POS[6][0], STAR_POS[6][1], 0.22),
         (TITLE_HIT, 0.5, 0.62, 0.35)]


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
