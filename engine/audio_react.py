"""Music reactivity and automatic timing (engine-audio, 2026-11-15).

The song's audio is analysed once, at load time, with numpy and an ffmpeg decode (no other dependency):

  level       slow loudness envelope, 0..1 (attack about 0.5 s, release about 1.6 s)
  beat        a smooth pulse on each beat, 0..1 (soft 0.07 s rise, 0.45 s decay; downbeats fuller, quiet beats small)
  brightness  spectral brightness (centroid), 0..1, smoothed
  onset       the raw onset strength (spectral flux), 0..1
  chorus      how loud the current section is, 0..1, crossfaded over about 1.5 s at section boundaries
  sections    section starts found from a novelty curve (self similarity, checkerboard kernel), snapped to beats

Everything is cached as arrays on a 100 per second grid. Song files can use the helpers inside Tracks or any
function of time:

    from audio_react import audio
    GLOW_EXTRA = lambda t: 0.2 * audio.level(t)
    audio.level(t), audio.beat(t), audio.brightness(t), audio.chorus(t), audio.section_starts(), audio.beats()

The song keys AUDIO_REACT, REACT_GLOW, REACT_SPARKLE, REACT_ARCH, REACT_AURORA and REACT_CHORUS (all optional,
all off by default) are applied by Reactor in render.py; see engine/UPGRADE-HOWTO.md, section P.

Which audio: the environment variable AUDIO (set by the Render workflow), else the song's AUDIO_FILE, else
work/<SONG>/audio.wav. Paths are relative to the repository root.
"""
import hashlib
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR, HOP, NFFT = 22050, 512, 2048
RATE = 100.0            # the cache grid: samples per second
VERSION = "a1"
KEYS = ("AUDIO_REACT", "REACT_GLOW", "REACT_SPARKLE", "REACT_ARCH", "REACT_AURORA", "REACT_CHORUS")
CAP = 0.25              # no reaction lifts anything by more than 25 percent


# ---------------------------------------------------------------- small numpy helpers
def _ss(a, b, x):
    u = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def follow(x, rate, attack, release):
    """One-pole follower with separate attack and release times (seconds)."""
    a = np.exp(-1.0 / (rate * max(attack, 1e-4)))
    r = np.exp(-1.0 / (rate * max(release, 1e-4)))
    y = np.empty(len(x))
    v = float(x[0]) if len(x) else 0.0
    for i, s in enumerate(x):
        k = a if s > v else r
        v = k * v + (1.0 - k) * s
        y[i] = v
    return y


def gauss(x, sigma):
    """Gaussian smoothing, sigma in samples."""
    if sigma <= 0.5 or len(x) < 3:
        return np.asarray(x, dtype=np.float64)
    n = int(sigma * 4) + 1
    k = np.exp(-0.5 * (np.arange(-n, n + 1) / sigma) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(x, n, mode="edge"), k, mode="valid")


def _norm(x, lo_p=5, hi_p=97, mask=None):
    v = x if mask is None or not mask.any() else x[mask]
    lo, hi = np.percentile(v, [lo_p, hi_p]) if len(v) else (0.0, 1.0)
    return np.clip((x - lo) / max(hi - lo, 1e-9), 0.0, 1.0)


def _local_max(x, half):
    """Indices where x is the maximum of its window of +-half samples."""
    n = len(x)
    if n == 0:
        return np.array([], dtype=int)
    p = np.pad(x, half, mode="constant", constant_values=-np.inf)
    w = np.lib.stride_tricks.sliding_window_view(p, 2 * half + 1)
    return np.nonzero(x >= w.max(axis=1))[0]


