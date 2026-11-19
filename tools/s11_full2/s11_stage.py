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

def _S(name, t0, t1, fov, keys=None, ap=0.02, focus=None, **kw):
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


# one shot per block of the core's EDIT (blocks_of("stage")): each a flowing flight through several keys
SHOTS = [
    # the orchestra wakes, the comets weave through it: a long low flight over the strings toward the choir
    _S("st_dawn", 26.33, 31.11, 46.0, roll=(-7.0, 3.0), keys=[(0.0, _P(-9.0, 1.2, 40.0), _P(-2.0, 1.5, 20.0)),
                                       (0.5, _P(-5.0, 2.2, 31.0), _P(0.0, 1.6, 18.0)),
                                       (1.0, _P(0.0, 3.4, 27.0), _P(0.0, 2.2, 8.0))], ap=0.012),
    # the choir breathes in, the comets spiral in: an orbit in front of the singers
    _S("st_breath_in", 77.46, 80.94, 42.0, [(0.0, _P(-7.0, 2.2, 11.5), _P(-1.0, 2.4, 2.5)),
                                            (0.5, _P(-3.0, 2.0, 9.8), _P(0.0, 2.5, 2.5)),
                                            (1.0, _P(1.5, 1.8, 8.4), _P(0.0, 2.6, 2.5))], focus=_P(0.0, 2.0, 4.0)),
    # the last half bar: a hard push into the choir
    _S("st_build4", 81.51, 82.08, 46.0, [(0.0, _P(2.0, 2.4, 12.5), _P(0.0, 2.7, 2.0)),
                                         (1.0, _P(0.5, 2.6, 7.5), _P(0.0, 2.7, 2.0))], focus=_P(0.0, 2.2, 4.0)),
    # SLAM 1: close in the blaze, then a great crane up and back over the whole stage
    _S("st_slam1", 82.08, 86.7, 52.0, roll=(9.0, -4.0), keys=[(0.0, _P(-6.0, 2.0, 30.0), _P(0.0, 4.0, 10.0)),
                                       (0.4, _P(-3.0, 8.0, 36.0), _P(0.0, 7.0, 10.0)),
                                       (1.0, _P(4.0, 16.0, 46.0), _P(0.0, 9.0, 8.0))], ap=0.01),
    # the brass and timpani blaze: a crane low over the strings up to the back rows
    _S("st_blaze1", 105.14, 108.4, 46.0, [(0.0, _P(4.0, 1.5, 28.0), _P(3.0, 2.0, 16.0)),
                                          (0.5, _P(3.5, 2.6, 23.0), _P(3.0, 2.2, 16.0)),
                                          (1.0, _P(1.0, 3.6, 20.0), _P(0.0, 2.0, 15.0))], ap=0.015),
    # the breath: a slow orbit round the still choir in the falling light
    _S("st_snow", 117.0, 121.32, 38.0, [(0.0, _P(6.0, 2.4, 10.0), _P(0.5, 2.5, 2.5)),
                                        (0.5, _P(3.0, 2.6, 11.0), _P(0.3, 2.5, 2.5)),
                                        (1.0, _P(0.0, 2.8, 11.5), _P(0.0, 2.6, 2.5))], focus=_P(0.3, 2.0, 4.0)),
    # verse 2: flying low along the strings to the harps
    _S("st_strings", 121.32, 125.92, 40.0, roll=(-5.0, 5.0), keys=[(0.0, _P(4.0, 1.3, 27.5), _P(1.0, 1.1, 21.0)),
                                            (0.5, _P(-2.0, 1.3, 27.8), _P(-3.0, 1.1, 21.0)),
                                            (1.0, _P(-7.0, 1.5, 27.5), _P(-9.2, 1.2, 23.5))], ap=0.02),
    # the choir draws breath: a push in from the side
    _S("st_build5", 160.6, 161.7, 42.0, [(0.0, _P(6.0, 2.4, 11.0), _P(0.5, 2.5, 2.5)),
                                         (1.0, _P(3.0, 2.4, 8.5), _P(0.5, 2.5, 2.5))], focus=_P(0.8, 2.0, 4.0)),
    # SLAM 2: low and wide up at the blazing brass, rising
    _S("st_slam2", 162.86, 165.16, 54.0, roll=(-10.0, 4.0), keys=[(0.0, _P(5.0, 1.2, 31.0), _P(0.0, 4.0, 14.0)),
                                          (0.5, _P(1.0, 5.0, 30.0), _P(0.0, 7.0, 12.0)),
                                          (1.0, _P(-4.0, 11.0, 32.0), _P(0.0, 10.0, 10.0))], ap=0.012),
    # the brass rising: a crane past the trombones
    _S("st_brass_rise", 183.0, 185.92, 46.0, roll=(4.0, -3.0), keys=[(0.0, _P(6.0, 1.6, 24.0), _P(4.5, 2.1, 16.5)),
                                              (0.5, _P(5.0, 3.0, 22.5), _P(4.2, 2.2, 16.5)),
                                              (1.0, _P(3.0, 5.0, 21.0), _P(2.0, 2.0, 15.0))], ap=0.02),
    # wondrous love: an arc from the front round the trumpets and timpani
    _S("st_love", 185.92, 188.27, 46.0, [(0.0, _P(-6.0, 3.4, 32.0), _P(-3.0, 2.4, 15.0)),
                                         (0.5, _P(-4.0, 3.2, 31.0), _P(-3.0, 2.4, 15.0)),
                                         (1.0, _P(-2.0, 3.0, 30.0), _P(-2.5, 2.4, 15.0))], ap=0.012),
    # the coda hit: a push into the choir as it blazes
    _S("st_coda_hit", 199.62, 200.7, 46.0, roll=(6.0, -2.0), keys=[(0.0, _P(-1.0, 2.5, 13.0), _P(0.0, 2.7, 2.0)),
                                            (1.0, _P(0.0, 2.6, 8.2), _P(0.0, 2.7, 2.0))], focus=_P(0.0, 2.2, 4.0)),
    # the choir in the sunrise: low from the right, up at the singers
    _S("st_choir_low", 210.3, 211.6, 46.0, [(0.0, _P(5.5, 1.0, 10.0), _P(1.0, 3.4, 2.0)),
                                            (1.0, _P(3.0, 1.3, 9.0), _P(0.8, 3.4, 2.0))], focus=_P(1.5, 2.0, 4.0)),
    # sacrifice: low under the trumpets' bells
    _S("st_sacrifice", 218.1, 220.2, 48.0, [(0.0, _P(-5.0, 1.7, 22.5), _P(-4.6, 2.5, 16.5)),
                                            (1.0, _P(-3.6, 2.2, 20.0), _P(-4.2, 2.5, 16.5))], ap=0.025,
       focus=_P(-4.5, 2.2, 16.8)),
    # home: Oh, the Church of God; a long flight in from the audience over the orchestra
    _S("st_home", 238.8, 242.5, 46.0, roll=(-4.0, 2.0), keys=[(0.0, _P(-6.0, 3.2, 42.0), _P(-0.5, 3.6, 6.0)),
                                       (0.5, _P(-3.0, 3.6, 36.0), _P(0.0, 3.4, 6.0)),
                                       (1.0, _P(0.0, 4.5, 28.0), _P(0.0, 3.0, 5.0))], ap=0.01),
    # the choir: a close orbit along the front row
    _S("st_home_choir", 244.8, 247.5, 42.0, [(0.0, _P(-5.0, 2.3, 11.0), _P(-0.5, 2.6, 2.5)),
                                             (0.5, _P(-2.0, 2.3, 10.0), _P(0.0, 2.6, 2.5)),
                                             (1.0, _P(1.0, 2.4, 9.5), _P(0.0, 2.6, 2.5))], focus=_P(0.0, 2.0, 4.0)),
    # the held breath: still, looking up past the choir to the sparks gathering above
    _S("st_held", 247.5, 249.43, 50.0, [(0.0, _P(0.0, 2.0, 16.0), _P(0.0, 5.0, 3.0)),
                                        (1.0, _P(0.0, 2.2, 15.0), _P(0.0, 6.0, 3.0))], ap=0.012, pace="linear"),
    # the final rise: a crane up and back over everyone
    _S("st_final", 249.43, 251.7, 54.0, roll=(0.0, 14.0), keys=[(0.0, _P(0.0, 2.6, 13.0), _P(0.0, 4.0, 3.0)),
                                         (0.35, _P(8.0, 5.0, 11.0), _P(0.0, 4.5, 3.0)),
                                         (0.7, _P(7.0, 10.0, 17.0), _P(0.0, 7.0, 3.0)),
                                         (1.0, _P(-3.0, 12.0, 24.0), _P(0.0, 40.0, 45.0))], ap=0.0),
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


CHOIR_ALL = _choir_places()
HERO_I = [8, 10, 12]                       # three singers in the middle of the front row, finely detailed
HERO_P = CHOIR_ALL[HERO_I]
CHOIR_P = np.delete(CHOIR_ALL, HERO_I, axis=0)
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
    k = 0.35 + 0.25 * loud(t) + 0.25 * beat_pulse(t, 0.12) + 0.35 * _mx("choir", t) * _room(t)
    k += 1.4 * _sc(77.46, 82.0, t) ** 1.6 * (1.0 - _sc(82.1, 84.5, t))
    k += 0.6 * hit_pulse(t, [SLAM1], fall=0.8)
    k += 0.7 * _win(t, 117.0, 121.2, 0.6, 0.4)
    k += 0.9 * _sc(247.5, 249.43, t) * (1.0 - _sc(250.5, 253.0, t)) + 1.2 * hit_pulse(t, [HIT["final"], LAST_CHORD], fall=0.9)
    k += 1.1 * chorus_flare(t)
    return k


def end_glow(t):
    """The choir blazes gold at the end (home, the held breath, the final rise)."""
    return 1.0 + 0.9 * _sc(247.0, 247.5, t) * (1.0 - _sc(252.0, 254.0, t))


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


def _mx(name, t):
    """A music-map channel (s11_music_fx), 0 when the map is missing."""
    try:
        import songs.s11_music_fx as MF
        return float(getattr(MF, "fx_" + name)(t))
    except Exception:  # noqa: BLE001
        return 0.0


def _room(t):
    try:
        import songs.s11_music_fx as MF
        return float(MF.room(t))
    except Exception:  # noqa: BLE001
        return 1.0


# Key moments in the stage and conductor shots (round 10, Anthony: "Not everything needs to be so washed out
# and bright all the time. Key timings should be highlighted. Do not saturate everything. Do not wash out."):
# the stage rests calmer and darker, and only these get the full light and colour
KEY_WINDOWS = [(82.08, 84.6), (97.7, 99.45), (104.9, 107.6), (121.32, 123.8), (162.86, 165.1), (184.65, 188.3),
               (199.62, 201.0), (213.0, 224.0), (247.5, 251.7)]


def key_k(t):
    """0 at rest, 1 inside a key moment (eased in 0.35 s, out 0.6 s)."""
    k = 0.0
    for a, b in KEY_WINDOWS:
        if a - 0.4 <= t <= b + 0.7:
            k = max(k, _sc(a - 0.35, a, t) * (1.0 - _sc(b, b + 0.6, t)))
    return k


def rest(t, lo):
    """A set's level: lo at rest, 1 in the key moments."""
    return lo + (1.0 - lo) * key_k(t)


def phrase_k(t):
    """0..1, eased: how much a phrase is reading at t (in 0.3 s before the words arrive, out 0.3 s after)."""
    import songs.s11_full2 as H
    k = 0.0
    for _l, (ti, _r0, _r1, to), *_x in H.PHRASE_LIST:
        if ti - 0.8 <= t <= to + 0.8:
            k = max(k, _sc(ti - 0.7, ti - 0.3, t) * (1.0 - _sc(to + 0.3, to + 0.7, t)))
    return k


WORD_BOX = (0.15, 0.85, 0.52, 0.75)     # x0, x1, y0, y1 of the words on screen (0..1, y up)


CORNER_BOX = (-0.05, 0.42, -0.05, 0.14)  # the logo and the periodic titles, bottom left


def corner_k(t):
    """0..1 while the corner titles show beside the logo (SIG_TEXT windows)."""
    import songs.s11_full2 as H
    k = 0.0
    for a, b in getattr(H, "SIG_TEXT", []):
        if a - 0.6 <= t <= b + 0.6:
            k = max(k, _sc(a - 0.6, a, t) * (1.0 - _sc(b, b + 0.6, t)))
    return k


class BoxGuard:
    """Keeps a point set's light out of the words while a phrase reads (Anthony's rule: nothing bright crosses
    a phrase): every point whose glow, as the camera sees it, reaches into the word box fades out there, with
    a feathered edge, and comes back as the phrase leaves. Everything else of the wrapped set is unchanged."""
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
        inside = np.clip(d / 0.06 + 0.5, 0.0, 1.0) * (z > 0.0)
        return inside

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
                f = np.maximum(f, self._fade(cam, np.asarray(b["pos2"], np.float64).reshape(-1, 3), size))
                f = np.maximum(f, self._fade(cam, 0.5 * (P + np.asarray(b["pos2"], np.float64).reshape(-1, 3)), size))
            a = np.broadcast_to(np.asarray(b.get("alpha", 1.0), np.float64), (len(P),))
            b["alpha"] = a * (1.0 - (1.0 - self.keep) * k * f)
            res.append(b)
        return res[0] if one else res


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
    """The choir's dark silhouette mask: off everywhere (round 8, Anthony: "choir still turns dark sometimes";
    f33: in far views the masks drew a dark slab at the church entrance). The singers always read as light."""
    return 0.0


def orch_mask(t):
    """The players' dark mask: off everywhere, as the choir's (they always glow)."""
    return 0.0


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
        return (float(self.g(t)) * (1.0 + 1.2 * _far(t, CHOIR_C)) * (1.0 + 0.5 * _sc(160.0, 205.0, t)) * end_glow(t)
                * rest(t, 0.62))

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
            near = 0.5 + 0.5 * _far(t, CHOIR_C)        # close up the lamps' glows pile into a white haze
            lamps = [dict(b[-2], alpha=b[-2]["alpha"] * min(0.7 * k, 1.8) * near,
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


# Anthony (2026-11-19): choir and orchestra as glowing blue sparkles; the instruments stay gold; every singer holds
# an open song book of gold light, like the instruments.
FIG_BLUE, FIG_BLUE2 = "#2f7dff", "#74b4ff"    # a clear saturated blue (round 9: "an easily distinguished blue")
BOOK_COL = "#ffb43c"                 # deep gold, apart from the blue singers (round 8)


def _book_local(rng, n=120):
    """An open book in the singer's frame (x right, y up, z forward), held at the chest: two pages in a
    shallow V, tipped toward the singer's eyes. Points on the page edges, a few on the pages, the spine."""
    w, h, open_deg, tip = 0.15, 0.22, 22.0, np.radians(52.0)
    pts = []
    for side in (-1.0, 1.0):
        a = np.radians(open_deg) * side
        u = np.array([side * np.cos(a), 0.0, -abs(np.sin(a))])     # across the page, away from the spine
        v = np.array([0.0, 1.0, 0.0])                                 # up the page
        # outline (the page's three free edges) and a light fill of lines of text
        t = np.linspace(0.0, 1.0, 14)
        rim = [np.outer(t * w, u) + 0.0 * v, np.outer(t * w, u) + h * v, w * u + np.outer(t * h, v)]
        lines = [np.outer(np.linspace(0.18, 0.88, 8) * w, u) + (0.25 + 0.1 * j) * h * v for j in range(6)]
        pts.append(np.concatenate(rim + lines))
    spine = np.outer(np.linspace(0.0, 1.0, 10) * h, np.array([0.0, 1.0, 0.0]))
    P = np.concatenate(pts + [spine]) - np.array([0.0, h / 2.0, 0.0])
    # tip the book back toward the singer (rotate about x)
    c, s_ = np.cos(tip), np.sin(tip)
    Rx = np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])
    return P @ Rx.T


class SongBooks:
    """An open gold song book in front of every singer of the choir (not the three soloists, whose hands
    gesture), at chest height, swaying with them and appearing as each singer forms."""

    def __init__(self, choir, height=1.16, ahead=0.27):
        self.choir = choir
        rng = np.random.default_rng(77)
        B = _book_local(rng)
        self.nb = len(B)
        P = CHOIR_P
        self.base = P[:, None, :] + _v(0.0, height, ahead)[None, None, :] + B[None, :, :]
        self.h = height
        d = np.hypot(P[:, 0] - 0.0, P[:, 2] - FACADE_Z)
        self.t_in = 21.3 + d / 9.0 + 0.4
        self.seed = rng.random(self.base.shape[:2])
        self.col = lin(BOOK_COL)

    def gain(self, t):
        return self.choir.gain(t)

    def sample(self, t):
        g = float(self.choir.g(t))
        if g <= 0.0:
            return []
        k = np.clip((t - self.t_in) / 0.8, 0.0, 1.0)
        if not k.any():
            return []
        P = self.base.copy()
        sw = getattr(self.choir, "_sw", None)
        if sw is not None and len(sw) == len(P):
            P[:, :, 0] += (sw * min(self.h / 1.7, 1.2) ** 2)[:, None]
        ch = _mx("choir", t) * _room(t)          # the books lift and brighten as the choir sings
        P[:, :, 1] += 0.035 * ch
        pos = P.reshape(-1, 3)
        a = np.repeat(k, self.nb) * 0.9
        glow = 0.85 + 0.25 * choir_glow(t) + 0.5 * ch
        return [dict(pos=pos, size=0.013, color=self.col * 1.7 * glow, alpha=np.minimum(a * 1.1, 1.0).astype(np.float32),
                     kind="spark", emit=1.9, twinkle=0.2, seed=self.seed.reshape(-1), dof=0.35),
                dict(pos=pos[:: 3], size=0.045, color=self.col * 0.45 * glow, alpha=(a[:: 3] * 0.30).astype(np.float32),
                     kind="soft", dof=0.35)]


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
        # slam 2's shot runs low through the players: they glow a third less there, so it does not white out
        s2 = 0.33 * _sc(SLAM2 - 0.1, SLAM2, t) * (1.0 - _sc(SLAM2 + 1.6, SLAM2 + 2.3, t))
        return float(self.g(t)) * (1.0 - (0.2 if t < SLAM3 else 0.0) * _far(t, ORCH_C)) * (1.0 - s2) * rest(t, 0.62)

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


# deep, saturated gold (round 8, Anthony: "hard to distinguish the instruments and books from the orchestra and
# choir"): pale amber went white beside the blue players; these stay gold at any brightness
INSTR_COL = {VIOLIN: "#ffab36", VIOLA: "#ffa22e", CELLO: "#ff9a2a", HARP: "#ffbe44", TIMPANI: "#ec8a3a",
             TRUMPET: "#ffc23e", TROMBONE: "#ffc23e"}


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
                lc.append(lin("#ffd98e") if sec != HARP else lin("#ffe6b0"))
        self.P, self.C = np.concatenate(pts), np.concatenate(cols)
        fam = {VIOLIN: 0, VIOLA: 0, CELLO: 0, HARP: 0, TRUMPET: 1, TROMBONE: 1, TIMPANI: 2}
        self.fam = np.concatenate([np.full(len(p), fam[sec]) for p, sec in zip(pts, ORCH_SEC)])
        self.F, self.FC = np.concatenate(fill), np.concatenate(fcol)
        self.LA, self.LB, self.LC = np.asarray(la), np.asarray(lb), np.asarray(lc)
        self.sec = ORCH_SEC
        self.bowed = [(k, VB if s == VIOLIN else VAB if s == VIOLA else CB) for k, s in enumerate(ORCH_SEC)
                      if s in (VIOLIN, VIOLA, CELLO)]
        self.timp = [k for k, s in enumerate(ORCH_SEC) if s == TIMPANI]
        self.bones = [k for k, s in enumerate(ORCH_SEC) if s == TROMBONE]
        hl = _hitters_local()
        hp, hd, hf = [], [], []
        for k, s in enumerate(ORCH_SEC):
            for q in hl.get(s, []):
                hp.append(_to_world(q, k, self.off)[0])
                hf.append(2 if s == TIMPANI else 1)
                if s == TIMPANI:
                    hd.append(_v(0.0, 1.0, 0.0))
                else:
                    a = np.radians(ORCH_FACE[k])
                    hd.append(_u(np.sin(a), 0.12, np.cos(a)))
        self.hp, self.hd, self.hf = np.asarray(hp), np.asarray(hd), np.asarray(hf)
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
        # each family answers its own sound: strings (and harps) glow with the strings, the brass with the brass
        # and its hits, the timpani flash on the timpani; held back under a phrase and where the music blazes
        rm = _room(t)
        m_str, m_bra, m_tim = _mx("strings", t) * rm, _mx("brass", t) * rm, _mx("timp", t) * rm
        lvl = np.array([1.0 + 0.9 * m_str, 1.0 + 1.1 * m_bra, 1.0 + 1.3 * m_tim])
        famk = lvl[self.fam][:, None]
        out = [dict(pos=self.P, size=0.018, color=self.C * famk * (1.35 + 0.6 * acc + 0.8 * hk), alpha=0.95 * g,
                    emit=1.9, kind="spark", twinkle=0.2, dof=0.6, fog=0.6),
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
        out.append(dict(pos=fa, pos2=fb, size=0.007, color=lin("#ffe8c4") * (1.2 + 0.8 * acc + 1.0 * m_str), alpha=0.95 * g,
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
        own = np.where(self.hf == 2, 0.45 * m_tim, 0.40 * m_bra)        # the bells flare with the brass, the heads with the timpani
        out.append(dict(pos=self.hp, size=0.35 + 0.5 * hk + 0.4 * own, color=lin(GOLD),
                        alpha=(0.10 + 0.12 * bp + 0.35 * hk + own) * g,
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
        return stage_k(t) * rest(t, 0.5)


# =========================================================================================================
# Light of the singing, and the snow of light in the breath
# =========================================================================================================
PERFORM = [(0.0, 21.5, "Orchestra (faint choir hum)"), (21.5, 29.8, "Choir and orchestra"), (29.8, 31.0, "Orchestra"),
           (31.0, 39.0, "Choir and orchestra"), (39.0, 41.0, "Orchestra"), (41.0, 247.5, "Choir and orchestra"),
           (247.5, 249.5, "Held breath"), (249.5, 259.95, "Choir and orchestra"), (259.95, 275.0, "Silence")]


class ChoirLight:
    """Light rising from the choir as they sing: more with the loudness, nothing while they are silent."""

    def gain(self, t):
        return (0.55 + 0.45 * _far(t, CHOIR_C)) * rest(t, 0.55)     # softer close up and at rest

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
        k *= 1.0 + 0.8 * _mx("choir", t) * _room(t)
        if k > 0.01:
            # every singer sends up four lights: two high, fine and sparkling, that climb higher with the high
            # voices; two low, warm and soft, that glow lower with the low voices
            hi = (np.arange(len(s)) % 2) == 0
            fh, fl = _mx("high", t) * _room(t), _mx("low", t) * _room(t)
            base = np.repeat(self.p, 4, axis=0) + _v(0.0, 1.62, 0.18)
            age = np.mod(t * (0.22 + 0.18 * s[:, 0]) + s[:, 1], 1.0)
            rise = np.where(hi, 3.2 * (1.0 + 0.7 * fh), 1.5)
            base = base - np.where(hi, 0.0, 0.55)[:, None] * _v(0.0, 1.0, 0.0)
            pos = base + np.stack([0.35 * (s[:, 2] - 0.5) * (0.4 + age), rise * age, 0.25 * (s[:, 3] - 0.5)], 1)
            amp = np.where(hi, 1.0 + 0.9 * fh, 0.7 + 1.0 * fl)
            col = np.where(hi[:, None], lin("#fff4dc")[None], lin("#ffc98a")[None])
            out.append(dict(pos=pos, size=np.where(hi, 0.018 + 0.014 * s[:, 2], 0.03 + 0.03 * s[:, 2]), color=col,
                            alpha=k * amp * np.sin(np.pi * age) ** 1.5, emit=2.2, kind="spark",
                            twinkle=0.7, seed=s[:, 3], dof=0.5))
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


# =========================================================================================================
# Comets that weave through the orchestra and spiral round the choir; the slams as a ray source
# =========================================================================================================
def _cphase(t):
    """A clock that runs with the music (beats, a little faster in loud passages)."""
    return beat_f(t) * _BP


def _comet_paths():
    O = PODIUM + _v(0.0, 0.0, -5.0)
    C = _v(0.0, SUMMIT, FACADE_Z + 2.5)

    def weave(t):        # an S through the orchestra, low over the players
        u = 0.32 * _cphase(t)
        return O + _v(10.0 * np.sin(u), 1.6 + 0.7 * np.sin(3.0 * u), 4.0 * np.sin(2.0 * u))

    def strings(t):      # low along the strings, back and forth
        u = 0.27 * _cphase(t) + 1.3
        return O + _v(9.5 * np.sin(u), 1.15 + 0.25 * np.sin(5.0 * u), 2.5 + 2.0 * np.cos(u))

    def choir_ring(t):   # round the choir, in front of the singers and behind them
        u = 0.36 * _cphase(t) + 2.0
        return C + _v(12.5 * np.cos(u), 2.4 + 1.2 * np.sin(2.0 * u), 4.2 * np.sin(u))

    def helix(t):        # a rising helix over the choir
        u = 0.55 * _cphase(t)
        h = np.mod(0.09 * _cphase(t), 1.0)
        return C + _v(6.0 * np.cos(u), 1.0 + 7.0 * h, 2.0 + 3.0 * np.sin(u))

    def brass(t):        # round the back rows, over the bells and the drums
        u = 0.4 * _cphase(t) + 4.0
        return PODIUM + _v(8.0 * np.sin(u), 3.0 + 0.6 * np.sin(2.0 * u), -10.6 + 2.0 * np.cos(u))
    return [weave, strings, choir_ring, helix, brass]


COMET_PATHS = _comet_paths()


class StageComet(Comet):
    """A comet that flies only while the camera is on the choir and orchestra. Near the lens it fades (it blew
    up into a white blur when a path passed within a few metres of the camera)."""
    wants_camera = True
    near = (1.5, 6.0)                                # gone within near[0] metres, whole beyond near[1]

    def gain(self, t):
        return rest(t, 0.55)

    def sample(self, t, cam=None):
        if not stage_view(t):
            return None
        out = super().sample(t)
        if not out or cam is None:
            return out
        res = []
        for b in out:
            P = np.asarray(b["pos"], np.float64).reshape(-1, 3)
            _xy, z = cam.project(P)
            f = np.clip((z - self.near[0]) / (self.near[1] - self.near[0]), 0.0, 1.0)
            f = f * f * (3.0 - 2.0 * f)
            b = dict(b, alpha=np.broadcast_to(np.asarray(b["alpha"], np.float64), (len(P),)) * f)
            res.append(b)
        return res


def blaze(t):
    """The choir and orchestra as a great light on the slams and the coda hit."""
    if not stage_view(t):
        return 0.0
    return min(0.45, 0.4 * hit_pulse(t, [SLAM1], rise=0.05, fall=0.8)
               + 0.22 * hit_pulse(t, [SLAM2, HIT["coda"]], rise=0.05, fall=0.6)   # slam 2, coda hit: washed with glare
               + 0.12 * hit_pulse(t, KICKS, fall=0.4))


# =========================================================================================================
# The hero singers (finely detailed, in the middle of the front row) and the conductor on the podium
# =========================================================================================================
HERO_ACTS = [("raise", SLAM1, 82.08, 86.7), ("raise", SLAM2, 162.86, 165.16), ("open", HIT["love"], 185.92, 188.27),
             ("raise", HIT["coda"], 199.62, 200.7), ("raise", HIT["final"], 249.43, 251.7)]


def _heroes():
    """Crowds of the hero singers: one acted crowd per gesture, each person shown only in its windows, and a
    singing crowd for the rest of the time."""
    n = len(HERO_P)
    out = []
    win = sorted((a, b) for _k, _h, a, b in HERO_ACTS)
    for kind in ("raise", "open"):
        acts = [(h, a, b) for k, h, a, b in HERO_ACTS if k == kind]
        if not acts:
            continue
        pl = np.concatenate([HERO_P for _ in acts])
        start = np.repeat([a - 0.02 for _h, a, _b in acts], n)
        until = np.repeat([b for _h, _a, b in acts], n)
        act = np.repeat([h - 0.08 for h, _a, _b in acts], n)
        c = GCrowd(gain=stage_k, places=pl, facing=0.0, kinds=(kind,), people=dict(woman=1.0), start=start,
                   until=until, act=act, fade=0.03, flash=0.0, color=FIG_BLUE, color2=FIG_BLUE2, bright=1.3,
                   points=22000, size=0.55, glints=0.01, dof=0.35, seed=31.0 + len(out), mirror=False,
                   scale=1.0)
        out.append(c)
    # singing: shown between the gesture windows
    gaps, t = [], 21.3
    for a, b in win:
        gaps.append((t, a))
        t = b
    gaps.append((t, 275.0))
    pl = np.concatenate([HERO_P for _ in gaps])
    start = np.repeat([g[0] for g in gaps], n)
    until = np.repeat([g[1] for g in gaps], n)
    sing = [dict(CHOIR_KINDS[0])]
    c = GCrowd(gain=stage_k, places=pl, facing=0.0, kinds=sing, start=start, until=until, fade=0.03, flash=0.0,
               color=FIG_BLUE, color2=FIG_BLUE2, bright=1.3, points=22000, size=0.55, glints=0.01, dof=0.35,
               seed=41.0, mirror=False, scale=1.0, light="#9fd0ff", lamp=(0.18, 1.0))
    out.append(c)
    return out


COND_P = PODIUM + _v(0.0, 0.25, 0.0)


def _beat_pattern(ph):
    """The conductor's right hand: a four-beat pattern (down, in, out, up) in the conductor's frame."""
    q = np.mod(ph, 1.0) * 4.0
    k = int(np.floor(q)) % 4
    f = q - np.floor(q)
    P = [_v(-0.05, 1.10, 0.42), _v(0.18, 1.22, 0.40), _v(-0.34, 1.22, 0.40), _v(-0.12, 1.48, 0.38)]
    a, b = P[k], P[(k + 1) % 4]
    e = f * f * (3.0 - 2.0 * f)
    return a + (b - a) * e + _v(0.0, 0.06 * np.sin(np.pi * f), 0.0)


class Conductor(Crowd):
    """The conductor on the podium, facing the orchestra, beating time on the beat with a baton of light."""

    def __init__(self, gain=None, **kw):
        kinds = [dict(shape="man", height=1.74, garment="coat", hair="short", motion="stand", loop=LOOP,
                      gest=[_gest("cdr", "R", _beat_pattern, palm=(0.0, -1.0, 0.3), fingers="pinch", look=True),
                            _gest("cdl", "L", lambda ph: _v(0.22, 1.20 + 0.04 * np.sin(2 * np.pi * ph), 0.30),
                                  palm=(-0.3, -0.2, 1.0), fingers="open")])]
        super().__init__(places=COND_P[None], kinds=kinds, facing=180.0, mirror=False, scale=1.0, **kw)
        self.facing[:] = np.radians(180.0)
        self.rate[:] = 0.0
        self.g = gain or stage_k

    def gain(self, t):
        return float(self.g(t))

    def sample(self, t):
        if self.g(t) <= 0.0:
            return []
        self.phase[:] = (beat_f(t) / 4.0) % 1.0
        return super().sample(t)


class Baton:
    """The conductor's baton, a line of light from the hand."""

    def sample(self, t):
        if stage_k(t) <= 0.0:
            return None
        h = _beat_pattern((beat_f(t) / 4.0) % 1.0)
        tip = h + _unit(_v(-0.1, 0.45, 0.9)) * 0.42
        w = lambda q: COND_P + _v(-q[0], q[1], -q[2])          # the conductor faces -z
        a, b = w(h), w(tip)
        return [dict(pos=a[None], pos2=b[None], size=0.008, color=lin("#fff6e6") * 1.5, alpha=1.0, emit=2.4,
                     kind="line", dof=0.5),
                dict(pos=b[None], size=0.05 + 0.08 * beat_pulse(t), color=lin("#fff1d8"), alpha=0.9, emit=3.0,
                     kind="soft", dof=0.5)]


# =========================================================================================================
# Grand: comets shooting up out of the orchestra on the slams, loops round the conductor and the heroes, a
# comet streaking past the lens along the strings, pillars of light round the stage, clouds banked beside it
# =========================================================================================================
BURSTS = [SLAM1, SLAM2, HIT["coda"]]


def _rocket(ts, i):
    """A comet shooting up out of the orchestra at ts, fanning out (i of nine)."""
    a = 2.0 * np.pi * i / 9.0
    base = PODIUM + _v(6.0 * np.sin(a) * 1.3, 2.0, -6.0 + 3.0 * np.cos(a))
    d = _unit(_v(0.6 * np.sin(a), 1.0, 0.25 * np.cos(a) + 0.15))

    def head(t):
        u = max(t - ts, 0.0)
        return base + d * (16.0 * (1.0 - np.exp(-u / 0.7)) + 4.0 * u) + _v(0.0, -2.0 * np.exp(-u / 0.2), 0.0)
    return head


def _loop_conductor(t):
    """Great loops of light round the conductor, like the promo's dancer's ribbon."""
    u = 0.9 * _cphase(t)
    return COND_P + _v(1.6 * np.cos(u), 1.3 + 1.0 * np.sin(2.0 * u), 1.6 * np.sin(u))


def _loop_heroes(t):
    """A figure of eight round the three hero singers."""
    u = 0.75 * _cphase(t) + 1.0
    c = HERO_P.mean(0)
    return c + _v(2.6 * np.sin(u), 1.4 + 0.8 * np.sin(3.0 * u), 0.9 + 0.9 * np.sin(2.0 * u))


def _lens_streak(t):
    """Low along the strings, past the lens of the strings' flight (verse 2)."""
    u = (t - 121.32) / 4.6
    return _v(14.0 - 30.0 * u, SUMMIT + 1.5 + 0.3 * np.sin(9.0 * u), FACADE_Z + 26.6 - 0.8 * np.sin(3.0 * u))


class StagePillars(Pillars):
    """Pillars of light that stand on the summit round the stage. The bright core is one continuous line of
    light (the shared pillar draws it as a row of soft dots 1.8 m apart, which read as dotted columns close
    up); the soft column and the pool stay as they are."""

    def sample(self, t):
        out = super().sample(t)
        if not out:
            return out
        res = []
        for j, b in enumerate(out):
            b = dict(b, pos=b["pos"] + _v(0.0, SUMMIT, 0.0))
            if j % 3 == 1 and len(b["pos"]) > 1:      # the core: a chain of line segments, no gaps
                P = b["pos"]
                a = np.broadcast_to(np.asarray(b["alpha"], np.float64), (len(P),))
                b = dict(pos=P[:-1], pos2=P[1:], size=self.width * 0.07, color=b["color"],
                         alpha=np.minimum(1.6 * 0.5 * (a[:-1] + a[1:]), 1.0), emit=2.6, kind="line", dof=0.3)
            res.append(b)
        return res


def pillar_k(t):
    """Pillars slam down round the stage on the slams, and stand through the held breath and the final rise."""
    if not stage_view(t):
        return 0.0
    k = 0.0
    for h in BURSTS:
        k = max(k, _sc(h - 0.05, h + 0.25, t) * (1.0 - _sc(h + 2.5, h + 4.2, t)))
    k = max(k, 0.7 * _sc(247.5, 249.0, t) * (1.0 - _sc(252.0, 254.0, t)))
    return 0.55 * k * (1.0 - 0.4 * _sc(SLAM2 - 0.1, SLAM2, t) * (1.0 - _sc(SLAM2 + 2.0, SLAM2 + 2.5, t)))


def cloud_k(t):
    return 0.55 * stage_view(t) * (0.6 + 0.4 * intensity(t))


class SoundAnswers:
    """Each sound of the music answered by its own light in the stage shots (round 9, Anthony: "way more effects
    consistently happening to match each different sound"): the timpani as low gold shock rings running across
    the stage floor from the drums, the high voices as fine sparkles above the front rows (the sopranos), the low
    voices as a deep blue swell round the back rows (the basses). (The strings along the bows, the brass flares
    off the bells and the choir's rising breath of light are in Instruments, SongBooks and ChoirLight.)"""

    def __init__(self, inst):
        self.tc = inst.hp[inst.hf == 2].mean(0) if (inst.hf == 2).any() else PODIUM + _v(0.0, 0.0, -10.0)
        self.tc = np.array([self.tc[0], SUMMIT + 0.06, self.tc[2]])
        z = CHOIR_P[:, 2]
        self.hi = CHOIR_P[z >= np.quantile(z, 0.65)]
        self.lo = CHOIR_P[z <= np.quantile(z, 0.35)]
        r = np.random.default_rng(81)
        self.hs = r.random((len(self.hi) * 3, 4))
        self.ang = np.linspace(0.0, 2.0 * np.pi, 360, endpoint=False)
        self.rs = r.random(360)
        self.hits = None

    def gain(self, t):
        return stage_k(t) * rest(t, 0.6)

    def sample(self, t):
        if not stage_view(t) or stage_k(t) <= 0.0:
            return None
        rm = _room(t)
        out = []
        if self.hits is None:
            try:
                import songs.s11_music_fx as MF
                self.hits = MF.timp_hits(0.5)
            except Exception:  # noqa: BLE001
                self.hits = []
        for th, st in self.hits:                     # timpani: a gold ring runs out across the floor
            u = t - th
            if 0.0 <= u < 1.4:
                rad = 0.6 + 11.0 * (1.0 - np.exp(-u / 0.45))
                P = self.tc[None, :] + np.stack([rad * np.sin(self.ang), np.zeros(360), rad * np.cos(self.ang)], 1)
                a = st * np.exp(-u / 0.45) * (1.0 - _sc(1.0, 1.4, u)) * (0.5 + 0.5 * rm)
                out.append(dict(pos=P, size=0.07 + 0.008 * rad, color=lin("#ffc062"), alpha=0.7 * a, kind="spark",
                                emit=2.4, twinkle=0.3, seed=self.rs, reflect=False))
                out.append(dict(pos=P[::8], size=0.9, color=lin("#ff9e3a"), alpha=0.06 * a, kind="soft", emit=1.4,
                                reflect=False))
        fh = _mx("high", t) * rm                     # high voices: sparkles above the front rows
        if fh > 0.03:
            hs = self.hs
            base = np.repeat(self.hi, 3, axis=0)
            ph = np.mod(t * (0.6 + 0.5 * hs[:, 0]) + hs[:, 1], 1.0)
            pos = base + np.stack([0.5 * (hs[:, 2] - 0.5), 2.0 + 0.9 * ph, 0.4 * (hs[:, 3] - 0.5)], 1)
            out.append(dict(pos=pos, size=0.02 + 0.02 * hs[:, 2], color=lin("#eaf4ff"),
                            alpha=fh * np.sin(np.pi * ph) ** 2, emit=2.6, kind="spark", twinkle=1.0, seed=hs[:, 3]))
        fl = _mx("low", t) * rm                      # low voices: a deep blue swell round the back rows
        if fl > 0.03:
            pos = self.lo + _v(0.0, 1.0, 0.0)
            out.append(dict(pos=pos, size=1.5 + 0.6 * fl, color=lin("#2457ff"), alpha=0.10 * fl, kind="soft",
                            emit=1.5))
        return out or None


def add(scene):
    choir = Choir(places=CHOIR_P, facing=0.0, kinds=CHOIR_KINDS,
                  start=dict(t=21.3, center=(0.0, FACADE_Z), speed=9.0), color=FIG_BLUE, color2=FIG_BLUE2,
                  bright=2.7, points=3200, size=1.1, flash=1.2, glints=0.004, dof=0.35, seed=3.0,
                  light="#9fd0ff", lamp=(0.20, 1.0), scale=(0.97, 1.03))
    # no dark mask: the singers always glow (f28, f33); behind a phrase they glow softer (f17)
    scene.add("choir", BoxGuard(choir, keep=0.35))
    scene.add("choir hearts", BoxGuard(ChoirHearts(choir), keep=0.4))
    scene.add("song books", SongBooks(choir))
    orch = Players(start=dict(t=2.2, dur=7.0), color=FIG_BLUE, color2=FIG_BLUE2, bright=3.6, points=3400,
                   size=1.2, glints=0.006, dof=0.35, seed=4.0)
    scene.add("orchestra", BoxGuard(orch, keep=0.35))     # no dark mask: the players always glow
    scene.add("risers", Risers())
    inst = Instruments()
    scene.add("instruments", inst)
    scene.add("sound answers", BoxGuard(SoundAnswers(inst), keep=0.1), reflect=False)
    scene.add("choir light", BoxGuard(ChoirLight(CHOIR_ALL), keep=0.2))
    scene.add("snow", Snow())
    for i, c in enumerate(_heroes()):
        scene.add("hero singers %d" % i, c)
    cond = Conductor(start=dict(t=2.2, dur=0.5), color=FIG_BLUE, color2=FIG_BLUE2, bright=1.4, points=20000,
                     size=0.6, glints=0.01, dof=0.35, seed=51.0)
    scene.add("conductor", cond)
    scene.add("baton", Baton())
    for i, f in enumerate(COMET_PATHS):
        col = COL9[(2 * i + 1) % 9]
        scene.add("stage comet %d" % i, BoxGuard(StageComet(f, col, 0.0, 260.0, trail=1.3, width=0.22, bright=1.0,
                                                            fade=0.5, n=70, seed=60 + i)))
    for j, ts in enumerate(BURSTS):
        for i in range(9):
            scene.add("slam rocket %d %d" % (j, i), BoxGuard(StageComet(
                _rocket(ts, i), COL9[i], ts - 0.05 if j == 0 else ts + 0.22, ts + 3.6,   # slam 2, coda hit: after the flash
                trail=1.2, width=0.62 if j == 0 else 0.5, bright=0.85 if j == 0 else 0.55, fade=0.3, n=170, sparks=False,
                seed=100 + 9 * j + i), when=lambda t: 1.0))    # always out of the words' box (they land on the slam)
    scene.add("loop conductor", BoxGuard(StageComet(_loop_conductor, COL9[6], 0.0, 260.0, trail=1.6, width=0.18, n=80,
                                           seed=131)))
    heroes = StageComet(_loop_heroes, COL9[3], 0.0, 260.0, trail=1.8, width=0.2, n=80, seed=132)
    heroes.near = (5.0, 14.0)        # it circles the soloists the close choir shots sit beside (white burst 1:19.5)
    scene.add("loop heroes", BoxGuard(heroes))
    scene.add("lens streak", StageComet(_lens_streak, COL9[5], 121.32, 125.92, trail=0.5, width=0.35, n=50,
                                        fade=0.2, seed=133))
    bases = [(-20.0, FACADE_Z + 6.0), (20.0, FACADE_Z + 6.0), (-17.0, FACADE_Z + 24.0), (17.0, FACADE_Z + 24.0),
             (-9.0, FACADE_Z + 36.0), (9.0, FACADE_Z + 36.0)]
    scene.add("stage pillars", BoxGuard(StagePillars(bases, top=160.0, color="#ffe6c0", width=1.6, gain=pillar_k),
                                        keep=0.15))
    for i, (x, z) in enumerate(()):          # no clouds at the stage: they crowded the choir and orchestra
        scene.add("stage clouds %d" % i, CloudBank(_v(x, SUMMIT - 4.0, z), size=(26.0, 16.0, 30.0), puffs=14,
                                                   seed=70 + i, gain=cloud_k, bright=0.8))
    add_light(COMET_PATHS[0], COL9[1], lambda t: 1.1 * stage_view(t) * (0.8 + 0.4 * beat_pulse(t)), radius=5.0)
    add_rays(lambda t: _v(0.0, SUMMIT + 3.2, FACADE_Z + 1.0), lambda t: blaze(t) * (1.0 if stage_view(t) else 0.0),
             color="#ffe8c0", size=0.7)          # only in stage shots (it glared over the dancers)
