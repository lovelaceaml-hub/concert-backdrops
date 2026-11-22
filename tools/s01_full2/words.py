"""Song 01 "All You Stars of Zion", full-length backdrop: the words on screen (lane WORDS).

Five moments, all keyed on SONG TIME t in seconds (0 is the first sample of the ensemble recording,
187.97 s long). Times are in TIMELINE below; the lead may change any of them.

    Compliment     "You're amazing. You're doing great!"   label COMPLIMENT, colour #364E96
                   forms 39.0 to 42.0, fully readable 42.0 to 52.0, loosens 52.0 to 55.0,
                   gathers into Compliment's star 55.0 to 58.0
    "like a torch" a line of fire runs left to right and lights each letter, 60.0 to 62.0;
                   the letters burn gently 62.0 to 67.0; they let go as rising embers 67.0 to 69.0
    "dew of the dawn"  a fine thread of light is drawn along the writing and each letter shows as the
                   light reaches it, 115.0 to 117.5; held 117.5 to 121.0; the threads come loose and
                   drift down toward the lake 121.0 to 123.0
    "Arise"        letter by letter the word stands up out of the lake (each letter turns upright as
                   it climbs), 145.8 to 147.8, whole on the big hit at 147.8 (2:27.8, the sunrise);
                   solid 147.8 to 151.8; the letters stretch upward into the first rays 151.8 to 153.8
    Encouragement  "I'll pray (or root) for you. Everything will go well."  label ENCOURAGEMENT,
                   colour #9E6AF6; forms 158.0 to 161.0, fully readable 161.0 to 172.0, loosens
                   172.0 to 175.0, becomes Encouragement's star 175.0 to 177.0 (hit at 177.4)

Same type and layering as the approved Revision 3: the cream Cormorant serif phrase with the glowing
coloured capsule label (engine p3d words, Claude Final v1, commit f43f451), drawn as particle words in
the 3D scene, flat to the picture, riding the camera so they are perfectly still on screen while solid,
never reflected in the water. Concert rules on top of R3: larger, centred about 0.345 of the frame height
from the top, nothing crossing a word (use clear()), no word mirrored in the lake.

How the lead uses it (inside a song module whose p3d package is the pinned engine d928ff9):

    from s01_full import words as S01W
    WORDS = S01W.build(camera=CAMERA_FOR_LAYOUT)            # any object with at/state/sample(t) or a callable
    WORDS.add_to(scene)                                       # in P3D["setup"]
    entry.pointset = WORDS.clear(entry.pointset)             # comets, sparks: dimmed inside reading bounds
    pos, glow = WORDS.star(t, "Compliment")                  # where the star is and how lit (0..1, holds 1
                                                              # after the hand-off): light the arch star from
                                                              # STAR_HANDOFF["Compliment"] on
    WORDS.reading(t), WORDS.active(t), WORDS.boxes(t, cam)    # for camera focus, scene calm, clearing light

Parameters the lead may adjust (all keyword arguments of build()):
    timeline   dict of per-moment times (copy TIMELINE and edit)
    centre_y   where the middle of each text block sits, 0..1 from the TOP of the frame (default .345)
    x          horizontal centre, 0..1 from the left (default .5)
    depth      metres in front of the camera the words ride at (default 7, as R3)
    scale      multiplies every width (1.0 is the concert size below)
    widths     dict of width as a share of the frame width per moment (WIDTH)
    stars      dict: "Compliment"/"Encouragement" -> a world point (x, y, z), a function of t giving one,
               or ("screen", x, y, depth) for a place on screen (x, y from the left and from the BOTTOM)
    style      dict per moment of Word settings (tint, bright, halo, color, glow) over STYLE
    backing    0..1: a very soft warm glow behind each text block so nothing dark sits behind a word
               (default .0; raise it if a scene is dark behind the words)
No em dash or en dash anywhere in this file.
"""
import importlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

