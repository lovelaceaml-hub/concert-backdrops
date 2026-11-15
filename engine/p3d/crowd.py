"""Crowds of hundreds of people of light, cheaply: a few prototype bodies are baked once (a few short loops of
frames each) and every person in the crowd is an instance of one of them, placed, turned, mirrored, sized and
started at its own time, each on its own phase and tempo, so no two move together.

    from p3d.crowd import Crowd
    crowd = Crowd(n=400, area=dict(center=(0, -20), radius=(6, 60)), facing=lambda x, z: 180.0,
                  kinds=("stand", "raise", "clap"), start=dict(t=10.0, center=(0, -6), speed=12.0))
    scene.add("crowd", crowd)

    # an acted crowd: they stand at rest, then (staggered, each in their own time) wave, then come back to rest
    Crowd(n=60, area=dict(center=(0, -8), radius=(2, 10)), kinds=("wave", "stand"), act=dict(t=12.0, dur=0.8),
          act_end=17.0)

KEYS
  n          how many people (or give `places`)
  places     (K, 2) or (K, 3) points on the ground: where they stand (default: spread over `area`)
  area       dict(center=(x, z), radius=(r0, r1), arc=(a0, a1) degrees, from +z toward +x): a ring or a
             full disc of people; they are spread evenly with a little jitter
  facing     degrees for all, (K,) one each, a function (x, z) -> degrees, or "center" (all face the
             area's centre) or "out"
  kinds      what people do; each kind is baked once per sort of person, any of:
               "stand", "walk", "run", "sit" (on the ground), "raise" (arms raised high), "clap", "bow", "pray",
               "open" (arms open), "wave", "heart" (a hand on the heart and a bow), "cheer" (both arms thrown
               up), "light" (a light carried in the right hand, raised high in the act), "nod" (listening,
               leaning in and nodding), "kneel" (kneeling, hands joined; in an act they go down onto the knees
               and get up again at act_end), "child" (a child standing), "child_run"
             or (name, weight) pairs; or a list of dicts of Body keys with a "loop" (seconds) for your own
  people     who the crowd is made of: weights over "woman", "man", "elder" (stooped, men and women) and
             "child"; default dict(woman=1, man=1, elder=0.3, child=0.25). (`shapes`, the older key, is a
             list of shapes with equal weights: shapes=("woman", "man") gives the crowd of before.)
  start      when each person appears: a number, (K,) times, or dict(t, center=(x, z), speed) (a wave that
             wakes them as it passes, metres per second) or dict(t, dur) (spread at random over dur)
  act        when each person begins the kind's gesture: None (default: they are in it from the moment they
             appear), a number, (K,) times, or a dict like `start`. From rest they go into it acted
             (anticipation, overshoot, settle), each at their own tempo, then hold it alive
  act_end    when they come out of it again (a number or (K,)): back to rest; None: they keep it
  until      when they go (a number or (K,)); fade: seconds each way; flash: how bright a new person flares
  walk       for walkers and runners: metres per second along their facing (0 keeps them on the spot)
  points     points per person (default 2600: people in the middle and far distance)
  scale      size (1 life size) or (lo, hi) for a spread; default (0.94, 1.06)
  mirror     True (default): half the people are mirrored (left-handed wavers, other garment folds)
  color, color2, bright, size (grain), twinkle, glints (share of four-point glints)
  dof        how much of the lens blur the crowd takes (default 0.55: far people stay people, not blobs)
  light      for "light" people: the colour of their lights (default warm "#ffcf8a") and lamp=(size, bright)
  seed       another crowd

Everything is a pure function of time. Baking costs a few seconds per prototype the first time the crowd is
sampled (in each render process); after that a frame of 400 people costs a few hundredths of a second. With
the environment variable P3D_CACHE set to a folder, the baked prototypes are kept there between processes
(keyed by the engine's own source, so a code change bakes afresh).
"""
import hashlib
import os

import numpy as np

from . import bodymath as bm
from .api import lin

