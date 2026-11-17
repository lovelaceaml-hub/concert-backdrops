"""Join native 4K ranges and approved audio without another lossy encode.

No bitrate cap or smaller viewing copy is applied. The owner requested only
the highest quality version. The range renderer encodes CRF 12 directly from
RGB48 frames, with the scene kept in floating point until that handoff.
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
    listing = WORK / 'parts.txt'
    if not listing.exists():
        raise SystemExit('Run tools/nine_colours_minor/quality.py --all first.')
    name = 'Film-10-Nine-Colours-Revision-3-HQ-4K60.mp4'
    dest = OUT / name
    temp = dest.with_suffix('.partial.mp4')
    cmd = ['ffmpeg', '-hide_banner', '-y',
           '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(AUDIO),
           '-map', '0:v:0', '-map', '1:a:0']
    # x265 retained the matrix but omitted primaries/transfer in its VUI.
    # Set those tags explicitly without touching encoded picture samples.
    cmd += ['-c:v', 'copy', '-bsf:v',
            'hevc_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0',
            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
            '-color_range', 'tv', '-tag:v', 'hvc1', '-c:a', 'copy',
            '-t', '66', '-movflags', '+faststart', str(temp)]
    with (WORK / 'encode-4K.log').open('w') as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
    info = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams',
        '-show_format', '-of', 'json', str(temp)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    expected = (3840, 2160)
    if (int(video['nb_frames']) != 3960 or
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
