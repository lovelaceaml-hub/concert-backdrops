"""Renders the backdrop frame by frame (software OpenGL) and pipes frames to ffmpeg."""
import argparse
import os
import subprocess
import sys
import time

os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
import numpy as np
import moderngl

import song as S
import text as T
import shaders as G

BL, ONE = moderngl.BLEND, moderngl.ONE


def setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v


def smoothstep(a, b, x):
    u = min(max((x - a) / (b - a), 0.0), 1.0)
    return u * u * (3 - 2 * u)


CALM_Y = 0.335   # top of the lower third (fraction from the bottom), kept calm for the performers


def _val(name, t, default):
    v = getattr(S, name, None)
    if v is None:
        return default
    return v(t) if callable(v) else v


def words_arrive(m):
    """When an expression's words reach their light: the first relight after they leave, else the star time."""
    a = m.get("arrive", None)
    if a is None:
        return m["star"]
    times = sorted(a) if isinstance(a, (list, tuple)) else [a]
    later = [x for x in times if x >= m["hold"]]
    return later[0] if later else times[-1]


def comp_blocks():
    """Which optional blocks of the composite shader this song needs (shaders.COMP_BLOCKS), decided once from
    the song file. A song that uses none of them gets exactly the original shader, so it renders bit for bit as
    before the features existed."""
    def has(*keys):
        return any(getattr(S, k, None) is not None for k in keys)

    out = []
    if has("SKY_THEME"):
        out.append("SKY_THEME")
    ts = getattr(S, "TEXT_SHADOW", None)
    if ts is not None:
        # only when TEXT_SHADOW really goes below 0.05 somewhere in the song: there the veil eases to nothing
        total = float(getattr(S, "TOTAL", 0.0) or S.NFRAMES / S.FPS)
        low = min(float(ts(k * 0.25)) for k in range(int(total * 4) + 2)) if callable(ts) else float(ts)
        if low < 0.05:
            out.append("SHADOW_ZERO")
    metas = list(getattr(S, "PHRASES", [])) + [getattr(S, "TITLE", {}), getattr(S, "TAGLINE", {}),
                                               getattr(S, "CREDIT", {})] + list(getattr(S, "FRAGMENTS", []))
    if any(isinstance(m, dict) and m.get("color") for m in metas):
        out.append("TEXT_INK")
    if has("LEAVES"):
        out.append("LEAVES_TINT")
    if has("RIPPLES_AUTO") or getattr(S, "RIPPLES", None):
        out.append("LAKE_RIPPLES")
    if has("FLOWERS", "TREE", "BLOSSOM", "WATERFALL", "STREAM"):
        out.append("NATURE_PAINT")
    if has("CAMERA_ZOOM", "CAMERA_PAN", "CAMERA_CRANE"):
        out.append("CAMERA_BG")
    import figure_look
    if figure_look.wanted():   # look="silk": the faint cool tint of a body of light on a bright sky
        out.append("FIGURE_TINT")
    if any(isinstance(m, dict) and m.get("paint") for m in (getattr(S, "SYMBOLS", None) or [])):
        out.append("SYMBOL_PAINT")   # a symbol's lines painted in their own colour (engine/water.py)
    return out