KINDS = dict(
    stand=dict(loop=4.0),
    walk=dict(motion="walk", loop="cycle"),
    run=dict(motion="run", loop="cycle"),
    raise_=dict(gest=[("raise", {})], loop=4.0),
    clap=dict(gest=[("clap", dict(period=0.5, height=0.6))], loop=2.0),
    bow=dict(gest=[("bow", dict(amount=40.0))], loop=4.0),
    pray=dict(gest=[("pray", {})], loop=4.0),
    open=dict(gest=[("open_arms", dict(lift=0.4))], loop=4.0),
    sit=dict(motion=[(0.0, "sit", dict(dur=0.01))], loop=4.0),
    wave=dict(gest=[("wave", dict(side="R"))], loop=2.48),
    heart=dict(gest=[("hand_on_heart", dict(side="R", bow=10.0)), ("bow", dict(amount=20.0), 0.3)], loop=4.0),
    cheer=dict(gest=[("cheer", {})], loop=3.6),
    light=dict(gest=[("raise_hand", dict(side="R", palm="up", fingers="hold"))], loop=4.0, light="palm.R"),
    nod=dict(gest=[("lean_in", dict(amount=0.7)), ("nod", dict(period=1.8, amount=8.0), 0.4)], loop=3.6),
    kneel=dict(motion=[(0.0, "kneel", dict(dur=0.01, hands="pray"))], loop=4.0,
               act_motion=[(0.0, "kneel", dict(dur=1.7, hands="pray", blend=0.05))],
               end_motion=[(0.0, "rise", dict(dur=1.7, one=False, blend=0.05))]),
)
GARMENTS = dict(woman=("dress", "robe"), man=("tunic", "coat"), child=("tunic", "dress"))
HAIRS = dict(woman=("bun", "bob", "tied", "covered"), man=("short", "cap"), child=("tied", "cap", "short"),
             elder_woman=("covered", "bun"), elder_man=("cap", "short"))
BUILDS = (1.0, 0.9, 1.12, 0.95, 1.06)
PEOPLE = dict(woman=1.0, man=1.0, elder=0.3, child=0.25)
NO_ELDER = ("run", "child", "child_run")
PRE = 2.5           # seconds simulated before anything is taken (the garments settle)
FPS = 15.0          # baked frames per second; sampling interpolates between frames
CROSS = 0.5         # seconds of crossfade that close each loop
REST, INTRO, OUTRO = 2.0, 1.8, 1.6       # an acted prototype: rest loop, going into the act, coming out of it
RELEASE = 1.0       # seconds the gesture takes to let go (inside OUTRO)
B_IN, B_OUT, B_BACK = 0.3, 0.45, 0.35    # seconds of the blends between the segments (phases differ)

_SRC = None


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _source_hash():
    global _SRC
    if _SRC is None:
        h = hashlib.sha1()
        d = os.path.dirname(os.path.abspath(__file__))
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"):
                with open(os.path.join(d, f), "rb") as fh:
                    h.update(fh.read())
        _SRC = h.hexdigest()
    return _SRC


def _at(seg, u, loop):
    """Frames of a segment at fractional frame indices u (one per instance), linearly interpolated."""
    F = len(seg)
    i0 = np.floor(u).astype(np.int64)
    f = (u - i0).astype(np.float32).reshape((-1,) + (1,) * (seg.ndim - 1))
    if loop:
        i0 = i0 % F
        i1 = (i0 + 1) % F
    else:
        i0 = np.clip(i0, 0, F - 1)
        i1 = np.minimum(i0 + 1, F - 1)
    return seg[i0] * (1.0 - f) + seg[i1] * f


