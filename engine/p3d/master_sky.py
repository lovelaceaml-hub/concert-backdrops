"""The masterpiece's heavenly scenery (engine/songs/master_peace.py): clouds of light lit from within, aurora
curtains, rivers of light, rain of light, rising lights, motes. Pure numpy point sets for the 3D layer
(engine/p3d/api.py). Everything is a pure function of the time t (and the camera), so any frame renders the same
in any order.
"""
import numpy as np

from .api import lin

TAU = 2.0 * np.pi


def ss(a, b, x):
    """Smoothstep from a to b (works on arrays)."""
    x = np.asarray(x, np.float64)
    if b <= a:
        return (x >= a).astype(np.float64)
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def sc(a, b, x):
    return float(ss(a, b, x))


def _day(hexs, k):
    import theme
    return theme.display(hexs) * k


# ---------------------------------------------------------------------------------------------------- looks
# Warm, heavenly skies: never dark, never cold. Display hex; the engine converts.
LOOKS = dict(
    twilight=dict(base="dawn", sky_top="#1c1d5c", sky_mid="#6b4a92", sky_hor="#f2a27a", sun_color="#ffd49a",
                  sun_int=0.95, sun_el=-1.5, sun_disc=0.0, sun_glow=0.9, stars=0.55, milky=0.25, clouds=0.0,
                  haze=0.55, haze_color="#d58f84", mist=0.30, mist_color="#c88a86", hills=0.0, water="#140c22",
                  mirror=1.0, ripple=0.25, rays=0.55, dust=0.5, dust_color="#ffe0a8", dust_color2="#ffc0c8",
                  bokeh=0.5),
    glory=dict(base="sunrise", sky_top="#2a2a78", sky_mid="#b0709e", sky_hor="#ffc884", sun_color="#ffe0a8",
               sun_int=1.0, sun_el=3.0, sun_disc=4.0, sun_glow=0.85, stars=0.15, milky=0.0, clouds=0.0,
               haze=0.55, haze_color="#e0a07a", mist=0.30, mist_color="#d89a80", hills=0.0, water="#1a1024",
               mirror=1.0, ripple=0.25, rays=0.8, dust=0.6, dust_color="#ffe6b0", dust_color2="#ffcfa8",
               bokeh=0.6, exposure=0.95),
    radiant=dict(base="golden", sky_top="#2f5cb8", sky_mid="#86a8e0", sky_hor="#ffe0b0", sun_color="#fff0d0",
                 sun_int=0.9, sun_el=14.0, sun_disc=3.0, sun_glow=0.7, stars=0.0, milky=0.0, clouds=0.0,
                 haze=0.5, haze_color="#f0d0b0", mist=0.2, mist_color="#f4dcc0", hills=0.0, water="#2a3050",
                 rays=0.6, dust=0.5, dust_color="#fff4dc", dust_color2="#ffe0b0", bokeh=0.4),
)


