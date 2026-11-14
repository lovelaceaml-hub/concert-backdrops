"""Song 10, Our Mother Saves the World: 1 minute promo v4 (original style), VISUAL ONLY, NO MUSIC YET.

Direction round 4 (Anthony): back to the look of the first engine version (engine/songs/s03_original.py): the
engine's own luminous world (deep sky with stars, a still lake with the mountain line and its mirror, motes, the arch
of nine lights), the words as large glowing gold light on the sky, and NOTHING DARK behind any text (TEXT_SHADOW = 0,
plus the corner credit's dark field switched off below). No painted plates and no people: everything is drawn from
the engine's own layers, according to this song.

There is no recording and no lyrics for this song yet, so this promo is drawn to a calm 60 second timeline of its
own (the silent clip audio/promo/s10.mp3 plays no part in the picture).

Song 10 look (DESIGN-SYSTEM.md section 6): pre-dawn under a great lamp. Midnight blue and deep gold, one strong
golden light at the centre of the horizon (Mother's lamp, never rising into day), quiet stars, still and centred.
Six scenes, told by sky, light, time and objects:
  1  the restless night (0 to 7 s): a small warm star alone on the horizon, thin drifting cloud, cold grey motes,
     uneasy ripples; the title card
  2  the great lamp is lifted (6 to 20 s): the cloud clears, a column of light rises out of the lamp and it grows
     strong and golden; Greeting
  3  threads of light (19.5 to 32 s): gold threads spread knot by knot from the lamp across the low sky, pulses of
     light running along them toward the cold lights; Consideration
  4  circles of peace (31.5 to 44 s): the threads settle, the sky deepens to violet indigo, the stars come out, and
     slow gold circles of peace open one by one where Her words arrived; Encouragement
  5  peace across the world (44 to 49 s): the threads reach the whole sky (the lamp's light laced over all the
     world), a rose gold pre-dawn glow, the whole arch glows; no words
  6  night of peace (48.5 to 60 s): the threads gone, the lamp set back down to a calm warm light, the lake a mirror,
     steady stars; end card
Signature moments of this song: the great lamp lifted (sun plus rising column), Her words as threads of light
(NET from the lamp), the circles of peace (slow gold rings of light), peace across the whole world (the net over
the whole sky).

Star history (DESIGN-SYSTEM.md 12a): all nine lights were lit in earlier songs. Greeting, Consideration and
Encouragement are spoken again here (illustrative placements, pending the lyrics) and each relights its light once.
Rings: start [0, 0, 1, 1, 0, 0, 4, 1, 1], end [1, 0, 1, 1, 0, 0, 5, 2, 1] (song 11 starts from these).
No lyric fragments: the lyrics are not available.
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
HORIZON = 0.33
RIDGE_X0, RIDGE_W = 0.035, 0.93

from track import Track   # noqa: E402


# ----------------------------------------------------------------- nothing dark behind any text (direction round 4)
# TEXT_SHADOW = 0 removes the veil and dark halo behind the expressions, the title and the end card. The corner
# credit has its own dark field (its texture's third channel, and its glow channel, darken the picture behind it in
# the final pass); this song blanks both, so the credit is crisp gold light with nothing dark around it. The engine
# itself is not changed: only this song's credit texture.
def _light_only_credit():
    """Install the light-only credit texture (called from Song(), which the renderer builds before the credit;
    text.py imports the song module, so it cannot be imported here at load time)."""
    import text as _text
    eng = _text.render_credit
    if getattr(eng, "_light_only", False):
        return

    def render_credit(*a, **k):
        tex, bbox = eng(*a, **k)
        tex = np.array(tex, copy=True)
        tex[..., 1] = 0
        tex[..., 2] = 0
        return tex, bbox

    render_credit._light_only = True
    _text.render_credit = render_credit


TEXT_SHADOW = 0.0


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


# ----------------------------------------------------------------- the minute (reading-time contract)
# Formation takes about 3.75 s from form; hold = form + 10.0 gives 6.25 s fully formed; the dissolve takes 1.6 s.
G_FORM = 8.3           # Greeting, under the great lamp        (dissolve ends 19.9)
C_FORM = 20.4          # Consideration, threads of light       (dissolve ends 32.0)
E_FORM = 32.5          # Encouragement, circles of peace       (dissolve ends 44.1)
HOLD = 10.0
WORLD = 44.0           # scene 5: peace across the world
NINTH = 46.0           # the whole arch glows (a flare without new rings)
TITLE_HIT = 52.0       # end card: the title forms from 49.0
HOME = 48.5            # scene 6: night of peace

_STORY = Track([(0, 0.30), (6, 0.33), (12, 0.44), (30, 0.50), (44, 0.60), (48, 0.66), (56, 0.58), (TOTAL, 0.52)])

# Moments that land like notes: restless ripples that thin out, each word's arrival, then the card
_EVENTS = ([(0.8 + 0.75 * k, 0.45) for k in range(9)]
           + [(G_FORM + HOLD + 1.1, 1.0), (C_FORM + HOLD + 1.1, 1.0), (E_FORM + HOLD + 1.1, 1.0)]
           + [(TITLE_HIT, 1.1)])
_EVENTS.sort()


class Song:
    """Same interface as a measured song, built from the timeline above."""

    def __init__(self):
        _light_only_credit()
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
        # where the great lamp rests
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
        hgt = 0.026 + 0.105 * v + (0.012 + 0.030 * v) * (crag - 0.5)
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
            keep.append((float(et), 0.10 + 0.80 * r[0], HORIZON * (0.72 + 0.25 * r[1]), float(min(s, 1.2))))
        self.rings = keep
        self.ring_t = np.array([k[0] for k in keep])

    def lantern(self, t):
        x = 0.5   # the great lamp itself, at the centre
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


# ----------------------------------------------------------------- look: six skies
SKYLINE_LANTERN = 0.0      # the sun is the lamp; no second light travelling on the ridge
BOTTOM_CALM = 1.0
RINGS_AT_START = [0, 0, 1, 1, 0, 0, 4, 1, 1]

PAL = {
    "restless": ("#010207", "#050a1e", "#0f1730", "#ffb347"),   # cold midnight, small warm star
    "lamp":     ("#01030c", "#071130", "#1f2a52", "#ffbf4f"),   # midnight blue lit from the centre in gold
    "threads":  ("#01030d", "#081335", "#2a2c55", "#ffc657"),   # deeper indigo, gold low sky
    "circles":  ("#030212", "#120d3a", "#33285a", "#ffd27a"),   # violet indigo, many stars
    "world":    ("#040619", "#141a46", "#6a4a52", "#ffd98a"),   # rose gold pre-dawn glow (never day)
    "peace":    ("#010310", "#060f2c", "#18224a", "#ffcf7a"),   # the home night of peace
}
_pal_keys = [
    (0.0, "restless"), (6.0, "restless"), (12.0, "lamp"), (19.5, "lamp"), (24.0, "threads"), (31.5, "threads"),
    (35.5, "circles"), (43.5, "circles"), (46.5, "world"), (48.0, "world"), (52.0, "peace"), (TOTAL, "peace"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# The sun is Mother's great lamp at the centre of the horizon: a small warm star, lifted and strong, set back down
SUN_INT = Track([(0, 0.16), (5.0, 0.20), (9.0, 0.75), (13.0, 1.00), (31.5, 1.05), (43.5, 0.95), (46.5, 1.25),
                 (49.0, 1.10), (53.0, 0.70), (TOTAL, 0.66)])
SUN_Y = Track([(0, 0.325), (5.0, 0.325), (13.0, 0.338), (46.5, 0.342), (53.0, 0.33), (TOTAL, 0.33)])
SUN_SIZE = Track([(0, 0.065), (5.0, 0.068), (13.0, 0.105), (43.5, 0.11), (46.5, 0.125), (53.0, 0.085), (TOTAL, 0.085)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 0.45), (12.0, 0.50), (31.5, 0.55), (36.0, 0.95), (43.5, 0.95),
               (47.0, 0.55), (52.0, 0.80), (TOTAL, 0.80)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.32), (6.0, 0.32), (12.0, 0.04), (TOTAL, 0.04)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.06), (3, 0.12), (12, 0.12), (20, 0.14), (32, 0.20), (44, 0.26), (48, 0.30), (53, 0.16),
               (TOTAL, 0.12)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
# still and centred; the framing breathes only a little between scenes
ZOOM = Track([(0, 1.0), (19.5, 1.0), (26.0, 1.03), (31.5, 1.03), (38.0, 0.985), (44.0, 0.985), (49.0, 1.0),
              (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (59.0, 1.0), (59.95, 0.0)])
RAYS = Track([(0, 0.0), (6.0, 0.0), (12.0, 0.16), (31.5, 0.16), (36.0, 0.08), (43.5, 0.08), (46.5, 0.30),
              (49.0, 0.22), (53.0, 0.10), (TOTAL, 0.10)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])

# The drifting lights: cold slate at first (people who are tired, hurt or alone), warming to gold as each word arrives
_WARM = Track([(0, 0.0), (8.0, 0.0), (19.4, 0.35), (31.5, 0.70), (43.6, 1.0), (TOTAL, 1.0)])


def MOTE_COLORS(t):
    k = _WARM(t)
    return (_mix_hex("#a7b6cc", "#ffe2a8", k), _mix_hex("#5a6a80", "#ffb066", k))


# ----------------------------------------------------------------- signature moments
# 1. The great lamp is lifted: a gentle column of light rises out of the lamp as it grows (gone as Greeting forms)
BEAM = Track([(0, 0.0), (4.6, 0.0), (6.6, 0.42), (8.4, 0.42), (10.6, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.345)
BEAM_WIDTH = (0.012, 0.034)
BEAM_COLOR = "#ffd98a"

# 2. Her words as threads of light: a web of gold threads spreads knot by knot from the lamp over the low sky (kept
#    below the words), then (5) reaches the whole world, then is gathered back before the end card
NET = Track([(0, 0.0), (19.0, 0.0), (24.5, 0.072), (43.5, 0.075), (47.4, 1.0), (49.4, 1.0), (49.5, 0.0),
             (TOTAL, 0.0)])
NET_BRIGHT = Track([(0, 1.0), (31.0, 1.0), (34.5, 0.38), (43.5, 0.38), (45.5, 0.85), (47.4, 0.85), (49.3, 0.0),
                    (TOTAL, 0.0)])
NET_ORIGIN = (0.5, 0.345)
NET_Y0 = 0.33
NET_SCALE = 8.0
NET_COLOR = "#ffcf7a"
NET_PULSE = "#fff1d2"

# 3. Circles of peace: slow gold circles of light open over the lake where the words arrived (at most four at once)
_CIRCLES = [(33.0, 0.30, 0.38, 0.40), (35.6, 0.70, 0.37, 0.40), (38.2, 0.42, 0.40, 0.36), (40.8, 0.60, 0.39, 0.36)]

# ----------------------------------------------------------------- the arch and the words
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

FORM_DUR = 3.0
_OFF = 1e9
LIT = -100.0
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=164,
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
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=E_FORM, hold=E_FORM + HOLD, arrive=E_FORM + HOLD + 1.1, star=LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         form=C_FORM, hold=C_FORM + HOLD, arrive=C_FORM + HOLD + 1.1, star=LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140,
         form=_OFF, hold=_OFF, star=LIT),
]

# End card (three lines), the tagline solid from 54.5 to 59.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
FRAGMENTS = []   # no lyrics yet
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=52.9, t1=54.5)

CREDIT = dict(song="Our Mother Saves the World", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=4.4, t_rest=6.4, scale=0.34, alpha_rest=0.62,
              margin_x=0.030, margin_top=0.048, t_gone0=17.6, t_gone1=19.0)


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
    # the corner credit leaves before the Greeting light is relit next to it (nothing crosses it)
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_gone0"], c["t_gone1"], t))
    alpha *= 1.0 - 0.95 * min(1.0, 12.0 * m * (1.0 - m))   # nearly out while it crosses the arch line on its way
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light: the circles of peace, and a small one where each spoken word reaches its light
WAVES = sorted(_CIRCLES + [
    (PHRASES[0]["arrive"], STAR_POS[0][0], STAR_POS[0][1], 0.22),
    (PHRASES[7]["arrive"], STAR_POS[7][0], STAR_POS[7][1], 0.22),
    (PHRASES[6]["arrive"], STAR_POS[6][0], STAR_POS[6][1], 0.22),
])


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
