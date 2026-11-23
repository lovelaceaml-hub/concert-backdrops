"""The song kit's light of the world: the looks, the sun and its rays, from the song's data (as Song 11's
tools/s11_full2/s11_light.py, which keeps its own story-specific curves). Every song keeps its own look from the
DESIGN-SYSTEM table (time of day, season, colours), so no two songs look alike.

song_data gives:
    LOOKS      dict name -> world look settings (as Song 11's LOOKS: base, sky_top, sky_mid, sky_hor, mist, ...)
    LOOK_KEYS  [(t, name, blend seconds)]: the look in force from t (blending into it over the given seconds)
    SUN        dict(el=[(t, degrees)], az=degrees or [(t, degrees)], int=[(t, 0..1)], rays=[(t, 0..1)])
Optional: GLARE_CALM [(a, b, k)]: the sun's glow and rays held down by k between a and b.
No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.kit_film import *  # noqa: F401,F403
import songs.kit_film as H
import song_data as D

SUN = dict(getattr(D, "SUN", {}))


def _curve(keys, default):
    if keys is None:
        return lambda t: default
    if isinstance(keys, (int, float)):
        return lambda t: float(keys)
    ts, vs = zip(*keys)
    return lambda t: float(np.interp(t, ts, vs))


_el = _curve(SUN.get("el"), -4.0)
_az = _curve(SUN.get("az"), 180.0)
_int = _curve(SUN.get("int"), 0.3)
_rays = _curve(SUN.get("rays"), 0.2)


def sun_el(t):
    return _el(t) + 1.4 * H.hit_pulse(t, H.SLAMS, fall=1.2) * 0.4      # the sun lifts a little on the slams


def sun_az(t):
    return _az(t)


def sun_int(t):
    return _int(t) * (0.9 + 0.2 * H.loud(t))


def rays(t):
    return _rays(t) * (0.85 + 0.3 * H.loud(t)) + 0.2 * H.hit_pulse(t, H.SLAMS, fall=1.2)


def glare_calm(t):
    """The sun's glow and rays held down where they would pale the picture (the song's GLARE_CALM spans)."""
    k = 1.0
    for a, b, v in getattr(D, "GLARE_CALM", []):
        k *= 1.0 - v * float(H._sc(a - 0.4, a, t) * (1.0 - H._sc(b, b + 0.4, t)))
    return k


def world():
    """The P3D world settings (built after the core has gathered every set's shots)."""
    return dict(
        looks=dict(D.LOOKS),
        look=sorted(list(D.LOOK_KEYS), key=lambda k: k[0]),
        sun_el=sun_el, sun_az=sun_az,
        sun_int=lambda t: sun_int(t) * glare_calm(t), rays=lambda t: rays(t) * glare_calm(t),
        react=dict(beat=0.25, level=0.25),
    )
