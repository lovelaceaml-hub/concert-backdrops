"""THE WORDS THAT BRING PEACE: the masterpiece. A 62 second promo for the Healing Concert "The Words of Mother's
Love That Bring Peace" (Sunday, December 6, 4:30 PM, World Mission Society Church of God, Las Vegas), on the seven
song medley with smooth blends (audio/promo/concert-medley7.mp3, MEDLEY3: 2.0 s of silence, the music fading in to
3.5, a natural ring-out to 62.0), built on the 3D layer (engine/p3d; UPGRADE-HOWTO sections V, W, X, X2, Y, Z) and
rendered at 60 fps. Approved treatment: scratchpad MASTER-TREATMENT.md.

THE IDEA
  Heavenly Mother's words of love fall from heaven as light. Wherever a word lands, light, colour and peace
  bloom: in people, in nature, across the whole world, until the Earth itself glows and settles between two
  hearts as the logo. Heavenly Mother appears only as hands of light: her open hands release the first word
  at the start.

THE TIMELINE. The film's cues were built on its own clock (the "old" time of v6, every constant below); TIME_MAP
plays that clock on the new medley (W(t_new) = t_old, smooth and monotone), so every stretch lands on its music
(new times):
  0.00   The opening title over a vast twilight sky above a sea of glowing clouds, held whole for 7 s; Mother's
         hands of light hold a drop of gold in the quiet; the music swells in from 2.0; the drop is let go (4.5)
         and falls; the title crumbles into dust (7.0 to 7.9) as we dive after it through the clouds (an eased
         1.5 s dive); it lands on a still sea of light on the 03 to 04 blend (8.0) and a ring of gold races out.
  8.75   GREETING: two men give each other a slight, warm bow. GRATITUDE: a gold woman lays her hand on her heart
         and bows as golden light pours down on her.
  15.46  (an eased carry on, on 01's downbeat) APOLOGY: in a soft rain of light a woman sits back on her
         heels, head bowed; her friend kneels beside her and lays a hand gently on her back; she lifts her head
         to her. INCLUSIVENESS: they rise together, turn to each other and embrace; the sun rises behind them.
  22.94  (a gliding carry, the 01 to 08 blend) up the river of light. CONCESSION: at a doorway of light a man steps
         aside, his hand on his heart, his other palm offering the way; petals rise from it through the door.
         On through the door (unhurried): RESPECT: two seated lean in to listen.
  31.46  (a gliding carry, the 08 to 11 blend) ENCOURAGEMENT: under a cathedral of falling light one kneels in
         prayer; her friend kneels behind her, a hand on her shoulder, the other on her heart; lights rise.
  37.35  (a gliding carry, on 11's bar) CONSIDERATION: a man reaches down and helps another up.
  40.81  (a gliding carry, the 11 to 06 blend) COMPLIMENT: a dancer gathers her arms, turns once as they open in
         a soft arc and lifts them high; hearts burst; a crowd of light claps and raises its hands.
  43.8   A still moment: motes in gold and the nine colours gather into one pearl of light over the calm sea.
  45.17  It bursts on 06's attack; we rise from rest up the column of light in one even, unhurried glide, the
         nine colours streaming with us, and break above the clouds into the glory of the sun on 06's cadence
         (47.19), easing to a hover through the breath.
  49.69  THE LIFT: the sun flares and we sweep out to the whole Earth; the nine symbols draw themselves in light
         and swirl round it through 07's climax, lighting the world; hearts bloom across it.
  52.76  They burst outward; the world becomes the logo between two hearts; light blooms into a soft pastel day;
         the logo glides into the end card, whole by the final cadence (55.0), alive to the last frame: a slow
         push-in, drifting sparkles and hearts, a breathing glow, a warm glow on the held final chord (56.75),
         settling to stillness over the last 1.5 s.

THE CONCERT INFORMATION (Anthony after v4: never flashed, at least 7 s at a time): the opening title holds
whole 0 to 7.0; from there the discreet signature stays on in the bottom left corner without a break (its
palette cross-fades to day as the sky turns bright) until the end card, which is whole from 55.0 to the last frame.

HOUSE RULES: people only in the two radiant looks, whole, few, tender, acted, with living hands; every touch
between two of the same gender (UPDATE 15), except parent and child; Heavenly Mother only as hands of light;
all nine expressions by name from words.EXPRESSIONS (exact wording, website colours), each read 2.5 s or more,
one at a time, never mirrored, centred about a third of the way down the picture with the people below them;
nothing dark behind text; no white-outs; frame 0 striking; no fade to black.
"""
import numpy as np

import songs.s03_original as _base

