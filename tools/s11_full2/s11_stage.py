"""Song 11 v2: the heavenly choir (gold glitter) and the crystal orchestra on the square before the
church of light, their instruments, the light of their singing, and the snow of light in the breath.

Owned by the stage thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.

The orchestra is a real one, seated in arcs round a podium and facing the audience (+z): violins on the
audience's left, violas and cellos on the right, two concert harps at the far left (in profile, so their
frames read), trumpets, trombones and timpani on risers at the back. Every player is one Crowd instance whose
arms are posed onto their instrument (Body gestures "touch" to points of the instrument), all at one height
(PLAY_H) so one drawing of each instrument fits every player. The players' loops are locked to the beat
(Players below): the bows are drawn on the beat, the timpani strike on it. The instruments are drawn in light
in the same frame as the players (local: feet at the origin, facing +z, the player's left is +x).
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
from p3d.api import Mask

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

def _S(name, t0, t1, fov, keys, ap=0.02, focus=None, **kw):
    """One shot of the edit: keys are (fraction of the block, camera place, target); the core paces the move
    with the music (fast on hits and loud passages)."""
    d = dict(name=name, kind="stage", t0=t0, t1=t1, fov=fov, aperture=ap,
             keys=[(t0 + f * (t1 - t0), p, q) for f, p, q in keys], **kw)
    if focus is not None:
        d["focus"] = focus
    return d


def _P(x, h, z):
    """A place on the stage: x across, h above the summit, z in front of the church's middle front."""
    return _v(x, Y + h, FZ + z)


# one shot per block of the core's EDIT (blocks_of("stage")), every one a different angle
SHOTS = [
    # the orchestra wakes at dawn, the choir behind: a low crane rising from the audience's floor
    _S("st_dawn", 26.33, 31.11, 46.0, [(0.0, _P(-8.0, 1.0, 40.0), _P(-1.0, 1.8, 12.0)),
                                       (1.0, _P(-5.0, 2.4, 36.0), _P(-1.0, 2.0, 12.0))], ap=0.012),
    # harps and strings over the low F pedal: close on the first harp's strings, sliding along them
    _S("st_harp", 35.9, 38.24, 40.0, [(0.0, _P(-8.4, 1.3, 27.2), _P(-9.0, 1.15, 24.1)),
                                      (1.0, _P(-9.5, 1.55, 26.7), _P(-9.1, 1.25, 24.1))], ap=0.03,
       focus=_P(-9.0, 1.2, 24.15)),
    # timpani and strings: down the centre aisle onto the kettles, the mallets falling
    _S("st_timp", 67.6, 69.4, 46.0, [(0.0, _P(0.25, 2.0, 18.6), _P(0.2, 1.3, 15.2)),
                                     (1.0, _P(0.25, 1.85, 17.6), _P(0.2, 1.35, 15.2))], ap=0.03,
       focus=_P(0.2, 1.4, 15.5)),
    # the build into slam 1, faster and faster: low up at the singers breathing in
    _S("st_build1", 77.46, 78.62, 44.0, [(0.0, _P(2.0, 1.0, 10.2), _P(0.5, 3.0, 2.5)),
                                         (1.0, _P(1.4, 1.1, 9.0), _P(0.4, 3.0, 2.5))], focus=_P(0.4, 2.0, 4.0)),
    # light gathering in the choir: close on the front row's hearts
    _S("st_build2", 78.62, 79.78, 40.0, [(0.0, _P(-1.6, 2.5, 8.0), _P(-1.0, 2.2, 3.0)),
                                         (1.0, _P(-1.2, 2.5, 6.4), _P(-1.0, 2.2, 3.0))], focus=_P(-1.0, 1.9, 4.3)),
    # the orchestra holds its breath: a fast dolly along the violins
    _S("st_build3", 79.78, 80.94, 42.0, [(0.0, _P(-10.0, 1.7, 27.5), _P(-6.0, 1.1, 20.0)),
                                         (1.0, _P(-3.5, 1.7, 27.5), _P(-1.5, 1.1, 20.0))], focus=_P(-4.0, 1.1, 21.0)),
    # the last half bar: a hard push into the choir
    _S("st_build4", 81.51, 82.08, 46.0, [(0.0, _P(0.0, 2.4, 13.5), _P(0.0, 2.7, 2.0)),
                                         (1.0, _P(0.0, 2.6, 8.0), _P(0.0, 2.7, 2.0))], focus=_P(0.0, 2.2, 4.0)),
    # SLAM 1: the whole stage from high, craning down onto it
    _S("st_slam1", 82.08, 84.4, 50.0, [(0.0, _P(0.0, 12.0, 46.0), _P(0.0, 2.0, 10.0)),
                                       (1.0, _P(0.0, 7.5, 39.0), _P(0.0, 2.6, 10.0))], ap=0.01),
    # the choir in full voice: crane over the orchestra to the choir
    _S("st_fullvoice", 84.4, 86.7, 44.0, [(0.0, _P(3.0, 6.0, 25.0), _P(0.0, 2.4, 2.5)),
                                          (1.0, _P(1.5, 4.2, 13.0), _P(0.0, 2.6, 2.5))], ap=0.015),
    # brass and strings: over a trumpeter's shoulder, past the bell, out over the orchestra
    _S("st_trumpet", 88.0, 89.3, 50.0, [(0.0, _P(-2.55, 2.55, 14.55), _P(-1.9, 2.1, 18.5)),
                                        (1.0, _P(-2.4, 2.45, 14.85), _P(-1.6, 2.05, 18.5))], ap=0.03,
       focus=_P(-2.06, 2.2, 16.1)),
    # the choir: an arc along the rows
    _S("st_choir_arc", 93.0, 95.4, 42.0, [(0.0, _P(-7.5, 2.5, 10.0), _P(-1.5, 2.4, 2.5)),
                                          (0.5, _P(-5.4, 2.5, 11.2), _P(-1.0, 2.4, 2.5)),
                                          (1.0, _P(-3.0, 2.5, 11.8), _P(-0.5, 2.4, 2.5))], ap=0.015),
    # the orchestra in full: high from the side, sweeping round
    _S("st_orch_high", 101.7, 103.6, 46.0, [(0.0, _P(15.0, 9.0, 39.0), _P(0.0, 1.5, 17.0)),
                                            (1.0, _P(9.0, 8.0, 37.5), _P(0.0, 1.5, 17.0))], ap=0.01),
    # brass and timpani blaze: low among the violas onto the trombones' bells
    _S("st_blaze1", 105.14, 106.5, 46.0, [(0.0, _P(3.2, 2.3, 21.6), _P(4.2, 2.1, 16.5)),
                                          (1.0, _P(3.0, 2.5, 20.2), _P(4.2, 2.2, 16.5))], ap=0.025,
       focus=_P(4.4, 2.1, 17.0)),
    # the breath: the choir still, light falling like snow (a slow drift)
    _S("st_snow", 117.0, 121.32, 36.0, [(0.0, _P(3.6, 2.3, 9.6), _P(0.5, 2.6, 2.5)),
                                        (1.0, _P(2.0, 2.4, 9.0), _P(0.3, 2.6, 2.5))], focus=_P(0.5, 2.0, 4.0)),
    # verse 2: the strings pulse, a low dolly along the violin section
    _S("st_strings", 121.32, 124.18, 38.0, [(0.0, _P(-8.0, 1.3, 27.6), _P(-5.5, 1.2, 21.0)),
                                            (1.0, _P(-3.6, 1.3, 27.4), _P(-2.5, 1.2, 20.5))], ap=0.025,
       focus=_P(-4.0, 1.2, 22.0)),
    # strings and harp: past a violinist's bow to the harps
    _S("st_strings_harp", 124.18, 125.92, 42.0, [(0.0, _P(-5.6, 1.5, 26.0), _P(-9.4, 1.1, 23.2)),
                                                 (1.0, _P(-6.3, 1.6, 25.4), _P(-9.6, 1.1, 23.0))], ap=0.025,
       focus=_P(-9.0, 1.2, 24.0)),
    # all kings worship You: crane up from the orchestra to the choir
    _S("st_kings", 150.4, 152.0, 44.0, [(0.0, _P(-2.0, 1.8, 12.5), _P(0.0, 2.8, 2.0)),
                                        (1.0, _P(-1.0, 4.6, 10.5), _P(0.0, 2.8, 2.0))], ap=0.015),
    # the build into slam 2: the choir draws breath
    _S("st_build5", 160.6, 161.7, 42.0, [(0.0, _P(4.2, 2.2, 10.8), _P(0.5, 2.4, 2.5)),
                                         (1.0, _P(2.4, 2.3, 8.4), _P(0.5, 2.4, 2.5))], focus=_P(0.8, 2.0, 4.0)),
    # the last half bar: a fast push to a trumpet's bell
    _S("st_build6", 162.3, 162.86, 48.0, [(0.0, _P(-3.0, 2.4, 21.5), _P(-2.06, 2.2, 16.1)),
                                          (1.0, _P(-2.2, 2.3, 18.0), _P(-2.06, 2.2, 16.1))], ap=0.03,
       focus=_P(-2.06, 2.2, 16.2)),
    # SLAM 2: low and wide from the front of the stage up at the blazing brass and timpani
    _S("st_slam2", 162.86, 165.16, 52.0, [(0.0, _P(0.0, 1.2, 29.5), _P(0.0, 3.4, 14.0)),
                                          (1.0, _P(0.0, 1.6, 26.0), _P(0.0, 3.4, 14.0))], ap=0.012),
    # the choir: along the rows from the side
    _S("st_choir_side", 167.5, 169.2, 44.0, [(0.0, _P(12.5, 3.0, 6.5), _P(0.0, 2.2, 2.5)),
                                             (1.0, _P(11.0, 3.3, 4.8), _P(0.0, 2.2, 2.5))], ap=0.015),
    # the orchestra: an arc round the conductor's podium
    _S("st_podium", 173.8, 176.1, 50.0, [(0.0, _P(3.2, 2.2, 28.2), _P(0.0, 1.2, 20.0)),
                                         (0.5, _P(0.0, 2.3, 29.6), _P(0.0, 1.2, 20.0)),
                                         (1.0, _P(-3.2, 2.2, 28.2), _P(0.0, 1.2, 20.0))], ap=0.015),
    # the brass rising: a crane up past the trombones
    _S("st_brass_rise", 183.0, 185.92, 46.0, [(0.0, _P(5.2, 1.8, 24.0), _P(4.5, 2.2, 16.5)),
                                              (1.0, _P(4.2, 4.6, 22.0), _P(4.2, 2.0, 16.5))], ap=0.02),
    # wondrous love: the trumpets and timpani blaze, from the front
    _S("st_love", 185.92, 188.27, 46.0, [(0.0, _P(-4.5, 3.6, 33.0), _P(-3.0, 2.4, 15.0)),
                                         (1.0, _P(-4.0, 3.2, 30.0), _P(-3.0, 2.4, 15.0))], ap=0.012),
    # the choir: from high above, looking down on the rows
    _S("st_choir_high", 190.6, 192.9, 44.0, [(0.0, _P(-6.0, 9.0, 12.5), _P(0.0, 1.8, 2.0)),
                                             (1.0, _P(-3.0, 8.0, 10.5), _P(0.0, 1.8, 2.0))], ap=0.012),
    # the coda hit: a fast push into the choir
    _S("st_coda_hit", 199.62, 200.7, 46.0, [(0.0, _P(0.0, 2.6, 12.5), _P(0.0, 2.7, 2.0)),
                                            (1.0, _P(0.0, 2.6, 8.4), _P(0.0, 2.7, 2.0))], focus=_P(0.0, 2.2, 4.0)),
    # the choir and orchestra in the sunrise: high and diagonal over everyone
    _S("st_sunrise", 203.9, 205.98, 50.0, [(0.0, _P(-17.0, 12.0, 40.0), _P(0.0, 2.0, 12.0)),
                                           (1.0, _P(-10.0, 10.0, 38.0), _P(0.0, 2.0, 12.0))], ap=0.01),
    # the choir: low from the right, up at the singers
    _S("st_choir_low", 210.3, 211.6, 46.0, [(0.0, _P(5.0, 1.0, 9.6), _P(1.0, 3.4, 2.0)),
                                            (1.0, _P(3.4, 1.2, 9.0), _P(0.8, 3.4, 2.0))], focus=_P(1.5, 2.0, 4.0)),
    # sacrifice: low under the trumpets' bells
    _S("st_sacrifice", 218.1, 220.2, 48.0, [(0.0, _P(-4.6, 1.8, 22.2), _P(-4.6, 2.5, 16.5)),
                                            (1.0, _P(-4.3, 2.0, 20.4), _P(-4.4, 2.5, 16.5))], ap=0.025,
       focus=_P(-4.5, 2.2, 16.8)),
    # home: Oh, the Church of God, the whole stage from the audience
    _S("st_home", 238.8, 240.19, 46.0, [(0.0, _P(-5.0, 3.2, 42.0), _P(-0.5, 3.6, 6.0)),
                                        (1.0, _P(-3.6, 3.4, 39.5), _P(-0.5, 3.6, 6.0))], ap=0.01),
    # the step down, hymn-like: a gentle arc toward the choir
    _S("st_stepdown", 240.19, 242.5, 44.0, [(0.0, _P(6.5, 3.0, 15.0), _P(0.0, 2.5, 3.0)),
                                            (1.0, _P(3.2, 3.2, 14.0), _P(0.0, 2.5, 3.0))], ap=0.015),
    # the choir: a slow push
    _S("st_home_choir", 244.8, 247.5, 42.0, [(0.0, _P(-2.6, 2.2, 11.2), _P(-0.5, 2.6, 2.5)),
                                             (1.0, _P(-1.8, 2.3, 9.6), _P(-0.5, 2.6, 2.5))], focus=_P(-0.5, 2.0, 4.0)),
    # the held breath: still, looking up past the choir to the sparks gathering above
    _S("st_held", 247.5, 249.43, 50.0, [(0.0, _P(0.0, 2.0, 16.0), _P(0.0, 6.5, 3.0)),
                                        (1.0, _P(0.0, 2.1, 15.3), _P(0.0, 6.6, 3.0))], ap=0.012, pace="linear"),
    # the final rise: a crane up and back over everyone
    _S("st_final", 249.43, 251.7, 52.0, [(0.0, _P(0.0, 2.6, 14.0), _P(0.0, 4.5, 3.0)),
                                         (1.0, _P(0.0, 9.5, 25.0), _P(0.0, 3.6, 3.0))], ap=0.01),
]

