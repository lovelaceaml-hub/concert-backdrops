"""Living figures (2026-11-15): people of light built on a moving skeleton, not a still picture.

A FIGURES entry with kind="rig" is drawn from a 2D/3D skeleton that is posed every frame:
  person       a robed person (three-quarter view by default), walks with a real stride, robe and sleeves sway
  person_back  the same body seen from behind with a long veil that flows (Heavenly Mother is shown only so)
  child        a smaller person with child proportions
  pair         two people side by side (walking together) or facing each other (embrace)
  hands        two hands with moving fingers that cup, open, offer a light and clasp

About 12,000 sparks are bound to the bones, the robe and the veil. Their positions are recomputed on the CPU
(numpy) for every frame from the posed skeleton, so the whole body moves continuously. Everything is a pure
function of time (no state carried between frames), so any frame renders on its own and the cloud workers that
render the video in parts agree with each other.

Units: a figure's local coordinates are fractions of its height; the feet stand on y = 0, the body faces +x,
z points sideways. The view angle `yaw` turns the body: 0 is a side view, about 0.45 three-quarter, pi/2
front or back.
"""
import math

import numpy as np

TAU = 2.0 * math.pi


def ss(a, b, x):
    u = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0.0, 1.0) if b != a else (np.asarray(x) >= a) * 1.0
    return u * u * (3 - 2 * u)


def _ssf(a, b, x):
    return float(ss(a, b, x))


def _norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


# ---------------------------------------------------------------- poses (actions)
# arm: (upper arm elevation, upper arm azimuth, forearm elevation, forearm azimuth). Elevation 0 hangs down,
# pi/2 points forward (azimuth 0) or out to the side (azimuth pi/2), pi points up. A negative azimuth crosses
# in front of the body toward the other side (prayer, embrace).
HANG = (0.10, 0.30, 0.24, 0.30)
POSES = {
    "stand":   dict(walk=0.0, kneel=0.0, lean=0.0, tilt=0.0, arm_r=HANG, arm_l=HANG, light=0.0),
    "idle":    dict(walk=0.0, kneel=0.0, lean=0.0, tilt=0.0, arm_r=HANG, arm_l=HANG, light=0.0),
    "walk":    dict(walk=1.0, kneel=0.0, lean=0.05, tilt=-0.05, arm_r=HANG, arm_l=HANG),
    "offer":   dict(walk=0.0, lean=0.06, tilt=-0.12, arm_r=(0.55, 0.15, 1.45, 0.12), arm_l=(0.55, 0.15, 1.45, 0.12),
                    light=1.0),
    "reach":   dict(walk=0.0, lean=0.08, tilt=0.0, arm_r=(1.30, 0.10, 1.50, 0.05), arm_l=HANG),
    "rise":    dict(walk=0.0, lean=-0.04, tilt=0.30, arm_r=(2.30, 0.95, 2.65, 0.75), arm_l=(2.30, 0.95, 2.65, 0.75)),
    "open":    dict(walk=0.0, lean=-0.02, tilt=0.12, arm_r=(1.30, 1.25, 1.70, 1.30), arm_l=(1.30, 1.25, 1.70, 1.30)),
    "bless":   dict(walk=0.0, lean=-0.02, tilt=0.18, arm_r=(1.75, 1.15, 2.05, 1.10), arm_l=(1.75, 1.15, 2.05, 1.10)),
    "pray":    dict(walk=0.0, lean=0.04, tilt=-0.20, arm_r=(0.35, 0.40, 1.95, -1.05), arm_l=(0.35, 0.40, 1.95, -1.05)),
    "embrace": dict(walk=0.0, lean=0.10, tilt=-0.10, arm_r=(1.10, 0.35, 1.45, -0.95), arm_l=(1.10, 0.35, 1.45, -0.95)),
    "bow":     dict(walk=0.0, lean=0.38, tilt=-0.35, arm_r=(0.30, 0.25, 1.30, -0.70), arm_l=(0.30, 0.25, 1.30, -0.70)),
    "kneel":   dict(walk=0.0, kneel=1.0, lean=0.12, tilt=-0.30, arm_r=(0.35, 0.40, 1.95, -1.05),
                    arm_l=(0.35, 0.40, 1.95, -1.05)),
    "wave":    dict(walk=0.0, lean=0.0, tilt=0.05, arm_r=(2.35, 0.55, 2.75, 0.40), arm_l=HANG),
    "turn":    dict(yaw=1.35),
    "face":    dict(yaw=0.0),
    # hands preset
    "cup":     dict(hx=0.105, hy=0.25, rot=0.22, curl=0.72, spread=0.10, light=0.0),
    "closed":  dict(hx=0.10, hy=0.24, rot=0.28, curl=0.95, spread=0.05, light=0.0),
    "hands_open": dict(hx=0.15, hy=0.26, rot=-0.10, curl=0.08, spread=0.85, light=0.35),
    "hands_offer": dict(hx=0.17, hy=0.33, rot=-0.55, curl=0.22, spread=0.55, light=1.0),
    "clasp":   dict(hx=0.042, hy=0.26, rot=0.10, curl=0.05, spread=0.0, light=0.0),
    "release": dict(hx=0.18, hy=0.35, rot=-0.70, curl=0.12, spread=0.75, light=1.0, orb_rise=1.0),
}
NUMERIC = ("walk", "kneel", "lean", "tilt", "light", "yaw", "hx", "hy", "rot", "curl", "spread", "orb_rise", "gap")
ARMS = ("arm_r", "arm_l")