# ---------------------------------------------------------------- decoding and analysis
def decode(path, sr=SR):
    """Mono float32 samples through ffmpeg."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype="<f4").astype(np.float64)


def _spectrum(y):
    """Magnitude spectrogram (frames x bins) and the RMS of each frame, in chunks to keep memory small."""
    pad = np.pad(y, (NFFT // 2, NFFT // 2))
    n = max(1 + (len(pad) - NFFT) // HOP, 1)
    if len(pad) < NFFT:
        pad = np.pad(pad, (0, NFFT - len(pad)))
    win = np.hanning(NFFT)
    frames = np.lib.stride_tricks.sliding_window_view(pad, NFFT)[::HOP][:n]
    mag = np.empty((n, NFFT // 2 + 1), dtype=np.float32)
    rms = np.empty(n)
    for a in range(0, n, 1024):
        f = frames[a:a + 1024]
        rms[a:a + 1024] = np.sqrt((f ** 2).mean(axis=1))
        mag[a:a + 1024] = np.abs(np.fft.rfft(f * win, axis=1)).astype(np.float32)
    return mag, rms


def _beats(on, fr, tempo_prior=110.0):
    """Tempo by autocorrelation of the onset curve, then dynamic programming beat tracking (Ellis 2007)."""
    n = len(on)
    if n < fr * 4 or on.max() <= 0:
        return np.array([], dtype=int), 0.0
    o = on - on.mean()
    ac = np.correlate(o, o, mode="full")[n - 1:]
    lags = np.arange(len(ac))
    lo, hi = int(fr * 60 / 180), min(int(fr * 60 / 50), len(ac) - 1)
    bpm = 60.0 * fr / np.maximum(lags[lo:hi], 1)
    w = np.exp(-0.5 * (np.log2(bpm / tempo_prior) / 0.9) ** 2)
    period = lo + int(np.argmax(ac[lo:hi] * w))
    # refine with parabolic interpolation
    if 0 < period < len(ac) - 1:
        a, b, c = ac[period - 1], ac[period], ac[period + 1]
        d = (a - c) / (2 * (a - 2 * b + c)) if (a - 2 * b + c) != 0 else 0.0
        p = period + float(np.clip(d, -0.5, 0.5))
    else:
        p = float(period)
    tempo = 60.0 * fr / p
    loc = o / (o.std() + 1e-9)
    score = loc.copy()
    back = np.full(n, -1)
    j0, j1 = int(round(p * 0.5)), int(round(p * 2.0))
    offs = np.arange(j0, j1 + 1)
    pen = -100.0 * np.log(offs / p) ** 2
    for i in range(j0, n):
        js = i - offs
        ok = js >= 0
        if not ok.any():
            continue
        cand = score[js[ok]] + pen[ok]
        k = int(np.argmax(cand))
        score[i] = loc[i] + cand[k]
        back[i] = js[ok][k]
    # end on the best scoring frame in the last beat period
    tail = np.arange(max(n - int(p), 0), n)
    i = int(tail[np.argmax(score[tail])])
    out = []
    while i >= 0:
        out.append(i)
        i = back[i]
    return np.array(out[::-1], dtype=int), float(tempo)


def _chroma_bands(mag, freqs):
    """24 log spaced band energies (60 Hz to 8 kHz) and a 12 bin pitch class profile, both log compressed."""
    edges = np.geomspace(60.0, 8000.0, 25)
    bidx = np.digitize(freqs, edges) - 1
    bands = np.zeros((mag.shape[0], 24))
    p = mag.astype(np.float64) ** 2
    for b in range(24):
        m = bidx == b
        if m.any():
            bands[:, b] = p[:, m].mean(axis=1)
    sel = (freqs >= 55.0) & (freqs <= 5000.0)
    pc = np.round(12 * np.log2(freqs[sel] / 440.0)).astype(int) % 12
    chroma = np.zeros((mag.shape[0], 12))
    ps = p[:, sel]
    for k in range(12):
        chroma[:, k] = ps[:, pc == k].sum(axis=1)
    chroma /= chroma.sum(axis=1, keepdims=True) + 1e-12
    return np.log1p(bands * 1e3), chroma


def _sections(feat, loud, fr, min_len=8.0, kernel_s=6.0):
    """Section starts (in analysis frames) from a novelty curve on 0.5 s windows."""
    step = max(int(round(fr * 0.5)), 1)
    nw = feat.shape[0] // step
    if nw < 8:
        return np.array([0]), np.zeros(feat.shape[0])
    X = feat[:nw * step].reshape(nw, step, -1).mean(axis=1)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    Sm = X @ X.T
    L = max(int(kernel_s / 0.5), 2)
    g = np.exp(-0.5 * ((np.arange(-L, L) + 0.5) / (0.5 * L)) ** 2)
    sign = np.sign(np.arange(-L, L) + 0.5)
    K = np.outer(g, g) * np.outer(sign, sign)
    P = np.pad(Sm, L, mode="edge")
    nov = np.array([float((K * P[i:i + 2 * L, i:i + 2 * L]).sum()) for i in range(nw)])
    nov = np.maximum(nov, 0.0)
    lw = loud[:nw * step].reshape(nw, step).mean(axis=1)
    d = np.zeros(nw)
    for i in range(nw):
        a, b = lw[max(i - 8, 0):i], lw[i:i + 8]
        if len(a) and len(b):
            d[i] = abs(b.mean() - a.mean())
    nov = nov / (nov.max() + 1e-9) * 0.75 + d / (d.max() + 1e-9) * 0.25
    nov = gauss(nov, 1.0)
    half = int(min_len / 0.5 / 2)
    pk = _local_max(nov, half)
    thr = nov.mean() + 0.35 * nov.std()
    pk = [int(i) for i in pk if nov[i] > thr and 2.0 / 0.5 <= i <= nw - 4.0 / 0.5]
    keep = []
    for i in sorted(pk, key=lambda i: -nov[i]):
        if all(abs(i - k) * 0.5 >= min_len for k in keep):
            keep.append(i)
    starts = np.array([0] + sorted(keep)) * step
    curve = np.interp(np.arange(feat.shape[0]), np.arange(nw) * step + step / 2, nov)
    return starts, curve


def analyse(y, sr=SR):
    """All features of a mono signal. Returns a dict of arrays on the RATE grid plus event lists (seconds)."""
    dur = len(y) / sr
    fr = sr / HOP
    grid = np.arange(int(np.ceil(dur * RATE)) + 1) / RATE
    if len(y) < NFFT or float(np.max(np.abs(y))) < 1e-4:
        z = np.zeros(len(grid))
        return dict(dur=dur, tempo=0.0, grid=grid, level=z, beat=z, bright=z, onset=z, chorus=z, novelty=z,
                    beats=np.array([]), downbeats=np.array([]), strong=np.array([]), onsets=np.array([]),
                    sections=np.array([0.0]))
    mag, rms = _spectrum(y)
    nf = mag.shape[0]
    ft = np.arange(nf) / fr
    freqs = np.fft.rfftfreq(NFFT, 1.0 / sr)
    db = 20 * np.log10(np.maximum(rms, 1e-7))
    active = db > db.max() - 45
    loud = _norm(db, 10, 97, active)
    level = follow(loud, fr, 0.5, 1.6)
    # onsets: positive spectral flux on a compressed spectrum
    lm = np.log1p(100.0 * mag[:, freqs >= 30.0])
    flux = np.concatenate([[0.0], np.maximum(np.diff(lm, axis=0), 0.0).mean(axis=1)])
    onset = np.clip(flux / (np.percentile(flux, 99) + 1e-9), 0.0, 1.5)
    base = gauss(onset, fr * 0.25)
    pk = _local_max(onset, 3)
    ons = [i for i in pk if onset[i] > base[i] + 0.12]
    keep, last = [], -1e9
    for i in ons:
        if i - last >= 0.1 * fr:
            keep.append(i)
            last = i
    onsets = ft[np.array(keep, dtype=int)] if keep else np.array([])
    # beats, their strength and the bar phase
    bidx, tempo = _beats(gauss(onset, 1.0), fr)
    while tempo > 115.0 and len(bidx) > 4:
        # calm, slow: a fast pulse is counted in half time (the stronger of the two phases)
        ph2 = int(np.argmax([onset[bidx[k::2]].mean() for k in range(2)]))
        bidx, tempo = bidx[ph2::2], tempo / 2.0
    if len(bidx):
        st = np.array([onset[max(i - 2, 0):i + 3].max() for i in bidx])
        st = np.clip(st / (np.percentile(st, 95) + 1e-9), 0.0, 1.0)
        low = _norm(np.log1p(mag[:, freqs < 200.0].mean(axis=1)), 5, 97)
        lowb = low[bidx]
        ph = int(np.argmax([(st[k::4] + lowb[k::4]).mean() if len(st[k::4]) else -1 for k in range(4)]))
        down = np.zeros(len(bidx), dtype=bool)
        down[ph::4] = True
        lv = level[bidx]
        amp = np.where(down, 0.65 + 0.35 * st, 0.35 + 0.40 * st) * (0.35 + 0.65 * lv)
        beats = ft[bidx]
    else:
        st, down, amp, beats = np.array([]), np.array([], dtype=bool), np.array([]), np.array([])
    # the beat pulse: soft rise, slow decay, never a hard flash
    pulse = np.zeros(len(grid))
    rise, decay = 0.07, 0.45
    for b, a in zip(beats, amp):
        i0 = int(b * RATE)
        i1 = min(i0 + int(decay * 6 * RATE), len(grid))
        u = grid[i0:i1] - b
        env = _ss(0.0, rise, u + rise * 0.5) * np.exp(-np.maximum(u, 0.0) / decay)
        pulse[i0:i1] = np.maximum(pulse[i0:i1], a * env)
    pulse = np.clip(pulse, 0.0, 1.0)
    # spectral brightness
    m = mag.astype(np.float64)
    cent = (m * freqs).sum(axis=1) / (m.sum(axis=1) + 1e-9)
    bright = _norm(np.log2(np.maximum(cent, 50.0)), 5, 95, active)
    bright = gauss(bright, fr * 0.4) * (loud > 0.02)
    bright = gauss(bright, fr * 0.2)
    # sections
    bands, chroma = _chroma_bands(mag, freqs)
    feat = np.hstack([bands, chroma * 3.0, loud[:, None] * 2.0])
    sidx, nov = _sections(feat, loud, fr)
    secs = ft[np.minimum(sidx, nf - 1)]
    downs = beats[down] if len(beats) else np.array([])
    snapped = [0.0]
    for s in secs[1:]:
        c = downs[np.abs(downs - s) <= 1.0] if len(downs) else []
        if len(c) == 0 and len(beats):
            c = beats[np.abs(beats - s) <= 0.6]
        snapped.append(float(c[np.argmin(np.abs(c - s))]) if len(c) else float(s))
    sections = np.unique(np.round(snapped, 3))
    # how loud each section is (chorus amount), crossfaded at the boundaries
    lev_grid = np.interp(grid, ft, level)
    sec_i = np.searchsorted(sections, grid, side="right") - 1
    means = np.array([lev_grid[sec_i == k].mean() if (sec_i == k).any() else 0.0 for k in range(len(sections))])
    chorus = _ss(0.50, 0.80, means[np.clip(sec_i, 0, len(means) - 1)])
    chorus = gauss(chorus, 0.75 * RATE)
    strong = downs[np.interp(downs, beats, st) >= 0.3] if len(downs) else np.array([])
    return dict(dur=dur, tempo=tempo, grid=grid, level=lev_grid,
                beat=pulse, bright=np.interp(grid, ft, bright), onset=np.interp(grid, ft, np.clip(onset, 0, 1)),
                chorus=chorus, novelty=np.interp(grid, ft, nov), beats=beats, downbeats=downs, strong=strong,
                onsets=onsets, sections=sections, beat_strength=st, section_level=means)


# ---------------------------------------------------------------- the shared helper object
def _resolve_path():
    p = os.environ.get("AUDIO") or os.environ.get("AUDIO_FILE")
    if not p:
        S = sys.modules.get("song")
        p = getattr(S, "AUDIO_FILE", None) if S is not None else None
    if not p:
        p = os.path.join("work", os.environ.get("SONG", "s03_original"), "audio.wav")
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


class Audio:
    """Lazy, cached analysis of one audio file. Every helper is safe to call before load(): it loads on first use.
    Times outside the audio give 0 (silence)."""

    def __init__(self, path=None):
        self.path = path
        self.d = None

    def load(self, path=None, cache=True):
        if path is not None:
            self.path, self.d = path, None
        if self.d is not None:
            return self
        p = self.path or _resolve_path()
        self.path = p
        if not os.path.exists(p):
            print(f"audio_react: no audio at {p}, music reactivity is silent", file=sys.stderr, flush=True)
            self.d = analyse(np.zeros(SR))
            return self
        st = os.stat(p)
        key = hashlib.sha1(f"{VERSION}|{os.path.abspath(p)}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:16]
        cpath = os.path.join(ROOT, "work", "audio_react", key + ".npz")
        if cache and os.path.exists(cpath):
            z = np.load(cpath)
            self.d = {k: (float(z[k]) if z[k].ndim == 0 else z[k]) for k in z.files}
            return self
        self.d = analyse(decode(p))
        if cache:
            try:
                os.makedirs(os.path.dirname(cpath), exist_ok=True)
                np.savez_compressed(cpath, **self.d)
            except OSError:
                pass
        return self

    def _at(self, name, t):
        d = self.load().d
        g = d["grid"]
        return float(np.interp(t, g, d[name], left=0.0, right=0.0))

    # the helpers for song files
    def level(self, t):
        """Slow loudness, 0..1."""
        return self._at("level", t)

    def beat(self, t):
        """Smooth beat pulse, 0..1 (0.45 s decay)."""
        return self._at("beat", t)

    def brightness(self, t):
        """Spectral brightness, 0..1."""
        return self._at("bright", t)

    def onset(self, t):
        return self._at("onset", t)

    def chorus(self, t):
        """How loud the current section is, 0..1 (1 in the loudest sections)."""
        return self._at("chorus", t)

    def section_starts(self):
        return [float(x) for x in self.load().d["sections"]]

    def beats(self):
        return [float(x) for x in self.load().d["beats"]]

    def downbeats(self):
        return [float(x) for x in self.load().d["downbeats"]]

    def strong_beats(self):
        return [float(x) for x in self.load().d["strong"]]

    def onsets(self):
        return [float(x) for x in self.load().d["onsets"]]

    @property
    def tempo(self):
        return float(self.load().d["tempo"])

    @property
    def duration(self):
        return float(self.load().d["dur"])


audio = Audio()


# ---------------------------------------------------------------- the song keys, applied by render.py
def _song():
    return sys.modules.get("song")


def enabled():
    S = _song()
    return S is not None and any(getattr(S, k, None) is not None for k in KEYS)


def _val(name, t, default):
    v = getattr(_song(), name, None)
    if v is None:
        return default
    return float(v(t) if callable(v) else v)


def amounts(t):
    """The master and the five amounts at t, each 0..1. With any REACT_* key set, AUDIO_REACT defaults to 1."""
    S = _song()
    any_react = any(getattr(S, k, None) is not None for k in KEYS[1:])
    m = min(max(_val("AUDIO_REACT", t, 1.0 if any_react else 0.0), 0.0), 1.0)
    out = {}
    for k in KEYS[1:]:
        out[k] = min(max(_val(k, t, 0.0), 0.0), 1.0) * m
    return out


def setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v


class Reactor:
    """Applies the REACT_* keys to the frame parameters and draws the beat sparkle. Made by render.py only when
    the song sets one of the keys, so songs without them render exactly as before."""

    def __init__(self, R):
        import moderngl
        self.R = R
        self.moderngl = moderngl
        audio.load()
        d = audio.d
        print(f"audio_react: {audio.path}: {d['dur']:.1f} s, tempo {d['tempo']:.1f} bpm, {len(d['beats'])} beats, "
              f"sections {[round(float(x), 1) for x in d['sections']]}", flush=True)
        seeds = np.random.default_rng(77).random((900, 4)).astype("f4")
        self.v_spark = R.ctx.vertex_array(R.p_mote, [(R.ctx.buffer(seeds.tobytes()), "4f", "aSeed")])

    def apply(self, P, t):
        a = amounts(t)
        lvl, bt, ch, br = audio.level(t), audio.beat(t), audio.chorus(t), audio.brightness(t)
        P = dict(P)
        # overall light swells with loudness; a loud section adds a little more, never past +25 percent
        g = 1.0 + min(CAP, CAP * a["REACT_GLOW"] * lvl + 0.10 * a["REACT_CHORUS"] * ch)
        P["glow"] = np.asarray(P["glow"]) * g
        P["rays"] = P["rays"] * g
        # aurora and sky intensity follow loudness (and a touch of brightness)
        k = a["REACT_AURORA"] * (0.7 * lvl + 0.3 * br)
        P["aurora"] = P["aurora"] * (1.0 + CAP * k)
        P["milky"] = P["milky"] * (1.0 + 0.20 * k)
        P["sky_top"] = np.asarray(P["sky_top"]) * (1.0 + 0.10 * k)
        P["sky_mid"] = np.asarray(P["sky_mid"]) * (1.0 + 0.14 * k)
        # the arch lights pulse gently on the beat
        ka = 0.22 * a["REACT_ARCH"] * bt
        if ka > 0.0:
            P["star"] = [(s[0] * (1.0 + ka),) + tuple(s[1:]) if s[0] > 0.001 else s for s in P["star"]]
        # a few more motes on the beat; the sparkle layer itself is drawn in draw()
        P["motes"] = P["motes"] * (1.0 + 0.15 * a["REACT_SPARKLE"] * bt)
        P["react_sparkle"] = a["REACT_SPARKLE"] * (0.12 * lvl + 0.88 * bt)
        P["react_sparkle_amt"] = a["REACT_SPARKLE"]
        # a bigger bloom in the loud sections
        P["bloom_gain"] = 1.0 + CAP * a["REACT_CHORUS"] * ch
        return P

    def draw(self, t, P):
        s = P.get("react_sparkle", 0.0)
        if s <= 0.002:
            return
        L = self.R
        S = _song()
        cal = getattr(S, "BOTTOM_CALM", 0.0)
        cal = float(cal(t) if callable(cal) else cal)
        lin = S.lin
        setu(L.p_mote, uT=t + 311.0, uAmount=0.25 + 0.35 * P.get("react_sparkle_amt", 0.0), uPx=L.px, uSizeMin=2.0,
             uSizeMax=9.0, uPeriod=46.0, uY0=0.30, uY1=1.06, uSway=0.02, uBright=1.15 * min(s, 1.0),
             uColA=lin("#fff3d8"), uColB=lin("#ffd08a"), uCalm=max(cal, 0.85), uCalmY=0.335)
        self.v_spark.render(self.moderngl.POINTS)
