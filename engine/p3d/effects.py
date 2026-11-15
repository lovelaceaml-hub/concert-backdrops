"""Effects of the particle bodies: light that gathers into a person and scatters from one.

Every effect is a pure function of time (no state from frame to frame), driven by repeatable noise fields:

  on a Body (engine/p3d/body.py), given in its `effects` list as dict(kind=..., t=..., ...):
    "form"       the body gathers out of drifting dust (or out of given points: a word becomes a body)
    "disperse"   it blows away into the air from one side (ref 01, 16)
    "dissolve"   it rises apart from the head down into flakes and sparks (ref 05, 11, 13)
    "petals"     it turns to petals that leave in a spiral (ref 07)
    "birds"      birds leave the silhouette (ref 08)
    "blow"       a stream of particles blown from the open palm (ref 14)
    "shed"       it sheds light as it stands or walks, and stays whole (ref 15, 09)
  on their own, as point sets:
    Flare        the flash where two hands touch (ref 04)
    Takeover     flies a set of particles (plain arrays) to given places

REVERSIBLE AMOUNTS
  "form", "disperse", "dissolve" and "petals" take amount=<a Track or any function of time, 0..1> instead of
  running on their own clock: 0 is the whole body, 1 fully gone (for "form": 0 not yet there, 1 formed). The
  Track may run forward, hold and run backward: while it holds, the particles hang in the air; when it runs
  back every particle flies home along its own path and the person is whole again (they return to the body
  where it is NOW, so someone can be mended while moving). `reach` is how many seconds of flight amount 1
  stands for (default 3).

ONE WIND
  Wind(base=(x, y, z), gusts=[(t, strength, seconds), ...]) is one wind for a whole scene: give the same
  object to every Body(wind=...) (garments and freed particles follow it) and read it elsewhere with
  wind.at(t). Flights take hang=<seconds>: the particles slow to a stop and stay in the air.

HANDING PARTICLES OVER (for words made of particles, engine/p3d words)
  Every effect knows where its free particles are and where they are going:
    body.free(t)  ->  dict(pos, vel, size, color, alpha, seed, id, effect): plain arrays for every particle
                      that is off the body at t
  and any effect takes a hand-over, in its dict or later with body.handover(...):
    to=dict(t=12.0, targets=<(K, 3) array or function of time>, arrive=1.5, stagger=0.6)
  From t on, the particles that are in the air then fly to the targets (each to its own; they are matched in
  order along the longest side of the target shape, so nothing crosses needlessly), arrive after `arrive`
  seconds, staggered across the shape by `stagger` seconds, and stay there. `until` ends them (fading over
  0.3 s) when another point set draws those places itself. effect.assignment() tells which target each
  particle took. The other way round, "form" takes source=<(K, 3) array or function of time>: the body's
  points start from those places.
"""
import numpy as np

from . import bodymath as bm
from .api import lin

BIN = 1.0 / 15.0
UP = np.array([0.0, 1.0, 0.0])
EFFECTS = ("form", "disperse", "dissolve", "petals", "birds", "blow", "shed")


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _hvec(seed, salt):
    """Repeatable directions on the unit sphere from seeds (K,) in 0..1."""
    i = (np.asarray(seed, np.float64) * 16777216.0).astype(np.int64)
    z = bm.hashf(i, salt) * 2.0 - 1.0
    a = bm.hashf(i, salt + 1) * 2.0 * np.pi
    r = np.sqrt(np.maximum(1.0 - z * z, 0.0))
    return np.stack([r * np.cos(a), z, r * np.sin(a)], axis=1)


def _rank(x):
    """0..1 by rank (ties broken by position), so that things spread evenly over a duration."""
    o = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[o] = (np.arange(len(x)) + 0.5) / max(len(x), 1)
    return r


class Wind:
    """One wind for a scene: a steady flow with timed gusts, the same for garments, freed particles and
    anything else that asks.

    base     (x, y, z) metres per second
    gusts    [(t, strength, seconds), ...]: around time t the wind swells to (1 + strength) times its base
             for about `seconds`; strength may also be a vector (x, y, z) added at the peak
    sway     how much it wanders on its own (0..1)
    """

    def __init__(self, base=(0.0, 0.0, 0.0), gusts=(), sway=0.25, seed=0.0):
        self.base = np.asarray(base, np.float64)
        self.gusts = [(float(g[0]), g[1], float(g[2]) if len(g) > 2 else 1.2) for g in gusts]
        self.sway, self.seed = float(sway), float(seed)
        self._cum = None

    def at(self, t):
        """The wind at time t (a vector, metres per second)."""
        w = self.base * (1.0 + self.sway * bm.wobble(t, self.seed + 0.5, 0.9))
        for (tg, s, ln) in self.gusts:
            b = float(np.exp(-((t - tg) / (0.42 * ln)) ** 2))
            w = w + (self.base * s if np.ndim(s) == 0 else np.asarray(s, np.float64)) * b
        return w

    def gust(self, t):
        """How strong the gusts are at t (0: none), for anything that wants to move with them."""
        return float(sum(np.exp(-((t - tg) / (0.42 * ln)) ** 2) * (s if np.ndim(s) == 0 else np.linalg.norm(s))
                         for (tg, s, ln) in self.gusts))

    def travel(self, t0, t1):
        """How far free air is carried from t0 to t1: (..., 3). t0 and t1 may be arrays."""
        step = 1.0 / 30.0
        t0 = np.asarray(t0, np.float64)
        t1 = np.asarray(t1, np.float64)
        hi = float(max(np.max(t0), np.max(t1), 0.0)) + 1.0
        lo = float(min(np.min(t0), np.min(t1), 0.0)) - 1.0
        if self._cum is None or self._cum[0] > lo or self._cum[1] < hi:
            lo, hi = min(lo, -2.0), max(hi, 90.0)
            ts = np.arange(lo, hi + step, step)
            v = np.array([self.at(x) for x in ts])
            self._cum = (lo, hi, np.concatenate([np.zeros((1, 3)), np.cumsum(0.5 * (v[1:] + v[:-1]) * step, axis=0)]))
        lo, _hi, cum = self._cum

        def W(t):
            x = (t - lo) / step
            k = np.clip(np.floor(x).astype(np.int64), 0, len(cum) - 2)
            f = (x - k)[..., None]
            return cum[k] * (1 - f) + cum[k + 1] * f
        return W(t1) - W(t0)


