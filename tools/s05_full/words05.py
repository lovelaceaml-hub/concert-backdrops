"""Song 05 "God Bless You!", full-length backdrop: the words on screen.

Adapted from the song 01 words lane (branch backdrop/s01-full-words, tools/s01_full/words.py: the Word class with
the "star" and "drift" leavings is copied unchanged). All times are SONG time t in seconds (0 is the first sample
of the organisers' reference audio, 153.15 s long; the picture holds 15 s more). project-docs/backdrops/s05-full/
TIMELINE.md explains every time below.

    title          "God Bless You!"                        the song's name over the opening
    bless          "God bless you!"                        verse 1, line 1 (a short lyric fragment, design section 8)
    Encouragement  "I'll pray (or root) for you. Everything will go well."   verse 1, line 2
    father         "Father's great love"                   verse 1, line 3, at its loud peak
    Consideration  "Can I give you a hand with anything?"   verse 1, line 4
    fruit          "good fruit"                            verse 1, line 6
    Encouragement2 the same words again                    verse 2, line 2
    Consideration2 the same words again                    verse 2, line 4
    Encouragement3 and Consideration3                      both together in the calm hold, to carry home

Same type and layering as the approved Revision 3: the cream Cormorant serif phrase with the glowing coloured
capsule label (Claude Final v1 words, commit f43f451), riding the camera so it is perfectly still on screen while
read, never reflected in the water, centred about 0.345 of the frame height from the top.
No em dash or en dash anywhere in this file.
"""
import importlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

TIMELINE = {
    "title": dict(t_in=1.2, t_read0=3.6, t_read1=10.2, t_out=12.4),
    "bless": dict(t_in=15.6, t_read0=17.4, t_read1=21.6, t_out=24.0),
    "Encouragement": dict(t_in=24.6, t_read0=26.4, t_read1=35.4, t_loose=36.4, t_out=37.6),
    "father": dict(t_in=43.6, t_read0=45.4, t_read1=51.2, t_out=53.4),
    "Consideration": dict(t_in=55.8, t_read0=57.4, t_read1=66.4, t_loose=67.4, t_out=68.6),
    "fruit": dict(t_in=76.6, t_read0=78.0, t_read1=82.4, t_out=84.0),
    "Encouragement2": dict(t_in=94.4, t_read0=96.0, t_read1=105.6, t_loose=106.4, t_out=107.4),
    "Consideration2": dict(t_in=126.6, t_read0=128.0, t_read1=137.0, t_loose=138.0, t_out=139.0),
    "Encouragement3": dict(t_in=153.6, t_read0=155.6, t_read1=171.0, t_out=173.0),
    "Consideration3": dict(t_in=154.6, t_read0=156.6, t_read1=171.0, t_out=173.0),
}
# widest line as a share of the frame width
WIDTH = {"title": .42, "bless": .38, "Encouragement": .62, "father": .46, "Consideration": .56, "fruit": .30,
         "Encouragement2": .62, "Consideration2": .56, "Encouragement3": .39, "Consideration3": .35}
# centre of each block, share of the frame height from the top
CENTRE = {"Encouragement3": .175, "Consideration3": .385}
TEXT = {"title": "God Bless You!", "bless": "God bless you!", "father": "Father\u2019s great love",
        "fruit": "good fruit"}
STYLE = {}
# where each expression's light goes when its words gather (the song module gives the arch's star places)
STARS = {"Encouragement": ("screen", .62, .90, 30.0), "Consideration": ("screen", .70, .88, 30.0)}


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


class S05Words:
    """The moments as one set. All methods take song time t (seconds)."""

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

        specs = []
        for name in ("Encouragement", "Encouragement2", "Encouragement3", "Consideration", "Consideration2",
                     "Consideration3"):
            expr = name.rstrip("23")
            final = name.endswith("3")
            specs.append(dict(expr=expr, name=name, arrive="pen", nib=False, leave="fade" if final else "star",
                              to=None if final else to_star(expr), pill=True, **tl[name]))
        specs += [
            dict(label="", lines=[TEXT["title"]], name="title", arrive="reveal", leave="fade", font="title",
                 color="#fff3dc", glow="#ffc46e", tint=.25, **tl["title"]),
            dict(label="", lines=[TEXT["bless"]], name="bless", arrive="shaft", leave="drift",
                 color="#fff1d0", glow="#ffcf7a", tint=.30, **tl["bless"]),
            dict(label="", lines=[TEXT["father"]], name="father", arrive="rays", leave="rise",
                 color="#fff3dc", glow="#ffd27a", tint=.30, **tl["father"]),
            dict(label="", lines=[TEXT["fruit"]], name="fruit", arrive="petals", leave="petals",
                 color="#fff0e4", glow="#ffb0c0", tint=.30, **tl["fruit"]),
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
            cy = CENTRE.get(name, centre_y)
            w = Word(ride=(x, 1.0 - cy, depth), face="screen", camera=camera, reflect=False,
                     backing=backing, **spec)
            # centre the whole block (label included) at centre_y: shift the ride by the block's offset
            x0, x1, y0, y1 = w.extent()
            w.ride = (x, 1.0 - cy - .5 * (y0 + y1) / (2.0 * half), depth)
            self.words.append(w)
        for w in self.words:
            w._others = [o for o in self.words if o is not w]

    def world(self, world=None):
        """The world settings with the light the words bring: a shaft for "shaft", rays for "rays"."""
        out = dict(world or {})
        shafts = list(out.get("shafts") or [])
        for w in self.words:
            if w.arrive == "shaft" and len(shafts) < 4:
                shafts.append(w.shaft())
            if w.arrive == "rays" and not out.get("light"):
                out["light"] = w.light()
        if shafts:
            out["shafts"] = shafts
        return out

    # ---------------------------------------------------------------- scene
    def __iter__(self):
        return iter(self.words)

    def __getitem__(self, name):
        return next(w for w in self.words if w.name == name)

    def add_to(self, scene, prefix="s05 word "):
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
        """(world position, glow 0..1) of an expression's star at t. The glow rises while
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
    return S05Words(camera, **params)
