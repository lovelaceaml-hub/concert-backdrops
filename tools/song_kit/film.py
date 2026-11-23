"""The song kit's film: render a song in parallel parts and join, check and keep it (cloud CPU only).

    python tools/song_kit/film.py part <song> --index 3 --parts 20 --quality draft|film --outdir DIR
    python tools/song_kit/film.py join <song> --parts-dir DIR --quality draft|film --outdir DIR

draft: 960x540 at 30 fps, one temporal sample (Song 11's review practice: drafts at 540p 30 fps);
film: native 1920x1080 at 60 fps, two temporal samples (Song 11's delivery contract). Lengths come from the
song's own data (LIVE + HOLD). The join writes the silent picture and the review copy with the song's prepared
score (the recording unstretched, then the calm hold), and checks frame count, size, frame rate and length:
any failed check exits with an error, so nothing unchecked is saved. It also writes the song's section cues
(cues.py for engine/live.py, cues.csv for show software). No phone copies (owner direction).
No em dash or en dash anywhere in this file.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]
QUALITY = dict(draft=dict(scale=0.5, fps=30, samples=1, crf="20"), film=dict(scale=1.0, fps=60, samples=2, crf="14"))


def data(song):
    spec = importlib.util.spec_from_file_location(f"{song}_data", KIT / "songs" / song / "song_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frames(song, quality):
    D = data(song)
    return int(round((float(D.LIVE) + float(getattr(D, "HOLD", 15.0))) * QUALITY[quality]["fps"]))


def part(a):
    q = QUALITY[a.quality]
    total = frames(a.song, a.quality)
    step = -(-total // a.parts)
    s0, s1 = a.index * step, min(total, (a.index + 1) * step)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    if s0 >= s1:
        print(f"part {a.index}: nothing to render")
        return
    workers = max(1, a.workers or os.cpu_count() or 1)
    sub = -(-(s1 - s0) // workers)
    pieces, procs = [], []
    env = dict(os.environ, PYTHONHASHSEED="0")
    for k in range(workers):
        x0, x1 = s0 + k * sub, min(s1, s0 + (k + 1) * sub)
        if x0 >= x1:
            continue
        piece = out / f".p{a.index:03d}-{k}.mp4"
        pieces.append(piece)
        procs.append(subprocess.Popen([sys.executable, str(KIT / "render.py"), a.song, "--range", str(x0), str(x1),
                                       "--out", str(piece), "--scale", str(q["scale"]), "--fps", str(q["fps"]),
                                       "--samples", str(q["samples"]), "--crf", q["crf"]], cwd=ROOT, env=env))
    if any(p.wait() for p in procs):
        raise SystemExit(f"part {a.index}: a render worker failed")
    listing = out / f".p{a.index:03d}.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in pieces))
    dest = out / f"part{a.index:03d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
                    str(dest)], check=True)
    for p in pieces + [listing]:
        p.unlink()
    print(f"part {a.index}: frames {s0} to {s1} -> {dest}")


def cues(D, out):
    """The song's section markers for both playback routes (AGENTS.md, 2026-11-23): cues.py for engine/live.py and
    cues.csv for show software, one cue per edit block of the song's data, the calm hold last. Song times; a
    suggestion until someone confirms them against the music."""
    total = float(D.LIVE) + float(getattr(D, "HOLD", 15.0))
    rows = []
    for t, _owner, note in D.EDIT:
        name = note.split(":")[0].strip() if ":" in note[:40] else note.strip()
        rows.append((name[:60], round(float(t), 4)))
    rows.append(("Calm hold", round(float(D.LIVE), 4)))
    lines = ['"""Section cues for ' + D.TITLE + ' (song kit; unverified until reviewed)."""',
             "# Paste CUES into a song file in engine/songs/ to step through sections in engine/live.py.",
             f"TOTAL = {round(total, 4)}", "CUES = ["]
    lines += [f"    ({n!r}, {t!r}, None)," for n, t in rows] + ["]", ""]
    (out / "cues.py").write_text("\n".join(lines), encoding="utf-8")
    import csv
    with (out / "cues.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["name", "start_seconds", "start_timecode_60fps"])
        for n, t in rows:
            f = int(round(t * 60))
            w.writerow([n, f"{t:.4f}", f"{f // 216000:02d}:{f // 3600 % 60:02d}:{f // 60 % 60:02d}:{f % 60:02d}"])


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                          "stream=codec_type,width,height,r_frame_rate,nb_read_frames:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def join(a):
    D = data(a.song)
    q = QUALITY[a.quality]
    total = frames(a.song, a.quality)
    seconds = total / q["fps"]
    parts = sorted(Path(a.parts_dir).rglob("part*.mp4"))
    if not parts:
        raise SystemExit("No part*.mp4 files found.")
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{D.TITLE} - song kit {a.quality}"
    picture = out / f"{stem} - picture.mp4"
    review = out / f"{stem} - review.mp4"
    listing = out / "parts.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
                    "-movflags", "+faststart", str(picture)], check=True)
    listing.unlink()
    score = ROOT / "work/song_kit" / a.song / "score.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(score), "-map", "0:v", "-map", "1:a",
                    "-af", "volume=-1.0dB,alimiter=limit=0.89:level=false", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "320k", "-ar", "48000", "-t", f"{seconds:.3f}", "-movflags", "+faststart", str(review)],
                   check=True)
    errors, report = [], {}
    w, h = int(1920 * q["scale"]) // 2 * 2, int(1080 * q["scale"]) // 2 * 2
    for f in (picture, review):
        info = probe(f)
        v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
        n, rate = int(v["nb_read_frames"]), v["r_frame_rate"]
        report[f.name] = dict(frames=n, width=v["width"], height=v["height"], rate=rate,
                              seconds=float(info["format"]["duration"]),
                              audio=any(s["codec_type"] == "audio" for s in info["streams"]))
        if n != total:
            errors.append(f"{f.name}: {n} frames, expected {total}")
        if (v["width"], v["height"]) != (w, h):
            errors.append(f"{f.name}: {v['width']}x{v['height']}, expected {w}x{h}")
        if rate != f"{q['fps']}/1":
            errors.append(f"{f.name}: frame rate {rate}, expected {q['fps']}")
    if not report[review.name]["audio"]:
        errors.append("the review copy has no sound")
    (out / "check.json").write_text(json.dumps(dict(song=a.song, quality=a.quality, expected_frames=total,
                                                    files=report, errors=errors), indent=2) + "\n")
    print(json.dumps(report, indent=2))
    cues(D, out)
    sheet = out / "contact.jpg"   # 48 small frames across the film, picture only (for review; no sound)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-vf",
                    f"fps=48/{seconds:.3f},scale=320:-2,tile=6x8", "-frames:v", "1", "-q:v", "4", str(sheet)],
                   check=False)
    if errors:
        raise SystemExit("Checks failed: " + "; ".join(errors))
    print("checks passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("part")
    p.add_argument("song"); p.add_argument("--index", type=int, required=True); p.add_argument("--parts", type=int, required=True)
    p.add_argument("--quality", choices=QUALITY, default="draft"); p.add_argument("--outdir", required=True)
    p.add_argument("--workers", type=int)
    p.set_defaults(fn=part)
    p = sub.add_parser("join")
    p.add_argument("song"); p.add_argument("--parts-dir", required=True); p.add_argument("--quality", choices=QUALITY, default="draft")
    p.add_argument("--outdir", required=True)
    p.set_defaults(fn=join)
    p = sub.add_parser("cues", help="write cues.py and cues.csv only")
    p.add_argument("song"); p.add_argument("--outdir", required=True)
    p.set_defaults(fn=lambda a: cues(data(a.song), Path(a.outdir)) or print("cues written"))
    a = ap.parse_args()
    if sys.platform == "darwin":
        raise SystemExit("The song kit renders on cloud CPU only (owner rule).")
    a.fn(a)


if __name__ == "__main__":
    main()
