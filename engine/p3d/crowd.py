"""Crowds of hundreds of people of light, cheaply: a few prototype bodies are baked once (a loop of frames each)
and every person in the crowd is an instance of one of them, placed, turned, sized and started at its own time.

    from p3d.crowd import Crowd
    crowd = Crowd(n=400, area=dict(center=(0, -20), radius=(6, 60)), facing=lambda x, z: 180.0,
                  kinds=("stand", "raise", "clap"), start=dict(t=10.0, center=(0, -6), speed=12.0))
    scene.add("crowd", crowd)

KEYS
  n          how many people (or give `places`)
  places     (K, 2) or (K, 3) points on the ground: where they stand (default: spread over `area`)
  area       dict(center=(x, z), radius=(r0, r1), arc=(a0, a1) degrees, from +z toward +x): a ring or a
             full disc of people; they are spread evenly with a little jitter
  facing     degrees for all, (K,) one each, a function (x, z) -> degrees, or "center" (all face the
             area's centre) or "out"
  kinds      the prototypes people are drawn from (each is baked once), any of:
               "stand", "walk", "run", "raise" (arms raised high), "clap", "bow", "pray", "open" (arms open),
               "sit" (on the ground), "child" (a child standing), "child_run"
             or (name, weight) pairs; or a list of dicts of Body keys with a "loop" (seconds) for your own
  shapes     which body shapes a kind may use, default ("woman", "man"); garments are mixed
  start      when each person appears: a number, (K,) times, or dict(t, center=(x, z), speed) (a wave that
             wakes them as it passes, metres per second) or dict(t, dur) (spread at random over dur)
  until      when they go (a number or (K,)); fade: seconds each way; flash: how bright a new person flares
  walk       for walkers and runners: metres per second along their facing (0 keeps them on the spot)
  points     points per person (default 2600: people in the middle and far distance)
  scale      size (1 life size) or (lo, hi) for a spread
  color, color2, bright, size (grain), twinkle, glints (share of four-point glints)
  seed       another crowd

Everything is a pure function of time. Baking costs a few seconds per prototype the first time the crowd is
sampled (in each render process); after that a frame of 400 people costs a few hundredths of a second.
"""
import numpy as np

from . import bodymath as bm
from .api import lin

KINDS = dict(
    stand=dict(motion="stand", loop=4.0),
    walk=dict(motion="walk", loop="cycle"),
    run=dict(motion="run", loop="cycle"),
    raise_=dict(motion="stand", gesture=[(0.0, 1e9, "raise", dict(ease=0.01))], loop=4.0),
    clap=dict(motion="stand", gesture=[(0.0, 1e9, "clap", dict(ease=0.01, period=0.5, height=0.6))], loop=2.0),
    bow=dict(motion="stand", gesture=[(0.0, 1e9, "bow", dict(ease=0.01, amount=40.0))], loop=4.0),
    pray=dict(motion="stand", gesture=[(0.0, 1e9, "pray", dict(ease=0.01))], loop=4.0),
    open=dict(motion="stand", gesture=[(0.0, 1e9, "open_arms", dict(ease=0.01, lift=0.4))], loop=4.0),
    sit=dict(motion=[(0.0, "sit", dict(dur=0.01))], loop=4.0),
)
GARMENTS = dict(woman=("dress", "robe"), man=("tunic", "coat"), child=("tunic", "dress"))
PRE = 2.5           # seconds simulated before a loop is taken (the garments settle)
FPS = 30.0


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


class _Proto:
    """One baked prototype: positions (F, P, 3) in its own place (feet at the origin, facing +z)."""

    def __init__(self, spec, points, seed):
        self.spec, self.points, self.seed = spec, points, seed
        self.pos = None

    def bake(self):
        if self.pos is not None:
            return
        from .body import Body
        sp = dict(self.spec)
        loop = sp.pop("loop")
        kw = dict(look="glitter", points=self.points, seed=self.seed, hair="default")
        kw.update(sp)
        b = Body(**kw)
        if loop == "cycle":
            c = b.actor.mo.clips[kw["motion"]]
            loop = c.T * max(1, int(round(1.0 / c.T)))
            cross = 0.0
        else:
            cross = min(0.6, loop * 0.25)
        F = max(int(round(loop * FPS)), 2)
        dt = loop / F
        X = int(round(cross / dt))
        frames = []
        for k in range(F + X):
            t = PRE + k * dt
            p, _n = b.points_at(t)
            f = b.actor.frame(t)
            o = f["origin"]
            q = bm.qy(-f["heading"])
            frames.append(bm.qrot(q, (p - o).astype(np.float64)).astype(np.float32))
        P = np.stack(frames)
        if X:
            w = (np.arange(X) / X)[:, None, None]
            P[:X] = P[F:F + X] * (1 - w) + P[:X] * w
        self.pos = P[:F]
        self.dt = dt
        self.F = F
        cl = b.cloud
        self.size = cl["size"].astype(np.float32)
        self.seed_pt = cl["seed"].astype(np.float32)
        self.part = cl["part"]
        self.edge = cl.get("edge", np.zeros(len(self.size))).astype(np.float32)
        self.height = b.rig.height


