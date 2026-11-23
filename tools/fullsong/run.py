#!/usr/bin/env python3
"""Shared full-length song kit: one command line for every song built the Song 11 way.

Cloud CPU only (GitHub Actions or a cloud session); never on the Mac. Songs are listed in
tools/fullsong/songs.json; each keeps its own scene folder (clock.py, prepare_audio.py, render.py, verify.py).

    python tools/fullsong/run.py engines                      # restore the pinned engine snapshots (once)
    python tools/fullsong/run.py prepare s07                  # fetch the chosen recording, measure the music
    python tools/fullsong/run.py stills s07 [--times 3,70] [--scale .5] [--outdir DIR]
    python tools/fullsong/run.py part s07 --index 0 --parts 20 --outdir DIR [--workers 4]
    python tools/fullsong/run.py assemble s07 --parts-dir DIR --outdir DIR
    python tools/fullsong/run.py verify s07 FILE [--audio]
    python tools/fullsong/run.py upload s07 FILE...           # save to the song's Drive Videos folder

The recording is used as it is (no time stretching) and the picture runs at native 1080p60 with two temporal
samples, as for Song 11. No phone copies (owner direction, 2026-11-22). No em dash or en dash in this file.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "tools/fullsong/songs.json"
PY = sys.executable


def song(song_id: str) -> dict:
    songs = json.loads(REGISTRY.read_text())["songs"]
    if song_id not in songs:
        raise SystemExit(f"{song_id} is not in tools/fullsong/songs.json (known: {', '.join(songs)})")
    entry = dict(songs[song_id], id=song_id)
    entry["path"] = ROOT / entry["dir"]
    spec = importlib.util.spec_from_file_location(f"{song_id}_clock", entry["path"] / "clock.py")
    clock = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clock)
    entry["clock"] = clock
    entry["frames"] = int(round(clock.TOTAL * clock.FPS))
    return entry


def run(cmd, **kw):
    print("+ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, **kw)


def engines(_args):
    """Restore the pinned Film 10 engine (d928ff9) and Claude Final v1 (f43f451) under work/."""
    for commit in ("d928ff9eafe02ac3150f0c646bdcc497fe5a7278", "f43f4514e4bc42dc25166e90160d98219f5a0db4"):
        if subprocess.run(["git", "cat-file", "-e", commit], cwd=ROOT).returncode:
            run(["git", "fetch", "--depth=1", "origin", commit])
    sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
    import prepare as snapshots
    try:
        snapshots.prepare()
    except subprocess.CalledProcessError as exc:
        # The snapshot prepare also measures the promo medley; the full-length songs only need the engines.
        if not (snapshots.SNAPSHOT / "engine/render.py").exists() or not (snapshots.CLAUDE / "engine/p3d/words.py").exists():
            raise
        print(f"engines ready (promo medley analysis skipped: {exc.cmd[0]} exited {exc.returncode})")


def prepare(args):
    entry = song(args.song)
    sys.path.insert(0, str(ROOT))
    from pipeline.song_draft import find_song, recording
    audio = recording(ROOT, find_song(ROOT, args.song))
    env = dict(os.environ, ANALYZE_PYTHON=PY)
    run([PY, entry["path"] / "prepare_audio.py", audio], env=env)


def stills(args):
    entry = song(args.song)
    times = [float(t) for t in args.times.split(",")] if args.times else entry["review_stills"]
    outdir = Path(args.outdir or ROOT / "out" / args.song / "stills")
    outdir.mkdir(parents=True, exist_ok=True)
    workers = max(1, min(args.workers or os.cpu_count() or 1, len(times)))
    groups = [times[k::workers] for k in range(workers)]
    procs = [subprocess.Popen([PY, entry["path"] / "render.py", "--stills", ",".join(f"{t:g}" for t in g),
                               "--scale", str(args.scale), "--outdir", outdir], cwd=ROOT) for g in groups if g]
    if any(p.wait() for p in procs):
        raise SystemExit("A stills worker failed.")
    print(f"{len(times)} stills in {outdir}")


def part(args):
    """Render one of N equal parts of the song, split again across this machine's cores."""
    entry = song(args.song)
    total = entry["frames"]
    step = -(-total // args.parts)
    a, b = args.index * step, min(total, (args.index + 1) * step)
    if a >= b:
        print(f"part {args.index}: nothing to render")
        return
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    workers = max(1, args.workers or os.cpu_count() or 1)
    sub = -(-(b - a) // workers)
    pieces, procs = [], []
    for k in range(workers):
        s, e = a + k * sub, min(b, a + (k + 1) * sub)
        if s >= e:
            continue
        piece = outdir / f".part{args.index:02d}-{k}.mp4"
        pieces.append(piece)
        procs.append(subprocess.Popen([PY, entry["path"] / "render.py", "--range", str(s), str(e), "--out", piece,
                                       "--crf", str(args.crf)], cwd=ROOT))
    if any(p.wait() for p in procs):
        raise SystemExit(f"part {args.index}: a render worker failed")
    listing = outdir / f".part{args.index:02d}.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in pieces))
    out = outdir / f"part{args.index:02d}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", out])
    for p in pieces + [listing]:
        p.unlink()
    print(f"part {args.index}: frames {a} to {b} -> {out}")