def _blend(a, b, w):
    out = dict(a)
    for k, v in b.items():
        if k in ARMS:
            av = a.get(k, HANG)
            out[k] = tuple(x + (y - x) * w for x, y in zip(av, v))
        elif k in NUMERIC:
            out[k] = a.get(k, 0.0) + (float(v) - a.get(k, 0.0)) * w
    return out


def pose_at(actions, t, base, blend=0.9):
    """Blends the actions in order: each one eases in over `blend` seconds from its start time.
    An action is (time, name) or (time, name, {overrides}) or (time, {overrides})."""
    p = dict(base)
    for a in actions:
        ta = float(a[0])
        if t < ta:
            break
        if isinstance(a[1], str):
            name = a[1]
            if name == "open" and base.get("_hands"):
                name = "hands_open"
            if name == "offer" and base.get("_hands"):
                name = "hands_offer"
            tgt = dict(POSES.get(name, {}))
            if len(a) > 2 and isinstance(a[2], dict):
                tgt.update(a[2])
        else:
            tgt = dict(a[1])
        dur = float(tgt.pop("blend", blend))
        p = _blend(p, tgt, _ssf(ta, ta + dur, t))
    return p


# ---------------------------------------------------------------- proportions
ADULT = dict(hip=0.535, thigh=0.255, shin=0.245, ankle=0.035, chest=0.70, neck=0.835, head=0.915, head_r=0.060,
             shoulder_y=0.805, shoulder_z=0.102, upper=0.165, fore=0.150, hip_z=0.050,
             torso=((0.072, 0.092), (0.080, 0.104), (0.030, 0.030)), waist=0.555, hem=0.055,
             robe_top=(0.078, 0.098), robe_flare=(0.060, 0.070), stride=0.62)
CHILD = dict(hip=0.500, thigh=0.235, shin=0.230, ankle=0.035, chest=0.655, neck=0.780, head=0.875, head_r=0.088,
             shoulder_y=0.755, shoulder_z=0.098, upper=0.150, fore=0.135, hip_z=0.050,
             torso=((0.078, 0.098), (0.084, 0.106), (0.034, 0.034)), waist=0.515, hem=0.085,
             robe_top=(0.082, 0.100), robe_flare=(0.050, 0.060), stride=0.55)


def _sample_unit_disc(rng, n, edge=0.6):
    """Random points in a disc (2D), with a share `edge` pushed toward the rim so the body has a bright edge."""
    th = rng.random(n) * TAU
    r = np.sqrt(rng.random(n))
    rim = rng.random(n) < edge
    r[rim] = 0.82 + 0.18 * rng.random(rim.sum())
    return th, r


