"""Build the independent seven-song Astra score without altering source audio.

Requires ffmpeg, numpy and soundfile. Writes only beneath --out (default work/astra).
The cue boundaries match master_astra.py. Equal-power 0.9 second overlaps join
phrases without a silence gap; one continuous s07 passage carries the ascent.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import soundfile as sf

RATE = 48000
TOTAL = 62.0
# file, film start, source start, film end: seven distinct recordings.
CUES = [
    ('s08', 2.0, 27.867, 8.84),
    ('s01', 8.84, 34.313, 15.30),
    ('s04', 15.30, 51.429, 21.85),
    ('s11', 21.85, 43.789, 28.79),
    ('s05', 28.79, 42.443, 35.36),
    ('s07', 35.36, 19.737, 51.47),
    ('s03', 51.47, 48.505, TOTAL),
]


def build(out):
    root = Path(__file__).resolve().parents[1]
    out.mkdir(parents=True, exist_ok=True)
    mix = np.zeros((round(TOTAL * RATE), 2), np.float64)
    rows = []
    half = 0.45
    for index, (name, start, source, end) in enumerate(CUES):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(root / 'audio/promo' / (name + '.mp3')),
                              '-ar', str(RATE), '-ac', '2', '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        audio = np.frombuffer(raw, '<f4').reshape(-1, 2)
        lo = start if index == 0 else start - half
        hi = end if index == len(CUES) - 1 else end + half
        count = round((hi - lo) * RATE)
        first = round((source + lo - start) * RATE)
        clip = audio[first:first + count].astype(np.float64)
        if len(clip) != count:
            raise ValueError(f'{name}: source is too short')
        rms = np.sqrt(np.mean(clip ** 2))
        gain_db = float(np.clip(-18.0 - 20 * np.log10(max(rms, 1e-9)), -15.0, 6.0))
        clip *= 10 ** (gain_db / 20)
        tt = np.arange(count) / RATE + lo
        env = np.ones(count)
        if name == 's07':
            # Let the ascent crest relax into the final song over several seconds.
            u = np.clip((tt - (end - 4.0)) / 3.55, 0, 1)
            env *= 10 ** (-2.0 * u * u * (3 - 2 * u) / 20)
        if index:
            env *= np.sin(np.clip((tt - lo) / (2 * half), 0, 1) * np.pi / 2)
        else:
            env *= np.sin(np.clip((tt - start) / 1.35, 0, 1) * np.pi / 2) ** 2
        if index < len(CUES) - 1:
            env *= np.cos(np.clip((tt - (end - half)) / (2 * half), 0, 1) * np.pi / 2)
        else:
            # Preserve the final chord and its natural decay, then taper only its quiet tail.
            env *= np.cos(np.clip((tt - 59.8) / 2.2, 0, 1) * np.pi / 2) ** 2
        begin = round(lo * RATE)
        mix[begin:begin + count] += clip * env[:, None]
        rows.append(dict(song=name, film_start=start, source_start=source, film_end=end, gain_db=gain_db))
    peak = float(np.max(np.abs(mix)))
    gain = min(1.0, 10 ** (-1.5 / 20) / max(peak, 1e-9))
    mix *= gain
    sf.write(out / 'astra-medley.wav', mix, RATE, subtype='PCM_24')
    report = dict(duration=TOTAL, sample_rate=RATE, songs=rows, global_gain=gain,
                  peak_dbfs=float(20 * np.log10(np.max(np.abs(mix)))),
                  last_quarter_rms_dbfs=float(20 * np.log10(max(np.sqrt(np.mean(mix[-RATE//4:] ** 2)), 1e-12))))
    (out / 'audio-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('work/astra'))
    build(parser.parse_args().out)