class Flight:
    """How a freed particle travels, as a function of its age (seconds since it left).

    dir      where the air carries it (a vector; its length does not matter) and speed in metres per second
    rise     metres per second upward (warm light rises)
    push     metres it is first pushed off the surface along the surface normal
    spread   how much each particle goes its own way
    turb     metres of drift in the eddies of the air; turb_scale: how small the eddies are
    swirl    radians per second around the vertical axis through `axis` (a spiral)
    tau      seconds to pick up speed (it starts from rest)
    burst    metres per second of a first puff straight out from `axis` that dies away
    hang     seconds after which it has slowed to a stop and stays in the air (None: it travels on)
    wind     a Wind that carries it as well; drag: how much of the wind it takes (0..1)
    """

    def __init__(self, dir=(0.0, 0.0, 0.0), speed=0.5, rise=0.0, push=0.08, spread=0.10, turb=0.30, turb_scale=1.5,
                 swirl=0.0, tau=0.9, burst=0.0, seed=0.0, gravity=0.0, hang=None, wind=None, drag=0.8):
        d = np.asarray(dir, np.float64)
        ln = np.linalg.norm(d, axis=-1, keepdims=True)
        self.dir = d / np.maximum(ln, 1e-9) * (ln > 1e-9)
        self.speed, self.rise, self.push, self.spread = speed, rise, push, spread
        self.turb, self.turb_scale, self.swirl, self.tau = turb, turb_scale, swirl, tau
        self.burst, self.seed, self.gravity = burst, seed, gravity
        self.hang, self.wind, self.drag = hang, wind, drag

    def offset(self, p0, n0, age, sd, t=0.0, axis=None):
        """Where the particle is, relative to where it left. p0, n0: (K, 3) the place and surface normal it left
        from; age, sd: (K,) seconds and a seed per particle."""
        a_real = np.maximum(np.asarray(age, np.float64), 0.0)
        a = a_real if not self.hang else self.hang * (1.0 - np.exp(-a_real / self.hang))
        sd = np.asarray(sd, np.float64)
        pace = 0.55 + 0.9 * bm.hashf((sd * 16777216.0).astype(np.int64), 21)
        ease = a - self.tau * (1.0 - np.exp(-a / self.tau))
        d = self.dir * (self.speed * pace * ease)[:, None]
        d[:, 1] += self.rise * pace * ease - 0.5 * self.gravity * a * a
        d += n0 * (self.push * (1.0 - np.exp(-a / 0.35)))[:, None]
        d += _hvec(sd, 23) * (self.spread * a ** 0.8)[:, None]
        if self.burst and axis is not None:
            out = p0 - axis
            out[:, 1] *= 0.4
            out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
            d += out * (self.burst * 0.5 * (1.0 - np.exp(-a / 0.5)) * pace)[:, None]
        if self.wind is not None and self.drag:
            d += self.wind.travel(t - a, t) * self.drag
        if self.turb:
            g = 1.0 - np.exp(-a / 0.7)
            d += bm.flow((p0 + d) * self.turb_scale, a * 0.55 + t * 0.12, speed=1.0, seed=self.seed) * (self.turb * g)[:, None]
        if self.swirl and axis is not None:
            ang = self.swirl * ease * (0.6 + 0.8 * pace)
            rel = p0 + d - axis
            c, s = np.cos(ang), np.sin(ang)
            x = rel[:, 0] * c + rel[:, 2] * s
            z = -rel[:, 0] * s + rel[:, 2] * c
            widen = 1.0 + 0.25 * ease
            d[:, 0] = axis[0] + x * widen - p0[:, 0]
            d[:, 2] = axis[2] + z * widen - p0[:, 2]
        return d


def _fade(age, life, fin=0.12, fout=0.45):
    """Brightness over a particle's life: quick in, slow out."""
    u = np.clip(age / np.maximum(life, 1e-6), 0.0, 1.0)
    return np.clip(age / fin, 0.0, 1.0) * np.clip((1.0 - u) / fout, 0.0, 1.0) ** 1.3


def _spin(seed, age, rate=1.0):
    r2 = bm.hashf((np.asarray(seed, np.float64) * 16777216.0).astype(np.int64), 29)
    return np.stack([seed * 6.283 + age * (0.5 + 1.5 * r2) * rate, r2 * 6.283 + age * (0.9 + 2.4 * seed) * rate], axis=1)


class _Free:
    """What every effect with free particles shares: the hand-over to targets, and reporting its particles."""
    to = None
    index = 0

    def _init_free(self, to):
        self.to = dict(to) if to else None
        self._asg = None

    def handover(self, t, targets, arrive=1.5, stagger=0.5, until=None, swirl=0.15):
        self.to = dict(t=float(t), targets=targets, arrive=float(arrive), stagger=float(stagger), until=until,
                       swirl=swirl)
        self._asg = None
        return self

    def _frozen(self, t):
        """The time that decides which particles exist: frozen at the hand-over."""
        return t if self.to is None else min(t, self.to["t"])

    def _targets(self, t):
        tg = self.to["targets"]
        return np.asarray(tg(t) if callable(tg) else tg, np.float64).reshape(-1, 3)

    def assignment(self):
        """After a hand-over: (ids, target index, delay) for every particle that takes part."""
        if self.to is None:
            return None
        if self._asg is None:
            th = self.to["t"]
            ids, pos, _a, _age = self._raw(th)[:4]
            tg = self._targets(th)
            if len(ids) == 0 or len(tg) == 0:
                self._asg = (ids, np.zeros(len(ids), np.int64), np.zeros(len(ids)))
            else:
                ax = int(np.argmax(tg.max(0) - tg.min(0)))
                ax2 = int(np.argsort(tg.max(0) - tg.min(0))[-2])
                # order both along the long side of the shape, and within it along the second side
                rp = _rank(pos[:, ax] + 1e-3 * pos[:, ax2])
                ot = np.argsort(tg[:, ax] + 1e-3 * tg[:, ax2], kind="stable")
                pick = ot[np.minimum((rp * len(tg)).astype(np.int64), len(tg) - 1)]
                self._asg = (ids, pick, rp * self.to.get("stagger", 0.5))
        return self._asg

    def _steer(self, t, ids, pos, alpha):
        """Bends free particles toward their targets after the hand-over time."""
        to = self.to
        if to is None or t <= to["t"] or len(ids) == 0:
            return pos, alpha
        aid, pick, delay = self.assignment()          # sorted by id
        if len(aid) == 0:
            return pos, alpha
        where = np.minimum(np.searchsorted(aid, ids), len(aid) - 1)
        found = aid[where] == ids
        pick, delay = pick[where], delay[where]
        tgs = self._targets(t)
        tg = tgs[np.minimum(pick, len(tgs) - 1)]
        s = bm.smoother((t - to["t"] - delay) / max(to.get("arrive", 1.5), 1e-3)) * found
        sw = to.get("swirl", 0.15)
        if sw:
            d = tg - pos
            side = np.cross(d, UP)
            pos = pos + side * (sw * np.sin(np.pi * s))[:, None]
        pos = pos * (1.0 - s)[:, None] + tg * s[:, None]
        alpha = alpha * (1.0 - s) + np.maximum(alpha, 0.85) * s
        if to.get("until") is not None:
            alpha = alpha * (1.0 - bm.ramp(t, to["until"], to["until"] + 0.3))
        return pos, alpha

    def particles(self, t):
        """dict(id, pos, alpha, age, size, color, seed, kind) of the free particles at t (steered if handed over)."""
        raise NotImplementedError

    def _crowd(self, n, t):
        """After a hand-over to fewer targets than particles, each particle is dimmed by as much as they crowd,
        so the targets do not blaze (several particles share one place). Eases in over the flight."""
        if self.to is None or t <= self.to["t"]:
            return 1.0
        asg = self.assignment()
        k = len(self._targets(self.to["t"]))
        m = max(len(asg[0]), 1)
        if m <= k:
            return 1.0
        u = float(bm.smoother((t - self.to["t"]) / max(self.to.get("arrive", 1.5) + self.to.get("stagger", 0.5), 1e-3)))
        return 1.0 + (min(1.0, 1.6 * k / m) - 1.0) * u


