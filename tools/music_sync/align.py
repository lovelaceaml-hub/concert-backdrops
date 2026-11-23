"""Studio-to-live audio alignment (chroma + DTW) and pure retiming helpers."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .io import MusicSyncError, decode_audio, file_sha256, package_version, read_json, write_json

SCHEMA_VERSION = 1


def _extract_anchors(tempo_map: dict[str, Any] | Iterable[Any]) -> tuple[np.ndarray, np.ndarray, float]:
    """Validate a tempo map and return (studio_times, live_times, stretch_slope)."""
    if isinstance(tempo_map, dict):
        raw_anchors = tempo_map.get("anchors")
        overall_stretch = tempo_map.get("overall_stretch")
    else:
        raw_anchors = list(tempo_map)
        overall_stretch = None

    if not isinstance(raw_anchors, (list, tuple)) or len(raw_anchors) == 0:
        raise ValueError("tempo_map must contain a non-empty 'anchors' list of (studio, live) pairs.")

    studio_list: list[float] = []
    live_list: list[float] = []
    for idx, pair in enumerate(raw_anchors):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError(f"tempo_map anchor {idx} must be a 2-item (studio, live) pair.")
        s_val, l_val = pair
        if isinstance(s_val, bool) or isinstance(l_val, bool):
            raise ValueError(f"tempo_map anchor {idx} cannot contain booleans.")
        s_f, l_f = float(s_val), float(l_val)
        if not (math.isfinite(s_f) and math.isfinite(l_f)):
            raise ValueError(f"tempo_map anchor {idx} must contain finite numbers.")
        studio_list.append(s_f)
        live_list.append(l_f)

    studio = np.asarray(studio_list, dtype=np.float64)
    live = np.asarray(live_list, dtype=np.float64)

    if studio.size >= 2:
        if np.any(np.diff(studio) <= 0.0):
            raise ValueError("tempo_map studio anchor times must be strictly increasing.")
        if np.any(np.diff(live) < -1e-9):
            raise ValueError("tempo_map live anchor times must be monotonically non-decreasing.")
        live = np.maximum.accumulate(live)

    slope: float | None = None
    if overall_stretch is not None and not isinstance(overall_stretch, bool):
        cand = float(overall_stretch)
        if math.isfinite(cand) and cand > 0.0:
            slope = cand
    if slope is None:
        if studio.size >= 2 and (studio[-1] - studio[0]) > 0.0:
            est = float((live[-1] - live[0]) / (studio[-1] - studio[0]))
            slope = est if (math.isfinite(est) and est > 0.0) else 1.0
        else:
            slope = 1.0

    return studio, live, slope


def _retime_scalar(t: float, studio: np.ndarray, live: np.ndarray, slope: float) -> float:
    if isinstance(t, bool) or not isinstance(t, (int, float, np.integer, np.floating)):
        raise ValueError(f"Time value must be a finite number, got {t!r}.")
    tf = float(t)
    if not math.isfinite(tf):
        raise ValueError(f"Time value must be finite, got {t!r}.")
    if tf < studio[0]:
        out = float(live[0] + (tf - studio[0]) * slope)
        if tf >= 0.0:
            out = max(0.0, out)
    elif tf > studio[-1]:
        out = float(live[-1] + (tf - studio[-1]) * slope)
    else:
        out = float(np.interp(tf, studio, live))
    return round(out, 6)


def retime(
    times: float | int | Iterable[float | int],
    tempo_map: dict[str, Any] | Iterable[Any],
) -> float | list[float]:
    """Pure function: convert studio-based time(s) to live performance time(s).

    Accepts either a single number (returning a float) or an iterable of numbers
    (returning a new list of floats). Uses piecewise linear interpolation inside the
    anchor range and linear extrapolation using overall_stretch outside it.
    """
    studio, live, slope = _extract_anchors(tempo_map)
    if isinstance(times, bool):
        raise ValueError("times cannot be a boolean.")
    if isinstance(times, (int, float, np.integer, np.floating)):
        return _retime_scalar(times, studio, live, slope)
    return [_retime_scalar(t, studio, live, slope) for t in times]


def retime_cues(
    cues: Iterable[tuple[str, float, float | None]],
    tempo_map: dict[str, Any] | Iterable[Any],
) -> list[tuple[str, float, float | None]]:
    """Pure function: retime an engine/live.py CUES list [(name, start, loop_end_or_None), ...]."""
    studio, live, slope = _extract_anchors(tempo_map)
    out: list[tuple[str, float, float | None]] = []
    for cue in cues:
        name, t0, t1 = cue
        new_t0 = _retime_scalar(float(t0), studio, live, slope)
        new_t1 = None if t1 is None else _retime_scalar(float(t1), studio, live, slope)
        out.append((str(name), new_t0, new_t1))
    return out


def _retime_phrase_value(val: float, studio: np.ndarray, live: np.ndarray, slope: float) -> float:
    """Retime a PHRASES timestamp while preserving engine sentinel values (< 0 or >= 1e8)."""
    fv = float(val)
    if fv < 0.0 or fv >= 1e8:
        return fv
    return _retime_scalar(fv, studio, live, slope)


def retime_phrases(
    phrases: Iterable[dict[str, Any]],
    tempo_map: dict[str, Any] | Iterable[Any],
) -> list[dict[str, Any]]:
    """Pure function: retime a song file's PHRASES list without mutating inputs.

    Retimes 'form', 'hold', 'star', and 'arrive' (single float or list of floats),
    leaving engine sentinel values such as star=-100.0 or form=1e9 unchanged.
    """
    studio, live, slope = _extract_anchors(tempo_map)
    out: list[dict[str, Any]] = []
    for phrase in phrases:
        updated = dict(phrase)
        for key in ("form", "hold", "star"):
            if key in updated and updated[key] is not None:
                updated[key] = _retime_phrase_value(updated[key], studio, live, slope)
        if "arrive" in updated and updated["arrive"] is not None:
            arrive = updated["arrive"]
            if isinstance(arrive, (list, tuple)):
                updated["arrive"] = [_retime_phrase_value(x, studio, live, slope) for x in arrive]
            else:
                updated["arrive"] = _retime_phrase_value(arrive, studio, live, slope)
        out.append(updated)
    return out


def _compute_chroma(y: np.ndarray, sr: int, hop_length: int) -> tuple[np.ndarray, str]:
    """Compute L2-normalized 12-bin chroma features with safe fallback for very short clips."""
    import librosa

    duration = len(y) / sr
    method = "librosa.chroma_cqt"
    if duration >= 2.0:
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
        except Exception:
            method = "librosa.chroma_stft"
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
    else:
        method = "librosa.chroma_stft"
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)

    chroma = np.asarray(chroma, dtype=np.float64)
    chroma = np.maximum(chroma, 0.0) + 1e-6
    norms = np.linalg.norm(chroma, axis=0, keepdims=True)
    chroma = chroma / np.maximum(norms, 1e-12)
    return chroma, method


def align_audio_arrays(
    studio_y: np.ndarray,
    live_y: np.ndarray,
    sr: int = 22050,
    *,
    bar_times: Iterable[float] | None = None,
    anchor_step: float = 2.0,
    hop_length: int = 1024,
    subseq: bool = False,
) -> dict[str, Any]:
    """Align a live audio array to a studio audio array using chroma features and DTW."""
    import librosa
    from scipy.spatial.distance import cdist

    studio_y = np.asarray(studio_y, dtype=np.float32).ravel()
    live_y = np.asarray(live_y, dtype=np.float32).ravel()
    if studio_y.size == 0 or live_y.size == 0:
        raise MusicSyncError("Cannot align empty audio arrays.")

    studio_dur = float(studio_y.size / sr)
    live_dur = float(live_y.size / sr)

    chroma_s, chroma_method = _compute_chroma(studio_y, sr, hop_length)
    chroma_l, _ = _compute_chroma(live_y, sr, hop_length)

    cost = cdist(chroma_s.T, chroma_l.T, metric="cosine")
    cost = np.nan_to_num(cost, nan=1.0, posinf=1.0, neginf=0.0)
    cost = np.clip(cost, 0.0, 1.0)

    # Full-track slope-constrained DTW by default; subsequence mode is opt-in for untrimmed recordings.
    use_subseq = bool(subseq and chroma_l.shape[1] >= chroma_s.shape[1] and chroma_s.shape[1] >= 4)
    slope_steps = np.array([[1, 1], [1, 2], [2, 1]], dtype=int)
    slope_weights = np.array([1.0, 1.5, 1.5], dtype=np.float64)

    try:
        _, wp = librosa.sequence.dtw(
            C=cost,
            step_sizes_sigma=slope_steps,
            weights_mul=slope_weights,
            subseq=use_subseq,
        )
    except Exception:
        use_subseq = False
        _, wp = librosa.sequence.dtw(C=cost, subseq=False)

    wp = np.asarray(wp, dtype=int)[::-1]  # chronological order: (studio_frame, live_frame)
    frame_sec = hop_length / float(sr)

    # Collapse duplicate studio frames to a strictly increasing studio timeline.
    unique_s_frames, inv = np.unique(wp[:, 0], return_inverse=True)
    l_for_s = np.empty(unique_s_frames.size, dtype=np.float64)
    for idx in range(unique_s_frames.size):
        l_for_s[idx] = float(np.median(wp[inv == idx, 1])) * frame_sec

    s_times = np.minimum(unique_s_frames.astype(np.float64) * frame_sec, studio_dur)
    l_times = np.clip(np.maximum.accumulate(l_for_s), 0.0, live_dur)

    # Remove any duplicate trailing studio timestamp introduced by clamping.
    keep_mask = np.concatenate([[True], np.diff(s_times) > 1e-6])
    s_times = s_times[keep_mask]
    l_times = l_times[keep_mask]

    if s_times.size == 0:
        raise MusicSyncError("DTW alignment produced no usable time points.")

    # Select anchor positions every bar (from sync downbeats) or every anchor_step seconds.
    t_start, t_end = float(s_times[0]), float(s_times[-1])
    candidates: list[float] = [t_start]
    if bar_times is not None:
        bars = sorted(float(b) for b in bar_times if t_start + 0.05 < float(b) < t_end - 0.05)
        candidates.extend(bars)
    if len(candidates) <= 1 and t_end > t_start:
        step = max(float(anchor_step), 0.25)
        grid = np.arange(t_start + step, t_end - 0.05, step)
        candidates.extend(float(x) for x in grid)
    if t_end > t_start + 1e-6:
        candidates.append(t_end)

    query_s = np.asarray(sorted(set(round(c, 4) for c in candidates)), dtype=np.float64)
    query_l = np.interp(query_s, s_times, l_times)
    query_l = np.maximum.accumulate(query_l)

    anchors = [[round(float(s), 4), round(float(l), 4)] for s, l in zip(query_s, query_l)]

    if s_times.size >= 2 and (s_times[-1] - s_times[0]) > 1e-6:
        stretch, offset = np.polyfit(s_times, l_times, 1)
        overall_stretch = float(stretch)
        overall_offset = float(offset)
    else:
        overall_stretch = 1.0
        overall_offset = float(l_times[0] - s_times[0])

    # Confidence combines mean cosine similarity along the path with a sanity factor on tempo stretch.
    path_costs = cost[wp[:, 0], wp[:, 1]]
    mean_similarity = float(np.clip(1.0 - np.mean(path_costs), 0.0, 1.0))
    if not math.isfinite(overall_stretch) or overall_stretch <= 0.0:
        stretch_factor = 0.0
        overall_stretch = 1.0
    elif 0.5 <= overall_stretch <= 2.0:
        stretch_factor = 1.0
    else:
        stretch_factor = 0.5
    confidence = round(float(np.clip(mean_similarity * stretch_factor, 0.0, 1.0)), 4)

    return {
        "schema_version": SCHEMA_VERSION,
        "studio_duration_seconds": round(studio_dur, 4),
        "live_duration_seconds": round(live_dur, 4),
        "anchors": anchors,
        "overall_offset_seconds": round(overall_offset, 4),
        "overall_stretch": round(overall_stretch, 6),
        "confidence": confidence,
        "tools": {
            "alignment": {
                "method": f"{chroma_method}_dtw",
                "version": package_version("librosa"),
                "hop_length": hop_length,
                "sample_rate": sr,
                "subsequence": use_subseq,
            }
        },
        "manually_verified": False,
        "note": "Automated studio-to-live alignment. Listen to key cues after retiming and adjust before show use.",
    }


def match_recordings(
    studio_audio: Path,
    live_audio: Path,
    out_dir: Path,
    *,
    sync_path: Path | None = None,
    anchor_step: float = 2.0,
    hop_length: int = 1024,
    sr: int = 22050,
    subseq: bool = False,
) -> Path:
    """Align a live or rehearsal recording to a studio track and write tempo_map.json."""
    studio_path = Path(studio_audio)
    live_path = Path(live_audio)
    out_dir = Path(out_dir)

    studio_y, actual_sr = decode_audio(studio_path, sr=sr, mono=True)
    live_y, _ = decode_audio(live_path, sr=actual_sr, mono=True)

    bar_times = None
    candidate_sync = Path(sync_path) if sync_path is not None else (out_dir / "sync.json")
    if candidate_sync.is_file():
        try:
            sync_data = read_json(candidate_sync)
            downbeats = sync_data.get("downbeats")
            if isinstance(downbeats, list) and len(downbeats) >= 2:
                bar_times = downbeats
        except MusicSyncError:
            bar_times = None

    result = align_audio_arrays(
        studio_y,
        live_y,
        sr=actual_sr,
        bar_times=bar_times,
        anchor_step=anchor_step,
        hop_length=hop_length,
        subseq=subseq,
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "studio": {
            "filename": studio_path.name,
            "sha256": file_sha256(studio_path),
            "duration_seconds": result["studio_duration_seconds"],
        },
        "live": {
            "filename": live_path.name,
            "sha256": file_sha256(live_path),
            "duration_seconds": result["live_duration_seconds"],
        },
        "anchors": result["anchors"],
        "overall_offset_seconds": result["overall_offset_seconds"],
        "overall_stretch": result["overall_stretch"],
        "confidence": result["confidence"],
        "tools": result["tools"],
        "manually_verified": False,
        "note": result["note"],
    }
    return write_json(out_dir / "tempo_map.json", payload)
