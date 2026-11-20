"""Hearts for the 3D layer (engine/p3d): heart sprites, hearts that drift off an expression in its colour, and
points of light arranged into a heart. Pure numpy; how a song uses it: engine/UPGRADE-HOWTO.md, section Z.

THE HEART SPRITE
  Every batch may use kind="heart" (engine/p3d/api.py): in focus a crisp heart that turns in the picture
  (rot[:, 0], radians) and tumbles (rot[:, 1]); out of focus its bokeh disc is itself a heart. Size is the
  diameter of the circle round the heart, in metres.

  Hearts(...)        a field of hearts that hang and drift: style "bokeh" (soft hearts out of focus), "sparkle"
                     (small bright hearts with a glint), "petal" (heart petals that tumble on the wind)
  HeartDrift(...)    small hearts released from a place (a point, a moving point, a hand) in a colour, rising and
                     swaying away, at a rate, between two times: "hearts drift off each expression"
  HeartForm(...)     lights that gather from where they are into a heart, hold, and let go
  heart_points(n)    points on a heart's outline or inside it (heart units: 1.0 high, centred)
  arrange_heart(points, ...)   for any K points, K places on a heart in the world, matched so paths do not cross
  heart_places(n, ...)         places for n people (or lanterns) standing in a heart on the ground
"""
import math

import numpy as np

from . import brand as B
from .api import hash01, lin

TAU = 2.0 * math.pi


def _col(c):
    if isinstance(c, str):
        if c in B.EXPRESSION_COLORS:
            return lin(B.EXPRESSION_COLORS[c])
        return lin(c)
    return np.asarray(c, np.float64)


def _colors(colors, n, seed=0):
    """n colours (linear) from one colour, an expression name, a list of them, or "nine" (the nine expressions)."""
    if colors is None or colors == "nine":
        colors = B.NINE
    if isinstance(colors, (str, tuple)) or (isinstance(colors, np.ndarray) and colors.ndim == 1):
        return np.broadcast_to(_col(colors), (n, 3)).astype(np.float32)
    pal = np.array([_col(c) for c in colors], np.float32)
    k = (hash01(n, seed) * len(pal)).astype(np.int64) % len(pal)
    return pal[k]


def _paint_of(col):
    """Paint colours (the light the picture shows as exactly that colour) for linear colours (N, 3)."""
    return B.show_rgb(np.clip(np.asarray(col, np.float64), 0.0, 1.0) ** (1.0 / 2.2)).astype(np.float32)


def _deepen(c, k=1.3):
    """The same hue, more saturated (light that keeps its colour when it glows)."""
    c = np.asarray(c, np.float64)
    m = np.maximum(c.max(axis=-1, keepdims=True), 1e-6)
    return m * (c / m) ** k


# --------------------------------------------------------------------------------------------- shapes
def heart_points(n=200, fill=False, seed=3):
    """n points of a heart, 1.0 high, centred on its box, y up: on its outline at even steps (fill=False), or
    spread evenly inside it (fill=True). Returns (n, 2)."""
    if not fill:
        p = B.heart_shape(2048)
        seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])
        u = (np.arange(n) + 0.5) / n * s[-1]
        return np.stack([np.interp(u, s, p[:, 0]), np.interp(u, s, p[:, 1])], axis=1)
    rng = np.random.default_rng(seed)
    poly = B.heart_shape(400)
    w = float(np.ptp(poly[:, 0]))                  # a heart is 1.0 high and about 1.09 wide
    m = int(n * 1.6) + 16
    while True:
        # a jittered grid over the heart's box, kept inside the heart
        g = int(math.ceil(math.sqrt(m)))
        xs, ys = np.meshgrid((np.arange(g) + 0.5) / g, (np.arange(g) + 0.5) / g)
        c = np.stack([xs.ravel(), ys.ravel()], axis=1)
        c = c + (rng.random(c.shape) - 0.5) / g * 0.7
        c = (c - 0.5) * np.array([w, 1.0])
        c = c[_inside(c, poly)]
        if len(c) >= n:
            break
        m = int(m * 1.5)
    idx = np.linspace(0, len(c) - 1, n).astype(np.int64)
    return c[idx]


