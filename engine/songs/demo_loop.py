"""Pre-show loop demo (I10): a calm two minute backdrop that loops with no seam, with the event card.

The luminous original look (song 03's first version: the low warm sun over the lake, aurora, rays, a glowing
skyline, motes and a few petals) in the campaign's colours, held calm for the minutes before the concert or
during an intermission. Nothing is lit on the arch yet (pre-show). Every setting either holds still or moves
with loop_wave(), which repeats a whole number of times per loop; the engine crossfades the rest (see
engine/output.py). Needs no music: the Render workflow lays a silent track under a loop video.
"""
import os
import numpy as np

from output import loop_wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])

LOOP_SECONDS = 120.0   # the loop's length (the video is exactly this long and starts where it ends)
LOOP_XFADE = 6.0       # seconds of the hidden crossfade at the start of the loop
FPS = 30
W, H = 1920, 1080
ASPECT = W / H
TOTAL = LOOP_SECONDS
MUSIC_END = 1e9
NFRAMES = int(round(TOTAL * FPS))
HORIZON = 0.30
L = LOOP_SECONDS

RIDGE_X0, RIDGE_W = 0.035, 0.93


def lin(hexs):
    h = hexs.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0
    return c ** 2.2


def wave(t, cycles=1, phase=0.0):
    return loop_wave(t, L, cycles, phase)


class Song:
    """No music: a gentle hand-made skyline and slow periodic water rings."""

    def __init__(self):
        xs = np.linspace(0.0, 1.0, 2048)

        def lattice(freq, seed):
            r = np.random.default_rng(seed).random(int(freq) + 3)
            u = xs * freq
            i = np.floor(u).astype(int)
            f = u - i
            f = f * f * (3 - 2 * f)
            return r[i] * (1 - f) + r[i + 1] * f

        crag = sum(a * (1.0 - np.abs(2.0 * lattice(fr, 20 + k) - 1.0))
                   for k, (a, fr) in enumerate(((0.5, 16), (0.25, 35), (0.125, 78), (0.0625, 170), (0.03, 380))))
        # two soft shoulders that rise toward the middle, like the original's chorus peaks
        v = 0.55 * np.exp(-((xs - 0.30) / 0.16) ** 2) + 0.75 * np.exp(-((xs - 0.68) / 0.13) ** 2) + 0.15
        hgt = 0.020 + 0.120 * v + (0.012 + 0.030 * v) * (crag - 0.5)
        sh = np.clip(np.minimum(xs, 1.0 - xs) / RIDGE_X0, 0.0, 1.0)
        sh = sh * sh * (3 - 2 * sh)
        self.ridge = np.maximum(hgt * (0.5 + 0.5 * sh), 0.006).astype("f4")
        rng = np.random.default_rng(11)
        # 24 rings per loop at fixed places; their age wraps with the loop, so the lake loops too
        self.rings = [(float(k * L / 24 + rng.random() * 2.0), 0.10 + 0.80 * rng.random(),
                       HORIZON * (0.45 + 0.45 * rng.random() ** 1.3), 0.35 + 0.25 * rng.random()) for k in range(24)]

    def lantern(self, t):
        return 0.5, HORIZON

    def rings_at(self, t, n=16, life=4.5):
        out = []
        for t0, x, y, s in self.rings:
            age = (t - t0) % L
            if age < life and len(out) < n:
                out.append((x, y, age, s))
        return out


# ----------------------------------------------------------------- the calm loop
NINTH = 1e9
TITLE_HIT = 1e9
SKYLINE_LANTERN = 0.0     # no light travelling along the skyline (it would not loop)
BOTTOM_CALM = 1.0         # calm lower third for the stage
TEXT_SHADOW = 0.0         # no veil behind the event card: the calm sky keeps it readable

