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
    # Round 3: the heavenly night of the approved promo. Deep skies and glowing mist so every light blazes;
    # dawn builds slowly through the choruses; the full gold sunrise is saved for the coda (3:21.73).
    city=dict(base="night", hills=0.0, stars=0.9, milky=0.6, clouds=0.12, haze=0.35, haze_color="#1a1238",
              mist=0.30, mist_color="#241a48", sky_top="#03030c", sky_mid="#0e0a2a", sky_hor="#3a2450",
              water="#02020a", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.25),
    space=dict(base="night", hills=0.0, stars=1.0, milky=0.75, clouds=0.0, sky_top="#02040f",
               sky_mid="#081236", sky_hor="#1a2a5e", sun_int=0.0, mist=0.02, haze=0.15, haze_color="#1a2a5e",
               water="#03061a", ripple=0.15, rays=0.0),
    # verse 1: still night, a first warm line of light on the horizon
    zion=dict(base="night", hills=0.0, stars=0.8, milky=0.45, clouds=0.15, haze=0.3, haze_color="#2a1c48",
              mist=0.30, mist_color="#3a2a5a", sky_top="#050418", sky_mid="#1e1648", sky_hor="#8a5070",
              water="#03030c", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.3),
    # chorus 1 to verse 2: lavender heaven with a peach-gold horizon (Anthony's references)
    sunrise=dict(base="dusk", hills=0.0, stars=0.6, milky=0.3, clouds=0.18, haze=0.3, haze_color="#22183e",
                 mist=0.30, mist_color="#6a5490", sky_top="#060722", sky_mid="#22184e", sky_hor="#b0687a",
                 water="#04040e", ripple=0.25, dust=0.9, bokeh=0.9, rays=0.45, sun_glow=0.35, sun_disc=4.0),
    # chorus 2: lavender turning rose, the horizon gold
    golden=dict(base="dusk", hills=0.0, stars=0.4, clouds=0.2, haze=0.3, haze_color="#28183a", mist=0.28,
                mist_color="#7a5088", sky_top="#070824", sky_mid="#2a1a56", sky_hor="#c07070", water="#04040e",
                ripple=0.25, dust=0.9, bokeh=0.9, rays=0.5, sun_glow=0.38, sun_disc=4.0),
    glory=dict(base="dusk", hills=0.0, stars=0.3, clouds=0.2, haze=0.3, haze_color="#2c1a3a", mist=0.25,
               mist_color="#8a5a88", sky_top="#080a28", sky_mid="#2e1e5c", sky_hor="#c8786c", water="#05040f",
               ripple=0.25, dust=0.9, bokeh=0.9, rays=0.55, sun_glow=0.4, sun_disc=4.5),
    # the coda (owned by the coda thread, from 3:08.27 on): pre-dawn hush, the sunrise in rose and violet folding
    # into gold, the sky stage, the summit, the Earth finale
    coda_dawn=dict(base="night", hills=0.0, clouds=0.25, stars=0.45, milky=0.2, sky_top="#05061a",
                   sky_mid="#24164a", sky_hor="#a04a62", sun_color="#ffc48e", haze=0.35, haze_color="#3a2048",
                   mist=0.30, mist_color="#4a2650", water="#04040e", ripple=0.3, sun_glow=0.4, sun_disc=4.0,
                   dust=0.9, bokeh=0.9, dust_color="#ffd2b0", dust_color2="#e8b0d8", rays=0.4),
    coda_rise=dict(base="sunrise", hills=0.0, clouds=0.32, stars=0.04, sky_top="#121c58", sky_mid="#6e3c84",
                   sky_hor="#f48a66", sun_color="#ffd296", haze=0.45, haze_color="#a8587a", mist=0.12,
                   mist_color="#9a5a76", water="#090720", ripple=0.35, sun_glow=0.32, sun_disc=4.0,
                   exposure=0.84, dust_color="#ffd8b0", dust_color2="#f0b8d8"),
    coda_gold=dict(base="sunrise", hills=0.0, clouds=0.30, stars=0.0, sky_top="#16286a", sky_mid="#9a5a8a",
                   sky_hor="#ffb468", sun_color="#ffe0a4", haze=0.42, haze_color="#b8706e", mist=0.12,
                   mist_color="#a86e70", water="#0a0a24", ripple=0.35, sun_glow=0.32, sun_disc=4.5,
                   exposure=0.84, dust_color="#ffe2b0", dust_color2="#ffc8b8"),
    coda_sky=dict(base="sunrise", hills=0.0, clouds=0.42, stars=0.0, sky_top="#0a1236", sky_mid="#3a2460",
                  sky_hor="#d07868", sun_color="#ffe0a4", haze=0.22, haze_color="#4e3870", mist=0.0,
                  water="#0c0a26", ripple=0.4, sun_glow=0.30, sun_disc=4.5, exposure=0.84,
                  dust_color="#ffe2b0", dust_color2="#ffc8d8"),
    coda_summit=dict(base="sunrise", hills=0.0, clouds=0.28, stars=0.0, sky_top="#0a1236", sky_mid="#3a2a60",
                     sky_hor="#d08070", sun_color="#ffe6b0", haze=0.18, haze_color="#6a4c80", mist=0.05,
                     mist_color="#8a6a8a", water="#0c1030", ripple=0.3, sun_glow=0.16, sun_disc=3.0,   # f35
                     exposure=0.78, dust_color="#fff0d0", dust_color2="#ffd0b8"),
    coda_home=dict(base="sunrise", hills=0.0, clouds=0.25, stars=0.25, sky_top="#0a1640", sky_mid="#3a3a80",
                   sky_hor="#d08a7a", sun_color="#fff0cc", haze=0.25, haze_color="#3a2a58", mist=0.2,
                   mist_color="#4a3a68", water="#050818", ripple=0.3, sun_glow=0.26, sun_disc=4.0, exposure=0.8,
                   dust=0.9, bokeh=0.9, dust_color="#fff0d0", dust_color2="#ffd8c0"),
    space_finale=dict(base="night", hills=0.0, stars=1.0, milky=0.6, clouds=0.0, sky_top="#02040f",
                      sky_mid="#0a1238", sky_hor="#24265e", sun_color="#ffd89c", sun_glow=0.26, sun_disc=5.0,
                      sun_size=1.6, mist=0.0, haze=0.12, haze_color="#24265e", water="#03061a", ripple=0.15,
                      exposure=0.95),
    brass=dict(base="night", hills=0.0, stars=0.5, clouds=0.15, sky_top="#0c0e3a", sky_mid="#3a2a70",
               sky_hor="#b06a7a", haze=0.2, haze_color="#22184c", mist=0.2, mist_color="#30204c", water="#04040e",
               sun_glow=0.3, sun_disc=4.0, rays=0.3, dust=0.9, bokeh=0.9),
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


