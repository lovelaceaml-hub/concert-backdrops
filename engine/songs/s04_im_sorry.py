"""Song 04, I'm Sorry, Please Forgive Me: the 1 minute promo, v2 (0:26 to 1:26 of the studio recording).

Design: "The Thaw" (project-docs/designs/04 I'm Sorry, Please Forgive Me.md, section "Promo v2: scenes").
A clip of the full backdrop: a frozen pale winter morning where the apology is said first (full words; star 3
flares and gains a thin ring); in a close view of the mirrored ice the pain held inside rises out of the reflection;
a path of footprints of light runs from the low sun across the ice, and for a few seconds a sister of light walks
out on it, truly humbled, the heart opening; at the first chorus the lake thaws into apricot light with a thin gold
path ending in one small warm light, and the three-line end card. People of light appear once, briefly and moving.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.5       # last sounding moment of the promo clip
SONG_END = 60.0        # length of the promo clip
TOTAL = 60.0           # promo length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.40         # water line, high: more of the (frozen) lake shows

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


# Promo landmarks (seconds into the 60 second clip, which starts at 0:26 of the studio recording).
# Measured: the instrumental introduction ends at about 0:30 (clip 4) and the first chorus starts at 1:15 (clip 49).
# Lyric line times inside verse 1 are estimates.
VOICE_IN = 5.0        # "I'm sorry" (verse 1, line 1) begins, about 0:31
CHORUS1 = 49.0        # first chorus, 1:15
NINTH = 1e9           # the whole arch does not glow at the end of this promo
TITLE_HIT = 49.9      # end card

# The scenes (promo v2), the phase 1 plates painted for this song (assets/plates/s04/, sun softened behind the
# words and the lower third calmed), each a different framing. Scene changes happen only in gaps between texts.
#  1   0 to 2.5   song 03's closing lake (engine world) drains to ice blue; frost spreads over the water
#  2   1.5 to 18  frozen_lake_wide: a wide frozen lake, low cold sun in haze; the apology's words alone
#  3  16.4 to 29  reflection_close: a low, very close view where the mirrored ice fills the frame (no mountains);
#                 "the pain you held inside" appears in the reflection, then rises
#  4  27 to 49    ice_path: a long view down the ice to the low sun, framed off centre; a path of footprints of
#                 light runs from the sun across the ice; a sister of light walks out on it for a few seconds
#                 ("truly humbled"), then "opened her heart"; the ice holds whole until the thaw
#  5  47 to 60    thaw_morning (graded to apricot and peach): the ice thaws on the first chorus; a thin gold path on
#                 the water, off the sun's reflection, ends in one small warm light where the sister's light came
#                 down; the three-line end card
SKYLINE_LANTERN = 0.0     # no travelling light on the drawn skyline (the plates have their own mountains)
BOTTOM_CALM = 1.0
RINGS_AT_START = {6: 2}   # Encouragement was relit in songs 02 and 03; Apology (03) and Compliment (01) have no rings yet

PAL = {
    "frost":   ("#5a789c", "#9db3cb", "#d6e0ea", "#eef4ff"),
    "apricot": ("#4d6e9c", "#c8aab0", "#ffc08e", "#ffd6a2"),
}
_pal_keys = [(0.0, "frost"), (40.0, "frost"), (50.0, "apricot"), (TOTAL, "apricot")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.34), (TOTAL, 0.34)])
SUN_Y = Track([(0, 0.445), (TOTAL, 0.445)])
SUN_SIZE = Track([(0, 0.15), (TOTAL, 0.15)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.62), (TOTAL, 0.62)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (6, 0.13), (40, 0.15), (48, 0.20), (TOTAL, 0.18)])  # frost glitter, then warm motes
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])   # no falling petals (they belong to songs 02 and 03)
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 1.4, 1.0), (TOTAL - 0.1, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])     # the plates carry their own light; nothing crosses the end card
PART = Track([(0, 0.0), (TOTAL, 0.0)])


# ice crystals glitter cold and pearly, then warm to apricot when the thaw comes
def MOTE_COLORS(t):
    return ("#eef6ff", "#b9d2f2") if t < 40.0 else ("#ffe4bf", "#ffb98c")


PETAL_COLORS = ("#ff9fb2", "#ffe0d2")

# A. scenes. Scene changes are plain fades that run only in the gaps between texts.
SCENES = [
    dict(image="assets/plates/s04/frozen_lake_wide.jpg", t0=1.5, t1=18.4, fade_in=2.0, fade_out=2.0,
         zoom=(1.04, 1.10), water=True, water_line=0.56, water_strength=0.45, calm_gain=0.8,
         gain=Track([(0, 1.0), (4.5, 0.82), (16.6, 0.82), (18.4, 1.0)])),
    dict(image="assets/plates/s04/reflection_close.jpg", t0=16.4, t1=29.2, fade_in=2.0, fade_out=2.0,
         zoom=(1.50, 1.56), pan=((0.06, -0.17), (0.04, -0.17)), water=True, water_line=0.98,
         water_strength=0.55, calm_gain=0.8, gain=Track([(0, 1.0), (18.4, 0.90), (27.0, 0.90), (29.2, 1.0)])),
    dict(image="assets/plates/s04/ice_path.jpg", t0=27.2, t1=49.0, fade_in=2.0, fade_out=2.0,
         zoom=(1.15, 1.12), pan=((0.06, 0.0), (0.055, 0.0)), water=True, water_line=0.55, water_strength=0.35,
         calm_gain=0.8,
         gain=Track([(0, 1.0), (29.2, 0.84), (47.0, 0.84), (49.0, 1.0)])),
    dict(image="assets/plates/s04/thaw_morning.jpg", t0=47.0, t1=61.0, fade_in=2.0, fade_out=0.0,
         zoom=(1.10, 1.05), water=True, water_line=0.445, water_strength=0.45, calm_gain=0.8,
         gain=Track([(0, 0.95), (49.0, 0.80), (TOTAL, 0.80)])),
]

# B. people of light (Anthony, round 3: rare and always moving, never posing under the words). One brief
# appearance: a sister of light gathers on the footprint path and walks across the ice toward her sister (the
# engine's figure motion, a gentle step bob), about five seconds, then her light flies down to the water where the
# small warm light will shine at the end.
WALK_T = (29.8, 35.2)
WALK_X = (0.53, 0.72)
FIGURES = [
    dict(poses=["assets/song_figures/s04/s04_walk.png"], t0=WALK_T[0], t1=WALK_T[1], gather=1.2, dissolve=2.4,
         x=WALK_X, move=WALK_T, ease="linear", bob=1.0, y=0.21, height=0.36, to=(0.42, 0.20), color="#ffb7a8"),
]


def _walk_x(t):
    return float(np.interp(t, WALK_T, WALK_X))


# C. signature effects: the ice and its thaw, frost over the frame, the path of footprints of light across the ice
# the ice stays whole (no thaw edges) through the first three scenes; it is only made fainter over the close
# reflection; it thaws in glowing pools and melts away on the first chorus
ICE = Track([(0, 0.0), (0.6, 0.0), (3.0, 1.0), (46.5, 1.0), (49.5, 0.40), (53.5, 0.0)])
ICE_LINE = Track([(0, 0.40), (1.5, 0.40), (3.5, 0.56), (16.4, 0.56), (18.4, 0.98), (27.2, 0.98), (29.2, 0.55),
                  (46.0, 0.55), (48.0, 0.445), (TOTAL, 0.445)])
ICE_OPACITY = Track([(0, 0.80), (16.4, 0.80), (18.4, 0.15), (27.2, 0.15), (29.2, 0.80), (46.5, 0.80),
                     (49.0, 0.45), (TOTAL, 0.45)])
THAW_COLOR = "#c89070"   # softer thaw rims (the shader keeps them at 0.3 of this in the calm bottom third)
ICE_FRAME = Track([(0, 0.0), (1.0, 0.0), (4.0, 0.35), (27.0, 0.35), (31.0, 0.12), (44.0, 0.08), (48.0, 0.0)])


def _beam(t):
    # ice path: footprints of light from the low sun across the ice toward the walking sister; thaw: a thin gold path that
    # ends in one small warm light at centre
    if t < 47.0:
        return 0.0 if t < 29.5 else min((t - 29.5) / 2.5, 1.0) * 0.55 * (1.0 - min(max((t - 43.0) / 3.0, 0.0), 1.0))
    return 1.0 * min(max((t - 49.0) / 3.0, 0.0), 1.0)


BEAM = _beam
# ice path: from the low sun to the walking sister's feet; thaw: the small warm light sits low in the water at
# x 0.42, left of the sun's reflection (x about 0.485), with its own round halo (the beam's source glow); its thin
# gold path runs back toward the horizon and ends on the water, below the end card's last line
BEAM_FROM = lambda t: (0.44, 0.59) if t < 47.0 else (0.42, 0.20)          # noqa: E731
BEAM_TO = lambda t: (_walk_x(t), 0.215) if t < 47.0 else (0.445, 0.37)    # noqa: E731
BEAM_WIDTH = lambda t: (0.010, 0.07) if t < 47.0 else (0.016, 0.004)      # noqa: E731
BEAM_COLOR = "#ffd2a0"
FLASH = Track([(0, 0.0), (48.6, 0.0), (49.3, 0.16), (50.8, 0.0)])
TEXT_SHADOW = Track([(0, 1.3), (TOTAL, 1.5)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# Stars lit before song 04 in the concert: 3 Apology (song 03), 7 Encouragement and 9 Compliment (song 01).
# In this minute Apology is spoken again: its light flares and gains a thin ring. Inclusiveness is first lit later
# in the song (verse 2), outside this promo minute, so it stays dark here.
OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=100, y=0.30,
         form=5.0, hold=15.0, star=-100.0, arrive=17.3),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.275,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
# Short lyric fragments from the design (never on screen with the expression). Times are estimates in verse 1.
FRAGMENTS = [
    dict(text="the pain you held inside", t0=18.6, t1=22.3, out=25.4, dy=0.0, size=88, glow="#bcd6ff",
         style="reflection", line=0.52),
    dict(text="truly humbled", t0=31.3, t1=34.1, out=37.1, dy=0.06, size=96, style="write", glow="#ffc48c"),
    dict(text="opened her heart", t0=39.2, t1=41.7, out=44.8, dy=0.06, size=96, glow="#ff9fb8"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.8, t1=TITLE_HIT + 3.3)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="I’m Sorry, Please Forgive Me", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.3, t_move=3.0, t_rest=4.8, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky: Apology's light flares again, then the end card
WAVES = [(PHRASES[2]["arrive"], STAR_POS[2][0], STAR_POS[2][1], 0.35), (TITLE_HIT, 0.5, 0.62, 1.2)]


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
