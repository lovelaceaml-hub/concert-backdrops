"""The 3D layer's API for point sets (engine/p3d). Pure numpy: nothing here needs a graphics context, so a
point set can be built and tested on its own (see `python engine/p3d/api.py`).

CONVENTIONS
  Units       metres. A person is about 1.7 m tall.
  Axes        right handed, y up. The lake surface is the plane y = 0. The arch of nine lights stands over the
              origin in the plane z = 0, its span along x. Its front faces +z: the default camera stands at
              positive z and looks toward negative z.
  Azimuth     degrees, measured around the y axis from +z toward +x: az 0 is at +z, az 90 at +x.
              `at(az, dist, height)` gives the point.
  Time        t is song time in seconds. Everything is a pure function of t (and of the camera at t): no state
              carried from frame to frame, so any part of a video renders the same frames.
  Light       colours are linear light, added to the engine's HDR light buffer (bloom, then the filmic curve).
              A colour around 1.0 is a clearly bright light; `emit` multiplies it for glints that bloom.
              `lin("#ffd27a")` turns a display hex colour into linear light. `show("#f0566a")` gives the light
              that the finished picture shows as exactly that colour (for `paint`).
  Size        the diameter of a sprite in metres (in focus). The renderer keeps the energy of a point when
              it is smaller than a pixel or spread by depth of field, so sizes are physical, not pixels.

A POINT SET
  Any object with `sample(t)` that returns one batch (a dict) or a list of batches. A batch:

    pos      (N, 3) float   positions in metres                                         required
    size     (N,) or number diameter in metres (for "line": the width; hairline when small)   default 0.02
    color    (N, 3) or (3,) linear light                                                default (1, 1, 1)
    alpha    (N,) or number 0..1, multiplies the light                                  default 1
    kind     one of KINDS   how each point is drawn (one kind per batch)                default "soft"
    pos2     (N, 3)         the other end of each segment                               "line", "ribbon"
    alpha2   (N,)           alpha at the pos2 end (tapered trails)                      default alpha
    size2    (N,)           width at the pos2 end (tapering ribbons)                    default size
    u, u2    (N,)           a place along the path at each end (metres along a ribbon, or any measure):
                            `pulse` travels along it                                    default 0
    rot      (N,) or (N, 2) radians: turn in the picture plane; second column: tumble   "flake", "petal", "bird"
    emit     (N,) or number extra brightness (HDR), for glints                          default 1
    normal   (N, 3)         unit surface normals; needed for `rim` and `lit`            optional
    seed     (N,)           0..1 per point, drives the twinkle (default: a hash of the index)
    vel      (N, 3)         metres per second; with motion blur the sprite is stretched along it
    birth    (N,)           the time in seconds at which each point appears (it stays dark before); works on
                            static sets too, so a million points can light up in any order    default: always there

  and per batch settings (numbers, all optional):

    twinkle  0..1   how strongly each point shimmers over time (glitter)                default 0
    rim      (strength 0..1, power): light only where the surface turns away from the camera, so a body shows
             as a bright edge with a dark inside (needs `normal`)                       default (0, 2)
    dof      how much of the lens blur the batch takes: True or 1 all of it, False or 0 none (drawn sharp
             whatever the focus), a number between eases from bokeh to sharp            default True
    fog      how much of the haze the batch takes (True, False or 0..1)                 default True
    reflect  False keeps the batch out of the lake mirror                               default True
    lod      False keeps every point even when very out of focus (see Scene.add)        default True
    backlight  0..1: the points glow more when the sun (or the world's light) stands behind them as seen
             from the camera, like dust in a ray of light                               default 0
    streak   how much of the motion blur the batch takes (True, False or 0..1): a moving point, or any
             point while the camera moves fast, is drawn out into a streak            default True
    fade     seconds a point takes to appear at its `birth`                             default 0.4
    flash    extra brightness of a point just born (it flares, then settles)            default 0
    pulse    (speed, length, gain, period): a brighter stretch `length` long travels along `u` at `speed`
             (units of u per second), every `period` units; for lines and ribbons       default off
    paint    0..1: also paint the points in their true colour over the scene, under their light. Light
             alone can only brighten what is behind it, so on a bright day sky a coloured point pales
             to white; a painted point shows its `color` exactly (give it with `show("#hex")`)   default 0
    paint_light  the share of its own light a painted batch keeps                       default 0.3
    lit      0..1: how much the points take the colour of the world's moving lights (world `lights`);
             with `normal` only the side turned toward a light                          default 0
    clear    False lets the batch into the keep-clear boxes (P3D `clear`), for example the words
             the box was made for                                                       default True

  READING MOMENTS (words made of points). A point exactly on the focus plane has no lens blur at all, and a
  point smaller than a pixel is drawn through a fixed small footprint whose light does not change as it moves
  across the pixel grid, so tens of thousands of small points stay steady and legible. For words that must be
  sharp wherever the focus is, give the batch dof=0 (and fog=0 to keep them clear of the haze) for the reading
  moment; both may change over time, so words can come out of bokeh, hold sharp, and return to it.

  A point set may also have these attributes:
    wants_camera = True   sample is then called as sample(t, cam) with a CameraState (for effects that depend
                          on the view, for example dispersing away from the camera)
    static = True         sample(0.0) is called once and the points stay on the graphics card (stars, dust);
                          `birth`, `pulse`, twinkle and gain still run on them
    dome = True           the positions are directions on the sky (unit vectors): the set is drawn far away
                          round the camera, behind the hills and clouds (stars); size is then an angle in radians
    gain(t) -> number     a brightness for the whole set at t (cheap fades; works with static sets)

KINDS
  "soft"    a round soft point of light (the default; out of focus it becomes a bokeh disc)
  "spark"   a bright core with a fine four-point glint that twinkles
  "disc"    a flat dot with a crisp edge (dotted colour bodies)
  "flake"   an irregular shard that turns and tumbles (dissolving bodies)
  "petal"   a petal shape that turns and tumbles
  "bird"    a small pair of wings; rot is the heading in the picture plane, the wings beat with seed and time
  "heart"   a heart (engine/p3d/brand_hearts.py): sharp, a crisp heart that turns (rot[:, 0]) and tumbles (rot[:, 1]);
            out of focus, a heart-shaped bokeh disc
  "line"    a straight segment from pos to pos2 (plexus lines); size is its width in metres, never thinner
            than a hairline on screen. Tens of thousands are fine; they take the lens blur and are cut
            cleanly where they pass the camera
  "ribbon"  a soft band from pos to pos2, width size to size2, alpha to alpha2. Segments that share their
            ends join into one continuous band (no beads): build one with `ribbon(points, ...)` or `Trail`

THE SCENE
  scene.add(name, pointset, reflect=True, depth_of_field=True, mask=None, fog=True, lod=True, window=False)
  scene.remove(name), scene.names(), scene.get(name)

  A song file reaches the scene through its P3D key:

      import p3d
      def build(scene):
          scene.add("walker", MyBody(...))
      P3D = dict(camera=..., world=dict(...), setup=build)      # see engine/UPGRADE-HOWTO.md, section V

THE MASK PASS (dark bodies, double exposures, windows onto another world)
  scene.add("profile", body, mask=Mask("dark"))            the silhouette of the set dims every light and the
                                                           sky BEHIND it (by depth): a dark body with a rim
  scene.add("profile", body, mask=Mask("sky", sky="sunrise"))   the silhouette is filled with a sky picture
                                                           (clouds, a sunrise, stars): a double exposure
  scene.add("profile", body, mask=Mask("sky", sky="world", look="day"))   the silhouette is a window onto the
                                                           same world, on the same camera, in another look
                                                           (its own sky, sun, hills and lake)
  scene.add("flock", birds, window=True)                   a set that lives inside the windows: it is drawn
                                                           only where a "sky" silhouette is
  The silhouette is drawn from the set's own points, each grown by Mask.grow metres so the cloud closes into
  a solid shape, then softened. Mask.source gives another point set for the shape (for example the whole body
  while the visible points are already dispersing). Mask.strength may be a function of t.

MOVING FRAMES
  frame = Frame(origin=lambda t: (0, 0, -20 * t), yaw=lambda t: 10 * t)     a frame that travels and turns
  scene.add("rider", Parented(body, frame))                the set rides the frame (positions, normals, speeds)
  Rig([...], parent=frame)                                 so does the camera (engine/p3d/camera.py)
"""
from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Union, runtime_checkable