# =========================================================================================================
# The beat clock
# =========================================================================================================
_BP = float(np.median(np.diff(BEATS)))


def beat_f(t):
    """The beat count at t as a smooth number (beat k falls on BEATS[k]); frozen through the held breath."""
    if HELD[0] <= t < HELD[1]:
        t = HELD[0]
    if t <= BEATS[0]:
        return (t - BEATS[0]) / _BP
    if t >= BEATS[-1]:
        return len(BEATS) - 1 + (t - BEATS[-1]) / _BP
    i = int(np.searchsorted(BEATS, t)) - 1
    return i + (t - BEATS[i]) / max(BEATS[i + 1] - BEATS[i], 1e-3)


_RATE = np.array([2.0 if intensity(b) > 0.62 else 1.0 for b in BEATS])
_CLK = None


def _clock():
    global _CLK
    if _CLK is None:
        _CLK = np.concatenate([[0.0], np.cumsum(_RATE / 4.0)])
    return _CLK


def play_ph(t):
    """The players' loop phase (0..1): one loop is four beats in the quiet, two in loud passages (bows,
    mallets, slides and harp hands go twice as fast); frozen in the held breath."""
    c = _clock()
    bf = beat_f(t)
    i = int(np.clip(np.floor(bf), 0, len(_RATE) - 1))
    return float((c[i] + _RATE[i] / 4.0 * (bf - i)) % 1.0)


_K0 = int(np.argmin(np.abs(BEATS - SLAM1)))


