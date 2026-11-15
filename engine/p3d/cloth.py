"""Garments of light: cloth simulated on the particle bodies (engine/p3d/body.py).

A garment piece is a grid of cloth particles (a tube for a skirt or a sleeve, a sheet for a veil, chains for
hair). Its top edge is pinned to the body and follows the skin; the rest hangs, swings and folds under
gravity, air and wind, and is pushed out of the body (capsules along the bones) and off the ground.

Deterministic and independent of which frames are asked for: the simulation always starts at the body's own
start time and advances in fixed steps of 1/120 s; snapshots are kept at 1/30 s and any time is read by
interpolation. Asking for a later time simulates up to it once; asking in any order gives the same answer.
"""
import numpy as np

from . import bodymath as bm

DT = 1.0 / 120.0
SNAP = 4                     # steps per snapshot (30 per second)
PREROLL = 1.5                # seconds simulated before the start so the cloth has settled


# ---------------------------------------------------------------------------------------------------------
# what the cloth collides with: the body as capsules
# ---------------------------------------------------------------------------------------------------------
class Colliders:
    """Capsules fixed to bones: each from point a to point b with radius ra at a and rb at b."""

    def __init__(self, rig):
        self.rig = rig
        i = rig.idx
        v = rig.verts0.astype(np.float64)
        k = rig.height / 1.6
        caps = []          # (bone a, rest point a, bone b, rest point b, ra, rb)
        groups = []        # which part of the body each capsule is ("leg", "arm", "foot", "hand", "torso", ...)

        def limb(b0, b1, b_end, scale=1.0, extra=0.0):
            """Capsule along a limb from the head of bone b0 to the head of b_end; radius from the skin."""
            a, b = rig.head[i[b0]], rig.head[i[b_end]]
            sel = np.isin(rig.vert_bone, [i[x] for x in b1])
            p = v[sel]
            ab = b - a
            t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
            d = np.linalg.norm(p - (a + t[:, None] * ab), axis=1)
            lo = d[t < 0.5]
            hi = d[t >= 0.5]
            ra = float(np.percentile(lo, 80)) if len(lo) else 0.04 * k
            rb = float(np.percentile(hi, 80)) if len(hi) else 0.04 * k
            caps.append((i[b0], a, i[b_end] if b_end in ("wrist.L", "wrist.R") else i[b1[-1]], b, ra * scale + extra,
                         rb * scale + extra))
            groups.append("leg" if "leg" in b0 else "arm." + b0[-1])

        for s in ("L", "R"):
            limb("upperleg01." + s, ["upperleg01." + s, "upperleg02." + s], "lowerleg01." + s)
            limb("lowerleg01." + s, ["lowerleg01." + s, "lowerleg02." + s], "foot." + s)
            limb("upperarm01." + s, ["upperarm01." + s, "upperarm02." + s], "lowerarm01." + s)
            limb("lowerarm01." + s, ["lowerarm01." + s, "lowerarm02." + s], "wrist." + s)
            # foot: ankle to the tip of the toes
            f = i["foot." + s]
            sel = rig.vert_bone == f
            tip = v[sel][np.argmax(v[sel][:, 2])]
            caps.append((f, rig.head[f] + np.array([0, -0.02, 0.0]) * k, f, tip + np.array([0, 0.012, -0.03]) * k,
                         0.045 * k, 0.03 * k))
            groups.append("foot")
            # hand
            w = i["wrist." + s]
            caps.append((w, rig.head[w], w, rig.head[i["finger3-1." + s]], 0.032 * k, 0.03 * k))
            groups.append("hand")
        # torso: flat capsules across the body at several heights (an oval cross-section each)
        torso = np.isin(rig.bone_region[rig.vert_bone], [2, 6])        # torso, hips
        hip_y = rig.head[i["upperleg01.L"]][1]
        sh_y = rig.head[i["upperarm01.L"]][1]
        for f in np.linspace(-0.06, 1.0, 9):
            y = hip_y + (sh_y - hip_y) * f
            sel = torso & (np.abs(v[:, 1] - y) < 0.03 * k)
            if sel.sum() < 12:
                continue
            p = v[sel]
            zc = 0.5 * (p[:, 2].max() + p[:, 2].min())
            r = 0.5 * (p[:, 2].max() - p[:, 2].min())
            hx = np.percentile(np.abs(p[:, 0]), 96)
            hx = max(hx - r, 0.005)
            bone = int(np.bincount(rig.vert_bone[sel]).argmax())
            caps.append((bone, np.array([-hx, y, zc]), bone, np.array([hx, y, zc]), r, r))
            groups.append("hips" if f < 0.4 else "chest")
        # neck and head
        n1, hd = i["neck01"], i["head"]
        caps.append((n1, rig.head[n1], hd, rig.head[hd], 0.052 * k, 0.05 * k))
        groups.append("neck")
        hc = rig.head_centre
        caps.append((hd, hc + np.array([0, -0.035, 0.02]) * k, hd, hc + np.array([0, 0.03, -0.012]) * k,
                     0.083 * k, 0.092 * k))
        groups.append("head")
        self.groups = groups
        # for the bell of a skirt: from the middle of the hips ...
        sel = torso & (np.abs(v[:, 1] - hip_y) < 0.03 * k)
        self.hip_centre = np.array([0.0, hip_y + 0.03 * k, 0.5 * (v[sel][:, 2].max() + v[sel][:, 2].min())], np.float32)
        self.hip_depth = 0.5 * float(v[sel][:, 2].max() - v[sel][:, 2].min())
        self.root = i["root"]
        self.ankles = (i["foot.L"], i["foot.R"])
        self.bone_a = np.array([c[0] for c in caps])
        self.bone_b = np.array([c[2] for c in caps])
        self.pa = np.array([c[1] for c in caps], np.float32)
        self.pb = np.array([c[3] for c in caps], np.float32)
        self.ra = np.array([c[4] for c in caps])
        self.rb = np.array([c[5] for c in caps])

    def at(self, M):
        """The capsules in the world for bone matrices M: (a, b)."""
        return (self.rig.carry(M, self.bone_a, self.pa).astype(np.float64),
                self.rig.carry(M, self.bone_b, self.pb).astype(np.float64))


