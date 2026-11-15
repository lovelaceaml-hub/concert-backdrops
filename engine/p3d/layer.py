"""The 3D layer inside the engine (made by render.py only for a song with the key P3D).

render.py calls, in frame order:
  adjust(t, P)       after the song's params: the camera and the world of this frame; the flat sky's own
                     stars, motes, lanterns, arch and lake are switched off (the 3D world replaces them)
  draw(t, P)         in the light pass: the silhouette masks, the paint of painted sets, then every point set
                     as sprites into the HDR light buffer, each with its mirror image in the lake
  background(t, P)   before the composite: sky dome, hills, lake, mist, shafts, rays, dark bodies, windows,
                     paint, bursts; handed to the composite as its background (texture unit 15)
Everything is a pure function of t, so any part of a video renders the same frames.
"""
import numpy as np
import moderngl

import song as S
from . import api
from . import camera as C
from . import shaders as K
from . import world as Wd

KIND_ID = dict(soft=0, spark=1, disc=2, flake=3, petal=4, bird=5, line=6, ribbon=7, shard=8, butterfly=9)
CAM_UNIT = 15            # the composite's background unit (shared with engine/sky_camera.py, never both)
LAKE_UNIT = 7            # the lake field (world key lake), bound while the layer draws
SHORE = 1400.0           # metres from the origin to the foot of the first hills: the lake ends there
FLAT_LAYERS = ("stars", "motes", "lanterns", "petals", "arch", "skyline", "rings", "waves")
CORE_FMT = "3f 1f 3f 1f 1f 1f 2f 1f /i"     # pos, size, colour, alpha, emit, seed, turn (or path places), birth


def setu(prog, **kw):
    for k, v in kw.items():
        if k not in prog:
            continue
        if isinstance(v, np.ndarray):
            if v.shape in ((4, 4), (3, 3)):
                prog[k].write(np.ascontiguousarray(v.T, dtype="f4").tobytes())
                continue
            v = tuple(float(x) for x in v.ravel())
        prog[k].value = v


def seta(prog, name, arr):
    """An array uniform (vec4[4] and the like), written whole."""
    if name in prog:
        prog[name].write(np.ascontiguousarray(arr, dtype="f4").tobytes())


def _ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def _val(v, t):
    return v(t) if callable(v) else v


def _col(c, t):
    c = _val(c, t)
    return api.lin(c) if isinstance(c, str) else np.asarray(c, np.float64)


CHUNK_MIN = 60000        # a static set with at least this many points is drawn in spatial cells (only those in view)
MIRROR_THIN = ((1200000, 3), (300000, 2))    # in the lake mirror a set this large draws every k-th point, k times
#                                              brighter (the image is dimmer and rippled; bodies stay whole)


def _thin(n):
    for lim, k in MIRROR_THIN:
        if n >= lim:
            return k
    return 1


def _chunks(pos, size, dome):
    """Sorts points into a grid of cells (about 4000 points each, at most 1024 cells). Returns the order and the
    cells: start, count, centre and radius (sprite sizes included)."""
    pos = np.asarray(pos, np.float64)
    m = len(pos)
    target = int(min(max(m // 4000, 8), 1024))
    lo, hi = pos.min(axis=0), pos.max(axis=0)
    ext = np.maximum(hi - lo, 1e-6)
    ext_e = np.maximum(ext, ext.max() * 0.02)
    edge = (np.prod(ext_e) / target) ** (1.0 / 3.0)
    dims = np.clip(np.ceil(ext_e / edge), 1, 64).astype(np.int64)
    ijk = np.minimum(((pos - lo) / ext * dims).astype(np.int64), dims - 1)
    key = (ijk[:, 0] * dims[1] + ijk[:, 1]) * dims[2] + ijk[:, 2]
    order = np.argsort(key, kind="stable")
    ks = key[order]
    start = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]])
    count = np.diff(np.r_[start, m])
    p = pos[order]
    cen = np.add.reduceat(p, start, axis=0) / count[:, None]
    d = np.linalg.norm(p - np.repeat(cen, count, axis=0), axis=1)
    sz = np.broadcast_to(np.asarray(size, np.float64), (m,))[order]
    rad = np.maximum.reduceat(d, start) + 0.5 * np.maximum.reduceat(sz, start)
    if dome:
        cen = cen / np.maximum(np.linalg.norm(cen, axis=1, keepdims=True), 1e-9)
        rad = rad + 0.01
    return order, dict(start=start, count=count, cen=cen, rad=rad)


def _visible_runs(cells, cam, mirror, dome, stride=1):
    """Indirect draw commands (count, instances, first, base instance, 0) for the runs of cells in view, None when
    every cell is in view. The test keeps a cell whose sphere reaches the view widened to 1.6 times (the sprite
    shader's own limit), so nothing that would be drawn is lost."""
    cen, rad = cells["cen"], cells["rad"]
    if mirror:
        cen = cen * np.array([1.0, -1.0, 1.0])
        rad = rad + (0.05 if dome else 0.25 * np.abs(cells["cen"][:, 1]) + 0.5)
    r, u, f = cam.basis()
    v = cen if dome else cen - np.asarray(cam.pos, np.float64)
    z, x, y = v @ f, v @ r, v @ u
    ty = 1.6 * np.tan(np.radians(cam.fov) * 0.5)
    tx = ty * cam.aspect
    ok = ((z > -rad) & (np.abs(x) - tx * z <= rad * np.sqrt(1.0 + tx * tx))
          & (np.abs(y) - ty * z <= rad * np.sqrt(1.0 + ty * ty)))
    if ok.all():
        return None
    st, ct = cells["start"][ok], cells["count"][ok]
    if len(st) == 0:
        return []
    # join neighbouring cells into runs
    brk = np.flatnonzero(st[1:] != st[:-1] + ct[:-1]) + 1
    rs = st[np.r_[0, brk]]
    re = np.r_[(st + ct)[brk - 1], (st + ct)[-1]]
    if stride > 1:
        a = (rs + stride - 1) // stride
        b = (re - 1) // stride + 1
        keep = b > a
        rs, re = a[keep], b[keep]
    cmd = np.zeros((len(rs), 5), np.uint32)       # moderngl reads indirect records 20 bytes apart
    cmd[:, 0] = 4
    cmd[:, 1] = re - rs
    cmd[:, 3] = rs
    return cmd


