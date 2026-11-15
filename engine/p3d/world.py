"""The world of the 3D layer: sky, light, air and water as numbers that blend over time (looks), and the
world's own point sets (star dome, dust and bokeh lights, floating lanterns, the arch of nine lights).

A song gives P3D["world"] = dict(look=..., <any setting>=..., arch=dict(...), lanterns=dict(...), ...).

  look       the name of a look (LOOKS), or a list [(t, name), (t, name, blend seconds), ...]: at each time
             the world changes to that look over `blend` seconds (default 1.5; 0 is a cut, to hide in a burst
             of light). Looks blend setting by setting, so the sky, the sun's place and colour, the stars,
             the haze and the water all travel together.
  looks      your own looks: dict(name=dict(base="night", sky_top="#...", sun_el=4, ...))
  any setting of a look may also be given directly: a number, a colour, a Track or a function of time. It
  then replaces the look's value (stars=Track([...]), sun_az=lambda t: 180 + 4 * t, ...).

Settings (colours are display hex or linear triples; angles in degrees):
  sky_top, sky_mid, sky_hor     the sky from the zenith to the horizon
  sun_az, sun_el                where the sun (or moon) stands: azimuth from +z toward +x, elevation
  sun_color, sun_int            its colour and strength (0 = no sun)
  sun_size, sun_disc, sun_glow  radius of the disc in degrees, its strength, the width of its glow
  stars, milky                  the star dome and the Milky Way (0..1)
  clouds, cloud_speed           amount of cloud (0..1) and its drift
  hills, hill_height, hill_color   the three rings of far hills (0 hides them)
  haze, haze_color              the air: how fast things fade into the horizon colour
  mist, mist_height, mist_color    ground mist over the lake
  water, mirror, mirror_min, ripple   the lake: its own colour, the strength of the mirror, the mirror when
                                looking straight down, and how restless the surface is (0 = a perfect mirror)
  rays                          rays from the sun through hills, clouds and silhouettes (0 = off)
  dust, dust_color, dust_color2, bokeh     floating dust and the larger soft lights among it
  lanterns                      amount of lanterns rising into the sky (0..1)
  floats                        amount of small lights floating on the water (0..1)
  star_turn                     degrees the star dome has turned about its pole (world key star_pole=(az, el))
  exposure                      multiplies the picture's exposure (a Track gives flashes and dips)
  bokeh_ring, bokeh_hex         the look of out-of-focus discs: a brighter edge, and how hexagonal (0 round)
"""
import numpy as np

from .api import at, hash01, lin, ribbon

try:                                    # theme.py lives beside the engine; the day looks use its colours
    import theme as _theme
except Exception:                       # pragma: no cover  (p3d used on its own, without the engine)
    _theme = None


def _day(hexs, k):
    return (_theme.display(hexs) if _theme is not None else lin(hexs)) * k


COLOR_KEYS = ("sky_top", "sky_mid", "sky_hor", "sun_color", "haze_color", "hill_color", "water", "mist_color",
              "dust_color", "dust_color2", "lantern_color", "lantern_color2")
NUMBER_KEYS = ("sun_az", "sun_el", "sun_int", "sun_size", "sun_disc", "sun_glow", "stars", "milky", "clouds",
               "cloud_speed", "hills", "hill_height", "haze", "mist", "mist_height", "mirror", "mirror_min",
               "ripple", "rays", "dust", "bokeh", "lanterns", "floats", "exposure", "bokeh_ring", "bokeh_hex", "star_turn")

_NIGHT = dict(
    sky_top=lin("#01020a"), sky_mid=lin("#060b24"), sky_hor=lin("#16204c"),
    sun_az=180.0, sun_el=-12.0, sun_color=lin("#8ea4ff"), sun_int=0.10, sun_size=1.3, sun_disc=6.0, sun_glow=1.0,
    stars=1.0, milky=1.0, clouds=0.10, cloud_speed=1.0, hills=1.0, hill_height=1.0, hill_color=lin("#03040b"),
    haze=0.5, haze_color=lin("#18224e"), mist=0.35, mist_height=2.2, mist_color=lin("#1c2552"),
    water=lin("#010309"), mirror=1.0, mirror_min=0.55, ripple=0.7, rays=0.0,
    dust=0.6, dust_color=lin("#ffe2a8"), dust_color2=lin("#bcd0ff"), bokeh=0.7,
    lanterns=0.0, floats=0.0, lantern_color=lin("#ffb45e"), lantern_color2=lin("#ff8a4c"),
    exposure=1.0, bokeh_ring=0.5, bokeh_hex=0.0, star_turn=0.0,
)


