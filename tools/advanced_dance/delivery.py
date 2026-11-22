"""Verify two revised films and assemble an exact updated ten-film collection.

This helper never renders or re-encodes a movie and never uploads anything.
The original eight retained members are accepted only from the pinned saved
archive and are checked against the repository's saved delivery evidence.
The output directory must be new; it appears only after every check succeeds.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile

import numpy as np

from tools.cinematic_ten.package_delivery import FILMS as ORIGINAL_FILMS
from tools.advanced_dance.delivery_evidence import (
    DeliveryError,
    _report_mode,
    ledger_qa_arguments,
    read_qa,
    require,
    verify_production_bindings,
)

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_ARCHIVE_SHA256 = "7bd5e9f32f4a40150cba39c00bda8cd9959768bb837e448c80b482877e84b0b2"
ORIGINAL_EVIDENCE = "project-docs/production-system/evidence/cinematic-ten-final-delivery.json"
ORIGINAL_TECHNICAL = "Ten_Cinematic_Films_Technical.json"
ARCHIVE_NAME = "Ten_Cinematic_Films_Advanced_Dance_1080p60.zip"
OVERVIEW_NAME = "Ten_Cinematic_Films_Advanced_Dance_Overview.jpg"
TECHNICAL_NAME = "Ten_Cinematic_Films_Advanced_Dance_Technical.json"
QA_NAME = "Advanced_Dance_QA.json"
README_NAME = "README.txt"
CHECKSUM_NAME = "SHA256SUMS.txt"
RECEIPT_NAME = "Packaging_Receipt.json"
FRACTIONS = (.10, .40, .70, 1.0)
NEW_NAMES = {
    1: "01_Silk_in_Light_Advanced_Dance_1080p60.mp4",
    2: "02_Petals_in_Motion_Advanced_Dance_1080p60.mp4",
}


@dataclass(frozen=True)
class Film:
    number: int
    title: str
    filename: str
    seconds: int
    frames: int
    revised: bool


FILMS = tuple(Film(f.number, f.title, NEW_NAMES.get(f.number, f.filename),
                   32 if f.number <= 2 else 20, 1920 if f.number <= 2 else 1200,
                   f.number <= 2) for f in ORIGINAL_FILMS)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True,
                                    allow_nan=False) + "\n", encoding="utf-8")


def _run(command, timeout=240, *, binary=False):
    result = subprocess.run(command, capture_output=True, text=not binary,
                            timeout=timeout, check=False)
    if result.returncode:
        error = result.stderr.decode(errors="replace") if binary else result.stderr
        raise DeliveryError(f"{command[0]} failed: {error[-3000:]}")
    return result


def _fraction(value):
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return Fraction(-1)


def metadata_checks(metadata):
    """Strict encoded-delivery contract for the two new 32-second movies."""
    videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
    require(len(videos) == 1 and len(audios) == 1,
            "Each revised movie must contain exactly one picture and one audio stream")
    video, audio = videos[0], audios[0]
    checks = {
        "one_video_and_one_audio_stream": True,
        "h264_video": video.get("codec_name") == "h264",
        "resolution_1920x1080": (video.get("width"), video.get("height")) == (1920, 1080),
        "pixel_format_yuv420p": video.get("pix_fmt") == "yuv420p",
        "average_fps_60": _fraction(video.get("avg_frame_rate")) == 60,
        "nominal_fps_60": _fraction(video.get("r_frame_rate")) == 60,
        "metadata_frames_1920": str(video.get("nb_frames")) == "1920",
        "video_duration_exactly_32_seconds": _fraction(video.get("duration")) == 32,
        "container_duration_exactly_32_seconds": _fraction(metadata.get("format", {}).get("duration")) == 32,
        "video_starts_at_zero": _fraction(video.get("start_time", "0")) == 0,
        "bt709_color_space": video.get("color_space") == "bt709",
        "bt709_transfer": video.get("color_transfer") == "bt709",
        "bt709_primaries": video.get("color_primaries") == "bt709",
        "limited_video_range": video.get("color_range") == "tv",
        "aac_audio": audio.get("codec_name") == "aac",
        "stereo_48000_hz": audio.get("channels") == 2 and str(audio.get("sample_rate")) == "48000",
        "audio_starts_at_zero": _fraction(audio.get("start_time", "0")) == 0,
        "audio_duration_within_one_aac_packet": abs(_fraction(audio.get("duration")) - 32) <= Fraction(1024, 48000),
    }
    return checks, video, audio


def check_movie(path, mode, *, timeout=240):
    """Decode both streams in full and check the actual constant frame clock."""
    path = Path(path).resolve()
    require(mode in ("solo", "ensemble"), "Expected solo or ensemble")
    require(path.is_file() and path.stat().st_size > 0, f"Missing finished movie: {path}")
    before = sha256(path)
    metadata = json.loads(_run(["ffprobe", "-v", "error", "-show_streams",
                                "-show_format", "-of", "json", str(path)], timeout).stdout)
    checks, video, audio = metadata_checks(metadata)
    bad = [name for name, ok in checks.items() if not ok]
    require(not bad, f"{mode} encoded metadata failed: {', '.join(bad)}")
    print(json.dumps(dict(event="full_movie_decode", mode=mode, movie=str(path))), flush=True)
    decoded = _run(["ffmpeg", "-hide_banner", "-v", "error", "-nostdin",
                    "-xerror", "-err_detect", "explode", "-threads", "2",
                    "-i", str(path), "-map", "0:v:0", "-map", "0:a:0",
                    "-progress", "pipe:1", "-nostats", "-f", "null", "-"], timeout)
    progress = {}
    for line in decoded.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            progress[key] = value
    checks["full_video_and_audio_decode_without_errors"] = decoded.returncode == 0 and not decoded.stderr.strip()
    checks["full_decoder_reported_1920_frames"] = progress.get("frame", "").strip() == "1920"
    checks["full_decoder_completed"] = progress.get("progress") == "end"

    frames = json.loads(_run(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_frames", "-show_entries", "frame=best_effort_timestamp",
        "-of", "json", str(path)], timeout).stdout).get("frames", [])
    time_base = _fraction(video.get("time_base"))
    checks["decoded_timestamp_count_1920"] = len(frames) == 1920
    checks["every_decoded_timestamp_matches_60fps"] = (
        len(frames) == 1920 and time_base > 0
        and all("best_effort_timestamp" in row
                and int(row["best_effort_timestamp"]) * time_base == Fraction(index, 60)
                for index, row in enumerate(frames)))

    audio_data = _run(["ffmpeg", "-v", "error", "-nostdin", "-xerror",
        "-err_detect", "explode", "-i", str(path), "-map", "0:a:0",
        "-vn", "-ac", "2", "-ar", "48000", "-f", "f32le", "-"], timeout, binary=True)
    decoded_audio = np.frombuffer(audio_data.stdout, dtype="<f4")
    checks["decoded_audio_finite"] = bool(len(decoded_audio) and np.isfinite(decoded_audio).all())
    checks["decoded_audio_stereo_samples"] = len(decoded_audio) % 2 == 0
    sample_count = len(decoded_audio) // 2
    checks["decoded_audio_covers_32_seconds_with_aac_padding_only"] = 1536000 <= sample_count <= 1538048
    peak = float(np.max(np.abs(decoded_audio))) if len(decoded_audio) else 0.0
    rms = float(np.sqrt(np.mean(decoded_audio.astype(np.float64)**2))) if len(decoded_audio) else 0.0
    checks["decoded_audio_not_clipped"] = 0 < peak < .999
    checks["decoded_audio_not_silent"] = rms > 1e-5
    checks["master_unchanged_during_checks"] = sha256(path) == before
    bad = [name for name, ok in checks.items() if not ok]
    require(not bad, f"{mode} full movie check failed: {', '.join(bad)}")
    return {
        "mode": mode, "status": "passed", "errors": [], "source_master": str(path),
        "sha256": before, "size_bytes": path.stat().st_size, "checks": checks,
        "media": {"video": video, "audio": audio, "container": metadata["format"]},
        "decode": {"video_frames": len(frames), "video_clock": "n / 60, n=0..1919",
                   "audio_sample_frames": sample_count, "audio_sample_rate_hz": 48000,
                   "audio_channel_count": 2, "audio_decoded_peak": peak,
                   "audio_decoded_peak_dbfs": float(20*np.log10(peak)),
                   "audio_decoded_rms": rms, "full_stream_decode": True},
        "scope": "Encoded media integrity and exact video timestamps; motion and visual review are separate.",
    }


def inspect_original(archive, *, root=ROOT):
    """Read the pinned original inventory without extracting or altering it."""
    archive, root = Path(archive).resolve(), Path(root).resolve()
    require(archive.is_file(), f"The saved original archive is missing: {archive}")
    require(sha256(archive) == ORIGINAL_ARCHIVE_SHA256,
            "Original archive bytes do not match the saved pinned version")
    evidence_path = root / ORIGINAL_EVIDENCE
    evidence = json.loads(evidence_path.read_text())
    saved = {row["filename"]: row for row in evidence["files"]}
    require(saved["Ten_Cinematic_Films_1080p60.zip"]["sha256"] == ORIGINAL_ARCHIVE_SHA256,
            "Repository evidence disagrees with the pinned original archive")
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        require(len(names) == len(set(names)), "Original archive contains duplicate names")
        raw = bundle.read(ORIGINAL_TECHNICAL)
        require(hashlib.sha256(raw).hexdigest() == saved[ORIGINAL_TECHNICAL]["sha256"],
                "Original technical record does not match its saved hash")
        technical = json.loads(raw)
        old_films = {row["film_id"]: row for row in technical["films"]}
        for film in FILMS[2:]:
            require(film.filename in names and film.filename in saved,
                    f"Original film {film.number:02d} is missing from its inventory")
            require(old_films[film.number]["sha256"] == saved[film.filename]["sha256"],
                    f"Original film {film.number:02d} evidence disagrees")
    return {
        "archive": archive, "saved": saved, "technical": old_films,
        "evidence_path": evidence_path, "evidence_sha256": sha256(evidence_path),
        "picture_source_commit": evidence["picture_source_commit"],
        "technical_sha256": saved[ORIGINAL_TECHNICAL]["sha256"],
    }


def _copy_member(bundle, name, output, expected, expected_size):
    digest = hashlib.sha256()
    size = 0
    with bundle.open(name) as source, Path(output).open("wb") as target:
        for block in iter(lambda: source.read(1024*1024), b""):
            target.write(block)
            digest.update(block)
            size += len(block)
    require(digest.hexdigest() == expected and size == expected_size,
            f"Original archive member differs from its saved evidence: {name}")


def overview_indices(frames):
    require(isinstance(frames, int) and frames >= 4, "Overview needs a complete integer frame count")
    return [min(frames-1, round(frames*fraction)) for fraction in FRACTIONS]


def make_overview(root, movies, stage):
    from PIL import Image, ImageDraw, ImageFont
    font_path = root / "fonts/jost-latin-500-normal.ttf"
    require(font_path.is_file(), "Install the registered reference fonts before packaging")
    heading = ImageFont.truetype(str(font_path), 44)
    title = ImageFont.truetype(str(font_path), 30)
    small = ImageFont.truetype(str(font_path), 21)
    width, header, row_height, footer = 2400, 148, 420, 64
    image = Image.new("RGB", (width, header+10*row_height+footer), "#0b1020")
    draw = ImageDraw.Draw(image)
    draw.text((56, 20), "Ten Cinematic Films | Advanced Dance", font=heading, fill="#f5edda")
    draw.text((56, 80), "Two revised 32-second dance films | Eight original 20-second films retained",
              font=small, fill="#bdc6da")
    draw.text((56, 113), "Native master samples at 10%, 40%, 70% and the final frame | Actual times shown per row",
              font=small, fill="#dcc490")
    evidence = []
    with tempfile.TemporaryDirectory(prefix="dance-overview-", dir=stage.parent) as directory:
        directory = Path(directory)
        for row, (film, movie) in enumerate(zip(FILMS, movies)):
            indices = overview_indices(film.frames)
            selection = "+".join(f"eq(n\\,{index})" for index in indices)
            template = directory / f"film{film.number:02d}_%02d.png"
            _run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-threads", "2",
                  "-filter_threads", "1", "-i", str(movie), "-map", "0:v:0", "-an",
                  "-vf", f"select={selection},scale=560:315:flags=lanczos",
                  "-fps_mode", "passthrough", "-frames:v", "4", str(template)])
            decoded = sorted(directory.glob(f"film{film.number:02d}_*.png"))
            require(len(decoded) == 4, f"Film {film.number:02d} did not yield all four overview frames")
            y = header + row*row_height
            if row % 2 == 0:
                draw.rectangle((32, y-5, width-32, y+row_height-10), fill="#10182a")
            change = "revised dance" if film.revised else "original picture retained"
            draw.text((56, y), f"{film.number:02d}  {film.title} | {change} | {film.seconds} seconds",
                      font=title, fill="#f1e9db")
            rows = []
            for col, (index, path) in enumerate(zip(indices, decoded)):
                with Image.open(path) as source:
                    tile = source.convert("RGB")
                require(tile.size == (560, 315), "An overview frame has unexpected dimensions")
                x = 56+col*576
                image.paste(tile, (x, y+48))
                draw.rectangle((x-1, y+47, x+560, y+363), outline="#2c3650")
                draw.text((x, y+370), f"{index/60:.3f} s | frame {index}", font=small, fill="#bdc6da")
                rows.append({"frame": index, "seconds": index/60,
                             "decoded_scaled_rgb_sha256": hashlib.sha256(tile.tobytes()).hexdigest()})
            evidence.append({"film_id": film.number, "filename": film.filename,
                             "duration_seconds": film.seconds, "frames": rows})
            print(json.dumps(dict(event="overview_row_decoded", film=film.number)), flush=True)
    draw.text((56, image.height-45), "Four decoded samples per film. Continuous motion and native detail review are recorded separately.",
              font=small, fill="#bdc6da")
    target = stage / OVERVIEW_NAME
    image.save(target, "JPEG", quality=94, subsampling=0, optimize=True)
    return {"filename": OVERVIEW_NAME, "size_pixels": list(image.size),
            "rows": 10, "frames_per_row": 4, "samples": evidence}


def readme_text(source_commit):
    lines = [
        "TEN CINEMATIC FILMS: ADVANCED DANCE",
        "",
        "This collection revises Film 01 and Film 02 with complete 32-second",
        "choreographed dance performances. Films 03 through 10 are the exact",
        "previously delivered 20-second movie bytes, carried forward unchanged.",
        "There are ten movies, with a combined running time of 224 seconds.",
        "",
        "THE TWO REVISED FILMS",
        "",
        "The solo and five-person ensemble have eight phrases, 64 estimated",
        "musical counts, 96 authored steps per performer, two three-turn runs,",
        "an active ending, articulated fan grips, pleated costumes, sparkles",
        "and coordinated stage lighting. The original music playback speed",
        "is preserved. These are original authored performances informed by",
        "the supplied fan videos; covered feet and fingers were authored.",
        "",
        "PLAYBACK",
        "",
        "All movies are 1920 x 1080 at 60 fps, H.264 with Rec.709 SDR tags and",
        "stereo AAC audio at 48 kHz. The new films contain 1,920 frames each.",
        "The retained films contain 1,200 frames each. Packaging did not",
        "resize, retime, concatenate or re-encode any movie.",
        "",
        "MOVIE INVENTORY",
        "",
    ]
    lines += [f"{f.number:02d}. {f.title} | {f.seconds} seconds | "
              + ("REVISED DANCE" if f.revised else "ORIGINAL PICTURE RETAINED")
              + f"\n    {f.filename}" for f in FILMS]
    lines += [
        "",
        "INCLUDED EVIDENCE",
        "",
        f"{OVERVIEW_NAME}",
        "Ten rows, four actual decoded samples per movie. Each row labels",
        "its own timestamps, including the different 32- and 20-second clocks.",
        "",
        f"{TECHNICAL_NAME}",
        "Full new-movie audio/video decoding, exact video timestamp checks,",
        "decoded audio peaks, movie identities and original carried-film",
        "technical records. The eight retained hashes match the saved archive.",
        "",
        f"{QA_NAME}",
        "Supplied motion, cast and visual/production review content with the",
        "original report byte hashes. Review flags remain explicit. Technical",
        "passing and sampled visual review do not imply owner approval.",
        "",
        f"{CHECKSUM_NAME}",
        "SHA-256 hashes for the movies, overview, README and JSON evidence.",
        "The archive's own hash is in the separate Packaging_Receipt.json.",
        "",
        "REUSE AND REVIEW",
        "",
        "Repository: https://github.com/lovelaceaml-hub/concert-backdrops",
        f"Frozen new picture commit: {source_commit}",
        "Repair guide: tools/advanced_dance/README.md in the repository.",
        "The support and anatomy checks are kinematic authoring checks,",
        "not a force/balance simulation or captured hidden-foot validation.",
        "Original eight-film picture source: df4fc478116d3f0e34a85d2166097fbda55911bf",
        f"Original archive SHA-256: {ORIGINAL_ARCHIVE_SHA256}",
        "",
    ]
    return "\n".join(lines)


def _archive(path, members, date):
    with zipfile.ZipFile(path, "w", allowZip64=True) as bundle:
        for name, source in members.items():
            entry = zipfile.ZipInfo(name, date_time=date)
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_STORED if source.suffix in (".mp4", ".jpg") else zipfile.ZIP_DEFLATED
            with source.open("rb") as src, bundle.open(entry, "w", force_zip64=True) as dst:
                shutil.copyfileobj(src, dst, 1024*1024)
    with zipfile.ZipFile(path) as bundle:
        require(bundle.namelist() == list(members), "Finished archive has unexpected members")
        for name, source in members.items():
            digest = hashlib.sha256()
            with bundle.open(name) as stream:
                for block in iter(lambda: stream.read(1024*1024), b""):
                    digest.update(block)
            require(digest.hexdigest() == sha256(source), f"Finished archive member changed: {name}")


def package(old_archive, solo, ensemble, source_commit, qa_arguments, destination, *, root=ROOT, validation_ledger=None):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    require(not destination.exists(), "Use a new output directory; an existing delivery is never replaced")
    require(re.fullmatch(r"[0-9a-f]{40}", source_commit), "Supply the full frozen picture commit SHA")
    _run(["git", "-C", str(root), "cat-file", "-e", source_commit+"^{commit}"], 30)
    committed = _run(["git", "-C", str(root), "show", "-s", "--format=%cI", source_commit], 30).stdout.strip()
    commit_time = datetime.fromisoformat(committed).astimezone(timezone.utc)
    committed = commit_time.isoformat()
    archive_date = commit_time.timetuple()[:6]
    bound = ledger_qa_arguments(validation_ledger, source_commit, root=root) if validation_ledger else None
    if bound:
        qa_arguments = bound["arguments"] + list(qa_arguments)
    original = inspect_original(old_archive, root=root)
    new = {mode: check_movie(path, mode) for mode, path in (("solo", solo), ("ensemble", ensemble))}
    snapshots = {original["archive"]: ORIGINAL_ARCHIVE_SHA256,
                 original["evidence_path"]: original["evidence_sha256"]}
    for mode, record in new.items():
        snapshots[Path(record["source_master"])] = record["sha256"]
    if bound:
        snapshots.update(bound["snapshots"])
    movie_hashes = {mode: row["sha256"] for mode, row in new.items()}
    reports = read_qa(qa_arguments, movie_hashes, snapshots)
    production_bindings = verify_production_bindings(reports, movie_hashes, bound["frozen_sources"]) if bound else None
    snapshot_sizes = {path: path.stat().st_size for path in snapshots}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="advanced-dance-delivery-", dir=destination.parent) as directory:
        stage = Path(directory)
        members, films, movies = {}, [], []
        for film, mode in zip(FILMS[:2], ("solo", "ensemble")):
            target = stage / film.filename
            shutil.copy2(new[mode]["source_master"], target)
            require(sha256(target) == new[mode]["sha256"], f"Copied {mode} master changed")
            members[film.filename] = target
            movies.append(target)
            films.append({"film_id": film.number, "title": film.title, "filename": film.filename,
                          "revision": "advanced_dance", "duration_seconds": 32, "frames": 1920,
                          "picture_source_commit": source_commit, "sha256": new[mode]["sha256"],
                          "size_bytes": new[mode]["size_bytes"], "new_media_check": new[mode]})
        with zipfile.ZipFile(original["archive"]) as bundle:
            for film in FILMS[2:]:
                saved = original["saved"][film.filename]
                target = stage / film.filename
                _copy_member(bundle, film.filename, target, saved["sha256"], saved["bytes"])
                members[film.filename] = target
                movies.append(target)
                films.append({"film_id": film.number, "title": film.title, "filename": film.filename,
                              "revision": "original_picture_retained", "duration_seconds": 20,
                              "frames": 1200, "sha256": saved["sha256"], "size_bytes": saved["bytes"],
                              "byte_exact_from_saved_original": True,
                              "original_saved_identity": saved,
                              "original_technical_record": original["technical"][film.number],
                              "current_round_decode_scope": "Four overview samples; original full technical checks retained."})
        overview = make_overview(root, movies, stage)
        readme = stage / README_NAME
        readme.write_text(readme_text(source_commit), encoding="utf-8")
        qa = {
            "schema_version": 1, "source_picture_commit": source_commit,
            "supplied_report_count": len(reports), "blocking_errors_in_supplied_reports": False,
            "review_flags_preserved": True, "owner_approval": "not_recorded_by_packaging",
            "scope": "Supplied report content and source-byte identities; encoded checks are in the technical file.",
            "source_reports": reports,
            "validation_ledger": bound["record"] if bound else None,
            "production_bindings": production_bindings,
        }
        _write_json(stage / QA_NAME, qa)
        technical = {
            "schema_version": 1, "collection": "Ten Cinematic Films: Advanced Dance",
            "film_count": 10, "revised_film_ids": [1, 2], "carried_forward_film_ids": list(range(3, 11)),
            "combined_duration_seconds": 224, "source_picture_commit": source_commit,
            "source_commit_time_utc": committed,
            "original_archive_sha256": ORIGINAL_ARCHIVE_SHA256,
            "original_evidence_sha256": original["evidence_sha256"],
            "original_technical_record_sha256": original["technical_sha256"],
            "movie_reencoding": False, "owner_approval": "not_recorded_by_packaging",
            "delivery_script_sha256": sha256(Path(__file__)),
            "new_movies_full_decode_passed": True,
            "validation_ledger_sha256": bound["record"]["source_sha256"] if bound else None,
            "production_receipt_bindings": production_bindings,
            "carried_movies_match_saved_original_bytes": True,
            "overview": overview, "films": films,
            "qa_file": {"filename": QA_NAME, "sha256": sha256(stage / QA_NAME)},
            "tools": {name: _run([name, "-version"], 10).stdout.splitlines()[0] for name in ("ffmpeg", "ffprobe")},
        }
        _write_json(stage / TECHNICAL_NAME, technical)
        for name in (OVERVIEW_NAME, README_NAME, TECHNICAL_NAME, QA_NAME):
            members[name] = stage / name
        checksums = "".join(f"{sha256(path)}  {name}\n" for name, path in members.items())
        (stage / CHECKSUM_NAME).write_text(checksums, encoding="ascii")
        members[CHECKSUM_NAME] = stage / CHECKSUM_NAME
        for path, expected in snapshots.items():
            require(path.is_file() and path.stat().st_size == snapshot_sizes[path] and sha256(path) == expected,
                    f"Input changed while packaging: {path}")
        _archive(stage / ARCHIVE_NAME, members, archive_date)
        all_outputs = {**members, ARCHIVE_NAME: stage / ARCHIVE_NAME}
        receipt = {
            "schema_version": 1, "status": "packaged",
            "packaged_utc": datetime.now(timezone.utc).isoformat(),
            "film_count": 10, "revised_movies": 2, "unchanged_original_movies": 8,
            "archive_members": len(members), "destination": str(destination),
            "archive": ARCHIVE_NAME, "archive_sha256": sha256(stage / ARCHIVE_NAME),
            "source_picture_commit": source_commit,
            "files": [{"filename": name, "sha256": sha256(path), "size_bytes": path.stat().st_size}
                      for name, path in all_outputs.items()],
        }
        _write_json(stage / RECEIPT_NAME, receipt)
        for path, expected in snapshots.items():
            require(path.is_file() and path.stat().st_size == snapshot_sizes[path] and sha256(path) == expected,
                    f"Input changed before final directory installation: {path}")
        require(not destination.exists(), "Output directory appeared during packaging; refusing to replace it")
        stage.replace(destination)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-archive", type=Path, required=True)
    parser.add_argument("--solo", type=Path, required=True)
    parser.add_argument("--ensemble", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--validation-ledger", type=Path, help="Expand and verify bound motion/cloth/history reports; requires final pipeline receipts as supplemental --qa inputs")
    parser.add_argument("--qa", action="append", required=True, metavar="LABEL=JSON_PATH")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = package(args.old_archive, args.solo, args.ensemble, args.source_commit, args.qa, args.out,
                     validation_ledger=args.validation_ledger)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
