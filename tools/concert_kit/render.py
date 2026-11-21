"""Isolated cloud CPU renderer for the native Consideration model proof.

Planning imports are cheap. The OpenGL context is created only by make_renderer.
RGB bytes use the established renderer's display curve, with explicit BT.709
matrix/range conversion at encoding and no second transfer-function conversion.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"work/concert-kit"
DURATION=18.0
FPS=60
CUTS=(3.0,12.0)
COLOR_CONTRACT={"name":"legacy_display_gamma","input":"rgb24", "display_curve":"established p3d filmic display RGB",
    "encode_matrix":"bt709","encode_range":"limited","primaries":"bt709",
    "transfer_tag":"bt709","transfer_conversion":False}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fonts_path():
    candidates=[Path(os.environ["CONCERT_KIT_FONTS"])] if os.environ.get("CONCERT_KIT_FONTS") else []
    candidates.extend([ROOT/"fonts",WORK/"fonts",ROOT.parent/"cinematic-beauty/fonts"])
    for p in candidates:
        if (p/"cormorant-garamond-latin-700-italic.ttf").is_file():
            return p.resolve()
    raise RuntimeError("Prepare the project fonts or set CONCERT_KIT_FONTS to their directory.")


def source_hashes():
    paths=set((ROOT/"tools/concert_kit").glob("*.py"))
    paths.update((ROOT/"engine").rglob("*.py"))
    paths.update([ROOT/"assets/p3d/body_v1.npz",ROOT/"pyproject.toml",ROOT/"uv.lock"])
    out={str(p.relative_to(ROOT)):digest(p) for p in sorted(paths) if p.is_file()}
    out.update({"fonts/"+p.name:digest(p) for p in sorted(fonts_path().glob("*.ttf"))})
    return out


def make_renderer(width=1920,height=1080,temporal_samples=2,fps=60,scene="consideration"):
    if sys.platform=="darwin":
        raise RuntimeError("This study is configured for cloud CPU rendering.")
    if os.environ.get("PYTHONHASHSEED")!="0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before starting Python.")
    if fps not in (30,60):
        raise ValueError("Use an explicitly supported native rate: 30 or 60 fps.")
    if scene not in ("consideration","model_atlas"):
        raise ValueError("Unknown concert kit scene")
    if "P3D_BODY_ASSET" in os.environ:
        raise RuntimeError("Unset P3D_BODY_ASSET: this study requires the pinned repository body asset.")
    cache_key=hashlib.sha256((digest(ROOT/"assets/p3d/body_v1.npz")+digest(ROOT/"engine/p3d/body.py")+
        digest(ROOT/"engine/p3d/actor.py")+digest(ROOT/"tools/concert_kit/people.py")).encode()).hexdigest()[:20]
    WORK.mkdir(parents=True,exist_ok=True)
    os.environ.update(SONG=scene,OUT_FPS=str(fps),OUT_RES="4k" if width==3840 else "1080p",
        LIBGL_ALWAYS_SOFTWARE="1",LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS","1"),
        OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",NUMBA_CACHE_DIR=str(WORK/"numba"),
        MESA_SHADER_CACHE_DIR=str(WORK/"mesa"),P3D_CACHE=str(WORK/"p3d-cache"/cache_key))
    sys.path.insert(0,str(ROOT))
    sys.path.insert(0,str(ROOT/"engine"))
    import songs
    songs.__path__.append(str(ROOT/"tools/concert_kit"))
    # Legacy text functions capture their font paths in default arguments.
    # Select the existing verified font root before that module is imported.
    import song
    fp=fonts_path()
    song.ROOT=str(fp.parent)
    import render as legacy
    import text as typography
    typography.FONTS=str(fp)
    for key,name in {"F_PHRASE":"cormorant-garamond-latin-700-italic.ttf",
        "F_TITLE":"cormorant-garamond-latin-700-normal.ttf","F_LABEL":"jost-latin-500-normal.ttf",
        "F_TAG":"cormorant-garamond-latin-600-italic.ttf"}.items():
        setattr(typography,key,str(fp/name))
    import shaders
    shaders.COMP_FS=shaders.COMP_FS.replace("col += (n1+n2-1.0)*(1.15/255.0);","// No added delivery grain.")
    r=legacy.Renderer(width,height)
    r.p3d.samples=int(temporal_samples)
    r.p3d.draft=False
    r.kit_fps=fps
    r.kit_scene=scene
    r.kit_cuts=tuple(importlib.import_module("songs."+scene).CUTS)
    r.kit_shutter=r.p3d.shutter
    r.kit_overlay=_make_overlays(width,height,fp)
    original=r.p3d.adjust
    def adjust(t,p):
        p=original(t,p)
        p["bloom_gain"]=p.get("bloom_gain",1.0)*.72
        return p
    r.p3d.adjust=adjust
    return r


def _make_overlays(width,height,fp):
    from PIL import Image,ImageDraw,ImageFont,ImageFilter
    from p3d.words import EXPRESSIONS
    from p3d.brand import logo_image
    scale=height/1080
    im=Image.new("RGBA",(width,height))
    d=ImageDraw.Draw(im)
    expr=next(e for e in EXPRESSIONS if e["label"]=="Consideration")
    label=ImageFont.truetype(str(fp/"jost-latin-500-normal.ttf"),round(18*scale))
    phrase=ImageFont.truetype(str(fp/"cormorant-garamond-latin-700-italic.ttf"),round(41*scale))
    x=width*.5
    half=label.getlength(expr["label"].upper())*.5+14*scale
    canonical=tuple(int(expr["color"][j:j+2],16) for j in (1,3,5))
    d.rounded_rectangle((x-half,height*.085-15*scale,x+half,height*.085+15*scale),
        radius=15*scale,fill=(61,19,45,125),outline=canonical+(180,),width=max(1,round(scale)))
    d.text((x,height*.085),expr["label"].upper(),font=label,anchor="mm",fill=expr["color"])
    for i,line in enumerate(expr["lines"]):
        d.text((x,height*(.13+.043*i)),line,font=phrase,anchor="mm",fill="#fff0d4")
    glow=im.filter(ImageFilter.GaussianBlur(4*scale))
    glow.putalpha(glow.getchannel("A").point(lambda a:int(a*.28)))
    title=Image.alpha_composite(glow,im)
    sig=Image.new("RGBA",(width,height))
    logo=logo_image(height=max(20,round(46*scale)))
    sig.alpha_composite(logo,(round(30*scale),height-round(76*scale)))
    return title,sig


def frame(renderer,global_index,fps=60):
    from PIL import Image
    import numpy as np
    if int(fps)!=renderer.kit_fps:
        raise ValueError("Frame rate must match the renderer initialized rate.")
    t=float(global_index)/fps
    renderer.p3d._frame=None
    renderer.p3d.shutter=0 if any(0<=t-cut<renderer.kit_shutter/fps for cut in renderer.kit_cuts) else renderer.kit_shutter
    try:
        raw=renderer.out.frame(t,global_index)
    finally:
        renderer.p3d.shutter=renderer.kit_shutter
    if renderer.kit_scene=="model_atlas":
        return raw
    im=Image.frombytes("RGB",(renderer.w,renderer.h),raw).convert("RGBA")
    title,sig=renderer.kit_overlay
    im=Image.alpha_composite(im,sig)
    u=float(np.clip((t-12.6)/.9,0,1));u=u*u*(3-2*u)
    if u>0:
        over=title.copy();over.putalpha(title.getchannel("A").point(lambda a:int(a*u)))
        im=Image.alpha_composite(im,over)
    return im.convert("RGB").tobytes()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--width",type=int,default=1920);ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--fps",type=int,choices=(30,60),default=60)
    ap.add_argument("--samples",type=int,default=2)
    ap.add_argument("--stills",help="Comma-separated seconds")
    ap.add_argument("--range",nargs=2,type=int,metavar=("START","END"))
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if not a.stills and a.range is None:ap.error("Choose --stills or --range")
    began=time.monotonic()
    r=make_renderer(a.width,a.height,a.samples,a.fps)
    print(json.dumps({"event":"initialized","seconds":round(time.monotonic()-began,3),"renderer":r.ctx.info["GL_RENDERER"]}),flush=True)
    if a.stills:
        from PIL import Image
        a.out.mkdir(parents=True,exist_ok=True)
        for t in map(float,a.stills.split(",")):
            start=time.monotonic();i=round(t*a.fps)
            dest=a.out/f"t{t:06.2f}.png"
            Image.frombytes("RGB",(a.width,a.height),frame(r,i,a.fps)).save(dest)
            print(json.dumps({"path":str(dest),"seconds":round(time.monotonic()-start,3)}),flush=True)
        import songs.consideration as s
        (a.out/"contact-evidence.json").write_text(json.dumps([s.pair().evidence(t) for t in [4.8,5.3,6,6.5,7,7.5,8]],indent=2)+"\n")
        return
    start,end=a.range
    if not (0<=start<end<=round(DURATION*a.fps)):ap.error("Range is outside the study")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    tmp=a.out.with_suffix(".assembling.mp4")
    cmd=["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{a.width}x{a.height}",
        "-r",str(a.fps),"-i","-","-vf","scale=out_color_matrix=bt709:out_range=tv", "-c:v","libx264",
        "-threads","2","-preset","medium","-crf","17","-pix_fmt","yuv420p","-color_primaries","bt709",
        "-color_trc","bt709","-colorspace","bt709","-color_range","tv","-movflags","+faststart",str(tmp)]
    ff=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    identity=source_hashes()
    try:
        for i in range(start,end):
            if (a.out.parent/"STOP").exists():raise RuntimeError("STOP requested")
            ff.stdin.write(frame(r,i,a.fps))
            if (i-start)%30==0:print(json.dumps({"frame":i,"elapsed":round(time.monotonic()-began,2)}),flush=True)
    except BaseException:
        ff.kill();ff.wait();raise
    finally:
        if ff.stdin and not ff.stdin.closed:ff.stdin.close()
    if ff.wait():raise RuntimeError("Encoder failed")
    if identity!=source_hashes():raise RuntimeError("Source changed during render; incomplete media retained")
    tmp.replace(a.out)
    receipt={"start":start,"end":end,"fps":a.fps,"width":a.width,"height":a.height,"samples":a.samples,
             "sha256":digest(a.out),"source_hashes":identity,"color":COLOR_CONTRACT,"elapsed":time.monotonic()-began}
    a.out.with_suffix(".json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"event":"done","path":str(a.out),"seconds":receipt["elapsed"]}),flush=True)


if __name__=="__main__":main()
