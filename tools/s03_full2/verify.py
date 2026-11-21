"""Song 03 backdrop v2: check the three delivery files.

    python tools/s03_full2/verify.py

Checks: exact length and frame count (19,680 frames at 60 fps, 328.000 s), size and codec, no black frames, no
frozen stretches longer than 2 s, no repeated (duplicate) frames, the signature present on every second after
the opening, sync of the review file's music to the conformed music at three hits, the phone file under 25 MB,
and SHA-256 of each file. Writes out/s03_full2/verify.txt. No em dash or en dash anywhere in this file.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s03_full2"
OUT = ROOT / "out/s03_full2"
NAME = "03 I Reminisce About Your Love - Backdrop v2"
FPS, TOTAL = 60, 328.0
NFRAMES = int(round(FPS * TOTAL))
HITS = [26.63, 181.35, 242.21]
lines = []


def say(s):
    print(s, flush=True)
    lines.append(s)


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def count_frames(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(f)], capture_output=True, text=True,
                       check=True)
    return int(r.stdout.strip())


def gray_frames(f, w=96, h=54):
    """Every frame, small and grey, for black, frozen and repeat checks."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", f"scale={w}:{h}:flags=area,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)


def frame_at(f, t, crop=None):
    vf = "format=rgb24" if crop is None else f"crop={crop},format=rgb24"
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(f), "-frames:v", "1", "-vf", vf,
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8)


def audio(f, sr=22050):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def main():
    files = {k: OUT / f"{NAME} - {k} {'720p60' if k == 'phone' else '1080p60'}.mp4"
             for k in ("stage", "review", "phone")}
    for k, f in files.items():
        p = probe(f)
        v = [s for s in p["streams"] if s["codec_type"] == "video"][0]
        a = [s for s in p["streams"] if s["codec_type"] == "audio"]
        n = count_frames(f)
        dur = float(p["format"]["duration"])
        size = f.stat().st_size
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        say(f"{f.name}: {v['width']}x{v['height']} {v['codec_name']} {v['pix_fmt']} {v['r_frame_rate']} fps, "
            f"{n} frames, {dur:.3f} s, audio {'none' if not a else a[0]['codec_name'] + ' ' + a[0].get('bit_rate', '?')}, "
            f"{size / 1e6:.1f} MB, sha256 {sha}")
        ok = n == NFRAMES and abs(dur - TOTAL) < 0.02 and v["r_frame_rate"] == "60/1"
        if k == "phone":
            ok = ok and size < 25e6
        say(f"  length and rate {'OK' if ok else 'PROBLEM'}")
    f = files["stage"]
    g = gray_frames(f)
    mean = g.mean(axis=(1, 2))
    say(f"stage: darkest frame mean {mean.min():.1f} of 255 at {mean.argmin() / FPS:.2f} s; brightest pixel "
        f"{g.max():.0f}; black frames (mean under 8): {int((mean < 8).sum())}")
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    rep = int((d == 0).sum())
    say(f"stage: identical consecutive frames: {rep}; smallest change {d.min():.4f}")
    still = d < 0.02
    run, longest, at = 0, 0, 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run > longest:
            longest, at = run, i
    say(f"stage: longest near-frozen stretch {longest / FPS:.2f} s (ending {at / FPS:.2f} s)")
    # the signature: its date line has strong edges in every second after the opening
    miss = []
    for t in np.arange(12.0, TOTAL, 1.0):
        px = frame_at(f, t, "420:150:40:30").reshape(150, 420, 3).astype(np.float32)
        lum = px.mean(axis=2)
        edge = np.abs(np.diff(lum, axis=1)).max()
        if edge < 40:
            miss.append(round(float(t), 1))
    say(f"stage: signature present at every whole second from 12 s: {'yes' if not miss else 'NO, missing at ' + str(miss)}")
    # first and last frames
    for t in (0.0, TOTAL - 1.0 / FPS):
        px = frame_at(f, t).reshape(1080, 1920, 3)
        say(f"stage frame at {t:.3f} s: mean {px.mean():.1f}")
    # sync: the review's music against the conformed music at three hits
    ref = audio(WORK / "score.wav")
    rev = audio(files["review"])
    sr = 22050
    for h in HITS:
        a0, a1 = int((h - 1.0) * sr), int((h + 1.0) * sr)
        x, y = ref[a0:a1], rev[a0 - 2205:a1 + 2205]
        c = np.correlate(y, x, mode="valid")
        lag = (int(np.argmax(c)) - 2205) / sr * 1000
        say(f"sync at {h:.2f} s: review music offset {lag:+.1f} ms")
    (OUT / "verify.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