# ---------------------------------------------------------------------------------------------------- clouds
def billow(rng, center, width, height, n=220, towers=5, flat=0.18):
    """Points on the skin of one cumulus billow: a row of round lobes (bigger in the middle) on a flat base.
    Only the outer skin is kept, so seen from anywhere the limbs are brighter (a silver lining).
    Returns (pos (n, 3), up 0..1, lobe radius per point)."""
    cx, cy, cz = center
    k = max(int(towers), 1)
    xs = np.linspace(-0.5, 0.5, k) * width * 0.78 + rng.normal(0.0, 0.05 * width, k)
    mid = 1.0 - np.abs(np.linspace(-1.0, 1.0, k)) ** 1.5
    rad = width * (0.16 + 0.16 * mid) * rng.uniform(0.8, 1.2, k)
    ys = rad * rng.uniform(0.45, 0.9, k) + height * 0.3 * mid
    zs = rng.normal(0.0, 0.12 * width, k)
    lobes = np.stack([xs, ys, zs], 1)
    pts, rr = [], []
    m = n * 3
    li = rng.integers(0, k, m)
    d = rng.normal(size=(m, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    p = lobes[li] + d * rad[li, None] * rng.uniform(0.88, 1.02, m)[:, None]
    inside = np.zeros(m, bool)
    for j in range(k):
        inside |= (np.linalg.norm(p - lobes[j], axis=1) < rad[j] * 0.86) & (li != j)
    base = flat * height
    keep = ~inside & (p[:, 1] > base * rng.uniform(0.0, 1.0, m))
    p, li = p[keep][:n], li[keep][:n]
    p[:, 1] *= min(1.0, height / max(0.55 * width, 1e-6))      # flatter banks when asked
    pts = np.asarray([cx, cy, cz]) + p
    top = np.clip((p[:, 1]) / max(float(np.max(p[:, 1])), 1e-6), 0.0, 1.0)
    return pts, top, rad[li]


class Billows:
    """Cumulus clouds of light lit from within: each a skin of soft points on round lobes (so the limbs glow like
    a silver lining), warm gold at the top and on the sun side, rose and lilac below, a faint warm body inside.
    Additive light: they glow, never darken.

    clouds: list of dict(center=(x, y, z), width, height, n, bright). gain(t) strength over time. The camera is
    used to leave out what is behind it and to thin puffs that would fill the picture (the camera can fly
    through)."""
    wants_camera = True

    def __init__(self, clouds, gain=None, seed=11, top="#ffd890", warm="#ffb060", rose="#f0708e", lilac="#7a6ae0",
                 core="#ffe8c0", sun_az=180.0, alpha=0.11, puff=0.42, drift=(0.6, 0.0, 0.0), sparkle=0.0,
                 body=0.35, shade=0.55):
        rng = np.random.default_rng(seed)
        P, U, S, B, R = [], [], [], [], []
        for c in clouds:
            n = int(c.get("n", 220))
            pts, up, rad = billow(rng, c["center"], c["width"], c["height"], n=n, towers=c.get("towers", 5))
            P.append(pts)
            U.append(up)
            S.append(rad * puff * rng.uniform(0.75, 1.25, len(pts)))
            B.append(np.full(len(pts), float(c.get("bright", 1.0))))
            R.append(np.full(len(pts), float(c["width"])))
        self.pos = np.concatenate(P)
        self.up = np.concatenate(U)
        self.size = np.concatenate(S)
        self.bright = np.concatenate(B)
        n = len(self.pos)
        self.seed = rng.random(n)
        a = np.radians(sun_az)
        sd = np.array([np.sin(a), 0.25, np.cos(a)])
        cen = np.concatenate([np.repeat(np.asarray(c["center"], np.float64)[None], len(p), 0)
                              for c, p in zip(clouds, P)])
        rel = self.pos - cen
        rel /= np.maximum(np.linalg.norm(rel, axis=1, keepdims=True), 1e-6)
        self.sunny = np.clip(0.5 + 0.5 * (rel @ sd), 0.0, 1.0)
        top, warm, rose, lilac, core = (lin(c) for c in (top, warm, rose, lilac, core))
        mix = rng.random(n)[:, None]
        low = rose[None] * (1.0 - mix) + lilac[None] * mix
        hi = top[None] * self.sunny[:, None] + warm[None] * (1.0 - self.sunny[:, None])
        u = self.up[:, None] ** 0.8
        self.color = hi * u + low * (1.0 - u)
        self.color = self.color * (0.75 + 0.5 * self.sunny[:, None])
        # the side away from the light is dimmer (clouds have depth); far from the sun's azimuth a whole cloud
        # is in shade
        caz = np.arctan2(cen[:, 0], cen[:, 2])
        off = np.abs(((caz - a + np.pi) % TAU) - np.pi)
        self.lit = (1.0 - shade) + shade * (0.55 * self.sunny + 0.45 * np.clip(1.0 - off / np.pi, 0.0, 1.0) ** 1.5)
        self.core = core
        self.cen = cen
        self._gain = gain
        self.alpha = alpha
        self.body = body
        self.drift = np.asarray(drift, np.float64)
        self.sparkle = sparkle

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t, cam=None):
        g = self.gain(t)
        if g <= 0.002:
            return None
        sh = self.drift[None] * t
        pos = self.pos + sh
        al = self.alpha * self.bright * g * (0.55 + 0.45 * self.up) * self.lit
        size = self.size
        col, seed = self.color, self.seed
        if cam is not None:
            e = np.asarray(cam.pos, np.float64)
            d = pos - e
            dist = np.linalg.norm(d, axis=1)
            f = np.asarray(cam.target, np.float64) - e
            f = f / max(float(np.linalg.norm(f)), 1e-9)
            ahead = d @ f
            keep = ahead > -1.2 * size
            al = al * ss(0.7, 2.2, dist / np.maximum(size, 1e-3))
            keep &= al > 2e-4
            pos, size, al, col, seed = pos[keep], size[keep], al[keep], col[keep], seed[keep]
        if len(pos) == 0:
            return None
        out = [dict(pos=pos, size=size, color=col, alpha=al, kind="soft", dof=0.0, fog=0.12, seed=seed,
                    streak=0.0)]
        if self.body > 0.0:                    # the warm light inside: a few big soft glows per cloud
            out.append(dict(pos=pos[::9], size=size[::9] * 2.6, color=self.core, alpha=al[::9] * self.body,
                            kind="soft", dof=0.0, fog=0.12, streak=0.0))
        return out


class CloudSea:
    """Banks of cloud lit from within: billows of soft light, warm gold at their hearts, rose and lilac at
    their edges, lit golden on the side toward the sun. Additive light (they glow; they never darken).

    banks: list of dict(center=(x, y, z), size=(sx, sy, sz), n=puffs, bright=1.0). With banks=None a sea of
    cloud is laid out on a ring round `center` between radii `r0` and `r1` at height `y` (a gap in the middle).
    gain(t): strength over time. The camera is used to leave out puffs behind it and to fade puffs that would
    fill the picture (the camera can fly through)."""
    wants_camera = True

    def __init__(self, banks=None, center=(0.0, 0.0), r0=60.0, r1=900.0, y=24.0, thick=14.0, count=520,
                 per=26, gain=None, seed=11, warm="#ffd08a", rose="#ff9eb0", lilac="#b89cff", core="#fff1d8",
                 sun_az=180.0, alpha=0.06, drift=(0.8, 0.0, 0.0)):
        rng = np.random.default_rng(seed)
        if banks is None:
            banks = []
            for _ in range(count):
                a = rng.uniform(0.0, TAU)
                r = np.sqrt(rng.uniform(r0 * r0, r1 * r1))
                s = rng.uniform(26.0, 60.0) * (0.6 + 0.6 * r / r1)
                banks.append(dict(center=(center[0] + np.sin(a) * r, y + rng.uniform(-0.3, 0.5) * thick,
                                          center[1] + np.cos(a) * r),
                                  size=(s, thick * rng.uniform(0.6, 1.3), s * rng.uniform(0.6, 1.0)), n=per))
        P, S, M, K, B = [], [], [], [], []
        for b in banks:
            n = int(b.get("n", per))
            cx, cy, cz = b["center"]
            sx, sy, sz = b["size"]
            # a billow: a few round lobes, puffs crowded toward each lobe's middle, the base flatter
            lobes = rng.normal(0.0, 0.42, (5, 3)) * np.array([1.0, 0.35, 1.0])
            lobes[:, 1] = np.abs(lobes[:, 1])
            li = rng.integers(0, 5, n)
            g = rng.normal(0.0, 0.28, (n, 3))
            p = lobes[li] + g
            p[:, 1] = np.abs(p[:, 1]) * 0.9
            P.append(np.array([cx, cy, cz]) + p * np.array([sx, sy, sz]))
            r = np.linalg.norm((p - lobes[li]) / 0.5, axis=1)
            S.append(sx * (0.22 + 0.16 * rng.random(n)) * (1.0 - 0.3 * np.clip(r, 0, 1)))
            M.append(np.exp(-1.6 * r * r))                      # 1 at a lobe's heart
            K.append(p[:, 1] / max(float(np.max(p[:, 1])), 1e-6))  # 0 at the base, 1 at the top
            B.append(np.full(n, float(b.get("bright", 1.0))))
        self.pos = np.concatenate(P)
        self.size = np.concatenate(S)
        self.inner = np.concatenate(M)
        self.top = np.concatenate(K)
        self.bright = np.concatenate(B)
        n = len(self.pos)
        self.seed = rng.random(n)
        self.mix = rng.random(n)
        a = np.radians(sun_az)
        self.sun_dir = np.array([np.sin(a), 0.0, np.cos(a)])
        side = ((self.pos - self.pos.mean(0)) @ self.sun_dir)
        self.sunny = ss(-1.0, 1.0, side / (np.std(side) + 1e-6))
        self._gain = gain
        self.alpha = alpha
        self.drift = np.asarray(drift, np.float64)
        warm, rose, lilac, core = (lin(c) for c in (warm, rose, lilac, core))
        edge = rose[None] * (1.0 - self.mix[:, None]) + lilac[None] * self.mix[:, None]
        lit = warm[None] * self.sunny[:, None] + edge * (1.0 - self.sunny[:, None])
        rim = lit * (0.55 + 0.45 * self.top[:, None])
        self.color = core[None] * self.inner[:, None] + rim * (1.0 - self.inner[:, None])

    def gain(self, t):
        return 1.0 if self._gain is None else float(self._gain(t))

    def sample(self, t, cam=None):
        g = self.gain(t)
        if g <= 0.002:
            return None
        pos = self.pos + self.drift[None] * t
        al = self.alpha * (0.35 + 0.9 * self.inner) * self.bright * g
        size = self.size
        if cam is not None:
            e = np.asarray(cam.pos, np.float64)
            d = pos - e
            dist = np.linalg.norm(d, axis=1)
            f = np.asarray(cam.target, np.float64) - e
            f = f / max(float(np.linalg.norm(f)), 1e-9)
            ahead = d @ f
            keep = ahead > -0.6 * size
            # a puff that would fill the picture thins away (the camera can fly through the cloud)
            near = ss(0.8, 2.6, dist / np.maximum(size, 1e-3))
            al = al * near
            keep &= al > 1e-4
            pos, size, al = pos[keep], size[keep], al[keep]
            col, seed = self.color[keep], self.seed[keep]
        else:
            col, seed = self.color, self.seed
        if len(pos) == 0:
            return None
        return dict(pos=pos, size=size, color=col, alpha=al, kind="soft", dof=0.0, fog=0.15, seed=seed,
                    streak=0.0, reflect=True)
