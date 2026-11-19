"""Song 11 v2: from thanks to Mother to the end: hearts rising, light gathering at the horizon, the
sun rising over Zion, the orchestra on clouds of light, everyone on the summit, the world finale on the Earth, the
held breath, the last chord and the end card's Earth.

Owned by the coda thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
from songs.s11_stage import Instruments, ORCH_P  # noqa: E402

Y, FZ, G = SUMMIT, FACADE_Z, GLOBE_C

# Two leftovers of the base song (songs.s03_original) show over the world finale: its title words ("Beginning of
# Peace / The Words of Mother's Love", formed at 3:45.9 and held) and its tagline (3:56 to 4:00.5). The core
# should switch them off (TITLE form/hold and TAGLINE t0/t1 to 1e9); until it does, they are switched off here.
import songs.s03_original as _B  # noqa: E402
for _d, _ks in ((_B.TITLE, ("form", "hold", "star")), (_B.TAGLINE, ("t0", "t1"))):
    for _k in _ks:
        if _k in _d:
            _d[_k] = 1e9 + (1.0 if _k in ("hold", "t1") else 0.0)

SKY_C = SKY_STAGE + _v(0.0, 1.0, -5.0)       # the middle of the sky orchestra

SHOTS = [
    # thanks to Mother: hearts rise; the last build: light gathers at the horizon behind Zion
    dict(name="hearts_rise", kind="local", t0=188.27, t1=201.73, fov=52.0, aperture=0.0,
         keys=[(188.27, _v(34.0, 74.0, -120.0), ZC + _v(0.0, Y + 6.0, 0.0)),
                          (201.73, _v(14.0, 58.0, -36.0), ZC + _v(0.0, Y + 12.0, -60.0))]),
    # the coda: the sun rises over Mount Zion (the camera cranes up as it comes)
    dict(name="sunrise", kind="local", t0=201.73, t1=205.98, fov=54.0, aperture=0.0,
         keys=[(201.73, _v(0.0, 14.0, 110.0), ZC + _v(0.0, Y + 6.0, -40.0)),
                          (205.98, _v(0.0, 30.0, 86.0), ZC + _v(0.0, Y + 12.0, -40.0))]),
    # the orchestra on clouds of light round the rising sun (the sun at the right edge, clear of the words)
    dict(name="sky_stage", kind="sky", t0=205.98, t1=211.6, fov=50.0, aperture=0.0,
         keys=[(205.98, SKY_C + _v(6.0, 2.8, 15.0), SKY_C + _v(0.0, 1.1, -1.5)),
                         (211.6, SKY_C + _v(4.0, 2.4, 12.0), SKY_C + _v(0.0, 1.4, -1.5))]),
    # third climb: the summit, everyone, the church of light, the sun (at the right edge)
    dict(name="summit", kind="local", t0=211.6, t1=224.03, fov=54.0, aperture=0.0,
         keys=[(211.6, _v(8.0, Y + 9.0, FZ + 100.0), _v(0.0, Y + 18.0, FZ - 13.0)),
                         (224.03, _v(5.0, Y + 7.0, FZ + 90.0), _v(0.0, Y + 21.0, FZ - 13.0))]),
    # the world finale
    dict(name="earth_finale", kind="globe", t0=224.03, t1=238.8, fov=48.0, aperture=0.0,
         keys=[(224.03, _gcam(150.0, 30.0), G + _v(0, 10, 0)), (226.6, _gcam(146.0, 27.0), G + _v(0, 16, 0)),
                (228.6, _gcam(142.0, 24.0), G + _v(0, 50, 0)), (238.8, _gcam(156.0, 12.0), G + _v(0, 48, 0))]),
    # the last chord: out to the whole Earth glowing, the end card
    dict(name="earth_end", kind="globe", t0=254.07, t1=TOTAL + 1.0, fov=46.0, aperture=0.0,
         keys=[(254.07, _gcam(150.0, 6.0), G), (TOTAL + 1.0, _gcam(185.0, 8.0), G)]),
]


class RisingHearts:
    """Thanks to Mother (3:09.5 to 3:17): hearts in the nine colours rise from everyone on the mountain."""
    wants_camera = True

    def __init__(self):
        r = np.random.default_rng(121)
        n = 220
        k = r.integers(0, N_TIER, n)
        a = np.radians(r.uniform(-75.0, 75.0, n))
        rr = np.asarray([tier_r(i) - 3.0 - 20.0 * r.random() for i in k])
        self.p0 = np.stack([ZC[0] + rr * np.sin(a), np.asarray([tier_y(i) for i in k]) + 2.0, ZC[2] + rr * np.cos(a)], 1)
        self.t0 = 189.5 + 7.0 * r.random(n)
        self.sz = 2.2 + 2.6 * r.random(n)
        self.v = 5.0 + 4.0 * r.random(n)
        self.col = np.asarray([lin(COL9[i % 9]) for i in range(n)])
        from p3d.brand_hearts import heart_points
        self.h = heart_points(36)
        self.ph = r.random(n) * 6.0

    def sample(self, t, cam=None):
        if cam is None or local_k(t) <= 0.0 or not (189.0 <= t < 202.0) or shot_name(t) != "hearts_rise":
            return None
        u = t - self.t0
        on = u > 0.0
        if not on.any():
            return None
        rgt, up, _f = cam.basis()
        u = u[on]
        c = self.p0[on] + up[None, :] * 0.0 + _v(0.0, 1.0, 0.0) * (self.v[on] * u)[:, None]
        c = c + rgt[None, :] * (1.5 * np.sin(0.9 * u + self.ph[on]))[:, None]
        a = _ss(0.0, 0.5, u) * (1.0 - _ss(5.0, 9.0, u)) * (1.0 - _sc(200.5, 201.7, t))
        sz = self.sz[on]
        hx, hy = self.h[:, 0], self.h[:, 1]
        P = (c[:, None, :] + sz[:, None, None] * (hx[None, :, None] * rgt[None, None, :] + hy[None, :, None] * up[None, None, :]))
        m = len(self.h)
        return [dict(pos=P.reshape(-1, 3), size=np.repeat(0.09 * sz, m), color=np.repeat(self.col[on], m, axis=0),
                     alpha=np.repeat(a, m), emit=3.0, kind="spark"),
                dict(pos=c, size=2.2 * sz, color=self.col[on], alpha=0.18 * a, emit=1.6, kind="soft")]


class Horizon:
    """The last build (3:17.2 to 3:21.7): light gathers along the horizon behind Zion, where the sun will rise."""

    def __init__(self):
        r = np.random.default_rng(131)
        n = 3000
        a = np.radians(163.0 + r.normal(0.0, 22.0, n))
        d = 2600.0 + 300.0 * r.random(n)
        self.P = np.stack([d * np.sin(a), 4.0 + 50.0 * r.random(n) ** 3, d * np.cos(a)], 1)
        self.s = r.random(n)

    def sample(self, t):
        if local_k(t) <= 0.0 or not (195.0 <= t < 206.0) or stage_view(t):
            return None
        k = _sc(196.5, 201.6, t) * (1.0 - 0.6 * _sc(202.0, 206.0, t))
        return [dict(pos=self.P, size=7.0, color=lin("#ffd29a"), alpha=0.35 * k, emit=2.0, kind="soft", dof=0.0),
                dict(pos=self.P[::3], size=2.2, color=lin("#fff0d0"), alpha=0.7 * k, emit=3.0, kind="spark",
                     twinkle=0.6, seed=self.s[::3], dof=0.0)]


SKY_OFF = SKY_STAGE - SQUARE


def sky_k(t):
    return 1.0 if shot_kind(t) == "sky" else 0.0


def _sun_dir_coda(el=4.0, az=163.0):
    e, a = np.radians(el), np.radians(az)
    return _v(np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e))


class Clouds:
    """The clouds of light the orchestra plays on, round the rising sun (the coda): a low billow of cloud under
    the players (kept thin, so the players read on it), a sea of cloud far below in rose, violet and gold, and
    banks of cloud lit gold round the sun."""

    def __init__(self):
        r = np.random.default_rng(141)
        # the billow under the orchestra: an ellipse round the players, thickest at its rim
        n = 5200
        a = 2 * np.pi * r.random(n)
        u = np.sqrt(r.random(n))
        u = 0.55 + 0.45 * u                      # most of the cloud lies round the players, not under them
        bill = 0.6 * np.sin(3.0 * a + 1.3) + 0.4 * np.sin(7.0 * a)
        rx, rz = 20.0 + 3.0 * bill, 10.0 + 2.0 * bill
        self.P = np.stack([SKY_C[0] + rx * u * np.sin(a),
                           SKY_STAGE[1] - 1.2 - 2.4 * u ** 3 - 1.2 * r.random(n) ** 2 + 1.0 * (u - 0.55),
                           SKY_C[2] + rz * u * np.cos(a)], 1)
        self.s = r.random(n)
        self.pu = u
        warm = np.asarray([lin("#ffe2c8"), lin("#ffc8d0"), lin("#e8d0ff")])
        self.pc = warm[r.integers(0, 3, n)]
        # the sea of cloud far below, coloured by where it lies against the sun
        m = 2600
        a = 2 * np.pi * r.random(m)
        rr = 80.0 + 520.0 * np.sqrt(r.random(m))
        self.F = np.stack([SKY_STAGE[0] + rr * np.sin(a), SKY_STAGE[1] - 40.0 - 30.0 * r.random(m),
                           SKY_STAGE[2] + rr * np.cos(a)], 1)
        sd = _sun_dir_coda()
        toward = np.clip((np.sin(a) * sd[0] + np.cos(a) * sd[2]), -1.0, 1.0)
        w = (0.5 + 0.5 * toward)[:, None] ** 2
        cool = np.where((r.random(m) < 0.5)[:, None], lin("#8a5aa0")[None, :], lin("#5a4aa8")[None, :])
        self.fc = cool * (1.0 - w) + lin("#e8a070")[None, :] * w
        self.fs = 16.0 + 14.0 * r.random(m)
        # banks of cloud round the sun, far away, lit gold on their sunward side
        k = 1400
        az = 163.0 + r.normal(0.0, 14.0, k)
        el = -1.0 + 6.0 * r.random(k) ** 1.5
        dd = 900.0 + 300.0 * r.random(k)
        e, aa = np.radians(el), np.radians(az)
        self.B = SKY_STAGE + np.stack([np.sin(aa) * np.cos(e), np.sin(e), np.cos(aa) * np.cos(e)], 1) * dd[:, None]
        near = np.exp(-((az - 163.0) / 10.0) ** 2)[:, None]
        self.bc = lin("#e6a0b8")[None, :] * (1.0 - near) + lin("#ffd08a")[None, :] * near
        self.bs = 30.0 + 40.0 * r.random(k)

    def sample(self, t):
        if sky_k(t) <= 0.0:
            return None
        drift = _v(0.4 * np.sin(0.2 * t), 0.0, 0.0)
        pulse = 1.0 + 0.25 * beat_pulse(t)
        rim = 0.25 + 0.75 * self.pu ** 2
        return [dict(pos=self.P + drift, size=1.0 + 1.2 * self.s, color=self.pc, alpha=0.03 * rim, emit=1.0,
                     kind="soft", seed=self.s, dof=0.0),
                dict(pos=self.P[::3] + drift, size=0.05, color=lin(GOLD2), alpha=0.55 * pulse, emit=2.0,
                     kind="spark", twinkle=0.8, seed=self.s[::3]),
                dict(pos=self.F, size=self.fs, color=self.fc, alpha=0.04, emit=1.0, kind="soft", dof=0.0,
                     reflect=False),
                dict(pos=self.B, size=self.bs, color=self.bc, alpha=0.06, emit=1.2, kind="soft", dof=0.0,
                     reflect=False)]


def summit_k(t):
    """Everyone on the summit: from the coda's sunrise to the last chord (not in the close stage shots)."""
    if globe_view(t) or not (201.73 <= t < 254.07):
        return 0.0
    return 1.0


