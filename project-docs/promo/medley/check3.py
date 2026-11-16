"""Measured checks for a built medley. Usage: check3.py NAME BASE   (BASE = work/main etc.)

Reads plans3.json (plan NAME), BASE.mp3, BASE.json, BASE.stems.npz. Prints every check with PASS or FAIL and
writes BASE.check.json for the section map.
  format     ffprobe: codec, bit rate, sample rate, channels; decoded length in samples (gapless) and seconds
  silence    0 to 2 s: peak sample level
  clipping   decoded sample peak and true peak (EBU R128, 4x oversampled)
  joins      0.25 s RMS envelope (50 ms hop): dip and jump against the line between the bodies before and
             after the blend (medians over 1.75 s), and the largest step between consecutive 0.25 s windows
  beats      each blend: onset-envelope cross-correlation of the two placed songs (lag of best match, +-150 ms),
             and per planned beat the gap between the two songs' nearest onset peaks
  bodies     integrated loudness of each song's own stretch (no blend) in the final file; neighbours within 1 dB,
             overall rise
  ending     final chord, ring-out length, level of the last second, no rise after the final chord
"""
import sys, json, subprocess, re
import numpy as np, librosa

NAME, BASE = sys.argv[1], sys.argv[2]
P = json.load(open('plans3.json'))[NAME]; B = json.load(open(BASE + '.json'))
SR = 44100
res = dict(ok=True)


def flag(ok):
    if not ok: res['ok'] = False
    return 'PASS' if ok else 'FAIL'


def T(sg, s):
    return sg['t_a'] + (s - sg['s_a']) * sg['alpha']


mp3 = BASE + '.mp3'
pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate:stream=codec_name,sample_rate,'
                     'channels,bit_rate', '-of', 'json', mp3], capture_output=True, text=True).stdout
pj = json.loads(pr); st = pj['streams'][0]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', mp3, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, '<f4').reshape(-1, 2).astype(np.float64)
n = len(x); N = int(round(P['total'] * SR))
print(f"format: {st['codec_name']} {int(st['bit_rate']) // 1000} kb/s {st['sample_rate']} Hz {st['channels']} ch; "
      f"ffprobe container duration {float(pj['format']['duration']):.6f} s; decoded {n} samples = {n / SR:.6f} s "
      f"-> {flag(n == N and st['codec_name'] == 'mp3' and int(st['bit_rate']) == 256000 and st['sample_rate'] == '44100' and st['channels'] == 2)}")
res['format'] = dict(codec=st['codec_name'], bitrate=int(st['bit_rate']), sr=int(st['sample_rate']),
                     ch=st['channels'], ffprobe_duration=float(pj['format']['duration']), decoded_s=n / SR)
db = lambda v: 20 * np.log10(max(v, 1e-12))
pk_lead = np.abs(x[:int(1.95 * SR)]).max(); pk_lead2 = np.abs(x[:int(2.0 * SR)]).max()
print(f'silence: peak 0-1.95 s {db(pk_lead):.1f} dBFS, 0-2.00 s {db(pk_lead2):.1f} dBFS -> {flag(pk_lead2 < 10 ** (-60 / 20))}')
res['silence'] = dict(peak_0_195=db(pk_lead), peak_0_2=db(pk_lead2))
e = subprocess.run(['ffmpeg', '-nostdin', '-i', mp3, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True,
                   text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)[-1])
LRA = float(re.findall(r'LRA:\s+(-?[\d.]+) LU', e)[-1])
smax = np.abs(x).max(); nclip = int((np.abs(x) >= 0.999).sum())
print(f'clipping: sample peak {db(smax):.2f} dBFS, samples at full scale {nclip}, true peak {TP:.2f} dBTP; '
      f'integrated {I:.2f} LUFS, LRA {LRA} LU -> {flag(nclip == 0 and TP <= -0.5)}')
