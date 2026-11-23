"""The song kit's conductor of light: Song 11's conductor (tools/s11_full2/s11_dance.py, round 7 onward; Anthony:
"Instead of a dancer, have a conductor but have it be dramatic as if he's conducting everything") made reusable
for any song. Song 11's delivered source is not changed; this is a generalized copy.

A song uses him by listing "kit_conductor" in song_data.SETS and giving edit blocks to the owner "conductor"
(EDIT entries (t0, "conductor", note)). SHOTS below are made for those blocks. A song that gives him no blocks
can still import this set: SHOTS is then empty, and he stands and conducts wherever CONDUCTOR["spans"] says
(or the whole film when there are no spans either), seen by other sets' shots that look at his place.

One heroic man of light in a tailcoat of light (no facial features) stands on a disc of light on the mirror sea
and conducts everything. His right hand beats real 4/4 patterns on the measured beat grid and downbeats (the
song's music map, work/song_kit/<song>/music_fx.npz, falling back to the engine's beats); the baton's tip is a
white-hot point that leaves a trail of the nine colours; comets are flung from the tip on the song's hits; the
sea ripples out from his feet on each downbeat; the world's sets named in CONDUCTOR["swell"] swell on his
upbeat; rays open when he raises both arms. Between the special moments he simply conducts on the grid.

song_data.CONDUCTOR (a dict; every key optional; Song 11's values as the example). Every moment defaults to
None (or empty), which switches it off so he simply conducts on the beat grid:
  at              (x, y, z) his disc on the mirror sea. Default (0.0, 0.0, 160.0). Song 11: (0.0, 0.0, 160.0)
  facing          degrees (p3d: 0 faces +z, 90 faces +x), or None to face the song's HOME. Song 11: None
                  (HOME is 580 m before him toward -z, so he faces 180)
  spans           [(t0, t1)] where he is seen besides his own blocks. Default []. Song 11: []
  summons         (t0, t1) THE SUMMONS: four big strokes, a stream off the tip on each beat braiding into one
                  rope to the sky, both arms up on the last beat and the rays open. Song 11: (97.7, 99.4)
  breath          (t0, t1) THE BREATH: hushed, small and slow, the left hand calming the sea, light falling
                  like snow. Song 11: (117.0, 121.32)
  strings         (t0, t1) THE STRINGS: quick staccato flicks, the left hand cues the strings open.
                  Song 11: (121.32, 125.92)
  strings_pulses  [t] the strings pulses inside it: the baton flicks up and a stream shoots off over the sea.
                  Song 11: [121.32, 124.18]
  heart           (t0, t1) WONDROUS LOVE: on the hit both arms sweep down from overhead and draw a heart; two
                  streams draw the same heart huge in the sky; it stays, beating. Song 11: (185.92, 188.27)
  heart_draw      (t0, t1) when the hands draw the heart. Default: from heart[0] for 45 percent of the
                  moment. Song 11: (185.92, 186.97)
  heart_hit       the hit the sky heart beats on. Default heart[0]. Song 11: 185.92 (HIT["love"])
  held            (t0, t1) THE HELD BREATH: the fermata, baton poised high, sparks gathering into its tip.
                  Song 11: (247.5, 249.43)
  rise            the final rise in the held breath: the baton sweeps up, a stream flies on, rays open.
                  Default held[1] - 0.31. Song 11: 249.12
  flings          [t] other times a comet is flung off the tip. Default None: the song's HIT times that fall in
                  his own blocks outside the moments. Song 11: [] (its flings are the strings pulses)
  bar_anchor      a downbeat time, used only when the music map has no downbeats. Default: the first beat.
                  Song 11: 121.32 (HIT["mother"])
  swell           names of other sets whose gain swells on his upbeat while he is seen. Default [].
                  Song 11: ["city dim", "city gold", "zion dim", "zion gold", "zion gardens", "zion towers",
                  "zion gates", "church"]
  faint           names of other sets held to 20 percent while he is seen. Default []. Song 11: ["paths"]

The moments' inner timings keep Song 11's offsets from these times (for example the arms go up 0.4 s before
the end of the summons). Camera shots: SHOTS (one per block he owns, exact times). Point sets: add(scene).
No em dash or en dash anywhere in this file.
"""
import os
import pathlib

import numpy as np

import song_data as SD
from songs.kit_film import *  # noqa: F401,F403
import songs.kit_film as H

OWNER = "conductor"
C = dict(getattr(SD, "CONDUCTOR", {}) or {})


def _pair(k):
    v = C.get(k)
    return None if v is None else (float(v[0]), float(v[1]))


DANCE_C = _v(*C.get("at", (0.0, 0.0, 160.0)))      # his disc on the mirror sea
COND_C = DANCE_C
if C.get("facing") is not None:
    _f = np.radians(float(C["facing"]))
    FWD = _v(np.sin(_f), 0.0, np.cos(_f))
else:
    _d = _v(H.HOME[0] - COND_C[0], 0.0, H.HOME[2] - COND_C[2])
    FWD = _unit(_d) if np.linalg.norm(_d) > 1e-6 else _v(0.0, 0.0, -1.0)
FACING = float(np.degrees(np.arctan2(FWD[0], FWD[2])))
LEFT = _v(FWD[2], 0.0, -FWD[0])                      # his left (Song 11: facing -z, his left is -x)
UP = _v(0.0, 1.0, 0.0)

SUMMONS = _pair("summons")
BREATH = _pair("breath")
STRINGS_W = _pair("strings")
STRINGS = [float(x) for x in C.get("strings_pulses", [])]
HEART = _pair("heart")
HELD = _pair("held")
if HEART is not None:
    HEART_T = _pair("heart_draw") or (HEART[0], HEART[0] + 0.447 * (HEART[1] - HEART[0]))
    HEART_HIT = float(C.get("heart_hit", HEART[0]))
else:
    HEART_T, HEART_HIT = None, None
RISE = (float(C["rise"]) if C.get("rise") is not None else HELD[1] - 0.31) if HELD else None
WINDOWS = {k: w for k, w in (("ring", SUMMONS), ("breath", BREATH), ("strings", STRINGS_W), ("heart", HEART),
                             ("held", HELD)) if w is not None}

LAV = PW.COLORS["Compliment"]
HEIGHT = 1.86
BATON = 0.52                           # the baton's length, metres
TIP_COL = "#fffaf0"


def _R(x, y, z):
    """A direction given in Song 11's world frame (he faces -z) turned to his facing."""
    return -LEFT * x + UP * y - FWD * z


def _D(x, y, z):
    return DANCE_C + _R(x, y, z)


def _W(q):
    """A point in his own frame (x his left, y up, z forward) in the world."""
    return COND_C + LEFT * q[0] + UP * q[1] + FWD * q[2]


def _local(d):
    """A world direction in Song 11's frame (the inverse of _R)."""
    return _v(-float(np.dot(d, LEFT)), float(d[1]), -float(np.dot(d, FWD)))


# =========================================================================================================
# The music map (work/song_kit/<song>/music_fx.npz, beside features.npz): read directly, 0 when missing
# =========================================================================================================
_MAP = {}


def _map():
    if "m" not in _MAP:
        m = None
        f = os.environ.get("FEATURES")
        if f:
            try:
                with np.load(pathlib.Path(f).parent / "music_fx.npz") as z:
                    m = {k: np.asarray(z[k], np.float64) for k in z.files}
            except Exception:  # noqa: BLE001  (no music map: the engine's beats, no music channels)
                m = None
        _MAP["m"] = m
    return _MAP["m"]


# =========================================================================================================
# The bar grid: the measured beats and downbeats (music map), falling back to the engine's beat grid
# =========================================================================================================
_GRID = {}


def _grid():
    if _GRID:
        return _GRID
    B = Dn = None
    m = _map()
    if m is not None and "down_t" in m and "beat_t" in m:
        B, Dn = m["beat_t"], m["down_t"]
    if B is None or len(B) < 8 or len(Dn) < 2:
        B = np.asarray(BEATS, np.float64)
        if len(B) < 2:
            B = np.arange(0.0, max(H.TOTAL, 1.0), 0.5)
        anchor = float(C.get("bar_anchor", B[0]))
        i0 = int(np.argmin(np.abs(B - anchor)))
        Dn = B[(np.arange(len(B)) - i0) % 4 == 0]
    c = np.arange(len(B), dtype=np.float64)
    dn = np.round(np.interp(Dn, B, c))
    _GRID.update(B=B, c=c, dn=np.unique(dn))
    return _GRID


