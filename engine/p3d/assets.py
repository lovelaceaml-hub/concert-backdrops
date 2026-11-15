"""The human form behind the particle bodies: the baked mesh, its skeleton, skinning and surface sampling.

The asset is assets/p3d/body_v1.npz (see assets/p3d/README.md for what it is, where it comes from and its
licences: the MakeHuman hm08 base mesh, CC0, and motion clips from the CMU motion capture database). It is built by
tools/build_p3d_body.py and tools/build_p3d_motion.py; nothing is downloaded at render time.

Conventions (the same as engine/p3d/api.py): metres, y up, the body stands with its soles on y = 0 and, at
facing 0, looks toward +z; the body's own left is +x.

The neutral pose: the mesh is modelled with the arms held out at an angle. All poses here are written against
a NEUTRAL pose instead (standing straight, legs vertical, arms hanging straight down), which is also the rest
pose of the motion clips. In the neutral pose every joint frame is aligned with the world axes, so a local
rotation about x is always "bend forward or back", about z "tilt left or right", about y "twist".
"""
import os

import numpy as np

from . import bodymath as bm

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "p3d", "body_v1.npz")
_CACHE = {}

SHAPES = ("woman", "man", "child")

# the body regions a point can belong to (by the bone that moves it most)
REGIONS = ("head", "neck", "torso", "arm", "forearm", "hand", "hips", "leg", "shin", "foot")


def _region_of(bone):
    b = bone.split(".")[0]
    if b == "head":
        return "head"
    if b.startswith("neck"):
        return "neck"
    if b.startswith(("spine", "clavicle", "shoulder")):
        return "torso"
    if b.startswith("upperarm"):
        return "arm"
    if b.startswith("lowerarm"):
        return "forearm"
    if b.startswith(("wrist", "finger", "metacarpal")):
        return "hand"
    if b.startswith(("root", "pelvis")):
        return "hips"
    if b.startswith("upperleg"):
        return "leg"
    if b.startswith("lowerleg"):
        return "shin"
    if b.startswith("foot"):
        return "foot"
    return "torso"


def load(path=None):
    """The arrays of the baked asset (cached)."""
    p = os.path.abspath(path or os.environ.get("P3D_BODY_ASSET", _PATH))
    if p not in _CACHE:
        if not os.path.exists(p):
            raise FileNotFoundError(
                "The particle bodies need %s. It is committed with the engine; if it is missing, rebuild it "
                "with: python tools/build_p3d_body.py" % p)
        with np.load(p, allow_pickle=False) as d:
            _CACHE[p] = {k: d[k] for k in d.files}
    return _CACHE[p]