def _summit_places(n=700, seed=151):
    """Everyone on the summit, in the open ground (the church thread's buildings fill the rest of the plateau):
    the great avenue down from the square (|x| < 13), and both wings of the square beside the orchestra."""
    r = np.random.default_rng(seed)
    pts = []
    n_av = int(n * 0.62)
    while len(pts) < n_av:
        x = r.uniform(-13.0, 13.0)
        z = r.uniform(FACADE_Z + 22.0, FACADE_Z + 80.0)
        if abs(x) < 1.2 or np.hypot(x - ZC[0], z - ZC[2]) > R_TOP - 9.0:
            continue
        pts.append((x, SUMMIT, z))
    while len(pts) < n:
        x = r.uniform(16.0, 38.0) * (1.0 if r.random() < 0.5 else -1.0)
        z = r.uniform(FACADE_Z - 8.0, FACADE_Z + 20.0)
        pts.append((x, SUMMIT, z))
    return np.asarray(pts)


class Gather:
    """The held breath (4:07.5 to 4:09.5): sparks gather above the choir, then open on the final rise."""

    def __init__(self):
        r = np.random.default_rng(161)
        n = 1600
        d = r.normal(0.0, 1.0, (n, 3))
        self.d = d / np.linalg.norm(d, axis=1, keepdims=True)
        self.r = 8.0 + 22.0 * r.random(n)
        self.s = r.random(n)
        self.c = _v(0.0, SUMMIT + 10.0, FACADE_Z + 2.0)

    def sample(self, t):
        if not (245.5 <= t < 252.0) or local_k(t) <= 0.0:
            return None
        if t < HIT["final"]:
            u = _sc(245.5, HIT["final"], t)
            rr = self.r * (1.0 - 0.94 * u)
            a = _sc(245.5, 246.5, t) * (0.6 + 0.4 * u)
        else:
            u = t - HIT["final"]
            rr = self.r * (0.06 + 0.6 * u)
            a = np.exp(-u / 0.9)
        P = self.c + self.d * rr[:, None]
        if t < HIT["final"]:
            core = _sc(246.0, HIT["final"], t)
        else:
            core = np.exp(-(t - HIT["final"]) / 0.5)
        return [dict(pos=P, size=0.16, color=lin("#ffcf70"), alpha=a, emit=4.0, kind="spark", twinkle=0.7, seed=self.s,
                     dof=0.0),
                dict(pos=self.c[None, :], size=3.0 + 5.0 * core, color=lin("#ffd890"), alpha=0.35 * core, emit=2.0,
                     kind="soft", dof=0.0)]