class _Proto:
    """One baked prototype: segments of positions (F, P, 3) in its own place (feet at the origin, facing +z):
    "loop" always; an acted one also has "rest", "intro" and "outro"."""

    def __init__(self, spec, points, seed, acted):
        self.spec, self.points, self.seed = spec, points, seed
        self.acted = bool(acted)
        self.seg = None

    # ---------------------------------------------------------------- baking
    def _key(self):
        s = repr((sorted((k, repr(v)) for k, v in self.spec.items()), self.points, self.seed, self.acted, FPS, PRE,
                  CROSS, REST, INTRO, OUTRO, RELEASE))
        return hashlib.sha1((s + _source_hash()).encode()).hexdigest()[:24]

    def bake(self):
        if self.seg is not None:
            return
        cache = os.environ.get("P3D_CACHE")
        path = os.path.join(cache, "crowd_%s.npz" % self._key()) if cache else None
        if path and os.path.exists(path):
            try:
                self._load(path)
                return
            except Exception:
                pass
        self._bake()
        if path:
            try:
                os.makedirs(cache, exist_ok=True)
                tmp = path + ".%d.tmp" % os.getpid()
                with open(tmp, "wb") as fh:
                    np.savez(fh, **self._arrays())
                os.replace(tmp, path)
            except OSError:
                pass

    def _arrays(self):
        out = dict(size=self.size, seed_pt=self.seed_pt, edge=self.edge, height=np.array(self.height))
        for name, (P, dt) in self.seg.items():
            out["seg_" + name] = P
            out["dt_" + name] = np.array(dt)
        for name, L in self.light.items():
            out["light_" + name] = L
        return out

    def _load(self, path):
        z = np.load(path)
        self.size, self.seed_pt, self.edge = z["size"], z["seed_pt"], z["edge"]
        self.height = float(z["height"])
        seg, light = {}, {}
        for k in z.files:
            if k.startswith("seg_"):
                seg[k[4:]] = (z[k], float(z["dt_" + k[4:]]))
            elif k.startswith("light_"):
                light[k[6:]] = z[k]
        self.seg, self.light = seg, light

    def _bake(self):
        from .body import Body
        sp = dict(self.spec)
        loop = sp.pop("loop")
        lamp = sp.pop("light", None)
        gest = sp.pop("gest", ())
        am = sp.pop("act_motion", None)
        em = sp.pop("end_motion", None)
        motion = sp.pop("motion", "stand")
        kw = dict(look="glitter", points=self.points, seed=self.seed, hair="default", size=0.8)
        kw.update(sp)
        if isinstance(motion, str) and motion in ("walk", "run"):
            from .motion import Motions
            from . import assets
            c = Motions(assets.Rig(kw.get("shape", "woman"), kw.get("height")), assets.load()).clips[motion]
            loop = c.T * max(1, int(round(1.0 / c.T)))
            cross = 0.0
        else:
            cross = CROSS
        plan = {}                     # segment -> (t_start, duration, crossfade toward the frames before it)
        if self.acted:
            r0 = PRE + CROSS
            A = r0 + REST + 0.2
            ls = A + INTRO
            B = ls + loop + 0.3
            plan = dict(rest=(r0, REST, CROSS), intro=(A, INTRO, 0.0), loop=(ls, loop, CROSS), outro=(B, OUTRO, 0.0))
            mk = [(-1e9, motion if isinstance(motion, str) else "stand", {})]
            if am:
                mk += [(A + dt0, nm, dict(p)) for dt0, nm, p in am]
            if em:
                mk += [(B + dt0, nm, dict(p)) for dt0, nm, p in em]
            if mk and "motion" not in kw:
                kw["motion"] = mk
            g = []
            for e in gest:
                nm, p = e[0], dict(e[1])
                d0 = e[2] if len(e) > 2 else 0.0
                p.setdefault("ease_out", RELEASE)
                g.append((A + d0, B + RELEASE, nm, p))
            if g:
                kw["gesture"] = g
        else:
            plan = dict(loop=(PRE + cross, loop, cross))
            kw.setdefault("motion", motion)
            if gest:
                kw.setdefault("gesture", [(0.0, 1e9, e[0], dict(e[1], ease=0.01)) for e in gest])
        b = Body(**kw)
        # every time to bake, in order (the garments simulate forward in time)
        jobs = []
        for name, (t0, dur, cr) in plan.items():
            F = max(int(round(dur * FPS)), 2)
            dt = dur / F
            X = int(round(cr / dt))
            for k in range(-X, F):
                jobs.append((t0 + k * dt, name, k))
            plan[name] = (t0, dur, cr, F, dt, X)
        jobs.sort(key=lambda j: j[0])
        frames = {name: {} for name in plan}
        lights = {name: {} for name in plan}
        for t, name, k in jobs:
            p, _n = b.points_at(t)
            f = b.actor.frame(t)
            o = f["origin"]
            q = bm.qy(-f["heading"])
            frames[name][k] = bm.qrot(q, (p - o).astype(np.float64)).astype(np.float32)
            if lamp:
                lp = b.actor.where(t, lamp) + np.array([0.0, 0.05 * b.k, 0.0])
                lights[name][k] = bm.qrot(q, (lp - o)[None])[0].astype(np.float32)
        self.seg, self.light = {}, {}
        for name, (t0, dur, cr, F, dt, X) in plan.items():
            P = np.stack([frames[name][k] for k in range(F)])
            L = np.stack([lights[name][k] for k in range(F)]) if lamp else None
            if X:
                # the loop's last frames ease into the frames just before its first: the seam is seamless
                pre = np.stack([frames[name][k] for k in range(-X, 0)])
                w = ((np.arange(X) + 1.0) / X)[:, None, None]
                P[F - X:] = P[F - X:] * (1 - w) + pre * w
                if lamp:
                    lpre = np.stack([lights[name][k] for k in range(-X, 0)])
                    L[F - X:] = L[F - X:] * (1 - w[:, :, 0]) + lpre * w[:, :, 0]
            self.seg[name] = (P, dt)
            if lamp:
                self.light[name] = L
        cl = b.cloud
        self.size = cl["size"].astype(np.float32)
        self.seed_pt = cl["seed"].astype(np.float32)
        self.edge = cl.get("edge", np.zeros(len(self.size))).astype(np.float32)
        self.height = b.rig.height

    # ---------------------------------------------------------------- sampling
    def frames(self, t, age, rate, phase, act, end, irate, light=False):
        """Positions (I, P, 3) (or the light, (I, 3)) of instances at t, each with its own age since it appeared,
        tempo, phase, act and act end times."""
        src = self.light if light else {k: v[0] for k, v in self.seg.items()}
        dt = {k: v[1] for k, v in self.seg.items()}
        if not self.acted:
            u = age * rate / dt["loop"] + phase * len(src["loop"])
            return _at(src["loop"], u, True)
        n = len(age)
        tin = t - act
        tout = t - end
        idur = INTRO / irate
        odur = OUTRO / irate
        st_rest0 = tin < 0.0
        st_in = (~st_rest0) & (tout < 0.0)
        st_out = (tout >= 0.0) & (tout < odur)
        st_back = tout >= odur
        w_r = 1.0 - bm.smooth(np.clip(tin / B_IN, 0.0, 1.0))
        w_h = 1.0 - bm.smooth(np.clip(tout / B_OUT, 0.0, 1.0))
        w_o = 1.0 - bm.smooth(np.clip((tout - odur) / B_BACK, 0.0, 1.0))
        w_rest = np.where(st_rest0, 1.0, 0.0) + np.where(st_in, w_r, 0.0) + np.where(st_back, 1.0 - w_o, 0.0)
        w_held = np.where(st_in, 1.0 - w_r, 0.0) + np.where(st_out, w_h, 0.0)
        w_outro = np.where(st_out, 1.0 - w_h, 0.0) + np.where(st_back, w_o, 0.0)
        in_intro = tin < idur
        weights = dict(rest=w_rest, intro=w_held * in_intro, loop=w_held * (~in_intro), outro=w_outro)
        index = dict(rest=age * rate / dt["rest"] + phase * len(src["rest"]),
                     intro=np.maximum(tin, 0.0) * irate / dt["intro"],
                     loop=np.maximum(tin - idur, 0.0) * rate / dt["loop"],
                     outro=np.maximum(tout, 0.0) * irate / dt["outro"])
        shape = (n,) + src["loop"].shape[1:]
        out = np.zeros(shape, np.float32)
        for name in ("rest", "intro", "loop", "outro"):
            w = weights[name]
            m = w > 1e-4
            if not m.any():
                continue
            part = _at(src[name], index[name][m], name in ("rest", "loop"))
            out[m] += part * w[m].astype(np.float32).reshape((-1,) + (1,) * (part.ndim - 1))
        return out