CODA_LOOKS = dict(hearts_rise="coda_dawn", sunrise="coda_rise", sky_stage="coda_sky", summit="coda_summit",
                  earth_finale="space_finale", home_stage="coda_home")


def _look_keys():
    keys = []
    for s in H.SHOTS:
        t0 = s["t0"]
        if s["name"] in CODA_LOOKS:
            name = CODA_LOOKS[s["name"]]
        elif t0 >= CODA0 and s["kind"] != "globe":
            # the choir and church cut-ins inside the coda take the coda's light around them
            name = ("coda_dawn" if t0 < 201.73 else "coda_rise" if t0 < 205.98 else "coda_sky" if t0 < 211.6
                    else "coda_summit" if t0 < 238.8 else "coda_home")
        elif s["kind"] == "globe":
            name = "pastel_card" if t0 >= 254.0 else "space"
        elif s["kind"] == "stage" and 160.0 <= t0 < CODA0:
            name = "brass"            # the brass cut-ins face the sunrise: a deeper sky so the words stay clear
        else:
            name = _local_look(t0)
        keys.append((t0, name, 0.0))
    keys.append((204.0, "coda_gold", 3.6))       # the sunrise: rose and violet fold into gold
    return sorted(keys, key=lambda k: k[0])


CODA0 = 188.27          # from here on the light is the coda's own (hearts_rise and after)


def _globe_sun(t):
    """The world finale: the sun stands just over the Earth's top edge as the camera sees it, and rises over it
    at the peak (3:55.6), the same sun as over Zion, seen from space. Returns (az, el)."""
    cam = H.CAMERA.state(t)
    d = np.asarray(GLOBE_C, np.float64) - np.asarray(cam.pos, np.float64)
    dist = float(np.linalg.norm(d))
    el_c = float(np.degrees(np.arcsin(d[1] / dist)))
    az_c = float(np.degrees(np.arctan2(d[0], d[2])))
    limb = float(np.degrees(np.arcsin(min(GLOBE_R / dist, 0.99))))
    rise = -6.0 + 8.5 * _sc(233.8, 235.6, t) + 1.5 * _sc(235.6, 238.8, t)
    return az_c, el_c + limb + rise


def _coda_el(t):
    k = [(CODA0, -2.2), (197.0, -1.4), (201.6, -0.9), (201.73, -0.4), (206.0, 3.4), (211.6, 3.6), (224.03, 6.5)]
    ts, vs = zip(*k)
    return float(np.interp(t, ts, vs))


