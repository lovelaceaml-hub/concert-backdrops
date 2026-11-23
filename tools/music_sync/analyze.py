"""Stem separation, beat/downbeat tracking, per-stem onsets/energy, and section segmentation."""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .io import MusicSyncError, decode_audio, file_sha256, package_version, write_json, write_wav

SCHEMA_VERSION = 1
STEM_NAMES = ("vocals", "drums", "bass", "other")
ANALYSIS_SR = 22050
HOP_LENGTH = 512


def _clean_sorted_times(values: Any, duration: float) -> list[float]:
    arr = np.asarray(values, dtype=np.float64).ravel()
    arr = arr[np.isfinite(arr)]
    arr = arr[(arr >= 0.0) & (arr <= duration + 1e-3)]
    if arr.size == 0:
        return []
    arr = np.sort(arr)
    dedup = [round(float(arr[0]), 4)]
    for v in arr[1:]:
        rv = round(float(v), 4)
        if rv > dedup[-1] + 1e-4:
            dedup.append(rv)
    return dedup


def compute_tempo_curve(beats: list[float], *, window: int = 3) -> tuple[list[dict[str, float]], float]:
    """Compute a median-smoothed tempo curve (time, bpm) and summary tempo from beat times."""
    if len(beats) < 2:
        return [], 0.0
    b = np.asarray(beats, dtype=np.float64)
    dt = np.diff(b)
    valid = (dt > 0.15) & (dt < 3.0)
    if not np.any(valid):
        return [], 0.0
    mids = 0.5 * (b[:-1] + b[1:])
    mids = mids[valid]
    raw_bpm = 60.0 / dt[valid]

    half = max(0, window // 2)
    smoothed = np.empty_like(raw_bpm)
    for i in range(raw_bpm.size):
        lo = max(0, i - half)
        hi = min(raw_bpm.size, i + half + 1)
        smoothed[i] = float(np.median(raw_bpm[lo:hi]))

    tempo_bpm = round(float(np.median(smoothed)), 2)
    curve = [{"time": round(float(t), 4), "bpm": round(float(bpm), 2)} for t, bpm in zip(mids, smoothed)]
    return curve, tempo_bpm


def separate_stems(
    audio_path: Path,
    stems_dir: Path,
    *,
    model_name: str = "htdemucs",
    shifts: int = 0,
    reuse: bool = False,
) -> tuple[dict[str, Path], dict[str, Any]]:
    """Separate audio into vocals, drums, bass, and other stems using Demucs on CPU."""
    stems_dir = Path(stems_dir)
    expected = {name: stems_dir / f"{name}.wav" for name in STEM_NAMES}
    if reuse and all(p.is_file() for p in expected.values()):
        return expected, {
            "method": f"demucs.{model_name}",
            "version": package_version("demucs"),
            "device": "cpu",
            "reused_existing": True,
        }

    try:
        import torch
        from demucs.apply import apply_model
        from demucs.pretrained import get_model
    except ImportError as exc:
        raise MusicSyncError(
            "Demucs is not installed. Install cloud dependencies from tools/music_sync/requirements.txt."
        ) from exc

    model = get_model(model_name)
    model.to("cpu")
    model.eval()

    model_sr = int(getattr(model, "samplerate", 44100))
    wav_stereo, _ = decode_audio(audio_path, sr=model_sr, mono=False)
    wav_tensor = torch.from_numpy(wav_stereo).unsqueeze(0).to("cpu")

    with torch.no_grad():
        sources = apply_model(
            model,
            wav_tensor,
            device="cpu",
            shifts=shifts,
            split=True,
            overlap=0.25,
            progress=False,
        )[0]

    stems_dir.mkdir(parents=True, exist_ok=True)
    stem_paths: dict[str, Path] = {}
    for source_name, tensor in zip(model.sources, sources):
        if source_name in STEM_NAMES:
            out_path = stems_dir / f"{source_name}.wav"
            write_wav(out_path, tensor.detach().cpu().numpy(), model_sr)
            stem_paths[source_name] = out_path

    missing = [name for name in STEM_NAMES if name not in stem_paths]
    if missing:
        raise MusicSyncError(f"Demucs model {model_name!r} did not produce expected stems: {missing}")

    meta = {
        "method": f"demucs.{model_name}",
        "version": package_version("demucs"),
        "torch_version": package_version("torch"),
        "device": "cpu",
        "shifts": shifts,
        "sample_rate": model_sr,
    }
    return stem_paths, meta


def _estimate_downbeats_from_beats(
    beats: list[float],
    y_mono: np.ndarray,
    sr: int,
    stems_mono: dict[str, np.ndarray] | None = None,
) -> list[float]:
    """Estimate downbeats on a 4/4 bar phase using drums+bass energy when available."""
    if not beats:
        return []
    if len(beats) < 4:
        return [beats[0]]

    ref = y_mono
    if stems_mono:
        parts = [stems_mono[k] for k in ("drums", "bass") if k in stems_mono and stems_mono[k].size > 0]
        if parts:
            min_len = min(p.size for p in parts)
            ref = np.sum([p[:min_len] for p in parts], axis=0)

    win = max(1, int(round(0.08 * sr)))
    scores = np.zeros(len(beats), dtype=np.float64)
    for idx, bt in enumerate(beats):
        center = int(round(bt * sr))
        lo = max(0, center - win // 2)
        hi = min(ref.size, center + win)
        if hi > lo:
            seg = ref[lo:hi]
            scores[idx] = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2)))

    phase_means = [float(scores[p::4].mean()) if scores[p::4].size else -1.0 for p in range(4)]
    best_phase = int(np.argmax(phase_means))
    return beats[best_phase::4]


