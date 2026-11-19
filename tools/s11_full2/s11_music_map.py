"""Song 11 v2: the music map. What every instrument and voice is doing, measured on the recording, as time series
at 60 Hz for the music effects (tools/s11_full2/s11_music_fx.py).

    python3 tools/s11_full2/s11_music_map.py            # reads work/s11_full2/score.wav
    S11_AUDIO=/path/to/score.wav python3 tools/s11_full2/s11_music_map.py [--out work/s11_full2/music_fx.npz]

Writes work/s11_full2/music_fx.npz (untracked, never into git; the render machines receive it beside
features.npz). Film time 0 is file time 0. Deterministic: librosa only (STFT, harmonic and percussive separation,
band energies, onset strength, beat tracking, pyin on the harmonic part); no models, no randomness.

Series (all 0..1 unless noted, sampled on `times`, 60 per second):
  bass       low band (30 to 150 Hz) envelope: the bass and the kick, how loud the low end is now
  bass_rel   the low end against its own last 8 s (it rises when the bass steps in, even in quiet parts)
  kick       a pulse on each low percussive onset (decays in about 0.15 s); kick_t, kick_s: the onsets
  timp       a pulse on each big low drum hit (timpani: strong 50 to 250 Hz percussive onsets that ring)
             timp_t, timp_s: the hits
  strings    sustained mid band (200 to 2000 Hz) harmonic energy, smoothed: the strings' bed
  swell      how fast the strings are rising (the swells), 0 when steady or falling
  brass      bright harmonic energy (1 to 4.5 kHz) above its local level; brass_hit, brass_t: bright onsets
  choir      voiced presence: pyin's voiced probability on the harmonic part times the vocal band level
  high       high voices (sopranos and altos): voiced energy 500 to 2000 Hz, and the sung pitch above 400 Hz
  low        low voices (tenors and basses): voiced energy 100 to 350 Hz, and the sung pitch below 350 Hz
  f0         the leading sung pitch in Hz (0 where unvoiced)
  level      overall loudness
  beat_t     the beat grid (seconds); beat: a pulse on each beat; down_t: every 4th beat (bar starts, estimated)
No em dash or en dash anywhere in this file.
"""
import argparse
import os
from pathlib import Path

import numpy as np
import librosa
import scipy.ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work/s11_full2"
SR = 24000
HOP = 400                    # 60 frames per second exactly
NFFT = 2048
FPS = SR / HOP


MUSIC = None                 # frames inside the music (0.84 s to 259.95 s): the percentiles are taken there


def _norm(x, lo=5.0, hi=98.0):
    v = x[MUSIC] if MUSIC is not None and len(MUSIC) == len(x) else x
    a, b = np.percentile(v, lo), np.percentile(v, hi)
    return np.clip((x - a) / max(b - a, 1e-12), 0.0, 1.0)


def _smooth(x, sec):
    n = max(int(round(sec * FPS)), 1)
    return ndi.uniform_filter1d(x, n, mode="nearest")


def _band(S, freqs, lo, hi):
    m = (freqs >= lo) & (freqs < hi)
    return S[m].sum(axis=0)


def _db(x):
    return 10.0 * np.log10(np.maximum(x, 1e-10))


def _rel(x, sec, lo=10.0):
    """x against its own recent level (a rolling low percentile): steps and swells stand out in quiet parts."""
    n = max(int(sec * FPS), 3)
    base = ndi.percentile_filter(x, lo, size=n, mode="nearest")
    return np.maximum(x - base, 0.0)


def _pulses(times, t_on, strength, fall):
    """A pulse series: each onset jumps to its strength and decays with time constant `fall`."""
    out = np.zeros_like(times)
    for t0, s in zip(t_on, strength):
        i0 = int(np.searchsorted(times, t0))
        i1 = min(len(times), i0 + int(6 * fall * FPS) + 2)
        d = times[i0:i1] - t0
        out[i0:i1] = np.maximum(out[i0:i1], s * np.exp(-np.maximum(d, 0.0) / fall))
    return out


def _peaks(env, thresh, gap):
    """Local maxima of env above thresh, at least `gap` seconds apart (strongest first)."""
    w = max(int(gap * FPS), 1)
    mx = ndi.maximum_filter1d(env, 2 * w + 1, mode="nearest")
    idx = np.flatnonzero((env >= mx) & (env > thresh))
    keep = []
    for i in idx[np.argsort(-env[idx], kind="stable")]:
        if all(abs(i - j) > w for j in keep):
            keep.append(i)
    return np.array(sorted(keep), int)