class Crowd:
    """Hundreds of people of light (see the module text)."""

    def __init__(self, n=200, places=None, area=None, facing=0.0, kinds=("stand",), shapes=None, people=None,
                 start=0.0, until=None, act=None, act_end=None, fade=0.6, flash=0.6, walk=0.0, points=2600,
                 scale=(0.94, 1.06), mirror=True, color="#f2b865", color2="#ffe6b8", bright=1.0, size=1.0,
                 twinkle=0.8, glints=0.002, light="#ffcf8a", lamp=(0.11, 1.0), dof=0.55, seed=1.0):
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
        if people is None:
            people = {s: 1.0 for s in shapes} if shapes is not None else dict(PEOPLE)
        acted = act is not None
        protos, weights = [], []
        for ki, kd in enumerate(kinds):
            if isinstance(kd, dict):
                protos.append((dict(kd), False))
                weights.append(1.0)
                continue
            name, wgt = (kd, 1.0) if isinstance(kd, str) else kd
            if name in ("child", "child_run"):
                base, who = dict(KINDS["stand" if name == "child" else "run"]), dict(child=1.0)
            else:
                base, who = dict(KINDS["raise_" if name == "raise" else name]), dict(people)
            if name in NO_ELDER:
                who.pop("elder", None)
            tot = sum(who.values())
            kact = acted and bool(base.get("gest") or base.get("act_motion"))
            for j, (person, wp) in enumerate(who.items()):
                if wp <= 0:
                    continue
                d = dict(base)
                v = ki * 3 + j
                if person == "elder":
                    sh = ("woman", "man")[ki % 2]
                    hs = HAIRS["elder_" + sh]
                    d.update(shape=sh, garment=GARMENTS[sh][1], stoop=0.55, hair=hs[v % len(hs)],
                             build=BUILDS[(v + 2) % len(BUILDS)])
                else:
                    hs = HAIRS[person]
                    d.update(shape=person, garment=GARMENTS[person][(j + ki) % 2], hair=hs[v % len(hs)],
                             build=BUILDS[v % len(BUILDS)])
                protos.append((d, kact))
                weights.append(wgt * wp / tot)
        self.protos = [_Proto(p, points, self.seed + 0.31 * k, a) for k, (p, a) in enumerate(protos)]
        w = np.asarray(weights, np.float64)
        self.kind = np.searchsorted(np.cumsum(w / w.sum()), rng.uniform(0.0, 1.0, n))
        self.kind = np.minimum(self.kind, len(self.protos) - 1)
        self.phase = rng.uniform(0.0, 1.0, n)
        self.rate = rng.uniform(0.9, 1.1, n)
        self.irate = rng.uniform(0.85, 1.15, n)
        self.mirror = np.where(rng.uniform(0.0, 1.0, n) < (0.5 if mirror else 0.0), -1.0, 1.0)
        lo, hi = (scale, scale) if np.ndim(scale) == 0 else scale
        self.scale = rng.uniform(lo, hi, n)
        self.walk = float(walk)
        # ---- when
        self.start = self._times(start, rng, pl)
        self.act = self._times(act, rng, pl) if acted else np.full(n, -1e9)
        self.act_end = np.full(n, 1e9) if act_end is None else self._times(act_end, rng, pl)
        self.until = None if until is None else np.broadcast_to(np.asarray(until, np.float64), (n,)).astype(np.float64)
        self.fade, self.flash = float(fade), float(flash)
        # ---- how
        c1, c2 = _col(color), _col(color2)
        mix = rng.uniform(0.0, 1.0, n) ** 1.5
        self.tint = c1[None] * (1 - mix)[:, None] + c2[None] * mix[:, None]
        self.bright, self.grain, self.twinkle, self.glints = float(bright), float(size), float(twinkle), float(glints)
        self.dof = float(dof)
        self.lamp_col = _col(light)
        self.lamp = (float(lamp[0]), float(lamp[1]))

    def _times(self, v, rng, pl):
        n = len(pl)
        if isinstance(v, dict):
            t0 = float(v.get("t", 0.0))
            if "speed" in v:
                c = np.asarray(v.get("center", getattr(self, "center", (0.0, 0.0))), np.float64)
                d = np.hypot(pl[:, 0] - c[0], pl[:, 2] - c[1])
                return t0 + d / max(float(v["speed"]), 1e-3)
            return t0 + rng.uniform(0.0, float(v.get("dur", 2.0)), n)
        return np.broadcast_to(np.asarray(v, np.float64), (n,)).astype(np.float64)

    def gain(self, t):
        return 1.0

    def _place(self, P, ii, age, pr):
        """Instance-local points (I, ..., 3) into the world."""
        cs, sn = np.cos(self.facing[ii]), np.sin(self.facing[ii])
        sc = self.scale[ii]
        ms = self.mirror[ii]
        ex = (slice(None),) + (None,) * (P.ndim - 2)
        px = P[..., 0] * ms[ex]
        x = (px * cs[ex] + P[..., 2] * sn[ex]) * sc[ex]
        z = (-px * sn[ex] + P[..., 2] * cs[ex]) * sc[ex]
        y = P[..., 1] * sc[ex]
        base = self.place[ii].copy()
        if self.walk and pr.spec.get("motion") in ("walk", "run"):
            v = self.walk * (1.6 if pr.spec.get("motion") == "run" else 1.0)
            base[:, 0] += np.sin(self.facing[ii]) * v * age
            base[:, 2] += np.cos(self.facing[ii]) * v * age
        return np.stack([x + base[:, 0][ex], y + base[:, 1][ex], z + base[:, 2][ex]], axis=-1)

    def sample(self, t):
        live = t >= self.start - 0.05
        if self.until is not None:
            live &= t <= self.until + self.fade
        if not live.any():
            return []
        out_p, out_s, out_c, out_a, out_b, out_sd, glint_p, glint_c, glint_a = [], [], [], [], [], [], [], [], []
        lamp_p, lamp_a, lamp_b, lamp_s = [], [], [], []
        for k, pr in enumerate(self.protos):
            ii = np.where(live & (self.kind == k))[0]
            if len(ii) == 0:
                continue
            pr.bake()
            age = np.maximum(t - self.start[ii], 0.0)
            args = (t, age, self.rate[ii], self.phase[ii], self.act[ii], self.act_end[ii], self.irate[ii])
            P = pr.frames(*args).astype(np.float64)                             # (I, P, 3)
            pos = self._place(P, ii, age, pr).reshape(-1, 3)
            m = len(ii)
            npt = P.shape[1]
            alpha = np.ones(m)
            if self.until is not None:
                alpha *= 1.0 - bm.smooth((t - self.until[ii]) / max(self.fade, 1e-3))
            a_pt = np.repeat(alpha, npt) * np.tile(0.30 * (1.0 + 1.6 * pr.edge), m)
            col = (self.tint[ii][:, None, :] * (0.75 + 0.5 * pr.seed_pt[None, :, None])).reshape(-1, 3)
            dark = np.tile(pr.seed_pt < 0.25, m)
            col[dark] *= 0.3
            sc = self.scale[ii]
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
            if pr.light:
                L = pr.frames(*args, light=True).astype(np.float64)              # (I, 3)
                lamp_p.append(self._place(L[:, None, :], ii, age, pr)[:, 0])
                fl = 0.85 + 0.15 * np.sin(t * (5.0 + 3.0 * self.phase[ii]) + 40.0 * self.phase[ii])
                lamp_a.append(alpha * fl)
                lamp_b.append(self.start[ii] + 0.3)
                lamp_s.append(sc)
        if not out_p:
            return []
        b = [dict(pos=np.concatenate(out_p), size=np.concatenate(out_s), color=np.concatenate(out_c),
                  alpha=np.concatenate(out_a), birth=np.concatenate(out_b), seed=np.concatenate(out_sd), kind="soft",
                  twinkle=self.twinkle, fade=self.fade, flash=self.flash, backlight=0.05, dof=self.dof)]
        gp = np.concatenate(glint_p)
        if len(gp):
            b.append(dict(pos=gp, size=0.010, color=np.concatenate(glint_c), alpha=np.concatenate(glint_a) * 1.4,
                          kind="spark", twinkle=1.0, emit=1.6, dof=self.dof))
        if lamp_p:
            lp, la, lb, ls = (np.concatenate(v) for v in (lamp_p, lamp_a, lamp_b, lamp_s))
            sz, br = self.lamp
            b.append(dict(pos=lp, size=sz * ls, color=self.lamp_col * 0.9 * br, alpha=0.45 * la, birth=lb,
                          kind="soft", fade=self.fade, flash=self.flash, backlight=0.2, dof=self.dof))
            b.append(dict(pos=lp, size=0.02 * ls, color=self.lamp_col * br, alpha=la, birth=lb, kind="spark",
                          emit=2.6, fade=self.fade, twinkle=0.3, dof=self.dof))
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
