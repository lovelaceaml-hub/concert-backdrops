"""Check song 05's finished backdrop (version 2): length, sync, frames, the signature, first and last frames.

    python tools/s05_full2/verify05.py --video "out/s05_full2/05 God Bless You! - Backdrop v2 - review 1080p60.mp4" \
        --audio out/s05_full2/music_conformed.wav --frames out/s05_full2/check

Prints a plain report. Sync: (1) the music in the video against the conformed music around the three measured
hits (stage 53.39, 115.74, 142.93 s), offset under one frame; (2) the picture's own reaction to the music
(frame brightness change) against the music's loudness around each hit, best lag reported. Frozen frames:
neighbouring frames that are pixel identical. Signature: the top left corner of every frame after the opening
compared with one frame (correlation, must stay high: never covered, never flashing).
No em dash or en dash anywhere in this file.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import timing  # noqa: E402

NFRAMES = timing.NFRAMES
FPS = timing.FPS
HITS = tuple(timing.stage(r) for r in (51.43, 111.48, 137.67))
SIG = (40, 24, 700, 210)            # the signature's box at 1080p: x0, y0, x1, y1


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
    tail = got[int((timing.LIVE + 0.4) * rate):]
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
    # the picture follows the music: brightness change against loudness, around each hit
    fr = np.abs(np.diff(f.mean(axis=(1, 2))))
    env = np.interp(np.arange(len(fr)) / FPS, np.arange(len(src)) / rate, src)
    for hh in HITS:
        i0, i1 = int((hh - 4) * FPS), int((hh + 4) * FPS)
        a_ = (env[i0:i1] - env[i0:i1].mean())
        best = max(range(-30, 31), key=lambda k: float(np.dot(a_, fr[i0 + k:i1 + k] - fr[i0 + k:i1 + k].mean())))
        print(f"picture reacts to the music near {hh:6.2f} s: best lag {best / FPS * 1000:+.0f} ms")
    # the signature on every frame after the opening
    x0, y0, x1, y1 = SIG
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(args.video), "-vf",
                        f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0},scale=166:46,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    g = np.frombuffer(r.stdout, np.uint8).reshape(-1, 46, 166).astype(np.float32)
    ref = g[int(30 * FPS)]
    rz = (ref - ref.mean()) / (ref.std() + 1e-6)
    cor = np.array([float(((x - x.mean()) / (x.std() + 1e-6) * rz).mean()) for x in g])
    after = cor[int(10.0 * FPS):]
    print(f"signature after the opening (from 10.0 s): lowest match {after.min():.3f} at frame "
          f"{int(after.argmin()) + int(10.0 * FPS)} ({'OK' if after.min() > 0.85 else 'CHECK'}); "
          f"present from frame {int(np.argmax(cor > 0.85))}")
    if args.frames:
        args.frames.mkdir(parents=True, exist_ok=True)
        for name, sel in (("first", "eq(n\\,0)"), ("last", f"eq(n\\,{NFRAMES - 1})")):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(args.video), "-vf", f"select='{sel}'",
                            "-frames:v", "1", str(args.frames / f"{name}.png")], check=True)
        print(f"first and last frames saved in {args.frames}")


if __name__ == "__main__":
    main()
