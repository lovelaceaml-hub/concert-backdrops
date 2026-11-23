"""Prepare the verified complete recording for the renewed Song 11 film."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_AUDIO = "70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, default=ROOT / "work/song-inputs/s11-original.mp3")
    args = parser.parse_args()
    source = args.audio.resolve()
    if not source.is_file():
        raise SystemExit("Supply the original Song 11 choir recording with --audio.")
    if hashlib.sha256(source.read_bytes()).hexdigest() != EXPECTED_AUDIO:
        raise SystemExit("The input does not match the project's verified full recording.")
    env = dict(os.environ, S11_AUDIO=str(source), PYTHONHASHSEED="0",
               PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1")
    subprocess.run([sys.executable, str(ROOT / "tools/s11_full2/s11_prepare.py")],
                   cwd=ROOT, env=env, check=True)
    work = ROOT / "work/s11_full2"
    if not (work / "music_fx.npz").is_file():
        subprocess.run([sys.executable, str(ROOT / "tools/s11_full2/s11_music_map.py"),
                        "--audio", str(work / "score.wav"), "--out", str(work / "music_fx.npz")],
                       cwd=ROOT, env=env, check=True)
    sys.path.insert(0, str(ROOT))
    from tools.s11_renewed.render import validate_full_analysis
    validate_full_analysis()
    receipt = dict(source_audio_sha256=EXPECTED_AUDIO, source_clock=[0, 260],
                   audio_fade_out_seconds=0.05, silent_hold_seconds=15,
                   duration_seconds=275, picture_delay_seconds=0.1,
                   analysis={name: hashlib.sha256((work / name).read_bytes()).hexdigest()
                             for name in ("score.wav", "features.npz", "music_fx.npz")})
    target = ROOT / "work/s11_renewed/preparation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
