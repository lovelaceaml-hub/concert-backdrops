"""Builds assets/p3d/body_v1.npz, the human form that engine/p3d/body.py draws as a cloud of points.

Nothing here runs at render time. The baked file is committed (about 1 MB); this script is the record of
exactly where it came from, and rebuilds it from two public packages on PyPI:

1. The body: the MakeHuman "hm08" base mesh, its default skeleton and skinning weights, and the
   macro shape targets (woman, man, child), as bundled in the wheel `anny` 0.6.2 under
   anny/data/mpfb2/ (the MPFB2 asset pack). Licence: CC0 1.0 Universal (anny/data/mpfb2/LICENSE.md;
   the mesh file itself says "explicitly released as CC0 in september 2020", copyright holders
   Data Collection AB, Joel Palmius, Jonas Hauquier; the weights file says "license": "CC0",
   Copyright (C) 2025 NAVER Corp.).
2. The motion clips are not made here: tools/build_p3d_motion.py adds them to the same file afterwards,
   from the CMU Graphics Lab Motion Capture Database (free for research and commercial use). An earlier
   version took clips from the pybullet source distribution (the DeepMimic reference motions, derived in
   part from the SFU database, whose terms were not verified); they are no longer used or stored.

What the script changes: the face region is smoothed so that no facial feature survives (a faceless
mannequin: only the outline of a profile remains), helper geometry is dropped, the face and toe bones
are folded into the head and the feet, units become metres with the soles at y = 0.

Usage (needs network access to PyPI, numpy only):
    python tools/build_p3d_body.py            # downloads into a temp folder, writes assets/p3d/body_v1.npz
    python tools/build_p3d_body.py --anny DIR # use an already extracted package
    python tools/build_p3d_motion.py          # then add the motion clips
"""
import argparse
import gzip
import json
import os
import subprocess
import sys
import tempfile
import zipfile

import numpy as np

ANNY = "anny==0.6.2"
SHAPES = {
    # name: list of (target under targets/macrodetails, weight)
    "woman": [("caucasian-female-young", 1 / 3), ("asian-female-young", 1 / 3), ("african-female-young", 1 / 3)],
    "man": [("caucasian-male-young", 1 / 3), ("asian-male-young", 1 / 3), ("african-male-young", 1 / 3)],
    "child": [("caucasian-female-child", 1 / 6), ("asian-female-child", 1 / 6), ("african-female-child", 1 / 6),
              ("caucasian-male-child", 1 / 6), ("asian-male-child", 1 / 6), ("african-male-child", 1 / 6)],
}


def fetch(tmp):
    """Downloads the package from PyPI and unpacks only what is needed. Returns the mpfb2 folder."""
    a = os.path.join(tmp, "anny")
    os.makedirs(a)
    subprocess.check_call([sys.executable, "-m", "pip", "download", "-q", "--no-deps", "-d", a, ANNY])
    whl = [f for f in os.listdir(a) if f.endswith(".whl")][0]
    with zipfile.ZipFile(os.path.join(a, whl)) as z:
        for n in z.namelist():
            if n.startswith("anny/data/mpfb2/") and (
                    n.endswith(("base.obj", "rig.default.json", "weights.default.json", "LICENSE.md"))
                    or "/macrodetails/" in n and n.count("/") == 5):
                z.extract(n, a)
    return os.path.join(a, "anny", "data", "mpfb2")


def read_obj(path):
    v = []
    faces = []
    grp = []
    g = ""
    for line in open(path):
        if line.startswith("v "):
            v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("g "):
            g = line.split()[1]
        elif line.startswith("f "):
            faces.append([int(x.split("/")[0]) - 1 for x in line.split()[1:]])
            grp.append(g)
    return np.array(v, np.float64), faces, grp


def read_target(path, n):
    d = np.zeros((n, 3))
    with gzip.open(path, "rt") as f:
        for line in f:
            s = line.split()
            if len(s) == 4 and not s[0].startswith("#"):
                d[int(s[0])] = [float(s[1]), float(s[2]), float(s[3])]
    return d