def downbeat(t):
    """(seconds since the last bar's first beat, the bar's number)."""
    i = int(np.searchsorted(BEATS, t, side="right")) - 1
    if i < 0:
        return 9.0, 0
    j = i - ((i - _K0) % 4)
    return float(t - BEATS[max(j, 0)]), (j - _K0) // 4


# =========================================================================================================
# The choir: robed singers of gold glitter on the steps before the church (veiled women and men)
# =========================================================================================================
def _choir_places():
    pts = []
    for i, (yy, zz) in enumerate(CHOIR_STEPS):
        n = 21 - i
        for j in range(n):
            x = (j - (n - 1) / 2.0) * 1.08 + (0.54 if i % 2 else 0.0) * 0.5
            pts.append((x, yy, zz - 0.15))
    return np.asarray(pts, np.float64)


CHOIR_P = _choir_places()
CHOIR_H = 1.66
# the singers hold their music before them (cup), the light of their singing gathers at the heart
_SING = [("cup", dict(height=0.16, out=0.02))]
CHOIR_KINDS = [
    dict(shape="woman", height=CHOIR_H, garment="robe", veil=dict(length=1.1), hair=False, gest=_SING,
         loop=4.0, light="heart", build=1.0),
    dict(shape="woman", height=CHOIR_H - 0.04, garment="robe", veil=dict(length=0.9), hair=False, gest=_SING,
         loop=4.0, light="heart", build=0.92),
    dict(shape="man", height=CHOIR_H + 0.06, garment="robe", hair="short", gest=_SING, loop=4.0, light="heart",
         build=1.05),
    dict(shape="man", height=CHOIR_H + 0.03, garment="robe", hair="cap", gest=_SING, loop=4.0, light="heart",
         build=0.97),
]


def choir_glow(t):
    """The light inside the singers: a calm glow, gathering through the breath in (1:17.5 to 1:22), bursting
    on the slam, steady and warm in the breath, and gathering again for the last chord."""
    k = 0.35 + 0.25 * loud(t) + 0.25 * beat_pulse(t, 0.12)
    k += 1.4 * _sc(77.46, 82.0, t) ** 1.6 * (1.0 - _sc(82.1, 84.5, t))
    k += 1.2 * hit_pulse(t, [SLAM1], fall=0.8)
    k += 0.7 * _win(t, 117.0, 121.2, 0.6, 0.4)
    k += 0.9 * _sc(247.5, 249.43, t) * (1.0 - _sc(250.5, 253.0, t)) + 1.2 * hit_pulse(t, [HIT["final"], LAST_CHORD], fall=0.9)
    k += 1.1 * chorus_flare(t)
    return k


def chorus_flare(t):
    """The hearts flare on the first beat of every bar in the choruses."""
    dt, _bar = downbeat(t)
    return _sc(0.55, 0.75, intensity(t)) * float(np.exp(-dt / 0.28)) * (0.0 if HELD[0] <= t < HELD[1] else 1.0)


def bar_colour(t):
    """The bar's colour from the nine campaign colours (linear)."""
    return lin(COL9[downbeat(t)[1] % 9])


def phrase_on(t):
    """1 while a phrase is on screen (the dark silhouettes must not hide words riding 30 m out)."""
    import songs.s11_full2 as H
    for _l, (ti, _r0, _r1, to), *_x in H.PHRASE_LIST:
        if ti - 0.4 <= t <= to + 0.4:
            return 1.0
    return 0.0


CHOIR_C = _v(0.0, SUMMIT + 2.0, FACADE_Z + 2.5)
ORCH_C = _v(0.0, SUMMIT + 1.0, FACADE_Z + 20.0)


def _far(t, p):
    """0 when the camera is near p, 1 when it is far (a wide view)."""
    import songs.s11_full2 as H
    if not stage_view(t):
        return 1.0
    d = float(np.linalg.norm(np.asarray(H.CAMERA.state(t).pos, np.float64) - p))
    return _sc(15.0, 26.0, d)


def choir_mask(t):
    f = _far(t, CHOIR_C)
    k = (0.85 if t < SLAM3 else 0.45) * (1.0 - f) + (0.35 if t >= SLAM3 else 0.0) * f
    return k


def orch_mask(t):
    f = _far(t, ORCH_C)
    k = 0.45 * (1.0 - f) + (0.55 if t >= SLAM3 else 0.0) * f
    return k


class MaskSource:
    """The shape of a crowd's dark silhouette: its own points (every other one), but while a phrase is on
    screen not where the words ride (they ride 30 m out, behind near performers, and the silhouette would hide
    them); there the performers simply glow."""
    wants_camera = True
    BOX = (0.15, 0.85, 0.52, 0.75)          # x0, x1, y0, y1 of the words (0..1, y up)

    def __init__(self, crowd):
        self.c = crowd

    def sample(self, t, cam=None):
        b = self.c.body(t)
        if not b:
            return None
        b = b[0]
        sl = slice(None, None, 2)
        pos, birth = b["pos"][sl], b["birth"][sl]
        size = b["size"][sl] if np.ndim(b["size"]) else b["size"]
        keep = None
        if cam is not None and phrase_on(t):
            xy, z = cam.project(pos)
            x0, x1, y0, y1 = self.BOX
            d = np.minimum(np.minimum(xy[:, 0] - x0, x1 - xy[:, 0]), np.minimum(xy[:, 1] - y0, y1 - xy[:, 1]))
            r = np.random.default_rng(7).random(len(d))
            keep = (d < 0.07 * r) | (z >= 31.0)          # a feathered edge, not a hard box
        if keep is not None:
            pos, birth = pos[keep], birth[keep]
            if np.ndim(size):
                size = size[keep]
        if len(pos) == 0:
            return None
        return dict(pos=pos, size=size, alpha=1.0, birth=birth, kind="soft")

    def gain(self, t):
        return 1.0


def choir_sway(t):
    """How much the singers sway (metres at the crown): gently with the beat, still in the breath and the held
    breath."""
    a = 0.025 + 0.085 * intensity(t)
    a *= 1.0 - 0.85 * _win(t, 117.0, 121.32, 0.5, 0.3)
    a *= 1.0 - _win(t, HELD[0], HELD[1], 0.3, 0.3)
    return a


class Choir(Crowd):
    """The choir: a Crowd that sways with the beat (a lean from the feet, every two beats one way) and whose
    heart lights follow choir_glow."""

    def __init__(self, gain=None, **kw):
        super().__init__(**kw)
        self.g = gain or local_k
        r = np.random.default_rng(31)
        self.sph = 0.35 * r.random(self.n) + 0.25 * (self.place[:, 2] - FACADE_Z)
        self._sw = np.zeros(self.n)

    def gain(self, t):
        return float(self.g(t)) * (1.0 + 1.2 * _far(t, CHOIR_C)) * (1.0 + 0.5 * _sc(160.0, 205.0, t))

    def _place(self, P, ii, age, pr):
        sw = self._sw[ii]
        if np.any(sw):
            P = P.copy()
            h = np.clip(P[..., 1] / 1.7, 0.0, 1.2) ** 2
            ex = (slice(None),) + (None,) * (P.ndim - 2)
            P[..., 0] += sw[ex] * h
        return super()._place(P, ii, age, pr)

    def sample(self, t):
        if self.g(t) <= 0.0:
            self._last = (t, [])
            self._body = (t, [])
            return []
        self._sw = choir_sway(t) * np.sin(np.pi * beat_f(t) + self.sph)
        b = super().sample(t)
        lamps = []
        if len(b) >= 3:
            k = choir_glow(t)
            fl = chorus_flare(t)
            tint = (1.0 - 0.45 * fl) * np.ones(3) + 0.45 * fl * bar_colour(t) / max(float(bar_colour(t).max()), 1e-6)
            lamps = [dict(b[-2], alpha=b[-2]["alpha"] * min(0.7 * k, 1.8),
                          color=b[-2]["color"] * (0.8 + 0.2 * k) * tint),
                     dict(b[-1], alpha=b[-1]["alpha"] * min(0.5 + 0.5 * k, 1.6))]
            b = b[:-2]
        self._last = (t, lamps)
        self._body = (t, b)
        return b

    def body(self, t):
        if getattr(self, "_body", (None,))[0] != t:
            self.sample(t)
        return self._body[1]

    def lamps(self, t):
        if getattr(self, "_last", (None,))[0] != t:
            self.sample(t)
        return [dict(b, pos=b["pos"] + _v(0.0, 0.0, 0.22)) for b in self._last[1]]


