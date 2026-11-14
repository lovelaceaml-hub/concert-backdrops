"""Song 09, Let's Save the World (songbook 335): the 1 minute promo v4, in the original engine style.

Direction round 4 (Anthony): back to the first engine look (engine/songs/s03_original.py): the engine's own luminous
world, words as glowing gold light on a naturally deep sky, nothing dark behind any text (TEXT_SHADOW 0), calm,
slow and magnificent. No painted plates and no people in this version: everything is built from the engine's own
layers, in the song 09 look (DESIGN-SYSTEM.md section 6: a misty sea at Galilee, teal, sea green, pearl and pale
gold; mist that parts for the glory; horizon at mid height and a wide sea; pale gold lamps; soft shafts only; no
aurora, violet sky, petals, rain or Milky Way).

Timed to audio/promo/s09.mp3, 2:35 to 3:35 of the 4:34 instrumental recording (verse 2 and the start of the chorus).
Cue times come from promo v2 (measured in the cloud from the sung guide recording); only cue labels are kept here.
All nine lights are already lit when song 09 begins; here 7 Encouragement shines again (flare and one new ring).

Six scenes:
1 the night shore in sea mist (0 to 9 s): one pale gold lamp walks the far shore under thick mist;
2 the calling (9 to 17 s): the lamps rise from the shore into the sky and a path of light opens on the sea;
3 the still mirror (17 to 33 s): clear stars, a pearl glow low on the horizon, the sea perfectly still for the
  Encouragement, then the words fly into star 7;
4 the glory (33 to 42 s): the mist parts, the pale gold sun rises and lays a path of gold across the sea;
5 the net of light (42 to 49 s): from the risen sun a net of light spreads knot by knot over the whole morning sky;
6 the evening star (49 to 60 s): the sky deepens to teal dusk, the sun sinks to one warm star on the horizon, faint
  net threads remain, and the end card.
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
HORIZON = 0.42         # water line: horizon at mid height, a wide sea (song 09 look)

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
        self.hi = _ar(np.interp(ft, t, np.clip((hi - lo_) / max(hi_ - lo_, 1e-6), 0, 1), right=0.0), 0.04, 0.35)
        on = np.clip(d["onset"] / max(np.percentile(d["onset"], 99), 1e-6), 0.0, 1.4)
        # max-pool the onset envelope into video frames
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the far shore of the sea: low, gentle hills shaped by the loudness of the minute
        xs = np.linspace(0.0, 1.0, 2048)
        st = (xs - RIDGE_X0) / RIDGE_W * MUSIC_END
        base_t = _gauss(n_f, 2.3 * FPS)
        mid_t = _gauss(n_f, 1.0 * FPS)
        base = np.interp(st, ft, base_t)
        mid = np.interp(st, ft, mid_t) - base
        v = np.clip((base - 0.30) / 0.56, 0.0, 1.0) ** 1.6

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
        hgt = 0.010 + 0.034 * v + 0.018 * mid * (0.35 + v) + (0.005 + 0.010 * v) * (crag - 0.5)
        edge = 0.009 + 0.005 * (crag - 0.5)
        sh = np.clip(np.minimum(xs - 0.0, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.where(inside, hgt, edge) * (0.5 + 0.5 * sh)
        self.ridge = np.maximum(self.ridge, 0.004).astype("f4")
        # water rings: one per clear note onset, placed by a hash of its index
        ons = d["onsets"]
        strength = np.interp(ons, t, on)
        keep, last = [], -9.0
        for k, (ot, s) in enumerate(zip(ons, strength)):
            if s > 0.33 and ot - last > 0.30 and ot < MUSIC_END:
                r = np.random.default_rng(1000 + k).random(2)
                keep.append((float(ot), 0.06 + 0.88 * r[0], HORIZON * (0.12 + 0.70 * r[1] ** 1.3), float(min(s, 1.2))))
                last = ot
        # while the Encouragement is on screen the sea falls perfectly still (no rings): peace
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

# Landmarks inside the promo minute (seconds; promo time = recording time minus 2:35), from promo v2.
HONOR = 4.6            # first fragment (end of verse 2 line 1)
CALL = 9.0             # verse 2 line 2: the lamps lift and rise
STILL_IN = 16.0        # the calling fades; the mirror scene settles
ENC_FORM = 20.0        # ENCOURAGEMENT forms at verse 2 line 3; solid from about 23.8
ENC_HOLD = 30.0        # the words start to fly (6.2 s fully formed and solid)
ENC_ARRIVE = 32.0      # the words reach star 7, which shines again and gains a thin ring
GLORY = 33.0           # verse 2 line 4: the mist parts and the sun rises
COMPARE = 34.0         # second fragment (verse 2 line 4)
NET_CAST = 42.6        # verse 2 line 5: the net of light spreads from the risen sun
DUSK = 47.5            # the sky starts to deepen for the end card
NINTH = 1e9            # no whole-arch glow in this song
TITLE_HIT = 51.0       # end card as verse 2 line 5 builds to the chorus
FORM_DUR = 3.0
STILL = [(STILL_IN, ENC_ARRIVE + 0.5)]

# Rings each light carries in from songs 01 to 08 (DESIGN-SYSTEM.md star history): 3 Apology relit in 04,
# 4 Inclusiveness relit in 06, 7 Encouragement relit in 02, 03 and 05, 8 Consideration relit in 07,
# 9 Compliment relit in 08.
RINGS_AT_START = {2: 1, 3: 1, 6: 3, 7: 1, 8: 1}

# Original style (Direction round 4): no dark veil, halo or band behind any words; legibility comes from the glow
# and from a naturally deep sky behind the words.
TEXT_SHADOW = 0.0
BOTTOM_CALM = 1.0      # calm lower third for the performers
# lights behind the end card are only softened, not cleared, so no empty starless field forms round the words
TEXT_PROTECT = Track([(0, 1.0), (TITLE_HIT - FORM_DUR - 1.0, 1.0), (TITLE_HIT - FORM_DUR, 0.4), (TOTAL, 0.4)])
# the lamp that walks the far shore in the night mist, then rises with the others at the calling
SKYLINE_LANTERN = Track([(0, 0.0), (1.0, 0.0), (2.5, 1.0), (CALL, 1.0), (CALL + 2.5, 0.0), (TOTAL, 0.0)])

# Song 09 look: teal, sea green, pearl and pale gold (top of sky, middle, horizon, glow of the low sun).
# The middle of the sky, where the words sit, stays deep in every scene.
PAL = {
    "seamist": ("#020c10", "#06191d", "#1d3d3e", "#9fc8b8"),   # 1 night shore in sea mist
    "calling": ("#03121a", "#0a2730", "#2f5853", "#e8d9a8"),   # 2 the calling: warmer mist, lamp light
    "mirror":  ("#020a12", "#061a24", "#2b5658", "#d8eadc"),   # 3 clear stars, pearl glow on the horizon
    "glory":   ("#05222c", "#163f4a", "#d2c89c", "#fff0c4"),   # 4 dawn: the mist parts, pale gold sun
    "morning": ("#082c36", "#1a4e56", "#9cc4b4", "#fff4d8"),   # 5 morning sea under the net of light
    "dusk":    ("#020a14", "#071c2a", "#1f4250", "#ecc28c"),   # 6 teal dusk, one warm star
}
_pal_keys = [
    (0.0, "seamist"), (CALL - 1.0, "seamist"), (CALL + 3.0, "calling"), (STILL_IN - 1.0, "calling"),
    (STILL_IN + 3.0, "mirror"), (GLORY, "mirror"), (GLORY + 5.0, "glory"), (NET_CAST - 2.0, "glory"),
    (NET_CAST + 2.0, "morning"), (DUSK, "morning"), (TITLE_HIT - 0.5, "dusk"), (TOTAL, "dusk"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the sun waits below the sea, glows at the calling, rises for the glory, then sinks to one warm star at dusk
SUN_INT = Track([(0, 0.06), (CALL, 0.08), (CALL + 3, 0.22), (STILL_IN, 0.18), (GLORY, 0.16), (GLORY + 4, 0.70),
                 (GLORY + 8, 0.95), (NET_CAST + 3, 0.95), (DUSK + 1, 0.55), (TITLE_HIT, 0.24), (TOTAL, 0.22)])
SUN_Y = Track([(0, 0.30), (GLORY, 0.32), (GLORY + 7.0, 0.50), (NET_CAST + 3, 0.53), (DUSK + 1, 0.50),
               (TITLE_HIT + 1.0, 0.425), (TOTAL, 0.42)])
SUN_SIZE = Track([(0, 0.08), (GLORY, 0.09), (GLORY + 8, 0.11), (DUSK, 0.11), (TITLE_HIT + 1.0, 0.045),
                  (TOTAL, 0.04)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.0, 0.45), (CALL, 0.40), (STILL_IN, 0.55), (STILL_IN + 3, 0.95),
               (GLORY, 0.85), (GLORY + 5, 0.12), (NET_CAST, 0.06), (DUSK + 1, 0.10), (TITLE_HIT + 2, 0.70),
               (TOTAL, 0.75)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
# thick sea mist at night, thinning at the calling, a thin low veil of mist on the mirror, parted at dawn
CLOUDS = Track([(0, 0.95), (CALL, 0.90), (CALL + 4, 0.65), (STILL_IN + 2, 0.30), (GLORY, 0.35), (GLORY + 4, 0.45),
                (NET_CAST, 0.35), (DUSK + 2, 0.30), (TOTAL, 0.30)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (CALL, 0.16), (STILL_IN + 2, 0.08), (GLORY, 0.10), (GLORY + 4, 0.30), (NET_CAST, 0.34),
               (TITLE_HIT - FORM_DUR, 0.08), (TOTAL, 0.07)])
MOTE_COLORS = ("#eef6ec", "#bfe3d6")   # pearl motes
# the lamps of the saints: a few on the shore in the mist, then many rise together at the calling
LANTERNS = Track([(0, 0.0), (1.5, 0.0), (4.0, 0.16), (CALL, 0.20), (CALL + 2.5, 0.85), (STILL_IN - 1.0, 0.75),
                  (STILL_IN + 2.5, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = ("#ffe6a8", "#f3c77c")   # pale gold
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
# framing: wide night shore, a slow push in for the calling, wide and still for the mirror, a push toward the sun
# for the glory, wide again for the net and the end card (below 1 brings the horizon closer)
ZOOM = Track([(0, 1.0), (CALL, 0.99), (STILL_IN, 0.95), (STILL_IN + 3, 1.0), (GLORY, 1.0), (NET_CAST - 1, 0.94),
              (NET_CAST + 3, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (59.0, 1.0), (TOTAL, 0.0)])
# soft shafts of light through the mist only (the full fan of rays belongs to songs 01, 06 and 11)
RAYS = Track([(0, 0.0), (GLORY, 0.0), (GLORY + 4, 0.16), (NET_CAST + 2, 0.12), (DUSK + 2, 0.0), (TOTAL, 0.0)])
# the mist parts behind the hills at dawn
PART = Track([(0, 0.0), (GLORY, 0.0), (GLORY + 3.5, 1.0), (DUSK, 1.0), (TITLE_HIT, 0.4), (TOTAL, 0.4)])

# The calling path of light on the sea: from the horizon toward the shore where we stand. At the calling it is a
# thin silver path from the hidden sun; at the glory it becomes a broad path of gold under the risen sun.
BEAM = Track([(0, 0.0), (CALL + 0.5, 0.0), (CALL + 3.0, 0.55), (STILL_IN - 0.5, 0.55), (STILL_IN + 2.0, 0.0),
              (GLORY + 2.0, 0.0), (GLORY + 5.0, 0.85), (NET_CAST + 2, 0.85), (DUSK + 1.5, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, HORIZON + 0.002)
BEAM_TO = (0.5, 0.25)
BEAM_WIDTH = Track([(0, (0.004, 0.07)), (STILL_IN + 2.0, (0.004, 0.07)), (GLORY + 2.0, (0.012, 0.13)),
                    (TOTAL, (0.012, 0.13))])
BEAM_COLOR = Track([(0, lin("#d8ecff")), (STILL_IN + 2.0, lin("#d8ecff")),
                    (GLORY + 2.0, lin("#ffe2a8")), (TOTAL, lin("#ffe2a8"))])

# The net of light: from the risen sun it spreads knot by knot over the whole sky in about 2 s, holds at strength
# until the title starts to form, then a few faint threads stay behind the end card.
NET = Track([(0, 0.0), (NET_CAST, 0.0), (NET_CAST + 2.2, 1.0), (TOTAL, 1.0)])
NET_ORIGIN = (0.5, 0.53)
NET_Y0 = 0.44
NET_SCALE = 5.0
NET_BRIGHT = Track([(0, 0.0), (NET_CAST, 0.0), (NET_CAST + 0.6, 0.7), (TITLE_HIT - FORM_DUR - 0.5, 0.7),
                    (TITLE_HIT - 1.0, 0.025), (TOTAL, 0.025)])
NET_COLOR = "#ffe1a6"
NET_PULSE = "#fff6e2"
# a very soft bloom when the Encouragement reaches star 7
FLASH = Track([(0, 0.0), (ENC_ARRIVE - 0.1, 0.0), (ENC_ARRIVE + 0.9, 0.05), (ENC_ARRIVE + 2.4, 0.0), (TOTAL, 0.0)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = dict(form=1e9, hold=1e9, star=-100.0)   # lit in an earlier song (all nine are lit by the end of song 08)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    # Encouragement at verse 2 line 3; star 7 shines again
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]

# End card of the promo (three lines)
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9, y=0.29)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.6, t1=TITLE_HIT + 2.8)

# The only words from the song on screen: two short fragments, never with the expression, both high on deep sky.
FRAGMENTS = [
    dict(text="hardships as honor", t0=HONOR, t1=HONOR + 3.0, out=HONOR + 6.5, dy=0.0, size=96, glow="#f2c47e",
         style="engrave"),
    dict(text="cannot even compare", t0=COMPARE, t1=COMPARE + 3.2, out=COMPARE + 5.6, dy=0.10, size=96,
         glow="#ffe2a8", style="write"),
]

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Let’s Save the World", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.2, t_move=3.4, t_rest=4.8, scale=0.34, alpha_rest=0.58,
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
    # the corner credit steps back before the net of light spreads over the sky (the end card carries the title)
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(NET_CAST - 1.8, NET_CAST, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky (time, x, y, strength): star 7 shines again (small), then the end card (high)
WAVES = [
    (ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.4),
    (TITLE_HIT, 0.5, 0.75, 0.45),
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
