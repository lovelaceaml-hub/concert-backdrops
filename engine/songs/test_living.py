"""Living figures test (2026-11-15): a 30 second clip for Anthony to judge the new engine work before any song is
redone. Not a promo. Original v4 look (the engine's own luminous world, engine/songs/s03_original.py), moving from
a deep dusk into a bright campaign-theme daylight (cream, sky blue, peach; coral and navy accents) so both looks can
be compared. No plates, no lyrics, no faces, everyone clothed, nothing dark behind any text, calm lower third.

What it shows (seconds):
 0 to 9    dusk: a person of light walks across the far shore in a full stride, robe and sleeves swaying, feet
           planted on each step; she stops, turns a little toward us and lifts her arms, and her light rises
 8 to 19   dawn: Heavenly Mother, only from behind, her veil flowing in the wind; her arms open in blessing;
           the Encouragement expression forms over the dawn sky (held more than 6 seconds), then flies to its light
 18 to 30  bright campaign day (theme.py: sky blue and cream, iridescent bubbles, a few leaves of light): two
           hands of light cup, open with their fingers moving and offer a light that rises to the Consideration
           light; a painted pair (assets/figures/consideration_b.png) walks in, warped alive (sway, breath, a step
           lilt, a rippling hem and a rising current); a navy fragment; the end card in coral and navy

Audio: audio/test/s03-newsong-first-60s.mp3 (only its first 30 seconds are used).
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
MUSIC_END = 29.8       # this test uses the first 30 seconds of the song 03 test clip
SONG_END = 30.0
TOTAL = 30.0           # test length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.34         # water line: the people of light stand on the far shore, just above the calm lower third

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
        on = np.clip(d["onset"] / np.percentile(d["onset"], 99), 0.0, 1.4)
        idx = np.minimum((t * FPS).astype(int), NFRAMES - 1)
        pooled = np.zeros(NFRAMES)
        np.maximum.at(pooled, idx, on)
        self.pulse = _ar(pooled, 0.001, 0.28)
        # the mountain skyline is the loudness of the clip
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
        hgt = 0.020 + 0.120 * v + 0.060 * mid * (0.35 + v) + (0.012 + 0.030 * v) * (crag - 0.5)
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

from track import Track   # noqa: E402
import theme   # noqa: E402

NINTH = 1e9
TITLE_HIT = 27.4      # end card
BOTTOM_CALM = 1.0
TEXT_SHADOW = 0.0     # nothing dark behind any text (Anthony, round 4)

# Sky: deep dusk, then dawn in peach and sky blue, then a bright cream and sky-blue day (the campaign theme)
PAL = {
    "dusk": ("#050a26", "#151a48", "#583c6c", "#ffb48a"),
    "dawn": ("#1d3f7c", "#6b94c9", "#f2c4a6", "#ffdcb4"),
    "day":  ("#4f9bd8", "#9ccbee", "#fcecd6", "#fff2dc"),
}
_pal_keys = [(0.0, "dusk"), (8.0, "dusk"), (13.0, "dawn"), (17.5, "dawn")]
# the bright day is the campaign theme sky (engine/theme.py, UPGRADE-HOWTO section I)
_day = [Track([(0.0, v), (1.0, v)]) for v in [tr(0.0) for tr in theme.sky_tracks([(0.0, "day")])]]


def _sky(k):
    keys = [(t, lin(PAL[p][k])) for t, p in _pal_keys] + [(20.5, _day[k](0.0)), (TOTAL, _day[k](0.0))]
    return Track(keys)


SKY_TOP, SKY_MID, SKY_HOR, GLOW = (_sky(k) for k in range(4))
SKY_THEME = Track([(0, 0.0), (16.5, 0.0), (20.5, 1.0), (TOTAL, 1.0)])   # the bright campaign world from 20.5 s
BUBBLES = Track([(0, 0.0), (17.0, 0.0), (21.0, 0.5), (TOTAL, 0.5)])     # iridescent soap bubbles in the day
LEAVES = Track([(0, 0.0), (18.0, 0.0), (22.0, 0.3), (TOTAL, 0.3)])      # a few leaves of light
LEAVES_COLORS = (theme.LEAF_GREEN, theme.LEAF_GOLD)
SUN_INT = Track([(0, 0.20), (8.0, 0.22), (13.0, 0.45), (18.0, 0.55), (21.0, 0.62), (TOTAL, 0.62)])
SUN_Y = Track([(0, 0.335), (8.0, 0.34), (13.0, 0.36), (21.0, 0.40), (TOTAL, 0.41)])
SUN_SIZE = Track([(0, 0.09), (13.0, 0.11), (21.0, 0.13), (TOTAL, 0.13)])
STARS = Track([(0, 0.0), (0.3, 0.0), (2.0, 0.9), (8.0, 0.8), (13.0, 0.25), (18.0, 0.08), (TOTAL, 0.08)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.10), (8.0, 0.12), (14.0, 0.30), (21.0, 0.40), (TOTAL, 0.40)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.10), (3, 0.20), (17, 0.22), (21, 0.30), (TOTAL, 0.30)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.45), (TOTAL, 0.55)])
ZOOM = Track([(0, 1.0), (TOTAL, 0.97)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (TOTAL - 0.5, 1.0), (TOTAL - 0.05, 0.0)])
RAYS = Track([(0, 0.0), (12.0, 0.0), (16.0, 0.12), (TOTAL, 0.14)])
PART = Track([(0, 0.0), (13.0, 0.0), (18.0, 0.4), (TOTAL, 0.5)])
SKYLINE_LANTERN = Track([(0, 1.0), (8.0, 1.0), (9.0, 0.3), (TOTAL, 0.3)])


def MOTE_COLORS(t):
    return ("#ffe2a8", "#ff9f8a") if t < 14.0 else (theme.WHITE_GLOW, theme.GOLD)


# People of light (engine/UPGRADE-HOWTO.md section H): two living rigs, living hands and one painted figure warped
WALK = (1.8, 8.0)
FIGURES = [
    # 1. a person of light walks the far shore in a full stride, stops, turns toward us, lifts her arms
    dict(kind="rig", preset="person", t0=0.6, t1=9.0, gather=1.6, dissolve=2.6, x=(0.10, 0.58), move=WALK,
         ease="linear", y=0.345, height=0.36,
         actions=[(0.6, "stand"), (WALK[0] - 0.3, "walk"), (WALK[1], "stand"), (8.1, "turn", {"yaw": 0.95}),
                  (8.2, "rise")],
         color="#ffcf9a", to_star=6),
    # 2. Heavenly Mother, only from behind; her veil flows; her arms open in blessing
    dict(kind="rig", preset="person_back", t0=9.0, t1=18.2, gather=2.0, dissolve=2.8, x=0.84, y=0.345,
         height=0.38, actions=[(9.0, "stand"), (11.4, "open", {"blend": 1.6}), (14.6, "bless", {"blend": 1.8})],
         color="#ffd9b8", to_star=6),
    # 3. two hands cup, open with moving fingers, offer a light that rises to Consideration's light
    dict(kind="rig", preset="hands", t0=18.6, t1=24.0, gather=1.8, dissolve=2.6, x=0.5, y=0.39, height=0.40,
         actions=[(18.6, "cup"), (20.2, "open", {"blend": 1.3}), (21.8, "offer", {"blend": 1.2}),
                  (23.2, "release", {"blend": 0.9})],
         color="#ffd6a0", to_star=7, particles=11000),
    # 4. an existing painted figure, brought alive with the new warp (no new art)
    dict(poses=["assets/figures/consideration_b.png"], t0=19.0, t1=25.6, gather=2.0, dissolve=2.4,
         x=(0.12, 0.25), move=(19.0, 25.6), ease="linear", bob=1.0, y=0.34, height=0.27, warp=True,
         leave="drift", color="#ffcfa0", glow=0.9),
]

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=100, y=0.28,
         form=8.6, hold=18.4, star=19.6),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128,
         form=1e9, hold=1e9, star=25.2),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.GOLD)
# short phrases written for this test (not lyrics)
FRAGMENTS = [
    dict(text="every step a little lighter", t0=3.4, t1=6.2, out=8.2, dy=0.15, size=80, glow="#ffc48c"),
    dict(text="a gift of light", t0=19.4, t1=22.0, out=23.8, dy=0.16, size=88, color=theme.NAVY,
         glow=theme.WHITE_GLOW),
]
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.4, t1=TITLE_HIT + 1.6, color=theme.NAVY, glow=theme.WHITE_GLOW)
CREDIT = dict(song="Living Figures (engine test)", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.1, t_move=2.4, t_rest=3.8, scale=0.34, alpha_rest=0.58,
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


WAVES = [(TITLE_HIT, 0.5, 0.62, 0.8)]


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
