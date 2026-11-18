"""Bakes the motion clips of the particle bodies from the CMU Graphics Lab Motion Capture Database.

    python tools/build_p3d_motion.py                 # downloads the BVH files it needs, then bakes
    python tools/build_p3d_motion.py --bvh DIR       # uses BVH files already on disk (DIR/035/35_01.bvh ...)

Source: the CMU Graphics Lab Motion Capture Database (mocap.cs.cmu.edu), in the BVH conversion by Bruce Hahne
(cgspeed, 2010 release), as mirrored at github.com/una-dinosauria/cmu-mocap. CMU: "This data is free for use
in research and commercial projects worldwide." The BVH conversion adds no restrictions. The data was
obtained from mocap.cs.cmu.edu; the database was created with funding from NSF EIA-0196217.

What it does: reads each BVH file, takes the stretch named in CLIPS, turns the whole body so that it faces +z
(and, for cycles, walks along +z), retargets every frame onto the MakeHuman skeleton of assets/p3d/body_v1.npz
by matching bone directions (twist kept from the capture), finds when each foot is planted, makes cycles loop
without a seam, and writes the clips into assets/p3d/body_v1.npz (replacing any clip there before).

Stored per clip (all float32 unless said):
  mclip_<name>_q        (frames, len(BONES), 4)  local rotations of the driven bones (engine/p3d/motion.py)
  mclip_<name>_root     (frames, 3)  the root joint relative to its neutral place, body frame, metres for the
                                     man's leg length (scaled at runtime by leg length); for cycles the steady
                                     travel is included (x, y, z)
  mclip_<name>_rot      (frames, 4)  the whole body's rotation about the root joint
  mclip_<name>_contact  (frames, 2)  0..1, how planted the left and the right foot are
  mclip_<name>_info     (5,)         fps, loop (0 or 1), leg length the root is measured for, frames,
                                     metres travelled per cycle (cycles)
"""
import argparse
import io
import os
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))

from p3d import assets, bodymath as bm  # noqa: E402

MIRROR = "https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/%03d/%s.bvh"

# name: (file, from, to (seconds of the capture, after its T-pose frame; None: the whole file), kind, notes)
#   kind "cycle": one clean cycle is found inside the stretch and looped; "once": played once;
#   ("pair", other): captured together with another subject; both share one placement
CLIPS = {
    "walk": ("35_01", None, None, "cycle", "walk (subject 35)"),
    "run": ("35_17", None, None, "cycle", "run, a light jog (subject 35)"),
    "jump": ("13_11", None, None, "once", "a forward jump from standing (subject 13)"),
    "dance": ("05_02", None, None, "once", "modern dance: expressive arms, a pirouette (subject 5)"),
    "twirl": ("05_02", 3.0, 6.2, "once", "the pirouette of the dance above, arms raised (subject 5)"),
    "pull_up": ("22_01", None, None, ("pair", "helped_up"), "pulls a sitting person up by the hands (subject 22)"),
    "helped_up": ("23_01", None, None, ("pair", "pull_up"), "sits on the ground and is pulled up (subject 23)"),
    "get_up": ("140_08", None, None, "once", "gets up from lying on the back (subject 140)"),
}

# the MakeHuman bones the clips drive (engine/p3d/motion.py reads this list from the asset)
BONES = ("spine05", "spine04", "spine03", "spine02", "spine01", "neck01", "neck02", "neck03", "head",
         "clavicle.L", "upperarm01.L", "lowerarm01.L", "lowerarm02.L", "wrist.L",
         "clavicle.R", "upperarm01.R", "lowerarm01.R", "lowerarm02.R", "wrist.R",
         "upperleg01.L", "lowerleg01.L", "foot.L", "upperleg01.R", "lowerleg01.R", "foot.R")
FPS = 30.0


