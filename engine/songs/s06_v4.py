"""Song 06, Heavenly Mother Tells Us to Be Grains: the 1 minute promo, version 4 (round 4 direction: the ORIGINAL
engine style, according to this song). Built like engine/songs/s03_original.py: the engine's own luminous world
(a deep sky, a still lake with a mountain line and its mirror, golden dust, the arch of nine lights) with words of
glowing gold light and nothing dark behind any text (TEXT_SHADOW = 0). No painted plates and no people.

Timed to audio/promo/s06.mp3, which is 62.0 to 122.0 s of the 2:06 guide recording (end of verse 1 through the end
of the song). Concession is lit for the first time (a provisional placement exception awaiting Anthony's decision,
not an exact lyric match: the line is about self sacrifice, the campaign phrase means letting another go first)
and Inclusiveness shines again after "Pardon one another".

Six scenes, all from the engine's own layers, in the song's harvest evening look (DESIGN-SYSTEM.md section 6):
  1. 0 to 9      the harvest field: golden field of light in front of the lake, long low sun, rays, golden dust
  2. 9 to 21     the path of light (Concession): the sun touches the hills and lays a narrow path on the water
  3. 21 to 33    the rose afterglow (Inclusiveness): first faint stars, a few lanterns, rings on the water;
                 the light of Inclusiveness is relit (the relit lantern)
  4. 33 to 41    the wilderness: the lake dries into cracked earth, then living gold water fills the cracks
  5. 41 to 47    the fragrance on the wind: clouds part, golden dust swirls, the field grows back
  6. 47 to 60    the edge of heaven: the last grain falls into the lake (a thin shaft of light and one ring),
                 the sun rises again, lanterns lift, the three line end card

Everything the renderer needs is a pure function of time, so any frame can be rendered on its own.
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
HORIZON = 0.27         # water line: low, a wide harvest sky (song 06 framing)

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
        # the last grain falls into the lake: three slow rings widen from where the shaft meets the water
        g0, gx, gy = GRAIN
        special = []
        for lag, s in ((0.0, 1.6), (0.7, 1.1), (1.5, 0.8)):
            age = t - g0 - lag
            if 0.0 <= age < 9.0:
                special.append((gx, gy, age * 0.5, s))
        return (special + out)[:n]


# ----------------------------------------------------------------- timeline


from track import Track   # noqa: E402

NINTH = 1e9            # the whole arch does not glow as one in this song

# Reading time: words form over about 3.75 s, stay solid at least 6 s (hold >= form + 9.75), dissolve over about
# 1.6 s; the next text starts at least 0.5 s after that.
C_FORM, C_HOLD = 10.0, 19.8         # Concession: solid 13.75 to 19.8; dissolved by 21.4; star lit 21.3
I_FORM, I_HOLD = 21.9, 31.7         # Inclusiveness: solid 25.65 to 31.7; dissolved by 33.3; relit 33.2
F1 = (34.8, 37.2, 39.4)             # "waters this wilderness" (engraved in gold as the water fills the cracks)
F2 = (41.2, 43.6, 46.0)             # "the fragrance of Her love"
TITLE_HIT = 51.1                    # title forms from 48.1; end card complete 54.6, held to the fade at 58.9
GRAIN = (47.3, 0.72, 0.14)          # the last grain reaches the lake: time, x, y

TEXT_SHADOW = 0.0         # round 4: nothing dark behind any text; the sky behind the words is kept deep instead
TEXT_PROTECT = 0.0        # no dimmed patch in the dust behind the words either
SKYLINE_LANTERN = 1.0     # the original look: a small light travels along the mountain line
# a calm lower third; a little lighter in the field and wilderness scenes, where no expression is on screen
BOTTOM_CALM = Track([(0, 0.55), (8.0, 0.55), (10.5, 1.0), (33.3, 1.0), (35.0, 0.65), (41.5, 0.65), (44.0, 0.6),
                     (TOTAL, 0.6)])
# Rings carried from earlier songs: Apology (index 2) relit once in song 04; Encouragement (index 6) relit in
# songs 02, 03 and 05.
RINGS_AT_START = {2: 1, 6: 3}

# Sky: top, middle, horizon, glow of the low sun. Harvest evening: amber, wheat gold, deep orange, never true
# night. The middle of the sky (where the words stand) stays deep in every scene so gold words read without a veil.
PAL = {
    "harvest": ("#0e0820", "#3c1a2e", "#d8803a", "#ffc070"),
    "ember":   ("#0a0720", "#311629", "#b8542c", "#ffaa58"),
    "rose":    ("#060920", "#211838", "#8e4248", "#ff9468"),
    "dust":    ("#0e0a16", "#2a1a1c", "#8a5630", "#ffb868"),
    "breath":  ("#0c0820", "#38183a", "#c8704a", "#ffc888"),
    "glory":   ("#090a24", "#2a1636", "#9a5434", "#ffc880"),
}
_pal_keys = [(0.0, "harvest"), (6.0, "harvest"), (10.5, "ember"), (19.5, "ember"), (23.5, "rose"), (32.0, "rose"),
             (34.5, "dust"), (38.5, "dust"), (42.0, "breath"), (46.0, "breath"), (50.0, "glory"), (TOTAL, "glory")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 1.0), (7, 0.9), (11, 0.75), (19.5, 0.7), (23.5, 0.5), (32, 0.45), (34.5, 0.32), (38, 0.32),
                 (41.5, 0.65), (46, 0.8), (49, 0.7), (53, 0.38), (TOTAL, 0.34)])
SUN_Y = Track([(0, 0.325), (7, 0.318), (11, 0.292), (19.5, 0.284), (23.5, 0.245), (33, 0.24), (40, 0.245),
               (46, 0.275), (49, 0.28), (54, 0.252), (TOTAL, 0.246)])
SUN_SIZE = Track([(0, 0.12), (TOTAL, 0.125)])
STARS = Track([(0, 0.12), (8, 0.18), (20, 0.24), (24, 0.36), (32, 0.4), (35, 0.2), (40, 0.12), (TOTAL, 0.14)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.45), (8, 0.45), (12, 0.3), (20, 0.3), (24, 0.2), (32, 0.22), (34.5, 0.7), (39.5, 0.65),
                (43, 0.45), (TOTAL, 0.4)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])   # no aurora: that belongs to songs 03 and 08
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.55), (8, 0.4), (10.5, 0.22), (20, 0.22), (24, 0.16), (32, 0.16), (34.5, 0.4), (39, 0.32),
               (42, 0.85), (46, 0.8), (49, 0.35), (TOTAL, 0.3)])
LANTERNS = Track([(0, 0.0), (22.0, 0.0), (25.0, 0.22), (32.0, 0.22), (34.5, 0.0), (48.0, 0.0), (51.0, 0.5),
                  (TOTAL, 0.5)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])   # no petals: fragrance is golden dust and warm glow
MOTE_COLORS = ("#ffd27a", "#ff9a3c")       # golden dust, wheat gold to deep orange
LANTERN_COLORS = ("#ffd27a", "#ffa040")
TRAIL = Track([(0, 0.2), (TOTAL, 0.25)])
ZOOM = Track([(0, 0.985), (TOTAL, 0.955)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (58.9, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.6), (8, 0.55), (10.5, 0.3), (19.5, 0.3), (23, 0.0), (40, 0.0), (43, 0.3), (47, 0.4),
              (50, 0.25), (54, 0.12), (TOTAL, 0.12)])
PART = Track([(0, 0.4), (38.5, 0.4), (41.5, 1.0), (47, 1.0), (50, 0.5), (TOTAL, 0.5)])

# Signature 1: the golden field of light (this song's own effect), in front of the lake in scenes 1, 5 and 6
GOLDEN_FIELD = Track([(0, 0.85), (7.0, 0.85), (10.5, 0.0), (40.5, 0.0), (44.0, 0.65), (48.0, 0.8), (TOTAL, 0.8)])
FIELD_LINE = Track([(0, 0.17), (30.0, 0.17), (40.0, 0.2), (TOTAL, 0.2)])
FIELD_COLOR = "#ffc35a"
FIELD_SPEED = 0.9
# Signature 2: living gold water filling the cracks. The ice layer, coloured as dry ochre earth, crusts over the lake
# after Inclusiveness, then "thaws" into pools whose glowing edges are gold water spreading through the cracks.
ICE = Track([(0, 0.0), (33.3, 0.0), (34.8, 1.0), (36.0, 1.0), (41.5, 0.0), (TOTAL, 0.0)])
ICE_LINE = HORIZON
ICE_COLOR = "#c8915a"
THAW_COLOR = "#ffcf5a"
ICE_OPACITY = 1.0
# The path of light on the water (Concession) and, at the end, the last grain falling into the lake (a thin shaft)
BEAM = Track([(0, 0.0), (9.0, 0.0), (12.0, 0.4), (19.6, 0.4), (22.5, 0.0), (46.0, 0.0), (46.8, 0.6),
              (47.6, 0.6), (48.8, 0.0), (TOTAL, 0.0)])
BEAM_FROM = Track([(0, (0.5, 0.272)), (30.0, (0.5, 0.272)), (40.0, (GRAIN[1], 0.56)), (TOTAL, (GRAIN[1], 0.56))])
BEAM_TO = Track([(0, (0.5, 0.08)), (30.0, (0.5, 0.08)), (40.0, GRAIN[1:]), (TOTAL, GRAIN[1:])])
BEAM_WIDTH = Track([(0, (0.006, 0.10)), (30.0, (0.006, 0.10)), (40.0, (0.002, 0.014)), (TOTAL, (0.002, 0.014))])
BEAM_COLOR = "#ffc070"
# Signature 3: the relit lantern: Inclusiveness shines again (ring, flare and wave), with a few lanterns on the air.
# Signature 4: the last grain: one slow widening ring where the shaft meets the lake (Song.rings_at).

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# Lit before song 06 (concert star history): 3 Apology, 4 Inclusiveness, 6 Respect, 7 Encouragement, 8 Consideration,
# 9 Compliment. This song lights 5 Concession for the first time (a provisional placement exception awaiting
# Anthony) and Inclusiveness shines again.
OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150,
         form=I_FORM, hold=I_HOLD, star=-100.0, arrive=I_HOLD + 1.5),
    dict(label="Concession", lines=["“Please, after you.”"], size=164,
         form=C_FORM, hold=C_HOLD, star=C_HOLD + 1.5),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)

# two short lyric fragments, never on screen together with an expression
FRAGMENTS = [
    dict(text="waters this wilderness", t0=F1[0], t1=F1[1], out=F1[2], dy=0.0, size=96, glow="#ffd27a",
         style="engrave"),   # carved in gold like the channels the living water fills
    dict(text="the fragrance of Her love", t0=F2[0], t1=F2[1], out=F2[2], dy=0.0, size=96, glow="#f4c6a6"),
]

# the three-line end card
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.2, t1=TITLE_HIT + 3.5)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Heavenly Mother Tells Us to Be Grains", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=1.2, t_move=3.6, t_rest=5.6, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048, t_out=(46.0, 47.6))   # leaves before the brighter end sky


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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(c["t_out"][0], c["t_out"][1], t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky when a light is lit or shines again (time, x, y, strength)
# (Inclusiveness shines again with its ring and flare only: a wave there would light the sky behind the corner
# credit; no wave under the end card title either, so the sky behind all text stays deep)
WAVES = [(PHRASES[4]["star"], STAR_POS[4][0], STAR_POS[4][1], 0.5)]


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
        star=star_state(t), link=link_state(t),   # noqa: F821 (installed by song.py from engine/arch.py)
    )


if __name__ == "__main__":
    s = Song()
    print("frames", NFRAMES, "rings", len(s.rings))
