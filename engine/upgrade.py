"""Upgrade layers for the backdrop engine (2026-11-13): scene plates, people of light, effect layers, fragment styles.

Everything here is optional. A song file switches a feature on by defining its setting; songs that define none of
them render exactly as before. How a song uses these is in engine/UPGRADE-HOWTO.md.

  SCENES     painted plates behind the light, with crossfades, slow zoom and pan, and a shimmering lake
  FIGURES    people of light made of golden sparks that gather, move from pose to pose and dissolve into the arch
  SNOW, ICE, SHARDS, SHARDS_MEND, GOLDEN_FIELD, NET, BEAM   effect layers driven by Tracks (0 = off)
  FRAGMENTS  style="write" | "reflection" | "petals" | "engrave" (or the default "sparks")
"""
import math
import os

import numpy as np
import moderngl
from PIL import Image

import song as S
import text as T
import upgrade_shaders as U
import shaders as G

TRANSITIONS = {"fade": 0, "dissolve": 1, "bloom": 2, "ripple": 3, "push": 4}
STYLES = {"write": 1, "reflection": 2, "petals": 3, "engrave": 4}


def val(name, t, default=None):
    """A song setting that may be a constant or a function of time (a Track is a function of time)."""
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def col(c, default):
    c = c if c is not None else default
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0) if b != a else float(x >= a)
    return u * u * (3 - 2 * u)


def setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v


def _path(p):
    return p if os.path.isabs(p) else os.path.join(S.ROOT, p)


# ---------------------------------------------------------------- matching sparks between poses
def match_points(A, B):
    """Reorders B so B[i] is near A[i] in the same part of the body (recursive halving along the longer side)."""
    n = len(A)
    out = np.empty(n, dtype=np.int64)
    stack = [(np.arange(n), np.arange(n))]
    while stack:
        ia, ib = stack.pop()
        if len(ia) <= 2:
            out[ia] = ib
            continue
        pa = A[ia]
        axis = 0 if np.ptp(pa[:, 0]) * 1.4 > np.ptp(pa[:, 1]) else 1
        sa = ia[np.argsort(A[ia, axis], kind="stable")]
        sb = ib[np.argsort(B[ib, axis], kind="stable")]
        m = len(ia) // 2
        stack.append((sa[:m], sb[:m]))
        stack.append((sa[m:], sb[m:]))
    return B[out]


def pose_layers(gray):
    """From a white-on-black pose (float 0..1, top row first) builds line, glass body and halo layers."""
    from scipy import ndimage as ndi
    line = np.clip(gray * 1.25, 0.0, 1.0)
    mask = gray > 0.22
    filled = ndi.binary_fill_holes(ndi.binary_closing(mask, iterations=4))
    if filled.sum() < mask.sum() * 2.5:   # the outline is not closed: use a soft body round the lines
        filled = ndi.binary_fill_holes(ndi.gaussian_filter(gray, 5.0) > 0.07)
    filled = ndi.binary_opening(filled, iterations=2)
    dist = ndi.distance_transform_edt(filled)
    rim = np.exp(-dist / 7.0)
    hgt = gray.shape[0]
    grad = (0.70 + 0.40 * (1.0 - np.arange(hgt) / hgt))[:, None]
    glass = ndi.gaussian_filter(filled * (0.16 + 0.84 * rim) * grad, 1.2)
    halo = ndi.gaussian_filter(filled.astype(np.float32), 20.0)
    halo /= max(halo.max(), 1e-6)
    return line, np.clip(glass, 0, 1), halo, filled