def _heart_sprites(b, cam):
    """A "heart" batch (the repo engine's heart sprites) as hearts of points for the pinned engine, which has no
    heart kind: each heart is a filled heart of sparks facing the camera, in its exact colour."""
    from p3d.brand_hearts import heart_points
    if not hasattr(_heart_sprites, "h"):
        _heart_sprites.h = np.concatenate([heart_points(40), heart_points(60, fill=True)])
    h = _heart_sprites.h
    rgt, up, _f = cam.basis()
    pos = np.asarray(b["pos"], np.float64)
    n, m = len(pos), len(h)
    sz = np.broadcast_to(np.asarray(b["size"], np.float64), (n,))
    P = pos[:, None, :] + sz[:, None, None] * (h[None, :, 0, None] * rgt[None, None, :] + h[None, :, 1, None] * up[None, None, :])
    out = dict(b)
    out.update(pos=P.reshape(-1, 3), size=np.repeat(0.11 * sz, m), kind="spark",
               alpha=np.repeat(np.broadcast_to(np.asarray(b["alpha"], np.float64), (n,)), m))
    for k in ("color", "seed"):
        v = np.asarray(b.get(k, 0.0))
        if v.ndim >= 1 and len(v) == n:
            out[k] = np.repeat(v, m, axis=0)
    return out