# ---------------------------------------------------------------------------------------------------------
# effects on the points of a body
# ---------------------------------------------------------------------------------------------------------
class Release(_Free):
    """Points leave the body one after another and travel away: "disperse", "dissolve", "petals"."""

    # sprites: (kind, share of the leaving points that become this sprite, size multiplier, brightness). The rest
    # of the leaving points simply go out, so the air never fills with more light than the body had.
    DEFAULTS = dict(
        disperse=dict(order="side", noise=0.45, life=4.5, speed=0.9, rise=0.12, push=0.05, spread=0.16, turb=0.45,
                      swirl=0.0, sprites=(("soft", 0.5, 1.0, 0.8),), grow=1.0),
        dissolve=dict(order="down", noise=0.35, life=5.0, speed=0.0, rise=0.85, push=0.10, spread=0.16, turb=0.32,
                      swirl=0.35, sprites=(("flake", 0.05, 3.2, 1.0), ("soft", 0.28, 1.0, 0.7)), grow=0.4),
        petals=dict(order="spiral", noise=0.25, life=5.5, speed=0.5, rise=0.18, push=0.12, spread=0.12, turb=0.35,
                    swirl=1.1, sprites=(("petal", 0.13, 6.0, 1.0), ("soft", 0.15, 0.9, 0.8)), grow=0.2),
    )

    def __init__(self, body, kind, t=0.0, dur=3.0, share=1.0, dir=None, order=None, noise=None, life=None, parts=None,
                 keep=False, color=None, color2=None, to=None, bright=1.0, size=1.0, amount=None, reach=3.0, **flight):
        d = dict(self.DEFAULTS[kind])
        self.body, self.kind = body, kind
        self.t, self.dur, self.share = float(t), float(dur), float(share)
        self.amount, self.reach = amount, float(reach)
        if amount is not None and life is None:
            life = 1e9                      # driven by an amount: the particles stay until it runs back
        self.life = float(d["life"] if life is None else life)
        self.keep = keep
        self.sprites = flight.pop("sprites", d["sprites"])
        self.grow = flight.pop("grow", d["grow"])
        self.bright, self.size = bright, size
        cl = body.cloud
        n = cl["n"]
        f0 = body.actor.frame(self.t)
        qh = bm.qy(f0["heading"])
        if dir is None:
            dir = (0.0, 0.0, 0.0) if kind == "dissolve" else bm.qrot(qh, [0.0, 0.1, -1.0])
        self.dir = np.asarray(dir, np.float64)
        fl = {k: d[k] for k in ("speed", "rise", "push", "spread", "turb", "swirl")}
        fl.update(flight)
        fl.setdefault("wind", body.wind)
        self.flight = Flight(dir=self.dir, seed=body.seed + 0.37 * (1 + self.index), **fl)
        # the order in which points leave
        order = order or d["order"]
        rest = cl["rest"]
        if order == "down":
            base = 1.0 - cl["h"]
        elif order == "up":
            base = cl["h"]
        elif order == "side":
            dl = bm.qrot(bm.qconj(qh), self.dir)
            dl = dl / max(np.linalg.norm(dl), 1e-9)
            base = 1.0 - _rank(rest @ dl)
        elif order == "spiral":
            ang = np.arctan2(rest[:, 0], rest[:, 2]) / (2 * np.pi)
            base = 1.0 - np.mod(cl["h"] * 2.2 + ang, 1.0) * 0.5 - cl["h"] * 0.5
        elif order == "out":
            base = 1.0 - _rank(np.hypot(rest[:, 0], rest[:, 2]))
        else:
            base = np.zeros(n)
        nz = d["noise"] if noise is None else noise
        blot = bm.flow(rest, 0.0, scale=5.0, speed=0.0, seed=body.seed + 3.0)[:, 0] * 0.5 + 0.5
        o = _rank(_rank(base) * (1 - nz) + nz * (0.6 * blot + 0.4 * cl["seed"]))
        if parts is not None:
            o = np.where(np.isin(cl["part"], parts), o, 2.0)
        self.tau = np.where(o <= self.share, self.t + self.dur * o / max(self.share, 1e-6), np.inf)
        # which free sprite each point becomes (or none)
        r = bm.hashf(np.arange(n), 41 + self.index)
        self.groups = []
        lo = 0.0
        for (sk, share, smul, em) in self.sprites:
            ids = np.where((r >= lo) & (r < lo + share) & np.isfinite(self.tau))[0]
            lo += share
            self.groups.append((sk, ids, smul, em))
        self.color = None if color is None else _col(color)
        self.color2 = None if color2 is None else _col(color2)
        self._init_free(to)

    def _clock(self, t):
        """The effect's own time: the real time, or the time its amount stands for."""
        if self.amount is None:
            return t
        a = self.amount(t) if callable(self.amount) else self.amount
        return self.t + float(np.clip(a, 0.0, 1.0)) * (self.dur + self.reach)

    def on_body(self, t, on):
        """Dims the points that have left (unless the body keeps them)."""
        if not self.keep:
            on *= 1.0 - bm.smooth((self._clock(t) - self.tau) / 0.10)

    def _raw(self, t, group=None):
        real = t
        t = self._clock(t)
        tq = t if self.amount is not None else self._frozen(t)
        out_ids, out_pos, out_alpha, out_age = [], [], [], []
        axis = self.body.actor.frame(real if self.amount is not None else min(t, self.t + self.dur))["origin"]
        for g, (sk, ids, smul, em) in enumerate(self.groups):
            if group is not None and g != group:
                continue
            tau = self.tau[ids]
            m = (tau <= tq) & (tq - tau < self.life)
            ii = ids[m]
            if len(ii) == 0:
                out_ids.append(ii)
                out_pos.append(np.zeros((0, 3)))
                out_alpha.append(np.zeros(0))
                out_age.append(np.zeros(0))
                continue
            tb = self.tau[ii]
            if self.amount is not None:
                p0, n0 = self.body.points_at(real, ii)          # home is where the body is now
            else:
                p0, n0 = self.body.anchor(("rel", self.index), tb, ii)
            sd = self.body.cloud["seed"][ii].astype(np.float64)
            age = t - tb
            pos = p0 + self.flight.offset(p0.astype(np.float64), n0.astype(np.float64), age, sd, real, axis)
            out_ids.append(ii)
            out_pos.append(pos)
            out_alpha.append(_fade(tq - tb, self.life))
            out_age.append(age)
        if group is not None:
            return out_ids[0], out_pos[0], out_alpha[0], out_age[0]
        return np.concatenate(out_ids), np.concatenate(out_pos), np.concatenate(out_alpha), np.concatenate(out_age)

    def assignment(self):
        if self.to is not None and self._asg is None:
            super().assignment()
            ids, pick, delay = self._asg
            o = np.argsort(ids, kind="stable")
            self._asg = (ids[o], pick[o], delay[o])
        return self._asg

    def batches(self, t, cam=None):
        cl = self.body.cloud
        out = []
        for g, (sk, ids, smul, em) in enumerate(self.groups):
            ii, pos, alpha, age = self._raw(t, g)
            if len(ii) == 0:
                continue
            pos, alpha = self._steer(t, ii, pos, alpha)
            sd = cl["seed"][ii]
            col = cl["color"][ii] if self.color is None else np.broadcast_to(self.color, (len(ii), 3)).copy()
            if self.color2 is not None:
                mix = bm.hashf(ii, 43)[:, None]
                col = col * (1 - mix) + self.color2[None] * mix
            u = np.clip(age / self.life, 0, 1)
            size = cl["size"][ii] * smul * self.size * (1.0 + self.grow * u) * (0.7 + 0.9 * bm.hashf(ii, 44) ** 2)
            b = dict(pos=pos, size=size, color=col, alpha=alpha * 0.9 * self.bright * self._crowd(len(ii), t),
                     kind=sk, seed=sd, emit=em, twinkle=0.7 if sk in ("soft", "spark") else 0.15, backlight=0.5)
            if sk in ("flake", "petal", "shard", "butterfly"):
                b["rot"] = _spin(sd, age)
            out.append(b)
        return out

    def particles(self, t):
        cl = self.body.cloud
        ii, pos, alpha, age = self._raw(t)
        pos, alpha = self._steer(t, ii, pos, alpha)
        return dict(id=ii, pos=pos, alpha=alpha, age=age, size=cl["size"][ii], color=cl["color"][ii], seed=cl["seed"][ii])


