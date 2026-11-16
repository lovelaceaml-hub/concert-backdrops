"""Opt-in clean export of the approved Revision 3, without changing its edit.

Render real 3840x2160 frames with no synthetic composite grain. Keep a lossless
RGB intermediate so final delivery codecs can be compared without rerendering.
The approved renderer, media and shared engine sources are left intact.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from prepare import ROOT, SNAPSHOT, CLAUDE, WORK, LEAD_IN

DEST = ROOT / 'out/nine_colours_quality'
CHECKS = ROOT / 'work/nine_colours_quality'
SIZE = (3840, 2160)
FRAMES = 3960
GRAIN = 'col += (n1+n2-1.0)*(1.15/255.0);'


def renderer(size=SIZE):
    from render import load
    Renderer, _ = load()
    import shaders
    if shaders.COMP_FS.count(GRAIN) != 1:
        raise RuntimeError('Pinned composite grain statement changed')
    shaders.COMP_FS = shaders.COMP_FS.replace(GRAIN, '// Clean export: no synthetic film grain.')
    return Renderer(*size)


def get_frame(r, index):
    clock = index / 60 - LEAD_IN
    return r.out.frame(clock, index - LEAD_IN * 60)


def probe(path):
    if not path.exists():
        return None
    run = subprocess.run(['ffprobe', '-v', 'error', '-count_frames',
                          '-select_streams', 'v:0', '-show_streams',
                          '-of', 'json', str(path)], capture_output=True, text=True)
    if run.returncode:
        return None
    streams = json.loads(run.stdout).get('streams', [])
    return streams[0] if streams else None


def worker(first, last, path):
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                      P3D_CACHE=str(WORK / 'p3d-cache'))
    r = renderer()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.partial.mkv')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', '3840x2160', '-r', '60', '-i', '-', '-an', '-c:v', 'libx264rgb',
           '-crf', '0', '-preset', 'ultrafast', '-threads', '1', '-g', '60', str(temp)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    started = time.process_time()
    try:
        for index in range(first, last):
            ff.stdin.write(get_frame(r, index))
            if (index - first) % 30 == 0:
                print(f'frame {index}: {time.process_time() - started:.1f} CPU s', flush=True)
    except BaseException:
        ff.kill()
        ff.wait()
        raise
    finally:
        ff.stdin.close()
    if ff.wait():
        raise RuntimeError('Lossless encoder failed')
    info = probe(temp)
    if not info or int(info['nb_read_frames']) != last - first:
        raise RuntimeError('Lossless range frame count mismatch')
    temp.replace(path)
    print(f'finished {path.name}: {last-first} frames', flush=True)


def manifest(parts):
    paths = sorted((ROOT / 'tools/nine_colours_minor').glob('*.py'))
    paths += sorted((SNAPSHOT / 'engine').rglob('*.py'))
    paths += sorted((CLAUDE / 'engine').rglob('*.py'))
    paths += sorted((ROOT / 'engine/p3d').glob('brand*.py'))
    paths += [ROOT / 'engine/titles.py', WORK / 'features.npz', WORK / 'score.wav']
    for directory in [ROOT / 'fonts', CLAUDE / 'assets']:
        paths += sorted(p for p in directory.rglob('*') if p.is_file())
    return dict(parts=parts, frames=FRAMES, fps=60, size=SIZE, synthetic_grain=False,
                hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in paths})


def render_all(workers, parts):
    CHECKS.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    expected = json.loads(json.dumps(manifest(parts)))
    mp = CHECKS / 'quality-manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != expected:
        raise SystemExit('Quality inputs changed. Use a fresh work/output folder.')
    mp.write_text(json.dumps(expected, indent=2) + '\n')

    def part(i):
        first, last = FRAMES * i // parts, FRAMES * (i + 1) // parts
        path = DEST / f'lossless-{i:02d}.mkv'
        info = probe(path)
        if info and int(info.get('nb_read_frames', 0)) == last - first:
            print(f'part {i}: reuse {last-first} frames', flush=True)
            return
        with (CHECKS / f'render-{i:02d}.log').open('w') as log:
            subprocess.run([sys.executable, __file__, '--range', str(first), str(last),
                            '--out', str(path)], cwd=ROOT, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        print(f'part {i}: complete {last-first} frames', flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(part, range(parts)))
    (CHECKS / 'lossless-parts.txt').write_text(''.join(
        f"file '{DEST / f'lossless-{i:02d}.mkv'}'\n" for i in range(parts)))
    print('All clean native 4K frames are complete.', flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stills', default='')
    p.add_argument('--size', choices=['1080p', '4k'], default='4k')
    p.add_argument('--outdir', type=Path, default=CHECKS / 'clean4k')
    p.add_argument('--range', type=int, nargs=2)
    p.add_argument('--out', type=Path)
    p.add_argument('--all', action='store_true')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--parts', type=int, default=12)
    a = p.parse_args()
    if not 1 <= a.workers <= 4 or not 1 <= a.parts <= 32:
        p.error('workers must be 1..4 and parts must be 1..32')
    if a.stills:
        from PIL import Image
        size = SIZE if a.size == '4k' else (1920, 1080)
        r = renderer(size)
        a.outdir.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for t in map(float, a.stills.split(',')):
            index = round(t * 60)
            data = get_frame(r, index)
            Image.frombytes('RGB', size, data).save(a.outdir / f't{t:07.2f}.png')
            hashes[str(t)] = hashlib.sha256(data).hexdigest()
            print(f'clean frame {index}', flush=True)
        (a.outdir / 'hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    elif a.range is not None and a.out:
        worker(*a.range, a.out)
    elif a.all:
        render_all(a.workers, a.parts)
    else:
        p.error('Use --stills, --range A B --out PATH, or --all')


if __name__ == '__main__':
    main()