def _look(base, **kw):
    d = dict(base)
    for k, v in kw.items():
        d[k] = lin(v) if isinstance(v, str) else v
    return d


LOOKS = {"night": _NIGHT}
LOOKS["dusk"] = _look(_NIGHT, sky_top="#050820", sky_mid="#221a48", sky_hor="#6e4263", sun_color="#ffa58c",
                      sun_int=0.34, sun_el=-7.0, stars=0.75, milky=0.5, clouds=0.25, haze_color="#5a3a60",
                      mist_color="#4a3560", hill_color="#06050f", water="#03030c")
LOOKS["predawn"] = _look(_NIGHT, sky_top="#080d2c", sky_mid="#33265c", sky_hor="#a85f6e", sun_color="#ffb48c",
                         sun_int=0.50, sun_el=-4.5, stars=0.60, milky=0.30, clouds=0.30, haze=0.6,
                         haze_color="#8c5568", mist=0.45, mist_color="#70495f", hill_color="#090712",
                         water="#04040e")
LOOKS["dawn"] = _look(_NIGHT, sky_top="#0f1b46", sky_mid="#553b7c", sky_hor="#e9836f", sun_color="#ffd08c",
                      sun_int=0.95, sun_el=-1.2, stars=0.30, milky=0.08, clouds=0.38, haze=0.7,
                      haze_color="#c97a6e", mist=0.55, mist_color="#a86a66", hill_color="#0e0a18", water="#06060f",
                      rays=0.35, dust_color="#ffd9a0", dust_color2="#ffc4b0")
LOOKS["sunrise"] = _look(_NIGHT, sky_top="#101f52", sky_mid="#6a3f7a", sky_hor="#e8854a", sun_color="#ffd89a",
                         sun_int=0.95, sun_el=5.5, stars=0.12, milky=0.0, clouds=0.50, haze=0.62,
                         haze_color="#a8623f", mist=0.28, mist_color="#96604a", hill_color="#120c1c",
                         water="#090811", rays=0.7, dust_color="#ffe2a8", dust_color2="#ffd0a8", sun_disc=8.0,
                         sun_glow=0.75, ripple=0.55, exposure=0.92)
LOOKS["golden"] = _look(_NIGHT, sky_top="#1c3a7c", sky_mid="#5e78b0", sky_hor="#e0bb96", sun_color="#fff2d8",
                        sun_int=0.85, sun_el=11.0, stars=0.0, milky=0.0, clouds=0.35, haze=0.6,
                        haze_color="#b8a394", mist=0.30, mist_color="#b9a898", hill_color="#2a3350",
                        water="#0c1322", rays=0.30, dust_color="#fff0d0", dust_color2="#ffe0b8", sun_glow=0.7)
LOOKS["day"] = _look(_NIGHT, sky_top=_day("#6fb6ea", 0.90), sky_mid=_day("#a9d4f4", 0.84), sky_hor=_day("#f2ead8", 0.60),
                     sun_color=_day("#fff6e2", 0.22), sun_int=0.8, sun_el=34.0, stars=0.0, milky=0.0, clouds=0.30,
                     haze=0.6, haze_color=_day("#dfe6ea", 0.50), mist=0.18, mist_color=_day("#eeeae2", 0.50),
                     hill_color=_day("#6f93b3", 0.50), water=_day("#4d8fc4", 0.45), mirror_min=0.45, rays=0.12,
                     dust=0.4, dust_color="#fff8ec", dust_color2="#ffd27a", sun_disc=2.5, sun_glow=0.6)
LOOKS["cream"] = _look(LOOKS["day"], sky_top=_day("#a9d2f0", 0.90), sky_mid=_day("#f3e6d4", 0.80),
                       sky_hor=_day("#fbf0e0", 0.66), haze_color=_day("#f0e6d8", 0.55),
                       hill_color=_day("#a9c0d4", 0.55), water=_day("#93bfe0", 0.50), sun_el=40.0)


