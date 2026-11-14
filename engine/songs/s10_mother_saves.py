"""Song 10, Our Mother Saves the World: 1 minute promo v2, VISUAL ONLY, NO MUSIC YET.

There is no recording and no lyrics for this song yet, so this promo is drawn to a calm 60 second timeline of its
own. The music features (loudness, onsets, the mountain skyline) are made here from that timeline instead of being
measured, so the silent audio file the workflow needs plays no part in the picture.

Design: "The Lamp on the Shore" (project-docs/designs/10 Our Mother Saves the World.md, "Promo v2: scenes").
The warm star that rests on the horizon in every song is lifted as Mother's great lamp, and its light is Her words:
gold threads run out from it across the dark world to cold, lonely lights, and where they arrive, people of light
act out the words and the night grows still and warm. Five scenes:
  1  the restless night (0 to 6.5 s): a small warm star alone on the horizon, cold grey lights drifting
  2  the great lamp is lifted (6.5 to 12 s): the star grows into the great lamp under a column of light
  3  Her words reach the cold lights (12 to 47 s): gold threads (NET) from the lamp; Greeting on the wide water road,
     then a closer view for Consideration and Encouragement; after each, the scene grows stiller and warmer
  4  peace across the world (47 to 52 s): the curve of the night Earth laced with gold paths (painted plate),
     the other six lights flare in turn and the whole arch glows
  5  night of peace (51 to 60 s): back on the home lake, calm, the lamp set back down, end card
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
LAMP = 6.5             # scene 2: the lamp is lifted
G_FORM = 12.5          # Greeting           (dissolve ends 24.1)
C_FORM = 24.6          # Consideration      (dissolve ends 36.2)
E_FORM = 36.7          # Encouragement      (dissolve ends 48.3)
HOLD = 10.0
EARTH = 48.0           # scene 4: peace across the world (after the words of 36.7 have dissolved at 48.3)
SWEEP = 48.6           # the other six lights flare in turn
NINTH = 50.0
TITLE_HIT = 52.4       # end card (title forms from 49.4, 1.1 s after Encouragement has gone)
HOME = 51.0            # scene 5: the night of peace shows through as the Earth plate fades out

# Calm story curve that stands in for loudness (no recording yet)
_STORY = Track([(0, 0.30), (LAMP, 0.33), (12, 0.44), (30, 0.50), (46, 0.60), (50, 0.68), (56, 0.58), (TOTAL, 0.52)])

# Moments that land like notes: restless ripples that thin out as each word arrives, then the sweep and the card
_EVENTS = ([(0.8 + 0.75 * k, 0.45) for k in range(15)]
           + [(12.4 + 1.3 * k, 0.40) for k in range(9)]
           + [(24.6 + 2.1 * k, 0.35) for k in range(5)]
           + [(37.0 + 3.4 * k, 0.30) for k in range(3)]
           + [(G_FORM + HOLD + 1.1, 1.0), (C_FORM + HOLD + 1.1, 1.0), (E_FORM + HOLD + 1.1, 1.0)]
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
SKYLINE_LANTERN = 0.0   # the lamp itself is the one light on the horizon
BOTTOM_CALM = 1.0
RINGS_AT_START = [0, 0, 1, 1, 0, 0, 4, 1, 1]   # relights earned in songs 02 to 09 (DESIGN-SYSTEM.md 12a)

PAL = {
    "restless": ("#010207", "#050a20", "#101935", "#ffb347"),
    "lamp":     ("#01030b", "#08112e", "#1f2a4e", "#ffbf4f"),
    "gold":     ("#020514", "#0b1638", "#38334a", "#ffc657"),
    "warm":     ("#030618", "#0e1a42", "#4a3c42", "#ffcd63"),
    "peace":    ("#020414", "#0a1238", "#1d2350", "#ffe3a3"),
}
_pal_keys = [(0.0, "restless"), (LAMP, "restless"), (12.0, "lamp"), (24.0, "gold"), (36.0, "warm"),
             (47.0, "warm"), (52.0, "peace"), (TOTAL, "peace")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# The sun is Mother's great lamp, always at the centre of the horizon: small and alone, lifted and strong while
# Her words go out, then set back down with a faint warm glow for the night of peace
SUN_INT = Track([(0, 0.16), (LAMP, 0.20), (9.5, 0.95), (12, 1.05), (24, 1.12), (36, 1.22), (47, 1.30),
                 (50.5, 0.95), (54, 0.62), (TOTAL, 0.58)])
SUN_Y = Track([(0, 0.325), (LAMP, 0.325), (10.5, 0.345), (47, 0.345), (52, 0.330), (TOTAL, 0.330)])
SUN_SIZE = Track([(0, 0.065), (LAMP, 0.07), (11, 0.13), (47, 0.15), (52, 0.10), (TOTAL, 0.10)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.55), (12, 0.55), (46, 0.5), (51, 0.85), (TOTAL, 0.85)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.22), (LAMP, 0.22), (14, 0.10), (36, 0.05), (TOTAL, 0.0)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (3, 0.16), (12, 0.14), (24, 0.18), (36, 0.22), (47, 0.28), (52, 0.18), (TOTAL, 0.14)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
# still camera; one slow settle closer between Greeting and Consideration (a medium shot for the two closer acts),
# back to the wide home view under the Earth plate
ZOOM = Track([(0, 1.0), (22.9, 1.0), (24.5, 1.14), (46.9, 1.14), (49.5, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (57.6, 1.0), (59.8, 0.0)])
RAYS = Track([(0, 0.0), (LAMP, 0.0), (9.5, 0.30), (12, 0.20), (46, 0.26), (50.5, 0.12), (TOTAL, 0.08)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])


# The lights on the water: cold slate at first (people who are tired, hurt or alone), warming to gold as each of
# Her words arrives (the unrest becoming warmth)
_WARM = Track([(0, 0.0), (12, 0.0), (23.6, 0.30), (35.7, 0.62), (47.8, 1.0), (TOTAL, 1.0)])


def MOTE_COLORS(t):
    k = _WARM(t)
    return (_mix_hex("#a7b6cc", "#ffe2a8", k), _mix_hex("#5a6a80", "#ffb066", k))


# ----------------------------------------------------------------- A. scenes
# Scenes 1, 2, 3 and 5 are the engine's own lake, lamp and sky (no painted plates exist for this song in the
# repository); scene 4 is a plate painted from code: assets/plates/s10/make_plates.py
SCENES = [
    # it comes in only after Encouragement's words have gone (no glowing edge across letters)
    dict(image="assets/plates/s10/earth_web.jpg", t0=EARTH, t1=HOME + 3.8, fade_in=1.6, fade_out=3.0,
         transition="fade", zoom=(1.0, 1.06), pan=((0.0, 0.0), (0.0, 0.01)), water=False,
         gain=Track([(0, 1.0), (48.6, 1.0), (50.0, 0.85), (TOTAL, 0.85)])),
]

# ----------------------------------------------------------------- B. people of light (shared library)
# Each pair stands to one side of the lamp, so the lamp's light reaches them along a thread; feet at 0.23,
# words above them at 0.29 to 0.30 (the bottom third stays calm water).
FIGURES = [
    # Greeting: the left person walks up and waves; the lonely one places their hands in the offered hands
    dict(poses=["assets/figures/greeting_a.png", "assets/figures/greeting_b.png"],
         t0=G_FORM - 2.6, t1=G_FORM + HOLD - 0.5, pose_times=[G_FORM + 3.2], x=0.29, y=0.23, height=0.36,
         to_star=0, color="#ffbfa6"),
    # Consideration: one bends under a heavy bundle; the other comes with open hands and they carry it together
    dict(poses=["assets/figures/consideration_a.png", "assets/figures/consideration_b.png"],
         t0=C_FORM - 2.4, t1=C_FORM + HOLD - 0.5, pose_times=[C_FORM + 3.4], x=0.71, y=0.23, height=0.36,
         to_star=7, color="#f8b3c2"),
    # Encouragement: one kneels, exhausted, the other prays over them; a hand on the back; both rise in hope
    dict(poses=["assets/figures/encouragement_a.png", "assets/figures/encouragement_b.png",
                "assets/figures/encouragement_c.png"],
         t0=E_FORM - 2.4, t1=E_FORM + HOLD - 0.5, pose_times=[E_FORM + 2.8, E_FORM + 6.2], x=0.29, y=0.23,
         height=0.36, to_star=6, color="#d3c0f4"),
]

# ----------------------------------------------------------------- C. signature effects
# The great lamp: a column of light settles on the horizon star as it is lifted (gone before any words form)
BEAM = Track([(0, 0.0), (LAMP, 0.0), (9.0, 0.70), (10.6, 0.55), (12.2, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.345)
BEAM_WIDTH = (0.012, 0.075)
BEAM_COLOR = "#ffd98a"
# Gold threads of Her words: spreading from the lamp further after each word arrives
# (the spread is a radius of about 1.9 x 1.12 x NET screen heights round the lamp: 0.17 reaches the people of light)
NET = Track([(0, 0.0), (10.5, 0.0), (14.0, 0.15), (22.0, 0.17), (25.0, 0.20), (34.0, 0.21), (37.0, 0.24),
             (46.5, 0.26), (TOTAL, 0.26)])
NET_ORIGIN = (0.5, 0.345)
NET_Y0 = 0.345
NET_SCALE = 6.0
NET_BRIGHT = Track([(0, 0.0), (10.5, 0.0), (12.0, 0.50), (46.2, 0.50), (48.4, 0.0), (TOTAL, 0.0)])
NET_COLOR = "#ffd38a"
NET_PULSE = "#fff2d6"
# deeper calm behind the words over the bright Earth plate and the end card
TEXT_SHADOW = Track([(0, 1.0), (46.5, 1.0), (49.0, 1.5), (TOTAL, 1.4)])

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
# (illustrative placements, pending the lyrics); the other six flare in turn in the sweep (arrive only, no words).
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=112, y=0.29,
         form=G_FORM, hold=G_FORM + HOLD, arrive=G_FORM + HOLD + 1.1, star=LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.0, star=LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.3, star=LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.6, star=LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164,
         form=_OFF, hold=_OFF, arrive=SWEEP + 0.9, star=LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128,
         form=_OFF, hold=_OFF, arrive=SWEEP + 1.2, star=LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=96, y=0.30,
         form=E_FORM, hold=E_FORM + HOLD, arrive=E_FORM + HOLD + 1.1, star=LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=100, y=0.30,
         form=C_FORM, hold=C_FORM + HOLD, arrive=C_FORM + HOLD + 1.1, star=LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         form=_OFF, hold=_OFF, arrive=SWEEP + 1.5, star=LIT),
]

# End card (PHASE2.md item 7: three lines)
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
FRAGMENTS = []   # no lyrics yet
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0)

CREDIT = dict(song="Our Mother Saves the World", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.4, t_rest=6.4, scale=0.34, alpha_rest=0.58,
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


# Waves of light across the sky: one where each spoken word reaches its light, softer ones in the sweep, one for
# the end card
WAVES = sorted([(p["arrive"], STAR_POS[i][0], STAR_POS[i][1], 0.45 if p["form"] < _OFF else 0.16)
                for i, p in enumerate(PHRASES)])
WAVES.append((TITLE_HIT, 0.5, 0.62, 0.55))   # soft: a strong wave left a bright blob under the title


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