def _skin_bind(rig, pts):
    """Skinning weights for free points: those of the nearest mesh vertex."""
    v = rig.verts0.astype(np.float64)
    idx = np.empty(len(pts), np.int64)
    for k in range(0, len(pts), 256):
        d = ((pts[k:k + 256, None, :] - v[None, :, :]) ** 2).sum(-1)
        idx[k:k + 256] = d.argmin(1)
    return rig.w_idx[idx], rig.w_val[idx]


def _ring(rig, y, n, regions, margin, arc=(0.0, 2 * np.pi)):
    """n points around the body at height y in the modelled pose: the outline of the body there, pushed out
    by margin. arc: (start, end) angles, measured from +z (front) toward +x. Returns (points, centre)."""
    v = rig.verts0.astype(np.float64)
    k = rig.height / 1.6
    sel = np.isin(rig.bone_region[rig.vert_bone], regions) & (np.abs(v[:, 1] - y) < 0.022 * k)
    p = v[sel]
    c = np.array([0.0, y, 0.5 * (p[:, 2].max() + p[:, 2].min())])
    ang = np.arctan2(p[:, 0] - c[0], p[:, 2] - c[2])
    rad = np.hypot(p[:, 0] - c[0], p[:, 2] - c[2])
    closed = abs((arc[1] - arc[0]) - 2 * np.pi) < 1e-6
    th = arc[0] + (arc[1] - arc[0]) * (np.arange(n) / (n if closed else n - 1))
    out = np.zeros((n, 3))
    for j, a in enumerate(th):
        d = np.abs((ang - a + np.pi) % (2 * np.pi) - np.pi)
        near = d < (2.2 * np.pi / 48)
        r = rad[near].max() if near.any() else rad[np.argmin(d)]
        out[j] = c + (r + margin) * np.array([np.sin(a), 0.0, np.cos(a)])
    # smooth the radius a little around the ring
    r = np.hypot(out[:, 0] - c[0], out[:, 2] - c[2])
    if closed:
        r = (np.roll(r, 1) + 2 * r + np.roll(r, -1)) / 4
    else:
        r[1:-1] = (r[:-2] + 2 * r[1:-1] + r[2:]) / 4
    out[:, 0] = c[0] + r * np.sin(th)
    out[:, 2] = c[2] + r * np.cos(th)
    return out, c


