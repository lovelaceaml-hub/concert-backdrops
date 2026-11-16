# Delivery validation

Render source: 7df8667, creative/light-that-reaches-you. Draft PR #64.
Principal reference: Film 10, Nine Colours, selected by the owner.

## Checks completed before the full export

- Sequential versus shuffled fresh-process rendering: all 19 sampled raw 1080p
  frames are byte-identical. This is a sampled regression check, not an exhaustive
  comparison of every possible ordering. Fifteen transition/finale samples and
  four people samples (10.5, 18.5, 26.5 and 37.5 seconds) were checked separately.
- Camera sampled at 60 fps: maximum angular speed 38.826 degrees per second,
  maximum translation speed 20.140 metres per second; finite positions and targets.
- All nine expression readings hold for 2.60 seconds after arrival.
- Opening is whole for seven seconds. The end card finishes arriving at 55 seconds
  and holds through the final frame at 61.9833 seconds.
- Native 60 fps ascent sample: 180 frames from 45 to 48 seconds, inspected as a
  10 fps strip. No cut or camera reversal occurs within that sampled rise.
- Thirteen study stills and seven refined stills inspected across the film.
  Broad comet-glow strip artifacts were removed and the paths lowered away from
  faces before the full export. Eleven departure stills exposed a camera pass
  through departing people. Their dissolve now completes before that pass. All
  eight departures were inspected after correction.
- The unchanged opening part (frames 0 through 464) was retained from d0a959b.
  The only subsequent rendering change is inside Performance.sample after its
  time guard; no performance is active before 8.6 seconds. All affected sections
  are rendered again against 7df8667. The full export receives a separate review.

## Source audio measurements

The retained independent seven-song edit rebuilt byte-identically from music.py.

| Measurement | Result |
| --- | --- |
| Duration | 62.000 seconds |
| Format | Stereo, 48 kHz, 24-bit WAV before AAC encoding |
| First two seconds | Exactly silent |
| Peak | -4.577 dBFS |
| Final second RMS | -65.820 dBFS |
| Final chord | 57.5 seconds |
| Blend duration | 2.143 seconds at each of six joins |
| Largest 250 ms level step near any join | 2.333 dB |

These are measured timing, level and harmonic-selection checks. No listening
review is claimed. They cannot establish the owner's experience of musical flow.

## Final exports

Both exported files pass `verify.py`. The full film was reviewed as 10 fps frame
sheets, with additional 20 fps strips at the busiest measured intervals around
23.5, 27.0 and 45.5 seconds. These intervals show the hoop flight and rising
braid. No listening audition is claimed.

| Measurement | 1080p master | 720p phone copy |
| --- | --- | --- |
| Duration | 62.000 s | 62.000 s |
| Frames | 3,720 | 3,720 |
| Frame rate | 60/1 | 60/1 |
| Video/audio | H.264 yuv420p / AAC | H.264 yuv420p / AAC |
| Faststart | Yes | Yes |
| File size (bytes) | 85537440 | 20701202 |
| Exact duplicate frame pairs | 0 | 0 |
| Peak audio (dBFS) | -4.664 | -4.603 |
| Final-second audio RMS (dBFS) | -66.674 | -66.783 |

No frozen stretch was found. Frame timestamp errors are below two microseconds.
At the seven render-part boundaries, frame-difference ratios relative to nearby
frames range from 0.97 to 1.14 across the two exports. Encoded audio remains
silent through the intended lead-in, each measured join stays under the 3 dB
limit, and the final second is below -66 dBFS. The end card remains readable
through the last frame; ambient motion continues behind it.

Delivered to the project's existing Videos folder without changing sharing:

- [Phone 720p60](https://drive.google.com/file/d/1VvLhK55-X4JP8pq9KhQP4rh2njDWckTB/view)
- [Master 1080p60](https://drive.google.com/file/d/1Sf_gwkjKouPH6rpkZZ1jzZ7Tizeii24w/view)

SHA-256 checksums:

- `The-Light-That-Reaches-You-1080p60.mp4`: `0542c43539542b5a5d4471ccfe05a3d1b483c8c2837b0c95fa267b760583c87f`
- `The-Light-That-Reaches-You-review-720p60.mp4`: `3bdba638ff98f0dca3cca40793007fc26f1678ccbab58ab98390d9ba93f8635d`

No paid services or GitHub Render workflow were used. No media, features or
caches are committed. PR #64 remains a draft; the owner decides whether to merge.
