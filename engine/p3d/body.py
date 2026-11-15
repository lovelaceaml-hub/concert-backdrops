"""People made of points: a lifelike human form, clothed in garments of light (engine/p3d).

    from p3d.body import Body, Hands
    def build(scene):
        Body("woman", at=(0, 2), facing=180, motion=[(0, "walk"), (6, "stand")],
             gesture=[(7, 14, "open_arms")], garment="robe", veil=True,
             look="glitter", color="#ffd9a0",
             effects=[dict(kind="form", t=0.5, dur=4), dict(kind="dissolve", t=16, dur=4)]).add(scene, "mother")
    P3D = dict(camera=..., world=..., setup=build)

A Body is a point set for the 3D layer (engine/p3d/api.py). What it is made of:
  the form      the MakeHuman base mesh (CC0), posed by a skeleton: motion capture (CMU) and gestures
                posed by hand (engine/p3d/actor.py, motion.py, gestures.py). No face: a profile is an outline.
  garments      cloth simulated on the body (engine/p3d/cloth.py): everyone is clothed.
  looks         how the points are drawn (engine/p3d/looks.py): glitter, plexus, rim, dots, window.
  effects       light that gathers into the body and scatters from it (engine/p3d/effects.py).
All of it is a pure function of time; a body may be asked for any time in any order.

KEYS OF Body(...)
  shape      "woman", "man" or "child"; height in metres (default: the shape's own, 1.59, 1.73, 1.31)
  at         where the feet stand: (x, z) on the lake or (x, y, z); or keys [(t, place), ...]; or a function of
             time (the figure is carried). See engine/p3d/actor.py.
  facing     degrees, 0 faces +z, 90 faces +x; a number or keys [(t, degrees), ...] (the figure turns)
  motion     a name or keys [(t, name), (t, name, dict(speed=..., blend=...)), ...]: motion.MOTIONS
  gesture    keys [(t_on, t_off, name), (t_on, t_off, name, dict(...))]: motion.GESTURES. A gesture's `to` is a
             point in the world or a function of time, usually another body's place: other.where(t, "palm.L")
  stoop      0..1: an elder's posture
  garment    "dress" (fitted, long skirt), "robe" (loose, wide sleeves, long skirt), "tunic" (short, with
             trousers), "coat" (to the knee, open in front, with trousers); default by shape
  veil       True or dict(length=1.0, wide=1.0): a veil from the crown over the shoulders and down the back
             (length 1.5: to the ground)
  hair       "bun" (hair worn close with a knot at the back: the default for a woman), "cap" (short: the
             default for a man and a child), True or dict(length=0.42) (long hair as flowing strands,
             simulated), or False (none). Not with a veil
  look       a look name, a dict, or a list of them (engine/p3d/looks.py). A look dict may carry
             weight=<number or function of time> (looks blend into each other over time) and
             after="<sweep>" or before="<sweep>" (the look lives behind or ahead of a sweep, see sweeps)
  color, color2   the two colours the look mixes (display hex)
  wash       dict(color="#...", amount=<number or function of time>): a colour wash over the whole body
  sweeps     dict(name=dict(t=..., at=<point, function of time, or the name of a place on this body>,
             speed=3.0, width=0.3, flash=2.0)): a front that crosses the body from a contact point at `speed`
             metres per second, flashing as it passes. Looks with after= or before= change over behind it
             (cold dust that ignites, a bloom from a touch).
  bright     overall brightness; points: how many points (30 to 120 thousand); size: grain size multiplier
  detail     dict region -> density multiplier for close-ups, for example dict(head=3, hand=4)
  part       draw only a part: "bust" (head and shoulders), "arm.R" / "arm.L" (a forearm and hand that fade out
             toward the elbow), "hand.R" / "hand.L" (the same, denser, the hand only), "hands" (both)
  hand       dict(side="R", at=..., aim=..., palm=..., pose="open" or [(t, pose), ...], anchor="palm"): the
             figure is moved so that this hand is exactly there (for hands in close-up and exact contact)
  scale      any size: 1 is life size, 100 a giant. Everything grows about the place `at`.
  frame      a function of time giving (x, y, z) or ((x, y, z), yaw degrees): moving ground. The body (with
             its garments and freed particles) rides it; `at` is then a place on that ground.
  light      a point in the world the body is lit from (plexus and glitter are brighter toward it)
  effects    a list of dict(kind=..., t=..., ...): engine/p3d/effects.py
  show       (t_in, t_out): the body exists only then (fading over `fade` seconds each way)
  wind       a Wind (engine/p3d/effects.py: one wind for the scene, with timed gusts) or (x, y, z) m/s;
             gust: how restless the air is
  seed       a number: another person (stance, timing, noise)

FOR SONG FILES AND OTHER POINT SETS (all in world coordinates, any time, any order)
  body.where(t, "palm.R")           a named place: head, crown, mouth, neck, heart, chest, back, pelvis, ground,
                                    and with .L / .R: shoulder, blade, elbow, wrist, palm, fingertips, index,
                                    thumb, pinch, hip, knee, ankle, toe, side. normal=True also gives the
                                    direction it faces.
  body.joint(t, "lowerarm01.L")     any joint of the skeleton
  body.constellation(t)             the body as a few stars and the lines between them (plain arrays)
  body.free(t)                      every particle that is off the body: dict(pos, vel, size, color, ...)
  body.handover(effect, t, targets) gives the free particles of one effect to target places
  body.shape_points(t)              the whole body as plain arrays (positions, normals)
"""
import numpy as np

from . import actor as act
from . import assets, cloth, looks
from . import bodymath as bm
from . import effects as fx
from .api import Mask, lin

GARMENTS = ("dress", "robe", "tunic", "coat")
PARTS = ("bust", "arm.L", "arm.R", "hand.L", "hand.R", "hands")
R = {name: k for k, name in enumerate(assets.REGIONS)}
REF_SPACING = np.sqrt(4.5 / 60000.0)        # metres between points of a whole body at 60 thousand points

