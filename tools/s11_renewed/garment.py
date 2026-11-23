"""Independent formal clothing for the Song 11 conductor.

The coat, sleeves and trousers are authored surfaces in the neutral rig space.
They do not offset or reproduce the underlying anatomical body mesh. The old
cloth sources are replaced before any frame is sampled. Head and hands retain
the established faceless figure-of-light treatment.
"""
from __future__ import annotations

import numpy as np


class Surface:
    """Two-bone skinning of a designed garment surface, using neutral joints."""

    def __init__(self, body, pos, normal, bones, weight, trim=None, hem=None):
        from p3d import bodymath as bm
        self.body = body
        self.n = len(pos)
        self.part = 2
        self.rest = np.asarray(pos, np.float32)
        self.normal = np.asarray(normal, np.float32)
        self.bones = np.asarray(bones, np.int64)
        self.weight = np.asarray(weight, np.float32)
        self.h = self.rest[:, 1] / body.rig.height
        self.seed = bm.rand(self.n, 1723).astype(np.float32)
        self.trim = np.zeros(self.n, bool) if trim is None else np.asarray(trim, bool)
        self.hem = np.zeros(self.n, np.float32) if hem is None else np.asarray(hem, np.float32)
        self.rel = self.rest[:, None] - body.rig.neutral_pos[self.bones]
        self._cache = (None, None)

    def at(self, t, sel=None):
        from p3d import bodymath as bm
        key = round(float(t), 6)
        if key != self._cache[0]:
            frame = self.body.actor.frame(t)
            rotation = bm.qmat(frame['A'])[self.bones]
            p = np.einsum('nkij,nkj->nki', rotation, self.rel) + frame['P'][self.bones]
            n = np.einsum('nkij,nj->nki', rotation, self.normal)
            p = (p * self.weight[..., None]).sum(1)
            n = (n * self.weight[..., None]).sum(1)
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-8)
            # A restrained hem response, delayed behind the conducting motion.
            # Its amplitude is centimetres, not a billowing anatomical skin.
            if np.any(self.hem):
                p[:, 0] += self.hem * (0.008 * np.sin(2.0 * t - 0.7) + 0.003 * np.sin(4.1 * t))
                p[:, 2] += self.hem * (0.007 * np.sin(1.65 * t + self.rest[:, 0] * 3.0))
            self._cache = (key, (p.astype(np.float32), n.astype(np.float32)))
        p, n = self._cache[1]
        return (p, n) if sel is None else (p[sel], n[sel])


def _combine(parts):
    return [np.concatenate([p[i] for p in parts]) for i in range(7)]


