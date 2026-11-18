"""Render song 05's full backdrop (version 2) in parallel parts, join them, and make the three deliverables.

    python tools/s05_full2/export05.py --audio <s05.m4a> --workers 4 --parts 12 --outdir out/s05_full2
    python tools/s05_full2/export05.py --audio <s05.m4a> --join-only --outdir out/s05_full2

Writes, in --outdir:
    parts/part_NN.mp4      H.264 CRF 16 yuv420p 60 fps pieces (identical settings, joined without re-encoding)
    05 God Bless You! - Backdrop v2 - stage 1080p60.mp4    silent, 174.0 s, faststart (the concert file)
    05 God Bless You! - Backdrop v2 - review 1080p60.mp4   the same picture with the reference music conformed
                                                          to the live length (atempo, pitch kept), CRF 20, AAC 320k
    05 God Bless You! - Backdrop v2 - phone 720p60.mp4     with music, under 25 MB
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
sys.path.insert(0, str(HERE))
import timing  # noqa: E402

NFRAMES = timing.NFRAMES
FPS = timing.FPS
STAGE = "05 God Bless You! - Backdrop v2 - stage 1080p60.mp4"
REVIEW = "05 God Bless You! - Backdrop v2 - review 1080p60.mp4"
PHONE = "05 God Bless You! - Backdrop v2 - phone 720p60.mp4"


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
           "--out", str(out), "--crf", "16"]
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode or frames_in(out) != b - a:
        raise RuntimeError(f"part {out.name} failed (see {log})")
    return out, "rendered"


def conformed(audio, outdir):
    """The reference music stretched to the live length (every section by the same factor, pitch kept), then
    silence to the end of the hold: 174.0 s of 48 kHz stereo."""
    wav = outdir / "music_conformed.wav"
    tempo = timing.REF_LENGTH / timing.LIVE
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-af",
                    f"aresample=48000,atempo={tempo:.6f},apad=whole_dur={timing.TOTAL:.4f}", "-ac", "2",
                    "-t", f"{timing.TOTAL:.4f}", "-c:a", "pcm_s24le", str(wav)], check=True)
    return wav


def join(audio, outdir):
    parts = sorted((outdir / "parts").glob("part_*.mp4"))
    lst = outdir / "parts.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    stage = outdir / STAGE
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-an", "-movflags", "+faststart", str(stage)], check=True)
    wav = conformed(audio, outdir)
    total = timing.TOTAL
    review = outdir / REVIEW
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(stage), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-g", "120",
                    "-c:a", "aac", "-b:a", "320k", "-t", f"{total:.4f}", "-movflags", "+faststart", str(review)],
                   check=True)
    phone = outdir / PHONE
    vbr = int((24.0 * 8e6 / total - 128e3) * 0.95)
    common = ["-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
              "-maxrate", str(int(vbr * 1.6)), "-bufsize", str(int(vbr * 2)), "-pix_fmt", "yuv420p", "-g", "120"]
    passlog = str(outdir / "phone2pass")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(stage)] + common +
                   ["-pass", "1", "-passlogfile", passlog, "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(stage), "-i", str(wav), "-map", "0:v", "-map", "1:a"]
                   + common + ["-pass", "2", "-passlogfile", passlog, "-c:a", "aac", "-b:a", "128k",
                               "-t", f"{total:.4f}", "-movflags", "+faststart", str(phone)], check=True)
    for p in (stage, review, phone):
        print(f"{p.name}: {p.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=ROOT / "out/s05_full2")
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
