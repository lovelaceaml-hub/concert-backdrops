"""A gathering crowd of people of light, and a light passed from hand to hand (2026-11-15, branch engine-gathering).

GATHERING  many small people of light walk in from the sides, slow down, turn toward the centre and settle with
           breathing idle motion. Each one is a light version of the rig in engine/rig.py: the same proportions,
           the same walk cycle (planted feet, striding legs, swinging arms, a robe that follows the legs and lags
           behind the motion), but all the people are posed together with numpy arrays (one row per person) and
           share one spark template (instancing), with a few hundred sparks each. 50 to 200 people stay fast.
PASS_LIGHT a small flame passes from hand to hand: each giver turns to the next person and reaches out, the flame
           hops across with a spark trail, the receiver reaches to take it, then holds it in cupped hands and
           begins to glow. Optionally the flame first comes down from the arch, and at the end everyone lifts their
           light, the lights rise to the arch and the arch brightens.

Everything is a pure function of time (no state carried between frames), so the cloud workers that render a
video in parts agree with each other. How a song uses this: engine/UPGRADE-HOWTO.md section K.
No faces (heads are soft glows), everyone wears a long robe. Text protection is automatic: the layer is drawn
into the light buffer before render.py dims the light behind the letters.
"""
import math

import numpy as np
import moderngl

import song as S
import rig as RG

TAU = 2.0 * math.pi
A = RG.ADULT
LIMB = A["thigh"] + A["shin"]
BETA = 0.62
HANG = np.array(RG.HANG)
HOLD = np.array((0.42, 0.25, 1.50, -0.62))      # forearms forward and in: cupped hands hold the flame
LIFT = np.array((2.05, 0.20, 2.55, -0.30))      # the light lifted up high
YAW_WALK = 0.30                                  # nearly side on while walking, so the stride reads
YAW_SETTLE = 0.80                                # three quarter, turned toward the centre, once settled

VS = """
#version 330
in vec2 aPos; in vec2 aSz; in vec3 aCol;
uniform float uPx;
out vec3 vCol; out float vSharp;
void main(){ vCol = aCol; vSharp = aSz.y; gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0); gl_PointSize = aSz.x*uPx; }
"""
FS = """
#version 330
in vec3 vCol; in float vSharp; out vec4 o;
void main(){ vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  o = vec4(vCol*exp(-r2*vSharp)*(1.0-r2*r2*0.15), 1.0); }
"""


def ss(a, b, x):
    x = np.asarray(x, dtype=np.float64)
    if b == a:
        return (x >= a) * 1.0
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def _val(v, t, default):
    if v is None:
        return default
    return v(t) if callable(v) else v


def _lin(c):
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def _armdir(el, az, side):
    """(N,) angles -> (N,3) directions, as rig._armdir."""
    se = np.sin(el)
    return np.stack([se * np.cos(az), -np.cos(el), side * se * np.sin(az)], -1)


def _disc(axis, th, r):
    """Offsets (N,k,3) in the disc perpendicular to each person's bone axis (N,3)."""
    a = axis / np.maximum(np.linalg.norm(axis, axis=-1, keepdims=True), 1e-9)
    e1 = np.cross(a, np.array([0.0, 0.0, 1.0]))
    e1 /= np.maximum(np.linalg.norm(e1, axis=-1, keepdims=True), 1e-9)
    e2 = np.cross(a, e1)
    return (np.cos(th) * r)[..., None] * e1[:, None, :] + (np.sin(th) * r)[..., None] * e2[:, None, :]


def _ik(H, Af, l1, l2):
    """Knees (N,2) of two-bone legs from hips H to ankles Af (N,2), bending forward (+x)."""
    D = Af - H
    dist = np.linalg.norm(D, axis=1)
    u = D / np.maximum(dist, 1e-6)[:, None]
    dist = np.clip(dist, 1e-4, (l1 + l2) * 0.9999)
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = np.sqrt(np.maximum(l1 * l1 - a * a, 0.0))
    n = np.stack([-u[:, 1], u[:, 0]], 1)
    n = np.where(n[:, :1] < 0, -n, n)
    return H + u * a[:, None] + n * h[:, None]