class ChoirHearts:
    """The light at each singer's heart (the choir's lamps, drawn outside the choir's dark silhouette)."""

    def __init__(self, choir):
        self.c = choir

    def sample(self, t):
        return self.c.lamps(t) or None

    def gain(self, t):
        return self.c.gain(t)


# =========================================================================================================
# The orchestra: where everyone sits
# =========================================================================================================
PODIUM = _v(0.0, SUMMIT, FACADE_Z + 25.5)     # the conductor's place: the arcs open round it toward +z
RISERS = ((7.3, 0.30), (9.3, 0.60))            # (radius, height) of the two risers at the back

VIOLIN, VIOLA, CELLO, HARP, TIMPANI, TRUMPET, TROMBONE = range(7)


def _orchestra():
    """(section, floor point, facing degrees) of every player."""
    out = []

    def arc(sec, r, a0, a1, n, rise=0.0):
        for a in np.linspace(a0, a1, n):
            ar = np.radians(a)
            p = PODIUM + _v(r * np.sin(ar), rise, -r * np.cos(ar))
            out.append((sec, p, -0.55 * a))
    arc(VIOLIN, 4.4, -78.0, -14.0, 5)
    arc(CELLO, 4.6, 18.0, 78.0, 4)
    arc(VIOLIN, 6.4, -80.0, -8.0, 7)
    arc(VIOLA, 6.4, 8.0, 80.0, 6)
    arc(VIOLIN, 8.3, -76.0, -6.0, 7, RISERS[0][1])
    arc(CELLO, 8.4, 10.0, 70.0, 5, RISERS[0][1])
    arc(TRUMPET, 10.3, -44.0, -12.0, 4, RISERS[1][1])
    arc(TIMPANI, 10.6, -4.0, 6.0, 2, RISERS[1][1])
    arc(TROMBONE, 10.3, 16.0, 46.0, 4, RISERS[1][1])
    out.append((HARP, PODIUM + _v(-9.6, 0.0, -1.4), 90.0))
    out.append((HARP, PODIUM + _v(-10.4, 0.0, -4.6), 90.0))
    return out


ORCHESTRA = _orchestra()
ORCH_P = np.asarray([p for _, p, _ in ORCHESTRA], np.float64)
ORCH_SEC = np.asarray([s for s, _, _ in ORCHESTRA])
ORCH_FACE = np.asarray([f for _, _, f in ORCHESTRA], np.float64)
ORCH = dict(strings_l=[p for s, p, _ in ORCHESTRA if s == VIOLIN], strings_r=[p for s, p, _ in ORCHESTRA if s == VIOLA],
            cellos=[p for s, p, _ in ORCHESTRA if s == CELLO], harps=[p for s, p, _ in ORCHESTRA if s == HARP],
            timpani=[p for s, p, _ in ORCHESTRA if s == TIMPANI],
            brass=[p for s, p, _ in ORCHESTRA if s in (TRUMPET, TROMBONE)])
SEATED = (VIOLIN, VIOLA, CELLO, HARP)
PLAY_H = 1.68          # every player's height: the instruments are drawn for it
SIT_DROP = 0.36        # the seated pose ("held": thighs forward, legs down) hangs its feet this far down
LOOP = 2.0             # baked seconds of one player loop (= LOOP_BEATS beats of music)
LOOP_BEATS = 4.0
LOOP_T0 = 2.5 + 0.5    # where the crowd bakes its loop (crowd.PRE + crowd.CROSS)


def _u(*a):
    return _unit(np.asarray(a, np.float64))


def _ease(f):
    return 1.0 - (1.0 - f) ** 2


# ------------------------------------------------------------------ the instruments in the player's frame
class Bowing:
    """A string player's bow: the stroke as a function of the loop phase (a stroke every two beats: down on
    beats 0 and 1, up on 2 and 3); `hand(ph)` the bow hand, `bow(ph)` the stick (frog, tip)."""

    def __init__(self, C, b, n, s0, s1, length):
        self.C, self.b, self.n, self.s0, self.s1, self.L = C, b, n, s0, s1, length

    def s(self, ph):
        ph = np.mod(ph, 1.0)
        f = np.mod(ph * 2.0, 1.0)
        down = (ph < 0.5)
        e = _ease(f)
        return np.where(down, self.s0 + (self.s1 - self.s0) * e, self.s1 - (self.s1 - self.s0) * e)

    def hand(self, ph):
        return self.C + self.b * self.s(ph) + self.n * 0.02

    def bow(self, ph):
        s = np.atleast_1d(self.s(ph))
        frog = self.C[None, :] + self.b[None, :] * s[:, None] + self.n[None, :] * 0.012
        tip = frog - self.b[None, :] * self.L
        return frog, tip


class _At:
    """A gesture target that moves with the loop: a callable with a stable repr (the crowd keys its bake cache
    on the repr of its spec, so a lambda would bake afresh in every process)."""

    def __init__(self, name, f):
        self.name, self.f = name, f

    def __call__(self, t):
        return np.asarray(self.f(((t - LOOP_T0) / LOOP) % 1.0), np.float64)

    def __repr__(self):
        v = np.round([self.f(q) for q in np.linspace(0.0, 1.0, 9)], 3)
        return "At(%s,%s)" % (self.name, v.tolist())


def _violin_frame(scale=1.0):
    """The violin (or viola, scale 1.12) under the chin of a seated player: its end E, axis v (toward the
    scroll), top normal n, across w."""
    v = _u(0.58, 0.10, 0.80)
    n0 = _u(-0.42, 1.0, -0.05)
    n = _unit(n0 - v * float(n0 @ v))
    w = np.cross(n, v)
    E = _v(0.075, 1.385, 0.02) - v * 0.05 * scale
    return E, v, n, w


def _violin_bowing(scale=1.0):
    E, v, n, w = _violin_frame(scale)
    C = E + v * 0.16 * scale + n * 0.035
    b = _unit(w if w[0] < 0 else -w)          # toward the player's right
    b = _unit(b + _v(0.0, -0.20, 0.0))
    b = _unit(b - v * float(b @ v))
    return Bowing(C, b, n, 0.10, 0.56, 0.72 * scale)


CELLO_C = _v(0.0, 0.98, 0.34)      # where the bow crosses the cello's strings (in reach of a seated player)
CELLO_PIN = 0.34                    # the endpin's length


def _cello_frame():
    """The cello between the knees: the endpin on the floor in front, leaning back toward the left shoulder.
    Gives the bottom of its body, axis u (up the neck), the top's normal n and across w."""
    u = _u(0.08, 1.0, -0.35)
    n0 = _u(0.0, 0.35, 1.0)
    n = _unit(n0 - u * float(n0 @ u))
    w = np.cross(u, n)
    end = CELLO_C - n * 0.06 - u * ((CELLO_C[1] - 0.06 * n[1] - SIT_DROP) / u[1])
    return end, u, n, w


def _cello_bowing():
    end, u, n, w = _cello_frame()
    b = _unit(_v(-1.0, -0.12, 0.10))
    b = _unit(b - u * float(b @ u))
    return Bowing(CELLO_C, b, n, 0.05, 0.33, 0.70)


VB, VAB, CB = _violin_bowing(), _violin_bowing(1.12), _cello_bowing()

# the harp (the player faces +z locally; the strings stand in the plane x = HX)
HX = -0.05
HARP_BASE = _v(HX, SIT_DROP + 0.04, 0.62)
HARP_SHOULDER = _v(HX - 0.02, 1.60, 0.06)
HARP_TOP = _v(HX, SIT_DROP + 1.80, 0.98)


