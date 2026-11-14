"""Song 04, I'm Sorry, Please Forgive Me: the 1 minute promo, v4 in the original style (0:26 to 1:26 of the
studio recording).

Anthony, round 4: back to the engine's own luminous world (engine/songs/s03_original.py), according to the song,
with nothing dark behind any text. This song's own story and look (DESIGN-SYSTEM.md section 6): a frozen pale
winter morning that thaws into apricot warmth; horizon high, more lake; a low cold sun in haze, then warm rays.
No plates: every scene is built from the engine's layers (sky, stars, the lake with its mountain line and mirror,
ice and frost, the path of light, motes, the arch). Song 04 owns the freeze and the thaw. No petals.

Scenes (seconds into the promo; changes run in gaps between texts):
 1  0 to 17     frost before dawn: a deep blue night over the lake, the last stars, frost creeping in from the
                corners and the lake freezing over; the title card; the Apology, said first, alone
 2  17 to 29    the mirror in the ice: the camera comes low and close over the ice under a violet night full
                of stars, the ice clear enough to show the mirror, frost thick at the edges of the frame; "the pain you held inside" rises out of the reflection
 3  29 to 46    cold winter morning: the sky opens to steel blue with a pale ice horizon, a low cold sun in
                haze; a path of footprints of light runs from the sun across the ice; a sister of light walks it
                (once, about 4 s, always moving); "truly humbled", then "opened her heart"
 4  46 to 60    the thaw into apricot: on the first chorus the ice melts in glowing pools, warm rays rise, a thin
                gold path on the open water ends in one small warm light; the three-line end card
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

import importlib.util  # noqa: E402
import sys  # noqa: E402

from track import Track   # the shared Track refuses keys that are not strictly increasing  # noqa: E402

# Promo landmarks (seconds into the 60 second clip, which starts at 0:26 of the studio recording).
# Measured: the instrumental introduction ends at about 0:30 (clip 4) and the first chorus starts at 1:15 (clip 49).
# Lyric line times inside verse 1 are estimates (as in promo v2).
VOICE_IN = 5.0        # "I'm sorry" (verse 1, line 1) begins, about 0:31
CHORUS1 = 49.0        # first chorus, 1:15
NINTH = 1e9           # the whole arch does not glow at the end of this promo
TITLE_HIT = 49.9      # end card

BOTTOM_CALM = 1.0
RINGS_AT_START = {6: 2}   # Encouragement was relit in songs 02 and 03

# Nothing dark behind any text (Anthony, round 4): no veil, no dark halo, no dark band. The words read by their
# own glow on a sky kept naturally deep where they sit.
TEXT_SHADOW = 0.0

# Scene palettes (top of sky, middle, horizon, glow of the low sun)
PAL = {
    "frostnight": ("#02061a", "#081634", "#22406a", "#9cc4ff"),
    "mirror":     ("#05041c", "#130f38", "#33295e", "#c6b4ff"),
    "coldmorn":   ("#040c28", "#10264c", "#6f8fb4", "#dfeaff"),
    "warming":    ("#060d2c", "#1a2652", "#a88a98", "#ffd8b8"),
    "apricot":    ("#070f30", "#1d2150", "#8e6070", "#ffc890"),
}
_pal_keys = [(0.0, "frostnight"), (16.5, "frostnight"), (19.5, "mirror"), (27.5, "mirror"), (31.0, "coldmorn"),
             (40.0, "coldmorn"), (45.5, "warming"), (49.0, "apricot"), (TOTAL, "apricot")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.14), (16.5, 0.18), (19.5, 0.06), (27.0, 0.08), (31.0, 0.42), (40.0, 0.50), (46.0, 0.52),
                 (49.5, 0.60), (TOTAL, 0.58)])
# the warm sun stays low, at the ridge, so the sky behind the end card stays deep
SUN_Y = Track([(0, 0.395), (16.5, 0.40), (19.5, 0.385), (27.0, 0.39), (31.0, 0.425), (44.0, 0.43), (49.0, 0.415),
               (TOTAL, 0.415)])
SUN_SIZE = Track([(0, 0.09), (27.5, 0.09), (31.0, 0.12), (44.0, 0.12), (49.0, 0.10), (TOTAL, 0.10)])
STARS = Track([(0, 0.0), (0.3, 0.0), (2.5, 0.85), (16.5, 0.7), (19.5, 1.0), (27.0, 0.9), (32.0, 0.12),
               (46.0, 0.05), (TOTAL, 0.05)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.12), (16.5, 0.15), (19.5, 0.05), (27.0, 0.06), (31.0, 0.45), (46.0, 0.45), (52.0, 0.30),
                (TOTAL, 0.30)])   # haze in the cold morning
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])     # aurora belongs to song 03
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.06), (3, 0.16), (17, 0.20), (29, 0.18), (46, 0.22), (50, 0.34), (TOTAL, 0.30)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])     # no petals (songs 02 and 03)
TRAIL = Track([(0, 0.0), (1.2, 0.45), (TOTAL, 0.55)])
# framing: wide night, then low and close over the mirror ice, back out to the long morning view, and the
# slightest push into the thaw
ZOOM = Track([(0, 1.0), (16.5, 0.985), (19.8, 0.62), (26.5, 0.60), (30.5, 1.0), (46.0, 0.985), (TOTAL, 0.955)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 1.4, 1.0), (TOTAL - 0.1, 0.0)])
RAYS = Track([(0, 0.0), (47.0, 0.0), (51.0, 0.14), (TOTAL, 0.14)])   # gentle warm rays only once it thaws
PART = Track([(0, 0.0), (47.5, 0.0), (51.0, 0.5), (TOTAL, 0.5)])     # the haze parts round the warm sun
# the light that travels the skyline (original style) rests while words stand near its path
SKYLINE_LANTERN = Track([(0, 1.0), (18.0, 1.0), (19.0, 0.0), (26.0, 0.0), (27.5, 1.0), (47.0, 1.0), (49.0, 0.3),
                         (TOTAL, 0.3)])


# frost glitter, cold and pearly; apricot once the thaw comes
def MOTE_COLORS(t):
    return ("#eef6ff", "#b9d2f2") if t < 47.5 else ("#ffe4bf", "#ffb98c")


# A. the freeze and the thaw (song 04's own signature): the lake freezes over at the start, holds whole, is made
# clearer over the close mirror, and thaws in glowing pools on the first chorus
ICE = Track([(0, 0.0), (0.8, 0.0), (5.0, 1.0), (47.5, 1.0), (50.5, 0.40), (55.0, 0.0)])
ICE_LINE = HORIZON
ICE_OPACITY = Track([(0, 0.85), (16.5, 0.85), (19.8, 0.25), (26.5, 0.25), (30.5, 0.85), (TOTAL, 0.85)])
ICE_COLOR = "#cfe2ff"
THAW_COLOR = "#e8a476"
ICE_FRAME = Track([(0, 0.0), (1.0, 0.0), (6.0, 0.32), (17.0, 0.32), (20.0, 0.45), (26.5, 0.45), (31.0, 0.12),
                   (44.0, 0.08), (48.0, 0.0)])

# B. one person of light, once (Anthony, round 4: optional, rare, always moving, small, never under words):
# in the gap between the reflection fragment and "truly humbled", a sister of light gathers far out on the
# ice and walks across it (left to right, facing the way she walks) for about 4 s, then her light flies down
# the path toward the sun. Far away, so small; feet on the ice just under the horizon, above the calm third.
WALK_T = (26.9, 31.1)
WALK_X = (0.27, 0.60)     # 0.33 of the width in 4.2 s: about 100 px a second at 720p
FIGURES = [
    dict(poses=["assets/song_figures/s04/s04_walk.png"], t0=WALK_T[0], t1=WALK_T[1], gather=1.0, dissolve=1.6,
         x=WALK_X, move=WALK_T, ease="linear", bob=1.0, y=0.345, height=0.17, to=(0.5, 0.41),
         color="#ffc8a8", glow=0.8, sparks=0.85),
]


def _walk_x(t):
    return float(np.interp(t, WALK_T, WALK_X))


# C. the path of light: footprints of light from the low sun across the ice to the walking sister's feet (cold
# morning); at the thaw a thin gold path on the open water from the sun's foot to one small warm light
def _beam(t):
    if t < 46.0:
        if t < 27.4:
            return 0.0
        return min((t - 27.4) / 2.0, 1.0) * 0.65 * (1.0 - min(max((t - 32.0) / 3.0, 0.0), 1.0))
    return 0.6 * min(max((t - 50.0) / 3.0, 0.0), 1.0)


BEAM = _beam
BEAM_FROM = lambda t: (0.5, 0.405) if t < 46.0 else (0.5, 0.398)                     # noqa: E731
BEAM_TO = lambda t: (_walk_x(min(t, WALK_T[1])), 0.35) if t < 46.0 else (0.5, 0.35)   # noqa: E731
BEAM_WIDTH = lambda t: (0.006, 0.030) if t < 46.0 else (0.004, 0.016)               # noqa: E731
BEAM_COLOR = "#ffd2a0"
FLASH = Track([(0, 0.0), (48.6, 0.0), (49.3, 0.12), (50.8, 0.0)])

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
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, y=0.36,
         form=5.0, hold=15.0, star=-100.0, arrive=17.3),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.29,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
# Short lyric fragments (never on screen with the expression). Times are estimates in verse 1.
FRAGMENTS = [
    dict(text="the pain you held inside", t0=19.2, t1=23.2, out=25.6, dy=0.0, size=92, glow="#bcd6ff",
         style="reflection", line=HORIZON),
    dict(text="truly humbled", t0=31.6, t1=34.4, out=37.4, dy=0.04, size=100, style="write", glow="#ffc48c"),
    dict(text="opened her heart", t0=39.2, t1=41.7, out=44.8, dy=0.04, size=100, glow="#ffad69"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.8, t1=TITLE_HIT + 3.3)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="I’m Sorry, Please Forgive Me", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.3, t_move=3.0, t_rest=4.8, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048)


class _CreditWithoutShade:
    """Round 4: nothing dark behind the corner credit either. The shared composite darkens the scene by the
    credit texture's glow and shield channels (not scaled by TEXT_SHADOW), so when the engine imports text.py
    this wraps its render_credit to keep only the sharp letters. Shared engine code is untouched."""

    def find_spec(self, name, path=None, target=None):
        if name != "text":
            return None
        sys.meta_path.remove(self)
        spec = importlib.util.find_spec(name)
        if spec is None or spec.loader is None:
            return spec
        run = spec.loader.exec_module

        def exec_module(mod):
            run(mod)
            plain = mod.render_credit

            def render_credit(*a, **k):
                tex, bbox = plain(*a, **k)
                tex = tex.copy()
                tex[..., 1:] = 0
                return tex, bbox

            mod.render_credit = render_credit

        spec.loader.exec_module = exec_module
        return spec


if "text" not in sys.modules:
    sys.meta_path.insert(0, _CreditWithoutShade())


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


# Waves of light that cross the sky: only the end card's (Apology's relight keeps its flare and thin ring)
WAVES = [(TITLE_HIT, 0.5, 0.62, 1.0)]


def _no_burst(stars):
    # Apology's relight keeps its flare and the thin ring that settles and stays, but not the wide expanding ring
    # (from light 3 it runs through the corner credit, review round 3).
    return [(s[0], -1.0, s[2]) if i == 2 else s for i, s in enumerate(stars)]


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
        star=_no_burst(star_state(t)), link=link_state(t),
    )
