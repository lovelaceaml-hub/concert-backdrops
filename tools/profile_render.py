"""Measure CPU seconds for advancing frames, excluding construction and seek warmup."""
import argparse
import cProfile
import json
from pathlib import Path
import sys
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--moments', default='1,8,18,30,44,52,57')
    p.add_argument('--frames', type=int, default=5)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--profile', type=Path)
    a = p.parse_args()
    if a.frames < 1:
        p.error('--frames must be positive')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
    import render
    r = render.Renderer()
    rows = []
    profile = cProfile.Profile(timer=time.process_time) if a.profile else None
    for t in map(float, a.moments.split(',')):
        first = round(t * render.S.FPS)
        r.out.frame((first - 1) / render.S.FPS, first - 1)
        r.ctx.finish()
        samples = []
        for index in range(first, first + a.frames):
            if profile:
                profile.enable()
            start = time.process_time()
            r.out.frame(index / render.S.FPS, index)
            r.ctx.finish()
            samples.append(time.process_time() - start)
            if profile:
                profile.disable()
        row = dict(t=t, cpu_seconds_per_frame=sum(samples) / len(samples), samples=samples)
        rows.append(row)
        print(json.dumps(row), flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rows, indent=2) + '\n')
    if profile:
        profile.dump_stats(str(a.profile))


if __name__ == '__main__':
    main()