# ---------------------------------------------------------------- the layers
class Upgrade:
    def __init__(self, R):
        self.R = R
        ctx = self.ctx = R.ctx
        self.w, self.h, self.px = R.w, R.h, R.px

        def prog(vs, fs):
            return ctx.program(vertex_shader=vs, fragment_shader=fs)

        self.quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        self.scenes = list(getattr(S, "SCENES", []) or [])
        self.figs = list(getattr(S, "FIGURES", []) or [])
        self.sfrags = [f for f in getattr(S, "FRAGMENTS", []) if f.get("style", "sparks") in STYLES]
        self.has_snow = getattr(S, "SNOW", None) is not None
        self.has_net = getattr(S, "NET", None) is not None
        self.has_beam = getattr(S, "BEAM", None) is not None
        self._init_plates()
        if self.figs:
            self.p_figp = prog(U.FIGP_VS, U.FIGP_FS)
            self.p_figt = prog(U.FIGT_VS, U.FIGT_FS)
            self.v_figt = ctx.vertex_array(self.p_figt, [(self.quad, "2f", "aPos")])
            self._init_figures()
        if self.has_snow:
            self.p_snow = prog(U.SNOW_VS, U.SNOW_FS)
            sd = np.random.default_rng(11).random((4200, 4)).astype("f4")
            self.v_snow = ctx.vertex_array(self.p_snow, [(ctx.buffer(sd.tobytes()), "4f", "aSeed")])
        if self.has_net:
            self.p_net = prog(G.QUAD_VS, U.NET_FS)
            setu(self.p_net, uFlip=1.0)
            self.v_net = ctx.vertex_array(self.p_net, [(self.quad, "2f", "aPos")])
        if self.has_beam:
            self.p_beam = prog(G.QUAD_VS, U.BEAM_FS)
            setu(self.p_beam, uFlip=1.0)
            self.v_beam = ctx.vertex_array(self.p_beam, [(self.quad, "2f", "aPos")])
        if self.sfrags:
            self.p_fragt = prog(G.QUAD_VS, U.FRAGT_FS)
            setu(self.p_fragt, uFlip=1.0)
            self.v_fragt = ctx.vertex_array(self.p_fragt, [(self.quad, "2f", "aPos")])
            self.p_fragp = prog(U.FRAGP_VS, U.FRAGP_FS)
            self._init_frags()

    # ------------------------------------------------------------ A. scene plates
    def _init_plates(self):
        self.ptex = {}
        for sc in self.scenes:
            p = sc["image"]
            if p in self.ptex:
                continue
            img = Image.open(_path(p)).convert("RGB")
            if img.size != (1920, 1080):
                img = img.resize((1920, 1080), Image.LANCZOS)
            arr = np.asarray(img)[::-1].copy()
            tx = self.ctx.texture((1920, 1080), 3, data=arr.tobytes(), dtype="f1")
            tx.build_mipmaps()
            tx.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            tx.repeat_x = tx.repeat_y = False
            self.ptex[p] = tx

    def _plate_view(self, sc, t, extra_zoom=1.0):
        t0, t1 = sc["t0"], sc["t1"]
        u = min(max((t - t0) / max(t1 - t0, 1e-3), 0.0), 1.0)
        z = sc.get("zoom", 1.06)
        z0, z1 = (z, z) if np.isscalar(z) else z
        zz = max((z0 + (z1 - z0) * u) * extra_zoom, 1.0)
        pan = sc.get("pan", ((0.0, 0.0), (0.0, 0.0)))
        cx = 0.5 + pan[0][0] + (pan[1][0] - pan[0][0]) * u
        cy = 0.5 + pan[0][1] + (pan[1][1] - pan[0][1]) * u
        half = 0.5 / zz
        cx, cy = min(max(cx, half), 1 - half), min(max(cy, half), 1 - half)
        g = sc.get("gain", 1.0)
        g = g(t) if callable(g) else g
        return (cx, cy, zz, float(g))

    def plate_state(self, t):
        act = []
        for sc in self.scenes:
            t0, t1 = sc["t0"], sc["t1"]
            if not (t0 <= t < t1):
                continue
            fi, fo = sc.get("fade_in", 2.0), sc.get("fade_out", 2.0)
            pin = ss(t0, t0 + fi, t) if fi > 0 else 1.0
            pout = 1.0 - (ss(t1 - fo, t1, t) if fo > 0 else 0.0)
            act.append(dict(sc=sc, pin=pin, pout=pout))
        act = act[-2:]
        flash = 0.0
        slots = []
        for k, a in enumerate(act):
            sc = a["sc"]
            mode = TRANSITIONS.get(sc.get("transition", "fade"), 0)
            pout = a["pout"]
            ez = 1.0
            if k == 0 and len(act) == 2:
                nxt = act[1]
                pout = min(1.0, pout + nxt["pin"])   # stay whole while the next scene comes in over it
                if nxt["sc"].get("transition") == "push":
                    ez = 1.0 + 0.35 * nxt["pin"] ** 1.6
            if mode == 4:
                ez *= 0.90 + 0.10 * (1 - (1 - a["pin"]) ** 2)
            if mode == 2 and 0 < a["pin"] < 1:
                flash += math.sin(math.pi * a["pin"]) ** 2 * sc.get("flash", 0.9)
            view = self._plate_view(sc, t, ez)
            wl = sc.get("water_line", S.HORIZON)
            rc = sc.get("ripple_from", (0.5, S.HORIZON * 0.6))
            slots.append(dict(tex=self.ptex[sc["image"]], view=view,
                              wat=(1.0 if sc.get("water") else 0.0, float(wl), float(sc.get("water_strength", 1.0)),
                                   float(sc.get("water_bottom", 0.0))),
                              tr=(float(mode), float(a["pin"]), float(rc[0]), float(rc[1])),
                              alpha=float(sc.get("opacity", 1.0)) * pout))
        return slots, flash

    def comp_uniforms(self, prog, t, P):
        """Sets the composite pass's upgrade uniforms (plates, shards, ice, field, flash)."""
        slots, flash = self.plate_state(t) if self.scenes else ([], 0.0)
        kw = dict(uPlN=len(slots), uFlash=float(flash + (val("FLASH", t, 0.0) or 0.0)),
                  uShadeK=float(val("TEXT_SHADOW", t, 1.0)))
        for k, sl in enumerate(slots):
            key = "A" if k == 0 else "B"
            sl["tex"].use(location=10 + k)
            kw.update({f"uPl{key}": 10 + k, f"uPl{key}View": sl["view"], f"uPl{key}Wat": sl["wat"],
                       f"uPl{key}Tr": sl["tr"], f"uPl{key}Alpha": sl["alpha"]})
        sh, mend = val("SHARDS", t, 0.0) or 0.0, val("SHARDS_MEND", t, 0.0) or 0.0
        kw["uShards"] = (float(sh), float(mend), float(val("SHARDS_SCALE", t, 4.2)),
                         float(val("SHARDS_Y", t, S.HORIZON + 0.015)))
        kw["uShardCol"] = col(val("SHARDS_COLOR", t), "#ffd27a")
        ice = val("ICE", t, 0.0) or 0.0
        kw["uIce"] = (float(ice), float(val("ICE_LINE", t, S.HORIZON)), float(val("ICE_OPACITY", t, 0.92)),
                      float(val("ICE_FRAME", t, 0.0) or 0.0))
        kw["uIceCol"] = col(val("ICE_COLOR", t), "#cfe2ff")
        kw["uThawCol"] = col(val("THAW_COLOR", t), "#ffbf8a")
        fld = val("GOLDEN_FIELD", t, 0.0) or 0.0
        kw["uField"] = (float(fld), float(val("FIELD_LINE", t, S.HORIZON)), float(val("FIELD_SPEED", t, 1.1)), 0.0)
        kw["uFieldCol"] = col(val("FIELD_COLOR", t), "#ffc35a")
        setu(prog, **kw)

    # ------------------------------------------------------------ B. people of light
    def _init_figures(self):
        ctx = self.ctx
        self.fdata = []
        for fi, fg in enumerate(self.figs):
            poses = fg["poses"][:4]
            grays = []
            for p in poses:
                g = np.asarray(Image.open(_path(p)).convert("L")).astype(np.float32) / 255.0
                if grays and g.shape != grays[0].shape:
                    g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize(
                        (grays[0].shape[1], grays[0].shape[0]), Image.LANCZOS)).astype(np.float32) / 255.0
                grays.append(g)
            H0, W0 = grays[0].shape
            n = int(fg.get("particles", 9000))
            rng = np.random.default_rng(1234 + fi)
            pts, texs = [], []
            th = 640
            tw = int(round(W0 * th / H0))
            for g in grays:
                small = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)
                                   ).astype(np.float32) / 255.0
                line, glass, halo, filled = pose_layers(small)
                tex = np.dstack([line, glass, halo])
                tex = (np.clip(tex, 0, 1) * 255).astype(np.uint8)[::-1].copy()
                t_ = ctx.texture((tw, th), 3, data=tex.tobytes(), dtype="f1")
                t_.build_mipmaps()
                t_.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
                t_.repeat_x = t_.repeat_y = False
                texs.append(t_)
                # sparks: most on the lines, some inside the body so it has volume
                n_line = int(n * 0.80)
                wgt = np.clip(small - 0.06, 0, None) ** 1.4
                p1 = self._sample(wgt, n_line, rng)
                p2 = self._sample(filled.astype(np.float32) * (0.3 + glass), n - n_line, rng)
                pts.append(np.vstack([p1, p2]))
            base = pts[0]
            order = rng.permutation(n)
            base = base[order]
            aligned = [base] + [match_points(base, rng.permutation(p)) for p in pts[1:]]
            while len(aligned) < 4:
                aligned.append(aligned[-1])
            seeds = rng.random((n, 4)).astype("f4")
            data = np.hstack(aligned + [seeds]).astype("f4")
            vao = ctx.vertex_array(self.p_figp, [(ctx.buffer(data.tobytes()), "2f 2f 2f 2f 4f",
                                                  "aP0", "aP1", "aP2", "aP3", "aSeed")])
            self.fdata.append(dict(meta=fg, vao=vao, texs=texs, aspect=W0 / H0, n=n))

    @staticmethod
    def _sample(wgt, n, rng):
        h, w = wgt.shape
        p = wgt.ravel().astype(np.float64)
        if p.sum() <= 0:
            p = np.ones_like(p)
        p /= p.sum()
        idx = rng.choice(p.size, size=n, p=p)
        ys, xs = np.divmod(idx, w)
        return np.stack([(xs + rng.random(n)) / w, 1.0 - (ys + rng.random(n)) / h], axis=1)

    def _fig_state(self, fd, t):
        m = fd["meta"]
        t0, t1 = m["t0"], m["t1"]
        gat, dis = m.get("gather", 3.0), m.get("dissolve", 3.5)
        if not (t0 <= t < t1 + dis):
            return None
        npose = len(fd["texs"])
        times = list(m.get("pose_times", []))
        if len(times) == npose:
            times = times[1:]
        times = times[:npose - 1]
        md = m.get("morph", 1.8)
        cur = 0
        for k, pt in enumerate(times):
            if t >= pt:
                cur = k + 1
        if cur == 0:
            a = b = 0
            u = 0.0
        else:
            u = min(max((t - times[cur - 1]) / md, 0.0), 1.0)
            a, b = cur - 1, cur
            if u >= 1.0:
                a = b = cur
                u = 0.0
        hgt = m.get("height", 0.34) * (1.0 + 0.006 * math.sin(t * 1.1 + m.get("x", 0.5) * 9.0))
        wid = hgt * fd["aspect"] / S.ASPECT
        x, y = m.get("x", 0.5), m.get("y", 0.18)
        rect = (x - wid / 2.0, y, wid, hgt)
        if "to_star" in m:
            to = S.STAR_POS[m["to_star"]]
        else:
            to = m.get("to", (0.5, 0.90))
        return dict(a=a, b=b, u=u, rect=rect, gather=t - t0, gdur=gat, diss=(t - t1) if t >= t1 else -1.0,
                    ddur=dis, to=to, mode=0 if m.get("leave", "rise") == "rise" else 1)

    def draw_figures(self, t):
        if not self.figs:
            return
        for fd in self.fdata:
            st = self._fig_state(fd, t)
            if st is None:
                continue
            m = fd["meta"]
            c = col(m.get("color"), "#ffcf8a")
            glow = float(m.get("glow", 1.0))
            # outline and glassy body
            formed = ss(st["gdur"] * 0.35, st["gdur"] * 1.05, st["gather"])
            gone = 1.0 - ss(0.0, st["ddur"] * 0.45, st["diss"]) if st["diss"] >= 0 else 1.0
            mu = st["u"] * st["u"] * (3 - 2 * st["u"])
            dip = 1.0 - 0.55 * math.sin(math.pi * st["u"])
            fd["texs"][st["a"]].use(location=0)
            fd["texs"][st["b"]].use(location=1)
            setu(self.p_figt, uTexA=0, uTexB=1, uMix=float(mu), uAlpha=float(formed * gone * dip * glow), uT=t,
                 uGlass=float(m.get("glass", 1.0)), uRect=st["rect"], uFlip=1.0 if m.get("flip") else 0.0,
                 uLine=S.lin("#ffe9c4") * 0.42 + c * 0.45, uBody=c * 0.30, uHalo=c * 0.24)
            self.v_figt.render(moderngl.TRIANGLE_STRIP)
            # the sparks
            setu(self.p_figp, uT=t, uPx=self.px, uRect=st["rect"], uFlip=1.0 if m.get("flip") else 0.0,
                 uPoseA=st["a"], uPoseB=st["b"], uMorph=float(st["u"]), uGather=float(st["gather"]),
                 uGatherDur=float(st["gdur"]), uDiss=float(st["diss"]), uDissDur=float(st["ddur"]),
                 uTo=tuple(float(v) for v in st["to"]), uMode=st["mode"], uBright=glow * float(m.get("sparks", 1.0)),
                 uSize=float(m.get("spark_size", 1.0)), uColA=S.lin("#ffe8c0"), uColB=c * 1.2)
            fd["vao"].render(moderngl.POINTS)

    # ------------------------------------------------------------ C. effect layers drawn as light
    def draw_effects(self, t, P):
        if self.has_snow:
            a = val("SNOW", t, 0.0) or 0.0
            if a > 0.001:
                setu(self.p_snow, uT=t, uAmount=float(a), uPx=self.px, uWind=float(val("SNOW_WIND", t, 0.35)),
                     uSpeed=float(val("SNOW_SPEED", t, 1.0)), uCol=col(val("SNOW_COLOR", t), "#eef4ff") * 0.95)
                self.v_snow.render(moderngl.POINTS)
        if self.has_beam:
            a = val("BEAM", t, 0.0) or 0.0
            if a > 0.001:
                setu(self.p_beam, uT=t, uAspect=S.ASPECT, uAmt=float(a),
                     uFrom=tuple(val("BEAM_FROM", t, (0.5, 1.02))), uTo=tuple(val("BEAM_TO", t, (0.5, S.HORIZON))),
                     uW=tuple(val("BEAM_WIDTH", t, (0.03, 0.08))), uCol=col(val("BEAM_COLOR", t), "#ffe2a8"))
                self.v_beam.render(moderngl.TRIANGLE_STRIP)
        if self.has_net:
            a = val("NET", t, 0.0) or 0.0
            if a > 0.001:
                setu(self.p_net, uT=t, uAspect=S.ASPECT, uAmt=float(a), uScale=float(val("NET_SCALE", t, 7.0)),
                     uY0=float(val("NET_Y0", t, 0.30)), uBright=float(val("NET_BRIGHT", t, 1.0)),
                     uOrigin=tuple(val("NET_ORIGIN", t, (0.5, 0.45))), uCol=col(val("NET_COLOR", t), "#ffd99a"),
                     uColB=col(val("NET_PULSE", t), "#fff4e0"))
                self.v_net.render(moderngl.TRIANGLE_STRIP)

    # ------------------------------------------------------------ D. fragment styles
    def _init_frags(self):
        ctx = self.ctx
        self.fd = []
        for k, fr in enumerate(self.sfrags):
            tex, bounds = T.render_fragment(fr["text"], fr.get("dy", 0.0), fr.get("size", 74))
            sharp = tex[::-1, :, 0].astype(np.float64)
            rows = np.nonzero(sharp.max(axis=1) > 40)[0]
            top, bot = 1.0 - rows.min() / T.H, 1.0 - (rows.max() + 1) / T.H
            t_ = ctx.texture((T.W, T.H), 3, data=tex.tobytes(), dtype="f1")
            t_.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t_.repeat_x = t_.repeat_y = False
            style = STYLES[fr["style"]]
            n = {1: 6000, 2: 1800, 3: 1500, 4: 7000}[style]
            rng = np.random.default_rng(777 + k)
            p = (sharp / sharp.sum()).ravel()
            idx = rng.choice(p.size, size=n, p=p)
            ys, xs = np.divmod(idx, T.W)
            px, py = xs + rng.random(n), ys + rng.random(n)
            x0, x1 = bounds[0] * T.W, bounds[1] * T.W
            order = (px - x0) / max(x1 - x0, 1.0)
            pts = np.stack([px / T.W, 1.0 - py / T.H, order], axis=1).astype("f4")
            seeds = rng.random((n, 4)).astype("f4")
            vao = ctx.vertex_array(self.p_fragp, [(ctx.buffer(np.hstack([pts, seeds]).tobytes()), "3f 4f",
                                                   "aTarget", "aSeed")])
            self.fd.append(dict(meta=fr, tex=t_, bounds=bounds, style=style, vao=vao, top=top, bot=bot))

    def _frag_times(self, m, t):
        t0, t1, out = m["t0"], m["t1"], m["out"]
        if not (t0 <= t < out + 2.6):
            return None
        return t - t0, max(t1 - t0, 0.5), (t - out) if t > out else -1.0

    def draw_frags(self, t):
        if not self.sfrags:
            return
        for f in self.fd:
            m = f["meta"]
            tm = self._frag_times(m, t)
            if tm is None:
                continue
            loc, dur, out = tm
            st = f["style"]
            hot = {1: "#fff4dc", 2: "#e6f0ff", 3: "#ffe8ee", 4: "#ffb662"}[st]
            pc = m.get("colors") or getattr(S, "PETAL_COLORS", None) or ("#ff9fb2", "#ffe0d2")
            f["tex"].use(location=0)
            setu(self.p_fragt, uTex=0, uMode=st, uLocal=float(loc), uDur=float(dur), uOut=float(out),
                 uAspect=S.ASPECT, uHz=float(m.get("line", S.HORIZON)), uAlpha=float(m.get("alpha", 0.95)),
                 uTop=float(f["top"]), uBot=float(f["bot"]), uBounds=f["bounds"], uCol=S.lin("#fff1d6"),
                 uGlowCol=S.lin(m.get("glow", "#ffc48c")), uHot=S.lin(hot))
            self.v_fragt.render(moderngl.TRIANGLE_STRIP)
            if st == 3:
                ca, cb = S.lin(pc[0]) * 0.95, S.lin(pc[1]) * 0.7
            elif st == 4:
                ca, cb = S.lin("#ffd27a"), S.lin("#ff9a4a")
            else:
                ca, cb = S.lin("#fff0cc"), S.lin(m.get("glow", "#ffb070"))
            setu(self.p_fragp, uMode=st, uT=t, uLocal=float(loc), uDur=float(dur), uOut=float(out), uPx=self.px,
                 uHz=float(m.get("line", S.HORIZON)), uColA=ca, uColB=cb, uHot=S.lin(hot))
            f["vao"].render(moderngl.POINTS)

    def text_shadow(self, t):
        """A soft shadow behind a styled fragment so it reads on bright plates: (texture, params, bounds, shade)."""
        for f in getattr(self, "fd", []):
            tm = self._frag_times(f["meta"], t)
            if tm is None:
                continue
            loc, dur, out = tm
            shade = ss(0.2 * dur, dur, loc) * (1.0 - ss(0.0, 1.4, out) if out > 0 else 1.0)
            return f["tex"], (99.0, 1.0, out if out > 0 else -1.0, 0.85), f["bounds"], shade
        return None