def _patch_globe_hearts():
    """The core's Earth (GLOBE) draws its hearts with kind "heart", which the pinned engine does not know (the
    frame fails from 3:46 on). Until the core changes, the coda turns them into hearts of points here."""
    if getattr(GLOBE, "_coda_hearts", False):
        return
    orig = GLOBE._hearts

    def hearts(t, cam, *a, **kw):
        out = orig(t, cam, *a, **kw)
        return [(_heart_sprites(b, cam) if b.get("kind") == "heart" else b) for b in out]
    GLOBE._hearts = hearts
    GLOBE._coda_hearts = True
    # the world finale: the Earth turns so that Zion (Korea) faces us while the light of every land flows to it
    # (without this, 3:44 to 3:59 shows the Atlantic and Zion is on the far side)
    front = GLOBE._front_at

    def front_at(t):
        if 224.03 <= t < 254.0:
            return ZION_LL[1] - 25.0 + 1.2 * (t - 231.0)
        return front(t)
    GLOBE._front_at = front_at


SHAFTS = []


def add(scene):
    _patch_globe_hearts()
    scene.add("rising hearts", RisingHearts())
    scene.add("horizon", Horizon())
    # the orchestra on clouds of light round the rising sun
    scene.add("clouds", Clouds())
    scene.add("sky orchestra", GCrowd(gain=sky_k, places=ORCH_P + SKY_OFF, facing=0.0, kinds=("sit",),
                                      people=dict(woman=1.0, man=1.0), start=0.0, color=CRYSTAL, color2="#ffffff",
                                      bright=2.3, size=1.7, points=1600, glints=0.012, seed=4.0))
    scene.add("sky instruments", Instruments(offset=SKY_OFF, gain=sky_k))
    # everyone on the summit, from the coda's sunrise to the last chord
    scene.add("summit", GCrowd(gain=summit_k, places=_summit_places(), facing=180.0,
                               kinds=(("raise", 3.0), ("stand", 1.0), ("cheer", 1.5)),
                               people=dict(woman=1.0, man=1.0, child=0.2),
                               start=dict(t=201.0, center=(0.0, FACADE_Z), speed=40.0), color="#ffc870",
                               color2="#fff2d8", bright=1.6, size=2.6, points=500, glints=0.012, seed=41.0))
    scene.add("gather", Gather())
