"""Song 01 "All You Stars of Zion" backdrop, version 2: full render in this cloud session (parallel frame ranges),
then the three deliverables and the checks.

    python tools/s01_full2/prepare_s01.py                       # engines, features, score (outside git)
    python tools/s01_full2/export.py --render --workers 4 --parts 12
    python tools/s01_full2/export.py --join                     # stage (silent), review (music), phone 720p60
    python tools/s01_full2/export.py --check

Stage clock = song clock: the reference (187.97 s) is within 1 s of the live length 188.0 s, so it is used as is.
Total 188.0 + 15 s calm hold = 203.0 s, 12180 frames at 60 fps. The review music is the reference untouched,
padded with silence to 203.0 s (prepare_s01.py score.wav). Audio and videos live outside the repository
(work/ is ignored by git). S01_PARTS may point the parts at another folder (extra cloud sessions).
No em dash or en dash anywhere in this file.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / "work/s01_full2"
OUT = WORK / "out"
PARTS = Path(os.environ.get("S01_PARTS", str(OUT / "parts")))
LIVE = 188.0
HOLD = 15.0
FPS = 60
TOTAL = LIVE + HOLD            # 203.0 s
NFR = int(round(TOTAL * FPS))  # 12180
NAME = "01 All You Stars of Zion - Backdrop v2"
STAGE = OUT / f"{NAME} - stage 1080p60.mp4"
REVIEW = OUT / f"{NAME} - review 1080p60.mp4"
PHONE = OUT / f"{NAME} - phone 720p60.mp4"
SCORE = WORK / "score.wav"
COLOR = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]


def run(cmd, **kw):
    print(" ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), check=True, **kw)


def ranges(parts):
    edges = [round(NFR * k / parts) for k in range(parts + 1)]
    return list(zip(edges[:-1], edges[1:]))


def render_part(a, b):
    out = PARTS / f"part_{a:05d}_{b:05d}.mp4"
    if out.exists() and (PARTS / (out.name + ".ok")).exists():
        return out, "kept"
    log = PARTS / (out.name + ".log")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(log, "w") as fh:
        subprocess.run([sys.executable, str(HERE / "render.py"), "--range", str(a), str(b), "--out", str(out)],
                       stdout=fh, stderr=subprocess.STDOUT, check=True)
    (PARTS / (out.name + ".ok")).write_text("ok\n")
    return out, "done"


def render(workers, parts, only=None):
    PARTS.mkdir(parents=True, exist_ok=True)
    jobs = ranges(parts)
    if only:
        jobs = [jobs[i] for i in only]
    with cf.ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(render_part, a, b): (a, b) for a, b in jobs}
        for f in cf.as_completed(futs):
            print(futs[f], f.result(), flush=True)


def join(parts):
    lst = OUT / "parts.txt"
    lst.write_text("".join(f"file '{PARTS / f'part_{a:05d}_{b:05d}.mp4'}'\n" for a, b in ranges(parts)))
    joined = OUT / "joined_video.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    # stage: silent, H.264 CRF 16
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-map", "0:v", "-c:v", "libx264", "-preset", "slow",
         "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), *COLOR, "-frames:v", str(NFR),
         "-movflags", "+faststart", STAGE])
    # review: the same picture with the conformed music, CRF 20, AAC 320k
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", SCORE, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), *COLOR, "-frames:v", str(NFR),
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", f"{TOTAL}", "-movflags", "+faststart", REVIEW])
    # phone: 720p60 with music, under 25 MB (two pass, about 640 kbps video and 96 kbps audio)
    for p in (1, 2):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", SCORE, "-map", "0:v", "-map", "1:a",
               "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-b:v", "640k",
               "-maxrate", "1200k", "-bufsize", "2400k", "-pass", str(p), "-passlogfile", str(OUT / "pass"),
               "-pix_fmt", "yuv420p", "-r", str(FPS), *COLOR, "-frames:v", str(NFR)]
        cmd += (["-an", "-f", "mp4", "/dev/null"] if p == 1 else
                ["-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-t", f"{TOTAL}", "-movflags", "+faststart", PHONE])
        run(cmd)


def check():
    rep = {}
    for f in (STAGE, REVIEW, PHONE):
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format",
                                        "-of", "json", str(f)], capture_output=True, text=True).stdout)
        v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        rep[f.name] = dict(size=int(pr["format"]["size"]), duration=float(pr["format"]["duration"]),
                           frames=v.get("nb_read_frames"), w=v["width"], h=v["height"], fps=v["r_frame_rate"],
                           pix=v.get("pix_fmt"), vdur=v.get("duration"), audio=[x.get("duration") for x in a],
                           sha256=hashlib.sha256(f.read_bytes()).hexdigest())
    bd = subprocess.run(["ffmpeg", "-v", "info", "-i", str(STAGE), "-vf", "blackdetect=d=0.02:pix_th=0.06",
                         "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["black"] = [ln for ln in bd.splitlines() if "black_start" in ln]
    fz = subprocess.run(["ffmpeg", "-v", "info", "-i", str(STAGE), "-vf", "freezedetect=n=0.0003:d=0.3",
                         "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["frozen"] = [ln.split("] ")[-1] for ln in fz.splitlines() if "freeze_start" in ln or "freeze_end" in ln]
    (OUT / "check.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--join", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--parts", type=int, default=12)
    ap.add_argument("--only", type=int, nargs="*")
    a = ap.parse_args()
    if a.render:
        render(a.workers, a.parts, a.only)
    if a.join:
        join(a.parts)
    if a.check:
        check()


if __name__ == "__main__":
    main()