STARS = ("crown", "neck", "chest", "pelvis", "shoulder.L", "shoulder.R", "elbow.L", "elbow.R", "wrist.L", "wrist.R",
         "fingertips.L", "fingertips.R", "hip.L", "hip.R", "knee.L", "knee.R", "ankle.L", "ankle.R", "toe.L", "toe.R")
STAR_LINES = (("crown", "neck"), ("neck", "chest"), ("chest", "pelvis"), ("neck", "shoulder.L"), ("neck", "shoulder.R"),
              ("shoulder.L", "elbow.L"), ("elbow.L", "wrist.L"), ("wrist.L", "fingertips.L"),
              ("shoulder.R", "elbow.R"), ("elbow.R", "wrist.R"), ("wrist.R", "fingertips.R"),
              ("pelvis", "hip.L"), ("pelvis", "hip.R"), ("hip.L", "knee.L"), ("knee.L", "ankle.L"), ("ankle.L", "toe.L"),
              ("hip.R", "knee.R"), ("knee.R", "ankle.R"), ("ankle.R", "toe.R"))


def _col(c):
    return lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


def _val(v, t):
    return float(v(t)) if callable(v) else float(v)


def _area(rig, keep, weight=None):
    t = rig.tris
    v = rig.verts0.astype(np.float64)
    a = 0.5 * np.linalg.norm(np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]), axis=1)
    ok = np.isin(rig.bone_region[rig.vert_bone[t[:, 0]]], [R[k] for k in keep])
    if weight is not None:
        a = a * weight((v[t[:, 0]] + v[t[:, 1]] + v[t[:, 2]]) / 3.0)
    return float(a[ok].sum())


class _SkinSource:
    """Points on the skin, or on a layer of cloth that lies on the skin (offset along the normal)."""

    def __init__(self, body, surf, part, offset=0.0):
        self.body, self.surf, self.part, self.offset = body, surf, part, offset
        self.n = surf.n
        self.h = (surf.rest[:, 1] / body.rig.height).astype(np.float32)
        if callable(offset):
            offset = np.asarray(offset(surf.rest), np.float32)
        self.offset = offset
        self.rest = surf.rest + surf.rest_normal * (offset[:, None] if np.ndim(offset) else offset)
        self.seed = surf.seed

    def at(self, t, sel=None):
        v, nv = self.body._skinned(t)
        vi = self.surf.vi if sel is None else self.surf.vi[sel]
        ba = self.surf.bary if sel is None else self.surf.bary[sel]
        p = (v[vi] * ba[:, :, None]).sum(1)
        n = (nv[vi] * ba[:, :, None]).sum(1)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        if np.ndim(self.offset):
            off = self.offset if sel is None else self.offset[sel]
            p = p + n * off[:, None]
        elif self.offset:
            p = p + n * self.offset
        return p, n


class _RigidSource:
    """Points fixed to one bone (a knot of hair at the back of the head)."""

    def __init__(self, body, bone, pts, nrm, part, salt=0):
        self.body, self.part = body, part
        self.bone = int(bone)
        self.pts = np.asarray(pts, np.float32)
        self.nrm = np.asarray(nrm, np.float32)
        self.n = len(self.pts)
        self.rest = self.pts.copy()
        self.h = (self.pts[:, 1] / body.rig.height).astype(np.float32)
        self.seed = bm.rand(self.n, 91 + salt).astype(np.float32)

    def at(self, t, sel=None):
        M = self.body.actor.frame(t)["M"][self.bone].astype(np.float64)
        p = self.pts if sel is None else self.pts[sel]
        n = self.nrm if sel is None else self.nrm[sel]
        return (p @ M[:, :3].T + M[:, 3]).astype(np.float32), (n @ M[:, :3].T).astype(np.float32)


def _bun(rig, n):
    """A knot of hair at the back of the head: points on an egg shape (rest pose), with outward normals."""
    k = rig.height / 1.6
    hc = rig.head_centre
    c = hc + np.array([0.0, 0.0, -0.098]) * k
    r = np.array([0.043, 0.036, 0.034]) * k
    u = bm.rand(n, 93) * 2.0 - 1.0
    a = bm.rand(n, 94) * 2.0 * np.pi
    q = np.sqrt(1.0 - u * u)
    d = np.stack([q * np.cos(a), u, q * np.sin(a)], axis=1)
    pts = c + d * r
    nrm = d / r
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    return pts, nrm


class _ClothSource:
    def __init__(self, body, cp, part):
        self.body, self.cp, self.part = body, cp, part
        self.n = cp.n
        self.rest = cp.rest()
        self.h = (self.rest[:, 1] / body.rig.height).astype(np.float32)
        self.seed = cp.seed

    def at(self, t, sel=None):
        p, n = self.cp.at(t, True, sel)
        if self.cp.strands:
            # for strands the second value is the strand direction: give a normal across it
            n = np.cross(n, [0.0, 1.0, 0.0])
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        return p, n