TIMELINE = {
    "Compliment": dict(t_in=39.0, t_read0=42.0, t_read1=52.0, t_loose=55.0, t_out=58.0),
    "torch": dict(t_in=60.0, t_read0=62.0, t_read1=67.0, t_out=69.0),
    "dew": dict(t_in=114.6, t_read0=117.0, t_read1=122.0, t_out=124.0),
    "Arise": dict(t_in=145.8, t_read0=147.8, t_read1=151.8, t_out=153.8),
    "Encouragement": dict(t_in=158.0, t_read0=161.0, t_read1=171.0, t_loose=174.0, t_out=177.0),
}
# width of the widest line of each phrase as a share of the frame width (R3 used .30 to .60)
WIDTH = {"Compliment": .50, "torch": .40, "dew": .44, "Arise": .36, "Encouragement": .64}
TEXT = {"torch": "like a torch", "dew": "dew of the dawn", "Arise": "Arise"}
# default star places on screen (x, y from the left and from the bottom, depth in metres): high in the
# sky where the arch is, Compliment far right (star 9), Encouragement third from the right (star 7)
STARS = {"Compliment": ("screen", .80, .88, 30.0), "Encouragement": ("screen", .68, .90, 30.0)}
# extra look per moment (any Word setting: tint, bright, halo, color, glow, paint). The two sunrise
# moments are read over a bright sky, so their letters keep more of their colour and a stronger halo
# instead of going cream-white into a pale sky.
STYLE = {
    "Arise": dict(color="#f0a032", glow="#d9731c", tint=.80, bright=.95, halo=1.6),
    "Encouragement": dict(tint=.75, bright=.95, halo=1.5),
}
STAR_HANDOFF = {"Compliment": TIMELINE["Compliment"]["t_out"],
                "Encouragement": TIMELINE["Encouragement"]["t_out"]}


def _pw():
    """The Claude Final v1 words module, as Revision 3 reads it (package nine_reference_p3d)."""
    if "nine_reference_p3d.words" in sys.modules:
        return sys.modules["nine_reference_p3d.words"]
    if "nine_reference_p3d" not in sys.modules:
        sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
        importlib.import_module("reference")
    return importlib.import_module("nine_reference_p3d.words")


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return (u * u * (3.0 - 2.0 * u)).astype(np.float32)


def _cam_at(camera, t):
    return _pw()._cam_at(camera, t)