def _harp_hand(side, ph):
    """Hands on the strings, plucking on each beat (pulled out of the plane, then back in)."""
    f = np.mod(ph * LOOP_BEATS, 1.0)
    pull = 0.05 * np.exp(-f * 5.0) * (1.0 - np.exp(-f * 60.0))
    if side == "L":
        base = _v(HX + 0.07, 1.06, 0.40)
        return base + _v(pull, 0.0, 0.02 * np.sin(2 * np.pi * ph))
    base = _v(HX - 0.12, 0.92, 0.30)
    return base + _v(-pull, 0.0, -0.02 * np.sin(2 * np.pi * ph + 1.0))


# timpani: two kettles in front of a standing timpanist
TIMP_C = (_v(0.40, 0.0, 0.62), _v(-0.40, 0.0, 0.62))
TIMP_R, TIMP_H = 0.34, 0.80


def _mallet(side, ph):
    """(hand, mallet head) of the left (strikes on the even beats) or right hand (odd beats)."""
    k = 0 if side == "L" else 1
    c = TIMP_C[k]
    f = np.mod(ph * LOOP_BEATS / 2.0 - 0.5 * k, 1.0)          # 0 at its stroke, one stroke per two beats
    lift = np.sin(np.pi * np.clip(f, 0.0, 1.0)) ** 0.6
    head = c + _v(-0.06 if k == 0 else 0.06, TIMP_H + 0.02 + 0.30 * lift, -0.06)
    sg = 1.0 if k == 0 else -1.0
    hand = head + _v(-0.08 * sg, 0.10 + 0.08 * lift, -0.28)
    return hand, head


# brass: trumpets held level at the lips, trombones with their slide
MOUTH = _v(0.0, 1.535, 0.15)
TR_AX = _u(0.0, 0.10, 1.0)


def _slide(ph):
    """The trombone slide's reach out from the lips (a long note every two beats)."""
    f = np.mod(ph * LOOP_BEATS / 2.0, 1.0)
    return 0.16 + 0.12 * (0.5 - 0.5 * np.cos(2.0 * np.pi * f))


def _gest(name, side, f, palm, fingers="hold", look=False, lean=0.0):
    return ("touch", dict(side=side, to=_At(name, f), palm=palm, fingers=fingers, look=look, lean=lean))


def _player_kinds():
    vE, vv, vn, vw = _violin_frame()
    aE, av, an, aw = _violin_frame(1.12)
    cend, cu, cn, cw = _cello_frame()
    sit = dict(motion="held", loop=LOOP, height=PLAY_H)
    stand = dict(motion="stand", loop=LOOP, height=PLAY_H)
    k = {}
    lv = vE + vv * 0.50 - vn * 0.03
    la = aE + av * 0.55 - an * 0.03
    k[VIOLIN] = dict(sit, shape="woman", garment="dress", hair="bun", gest=[
        _gest("vl", "L", lambda ph: lv, palm=tuple(_unit(-vw * 0.0 + _v(-0.6, 0.2, 0.0))), look=True),
        _gest("vr", "R", VB.hand, palm=(0.0, -1.0, 0.2))])
    k[VIOLA] = dict(sit, shape="man", garment="tunic", hair="short", gest=[
        _gest("al", "L", lambda ph: la, palm=(-0.6, 0.2, 0.0), look=True),
        _gest("ar", "R", VAB.hand, palm=(0.0, -1.0, 0.2))])
    lc = cend + cu * (CELLO_PIN + 0.88) - cn * 0.03 + _v(0.03, 0.0, 0.0)
    k[CELLO] = dict(sit, shape="man", garment="tunic", hair="cap", gest=[
        _gest("cl", "L", lambda ph: lc, palm=(-1.0, 0.0, 0.2), look=True),
        _gest("cr", "R", CB.hand, palm=(0.0, -1.0, 0.0))])
    k[HARP] = dict(sit, shape="woman", garment="dress", hair="bun", gest=[
        _gest("hl", "L", lambda ph: _harp_hand("L", ph), palm=(-1.0, 0.0, 0.0), fingers="relaxed"),
        _gest("hr", "R", lambda ph: _harp_hand("R", ph), palm=(1.0, 0.0, 0.0), fingers="relaxed")])
    k[TIMPANI] = dict(stand, shape="man", garment="tunic", hair="short", gest=[
        _gest("tl", "L", lambda ph: _mallet("L", ph)[0], palm=(-0.3, -1.0, 0.0), fingers="fist", look=True),
        _gest("tr", "R", lambda ph: _mallet("R", ph)[0], palm=(0.3, -1.0, 0.0), fingers="fist")])
    k[TRUMPET] = dict(stand, shape="man", garment="coat", hair="cap", gest=[
        _gest("pl", "L", lambda ph: MOUTH + TR_AX * 0.20 + _v(0.035, -0.035, 0.0), palm=(-1.0, 0.0, 0.0)),
        _gest("pr", "R", lambda ph: MOUTH + TR_AX * 0.25 + _v(-0.01, 0.03, 0.0), palm=(0.0, -1.0, 0.0))])
    k[TROMBONE] = dict(stand, shape="woman", garment="coat", hair="tied", gest=[
        _gest("bl", "L", lambda ph: MOUTH + _v(0.05, -0.06, 0.12), palm=(-1.0, 0.0, 0.0)),
        _gest("br", "R", lambda ph: MOUTH + _v(-0.02, -0.16, 0.10 + _slide(ph)), palm=(1.0, 0.0, 0.0))])
    return [k[i] for i in range(7)]


class Players(Crowd):
    """The orchestra: a Crowd whose loops run on the beat (LOOP_BEATS beats per loop, all in time), with each
    player's section as its kind and exact facing (the instruments are drawn to fit)."""

    def __init__(self, gain=None, offset=_v(0.0, 0.0, 0.0), **kw):
        pl = ORCH_P + offset + np.where(np.isin(ORCH_SEC, SEATED), -SIT_DROP, 0.0)[:, None] * _v(0.0, 1.0, 0.0)
        super().__init__(places=pl, kinds=_player_kinds(), mirror=False, scale=1.0, **kw)
        self.g = gain or stage_k
        self.kind = ORCH_SEC.copy()
        self.facing = np.radians(ORCH_FACE)
        self.rate[:] = 0.0

    def gain(self, t):
        return float(self.g(t)) * (1.0 - (0.2 if t < SLAM3 else 0.0) * _far(t, ORCH_C))

    def sample(self, t):
        if self.g(t) <= 0.0:
            self._body = (t, [])
            return []
        self.phase[:] = play_ph(t)
        b = super().sample(t)
        self._body = (t, b)
        return b

    def body(self, t):
        if getattr(self, "_body", (None,))[0] != t:
            self.sample(t)
        return self._body[1]


def stage_k(t):
    """How present the choir and orchestra are: always there on the square (they show in the wide views of the
    city), formed in the intro (the orchestra wakes from 0:02.2, the choir out of the light from 0:21.5)."""
    return local_k(t)


# ------------------------------------------------------------------ drawing the instruments in light
def _outline(E, v, w, L, hw, step):
    """The outline of a violin-family body in its plane: from E along v for L, half width hw(l) across w."""
    n = max(int(2.6 * L / step), 24)
    l = np.linspace(0.0, L, n)
    h = hw(l / L) * L
    side = [E[None] + v[None] * l[:, None] + w[None] * (sg * h)[:, None] for sg in (1.0, -1.0)]
    return np.concatenate(side)


def _vhw(u):
    """Half width of a violin body (in body lengths) along its length u (0 the end button, 1 the neck)."""
    lower = 0.29 * np.exp(-((u - 0.27) / 0.22) ** 2)
    upper = 0.235 * np.exp(-((u - 0.78) / 0.17) ** 2)
    waist = 0.155
    w = np.maximum(np.maximum(lower, upper), waist * (1.0 - 0.0 * u))
    w = np.where((u > 0.42) & (u < 0.62), np.minimum(w, 0.155 + 0.6 * (np.abs(u - 0.52)) ** 1.5), w)
    tip = np.clip(u / 0.05, 0.0, 1.0) ** 0.5 * np.clip((1.0 - u) / 0.05, 0.0, 1.0) ** 0.5
    return w * tip


