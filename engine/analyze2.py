import sys, numpy as np, librosa
d = np.load(sys.argv[1]); times=d["times"]; rms=d["rms"]; onset=d["onset"]; beat_t=d["beat_t"]; air=d["air"]; high=d["high"]; low=d["low"]
def db(x): return 20*np.log10(np.maximum(x,1e-7))
sr=22050; hop=512
# meter guess: autocorrelation of onset envelope
ac = librosa.autocorrelate(onset, max_size=int(8*sr/hop))
lags = np.arange(len(ac))*hop/sr
pk = librosa.util.peak_pick(ac, pre_max=5, post_max=5, pre_avg=5, post_avg=5, delta=0.0, wait=5)
top = sorted([(ac[i], round(lags[i],3)) for i in pk if lags[i]>0.3], reverse=True)[:8]
print("onset autocorr peaks (strength, lag s):", [(round(a/ac[0],3), l) for a,l in top])
def win(a,b,step=1.0):
    print(f"--- {a}-{b}s  (rms dB | low | high | air | onset max)")
    for t0 in np.arange(a,b,step):
        m=(times>=t0)&(times<t0+step)
        print(f"{t0:6.1f} {db(rms[m]).mean():6.1f} {db(low[m]).mean():5.0f} {db(high[m]).mean():5.0f} {db(air[m]).mean():5.0f}  {onset[m].max():5.1f}  " + "#"*int(max(0,db(rms[m]).mean()+45)))
win(0,30); win(48,82); win(108,140); win(166,200); win(214,251)
# strongest onsets overall
idx = np.argsort(onset)[::-1]
seen=[]; 
for i in idx:
    t=times[i]
    if all(abs(t-s)>1.5 for s in seen): seen.append(t)
    if len(seen)>=24: break
print("strongest onsets at (s):", sorted(round(float(s),2) for s in seen))
# bar phase: energy of onset at beats modulo 4 and modulo 3
on_b = np.interp(beat_t, times, onset)
for m in (3,4,6):
    print("mod",m,[round(float(on_b[k::m].mean()),2) for k in range(m)])
lowb = np.interp(beat_t, times, db(low))
print("low-band at beat mod4:", [round(float(lowb[k::4].mean()),1) for k in range(4)], " mod3:", [round(float(lowb[k::3].mean()),1) for k in range(3)])
