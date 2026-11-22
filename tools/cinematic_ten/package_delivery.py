"""Package all ten completed native masters after their technical checks pass.

This delivery helper is outside the per-film picture dependency lists. It never
renders a scene or encodes a movie. FFmpeg only decodes four overview frames.
Existing identical deliverables are reused without copying or changing xattrs;
an existing file with different bytes is an error, never an overwrite request.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
FROZEN_PICTURE_COMMIT = "df4fc478116d3f0e34a85d2166097fbda55911bf"
PULL_REQUEST_URL = "https://github.com/lovelaceaml-hub/concert-backdrops/pull/108"
MOTION_DOCUMENT_URL = (
    "https://github.com/lovelaceaml-hub/concert-backdrops/blob/"
    "909763eeddcf519abc687f86047ba60754658d7b/"
    "project-docs/production-system/CINEMATIC-TEN-MOTION.md"
)
OVERVIEW_NAME = "Ten_Cinematic_Films_Overview.jpg"
TECHNICAL_NAME = "Ten_Cinematic_Films_Technical.json"
CHECKSUM_NAME = "SHA256SUMS.txt"
ARCHIVE_NAME = "Ten_Cinematic_Films_1080p60.zip"
OVERVIEW_FRAMES = (120, 480, 840, 1199)
EXPECTED = {"width": 1920, "height": 1080, "fps": 60, "frames": 1200,
            "seconds": 20.0, "audio_present": True}
REQUIRED_CHECKS = (
    "resolution_1920x1080", "fps_60", "nominal_fps_60",
    "video_duration_20_seconds", "container_duration_20_seconds",
    "audio_present", "full_decode_without_errors", "decoded_frames_1200",
    "metadata_frame_count_consistent", "sample_decode_without_errors",
    "eight_samples_decoded", "eight_sampled_frames_unique",
    "master_unchanged_during_checks",
)


@dataclass(frozen=True)
class Film:
    number: int
    title: str
    filename: str


FILMS = (
    Film(1, "Silk in Light", "01_Silk_in_Light_1080p60.mp4"),
    Film(2, "Petals in Motion", "02_Petals_in_Motion_1080p60.mp4"),
    Film(3, "One World, Many Hearts", "03_One_World_Many_Hearts_1080p60.mp4"),
    Film(4, "The Written Light", "04_The_Written_Light_1080p60.mp4"),
    Film(5, "Procession of Lanterns", "05_Procession_of_Lanterns_1080p60.mp4"),
    Film(6, "A Garden Awakens", "06_A_Garden_Awakens_1080p60.mp4"),
    Film(7, "Wings of Peace", "07_Wings_of_Peace_1080p60.mp4"),
    Film(8, "Ocean of Light", "08_Ocean_of_Light_1080p60.mp4"),
    Film(9, "Celestial Clockwork", "09_Celestial_Clockwork_1080p60.mp4"),
    Film(10, "Together in the Light", "10_Together_in_the_Light_1080p60.mp4"),
)


class DeliveryError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise DeliveryError(message)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_value(value, label):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value),
            f"Missing or invalid SHA256 in {label}")
    return value


def read_record(path, snapshots):
    require(path.is_file(), f"Required report or manifest is missing: {path}")
    raw = path.read_bytes()
    snapshots[path] = hashlib.sha256(raw).hexdigest()
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise DeliveryError(f"Invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"Expected a JSON object: {path}")
    return value


def repo_file(root, name, label):
    require(isinstance(name, str) and name, f"Missing path in {label}")
    path = (root / name).resolve()
    require(path.is_relative_to(root), f"Path leaves the checkout in {label}: {name}")
    require(path.is_file(), f"Required file is missing: {path}")
    return path


def validate_film(root, reports, film, snapshots):
    project_id = f"cinematic-ten-{film.number:02d}"
    folder = root / "work/pipeline" / project_id / "final"
    master = folder / "master.mp4"
    require(master.is_file() and master.stat().st_size > 0,
            f"Final master is missing or empty: {master}")
    checker_path = reports / f"film{film.number:02d}" / "report.json"
    visual_path = checker_path.with_name("visual-review.json")
    qa_path, assembly_path = folder / "qa.json", folder / "master.json"
    render_path = folder / "shots/film/receipt.json"
    project_path = root / "projects" / project_id / "project.json"
    checker = read_record(checker_path, snapshots)
    visual = read_record(visual_path, snapshots)
    qa = read_record(qa_path, snapshots)
    assembly = read_record(assembly_path, snapshots)
    rendered = read_record(render_path, snapshots)
    project = read_record(project_path, snapshots)

    require(checker.get("film_id") == film.number and checker.get("status") == "passed"
            and checker.get("errors") == [], f"Film {film.number:02d} checker did not pass")
    checks = checker.get("checks")
    require(isinstance(checks, dict) and all(checks.get(k) is True for k in REQUIRED_CHECKS)
            and all(value is True for value in checks.values()),
            f"Film {film.number:02d} has missing or failed checker checks")
    checked_path = checker.get("path")
    require(isinstance(checked_path, str) and (root / checked_path).resolve() == master.resolve(),
            f"Film {film.number:02d} checker points to a different master")
    require(qa.get("project_id") == project_id and qa.get("quality") == "final"
            and qa.get("technical_passed") is True and qa.get("errors") == [],
            f"Film {film.number:02d} pipeline QA did not pass")
    require(visual.get("film_id") == film.number
            and visual.get("blocking_visual_defects_found") is False,
            f"Film {film.number:02d} has no matching visual review without blocking defects")
    require(assembly.get("project_id") == project_id and assembly.get("quality") == "final"
            and assembly.get("filename") == "master.mp4",
            f"Film {film.number:02d} assembly receipt is not the final master")
    require(project.get("project_id") == project_id and project.get("title") == film.title,
            f"Film {film.number:02d} registered title or project does not match the delivery mapping")
    for key in ("width", "height", "fps", "frames"):
        require(assembly.get(key) == EXPECTED[key],
                f"Film {film.number:02d} assembly {key} is not {EXPECTED[key]}")
    require(qa.get("frames") == 1200 and qa.get("fps") == 60
            and abs(float(qa.get("duration_seconds", 0)) - 20) <= .05
            and qa.get("audio_streams", 0) >= 1,
            f"Film {film.number:02d} pipeline media metadata is incomplete")
    require(rendered.get("complete") is True
            and set(rendered.get("frames", {})) == {str(i) for i in range(1200)},
            f"Film {film.number:02d} has no complete 1200-frame render receipt")
    require(rendered.get("width") == 1920 and rendered.get("height") == 1080
            and rendered.get("fps") == 60,
            f"Film {film.number:02d} render receipt is not native 1080p60")
    require(assembly.get("shot_fingerprints", {}).get("film") == rendered.get("fingerprint")
            and isinstance(rendered.get("fingerprint"), str),
            f"Film {film.number:02d} render and assembly fingerprints disagree")

    media = checker.get("media", {})
    require(media.get("width") == 1920 and media.get("height") == 1080
            and Fraction(media.get("avg_frame_rate", "0")) == 60
            and Fraction(media.get("r_frame_rate", "0")) == 60
            and media.get("codec") == "h264" and media.get("pixel_format") == "yuv420p"
            and all(media.get(k) == "bt709" for k in ("color_space", "color_transfer", "color_primaries"))
            and checker.get("decode", {}).get("frames") == 1200
            and checker.get("decode", {}).get("returncode") == 0,
            f"Film {film.number:02d} checker media metadata does not match the delivery")
    audio_streams = media.get("audio_streams", [])
    require(isinstance(audio_streams, list) and audio_streams
            and all(s.get("codec_name") == "aac" and str(s.get("sample_rate")) == "48000"
                    and s.get("channels") == 2 for s in audio_streams),
            f"Film {film.number:02d} requires stereo AAC audio at 48000 Hz")

    actual = sha256(master)
    snapshots[master] = actual
    for label, expected in (("checker", checker.get("sha256")),
                            ("pipeline QA", qa.get("master_sha256")),
                            ("visual review", visual.get("master_sha256")),
                            ("assembly", assembly.get("sha256"))):
        require(actual == hash_value(expected, f"film {film.number:02d} {label}"),
                f"Film {film.number:02d} master hash does not match {label}")
    require(checker.get("size_bytes") == master.stat().st_size,
            f"Film {film.number:02d} master size changed after its checker report")
    registered_audio = project.get("audio", {})
    audio_path = repo_file(root, registered_audio.get("source"), f"film {film.number:02d} audio")
    audio_hash = sha256(audio_path)
    snapshots[audio_path] = audio_hash
    require(audio_hash == hash_value(registered_audio.get("source_sha256"), "registered audio")
            and audio_hash == hash_value(assembly.get("audio_source_sha256"), "assembled audio"),
            f"Film {film.number:02d} registered or assembled audio hash does not match")
    require(registered_audio.get("offset_seconds", 0) == 0,
            f"Film {film.number:02d} audio offset differs from this delivery contract")

    def report(path, content):
        return {"path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
                "sha256": snapshots[path], "content": content}

    record = {
        "film_id": film.number, "title": film.title, "filename": film.filename,
        "source_master": str(master.relative_to(root)), "sha256": actual,
        "size_bytes": master.stat().st_size, "media": media,
        "audio": {"source": str(audio_path.relative_to(root)), "source_sha256": audio_hash,
                  "source_size_bytes": audio_path.stat().st_size, "offset_seconds": 0,
                  "embedded_streams": audio_streams, "timing_declaration": project.get("timing", {})},
        "render": {"fingerprint": rendered["fingerprint"], "complete": True,
                   "frames": 1200, "receipt_sha256": snapshots[render_path],
                   "provenance": rendered.get("provenance", {})},
        "project_manifest_sha256": snapshots[project_path],
        "reports": {"movie_checker": report(checker_path, checker),
                    "pipeline_qa": report(qa_path, qa), "visual_review": report(visual_path, visual),
                    "assembly": report(assembly_path, assembly)},
    }
    return master, record


def existing_identical(path, expected):
    if not path.exists() and not path.is_symlink():
        return False
    require(path.is_file(), f"Destination exists but is not a file: {path}")
    require(sha256(path) == expected,
            f"Destination has different content; refusing to replace it: {path}")
    return True


def make_overview(root, ffmpeg, movies, stage):
    from PIL import Image, ImageDraw, ImageFont

    font_file = root / "fonts/jost-latin-500-normal.ttf"
    require(font_file.is_file(), f"Overview font is missing: {font_file}")
    heading = ImageFont.truetype(str(font_file), 44)
    title_font = ImageFont.truetype(str(font_file), 30)
    small = ImageFont.truetype(str(font_file), 21)
    width, header, row_height, footer = 2400, 148, 395, 54
    canvas = Image.new("RGB", (width, header + 10 * row_height + footer), "#0b1020")
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 20), "Ten Cinematic Films", font=heading, fill="#f5edda")
    draw.text((56, 78), "Native 1080p60 | 20 seconds each | Frames decoded from the delivered masters",
              font=small, fill="#bdc6da")
    for col, index in enumerate(OVERVIEW_FRAMES):
        draw.text((56 + col * 576, 116), f"{index / 60:.3f} seconds", font=small, fill="#dcc490")
    frames_dir = stage / "overview-frames"
    frames_dir.mkdir()
    selection = "+".join(f"eq(n\\,{index})" for index in OVERVIEW_FRAMES)
    for row, (film, movie) in enumerate(zip(FILMS, movies)):
        template = frames_dir / f"film{film.number:02d}_%02d.png"
        result = subprocess.run([
            ffmpeg, "-v", "error", "-nostdin", "-y", "-threads", "2",
            "-filter_threads", "1", "-i", str(movie), "-map", "0:v:0", "-an",
            "-vf", f"select={selection},scale=560:315:flags=lanczos", "-fps_mode", "passthrough",
            "-frames:v", "4", str(template),
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=180)
        require(result.returncode == 0,
                f"Overview decode failed for film {film.number:02d}: {result.stderr[-1000:]}")
        decoded = sorted(frames_dir.glob(f"film{film.number:02d}_*.png"))
        require(len(decoded) == 4, f"Overview did not decode four frames for film {film.number:02d}")
        y = header + row * row_height
        if row % 2 == 0:
            draw.rectangle((32, y - 5, width - 32, y + row_height - 10), fill="#10182a")
        draw.text((56, y + 1), f"{film.number:02d}  {film.title}", font=title_font, fill="#f1e9db")
        for col, path in enumerate(decoded):
            with Image.open(path) as image:
                require(image.size == (560, 315), f"Unexpected overview image dimensions: {path}")
                canvas.paste(image.convert("RGB"), (56 + col * 576, y + 48))
            draw.rectangle((55 + col * 576, y + 47, 616 + col * 576, y + 363), outline="#2c3650")
        print(f"Overview row {film.number:02d}/10 decoded", flush=True)
    draw.text((56, canvas.height - 41), "Four samples per film: frames 120, 480, 840 and 1199 of 1200.",
              font=small, fill="#bdc6da")
    path = stage / OVERVIEW_NAME
    canvas.save(path, format="JPEG", quality=94, subsampling=0, optimize=True)
    return path, canvas.size


def readme_text():
    rows = "\n".join(f"| {film.number:02d} | {film.title} | `{film.filename}` |" for film in FILMS)
    return f"""# Ten Cinematic Films