import numpy as np

KINDS = ("soft", "spark", "disc", "flake", "petal", "bird", "line", "ribbon", "heart")
SEGMENT_KINDS = ("line", "ribbon")
MASK_MODES = ("dark", "sky")
MASK_SKIES = ("clouds", "sunrise", "stars", "day", "world", "flat")

_ARRAY_FIELDS = dict(pos=3, size=1, color=3, alpha=1, pos2=3, alpha2=1, size2=1, u=1, u2=1, rot=2, emit=1, normal=3,
                     seed=1, vel=3, birth=1)
_BATCH_SETTINGS = dict(twinkle=0.0, rim=(0.0, 2.0), dof=1.0, fog=1.0, reflect=True, lod=True, backlight=0.0,
                       streak=1.0, fade=0.4, flash=0.0, pulse=(0.0, 1.0, 0.0, 0.0), paint=0.0, paint_light=0.3,
                       lit=0.0, clear=True)
_AMOUNTS = ("twinkle", "dof", "fog", "backlight", "streak", "paint", "paint_light", "lit")


def lin(hexs):
    """A display hex colour as linear light (the same curve as song files use)."""
    h = hexs.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float64) ** 2.2


def show(hexs, exposure=1.0):
    """The linear light that the finished picture shows as exactly this display colour (the inverse of the
    engine's filmic curve; the same as theme.display). Use it for `paint` colours and sky colours."""
    y = np.clip(lin(hexs), 0.0, 0.975)
    a, b, c = 2.43 * y - 2.51, 0.59 * y - 0.03, 0.14 * y
    return (-b - np.sqrt(np.maximum(b * b - 4.0 * a * c, 0.0))) / (2.0 * a) / exposure


