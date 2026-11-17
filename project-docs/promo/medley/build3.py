"""Render a medley plan from plans3.json. Usage: build3.py SRC_DIR NAME OUT_BASE [key=value ...]

Pass 1, per segment: decode the clip, time-stretch with Rubber Band (ffmpeg rubberband, transients=mixed,
channels=together: chosen by measurement in stretch_test.py and stretch_test2.py), place it on the medley
timeline and set its body loudness (EBU R128 integrated over its body window) to its target (+0.5 dB per song).
Pass 2, level riding at the joins: each song's loudness inside the blend is measured; a gain ramp (1 s in, held
through the blend, 1 s out) brings it to its body target, at most +-6 dB, so a quiet held chord or a loud
pickup does not dip or jump the mix. In the lift the incoming pedal is ridden to sit LIFT_DB below its body and
the ride ends just before the entrance (the breath).
Pass 3, the blends: each placed song is split into three zero-phase bands (below 200 Hz, 200 Hz to 4 kHz, above
4 kHz; the bands sum back to the original exactly) with their own equal-power envelopes:
  beat and hold joins  outgoing: lows leave first (gone at 60 percent of the blend), mids and highs on a cosine;
                       incoming: highs ease in first (full at 75 percent), mids on a sine, lows swap in with
                       the outgoing lows
  lift                 the outgoing cadence chord fades after its arrival (lows first) while the incoming
                       song's quiet pedal swells (highs, then mids, then lows) under the breath
  splice               30 ms equal-power crossfade inside a sung breath (same song, same gain)
A short, subtle reverb tail (synthetic stereo room, high-passed send) follows the outgoing song of each join and
a longer one the final chord. Master: loudness target, limiter at -1 dBTP with 4x oversampling, MP3 256 kb/s,
44.1 kHz stereo. Outputs: OUT_BASE.pre.wav, .mp3, .json (gains and rides), .stems.npz (each song as heard, and
each song placed without its envelopes, mono, for the alignment checks).
"""
import sys, json, subprocess, re
import numpy as np
from scipy import signal

SRC, NAME, OUT = sys.argv[1:4]
OPT = dict(a.split('=') for a in sys.argv[4:])
SR = 44100
P = json.load(open('plans3.json'))[NAME]
N = int(round(P['total'] * SR)); tt = np.arange(N) / SR
BASE = float(OPT.get('base', -17.0))          # body loudness of the first song (pre-master scale)
LIFT_DB = float(OPT.get('lift_db', 2.0))      # the breath: the incoming pedal sits this far below its body
HOLD_DB = float(OPT.get('hold_db', 1.0))      # the lift's outgoing cadence chord sits this far below its body
TARGET_I = float(OPT.get('target', -13.8))     # master integrated loudness
REV_DB = float(OPT.get('rev_db', -15.0))      # join reverb wet level
RIDE_MAX = 6.0
BREATH_DB = float(OPT.get('breath_db', 1.9))   # the breath sits this far under the line between the bodies
LIFT_MODE = OPT.get('lift_mode', 'rms')           # how the breath is judged: 0.25 s RMS line or K-weighted
SWELL = float(OPT.get('swell', 0.0))              # how much of the breath is given back in its last 0.6 s
DARK = float(OPT.get('dark', 1.0))                # the incoming highs stay at this gain until the entrance
KGAP = float(OPT.get('kgap', 1.0))               # the breath stays this far (K-weighted) under the climax body
HIT_DB = float(OPT.get('hit_db', 3.0))           # the entrance may rise this far over the climax body
LIFT_SEGRIDE = int(OPT.get('lift_segride', 1))   # 1: also ride the two songs of the lift separately (0: the bus does it)
PEAK_GAP = float(OPT.get('peak_gap', 1.0))       # before the breath nothing is louder than the climax peaks minus this
RISE_MAX = float(OPT.get('rise_max', 2.8))       # elsewhere no ear-weighted rise over 0.5 s may exceed this
c01 = lambda x: np.clip(x, 0.0, 1.0)