LEAD = 2.0                  # the quiet lead-in: the medley begins here
TOTAL = 62.0
_base.TOTAL = TOTAL
_base.NFRAMES = int(round(TOTAL * _base.FPS))
_base.MUSIC_END = 61.6
_base.SONG_END = 62.0
_base.FADE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])          # no fade in, no fade out
_base.EXPOSURE = _base.Track([(0.0, 1.0), (TOTAL, 1.0)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9                     # the nine are particle words in 3D
_base.TITLE_HIT = _base.NINTH = 1e9
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9, 1e9 + 1.0
_base.CREDIT["t_move"], _base.CREDIT["t_rest"] = 1e9 + 2.0, 1e9 + 3.0
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from track import Track  # noqa: E402
from p3d import lin  # noqa: E402
from p3d import words as PW  # noqa: E402
from p3d.api import CameraState, show  # noqa: E402
from p3d.camera import Move, Rig  # noqa: E402
from p3d import master_sky as MS  # noqa: E402
from p3d import brand as BR  # noqa: E402

AUDIO_FILE = "audio/promo/concert-medley7.mp3"
TOTAL = 62.0
NFRAMES = int(round(TOTAL * FPS))  # noqa: F405
MUSIC_END = 61.6
SONG_END = 62.0
BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0           # nothing dark behind any text
FADE = _base.FADE
EXPOSURE = _base.EXPOSURE

SEC = [LEAD + s for s in (0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47)]
BREATH_END = LEAD + 41.85
FINAL_HIT = LEAD + 58.11                         # (set again from the new medley's map below)
LAND_T = LEAD + 6.15        # the drop touches the sea (a bar start of the first song)
RELEASE_T = LEAD + 2.25     # Mother's hands let the drop go (on a beat, once the music has swelled in)
OPEN_FULL = 7.0             # the opening title is whole and still until here (Anthony: at least 7 s)
OPEN_END = 8.0              # ... and has crumbled away by here

# the nine colours of the campaign website (words.COLORS); a lighter glow for the deep ones
COL = dict(PW.COLORS)
GLOWC = dict(COL, Respect="#8a9cff", Compliment="#6f86d8")
NINE = [COL[k] for k in PW.LABELS]
NINE_GLOW = [GLOWC[k] for k in PW.LABELS]

# The two radiant looks. Until STYLES delivers crystal_light (coordinator), both are warm gold glitter: a deep
# gold, and a lighter gold for the second person of a pair, so the two stay apart.
GOLD = dict(look="glitter", color="#f2a640", color2="#ffdc96", bright=1.45)
CRYSTAL = dict(look=dict(name="glitter", seams=0.6), color="#ffc664", color2="#fff0c8", bright=1.45)

# The signature's corner (bottom left, the whole film) and the place people keep out of: its box from
# titles.py (x 0.051 to 0.521, y 0.803 to 0.915 from the top at 1080p) grown by about 40 px.
SIG_CORNER = "bl"
SIG_KEEP = (0.0, 0.55, 0.77, 1.0)            # x0, x1, y0, y1 as shares of the frame from the left and the top


def _v(x, y, z):
    return np.array([x, y, z], np.float64)


def _unit(a):
    a = np.asarray(a, np.float64)
    return a / max(float(np.linalg.norm(a)), 1e-9)


def ss(a, b, x):
    return MS.ss(a, b, x)


def sc(a, b, x):
    return MS.sc(a, b, x)


def lerp(a, b, u):
    return np.asarray(a, np.float64) * (1.0 - u) + np.asarray(b, np.float64) * u


UP = _v(0.0, 1.0, 0.0)


def _pchip_1d(x, y):
    """Monotone cubic slopes (Fritsch and Carlson): no overshoot between keys."""
    h = np.diff(x)
    d = np.diff(y) / h
    m = np.zeros_like(y)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(y) - 1):
        if d[i - 1] * d[i] <= 0.0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return m


def _pchip(keys):
    """A camera path through keys [(t, pos, target), ...] with no overshoot: f(t) -> (pos, target)."""
    ts = np.array([k[0] for k in keys], np.float64)
    P = np.array([np.r_[k[1], k[2]] for k in keys], np.float64)       # (K, 6)
    M = np.stack([_pchip_1d(ts, P[:, j]) for j in range(6)], 1)

    def f(t):
        if t <= ts[0]:
            v = P[0]
        elif t >= ts[-1]:
            v = P[-1]
        else:
            i = int(np.searchsorted(ts, t, side="right") - 1)
            h = ts[i + 1] - ts[i]
            u = (t - ts[i]) / h
            h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
            h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
            v = h00 * P[i] + h10 * h * M[i] + h01 * P[i + 1] + h11 * h * M[i + 1]
        return v[:3], v[3:]
    return f


def _aim(pos, subject, sx, sy, fov=46.0):
    """The look target from `pos` that puts `subject` at (sx, sy) of the picture (shares from the left and from
    the TOP). Used to frame the people below the words (Anthony: the words in the upper middle, the acted
    people below them) and clear of the signature's corner."""
    pos = np.asarray(pos, np.float64)
    s = np.asarray(subject, np.float64)
    dist = float(np.linalg.norm(s - pos))
    tgt = s.copy()
    th = float(np.tan(np.radians(fov) * 0.5))
    for _ in range(8):
        cam = CameraState(pos=pos, target=tgt, fov=fov, aspect=16.0 / 9.0)
        xy, _ = cam.project(s[None])
        ex, ey = float(xy[0, 0]) - sx, (1.0 - float(xy[0, 1])) - sy
        r, u, _f = cam.basis()
        tgt = tgt + r * (ex * 2.0 * th * (16.0 / 9.0) * dist) - u * (ey * 2.0 * th * dist)
    return tgt


class Warp:
    """The film's own timeline (its cues as built for v6, "old" time) played on the new medley's timeline: a
    smooth monotone curve through anchors [(new, old), ...]. W(t_new) gives t_old; W.R(t_old) gives t_new.
    Everything in the 3D layer (camera, point sets, world looks, bursts) runs on old time through it, so each
    stretch of the film keeps its shape and simply lands on the new music's cues (MEDLEY3's section map)."""

    def __init__(self, pairs):
        pairs = sorted((float(a), float(b)) for a, b in pairs)
        lo, hi = pairs[0], pairs[-1]
        pairs = [(lo[0] - 20.0, lo[1] - 20.0)] + pairs + [(hi[0] + 20.0, hi[1] + 20.0)]
        self.n = np.array([p_[0] for p_ in pairs])
        self.o = np.array([p_[1] for p_ in pairs])
        self.m = _pchip_1d(self.n, self.o)
        tt = np.arange(self.n[1] - 4.0, self.n[-2] + 4.0, 1.0 / 480.0)
        self._tn, self._to = tt, np.array([self(x) for x in tt])

    def __call__(self, t):
        t = float(t)
        n, o, m = self.n, self.o, self.m
        i = int(np.clip(np.searchsorted(n, t, side="right") - 1, 0, len(n) - 2))
        h = n[i + 1] - n[i]
        u = (t - n[i]) / h
        h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
        h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        return float(h00 * o[i] + h10 * h * m[i] + h01 * o[i + 1] + h11 * h * m[i + 1])

    def R(self, t_old):
        return float(np.interp(float(t_old), self._to, self._tn))

    def rate(self, t):
        """How fast old time runs at new time t (1: as built)."""
        return (self(t + 0.01) - self(t - 0.01)) / 0.02


# The new medley (audio/promo/concert-medley7.mp3, MEDLEY3's SECTION-MAP) against the film's own cues: (new, old).
# 0 to 2 s silence, the music fades in by 3.5; the title whole to 7.0; the dive lands on the 03 to 04 blend
# (7.99); Greeting and Gratitude in 04; the dissolve into the Apology on 01's C minor downbeat (15.46); into the
# river on the 01 to 08 blend (22.94); into the cathedral on the 08 to 11 blend (31.46); the help up inside 11;
# the carry to the dancer on the 11 to 06 blend (40.81); the pearl gathers and bursts on 06's attack (45.17); we
# break above the clouds on 06's cadence (47.19) and hover in the glory through the breath; THE LIFT (49.69):
# out to the world, the symbols swirl through 07's climax and burst on its bar (52.76); the world becomes the logo,
# the card is whole on the final cadence (55.11) and holds through the ring-out; one warm glow on the held final
# chord (56.75).
TIME_MAP = [(0.0, 0.0), (2.0, 2.0), (3.5, 3.5), (5.5, 5.5), (7.0, 7.0), (8.0, 8.15), (8.75, 8.84), (15.46, 15.3),
            (22.94, 21.85), (31.46, 28.79), (37.35, 35.36), (40.81, 38.95), (43.8, 42.21), (45.17, 43.85),
            (47.19, 46.3), (49.69, 49.2), (52.76, 52.22), (54.0, 53.85), (54.3, 54.15), (55.1, 54.95), (62.0, 62.0)]
TW = Warp(TIME_MAP)
FINAL_HIT = TW(56.75)                            # the held final chord (old time, for the glow)


class Path(Move):
    """A camera move from a function f(t) -> (pos, target)."""

    def __init__(self, f, t0, t1, **kw):
        super().__init__(t0, t1, **kw)
        self.f = f

    def pose(self, t):
        p, q = self.f(t)
        return np.asarray(p, np.float64), np.asarray(q, np.float64)


# =============================================================================================================
# GEOGRAPHY (metres, y up, the sea of light is y = 0; the light of dawn lies toward -z)
# =============================================================================================================
D0 = _v(0.0, 0.0, 7.6)                  # where the drop lands
H0 = _v(0.0, 41.0, 7.6)                 # Mother's cupped hands, high above it (a dive of about 40 m)
HAND_S = 5.0                            # their scale (hands of light, larger than life)
C0 = _v(0.0, 41.7, 10.9)               # frame 0's camera, in front of the hands
P1 = _v(-2.4, 0.0, -2.0)               # Greeting: the pair
P1b = _v(3.6, 0.0, -5.5)               # Gratitude: the gold woman under the pouring light
# The stages stand close together along the sea (Anthony after v6: no strobing whips), so the camera glides from
# one to the next in a continuous carry where the songs blend, while the scenery of each fades in and out
P2 = _v(0.0, 0.0, -18.0)               # Apology and Inclusiveness: the two kneeling in the rain, then the embrace
P3 = _v(2.0, 0.0, -34.0)               # Concession: the doorway of light on the river
P3b = _v(2.0, 0.0, -44.0)              # Respect: the two seated beyond the door
P4 = _v(-6.0, 0.0, -58.0)              # Encouragement: the cathedral of falling light
P5 = _v(6.0, 0.0, -70.0)               # Consideration
P5b = _v(12.0, 0.0, -78.0)             # Compliment: the dancer and the crowd of light
A7 = _v(12.0, 0.0, -102.0)             # the axis of the ascent
PEARL = A7 + _v(0.0, 3.2, 0.0)         # the breath: the light gathers here, and bursts on the biggest hit


def drop_pos(t):
    """The drop: held in the palms, released on the hit, falling (slowly at first) to the sea at LAND_T."""
    hold = H0 + _v(0.0, 0.10 * HAND_S * 0.5, 0.0) + _v(0.0, 0.015 * np.sin(1.3 * t), 0.0)
    if t <= RELEASE_T:
        return hold
    u = min((t - RELEASE_T) / (LAND_T - RELEASE_T), 1.0)
    e = u * u * u * (u * (6.0 * u - 15.0) + 10.0)           # it floats free, falls, and settles onto the sea
    y = float(hold[1]) * (1.0 - e)
    return _v(float(hold[0]), y, float(hold[2]))


# =============================================================================================================
# THE CAMERA
# =============================================================================================================
DIVE = (5.3, 8.45)          # the dive after the drop (one eased 3.15 s glide; the title stays whole to 7.0)


def _s0(t):
    """Frame 0 to the landing: a still, slow push on the hands under the title through the quiet lead-in and
    the swell, the release, then (as the title crumbles) the gaze turns down after the falling drop and we dive
    with it through the clouds and level out over the sea as it lands."""
    look0 = _v(0.0, 44.45, -40.0)            # looking a little up: the title stands on the deep sky
    drift = C0 + _v(0.0, 0.015 * t, -0.045 * t)
    if t < RELEASE_T:
        return drift, look0
    d = drop_pos(t)
    # the camera falls with the drop (whose own fall is eased: it floats free, falls and settles), keeping it in
    # view from a little above and behind; the distance opens out evenly, so nothing turns or jolts; after the
    # landing it drifts on over the sea
    f = sc(RELEASE_T, RELEASE_T + 0.6, t)                    # from the release (the drop barely moving yet)
    hold = drop_pos(RELEASE_T)
    off = lerp(drift - hold, _v(2.2, 1.7, 11.0), sc(RELEASE_T + 0.3, 8.6, t))
    w = max(t - 8.6, 0.0)
    drift_on = 1.5 * (w * w / 1.2 if w < 0.6 else w - 0.3)  # eased into a slow drift
    pos = lerp(drift, d + off, f) + _v(0.0, 0.0, -drift_on)
    # the gaze turns down to the drop (an even turn), keeping it low in the picture, below the title (nothing
    # crosses the title while it stands whole)
    a, b = _unit(look0 - pos), _unit(_aim(pos, d, 0.5, 0.70, 52.0) - pos)
    om = float(np.arccos(np.clip(a @ b, -1.0, 1.0)))
    u = sc(RELEASE_T + 0.2, 6.7, t)
    g = a if om < 1e-6 else (np.sin((1.0 - u) * om) * a + np.sin(u * om) * b) / np.sin(om)
    look = pos + 12.0 * g
    look = lerp(look, D0 + _v(-2.7, 0.6 + 3.2 * sc(7.9, 8.9, t), 0.0), sc(7.7, 8.8, t))   # up with the burst,
    # the landing a little right of the middle: its light and reflection stay clear of the signature's corner
    return pos, look


F1 = 46.0


def _cam_keys_s1():
    pair = P1 + _v(0.0, 1.25, 0.0)
    her = P1b + _v(0.0, 1.2, 0.0)
    c1, c2 = P1 + _v(-0.75, 1.7, 4.6), P1 + _v(-0.75, 1.68, 4.1)
    c3, c4, c5 = P1b + _v(-1.0, 1.5, 4.6), P1b + _v(-0.9, 1.48, 4.1), P1b + _v(-0.87, 1.47, 3.9)
    cw = D0 + _v(-3.4, 1.72, 2.4)                    # wide of the landing's light
    return [(8.84, D0 + _v(2.0, 1.7, 9.6), D0 + _v(-1.0, 0.8, -4.0)),
            (9.6, cw, _aim(cw, pair, 0.66, 0.70, F1)),
            (10.4, c1, _aim(c1, pair, 0.70, 0.70, F1)),                 # the two men, below the words, right
            (11.5, c2, _aim(c2, pair, 0.705, 0.70, F1)),
            (13.3, c3, _aim(c3, her, 0.74, 0.69, F1)),                 # she stands right, her words on the left
            (15.3, c4, _aim(c4, her, 0.74, 0.69, F1)),
            (15.8, c5, _aim(c5, her, 0.74, 0.69, F1))]                 # drifting on as the carry begins


F2 = 44.0


def _cam_keys_s2():
    kneel = P2 + _v(0.0, 0.8, 0.0)
    hold = P2 + _v(0.0, 1.25, 0.0)
    c0, c1, c2 = P2 + _v(-1.45, 1.62, 5.8), P2 + _v(-1.3, 1.6, 5.3), P2 + _v(-1.2, 1.55, 4.9)
    c3, c4, c5, c6 = (P2 + _v(-1.6, 1.55, 4.1), P2 + _v(-2.0, 1.52, 3.2), P2 + _v(-1.9, 1.5, 2.85),
                      P2 + _v(-1.85, 1.49, 2.7))
    return [(15.3, c0, _aim(c0, kneel, 0.745, 0.72, F2)),               # the carry arrives, drifting in
            (16.6, c1, _aim(c1, kneel, 0.745, 0.72, F2)),               # the two kneeling in the rain of light
            (18.3, c2, _aim(c2, kneel, 0.76, 0.72, F2)),
            (19.6, c3, _aim(c3, hold, 0.72, 0.70, F2)),                # with them as they rise
            (20.6, c4, _aim(c4, hold, 0.70, 0.70, F2)),                # the embrace, her face over her shoulder
            (21.85, c5, _aim(c5, hold, 0.70, 0.70, F2)),
            (22.4, c6, _aim(c6, hold, 0.70, 0.70, F2))]


RIVER_CALM = 25.4                     # the river calms behind Respect
RIVER = [P2 + _v(0.0, 0.0, -1.0), P2 + _v(1.2, 0.0, -7.0), P3 + _v(-0.5, 0.0, 7.0),
         P3 + _v(0.0, 0.0, 3.0), P3 + _v(0.0, 0.0, -4.0), P3b + _v(-0.5, 0.0, 1.5), P3b + _v(-3.0, 0.0, -10.0),
         P3b + _v(4.0, 0.0, -40.0), P3b + _v(-6.0, 0.0, -90.0), P3b + _v(10.0, 0.0, -180.0),
         P3b + _v(-10.0, 0.0, -420.0), P3b + _v(30.0, 0.0, -900.0)]
F3 = 46.0


def _cam_keys_s3():
    door = P3 + _v(0.0, 1.25, 0.0)
    two = P3b + _v(0.0, 0.75, 0.0)
    c1 = P2 + _v(-3.2, 2.3, -1.6)                 # past the embrace, on the left, up the river to the door
    c2, c3, c4 = P3 + _v(-1.7, 1.5, 9.0), P3 + _v(-1.5, 1.42, 7.6), P3 + _v(-1.4, 1.4, 6.8)
    c6, c7, c8 = P3b + _v(-0.5, 1.25, 4.0), P3b + _v(-0.46, 1.22, 3.65), P3b + _v(-0.45, 1.21, 3.55)
    return [(21.85, c1, _aim(c1, door, 0.70, 0.62, F3)),                # gliding on up the river of light
            (23.0, c2, _aim(c2, door, 0.76, 0.67, F3)),
            (23.6, c3, _aim(c3, door, 0.76, 0.67, F3)),
            (25.3, c4, _aim(c4, door, 0.79, 0.67, F3)),
            (26.15, P3 + _v(-0.2, 1.5, 0.3), P3 + _v(-0.6, 1.25, -8.0)),   # on through the door, unhurried
            (27.1, c6, _aim(c6, two, 0.70, 0.71, F3)),                 # the two seated, both in profile
            (28.79, c7, _aim(c7, two, 0.705, 0.71, F3)),
            (29.3, c8, _aim(c8, two, 0.705, 0.71, F3))]


def _cam_keys_s4():
    two = P4 + _v(0.0, 0.62, 0.0)                  # the two kneeling: their heads at about 0.9 m
    c0, c1 = P4 + _v(-1.2, 1.3, 14.0), P4 + _v(-1.3, 1.0, 8.5)
    c2, c3, c4 = P4 + _v(-0.9, 1.0, 3.9), P4 + _v(-0.85, 0.98, 3.5), P4 + _v(-0.8, 1.05, 3.1)
    return [(28.79, c0, _aim(c0, two, 0.62, 0.73, 58.0)),           # wide: small people under the light
            (30.4, c1, _aim(c1, two, 0.62, 0.72, 52.0)),
            (31.6, c2, _aim(c2, two, 0.67, 0.71, 48.0)),            # closer: the hand on the shoulder
            (33.6, c3, _aim(c3, two, 0.67, 0.71, 48.0)),
            (35.9, c4, _aim(c4, two + _v(0.0, 0.5, 0.0), 0.62, 0.66, 48.0))]   # drifting on as the carry begins


F5 = 48.0


def _cam_keys_s5():
    g = P5 + _v(0.0, 0.85, 0.0)                     # where the two hands meet
    d = P5b + _v(0.0, 1.1, 0.0)

    def side(dist, h, az):            # their hands meet on an axis at about 52 degrees: we look across it
        a = np.radians(az)
        return P5 + _v(np.sin(a) * dist, h, np.cos(a) * dist)

    def orb(az, r=4.3, h=1.5):        # round the dancer, the crowd of light behind her
        a = np.radians(az)
        return P5b + _v(np.sin(a) * r, h, np.cos(a) * r)
    c0, c1, c2, c3 = side(6.4, 1.8, -50.0), side(5.7, 1.6, -42.0), side(5.3, 1.56, -37.0), side(5.25, 1.56, -36.0)
    o1, o2, o3 = orb(-34.0), orb(-14.0), orb(6.0)
    m = P5 + _v(2.8, 2.4, 2.2)                      # the carry arcs up and round them (never through anyone)
    return [(35.36, c0, _aim(c0, g, 0.68, 0.72, F5)),                  # the carry arrives, onto them
            (36.3, c1, _aim(c1, g, 0.68, 0.73, F5)),
            (38.2, c2, _aim(c2, g, 0.685, 0.745, F5)),
            (39.05, m, lerp(g, d, 0.55) + _v(0.0, 0.4, 0.0)),           # a gliding carry to the dancer
            (39.9, o1, _aim(o1, d, 0.68, 0.71, F5)),
            (40.6, o2, _aim(o2, d, 0.71, 0.71, F5)),
            (42.0, o3, _aim(o3, d, 0.72, 0.71, F5))]


CARRY5 = (38.2, 42.0)                            # the carry from the two to the dancer and round her


def _catmull(pts, n=400):
    """A smooth curve through points (centripetal Catmull-Rom), densely sampled."""
    P = [2 * pts[0] - pts[1]] + list(pts) + [2 * pts[-1] - pts[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + float(np.linalg.norm(p1 - p0)) ** 0.5 + 1e-6
        t2 = t1 + float(np.linalg.norm(p2 - p1)) ** 0.5 + 1e-6
        t3 = t2 + float(np.linalg.norm(p3 - p2)) ** 0.5 + 1e-6
        for u in np.linspace(t1, t2, n, endpoint=False):
            a1 = (t1 - u) / (t1 - t0) * p0 + (u - t0) / (t1 - t0) * p1
            a2 = (t2 - u) / (t2 - t1) * p1 + (u - t1) / (t2 - t1) * p2
            a3 = (t3 - u) / (t3 - t2) * p2 + (u - t2) / (t3 - t2) * p3
            b1 = (t2 - u) / (t2 - t0) * a1 + (u - t0) / (t2 - t0) * a2
            b2 = (t3 - u) / (t3 - t1) * a2 + (u - t1) / (t3 - t1) * a3
            out.append((t2 - u) / (t2 - t1) * b1 + (u - t1) / (t2 - t1) * b2)
    out.append(pts[-1])
    return np.array(out)


def _s5_make():
    """Onto the two (keys), then one even carry (eased from rest, a constant glide, eased to rest): up and
    round the two, never through them, and gently on in to the dancer as she turns."""
    keys = _cam_keys_s5()
    head = _pchip(keys[:3])
    c2 = np.asarray(keys[2][1], np.float64)
    orb = [np.asarray(k[1], np.float64) for k in keys[4:]]
    mid = 0.5 * (c2 + orb[0])
    perp = _unit(np.cross(orb[0] - c2, UP))
    if perp @ _v(1.0, 0.0, 1.0) < 0.0:
        perp = -perp
    bulge = mid + 3.0 * perp + _v(0.0, 0.6, 0.0)
    curve = _catmull([c2, bulge, orb[-1]])                 # on in one smooth curve (no corner round her)
    seg = np.linalg.norm(np.diff(curve, axis=0), axis=1)
    arc = np.r_[0.0, np.cumsum(seg)]
    ts = np.linspace(CARRY5[0], CARRY5[1], 1200)
    v = ss(CARRY5[0], CARRY5[0] + 1.0, ts) * (1.0 - ss(CARRY5[1] - 1.4, CARRY5[1], ts))
    prog = np.r_[0.0, np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(ts))]
    prog /= prog[-1]
    g, d = P5 + _v(0.0, 0.85, 0.0), P5b + _v(0.0, 1.1, 0.0)

    def f(t):
        if t <= CARRY5[0]:
            return head(t)
        s_ = float(np.interp(t, ts, prog)) * arc[-1]
        pos = np.array([np.interp(s_, arc, curve[:, j]) for j in range(3)])
        k = ss(38.5, 40.2, t)
        subj = lerp(g, d, k)
        sx = 0.685 + (0.72 - 0.685) * ss(38.5, CARRY5[1], t)
        sy = 0.745 + (0.71 - 0.745) * k
        return pos, _aim(pos, subj, sx, sy, F5)
    return f


_s5 = _s5_make()
_B0, _BQ0 = _s5(42.0)                             # the breath starts just where the dancer's shot ends
_B1 = _B0 + _v(1.2, 0.6, -0.6)                   # a slow drift up and aside (no pull back: no bounce)
_BQ1 = _aim(_B1, PEARL, 0.5, 0.40, F5)


def _s6(t):
    """The breath: nearly still, the camera drifts a little up and aside from the dancer and the gaze lifts over
    the calm sea to where the light gathers beyond her."""
    u = sc(41.6, BREATH_END - 0.1, t)
    d0, d1 = _unit(_BQ0 - _B0), _unit(_BQ1 - _B1)
    om = float(np.arccos(np.clip(d0 @ d1, -1.0, 1.0)))             # an even turn of the gaze
    d = d0 if om < 1e-6 else (np.sin((1.0 - u) * om) * d0 + np.sin(u * om) * d1) / np.sin(om)
    p = lerp(_B0, _B1, u)
    return p, p + d * float(np.linalg.norm(lerp(_BQ0 - _B0, _BQ1 - _B1, u)))


ASC0 = BREATH_END
HEAVEN_T = LEAD + 44.3                           # we break above the clouds into the glory of the sun (06's cadence)
ASC1 = 49.2                                      # out of the glory, up to the world
SUN_AZ = 228.0                                   # the dawn lies ahead and to the left (WORLD sun_az)
HV = _v(np.sin(np.radians(SUN_AZ)), 0.0, np.cos(np.radians(SUN_AZ)))     # level, toward the sun
GLORY_EL = 6.0                                   # the sun stands low over the sea of clouds


_A0 = float(np.degrees(np.arctan2(_B1[0] - A7[0], _B1[2] - A7[2])))      # the ascent starts where the breath is
_R0 = float(np.hypot(_B1[0] - A7[0], _B1[2] - A7[2]))
ASC_R = 20.0                                     # how far from the column we rise
ASC_AZ = 40.0                                    # where we come out: the column between us and the sun (it fades)


GLORY_Y = 22.0                                   # the sea of golden clouds we break through
CLIMB_H = GLORY_Y + 6.0 - float(_B1[1])          # how far we rise to break above it
ASC_DRIFT = 1.0                                  # metres a second we keep rising in the glory


def _asc_tables():
    """The ascent as one even glide: the climb and the turn round the column gather from rest (about a second),
    run at a constant speed, and ease off as we break above the clouds into a slow drift (no rush, no snap).
    Integrated once from the speed profiles."""
    t = np.arange(ASC0 - 1.0, TOTAL + 2.0, 1.0 / 600.0)
    up = ss(ASC0 - 0.5, ASC0 + 1.8, t)
    down = ss(HEAVEN_T - 0.5, HEAVEN_T + 1.0, t)
    shape = up * (1.0 - down)
    dt = t[1] - t[0]
    A = float(np.sum(shape[t < HEAVEN_T]) * dt)
    B = float(np.sum((up * down)[t < HEAVEN_T]) * dt)
    v = shape * (CLIMB_H - ASC_DRIFT * B) / A + ASC_DRIFT * up * down
    y = float(_B1[1]) + np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * dt)])
    tot = ((ASC_AZ - _A0 + 180.0) % 360.0) - 180.0
    turn = ss(ASC0, ASC0 + 1.2, t) * (1.0 - ss(HEAVEN_T - 0.3, HEAVEN_T + 1.4, t))
    a = np.concatenate([[0.0], np.cumsum(0.5 * (turn[1:] + turn[:-1]) * dt)])
    a = _A0 + tot * a / a[-1]
    return t, y, a


