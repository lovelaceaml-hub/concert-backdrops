"""The song kit's Words of Mother's Love: the part of every song that shows the nine expressions.

Anthony (2026-11-23): build the kit from Almighty God Knows the Future "but expect to add more to the kit that
represents mothers words of love closer". Everything about the expressions lives here so a new idea is added
once and every song can use it:

    the arch     the arch of nine lights across the top of the sky, carried from song to song (DESIGN-SYSTEM 5):
                 lit at the start, lit in this song, relit in this song (song_data.ARCH)
    the words    each expression's exact wording (words.EXPRESSIONS) in its website colour with its capsule
                 label, upper middle, read at least 2.5 s, never over a person; it streams into its star
    the act      people of light act the expression out (ACTS, by name). Rules (PHASEB UPDATE 15): greeting,
                 two men each give a slight bow; embraces, two women; every touch between people of the same
                 gender, except a parent and child
    the answer   what the world does in reply (ANSWERS, by name), for example a peace ring across the water

song_data.EXPRESSIONS: [dict(label, t_in, read0, read1, t_out, act=name or None, at=(x, z), facing=degrees,
answer=name or None, frac=0.36)]. The act's people appear a little before the words and act during the reading.
A song with edit blocks owned by "love" gets a close, slow shot of each act (SHOTS). To add an act: write a
function act_<name>(e) returning body settings and register it in ACTS. No em dash or en dash in this file.
"""
import numpy as np

from songs.kit_film import *  # noqa: F401,F403
import songs.kit_film as H
import song_data as D

OWNER = "love"
SHOTS = []
LABELS = list(PW.LABELS)                       # Greeting .. Compliment (the arch's order)
EXPRESSIONS = [dict(e) for e in getattr(D, "EXPRESSIONS", [])]
ARCH = dict(getattr(D, "ARCH", {}))
WORD_Y = 0.655                                 # centre of an expression, from the bottom (the upper middle)
WORD_DEPTH = 7.0

for _e in EXPRESSIONS:
    if _e["label"] not in LABELS:
        raise ValueError(f"unknown expression {_e['label']!r}; use one of {LABELS}")
    if _e["read1"] - _e["read0"] < 2.5:
        raise ValueError(f"{_e['label']}: an expression is read at least 2.5 s")


# =========================================================================================================
# The arch of nine lights: one place in the picture whatever the camera does (across the top of the sky, its
# feet at about half the picture's height near the sides, its top above the words)
# =========================================================================================================
ARCH_D = 60.0
ARCH_SCREEN = dict(ARCH.get("screen", dict(x0=0.13, x1=0.87, foot=0.50, top=0.19)))


def _place(t, x, y, depth):
    return np.asarray(PW.place(H.CAMERA, t, x, y, depth), np.float64)


def _width_at(t, depth, frac):
    cam = PW._cam_at(H.CAMERA, t)
    return float(2.0 * depth * np.tan(np.radians(cam.fov) * 0.5) * cam.aspect * frac)


def _arch_frame(t):
    cam = PW._cam_at(H.CAMERA, t)
    f = np.asarray(cam.target, np.float64) - np.asarray(cam.pos, np.float64)
    yaw = float(np.degrees(np.arctan2(-f[0], -f[2])))
    foot = _place(t, 0.5, 1.0 - ARCH_SCREEN["foot"], ARCH_D)
    top = _place(t, 0.5, 1.0 - ARCH_SCREEN["top"], ARCH_D)
    span = _width_at(t, ARCH_D, ARCH_SCREEN["x1"] - ARCH_SCREEN["x0"])
    return foot, yaw, span, float(top[1] - foot[1])


def arch_homes(t):
    """The nine places of the arch at t (as p3d.world.Arch.point)."""
    c, yaw, span, height = _arch_frame(t)
    th = np.radians(np.linspace(172.0, 8.0, 9))
    x, y = 0.5 * span * np.cos(th), height * np.sin(th)
    a = np.radians(yaw)
    return np.stack([c[0] + x * np.cos(a), c[1] + y, c[2] - x * np.sin(a)], axis=1)


def _star_times():
    """When each light is lit (first time in the concert) or relit in this song: {index: (time, kind)}."""
    out = {}
    for e in EXPRESSIONS:
        i = LABELS.index(e["label"])
        kind = "relit" if (i + 1) in ARCH.get("lit_start", []) else "lit"
        out[i] = (float(e["t_out"]), kind)
    return out


def _arch_lit(t):
    start = set(ARCH.get("lit_start", []))
    stars = _star_times()
    out = []
    for i in range(9):
        if i in stars:
            ts, kind = stars[i]
            age = t - ts
            if kind == "lit":
                if age < -0.35:
                    out.append((0.0, -1.0))
                else:
                    g = min(max((age + 0.35) / 0.35, 0.0), 1.0)
                    out.append((0.62 * g + (1.5 * np.exp(-max(age, 0.0) * 1.2) if age >= 0 else 0.0), max(age, 0.0)))
            else:
                flare = 1.2 * np.exp(-max(age, 0.0) * 1.4) if age >= 0 else 0.0
                out.append((0.55 + flare, 30.0 + max(age, 0.0) if age < 0 else max(age, 0.0)))
        elif (i + 1) in start:
            out.append((0.55, 30.0 + t))
        else:
            out.append((0.0, -1.0))
    return out


