"""Join song 04's rendered parts (version 2), encode the three delivery files and check them.

    python tools/s04_full2/export.py

Inputs: work/s04v2/parts/p00.mp4 ... (render.py --range, 60 fps, in frame order), work/s04v2/live_hold.wav (the
reference conformed to 220.0 s, then 15 s of silence). Outputs in work/s04v2/out/ (never committed):
    04 I'm Sorry, Please Forgive Me - Backdrop v2 - stage 1080p60.mp4    silent, H.264 CRF 16, yuv420p, faststart
    04 I'm Sorry, Please Forgive Me - Backdrop v2 - review 1080p60.mp4   with the music, AAC 320k, CRF 20
    04 I'm Sorry, Please Forgive Me - Backdrop v2 - phone 720p60.mp4     with the music, under 25 MB
and checks.txt: length and frame count, black, repeated and frozen frames, the signature on every frame after
the opening, audio sync at three hits, first and last frames, SHA-256 of each file.
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/s04v2'
OUT = WORK / 'out'
TITLE = "04 I'm Sorry, Please Forgive Me - Backdrop v2"
FPS = 60
FRAMES = 14100
DUR = FRAMES / FPS
HITS = (27.4, 85.0, 162.0)
SIG_FROM = 11.0            # the signature is fully on from here to the last frame


def run(cmd, **kw):
    print(' '.join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def info(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames,width,height,r_frame_rate,pix_fmt:format=duration,size', '-of',
                        'default=nw=1', str(path)], capture_output=True, text=True, check=True)
    return dict(x.split('=', 1) for x in r.stdout.split())


def pcm(path, start, dur):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', str(path), '-ac', '1',
                        '-ar', '8000', '-f', 's16le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.int16).astype(np.float64)


def frames_gray(path, w=160, h=90):
    """Every frame, small and grey, as an array (n, h, w)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'scale={w}:{h}:flags=area,format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)


def sig_crop(path):
    """The signature corner (top left, 1080p pixels 40..720 x 30..200) of every frame, small and grey."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf',
                        'crop=680:170:40:30,scale=170:42:flags=area,format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 42, 170).astype(np.float32)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-encode', action='store_true')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    parts = sorted((WORK / 'parts').glob('p*.mp4'))
    if not parts:
        sys.exit('no parts')
    stage = OUT / f'{TITLE} - stage 1080p60.mp4'
    review = OUT / f'{TITLE} - review 1080p60.mp4'
    phone = OUT / f'{TITLE} - phone 720p60.mp4'
    music = WORK / 'live_hold.wav'
    if not args.skip_encode:
        lst = WORK / 'parts/list.txt'
        lst.write_text(''.join(f"file '{p}'\n" for p in parts))
        color = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-map', '0:v',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), *color,
             '-frames:v', str(FRAMES), '-an', '-movflags', '+faststart', str(stage)])
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(stage), '-i', str(music), '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', *color,
             '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{DUR:.4f}', '-movflags', '+faststart', str(review)])
        vb = int((23.5 * 8 * 1024 * 1024 / DUR - 128000) * 0.97)
        common = ['-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', str(vb),
                  '-maxrate', str(int(vb * 1.6)), '-bufsize', str(int(vb * 3)), '-pix_fmt', 'yuv420p', '-r', str(FPS)]
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(stage), *common, '-pass', '1', '-passlogfile',
             str(OUT / 'pass'), '-an', '-f', 'mp4', '/dev/null'])
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(stage), '-i', str(music), '-map', '0:v', '-map', '1:a', *common,
             '-pass', '2', '-passlogfile', str(OUT / 'pass'), '-c:a', 'aac', '-b:a', '128k', '-t', f'{DUR:.4f}',
             '-movflags', '+faststart', str(phone)])

    lines = []
    for f in (stage, review, phone):
        d = info(f)
        lines.append(f'{f.name}: {d.get("width")}x{d.get("height")}, {d.get("r_frame_rate")} fps, '
                     f'{d.get("nb_read_frames")} frames, {float(d.get("duration", 0)):.3f} s, '
                     f'{int(d.get("size", 0)) / 1e6:.1f} MB, {d.get("pix_fmt")}')
    g = frames_gray(stage)
    n = len(g)
    lines.append(f'stage frames decoded: {n} (expected {FRAMES})')
    mean = g.mean(axis=(1, 2))
    lines.append(f'darkest frame mean (0..255): {mean.min():.1f} at {mean.argmin() / FPS:.2f} s; brightest '
                 f'{mean.max():.1f} at {mean.argmax() / FPS:.2f} s; frames with mean above 235 (near white): '
                 f'{int((mean > 235).sum())}; below 16 (near black): {int((mean < 16).sum())}')
    diff = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    lines.append(f'frame to frame change: min {diff.min():.4f}, median {np.median(diff):.4f}, max {diff.max():.3f} '
                 f'(at {(diff.argmax() + 1) / FPS:.2f} s)')
    same = np.nonzero(diff < 0.002)[0]
    lines.append(f'repeated frames (no change at all): {len(same)}'
                 + (f', first at {(same[0] + 1) / FPS:.2f} s' if len(same) else ''))
    k = np.convolve((diff < 0.02).astype(int), np.ones(FPS, int), 'valid')
    frozen = np.nonzero(k >= FPS)[0]
    lines.append(f'frozen stretches (1 s with no visible change): {len(frozen)}'
                 + (f', first at {frozen[0] / FPS:.2f} s' if len(frozen) else ''))
    sc = sig_crop(stage)
    i0 = int(SIG_FROM * FPS)
    ref = np.median(sc[i0::30], axis=0)
    mask = ref < (np.median(ref) - 25)          # the navy letters
    dev = np.array([np.abs(c[mask] - ref[mask]).mean() for c in sc[i0:]])
    lines.append(f'signature after {SIG_FROM:.0f} s: letter pixels {int(mask.sum())}, mean deviation per frame '
                 f'max {dev.max():.1f} (at {(dev.argmax() + i0) / FPS:.2f} s), median {np.median(dev):.1f} (0..255)')
    src = WORK / 'live_hold.wav'
    for h in HITS:
        a = pcm(src, h - 1.0, 2.0)
        for f in (review, phone):
            b = pcm(f, h - 1.5, 3.0)
            c = np.correlate(b - b.mean(), a - a.mean(), mode='valid')
            off = (int(np.argmax(c)) - 4000) / 8.0
            lines.append(f'audio sync at {h:.1f} s ({f.name.split(" - ")[-1]}): offset {off:+.1f} ms')
    for t, nm in ((0.0, 'first'), ((FRAMES - 1) / FPS, 'last')):
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.4f}', '-i', str(stage), '-frames:v', '1',
             str(OUT / f'{nm}_frame.png')])
    for f in (stage, review, phone):
        lines.append(f'SHA-256 {f.name}: {sha(f)}')
    (OUT / 'checks.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