res['loud'] = dict(sample_peak=db(smax), true_peak=TP, I=I, LRA=LRA)
# 0.25 s RMS envelope (stereo: mean of the two channels' power), 50 ms hop, window centred
m = x.mean(1); W = int(0.25 * SR); H = int(0.05 * SR)
p2 = 0.5 * (x[:, 0] ** 2 + x[:, 1] ** 2)
cen = np.arange(W // 2, n - W // 2, H) / SR
env = np.array([db(np.sqrt(np.mean(p2[int(c * SR) - W // 2:int(c * SR) + W // 2]))) for c in cen])
res['env'] = dict(t=cen.tolist(), db=env.tolist())


def envat(a, b):
    k = (cen >= a) & (cen <= b)
    return cen[k], env[k]


res['joins'] = []
for j in P['joins']:
    if j['kind'] == 'splice': continue
    o, i = P['segs'][j['out']], P['segs'][j['inn']]
    t0, t1 = j['t0'], j['t1']
    if j['kind'] == 'lift':
        rb = np.median(envat(t0 - 2.0, t0 - 0.25)[1]); ra = np.median(envat(t1 + 0.25, t1 + 2.0)[1])
    else:
        rb = np.median(envat(t0 - 2.0, t0 - 0.25)[1]); ra = np.median(envat(t1 + 0.25, t1 + 2.0)[1])
    c, v = envat(t0, t1)
    ref = rb + (ra - rb) * (c - t0) / (t1 - t0)
    dip = float(np.max(ref - v)); jump = float(np.max(v - ref))
    # consecutive non-overlapping 0.25 s windows across the join (and its edges)
    c2, v2 = envat(t0 - 0.25, t1 + 0.25)
    steps = [abs(v2[q + 5] - v2[q]) for q in range(len(v2) - 5)]
    step = float(max(steps))
    ok = dip <= 3.0 and jump <= 3.0
    r = dict(kind=j['kind'], out=o['key'], inn=i['key'], t0=t0, t1=t1, mid=(t0 + t1) / 2, ref_before=float(rb),
             ref_after=float(ra), dip=dip, jump=jump, step=step)
    res['joins'].append(r)
    print(f"join {o['key']}->{i['key']} ({j['kind']}) {t0:.2f}-{t1:.2f}: bodies {rb:.1f} / {ra:.1f} dB, dip {dip:.2f} dB, "
          f"jump {jump:.2f} dB, largest 0.25 s step {step:.2f} dB -> {flag(ok)}")
# the lift in detail
E, Hh = P['lift']['E'], P['lift']['H']
cb, vb = envat(E, Hh - 0.15)
pre = np.median(envat(E - 2.5, E - 0.6)[1]); post = np.median(envat(Hh + 0.3, Hh + 2.3)[1])
hit_step = float(np.max(envat(Hh - 0.1, Hh + 0.6)[1]) - np.median(envat(Hh - 0.6, Hh - 0.1)[1]))
print(f'lift: body before {pre:.1f} dB, breath {E:.2f}-{Hh:.2f} median {np.median(vb):.1f} dB (min {vb.min():.1f}), '
      f'body after the hit {post:.1f} dB; breath easing {pre - np.median(vb):.2f} dB below the body before; '
      f'hit at {Hh:.2f}: rise {hit_step:.2f} dB over the last 0.5 s of the breath')
res['lift'] = dict(E=E, H=Hh, body_before=float(pre), breath_median=float(np.median(vb)), breath_min=float(vb.min()),
                   body_after=float(post), hit_rise=hit_step)
# beats: stems
S = np.load(BASE + '.stems.npz')
HOPB = 64


def oenv(y, a, b):
    seg = y[int(a * SR):int(b * SR)]
    o = librosa.onset.onset_strength(y=seg.astype(np.float32), sr=SR, hop_length=HOPB, lag=2, n_fft=1024)
    return o


def beat_phase(y, a, b, Pm, ref):
    """Where the beat falls (ms from the grid ref + k*Pm) by onset, bass flux, loudness rise and chord change."""
    seg = y[int(a * SR):int(b * SR)].astype(np.float32)
    Sx = np.abs(librosa.stft(seg, n_fft=2048, hop_length=HOPB)); frq = librosa.fft_frequencies(sr=SR, n_fft=2048)
    Dx = librosa.amplitude_to_db(Sx + 1e-9)
    fl = lambda mk: np.concatenate([np.zeros(4), np.maximum(0, Dx[mk][:, 4:] - Dx[mk][:, :-4]).mean(0)])
    rmsx = librosa.power_to_db((Sx ** 2).sum(0) + 1e-12)
    rise = np.maximum(0, np.concatenate([np.zeros(6), rmsx[6:] - rmsx[:-6]]))
    ch = librosa.feature.chroma_stft(S=Sx ** 2, sr=SR); chn = ch / (np.linalg.norm(ch, axis=0) + 1e-9)
    k = int(0.15 * SR / HOPB); nov = np.zeros(ch.shape[1])
    cs = np.cumsum(np.pad(chn, ((0, 0), (1, 0))), axis=1)
    for q in range(k, ch.shape[1] - k):
        u = cs[:, q] - cs[:, q - k]; v = cs[:, q + k] - cs[:, q]
        nov[q] = 1 - u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9)
    ons = librosa.onset.onset_strength(S=Dx, sr=SR, hop_length=HOPB, lag=2)
    n = min(len(ons), len(nov))
    z = lambda f: (f[:n] - f[:n].mean()) / (f[:n].std() + 1e-9)
    comb = z(ons) + z(fl((frq > 30) & (frq < 250))) + z(rise) + z(nov)
    tt_ = a + np.arange(n) * HOPB / SR
    zz = (comb * np.exp(-2j * np.pi * (tt_ - ref) / Pm)).sum()
    off = (-np.angle(zz) / (2 * np.pi) * Pm + Pm / 2) % Pm - Pm / 2
    return off * 1000, abs(zz) / np.abs(comb).sum()


res['beats'] = []
for j in P['joins']:
    if j['kind'] not in ('beat', 'hold', 'lift'): continue
    o, i = P['segs'][j['out']], P['segs'][j['inn']]
    t0, t1 = j['t0'], j['t1']
    yo, yi = S[o['key']], S[i['key']]
    eo_in, ei_in = oenv(yo, t0, t1), oenv(yi, t0, t1)
    # both songs as placed, without the blend envelopes, over the blend and up to 1.5 s around it
    wa = max(t0 - 1.5, T(i, i['s_in']) + 0.05); wb = min(t1 + 1.5, T(o, o['s_out']) - 0.05)
    if j['kind'] == 'lift': wa, wb = t0, t1
    ro, ri = S['raw_' + o['key']], S['raw_' + i['key']]
    eo, ei = oenv(ro, wa, wb), oenv(ri, wa, wb)
    L = int(0.15 * SR / HOPB)

    def xlag(p, q, peak=False):
        a0, b0 = (p - p.mean()) / (p.std() + 1e-9), (q - q.mean()) / (q.std() + 1e-9)
        cc = [float((a0[max(0, l):len(a0) + min(0, l)] * b0[max(0, -l):len(b0) - max(0, l)]).mean())
              for l in range(-L, L + 1)]
        v = (int(np.argmax(cc)) - L) * HOPB / SR * 1000
        return (v, float(max(cc))) if peak else v
    (lag, cpk), lag_in = xlag(eo, ei, True), xlag(eo_in, ei_in)
    # beat phase of each song in the window (onset, bass, loudness rise, chord change), against one grid
    same_tempo = abs(o['P'] * o['alpha'] - i['P'] * i['alpha']) < 0.01
    if same_tempo and j['kind'] != 'lift':
        Pm = i['P'] * i['alpha']; ref = T(i, i['g_a'])
        po, so = beat_phase(ro, wa, wb, Pm, ref); pi_, si = beat_phase(ri, wa, wb, Pm, ref)
        dphase = (po - pi_ + Pm * 500) % (Pm * 1000) - Pm * 500
    else:
        po = pi_ = so = si = dphase = float('nan')

    def pb(sg):
        P0, a = sg['P'], sg['g_a']
        tb = np.array([T(sg, a + k * P0) for k in np.arange(-80, 80)])
        return tb[(tb >= wa + 0.08) & (tb <= wb - 0.08)]
    bo, bi = pb(o), pb(i)
    gaps = []
    fr = np.arange(len(eo)) * HOPB / SR + wa
    for tb in bi:
        q = np.argmin(abs(bo - tb)) if len(bo) else None
        if q is None or abs(bo[q] - tb) > 0.1: continue
        w = (fr >= tb - 0.07) & (fr <= tb + 0.07)
        if not w.any(): continue
        po = fr[w][np.argmax(eo[w])]; pi = fr[w][np.argmax(ei[w])]
        gaps.append(((tb + bo[q]) / 2, (pi - po) * 1000, float(bo[q] - tb) * 1000))
    # how rhythmic is the outgoing side inside the blend (held chord or not): onset strength vs its own body
    sb = (o['body'][0], o['body'][1])
    eob = oenv(ro, T(o, sb[0]), T(o, sb[1]))
    act = float(np.median(oenv(ro, t0 + 0.3, t1)) / (np.median(eob) + 1e-9))
    planned = [g[2] for g in gaps]
    gl = [g[1] for g in gaps]
    med = float(np.median(gl)) if gaps else float('nan')
    r = dict(out=o['key'], inn=i['key'], kind=j['kind'], window=[wa, wb], xcorr_lag_ms=lag, xcorr_lag_in_blend_ms=lag_in,
             beat_gaps_ms=gl, median_gap_ms=med, planned_offsets_ms=planned, out_activity=act, beats=[g[0] for g in gaps],
             phase_out_ms=po, phase_in_ms=pi_, phase_strength=[so, si], phase_diff_ms=dphase, xcorr_peak=cpk)
    measurable = cpk >= 0.10
    r['measurable'] = measurable
    res['beats'].append(r)
    gtxt = ', '.join(f'{v:+.0f}' for v in gl)
    gridmax = max([abs(p) for p in planned] + [0])
    if j['kind'] == 'beat':
        ok = (abs(lag) <= 20) if measurable else gridmax <= 20
    else:
        ok = True
    verdict = (f"onset cross-correlation lag {lag:+.0f} ms (peak correlation {cpk:.2f})" if measurable else
               f"no common pulse strong enough to measure (peak correlation {cpk:.2f} < 0.10, best lag {lag:+.0f} ms "
               f"is noise); the fitted beat grids agree within {gridmax:.0f} ms")
    print(f"beats {o['key']}->{i['key']} ({j['kind']}) window {wa:.2f}-{wb:.2f}: {verdict}; beat phase by onset, bass, "
          f"rise and chord change: out {po:+.0f} ms (strength {so:.2f}), in {pi_:+.0f} ms ({si:.2f}); per-beat onset gaps "
          f"[{gtxt}] ms, median {med:+.0f}; outgoing rhythmic activity in the blend {act:.2f} of its body -> {flag(ok)}")
# bodies in the final file
res['bodies'] = []
segs = P['segs']
for k, sg in enumerate(segs):
    if sg['key'] == '07b': continue
    a, b = B['info'][k]['body_window']        # the song's own stretch, between its blends
    seg = x[int(a * SR):int(b * SR)]
    e2 = subprocess.run(['ffmpeg', '-nostdin', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128',
                         '-f', 'null', '-'], input=seg.astype('<f8').tobytes(), capture_output=True).stderr.decode()
    Lb = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e2)[-1])
    res['bodies'].append(dict(key=sg['key'][:2], a=a, b=b, lufs=Lb))
Ls = [r['lufs'] for r in res['bodies']]
diffs = np.diff(Ls)
print('bodies: ' + ', '.join(f"{r['key']} {r['a']:.1f}-{r['b']:.1f} {r['lufs']:.1f}" for r in res['bodies']) +
      f" LUFS; neighbour steps {', '.join(f'{d:+.1f}' for d in diffs)}; rise first to last {Ls[-1] - Ls[0]:+.1f} dB, "
      f"max minus min {max(Ls) - min(Ls):.1f} dB -> {flag(np.all(np.abs(diffs) <= 1.0) and Ls[-1] - Ls[0] <= 3.3)}")
# context: how big are the songs' own 0.25 s steps inside their bodies (beats, accents)?
bsteps = []
for r_ in res['bodies']:
    c_, v_ = envat(r_['a'], r_['b'])
    st_ = [abs(v_[q + 5] - v_[q]) for q in range(len(v_) - 5)]
    if st_: bsteps.append((r_['key'], float(np.percentile(st_, 95)), float(max(st_))))
print('context, the songs\' own 0.25 s steps inside their bodies (95th percentile / largest): ' +
      ', '.join(f'{k} {p:.1f}/{mx:.1f} dB' for k, p, mx in bsteps))
res['body_steps'] = bsteps
# the lift by ear: K-weighted level and rhythmic activity before, in and after the breath
from scipy import signal as _sg
_A = 10 ** (4 / 40); _w = 2 * np.pi * 1681.97 / SR; _al = np.sin(_w) / (2 * 0.7071); _cw = np.cos(_w)
_b = [_A * ((_A + 1) + (_A - 1) * _cw + 2 * np.sqrt(_A) * _al), -2 * _A * ((_A - 1) + (_A + 1) * _cw),
      _A * ((_A + 1) + (_A - 1) * _cw - 2 * np.sqrt(_A) * _al)]
_a = [(_A + 1) - (_A - 1) * _cw + 2 * np.sqrt(_A) * _al, 2 * ((_A - 1) - (_A + 1) * _cw),
      (_A + 1) - (_A - 1) * _cw - 2 * np.sqrt(_A) * _al]
mk = _sg.lfilter(_b, _a, m)
kl = lambda a, b: 10 * np.log10(np.mean(mk[int(a * SR):int(b * SR)] ** 2) + 1e-20)
y22 = librosa.resample(m.astype(np.float32), orig_sr=SR, target_sr=22050)
on22 = librosa.onset.onset_strength(y=y22, sr=22050, hop_length=256); f22 = np.arange(len(on22)) * 256 / 22050
oa = lambda a, b: float(np.mean(on22[(f22 >= a) & (f22 < b)]))
wins = dict(before=(E - 2.4, E - 0.6), breath=(E + 0.3, Hh - 0.05), entrance=(Hh, Hh + 0.6), after=(Hh + 0.6, Hh + 2.6))
kv = {k_: kl(*v_) for k_, v_ in wins.items()}; av = {k_: oa(*v_) for k_, v_ in wins.items()}
lowb = _sg.sosfiltfilt(_sg.butter(4, 200, 'low', fs=SR, output='sos'), m)
lv = {k_: 10 * np.log10(np.mean(lowb[int(v_[0] * SR):int(v_[1] * SR)] ** 2) + 1e-20) for k_, v_ in wins.items()}
hit_on = float(on22[(f22 >= Hh - 0.05) & (f22 <= Hh + 0.12)].max() / np.median(on22))
rank = int(np.sum(on22 / np.median(on22) > hit_on))
print(f"lift by ear (K-weighted dB, relative to the body before): breath {kv['breath'] - kv['before']:+.1f}, entrance "
      f"{kv['entrance'] - kv['before']:+.1f}, climax body {kv['after'] - kv['before']:+.1f}; rhythmic activity (mean onset "
      f"strength) before {av['before']:.2f}, breath {av['breath']:.2f}, after {av['after']:.2f}; bass below 200 Hz "
      f"breath {lv['breath'] - lv['before']:+.1f} dB, climax {lv['after'] - lv['before']:+.1f} dB; onset at the hit "
      f"{hit_on:.1f}x the median ({rank} onset frames in the film are stronger)")
res['lift_ear'] = dict(k=kv, activity=av, low=lv, hit_onset=hit_on, hit_rank=rank)
# ending
F = P['end']['final']
cl, vl = envat(61.0, 61.9)
last = db(np.sqrt(np.mean(m[int(61.0 * SR):] ** 2))); lastpk = db(np.abs(m[int(61.0 * SR):]).max())
ce, ve = envat(F + 0.3, 61.9)
rise = float(max(ve[q + 5] - ve[q] for q in range(len(ve) - 5)))
tail = np.abs(x[-int(0.05 * SR):]).max()
print(f'ending: final chord {F:.2f} s, ring-out {P["total"] - F:.2f} s; last second RMS {last:.1f} dBFS, peak {lastpk:.1f} dBFS; '
      f'largest rise after the chord {rise:+.1f} dB; last 50 ms peak {db(tail):.1f} dBFS '
      f'-> {flag(P["total"] - F >= 4.0 and last < -45 and rise < 1.5)}')
res['ending'] = dict(final=F, ringout=P['total'] - F, last_rms=last, last_peak=lastpk, rise=rise)
# loudest moment (EBU momentary) and strongest hits
r = subprocess.run(['ffmpeg', '-nostdin', '-i', mp3, '-af', 'ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-',
                    '-f', 'null', '-'], capture_output=True, text=True)
ts, vs, t = [], [], None
for line in r.stdout.splitlines():
    mm = re.search(r'pts_time:([\d.]+)', line)
    if mm: t = float(mm.group(1))
    mm = re.search(r'lavfi.r128.M=(-?[\d.inf]+)', line)
    if mm and t is not None: ts.append(t - 0.2); vs.append(float(mm.group(1)))
ts, vs = np.array(ts), np.array(vs)
im = int(np.argmax(vs))
k3 = np.argmax(np.convolve(vs, np.ones(30) / 30, mode='same'))
print(f'loudest: momentary peak {vs[im]:.1f} LUFS at {ts[im]:.2f} s; loudest 3 s around {ts[k3]:.2f} s; '
      f'loudest 0.25 s RMS window at {cen[np.argmax(env)]:.2f} s ({env.max():.1f} dBFS)')
res['loudest'] = dict(M=float(vs[im]), t=float(ts[im]), t3=float(ts[k3]), rms_t=float(cen[np.argmax(env)]))
y22 = librosa.resample(m.astype(np.float32), orig_sr=SR, target_sr=22050)
on = librosa.onset.onset_strength(y=y22, sr=22050, hop_length=256)
fr = np.arange(len(on)) * 256 / 22050
pk = librosa.util.peak_pick(on, pre_max=20, post_max=20, pre_avg=40, post_avg=40, delta=0.5, wait=20)
top = sorted(pk, key=lambda q: -on[q])[:14]
res['hits'] = sorted([dict(t=float(fr[q]), s=float(on[q] / np.median(on))) for q in top], key=lambda d: d['t'])
print('strongest onsets: ' + ', '.join(f"{h['t']:.2f} ({h['s']:.1f}x)" for h in res['hits']))
print('ALL CHECKS ' + ('PASS' if res['ok'] else 'FAIL'))
json.dump(res, open(BASE + '.check.json', 'w'), indent=1)