def analyse(path, out):
    y, _ = librosa.load(str(path), sr=SR, mono=True)
    D = librosa.stft(y, n_fft=NFFT, hop_length=HOP, center=True)
    S = np.abs(D) ** 2
    freqs = librosa.fft_frequencies(sr=SR, n_fft=NFFT)
    n = S.shape[1]
    times = np.arange(n) / FPS
    global MUSIC
    MUSIC = (times >= 0.84) & (times <= 259.95)
    H, P = librosa.decompose.hpss(S, kernel_size=(31, 31), margin=1.0)
    total = S.sum(axis=0) + 1e-10
    level = _norm(_db(total), 5, 99.5)
    quiet = level < 0.05

    # the low end: bass and kick
    low_all = _band(S, freqs, 30, 150)
    bass = _norm(_db(_smooth(low_all, 0.05)), 20, 99.5)
    bass_rel = _norm(_rel(_db(_smooth(low_all, 0.08)), 8.0), 0, 99)
    low_p = _band(P, freqs, 30, 120)
    flux = np.maximum(np.diff(_db(low_p), prepend=_db(low_p[:1])), 0.0)
    flux = _smooth(flux, 0.03)
    k_env = _norm(flux, 50, 99.7)
    k_env[quiet] = 0.0
    ki = _peaks(k_env, 0.25, 0.18)
    kick_t, kick_s = times[ki], k_env[ki]
    kick = _pulses(times, kick_t, kick_s, 0.15)

    # timpani: big low percussive onsets that ring on (energy still there 0.2 s later)
    tp = _band(P, freqs, 50, 250) + 0.5 * _band(H, freqs, 60, 200)
    tflux = _smooth(np.maximum(np.diff(_db(tp), prepend=_db(tp[:1])), 0.0), 0.03)
    t_env = _norm(tflux, 50, 99.8)
    ring = _db(_smooth(tp, 0.2))
    lag = int(0.2 * FPS)
    sustain = np.concatenate([ring[lag:], np.full(lag, ring[-1])]) - _db(_smooth(tp, 0.6))
    t_env = t_env * np.clip(1.0 + sustain / 6.0, 0.3, 1.2) * np.clip(level * 1.5, 0.0, 1.0)
    ti = _peaks(t_env, np.percentile(t_env, 99.0), 0.35)
    timp_t = times[ti]
    timp_s = np.clip(t_env[ti] / max(np.percentile(t_env[ti], 90), 1e-6), 0.0, 1.0) if len(ti) else np.zeros(0)
    timp = _pulses(times, timp_t, timp_s, 0.45)

    # strings: the sustained mid band of the harmonic part
    mid_h = _band(H, freqs, 200, 2000)
    strings = _norm(_db(_smooth(mid_h, 0.5)), 10, 99.5)
    st = _smooth(strings, 1.0)
    swell = np.maximum(np.gradient(st) * FPS, 0.0)
    swell = _norm(_smooth(swell, 0.6), 30, 99.5)

    # brass: bright harmonic energy over its local level, and its onsets
    br = _band(H, freqs, 1000, 4500)
    share = br / (_band(H, freqs, 100, 4500) + 1e-10)
    brass = _norm(_db(_smooth(br, 0.15)), 30, 99.7) * _norm(_smooth(share, 0.3), 10, 99)
    brass = _norm(brass, 5, 99.5)
    bflux = _smooth(np.maximum(np.diff(_db(br), prepend=_db(br[:1])), 0.0), 0.04)
    b_env = _norm(bflux, 60, 99.7) * np.clip(brass * 2.0, 0.0, 1.0)
    bi = _peaks(b_env, 0.35, 0.25)
    brass_t = times[bi]
    brass_hit = _pulses(times, brass_t, b_env[bi], 0.35)

    # voices: pyin on the harmonic part (the leading sung line) and the voiced bands
    yh = librosa.istft(np.sqrt(H) * np.exp(1j * np.angle(D)), hop_length=HOP, length=len(y))
    y11 = librosa.resample(yh, orig_sr=SR, target_sr=12000)
    f0, vflag, vprob = librosa.pyin(y11, fmin=80.0, fmax=1100.0, sr=12000, frame_length=1024, hop_length=200,
                                    center=True)
    f0 = np.nan_to_num(f0, nan=0.0)
    f0 = np.interp(times, np.arange(len(f0)) * 200 / 12000, f0)[:n]
    vprob = np.interp(times, np.arange(len(vprob)) * 200 / 12000, vprob)[:n]
    voc = _band(H, freqs, 250, 3500)
    vsm = np.clip(_smooth(vprob, 0.4) * 2.0, 0.0, 1.0)
    choir = _norm(_db(_smooth(voc, 0.3)), 15, 99.5) * (0.45 + 0.55 * vsm)
    choir = _norm(choir, 5, 99.5)
    sing = np.clip(choir * 2.5, 0.0, 1.0)          # the voices gate (the low band also carries the bass line)
    hi_b = _band(H, freqs, 500, 2000)
    lo_b = _band(H, freqs, 100, 350)
    hi_share = hi_b / (hi_b + lo_b + 1e-10)
    pitch_hi = np.clip((f0 - 330.0) / 220.0, 0.0, 1.0) * (f0 > 0)
    pitch_lo = np.clip((380.0 - f0) / 160.0, 0.0, 1.0) * (f0 > 0)
    vs = np.clip(_smooth(vprob, 0.3) * 1.5, 0.0, 1.0)
    high = _norm(_db(_smooth(hi_b, 0.25)), 20, 99.5) * (0.35 + 0.65 * _norm(_smooth(hi_share, 0.5), 5, 95))
    high = _norm(_smooth(sing * (high * (0.6 + 0.4 * vs) + 0.3 * _smooth(pitch_hi, 0.3) * vs), 0.15), 3, 99.5)
    low = _norm(_db(_smooth(lo_b, 0.25)), 20, 99.5) * (0.35 + 0.65 * _norm(_smooth(1.0 - hi_share, 0.5), 5, 95))
    low = _norm(_smooth(sing * (low * (0.6 + 0.4 * vs) + 0.3 * _smooth(pitch_lo, 0.3) * vs), 0.15), 3, 99.5)

    # the beat grid
    oenv = librosa.onset.onset_strength(S=librosa.power_to_db(S, ref=np.max), sr=SR)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=SR, hop_length=HOP, start_bpm=125.0, tightness=120,
                                           trim=False)
    beat_t = times[beats]
    beat_t = beat_t[(beat_t > 0.5) & (beat_t < 260.0)]
    beat = _pulses(times, beat_t, np.ones(len(beat_t)), 0.09)
    # bar starts: the phase of 4 that carries the most low energy
    if len(beat_t) >= 8:
        lows = np.interp(beat_t, times, kick + 0.5 * bass)
        ph = int(np.argmax([lows[k::4].mean() for k in range(4)]))
        down_t = beat_t[ph::4]
    else:
        down_t = beat_t

    f32 = lambda a: np.asarray(a, np.float32)  # noqa: E731
    np.savez_compressed(out, times=f32(times), fps=np.float32(FPS), level=f32(level), bass=f32(bass),
                        bass_rel=f32(bass_rel), kick=f32(kick), kick_t=f32(kick_t), kick_s=f32(kick_s),
                        timp=f32(timp), timp_t=f32(timp_t), timp_s=f32(timp_s), strings=f32(strings),
                        swell=f32(swell), brass=f32(brass), brass_hit=f32(brass_hit), brass_t=f32(brass_t),
                        choir=f32(choir), high=f32(high), low=f32(low), f0=f32(f0), beat=f32(beat),
                        beat_t=f32(beat_t), down_t=f32(down_t), tempo=np.float32(np.atleast_1d(tempo)[0]))
    print(f"music map: {out} ({n} frames, {len(kick_t)} kicks, {len(timp_t)} timpani hits, {len(brass_t)} brass "
          f"onsets, {len(beat_t)} beats, tempo {float(np.atleast_1d(tempo)[0]):.1f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", type=Path, default=Path(os.environ.get("S11_AUDIO", str(WORK / "score.wav"))))
    ap.add_argument("--out", type=Path, default=WORK / "music_fx.npz")
    a = ap.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    analyse(a.audio, a.out)


if __name__ == "__main__":
    main()
