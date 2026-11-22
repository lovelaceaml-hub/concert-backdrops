"""Check the ten delivered movies without importing any picture source.

Usage: .venv/bin/python -m tools.cinematic_ten.check_movies
Missing masters are reported as incomplete. Use --allow-missing while renders
are running; present movies must still pass every technical check.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = dict(width=1920, height=1080, fps=60, frames=1200, seconds=20.0,
                audio_present=True)
SAMPLE_FRAMES = (0, 120, 300, 480, 660, 840, 1020, 1199)


def _json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rate(value):
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return None


def _run(command, timeout):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                          check=False)


def _font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _contact(film_id, samples, target):
    sheet = Image.new("RGB", (1920, 662), "#07101e")
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 16), f"Film {film_id:02d} | Decoded final movie | Eight timeline samples",
              font=_font(23), fill="#f4e8cc")
    for index, frame_index in enumerate(SAMPLE_FRAMES):
        x, y = (index % 4) * 480, 58 + (index // 4) * 300
        sample = samples.get(frame_index)
        if sample is not None:
            sheet.paste(sample.resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        else:
            draw.rectangle((x + 1, y, x + 479, y + 269), outline="#344454")
            draw.text((x + 20, y + 120), "Sample unavailable", font=_font(20), fill="#ed9a94")
        draw.text((x + 12, y + 276), f"{frame_index / 60:.3f} s | frame {frame_index}",
                  font=_font(16), fill="white")
    sheet.save(target, quality=94, subsampling=0)


def check_movie(film_id, master, out, ffprobe, ffmpeg, timeout=180):
    result = dict(film_id=film_id, path=str(master), status="missing", errors=[])
    if not master.is_file():
        return result
    before = master.stat()
    result.update(status="failed", size_bytes=before.st_size)
    film_out = out / f"film{film_id:02d}"
    film_out.mkdir(parents=True, exist_ok=True)
    try:
        probe = _run([ffprobe, "-v", "error", "-show_streams", "-show_format",
                      "-of", "json", str(master)], timeout)
        if probe.returncode:
            raise RuntimeError("ffprobe failed: " + probe.stderr[-6000:])
        metadata = json.loads(probe.stdout)
        videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")]
        audio = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
        if not videos:
            raise RuntimeError("No video stream was found.")
        video = videos[0]
        avg_rate, nominal_rate = _rate(video.get("avg_frame_rate")), _rate(video.get("r_frame_rate"))
        rate = avg_rate if avg_rate and avg_rate > 0 else nominal_rate
        video_seconds = _number(video.get("duration"))
        format_seconds = _number(metadata.get("format", {}).get("duration"))
        checks = {
            "resolution_1920x1080": (video.get("width"), video.get("height")) == (1920, 1080),
            "fps_60": rate == Fraction(60, 1),
            "nominal_fps_60": nominal_rate in (None, Fraction(60, 1)),
            "video_duration_20_seconds": video_seconds is not None and abs(video_seconds - 20) <= .02,
            "container_duration_20_seconds": format_seconds is not None and abs(format_seconds - 20) <= .05,
            "audio_present": bool(audio),
        }
        result["media"] = dict(width=video.get("width"), height=video.get("height"),
                               avg_frame_rate=video.get("avg_frame_rate"),
                               r_frame_rate=video.get("r_frame_rate"),
                               video_duration_seconds=video_seconds,
                               container_duration_seconds=format_seconds,
                               metadata_frames=video.get("nb_frames"),
                               codec=video.get("codec_name"), pixel_format=video.get("pix_fmt"),
                               color_space=video.get("color_space"),
                               color_transfer=video.get("color_transfer"),
                               color_primaries=video.get("color_primaries"),
                               audio_streams=[{k: s.get(k) for k in
                                              ("codec_name", "sample_rate", "channels", "duration")}
                                             for s in audio])
        # A full decode counts actual frames and checks the audio payload too.
        decoded = _run([ffmpeg, "-hide_banner", "-v", "error", "-nostdin", "-xerror",
                        "-err_detect", "explode", "-threads", "2", "-i", str(master),
                        "-map", "0:v:0", "-map", "0:a?", "-fps_mode", "passthrough",
                        "-threads", "2", "-progress", "pipe:1", "-nostats", "-f", "null", "-"], timeout)
        progress = dict(line.split("=", 1) for line in decoded.stdout.splitlines() if "=" in line)
        decoded_frames = int(progress.get("frame", "0").strip())
        checks["full_decode_without_errors"] = decoded.returncode == 0 and not decoded.stderr.strip()
        checks["decoded_frames_1200"] = decoded_frames == 1200
        declared_frames = _number(video.get("nb_frames"))
        checks["metadata_frame_count_consistent"] = declared_frames in (None, decoded_frames)
        result["decode"] = dict(returncode=decoded.returncode, frames=decoded_frames,
                                diagnostic=decoded.stderr[-12000:], progress_end=progress.get("progress"))

        selector = "+".join(f"eq(n\\,{n})" for n in SAMPLE_FRAMES)
        samples, records = {}, []
        with tempfile.TemporaryDirectory(prefix="decode-", dir=film_out) as temp_name:
            temp = Path(temp_name)
            extracted = _run([ffmpeg, "-hide_banner", "-v", "error", "-nostdin", "-xerror",
                              "-threads", "2", "-i", str(master), "-map", "0:v:0", "-an",
                              "-vf", f"select={selector}", "-fps_mode", "passthrough",
                              "-frames:v", "8", "-threads", "1", "-compression_level", "2",
                              "-start_number", "0", str(temp / "sample_%02d.png")], timeout)
            checks["sample_decode_without_errors"] = extracted.returncode == 0 and not extracted.stderr.strip()
            if extracted.stderr.strip():
                result["sample_decode_diagnostic"] = extracted.stderr[-6000:]
            previous = None
            for frame_index, path in zip(SAMPLE_FRAMES, sorted(temp.glob("sample_*.png"))):
                with Image.open(path) as source:
                    image = source.convert("RGB")
                small = image.resize((320, 180), Image.Resampling.BILINEAR)
                difference = (sum(ImageStat.Stat(ImageChops.difference(small, previous)).mean) / 3
                              if previous is not None else None)
                records.append(dict(frame_index=frame_index, seconds=frame_index / 60,
                                    decoded_rgb_sha256=hashlib.sha256(image.tobytes()).hexdigest(),
                                    mean_absolute_difference_from_previous_sample=difference))
                samples[frame_index] = image
                previous = small
        unique = len({record["decoded_rgb_sha256"] for record in records})
        checks["eight_samples_decoded"] = len(records) == 8
        checks["eight_sampled_frames_unique"] = unique == 8
        result["samples"] = dict(count=len(records), unique_count=unique, frames=records)
        contact = film_out / "contact.jpg"
        _contact(film_id, samples, contact)
        result["contact_sheet"] = str(contact)
        result["sha256"] = _sha256(master)
        after = master.stat()
        checks["master_unchanged_during_checks"] = (
            before.st_ino, before.st_size, before.st_mtime_ns
        ) == (after.st_ino, after.st_size, after.st_mtime_ns)
        result["checks"] = checks
        result["errors"].extend(name for name, passed in checks.items() if not passed)
        result["status"] = "passed" if not result["errors"] else "failed"
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        result["errors"].append(str(error))
    _json(film_out / "report.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--master-pattern", default="work/pipeline/cinematic-ten-{film:02d}/final/master.mp4",
                        help="Absolute path or path relative to --root; accepts {film:02d}.")
    parser.add_argument("--out", type=Path, default=Path("work/cinematic-ten/qa/final-masters"))
    parser.add_argument("--films", default="1,2,3,4,5,6,7,8,9,10")
    parser.add_argument("--allow-missing", action="store_true",
                        help="Exit successfully when present movies pass and other masters are still missing.")
    parser.add_argument("--timeout", type=int, default=180, help="Maximum seconds for each media command.")
    args = parser.parse_args()
    try:
        films = sorted(set(int(value) for value in args.films.split(",")))
        if not films or any(film not in range(1, 11) for film in films):
            raise ValueError()
        paths = [Path(args.master_pattern.format(film=film)) for film in films]
    except (ValueError, KeyError, IndexError):
        parser.error("Use film numbers 1..10 and a master pattern containing only the film format field.")
    root = args.root.resolve()
    out = args.out.resolve() if args.out.is_absolute() else root / args.out
    out.mkdir(parents=True, exist_ok=True)
    ffprobe, ffmpeg = shutil.which("ffprobe"), shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        parser.error("ffprobe and ffmpeg must be installed.")
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), expected=EXPECTED,
                  duration_tolerance_seconds=dict(video=.02, container=.05),
                  scope="Technical media checks and eight decoded timeline samples. Visual composition and choreography require separate review.",
                  requested_films=films, movies=[])
    for film_id, path in zip(films, paths):
        master = path.resolve() if path.is_absolute() else root / path
        result = check_movie(film_id, master, out, ffprobe, ffmpeg, args.timeout)
        report["movies"].append(result)
        statuses = [movie["status"] for movie in report["movies"]]
        report["summary"] = {name: statuses.count(name) for name in ("passed", "failed", "missing")}
        report["complete"] = len(statuses) == len(films) and not report["summary"]["missing"]
        report["all_passed"] = report["complete"] and not report["summary"]["failed"]
        _json(out / "report.json", report)
        print(json.dumps(dict(film_id=film_id, status=result["status"], errors=result["errors"])), flush=True)
    print(json.dumps(dict(report=str(out / "report.json"), **report["summary"])), flush=True)
    return 1 if report["summary"]["failed"] else 2 if report["summary"]["missing"] and not args.allow_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
