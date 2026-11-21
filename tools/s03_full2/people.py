"""Song 03 backdrop v2: render the people of the two expressions (tools/s03_full2/s03_people.py) on black with the
approved tag's own engine, as numbered PNG frames for overlay2.py. CPU only, in this cloud session.

    python tools/s03_full2/people.py --stills 30,228            # check stills in work/s03_full2/people_stills
    python tools/s03_full2/people.py --part 0 4                  # part 0 of 4 of every frame in the windows

Frames are written to work/s03_full2/people/fNNNNN.png (NNNNN = the stage video's 60 fps frame index), at
SCALE of 1920x1080; overlay2.py scales and places them. No em dash or en dash anywhere in this file.
"""
import argparse
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / "work/s03_full2"
SCALE = 0.6
FPS = 60


def load():
    os.environ.update(SONG="s03_people", OUT_FPS="60", OUT_RES="1080p", FEATURES=str(WORK / "features.npz"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                      OMP_NUM_THREADS="1", NUMBA_CACHE_DIR=str(WORK / "numba_people"),
                      MESA_SHADER_CACHE_DIR=str(WORK / "mesa_people"))
    sys.path.insert(0, str(ROOT / "engine"))
    sys.path.insert(1, str(HERE))
    import songs
    songs.__path__.append(str(HERE))
    import song as S
    import render as engine_render
    return engine_render.Renderer, S


def frames():
    sys.path.insert(0, str(HERE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_win", HERE / "people_windows.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = []
    for a, b in m.WINDOWS:
        out += list(range(int(a * FPS), int(b * FPS) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--part", type=int, nargs=2)
    a = ap.parse_args()
    from PIL import Image
    if a.part:
        todo = frames()
        k, n = a.part
        todo = todo[k::n]
        outdir = WORK / "people"
        todo = [i for i in todo if not (outdir / f"f{i:05d}.png").exists()]
    else:
        todo = [int(round(float(s) * FPS)) for s in a.stills.split(",")]
        outdir = WORK / "people_stills"
    outdir.mkdir(parents=True, exist_ok=True)
    Renderer, S = load()
    w, h = int(1920 * SCALE) // 2 * 2, int(1080 * SCALE) // 2 * 2
    R = Renderer(w, h)
    t0 = time.time()
    for j, i in enumerate(todo):
        buf = R.out.frame(i / FPS, i)
        tmp = outdir / f".f{i:05d}.png"
        Image.frombytes("RGB", (w, h), buf).save(tmp, compress_level=3)
        tmp.rename(outdir / f"f{i:05d}.png")
        if j % 30 == 0:
            el = time.time() - t0
            print(f"people frame {i} ({j + 1}/{len(todo)})  {el / (j + 1):.2f}s/frame", flush=True)
    print("people done", len(todo), f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