# ------------------------------------------------------------------------------------------------- BVH
def read_bvh(text):
    """(joints, frames (F, C) float64, frame time). joints: list of dict(name, parent, offset, channels, col)."""
    tok = text.split()
    i = 0
    joints, stack = [], []
    col = 0
    while i < len(tok):
        w = tok[i]
        if w in ("ROOT", "JOINT"):
            joints.append(dict(name=tok[i + 1], parent=stack[-1] if stack else -1, offset=None, channels=[], col=col))
            i += 2
        elif w == "End":
            joints.append(dict(name=None, parent=stack[-1], offset=None, channels=[], col=col))
            i += 2
        elif w == "{":
            stack.append(len(joints) - 1)
            i += 1
        elif w == "}":
            stack.pop()
            i += 1
        elif w == "OFFSET":
            joints[stack[-1]]["offset"] = np.array([float(x) for x in tok[i + 1:i + 4]])
            i += 4
        elif w == "CHANNELS":
            n = int(tok[i + 1])
            joints[stack[-1]]["channels"] = tok[i + 2:i + 2 + n]
            joints[stack[-1]]["col"] = col
            col += n
            i += 2 + n
        elif w == "MOTION":
            nf = int(tok[i + 2])
            ft = float(tok[i + 5])
            vals = np.array([float(x) for x in tok[i + 6:i + 6 + nf * col]]).reshape(nf, col)
            return joints, vals, ft
        else:
            i += 1
    raise ValueError("no MOTION section")