def _oval(body, count, rng, ys, rx, rz, center_z, bones, collar=False, lower=False):
    u = rng.random(count)
    a = rng.random(count) * 2.0 * np.pi
    y = ys[0] + (ys[-1] - ys[0]) * u
    width = np.interp(y, ys, rx)
    depth = np.interp(y, ys, rz)
    ca, sa = np.cos(a), np.sin(a)
    # Rounded rectangular panels flatten the front and back of the coat.
    power = 0.66 if not collar else 1.0
    x = width * np.sign(ca) * abs(ca) ** power
    z = center_z + depth * np.sign(sa) * abs(sa) ** power
    p = np.stack([x, y, z], 1)
    n = np.stack([ca / np.maximum(width, .01), np.zeros(count), sa / np.maximum(depth, .01)], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    w = np.clip((y - ys[0]) / (ys[-1] - ys[0]), 0, 1)
    if lower:
        w *= .10
    bb = np.tile([body.rig.idx[b] for b in bones], (count, 1))
    ww = np.stack([1 - w, w], 1)
    # Designed front lapels, a narrow button line, and restrained hem piping.
    front = sa > .72
    lapel_x = np.interp(y, [1.17, 1.47, 1.56], [.035, .15, .09]) * body.rig.height / 1.86
    lapels = front & (y > 1.17 * body.rig.height / 1.86) & (abs(abs(x) - lapel_x) < .009)
    buttons = front & (abs(x) < .012) & (np.abs(np.sin((y - 1.13) * np.pi / .09)) < .16) & (y > 1.13) & (y < 1.42)
    trim = (u < .018) | (collar & (u > .84)) | lapels | buttons
    hem = (1 - u) ** 3 if lower else np.zeros(count)
    return p, n, bb, ww, trim, hem, np.full(count, 1 if collar else 0)


def _limb(body, count, rng, side, upper, middle, end, radii, cuff=False):
    r = body.rig
    N = r.neutral_pos
    q0, q1, q2 = (N[r.idx[b + '.' + side]] for b in (upper, middle, end))
    lengths = np.array([np.linalg.norm(q1 - q0), np.linalg.norm(q2 - q1)])
    split = lengths[0] / lengths.sum()
    u = rng.random(count)
    ang = rng.random(count) * 2.0 * np.pi
    first = u < split
    v = np.where(first, u / split, (u - split) / (1 - split))
    start = np.where(first[:, None], q0, q1)
    stop = np.where(first[:, None], q1, q2)
    center = start * (1 - v[:, None]) + stop * v[:, None]
    axis = stop - start
    axis /= np.linalg.norm(axis, axis=1, keepdims=True)
    tangent = np.cross(axis, [0, 0, 1.0])
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1, keepdims=True), 1e-8)
    second = np.cross(axis, tangent)
    radius = np.interp(u, [0, split, 1], radii) * r.height / 1.86
    normal = tangent * np.cos(ang)[:, None] + second * np.sin(ang)[:, None]
    p = center + radius[:, None] * normal
    blend = np.clip((u - split + .075) / .15, 0, 1)
    bb = np.tile([r.idx[upper + '.' + side], r.idx[middle + '.' + side]], (count, 1))
    ww = np.stack([1 - blend, blend], 1)
    trim = (u > .935) if cuff else np.zeros(count, bool)
    return p, normal, bb, ww, trim, np.zeros(count), np.zeros(count)


def _upper(body, count):
    rng = np.random.default_rng(7111)
    scale = body.rig.height / 1.86
    n0, n1 = int(count * .50), int(count * .22)
    parts = [_oval(body, n0, rng, np.array([.91, 1.06, 1.27, 1.49, 1.56]) * scale,
                   np.array([.26, .245, .26, .285, .155]) * scale,
                   np.array([.18, .175, .185, .16, .115]) * scale, -.01 * scale,
                   ('spine05', 'spine01'))]
    for side in ('L', 'R'):
        parts.append(_limb(body, n1, rng, side, 'upperarm01', 'lowerarm01', 'wrist', [.098, .083, .062], cuff=True))
    remaining = count - n0 - 2 * n1
    parts.append(_oval(body, remaining, rng, np.array([1.53, 1.615]) * scale,
                       np.array([.115, .09]) * scale, np.array([.105, .085]) * scale, .015 * scale,
                       ('spine01', 'neck01'), collar=True))
    p, n, b, w, trim, hem, _ = _combine(parts)
    return Surface(body, p, n, b, w, trim, hem)


def _lower(body, count):
    rng = np.random.default_rng(7112)
    k = body.rig.height / 1.86
    p, n, b, w, trim, hem, _ = _oval(body, count, rng,
        np.array([.54, .74, .91, 1.07]) * k,
        np.array([.325, .305, .278, .25]) * k,
        np.array([.225, .215, .195, .18]) * k, -.012 * k, ('root', 'spine05'), lower=True)
    return Surface(body, p, n, b, w, trim, hem)


