"""Test raw-frame render order for the revised creative film.

The typography, Respect and finale are intentionally revised. This is an
order-independence check, not pixel equality to a previous creative version.
Reports remain under work/nine_colours_revision3, outside version control.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from prepare import ROOT, WORK, LEAD_IN

ORDER_TIMES = [0,6.3,7.2,8,10,16,21,24.5,29,34.5,38,40,41.5,43,44.5,46.3,
               49,54.5,54.75,55.46,55.48,55.8,56.4,57.2,57.8,58.4,59,65.98]


def worker(mode, output):
    from render import load
    Renderer, film = load()
    renderer = Renderer()
    times = ORDER_TIMES
    if mode == 'reverse':
        times = times[::-1]
    hashes = {}
    for t in times:
        clock = t-LEAD_IN
        data = renderer.out.frame(clock, round(clock*60))
        hashes[str(t)] = hashlib.sha256(data).hexdigest()
        print(mode, t, hashes[str(t)], flush=True)
    output.write_text(json.dumps(hashes, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=['forward', 'reverse'])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.output)
        return
    results = {}
    for mode in ['forward', 'reverse']:
        output = WORK/f'fidelity-{mode}.json'
        subprocess.run([sys.executable, __file__, '--worker', mode, '--output', str(output)],
                       cwd=ROOT, check=True)
        results[mode] = json.loads(output.read_text())
    report = dict(
        forward_reverse_raw_pixels_identical=results['forward'] == results['reverse'],
        order_times=ORDER_TIMES,
        resolution='1920x1080', fps=60,
        scope='Revised creative output in fresh forward and reverse processes. '
              'Intentional picture changes are not tested for equality to a prior film.')
    (WORK/'fidelity-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    if not report['forward_reverse_raw_pixels_identical']:
        raise SystemExit('Fidelity check failed')


if __name__ == '__main__':
    main()
