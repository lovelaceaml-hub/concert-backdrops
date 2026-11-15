"""The 3D layer inside the engine (made by render.py only for a song with the key P3D).

render.py calls, in frame order:
  adjust(t, P)       after the song's params: the camera and the world of this frame; the flat sky's own
                     stars, motes, lanterns, arch and lake are switched off (the 3D world replaces them)
  draw(t, P)         in the light pass: the silhouette masks, then every point set as sprites into the HDR
                     light buffer, each with its mirror image in the lake
  background(t, P)   before the composite: sky dome, hills, lake, mist, shafts, rays, dark bodies and double
                     exposures, bursts; handed to the composite as its background (texture unit 15)
Everything is a pure function of t, so any part of a video renders the same frames.
"""
import numpy as np
import moderngl

import song as S
from . import api
from . import camera as C
from . import shaders as K
from . import world as Wd

KIND_ID = dict(soft=0, spark=1, disc=2, flake=3, petal=4, bird=5, line=6, ribbon=7)
CAM_UNIT = 15            # the composite's background unit (shared with engine/sky_camera.py, never both)
SHORE = 1400.0           # metres from the origin to the foot of the first hills: the lake ends there
FLAT_LAYERS = ("stars", "motes", "lanterns", "petals", "arch", "skyline", "rings", "waves")


def setu(prog, **kw):
    for k, v in kw.items():
        if k not in prog:
            continue
        if isinstance(v, np.ndarray):
            if v.shape == (4, 4):
                prog[k].write(np.ascontiguousarray(v.T, dtype="f4").tobytes())
                continue
            v = tuple(float(x) for x in v.ravel())
        prog[k].value = v


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