def _trousers(body, count):
    rng = np.random.default_rng(7113)
    parts = []
    for side, n in [('L', count // 2), ('R', count - count // 2)]:
        parts.append(_limb(body, n, rng, side, 'upperleg01', 'lowerleg01', 'foot', [.118, .105, .09]))
    p, n, b, w, trim, hem, _ = _combine(parts)
    return Surface(body, p, n, b, w, trim, hem)


def dress(body):
    """Replace every anatomical clothing surface, retaining head, hands and boots."""
    from p3d import looks
    from p3d.api import lin
    cloth = [j for j, s in enumerate(body.sources) if s.part == looks.CLOTH]
    if len(cloth) != 3:
        raise RuntimeError('Renewed conductor expects the three original coat sources.')
    for j, fn in zip(cloth, (_upper, _trousers, _lower)):
        body.sources[j] = fn(body, body.sources[j].n)
    body.cloth = None  # All garment surfaces now have their own authored geometry.
    body.cloud['rest'] = np.concatenate([s.rest for s in body.sources]).astype(np.float32)
    body.cloud['h'] = np.clip(np.concatenate([s.h for s in body.sources]), 0, 1).astype(np.float32)
    body.skinlike = np.concatenate([np.full(s.n, not isinstance(s, Surface)) for s in body.sources])
    body._pts.clear()
    body._sk.clear()
    body._anchors.clear()
    garment = np.zeros(body.cloud['n'], bool)
    trim = np.zeros(body.cloud['n'], bool)
    trouser = np.zeros(body.cloud['n'], bool)
    for j in cloth:
        sl = slice(body.offs[j], body.offs[j + 1])
        garment[sl] = True
        trim[sl] = body.sources[j].trim
        if j == cloth[1]:
            trouser[sl] = True
    seed = body.cloud['seed']
    colors = np.broadcast_to(lin('#f1d9a8'), (body.cloud['n'], 3)).copy()
    colors[garment] = lin('#3478b8') * (.85 + .30 * seed[garment, None])
    colors[trouser] = lin('#214a7b') * (.9 + .2 * seed[trouser, None])
    colors[trim] = lin('#e9bf69') * 1.15
    for layer in body.layers:
        ii = layer['idx']
        layer['color'] = colors[ii].astype(np.float32)
        if layer['kind'] == 'spark':
            layer['color'] = (layer['color'] * .75 + lin('#b7d9fa') * .25).astype(np.float32)
        layer['alpha'] *= np.where(garment[ii], 1.1, .8)
        layer['alpha'] *= np.where(trim[ii], 1.8, 1.0)
    # Dense, dim fabric points create a readable coat while its surface sparkles.
    ii = np.flatnonzero(garment)
    body.layers.insert(0, dict(kind='soft', idx=ii,
        size=np.full(len(ii), .0075 * body.k, np.float32), color=(colors[ii] * .34).astype(np.float32),
        alpha=np.full(len(ii), .30, np.float32), emit=np.ones(len(ii), np.float32),
        seed=seed[ii], twinkle=.08, rim=(.0, 2.0), backlight=0.0, lit=0.0,
        weight=1.0, after=None, before=None, detail=None))
    body._renewed_garment = dict(kind='independent_closed_long_coat',
        source_points=int(garment.sum()), trim_points=int(trim.sum()),
        underlying_torso_and_seat_rendered=False)
    return body


def dress_crowd(body):
    """Remove body-shaped torso/seat surfaces from every clothed prototype.

    Existing loose simulated skirts, veils and sleeves remain. Only skin-offset
    torso/seat sources are replaced with independently designed formal surfaces.
    This supports the original seated instrumentalists as well as walkers.
    """
    from p3d import looks
    changed = False
    for j, source in enumerate(body.sources):
        if source.part != looks.CLOTH or not hasattr(source, 'surf'):
            continue
        surf = source.surf
        regions = body.rig.bone_region[body.rig.vert_bone[surf.vi[:, 0]]]
        if np.any(regions == 2):  # torso, with or without its arm sleeves
            body.sources[j] = _upper(body, source.n)
            changed = True
        elif np.any(regions == 6):  # a trouser/seat layer, no anatomical cleft
            body.sources[j] = _trousers(body, source.n)
            changed = True
    if changed:
        body.cloud['rest'] = np.concatenate([s.rest for s in body.sources]).astype(np.float32)
        body.cloud['h'] = np.clip(np.concatenate([s.h for s in body.sources]), 0, 1).astype(np.float32)
        body.skinlike = np.concatenate([np.full(s.n, not isinstance(s, Surface)) for s in body.sources])
        body._pts.clear()
        body._sk.clear()
        body._anchors.clear()
    return body