_AT, _AY, _AA = _asc_tables()


def _climb(t):
    return float(np.interp(t, _AT, _AY))


def _asc_angle(t):
    return np.radians(float(np.interp(t, _AT, _AA)))


def _asc_radius(t):
    return ASC_R + (_R0 - ASC_R) * (1.0 - sc(ASC0, ASC0 + 2.4, t))


def _asc_pos(t):
    a, r = _asc_angle(t), _asc_radius(t)
    return A7 + _v(np.sin(a) * r, _climb(t), np.cos(a) * r)


def _sun_dir(el=GLORY_EL):
    e = np.radians(el)
    return _v(HV[0] * np.cos(e), np.sin(e), HV[2] * np.cos(e))


def _s7(t):
    """The ascent: a slow corkscrew up round the column of light, looking up along it with the nine colours
    streaming past, then we break above the clouds and the gaze levels to the glory of the sun over a sea of
    golden-rose clouds."""
    p = _asc_pos(t)
    y = _climb(t)
    r = _asc_radius(t)
    up = _unit(A7 + _v(0.0, y + 1.5 + 0.2 * r, 0.0) - p)        # a little up along the column (about 12 degrees)
    d0 = _slerp(_unit(_BQ1 - _B1), up, sc(ASC0 - 0.2, ASC0 + 2.2, t))  # from the breath's gaze, without a jolt
    d = _slerp(d0, _unit(HV + _v(0.0, -0.06, 0.0)), sc(HEAVEN_T - 0.7, HEAVEN_T + 1.2, t))   # level, to the sun
    return p, p + 30.0 * d


def _slerp(d0, d1, u):
    """An even turn from one direction to another (never a swing)."""
    om = float(np.arccos(np.clip(d0 @ d1, -1.0, 1.0)))
    return d0 if om < 1e-6 else (np.sin((1.0 - u) * om) * d0 + np.sin(u * om) * d1) / np.sin(om)


# ---- the finale: BRAND's world of light, the nine symbols swirl round it and burst, it becomes the logo ------
FIN_R = 9.0                                      # the Earth's radius (metres)
FIN_SHRINK = 0.47
FIN_C = A7 + _v(0.0, 140.0, 0.0) + HV * 90.0     # it hangs in the night above the glory
FIN_T = 49.4                                     # it gathers (BR.Finale t_world)
SWIRL = (49.25, LEAD + 50.22)                    # the symbols swirl round it from the lift; they burst on the bar
HEARTS_T0, HEARTS_T1 = 50.5, 52.1
SETTLE = (51.5, 53.0)
LOGO_T = (SWIRL[1], 53.85)                       # world to logo, straight out of the burst
BLOOM_T = LEAD + 51.34                           # the bloom into the pastel day (a hit after a hush)
END_FOV = 50.0
EC_SCALE = 1.0                                   # TITLES end card scale (see TITLES below)
SLOT_Y = (48.0 + 85.0 - 540.0) * EC_SCALE / 1080.0 + 0.5   # the end card logo's middle, from the top
SLOT_H = 170.0 * EC_SCALE / 1080.0
END_T0, END_T = 53.85, 54.4                      # the logo glides into the end card's logo slot
EC_IN, EC_FADE = 54.15, 0.7                      # the end card: whole from 55.0 (new) to the last frame


PUSH = (EC_IN + EC_FADE, TOTAL)                  # the end card's slow push-in (whole card to the last frame)


def _end_fov(t):
    """The end: a slow push-in of about 3 percent, from rest, settling to stillness at the last frame."""
    return END_FOV * (1.0 - 0.03 * sc(PUSH[0], PUSH[1], t))


def _fin_scale(t):
    return 1.0 - (1.0 - FIN_SHRINK) * sc(SETTLE[0] - 0.4, SETTLE[1], t)


def _fin_cam(az, el, d):
    """A place round the world: az degrees round from the side away from the sun, el above, d metres off."""
    a, e = np.radians(az), np.radians(el)
    back = -HV
    side = _unit(np.cross(UP, back))
    return FIN_C + d * (np.cos(e) * (np.cos(a) * back + np.sin(a) * side) + np.sin(e) * UP)


_LOGO_DROP = 0.1624 * FIN_R * FIN_SHRINK / 0.3058     # the logo's middle stands this far below the globe's
FIN_LIFT = 0.17 * FIN_R                                # the world a little high in the picture (the corner)


LIFT_END = 51.0                                  # the glide out to the world has arrived


def _s8(t):
    """Out to the world: up from the glory into the night where the Earth hangs, a slow turn round it while the
    symbols swirl and the hearts light across it, in to frame the logo as the world becomes it, then still
    while the logo glides into the end card's place."""
    p_a = _asc_pos(ASC1)
    q_a = p_a + 100.0 * _unit(HV + _v(0.0, -0.06, 0.0))
    p_b = _fin_cam(-22.0, -6.0, 4.45 * FIN_R)
    p_c = _fin_cam(4.0, -3.0, 4.2 * FIN_R)
    tgt = FIN_C - _v(0.0, FIN_LIFT, 0.0)
    tgt_logo = FIN_C - _v(0.0, _LOGO_DROP + 1.0 * FIN_LIFT, 0.0)
    p_d = _fin_cam(8.0, 1.0, 3.9 * FIN_R) - _v(0.0, _LOGO_DROP, 0.0)
    if t < LIFT_END:
        e = sc(ASC1 - 0.3, LIFT_END, t)                # out to the world: a long, eased glide (about 2 s)
        return lerp(p_a, p_b, e), lerp(q_a, tgt, sc(ASC1 - 0.2, LIFT_END - 0.4, t))
    if t < LOGO_T[0]:
        e = sc(LIFT_END, LOGO_T[0], t)
        return lerp(p_b, p_c, e), tgt
    if t < LOGO_T[1]:
        e = sc(LOGO_T[0], LOGO_T[1], t)
        return lerp(p_c, p_d, e), lerp(tgt, tgt_logo, e)
    e = sc(END_T + 0.2, TOTAL, t)                  # still while the logo glides home, then the gentlest drift
    return p_d + e * _v(0.0, 1.5, 0.0) + e * 2.0 * HV, tgt_logo + e * _v(0.0, 2.5, 0.0)


def _rig(focus):
    """Anthony after v6: no strobing whips. Every change of place is a gliding carry (the stages stand close
    together, so the camera simply travels on to the next, about two seconds, eased at both ends, on the music's
    blends) while each stage's scenery fades out and the next one's fades in; focus moves smoothly."""
    def fo(default):
        return (lambda t: focus(t, default)) if focus is not None else "target"
    return Rig([
        Path(_s0, 0.0, SEC[1], fov=lambda t: 50.0 + 6.0 * sc(6.0, 7.6, t) - 4.0 * sc(7.7, 9.0, t), aperture=0.0,
             focus=fo(lambda t: lerp(drop_pos(t), D0 + _v(0, 1.0, 0), sc(7.9, 8.5, t)))),
        Path(_pchip(_cam_keys_s1()), SEC[1], SEC[2], blend=1.6, fov=F1, aperture=0.012,
             focus=fo(lambda t: lerp(P1 + _v(0, 1.2, 0), P1b + _v(0, 1.3, 0), sc(11.8, 12.9, t)))),
        Path(_pchip(_cam_keys_s2()), SEC[2], SEC[3], blend=2.0, fov=F2, aperture=0.012,
             focus=fo(lambda t: lerp(P2 + _v(0, 0.8, 0), P2 + _v(0, 1.25, 0), sc(18.4, 19.8, t)))),
        Path(_pchip(_cam_keys_s3()), SEC[3], SEC[4], blend=1.8, fov=F3, aperture=0.01,
             focus=fo(lambda t: lerp(P3 + _v(-1.0, 1.3, 2.0), P3b + _v(0, 0.9, 0), sc(25.4, 26.7, t)))),
        Path(_pchip(_cam_keys_s4()), SEC[4], SEC[5], blend=2.4,
             fov=lambda t: 58.0 - 6.0 * sc(28.79, 30.4, t) - 4.0 * sc(30.4, 31.6, t), aperture=0.01,
             focus=fo(P4 + _v(0, 0.7, 0))),
        Path(_s5, SEC[5], 42.0, blend=3.0, fov=F5, aperture=0.01,
             focus=fo(lambda t: lerp(P5 + _v(0, 1.0, 0), P5b + _v(0, 1.1, 0), sc(38.4, 39.6, t)))),
        Path(_s6, 42.0, BREATH_END, blend=1.2, fov=F5, aperture=0.0),
        Path(_s7, BREATH_END, ASC1, blend=0.5, fov=lambda t: F5 + 10.0 * sc(ASC0 - 0.2, ASC0 + 1.8, t), aperture=0.0),
        Path(_s8, ASC1, TOTAL + 1.0, blend=1.0, fov=_end_fov, aperture=0.0),
    ], blend=0.6, fov=48.0, aperture=0.0, handheld=0.12, min_height=0.4)


_LAYOUT = _rig(None)


def place(t, x, y, depth):
    return np.asarray(PW.place(_LAYOUT, t, x, y, depth), np.float64)


