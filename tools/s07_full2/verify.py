"""Check a finished song 07 v2 video: length, frame rate, black, frozen, repeated and dropped frames, white-outs,
the signature on every frame after the opening, the calm bottom third, audio level and sync on 3 hits.

    python tools/s07_full2/verify.py "<video.mp4>" [--audio]

No em dash or en dash anywhere in this file.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clock  # noqa: E402

W, H, FPS = 480, 270, clock.FPS
# three hits (reference seconds, measured onsets) checked against the conformed music in the review copy
HITS_REF = [53.4, 130.5, 231.6]
# the date line of the signature ("DEC 6 · 4:30 PM") in 480x270 pixels
SIG = (slice(int(112 / 4), int(152 / 4)), slice(int(150 / 4), int(420 / 4)))


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,pix_fmt,"
                          "duration,bit_rate:format=duration,size", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def scan(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo",
                          "-"], stdout=subprocess.PIPE)
    size = W * H
    mean, diff, white, sig, sigc, low, prev = [], [], [], [], [], [], None
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.float32)
        mean.append(f.mean())
        white.append((f > 245).mean())
        s = f[SIG]
        sig.append(s.max())
        sigc.append(float(np.percentile(s, 98) - np.percentile(s, 30)))
        low.append(np.percentile(f[int(H * 0.67):], 99.5))
        diff.append(0.0 if prev is None else float(np.abs(f - prev).mean()))
        prev = f
    p.wait()
    return [np.array(x) for x in (mean, diff, white, sig, sigc, low)]


def audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    path = sys.argv[1]
    info = probe(path)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    print(f"video {v['codec_name']} {v['width']}x{v['height']} {v['pix_fmt']} r={v['r_frame_rate']} "
          f"avg={v['avg_frame_rate']} frames={v.get('nb_frames')} duration={info['format']['duration']} s, "
          f"size {int(info['format']['size']) / 1e6:.1f} MB")
    mean, diff, white, sig, sigc, low = scan(path)
    n = len(mean)
    fps = eval(v["r_frame_rate"])
    print(f"decoded frames {n} = {n / fps:.3f} s (expected {clock.TOTAL * fps:.0f} = {clock.TOTAL:.3f} s)")
    print(f"darkest frame mean {mean.min():.1f} at {mean.argmin() / fps:.2f} s (black would be under 4); "
          f"brightest frame mean {mean.max():.1f} at {mean.argmax() / fps:.2f} s")
    print(f"first frame mean {mean[0]:.1f}, last frame mean {mean[-1]:.1f}")
    print(f"most near-white pixels in one frame: {100 * white.max():.2f} % at {white.argmax() / fps:.2f} s "
          f"(a white-out would be over 30 %)")
    rep = np.flatnonzero(diff[1:] < 0.01) + 1
    print(f"repeated (identical) neighbour frames: {len(rep)}" + (f", first at {rep[:8] / fps}" if len(rep) else ""))
    still = diff < 0.03
    run, best, at = 0, 0, 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run > best:
            best, at = run, i
    print(f"longest frozen stretch {best / fps:.2f} s ending at {at / fps:.2f} s")
    jumps = np.flatnonzero(diff > 10.0)
    print(f"big jumps (flash or cut): {len(jumps)}" + (f" at {jumps[:10] / fps}" if len(jumps) else "")
          + f"; largest frame change {diff.max():.2f} at {diff.argmax() / fps:.2f} s")
    after = slice(int(9.0 * fps), n)
    print(f"signature date line after the opening: brightest pixel min {sig[after].min():.0f}, contrast min "
          f"{sigc[after].min():.0f} at {(np.argmin(sigc[after]) + int(9 * fps)) / fps:.2f} s "
          f"(text present: brightest over 200 and contrast over 40)")
    print(f"bottom third: brightest 99.5th percentile {low.max():.0f} at {low.argmax() / fps:.2f} s, "
          f"median {np.median(low):.0f}")
    if "--audio" in sys.argv:
        a = audio(path)
        sr = 8000
        print(f"audio {len(a) / sr:.3f} s, peak {20 * np.log10(np.abs(a).max() + 1e-9):.1f} dBFS")
        for h in HITS_REF:
            hl = clock.live(h)
            seg = a[int((hl - 0.6) * sr):int((hl + 0.6) * sr)]
            e = np.convolve(np.abs(np.diff(seg)), np.ones(80) / 80, "same")
            got = hl - 0.6 + np.argmax(e) / sr
            print(f"hit ref {h:.1f} -> live {hl:.2f}: strongest attack in the file at {got:.2f} s "
                  f"(off by {got - hl:+.2f} s)")
        tail = a[-int(14 * sr):]
        print(f"last 14 s RMS {20 * np.log10(np.sqrt((tail ** 2).mean()) + 1e-9):.1f} dBFS (silent hold)")


if __name__ == "__main__":
    main()