class _Shape:
    """The body's own silhouette for the renderer's mask pass: the points that are still on the body."""

    def __init__(self, body):
        self.body = body
        n = body.cloud["n"]
        self.idx = np.arange(n)[(body.cloud["seed"] < min(26000.0 / max(n, 1), 1.0))
                                & ((body.cloud["part"] != looks.HAIR) | body.skinlike)]
        self.skinlike = body.skinlike[self.idx]
        hy = body.rig.head[body.rig.idx["neck03"]][1]
        self.head = body.skinlike[self.idx] & (body.cloud["rest"][self.idx, 1] > hy)
        self.inset = 0.005 + 0.008 + 0.002          # half the disc, the mask's margin, and a little more

    def sample(self, t):
        b = self.body
        if b.show is not None and (t < b.show[0] or t > b.show[1]):
            return []
        pos, nrm = b.points_at(t, self.idx)
        on = b._on(t)[self.idx]
        keep = on > 0.25
        if not keep.any():
            return []
        pos, nrm = pos[keep].astype(np.float64), nrm[keep].astype(np.float64)
        # each point is drawn as a disc grown by the mask's own margin: pull it in by as much, so the dark shape
        # ends just inside the bright edge (no dark halo round the body). Skin follows its normal; cloth (whose
        # normals may point either way) is pulled toward the body's own axis.
        inset = self.inset * b.k
        sk = self.skinlike[keep]
        d = nrm.copy()
        # the head (whose smoothed face has a few stray normals): straight in toward its centre
        hd = self.head[keep]
        if hd.any():
            hc = b.actor.where(t, "head")
            r = pos[hd] - hc
            d[hd] = r / np.maximum(np.linalg.norm(r, axis=1, keepdims=True), 1e-6)
        if (~sk).any():
            ax = b.actor.where(t, "pelvis")
            h = pos[~sk] - ax
            h[:, 1] = 0.0
            d[~sk] = h / np.maximum(np.linalg.norm(h, axis=1, keepdims=True), 1e-6)
        pos = pos - d * inset
        pos = b._w(pos, t)
        return dict(pos=pos, size=0.010 * b.k * b.scale, alpha=on[keep], kind="soft")


