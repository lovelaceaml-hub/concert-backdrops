"""The lake responds, and campaign symbols are drawn in light (2026-11-15, branch engine-water-symbols).

Everything is optional. A song that sets none of these keys renders exactly as before.

  RIPPLES        [(t, x, strength), ...] or (t, x, strength, y): expanding rings where something touches the water
  RIPPLES_AUTO   number or Track (0 = off): petals, falling stars and figures' feet near the waterline add ripples
  RIPPLE_COLOR, RIPPLE_BRIGHT, RIPPLE_Y   the rings' light colour, its strength, the default depth of a ripple
  FALLING_STARS  [(t, x), ...] or (t, x, y): a star falls and lands on the lake at time t
  SYMBOLS        [dict(kind="emblem"|"heart"|"gate"|"bridge", t0, t1, out, x, y, size, ...)]

How a song uses them: engine/UPGRADE-HOWTO.md, section L. Every ripple is a pure function of t, so a frame
renders the same whichever part of the video it falls in.
"""
import math

import numpy as np
import moderngl

import song as S
import symbols as Y
import water_shaders as WS

MAX_RIP = 24
LIFE = 5.0          # seconds a ripple lasts
FALL_DUR = 1.1      # seconds a falling star takes to reach the water
SYM_UNIT = 16       # texture unit of a symbol's paint in the composite (free: UPGRADE-HOWTO section S)


def _val(name, t, default=None):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def _lin(c, default):
    c = c if c is not None else default
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0) if b != a else float(x >= a)
    return u * u * (3 - 2 * u)


def _setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v


