"""Suggests expression timing from the music (engine-audio, 2026-11-15).

    python tools/suggest_timing.py audio/promo/s05.mp3 -n 4
    python tools/suggest_timing.py audio/promo/s05.mp3 -n 4 --start 6 --end 46 --json

Prints the tempo, the section starts, the strong beats (downbeats), and for N expressions the suggested
form, hold, out and star times, ready to paste into a song file's PHRASES.

The reading time contract (PHASE2.md item 4) is always honoured: the words take FORM_DUR (3.75 s) to form, then
stay solid at least --solid seconds (default 6), so hold >= form + 9.75; the dissolve ends DISSOLVE (1.6 s) after
hold ("out"), and the next expression starts forming at least GAP (0.5 s) after that. Hold moments are placed on
section starts and strong beats where possible and spread evenly over the window; each form time is the first strong
beat after the previous dissolve and gap (so the words stay solid as long as possible); each star (the light is lit) is a strong beat about 3 s after hold.
Needs only numpy and ffmpeg.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
import audio_react  # noqa: E402

FORM_DUR, DISSOLVE, GAP, FLY = 3.75, 1.6, 0.5, 3.0


def plan(a, n, start, end, solid=6.0, spacing_weight=30.0):
    """Chooses n hold times on the music. Returns a list of dicts or raises ValueError when they cannot fit."""
    beats = np.array(a.beats())
    downs = set(np.round(a.downbeats(), 3))
    strong = set(np.round(a.strong_beats(), 3))
    secs = np.array(a.section_starts())
    lead = FORM_DUR + solid                      # form to hold
    tail = DISSOLVE + GAP                        # hold to the next form
    if n * lead + (n - 1) * tail + DISSOLVE > end - start + 1e-6:
        raise ValueError(f"{n} expressions need at least {n * lead + (n - 1) * tail + DISSOLVE:.1f} s, "
                         f"the window {start:g} to {end:g} s has {end - start:.1f} s")
    # candidate hold times: every beat and section start in range, plus a fine grid so a plan always exists
    cand = np.unique(np.round(np.concatenate([beats, secs, np.arange(start, end, 0.25)]), 3))
    cand = cand[(cand >= start + lead - 1e-6) & (cand <= end - DISSOLVE + 1e-6)]
    if len(cand) == 0:
        raise ValueError("no room for a hold time in the window")

    def score(h):
        s = 0.0
        if np.any(np.abs(secs - h) < 0.05):
            s += 1.5
        r = round(float(h), 3)
        if r in strong:
            s += 0.9
        elif r in downs:
            s += 0.7
        elif np.any(np.abs(beats - h) < 0.02):
            s += 0.3
        return s

    sc = np.array([score(h) for h in cand])
    span = (end - DISSOLVE - start - (n - 1) * tail) / n   # even form-to-hold time per expression
    C = len(cand)
    best = np.full((n, C), -np.inf)
    back = np.full((n, C), -1)
    best[0] = sc - spacing_weight * ((cand - start - span) / span) ** 2
    for i in range(1, n):
        for c in range(C):
            prev = cand <= cand[c] - lead - tail + 1e-6
            if not prev.any():
                continue
            v = best[i - 1][prev] - spacing_weight * ((cand[c] - cand[prev] - tail - span) / span) ** 2
            k = int(np.argmax(v))
            best[i, c] = sc[c] + v[k]
            back[i, c] = np.nonzero(prev)[0][k]
    fin = best[n - 1] - spacing_weight * ((end - DISSOLVE - cand) / span) ** 2
    c = int(np.argmax(fin))
    if not np.isfinite(fin[c]):
        raise ValueError("no plan fits")
    holds = []
    for i in range(n - 1, -1, -1):
        holds.append(float(cand[c]))
        c = back[i, c]
    holds = holds[::-1]
    out, prev_out = [], start - GAP
    for h in holds:
        lo, hi = prev_out + GAP, h - lead
        # form as early as the gap allows (the longest reading time), on a strong beat if one is close
        win = lambda x: x[(x >= lo - 1e-6) & (x <= min(hi, lo + 2.0) + 1e-6)]
        fs, fb = win(np.array(sorted(strong | downs))), win(beats)
        form = float(fs.min()) if len(fs) else float(fb.min()) if len(fb) else max(lo, start)
        form = min(form, hi)
        # a star on a strong beat about FLY seconds after the words leave
        sb = np.array(sorted(strong | downs))
        sb = sb[(sb >= h + FLY - 0.8) & (sb <= h + FLY + 0.8)] if len(sb) else sb
        star = float(sb[np.argmin(np.abs(sb - h - FLY))]) if len(sb) else h + FLY
        out.append(dict(form=round(form, 2), solid_from=round(form + FORM_DUR, 2), hold=round(h, 2),
                        out=round(h + DISSOLVE, 2), star=round(star, 2),
                        solid=round(h - form - FORM_DUR, 2), on_section=bool(np.any(np.abs(secs - h) < 0.05))))
        prev_out = h + DISSOLVE
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("audio")
    ap.add_argument("-n", type=int, default=0, help="number of expressions to place")
    ap.add_argument("--start", type=float, default=6.0, help="earliest form time (after the title card), s")
    ap.add_argument("--end", type=float, default=None, help="latest dissolve end (before the end card), s")
    ap.add_argument("--solid", type=float, default=6.0, help="seconds each expression stays solid (at least 6)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.solid < 6.0:
        sys.exit("the reading time contract needs --solid of at least 6 seconds")
    au = audio_react.Audio(a.audio).load(cache=False)
    end = a.end if a.end is not None else au.duration - 12.0
    res = dict(audio=a.audio, duration=round(au.duration, 2), tempo=round(au.tempo, 1),
               sections=[round(x, 2) for x in au.section_starts()], strong_beats=[round(x, 2) for x in au.strong_beats()])
    if a.n > 0:
        try:
            res["expressions"] = plan(au, a.n, a.start, end, a.solid)
        except ValueError as e:
            res["error"] = str(e)
    if a.json:
        print(json.dumps(res, indent=1))
        return
    print(f"{a.audio}: {res['duration']} s, tempo {res['tempo']} bpm")
    print("section starts (s):", ", ".join(f"{x:g}" for x in res["sections"]))
    print("strong beats (s):  ", ", ".join(f"{x:g}" for x in res["strong_beats"]))
    if "error" in res:
        sys.exit("cannot place the expressions: " + res["error"])
    if a.n > 0:
        print(f"\n{a.n} expressions between {a.start:g} and {end:g} s (form {FORM_DUR} s, solid >= {a.solid:g} s, "
              f"dissolve {DISSOLVE} s, gap {GAP} s)")
        print("  #   form   solid from   hold    out    star   solid s   hold on")
        for i, e in enumerate(res["expressions"]):
            print(f"  {i + 1}  {e['form']:6.2f}   {e['solid_from']:6.2f}   {e['hold']:6.2f}  {e['out']:6.2f}  "
                  f"{e['star']:6.2f}   {e['solid']:5.2f}    {'section start' if e['on_section'] else 'beat'}")
        print("\nfor PHRASES: " + ", ".join(f"(form={e['form']}, hold={e['hold']}, star={e['star']})"
                                            for e in res["expressions"]))


if __name__ == "__main__":
    main()