def _rot(axis, deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    m = np.zeros(a.shape + (3, 3))
    k = "XYZ".index(axis)
    i, j = [(1, 2), (2, 0), (0, 1)][k]
    m[..., k, k] = 1.0
    m[..., i, i] = c
    m[..., j, j] = c
    m[..., i, j] = -s
    m[..., j, i] = s
    return m


def bvh_fk(joints, vals):
    """World rotations (F, J, 3, 3) and joint positions (F, J, 3) for every frame."""
    F = len(vals)
    J = len(joints)
    G = np.zeros((F, J, 3, 3))
    P = np.zeros((F, J, 3))
    for j, jt in enumerate(joints):
        R = np.tile(np.eye(3), (F, 1, 1))
        pos = np.zeros((F, 3))
        for k, ch in enumerate(jt["channels"]):
            v = vals[:, jt["col"] + k]
            if ch.endswith("rotation"):
                R = R @ _rot(ch[0], v)
            else:
                pos[:, "XYZ".index(ch[0])] = v
        p = jt["parent"]
        if p < 0:
            G[:, j] = R
            P[:, j] = pos + jt["offset"]
        else:
            G[:, j] = G[:, p] @ R
            P[:, j] = P[:, p] + np.einsum("fij,j->fi", G[:, p], jt["offset"])
    return G, P


# ------------------------------------------------------------------------------------------------- maths
def mat2q(M):
    return np.array([bm.qfrommat(m) for m in M.reshape(-1, 3, 3)]).reshape(M.shape[:-2] + (4,))


def swing_twist(q, axis):
    """q = swing * twist, twist about `axis` (unit, in the rotated frame's own coordinates)."""
    q = np.asarray(q, np.float64)
    p = (q[..., 1:] * axis).sum(-1, keepdims=True) * axis
    tw = np.concatenate([q[..., :1], p], axis=-1)
    tw = bm.qn(np.where(np.linalg.norm(tw, axis=-1, keepdims=True) < 1e-9, bm.IDENT, tw))
    sw = bm.qmul(q, bm.qconj(tw))
    return sw, tw


def unroll(q):
    """Makes a run of quaternions continuous (no sign flips)."""
    q = q.copy()
    for k in range(1, len(q)):
        flip = (q[k] * q[k - 1]).sum(-1) < 0
        q[k][flip] *= -1
    return q


# ------------------------------------------------------------------------------------------------- retarget
class Retarget:
    """Carries CMU frames onto the MakeHuman skeleton (the man's proportions; the local rotations suit every
    shape, because every shape's neutral frames are aligned with the world axes)."""

    MAP = {  # MakeHuman bone: (CMU joint whose rotation drives it, MH joint the bone points to, CMU joint it points to)
        "upperleg01": ("UpLeg", "lowerleg01", "Leg"),
        "lowerleg01": ("Leg", "foot", "Foot"),
        "foot": ("Foot", None, "ToeBase"),
        "upperarm01": ("Arm", "lowerarm01", "ForeArm"),
        "lowerarm01": ("ForeArm", "wrist", "Hand"),
        "wrist": ("Hand", None, None),
        "clavicle": ("Shoulder", "upperarm01", "Arm"),
    }

    def __init__(self, joints, ref):
        """ref: the channels of the capture's T-pose frame (the first frame of every file of the 2010 release:
        legs straight down, arms straight out, head level). Rotations are taken relative to it."""
        self.rig = assets.Rig("man")
        rig = self.rig
        self.ci = {jt["name"]: j for j, jt in enumerate(joints) if jt["name"]}
        G0, P0 = bvh_fk(joints, np.asarray(ref, np.float64)[None])
        self.P0 = P0[0]
        self.G0 = G0[0]
        N = rig.neutral_pos
        i = rig.idx
        self.Q = {}
        for side, cs in (("L", "Left"), ("R", "Right")):
            for mh, (cj, mh_to, c_to) in self.MAP.items():
                b = mh + "." + side
                if mh == "foot":
                    d_mh = rig.tail[i[b]] - rig.head[i[b]]
                    d_mh = bm.qrot(rig.C[i[b]], d_mh)
                elif mh_to is None:
                    self.Q[b] = bm.IDENT.copy()
                    continue
                else:
                    d_mh = N[i[mh_to + "." + side]] - N[i[b]]
                if mh == "clavicle":
                    d_mh = N[i["upperarm01." + side]] - N[i[b]]
                cfrom = cs + cj
                cto = cs + c_to
                d_c = self.P0[self.ci[cto]] - self.P0[self.ci[cfrom]]
                self.Q[b] = bm.qbetween(d_mh, d_c)
        # leg length of both skeletons (hip joint to ankle), for the root's travel
        self.leg_mh = float(np.linalg.norm(N[i["lowerleg01.L"]] - N[i["upperleg01.L"]])
                            + np.linalg.norm(N[i["foot.L"]] - N[i["lowerleg01.L"]]))
        P = self.P0
        self.leg_c = float(np.linalg.norm(P[self.ci["LeftLeg"]] - P[self.ci["LeftUpLeg"]])
                           + np.linalg.norm(P[self.ci["LeftFoot"]] - P[self.ci["LeftLeg"]]))
        self.s = self.leg_mh / self.leg_c
        hips_c = 0.5 * (P[self.ci["LeftUpLeg"]] + P[self.ci["RightUpLeg"]])
        self.hip_off_c = hips_c - P[self.ci["Hips"]]          # from the BVH root to the middle of the hip joints

    def frames(self, G, Pc, foot_pitch=None):
        """Local rotations (F, len(BONES), 4), root rotation (F, 4) and root position (F, 3) (MH body frame,
        metres, relative to the neutral root place, not yet re-centred)."""
        rig = self.rig
        i = rig.idx
        ci = self.ci
        F = len(G)
        Gq = {name: unroll(mat2q(G[:, j] @ self.G0[j].T)) for name, j in ci.items()}
        A = {}
        A["root"] = Gq["Hips"]
        A["chest"] = Gq["Spine1"]
        A["head"] = Gq["Head"]
        for side, cs in (("L", "Left"), ("R", "Right")):
            for mh, (cj, _a, _b) in self.MAP.items():
                b = mh + "." + side
                A[b] = bm.qmul(Gq[cs + cj], self.Q[b])
        out = np.zeros((F, len(BONES), 4))
        out[..., 0] = 1.0
        B = {n: k for k, n in enumerate(BONES)}
        rootq = A["root"]
        # spine: the chest relative to the pelvis, shared over four vertebrae
        rel = bm.qmul(bm.qconj(rootq), A["chest"])
        for b in ("spine05", "spine04", "spine03", "spine02"):
            out[:, B[b]] = bm.qpow(rel, 0.25)
        relh = bm.qmul(bm.qconj(A["chest"]), A["head"])
        for b in ("neck01", "neck02", "neck03"):
            out[:, B[b]] = bm.qpow(relh, 1.0 / 6.0)
        out[:, B["head"]] = bm.qpow(relh, 0.5)
        # limbs, one frame at a time through the MakeHuman hierarchy
        for f in range(F):
            q = np.tile(bm.IDENT, (rig.nb, 1))
            for k, b in enumerate(BONES):
                if b in ("spine05", "spine04", "spine03", "spine02", "neck01", "neck02", "neck03", "head"):
                    q[i[b]] = out[f, k]
            for side in ("L", "R"):
                # clavicle (half of the captured shrug: the capture's shoulders are noisy)
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[rig.parent[i["clavicle." + side]]]
                lc = bm.qpow(bm.qmul(bm.qconj(par), A["clavicle." + side][f]), 0.5)
                q[i["clavicle." + side]] = lc
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[rig.parent[i["upperarm01." + side]]]
                q[i["upperarm01." + side]] = bm.qmul(bm.qconj(par), A["upperarm01." + side][f])
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[i["upperarm02." + side]]
                rel = bm.qmul(bm.qconj(par), A["lowerarm01." + side][f])
                sw, tw = swing_twist(rel, np.array([0.0, 1.0, 0.0]))
                q[i["lowerarm01." + side]] = sw
                q[i["lowerarm02." + side]] = tw
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[i["lowerarm02." + side]]
                q[i["wrist." + side]] = bm.qpow(bm.qmul(bm.qconj(par), A["wrist." + side][f]), 0.5)
                # legs
                par = Aw[rig.parent[i["upperleg01." + side]]]
                q[i["upperleg01." + side]] = bm.qmul(bm.qconj(par), A["upperleg01." + side][f])
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[i["upperleg02." + side]]
                q[i["lowerleg01." + side]] = bm.qmul(bm.qconj(par), A["lowerleg01." + side][f])
                _, _, Aw = rig.fk(q, None, rootq[f])
                par = Aw[i["lowerleg02." + side]]
                fq = A["foot." + side][f]
                if foot_pitch is not None:
                    fq = bm.qmul(fq, bm.qx(foot_pitch[side]))
                q[i["foot." + side]] = bm.qmul(bm.qconj(par), fq)
            for k, b in enumerate(BONES):
                out[f, k] = q[i[b]]
        # the root: the middle of the hip joints carried into MakeHuman metres
        hips = Pc[:, ci["Hips"]] + np.einsum("fij,j->fi", G[:, ci["Hips"]], self.hip_off_c)
        N = rig.neutral_pos
        mh_hips = 0.5 * (N[i["upperleg01.L"]] + N[i["upperleg01.R"]])
        root_off = N[i["root"]] - mh_hips
        pos = hips * self.s + bm.qrot(rootq, root_off) - N[i["root"]]
        return np.array([unroll(out[:, k]) for k in range(len(BONES))]).transpose(1, 0, 2), rootq, pos


def heading_of(G, ci):
    """Facing (radians about y, 0 toward +z) of the pelvis in each frame."""
    r = G[:, ci["Hips"]] @ np.array([0.0, 0.0, 1.0])
    return np.arctan2(r[:, 0], r[:, 2])


def contacts(rig, qs, rootq, pos, fps):
    """How planted each foot is in each frame (0..1): low and slow."""
    F = len(qs)
    i = rig.idx
    q = np.tile(bm.IDENT, (rig.nb, 1))
    ank = np.zeros((F, 2, 3))
    toe = np.zeros((F, 2, 3))
    for f in range(F):
        for k, b in enumerate(BONES):
            q[i[b]] = qs[f, k]
        D, P, A = rig.fk(q, rig.neutral_pos[0] + pos[f], rootq[f])
        M = rig.matrices(D, P)
        for s, sd in enumerate(("L", "R")):
            ank[f, s] = P[i["foot." + sd]]
            fb = i["foot." + sd]
            toe[f, s] = M[fb][:, :3] @ rig.tail[fb] + M[fb][:, 3]
    base_a = np.percentile(ank[..., 1], 8, axis=0)
    base_t = np.percentile(toe[..., 1], 8, axis=0)
    low = np.minimum(ank[..., 1] - base_a, toe[..., 1] - base_t)
    vel = np.zeros((F, 2))
    va = np.linalg.norm(np.gradient(ank[..., [0, 2]], axis=0), axis=-1) * fps
    vt = np.linalg.norm(np.gradient(toe[..., [0, 2]], axis=0), axis=-1) * fps
    vel = np.minimum(va, vt)
    c = np.clip(1.0 - low / 0.06, 0, 1) * np.clip(1.0 - (vel - 0.35) / 0.55, 0, 1)
    k = np.array([0.25, 0.5, 0.25])
    for s in range(2):
        c[:, s] = np.convolve(np.pad(c[:, s], 1, mode="edge"), k, mode="valid")
    return np.clip((c - 0.3) / 0.4, 0, 1), ank, toe


def level_feet(rig, qs, rq, pos, con, ank):
    """Both soles on one level: the capture's two legs are not quite the same length, so after retargeting one
    foot stands a little higher than the other when planted. Each leg is bent or stretched (by inverse
    kinematics, the foot's own rotation kept) so that its planted height matches the lower foot's."""
    from p3d import motion as mo
    M = mo.Motions(rig, {})
    i = rig.idx
    h = [float(np.median(ank[con[:, s] > 0.8, s, 1])) if (con[:, s] > 0.8).any() else 0.0 for s in range(2)]
    ref = min(h)
    qs = qs.copy()
    for f in range(len(qs)):
        P = M.identity()
        for k, b in enumerate(BONES):
            P.q[i[b]] = qs[f, k]
        P.rot = rq[f]
        P.pos = pos[f]
        for s, sd in enumerate(("L", "R")):
            d = h[s] - ref
            if d < 0.002:
                continue
            _, Pj, A = M.local_fk(P)
            ank_f = Pj[i["foot." + sd]] - np.array([0.0, d, 0.0])
            hip = Pj[i["upperleg01." + sd]]
            knee = Pj[i["lowerleg01." + sd]]
            pole = knee - 0.5 * (hip + Pj[i["foot." + sd]])
            M.leg_to(P, sd, ank_f, knee=pole, foot=A[i["foot." + sd]])
        for k, b in enumerate(BONES):
            qs[f, k] = P.q[i[b]]
    return qs, h


def load_bvh(name, folder):
    subj = int(name.split("_")[0])
    if folder:
        p = os.path.join(folder, "%03d" % subj, name + ".bvh")
        with open(p) as f:
            return f.read()
    url = MIRROR % (subj, name)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("ascii", "replace")


def resample(vals, ft, a, b, fps):
    """Frames a..b of a capture at `fps` (linear in channels is not right for angles: picks the nearest frames
    of a 120 fps capture, which at 30 fps are exact)."""
    step = (1.0 / fps) / ft
    idx = np.arange(a, b, step)
    return vals[np.round(idx).astype(int)]


# ------------------------------------------------------------------------------------------------- baking
def find_cycle(P, ci, ft, lo, hi):
    """(start, length) in capture frames of the cleanest cycle: the pose (joints relative to the pelvis, in
    the pelvis's own heading) and the vertical speed match best one cycle later."""
    hips = P[:, ci["Hips"]]
    rel = P - hips[:, None]
    F = len(P)
    feat = rel.reshape(F, -1)
    vy = np.gradient(hips[:, 1])
    best = (1e18, 0, 0)
    for n in range(int(lo / ft), int(hi / ft)):
        for s0 in range(5, F - n - 5, 2):
            e = np.sum((feat[s0] - feat[s0 + n]) ** 2) + 400.0 * (vy[s0] - vy[s0 + n]) ** 2
            if e < best[0]:
                best = (e, s0, n)
    return best[1], best[2]


def yaw_matrix(a):
    c, s_ = np.cos(a), np.sin(a)
    return np.array([[c, 0.0, s_], [0.0, 1.0, 0.0], [-s_, 0.0, c]])


def floor_offset(rig, qs, rq, pos):
    """How far to lift the root so that the lowest skin point of the clip touches the ground."""
    i = rig.idx
    lows = []
    for f in range(0, len(qs), 2):
        q = np.tile(bm.IDENT, (rig.nb, 1))
        for k, b in enumerate(BONES):
            q[i[b]] = qs[f, k]
        D, Pj, A = rig.fk(q, rig.neutral_pos[0] + pos[f], rq[f])
        v = rig.skin(rig.matrices(D, Pj))
        lows.append(float(v[:, 1].min()))
    return -float(np.percentile(lows, 3))


def bake(folder, names=None):
    out = {}
    done = set()
    texts = {}

    def get(name):
        if name not in texts:
            texts[name] = read_bvh(load_bvh(name, folder))
        return texts[name]

    for name, (src, a, b, kind, note) in CLIPS.items():
        if names and name not in names or name in done:
            continue
        group = [(name, src, a, b, note)]
        if isinstance(kind, tuple):
            o = kind[1]
            group.append((o, CLIPS[o][0], CLIPS[o][1], CLIPS[o][2], CLIPS[o][4]))
        shared = None
        for (nm, sr, a0, b0, nt) in group:
            J, V, ft = get(sr)
            ret = Retarget(J, V[0])
            V = V[1:]
            f0 = 0 if a0 is None else int(round(a0 / ft))
            f1 = len(V) if b0 is None else int(round(b0 / ft))
            V = V[f0:f1]
            G, P = bvh_fk(J, V)
            ci = ret.ci
            loop = kind == "cycle"
            if loop:
                lo, hi = (0.85, 1.45) if nm == "walk" else (0.5, 0.95)
                s0, n = find_cycle(P, ci, ft, lo, hi)
                hips = P[:, ci["Hips"]]
                d = hips[s0 + n] - hips[s0]
                yaw = np.arctan2(d[0], d[2])
                origin = hips[s0, [0, 2]]
                m = max(int(round(n * ft * FPS)), 2)
                idx = np.round(s0 + np.arange(m + 1) * n / m).astype(int)
            else:
                if shared is None:
                    yaw = heading_of(G[:1], ci)[0]
                    origin = P[0, ci["Hips"], [0, 2]]
                    shared = (yaw, origin)
                else:
                    yaw, origin = shared
                step = 1.0 / FPS / ft
                idx = np.round(np.arange(0, len(V) - 1, step)).astype(int)
            Y = yaw_matrix(-yaw)
            o3 = np.array([origin[0], 0.0, origin[1]])
            Gt = np.einsum("ij,fkjl->fkil", Y, G[idx])
            Pt = np.einsum("ij,fkj->fki", Y, P[idx] - o3)
            qs, rq, pos = ret.frames(Gt, Pt)
            rig = ret.rig
            levels = (0.0, 0.0)
            if loop:
                c0, ank0, _ = contacts(rig, qs, rq, pos, FPS)
                qs, levels = level_feet(rig, qs, rq, pos, c0, ank0)
            if loop:
                # the seam: what is left between the last frame (one cycle on) and the first is spread over the cycle
                L = float(pos[-1, 2] - pos[0, 2])
                m = len(idx) - 1
                w = (np.arange(m + 1) / m)
                for k in range(qs.shape[1]):
                    e = bm.qmul(bm.qconj(qs[-1, k]), qs[0, k])
                    qs[:, k] = bm.qmul(qs[:, k], bm.qpow(np.broadcast_to(e, (m + 1, 4)), w[:, None]))
                e = bm.qmul(bm.qconj(rq[-1]), rq[0])
                rq = bm.qmul(rq, bm.qpow(np.broadcast_to(e, (m + 1, 4)), w[:, None]))
                r = pos[-1] - pos[0] - np.array([0.0, 0.0, L])
                pos = pos - r[None] * w[:, None]
                pos[:, [0, 2]] -= pos[0, [0, 2]]
                qs, rq, pos = qs[:-1], rq[:-1], pos[:-1]
                # contacts over three laps so that the seam is read like any other moment
                q3 = np.concatenate([qs, qs, qs])
                r3 = np.concatenate([rq, rq, rq])
                p3 = np.concatenate([pos, pos + [0, 0, L], pos + [0, 0, 2 * L]])
                c3, _, _ = contacts(rig, q3, r3, p3, FPS)
                con = c3[m:2 * m]
            else:
                con, _, _ = contacts(rig, qs, rq, pos, FPS)
            pos[:, 1] += floor_offset(rig, qs, rq, pos)
            out["mclip_%s_q" % nm] = qs.astype(np.float16)
            out["mclip_%s_rot" % nm] = rq.astype(np.float32)
            out["mclip_%s_root" % nm] = pos.astype(np.float32)
            out["mclip_%s_contact" % nm] = con.astype(np.float32)
            out["mclip_%s_info" % nm] = np.array([FPS, 1.0 if loop else 0.0, ret.leg_mh, len(qs), L if loop else 0.0], np.float32)
            print("%-10s %-7s %5d frames %5.2f s  feet levelled by %.3f m  %s%s" % (nm, sr, len(qs), len(qs) / FPS,
                  abs(levels[0] - levels[1]), nt,
                  ("  travel %.2f m per cycle, %.2f m/s" % (L, L * FPS / len(qs))) if loop else ""))
            done.add(nm)
    out["mclip_bones"] = np.array(BONES)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bvh", default="", help="folder of CMU BVH files (NNN/NN_NN.bvh); default: download them")
    ap.add_argument("--asset", default=os.path.join(HERE, "..", "assets", "p3d", "body_v1.npz"))
    ap.add_argument("--only", default="", help="comma separated clip names (default: all)")
    a = ap.parse_args()
    names = [x for x in a.only.split(",") if x] or None
    clips = bake(a.bvh, names)
    with np.load(a.asset, allow_pickle=False) as d:
        keep = {k: d[k] for k in d.files if not k.startswith("clip_") and not (names is None and k.startswith("mclip_"))}
    keep.update(clips)
    src = str(keep.get("source", "")).split(" | ")[0].split("; motion clips")[0]
    if "build_p3d_body" not in src:
        src += "; built by tools/build_p3d_body.py"
    note = ("motion clips from the CMU Graphics Lab Motion Capture Database (mocap.cs.cmu.edu, BVH conversion by "
            "B. Hahne; free for research and commercial use), retargeted by tools/build_p3d_motion.py")
    keep["source"] = np.array(src + " | " + note)
    buf = io.BytesIO()
    np.savez_compressed(buf, **keep)
    with open(a.asset, "wb") as f:
        f.write(buf.getvalue())
    print("wrote", os.path.abspath(a.asset), "%.0f KB" % (len(buf.getvalue()) / 1024))


if __name__ == "__main__":
    main()
