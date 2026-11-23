"""Word-level sung-lyric timing with faster-whisper (CPU, int8).

Lyrics are copyrighted: words.json must never be committed to git or uploaded as a
public/workflow artifact. Save words.json only to the private Google Drive folder.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .io import MusicSyncError, file_sha256, package_version, write_json

SCHEMA_VERSION = 1
ALLOWED_MODELS = ("tiny", "base", "small", "medium", "large-v3")


def extract_lyrics(
    audio_path: Path,
    out_dir: Path,
    *,
    language: str = "en",
    model_size: str = "small",
    vocals_path: Path | None = None,
    vad_filter: bool = False,
    transcriber: Callable[[Path, str, str], tuple[list[dict[str, Any]], dict[str, Any]]] | None = None,
) -> Path:
    """Extract word-level timestamps into <out_dir>/words.json.

    Uses the Demucs vocals stem (<out_dir>/stems/vocals.wav or --vocals) when present,
    falling back to the original audio mix when no vocals stem exists.
    """
    audio_path = Path(audio_path)
    out_dir = Path(out_dir)
    if not audio_path.is_file():
        raise MusicSyncError(f"Audio file not found: {audio_path}")
    if model_size not in ALLOWED_MODELS:
        raise MusicSyncError(f"Unsupported whisper model {model_size!r}; choose from {', '.join(ALLOWED_MODELS)}.")

    target_audio = audio_path
    audio_used = "mix"
    if vocals_path is not None:
        vp = Path(vocals_path)
        if not vp.is_file():
            raise MusicSyncError(f"Specified vocals stem not found: {vp}")
        target_audio = vp
        audio_used = "vocals_stem"
    else:
        auto_vocals = out_dir / "stems" / "vocals.wav"
        if auto_vocals.is_file():
            target_audio = auto_vocals
            audio_used = "vocals_stem"

    if transcriber is not None:
        words, meta = transcriber(target_audio, language, model_size)
        detected_language = str(meta.get("detected_language", language))
        lang_prob = float(meta.get("language_probability", 1.0))
        tool_meta = dict(meta.get("tool", {"method": "faster_whisper", "model": model_size, "version": "mock"}))
    else:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise MusicSyncError(
                "faster-whisper is not installed. Install cloud dependencies from tools/music_sync/requirements.txt."
            ) from exc

        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        # Decode with the project's ffmpeg loader (16 kHz mono, as Whisper expects) so the
        # PyAV version faster-whisper would otherwise use never matters.
        from .io import decode_audio
        samples, _ = decode_audio(target_audio, sr=16000, mono=True)
        segments, info = model.transcribe(
            samples,
            language=language or None,
            word_timestamps=True,
            vad_filter=vad_filter,
        )
        words = []
        for segment in segments:
            for item in segment.words or []:
                text = (item.word or "").strip()
                if not text:
                    continue
                start = max(0.0, float(item.start))
                end = max(start, float(item.end))
                prob = min(max(float(getattr(item, "probability", 0.0)), 0.0), 1.0)
                words.append(
                    {
                        "word": text,
                        "start": round(start, 4),
                        "end": round(end, 4),
                        "confidence": round(prob, 4),
                    }
                )
        detected_language = str(getattr(info, "language", language) or language)
        lang_prob = round(float(getattr(info, "language_probability", 0.0)), 4)
        tool_meta = {
            "method": "faster_whisper",
            "model": model_size,
            "compute_type": "int8",
            "device": "cpu",
            "vad_filter": vad_filter,
            "version": package_version("faster-whisper"),
        }

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "filename": audio_path.name,
            "sha256": file_sha256(audio_path),
            "audio_used": audio_used,
        },
        "language": language,
        "detected_language": detected_language,
        "language_probability": lang_prob,
        "word_count": len(words),
        "words": words,
        "tools": {
            "transcription": tool_meta,
        },
        "manually_verified": False,
        "copyright_notice": "Private lyric timing only. Never commit words.json to git; store only in Google Drive.",
    }
    return write_json(out_dir / "words.json", payload)
