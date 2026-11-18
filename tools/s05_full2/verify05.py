"""Check song 05's finished backdrop: length, audio sync, dropped or frozen frames, black frames, first and last.

    python tools/s05_full2/verify05.py --video "out/s05_full2/05 God Bless You! - Backdrop 1080p30.mp4" \
        --audio <s05.m4a> --frames out/s05_full2/check

Prints a plain report. Sync: the music's loudness envelope in the video is cross-correlated with the source
around three hit points (0:08, 0:51.5, 1:58); the offset must be under one frame. Frozen frames: neighbouring
frames that are pixel identical (the picture is always gently alive, so there should be none).
No em dash or en dash anywhere in this file.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

NFRAMES = 5045
FPS = 30
HITS = (8.0, 51.5, 118.0)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,"
                        "sample_rate,channels,bit_rate,start_time", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def pcm(path, sr=8000):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le",
                        "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def envelope(x, sr=8000, hop=40):
    n = len(x) // hop
    return np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12), sr / hop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--frames", type=Path, default=None)
    args = ap.parse_args()
    info = probe(args.video)
    v = [s for s in info["streams"] if s.get("width")][0]
    a = [s for s in info["streams"] if s.get("sample_rate")][0]
    print(f"size {int(info['format']['size']) / 1e6:.1f} MB, duration {float(info['format']['duration']):.3f} s")
    print(f"video {v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']} {v['pix_fmt']} frames {v.get('nb_frames')}")
    print(f"audio {a['codec_name']} {a['sample_rate']} Hz {a['channels']} ch {int(a.get('bit_rate', 0)) // 1000} kb/s "
          f"start {a.get('start_time')}")
    ok = int(v.get("nb_frames", 0)) == NFRAMES
    print(f"frame count {'OK' if ok else 'WRONG'} (want {NFRAMES} = {NFRAMES / FPS:.3f} s)")
    # sync
    src, _ = envelope(pcm(args.audio))
    got, rate = envelope(pcm(args.video))
    for h in HITS:
        i0, i1 = int((h - 3) * rate), int((h + 3) * rate)
        seg = src[i0:i1]
        best = max(range(-40, 41), key=lambda k: float(np.dot(seg, got[i0 + k:i1 + k])))
        print(f"sync at {h:6.1f} s: offset {best / rate * 1000:+.1f} ms ({'OK' if abs(best / rate) < 1 / FPS else 'OFF'})")
    tail = got[int(153.4 * rate):]
    print(f"after the music: peak level {20 * np.log10(tail.max() + 1e-9):.1f} dBFS (silence expected)")
    # frames: identical neighbours and dark frames, on a small grey copy of every frame
    w, h = 96, 54
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(args.video), "-vf", f"scale={w}:{h},format=gray", "-f",
                        "rawvideo", "-"], capture_output=True, check=True)
    f = np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.int16)
    diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    same = int((diff == 0).sum())
    mean = f.mean(axis=(1, 2))
    print(f"decoded frames {len(f)}; identical neighbours {same}; smallest change {diff.min():.3f}; "
          f"largest change {diff.max():.2f} at frame {int(diff.argmax()) + 1}")
    print(f"brightness: darkest frame {mean.min():.1f}/255 at {int(mean.argmin())}, brightest {mean.max():.1f}/255 "
          f"at {int(mean.argmax())}; black frames (mean under 16): {int((mean < 16).sum())}")
    if args.frames:
        args.frames.mkdir(parents=True, exist_ok=True)
        for name, sel in (("first", "eq(n\\,0)"), ("last", f"eq(n\\,{NFRAMES - 1})")):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(args.video), "-vf", f"select='{sel}'",
                            "-frames:v", "1", str(args.frames / f"{name}.png")], check=True)
        print(f"first and last frames saved in {args.frames}")


if __name__ == "__main__":
    main()