Ten original, twenty-second films authored in the established concert 3D world.
The scenes use original motion scores, articulated characters, native geometry,
reflections and moving cameras. Supplied reference recordings informed gesture
and composition; the authored performances are not presented as motion capture.

## Playback

Every MP4 contains 1,200 frames at 1920 x 1080 and 60 fps, with a duration of
20.000 seconds. Delivery is H.264, Rec.709 SDR, with stereo AAC audio at 48 kHz.
The movies are byte-for-byte copies of the completed, technically checked
production masters. Packaging does not resize, retime or re-encode them.

## Films

| Number | Title | Movie |
| --- | --- | --- |
{rows}

## Included records

- `{OVERVIEW_NAME}` has four decoded frames per film, at 2.000, 8.000,
  14.000 and 19.983 seconds, arranged in ten titled rows.
- `{TECHNICAL_NAME}` contains the individual movie-checker reports, pipeline
  QA, scoped visual reviews, assembly records, audio identities, source provenance
  and SHA256 hashes.
- `{CHECKSUM_NAME}` lists the hashes of the ten movies, overview and documents.

The technical records describe media validation. They do not record owner
approval or claim that pixel checks establish artistic quality or natural motion.
The audio follows the authored visual clock; instrument-level synchronization
is not claimed by the production timing declarations.

