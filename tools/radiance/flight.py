"""Camera choreography for the flight revision, independent of the shared films."""
import numpy as np
from scipy.interpolate import PchipInterpolator
from p3d.camera import Move, Rig


def smooth(a, b, t):
    u = np.clip((np.asarray(t)-a)/(b-a), 0, 1)
    return u*u*u*(u*(u*6-15)+10)


class Flight(Move):
    """Low reflected fly-bys, banked landings, then a climbing barrel roll."""
    def __init__(self, centers, starts, aim):
        super().__init__(0, 62, roll=self.bank, fov=self.lens)
        self.starts = starts
        keys = [(0, (0, 2.6, 12), (0, 4.8, -16)),
                (6.6, (.5, 2.5, 9), (0, 4.3, -19)),
                (7.35, (-3, 5.8, 2), (0, 1.8, -22)),
                (8.35, (-2, 1.1, -9), (0, 2.5, -22))]
        self.angles = np.radians([-12, 16, -18, 12, -15, 21, -18, 15, -18])
        distances = [7.4, 6.7, 7.2, 7.2, 8.6, 6.2, 6.7, 6.2, 8.7]
        for k, (a, c, dist, az) in enumerate(zip(starts, centers, distances, self.angles)):
            for dt, da in [(.35, -.025), (2.95, .025)]:
                p = c + [dist*np.sin(az+da), 1.9, dist*np.cos(az+da)]
                keys.append((float(a+dt), p, aim(p, c+[0, 1.4, 0])))
            if k < 8:
                # Cross beside the lettering and look down at its reflection.
                # The actors have dissolved before this corridor is crossed.
                p = c + [np.sign(az)*3.2, 4.8, 7.0]
                q = c + [0, -2, -5]
                keys.append((float(a+3.5), p, q))
        keys.extend([
            (43.65, (-6, 3, -150), (0, 4, -174)),
            (44.4, (-9, 4.5, -164), (0, 8, -174)),
            (45.2, (-5, 7, -178), (0, 18, -174)),
            (46.2, (2.5, 14, -177), (0, 34, -174)),
            (47.3, (1.5, 27, -172), (0, 51, -174)),
            (48.3, (-1, 40, -170), (0, 60, -174)),
            (49.2, (-9, 49, -158), (0, 50, -174)),
            (50.4, (-14, 52, -151), (0, 50, -174)),
            (52.1, (7, 53, -151), (0, 50, -174)),
            (54.8, (0, 51.3, -158), (0, 50, -174)),
            (62, (0, 51.1, -158.4), (0, 50, -174))])
        self.curve = PchipInterpolator([k[0] for k in keys],
            np.array([np.r_[k[1], (np.asarray(k[2])-k[1])/np.linalg.norm(np.asarray(k[2])-k[1])] for k in keys]), axis=0)

    def pose(self, t):
        v = self.curve(np.clip(t, 0, 62))
        return v[:3], v[:3]+20*v[3:]/np.linalg.norm(v[3:])

    def bank(self, t):
        v = -15*np.sin(np.pi*smooth(6.7, 8.8, t))
        for k, a in enumerate(self.starts[:-1]):
            v += (-1 if k % 2 else 1)*18*np.sin(np.pi*smooth(a+2.98, a+4.2, t))
        return float(v+360*smooth(43.5, 49.2, t))

    def lens(self, t):
        # Wider only in flight; each reading shot has the same legible scale.
        v = 44+10*np.sin(np.pi*smooth(6.7, 8.8, t))
        for a in self.starts[:-1]:
            v += 9*np.sin(np.pi*smooth(a+2.98, a+4.2, t))
        v += 34*smooth(43.4, 46.3, t)*(1-smooth(48.3, 50.5, t))
        return float(v)


def make_camera(centers, starts, aim):
    flight = Flight(centers, starts, aim)
    return Rig([flight], fov=44, aperture=.008, handheld=0, shutter=.72, free=True, right=1.2), flight
