"""Builds a punchy medley from a plan. Usage: build2.py REPO plan.json NAME OUTBASE

plan: {"segs": [[song, anchor_src, T, xfade, pre, level], ...]  anchor_src (a downbeat or hit) lands at medley T.
               For k>0 the crossfade into segment k spans [T - pre*X, T + (1-pre)*X] (pre=1: incoming is full at its
               hit, for hit cuts). level: target loudness (LUFS, relative scale) of the segment body.
       "level_win": [[a, b] per seg] source window used to measure each segment's body loudness (optional),
       "final_src": the final hit in the last song, "hold": s held after it, then a decaying tail to 60.0,
       "target": integrated LUFS before limiting}
"""
import sys, json, subprocess, re
import numpy as np
SR = 44100; DUR = 60.0
REPO, PLAN, NAME, OUT = sys.argv[1:5]
P = json.load(open(PLAN))[NAME]


def load(s):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', f'{REPO}/audio/promo/s{s}.mp3', '-ac', '2',
                          '-ar', str(SR), '-f', 'f32le', '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype='<f4').reshape(-1, 2).astype(np.float64)


def lufs(x):
    e = subprocess.run(['ffmpeg', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af',
                        'ebur128', '-f', 'null', '-'], input=x.astype('<f8').tobytes(), capture_output=True).stderr.decode()
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1])


segs = P['segs']
N = int(round(DUR * SR)); t = np.arange(N) / SR
mix = np.zeros((N, 2)); info = []
src_cache = {}
for k, sg in enumerate(segs):
    song, anchor, T, X, pre, level = sg[:6]
    src = src_cache.setdefault(song, load(song))
    off = anchor - T
    t0 = 0.0 if k == 0 else T - pre * X
    if k < len(segs) - 1:
        _, _, Tn, Xn, pren, _ = segs[k + 1][:6]
        outx = segs[k + 1][6] if len(segs[k + 1]) > 6 else (1 - pren) * Xn   # outgoing may ring past the hit
        t1 = Tn + outx
    else:
        t1 = DUR
    i0, i1 = int(round(t0 * SR)), int(round(t1 * SR))
    si = np.arange(i0, i1) + int(round(off * SR))
    if si[0] < 0 or si[-1] >= len(src):
        raise SystemExit(f'seg {k} {song} out of range {si[0]/SR:.2f}..{si[-1]/SR:.2f}')
    seg = src[si].copy(); tt = t[i0:i1]; env = np.ones(len(tt))
    if k > 0:
        u = np.clip((tt - t0) / X, 0, 1); env *= np.sin(0.5 * np.pi * u)
    if k < len(segs) - 1:
        a = Tn - pren * Xn
        u = np.clip((tt - a) / (t1 - a), 0, 1); env *= np.cos(0.5 * np.pi * u)
    # body loudness measured on the source between the crossfades (or a given window)
    if P.get('level_win') and P['level_win'][k]:
        a, b = P['level_win'][k]
    else:
        a = (T + (1 - pre) * X if k else 0.5) + off
        b = (Tn - pren * Xn if k < len(segs) - 1 else P['final_src'] - off) + off
    L = lufs(src[int(a * SR):int(b * SR)])
    g = level - L
    mix[i0:i1] += seg * (env * 10 ** (g / 20))[:, None]
    info.append(dict(song=song, anchor=anchor, T=T, off=off, t0=t0, t1=t1, body=[a, b], body_lufs=L, gain=g,
                     X=X, pre=pre, level=level))
    print(f'seg {k} {song}: medley {t0:6.2f}-{t1:6.2f} src {t0+off:6.2f}-{t1+off:6.2f} anchor {anchor} at {T:.2f}; '
          f'body {a:.2f}-{b:.2f} {L:.1f} LUFS -> gain {g:+.1f}')
fi = np.clip(t / 0.02, 0, 1); mix *= fi[:, None]
last = info[-1]
Tf = P['final_src'] - last['off']; tail0 = Tf + P['hold']
u = np.clip((t - tail0) / (DUR - tail0), 0, 1)
mix *= np.where(t < tail0, 1.0, (1 - u) ** P.get('tail_pow', 2.0))[:, None]
I = lufs(mix); mix *= 10 ** ((P['target'] - I) / 20)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-c:a', 'pcm_f32le', OUT + '.pre.wav'], input=mix.astype('<f8').tobytes(), check=True)
json.dump(dict(tracks=info, final=Tf, tail0=tail0), open(OUT + '.json', 'w'), indent=1)
print(f'final hit at medley {Tf:.3f}, tail {tail0:.3f}-60; pre-limiter I {I:.2f} -> {P["target"]}')
