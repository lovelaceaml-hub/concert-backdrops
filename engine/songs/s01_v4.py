"""Song 01, All You Stars of Zion: the 1 minute promo, version 4 (round 4, the original style).

Anthony, round 4: "I don't like the dark behind the text ... Make new versions ... It just has to be according to
the song." So this version goes back to the engine's own luminous world of the first song 03 file
(engine/songs/s03_original.py): a deep sky with stars over a still lake, the skyline drawn from the music and its
mirror, motes, the arch of nine lights. No painted plates, no people of light, and nothing dark behind any words:
the words are glowing light on a sky that is kept naturally deep where they stand.

The minute is 3:01 to 4:01 of the studio recording (audio/promo/s01.mp3): the final chorus, from the last stars
of the night to the first morning of the concert. Four scenes, clearly different in sky, light and framing:
1 the stars come down (0 to 12 s): navy night, the Milky Way, falling stars streaking down toward the lake, a
  soft flash on the loudest moment (9 s); wide.
2 dew of the dawn (12 to 21 s): the violet blue hour, the Milky Way fades, silver dew drifting down, the camera
  tilts down and pushes in close over the water; "dew of the dawn" is written by a pen of light.
3 Arise (21 to 33 s): the camera pulls back level as the sun breaks the ridge, rose and gold horizon, a fan of
  sunrise rays; "Arise" lies in the lake as a reflection, then rises out of the water.
4 the morning of hope (33 to 60 s): the camera tilts up to a wide sapphire morning sky over a golden horizon, a
  slanting column of morning light on the lake at the right; ENCOURAGEMENT forms and flies into star 7 (lit for
  the first time in the concert); then the sun settles into a soft glow behind the ridge under the three-line
  end card while the camera keeps pushing in slowly.
Engine patches (this file only, applied when it loads): no dark veil or credit halo behind text, falling stars in
place of the sky's rain layer, and a moving water line for the camera tilt (HORIZON_T).
Live the song is a 3:08 brass version with no singing.
"""
import os
import sys
import numpy as np

import shaders as _G   # engine/ is on the path (song.py); patched below, for this song only

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
HORIZON = 0.24         # water line: low, for the big sky of song 01

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


# ----------------------------------------------------------------- engine patches for this song only
# Round 4: nothing dark behind any text. TEXT_SHADOW = 0 already removes the soft shadow and the tight halo; these
# two replacements make the remaining parts of the text protection follow it too (the cap that dims bright
# scenery behind words, and the dark halo of the corner credit). With TEXT_SHADOW 1 they change nothing.
_VK_OLD = "float vk = smoothstep(0.0, 0.85, shAll);"
_CR_OLD = "col *= 1.0-(ct.g*0.50+ct.b*0.34)*uCredit.w;"
if _VK_OLD in _G.COMP_FS and _CR_OLD in _G.COMP_FS:
    _G.COMP_FS = _G.COMP_FS.replace(_VK_OLD, "float vk = smoothstep(0.0, 0.85, shAll)*min(uShadeK, 1.0);")
    _G.COMP_FS = _G.COMP_FS.replace(_CR_OLD, "col *= 1.0-(ct.g*0.50+ct.b*0.34)*uCredit.w*min(uShadeK, 1.0);")
else:
    print("s01_v4: text veil patch not applied (engine changed)")

# Falling stars (DESIGN-SYSTEM.md section 6, song 01's look; the engine has none): song 01 has no rain, so the
# sky's rain layer is replaced, for this song only, by a few falling stars that streak down toward the lake.
# RAIN (below) sets their strength.
_RAIN_A = "  // a quiet rain of light"
_RAIN_B = "  o = vec4(c,1.0);"
_FALLING = """  // falling stars (song 01)
  if(uRain>0.001){
    vec2 pa = vec2(uv.x*uAspect, uv.y);
    for(int i=0;i<7;i++){
      float fi = float(i);
      float per = 2.3+1.7*hash11(fi*3.7+1.3);
      float tt = uT+fi*0.83;
      float cyc = floor(tt/per);
      float ph = tt-cyc*per;
      float life = 0.75+0.45*hash11(cyc*1.93+fi*7.1);
      if(ph<life && hash11(cyc*5.31+fi*2.9)<0.85){
        float s = ph/life;
        float hx = hash11(cyc*4.13+fi*11.7), hy = hash11(cyc*9.71+fi*3.3);
        float sd = hash11(cyc*2.77+fi*5.5)<0.5 ? -1.0 : 1.0;   // left or right of the words, falling outward
        vec2 dir = normalize(vec2(sd*(0.55+0.5*hash11(cyc*6.1+fi)), -1.0));
        vec2 p0 = vec2((0.5+sd*(0.21+0.25*hx))*uAspect, 0.70+0.26*hy);
        vec2 head = p0 + dir*(0.26+0.12*hash11(cyc*8.3+fi*1.7))*s;
        float len = 0.12*smoothstep(0.0, 0.35, s);
        vec2 rel = pa-head;
        float al = -dot(rel, dir);
        float pr = length(rel+dir*al);
        float along = clamp(al/max(len, 1e-3), 0.0, 1.0);
        float on = step(-0.003, al)*step(al, len);
        float core = exp(-pow(pr/0.0017, 2.0))*(1.0-along)*(1.0-along)*on;
        float halo = exp(-pow(pr/0.0060, 2.0))*(1.0-along)*on*0.22;
        float hd = exp(-dot(rel, rel)/(0.0042*0.0042));
        c += uRain*vec3(1.0,0.93,0.80)*(core*1.5+halo+hd*2.0)*sin(3.14159*s)*smoothstep(0.03, 0.14, h);
      }
    }
  }
"""
if _RAIN_A in _G.SKY_FS and _RAIN_B in _G.SKY_FS and "falling stars (song 01)" not in _G.SKY_FS:
    _a = _G.SKY_FS.index(_RAIN_A)
    _b = _G.SKY_FS.index(_RAIN_B, _a)
    _G.SKY_FS = _G.SKY_FS[:_a] + _FALLING + _G.SKY_FS[_b:]


