"""Native 1080p60 cloud CPU rendering with exact reusable source identity."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from tools.concert_kit.render import COLOR_CONTRACT,digest,fonts_path

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"work/advanced-dance"
DURATION=32.0
FPS=60
SOURCE_START=0.0


def cut_times(mode):
    clock=json.loads((ROOT/"tools/advanced_dance/clock.json").read_text())
    return tuple(round(clock[mode]["beat_seconds"][b]*60)/60 for b in (16,32,48))


def source_hashes():
    names=("__init__.py","score.py","anatomy.py","costume.py","cache.py","props.py",
           "lights.py","scene.py","song_dance.py","render.py","solo.py","ensemble.py","clock.json")
    paths={ROOT/"tools/advanced_dance"/n for n in names}
    paths.update((ROOT/"engine").rglob("*.py"))
    for folder in ("tools/concert_kit","tools/concert_fan","tools/cinematic_ten"):
        paths.update((ROOT/folder).glob("*.py"))
    paths.update(ROOT/n for n in ("assets/p3d/body_v1.npz","assets/p3d/brand/land_2048.png","pyproject.toml","uv.lock"))
    result={str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}
    result.update({"fonts/"+p.name:digest(p) for p in sorted(fonts_path().glob("*.ttf"))})
    return result


def make_renderer(width=1920,height=1080,temporal_samples=2,fps=60,mode="solo"):
    if sys.platform=="darwin":
        raise RuntimeError("This production uses cloud CPU rendering")
    if os.environ.get("PYTHONHASHSEED")!="0":
        raise RuntimeError("Set PYTHONHASHSEED=0 before Python starts")
    if mode not in ("solo","ensemble") or fps not in (30,60):
        raise ValueError("Expected solo or ensemble and 30 or 60 fps")
    if "P3D_BODY_ASSET" in os.environ or "song" in sys.modules:
        raise RuntimeError("Use the declared original rig and an isolated scene process")
    identity=source_hashes()
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:20]
    WORK.mkdir(parents=True,exist_ok=True)
    os.environ.update(SONG="song_dance",ADVANCED_DANCE_MODE=mode,OUT_FPS=str(fps),
        OUT_RES="4k" if width==3840 else "1080p",LIBGL_ALWAYS_SOFTWARE="1",
        LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS","1"),OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",
        NUMBA_CACHE_DIR=str(WORK/"numba"),MESA_SHADER_CACHE_DIR=str(WORK/"mesa"),P3D_CACHE=str(WORK/"p3d-cache"/key))
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"engine"))
    import songs
    songs.__path__.append(str(ROOT/"tools/advanced_dance"))
    import song
    fp=fonts_path();song.ROOT=str(fp.parent)
    import render as legacy
    import text as typography
    typography.FONTS=str(fp)
    for key,name in {"F_PHRASE":"cormorant-garamond-latin-700-italic.ttf",
        "F_TITLE":"cormorant-garamond-latin-700-normal.ttf","F_LABEL":"jost-latin-500-normal.ttf",
        "F_TAG":"cormorant-garamond-latin-600-italic.ttf"}.items():
        setattr(typography,key,str(fp/name))
    import shaders
    shaders.COMP_FS=shaders.COMP_FS.replace("col += (n1+n2-1.0)*(1.15/255.0);","// No added delivery grain.")
    renderer=legacy.Renderer(width,height)
    renderer.p3d.samples=int(temporal_samples)
    renderer.p3d.draft=False
    renderer.dance_fps=fps
    renderer.dance_cuts=cut_times(mode)
    from tools.cinematic_ten.render import _signature
    renderer.dance_signature=_signature(width,height)
    original=renderer.p3d.adjust
    def adjust(t,params):
        params=original(t,params)
        params["bloom_gain"]=params.get("bloom_gain",1)*.58
        return params
    renderer.p3d.adjust=adjust
    return renderer


def frame(renderer,global_index,fps=60):
    from PIL import Image
    if fps!=renderer.dance_fps:
        raise ValueError("Delivery fps must match initialized renderer")
    t=float(global_index)/fps
    renderer.p3d._frame=None
    shutter=renderer.p3d.shutter
    if any(0<=t-cut<shutter/fps for cut in renderer.dance_cuts):
        renderer.p3d.shutter=0
    try:
        raw=renderer.out.frame(t,global_index)
    finally:
        renderer.p3d.shutter=shutter
    im=Image.frombytes("RGB",(renderer.w,renderer.h),raw).convert("RGBA")
    return Image.alpha_composite(im,renderer.dance_signature).convert("RGB").tobytes()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("solo","ensemble"),required=True)
    p.add_argument("--stills")
    p.add_argument("--start-frame",type=int,default=0)
    p.add_argument("--end-frame",type=int,default=1920)
    p.add_argument("--width",type=int,default=1920)
    p.add_argument("--height",type=int,default=1080)
    p.add_argument("--samples",type=int,default=2)
    p.add_argument("--fps",type=int,default=60,choices=(30,60))
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    from PIL import Image
    began=time.monotonic()
    r=make_renderer(a.width,a.height,a.samples,a.fps,a.mode)
    print(json.dumps(dict(event="initialized",mode=a.mode,seconds=round(time.monotonic()-began,3),renderer=r.ctx.info["GL_RENDERER"])),flush=True)
    a.out.mkdir(parents=True,exist_ok=True)
    ids=[round(float(t)*a.fps) for t in a.stills.split(",")] if a.stills else range(a.start_frame,a.end_frame)
    for i in ids:
        path=a.out/(f"t{i/a.fps:07.3f}.png" if a.stills else f"{i:06d}.png")
        if path.is_file():
            continue
        began=time.monotonic()
        im=Image.frombytes("RGB",(a.width,a.height),frame(r,i,a.fps))
        temp=path.with_suffix(".partial.png");im.save(temp,compress_level=3);temp.replace(path)
        if a.stills or i%30==0:
            print(json.dumps(dict(file=str(path),seconds=round(time.monotonic()-began,3))),flush=True)


if __name__=="__main__":
    main()