def arch_world():
    """The world's arch settings, or None for a song without one."""
    if not ARCH:
        return None
    return dict(lit=_arch_lit, colors=H.COL9, span=lambda t: _arch_frame(t)[2],
                height=lambda t: _arch_frame(t)[3], z=0.0, center=lambda t: _arch_frame(t)[0],
                yaw=lambda t: _arch_frame(t)[1], line=lambda t: 0.08 + 0.62 * H._sc(H.OPENING_END, H.OPENING_END + 3.0, t),
                bright=1.5)


# =========================================================================================================
# The words of each expression: exact wording, website colour, capsule label; they stream into the star
# =========================================================================================================
def specs(width):
    out = []
    for e in EXPRESSIONS:
        i = LABELS.index(e["label"])
        ride = (0.5, e.get("y", WORD_Y), WORD_DEPTH)
        ts = np.linspace(e["t_in"], e["t_out"], 12)
        s = dict(name=f"expr_{e['label']}", ride=ride, face="screen", width=width(ts, WORD_DEPTH, e.get("frac", 0.38)),
                 t_in=e["t_in"], t_read0=e["read0"], t_read1=e["read1"], t_out=e["t_out"], reflect=False, sharp=1.0,
                 expr=e["label"], pill=True, arrive=e.get("arrive", "pen"), nib=False)
        if ARCH:
            s.update(leave="stream", to=arch_homes(e["t_out"])[i])
        else:
            s.update(leave="rise")
        out.append(s)
    return out


def read_windows():
    return [(e["t_in"], e["read0"], e["read1"], e["t_out"]) for e in EXPRESSIONS]


# =========================================================================================================
# The people of light: bodies built when the scene is set up (Claude Final v1 bodies, warm gold glitter)
# =========================================================================================================
_BODIES = {}
_TONES = [("#ffc664", "#fff0c8"), ("#f2a640", "#ffdc96"), ("#ffd27a", "#fff4dc"), ("#f6b85a", "#ffe8b8")]


def body(name, shape, **kw):
    """A person of light (shape "man", "woman" or "child"); kw as nine_reference_p3d.body.Body plus tone."""
    from nine_reference_p3d.body import Body
    c, c2 = _TONES[kw.pop("tone", 0) % len(_TONES)]
    common = dict(look=kw.pop("look", "glitter"), color=kw.pop("color", c), color2=kw.pop("color2", c2),
                  points=int(kw.pop("points", 30000) * 1.6), fade=kw.pop("fade", 0.8),
                  bright=kw.pop("bright", 1.35) * 1.7, size=kw.pop("size", 1.5))
    common.update(kw)
    b = Body(shape, **common)
    _BODIES[name] = b
    return b


def _raw(name, t, part):
    return np.asarray(_BODIES[name].where(t, part, raw=True), np.float64)


def _side(e, d):
    """A point d metres to the side of the act's place (along its facing line)."""
    x, z = e["at"]
    a = np.radians(e.get("facing", 0.0))
    return (x + d * np.cos(a), z - d * np.sin(a))


def act_greeting(e):
    """"How are you?": two men walk in, face each other and each gives a slight, warm bow (UPDATE 15)."""
    t0, r0, r1 = e["t_in"], e["read0"], e["read1"]
    yaw = e.get("facing", 0.0)
    show = (t0 - 3.0, e["t_out"] + 2.5)
    k = e["label"]
    body(f"{k} A", "man", at=_side(e, -0.85), facing=yaw + 90.0, garment="coat", tone=1, seed=21.0, show=show,
         motion=[(show[0], "walk", dict(speed=0.35)), (t0 - 0.5, "stand", dict(blend=1.2))],
         gesture=[(r0 - 0.2, r1 - 0.8, "bow", dict(amount=16.0))], fade=2.0, points=30000)
    body(f"{k} B", "man", at=_side(e, 0.85), facing=yaw - 90.0, garment="tunic", tone=0, seed=22.0, show=show,
         motion=[(show[0], "walk", dict(speed=0.35)), (t0 - 0.5, "stand", dict(blend=1.2))],
         gesture=[(r0, r1 - 0.6, "bow", dict(amount=18.0))], fade=2.0, points=30000)


