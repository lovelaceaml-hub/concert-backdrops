"""Song 01, All You Stars of Zion: the 1 minute promo, version 2 (design "From Starlight to Sunrise").

The minute is 3:01 to 4:01 of the studio recording: the final chorus, from the last stars of the night to the
first sunrise of the concert. Five painted scenes: the stars come down over the night lake (the morning star
flares on the loudest moment); "dew of the dawn" written in light across a dawn web in the violet blue hour;
"Arise" rising out of the lake as the sun breaks the ridge; Encouragement acted out by people of light on the
golden morning shore beside the tree of light, with two torch bearers raising their torches toward the one who
kneels, then star 7 lit for the first time in the concert (Compliment, star 9, was lit earlier in the song);
the end card over the clear morning with the faint heavenly city of light beyond the mountains.
Audio: audio/promo/s01.mp3 (60 s clip). Live the song is a 3:08 brass version with no singing.
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
MUSIC_END = 59.3       # last sounding moment of the clip (final chord at 4:00 of the recording)
SONG_END = 60.0        # length of the clip
TOTAL = 60.0           # promo length
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.24         # water line, fraction of the height from the bottom: low, for the big sky of song 01

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
        hgt = 0.020 + 0.080 * v + 0.070 * mid * (0.35 + v) + (0.020 + 0.055 * v) * (crag - 0.5)   # lower: this clip is loud throughout
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


# Landmarks in the promo minute (seconds of the clip; add 181 for the recording). Measured loudness:
# rise 4 to 9, loudest moment 9, lift 21, sunbeam pocket 32, full plateau 41 to 58, final chord ends 59.
RISE = 4.0
PEAK = 9.0
SUNRISE = 21.0
BEAMS = 32.0
PLATEAU = 41.0
NINTH = 1e9            # the whole arch does not glow in song 01
TITLE_HIT = 52.0       # end card
ENC_FORM = 36.5        # Encouragement words start forming (solid from about 40.25)
ENC_HOLD = 46.5        # Encouragement words start flying to star 7 (6.25 s solid)
ENC_STAR = 47.9        # star 7 (Encouragement) lit for the first time in the concert
SKYLINE_LANTERN = 0.0  # every scene is a painted plate with its own mountains
BOTTOM_CALM = 1.0      # calm lower third for the performers (Astra round 1, finding 12)

# Procedural sky: only shows where a plate is not fully in (the first second); kept in song 01's colours
PAL = {
    "lastnight": ("#03071c", "#0b1440", "#2a2a62", "#a69ad0"),
    "dawn":      ("#0a1848", "#3a3274", "#c4787a", "#ffc890"),
    "morning":   ("#173a74", "#8c7282", "#ffc47c", "#ffeacc"),
}
_pal_keys = [(0.0, "lastnight"), (12.0, "lastnight"), (22.0, "dawn"), (40.0, "morning"), (TOTAL, "morning")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 0.0), (TOTAL, 0.0)])      # each plate paints its own sun
SUN_Y = Track([(0, 0.24), (TOTAL, 0.41)])
SUN_SIZE = Track([(0, 0.10), (TOTAL, 0.13)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])        # the night plate carries the stars and the Milky Way
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])       # a clear sky
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])       # no aurora in song 01 (it belongs to songs 03 and 08)
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.0), (TOTAL, 0.0)])         # the sunrise plates paint their own rays
PART = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 1.0), (TOTAL, 1.0)])         # the plates carry the camera moves
EXPOSURE = Track([(0, 1.0), (44, 1.0), (51, 0.88), (TOTAL, 0.86)])   # calmer light behind the end card
FADE = Track([(0, 0.0), (1.2, 1.0), (58.6, 1.0), (59.9, 0.0)])
# the stars come down: silver motes falling slowly through the night, turning gold at sunrise
MOTES = Track([(0, 0.14), (4, 0.20), (9, 0.30), (15, 0.20), (21, 0.26), (30, 0.20), (36, 0.14), (50, 0.14),
               (TOTAL, 0.18)])
MOTE_Y = (1.05, 0.18)


def _mix_hex(a, b, u):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02x}" for x, y in zip(ca, cb))


def MOTE_COLORS(t):
    u = min(max((t - 14.0) / 9.0, 0.0), 1.0)
    u = u * u * (3 - 2 * u)
    return (_mix_hex("#e8ecff", "#ffe6b0", u), _mix_hex("#c8b8ff", "#ffc890", u))


# A. Five scenes (painted plates, assets/plates/s01/), from the last stars of the night to the first morning.
# 1 the stars come down: navy night, Milky Way arching over the lake, falling stars, the morning star on the horizon
# 2 dew of the dawn: close on the shore in the violet blue hour, silk threads of a dawn web, the lake blurred
# 3 Arise: the sun breaking over the ridge, rays filling the sky, a golden road on the water
# 4 Encouragement: the golden morning shore, sunbeams through the haze, the tree of light at the left edge
# 5 the morning of hope: clear gold morning, the faint heavenly city of light above the mountains, the end card
SCENES = [
    dict(image="assets/plates/s01/s01_night_lake.jpg", t0=0.0, t1=14.5, fade_in=1.0, fade_out=3.5,
         zoom=(1.03, 1.11), pan=((0.0, 0.0), (0.0, 0.012)), water=True, water_line=0.24, water_strength=0.7,
         gain=Track([(0, 1.0), (2.0, 0.82), (7.0, 0.82), (9.0, 1.05), (11.0, 1.0), (TOTAL, 1.0)])),
    dict(image="assets/plates/s01/s01_dawn_web.jpg", t0=11.0, t1=24.0, fade_in=3.5, fade_out=3.0,
         transition="dissolve", zoom=(1.10, 1.02), pan=((-0.02, 0.0), (0.0, 0.0)), water=True, water_line=0.32,
         water_strength=0.5, gain=Track([(0, 0.95), (12.0, 0.85), (18.5, 0.85), (20.5, 1.0), (TOTAL, 1.0)])),
    dict(image="assets/plates/s01/s01_sunrise.jpg", t0=21.0, t1=34.0, fade_in=3.0, fade_out=3.5,
         transition="bloom", flash=0.85, zoom=(1.02, 1.10), pan=((0.0, -0.01), (0.0, 0.0)), water=True,
         water_line=0.22, water_strength=0.8,
         gain=Track([(0, 1.0), (23.0, 1.0), (24.5, 0.78), (29.5, 0.78), (31.5, 0.95), (TOTAL, 0.95)])),
    dict(image="assets/plates/s01/s01_morning_beams.jpg", t0=30.5, t1=51.3, fade_in=3.5, fade_out=3.5,
         transition="push", zoom=(1.10, 1.17), pan=((0.035, 0.0), (0.05, 0.0)), water=True, water_line=0.19,
         water_strength=0.7,
         gain=Track([(0, 1.0), (31.5, 1.0), (34.0, 0.78), (37.0, 0.72), (47.5, 0.72), (TOTAL, 0.8)])),
    dict(image="assets/plates/s01/s01_heavenly_city.jpg", t0=48.3, t1=61.0, fade_in=3.0, fade_out=0.0,
         transition="dissolve", zoom=(1.06, 1.0), water=True, water_line=0.21,
         water_strength=0.6, water_bottom=0.20,
         gain=Track([(0, 0.95), (49.0, 0.9), (51.5, 0.76), (TOTAL, 0.76)])),
]

# B. People of light. Encouragement acted out in full on the morning shore (the shared library): the young man
# kneels exhausted and his friend prays over him; she rests a hand on his back and cheers him on as he begins to
# rise; they stand and lift their joined hands. Two torch bearers (song 01's special figures) stand on the shore
# and raise their torches toward him; at the end every flame lifts as sparks into the new violet light.
_ENC_C = "#e2d2ff"
FIGURES = [
    dict(poses=["assets/figures/encouragement_a.png", "assets/figures/encouragement_b.png",
                "assets/figures/encouragement_c.png"],
         t0=31.5, t1=ENC_HOLD - 0.5, pose_times=[35.5, 41.0], x=0.5, y=0.21, height=0.37, to_star=6,
         color=_ENC_C, glow=1.05),
    dict(poses=["assets/song_figures/s01/s01_torchbearer_a.png"], t0=33.0, t1=ENC_HOLD - 0.3,
         x=0.21, y=0.21, height=0.32, to_star=6, color="#ffd796", glow=0.9, particles=7000),
    dict(poses=["assets/song_figures/s01/s01_torchbearer_b.png"], t0=34.0, t1=ENC_HOLD - 0.1,
         x=0.79, y=0.21, height=0.38, to_star=6, color="#ffd796", glow=0.9, particles=7000, flip=True),
]

# C. Effect layers: a sunbeam falls on the kneeling young man before the words form (it is gone before they
# are solid), and soft flashes on the morning star (the loudest moment) and on the new star.
BEAM = Track([(0, 0.0), (32.5, 0.0), (34.5, 0.55), (36.0, 0.55), (38.5, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.60, 1.02)
BEAM_TO = (0.52, 0.22)
BEAM_WIDTH = (0.02, 0.09)
BEAM_COLOR = "#ffe6b0"
FLASH = Track([(0, 0.0), (8.4, 0.0), (9.0, 0.22), (10.6, 0.0), (47.7, 0.0), (48.1, 0.16), (49.5, 0.0),
               (TOTAL, 0.0)])
TEXT_SHADOW = Track([(0, 1.0), (19.0, 1.0), (22.0, 1.6), (TOTAL, 1.7)])   # deeper veil on the bright dawn plates

# Nine lights on an arch over the stage, one for each expression (campaign order, left to right)
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

_NOT_YET = dict(form=1e9, hold=1e9, star=1e9)
PHRASES = [
    # label, lines, max font px, form start, hold end, star time
    dict(label="Greeting", lines=["“How are you?”"], size=176, **_NOT_YET),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **_NOT_YET),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **_NOT_YET),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **_NOT_YET),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **_NOT_YET),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **_NOT_YET),
    # lit for the first time in the concert, on the final "Now let us arise" (the full plateau)
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=100,
         y=0.30, form=ENC_FORM, hold=ENC_HOLD, star=ENC_STAR),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **_NOT_YET),
    # lit earlier in this song (verse 1, "faithful and beautiful work"), already shining in this minute
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=1e9, hold=1e9,
         star=-100.0),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit before this minute: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)

# D. Short lyric fragments (never on screen together with an expression), each in its own way:
# "dew of the dawn" is written by a pen of light, like the first light running along the dawn web's threads;
# "Arise" first lies in the lake as a golden reflection, then rises out of the water as the sun breaks the ridge.
FRAGMENTS = [
    dict(text="dew of the dawn", t0=11.6, t1=14.6, out=18.6, dy=0.0, size=92, glow="#d8c8ff", style="write"),
    dict(text="Arise", t0=21.0, t1=25.0, out=29.6, dy=0.0, size=170, glow="#ffd9a0", style="reflection",
         line=0.22),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="All You Stars of Zion", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.3, t_full=1.5, t_move=6.0, t_rest=8.0, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky when a light is lit (time, x, y, strength)
WAVES = [(ENC_STAR, STAR_POS[6][0], STAR_POS[6][1], 1.1), (TITLE_HIT, 0.5, 0.62, 1.2)]


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