def track_beats(
    y_mono: np.ndarray,
    sr: int = ANALYSIS_SR,
    *,
    stems_mono: dict[str, np.ndarray] | None = None,
    tracker: Callable[[np.ndarray, int], tuple[list[float], list[float], dict[str, Any]]] | None = None,
) -> tuple[list[float], list[float], dict[str, Any]]:
    """Track beats and downbeats, preferring beat_this on CPU and falling back to librosa."""
    duration = float(len(y_mono) / sr)
    if tracker is not None:
        raw_beats, raw_downbeats, meta = tracker(y_mono, sr)
        return _clean_sorted_times(raw_beats, duration), _clean_sorted_times(raw_downbeats, duration), meta

    fallback_reason = ""
    try:
        from beat_this.inference import Audio2Beats

        model = Audio2Beats(checkpoint_path="final0", device="cpu", dbn=False)
        raw_beats, raw_downbeats = model(np.asarray(y_mono, dtype=np.float32), sr)
        beats = _clean_sorted_times(raw_beats, duration)
        downbeats = _clean_sorted_times(raw_downbeats, duration)
        meta = {
            "method": "beat_this.final0",
            "version": package_version("beat-this"),
            "device": "cpu",
            "fallback_used": False,
        }
        return beats, downbeats, meta
    except Exception as exc:
        fallback_reason = f"{type(exc).__name__}: {exc}"

    try:
        import librosa

        _, beat_times = librosa.beat.beat_track(y=np.asarray(y_mono, dtype=np.float32), sr=sr, units="time")
        beats = _clean_sorted_times(beat_times, duration)
        downbeats = _estimate_downbeats_from_beats(beats, y_mono, sr, stems_mono=stems_mono)
        meta = {
            "method": "librosa.beat.beat_track",
            "downbeat_method": "bar_phase_4_4_heuristic",
            "version": package_version("librosa"),
            "device": "cpu",
            "fallback_used": True,
            "fallback_reason": fallback_reason,
        }
        return beats, downbeats, meta
    except ImportError as exc:
        raise MusicSyncError(
            f"Neither beat_this ({fallback_reason}) nor librosa is available for beat tracking."
        ) from exc