# ----------------------------------------------------------------- timeline

from track import Track   # noqa: E402

# Landmarks in the promo minute (seconds of the clip; add 181 for the recording). Measured loudness:
# rise 4 to 9, loudest moment 9, lift 21, pocket 32, full plateau 41 to 58, final chord ends 59.
PEAK = 9.0
SUNRISE = 21.0
NINTH = 1e9            # the whole arch does not glow in song 01
TITLE_HIT = 50.5       # end card (title forms from 47.5, tagline complete 52.9, solid to 58.6)
ENC_FORM = 35.0        # Encouragement words start forming (fully formed about 38.75)
ENC_HOLD = 45.0        # words start flying to star 7 (6.25 s solid)
ENC_STAR = 46.4        # star 7 (Encouragement) lit for the first time in the concert
BOTTOM_CALM = 1.0      # calm lower third for the performers
TEXT_SHADOW = 0.0      # round 4: nothing dark behind any text (see the patch above)

# Palettes (top of sky, middle, horizon, glow). The middle of the sky, where the words stand, stays deep in every
# scene; the colour and light of each scene live at the horizon and in the glow.
PAL = {
    "night":    ("#02040f", "#0a1338", "#23285c", "#a69ad0"),
    "bluehour": ("#05092a", "#1b1d58", "#5a4a8e", "#c6b2ff"),
    "predawn":  ("#08103a", "#272465", "#b0607a", "#ffb890"),
    "sunrise":  ("#0b1848", "#2e2d6c", "#f08a68", "#ffd08c"),
    "morning":  ("#0c1d52", "#26377a", "#f4a870", "#ffe2b0"),
    "hope":     ("#0a1a4c", "#213272", "#d99a78", "#ffd8b0"),
}
_pal_keys = [(0.0, "night"), (11.0, "night"), (15.0, "bluehour"), (19.0, "bluehour"), (21.5, "predawn"),
             (24.5, "sunrise"), (31.0, "sunrise"), (35.0, "morning"), (46.0, "morning"), (51.0, "hope"),
             (TOTAL, "hope")]
SKY_TOP = Track([(t, lin(PAL[p][0])) for t, p in _pal_keys])
SKY_MID = Track([(t, lin(PAL[p][1])) for t, p in _pal_keys])
SKY_HOR = Track([(t, lin(PAL[p][2])) for t, p in _pal_keys])
GLOW = Track([(t, lin(PAL[p][3])) for t, p in _pal_keys])

# Camera tilt (the water line moves; params() below applies it every frame): a big sky at night, tilted down
# close over the water in the blue hour, level for the sunrise, a wider sky again for the morning and end card.
HORIZON_T = Track([(0, 0.21), (10.5, 0.21), (15.0, 0.33), (19.5, 0.33), (22.0, 0.24), (32.0, 0.24),
                   (36.0, 0.20), (TOTAL, 0.20)])

# the sun stays low, on the skyline: its light fills the horizon, never the sky where the words stand; behind the
# end card it settles into a soft glow behind the ridge so the date and place lines stand on deep sky
SUN_INT = Track([(0, 0.12), (11, 0.15), (15, 0.30), (19.5, 0.50), (21.5, 0.75), (24.5, 1.05), (31, 1.10),
                 (35, 0.85), (46, 0.85), (51, 0.55), (TOTAL, 0.55)])
SUN_Y = Track([(0, 0.205), (10.5, 0.205), (15, 0.325), (19.5, 0.325), (22, 0.235), (28, 0.265), (32, 0.275),
               (36, 0.235), (46, 0.25), (51, 0.215), (TOTAL, 0.215)])