class Form:
    """The body gathers: its points arrive one after another out of drifting dust, or from given places."""

    def __init__(self, body, t=0.0, dur=4.0, travel=1.8, order="noise", noise=0.6, dust=0.10, source=None, dir=None,
                 speed=0.25, rise=-0.05, push=0.32, spread=0.22, turb=0.38, swirl=0.45, parts=None, amount=None,
                 share=0.5, **kw):
        self.body = body
        self.t, self.dur = float(t), float(dur)
        self.amount = amount
        self.travel = float(min(travel, dur * 0.7))
        self.dust = dust
        self.source = source
        cl = body.cloud
        n = cl["n"]
        if order == "up":
            base = cl["h"]
        elif order == "down":
            base = 1.0 - cl["h"]
        elif order == "out":
            base = _rank(np.hypot(cl["rest"][:, 0], cl["rest"][:, 2]))
        else:
            base = np.zeros(n)
        blot = bm.flow(cl["rest"], 0.0, scale=4.0, speed=0.0, seed=body.seed + 5.0)[:, 0] * 0.5 + 0.5
        o = _rank(_rank(base) * (1 - noise) + noise * (0.55 * blot + 0.45 * cl["seed"]))
        self.tau = self.t + self.travel + (self.dur - self.travel) * o
        if parts is not None:
            self.tau = np.where(np.isin(cl["part"], parts), self.tau, -np.inf)
        d = (0.0, 0.0, 0.0) if dir is None else dir
        self.flight = Flight(dir=d, speed=speed, rise=rise, push=push, spread=spread, turb=turb, swirl=swirl,
                             seed=body.seed + 0.71, tau=0.6)
        self._src_pick = None
        # only a share of the points travel visibly (the others light up where they are as the body forms)
        self.flying = bm.hashf(np.arange(n), 47) < (1.0 if source is not None else share)

    def _clock(self, t):
        if self.amount is None:
            return t
        a = self.amount(t) if callable(self.amount) else self.amount
        return self.t + float(np.clip(a, 0.0, 1.0)) * (self.dur + 0.2)

    def on_body(self, t, on):
        on *= bm.smooth((self._clock(t) - self.tau) / 0.15 + 1.0)

    def _source(self, t, ids):
        src = np.asarray(self.source(t) if callable(self.source) else self.source, np.float64).reshape(-1, 3)
        if self._src_pick is None:
            # match the body's points to the source places in order along the long side of the source shape
            cl = self.body.cloud
            ax = int(np.argmax(src.max(0) - src.min(0)))
            f = self.body.actor.frame(self.t)
            world_rest = bm.qrot(bm.qy(f["heading"]), cl["rest"].astype(np.float64))
            rp = _rank(world_rest[:, ax])
            os_ = np.argsort(src[:, ax], kind="stable")
            self._src_pick = os_[np.minimum((rp * len(src)).astype(np.int64), len(src) - 1)]
        return src[np.minimum(self._src_pick[ids], len(src) - 1)]

    def batches(self, t, cam=None):
        cl = self.body.cloud
        real = t
        t = self._clock(t)
        rev = self.tau - t                       # seconds until each point arrives
        horizon = self.travel if self.dust <= 0 else self.travel * 2.2
        ii = np.where((rev > 0) & (rev < horizon) & (t > self.t - 0.01) & (self.flying | (rev < 0.25)))[0]
        if len(ii) == 0:
            return []
        if self.amount is not None:
            p0, n0 = self.body.points_at(real, ii)
        else:
            p0, n0 = self.body.anchor(("form", 0), self.tau[ii], ii)
        sd = cl["seed"][ii].astype(np.float64)
        a = rev[ii]
        axis = self.body.actor.frame(real)["origin"]
        u = np.clip(a / self.travel, 0.0, 1.0)
        if self.source is not None:
            s = bm.smoother(1.0 - u)
            src = self._source(real, ii)
            arc = self.flight.offset(p0.astype(np.float64), n0.astype(np.float64), a * 0.6, sd, t, axis) * np.sin(np.pi * s)[:, None] * 0.35
            pos = src * (1 - s)[:, None] + p0 * s[:, None] + arc
            alpha = np.clip((self.travel * 1.0 - a) / (0.15 * self.travel), 0.0, 1.0)
        else:
            pos = p0 + self.flight.offset(p0.astype(np.float64), n0.astype(np.float64), a, sd, t, axis)
            near = (1.0 - u) ** 0.8
            alpha = np.maximum(near, self.dust * np.clip((horizon - a) / (0.4 * self.travel), 0, 1))
            if self.amount is None:
                alpha = alpha * np.clip((t - self.t) / 0.4, 0.0, 1.0)
        size = cl["size"][ii] * (1.0 + 0.5 * u)
        return [dict(pos=pos, size=size, color=cl["color"][ii], alpha=alpha * 0.6, kind="soft", seed=cl["seed"][ii],
                     twinkle=0.8, backlight=0.5)]

    def particles(self, t):
        return None


