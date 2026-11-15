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
    p.add_argument('--stages', action='store_true', help='Synchronize GL around major stages')
    a = p.parse_args()
    if a.frames < 1:
        p.error('--frames must be positive')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
    import render
    r = render.Renderer()
    stage_totals = {}
    if a.stages:
        def instrument(obj, name, label):
            original = getattr(obj, name)
            def timed(*args, **kwargs):
                r.ctx.finish()
                start = time.process_time()
                result = original(*args, **kwargs)
                r.ctx.finish()
                stage_totals[label] = stage_totals.get(label, 0.0) + time.process_time() - start
                return result
            setattr(obj, name, timed)
        if r.p3d:
            for name in ('_batches', '_mask_pass', '_draw_sets', 'background'):
                instrument(r.p3d, name, 'p3d.' + name)
        instrument(r, 'text_plan', 'text_plan')
        if r.titles:
            for name in ('protect', 'overlay'):
                instrument(r.titles, name, 'titles.' + name)
    rows = []
    profile = cProfile.Profile(timer=time.process_time) if a.profile else None
    for t in map(float, a.moments.split(',')):
        first = round(t * render.S.FPS)
        r.out.frame((first - 1) / render.S.FPS, first - 1)
        r.ctx.finish()
        samples = []
        stage_totals.clear()
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
        if a.stages:
            row["stages_cpu_seconds_per_frame"] = {k: v / a.frames for k, v in stage_totals.items()}
        rows.append(row)
        print(json.dumps(row), flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rows, indent=2) + '\n')
    if profile:
        a.profile.parent.mkdir(parents=True, exist_ok=True)
        profile.dump_stats(str(a.profile))


if __name__ == '__main__':
    main()
