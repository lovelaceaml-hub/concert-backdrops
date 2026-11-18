"""Song 07 v2: layout checks over the whole stage video, no rendering needed.  No em dash or en dash here.

    python tools/s07_full2/check_layout.py

Every 0.25 s of LIVE time: every lit arch star outside the signature box; every word box at least 40 px
from the signature and above the calm bottom third; only one expression readable at a time; reading times
(live seconds) of every expression and fragment.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402
import clock  # noqa: E402


def main():
    render.load()
    from cards07 import signature_box
    import songs.s07_full2_song as S
    PW = S.PW
    sx0, sy0, sx1, sy1 = signature_box()
    W, H = 1920.0, 1080.0
    problems = []
    worst_star = 1e9
    worst_word = 1e9
    for tl in np.arange(8.0, clock.TOTAL, 0.25):
        t = clock.ref(tl)
        cam = PW._cam_at(S._LAYOUT, t)
        lit = S._arch_lit(t)
        P = S.arch_homes(t)
        xy, z = cam.project(P)
        for i in range(9):
            if lit[i][0] <= 0.01 or z[i] <= 0:
                continue
            px, py = xy[i, 0] * W, (1.0 - xy[i, 1]) * H
            dx = max(sx0 - px, 0.0, px - sx1)
            dy = max(sy0 - py, 0.0, py - sy1)
            d = float(np.hypot(dx, dy))
            worst_star = min(worst_star, d)
            if d < 12.0:
                problems.append(f"{tl:7.2f}: arch star {i + 1} inside the signature (at {px:.0f},{py:.0f})")
        reading = []
        for w in S.WORDS:
            if not (w.t_in <= t <= w.t_out):
                continue
            x0, x1, y0, y1, front, *_ = PW.screen_box(w, cam, t)
            if not front:
                continue
            bx0, bx1, by0, by1 = x0 * W, x1 * W, (1 - y1) * H, (1 - y0) * H
            dx = max(sx0 - bx1, bx0 - sx1, 0.0)
            dy = max(sy0 - by1, by0 - sy1, 0.0)
            gap = max(dx, dy)
            worst_word = min(worst_word, gap)
            if gap < 40.0:
                problems.append(f"{tl:7.2f}: word {w.name} only {gap:.0f} px from the signature")
            if y0 < S.BOTTOM and w.t_read0 <= t <= w.t_read1:
                problems.append(f"{tl:7.2f}: word {w.name} reaches the bottom third (y0 {y0:.2f})")
            if w.t_read0 <= t <= w.t_read1 and getattr(w, "expr", None):
                reading.append(w.name)
        if len(reading) > 1:
            problems.append(f"{tl:7.2f}: two expressions read at once {reading}")
    for w in S.WORDS:
        r0, r1 = clock.live(w.t_read0), clock.live(w.t_read1)
        print(f"{w.name:14s} arrives {clock.live(w.t_in):7.2f}  reads {r0:7.2f} to {r1:7.2f} ({r1 - r0:4.1f} s)  "
              f"gone {clock.live(w.t_out):7.2f}")
    print(f"closest lit arch star to the signature: {worst_star:.0f} px; closest word: {worst_word:.0f} px")
    print("\n".join(problems[:40]) if problems else "layout: no problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