def bar_pos(t):
    """Where t lies in its bar, 0..4: 0 is the downbeat, 1, 2, 3 the other beats (fractional between)."""
    g = _grid()
    cb = float(np.interp(t, g["B"], g["c"]))
    k = int(np.searchsorted(g["dn"], cb, side="right")) - 1
    if k < 0:
        return cb % 4.0
    return float(min(cb - g["dn"][k], 3.999))


def beat_times(a, b):
    g = _grid()
    B = g["B"]
    return [float(x) for x in B[(B >= a) & (B < b)]]


def down_times(a, b):
    g = _grid()
    Dn = np.interp(g["dn"], g["c"], g["B"])
    return [float(x) for x in Dn[(Dn >= a) & (Dn < b)]]


def _mf(name, t):
    m = _map()
    if m is None or name not in m or t > LIVE:
        return 0.0
    return float(np.interp(t, m["times"], m[name], left=0.0, right=0.0))


def _timp_hits(min_s=0.5):
    m = _map()
    if m is None or "timp_t" not in m:
        return []
    return [(float(a), float(s)) for a, s in zip(m["timp_t"], m["timp_s"]) if s >= min_s and a < LIVE]


def upbeat(t):
    """The upbeat swell: rises through beat 4 into the downbeat, then falls away (the world breathes in)."""
    p = bar_pos(t)
    return _sc(2.4, 3.95, p) if p >= 1.0 else float(np.exp(-p / 0.22))


def downbeat(t, fall=0.35):
    p = bar_pos(t)
    return float(np.exp(-p * 0.47 / fall)) if p < 2.0 else 0.0


# =========================================================================================================
# Where he is seen: his own blocks and CONDUCTOR["spans"] (neither: the whole film)
# =========================================================================================================
def _merge(spans):
    out = []
    for a, b in sorted(spans):
        if out and a <= out[-1][1] + 1e-6:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


OWN = [(float(a), float(b)) for a, b, _n in H.blocks_of(OWNER)]
SEEN = _merge(OWN + [(float(a), float(b)) for a, b in C.get("spans", [])]) or [(-1.0, float(H.TOTAL) + 1.0)]


def dance_k(t):
    """1 where he is seen (his blocks and spans)."""
    for a, b in SEEN:
        if a <= t < b:
            return 1.0
    return 0.0


def _in(t, name, pre=0.6, post=0.6):
    if name not in WINDOWS:
        return False
    a, b = WINDOWS[name]
    return a - pre <= t <= b + post


# =========================================================================================================
# Shots (kind "local": the conductor on the sea, the song's world before him), one per block he owns
# =========================================================================================================
def _shot(name, t0, t1, fov, keys, ap=0.03, **kw):
    return dict(name=name, kind="local", t0=t0, t1=t1, fov=fov, aperture=ap,
                keys=[(t0 + f * (t1 - t0), p, q) for f, p, q in keys], **kw)


def _orbit(t0, t1):
    """A slow orbit round him from his right side toward his front, at chest height, looking at him."""
    keys = []
    for f in np.linspace(0.0, 1.0, 5):
        th = np.radians(70.0 + 55.0 * f)              # 0 behind him, 180 before him (Song 11's frame)
        r = 6.6 - 0.8 * f
        keys.append((float(f), _D(r * np.sin(th), 1.05 - 0.2 * f, r * np.cos(th)), _D(0.0, 1.45, 0.0)))
    return _shot("cond_orbit", t0, t1, 42.0, keys, ap=0.02, focus=6.2, pace="linear")


GENERIC = [
    # low behind his right shoulder, looking past him to the world he conducts; a slow push in
    lambda t0, t1: _shot("cond_behind", t0, t1, 50.0, [(0.0, _D(2.4, 0.85, 7.6), _D(-0.3, 2.6, -24.0)),
                                                       (1.0, _D(1.7, 0.70, 5.4), _D(-0.3, 2.9, -24.0))],
                         ap=0.012, focus=6.0, roll=(-2.0, 1.0), pace="linear"),
    _orbit,
    # close from the front for a moment, low, looking up at him against the sky
    lambda t0, t1: _shot("cond_front", t0, t1, 40.0, [(0.0, _D(1.5, 0.55, -4.8), _D(0.0, 1.70, 0.0)),
                                                      (1.0, _D(1.2, 0.50, -4.1), _D(0.0, 1.85, 0.0))],
                         ap=0.03, pace="linear"),
]

# the moments' own framings (Song 11's, positioned relative to his place)
MOMENT_SHOTS = dict(
    # the summons: low behind his right shoulder, looking up past him to the sky the comets braid into
    ring=lambda t0, t1: _shot("cond_ring", t0, t1, 56.0, [(0.0, _D(2.6, 0.70, 6.2), _D(-0.3, 2.2, -6.0)),
                                                          (0.82, _D(1.35, 0.44, 3.7), _D(-0.2, 4.9, -9.0)),
                                                          (1.0, _D(1.30, 0.42, 3.6), _D(-0.2, 5.2, -9.0))],
                              roll=(-3.0, 2.0), pace="linear"),
    # the breath: low behind and to his left, a slow drift round him
    breath=lambda t0, t1: _shot("cond_breath", t0, t1, 44.0, [(0.0, _D(-2.7, 0.6, 3.4), _D(0.3, 1.55, -2.0)),
                                                              (1.0, _D(-1.6, 0.5, 3.9), _D(0.3, 1.6, -2.0))],
                                pace="linear"),
    # the strings: a slow push in from wide over the sea, settling on him as he cues the strings open
    strings=lambda t0, t1: _shot("cond_strings", t0, t1, 50.0, [(0.0, _D(7.4, 1.0, 4.6), _D(-0.6, 2.1, -4.0)),
                                                                (0.85, _D(4.5, 0.8, 2.7), _D(-0.5, 2.2, -4.2)),
                                                                (1.0, _D(4.4, 0.8, 2.6), _D(-0.5, 2.2, -4.2))],
                                 roll=(2.0, -1.0), pace="linear"),
    # wondrous love: low in front of him on a long lens, looking up at him against the sky; he stands at the
    # right edge, the heart drawn in the sky above the middle
    heart=lambda t0, t1: _shot("cond_heart", t0, t1, 38.0, [(0.0, _D(3.0, 0.45, -7.5), _D(3.9, 4.0, 8.0)),
                                                            (1.0, _D(2.9, 0.42, -7.1), _D(3.9, 4.1, 8.0))],
                               pace="linear"),
    # the held breath: low in front of him, looking up against the light; tilting up as the comet flies on
    held=lambda t0, t1: _shot("cond_held", t0, t1, 46.0, [(0.0, _D(1.6, 0.45, -4.6), _D(0.0, 1.75, 0.0)),
                                                          (0.8, _D(1.3, 0.42, -4.1), _D(0.0, 1.9, 0.0)),
                                                          (1.0, _D(1.25, 0.42, -4.0), _D(0.0, 2.8, 0.0))],
                              pace="linear"),
)


def _make_shots():
    out, last, g = [], None, 0
    for t0, t1, _note in H.blocks_of(OWNER):
        moment = None
        for name in ("heart", "held", "ring", "strings", "breath"):     # the heart's view places the sky heart
            w = WINDOWS.get(name)
            if w is not None and t0 - 0.05 <= w[0] < t1:
                moment = name
                break
        if moment is not None:
            s = MOMENT_SHOTS[moment](t0, t1)
        else:
            k = g % len(GENERIC)
            if last is not None and GENERIC[k](t0, t1)["name"] == last:
                g += 1
                k = g % len(GENERIC)
            s = GENERIC[k](t0, t1)
            g += 1
        out.append(s)
        last = s["name"]
    return out


SHOTS = _make_shots()


# =========================================================================================================
# The hands: a real 4/4 pattern on the beat (right hand, the baton), and what the left hand does in each moment
# =========================================================================================================
# the ictus of each beat (the bottom of each stroke, where the beat falls) and the rebound between beats, in the
# pattern's own units (x toward his left, y up); the hand leaves each ictus fast, slows at the rebound's top and
# falls fast into the next ictus
_ICT = [(0.0, -0.26), (0.32, -0.10), (-0.44, -0.10), (-0.12, 0.06)]
_REB = [(0.08, 0.10), (-0.02, 0.07), (-0.34, 0.18), (-0.04, 0.46)]
R_CEN = (-0.22, 1.30, 0.44)                 # where the pattern sits (his right, before the chest)


