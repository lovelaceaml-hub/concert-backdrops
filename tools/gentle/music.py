"""Reproducible seven-recording edit for A World Made Gentle.

Source recordings are read only. Generated audio and analysis stay under work/.
The common 112 bpm pulse uses a dotted-quarter interpretation for the three
compound-meter selections. All stretching preserves pitch through ffmpeg atempo.
"""
from pathlib import Path
import json
import subprocess
import os

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/gentle'
os.environ.setdefault('NUMBA_CACHE_DIR', str(WORK/'numba'))

import librosa
import numpy as np
from scipy.signal import butter, sosfiltfilt
from scipy.ndimage import gaussian_filter1d
import soundfile as sf

RATE = 48000
TOTAL = 62.0
BPM = 112.0
BAR = 240.0 / BPM
ORDER = ['s09', 's08', 's04', 's05', 's11', 's01', 's03']
TEMPO = dict(s09=161.4990234375, s08=151.99908088235293,
             s04=151.99908088235293, s05=99.38401442307692,
             s11=103.359375, s01=117.45383522727273, s03=123.046875)
METER = dict(s09=2/3, s08=2/3, s04=2/3)
PREFERRED = [22.0, 27.8, 39.0, 40.0, 39.0, 34.3]
STARTS = [2.0 + 4 * BAR * i for i in range(7)]
FINAL_CHORD = 57.5
SOURCE_FINAL_CHORD = 55.145


def decode(name, rate=RATE):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i',
        str(ROOT / f'audio/promo/{name}.mp3'), '-ar', str(rate), '-ac', '2', '-f', 'f32le', '-'])
    return np.frombuffer(raw, '<f4').reshape(-1, 2).copy()


def analysis(name):
    path = WORK / f'{name}-analysis.npz'
    if not path.exists():
        y = decode(name, 22050).mean(axis=1)
        onset = librosa.onset.onset_strength(y=y, sr=22050)
        _, beats = librosa.beat.beat_track(onset_envelope=onset, sr=22050, trim=False)
        np.savez_compressed(path, beats=librosa.frames_to_time(beats, sr=22050),
            chroma=librosa.feature.chroma_stft(y=y, sr=22050),
            rms=librosa.feature.rms(y=y)[0], onset=onset)
    return np.load(path)


def color(d, a, b):
    i, j = max(0, round(a*22050/512)), round(b*22050/512)
    c = d['chroma'][:, i:max(i+1, j)].mean(axis=1)
    return c / max(float(np.linalg.norm(c)), 1e-9)


def select():
    """Choose bar candidates for harmonic continuity, without copying another mix."""
    candidates, descriptors = [], []
    for i, name in enumerate(ORDER):
        d = analysis(name)
        rate = BPM / (TEMPO[name] * METER.get(name, 1.0))
        duration = (STARTS[i+1] if i < 6 else TOTAL) - STARTS[i]
        if i == 6:
            starts = [SOURCE_FINAL_CHORD - (FINAL_CHORD - STARTS[i])*rate]
        else:
            stride = 6 if name in METER else 4
            starts = [float(t) for t in d['beats'][::stride]
                      if abs(t-PREFERRED[i]) < 8 and t > 2 and t+(duration+BAR/2)*rate < 59.5]
        if not starts:
            raise RuntimeError(f'No safe excerpt for {name}')
        candidates.append(starts)
        descriptors.append([(color(d, s, s+BAR*rate),
                             color(d, s+(duration-BAR)*rate, s+duration*rate)) for s in starts])
    costs = [np.array([0.012*abs(s-PREFERRED[0]) for s in candidates[0]])]
    parents = []
    for i in range(1, 7):
        matrix = np.array([[costs[-1][j] + 1-float(np.dot(a[1], b[0]))
                            + (0.012*abs(candidates[i][k]-PREFERRED[i]) if i<6 else 0)
                            for k,b in enumerate(descriptors[i])]
                           for j,a in enumerate(descriptors[i-1])])
        parents.append(matrix.argmin(axis=0))
        costs.append(matrix.min(axis=0))
    selected = [int(costs[-1].argmin())]
    for parent in parents[::-1]:
        selected.append(int(parent[selected[-1]]))
    selected.reverse()
    return [row[index] for row,index in zip(candidates, selected)]


def db(x):
    return float(20*np.log10(max(float(np.sqrt(np.mean(np.asarray(x)**2))), 1e-12)))