# ---------------------------------------------------------------------------------------------------------
# emitters
# ---------------------------------------------------------------------------------------------------------
class Shed(_Free):
    """The body sheds light all the time and stays whole: particles are born on its surface and drift away."""

    def __init__(self, body, t=None, until=None, n=7000, life=3.2, where=None, dir=None, speed=0.35, rise=0.10,
                 push=0.04, spread=0.10, turb=0.35, swirl=0.0, color=None, size=1.0, bright=1.0, sprite="soft",
                 to=None, **kw):
        self.body = body
        self.t0 = body.t_start if t is None else float(t)
        self.t1 = np.inf if until is None else float(until)
        self.n, self.life = int(n), float(life)
        cl = body.cloud
        pool = np.arange(cl["n"])
        if where == "back":
            pool = pool[cl["rest"][:, 2] < np.percentile(cl["rest"][:, 2], 45)]
        elif where == "top":
            pool = pool[cl["h"] > 0.6]
        elif where is not None:
            pool = pool[np.isin(cl["part"], where)]
        self.pool = pool[np.argsort(bm.hashf(pool, 51), kind="stable")[:max(min(len(pool), 9000), 1)]]
        i = np.arange(self.n)
        self.phase = bm.hashf(i, 52)
        self.lives = self.life * (0.6 + 0.8 * bm.hashf(i, 53))
        self.sd = bm.hashf(i, 54)
        self.auto_dir = dir is None
        self.flight = Flight(dir=(0, 0, 0) if dir is None else dir, speed=speed, rise=rise, push=push, spread=spread,
                             turb=turb, swirl=swirl, seed=body.seed + 0.93, wind=body.wind, hang=kw.get("hang"))
        self.speed = speed
        self.color = None if color is None else _col(color)
        self.size, self.bright, self.sprite = size, bright, sprite
        self._init_free(to)

    def _raw(self, t):
        tq = self._frozen(t)
        k = np.floor((tq - self.t0) / self.lives - self.phase)
        birth = self.t0 + (k + self.phase) * self.lives
        m = (k >= 0) & (birth <= self.t1) & (birth >= self.t0)
        ids = np.where(m)[0]
        if len(ids) == 0:
            return ids, np.zeros((0, 3)), np.zeros(0), np.zeros(0)
        b = birth[ids]
        src = self.pool[(bm.hashf(ids * 7919 + k[ids].astype(np.int64), 55) * len(self.pool)).astype(np.int64) % len(self.pool)]
        p0, n0 = self.body.anchor(("shed", self.index), b, src, pool=self.pool)
        age = t - b
        sd = np.mod(self.sd[ids] + 0.618 * k[ids], 1.0)
        # the air stands still while the body moves on: what it sheds is left behind and drifts
        pos = p0 + self.flight.offset(p0.astype(np.float64), n0.astype(np.float64), age, sd, t, None)
        self._last_src = src
        return ids, pos, _fade(tq - b, self.lives[ids], fin=0.2, fout=0.7), age

    def batches(self, t, cam=None):
        ids, pos, alpha, age = self._raw(t)
        if len(ids) == 0:
            return []
        pos, alpha = self._steer(t, ids, pos, alpha)
        cl = self.body.cloud
        src = self._last_src
        col = cl["color"][src] if self.color is None else np.broadcast_to(self.color, (len(ids), 3))
        u = np.clip(age / self.lives[ids], 0, 1)
        size = cl["size"][src] * self.size * (0.8 + 1.6 * self.sd[ids] ** 3) * (1.0 + 0.8 * u)
        b = dict(pos=pos, size=size, color=col, alpha=alpha * 0.8 * self.bright, kind=self.sprite, seed=self.sd[ids],
                 twinkle=0.8, backlight=0.6)
        if self.sprite in ("flake", "petal", "shard", "butterfly"):
            b["rot"] = _spin(self.sd[ids], age)
        return [b]

    def particles(self, t):
        ids, pos, alpha, age = self._raw(t)
        pos, alpha = self._steer(t, ids, pos, alpha)
        cl = self.body.cloud
        src = self._last_src if len(ids) else np.zeros(0, np.int64)
        return dict(id=ids, pos=pos, alpha=alpha, age=age, size=cl["size"][src], color=cl["color"][src], seed=self.sd[ids])