class Layer:
    def __init__(self, R):
        cfg = dict(S.P3D) if isinstance(S.P3D, dict) else {}
        known = {"camera", "world", "setup", "sets", "keep", "motion_blur", "bursts", "lod", "bokeh_max"}
        if set(cfg) - known:
            raise ValueError(f"P3D: unknown keys {sorted(set(cfg) - known)} (known: {sorted(known)})")
        self.R = R
        ctx = self.ctx = R.ctx
        self.w, self.h = R.w, R.h
        import draft
        self.draft = bool(draft.DRAFT)
        self.rig = C.make(cfg.get("camera"))
        self.world = Wd.World(cfg.get("world"))
        self.keep = set(cfg.get("keep") or ())
        if self.keep - set(FLAT_LAYERS):
            raise ValueError(f"P3D keep: unknown layers {sorted(self.keep - set(FLAT_LAYERS))} (known: {FLAT_LAYERS})")
        mb = cfg.get("motion_blur", None)
        self.shutter = float(self.rig.shutter if mb is None else mb)
        self.bursts = [dict(b) for b in (cfg.get("bursts") or [])]
        self.lod_r = float(cfg.get("lod", 7.0))
        self.bokeh_max = float(cfg.get("bokeh_max", 0.20))

        # the scene: the world's own sets, then the song's
        self.scene = api.Scene()
        wd = self.world
        n = draft.n
        self.scene.add("_stars", Wd.Stars(wd, n=n(14000)), fog=False)
        self.scene.add("_sun", Wd.SunGlow(wd), fog=False, depth_of_field=False, lod=False)
        self.scene.add("_dust", Wd.Dust(wd, **{**dict(n=n(7000), n_bokeh=n(300)), **wd.dust_cfg}))
        self.scene.add("_lanterns", Wd.Lanterns(wd, **{**dict(count=n(420)), **wd.lantern_cfg}), lod=False)
        self.arch = None
        if wd.arch:
            akw = dict(wd.arch) if isinstance(wd.arch, dict) else {}
            self.arch = Wd.Arch(wd, **akw)
            self.scene.add("_arch", self.arch)
        if cfg.get("setup"):
            cfg["setup"](self.scene)
        for item in cfg.get("sets") or []:
            self.scene.add(**item)

        # programs
        def prog(vs, fs):
            return ctx.program(vertex_shader=vs, fragment_shader=fs)

        self.p_sprite = prog(K.SPRITE_VS, K.SPRITE_FS)
        self.p_seg = prog(K.SEG_VS, K.SEG_FS)
        self.p_mask = prog(K.MASK_VS, K.MASK_FS)
        self.p_mblur = prog(K.QUAD_VS, K.MASKBLUR_FS)
        self.p_bg = prog(K.QUAD_VS, K.BG_FS)
        self.p_rsrc = prog(K.QUAD_VS, K.RAYSRC_FS)
        self.p_rad = prog(K.QUAD_VS, K.RADIAL_FS)
        self.p_res = prog(K.QUAD_VS, K.RESOLVE_FS)
        self.quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        self.b_zero3 = ctx.buffer(np.array([0.0, 0.0, 1.0], "f4").tobytes())
        self.b_vel0 = ctx.buffer(np.array([0.0, 0.0, 0.0], "f4").tobytes())

        def qvao(p):
            return ctx.vertex_array(p, [(self.quad, "2f", "aPos")])

        self.v_mblur, self.v_bg, self.v_rsrc = qvao(self.p_mblur), qvao(self.p_bg), qvao(self.p_rsrc)
        self.v_rad, self.v_res = qvao(self.p_rad), qvao(self.p_res)

        def tex(size):
            t = ctx.texture(size, 4, dtype="f2")
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t, ctx.framebuffer([t])

        w, h = self.w, self.h
        self.msize = (max(w // 2, 8), max(h // 2, 8))
        self.t_mask, self.f_mask = tex(self.msize)
        self.t_mask2, self.f_mask2 = tex(self.msize)
        self.t_bg, self.f_bg = tex((w, h))
        self.t_fin, self.f_fin = tex((w, h))
        qs = (max(w // 4, 8), max(h // 4, 8))
        self.t_rsrc, self.f_rsrc = tex(qs)
        self.t_rtmp, self.f_rtmp = tex(qs)
        self.t_rayA, self.f_rayA = tex(qs)
        self.t_rayB, self.f_rayB = tex(qs)
        self.f_rayA.clear(0.0, 0.0, 0.0, 1.0)
        self.f_rayB.clear(0.0, 0.0, 0.0, 1.0)
        self.slots = {}
        self._static = {}
        self._frame = None
        self._mask = None
        try:
            from audio_react import audio
            self.audio = audio if self.world.react else None
        except Exception:       # pragma: no cover
            self.audio = None
        print(f"p3d: {len(self.scene.names())} point sets ({', '.join(self.scene.names())}), "
              f"{len(self.rig.moves)} camera moves, motion blur {self.shutter:g}", flush=True)

    # ------------------------------------------------------------------ the frame's camera and world
    def state(self, t):
        if self._frame is not None and self._frame[0] == t:
            return self._frame[1:]
        asp = float(S.ASPECT)
        cam = self.rig.state(t, asp)
        prev = self.rig.state(t - self.shutter / float(S.FPS), asp) if self.shutter > 0.0 else cam
        w = self.world.state(t)
        rc = self.world.react
        if self.audio is not None and rc:
            bt, lv = self.audio.beat(t), self.audio.level(t)
            kb, kl = float(rc.get("beat", 0.0)), float(rc.get("level", 0.0))
            w["dust"] = w["dust"] * (1.0 + 0.8 * kb * bt)
            w["bokeh"] = w["bokeh"] * (1.0 + 0.8 * kb * bt)
            w["sun_int"] = w["sun_int"] * (1.0 + 0.5 * kl * lv)
            w["rays"] = w["rays"] * (1.0 + 0.8 * kl * lv)
            w["exposure"] = w["exposure"] * (1.0 + 0.05 * kb * bt)
            w["_beat"] = kb * bt
        else:
            w["_beat"] = 0.0
        self.world.now = w
        self._frame = (t, cam, prev, w)
        return cam, prev, w

    def adjust(self, t, P):
        cam, prev, w = self.state(t)
        if self.arch is not None:
            self.arch.song_state = list(P.get("star", []))
            self.arch.beat = w["_beat"] * 0.35
        keep = self.keep
        if "stars" not in keep:
            P["stars"] = 0.0
            P["milky"] = 0.0
        if "motes" not in keep:
            P["motes"] = 0.0
        if "lanterns" not in keep:
            P["lanterns"] = 0.0
        if "petals" not in keep:
            P["petals"] = 0.0
        if "arch" not in keep:
            P["star"] = [(0.0, -1.0)] * 9
            P["link"] = [0.0] * 8
        if "skyline" not in keep:
            P["lantern"] = (-2.0, -2.0)
        if "rings" not in keep:
            P["rings"] = []
        if "waves" not in keep:
            P["waves"] = []
        P["sun_int"] = min(float(w["sun_int"]), 1.3) * _ss(-2.0, 2.0, float(w["sun_el"]))
        P["exposure"] = float(P.get("exposure", 1.0)) * float(w["exposure"])
        P["p3d_cam"] = cam
        return P

    def camera(self, t):
        """The camera at t (a CameraState): for other layers that want to place something in the 3D picture."""
        return self.state(t)[0]

    def _uniforms(self, t, cam, prev, w):
        r, u, f = cam.basis()
        focal = 1.0 / np.tan(np.radians(cam.fov) * 0.5)
        px = self.h / 1080.0
        cs = float(w["cloud_speed"])
        return dict(
            uView=cam.view(), uProj=cam.proj(), uPrevVP=prev.proj() @ prev.view(), uCamPos=np.asarray(cam.pos),
            uCamR=r, uCamU=u, uCamF=f, uRes=(float(self.w), float(self.h)), uFocal=float(focal),
            uAspect=float(cam.aspect), uFocus=float(cam.focus), uAperture=float(cam.aperture), uNear=0.08,
            uT=float(t), uHillP=(float(w["hills"]), float(w["hill_height"]), 0.0, 0.0),
            uCloudP=(float(w["clouds"]), 0.006 * cs, 0.003 * cs, 0.55), uSunDir=w["sun_dir"],
            uFogP=(float(w["haze"]) * 0.0011, float(w["mist"]) * 0.020, float(w["mist_height"]),
                   0.10 + 0.25 * float(w["haze"])),
            uLakeP=(float(w["mirror_min"]), float(w["mirror"]), float(w["ripple"]), SHORE),
            uSigMin=0.6, uCocMax=self.bokeh_max * self.h, uLodR=self.lod_r * px, uDomeDist=3000.0,
            uShutterDt=self.shutter / float(S.FPS), uMaxStreak=0.20 * self.h, uSmear=0.03, uPx=px,
            uBokeh=(float(w["bokeh_ring"]), float(w["bokeh_hex"])), uHair=0.30 * px,
        )

    # ------------------------------------------------------------------ point sets to buffers
    def _batches(self, entry, t, cam):
        ps = entry.pointset
        if getattr(ps, "static", False):
            if entry.name not in self._static:
                self._static[entry.name] = self.scene.collect(entry, 0.0, cam)
            bs = self._static[entry.name]
            g = float(ps.gain(t)) if hasattr(ps, "gain") else 1.0
            for b in bs:
                b["gain"] = g
            return bs
        return self.scene.collect(entry, t, cam)

    def _slot(self, key, b, static=False):
        ctx = self.ctx
        sl = self.slots.get(key)
        if sl is None:
            sl = self.slots[key] = dict(cap=0, core=None, normal=None, seg=None, vel=None, vaos={}, done=False,
                                        draft_keep=True)
        if static and sl["done"]:
            return sl
        n = b["n"]
        step = 2 if (self.draft and n > 30000) else 1       # a draft draws every second point of a big set
        idx = slice(None, None, step)
        m = len(range(0, n, step))
        core = np.empty((m, 12), np.float32)
        core[:, 0:3] = b["pos"][idx]
        core[:, 3] = b["size"][idx]
        core[:, 4:7] = b["color"][idx]
        core[:, 7] = b["alpha"][idx]
        core[:, 8] = b["emit"][idx] * step
        core[:, 9] = b["seed"][idx]
        core[:, 10:12] = b["rot"][idx]
        if m > sl["cap"] or sl["core"] is None:
            sl["cap"] = int(m * 1.3) + 64
            for k in ("core", "normal", "seg", "vel"):
                if sl[k] is not None:
                    sl[k].release()
                    sl[k] = None
            for v in sl["vaos"].values():
                v.release()
            sl["vaos"] = {}
            sl["core"] = ctx.buffer(reserve=sl["cap"] * 48, dynamic=True)
        sl["core"].write(core.tobytes())

        def extra(name, arr, width):
            if arr is None:
                return False
            if sl[name] is None:
                sl[name] = ctx.buffer(reserve=sl["cap"] * 4 * width, dynamic=True)
                sl["vaos"] = {}
            sl[name].write(np.ascontiguousarray(arr[idx], np.float32).tobytes())
            return True

        sl["has_normal"] = extra("normal", b["normal"], 3)
        sl["has_vel"] = extra("vel", b["vel"], 3)
        if b["pos2"] is not None:
            seg = np.empty((m, 4), np.float32)
            seg[:, 0:3] = b["pos2"][idx]
            seg[:, 3] = b["alpha2"][idx]
            extra("seg", seg, 4)
        sl["n"] = m
        sl["done"] = True
        return sl

    def _vao(self, sl, which):
        key = (which, sl.get("has_normal"), sl.get("has_vel"))
        v = sl["vaos"].get(key)
        if v is not None:
            return v
        ctx = self.ctx
        if which == "sprite":
            content = [(self.quad, "2f", "aCorner"),
                       (sl["core"], "3f 1f 3f 1f 1f 1f 2f /i", "aPos", "aSize", "aColor", "aAlpha", "aEmit", "aSeed", "aRot"),
                       ((sl["normal"], "3f /i", "aNormal") if sl["has_normal"] else (self.b_zero3, "3f /r", "aNormal")),
                       ((sl["vel"], "3f /i", "aVel") if sl["has_vel"] else (self.b_vel0, "3f /r", "aVel"))]
            v = ctx.vertex_array(self.p_sprite, content)
        elif which == "seg":
            v = ctx.vertex_array(self.p_seg, [
                (self.quad, "2f", "aCorner"),
                (sl["core"], "3f 1f 3f 1f 1f 1f 8x /i", "aPos", "aSize", "aColor", "aAlpha", "aEmit", "aSeed"),
                (sl["seg"], "4f /i", "aPos2A2")])
        else:
            v = ctx.vertex_array(self.p_mask, [
                (self.quad, "2f", "aCorner"),
                (sl["core"], "3f 1f 12x 1f 16x /i", "aPos", "aSize", "aAlpha")])
        sl["vaos"][key] = v
        return v

    # ------------------------------------------------------------------ the silhouette masks
    def _mask_pass(self, items, t, cam, U):
        """Draws the silhouettes of the masked sets. Returns the frame's mask state, or None."""
        todo = []
        for e, batches in items:
            if e.mask is None:
                continue
            k = e.mask.strength_at(t)
            if k <= 0.001:
                continue
            todo.append((e, batches, k))
        if not todo:
            return None
        ctx = self.ctx
        self.f_mask.use()
        self.f_mask.clear(0.0, 0.0, 0.0, 60000.0)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        ctx.blend_equation = (moderngl.FUNC_ADD, moderngl.MIN)
        p = self.p_mask
        setu(p, uView=U["uView"], uProj=U["uProj"], uFocal=U["uFocal"], uNear=U["uNear"],
             uRes=(float(self.msize[0]), float(self.msize[1])))
        st = dict(dark=0.0, sky=0.0, kind=1, box=(0.5, 0.5, 0.4, 0.0), edge=0.0, tint=(1.0, 1.0, 1.0), soft=3.0)
        for e, batches, k in todo:
            mk = e.mask
            if mk.source is not None:
                src = api.Entry(e.name + "#mask", mk.source)
                batches = self._batches(src, t, cam)
                name = src.name
            else:
                name = e.name
            sky = mk.mode == "sky"
            pts = []
            for bi, b in enumerate(batches):
                if b["kind"] in api.SEGMENT_KINDS:
                    continue
                sl = self._slot((name, bi), b, static=getattr(e.pointset, "static", False) and mk.source is None)
                setu(p, uGrow=float(mk.grow), uSel=1 if sky else 0)
                self._vao(sl, "mask").render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
                pts.append(b["pos"][:: max(b["n"] // 400, 1)])
            st["soft"] = max(st["soft"], float(mk.soft))
            if sky:
                st["sky"] = max(st["sky"], k)
                st["kind"] = api.MASK_SKIES.index(mk.sky)
                st["edge"] = float(mk.edge)
                st["tint"] = tuple(float(x) for x in np.asarray(mk.tint, np.float64))
                if pts:
                    xy, z = cam.project(np.concatenate(pts))
                    ok = z > 0.1
                    if np.any(ok):
                        lo, hi = xy[ok].min(axis=0), xy[ok].max(axis=0)
                        st["box"] = (float((lo[0] + hi[0]) * 0.5), float((lo[1] + hi[1]) * 0.5),
                                     float(max((hi[1] - lo[1]) * 0.5, 0.05)), 0.0)
            else:
                st["dark"] = max(st["dark"], k)
        ctx.blend_equation = moderngl.FUNC_ADD
        ctx.disable(moderngl.BLEND)
        d = st["soft"] * (self.h / 1080.0) * 0.5 / 3.2
        self.f_mask2.use()
        self.t_mask.use(location=0)
        setu(self.p_mblur, uTex=0, uDir=(d / self.msize[0], 0.0))
        self.v_mblur.render(moderngl.TRIANGLE_STRIP)
        self.f_mask.use()
        self.t_mask2.use(location=0)
        setu(self.p_mblur, uTex=0, uDir=(0.0, d / self.msize[1]))
        self.v_mblur.render(moderngl.TRIANGLE_STRIP)
        return st

    # ------------------------------------------------------------------ the light pass
    def draw(self, t, P):
        ctx, R = self.ctx, self.R
        cam, prev, w = self.state(t)
        U = self._uniforms(t, cam, prev, w)
        items = [(e, self._batches(e, t, cam)) for e in self.scene.entries()]
        self._mask = self._mask_pass(items, t, cam, U)
        R.f_L.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        mask_on = 0.0
        if self._mask is not None:
            self.t_mask.use(location=0)
            mask_on = 1.0
        blur = 1.0 if self.shutter > 0.0 else 0.0
        mirror = float(w["mirror"]) > 0.001 and cam.pos[1] > 0.0
        for p in (self.p_sprite, self.p_seg):
            setu(p, uMaskTex=0, uMaskOn=mask_on,
                 uMaskK=(self._mask["dark"], self._mask["sky"]) if self._mask else (0.0, 0.0), uMaskBias=0.05, **U)
        for e, batches in items:
            ps = e.pointset
            dome = 1.0 if getattr(ps, "dome", False) else 0.0
            static = getattr(ps, "static", False)
            for bi, b in enumerate(batches):
                if b["gain"] <= 0.0005:
                    continue
                seg = b["kind"] in api.SEGMENT_KINDS
                sl = self._slot((e.name, bi), b, static=static)
                p = self.p_seg if seg else self.p_sprite
                setu(p, uKind=KIND_ID[b["kind"]], uGain=float(b["gain"]), uTwinkle=b["twinkle"], uRim=b["rim"],
                     uDofAmt=b["dof"] if e.depth_of_field else 0.0, uFogAmt=b["fog"] if e.fog else 0.0,
                     uBack=b["backlight"], uLod=1.0 if (b["lod"] and e.lod) else 0.0, uDome=dome,
                     uBlur=blur * b["streak"], uMirror=0.0)
                vao = self._vao(sl, "seg" if seg else "sprite")
                vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
                if mirror and e.reflect and b["reflect"]:
                    setu(p, uMirror=1.0, uMaskOn=0.0)
                    vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
                    setu(p, uMaskOn=mask_on)
        R.f_L.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)

    # ------------------------------------------------------------------ the background
    def _burst_state(self, t, cam):
        out = []
        for b in self.bursts:
            tb = float(b["t"])
            rise, fall = float(b.get("rise", 0.25)), float(b.get("fall", 0.7))
            if not (tb - rise < t < tb + fall * 2.5):
                continue
            env = _ss(tb - rise, tb, t) if t <= tb else float(np.exp(-(t - tb) / (fall * 0.45)))
            k = float(b.get("strength", 4.0)) * env
            if k <= 0.002:
                continue
            xy = (0.5, 0.5)
            if b.get("at") is not None:
                q, z = cam.project(np.asarray(b["at"], np.float64))
                if z[0] > 0.05:
                    xy = (float(q[0, 0]), float(q[0, 1]))
            col = api.lin(b["color"]) if isinstance(b.get("color", "#fff3d6"), str) else np.asarray(b["color"])
            out.append(((xy[0], xy[1], float(b.get("radius", 0.35)), k), tuple(float(x) for x in col)))
        return out[:4]

    def _rays(self, U, mode, center, mask_on, light=None, light_col=(0, 0, 0)):
        """Source and two radial blurs at quarter size; the result is left in t_rayA (sun) or t_rayB (light)."""
        w = self.world.now
        self.f_rsrc.use()
        self.t_bg.use(location=0)
        self.t_mask.use(location=1)
        setu(self.p_rsrc, uBg=0, uMask=1, uCamR=U["uCamR"], uCamU=U["uCamU"], uCamF=U["uCamF"],
             uFocal=U["uFocal"], uAspect=U["uAspect"], uSunDir=w["sun_dir"], uSunCol=np.asarray(w["sun_color"]),
             uSunInt=float(w["sun_int"]), uMaskOn=mask_on, uMode=float(mode), uCenter=center, uFan=0.75,
             uT=U["uT"],
             uLight=light or (0.5, 0.5, 0.1, 1.0), uLightCol=tuple(float(x) for x in light_col))
        self.v_rsrc.render(moderngl.TRIANGLE_STRIP)
        self.f_rtmp.use()
        self.t_rsrc.use(location=0)
        setu(self.p_rad, uTex=0, uCenter=center, uLen=0.92, uDecay=0.86)
        self.v_rad.render(moderngl.TRIANGLE_STRIP)
        (self.f_rayA if mode == 0 else self.f_rayB).use()
        self.t_rtmp.use(location=0)
        setu(self.p_rad, uTex=0, uCenter=center, uLen=0.92 / 14.0, uDecay=1.0)
        self.v_rad.render(moderngl.TRIANGLE_STRIP)

    def background(self, t, P):
        ctx, R = self.ctx, self.R
        cam, prev, w = self.state(t)
        U = self._uniforms(t, cam, prev, w)
        ctx.disable(moderngl.BLEND)
        # 1. sky, hills, lake, mist, shafts
        self.f_bg.use()
        p = self.p_bg
        sh_a = np.zeros((4, 4), "f4")
        sh_b = np.zeros((4, 4), "f4")
        ns = 0
        for sh in self.world.shafts[:4]:
            k = sh.get("strength", 1.0)
            k = float(k(t) if callable(k) else k)
            if k <= 0.001:
                continue
            base = sh.get("base", (0.0, 0.0))
            base = base(t) if callable(base) else base
            col = sh.get("color", "#cfe0ff")
            col = api.lin(col) if isinstance(col, str) else np.asarray(col, np.float64)
            sh_a[ns] = (base[0], base[1], float(sh.get("radius", 1.5)), float(sh.get("top", 40.0)))
            sh_b[ns] = (col[0] * k, col[1] * k, col[2] * k, float(sh.get("spread", 0.0)))
            ns += 1
        if "uShA" in p:
            p["uShA"].write(sh_a.tobytes())
        if "uShB" in p:
            p["uShB"].write(sh_b.tobytes())
        cosr = float(np.cos(np.radians(w["sun_size"])))
        setu(p, uNShaft=ns, uSkyTop=np.asarray(w["sky_top"]), uSkyMid=np.asarray(w["sky_mid"]),
             uSkyHor=np.asarray(w["sky_hor"]), uSunCol=np.asarray(w["sun_color"]),
             uHazeCol=np.asarray(w["haze_color"]), uHillCol=np.asarray(w["hill_color"]),
             uWater=np.asarray(w["water"]), uMilkyN=Wd.MILKY_N, uMistCol=np.asarray(w["mist_color"]),
             uSunP=(float(w["sun_int"]), cosr, float(w["sun_disc"]) * _ss(-1.5, 0.5, float(w["sun_el"])),
                    float(w["sun_glow"])),
             uAirP=(U["uFogP"][0], U["uFogP"][1], U["uFogP"][2], float(w["milky"]) * float(w["stars"])), **U)
        self.v_bg.render(moderngl.TRIANGLE_STRIP)

        # 2. rays (quarter size)
        mk = self._mask
        mask_on = 1.0 if mk is not None else 0.0
        fwd = cam.basis()[2]
        ray_sun = float(w["rays"]) * _ss(0.05, 0.40, float(np.dot(fwd, w["sun_dir"]))) * _ss(-4.0, 0.5, float(w["sun_el"]))
        if ray_sun > 0.002 and float(w["sun_int"]) > 0.002:
            q, z = cam.project(np.asarray(cam.pos) + w["sun_dir"] * 1000.0)
            self._rays(U, 0, (float(q[0, 0]), float(q[0, 1])), mask_on)
        else:
            ray_sun = 0.0
        ray_light = 0.0
        lt = self.world.light
        if lt:
            k = lt.get("strength", 1.0)
            k = float(k(t) if callable(k) else k) * float(lt.get("rays", 1.0))
            pos = lt["pos"](t) if callable(lt["pos"]) else lt["pos"]
            q, z = cam.project(np.asarray(pos, np.float64))
            if k > 0.002 and z[0] > 0.1:
                focal = U["uFocal"]
                rad = max(float(lt.get("size", 0.6)) * 0.5 * focal / z[0], 0.01)
                col = lt.get("color", "#fff0cc")
                col = api.lin(col) if isinstance(col, str) else np.asarray(col, np.float64)
                self._rays(U, 1, (float(q[0, 0]), float(q[0, 1])), mask_on,
                           light=(float(q[0, 0]), float(q[0, 1]), rad, float(z[0])), light_col=col)
                ray_light = k

        # 3. resolve: motion blur, dark bodies, double exposures, rays, bursts
        self.f_fin.use()
        p = self.p_res
        self.t_bg.use(location=0)
        self.t_rayA.use(location=1)
        self.t_rayB.use(location=2)
        self.t_mask.use(location=3)
        bursts = self._burst_state(t, cam)
        ba = np.zeros((4, 4), "f4")
        bc = np.zeros((4, 3), "f4")
        for i, (a, c) in enumerate(bursts):
            ba[i], bc[i] = a, c
        if "uBurst" in p:
            p["uBurst"].write(ba.tobytes())
        if "uBurstCol" in p:
            p["uBurstCol"].write(bc.tobytes())
        moving = self.shutter > 0.0 and (not np.allclose(cam.pos, prev.pos, atol=1e-5)
                                         or not np.allclose(cam.target, prev.target, atol=1e-5))
        setu(p, uBg=0, uRayA=1, uRayB=2, uMask=3, uCamR=U["uCamR"], uCamU=U["uCamU"], uCamF=U["uCamF"],
             uCamPos=U["uCamPos"], uPrevVP=U["uPrevVP"], uFocal=U["uFocal"], uAspect=U["uAspect"], uT=float(t),
             uBlur=1.0 if moving else 0.0, uShore=SHORE, uRes=U["uRes"], uRayK=(ray_sun * 0.55, ray_light, 0.0, 0.0),
             uMaskOn=mask_on, uDarkK=mk["dark"] if mk else 0.0, uSkyK=mk["sky"] if mk else 0.0,
             uFillEdge=mk["edge"] if mk else 0.0, uFillKind=mk["kind"] if mk else 0,
             uFillBox=mk["box"] if mk else (0.5, 0.5, 0.4, 0.0), uFillTint=mk["tint"] if mk else (1.0, 1.0, 1.0),
             uDarkTint=tuple(float(x) for x in np.asarray(w["sky_top"]) * 0.35), uNBurst=len(bursts))
        self.v_res.render(moderngl.TRIANGLE_STRIP)
        self.t_fin.use(location=CAM_UNIT)
        setu(R.p_comp, uCamOn=1.0, uCamBg=CAM_UNIT)
