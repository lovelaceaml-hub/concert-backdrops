"""Render song 05's full backdrop in parallel parts, join them and add the music (then 15 s of silence).

    python tools/s05_full/export05.py --audio <s05.m4a> --workers 4 --parts 12 --outdir out/s05_full
    python tools/s05_full/export05.py --audio <s05.m4a> --join-only --outdir out/s05_full

Writes, in --outdir:
    parts/part_NN.mp4                       H.264 CRF 18 pieces (same settings, joined without re-encoding)
    05 God Bless You! - Backdrop 1080p30.mp4   master: 1920x1080 30 fps, H.264 CRF 18, yuv420p, AAC 320k, faststart
    05 God Bless You! - Backdrop 720p (share).mp4   1280x720, under 25 MB
A part that already exists and is complete is kept (delete it to render it again).
Cloud only. Never commit the outputs. No em dash or en dash anywhere in this file.
"""
import argparse
import concurrent.futures as cf
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NFRAMES = 5045
FPS = 30
MASTER = "05 God Bless You! - Backdrop 1080p30.mp4"
SHARE = "05 God Bless You! - Backdrop 720p (share).mp4"


def frames_in(path):
    if not path.exists():
        return -1
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return -1


def render_part(audio, a, b, out, log):
    if frames_in(out) == b - a:
        return out, "kept"
    cmd = [sys.executable, str(HERE / "render05.py"), "--audio", str(audio), "--range", str(a), str(b),
           "--out", str(out), "--crf", "18"]
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode or frames_in(out) != b - a:
        raise RuntimeError(f"part {out.name} failed (see {log})")
    return out, "rendered"


def join(audio, outdir):
    parts = sorted((outdir / "parts").glob("part_*.mp4"))
    lst = outdir / "parts.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    video = outdir / "video_only.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(video)], check=True)
    total = NFRAMES / FPS
    master = outdir / MASTER
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(audio), "-filter_complex",
                    f"[1:a]aresample=48000,apad=whole_dur={total:.4f}[a]", "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ac", "2", "-t", f"{total:.4f}",
                    "-movflags", "+faststart", str(master)], check=True)
    # share copy: two-pass to stay under 25 MB
    share = outdir / SHARE
    vbr = int((24.0 * 8e6 / total - 128e3) * 0.97)
    common = ["-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
              "-pix_fmt", "yuv420p", "-g", "60"]
    passlog = str(outdir / "share2pass")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master)] + common +
                   ["-pass", "1", "-passlogfile", passlog, "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master)] + common +
                   ["-pass", "2", "-passlogfile", passlog, "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                    str(share)], check=True)
    for p in (master, share):
        print(f"{p.name}: {p.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=ROOT / "out/s05_full")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--parts", type=int, default=12)
    ap.add_argument("--join-only", action="store_true")
    args = ap.parse_args()
    audio = args.audio.resolve()
    (args.outdir / "parts").mkdir(parents=True, exist_ok=True)
    if not args.join_only:
        edges = [round(NFRAMES * k / args.parts) for k in range(args.parts + 1)]
        jobs = []
        with cf.ThreadPoolExecutor(args.workers) as ex:
            for k in range(args.parts):
                out = args.outdir / "parts" / f"part_{k:02d}.mp4"
                log = args.outdir / "parts" / f"part_{k:02d}.log"
                jobs.append(ex.submit(render_part, audio, edges[k], edges[k + 1], out, log))
            for j in cf.as_completed(jobs):
                out, how = j.result()
                print(out.name, how, flush=True)
        (args.outdir / "edges.json").write_text(json.dumps(edges))
    join(audio, args.outdir)


if __name__ == "__main__":
    main()
