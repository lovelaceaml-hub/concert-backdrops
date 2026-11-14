"""Song 06, Heavenly Mother Tells Us to Be Grains: the 1 minute promo, version 2 (design "The Field That Grew From
One Grain", section 11a). Timed to audio/promo/s06.mp3, which is 62.0 to 122.0 s of the 2:06 guide recording (end of
verse 1 through the end of the song). Concession is lit for the first time (a provisional placement exception
awaiting Anthony's decision, not an exact lyric match) and Inclusiveness shines again.

Six scenes: the harvest field (the engine's own lake and golden field), the narrow shore path ("Please, after you."),
the water's edge at ember dusk ("It's okay. I understand."), the cracked wilderness that living gold
water fills, the healed land in blossom, and the edge of heaven (lake, golden field, rays and rising lanterns) with
the end card. The plates in assets/plates/s06/ are Anthony's paintings (Drive folder Assets/s06); the two figures
in assets/song_figures/s06/ are his special figures turned into line art. People of light are rare and always
moving (round 3 direction): one brief appearance, never under the words.

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
HORIZON = 0.24         # water line, low: song 06 is framed wide with a big harvest sky

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

# Musical landmarks in the promo clip (seconds; clip time = guide recording time - 62.0)
PEAK_V1 = 2.0          # loudest point of verse 1 (guide 63.5 to 64.5)
VERSE2 = 8.5           # verse 2, the grains line (guide 70.5)
HUSH = 16.0            # quietest, most tender stretch (guide 78 to 85.5)
PARDON = 27.0          # "Pardon one another" (guide 89 to 90.5)
FRAGRANCE = 35.0       # fragrance (guide 97)
REFRAIN = 40.5         # final refrain (guide 102.5)
PEAK_END = 57.0        # loudest point of the song (guide 119 to 120.5)
NINTH = 1e9            # the whole arch does not glow as one in this song

# The reading-time contract (PHASE2.md item 4): words form over about 3.75 s, then stay solid at least 6 s
# (hold >= form + 9.75), then dissolve over about 1.6 s; the next text starts at least 0.5 s after that.
C_FORM, C_HOLD = 10.0, 19.8         # Concession: solid 13.75 to 19.8 (6.05 s); dissolved by 21.4
I_FORM, I_HOLD = 21.9, 31.7         # Inclusiveness: solid 25.65 to 31.7 (6.05 s); dissolved by 33.3
F1 = (35.6, 37.6, 39.9)             # "waters this wilderness": starts once the relit star's ring has passed
F2 = (42.0, 44.5, 47.5)             # "the fragrance of Her love": solid 44.5 to 47.5
TITLE_HIT = 52.6                    # title forms from 49.6 (0.5 s after the last fragment has left)

SKYLINE_LANTERN = 0.0     # the scenes have their own land; the small light along the drawn skyline is hidden
BOTTOM_CALM = 1.0         # calm lower third (Astra round 1, finding 12)
# Rings carried from earlier songs: Apology (index 2) relit once in song 04; Encouragement (index 6) relit in
# songs 02, 03 and 05.
RINGS_AT_START = {2: 1, 6: 3}

# Procedural sky and lake (scene 1, the harvest field, and scene 6, the edge of heaven). Song 06's look
# (DESIGN-SYSTEM.md section 6): a harvest evening, amber, wheat gold and deep orange, a long low sun; never night.
PAL = {
    "gold":  ("#3b2340", "#b8642e", "#f4b24e", "#ffd88a"),
    "amber": ("#2c1a36", "#94492c", "#e88a3a", "#ffc070"),
    "glory": ("#33204a", "#9a4c2c", "#d8823a", "#ffd890"),
}
_pal_keys = [(0.0, "gold"), (4.0, "amber"), (44.0, "amber"), (50.0, "glory"), (TOTAL, "glory")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])
SUN_INT = Track([(0, 1.00), (6, 0.8), (44, 0.8), (50, 0.9), (PEAK_END, 0.95), (TOTAL, 0.9)])
SUN_Y = Track([(0, 0.32), (6, 0.30), (44, 0.29), (TOTAL, 0.30)])
SUN_SIZE = Track([(0, 0.13), (TOTAL, 0.14)])
STARS = Track([(0, 0.0), (TOTAL, 0.0)])
MILKY = Track([(0, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.6), (TOTAL, 0.6)])
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])
RAIN = Track([(0, 0.0), (TOTAL, 0.0)])
MOTES = Track([(0, 0.6), (6, 0.35), (18, 0.25), (31, 0.25), (34, 0.45), (40, 0.55), (46, 0.5), (50, 0.25), (TOTAL, 0.25)])
LANTERNS = Track([(0, 0.0), (46.0, 0.0), (49.0, 0.6), (TOTAL, 0.6)])   # lanterns lift at the end (the painting has its own)
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
MOTE_COLORS = ("#ffd27a", "#ff9a3c")     # golden dust, wheat gold to deep orange
LANTERN_COLORS = ("#ffd27a", "#ffa040")   # bright paper lanterns, set apart from the dimmer dust at the end
TRAIL = Track([(0, 0.0), (TOTAL, 0.0)])
ZOOM = Track([(0, 0.98), (TOTAL, 0.96)])
EXPOSURE = Track([(0, 1.0), (45.0, 1.0), (50.0, 0.88), (TOTAL, 0.88)])
FADE = Track([(0, 0.0), (0.8, 1.0), (58.6, 1.0), (TOTAL, 0.0)])
RAYS = Track([(0, 0.75), (4, 0.6), (44, 0.6), (49, 0.75), (TOTAL, 0.7)])
PART = Track([(0, 0.5), (TOTAL, 0.5)])

# A. six scenes, Anthony's paintings in assets/plates/s06/ (from the Drive folder Assets/s06, highlights given a soft
# shoulder so the suns stay soft; wilderness_dry.jpg is derived from wilderness.jpg). Every change of scene starts
# only once the words before it have gone, or is a plain fade (attack round 2).
P = "assets/plates/s06/"
SCENES = [
    # 1. the harvest field: an ocean of golden wheat of light round the mirror lake, the long low sun, lanterns
    dict(image=P + "field.jpg", t0=0.0, t1=7.4, fade_in=0.0, fade_out=2.4, zoom=(1.06, 1.10),
         water=True, water_line=0.375, water_strength=0.5, gain=0.85, calm_gain=0.35),
    # 2. the narrow shore path between the still water and tall glowing wheat (Concession)
    dict(image=P + "path.jpg", t0=5.0, t1=21.4, fade_in=2.4, fade_out=1.6, transition="bloom", flash=0.25,
         zoom=(1.08, 1.02), pan=((0.01, 0.0), (0.0, 0.0)),
         gain=Track([(0, 1.0), (7.0, 1.0), (9.0, 0.85), (19.8, 0.85), (21.4, 1.0)])),
    # 3. the water's edge at rose ember dusk, wheat close at the left (Inclusiveness); comes in once the Concession
    # words dissolve and stays until the Inclusiveness words have gone
    dict(image=P + "shore.jpg", t0=19.8, t1=34.1, fade_in=1.6, fade_out=0.8, transition="fade",
         zoom=(1.04, 1.08), water=True, water_line=0.35, water_strength=0.4, calm_gain=0.4),
    # 4. the cracked wilderness, dry and dusty ...
    dict(image=P + "wilderness_dry.jpg", t0=33.3, t1=36.2, fade_in=0.8, fade_out=1.0, transition="fade",
         zoom=(1.02, 1.04), water=True, water_line=0.333, water_strength=0.4, calm_gain=0.35),
    # ... which the living gold water fills, spreading out from where it meets the lake, with green shoots
    dict(image=P + "wilderness.jpg", t0=34.1, t1=43.5, fade_in=1.8, fade_out=2.0, transition="ripple",
         ripple_from=(0.62, 0.34), zoom=(1.04, 1.09), water=True, water_line=0.333, water_strength=0.4, calm_gain=0.35,
         gain=Track([(0, 1.0), (34.1, 0.9), (43.5, 0.9)])),
    # 5. the fragrance: the healed land, wheat bending in the wind, white blossoms along a golden stream
    dict(image=P + "blossom.jpg", t0=41.5, t1=48.6, fade_in=2.0, fade_out=3.0, transition="fade",
         zoom=(1.03, 1.08), water=True, water_line=0.34, water_strength=0.4, calm_gain=0.35,
         gain=Track([(0, 0.9), (43.0, 0.85), (48.6, 0.85)])),
    # 6. the edge of heaven: the lake, the sea of wheat, a plain of lit homes, lanterns rising, the end card
    dict(image=P + "heaven.jpg", t0=45.6, t1=61.0, fade_in=3.0, fade_out=0.0, transition="fade",
         zoom=(1.08, 1.02), water=True, water_line=0.39, water_strength=0.5, calm_gain=0.35,
         gain=Track([(0, 0.85), (49.0, 0.85), (52.0, 0.75), (TOTAL, 0.75)])),
]

# B. people of light (round 3 direction from Anthony: people rare and always moving, never posing under the words).
# One brief appearance, Anthony's special figure (prepared with tools/prepare_figure.py, then turned into line art by
# assets/song_figures/s06/line_figure.py), moved with the engine's moving figures (UPGRADE-HOWTO G). Inclusiveness
# has no people: the relit lantern of light, the star and the words carry it (final review, round 3).
F = "assets/song_figures/s06/"
FIGURES = [
    # far along the path, before the words: the one with the sheaf steps aside as the elder with the basket passes;
    # small and soft, the pair walks along the top of the wheat toward the far end of the path and dissolves as it goes
    dict(poses=[F + "s06_concession_step_aside.png"], t0=6.4, t1=8.4, gather=1.0, dissolve=1.4, leave="drift",
         x=(0.84, 0.58), y=(0.36, 0.40), height=(0.21, 0.18), move=(6.4, 9.8), ease="linear", bob=1.0,
         color="#cfe0ff", glow=0.5),
]

# C. signature effects: the golden fields of light and the living water are in the paintings (scenes 1, 4 and 6;
# the dry land turns to living gold with a ripple); the relit lantern is the star of Inclusiveness shining again.
TEXT_SHADOW = Track([(0, 1.5), (TOTAL, 1.5)])   # bright painted skies behind the words

# Nine lights on an arch over the stage, one for each expression
STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

# Lit before song 06 (concert star history): 3 Apology, 4 Inclusiveness, 6 Respect, 7 Encouragement, 8 Consideration,
# 9 Compliment. This song lights 5 Concession for the first time (guide about 70.8 s; words 10.0 to 21.4, star 21.3; a
# placement exception awaiting Anthony) and Inclusiveness shines again after "Pardon one another" (relit 33.2).
OFF = dict(form=1e9, hold=1e9, star=1e9)
LIT = dict(form=1e9, hold=1e9, star=-100.0)
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **LIT),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=112, y=0.29,
         form=I_FORM, hold=I_HOLD, star=-100.0, arrive=I_HOLD + 1.5),
    dict(label="Concession", lines=["“Please, after you.”"], size=118, y=0.29,
         form=C_FORM, hold=C_HOLD, star=C_HOLD + 1.5),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **LIT),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **LIT),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **LIT),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **LIT),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)

# D. two short lyric fragments, never on screen together with an expression
FRAGMENTS = [
    dict(text="waters this wilderness", t0=F1[0], t1=F1[1], out=F1[2], dy=0.0, size=84, glow="#ffd27a",
         style="engrave"),   # carved in gold like the channels the living water fills
    dict(text="the fragrance of Her love", t0=F2[0], t1=F2[1], out=F2[2], dy=0.0, size=84, glow="#f4c6a6"),
]

# the three-line end card (PHASE2.md item 7)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0)

# Opening title card that then rests, small, in the top left corner
CREDIT = dict(song="Heavenly Mother Tells Us to Be Grains", concert="The Words of Mother’s Love Healing Concert",
              t_in=0.2, t_full=1.2, t_move=3.6, t_rest=5.6, scale=0.34, alpha_rest=0.58,
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


# Waves of light that cross the sky when a light is lit or shines again (time, x, y, strength)
WAVES = [(PHRASES[4]["star"], STAR_POS[4][0], STAR_POS[4][1], 0.4),
         (PHRASES[3]["arrive"], STAR_POS[3][0], STAR_POS[3][1], 0.25),   # gentle: it passes near the corner credit
         (TITLE_HIT, 0.5, 0.62, 0.6)]                                      # no haze under the end card title


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