# =============================================================================================================
# THE WORDS (all nine, by name; exact wording and colours from words.EXPRESSIONS; never mirrored; one at a time;
# each block centred about a third of the way down the picture, clear sky above it, the people below it)
# =============================================================================================================
def _width(t, depth, frac):
    cam = PW._cam_at(_LAYOUT, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _w(expr, t_in, r0, r1, t_out, x, y, depth, frac, **kw):
    """A word that rides with the camera: it keeps its place in the picture (x, y from the left and the bottom)
    `depth` metres ahead of the lens whatever the camera does, `frac` of the picture's width wide."""
    tm = 0.5 * (r0 + r1)
    d = dict(expr=expr, ride=(x, y, depth), face="screen", width=_width(tm, depth, frac), t_in=t_in, t_read0=r0,
             t_read1=r1, t_out=t_out, leave="fade", pill=True)
    d.update(kw)
    return d


_REVEAL = dict(arrive="reveal", edge="right", soft=0.16, edge_glow=2.2)
_PEN = dict(arrive="pen", nib=False)

_SPECS = [
    _w("Greeting", 8.95, 9.35, 11.95, 12.15, 0.46, 0.625, 7.0, 0.30, **_REVEAL),
    _w("Gratitude", 12.15, 12.52, 15.0, 15.2, 0.36, 0.620, 7.0, 0.52, **_PEN),
    _w("Apology", 15.6, 16.0, 18.4, 18.6, 0.46, 0.620, 7.0, 0.52, **_REVEAL),
    _w("Inclusiveness", 18.6, 19.0, 21.35, 21.55, 0.46, 0.625, 7.0, 0.48, **_PEN),
    _w("Concession", 22.45, 22.85, 25.25, 25.45, 0.46, 0.625, 7.0, 0.40, **_REVEAL),
    _w("Respect", 25.5, 25.95, 28.3, 28.5, 0.46, 0.620, 7.0, 0.45, **_PEN),
    _w("Encouragement", 29.5, 30.0, 33.3, 33.6, 0.46, 0.620, 7.0, 0.51, **_REVEAL),
    _w("Consideration", 35.5, 35.85, 38.75, 38.9, 0.40, 0.620, 7.0, 0.44, **_PEN),
    _w("Compliment", 38.95, 39.2, 42.0, 42.15, 0.45, 0.620, 7.0, 0.41, **_REVEAL),
]


def _clean_leave(t, info):
    """Every word leaves in place and sharp, thinning out evenly: never smeared, drifting or broken letters."""
    if info["state"] == "leave":
        return dict(pos=info["home"], assist=1.0)
    return None


WORDS = PW.Words(_SPECS, camera=_LAYOUT, reflect=False, drive=_clean_leave)


def _focus(t, default, ease=0.6):
    """Keep the subject sharp (the words are sharp whatever the lens does)."""
    return np.asarray(default(t) if callable(default) else default, np.float64)


CAMERA = _rig(_focus)            # on the film's own (old) time: what the scene's pieces look through


class WarpRig(Rig):
    """The camera on the new medley's time: the film's rig asked at W(t)."""

    def __init__(self, inner, warp):
        self.__dict__.update(inner.__dict__)
        self.inner, self.warp = inner, warp

    def state(self, t, aspect=16.0 / 9.0, ref=None):
        return self.inner.state(self.warp(t), aspect, ref=None if ref is None else self.warp(ref))

    def raw(self, t, ref=None, swing=True):
        return self.inner.raw(self.warp(t), ref=None if ref is None else self.warp(ref), swing=swing)

    def cuts(self):
        return [self.warp.R(c) for c in self.inner.cuts()]


class _Warped:
    """A point set of the scene on the new medley's time (it is asked at W(t))."""

    def __init__(self, inner, warp):
        self.inner, self.warp = inner, warp
        self.wants_camera = bool(getattr(inner, "wants_camera", False))
        for k in ("static", "dome", "turns"):
            if hasattr(inner, k):
                setattr(self, k, getattr(inner, k))
        if hasattr(inner, "gain"):
            self.gain = lambda t: inner.gain(warp(t))

    def sample(self, t, cam=None):
        to = self.warp(t)
        return self.inner.sample(to, cam) if self.wants_camera else self.inner.sample(to)


class _WarpScene:
    """Hands the song's setup a scene whose every point set runs on the new medley's time."""

    def __init__(self, scene, warp):
        self.scene, self.warp = scene, warp

    def add(self, name, ps, **kw):
        self.scene.add(name, _Warped(ps, self.warp), **kw)
        return ps

    def __getattr__(self, k):
        return getattr(self.scene, k)


# =============================================================================================================
# THE WORLD: heavenly looks, section by section (never dark, never cold)
# =============================================================================================================
LOOKS = dict(
    # above the sea of clouds at twilight: a deep blue-violet zenith, a band of gold and coral low down
    opening=dict(base="dawn", sky_top="#0d1250", sky_mid="#3a2e86", sky_hor="#e88a6a", sun_color="#ffc88a",
                 sun_int=0.7, sun_el=-1.5, sun_disc=0.0, sun_glow=0.65, stars=0.85, milky=0.4, clouds=0.0,
                 haze=0.65, haze_color="#c87a72", mist=0.35, mist_height=30.0, mist_color="#b0708a", hills=0.0,
                 water="#2a1838", mirror=0.6,
                 ripple=0.2, rays=0.25, dust=0.3, dust_color="#ffe0a8", dust_color2="#ffc0c8", bokeh=0.3,
                 keep_hue=0.8),
    # the sea of light: deep and clear, the warm light of the dawn off to one side
    shore=dict(base="dawn", sky_top="#0b1046", sky_mid="#2a2470", sky_hor="#9a5068", sun_color="#ffc890",
               sun_int=0.7, sun_el=-1.5, sun_disc=0.0, sun_glow=0.6, stars=0.75, milky=0.35, clouds=0.25,
               haze=0.3, haze_color="#7a4a6a", mist=0.12, mist_color="#6a4a7a", hills=0.0, water="#070818",
               mirror=1.0, ripple=0.25, rays=0.3, dust=0.6, dust_color="#ffe0a8", dust_color2="#ffc0c8",
               bokeh=0.6, keep_hue=0.8),
    rain=dict(base="dusk", sky_top="#0a0c3a", sky_mid="#28226a", sky_hor="#84506e", sun_color="#ffb8a0",
              sun_int=0.45, sun_el=-3.5, sun_disc=0.0, sun_glow=0.7, stars=0.6, milky=0.3, clouds=0.35,
              haze=0.3, haze_color="#5a3a6a", mist=0.25, mist_color="#4a3a6a", hills=0.0, water="#060716",
              mirror=1.0, ripple=0.35, rays=0.05, dust=0.4, dust_color="#e8e8ff", dust_color2="#ffd0d8",
              bokeh=0.5, keep_hue=0.8),
    # the embrace: the dawn breaks to the side, a warm amber glow over the sea
    sunrise=dict(base="sunrise", sky_top="#0c1048", sky_mid="#3c2670", sky_hor="#b45a50", sun_color="#ffb860",
                 sun_int=0.38, sun_el=0.5, sun_disc=1.5, sun_glow=0.35, stars=0.4, milky=0.15, clouds=0.3,
                 haze=0.22, haze_color="#8a4a4a", mist=0.12, mist_color="#6a4060", hills=0.0, water="#080716",
                 mirror=1.0, ripple=0.25, rays=0.35, dust=0.6, dust_color="#ffe2a8", dust_color2="#ffcfa8",
                 bokeh=0.6, keep_hue=0.8, exposure=0.9),
    river=dict(base="sunrise", sky_top="#0e1254", sky_mid="#3a2a7c", sky_hor="#9a5268", sun_color="#ffc890",
               sun_int=0.5, sun_el=1.0, sun_disc=1.5, sun_glow=0.45, stars=0.3, milky=0.1, clouds=0.35,
               haze=0.3, haze_color="#9a5a5a", mist=0.1, mist_color="#8a5a6a", hills=0.0, water="#0a0a1c",
               mirror=1.0, ripple=0.3, rays=0.4, dust=0.6, dust_color="#ffe6b0", dust_color2="#ffd0b0",
               bokeh=0.6, keep_hue=0.8, exposure=0.92),
    cathedral=dict(base="dusk", sky_top="#070830", sky_mid="#2a1a66", sky_hor="#7a3a72", sun_color="#ffcf8a",
                   sun_int=0.35, sun_el=-3.0, sun_disc=0.0, sun_glow=0.5, stars=0.95, milky=0.7, clouds=0.1,
                   haze=0.18, haze_color="#4a2a64", mist=0.12, mist_color="#3a2a5a", hills=0.0, water="#060616",
                   mirror=1.0, ripple=0.2, rays=0.15, dust=0.7, dust_color="#ffe2a8", dust_color2="#e0c8ff",
                   bokeh=0.7, keep_hue=0.8),
    rivers=dict(base="predawn", sky_top="#080a3a", sky_mid="#22206a", sky_hor="#7e4a7c", sun_color="#ffc0a0",
                sun_int=0.45, sun_el=-3.0, sun_disc=0.0, sun_glow=0.7, stars=1.0, milky=0.8, clouds=0.12,
                haze=0.3, haze_color="#4a3a72", mist=0.15, mist_color="#4a3a7a", hills=0.0, water="#060618",
                mirror=1.0, ripple=0.2, rays=0.0, dust=0.6, dust_color="#ffe2a8", dust_color2="#c8d0ff",
                bokeh=0.6, keep_hue=0.8),
    breath=dict(base="predawn", sky_top="#070a36", sky_mid="#1e1e62", sky_hor="#8a5a86", sun_color="#ffc0a0",
                sun_int=0.4, sun_el=-3.5, sun_disc=0.0, sun_glow=0.7, stars=1.0, milky=0.9, clouds=0.0,
                haze=0.3, haze_color="#3e3a72", mist=0.12, mist_color="#3e3a7a", hills=0.0, water="#050616",
                mirror=1.0, ripple=0.05, rays=0.0, dust=0.4, dust_color="#ffe2a8", dust_color2="#c8d0ff",
                bokeh=0.4, keep_hue=0.8),
    ascent=dict(base="sunrise", sky_top="#121c66", sky_mid="#4c3a8a", sky_hor="#f0a060", sun_color="#ffd890",
                sun_int=0.8, sun_el=5.0, sun_disc=3.0, sun_glow=0.55, stars=0.2, milky=0.0, clouds=0.25,
                haze=0.3, haze_color="#b07a6a", mist=0.0, hills=0.0, water="#100c24", mirror=0.8,
                rays=0.6, dust=0.5, dust_color="#fff0d0", dust_color2="#ffe0b0", bokeh=0.4, keep_hue=0.8,
                exposure=0.92),
    radiant=dict(base="golden", sky_top="#1e48a8", sky_mid="#5e86d0", sky_hor="#ffcf9a", sun_color="#fff0d0",
                 sun_int=0.75, sun_el=12.0, sun_disc=2.5, sun_glow=0.55, stars=0.0, milky=0.0, clouds=0.2,
                 haze=0.35, haze_color="#e0c0a0", mist=0.0, hills=0.0, water="#1a2448", rays=0.45, dust=0.4,
                 dust_color="#fff4dc", dust_color2="#ffe0b0", bokeh=0.3, keep_hue=0.8, exposure=0.9),
    heaven=dict(base="night", sky_top="#060a30", sky_mid="#121a5a", sky_hor="#3a3486", sun_color="#c8b8ff",
                sun_int=0.0, sun_el=40.0, sun_disc=0.0, stars=1.0, milky=0.9, clouds=0.0, haze=0.2,
                haze_color="#3a3a86", mist=0.0, hills=0.0, water="#060820", mirror=0.4, rays=0.0, dust=0.15,
                bokeh=0.15, keep_hue=0.8),
    # above the clouds: the sun low over a sea of golden-rose cloud, its glory fanning out
    glory=dict(base="golden", sky_top="#16247e", sky_mid="#5a4cae", sky_hor="#f8a878", sun_color="#ffe0a8",
               sun_int=0.75, sun_el=GLORY_EL, sun_size=1.4, sun_disc=2.5, sun_glow=0.6, stars=0.15, milky=0.0,
               clouds=0.0, haze=0.3, haze_color="#e89880", mist=0.0, hills=0.0, water="#2a2050", mirror=0.3,
               rays=0.6, dust=0.3, dust_color="#fff0d0", dust_color2="#ffd0c0", bokeh=0.25, keep_hue=0.85,
               exposure=0.8),
)

# the pastel day under the end card (BRAND's PASTEL, warmer and a little deeper below the horizon: a soft peach
# and cream sea, never near white)
LOOKS["pastel"] = dict(BR.PASTEL, water=show("#f4e2d2") * 0.5, mirror=0.4, mirror_min=0.22,
                       mist_color=show("#ffe8d8") * 0.5, haze_color=show("#ffecdc") * 0.55, mist=0.12, exposure=0.94)

LOOK_KEYS = [(0.0, "opening"), (7.6, "shore", 1.6), (SEC[2], "rain", 1.4), (19.6, "sunrise", 2.2),
             (SEC[3], "river", 1.4), (SEC[4], "cathedral", 1.6), (SEC[5], "rivers", 1.6), (SEC[6], "breath", 1.2),
             (BREATH_END + 1.1, "ascent", 2.4), (HEAVEN_T - 0.5, "glory", 1.0), (ASC1 + 0.4, "heaven", 1.2)]

STAGES = [(8.4, P1), (12.3, P1b), (15.3, P2), (22.3, P3), (25.8, P3b), (28.79, P4), (35.36, P5), (38.9, P5b)]


def _calm(t):
    """A calm disc of clean mirror under the people of the moment (the sparkle carpet stays away from them)."""
    c = STAGES[0][1]
    for t0, p in STAGES:
        if t >= t0 - 0.3:
            c = p
    return [dict(center=(float(c[0]), float(c[2])), radius=6.0, soft=4.0, ripple=0.0, mirror=0.75)]


WORLD = dict(
    looks=LOOKS,
    calm=_calm,
    look=LOOK_KEYS,
    sun_az=228.0,              # the dawn lies ahead and to the left: its glow never stands behind the people
    lanterns=0.0,
    arch=None,
    react=dict(beat=0.3, level=0.2),
)


def _shaft(segs, radius=1.0, color="#ffd89a", top=26.0):
    """One of the world's four shafts of light, moved from place to place over time: segs is a list of
    (place, t0, t1, strength); it fades in and out at each."""
    segs = sorted(segs, key=lambda s: s[1])

    def which(t):
        best = segs[0]
        for sg in segs:
            if t >= sg[1] - 1.0:
                best = sg
        return best

    def base(t):
        p = which(t)[0]
        return (float(p[0]), float(p[2]))

    def strength(t):
        p, t0, t1, k = which(t)
        return k * sc(t0, t0 + 0.8, t) * (1.0 - sc(t1 - 0.5, t1, t))
    return dict(base=base, radius=radius, top=top, spread=-0.4, color=color, strength=strength)


# =============================================================================================================
# THE CAST (built when the scene is set up: the workflow's first job imports this file with numpy only)
# =============================================================================================================
_CAST = {}


def _view(at, cam_pos):
    d = np.asarray(cam_pos, np.float64) - np.asarray(at, np.float64)
    return float(np.degrees(np.arctan2(d[0], d[2])))


def _mother_hands():
    """Heavenly Mother's hands of light (never more of her): held out toward us, cupped together, palms up,
    holding the drop; on the release they part a little and tip forward, and the drop slips away."""
    from p3d.body import Body
    out = []
    for j, side in enumerate(("L", "R")):
        sg = -1.0 if side == "L" else 1.0          # L: the hand on the picture's left (fingers toward us)

        def at(t, sg=sg, j=j):
            o = sc(RELEASE_T - 0.9, RELEASE_T + 0.6, t)         # they begin to open as the music swells in
            return H0 + _v(sg * (0.034 + 0.05 * o) * HAND_S, -0.03 * HAND_S * o, 0.0) + \
                _v(0.0, 0.004 * HAND_S * np.sin(1.1 * t + j), 0.0)
        aim = _unit(_v(sg * 0.18, 0.12, 1.0))       # fingers toward the camera, a little apart
        palm = _unit(_v(-sg * 0.30, 1.0, 0.45))     # palms up, turned a little toward us and toward each other
        out.append(Body("woman", part="arm." + ("R" if side == "L" else "L"), look=dict(name="glitter", seams=0.0),
                        color="#ffc860", color2="#fff0c8", bright=1.5, points=80000, scale=HAND_S,
                        show=(-1.0, 7.6), fade=1.0,
                        seed=3.0 + j,
                        effects=[dict(kind="shed", t=-1.0, n=3000, life=2.0, speed=0.15, rise=0.25, spread=0.05)],
                        hand=dict(side=("R" if side == "L" else "L"), at=at, aim=aim, palm=palm, pose="cup",
                                  anchor="palm")))
    return out


def _embrace_pair(o, t_touch, t_look, t_rise, t_hold, until):
    """APOLOGY then INCLUSIVENESS (two women, UPDATE 15). Anthony after v6: tender and simple. One woman sits
    back on her heels, head bowed, hands in her lap. The other kneels beside her, leans in and gently lays her
    hand on her shoulder, the arm rounded (t_touch). After a beat the seated woman lifts her head toward her
    (t_look). They rise together (t_rise; the comforting hand lets go as they rise), turn to each other with a
    small step, and hold each other (t_hold), cheek past shoulder."""
    from p3d import pairs
    from p3d.body import Body
    refs = {}
    gap, side = 0.24, 0.085
    # kneeling, both seen in profile: b sits back on her heels facing the picture's right, a little toward us;
    # a kneels just behind her (picture left), turned to her, and lays her near hand on b's upper back
    kb_k, fb_k = (o[0] + 0.25, o[2] + 0.02), 58.0
    ka_k, fa_k = (o[0] - 0.30, o[2] - 0.06), 74.0
    # the embrace (pairs.embrace's places: a faces +x, b faces -x, each a little to their own left)
    ka_e = (o[0] - 0.5 * gap, o[2] - side)
    kb_e = (o[0] + 0.5 * gap, o[2] + side)
    up_a, up_b = 1.45, 1.55                      # seconds to rise
    t_ra, t_rb = t_rise, t_rise + 0.2
    s0 = t_hold - 0.9                            # stood up: she turns round to her friend with small steps
    show = (SEC[2] - 0.4, until)

    def on(name, fn, guess):
        return lambda tt: fn(refs[name], tt) if name in refs else np.asarray(guess, np.float64)

    def her_back(B, tt):                # high on her back, by the right shoulder blade: where a hand rests
        bl, n = B.where(tt, "blade.R", normal=True, raw=True)
        sh = B.where(tt, "shoulder.R", raw=True)
        return 0.6 * bl + 0.4 * sh + 0.015 * n
    a = dict(shape="woman", garment="dress", hair="bun",
             at=[(0.0, ka_k), (s0, ka_k), (t_hold + 0.1, ka_e)],
             facing=[(0.0, fa_k), (s0, fa_k), (t_hold + 0.1, 90.0)],
             motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="free")),
                     (t_ra, "rise_up", dict(dur=up_a, sit=0.85, blend=0.15)),
                     (s0, "shuffle", dict(blend=0.45, amount=0.3)), (t_hold + 0.15, "stand", dict(blend=0.6))],
             gesture=[(-1e9, t_ra + 0.3, "lap", dict(ease_out=0.9)),
                      (t_touch, t_ra + 0.35, "comfort",
                       dict(side="R", to=on("b", her_back, o + _v(0.12, 1.0, 0.08)), lean=9.0, bow=8.0,
                            ease_in=1.3, ease_out=0.9))],
             points=75000, show=show, fade=0.6, seed=61.0, wind=(0.2, 0.0, -0.1), **GOLD)
    b = dict(shape="woman", garment="dress", hair="bob",
             at=[(0.0, kb_k), (s0, kb_k), (t_hold + 0.1, kb_e)],
             facing=[(0.0, fb_k), (s0, fb_k), (t_hold + 0.1, -90.0)],
             motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="free")),
                     (t_rb, "rise_up", dict(dur=up_b, sit=0.85, blend=0.15)),
                     (s0, "shuffle", dict(blend=0.45, amount=0.35)), (t_hold + 0.15, "stand", dict(blend=0.6))],
             gesture=[(-1e9, t_rb + 0.35, "lap", dict(ease_out=1.0)),
                      (-1e9, t_look + 0.4, "bow", dict(amount=24.0, ease_out=1.2)),
                      (t_look, t_hold + 0.2, "look_to",
                       dict(to=on("a", lambda A, tt: A.where(tt, "head", raw=True), o + _v(-0.30, 1.0, -0.04)),
                            up=2.0, ease_in=1.4, ease_out=0.8))],
             points=75000, show=show, fade=0.6, seed=62.0, wind=(0.2, 0.0, -0.1), **CRYSTAL)
    # the embrace (as pairs.embrace, closer, the arms rounded): her arms over her friend's shoulders, the
    # other's round her back at the shoulder blades; heads beside each other; they rock gently together
    def back(name, side_, drop):
        def f(X, tt):
            bl, br = X.where(tt, "blade.L", raw=True), X.where(tt, "blade.R", raw=True)
            c = 0.5 * (bl + br)
            u = (bl - br) if side_ == "L" else (br - bl)
            return c + 0.38 * u - _v(0.0, drop, 0.0)
        return on(name, f, o + _v(0.0, 1.1, 0.0))
    end = until + 1.0
    a["gesture"] = a["gesture"] + [
        (t_hold, end, "embrace", dict(to=back("b", "R", 0.0), to2=back("b", "L", 0.0), head="L", ease=1.1)),
        (t_hold + 1.0, end, "sway", dict(period=3.6, amount=1.6, ease_in=1.2))]
    b["gesture"] = b["gesture"] + [
        (t_hold + 0.12, end, "embrace", dict(to=back("a", "R", 0.10), to2=back("a", "L", 0.10), head="L",
                                             ease=1.15)),
        (t_hold + 1.0, end, "sway", dict(period=3.6, amount=1.6, phase=0.5, ease_in=1.2))]
    A = Body(**a)
    refs["a"] = A
    B = Body(**b)
    refs["b"] = B
    pairs._built(A, B)
    return A, B


