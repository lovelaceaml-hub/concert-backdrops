"""Join song 10's rendered parts (version 2), make the three delivery files and check them.

    python tools/s10_full2/finish.py

Stage: silent, H.264 CRF 16, yuv420p, faststart, 1920x1080, 60 fps, 226.0 s (live length 211.0 s + 15 s hold).
Review: the same picture with the reference conformed to 211.0 s (work/s10_full2/score.wav), AAC 320k, CRF 20.
Phone: 1280x720, 60 fps, with music, under 25 MB (two pass).
Checks: exact frame count and length, first and last frames, no black frames, no repeated or frozen stretches,
the signature present on every frame after the opening, audio length, and three hits against the measured
times. Prints a report; writes out/s10_full2/CHECKS.txt.
No em dash or en dash anywhere in this file.
"""
import glob
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/s10_full2'
WORK = ROOT / 'work/s10_full2'
NF, FPS = 13560, 60
NAME = '10 Our Mother Saves the World - Backdrop v2'
K = 211.0 / 211.605333               # reference clock to stage video clock
HITS = [round(h * K, 2) for h in (25.33, 52.04, 205.11)]
SIG_FROM = 10.0                      # the signature is whole from here to the last frame


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
    stage = OUT / f'{NAME} - stage 1080p60.mp4'
    review = OUT / f'{NAME} - review 1080p60.mp4'
    phone = OUT / f'{NAME} - phone 720p60.mp4'
    color = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    dur = f'{NF / FPS:.6f}'
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-map', '0:v',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-g', '120']
        + color + ['-an', '-t', dur, '-movflags', '+faststart', str(stage)])
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(stage), '-i', str(WORK / 'score.wav'), '-map', '0:v', '-map', '1:a',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-g', '120'] + color
        + ['-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', dur, '-movflags', '+faststart', str(review)])
    vbr = int((22.5 * 8 * 1024 * 1024) / (NF / FPS) - 128000)
    for ps in (1, 2):
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(stage), '-i', str(WORK / 'score.wav'), '-map', '0:v',
             '-map', '1:a', '-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow',
             '-b:v', str(vbr), '-pass', str(ps), '-passlogfile', str(OUT / 'pass'), '-pix_fmt', 'yuv420p',
             '-g', '120'] + color
            + (['-an', '-f', 'mp4', '/dev/null'] if ps == 1 else
               ['-c:a', 'aac', '-b:a', '128k', '-t', dur, '-movflags', '+faststart', str(phone)]))
    master = review
    rep = {}
    for f in (stage, review, phone):
        info = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                               'stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames,pix_fmt:'
                               'format=duration,size', '-of', 'json', str(f)]))
        rep[f.name] = dict(info=info, frames=frames_of(f), sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                           mb=f.stat().st_size / 1048576)
    # black and frozen frames on a small grey copy of the master
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(stage), '-vf', 'scale=64:36', '-pix_fmt', 'gray',
                          '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    mean = g.mean(axis=(1, 2))
    diff = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    rep['frames_decoded'] = int(len(g))
    rep['darkest_frame'] = dict(index=int(mean.argmin()), mean=float(mean.min()))
    rep['black_frames'] = int((mean < 6).sum())
    rep['identical_neighbours'] = int((diff < 0.02).sum())
    rep['identical_neighbour_times'] = [round(float(i) / FPS, 2) for i in np.nonzero(diff < 0.02)[0][:40]]
    run_len, longest = 0, 0
    for d in diff:
        run_len = run_len + 1 if d < 0.02 else 0
        longest = max(longest, run_len)
    rep['longest_frozen_seconds'] = round(longest / FPS, 3)
    rep['first_frame_mean'], rep['last_frame_mean'] = float(mean[0]), float(mean[-1])
    # the signature (top left) on every frame after the opening: its brightest pixel stays bright
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(stage), '-vf', 'crop=560:170:60:40,scale=140:42',
                          '-pix_fmt', 'gray', '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
    sg = np.frombuffer(raw, np.uint8).reshape(-1, 42, 140)
    peak = sg.reshape(len(sg), -1).max(axis=1)[int(SIG_FROM * FPS):]
    rep['signature_min_peak_after_opening'] = int(peak.min())
    rep['signature_frames_dim'] = int((peak < 170).sum())
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