def _make_class(PW):
    lin, _mix, WARM = PW.lin, PW._mix, PW.WARM

    class Word(PW.Word):
        """A Word with the song's own ways in and out: arrive flame/stand, leave star/beams/drift."""

        def __init__(self, arrive=None, leave=None, backing=0.0, **kw):
            mine_in = arrive in ("flame", "stand")
            mine_out = leave in ("star", "beams", "drift", "embers")
            super().__init__(arrive="reveal" if mine_in else arrive, leave="fade" if mine_out else leave, **kw)
            if mine_in:
                self.arrive = arrive
            if mine_out:
                self.leave = leave
            self.backing = float(backing)
            self.t_loose = float(self.opts.pop("t_loose", self.t_read1))

        # ------------------------------------------------------------ arrivals
        def _arr_flame(self, P, a, t, cam, F, tg):
            """A line of fire runs from left to right; each letter catches as it passes, hot, then settles."""
            front = -0.06 + 1.12 * float(_ss(0.0, 0.92, a))
            d = front - self.xn
            g = np.clip(d / 0.05, 0.0, 1.0)
            heat = np.exp(-np.maximum(d, 0.0) / 0.10) * (d > 0.0)
            P["alpha"] = g.astype(np.float32)
            P["emit"] = (1.0 + 2.6 * heat).astype(np.float32)
            P["color"] = _mix(self.c_letter[None, :], lin("#ffb35c").astype(np.float32)[None, :] * 1.25,
                              (0.8 * heat)[:, None]).astype(np.float32)
            # the running fire itself: a short bright line moving along just under the letters
            if 0.0 < front < 1.05:
                xs = np.linspace(0.0, 1.0, 40)
                x = float(self.xl.min()) + (front - 0.10 * xs) * float(np.ptp(self.xl))
                y = np.full(40, self.ybot + 0.25 * self.Ht) + 0.04 * self.Ht * np.sin(t * 9.0 + xs * 20.0)
                P["extra"].append(dict(pos=self._local(F, t, x, y), size=np.linspace(0.05, 0.015, 40) * self.Ht,
                                       color=lin("#ffbe6e"), alpha=np.linspace(0.9, 0.0, 40) * 0.6, emit=3.0,
                                       kind="soft", dof=False, reflect=False))

        def _arr_stand(self, P, a, t, cam, F, tg):
            """Letter by letter the word stands up out of the water: each letter climbs from below and turns
            upright about its foot, shedding drops of light that fall back. No mirror image is drawn."""
            o, r, u, nrm = F
            s = self.s
            start = 0.05 + 0.55 * self.xn + 0.03 * s[:, 0]
            p = np.clip((a - start) / 0.38, 0.0, 1.0)
            e = 1.0 - (1.0 - p) ** 3
            lie = (1.0 - e) * np.radians(80.0)                 # lying back on the water, then upright
            yy = self.yl - self.ybot
            climb = (1.0 - e) * float(self.opts.get("climb", 1.0)) * self.Ht
            y = self.ybot + yy * np.cos(lie) - climb
            z = -yy * np.sin(lie)
            P["pos"] = self._local(F, t, self.xl, y, z)
            P["alpha"] = _ss(0.0, 0.25, p)
            P["emit"] = (1.0 + 1.8 * np.exp(-p / 0.15) * (p > 0.0)).astype(np.float32)
            P["assist"] = _ss(0.6, 1.0, p)
            m = self.M
            sec = np.maximum(a - start[:m] - 0.05, 0.0) * max(self.t_read0 - self.t_in, 1e-6)
            al = (sec > 0.0) * (1.0 - _ss(0.4, 1.2, sec)) * (np.arange(m) % 3 == 0)
            vis = al > 0.01
            if vis.any():
                dp = P["pos"][:m][vis].copy()
                dp -= (0.5 * 9.8 * sec[vis] ** 2 * 0.25)[:, None] * u[None, :].astype(np.float32)
                P["extra"].append(dict(pos=dp, size=self.size0[:m][vis] * 2.0, color=lin("#ffe2a8"),
                                       alpha=al[vis] * 0.6, emit=1.8, kind="soft", seed=s[:m][vis, 2],
                                       streak=1.0, reflect=False))

        # ------------------------------------------------------------ leavings
        def _lea_drift(self, P, l, t, cam, F, tg):
            """Fine threads come loose and drift down toward the lake, slowly, thinning to nothing."""
            s = self.s
            w = self.W
            o, r, u, nrm = F
            st = 0.35 * self.xn + 0.10 * s[:, 0]
            lp = np.clip((l - st) / 0.6, 0.0, 1.0)
            fall = (0.9 * lp * lp) * self.Ht * (0.6 + 0.8 * s[:, 1])
            sway = 0.05 * w * np.sin(t * 1.4 + s[:, 2] * 6.28) * lp
            P["pos"] = (tg - fall[:, None] * u[None, :].astype(np.float32)
                        + sway[:, None] * r[None, :].astype(np.float32)).astype(np.float32)
            P["alpha"] = (1.0 - _ss(0.15, 1.0, lp)).astype(np.float32)
            P["assist"] = (1.0 - _ss(0.0, 0.15, lp)).astype(np.float32)
            P["size"] = self.size0 * (1.0 - 0.5 * lp)

        def _lea_embers(self, P, l, t, cam, F, tg):
            """Each letter lets go of its flame as small rising embers that drift up and go out."""
            n0 = len(P["extra"])
            self._lea_rise(P, l, t, cam, F, tg)
            for b in P["extra"][n0:]:
                if b.get("kind") == "flake":
                    b.pop("rot", None)
                    b.update(kind="soft", size=np.asarray(b["size"]) * 0.28, emit=2.2, reflect=False,
                             color=_mix(lin("#ff8a2a"), lin("#ffd08a"), 0.45),
                             alpha=np.asarray(b["alpha"]) * (0.75 + 0.25 * np.sin(t * 11.0 + np.arange(len(b["pos"])))))
            P["color"] = _mix(self.c_letter[None, :], lin("#ff9d48").astype(np.float32)[None, :],
                              np.full((self.N, 1), float(_ss(0.0, 0.5, l)), np.float32)).astype(np.float32)

        def _lea_beams(self, P, l, t, cam, F, tg):
            """Each letter stretches upward and becomes a ray of the sunrise."""
            o, r, u, nrm = F
            s = self.s
            st = 0.25 * np.abs(self.xn - 0.5) * 2.0 + 0.05 * s[:, 0]
            lp = np.clip((l - st) / 0.7, 0.0, 1.0)
            up = (lp ** 1.6) * (0.4 + 1.6 * self.yn) * 2.2 * self.Ht
            P["pos"] = (tg + up[:, None] * u[None, :].astype(np.float32)).astype(np.float32)
            P["alpha"] = (1.0 - _ss(0.35, 1.0, lp)).astype(np.float32)
            P["assist"] = (1.0 - _ss(0.0, 0.1, lp)).astype(np.float32)
            P["emit"] = (1.0 + 1.2 * np.sin(np.pi * lp)).astype(np.float32)
            k = float(_ss(0.0, 0.25, l) * (1.0 - _ss(0.6, 1.0, l)))
            if k > 0.01:
                n = 26
                xs = np.linspace(float(self.xl.min()), float(self.xl.max()), n)
                h = PW._h(n, 61)
                a0 = self._local(F, t, xs, np.full(n, self.ytop))
                a1 = self._local(F, t, xs * (1.0 + 0.4 * l), np.full(n, self.ytop + (1.0 + 3.0 * l) * self.Ht))
                P["extra"].append(dict(pos=a0, pos2=a1, size=(0.03 + 0.05 * h) * self.Ht,
                                       color=_mix(lin(WARM), self.c_glow, 0.4), alpha=0.22 * k, alpha2=0.0,
                                       kind="ribbon", dof=False, reflect=False))

        def _lea_star(self, P, l, t, cam, F, tg):
            """Two steps. First the letters loosen into a soft cloud of their colour, still where they were
            (t_read1 to t_loose). Then the cloud draws together and rises along a gentle curve into one point,
            the star (t_loose to t_out), which flares as the last light arrives."""
            o, r, u, nrm = F
            s = self.s
            w = self.W
            span = max(self.t_out - self.t_read1, 1e-6)
            split = float(np.clip((self.t_loose - self.t_read1) / span, 0.05, 0.95))
            la = float(np.clip(l / split, 0.0, 1.0))
            lb = float(np.clip((l - split) / (1.0 - split), 0.0, 1.0))
            loose = _ss(0.0, 1.0, la)
            cloud = tg + PW._swirl(tg, t, 3.0 / max(w, 1e-6) * 4.0, 2.0) * (0.05 * w * loose)
            cloud = cloud + self._world(F, (s[:, 1] - 0.5) * 0.06 * w * loose, 0.03 * w * loose * s[:, 2],
                                        0 * s[:, 0])
            goal = self._point(self.to, t, cam, o + u * (self.ytop + 0.9 * w)).astype(np.float32)
            p = np.clip((lb - 0.35 * (0.6 * self.ord + 0.4 * s[:, 0])) / 0.6, 0.0, 1.0)
            e = (p * p * (3.0 - 2.0 * p)) ** 1.3
            d = goal[None, :] - cloud
            p1 = cloud + self._world(F, 0 * s[:, 0], 0.15 * w + 0 * s[:, 0], 0 * s[:, 0])
            p2 = goal[None, :] - d * 0.35
            pos = PW._bez(cloud, p1, p2, np.repeat(goal[None, :], self.N, 0), e)
            P["pos"] = pos.astype(np.float32)
            P["alpha"] = ((1.0 - 0.45 * loose) * (1.0 - _ss(0.85, 1.0, p))).astype(np.float32)
            P["assist"] = np.full(self.N, 1.0 - float(_ss(0.0, 0.5, la)), np.float32)
            P["size"] = (self.size0 * (1.0 - 0.45 * e)).astype(np.float32)
            P["color"] = _mix(self.c_letter[None, :], self.c_base[None, :], (0.5 * loose)[..., None]
                              * np.ones((self.N, 1), np.float32)).astype(np.float32)
            got = float((p >= 1.0).mean())
            star = (0.15 + 0.85 * got) * float(_ss(0.0, 0.3, lb))
            if star > 0.01:
                P["extra"].append(dict(pos=goal[None, :], size=0.07 * w, color=_mix(lin(WARM), self.c_base, 0.35),
                                       alpha=star, emit=3.0 + 7.0 * got, kind="spark", twinkle=0.3, dof=False,
                                       reflect=False))
                P["extra"].append(dict(pos=goal[None, :], size=0.5 * w, color=self.c_glow, alpha=0.10 * star,
                                       kind="soft", dof=False, reflect=False))

        # ------------------------------------------------------------ light that stays with the words
        def _ambient(self, out, style, a, t, F, arriving, hold=0.0, fade=0.0):
            o, r, u, nrm = F
            if self.backing > 0.0:
                env = float(_ss(0.0, 0.3, a)) * (1.0 - float(_ss(0.0, 0.6, fade)))
                if env > 0.003:
                    k = 15
                    gx = (PW._h(k, 71) - 0.5) * 1.0 * self.W
                    gy = self.ymid + (PW._h(k, 72) - 0.5) * 1.2 * self.Ht
                    p = self._local(F, t, gx, gy, np.full(k, -0.08 * self.W))
                    out.append(dict(pos=p, size=np.full(k, 0.55 * max(self.Ht, 0.25 * self.W)),
                                    color=_mix(lin("#ffe6c4"), self.c_glow, 0.25),
                                    alpha=0.05 * self.backing * env, kind="soft", dof=False, reflect=False))
            if style == "flame":
                # small flames breathing on the letters while they burn (they go as the embers rise)
                env = float(_ss(0.2, 1.0, a)) * (1.0 - float(_ss(0.0, 0.35, fade)))
                if env > 0.003:
                    m = self.M
                    s = self.s[:m]
                    top = self.yn[:m] > 0.55
                    if top.any():
                        x = self.xl[:m][top]
                        flick = 0.5 + 0.5 * np.sin(t * (5.0 + 4.0 * s[top, 1]) + s[top, 2] * 30.0)
                        y = self.yl[:m][top] + (0.06 + 0.10 * flick) * self.Ht
                        x = x + 0.012 * self.W * np.sin(t * 3.0 + s[top, 3] * 20.0)
                        out.append(dict(pos=self._local(F, t, x, y), size=self.size0[:m][top] * (2.5 + 2.0 * flick),
                                        color=_mix(lin("#ff9a3c"), lin("#ffd08a"), 0.5),
                                        alpha=0.22 * env * flick, emit=1.6, kind="soft", dof=False,
                                        reflect=False))
                return
            if style in ("stand", "reveal"):
                return
            super()._ambient(out, style, a, t, F, arriving, hold, fade)

    return Word