def analyze_stem(
    y_mono: np.ndarray,
    sr: int = ANALYSIS_SR,
    *,
    energy_hop_seconds: float = 0.1,
    min_spacing_seconds: float = 0.06,
    strength_threshold: float = 0.08,
) -> tuple[list[dict[str, float]], dict[str, Any], dict[str, str]]:
    """Extract onset hits (time, strength) and RMS energy curve for a single stem."""
    y = np.asarray(y_mono, dtype=np.float32).ravel()
    duration = float(y.size / sr) if sr > 0 else 0.0

    # Compact RMS energy curve at energy_hop_seconds spacing.
    hop_samples = max(1, int(round(sr * energy_hop_seconds)))
    if y.size == 0:
        rms_frames = np.zeros(1, dtype=np.float64)
    else:
        n_frames = max(1, int(math.ceil(y.size / hop_samples)))
        rms_frames = np.empty(n_frames, dtype=np.float64)
        for i in range(n_frames):
            seg = y[i * hop_samples : (i + 1) * hop_samples]
            rms_frames[i] = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) if seg.size else 0.0

    rms_peak = float(np.max(rms_frames)) if rms_frames.size else 0.0
    rms_mean = float(np.mean(rms_frames)) if rms_frames.size else 0.0
    if rms_peak > 1e-8:
        norm_curve = [round(float(v / rms_peak), 4) for v in rms_frames]
    else:
        norm_curve = [0.0 for _ in rms_frames]

    energy = {
        "rms_mean": round(rms_mean, 6),
        "rms_peak": round(rms_peak, 6),
        "curve": norm_curve,
    }

    # Silent stems produce zero hits.
    if y.size < HOP_LENGTH or float(np.max(np.abs(y))) < 1e-4:
        return [], energy, {"method": "librosa.onset", "version": package_version("librosa")}

    try:
        import librosa

        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP_LENGTH)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=HOP_LENGTH,
            backtrack=False,
            units="frames",
        )
        frame_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)
        tool_info = {"method": "librosa.onset", "version": package_version("librosa")}
    except ImportError:
        from scipy.signal import find_peaks, stft

        _, times, spec = stft(y, fs=sr, nperseg=2048, noverlap=2048 - HOP_LENGTH)
        mag = np.abs(spec)
        onset_env = np.maximum(np.diff(np.log1p(100.0 * mag), axis=1, prepend=np.log1p(100.0 * mag[:, :1])), 0.0).mean(axis=0)
        prom = max(float(np.percentile(onset_env, 85)) * 0.35, 1e-8)
        dist = max(1, int(round(min_spacing_seconds * sr / HOP_LENGTH)))
        onset_frames, _ = find_peaks(onset_env, prominence=prom, distance=dist)
        frame_times = times[onset_frames]
        tool_info = {"method": "scipy.signal.stft_flux", "version": package_version("scipy")}

    if onset_env.size == 0 or len(onset_frames) == 0:
        return [], energy, tool_info

    scale = max(float(np.percentile(onset_env, 99)), 1e-8)
    raw_hits: list[tuple[float, float]] = []
    for frame_idx, t_sec in zip(onset_frames, frame_times):
        t_val = float(t_sec)
        if not (0.0 <= t_val <= duration):
            continue
        strength = float(np.clip(onset_env[int(frame_idx)] / scale, 0.0, 1.0))
        if strength >= strength_threshold:
            raw_hits.append((t_val, strength))

    # Enforce minimum spacing, keeping the stronger hit when two peaks are too close.
    dedup_hits: list[tuple[float, float]] = []
    for t_val, strength in raw_hits:
        if dedup_hits and (t_val - dedup_hits[-1][0]) < min_spacing_seconds:
            if strength > dedup_hits[-1][1]:
                dedup_hits[-1] = (t_val, strength)
        else:
            dedup_hits.append((t_val, strength))

    hits = [{"time": round(t, 4), "strength": round(s, 4)} for t, s in dedup_hits]
    return hits, energy, tool_info


def _gaussian_smooth_1d(x: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0.25 or x.size < 3:
        return x.astype(np.float64, copy=True)
    radius = max(1, int(round(sigma * 4)))
    grid = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (grid / sigma) ** 2)
    kernel /= kernel.sum()
    return np.convolve(np.pad(x, radius, mode="edge"), kernel, mode="valid")


