"""Prepare a song made on the song kit: the pinned engines and the song's music (kept outside git).

    python tools/song_kit/prepare.py <song> [--audio file]

Without --audio the song's chosen recording comes from the song catalog (song_data.CATALOG_ID, fetched from
Drive by its file id when it is not in work/song-sources/). As for Song 11 the recording is used unstretched:
the score is the file cut at song_data.LIVE seconds (a 0.05 s fade), then the calm hold in silence. Writes
work/song_kit/<song>/: score.wav, features.npz (the engine's analysis), music_fx.npz (Song 11's music map) and
provenance.json. No em dash or en dash anywhere in this file.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]
sys.path.insert(0, str(ROOT / "tools/nine_colours_minor"))
import prepare as r3  # noqa: E402


def song_data(song):
    path = KIT / "songs" / song / "song_data.py"
    spec = importlib.util.spec_from_file_location(f"{song}_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def recording(D):
    sys.path.insert(0, str(ROOT))
    from pipeline.song_draft import find_song, recording as fetch
    return fetch(ROOT, find_song(ROOT, D.CATALOG_ID))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--stand-in", action="store_true",
                    help="layout work only: accept another recording (labelled in provenance.json, never for delivery)")
    args = ap.parse_args()
    D = song_data(args.song)
    try:
        r3.prepare()
    except subprocess.CalledProcessError:
        # the snapshot prepare also measures the promo medley; the song kit only needs the two engines
        if not (r3.SNAPSHOT / "engine/render.py").exists() or not (r3.CLAUDE / "engine/p3d/words.py").exists():
            raise
    work = ROOT / "work/song_kit" / args.song
    work.mkdir(parents=True, exist_ok=True)
    audio = args.audio or recording(D)
    sha = hashlib.sha256(Path(audio).read_bytes()).hexdigest()
    expect = getattr(D, "AUDIO_SHA256", None)
    if expect and sha != expect and not args.stand_in:
        raise SystemExit(f"Unexpected recording {audio}: {sha}, expected {expect}")
    live, hold = float(D.LIVE), float(getattr(D, "HOLD", 15.0))
    start = float(getattr(D, "AUDIO_START", 0.0))
    total = live + hold
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start}", "-i", str(audio), "-ac", "2", "-ar", "48000",
                    "-af", f"atrim=0:{live},afade=t=out:st={live - 0.05}:d=0.05,apad=whole_dur={total}",
                    "-t", f"{total}", "-c:a", "pcm_s24le", str(work / "score.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "score.wav"), "-ac", "1", "-ar", "22050",
                    str(work / "audio.wav")], check=True)
    env = dict(os.environ, NUMBA_CACHE_DIR=str(work / "numba"))
    subprocess.run([sys.executable, str(r3.SNAPSHOT / "engine/analyze.py"), str(work / "audio.wav"),
                    str(work / "features.npz")], env=env, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/s11_full2/s11_music_map.py"), "--out", str(work / "music_fx.npz")],
                   env=dict(env, S11_AUDIO=str(work / "score.wav")), check=True)
    (work / "provenance.json").write_text(json.dumps(dict(
        song=args.song, title=D.TITLE, engine_commit=r3.ENGINE_COMMIT, claude_reference_commit=r3.CLAUDE_COMMIT,
        audio=str(audio), audio_sha256=sha, stand_in=bool(args.stand_in and sha != expect), audio_start=start, live_seconds=live, hold_seconds=hold,
        total_seconds=total, fps=60), indent=2) + "\n")
    print(f"{args.song} ready: {work}")


if __name__ == "__main__":
    main()