def _fill(E, v, w, L, hw, n, rng):
    u = rng.random(n)
    s = rng.uniform(-1.0, 1.0, n)
    h = hw(u) * L
    return E[None] + v[None] * (u * L)[:, None] + w[None] * (s * h)[:, None]


def _string_family(E, v, n, w, L, neck, rng, step):
    """A violin, viola or cello: (outline points, fill points, lines (a, b) of the strings and fingerboard)."""
    out = _outline(E, v, w, L, _vhw, step)
    out = np.concatenate([out, out + n * 0.012 * L / 0.36])
    fill = _fill(E + n * 0.006, v, w, L, _vhw, int(220 * L / 0.36), rng)
    # f-holes, the bridge and the scroll
    extra = []
    for sg in (1.0, -1.0):
        extra.append(_seg(E + v * L * 0.36 + w * sg * L * 0.075, E + v * L * 0.56 + w * sg * L * 0.07, step * 0.6))
    br = E + v * L * 0.44 + n * L * 0.06
    extra.append(_seg(br - w * L * 0.07, br + w * L * 0.07, step * 0.5))
    sc = E + v * (L + neck + 0.025 * L / 0.36) + n * 0.02
    a = np.linspace(0.0, 4.0 * np.pi, 30)
    rr = 0.022 * L / 0.36 * (1.0 - a / (5.0 * np.pi))
    extra.append(sc[None] + v[None] * (rr * np.cos(a))[:, None] + n[None] * (rr * np.sin(a))[:, None])
    out = np.concatenate([out] + extra)
    lines = []
    for k in np.linspace(-1.5, 1.5, 4):
        a0 = E + v * L * 0.06 + n * L * 0.045 + w * k * L * 0.018
        a1 = E + v * (L + neck) + n * 0.012 + w * k * L * 0.008
        lines.append((a0, a1))
    lines.append((E + v * L * 0.62 + n * L * 0.03, E + v * (L + neck) + n * 0.01))     # the fingerboard
    return out, fill, lines


def _harp(rng, step):
    """A concert harp: column, soundboard, the curved neck and the strings (all in the plane x = HX)."""
    col = _seg(HARP_BASE + _v(0.0, 0.0, 0.10), HARP_TOP, step)
    col = np.concatenate([col, col + _v(0.012, 0.0, 0.0), col + _v(-0.012, 0.0, 0.0)])
    board = _seg(HARP_BASE, HARP_SHOULDER, step)
    board = np.concatenate([board, board + _v(0.0, 0.0, 0.05)])
    m = 80
    s = np.linspace(0.0, 1.0, m)
    neck = HARP_SHOULDER[None] * (1 - s)[:, None] + HARP_TOP[None] * s[:, None]
    neck[:, 1] += 0.16 * np.sin(np.pi * s) * (1.0 - 0.6 * s) - 0.10 * np.sin(np.pi * s) ** 4
    crown = HARP_TOP + _v(0.0, 0.06, 0.02)
    base = _ring(HARP_BASE + _v(0.0, 0.0, 0.06), 0.12, SIT_DROP + 0.02, step)
    pts = np.concatenate([col, board, neck, neck + _v(0.0, 0.025, 0.0), base, crown[None]])
    lines = []
    for q in np.linspace(0.06, 0.94, 28):
        z = HARP_SHOULDER[2] + (HARP_BASE[2] - HARP_SHOULDER[2]) * q
        bot = HARP_SHOULDER + (HARP_BASE - HARP_SHOULDER) * q
        j = int(np.argmin(np.abs(neck[:, 2] - z)))
        top = _v(HX, neck[j, 1] - 0.01, z)
        lines.append((bot + _v(0.0, 0.0, 0.02), top))
    return pts, lines


def _timpani(step):
    pts, heads = [], []
    for i, c in enumerate(TIMP_C):
        top = c[1] + TIMP_H
        for el in np.linspace(0.0, 1.25, 7):
            pts.append(_ring(c, TIMP_R * np.cos(el) * (1.0 if el > 0 else 1.04), top - 0.42 * np.sin(el) - 0.02, step))
        for a in np.linspace(0.0, 2 * np.pi, 14, endpoint=False):
            e = np.linspace(0.0, 1.25, 14)
            pts.append(np.stack([c[0] + TIMP_R * np.cos(e) * np.sin(a), top - 0.02 - 0.42 * np.sin(e),
                                 c[2] + TIMP_R * np.cos(e) * np.cos(a)], 1))
        for a in np.linspace(0.0, 2 * np.pi, 3, endpoint=False):           # the legs
            pts.append(_seg(c + _v(0.22 * np.sin(a), top - 0.42, 0.22 * np.cos(a)),
                            c + _v(0.30 * np.sin(a), 0.0, 0.30 * np.cos(a)), step))
        r = np.sqrt(np.random.default_rng(70 + i).random(260)) * TIMP_R * 0.98
        a = np.random.default_rng(80 + i).random(260) * 2 * np.pi
        heads.append(np.stack([c[0] + r * np.sin(a), np.full(260, top + 0.005), c[2] + r * np.cos(a)], 1))
        pts.append(_ring(c, TIMP_R + 0.015, top + 0.01, step * 0.7))
    return np.concatenate(pts), np.concatenate(heads)


def _bell(c, ax, r0, r1, L, step):
    """A flared bell: rings opening along ax from radius r0 to r1 over L."""
    ax = _unit(ax)
    a = _unit(np.cross(ax, _v(0.0, 1.0, 0.0)) if abs(ax[1]) < 0.9 else np.cross(ax, _v(1.0, 0.0, 0.0)))
    b = np.cross(ax, a)
    out = []
    for q in np.linspace(0.0, 1.0, 6):
        r = r0 + (r1 - r0) * q ** 3
        n = max(int(2 * np.pi * r / step), 8)
        ph = np.linspace(0, 2 * np.pi, n, endpoint=False)
        out.append(c[None] + ax[None] * (L * q) + r * (np.cos(ph)[:, None] * a[None] + np.sin(ph)[:, None] * b[None]))
    return np.concatenate(out)


def _trumpet(step):
    m = MOUTH + TR_AX * 0.02
    bell0 = m + TR_AX * 0.40
    pts = [_seg(m, bell0, step * 0.7), _seg(m + TR_AX * 0.10 + _v(0, -0.055, 0), m + TR_AX * 0.36 + _v(0, -0.055, 0), step * 0.7),
           _bell(bell0, TR_AX, 0.012, 0.062, 0.14, step * 0.6)]
    for k in range(3):
        v0 = m + TR_AX * (0.21 + 0.03 * k)
        pts.append(_seg(v0 + _v(0, -0.07, 0), v0 + _v(0, 0.03, 0), step * 0.5))
    return np.concatenate(pts), bell0 + TR_AX * 0.14


def _trombone(step):
    m = MOUTH + _v(0.0, 0.0, 0.02)
    ax = _u(0.0, -0.08, 1.0)
    bell_c = m + _v(0.09, 0.03, 0.06)
    pts = [_seg(m, m + ax * 0.12, step * 0.7), _seg(bell_c - ax * 0.10, bell_c + ax * 0.30, step * 0.7),
           _bell(bell_c + ax * 0.30, ax, 0.02, 0.11, 0.22, step * 0.6),
           _seg(m + ax * 0.04, bell_c - ax * 0.10, step * 0.7)]
    return np.concatenate(pts), bell_c + ax * 0.52


def _local_instruments():
    """Every section's instrument in the player's frame: dict(sec -> (points, fill, lines))."""
    rng = np.random.default_rng(77)
    st = 0.006
    out = {}
    E, v, n, w = _violin_frame()
    out[VIOLIN] = _string_family(E, v, n, w, 0.36, 0.23, rng, st)
    E, v, n, w = _violin_frame(1.12)
    out[VIOLA] = _string_family(E, v, n, w, 0.41, 0.25, rng, st)
    e, u, n, w = _cello_frame()
    o, f, l = _string_family(e + u * CELLO_PIN, u, n, w, 0.76, 0.42, rng, 0.01)
    out[CELLO] = (np.concatenate([o, _seg(e, e + u * CELLO_PIN, 0.01)]), f, l)
    hp, hl = _harp(rng, 0.012)
    out[HARP] = (hp, np.zeros((0, 3)), hl)
    tp, th = _timpani(0.014)
    out[TIMPANI] = (tp, th, [])
    p, _ = _trumpet(0.006)
    out[TRUMPET] = (p, np.zeros((0, 3)), [])
    p, _ = _trombone(0.006)
    out[TROMBONE] = (p, np.zeros((0, 3)), [])
    return out


