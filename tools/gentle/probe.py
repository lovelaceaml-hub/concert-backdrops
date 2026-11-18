"""Compare raw 1080p frames in sequential and shuffled fresh processes.

This is a creative-film regression check, not the engine performance suite.
Hashes and reports are private outputs under work/gentle/order/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time

from render import ROOT, load

FRAMES=[929,930,931,1859,1860,1861,2039,2040,2041,2279,2280,2281,2789,2790,2791]


def worker(order, destination):
    load()
    renderer=runpy.run_path(str(ROOT/'engine/render.py'))['Renderer'](1920,1080)
    rows={}
    for frame in order:
        start=time.process_time()
        data=renderer.out.frame(frame/60,frame)
        rows[frame]=dict(sha256=hashlib.sha256(data).hexdigest(),
                         cpu_seconds=time.process_time()-start)
        print(f'probe frame {frame}: {rows[frame]["cpu_seconds"]:.3f} CPU s',flush=True)
    destination.write_text(json.dumps(rows,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',choices=('sequential','shuffled'))
    args=parser.parse_args()
    folder=ROOT/'work/gentle/order'
    folder.mkdir(parents=True,exist_ok=True)
    if args.worker:
        order=FRAMES if args.worker=='sequential' else FRAMES[::2][::-1]+FRAMES[1::2]
        worker(order,folder/f'{args.worker}.json')
        return
    sources=sorted(Path(__file__).parent.glob('*.py'))+[ROOT/'work/gentle/features.npz']
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for name in ('sequential','shuffled'):
        subprocess.run([sys.executable,__file__,'--worker',name],check=True,cwd=ROOT)
        if any(hashlib.sha256(p.read_bytes()).hexdigest()!=hashes[p.name] for p in sources):
            raise SystemExit('Source changed during the probe. Rerun against fixed inputs.')
    a,b=[json.loads((folder/f'{name}.json').read_text()) for name in ('sequential','shuffled')]
    same=all(a[str(f)]['sha256']==b[str(f)]['sha256'] for f in FRAMES)
    report=dict(pixel_identical=same,frames=FRAMES,sources=hashes,sequential=a,shuffled=b)
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not same:
        raise SystemExit('Raw frame order mismatch')
    print(f'All {len(FRAMES)} raw frames are pixel identical across fresh-process render orders.')


if __name__=='__main__':
    main()