class Body:
    wants_camera = True

    def __init__(self, shape="woman", height=None, at=(0.0, 0.0), facing=0.0, motion="stand", gesture=(),
                 garment="default", veil=False, hair="default", look="glitter", color="#f2b865", color2="#ffe9c4",
                 bright=1.0, points=60000, detail=None, part=None, hand=None, light=None, effects=(), show=None,
                 fade=0.6, wind=None, gust=0.35, seed=1.0, size=1.0, scale=1.0, frame=None, stoop=0.0, wash=None,
                 sweeps=None):
        self.rig = assets.Rig(shape, height)
        rig = self.rig
        self.seed = float(seed)
        self.k = rig.height / 1.6
        self.scale = float(scale)
        self.frame = frame
        self.color = _col(color)
        self.color2 = _col(color2)
        self.bright = float(bright)
        self.light = None if light is None else np.asarray(light, np.float64)
        self.show = None if show is None else (float(show[0]), float(show[1]))
        self.fade = float(fade)
        self.wash = dict(wash) if wash else None
        self.sweeps = {k: dict(v) for k, v in (sweeps or {}).items()}
        if isinstance(wind, fx.Wind):
            self.wind = wind
        elif wind is None:
            self.wind = None
        else:
            self.wind = fx.Wind(base=wind, sway=gust) if np.any(np.asarray(wind) != 0) else None
        if part is not None and part not in PARTS:
            raise ValueError("part must be one of %s, got %r" % (PARTS, part))
        self.part = part
        if hand is not None:
            hand = dict(hand)
            hand.setdefault("side", part[-1] if part in ("arm.L", "arm.R", "hand.L", "hand.R") else "R")
        self.actor = act.Actor(shape, height, at=at, facing=facing, motion=motion, gesture=gesture, seed=seed,
                               rig=rig, start=None if self.show is None else self.show[0], stoop=stoop, hand=hand)
        self.actor.to_internal = self._to_internal
        self.origin0 = self.actor.origin.copy()
        self.t_start = self.show[0] if self.show else self.actor.t_ref
        if garment == "default":
            garment = "dress" if shape == "woman" else "tunic"
        if garment is not None and garment not in GARMENTS:
            raise ValueError("garment must be one of %s or None, got %r" % (GARMENTS, garment))
        self.garment = garment
        hc = rig.head_centre
        k = self.k

        # ---- what is cloth and what is skin
        pieces = []
        layers = []       # (regions, offset, part code, weight function)
        skin = ["head", "neck", "hand", "foot"]
        skin_w = {}       # region -> weight function (where the region shows as skin)
        side_w = None
        if part in ("arm.L", "arm.R", "hand.L", "hand.R", "hands"):
            skin = ["forearm", "hand"]
            garment = None
            veil = hair = False
            if part != "hands":
                sg = 1.0 if part[-1] == "L" else -1.0
                side_w = lambda c: (c[:, 0] * sg > 0).astype(float)      # noqa: E731
        hip_y = rig.head[rig.idx["upperleg01.L"]][1]

        def loose(c, base, more, hip_y=hip_y):
            # trousers that hang loose: the cloth stands further off the leg toward the ankle
            return base + more * np.clip(1.0 - c[:, 1] / hip_y, 0.0, 1.0) ** 1.3
        if garment == "dress":
            layers.append((["torso", "arm", "forearm"], 0.009 * k, looks.CLOTH, None))
            pieces.append(cloth.skirt(rig, flare=1.7))
        elif garment == "robe":
            layers.append((["torso"], 0.014 * k, looks.CLOTH, None))
            sh_x = abs(rig.head[rig.idx["upperarm01.L"]][0]) + 0.07 * k
            layers.append((["arm"], 0.012 * k, looks.CLOTH, lambda c: (np.abs(c[:, 0]) < sh_x).astype(float)))
            # an under-sleeve on the forearm, so a raised arm never leaves its hand floating
            layers.append((["forearm"], 0.008 * k, looks.CLOTH, None))
            pieces += [cloth.skirt(rig, flare=2.0, bell=0.6), cloth.sleeve(rig, "L"), cloth.sleeve(rig, "R")]
        elif garment == "tunic":
            layers.append((["torso", "arm", "forearm"], 0.011 * k, looks.CLOTH, None))
            layers.append((["hips", "leg", "shin"], lambda c: loose(c, 0.014 * k, 0.026 * k), looks.CLOTH, None))
            pieces.append(cloth.skirt(rig, hem=0.56, flare=1.32, rows=14, bell=0.12, air=1.1, name="skirt"))
        elif garment == "coat":
            layers.append((["torso", "arm", "forearm"], 0.013 * k, looks.CLOTH, None))
            layers.append((["hips", "leg", "shin"], lambda c: loose(c, 0.014 * k, 0.022 * k), looks.CLOTH, None))
            pieces.append(cloth.skirt(rig, hem=0.40, flare=1.5, rows=20, bell=0.25, open_front=True, name="skirt"))
        if veil:
            vk = dict(veil) if isinstance(veil, dict) else {}
            pieces.append(cloth.veil(rig, **vk))
            y0 = hc[1] + 0.012 * k

            def cover(c, y0=y0, hc=hc, k=k):
                # all of the head but the face: the top, the back and the sides down to the jaw
                return ((c[:, 1] > y0) | ((c[:, 2] < hc[2] + 0.025 * k) & (c[:, 1] > hc[1] - 0.075 * k))).astype(float)
            layers.append((["head"], 0.011 * k, looks.VEIL, cover))
            skin_w["head"] = lambda c, cover=cover: 1.0 - cover(c)
        elif hair:
            if hair == "default":
                hair = "bun" if shape == "woman" else "cap"
            scalp = (lambda c: ((c[:, 1] > hc[1] + 0.02 * k)
                                | ((c[:, 2] < hc[2] + 0.01 * k) & (c[:, 1] > hc[1] - 0.06 * k))).astype(float))
            if hair in ("bun", "cap"):
                # hair worn close: a layer over the scalp (and a knot at the back for "bun"), no simulation
                layers.append((["head"], 0.007 * k, looks.HAIR, scalp))
                if hair == "bun":
                    self._bun = True
            else:
                hk = dict(hair) if isinstance(hair, dict) else {}
                pieces.append(cloth.hair(rig, **hk))
                layers.append((["head"], 0.006 * k, looks.HAIR, scalp))
        self.cloth = cloth.ClothSystem(self.actor, pieces, t_start=self.t_start, wind=self.wind if self.wind else (0, 0, 0),
                                       gust=gust, seed=self.seed) if pieces else None

        # ---- share the points out by area
        det = dict(head=1.5, hand=1.6)
        det.update(detail or {})
        want = []      # (kind, weight, area, payload)
        def _wfn(reg):
            fa, fb = side_w, skin_w.get(reg)
            if fa is None or fb is None:
                return fa or fb
            return lambda c: fa(c) * fb(c)
        for reg in skin:
            a = _area(rig, [reg], _wfn(reg))
            if a > 1e-6:
                want.append(("skin", a * det.get(reg, 1.0), a, reg))
        for (regs, off, pcode, wfn) in layers:
            a = _area(rig, regs, wfn)
            want.append(("layer", a * (1.6 if pcode in (looks.VEIL, looks.HAIR) else 1.0), a, (regs, off, pcode, wfn)))
        if getattr(self, "_bun", False):
            want.append(("bun", 0.030 * k * k * 1.6, 0.030 * k * k, None))
        for pc in pieces:
            if pc.strands:
                want.append(("cloth", 0.10, 0.10, pc))
            else:
                r = pc.rest
                nxt = np.roll(r, -1, axis=1) if pc.closed else np.concatenate([r[:, 1:], r[:, -1:]], axis=1)
                a = float(np.linalg.norm(np.cross((nxt - r)[:-1], (r[1:] - r[:-1])), axis=2).sum())
                want.append(("cloth", a * (1.05 if pc.name == "veil" else 0.8), a, pc))
        total = sum(w for _, w, _, _ in want)
        area = sum(a for _, _, a, _ in want)
        self.grain = float(np.clip(np.sqrt(area / max(points, 1)) / REF_SPACING, 0.1, 3.0))
        self.sources = []
        salt = 0
        for kind, w, _a, payload in want:
            n = max(int(round(points * w / total)), 16)
            salt += 7
            if kind == "skin":
                reg = payload
                surf = assets.Surface(rig, n, keep=[reg], salt=salt, weight=_wfn(reg))
                self.sources.append(_SkinSource(self, surf, looks.HAND if reg in ("hand", "forearm") else
                                                (looks.FOOT if reg == "foot" else looks.SKIN)))
            elif kind == "layer":
                regs, off, pcode, wfn = payload
                surf = assets.Surface(rig, n, keep=regs, salt=salt, weight=wfn)
                self.sources.append(_SkinSource(self, surf, pcode, off))
            elif kind == "bun":
                pts, nrm = _bun(rig, n)
                self.sources.append(_RigidSource(self, rig.idx["head"], pts, nrm, looks.HAIR, salt))
            else:
                cp = cloth.ClothPoints(self.cloth, payload.name, n, salt=salt)
                self.sources.append(_ClothSource(self, cp, looks.HAIR if payload.strands else
                                                 (looks.VEIL if payload.name == "veil" else looks.CLOTH)))
        offs = np.cumsum([0] + [s.n for s in self.sources])
        self.offs = offs
        n = int(offs[-1])
        part_code = np.concatenate([np.full(s.n, s.part) for s in self.sources])
        self.src_of = np.concatenate([np.full(s_.n, j) for j, s_ in enumerate(self.sources)])
        seed_arr = np.concatenate([s.seed for s in self.sources]).astype(np.float32)
        rest = np.concatenate([s.rest for s in self.sources]).astype(np.float32)
        h = np.concatenate([s.h for s in self.sources]).astype(np.float32)
        mix = (bm.hashf(np.arange(n), 4) ** 1.5)[:, None]
        g = k * size * self.grain
        self.skinlike = np.concatenate([np.full(s_.n, isinstance(s_, (_SkinSource, _RigidSource)))
                                        for s_ in self.sources])
        edge = self._edges(rest, part_code, k)
        self.cloud = dict(n=n, part=part_code, seed=seed_arr, rest=rest, h=np.clip(h, 0.0, 1.0), edge=edge,
                          size=((0.003 + 0.008 * seed_arr.astype(np.float64) ** 4) * g).astype(np.float32),
                          color=(self.color[None] * (1 - mix) + self.color2[None] * mix).astype(np.float32),
                          pairs_fn=self._pairs)
        # a part only: fade away from it
        self.part_alpha = None
        if part in ("arm.L", "arm.R", "hand.L", "hand.R", "hands"):
            pa = np.zeros(n, np.float32)
            for sd in (("L", "R") if part == "hands" else (part[-1],)):
                wr = rig.head[rig.idx["wrist." + sd]]
                el = rig.head[rig.idx["lowerarm01." + sd]]
                ax = (el - wr) / np.linalg.norm(el - wr)
                along = (rest - wr) @ ax / np.linalg.norm(el - wr)          # 0 at the wrist, 1 at the elbow
                same = (rest[:, 0] > 0) == (sd == "L")
                far = 0.75 if part.startswith("arm") or part == "hands" else 0.45
                pa = np.maximum(pa, same * np.clip(1.0 - (along - 0.12) / far, 0.0, 1.0) ** 1.6)
            self.part_alpha = pa.astype(np.float32)
        elif part == "bust":
            self.part_alpha = np.clip((h - 0.60) / 0.14, 0.0, 1.0).astype(np.float32)

        # ---- looks
        lk = look if isinstance(look, (list, tuple)) else [look]
        self.look_names = [(x if isinstance(x, str) else x["name"]) for x in lk]
        self.layers = []
        for x in lk:
            spec = dict(name=x) if isinstance(x, str) else dict(x)
            when = dict(weight=spec.pop("weight", 1.0), after=spec.pop("after", None), before=spec.pop("before", None),
                        detail=spec.get("detail", None))
            for ly in looks.build(spec, self.cloud, self.color, self.color2, self.bright, g):
                ly.update(when)
                self.layers.append(ly)
        for name in [ly[key] for ly in self.layers for key in ("after", "before") if ly[key]]:
            if name not in self.sweeps:
                raise ValueError("a look refers to the sweep %r, which is not in sweeps" % (name,))
        self._sk = {}
        self._pts = {}
        self._anchors = {}
        self._onc = (None, None)
        # ---- effects
        self.fx = []
        for j, e in enumerate(effects):
            self.fx.append(fx.make(self, self._effect_spec(e), j))

    def _edges(self, rest, part_code, k):
        """0..1 per point: how near it is to the end of a garment (a hem, a cuff, the neckline)."""
        n = len(rest)
        edge = np.zeros(n, np.float32)
        cloth_like = np.isin(part_code, (looks.CLOTH, looks.VEIL))
        bare = np.isin(part_code, (looks.SKIN, looks.HAND, looks.FOOT))
        if cloth_like.any() and bare.any():
            from scipy.spatial import cKDTree
            d, _ = cKDTree(rest[bare].astype(np.float64)).query(rest[cloth_like].astype(np.float64), k=1)
            edge[cloth_like] = np.exp(-(d / (0.016 * k)) ** 2)
        for j, s_ in enumerate(self.sources):
            if isinstance(s_, _ClothSource) and not s_.cp.strands:
                u = s_.cp.u
                sl = slice(self.offs[j], self.offs[j + 1])
                edge[sl] = np.maximum(edge[sl], bm.smooth((u - 0.88) / 0.10))
        return edge

    # ------------------------------------------------------------------ world and own space
    def _frame(self, t):
        if self.frame is None:
            return None
        f = self.frame(t)
        if len(f) == 2 and np.ndim(f[0]) == 1:
            return np.asarray(f[0], np.float64), float(f[1])
        return np.asarray(f, np.float64), 0.0

    def _w(self, pos, t):
        """Own space to the world: positions (N, 3)."""
        fr = self._frame(t)
        if fr is None and self.scale == 1.0:
            return pos
        p = self.origin0 + (np.asarray(pos, np.float64) - self.origin0) * self.scale
        if fr is not None:
            T, yaw = fr
            if yaw:
                p = bm.qrot(bm.qy(np.radians(yaw)), p)
            p = p + T
        return p

    def _wdir(self, d, t):
        fr = self._frame(t)
        if fr is None or not fr[1]:
            return d
        return bm.qrot(bm.qy(np.radians(fr[1])), np.asarray(d, np.float64))

    def _to_internal(self, X, t):
        """The world to own space."""
        fr = self._frame(t)
        p = np.asarray(X, np.float64)
        if fr is None and self.scale == 1.0:
            return p
        if fr is not None:
            T, yaw = fr
            p = p - T
            if yaw:
                p = bm.qrot(bm.qy(-np.radians(yaw)), p)
        return self.origin0 + (p - self.origin0) / self.scale

    def _effect_spec(self, e):
        """An effect's dict with its world places (targets, sources) turned into the body's own space."""
        if isinstance(e, (tuple, list)):
            d = dict(e[2]) if len(e) > 2 else {}
            d.update(kind=e[0], t=e[1])
            e = d
        e = dict(e)
        if e.get("to"):
            to = dict(e["to"])
            to["targets"] = self._wrap(to["targets"])
            e["to"] = to
        if e.get("source") is not None:
            e["source"] = self._wrap(e["source"])
        if e.get("dir") is not None and self.frame is not None:
            e["dir"] = self._wdir(e["dir"], self.t_start)
        return e

    def _wrap(self, pts):
        if self.frame is None and self.scale == 1.0:
            return pts
        if callable(pts):
            return lambda t: self._to_internal(np.asarray(pts(t), np.float64).reshape(-1, 3), t)
        fixed = np.asarray(pts, np.float64).reshape(-1, 3)
        return lambda t: self._to_internal(fixed, t)

    # ------------------------------------------------------------------ geometry (own space)
    def _skinned(self, t):
        key = round(float(t), 6)
        c = self._sk.get(key)
        if c is None:
            c = self.rig.skin(self.actor.frame(t)["M"], True)
            if len(self._sk) > 40:
                self._sk.pop(next(iter(self._sk)))
            self._sk[key] = c
        return c

    def points_at(self, t, idx=None):
        """Positions and normals of the cloud's points at t (all, or those in idx), in the body's own space."""
        if idx is None:
            key = round(float(t), 6)
            c = self._pts.get(key)
            if c is None:
                ps, ns = zip(*[s.at(t) for s in self.sources])
                c = (np.concatenate(ps).astype(np.float32), np.concatenate(ns).astype(np.float32))
                if len(self._pts) > 3:
                    self._pts.pop(next(iter(self._pts)))
                self._pts[key] = c
            return c
        idx = np.asarray(idx)
        pos = np.empty((len(idx), 3), np.float32)
        nrm = np.empty((len(idx), 3), np.float32)
        which = np.searchsorted(self.offs, idx, side="right") - 1
        for j, s in enumerate(self.sources):
            m = which == j
            if m.any():
                pos[m], nrm[m] = s.at(t, idx[m] - self.offs[j])
        return pos, nrm

    def anchor(self, key, tb, idx, pool=None):
        """Where the cloud points idx were, each at its own time tb (times are taken in steps of 1/15 s):
        (positions, normals). pool: the full set idx is drawn from, when it varies from call to call."""
        idx = np.asarray(idx)
        bins = np.floor(np.asarray(tb, np.float64) / fx.BIN).astype(np.int64)
        pos = np.empty((len(idx), 3), np.float32)
        nrm = np.empty((len(idx), 3), np.float32)
        for b in np.unique(bins):
            m = bins == b
            ck = (key, int(b))
            c = self._anchors.get(ck)
            want = idx[m]
            if c is None:
                ids = np.unique(want) if pool is None else np.unique(pool)
                p, n = self.points_at((b + 0.5) * fx.BIN, ids)
                c = (ids, p, n)
                if len(self._anchors) > 900:
                    for old in list(self._anchors)[:300]:
                        self._anchors.pop(old)
                self._anchors[ck] = c
            w = np.minimum(np.searchsorted(c[0], want), len(c[0]) - 1)
            if (c[0][w] != want).any():
                ids = np.union1d(c[0], want)
                p, n = self.points_at((b + 0.5) * fx.BIN, ids)
                c = (ids, p, n)
                self._anchors[ck] = c
                w = np.searchsorted(c[0], want)
            pos[m] = c[1][w]
            nrm[m] = c[2][w]
        return pos, nrm

    def _pairs(self, nodes, links=3, reach=0.11):
        """Pairs of nearby points among `nodes` (indices into the cloud), by their places in the rest pose:
        the lines of a plexus. Returns (m, 2) positions into `nodes`."""
        from scipy.spatial import cKDTree
        p = self.cloud["rest"][nodes].astype(np.float64)
        part = self.cloud["part"][nodes]
        src = self.src_of[nodes]
        tree = cKDTree(p)
        _d, j = tree.query(p, k=links + 1, distance_upper_bound=reach * self.k * max(self.grain, 0.35) ** 0.5)
        i = np.repeat(np.arange(len(nodes)), links)
        j = j[:, 1:].reshape(-1)
        ok = j < len(nodes)
        i, j = i[ok], j[ok]
        # lines stay within one piece (a skirt never links to the trousers under it); bare skin links across
        ok = (src[i] == src[j]) | ((part[i] <= 1) & (part[j] <= 1))
        return np.unique(np.sort(np.stack([i[ok], j[ok]], axis=1), axis=1), axis=0)

    def _on(self, t):
        """How much each cloud point is on the body at t (0: gone or not yet there)."""
        key = round(float(t), 6)
        if self._onc[0] == key:
            return self._onc[1]
        on = np.ones(self.cloud["n"], np.float32)
        if self.part_alpha is not None:
            on *= self.part_alpha
        for e in self.fx:
            if hasattr(e, "on_body"):
                e.on_body(t, on)
        self._onc = (key, on)
        return on

    def _sweep(self, name, t, pos):
        """(how far the sweep has passed each point 0..1, its flash at each point)."""
        s = self.sweeps[name]
        t0 = float(s.get("t", 0.0))
        if t < t0:
            return np.zeros(len(pos), np.float32), np.zeros(len(pos), np.float32)
        at = s.get("at", "heart")
        if isinstance(at, str):
            o = self.actor.where(t, at)
        else:
            o = self._to_internal(np.asarray(at(t) if callable(at) else at, np.float64), t)
        wd = float(s.get("width", 0.3)) / self.scale
        r = float(s.get("speed", 3.0)) * (t - t0) / self.scale
        d = np.linalg.norm(pos - o.astype(np.float32), axis=1)
        f = bm.smooth((r - d) / wd)
        fl = float(s.get("flash", 1.5)) * np.exp(-((d - r) / wd) ** 2)
        return f.astype(np.float32), fl.astype(np.float32)

    # ------------------------------------------------------------------ the point set
    def gain(self, t):
        if self.show is None:
            return 1.0
        a = float(bm.ramp(t, self.show[0], self.show[0] + self.fade))
        b = 1.0 - float(bm.ramp(t, self.show[1] - self.fade, self.show[1]))
        return a * b

    def sample(self, t, cam=None):
        if self.show is not None and (t < self.show[0] or t > self.show[1]):
            return []
        cl = self.cloud
        pos, nrm = self.points_at(t)
        on = self._on(t)
        sw = {name: self._sweep(name, t, pos) for name in self.sweeps}
        flash = None
        for name, (_f, fl) in sw.items():
            flash = fl if flash is None else np.maximum(flash, fl)
        wash = None
        if self.wash is not None:
            wa = _val(self.wash.get("amount", 1.0), t)
            if wa > 0.002:
                wash = (wa, _col(self.wash.get("color", "#ffffff")))
        light = None if self.light is None else self._to_internal(self.light, t)
        out = []
        for ly in self.layers:
            wgt = _val(ly["weight"], t)
            if wgt <= 0.002:
                continue
            idx = ly["idx"]
            a = ly["alpha"] * on[idx] * wgt
            if ly["after"]:
                a = a * sw[ly["after"]][0][idx]
            if ly["before"]:
                a = a * (1.0 - sw[ly["before"]][0][idx])
            det = None
            if ly.get("lines") is not None and ly["detail"] is not None:
                det = float(np.clip(_val(ly["detail"], t), 0.0, 1.0))
                if "rank" not in ly:
                    ly["rank"] = np.argsort(np.argsort(ly["seed"], kind="stable"), kind="stable")
                count = 24 + (len(idx) - 24) * det ** 1.6
                a = a * np.clip(count - ly["rank"], 0.0, 1.0)
            keep = a > 0.004
            if not keep.any():
                continue
            ii = idx[keep]
            p = pos[ii]
            n = nrm[ii]
            a = a[keep]
            col = ly["color"][keep]
            emit = ly["emit"][keep]
            if ly["lit"] > 0.0 and light is not None:
                ldir = light[None] - p
                ldir /= np.maximum(np.linalg.norm(ldir, axis=1, keepdims=True), 1e-9)
                f = np.clip(0.5 + 0.5 * (n * ldir).sum(1), 0.0, 1.0) ** 1.6
                a = a * ((1.0 - ly["lit"]) + ly["lit"] * 2.2 * f)
            if flash is not None:
                emit = emit * (1.0 + flash[ii])
            if wash is not None:
                lum = col.mean(1, keepdims=True) / max(float(wash[1].mean()), 1e-6)
                col = col * (1.0 - wash[0]) + wash[1][None] * lum * wash[0]
            out.append(dict(pos=p, normal=n, size=ly["size"][keep], color=col, alpha=a, emit=emit,
                            seed=ly["seed"][keep], kind=ly["kind"], twinkle=ly["twinkle"], rim=ly["rim"],
                            backlight=ly["backlight"]))
            if ly.get("lines") is not None and len(ly["lines"]):
                pr = ly["lines"]
                full = np.zeros(len(idx), np.float32)
                full[keep] = a / np.maximum(ly["alpha"][keep], 1e-6)
                la = np.minimum(full[pr[:, 0]], full[pr[:, 1]])
                kk = la > 0.02
                if kk.any():
                    lc = ly["line_color"]
                    if wash is not None:
                        lc = lc * (1.0 - wash[0]) + wash[1] * (lc.mean() / max(float(wash[1].mean()), 1e-6)) * wash[0]
                    out.append(dict(pos=pos[idx[pr[kk, 0]]], pos2=pos[idx[pr[kk, 1]]], size=ly["line_size"],
                                    color=lc, alpha=np.minimum(la[kk], 1.0) * ly["line_alpha"], kind="line"))
                if det is not None and det < 0.999:
                    out += self._star_batches(t, ly, (1.0 - 0.75 * det) * wgt * float(on.mean() > 0.02))
        if self.cloth is not None and "hair" in self.cloth.slices:
            hm = cl["part"] == looks.HAIR
            hair_on = float(on[hm].mean()) if hm.any() else 1.0
            if hair_on > 0.02:
                g = self.cloth.piece("hair", t)
                seg = g.shape[0] - 1
                u = (np.arange(seg) / seg)[:, None] * np.ones((1, g.shape[1]))
                a0 = 0.30 * hair_on * self.bright
                av = (a0 * (1.0 - 0.6 * u)).reshape(-1)
                av2 = (a0 * (1.0 - 0.6 * (u + 1.0 / seg))).reshape(-1)
                p1, p2 = g[:-1].reshape(-1, 3), g[1:].reshape(-1, 3)
                if "rim" in self.look_names and cam is not None:
                    # a dark head of hair with light only on its outline, as the rim draws the body
                    eye = self._to_internal(np.asarray(cam.pos, np.float64), t)
                    mid = 0.5 * (p1 + p2)
                    hc = self.actor.where(t, "head")
                    nr = mid - hc
                    low = mid[:, 1] < hc[1] - 0.10 * self.k
                    nr[low, 1] = 0.0
                    nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-6)
                    vv = eye[None] - mid
                    vv /= np.maximum(np.linalg.norm(vv, axis=1, keepdims=True), 1e-6)
                    f = (1.0 - np.abs((nr * vv).sum(1))) ** 4
                    av = av * (0.04 + 1.1 * f)
                    av2 = av2 * (0.04 + 1.1 * f)
                out.append(dict(pos=p1, pos2=p2, size=0.0016 * self.k, color=self.color * 0.7 + self.color2 * 0.3,
                                alpha=av, alpha2=av2, kind="line"))
        for e in self.fx:
            out += e.batches(t, cam)
        return self._out(out, t)

    def _star_batches(self, t, ly, alpha):
        """The body as a constellation: a star at each joint and the lines between them (own space)."""
        if alpha <= 0.01:
            return []
        p = np.array([self.actor.where(t, n) for n in STARS])
        ia = [STARS.index(a) for a, _ in STAR_LINES]
        ib = [STARS.index(b) for _, b in STAR_LINES]
        c = ly["line_color"]
        return [dict(pos=p, size=0.02 * self.k, color=self.color2, alpha=alpha, kind="spark", emit=3.0, twinkle=0.5),
                dict(pos=p[ia], pos2=p[ib], size=0.003 * self.k, color=c, alpha=0.7 * alpha, kind="line")]

    def _out(self, batches, t):
        """Own space to the world for finished batches."""
        if self.frame is None and self.scale == 1.0:
            return batches
        s = self.scale
        for b in batches:
            b["pos"] = self._w(b["pos"], t)
            if b.get("pos2") is not None:
                b["pos2"] = self._w(b["pos2"], t)
            if b.get("normal") is not None:
                b["normal"] = self._wdir(b["normal"], t)
            if b.get("vel") is not None:
                b["vel"] = self._wdir(b["vel"], t) * s
            b["size"] = np.asarray(b.get("size", 0.02)) * s
        return batches

    # ------------------------------------------------------------------ for song files and other point sets
    def where(self, t, name, normal=False, raw=False):
        """A named place on the body at t, in the world (see the module text for the names). With normal=True:
        (position, the direction it faces). raw=True: where it is without the body's gestures (what another
        body's gesture should aim at when this body also reaches for that one: no waiting on each other)."""
        r = self.actor.where(t, name, normal, raw)
        if normal:
            return self._w(r[0][None], t)[0], self._wdir(r[1], t)
        return self._w(r[None], t)[0]

    def joint(self, t, bone):
        """World position of a joint of the skeleton (the head of a bone, engine/p3d/assets.py) at t."""
        return self._w(self.actor.joint(t, bone)[None], t)[0]

    def constellation(self, t):
        """The body as a few stars: dict(names, pos (K, 3) world, pairs (M, 2) into pos)."""
        p = self._w(np.array([self.actor.where(t, n) for n in STARS]), t)
        pairs = np.array([[STARS.index(a), STARS.index(b)] for a, b in STAR_LINES])
        return dict(names=STARS, pos=p, pairs=pairs)

    def free(self, t):
        """Plain arrays of every particle that is off the body at t: dict(id, pos, vel, size, color, alpha,
        seed, age, effect), world coordinates. `effect` is the place of the effect in the effects list."""
        r = fx._free_report([e for e in self.fx if isinstance(e, fx._Free)], t)
        if (self.frame is not None or self.scale != 1.0) and len(r["pos"]):
            r["vel"] = self._wdir(r["vel"], t) * self.scale
            r["pos"] = self._w(r["pos"], t)
            r["size"] = r["size"] * self.scale
        return r

    def effect(self, which):
        """An effect of this body by its place in the list or by its kind (the first of that kind)."""
        if isinstance(which, int):
            return self.fx[which]
        for e in self.fx:
            if e.kind == which:
                return e
        raise KeyError(which)

    def handover(self, which, t, targets, arrive=1.5, stagger=0.5, until=None):
        """From t on, the free particles of one effect fly to `targets` ((K, 3) world places, or a function of
        time) and stay there (see engine/p3d/effects.py). Returns the effect; effect.assignment() tells who
        went where."""
        return self.effect(which).handover(t, self._wrap(targets), arrive=arrive, stagger=stagger, until=until)

    def shape_points(self, t):
        """The whole body at t as plain arrays (positions, normals) in the world, whatever the effects do to
        it: for another point set that wants to become this body, or to use its shape."""
        p, n = self.points_at(t)
        return self._w(p, t), self._wdir(n, t)

    def mask(self, **kw):
        """The renderer mask that suits the look: a dark body for "rim", a window onto a sky for "window"
        (keywords go to p3d.api.Mask, for example sky="sunrise"). The shape is the body itself, without the
        particles that have left it."""
        if "window" in self.look_names:
            d = dict(mode="sky", sky="sunrise", edge=0.5, grow=0.012 * self.k * self.scale, source=_Shape(self))
            d.update(kw)
            return Mask(**d)
        if "rim" in self.look_names:
            d = dict(mode="dark", strength=0.9, grow=0.008 * self.k * self.scale, source=_Shape(self))
            d.update(kw)
            return Mask(**d)
        return None

    def add(self, scene, name, **kw):
        """Adds the body to the scene with the mask its look needs. Keywords go to scene.add; mask=dict(...)
        goes to the mask, mask=False leaves it out."""
        mk = kw.pop("mask", None)
        if mk is False:
            m = None
        elif isinstance(mk, dict):
            m = self.mask(**mk)
        else:
            m = mk if mk is not None else self.mask()
        scene.add(name, self, mask=m, **kw)
        return self