def at(az, dist, height=0.0):
    """The point at azimuth az (degrees from +z toward +x), dist metres from the y axis, height metres up."""
    a = np.radians(az)
    return np.array([np.sin(a) * dist, height, np.cos(a) * dist], dtype=np.float64)


def hash01(n, salt=0):
    """n reproducible numbers in 0..1 (a fixed hash of the index: the same on every machine and run)."""
    i = np.arange(n, dtype=np.uint64) + np.uint64((int(salt) * 0x9E3779B97F4A7C15) % (1 << 64))
    i = (i ^ (i >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    i = (i ^ (i >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    i = i ^ (i >> np.uint64(31))
    return ((i >> np.uint64(11)).astype(np.float64) / float(1 << 53)).astype(np.float32)


@runtime_checkable
class PointSet(Protocol):
    def sample(self, t: float) -> Union[dict, list]:
        ...


@dataclass
class CameraState:
    """The camera at one moment (engine/p3d/camera.py makes these). Given to point sets with wants_camera."""
    pos: np.ndarray                 # where the camera is (metres)
    target: np.ndarray              # the point it looks at
    fov: float = 50.0               # vertical field of view, degrees
    roll: float = 0.0               # degrees, positive tilts the horizon clockwise (any number: barrel rolls)
    focus: float = 10.0             # distance in metres that is sharp
    aperture: float = 0.0           # lens opening in metres (0: everything sharp). 0.05 is a strong blur
    aspect: float = 16.0 / 9.0
    near: float = 0.05              # nothing nearer than this is drawn (0.02 for macro shots)
    far: float = 5000.0
    up: Any = None                  # which way is up for the camera (default: the world's up). A camera that
    #                                 loops or looks straight down carries its own up, so it never flips

    def basis(self):
        """(right, up, forward) unit vectors of the camera, roll included."""
        f = np.asarray(self.target, np.float64) - np.asarray(self.pos, np.float64)
        f = f / max(np.linalg.norm(f), 1e-9)
        wup = np.array([0.0, 1.0, 0.0]) if self.up is None else np.asarray(self.up, np.float64)
        r = np.cross(f, wup)
        if np.linalg.norm(r) < 1e-6:        # looking straight along up: any steady sideways will do
            r = np.cross(f, [0.0, 0.0, -1.0] if abs(f[1]) > 0.9 else [0.0, 1.0, 0.0])
        r = r / np.linalg.norm(r)
        u = np.cross(r, f)
        if self.roll:
            a = np.radians(self.roll)
            r, u = r * np.cos(a) + u * np.sin(a), u * np.cos(a) - r * np.sin(a)
        return r, u, f

    def view(self):
        """World to camera space (4 x 4, column vectors; the camera looks down its own -z)."""
        r, u, f = self.basis()
        m = np.eye(4)
        m[0, :3], m[1, :3], m[2, :3] = r, u, -f
        m[:3, 3] = -m[:3, :3] @ np.asarray(self.pos, np.float64)
        return m

    def proj(self):
        """Camera space to clip space (4 x 4, OpenGL convention)."""
        fl = 1.0 / np.tan(np.radians(self.fov) * 0.5)
        n, fa = self.near, self.far
        m = np.zeros((4, 4))
        m[0, 0], m[1, 1] = fl / self.aspect, fl
        m[2, 2], m[2, 3] = (fa + n) / (n - fa), 2.0 * fa * n / (n - fa)
        m[3, 2] = -1.0
        return m

    def project(self, pts):
        """Screen positions of world points: (xy in 0..1 with y up, depth in metres along the view axis).
        Points behind the camera have a depth below zero."""
        p = np.asarray(pts, np.float64).reshape(-1, 3)
        r, u, f = self.basis()
        d = p - np.asarray(self.pos, np.float64)
        z = d @ f
        fl = 1.0 / np.tan(np.radians(self.fov) * 0.5)
        zs = np.where(np.abs(z) < 1e-9, 1e-9, z)
        x = (d @ r) * fl / (self.aspect * zs)
        y = (d @ u) * fl / zs
        return np.stack([x * 0.5 + 0.5, y * 0.5 + 0.5], axis=1), z

    def coc_radius(self, depth):
        """Radius of the circle of confusion at a view depth, as a fraction of the picture height."""
        depth = np.maximum(np.asarray(depth, np.float64), 1e-3)
        fl = 1.0 / np.tan(np.radians(self.fov) * 0.5)
        return 0.25 * self.aperture * fl * np.abs(1.0 / self.focus - 1.0 / depth)


@dataclass
class Mask:
    """How a point set's silhouette is used (see the module text)."""
    mode: str = "dark"                      # "dark" or "sky"
    sky: str = "sunrise"                    # mode "sky": which picture fills the shape (MASK_SKIES)
    strength: Union[float, Callable] = 1.0  # 0..1, a number or a function of t
    grow: float = 0.03                      # metres added to each point's size when the shape is drawn
    soft: float = 3.0                       # softness of the edge, in pixels of a 1080p picture. Below 2.5 the
    #                                         silhouettes are drawn at full size that frame (crisp letters)
    source: Any = None                      # another point set that gives the shape (default: the set itself)
    edge: float = 0.0                       # mode "sky": a light rim along the edge of the shape (0..1)
    tint: Any = (1.0, 1.0, 1.0)             # mode "sky": multiplies the fill (linear)
    look: Any = None                        # sky "world": the look (a name, or a dict of world settings) of the
    #                                         world seen through the shape; may be a function of t giving a name
    color: Any = None                       # sky "flat": the colour that fills the shape, a display hex shown
    #                                         exactly (as `paint`), or linear light; may be a function of t
    slot: Any = None                        # which of the two sky layers (0 or 1); by default sets with the same
    #                                         fill share a layer and different fills take the next free one

    def __post_init__(self):
        if self.mode not in MASK_MODES:
            raise ValueError(f"Mask mode must be one of {MASK_MODES}, got {self.mode!r}")
        if self.mode == "sky" and self.sky not in MASK_SKIES:
            raise ValueError(f"Mask sky must be one of {MASK_SKIES}, got {self.sky!r}")
        if self.mode == "sky" and self.sky == "world" and self.look is None:
            raise ValueError('Mask("sky", sky="world") needs look=: the look of the world behind the window')
        if self.mode == "sky" and self.sky == "flat" and self.color is None:
            raise ValueError('Mask("sky", sky="flat") needs color=: the colour that fills the shape')
        if self.slot not in (None, 0, 1):
            raise ValueError("Mask slot is 0 or 1 (two sky layers per frame)")

    def fill_key(self):
        """Masks with the same key share one sky layer."""
        if self.slot is not None:
            return ("slot", self.slot)
        lk = self.look if isinstance(self.look, (str, type(None))) else id(self.look)
        col = self.color if isinstance(self.color, (str, type(None), tuple)) else id(self.color)
        return (self.sky, lk, col, tuple(np.asarray(self.tint, np.float64).round(4)), float(self.edge))

    def strength_at(self, t):
        s = self.strength(t) if callable(self.strength) else self.strength
        return float(min(max(s, 0.0), 1.0))


def normalize(batch, where="batch"):
    """Checks one batch and returns it with every array as float32 of the right shape (N,), (N, 3)...
    Numbers and single colours are spread over all points. Raises ValueError with a clear message."""
    if not isinstance(batch, dict):
        raise ValueError(f"{where}: a batch is a dict, got {type(batch).__name__}")
    unknown = set(batch) - set(_ARRAY_FIELDS) - set(_BATCH_SETTINGS) - {"kind"}
    if unknown:
        raise ValueError(f"{where}: unknown keys {sorted(unknown)}")
    if "pos" not in batch:
        raise ValueError(f"{where}: 'pos' is required")
    kind = batch.get("kind", "soft")
    if kind not in KINDS:
        raise ValueError(f"{where}: kind must be one of {KINDS}, got {kind!r}")
    pos = np.ascontiguousarray(batch["pos"], dtype=np.float32)
    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"{where}: pos must have shape (N, 3), got {pos.shape}")
    n = pos.shape[0]
    out = dict(kind=kind, n=n, pos=pos)

    def arr(key, width, default):
        v = batch.get(key, None)
        if v is None:
            if default is None:
                return None
            v = default
        a = np.asarray(v, dtype=np.float32)
        if width == 1:
            if a.ndim == 0:
                a = np.full(n, float(a), np.float32)
            a = a.reshape(-1)
            if a.shape[0] != n:
                raise ValueError(f"{where}: {key} must have {n} values, got {a.shape}")
        else:
            if a.ndim == 1 and a.shape[0] == width:
                a = np.broadcast_to(a, (n, width))
            if a.ndim != 2 or a.shape != (n, width):
                raise ValueError(f"{where}: {key} must have shape ({n}, {width}), got {a.shape}")
        return np.ascontiguousarray(a, dtype=np.float32)

    out["size"] = arr("size", 1, 0.02)
    out["color"] = arr("color", 3, (1.0, 1.0, 1.0))
    out["alpha"] = arr("alpha", 1, 1.0)
    out["emit"] = arr("emit", 1, 1.0)
    out["seed"] = arr("seed", 1, None)
    if out["seed"] is None:
        out["seed"] = hash01(n)
    out["normal"] = arr("normal", 3, None)
    out["vel"] = arr("vel", 3, None)
    out["birth"] = arr("birth", 1, None)
    rot = batch.get("rot", None)
    if rot is None:
        out["rot"] = np.zeros((n, 2), np.float32)
    else:
        r = np.asarray(rot, dtype=np.float32)
        if r.ndim == 0:
            r = np.full(n, float(r), np.float32)
        if r.ndim == 1:
            if r.shape[0] != n:
                raise ValueError(f"{where}: rot must have {n} values, got {r.shape}")
            r = np.stack([r, np.zeros(n, np.float32)], axis=1)
        if r.shape != (n, 2):
            raise ValueError(f"{where}: rot must have shape ({n},) or ({n}, 2), got {r.shape}")
        out["rot"] = np.ascontiguousarray(r, dtype=np.float32)
    if kind in SEGMENT_KINDS:
        if batch.get("pos2", None) is None:
            raise ValueError(f"{where}: kind {kind!r} needs pos2")
        out["pos2"] = arr("pos2", 3, None)
        out["alpha2"] = arr("alpha2", 1, None)
        if out["alpha2"] is None:
            out["alpha2"] = out["alpha"]
        out["size2"] = arr("size2", 1, None)
        if out["size2"] is None:
            out["size2"] = out["size"]
        # the place along the path at each end rides in the slot a sprite uses for its turn
        out["rot"] = np.ascontiguousarray(np.stack([arr("u", 1, 0.0), arr("u2", 1, 0.0)], axis=1), dtype=np.float32)
    else:
        out["pos2"] = out["alpha2"] = out["size2"] = None
    for key, default in _BATCH_SETTINGS.items():
        v = batch.get(key, default)
        if key == "rim":
            v = tuple(float(x) for x in (v if isinstance(v, (tuple, list)) else (v, 2.0)))
            if len(v) != 2:
                raise ValueError(f"{where}: rim is (strength, power)")
            if v[0] > 0.0 and out["normal"] is None:
                raise ValueError(f"{where}: rim needs 'normal'")
        elif key == "pulse":
            v = tuple(float(x) for x in v)
            if len(v) != 4:
                raise ValueError(f"{where}: pulse is (speed, length, gain, period)")
        elif key in _AMOUNTS:
            v = float(min(max(float(v), 0.0), 1.0))
        elif key in ("fade", "flash"):
            v = float(max(float(v), 0.0))
        else:
            v = bool(v)
        out[key] = v
    for key in ("pos", "pos2", "normal", "vel"):
        if out.get(key) is not None and not np.all(np.isfinite(out[key])):
            raise ValueError(f"{where}: {key} has values that are not numbers")
    return out


@dataclass
class Entry:
    name: str
    pointset: Any
    reflect: bool = True
    depth_of_field: bool = True
    mask: Optional[Mask] = None
    fog: bool = True
    lod: bool = True
    order: int = 0
    window: Any = False


class Scene:
    """The list of point sets the 3D layer draws. Song files fill it in P3D["setup"](scene)."""

    def __init__(self):
        self._entries = {}
        self._count = 0

    def add(self, name, pointset, reflect=True, depth_of_field=True, mask=None, fog=True, lod=True, window=False):
        # window: False, True (inside the first window), or the name of the masked set whose window it lives in
        """Adds (or replaces) a point set.

        reflect          also draw its mirror image in the lake (rippled, dimmer)
        depth_of_field   blur its points by their distance from the focus plane (bokeh)
        mask             a Mask: use the set's silhouette as a dark body or a window onto a sky
        fog              let the haze of the world dim and tint it with distance
        lod              when a point is far out of focus its light is spread over a big disc; with lod the
                         renderer then draws a share of such points, each brighter, which looks the same in
                         a cloud of points and keeps the frame fast. Set False for a few big lights whose
                         every disc matters (lanterns).
        window           the set lives inside a window: it is drawn only where a "sky" silhouette is. True: the
                         first window; the name of a masked set: inside that set's window. A set that lives in
                         a window and has a Mask("sky") of its own is a window inside the window (nested)
        """
        if not hasattr(pointset, "sample"):
            raise TypeError(f"Scene.add({name!r}): the point set needs a sample(t) method")
        if mask is not None and not isinstance(mask, Mask):
            raise TypeError(f"Scene.add({name!r}): mask must be a p3d.api.Mask")
        win = window if isinstance(window, str) else bool(window)
        self._entries[name] = Entry(name, pointset, bool(reflect), bool(depth_of_field), mask, bool(fog),
                                    bool(lod), self._count, win)
        self._count += 1
        return pointset

    def remove(self, name):
        self._entries.pop(name, None)

    def get(self, name):
        return self._entries[name].pointset

    def names(self):
        return list(self._entries)

    def entries(self):
        return sorted(self._entries.values(), key=lambda e: e.order)

    def collect(self, entry, t, cam=None):
        """The normalized batches of one entry at t (what the renderer draws), with the set's gain applied
        as out["gain"]. Static sets are sampled at t = 0."""
        ps = entry.pointset
        ts = 0.0 if getattr(ps, "static", False) else t
        res = ps.sample(ts, cam) if getattr(ps, "wants_camera", False) else ps.sample(ts)
        batches = res if isinstance(res, (list, tuple)) else [res]
        gain = float(ps.gain(t)) if hasattr(ps, "gain") else 1.0
        out = []
        for k, b in enumerate(batches):
            if b is None:
                continue
            nb = normalize(b, f"{entry.name}[{k}]")
            if nb["n"] == 0:
                continue
            nb["gain"] = gain
            out.append(nb)
        return out


# ---------------------------------------------------------------------------------------------------------
# Moving frames: parenting a point set (or the camera) to something that travels and turns
# ---------------------------------------------------------------------------------------------------------
def _at_time(v, t):
    return v(t) if callable(v) else v


class Frame:
    """A frame of reference that can travel, turn and grow: each setting a constant or a function of time.

    origin   where the frame's own origin is in the world (or in its parent)
    yaw      degrees it is turned about the vertical (toward +x from +z, like every azimuth)
    basis    instead of yaw: a full 3 x 3 turn (columns: the frame's x, y, z axes in the world)
    scale    a size factor (a hand at 5000 times life size)
    parent   another Frame this one rides
    """

    def __init__(self, origin=(0.0, 0.0, 0.0), yaw=0.0, basis=None, scale=1.0, parent=None):
        self.origin, self.yaw, self.basis, self.scale, self.parent = origin, yaw, basis, scale, parent

    def at(self, t):
        """(origin (3,), turn (3, 3), scale) in the world at t."""
        o = np.asarray(_at_time(self.origin, t), np.float64)
        if self.basis is not None:
            R = np.asarray(_at_time(self.basis, t), np.float64)
        else:
            a = np.radians(float(_at_time(self.yaw, t)))
            ca, sa = np.cos(a), np.sin(a)
            R = np.array([[ca, 0.0, sa], [0.0, 1.0, 0.0], [-sa, 0.0, ca]])
        s = float(_at_time(self.scale, t))
        if self.parent is not None:
            po, pR, ps = self.parent.at(t)
            o, R, s = po + (pR @ o) * ps, pR @ R, ps * s
        return o, R, s

    def points(self, p, t):
        """Positions given in the frame, as world positions."""
        o, R, s = self.at(t)
        return (np.asarray(p, np.float64) @ R.T) * s + o

    def vectors(self, v, t):
        """Directions given in the frame, as world directions (turned, not moved or scaled)."""
        return np.asarray(v, np.float64) @ self.at(t)[1].T

    def velocity(self, t, dt=1.0 / 120.0):
        """How fast the frame's origin moves in the world at t (metres per second)."""
        return (self.at(t + dt)[0] - self.at(t - dt)[0]) / (2.0 * dt)


class Parented:
    """A point set that rides a Frame: its positions, segment ends, normals, speeds and sizes follow the
    frame. The set itself keeps working in its own coordinates."""

    def __init__(self, pointset, frame):
        self.pointset, self.frame = pointset, frame
        self.wants_camera = bool(getattr(pointset, "wants_camera", False))
        if hasattr(pointset, "gain"):
            self.gain = pointset.gain

    def _move(self, b, t):
        if b is None:
            return None
        o, R, s = self.frame.at(t)
        b = dict(b)
        b["pos"] = (np.asarray(b["pos"], np.float64) @ R.T) * s + o
        if b.get("pos2") is not None:
            b["pos2"] = (np.asarray(b["pos2"], np.float64) @ R.T) * s + o
        if b.get("normal") is not None:
            b["normal"] = np.asarray(b["normal"], np.float64) @ R.T
        if b.get("vel") is not None:
            b["vel"] = (np.asarray(b["vel"], np.float64) @ R.T) * s + self.frame.velocity(t)
        if s != 1.0:
            for k in ("size", "size2"):
                if b.get(k) is not None:
                    b[k] = np.asarray(b[k], np.float64) * s
                elif k == "size":
                    b[k] = 0.02 * s
        return b

    def sample(self, t, cam=None):
        res = self.pointset.sample(t, cam) if self.wants_camera else self.pointset.sample(t)
        if isinstance(res, (list, tuple)):
            return [self._move(b, t) for b in res]
        return self._move(res, t)


# ---------------------------------------------------------------------------------------------------------
# Ribbons: one continuous tapering band along a path
# ---------------------------------------------------------------------------------------------------------
def ribbon(points, width=0.08, color=(1.0, 1.0, 1.0), alpha=1.0, **settings):
    """A ribbon batch along a line of points (M, 3): one continuous band, no beads.

    width, alpha   a number, or M values (one per point) for tapering: for example np.linspace(0, 1, M)
    color          one colour or M colours
    settings       any batch setting (emit, pulse=(speed, length, gain, period), dof, paint, ...)
    The path coordinate u is the length along the ribbon in metres, so a pulse travels at metres per second.
    """
    p = np.asarray(points, np.float64).reshape(-1, 3)
    m = p.shape[0]
    if m < 2:
        return None
    w = np.broadcast_to(np.asarray(width, np.float64), (m,))
    a = np.broadcast_to(np.asarray(alpha, np.float64), (m,))
    c = np.asarray(color, np.float64)
    c = np.broadcast_to(c, (m, 3)) if c.ndim == 1 else c
    u = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    b = dict(pos=p[:-1], pos2=p[1:], size=w[:-1], size2=w[1:], alpha=a[:-1], alpha2=a[1:], u=u[:-1], u2=u[1:],
             color=0.5 * (c[:-1] + c[1:]), kind="ribbon")
    b.update(settings)
    return b


class Trail:
    """A ribbon that follows a moving point: its head is at path(t), its tail where the point was `length`
    seconds ago, tapering to nothing (a comet, a stream from a hand, a road of light).

    path     a function t -> (x, y, z)
    length   seconds of the path the ribbon keeps
    width    metres at the head (the tail narrows to `tail` of it)
    born     the ribbon starts growing at this time (nothing before it)
    """

    def __init__(self, path, length=1.5, n=64, width=0.10, color=(1.0, 1.0, 1.0), alpha=1.0, tail=0.15, born=None,
                 **settings):
        self.path, self.length, self.n, self.width, self.alpha, self.tail = path, float(length), int(n), width, alpha, tail
        self.color, self.born, self.settings = color, born, settings

    def sample(self, t):
        t0 = t - self.length if self.born is None else max(t - self.length, float(self.born))
        if t - t0 < 1e-4:
            return None
        ts = np.linspace(t0, t, self.n + 1)
        pts = np.array([np.asarray(self.path(float(x)), np.float64) for x in ts])
        k = (ts - (t - self.length)) / self.length          # 0 at the far end of a full tail, 1 at the head
        w = float(_at_time(self.width, t)) * (self.tail + (1.0 - self.tail) * k)
        a = float(_at_time(self.alpha, t)) * np.clip(k * 1.5, 0.0, 1.0)
        col = self.color(t) if callable(self.color) else self.color
        return ribbon(pts, width=w, color=col, alpha=a, **self.settings)


# ---------------------------------------------------------------------------------------------------------
# A stand-in figure: a robed person of points, to test framing, focus and the mask pass until real bodies land.
# ---------------------------------------------------------------------------------------------------------
class StandIn:
    """A simple robed figure made of points (about `height` metres tall), standing with its feet at `pos`
    and facing azimuth `facing` (degrees; 0 faces +z). Not lifelike: a placeholder for helper BODY's people.

    look: "glitter" (a soft cloud of twinkling points) or "rim" (normals given, bright edge, dark inside).
    """

    def __init__(self, pos=(0.0, 0.0, 0.0), height=1.7, n=24000, color="#ffd9a0", facing=0.0, look="glitter",
                 seed=7, bright=1.0):
        rng = np.random.default_rng(seed)
        parts = []   # (centre, radii, share of points): ellipsoids in a body frame of height 1, feet at y = 0

        def ell(c, r, w):
            parts.append((np.array(c, np.float64), np.array(r, np.float64), w))

        ell((0.0, 0.925, 0.0), (0.062, 0.072, 0.068), 0.10)        # head
        ell((0.0, 0.845, 0.0), (0.030, 0.035, 0.030), 0.02)        # neck
        ell((0.0, 0.700, 0.0), (0.118, 0.140, 0.070), 0.20)        # chest and shoulders
        ell((0.0, 0.560, 0.0), (0.100, 0.110, 0.066), 0.12)        # waist
        ell((-0.150, 0.640, 0.0), (0.034, 0.170, 0.036), 0.07)     # arms (hanging)
        ell((0.150, 0.640, 0.0), (0.034, 0.170, 0.036), 0.07)
        ell((-0.165, 0.455, 0.01), (0.026, 0.050, 0.022), 0.02)    # hands
        ell((0.165, 0.455, 0.01), (0.026, 0.050, 0.022), 0.02)
        pts, nrm = [], []
        for c, r, w in parts:
            k = max(int(n * w), 1)
            d = rng.normal(size=(k, 3))
            d /= np.linalg.norm(d, axis=1, keepdims=True)
            pts.append(c + d * r)
            g = d / r
            nrm.append(g / np.linalg.norm(g, axis=1, keepdims=True))
        # a long robe: a cone from the waist to the hem, with soft folds
        k = n - sum(p.shape[0] for p in pts)
        v = rng.random(k) ** 0.8
        a = rng.random(k) * 2 * np.pi
        y = 0.50 * (1 - v) + 0.012
        rad = (0.095 + 0.105 * v) * (1.0 + 0.07 * np.sin(a * 7 + v * 5.0))
        pts.append(np.stack([np.cos(a) * rad, y, np.sin(a) * rad * 0.74], axis=1))
        g = np.stack([np.cos(a), np.full(k, 0.22), np.sin(a)], axis=1)
        nrm.append(g / np.linalg.norm(g, axis=1, keepdims=True))
        body = np.concatenate(pts) * float(height)
        normal = np.concatenate(nrm)
        ca, sa = np.cos(np.radians(facing)), np.sin(np.radians(facing))
        rot = np.array([[ca, 0.0, sa], [0.0, 1.0, 0.0], [-sa, 0.0, ca]])
        self.base = (body @ rot.T).astype(np.float32)
        self.normal = (normal @ rot.T).astype(np.float32)
        self.origin = np.asarray(pos, np.float32)
        self.height = float(height)
        self.look = look
        self.color = (lin(color) * bright).astype(np.float32)
        self.seed = rng.random(n).astype(np.float32)
        self.size = (0.006 + 0.012 * rng.random(n) ** 3).astype(np.float32) * float(height) / 1.7
        self.phase = (rng.random(n) * 6.2832).astype(np.float32)

    def sample(self, t):
        breathe = 1.0 + 0.004 * np.sin(t * 1.3)
        sway = 0.004 * self.height * np.sin(t * 0.9 + self.base[:, 1:2] * 3.0)
        pos = self.base * np.array([breathe, 1.0, breathe], np.float32)
        pos = pos + np.concatenate([sway, np.zeros_like(sway), np.zeros_like(sway)], axis=1) + self.origin
        if self.look == "rim":
            return dict(pos=pos, size=self.size * 1.2, color=self.color, alpha=0.9, kind="soft",
                        normal=self.normal, rim=(1.0, 2.5), seed=self.seed, twinkle=0.5)
        return dict(pos=pos, size=self.size, color=self.color, alpha=0.55, kind="soft", seed=self.seed,
                    twinkle=0.7, emit=1.0 + 2.0 * (self.seed > 0.93))


if __name__ == "__main__":
    # a quick self check without graphics: python engine/p3d/api.py
    sc = Scene()
    frame = Frame(origin=lambda t: (0.0, 0.0, 2.0 - t), yaw=lambda t: 20.0 * t)
    sc.add("stand-in", Parented(StandIn(), frame), mask=Mask("dark"))
    sc.add("trail", Trail(lambda t: (np.sin(t), 1.0 + 0.2 * t, np.cos(t)), length=1.0, pulse=(2.0, 0.3, 2.0, 1.5)))
    cam = CameraState(pos=at(0, 8, 1.6), target=np.array([0.0, 1.0, 0.0]), fov=40.0, focus=6.0, aperture=0.04)
    for e in sc.entries():
        for b in sc.collect(e, 1.0, cam):
            xy, z = cam.project(b["pos"])
            print(e.name, b["kind"], b["n"], "points; on screen x %.2f..%.2f y %.2f..%.2f depth %.1f..%.1f m; "
                  "blur radius %.4f of the height" % (xy[:, 0].min(), xy[:, 0].max(), xy[:, 1].min(),
                                                     xy[:, 1].max(), z.min(), z.max(),
                                                     float(cam.coc_radius(z.mean()))))
    down = CameraState(pos=np.array([0.0, 30.0, 0.0]), target=np.zeros(3), up=np.array([0.0, 0.0, -1.0]))
    print("looking straight down, right and up:", np.round(down.basis()[0], 3), np.round(down.basis()[1], 3))
    print("show('#f0566a') =", np.round(show("#f0566a"), 3))
    print("ok")