# the original's rose dawn, pulled toward the campaign's coral, gold, pink and sky blue
SKY_TOP = lin("#132358")
SKY_MID = lin("#6a4a8c")
SKY_HOR = lin("#f6947a")   # toward Greeting coral #FF977C
GLOW = lin("#ffd98f")      # toward Gratitude gold #FFD05F
AURORA_WARM = ("#f582af", "#ffd05f")   # Inclusiveness pink, Gratitude gold
AURORA_COOL = ("#82b0ed", "#b293e7")   # Concession sky blue, Encouragement violet
MOTE_COLORS = ("#ffe2a8", "#ff977c")   # warm gold and coral
PETAL_COLORS = ("#f582af", "#ffd2c2")


def MILKY(t):
    return 0.0


STAR_POS = []
for i in range(9):
    x = 0.12 + 0.095 * i
    y = 0.895 - 0.085 * ((x - 0.5) / 0.38) ** 2
    STAR_POS.append((x, y))

OFF = dict(form=1e9, hold=1e9, star=1e9)   # pre-show: no light on the arch is lit yet
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, **OFF),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"], size=118, **OFF),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], size=124, **OFF),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], size=150, **OFF),
    dict(label="Concession", lines=["“Please, after you.”"], size=164, **OFF),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], size=128, **OFF),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"], size=118, **OFF),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], size=128, **OFF),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], size=140, **OFF),
]
FORM_DUR = 3.0
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, form=1e9, hold=1e9, star=1e9)
FRAGMENTS = []
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.", t0=1e9, t1=1e9 + 1)
CREDIT = dict(song="Pre-show", concert="The Words of Mother’s Love Healing Concert",
              t_in=1e9, t_full=1e9 + 1, t_move=1e9 + 2, t_rest=1e9 + 3, scale=0.34, alpha_rest=0.58,
              margin_x=0.030, margin_top=0.048)   # no corner credit: the event card says it all

# The event card (I10): campaign title, concert title, date and time, place. Edit these for each event.
EVENT_CARD = dict(
    lines=["The Words of Mother’s Love That Bring Peace",
           "The Words of Mother’s Love Healing Concert",
           "Sunday, December 6 · 4:30 PM",
           "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas"],
    t_show=None,   # None: always on. Or seconds into the loop it fades in (with t_hide, when it fades out)
    y=0.40,        # centre of the card, from the top
)


def credit_state(t, bbox):
    x0, x1, y0, y1 = bbox
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    return (cx0, cy0, 1.0, 0.0), (cx0, cy0)


def params(song, t):
    t = t % L
    # the scene breathes on its own, in whole cycles per loop
    envs = 0.46 + 0.06 * wave(t, 6) + 0.04 * wave(t, 10, 0.3)
    hi = 0.32 + 0.08 * wave(t, 15, 0.1)
    return dict(
        t=t, env=float(envs), env_slow=float(envs), hi=float(hi), pulse=0.0,
        sky_top=SKY_TOP, sky_mid=SKY_MID, sky_hor=SKY_HOR, glow=GLOW,
        sun_int=0.92 + 0.08 * wave(t, 4), sun_y=0.36 + 0.004 * wave(t, 2), sun_size=0.125,
        stars=0.22, milky=0.0, clouds=0.62 + 0.08 * wave(t, 3, 0.2), aurora=0.38 + 0.08 * wave(t, 5, 0.6),
        rain=0.0, motes=0.40 + 0.06 * wave(t, 8), lanterns=0.0, petals=0.22 + 0.06 * wave(t, 4, 0.5),
        trail=0.75, exposure=1.0, fade=1.0, rays=0.42 + 0.08 * wave(t, 3), part=0.25, zoom=0.985 + 0.004 * wave(t),
        lantern=(0.5, HORIZON), prog=1.0, rings=song.rings_at(t), waves=[],
        star=star_state(t), link=link_state(t),
    )


if __name__ == "__main__":
    s = Song()
    print("frames", NFRAMES, "rings", len(s.rings))