def _pattern(p, amp=1.0, style="legato"):
    """The right hand at bar position p (0..4), his frame."""
    k = int(np.floor(p)) % 4
    s = p - np.floor(p)
    if style == "staccato":                  # a flick away from the ictus, then still until the next
        s = 1.0 - (1.0 - min(s * 1.15, 1.0)) ** 2.2
    a, c, b = np.array(_ICT[k]), np.array(_REB[k]), np.array(_ICT[(k + 1) % 4])
    q = (1.0 - s) ** 2 * a + 2.0 * s * (1.0 - s) * c + s * s * b
    z = R_CEN[2] + 0.07 * amp * (1.0 - np.sin(np.pi * s))
    return np.array([R_CEN[0] + amp * q[0], R_CEN[1] + amp * q[1], z])


L_HUSH = np.array([0.30, 1.02, 0.42])       # the left hand low, palm down: softly
L_HOLD = np.array([0.30, 1.22, 0.36])
L_UP = np.array([0.40, 2.05, 0.22])         # both arms raised: the rays open
R_UP = np.array([-0.38, 2.08, 0.26])


def _mirror(r):
    return np.array([-r[0], r[1], r[2]])


def _heart_xy(s):
    """The heart outline from the top dip (s = 0) round one lobe to the bottom point (s = 1): x >= 0, y (units)."""
    th = np.pi * s
    x = 16.0 * np.sin(th) ** 3
    y = 13.0 * np.cos(th) - 5.0 * np.cos(2 * th) - 2.0 * np.cos(3 * th) - np.cos(4 * th)
    return x / 16.0, y / 16.0


HAND_HEART_C = np.array([0.0, 1.62, 0.50])  # the heart his hands draw (his frame)
HAND_HEART_S = 0.38                         # its half width (kept narrow so he stands clear of the phrase)


def _heart_prog(t):
    u = float(np.clip((t - HEART_T[0]) / (HEART_T[1] - HEART_T[0]), 0.0, 1.0))
    return u ** 0.8 * (1.6 - 0.6 * u ** 0.8) if u < 1.0 else 1.0      # fast off the hit, easing in at the bottom


def _plain(t, p):
    """Plain conducting on the grid: the pattern grows with the music, the left hand shadows it softly."""
    amp = 0.75 + 0.45 * intensity(t)
    r = _pattern(p, amp, "legato")
    l = L_HOLD * 0.55 + (_mirror(r) + np.array([0.0, -0.05, -0.04])) * 0.45
    return r, l


def _pose_ring(t, p):                        # the summons: big, marcato; both arms up on the last beat
    b = SUMMONS[1]
    r = _pattern(p, 1.35, "legato")
    l = _mirror(r) + np.array([0.0, -0.05, -0.04])
    up = _sc(b - 0.40, b - 0.08, t)
    return r * (1 - up) + R_UP * up, l * (1 - up) + L_UP * up


def _pose_breath(t, p):                      # the breath: small and slow, the left hand calming the sea
    r = _pattern(p, 0.55, "legato")
    sway = 0.04 * np.sin(2.0 * np.pi * (t - BREATH[0]) / 3.6)
    return r, L_HUSH + np.array([0.0, sway, 0.0])


def _pose_strings(t, p):                     # the strings: staccato flicks, up on each strings pulse
    r = _pattern(p, 0.85, "staccato")
    fl = hit_pulse(t, STRINGS, rise=0.06, fall=0.32)
    r = r + np.array([-0.10 * fl, 0.42 * fl, 0.0])
    cue = hit_pulse(t, STRINGS, rise=0.12, fall=0.9)
    l = L_HOLD + np.array([0.28, 0.30, -0.06]) * min(cue, 1.0)
    return r, l


def _pose_heart(t, p):                       # wondrous love: overhead, the heart on the hit, then the next bar
    x0, y0 = _heart_xy(0.0)
    top = HAND_HEART_C + np.array([0.0, y0 * HAND_HEART_S, 0.0])
    if t < HEART_T[0]:                       # poised at the heart's top, lifting into the hit
        lift = _sc(HEART_T[0] - 1.2, HEART_T[0] - 0.12, t)
        return (top + np.array([-0.06, 0.10 + 0.22 * lift, -0.04]),
                top + np.array([0.06, 0.10 + 0.22 * lift, -0.04]))
    if t <= HEART_T[1]:
        x, y = _heart_xy(_heart_prog(t))
        sc = HAND_HEART_S
        r = HAND_HEART_C + np.array([-x * sc, y * sc, 0.0])
        return r, _mirror(r)
    w = _sc(HEART_T[1], HEART_T[1] + 0.35, t)
    x, y = _heart_xy(1.0)
    bot = HAND_HEART_C + np.array([0.0, y * HAND_HEART_S, 0.0])
    r = _pattern(p, 0.62, "legato") + np.array([0.10, 0.06, 0.0])
    l = L_HOLD + np.array([-0.04, 0.30 + 0.15 * _sc(HEART_T[1] + 0.43, HEART[1] - 0.07, t), -0.02])
    return bot * (1 - w) + r * w, bot * (1 - w) + l * w


def _pose_held(t, p):                        # the fermata, poised high; the dip on beat 4, up on the final rise
    breath = 0.012 * np.sin(2.0 * np.pi * (t - HELD[0]) / 1.9)
    poised = np.array([-0.30, 1.78 + breath, 0.42])
    lpo = np.array([0.34, 1.48 + breath, 0.36])
    dip = _sc(RISE - 0.57, RISE - 0.17, t) * (1.0 - _sc(RISE - 0.17, RISE, t))
    up = _sc(RISE - 0.12, RISE + 0.28, t)
    r = poised + np.array([0.04, -0.30, 0.04]) * dip
    l = lpo + np.array([0.0, -0.18, 0.0]) * dip
    return r * (1 - up) + np.array([-0.22, 2.22, 0.20]) * up, l * (1 - up) + L_UP * up


def _moment_spans():
    """(name, lo, hi, pose): where each moment's pose holds (it eases to and from plain conducting over 0.4 s)."""
    out = []
    if SUMMONS:
        out.append(("ring", SUMMONS[0] - 1.5, SUMMONS[1] + 0.8, _pose_ring))
    joined = BREATH is not None and STRINGS_W is not None and abs(STRINGS_W[0] - BREATH[1]) < 0.1
    if BREATH:
        out.append(("breath", BREATH[0] - 0.5, BREATH[1] + (0.0 if joined else 0.5), _pose_breath))
    if STRINGS_W:
        out.append(("strings", STRINGS_W[0] - (0.0 if joined else 0.5), STRINGS_W[1] + 0.6, _pose_strings))
    if HEART:
        out.append(("heart", HEART_T[0] - 1.5, HEART[1] + 0.6, _pose_heart))
    if HELD:
        out.append(("held", HELD[0] - 0.8, max(HELD[1], RISE + 0.3) + 0.6, _pose_held))
    return out


MOMENTS = _moment_spans()


def _active(t):
    """(name, weight, pose) of the moment that holds the hands at t (weight 0: plain conducting)."""
    best = (None, 0.0, None)
    for name, lo, hi, pose in MOMENTS:
        if lo - 0.4 <= t <= hi + 0.4:
            w = _sc(lo - 0.4, lo, t) * (1.0 - _sc(hi, hi + 0.4, t))
            if w > 0.0 and w >= best[1]:
                best = (name, w, pose)
    return best


def _hands_raw(t):
    """(right, left) hand places in his frame at t, before smoothing (the poses the music asks for)."""
    p = bar_pos(t)
    r0, l0 = _plain(t, p)
    _name, w, pose = _active(t)
    if w <= 0.0:
        return r0, l0
    r, l = pose(t, p)
    return r0 * (1 - w) + r * w, l0 * (1 - w) + l * w


_SM_OFF = np.linspace(-2.2, 2.2, 13)
_SM_W = np.exp(-0.5 * _SM_OFF ** 2)
_SM_W = _SM_W / _SM_W.sum()


_HCACHE = {}


def _hands(t, lag=0.0):
    """Cached (many streams ask for the same moments of his hands every frame)."""
    key = (int(round(t * 2000.0)), lag)
    v = _HCACHE.get(key)
    if v is None:
        if len(_HCACHE) > 200000:
            _HCACHE.clear()
        v = _HCACHE[key] = _hands_s(t, lag)
    return v