class Rig:
    """One body shape with its skeleton: neutral pose, forward kinematics, skinning.

    shape    "woman", "man" or "child"
    height   metres (default: the shape's own height, about 1.59, 1.73 and 1.31)
    build    1 as modelled; above 1 heavier (1.15: broad), below 1 slighter (0.88: slight)
    """

    def __init__(self, shape="woman", height=None, build=1.0):
        if shape not in SHAPES:
            raise ValueError("shape must be one of %s, got %r" % (SHAPES, shape))
        d = load()
        v = d["verts_" + shape].astype(np.float64)
        native = float(v[:, 1].max())
        s = 1.0 if height is None else float(height) / native
        self.shape = shape
        self.scale = s
        self.height = native * s
        self.verts0 = (v * s).astype(np.float32)
        self.head = d["head_" + shape].astype(np.float64) * s
        self.tail = d["tail_" + shape].astype(np.float64) * s
        self.names = [str(n) for n in d["bone_names"]]
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.parent = d["bone_parent"].astype(np.int64)
        self.nb = len(self.names)
        self.tris = d["tris"].astype(np.int64)
        self.w_idx = d["w_idx"].astype(np.int64)
        self.w_val = d["w_val"].astype(np.float32)
        self.face_weight = d["face_weight"].astype(np.float32)
        self.offset = np.zeros((self.nb, 3))
        for b in range(self.nb):
            p = self.parent[b]
            self.offset[b] = self.head[b] - (self.head[p] if p >= 0 else 0.0)
        self.vert_bone = self.w_idx[:, 0]
        self.bone_region = np.array([REGIONS.index(_region_of(n)) for n in self.names])
        self.side = np.array([1 if n.endswith(".L") else (-1 if n.endswith(".R") else 0) for n in self.names])
        self.build = float(build)
        if abs(self.build - 1.0) > 1e-4:
            self._inflate(self.build)
        self._neutral()
        self._levels()
        self.normals0 = self._vertex_normals(self.verts0)
        self._measure()

    def _inflate(self, b):
        """A heavier (b > 1) or slighter (b < 1) build: the flesh moves away from (or toward) the axis of each
        bone it is weighted to, most on the trunk and thighs, little on the head, hands and feet; blended by
        the skin weights, so there is no seam at the joints."""
        gain = dict(head=0.15, neck=0.6, torso=1.0, arm=0.85, forearm=0.65, hand=0.25, hips=1.0, leg=0.9,
                    shin=0.55, foot=0.12)
        g_bone = np.array([gain[REGIONS[r]] for r in self.bone_region])
        v = self.verts0.astype(np.float64)
        out = np.zeros_like(v)
        wsum = np.zeros(len(v))
        for j in range(self.w_idx.shape[1]):
            bj = self.w_idx[:, j]
            wj = self.w_val[:, j].astype(np.float64)
            h, ax = self.head[bj], self.tail[bj] - self.head[bj]
            u = np.clip(((v - h) * ax).sum(1) / np.maximum((ax * ax).sum(1), 1e-12), 0.0, 1.0)
            c = h + ax * u[:, None]
            f = 1.0 + (b - 1.0) * g_bone[bj]
            out += wj[:, None] * (c + (v - c) * f[:, None])
            wsum += wj
        self.verts0 = (out / np.maximum(wsum, 1e-9)[:, None]).astype(np.float32)

    # ------------------------------------------------------------------ neutral pose
    def _neutral(self):
        i = self.idx
        down = np.array([0.0, -1.0, 0.0])
        aims = {}
        for s in ("L", "R"):
            aims["upperleg01." + s] = (i["lowerleg01." + s], down)
            aims["lowerleg01." + s] = (i["foot." + s], down)
            aims["upperarm01." + s] = (i["lowerarm01." + s], down)
            aims["lowerarm01." + s] = (i["wrist." + s], down)
        C = np.tile(bm.IDENT, (self.nb, 1))
        for b in range(self.nb):
            p = self.parent[b]
            cp = C[p] if p >= 0 else bm.IDENT
            n = self.names[b]
            if n in aims:
                end, want = aims[n]
                d = bm.qrot(cp, self.head[end] - self.head[b])
                C[b] = bm.qn(bm.qmul(bm.qbetween(d, want), cp))
            elif n.startswith("foot."):
                C[b] = bm.IDENT          # the sole stays flat on the ground
            else:
                C[b] = cp
        # hands: the smallest rotation leaves the palms turned a little outward; turn each forearm about its
        # own (now vertical) axis so the palm faces the thigh, as a hanging arm does
        self.palm_twist = {}
        self.palm_n = {}
        for s, sg in (("L", 1.0), ("R", -1.0)):
            w = i["wrist." + s]
            e1 = self.tail[i["metacarpal1." + s]] - self.head[w]
            e2 = self.tail[i["metacarpal4." + s]] - self.head[w]
            out = np.cross(e1, e2) * -sg                 # out of the palm, in the modelled rest pose
            n = bm.qrot(C[w], out / np.linalg.norm(out))
            now = np.arctan2(n[0], n[2])                 # azimuth of the palm normal (from +z toward +x)
            want = -sg * np.radians(100.0)               # facing the thigh, a little to the back
            th = (want - now + np.pi) % (2 * np.pi) - np.pi
            self.palm_twist[s] = float(th)
            self.palm_n[s] = bm.qrot(bm.qy(th), n)       # palm normal in the neutral pose
            for b in range(self.nb):
                nm = self.names[b]
                if not nm.endswith("." + s):
                    continue
                if nm.startswith("upperarm02"):
                    f = 0.25
                elif nm.startswith("lowerarm01"):
                    f = 0.6
                elif nm.startswith(("lowerarm02", "wrist", "finger", "metacarpal")):
                    f = 1.0
                else:
                    continue
                C[b] = bm.qn(bm.qmul(bm.qy(th * f), C[b]))
        self.C = C
        # joint positions and bone directions in the neutral pose
        P = np.zeros((self.nb, 3))
        for b in range(self.nb):
            p = self.parent[b]
            P[b] = self.head[b] if p < 0 else P[p] + bm.qrot(C[p], self.offset[b])
        self.neutral_pos = P
        self.neutral_dir = bm.qrot(C, self.tail - self.head)
        self.neutral_dir /= np.maximum(np.linalg.norm(self.neutral_dir, axis=1, keepdims=True), 1e-9)

    def _levels(self):
        depth = np.zeros(self.nb, np.int64)
        for b in range(self.nb):
            if self.parent[b] >= 0:
                depth[b] = depth[self.parent[b]] + 1
        self.levels = [np.where(depth == k)[0] for k in range(depth.max() + 1)]

    def _measure(self):
        i = self.idx
        P = self.neutral_pos
        self.leg_len = float(P[i["upperleg01.L"]][1] - P[i["foot.L"]][1])
        self.hip_height = float(P[i["upperleg01.L"]][1])
        self.root_height = float(P[i["root"]][1])
        self.shoulder_height = float(P[i["upperarm01.L"]][1])
        self.head_centre = self.head[i["head"]] + np.array([0.0, 0.085, 0.0]) * self.height / 1.6
        # ground probes: the lowest points of each foot, and the knees and toes (for kneeling)
        probes = []
        for s in ("L", "R"):
            f = i["foot." + s]
            sel = np.where(self.vert_bone == f)[0]
            vv = self.verts0[sel]
            low = sel[np.argsort(vv[:, 1])[:40]]
            for k in low[::4]:
                probes.append((f, self.verts0[k].astype(np.float64)))
            kn = i["lowerleg01." + s]
            sel = np.where((self.vert_bone == kn) | (self.vert_bone == i["upperleg02." + s]))[0]
            vv = self.verts0[sel]
            near = sel[np.abs(vv[:, 1] - self.head[kn][1]) < 0.05 * self.height / 1.6]
            vv = self.verts0[near]
            front = near[np.argsort(-vv[:, 2])[:6]]
            for k in front:
                probes.append((int(self.vert_bone[k]), self.verts0[k].astype(np.float64)))
        self.probe_bone = np.array([p[0] for p in probes])
        self.probe_pos = np.array([p[1] for p in probes])

    # ------------------------------------------------------------------ kinematics
    def fk(self, q, root_pos=None, root_rot=None):
        """Poses the skeleton. q: (bones, 4) local rotations in the neutral frames; root_pos: where the root
        joint is (default: its neutral place); root_rot: a rotation of the whole body about the root joint.
        Returns (D, P, A): the world rotation of every bone relative to the modelled rest pose, the joint
        positions, and the world rotation of every bone relative to the neutral pose."""
        A = np.empty((self.nb, 4))
        D = np.empty((self.nb, 4))
        P = np.empty((self.nb, 3))
        r = self.levels[0]
        A[r] = q[r] if root_rot is None else bm.qmul(np.asarray(root_rot, np.float64)[None], q[r])
        D[r] = bm.qmul(A[r], self.C[r])
        P[r] = self.neutral_pos[r] if root_pos is None else np.asarray(root_pos, np.float64)[None]
        for lv in self.levels[1:]:
            p = self.parent[lv]
            A[lv] = bm.qmul(A[p], q[lv])
            D[lv] = bm.qmul(A[lv], self.C[lv])
            P[lv] = P[p] + bm.qrot(D[p], self.offset[lv])
        return D, P, A

    def matrices(self, D, P):
        """(bones, 3, 4) matrices that carry rest-pose points of each bone into the pose."""
        R = bm.qmat(D)
        T = P - np.einsum("bij,bj->bi", R, self.head)
        return np.concatenate([R, T[:, :, None]], axis=2).astype(np.float32)

    def skin(self, M, with_normals=False):
        """The posed mesh vertices (and unit normals) from bone matrices."""
        Mv = np.einsum("vk,vkij->vij", self.w_val, M[self.w_idx])
        v = np.einsum("vij,vj->vi", Mv[:, :, :3], self.verts0) + Mv[:, :, 3]
        if not with_normals:
            return v
        n = np.einsum("vij,vj->vi", Mv[:, :, :3], self.normals0)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        return v, n

    def carry(self, M, bones, pts):
        """Rest-pose points rigidly attached to given bones, in the pose."""
        m = M[bones]
        return np.einsum("nij,nj->ni", m[:, :, :3], pts) + m[:, :, 3]

    def lowest(self, M):
        """Height of the lowest ground probe (soles, knees) in the pose."""
        return float(self.carry(M, self.probe_bone, self.probe_pos.astype(np.float32))[:, 1].min())

    def _vertex_normals(self, v):
        t = self.tris
        fn = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
        n = np.zeros_like(v)
        for k in range(3):
            np.add.at(n, t[:, k], fn)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        return n.astype(np.float32)