def decode(song):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', f'{SRC}/s{song}.mp3', '-f', 'f32le', '-ac', '2',
                          '-ar', str(SR), '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, '<f4').reshape(-1, 2).astype(np.float64)


def ffpipe(x, af):
    return np.frombuffer(subprocess.run(
        ['ffmpeg', '-v', 'error', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', af,
         '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-'], input=x.astype('<f8').tobytes(), capture_output=True,
        check=True).stdout, '<f8').reshape(-1, 2)


def lufs(x):
    e = subprocess.run(['ffmpeg', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128',
                        '-f', 'null', '-'], input=x.astype('<f8').tobytes(), capture_output=True).stderr.decode()
    v = re.findall(r'I:\s+(-?[\d.]+) LUFS', e)
    return float(v[-1]) if v else -70.0


def lufs_at(x, a, b):
    return lufs(x[int(a * SR):int(b * SR)])


SOS_LO = signal.butter(4, 200, 'low', fs=SR, output='sos')
SOS_HI = signal.butter(4, 4000, 'high', fs=SR, output='sos')


def bands(x):
    lo = signal.sosfiltfilt(SOS_LO, x, axis=0); hi = signal.sosfiltfilt(SOS_HI, x, axis=0)
    return lo, x - lo - hi, hi


def room(rt60, seconds, seed, predelay=0.012):
    """Synthetic stereo room: decorrelated noise, frequency-dependent decay (highs die faster)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR); t = np.arange(n) / SR
    ir = np.zeros((n + int(predelay * SR), 2))
    for ch in range(2):
        z = rng.standard_normal(n)
        lo = signal.sosfilt(signal.butter(2, 500, 'low', fs=SR, output='sos'), z)
        hi = signal.sosfilt(signal.butter(2, 3000, 'high', fs=SR, output='sos'), z)
        mid = z - lo - hi
        d = lambda r: 10 ** (-3 * t / r)
        y = lo * d(rt60 * 1.1) + mid * d(rt60) + hi * d(rt60 * 0.45)
        y *= np.minimum(1, t / 0.008)
        ir[int(predelay * SR):, ch] = y
    ir /= np.sqrt((ir ** 2).sum(0).mean())
    return ir


SOS_SEND = signal.butter(2, 250, 'high', fs=SR, output='sos')


def reverb(send, rt60, wet_db, seed):
    nz = np.nonzero(np.abs(send) > 0)[0]
    out = np.zeros((N, 2))
    if not len(nz): return out
    a, b = nz[0], nz[-1] + 1
    x = signal.sosfilt(SOS_SEND, send[a:b])
    ir = room(rt60, rt60 * 1.3, seed)
    y = np.stack([signal.fftconvolve(x, ir[:, c]) for c in range(2)], 1) * 10 ** (wet_db / 20)
    m = min(len(y), N - a)
    out[a:a + m] = y[:m]
    return out


def T(sg, s):
    return sg['t_a'] + (s - sg['s_a']) * sg['alpha']


segs, joins = P['segs'], P['joins']
# ---------------------------------------------------------------- pass 1: place, stretch, body gain
cache, placed, info = {}, [], []
gain07 = None
for k, sg in enumerate(segs):
    x = cache.setdefault(sg['song'], decode(sg['song']))
    ex0 = max(sg['s_in'] - 1.0, 0.0); ex1 = min(sg['s_out'] + 1.0, len(x) / SR)
    ex = x[int(ex0 * SR):int(ex1 * SR)]
    y = ffpipe(ex, f"rubberband=tempo={1 / sg['alpha']:.8f}:transients=mixed:channels=together") \
        if abs(sg['alpha'] - 1) > 1e-6 else ex
    a = T(sg, sg['s_in']); b = T(sg, sg['s_out'])
    n0, n1 = max(int(np.floor(a * SR)), 0), min(int(np.ceil(b * SR)), N)
    idx = np.clip(np.round((tt[n0:n1] - sg['t_a'] + (sg['s_a'] - ex0) * sg['alpha']) * SR).astype(int), 0, len(y) - 1)
    pl = np.zeros((N, 2)); pl[n0:n1] = y[idx]
    if sg['key'] == '07b' and gain07 is not None:
        g_db, L = gain07
    else:
        L = lufs_at(pl, T(sg, sg['body'][0]), T(sg, sg['body'][1]))
        g_db = BASE + sg['level'] - L
        if sg['key'] == '07a': gain07 = (g_db, L)
    pl *= 10 ** (g_db / 20)
    placed.append(pl)
    info.append(dict(key=sg['key'], body_lufs=L, gain_db=g_db, medley=[a, b], alpha=sg['alpha'], rides=[]))
    print(f"{sg['key']:4s} medley {a:6.2f}-{b:6.2f} alpha {sg['alpha']:.5f} body {L:6.2f} LUFS -> gain {g_db:+6.2f} dB")
    sys.stdout.flush()
# ---------------------------------------------------------------- envelopes that do not depend on the gains
env_lmh = [[np.zeros(N), np.zeros(N), np.zeros(N)] for _ in segs]
for k, sg in enumerate(segs):
    for e in env_lmh[k]: e[(tt >= T(sg, sg['s_in'])) & (tt < T(sg, sg['s_out']))] = 1.0
for j in joins:
    o, i, t0, t1 = j['out'], j['inn'], j['t0'], j['t1']
    u = (tt - t0) / (t1 - t0); w = (tt >= t0) & (tt < t1)
    eo, ei = env_lmh[o], env_lmh[i]
    if j['kind'] in ('beat', 'hold'):
        lo_u = c01((u - 0.15) / 0.45)
        sh = [(np.cos(np.pi / 2 * lo_u), np.sin(np.pi / 2 * lo_u)),
              (np.cos(np.pi / 2 * c01(u)), np.sin(np.pi / 2 * c01(u))),
              (np.cos(np.pi / 2 * c01(u)), np.sin(np.pi / 2 * c01(u / 0.75)))]
        for bnd in range(3):
            eo[bnd][w] *= sh[bnd][0][w]; ei[bnd][w] *= sh[bnd][1][w]
            eo[bnd][tt >= t1] = 0; ei[bnd][tt < t0] = 0
    elif j['kind'] == 'lift':
        E, H = j['breath']; oe = j['out_end']
        uo = c01((tt - (E + 0.2)) / (oe - (E + 0.2))); ul = c01((tt - (E + 0.5)) / (oe - 0.3 - (E + 0.5)))
        eo[0] *= np.cos(np.pi / 2 * ul); eo[1] *= np.cos(np.pi / 2 * uo); eo[2] *= np.cos(np.pi / 2 * uo)
        for e in eo: e[tt >= oe] = 0
        ei[2] *= np.sin(np.pi / 2 * c01((tt - t0) / (H - 0.3 - t0))) * (DARK + (1 - DARK) * c01((tt - (H - 0.04)) / 0.04))
        ei[1] *= np.sin(np.pi / 2 * c01((tt - t0) / 1.6))
        ei[0] *= np.sin(np.pi / 2 * c01((tt - (E - 0.2)) / 0.9))
        for e in ei: e[tt < t0] = 0
    elif j['kind'] == 'splice':
        for bnd in range(3):
            eo[bnd][w] *= np.cos(np.pi / 2 * u[w]); ei[bnd][w] *= np.sin(np.pi / 2 * u[w])
            eo[bnd][tt >= t1] = 0; ei[bnd][tt < t0] = 0
lead, fi = P['lead'], P['fadein']
ufi = c01((tt - lead) / fi); gstart = np.where(tt < lead, 0.0, ufi * ufi * (3 - 2 * ufi))
end = P['end']
ue = c01((tt - end['fade0']) / (end['fade1'] - end['fade0']))
gend = np.where(tt >= end['fade1'], 0.0, 10 ** (-60 * ue ** 1.3 / 20))
BANDS = [bands(p) for p in placed]                       # placed at unit (body) gain; bands scale with gain
E_lift, H_lift = P['lift']['E'], P['lift']['H']


def body_window(k):
    """A song's own stretch: from the end of its incoming blend to the start of its outgoing blend."""
    a, b = (lead + fi, None)
    for j in joins:
        if j['inn'] == k: a = j['t1'] if j['kind'] != 'lift' else H_lift
        if j['out'] == k and j['kind'] != 'splice': b = j['t0'] if j['kind'] != 'lift' else j['breath'][0]
        if j['out'] == k and j['kind'] == 'splice': b = j['t0']
    return a, b