def _inside(p, poly):
    """Points (N, 2) inside a closed polygon (even odd rule)."""
    x, y = p[:, 0][:, None], p[:, 1][:, None]
    x0, y0 = poly[:-1, 0][None, :], poly[:-1, 1][None, :]
    x1, y1 = poly[1:, 0][None, :], poly[1:, 1][None, :]
    cross = ((y0 > y) != (y1 > y)) & (x < (x1 - x0) * (y - y0) / np.where(y1 - y0 == 0, 1e-12, y1 - y0) + x0)
    return cross.sum(axis=1) % 2 == 1


def _frame(center, facing=0.0, tilt=0.0, face="fixed", cam=None):
    c = np.asarray(center, np.float64)
    if face == "camera" and cam is not None:
        d = np.asarray(cam.pos, np.float64) - c
        facing = math.degrees(math.atan2(d[0], d[2]))
    if face == "screen" and cam is not None:
        r, u, f = cam.basis()
        return c, r, u, -f
    a = math.radians(facing)
    nrm = np.array([math.sin(a), 0.0, math.cos(a)])
    right = np.array([math.cos(a), 0.0, -math.sin(a)])
    up = np.array([0.0, 1.0, 0.0])
    if face == "flat":
        up, nrm = -nrm, np.array([0.0, 1.0, 0.0])
    tl = math.radians(tilt)
    if tl:
        up, nrm = up * math.cos(tl) - nrm * math.sin(tl), nrm * math.cos(tl) + up * math.sin(tl)
    return c, right, up, nrm


def arrange_heart(points, center, size, facing=0.0, tilt=0.0, face="fixed", fill=False, cam=None):
    """K places on a heart for K given points (K, 3), matched so that each point goes to the place in the same
    direction from the middle (paths barely cross). The heart is `size` metres high, centred at `center`,
    facing azimuth `facing` (or face="flat" lying on the ground, read from above). Returns (K, 3)."""
    p = np.asarray(points, np.float64).reshape(-1, 3)
    k = len(p)
    hp = heart_points(k, fill=fill)
    c, r, u, n = _frame(center, facing, tilt, face, cam)
    tgt = c[None, :] + size * (hp[:, 0:1] * r[None, :] + hp[:, 1:2] * u[None, :])
    # match by angle round the middles (and, filled, by distance from the middle)
    pc = p - p.mean(axis=0)
    a_src = np.arctan2(pc @ u, pc @ r)
    a_tgt = np.arctan2(hp[:, 1], hp[:, 0])
    if fill:
        rs = np.hypot(pc @ u, pc @ r)
        rt = np.hypot(hp[:, 0], hp[:, 1])
        os_ = np.lexsort((a_src, np.minimum((rs / max(rs.max(), 1e-9) * 4).astype(int), 3)))
        ot = np.lexsort((a_tgt, np.minimum((rt / max(rt.max(), 1e-9) * 4).astype(int), 3)))
    else:
        os_, ot = np.argsort(a_src), np.argsort(a_tgt)
    out = np.empty_like(tgt)
    out[os_] = tgt[ot]
    return out


def heart_places(n, center=(0.0, 0.0), size=12.0, facing=0.0, fill=False):
    """Places (n, 3) on the ground (y = 0) for n people or lanterns standing in a heart, seen whole from above
    or from the side it faces; `size` metres from tip to top, the tip toward `facing` (degrees)."""
    hp = heart_points(n, fill=fill)
    a = math.radians(facing)
    fwd = np.array([math.sin(a), 0.0, math.cos(a)])
    side = np.array([math.cos(a), 0.0, -math.sin(a)])
    c = np.array([center[0], 0.0, center[1]])
    return c[None, :] + size * (hp[:, 0:1] * side[None, :] - hp[:, 1:2] * fwd[None, :])