class Blow(_Free):
    """A stream of particles blown from the open palm (the body's "blow" gesture holds the palm up).

    t, dur     when the breath starts and how long it lasts
    n          how many particles; gather: seconds before t in which they glimmer on the palm
    reach      metres the stream travels; life: seconds each particle lives
    """

    def __init__(self, body, t, dur=3.0, side="R", n=5000, gather=1.2, life=4.0, reach=2.2, spread=0.22, turb=0.4,
                 rise=0.05, color=None, color2=None, size=1.0, bright=1.0, dir=None, to=None, **kw):
        self.body = body
        self.t, self.dur, self.side = float(t), float(dur), side
        self.n, self.gather, self.life, self.reach = int(n), float(gather), float(life), float(reach)
        i = np.arange(self.n)
        self.birth = self.t + self.dur * bm.hashf(i, 61) ** 1.3
        self.sd = bm.hashf(i, 62)
        self.disc = (bm.hashf(i, 63) ** 0.5 * 0.045, bm.hashf(i, 64) * 2 * np.pi, bm.hashf(i, 65))
        self.spread, self.turb, self.rise = spread, turb, rise
        self.dir = None if dir is None else np.asarray(dir, np.float64)
        c = body.color if color is None else _col(color)
        c2 = body.color2 if color2 is None else _col(color2)
        mix = bm.hashf(i, 66)[:, None]
        self.color = c[None] * (1 - mix) + c2[None] * mix
        self.size0 = (0.004 + 0.012 * bm.hashf(i, 67) ** 4) * size * body.rig.height / 1.6
        self.bright = bright
        self._palm = {}
        self._init_free(to)

    def _palm_at(self, tb):
        """Palm centre, palm normal, finger direction and blow direction at binned times."""
        bins = np.floor(tb / (BIN * 0.5)).astype(np.int64)
        c = np.empty((len(tb), 3))
        n = np.empty((len(tb), 3))
        f = np.empty((len(tb), 3))
        d = np.empty((len(tb), 3))
        for b in np.unique(bins):
            if b not in self._palm:
                tt = (b + 0.5) * BIN * 0.5
                pc, pn, pf = self.body.actor.palm(tt, self.side)
                mouth, fwd = self.body.actor.mouth(tt)
                if self.dir is not None:
                    bd = self.dir
                else:
                    bd = pc - mouth
                    bd = bd / max(np.linalg.norm(bd), 1e-9) * 0.55 + fwd * 0.6 + UP * 0.12
                self._palm[int(b)] = (pc, pn, pf, bd / np.linalg.norm(bd))
            m = bins == b
            c[m], n[m], f[m], d[m] = self._palm[int(b)]
        return c, n, f, d

    def _raw(self, t):
        tq = self._frozen(t)
        early = (tq < self.birth) & (bm.hashf(np.arange(self.n), 70) > 0.12)       # most wait unseen
        m = (self.birth - self.gather <= tq) & (tq - self.birth < self.life) & ~early
        ids = np.where(m)[0]
        if len(ids) == 0:
            return ids, np.zeros((0, 3)), np.zeros(0), np.zeros(0)
        b = self.birth[ids]
        flying = t >= b
        tb = np.where(flying, b, t)
        c, n, f, d = self._palm_at(tb)
        r, a, hgt = self.disc[0][ids], self.disc[1][ids], self.disc[2][ids]
        k = self.body.rig.height / 1.6
        side = np.cross(n, f)
        p0 = c + (f * (r * np.cos(a))[:, None] + side * (r * np.sin(a))[:, None]) * k + n * (0.006 + 0.03 * hgt ** 2)[:, None] * k
        age = np.maximum(t - b, 0.0)
        sd = self.sd[ids]
        pace = 0.6 + 0.8 * bm.hashf(ids, 68)
        dd = d + _hvec(sd, 69) * self.spread
        dd /= np.linalg.norm(dd, axis=1, keepdims=True)
        tau = 1.1
        travel = self.reach * pace * (1.0 - np.exp(-age / tau)) + 0.12 * age
        off = dd * travel[:, None]
        off[:, 1] += self.rise * age
        g = 1.0 - np.exp(-age / 0.8)
        off += bm.flow((p0 + off) * 1.4, age * 0.5 + t * 0.1, speed=1.0, seed=self.body.seed + 1.7) * (self.turb * g)[:, None]
        pos = p0 + off
        wait = np.clip((tq - (b - self.gather)) / max(self.gather * 0.6, 1e-3), 0.0, 1.0)
        alpha = np.where(tq >= b, _fade(tq - b + 0.2, self.life, fin=0.1, fout=0.6), 0.22 * wait)
        return ids, pos, alpha, age

    def batches(self, t, cam=None):
        ids, pos, alpha, age = self._raw(t)
        if len(ids) == 0:
            return []
        pos, alpha = self._steer(t, ids, pos, alpha)
        u = np.clip(age / self.life, 0, 1)
        big = self.sd[ids] > 0.975
        out = [dict(pos=pos[~big], size=(self.size0[ids] * (1.0 + 1.5 * u))[~big], color=self.color[ids][~big],
                    alpha=alpha[~big] * 0.9 * self.bright, kind="soft", seed=self.sd[ids][~big], twinkle=0.85, backlight=0.6)]
        if big.any():
            out.append(dict(pos=pos[big], size=(self.size0[ids] * 1.2)[big], color=self.color[ids][big],
                            alpha=alpha[big] * self.bright, kind="spark", seed=self.sd[ids][big], twinkle=1.0,
                            emit=2.5, backlight=0.6))
        return out

    def particles(self, t):
        ids, pos, alpha, age = self._raw(t)
        pos, alpha = self._steer(t, ids, pos, alpha)
        return dict(id=ids, pos=pos, alpha=alpha, age=age, size=self.size0[ids], color=self.color[ids], seed=self.sd[ids])


