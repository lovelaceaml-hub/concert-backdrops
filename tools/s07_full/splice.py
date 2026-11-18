"""Replace short frame ranges of the rendered parts with re-rendered patches (cloud only).

    python tools/s07_full/splice.py PARTDIR PATCHDIR OUTDIR

PARTDIR holds part0.mp4 .. partN.mp4 from render_parts.sh (8 parts of 7,846 frames); PATCHDIR holds
p<first frame>.mp4 files and ranges.txt ("first last" per line, last exclusive). OUTDIR gets numbered pieces
seg000.mp4 ... in play order, ready for finish.sh. No em dash or en dash anywhere in this file.
"""
from pathlib import Path
import subprocess
import sys

TOTAL, PARTS = 7846, 8


def cut(src, a, b, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf",
                    f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS", "-an", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", "-r", "30", str(dst)], check=True)


def main():
    parts, patches, out = (Path(x) for x in sys.argv[1:4])
    out.mkdir(parents=True, exist_ok=True)
    ranges = sorted(tuple(map(int, line.split())) for line in (patches / "ranges.txt").read_text().split("\n")
                    if line.strip())
    bounds = [TOTAL * i // PARTS for i in range(PARTS + 1)]
    pieces = []          # (kind, file, first frame in file, last frame in file)
    pos = 0
    for a, b in ranges + [(TOTAL, TOTAL)]:
        while pos < a:
            k = max(i for i in range(PARTS) if bounds[i] <= pos)
            end = min(a, bounds[k + 1])
            pieces.append((parts / f"part{k}.mp4", pos - bounds[k], end - bounds[k]))
            pos = end
        if a < TOTAL:
            pieces.append((patches / f"p{a}.mp4", 0, None))
            pos = b
    n = 0
    for i, (src, a, b) in enumerate(pieces):
        dst = out / f"seg{i:03d}.mp4"
        if b is None:
            subprocess.run(["cp", str(src), str(dst)], check=True)
        else:
            cut(src, a, b, dst)
        got = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=nb_read_frames",
                                  "-of", "csv=p=0", str(dst)], capture_output=True, text=True).stdout.strip())
        n += got
        print(dst.name, src.name, a, b, got, flush=True)
    print("total frames", n)


if __name__ == "__main__":
    main()