# ---------------------------------------------------------------- a robed person
class Person:
    """One robed person. Joints are 3D in the figure's local frame (feet on y=0, facing +x)."""

    def __init__(self, rng, n, child=False, veil=False, x0=0.0, facing=1.0, phase=0.0, yaw=0.45, z0=0.0):
        self.P = dict(CHILD if child else ADULT)
        self.veil = veil
        self.x0, self.facing, self.phase, self.yaw0, self.z0 = x0, facing, phase, yaw, z0
        P = self.P
        # share of sparks per part
        parts = [("robe", 0.36), ("torso", 0.14), ("head", 0.07), ("arm", 0.16), ("hand", 0.04), ("leg", 0.07),
                 ("foot", 0.04)]
        if veil:
            parts = [(k, v * 0.80) for k, v in parts] + [("veil", 0.20)]
        tot = sum(v for _, v in parts)
        counts = {k: int(n * v / tot) for k, v in parts}
        counts["robe"] += n - sum(counts.values())
        self.n = n
        self.g = {}
        # robe: (v down 0..1, angle round the body, radial fraction)
        k = counts["robe"]
        th, r = _sample_unit_disc(rng, k, edge=0.72)
        self.g["robe"] = dict(v=rng.random(k) ** 0.85, th=th, r=r, seed=rng.random(k))
        # torso: (s up 0..1, angle, radial)
        k = counts["torso"]
        th, r = _sample_unit_disc(rng, k, edge=0.65)
        self.g["torso"] = dict(s=rng.random(k), th=th, r=r)
        # head: a soft glow (no face): a ball, denser at the centre
        k = counts["head"]
        d = rng.normal(size=(k, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        rr = rng.random(k) ** 0.6
        self.g["head"] = dict(d=d, r=rr)
        # arms: side (+1 right/near, -1 left/far), segment (0 upper, 1 fore), s along, disc offset
        k = counts["arm"]
        side = np.where(rng.random(k) < 0.5, 1.0, -1.0)
        seg = (rng.random(k) < 0.52).astype(int)
        th, r = _sample_unit_disc(rng, k, edge=0.6)
        self.g["arm"] = dict(side=side, seg=seg, s=rng.random(k), th=th, r=r)
        k = counts["hand"]
        self.g["hand"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), s=rng.random(k) ** 0.8,
                              d=_unit3(rng, k), r=rng.random(k) ** 0.5)
        k = counts["leg"]
        th, r = _sample_unit_disc(rng, k, edge=0.5)
        self.g["leg"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), seg=(rng.random(k) < 0.5).astype(int),
                             s=rng.random(k), th=th, r=r)
        k = counts["foot"]
        self.g["foot"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), s=rng.random(k), d=_unit3(rng, k),
                              r=rng.random(k) ** 0.5)
        if veil:
            k = counts["veil"]
            a = rng.random(k) * 2 - 1
            edge = rng.random(k) < 0.25
            a[edge] = np.sign(a[edge]) * (0.9 + 0.1 * rng.random(edge.sum()))
            self.g["veil"] = dict(a=a, v=rng.random(k) ** 0.9, seed=rng.random(k))
        self.order = [k for k, _ in parts]
        self.sizes = [counts[k] for k in self.order]

    # ------------------------------------------------------------ the skeleton
    def joints(self, t, pose, d, walk, vel):
        """Posed joints at time t. d: distance walked (local units, along facing). vel: (now, smoothed) speed."""
        P = self.P
        stride = P["stride"]
        # breath and weight shift: never fully still
        br = math.sin(TAU * t / 4.3 + self.phase * 3.0)
        sway = math.sin(TAU * t / 6.1 + self.phase * 5.0)
        kneel = pose.get("kneel", 0.0)
        # feet
        feet = {}
        hip_x = 0.0
        beta = 0.62
        Pph = d / stride + self.phase
        for side, off in ((1.0, 0.0), (-1.0, 0.5)):
            u_all = Pph + off
            kk = math.floor(u_all)
            u = u_all - kk
            if u < beta:
                fx = stride * (kk - off - self.phase + beta / 2.0) - d
                fy = P["ankle"] + 0.022 * _ssf(0.80 * beta, beta, u)
                pitch = 0.35 * _ssf(0.80 * beta, beta, u)
            else:
                s = (u - beta) / (1.0 - beta)
                se = s * s * (3 - 2 * s)
                fx = stride * (kk - off - self.phase + beta / 2.0 + se) - d
                fy = P["ankle"] + 0.022 * (1 - se) + 0.075 * math.sin(math.pi * s) ** 1.2
                pitch = 0.35 * (1 - s) - 0.25 * math.sin(math.pi * s)
            # standing feet, a little apart, one slightly forward; weight shifts with the sway
            st_x = 0.03 * side + 0.004 * sway
            ax = st_x + (fx - st_x) * walk
            ay = P["ankle"] + (fy - P["ankle"]) * walk
            feet[side] = [ax, ay, side * P["hip_z"] * 0.9, pitch * walk, u]
        # kneeling: the near leg kneels forward, the far knee rests on the ground
        if kneel > 0:
            feet[1.0][0] += (0.20 - feet[1.0][0]) * kneel
            feet[-1.0][0] += (-0.33 - feet[-1.0][0]) * kneel
            feet[-1.0][1] += (0.05 - feet[-1.0][1]) * kneel
        L = P["thigh"] + P["shin"]
        hip_y = P["hip"] - 0.010 * walk + 0.002 * br
        for side in (1.0, -1.0):
            dx = feet[side][0] - hip_x
            hip_y = min(hip_y, feet[side][1] + math.sqrt(max((L * 0.997) ** 2 - dx * dx, 0.01)))
        hip_y += (0.30 - hip_y) * kneel
        lean = pose.get("lean", 0.0) + 0.04 * walk
        J = {}
        J["hip"] = np.array([hip_x + 0.006 * sway * (1 - walk), hip_y, 0.0])
        # spine: lean forward (rotate round the hip), a little counter-sway
        up = np.array([math.sin(lean), math.cos(lean), 0.0])
        J["chest"] = J["hip"] + up * (P["chest"] - P["hip"]) + np.array([0.0, 0.004 * br, 0.0])
        J["neck"] = J["hip"] + up * (P["neck"] - P["hip"]) + np.array([0.0, 0.005 * br, 0.0])
        tilt = pose.get("tilt", 0.0) + 0.03 * math.sin(TAU * t / 5.3 + self.phase)
        hd = np.array([math.sin(lean - tilt * 0.6), math.cos(lean - tilt * 0.6), 0.0])
        J["head"] = J["neck"] + hd * (P["head"] - P["neck"])
        # shoulders counter-rotate against the stride
        twist = 0.0
        legs = {}
        for side in (1.0, -1.0):
            ax, ay, az, pitch, u = feet[side]
            H = np.array([J["hip"][0], hip_y, side * P["hip_z"]])
            A = np.array([ax, ay, az])
            knee = _ik(H, A, P["thigh"], P["shin"])
            if kneel > 0 and side < 0:
                kn = np.array([-0.07, 0.035, az])
                knee = knee + (kn - knee) * kneel
            toe = A + np.array([0.075 * math.cos(pitch) + 0.0, -0.028 - 0.06 * math.sin(pitch) * 0.5, 0.0])
            legs[side] = (H, knee, A, toe)
            twist += -side * (ax - J["hip"][0])
        twist = max(-0.25, min(0.25, twist)) * 0.18
        J["legs"] = legs
        sh_y = J["hip"][1] + (P["shoulder_y"] - P["hip"]) * math.cos(lean)
        arms = {}
        for side, key in ((1.0, "arm_r"), (-1.0, "arm_l")):
            a = list(pose.get(key, HANG))
            # natural swing opposite to the leg on the same side
            fx = legs[side][2][0] - J["hip"][0]
            a[0] += -1.25 * fx * walk
            a[2] += -1.55 * fx * walk + 0.10 * walk
            # a breath of motion in the hands even when still
            a[0] += 0.03 * math.sin(TAU * t / 3.7 + side + self.phase * 2)
            a[2] += 0.05 * math.sin(TAU * t / 3.1 + side * 2 + self.phase)
            S = np.array([J["hip"][0] + (P["shoulder_y"] - P["hip"]) * math.sin(lean) + side * twist * 0.05,
                          sh_y + 0.004 * br, side * P["shoulder_z"]])
            d1 = _armdir(a[0], a[1], side)
            E = S + d1 * P["upper"]
            d2 = _armdir(a[2], a[3], side)
            Hn = E + d2 * P["fore"]
            arms[side] = (S, E, Hn, d2)
        J["arms"] = arms
        J["feet"] = feet
        return J

    # ------------------------------------------------------------ the sparks
    def points(self, t, J, pose, vel, lag):
        """Sparks for this body (local 3D, n x 3) and a brightness per spark."""
        P = self.P
        out, bright = [], []
        hip, chest, neck, head = J["hip"], J["chest"], J["neck"], J["head"]
        legs, arms = J["legs"], J["arms"]
        br = math.sin(TAU * t / 4.3 + self.phase * 3.0)
        # ---- robe: an A-line skirt whose cross-section follows both legs, so the stride shows through it
        g = self.g["robe"]
        v = (g["v"] - 0.035 * t) % 1.0                       # the light flows slowly up the robe
        y_top = hip[1] + (P["waist"] - P["hip"])
        hem_wave = 0.010 * np.sin(3 * g["th"] + 2.1 * t) + 0.006 * np.sin(5 * g["th"] - 1.6 * t + 1.0)
        y = y_top + (P["hem"] + hem_wave - y_top) * v
        # leg points at this height (fraction along each leg)
        xs = []
        for side in (1.0, -1.0):
            H, K, A, _ = legs[side]
            f = np.clip((H[1] - y) / max(H[1] - A[1], 1e-3), 0.0, 1.0)
            l1 = np.clip(f * 2.0, 0, 1)
            l2 = np.clip(f * 2.0 - 1.0, 0, 1)
            x = np.where(f < 0.5, H[0] + (K[0] - H[0]) * l1, K[0] + (A[0] - K[0]) * l2)
            xs.append(x)
        cx = 0.5 * (xs[0] + xs[1])
        half = 0.5 * np.abs(xs[0] - xs[1])
        ax = P["robe_top"][0] + P["robe_flare"][0] * v ** 1.3 + half * 0.62
        az = P["robe_top"][1] + P["robe_flare"][1] * v ** 1.3
        # the hem lags behind the walk and swings on when she stops (secondary motion)
        cx = cx + lag * v ** 1.6 + 0.010 * v * v * math.sin(TAU * t / 2.7 + self.phase)
        breathe = 1.0 + 0.05 * np.sin(1.3 * t + g["th"] * 3 + v * 5)
        rr = g["r"] * breathe
        pts = np.stack([cx + ax * rr * np.cos(g["th"]), y, az * rr * np.sin(g["th"])], axis=1)
        out.append(pts)
        bright.append(0.80 + 0.35 * (g["r"] > 0.82) + 0.25 * v - 0.6 * ss(0.92, 1.0, v) - 0.4 * (1 - ss(0.0, 0.06, v)))
        # ---- torso (up from the hip to the neck), light flowing upward
        g = self.g["torso"]
        s = (g["s"] + 0.05 * t) % 1.0
        r0, r1, r2 = P["torso"]
        seg1 = s < 0.68
        u1 = s / 0.68
        u2 = np.clip((s - 0.68) / 0.32, 0.0, 1.0)
        c = np.where(seg1[:, None], hip + (chest - hip) * u1[:, None], chest + (neck - chest) * u2[:, None])
        rx = np.where(seg1, r0[0] + (r1[0] - r0[0]) * u1, r1[0] + (r2[0] - r1[0]) * u2 ** 0.7)
        rz = np.where(seg1, r0[1] + (r1[1] - r0[1]) * u1, r1[1] + (r2[1] - r1[1]) * u2 ** 0.7)
        rx = rx * (1 + 0.02 * br)
        pts = c + np.stack([rx * g["r"] * np.cos(g["th"]), np.zeros_like(s), rz * g["r"] * np.sin(g["th"])], axis=1)
        out.append(pts)
        bright.append(0.85 + 0.3 * (g["r"] > 0.82))
        # ---- head: a soft ball of light (no face)
        g = self.g["head"]
        hr = P["head_r"] * (1 + 0.03 * math.sin(t * 1.7 + self.phase))
        out.append(head + g["d"] * (hr * g["r"])[:, None] * np.array([0.92, 1.08, 0.92]))
        bright.append(1.15 - 0.35 * g["r"])
        # ---- arms with robe sleeves that widen toward the wrist and trail the motion
        g = self.g["arm"]
        pts = np.zeros((len(g["s"]), 3))
        br_a = np.ones(len(g["s"]))
        for side in (1.0, -1.0):
            S, E, Hn, d2 = arms[side]
            for seg in (0, 1):
                m = (g["side"] == side) & (g["seg"] == seg)
                if not m.any():
                    continue
                s = g["s"][m]
                A, B = (S, E) if seg == 0 else (E, Hn)
                c = A + (B - A) * s[:, None]
                rad = 0.030 + 0.002 * s if seg == 0 else 0.032 + 0.030 * s ** 1.5
                if seg == 1:
                    c = c + lag * 0.25 * (s ** 2)[:, None] * np.array([1.0, 0.0, 0.0])
                    c = c + np.array([0.0, -1.0, 0.0]) * (0.018 * s ** 2)[:, None]   # the sleeve hangs
                pts[m] = c + _disc3(B - A, g["th"][m], g["r"][m] * rad)
                br_a[m] = 0.85 + 0.3 * (g["r"][m] > 0.8)
        out.append(pts)
        bright.append(br_a)
        # ---- hands: small soft hands out of the sleeves
        g = self.g["hand"]
        pts = np.zeros((len(g["s"]), 3))
        for side in (1.0, -1.0):
            S, E, Hn, d2 = arms[side]
            m = g["side"] == side
            c = Hn + d2 * (0.055 * g["s"][m])[:, None]
            pts[m] = c + g["d"][m] * (0.020 * g["r"][m] * (1.0 - 0.4 * g["s"][m]))[:, None]
        out.append(pts)
        bright.append(np.full(len(g["s"]), 1.05))
        # ---- legs under the robe (faint) and the feet that step out under the hem
        g = self.g["leg"]
        pts = np.zeros((len(g["s"]), 3))
        for side in (1.0, -1.0):
            H, K, A, toe = legs[side]
            for seg in (0, 1):
                m = (g["side"] == side) & (g["seg"] == seg)
                a0, b0 = (H, K) if seg == 0 else (K, A)
                c = a0 + (b0 - a0) * g["s"][m][:, None]
                pts[m] = c + _disc3(b0 - a0, g["th"][m], g["r"][m] * (0.036 if seg == 0 else 0.026))
        out.append(pts)
        bright.append(np.full(len(g["s"]), 0.75))
        g = self.g["foot"]
        pts = np.zeros((len(g["s"]), 3))
        for side in (1.0, -1.0):
            H, K, A, toe = legs[side]
            m = g["side"] == side
            c = A + (toe - A) * g["s"][m][:, None]
            pts[m] = c + g["d"][m] * (0.017 * g["r"][m])[:, None] * np.array([1.0, 0.7, 1.0])
        out.append(pts)
        bright.append(np.full(len(g["s"]), 1.0))
        # ---- veil: from the crown over the back of the head down to the waist; it ripples and streams
        if self.veil:
            g = self.g["veil"]
            v = g["v"]
            a = g["a"]
            crown = head + np.array([-0.012, P["head_r"] * 1.05, 0.0])
            nape = head + np.array([-0.050, -0.055, 0.0])
            back = chest + np.array([-0.095, -0.03, 0.0])
            low = hip + np.array([-0.11, -0.02, 0.0])
            c = np.where((v < 0.22)[:, None], crown + (nape - crown) * (v / 0.22)[:, None],
                         np.where((v < 0.58)[:, None], nape + (back - nape) * ((v - 0.22) / 0.36)[:, None],
                                  back + (low - back) * ((v - 0.58) / 0.42)[:, None]))
            width = np.interp(v, [0.0, 0.22, 0.58, 1.0], [0.062, 0.100, 0.150, 0.172])
            wind = 0.5 + 0.5 * math.sin(TAU * t / 7.0)
            ph = TAU * (0.9 * v - 0.30 * t) + 1.4 * a
            dz = v * v * (0.030 * np.sin(ph) + 0.022 * wind + 0.012 * np.sin(TAU * (1.7 * v - 0.45 * t) + a * 3))
            dx = -v * v * (0.030 + 0.020 * np.sin(TAU * (0.7 * v - 0.23 * t) + a * 2)) + lag * 0.6 * v * v
            dy = 0.012 * v * v * np.sin(TAU * (1.1 * v - 0.4 * t) + a)
            # the veil wraps round the shoulders at the sides
            wrap = -0.05 * (np.abs(a) ** 2) * ss(0.1, 0.5, v)
            pts = np.stack([c[:, 0] + dx + wrap, c[:, 1] + dy, a * width + dz], axis=1)
            out.append(pts)
            edge = (np.abs(a) > 0.88) | (v > 0.93)
            bright.append(0.75 + 0.55 * edge + 0.25 * np.sin(ph * 0.5) ** 2)
        pts = np.vstack(out)
        b = np.concatenate([np.broadcast_to(x, (len(o),)) for x, o in zip(bright, out)])
        return pts, b

    def project(self, pts, yaw):
        """Local 3D -> local 2D (x along the screen, y up). The body sits at x0 and faces `facing`."""
        cy, sy = math.cos(yaw), math.sin(yaw)
        x = pts[:, 0] * cy + pts[:, 2] * sy
        return np.stack([self.x0 + self.facing * x, pts[:, 1]], axis=1)


