"""Audio decoding, hashing, and atomic JSON helpers for tools.music_sync."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np


class MusicSyncError(RuntimeError):
    """Actionable error raised by music sync commands."""


def file_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> Path:
    """Write a JSON document atomically and reject NaN/Infinity values."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return path


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MusicSyncError(f"Cannot read JSON from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise MusicSyncError(f"Expected a JSON object in {path}.")
    return data


def package_version(dist_name: str) -> str:
    """Return an installed distribution version, or 'not_installed'."""
    try:
        return importlib.metadata.version(dist_name)
    except importlib.metadata.PackageNotFoundError:
        return "not_installed"


def _read_wav_stdlib(path: Path) -> tuple[np.ndarray, int]:
    """Read a PCM WAV file using only the standard library (returns channels x samples float32)."""
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    if sampwidth == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sampwidth == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sampwidth == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise MusicSyncError(f"Unsupported WAV sample width ({sampwidth} bytes) in {path}.")
    if channels > 1:
        data = data.reshape(-1, channels).T
    else:
        data = data.reshape(1, -1)
    return data, sr


def _resample_channels(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample (channels, samples) float32 audio when sample rates differ."""
    if orig_sr == target_sr or data.shape[1] == 0:
        return data.astype(np.float32, copy=False)
    from math import gcd
    from scipy.signal import resample_poly

    g = gcd(orig_sr, target_sr)
    up = target_sr // g
    down = orig_sr // g
    out = [resample_poly(ch, up, down).astype(np.float32) for ch in data]
    return np.stack(out, axis=0)


def decode_audio(path: Path, *, sr: int = 22050, mono: bool = True) -> tuple[np.ndarray, int]:
    """Decode any audio file to float32 samples at the requested sample rate.

    Returns a 1D array of shape (samples,) when mono=True, or a 2D array of shape
    (2, samples) when mono=False. Uses ffmpeg when available, with a direct soundfile/wave
    path for WAV inputs so local checks work even without ffmpeg.
    """
    path = Path(path)
    if not path.is_file():
        raise MusicSyncError(f"Audio file not found: {path}")

    channels = 1 if mono else 2
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-nostdin",
        "-i",
        str(path),
        "-vn",
        "-ac",
        str(channels),
        "-ar",
        str(sr),
        "-f",
        "f32le",
        "-",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
    except FileNotFoundError:
        result = None

    if result is not None and result.returncode == 0:
        raw = np.frombuffer(result.stdout, dtype="<f4").copy()
        if raw.size == 0:
            raise MusicSyncError(f"Audio file contains no decodable samples: {path}")
        if not np.isfinite(raw).all():
            raise MusicSyncError(f"Audio contains non-finite samples: {path}")
        if mono:
            return raw, sr
        frames = raw.size // channels
        return raw[: frames * channels].reshape(frames, channels).T.copy(), sr

    # Fallback for WAV files when ffmpeg is unavailable.
    if path.suffix.lower() == ".wav":
        try:
            import soundfile as sf

            audio, orig_sr = sf.read(str(path), dtype="float32", always_2d=True)
            data = audio.T
        except Exception:
            data, orig_sr = _read_wav_stdlib(path)
        if data.shape[1] == 0:
            raise MusicSyncError(f"Audio file contains no decodable samples: {path}")
        if mono:
            data = data.mean(axis=0, keepdims=True)
        elif data.shape[0] == 1:
            data = np.repeat(data, 2, axis=0)
        elif data.shape[0] > 2:
            data = data[:2, :]
        data = _resample_channels(data, orig_sr, sr)
        if not np.isfinite(data).all():
            raise MusicSyncError(f"Audio contains non-finite samples: {path}")
        return (data[0].copy() if mono else data.copy()), sr

    stderr = result.stderr.decode(errors="replace")[-1200:] if result is not None else "ffmpeg not found on PATH"
    raise MusicSyncError(f"Audio decode failed for {path}: {stderr}")


def write_wav(path: Path, data: np.ndarray, sr: int) -> Path:
    """Write float32 audio (samples,) or (channels, samples) to a 16-bit PCM WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.asarray(data, dtype=np.float32)
    arr = np.clip(arr, -1.0, 1.0)
    try:
        import soundfile as sf

        to_write = arr.T if arr.ndim == 2 else arr
        sf.write(str(path), to_write, sr, subtype="PCM_16")
        return path
    except ImportError:
        pass

    if arr.ndim == 1:
        channels = 1
        interleaved = arr
    elif arr.ndim == 2:
        channels = arr.shape[0]
        interleaved = arr.T.reshape(-1)
    else:
        raise MusicSyncError(f"Unsupported audio array shape for WAV export: {arr.shape}")
    pcm = np.round(interleaved * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(int(sr))
        wf.writeframes(pcm.tobytes())
    return path