def _hands_s(t, lag=0.0):
    """The hands, smoothed (Song 11 round 8, Anthony: "the conductor's animation is so choppy"): a gaussian over
    the raw poses (0.07 s; 0.045 s in the quick strokes of the summons and the strings) taken a little in the
    past, so every stroke eases in and out, nothing snaps, and the arms follow through behind the beat."""
    name, w, _pose = _active(t)
    sig = 0.045 if (name in ("ring", "strings") and w > 0.5) else 0.07
    c = t - 0.025 - lag
    R = np.zeros(3)
    L = np.zeros(3)
    for o, wt in zip(_SM_OFF, _SM_W):
        r, l = _hands_raw(c + o * sig)
        R += wt * r
        L += wt * l
    return R, L


def hand_R(t):
    return _W(_hands(t)[0])


def hand_L(t):
    return _W(_hands(t)[1])


_SH_R = np.array([-0.19, 1.50, 0.02])


def tip(t):
    """The baton's white-hot tip: along the arm from the shoulder through the hand, lifted forward and up."""
    h = _hands(t)[0]
    hl = _hands(t, lag=0.06)[0]              # the baton trails the hand: follow-through on every stroke
    d = _unit(h - _SH_R + np.array([0.0, 0.22, 0.30]) + 1.6 * (hl - h))
    return _W(h + d * BATON)


def tip_L(t):
    """The left fingertips (the left hand also draws the heart)."""
    h = _hands(t)[1]
    d = _unit(h - np.array([0.19, 1.50, 0.02]) + np.array([0.0, 0.1, 0.2]))
    return _W(h + d * 0.16)


# =========================================================================================================
# The conductor (p3d Body: a man in a tailcoat of light, glitter look, both arms driven to the hand places)
# =========================================================================================================
_BODIES = {}
BODY_BRIGHT = 2.4
# rim lit against the light (Song 11 round 8): a bright edge round the silhouette as the camera sees it, the
# inside a dim warm glitter, so he reads as a figure standing against the light rather than a white shape
LOOK = [dict(name="rim", bright=1.25, power=2.4), dict(name="glitter", bright=0.32)]
LIGHT_AT = _D(0.0, 3.5, 4.0)
SHOW = (-1.0, float(H.TOTAL) + 1.0)


def _gestures():
    g = []
    palm_r = dict(side="R", to=hand_R, end="palm", palm=(0.0, -0.6, 0.6), fingers="pinch", look=False, lean=0.35,
                  wrist=-12.0, ease=0.3)
    for a, b in SEEN:
        a, b = max(a - 0.8, SHOW[0]), min(b + 0.6, SHOW[1])
        g.append((a, b, "touch", dict(palm_r)))
        cuts = [a, b]
        if BREATH and a < BREATH[0] - 0.8 < b:       # the left palm turns down to calm the sea in the breath
            cuts = [a, BREATH[0] - 0.8, min(max(BREATH[1], (STRINGS_W or BREATH)[1]), b), b]
        for i in range(len(cuts) - 1):
            if cuts[i + 1] - cuts[i] <= 0.05:
                continue
            down = len(cuts) == 4 and i == 1
            g.append((cuts[i], cuts[i + 1], "touch", dict(side="L", to=hand_L, end="palm",
                                                          palm="down" if down else (0.0, 0.2, 1.0),
                                                          fingers="open", look=False, lean=0.25, ease=0.3)))
    if HELD:
        g.append((HELD[0] - 0.5, HELD[1] + 0.57, "look_up", dict(amount=14.0, ease=0.6)))
    if HEART:
        g.append((HEART_T[0] - 0.52, HEART[1] + 0.33, "look_up", dict(amount=10.0, ease=0.4)))
    return g


def _bodies():
    if _BODIES:
        return _BODIES
    from p3d.body import Body
    c = COND_C
    _BODIES["cond"] = Body(
        "man", height=HEIGHT, at=(c[0], c[2]), facing=FACING, motion="stand", gesture=_gestures(),
        garment="coat", look=LOOK, color="#ffd49a", color2="#fff4e2", points=90000, bright=BODY_BRIGHT,
        size=1.35, light=LIGHT_AT, show=SHOW, fade=0.2, seed=8.0)
    return _BODIES


def _breath_quiet(t):
    return BREATH is not None and BREATH[0] - 1.0 < t < BREATH[1]


class Gate:
    """A body seen only where he is seen."""
    wants_camera = True

    def __init__(self, body):
        self.b = body

    def sample(self, t, cam=None):
        if dance_k(t) <= 0.0:
            return []
        return self.b.sample(t, cam)

    def gain(self, t):
        quiet = 1.0 - (0.22 * _env(t, BREATH[0], BREATH[1], 0.4, 0.3) if BREATH else 0.0)   # the breath rests calmer
        return self.b.gain(t) * dance_k(t) * quiet


# =========================================================================================================
# A ribbon of light (the baton's trail): a band that follows its head back in time
# =========================================================================================================
def _deep(hexs, k=1.3):
    c = lin(hexs)
    return np.clip(c * k - 0.15 * c.mean(), 0.0, 1.0)


class Ribbon:
    def __init__(self, head, hand, color, win, trail=1.2, width=0.16, n=70, seed=0, flick=None, sparks=160):
        self.head, self.hand, self.color, self.win = head, hand, color, win
        self.trail, self.width, self.n = trail, width, n
        r = np.random.default_rng(300 + seed)
        self.sp = r.random((sparks, 4))
        self.flick = flick

    def k(self, t):
        return max(_env(t, a, b, 0.25, 0.2) for a, b in self.win) * dance_k(t)

    def points(self, t):
        u = np.linspace(0.0, 1.0, self.n)
        P = np.array([self.head(t - self.trail * x) for x in u])
        if self.hand is not None:
            h = self.hand(t)
            m = 12
            g = np.linspace(0.0, 1.0, m + 2)[1:-1, None]
            sag = _v(0.0, -0.12, 0.0) * np.sin(np.pi * g)
            tie = h[None, :] * (1.0 - g) + P[0][None, :] * g + sag
            P = np.concatenate([P[::-1], tie[::-1], h[None, :]])[::-1]
            v = np.concatenate([np.zeros(m + 1), u])
        else:
            v = u
        return P, v

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0:
            return None
        P, v = self.points(t)
        c = lin(self.color)
        deep = _deep(self.color)
        core = 0.5 * c + 0.5 * lin(WHITE)
        pulse = 1.0 + 0.35 * beat_pulse(t) * intensity(t) + 0.6 * hit_pulse(t, KICKS, fall=0.4)
        kk = 1.0 - v
        w = self.width
        out = [ribbon(P, width=w * 2.2 * (0.15 + 0.85 * kk), color=c, alpha=k * 0.16 * np.clip(kk * 1.4, 0, 1),
                      emit=1.4, dof=0.2),
               ribbon(P, width=w * (0.15 + 0.85 * kk), color=deep, alpha=k * 0.7 * np.clip(kk * 1.4, 0, 1),
                      emit=2.0, dof=0.2),
               ribbon(P, width=w * 0.16 * (0.15 + 0.85 * kk), color=core, alpha=k * 0.95 * np.clip(kk * 1.6, 0, 1),
                      emit=2.6 * pulse, dof=0.2)]
        sp = self.sp
        m = len(P)
        f = np.mod(sp[:, 0] + t * (0.8 + 0.4 * sp[:, 1]), 1.0)
        idx = np.minimum((f * (m - 1)).astype(int), m - 1)
        drift = (sp[:, 1:4] - 0.5) * (w * 3.0) * f[:, None] - _v(0.0, 0.5 * w, 0.0) * f[:, None]
        out.append(dict(pos=P[idx] + drift, size=w * (0.09 + 0.10 * sp[:, 2]), color=0.5 * c + 0.5 * core,
                        alpha=k * 0.9 * (1.0 - f) ** 1.2, emit=2.0, kind="spark", twinkle=0.6, seed=sp[:, 3]))
        return [b for b in out if b is not None]


# =========================================================================================================
# The baton (a line of light from the hand, the white-hot tip), its comets, the heart in the sky, the sea's
# ripples from his feet, his disc, the falling light, the sparks gathering into the tip
# =========================================================================================================
def _flings():
    if C.get("flings") is not None:
        return [float(x) for x in C["flings"]]
    out = []
    for h in sorted(HIT.values()):
        if any(a <= h < b for a, b in OWN) and not any(lo - 0.3 <= h <= hi for _n, lo, hi, _p in MOMENTS):
            out.append(float(h))
    return out


FLINGS = _flings()


