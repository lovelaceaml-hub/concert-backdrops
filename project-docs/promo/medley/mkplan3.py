"""Resolve the medley plans into medley times. Writes plans3.json (read by build3.py and check3.py).

Every number here comes from the measured grids (segfit.py on each source window):
  song  period P (s)  grid anchor (a beat, source s)   meter
  03    0.7502        4.525  downbeat                  4/4
  04    0.7697        3.199  downbeat                  4/4
  01    0.7263        7.482  downbeat                  4/4
  08    0.7490        7.883  (phrase cadence, beat)    4/4 (uncertain)
  11    0.5774        43.786 downbeat                  4/4
  06    0.5798        19.857 downbeat (Eb cadence)     3/4
  07    0.7689        28.892 climax entrance            4/4
  07    0.7739        49.666 final cadence grid
Placement: medley t = t_a + (s - s_a) * alpha, alpha = output length / source length (time-stretch).
"""
import json

PT = 0.7477                      # slow-chain beat period in the medley (80.25 bpm)
G = {'03': (0.7502, 4.525), '04': (0.7697, 3.199), '01': (0.7263, 7.482), '08': (0.7490, 7.883),
     '11': (0.5774, 43.786), '06': (0.5798, 19.857), '07a': (0.7689, 28.892), '07b': (0.7739, 49.666)}


def beat(song, k):
    P, a = G[song]
    return a + k * P


def seg(song, alpha, s_a, t_a, s_in, s_out, body, level, meter, grid_song=None, **kw):
    d = dict(song=song[:2], key=song, alpha=alpha, s_a=s_a, t_a=t_a, s_in=s_in, s_out=s_out, body=body,
             level=level, meter=meter, P=G[grid_song or song][0], g_a=G[grid_song or song][1])
    d.update(kw)
    return d


def T(sg, s):
    return sg['t_a'] + (s - sg['s_a']) * sg['alpha']


M = 1.5   # extra source kept on each side of a segment (silent under the envelopes; used to measure alignment)
BREATH = 2.5   # the lift: seconds from 06's Eb cadence to 07's climax entrance


def main_plan():
    a = {s: PT / G[s][0] for s in ('03', '04', '01', '08')}
    S = []
    # 1. 03: intro phrase; its downbeat 4.525 lands where the 1.5 s fade-in completes (3.5 s)
    s03 = seg('03', a['03'], 4.525, 3.5, 4.525 - 1.5 / a['03'], beat('03', 8) + M, [4.525, 7.526], 0.0, 4)
    S.append(s03)
    # 2. 04: its Bb downbeat (3.199) lands on 03's next-but-one downbeat (10.526): 03's Cm bar and F7 hold
    #    resolve into 04's Bb
    t = T(s03, beat('03', 8))
    s04 = seg('04', a['04'], beat('04', 0), t, 0.0, beat('04', 8) + M, [3.199, 6.278], 0.4, 4)
    S.append(s04)
    # 3. 01: its Cm downbeat (4.577, k=-4) on 04's Cm downbeat (9.356, k=8)
    t = T(s04, beat('04', 8))
    s01 = seg('01', a['01'], beat('01', -4), t, max(beat('01', -8) - M, 0.0), beat('01', 8) + M, [4.577, 10.387], 0.8, 4)
    S.append(s01)
    # 4. 08: its C cadence (7.883, k=0) on 01's C cadence downbeat (10.387, k=4)
    t = T(s01, beat('01', 4))
    s08 = seg('08', a['08'], beat('08', 0), t, beat('08', 0) - M, beat('08', 15) + M, [10.879, 16.80], 1.2, 4)
    S.append(s08)
    # 5. 11 (no stretch): its bass downbeat 41.476 on 08's C arrival (16.871, k=12): 08 holds C, 11 plays C
    t = T(s08, beat('08', 12))
    s11 = seg('11', 1.0, 41.476, t, 41.476 - M, beat('11', 16) + M, [43.786, 50.715], 1.6, 4)
    S.append(s11)
    # 6. 06 (no stretch): aligned with 11 at the middle of the blend bar (11's 51.870 = 06's 13.479)
    t = T(s11, beat('11', 14))
    s06 = seg('06', 1.0, beat('06', -11), t, beat('06', -13) - M, beat('06', 3) + 0.4, [14.639, 19.857], 2.15, 3)
    S.append(s06)
    E = T(s06, beat('06', 0))     # 06's Eb cadence arrives: the breath begins
    H = E + BREATH                # the lift hit: 07's climax entrance
    # 7a. 07 climax (no stretch) from its Eb pedal (the breath) to the splice in the choir's gap at 34.25
    s07a = seg('07a', 1.0, 28.892, H, 28.892 - 4.0, 34.25 + 0.6, [28.892, 34.25], 3.0, 4, grid_song='07a')
    S.append(s07a)
    # 7b. 07 final cadence: its attack (49.73) takes the place of the climax's next attack (34.31); the song's
    #     own tag (Bbm, Eb7, Db) follows and the held Ab arrives at 51.37 and rings to 54.2
    tF = T(s07a, 34.31)
    s07b = seg('07b', 1.0, 49.73, tF, 49.67 - 0.6, 54.20, [28.892, 34.25], 3.0, 4, grid_song='07b')
    S.append(s07b)
    J = [
        dict(kind='beat', out=0, inn=1, t0=T(s03, beat('03', 4)), t1=T(s03, beat('03', 8))),
        dict(kind='hold', out=1, inn=2, t0=T(s04, beat('04', 4)), t1=T(s04, beat('04', 8))),
        dict(kind='beat', out=2, inn=3, t0=T(s01, beat('01', 4)), t1=T(s01, beat('01', 8))),
        dict(kind='hold', out=3, inn=4, t0=T(s08, 16.80) - 0.02, t1=T(s08, beat('08', 15)) - 0.07),
        dict(kind='beat', out=4, inn=5, t0=T(s11, beat('11', 12)), t1=T(s11, beat('11', 16))),
        dict(kind='lift', out=5, inn=6, t0=E - 0.5, t1=H, breath=[E, H], out_end=T(s06, 21.45)),
        dict(kind='splice', out=6, inn=7, t0=T(s07a, 34.235), t1=T(s07a, 34.265)),
    ]
    final = T(s07b, 51.37)
    end = dict(cadence=tF, final=final, fade0=final + 0.7, fade1=T(s07b, 54.15), rev_rt60=3.0, rev_db=-10.0)
    return dict(name='main', order=['03', '04', '01', '08', '11', '06', '07'], PT=PT, segs=S, joins=J,
                end=end, lift=dict(E=E, H=H), total=62.0, lead=2.0, fadein=1.5)


