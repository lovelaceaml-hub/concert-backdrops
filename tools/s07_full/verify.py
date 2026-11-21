"""Check a finished song 07 backdrop: length, frame count, black, frozen and dropped frames, audio and hit sync.

    python tools/s07_full/verify.py "<master.mp4>"

No em dash or en dash anywhere in this file.
"""
import json
import subprocess
import sys

import numpy as np

HITS = [53.35, 130.46, 231.55]
W, H, FPS = 160, 90, 30


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def frames(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo",
                          "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    path = sys.argv[1]
    info = probe(path)
    print(json.dumps(info, indent=1))
    f = frames(path)
    n = len(f)
    mean = f.mean(axis=(1, 2))
    diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    print(f"frames {n} ({n / FPS:.3f} s at {FPS} fps)")
    print(f"darkest frame mean {mean.min():.1f} at {mean.argmin() / FPS:.2f} s (black would be under 4)")
    print(f"first frame mean {mean[0]:.1f}, last frame mean {mean[-1]:.1f}")
    frozen = np.flatnonzero(diff < 0.02)
    print(f"identical neighbour frames: {len(frozen)}" + (f" first at {frozen[:10] / FPS}" if len(frozen) else ""))
    # longest stretch with almost no change (a freeze) outside the final hold
    still = diff < 0.05
    run, best, at = 0, 0, 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run > best:
            best, at = run, i
    print(f"longest near-still stretch {best / FPS:.2f} s ending at {at / FPS:.2f} s")
    jumps = np.flatnonzero(diff > 12.0)
    print(f"big jumps (cuts): {len(jumps)} {jumps[:10] / FPS}")
    a = audio(path)
    sr = 8000
    print(f"audio {len(a) / sr:.3f} s, peak {20 * np.log10(np.abs(a).max() + 1e-9):.1f} dBFS")
    for h in HITS:
        seg = a[int((h - 0.6) * sr):int((h + 0.6) * sr)]
        e = np.convolve(np.abs(np.diff(seg)), np.ones(80) / 80, "same")
        print(f"hit {h:.2f}: strongest attack in the file at {h - 0.6 + np.argmax(e) / sr:.2f} s")
    tail = a[-int(14 * sr):]
    print(f"last 14 s RMS {20 * np.log10(np.sqrt((tail ** 2).mean()) + 1e-9):.1f} dBFS (silent hold)")


if __name__ == "__main__":
    main()