def _greeting_pair(o, t0, t1):
    """GREETING (two men, UPDATE 15): they face each other and each gives a slight, warm bow, a gentle dip of
    the head and shoulders that comes back up to a small nod; the hands stay relaxed at the sides; no touch."""
    from p3d.body import Body
    a = Body("man", at=(o[0] - 0.55, o[2]), facing=90.0, garment="tunic", points=75000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=21.0,
             gesture=[(t0, t1 + 0.8, "greet_bow", dict(amount=17.0, down=0.95, hold=0.55, up=1.1, ease_in=0.5,
                                                       ease_out=1.0)),
                      (t0 + 2.4, t1 + 0.8, "nod", dict(period=2.6, amount=4.0, ease_in=1.0))],
             sweeps=dict(glow=dict(t=t0 + 0.2, at="heart", speed=2.5, width=0.35, flash=1.6)), **GOLD)
    b = Body("man", at=(o[0] + 0.55, o[2]), facing=270.0, garment="coat", points=75000, show=(t0 - 1.0, t1 + 0.8),
             fade=0.6, seed=22.0,
             gesture=[(t0 + 0.4, t1 + 0.8, "greet_bow", dict(amount=15.0, down=1.0, hold=0.5, up=1.1, ease_in=0.5,
                                                             ease_out=1.0)),
                      (t0 + 2.8, t1 + 0.8, "nod", dict(period=2.9, amount=4.0, ease_in=1.0))],
             sweeps=dict(glow=dict(t=t0 + 0.55, at="heart", speed=2.5, width=0.35, flash=1.6)), **CRYSTAL)
    return [a, b]


def _prayer_pair(o, t0, t1, view):
    """ENCOURAGEMENT (two women): one kneels, sitting back on her heels, hands joined in prayer, head bowed. Her
    friend kneels close behind her shoulder (the mirror of the Apology), lays her near hand gently on her
    shoulder, the arm rounded, her other hand on her own heart, and bows her head with her: she prays for her."""
    from p3d import pairs
    from p3d.body import Body
    refs = {}
    a_ = np.radians(view)
    cam = np.array([np.sin(a_), 0.0, np.cos(a_)])
    right = np.array([np.cos(a_), 0.0, -np.sin(a_)])

    def pl(x, z):
        p = np.array([o[0], 0.0, o[2]]) + right * x + cam * z
        return (float(p[0]), float(p[2]))

    def her_shoulder(B, tt):
        sh = B.where(tt, "shoulder.L", raw=True)
        bl, n = B.where(tt, "blade.L", normal=True, raw=True)
        return 0.62 * sh + 0.38 * bl + 0.015 * n + _v(0.0, 0.01, 0.0)
    show = (t0 - 0.9, t1 + 0.9)
    kb = dict(shape="woman", garment="dress", hair="covered", at=pl(-0.22, 0.02), facing=view - 58.0,
              motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="pray"))],
              gesture=[(t0 - 0.6, t1 + 0.9, "bow", dict(amount=16.0, ease_in=1.4))],
              points=70000, show=show, fade=0.6, seed=71.0, **CRYSTAL)
    ka = dict(shape="woman", garment="dress", hair="bun", at=pl(0.33, -0.06), facing=view - 74.0,
              motion=[(-1e9, "kneel", dict(dur=0.01, sit=0.85, hands="free"))],
              gesture=[(-1e9, t0 + 0.6, "lap", dict(ease_out=1.0)),
                       (t0, t1 + 0.9, "comfort",
                        dict(side="L", to=lambda tt: her_shoulder(refs["b"], tt) if "b" in refs else
                             np.array([o[0], 0.75, o[2]]), lean=9.0, bow=12.0, ease_in=1.4, ease_out=1.0)),
                       (t0 + 0.5, t1 + 0.9, "hand_on_heart", dict(side="R", bow=6.0, ease_in=1.2)),
                       (t0 + 1.2, t1 + 0.9, "sway", dict(period=4.4, amount=1.0, ease_in=1.2))],
              points=70000, show=show, fade=0.6, seed=72.0, **GOLD)
    B = Body(**kb)
    refs["b"] = B
    A = Body(**ka)
    pairs._built(A, B)
    return [A, B]


def _concession_man(o, t0, t1, view):
    """CONCESSION: a man takes a small step aside from the doorway of light, turns a little toward the way through
    it and offers it with an open palm low and to the side, the elbow soft (never a straight arm), his other hand
    on his heart, a small bow: "Please, after you." """
    from p3d.body import Body
    a_ = np.radians(view)
    cam = np.array([np.sin(a_), 0.0, np.cos(a_)])
    right = np.array([np.cos(a_), 0.0, -np.sin(a_)])

    def pl(x, z):
        p = np.array([o[0], 0.0, o[2]]) + right * x + cam * z
        return (float(p[0]), float(p[2]))
    ref = {}

    def way(tt):                    # his open palm: low and out to his left, a comfortable reach
        if "m" not in ref:
            return np.array([o[0], 1.0, o[2]])
        M = ref["m"]
        sh = M.where(tt, "shoulder.L", raw=True)
        h = np.radians(M.actor.heading(tt))
        fwd = np.array([np.sin(h), 0.0, np.cos(h)])
        left = np.array([np.cos(h), 0.0, -np.sin(h)])
        return sh + left * 0.26 * M.k + fwd * 0.24 * M.k + np.array([0.0, -0.28, 0.0]) * M.k
    m = Body("man", garment="coat", hair="short", height=1.74,
             at=[(t0 - 0.1, pl(0.0, 0.0)), (t0 + 0.8, pl(-0.40, -0.08))],
             facing=[(t0 - 0.1, view + 4.0), (t0 + 0.8, view + 22.0)],
             motion=[(-1e9, "stand"), (t0 - 0.15, "shuffle", dict(blend=0.3, amount=0.35)),
                     (t0 + 0.85, "stand", dict(blend=0.5))],
             gesture=[(t0 + 0.25, t1 + 0.9, "after_you", dict(side="L", to=way, bow=12.0, ease_in=1.0)),
                      (t0 + 0.45, t1 + 0.9, "hand_on_heart", dict(side="R", bow=4.0, ease_in=1.1))],
             points=95000, show=(t0 - 1.4, t1), fade=0.5, seed=5.0, **dict(GOLD, bright=1.75))
    ref["m"] = m
    from p3d import pairs
    pairs._built(m)
    return [m]


def _help_up(o, t0, t1, view):
    """CONSIDERATION (two men): one kneels on one knee; the other steps close, bends a little and reaches down a
    hand, the elbow soft; they clasp hands and he is lifted gently to his feet, then lays his free hand on his
    helper's shoulder in thanks (pairs.helped_up, closer than the library's default so no arm locks straight)."""
    from p3d import pairs
    st_face = view + 90.0 - 15.0                                   # facing the picture's right, opened to us
    a = dict(shape="man", garment="coat", hair="short", height=1.76, build=1.06, points=70000,
             show=(t0 - 1.4, t1 + 0.5), fade=0.5, seed=8.0,
             gesture=[(t0 - 0.2, t0 + 1.6, "bow", dict(amount=14.0, ease_in=0.9, ease_out=1.0))], **GOLD)
    b = dict(shape="man", garment="tunic", hair="cap", height=1.72, build=0.92, points=70000,
             show=(t0 - 1.4, t1 + 0.5), fade=0.5, seed=9.37, **CRYSTAL)
    A, B = pairs.helped_up(t0 + 0.5, at=(o[0], o[2]), facing=st_face, a=a, b=b, rise=1.7, reach=1.0, apart=0.68)
    return [A, B]


def _dancer(o, t0, t1, view):
    """COMPLIMENT: a joyful, graceful moment. She gathers her arms low and round, turns once as they open in a soft
    rounded arc, the way a dancer moves, and lifts them into a high, open V, her face rising; then she sways,
    alive, as the crowd round her claps and raises its hands."""
    from p3d.body import Body
    f0 = view - 25.0
    sp0, sp1 = t0 + 0.9, t0 + 2.5
    return [Body("woman", at=(o[0], o[2]), garment="dress", hair="bun",
                 facing=[(0.0, f0), (sp0, f0), (sp1, f0 + 360.0)],
                 motion=[(-1e9, "stand")],
                 gesture=[(t0, t1 + 1.0, "dance", dict(ease_in=0.3, ease_out=1.3)),
                          (t0 + 2.8, t1 + 1.0, "sway", dict(period=3.2, amount=2.0, ease_in=1.0))],
                 points=95000, show=(t0 - 0.15, t1 + 1.1), fade=0.5, seed=9.0, **dict(CRYSTAL, bright=1.8))]


def _cam_at_key(keys, t):
    """The camera's place at a key time (for turning a performance toward where we watch it from)."""
    for k in keys:
        if abs(k[0] - t) < 1e-6:
            return k[1]
    return keys[-1][1]


def _cast():
    if _CAST:
        return _CAST
    from p3d import acting
    from p3d import master_acting  # noqa: F401  (registers the film's own gestures and crowd kinds)
    C = _CAST
    C["hands0"] = _mother_hands()
    C["greeting"] = _greeting_pair(P1, 9.25, 12.1)
    cam1b = _cam_at_key(_cam_keys_s1(), 12.75)
    C["gratitude"] = acting.perform("Gratitude", 12.6, 15.4, at=(P1b[0], P1b[2]), view=_view(P1b, cam1b),
                                    variant="heart", style=dict(points=80000, **GOLD), pre=1.2, post=0.6, seed=3.0)
    C["embrace"] = list(_embrace_pair(P2, 15.4, 16.8, 18.0, 20.4, 22.15))
    cam3 = _pchip(_cam_keys_s3())(23.4)[0]        # where we watch him from as he steps aside
    C["concession"] = _concession_man(P3 + _v(-1.0, 0.0, 2.0), 23.0, 25.6, _view(P3, cam3))
    cam3b = _cam_at_key(_cam_keys_s3(), 26.5)
    C["respect"] = acting.perform("Respect", 26.2, 28.8, at=(P3b[0], P3b[2]), view=_view(P3b, cam3b),
                                  variant="listen", style=dict(points=65000), style_a=dict(CRYSTAL),
                                  style_b=dict(GOLD), pre=0.9, post=0.3, seed=6.0)
    cam4 = _cam_at_key(_cam_keys_s4(), 31.6)
    C["encouragement"] = _prayer_pair(P4, 29.6, 33.6, _view(P4, cam4))
    cam5 = P5 + _v(-0.8, 1.3, 6.0)
    C["consideration"] = _help_up(P5, 35.9, 38.9, _view(P5, cam5))
    cam5b = P5b + _v(-2.0, 1.55, 6.4)
    C["compliment"] = _dancer(P5b, 39.0, 42.0, _view(P5b, cam5b))
    return C


# =============================================================================================================
# THE SCENE
# =============================================================================================================
def _cloud_sea(rng, center, r0, r1, n, y, wmin, wmax, bright=1.0, hk=(0.35, 0.6)):
    out = []
    for _ in range(n):
        a = rng.uniform(0.0, 2.0 * np.pi)
        r = np.sqrt(rng.uniform(r0 * r0, r1 * r1))
        w = rng.uniform(wmin, wmax) * (0.7 + 0.6 * r / r1)
        out.append(dict(center=(center[0] + np.sin(a) * r, y + rng.uniform(-3.0, 5.0), center[2] + np.cos(a) * r),
                        width=w, height=w * rng.uniform(*hk), n=int(140 + 110 * w / 100.0),
                        towers=int(rng.integers(3, 7)), bright=bright))
    return out


OPENING_BOX = (0.15, 0.85, 0.40, 0.97)       # the opening lockup (TITLES opening at y 0.30), screen 0..1, y up


SIG_CLEAR = (-0.2, 0.56, -0.2, 0.235)         # the signature's corner (y up): the effects ease away from it


def _sig_on(t):
    a = SIG_PALETTES[0][0]
    return float(ss(a, a + SIG_FADE, t) * (1.0 - ss(SIG_END - SIG_FADE, SIG_END, t)))


