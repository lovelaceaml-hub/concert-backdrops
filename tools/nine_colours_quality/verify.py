"""Verify the single UHD delivery against exact RGB48 render samples."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from deliver import ROOT, OUT, WORK, AUDIO

TIMES = [0, 3, 10, 16, 21, 24.5, 29, 34.5, 39, 43, 49, 54.5, 55.8,
         56.8, 57.8, 59, 62, 65.98]


def audio_hash(path):
    return subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
        '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], text=True).strip()


def frame(path, *, index=None, seconds=None):
    cmd = ['ffmpeg', '-v', 'error', '-threads', '2', '-filter_threads', '1']
    if seconds is not None:
        cmd += ['-ss', f'{seconds:.9f}']
    cmd += ['-i', str(path)]
    if index is not None:
        cmd += ['-vf', f'select=eq(n\\,{index})']
    cmd += ['-frames:v', '1', '-pix_fmt', 'rgb48le', '-f', 'rawvideo', '-']
    data = subprocess.check_output(cmd)
    return np.frombuffer(data, '<u2').reshape(2160, 3840, 3)


def run():
    path = OUT / 'Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4'
    metadata = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_packets', '-show_streams',
        '-show_format', '-of', 'json', str(path)]))
    video = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in metadata['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height']) == (3840, 2160)
    assert video['nb_read_packets'] == '3960'
    assert video['nb_frames'] == '3960'
    assert video['avg_frame_rate'] == '60/1'
    assert video['pix_fmt'] == 'yuv420p10le'
    assert video['codec_tag_string'] == 'hvc1'
    assert abs(float(video['duration']) - 66) < .001
    assert abs(float(audio['duration']) - 66) < .001
    timestamps = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_packets', '-show_entries', 'packet=pts_time',
        '-of', 'json', str(path)]))
    # Packets arrive in decode order because of B frames. Their sorted PTS
    # gives the presentation cadence; the full decode below checks every frame.
    times = np.sort([float(f['pts_time']) for f in timestamps['packets']])
    assert len(times) == 3960
    timing_error = float(np.max(np.abs(times - np.arange(3960) / 60)))
    assert timing_error < .000002
    same_audio = audio_hash(path) == audio_hash(AUDIO)
    assert same_audio, 'Approved compressed audio packets changed'

    data = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-filter_threads', '1',
        '-i', str(path), '-an', '-vf', 'scale=160:90', '-pix_fmt', 'gray',
        '-f', 'rawvideo', '-'])
    small = np.frombuffer(data, np.uint8).reshape(-1, 90, 160).astype(np.int16)
    assert len(small) == 3960, 'Decoded frame count mismatch'
    delta = np.abs(np.diff(small, axis=0)).mean(axis=(1, 2))
    duplicates = int(np.count_nonzero(delta == 0))
    assert duplicates == 0, 'Repeated frames found'

    fresh_hashes = json.loads((WORK / 'clean4k' / 'hashes.json').read_text())
    samples = []
    sheet = Image.new('RGB', (1920, 6 * 385))
    draw = ImageDraw.Draw(sheet)
    for j, t in enumerate(TIMES):
        index = round(t * 60)
        raw = np.load(WORK / 'source-frames' / f'frame-{index:06d}.npz')['rgb']
        encoded = frame(path, seconds=index/60)
        diff = (encoded.astype(np.float32) - raw.astype(np.float32)) / 257
        mse = float(np.mean(diff * diff))
        psnr = float(10 * np.log10(255 * 255 / mse)) if mse else None
        samples.append(dict(time=index/60, rgb_psnr_db=psnr,
                            mean_absolute_channel_error=float(np.mean(np.abs(diff)))))
        print(samples[-1], flush=True)
        preview = np.rint(encoded.astype(np.float32) / 257).astype(np.uint8)
        pic = Image.fromarray(preview).resize((640, 360), Image.Resampling.LANCZOS)
        x, y = (j % 3) * 640, (j // 3) * 385
        sheet.paste(pic, (x, y + 25))
        draw.text((x + 8, y + 5), f'{index/60:.3f} s', fill='white')
        if t in [3, 16, 43, 56.8, 62]:
            Image.fromarray(preview).save(WORK / f'encoded-{t}.png')
            assert hashlib.sha256(raw.tobytes()).hexdigest() == fresh_hashes[str(float(t))], (
                f'Fresh/range source mismatch at {t}')
    sheet.save(WORK / 'full-film-review.jpg', quality=95)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    report = dict(file=path.name, size_bytes=path.stat().st_size, sha256=digest,
                  metadata=metadata, maximum_timestamp_error_seconds=timing_error,
                  consecutive_duplicate_frames=duplicates, approved_audio_identical=same_audio,
                  five_fresh_raw_samples_equal_full_render_samples=True,
                  compression_samples=samples)
    (WORK / 'final-qa.json').write_text(json.dumps(report, indent=2) + '\n')
    print('UHD delivery structural and source checks passed.', flush=True)


if __name__ == '__main__':
    run()
