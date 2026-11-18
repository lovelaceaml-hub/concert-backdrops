"""Song 05 version 2: the last pass over the joined picture, the bottom third held calm once more.

The 2D layer (overlay05.Overlay._calm) already softens the water under the people. This pass, run once on the
joined video, also holds down thin bright lines there (the rings of the waves of peace where they cross the
near water), so the bottom third has no bright reflections, rings or particles (brief, Never 9). It changes
nothing above 0.67 of the frame height, so the words, the people and the signature are untouched.

    python tools/s05_full2/post05.py joined.mp4 stage.mp4 [--crf 16]
No em dash or en dash anywhere in this file.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d

sys.path.insert(0, str(Path(__file__).resolve().parent))
import timing  # noqa: E402

W, H = 1920, 1080


def _ss(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


Y0 = int(0.665 * H)
YY = (np.arange(Y0, H, dtype=np.float32) / H)[:, None, None]
K = 0.95 * _ss(0.668, 0.70, YY)


def calm(frame):
    """Each pixel of the near water is held to a little above the smaller of its vertical and horizontal
    neighbourhood averages: a thin bright line in either direction (a ring, a glint, a streak) is flattened into
    the water, while the soft colour of the water itself stays."""
    reg = frame[Y0:].astype(np.float32) / 255.0
    lum = reg.mean(axis=2)
    v = uniform_filter1d(lum, 61, axis=0, mode="nearest")
    h = uniform_filter1d(lum, 61, axis=1, mode="nearest")
    ref = np.minimum(v, h)
    over = np.maximum(lum - (ref + 0.012), 0.0)[..., None]
    out = reg - over * K
    frame[Y0:] = (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--crf", default="16")
    a = ap.parse_args()
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(a.src), "-vf",
                            "scale=in_color_matrix=bt709:in_range=tv:out_range=full:flags=accurate_rnd+full_chroma_int,format=rgb24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(timing.FPS), "-i", "-", "-vf",
                            "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p",
                            "-c:v", "libx264", "-preset", "medium", "-crf", a.crf, "-pix_fmt", "yuv420p", "-g", "120",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-color_range", "tv", "-an", "-movflags", "+faststart", str(a.dst)],
                           stdin=subprocess.PIPE)
    n = 0
    size = W * H * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        enc.stdin.write(calm(f).tobytes())
        n += 1
    enc.stdin.close()
    if enc.wait() or dec.wait():
        raise SystemExit("post pass failed")
    print(f"post pass: {n} frames -> {a.dst}")


if __name__ == "__main__":
    main()