Frozen picture source commit: `{FROZEN_PICTURE_COMMIT}`.
Assembly Git metadata is retained separately because delivery documentation and
other files outside the picture dependencies can be added after that freeze.

## Source and reusable motion

- [Project changes in GitHub PR 108]({PULL_REQUEST_URL})
- [Reusable cinematic motion: APIs, provenance and reviewed scope]({MOTION_DOCUMENT_URL})
"""


def unchanged(snapshots):
    for path, expected in snapshots.items():
        require(path.is_file() and sha256(path) == expected,
                f"Input changed during packaging; no complete package will be published: {path}")


def archive_date(records):
    dates = []
    for record in records:
        value = record["reports"]["assembly"]["content"].get("created_utc")
        require(isinstance(value, str), "An assembly receipt has no creation time")
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(date.tzinfo is not None and 1980 <= date.year <= 2107, "Invalid assembly UTC timestamp")
        dates.append(date.astimezone(timezone.utc))
    return max(dates).timetuple()[:6]


def make_archive(path, members, hashes, date):
    with zipfile.ZipFile(path, "w", allowZip64=True) as bundle:
        for name, source in members.items():
            entry = zipfile.ZipInfo(name, date_time=date)
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            if source.suffix.lower() in (".mp4", ".jpg"):
                entry.compress_type = zipfile.ZIP_STORED
                with source.open("rb") as src, bundle.open(entry, "w", force_zip64=True) as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
            else:
                bundle.writestr(entry, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as bundle:
        require(bundle.namelist() == list(members), "ZIP members do not match the complete delivery")
        for name, source in members.items():
            digest = hashlib.sha256()
            with bundle.open(name) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            require(digest.hexdigest() == hashes[name] and bundle.getinfo(name).file_size == source.stat().st_size,
                    f"ZIP member integrity failed: {name}")


def publish_without_overwrite(source, destination, expected):
    if existing_identical(destination, expected):
        return True
    try:
        os.link(source, destination)
    except FileExistsError:
        require(existing_identical(destination, expected), f"Destination appeared during publication: {destination}")
        return True
    require(sha256(destination) == expected, f"Published file hash changed: {destination}")
    return False


def package(root, destination, reports, ffmpeg):
    root, destination, reports = root.resolve(), destination.resolve(), reports.resolve()
    require(root.is_dir(), f"Checkout is missing: {root}")
    executable = shutil.which(ffmpeg)
    require(executable is not None, f"FFmpeg decoder is unavailable: {ffmpeg}")
    result = subprocess.run(["git", "cat-file", "-e", FROZEN_PICTURE_COMMIT + "^{commit}"],
                            cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    require(result.returncode == 0, "The frozen picture commit is absent from this checkout")
    snapshots, records, masters = {}, [], []
    for film in FILMS:
        master, record = validate_film(root, reports, film, snapshots)
        existing_identical(destination / film.filename, record["sha256"])
        masters.append(master)
        records.append(record)
        print(f"Validated film {film.number:02d}/10 and matching report hashes", flush=True)

    # All ten pass before creating staging or any new delivery file.
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".cinematic-ten-package-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        members, hashes = {}, {}
        for film, master, record in zip(FILMS, masters, records):
            target = destination / film.filename
            if existing_identical(target, record["sha256"]):
                members[film.filename] = target
            else:
                copy = stage / film.filename
                shutil.copy2(master, copy)
                require(sha256(copy) == record["sha256"], f"Copied master hash changed: {film.filename}")
                members[film.filename] = copy
            hashes[film.filename] = record["sha256"]
        overview, overview_size = make_overview(root, executable, masters, stage)
        readme = stage / "README.md"
        readme.write_text(readme_text(), encoding="utf-8")
        for path in (overview, readme):
            members[path.name], hashes[path.name] = path, sha256(path)
        technical = {
            "schema_version": 1, "collection": "Ten Cinematic Films", "film_count": 10,
            "frozen_picture_source_commit": FROZEN_PICTURE_COMMIT,
            "repository": "lovelaceaml-hub/concert-backdrops",
            "source_links": {"pull_request": PULL_REQUEST_URL, "reusable_motion_document": MOTION_DOCUMENT_URL},
            "authorship": "Original films and motion authored in code in the established native concert 3D world.",
            "creative_approval": "not_assessed", "expected_media": EXPECTED,
            "packaging": {"movie_reencoding": False, "identical_existing_files_preserved": True,
                          "all_ten_checker_reports_passed": True, "all_ten_pipeline_qa_reports_passed": True,
                          "all_ten_scoped_visual_reviews_found_no_blocking_defects": True,
                          "master_hashes_match_checker_pipeline_qa_and_assembly": True,
                          "master_hashes_match_scoped_visual_reviews": True,
                          "registered_audio_hashes_match": True,
                          "packaging_script_sha256": sha256(Path(__file__).resolve())},
            "overview": {"filename": OVERVIEW_NAME, "sha256": hashes[OVERVIEW_NAME],
                         "size_pixels": list(overview_size), "rows": 10, "frames_per_row": 4,
                         "decoded_frame_indices": list(OVERVIEW_FRAMES),
                         "seconds": [index / 60 for index in OVERVIEW_FRAMES]},
            "readme": {"filename": "README.md", "sha256": hashes["README.md"]},
            "films": records,
        }
        technical_path = stage / TECHNICAL_NAME
        technical_path.write_text(json.dumps(technical, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        members[TECHNICAL_NAME], hashes[TECHNICAL_NAME] = technical_path, sha256(technical_path)
        checksum_path = stage / CHECKSUM_NAME
        checksum_path.write_text("".join(f"{hashes[name]}  {name}\n" for name in members), encoding="ascii")
        members[CHECKSUM_NAME], hashes[CHECKSUM_NAME] = checksum_path, sha256(checksum_path)
        unchanged(snapshots)
        for name, source in members.items():
            require(sha256(source) == hashes[name], f"Staged or existing file changed: {name}")
            existing_identical(destination / name, hashes[name])
        archive = stage / ARCHIVE_NAME
        make_archive(archive, members, hashes, archive_date(records))
        archive_hash = sha256(archive)
        existing_identical(destination / ARCHIVE_NAME, archive_hash)
        unchanged(snapshots)
        destination.mkdir(parents=True, exist_ok=True)
        published = []
        for name, source in (*members.items(), (ARCHIVE_NAME, archive)):
            expected = archive_hash if name == ARCHIVE_NAME else hashes[name]
            reused = publish_without_overwrite(source, destination / name, expected)
            published.append({"filename": name, "sha256": expected,
                              "size_bytes": (destination / name).stat().st_size, "reused": reused})
        return {"status": "packaged", "film_count": 10, "archive_members": len(members),
                "deliverables": str(destination), "archive": str(destination / ARCHIVE_NAME),
                "archive_sha256": archive_hash, "files": published}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="Recovered concert checkout")
    parser.add_argument("--deliverables", type=Path, default=ROOT.parent / "deliverables",
                        help="Destination directory; matching files are preserved and differing files fail")
    parser.add_argument("--reports-dir", type=Path,
                        help="Per-film checker directory, default: REPO/work/cinematic-ten/qa/final-masters")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable used only to decode overview frames")
    args = parser.parse_args(argv)
    reports = args.reports_dir or args.repo_root / "work/cinematic-ten/qa/final-masters"
    try:
        result = package(args.repo_root, args.deliverables, reports, args.ffmpeg)
    except (DeliveryError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Packaging failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