class Renderer:
    def __init__(self, w=S.W, h=S.H, ctx=None):
        self.w, self.h = w, h
        self.px = h / 1080.0
        # ctx: a window's context (engine/live.py); by default an offscreen one for the cloud render
        self.ctx = ctx = ctx or moderngl.create_standalone_context(backend="egl")
        self.song = S.Song()
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def prog(vs, fs):
            return ctx.program(vertex_shader=vs, fragment_shader=fs)

        def qvao(p):
            return ctx.vertex_array(p, [(quad, "2f", "aPos")])

        self.p_sky = prog(G.QUAD_VS, G.SKY_FS); self.v_sky = qvao(self.p_sky)
        self.p_text = prog(G.QUAD_VS, G.TEXT_FS); self.v_text = qvao(self.p_text)
        self.p_lights = prog(G.QUAD_VS, G.LIGHTS_FS); self.v_lights = qvao(self.p_lights)
        self.p_credit = prog(G.QUAD_VS, G.CREDIT_FS); self.v_credit = qvao(self.p_credit)
        self.p_blur = prog(G.QUAD_VS, G.BLUR_FS); self.v_blur = qvao(self.p_blur)
        self.p_comp = prog(G.QUAD_VS, G.comp_fs(comp_blocks())); self.v_comp = qvao(self.p_comp)
        self.p_prot = prog(G.QUAD_VS, G.PROTECT_FS); self.v_prot = qvao(self.p_prot)
        import sky_camera as SKC   # cam_vs: the stars move with the sky when a song moves the camera
        self.p_star = prog(SKC.cam_vs(G.STAR_VS), G.STAR_FS)
        self.p_mote = prog(G.MOTE_VS, G.MOTE_FS)
        self.p_petal = prog(G.PETAL_VS, G.PETAL_FS)
        self.p_textp = prog(G.TEXTP_VS, G.TEXTP_FS)
        for p in (self.p_sky, self.p_text, self.p_lights, self.p_blur, self.p_credit, self.p_prot):
            setu(p, uFlip=1.0)
        setu(self.p_comp, uFlip=-1.0)   # the last pass is drawn upside down so rows read top to bottom

        rng = np.random.default_rng(42)
        n = 1700
        st = np.zeros((n, 4), "f4")
        st[:, 0] = rng.random(n)
        st[:, 1] = 0.44 + 0.56 * rng.random(n) ** 0.75
        st[:, 2:] = rng.random((n, 2))
        self.v_star = ctx.vertex_array(self.p_star, [(ctx.buffer(st.tobytes()), "2f 2f", "aPos", "aSeed")])
        self.n_star = n
        self.lake_stars = None
        if getattr(S, "LAKE_STARS", None) is not None:
            import lake_stars
            self.lake_stars = lake_stars.LakeStars(self, st)   # the stars mirrored in the lake (optional)

        def seeds(k, seed):
            return ctx.buffer(np.random.default_rng(seed).random((k, 4)).astype("f4").tobytes())

        self.v_mote = ctx.vertex_array(self.p_mote, [(seeds(2400, 1), "4f", "aSeed")])
        self.v_lant = ctx.vertex_array(self.p_mote, [(seeds(110, 2), "4f", "aSeed")])
        self.v_petal = ctx.vertex_array(self.p_petal, [(seeds(300, 3), "4f", "aSeed")])

        def tex_f(size, comps=4):
            t = ctx.texture(size, comps, dtype="f2")
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t

        self.t_sky = tex_f((w, h)); self.f_sky = ctx.framebuffer([self.t_sky])
        self.t_L = tex_f((w, h)); self.f_L = ctx.framebuffer([self.t_L])
        self.bl = []
        gs = max(h / 1080.0, 1.0)   # HOWTO Q: at 4K the glow buffers keep their 1080p sizes, so the bloom looks the same
        for k in (2, 4, 8, 16):
            size = (max(int(w // (k * gs)), 8), max(int(h // (k * gs)), 8))
            ta, tb = tex_f(size), tex_f(size)
            self.bl.append((size, ta, ctx.framebuffer([ta]), tb, ctx.framebuffer([tb])))
        self.t_out = ctx.texture((w, h), 3, dtype="f1"); self.f_out = ctx.framebuffer([self.t_out])

        self.t_ridge = ctx.texture((2048, 1), 1, data=self.song.ridge.tobytes(), dtype="f4")
        self.t_ridge.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.t_ridge.repeat_x = self.t_ridge.repeat_y = False

        phrases, title, tag = T.build_all()

        def ttex(arr):
            t = ctx.texture((T.W, T.H), 3, data=arr.tobytes(), dtype="f1")
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t

        self.words = []
        for meta, d in zip(S.PHRASES + [S.TITLE], phrases + [title]):
            vao = ctx.vertex_array(self.p_textp, [(ctx.buffer(d["pts"].tobytes()), "3f 4f", "aTarget", "aSeed")])
            self.words.append(dict(meta=meta, tex=ttex(d["tex"]), vao=vao, n=d["pts"].shape[0], bounds=d["bounds"]))
        self.tag = dict(tex=ttex(tag["tex"]), bounds=tag["bounds"])
        self.frags = [dict(tex=ttex(f["tex"]), bounds=f["bounds"], meta=f["meta"]) for f in tag["frags"]]
        ctex, self.credit_bbox = T.render_credit(S.CREDIT["song"], S.CREDIT["concert"])
        self.t_credit = ctx.texture((T.W, T.H), 3, data=ctex.tobytes(), dtype="f1")
        self.t_credit.build_mipmaps()
        self.t_credit.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.t_credit.repeat_x = self.t_credit.repeat_y = False
        self.t_blank = ctx.texture((4, 4), 3, data=bytes(48), dtype="f1")
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        import upgrade
        self.up = upgrade.Upgrade(self)   # scenes, people of light, effect layers, fragment styles (all optional)
        import text_anims
        self.ta = text_anims.TextAnims(self)   # other text animations (anim=, UPGRADE-HOWTO section J; all optional)
        import gathering
        self.gath = gathering.Gathering(self)   # a gathering crowd and a light passed hand to hand (optional)
        import water
        self.water = water.Water(self)   # lake ripples, symbols drawn in light, falling stars (all optional)
        import creatures
        self.cr = creatures.Creatures(self)   # doves, butterflies, fireflies (all optional)
        import nature
        self.nature = nature.Nature(self)   # flowers, tree, blossoms, waterfall, stream (all optional)
        import sky_camera
        self.sky = sky_camera.SkyCamera(self)   # time of day, 3D clouds, god rays, camera (all optional)
        import audio_react
        self.react = audio_react.Reactor(self) if audio_react.enabled() else None   # music reactivity (optional)
        import output
        self.out = output.Output(self)   # HOWTO Q: event card and seamless loop (optional)
        import figure_look
        self.fl = figure_look.FigureLook(self)   # HOWTO H5: the silk look for people of light (optional)

    # ------------------------------------------------------------------
    def text_plan(self, t):
        """The text on screen at t, as two slots (texture, form params, bounds, shade strength).
        A: an expression or the closing title. B: the end card lines, else a lyric fragment (any style)."""
        blank = (self.t_blank, (0.0, 3.0, -1.0, 0.0), (0.0, 1.0), 0.0, (0.0, 0.0))
        A, B = blank, blank
        # the shade is only an on/off master: the shaders tie the veil per pixel to the letters themselves
        for wd in self.words:
            m = wd["meta"]
            arrive = words_arrive(m)
            if not (m["form"] <= t < arrive + 0.2):
                continue
            form_t, fly_t = t - m["form"], t - m["hold"]
            A = (wd["tex"], (form_t, S.FORM_DUR, fly_t, 1.0), wd["bounds"], 1.0, (0.0, 0.0))
        tg = S.TAGLINE
        if t >= tg["t0"]:
            B = (self.tag["tex"], ((t - tg["t0"]) + 1.35, (tg["t1"] - tg["t0"]), -1.0, 0.92), self.tag["bounds"],
                 1.0, (0.0, 0.0))
            return A, B
        for fr in self.frags:
            m = fr["meta"]
            if m.get("style", "sparks") != "sparks" or not (m["t0"] <= t < m["out"] + 1.6):
                continue
            dur = max(m["t1"] - m["t0"], 0.5)
            fly = (t - m["out"]) if t > m["out"] else -1.0
            return A, (fr["tex"], ((t - m["t0"]) + 1.35, dur, fly, m.get("alpha", 0.95)), fr["bounds"], 1.0, (0.0, 0.0))
        ev = self.out.card_slot(t)   # HOWTO Q: the event card of a pre-show or intermission loop
        if ev is not None:
            return A, ev
        ts = self.up.text_shadow(t)
        if ts is not None:
            B = tuple(ts) + ((0.0, 0.0),) if len(ts) == 4 else tuple(ts)
        return A, B

    def frame(self, t, index=0):
        ctx, w, h, px = self.ctx, self.w, self.h, self.px
        P = S.params(self.song, t)
        self.sky.adjust(t, P)
        if self.react:
            P = self.react.apply(P, t)
        asp = S.ASPECT
        L = S.lin
        cool = S.MILKY(t)

        def cols(name, default):
            # a song may set NAME to a pair of colors, or to a function of time returning a pair
            c = getattr(S, name, None)
            c = c(t) if callable(c) else c
            return c if c else default

        aw, ac = cols("AURORA_WARM", ("#ff8fa8", "#ffc88a")), cols("AURORA_COOL", ("#86c8ff", "#b39cff"))
        aurA = L(aw[0]) * 0.72 * (1 - cool) + L(ac[0]) * cool
        aurB = L(aw[1]) * 0.72 * (1 - cool) + L(ac[1]) * cool

        # 1. sky (half size: it is all soft light)
        ctx.disable(BL)
        self.f_sky.use()
        setu(self.p_sky, uT=t, uAspect=asp, uHorizon=S.HORIZON, uSkyTop=P["sky_top"], uSkyMid=P["sky_mid"],
             uSkyHor=P["sky_hor"], uGlow=P["glow"], uAurA=aurA, uAurB=aurB, uSun=(0.5, P["sun_y"]),
             uSunInt=P["sun_int"], uSunSize=P["sun_size"], uClouds=P["clouds"], uAurora=P["aurora"],
             uRain=P["rain"], uMilky=P["milky"], uEnv=P["env"], uRays=P["rays"], uPart=P["part"])
        self.v_sky.render(moderngl.TRIANGLE_STRIP)
        self.sky.draw_clouds(t, P)

        # 2. everything that glows
        self.f_L.use()
        self.f_L.clear(0.0, 0.0, 0.0, 1.0)
        ctx.enable(BL)
        ctx.blend_func = (ONE, ONE)
        calm0 = float(_val("BOTTOM_CALM", t, 0.0))   # Astra round 1, finding 12: a calm lower third
        setu(self.p_star, uT=t, uStars=P["stars"], uHi=P["hi"], uPx=px, uCamAff=self.sky.aff(0.12))
        self.v_star.render(moderngl.POINTS)
        if self.lake_stars is not None:   # LAKE_STARS: the same stars, mirrored in the lake (engine/lake_stars.py)
            self.lake_stars.draw(t, P, calm0)
        setu(self.p_mote, uT=t, uAmount=min(P["motes"], 1.0), uPx=px, uSizeMin=getattr(S, "MOTE_SIZE", (2.4, 24.0))[0],
             uSizeMax=getattr(S, "MOTE_SIZE", (2.4, 24.0))[1], uPeriod=30.0,
             uY0=getattr(S, "MOTE_Y", (-0.05, 1.05))[0], uY1=getattr(S, "MOTE_Y", (-0.05, 1.05))[1], uSway=0.012,
             uBright=0.62 + 0.30 * P["env"], uColA=L(cols("MOTE_COLORS", ("#ffe2a8", "#ff9f8a"))[0]),
             uColB=L(cols("MOTE_COLORS", ("#ffe2a8", "#ff9f8a"))[1]), uCalm=calm0, uCalmY=CALM_Y)
        self.v_mote.render(moderngl.POINTS)
        if P["lanterns"] > 0.001:
            setu(self.p_mote, uT=t, uAmount=P["lanterns"], uPx=px, uSizeMin=13.0, uSizeMax=44.0, uPeriod=40.0,
                 uY0=0.24, uY1=1.08, uSway=0.016, uBright=1.25,
                 uColA=L(cols("LANTERN_COLORS", ("#ffb45e", "#ff8a4c"))[0]), uColB=L(cols("LANTERN_COLORS", ("#ffb45e", "#ff8a4c"))[1]))
            self.v_lant.render(moderngl.POINTS)
        if P["petals"] > 0.001:
            setu(self.p_petal, uT=t, uAmount=P["petals"], uPx=px, uColA=L(cols("PETAL_COLORS", ("#ff7fa2", "#ffd2c2"))[0]) * 0.95,
                 uColB=L(cols("PETAL_COLORS", ("#ff7fa2", "#ffd2c2"))[1]) * 0.62, uCalm=calm0, uCalmY=CALM_Y)
            self.v_petal.render(moderngl.POINTS)
        self.up.draw_effects(t, P)
        self.nature.draw(t)
        self.cr.draw(t)
        if self.react:
            self.react.draw(t, P)
        self.fl.begin(t, P)       # look="silk" (engine/figure_look.py): figures and crowd queue their bodies,
        self.up.draw_figures(t)
        self.gath.draw(t)
        self.fl.resolve(t, P)     # which are drawn here, with their mirror images in the lake
        self.water.draw(t)
        self.sky.draw_light(t, P)

        # which text is on screen: A is an expression or the closing title, B the end card lines or a fragment
        (texA, txA, bndA, shadeA, offA), (texB, txB, bndB, shadeB, offB) = self.text_plan(t)
        credit, c0 = S.credit_state(t, self.credit_bbox)

        # protect the text (Astra round 1, finding 3): dim every light drawn so far (motes, petals, snow, beams,
        # nets, figures) behind the words, so no spark or ray crosses a letter; the words are drawn after this
        prot = float(min(max(_val("TEXT_PROTECT", t, 1.0), 0.0), 1.0))
        if prot > 0.0 and (shadeA > 0.0 or shadeB > 0.0 or credit[3] > 0.001):
            ctx.blend_func = (moderngl.ZERO, moderngl.SRC_COLOR)
            texA.use(location=0); texB.use(location=1); self.t_credit.use(location=2)
            setu(self.p_prot, uTexA=0, uTexB=1, uTexC=2, uShade=(float(shadeA), float(shadeB)), uK=0.94 * prot,
                 uTxA=tuple(float(v) for v in txA), uTxB=tuple(float(v) for v in txB), uBndA=tuple(bndA),
                 uBndB=tuple(bndB), uOffA=tuple(offA), uOffB=tuple(offB),
                 uCredit=tuple(float(v) for v in credit), uC0=c0)
            self.v_prot.render(moderngl.TRIANGLE_STRIP)
            ctx.blend_func = (ONE, ONE)
        self.sky.after_protect(t, P)   # god rays, when TEXT_SHADOW is below 0.05 (no hole in the haze behind text)

        # words: particles, then the solid letters
        calm = float(_val("BOTTOM_CALM", t, 0.0))
        for i, wd in enumerate(self.words):
            m = wd["meta"]
            arrive = words_arrive(m)   # when the words reach their light (a relit star arrives later)
            if not (m["form"] <= t < arrive + 0.2):
                continue
            form_t = t - m["form"]
            fly_t = t - m["hold"]
            fly_dur = max(arrive - m["hold"], 1.0)
            star = S.STAR_POS[i] if i < 9 else (0.5, 0.9)
            if self.ta.draw_word(i, t, form_t, fly_t, fly_dur, star, P, calm):
                continue
            setu(self.p_textp, uT=t, uFormT=form_t, uFormDur=S.FORM_DUR, uFlyT=fly_t, uFlyDur=fly_dur, uPx=px,
                 uPulse=P["pulse"], uStar=star, **self.up.text_sparks(m, t),
                 uCalm=calm, uCalmY=CALM_Y)
            wd["vao"].render(moderngl.POINTS)
            wd["tex"].use(location=0)
            setu(self.p_text, uTex=0, uFormT=form_t, uFormDur=S.FORM_DUR, uFlyT=fly_t, uAspect=asp, uAlpha=1.0,
                 uPulse=P["pulse"], uBounds=wd["bounds"], **self.up.text_light(m, t, "#fff5df"))
            self.v_text.render(moderngl.TRIANGLE_STRIP)
        tg = S.TAGLINE
        if t >= tg["t0"] and not self.ta.draw_tagline(t, calm):
            self.tag["tex"].use(location=0)
            setu(self.p_text, uTex=0, uFormT=(t - tg["t0"]) + 1.35, uFormDur=(tg["t1"] - tg["t0"]), uFlyT=-1.0,
                 uAspect=asp, uAlpha=0.92, uPulse=0.0, uBounds=self.tag["bounds"],
                 **self.up.text_light(tg, t, "#fff1d6"))
            self.v_text.render(moderngl.TRIANGLE_STRIP)

        # short lyric fragments: form, hold, then dissolve
        for k, fr in enumerate(self.frags):
            m = fr["meta"]
            if m.get("style", "sparks") != "sparks":
                continue   # drawn by the upgrade layers below
            if not (m["t0"] <= t < m["out"] + 1.6):
                continue
            if self.ta.draw_frag(k, t, calm):
                continue
            fly = (t - m["out"]) if t > m["out"] else -1.0
            fr["tex"].use(location=0)
            setu(self.p_text, uTex=0, uFormT=(t - m["t0"]) + 1.35, uFormDur=max(m["t1"] - m["t0"], 0.5), uFlyT=fly,
                 uAspect=asp, uAlpha=m.get("alpha", 0.95), uPulse=0.0, uBounds=fr["bounds"],
                 **self.up.text_light(m, t, "#fff1d6"))
            self.v_text.render(moderngl.TRIANGLE_STRIP)
        self.up.draw_frags(t)
        self.out.draw_card(t)

        # song title and concert title: a card at the start, then small in the corner
        if credit[3] > 0.001:
            self.t_credit.use(location=0)
            setu(self.p_credit, uTex=0, uCredit=tuple(float(v) for v in credit), uC0=c0,
                 **self.up.text_light(S.CREDIT, t, "#fff5df"))
            self.v_credit.render(moderngl.TRIANGLE_STRIP)

        # the nine lights and the lines between them
        st = P["star"]
        if any(s[0] > 0.001 for s in st):
            self.f_L.scissor = (0, int(h * 0.73), w, h - int(h * 0.73))
            self.p_lights["uStarPos"].value = [tuple(p) for p in S.STAR_POS]
            self.p_lights["uStarI"].value = [(float(s[0]), float(s[1])) for s in st]
            if "uStarR" in self.p_lights:
                self.p_lights["uStarR"].value = [float(s[2]) if len(s) > 2 else 0.0 for s in st]
            self.p_lights["uLink"].value = [float(v) for v in P["link"]]
            setu(self.p_lights, uT=t, uAspect=asp, uHi=P["hi"], uColA=L("#fff3d6"), uColB=L("#ffc2a4"), uMode=0)
            self.v_lights.render(moderngl.TRIANGLE_STRIP)
        # the lantern that crosses the skyline with the music
        lx, ly = P["lantern"]
        sl = getattr(S, "SKYLINE_LANTERN", 1.0)   # optional: 0 hides the light that travels along the skyline
        sl = sl(t) if callable(sl) else sl
        li = smoothstep(0.15, 1.2, t) * (0.80 + 0.45 * P["env"]) * sl
        x0, x1 = max(int((lx - 0.07) * w), 0), min(int((lx + 0.07) * w), w)
        y0, y1 = max(int((ly - 0.11) * h), 0), min(int((ly + 0.11) * h), h)
        self.f_L.scissor = (x0, y0, max(x1 - x0, 1), max(y1 - y0, 1))
        setu(self.p_lights, uT=t, uAspect=asp, uHi=P["hi"], uColA=L("#ffe3a6"), uMode=1,
             uLantern=(lx, ly + 0.004), uLanternI=li)
        self.v_lights.render(moderngl.TRIANGLE_STRIP)
        self.f_L.scissor = None

        # 3. glow: four blurred copies, each half the size of the last
        ctx.disable(BL)
        src = self.t_L
        for size, ta, fa, tb, fb in self.bl:
            fa.use(); src.use(location=0)
            setu(self.p_blur, uTex=0, uDir=(1.0 / size[0], 0.0))
            self.v_blur.render(moderngl.TRIANGLE_STRIP)
            fb.use(); ta.use(location=0)
            setu(self.p_blur, uTex=0, uDir=(0.0, 1.0 / size[1]))
            self.v_blur.render(moderngl.TRIANGLE_STRIP)
            src = tb

        # 4. put it together
        self.sky.camera_bg(t, P)
        self.f_out.use()
        self.t_sky.use(location=0); self.t_L.use(location=1)
        for k in range(4):
            self.bl[k][3].use(location=2 + k)
        self.t_ridge.use(location=6); texA.use(location=7); texB.use(location=8); self.t_credit.use(location=9)
        rings = P["rings"]
        ra = np.zeros((16, 4), "f4")
        for k, r in enumerate(rings):
            ra[k] = r
        wa = np.zeros((4, 4), "f4")
        waves = P["waves"][-4:]
        for k, wv in enumerate(waves):
            wa[k] = wv
        if "uRings" in self.p_comp:
            self.p_comp["uRings"].write(ra.tobytes())
        if "uWaves" in self.p_comp:
            self.p_comp["uWaves"].write(wa.tobytes())
        mtn = P["sky_mid"] * 0.22 + L("#05060f")
        setu(self.p_comp, uSky=0, uL=1, uB1=2, uB2=3, uB3=4, uB4=5, uRidge=6, uTextA=7, uTextB=8,
             uT=t, uAspect=asp, uHorizon=S.HORIZON, uProg=P["prog"], uTrail=P["trail"], uExposure=P["exposure"],
             uFade=P["fade"], uFrame=float(index % 1024), uBloom=(1.0 - 0.30 * min(P["sun_int"], 1.3) / 1.3) * P.get("bloom_gain", 1.0),
             uTxA=txA, uBndA=bndA, uTxB=txB, uBndB=bndB, uZoom=P["zoom"],
             uTextC=9, uCredit=tuple(float(v) for v in credit), uC0=c0, uHi=P["hi"], uEnv=P["env"],
             uSunInt=P["sun_int"], uMtn=mtn, uSkyHor=P["sky_hor"], uGlow=P["glow"], uTrailCol=L("#ffd396"),
             uSun=(0.5, P["sun_y"]), uShade=(float(shadeA), float(shadeB)), uNRings=len(rings), uNWaves=len(waves),
             uOffA=tuple(float(v) for v in offA), uOffB=tuple(float(v) for v in offB),
             uCalm=calm0, uCalmY=CALM_Y)
        self.up.comp_uniforms(self.p_comp, t, P)
        self.water.comp_uniforms(self.p_comp, t)
        self.nature.comp_uniforms(self.p_comp)
        self.fl.comp_uniforms(self.p_comp, t, P)
        self.v_comp.render(moderngl.TRIANGLE_STRIP)
        return self.f_out.read(components=3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", default=os.path.join(S.ROOT, "previews"))
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--range", nargs=2, type=int, default=None)
    ap.add_argument("--out", default="")
    ap.add_argument("--crf", default="15")
    ap.add_argument("--preset", default="medium")
    a = ap.parse_args()
    import output
    a.scale *= output.scale(S)   # HOWTO Q: OUT_RES=4k draws 3840x2160 frames from the same 1920x1080 design
    w, h = int(S.W * a.scale) // 2 * 2, int(S.H * a.scale) // 2 * 2
    R = Renderer(w, h)
    if a.stills:
        from PIL import Image
        os.makedirs(a.outdir, exist_ok=True)
        for s in a.stills.split(","):
            t = float(s)
            t0 = time.time()
            buf = R.out.frame(t, int(t * S.FPS))
            dt = time.time() - t0
            Image.frombytes("RGB", (w, h), buf).save(os.path.join(a.outdir, f"t{t:07.2f}.png"))
            print(f"still {t:7.2f}s  {dt:.2f}s/frame", flush=True)
        return
    f0, f1 = a.range
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(S.FPS),
           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", a.preset,
           "-crf", a.crf, "-pix_fmt", "yuv420p", "-g", "60", "-bf", "2", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-movflags", "+faststart", a.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(f0, f1):
        ff.stdin.write(R.out.frame(i / S.FPS, i))
        if (i - f0) % 150 == 0:
            el = time.time() - t0
            print(f"frame {i} ({i - f0}/{f1 - f0})  {el:.0f}s  {(el / max(i - f0, 1)):.2f}s/frame", flush=True)
    ff.stdin.close()
    ff.wait()
    if ff.returncode != 0:
        sys.exit(f"ffmpeg failed with code {ff.returncode}")
    print("done", a.out, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