def Hands(meet=(0.0, 1.25, 0.0), t_touch=6.0, axis=90.0, color="#ffcf8a", color2="#8fd0ff", look="glitter",
          apart=0.5, approach=5.0, points=50000, shed=True, shapes=("woman", "man"), bright=1.0, seed=2.0, tilt=18.0,
          poses=("offer", "open"), flare=1.0):
    """Two hands of light reaching for each other until their fingertips touch (ref 04): returns dict(left=Body,
    right=Body, flare=Flare). Add all three to the scene.

    meet      the point where the fingertips meet; t_touch: when
    axis      the direction from the first hand to the second, degrees (90: along +x)
    apart     metres between the fingertips at the start; approach: seconds of reaching
    tilt      degrees: the first hand comes from a little below, the second from a little above
    flare     size of the flash at the touch (1 suits this close-up; 0 for none)
    """
    meet = np.asarray(meet, np.float64)
    a = np.radians(axis)
    d = np.array([np.sin(a), 0.0, np.cos(a)])
    out = {}
    t0 = t_touch - approach
    tl = np.radians(tilt)
    for j, (name, sgn, col, side) in enumerate((("left", 1.0, color, "R"), ("right", -1.0, color2, "L"))):
        aim = sgn * d * np.cos(tl) + np.array([0.0, np.sin(tl) * (1.0 if j == 0 else -1.0), 0.0])

        def at(t, aim=aim, j=j):
            u = bm.smoother((t - t0) / max(approach, 1e-3))
            gap = 0.5 * apart * (1.0 - u)
            drift = np.array([0.0, 0.010 * bm.wobble(t, 3.0 + j, 0.9), 0.010 * bm.wobble(t, 5.0 + j, 0.7)]) * (1.0 - u)
            return meet - aim * gap + drift

        fxs = [dict(kind="shed", n=5000, life=2.4, where=[looks.HAND], dir=-aim, speed=0.5, rise=0.03, turb=0.22,
                    spread=0.05)] if shed else []
        light = _col(col)
        out[name] = Body(shapes[j], part="arm." + side, look=look, color=col, color2=light * 0.55 + 0.45, points=points,
                         effects=fxs, bright=bright, seed=seed + j,
                         hand=dict(side=side, at=at, aim=aim, palm=(0.0, 1.0, 0.0) if j == 0 else (0.0, -1.0, 0.0),
                                   pose=poses[j], anchor="fingertips"))
    if flare:
        out["flare"] = fx.Flare(meet, t_touch, color=color, color2=color2, scale=flare)
    return out
