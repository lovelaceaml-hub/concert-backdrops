"""The shared timeline helper (Astra round 1, finding 8).

Track([(t, value), ...]) eases smoothly between keys. The key times must be strictly increasing: a Track
with keys out of order (or two keys at the same time) is refused with a clear error, because the easing
between unsorted keys jumps instead of moving.

New song files use it with `from track import Track`. Older song files still define their own copy; song.py
checks every Track-like setting of the chosen song with check_song() when the engine loads it.
"""
import numpy as np


class TrackKeyError(ValueError):
    pass


def check_times(times, where="Track"):
    t = np.asarray(times, dtype=np.float64)
    if t.size == 0:
        raise TrackKeyError(f"{where}: a Track needs at least one key")
    if not np.all(np.isfinite(t)):
        raise TrackKeyError(f"{where}: key times must be numbers, got {list(t)}")
    bad = np.nonzero(np.diff(t) <= 0)[0]
    if bad.size:
        i = int(bad[0])
        raise TrackKeyError(f"{where}: key times must be strictly increasing, but key {i + 1} is at {t[i + 1]:g} "
                            f"after key {i} at {t[i]:g} (all times: {[round(float(x), 3) for x in t]})")


class Track:
    def __init__(self, keys, name="Track"):
        keys = list(keys)
        check_times([k[0] for k in keys], name)
        self.t = np.array([k[0] for k in keys], dtype=np.float64)
        self.v = np.array([np.atleast_1d(np.asarray(k[1], dtype=np.float64)) for k in keys])

    def __call__(self, t):
        if t <= self.t[0]:
            v = self.v[0]
        elif t >= self.t[-1]:
            v = self.v[-1]
        else:
            i = int(np.searchsorted(self.t, t, side="right")) - 1
            u = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
            u = u * u * (3 - 2 * u)
            v = self.v[i] * (1 - u) + self.v[i + 1] * u
        return float(v[0]) if v.shape[0] == 1 else v


def _is_track(obj):
    return callable(obj) and isinstance(getattr(obj, "t", None), np.ndarray) and hasattr(obj, "v")


def check_song(module):
    """Refuses any Track in a song module (top level, or inside SCENES, FIGURES, lists and dicts) whose keys
    are not strictly increasing."""
    seen = set()

    def walk(obj, where, depth):
        if depth > 4 or id(obj) in seen:
            return
        seen.add(id(obj))
        if _is_track(obj):
            check_times(obj.t, where)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{where}[{k!r}]", depth + 1)
        elif isinstance(obj, (list, tuple)):
            for k, v in enumerate(obj):
                walk(v, f"{where}[{k}]", depth + 1)

    for name, obj in vars(module).items():
        if not name.startswith("_"):
            walk(obj, f"{module.__name__}.{name}", 0)
