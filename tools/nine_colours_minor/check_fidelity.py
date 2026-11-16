"""Compare original-engine frames and test independent render order.

The reference is the raw render at 60 fps, not the lossy 30 fps share MP4.
Compare only untouched chapters; opening, Respect and finale are intentionally revised.
Reports and PNGs remain under work/nine_colours_revision2, outside version control.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from prepare import ROOT, WORK, LEAD_IN

TIMES = [4, 6.5, 9, 13.5, 18, 23.5, 25.5, 30, 32, 41.5, 44, 48.0]
ORDER_TIMES = [0, 6.3, 7.2, 8, 18, 40, 42, 45.9, 46.3, 54.5, 55.5, 56.8, 57.7, 58.5, 59, 65.98]


def worker(mode, output):
    from render import load
    Renderer, film = load(mode == 'baseline')
    renderer = Renderer()
    if mode == 'stripped':
        # Remove additions; retained original members keep their original draw order.
        for name in ['world', 'logo', 'symbol ring', 'listening light']:
            renderer.p3d.scene.remove('addition '+name)
        for word in film.WORDS:
            renderer.p3d.scene.remove('addition symbol '+word.name)
        renderer.cards.overlay = lambda t: False
    times = TIMES if mode in ('baseline', 'stripped') else ORDER_TIMES
    if mode == 'reverse':
        times = times[::-1]
    hashes = {}
    for t in times:
        clock = t if mode in ('baseline', 'stripped') else t-LEAD_IN
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
              'Opening, Respect and finale excluded by design; the finale transition starts at original 48.37 s.')
    (WORK/'fidelity-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    if not (report['original_engine_raw_pixels_identical'] and
            report['forward_reverse_raw_pixels_identical']):
        raise SystemExit('Fidelity check failed')


if __name__ == '__main__':
    main()