def build():
    WORK.mkdir(parents=True, exist_ok=True)
    source_starts = select()
    mix = np.zeros((round(RATE*TOTAL), 2), np.float64)
    rows = []
    lowpass = butter(2, 180, fs=RATE, output='sos')
    for i, (name, source) in enumerate(zip(ORDER, source_starts)):
        rate = BPM / (TEMPO[name] * METER.get(name, 1.0))
        start, end = STARTS[i], STARTS[i+1] if i<6 else TOTAL
        lo, hi = start-(BAR/2 if i else 0), end+(BAR/2 if i<6 else 0)
        source_lo = source + (lo-start)*rate
        count = round((hi-lo)*RATE)
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i',
            str(ROOT / f'audio/promo/{name}.mp3'), '-ss', f'{source_lo:.9f}',
            '-af', f'atempo={rate:.12f}', '-t', f'{hi-lo+0.1:.9f}',
            '-ar', str(RATE), '-ac', '2', '-f', 'f32le', '-'])
        clip = np.frombuffer(raw, '<f4').reshape(-1, 2)[:count].astype(np.float64)
        if len(clip) != count:
            raise RuntimeError(f'{name}: excerpt too short')
        gain = float(np.clip(-18.5-db(clip), -18, 12))
        clip *= 10**(gain/20)
        tt = np.arange(count)/RATE+lo
        env = np.ones(count)
        bass_env = np.ones(count)
        if i:
            u = np.clip((tt-lo)/BAR, 0, 1)
            env *= np.sin(u*np.pi/2)
            bass_env *= np.sin(u*np.pi/2)**1.6
        else:
            env *= np.sin(np.clip((tt-start)/1.5,0,1)*np.pi/2)**2
            bass_env = env.copy()
        if i<6:
            u = np.clip((tt-(end-BAR/2))/BAR,0,1)
            env *= np.cos(u*np.pi/2)
            bass_env *= np.cos(u*np.pi/2)**1.6
        else:
            tail = np.cos(np.clip((tt-58.5)/3.3,0,1)*np.pi/2)**4
            env *= tail
            bass_env *= tail
        bass = sosfiltfilt(lowpass, clip, axis=0)
        clip = (clip-bass)*env[:,None]+bass*bass_env[:,None]
        first = round(lo*RATE)
        mix[first:first+count] += clip
        rows.append(dict(source=name, source_start=source, film_start=start,
                         film_end=end, tempo_factor=rate, effective_source_bpm=TEMPO[name]*METER.get(name,1),
                         gain_db=gain, overlap_seconds=BAR))
    # A slow gain handoff matches the actual boundary phrases, rather than
    # assuming matching each excerpt's overall RMS also matches its endpoints.
    times = np.arange(len(mix))/RATE
    correction = np.zeros(len(mix))
    for t in STARTS[1:]:
        a = db(mix[round((t-1.0)*RATE):round((t-.25)*RATE)])
        b = db(mix[round((t+.25)*RATE):round((t+1.0)*RATE)])
        delta = float(np.clip((b-a)*0.65,-3,3))
        correction += np.interp(times,[t-2.2,t-.9,t-.35,t+.35,t+.9,t+2.2],
                                 [0,delta,delta,-delta,-delta,0],left=0,right=0)
    # Smooth a compact envelope, then upsample it, avoiding per-sample convolution.
    grid = np.arange(0,len(mix),480)
    smooth = gaussian_filter1d(correction[grid],12,mode='nearest')
    mix *= 10**(np.interp(np.arange(len(mix)),grid,smooth)[:,None]/20)
    # Brief level riding around the blends also handles a quiet pickup followed
    # by a loud downbeat inside an otherwise well-matched pair of excerpts.
    hop=RATE//8
    levels=np.array([db(mix[j:j+hop]) for j in range(0,len(mix),hop)])
    level_t=(np.arange(len(levels))+.5)/8
    target=gaussian_filter1d(levels,5,mode='nearest')
    gain=np.clip(1.25*(target-levels),-7.0,7.0)
    gain=gaussian_filter1d(gain,.65,mode='nearest')
    weight=np.zeros(len(levels))
    for t in STARTS[1:]:
        distance=np.abs(level_t-t)
        weight=np.maximum(weight,np.clip((2.5-distance)/.8,0,1))
    mix *= 10**(np.interp(times,level_t,gain*weight)[:,None]/20)
    peak = np.abs(mix).max()
    global_gain = min(1, 10**(-2/20)/peak)
    mix *= global_gain
    sf.write(WORK/'score.wav',mix,RATE,subtype='PCM_24')
    def level(a,b):return db(mix[round(a*RATE):round(b*RATE)])
    joins = [dict(time=t,before_dbfs=level(t-1.0,t-.25),after_dbfs=level(t+.25,t+1.0)) for t in STARTS[1:]]
    report = dict(title='A World Made Gentle',duration=TOTAL,bpm=BPM,order=ORDER,cues=rows,
                  final_chord=FINAL_CHORD,global_gain=float(global_gain),
                  peak_dbfs=float(20*np.log10(np.abs(mix).max())),
                  last_second_rms_dbfs=level(61,62),last_quarter_rms_dbfs=level(61.75,62),
                  lead_peak=float(np.abs(mix[:2*RATE]).max()),joins=joins,
                  validation='Measured source timing, chroma and level checks; not a listening audition.')
    (WORK/'score-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    build()
