"""Song 03 full backdrop: render every frame in parallel parts, join, add the music, make the two delivery files.

    python tools/s03_full/export.py --workers 4 --parts 16

Parts go to work/s03_full/parts (a finished part is kept and reused if its log says done), the deliveries to
out/s03_full/. Master: H.264 CRF 18, yuv420p, AAC 320k, faststart. Share copy: 1280x720 under 25 MB.
No em dash or en dash anywhere in this file.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s03_full"
OUT = ROOT / "out/s03_full"
NFRAMES = 11103          # 370.1 s at 30 fps: the song (355.09 s), then the 15 second hold
NAME = "03 I Reminisce About Your Love - Backdrop"


def part(job):
    k, a, b = job
    out = WORK / f"parts/p{k:02d}.mp4"
    log = WORK / f"parts/p{k:02d}.log"
    if out.exists() and log.exists() and "done" in log.read_text():
        return k, "kept"
    with open(log, "w") as fh:
        r = subprocess.run([sys.executable, str(ROOT / "tools/s03_full/render.py"), "--range", str(a), str(b),
                            "--out", str(out)], stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode:
        raise SystemExit(f"part {k} failed, see {log}")
    return k, "rendered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--parts", type=int, default=16)
    args = ap.parse_args()
    (WORK / "parts").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    edges = [round(i * NFRAMES / args.parts) for i in range(args.parts + 1)]
    jobs = [(k, edges[k], edges[k + 1]) for k in range(args.parts)]
    # interleave heavy (plate) and light (procedural) parts by starting from both ends
    order = [jobs[i // 2] if i % 2 == 0 else jobs[-1 - i // 2] for i in range(len(jobs))]
    with ThreadPoolExecutor(args.workers) as pool:
        for k, how in pool.map(part, order):
            print(f"part {k:02d} {how}", flush=True)
    lst = WORK / "parts/list.txt"
    lst.write_text("".join(f"file 'p{k:02d}.mp4'\n" for k, _, _ in jobs))
    joined = WORK / "joined.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(joined)], check=True)
    master = OUT / f"{NAME} 1080p30.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", str(WORK / "score.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-color_range", "tv", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                    "-frames:v", str(NFRAMES), "-movflags", "+faststart", str(master)], check=True)
    share = OUT / f"{NAME} share 720p.mp4"
    vb = "380k"
    common = ["-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-b:v", vb,
              "-pix_fmt", "yuv420p", "-frames:v", str(NFRAMES)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), *common, "-pass", "1",
                    "-passlogfile", str(WORK / "pass"), "-an", "-f", "mp4", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), *common, "-pass", "2",
                    "-passlogfile", str(WORK / "pass"), "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
                    str(share)], check=True)
    for f in (master, share):
        print(f, f.stat().st_size / 1e6, "MB")


if __name__ == "__main__":
    main()
