"""Full render of song 02 "The Rose" backdrop in this cloud session: parallel frame ranges, joined with the music
and a 15 second silent hold, then the master and the share copy, then checks.

    python tools/s02_full/export.py --prepare                 # audio features and the padded score (outside git)
    python tools/s02_full/export.py --render --workers 4 --parts 12
    python tools/s02_full/export.py --join                    # master + share copy
    python tools/s02_full/export.py --check

Audio and videos live outside the repository (S02_AUDIO_DIR, default ../media/audio; output ../media/out).
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
MEDIA = ROOT.parent / "media"
AUDIO = Path(os.environ.get("S02_AUDIO_DIR", str(MEDIA / "audio")))
OUT = MEDIA / "out"
PARTS = OUT / "parts"
SRC = AUDIO / "s02.m4a"
SRC_SHA = "45ba01babded6297abef3ea531154c7e3c6a75a690af370461457a5e82cb19f9"
FPS = 30
TOTAL = 227.3
NFR = int(round(TOTAL * FPS))
MASTER = OUT / "02 The Rose - Concert Backdrop - 1080p30.mp4"
SHARE = OUT / "02 The Rose - Concert Backdrop - share 720p.mp4"


def run(cmd, **kw):
    print(" ".join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def prepare():
    if hashlib.sha256(SRC.read_bytes()).hexdigest() != SRC_SHA:
        raise SystemExit("the song audio does not match the shared recording")
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-ac", "1", "-ar", "22050", AUDIO / "s02_22k.wav"])
    run([sys.executable, ROOT / "work/nine_colours_minor/render1/engine/analyze.py", AUDIO / "s02_22k.wav",
         AUDIO / "s02_features.npz"], env=dict(os.environ, NUMBA_CACHE_DIR=str(MEDIA / "numba")),
        stdout=subprocess.DEVNULL)
    # the score: the music from frame 0, then silence to the end of the hold
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af", f"apad=whole_dur={TOTAL}", "-t", f"{TOTAL}", "-ac", "2",
         "-ar", "48000", "-c:a", "pcm_s24le", AUDIO / "s02_score.wav"])


def ranges(parts):
    # people's cloth is simulated from each body's first moment, so parts are cut at the same quiet seams
    # and balanced by an estimate of the cost of each second
    edges = [round(NFR * k / parts) for k in range(parts + 1)]
    return list(zip(edges[:-1], edges[1:]))


def render_part(a, b):
    out = PARTS / f"part_{a:05d}_{b:05d}.mp4"
    if out.exists() and (PARTS / (out.name + ".ok")).exists():
        return out, "kept"
    log = PARTS / (out.name + ".log")
    with open(log, "w") as fh:
        subprocess.run([sys.executable, HERE / "render.py", "--range", str(a), str(b), "--out", str(out)],
                       stdout=fh, stderr=subprocess.STDOUT, check=True)
    (PARTS / (out.name + ".ok")).write_text("ok\n")
    return out, "done"


def render(workers, parts, only=None):
    PARTS.mkdir(parents=True, exist_ok=True)
    jobs = ranges(parts)
    if only:
        jobs = [jobs[i] for i in only]
    # longest-looking first: the people-heavy middle
    with cf.ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(render_part, a, b): (a, b) for a, b in jobs}
        for f in cf.as_completed(futs):
            print(futs[f], f.result(), flush=True)


def join(parts):
    lst = OUT / "parts.txt"
    lst.write_text("".join(f"file '{PARTS / f'part_{a:05d}_{b:05d}.mp4'}'\n" for a, b in ranges(parts)))
    joined = OUT / "joined_video.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", AUDIO / "s02_score.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", f"{TOTAL}", "-movflags", "+faststart", MASTER])
    # share copy under 25 MB: two pass at about 700 kbps video, 128 kbps audio
    vb = "700k"
    for p in (1, 2):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", MASTER, "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264",
               "-preset", "slow", "-b:v", vb, "-pass", str(p), "-passlogfile", str(OUT / "pass"), "-pix_fmt",
               "yuv420p"]
        cmd += (["-an", "-f", "mp4", "/dev/null"] if p == 1 else
                ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", SHARE])
        run(cmd)


def check():
    rep = {}
    for f in (MASTER, SHARE):
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
                                        str(f)], capture_output=True, text=True).stdout)
        v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
        rep[f.name] = dict(size=int(pr["format"]["size"]), duration=float(pr["format"]["duration"]),
                           frames=v.get("nb_frames"), w=v["width"], h=v["height"], fps=v["r_frame_rate"],
                           vdur=v.get("duration"), adur=a.get("duration"),
                           sha256=hashlib.sha256(f.read_bytes()).hexdigest())
    # black frames and frozen frames on the master
    bd = subprocess.run(["ffmpeg", "-v", "info", "-i", str(MASTER), "-vf", "blackdetect=d=0.03:pix_th=0.06",
                         "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["black"] = [l for l in bd.splitlines() if "black_start" in l]
    fz = subprocess.run(["ffmpeg", "-v", "info", "-i", str(MASTER), "-vf", "freezedetect=n=0.0003:d=0.5",
                         "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["frozen"] = [l.split("] ")[-1] for l in fz.splitlines() if "freeze_start" in l or "freeze_end" in l]
    (OUT / "check.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--join", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--parts", type=int, default=12)
    ap.add_argument("--only", type=int, nargs="*")
    a = ap.parse_args()
    if a.prepare:
        prepare()
    if a.render:
        render(a.workers, a.parts, a.only)
    if a.join:
        join(a.parts)
    if a.check:
        check()


if __name__ == "__main__":
    main()
