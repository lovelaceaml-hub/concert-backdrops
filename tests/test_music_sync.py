"""Focused unit tests for tools/music_sync (synthetic signals and mocks, no model downloads)."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import types

import numpy as np
import pytest

from tools.music_sync.align import (
    align_audio_arrays,
    retime,
    retime_cues,
    retime_phrases,
)
from tools.music_sync.analyze import STEM_NAMES, analyze_audio, compute_tempo_curve, validate_sync_data
from tools.music_sync.cli import main as cli_main
from tools.music_sync.cues import build_cues, export_cues, seconds_to_timecode
from tools.music_sync.io import file_sha256, write_wav
from tools.music_sync.lyrics import extract_lyrics


def _sample_sync_data(duration: float = 60.0) -> dict:
    return {
        "schema_version": 1,
        "source": {
            "filename": "demo_song.wav",
            "sha256": "a" * 64,
            "sample_rate": 22050,
        },
        "duration_seconds": duration,
        "tempo_bpm": 120.0,
        "tempo_curve": [
            {"time": 0.75, "bpm": 120.0},
            {"time": 1.25, "bpm": 120.0},
        ],
        "beats": [0.5, 1.0, 1.5, 2.0, 2.5],
        "downbeats": [0.5, 2.5],
        "sections": [
            {"name": "Section 1", "start": 0.0, "end": 18.5, "energy": 0.35},
            {"name": "Section 2", "start": 18.5, "end": 42.25, "energy": 0.82},
            {"name": "Section 3", "start": 42.25, "end": duration, "energy": 0.55},
        ],
        "stem_hits": {
            "vocals": [{"time": 4.2, "strength": 0.7}],
            "drums": [{"time": 0.5, "strength": 1.0}, {"time": 1.0, "strength": 0.6}],
            "bass": [{"time": 0.5, "strength": 0.8}],
            "other": [{"time": 1.5, "strength": 0.4}],
        },
        "stem_energy": {
            "frame_hop_seconds": 0.1,
            "stems": {name: {"rms_mean": 0.1, "rms_peak": 0.5, "curve": [0.2, 0.4]} for name in STEM_NAMES},
        },
        "tools": {
            "stem_separation": {"method": "demucs.htdemucs", "version": "4.0.1", "device": "cpu"},
            "beat_tracking": {"method": "beat_this.final0", "version": "1.1.0", "device": "cpu", "fallback_used": False},
            "stem_onsets": {"method": "librosa.onset", "version": "0.11.0"},
            "sections": {"method": "librosa.chroma_mfcc_self_similarity", "version": "0.11.0"},
        },
        "manually_verified": False,
    }


def _load_live_parse_cues():
    root = Path(__file__).resolve().parents[1]
    live_path = root / "engine" / "live.py"
    spec = importlib.util.spec_from_file_location("concert_engine_live_test", live_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_cues


# -------------------------------------------------------------------- retime() tests


def test_retime_scalar_and_sequence_interpolation_and_extrapolation():
    tempo_map = {
        "anchors": [
            [1.0, 2.0],
            [11.0, 12.0],  # 1.0x section
            [21.0, 27.0],  # 1.5x slower section
        ],
        "overall_stretch": 1.25,
    }

    # Exact anchors and midpoints.
    assert retime(1.0, tempo_map) == pytest.approx(2.0)
    assert retime(6.0, tempo_map) == pytest.approx(7.0)
    assert retime(16.0, tempo_map) == pytest.approx(19.5)
    assert retime(21.0, tempo_map) == pytest.approx(27.0)

    # Extrapolation before first anchor and after last anchor using overall_stretch.
    assert retime(0.0, tempo_map) == pytest.approx(0.75)
    assert retime(25.0, tempo_map) == pytest.approx(32.0)

    # Sequence input returns a fresh list and never mutates the caller's list.
    original = [1.0, 11.0, 16.0]
    snapshot = list(original)
    retimed = retime(original, tempo_map)
    assert original == snapshot
    assert retimed == pytest.approx([2.0, 12.0, 19.5])

    # Accepts raw anchor list directly too.
    assert retime([0.0, 5.0, 10.0], [(0.0, 0.5), (10.0, 11.5)]) == pytest.approx([0.5, 6.0, 11.5])


def test_retime_rejects_invalid_or_non_monotonic_maps():
    with pytest.raises(ValueError):
        retime(1.0, {"anchors": []})
    with pytest.raises(ValueError):
        retime(1.0, {"anchors": [[2.0, 2.0], [1.0, 3.0]]})
    with pytest.raises(ValueError):
        retime(1.0, {"anchors": [[0.0, 5.0], [10.0, 4.0]]})
    with pytest.raises(ValueError):
        retime(float("nan"), {"anchors": [[0.0, 0.0], [10.0, 10.0]]})


def test_retime_cues_and_phrases_preserve_sentinels_and_purity():
    tempo_map = {
        "anchors": [[0.0, 1.0], [10.0, 12.0], [20.0, 24.0]],
        "overall_stretch": 1.15,
    }
    cues = [("Opening", 0.0, None), ("Verse 1", 10.0, 20.0)]
    retimed_cues = retime_cues(cues, tempo_map)
    assert retimed_cues == [("Opening", 1.0, None), ("Verse 1", 12.0, 24.0)]
    assert cues == [("Opening", 0.0, None), ("Verse 1", 10.0, 20.0)]

    phrases = [
        {"label": "Greeting", "form": 5.0, "hold": 10.0, "star": -100.0, "arrive": [10.0, 20.0]},
        {"label": "Future", "form": 1e9, "hold": 1e9, "star": 1e9},
    ]
    retimed_phrases = retime_phrases(phrases, tempo_map)
    assert retimed_phrases[0]["form"] == pytest.approx(6.5)
    assert retimed_phrases[0]["hold"] == pytest.approx(12.0)
    assert retimed_phrases[0]["star"] == -100.0
    assert retimed_phrases[0]["arrive"] == pytest.approx([12.0, 24.0])
    assert retimed_phrases[1]["form"] == 1e9
    assert retimed_phrases[1]["star"] == 1e9
    # Input list and dicts are untouched.
    assert phrases[0]["form"] == 5.0
    assert phrases[0]["arrive"] == [10.0, 20.0]


# -------------------------------------------------------------------- cue export tests


def test_seconds_to_timecode_60fps():
    assert seconds_to_timecode(0.0, 60) == "00:00:00:00"
    assert seconds_to_timecode(1.5, 60) == "00:00:01:30"
    assert seconds_to_timecode(65.25, 60) == "00:01:05:15"
    assert seconds_to_timecode(3661.0, 60) == "01:01:01:00"
    with pytest.raises(ValueError):
        seconds_to_timecode(-0.1, 60)


def test_export_cues_matches_engine_live_and_csv(tmp_path: Path):
    sync_path = tmp_path / "sync.json"
    sync_data = _sample_sync_data(duration=60.0)
    sync_path.write_text(json.dumps(sync_data), encoding="utf-8")

    out_dir = tmp_path / "cues_out"
    cues_py, cues_csv = export_cues(sync_path, out_dir)
    assert cues_py.is_file()
    assert cues_csv.is_file()

    # Load generated cues.py and verify engine/live.py:parse_cues accepts it verbatim.
    namespace: dict = {}
    exec(cues_py.read_text(encoding="utf-8"), namespace)
    song_stub = types.SimpleNamespace(CUES=namespace["CUES"], TOTAL=namespace["TOTAL"])
    parse_cues = _load_live_parse_cues()
    parsed = parse_cues(song_stub)
    assert parsed == [
        ("Section 1", 0.0, None),
        ("Section 2", 18.5, None),
        ("Section 3", 42.25, None),
    ]

    # Verify cues.csv columns and 60 fps timecodes.
    with cues_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows == [
        ["name", "start_seconds", "start_timecode_60fps"],
        ["Section 1", "0.0000", "00:00:00:00"],
        ["Section 2", "18.5000", "00:00:18:30"],
        ["Section 3", "42.2500", "00:00:42:15"],
    ]

    # Verify loop_sections=True also passes engine/live.py:parse_cues.
    loop_cues = build_cues(sync_data, loop_sections=True)
    parsed_loop = parse_cues(types.SimpleNamespace(CUES=loop_cues, TOTAL=60.0))
    assert parsed_loop == [
        ("Section 1", 0.0, 18.5),
        ("Section 2", 18.5, 42.25),
        ("Section 3", 42.25, 60.0),
    ]


def test_cli_cues_with_tempo_map(tmp_path: Path):
    sync_path = tmp_path / "sync.json"
    sync_path.write_text(json.dumps(_sample_sync_data(duration=60.0)), encoding="utf-8")
    tmap_path = tmp_path / "tempo_map.json"
    tmap_path.write_text(
        json.dumps({"anchors": [[0.0, 1.0], [60.0, 67.0]], "overall_stretch": 1.1}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "cli_out"
    rc = cli_main(["cues", str(sync_path), "--out", str(out_dir), "--tempo-map", str(tmap_path)])
    assert rc == 0
    with (out_dir / "cues.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[1][1] == "1.0000"
    assert rows[1][2] == "00:00:01:00"


# -------------------------------------------------------------------- sync.json schema & synthetic analyze


def test_validate_sync_data_accepts_valid_and_rejects_bad_schema():
    valid = _sample_sync_data()
    validate_sync_data(valid)

    bad_sha = _sample_sync_data()
    bad_sha["source"]["sha256"] = "not-a-sha"
    with pytest.raises(ValueError, match="sha256"):
        validate_sync_data(bad_sha)

    bad_stem = _sample_sync_data()
    del bad_stem["stem_hits"]["drums"]
    with pytest.raises(ValueError, match="drums"):
        validate_sync_data(bad_stem)

    bad_strength = _sample_sync_data()
    bad_strength["stem_hits"]["drums"].append({"time": 2.0, "strength": 1.5})
    with pytest.raises(ValueError, match="strength"):
        validate_sync_data(bad_strength)

    bad_gap = _sample_sync_data()
    bad_gap["sections"][1]["start"] = 20.0
    with pytest.raises(ValueError, match="contiguous"):
        validate_sync_data(bad_gap)

    bad_verified = _sample_sync_data()
    bad_verified["manually_verified"] = "no"
    with pytest.raises(ValueError, match="manually_verified"):
        validate_sync_data(bad_verified)


def test_analyze_audio_synthetic_signals_with_mocks(tmp_path: Path):
    sr = 22050
    dur = 4.0
    t = np.arange(int(sr * dur), dtype=np.float32) / sr

    # Synthetic drum clicks every 0.5 s (120 BPM).
    drums = np.zeros_like(t)
    for click_t in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        idx = int(click_t * sr)
        burst_len = int(0.03 * sr)
        env = np.exp(-np.linspace(0.0, 6.0, burst_len)).astype(np.float32)
        drums[idx : idx + burst_len] += 0.9 * env * np.sin(2.0 * np.pi * 120.0 * np.arange(burst_len) / sr)

    # Synthetic bass pulse every 1.0 s, harmonic pad in other, silent vocals.
    bass = (0.4 * np.sin(2.0 * np.pi * 65.4 * t) * (0.5 + 0.5 * np.sin(2.0 * np.pi * 1.0 * t))).astype(np.float32)
    other = (0.3 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.float32)
    vocals = np.zeros_like(t)
    mix = np.clip(drums + bass + other, -1.0, 1.0)

    mix_wav = tmp_path / "synthetic_mix.wav"
    write_wav(mix_wav, mix, sr)

    def mock_separator(_audio_path: Path, stems_dir: Path):
        stems_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "drums": write_wav(stems_dir / "drums.wav", drums, sr),
            "bass": write_wav(stems_dir / "bass.wav", bass, sr),
            "other": write_wav(stems_dir / "other.wav", other, sr),
            "vocals": write_wav(stems_dir / "vocals.wav", vocals, sr),
        }
        return paths, {"method": "mock.htdemucs", "version": "0.0-test", "device": "cpu"}

    def mock_beats(_y: np.ndarray, _sr: int):
        beats = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        downbeats = [0.5, 2.5]
        return beats, downbeats, {"method": "mock.beat_this", "version": "0.0-test", "device": "cpu", "fallback_used": False}

    out_dir = tmp_path / "out"
    sync_path = analyze_audio(mix_wav, out_dir, separator=mock_separator, beat_tracker=mock_beats)
    assert sync_path == out_dir / "sync.json"

    data = json.loads(sync_path.read_text(encoding="utf-8"))
    validate_sync_data(data)
    assert data["source"]["filename"] == "synthetic_mix.wav"
    assert data["source"]["sha256"] == file_sha256(mix_wav)
    assert data["manually_verified"] is False
    assert data["tempo_bpm"] == pytest.approx(120.0, abs=0.5)
    assert len(data["tempo_curve"]) >= 4
    assert data["beats"] == [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    assert data["downbeats"] == [0.5, 2.5]
    # Drum clicks produce hits; silent vocals stem produces zero hits.
    assert len(data["stem_hits"]["drums"]) >= 4
    assert data["stem_hits"]["vocals"] == []


def test_compute_tempo_curve_handles_short_and_steady_beats():
    assert compute_tempo_curve([]) == ([], 0.0)
    assert compute_tempo_curve([1.0]) == ([], 0.0)
    curve, bpm = compute_tempo_curve([0.0, 0.5, 1.0, 1.5, 2.0])
    assert bpm == pytest.approx(120.0)
    assert len(curve) == 4


def test_extract_lyrics_uses_vocals_stem_when_present(tmp_path: Path):
    mix_wav = write_wav(tmp_path / "song.wav", np.zeros(22050, dtype=np.float32), 22050)
    out_dir = tmp_path / "out"
    vocals_wav = write_wav(out_dir / "stems" / "vocals.wav", np.zeros(22050, dtype=np.float32), 22050)

    seen_paths: list[Path] = []

    def mock_transcriber(audio_path: Path, language: str, model_size: str):
        seen_paths.append(audio_path)
        return (
            [{"word": "peace", "start": 0.25, "end": 0.75, "confidence": 0.94}],
            {"detected_language": language, "language_probability": 0.99, "tool": {"method": "faster_whisper", "model": model_size, "version": "test"}},
        )

    words_path = extract_lyrics(mix_wav, out_dir, language="en", transcriber=mock_transcriber)
    assert seen_paths == [vocals_wav]
    payload = json.loads(words_path.read_text(encoding="utf-8"))
    assert payload["source"]["audio_used"] == "vocals_stem"
    assert payload["manually_verified"] is False
    assert payload["words"] == [{"word": "peace", "start": 0.25, "end": 0.75, "confidence": 0.94}]


def test_align_audio_arrays_synthetic_tempo_stretch():
    pytest.importorskip("librosa")
    sr = 22050

    def make_melody(scale: float) -> np.ndarray:
        # Three distinct musical pitches (C4, E4, G4) stretched by `scale`.
        parts = []
        for freq, base_dur in ((261.63, 1.0), (329.63, 1.0), (392.00, 1.0)):
            n = int(round(sr * base_dur * scale))
            t = np.arange(n, dtype=np.float32) / sr
            sig = 0.5 * np.sin(2.0 * np.pi * freq * t) + 0.2 * np.sin(2.0 * np.pi * 2.0 * freq * t)
            parts.append(sig.astype(np.float32))
        return np.concatenate(parts)

    studio = make_melody(1.0)
    live = make_melody(1.15)
    tmap = align_audio_arrays(studio, live, sr=sr, anchor_step=0.75, hop_length=512)

    anchors = tmap["anchors"]
    assert len(anchors) >= 3
    studio_pts = [a[0] for a in anchors]
    live_pts = [a[1] for a in anchors]
    assert all(b > a for a, b in zip(studio_pts, studio_pts[1:]))
    assert all(b >= a for a, b in zip(live_pts, live_pts[1:]))
    assert 1.05 <= tmap["overall_stretch"] <= 1.25
    assert 0.5 <= tmap["confidence"] <= 1.0
    assert tmap["manually_verified"] is False
    # Round-trip check through retime().
    mid_live = retime(1.5, tmap)
    assert 1.4 <= mid_live <= 2.1