def assemble(args):
    """Join the parts into the stage file (silent) and the review file (with the unstretched recording)."""
    entry = song(args.song)
    parts = sorted(Path(args.parts_dir).glob("part*.mp4"))
    if not parts:
        raise SystemExit("No part*.mp4 files found.")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    listing = outdir / "parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    seconds = entry["clock"].TOTAL
    stage = outdir / f"{entry['file_stem']} - stage 1080p60.mp4"
    review = outdir / f"{entry['file_stem']} - review 1080p60.mp4"
    color = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-map", "0:v", "-c:v", "libx264",
         "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(entry["clock"].FPS), *color,
         "-movflags", "+faststart", stage])
    wav = ROOT / entry["work"] / "review.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", stage, "-i", wav, "-map", "0:v", "-map", "1:a",
         "-af", "volume=-1.5dB,alimiter=limit=0.89:level=false", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
         "-ar", "48000", "-t", f"{seconds:.3f}", "-movflags", "+faststart", review])
    listing.unlink()
    print(stage)
    print(review)


def verify(args):
    entry = song(args.song)
    run([PY, entry["path"] / "verify.py", args.file] + (["--audio"] if args.audio else []))


def upload(args):
    entry = song(args.song)
    helper = os.environ.get("DRIVE_PYTHON") or shutil.which("python3") or PY
    for f in args.files:
        run([helper, ROOT / "tools/drive_sync.py", "put", f, "--path", entry["drive_folder"]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("engines").set_defaults(fn=engines)
    p = sub.add_parser("prepare"); p.add_argument("song"); p.set_defaults(fn=prepare)
    p = sub.add_parser("stills"); p.add_argument("song"); p.add_argument("--times")
    p.add_argument("--scale", type=float, default=0.5); p.add_argument("--outdir"); p.add_argument("--workers", type=int)
    p.set_defaults(fn=stills)
    p = sub.add_parser("part"); p.add_argument("song"); p.add_argument("--index", type=int, required=True)
    p.add_argument("--parts", type=int, required=True); p.add_argument("--outdir", required=True)
    p.add_argument("--workers", type=int); p.add_argument("--crf", type=int, default=14); p.set_defaults(fn=part)
    p = sub.add_parser("assemble"); p.add_argument("song"); p.add_argument("--parts-dir", required=True)
    p.add_argument("--outdir", required=True); p.set_defaults(fn=assemble)
    p = sub.add_parser("verify"); p.add_argument("song"); p.add_argument("file"); p.add_argument("--audio", action="store_true")
    p.set_defaults(fn=verify)
    p = sub.add_parser("upload"); p.add_argument("song"); p.add_argument("files", nargs="+"); p.set_defaults(fn=upload)
    args = ap.parse_args()
    if sys.platform == "darwin" and args.cmd in ("stills", "part"):
        raise SystemExit("Full-length rendering is cloud CPU only (owner rule). Use the fullsong GitHub workflow.")
    args.fn(args)


if __name__ == "__main__":
    main()