def _unit3(rng, n):
    d = rng.normal(size=(n, 3))
    return d / np.linalg.norm(d, axis=1, keepdims=True)


def _disc3(axis, th, r):
    """Offsets in the disc perpendicular to `axis` (one axis for all points)."""
    a = _norm(np.asarray(axis, dtype=np.float64))
    ref = np.array([0.0, 0.0, 1.0]) if abs(a[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = _norm(np.cross(a, ref))
    e2 = np.cross(a, e1)
    return (np.cos(th) * r)[:, None] * e1 + (np.sin(th) * r)[:, None] * e2


def _armdir(el, az, side):
    return np.array([math.sin(el) * math.cos(az), -math.cos(el), side * math.sin(el) * math.sin(az)])


def _ik(H, A, l1, l2):
    """Knee of a two-bone leg from hip H to ankle A, bending forward (+x)."""
    D = A - H
    d2 = D[:2]
    dist = float(np.linalg.norm(d2))
    dist = min(max(dist, 1e-4), (l1 + l2) * 0.9999)
    u = d2 / max(np.linalg.norm(d2), 1e-6)
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    n = np.array([-u[1], u[0]])
    if n[0] < 0:
        n = -n
    k2 = H[:2] + u * a + n * h
    return np.array([k2[0], k2[1], H[2] + (A[2] - H[2]) * (a / dist)])


# ---------------------------------------------------------------- two hands
class Hands:
    """Two hands in front view, forearms in wide sleeves rising from below. Fingers curl and open in a wave."""
    FINGERS = ((-0.050, 0.150, 0.20), (-0.017, 0.170, 0.06), (0.017, 0.160, -0.06), (0.048, 0.125, -0.20))

    def __init__(self, rng, n):
        parts = [("palm", 0.20), ("finger", 0.36), ("thumb", 0.08), ("sleeve", 0.24), ("orb", 0.12)]
        counts = {k: int(n * v) for k, v in parts}
        counts["palm"] += n - sum(counts.values())
        self.g = {}
        k = counts["palm"]
        th, r = _sample_unit_disc(rng, k, edge=0.22)
        self.g["palm"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), th=th, r=r)
        k = counts["finger"]
        self.g["finger"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), f=rng.integers(0, 4, k),
                                s=rng.random(k), th=rng.random(k) * TAU, r=rng.random(k) ** 0.5)
        k = counts["thumb"]
        self.g["thumb"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), s=rng.random(k),
                               th=rng.random(k) * TAU, r=rng.random(k) ** 0.5)
        k = counts["sleeve"]
        th, r = _sample_unit_disc(rng, k, edge=0.7)
        self.g["sleeve"] = dict(side=np.where(rng.random(k) < 0.5, 1.0, -1.0), s=rng.random(k), th=th, r=r)
        k = counts["orb"]
        self.g["orb"] = dict(d=_unit3(rng, k), r=rng.random(k) ** 0.45, seed=rng.random(k))
        self.order = [k for k, _ in parts]
        self.n = n

    def joints(self, t, pose):
        J = {}
        curl = pose.get("curl", 0.5)
        spread = pose.get("spread", 0.3)
        rot = pose.get("rot", 0.0)
        for side in (1.0, -1.0):
            ph = 0.0 if side > 0 else 1.3
            wx = side * (pose.get("hx", 0.12) + 0.004 * math.sin(t * 0.9 + ph))
            wy = pose.get("hy", 0.25) + 0.006 * math.sin(TAU * t / 4.0 + ph)
            # the hand turns: positive rot tips the fingers toward the middle
            ang = -side * rot + 0.04 * math.sin(t * 1.1 + ph)
            up = np.array([math.sin(ang), math.cos(ang)])
            rt = np.array([up[1], -up[0]]) * side       # toward the outer side of this hand
            W = np.array([wx, wy])
            palm = W + up * 0.075
            fingers = []
            for i, (fx, flen, fang) in enumerate(self.FINGERS):
                # the outer fingers start the wave; each finger breathes on its own
                wave = 0.10 * math.sin(TAU * t / 2.6 - i * 0.7 + ph)
                c = min(max(curl + wave * (0.4 + curl), 0.0), 1.05)
                base = palm + up * 0.072 + rt * (fx * 1.0)
                a = ang - side * (fang * (0.35 + 1.1 * spread)) - side * 0.15 * c
                pts = [base]
                seglen = (0.46, 0.31, 0.23)
                p = base
                for j, sl in enumerate(seglen):
                    a -= side * (0.45 * c) * (1.0 if j else 0.6)
                    L = flen * sl * (1.0 - 0.62 * math.sin(min(c, 1.0) * math.pi / 2) * (0.5 + 0.25 * j))
                    p = p + np.array([math.sin(a), math.cos(a)]) * L
                    pts.append(p)
                fingers.append(pts)
            # the thumb from the inner side of the palm
            tb = palm + rt * (-0.055) + up * (-0.015)
            ta = ang - side * (0.75 + 0.45 * spread) + side * 0.9 * curl
            t1 = tb + np.array([math.sin(ta), math.cos(ta)]) * 0.060
            ta2 = ta + side * 0.5 * curl
            t2 = t1 + np.array([math.sin(ta2), math.cos(ta2)]) * 0.050
            # forearm in a sleeve, from below the frame of the hands
            elbow = W + np.array([side * 0.07, -0.20])
            J[side] = dict(W=W, palm=palm, up=up, rt=rt, fingers=fingers, thumb=(tb, t1, t2), elbow=elbow)
        light = pose.get("light", 0.0)
        rise = pose.get("orb_rise", 0.0)
        J["orb"] = np.array([0.0, 0.50 + 0.10 * light + 0.40 * rise + 0.008 * math.sin(t * 1.4)])
        J["orb_r"] = 0.10 * light * (1.0 + 0.06 * math.sin(t * 2.3))
        J["light"] = light
        return J

    def points(self, t, J, pose):
        out, bright = [], []
        g = self.g["palm"]
        pts = np.zeros((len(g["th"]), 2))
        for side in (1.0, -1.0):
            m = g["side"] == side
            h = J[side]
            sy = np.sin(g["th"][m])
            off = (np.cos(g["th"][m]) * g["r"][m] * (0.058 - 0.010 * np.clip(-sy, 0, 1)))[:, None] * h["rt"] + \
                  (sy * g["r"][m] * 0.078)[:, None] * h["up"]
            pts[m] = h["palm"] + off
        out.append(pts)
        bright.append(0.85 + 0.15 * g["r"])
        g = self.g["finger"]
        pts = np.zeros((len(g["s"]), 2))
        for side in (1.0, -1.0):
            h = J[side]
            for i in range(4):
                m = (g["side"] == side) & (g["f"] == i)
                if not m.any():
                    continue
                ch = h["fingers"][i]
                s = g["s"][m] * 3.0
                j = np.minimum(s.astype(int), 2)
                u = (s - j)[:, None]
                A = np.array(ch)[j]
                B = np.array(ch)[j + 1]
                c = A + (B - A) * u
                rad = 0.0165 - 0.003 * j
                pts[m] = c + np.stack([np.cos(g["th"][m]), np.sin(g["th"][m])], 1) * (g["r"][m] * rad)[:, None]
        out.append(pts)
        bright.append(1.0 + 0.25 * g["s"])
        g = self.g["thumb"]
        pts = np.zeros((len(g["s"]), 2))
        for side in (1.0, -1.0):
            m = g["side"] == side
            tb, t1, t2 = J[side]["thumb"]
            s = g["s"][m] * 2
            c = np.where((s < 1)[:, None], tb + (t1 - tb) * s[:, None], t1 + (t2 - t1) * (s - 1)[:, None])
            pts[m] = c + np.stack([np.cos(g["th"][m]), np.sin(g["th"][m])], 1) * (g["r"][m] * 0.018)[:, None]
        out.append(pts)
        bright.append(np.full(len(g["s"]), 1.1))
        g = self.g["sleeve"]
        pts = np.zeros((len(g["s"]), 2))
        for side in (1.0, -1.0):
            m = g["side"] == side
            h = J[side]
            s = g["s"][m]
            A, B = h["elbow"], h["W"] - h["up"] * 0.02
            c = A + (B - A) * s[:, None]
            ax = _norm(B - A)
            nrm = np.array([-ax[1], ax[0]])
            rad = 0.040 + 0.040 * s ** 1.6
            flow = 0.008 * np.sin(TAU * (s * 1.3 - 0.35 * t) + side)
            pts[m] = c + nrm[None, :] * (g["r"][m] * np.cos(g["th"][m]) * rad + flow)[:, None]
        out.append(pts)
        bright.append((0.70 + 0.4 * (g["r"] > 0.85)) * ss(0.0, 0.6, g["s"]))   # the sleeves fade out below
        # the offered light: a soft orb that breathes above the palms
        g = self.g["orb"]
        sw = 0.6 + 0.4 * np.sin(t * 2.0 + g["seed"] * 30)
        pts = J["orb"][None, :] + g["d"][:, :2] * (g["r"] * J["orb_r"])[:, None]
        out.append(pts)
        bright.append(J["light"] * (1.6 - 0.8 * g["r"]) * sw)
        pts = np.vstack(out)
        b = np.concatenate([np.broadcast_to(x, (len(o),)) for x, o in zip(bright, out)])
        return pts, b