def _boxes(t, cam):
    """Screen boxes (x0, x1, y0, y1, strength, feather; y up) of every word on screen now, padded, of the
    opening title while it stands whole (the clearing eases off as it crumbles, so the landing shows), and of the
    signature's corner while it is on (a wide feather: the effects fade softly as they come near it)."""
    out = []
    for w in WORDS:
        if w.t_in - 0.5 < t < w.t_out + 0.4:       # eased in before the word arrives and out after it goes
            k = sc(w.t_in - 0.5, w.t_in + 0.02, t) * (1.0 - sc(w.t_out, w.t_out + 0.4, t))
            b = PW.screen_box(w, cam, t)
            if b[4] and k > 0.0:
                out.append((b[0] - 0.035, b[1] + 0.035, b[2] - 0.04, b[3] + 0.04, k, 0.025))
    k = 1.0 - sc(OPEN_FULL, OPEN_FULL + 0.8, t)
    if k > 0.0:
        out.append(OPENING_BOX + (k, 0.025))
    k = _sig_on(t)
    if k > 0.0:
        out.append(SIG_CLEAR + (k, 0.07))
    return out


class Clear:
    """Wraps a point set: its light goes out inside the screen box of every word on screen and of the opening
    title, so nothing crosses a word while it is read (lines and ribbons at both ends)."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        if hasattr(inner, "gain"):
            self.gain = inner.gain

    @staticmethod
    def _dim(pts, cam, boxes):
        xy, z = cam.project(np.asarray(pts, np.float64).reshape(-1, 3))
        f = np.ones(len(xy))
        for x0, x1, y0, y1, k, e in boxes:
            inside = (ss(x0 - e, x0, xy[:, 0]) * (1.0 - ss(x1, x1 + e, xy[:, 0]))
                      * ss(y0 - e, y0, xy[:, 1]) * (1.0 - ss(y1, y1 + e, xy[:, 1])))
            f = np.minimum(f, 1.0 - k * inside * (z > 0))
        return f

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None or cam is None:
            return res
        boxes = _boxes(t, cam)
        if not boxes:
            return res
        out = []
        for b in (res if isinstance(res, (list, tuple)) else [res]):
            if b is None:
                continue
            b = dict(b)
            P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            f = self._dim(P, cam, boxes)
            if b.get("pos2") is not None:
                f2 = self._dim(np.asarray(b["pos2"], np.float64).reshape(-1, 3), cam, boxes)
                f = np.minimum(f, f2)
                b["alpha2"] = np.asarray(b.get("alpha2", b.get("alpha", 1.0)), np.float64) * f
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
            out.append(b)
        return out


class ColumnClear:
    """Wraps columns of falling light: while a word is on screen, the part of a column that would stand behind
    the words (and above them) goes out softly, so the light seems to pour down from under the words onto the
    people below, and no column is ever seen across a word or cut into pieces round it."""
    wants_camera = True

    def __init__(self, inner):
        self.inner = inner
        if hasattr(inner, "gain"):
            self.gain = inner.gain

    def _boxes(self, t, cam):
        out = []
        for w in WORDS:
            k = float(ss(w.t_in - 0.5, w.t_in, t) * (1.0 - ss(w.t_out, w.t_out + 0.4, t)))
            if k <= 0.0:
                continue
            b = PW.screen_box(w, cam, t)
            if b[4]:
                out.append((b[0] - 0.04, b[1] + 0.04, b[2] - 0.05, k))
        return out

    @staticmethod
    def _f(P, cam, boxes):
        xy, z = cam.project(np.asarray(P, np.float64).reshape(-1, 3))
        f = np.ones(len(xy))
        e = 0.035
        for x0, x1, y0, k in boxes:
            inx = ss(x0 - e, x0, xy[:, 0]) * (1.0 - ss(x1, x1 + e, xy[:, 0]))
            f = np.minimum(f, 1.0 - k * inx * ss(y0 - e, y0, xy[:, 1]) * (z > 0))
        return f

    def sample(self, t, cam=None):
        res = self.inner.sample(t)
        if res is None or cam is None:
            return res
        boxes = self._boxes(t, cam)
        if not boxes:
            return res
        out = []
        for bb in (res if isinstance(res, (list, tuple)) else [res]):
            if bb is None:
                continue
            bb = dict(bb)
            f = self._f(bb["pos"], cam, boxes)
            if bb.get("pos2") is not None:
                f2 = self._f(bb["pos2"], cam, boxes)
                bb["alpha2"] = np.asarray(bb.get("alpha2", bb.get("alpha", 1.0)), np.float64) * f2
            bb["alpha"] = np.asarray(bb.get("alpha", 1.0), np.float64) * f
            out.append(bb)
        return out or None


class NearFade:
    """Wraps a point set: its light fades out within `d` metres of the lens (no streak of rain across the
    picture from a drop beside the camera)."""
    wants_camera = True

    def __init__(self, inner, d=2.0):
        self.inner, self.d = inner, float(d)
        if hasattr(inner, "gain"):
            self.gain = inner.gain

    def sample(self, t, cam=None):
        ps = self.inner
        res = ps.sample(t, cam) if getattr(ps, "wants_camera", False) else ps.sample(t)
        if res is None or cam is None:
            return res
        e = np.asarray(cam.pos, np.float64)
        out = []
        for b in (res if isinstance(res, (list, tuple)) else [res]):
            if b is None:
                continue
            b = dict(b)
            P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            f = ss(0.4 * self.d, self.d, np.linalg.norm(P - e, axis=1))
            if b.get("pos2") is not None:
                P2 = np.asarray(b["pos2"], np.float64).reshape(-1, 3)
                f = np.minimum(f, ss(0.4 * self.d, self.d, np.linalg.norm(P2 - e, axis=1)))
                b["alpha2"] = np.asarray(b.get("alpha2", b.get("alpha", 1.0)), np.float64) * f
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * f
            out.append(b)
        return out


def _gain(*keys):
    tr = Track(list(keys))
    return lambda t: float(tr(t))


def _joy_crowd(places):
    """The crowd of light round the dancer: they appear one by one, then each in their own time claps, raises a
    hand, lifts both arms or lays a hand on the heart, swaying with the music (master_acting's crowd kinds)."""
    from p3d import master_acting  # noqa: F401
    from p3d.crowd import Crowd
    places = np.asarray(places, np.float64)
    toward = np.degrees(np.arctan2(P5b[0] - places[:, 0], P5b[2] - places[:, 1]))      # each faces the dancer
    return Crowd(n=len(places), places=places, facing=toward,
                 kinds=(("joy_clap", 1.5), ("joy_raise", 1.4), ("joy_up", 1.0)),
                 people=dict(woman=1.0, man=1.0),                      # six prototypes: a quick bake
                 start=dict(t=38.6, dur=0.8), act=dict(t=39.3, dur=1.4), until=42.3, fade=0.6, points=4600,
                 color="#ffcf7a", color2="#fff1d6", bright=1.3)


def _crowd_for_preview():
    return _joy_crowd(_crowd_places(np.random.default_rng(55)))


def _crowd_places(rr):
    """The crowd of light round the dancer, in depth (near, middle and far, never in a row), keeping out of the
    words and the signature's corner while she twirls (checked from the camera)."""
    ring = [(9, 2.7, 3.6), (12, 4.6, 6.4), (11, 7.4, 10.5)]
    ang, rad = [], []
    for m_, r0_, r1_ in ring:
        a_ = np.radians(np.linspace(100.0, 260.0, m_)) + rr.normal(0.0, 0.07, m_)
        ang.append(a_)
        rad.append(r0_ + (r1_ - r0_) * rr.random(m_))
    ang, rad = np.concatenate(ang), np.concatenate(rad)
    places = np.stack([P5b[0] + np.sin(ang) * rad, P5b[2] + np.cos(ang) * rad], 1)
    keep = np.ones(len(places), bool)
    for t in np.arange(38.9, 42.3, 0.25):
        cam = PW._cam_at(_LAYOUT, float(t))
        for i, (x, z) in enumerate(places):
            pts = np.array([[x, 0.0, z], [x, 1.9, z], [x + 0.3, 1.0, z], [x - 0.3, 1.0, z]])
            xy, zz = cam.project(pts)
            if (zz <= 0).any():
                continue
            x0, x1 = xy[:, 0].min() - 0.02, xy[:, 0].max() + 0.02
            y0, y1 = 1.0 - xy[:, 1].max() - 0.02, 1.0 - xy[:, 1].min() + 0.02
            if not (x1 < SIG_KEEP[0] or x0 > SIG_KEEP[1] or y1 < SIG_KEEP[2] or y0 > SIG_KEEP[3]):
                keep[i] = False
    return places[keep]


def _setup(scene):
    scene = _WarpScene(scene, TW)
    from p3d import master_fx as FX
    from p3d import master_brand as MB
    rng = np.random.default_rng(2026)

    # ---- the sky's clouds: the sea of clouds at the start (we fall through it), far banks round the
    # horizon all the way, and the high golden layer we rise through
    near = _cloud_sea(rng, D0, 24.0, 300.0, 70, 22.0, 26.0, 60.0, 1.0)
    far = _cloud_sea(rng, _v(0.0, 0.0, -120.0), 650.0, 1600.0, 230, 14.0, 70.0, 140.0, 0.9, hk=(0.28, 0.45))
    high = _cloud_sea(rng, A7, 30.0, 900.0, 160, 118.0, 40.0, 110.0, 1.0)
    scene.add("clouds_near", MS.Billows(near, gain=_gain((0.0, 1.0), (7.7, 1.0), (9.4, 0.0), (TOTAL, 0.0)),
                                        seed=12, alpha=0.085), depth_of_field=False)
    scene.add("clouds_far", MS.Billows(far, gain=_gain((0.0, 1.0), (8.6, 1.0), (9.6, 0.0), (42.0, 0.0), (42.6, 0.45),
                                                       (43.95, 0.45), (44.75, 0.0), (TOTAL, 0.0)), seed=13,
                                       alpha=0.055, body=0.2, sun_az=WORLD["sun_az"]), depth_of_field=False)
    del high                                  # (drawn for the order of the random numbers; the glory replaces it)
    r2 = np.random.default_rng(77)
    # S1: towering golden clouds of the dawn, near and far, with open sky between them (never a flat band)
    dawn = []
    for (az, dist, w, h, y0) in ((-58.0, 210.0, 70.0, 120.0, 4.0), (-34.0, 380.0, 110.0, 190.0, 0.0),
                                 (-12.0, 160.0, 46.0, 84.0, 6.0), (14.0, 300.0, 90.0, 150.0, 0.0),
                                 (38.0, 190.0, 60.0, 105.0, 3.0), (62.0, 420.0, 120.0, 170.0, 0.0),
                                 (-80.0, 330.0, 90.0, 140.0, 0.0), (84.0, 250.0, 70.0, 110.0, 2.0)):
        a = np.radians(180.0 + az)
        dawn += MS.tower(r2, P1 + _v(np.sin(a) * dist, y0, np.cos(a) * dist), w, h, n_layer=4, per=240)
    scene.add("clouds_dawn", MS.Billows(dawn, gain=_gain((0.0, 0.0), (8.3, 0.0), (9.3, 1.0), (15.2, 1.0), (15.9, 0.0),
                                                         (TOTAL, 0.0)), seed=21, alpha=0.07, body=0.35,
                                        sun_az=SUN_AZ), depth_of_field=False)
    # the fall: layers of cloud round the drop's path that the camera dives through with it
    dive = (_cloud_sea(r2, D0, 7.0, 70.0, 16, 32.0, 12.0, 24.0, 1.0)
            + _cloud_sea(r2, D0, 7.0, 90.0, 20, 19.0, 14.0, 28.0, 1.0))
    scene.add("clouds_dive", MS.Billows(dive, gain=_gain((0.0, 0.0), (6.9, 0.0), (7.25, 1.0), (7.8, 1.0), (8.3, 0.0),
                                                         (TOTAL, 0.0)), seed=19, alpha=0.08, body=0.3,
                                        sun_az=WORLD["sun_az"]), depth_of_field=False)
    # the glory: a vast sea of golden-rose clouds that we rise through and then see from above, to the horizon
    glory = _cloud_sea(r2, A7, 10.0, 1500.0, 280, GLORY_Y, 46.0, 150.0, 1.0, hk=(0.26, 0.46))
    # (we rise through it: the puffs near the lens thin away, so it never whites out the picture or the corner)
    glory_b = MS.Billows(glory, gain=_gain((0.0, 0.0), (43.6, 0.0), (44.9, 1.0), (ASC1 + 0.4, 1.0), (ASC1 + 1.2, 0.0),
                                           (TOTAL, 0.0)), seed=14, alpha=0.07, top="#ffd49a", warm="#ffa46c",
                         rose="#e8789c", lilac="#7a68c0", core="#ffe0b8", body=0.25, shade=0.55, sun_az=SUN_AZ)
    scene.add("clouds_glory", NearFade(glory_b, 28.0), depth_of_field=False)
    # S2: towering clouds of rose light over the rain
    storm = []
    for (x, z, w, h) in ((-70, -110, 80, 120), (-20, -160, 95, 150), (45, -125, 75, 110), (100, -170, 90, 140),
                         (-125, -70, 70, 100), (140, -90, 70, 95)):
        storm += MS.tower(rng, P2 + _v(x, 20.0, z), w, h, n_layer=4, per=260)
    scene.add("clouds_storm", MS.Billows(storm, gain=_gain((0.0, 0.0), (14.9, 0.0), (15.8, 1.0), (21.9, 1.0),
                                                           (22.4, 0.0), (TOTAL, 0.0)), seed=16, alpha=0.07,
                                         top="#ffc8dc", warm="#f090b0", rose="#c86aa0", lilac="#6a5ad0",
                                         core="#ffe0ec", sun_az=WORLD["sun_az"]), depth_of_field=False)
    # S3: a canyon of golden clouds along the river of light
    canyon = []
    for i, z in enumerate(np.arange(-60.0, -620.0, -48.0)):
        for side in (-1.0, 1.0):
            off = side * rng.uniform(48.0, 70.0) + side * 0.06 * abs(z)
            w = rng.uniform(42.0, 66.0) * (1.0 + 0.6 * abs(z) / 600.0)
            h = rng.uniform(60.0, 110.0) * (1.0 + 0.8 * abs(z) / 600.0)
            canyon += MS.tower(rng, _v(P3[0] + off, 2.0, P3[2] + 40.0 + z), w, h, n_layer=4, per=200)
    scene.add("clouds_canyon", MS.Billows(canyon, gain=_gain((0.0, 0.0), (21.3, 0.0), (21.85, 1.0), (28.2, 1.0),
                                                             (29.3, 0.0), (TOTAL, 0.0)), seed=17, alpha=0.048,
                                          sun_az=WORLD["sun_az"]), depth_of_field=False)
    # the ascent: columns of golden cloud standing round the column of light
    rise = []
    for i in range(10):
        a = 2.0 * np.pi * i / 10.0 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(34.0, 60.0)
        rise += MS.tower(rng, A7 + _v(np.sin(a) * r, 6.0 + rng.uniform(0, 14), np.cos(a) * r), rng.uniform(26, 40),
                         0.36 * rng.uniform(120, 170), n_layer=5, per=200)
    rise_b = MS.Billows(rise, gain=_gain((0.0, 0.0), (43.75, 0.0), (44.25, 1.0), (HEAVEN_T - 0.3, 1.0),
                                         (HEAVEN_T + 0.6, 0.0), (TOTAL, 0.0)), seed=18, alpha=0.075,
                        sun_az=WORLD["sun_az"])
    scene.add("clouds_rise", NearFade(rise_b, 20.0), depth_of_field=False)

    C = _cast()

    def addp(name, sets):
        for i, ps in enumerate(sets if isinstance(sets, (list, tuple)) else [sets]):
            if hasattr(ps, "add") and hasattr(ps, "mask"):
                ps.add(scene, "%s_%d" % (name, i), mask=False)
            else:
                scene.add("%s_%d" % (name, i), PW.KeepClear(ps, WORDS))

    # ---- S0: Mother's hands, the drop, the landing, the ring of gold. The lead-in (0 to 2.0) is quiet: the
    # hands hold the drop and breathe, light wells softly from the palms; it grows as the music swells in.
    for i, h in enumerate(C["hands0"]):           # warm, soft hands of light (never a net of grains)
        scene.add("hands0_%d" % i, Clear(FX.SoftLight(h, every=40, fill=0.014 * HAND_S, fill_alpha=0.02, a_ref=0.63,
                                                      grain=0.8)))
    palms = H0 + _v(0.0, 0.07 * HAND_S, 0.0)
    scene.add("palm_light0", Clear(FX.Upwell(palms, -1.0, 6.8, n=1400, radius=0.13 * HAND_S, speed=0.3, life=2.6,
                                             size=0.012, gain=_gain((0.0, 0.6), (2.0, 0.65), (3.5, 1.0), (5.8, 1.0),
                                                                    (7.2, 0.0), (TOTAL, 0.0)))),
              reflect=False)
    # on the release light pours from her hands after the drop, which falls with a luminous trail
    pour = FX.Pour(lambda t: H0 + _v(0.0, 0.03 * HAND_S, 0.0), RELEASE_T - 0.05, RELEASE_T + 2.3, n=4200, g=7.8,
                   spread=0.10, life=3.8, size=0.022, width=0.04 * HAND_S, until=LAND_T + 1.25, color="#ffc860",
                   color2="#ffe0a0")
    scene.add("pour0", _Dim(Clear(NearFade(pour, 3.5)), lambda t: 1.0 - sc(LAND_T + 0.1, LAND_T + 0.7, t)),
              reflect=True)                       # gone before the camera glides past the landing place
    scene.add("trail0", Clear(MB.Rivers([(drop_pos, "#ffd27a",
                                    lambda t: sc(RELEASE_T, RELEASE_T + 0.3, t) * (1.0 - sc(LAND_T - 0.05, LAND_T + 0.1, t)),
                                    0.2)], cuts=[RELEASE_T], tail=0.9)), reflect=True)
    scene.add("drop", Clear(FX.Drop(drop_pos, t_show=(-1.0, LAND_T + 0.2), t_land=LAND_T, scale=1.6, t_pulse=3.4)),
              reflect=True)                       # (its glowing tail never across the title)
    # the landing: a towering fountain and a pillar of light, the ring racing out over the sea
    # (the camera then glides past the landing place to the greeting: what is near the lens fades away)
    burst0 = FX.Fountain(D0 + _v(0.0, 0.1, 0.0), LAND_T, n=2600, colors=["#ffd27a", "#ffb84a", "#ffc890", "#ffa8b8",
                                                                     "#ffcf9a"],
                         speed=(4.0, 11.0), spread=0.22, life=1.2, seed=96, fade0=0.25)
    scene.add("burst0", _Dim(NearFade(Clear(burst0), 9.0), lambda t: 1.0 - sc(LAND_T + 0.3, LAND_T + 0.85, t)),
              reflect=True)
    scene.add("pillar0", NearFade(Clear(FX.LightColumns([D0], top=70.0, per=1300, core_w=1.4, fall=-16.0, core_k=0.22,
                                               spark=0.05, seed=72, color="#ffcf80", color2="#ffdca0", segs=40,
                                               gain=_gain((0.0, 0.0), (LAND_T - 0.02, 0.0), (LAND_T + 0.45, 0.6),
                                                          (LAND_T + 0.75, 0.4), (LAND_T + 1.05, 0.0), (TOTAL, 0.0)))),
                                  7.0), reflect=False)
    scene.add("splash", NearFade(Clear(FX.Splash(D0, LAND_T, scale=1.0)), 5.0))
    scene.add("ring", NearFade(Clear(FX.RingWave(D0, LAND_T, speed=24.0, reach=1500.0, until=SEC[3] + 0.5,
                                                 color="#ffb24a", core="#ffd88a")), 9.0))
    scene.add("motes0", FX.Motes(n=900, box=(14.0, 8.0, 14.0), center=None,
                                 gain=_gain((0.0, 0.6), (6.0, 0.6), (7.0, 0.0), (TOTAL, 0.0))), reflect=False)

    # ---- S1: the greeting and the bow of thanks under pouring light
    addp("greeting", C["greeting"])
    addp("gratitude", C["gratitude"])
    scene.add("pour", PW.KeepClear(FX.LightColumns([P1b], top=9.0, per=360, fall=2.2, ring=0.95, core=False,
                                                    spark=0.028, soft=True,
                                                    gain=_gain((0.0, 0.0), (12.3, 0.0), (13.0, 1.0), (15.6, 1.0),
                                                               (16.4, 0.0), (TOTAL, 0.0))), WORDS))
    scene.add("motes1", PW.KeepClear(FX.Motes(n=350, box=(18.0, 6.0, 18.0), center=(P1 + P1b) * 0.5 + _v(0, 3, 0),
                                              gain=_gain((0.0, 0.0), (8.4, 0.0), (9.2, 1.0), (15.6, 1.0),
                                                         (16.6, 0.0), (TOTAL, 0.0))), WORDS), reflect=False)

    # ---- S2: the rain of light, the two kneeling, the embrace, the sunrise
    def rain_tau(t):
        # falls, slows at the embrace, hangs, then runs backward: the drops rise as warm sparks
        if t < 19.3:
            return t
        u = t - 19.3                  # (the turn eased over a second, then an even, gentle rise: never a rush)
        if u < 1.2:
            return 19.3 + 0.9 * u - 0.6 * u * u
        return 19.3 + 0.9 * 1.2 - 0.6 * 1.44 - 0.54 * (u - 1.2)
    scene.add("rain", Clear(NearFade(FX.RainOfLight(P2, radius=11.0, top=15.0, n=6000, speed=4.0, tau=rain_tau,
                                                  warm=lambda t: sc(19.0, 20.5, t),
                                                  gain=_gain((0.0, 0.0), (14.8, 0.0), (15.8, 1.0), (20.8, 1.0),
                                                             (22.0, 0.0), (TOTAL, 0.0))), 4.0)))
    addp("embrace", C["embrace"])

    # ---- S3: the river of light, the doorway, the two seated
    # the river flows fast for the surge, then calms to a slow drift behind the two seated listening (no sparkle
    # flicker: slower, softer twinkle, its points drawn sharp, without the lens's bokeh discs)
    scene.add("river", Clear(FX.LightRiver(RIVER, width=3.2, n=30000, speed=10.0, twinkle=0.25, edge=9.0,
                                           clock=lambda t: MB.still_clock(t, RIVER_CALM, dur=1.0, floor=0.25),
                                                  gain=_gain((0.0, 0.0), (20.6, 0.0), (21.85, 1.0), (22.9, 1.0),
                                                             (23.5, 0.5), (25.6, 0.5),
                                                             (26.4, 0.35), (28.2, 0.35), (29.2, 0.0), (TOTAL, 0.0)))),
              depth_of_field=False)
    # the door fades before we pass through it (no white bars across the arriving Respect)
    scene.add("door", NearFade(FX.Door(P3, width=1.4, height=2.5, facing=0.0, t_open=23.0,
                                       gain=_gain((0.0, 0.0), (21.9, 0.0), (22.3, 1.0), (25.2, 1.0), (25.65, 0.0),
                                                  (TOTAL, 0.0))), 4.0))
    # the petals rise from his open palm and stream on through the doorway (never across him)
    palm = np.asarray(C["concession"][0].where(24.6, "palm.L"), np.float64)
    petal_path = [palm + _v(0.05, 0.02, 0.0), palm + _v(0.35, 0.18, -0.25), P3 + _v(-0.25, 1.25, 0.5),
                  P3 + _v(0.0, 1.35, 0.0), P3 + _v(0.2, 1.6, -3.0), P3 + _v(-0.4, 2.2, -8.0), P3 + _v(0.5, 3.4, -14.0)]
    scene.add("petals3", Clear(NearFade(FX.PetalStream(petal_path, 24.1, 25.3, n=1100, speed=2.6, spread=0.2), 6.0)),
              reflect=True)
    scene.add("tree", Clear(NearFade(FX.TreeOfLight(P3b + _v(7.0, 0.0, 2.5), height=3.4, t_bloom=25.9,
                                                    gain=_gain((0.0, 0.0), (25.4, 0.0), (25.9, 1.0), (28.2, 1.0),
                                                               (29.1, 0.0), (TOTAL, 0.0))), 5.0)))
    addp("concession", C["concession"])
    addp("respect", C["respect"])

    # ---- S4: the cathedral of falling light, rising lights
    nave = [P4 + _v(sx * 7.5, 0.0, dz) for dz in (8.0, 0.0, -8.0, -16.0) for sx in (-1.0, 1.0)]
    nave += [P4 + _v(0.0, 0.0, -24.0)]
    vault = _cloud_sea(r2, P4 + _v(0.0, 0.0, -14.0), 0.0, 75.0, 26, 56.0, 24.0, 48.0, 1.0, hk=(0.3, 0.5))
    scene.add("clouds_vault", MS.Billows(vault, gain=_gain((0.0, 0.0), (28.2, 0.0), (29.3, 1.0), (34.8, 1.0),
                                                           (35.9, 0.0), (TOTAL, 0.0)), seed=20, alpha=0.07, body=0.2,
                                         rose="#d0609a", lilac="#6a50c0",
                                         sun_az=SUN_AZ), depth_of_field=False)
    # the light pours down from under the words while they are read (never across them)
    scene.add("nave", ColumnClear(FX.LightColumns(nave, top=62.0, per=650, core_w=0.45, fall=6.0, core_k=0.8,
                                                  spark=0.04, segs=40,
                                                  gain=_gain((0.0, 0.0), (28.4, 0.0), (29.4, 1.0), (33.9, 1.0),
                                                             (34.8, 0.0), (TOTAL, 0.0)))))
    scene.add("pour4", PW.KeepClear(FX.LightColumns([P4], top=30.0, per=420, fall=2.4, ring=1.2, core=False,
                                                    spark=0.03, soft=True,
                                                    gain=_gain((0.0, 0.0), (28.4, 0.0), (29.4, 0.45), (33.9, 0.45),
                                                               (34.8, 0.0), (TOTAL, 0.0))), WORDS))
    scene.add("rising4", Clear(FX.RisingLights(P4, 30.0, r0=2.5, r1=45.0, n=700, speed=16.0, until=SEC[5])))
    addp("encouragement", C["encouragement"])

    # ---- S5: the help up, the twirl, the crowd of light
    addp("consideration", C["consideration"])
    addp("compliment", C["compliment"])
    try:
        places = _crowd_places(np.random.default_rng(55))
        crowd = _joy_crowd(places)
        scene.add("crowd5", PW.KeepClear(crowd, WORDS), reflect=False)      # no tall columns in the water
    except Exception as e:          # pragma: no cover
        print("crowd skipped:", e)
    twirl = C["compliment"][0]
    scene.add("hearts5", Clear(MB.HeartBurst(lambda t: twirl.where(t, "chest"), 39.9, NINE_GLOW, n=30,
                                             reach=1.5)), reflect=False)

    # ---- the breath: a still moment of light; it gathers into one pearl over the calm sea
    scene.add("gather", FX.Gather(PEARL, SEC[6] - 0.1, BREATH_END, colors=NINE_GLOW), reflect=True)

    # ---- the ascent: the nine colours stream past us and upward in long sweeping spirals, opening out as we
    # break above the clouds
    rs = np.random.default_rng(404)
    streaks = []
    n_s = 30
    for j in range(n_s):
        tl = BREATH_END + 0.05 + (HEAVEN_T - 0.6 - BREATH_END) * j / (n_s - 1) + rs.uniform(-0.05, 0.05)
        dl = rs.uniform(-0.8, 0.8)
        rr = rs.uniform(3.5, 10.5)
        om = (1.0 if j % 2 == 0 else -1.0) * rs.uniform(0.25, 0.6)
        y0 = rs.uniform(-15.0, -9.0)
        vr = rs.uniform(7.0, 11.0)

        def f(t, tl=tl, dl=dl, rr=rr, om=om, y0=y0, vr=vr):
            u = t - tl
            a = _asc_angle(t) + dl + om * u
            r = rr + 34.0 * max(t - (HEAVEN_T - 0.5), 0.0) ** 2
            return A7 + _v(np.sin(a) * r, _climb(t) + y0 + vr * u, np.cos(a) * r)

        def g(t, tl=tl):
            return sc(tl, tl + 0.15, t) * (1.0 - sc(tl + 1.0, tl + 1.5, t)) * (1.0 - sc(HEAVEN_T, HEAVEN_T + 0.4, t))
        streaks.append((f, NINE_GLOW[j % 9], g, 0.5))
    scene.add("streaks", NearFade(Clear(MB.Rivers(streaks, cuts=[BREATH_END], tail=0.6, seed=12)), 4.0),
              reflect=False)
    scene.add("pillar7", FX.LightColumns([A7], top=320.0, per=4000, core_w=2.2, fall=-6.0, core_k=0.4,
                                         gain=_gain((0.0, 0.0), (43.75, 0.0), (44.15, 1.0), (HEAVEN_T - 0.7, 1.0),
                                                    (HEAVEN_T + 0.2, 0.0), (TOTAL, 0.0))), reflect=False)

    # ---- above the clouds: the glory of the sun, and the nine colours flying ahead of us toward the light
    o_h = _asc_pos(HEAVEN_T)
    rt_h = _unit(np.cross(HV, UP))

    def ahead(k):
        x = (k - 4.0) / 4.0
        yk = 0.9 * np.sin(1.7 * k + 0.4)
        sd = _sun_dir()
        up_h = _unit(np.cross(rt_h, sd))

        def f(t):
            u = max(t - (HEAVEN_T - 0.3), 0.0)
            d = 7.0 + 16.0 * u + 8.0 * u * u
            w = 7.0 * (1.0 - 0.8 * d / (d + 50.0))
            wv = 1.3 * (1.0 - 0.6 * d / (d + 50.0))
            lift = _climb(t) - float(o_h[1]) + float(A7[1])          # they keep pace with us as we rise
            return (o_h + sd * d + rt_h * (x * w + wv * np.sin(1.5 * t + 1.3 * k))
                    + up_h * (yk * w * 0.55 + wv * np.cos(1.2 * t + 0.9 * k)) + _v(0.0, lift - 1.5, 0.0))
        return f
    heads = [(ahead(k), NINE_GLOW[k], lambda t: sc(HEAVEN_T - 0.3, HEAVEN_T + 0.2, t) * (1.0 - sc(ASC1 - 0.4, ASC1 + 0.1, t)),
              1.0) for k in range(9)]
    scene.add("ahead", Clear(MB.Rivers(heads, cuts=[HEAVEN_T - 0.3], tail=1.1, seed=13)), reflect=False)
    scene.add("glory", FX.Glory(lambda t: _asc_pos(min(t, ASC1)) + 900.0 * _sun_dir(), n=28,
                                gain=_gain((0.0, 0.0), (HEAVEN_T - 0.4, 0.0), (HEAVEN_T + 0.6, 1.0), (ASC1 - 0.2, 1.0),
                                           (ASC1 + 0.4, 0.0), (TOTAL, 0.0))), reflect=False)

    # ---- the pearl bursts (06's attack), a fountain of light and a ring of the nine colours
    scene.add("fountain", Clear(FX.Fountain(A7 + _v(0.0, 0.5, 0.0), BREATH_END, n=4000, colors=NINE_GLOW,
                                            speed=(6.0, 16.0))), reflect=True)
    scene.add("ring9", NearFade(Clear(FX.ColorRing(A7, BREATH_END, NINE_GLOW, speed=18.0, reach=320.0)), 20.0))

    # ---- the finale: BRAND's world of light. The nine symbols swirl round it as the music builds, lighting it
    # (the world brightens, hearts bloom across it from Las Vegas); at the hit they burst outward into light and
    # sparkle; the world becomes the logo (its hearts whole and in their own colours from the first frame), the
    # bloom into the pastel day, and the logo glides into the end card's place
    MB.rose_hearts(FINALE.logo)
    scene.add("finale globe", MB.Brighten(FINALE.globe, lambda t: 0.72 + 0.55 * sc(SWIRL[0] + 0.2, SWIRL[1], t)))
    scene.add("finale logo", _Fade(FINALE.logo, lambda t: 1.0 - sc(54.8, 55.2, t)))    # the card's logo takes over
    FINALE.add_to(_OnlyBloom(scene))
    scene.add("swirl", Clear(MB.SymbolSwirl(FIN_C, FIN_R, PW.LABELS, NINE_GLOW, SWIRL[0], SWIRL[1], CAMERA,
                                            scale=_fin_scale)), reflect=False)
    pastel = _cloud_sea(rng, FIN_C, 260.0, 1600.0, 150, float(FIN_C[1]) - 40.0, 60.0, 130.0, 1.0, hk=(0.28, 0.45))
    scene.add("clouds_pastel", MS.Billows(pastel, gain=_gain((0.0, 0.0), (BLOOM_T, 0.0), (BLOOM_T + 1.0, 0.6),
                                                             (TOTAL, 0.6)), seed=15, alpha=0.03, body=0.2,
                                          top="#ffd8bc", warm="#f2b994", rose="#eaa894", lilac="#dcb2a4",
                                          core="#ffe2c8", shade=0.5, sun_az=180.0), depth_of_field=False)

    def card(t):                    # the end card's middle, in the picture's plane, 14 m ahead of the lens
        cam = PW._cam_at(CAMERA, t)
        r, u, f = cam.basis()
        return np.asarray(cam.pos, np.float64) + 14.0 * f, r, u
    scene.add("final_glow", MB.FinalGlow(card, FINAL_HIT, ring=0.04, glint=0.05), reflect=False)
    # the end card stays alive: sparkles and hearts drifting, a slow glow breath, settling to near stillness
    # over the last 1.5 s; the lettering pushes in with the picture (about 2 percent)
    scene.add("card_life", MB.CardLife(card, EC_IN + 0.3, TOTAL - 1.5), reflect=False, depth_of_field=False)
    try:
        MB.endcard_push(TW.R(PUSH[0]), TOTAL, push=0.02)
    except Exception as e:          # pragma: no cover (the titles are drawn by the renderer)
        print("end card push skipped:", e)

    # ---- hearts off every word, the nine symbols as subtle scenery
    acts = [("Greeting", P1 + _v(0.0, 1.45, 0.0), 10.2, 12.1), ("Gratitude", None, 13.3, 15.4),
            ("Apology", P2 + _v(0.0, 1.05, 0.0), 17.0, 18.2), ("Inclusiveness", P2 + _v(0.0, 1.78, 0.0), 19.9, 21.8),
            ("Concession", P3 + _v(-1.0, 1.45, 2.0), 23.5, 25.5), ("Respect", P3b + _v(0.0, 1.0, 0.0), 26.6, 28.6),
            ("Encouragement", P4 + _v(-0.05, 1.05, 0.0), 31.0, 33.3),
            ("Consideration", P5 + _v(0.0, 1.0, 0.0), 36.8, 38.7), ("Compliment", P5b + _v(0.0, 1.3, 0.0), 40.2, 42.0)]
    grat = C["gratitude"][0]
    for k, (lab, at, t0, t1) in enumerate(acts):
        src = (lambda t: np.asarray(grat.where(t, "heart"), np.float64)) if at is None else (lambda t, at=at: at)
        scene.add("hearts_%d" % k, Clear(BR.HeartDrift(src, t0, t1, color=GLOWC[lab], rate=3.2, life=2.6, rise=0.42,
                                                       spread=0.35, size=(0.06, 0.12), style="heart", seed=300 + k)),
                  reflect=False)
    for k, (lab, tt, anchor, size) in enumerate(SYMBOL_PLAN):
        scene.add("symbol_%d" % k, Clear(MB.SymbolLight(lab, anchor, tt, GLOWC[lab], size=size, seed=91 + k)))

    WORDS.add_to(scene, reflect=False)
    try:
        WORDS.check(CAMERA)
    except Exception as e:          # the check is advice; never stop a render for it
        print("words check failed:", e)


class _Dim:
    """Wraps a point set: its light (alpha) times f(t); nothing drawn while f is 0."""

    def __init__(self, inner, f):
        self.inner, self.f = inner, f
        self.wants_camera = bool(getattr(inner, "wants_camera", False))

    def sample(self, t, cam=None):
        k = float(self.f(t))
        if k <= 0.0:
            return None
        ps = self.inner
        res = ps.sample(t, cam) if self.wants_camera else ps.sample(t)
        if res is None or k >= 1.0:
            return res
        out = []
        for b in (res if isinstance(res, (list, tuple)) else [res]):
            if b is None:
                continue
            b = dict(b)
            b["alpha"] = np.asarray(b.get("alpha", 1.0), np.float64) * k
            if b.get("alpha2") is not None:
                b["alpha2"] = np.asarray(b["alpha2"], np.float64) * k
            out.append(b)
        return out


class _Fade:
    """Wraps a point set that has a gain (BRAND's Logo): its gain times f(t)."""

    def __init__(self, inner, f):
        self.inner, self.f = inner, f
        self.wants_camera = bool(getattr(inner, "wants_camera", False))

    def gain(self, t):
        g = float(self.inner.gain(t)) if hasattr(self.inner, "gain") else 1.0
        return g * float(self.f(t))

    def sample(self, t, cam=None):
        if float(self.f(t)) <= 0.0:
            return None
        ps = self.inner
        return ps.sample(t, cam) if self.wants_camera else ps.sample(t)


class _OnlyBloom:
    """Hands FINALE.add_to only its bloom: the song adds the globe and the logo itself (the globe brightens with
    the swirl; the logo's hearts arrive whole)."""

    def __init__(self, scene):
        self.scene = scene

    def add(self, name, ps, **kw):
        if name.endswith(" bloom"):
            self.scene.add(name, ps, **kw)


def _sym_place(c, cam_t):
    """A symbol standing at c, facing the camera as it is at cam_t."""
    def f(t):
        cam = PW._cam_at(_LAYOUT, cam_t)
        d = _unit(np.asarray(cam.pos, np.float64) - c)
        rt = _unit(np.cross(UP, d))
        return c, rt, UP
    return f


# each symbol drawn subtly in the world near its expression, in its colour (never over the words)
SYMBOL_PLAN = [
    ("Greeting", 10.2, _sym_place(P1 + _v(-2.6, 2.2, -3.0), 10.6), 0.9),
    ("Gratitude", 13.2, _sym_place(P1b + _v(2.6, 2.4, -4.0), 13.6), 1.0),
    ("Apology", 16.9, _sym_place(P2 + _v(-3.2, 2.0, -4.0), 17.4), 1.0),
    ("Inclusiveness", 20.2, _sym_place(P2 + _v(3.0, 2.6, -5.0), 20.6), 1.2),
    ("Concession", 23.6, _sym_place(P3 + _v(-3.0, 1.6, -2.0), 24.0), 1.1),
    ("Respect", 26.8, _sym_place(P3b + _v(-2.8, 3.4, -3.5), 27.2), 1.1),
    ("Encouragement", 30.6, _sym_place(P4 + _v(-3.6, 3.0, -6.0), 31.0), 1.4),
    ("Consideration", 36.6, _sym_place(P5 + _v(3.4, 2.4, -4.0), 37.0), 1.1),
    ("Compliment", 40.0, _sym_place(P5b + _v(-3.4, 2.8, -5.0), 40.4), 1.2),
]


LAS_VEGAS_LON = -115.1
FIN_SPIN = 6.0
FINALE = BR.Finale(pos=tuple(FIN_C), radius=FIN_R, shrink=FIN_SHRINK, camera=CAMERA, look="night", t_world=FIN_T,
                   spin=FIN_SPIN, front=LAS_VEGAS_LON - FIN_SPIN * HEARTS_T0,   # Las Vegas faces us as hearts begin
                   hearts=dict(t0=HEARTS_T0, t1=HEARTS_T1, n=44), t_settle=SETTLE, t_logo=LOGO_T,
                   bloom=dict(t=BLOOM_T, dur=1.6), blend=2.4,       # the day comes up softly (about 1.7 s)
                   end=dict(t=(END_T0, END_T), ride=(0.5, 1.0 - SLOT_Y, 14.0), frac=SLOT_H), logo=dict(reflect=False))

def _world_on_new_time(w):
    """The world's settings on the new medley's time: its look keys moved to the new times (blends scaled with
    the local pace), its calm discs and shafts asked at W(t)."""
    w = dict(w)
    keys = []
    for k in w["look"]:
        t, name = float(k[0]), k[1]
        bl = float(k[2]) if len(k) > 2 else 1.5
        tn = TW.R(t)
        keys.append((tn, name, bl / max(TW.rate(tn), 1e-3)))
    w["look"] = keys
    calm = w.get("calm")
    if callable(calm):
        w["calm"] = lambda t, f=calm: f(TW(t))
    sh = []
    for d in w.get("shafts", []):
        d = dict(d)
        for k in ("base", "strength"):
            if callable(d.get(k)):
                d[k] = (lambda f: (lambda t: f(TW(t))))(d[k])
        sh.append(d)
    w["shafts"] = sh
    return w


def _bursts_on_new_time(bs):
    out = []
    for b in bs:
        b = dict(b)
        b["t"] = TW.R(float(b["t"]))
        out.append(b)
    return out


def _samples_on_new_time(spans):
    """P3D motion_samples on the new medley's time: n samples in each (old t0, old t1, n), 1 elsewhere."""
    sp = [(TW.R(a), TW.R(b), int(n)) for a, b, n in spans]
    return lambda t: max([n for a, b, n in sp if a <= t <= b] + [1])


P3D = dict(
    camera=WarpRig(CAMERA, TW),
    world=_world_on_new_time(
        FINALE.world(dict(WORLD, shafts=[_shaft([(P1b, 12.3, 16.0, 0.45), (P5, 35.6, 39.2, 0.45)], radius=1.2),
                                         _shaft([(P3, 22.6, 25.9, 0.5), (P5b, 39.2, 42.6, 0.5)], radius=1.2,
                                                color="#ffeccc"),
                                         _shaft([(P2, 19.2, 21.9, 0.35)], radius=1.0, color="#ffd8a0", top=22.0)]))),
    setup=_setup,
    bursts=_bursts_on_new_time(
        [dict(t=LAND_T, strength=0.1, rise=0.35, fall=0.8, color="#ffd9a0", at=tuple(D0 + _v(0.0, 2.0, 0.0))),
         dict(t=BREATH_END, strength=0.15, rise=0.4, fall=0.9, color="#ffd9a0", at=tuple(A7 + _v(0.0, 6.0, 0.0))),
         # THE LIFT: the sun of the glory flares warm as we launch out to the world (never white)
         dict(t=ASC1 + 0.02, strength=0.2, rise=0.12, fall=0.9, color="#ffc890", radius=0.45,
              at=tuple(_asc_pos(ASC1) + 900.0 * _sun_dir()))]
        + FINALE.bursts()),
    motion_blur=0.5,
    # true motion blur (the point sets drawn at several moments of the shutter) through the fast moves where no
    # person is on screen (a body asked at several moments of a frame re-simulates its garments: very slow); the
    # carries past people are slow enough for the shutter's own streaks at 60 fps
    motion_samples=_samples_on_new_time([(6.85, 8.6, 6), (43.65, 48.2, 5), (49.0, 50.8, 4)]),
)


# =============================================================================================================
# THE TITLES (TITLES: the opening, the signature always on, the official-style end card); old keys off
# =============================================================================================================
FORM_DUR = 3.0
TITLE_FORM = 1e9
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=1e9, hold=1e9, star=1e9)
TAGLINE = dict(text="", t0=1e9, t1=1e9 + 1.0)
FRAGMENTS = []
TITLE_HIT = 1e9
PHRASES = _base.PHRASES
WAVES = []

