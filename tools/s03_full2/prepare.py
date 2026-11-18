"""Song 03 backdrop v2: check the reference audio, conform it to the 5:13 live length, make the render inputs.

    python tools/s03_full2/prepare.py /path/outside/the/repo/s03.mp3

Nothing made here goes into git (work/ is ignored). The reference is the church's upload youtu.be/TH_p9g7Eu30
(355.09 s), kept as s03.mp3 on Anthony's private Artifact page.

Conforming (estimate until a rehearsal recording exists, see TIMELINE.md): the reference holds one repeated
passage in chorus 2. Its music at 4:32.74 and at 5:14.79 is the same (chroma and timbre match, both on the
beat grid of 0.3755 s; 112 beats apart). The live arrangement is taken to sing that passage once, so the
42.05 s between the two points are cut with a 40 ms crossfade on the beat. Result: 313.04 s, within 0.04 s of
the live length, so nothing is sped up or slowed down. The last 0.04 s of the tail silence is trimmed to give
exactly 313.000 s.

Makes in work/s03_full2/:
  live.wav       the conformed music, 313.000 s, 48 kHz stereo (for the review and phone copies)
  score.wav      live.wav then 15 s of silence: 328.000 s (the stage video's length)
  features.npz   the engine's music features of score.wav (engine/analyze.py of the pinned engine)
No em dash or en dash anywhere in this file.
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s03_full2"
SNAPSHOT = ROOT / "work/nine_colours_minor/render1"
SHA256 = "c86a81c76aef1af7ae351b0b02eb2109bba78b43beaa3e8f9b329b4e49f9f485"
CUT_A = 272.74         # reference seconds: the first time the passage is heard (kept up to here)
CUT_B = 314.79         # the same music the second time (kept from here)
XFADE = 0.04
LIVE = 313.0
HOLD = 15.0
TOTAL = LIVE + HOLD


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    src = Path(sys.argv[1]).resolve()
    if ROOT in src.parents:
        raise SystemExit("Keep the song audio outside the repository.")
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != SHA256:
        raise SystemExit(f"Unexpected audio: sha256 {got}")
    if not (SNAPSHOT / "engine/render.py").exists():
        run([sys.executable, str(ROOT / "tools/nine_colours_minor/prepare.py")])
    WORK.mkdir(parents=True, exist_ok=True)
    live = WORK / "live.wav"
    fc = (f"[0:a]atrim=0:{CUT_A + XFADE / 2},asetpts=PTS-STARTPTS[a];"
          f"[0:a]atrim={CUT_B - XFADE / 2},asetpts=PTS-STARTPTS[b];"
          f"[a][b]acrossfade=d={XFADE}:c1=tri:c2=tri,atrim=0:{LIVE},asetpts=PTS-STARTPTS[o]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[o]", "-ac", "2",
         "-ar", "48000", "-c:a", "pcm_s24le", str(live)])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(live), "-af", f"apad=whole_dur={TOTAL}", "-t", f"{TOTAL}",
         "-c:a", "pcm_s24le", str(WORK / "score.wav")])
    wav = WORK / "mono22k.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "score.wav"), "-ac", "1", "-ar", "22050", str(wav)])
    env = dict(os.environ, NUMBA_CACHE_DIR=str(WORK / "numba"))
    subprocess.run([sys.executable, str(SNAPSHOT / "engine/analyze.py"), str(wav), str(WORK / "features.npz")],
                   env=env, check=True)
    (WORK / "audio_source.txt").write_text(f"{src}\n{SHA256}\ncut {CUT_A} to {CUT_B}\n")
    print("ready:", live, WORK / "score.wav", WORK / "features.npz")


if __name__ == "__main__":
    main()