class Layer:
    def __init__(self, R):
        cfg = dict(S.P3D) if isinstance(S.P3D, dict) else {}
        known = {"camera", "world", "setup", "sets", "keep", "motion_blur", "motion_samples", "bursts", "lod", "sky_res",
                 "bokeh_max", "clear"}
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
        ms = cfg.get("motion_samples", 1)
        self.samples = ms if callable(ms) else max(int(ms), 1)      # a number, or a Track (more only in the whips)
        self.bursts = [dict(b) for b in (cfg.get("bursts") or [])]
        self.clear = cfg.get("clear") or []
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
        self.scene.add("_floats", Wd.Floats(wd, **{**dict(count=n(700)), **wd.float_cfg}))
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
        self.msize = self.msize_half = (max(w // 2, 8), max(h // 2, 8))
        self._tex = tex
        # silhouettes, a scratch texture, and the silhouettes' mirror images in the lake; full size made when asked
        self.masks = {"half": (tex(self.msize), tex(self.msize), tex(self.msize))}
        (self.t_mask, self.f_mask), (self.t_mask2, self.f_mask2), (self.t_mmask, self.f_mmask) = self.masks["half"]
        self._mirror_mask = False
        # the sky, hills, lake and mist: full size, or (P3D sky_res=0.5) half size for speed on heavy scenes
        self.sky_res = float(cfg.get("sky_res", 1.0))
        bs = (w, h) if self.sky_res >= 0.999 else (max(int(w * self.sky_res), 8), max(int(h * self.sky_res), 8))
        self.t_bg, self.f_bg = tex(bs)
        self.bg_size = bs
        self.t_bg2, self.f_bg2 = tex(self.msize)        # the world behind a window (sky layer 0), in its other look
        self.t_bg3, self.f_bg3 = tex(self.msize)        # the same for sky layer 1
        self.t_paint, self.f_paint = tex((w, h))        # painted sets: premultiplied colour and coverage
        self.t_fin, self.f_fin = tex((w, h))
        qs = (max(w // 4, 8), max(h // 4, 8))
        self.t_rsrc, self.f_rsrc = tex(qs)
        self.t_rtmp, self.f_rtmp = tex(qs)
        self.t_rayA, self.f_rayA = tex(qs)
        self.t_rayB, self.f_rayB = tex(qs)
        self.f_rayA.clear(0.0, 0.0, 0.0, 1.0)
        self.f_rayB.clear(0.0, 0.0, 0.0, 1.0)
        self.slots = {}
        self.t_lake, self._lake_t, self._lake_box = None, None, None
        self._static = {}
        self._frame = None
        self._mask = None
        self._painted = False
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
        # where the camera was when the shutter opened (on this frame's side of any cut: no blur across a cut)
        prev = self.rig.state(t - self.shutter / float(S.FPS), asp, ref=t) if self.shutter > 0.0 else cam
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

    def _clear_boxes(self, t):
        """Up to two keep-clear boxes at t: (x0, y0, x1, y1) in screen fractions (y up), and (amount, soft)."""
        items = _val(self.clear, t) or []
        box, k = np.zeros((2, 4), "f4"), np.zeros(4, "f4")
        i = 0
        for it in items:
            if i >= 2:
                break
            a = float(_val(it.get("amount", 1.0), t))
            if "t0" in it:
                f = float(it.get("fade", 0.3))
                a *= _ss(it["t0"] - f, it["t0"], t) * (1.0 - _ss(it.get("t1", 1e9), it.get("t1", 1e9) + f, t))
            if a <= 0.001:
                continue
            box[i] = _val(it["box"], t)
            k[2 * i], k[2 * i + 1] = a, float(it.get("soft", 0.03))
            i += 1
        return box, k

    def _uniforms(self, t, cam, prev, w):
        r, u, f = cam.basis()
        focal = 1.0 / np.tan(np.radians(cam.fov) * 0.5)
        px = self.h / 1080.0
        cs = float(w["cloud_speed"])
        wd = self.world
        calm_a, calm_b, ncalm = wd.calm_at(t)
        lake = self._lake_field(t)
        lp, lc, nl = wd.lights_at(t)
        split, sp = wd.split_at(t, w, cam.pos)
        box, boxk = self._clear_boxes(t)
        return dict(
            uView=cam.view(), uProj=cam.proj(), uPrevVP=prev.proj() @ prev.view(), uCamPos=np.asarray(cam.pos),
            uCamR=r, uCamU=u, uCamF=f, uRes=(float(self.w), float(self.h)), uFocal=float(focal),
            uAspect=float(cam.aspect), uFocus=float(cam.focus), uAperture=float(cam.aperture),
            uNear=float(min(max(cam.near, 0.02), 1.0)),
            uT=float(t), uHillP=(float(w["hills"]), float(w["hill_height"]), max(float(w["shore"]) / SHORE, 1.0), 0.0),
            uCloudP=(float(w["clouds"]), 0.006 * cs, 0.003 * cs, 0.55), uSunDir=w["sun_dir"],
            uFogP=(float(w["haze"]) * 0.0011, float(w["mist"]) * 0.020, float(w["mist_height"]),
                   0.10 + 0.25 * float(w["haze"])),
            uLakeP=(float(w["mirror_min"]), float(w["mirror"]), float(w["ripple"]), float(w["shore"])),
            uSigMin=0.6, uCocMax=self.bokeh_max * self.h, uLodR=self.lod_r * px, uDomeDist=3000.0,
            uShutterDt=self.shutter / float(S.FPS), uMaxStreak=0.20 * self.h, uSmear=0.03, uPx=px,
            uBokeh=(float(w["bokeh_ring"]), float(w["bokeh_hex"])), uHair=0.30 * px,
            uNCalm=ncalm, uNLights=nl, uDomeRot=wd.dome_rot(w), uSplit=split, uSplitStars=float(sp.get("_stars", 1.0)),
            uSplitBias=float(sp.get("_bias", 0.0)),
            uLakeOn=1.0 if lake is not None else 0.0, uLakeF=lake if lake is not None else (0.0, 0.0, 1.0, 1.0),
            uLakeTex=LAKE_UNIT,
            _calm=(calm_a, calm_b), _lights=(lp, lc), _clear=(box, boxk), _split=sp,
        )

    def _lake_field(self, t):
        """The lake field of the frame (world key lake): sent to its texture once per frame, bound at LAKE_UNIT."""
        if self.world.lake is None:
            return None
        if self._lake_t != t:
            data, box = self.world.lake_at(t)
            n = data.shape[0]
            if self.t_lake is None or self.t_lake.size != (n, n):
                if self.t_lake is not None:
                    self.t_lake.release()
                self.t_lake = self.ctx.texture((n, n), 2, dtype="f4")
                self.t_lake.filter = (moderngl.LINEAR, moderngl.LINEAR)
                self.t_lake.repeat_x = self.t_lake.repeat_y = False
            self.t_lake.write(np.ascontiguousarray(data, "f4").tobytes())
            self._lake_t, self._lake_box = t, box
        self.t_lake.use(location=LAKE_UNIT)
        return self._lake_box

    def _arrays(self, p, U):
        seta(p, "uCalmA", U["_calm"][0])
        seta(p, "uCalmB", U["_calm"][1])
        seta(p, "uLightP", U["_lights"][0])
        seta(p, "uLightC", U["_lights"][1])
        seta(p, "uClear", U["_clear"][0])

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

    def _slot(self, key, b, static=False, dome=False):
        ctx = self.ctx
        sl = self.slots.get(key)
        if sl is None:
            sl = self.slots[key] = dict(cap=0, core=None, normal=None, seg=None, vel=None, idx=None, ind=None,
                                        vaos={}, done=False, draft_keep=True, cells=None)
        if static and sl["done"]:
            return sl
        n = b["n"]
        step = 2 if (self.draft and n > 30000 and b["pos2"] is None) else 1   # a draft draws every second point
        sel = np.arange(0, n, step) if step > 1 else None
        m = n if sel is None else len(sel)
        # a large static set is sorted into spatial cells, so a frame draws only the cells in view
        cells = order = None
        if static and b["pos2"] is None and m >= CHUNK_MIN:
            order, cells = _chunks(b["pos"] if sel is None else b["pos"][sel],
                                   b["size"] if sel is None else b["size"][sel], dome)
            sel = order if sel is None else sel[order]

        def pick(a):
            return a if sel is None else a[sel]

        core = np.empty((m, 13), np.float32)
        core[:, 0:3] = pick(b["pos"])
        core[:, 3] = pick(b["size"])
        core[:, 4:7] = pick(b["color"])
        core[:, 7] = pick(b["alpha"])
        core[:, 8] = pick(b["emit"]) * step
        core[:, 9] = pick(b["seed"])
        core[:, 10:12] = pick(b["rot"])
        core[:, 12] = -1e9 if b["birth"] is None else pick(b["birth"])
        if m > sl["cap"] or sl["core"] is None:
            sl["cap"] = int(m * 1.3) + 64
            for k in ("core", "normal", "seg", "vel", "idx"):
                if sl[k] is not None:
                    sl[k].release()
                    sl[k] = None
            for v in sl["vaos"].values():
                v.release()
            sl["vaos"] = {}
            sl["core"] = ctx.buffer(reserve=sl["cap"] * 52, dynamic=True)
        sl["core"].write(core)

        def extra(name, arr, width):
            if arr is None:
                return False
            if sl[name] is None:
                sl[name] = ctx.buffer(reserve=sl["cap"] * 4 * width, dynamic=True)
                sl["vaos"] = {}
            sl[name].write(np.ascontiguousarray(pick(arr), np.float32))
            return True

        sl["has_normal"] = extra("normal", b["normal"], 3)
        sl["has_vel"] = extra("vel", b["vel"], 3)
        if b["pos2"] is not None:
            seg = np.empty((n, 5), np.float32)
            seg[:, 0:3] = b["pos2"]
            seg[:, 3] = b["alpha2"]
            seg[:, 4] = b["size2"]
            extra("seg", seg, 5)
        if cells is not None:
            sel_keep = sel
            sel = None
            extra("idx", order.astype(np.float32), 1)      # each point keeps its own index (bokeh sharing, mirror)
            sel = sel_keep
        sl["cells"] = cells
        sl["n"] = m
        sl["done"] = True
        return sl

    def _vao(self, sl, which, stride=1):
        key = (which, sl.get("has_normal"), sl.get("has_vel"), stride, sl.get("cells") is not None)
        v = sl["vaos"].get(key)
        if v is not None:
            return v
        ctx = self.ctx
        if which == "sprite":
            pad = (lambda width: f" {width * (stride - 1)}x" if stride > 1 else "")
            content = [(self.quad, "2f", "aCorner"),
                       (sl["core"], CORE_FMT.replace(" /i", pad(52) + " /i"), "aPos", "aSize", "aColor", "aAlpha",
                        "aEmit", "aSeed", "aRot", "aBirth"),
                       ((sl["normal"], "3f" + pad(12) + " /i", "aNormal") if sl["has_normal"]
                        else (self.b_zero3, "3f /r", "aNormal")),
                       ((sl["vel"], "3f" + pad(12) + " /i", "aVel") if sl["has_vel"] else (self.b_vel0, "3f /r", "aVel"))]
            if sl.get("cells") is not None:
                content.append((sl["idx"], "1f" + pad(4) + " /i", "aIdx"))
            v = ctx.vertex_array(self.p_sprite, content)
        elif which == "seg":
            v = ctx.vertex_array(self.p_seg, [
                (self.quad, "2f", "aCorner"),
                (sl["core"], CORE_FMT, "aPos", "aSize", "aColor", "aAlpha", "aEmit", "aSeed", "aUV", "aBirth"),
                (sl["seg"], "4f 1f /i", "aPos2A2", "aSize2"),
                ((sl["vel"], "3f /i", "aVel") if sl["has_vel"] else (self.b_vel0, "3f /r", "aVel"))])
        else:
            v = ctx.vertex_array(self.p_mask, [
                (self.quad, "2f", "aCorner"),
                (sl["core"], "3f 1f 12x 1f 16x 1f /i", "aPos", "aSize", "aAlpha", "aBirth")])
        sl["vaos"][key] = v
        return v

    def _render(self, sl, vao, cam, stride=1, mirror=False, dome=False):
        """Draws a slot's sprites: all of them, or for a set in spatial cells only the cells in view (one
        indirect draw of the runs of visible cells). stride k draws every k-th point (the thin mirror)."""
        n = sl["n"]
        cells = sl.get("cells")
        if cells is None:
            vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=(n - 1) // stride + 1)
            return
        cmd = _visible_runs(cells, cam, mirror, dome, stride)
        if cmd is None:
            vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=(n - 1) // stride + 1)
            return
        if len(cmd) == 0:
            return
        data = np.ascontiguousarray(cmd, np.uint32)
        if sl["ind"] is None or sl["ind"].size < data.nbytes:
            if sl["ind"] is not None:
                sl["ind"].release()
            sl["ind"] = self.ctx.buffer(reserve=max(data.nbytes, 20 * len(cells["start"])), dynamic=True)
        sl["ind"].write(data)
        vao.render_indirect(sl["ind"], mode=moderngl.TRIANGLE_STRIP, count=len(cmd))

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
        # the two sky layers: masks with the same fill share one, a different fill takes the next free one
        layers, slot_of = [None, None], {}
        for e, batches, k in todo:
            mk = e.mask
            if mk.mode != "sky":
                continue
            key = (mk.fill_key(), e.window)        # a window inside a window never shares a layer with others
            s = mk.slot
            if s is None:
                s = next((i for i in (0, 1) if layers[i] is not None and layers[i]["key"] == key), None)
                if s is None:
                    s = next((i for i in (0, 1) if layers[i] is None), None)
            if s is None:
                if not getattr(self, "_warned_layers", False):
                    print(f"p3d: more than two different window fills at {t:.2f} s; {e.name} is left out", flush=True)
                    self._warned_layers = True
                continue
            if layers[s] is None:
                col = None
                if mk.sky == "flat":
                    c = _val(mk.color, t)
                    col = api.show(c) if isinstance(c, str) else np.asarray(c, np.float64)
                elif mk.sky == "nebula":
                    c = _val(mk.color, t) if mk.color is not None else "#ff9440"
                    col = api.lin(c) if isinstance(c, str) else np.asarray(c, np.float64)
                gl = _val(mk.glow, t) if mk.glow is not None else (-0.25, 0.30, 1.0, 0.5)
                layers[s] = dict(key=key, kind=api.MASK_SKIES.index(mk.sky), k=0.0, edge=float(mk.edge),
                                 tint=tuple(float(x) for x in np.asarray(mk.tint, np.float64)), look=mk.look,
                                 color=col, box=(0.5, 0.5, 0.4, 0.0), parent=-1, soft=0.0, pts=[],
                                 glow=tuple(float(x) for x in gl))
            layers[s]["k"] = max(layers[s]["k"], k)
            layers[s]["soft"] = max(layers[s]["soft"], float(mk.soft))
            slot_of[e.name] = s
        for e, batches, k in todo:             # a window inside a window: the layer of the set it lives in
            s = slot_of.get(e.name)
            if s is None or not e.window:
                continue
            par = slot_of.get(e.window) if isinstance(e.window, str) else next(
                (i for i in (0, 1) if layers[i] is not None and i != s), None)
            if par is not None and par != s:
                layers[s]["parent"] = par
        dark_soft = max([float(e.mask.soft) for e, _, _ in todo if e.mask.mode == "dark"] or [0.0])
        softs = [dark_soft] + [ly["soft"] if ly else 0.0 for ly in layers]
        used = [s for s, on in zip(softs, [any(e.mask.mode == "dark" for e, _, _ in todo)] +
                                   [ly is not None for ly in layers]) if on]
        full = bool(used) and min(used) < 2.5            # crisp silhouettes: draw them at full size this frame
        self._use_mask("full" if full else "half")
        ctx = self.ctx
        self.f_mask.use()
        self.f_mask.clear(0.0, 0.0, 0.0, 60000.0)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        ctx.blend_equation = (moderngl.FUNC_ADD, moderngl.MIN)
        p = self.p_mask
        setu(p, uView=U["uView"], uProj=U["uProj"], uFocal=U["uFocal"], uNear=U["uNear"], uT=U["uT"],
             uRes=(float(self.msize[0]), float(self.msize[1])))
        st = dict(dark=0.0, layers=layers, slot_of=slot_of, full=full)
        w = self.world.now
        mirror = float(w["mirror"]) > 0.001 and cam.pos[1] > 0.0
        srcs = []
        for e, batches, k in todo:
            mk = e.mask
            if mk.mode == "sky" and e.name not in slot_of:
                continue
            if mk.source is not None:
                src = api.Entry(e.name + "#mask", mk.source)
                srcs.append((e, self._batches(src, t, cam), k, src.name))
            else:
                srcs.append((e, batches, k, e.name))
        try:
            for e, batches, k, name in srcs:
                mk = e.mask
                sky = mk.mode == "sky"
                for bi, b in enumerate(batches):
                    if b["kind"] in api.SEGMENT_KINDS:
                        continue
                    sl = self._slot((name, bi), b, static=getattr(e.pointset, "static", False) and mk.source is None)
                    setu(p, uGrow=float(mk.grow), uSel=(1 + slot_of[e.name]) if sky else 0, uMirrorM=0.0)
                    self._vao(sl, "mask").render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
                    if sky:
                        layers[slot_of[e.name]]["pts"].append(b["pos"][:: max(b["n"] // 400, 1)])
                if not sky:
                    st["dark"] = max(st["dark"], k)
            # the silhouettes' images in the lake (the same shapes upside down below the water)
            self._mirror_mask = mirror and any(e.reflect for e, _, _, _ in srcs)
            if self._mirror_mask:
                self.f_mmask.use()
                self.f_mmask.clear(0.0, 0.0, 0.0, 60000.0)
                for e, batches, k, name in srcs:
                    if not e.reflect:
                        continue
                    mk = e.mask
                    sky = mk.mode == "sky"
                    for bi, b in enumerate(batches):
                        if b["kind"] in api.SEGMENT_KINDS or not b["reflect"]:
                            continue
                        sl = self._slot((name, bi), b, static=getattr(e.pointset, "static", False) and mk.source is None)
                        setu(p, uGrow=float(mk.grow), uSel=(1 + slot_of[e.name]) if sky else 0, uMirrorM=1.0)
                        self._vao(sl, "mask").render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
        finally:
            ctx.blend_equation = moderngl.FUNC_ADD
            ctx.disable(moderngl.BLEND)
        for ly in layers:
            if ly is None or not ly["pts"]:
                continue
            xy, z = cam.project(np.concatenate(ly.pop("pts")))
            ok = z > 0.1
            if np.any(ok):
                lo, hi = xy[ok].min(axis=0), xy[ok].max(axis=0)
                ly["box"] = (float((lo[0] + hi[0]) * 0.5), float((lo[1] + hi[1]) * 0.5),
                             float(max((hi[1] - lo[1]) * 0.5, 0.05)), 0.0)
        # soften each channel by its own softness (pixels of a 1080p picture)
        k = (self.h / 1080.0) * (self.msize[1] / float(self.h)) / 3.2
        rad = tuple(float(s) * k for s in softs)
        pairs = [(self.t_mask, self.f_mask)] + ([(self.t_mmask, self.f_mmask)] if self._mirror_mask else [])
        for tm, fm in pairs:
            self.f_mask2.use()
            tm.use(location=0)
            setu(self.p_mblur, uTex=0, uDir=(1.0 / self.msize[0], 0.0), uRad=rad)
            self.v_mblur.render(moderngl.TRIANGLE_STRIP)
            fm.use()
            self.t_mask2.use(location=0)
            setu(self.p_mblur, uTex=0, uDir=(0.0, 1.0 / self.msize[1]), uRad=rad)
            self.v_mblur.render(moderngl.TRIANGLE_STRIP)
        return st

    def _use_mask(self, which):
        """Switches the silhouette textures between half size (soft edges, the default) and full size."""
        if which not in self.masks:
            size = (self.w, self.h)
            self.masks[which] = (self._tex(size), self._tex(size), self._tex(size))
        (self.t_mask, self.f_mask), (self.t_mask2, self.f_mask2), (self.t_mmask, self.f_mmask) = self.masks[which]
        self.msize = self.t_mask.size

    # ------------------------------------------------------------------ the light pass
    def draw(self, t, P):
        ctx, R = self.ctx, self.R
        cam, prev, w = self.state(t)
        U = self._uniforms(t, cam, prev, w)
        items = [(e, self._batches(e, t, cam)) for e in self.scene.entries()]
        self._mask = self._mask_pass(items, t, cam, U)
        # painted sets: their true colour, laid over the scene by the background pass
        self._painted = any(b["paint"] > 0.0 and b["gain"] > 0.0005 for _, bs in items for b in bs)
        if self._painted:
            self.f_paint.use()
            self.f_paint.clear(0.0, 0.0, 0.0, 0.0)
            self._draw_sets(items, U, cam, w, 1.0, paint=True)
        n = max(int(round(float(_val(self.samples, t)))), 1) if self.shutter > 0.0 else 1
        if n <= 1:
            self._draw_sets(items, U, cam, w, 1.0)
        else:
            # motion blur by time sampling: the sets at n moments inside the shutter, each a share of the light
            # (and each still drawn out along its own short path, so the moments join into one streak)
            dt = self.shutter / float(S.FPS)
            asp = float(S.ASPECT)
            for i in range(n):
                ts = t - dt * (n - 1 - i) / n
                c, pv = self.rig.state(ts, asp, ref=t), self.rig.state(ts - dt / n, asp, ref=t)
                Ui = self._uniforms(ts, c, pv, w)
                Ui["uShutterDt"] = dt / n
                its = items if i == n - 1 else [(e, self._batches(e, ts, c)) for e in self.scene.entries()]
                self._draw_sets(its, Ui, c, w, 1.0 / n)
        R.f_L.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)

    def _draw_sets(self, items, U, cam, w, share, paint=False):
        ctx, R = self.ctx, self.R
        if not paint:
            R.f_L.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA) if paint else (moderngl.ONE, moderngl.ONE)
        mask_on = 0.0
        if self._mask is not None:
            self.t_mask.use(location=0)
            mask_on = 1.0
            if self._mirror_mask:
                self.t_mmask.use(location=1)
        blur = 1.0 if self.shutter > 0.0 else 0.0
        mirror = float(w["mirror"]) > 0.001 and cam.pos[1] > 0.0
        Uv = {k: v for k, v in U.items() if not k.startswith("_")}
        mk = self._mask
        if mk is not None:
            ly = mk["layers"]
            hide = (mk["dark"], ly[0]["k"] if ly[0] else 0.0, ly[1]["k"] if ly[1] else 0.0)
        else:
            hide = (0.0, 0.0, 0.0)
        for p in (self.p_sprite, self.p_seg):
            setu(p, uMaskTex=0, uMaskTexM=1, uMaskOn=mask_on, uPaint=1.0 if paint else 0.0, uMaskK=hide, uMaskBias=0.05,
                 **Uv)
            self._arrays(p, U)
        boxk = U["_clear"][1]
        for e, batches in items:
            win = self._win(e)
            for bi, b in enumerate(batches):
                self._draw_batch(e, bi, b, cam, share, paint, blur, mirror, mask_on, boxk, win)
        # the stars of a world seen through a window (its own look's stars, inside the window only)
        if mk is not None and not paint:
            stars = next(((e, bs) for e, bs in items if e.name == "_stars"), None)
            for s, ly in enumerate(mk["layers"]):
                if stars is None or ly is None or ly["kind"] != 4:
                    continue
                amt = float(self.world.state_of(ly["look"], float(U["uT"]))["stars"])
                if amt <= 0.001:
                    continue
                win = self._win(None, slot=s)
                for bi, b in enumerate(stars[1]):
                    bb = dict(b, gain=amt)
                    self._draw_batch(stars[0], bi, bb, cam, share, False, blur, False, mask_on, boxk, win)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)

    def _win(self, e, slot=None):
        """How a set sits in the windows: (window on, its layer, that layer's parent, layers inside it) as the
        shader's channel selectors."""
        z = (0.0, 0.0, 0.0)
        if slot is None:
            if e is None or not e.window:
                return 0.0, z, z, z
            mk = self._mask
            if mk is None:
                return 1.0, z, z, z
            if isinstance(e.window, str):
                slot = mk["slot_of"].get(e.window)
            else:
                slot = next((i for i in (0, 1) if mk["layers"][i] is not None), None)
            if slot is None:
                return 1.0, z, z, z
        layers = self._mask["layers"]

        def unit(i):
            v = [0.0, 0.0, 0.0]
            if i is not None and i >= 0:
                v[1 + i] = 1.0
            return tuple(v)
        par = layers[slot]["parent"] if layers[slot] else -1
        child = [0.0, 0.0, 0.0]
        for i, ly in enumerate(layers):
            if ly is not None and ly["parent"] == slot:
                child[1 + i] = 1.0
        return 1.0, unit(slot), unit(par), tuple(child)

    def _draw_batch(self, e, bi, b, cam, share, paint, blur, mirror, mask_on, boxk, win):
        ps = e.pointset
        dome = 1.0 if getattr(ps, "dome", False) else 0.0
        static = getattr(ps, "static", False)
        if b["gain"] <= 0.0005:
            return
        if paint:
            if b["paint"] <= 0.0:
                return
            gain = float(b["gain"]) * b["paint"]
        else:
            gain = float(b["gain"]) * share * (1.0 - b["paint"] * (1.0 - b["paint_light"]))
            if gain <= 0.0:
                return
        seg = b["kind"] in api.SEGMENT_KINDS
        sl = self._slot((e.name, bi), b, static=static, dome=bool(dome))
        p = self.p_seg if seg else self.p_sprite
        chunked = 1.0 if sl.get("cells") is not None else 0.0
        setu(p, uKind=KIND_ID[b["kind"]], uGain=gain, uTwinkle=b["twinkle"], uRim=b["rim"], uIdxK=(chunked, 1.0),
             uDofAmt=b["dof"] if e.depth_of_field else 0.0, uFogAmt=b["fog"] if e.fog else 0.0,
             uBack=b["backlight"], uLod=1.0 if (b["lod"] and e.lod) else 0.0, uDome=dome,
             uTurn=1.0 if getattr(ps, "turns", False) else 0.0, uBlur=blur * b["streak"], uMirror=0.0,
             uBirth=(b["fade"], b["flash"]), uPulse=b["pulse"], uLit=b["lit"],
             uHasN=1.0 if sl.get("has_normal") else 0.0, uWindow=win[0], uWinSel=win[1], uWinPar=win[2],
             uWinChild=win[3], uClearK=tuple(float(x) for x in boxk) if b["clear"] else (0.0, 0.0, 0.0, 0.0))
        vao = self._vao(sl, "seg" if seg else "sprite")
        if seg:
            vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
        else:
            self._render(sl, vao, cam, dome=bool(dome))
        mm = 1.0 if (self._mask is not None and self._mirror_mask) else 0.0
        if mirror and e.reflect and b["reflect"] and (not e.window or mm > 0.0):
            k = 1 if seg else _thin(sl["n"])
            setu(p, uMirror=1.0, uMaskOn=mm, uWindow=win[0] if mm > 0.0 else 0.0, uGain=gain * k,
                 uIdxK=(chunked, float(k)))
            if seg:
                vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=sl["n"])
            else:
                self._render(sl, self._vao(sl, "sprite", stride=k), cam, stride=k, mirror=True, dome=bool(dome))
            setu(p, uMaskOn=mask_on)

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
                q, z = cam.project(np.asarray(_val(b["at"], t), np.float64))
                if z[0] > 0.05:
                    xy = (float(q[0, 0]), float(q[0, 1]))
            col = _col(b.get("color", "#fff3d6"), t)
            out.append(((xy[0], xy[1], float(b.get("radius", 0.35)), k), tuple(float(x) for x in col)))
        return out[:4]

    def _rays(self, U, mode, center, mask_on, light=None, light_col=(0, 0, 0), add=False):
        """Source and two radial blurs at quarter size; the result is left in t_rayA (sun) or t_rayB (lights;
        add=True adds this light's rays to those already there)."""
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
        if add:
            self.ctx.enable(moderngl.BLEND)
            self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self.v_rad.render(moderngl.TRIANGLE_STRIP)
        if add:
            self.ctx.disable(moderngl.BLEND)

    def _sky(self, fbo, size, w, U, t, split=None):
        """Sky, hills, lake, mist, shafts and the glow of the moving lights for the world state w."""
        fbo.use()
        p = self.p_bg
        sh_a = np.zeros((4, 4), "f4")
        sh_b = np.zeros((4, 4), "f4")
        ns = 0
        for sh in self.world.shafts[:4]:
            k = float(_val(sh.get("strength", 1.0), t))
            if k <= 0.001:
                continue
            base = _val(sh.get("base", (0.0, 0.0)), t)
            col = _col(sh.get("color", "#cfe0ff"), t)
            sh_a[ns] = (base[0], base[1], float(_val(sh.get("radius", 1.5), t)), float(sh.get("top", 40.0)))
            sh_b[ns] = (col[0] * k, col[1] * k, col[2] * k, float(sh.get("spread", 0.0)))
            ns += 1
        seta(p, "uShA", sh_a)
        seta(p, "uShB", sh_b)
        self._arrays(p, U)
        cosr = float(np.cos(np.radians(w["sun_size"])))
        sp = split if split is not None else {}
        Uv = {k: v for k, v in U.items() if not k.startswith("_")}
        Uv.update(uRes=(float(size[0]), float(size[1])), uSunDir=w["sun_dir"],
                  uHillP=(float(w["hills"]), float(w["hill_height"]), max(float(w["shore"]) / SHORE, 1.0), 0.0),
                  uCloudP=(float(w["clouds"]), 0.006 * float(w["cloud_speed"]), 0.003 * float(w["cloud_speed"]), 0.55),
                  uLakeP=(float(w["mirror_min"]), float(w["mirror"]), float(w["ripple"]), float(w["shore"])))
        if split is None:
            Uv["uSplit"] = (0.0, 1.0, 0.3, 0.0)
        # the other look's own sun, water and hills (the split side)
        sb = sp if sp else w
        cosb = float(np.cos(np.radians(sb["sun_size"])))
        setu(p, uSunDirB=np.asarray(sb["sun_dir"]), uSunColB=np.asarray(sb["sun_color"]),
             uWaterB=np.asarray(sb["water"]), uHillColB=np.asarray(sb["hill_color"]),
             uSunPB=(float(sb["sun_int"]), cosb, float(sb["sun_disc"]) * _ss(-1.5, 0.5, float(sb["sun_el"])),
                     float(sb["sun_glow"])))
        hz = float(w["haze"]) * 0.0011
        setu(p, uNShaft=ns, uSkyTop=np.asarray(w["sky_top"]), uSkyMid=np.asarray(w["sky_mid"]),
             uSkyHor=np.asarray(w["sky_hor"]), uSunCol=np.asarray(w["sun_color"]),
             uHazeCol=np.asarray(w["haze_color"]), uHillCol=np.asarray(w["hill_color"]),
             uWater=np.asarray(w["water"]), uMilkyN=self.world.dome_rot(w) @ Wd.MILKY_N,
             uMistCol=np.asarray(w["mist_color"]),
             uSkyTopB=np.asarray(sp.get("sky_top", w["sky_top"])), uSkyMidB=np.asarray(sp.get("sky_mid", w["sky_mid"])),
             uSkyHorB=np.asarray(sp.get("sky_hor", w["sky_hor"])),
             uHazeColB=np.asarray(sp.get("haze_color", w["haze_color"])),
             uSunP=(float(w["sun_int"]), cosr, float(w["sun_disc"]) * _ss(-1.5, 0.5, float(w["sun_el"])),
                    float(w["sun_glow"])),
             uAirP=(hz, float(w["mist"]) * 0.020, float(w["mist_height"]), float(w["milky"]) * float(w["stars"])), **Uv)
        self.v_bg.render(moderngl.TRIANGLE_STRIP)

    def background(self, t, P):
        ctx, R = self.ctx, self.R
        cam, prev, w = self.state(t)
        U = self._uniforms(t, cam, prev, w)
        ctx.disable(moderngl.BLEND)
        # 1. sky, hills, lake, mist, shafts (and, behind a window, the same world in its other look)
        self._sky(self.f_bg, self.bg_size, w, U, t, split=U["_split"])
        mk = self._mask
        if mk is not None:
            for ly, fb in zip(mk["layers"], (self.f_bg2, self.f_bg3)):
                if ly is not None and ly["kind"] == 4 and ly["k"] > 0.0:
                    self._sky(fb, self.msize_half, self.world.state_of(ly["look"], t), U, t)

        # 2. rays (quarter size)
        mask_on = 1.0 if mk is not None else 0.0
        fwd = cam.basis()[2]
        ray_sun = float(w["rays"]) * _ss(0.05, 0.40, float(np.dot(fwd, w["sun_dir"]))) * _ss(-4.0, 0.5, float(w["sun_el"]))
        if ray_sun > 0.002 and float(w["sun_int"]) > 0.002:
            q, z = cam.project(np.asarray(cam.pos) + w["sun_dir"] * 1000.0)
            self._rays(U, 0, (float(q[0, 0]), float(q[0, 1])), mask_on)
        else:
            ray_sun = 0.0
        # rays round the world's light (light=) and round each moving light that asks for them (lights=[...,
        # rays=...]): each is cut by the silhouettes in front of it; they add up
        ray_light = 0.0
        srcs = []
        lt = self.world.light
        if lt:
            srcs.append((_val(lt["pos"], t), _col(lt.get("color", "#fff0cc"), t),
                         float(_val(lt.get("strength", 1.0), t)) * float(lt.get("rays", 1.0)), float(lt.get("size", 0.6))))
        for it in self.world.lights:
            r = float(_val(it.get("rays", 0.0), t))
            if r > 0.0:
                srcs.append((_val(it["pos"], t), _col(it.get("color", "#ffffff"), t),
                             float(_val(it.get("strength", 1.0), t)) * r, float(_val(it.get("size", 0.6), t))))
        for pos, col, k, size in srcs:
            q, z = cam.project(np.asarray(pos, np.float64))
            if k > 0.002 and z[0] > 0.1:
                rad = max(size * 0.5 * U["uFocal"] / z[0], 0.01)
                self._rays(U, 1, (float(q[0, 0]), float(q[0, 1])), mask_on,
                           light=(float(q[0, 0]), float(q[0, 1]), rad, float(z[0])),
                           light_col=np.asarray(col, np.float64) * k, add=ray_light > 0.0)
                ray_light = 1.0

        # 3. resolve: motion blur, dark bodies, windows, paint, rays, bursts
        self.f_fin.use()
        p = self.p_res
        self.t_bg.use(location=0)
        self.t_rayA.use(location=1)
        self.t_rayB.use(location=2)
        self.t_mask.use(location=3)
        self.t_paint.use(location=4)
        self.t_bg2.use(location=5)
        self.t_bg3.use(location=6)
        mm = mk is not None and self._mirror_mask
        if mm:
            self.t_mmask.use(location=7)
        fa, fbox, ftint, fcol, fglow = (np.zeros((2, 4), "f4") for _ in range(5))
        if mk is not None:
            for i, ly in enumerate(mk["layers"]):
                if ly is None:
                    continue
                fa[i] = (ly["kind"], ly["k"], ly["edge"], ly["parent"] + 1)
                fbox[i] = ly["box"]
                ftint[i, :3] = ly["tint"]
                if ly["color"] is not None:
                    fcol[i, :3] = ly["color"]
                fglow[i] = ly.get("glow", (0.0, 0.0, 0.0, 0.0))
        for name, arr in (("uFillA", fa), ("uFillBox", fbox), ("uFillTint", ftint), ("uFillCol", fcol),
                          ("uFillL", fglow)):
            seta(p, name, arr)
        bursts = self._burst_state(t, cam)
        ba = np.zeros((4, 4), "f4")
        bc = np.zeros((4, 3), "f4")
        for i, (a, c) in enumerate(bursts):
            ba[i], bc[i] = a, c
        seta(p, "uBurst", ba)
        seta(p, "uBurstCol", bc)
        moving = self.shutter > 0.0 and (not np.allclose(cam.pos, prev.pos, atol=1e-5)
                                         or not np.allclose(cam.target, prev.target, atol=1e-5))
        setu(p, uMaskM=7, uMirrorK=0.85 * min(float(w["mirror"]), 1.0) if mm else 0.0)
        setu(p, uBg=0, uRayA=1, uRayB=2, uMask=3, uPaintT=4, uBg2=5, uBg3=6, uPaintOn=1.0 if self._painted else 0.0,
             uCamR=U["uCamR"], uCamU=U["uCamU"], uCamF=U["uCamF"],
             uCamPos=U["uCamPos"], uPrevVP=U["uPrevVP"], uFocal=U["uFocal"], uAspect=U["uAspect"], uT=float(t),
             uBlur=1.0 if moving else 0.0, uShore=float(w["shore"]) if float(w["hills"]) > 0.001 else 1e9, uRes=U["uRes"],
             uRayK=(ray_sun * 0.55, ray_light, 0.0, 0.0),
             uMaskOn=mask_on, uDarkK=mk["dark"] if mk else 0.0, uDarkTint=tuple(float(x) for x in np.asarray(w["sky_top"]) * 0.35), uNBurst=len(bursts))
        self.v_res.render(moderngl.TRIANGLE_STRIP)
        self.t_fin.use(location=CAM_UNIT)
        setu(R.p_comp, uCamOn=1.0, uCamBg=CAM_UNIT, uHueKeep=float(min(max(w["keep_hue"], 0.0), 1.0)))
