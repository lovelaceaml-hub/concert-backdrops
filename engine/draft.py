"""Draft mode: the whole song, fast and small, to judge timing and layout (not for showing anyone).

  python draft.py --range 0 225 --out part0.mp4          frames 0 to 224 of the draft (15 fps, 640x360)
  python draft.py --sheet draft.mp4 --out sheet.jpg       a labelled contact sheet of a finished draft

The flag: DRAFT=1 in the environment (this script sets it). Any layer can read it and draw less:

  import draft
  if draft.DRAFT: ...                 # True in a draft render
  n = draft.n(4200)                   # a particle count, cut to the draft share (DRAFT_PARTICLES, default 0.5)

Without any change in the layers, apply() (called once on the built renderer) already cuts every particle layer
(stars, motes, lanterns, petals, words, figures, snow, fragment sparks, and any new one) to that share by drawing
only the first part of each vertex buffer; the seeds are random, so the part drawn is an even sample. A layer whose
buffer is in a meaningful order (a rigged figure's body parts, a symbol's strokes) keeps it whole by putting
draft_keep=True in the dict that holds its vertex array. The picture is drawn at 640x360, so every full-screen
shader does a ninth of the work. Normal renders are untouched.
"""
import os
import sys

DRAFT = os.environ.get("DRAFT", "") not in ("", "0")
SHARE = float(os.environ.get("DRAFT_PARTICLES", "0.5"))
FPS = 15
W, H = 640, 360


def n(count):
    """A particle count for this render: unchanged normally, cut to the draft share in a draft."""
    return max(1, int(count * SHARE)) if DRAFT else count


def _collect(obj, found, depth=0):
    import moderngl
    if isinstance(obj, moderngl.VertexArray):
        found[id(obj)] = obj
    elif isinstance(obj, dict) and obj.get("draft_keep"):
        return   # an ordered buffer (a rigged figure's body, a symbol's strokes): half of it is not an even sample
    elif depth < 4 and isinstance(obj, dict):
        for v in obj.values():
            _collect(v, found, depth + 1)
    elif depth < 4 and isinstance(obj, (list, tuple)):
        for v in obj:
            _collect(v, found, depth + 1)


def apply(R):
    """Called once when the renderer is built: in a draft, draw only SHARE of every particle buffer.
    Looks at the renderer and at every layer object hung off it that keeps a reference back to it (R.up and
    any later ones)."""
    if not DRAFT or SHARE >= 1.0:
        return 0
    found = {}
    _collect(vars(R), found)
    for obj in list(vars(R).values()):
        if hasattr(obj, "__dict__") and getattr(obj, "R", None) is R:
            _collect(vars(obj), found)
    k = 0
    for vao in found.values():
        if vao.vertices > 64:   # full-screen quads have 4 vertices; leave those alone
            vao.vertices = max(1, int(vao.vertices * SHARE))
            k += 1
    print(f"draft: {k} particle layers cut to {SHARE:.0%}", flush=True)
    return k


def render_range(f0, f1, out, crf="27"):
    import subprocess
    import time
    import render
    import song as S
    R = render.Renderer(W, H)
    apply(R)
    total = int(round(S.NFRAMES * FPS / S.FPS))
    f1 = min(f1, total)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", crf, "-pix_fmt", "yuv420p", "-g", "30",
           "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(f0, f1):
        t = i / FPS
        ff.stdin.write(R.out.frame(t, int(round(t * S.FPS))))   # through Output, so a loop song wraps (HOWTO Q)
        if (i - f0) % 60 == 0:
            el = time.time() - t0
            print(f"draft frame {i} ({i - f0}/{f1 - f0})  {el:.0f}s  {el / max(i - f0, 1):.3f}s/frame", flush=True)
    ff.stdin.close()
    ff.wait()
    if ff.returncode != 0:
        sys.exit(f"ffmpeg failed with code {ff.returncode}")
    print(f"draft done {out}: {f1 - f0} frames in {time.time() - t0:.0f}s", flush=True)


def contact_sheet(video, out, cols=6, rows=5, tw=320):
    """A grid of frames spread over the whole video, each labelled with its time."""
    import subprocess
    import numpy as np
    from PIL import Image, ImageDraw
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                video], capture_output=True, text=True).stdout.strip())
    th = tw * 9 // 16
    nimg = cols * rows
    sheet = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for k in range(nimg):
        t = (k + 0.5) * dur / nimg
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf",
                              f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        if len(raw) < tw * th * 3:
            continue
        im = Image.fromarray(np.frombuffer(raw[: tw * th * 3], np.uint8).reshape(th, tw, 3))
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(im, (x, y))
        label = f"{int(t // 60)}:{t % 60:04.1f}"
        d.rectangle((x + 4, y + 4, x + 8 + 7 * len(label), y + 18), fill=(0, 0, 0))
        d.text((x + 6, y + 5), label, fill=(255, 230, 120))
    sheet.save(out, quality=88)
    print("contact sheet", out, sheet.size)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", nargs=2, type=int)
    ap.add_argument("--sheet", default="")
    ap.add_argument("--frames", action="store_true", help="print the number of draft frames for the song")
    ap.add_argument("--out", default="draft.mp4")
    a = ap.parse_args()
    if a.frames:
        import song as S
        print(int(round(S.NFRAMES * FPS / S.FPS)))
    elif a.sheet:
        contact_sheet(a.sheet, a.out)
    else:
        render_range(a.range[0], a.range[1], a.out)


if __name__ == "__main__":
    os.environ["DRAFT"] = os.environ.get("DRAFT", "1") or "1"
    DRAFT = True
    main()