def act_consideration(e):
    """"Can I give you a hand with anything?": a man has sunk to one knee; another reaches down his hand and
    pulls him up to standing, then rests a hand on his shoulder (men with men, UPDATE 15)."""
    t0, r0, r1 = e["t_in"], e["read0"], e["read1"]
    yaw = e.get("facing", 0.0)
    rise = 0.5 * (r0 + r1)
    show = (t0 - 3.5, e["t_out"] + 2.5)
    k = e["label"]

    def grip(t):
        pa, pb = _raw(f"{k} helper", t, "shoulder.R"), _raw(f"{k} weary", t, "shoulder.R")
        g = 0.5 * (pa + pb)
        g[1] = 0.5 * (pa[1] + pb[1]) - 0.36
        return g

    body(f"{k} weary", "man", at=_side(e, 0.55), facing=yaw - 90.0, garment="coat", tone=1, seed=31.0, show=show,
         stoop=0.4, motion=[(show[0], "kneel", dict(one=True, dur=0.1, blend=0.0)),
                            (rise, "rise", dict(dur=1.7, one=True, blend=0.05))],
         gesture=[(rise - 0.8, rise + 2.6, "handshake", dict(side="R", to=grip, grip=1.0, ease=0.6))],
         fade=2.0, points=32000)
    body(f"{k} helper", "man", at=_side(e, -0.55), facing=yaw + 90.0, garment="tunic", tone=0, seed=32.0, show=show,
         motion=[(show[0], "walk", dict(speed=0.3)), (t0, "stand", dict(blend=1.0))],
         gesture=[(rise - 1.0, rise + 2.6, "handshake", dict(side="R", to=grip, grip=1.0, ease=0.7)),
                  (rise + 2.4, r1 + 1.0, "hand_on_shoulder",
                   dict(side="L", to=lambda t: _raw(f"{k} weary", t, "shoulder.R"), ease=0.9))],
         fade=2.0, points=32000)


ACTS = dict(greeting=act_greeting, consideration=act_consideration)


# =========================================================================================================
# The answers of light: what the world does in reply
# =========================================================================================================
class PeaceRing:
    """A ring of warm golden stillness spreading across the water from the act's place after the words reach
    their star (Song 7's signature, offered to every song)."""

    def __init__(self, at, t0, color="#ffd27a", n=900, reach=26.0, dur=6.0):
        self.c, self.t0, self.col = np.asarray([at[0], 0.08, at[1]], np.float64), float(t0), lin(color)
        self.reach, self.dur = float(reach), float(dur)
        self.a = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
        self.s = np.random.default_rng(int(t0 * 10) % 997).random(n)

    def sample(self, t):
        age = t - self.t0
        if age < 0.0 or age > self.dur:
            return None
        u = age / self.dur
        r = self.reach * (1.0 - (1.0 - u) ** 2.2)
        k = (1.0 - u) ** 1.3 * H._sc(0.0, 0.3, age)
        rr = r * (1.0 + 0.012 * (self.s - 0.5))
        P = np.stack([self.c[0] + rr * np.cos(self.a), np.full_like(self.a, self.c[1]), self.c[2] + rr * np.sin(self.a)], 1)
        return [dict(pos=P, size=0.10 + 0.08 * self.s, color=self.col, alpha=0.8 * k, kind="spark", emit=2.6,
                     twinkle=0.6, seed=self.s, reflect=False),
                dict(pos=P[::4], size=0.9, color=self.col, alpha=0.10 * k, kind="soft", emit=1.4, reflect=False)]


def answer_peace_ring(e):
    return [PeaceRing(e["at"], e["t_out"])]


ANSWERS = dict(peace_ring=answer_peace_ring)


# =========================================================================================================
# The shots of the acts (for edit blocks owned by "love"): close, slow, eye height, the act in the lower half
# =========================================================================================================
def _act_shot(b):
    e = min(EXPRESSIONS, key=lambda e: abs(e["read0"] - b[0])) if EXPRESSIONS else None
    x, z = e["at"] if e else (0.0, 0.0)
    a = np.radians(e.get("facing", 0.0) if e else 0.0)
    fwd = np.array([np.sin(a), 0.0, np.cos(a)])          # the camera stands in front of the pair
    c = H._v(x, 1.1, z)
    return dict(name="act_" + (e["label"] if e else "none"), kind="local", t0=b[0], t1=b[1], fov=38.0, aperture=0.006,
                keys=[(b[0], c + fwd * 7.2 + H._v(0.0, 0.7, 0.0), c + H._v(0.0, 0.6, 0.0)),
                      (b[1], c + fwd * 5.6 + H._v(0.0, 0.55, 0.0), c + H._v(0.0, 0.55, 0.0))], pace="linear")


SHOTS = [_act_shot(b) for b in H.blocks_of(OWNER)]


def add(scene):
    for e in EXPRESSIONS:
        if e.get("act"):
            ACTS[e["act"]](e)
        if e.get("answer"):
            for k, ps in enumerate(ANSWERS[e["answer"]](e)):
                scene.add(f"answer {e['label']} {k}", ps, reflect=False)
    for name, b in _BODIES.items():
        b.add(scene, name, reflect=False)
