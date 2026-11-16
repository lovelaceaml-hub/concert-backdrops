"""Deliver one clean native 4K master, with the approved audio stream copied.

No bitrate cap or smaller viewing copy is applied. The owner requested only
the highest quality version. CRF 12 preserves fine detail from lossless RGB.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/nine_colours_quality'
WORK = ROOT / 'work/nine_colours_quality'
AUDIO = ROOT / 'out/nine_colours_revision3/Film-10-Nine-Colours-Revision-3-1080p60.mp4'


def run():
    listing = WORK / 'lossless-parts.txt'
    if not listing.exists():
        raise SystemExit('Run tools/nine_colours_minor/quality.py --all first.')
    name = 'Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4'
    dest = OUT / name
    temp = dest.with_suffix('.partial.mp4')
    cmd = ['ffmpeg', '-hide_banner', '-y', '-filter_threads', '2',
           '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(AUDIO),
           '-map', '0:v:0', '-map', '1:a:0']
    cmd += ['-vf', 'settb=1/60,setpts=N,scale=out_color_matrix=bt709:out_range=tv',
            '-c:v', 'libx265', '-preset', 'medium', '-crf', '12',
            '-pix_fmt', 'yuv420p10le', '-tag:v', 'hvc1', '-x265-params',
            'pools=3:frame-threads=2:keyint=120:min-keyint=60:log-level=error']
    cmd += ['-r', '60', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-colorspace', 'bt709', '-color_range', 'tv', '-c:a', 'copy',
            '-t', '66', '-movflags', '+faststart', str(temp)]
    with (WORK / 'encode-4K.log').open('w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
    info = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-show_streams',
        '-show_format', '-of', 'json', str(temp)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    expected = (3840, 2160)
    if (int(video['nb_read_frames']) != 3960 or
            video['avg_frame_rate'] != '60/1' or
            (video['width'], video['height']) != expected):
        raise RuntimeError('Delivery geometry or timing validation failed')
    temp.replace(dest)
    with dest.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    (WORK / 'delivery-4K.json').write_text(json.dumps(
        dict(file=name, sha256=digest, size=dest.stat().st_size,
             command=cmd, probe=info), indent=2) + '\n')
    print(dest, flush=True)


if __name__ == '__main__':
    run()