# ------------------------------------------------------------------------------------------- fields
def _fade(t, t0, t1, fin=0.8, fout=0.8):
    a = np.clip((t - t0) / max(fin, 1e-6), 0.0, 1.0) if t0 is not None else 1.0
    b = np.clip((t1 - t) / max(fout, 1e-6), 0.0, 1.0) if t1 is not None else 1.0
    return float(a * b)


class Hearts:
    """A field of hearts that hang in the air and drift.

    style    "bokeh": soft hearts, out of focus (give them a place nearer or farther than the focus; dof on)
             "sparkle": small bright hearts with a glint in the middle that twinkle
             "petal": heart petals that turn and tumble, drifting on the wind (painted on a bright sky)
    n        how many
    center, box   the middle of the field and its size (x, y, z metres); hearts wrap round inside it as they drift
    size     (smallest, largest) diameter in metres
    colors   one colour, an expression name ("Greeting"), a list, or "nine" (the website colours)
    drift    (x, y, z) metres per second; sway: metres of side to side swaying
    bright   strength of the light; paint 0..1 (petals on a bright sky: 1, their exact colours)
    t0, t1, fade    when the field is there and how many seconds it takes to come and go
    The set's gain fades it, so a field outside its times costs nothing.
    """

    def __init__(self, style="bokeh", n=60, center=(0.0, 4.0, 0.0), box=(20.0, 8.0, 10.0), size=None, colors="nine",
                 drift=(0.15, 0.25, 0.0), sway=0.4, bright=1.0, paint=0.0, t0=None, t1=None, fade=1.0, seed=11,
                 dof=1.0):
        self.style = style
        self.n = int(n)
        self.center, self.box = np.asarray(center, np.float64), np.asarray(box, np.float64)
        if size is None:
            size = dict(bokeh=(0.35, 0.8), sparkle=(0.06, 0.14), petal=(0.10, 0.22))[style]
        self.size = size
        self.drift, self.sway = np.asarray(drift, np.float64), float(sway)
        self.bright, self.paint = float(bright), paint
        self.t0, self.t1, self.fade = t0, t1, float(fade)
        self.dof = dof
        rng = np.random.default_rng(seed)
        self.s = rng.random((self.n, 6))
        self.col = _colors(colors, self.n, seed)
        self.paintc = _paint_of(self.col)

    def gain(self, t):
        return _fade(t, self.t0, self.t1, self.fade, self.fade)

    def sample(self, t):
        if self.gain(t) <= 0.0:
            return None
        s = self.s
        p = (s[:, :3] - 0.5) * self.box[None, :]
        p = p + self.drift[None, :] * t
        p = np.mod(p + 0.5 * self.box[None, :], self.box[None, :]) - 0.5 * self.box[None, :]
        ph = s[:, 3] * TAU
        p[:, 0] += self.sway * np.sin(t * (0.4 + 0.5 * s[:, 4]) + ph)
        p[:, 1] += 0.4 * self.sway * np.sin(t * (0.6 + 0.4 * s[:, 5]) + 2.0 * ph)
        pos = (p + self.center[None, :]).astype(np.float32)
        lo, hi = self.size
        size = (lo + (hi - lo) * s[:, 4]).astype(np.float32)
        # hearts near the edges of the box fade, so the wrap is never seen
        edge = np.min(0.5 - np.abs(p / self.box[None, :]), axis=1)
        a_edge = np.clip(edge / 0.08, 0.0, 1.0)
        tilt = 0.35 * np.sin(t * (0.5 + s[:, 5]) + ph)
        paint = float(np.clip(self.paint(t) if callable(self.paint) else self.paint, 0.0, 1.0))
        if self.style == "bokeh":
            return dict(pos=pos, size=size, color=_deepen(self.col) * 0.9 * self.bright, alpha=0.55 * a_edge,
                        kind="heart", rot=np.stack([tilt, np.zeros(self.n)], axis=1), seed=s[:, 0], twinkle=0.15,
                        dof=self.dof, lod=False)
        if self.style == "sparkle":
            tw = 0.55 + 0.45 * np.sin(t * (2.0 + 3.0 * s[:, 5]) + ph * 3.0) ** 2
            out = [dict(pos=pos, size=size, color=_deepen(self.col) * 1.6 * self.bright, alpha=a_edge * tw,
                        kind="heart", rot=np.stack([tilt, np.zeros(self.n)], axis=1), seed=s[:, 0], dof=self.dof)]
            out.append(dict(pos=pos, size=size * 0.9, color=np.array([1.0, 0.95, 0.88]) * self.bright,
                            alpha=a_edge * tw * 0.7, emit=2.0, kind="spark", twinkle=1.0, seed=s[:, 1], dof=self.dof))
            return out
        # petals: tumble and turn on the wind
        rot = np.stack([s[:, 0] * TAU + t * (0.6 + s[:, 3]), s[:, 1] * TAU + t * (1.2 + 1.8 * s[:, 4])], axis=1)
        return dict(pos=pos, size=size, color=(self.paintc if paint > 0 else _deepen(self.col) * 1.1 * self.bright),
                    alpha=0.9 * a_edge, kind="heart", rot=rot, seed=s[:, 2], paint=paint, paint_light=0.35,
                    dof=self.dof)


