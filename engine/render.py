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


class Renderer:
    def __init__(self, w=S.W, h=S.H):
        self.w, self.h = w, h
        self.px = h / 1080.0
        self.ctx = ctx = moderngl.create_standalone_context(backend="egl")
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
        self.p_comp = prog(G.QUAD_VS, G.COMP_FS); self.v_comp = qvao(self.p_comp)
        self.p_star = prog(G.STAR_VS, G.STAR_FS)
        self.p_mote = prog(G.MOTE_VS, G.MOTE_FS)
        self.p_petal = prog(G.PETAL_VS, G.PETAL_FS)
        self.p_textp = prog(G.TEXTP_VS, G.TEXTP_FS)
        for p in (self.p_sky, self.p_text, self.p_lights, self.p_blur, self.p_credit):
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
        for k in (2, 4, 8, 16):
            size = (max(w // k, 8), max(h // k, 8))
            ta, tb = tex_f(size), tex_f(size)
            self.bl.append((size, ta, ctx.framebuffer([ta]), tb, ctx.framebuffer([tb])))
        self.t_out = ctx.texture((w, h), 3, dtype="f1"); self.f_out = ctx.framebuffer([self.t_out])

        self.t_ridge = ctx.texture((2048, 1), 1, data=self.song.ridge.tobytes(), dtype="f4")
        self.t_ridge.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.t_ridge.repeat_x = self.t_ridge.repeat_y = False

        phrases, title, tag = T.build_all()

        def ttex(arr):
            t = ctx.texture((S.W, S.H), 3, data=arr.tobytes(), dtype="f1")
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t

        self.words = []
        for meta, d in zip(S.PHRASES + [S.TITLE], phrases + [title]):
            vao = ctx.vertex_array(self.p_textp, [(ctx.buffer(d["pts"].tobytes()), "3f 4f", "aTarget", "aSeed")])
            self.words.append(dict(meta=meta, tex=ttex(d["tex"]), vao=vao, n=d["pts"].shape[0], bounds=d["bounds"]))
        self.tag = dict(tex=ttex(tag["tex"]), bounds=tag["bounds"])
        ctex, self.credit_bbox = T.render_credit(S.CREDIT["song"], S.CREDIT["concert"])
        self.t_credit = ctx.texture((S.W, S.H), 3, data=ctex.tobytes(), dtype="f1")
        self.t_credit.build_mipmaps()
        self.t_credit.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.t_credit.repeat_x = self.t_credit.repeat_y = False
        self.t_blank = ctx.texture((4, 4), 3, data=bytes(48), dtype="f1")
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)

    # ------------------------------------------------------------------
    def frame(self, t, index=0):
        ctx, w, h, px = self.ctx, self.w, self.h, self.px
        P = S.params(self.song, t)
        asp = S.ASPECT
        L = S.lin
        cool = S.MILKY(t)
        aurA = L("#ff8fa8") * 0.72 * (1 - cool) + L("#86c8ff") * cool
        aurB = L("#ffc88a") * 0.72 * (1 - cool) + L("#b39cff") * cool

        # 1. sky (half size: it is all soft light)
        ctx.disable(BL)
        self.f_sky.use()
        setu(self.p_sky, uT=t, uAspect=asp, uHorizon=S.HORIZON, uSkyTop=P["sky_top"], uSkyMid=P["sky_mid"],
             uSkyHor=P["sky_hor"], uGlow=P["glow"], uAurA=aurA, uAurB=aurB, uSun=(0.5, P["sun_y"]),
             uSunInt=P["sun_int"], uSunSize=P["sun_size"], uClouds=P["clouds"], uAurora=P["aurora"],
             uRain=P["rain"], uMilky=P["milky"], uEnv=P["env"], uRays=P["rays"], uPart=P["part"])
        self.v_sky.render(moderngl.TRIANGLE_STRIP)

        # 2. everything that glows
        self.f_L.use()
        self.f_L.clear(0.0, 0.0, 0.0, 1.0)
        ctx.enable(BL)
        ctx.blend_func = (ONE, ONE)
        setu(self.p_star, uT=t, uStars=P["stars"], uHi=P["hi"], uPx=px)
        self.v_star.render(moderngl.POINTS)
        setu(self.p_mote, uT=t, uAmount=min(P["motes"], 1.0), uPx=px, uSizeMin=2.4, uSizeMax=24.0, uPeriod=30.0,
             uY0=-0.05, uY1=1.05, uSway=0.012, uBright=0.62 + 0.30 * P["env"], uColA=L("#ffe2a8"), uColB=L("#ff9f8a"))
        self.v_mote.render(moderngl.POINTS)
        if P["lanterns"] > 0.001:
            setu(self.p_mote, uT=t, uAmount=P["lanterns"], uPx=px, uSizeMin=13.0, uSizeMax=44.0, uPeriod=40.0,
                 uY0=0.24, uY1=1.08, uSway=0.016, uBright=1.25, uColA=L("#ffb45e"), uColB=L("#ff8a4c"))
            self.v_lant.render(moderngl.POINTS)
        if P["petals"] > 0.001:
            setu(self.p_petal, uT=t, uAmount=P["petals"], uPx=px, uColA=L("#ff7fa2") * 0.95, uColB=L("#ffd2c2") * 0.62)
            self.v_petal.render(moderngl.POINTS)

        # words: particles, then the solid letters
        texA, shadeA = self.t_blank, 0.0
        txA, bndA, txB, bndB = (0.0, 3.0, -1.0, 0.0), (0.0, 1.0), (0.0, 3.0, -1.0, 0.0), (0.0, 1.0)
        for i, wd in enumerate(self.words):
            m = wd["meta"]
            if not (m["form"] <= t < m["star"] + 0.2):
                continue
            form_t = t - m["form"]
            fly_t = t - m["hold"]
            fly_dur = max(m["star"] - m["hold"], 1.0)
            star = S.STAR_POS[i] if i < 9 else (0.5, 0.9)
            setu(self.p_textp, uT=t, uFormT=form_t, uFormDur=S.FORM_DUR, uFlyT=fly_t, uFlyDur=fly_dur, uPx=px,
                 uPulse=P["pulse"], uStar=star, uColA=L("#fff0cc") * 1.0, uColB=L("#ffb070") * 1.15)
            wd["vao"].render(moderngl.POINTS)
            wd["tex"].use(location=0)
            setu(self.p_text, uTex=0, uFormT=form_t, uFormDur=S.FORM_DUR, uFlyT=fly_t, uAspect=asp, uAlpha=1.0,
                 uPulse=P["pulse"], uBounds=wd["bounds"], uCol=L("#fff5df"), uGlowCol=L("#ffc48c"))
            self.v_text.render(moderngl.TRIANGLE_STRIP)
            texA = wd["tex"]
            txA, bndA = (form_t, S.FORM_DUR, fly_t, 1.0), wd["bounds"]
            shadeA = smoothstep(0.6, S.FORM_DUR + 0.6, form_t) * (1.0 - smoothstep(0.0, 1.6, fly_t))
        texB, shadeB = self.t_blank, 0.0
        tg = S.TAGLINE
        if t >= tg["t0"]:
            self.tag["tex"].use(location=0)
            setu(self.p_text, uTex=0, uFormT=(t - tg["t0"]) + 1.35, uFormDur=(tg["t1"] - tg["t0"]), uFlyT=-1.0,
                 uAspect=asp, uAlpha=0.92, uPulse=0.0, uBounds=self.tag["bounds"], uCol=L("#fff1d6"), uGlowCol=L("#ffc48c"))
            self.v_text.render(moderngl.TRIANGLE_STRIP)
            texB, shadeB = self.tag["tex"], smoothstep(tg["t0"], tg["t1"] + 1.0, t)
            txB, bndB = ((t - tg["t0"]) + 1.35, (tg["t1"] - tg["t0"]), -1.0, 0.92), self.tag["bounds"]

        # song title and concert title: a card at the start, then small in the corner
        credit, c0 = S.credit_state(t, self.credit_bbox)
        if credit[3] > 0.001:
            self.t_credit.use(location=0)
            setu(self.p_credit, uTex=0, uCredit=tuple(float(v) for v in credit), uC0=c0,
                 uCol=L("#fff5df"), uGlowCol=L("#ffc48c"))
            self.v_credit.render(moderngl.TRIANGLE_STRIP)

        # the nine lights and the lines between them
        st = P["star"]
        if any(s[0] > 0.001 for s in st):
            self.f_L.scissor = (0, int(h * 0.73), w, h - int(h * 0.73))
            self.p_lights["uStarPos"].value = [tuple(p) for p in S.STAR_POS]
            self.p_lights["uStarI"].value = [(float(s[0]), float(s[1])) for s in st]
            self.p_lights["uLink"].value = [float(v) for v in P["link"]]
            setu(self.p_lights, uT=t, uAspect=asp, uHi=P["hi"], uColA=L("#fff3d6"), uColB=L("#ffc2a4"), uMode=0)
            self.v_lights.render(moderngl.TRIANGLE_STRIP)
        # the lantern that crosses the skyline with the music
        lx, ly = P["lantern"]
        li = smoothstep(0.15, 1.2, t) * (0.80 + 0.45 * P["env"])
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
             uFade=P["fade"], uFrame=float(index % 1024), uBloom=1.0 - 0.30 * min(P["sun_int"], 1.3) / 1.3,
             uTxA=txA, uBndA=bndA, uTxB=txB, uBndB=bndB, uZoom=P["zoom"],
             uTextC=9, uCredit=tuple(float(v) for v in credit), uC0=c0, uHi=P["hi"], uEnv=P["env"],
             uSunInt=P["sun_int"], uMtn=mtn, uSkyHor=P["sky_hor"], uGlow=P["glow"], uTrailCol=L("#ffd396"),
             uSun=(0.5, P["sun_y"]), uShade=(float(shadeA), float(shadeB)), uNRings=len(rings), uNWaves=len(waves))
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
    w, h = int(S.W * a.scale) // 2 * 2, int(S.H * a.scale) // 2 * 2
    R = Renderer(w, h)
    if a.stills:
        from PIL import Image
        os.makedirs(a.outdir, exist_ok=True)
        for s in a.stills.split(","):
            t = float(s)
            t0 = time.time()
            buf = R.frame(t, int(t * S.FPS))
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
        ff.stdin.write(R.frame(i / S.FPS, i))
        if (i - f0) % 150 == 0:
            el = time.time() - t0
            print(f"frame {i} ({i - f0}/{f1 - f0})  {el:.0f}s  {(el / max(i - f0, 1)):.2f}s/frame", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", a.out, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
