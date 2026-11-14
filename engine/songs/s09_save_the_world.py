"""Song 09, Let's Save the World (songbook 335): the 1 minute promo v2, "The Shore of Calling", five scenes.

Timed to audio/promo/s09.mp3, 2:35 to 3:35 of the 4:34 instrumental recording (the official instrumental track,
close to the live piano solo). Line times come from the sung guide recording, matched in the cloud. The part used is
the second verse, where the early church saints call out to us, the Encouragement, and the light of glory.
Live the song is a piano solo, so the words on screen carry what the audience will not hear sung.
Design: "09 Let's Save the World - Video Design" (Google Doc) in the project's Drive folder.
All nine lights are already lit when song 09 begins; here 7 Encouragement shines again (flare and one new ring).

Promo v2 (PHASE2.md, design section 15 "Promo v2: scenes"). The painted plates and the three special figures made
for this song in phase 1 never reached the repository (pull request 16 committed only a README), so the five
scenes are built from the engine's own layers (sky, sea mist, sun, lamps, beam, net) and the shared figure library:
1 the saints' lamps in the sea mist (0 to 8 s); 2 their souls call out to us, the lamps lifted and the camera
drawn toward them (8 to 14 s); 3 the Encouragement acted out by people of light on the perfectly still sea
(14 to 32 s); 4 the glory that waits: the mist parts and the calling light comes down onto the water (32 to 44 s);
5 the net of light cast over the world, and the end card (44 to 60 s).

Song features and the visual timeline for the backdrop. Everything the renderer needs is a pure function of time.
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
HORIZON = 0.40         # water line: horizon mid, a wide sea (song 09 look, DESIGN-SYSTEM.md section 6)

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
        # while the Encouragement is on screen the lake falls perfectly still (no rings): peace
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

# Landmarks inside the promo minute (seconds; promo time = recording time minus CLIP_START).
CLIP_START = 155.0     # the clip is 2:35 to 3:35 of the 4:34 instrumental recording (verse 2)
# Line times were measured in the cloud: the sung guide recording was transcribed line by line and each line's music
# was matched to the instrumental (chroma match 0.79 to 0.85). In the instrumental, verse 2 runs: saints and
# "hardships as honor" about 2:30 to 2:42, martyrs whose souls call out to us 2:42 to 2:55, "Pain and sufferings ...
# Heaven's glory waits for us" 2:55.5 to 3:08, "cannot even compare" 3:08 to 3:20, "With joy ... the day of glory"
# 3:23 to 3:34, "Heavenly Mother is life" 3:34 (the climax).
HONOR = 5.0            # "hardships as honor" engraved in gold over the saints' lamps
CALL = 8.0             # the martyrs' souls call out to us: the lamps are lifted and brighten together (2:43)
ENC_ACT = 14.2         # people of light gather on the still shore: one kneels, worn out; the friend prays over them
ENC_TOUCH = 19.0       # the friend rests a hand on their back and cheers them on as the words gather (2:55.5)
ENC_FORM = 20.0        # ENCOURAGEMENT forms (formation about 3.75 s, solid from about 23.8)
ENC_RISE = 25.0        # both stand and lift their joined hands in hope
ENC_HOLD = 30.0        # the words start to fly (6.2 s fully formed and solid)
ENC_ARRIVE = 32.0      # the words reach star 7, which shines again and gains a thin ring
GLORY = 32.5           # "All our present suff'rings cannot even compare to the glory" (3:08): the mist parts
COMPARE = 35.0         # the fragment "cannot even compare", written by a pen of light
NET_CAST = 43.5        # the net of light is cast from the sea and spreads over the sky
NINTH = 1e9            # no whole-arch glow in this song
TITLE_HIT = 50.0       # end card, as "With joy, let us work hard for the day of glory" builds to the climax
FORM_DUR = 3.0
# While the Encouragement is on screen the sea falls perfectly still: peace
STILL = [(ENC_ACT, ENC_ARRIVE + 0.5)]

# Rings each light carries in from songs 01 to 08 (DESIGN-SYSTEM.md 12a star history): 3 Apology relit in 04,
# 4 Inclusiveness relit in 06, 7 Encouragement relit in 02, 03 and 05, 8 Consideration relit in 07,
# 9 Compliment relit in 08.
RINGS_AT_START = {2: 1, 3: 1, 6: 3, 7: 1, 8: 1}

# Song 09 look (DESIGN-SYSTEM.md section 6): a misty sea dawn at Galilee. Teal, sea green, pearl and pale gold;
# morning mist and low cloud, glittering water, horizon mid and a wide sea. No violet sky, aurora, petals or rain.
PAL = {
    "seamist": ("#04141a", "#0b2e33", "#2f5a58", "#bfe0d0"),   # 1 night sea mist
    "mist":    ("#06202a", "#14424a", "#4f8478", "#e6e2b8"),   # 2 lamps lifted: warmer mist
    "pearl":   ("#0b2f37", "#2c5e62", "#8fb4a8", "#eef0e0"),   # 3 pearl hush before dawn
    "dawn":    ("#13505a", "#4f8a82", "#d6d3b2", "#fff1c8"),   # 4 the glory
    "morning": ("#155866", "#5d9a92", "#cfe0c8", "#fff4d6"),   # 5 morning sea
    "endcard": ("#0c414a", "#2a6866", "#6fa293", "#f1e2b8"),   # deeper teal under the end card
}
_pal_keys = [
    (0.0, "seamist"), (CALL - 1.0, "seamist"), (CALL + 3.0, "mist"), (ENC_ACT - 1.0, "mist"), (ENC_ACT + 3.0, "pearl"),
    (ENC_ARRIVE - 1.0, "pearl"), (GLORY + 5.0, "dawn"), (NET_CAST, "dawn"), (NET_CAST + 4.0, "morning"),
    (TITLE_HIT - 2.0, "morning"), (TITLE_HIT + 2.0, "endcard"), (TOTAL, "endcard"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the pale sun waits below the sea horizon, then breaks through the mist for the glory
SUN_INT = Track([(0, 0.08), (CALL, 0.10), (CALL + 4, 0.22), (ENC_ACT, 0.16), (GLORY - 1, 0.20), (GLORY + 3, 0.60),
                 (GLORY + 8, 0.90), (NET_CAST + 2, 0.95), (TITLE_HIT, 0.75), (TITLE_HIT + 3, 0.55), (TOTAL, 0.55)])
SUN_Y = Track([(0, HORIZON - 0.05), (GLORY - 1, HORIZON - 0.05), (GLORY + 7, HORIZON + 0.03),
               (NET_CAST + 2, HORIZON + 0.06), (TITLE_HIT + 3, HORIZON + 0.02), (TOTAL, HORIZON + 0.02)])
SUN_SIZE = Track([(0, 0.10), (GLORY, 0.10), (GLORY + 10, 0.12), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.0, 0.35), (ENC_ACT, 0.28), (GLORY + 4, 0.06), (TOTAL, 0.03)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
# thick sea mist in the night of hardship, thinning as the lamps lift, a hush for the Encouragement, parted by the glory
CLOUDS = Track([(0, 0.95), (CALL, 0.92), (CALL + 4, 0.72), (ENC_ACT + 2, 0.80), (GLORY - 1, 0.80), (GLORY + 4, 0.45),
                (NET_CAST, 0.40), (TOTAL, 0.45)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.15), (CALL, 0.22), (ENC_ACT, 0.14), (GLORY, 0.35), (NET_CAST, 0.45), (TOTAL, 0.40)])
MOTE_COLORS = ("#eef6ec", "#bfe3d6")
# signature 1: the saints' lamps, pale gold in the mist; lifted and brightening as their souls call out to us,
# dimmed to a few embers during the Encouragement so nothing bright sits behind the words
LANTERNS = Track([(0, 0.0), (1.5, 0.50), (CALL - 1, 0.55), (CALL + 2.5, 1.0), (ENC_ACT - 1, 1.0), (ENC_ACT + 3, 0.18),
                  (ENC_ARRIVE, 0.18), (GLORY + 5, 0.0), (TOTAL, 0.0)])
LANTERN_COLORS = ("#ffe6a8", "#f3c77c")
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.30), (GLORY - 3, 0.40), (GLORY + 5, 0.75), (TOTAL, 0.75)])
# camera: wide on the misty shore, a slow push toward the lamps as they call, a still frame for the pair,
# a push toward the light, then wide and high over the morning sea for the net
ZOOM = Track([(0, 1.0), (CALL, 1.01), (ENC_ACT - 1, 1.16), (ENC_ACT + 2, 1.04), (ENC_ARRIVE, 1.04),
              (NET_CAST - 2, 1.12), (NET_CAST + 4, 0.97), (TOTAL, 0.96)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (59.0, 1.0), (TOTAL, 0.0)])
# soft shafts of light through the mist, never the full fan of rays (that belongs to songs 01, 06 and 11)
RAYS = Track([(0, 0.0), (GLORY - 1, 0.0), (GLORY + 4, 0.14), (NET_CAST, 0.16), (TITLE_HIT - 2, 0.12), (TOTAL, 0.10)])
# the mist parts behind the mountains: the glory that waits for us
PART = Track([(0, 0.0), (GLORY - 1, 0.0), (GLORY + 3, 1.0), (TITLE_HIT - 4, 1.0), (TITLE_HIT, 0.6), (TOTAL, 0.5)])

# signature 2: the calling light, a column of pale gold that comes down through the parted mist onto the sea
BEAM = Track([(0, 0.0), (GLORY, 0.0), (GLORY + 3.5, 0.55), (NET_CAST - 1, 0.55), (NET_CAST + 3, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.5, 1.02)
BEAM_TO = (0.5, 0.35)
BEAM_WIDTH = (0.016, 0.09)
BEAM_COLOR = "#ffe9b8"
# signature 3: the net of light, cast from the sea and spreading knot by knot over the sky above the waterline
NET = Track([(0, 0.0), (NET_CAST, 0.0), (NET_CAST + 7.0, 1.0), (TOTAL, 1.0)])
NET_ORIGIN = (0.5, 0.42)
NET_Y0 = 0.42
NET_SCALE = 6.0
NET_BRIGHT = Track([(0, 0.0), (NET_CAST, 0.75), (TITLE_HIT - 3, 0.75), (TITLE_HIT, 0.22), (TOTAL, 0.22)])
NET_COLOR = "#ffe1a6"
NET_PULSE = "#fff6e2"
# a soft bloom from star 7 when the Encouragement arrives
FLASH = Track([(0, 0.0), (ENC_ARRIVE - 0.1, 0.0), (ENC_ARRIVE + 0.4, 0.22), (ENC_ARRIVE + 2.0, 0.0), (TOTAL, 0.0)])
TEXT_SHADOW = Track([(0, 1.1), (GLORY, 1.1), (GLORY + 3, 1.5), (TOTAL, 1.6)])

# People of light act out the Encouragement (shared library, assets/figures/README.md): one kneels, exhausted,
# while the friend prays over them; the friend rests a hand on their back and cheers them on; both stand and lift
# their joined hands in hope; then the sparks fly with the words into star 7.
FIGURES = [
    dict(poses=["assets/figures/encouragement_a.png", "assets/figures/encouragement_b.png",
                "assets/figures/encouragement_c.png"],
         t0=ENC_ACT, t1=ENC_HOLD - 0.5, pose_times=[ENC_TOUCH, ENC_RISE], x=0.5, y=0.23, height=0.36,
         to_star=6, color="#e6d6ff"),
]

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
    # Encouragement: the saints who went before us call out to us in our hardship; star 7 shines again
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=98,
         y=0.30, form=ENC_FORM, hold=ENC_HOLD, star=-100.0, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]

# End card of the promo (three lines, PHASE2.md item 7)
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0)

# Short lyric fragments: the words the audience will not hear sung at the piano solo. Never on screen with the expression.
FRAGMENTS = [
    # hardship carved into honor in gold, over the saints' lamps
    dict(text="hardships as honor", t0=HONOR, t1=HONOR + 3.0, out=HONOR + 7.0, dy=0.0, size=88, glow="#f2b45e",
         style="engrave"),
    # written stroke by stroke by a pen of light as the mist parts for the glory
    dict(text="cannot even compare", t0=COMPARE, t1=COMPARE + 3.2, out=COMPARE + 7.0, dy=0.0, size=90, glow="#e9d79a",
         style="write"),
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
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m)
    return (cx, cy, scale, alpha), (cx0, cy0)


# Waves of light that cross the sky (time, x, y, strength): star 7 shines again, then the end card
WAVES = [
    (ENC_ARRIVE, STAR_POS[6][0], STAR_POS[6][1], 0.8),
    (TITLE_HIT, 0.5, 0.62, 1.1),
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
