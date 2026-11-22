"""Song 03 backdrop v2: render every frame in parallel parts on this machine's cores, join them, and make the
three delivery files (never committed: they stay in out/s03_full2/).

    python tools/s03_full2/export.py render --workers 4 --parts 24   # resumable: finished parts are kept
    python tools/s03_full2/export.py deliver

Delivery:
  stage   silent, H.264 CRF 16, yuv420p, faststart, 1920x1080, 60 fps, 328.000 s
  review  the same picture with the conformed reference music (work/s03_full2/score.wav), AAC 320k, CRF 20
  phone   1280x720, 60 fps, with music, two-pass to stay under 25 MB
No em dash or en dash anywhere in this file.
"""
import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / "work/s03_full2"
OUT = ROOT / "out/s03_full2"
FPS = 60
TOTAL = 328.0
NFRAMES = int(round(TOTAL * FPS))
NAME = "03 I Reminisce About Your Love - Backdrop v2"
BT709 = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]


def parts(n):
    step = -(-NFRAMES // n)
    return [(a, min(a + step, NFRAMES)) for a in range(0, NFRAMES, step)]


def render(workers, n):
    pdir = WORK / "parts"
    (WORK / "logs").mkdir(parents=True, exist_ok=True)
    pdir.mkdir(parents=True, exist_ok=True)
    todo = [(k, a, b) for k, (a, b) in enumerate(parts(n)) if not (pdir / f"p{k:02d}.done").exists()]
    print(f"{len(todo)} of {n} parts to render", flush=True)

    def one(job):
        k, a, b = job
        out = pdir / f"p{k:02d}.mkv"
        with open(WORK / "logs" / f"part{k:02d}.log", "w") as log:
            r = subprocess.run([sys.executable, str(HERE / "render.py"), "--range", str(a), str(b), "--out", str(out)],
                               stdout=log, stderr=subprocess.STDOUT)
        if r.returncode == 0:
            (pdir / f"p{k:02d}.done").write_text(f"{a} {b}\n")
        print(f"part {k:02d} ({a} to {b}) {'ok' if r.returncode == 0 else 'FAILED'} {time.strftime('%H:%M:%S')}",
              flush=True)
        return r.returncode

    with ThreadPoolExecutor(workers) as ex:
        codes = list(ex.map(one, todo))
    if any(codes):
        raise SystemExit("some parts failed")


def run(cmd):
    print(" ".join(str(c) for c in cmd[:12]), "...", flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def deliver(n):
    pdir = WORK / "parts"
    OUT.mkdir(parents=True, exist_ok=True)
    lst = WORK / "parts.txt"
    lst.write_text("".join(f"file '{pdir / f'p{k:02d}.mkv'}'\n" for k in range(len(parts(n)))))
    joined = WORK / "joined.mkv"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    stage = OUT / f"{NAME} - stage 1080p60.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-vf", "scale=out_color_matrix=bt709:out_range=tv",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "120",
         *BT709, "-an", "-movflags", "+faststart", stage])
    review = OUT / f"{NAME} - review 1080p60.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", WORK / "score.wav",
         "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "120", *BT709, "-c:a", "aac", "-b:a", "320k",
         "-map", "0:v", "-map", "1:a", "-t", f"{TOTAL}", "-movflags", "+faststart", review])
    phone = OUT / f"{NAME} - phone 720p60.mp4"
    vbit = "470k"
    common = ["-vf", "scale=1280:720:flags=lanczos:out_color_matrix=bt709:out_range=tv", "-c:v", "libx264",
              "-preset", "slow", "-b:v", vbit, "-maxrate", "900k", "-bufsize", "1800k", "-pix_fmt", "yuv420p",
              "-r", str(FPS), "-g", "240", *BT709]
    plog = WORK / "phone2pass"
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, *common, "-pass", "1", "-passlogfile", plog, "-an",
         "-f", "mp4", "/dev/null"])
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", WORK / "score.wav", *common, "-pass", "2",
         "-passlogfile", plog, "-c:a", "aac", "-b:a", "96k", "-map", "0:v", "-map", "1:a", "-t", f"{TOTAL}",
         "-movflags", "+faststart", phone])
    for f in (stage, review, phone):
        print(f, f"{f.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["render", "deliver"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--parts", type=int, default=24)
    a = ap.parse_args()
    if a.what == "render":
        render(a.workers, a.parts)
    else:
        deliver(a.parts)


if __name__ == "__main__":
    main()