class Surface:
    """Points fixed on the mesh surface (triangle and barycentric coordinates), evenly spread by area.

    n         how many points
    density   optional dict region -> multiplier (for example dict(head=2.0, hand=3.0) for close-ups)
    keep      optional list of regions to keep (others get no points)
    weight    optional function of the triangle centres (F, 3) in the modelled pose that gives a multiplier
              per triangle (0 leaves a place empty)
    """

    def __init__(self, rig, n=60000, density=None, keep=None, salt=0, weight=None):
        t = rig.tris
        v = rig.verts0.astype(np.float64)
        area = 0.5 * np.linalg.norm(np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]), axis=1)
        tri_bone = rig.vert_bone[t[:, 0]]
        tri_region = rig.bone_region[tri_bone]
        w = area.copy()
        if density:
            for name, mult in density.items():
                w[tri_region == REGIONS.index(name)] *= float(mult)
        if keep is not None:
            ok = np.isin(tri_region, [REGIONS.index(k) for k in keep])
            w[~ok] = 0.0
        if weight is not None:
            w = w * np.asarray(weight((v[t[:, 0]] + v[t[:, 1]] + v[t[:, 2]]) / 3.0), np.float64)
        self.area = float(w.sum())
        cdf = np.cumsum(w)
        total = cdf[-1]
        # stratified over the area: even spacing, no clumps
        u = (np.arange(n) + bm.rand(n, 11 + salt)) / n * total
        tri = np.minimum(np.searchsorted(cdf, u), len(t) - 1)
        r1 = np.sqrt(bm.rand(n, 12 + salt))
        r2 = bm.rand(n, 13 + salt)
        bary = np.stack([1.0 - r1, r1 * (1.0 - r2), r1 * r2], axis=1).astype(np.float32)
        # shuffle so that any leading share of the points is itself an even sample
        order = np.argsort(bm.rand(n, 14 + salt), kind="stable")
        self.rig = rig
        self.n = n
        self.tri = tri[order]
        self.bary = bary[order]
        self.vi = t[self.tri]
        self.bone = tri_bone[self.tri]
        self.region = tri_region[self.tri]
        self.side = rig.side[self.bone]
        self.seed = bm.rand(n, 15 + salt).astype(np.float32)
        self.face = (rig.face_weight[self.vi] * self.bary).sum(1)
        self.rest = self.at(rig.verts0)
        self.rest_normal = self.at(rig.normals0)

    def at(self, verts):
        """The points for given mesh vertices (positions or normals)."""
        return (verts[self.vi] * self.bary[:, :, None]).sum(1)