def segment_sections(
    y_mono: np.ndarray,
    sr: int = ANALYSIS_SR,
    *,
    beats: list[float] | None = None,
    downbeats: list[float] | None = None,
    min_section_seconds: float = 12.0,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Detect structural section boundaries from chroma + MFCC self-similarity."""
    y = np.asarray(y_mono, dtype=np.float32).ravel()
    duration = float(y.size / sr) if sr > 0 else 0.0
    if duration <= 0.0:
        return [{"name": "Section 1", "start": 0.0, "end": 0.0, "energy": 0.0}], {
            "method": "librosa.chroma_mfcc_self_similarity",
            "version": package_version("librosa"),
        }

    step_sec = 0.5
    effective_min_len = min(min_section_seconds, max(2.0, duration / 4.0))

    try:
        import librosa

        if duration >= 2.0:
            try:
                chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP_LENGTH)
            except Exception:
                chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=HOP_LENGTH)
        else:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=HOP_LENGTH)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=HOP_LENGTH)
        rms = librosa.feature.rms(y=y, hop_length=HOP_LENGTH)[0]
        feat_frames = np.vstack([chroma, mfcc]).T  # (n_frames, 25)
        tool_info = {"method": "librosa.chroma_mfcc_self_similarity", "version": package_version("librosa")}
    except ImportError:
        from scipy.signal import stft

        freqs, _, spec = stft(y, fs=sr, nperseg=2048, noverlap=2048 - HOP_LENGTH)
        mag = np.abs(spec)
        rms = np.sqrt(np.mean(mag**2, axis=0))
        edges = np.geomspace(60.0, min(8000.0, sr / 2.0 - 1.0), 17)
        bidx = np.digitize(freqs, edges) - 1
        bands = np.zeros((mag.shape[1], 16), dtype=np.float64)
        for b in range(16):
            mask = bidx == b
            if np.any(mask):
                bands[:, b] = np.log1p(100.0 * mag[mask, :].mean(axis=0))
        feat_frames = bands
        tool_info = {"method": "scipy.stft_self_similarity", "version": package_version("scipy")}

    frames_per_sec = sr / float(HOP_LENGTH)
    win_frames = max(1, int(round(frames_per_sec * step_sec)))
    nw = feat_frames.shape[0] // win_frames

    boundary_times: list[float] = [0.0]
    if nw >= 8 and float(np.max(np.abs(y))) >= 1e-4:
        pooled = feat_frames[: nw * win_frames].reshape(nw, win_frames, -1).mean(axis=1)
        pooled = (pooled - pooled.mean(axis=0)) / (pooled.std(axis=0) + 1e-8)
        if pooled.shape[1] >= 25:
            # Give harmonic chroma slightly stronger weight alongside timbre MFCCs.
            pooled[:, :12] *= 1.3
        pooled /= np.linalg.norm(pooled, axis=1, keepdims=True) + 1e-8

        sim = pooled @ pooled.T
        kernel_sec = min(8.0, max(2.0, duration / 4.0))
        half_k = max(2, min(int(round(kernel_sec / step_sec)), nw // 3))
        coords = np.arange(-half_k, half_k, dtype=np.float64) + 0.5
        gauss = np.exp(-0.5 * (coords / (0.5 * half_k)) ** 2)
        sign = np.sign(coords)
        kernel = np.outer(gauss, gauss) * np.outer(sign, sign)

        padded = np.pad(sim, half_k, mode="edge")
        novelty = np.array(
            [float((kernel * padded[i : i + 2 * half_k, i : i + 2 * half_k]).sum()) for i in range(nw)],
            dtype=np.float64,
        )
        novelty = np.maximum(novelty, 0.0)
        if novelty.max() > 0.0:
            novelty /= novelty.max()
        novelty = _gaussian_smooth_1d(novelty, sigma=1.0)

        min_dist_w = max(1, int(round(effective_min_len / step_sec)))
        margin_w = max(1, int(round(min(4.0, duration * 0.15) / step_sec)))
        threshold = float(novelty.mean() + 0.5 * novelty.std())

        peaks: list[int] = []
        for i in range(margin_w, nw - margin_w):
            lo = max(0, i - min_dist_w // 2)
            hi = min(nw, i + min_dist_w // 2 + 1)
            if novelty[i] >= novelty[lo:hi].max() and novelty[i] > threshold:
                peaks.append(i)

        kept: list[int] = []
        for idx in sorted(peaks, key=lambda k: -novelty[k]):
            if all(abs(idx - other) * step_sec >= effective_min_len for other in kept):
                kept.append(idx)

        down_arr = np.asarray(downbeats or [], dtype=np.float64)
        beat_arr = np.asarray(beats or [], dtype=np.float64)
        for idx in sorted(kept):
            raw_t = (idx + 0.5) * step_sec
            snapped = raw_t
            if down_arr.size:
                close_d = down_arr[np.abs(down_arr - raw_t) <= 1.5]
                if close_d.size:
                    snapped = float(close_d[np.argmin(np.abs(close_d - raw_t))])
            if snapped == raw_t and beat_arr.size:
                close_b = beat_arr[np.abs(beat_arr - raw_t) <= 0.75]
                if close_b.size:
                    snapped = float(close_b[np.argmin(np.abs(close_b - raw_t))])
            if 0.5 < snapped < duration - 0.5:
                boundary_times.append(snapped)

    # Deduplicate and keep strictly increasing boundaries.
    starts: list[float] = [0.0]
    for bt in sorted(boundary_times[1:]):
        rbt = round(float(bt), 4)
        if rbt - starts[-1] >= max(1.0, effective_min_len * 0.5) and duration - rbt >= 0.5:
            starts.append(rbt)

    rms_peak = float(np.max(rms)) if rms.size else 0.0
    rms_times = np.arange(rms.size, dtype=np.float64) / frames_per_sec

    sections: list[dict[str, Any]] = []
    end_total = round(duration, 4)
    for idx, start_t in enumerate(starts):
        end_t = starts[idx + 1] if idx + 1 < len(starts) else end_total
        if end_t <= start_t:
            continue
        mask = (rms_times >= start_t) & (rms_times < end_t)
        if np.any(mask) and rms_peak > 1e-8:
            energy = float(np.mean(rms[mask]) / rms_peak)
        else:
            energy = 0.0
        sections.append(
            {
                "name": f"Section {len(sections) + 1}",
                "start": round(float(start_t), 4),
                "end": round(float(end_t), 4),
                "energy": round(float(np.clip(energy, 0.0, 1.0)), 4),
            }
        )

    if not sections:
        sections.append({"name": "Section 1", "start": 0.0, "end": end_total, "energy": 0.0})
    return sections, tool_info


def validate_sync_data(data: dict[str, Any]) -> None:
    """Validate the sync.json schema; raise ValueError on any structural problem."""
    if not isinstance(data, dict):
        raise ValueError("sync.json root must be an object.")
    if type(data.get("schema_version")) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}.")

    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("source must be an object.")
    if not isinstance(source.get("filename"), str) or not source["filename"]:
        raise ValueError("source.filename must be a non-empty string.")
    sha = source.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("source.sha256 must be a 64-character lowercase hex digest.")

    duration = data.get("duration_seconds")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration_seconds must be a finite positive number.")

    tempo_bpm = data.get("tempo_bpm")
    if isinstance(tempo_bpm, bool) or not isinstance(tempo_bpm, (int, float)) or not math.isfinite(tempo_bpm) or tempo_bpm < 0:
        raise ValueError("tempo_bpm must be a finite non-negative number.")

    tempo_curve = data.get("tempo_curve")
    if not isinstance(tempo_curve, list):
        raise ValueError("tempo_curve must be a list.")
    prev_t = -1.0
    for idx, pt in enumerate(tempo_curve):
        if not isinstance(pt, dict):
            raise ValueError(f"tempo_curve[{idx}] must be an object.")
        pt_t, pt_b = pt.get("time"), pt.get("bpm")
        if (
            isinstance(pt_t, bool)
            or isinstance(pt_b, bool)
            or not isinstance(pt_t, (int, float))
            or not isinstance(pt_b, (int, float))
            or not (math.isfinite(pt_t) and math.isfinite(pt_b))
            or pt_t < prev_t
            or pt_b <= 0
        ):
            raise ValueError(f"tempo_curve[{idx}] must have non-decreasing time and positive bpm.")
        prev_t = float(pt_t)

    for key in ("beats", "downbeats"):
        vals = data.get(key)
        if not isinstance(vals, list):
            raise ValueError(f"{key} must be a list.")
        prev = -1.0
        for idx, v in enumerate(vals):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < prev or v > duration + 0.1:
                raise ValueError(f"{key}[{idx}] must be a non-decreasing timestamp within [0, duration_seconds].")
            prev = float(v)

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections must be a non-empty list.")
    prev_end: float | None = None
    for idx, sec in enumerate(sections):
        if not isinstance(sec, dict):
            raise ValueError(f"sections[{idx}] must be an object.")
        if not isinstance(sec.get("name"), str) or not sec["name"]:
            raise ValueError(f"sections[{idx}].name must be a non-empty string.")
        s0, s1 = sec.get("start"), sec.get("end")
        if (
            isinstance(s0, bool)
            or isinstance(s1, bool)
            or not isinstance(s0, (int, float))
            or not isinstance(s1, (int, float))
            or not (math.isfinite(s0) and math.isfinite(s1))
            or s0 < 0
            or s1 <= s0
        ):
            raise ValueError(f"sections[{idx}] must have finite 0 <= start < end.")
        if prev_end is not None and abs(s0 - prev_end) > 1e-3:
            raise ValueError(f"sections[{idx}] must be contiguous with the previous section.")
        prev_end = float(s1)

    stem_hits = data.get("stem_hits")
    if not isinstance(stem_hits, dict):
        raise ValueError("stem_hits must be an object.")
    for stem in STEM_NAMES:
        hits = stem_hits.get(stem)
        if not isinstance(hits, list):
            raise ValueError(f"stem_hits.{stem} must be a list.")
        for idx, hit in enumerate(hits):
            if not isinstance(hit, dict):
                raise ValueError(f"stem_hits.{stem}[{idx}] must be an object.")
            ht, hs = hit.get("time"), hit.get("strength")
            if (
                isinstance(ht, bool)
                or isinstance(hs, bool)
                or not isinstance(ht, (int, float))
                or not isinstance(hs, (int, float))
                or not (math.isfinite(ht) and math.isfinite(hs))
                or ht < 0
                or not (0.0 <= hs <= 1.0)
            ):
                raise ValueError(f"stem_hits.{stem}[{idx}] must have non-negative time and strength in [0, 1].")

    tools = data.get("tools")
    if not isinstance(tools, dict):
        raise ValueError("tools must be an object.")
    for tool_key in ("stem_separation", "beat_tracking", "stem_onsets", "sections"):
        entry = tools.get(tool_key)
        if not isinstance(entry, dict) or not isinstance(entry.get("method"), str) or not isinstance(entry.get("version"), str):
            raise ValueError(f"tools.{tool_key} must record method and version strings.")

    if type(data.get("manually_verified")) is not bool:
        raise ValueError("manually_verified must be a boolean.")


def analyze_audio(
    audio_path: Path,
    out_dir: Path,
    *,
    demucs_model: str = "htdemucs",
    demucs_shifts: int = 0,
    reuse_stems: bool = False,
    separator: Callable[[Path, Path], tuple[dict[str, Path], dict[str, Any]]] | None = None,
    beat_tracker: Callable[[np.ndarray, int], tuple[list[float], list[float], dict[str, Any]]] | None = None,
) -> Path:
    """Run full musical analysis (stems, beats/downbeats, per-stem hits/energy, sections) and write sync.json."""
    audio_path = Path(audio_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stems_dir = out_dir / "stems"

    # 1. Separate stems with Demucs (CPU), or use an injected separator in unit tests.
    if separator is not None:
        stem_paths, stem_meta = separator(audio_path, stems_dir)
    else:
        stem_paths, stem_meta = separate_stems(
            audio_path,
            stems_dir,
            model_name=demucs_model,
            shifts=demucs_shifts,
            reuse=reuse_stems,
        )

    # 2. Decode mix and separated stems to mono 22050 Hz for musical feature extraction.
    y_mix, sr = decode_audio(audio_path, sr=ANALYSIS_SR, mono=True)
    duration = float(y_mix.size / sr)

    stems_mono: dict[str, np.ndarray] = {}
    for name in STEM_NAMES:
        stems_mono[name], _ = decode_audio(stem_paths[name], sr=ANALYSIS_SR, mono=True)

    # 3. Beat and downbeat tracking (beat_this preferred; librosa fallback recorded).
    beats, downbeats, beat_meta = track_beats(y_mix, sr, stems_mono=stems_mono, tracker=beat_tracker)
    tempo_curve, tempo_bpm = compute_tempo_curve(beats)

    # 4. Per-stem onsets and energy curves.
    energy_hop = 0.1
    stem_hits: dict[str, list[dict[str, float]]] = {}
    stem_energy_map: dict[str, dict[str, Any]] = {}
    onset_tool_meta: dict[str, str] = {"method": "librosa.onset", "version": package_version("librosa")}
    for name in STEM_NAMES:
        hits, energy, onset_tool_meta = analyze_stem(stems_mono[name], sr, energy_hop_seconds=energy_hop)
        stem_hits[name] = hits
        stem_energy_map[name] = energy

    # 5. Structural section boundaries from chroma + MFCC self-similarity.
    sections, section_tool_meta = segment_sections(y_mix, sr, beats=beats, downbeats=downbeats)

    sync_data: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "filename": audio_path.name,
            "sha256": file_sha256(audio_path),
            "sample_rate": sr,
        },
        "duration_seconds": round(duration, 4),
        "tempo_bpm": tempo_bpm,
        "tempo_curve": tempo_curve,
        "beats": beats,
        "downbeats": downbeats,
        "sections": sections,
        "stem_hits": stem_hits,
        "stem_energy": {
            "frame_hop_seconds": energy_hop,
            "stems": stem_energy_map,
        },
        "tools": {
            "stem_separation": stem_meta,
            "beat_tracking": beat_meta,
            "stem_onsets": onset_tool_meta,
            "sections": section_tool_meta,
        },
        "manually_verified": False,
        "note": "Automated music sync suggestions. Listen and verify beats, downbeats, hits, and sections before locking final timing.",
    }
    validate_sync_data(sync_data)
    return write_json(out_dir / "sync.json", sync_data)