# ---------------------------------------------------------------------------------------------------------
# pieces
# ---------------------------------------------------------------------------------------------------------
class Piece:
    """One garment piece as a grid of rows x cols particles in the modelled pose (rest shape), with its pins."""

    def __init__(self, name, rest, closed, pin_rows=1, init_bone=None, stiff=1.0, bend=0.08, air=1.4, weight=1.0,
                 collide=("leg", "foot", "hips"), bell=0.0, strands=False):
        self.name = name
        self.rest = np.asarray(rest, np.float64)          # (rows, cols, 3)
        self.rows, self.cols = self.rest.shape[:2]
        self.closed = closed
        self.pin_rows = pin_rows
        self.init_bone = init_bone                         # (rows, cols) bone that carries each particle at the start
        self.stiff = stiff
        self.bend = bend
        self.air = air                                     # how strongly the air carries the cloth (1/s)
        self.weight = weight
        self.collide = tuple(collide)                      # which body parts push this piece out
        self.bell = bell                                   # skirts: radius of the bell at the hem (0: none)
        self.strands = strands


def skirt(rig, top=0.625, hem=0.035, flare=1.7, cols=48, rows=28, margin=0.012, name="skirt", open_front=False,
          air=1.3, bell=0.55):
    """A skirt as a tube from a ring around the body at height `top` (a share of the body height) down to
    `hem` (metres above the ground, for a 1.6 m body). flare: how many times wider the hem is than the waist
    (more: more folds). bell: how full the skirt stands (0: it falls onto the legs; 0.55: an A-line)."""
    H = rig.height
    k = H / 1.6
    y0 = top * H
    arc = (np.radians(14.0), np.radians(346.0)) if open_front else (0.0, 2 * np.pi)
    ring, c = _ring(rig, y0, cols, [2, 6], margin * k, arc)
    hip, _ = _ring(rig, rig.head[rig.idx["upperleg01.L"]][1] + 0.01 * k, cols, [2, 6, 7], (margin + 0.012) * k, arc)
    y_hip = hip[0, 1]
    ys = np.linspace(y0, hem * k, rows)
    rest = np.zeros((rows, cols, 3))
    r_w = np.hypot(ring[:, 0] - c[0], ring[:, 2] - c[2])
    r_h = np.maximum(np.hypot(hip[:, 0] - c[0], hip[:, 2] - c[2]), r_w)
    th = np.arctan2(ring[:, 0] - c[0], ring[:, 2] - c[2])
    r_hem = max(flare * r_w.mean(), r_h.mean() * 1.05)
    for r in range(rows):
        y = ys[r]
        if y >= y_hip:
            u = (y0 - y) / max(y0 - y_hip, 1e-6)
            rad = r_w + (r_h - r_w) * bm.smooth(u)
        else:
            u = (y_hip - y) / max(y_hip - hem * k, 1e-6)
            rad = r_h + (r_hem - r_h.mean()) * u ** 0.9 * (r_h / r_h.mean())
        rest[r, :, 0] = c[0] + rad * np.sin(th)
        rest[r, :, 1] = y
        rest[r, :, 2] = c[2] + rad * np.cos(th)
    init = np.full((rows, cols), rig.idx["root"])
    return Piece(name, rest, closed=not open_front, pin_rows=1, init_bone=init, air=air,
                 collide=("leg", "foot", "hips"), bell=bell * r_hem)


def sleeve(rig, side, length=1.02, wide=2.4, cols=18, rows=18, start=0.12, name=None):
    """A wide sleeve as a tube along the arm from just below the shoulder to the wrist. wide: how many times
    wider the opening at the wrist is than the arm."""
    i = rig.idx
    k = rig.height / 1.6
    a = rig.head[i["upperarm01." + side]]
    e = rig.head[i["lowerarm01." + side]]
    w = rig.head[i["wrist." + side]]
    L1 = np.linalg.norm(e - a)
    L2 = np.linalg.norm(w - e)
    total = (L1 + L2) * length
    s0 = start * L1
    ss = np.linspace(s0, total, rows)
    rest = np.zeros((rows, cols, 3))
    init = np.zeros((rows, cols), np.int64)
    up = np.array([0.0, 1.0, 0.0])
    for r, s in enumerate(ss):
        if s <= L1:
            p = a + (e - a) * (s / L1)
            ax = (e - a) / L1
            bone = i["upperarm01." + side] if s < 0.4 * L1 else i["upperarm02." + side]
        else:
            ax = (w - e) / L2
            p = e + ax * (s - L1)
            bone = i["lowerarm01." + side] if s < L1 + 0.5 * L2 else i["lowerarm02." + side]
        u = (s - s0) / (total - s0)
        rad = (0.058 + 0.004 * (1 - u)) * k * (1.0 + (wide - 1.0) * u ** 1.4)
        n1 = np.cross(ax, up)
        n1 /= np.linalg.norm(n1)
        n2 = np.cross(ax, n1)
        th = 2 * np.pi * np.arange(cols) / cols
        rest[r] = p + rad * (np.cos(th)[:, None] * n1 + np.sin(th)[:, None] * n2)
        init[r] = bone
    return Piece(name or ("sleeve." + side), rest, closed=True, pin_rows=2, init_bone=init, bend=0.05, air=1.8,
                 collide=("arm." + side, "chest", "hips", "leg"))


