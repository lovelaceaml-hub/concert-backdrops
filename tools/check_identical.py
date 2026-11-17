"""Render fixed moments and compare RGB pixels with saved reference stills."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--song', required=True)
    parser.add_argument('--moments', required=True, help='Comma-separated seconds')
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--allow-tolerance', action='store_true',
                        help='Allow at most 2 levels on strictly fewer than 0.1 percent of pixels')
    args = parser.parse_args()
    moments = [float(t) for t in args.moments.split(',')]
    names = [f't{t:07.2f}.png' for t in moments]
    if len(set(names)) != len(names):
        parser.error('Moments collide at the renderer filename precision')
    for name in names:
        if not (args.reference / name).is_file():
            parser.error(f'Missing reference: {args.reference / name}')
    root = Path(__file__).resolve().parents[1]
    failed = False
    with tempfile.TemporaryDirectory(prefix='render-identical-') as tmp:
        subprocess.run([sys.executable, 'render.py', '--stills', args.moments,
                        '--outdir', tmp], cwd=root / 'engine', check=True,
                       env=dict(os.environ, SONG=args.song))
        for name in names:
            with Image.open(args.reference / name) as im:
                before = np.asarray(im.convert('RGB'), dtype=np.int16)
            with Image.open(Path(tmp) / name) as im:
                after = np.asarray(im.convert('RGB'), dtype=np.int16)
            if before.shape != after.shape:
                print(f'FAIL {name}: shape {before.shape} != {after.shape}')
                failed = True
                continue
            delta = np.abs(before - after)
            changed = int(np.count_nonzero(np.any(delta, axis=2)))
            fraction = changed / (before.shape[0] * before.shape[1])
            maximum = int(delta.max())
            ok = changed == 0 or (args.allow_tolerance and maximum <= 2 and fraction < .001)
            failed |= not ok
            print(f'{"PASS" if ok else "FAIL"} {name}: max={maximum}, '
                  f'changed={changed} ({fraction:.6%})', flush=True)
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