def _tip_flare(t):
    return (1.0 + 0.8 * beat_pulse(t, 0.08) + 0.9 * hit_pulse(t, KICKS, fall=0.35) + 0.8 * _mf("brass", t)
            + 1.4 * hit_pulse(t, STRINGS + FLINGS, fall=0.3))


class Baton:
    def sample(self, t):
        k = dance_k(t)
        if k <= 0.0:
            return None
        a, b = hand_R(t), tip(t)
        fl = _tip_flare(t)
        quiet = 0.6 if _breath_quiet(t) else 1.0
        return [dict(pos=a[None], pos2=b[None], size=0.010, color=lin(TIP_COL) * 1.6, alpha=1.0, emit=2.6,
                     kind="line", dof=0.3),
                dict(pos=b[None], size=0.03 + 0.012 * fl, color=lin(WHITE), alpha=1.0, emit=4.0 * min(fl, 2.5) * quiet,
                     kind="spark"),
                dict(pos=b[None], size=0.10 + 0.05 * fl, color=lin(GOLD2), alpha=0.12 * quiet, kind="soft",
                     emit=2.0)]


class CondComet(Comet):
    """A comet that leaves the baton tip at ts (before that its trail is the tip's own path)."""

    def __init__(self, ts, fly, color, t1, src=None, **kw):
        self.ts, self.fly, self.src = float(ts), fly, (src or tip)
        super().__init__(self._head, color, ts, t1, **kw)

    def _head(self, t):
        if t <= self.ts:
            return self.src(t)
        return self.fly(t - self.ts, self.src(self.ts))

    def k(self, t):
        return super().k(t) * dance_k(t)


BRAID_AXIS = _D(-0.4, 0.0, -14.0)          # the braid climbs round this upright line, before him
BRAID_TOP = ((SUMMONS[1] - 0.05) if SUMMONS else 0.0, 15.0)   # every strand reaches the crown as his arms go up


def rainbow(t):
    """The nine colours flowing one into the next along a trail, a colour every half beat (linear rgb)."""
    x = t / 0.5
    k = int(np.floor(x))
    f = x - k
    return lin(COL9[k % 9]) * (1.0 - f) + lin(COL9[(k + 1) % 9]) * f


class Stream:
    """A stream of coloured light like the promo's (Song 11 round 9, Anthony: "It looks like he is shooting
    glowing balls of light. I don't want that ... more dramatic like the lights of color from the promo video"):
    a long thin neon line, a white-hot core inside a coloured glow, fizzing with fine sparks along its length,
    that follows its head back in time and sweeps and curves with his gestures. No ball at the head, only a
    bright point. head(t) -> position; launch ts with fly(u, p0) as CondComet (before ts the stream is the tip's
    own path); color: a hex colour or a function of time (the colour each part of the trail had when drawn)."""

    def __init__(self, head, color, win, trail=1.6, width=0.16, n=160, seed=0, fly=None, ts=None, src=None,
                 fade=0.2, bright=1.0, fizz=260):
        self.src = src or head
        self.fly, self.ts = fly, ts
        self.color, self.win, self.trail, self.width, self.n = color, win, float(trail), float(width), n
        self.fade, self.bright = float(fade), float(bright)
        self.sp = np.random.default_rng(500 + seed).random((fizz, 4))

    def head(self, t):
        if self.fly is None or t <= self.ts:
            return self.src(t)
        return self.fly(t - self.ts, self.src(self.ts))

    def k(self, t):
        if not self.win:
            return 0.0
        return max(_env(t, a, b, self.fade, self.fade) for a, b in self.win) * dance_k(t)

    def sample(self, t):
        k = self.k(t)
        if k <= 0.0:
            return None
        u = np.linspace(0.0, 1.0, self.n)
        tt = t - self.trail * u
        tt[1:] = np.round(tt[1:] * 480.0) / 480.0     # the trail on a fine time grid: shared between frames and streams
        P = np.array([self.head(x) for x in tt])
        if callable(self.color):
            Cc = np.array([self.color(x) for x in tt])
        else:
            Cc = np.repeat(lin(self.color)[None], self.n, 0)
        Cc = np.clip(Cc * 1.25 - 0.12 * Cc.mean(1, keepdims=True), 0.0, None)        # deep, saturated colour
        pulse = (1.0 + 0.35 * beat_pulse(t) * intensity(t) + 0.5 * hit_pulse(t, KICKS, fall=0.4)
                 + 0.7 * _mf("strings", t))        # the strings run as light along his streams
        fall = (1.0 - u) ** 0.9
        taper = 0.25 + 0.75 * (1.0 - u) ** 0.5
        w = self.width
        core = 0.35 * Cc + 0.65 * lin(WHITE)
        out = [ribbon(P, width=w * 3.2 * taper, color=Cc, alpha=k * 0.10 * fall * self.bright, emit=1.6, dof=0.2),
               ribbon(P, width=w * taper, color=Cc, alpha=k * 0.55 * fall * self.bright, emit=2.2, dof=0.2),
               ribbon(P, width=w * 0.22 * taper, color=core, alpha=k * 0.95 * fall, emit=3.0 * pulse * self.bright,
                      dof=0.2)]
        sp = self.sp                                    # the fizz: fine sparks crackling off the line
        idx = np.minimum((sp[:, 0] ** 1.4 * (self.n - 1)).astype(int), self.n - 1)
        off = (sp[:, 1:4] - 0.5) * w * (1.5 + 5.0 * u[idx, None])
        out.append(dict(pos=P[idx] + off, size=w * (0.10 + 0.12 * sp[:, 2]), color=0.6 * Cc[idx] + 0.4 * lin(WHITE),
                        alpha=k * 0.9 * (1.0 - u[idx]) ** 1.3, emit=2.4, kind="spark", twinkle=0.9, seed=sp[:, 3]))
        out.append(dict(pos=P[:1], size=w * 0.9, color=lin(WHITE), alpha=k, emit=3.5 * pulse, kind="spark"))
        return [b for b in out if b is not None]


SWEEP_ANCHOR = R_CEN + np.array([0.0, 0.30, 0.40])     # the middle of his baton's pattern (his frame)


def _sweep(gain, lag, lift=0.35):
    """A head that draws his baton's strokes huge in the air round him: the tip's motion about the middle of
    its pattern, scaled up by gain (a 30 cm stroke becomes a 2 to 3 m arc of light), a moment behind the tip."""
    anc = _W(SWEEP_ANCHOR)

    def f(t):
        p = tip(t - lag)
        return anc + (p - anc) * gain + _v(0.0, lift * (gain - 1.0), 0.0)
    return f


def _rainbow_from(off):
    return lambda t: rainbow(t + off)


def _braid(i, n, ts):
    """The summons: comet i of n leaves the tip on its beat (ts) and joins the rope at its own strand. All the
    strands turn together round one axis (evenly spaced in angle) and the later ones climb faster, so their
    trails wind round each other into one braided rope that reaches its crown on the last beat."""
    a0 = 2.0 * np.pi * i / n
    dur = max(BRAID_TOP[0] - ts, 0.05)
    t_ref = SUMMONS[0] - 0.15

    def f(u, p0):
        t = ts + u
        q = u / dur
        y = 1.2 + (BRAID_TOP[1] - 1.2) * q ** 1.25
        r = 1.6 * (1.0 - 0.45 * min(q, 1.0) ** 2) + 0.2
        a = a0 + 4.6 * (t - t_ref)
        sp = BRAID_AXIS + _v(r * np.sin(a), y, r * np.cos(a))
        w = _sc(0.0, 0.32, u)
        lead = p0 + _R(0.0, 2.5 * u, -12.0 * u)
        return lead * (1.0 - w) + sp * w
    return f


def _string_shot(side):
    """A comet flicked off the tip, out over the sea before him, arcing up."""
    def f(u, p0):
        return p0 + _R(side * 3.5 * u, 9.0 * u - 1.5 * u * u, -40.0 * u)
    return f


def _final_rise(u, p0):
    """The held breath: on the final rise the comet flies straight up and on into the sky."""
    return p0 + _R(-0.6 * u, 26.0 * u * (0.35 + u), 3.0 * u)


SKY_HEART_C = _D(-0.20, 17.67, 25.96)     # in the sky above the phrase, as the heart framing sees it
SKY_HEART_S = 2.56
_HX = _unit(_R(-0.9981, 0.0, 0.0619))       # the heart's plane faces the camera of the heart framing