def sun_el(t):
    if globe_view(t):
        if t >= 254.0:
            return 30.0
        if t >= 224.03:          # the world finale: the same sun rises over the Earth's edge at the peak
            return _globe_sun(t)[1]
        return -12.0 + 10.0 * _sc(75.2, 77.46, t)
    if CODA0 <= t < 238.8:
        return _coda_el(t)
    k = [(0.0, -7.0), (53.78, -3.5), (80.0, -1.5), (82.08, 2.6), (160.0, 4.0), (162.86, 6.0), (197.0, 6.8),
         (201.73, 7.0), (206.0, 12.0), (224.0, 16.0), (275.0, 18.0)]
    ts, vs = zip(*k)
    v = float(np.interp(t, ts, vs))
    v += 1.4 * _sc(81.9, 82.3, t) * (1.0 - _sc(82.3, 86.0, t))      # the sun jumps on the slam
    return v


def sun_az(t):
    if globe_view(t):
        return _globe_sun(t)[0] if 224.03 <= t < 254.0 else 0.0
    if shot_name(t) == "summit":
        return 145.0      # the summit looks down the avenue toward the church: the sun stays at the right edge
    return 163.0          # behind Zion's right shoulder, clear of the words


def sun_int(t):
    if globe_view(t):
        if 224.03 <= t < 254.0:
            return 0.10 + 0.65 * _sc(233.8, 235.6, t) - 0.15 * _sc(236.5, 238.8, t)
        return 0.9 if t >= 224.03 else 0.0
    if CODA0 <= t < 238.8:
        if t < 201.73:          # the hush before the dawn: the glow gathers behind Zion
            return 0.55 + 0.35 * _sc(196.5, 201.6, t)
        k = {"sky_stage": 0.72, "summit": 0.66}.get(shot_name(t), 0.82)
        return k + 0.10 * loud(t) + 0.15 * hit_pulse(t, [SLAM3], fall=1.0)
    if 238.8 <= t < 254.07:      # home to everyone on Mount Zion: the sun high, its glare kept small
        return 0.20 + 0.05 * loud(t) + 0.15 * hit_pulse(t, [HIT["final"]], fall=1.2)
    k = (0.22 + 0.12 * _sc(53.0, 82.08, t) + 0.16 * _sc(160.0, 201.73, t) + 0.06 * loud(t))   # a low dawn sun
    return k * (0.45 if stage_view(t) and t >= 160.0 else 1.0)


def rays(t):
    if globe_view(t):
        return 0.45 * _sc(234.4, 235.8, t) * (1.0 - 0.4 * _sc(236.5, 238.8, t)) if t < 254.0 else 0.0
    if CODA0 <= t < 238.8:
        if t < 201.73:
            return 0.12 + 0.30 * _sc(196.5, 201.6, t)
        return 0.38 + 0.08 * loud(t) + 0.25 * hit_pulse(t, [SLAM3], fall=1.2)
    base = 0.12 + 0.35 * _sc(80.0, 83.0, t) + 0.2 * _sc(197.0, 202.0, t)
    r = base * (0.85 + 0.3 * loud(t)) + 0.2 * hit_pulse(t, [SLAM1, SLAM2, SLAM3], fall=1.2)
    return r * (0.25 if stage_view(t) and t >= 160.0 else 1.0)    # the brass cut-ins face the sun: no wash


def _win(a, b, t, f=0.4):
    return float(_sc(a - f, a, t) * (1.0 - _sc(b, b + f, t)))


def glare_calm(t):
    """Round 8: the sun's glow and rays held down where they paled the picture: by half over the coda summit
    3:33.5 to 3:39.5 (f35), swelling back only on the beats; by 40 percent in the slam-2 aftermath 2:51.5 to
    2:54 (f18) so the second climb keeps its colour."""
    b = float(H.beat_pulse(t))
    return (1.0 - 0.5 * _win(213.5, 219.5, t) * (1.0 - 0.8 * b)) * (1.0 - 0.4 * _win(171.5, 174.0, t))


def _rise_aside(t):
    """Round 8 (ZION's epic sun disc, 3:21.73 to 3:26): the coda sun stands higher and to the side of the words."""
    return _win(201.73, 206.0, t, 0.6)


def world():
    """The P3D world settings (built after the core has gathered every thread's shots)."""
    return dict(
        looks=LOOKS,
        look=_look_keys(),
        sun_el=lambda t: max(sun_el(t), 12.0 * _rise_aside(t)) if _rise_aside(t) > 0.0 else sun_el(t),
        sun_az=lambda t: sun_az(t) + (178.0 - sun_az(t)) * _rise_aside(t),
        sun_int=lambda t: sun_int(t) * glare_calm(t), rays=lambda t: rays(t) * glare_calm(t),
        react=dict(beat=0.25, level=0.25),
    )
