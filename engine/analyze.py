import sys, json, numpy as np, librosa, warnings
warnings.filterwarnings("ignore")
wav, out = sys.argv[1], sys.argv[2]
y, sr = librosa.load(wav, sr=22050, mono=True)
dur = len(y)/sr
hop = 512
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
rms = librosa.feature.rms(S=S, frame_length=2048, hop_length=hop)[0]
def band(lo, hi):
    m = (freqs >= lo) & (freqs < hi)
    return np.sqrt((S[m]**2).mean(axis=0))
low, mid, high, air = band(20,200), band(200,2000), band(2000,6000), band(6000,11000)
cent = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
onset = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S, ref=np.max), sr=sr, hop_length=hop)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=hop, units="frames")
tempo = float(np.atleast_1d(tempo)[0])
beat_t = times[beats]
onsets = librosa.onset.onset_detect(onset_envelope=onset, sr=sr, hop_length=hop, units="time", backtrack=False)
# harmonic/percussive
yh, yp = librosa.effects.hpss(y)
rh = librosa.feature.rms(y=yh, frame_length=2048, hop_length=hop)[0]
rp = librosa.feature.rms(y=yp, frame_length=2048, hop_length=hop)[0]
# structure from beat-synced chroma+mfcc
chroma = librosa.feature.chroma_cqt(y=yh, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(S=librosa.power_to_db(librosa.feature.melspectrogram(S=S**2, sr=sr)), n_mfcc=13)
feat = np.vstack([librosa.util.normalize(chroma, axis=0), librosa.util.normalize(mfcc, axis=0)])
fs = librosa.util.sync(feat, beats, aggregate=np.median)
segs = {}
for k in (6, 8, 10, 12):
    b = librosa.segment.agglomerative(fs, k)
    bf = librosa.util.fix_frames(beats)[b] if len(b) else b
    segs[k] = [round(float(times[min(i, len(times)-1)]), 2) for i in bf]
# key estimate
ch = chroma.mean(axis=1)
maj = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); minr = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
best = max(((np.corrcoef(np.roll(maj,i),ch)[0,1], names[i]+" major") for i in range(12)), key=lambda x:x[0])
bestm = max(((np.corrcoef(np.roll(minr,i),ch)[0,1], names[i]+" minor") for i in range(12)), key=lambda x:x[0])
def db(x): return 20*np.log10(np.maximum(x,1e-7))
print(f"duration {dur:.2f}s  tempo {tempo:.1f} bpm  beats {len(beat_t)}  onsets {len(onsets)}  key {max(best,bestm)[1]} ({best[0]:.2f} maj / {bestm[0]:.2f} min)")
print("first beats:", np.round(beat_t[:12],2).tolist())
ib = np.diff(beat_t); print(f"beat interval median {np.median(ib):.3f}s  p10 {np.percentile(ib,10):.3f}  p90 {np.percentile(ib,90):.3f}")
for k,v in segs.items(): print(f"segments k={k}:", v)
print("\n t(s)  rms_dB  low   mid   high  air   cent  harm  perc  onsets/s")
step = 4.0
for t0 in np.arange(0, dur, step):
    m = (times >= t0) & (times < t0+step)
    if not m.any(): continue
    oc = ((onsets >= t0) & (onsets < t0+step)).sum()/step
    bar = "#"*int(max(0,(db(rms[m]).mean()+50))/1.6)
    print(f"{t0:5.0f}  {db(rms[m]).mean():6.1f} {db(low[m]).mean():5.0f} {db(mid[m]).mean():5.0f} {db(high[m]).mean():5.0f} {db(air[m]).mean():5.0f} {cent[m].mean():6.0f} {db(rh[m]).mean():5.0f} {db(rp[m]).mean():5.0f}  {oc:4.1f} {bar}")
np.savez_compressed(out, times=times, rms=rms, low=low, mid=mid, high=high, air=air, cent=cent, onset=onset, beat_t=beat_t, onsets=onsets, rh=rh, rp=rp, dur=dur, tempo=tempo)
print("saved", out)