class Birds(_Free):
    """Birds leave the silhouette: each rises out of a point of the body and flies off (ref 08)."""

    def __init__(self, body, t, dur=3.0, n=36, dir=None, speed=2.4, life=7.0, size=0.11, color="#ffffff", spread=0.35,
                 rise=0.5, where=None, bright=1.0, to=None, **kw):
        self.body = body
        self.t, self.dur, self.n, self.life = float(t), float(dur), int(n), float(life)
        cl = body.cloud
        pool = np.arange(cl["n"])
        if where is not None:
            pool = pool[np.isin(cl["part"], where)]
        else:
            pool = pool[cl["h"] > 0.45]
        i = np.arange(self.n)
        self.src = pool[(bm.hashf(i, 81) * len(pool)).astype(np.int64) % len(pool)]
        self.tau = self.t + self.dur * _rank(bm.hashf(i, 82) * 0.6 + 0.4 * (1 - cl["h"][self.src]))
        self.sd = bm.hashf(i, 83)
        f0 = body.actor.frame(self.t)
        if dir is None:
            dir = bm.qrot(bm.qy(f0["heading"]), [0.3, 0.35, 1.0])
        d = np.asarray(dir, np.float64)
        d = d / np.linalg.norm(d)
        dd = d[None] + _hvec(self.sd, 84) * spread
        dd[:, 1] = np.abs(dd[:, 1]) * 0.6 + rise * 0.3
        self.dirs = dd / np.linalg.norm(dd, axis=1, keepdims=True)
        self.speed = speed * (0.75 + 0.5 * bm.hashf(i, 85))
        self.size = size * (0.7 + 0.6 * bm.hashf(i, 86)) * body.rig.height / 1.6
        self.color = _col(color)
        # dark birds (ref 08: silhouettes on a pale sky) are painted in their true colour: light alone cannot
        # darken a bright sky
        self.paint = 1.0 if float(np.mean(self.color)) < 0.12 else 0.0
        if self.paint and isinstance(color, str):
            from .api import show as _show
            self.color = np.asarray(_show(color), np.float64)
        self.bright = bright
        self._init_free(to)

    def _path(self, t, ids):
        p0, _ = self.body.anchor(("birds", self.index), self.tau[ids], self.src[ids])
        age = t - self.tau[ids]
        a = np.maximum(age, 0.0)
        ease = a - 0.7 * (1.0 - np.exp(-a / 0.7))
        d = self.dirs[ids]
        side = np.cross(d, UP)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        sd = self.sd[ids]
        weave = np.sin(a * (0.9 + 0.8 * sd) + sd * 20.0) * 0.35 * np.minimum(a, 1.5)
        bob = np.sin(a * (1.7 + sd) + sd * 9.0) * 0.12 * np.minimum(a, 1.0)
        pos = p0 + d * (self.speed[ids] * ease)[:, None] + side * weave[:, None] + UP[None] * (bob + 0.15 * ease)[:, None]
        return pos, age

    def _raw(self, t):
        tq = self._frozen(t)
        m = (self.tau <= tq) & (tq - self.tau < self.life)
        ids = np.where(m)[0]
        if len(ids) == 0:
            return ids, np.zeros((0, 3)), np.zeros(0), np.zeros(0)
        pos, age = self._path(t, ids)
        return ids, pos, _fade(tq - self.tau[ids], self.life, fin=0.5, fout=0.3), age

    def batches(self, t, cam=None):
        ids, pos, alpha, age = self._raw(t)
        if len(ids) == 0:
            return []
        p2, _ = self._path(t + 0.05, ids)
        pos, alpha = self._steer(t, ids, pos, alpha)
        if self.to is not None and t > self.to["t"]:
            p2s, _ = self._steer(t + 0.05, ids, p2, alpha)
            vel = (p2s - pos) / 0.05
        else:
            vel = (p2 - pos) / 0.05
        if cam is not None:
            r, u, _f = cam.basis()
            rot = np.arctan2(vel @ u, vel @ r)
        else:
            rot = np.arctan2(vel[:, 1], np.hypot(vel[:, 0], vel[:, 2]))
        grow = np.clip(age / 0.8, 0.15, 1.0)
        return [dict(pos=pos, size=self.size[ids] * grow, color=self.color, alpha=alpha * 0.95 * self.bright, kind="bird",
                     rot=rot, seed=self.sd[ids], twinkle=0.0, vel=vel, paint=self.paint, paint_light=0.0)]

    def particles(self, t):
        ids, pos, alpha, age = self._raw(t)
        pos, alpha = self._steer(t, ids, pos, alpha)
        return dict(id=ids, pos=pos, alpha=alpha, age=age, size=self.size[ids],
                    color=np.broadcast_to(self.color, (len(ids), 3)), seed=self.sd[ids])


def make(body, spec, index):
    """An effect object for a body from its dict (or (kind, t, dict))."""
    if isinstance(spec, (tuple, list)):
        d = dict(spec[2]) if len(spec) > 2 else {}
        d.update(kind=spec[0], t=spec[1])
        spec = d
    spec = dict(spec)
    kind = spec.pop("kind")
    if kind not in EFFECTS:
        raise ValueError("effect kind must be one of %s, got %r" % (EFFECTS, kind))
    # batch=dict(...) is merged into every batch the effect draws (paint=1 for dark painted flakes on a day sky);
    # a list of dicts draws each batch once per dict (a dark painted shard and its edge of light)
    extra = spec.pop("batch", None)
    cls = dict(form=Form, shed=Shed, blow=Blow, birds=Birds).get(kind)
    if cls is None:
        e = Release.__new__(Release)
        e.index = index
        e.__init__(body, kind, **spec)
    else:
        e = cls.__new__(cls)
        e.index = index
        e.__init__(body, **spec)
    e.kind = kind
    if extra:
        raw = e.batches
        ways = [dict(x) for x in extra] if isinstance(extra, (list, tuple)) else [dict(extra)]

        def batches(t, cam=None, raw=raw, ways=ways):
            return [dict(b, **w) for b in raw(t, cam) for w in ways]
        e.batches = batches
    return e


