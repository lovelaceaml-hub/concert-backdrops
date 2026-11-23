"""Music sync tools for concert backdrops: stem analysis, lyric timing, live alignment, and cue export."""
from __future__ import annotations

from .align import align_audio_arrays, match_recordings, retime, retime_cues, retime_phrases
from .analyze import SCHEMA_VERSION, STEM_NAMES, analyze_audio, validate_sync_data
from .cues import build_cues, export_cues, seconds_to_timecode
from .lyrics import extract_lyrics

__all__ = [
    "SCHEMA_VERSION",
    "STEM_NAMES",
    "align_audio_arrays",
    "analyze_audio",
    "build_cues",
    "export_cues",
    "extract_lyrics",
    "match_recordings",
    "retime",
    "retime_cues",
    "retime_phrases",
    "seconds_to_timecode",
    "validate_sync_data",
]