def veil(rig, length=1.0, cols=40, rows=34, arc=250.0, margin=0.012, name="veil", wide=1.0):
    """A veil hanging from a circlet around the crown of the head, open at the face, falling over the
    shoulders and down the back. length: metres from the crown (for a 1.6 m body); arc: degrees of the circlet
    that carry cloth (the rest is the open front); wide: how full it is."""
    i = rig.idx
    k = rig.height / 1.6
    hc = rig.head_centre
    y0 = hc[1] + 0.022 * k
    half = np.radians(arc) * 0.5
    ring, c = _ring(rig, y0, cols, [0], margin * k, (np.pi - half, np.pi + half))
    th = np.arctan2(ring[:, 0] - c[0], ring[:, 2] - c[2])
    th = np.where(th < 0, th + 2 * np.pi, th)
    r0 = np.hypot(ring[:, 0] - c[0], ring[:, 2] - c[2])
    sh = abs(rig.head[i["upperarm01.L"]][0]) + 0.05 * k        # half the shoulder width
    y_sh = rig.head[i["upperarm01.L"]][1]
    rest = np.zeros((rows, cols, 3))
    vs = np.linspace(0.0, length * k, rows)
    cz = 0.5 * (c[2] + rig.head[i["spine01"]][2])
    for r, vdist in enumerate(vs):
        y = y0 - vdist
        u = float(np.clip((y0 - y) / max(y0 - y_sh, 1e-6), 0.0, 1.0))
        low = max(y_sh - y, 0.0) / max(length * k - (y0 - y_sh), 1e-6)
        rx = r0 + (sh * 1.12 * wide - r0) * bm.smooth(u) + 0.10 * k * wide * low
        rz = r0 + (sh * 0.80 * wide - r0) * bm.smooth(u) + 0.08 * k * wide * low
        zc = c[2] + (cz - c[2]) * bm.smooth(u)
        rest[r, :, 0] = c[0] + rx * np.sin(th)
        rest[r, :, 1] = y
        rest[r, :, 2] = zc + rz * np.cos(th)
    init = np.full((rows, cols), i["head"])
    init[vs > 0.2 * k] = i["spine01"]
    return Piece(name, rest, closed=False, pin_rows=1, init_bone=init, bend=0.04, air=2.6, weight=0.9,
                 collide=("head", "neck", "chest", "arm.L", "arm.R"))


def hair(rig, length=0.42, strands=150, seg=14, name="hair", salt=0):
    """Long hair as chains from the scalp (the back and sides of the head). length: metres (for a 1.6 m body)."""
    i = rig.idx
    k = rig.height / 1.6
    hc = rig.head_centre
    v = rig.verts0.astype(np.float64)
    hb = i["head"]
    sel = np.where((rig.vert_bone == hb) & (v[:, 1] > hc[1] - 0.045 * k)
                   & ((v[:, 2] < hc[2] + 0.035 * k) | (v[:, 1] > hc[1] + 0.07 * k)))[0]
    pick = sel[np.argsort(bm.hashf(sel, 71 + salt), kind="stable")[:strands]]
    roots = v[pick]
    n = rig.normals0[pick].astype(np.float64)
    rest = np.zeros((seg, len(pick), 3))
    ln = length * k * (0.75 + 0.5 * bm.hashf(pick, 72 + salt))
    for q in range(seg):
        u = q / (seg - 1)
        out = n * (0.012 * k + 0.05 * k * np.sin(np.pi * min(u * 2.5, 1.0) * 0.5))
        out[:, 1] *= 0.3
        rest[q] = roots + out + np.array([0.0, -1.0, 0.0]) * (ln * u)[:, None] + np.array([0.0, 0.0, -0.03 * k]) * u
    init = np.full((seg, len(pick)), hb)
    return Piece(name, rest, closed=False, pin_rows=1, init_bone=init, bend=0.3, air=1.6, weight=1.0,
                 collide=("head", "neck", "chest", "arm.L", "arm.R"), strands=True)


