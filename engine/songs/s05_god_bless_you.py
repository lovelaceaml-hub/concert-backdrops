"""Song 05, God Bless You! (songbook 247): the 1 minute promo v2, "The Tree of Blessing".

Look: a spring afternoon full of blessing (DESIGN-SYSTEM.md section 6). Timed to audio/promo/s05.mp3, which is
2:26 to 3:26 of the ver.3 recording: the sister verse, from the prayer for her to the final climax.
Design: project-docs/designs/05 God Bless You!.md (and its Google Doc, section 14 "Promo v2: scenes").

Round 3 direction (Anthony): the promo is a clip of the real backdrop, not a film of people acting. The words,
the tree of blessing, the petals and the light carry each expression; people of light appear once, briefly and
in motion, off to the side.
Four scenes: (1) the young blossom tree on the shore (Encouragement, relit); (2) the listening shore with its
resting stone (Respect, first lit; a provisional exception awaiting Anthony, not an exact lyric match); (3) the
open spring lake, wide to the far shore (Consideration, lit in the brother verse, relit), where a pair of light
carrying a load together gathers on the far shore and drifts up into light; (4) the tree of blessing again,
closer, as the afternoon sun breaks through above it and "God bless you!" forms of blossom petals, ending on the
three-line concert card.
Line times inside the minute are estimates from loudness (the sung guide alignment is still to do).

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
HORIZON = 0.27         # water line: a little lower than other songs, for an open, airy sky

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
        # earnest prayer, careful listening and the offer of help: the lake falls still (no rings) under the words
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

# Landmarks inside the promo minute (seconds; promo time = recording time minus 146).
# Measured: breaths near 12 to 15 and 24 to 26, climax 44 to 58 (loudest of the song), fade from 58.
# Estimated from loudness (sung guide alignment still to do): the prayer line about 0 to 12, the line Respect
# is placed on about 15 to 27, the offer of help about 27 to 36, the request for fruit about 36 to 44, the last
# line 44 to 58.
# Reading time contract (PHASE2.md item 4): formation takes about 3.75 s, so hold = form + 9.75 gives 6 s fully
# formed. Each dissolve (about 1.6 s) ends before the next text starts (0.5 s gap), and every scene transition
# runs inside a gap with no text on screen. Pose changes finish before the words are fully formed.
READ = 9.75            # form to hold
ENC_FORM = 2.6         # Encouragement: the prayer for her (lit in song 01, shines again)
RESPECT_FORM = 15.5    # Respect: the brother stops and listens to his sister (first lit; provisional exception)
CONS_FORM = 28.4       # Consideration: the offer of help to her (lit in the brother verse, shines again)
FRAG_T0 = 41.4         # "God bless you!" in blossom petals, as the sun begins to break through
SUNRISE = 42.0         # the climax: the afternoon sun breaks through the haze above the tree
NINTH = 1e9            # no whole-arch glow in this song
TITLE_HIT = 52.1       # end card: the tagline is fully formed at 55.1 and holds 4.6 s before the fade
SKYLINE_LANTERN = 0.0  # no small light travelling along the drawn skyline
BOTTOM_CALM = 1.0      # calm lower third for the performers
TEXT_PROTECT = 1.0
# Star history before this minute (DESIGN-SYSTEM.md 12a): Apology lit in 03 and relit in 04 (one ring);
# Encouragement lit in 01, relit in 02, 03 and in this song's brother verse (three rings).
RINGS_AT_START = {2: 1, 6: 3}
# While prayer, listening and the offer of help are on screen the lake falls perfectly still
STILL = [(ENC_FORM - 0.5, ENC_FORM + 11.0), (RESPECT_FORM - 0.5, RESPECT_FORM + 11.0), (CONS_FORM - 0.5, CONS_FORM + 11.0)]

# Procedural sky (seen in scene 3, the open lake). Song 05's look (DESIGN-SYSTEM.md section 6): a spring
# afternoon full of blessing, fresh green gold, cream and soft rose, bright daylight, blossom petals, warm haze.
PAL = {
    "haze":    ("#2a5a98", "#5f8cc2", "#e2dfb0", "#fff0c8"),   # soft hazy afternoon
    "bright":  ("#2860a6", "#6496cb", "#e8e2b4", "#fff4d0"),   # clear bright spring afternoon
    "blossom": ("#2a63ab", "#6a9acd", "#efd9bf", "#fff1d8"),   # rose tint of blossoms in the haze
    "bless":   ("#2d66ae", "#78a5d3", "#f3e3bb", "#fff8dc"),   # the sun breaks through: full blessing light
    "golden":  ("#2b5a98", "#8fa8c8", "#efd3a0", "#ffe9b8"),   # warm late afternoon, handed to song 06
}
_pal_keys = [(0.0, "haze"), (22.0, "bright"), (34.0, "blossom"), (44.0, "bless"), (52.0, "bless"), (TOTAL, "golden")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

SUN_INT = Track([(0, 0.45), (26, 0.5), (32, 0.55), (38, 0.6), (TOTAL, 0.6)])
SUN_Y = Track([(0, 0.40), (TOTAL, 0.40)])
SUN_SIZE = Track([(0, 0.11), (TOTAL, 0.11)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.55), (TOTAL, 0.45)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.15), (2, 0.25), (38, 0.25), (44, 0.45), (50, 0.45), (54, 0.3), (TOTAL, 0.3)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.25), (26, 0.25), (34, 0.35), (44, 0.6), (49, 0.6), (53, 0.35), (TOTAL, 0.35)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (59.7, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.12), (TOTAL, 0.12)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
# spring colors: soft rose and cream blossom petals, green gold pollen of light drifting gently upward
PETAL_COLORS = ("#ffa9bf", "#fff0e2")
MOTE_COLORS = ("#f4efb0", "#fff4d6")
MOTE_Y = (-0.05, 1.05)
TEXT_SHADOW = Track([(0, 1.6), (TOTAL, 1.7)])   # bright spring plates: a deeper veil behind every word

# A. Scenes: the song's three painted plates (assets/plates/s05/), four scenes. The two "_stage" plates are the
# painted originals with the band behind the arch of lights dimmed (so the stars read over the blossom crown) and
# the painted reflections below the shore line darkened (calm lower third).
SCENES = [
    # 1. the young blossom tree on the shore: two pray for the sister
    dict(image="assets/plates/s05/p1_young_tree_stage.jpg", t0=0.0, t1=15.55, fade_in=0.8, fade_out=1.6,
         zoom=(1.10, 1.04), pan=((0.02, 0.0), (0.0, 0.0)), water=True, water_line=0.35, calm_gain=0.4,
         gain=Track([(0, 0.95), (2.6, 0.8), (15.55, 0.8)])),
    # 2. the listening shore with its resting stone: the brother stops and listens
    dict(image="assets/plates/s05/p2b_listening_shore_stage.jpg", t0=13.95, t1=28.45, fade_in=1.6, fade_out=1.6,
         transition="fade", zoom=(1.04, 1.11), pan=((0.0, 0.0), (0.015, 0.0)), water=True, water_line=0.38, calm_gain=0.4,
         gain=0.8),
    # 3. the open spring lake: a wide view across the water to the snowy peaks and the blossoming far shore
    # (the left part of the first listening-shore painting; its resting stone stays out of frame)
    dict(image="assets/plates/s05/p2_listening_shore.jpg", t0=26.85, t1=41.35, fade_in=1.6, fade_out=1.6,
         transition="ripple", ripple_from=(0.42, 0.36), zoom=(1.50, 1.46), pan=((-0.15, -0.06), (-0.155, -0.06)),
         water=True, water_line=0.33, calm_gain=0.12, gain=0.8),
    # 4. the tree of blessing again, closer, as the sun breaks through above it; it stays for the end card
    dict(image="assets/plates/s05/p1_young_tree_stage.jpg", t0=39.75, t1=61.0, fade_in=1.6, fade_out=0.0,
         transition="bloom", flash=0.25, zoom=(1.24, 1.12), pan=((-0.08, 0.02), (-0.05, 0.0)), water=True,
         water_line=0.35, calm_gain=0.4,
         gain=Track([(0, 0.8), (42.0, 0.8), (44.0, 0.88), (46.5, 0.88), (49.0, 0.72), (TOTAL, 0.72)])),
]

# B. People of light (shared library, assets/figures/): no acting pairs under the words (round 3 direction)
# One brief appearance only, always in motion: on the far shore at the right, well clear of the words, a small
# pair of light carrying a load together walks to the right along the shore, then rises from it and dissolves
# into light (about 5 s on screen, never still, never under the words).
FIGURES = [
    dict(poses=["assets/figures/consideration_b.png"], t0=32.4, t1=36.6, gather=1.2, dissolve=2.0,
         leave="drift", x=(0.72, 0.92), move=(32.4, 37.4), ease="linear", bob=1.0,
         y=Track([(32.4, 0.345), (34.8, 0.345), (37.4, 0.50), (38.6, 0.56)]), height=0.11, color="#ffc8d4", glow=0.85),
]


# C. Signature effects: the tree of blessing (scenes 1 and 4), and at the climax the afternoon sun breaking
# through the haze above it (a column of light onto the tree, left of the words, gone before the end card);
# blossom petals form the blessing.
BEAM_FROM = (0.08, 1.04)
BEAM_TO = (0.25, 0.42)
BEAM_WIDTH = (0.05, 0.17)
BEAM = Track([(0, 0.0), (SUNRISE, 0.0), (43.0, 1.1), (46.0, 1.1), (47.6, 0.0), (TOTAL, 0.0)])
BEAM_COLOR = "#fff0c8"

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    # Lit before this minute (DESIGN-SYSTEM.md 12a): 3 Apology, 4 Inclusiveness, 7 Encouragement, 9 Compliment,
    # and 8 Consideration (first lit in this song's brother verse, before the promo minute starts).
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    # Respect, lit here for the first time: the brother stops and listens (provisional exception, see the doc)
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=92, y=0.30,
         form=RESPECT_FORM, hold=RESPECT_FORM + READ, star=RESPECT_FORM + READ + 1.2),
    # Encouragement: the prayer for her makes it shine again
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=92,
         y=0.30, form=ENC_FORM, hold=ENC_FORM + READ, star=-100.0, arrive=ENC_FORM + READ + 1.2),
    # Consideration: the offer of help to her; it shines again
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=92, y=0.30,
         form=CONS_FORM, hold=CONS_FORM + READ, star=-100.0, arrive=CONS_FORM + READ + 1.2),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# D. The song's blessing, formed of blossom petals as the sun breaks through, then blown away by the wind
FRAGMENTS = [
    dict(text="      God bless you!",   # leading spaces: centred a little right of the tree and its beam
         t0=FRAG_T0, t1=FRAG_T0 + 2.7, out=FRAG_T0 + 5.7, dy=0.03, size=140,
         glow="#ffb070", style="petals", colors=("#ffa9bf", "#fff0e2")),
]

# The three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 3.0)

# Opening title card that then rests, small, in the top left corner (moved away before the first words)
CREDIT = dict(song="God Bless You!", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=0.8, t_move=1.4, t_rest=2.4, scale=0.34, alpha_rest=0.58,
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(49.0, 50.0, t))   # gone before the end card
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of peace that cross the sky when a light is lit or shines again (time, x, y, strength):
# after each practiced word the scene visibly settles from unrest into stillness and warmth
WAVES = [(ENC_FORM + READ + 1.2, STAR_POS[6][0], STAR_POS[6][1], 0.6),
         (RESPECT_FORM + READ + 1.2, STAR_POS[5][0], STAR_POS[5][1], 0.8),
         (CONS_FORM + READ + 1.2, STAR_POS[7][0], STAR_POS[7][1], 0.85),
         (TITLE_HIT, 0.5, 0.62, 1.2)]


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


if __name__ == "__main__":
    s = Song()
    print("frames", NFRAMES, "rings", len(s.rings))
    d = np.load(FEATURES)
    t = d["times"]
    db = _db(d["rms"])
    for tt in (0, 3, 6, 12, 20, 30, 40, 46, 53, 58):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
