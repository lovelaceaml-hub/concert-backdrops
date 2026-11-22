"""Native cloud CPU renderer for the isolated procedural model prototypes.

Run with PYTHONHASHSEED=0. A silent proof is a technical and visual prototype,
not an approved song design. Outputs and caches remain in ignored work files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/concert-addons"
DURATION = 6.0
COLOR_CONTRACT = {"name": "legacy_display_gamma", "input": "rgb24",
                  "encode_matrix": "bt709", "encode_range": "limited",
                  "primaries": "bt709", "transfer_tag": "bt709", "transfer_conversion": False}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    paths = set((ROOT / "tools/concert_addons").glob("*.py"))
    paths.update((ROOT / "engine").rglob("*.py"))
    paths.update((ROOT / "fonts").glob("*.ttf"))
    paths.update([ROOT / "pyproject.toml", ROOT / "uv.lock"])
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths) if p.is_file()}


def make_renderer(width=1920, height=1080, temporal_samples=2, fps=60, scene="flight"):
    if sys.platform == "darwin":
        raise RuntimeError("This prototype is configured for cloud CPU rendering.")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Start Python with PYTHONHASHSEED=0.")
    if scene not in ("flight", "rose", "wheat"):
        raise ValueError("Unknown prototype scene")
    if temporal_samples not in (1, 2, 3, 4) or fps not in (30, 60):
        raise ValueError("Use 1 to 4 temporal samples and 30 or 60 native frames per second.")
    fonts = ROOT / "fonts"
    if not (fonts / "cormorant-garamond-latin-700-italic.ttf").is_file():
        raise RuntimeError("Prepare the pinned repository fonts before rendering.")
    WORK.mkdir(parents=True, exist_ok=True)
    os.environ.update(SONG="prototype_scene", CONCERT_ADDONS_SCENE=scene, OUT_FPS=str(fps),
        OUT_RES="4k" if width == 3840 else "1080p", LIBGL_ALWAYS_SOFTWARE="1",
        LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
        NUMBA_CACHE_DIR=str(WORK / "numba"), MESA_SHADER_CACHE_DIR=str(WORK / "mesa"),
        P3D_CACHE=str(WORK / "p3d-cache"))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "engine"))
    import songs
    songs.__path__.append(str(ROOT / "tools/concert_addons"))
    import song
    song.ROOT = str(fonts.parent)
    import render as legacy
    import text as typography
    typography.FONTS = str(fonts)
    for key, name in {"F_PHRASE": "cormorant-garamond-latin-700-italic.ttf",
                      "F_TITLE": "cormorant-garamond-latin-700-normal.ttf",
                      "F_LABEL": "jost-latin-500-normal.ttf",
                      "F_TAG": "cormorant-garamond-latin-600-italic.ttf"}.items():
        setattr(typography, key, str(fonts / name))
    import shaders
    shaders.COMP_FS = shaders.COMP_FS.replace("col += (n1+n2-1.0)*(1.15/255.0);", "// No added grain.")
    renderer = legacy.Renderer(width, height)
    renderer.p3d.samples = int(temporal_samples)
    renderer.p3d.draft = False
    renderer.addons_fps = fps
    renderer.addons_scene = scene
    original = renderer.p3d.adjust
    def adjust(t, p):
        p = original(t, p)
        p["bloom_gain"] = p.get("bloom_gain", 1.0)*.65
        return p
    renderer.p3d.adjust = adjust
    return renderer


def frame(renderer, index, fps=60):
    if fps != renderer.addons_fps:
        raise ValueError("Frame rate must match the initialized renderer.")
    renderer.p3d._frame = None
    return renderer.out.frame(float(index)/fps, int(index))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scene", choices=("flight", "rose", "wheat"), default="flight")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, choices=(30, 60), default=60)
    ap.add_argument("--samples", type=int, choices=(1, 2, 3, 4), default=2)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--stills", help="Comma-separated absolute seconds")
    group.add_argument("--range", nargs=2, type=int, metavar=("START", "END"))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    began = time.monotonic()
    identity = source_hashes()
    r = make_renderer(a.width, a.height, a.samples, a.fps, a.scene)
    print(json.dumps({"event": "initialized", "seconds": round(time.monotonic()-began, 3),
                      "renderer": r.ctx.info["GL_RENDERER"]}), flush=True)
    receipt = {"scene": a.scene, "fps": a.fps, "width": a.width, "height": a.height,
               "samples": a.samples, "source_hashes": identity, "color": COLOR_CONTRACT,
               "renderer": r.ctx.info["GL_RENDERER"], "owner_approval": "pending"}
    if a.stills:
        from PIL import Image
        a.out.mkdir(parents=True, exist_ok=True)
        receipt["frames"] = []
        for t in map(float, a.stills.split(",")):
            if not 0 <= t <= DURATION:
                ap.error("Still time is outside the six-second prototype")
            start = time.monotonic()
            path = a.out / f"{a.scene}-t{t:06.2f}.png"
            Image.frombytes("RGB", (a.width, a.height), frame(r, round(t*a.fps), a.fps)).save(path)
            record = {"path": str(path), "sha256": digest(path), "time": t,
                      "seconds": round(time.monotonic()-start, 3)}
            receipt["frames"].append(record)
            print(json.dumps(record), flush=True)
        receipt_path = a.out / (a.scene+"-receipt.json")
    else:
        start, end = a.range
        if not 0 <= start < end <= round(DURATION*a.fps):
            ap.error("Frame range is outside the six-second prototype")
        a.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = a.out.with_suffix(".assembling.mp4")
        filters = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
               "-video_size", f"{a.width}x{a.height}", "-framerate", str(a.fps), "-i", "-",
               "-vf", filters, "-c:v", "libx264", "-threads", "1", "-preset", "medium",
               "-crf", "17", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
               "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off:rc-lookahead=10",
               "-movflags", "+faststart+write_colr", str(tmp)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for i in range(start, end):
                if (WORK / "STOP").exists():
                    raise RuntimeError("Prototype STOP requested")
                ff.stdin.write(frame(r, i, a.fps))
                if (i-start) % 30 == 0:
                    print(json.dumps({"frame": i, "elapsed": round(time.monotonic()-began, 2)}), flush=True)
        except BaseException:
            ff.kill(); ff.wait()
            raise
        finally:
            if ff.stdin and not ff.stdin.closed:
                ff.stdin.close()
        if ff.wait():
            raise RuntimeError("Encoder failed")
        if source_hashes() != identity:
            raise RuntimeError("Source changed during render; assembling file is not delivered")
        tmp.replace(a.out)
        receipt.update(start=start, end=end, sha256=digest(a.out), path=str(a.out))
        receipt_path = a.out.with_suffix(".json")
    if source_hashes() != identity:
        raise RuntimeError("Source changed during render; receipt was not finalized")
    receipt.update(seconds=round(time.monotonic()-began, 3),
                   maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    receipt_path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps({"event": "done", "receipt": str(receipt_path), "seconds": receipt["seconds"],
                      "maxrss_kib": receipt["maxrss_kib"]}), flush=True)


if __name__ == "__main__":
    main()
