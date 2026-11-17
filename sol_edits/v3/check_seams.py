"""Compare actual split-boundary raw hashes with one continuous sampling pass."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sol_edits.v3.render import S,make_renderer,frame


def main():
    out=ROOT/'work/sol3/nine-colors'
    expected={}
    for path in sorted(out.glob('part-*.hashes.json')):
        expected.update(json.loads(path.read_text()))
    step=S.NFRAMES//5
    indices=[i for cut in range(step,S.NFRAMES,step) for i in range(cut-2,cut+2)]
    r=make_renderer(S.W,S.H)
    report=[]
    for i in indices:
        actual=hashlib.sha256(frame(r,i)).hexdigest()
        ok=actual==expected[str(i)]
        report.append(dict(frame=i,match=ok,sha256=actual))
        print(i,'match' if ok else 'MISMATCH',flush=True)
    (out/'seam-check.json').write_text(json.dumps(report,indent=2)+'\n')
    assert all(q['match'] for q in report),'Split render differs at a boundary'

if __name__=='__main__': main()