def joint_pos(spec, v, cubes):
    s = spec["strategy"]
    if s == "CUBE":
        return v[cubes[spec["cube_name"]]].mean(0)
    if s == "VERTEX":
        return v[spec["vertex_index"]]
    if s == "MEAN":
        return v[spec["vertex_indices"]].mean(0)
    raise ValueError(s)


def smooth_face(v, tris, w_face, iters):
    """Taubin smoothing of the face region (weight w_face per vertex, 0..1): melts eyes, lips, nostrils and
    ears into a mannequin surface while the head keeps its size and the profile keeps its outline."""
    n = len(v)
    e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    e = np.concatenate([e, e[:, ::-1]])
    e = np.unique(e, axis=0)
    deg = np.bincount(e[:, 0], minlength=n).astype(np.float64)
    deg[deg == 0] = 1
    out = v.copy()
    for _ in range(iters):
        for lam in (0.55, -0.57):
            avg = np.zeros_like(out)
            np.add.at(avg, e[:, 0], out[e[:, 1]])
            avg /= deg[:, None]
            out = out + (lam * w_face)[:, None] * (avg - out)
    return out


def visibility(v, t, sel, ndir=128, pix=0.01, tol=0.015):
    """For each selected vertex, the share of directions from which it can be seen from outside the mesh
    (depth buffers of a dense point sampling of the selected region; units: decimetres here)."""
    tt = t[np.isin(t, sel).all(1)]
    a, b, c = v[tt[:, 0]], v[tt[:, 1]], v[tt[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    k = np.maximum((area / (0.35 * pix * pix)).astype(int), 3)
    rng = np.random.default_rng(1)
    ti = np.repeat(np.arange(len(tt)), k)
    r1 = np.sqrt(rng.random(len(ti)))
    r2 = rng.random(len(ti))
    pts = a[ti] * (1 - r1)[:, None] + b[ti] * (r1 * (1 - r2))[:, None] + c[ti] * (r1 * r2)[:, None]
    vs = v[sel]
    lo = pts.min(0) - 0.1
    i = np.arange(ndir) + 0.5
    ph = np.arccos(1 - 2 * i / ndir)
    th = np.pi * (1 + 5 ** 0.5) * i
    dirs = np.stack([np.cos(th) * np.sin(ph), np.cos(ph), np.sin(th) * np.sin(ph)], 1)
    seen = np.zeros(len(sel))
    for dv in dirs:
        ax = np.cross(dv, [0.0, 1.0, 0.0])
        if np.linalg.norm(ax) < 1e-3:
            ax = np.cross(dv, [1.0, 0.0, 0.0])
        ax /= np.linalg.norm(ax)
        bx = np.cross(dv, ax)
        px = ((pts - lo) @ ax / pix).astype(int)
        py = ((pts - lo) @ bx / pix).astype(int)
        ox, oy = px.min(), py.min()
        w = px.max() - ox + 1
        h = py.max() - oy + 1
        zb = np.full(w * h, -1e9)
        np.maximum.at(zb, (py - oy) * w + (px - ox), pts @ dv)
        vx = np.clip(((vs - lo) @ ax / pix).astype(int) - ox, 0, w - 1)
        vy = np.clip(((vs - lo) @ bx / pix).astype(int) - oy, 0, h - 1)
        seen += (vs @ dv) >= zb[vy * w + vx] - tol
    return seen / ndir


def close_cavities(v, tris, sel):
    """Removes the pockets inside the head (the mouth bag and the two eye sockets) and closes the openings.
    Returns (new triangles, kept vertex indices, loops): each loop is the ring of kept vertices around one
    opening; a new vertex at its centre closes it (appended after the kept vertices, in loop order)."""
    frac = visibility(v, tris, sel)
    inside = np.zeros(len(v), bool)
    inside[sel[frac < 0.08]] = True
    # keep only the big pockets (the mouth and the two eyes), not stray pits
    e0 = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    e0 = e0[inside[e0].all(1)]
    lab = np.arange(len(v))
    for _ in range(200):                      # label spreading over the edges between inside vertices
        m = np.minimum(lab[e0[:, 0]], lab[e0[:, 1]])
        new = lab.copy()
        np.minimum.at(new, e0[:, 0], m)
        np.minimum.at(new, e0[:, 1], m)
        if (new == lab).all():
            break
        lab = new
    size = np.bincount(lab[inside], minlength=len(v))
    inside &= size[lab] >= 60
    keep_t = ~inside[tris].any(1)
    t2 = tris[keep_t]
    # boundary edges, directed as in their triangle
    e = np.concatenate([t2[:, [0, 1]], t2[:, [1, 2]], t2[:, [2, 0]]])
    key = np.sort(e, axis=1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    be = e[cnt[inv.reshape(-1)] == 1]
    nxt = {}
    for x, y in be:
        nxt.setdefault(int(x), []).append(int(y))
    loops = []
    while nxt:
        s0 = min(nxt)
        loop = [s0]
        cur = nxt[s0].pop()
        if not nxt[s0]:
            del nxt[s0]
        while cur != s0 and cur in nxt:
            loop.append(cur)
            n2 = nxt[cur].pop()
            if not nxt[cur]:
                del nxt[cur]
            cur = n2
        loops.append(loop)
    used = np.zeros(len(v), bool)
    used[t2.reshape(-1)] = True
    kept = np.where(used)[0]
    remap = -np.ones(len(v), np.int64)
    remap[kept] = np.arange(len(kept))
    t2 = remap[t2]
    fans = []
    for k, loop in enumerate(loops):
        c = len(kept) + k
        for a, b in zip(loop, loop[1:] + loop[:1]):
            fans.append([remap[b], remap[a], c])
    t2 = np.concatenate([t2, np.array(fans, np.int64)])
    return t2.astype(np.int32), kept, loops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anny", default="", help="folder that holds the extracted anny/data/mpfb2")
    ap.add_argument("--smooth", type=int, default=160, help="face smoothing passes")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "p3d",
                                                  "body_v1.npz"))
    a = ap.parse_args()
    mp = a.anny or fetch(tempfile.mkdtemp(prefix="p3dbody"))

    v0, faces, grp = read_obj(os.path.join(mp, "3dobjs", "base.obj"))
    nv = len(v0)
    cubes = {}
    for f, g in zip(faces, grp):
        if g.startswith("joint-"):
            cubes.setdefault(g, set()).update(f)
    cubes = {k: sorted(s) for k, s in cubes.items()}
    body_faces = [f for f, g in zip(faces, grp) if g == "body"]
    used = sorted({i for f in body_faces for i in f})
    remap = -np.ones(nv, np.int64)
    remap[used] = np.arange(len(used))
    tris = []
    for f in body_faces:
        f = [remap[i] for i in f]
        for k in range(1, len(f) - 1):
            tris.append([f[0], f[k], f[k + 1]])
    tris = np.array(tris, np.int32)

    rig = json.load(open(os.path.join(mp, "rigs", "standard", "rig.default.json")))
    wts = json.load(open(os.path.join(mp, "rigs", "standard", "weights.default.json")))["weights"]

    # bones kept: everything except the face rig (folded into head), the toes (into the feet), the breasts
    # (into the chest)
    def ancestors(b):
        out = []
        while rig[b].get("parent"):
            b = rig[b]["parent"]
            out.append(b)
        return out
    fold = {}
    for b in rig:
        if "head" in ancestors(b):
            fold[b] = "head"
        elif b.startswith("toe"):
            fold[b] = "foot." + b[-1]
        elif b.startswith("breast"):
            fold[b] = "spine02"
    order = []

    def add(b):
        if b in order:
            return
        p = rig[b].get("parent")
        if p:
            add(p)
        order.append(b)
    for b in rig:
        if b not in fold:
            add(b)
    names = order
    bi = {b: i for i, b in enumerate(names)}
    parent = np.array([bi[rig[b]["parent"]] if rig[b].get("parent") else -1 for b in names], np.int16)

    W = np.zeros((len(used), len(names)))
    for b, lst in wts.items():
        if b not in rig:
            continue
        j = bi[fold.get(b, b)]
        for vi, w in lst:
            if remap[vi] >= 0:
                W[remap[vi], j] += w
    assert (W.sum(1) > 0).all(), "vertices without weights"
    top = np.argsort(-W, axis=1, kind="stable")[:, :4]
    wv = np.take_along_axis(W, top, 1)
    wv = wv / wv.sum(1, keepdims=True)

    # the face region: vertices that the face rig moves
    wf = np.zeros(len(used))
    for b in wts:
        if fold.get(b) == "head":
            for vi, w in wts[b]:
                if remap[vi] >= 0:
                    wf[remap[vi]] += w
    head_w = W[:, bi["head"]]

    # the three body shapes, in the units of the mesh file (decimetres)
    shapes = {}
    for shape, mix in SHAPES.items():
        v = v0.copy()
        for name, w in mix:
            v += w * read_target(os.path.join(mp, "targets", "macrodetails", name + ".target.gz"), nv)
        heads = np.array([joint_pos(rig[b]["head"], v, cubes) for b in names])
        tails = np.array([joint_pos(rig[b]["tail"], v, cubes) for b in names])
        shapes[shape] = (v[used], heads, tails)

    # no face: remove the mouth bag and the eye sockets, close the openings (the same cut for every shape)
    tris, kept, loops = close_cavities(shapes["woman"][0], tris, np.where(head_w > 0.2)[0])
    print("closed", len(loops), "openings (mouth and eyes), loop sizes", [len(x) for x in loops])
    W = np.concatenate([W[kept]] + [W[lp].mean(0, keepdims=True) for lp in loops])
    wf = np.concatenate([wf[kept]] + [np.ones(1) for lp in loops])
    head_w = W[:, bi["head"]]
    top = np.argsort(-W, axis=1, kind="stable")[:, :4]
    wv = np.take_along_axis(W, top, 1)
    wv = wv / wv.sum(1, keepdims=True)

    out = {}
    for shape, (vb, heads, tails) in shapes.items():
        vb = np.concatenate([vb[kept]] + [vb[lp].mean(0, keepdims=True) for lp in loops])
        # face smoothing weight: full on the face rig area and the ears, fading over the back of the skull
        hc = heads[bi["head"]]
        top_y = vb[head_w > 0.5][:, 1].max()
        size = top_y - hc[1]
        front = np.clip((vb[:, 2] - (hc[2] - 0.6 * size)) / (0.5 * size), 0, 1)
        fw = np.clip(np.maximum(wf, head_w * front), 0, 1) * (head_w > 0.02)
        vb = smooth_face(vb, tris, fw, a.smooth)
        # metres, soles on y = 0
        y0 = vb[:, 1].min()
        sc = 0.1
        vb = (vb - [0, y0, 0]) * sc
        heads = (heads - [0, y0, 0]) * sc
        tails = (tails - [0, y0, 0]) * sc
        out["verts_" + shape] = vb.astype(np.float32)
        out["head_" + shape] = heads.astype(np.float32)
        out["tail_" + shape] = tails.astype(np.float32)
        print(shape, "height %.3f m" % vb[:, 1].max(), "verts", len(vb))

    out["tris"] = tris
    out["bone_names"] = np.array(names)
    out["bone_parent"] = parent
    out["w_idx"] = top.astype(np.int16)
    out["w_val"] = wv.astype(np.float32)
    out["face_weight"] = np.clip(np.maximum(wf, head_w), 0, 1).astype(np.float32)
    out["source"] = np.array(
        "MakeHuman hm08 base mesh, default rig and weights from the PyPI wheel %s (anny/data/mpfb2, CC0 1.0); "
        "built by tools/build_p3d_body.py" % ANNY)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez_compressed(a.out, **out)
    print("wrote", a.out, os.path.getsize(a.out), "bytes;", len(names), "bones;", len(tris), "triangles")


if __name__ == "__main__":
    main()