# ---------------------------------------------------------------- one FIGURES entry
PRESETS = ("person", "person_back", "child", "pair", "hands")


class Rig:
    """A living figure. place(t) gives where it stands; sparks(t) the sparks on screen."""

    def __init__(self, meta, aspect, value, seed=0):
        self.m = meta
        self.aspect = aspect
        self.value = value            # value(meta, key, default, t): the figure's x, y, height at t
        self.preset = meta.get("preset", "person")
        if self.preset not in PRESETS:
            raise ValueError(f"FIGURES: unknown rig preset {self.preset!r} (choose from {', '.join(PRESETS)})")
        n = int(meta.get("particles", 12000))
        rng = np.random.default_rng(4321 + seed)
        self.t0, self.t1 = float(meta["t0"]), float(meta["t1"])
        self.tend = self.t1 + float(meta.get("dissolve", 3.5))
        # facing: from the key, else the way it moves
        f = meta.get("facing", None)
        if f is None:
            dx = self.value(meta, "x", 0.5, self.t1) - self.value(meta, "x", 0.5, self.t0)
            f = "left" if dx < -1e-4 else "right"
        self.face = -1.0 if f == "left" else 1.0
        if meta.get("flip"):
            self.face = -self.face
        actions = list(meta.get("actions", []))
        self.actions = sorted(actions, key=lambda a: float(a[0]))
        yaw = meta.get("yaw", None)
        self.bodies = []
        if self.preset == "hands":
            self.hands = Hands(rng, n)
            self.base = dict(POSES["cup"], _hands=True)
        else:
            self.hands = None
            if self.preset == "pair":
                together = meta.get("together", True)
                gap = float(meta.get("gap", 0.30))
                y0 = 0.45 if yaw is None else float(yaw)
                if together:
                    self.bodies = [Person(rng, n // 2, x0=-gap * 0.45, phase=0.0, yaw=y0, veil=False),
                                   Person(rng, n - n // 2, x0=gap * 0.45, phase=0.47, yaw=y0, veil=True)]
                    self.bodies[0].z0, self.bodies[1].z0 = -gap * 0.3, gap * 0.3
                else:
                    self.bodies = [Person(rng, n // 2, x0=-gap / 2, facing=1.0, yaw=y0),
                                   Person(rng, n - n // 2, x0=gap / 2, facing=-1.0, yaw=y0, veil=True, phase=0.3)]
                self.gap = gap
                self.together = together
            else:
                child = self.preset == "child"
                back = self.preset == "person_back"
                y0 = (math.pi / 2 if back else 0.45) if yaw is None else float(yaw)
                veil = bool(meta.get("veil", back))
                self.bodies = [Person(rng, n, child=child, veil=veil, yaw=y0)]
            self.base = dict(POSES["stand"], yaw=self.bodies[0].yaw0)
            if self.preset == "pair":
                self.base["gap"] = self.gap
        self.n = n
        self.stride = float(meta.get("stride", self.bodies[0].P["stride"] if self.bodies else 0.6))
        for b in self.bodies:
            b.P["stride"] = self.stride
        # the walked distance, integrated once (deterministic: any frame can be rendered on its own)
        dt = 1.0 / 120.0
        self.tab_t = np.arange(self.t0 - 1.0, self.tend + 1.0, dt)
        xs = np.array([self.value(meta, "x", 0.5, t) for t in self.tab_t])
        hs = np.array([self.value(meta, "height", 0.34, t) for t in self.tab_t])
        vx = np.gradient(xs, dt) * self.aspect / np.maximum(hs, 1e-3) * self.face   # local units per second
        vx += float(meta.get("speed", 0.0))
        self.tab_v = vx
        self.tab_d = np.concatenate([[0.0], np.cumsum(0.5 * (vx[1:] + vx[:-1]) * dt)])
        k = int(0.6 / dt)
        ker = np.ones(k) / k
        self.tab_vs = np.convolve(np.pad(vx, (k - 1, 0), mode="edge"), ker, mode="valid")   # trailing mean
        self.auto_walk = bool(meta.get("auto_walk", self.preset != "hands"))

    # ------------------------------------------------------------ state
    def dist(self, t):
        return float(np.interp(t, self.tab_t, self.tab_d))

    def vel(self, t):
        return float(np.interp(t, self.tab_t, self.tab_v)), float(np.interp(t, self.tab_t, self.tab_vs))

    def pose(self, t):
        return pose_at(self.actions, t, self.base, float(self.m.get("blend", 0.9)))

    def skeleton(self, t):
        """Joints of every body at t (local units), for checks and for the sparks."""
        p = self.pose(t)
        if self.hands is not None:
            return p, [self.hands.joints(t, p)]
        v, vs = self.vel(t)
        walk = p.get("walk", 0.0)
        if self.auto_walk:
            walk = max(walk, _ssf(0.05, 0.16, abs(vs)), _ssf(0.05, 0.16, abs(v)))
        # a body seen at an angle covers less ground on screen per step: scale the stride so the feet stay put
        d = self.dist(t) / max(math.cos(p.get("yaw", self.bodies[0].yaw0)), 0.35)
        out = []
        for b in self.bodies:
            out.append(b.joints(t, p, d, walk, (v, vs)))
        return p, out

    def local_points(self, t):
        """All sparks in local 2D units (feet at y=0), with a brightness per spark."""
        p, Js = self.skeleton(t)
        if self.hands is not None:
            pts, b = self.hands.points(t, Js[0], p)
            return pts, b
        v, vs = self.vel(t)
        lag = -0.09 * vs - 0.12 * (v - vs)
        lag = max(-0.08, min(0.08, lag))
        P, B = [], []
        yaw = p.get("yaw", self.bodies[0].yaw0)
        for k, (body, J) in enumerate(zip(self.bodies, Js)):
            pts3, b = body.points(t, J, p, (v, vs), lag)
            if self.preset == "pair" and self.together:
                pts3 = pts3 + np.array([0.0, 0.0, body.z0])
            if self.preset == "pair" and not self.together:
                g = p.get("gap", self.gap)
                body.x0 = -body.facing * g / 2
            P.append(body.project(pts3, yaw))
            B.append(b)
        return np.vstack(P), np.concatenate(B)

    def place(self, t):
        x = self.value(self.m, "x", 0.5, t)
        y = self.value(self.m, "y", 0.30, t)
        h = self.value(self.m, "height", 0.34, t)
        return x, y, h

    def to_screen(self, t, loc):
        x, y, h = self.place(t)
        return np.stack([x + self.face * loc[:, 0] * h / self.aspect, y + loc[:, 1] * h], axis=1)

    def sparks(self, t):
        """Screen positions (n x 2), local height (n,) and brightness (n,) of every spark at t."""
        loc, b = self.local_points(t)
        return self.to_screen(t, loc), loc[:, 1], b

    def feet_screen(self, t):
        """Screen x of each body's ankles, and each foot's place in its step cycle (0..0.62 is the stance)."""
        p, Js = self.skeleton(t)
        out = []
        for body, J in zip(self.bodies, Js):
            for side in (1.0, -1.0):
                ax, ay, az, pitch, u = J["feet"][side]
                lx = body.x0 + body.facing * (ax * math.cos(p.get("yaw", body.yaw0)) + az * math.sin(p.get("yaw", body.yaw0)))
                out.append((float(self.to_screen(t, np.array([[lx, ay]]))[0, 0]), u))
        return out
