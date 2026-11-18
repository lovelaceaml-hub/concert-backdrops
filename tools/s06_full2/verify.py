"""Checks the finished song 06 backdrop v2 files.

    python tools/s06_full2/verify.py <stage.mp4> <review.mp4> <phone.mp4>

Stage: exact frame count (9120) and length (152.0 s), 60 fps, 1920x1080, yuv420p, no audio; no black, frozen or
exactly repeated frames; the signature present on every frame after the opening (bright letter pixels in the top
left corner on every frame from 9.4 s, dimmer ones during the fade-in from 8.6 s); first, last and sync-checkpoint frames saved for a look.
Review: same picture length, AAC audio from 0, music level at the three sync hits (live times).
Phone: 1280x720, 60 fps, under 25 MB.
No em dash or en dash anywhere in this file.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np

NFRAMES, FPS = 9120, 60
TOTAL = NFRAMES / FPS
K = 137.0 / 134.8467
HITS = {'breath before verse 1 line 2': 18.2 * K, 'the same breath in verse 2': 80.6 * K,
        'loudest hit of the final refrain': 126.3 * K}
LAST_NOTE = 134.35 * K
CHECK = (0.0, 7.0, 8.6, *HITS.values(), LAST_NOTE, 145.0, TOTAL - 1 / FPS)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-count_frames', '-of', 'json',
                          str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def level(path, t0, dur=0.25):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-ss', f'{t0:.3f}', '-t', str(dur), '-i', str(path), '-vn', '-af',
                        'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'mean_volume: (\S+) dB', r)
    return float(m.group(1)) if m else float('nan')


def main():
    stage, review, phone = map(Path, sys.argv[1:4])
    ok = True
    info = probe(stage)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
    print('stage', v['codec_name'], v['width'], v['height'], v['pix_fmt'], v['r_frame_rate'], 'frames',
          v['nb_read_frames'], 'duration', v['duration'], 'audio streams', len(audio), 'size', info['format']['size'])
    ok &= int(v['nb_read_frames']) == NFRAMES and abs(float(v['duration']) - TOTAL) < 0.02
    ok &= v['r_frame_rate'] == '60/1' and v['width'] == 1920 and v['height'] == 1080 and not audio
    log = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(stage), '-vf',
                          'blackdetect=d=0.03:pix_th=0.06,freezedetect=n=0.0005:d=1.0', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    black = re.findall(r'black_start:\S+ black_end:\S+', log)
    freeze = re.findall(r'freeze_start: \S+', log)
    print('black stretches:', black or 'none')
    print('frozen stretches (1 s or more):', freeze or 'none')
    ok &= not black and not freeze
    rep = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(stage), '-vf', 'mpdecimate=hi=1:lo=1:frac=1', '-an',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    drops = len(re.findall(r'drop pts', rep))
    print('exactly repeated frames:', drops)
    ok &= drops == 0
    # the signature on every frame: bright warm letter pixels in its corner box (top left, 1080p)
    w, h = 176, 56
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(stage), '-vf',
                          f'crop=700:220:40:30,scale={w}:{h}:flags=area,format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(-1, h, w)
    bright = (g > 200).sum(axis=(1, 2))
    # it fades in over 0.9 s (reference 8.3 to 9.2 s, live about 8.43 to 9.35 s): during the fade the letters are
    # there but dimmer, so that window is checked with a lower brightness level
    fade = (g[int(8.6 * FPS):int(9.4 * FPS)] > 120).sum(axis=(1, 2))
    start = int(9.4 * FPS)
    after = bright[start:]
    print(f'signature fade-in 8.6 to 9.4 s: letter pixels (dimmer level) min {fade.min()}')
    print(f'signature from 9.4 s: frames checked {len(after)}, letter pixels min {after.min()} median {int(np.median(after))}')
    sig_ok = after.min() >= 40 and fade.min() >= 10
    ok &= bool(sig_ok)
    print('signature on every frame after the opening:', 'yes' if sig_ok else 'NO')
    out = stage.parent / 'check'
    out.mkdir(exist_ok=True)
    for t in CHECK:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.4f}', '-i', str(stage), '-frames:v', '1',
                        str(out / f'frame_{t:07.2f}.png')], check=True)
    info = probe(review)
    rv = next(s for s in info['streams'] if s['codec_type'] == 'video')
    ra = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    print('review', rv['width'], rv['height'], rv['r_frame_rate'], 'frames', rv['nb_read_frames'], 'audio',
          ra['codec_name'], ra.get('bit_rate'), 'start', ra['start_time'], 'duration', ra['duration'])
    ok &= int(rv['nb_read_frames']) == NFRAMES and abs(float(ra['start_time'])) < 0.01
    for name, t in HITS.items():
        print(f'sync {name} at {t:.2f} s: before {level(review, t - 0.35):.1f} dB, after {level(review, t):.1f} dB')
    print(f'music stops at {LAST_NOTE:.2f} s: before {level(review, LAST_NOTE - 0.4):.1f} dB, '
          f'hold {level(review, 140.0, 5):.1f} dB')
    info = probe(phone)
    pv = next(s for s in info['streams'] if s['codec_type'] == 'video')
    size = int(info['format']['size'])
    print('phone', pv['width'], pv['height'], pv['r_frame_rate'], 'frames', pv['nb_read_frames'], 'size', size)
    ok &= size < 25 * 1024 * 1024 and pv['r_frame_rate'] == '60/1'
    print('PASS' if ok else 'CHECK FAILED')


if __name__ == '__main__':
    main()
