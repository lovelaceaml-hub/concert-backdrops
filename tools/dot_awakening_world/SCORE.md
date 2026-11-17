# The Light We Share: independent music draft

This is a new 62-second edit of seven owner-supplied concert recordings, not AI-generated music and not a copy of an existing medley. Order: 01, 04, 08, 05, 09, 07, 03.

Run `build.py` with numpy, scipy, librosa, soundfile and ffmpeg installed. Place the seven authorized recordings in `sources/sNN.mp3`. Do not commit source recordings, generated audio, caches or metadata containing private access links.

The first two seconds are silent in PCM. A 1.5-second fade introduces the first recording. Six equal-power 2.5-second blends begin at 10, 18, 26, 34, 42 and 50 seconds. Recorded source 03's final decay is retained, followed by additional tapering to quiet. The original tail around source 346 to 351 seconds maps to about film 55.8 to 60.8 seconds. No synthetic reverb is added.

The script uses detected beat positions near selected early excerpts, modest pitch-preserving tempo changes and local gain riding around joins. A 2/3 pulse interpretation is assumed for detected tempos over 145 bpm. That interpretation and the phrase boundaries are not verified by listening. The script deliberately limits speed changes to 10 percent, so the sources are not all exactly tempo-matched.

Measured encoded AAC draft: 62.000 seconds, stereo, 48000 Hz; full decode succeeds. Peak -4.252 dBFS, final-second RMS -94.067 dBFS, maximum adjacent quarter-second RMS change at the six joins 2.563 dB. AAC pre-echo before 2 seconds is below -124 dBFS. The source PCM begins with exact zero samples.

These checks establish duration, level and continuity measurements, not musical quality. A listening review is still required for phrase continuity, tonal relationships, pulse interpretation, pumping from gain riding, and whether the final cadence feels resolved. The film should be labeled a creative draft, not approved production.
