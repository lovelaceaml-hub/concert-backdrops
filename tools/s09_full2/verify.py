"""Check song 09's delivered videos: exact length and frame count, no frozen or dropped frames, no black frames,
audio in sync with the recording at three hit points, and save the first and last frames for a look.

    python tools/s09_full2/verify.py out/s09_full2/<stage>.mp4 out/s09_full2/<review>.mp4 out/s09_full2/<phone>.mp4

Also checks that the signature is on every frame after the opening (its navy letters in the top left corner)
and that no stretch of the picture is frozen.

No em dash or en dash anywhere in this file.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'tools/nine_colours_minor'))
sys.path.insert(0, str(HERE))
from setup_s09 import WORK, FRAMES, FPS, TOTAL  # noqa: E402

HITS = (59.5, 148.8, 242.0)
SIG_FROM = 9.5          # the signature is fully in from 8.9 s


def signature_present(path):
    """For every frame: does the top left corner hold the signature's dark navy letters?"""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf',
                        'scale=1920:1080,crop=560:150:110:50,scale=280:75,format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    g = np.frombuffer(r.stdout, np.uint8).reshape(-1, 75, 280).astype(np.float32)
    dark = (g < g.reshape(len(g), -1).mean(axis=1)[:, None, None] - 45).mean(axis=(1, 2))
    return dark


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'format=duration,size:stream=codec_name,width,height,r_frame_rate,pix_fmt,nb_frames,'
                        'start_time,duration,bit_rate,sample_rate,channels', '-of', 'json', str(path)],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def gray_frames(path, w=96, h=54):
    """Every frame as a tiny grey picture (for frozen-frame and black-frame checks)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'scale={w}:{h},format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)


def pcm(path, start, dur, rate=8000):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{start}', '-t', f'{dur}', '-i', str(path), '-ac', '1',
                        '-ar', str(rate), '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def offset(a, b, rate=8000):
    """Lag of b against a in milliseconds (positive: b is late)."""
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    c = np.fft.irfft(np.fft.rfft(b, 2 * n) * np.conj(np.fft.rfft(a, 2 * n)))
    lag = int(np.argmax(c))
    if lag > n:
        lag -= 2 * n
    return 1000.0 * lag / rate


def check(path, expect_w):
    path = Path(path)
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_name'] == 'h264')
    a = next((s for s in info['streams'] if s['codec_name'] == 'aac'), None)
    g = gray_frames(path)
    diff = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    mean = g.mean(axis=(1, 2))
    out = dict(file=path.name, bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               width=v['width'], height=v['height'], fps=v['r_frame_rate'], pix_fmt=v['pix_fmt'],
               frames=len(g), expected_frames=FRAMES, duration=float(info['format']['duration']),
               video_start=float(v.get('start_time', 0)),
               audio_start=float(a.get('start_time', 0)) if a else None,
               audio_rate=a.get('sample_rate') if a else None, audio_bitrate=a.get('bit_rate') if a else None,
               identical_neighbours=int((diff < 0.02).sum()), smallest_change=float(diff.min()),
               largest_jump=float(diff.max()), largest_jump_at_s=float((np.argmax(diff) + 1) / FPS),
               darkest_frame_mean=float(mean.min()), darkest_at_s=float(np.argmin(mean) / FPS),
               black_frames=int((mean < 16).sum()), brightest_frame_mean=float(mean.max()),
               brightest_at_s=float(np.argmax(mean) / FPS))
    # frozen: the longest run of frames that hardly change (a backdrop must never stop living)
    still = diff < 0.05
    run = best = 0
    for x in still:
        run = run + 1 if x else 0
        best = max(best, run)
    out['longest_frozen_run_frames'] = int(best)
    sync_ok = True
    if a:
        ref = WORK / 's09.mp3'
        out['sync_ms'] = {f'{h:.1f}': round(offset(pcm(ref, h - 1.5, 3.0), pcm(path, h - 1.5, 3.0)), 2)
                          for h in HITS}
        out['tail_rms_db'] = float(20 * np.log10(np.sqrt(np.mean(pcm(path, TOTAL - 10.0, 9.5) ** 2)) + 1e-12))
        sync_ok = all(abs(x) <= 1000.0 / FPS for x in out['sync_ms'].values())
    if expect_w == 1920:
        dark = signature_present(path)
        k = int(SIG_FROM * FPS)
        out['signature_min_ink_after_opening'] = float(dark[k:].min())
        out['signature_missing_frames'] = int((dark[k:] < 0.01).sum())
    out['ok'] = bool(out['frames'] == FRAMES and abs(out['duration'] - TOTAL) < 0.05 and v['width'] == expect_w
                     and out['identical_neighbours'] == 0 and out['black_frames'] == 0 and sync_ok
                     and out['longest_frozen_run_frames'] < FPS and out.get('signature_missing_frames', 0) == 0)
    stem = path.with_suffix('')
    for label, t in (('first', 0.0), ('last', TOTAL - 1.0 / FPS)):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t}', '-i', str(path), '-frames:v', '1',
                        f'{stem} {label} frame.jpg'], check=True)
    return out


if __name__ == '__main__':
    results = [check(p, 1280 if '720p' in p else 1920) for p in sys.argv[1:]]
    print(json.dumps(results, indent=2))
    (WORK / 'verify.json').write_text(json.dumps(results, indent=2) + '\n')