class HeartDrift:
    """Small hearts released from a place in a colour, rising and swaying away: hearts drifting off an expression.

    source   a point (x, y, z), a function of t giving one, or a point set with `where(t)` or `targets(t)`
             (a particle word: they rise from its letters)
    t0, t1   when hearts are released; rate: hearts a second
    color    an expression name ("Gratitude"), a hex colour, a list, or "nine"
    life     seconds each heart lives; rise: metres a second upward; spread: metres of sideways scatter
    size     (smallest, largest) diameter in metres; bright; paint 0..1 for a bright sky
    style    "heart" (crisp, glowing), "sparkle" (with a glint), "bokeh" (soft, out of focus)
    wind     (x, y, z) metres a second added to every heart
    """

    def __init__(self, source, t0, t1, color="Greeting", rate=12.0, life=2.8, rise=0.9, spread=0.6,
                 size=(0.10, 0.22), bright=1.0, paint=0.0, style="heart", wind=(0.0, 0.0, 0.0), seed=5, dof=1.0):
        self.source, self.t0, self.t1 = source, float(t0), float(t1)
        self.rate, self.life, self.rise, self.spread = float(rate), float(life), float(rise), float(spread)
        self.size, self.bright, self.paint, self.style = size, float(bright), paint, style
        self.wind = np.asarray(wind, np.float64)
        self.dof = dof
        self.k = max(int(math.ceil((self.t1 - self.t0) * self.rate)), 1)
        rng = np.random.default_rng(seed)
        self.s = rng.random((self.k, 7))
        self.birth = self.t0 + (np.arange(self.k) + 0.6 * self.s[:, 0]) / self.rate
        self.col = _colors(color, self.k, seed)
        self.paintc = _paint_of(self.col)
        self._memo = {}

    def gain(self, t):
        return 1.0 if self.t0 - 0.1 <= t <= self.t1 + self.life + 0.1 else 0.0

    def _born(self, i):
        """Where heart i was born (the source at its birth; a moving source leaves a trail). Kept: a pure
        function of i, worked out once."""
        if i in self._memo:
            return self._memo[i]
        s, bt = self.source, float(self.birth[i])
        if callable(s):
            p = np.asarray(s(bt), np.float64)
        elif hasattr(s, "targets") or hasattr(s, "where"):
            pts = np.asarray(s.targets(bt) if hasattr(s, "targets") else s.where(bt), np.float64).reshape(-1, 3)
            p = pts[int(self.s[i, 6] * len(pts)) % max(len(pts), 1)] if len(pts) else np.zeros(3)
        else:
            p = np.asarray(s, np.float64)
        self._memo[i] = p
        return p

    def sample(self, t):
        if self.gain(t) <= 0.0:
            return None
        age = t - self.birth
        live = np.nonzero((age >= 0.0) & (age <= self.life))[0]
        if len(live) == 0:
            return None
        a = age[live]
        s = self.s[live]
        born = np.array([self._born(int(i)) for i in live])
        ang = s[:, 1] * TAU
        side = np.stack([np.cos(ang), np.zeros(len(a)), np.sin(ang)], axis=1)
        out_r = self.spread * (1.0 - np.exp(-a * 1.4)) * (0.4 + 0.6 * s[:, 2])
        sway = 0.12 * np.sin(a * (2.0 + 1.5 * s[:, 3]) + s[:, 4] * TAU)
        pos = born + side * out_r[:, None] + np.stack([sway, self.rise * a * (0.7 + 0.6 * s[:, 5]), sway * 0.5],
                                                      axis=1) + self.wind[None, :] * a[:, None]
        lo, hi = self.size
        size = (lo + (hi - lo) * s[:, 2]) * (0.6 + 0.4 * np.clip(a / 0.4, 0.0, 1.0))
        al = np.clip(a / 0.25, 0.0, 1.0) * np.clip((self.life - a) / (0.45 * self.life), 0.0, 1.0)
        rot = np.stack([0.4 * np.sin(a * 1.7 + s[:, 4] * 6.0), 0.5 * np.sin(a * 2.3 + s[:, 3] * 6.0)], axis=1)
        col = self.col[live]
        paint = float(np.clip(self.paint(t) if callable(self.paint) else self.paint, 0.0, 1.0))
        res = [dict(pos=pos.astype(np.float32), size=size.astype(np.float32),
                    color=(self.paintc[live] if paint > 0 else _deepen(col) * 1.4 * self.bright),
                    alpha=al.astype(np.float32), kind="heart", rot=rot, seed=s[:, 0], paint=paint, paint_light=0.4,
                    dof=self.dof, streak=0.3)]
        if self.style in ("sparkle", "heart"):
            res.append(dict(pos=pos.astype(np.float32), size=(size * 3.5).astype(np.float32),
                            color=_deepen(col) * self.bright, alpha=(al * 0.05).astype(np.float32), kind="soft",
                            seed=s[:, 1], dof=1.0, streak=0.0))
        if self.style == "sparkle":
            res.append(dict(pos=pos.astype(np.float32), size=(size * 0.8).astype(np.float32),
                            color=np.array([1.0, 0.95, 0.88]) * self.bright, alpha=(al * 0.6).astype(np.float32),
                            emit=2.0, kind="spark", twinkle=1.0, seed=s[:, 2], dof=self.dof))
        if self.style == "bokeh":
            res[0]["dof"] = 1.0
        return res


