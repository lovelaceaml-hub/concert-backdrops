"""The arch of nine lights, shared by every song file (song.py installs these into the chosen song).

Astra round 0: a line between two lights grows only when BOTH lights are lit, and a light that is lit again
in a later song reports its age from the moment its words arrive, so the shader draws a fresh ring.
Astra round 1, finding 10: a line starts growing only once both of its lights are visible (no head start).
Astra round 1, finding 11: every relight leaves a thin ring that stays round the light for the rest of the
song. RINGS_AT_START (a list of nine numbers, or a dict {star index: rings}) gives a light rings carried
over from earlier songs. A phrase's `arrive` may be one time or a list of times (several relights).
"""
import numpy as np

MAX_RINGS = 6
STAR_VISIBLE = 0.0     # seconds after its `star` time when a light counts as visible (its gather ends here)
LINK_GROW = 1.4        # seconds a line takes to grow


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def _arrivals(p):
    a = p.get("arrive", None)
    if a is None:
        return []
    return sorted(float(x) for x in (a if isinstance(a, (list, tuple)) else [a]))


def rings_at_start(m, i):
    r = getattr(m, "RINGS_AT_START", None)
    if not r:
        return 0.0
    if isinstance(r, dict):
        return float(r.get(i, 0.0))
    return float(r[i]) if i < len(r) else 0.0


def make(m):
    def star_state(t):
        """Per light: (intensity, age of the newest expanding ring or -1, persistent ring count)."""
        out = []
        for i, p in enumerate(m.PHRASES):
            age = t - p["star"]
            if age < -0.2:
                out.append((0.0, -1.0, 0.0))
                continue
            gather = min(max((age + 0.2) / 0.2, 0.0), 1.0)
            base = 0.55 * gather
            flash = np.exp(-max(age, 0.0) * 1.1) * 1.3 if age >= 0 else 0.0
            ring_age = max(age, 0.0)
            rings = rings_at_start(m, i)
            for a in _arrivals(p):
                if t >= a:
                    flash += np.exp(-(t - a) * 1.1) * 0.9   # a softer flare when the light is lit again
                    ring_age = t - a                        # a fresh expanding ring
                    rings += _ss(a + 0.9, a + 2.6, t)       # which settles into a thin ring that stays
            fin = 0.0
            if t > m.NINTH:
                fin = 0.35 * min((t - m.NINTH) / 2.0, 1.0)
            if t > m.TITLE_HIT:
                fin += 0.35 * np.exp(-(t - m.TITLE_HIT) * 0.25) + 0.15
            out.append((base + flash + fin, ring_age, min(rings, float(MAX_RINGS))))
        return out

    def link_state(t):
        out = []
        for i in range(8):
            # both ends must be visible before the line begins to grow
            t1 = max(m.PHRASES[i]["star"], m.PHRASES[i + 1]["star"]) + STAR_VISIBLE
            g = min(max((t - t1) / LINK_GROW, 0.0), 1.0)
            out.append(g * g * (3 - 2 * g))
        return out

    return star_state, link_state
