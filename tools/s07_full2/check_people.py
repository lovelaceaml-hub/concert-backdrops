"""Song 07 v2: where every person's feet land in the picture, every 0.25 s of live time (no rendering).
Reports any shown person whose lowest point (toes or ankles) falls into the calm bottom third.

    python tools/s07_full2/check_people.py

No em dash or en dash here.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402
import clock  # noqa: E402

PARTS = ("toe.L", "toe.R", "ankle.L", "ankle.R")


def main():
    render.load()
    import songs.s07_full2_song as S
    PW = S.PW
    bodies = S._bodies()
    line = 1.0 / 3.0
    worst = {}
    for tl in np.arange(0.0, clock.TOTAL, 0.25):
        t = clock.ref(tl)
        cam = PW._cam_at(S._LAYOUT, t)
        for name, b in bodies.items():
            if b.show is not None and not (b.show[0] <= t <= b.show[1]):
                continue
            P = np.array([np.asarray(b.where(t, p), np.float64) for p in PARTS])
            xy, z = cam.project(P)
            ok = (z > 0) & (xy[:, 0] > -0.02) & (xy[:, 0] < 1.02)
            if not ok.any():
                continue
            y = float(xy[ok, 1].min())          # 0 at the bottom of the frame
            if y < line:
                w = worst.setdefault(name, [tl, tl, y])
                w[1] = tl
                w[2] = min(w[2], y)
    for name, (a, b, y) in worst.items():
        print(f"{name:10s} feet in the bottom third from {a:7.2f} to {b:7.2f} s (lowest {y:.3f} of the height)")
    print("people: no problems" if not worst else f"{len(worst)} people dip into the bottom third")
    return 1 if worst else 0


if __name__ == "__main__":
    raise SystemExit(main())