def _to_world(P, k, offset):
    """Points of player k's frame into the world (as the crowd places the player)."""
    P = np.asarray(P, np.float64).reshape(-1, 3)
    a = np.radians(ORCH_FACE[k])
    cs, sn = np.cos(a), np.sin(a)
    base = ORCH_P[k] + offset - (_v(0.0, SIT_DROP, 0.0) if ORCH_SEC[k] in SEATED else 0.0)
    x = P[:, 0] * cs + P[:, 2] * sn
    z = -P[:, 0] * sn + P[:, 2] * cs
    return np.stack([x + base[0], P[:, 1] + base[1], z + base[2]], 1)


INSTR_COL = {VIOLIN: "#ffc98a", VIOLA: "#ffc07a", CELLO: "#ffb870", HARP: "#ffd88c", TIMPANI: "#f0a066",
             TRUMPET: "#ffd77a", TROMBONE: "#ffd77a"}


def _hitters_local():
    out = {TRUMPET: [_trumpet(0.01)[1]], TROMBONE: [_trombone(0.01)[1]],
           TIMPANI: [c + _v(0.0, TIMP_H + 0.02, 0.0) for c in TIMP_C]}
    return out


class Instruments:
    """The orchestra's instruments drawn in light, fitted to the players (Players): violins, violas and cellos
    in warm amber with strings and bows of light that move on the beat, two concert harps, copper timpani
    with their mallets, trumpets and trombones; light bursts from the bells and the drum heads on the hits.
    Instruments(offset=..., gain=...) draws the same orchestra moved by offset (the coda's orchestra on the
    clouds uses it)."""

    HITS = None

    def __init__(self, offset=_v(0.0, 0.0, 0.0), gain=None):
        self.off = np.asarray(offset, np.float64)
        self.g = gain or stage_k
        loc = _local_instruments()
        pts, cols, fill, fcol, la, lb, lc = [], [], [], [], [], [], []
        for k, sec in enumerate(ORCH_SEC):
            p, f, lines = loc[sec]
            c = lin(INSTR_COL[sec])
            pts.append(_to_world(p, k, self.off))
            cols.append(np.repeat(c[None], len(p), 0))
            if len(f):
                fill.append(_to_world(f, k, self.off))
                fcol.append(np.repeat(c[None] * (0.55 if sec != TIMPANI else 1.2), len(f), 0))
            for a, b in lines:
                la.append(_to_world(a, k, self.off)[0])
                lb.append(_to_world(b, k, self.off)[0])
                lc.append(lin("#fff4e0") if sec != HARP else lin("#f4f8ff"))
        self.P, self.C = np.concatenate(pts), np.concatenate(cols)
        self.F, self.FC = np.concatenate(fill), np.concatenate(fcol)
        self.LA, self.LB, self.LC = np.asarray(la), np.asarray(lb), np.asarray(lc)
        self.sec = ORCH_SEC
        self.bowed = [(k, VB if s == VIOLIN else VAB if s == VIOLA else CB) for k, s in enumerate(ORCH_SEC)
                      if s in (VIOLIN, VIOLA, CELLO)]
        self.timp = [k for k, s in enumerate(ORCH_SEC) if s == TIMPANI]
        self.bones = [k for k, s in enumerate(ORCH_SEC) if s == TROMBONE]
        hl = _hitters_local()
        hp, hd = [], []
        for k, s in enumerate(ORCH_SEC):
            for q in hl.get(s, []):
                hp.append(_to_world(q, k, self.off)[0])
                if s == TIMPANI:
                    hd.append(_v(0.0, 1.0, 0.0))
                else:
                    a = np.radians(ORCH_FACE[k])
                    hd.append(_u(np.sin(a), 0.12, np.cos(a)))
        self.hp, self.hd = np.asarray(hp), np.asarray(hd)
        r = np.random.default_rng(5)
        self.s = r.random((len(self.hp), 70, 4))
        self.rs = r.random(len(self.F))

    def _hit(self, t):
        k, last = 0.0, None
        for h in KICKS:
            if -0.05 <= t - h < 2.0:
                big = 1.0 if h in (SLAM1, SLAM2, SLAM3) else 0.7
                k, last = big * np.exp(-max(t - h, 0.0) / (0.5 if big == 1.0 else 0.35)), h
        return k, last

    def sample(self, t):
        g = self.g(t)
        if g <= 0.0:
            return None
        g *= _sc(2.2, 6.0, t)
        if g <= 0.0:
            return None
        ph = play_ph(t)
        acc = hit_pulse(t, STRINGS, fall=0.5) + 0.35 * beat_pulse(t, 0.1)
        hk, last = self._hit(t)
        out = [dict(pos=self.P, size=0.016, color=self.C * (1.0 + 0.6 * acc + 0.8 * hk), alpha=0.85 * g,
                    emit=1.6, kind="spark", twinkle=0.25, dof=0.6, fog=0.6),
               dict(pos=self.F, size=0.03, color=self.FC, alpha=(0.30 + 0.25 * acc) * g, kind="soft", emit=1.0,
                    twinkle=0.4, seed=self.rs, dof=0.6, fog=0.6),
               dict(pos=self.LA, pos2=self.LB, size=0.0035, color=self.LC * (1.0 + 0.8 * acc), alpha=0.75 * g,
                    emit=1.6, kind="line", dof=0.6, fog=0.6)]
        # the bows: drawn on the beat, every section in time
        fa, fb = [], []
        for k, bw in self.bowed:
            frog, tip = bw.bow(ph)
            fa.append(_to_world(frog, k, self.off)[0])
            fb.append(_to_world(tip, k, self.off)[0])
        fa, fb = np.asarray(fa), np.asarray(fb)
        out.append(dict(pos=fa, pos2=fb, size=0.007, color=lin("#fff6ea") * (1.2 + 0.8 * acc), alpha=0.95 * g,
                        emit=2.0, kind="line", dof=0.6, fog=0.6))
        out.append(dict(pos=fa, size=0.03, color=lin("#fff1d8"), alpha=0.8 * g, emit=2.0, kind="spark", dof=0.6))
        # the mallets
        ma, mb = [], []
        for k in self.timp:
            for side in ("L", "R"):
                hand, head = _mallet(side, ph)
                ma.append(_to_world(hand, k, self.off)[0])
                mb.append(_to_world(head, k, self.off)[0])
        if ma:
            ma, mb = np.asarray(ma), np.asarray(mb)
            out.append(dict(pos=ma, pos2=mb, size=0.012, color=lin("#fff1dc"), alpha=0.9 * g, emit=1.6, kind="line",
                            dof=0.6))
            out.append(dict(pos=mb, size=0.07, color=lin("#fff6e8"), alpha=0.9 * g, emit=2.4, kind="soft", dof=0.6))
        # the trombone slides
        sa, sb = [], []
        for k in self.bones:
            m = MOUTH + _v(0.0, -0.02, 0.06)
            ax = _u(0.0, -0.08, 1.0)
            L = 0.30 + _slide(ph)
            for dx in (-0.025, 0.025):
                sa.append(_to_world(m + _v(dx, -0.05, 0.0), k, self.off)[0])
                sb.append(_to_world(m + ax * L + _v(dx, -0.05, 0.0), k, self.off)[0])
        if sa:
            out.append(dict(pos=np.asarray(sa), pos2=np.asarray(sb), size=0.009, color=lin(INSTR_COL[TROMBONE]),
                            alpha=0.9 * g, emit=1.8, kind="line", dof=0.6))
        # the drum heads breathe on the beat; light bursts from the bells and heads on the hits
        bp = beat_pulse(t, 0.1)
        out.append(dict(pos=self.hp, size=0.35 + 0.5 * hk, color=lin(GOLD), alpha=(0.10 + 0.12 * bp + 0.35 * hk) * g,
                        kind="soft", emit=1.5, dof=0.6))
        if hk > 0.01:
            u = max(t - last, 0.0)
            s = self.s
            d = self.hd[:, None, :] * 1.2 + (s[..., :3] - 0.5) * 1.2
            d /= np.linalg.norm(d, axis=2, keepdims=True)
            reach = (0.25 + 3.0 * (1.0 - np.exp(-u / 0.5))) * (0.4 + 0.6 * s[..., 3:4])
            pos = self.hp[:, None, :] + d * reach
            col = 0.45 * lin("#fff1cf") + 0.55 * lin(COL9[KICKS.index(last) % 9]) * 1.6
            out.append(dict(pos=pos.reshape(-1, 3), size=0.045, color=col, alpha=0.85 * hk * g, emit=3.0,
                            kind="spark", twinkle=0.5, dof=0.6))
            # beams of light out of the bells and up from the drum heads
            a = np.repeat(self.hp, 3, axis=0)
            dd = np.repeat(self.hd, 3, axis=0) + (self.s[:, :3, :3].reshape(-1, 3) - 0.5) * 0.25
            dd /= np.linalg.norm(dd, axis=1, keepdims=True)
            b = a + dd * (1.5 + 4.5 * (1.0 - np.exp(-u / 0.35)))
            out.append(dict(pos=a, pos2=b, alpha2=np.zeros(len(a)), size=0.08, size2=0.28, color=col,
                            alpha=0.3 * hk * g, emit=2.0, kind="ribbon", dof=0.6))
        return out