# The signature: on from the opening's end to the end card without a break, in one corner. Only its palette
# changes, by a cross-fade (two windows overlapping by the fade: one fades out exactly as the other fades in)
# when the sky behind the corner turns bright. (start, palette) in order; it fades out under the end card.
SIG_FADE = 0.6
SIG_PALETTES = [(OPEN_FULL + 0.7, "night"), (BLOOM_T + 0.05, "day")]
SIG_END = EC_IN + 0.3                            # gone before the card's lines sweep in under it


def _sig_windows():
    out = []
    for i, (a, pal) in enumerate(SIG_PALETTES):
        b = SIG_PALETTES[i + 1][0] + SIG_FADE if i + 1 < len(SIG_PALETTES) else SIG_END
        out.append((TW.R(a), TW.R(b), SIG_CORNER, pal))      # on the new medley's time
    return out


TITLES = dict(
    opening=dict(t_end=TW.R(OPEN_END), dissolve=TW.R(OPEN_END) - TW.R(OPEN_FULL), y=0.30, palette="night",
                 protect=dict(keep=0.6, blur=12.0, gain=4.0)),      # no dark window as we dive behind it
    # on over the whole film, over every kind of light: the scene's light is dimmed only close round its letters
    # (titles.py signature protect), never as a dark box behind it
    signature=dict(windows=_sig_windows(), fade=SIG_FADE, protect=dict(keep=0.7, blur=6.0, gain=3.0)),
    # its own crisp BRAND logo (exact colours, drawn over the veil) takes over from the 3D logo as the card sweeps
    # in; a lighter veil, so the pastel day under the card stays a soft peach and cream
    end_card=dict(t_in=TW.R(EC_IN), fade=EC_FADE, scale=EC_SCALE, backdrop="auto", veil=0.6),
)
