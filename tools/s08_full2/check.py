"""Checks on song 08's finished version 2 files (nothing here goes in git but this script).

    python tools/s08_full2/check.py <final dir> <recording.mp3>

Length and frame count of the three files, frame rate, black and frozen stretches, the first and last frames,
the signature on every frame after the opening (sampled 4 times a second), the brightest frame (no white-outs),
the calm bottom third, and sync: the three hits measured on the review file's own sound against the picture's
own events (the star 9 flare is not a hit; the hits are 43.20 s, 109.16 s and 202.28 s). No em dash or en dash.
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np

TOTAL, FPS = 225.0, 60
HITS = (43.20, 109.16, 202.28)


def probe(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                          'stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt:format=duration,size',
                          '-of', 'json', f], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def frames(f, fps, w=480, h=270, crop=None, t0=0.0, dur=None):
    vf = (f'crop={crop},' if crop else '') + f'fps={fps},scale={w}:{h}'
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', f] + (['-t', str(dur)] if dur else []) + \
          ['-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def main():
    d, rec = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(d, '08 *.mp4')))
    stage = [f for f in files if 'stage' in f][0]
    review = [f for f in files if 'review' in f][0]
    for f in files:
        p = probe(f)
        v = [s for s in p['streams'] if s['codec_type'] == 'video'][0]
        a = [s for s in p['streams'] if s['codec_type'] == 'audio']
        print(os.path.basename(f), f"{float(p['format']['duration']):.3f} s, {int(p['format']['size']) / 1e6:.1f} MB,",
              v['codec_name'], f"{v['width']}x{v['height']}", v['r_frame_rate'], v['pix_fmt'],
              'frames', v['nb_read_frames'], 'audio ' + a[0]['codec_name'] if a else 'silent')
    for name, filt in (('black', 'blackdetect=d=0.1:pix_th=0.06'), ('frozen', 'freezedetect=n=-70dB:d=0.5')):
        out = subprocess.run(['ffmpeg', '-v', 'info', '-i', stage, '-vf', filt, '-an', '-f', 'null', '-'],
                             capture_output=True, text=True).stderr
        hits = [ln.strip() for ln in out.splitlines() if (name + '_start') in ln or 'freeze_start' in ln]
        print(f'{name} stretches:', len(hits), hits[:4])
    # consecutive identical frames (a repeated frame) across the whole stage file at quarter size
    g = frames(stage, FPS, 320, 180)
    diff = np.array([np.abs(g[i + 1].astype(np.int16) - g[i]).mean() for i in range(len(g) - 1)])
    print(f'frames read {len(g)}; repeated frames (mean difference < 0.01): {int((diff < 0.01).sum())}; '
          f'largest jump {diff.max():.1f} at {np.argmax(diff) / FPS:.2f} s')
    print(f'first frame mean {g[0].mean():.0f}, last frame mean {g[-1].mean():.0f} (never black)')
    full = frames(stage, 4, 480, 270).astype(np.float32)
    print(f'brightest sampled frame mean {full.mean(axis=(1, 2)).max():.0f} / 255 at '
          f'{np.argmax(full.mean(axis=(1, 2))) / 4:.2f} s; share of pixels above 245 at most '
          f'{(full > 245).mean(axis=(1, 2)).max():.4f}')
    bt = full[:, 180:, :]
    print(f'bottom third: mean {bt.mean():.0f}, 99th percentile of frames 99th percentile '
          f'{np.percentile(np.percentile(bt, 99, axis=(1, 2)), 99):.0f}')
    # the signature: the date line DEC 6 . 4:30 PM, top left (1080p box x 190..560, y 136..176)
    sig = frames(stage, 4, 370, 40, crop='370:40:190:136').astype(np.float32)
    lit = (sig > 170).mean(axis=(1, 2))
    after = lit[int(9.0 * 4):]
    print(f'signature date line: lit share after 0:09 min {after.min():.3f} median {np.median(after):.3f} '
          f'(frames below half the median: {int((after < 0.5 * np.median(after)).sum())})')
    # sync: the review file's own sound at the three hits
    import soundfile as sf
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', review, '-ac', '1', '-ar', '22050', '/tmp/s08_review.wav'],
                   check=True)
    x, sr = sf.read('/tmp/s08_review.wav')
    h = int(sr * 0.02)
    e = np.array([np.sqrt(np.mean(x[i * h:(i + 1) * h] ** 2)) + 1e-9 for i in range(len(x) // h)])
    db = 20 * np.log10(e)
    for c in HITS:
        i0, i1 = int((c - 1.0) / .02), int((c + 1.0) / .02)
        jump = db[i0 + 5:i1] - np.array([db[k - 5:k].mean() for k in range(i0 + 5, i1)])
        k = int(np.argmax(jump))
        print(f'hit planned {c:.2f} s: heard in the review file at {(i0 + 5 + k) * .02:.2f} s '
              f'(picture frame {round(c * FPS)})')
    # the picture's own response at the final chord: centre of the sky brightens as the curtain opens
    ctr = frames(stage, 10, 64, 36, crop='480:400:720:80', t0=200.0, dur=6.0).astype(np.float32).mean(axis=(1, 2))
    print('centre sky brightness 200 to 206 s every 0.5 s:', ' '.join(f'{v:.0f}' for v in ctr[::5]))


if __name__ == '__main__':
    main()