# ---------------------------------------------------------------------------------------------------------
# the simulation
# ---------------------------------------------------------------------------------------------------------
class ClothSystem:
    """All cloth pieces of one body, simulated together.

    actor     the engine/p3d/actor.py Actor that wears them
    pieces    list of Piece
    t_start   when the simulation starts (the body's own start); the cloth is settled by then
    wind      (x, y, z) metres per second, a steady wind in the world; gust: how much it swells and eddies
    """

    def __init__(self, actor, pieces, t_start=0.0, wind=(0.0, 0.0, 0.0), gust=0.35, seed=1.0, ground=None):
        from scipy import sparse
        self.actor = actor
        self.rig = actor.rig
        self.pieces = pieces
        self.t_start = float(t_start)
        self.wind = np.asarray(wind, np.float64)
        self.gust = float(gust)
        self.seed = float(seed)
        self.ground = ground
        self.col = Colliders(self.rig)
        rig = self.rig
        rest, pinned, init_bone, weight, air = [], [], [], [], []
        hard = {}      # colour -> list of (i, j): solved one colour at a time (no particle twice in a colour)
        soft = []      # (i, j, stiffness): solved together, averaged
        self.slices = {}
        lra = []
        off = 0
        for pc in pieces:
            R, C = pc.rows, pc.cols
            idx = off + np.arange(R * C).reshape(R, C)
            self.slices[pc.name] = (off, R, C)
            rest.append(pc.rest.reshape(-1, 3))
            pm = np.zeros((R, C), bool)
            pm[:pc.pin_rows] = True
            pinned.append(pm.reshape(-1))
            init_bone.append(pc.init_bone.reshape(-1))
            weight.append(np.full(R * C, pc.weight))
            air.append(np.full(R * C, pc.air))

            def add_hard(colour, a, b):
                hard.setdefault(colour, []).append(np.stack([a.reshape(-1), b.reshape(-1)], 1))

            def add_soft(a, b, k):
                a = a.reshape(-1)
                soft.append(np.stack([a, b.reshape(-1), np.full(len(a), k)], 1))

            n0 = len(idx[0:-1:2])
            add_hard("v0", idx[0:-1:2], idx[1::2][:n0])                                   # down the rows
            n1 = len(idx[1:-1:2])
            if n1:
                add_hard("v1", idx[1:-1:2], idx[2::2][:n1])
            cc = np.arange(C)
            if not pc.strands:
                nxt = (cc + 1) % C if pc.closed else cc + 1
                ok = np.ones(C, bool) if pc.closed else cc < C - 1
                ev = ok & (cc % 2 == 0)
                od = ok & (cc % 2 == 1)
                if pc.closed and C % 2 == 1:
                    ev[-1] = False
                    add_hard("h2", idx[:, [C - 1]], idx[:, [0]])
                add_hard("h0", idx[:, cc[ev]], idx[:, nxt[ev]])                            # around
                add_hard("h1", idx[:, cc[od]], idx[:, nxt[od]])
                rr = np.arange(R - 1)
                for sgn in (1, -1):                                                          # shear
                    c2 = (cc + sgn) % C if pc.closed else cc + sgn
                    okc = np.ones(C, bool) if pc.closed else (c2 >= 0) & (c2 < C)
                    add_soft(idx[np.ix_(rr, cc[okc])], idx[np.ix_(rr + 1, c2[okc])], pc.stiff * 0.5)
                c2 = (cc + 2) % C if pc.closed else cc + 2                                   # bend around
                okc = np.ones(C, bool) if pc.closed else c2 < C
                add_soft(idx[:, cc[okc]], idx[:, c2[okc]], pc.bend)
            if R > 2:
                add_soft(idx[:-2], idx[2:], pc.bend)                                         # bend down
            # long range attachment: each particle to the pinned particle at the top of its column
            lra.append(np.broadcast_to(idx[pc.pin_rows - 1], (R, C)).reshape(-1))
            off += R * C
        self.n = off
        self.rest = np.concatenate(rest)
        self.pinned = np.concatenate(pinned)
        self.free = ~self.pinned
        self.init_bone = np.concatenate(init_bone)
        self.weight = np.concatenate(weight)
        self.air = np.concatenate(air)[:, None]
        self.lra_anchor = np.concatenate(lra)
        # pins follow the skin
        self.pin_idx = np.where(self.pinned)[0]
        self.pin_w_idx, self.pin_w_val = _skin_bind(rig, self.rest[self.pin_idx])
        self.pin_rest = self.rest[self.pin_idx].astype(np.float32)
        # hard constraints, one batch per colour
        self.batches = []
        for colour in sorted(hard):
            ij = np.concatenate(hard[colour])
            a, b = ij[:, 0], ij[:, 1]
            L = np.linalg.norm(self.rest[a] - self.rest[b], axis=1)
            wa = self.free[a].astype(np.float64)
            wb = self.free[b].astype(np.float64)
            ws = wa + wb
            keep = ws > 0
            self.batches.append((a[keep], b[keep], L[keep], (wa / np.maximum(ws, 1e-9))[keep, None],
                                 (wb / np.maximum(ws, 1e-9))[keep, None]))
        # soft constraints as one sparse step: move = G @ corrections
        sf = np.concatenate(soft)
        a = sf[:, 0].astype(np.int64)
        b = sf[:, 1].astype(np.int64)
        kk = sf[:, 2]
        keep = self.free[a] | self.free[b]
        a, b, kk = a[keep], b[keep], kk[keep]
        self.sa, self.sb = a, b
        self.sL = np.linalg.norm(self.rest[a] - self.rest[b], axis=1)
        wa = self.free[a].astype(np.float64)
        wb = self.free[b].astype(np.float64)
        ws = np.maximum(wa + wb, 1e-9)
        cnt = np.bincount(np.concatenate([a, b]), minlength=self.n).astype(np.float64)
        cnt = np.maximum(cnt, 1.0)
        m = len(a)
        rows_ = np.concatenate([a, b])
        cols_ = np.concatenate([np.arange(m), np.arange(m)])
        vals = np.concatenate([kk * wa / ws * 2.0 / cnt[a], -kk * wb / ws * 2.0 / cnt[b]])
        self.G = sparse.csr_matrix((vals, (rows_, cols_)), shape=(self.n, m))
        # rest distance to the anchor, measured down the column (the cloth cannot stretch past it)
        d = np.zeros(self.n)
        self.col_sets = []
        for pc in pieces:
            o, R, C = self.slices[pc.name]
            seg = np.linalg.norm(np.diff(pc.rest, axis=0), axis=2)
            cum = np.concatenate([np.zeros((1, C)), np.cumsum(seg, axis=0)])
            cum = cum - cum[pc.pin_rows - 1]
            d[o:o + R * C] = np.maximum(cum, 0.0).reshape(-1) * 1.02
            caps = np.array([j for j, g in enumerate(self.col.groups) if g in pc.collide], np.int64)
            self.col_sets.append((o, o + R * C, caps, pc.bell))
        self.lra_len = d
        self.lra_idx = np.where(self.free & (d > 0))[0]
        self.lra_anc = self.lra_anchor[self.lra_idx]
        self.lra_d = d[self.lra_idx]
        self.snaps = []          # positions every SNAP steps from t_start
        self.x = None
        self.xp = None
        self.steps = 0
        self.t0 = self.t_start - PREROLL

    # ------------------------------------------------------------------ stepping
    def _pins(self, M):
        Mv = np.einsum("vk,vkij->vij", self.pin_w_val, M[self.pin_w_idx])
        return (np.einsum("vij,vj->vi", Mv[:, :, :3], self.pin_rest) + Mv[:, :, 3]).astype(np.float64)

    def _start(self):
        M = self.actor.frame(self.t0)["M"]
        x = self.rig.carry(M, self.init_bone, self.rest.astype(np.float32)).astype(np.float64)
        x[self.pin_idx] = self._pins(M)
        self.x = x
        self.xp = x.copy()
        self.steps = 0
        self.snaps = []

    def _collide(self, xn, ca, cb, g, P, M, touched):
        ra, rb = self.col.ra, self.col.rb
        for (o0, o1, caps, bell) in self.col_sets:
            a = ca[caps]
            b = cb[caps]
            r0 = ra[caps]
            r1 = rb[caps]
            if bell > 0.0:
                # the bell of a skirt: a cone from the middle of the hips to the ground between the feet
                top = self.rig.carry(M, np.array([self.col.root]), self.col.hip_centre[None])[0].astype(np.float64)
                mid = 0.5 * (P[self.col.ankles[0]] + P[self.col.ankles[1]])
                bot = np.array([mid[0], g + bell * 0.5, mid[2]])
                a = np.concatenate([a, top[None]])
                b = np.concatenate([b, bot[None]])
                r0 = np.concatenate([r0, [self.col.hip_depth]])
                r1 = np.concatenate([r1, [bell]])
            x = xn[o0:o1]
            ab = b - a
            ab2 = np.maximum(np.einsum("kj,kj->k", ab, ab), 1e-12)
            rel = x[:, None, :] - a[None, :, :]
            tt = np.clip(np.einsum("nkj,kj->nk", rel, ab) / ab2[None], 0.0, 1.0)
            dv = rel - tt[:, :, None] * ab[None]
            dist = np.sqrt(np.einsum("nkj,nkj->nk", dv, dv))
            pen = (r0[None] + (r1 - r0)[None] * tt + 0.012) - dist
            kbest = pen.argmax(1)
            rows = np.arange(o1 - o0)
            pk = pen[rows, kbest]
            hit = (pk > 0) & self.free[o0:o1]
            if hit.any():
                h = rows[hit]
                push = dv[h, kbest[hit]] / np.maximum(dist[h, kbest[hit]], 1e-9)[:, None] * pk[hit][:, None]
                x[h] += push
                touched[o0 + h] = True

    def _body(self, t):
        """The body at a simulation time: posed at every second step, halfway in between otherwise."""
        k = int(round((t - self.t_start) / DT))
        if k % 2 == 0:
            f = self.actor.frame(self.t_start + k * DT)
            return f["M"], f["P"], f["origin"][1]
        f0 = self.actor.frame(self.t_start + (k - 1) * DT)
        f1 = self.actor.frame(self.t_start + (k + 1) * DT)
        return 0.5 * (f0["M"] + f1["M"]), 0.5 * (f0["P"] + f1["P"]), 0.5 * (f0["origin"][1] + f1["origin"][1])

    def _step(self):
        t = self.t0 + (self.steps + 1) * DT
        M, P, gy = self._body(t)
        x, xp = self.x, self.xp
        v = (x - xp) / DT
        # air: the cloth is dragged toward the speed of the air around it (a steady wind, gusts, eddies)
        wind = self.wind * (1.0 + self.gust * bm.wobble(t, self.seed + 0.5, 0.9))
        ed = bm.flow(x, t, scale=1.3, speed=0.7, seed=self.seed) * ((0.25 + 0.6 * np.linalg.norm(self.wind)) * self.gust)
        acc = (wind + ed - v) * self.air
        acc[:, 1] -= 9.81 * self.weight
        xn = x + (x - xp) * 0.996 + acc * (DT * DT)
        pins = self._pins(M)
        xn[self.pin_idx] = pins
        ca, cb = self.col.at(M)
        g = (gy if self.ground is None else self.ground) + 0.012
        touched = np.zeros(self.n, bool)
        for it in range(3):
            for a, b, L, wa, wb in self.batches:
                d = xn[b] - xn[a]
                ln = np.sqrt(np.einsum("ij,ij->i", d, d))
                c = ((ln - L) / np.maximum(ln, 1e-9))[:, None] * d
                xn[a] += c * wa
                xn[b] -= c * wb
            d = xn[self.sb] - xn[self.sa]
            ln = np.sqrt(np.einsum("ij,ij->i", d, d))
            xn += self.G @ (((ln - self.sL) / np.maximum(ln, 1e-9))[:, None] * d)
            # cannot stretch past its length from the pinned edge
            anc = xn[self.lra_anc]
            d = xn[self.lra_idx] - anc
            ln = np.sqrt(np.einsum("ij,ij->i", d, d))
            over = ln > self.lra_d
            if over.any():
                xn[self.lra_idx[over]] = anc[over] + d[over] * (self.lra_d[over] / ln[over])[:, None]
            if it == 2:
                self._collide(xn, ca, cb, g, P, M, touched)
            low = self.free & (xn[:, 1] < g)
            if low.any():
                xn[low, 1] = g
                touched |= low
            xn[self.pin_idx] = pins
        if touched.any():                     # friction: cloth that touches the body or the ground slows
            x = x.copy()
            x[touched] += (xn[touched] - x[touched]) * 0.35
        self.xp = x
        self.x = xn
        self.steps += 1

    def _ensure(self, t):
        if self.x is None:
            self._start()
            pre = int(round(PREROLL / DT))
            for _ in range(pre):
                self._step()
            self.steps = 0
            self.t0 = self.t_start
            self.snaps.append(self.x.astype(np.float32))
        need = int(np.ceil(max(t - self.t_start, 0.0) / (DT * SNAP))) + 1
        while len(self.snaps) <= need:
            for _ in range(SNAP):
                self._step()
            self.snaps.append(self.x.astype(np.float32))

    def positions(self, t):
        """All cloth particles at time t (N, 3)."""
        self._ensure(t)
        x = max(t - self.t_start, 0.0) / (DT * SNAP)
        k = min(int(x), len(self.snaps) - 2)
        f = np.float32(x - k)
        return self.snaps[k] * (1 - f) + self.snaps[k + 1] * f

    def piece(self, name, t):
        o, R, C = self.slices[name]
        return self.positions(t)[o:o + R * C].reshape(R, C, 3)