class Crowd:
    """Hundreds of people of light (see the module text)."""

    def __init__(self, n=200, places=None, area=None, facing=0.0, kinds=("stand",), shapes=("woman", "man"),
                 start=0.0, until=None, fade=0.6, flash=0.6, walk=0.0, points=2600, scale=1.0, color="#f2b865",
                 color2="#ffe6b8", bright=1.0, size=1.0, twinkle=0.8, glints=0.002, seed=1.0):
        rng = np.random.default_rng(int(seed * 1000) + 7)
        self.seed = float(seed)
        # ---- where
        if places is not None:
            pl = np.asarray(places, np.float64)
            if pl.shape[1] == 2:
                pl = np.stack([pl[:, 0], np.zeros(len(pl)), pl[:, 1]], axis=1)
            n = len(pl)
        else:
            ar = dict(center=(0.0, 0.0), radius=(2.0, 20.0), arc=(0.0, 360.0))
            ar.update(area or {})
            c = np.asarray(ar["center"], np.float64)
            r0, r1 = ar["radius"]
            a0, a1 = np.radians(ar["arc"][0]), np.radians(ar["arc"][1])
            # even spread over the ring (golden angle), jittered
            k = np.arange(n) + 0.5
            u = k / n
            r = np.sqrt(r0 * r0 + (r1 * r1 - r0 * r0) * u)
            th = a0 + ((k * 2.399963) % (2 * np.pi)) / (2 * np.pi) * (a1 - a0)
            r = r + rng.uniform(-0.35, 0.35, n)
            th = th + rng.uniform(-0.02, 0.02, n)
            pl = np.stack([c[0] + r * np.sin(th), np.zeros(n), c[1] + r * np.cos(th)], axis=1)
            self.center = c
        self.n = n
        self.place = pl
        # ---- which way
        if callable(facing):
            fc = np.array([float(facing(p[0], p[2])) for p in pl])
        elif isinstance(facing, str):
            c = getattr(self, "center", pl.mean(0)[[0, 2]])
            fc = np.degrees(np.arctan2(c[0] - pl[:, 0], c[1] - pl[:, 2]))
            if facing == "out":
                fc = fc + 180.0
        else:
            fc = np.broadcast_to(np.asarray(facing, np.float64), (n,)).astype(np.float64)
        self.facing = np.radians(fc + rng.uniform(-6.0, 6.0, n))
        # ---- who
        protos = []
        weights = []
        for kd in kinds:
            if isinstance(kd, dict):
                protos.append(dict(kd))
                weights.append(1.0)
                continue
            name, wgt = (kd, 1.0) if isinstance(kd, str) else kd
            base = dict(KINDS["raise_" if name == "raise" else name]) if name not in ("child", "child_run") else \
                dict(KINDS["stand" if name == "child" else "run"])
            shp = ("child",) if name.startswith("child") else shapes
            for j, sh in enumerate(shp):
                g = GARMENTS[sh][j % 2]
                d = dict(base, shape=sh, garment=g)
                if sh == "woman" and name in ("stand", "pray", "open") and j % 2:
                    d["veil"] = False
                protos.append(d)
                weights.append(wgt / len(shp))
        self.protos = [_Proto(p, points, self.seed + 0.31 * k) for k, p in enumerate(protos)]
        w = np.asarray(weights, np.float64)
        self.kind = np.searchsorted(np.cumsum(w / w.sum()), rng.uniform(0.0, 1.0, n))
        self.kind = np.minimum(self.kind, len(self.protos) - 1)
        self.phase = rng.uniform(0.0, 1.0, n)
        self.rate = rng.uniform(0.92, 1.08, n)
        lo, hi = (scale, scale) if np.ndim(scale) == 0 else scale
        self.scale = rng.uniform(lo, hi, n)
        self.walk = float(walk)
        # ---- when
        if isinstance(start, dict):
            t0 = float(start.get("t", 0.0))
            if "speed" in start:
                c = np.asarray(start.get("center", getattr(self, "center", (0.0, 0.0))), np.float64)
                d = np.hypot(pl[:, 0] - c[0], pl[:, 2] - c[1])
                self.start = t0 + d / max(float(start["speed"]), 1e-3)
            else:
                self.start = t0 + rng.uniform(0.0, float(start.get("dur", 2.0)), n)
        else:
            self.start = np.broadcast_to(np.asarray(start, np.float64), (n,)).astype(np.float64)
        self.until = None if until is None else np.broadcast_to(np.asarray(until, np.float64), (n,)).astype(np.float64)
        self.fade, self.flash = float(fade), float(flash)
        # ---- how
        c1, c2 = _col(color), _col(color2)
        mix = rng.uniform(0.0, 1.0, n) ** 1.5
        self.tint = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        self.bright, self.grain, self.twinkle, self.glints = float(bright), float(size), float(twinkle), float(glints)

    def gain(self, t):
        return 1.0

    def sample(self, t):
        live = t >= self.start - 0.05
        if self.until is not None:
            live &= t <= self.until + self.fade
        if not live.any():
            return []
        out_p, out_s, out_c, out_a, out_b, out_sd, glint_p, glint_c, glint_a = [], [], [], [], [], [], [], [], []
        for k, pr in enumerate(self.protos):
            ii = np.where(live & (self.kind == k))[0]
            if len(ii) == 0:
                continue
            pr.bake()
            age = np.maximum(t - self.start[ii], 0.0)
            fr = (np.floor(age * self.rate[ii] / pr.dt + self.phase[ii] * pr.F).astype(np.int64)) % pr.F
            P = pr.pos[fr].astype(np.float64)                                    # (I, P, 3)
            cs, sn = np.cos(self.facing[ii]), np.sin(self.facing[ii])
            sc = self.scale[ii]
            x = (P[:, :, 0] * cs[:, None] + P[:, :, 2] * sn[:, None]) * sc[:, None]
            z = (-P[:, :, 0] * sn[:, None] + P[:, :, 2] * cs[:, None]) * sc[:, None]
            y = P[:, :, 1] * sc[:, None]
            base = self.place[ii].copy()
            if self.walk and pr.spec.get("motion") in ("walk", "run"):
                v = self.walk * (1.6 if pr.spec.get("motion") == "run" else 1.0)
                base[:, 0] += np.sin(self.facing[ii]) * v * age
                base[:, 2] += np.cos(self.facing[ii]) * v * age
            pos = np.stack([x + base[:, 0:1], y + base[:, 1:2], z + base[:, 2:3]], axis=2).reshape(-1, 3)
            m = len(ii)
            npt = pr.pos.shape[1]
            alpha = np.ones(m)
            if self.until is not None:
                alpha *= 1.0 - bm.smooth((t - self.until[ii]) / max(self.fade, 1e-3))
            a_pt = np.repeat(alpha, npt) * np.tile(0.42 * (1.0 + 1.2 * pr.edge), m)
            col = (self.tint[ii][:, None, :] * (0.75 + 0.5 * pr.seed_pt[None, :, None])).reshape(-1, 3)
            dark = np.tile(pr.seed_pt < 0.25, m)
            col[dark] *= 0.3
            size = (np.tile(pr.size, m) * np.repeat(sc, npt) * self.grain)
            birth = np.repeat(self.start[ii], npt) + np.tile(pr.seed_pt * 0.35, m)
            sd = np.tile(pr.seed_pt, m)
            g = np.tile(pr.seed_pt > 1.0 - self.glints, m)
            out_p.append(pos[~g])
            out_s.append(size[~g])
            out_c.append(col[~g])
            out_a.append(a_pt[~g] * self.bright)
            out_b.append(birth[~g])
            out_sd.append(sd[~g])
            glint_p.append(pos[g])
            glint_c.append(col[g])
            glint_a.append(a_pt[g] * self.bright)
        if not out_p:
            return []
        b = [dict(pos=np.concatenate(out_p), size=np.concatenate(out_s), color=np.concatenate(out_c),
                  alpha=np.concatenate(out_a), birth=np.concatenate(out_b), seed=np.concatenate(out_sd), kind="soft",
                  twinkle=self.twinkle, fade=self.fade, flash=self.flash, backlight=0.12)]
        gp = np.concatenate(glint_p)
        if len(gp):
            b.append(dict(pos=gp, size=0.012, color=np.concatenate(glint_c), alpha=np.concatenate(glint_a) * 1.6,
                          kind="spark", twinkle=1.0, emit=2.0))
        return b

    def where(self, t, k):
        """Where person k stands at t (their feet), for other point sets."""
        p = self.place[k].copy()
        pr = self.protos[self.kind[k]]
        if self.walk and pr.spec.get("motion") in ("walk", "run"):
            age = max(t - self.start[k], 0.0)
            v = self.walk * (1.6 if pr.spec.get("motion") == "run" else 1.0)
            p[0] += np.sin(self.facing[k]) * v * age
            p[2] += np.cos(self.facing[k]) * v * age
        return p
