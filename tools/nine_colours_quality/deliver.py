"""Encode clean 4K render ranges once, with the approved audio stream copied.

No bitrate cap or 720p step is applied. Both deliverables use native 60 fps.
The 1080p copy is downsampled from lossless 4K RGB before its first lossy encode.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/nine_colours_quality'
WORK = ROOT / 'work/nine_colours_quality'
AUDIO = ROOT / 'out/nine_colours_revision3/Film-10-Nine-Colours-Revision-3-1080p60.mp4'


def run(profile):
    listing = WORK / 'lossless-parts.txt'
    if not listing.exists():
        raise SystemExit('Run tools/nine_colours_minor/quality.py --all first.')
    name = 'Film-10-Nine-Colours-Revision-3-HQ-' + profile + '60.mp4'
    dest = OUT / name
    temp = dest.with_suffix('.partial.mp4')
    cmd = ['ffmpeg', '-hide_banner', '-y', '-filter_threads', '2',
           '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(AUDIO),
           '-map', '0:v:0', '-map', '1:a:0']
    if profile == '4K':
        cmd += ['-vf', 'settb=1/60,setpts=N,scale=out_color_matrix=bt709:out_range=tv',
                '-c:v', 'libx265', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', 'yuv420p10le', '-tag:v', 'hvc1', '-x265-params',
                'pools=2:frame-threads=2:keyint=120:min-keyint=60:log-level=error']
    else:
        cmd += ['-vf', 'settb=1/60,setpts=N,scale=1920:1080:flags=lanczos:out_color_matrix=bt709:out_range=tv',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                '-pix_fmt', 'yuv420p', '-threads', '3', '-g', '120']
    cmd += ['-r', '60', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-colorspace', 'bt709', '-color_range', 'tv', '-c:a', 'copy',
            '-t', '66', '-movflags', '+faststart', str(temp)]
    with (WORK / f'encode-{profile}.log').open('w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
    info = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-show_streams',
        '-show_format', '-of', 'json', str(temp)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    expected = (3840, 2160) if profile == '4K' else (1920, 1080)
    if (int(video['nb_read_frames']) != 3960 or
            video['avg_frame_rate'] != '60/1' or
            (video['width'], video['height']) != expected):
        raise RuntimeError('Delivery geometry or timing validation failed')
    temp.replace(dest)
    digest = hashlib.file_digest(dest.open('rb'), 'sha256').hexdigest()
    (WORK / f'delivery-{profile}.json').write_text(json.dumps(
        dict(file=name, sha256=digest, size=dest.stat().st_size,
             command=cmd, probe=info), indent=2) + '\n')
    print(dest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('profile', choices=['4K', '1080p'])
    run(p.parse_args().profile)
