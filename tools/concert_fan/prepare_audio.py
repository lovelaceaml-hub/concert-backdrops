"""Prepare the exact twenty-second score from the verified private Song 07 file."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"
SCORE_SHA256 = "b26b7ec1dd00a4c91330df5c83a47afc8c40791861a722dd91408eb246f0cd0b"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "work/song-sources/s07.mp3")
    parser.add_argument("--out", type=Path, default=ROOT / "work/song-sources/fan-trio-score.wav")
    args = parser.parse_args()
    if not args.source.is_file() or sha256(args.source) != SOURCE_SHA256:
        raise SystemExit("Obtain the private Song 07 source recorded in the song catalog; its bytes must match.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(".partial.wav")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "137.5",
        "-i", str(args.source), "-t", "20", "-af",
        "afade=t=in:st=0:d=0.08,afade=t=out:st=19.4:d=0.6,volume=-1dB",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(temporary),
    ], check=True)
    actual = sha256(temporary)
    if actual != SCORE_SHA256:
        raise SystemExit(f"Score differs from the pinned FFmpeg 7.1.5 output: {actual}. Inspect before changing the manifest.")
    temporary.replace(args.out)
    print(f"Prepared {args.out}: {actual}")


if __name__ == "__main__":
    main()