def _smoother(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def _value(v, t):
    v = v(t) if callable(v) else v
    if isinstance(v, str):
        return lin(v)
    return np.asarray(v, dtype=np.float64) if isinstance(v, (tuple, list, np.ndarray)) else float(v)


class World:
    def __init__(self, cfg=None):
        cfg = dict(cfg or {})
        self.looks = dict(LOOKS)
        for name, d in (cfg.pop("looks", None) or {}).items():
            d = dict(d)
            base = self.looks[d.pop("base", "night")]
            self.looks[name] = _look(base, **d)
        look = cfg.pop("look", "night")
        self.keys = [(0.0, look, 0.0)] if isinstance(look, str) else [
            (float(k[0]), k[1], float(k[2]) if len(k) > 2 else 1.5) for k in sorted(look, key=lambda k: k[0])]
        for _, name, _ in self.keys:
            if name not in self.looks:
                raise ValueError(f"P3D world: unknown look {name!r} (known: {sorted(self.looks)})")
        self.arch = cfg.pop("arch", None)
        self.lantern_cfg = cfg.pop("lantern_field", None) or {}
        self.float_cfg = cfg.pop("float_field", None) or {}
        self.dust_cfg = cfg.pop("dust_field", None) or {}
        self.shafts = list(cfg.pop("shafts", None) or [])
        self.light = cfg.pop("light", None)
        self.react = cfg.pop("react", None) or {}
        self.calm = cfg.pop("calm", None) or []
        self.lights = cfg.pop("lights", None) or []
        self.split = cfg.pop("split", None)
        pole = cfg.pop("star_pole", (0.0, 38.0))
        self.pole = np.array([np.sin(np.radians(pole[0])) * np.cos(np.radians(pole[1])), np.sin(np.radians(pole[1])),
                              np.cos(np.radians(pole[0])) * np.cos(np.radians(pole[1]))])
        unknown = set(cfg) - set(COLOR_KEYS) - set(NUMBER_KEYS)
        if unknown:
            raise ValueError(f"P3D world: unknown settings {sorted(unknown)}")
        self.over = cfg

    def state(self, t):
        """Every setting at t: the looks blended, then the song's own values."""
        s = dict(self.looks[self.keys[0][1]])
        for tk, name, w in self.keys[1:]:
            k = (1.0 if t >= tk else 0.0) if w <= 0.0 else _smoother((t - (tk - 0.5 * w)) / w)
            if k <= 0.0:
                break
            b = self.looks[name]
            if k >= 1.0:
                s = dict(b)
            else:
                s = {key: s[key] * (1.0 - k) + b[key] * k for key in s}
        for key, v in self.over.items():
            s[key] = _value(v, t)
        return self._finish(s)

    @staticmethod
    def _finish(s):
        el, az = np.radians(s["sun_el"]), np.radians(s["sun_az"])
        s["sun_dir"] = np.array([np.sin(az) * np.cos(el), np.sin(el), np.cos(az) * np.cos(el)])
        return s

    def state_of(self, look, t):
        """The settings of one look at t: a name, a dict(base=name, <settings>), or a function of t giving either."""
        look = look(t) if callable(look) else look
        if isinstance(look, str):
            s = dict(self.looks[look])
        else:
            d = dict(look)
            s = dict(self.looks[d.pop("base", "night")])
            for key, v in d.items():
                s[key] = _value(v, t)
        return self._finish(s)

    def calm_at(self, t):
        """Discs of the lake with their own ripple and mirror: world key
        calm=[dict(center=(x, z), radius, soft=None, ripple=0.0, mirror=1.0)] (each value may be a function of
        time, and so may the whole list): glass in a storm, or a storm on glass. Up to four."""
        a, b = np.zeros((4, 4), "f4"), np.zeros((4, 4), "f4")
        items = self.calm(t) if callable(self.calm) else self.calm
        n = 0
        for it in list(items)[:4]:
            c = it["center"](t) if callable(it["center"]) else it["center"]
            r = float(it["radius"](t) if callable(it["radius"]) else it["radius"])
            if r <= 0.0:
                continue
            soft = it.get("soft", None)
            soft = 0.25 * r if soft is None else float(soft(t) if callable(soft) else soft)
            rp, mr = it.get("ripple", 0.0), it.get("mirror", 1.0)
            a[n] = (c[0], c[1], r, max(soft, 0.01))
            b[n] = (float(rp(t) if callable(rp) else rp), float(mr(t) if callable(mr) else mr), 0.0, 0.0)
            n += 1
        return a, b, n

    def lights_at(self, t):
        """The moving coloured lights: world key lights=[dict(pos, color, strength=1.0, radius=3.0)] (values or
        functions of time). They glow in the mist, lay a pool on the water and colour the points of batches
        with `lit`. Up to four."""
        p, c = np.zeros((4, 4), "f4"), np.zeros((4, 3), "f4")
        n = 0
        for it in list(self.lights)[:4]:
            k = it.get("strength", 1.0)
            k = float(k(t) if callable(k) else k)
            if k <= 0.0005:
                continue
            pos = it["pos"](t) if callable(it["pos"]) else it["pos"]
            col = it.get("color", "#ffffff")
            col = col(t) if callable(col) else col
            col = lin(col) if isinstance(col, str) else np.asarray(col, np.float64)
            r = it.get("radius", 3.0)
            p[n] = (pos[0], pos[1], pos[2], float(r(t) if callable(r) else r))
            c[n] = col * k
            n += 1
        return p, c, n

    def split_at(self, t, w):
        """A sky of two looks: world key split=dict(look=..., toward=azimuth, soft=0.35, amount=1.0): the half of
        the sky toward that azimuth (and the haze and hills there) takes the other look, with a soft seam
        between (night ahead, dawn behind). Returns the shader's (x, z, soft, amount) and the other colours."""
        sp = self.split
        if not sp:
            return (0.0, 1.0, 0.3, 0.0), {}
        amt = sp.get("amount", 1.0)
        amt = float(amt(t) if callable(amt) else amt)
        if amt <= 0.0005:
            return (0.0, 1.0, 0.3, 0.0), {}
        az = sp.get("toward", 0.0)
        az = np.radians(float(az(t) if callable(az) else az))
        b = self.state_of(sp["look"], t)
        b["_stars"] = float(b["stars"]) / max(float(w["stars"]), 1e-3)
        return (float(np.sin(az)), float(np.cos(az)), float(sp.get("soft", 0.35)), amt), b

    def dome_rot(self, w):
        """The turn of the star dome about its pole (a 3 x 3 matrix)."""
        a = np.radians(float(w.get("star_turn", 0.0)))
        if a == 0.0:
            return np.eye(3)
        k = self.pole
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)


