"""Small numpy helpers for the particle bodies (engine/p3d/body.py): quaternions, easing, repeatable noise.

Quaternions are (w, x, y, z), unit length; arrays of them have shape (..., 4). All angles are radians here.
Everything is a pure function: the same input gives the same output on every machine.
"""
import numpy as np

IDENT = np.array([1.0, 0.0, 0.0, 0.0])


def qn(q):
    q = np.asarray(q, np.float64)
    return q / np.maximum(np.linalg.norm(q, axis=-1, keepdims=True), 1e-12)


def qmul(a, b):
    a = np.asarray(a, np.float64)
    b = np.asarray(b, np.float64)
    aw, ax, ay, az = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    bw, bx, by, bz = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([aw * bw - ax * bx - ay * by - az * bz,
                     aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw], axis=-1)


def qconj(q):
    q = np.asarray(q, np.float64).copy()
    q[..., 1:] *= -1.0
    return q


def qaxis(axis, angle):
    """Rotation by angle (radians) about axis (need not be unit)."""
    axis = np.asarray(axis, np.float64)
    axis = axis / np.maximum(np.linalg.norm(axis, axis=-1, keepdims=True), 1e-12)
    angle = np.asarray(angle, np.float64)
    s = np.sin(angle * 0.5)
    return np.concatenate([np.cos(angle * 0.5)[..., None], axis * s[..., None]], axis=-1)


def qx(a):
    return np.array([np.cos(a * 0.5), np.sin(a * 0.5), 0.0, 0.0])


def qy(a):
    return np.array([np.cos(a * 0.5), 0.0, np.sin(a * 0.5), 0.0])


def qz(a):
    return np.array([np.cos(a * 0.5), 0.0, 0.0, np.sin(a * 0.5)])


def qeuler(x=0.0, y=0.0, z=0.0):
    """Rotation about x, then y, then z of the fixed axes (radians)."""
    return qmul(qz(z), qmul(qy(y), qx(x)))


def qmat(q):
    """(..., 4) quaternions to (..., 3, 3) rotation matrices."""
    q = np.asarray(q, np.float64)
    w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    m = np.empty(q.shape[:-1] + (3, 3))
    m[..., 0, 0] = 1 - 2 * (y * y + z * z)
    m[..., 0, 1] = 2 * (x * y - z * w)
    m[..., 0, 2] = 2 * (x * z + y * w)
    m[..., 1, 0] = 2 * (x * y + z * w)
    m[..., 1, 1] = 1 - 2 * (x * x + z * z)
    m[..., 1, 2] = 2 * (y * z - x * w)
    m[..., 2, 0] = 2 * (x * z - y * w)
    m[..., 2, 1] = 2 * (y * z + x * w)
    m[..., 2, 2] = 1 - 2 * (x * x + y * y)
    return m


def qrot(q, v):
    return np.einsum("...ij,...j->...i", qmat(q), np.asarray(v, np.float64))


def qpow(q, f):
    """A fraction f of the rotation q (same axis, f times the angle)."""
    q = np.asarray(q, np.float64)
    q = np.where(q[..., :1] < 0, -q, q)
    v = q[..., 1:]
    s = np.linalg.norm(v, axis=-1, keepdims=True)
    ang = 2.0 * np.arctan2(s, q[..., :1])
    axis = v / np.maximum(s, 1e-12)
    h = ang * f * 0.5
    return np.concatenate([np.cos(h), axis * np.sin(h)], axis=-1)


def qslerp(a, b, u):
    """Shortest way from a to b; u may be a number or an array matching the leading shape."""
    a = np.asarray(a, np.float64)
    b = np.asarray(b, np.float64)
    u = np.asarray(u, np.float64)
    if u.ndim < a.ndim:
        u = u[..., None] if u.ndim else u
    d = np.sum(a * b, axis=-1, keepdims=True)
    b = np.where(d < 0, -b, b)
    d = np.clip(np.abs(d), 0.0, 1.0)
    th = np.arccos(d)
    s = np.sin(th)
    small = s < 1e-5
    s = np.where(small, 1.0, s)
    wa = np.where(small, 1.0 - u, np.sin((1.0 - u) * th) / s)
    wb = np.where(small, u, np.sin(u * th) / s)
    return qn(wa * a + wb * b)


def qbetween(a, b):
    """The smallest rotation that turns direction a onto direction b (single vectors)."""
    a = np.asarray(a, np.float64)
    b = np.asarray(b, np.float64)
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    c = float(np.dot(a, b))
    if c > 1 - 1e-12:
        return IDENT.copy()
    if c < -1 + 1e-9:
        ax = np.cross(a, [1.0, 0.0, 0.0])
        if np.linalg.norm(ax) < 1e-6:
            ax = np.cross(a, [0.0, 1.0, 0.0])
        return qaxis(ax, np.pi)
    ax = np.cross(a, b)
    return qn(np.concatenate([[1.0 + c], ax]))


def qfrommat(m):
    """A 3 x 3 rotation matrix as a quaternion."""
    m = np.asarray(m, np.float64)
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2
        q = [0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [(m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s]
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s]
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s]
    return qn(np.array(q))


def smooth(x):
    """Smoothstep 0..1 (eased at both ends)."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def smoother(x):
    """A gentler ease (zero speed and acceleration at both ends)."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


def ramp(t, t0, t1):
    """0 before t0, 1 after t1, eased between."""
    if t1 <= t0:
        return np.where(np.asarray(t) >= t0, 1.0, 0.0)
    return smoother((np.asarray(t, np.float64) - t0) / (t1 - t0))


def hashf(i, salt=0):
    """Repeatable numbers in 0..1 from integer arrays (the same on every machine)."""
    with np.errstate(over="ignore"):
        i = np.asarray(i).astype(np.uint64) + np.uint64((int(salt) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF)
        i = (i ^ (i >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        i = (i ^ (i >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        i = i ^ (i >> np.uint64(31))
    return (i >> np.uint64(11)).astype(np.float64) / float(1 << 53)


def rand(n, salt=0):
    return hashf(np.arange(n), salt)


def wobble(t, seed, rate=1.0):
    """A smooth wandering value in about -1..1 over time (sum of three slow sines; seed picks the phases)."""
    s = float(seed)
    return (np.sin(t * rate * 1.00 + s * 12.9898) * 0.5
            + np.sin(t * rate * 0.618 + s * 78.233 + 1.7) * 0.3
            + np.sin(t * rate * 1.618 + s * 37.719 + 4.1) * 0.2)


def flow(p, t, scale=1.0, speed=0.3, seed=0.0):
    """A smooth, divergence-free looking drift field for particles: p (N, 3) positions, returns (N, 3) in
    about -1..1. Built from a few sines so that it is cheap, repeatable and never needs stored state."""
    p = np.asarray(p, np.float64) * scale
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    a = t * speed + seed * 3.1
    fx = np.sin(y * 1.31 + a) + np.sin(z * 1.73 - a * 0.7 + 1.3) * 0.7 + np.sin((y + z) * 2.9 + a * 1.3) * 0.35
    fy = np.sin(z * 1.19 + a * 0.9 + 2.1) + np.sin(x * 1.57 - a * 0.6) * 0.7 + np.sin((z + x) * 2.7 - a * 1.1) * 0.35
    fz = np.sin(x * 1.43 - a * 0.8 + 0.7) + np.sin(y * 1.61 + a * 0.5 + 3.3) * 0.7 + np.sin((x + y) * 3.1 + a * 0.9) * 0.35
    return np.stack([fx, fy, fz], axis=1) * 0.5