# ---------------------------------------------------------------- the shared spark template (instancing)
class Template:
    """One set of spark parameters shared by every person; each person turns it by its own offsets."""

    def __init__(self, rng, n):
        parts = [("robe", 0.38), ("torso", 0.13), ("head", 0.10), ("arm", 0.17), ("hand", 0.05), ("leg", 0.10),
                 ("foot", 0.07)]
        c = {k: max(int(n * v), 8) for k, v in parts}
        self.c = c
        th, r = RG._sample_unit_disc(rng, c["robe"], edge=0.72)
        self.robe = dict(v=rng.random(c["robe"]) ** 0.85, th=th, r=r)
        th, r = RG._sample_unit_disc(rng, c["torso"], edge=0.65)
        self.torso = dict(s=rng.random(c["torso"]), th=th, r=r)
        self.head = dict(d=RG._unit3(rng, c["head"]), r=rng.random(c["head"]) ** 0.6)
        k = c["arm"]
        th, r = RG._sample_unit_disc(rng, k, edge=0.6)
        self.arm = dict(side=np.where(np.arange(k) % 2 == 0, 1.0, -1.0), seg=(np.arange(k) // 2) % 2,
                        s=rng.random(k), th=th, r=r)
        k = c["hand"]
        self.hand = dict(side=np.where(np.arange(k) % 2 == 0, 1.0, -1.0), s=rng.random(k) ** 0.8,
                         d=RG._unit3(rng, k), r=rng.random(k) ** 0.5)
        k = c["leg"]
        th, r = RG._sample_unit_disc(rng, k, edge=0.5)
        self.leg = dict(side=np.where(np.arange(k) % 2 == 0, 1.0, -1.0), seg=(np.arange(k) // 2) % 2,
                        s=rng.random(k), th=th, r=r)
        k = c["foot"]
        self.foot = dict(side=np.where(np.arange(k) % 2 == 0, 1.0, -1.0), s=rng.random(k), d=RG._unit3(rng, k),
                         r=rng.random(k) ** 0.5)
        self.K = sum(c.values())
        self.seed = rng.random((self.K, 3))       # twinkle speed, twinkle phase, size
        self.size = 1.25 + 2.3 * self.seed[:, 2] ** 3


# ---------------------------------------------------------------- the crowd
class Crowd:
    def __init__(self, m, pl, aspect, star_pos):
        self.m, self.pl, self.aspect = m, pl, aspect
        self.star_pos = [tuple(p) for p in star_pos] if star_pos else [(0.5, 0.9)]
        # CAMERA: the crowd moves with the shore, the arch does not. fix(p) gives a fixed screen point (a light
        # of the arch, the flame's source) in the crowd's own coordinates; Gathering.draw sets it every frame
        self.fix = lambda p: p
        seed = int(m.get("seed", 7))
        rng = np.random.default_rng(seed)
        N = self.N = int(m.get("count", 80))
        self.t0 = float(m.get("t0", 0.0))
        self.t1 = float(m.get("t1", 1e9))
        self.dis = float(m.get("dissolve", 3.0))
        cx, cy = m.get("center", (0.5, 0.345))
        self.cx, self.cy = float(cx), float(cy)
        sp = m.get("spread", 0.30)
        sx, sdepth = (float(sp[0]), float(sp[1])) if isinstance(sp, (tuple, list)) else (float(sp), 0.03)
        hole = float(m.get("hole", 0.0))
        h0 = m.get("height", 0.13)
        h0, hvar = (float(h0[0]), float(h0[1])) if isinstance(h0, (tuple, list)) else (float(h0), 0.12)
        self.tpl = Template(np.random.default_rng(seed + 1), int(m.get("detail", 420)))

        # slots: staggered rows on the shore, so the people behind stand in the gaps of the row in front;
        # back rows a little higher, smaller and dimmer
        rows = max(int(m.get("rows", 3)), 1)
        per = np.diff(np.round(np.linspace(0, N, rows + 1)).astype(int))
        xs_l, dp_l = [], []
        for k in range(rows):
            n = int(per[k])
            u = (np.arange(n) + 0.5 + (0.5 if k % 2 else 0.0)) / (n + 0.5) * 2 - 1
            u = u + (rng.random(n) - 0.5) * 0.5 * 2 / max(n, 1)
            if hole > 0:
                u = np.sign(u) * (hole + (1 - hole) * np.abs(u))
            xs_l.append(u)
            dp_l.append(np.clip(k / max(rows - 1, 1) + (rng.random(n) - 0.5) * 0.35 / rows, 0, 1))
        xs, depth = np.concatenate(xs_l), np.concatenate(dp_l)
        keep = np.arange(N)
        self.r = depth[keep]
        self.tx = self.cx + xs[keep] * sx
        self.silk = m.get("look", getattr(S, "FIGURE_LOOK", None)) == "silk"
        if self.silk and not m.get("cluster"):   # look="silk": uneven spacing, unless the song groups them itself
            import figure_look as FL
            self.tx = FL.cluster_x(self.tx, self.cx, float(m.get("spacing", 1.0)), seed)
        self.fy = self.cy + self.r * sdepth
        self.h = h0 * (1 + hvar * (rng.random(N) * 2 - 1)) * (1 - 0.30 * self.r)
        child = rng.random(N) < float(m.get("children", 0.12))
        self.h = np.where(child, self.h * 0.72, self.h)
        self.bright = (1.0 - 0.35 * self.r) * (0.85 + 0.3 * rng.random(N))
        cols = m.get("colors", ("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f6d4ff"))
        cols = [_lin(c) for c in cols]
        self.col = np.array([cols[k] for k in rng.integers(0, len(cols), N)])
        self.ph = rng.random(N)
        self.off = rng.random((N, 4))             # spark template turns per person

        # where they come from
        sides = m.get("sides", ("left", "right"))
        if isinstance(sides, str):
            sides = (sides,)
        if set(sides) >= {"left", "right"}:
            from_left = self.tx < self.cx
        else:
            from_left = np.full(N, sides[0] == "left")
        self.sx = np.where(from_left, -0.05 - 0.03 * rng.random(N), 1.05 + 0.03 * rng.random(N))
        self.fw = np.where(from_left, 1.0, -1.0)  # walking direction on screen
        tc = np.where(np.abs(self.tx - self.cx) < 1e-3, self.fw, np.sign(self.cx - self.tx))
        self.ys = np.where(tc == self.fw, YAW_SETTLE, math.pi - YAW_SETTLE)   # turn round if the centre is behind
        self.orient = tc                           # which way they face once settled
        spd = float(m.get("speed", 1.0))          # figure heights per second
        self.v = spd * (0.80 + 0.40 * rng.random(N)) * np.where(child, 1.15, 1.0)
        self.L = np.abs(self.tx - self.sx) * aspect / self.h
        self.D = np.minimum(0.55, 0.3 * self.L)
        self.Tc = (self.L - self.D) / self.v
        self.Td = 2 * self.D / self.v
        walk = self.Tc + self.Td
        arrive_by = float(m.get("arrive_by", self.t0 + 14.0))
        rank = np.argsort(np.argsort(np.abs(self.tx - self.cx) + 0.06 * rng.random(N)))
        q = 0.30 + 0.70 * rank / max(N - 1, 1)
        self.Ta = np.maximum(self.t0 + walk, self.t0 + (arrive_by - self.t0) * q)
        self.Te = self.Ta - walk
        self.leave = self.t1 + 0.8 * rng.random(N)
        self.has_pass = pl is not None
        if self.has_pass:
            self._plan_pass(rng)

    # ------------------------------------------------------------ PASS_LIGHT: who passes to whom, and when
    def _plan_pass(self, rng):
        pl, N, asp = self.pl, self.N, self.aspect
        t0 = float(pl.get("t0", self.t0 + 15.0))
        speed = float(pl.get("speed", 0.15))      # screen widths per second while the flame hops
        lead = float(pl.get("reach", 0.40))
        hold = float(pl.get("hold", 0.25))
        self.lead = lead
        self.fcol = _lin(pl.get("color", "#ffe2a0"))
        hx = self.tx + self.orient * 0.16 * self.h / asp     # where the held flame rests (screen)
        hy = self.fy + 0.52 * self.h
        self.Tr = np.full(N, np.inf)
        self.Trs = np.full(N, np.inf)              # when each receiver starts to reach
        self.rmx, self.rmy = hx.copy(), hy.copy()  # where each receiver reaches to
        hops = []                                  # (giver, child, hop start, arrival)
        path = pl.get("path", "crowd")
        start = pl.get("start", "center")
        if isinstance(start, (int, np.integer)):
            first = int(start)
        elif start == "left":
            first = int(np.argmin(self.tx + 0.02 * self.r))
        elif start == "right":
            first = int(np.argmax(self.tx - 0.02 * self.r))
        else:
            sxp = self.cx if start == "center" else float(start[0])
            first = int(np.argmin(np.abs(self.tx - sxp) + 0.5 * self.r * 0.03))
        src = pl.get("source", None)
        if src == "arch":
            src = self.star_pos[len(self.star_pos) // 2]
        self.src = None if src is None else (float(src[0]), float(src[1]))
        Tfirst = max(t0, self.Ta[first] + 0.8)
        if self.src is not None:
            desc = float(pl.get("descent", 2.5))
            self.src_t = (Tfirst, Tfirst + desc)
            Tfirst += desc
            self.rmx[first], self.rmy[first] = hx[first], hy[first] + 0.30 * self.h[first]
            self.Trs[first] = Tfirst - desc * 0.6
        else:
            self.Trs[first] = Tfirst - lead
        self.Tr[first] = Tfirst

        def hop(g, c, ready):
            mx = 0.5 * (hx[g] + hx[c])
            my = 0.5 * (hy[g] + hy[c]) + 0.04 * min(self.h[g], self.h[c])
            dist = math.hypot((hx[c] - hx[g]) * asp, hy[c] - hy[g]) / asp
            Tg = max(ready, self.Ta[c] + 0.6) + lead
            Tarr = Tg + max(dist / speed, 0.25)
            self.Tr[c], self.Trs[c] = Tarr, Tg - lead
            self.rmx[c], self.rmy[c] = mx, my
            hops.append((g, c, Tg, Tarr, mx, my))
            return Tarr

        if isinstance(path, str) and path == "crowd":
            # every lit person passes on to the people near them who still wait, one after another; at each
            # step the hand-over that can arrive soonest happens next, so the light spreads out like a wave
            free = np.full(N, np.inf)
            free[first] = Tfirst + hold
            claimed = np.zeros(N, bool)
            claimed[first] = True
            P = np.stack([hx * asp, hy], 1)
            Dm = np.linalg.norm(P[:, None] - P[None], axis=2) / asp
            near = np.sort(Dm + np.eye(N) * 9, axis=0)[2]           # each person's second nearest neighbour
            far = Dm > np.maximum(float(pl.get("reach_far", 2.2)) * near[None, :], 0.04)       # only hand to a near neighbour
            for _ in range(N - 1):
                ready = np.maximum(free[:, None], self.Ta[None, :] + 0.6)
                cost = ready + lead + np.maximum(Dm / speed, 0.25)
                cost[:, claimed] = np.inf
                if np.isfinite(np.where(far, np.inf, cost)).any():
                    cost = np.where(far, np.inf, cost)
                g, c = np.unravel_index(int(np.argmin(cost)), cost.shape)
                if not np.isfinite(cost[g, c]):
                    break
                claimed[c] = True
                Tarr = hop(g, c, free[g])
                free[g] = Tarr + 0.25
                free[c] = Tarr + hold
        else:
            if isinstance(path, str):              # "line": along the crowd from the start side
                order = list(np.argsort(self.tx if self.tx[first] <= self.cx else -self.tx))
                order.remove(first)
                order = [first] + order
            else:                                  # a list of screen points: the people nearest them, in order
                order, used = [first], {first}
                for p in path:
                    d = np.hypot((self.tx - p[0]) * asp, self.fy - p[1])
                    d[list(used)] = 1e9
                    k = int(np.argmin(d))
                    used.add(k)
                    order.append(k)
            ready = Tfirst + hold
            for g, c in zip(order[:-1], order[1:]):
                ready = hop(g, c, ready) + hold
        self.hops = hops
        # each person's gives, padded to (N, M)
        M = max([sum(1 for h in hops if h[0] == i) for i in range(N)] + [1])
        self.gT = np.full((N, M, 2), np.inf)
        self.gM = np.zeros((N, M, 2))
        cnt = np.zeros(N, int)
        for g, c, Tg, Tarr, mx, my in hops:
            j = cnt[g]
            self.gT[g, j] = (Tg, Tarr)
            self.gM[g, j] = (mx, my)
            cnt[g] += 1
        lit = self.Tr[np.isfinite(self.Tr)]
        self.Tend = float(lit.max()) if len(lit) else t0
        lift = pl.get("lift", True)
        # optional timing keys (the defaults are the original numbers, so songs without them render as before):
        # lift_spread (how long the lifts are staggered over), rise_delay (pause between a lift and its rise),
        # rise_spread (stagger of the rises) and rise_dur (shortest flight time to the arch)
        l_spread = float(pl.get("lift_spread", 0.9))
        self.Tlift = (self.Tend + 0.4 if lift is True else float(lift)) + l_spread * rng.random(N) if lift else \
            np.full(N, np.inf)
        rise = pl.get("rise", True)
        r_delay, r_spread = float(pl.get("rise_delay", 1.0)), float(pl.get("rise_spread", 1.4))
        self.Trise = self.Tlift + r_delay + r_spread * rng.random(N) if (rise and lift) else np.full(N, np.inf)
        self.rise_dur = float(pl.get("rise_dur", 3.0)) + 0.6 * rng.random(N)
        self.star_of = np.array([int(np.argmin([abs(x - p[0]) for p in self.star_pos])) for x in self.tx])
        self.arch_gain = float(pl.get("arch", 1.0))
        self.arch_t = float(np.nanmin(np.where(np.isfinite(self.Trise), self.Trise + self.rise_dur, np.inf))) \
            if np.isfinite(self.Trise).any() else self.Tend + 1.0

    # ------------------------------------------------------------ motion along the path
    def motion(self, t):
        tau = t - self.Te
        v, Tc, Td, L, D = self.v, self.Tc, self.Td, self.L, self.D
        u = np.clip(tau - Tc, 0.0, Td)
        d = np.where(tau < Tc, v * np.maximum(tau, 0.0), (L - D) + v * u - 0.5 * (v / Td) * u * u)
        d = np.minimum(d, L)
        vel = np.where(tau < 0, 0.0, np.where(tau < Tc, v, v * np.clip(1 - (tau - Tc) / Td, 0.0, 1.0)))
        x = self.sx + self.fw * d * self.h / self.aspect
        return x, d, vel

    def _weights(self, t):
        """Reach, turn, hold and lift weights per person at t."""
        N = self.N
        w_recv = np.zeros(N)
        w_give = np.zeros(N)
        gx, gy = np.zeros(N), np.zeros(N)
        w_hold = np.zeros(N)
        w_lift = np.zeros(N)
        lit = np.zeros(N)
        if not self.has_pass:
            return w_recv, w_give, gx, gy, w_hold, w_lift, lit
        Tr, Trs = self.Tr, self.Trs
        w_recv = ss(0.0, 0.45, t - Trs) * (1 - ss(0.05, 0.6, t - Tr))
        Tg, Ta = self.gT[..., 0], self.gT[..., 1]
        wg = ss(0.0, 0.45, t - (Tg - self.lead)) * (1 - ss(0.05, 0.55, t - Ta))
        wg = np.where(np.isfinite(Tg), wg, 0.0)
        j = np.argmax(wg, axis=1)
        w_give = wg[np.arange(N), j]
        gx, gy = self.gM[np.arange(N), j, 0], self.gM[np.arange(N), j, 1]
        w_hold = ss(-0.1, 0.7, t - Tr)
        w_lift = ss(0.0, 1.4, t - self.Tlift)
        lit = ss(0.0, 1.2, t - Tr)
        return w_recv, w_give, gx, gy, w_hold, w_lift, lit

    # ------------------------------------------------------------ the posed skeletons of everyone at t
    def skeleton(self, t):
        N, P, asp = self.N, A, self.aspect
        x, d, vel = self.motion(t)
        w = ss(0.05, 0.30, vel)
        ph = self.ph
        br = np.sin(TAU * t / 4.3 + ph * 19.0)
        sway = np.sin(TAU * t / 6.1 + ph * 31.0)
        w_recv, w_give, gx, gy, w_hold, w_lift, lit = self._weights(t)
        # turning: walk nearly side on, then turn toward the centre; turn round to reach someone behind
        settle = ss(-0.4, 1.0, t - self.Ta)
        ys = YAW_WALK + (self.ys - YAW_WALK) * settle
        face = self.fw * np.sign(np.cos(self.ys))           # facing once settled (screen)
        behind_r = np.sign(self.rmx - self.tx) * face < 0
        behind_g = np.sign(gx - self.tx) * face < 0
        w_turn = np.maximum(w_recv * behind_r, w_give * behind_g)
        yaw = ys + ((math.pi - self.ys) - ys) * w_turn * settle
        cy, sy = np.cos(yaw), np.sin(yaw)
        # feet (the rig's walk cycle, for everyone at once)
        dl = d / max(math.cos(YAW_WALK), 0.35)
        stride = P["stride"]
        feet = {}
        for side, off in ((1.0, 0.0), (-1.0, 0.5)):
            ua = dl / stride + ph + off
            kk = np.floor(ua)
            u = ua - kk
            st = u < BETA
            s = np.clip((u - BETA) / (1 - BETA), 0, 1)
            se = s * s * (3 - 2 * s)
            fx = stride * (kk - off - ph + BETA / 2 + np.where(st, 0.0, se)) - dl
            fy = np.where(st, P["ankle"] + 0.022 * ss(0.8 * BETA, BETA, u),
                          P["ankle"] + 0.022 * (1 - se) + 0.075 * np.sin(math.pi * s) ** 1.2)
            pitch = np.where(st, 0.35 * ss(0.8 * BETA, BETA, u), 0.35 * (1 - s) - 0.25 * np.sin(math.pi * s))
            stx = 0.03 * side + 0.004 * sway
            feet[side] = (stx + (fx - stx) * w, P["ankle"] + (fy - P["ankle"]) * w, pitch * w)
        hip_x = 0.006 * sway * (1 - w)
        hip_y = P["hip"] - 0.010 * w + 0.002 * br
        for side in (1.0, -1.0):
            ax, ay, _ = feet[side]
            dx = ax - hip_x
            hip_y = np.minimum(hip_y, ay + np.sqrt(np.maximum((LIMB * 0.997) ** 2 - dx * dx, 0.01)))
        lean = 0.04 * w + 0.05 * w_recv + 0.06 * w_give - 0.04 * w_lift + 0.02 * w_hold
        tilt = 0.03 * np.sin(TAU * t / 5.3 + ph * 7) - 0.10 * w_hold * (1 - w_lift) + 0.25 * w_lift
        Z = np.zeros(N)
        hip = np.stack([hip_x, hip_y, Z], 1)
        up = np.stack([np.sin(lean), np.cos(lean), Z], 1)
        chest = hip + up * (P["chest"] - P["hip"]) + np.stack([Z, 0.004 * br, Z], 1)
        neck = hip + up * (P["neck"] - P["hip"]) + np.stack([Z, 0.005 * br, Z], 1)
        hd = np.stack([np.sin(lean - tilt * 0.6), np.cos(lean - tilt * 0.6), Z], 1)
        head = neck + hd * (P["head"] - P["neck"])
        legs = {}
        for side in (1.0, -1.0):
            ax, ay, pitch = feet[side]
            H2 = np.stack([hip_x, hip_y], 1)
            K2 = _ik(H2, np.stack([ax, ay], 1), P["thigh"], P["shin"])
            zz = np.full(N, side * P["hip_z"])
            Hj = np.stack([hip_x, hip_y, zz], 1)
            Kj = np.stack([K2[:, 0], K2[:, 1], zz * 0.95], 1)
            Aj = np.stack([ax, ay, zz * 0.9], 1)
            toe = Aj + np.stack([0.075 * np.cos(pitch), -0.028 - 0.03 * np.sin(pitch), Z], 1)
            legs[side] = (Hj, Kj, Aj, toe)
        # arms: hang and swing, hold the flame, reach to give or receive, lift the light
        sh_y = hip_y + (P["shoulder_y"] - P["hip"]) * np.cos(lean)
        sh_x = hip_x + (P["shoulder_y"] - P["hip"]) * np.sin(lean)
        acy = np.maximum(np.abs(cy), 0.45)

        def reach_angles(mx, my):
            dxl = np.abs(mx - self.tx) * asp / self.h / acy
            dyl = (my - self.fy) / self.h - P["shoulder_y"]
            el = np.clip(np.arctan2(np.maximum(dxl, 0.05), -dyl), 0.35, 2.7)
            return el

        el_r = reach_angles(self.rmx, self.rmy)
        el_g = reach_angles(gx, gy)
        arms = {}
        for side in (1.0, -1.0):
            a = np.tile(HANG, (N, 1))
            a = a + (HOLD - a) * w_hold[:, None]
            a = a + (LIFT - a) * w_lift[:, None]
            rec = np.stack([el_r - 0.15, np.full(N, 0.30), el_r + 0.05, np.full(N, -0.35)], 1)
            a = a + (rec - a) * w_recv[:, None]
            if side > 0:
                giv = np.stack([el_g - 0.12, np.full(N, 0.15), el_g + 0.08, np.full(N, 0.05)], 1)
                a = a + (giv - a) * w_give[:, None]
            fxr = legs[side][2][:, 0] - hip_x
            a[:, 0] += -1.25 * fxr * w + 0.03 * np.sin(TAU * t / 3.7 + side + ph * 11)
            a[:, 2] += -1.55 * fxr * w + 0.10 * w + 0.05 * np.sin(TAU * t / 3.1 + side * 2 + ph * 13)
            S0 = np.stack([sh_x, sh_y + 0.004 * br, np.full(N, side * P["shoulder_z"])], 1)
            d1 = _armdir(a[:, 0], a[:, 1], side)
            E = S0 + d1 * P["upper"]
            d2 = _armdir(a[:, 2], a[:, 3], side)
            Hn = E + d2 * P["fore"]
            arms[side] = (S0, E, Hn, d2)
        lag = np.clip(-0.09 * vel, -0.08, 0.08)
        return dict(x=x, vel=vel, w=w, yaw=yaw, cy=cy, sy=sy, hip=hip, chest=chest, neck=neck, head=head,
                    legs=legs, arms=arms, lag=lag, br=br, lit=lit, w_hold=w_hold, w_lift=w_lift)

    def to_screen(self, J, lx, ly):
        return (J["x"][:, None] + (self.fw[:, None] * lx) * self.h[:, None] / self.aspect,
                self.fy[:, None] + ly * self.h[:, None])

    def project(self, J, p):
        """Local 3D (N,k,3) -> screen x, y (N,k)."""
        X = p[..., 0] * J["cy"][:, None] + p[..., 2] * J["sy"][:, None]
        return self.to_screen(J, X, p[..., 1])

    def hands_screen(self, J):
        """Where each person holds the flame (screen), from the posed hands."""
        pts = []
        for side in (1.0, -1.0):
            S0, E, Hn, d2 = J["arms"][side]
            pts.append(Hn + d2 * 0.03)
        c = 0.5 * (pts[0] + pts[1])[:, None, :]
        c = c + np.array([0.0, 0.035, 0.0])
        x, y = self.project(J, c)
        hx, hy = self.project(J, pts[0][:, None, :])
        return x[:, 0], y[:, 0], hx[:, 0], hy[:, 0]

    # ------------------------------------------------------------ the sparks of everyone
    def sparks(self, t, J):
        T, N = self.tpl, self.N
        P = A
        out, bri = [], []
        off = self.off
        hip, chest, neck, head = J["hip"], J["chest"], J["neck"], J["head"]
        legs, arms, lag = J["legs"], J["arms"], J["lag"][:, None]
        # robe: an A-line skirt whose cross-section follows both legs
        g = T.robe
        v = (g["v"][None, :] - 0.035 * t + off[:, :1]) % 1.0
        th = g["th"][None, :] + off[:, 1:2] * TAU
        y_top = (hip[:, 1] + (P["waist"] - P["hip"]))[:, None]
        hem_wave = 0.010 * np.sin(3 * th + 2.1 * t) + 0.006 * np.sin(5 * th - 1.6 * t + 1.0)
        y = y_top + (P["hem"] + hem_wave - y_top) * v
        xs = []
        for side in (1.0, -1.0):
            H, K, Af, _ = legs[side]
            f = np.clip((H[:, 1:2] - y) / np.maximum(H[:, 1:2] - Af[:, 1:2], 1e-3), 0, 1)
            l1 = np.clip(f * 2, 0, 1)
            l2 = np.clip(f * 2 - 1, 0, 1)
            xs.append(np.where(f < 0.5, H[:, :1] + (K[:, :1] - H[:, :1]) * l1, K[:, :1] + (Af[:, :1] - K[:, :1]) * l2))
        cx = 0.5 * (xs[0] + xs[1]) + lag * v ** 1.6 + 0.010 * v * v * np.sin(TAU * t / 2.7 + self.ph[:, None] * 9)
        half = 0.5 * np.abs(xs[0] - xs[1])
        ax = P["robe_top"][0] + P["robe_flare"][0] * v ** 1.3 + half * 0.62
        az = P["robe_top"][1] + P["robe_flare"][1] * v ** 1.3
        rr = g["r"][None, :] * (1.0 + 0.05 * np.sin(1.3 * t + th * 3 + v * 5))
        out.append(np.stack([cx + ax * rr * np.cos(th), y, az * rr * np.sin(th)], -1))
        bri.append(0.80 + 0.35 * (g["r"][None, :] > 0.82) + 0.25 * v - 0.6 * ss(0.92, 1.0, v)
                   - 0.4 * (1 - ss(0.0, 0.06, v)))
        # torso
        g = T.torso
        s = (g["s"][None, :] + 0.05 * t + off[:, 2:3]) % 1.0
        r0, r1, r2 = P["torso"]
        s1 = s < 0.68
        u1 = (s / 0.68)[..., None]
        u2 = np.clip((s - 0.68) / 0.32, 0, 1)[..., None]
        c = np.where(s1[..., None], hip[:, None] + (chest - hip)[:, None] * u1, chest[:, None] + (neck - chest)[:, None] * u2)
        u1, u2 = u1[..., 0], u2[..., 0]
        rx = np.where(s1, r0[0] + (r1[0] - r0[0]) * u1, r1[0] + (r2[0] - r1[0]) * u2 ** 0.7)
        rz = np.where(s1, r0[1] + (r1[1] - r0[1]) * u1, r1[1] + (r2[1] - r1[1]) * u2 ** 0.7)
        tht = g["th"][None, :]
        out.append(c + np.stack([rx * g["r"] * np.cos(tht), np.zeros_like(s), rz * g["r"] * np.sin(tht)], -1))
        bri.append(np.broadcast_to(0.85 + 0.3 * (g["r"] > 0.82), s.shape))
        # head: a soft ball of light (no face)
        g = T.head
        hr = P["head_r"] * (1 + 0.03 * np.sin(t * 1.7 + self.ph * 9))
        out.append(head[:, None] + g["d"][None] * (hr[:, None] * g["r"][None])[..., None] * np.array([0.92, 1.08, 0.92]))
        bri.append(np.broadcast_to(1.15 - 0.35 * g["r"], (N, len(g["r"]))))
        # arms in wide sleeves
        g = T.arm
        pts = np.zeros((N, len(g["s"]), 3))
        for side in (1.0, -1.0):
            S0, E, Hn, d2 = arms[side]
            for seg in (0, 1):
                m = (g["side"] == side) & (g["seg"] == seg)
                s = g["s"][m][None, :]
                Aa, Bb = (S0, E) if seg == 0 else (E, Hn)
                cc = Aa[:, None] + (Bb - Aa)[:, None] * s[..., None]
                rad = 0.030 + 0.002 * s if seg == 0 else 0.032 + 0.030 * s ** 1.5
                if seg == 1:
                    cc = cc + (lag * 0.25 * s ** 2)[..., None] * np.array([1.0, 0, 0]) - \
                        (0.018 * s ** 2)[..., None] * np.array([0, 1.0, 0])
                pts[:, m] = cc + _disc(Bb - Aa, np.broadcast_to(g["th"][m], (N, m.sum())), np.broadcast_to(g["r"][m] * rad, (N, m.sum())))
        out.append(pts)
        bri.append(np.broadcast_to(0.85 + 0.3 * (g["r"] > 0.8), (N, len(g["s"]))))
        # hands
        g = T.hand
        pts = np.zeros((N, len(g["s"]), 3))
        for side in (1.0, -1.0):
            S0, E, Hn, d2 = arms[side]
            m = g["side"] == side
            cc = Hn[:, None] + d2[:, None] * (0.055 * g["s"][m])[None, :, None]
            pts[:, m] = cc + (g["d"][m] * (0.020 * g["r"][m] * (1 - 0.4 * g["s"][m]))[:, None])[None]
        out.append(pts)
        bri.append(np.full((N, len(g["s"])), 1.6))   # hands read clearly at crowd size
        # legs (faint, under the robe) and feet stepping out under the hem
        g = T.leg
        pts = np.zeros((N, len(g["s"]), 3))
        for side in (1.0, -1.0):
            H, K, Af, toe = legs[side]
            for seg in (0, 1):
                m = (g["side"] == side) & (g["seg"] == seg)
                a0, b0 = (H, K) if seg == 0 else (K, Af)
                cc = a0[:, None] + (b0 - a0)[:, None] * g["s"][m][None, :, None]
                pts[:, m] = cc + _disc(b0 - a0, np.broadcast_to(g["th"][m], (N, m.sum())),
                                       np.broadcast_to(g["r"][m] * (0.036 if seg == 0 else 0.026), (N, m.sum())))
        out.append(pts)
        bri.append(np.full((N, len(g["s"])), 0.75))
        g = T.foot
        pts = np.zeros((N, len(g["s"]), 3))
        for side in (1.0, -1.0):
            H, K, Af, toe = legs[side]
            m = g["side"] == side
            cc = Af[:, None] + (toe - Af)[:, None] * g["s"][m][None, :, None]
            pts[:, m] = cc + (g["d"][m] * (0.017 * g["r"][m])[:, None] * np.array([1.0, 0.7, 1.0]))[None]
        out.append(pts)
        bri.append(np.full((N, len(g["s"])), 1.7))   # so do the stepping feet
        p = np.concatenate(out, axis=1)
        b = np.concatenate(bri, axis=1)
        X, Y = self.project(J, p)
        return X, Y, b, p[..., 1]

    # ------------------------------------------------------------ everything this layer draws at t, as sprites
    def sprites(self, t, px):
        """Arrays of (x, y, size in pixels at 1080p, sharpness, r, g, b)."""
        N, T = self.N, self.tpl
        J = self.skeleton(t)
        X, Y, b, ly = self.sparks(t, J)
        # who is on screen: enter from the edge; at t1 rise and fade
        a_in = ss(0.0, 0.6, t - self.Te) * (t >= self.Te)
        fdis = ss(0.0, self.dis, t - self.leave)
        alive = a_in * (1 - fdis)
        lit = J["lit"]
        dim = 0.55 if self.has_pass else 1.0
        pb = self.bright * alive * (dim + (1.25 - dim) * lit) * float(self.m.get("glow", 1.0))
        col = self.col
        if self.has_pass:
            col = col + (self.fcol - col) * (0.45 * lit)[:, None]
        tw = 0.62 + 0.38 * np.sin(t * (1.8 + 3.2 * T.seed[None, :, 0]) + T.seed[None, :, 1] * 50 + self.ph[:, None] * 40)
        cur = np.exp(-((((ly * 0.9 - 0.20 * t + self.ph[:, None]) % 1.0) - 0.5) / 0.06) ** 2)   # a rising current
        amp = b * tw * (1 + 0.8 * cur) * pb[:, None] * 0.75
        sc = np.sqrt(self.h / 0.13)[:, None]
        size = T.size[None, :] * sc
        if (fdis > 0).any():                       # leaving: the sparks drift up as they fade
            f = fdis[:, None]
            Y = Y + (0.03 + 0.12 * T.seed[None, :, 1]) * f * f * self.h[:, None] * 2
            X = X + (T.seed[None, :, 0] - 0.5) * 0.02 * f
        hot = 0.25 * cur
        cA = np.array([1.0, 0.86, 0.66])
        C = (col[:, None, :] * (1 - hot[..., None]) + cA * hot[..., None]) * amp[..., None]
        keep = amp > 0.004
        parts = [np.column_stack([X[keep], Y[keep], np.broadcast_to(size, keep.shape)[keep], np.full(keep.sum(), 3.2),
                                  C[keep]])]
        # the glassy body: soft glows strung along the bones give each person a clear silhouette
        # (head, chest, waist, robe, sleeves and hands), cheap enough for a crowd
        legs, arms = J["legs"], J["arms"]
        knee = 0.5 * (legs[1.0][1] + legs[-1.0][1])
        ank = 0.5 * (legs[1.0][2] + legs[-1.0][2])
        hip = J["hip"]
        bones = [(J["head"], 0.16, 0.50), (0.5 * (J["neck"] + J["chest"]), 0.15, 0.32),
                 (0.5 * (J["chest"] + hip), 0.17, 0.30), (0.5 * (hip + knee), 0.19, 0.26),
                 (knee, 0.21, 0.24), (0.5 * (knee + ank) + np.array([0.0, 0.03, 0.0]), 0.23, 0.22)]
        for side in (1.0, -1.0):
            S0, E, Hn, d2 = arms[side]
            bones += [(0.5 * (S0 + E), 0.07, 0.16), (0.5 * (E + Hn), 0.08, 0.20), (Hn + d2 * 0.03, 0.06, 0.55),
                      (legs[side][2] + np.array([0.03, -0.01, 0.0]), 0.06, 0.45)]
        bp = np.stack([b[0] for b in bones], 1)
        bx, by = self.project(J, bp)
        bsz = np.array([b[1] for b in bones])[None, :] * (self.h * 1080.0)[:, None] * 1.25
        bw = np.array([b[2] for b in bones])[None, :] * (pb * (0.42 + 0.30 * lit))[:, None]
        on = bw > 0.003
        bc = (col[:, None, :] * 0.8 + 0.2) * bw[..., None]
        parts.append(np.column_stack([bx[on], by[on], bsz[on], np.full(on.sum(), 3.0), bc[on] * 0.55]))
        if self.has_pass:
            parts += self._flames(t, J, alive)
        return np.vstack(parts).astype("f4")

    def _flame(self, x, y, scale, inten, t, phase):
        """A small flame: hot core, warm glow and halo, flickering."""
        fl = 0.85 + 0.15 * np.sin(t * 13.0 + phase * 7) * np.sin(t * 7.3 + phase * 3)
        c = self.fcol
        white = np.array([1.0, 0.97, 0.88])
        rows = []
        for sz, sharp, cc, a in ((5.5, 2.4, white, 1.6), (15.0, 3.0, c, 0.65), (46.0, 2.6, c, 0.16)):
            amp = (inten * fl * a)[:, None]
            rows.append(np.column_stack([x, y + 0.002 * (sz > 6), np.full(len(x), sz) * scale, np.full(len(x), sharp),
                                         cc[None, :] * amp]))
        return rows

    def _flames(self, t, J, alive):
        out = []
        fx, fy, rx, ry = self.hands_screen(J)
        sc = np.sqrt(self.h / 0.13)
        held = (t >= self.Tr) & (alive > 0.01)
        risen = ss(0.0, 0.6, t - self.Trise)
        if held.any():
            i = np.nonzero(held)[0]
            inten = ss(0.0, 0.4, t - self.Tr[i]) * alive[i] * (1 - 0.55 * risen[i]) * (1 - 0.25 * self.r[i])
            out += self._flame(fx[i], fy[i], sc[i], inten, t, self.ph[i] * 10)
        # the flame coming down from the arch
        if self.src is not None and self.src_t[0] <= t < self.src_t[1] + 0.05:
            u = (t - self.src_t[0]) / (self.src_t[1] - self.src_t[0])
            k = int(np.argmin(np.where(np.isfinite(self.Tr), self.Tr, np.inf)))
            out += self._travel(t, self.fix(self.src), (fx[k], fy[k]), u, 0.06, 1.3, sc[k])
        # hops in flight
        for g, c, Tg, Tarr, mx, my in self.hops:
            if Tg <= t < Tarr:
                u = (t - Tg) / (Tarr - Tg)
                out += self._travel(t, (rx[g], ry[g]), (fx[c], fy[c]), u, 0.35, 1.0, sc[c])
        # the lights rise to the arch, which brightens
        fly = (t >= self.Trise) & (t < self.Trise + self.rise_dur)
        for i in np.nonzero(fly)[0]:
            u = (t - self.Trise[i]) / self.rise_dur[i]
            sp = self.fix(self.star_pos[self.star_of[i]])
            out += self._travel(t, (fx[i], fy[i]), sp, u, 0.18 + 0.1 * self.ph[i], 0.75 * (1 - 0.6 * self.r[i]),
                                sc[i] * 0.8, side=0.05 * (self.ph[i] - 0.5))
        A = self.arch_gain * ss(self.arch_t - 1.5, self.arch_t + 3.0, t)
        if A > 0.002:
            sp = np.array([self.fix(q) for q in self.star_pos])
            # along the arch: a band of light through the nine lights
            k = 260
            u = np.linspace(0, 1, k)
            xs = np.interp(u * (len(sp) - 1), np.arange(len(sp)), sp[:, 0])
            ys = np.interp(u * (len(sp) - 1), np.arange(len(sp)), sp[:, 1])
            rng = np.random.default_rng(5)
            jit = rng.normal(size=(k, 2)) * np.array([0.004, 0.006])
            tw = 0.55 + 0.45 * np.sin(t * (1.3 + 2 * rng.random(k)) + rng.random(k) * 40)
            amp = A * tw * 0.55 * (0.6 + 0.4 * ss(0.0, 0.3, (u * (len(sp) - 1) + 0.5) % 1))
            out.append(np.column_stack([xs + jit[:, 0], ys + jit[:, 1], 2.0 + 2.5 * rng.random(k), np.full(k, 3.0),
                                        self.fcol[None, :] * amp[:, None]]))
            out.append(np.column_stack([sp[:, 0], sp[:, 1], np.full(len(sp), 120.0), np.full(len(sp), 2.4),
                                        np.tile(self.fcol * 0.30 * A, (len(sp), 1))]))
        return out

    def _travel(self, t, a, b, u, arc, inten, scale, side=0.0):
        """A flame moving from a to b (screen) along an arc, at progress u, with a spark trail."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = math.hypot((b[0] - a[0]) * self.aspect, b[1] - a[1])

        def at(uu):
            e = uu * uu * (3 - 2 * uu)
            p = a + (b - a) * e
            return p[0] + side * math.sin(math.pi * uu), p[1] + arc * d * math.sin(math.pi * uu)

        x, y = at(u)
        rows = self._flame(np.array([x]), np.array([y]), np.array([scale * 1.15]), np.array([inten]), t, 0.3)
        n = 14
        us = np.clip(u - np.arange(1, n + 1) * 0.022, 0.0, 1.0)
        tr = np.array([at(uu) for uu in us])
        fade = (1 - np.arange(n) / n) ** 1.5 * inten * (us > 0)
        rows.append(np.column_stack([tr[:, 0], tr[:, 1], np.full(n, 6.0) * scale, np.full(n, 3.0),
                                     self.fcol[None, :] * (fade * 0.55)[:, None]]))
        rng = np.random.default_rng(int(t * 60) % 100000)
        m = 10
        uu = np.clip(u - rng.random(m) * 0.25, 0, 1)
        sp = np.array([at(q) for q in uu]) + rng.normal(size=(m, 2)) * np.array([0.004, 0.006])
        rows.append(np.column_stack([sp[:, 0], sp[:, 1], 2.0 + 2.0 * rng.random(m), np.full(m, 3.0),
                                     np.tile(np.array([1.0, 0.92, 0.75]) * 0.9 * inten, (m, 1))]))
        return rows


# ---------------------------------------------------------------- the layer, drawn by render.py
class Gathering:
    def __init__(self, R):
        g = getattr(S, "GATHERING", None)
        pl = getattr(S, "PASS_LIGHT", None)
        self.on = g is not None
        if not self.on:
            if pl is not None:
                raise ValueError("PASS_LIGHT needs a GATHERING (the crowd that passes the light)")
            return
        self.R = R
        self.crowd = Crowd(dict(g), dict(pl) if pl is not None else None, S.ASPECT, getattr(S, "STAR_POS", None))
        ctx = R.ctx
        import sky_camera as SKC
        self.prog = ctx.program(vertex_shader=SKC.cam_vs(VS), fragment_shader=FS)   # the crowd follows the camera
        self.cap = 0
        self.buf = None
        self.vao = None

    def draw(self, t):
        if not self.on:
            return
        c = self.crowd
        if t < float(np.min(c.Te)) or t > float(np.max(c.leave)) + c.dis + 0.1:
            return
        # CAMERA: the whole crowd stands at one depth, the ground under its feet line (`depth=` overrides it)
        sky = getattr(self.R, "sky", None)
        aff = (0.0, 0.0, 0.0)
        if sky is not None:
            w = float(c.m["depth"]) if c.m.get("depth") is not None else sky.ground_depth(c.cy)
            aff = sky.aff(w)
            c.fix = lambda q, w=w: sky.unplace(q, w)
        if c.silk:   # look="silk": the people are bodies of light (engine/figure_look.py); only flames are sprites
            data = self.R.fl.draw_crowd(c, t, aff)
        else:
            data = c.sprites(t, self.R.px)
        n = len(data)
        if n == 0:
            return
        if n > self.cap:
            self.cap = int(n * 1.3) + 64
            self.buf = self.R.ctx.buffer(reserve=self.cap * 7 * 4, dynamic=True)
            self.vao = self.R.ctx.vertex_array(self.prog, [(self.buf, "2f 2f 3f", "aPos", "aSz", "aCol")])
        self.buf.orphan(self.cap * 7 * 4)
        self.buf.write(data.tobytes())
        self.prog["uPx"].value = float(self.R.px)
        if "uCamAff" in self.prog:
            self.prog["uCamAff"].value = aff
        self.vao.render(moderngl.POINTS, vertices=n)
