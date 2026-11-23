"""Render a song made on the song kit: stills or a range of frames (cloud CPU only; never on the Mac).

    python tools/song_kit/prepare.py <song> [--audio file]
    python tools/song_kit/render.py <song> --stills 0,12.5,40 --scale 0.5 [--outdir DIR]
    python tools/song_kit/render.py <song> --range 0 600 --out part.mp4 [--fps 60]

Frames are 60 fps; frame i shows song time i/60 - PICTURE_DELAY (Song 11 review f20: the measured hit times sit
about 0.1 s before the audible attack). Everything is a pure function of time, so ranges render in parallel in
any order. The song is tools/song_kit/songs/<song>/ (song_data.py and its own sets). No em dash or en dash.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
import prepare as r3  # noqa: E402  (the pinned Film 10 engine and Claude Final v1)

PICTURE_DELAY = 0.1


def work(song):
    return ROOT / "work/song_kit" / song


def load(song, fps=60):
    snap = r3.SNAPSHOT
    w = work(song)
    if not (snap / "engine/render.py").exists() or not (w / "features.npz").exists():
        raise SystemExit(f"Run tools/song_kit/prepare.py {song} first.")
    here = KIT / "songs" / song
    if not (here / "song_data.py").exists():
        raise SystemExit(f"No song {song}: expected {here}/song_data.py")
    os.environ.update(SONG="kit_film", OUT_FPS=str(fps), OUT_RES="1080p",
                      FEATURES=str(w / "features.npz"), AUDIO=str(w / "score.wav"),
                      LIBGL_ALWAYS_SOFTWARE="1", LP_NUM_THREADS=os.environ.get("LP_NUM_THREADS", "1"),
                      OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                      NUMBA_CACHE_DIR=str(w / "numba"), MESA_SHADER_CACHE_DIR=str(w / "mesa"),
                      P3D_CACHE=os.environ.get("KIT_CACHE", str(w / "p3dcache")))
    sys.path.insert(0, str(here))                       # song_data and the song's own sets
    sys.path.insert(0, str(KIT))                        # kit_cards
    sys.path.insert(0, str(snap / "engine"))
    import songs
    songs.__path__.append(str(KIT / "modules"))         # songs.kit_film, kit_light, kit_words, kit_love
    songs.__path__.append(str(here))                    # the song's own sets, as songs.<name>
    import p3d
    p3d.__path__.append(str(ROOT / "engine/p3d"))       # the repo's brand modules (globe, logo, hearts)
    import song  # noqa: F401  (loads songs.kit_film)
    spec = importlib.util.spec_from_file_location("reference_renderer", snap / "engine/render.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    spec = importlib.util.spec_from_file_location("titles", ROOT / "engine/titles.py")
    titles = importlib.util.module_from_spec(spec)
    sys.modules["titles"] = titles
    spec.loader.exec_module(titles)
    from kit_cards import Cards

    class Renderer(old.Renderer):
        def __init__(self, w=1920, h=1080):
            super().__init__(w, h)
            self.cards = Cards(self)

        def frame(self, t, index=0):
            data = super().frame(t, index)
            if self.cards.overlay(t):
                return self.f_out.read(components=3)
            return data

    return Renderer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--stills", default="")
    ap.add_argument("--outdir", type=Path)
    ap.add_argument("--range", type=int, nargs=2)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--crf", default="14")
    ap.add_argument("--fps", type=int, default=60, help="60 for the final, 30 for drafts")
    ap.add_argument("--samples", type=int, default=0, help="temporal samples (0: the engine default)")
    args = ap.parse_args()
    if sys.platform == "darwin":
        raise SystemExit("The song kit renders on cloud CPU only (owner rule).")
    fps = args.fps
    Renderer = load(args.song, fps)
    w, h = int(1920 * args.scale) // 2 * 2, int(1080 * args.scale) // 2 * 2
    renderer = Renderer(w, h)
    if args.samples and getattr(renderer, "p3d", None) is not None:
        renderer.p3d.samples = args.samples

    def frame(t):
        return renderer.out.frame(t, int(round(t * fps)))

    if args.stills:
        from PIL import Image
        outdir = args.outdir or work(args.song) / "stills"
        outdir.mkdir(parents=True, exist_ok=True)
        for t in map(float, args.stills.split(",")):
            start = time.process_time()
            data = frame(t)
            Image.frombytes("RGB", (w, h), data).save(outdir / f"t{t:07.2f}.png")
            print(f"{t:.3f}: {time.process_time() - start:.2f} CPU s", flush=True)
        return
    if args.range is None or args.out is None:
        ap.error("Use --stills or --range A B --out file.mp4")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-c:v", "libx264", "-threads", "1", "-preset", "medium", "-crf", args.crf,
           "-pix_fmt", "yuv420p", "-g", str(fps * 2), "-color_primaries", "bt709",
           "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", str(args.out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    start = time.time()
    try:
        for i in range(*args.range):
            ff.stdin.write(frame(max(0.0, i / fps - PICTURE_DELAY)))
            if (i - args.range[0]) % (5 * fps) == 0:
                print(f"frame {i}: {time.time() - start:.1f} s", flush=True)
    finally:
        ff.stdin.close()
    if ff.wait():
        raise SystemExit("Encoder failed")
    print(f"done {args.out}: {time.time() - start:.1f} s", flush=True)


if __name__ == "__main__":
    main()
