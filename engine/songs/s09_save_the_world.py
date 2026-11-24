"""Song 09, Let's Save the World (songbook 335): the 1 minute promo, "The Shore of Calling".

Timed to audio/promo/s09.mp3, 2:35 to 3:35 of the 4:34 instrumental recording (the official instrumental track,
close to the live piano solo). Line times come from the sung guide recording, matched in the cloud. The part used is
the second verse, where the early church saints call out to us, the Encouragement, and the light of glory.
Live the song is a piano solo, so the words on screen carry what the audience will not hear sung.
Design: "09 Let's Save the World - Video Design" (Google Doc) in the project's Drive folder.
All nine lights are already lit when song 09 begins; here 7 Encouragement shines again (flare and one new ring).

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

class Track:
    def __init__(self, keys):
        self.t = np.array([k[0] for k in keys], dtype=np.float64)
        self.v = np.array([np.atleast_1d(np.asarray(k[1], dtype=np.float64)) for k in keys])

    def __call__(self, t):
        if t <= self.t[0]:
            v = self.v[0]
        elif t >= self.t[-1]:
            v = self.v[-1]
        else:
            i = int(np.searchsorted(self.t, t, side="right")) - 1
            u = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
            u = u * u * (3 - 2 * u)
            v = self.v[i] * (1 - u) + self.v[i + 1] * u
        return float(v[0]) if v.shape[0] == 1 else v


# Landmarks inside the promo minute (seconds; promo time = recording time minus CLIP_START).
CLIP_START = 155.0     # the clip is 2:35 to 3:35 of the 4:34 instrumental recording (verse 2)
# Line times were measured in the cloud: the sung guide recording ("09 Let's Save the World (sung guide, for lyric
# timing).mp3") was transcribed line by line and each line's music was matched to the instrumental (chroma match 0.79
# to 0.85). In the instrumental, verse 2 runs: saints and "hardships as honor" about 2:30 to 2:42, martyrs whose souls
# call out to us 2:42 to 2:55, "Pain and sufferings ... Heaven's glory waits for us" 2:55.5 to 3:08, "cannot even
# compare" 3:08 to 3:20, "With joy ... the day of glory" 3:23 to 3:34, "Heavenly Mother is life" 3:34 (the climax).
SAINTS = 0.0           # the saints walk with their lamps through the sea mist
HONOR = 5.5            # "hardships as honor" (sung at the end of the first line, about 2:38 to 2:42)
CALL = 8.0             # the martyrs' souls call out to us: the lamps brighten together (2:42 to 2:55)
ENC_FORM = 20.5        # Encouragement at "Pain and sufferings are our destiny, but Heaven's glory waits for us" (2:55.5)
ENC_ARRIVE = 31.5      # the words rise into star 7, which shines again
GLORY = 33.0           # "All our present suff'rings cannot even compare to the glory" (3:08): the mist parts
COMPARE = 36.0         # the fragment "cannot even compare"
NINTH = 1e9            # no whole-arch glow in this song
TITLE_HIT = 50.0       # end card, as "With joy, let us work hard for the day of glory" builds to the climax
# While the Encouragement is on screen the lake falls perfectly still: peace
STILL = [(ENC_FORM - 0.5, ENC_ARRIVE)]

# Song 09 look (DESIGN-SYSTEM.md section 6): a misty sea dawn at Galilee. Teal, sea green, pearl and pale gold;
# morning mist and low cloud, glittering water, horizon mid and a wide sea. No violet, aurora, petals or rain.
# The saints walk through the grey-green sea mist before dawn; the Encouragement comes in a pearl hush;
# then the mist parts and the pale gold sun breaks through: the glory that waits for us.
PAL = {
    "seamist": ("#04141a", "#0b2e33", "#2f5a58", "#bfe0d0"),
    "mist":    ("#08242b", "#184548", "#5d8a80", "#e1eedc"),
    "pearl":   ("#0e353c", "#36686a", "#a6c4b6", "#f4f2e2"),
    "dawn":    ("#13505a", "#4f8a82", "#d6d3b2", "#fff1c8"),
    "dawnhi":  ("#1a5e66", "#6aa298", "#e8dfba", "#fff6d8"),
    # under the end card the sea sky settles back to a deeper teal so the date and place read clearly
    "endcard": ("#0c414a", "#2a6866", "#6fa293", "#f1e2b8"),
}
_pal_keys = [
    (0.0, "seamist"), (CALL, "mist"), (ENC_FORM - 1.0, "mist"), (ENC_FORM + 3.0, "pearl"),
    (ENC_ARRIVE - 1.0, "pearl"), (GLORY + 6.0, "dawn"), (TITLE_HIT - 4.0, "dawnhi"), (TITLE_HIT + 2.0, "endcard"), (TOTAL, "endcard"),
]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# the pale sun waits below the sea horizon, then breaks through the mist
SUN_INT = Track([(0, 0.10), (20, 0.16), (GLORY - 1, 0.22), (GLORY + 2, 0.55), (GLORY + 7, 0.85), (TITLE_HIT - 4, 1.0),
                 (TITLE_HIT + 2, 0.6), (TOTAL, 0.58)])
SUN_Y = Track([(0, HORIZON - 0.05), (GLORY - 1, HORIZON - 0.05), (GLORY + 8, HORIZON + 0.01), (TITLE_HIT - 2, HORIZON + 0.04),
               (TITLE_HIT + 3, HORIZON + 0.015), (TOTAL, HORIZON + 0.015)])
SUN_SIZE = Track([(0, 0.10), (GLORY, 0.10), (GLORY + 10, 0.115), (TOTAL, 0.12)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.0, 0.35), (GLORY - 3, 0.3), (GLORY + 4, 0.08), (TOTAL, 0.04)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
# morning sea mist and low cloud, thick in the night of hardship, parting for the glory
CLOUDS = Track([(0, 0.95), (CALL, 0.9), (GLORY - 1, 0.85), (GLORY + 4, 0.55), (TITLE_HIT - 6, 0.5), (TOTAL, 0.55)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
# pearl motes drifting like spray over the sea
MOTES = Track([(0, 0.15), (HONOR + 7, 0.28), (ENC_FORM - 2, 0.22), (GLORY, 0.45), (TITLE_HIT - 8, 0.6), (TOTAL, 0.5)])
MOTE_COLORS = ("#eef6ec", "#bfe3d6")
# the saints' lamps, pale gold in the mist: they brighten when the saints call out to us, then rise into the light
LANTERNS = Track([(0, 0.0), (1.5, 0.45), (CALL - 4, 0.55), (CALL, 0.9), (GLORY - 1, 0.9), (GLORY + 7, 0.25), (TITLE_HIT - 6, 0.0),
                  (TOTAL, 0.0)])
LANTERN_COLORS = ("#ffe6a8", "#f3c77c")
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.35), (GLORY - 3, 0.45), (GLORY + 5, 0.8), (TOTAL, 0.85)])
ZOOM = Track([(0, 1.0), (ENC_FORM, 0.99), (GLORY, 0.985), (TOTAL, 0.965)])
EXPOSURE = Track([(0, 1.0), (TOTAL, 1.0)])
FADE = Track([(0, 0.0), (0.8, 1.0), (59.0, 1.0), (TOTAL, 0.0)])
# soft shafts of light through the mist, never the full fan of rays (that belongs to songs 01, 06 and 11)
RAYS = Track([(0, 0.0), (GLORY - 1, 0.0), (GLORY + 4, 0.35), (TITLE_HIT - 6, 0.45), (TITLE_HIT + 2, 0.22), (TOTAL, 0.2)])
# the mist parts behind the mountains: the glory that waits for us
PART = Track([(0, 0.0), (GLORY - 1, 0.0), (GLORY + 3, 1.0), (TITLE_HIT - 6, 1.0), (TITLE_HIT - 1, 0.5), (TOTAL, 0.4)])

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

LIT = -100.0           # lit in an earlier song (all nine are lit by the end of song 08)
PHRASES = [
    dict(label="Greeting", lines=["\u201cHow are you?\u201d"], size=176, form=1e9, hold=1e9, star=LIT),
    dict(label="Gratitude", lines=["\u201cThank you. It\u2019s all thanks to you.", "You\u2019ve worked hard.\u201d"], size=118,
         form=1e9, hold=1e9, star=LIT),
    dict(label="Apology", lines=["\u201cI\u2019m sorry.", "It must have been hard on you.\u201d"], size=124, form=1e9, hold=1e9, star=LIT),
    dict(label="Inclusiveness", lines=["\u201cIt\u2019s okay. I understand.\u201d"], size=150, form=1e9, hold=1e9, star=LIT),
    dict(label="Concession", lines=["\u201cPlease, after you.\u201d"], size=164, form=1e9, hold=1e9, star=LIT),
    dict(label="Respect", lines=["\u201cI\u2019d love to hear more", "about your thoughts.\u201d"], size=128, form=1e9, hold=1e9, star=LIT),
    # Encouragement: the saints who went before us call out to us in our hardship; star 7 shines again
    dict(label="Encouragement", lines=["\u201cI\u2019ll pray (or root) for you.", "Everything will go well.\u201d"], size=118,
         form=ENC_FORM, hold=ENC_FORM + 8.5, star=LIT, arrive=ENC_ARRIVE),
    dict(label="Consideration", lines=["\u201cCan I give you a hand", "with anything?\u201d"], size=128, form=1e9, hold=1e9, star=LIT),
    dict(label="Compliment", lines=["\u201cYou\u2019re amazing.", "You\u2019re doing great!\u201d"], size=140, form=1e9, hold=1e9, star=LIT),
]
FORM_DUR = 3.0
# PHRASES keys: label, lines, size, form (words start forming), hold (words start flying), star (the light is lit).
# A light already lit in an earlier song: star=-100.0. Not lit yet in the concert: form=hold=star=1e9.
# A light lit earlier and spoken again in this song: star=-100.0 plus form, hold and arrive (when the words reach it).

# End card of the promo
TITLE = dict(label="Healing Concert", lines=["The Words of Mother\u2019s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9)
# Short lyric fragments: the words the audience will not hear sung at the piano solo. Never on screen with the expression.
FRAGMENTS = [
    # hardship glowing into honor (warm gold glow in the grey mist)
    dict(text="hardships as honor", t0=HONOR, t1=HONOR + 2.0, out=HONOR + 5.5, dy=0.0, size=80, glow="#f2b45e"),
    # as the mist parts for the light of glory (pale gold glow)
    dict(text="cannot even compare", t0=COMPARE, t1=COMPARE + 2.0, out=COMPARE + 7.0, dy=0.0, size=86, glow="#e9d79a", alpha=1.0),
]

TAGLINE = dict(text="Sunday, December 6 \u00b7 4:30 PM\nThe World Mission Society Church of God \u00b7 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 2.5,
               t1=TITLE_HIT + 5.5)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Let\u2019s Save the World", concert="The Words of Mother\u2019s Love Healing Concert",
              t_in=0.3, t_full=1.2, t_move=3.6, t_rest=5.0, scale=0.34, alpha_rest=0.58,
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


def star_state(t):
    """Brightness and time since lighting for each of the nine lights."""
    out = []
    for i, p in enumerate(PHRASES):
        age = t - p["star"]
        if age < -0.2:
            out.append((0.0, -1.0))
            continue
        gather = min(max((age + 0.2) / 0.2, 0.0), 1.0)
        base = 0.55 * gather
        flash = np.exp(-max(age, 0.0) * 1.1) * 1.3 if age >= 0 else 0.0
        if "arrive" in p and t >= p["arrive"]:
            # a light that was lit in an earlier song shines again: a softer flare
            flash += np.exp(-(t - p["arrive"]) * 1.1) * 0.9
        fin = 0.0
        if t > NINTH:
            fin = 0.35 * min((t - NINTH) / 2.0, 1.0)
        if t > TITLE_HIT:
            fin += 0.35 * np.exp(-(t - TITLE_HIT) * 0.25) + 0.15
        out.append((base + flash + fin, max(age, 0.0)))
    return out


def link_state(t):
    """How far the line of light has grown between light i and light i+1 (0..1)."""
    out = []
    for i in range(8):
        t1 = PHRASES[i + 1]["star"]
        # the line starts growing as the next light gathers and completes when it is lit
        g = min(max((t - (t1 - 1.2)) / 1.4, 0.0), 1.0)
        out.append(g * g * (3 - 2 * g))
    return out


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
    for a, b in ((20.0, 23.0), (32.0, 34.0), (57.0, 60.0)):
        m = (t >= a) & (t <= b)
        print("fine rms", a, b, " ".join(f"{x:.0f}" for x in db[m][::4]))
    for tt in (0, 5, 10, 22, 30, 36, 44, 52, 59):
        p = params(s, tt)
        print(tt, {k: (round(v, 2) if isinstance(v, float) else None) for k, v in p.items() if isinstance(v, float)})