class ClothPoints:
    """Points spread evenly over a cloth piece (fixed places in the grid), for drawing."""

    def __init__(self, system, name, n, salt=0):
        pc = [p for p in system.pieces if p.name == name][0]
        self.system = system
        self.name = name
        R, C = pc.rows, pc.cols
        self.strands = pc.strands
        rest = pc.rest
        if self.strands:
            # points along each chain
            r = bm.rand(n, 31 + salt) * (R - 1)
            c = (bm.rand(n, 32 + salt) * C).astype(np.int64) % C
            self.r0 = np.minimum(r.astype(np.int64), R - 2)
            self.fr = (r - self.r0).astype(np.float32)
            self.c0 = c
            self.c1 = c
            self.fc = np.zeros(n, np.float32)
            self.u = (r / (R - 1)).astype(np.float32)
        else:
            nc = C if pc.closed else C - 1
            a = rest[:-1, :nc]
            b = rest[1:, :nc]
            cnext = (np.arange(nc) + 1) % C
            area = np.linalg.norm(np.cross(rest[:-1, cnext] - a, b - a), axis=2)        # (R-1, nc)
            cdf = np.cumsum(area.reshape(-1))
            u = (np.arange(n) + bm.rand(n, 33 + salt)) / n * cdf[-1]
            cell = np.minimum(np.searchsorted(cdf, u), len(cdf) - 1)
            self.r0 = cell // nc
            self.c0 = cell % nc
            self.c1 = cnext[self.c0]
            self.fr = bm.rand(n, 34 + salt).astype(np.float32)
            self.fc = bm.rand(n, 35 + salt).astype(np.float32)
            self.u = ((self.r0 + self.fr) / (R - 1)).astype(np.float32)
        order = np.argsort(bm.rand(n, 36 + salt), kind="stable")
        for k in ("r0", "c0", "c1", "fr", "fc", "u"):
            setattr(self, k, getattr(self, k)[order])
        self.n = n
        self.seed = bm.rand(n, 37 + salt).astype(np.float32)

    def at(self, t, with_normals=True):
        g = self.system.piece(self.name, t)
        p00 = g[self.r0, self.c0]
        p01 = g[self.r0, self.c1]
        p10 = g[self.r0 + 1, self.c0]
        p11 = g[self.r0 + 1, self.c1]
        fr = self.fr[:, None]
        fc = self.fc[:, None]
        pos = (p00 * (1 - fc) + p01 * fc) * (1 - fr) + (p10 * (1 - fc) + p11 * fc) * fr
        if not with_normals:
            return pos
        if self.strands:
            d = p10 - p00
            d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
            return pos, d            # for chains the "normal" is the direction of the strand
        n = np.cross(p01 - p00, p10 - p00)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        return pos, n