def _star_point(spec, camera, t, cam=None):
    if spec is None:
        return None
    if isinstance(spec, tuple) and len(spec) == 4 and spec[0] == "screen":
        c = cam if cam is not None else _cam_at(camera, t)
        return np.asarray(_pw().place(c, t, spec[1], spec[2], spec[3]), np.float64)
    if callable(spec):
        return np.asarray(spec(t), np.float64)
    return np.asarray(spec, np.float64)


class S01Words:
    """The five moments as one set. All methods take song time t (seconds)."""

    def __init__(self, camera, timeline=None, centre_y=.345, x=.5, depth=7.0, scale=1.0, widths=None,
                 stars=None, backing=0.0, style=None):
        PW = _pw()
        self.PW, self.camera = PW, camera
        self.timeline = {k: dict(v) for k, v in (timeline or TIMELINE).items()}
        self.stars = dict(STARS, **(stars or {}))
        widths = dict(WIDTH, **(widths or {}))
        Word = _make_class(PW)
        tl = self.timeline

        def to_star(name):
            spec = self.stars[name]
            return lambda t: _star_point(spec, self.camera, t)

        specs = [
            dict(expr="Compliment", name="Compliment", arrive="pen", nib=False, leave="star",
                 to=to_star("Compliment"), pill=True, **tl["Compliment"]),
            dict(label="", lines=[TEXT["torch"]], name="torch", arrive="flame", leave="embers",
                 color="#ffc77a", glow="#ff9d48", tint=.30, speed=.22, **tl["torch"]),
            dict(label="", lines=[TEXT["dew"]], name="dew", arrive="stitch", leave="drift",
                 color="#e6eeff", glow="#a9c2ff", tint=.30, **tl["dew"]),
            dict(label="", lines=[TEXT["Arise"]], name="Arise", arrive="stand", leave="beams",
                 color="#ffd27a", glow="#ffb347", tint=.40, bright=1.05, **tl["Arise"]),
            dict(expr="Encouragement", name="Encouragement", arrive="pen", nib=False, leave="star",
                 to=to_star("Encouragement"), pill=True, **tl["Encouragement"]),
        ]
        style = {k: dict(STYLE.get(k, {}), **(style or {}).get(k, {})) for k in set(STYLE) | set(style or {})}
        for spec in specs:
            spec.update(style.get(spec["name"], {}))
        self.words = []
        for spec in specs:
            name = spec["name"]
            mid = .5 * (spec["t_read0"] + spec["t_read1"])
            cam = _cam_at(camera, mid)
            half = np.tan(np.radians(cam.fov) * .5) * depth          # half the frame height, metres
            spec["width"] = float(2.0 * half * cam.aspect * widths[name] * scale)
            w = Word(ride=(x, 1.0 - centre_y, depth), face="screen", camera=camera, reflect=False,
                     backing=backing, **spec)
            # centre the whole block (label included) at centre_y: shift the ride by the block's offset
            x0, x1, y0, y1 = w.extent()
            w.ride = (x, 1.0 - centre_y - .5 * (y0 + y1) / (2.0 * half), depth)
            self.words.append(w)
        for w in self.words:
            w._others = [o for o in self.words if o is not w]

    # ---------------------------------------------------------------- scene
    def __iter__(self):
        return iter(self.words)

    def __getitem__(self, name):
        return next(w for w in self.words if w.name == name)

    def add_to(self, scene, prefix="s01 word "):
        """Every word into the 3D scene: depth of field like R3, never reflected in the lake."""
        for w in self.words:
            scene.add(prefix + w.name, w, reflect=False, depth_of_field=True)
        return self

    # ---------------------------------------------------------------- what is on screen when
    def active(self, t):
        """{name: state} of the words on screen at t; state is arrive, read or leave."""
        return {w.name: w.state(t) for w in self.words if w.state(t) != "out"}

    def reading(self, t):
        """Names of the words that are solid and still at t (hold the scene calm, keep light off them)."""
        return [w.name for w in self.words if w.t_read0 <= t <= w.t_read1]

    def calm(self, t, ease=1.0):
        """0..1: how much the scene should hold still for the words (1 while any word is read)."""
        k = 0.0
        for w in self.words:
            k = max(k, float(_ss(w.t_read0 - ease, w.t_read0, t) * (1.0 - _ss(w.t_read1, w.t_read1 + ease, t))))
        return k

    def boxes(self, t, cam=None, pad=(.02, .035)):
        """Screen boxes (x0, x1, y0, y1; 0..1, y up) of the words on screen at t, padded."""
        cam = cam if cam is not None else _cam_at(self.camera, t)
        out = []
        for w in self.words:
            if w.t_in <= t <= w.t_out:
                x0, x1, y0, y1, front, *_ = self.PW.screen_box(w, cam, t)
                if front:
                    out.append((x0 - pad[0], x1 + pad[0], y0 - pad[1], y1 + pad[1]))
        return out

    def focus_point(self, t, default, ease=0.8):
        acc, wsum, top = np.zeros(3), 0.0, 0.0
        d = np.asarray(default(t) if callable(default) else default, np.float64)
        for w in self.words:
            k = float(_ss(w.t_read0 - ease, w.t_read0, t) * (1.0 - _ss(w.t_read1, w.t_read1 + ease, t)))
            if k > 0.0:
                acc += k * w.centre(t)
                wsum += k
                top = max(top, k)
        return d if wsum <= 0.0 else d + (acc / wsum - d) * top

    def clear(self, pointset):
        """Wrap a point set (comets, sparks, hoops) so its light dims inside the reading bounds: nothing
        crosses a word. Same rule as Revision 3's expressions.Clear."""
        return _Clear(pointset, self)

    # ---------------------------------------------------------------- the stars of the arch
    def star(self, t, name, cam=None):
        """(world position, glow 0..1) of Compliment's or Encouragement's star at t. The glow rises while
        the words gather (t_loose to t_out) and is 1 from the hand-off (t_out) on: from then the lead's arch
        star must be drawn there, as the words are gone."""
        w = self[name]
        pos = _star_point(self.stars[name], self.camera, t, cam)
        glow = float(_ss(w.t_loose, w.t_out, t))
        return pos, glow


