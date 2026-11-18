"""Song 07: analyse the recording for the render (features under work/s07; the audio itself never goes in git).

    python tools/s07_full/prepare_audio.py /path/to/s07.mp3

Expected input: the church's upload youtu.be/7piuHaCYnFM as shared from the owner's Drive,
SHA-256 2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a, 246.55 s.
No em dash or en dash anywhere in this file.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s07"
SHA = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"


def main():
    src = Path(sys.argv[1])
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != SHA:
        print(f"warning: audio SHA-256 is {got}, expected {SHA}")
    WORK.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", "22050",
                    str(WORK / "audio.wav")], check=True)
    env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / "numba"))
    snap = ROOT / "work/nine_colours_minor/render1/engine/analyze.py"
    subprocess.run([sys.executable, str(snap), str(WORK / "audio.wav"), str(WORK / "features.npz")], env=env,
                   check=True)
    print("features ready:", WORK / "features.npz")


if __name__ == "__main__":
    main()