class HeartForm:
    """Lights that gather into a heart, hold, and let go: fireflies, lanterns, the lights of a crowd.

    center, size, facing, tilt, face   the heart (size: metres high; face "camera", "screen" or "flat" as Place)
    start    where the lights are before: (K, 3) points, a function of t giving (K, 3) (a crowd's lights that move),
             or None: a loose cloud round the heart (n lights, `scatter` metres)
    t0, t1   they gather between these times (each on its own clock along a curved path)
    hold     seconds they stay as a heart (None: until the end); release: seconds to fly back or drift off
    then     "back" (to where they came from), "up" (they rise and fade), "burst" (outward)
    fill     False: the outline of the heart; True: spread inside it
    color    one colour, an expression name, a list or "nine"; kind "spark" (default), "soft" or "heart"
    size     sprite diameter in metres; bright
    camera   the song's Rig, for face="camera" or "screen"
    """

    def __init__(self, center, size=4.0, facing=0.0, tilt=0.0, face="fixed", start=None, n=160, scatter=6.0,
                 t0=0.0, t1=2.0, hold=2.0, release=1.6, then="up", fill=False, color="#ffd27a", kind="spark",
                 point=0.08, bright=1.0, camera=None, seed=9, dof=1.0):
        self.center, self.size, self.facing, self.tilt, self.face = center, float(size), facing, tilt, face
        self.start, self.scatter = start, float(scatter)
        self.t0, self.t1 = float(t0), float(t1)
        self.hold, self.release, self.then = hold, float(release), then
        self.fill, self.kind, self.point, self.bright = fill, kind, float(point), float(bright)
        self.camera = camera
        self.wants_camera = face in ("camera", "screen")
        self.dof = dof
        k = len(np.asarray(start).reshape(-1, 3)) if (start is not None and not callable(start)) else int(n)
        if callable(start):
            k = len(np.asarray(start(self.t0)).reshape(-1, 3))
        self.k = k
        rng = np.random.default_rng(seed)
        self.s = rng.random((k, 6))
        d = rng.normal(size=(k, 3))
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
        self.cloud = d * (self.scatter * (0.4 + 0.6 * self.s[:, 0:1] ** 0.5))
        self.col = _colors(color, k, seed)

    def _start(self, t):
        if self.start is None:
            return np.asarray(self.center, np.float64)[None, :] + self.cloud
        if callable(self.start):
            return np.asarray(self.start(t), np.float64).reshape(-1, 3)
        return np.asarray(self.start, np.float64).reshape(-1, 3)

    def targets(self, t, cam=None):
        return arrange_heart(self._start(self.t0), self.center, self.size, self.facing, self.tilt, self.face,
                             self.fill, cam)

    def gain(self, t):
        end = None if self.hold is None else self.t1 + self.hold + self.release + 0.2
        return 1.0 if (t >= self.t0 - 0.2 and (end is None or t <= end)) else 0.0

    def sample(self, t, cam=None):
        if self.gain(t) <= 0.0:
            return None
        if cam is None and self.camera is not None:
            cam = self.camera.state(t) if hasattr(self.camera, "state") else self.camera(t)
        a = self._start(t)
        tgt = self.targets(t, cam)
        s = self.s
        span = max(self.t1 - self.t0, 1e-6)
        delay = 0.35 * s[:, 1]
        u = np.clip(((t - self.t0) / span - delay) / 0.65, 0.0, 1.0)
        e = u * u * (3.0 - 2.0 * u)
        # a curved path: out to the side and up a little on the way
        mid = 0.5 * (a + tgt) + (s[:, 2:5] - 0.5) * self.size * 0.6
        pos = ((1 - e) ** 2)[:, None] * a + (2 * e * (1 - e))[:, None] * mid + (e * e)[:, None] * tgt
        alpha = np.full(self.k, 1.0)
        emit = 1.0 + 1.5 * np.exp(-np.abs(u - 1.0) / 0.05) * (u > 0.95)
        if self.hold is not None:
            tr = self.t1 + float(self.hold)
            v = np.clip((t - tr - 0.3 * s[:, 5]) / max(self.release, 1e-6), 0.0, 1.0)
            if (v > 0).any():
                ve = v * v * (3.0 - 2.0 * v)
                if self.then == "back":
                    pos = pos * (1 - ve)[:, None] + a * ve[:, None]
                elif self.then == "burst":
                    d = tgt - np.asarray(self.center, np.float64)[None, :]
                    pos = pos + d * (2.0 * ve)[:, None]
                    alpha *= 1.0 - ve
                else:
                    pos = pos + np.array([0.0, 1.0, 0.0])[None, :] * (self.size * 0.8 * ve)[:, None] \
                        + (s[:, 2:5] - 0.5) * (self.size * 0.5 * ve)[:, None]
                    alpha *= 1.0 - ve
        tw = 0.75 + 0.25 * np.sin(t * (3.0 + 4.0 * s[:, 0]) + s[:, 1] * 30.0)
        out = [dict(pos=pos.astype(np.float32), size=self.point, color=_deepen(self.col) * 1.6 * self.bright,
                    alpha=(alpha * tw).astype(np.float32), emit=emit.astype(np.float32), kind=self.kind,
                    twinkle=0.5, seed=s[:, 0], dof=self.dof)]
        out.append(dict(pos=pos.astype(np.float32), size=self.point * 6.0, color=_deepen(self.col) * self.bright,
                        alpha=(alpha * 0.04).astype(np.float32), kind="soft", seed=s[:, 1], dof=1.0, streak=0.0))
        return out