class _Clear:
    wants_camera = True

    def __init__(self, inner, words):
        self.inner, self.words = inner, words

    def gain(self, t):
        return self.inner.gain(t) if hasattr(self.inner, "gain") else 1

    def sample(self, t, cam):
        got = self.inner.sample(t, cam) if getattr(self.inner, "wants_camera", False) else self.inner.sample(t)
        if got is None:
            return None
        boxes = self.words.boxes(t, cam)
        if not boxes:
            return got
        out = []
        for source in got if isinstance(got, (list, tuple)) else [got]:
            if source is None:
                continue
            b = dict(source)
            p = np.asarray(b["pos"]).reshape(-1, 3)
            xy, z = cam.project(p)
            end = None
            if b.get("pos2") is not None:
                end, _ = cam.project(np.asarray(b["pos2"]).reshape(-1, 3))
            gain = np.ones(len(p))
            for u in (np.linspace(0, 1, 9) if end is not None else [0]):
                q = xy if end is None else xy * (1 - u) + end * u
                for x0, x1, y0, y1 in boxes:
                    dx = np.minimum(q[:, 0] - x0, x1 - q[:, 0])
                    dy = np.minimum(q[:, 1] - y0, y1 - q[:, 1])
                    f = np.clip(np.minimum(dx, dy) / .02 + .5, 0, 1)
                    gain = np.minimum(gain, 1 - .98 * f * (z > 0))
            b["alpha"] = np.asarray(b.get("alpha", 1)) * gain
            if "alpha2" in b:
                b["alpha2"] = np.asarray(b["alpha2"]) * gain
            out.append(b)
        return out


def build(camera, **params):
    """The song's words. camera: the layout camera (see the module text); params: see the module text."""
    return S01Words(camera, **params)