# ---------------------------------------------------------------- level riding of each song inside the blends
def make_rides(gdb):
    ride = [np.zeros(N) for _ in segs]; log = []

    def add(k, d_db, a_in, a_full, b_full, b_out):
        r = np.zeros(N); r[(tt >= a_full) & (tt <= b_full)] = 1
        if a_full > a_in:
            w = (tt >= a_in) & (tt < a_full); u = (tt[w] - a_in) / (a_full - a_in); r[w] = u * u * (3 - 2 * u)
        if b_out > b_full:
            w = (tt > b_full) & (tt <= b_out); u = (b_out - tt[w]) / (b_out - b_full); r[w] = u * u * (3 - 2 * u)
        ride[k] += d_db * r
    for j in joins:
        o, i, t0, t1 = j['out'], j['inn'], j['t0'], j['t1']
        po = placed[o] * 10 ** (gdb[o] / 20); pi = placed[i] * 10 ** (gdb[i] / 20)
        if j['kind'] in ('beat', 'hold'):
            Lo = lufs_at(po, t0, t0 + 0.6 * (t1 - t0)); Li = lufs_at(pi, t0 + 0.4 * (t1 - t0), t1)
            do = float(np.clip(BASE + segs[o]['level'] - Lo, -RIDE_MAX, RIDE_MAX))
            di = float(np.clip(BASE + segs[i]['level'] - Li, -RIDE_MAX, RIDE_MAX))
            add(o, do, t0 - 0.6, t0 + 0.3, t1, t1 + 0.01); add(i, di, t0 - 0.01, t0, t1 - 0.6, t1)
            log.append(f"ride {segs[o]['key']}->{segs[i]['key']}: outgoing {Lo:6.2f} LUFS {do:+.2f} dB, incoming {Li:6.2f} LUFS {di:+.2f} dB")
        elif j['kind'] == 'lift':
            Lo = lufs_at(po, E_lift - 0.4, E_lift + 0.9); Li = lufs_at(pi, E_lift + 0.6, H_lift - 0.15)
            do = float(np.clip(BASE + segs[o]['level'] - HOLD_DB - Lo, -RIDE_MAX, RIDE_MAX)) if LIFT_SEGRIDE else 0.0
            di = float(np.clip(BASE + segs[i]['level'] - LIFT_DB - Li, -RIDE_MAX, 9.0)) if LIFT_SEGRIDE else 0.0
            add(o, do, E_lift - 1.0, E_lift, j['out_end'], j['out_end'] + 0.01)
            add(i, di, t0 - 0.01, t0, H_lift - 0.15, H_lift - 0.03)   # ends just before the entrance
            log.append(f"lift ride: cadence chord {Lo:6.2f} LUFS {do:+.2f} dB, pedal {Li:6.2f} LUFS {di:+.2f} dB")
    return ride, log


