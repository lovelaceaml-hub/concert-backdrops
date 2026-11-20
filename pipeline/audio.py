"""Measured audio features and reviewable onset suggestions, never generated music."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks, stft

from .project import PipelineError, Project, file_hash, safe_path, write_json


def measure(path: Path, *, offset: float = 0, duration: float | None = None) -> dict:
    command = ["ffmpeg", "-v", "error", "-ss", str(offset), "-i", str(path)]
    if duration is not None:
        command += ["-t", str(duration)]
    command += ["-vn", "-ac", "1", "-ar", "22050", "-f", "f32le", "-"]
    result = subprocess.run(command, capture_output=True, timeout=180)
    if result.returncode:
        raise PipelineError("Audio decode failed: " + result.stderr.decode(errors="replace")[-1200:])
    samples = np.frombuffer(result.stdout, "<f4").copy()
    if not len(samples):
        raise PipelineError("Audio source contains no decodable samples.")
    if not np.isfinite(samples).all():
        raise PipelineError("Audio contains nonfinite samples.")
    duration_actual = len(samples) / 22050
    if len(samples) < 2048:
        samples = np.pad(samples, (0, 2048 - len(samples)))
    frequencies, times, spectrum = stft(samples, fs=22050, nperseg=2048, noverlap=1536)
    magnitudes = np.abs(spectrum)
    rms = np.sqrt(np.mean(magnitudes ** 2, axis=0))
    positive_flux = np.maximum(np.diff(magnitudes, axis=1, prepend=magnitudes[:, :1]), 0).mean(axis=0)
    prominence = max(float(np.percentile(positive_flux, 85)) * 0.5, 1e-8)
    peaks, _ = find_peaks(positive_flux, prominence=prominence, distance=max(1, round(0.12 * 22050 / 512)))
    peaks = peaks[times[peaks] < duration_actual]
    onsets = times[peaks]
    tempo = 60 / float(np.median(np.diff(onsets))) if len(onsets) > 2 else 0.0
    features = {"times": times, "rms": rms, "onset": positive_flux, "onsets": onsets, "beat_t": onsets, "dur": duration_actual, "tempo": tempo}
    for name, low, high in (("low", 20, 200), ("mid", 200, 2000), ("high", 2000, 6000), ("air", 6000, 11025)):
        band = magnitudes[(frequencies >= low) & (frequencies < high)]
        features[name] = np.sqrt(np.mean(band ** 2, axis=0))
    features["cent"] = (magnitudes * frequencies[:, None]).sum(axis=0) / np.maximum(magnitudes.sum(axis=0), 1e-10)
    # The compatibility slots are energy summaries, not claimed instrument or stem separation.
    features["rh"], features["rp"] = rms.copy(), positive_flux.copy()
    features["peak_amplitude"] = float(np.max(np.abs(samples)))
    return features


def analyze(project: Project) -> Path:
    source = project.data.get("audio", {}).get("source")
    if not source:
        raise PipelineError("This project is visual-only. Set audio.source to an existing recording before analyzing music.")
    path = safe_path(project.root, source)
    features = measure(path, offset=project.data["audio"].get("offset_seconds", 0), duration=project.seconds)
    # Never silently replace approved hit times in the project manifest or timing file.
    target = project.root / "work/pipeline" / project.id / "audio-analysis.json"
    write_json(target, {
        "schema_version": 1, "source": source, "source_sha256": file_hash(path), "fps": project.fps,
        "duration_seconds": features["dur"], "method": "spectral_flux_onset_suggestions", "manually_verified": False,
        "note": "These are onset suggestions, not instrument-specific beats. Listen and adjust important hits before promoting them to timing.json.",
        "events": [{"seconds": round(float(t), 6), "frame": round(float(t) * project.fps), "kind": "onset", "confirmed": False} for t in features["onsets"]],
        "rms": [{"seconds": round(float(t), 6), "value": round(float(r), 8)} for t, r in zip(features["times"], features["rms"])],
        "peak_amplitude": features["peak_amplitude"],
    })
    return target


def legacy_features(job: dict) -> Path:
    root = Path(job["repo_root"])
    supplied = job["shot"].get("params", {}).get("features")
    if supplied:
        return safe_path(root, supplied)
    directory = Path(job["features_dir"])
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "features.npz"
    source = job.get("audio", {}).get("source")
    if source:
        features = measure(safe_path(root, source))
    else:
        # Silent control data only. No audio file or musical content is created.
        times = np.arange(0, max(360, job["shot"]["end_frame_exclusive"] / job["video"]["fps"] + 1), 512 / 22050)
        flat = 1e-7 * (1 + 0.02 * np.sin(times * 0.31))
        features = {name: flat.copy() for name in ("rms", "low", "mid", "high", "air", "cent", "rh", "rp", "onset")}
        features.update(times=times, onsets=np.array([]), beat_t=np.array([]), dur=times[-1], tempo=0)
    # Avoid zero denominators in the existing song feature normalization, preserving silence.
    count = len(features["times"])
    epsilon = 1e-9 * (1 + np.linspace(0, 0.01, count))
    for name in ("rms", "high", "onset"):
        features[name] = np.maximum(features[name], epsilon)
    np.savez_compressed(output, **features)
    return output
