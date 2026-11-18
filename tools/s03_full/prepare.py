"""Song 03 full backdrop: check the song audio and prepare the render inputs (nothing goes into git).

    python tools/s03_full/prepare.py /path/outside/the/repo/s03.mp3

The audio is the church's YouTube upload, kept on Anthony's private Artifact page as s03.mp3 (never committed).
Makes work/s03_full/features.npz (the engine's music features) and work/s03_full/score.wav (the music, then
silence to the end of the 15 second hold, 48 kHz stereo). Also restores the pinned engine if it is missing.
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s03_full"
SNAPSHOT = ROOT / "work/nine_colours_minor/render1"
SHA256 = "c86a81c76aef1af7ae351b0b02eb2109bba78b43beaa3e8f9b329b4e49f9f485"
TOTAL = 370.1


def main():
    src = Path(sys.argv[1]).resolve()
    if ROOT in src.parents:
        raise SystemExit("Keep the song audio outside the repository.")
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != SHA256:
        raise SystemExit(f"Unexpected audio: sha256 {got}")
    if not (SNAPSHOT / "engine/render.py").exists():
        subprocess.run([sys.executable, str(ROOT / "tools/nine_colours_minor/prepare.py")], check=True)
    WORK.mkdir(parents=True, exist_ok=True)
    if not (WORK / "features.npz").exists():
        wav = WORK / "audio.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", "22050", str(wav)], check=True)
        env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / "numba"))
        subprocess.run([sys.executable, str(SNAPSHOT / "engine/analyze.py"), str(wav), str(WORK / "features.npz")],
                       env=env, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "2", "-ar", "48000",
                    "-af", f"apad=whole_dur={TOTAL}", "-t", f"{TOTAL}", "-c:a", "pcm_s24le", str(WORK / "score.wav")],
                   check=True)
    (WORK / "audio_source.txt").write_text(f"{src}\n{SHA256}\n")
    print("ready:", WORK / "features.npz", WORK / "score.wav")


if __name__ == "__main__":
    main()
