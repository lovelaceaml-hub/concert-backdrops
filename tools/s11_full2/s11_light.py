"""Song 11 v2: the light of the world: one long sunrise (pre-dawn in the waiting city, full sunrise over
Zion at the coda), the looks, the sun and its rays. Owned by the coda thread; values before 3:05.92 stay as they
are unless the core agrees.

Owned by the coda thread. Imported by tools/s11_full2/s11_full2.py (the core) part way through its load:
everything the core defined before the scene imports (music, places, helpers, shot lookups) comes in by the
star import. Camera shots: SHOTS below (cut times are locked to the music; change only keys, fov, aperture
and focus). Point sets: add(scene). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H


LOOKS = dict(
    city=dict(base="predawn", hills=0.0, stars=0.55, milky=0.25, clouds=0.18, haze=0.45, mist=0.10,
              sky_top="#0a1236", sky_mid="#3a2c6a", sky_hor="#c4786e", water="#05061a", ripple=0.25),
    space=dict(base="night", hills=0.0, stars=1.0, milky=0.75, clouds=0.0, sky_top="#02040f",
               sky_mid="#081236", sky_hor="#1a2a5e", sun_int=0.0, mist=0.02, haze=0.15, haze_color="#1a2a5e",
               water="#03061a", ripple=0.15, rays=0.0),
    zion=dict(base="dawn", hills=0.0, clouds=0.25, mist=0.2, ripple=0.3, water="#0a0a1e"),
    sunrise=dict(base="sunrise", hills=0.0, clouds=0.30, mist=0.12, ripple=0.35, sky_top="#0f2560",
                 sky_mid="#5a3f86", sky_hor="#f09a5c", rays=0.6, exposure=0.82, water="#0a0820", haze=0.4, sun_glow=0.45, sun_disc=5.0),
    golden=dict(base="golden", hills=0.0, clouds=0.25, sky_top="#123a86", sky_mid="#4f6fb4",
                sky_hor="#f2b27a", rays=0.5, sun_glow=0.45, sun_disc=5.0, mist=0.12, ripple=0.3, exposure=0.8,
                water="#0b1838", haze=0.35, haze_color="#b8907a"),
    glory=dict(base="golden", hills=0.0, clouds=0.15, sky_top="#1a4ea6", sky_mid="#5f8fd0",
               sky_hor="#ffcf8f", sun_color="#fff2d6", rays=0.6, sun_glow=0.5, sun_disc=5.5, mist=0.10,
               ripple=0.3, water="#0e2148", haze=0.3, haze_color="#d8b090", exposure=0.8),
    pastel_card=dict(base="day", hills=0.0, sky_top="#9bdbf6", sky_mid="#efcfeb", sky_hor="#ffd9b6",
                     sun_int=0.3, sun_glow=0.3, mist=0.14, haze=0.14, stars=0.2, water="#8ab4e0"),
)


def _local_look(t):
    if t < 53.78:
        return "city"
    if t < 82.08:
        return "zion"
    if t < 162.86:
        return "sunrise"
    if t < 201.73:
        return "golden"
    return "glory"


def _look_keys():
    keys = []
    for s in H.SHOTS:
        t0 = s["t0"]
        if s["kind"] == "globe":
            name = "pastel_card" if t0 >= 254.0 else "space"
        else:
            name = _local_look(t0)
        keys.append((t0, name, 0.0))
    return keys


def sun_el(t):
    if globe_view(t):
        if t >= 254.0:
            return 30.0
        if t >= 224.03:          # the world finale: the same sun rises over the Earth's edge at the peak
            return -4.0 + 26.0 * _sc(226.0, 235.6, t)
        return -12.0 + 10.0 * _sc(75.2, 77.46, t)
    k = [(0.0, -7.0), (53.78, -3.5), (80.0, -1.5), (82.08, 2.6), (160.0, 4.0), (162.86, 6.0), (197.0, 6.8),
         (201.73, 7.0), (206.0, 12.0), (224.0, 16.0), (275.0, 18.0)]
    ts, vs = zip(*k)
    v = float(np.interp(t, ts, vs))
    v += 1.4 * _sc(81.9, 82.3, t) * (1.0 - _sc(82.3, 86.0, t))      # the sun jumps on the slam
    return v


def sun_az(t):
    return 0.0 if globe_view(t) else 163.0          # behind Zion's right shoulder, clear of the words


def sun_int(t):
    if globe_view(t):
        return 0.9 if t >= 224.03 else 0.0
    return 0.40 + 0.25 * _sc(53.0, 82.08, t) + 0.15 * _sc(160.0, 201.73, t) + 0.08 * loud(t)


def rays(t):
    if globe_view(t):
        return 0.6 * _sc(232.0, 236.0, t) if t < 254.0 else 0.0
    base = 0.12 + 0.35 * _sc(80.0, 83.0, t) + 0.2 * _sc(197.0, 202.0, t)
    return base * (0.85 + 0.3 * loud(t)) + 0.2 * hit_pulse(t, [SLAM1, SLAM2, SLAM3], fall=1.2)


def world():
    """The P3D world settings (built after the core has gathered every thread's shots)."""
    return dict(
        looks=LOOKS,
        look=_look_keys(),
        sun_el=sun_el, sun_az=sun_az, sun_int=sun_int, rays=rays,
        react=dict(beat=0.25, level=0.25),
    )