# ---------------------------------------------------------------------------------------------------------
# point sets of their own
# ---------------------------------------------------------------------------------------------------------
class Flare(_Free):
    """A flash of light at a point: a bright core, a burst of sparks, slow embers (where two hands touch).

    at      the point (x, y, z), or a function of time that gives it
    t       when it flashes; strength: how bright; n: how many sparks
    scale   size of the whole flash: 1 suits two hands in close-up (a core of a few centimetres, sparks
            reaching about 35 cm); 2.5 is the size it had before (a flash for a wide shot)
    reach   metres the sparks fly (default 0.36 times scale)
    """

    def __init__(self, at, t, color="#fff1d0", color2="#9fd0ff", n=900, strength=1.0, reach=None, life=2.2, seed=3.0,
                 to=None, scale=1.0):
        self.at, self.t = at, float(t)
        self.scale = float(scale)
        reach = 0.36 * self.scale if reach is None else reach
        self.n, self.strength, self.reach, self.life = int(n), float(strength), float(reach), float(life)
        i = np.arange(self.n)
        self.sd = bm.hashf(i, 91 + int(seed))
        self.dirs = _hvec(self.sd, 92)
        self.pace = bm.hashf(i, 93) ** 1.6
        mix = bm.hashf(i, 94)[:, None]
        self.color = _col(color)[None] * (1 - mix) + _col(color2)[None] * mix
        self.seed = seed
        self._init_free(to)

    def _centre(self, t):
        return np.asarray(self.at(t) if callable(self.at) else self.at, np.float64)

    def _raw(self, t):
        tq = self._frozen(t)
        if tq < self.t or tq - self.t > self.life:
            return np.zeros(0, np.int64), np.zeros((0, 3)), np.zeros(0), np.zeros(0)
        a = t - self.t
        c = self._centre(self.t)
        sc = self.scale
        travel = self.reach * self.pace * (1.0 - np.exp(-a / 0.45)) + 0.02 * sc * a
        pos = c + self.dirs * travel[:, None]
        pos += bm.flow(pos * 2.0 / sc, a * 0.6, speed=1.0, seed=self.seed) * 0.07 * sc * (1.0 - np.exp(-a / 0.8))
        pos[:, 1] += 0.025 * sc * a
        aq = tq - self.t
        alpha = np.clip(aq / 0.05, 0, 1) * np.clip(1.0 - aq / (self.life * (0.5 + 0.5 * self.sd)), 0.0, 1.0) ** 1.5
        return np.arange(self.n), pos, alpha, np.full(self.n, a)

    def sample(self, t):
        a = t - self.t
        out = []
        sc = self.scale
        if -0.6 < a < 1.2:
            # the core: swells just before the touch, flashes, dies away
            k = np.exp(-max(a, 0.0) / 0.22) if a >= 0 else np.exp(a / 0.2) * 0.35
            c = self._centre(t)
            out.append(dict(pos=c[None], size=(0.035 + 0.07 * max(a, 0.0)) * sc, color=self.color.mean(0),
                            alpha=min(k, 1.0), kind="soft", emit=5.0 * self.strength * k, dof=0.3))
            out.append(dict(pos=c[None], size=0.018 * sc, color=(1.0, 1.0, 1.0), alpha=min(k, 1.0), kind="spark",
                            emit=16.0 * self.strength * k, dof=0.0))
        ids, pos, alpha, age = self._raw(t)
        if len(ids):
            pos, alpha = self._steer(t, ids, pos, alpha)
            out.append(dict(pos=pos, size=(0.0015 + 0.005 * self.sd ** 4) * sc, color=self.color, alpha=alpha,
                            kind="soft", seed=self.sd, emit=1.5 + 4.0 * self.strength * np.exp(-age / 0.4),
                            twinkle=0.9))
        return out

    def particles(self, t):
        ids, pos, alpha, age = self._raw(t)
        pos, alpha = self._steer(t, ids, pos, alpha)
        return dict(id=ids, pos=pos, alpha=alpha, age=age, size=((0.0015 + 0.005 * self.sd ** 4) * self.scale)[ids],
                    color=self.color[ids], seed=self.sd[ids])

    def free(self, t):
        return _free_report([self], t)


def _free_report(effects, t, dt=0.02):
    """Plain arrays of every free particle of the given effects at t (see the module text)."""
    parts = []
    for k, e in enumerate(effects):
        a = e.particles(t)
        if a is None or len(a["id"]) == 0:
            continue
        b = e.particles(t + dt)
        vel = np.zeros_like(a["pos"])
        if b is not None and len(b["id"]) == len(a["id"]):
            vel = (b["pos"] - a["pos"]) / dt
        a["vel"] = vel
        a["effect"] = np.full(len(a["id"]), getattr(e, "index", k), np.int64)
        parts.append(a)
    keys = ("id", "pos", "vel", "size", "color", "alpha", "seed", "age", "effect")
    if not parts:
        return {k: np.zeros((0, 3)) if k in ("pos", "vel", "color") else np.zeros(0) for k in keys}
    return {k: np.concatenate([np.asarray(p[k]) for p in parts]) for k in keys}


class Takeover:
    """Flies particles given as plain arrays to target places: for a point set that takes another's particles.

    state     dict(pos (K, 3), vel (K, 3), color (K, 3), size (K,), alpha (K,), seed (K,)): for example what
              body.free(t) returned
    t         the hand-over time (the moment the state was taken)
    targets   (K, 3) places (or a function of time), one per particle, in the same order
    arrive    seconds of flight; stagger: (K,) or a number of extra seconds per particle
    """

    def __init__(self, state, t, targets, arrive=1.5, stagger=0.0, kind="soft", until=None, twinkle=0.7):
        self.s = {k: np.asarray(v) for k, v in state.items()}
        self.t, self.targets, self.arrive = float(t), targets, float(arrive)
        self.stagger = stagger
        self.kind, self.until, self.twinkle = kind, until, twinkle

    def sample(self, t):
        if t < self.t or len(self.s["pos"]) == 0:
            return []
        tg = np.asarray(self.targets(t) if callable(self.targets) else self.targets, np.float64).reshape(-1, 3)
        k = len(self.s["pos"])
        a = np.broadcast_to(np.asarray(t - self.t - self.stagger, np.float64), (k,))
        s = bm.smoother(a / self.arrive)
        # start along the old velocity, end at rest on the target
        coast = self.s["pos"] + self.s["vel"] * (np.clip(a, 0.0, self.arrive) * 0.5)[:, None]
        pos = coast * (1 - s)[:, None] + tg * s[:, None]
        alpha = self.s["alpha"] * (1 - s) + np.maximum(self.s["alpha"], 0.85) * s
        if self.until is not None:
            alpha = alpha * (1.0 - bm.ramp(t, self.until, self.until + 0.3))
        return dict(pos=pos, size=self.s["size"], color=self.s["color"], alpha=alpha, kind=self.kind,
                    seed=self.s["seed"], twinkle=self.twinkle)
