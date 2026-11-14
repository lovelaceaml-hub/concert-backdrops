"""Song 11, Almighty God Who Knows the Future (the finale): the 1 minute promo, version 2 (five scenes).

Design: project-docs/designs/11 Almighty God Who Knows the Future.md, section 13 "Promo v2: scenes"
("The Gate of Mother's Love"). Promo audio: audio/promo/s11.mp3 (1:59 to 2:59 of the studio recording).

Five painted scenes (assets/plates/s11/) with people of light (assets/song_figures/s11/):
1 the promise: a faint silver city drawn above the mountain before it is built (0 to 11.5 s);
2 Mother's road: Heavenly Mother, seen only from behind, with her children on the near shore; at her words to trust
  Father and march ahead she raises her arm toward the city and all step out; Encouragement in full, then its light
  (8.5 to 26 s);
3 all nations streaming in: the city filled with gold, rivers of nine colors, the peoples of every land walking in
  from both sides (23 to 43 s);
4 the gate and the sun: the second lift blooms into the open gate with the sun inside it and the light pouring
  down the mountain; "Joy of salvation endures forever" rises out of the water (40.5 to 50.5 s);
5 peace settled: the calm golden lake with nine small glows under the nine lights, and the end card (48 to 60 s).
Signature effects done for real: the promised city filling with gold (scenes 1 to 3), the nations streaming in
(scene 3), the sun through the gate (scene 4).
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
HORIZON = 0.35         # water line, high: grand framing with a wide golden lake (song 11 look)

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


# ---------------------------------------------------------------- promo timeline
# The promo is 1:59 to 2:59 of the studio recording (song second = promo second + 119.0). Lyric times are measured
# word times from a speech-to-text pass of the recording (2026-11-13), not estimates.
CLIP_START = 119.0
MOTHER = 121.2 - CLIP_START      # verse 2 begins: Mother, who planned the future
MARCH = 129.9 - CLIP_START       # her words to trust Father and march ahead
HOPE = 141.3 - CLIP_START        # hope engraved in every heart, now fulfilled
KINGS = 150.6 - CLIP_START       # all kings worship and run to the Church of God
LIFT = 160.5 - CLIP_START        # the second lift (measured step up in loudness)
JOY = 162.1 - CLIP_START         # joy of salvation
FOREVER = 165.5 - CLIP_START     # endures forever
TITLE_HIT = 52.4                 # end card: title complete; the tagline is solid from 54.6 to the fade at 59.6
NINTH = LIFT                     # the whole arch glows from the second lift on: the finale's glory

# Reading-time contract (PHASE2.md item 4): formation takes about 3.75 s, so hold >= form + 9.75.
ENC_FORM = MARCH + 0.6           # 11.5: the words form as her arm rises toward the city
ENC_HOLD = ENC_FORM + 9.9        # 21.4: fully formed and solid from about 15.25 to 21.4 (6.15 s)
ENC_ARRIVE = ENC_HOLD + 1.6      # 23.0: the words reach light 7 (flare and a fresh ring)
# The one fragment, engraved in place: 41.5 to 44.0, solid 44.0 to 47.5 (3.5 s), gone by about 48.9, so the end
# card (forming from 49.4) starts after a clean gap (Astra round 1, finding 9).
FRAG_T0, FRAG_T1, FRAG_OUT = LIFT, LIFT + 2.5, LIFT + 6.0

SKYLINE_LANTERN = 0.0            # all plates: hide the light that travels along the drawn skyline
BOTTOM_CALM = 1.0                # calm lower third (PHASE2.md item 6)
# Rings each light already earned before this minute (DESIGN-SYSTEM.md 12a star history): light 7 in songs 02, 03,
# 05 and 09; light 3 in 04; light 4 in 06; light 8 in 07; light 9 in 08; light 2 at this song's thanks to Father
# (1:51). Index 0 is light 1.
RINGS_AT_START = {1: 1, 2: 1, 3: 1, 6: 4, 7: 1, 8: 1}

# Song 11 look (DESIGN-SYSTEM.md section 6): a radiant full sunrise, the brightest scene of the night. White gold,
# sky blue and all nine colors; full rays; a clear sky; the complete arch; grand framing with a high horizon.
NINE = ["#FF977C", "#FFD05F", "#FFAD69", "#F582AF", "#82B0ED", "#CE927E", "#B293E7", "#EF7A96", "#BE9CEB"]


def _nine_pair(rate, offset):
    def f(t):
        k = int(t * rate + offset) % 9
        return (NINE[k], NINE[(k + 4) % 9])
    return f


# Procedural sky and lake (only seen where no plate covers the frame; kept in the song 11 look)
PAL = {
    "clear": ("#0d3880", "#2c69b9", "#f5c07c", "#ffe8c2"),
    "glory": ("#124c9a", "#3f82d0", "#fcd9a4", "#fff3da"),
}
_pal_keys = [(0.0, "clear"), (LIFT, "glory"), (TOTAL, "glory")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.80), (TOTAL, 0.80)])
SUN_Y = Track([(0, 0.40), (TOTAL, 0.47)])
SUN_SIZE = Track([(0, 0.14), (TOTAL, 0.16)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.10), (TOTAL, 0.10)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
AURORA_WARM = _nine_pair(0.18, 0)
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])
FADE = Track([(0, 0.0), (1.0, 1.0), (TOTAL - 0.4, 1.0), (TOTAL - 0.02, 0.0)])
# white-gold motes in the air, quieter while words are on screen
MOTES = Track([(0, 0.30), (ENC_FORM, 0.30), (ENC_FORM + 2, 0.18), (ENC_ARRIVE, 0.18), (ENC_ARRIVE + 2, 0.55),
               (LIFT - 1, 0.70), (LIFT + 1, 0.30), (TITLE_HIT - 2, 0.30), (TOTAL, 0.25)])
MOTE_COLORS = ("#fff6e2", "#ffe2a0")
# lights in all nine colors rising from the rivers: the words practiced on the way as the nations stream in
LANTERNS = Track([(0, 0.0), (24.0, 0.0), (29.0, 0.70), (KINGS, 0.85), (LIFT - 1.5, 0.85), (LIFT + 0.3, 0.10),
                  (LIFT + 2.0, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = _nine_pair(0.5, 2)
# the usual veil behind the words; the plates are lowered under the text instead
TEXT_SHADOW = Track([(0, 1.05), (TOTAL, 1.05)])

# A. five painted scenes (assets/plates/s11/); each crossfade starts the next plate at this t1 - fade_out
_P = "assets/plates/s11/"
SCENES = [
    # 1 the promise: faint silver city lines above the mountain, faint riverbeds; slow push toward the mountain
    dict(image=_P + "s11_promise.jpg", t0=0.0, t1=11.5, fade_in=0.4, fade_out=3.0,
         zoom=(1.03, 1.10), pan=((0.0, 0.0), (0.0, 0.01)), water=True, water_line=0.477,
         gain=Track([(0, 0.88), (6.5, 0.88), (8.5, 1.0), (TOTAL, 1.0)])),
    # 2 Mother's road: on her first words a soft bloom of light, the violet-gold road across the water
    dict(image=_P + "s11_road.jpg", t0=8.5, t1=26.0, fade_in=3.0, fade_out=3.0, transition="bloom", flash=0.35,
         zoom=(1.04, 1.12), water=True, water_line=0.47,
         # people of light are added light, so the bright morning is calmed while they stand on the shore
         gain=Track([(0, 0.62), (10.5, 0.55), (ENC_HOLD, 0.55), (ENC_ARRIVE + 1.5, 0.85), (TOTAL, 0.85)])),
    # 3 all nations streaming in: the camera follows the road (push) into the city filled with gold
    dict(image=_P + "s11_nations.jpg", t0=23.0, t1=43.0, fade_in=3.0, fade_out=2.5, transition="push",
         zoom=(1.12, 1.04), water=True, water_line=0.37,
         gain=Track([(0, 0.85), (25.5, 0.58), (39.5, 0.58), (LIFT, 0.9), (TOTAL, 0.9)])),
    # 4 the gate and the sun: the second lift blooms into the open gate
    dict(image=_P + "s11_gate.jpg", t0=40.5, t1=51.5, fade_in=2.0, fade_out=2.0, transition="bloom", flash=0.9,
         zoom=(1.10, 1.04), water=True, water_line=0.175, water_strength=0.6,
         gain=Track([(0, 1.0), (LIFT, 1.0), (LIFT + 1.2, 0.60), (FRAG_OUT + 1.2, 0.60), (51.5, 0.75)])),
    # 5 peace settled: a low view from the water's edge, the nine glows large on the calm lake, the city cut by the
    # top of the frame (a different composition from scene 3); a soft bloom after the fragment has gone; end card
    dict(image=_P + "s11_rest.jpg", t0=49.5, t1=61.0, fade_in=2.0, fade_out=0.0, transition="bloom", flash=0.3,
         zoom=(1.62, 1.55), pan=((0.0, -0.14), (0.0, -0.15)), water=True, water_line=0.378, water_strength=0.7,
         gain=Track([(0, 0.9), (TITLE_HIT - 1.5, 0.62), (TOTAL, 0.62)])),
]

# B. people of light
_F = "assets/song_figures/s11/"
_NOW = [0.0]     # the frame time, set by params() before the engine draws the figures


class _Moving(dict):
    """A figure whose x, y and height may be Tracks: the engine reads them with .get() each frame, so the people
    walk (the engine itself takes plain numbers only)."""

    def get(self, k, default=None):
        v = dict.get(self, k, default)
        return v(_NOW[0]) if isinstance(v, Track) else v


FIGURES = [
    # Heavenly Mother, seen only from behind, robed and veiled, with a child holding her robe, a young woman and an
    # elder with a staff; at her words to trust Father and march ahead she raises her arm toward the city and all
    # step out together, walking right and up onto the road of light. Then the sparks fly to light 7 with the words.
    _Moving(poses=[_F + "s11_mother_children_a.png", _F + "s11_mother_children_b.png"],
            t0=7.6, t1=ENC_HOLD - 0.5, pose_times=[MARCH], morph=2.0,
            x=Track([(0, 0.28), (15.0, 0.28), (21.0, 0.37), (TOTAL, 0.37)]),
            y=Track([(0, 0.18), (15.0, 0.18), (21.0, 0.215), (TOTAL, 0.215)]),
            height=Track([(0, 0.40), (15.0, 0.40), (21.0, 0.375), (TOTAL, 0.375)]),
            to_star=6, color="#cdb6ff", glass=1.0),
    # the peoples of every land streaming in along the two rivers of light toward the gate: two different groups,
    # walking inward and a little up the river bands, at different heights and times
    _Moving(poses=[_F + "s11_crowd_left.png"], t0=24.5, t1=39.0,
            x=Track([(0, 0.13), (24.5, 0.13), (39.0, 0.26), (TOTAL, 0.26)]),
            y=Track([(0, 0.235), (24.5, 0.235), (39.0, 0.265), (TOTAL, 0.265)]),
            height=Track([(0, 0.30), (24.5, 0.30), (39.0, 0.27), (TOTAL, 0.27)]),
            to=(0.5, 0.66), color="#ffd58a", particles=11000, dissolve=3.0, glass=1.1),
    _Moving(poses=[_F + "s11_crowd_right.png"], t0=26.5, t1=39.8,
            x=Track([(0, 0.88), (26.5, 0.88), (39.8, 0.75), (TOTAL, 0.75)]),
            y=Track([(0, 0.25), (26.5, 0.25), (39.8, 0.28), (TOTAL, 0.28)]),
            height=Track([(0, 0.33), (26.5, 0.33), (39.8, 0.30), (TOTAL, 0.30)]),
            to=(0.5, 0.66), color="#ffc0d8", particles=11000, dissolve=3.0, glass=1.1),
]

# C. the sun through the gate is painted into plate 4 and revealed by the bloom of light at the second lift

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = dict(form=1e9, hold=1e9, star=-100.0)     # lit in an earlier song (all nine are lit before the finale)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **LIT),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **LIT),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **LIT),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **LIT),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    # Encouragement shines again: Heavenly Mother tells her children to trust Father and march ahead
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=96, y=0.30,
         form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)

# D. design fragment 3 in one piece, engraved in gold at the second lift, high above the gate so the sun inside it
# stays clear
FRAGMENTS = [
    dict(text="Joy of salvation endures forever", t0=FRAG_T0, t1=FRAG_T1, out=FRAG_OUT, dy=0.175, size=92,
         glow="#ffcf7a", style="engrave"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.8, t1=TITLE_HIT + 2.2)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Almighty God Who Knows the Future", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.4, t_move=5.2, t_rest=7.0, scale=0.34, alpha_rest=0.58,
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(TITLE_HIT - 3.0, TITLE_HIT - 1.5, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light across the sky: Encouragement reaching its light again, the whole arch answering the second lift,
# and the end card
WAVES = [(ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.7),
         (LIFT, 0.5, 0.86, 0.9),
         (TITLE_HIT, 0.5, 0.62, 1.1)]


def params(song, t):
    _NOW[0] = t
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
