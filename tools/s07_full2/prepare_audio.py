"""Song 07 v2: analyse the reference recording and conform it to the live length (audio stays outside git).

    python tools/s07_full2/prepare_audio.py /path/to/s07.mp3

Reference: the church's upload youtu.be/7piuHaCYnFM (Drive file 1wL9dyLETDn3q9ECkIXKrDb3UIt_eAgEA),
SHA-256 2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a, 246.55 s, silent from 243.5 s.
Live length 238.0 s (DESIGN-SYSTEM 4). The music part 0 to 243.5 s is conformed evenly to 238.0 s
(ffmpeg atempo, pitch kept); the scene itself is authored on the reference clock and mapped by clock.py.
Writes work/s07v2: audio.wav (mono 22.05 kHz reference, for the analysis), features.npz (reference clock),
music_live.wav (238.0 s, stereo 48 kHz) and review.wav (music_live plus 15 s of silence: 253.0 s).
No em dash or en dash anywhere in this file.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from clock import LIVE, REF_MUSIC, HOLD  # noqa: E402

ROOT = HERE.parents[1]
WORK = ROOT / "work/s07v2"
SHA = "2fea173b63d4086703927a0e6048b5026d0440d151c99c90f3129c37fea6266a"


def run(*cmd, **kw):
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def main():
    src = Path(sys.argv[1])
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != SHA:
        raise SystemExit(f"audio SHA-256 is {got}, expected {SHA}")
    WORK.mkdir(parents=True, exist_ok=True)
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "22050", WORK / "audio.wav")
    tempo = REF_MUSIC / LIVE
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-t", f"{REF_MUSIC:.3f}", "-af",
        f"atempo={tempo:.6f},apad=whole_dur={LIVE:.3f},atrim=0:{LIVE:.3f}", "-ac", "2", "-ar", "48000",
        "-c:a", "pcm_s24le", WORK / "music_live.wav")
    run("ffmpeg", "-v", "error", "-y", "-i", WORK / "music_live.wav", "-af",
        f"apad=whole_dur={LIVE + HOLD:.3f},atrim=0:{LIVE + HOLD:.3f}", "-c:a", "pcm_s24le", WORK / "review.wav")
    snap = ROOT / "work/nine_colours_minor/render1/engine/analyze.py"
    env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / "numba"))
    run(sys.executable, snap, WORK / "audio.wav", WORK / "features.npz", env=env)
    print(f"tempo {tempo:.6f}; ready in {WORK}")


if __name__ == "__main__":
    main()
