"""The arch of nine lights, shared by every song file (song.py installs these into the chosen song).

Fixes from Astra round 0: a line between two lights grows only when BOTH lights are lit, and a light that is
lit again in a later song reports its age from the moment its words arrive, so the shader draws a fresh ring.
"""
import numpy as np


def make(m):
    def _arrive(p):
        return p.get("arrive", None)

    def star_state(t):
        out = []
        for p in m.PHRASES:
            age = t - p["star"]
            if age < -0.2:
                out.append((0.0, -1.0))
                continue
            gather = min(max((age + 0.2) / 0.2, 0.0), 1.0)
            base = 0.55 * gather
            flash = np.exp(-max(age, 0.0) * 1.1) * 1.3 if age >= 0 else 0.0
            ring_age = max(age, 0.0)
            a = _arrive(p)
            if a is not None and t >= a:
                flash += np.exp(-(t - a) * 1.1) * 0.9   # a softer flare when the light is lit again
                ring_age = t - a                        # and a fresh ring
            fin = 0.0
            if t > m.NINTH:
                fin = 0.35 * min((t - m.NINTH) / 2.0, 1.0)
            if t > m.TITLE_HIT:
                fin += 0.35 * np.exp(-(t - m.TITLE_HIT) * 0.25) + 0.15
            out.append((base + flash + fin, ring_age))
        return out

    def link_state(t):
        out = []
        for i in range(8):
            t1 = max(m.PHRASES[i]["star"], m.PHRASES[i + 1]["star"])   # both ends must be lit
            g = min(max((t - (t1 - 1.2)) / 1.4, 0.0), 1.0)
            out.append(g * g * (3 - 2 * g))
        return out

    return star_state, link_state
