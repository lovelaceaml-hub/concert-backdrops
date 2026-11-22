"""Prepare registered film manifests and exact twenty-second score excerpts.

Full recordings stay under ignored work/song-sources. No audio is added to Git.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

from tools.cinematic_ten.render import ROOT, TITLES

# Authored picture clocks are independent of these review score excerpts.
# The full recordings must match the production catalog before extraction.
SCORES = {
    1: ("work/song-sources/s07.mp3", 137.5),
    2: ("audio/promo/s03.mp3", 15.0),
    3: ("work/song-sources/s11.mp3", 97.8),
    4: ("audio/promo/s04.mp3", 12.0),
    5: ("work/song-sources/s07.mp3", 174.5),
    6: ("audio/promo/s05.mp3", 8.0),
    7: ("audio/promo/s08.mp3", 15.0),
    8: ("audio/promo/s06.mp3", 10.0),
    9: ("audio/promo/s01.mp3", 18.0),
    10: ("work/song-sources/s11.mp3", 218.0),
}
FULL_HASHES = {
    "work/song-sources/s07.mp3": "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a",
    "work/song-sources/s11.mp3": "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipts = []
    for film_id, title in TITLES.items():
        source, offset = SCORES[film_id]
        source_path = ROOT / source
        sha = digest(source_path)
        if source in FULL_HASHES and sha != FULL_HASHES[source]:
            raise RuntimeError("Source recording differs from production catalog: " + source)
        audio = ROOT / f"work/cinematic-ten/audio/film{film_id:02d}.wav"
        audio.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(offset), "-i", str(source_path), "-t", "20", "-vn",
            "-af", "afade=t=in:st=0:d=0.08,afade=t=out:st=19.3:d=0.7,volume=-1dB",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(audio)], check=True)
        score = dict(film_id=film_id, source=source, source_sha256=sha,
            source_offset_seconds=offset, duration_seconds=20, speed=1,
            opening_fade_seconds=.08, ending_fade_seconds=.7, gain_db=-1,
            output=str(audio.relative_to(ROOT)), sha256=digest(audio))
        receipts.append(score)
        pid = f"cinematic-ten-{film_id:02d}"
        settings = {"width": 1920, "height": 1080, "temporal_samples": 2, "image_bit_depth": 8}
        manifest = {
            "schema_version": 1, "project_id": pid, "title": title,
            "description": "An original twenty-second film authored in the established native concert 3D renderer.",
            "video": {"width": 1920, "height": 1080, "fps": 60},
            "production": {"cloud_gpu_provider": None, "allow_local_gpu": False,
                "allow_paid_services": False, "allow_ai_generated_visuals": False,
                "allow_stock_footage": False, "random_seed": 20261121,
                "threads": 1, "render_workers": 3 if film_id == 10 else 2,
                "render_chunk_frames": 50 if film_id == 10 else 300,
                "render_timeout_seconds": 7200},
            "quality": {
                "draft": {"width": 960, "height": 540, "temporal_samples": 1, "image_bit_depth": 8},
                "review": dict(settings), "final": dict(settings)},
            "delivery": {"profile": "h264", "source_transfer": "legacy_display_gamma", "color_space": "rec709"},
            "style": "styles/zion-cinematic.json",
            "audio": {"source": score["output"], "source_sha256": score["sha256"], "offset_seconds": 0},
            "timing": {"fps": 60, "visual_only": True, "manually_verified": False,
                "note": "Twenty seconds at original score speed. The acted visual clock does not claim instrument or transient alignment.",
                "events": []},
            "shots": [{"id": "film", "name": title, "renderer": "p3d-kit", "start_frame": 0,
                "end_frame_exclusive": 1200, "scene": f"tools/cinematic_ten/film{film_id:02d}.py", "params": {}}],
        }
        path = ROOT / "projects" / pid / "project.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2) + "\n")
    path = ROOT / "work/cinematic-ten/audio/receipt.json"
    path.write_text(json.dumps(receipts, indent=2) + "\n")
    print(json.dumps({"projects": len(receipts), "audio_receipt": str(path)}))


if __name__ == "__main__":
    main()