SUN_SIZE = Track([(0, 0.10), (21, 0.10), (30, 0.12), (TOTAL, 0.13)])
STARS = Track([(0, 0.0), (0.2, 0.0), (2.5, 1.0), (12, 1.0), (18, 0.6), (24, 0.32), (34, 0.16), (TOTAL, 0.12)])
MILKY = Track([(0, 0.0), (3, 1.0), (11, 1.0), (17, 0.3), (21, 0.0), (TOTAL, 0.0)])
CLOUDS = Track([(0, 0.0), (TOTAL, 0.0)])       # a clear sky
AURORA = Track([(0, 0.0), (TOTAL, 0.0)])       # no aurora in song 01 (it belongs to songs 03 and 08)
# falling stars (the patched rain layer): through the night, most on the loudest moment
RAIN = Track([(0, 0.0), (2.0, 0.0), (3.5, 0.7), (8.4, 0.85), (9.4, 1.0), (11.5, 0.6), (14.5, 0.0), (TOTAL, 0.0)])
LANTERNS = Track([(0, 0.0), (TOTAL, 0.0)])
PETALS = Track([(0, 0.0), (TOTAL, 0.0)])
TRAIL = Track([(0, 0.0), (1.2, 0.55), (21, 0.8), (40, 1.0), (TOTAL, 0.9)])   # the morning star along the skyline
RAYS = Track([(0, 0.0), (20, 0.0), (23.5, 0.6), (31, 0.7), (35, 0.32), (46, 0.32), (51, 0.15), (TOTAL, 0.15)])
PART = Track([(0, 0.0), (TOTAL, 0.0)])
# framing: wide night; close over the water in the blue hour; pulled back for the sunrise; a slow push to the end
ZOOM = Track([(0, 1.0), (10.5, 0.985), (15.5, 0.82), (20, 0.80), (24, 1.0), (33, 0.995), (46, 0.965),
              (TOTAL, 0.935)])
EXPOSURE = Track([(0, 1.0), (47, 1.0), (51, 0.95), (TOTAL, 0.95)])
FADE = Track([(0, 0.0), (1.2, 1.0), (58.6, 1.0), (59.9, 0.0)])
# the stars come down: silver motes falling slowly through the night, turning gold at sunrise
MOTES = Track([(0, 0.05), (2, 0.14), (12, 0.18), (20, 0.24), (33, 0.32), (45, 0.40), (50, 0.30), (TOTAL, 0.30)])
MOTE_Y = (1.05, 0.18)


def _mix_hex(a, b, u):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * u)):02x}" for x, y in zip(ca, cb))


def MOTE_COLORS(t):
    u = min(max((t - 18.0) / 8.0, 0.0), 1.0)
    u = u * u * (3 - 2 * u)
    return (_mix_hex("#e8ecff", "#ffe6b0", u), _mix_hex("#c8b8ff", "#ffc890", u))


# A slanting column of morning light on the lake at the right of the frame (scene 4), clear of the words
BEAM = Track([(0, 0.0), (32.0, 0.0), (35.0, 0.42), (44.0, 0.42), (47.5, 0.0), (TOTAL, 0.0)])
BEAM_FROM = (0.99, 1.02)
BEAM_TO = (0.84, 0.25)
BEAM_WIDTH = (0.02, 0.07)
BEAM_COLOR = "#ffe6b0"
FLASH = Track([(0, 0.0), (8.4, 0.0), (9.0, 0.07), (10.6, 0.0), (46.2, 0.0), (46.6, 0.05), (48.0, 0.0),
               (TOTAL, 0.0)])

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
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118,
         form=ENC_FORM, hold=ENC_HOLD, star=ENC_STAR),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **_NOT_YET),
    # lit earlier in this song (verse 1, "faithful and beautiful work"), already shining in this minute
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, form=1e9, hold=1e9,
         star=-100.0),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=TITLE_HIT - FORM_DUR,
             hold=1e9, star=1e9, y=0.285)


def _apply_horizon(t):
    """Moves the water line for the camera tilt (HORIZON_T): here and in the engine's song module."""
    global HORIZON
    hz = float(HORIZON_T(t))
    HORIZON = hz
    sm = sys.modules.get("song")
    if sm is not None and hasattr(sm, "HORIZON"):
        sm.HORIZON = hz

# Short lyric fragments (never on screen together with an expression)
FRAGMENTS = [
    dict(text="dew of the dawn", t0=13.5, t1=16.3, out=19.8, dy=0.0, size=96, glow="#d8c8ff", style="write"),
    dict(text="Arise", t0=22.5, t1=26.5, out=30.5, dy=0.0, size=170, glow="#ffd9a0", style="reflection",
         line=HORIZON),
]

# the three-line end card
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 0.6, t1=TITLE_HIT + 2.4)

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
WAVES = [(ENC_STAR, STAR_POS[6][0], STAR_POS[6][1], 1.1), (TITLE_HIT, 0.5, 0.80, 0.35)]   # a soft wave high in the sky only


def params(song, t):
    _apply_horizon(t)
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
