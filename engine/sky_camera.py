"""Sky and camera layers (2026-11-15, engine helper S). Everything here is optional: a song that sets none of
these keys renders exactly as before. How a song uses them: engine/UPGRADE-HOWTO.md, section I7.

  TIME_OF_DAY   a Track: 0 night, 0.5 dawn, 1 day, 1.5 dusk, 2 night again. Sky colours, sun height and
                strength, the colour of the light, stars
  CLOUDS3D      soft layered clouds in perspective that drift and change shape, lit from the sun side, with
                silver linings when the sun is low (CLOUDS_SPEED, CLOUDS_LIGHT)
  GOD_RAYS      shafts of light from the sun (or RAYS_FROM, a point in the sky) through the moving clouds and
                past the mountains: screen space radial light scattering (RAYS_COLOR, RAYS_DECAY)
  CAMERA_ZOOM, CAMERA_PAN, CAMERA_CRANE, PARALLAX   slow camera moves; the sky, the clouds, three mountain
                ranges, the lake and near motes (CAMERA_MOTES) each move at their own depth. Text, the arch of
                lights and the people of light are not moved.

render.py calls, in frame order: adjust (after params), draw_clouds (after the sky pass), draw_light (after the
effect layers, before text protection: the rays are dimmed behind words like every other light) and
camera_bg (after the glow blur, before the composite).
"""
import numpy as np
import moderngl

import song as S
import shaders as G
import sky_camera_shaders as K

W_SKY, W_FAR = 0.12, 0.45
CAM_UNIT = 15        # texture unit of the camera background in the composite
CALM_Y = 0.335

# time of day keys: top, middle, horizon, glow, sun height above the horizon, sun strength, sun size, stars
TOD = [
    (0.00, "#02030b", "#070c26", "#161f4a", "#8ea4ff", -0.12, 0.10, 0.10, 1.00),
    (0.30, "#080d2c", "#33265c", "#a85f6e", "#ffb48c", -0.035, 0.45, 0.105, 0.65),
    (0.50, "#0f1b46", "#553b7c", "#e9836f", "#ffd08c", 0.015, 0.95, 0.115, 0.32),
    (0.70, "#152b68", "#93578a", "#ffb873", "#ffecc4", 0.10, 1.20, 0.130, 0.12),
    (1.00, "#1c3a7c", "#5e78b0", "#c9d2e2", "#fff2d8", 0.36, 1.05, 0.135, 0.0),
    (1.25, "#173a7a", "#7a6a9c", "#f2b27a", "#ffd9a0", 0.12, 1.15, 0.130, 0.05),
    (1.50, "#0d1440", "#4a2f6e", "#e0725e", "#ffb27a", 0.010, 0.90, 0.120, 0.20),
    (1.75, "#050820", "#221a48", "#6e4263", "#ffa58c", -0.06, 0.32, 0.105, 0.60),
    (2.00, "#02030b", "#070c26", "#161f4a", "#8ea4ff", -0.12, 0.10, 0.10, 1.00),
]
_TOD_T = np.array([k[0] for k in TOD])
_TOD_V = np.array([np.concatenate([S.lin(k[1]), S.lin(k[2]), S.lin(k[3]), S.lin(k[4]), k[5:]]) for k in TOD])