def alt_plan():
    """The alternative: the bright, fast songs first (11, 06), a breath on 06's Eb cadence into the reflective
    slow songs (03, 04, 01, 08), and the lift from 08's held C into 07's climax."""
    a = {s: PT / G[s][0] for s in ('03', '04', '01', '08')}
    S = []
    # 1. 11: its F downbeat (43.786) lands where the fade-in completes
    s11 = seg('11', 1.0, 43.786, 3.5, 43.786 - 1.5, beat('11', 16) + M, [43.786, 50.715], 0.0, 4)
    S.append(s11)
    t = T(s11, beat('11', 14))
    s06 = seg('06', 1.0, beat('06', -11), t, beat('06', -13) - M, beat('06', 3) + 0.4, [14.639, 19.857], 0.4, 3)
    S.append(s06)
    E6 = T(s06, beat('06', 0))
    # 3. 03: its F7 entrance downbeat (4.525) 1.7 s after 06's Eb cadence (06 holds while 03's soft intro enters)
    s03 = seg('03', a['03'], 4.525, E6 + 1.7, 4.525 - 1.9, beat('03', 8) + M, [4.525, 7.526], 0.8, 4)
    S.append(s03)
    t = T(s03, beat('03', 8))
    s04 = seg('04', a['04'], beat('04', 0), t, 0.0, beat('04', 8) + M, [3.199, 6.278], 1.2, 4)
    S.append(s04)
    t = T(s04, beat('04', 8))
    s01 = seg('01', a['01'], beat('01', -4), t, max(beat('01', -8) - M, 0.0), beat('01', 8) + M, [4.577, 10.387], 1.6, 4)
    S.append(s01)
    t = T(s01, beat('01', 4))
    s08 = seg('08', a['08'], beat('08', 0), t, beat('08', 0) - M, beat('08', 15) + M, [10.879, 16.80], 2.0, 4)
    S.append(s08)
    E = T(s08, 16.80)            # 08's C cadence arrives: the breath begins
    H = E + 2.3
    s07a = seg('07a', 1.0, 28.892, H, 28.892 - 4.0, 34.25 + 0.6, [28.892, 34.25], 3.0, 4, grid_song='07a')
    S.append(s07a)
    tF = T(s07a, 34.31)
    s07b = seg('07b', 1.0, 49.73, tF, 49.67 - 0.6, 54.20, [28.892, 34.25], 3.0, 4, grid_song='07b')
    S.append(s07b)
    J = [
        dict(kind='beat', out=0, inn=1, t0=T(s11, beat('11', 12)), t1=T(s11, beat('11', 16))),
        dict(kind='hold', out=1, inn=2, t0=E6 - 0.4, t1=E6 + 1.8),
        dict(kind='beat', out=2, inn=3, t0=T(s03, beat('03', 4)), t1=T(s03, beat('03', 8))),
        dict(kind='hold', out=3, inn=4, t0=T(s04, beat('04', 4)), t1=T(s04, beat('04', 8))),
        dict(kind='beat', out=4, inn=5, t0=T(s01, beat('01', 4)), t1=T(s01, beat('01', 8))),
        dict(kind='lift', out=5, inn=6, t0=E - 0.5, t1=H, breath=[E, H], out_end=T(s08, 19.05)),
        dict(kind='splice', out=6, inn=7, t0=T(s07a, 34.235), t1=T(s07a, 34.265)),
    ]
    final = T(s07b, 51.37)
    end = dict(cadence=tF, final=final, fade0=final + 0.7, fade1=T(s07b, 54.15), rev_rt60=3.0, rev_db=-10.0)
    return dict(name='alt', order=['11', '06', '03', '04', '01', '08', '07'], PT=PT, segs=S, joins=J,
                end=end, lift=dict(E=E, H=H), total=62.0, lead=2.0, fadein=1.5)


if __name__ == '__main__':
    P = {'main': main_plan(), 'alt': alt_plan()}
    json.dump(P, open('plans3.json', 'w'), indent=1)
    for name, p in P.items():
        print('==', name, ' '.join(p['order']))
        for sg in p['segs']:
            print(f"{sg['key']:4s} alpha {sg['alpha']:.5f} ({(1 / sg['alpha'] - 1) * 100:+.2f}% tempo) src {sg['s_in']:6.3f}-{sg['s_out']:6.3f} "
                  f"-> medley {T(sg, sg['s_in']):6.3f}-{T(sg, sg['s_out']):6.3f}")
        for j in p['joins']:
            print(f"join {j['kind']:6s} {p['segs'][j['out']]['key']}->{p['segs'][j['inn']]['key']}: {j['t0']:.3f}-{j['t1']:.3f} "
                  f"({j['t1'] - j['t0']:.2f} s, mid {(j['t0'] + j['t1']) / 2:.3f})")
        print('lift', p['lift'], 'end', p['end'])
