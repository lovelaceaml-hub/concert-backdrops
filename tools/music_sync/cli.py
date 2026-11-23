"""Command-line interface for python -m tools.music_sync."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .align import match_recordings
from .analyze import analyze_audio
from .cues import export_cues
from .io import MusicSyncError
from .lyrics import ALLOWED_MODELS, extract_lyrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.music_sync",
        description="Music sync tools for concert backdrops (cloud CPU).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser(
        "analyze",
        help="Separate stems (Demucs htdemucs), track beats/downbeats, per-stem hits, and sections into sync.json.",
    )
    p_analyze.add_argument("audio", type=Path, help="Input audio file (mp3, wav, m4a, etc.).")
    p_analyze.add_argument("--out", type=Path, required=True, help="Output directory (keep inside work/).")
    p_analyze.add_argument("--model", default="htdemucs", help="Demucs model name (default: htdemucs).")
    p_analyze.add_argument("--shifts", type=int, default=0, help="Demucs random shifts (default: 0 for fast CPU).")
    p_analyze.add_argument("--reuse-stems", action="store_true", help="Reuse existing WAV stems in <out>/stems if present.")

    p_lyrics = sub.add_parser(
        "lyrics",
        help="Extract word-level sung-lyric timestamps into words.json (Drive only, never git).",
    )
    p_lyrics.add_argument("audio", type=Path, help="Input audio file (uses <out>/stems/vocals.wav automatically if present).")
    p_lyrics.add_argument("--out", type=Path, required=True, help="Output directory (keep inside work/).")
    p_lyrics.add_argument("--language", default="en", help="Language code for faster-whisper (default: en).")
    p_lyrics.add_argument("--model", default="small", choices=ALLOWED_MODELS, help="Whisper model size (default: small).")
    p_lyrics.add_argument("--vocals", type=Path, default=None, help="Explicit path to a separated vocals WAV stem.")
    p_lyrics.add_argument("--vad", action="store_true", help="Enable Silero VAD filter (off by default for singing).")

    p_match = sub.add_parser(
        "match",
        help="Align a rehearsal or live recording to the studio recording and write tempo_map.json.",
    )
    p_match.add_argument("studio_audio", type=Path, help="Studio reference audio file.")
    p_match.add_argument("live_audio", type=Path, help="Rehearsal or live performance audio file.")
    p_match.add_argument("--out", type=Path, required=True, help="Output directory (keep inside work/).")
    p_match.add_argument("--sync", type=Path, default=None, help="Optional sync.json to place anchors on studio downbeats.")
    p_match.add_argument("--anchor-step", type=float, default=2.0, help="Anchor spacing in seconds when downbeats are absent (default: 2.0).")
    p_match.add_argument("--subseq", action="store_true", help="Allow subsequence matching when live audio contains long extra talk or applause.")

    p_cues = sub.add_parser(
        "cues",
        help="Export section starts from sync.json as engine/live.py CUES (cues.py) and 60 fps cues.csv.",
    )
    p_cues.add_argument("sync_json", type=Path, help="Path to sync.json produced by analyze.")
    p_cues.add_argument("--out", type=Path, required=True, help="Output directory.")
    p_cues.add_argument("--tempo-map", type=Path, default=None, help="Optional tempo_map.json to retime cues to a live recording.")
    p_cues.add_argument("--fps", type=int, default=60, help="Timecode frame rate for cues.csv (default: 60).")
    p_cues.add_argument("--loop-sections", action="store_true", help="Set each cue's loop end to the section end instead of None.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            out_path = analyze_audio(
                args.audio,
                args.out,
                demucs_model=args.model,
                demucs_shifts=args.shifts,
                reuse_stems=args.reuse_stems,
            )
            print(f"wrote {out_path}")
            return 0

        if args.command == "lyrics":
            out_path = extract_lyrics(
                args.audio,
                args.out,
                language=args.language,
                model_size=args.model,
                vocals_path=args.vocals,
                vad_filter=args.vad,
            )
            # Never print lyric text to stdout or CI logs.
            print(f"wrote {out_path} (private lyrics timing; upload to Drive only, never commit to git)")
            return 0

        if args.command == "match":
            out_path = match_recordings(
                args.studio_audio,
                args.live_audio,
                args.out,
                sync_path=args.sync,
                anchor_step=args.anchor_step,
                subseq=args.subseq,
            )
            print(f"wrote {out_path}")
            return 0

        if args.command == "cues":
            cues_py, cues_csv = export_cues(
                args.sync_json,
                args.out,
                tempo_map_path=args.tempo_map,
                fps=args.fps,
                loop_sections=args.loop_sections,
            )
            print(f"wrote {cues_py}")
            print(f"wrote {cues_csv}")
            return 0

        parser.error(f"Unknown command: {args.command}")
        return 2
    except (MusicSyncError, ValueError) as exc:
        print(f"music_sync error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
