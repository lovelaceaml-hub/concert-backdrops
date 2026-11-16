"""Respect as two answering streams opening into a luminous canopy."""
import numpy as np
from p3d.api import lin


def smooth(a, b, t):
    u = np.clip((t-a)/(b-a), 0, 1)
    return u*u*(3-2*u)


class Gate:
    wants_camera = True

    def __init__(self, inner, start=33.16, end=40.21):
        self.inner, self.start, self.end = inner, start, end

    def gain(self, t):
        k = 1-smooth(self.start, self.start+.5, t)*(1-smooth(self.end-.4, self.end, t))
        return k*(self.inner.gain(t) if hasattr(self.inner, 'gain') else 1)

    def sample(self, t, cam):
        if self.gain(t) < .0001:
            return None
        return self.inner.sample(t, cam) if getattr(self.inner, 'wants_camera', False) else self.inner.sample(t)


class ListeningLight:
    """Continuous flowing light, with no human masks or silhouettes."""
    wants_camera = True

    def __init__(self):
        rng = np.random.default_rng(710)
        self.u = np.linspace(0, 1, 1800)
        self.v = rng.random(14000)
        self.q = rng.uniform(-1, 1, len(self.v))
        self.petal = rng.integers(0, 9, len(self.v))
        self.s = rng.random(len(self.v))

    def sample(self, t, cam=None):
        if not 33.16 < t < 40.21:
            return None
        fade = smooth(33.16, 34.0, t)*(1-smooth(39.65, 40.21, t))
        age = t-33.36
        rows = []
        for side, color in [(-1, '#ffdc9b'), (1, '#c8bcff')]:
            u = self.u
            x = side*(5.8*(1-u)+.7*np.sin(2*np.pi*u+age*.7))
            y = -4.8+3.0*u+1.4*np.sin(np.pi*u)
            z = 1.5*np.sin(2*np.pi*u+side*.6+age*.35)
            p = np.column_stack([x, y, z])
            pulse = .35+.65*(.5+.5*np.sin(24*u-age*4.5))**4
            reveal = np.clip(age*.5-u+.15, 0, .25)*4
            rows.append(dict(pos=p, size=.035, color=lin(color)*1.1,
                             alpha=pulse*fade*reveal*.45, kind='soft', emit=.7))
            rows.append(dict(pos=p[::12], size=.12, color=lin(color),
                             alpha=pulse[::12]*fade*reveal[::12]*.035, kind='soft'))
        v, q = self.v, self.q
        opening = smooth(34.0, 38.3, t)
        radius = (1.3+5.2*opening)*v
        angle = self.petal*2*np.pi/9 + q*.35*np.sin(np.pi*v) + age*.12
        x = radius*np.cos(angle)
        z = radius*np.sin(angle)*.8
        y = -3.5 + (1.0+2.6*opening)*v**1.7 + .65*(1-q*q)*np.sin(np.pi*v)
        # An inclined crown reveals the inner curves as it slowly turns.
        yy = y*.87-z*.35
        zz = y*.35+z*.87
        p = np.column_stack([x, yy, zz])
        edge = np.maximum(abs(q)**5, .15)
        alpha = fade*smooth(34.1, 36.0, t)*(.16+.38*edge)
        color = lin('#d5baff')[None, :]*(1-self.s[:, None]) + lin('#ffe2ad')[None, :]*self.s[:, None]
        rows.append(dict(pos=p, size=.042, color=color, alpha=alpha,
                         kind='soft', emit=.5, twinkle=.05, seed=self.s))
        idx = self.s > .987
        rows.append(dict(pos=p[idx], size=.055, color=lin('#fff1ce'),
                         alpha=fade*.35*smooth(35, 37, t), kind='spark', emit=1,
                         twinkle=.15, seed=self.s[idx]))
        for row in rows:
            row.update(reflect=False, fog=False, dof=False, streak=False)
        return rows