def _sky_heart_point(s, side):
    x, y = _heart_xy(s)
    return SKY_HEART_C + _HX * (side * x * SKY_HEART_S) + _v(0.0, y * SKY_HEART_S, 0.0)


HEART_EYE = _D(2.95, 0.43, -7.3)          # where the heart framing's camera stands (the comets fly in its view)


def _azel(d):
    d = _local(d)                           # (in Song 11's frame, so any facing interpolates the same way)
    return np.arctan2(d[0], -d[2]), np.arctan2(d[1], np.hypot(d[0], d[2])), float(np.linalg.norm(d))


def _heart_fly(side):
    """The heart: the comet leaves the hand at the hit, rises straight up beside him (as the camera sees it),
    turns over above the phrase and draws its half of the heart huge in the sky; it never crosses the phrase."""
    def f(u, p0):
        t = HEART_T[0] + u
        hp = _sky_heart_point(_heart_prog(t), side)
        a0, e0, r0 = _azel(p0 - HEART_EYE)
        a1, e1, r1 = _azel(hp - HEART_EYE)
        wy = _sc(0.0, 0.16, u)
        wh = _sc(0.07, 0.30, u)
        a, e, r = a0 + (a1 - a0) * wh, e0 + (e1 - e0) * wy, r0 + (r1 - r0) * wh
        return HEART_EYE + r * _R(np.cos(e) * np.sin(a), np.sin(e), -np.cos(e) * np.cos(a))
    return f


class SkyHeart:
    """The heart of light that stays where the comets drew it, beating with the music."""

    def __init__(self):
        s = np.linspace(0.0, 1.0, 300)
        self.P = np.concatenate([np.array([_sky_heart_point(x, sd) for x in s]) for sd in (-1.0, 1.0)])
        tb = np.array([HEART_T[0] + self._inv(x) for x in s])
        self.birth = np.concatenate([tb, tb])
        self.col = np.concatenate([np.repeat(lin(PW.COLORS["Inclusiveness"])[None, :], len(s), 0),
                                   np.repeat(lin(PW.COLORS["Gratitude"])[None, :], len(s), 0)])
        self.sd = np.random.default_rng(31).random(len(self.P))

    @staticmethod
    def _inv(s):
        ts = np.linspace(HEART_T[0], HEART_T[1], 400)
        pr = np.array([_heart_prog(x) for x in ts])
        return float(np.interp(s, pr, ts - HEART_T[0]))

    def sample(self, t):
        k = _env(t, HEART_T[0], HEART[1], 0.05, 0.15) * dance_k(t)
        if k <= 0.0:
            return None
        on = self.birth <= t
        if not on.any():
            return None
        beat = 1.0 + 0.5 * beat_pulse(t, 0.12) + 0.5 * hit_pulse(t, [HEART_HIT], fall=0.6) + 0.4 * downbeat(t)
        grow = 1.0 + 0.05 * beat_pulse(t, 0.12)
        P = SKY_HEART_C + (self.P[on] - SKY_HEART_C) * grow
        age = t - self.birth[on]
        fl = 1.0 + 2.0 * np.exp(-age / 0.25)
        col = self.col[on] * 0.55 + lin(WHITE) * 0.45
        out = [dict(pos=P, size=0.10 * fl, color=col, alpha=k * np.minimum(1.0, 0.8 * fl), emit=3.0 * beat,
                    kind="spark", twinkle=0.4, seed=self.sd[on]),
               dict(pos=P[::5], size=1.4, color=self.col[on][::5], alpha=0.08 * k * beat, kind="soft", emit=1.6)]
        full = _sc(HEART_T[1] - 0.1, HEART_T[1] + 0.25, t)
        if full > 0.0:                         # the whole heart glows from within once it is closed
            out.append(dict(pos=SKY_HEART_C[None, :] + _v(0.0, -0.6, 0.0), size=9.0, color=lin(ROSE),
                            alpha=0.07 * full * k * beat, kind="soft", emit=1.5))
        return out


def _ripple_times():
    """Rings from his feet: each downbeat where he is seen (stronger in the summons and the heart, softer in the
    breath and the hold), the heart's hit, the timpani in the moments, the strings pulses and the flings."""
    special = {"ring": 1.0, "breath": 0.45, "strings": 0.45, "heart": 1.0, "held": 0.5}
    out = []
    for a, b in SEEN:
        for d in down_times(max(a, 0.0) - 1.9, min(b, LIVE)):
            s = 0.6
            for name, w in WINDOWS.items():
                if w[0] - 1.9 <= d < w[1]:
                    s = special[name]
            out.append((d, s))
    if HEART_HIT is not None:
        out.append((HEART_HIT, 0.9))
    for th, st in _timp_hits(0.5):              # the timpani: a ring runs out across the sea from his feet
        if any(a - 0.6 <= th <= b for a, b in WINDOWS.values()):
            out.append((th, 0.5 + 0.5 * st))
    out += [(x, 0.7) for x in STRINGS + FLINGS]
    return sorted(out)


class SeaRipple:
    """Rings of light running out across the sea from his feet on each of his downbeats."""

    def __init__(self):
        self.ang = np.linspace(0.0, 2.0 * np.pi, 540, endpoint=False)
        self.sd = np.random.default_rng(91).random(540)
        self.hits = None

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        if self.hits is None:
            self.hits = _ripple_times()
        out = []
        for th, s in self.hits:
            u = t - th
            if not (0.0 <= u < 1.8) or shot_of(th) != shot_of(t):
                continue
            rad = 0.8 + 16.0 * (1.0 - np.exp(-u / 0.7))
            P = np.stack([COND_C[0] + rad * np.sin(self.ang), np.full(len(self.ang), 0.03),
                          COND_C[2] + rad * np.cos(self.ang)], 1)
            a = s * np.exp(-u / 0.55) * (1.0 - _sc(1.3, 1.8, u))
            out.append(dict(pos=P, size=0.05 + 0.006 * rad, color=lin(GOLD2) * 0.6 + lin(CRYSTAL) * 0.4,
                            alpha=0.55 * a, kind="spark", emit=2.4, seed=self.sd, twinkle=0.3, reflect=False))
            out.append(dict(pos=P[::6], size=0.6 + 0.05 * rad, color=lin("#c8b8ff"), alpha=0.05 * a, kind="soft",
                            emit=1.3, reflect=False))
        return out or None


class Disc:
    """The disc of light he stands on: it flares on his downbeats."""

    def __init__(self):
        r = np.random.default_rng(17)
        n = 900
        a = r.random(n) * 2.0 * np.pi
        rr = 1.05 * np.sqrt(r.random(n))
        self.P = COND_C + np.stack([rr * np.sin(a), np.full(n, 0.02), rr * np.cos(a)], 1)
        ang = np.linspace(0, 2 * np.pi, 220, endpoint=False)
        self.R = COND_C + np.stack([1.1 * np.sin(ang), np.full(220, 0.03), 1.1 * np.cos(ang)], 1)
        self.sd = r.random(n)

    def sample(self, t):
        k = dance_k(t)
        if k <= 0.0:
            return None
        d = 1.0 + 1.2 * downbeat(t) + 0.4 * beat_pulse(t)
        q = 0.6 if _breath_quiet(t) else 1.0
        return [dict(pos=self.P, size=0.022, color=lin(GOLD2), alpha=0.5 * q, emit=1.6 * d, kind="spark",
                     twinkle=0.6, seed=self.sd, reflect=False),
                dict(pos=self.R, size=0.03, color=lin(WHITE), alpha=0.8 * q, emit=2.2 * d, kind="spark",
                     reflect=False),
                dict(pos=COND_C[None] + _v(0.0, 0.05, 0.0), size=3.0, color=lin(GOLD), alpha=0.10 * q * d,
                     kind="soft", emit=1.4, reflect=False)]


