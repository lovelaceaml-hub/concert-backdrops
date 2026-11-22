"""Song 03 full backdrop: check a delivered video.

    python tools/s03_full/verify.py <video.mp4> <song audio outside the repo> [--frames outdir]

Checks: frame count and length (11,103 frames, 370.1 s), stream format, audio sync at three hits (the music
inside the video against the original file, by cross-correlation), black frames, frozen stretches, and the
loudness after the music (silence). Optionally saves the first, last and hit frames for a look.
No em dash or en dash anywhere in this file.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

NFRAMES = 11103
HITS = (36.9, 236.8, 325.7)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def pcm(path, t0, dur, sr=22050):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-t", f"{dur}", "-i", str(path), "-ac", "1",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    video, song = Path(sys.argv[1]), Path(sys.argv[2])
    frames_dir = Path(sys.argv[sys.argv.index("--frames") + 1]) if "--frames" in sys.argv else None
    ok = True
    info = probe(video)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"][0]
    n = int(v["nb_read_frames"])
    print(f"video {v['codec_name']} {v['width']}x{v['height']} {v['pix_fmt']} {v['r_frame_rate']} frames {n} "
          f"duration {float(v['duration']):.3f} s")
    print(f"audio {a['codec_name']} {a['sample_rate']} Hz {a['channels']} ch {int(a.get('bit_rate', 0)) // 1000} kb/s "
          f"duration {float(a['duration']):.3f} s; file {int(info['format']['size']) / 1e6:.1f} MB")
    if n != NFRAMES:
        print(f"FAIL frame count {n} != {NFRAMES}")
        ok = False
    sr = 22050
    for hit in HITS:
        if hit > 351:
            continue
        ref = pcm(song, hit - 2.0, 4.0, sr)
        got = pcm(video, hit - 2.5, 5.0, sr)
        c = np.correlate(got, ref, mode="valid")
        lag = (int(np.argmax(c)) - int(0.5 * sr)) / sr
        print(f"audio sync at {hit:.1f} s: offset {lag * 1000:+.1f} ms")
        if abs(lag) > 0.02:
            ok = False
    tail = pcm(video, 352.0, 18.0, sr)
    print(f"after the music (352 s to the end): peak {20 * np.log10(max(np.abs(tail).max(), 1e-9)):.1f} dBFS")
    log = subprocess.run(["ffmpeg", "-v", "info", "-i", str(video), "-vf",
                          "blackdetect=d=0.1:pix_th=0.06,freezedetect=n=-60dB:d=1.5", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    black = [l for l in log.splitlines() if "black_start" in l]
    frozen = [l for l in log.splitlines() if "freeze_start" in l]
    print(f"black stretches: {len(black)}" + ("".join("\n  " + l.strip() for l in black)))
    print(f"frozen stretches (1.5 s or longer): {len(frozen)}" + ("".join("\n  " + l.strip() for l in frozen[:20])))
    if black or frozen:
        ok = False
    if frames_dir:
        frames_dir.mkdir(parents=True, exist_ok=True)
        for name, t in [("first", 0.0), ("hit036.9", 36.9), ("hit236.8", 236.8), ("hit325.7", 325.7),
                        ("last", (NFRAMES - 1) / 30.0)]:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                            str(frames_dir / f"{name}.png")], check=True)
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")


if __name__ == "__main__":
    main()
