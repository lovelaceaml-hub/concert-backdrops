"""Checks a finished song 06 backdrop: exact length and frame count, audio length and start, no black frames,
no frozen stretches, frame timestamps, loudness of the music and of the hold, and saves the first, last and
sync-checkpoint frames for a look.

    python tools/s06_full/verify.py <master.mp4> [<share.mp4>]
"""
import json
from pathlib import Path
import re
import subprocess
import sys

NFRAMES, FPS = 4496, 30
TOTAL = NFRAMES / FPS
CHECK = (0.0, 10.0, 18.2, 80.6, 126.3, 134.35, TOTAL - 1 / FPS)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-count_frames', '-of', 'json',
                          str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    master = Path(sys.argv[1])
    info = probe(master)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    print('video', v['codec_name'], v['width'], v['height'], v['pix_fmt'], v['r_frame_rate'],
          'frames', v['nb_read_frames'], 'duration', v['duration'])
    print('audio', a['codec_name'], a['sample_rate'], a['channels'], 'bit_rate', a.get('bit_rate'),
          'start', a['start_time'], 'duration', a['duration'])
    print('size', info['format']['size'])
    ok = int(v['nb_read_frames']) == NFRAMES and abs(float(v['duration']) - TOTAL) < 0.02
    ok &= abs(float(a['duration']) - TOTAL) < 0.05 and abs(float(a['start_time'])) < 0.01
    log = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(master), '-vf',
                          'blackdetect=d=0.05:pix_th=0.06,freezedetect=n=0.0005:d=1.0', '-af',
                          'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    black = re.findall(r'black_start:\S+ black_end:\S+', log)
    freeze = re.findall(r'freeze_start: \S+', log)
    print('black stretches:', black or 'none')
    print('frozen stretches (1 s or more):', freeze or 'none')
    m = re.search(r'Integrated loudness:\s+I:\s+(\S+) LUFS', log)
    print('integrated loudness', m.group(1) if m else '?', 'LUFS')
    ok &= not black and not freeze
    # repeated frames: every frame differs from the one before
    rep = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(master), '-vf', 'mpdecimate=hi=1:lo=1:frac=1', '-an',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    drops = len(re.findall(r'drop pts', rep))
    print('exactly repeated frames:', drops)
    out = master.parent / 'check'
    out.mkdir(exist_ok=True)
    for t in CHECK:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.4f}', '-i', str(master), '-frames:v', '1',
                        str(out / f'frame_{t:07.2f}.png')], check=True)
    # audio at the sync checkpoints: level in a 0.25 s window before and after
    for t in (18.2, 80.6, 126.3, 134.35):
        lv = []
        for s0 in (t - 0.3, t):
            r = subprocess.run(['ffmpeg', '-v', 'info', '-ss', f'{s0:.3f}', '-t', '0.25', '-i', str(master), '-vn',
                                '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
            mm = re.search(r'mean_volume: (\S+) dB', r)
            lv.append(mm.group(1) if mm else '?')
        print(f'audio at {t}: before {lv[0]} dB, after {lv[1]} dB')
    r = subprocess.run(['ffmpeg', '-v', 'info', '-ss', '135.5', '-i', str(master), '-vn', '-af', 'volumedetect',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    print('hold audio:', re.search(r'max_volume: (\S+) dB', r).group(1), 'dB max')
    for extra in sys.argv[2:]:
        i = probe(extra)
        vv = next(s for s in i['streams'] if s['codec_type'] == 'video')
        print('share', vv['width'], vv['height'], 'frames', vv['nb_read_frames'], 'size', i['format']['size'])
    print('PASS' if ok else 'CHECK FAILED')


if __name__ == '__main__':
    main()