class Snow:
    """Light falling like snow round him in the breath, a breath brighter on his downbeats, and sparks
    gathering into the baton tip in the held breath."""

    def __init__(self):
        r = np.random.default_rng(77)
        self.s = r.random((1000, 5))
        self.g = np.random.default_rng(78).random((420, 5))

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        s = self.s
        out = []
        kb = _env(t, BREATH[0], BREATH[1] + 0.58, 0.4, 0.6) if BREATH else 0.0
        if kb > 0.0:
            y = 7.0 - np.mod(t * (0.22 + 0.22 * s[:, 2]) + 7.0 * s[:, 3], 7.0)
            x = -8.0 + 16.0 * s[:, 0] + 0.3 * np.sin(t * 0.7 + 6.0 * s[:, 4])
            z = -9.0 + 15.0 * s[:, 1]
            g = 1.0 + 0.7 * downbeat(t, 0.5) + 0.3 * beat_pulse(t, 0.12)
            P = DANCE_C + x[:, None] * (-LEFT) + y[:, None] * UP + z[:, None] * (-FWD)
            out.append(dict(pos=P, size=0.016 + 0.02 * s[:, 4], color=lin("#fff1d8"),
                            alpha=0.7 * kb, emit=1.8 * g, kind="spark", twinkle=0.5, seed=s[:, 4], dof=0.6))
        kh = _env(t, HELD[0], RISE - 0.02, 0.3, 0.1) if HELD else 0.0
        if kh > 0.0:                          # sparks from all round gathering into the poised baton's tip
            c = tip(min(t, RISE - 0.22))
            s = self.g
            u = np.clip((t - HELD[0] - 1.1 * s[:, 0]) / 0.9, 0.0, 1.0)
            u = u * u * (3.0 - 2.0 * u)
            d = np.stack([s[:, 1] - 0.5, 0.7 * (s[:, 2] - 0.4), s[:, 3] - 0.5], 1)
            d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
            P = c[None, :] + d * (0.8 + 2.4 * s[:, 4:5]) * (1.0 - u)[:, None]
            col = np.array([lin(COL9[int(x * 9) % 9]) for x in s[:, 0]]) * 0.5 + lin(WHITE) * 0.5
            out.append(dict(pos=P, size=0.006 + 0.008 * s[:, 4], color=col, alpha=kh * 0.9 * (1.0 - u) ** 0.7,
                            emit=2.2, kind="spark", twinkle=0.6, seed=s[:, 4], dof=0.0))
        return out or None


class Halo:
    """A soft glow round him: a figure of light from afar, a silhouette against the light behind."""

    def __init__(self, name, color):
        self.name, self.col = name, lin(color)

    def sample(self, t):
        b = _bodies()[self.name]
        if dance_k(t) <= 0.0 or not (b.show[0] < t < b.show[1]):
            return None
        k = b.gain(t) * (1.0 + 0.3 * beat_pulse(t) * intensity(t) + 0.3 * _mf("choir", t))
        c = b.where(t, "chest")
        p = np.stack([c, 0.5 * (c + b.where(t, "pelvis")), b.where(t, "knee.L") * 0.5 + b.where(t, "knee.R") * 0.5])
        return [dict(pos=p, size=np.array([1.4, 1.3, 1.1]), color=self.col, alpha=0.035 * k, kind="soft", emit=1.5)]


class BackLight:
    """The blazing light he stands against (a great soft glow behind him as the camera sees him)."""

    def __init__(self, spots):
        self.spots = spots                      # (t0, t1, place, size, colour, strength fn)

    def sample(self, t):
        if dance_k(t) <= 0.0:
            return None
        out = []
        for a, b, p, sz, col, f in self.spots:
            if a <= t <= b:
                k = float(f(t)) * (1.0 + 0.6 * _mf("brass", t))     # the brass flares the light behind him
                if k > 0.0:
                    out.append(dict(pos=p[None], size=sz, color=lin(col), alpha=0.10 * k, kind="soft", emit=1.5,
                                    reflect=False))
                    out.append(dict(pos=p[None], size=sz * 0.3, color=lin(WHITE), alpha=0.12 * k, kind="soft",
                                    emit=2.0, reflect=False))
        return out or None


RING_COL = [COL9[k] for k in (0, 2, 4, 6, 8, 1, 3)]


# =========================================================================================================
# Keeping his light out of the words (Song 11's BoxGuard, tools/s11_full2/s11_stage.py, reading the kit's phrases)
# =========================================================================================================
WORD_BOX = (0.15, 0.85, 0.52, 0.75)     # x0, x1, y0, y1 of the words on screen (0..1, y up)
CORNER_BOX = (-0.05, 0.42, -0.05, 0.14)  # the logo and the periodic titles, bottom left


def phrase_k(t):
    """0..1, eased: how much a phrase is reading at t (in 0.3 s before the words arrive, out 0.3 s after)."""
    k = 0.0
    for _l, (ti, _r0, _r1, to), *_x in getattr(H, "PHRASE_LIST", []):
        if ti - 0.8 <= t <= to + 0.8:
            k = max(k, _sc(ti - 0.7, ti - 0.3, t) * (1.0 - _sc(to + 0.3, to + 0.7, t)))
    return k


def corner_k(t):
    """0..1 while the corner titles show beside the logo (SIG_TEXT windows)."""
    k = 0.0
    for a, b in getattr(H, "SIG_TEXT", []):
        if a - 0.6 <= t <= b + 0.6:
            k = max(k, _sc(a - 0.6, a, t) * (1.0 - _sc(b, b + 0.6, t)))
    return k


class BoxGuard:
    """Keeps a point set's light out of a screen box while `when` says (default: a phrase reads)."""
    wants_camera = True

    def __init__(self, ps, keep=0.06, box=WORD_BOX, when=None):
        self.ps, self.keep, self.box = ps, keep, box
        self.when = when or phrase_k
        self.inner_camera = bool(getattr(ps, "wants_camera", False))
        if hasattr(ps, "gain"):
            self.gain = ps.gain

    def _fade(self, cam, P, size):
        xy, z = cam.project(P)
        fl = 1.0 / np.tan(np.radians(cam.fov) * 0.5)
        r = 0.5 * np.asarray(size, np.float64) * fl / np.maximum(z, 0.05)      # glow radius, screen heights
        x0, x1, y0, y1 = self.box
        dx = np.minimum(xy[:, 0] - x0, x1 - xy[:, 0]) * cam.aspect
        dy = np.minimum(xy[:, 1] - y0, y1 - xy[:, 1])
        d = np.minimum(dx, dy) + r                       # > 0: the glow reaches into the box
        return np.clip(d / 0.06 + 0.5, 0.0, 1.0) * (z > 0.0)

    def sample(self, t, cam=None):
        out = self.ps.sample(t, cam) if self.inner_camera else self.ps.sample(t)
        k = self.when(t)
        if not out or cam is None or k <= 0.0:
            return out
        one = isinstance(out, dict)
        res = []
        for b in ([out] if one else out):
            if b is None or "pos" not in b or len(b["pos"]) == 0:
                res.append(b)
                continue
            b = dict(b)
            P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            size = b.get("size", 0.0)
            f = self._fade(cam, P, size)
            if "pos2" in b:
                P2 = np.asarray(b["pos2"], np.float64).reshape(-1, 3)
                f = np.maximum(f, self._fade(cam, P2, size))
                f = np.maximum(f, self._fade(cam, 0.5 * (P + P2), size))
            a = np.broadcast_to(np.asarray(b.get("alpha", 1.0), np.float64), (len(P),))
            b["alpha"] = a * (1.0 - (1.0 - self.keep) * k * f)
            res.append(b)
        return res[0] if one else res


def _wrap(scene, name, f):
    """The world answers him: another set's gain multiplied by f(t) while he conducts (1 elsewhere)."""
    try:
        ps = scene.get(name)
    except KeyError:
        return
    g0 = ps.gain if hasattr(ps, "gain") else (lambda t: 1.0)
    ps.gain = lambda t, g0=g0: float(g0(t)) * (f(t) if dance_k(t) > 0.0 else 1.0)


def _swell_amt(t):
    calm = _breath_quiet(t) or (HELD is not None and HELD[0] - 0.5 < t < RISE - 0.12)
    return 0.25 if calm else 0.55


def _subtract(spans, cuts):
    """spans minus the cut ranges."""
    out = list(spans)
    for lo, hi in cuts:
        nxt = []
        for a, b in out:
            if hi <= a or lo >= b:
                nxt.append((a, b))
                continue
            if a < lo:
                nxt.append((a, lo))
            if hi < b:
                nxt.append((hi, b))
        out = nxt
    return [(a, b) for a, b in out if b - a > 0.3]