# ---------------------------------------------------------------- the mix bus: keep the level steady through blends
HOPE = 0.01


def env_db(x):
    p2 = 0.5 * (x[:, 0] ** 2 + x[:, 1] ** 2); c = np.concatenate([[0.0], np.cumsum(p2)])   # stereo: mean channel power
    W = int(0.25 * SR); tg = np.arange(0.125, P['total'] - 0.125, HOPE)
    i = (tg * SR).astype(int)
    return tg, 10 * np.log10((c[i + W // 2] - c[i - W // 2]) / W + 1e-12)


def smooth(v, sec):
    n = max(int(sec / HOPE), 1) | 1; k = np.hanning(n + 2)[1:-1]; k /= k.sum()
    return np.convolve(np.pad(v, n, mode='edge'), k, mode='same')[n:-n]


def kfilter():
    """ITU-R BS.1770 K-weighting (high shelf +4 dB near 1.7 kHz, high pass near 38 Hz), RBJ biquads at SR."""
    A = 10 ** (4 / 40); w = 2 * np.pi * 1681.97 / SR; al = np.sin(w) / (2 * 0.7071); cw = np.cos(w)
    b1 = [A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * cw),
          A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * al)]
    a1 = [(A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * cw),
          (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * al]
    w = 2 * np.pi * 38.13 / SR; al = np.sin(w) / (2 * 0.5); cw = np.cos(w)
    b2 = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; a2 = [1 + al, -2 * cw, 1 - al]
    return np.array([np.r_[b1, a1] / a1[0], np.r_[b2, a2] / a2[0]])


SOS_K = kfilter()


def env_k(x, win=0.4):
    kf = signal.sosfilt(SOS_K, x, axis=0); p2 = 0.5 * (kf[:, 0] ** 2 + kf[:, 1] ** 2); c = np.concatenate([[0.0], np.cumsum(p2)]); m = p2
    W = int(win * SR); tg = np.arange(0.125, P['total'] - 0.125, HOPE)
    i = np.clip((tg * SR).astype(int), W // 2, len(m) - W // 2)
    return tg, 10 * np.log10((c[i + W // 2] - c[i - W // 2]) / W + 1e-12)


def bus_ride(x, tol=1.0):
    tg, e = env_db(x); es = smooth(e, 0.25); corr = np.zeros(len(tg))
    med = lambda a, b: float(np.median(e[(tg >= a) & (tg <= b)]))
    _, ek = env_k(x); eks = smooth(ek, 0.2)
    medk = lambda a, b: float(np.median(ek[(tg >= a) & (tg <= b)]))
    for j in joins:
        if j['kind'] in ('beat', 'hold'):
            t0, t1 = j['t0'], j['t1']
            rb, ra = med(t0 - 2.0, t0 - 0.3), med(t1 + 0.3, t1 + 2.0)
            ref = rb + (ra - rb) * c01((tg - t0) / (t1 - t0))
            d = ref - es; c = np.sign(d) * np.maximum(np.abs(d) - tol, 0)
            wr = c01((tg - (t0 - 0.35)) / 0.3) * c01(((t1 + 0.35) - tg) / 0.3)
            corr += smooth(np.clip(c, -5, 5) * wr, 0.3) * wr
        elif j['kind'] == 'lift':
            # the breath, judged by ear-weighted loudness (K-weighted, 0.4 s): BREATH_DB under the body before by
            # E + 0.3, swelling in its last 0.6 s to half that under the quieter of the two bodies; then the
            # entrance: its first 0.7 s never above the climax body (unweighted)
            t0, t1 = j['t0'], j['t1']
            rb, ra = med(t0 - 2.0, t0 - 0.3), med(t1 + 0.3, t1 + 2.0)
            if LIFT_MODE == 'k':
                kb, ka = medk(t0 - 2.0, t0 - 0.3), medk(t1 + 0.3, t1 + 2.0)
                low_ = kb - BREATH_DB; top_ = min(kb, ka) - 0.5 * BREATH_DB
                target = kb + (low_ - kb) * c01((tg - t0) / (E_lift + 0.3 - t0))
                target = target + (top_ - low_) * c01((tg - (H_lift - 0.6)) / 0.6)
                cur = eks
            else:   # 'rms': BREATH_DB under the line between the bodies (0.25 s RMS), swelling into the entrance
                line = rb + (ra - rb) * c01((tg - t0) / (t1 - t0))
                swell = 1 - SWELL * c01((tg - (H_lift - 0.6)) / 0.55)
                target = line - BREATH_DB * c01((tg - t0) / (E_lift + 0.3 - t0)) * swell
                cur = es
            d = target - cur; c = np.clip(np.sign(d) * np.maximum(np.abs(d) - 0.3, 0), -8, 6)
            kcap = float(np.percentile(ek[(tg >= t1 + 0.3) & (tg <= t1 + 2.5)], 90)) - KGAP   # by ear: under the climax peaks
            if KGAP < 50: c = np.minimum(c, kcap - eks)
            hb = H_lift - 0.012
            pre = tg < hb
            c[~pre] = c[pre][-1]                        # hold the last value so smoothing does not sag at the hit
            c[tg < t0 - 0.1] = 0
            wr = c01((tg - (t0 - 0.1)) / 0.3) * pre
            corr += smooth(c, 0.2) * wr
            cap = ra + HIT_DB
            d2 = np.minimum(cap - es, 0); d2[tg < hb] = 0
            w2 = (tg >= hb) * c01((H_lift + 0.7 - tg) / 0.25)
            corr += smooth(np.clip(d2, -4, 0), 0.12) * w2
    if PEAK_GAP < 50:
        # the climax keeps the loudest moments: before the breath nothing rises (by ear, K-weighted 0.4 s) above
        # the climax's 90th percentile minus PEAK_GAP; only ever turned down, gently
        climax = (tg >= H_lift + 0.3) & (tg <= H_lift + 4.5)
        kc = float(np.percentile(ek[climax], 90)) - PEAK_GAP
        cur = eks + corr
        d3 = np.minimum(kc - cur, 0) * (tg >= lead + fi) * (tg < E_lift - 0.6)
        corr += smooth(d3, 0.5)
    if RISE_MAX < 50:
        # the lift keeps the strongest entrance: elsewhere no rise (by ear, K-weighted 0.5 s after minus 0.5 s
        # before) is allowed above RISE_MAX; an accent that rises more is turned down by the excess, gently
        _, k5 = env_k(x, 0.5)
        lvl = k5 + corr
        n5 = int(0.25 / HOPE)
        r = np.full(len(tg), -99.0); r[n5:-n5] = lvl[2 * n5:] - lvl[:-2 * n5]
        allowed = (tg > lead + fi + 0.2) & ~((tg > E_lift - 0.1) & (tg < H_lift + 0.9))
        ex = np.where(allowed, np.maximum(r - RISE_MAX, 0), 0)
        cut = np.zeros(len(tg)); m50 = int(0.5 / HOPE)
        for q in np.nonzero(ex > 0)[0]:
            cut[q:q + m50] = np.maximum(cut[q:q + m50], ex[q])
        corr -= smooth(cut, 0.15)
    return np.interp(tt, tg, 10 ** (corr / 20)), corr


def render(gdb):
    ride, log = make_rides(gdb)
    mix = np.zeros((N, 2)); stems = {}
    for k, sg in enumerate(segs):
        lo, mi, hi = BANDS[k]; el = env_lmh[k]
        g = 10 ** ((ride[k] + gdb[k]) / 20) * gstart * gend
        out = (lo * el[0][:, None] + mi * el[1][:, None] + hi * el[2][:, None]) * g[:, None]
        mix += out; stems[sg['key']] = out.mean(1)
    rev = np.zeros((N, 2))
    for n, j in enumerate(joins):
        if j['kind'] == 'splice': continue
        st = stems[segs[j['out']]['key']]
        if j['kind'] == 'lift':
            a0, a1, rt, wdb = j['breath'][0] - 0.2, j['out_end'], 1.8, REV_DB + 2
        else:
            a0, a1, rt, wdb = j['t0'] - 0.3, j['t1'], 1.2, REV_DB
        rev += reverb(st * ((tt >= a0) & (tt <= a1)), rt, wdb, seed=11 + n)
    F = end['final']
    rev += reverb(stems['07b'] * (tt >= F - 0.05), end['rev_rt60'], end['rev_db'], seed=99)
    rev *= gstart[:, None]
    w = tt >= P['total'] - 0.6
    rev[w] *= c01((P['total'] - 0.05 - tt[w]) / 0.55)[:, None]
    mix += rev
    bus = np.ones(N)
    for it in range(2):
        b, corr = bus_ride(mix * bus[:, None])
        bus *= b
    mix *= bus[:, None]
    mix[tt < lead] = 0.0
    return mix, stems, rev, bus, log


gdb = np.array([i['gain_db'] for i in info]) * 0.0     # extra gain on top of the body gain, per segment
for it in range(3):
    mix, stems, rev, bus, log = render(gdb)
    devs = []
    for k, sg in enumerate(segs):
        if sg['key'] == '07b': devs.append(None); continue
        a, b = body_window(k)
        L = lufs_at(mix, a, b); devs.append(BASE + sg['level'] - L)
    ref = np.mean([d for d in devs if d is not None])
    print(f'iteration {it}: body deviation from target (dB, after removing the mean {ref:+.2f}): ' +
          ', '.join(f"{segs[k]['key']} {d - ref:+.2f}" for k, d in enumerate(devs) if d is not None))
    for k, d in enumerate(devs):
        if d is not None: gdb[k] += d - ref
    gdb[[k for k, s in enumerate(segs) if s['key'] == '07b']] = gdb[[k for k, s in enumerate(segs) if s['key'] == '07a']]
mix, stems, rev, bus, log = render(gdb)
print('\n'.join(log))
for k, sg in enumerate(segs):
    info[k]['gain_db'] += float(gdb[k]); info[k]['body_window'] = body_window(k)
Ipre = lufs(mix)
mg = 10 ** ((TARGET_I - Ipre) / 20)
mix *= mg
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-c:a', 'pcm_f32le', OUT + '.pre.wav'], input=mix.astype('<f8').tobytes(), check=True)
np.savez_compressed(OUT + '.stems.npz', sr=SR, gain=mg, rev=rev.mean(1).astype(np.float32), bus=bus.astype(np.float32),
                    **{k: (v * bus).astype(np.float32) for k, v in stems.items()},
                    **{'raw_' + sg['key']: placed[k].mean(1).astype(np.float32) for k, sg in enumerate(segs)})
json.dump(dict(plan=NAME, info=info, pre_I=Ipre, target_I=TARGET_I, base=BASE, lift_db=LIFT_DB, hold_db=HOLD_DB,
               breath_db=BREATH_DB, rev_db=REV_DB, rides=log,
               bus_min_db=float(20 * np.log10(bus.min())), bus_max_db=float(20 * np.log10(bus.max()))),
          open(OUT + '.json', 'w'), indent=1)
print(f'pre-master I {Ipre:.2f} -> {TARGET_I}; peak {20 * np.log10(np.abs(mix).max()):.2f} dBFS; '
      f'bus ride range {20 * np.log10(bus.min()):+.1f} to {20 * np.log10(bus.max()):+.1f} dB')


def meas(path):
    p = subprocess.run(['ffmpeg', '-nostdin', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return (float(re.findall(r'I:\s+(-?[\d.]+) LUFS', p)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', p)[-1]))


g, lim = 0.0, -1.5
for it in range(6):
    af = (f'volume={g}dB,aresample=176400,alimiter=limit={10 ** (lim / 20):.4f}:attack=4:release=150:level=false,'
          f'aresample=44100')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-i', OUT + '.pre.wav', '-af', af, '-c:a', 'libmp3lame',
                    '-b:a', '256k', '-ar', '44100', '-ac', '2', OUT + '.mp3'], check=True)
    I, TP = meas(OUT + '.mp3')
    print(f'master iter {it}: gain {g:+.2f} limit {lim:.2f} -> I {I:.2f} LUFS, TP {TP:.2f} dBTP')
    if TP <= -1.0 and abs(I - TARGET_I) <= 0.15: break
    if TP > -1.0: lim -= (TP + 1.0) + 0.1
    if abs(I - TARGET_I) > 0.15: g += TARGET_I - I
