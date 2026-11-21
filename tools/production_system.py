"""Portable, read-first entry point for the shared concert production system.

No network credentials, uploads, paid dispatch or rendering are hidden here.
Rendering belongs to scripts/video. Full recordings stay in ignored work/.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ROOT / "project-docs/production-system"
SONGS = SYSTEM / "catalogs/songs.json"
REFERENCES = SYSTEM / "catalogs/references.json"
MODELS = SYSTEM / "catalogs/models.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path escapes checkout: {relative}")
    return path


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".concert-", delete=False) as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        temporary = stream.name
    os.replace(temporary, path)


def song_record(song_id):
    song_id = "s" + song_id.removeprefix("s").zfill(2)
    return next(song for song in read(SONGS)["songs"] if song["id"] == song_id)


def source_path(song):
    return inside(song["audio"]["source"]["local_path"])


def check_audio(song, decode=False):
    source = song["audio"]["source"]
    path = source_path(song)
    result = {"song": song["id"], "path": str(path), "present": path.is_file(),
              "expected_sha256": source.get("sha256"), "verified": False}
    if not path.is_file():
        result["action"] = "Download the cataloged Drive file to this private path."
        return result
    result["sha256"] = digest(path)
    result["bytes"] = path.stat().st_size
    result["verified"] = bool(source.get("sha256")) and result["sha256"] == source["sha256"]
    if not result["verified"]:
        result["error"] = "Recording bytes differ from the selected source; do not reuse its cues."
        return result
    if decode:
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
            "stream=codec_name,sample_rate,channels:format=duration", "-of", "json", str(path)
        ], text=True))
        subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path),
                        "-map", "0:a:0", "-f", "null", "-"], check=True)
        result["probe"] = probe
        result["decoded_without_errors"] = True
    return result


def validate_catalogs():
    errors = []
    songs = read(SONGS)["songs"]
    if {s["id"] for s in songs} != {f"s{i:02}" for i in range(1, 12)} or len(songs) != 11:
        errors.append("The song catalog must contain s01 through s11 exactly once.")
    for song in songs:
        source = song["audio"]["source"]
        if len(source.get("sha256") or "") != 64 or not source.get("file_id"):
            errors.append(f"{song['id']}: missing selected source identity")
        source_path(song)
    models = read(MODELS)
    ids = set()
    for model in models["models"]:
        if model["id"] in ids:
            errors.append(f"Duplicate model: {model['id']}")
        ids.add(model["id"])
        for path in model["source_paths"]:
            if not inside(path).is_file():
                errors.append(f"{model['id']}: missing source {path}")
        if model.get("code_only_eligible") and model.get("provenance") == "generated_raster":
            errors.append(f"Generated raster marked eligible: {model['id']}")
    references = read(REFERENCES)
    for item in references["references"]:
        if item["status"] == "owner_approved" and not item.get("approval_evidence"):
            errors.append(f"Approval has no evidence: {item['id']}")
    return errors


def status(as_json=False):
    catalog = read(SONGS)
    rows = []
    for song in catalog["songs"]:
        src = song["audio"]["source"]
        rows.append({"id": song["id"], "title": song["title"],
                     "audio_present": source_path(song).is_file(),
                     "sha256_cataloged": bool(src.get("sha256")),
                     "live_rehearsal_verified": song["duration"]["live_rehearsal_verified"]})
    result = {"catalog_errors": validate_catalogs(), "songs": rows,
              "start_here": "project-docs/production-system/START-HERE.md",
              "render_projects": ["approved-light-s11", "concert-kit-consideration"],
              "note": "Presence is not a fresh hash check. Run verify-audio before analysis or rendering."}
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for row in rows:
            print(f"{row['id']}  {'present' if row['audio_present'] else 'download needed':15}  {row['title']}")
        print("\n" + result["note"])
        print("Read " + result["start_here"])
        print("Catalog checks: " + ("PASS" if not result["catalog_errors"] else "; ".join(result["catalog_errors"])))
    return 1 if result["catalog_errors"] else 0


def plan(song_id, output=None):
    song = song_record(song_id)
    data = {"schema_version": 1, "song_id": song["id"], "title": song["title"],
            "status": "authored_scene_required", "source": song["audio"]["source"],
            "source_check": check_audio(song), "historical_world": song["historical_world"],
            "expression_continuity": song["expressions"],
            "enhancement_proposal": song["enhancement_proposal"],
            "historical_delivery": song["existing_film"],
            "unresolved": song["unresolved"],
            "references": ["promo-nine-colours-r3", "song11-beauty-30s"],
            "next_steps": [
                "Read current Drive rules, song status, and immutable reference records.",
                "Verify the selected recording and write its source clock before timing a scene.",
                "Choose reviewed models and one meaningful performance; inspect close contact.",
                "Author three full-size keyframes and a short moving proof before a full film.",
                "Record the scene, source-dependent cues, colors, camera and output profile.",
                "Use scripts/video produce for an explicitly registered project; resume verified frames.",
                "Review the actual complete output, archive hashes and direct links, then update status."
            ],
            "render_command": None,
            "render_command_reason": "A catalog proposal is not an authored full-song scene."
            }
    path = Path(output) if output else ROOT / f"work/song-plans/{song['id']}.json"
    if path.exists():
        raise ValueError(f"Plan exists; preserve authored work and choose another --out: {path}")
    write_json(path, data)
    print(path)
    return 0


def study_audio_receipt(out, source_sha, container_sha, pcm_sha):
    write_json(out.with_name("audio-provenance.json"), {
        "source_song": "s07", "source_sha256": source_sha,
        "source_drive_id": "1wL9dyLETDn3q9ECkIXKrDb3UIt_eAgEA",
        "source_start_seconds": 137.5, "source_end_seconds": 155.5,
        "duration_seconds": 18.0, "rate": 48000, "channels": 2,
        "samples_per_channel": 864000, "gain_db": -1.0,
        "fade_in_seconds": 0.08, "fade_out_seconds": 0.35, "time_stretch": False,
        "intended_world_response_seconds": 11.5,
        "cue_status": "Source timeline form transition, not individually ear-verified onset",
        "prepared_sha256": container_sha, "pcm_s24le_sha256": pcm_sha,
        "container": "canonical Python wave PCM24 header without encoder metadata",
        "prepared_path": str(out.relative_to(ROOT))
    })


def prepare_study_audio():
    song = song_record("s07")
    checked = check_audio(song)
    if not checked["verified"]:
        raise ValueError(json.dumps(checked))
    out = ROOT / "work/concert-kit/consideration-score.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    expected = "0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b"
    expected_pcm = "493d1fa5efeaea437edcfecb241fb536439ec832d6f899750c4282c0d6895f84"
    if out.exists():
        if digest(out) == expected:
            study_audio_receipt(out, checked["sha256"], expected, expected_pcm)
            print(f"Verified prepared audio: {out}")
            return 0
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
            "stream=sample_rate,channels", "-of", "json", str(out)
        ], text=True))["streams"][0]
        if int(probe["sample_rate"]) != 48000 or probe["channels"] != 2:
            raise ValueError("Existing prepared audio has the wrong rate or channel count.")
        pcm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(out), "-map", "0:a:0",
                                       "-c:a", "pcm_s24le", "-f", "s24le", "-"])
    else:
        pcm = subprocess.check_output([
            "ffmpeg", "-v", "error", "-i", str(source_path(song)), "-af",
            "atrim=start=137.5:end=155.5,asetpts=PTS-STARTPTS,volume=-1dB,"
            "afade=t=in:st=0:d=0.08,afade=t=out:st=17.65:d=0.35",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", "-f", "s24le", "-"
        ])
    if len(pcm) != 864000 * 2 * 3 or hashlib.sha256(pcm).hexdigest() != expected_pcm:
        raise ValueError("Prepared PCM samples differ from reference; existing audio is preserved. Check source, filters and decoder version.")
    # A canonical PCM WAV has no host-specific FFmpeg encoder tag. Verify the
    # audio samples before writing the stable container, not only its header.
    temporary = out.with_name("consideration-score.pending.wav")
    with wave.open(str(temporary), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(3)
        stream.setframerate(48000)
        stream.writeframes(pcm)
    actual = digest(temporary)
    if actual != expected:
        raise ValueError(f"Canonical WAV differs ({actual}); pending file retained.")
    if out.exists():
        backup = out.with_name("consideration-score.original-container.wav")
        if backup.exists() and digest(backup) != digest(out):
            raise ValueError("An earlier container backup differs; preserve it elsewhere before normalizing this one.")
        if not backup.exists():
            backup.write_bytes(out.read_bytes())
    os.replace(temporary, out)
    study_audio_receipt(out, checked["sha256"], actual, expected_pcm)
    print(f"Prepared and verified: {out}")
    return 0


def restore(manifest, directory, output):
    data = read(manifest)
    directory, output = Path(directory).resolve(), Path(output).resolve()
    if output.exists():
        if digest(output) == data["sha256"]:
            print(f"Already restored and verified: {output}")
            return 0
        raise ValueError("Output already exists with different bytes; choose a new output path.")
    parts = []
    for item in data["parts"]:
        path = (directory / item["filename"]).resolve()
        if path.parent != directory or path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise ValueError(f"Invalid archive part: {item['filename']}")
        parts.append(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".restoring")
    if temporary.exists():
        raise ValueError(f"A previous restore is present: {temporary}")
    with temporary.open("xb") as target:
        for path in parts:
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    target.write(block)
    if temporary.stat().st_size != data["bytes"] or digest(temporary) != data["sha256"]:
        raise ValueError("Restored master checksum failed; temporary file retained for diagnosis.")
    os.replace(temporary, output)
    print(f"Exact original restored: {output}")
    return 0


def export_handoff(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError("Handoff already exists; use a versioned output name.")
    files = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "GEMINI.md", ROOT / "README.md",
             ROOT / "project-docs/AGENTS.md", ROOT / "apps/README.md",
             ROOT / "tools/production_system.py", ROOT / "scripts/concert"]
    files += list((ROOT / "docs").rglob("*.md"))
    for directory in ("tools/concert_kit", "tools/concert_addons", "tools/concert_review", "tools/promo_beauty_example"):
        files += list((ROOT / directory).glob("*.md"))
    for project in ("approved-light-s11", "concert-kit-consideration"):
        files.append(ROOT / "projects" / project / "project.json")
    files += [p for p in SYSTEM.rglob("*") if p.is_file() and p.suffix in {".md", ".json"}]
    files = sorted({path for path in files if path.is_file()})
    git = lambda *args: subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    receipt = {"schema_version": 1, "exported_at_utc": datetime.now(timezone.utc).isoformat(),
               "producing_commit": git("rev-parse", "HEAD"),
               "producing_branch": git("branch", "--show-current"),
               "working_tree_dirty": bool(git("status", "--porcelain")),
               "files": {str(path.relative_to(ROOT)): {"bytes": path.stat().st_size,
                         "sha256": digest(path)} for path in files},
               "note": "When dirty is true, these exact exported file hashes identify the handoff; the commit alone does not identify all content."}
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, str(path.relative_to(ROOT)))
        archive.writestr("EXPORT-RECEIPT.json", json.dumps(receipt, indent=2) + "\n")
    print(f"Handoff saved: {output}  SHA256 {digest(output)}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("status"); p.add_argument("--json", action="store_true")
    commands.add_parser("verify-catalogs")
    p = commands.add_parser("verify-audio"); p.add_argument("song", nargs="?", default="all"); p.add_argument("--decode", action="store_true")
    p = commands.add_parser("song"); p.add_argument("song")
    p = commands.add_parser("plan"); p.add_argument("song"); p.add_argument("--out")
    commands.add_parser("prepare-study-audio")
    p = commands.add_parser("restore-master"); p.add_argument("--manifest", required=True); p.add_argument("--parts", required=True); p.add_argument("--out", required=True)
    p = commands.add_parser("export-handoff"); p.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "status": return status(args.json)
        if args.command == "verify-catalogs":
            errors = validate_catalogs(); print(json.dumps({"errors": errors}, indent=2)); return bool(errors)
        if args.command == "verify-audio":
            songs = read(SONGS)["songs"] if args.song == "all" else [song_record(args.song)]
            results = [check_audio(song, args.decode) for song in songs]
            print(json.dumps(results, indent=2)); return int(any(not r["verified"] for r in results))
        if args.command == "song": print(json.dumps(song_record(args.song), indent=2)); return 0
        if args.command == "plan": return plan(args.song, args.out)
        if args.command == "prepare-study-audio": return prepare_study_audio()
        if args.command == "restore-master": return restore(args.manifest, args.parts, args.out)
        if args.command == "export-handoff": return export_handoff(args.out)
    except (ValueError, KeyError, StopIteration, OSError, subprocess.CalledProcessError) as exc:
        print(f"Concert system: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