def add(scene):
    b = _bodies()
    scene.add("conductor of light", Gate(b["cond"]))
    scene.add("conductor halo", Halo("cond", "#ffd9a0"))
    scene.add("conductor disc", Disc())
    scene.add("conductor baton", Baton())
    # plain conducting: the baton draws a soft stream of the nine colours on every stroke
    plain = _subtract(SEEN, [(lo, hi) for _n, lo, hi, _p in MOMENTS])
    if plain:
        scene.add("conductor stream beat", BoxGuard(Stream(tip, rainbow, plain, trail=1.0, width=0.07, seed=7,
                                                           bright=0.75, fade=0.4), keep=0.1))
    # the baton draws streams of coloured light (no balls): the nine colours along a long trail in the strokes,
    # a soft lavender line in the breath and the hold, gratitude in the strings
    strokes = [w for w in (SUMMONS, HEART) if w]
    if strokes:
        scene.add("conductor stream strokes", Stream(tip, rainbow, strokes, trail=1.1, width=0.09, seed=1))
    if HEART:
        scene.add("conductor stream left", Stream(tip_L, rainbow, [HEART], trail=0.9, width=0.07, seed=5,
                                                  bright=0.8))
    hush = [w for w in (BREATH, HELD) if w]
    if hush:
        scene.add("conductor stream breath", Stream(tip, LAV, hush, trail=1.8, width=0.07, seed=2, bright=0.8))
    if STRINGS_W:
        scene.add("conductor stream strings", Stream(tip, PW.COLORS["Gratitude"], [STRINGS_W], trail=0.9,
                                                     width=0.08, seed=3))
    # the great sweeps: his strokes drawn huge round him in long streams of the nine colours (the promo's
    # lights of colour); kept out of the words while a phrase reads
    LOWER_THIRD = (-0.05, 1.05, -0.05, 0.36)
    sweeps = []
    if SUMMONS:
        sweeps.append((0, (SUMMONS[0] - 0.1, SUMMONS[1] + 0.05), (2.4, 0.06), (3.2, 0.14), (4.0, 0.22)))
    if STRINGS_W:
        sweeps.append((1, STRINGS_W, (3.5, 0.05), (5.5, 0.12), (7.5, 0.20)))
    if HEART:
        sweeps.append((2, HEART, (2.6, 0.06), (3.6, 0.12), (4.6, 0.18)))
    for j, win, *arms in sweeps:
        for i, (gain, lag) in enumerate(arms):
            sm = j == 0                          # the summons: thinner, softer, climbing above his head
            st = Stream(_sweep(gain, lag, lift=1.1 if sm else 0.35), _rainbow_from(1.5 * i), [win],
                        trail=1.3 + 0.2 * i, width=(0.08 + 0.03 * i) if sm else (0.16 + 0.06 * i), fade=0.25,
                        bright=0.55 if sm else 1.1, seed=600 + 10 * j + i)
            corner = BoxGuard(st, keep=0.1, box=CORNER_BOX, when=corner_k)     # off the corner titles too
            if sm:                               # the lower third stays clear: he is the bright figure there
                corner = BoxGuard(corner, keep=0.08, box=LOWER_THIRD, when=lambda t: 1.0)
            scene.add("conductor sweep %d %d" % (j, i), BoxGuard(corner, keep=0.0))
    # the summons: a stream off the tip on each beat, the four winding into one braided rope to the sky
    if SUMMONS:
        bt = beat_times(SUMMONS[0] - 0.15, SUMMONS[1] - 0.2)[:4]
        for i, ts in enumerate(bt):
            scene.add("conductor stream summons %d" % i, Stream(tip, RING_COL[(2 * i) % 7], [(ts, SUMMONS[1] + 0.05)],
                                                                trail=2.2, width=0.13, bright=0.6,
                                                                fly=_braid(i, len(bt), ts), ts=ts, fade=0.1,
                                                                seed=400 + i))
    # the strings pulses and the flings: a stream flicked off over the sea on each
    for i, ts in enumerate(STRINGS + FLINGS):
        scene.add("conductor stream flick %d" % i, Stream(tip, COL9[(5 + 3 * i) % 9], [(ts + 0.03, ts + 2.6)],
                                                          trail=1.8, width=0.24, fly=_string_shot(1.0 - 2.0 * (i % 2)),
                                                          ts=ts + 0.03, fade=0.15, seed=410 + i))
    # wondrous love: two streams (the baton tip and the left fingertips) draw the heart huge in the sky
    if HEART:
        scene.add("conductor stream heart R", Stream(tip, PW.COLORS["Gratitude"], [(HEART_T[0], HEART[1] + 0.13)],
                                                     trail=1.4, width=0.16, fly=_heart_fly(1.0), ts=HEART_T[0],
                                                     fade=0.1, bright=0.85, seed=420))
        scene.add("conductor stream heart L", Stream(tip_L, PW.COLORS["Inclusiveness"],
                                                     [(HEART_T[0], HEART[1] + 0.13)], trail=1.4, width=0.16,
                                                     fly=_heart_fly(-1.0), ts=HEART_T[0], fade=0.1, bright=0.85,
                                                     seed=421))
        scene.add("conductor sky heart", SkyHeart())
    # the held breath: on the final rise the comet flies up and on
    if HELD:
        scene.add("conductor stream final", Stream(tip, rainbow, [(RISE - 0.52, RISE + 0.78)], trail=2.0, width=0.26,
                                                   fly=_final_rise, ts=RISE, fade=0.12, seed=430))
    scene.add("conductor ripples", SeaRipple(), reflect=False)
    if BREATH or HELD:
        scene.add("conductor snow", Snow())
    spots = []
    if SUMMONS:
        a, e = SUMMONS
        spots.append((a - 0.7, e + 0.2, _D(0.0, 26.0, -60.0), 44.0, "#c98cff",
                      lambda t, e=e: 0.40 + 0.35 * downbeat(t, 0.4) + 0.6 * _sc(e - 0.4, e - 0.05, t)))
    if BREATH:
        spots.append((BREATH[0] - 0.5, BREATH[1] + 0.08, _D(0.0, 6.0, -70.0), 34.0, "#e8d8ff",
                      lambda t: 0.3 + 0.2 * downbeat(t, 0.5)))
    if STRINGS_W:
        spots.append((STRINGS_W[0] - 0.02, STRINGS_W[1] + 0.08, _D(-8.0, 10.0, -70.0), 44.0, "#ff9ec8",
                      lambda t: 0.50 + 0.3 * upbeat(t) + 0.35 * downbeat(t, 0.4)))
    if HEART:
        spots.append((HEART[0] - 0.42, HEART[1] + 0.13, _D(-22.3, 8.7, 55.3), 18.0, "#ffd8c8",
                      lambda t: 0.4 + 0.3 * upbeat(t)))
    if HELD:
        spots.append((HELD[0] - 0.5, HELD[1] + 0.17, _D(-1.0, 7.0, 40.0), 34.0, "#fff0dc",
                      lambda t: 0.45 + 0.35 * _sc(HELD[0], RISE - 0.12, t) + 0.8 * _sc(RISE - 0.12, RISE + 0.28, t)))
    if spots:
        scene.add("conductor backlight", BackLight(spots))
    # the light he carries and the rays that open when he raises both arms
    add_light(tip, TIP_COL, lambda t: 0.10 * dance_k(t) * (0.8 + 0.4 * beat_pulse(t)) * _tip_flare(t) / 2.0, radius=3.5)
    if SUMMONS or HELD:
        def ray_pos(t):
            if HELD and (not SUMMONS or abs(t - RISE) < abs(t - SUMMONS[1])):
                return _D(-1.0, 9.0, 40.0)
            return _D(0.0, 30.0, -70.0)

        def ray_k(t):
            v = 0.0
            if SUMMONS:
                e = SUMMONS[1]
                v += 0.9 * _sc(e - 0.4, e - 0.1, t) * (1.0 - _sc(e + 0.1, e + 0.3, t))
            if HELD:
                v += 0.95 * _sc(RISE - 0.07, RISE + 0.28, t) * (1.0 - _sc(RISE + 0.48, RISE + 0.78, t))
            return dance_k(t) * v
        add_rays(ray_pos, ray_k, color="#fff1d8", size=0.8)
    # the world answers him: the sets the song names swell on his upbeat; the sea glitter, the horizon clouds
    # and the constellations ripple with his downbeats
    for name in C.get("swell", []):
        _wrap(scene, name, lambda t: 1.0 + _swell_amt(t) * upbeat(t))
    for name in C.get("faint", []):
        _wrap(scene, name, lambda t: 0.2)
    for k in range(8):
        _wrap(scene, "horizon clouds %d" % k, lambda t: 1.0 + 0.8 * _swell_amt(t) * upbeat(t))
    _wrap(scene, "sea glitter", lambda t: 1.0 + 0.9 * downbeat(t, 0.3))
    _wrap(scene, "constellations", lambda t: 1.0 + 0.7 * downbeat(t, 0.45) + 0.4 * _mf("high", t))