class Risers:
    """The orchestra's floor of light: the two curved risers at the back and the podium."""
    static = True

    def __init__(self):
        pts = []
        for r, h in RISERS:
            a0, a1 = np.radians(-84.0), np.radians(84.0)
            pts.append(_ring(PODIUM, r, PODIUM[1] + h, 0.05, np.pi - a1, np.pi - a0))
            pts.append(_ring(PODIUM, r, PODIUM[1] + 0.02, 0.08, np.pi - a1, np.pi - a0))
        pts.append(_ring(PODIUM, 0.6, PODIUM[1] + 0.25, 0.04))
        pts.append(_ring(PODIUM, 0.6, PODIUM[1] + 0.02, 0.06))
        self.P = np.concatenate(pts)

    def sample(self, t):
        return dict(pos=self.P, size=0.02, color=lin("#cfe4ff") * 0.35, alpha=0.5, emit=1.0, kind="spark",
                    twinkle=0.2)

    def gain(self, t):
        return stage_k(t)


# =========================================================================================================
# Light of the singing, and the snow of light in the breath
# =========================================================================================================
PERFORM = [(0.0, 21.5, "Orchestra (faint choir hum)"), (21.5, 29.8, "Choir and orchestra"), (29.8, 31.0, "Orchestra"),
           (31.0, 39.0, "Choir and orchestra"), (39.0, 41.0, "Orchestra"), (41.0, 247.5, "Choir and orchestra"),
           (247.5, 249.5, "Held breath"), (249.5, 259.95, "Choir and orchestra"), (259.95, 275.0, "Silence")]


class ChoirLight:
    """Light rising from the choir as they sing: more with the loudness, nothing while they are silent."""

    def __init__(self, places, gain=None):
        self.p = places
        r = np.random.default_rng(9)
        self.s = r.random((len(places) * 4, 4))
        d = r.normal(0.0, 1.0, (len(self.s), 3))
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.g = gain or stage_k

    def sample(self, t):
        g = self.g(t)
        sing = 0.0
        for a, b, w in PERFORM:
            if a <= t < b and w.startswith("Choir"):
                sing = 1.0
        k = g * sing * _sc(21.4, 22.6, t) * (0.25 + 0.5 * loud(t))
        out = []
        s = self.s
        if k > 0.01:
            base = np.repeat(self.p, 4, axis=0) + _v(0.0, 1.62, 0.18)
            age = np.mod(t * (0.22 + 0.18 * s[:, 0]) + s[:, 1], 1.0)
            pos = base + np.stack([0.35 * (s[:, 2] - 0.5) * (0.4 + age), 3.2 * age, 0.25 * (s[:, 3] - 0.5)], 1)
            out.append(dict(pos=pos, size=0.022 + 0.02 * s[:, 2], color=lin("#ffe6b0"),
                            alpha=k * np.sin(np.pi * age) ** 1.5, emit=2.2, kind="spark", twinkle=0.7, seed=s[:, 3],
                            dof=0.5))
        # the breath in (1:17.5 to 1:22): light streams in from the air round each singer and gathers at the
        # heart; on the slam it bursts out again
        if 77.0 <= t < 84.0 and g > 0.0:
            heart = np.repeat(self.p, 4, axis=0) + _v(0.0, 1.20, 0.30)
            d = self.d
            if t < SLAM1:
                ramp = _sc(77.2, 81.6, t)
                cyc = np.mod(t * (0.55 + 0.35 * s[:, 0]) + s[:, 1], 1.0)
                r = (0.25 + 1.6 * s[:, 2]) * (1.0 - cyc) ** 1.6
                a = g * (0.25 + 0.75 * ramp) * np.sin(np.pi * cyc) ** 0.7
                pos = heart + d * r[:, None] + _v(0.0, 0.5, 0.0) * (r[:, None] * 0.4)
            else:
                u = t - SLAM1
                r = (0.1 + 4.0 * (1.0 - np.exp(-u / 0.5))) * (0.4 + 0.6 * s[:, 2])
                a = g * np.exp(-u / 0.6) * np.ones(len(s))
                pos = heart + d * r[:, None]
            out.append(dict(pos=pos, size=0.02 + 0.02 * s[:, 3], color=lin("#fff0cf"), alpha=a, emit=2.6,
                            kind="spark", twinkle=0.4, seed=s[:, 0], dof=0.5))
        return out or None


class Snow:
    """The breath (1:57 to 2:01.3): light falls like snow round the still, glowing choir."""

    def __init__(self):
        r = np.random.default_rng(101)
        self.s = r.random((1800, 5))

    def sample(self, t):
        if not (116.5 <= t < 121.9) or local_k(t) <= 0.0:
            return None
        k = _env(t, 116.8, 121.8, 0.6, 0.8)
        s = self.s
        y = SUMMIT + 9.0 - np.mod(t * (0.35 + 0.35 * s[:, 2]) + 9.0 * s[:, 3], 9.0)
        x = -14.0 + 28.0 * s[:, 0] + 0.25 * np.sin(t * 0.8 + 6.0 * s[:, 4])
        z = FACADE_Z - 1.0 + 13.0 * s[:, 1]
        return dict(pos=np.stack([x, y, z], 1), size=0.018 + 0.022 * s[:, 4], color=lin("#fff1d8"), alpha=0.75 * k,
                    emit=1.8, kind="spark", twinkle=0.5, seed=s[:, 4], dof=0.8)


def add(scene):
    choir = Choir(places=CHOIR_P, facing=0.0, kinds=CHOIR_KINDS,
                  start=dict(t=21.3, center=(0.0, FACADE_Z), speed=9.0), color="#ffb84a", color2="#ffe9b8",
                  bright=3.2, points=3200, size=1.1, flash=1.2, glints=0.004, dof=0.35, seed=3.0,
                  light="#ffd890", lamp=(0.20, 1.0), scale=(0.97, 1.03))
    scene.add("choir", choir, mask=Mask("dark", strength=choir_mask, grow=0.03, source=MaskSource(choir)))
    scene.add("choir hearts", ChoirHearts(choir))
    orch = Players(start=dict(t=2.2, dur=7.0), color=CRYSTAL, color2="#ffffff", bright=3.5, points=2800,
                   size=1.2, glints=0.006, dof=0.35, seed=4.0)
    scene.add("orchestra", orch, mask=Mask("dark", strength=orch_mask, grow=0.03, source=MaskSource(orch)))
    scene.add("risers", Risers())
    scene.add("instruments", Instruments())
    scene.add("choir light", ChoirLight(CHOIR_P))
    scene.add("snow", Snow())