# ---------------------------------------------------------------------------------------------------------
# The world's own point sets. Each takes the World and reads the frame's state through world.now (set by the
# layer before the sets are sampled), so their colours and amounts follow the looks.
# ---------------------------------------------------------------------------------------------------------
MILKY_N = np.array([0.52, 0.36, 0.775]) / np.linalg.norm([0.52, 0.36, 0.775])   # the normal of the Milky Way's plane


class Stars:
    """Thousands of stars on a dome, denser along the Milky Way. Positions are directions (the renderer puts
    them far away round the camera)."""
    static = True
    dome = True
    turns = True          # the dome turns with the world setting star_turn

    def __init__(self, world, n=14000, seed=11):
        self.world = world
        rng = np.random.default_rng(seed)
        n_band = int(n * 0.42)
        d = rng.normal(size=(n - n_band, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        d[:, 1] = np.abs(d[:, 1])
        # the band: directions close to the great circle whose normal is MILKY_N
        a = rng.random(n_band) * 2 * np.pi
        e1 = np.cross(MILKY_N, [0.0, 1.0, 0.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(MILKY_N, e1)
        off = rng.normal(size=n_band) * 0.11
        b = np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2 + off[:, None] * MILKY_N
        b /= np.linalg.norm(b, axis=1, keepdims=True)
        b[:, 1] = np.abs(b[:, 1])
        self.dir = np.concatenate([d, b]).astype(np.float32)
        mag = rng.random(n) ** 4
        mag[n - n_band:] *= 0.5                                    # the band is a dust of faint stars
        self.size = (0.0009 + 0.0026 * mag).astype(np.float32)     # angular diameter in radians
        tint = rng.random(n)
        col = np.stack([0.80 + 0.20 * tint, 0.86 + 0.10 * tint, 1.0 - 0.22 * tint], axis=1)
        self.color = col.astype(np.float32)
        self.alpha = (0.75 + 7.0 * mag).astype(np.float32)
        self.seed = rng.random(n).astype(np.float32)
        self.bright = np.argsort(mag)[-max(n // 110, 8):]             # the brightest carry a fine glint

    def sample(self, t):
        b = self.bright
        return [dict(pos=self.dir, size=self.size, color=self.color, alpha=self.alpha, seed=self.seed,
                     kind="soft", twinkle=0.55, fog=0.0, streak=0.3),
                dict(pos=self.dir[b], size=self.size[b] * 1.5, color=self.color[b], alpha=self.alpha[b] * 0.7,
                     seed=self.seed[b], kind="spark", twinkle=0.4, fog=0.0, streak=0.3)]

    def gain(self, t):
        return float(self.world.now["stars"])


class SunGlow:
    """The sun's own bloom: one soft light on the dome where the sun stands (hills and clouds hide it)."""
    dome = True

    def __init__(self, world):
        self.world = world

    def sample(self, t):
        s = self.world.now
        k = float(s["sun_int"]) * min(max((s["sun_el"] + 2.5) / 3.0, 0.0), 1.0)
        if k <= 0.001:
            return None
        return dict(pos=s["sun_dir"][None, :], size=0.060, color=np.asarray(s["sun_color"]), alpha=min(k, 2.0) * 0.6,
                    kind="soft", fog=0.0, dof=0.0, lod=False, streak=False)


class Dust:
    """Dust in the air round the camera, and larger soft lights among it (the foreground bokeh). The dust is
    fixed in the world: the camera flies through it, and a box of it always surrounds the camera."""
    wants_camera = True

    def __init__(self, world, n=7000, n_bokeh=300, seed=21, box=(38.0, 22.0, 38.0), bokeh_box=(64.0, 22.0, 64.0)):
        self.world = world
        rng = np.random.default_rng(seed)
        self.sets = []
        for count, bx, kind in ((n, box, 0), (n_bokeh, bokeh_box, 1)):
            sd = rng.random((count, 3))
            ph = rng.random((count, 3)) * 6.2832
            b = rng.random(count)
            if kind == 0:
                size = 0.010 + 0.022 * b ** 2
                alpha = 0.15 + 0.50 * rng.random(count)
                emit = 1.0 + 3.0 * (rng.random(count) > 0.95)
            else:
                size = 0.05 + 0.09 * b
                alpha = 0.40 + 0.40 * rng.random(count)
                emit = 2.0 + 3.0 * rng.random(count) ** 2
            self.sets.append(dict(sd=sd, ph=ph, box=np.asarray(bx), size=size.astype(np.float32),
                                  alpha=alpha.astype(np.float32), emit=emit.astype(np.float32),
                                  mix=rng.random(count), seed=rng.random(count).astype(np.float32),
                                  drift=np.array([0.10, 0.05, 0.06]) * (1.0 if kind == 0 else 0.7)))

    def sample(self, t, cam):
        s = self.world.now
        out = []
        cp = np.asarray(cam.pos, np.float64)
        for k, d in enumerate(self.sets):
            amt = float(s["dust"] if k == 0 else s["bokeh"] * min(s["dust"] * 2.0, 1.0))
            if amt <= 0.001:
                continue
            B = d["box"]
            w = d["sd"] * B + d["drift"] * t + 0.35 * np.sin(t * 0.21 + d["ph"])
            rel = np.empty_like(w)
            for ax in (0, 2):                                  # a box of dust always round the camera
                rel[:, ax] = (np.mod((w[:, ax] - cp[ax]) / B[ax] + 0.5, 1.0) - 0.5) * B[ax]
            y = np.mod(w[:, 1], B[1])
            pos = np.stack([cp[0] + rel[:, 0], y, cp[2] + rel[:, 2]], axis=1)
            fx = np.clip((0.5 - np.abs(rel[:, 0]) / B[0]) / 0.12, 0.0, 1.0)
            fz = np.clip((0.5 - np.abs(rel[:, 2]) / B[2]) / 0.12, 0.0, 1.0)
            fy = np.clip(y / 0.4, 0.0, 1.0) * np.clip((B[1] - y) / 4.0, 0.0, 1.0)
            # nothing flashes past right at the lens: the dust fades in from a little way off
            dist = np.sqrt(rel[:, 0] ** 2 + rel[:, 2] ** 2 + (y - cp[1]) ** 2)
            fy = fy * (np.clip((dist - 1.0) / 2.5, 0.0, 1.0) if k == 0 else np.clip((dist - 3.0) / 5.0, 0.0, 1.0))
            col = np.asarray(s["dust_color"])[None, :] * (1 - d["mix"][:, None] * 0.6) + np.asarray(
                s["dust_color2"])[None, :] * (d["mix"][:, None] * 0.6)
            out.append(dict(pos=pos, size=d["size"], color=col, alpha=d["alpha"] * fx * fz * fy * amt,
                            emit=d["emit"], seed=d["seed"], kind="soft", twinkle=0.5 if k == 0 else 0.25,
                            backlight=0.7, streak=0.15, reflect=(k == 1)))
        return out


class Floats:
    """Small lights floating on the water, in a ring round `center` (candles set on the lake). Close to the
    surface, so each sits on its own mirror image; a low camera rushes past them."""

    def __init__(self, world, count=700, center=(0.0, 0.0), radius=(10.0, 170.0), size=0.16, seed=37):
        self.world = world
        rng = np.random.default_rng(seed)
        r = np.sqrt(rng.random(count) * (radius[1] ** 2 - radius[0] ** 2) + radius[0] ** 2)
        a = rng.random(count) * 2 * np.pi
        self.base = np.stack([center[0] + r * np.sin(a), center[1] + r * np.cos(a)], axis=1)
        self.rank = rng.permutation(count) / float(count)
        self.seed = rng.random(count).astype(np.float32)
        self.size = (size * (0.7 + 0.6 * rng.random(count))).astype(np.float32)
        self.mix = rng.random(count)
        self.ph = rng.random((count, 2)) * 6.2832

    def sample(self, t):
        s = self.world.now
        amt = float(s["floats"])
        if amt <= 0.001:
            return None
        vis = np.clip((amt - self.rank) / 0.08, 0.0, 1.0)
        keep = vis > 0.002
        if not np.any(keep):
            return None
        x = self.base[keep, 0] + 0.25 * np.sin(t * 0.17 + self.ph[keep, 0])
        z = self.base[keep, 1] + 0.25 * np.sin(t * 0.13 + self.ph[keep, 1])
        y = 0.16 + 0.03 * np.sin(t * 0.9 + self.ph[keep, 0])
        pos = np.stack([x, y, z], axis=1)
        mix = self.mix[keep, None]
        col = np.asarray(s["lantern_color"])[None, :] * (1 - mix) + np.asarray(s["lantern_color2"])[None, :] * mix
        flick = 0.8 + 0.2 * np.sin(t * (6.0 + 5.0 * self.seed[keep]) + self.seed[keep] * 70.0)
        a = (vis[keep] * flick).astype(np.float32)
        return [dict(pos=pos, size=self.size[keep] * 2.2, color=col, alpha=a * 0.45, kind="soft", seed=self.seed[keep]),
                dict(pos=pos, size=self.size[keep] * 0.5, color=col * 0.5 + 0.5, alpha=a, emit=3.0, kind="soft",
                     seed=self.seed[keep])]


class Lanterns:
    """Lanterns floating up from the lake: warm paper lights rising in a ring round `center`."""

    def __init__(self, world, count=420, center=(0.0, 0.0), radius=(6.0, 70.0), height=46.0, speed=(0.45, 0.95),
                 size=0.5, seed=31):
        self.world = world
        rng = np.random.default_rng(seed)
        r = np.sqrt(rng.random(count) * (radius[1] ** 2 - radius[0] ** 2) + radius[0] ** 2)
        a = rng.random(count) * 2 * np.pi
        self.base = np.stack([center[0] + r * np.sin(a), center[1] + r * np.cos(a)], axis=1)
        self.speed = speed[0] + (speed[1] - speed[0]) * rng.random(count)
        self.phase = rng.random(count)
        self.sway = rng.random((count, 2)) * 6.2832
        self.rank = rng.permutation(count) / float(count)          # which lanterns come first as the amount rises
        self.size = (size * (0.75 + 0.5 * rng.random(count))).astype(np.float32)
        self.seed = rng.random(count).astype(np.float32)
        self.mix = rng.random(count)
        self.height = float(height)

    def sample(self, t):
        s = self.world.now
        amt = float(s["lanterns"])
        if amt <= 0.001:
            return None
        H = self.height
        y = np.mod(self.phase * H + self.speed * t, H)
        vis = np.clip((amt - self.rank) / 0.08, 0.0, 1.0) * np.clip(y / 1.2, 0.0, 1.0) * np.clip((H - y) / (0.18 * H), 0.0, 1.0)
        keep = vis > 0.002
        if not np.any(keep):
            return None
        x = self.base[:, 0] + 0.6 * np.sin(t * 0.23 + self.sway[:, 0]) + 0.03 * y * np.sin(self.sway[:, 1])
        z = self.base[:, 1] + 0.6 * np.sin(t * 0.19 + self.sway[:, 1]) + 0.03 * y * np.cos(self.sway[:, 0])
        pos = np.stack([x, y + 0.4, z], axis=1)[keep]
        mix = self.mix[keep, None]
        col = np.asarray(s["lantern_color"])[None, :] * (1 - mix) + np.asarray(s["lantern_color2"])[None, :] * mix
        flick = 0.85 + 0.15 * np.sin(t * (5.0 + 4.0 * self.seed[keep]) + self.seed[keep] * 60.0)
        a = (vis[keep] * flick).astype(np.float32)
        vel = np.stack([np.zeros(keep.sum()), self.speed[keep], np.zeros(keep.sum())], axis=1)
        body = dict(pos=pos, size=self.size[keep], color=col, alpha=a * 0.85, kind="soft", seed=self.seed[keep],
                    lod=False, vel=vel)
        core = dict(pos=pos - np.array([0.0, 0.08, 0.0]), size=self.size[keep] * 0.30, color=col * 0.6 + 0.4,
                    alpha=a, emit=3.2, kind="soft", seed=self.seed[keep], lod=False, vel=vel)
        return [body, core]


def _tv(v, t):
    return v(t) if callable(v) else v


def arch_points(span=22.0, height=13.0, z=0.0, n=9, center=(0.0, 0.0, 0.0), yaw=0.0):
    """Where the nine lights stand: an arc (half an ellipse) over the lake, feet near the water. center moves
    the whole arch, yaw (degrees) turns it about the vertical."""
    th = np.radians(np.linspace(172.0, 8.0, n))
    x, y = 0.5 * span * np.cos(th), height * np.sin(th)
    a = np.radians(yaw)
    c = np.asarray(center, np.float64)
    return np.stack([c[0] + x * np.cos(a), c[1] + y, c[2] + z - x * np.sin(a)], axis=1)


class Arch:
    """The arch of nine lights as a real arc in space. Each light can be lit at its own time.

    lit       nine times in seconds (None: never lit, a negative time: lit from the start), or a function
              t -> nine (brightness, age in seconds) pairs. Without it the song's own arch timing is used.
    span, height, center, yaw   the size, place and turn of the arch: numbers or functions of time
    colors    (lights, line) as before, or nine colours, one for each light
    line      0..1 (or a function of time): the arc itself and the lines between lit lights; the lights
              keep their own brightness, so the line can be drawn after them or left out
    travel    dict(start=(9, 3) points or one point, t=nine arrival times or one, dur=1.5): each light
              flies from its start to its place on the arch, arriving at its time
    A song file can read the geometry: Arch(None, **settings).positions(t) gives the nine places at t, and
    point(u, t) any place along the arc (u from 0 at the first light's foot to 1 at the ninth's).
    """

    def __init__(self, world, span=22.0, height=13.0, z=0.0, lit=None, colors=("#fff3d6", "#ffc2a4"), bright=1.0,
                 dust=7000, seed=41, pulse=0.0, center=(0.0, 0.0, 0.0), yaw=0.0, line=1.0, travel=None):
        self.world = world
        self.span, self.height, self.z, self.center, self.yaw, self.line = span, height, float(z), center, yaw, line
        self.lit = lit
        self.song_state = None               # set each frame by the layer when lit is None
        cols = [lin(c) if isinstance(c, str) else np.asarray(c, np.float64) for c in colors]
        if len(cols) == 9:
            self.cols = np.array(cols) * bright
            self.colB = self.cols.mean(axis=0)
        else:
            self.cols = np.tile(cols[0] * bright, (9, 1))
            self.colB = cols[1] * bright
        self.colA = self.cols.mean(axis=0)
        self.pulse = pulse
        self.beat = 0.0                      # set each frame by the layer (world react: the lights pulse on the beat)
        self.travel = travel
        rng = np.random.default_rng(seed)
        self.du = rng.random(dust)
        self.djit = rng.normal(size=(dust, 3)) * 0.10
        self.dsize = (0.022 + 0.05 * rng.random(dust) ** 3).astype(np.float32)
        self.dseed = rng.random(dust).astype(np.float32)
        self.dspeed = 0.004 + 0.010 * rng.random(dust)
        m = 70
        self.oa = rng.random((9, m)) * 6.2832
        self.ow = (0.5 + 1.4 * rng.random((9, m))) * np.where(rng.random((9, m)) > 0.5, 1.0, -1.0)
        self.orad = 0.45 + 1.25 * rng.random((9, m)) ** 1.5
        ax = rng.normal(size=(9, m, 3))
        ax /= np.linalg.norm(ax, axis=2, keepdims=True)
        e1 = np.cross(ax, [0.0, 1.0, 0.0])
        e1 /= np.maximum(np.linalg.norm(e1, axis=2, keepdims=True), 1e-6)
        self.e1, self.e2 = e1, np.cross(ax, e1)
        self.oseed = rng.random((9, m)).astype(np.float32)
        self.osize = (0.035 + 0.06 * rng.random((9, m)) ** 2).astype(np.float32)

    def point(self, u, t=0.0):
        """The point of the arc at u (0 at the first light's end, 1 at the ninth's) at time t."""
        th = np.radians(172.0 - 164.0 * np.asarray(u))
        x, y = 0.5 * float(_tv(self.span, t)) * np.cos(th), float(_tv(self.height, t)) * np.sin(th)
        a = np.radians(float(_tv(self.yaw, t)))
        c = np.asarray(_tv(self.center, t), np.float64)
        return np.stack([c[0] + x * np.cos(a), c[1] + y, c[2] + self.z - x * np.sin(a)], axis=-1)

    def homes(self, t=0.0):
        """The nine places on the arch at t."""
        return self.point(np.linspace(0.0, 1.0, 9), t)

    def positions(self, t=0.0):
        """Where the nine lights are at t (on their way while they travel, then at their places)."""
        P = self.homes(t)
        tr = self.travel
        if tr:
            start = np.broadcast_to(np.asarray(_tv(tr["start"], t), np.float64), (9, 3))
            ta = np.broadcast_to(np.asarray(tr.get("t", 0.0), np.float64), (9,))
            u = np.clip((t - (ta - float(tr.get("dur", 1.5)))) / float(tr.get("dur", 1.5)), 0.0, 1.0)
            u = 1.0 - (1.0 - u) ** 3
            P = start + (P - start) * u[:, None]
        return P

    def states(self, t):
        """Nine (brightness, age) pairs at t."""
        if callable(self.lit):
            return [(float(a), float(b)) for a, b in self.lit(t)]
        if self.lit is None:
            st = self.song_state or [(0.0, -1.0)] * 9
            return [(float(s[0]), float(s[1])) for s in st]
        out = []
        for tl in self.lit:
            if tl is None:
                out.append((0.0, -1.0))
                continue
            age = t - float(tl)
            if age < -0.35:
                out.append((0.0, -1.0))
                continue
            gather = min(max((age + 0.35) / 0.35, 0.0), 1.0)
            flash = 1.5 * np.exp(-max(age, 0.0) * 1.2) if age >= 0 else 0.0
            out.append((0.60 * gather + flash, max(age, 0.0)))
        return out

    def sample(self, t):
        st = self.states(t)
        inten = np.array([s[0] for s in st])
        age = np.array([s[1] for s in st])
        pulse = float(self.pulse(t)) if callable(self.pulse) else float(self.pulse)
        inten = inten * (1.0 + pulse + self.beat)
        line = float(_tv(self.line, t))
        out = []
        if line > 0.001:
            # the arc itself: a ghost of dust, glowing where its lights are lit
            u = np.mod(self.du + self.dspeed * t, 1.0)
            grid = np.linspace(0.0, 1.0, 9)
            lit_u = np.interp(u, grid, np.minimum(inten, 1.4))
            col = np.stack([np.interp(u, grid, self.cols[:, k]) for k in range(3)], axis=1) * 0.55 + self.colB * 0.45
            out.append(dict(pos=self.point(u, t) + self.djit, size=self.dsize, color=col,
                            alpha=((0.035 + 0.55 * lit_u) * line).astype(np.float32), seed=self.dseed, kind="soft",
                            twinkle=0.6))
        on = inten > 0.002
        if np.any(on):
            P = self.positions(t)[on]
            k = inten[on]
            cols = self.cols[on]
            out.append(dict(pos=P, size=0.95, color=cols, alpha=np.minimum(k, 1.6), emit=3.0, kind="spark",
                            seed=np.linspace(0.1, 0.9, 9)[on], lod=False))
            out.append(dict(pos=P, size=5.5, color=cols * 0.6 + self.colB * 0.4, alpha=0.085 * np.minimum(k, 2.0),
                            kind="soft", lod=False, dof=0.0))
            # sparks circling the lit lights; a newly lit light throws them outward
            burst = 1.0 + 2.6 * np.exp(-np.maximum(age[on], 0.0) * 1.4)
            ang = self.oa[on] + self.ow[on] * t
            rad = self.orad[on] * burst[:, None]
            op = P[:, None, :] + rad[:, :, None] * (np.cos(ang)[:, :, None] * self.e1[on] + np.sin(ang)[:, :, None] * self.e2[on])
            oa = np.minimum(k, 1.5)[:, None] * (0.35 + 0.65 * self.oseed[on])
            oc = np.repeat(cols[:, None, :], self.oa.shape[1], axis=1)
            out.append(dict(pos=op.reshape(-1, 3), size=self.osize[on].reshape(-1), color=oc.reshape(-1, 3),
                            alpha=oa.reshape(-1), emit=1.6, kind="soft", seed=self.oseed[on].reshape(-1), twinkle=0.7))
            # one line of light between neighbours that are both lit (a ribbon along the arc)
            if line > 0.001 and not self.travel:
                for i in range(8):
                    g = min(inten[i], inten[i + 1], 1.0)
                    if g > 0.01:
                        out.append(ribbon(self.point(np.linspace(i / 8.0, (i + 1) / 8.0, 13), t), width=0.16,
                                          color=0.5 * (self.cols[i] + self.cols[i + 1]) * 0.6 + self.colB * 0.4,
                                          alpha=g * 0.55 * line))
        return out
