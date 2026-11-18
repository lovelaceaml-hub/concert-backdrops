"""Join song 10's rendered parts with the soundtrack, make the master and the share copy, and check them.

    python tools/s10_full/finish.py

Master: H.264 CRF 18, yuv420p, AAC 320k, faststart, 1920x1080, 30 fps. Share copy: 1280x720, under 25 MB.
Checks: exact frame count and length, no black frames, no repeated (frozen) frames, audio length, and the
loudness onsets of three hits against the song's measured times. Prints a report; writes out/s10_full/CHECKS.txt.
No em dash or en dash anywhere in this file.
"""
import glob
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/s10_full'
WORK = ROOT / 'work/s10_full'
NF, FPS = 6799, 30
NAME = '10 Our Mother Saves the World - Concert Backdrop'
HITS = [25.33, 52.04, 205.11]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def frames_of(path):
    out = run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
               'stream=nb_read_frames', '-of', 'csv=p=0', str(path)])
    return int(out.strip().split(',')[0])


def main():
    parts = sorted(p for p in glob.glob(str(OUT / 'parts/p*.mp4')) if not p.endswith('.tmp.mp4'))
    starts = [int(Path(p).stem[1:]) for p in parts]
    counts = [frames_of(p) for p in parts]
    pos = 0
    for s, c, p in zip(starts, counts, parts):
        assert s == pos, f'gap or overlap at frame {pos}: {p} starts at {s}'
        pos += c
    assert pos == NF, f'{pos} frames rendered, {NF} expected'
    lst = OUT / 'parts.txt'
    lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    master = OUT / f'{NAME} - 1080p master.mp4'
    share = OUT / f'{NAME} - 720p share.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(WORK / 'score.wav'),
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-r', str(FPS), '-g', '60', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
         '-color_range', 'tv', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{NF / FPS:.6f}',
         '-movflags', '+faststart', str(master)])
    # share copy: two-pass to a size target of about 22 MB
    dur = NF / FPS
    vbr = int((22.0 * 8 * 1024 * 1024) / dur - 128000)
    for ps in (1, 2):
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(master), '-vf', 'scale=1280:720:flags=lanczos',
             '-c:v', 'libx264', '-preset', 'slow', '-b:v', str(vbr), '-pass', str(ps),
             '-passlogfile', str(OUT / 'pass'), '-pix_fmt', 'yuv420p', '-g', '60']
            + (['-an', '-f', 'mp4', '/dev/null'] if ps == 1 else
               ['-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(share)]))
    rep = {}
    for f in (master, share):
        info = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                               'stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames,pix_fmt:'
                               'format=duration,size', '-of', 'json', str(f)]))
        rep[f.name] = dict(info=info, frames=frames_of(f), sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                           mb=f.stat().st_size / 1048576)
    # black and frozen frames on a small grey copy of the master
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(master), '-vf', 'scale=64:36', '-pix_fmt', 'gray',
                          '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    mean = g.mean(axis=(1, 2))
    diff = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    rep['frames_decoded'] = int(len(g))
    rep['darkest_frame'] = dict(index=int(mean.argmin()), mean=float(mean.min()))
    rep['black_frames'] = int((mean < 6).sum())
    rep['identical_neighbours'] = int((diff < 0.02).sum())
    rep['identical_neighbour_times'] = [round(float(i) / FPS, 2) for i in np.nonzero(diff < 0.02)[0][:40]]
    # audio sync: the soundtrack's onset peaks near the measured hits
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(master), '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(pcm, np.int16).astype(np.float32)
    hop = 80
    env = np.sqrt(np.convolve(a * a, np.ones(hop) / hop, 'same')[::hop] + 1.0)
    flux = np.maximum(np.diff(np.log(env)), 0)
    sync = []
    for h in HITS:
        i0, i1 = int((h - 0.5) * 100), int((h + 0.5) * 100)
        sync.append(dict(expected=h, found=round((i0 + int(np.argmax(flux[i0:i1]))) / 100.0, 2)))
    rep['hits'] = sync
    rep['audio_seconds'] = len(a) / 8000.0
    text = json.dumps(rep, indent=2)
    (OUT / 'CHECKS.txt').write_text(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