def val(name, t, default=None):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def col(c, default):
    c = c if c is not None else default
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def ss(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


def tod_state(v):
    """The sky at time of day v (0..2), eased between the keys."""
    v = min(max(float(v), 0.0), 2.0)
    i = min(int(np.searchsorted(_TOD_T, v, side="right")) - 1, len(TOD) - 2)
    u = (v - _TOD_T[i]) / (_TOD_T[i + 1] - _TOD_T[i])
    u = u * u * (3 - 2 * u)
    x = _TOD_V[i] * (1 - u) + _TOD_V[i + 1] * u
    return dict(top=x[0:3], mid=x[3:6], hor=x[6:9], glow=x[9:12], sun_dy=x[12], sun_int=x[13], sun_size=x[14],
                stars=x[15])


def setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v


class SkyCamera:
    def __init__(self, R):
        has = lambda k: getattr(S, k, None) is not None  # noqa: E731
        self.has_tod = has("TIME_OF_DAY")
        self.has_clouds = has("CLOUDS3D")
        self.has_rays = has("GOD_RAYS")
        self.has_cam = any(has(k) for k in ("CAMERA_ZOOM", "CAMERA_PAN", "CAMERA_CRANE"))
        self.has_motes = has("CAMERA_MOTES")
        self.on = self.has_tod or self.has_clouds or self.has_rays or self.has_cam or self.has_motes
        if not self.on:
            return
        self.R = R
        ctx = self.ctx = R.ctx
        w, h = R.w, R.h
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def prog(fs, vs=G.QUAD_VS):
            p = ctx.program(vertex_shader=vs, fragment_shader=fs)
            setu(p, uFlip=1.0)
            return p, ctx.vertex_array(p, [(quad, "2f", "aPos")]) if vs is G.QUAD_VS else None

        def tex(size, comps=4):
            t = ctx.texture(size, comps, dtype="f2")
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t

        if self.has_clouds or self.has_rays:
            self.p_cl, self.v_cl = prog(K.CLOUDS_FS)
            self.p_blit, self.v_blit = prog(K.BLIT_FS)
            hs = (max(w // 2, 8), max(h // 2, 8))
            self.t_cl, self.t_cd = tex(hs), tex(hs)
            self.f_cl = ctx.framebuffer([self.t_cl, self.t_cd])
        if self.has_rays:
            self.p_occ, self.v_occ = prog(K.OCC_FS)
            self.p_rad, self.v_rad = prog(K.RADIAL_FS)
            self.p_rays, self.v_rays = prog(K.RAYS_FS)
            qs = (max(w // 4, 8), max(h // 4, 8))
            self.t_occ, self.t_ray = tex(qs), tex(qs)
            self.f_occ, self.f_ray = ctx.framebuffer([self.t_occ]), ctx.framebuffer([self.t_ray])
        if self.has_cam:
            self.p_bg, self.v_bg = prog(K.CAMBG_FS)
            self.t_cam = tex((w, h))
            self.f_cam = ctx.framebuffer([self.t_cam])
        if self.has_motes:
            self.p_nm = ctx.program(vertex_shader=K.NMOTE_VS, fragment_shader=K.NMOTE_FS)
            sd = np.random.default_rng(23).random((160, 4)).astype("f4")
            self.v_nm = ctx.vertex_array(self.p_nm, [(ctx.buffer(sd.tobytes()), "4f", "aSeed")])

    # ------------------------------------------------------------ camera
    def cam(self, t, P):
        """(zoom, pan, crane, parallax), centre and the song's own base zoom."""
        z = float(val("CAMERA_ZOOM", t, 1.0))
        pan = float(val("CAMERA_PAN", t, 0.0))
        cr = float(val("CAMERA_CRANE", t, 0.0))
        par = float(val("PARALLAX", t, 1.0)) if self.has_cam else 1.0
        c = val("CAMERA_CENTER", t, (0.5, S.HORIZON + 0.12))
        return (z, pan, cr, par), (float(c[0]), float(c[1])), float(P.get("zoom", 1.0))

    def to_screen(self, q, w, t, P):
        """Where a point of a layer at depth w (layer coordinates) is on screen now."""
        (z, pan, cr, par), c, bz = self.cam(t, P)
        k = 1.0 + (w - 1.0) * par
        zz = max(1.0 + (z - 1.0) * k, 0.2)
        ux = c[0] + (q[0] - c[0] - pan * k) * zz
        uy = c[1] + (q[1] - c[1] - cr * k) * zz
        return (ux - 0.5) / bz + 0.5, (uy - S.HORIZON) / bz + S.HORIZON

    def _cam_uniforms(self, p, t, P):
        cam, c, bz = self.cam(t, P)
        setu(p, uCam=cam, uCamC=c, uBaseZ=bz, uHorizon=float(S.HORIZON), uAspect=float(S.ASPECT))

    def _text_uniforms(self, p, t, units=(0, 1, 2)):
        R = self.R
        (texA, txA, bndA, shA, offA), (texB, txB, bndB, shB, offB) = R.text_plan(t)
        credit, c0 = S.credit_state(t, R.credit_bbox)
        texA.use(location=units[0]); texB.use(location=units[1]); R.t_credit.use(location=units[2])
        setu(p, uTextA=units[0], uTextB=units[1], uTextC=units[2], uShade=(float(shA), float(shB)),
             uTxA=tuple(float(v) for v in txA), uTxB=tuple(float(v) for v in txB), uBndA=tuple(float(v) for v in bndA),
             uBndB=tuple(float(v) for v in bndB), uOffA=tuple(float(v) for v in offA),
             uOffB=tuple(float(v) for v in offB), uCredit=tuple(float(v) for v in credit),
             uC0=tuple(float(v) for v in c0))

    def sun_screen(self, t, P):
        return self.to_screen((0.5, float(P["sun_y"])), W_SKY, t, P)

    # ------------------------------------------------------------ 1. time of day, lantern
    def adjust(self, t, P):
        if not self.on:
            return
        if self.has_tod:
            s = tod_state(val("TIME_OF_DAY", t, 1.0))
            P["sky_top"], P["sky_mid"], P["sky_hor"], P["glow"] = s["top"], s["mid"], s["hor"], s["glow"]
            P["sun_y"] = S.HORIZON + float(s["sun_dy"])
            P["sun_int"] = float(s["sun_int"]) * (0.88 + 0.30 * float(P.get("env_slow", 0.4)))
            P["sun_size"] = float(s["sun_size"])
            P["stars"] = float(s["stars"])
            P["milky"] = float(P.get("milky", 0.0)) * float(s["stars"])
        if self.has_clouds:
            P["clouds"] = float(P.get("clouds", 0.0)) * (1.0 - 0.85 * min(float(val("CLOUDS3D", t, 0.0)), 1.0))
        if self.has_cam and "lantern" in P:
            # the light on the skyline rides the far range
            lx, ly = P["lantern"]
            bz = float(P.get("zoom", 1.0))
            q = ((lx - 0.5) * bz + 0.5, (ly - S.HORIZON) * bz + S.HORIZON)
            P["lantern"] = self.to_screen(q, W_FAR, t, P)

    # ------------------------------------------------------------ 2. clouds (over the sky texture)
    def draw_clouds(self, t, P):
        if not (self.has_clouds or self.has_rays):
            return
        amt = float(val("CLOUDS3D", t, 0.0) or 0.0)
        self.cloud_amt = amt
        if amt <= 0.001:
            return
        ctx = self.ctx
        ctx.disable(moderngl.BLEND)
        self.f_cl.use()
        p = self.p_cl
        self._cam_uniforms(p, t, P)
        self._text_uniforms(p, t)
        sun_dy = float(P["sun_y"]) - S.HORIZON
        silver = (0.25 + 0.75 * (1.0 - ss(0.08, 0.30, sun_dy))) * ss(-0.08, 0.0, sun_dy)
        setu(p, uT=float(t), uCloudSpd=float(val("CLOUDS_SPEED", t, 1.0)), uCloudAmt=amt,
             uSkyTop=P["sky_top"], uSkyMid=P["sky_mid"], uSkyHor=P["sky_hor"], uGlow=P["glow"],
             uSunS=self.sun_screen(t, P), uSunInt=float(P["sun_int"]), uLight=float(val("CLOUDS_LIGHT", t, 1.0)),
             uSilver=float(silver))
        self.v_cl.render(moderngl.TRIANGLE_STRIP)
        self.R.f_sky.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
        self.t_cl.use(location=0)
        setu(self.p_blit, uTex=0)
        self.v_blit.render(moderngl.TRIANGLE_STRIP)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        ctx.disable(moderngl.BLEND)

    # ------------------------------------------------------------ 3. god rays and near motes (into the light layer)
    def draw_light(self, t, P):
        if not self.on:
            return
        ctx, R = self.ctx, self.R
        calm = float(val("BOTTOM_CALM", t, 0.0) or 0.0)
        drew = False
        a = float(val("GOD_RAYS", t, 0.0) or 0.0) if self.has_rays else 0.0
        if a > 0.001:
            src = val("RAYS_FROM", t, "sun")
            if isinstance(src, str):
                sx, sy = self.sun_screen(t, P)
                size = float(P["sun_size"]) * 0.75
                gain = min(float(P["sun_int"]), 1.4)
            else:
                sx, sy = self.to_screen((float(src[0]), float(src[1])), W_SKY, t, P)
                size, gain = 0.06, 1.0
            ctx.disable(moderngl.BLEND)
            self.f_occ.use()
            self._cam_uniforms(self.p_occ, t, P)
            R.t_ridge.use(location=0)
            cl_on = 1.0 if (self.has_clouds and getattr(self, "cloud_amt", 0.0) > 0.001) else 0.0
            if cl_on:
                self.t_cd.use(location=1)
            setu(self.p_occ, uRidge=0, uCloudD=1, uCloudOn=cl_on, uSrc=(sx, sy), uSrcSize=size)
            self.v_occ.render(moderngl.TRIANGLE_STRIP)
            self.f_ray.use()
            self.t_occ.use(location=0)
            setu(self.p_rad, uOcc=0, uSrc=(sx, sy), uDecay=float(min(max(val("RAYS_DECAY", t, 0.965), 0.5), 0.995)),
                 uAspect=float(S.ASPECT))
            self.v_rad.render(moderngl.TRIANGLE_STRIP)
            rc = val("RAYS_COLOR", t, None)
            c = col(rc, "#ffffff") if rc is not None else np.asarray(P["glow"]) * 0.75 + S.lin("#fff1dc") * 0.25
            R.f_L.use()
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = (moderngl.ONE, moderngl.ONE)
            self.t_ray.use(location=0)
            setu(self.p_rays, uRays=0, uCol=c, uAmt=a * gain * 2.2, uHorizon=float(self.to_screen((0.5, S.HORIZON), 0.80, t, P)[1]), uCalm=calm,
                 uCalmY=CALM_Y)
            self.v_rays.render(moderngl.TRIANGLE_STRIP)
            drew = True
        m = float(val("CAMERA_MOTES", t, 0.0) or 0.0) if self.has_motes else 0.0
        if m > 0.001:
            if not drew:
                R.f_L.use()
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = (moderngl.ONE, moderngl.ONE)
            self._cam_uniforms(self.p_nm, t, P)
            mc = val("MOTE_COLORS", t, None)
            setu(self.p_nm, uT=float(t), uAmt=m, uPx=R.px, uCalm=calm, uCalmY=CALM_Y,
                 uCol=col(mc[0] if mc else None, "#ffe2a8"))
            self.v_nm.render(moderngl.POINTS)
        R.f_L.use()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)

    # ------------------------------------------------------------ 4. the camera background
    def camera_bg(self, t, P):
        if not self.has_cam:
            return
        ctx, R = self.ctx, self.R
        ctx.disable(moderngl.BLEND)
        self.f_cam.use()
        p = self.p_bg
        self._cam_uniforms(p, t, P)
        R.t_sky.use(location=0); R.t_ridge.use(location=1)
        for k, u in ((1, 2), (2, 3), (3, 4)):
            R.bl[k][3].use(location=u)
        self._text_uniforms(p, t, units=(5, 6, 7))
        rings = P.get("rings", [])
        ra = np.zeros((16, 4), "f4")
        for k, r in enumerate(rings[:16]):
            ra[k] = r
        if "uRings" in p:
            p["uRings"].write(ra.tobytes())
        setu(p, uSky=0, uRidge=1, uB2=2, uB3=3, uB4=4, uT=float(t), uProg=float(P["prog"]),
             uTrail=float(P["trail"]), uHi=float(P["hi"]), uSunInt=float(P["sun_int"]),
             uMtn=np.asarray(P["sky_mid"]) * 0.22 + S.lin("#05060f"), uGlow=P["glow"], uTrailCol=S.lin("#ffd396"),
             uSunS=self.sun_screen(t, P), uNRings=min(len(rings), 16),
             uCalm=float(val("BOTTOM_CALM", t, 0.0) or 0.0), uCalmY=CALM_Y)
        self.v_bg.render(moderngl.TRIANGLE_STRIP)
        self.t_cam.use(location=CAM_UNIT)
        setu(R.p_comp, uCamOn=1.0, uCamBg=CAM_UNIT)