class Water:
    def __init__(self, R):
        self.R = R
        self.ctx = ctx = R.ctx
        self.px = R.px
        self.rips = [tuple(r) for r in (getattr(S, "RIPPLES", None) or [])]
        self.auto = getattr(S, "RIPPLES_AUTO", None) is not None
        self.falls = [tuple(f) for f in (getattr(S, "FALLING_STARS", None) or [])]
        self.syms = list(getattr(S, "SYMBOLS", None) or [])
        self.has_rip = bool(self.rips) or self.auto
        self.active = self.has_rip or bool(self.syms) or bool(self.falls)
        # optional: a symbol's lines also painted in their own colour over the scene (SYMBOLS key `paint`)
        self.painted = any(float(m.get("paint", 0.0) or 0.0) > 0.0 for m in self.syms)
        self.paint_k = 0.0
        if not self.active:
            return
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        import sky_camera as SKC   # cam_vs: symbols and falling stars follow the camera (CAMERA_*)
        cv = SKC.cam_vs
        self.p_ring = ctx.program(vertex_shader=WS.RING_VS, fragment_shader=WS.RING_FS)
        self.v_ring = ctx.vertex_array(self.p_ring, [(quad, "2f", "aPos")])
        self.p_glow = ctx.program(vertex_shader=cv(WS.GLOW_VS), fragment_shader=WS.GLOW_FS)
        self.v_glow = ctx.vertex_array(self.p_glow, [(quad, "2f", "aPos")])
        self.p_dot = ctx.program(vertex_shader=WS.DOT_VS, fragment_shader=WS.DOT_FS)
        self.dot_buf = ctx.buffer(reserve=4 * 4 * 4096, dynamic=True)
        self.v_dot = ctx.vertex_array(self.p_dot, [(self.dot_buf, "2f 1f 1f", "aP", "aB", "aS")])
        self.petal_seeds = np.random.default_rng(3).random((300, 4))   # the same petals render.py draws
        self.p_sym = ctx.program(vertex_shader=cv(WS.SYM_VS), fragment_shader=WS.SYM_FS)
        if self.painted:
            self.p_symp = ctx.program(vertex_shader=cv(WS.SYM_VS), fragment_shader=WS.SYM_PAINT_FS)
            self.t_paint = ctx.texture((R.w, R.h), 4, dtype="f2")
            self.t_paint.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.t_paint.repeat_x = self.t_paint.repeat_y = False
            self.f_paint = ctx.framebuffer([self.t_paint])
        self.sdata = []
        for k, m in enumerate(self.syms):
            kind = m.get("kind", "heart")
            size = float(m.get("size", 0.3))
            stretch = float(m.get("stretch", 1.0))
            pts, roles = Y.build(kind, size * R.h * max(stretch, 1.0) ** 0.5)
            pal = dict(Y.ROLES)
            c = m.get("color")
            if isinstance(c, str):
                pal = {r: c for r in pal}
            elif isinstance(c, dict):
                pal.update(c)
            # light, never dark: each colour is lifted a little toward white so the lines glow
            cols = np.array([S.lin(pal[r]) * 0.82 + 0.18 for r in roles], dtype=np.float64)
            seeds = np.random.default_rng(4100 + k).random((len(pts), 4))
            data = np.hstack([pts, cols, seeds]).astype("f4")
            vao = ctx.vertex_array(self.p_sym, [(ctx.buffer(data.tobytes()), "4f 3f 4f", "aP", "aCol", "aSeed")])
            ext = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
            avg = cols.mean(axis=0)
            sd = dict(meta=m, vao=vao, ext=ext, avg=avg, kind=kind, size=size, stretch=stretch,
                      draft_keep=True)   # points in drawing order: a draft keeps every stroke
            if float(m.get("paint", 0.0) or 0.0) > 0.0:
                # `paint`: the lines of the chosen roles (`paint_roles`, default all of them) are also painted in
                # exactly their colour. The points are split in two, so the painted lines can carry less light
                # (`paint_light`) while the other lines stay as they are.
                import theme
                pr = m.get("paint_roles")
                sel = np.array([pr is None or r in pr for r in roles], dtype=bool)
                pcols = np.array([theme.display(pal[r]) for r in roles], dtype=np.float64)

                def part(prog, rows):
                    if not len(rows):
                        return None
                    buf = ctx.buffer(rows.astype("f4").tobytes())
                    return ctx.vertex_array(prog, [(buf, "4f 3f 4f", "aP", "aCol", "aSeed")])

                sd["vao_lit"] = part(self.p_sym, data[sel])
                sd["vao_rest"] = part(self.p_sym, data[~sel])
                sd["vao_paint"] = part(self.p_symp, np.hstack([pts, pcols, seeds])[sel])
            self.sdata.append(sd)

    # ------------------------------------------------------------ the water line and the ripples at time t
    def water_line(self, t):
        wl = S.HORIZON
        up = getattr(self.R, "up", None)
        for sc in (getattr(up, "scenes", None) or []):
            if sc["t0"] <= t < sc["t1"] and sc.get("water"):
                v = up._plate_view(sc, t)
                wl = 0.5 + (float(sc.get("water_line", S.HORIZON)) - v[1]) * v[2]
        return float(_val("RIPPLE_LINE", t, wl))

    def _default_y(self, t, wl):
        return float(_val("RIPPLE_Y", t, wl * 0.78))

    def ripples(self, t):
        """All ripples alive at t as (x, y, age, strength), newest first, at most 24. A pure function of t."""
        wl = self.water_line(t)
        out = []
        for r in self.rips:
            age = t - float(r[0])
            if 0.0 <= age < LIFE:
                y = float(r[3]) if len(r) > 3 else self._default_y(r[0], wl)
                if len(r) > 4:
                    # optional fifth number: the ring spreads that many times as fast and fades as slowly as any
                    # other ring (the shader sizes and fades a ring by its age: a larger age, a strength to match)
                    sp = float(r[4])
                    out.append((float(r[1]), y, age * sp, float(r[2]) * math.exp(age * (sp - 1.0) / 1.6)))
                else:
                    out.append((float(r[1]), y, age, float(r[2])))
        for f in self.falls:
            age = t - float(f[0])
            if self.auto and 0.0 <= age < LIFE:
                a = float(_val("RIPPLES_AUTO", f[0], 0.0) or 0.0)
                if a > 0.0:
                    y = float(f[2]) if len(f) > 2 else self._default_y(f[0], wl)
                    out.append((float(f[1]), y, age, 1.1 * a))
        if self.auto:
            out += self._petal_ripples(t, wl)
            out += self._figure_ripples(t, wl)
        out = [r for r in out if r[1] < wl]
        out.sort(key=lambda r: r[2])
        return out[:MAX_RIP]

    def _petal_ripples(self, t, wl):
        petals = getattr(S, "PETALS", None)
        if petals is None:
            return []
        sd = self.petal_seeds
        per = 15.0 + 12.0 * sd[:, 0]
        off = sd[:, 1] * 5.77
        h = np.modf(sd[:, 2] * 91.7 + sd[:, 3] * 13.1)[0]
        y_land = wl * (0.10 + 0.80 * np.modf(sd[:, 0] * 47.3 + sd[:, 1] * 7.9)[0])
        ph_land = (1.06 - y_land) / 1.02
        k = np.floor(t / per + off - ph_land)
        tb = per * (k + ph_land - off)
        age = t - tb
        out = []
        for i in np.nonzero((age >= 0.0) & (age < LIFE) & (h < 0.30))[0]:
            tbi = float(tb[i])
            amount = petals(tbi) if callable(petals) else float(petals)
            a = float(_val("RIPPLES_AUTO", tbi, 0.0) or 0.0)
            on = _ss(amount, amount - 0.1, sd[i, 3] * 0.999)
            if on < 0.5 or a <= 0.0:
                continue
            ph = ph_land[i]
            x = (sd[i, 2] + 0.22 * ph + 0.035 * math.sin(tbi * 0.5 + sd[i, 3] * 30.0)
                 + 0.02 * math.sin(tbi * 1.1 + sd[i, 0] * 17.0)) % 1.0
            out.append((float(x), float(y_land[i]), float(age[i]), 0.35 * a))
        return out

    def _figure_ripples(self, t, wl):
        figs = getattr(S, "FIGURES", None) or []
        if not figs:
            return []
        import upgrade as U
        out = []
        ts = np.arange(max(t - LIFE, 0.0), t + 1e-6, 1.0 / 30.0)
        for m in figs:
            t0, t1 = m["t0"], m["t1"]
            if t1 < t - LIFE or t0 > t:
                continue
            # feet on the water: the feet line is at or below the waterline (within 0.02)
            if U.fig_value(m, "y", 0.18, t0) > wl + 0.02:
                continue
            tg = t0 + 0.6 * m.get("gather", 3.0)
            if 0.0 <= t - tg < LIFE:
                a = float(_val("RIPPLES_AUTO", tg, 0.0) or 0.0)
                out.append((U.fig_value(m, "x", 0.5, tg), min(U.fig_value(m, "y", 0.18, tg), wl - 0.01), t - tg, 0.6 * a))
            # one ripple per step while the figure walks
            seg = ts[(ts >= t0) & (ts <= t1)]
            if len(seg) < 2:
                continue
            hgt = U.fig_value(m, "height", 0.34, t0)
            step = 0.10 * hgt
            xs = np.array([U.fig_value(m, "x", 0.5, tt) for tt in seg])
            idx = np.floor(xs / step)
            for j in np.nonzero(np.diff(idx) != 0)[0]:
                tt = float(seg[j + 1])
                a = float(_val("RIPPLES_AUTO", tt, 0.0) or 0.0)
                y = min(U.fig_value(m, "y", 0.18, tt), wl - 0.01)
                out.append((float(xs[j + 1]), y, t - tt, 0.40 * a))
        return out

    def _sky(self):
        return getattr(self.R, "sky", None)

    def _rip_uniforms(self, prog, rips, wl, cam=True):
        """cam: the ripples and the water line are given where the camera (CAMERA_*) shows them now, each ripple
        at the depth of the lake under it. cam=False keeps rest coordinates (for a program wrapped with cam_vs)."""
        sky = self._sky() if cam else None
        arr = np.zeros((MAX_RIP, 4), "f4")
        for k, r in enumerate(rips):
            arr[k] = r
            if sky is not None:
                arr[k, 0:2] = sky.place((r[0], r[1]), sky.ground_depth(r[1]))
        if sky is not None:
            wl = sky.place((0.5, wl), sky.ground_depth(wl))[1]
        if "uRip" in prog:
            prog["uRip"].write(arr.tobytes())
        _setu(prog, uNRip=len(rips), uRipWL=float(wl))

    # ------------------------------------------------------------ composite pass: the ripples bend the lake
    def comp_uniforms(self, prog, t):
        if "uSymK" in prog:   # the SYMBOL_PAINT block: the painted lines of this frame, laid over the scene
            if self.painted and self.paint_k > 0.0:
                self.t_paint.use(location=SYM_UNIT)
                prog["uSymT"].value = SYM_UNIT
                prog["uSymK"].value = float(self.paint_k)
            else:
                prog["uSymK"].value = 0.0
        if not self.has_rip:
            return
        wl = self.water_line(t)
        self._rip_uniforms(prog, self.ripples(t), wl)

    # ------------------------------------------------------------ light: ripple rings, falling stars, symbols
    def draw(self, t):
        if not self.active:
            return
        wl = self.water_line(t)
        calm = float(_val("BOTTOM_CALM", t, 0.0) or 0.0)
        rips = self.ripples(t) if self.has_rip else []
        sky = self._sky()
        if rips:
            self._rip_uniforms(self.p_ring, rips, wl)
            wls = sky.place((0.5, wl), sky.ground_depth(wl))[1] if sky is not None else wl   # the line on screen now
            _setu(self.p_ring, uRect=(0.5, wls / 2.0, 0.5, wls / 2.0), uAspect=S.ASPECT, uCalm=calm, uCalmY=0.335,
                  uBright=float(_val("RIPPLE_BRIGHT", t, 1.0)) * 0.24,
                  uCol=_lin(_val("RIPPLE_COLOR", t), "#ffe6c4"))
            self.v_ring.render(moderngl.TRIANGLE_STRIP)
        self._draw_falls(t, wl)
        self.paint_k = 0.0
        if self.sdata:
            self._rip_uniforms(self.p_sym, rips, wl, cam=False)
            if self.painted:
                self._rip_uniforms(self.p_symp, rips, wl, cam=False)
            for sd in self.sdata:
                self._draw_symbol(sd, t, wl, calm)

    def _draw_falls(self, t, wl):
        pts = []
        for f in self.falls:
            tl = float(f[0])
            # optional: (t, x, y, from x, from y, seconds, trail points): the star's own path, flight time and
            # trail length; without them the original short steep fall
            dur = float(f[5]) if len(f) > 5 else FALL_DUR
            ntr = int(f[6]) if len(f) > 6 else 60
            u = (t - (tl - dur)) / dur
            if not (0.0 <= u <= 1.08):
                continue
            x1 = float(f[1])
            y1 = float(f[2]) if len(f) > 2 else self._default_y(tl, wl)
            sky = self._sky()
            if sky is not None:   # CAMERA: the star lands where the camera shows that spot of the lake now
                x1, y1 = sky.place((x1, y1), sky.ground_depth(y1))
            x0, y0 = (float(f[3]), float(f[4])) if len(f) > 4 else (x1 - 0.13, 0.97)
            du = 0.006 if ntr == 60 else 0.006 * (60.0 / ntr) ** 0.5   # a longer trail is also a denser one
            for j in range(ntr):
                uj = u - j * du
                if uj < 0.0 or uj > 1.0:
                    continue
                e = uj * uj
                x, y = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
                b = (1.0 - j / float(ntr)) ** 2 * (1.6 if j == 0 else 0.55) * (1.0 - _ss(0.98, 1.08, u))
                pts.append((x, y, b, 9.0 if j == 0 else 5.0 - 3.0 * j / float(ntr)))
        if not pts:
            return
        arr = np.array(pts[:4096], "f4")
        self.dot_buf.orphan(4 * 4 * 4096)
        self.dot_buf.write(arr.tobytes())
        _setu(self.p_dot, uPx=self.px, uCol=S.lin("#fff2d4"))
        self.v_dot.render(moderngl.POINTS, vertices=len(arr))

    def _draw_symbol(self, sd, t, wl, calm):
        m = sd["meta"]
        t0, t1 = float(m["t0"]), float(m["t1"])
        out = float(m.get("out", 1e9))
        leave = 1 if m.get("leave", "sparks") == "to_star" else 0
        ldur = float(m.get("leave_dur", 2.6 if leave else 2.8))
        if not (t0 <= t < out + ldur + 1.0):
            return
        x, y = float(m.get("x", 0.5)), float(m.get("y", 0.55))
        size, stretch = sd["size"], sd["stretch"]
        glow = float(m.get("glow", 1.0))
        to = S.STAR_POS[int(m.get("star", 4))] if leave else (0.5, 0.9)
        # CAMERA: a symbol hangs over the far shore and moves with it (`depth=` overrides 0.80); the light of the
        # arch it flies to stays where it is
        sky = self._sky()
        aff = (0.0, 0.0, 0.0)
        if sky is not None:
            w = float(m.get("depth", 0.80))
            aff, to = sky.aff(w), sky.unplace(to, w)
        for pr in (self.p_glow, self.p_sym) + ((self.p_symp,) if self.painted else ()):
            if "uCamAff" in pr:
                pr["uCamAff"].value = aff
        op = 0.0
        ot = m.get("open", True)
        if sd["kind"] == "gate" and ot is not None and ot is not False:
            ot = t1 + 0.8 if ot is True else float(ot)
            op = _ss(ot, ot + float(m.get("open_dur", 2.5)), t)
        o_t = (t - out) if t >= out else -1.0
        gone = 1.0 - _ss(out, out + 1.2, t)
        hw, spring, bot = Y.GATE_DOOR
        common = dict(uT=t, uPx=self.px, uAspect=S.ASPECT, uSize=size, uStretch=stretch, uLocal=t - t0,
                      uDur=max(t1 - t0, 0.0), uOut=o_t, uLeaveDur=ldur, uCenter=(x, y), uTo=tuple(to),
                      uLeave=leave, uOpen=op, uDoor=(hw, spring, bot), uCalm=calm, uCalmY=0.335)
        # the soft aura once the symbol is drawn, and the light through the open gate
        aura = _ss(t1 - 0.6, t1 + 1.6, t) * gone * glow
        ex = sd["ext"]
        if aura > 0.001:
            _setu(self.p_glow, uCenter=(x, y), uSize=size, uAspect=S.ASPECT, uStretch=stretch, uMode=0, uT=t,
                  uBox=(ex[0] * 1.5, ex[1] * 1.5, ex[2] * 1.5, ex[3] * 1.5), uAmt=0.10 * aura,
                  uCol=sd["avg"])
            self.v_glow.render(moderngl.TRIANGLE_STRIP)
        if op > 0.001 and gone > 0.001:
            _setu(self.p_glow, uCenter=(x, y), uSize=size, uAspect=S.ASPECT, uStretch=stretch, uMode=1, uT=t,
                  uBox=(-0.55, -0.80, 0.55, 0.40), uAmt=glow * gone, uOpen=op, uDoor=(hw, spring, bot),
                  uCol=S.lin(m.get("light", "#ffcf7a")), uColHot=S.lin("#fff3d8"))
            self.v_glow.render(moderngl.TRIANGLE_STRIP)
        reflect = bool(m.get("reflect", True))
        stroke = float(m.get("stroke", 1.0))   # optional: thickness of the drawn line (1 = as before)
        mgain = float(m.get("mirror", 1.0))    # optional: strength of the mirror image in the lake (1 = as before)
        halo = float(m.get("halo", 1.0))       # optional: strength of the soft glow round the line (1 = as before)
        passes = [(0.0, 3.2 * stroke, 0.30, 1.0), (0.0, 15.0, 0.022 * halo, 0.4)]
        if reflect:
            passes += [(1.0, 3.6 * stroke, 0.30 * mgain, 0.6), (1.0, 15.0, 0.020 * mgain * halo, 0.3)]
        # optional `paint`: while the symbol is here its chosen lines are painted in their own colour and carry
        # only `paint_light` of their light; as it leaves, the paint goes and the lines are light again. The
        # mirror image in the lake stays light alone, at its full strength (painted, it was heavier than the
        # symbol above it: check still of run 43711153933).
        pk = 0.0
        if sd.get("vao_paint") is not None:
            pk = min(float(m.get("paint", 0.0)), 1.0) * (1.0 - _ss(out, out + float(m.get("paint_out", 0.9)), t))
        if pk > 0.001:
            lk = 1.0 + (float(m.get("paint_light", 0.3)) - 1.0) * pk
            groups = [(sd["vao_rest"], 1.0), (sd["vao_lit"], lk)]
        else:
            groups = [(sd["vao"], 1.0)]
        for mir, pt, br, hd in passes:
            for vao, k in groups:
                if vao is None:
                    continue
                _setu(self.p_sym, uMirror=mir, uPt=pt, uBright=br * glow * (k if mir < 0.5 else 1.0), uHead=hd,
                      **common)
                vao.render(moderngl.POINTS)
        if pk > 0.001:
            ctx = self.ctx
            self.f_paint.use()
            if self.paint_k <= 0.0:   # the first painted symbol of this frame: a clean layer
                self.f_paint.clear(0.0, 0.0, 0.0, 0.0)
            ctx.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
            # the line itself, a little wider than its light, and a faint tint round it
            pw = float(m.get("paint_width", 1.7))
            pp = [(0.0, 3.2 * stroke * pw, 0.90 * pk), (0.0, 24.0, 0.012 * halo * pk)]
            for mir, pt, br in pp:
                _setu(self.p_symp, uMirror=mir, uPt=pt, uBright=br, uHead=0.0, **common)
                sd["vao_paint"].render(moderngl.POINTS)
            ctx.blend_func = (moderngl.ONE, moderngl.ONE)
            self.R.f_L.use()
            self.paint_k = 1.0
