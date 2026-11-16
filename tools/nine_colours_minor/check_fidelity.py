"""Compare original-engine frames and test independent render order.

The reference is the raw render at 60 fps, not the lossy 30 fps share MP4.
With additions disabled, closing-card replacement is the only intended change.
Reports and PNGs remain under work/nine_colours_minor, outside version control.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from prepare import ROOT, WORK

TIMES = [0, .5, 4, 6.5, 9, 13.5, 18, 23.5, 25.5, 30, 34, 38.5, 41.5, 44, 48.5, 51]
ORDER_TIMES = [0, 2.5, 6, 11, 19, 27.5, 40.5, 50.5, 53, 54.5, 54.75, 55, 61.98]


def worker(mode, output):
    from render import load
    Renderer, film = load(mode == 'baseline')
    renderer = Renderer()
    if mode == 'stripped':
        # Remove only added scene members. All original members remain in order.
        for name in ['world', 'logo', 'symbol ring']:
            renderer.p3d.scene.remove('addition '+name)
        for word in film.WORDS:
            renderer.p3d.scene.remove('addition symbol '+word.name)
        renderer.cards.overlay = lambda t: False
    times = TIMES if mode in ('baseline', 'stripped') else ORDER_TIMES
    if mode == 'reverse':
        times = times[::-1]
    hashes = {}
    for t in times:
        clock = t if mode in ('baseline', 'stripped') else t-2
        data = renderer.out.frame(clock, round(clock*60))
        hashes[str(t)] = hashlib.sha256(data).hexdigest()
        print(mode, t, hashes[str(t)], flush=True)
    output.write_text(json.dumps(hashes, indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=['baseline', 'stripped', 'forward', 'reverse'])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.output)
        return
    results = {}
    for mode in ['baseline', 'stripped', 'forward', 'reverse']:
        output = WORK/f'fidelity-{mode}.json'
        subprocess.run([sys.executable, __file__, '--worker', mode, '--output', str(output)],
                       cwd=ROOT, check=True)
        results[mode] = json.loads(output.read_text())
    report = dict(
        original_engine_raw_pixels_identical=results['baseline'] == results['stripped'],
        original_engine_times=TIMES,
        forward_reverse_raw_pixels_identical=results['forward'] == results['reverse'],
        order_times=ORDER_TIMES,
        resolution='1920x1080', fps=60,
        scope='Original engine at original times; additions disabled for baseline comparison. '
              'Original closing card intentionally replaced after original time 51.4 s.')
    (WORK/'fidelity-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    if not (report['original_engine_raw_pixels_identical'] and
            report['forward_reverse_raw_pixels_identical']):
        raise SystemExit('Fidelity check failed')


if __name__ == '__main__':
    main()
