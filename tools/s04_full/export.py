"""Join song 04's rendered parts, add the music, encode the master and the share copy, and check them.

    python tools/s04_full/export.py

Inputs: work/s04/parts/p0.mp4 ... p7.mp4 (render.py --range), work/s04/s04.wav (the reference music padded
with silence to 234.433 s). Outputs in work/s04/out/ (never committed):
    04 I'm Sorry, Please Forgive Me - Backdrop.mp4          master, H.264 CRF 18, yuv420p, AAC 320k, faststart
    04 I'm Sorry, Please Forgive Me - Backdrop (share).mp4  1280x720, under 25 MB
and checks.txt: length and frame count, black and frozen frames, audio sync at three hits.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/s04'
OUT = WORK / 'out'
NAME = "04 I'm Sorry, Please Forgive Me - Backdrop"
FRAMES = 7033
DUR = FRAMES / 30.0
HITS = (43.5, 83.9, 142.0)


def run(cmd, **kw):
    print(' '.join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def probe(path, entries):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', entries,
                        '-of', 'default=nw=1', str(path)], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def pcm(path, start, dur):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', str(path), '-ac', '1',
                        '-ar', '8000', '-f', 's16le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.int16).astype(np.float64)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = [WORK / f'parts/p{i}.mp4' for i in range(8)]
    for p in parts:
        if not p.exists():
            sys.exit(f'missing {p}')
    lst = WORK / 'parts/list.txt'
    lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    master = OUT / f'{NAME}.mp4'
    share = OUT / f'{NAME} (share).mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(WORK / 's04.wav'),
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
         '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{DUR:.4f}', '-movflags', '+faststart', str(master)])
    # share copy: two-pass to fit under 25 MB (video about 700 kb/s, audio 128 kb/s)
    vb = int((24.0 * 8 * 1024 * 1024 / DUR - 128000) * 0.97)
    common = ['-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-b:v', str(vb),
              '-pix_fmt', 'yuv420p']
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), *common, '-pass', '1', '-passlogfile',
         str(OUT / 'pass'), '-an', '-f', 'mp4', '/dev/null'])
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), *common, '-pass', '2', '-passlogfile',
         str(OUT / 'pass'), '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(share)])

    lines = []
    for f in (master, share):
        n = probe(f, 'stream=nb_read_frames,width,height,r_frame_rate')
        d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=nw=1',
                            str(f)], capture_output=True, text=True).stdout.strip()
        lines.append(f'{f.name}: {n.replace(chr(10), ", ")}, {d.replace(chr(10), ", ")}')
    bl = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(master), '-vf', 'blackdetect=d=0.05:pix_th=0.08',
                         '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lines.append('black frames: ' + (' | '.join(x.split('] ')[-1] for x in bl.splitlines() if 'black_start' in x)
                                     or 'none'))
    fr = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(master), '-vf', 'freezedetect=n=0.0003:d=1.0',
                         '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr
    frozen = [x.split('] ')[-1] for x in fr.splitlines() if 'freeze_start' in x or 'freeze_end' in x]
    lines.append('frozen stretches (no visible change for 1 s or more): ' + (' | '.join(frozen) or 'none'))
    # audio sync: the music in the master lines up with the source at each hit (offset in ms)
    src = ROOT / 'work/s04/s04.wav'
    for h in HITS:
        a = pcm(src, h - 1.0, 2.0)
        b = pcm(master, h - 1.5, 3.0)
        c = np.correlate(b - b.mean(), a - a.mean(), mode='valid')
        off = (int(np.argmax(c)) - 4000) / 8.0
        lines.append(f'audio sync at {h:.1f} s: offset {off:+.1f} ms')
    for t, nm in ((0.0, 'first'), (DUR - 1 / 30.0, 'last')):
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.4f}', '-i', str(master), '-frames:v', '1',
             str(OUT / f'{nm}_frame.png')])
    (OUT / 'checks.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
