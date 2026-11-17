# Delivery validation, 2026-11-16

This is a creative upgrade of Nine Colours render 1, not a pixel-identical
engine optimization. Reference: run `43726203825`, source
`d928ff9eafe02ac3150f0c646bdcc497fe5a7278`. The latest direction is PHASEB
UPDATE 20. The source is isolated under `tools/nine_colours/` in draft PR #66.

## Finished videos

- [Phone, 720p60](https://drive.google.com/file/d/14yx-oGbeKneDZhfNzlyxbXyJwPrrplwT/view)
- [Full resolution, 1080p60](https://drive.google.com/file/d/1YJBkTVJ0SlnjZqcSzMzkcgbHxbjeJpXg/view)

| Measurement | Full resolution | Phone |
|---|---:|---:|
| Resolution | 1920 x 1080 | 1280 x 720 |
| Video and audio duration | 62.000 s | 62.000 s |
| Frame rate / decoded frames | 60 / 3720 | 60 / 3720 |
| Size | 93,466,738 bytes | 22,004,075 bytes |
| Consecutive identical decoded frames | 0 | 0 |
| Largest timestamp-step rounding error | 0.667 microseconds | 0.667 microseconds |
| Integrated loudness | -13.0 LUFS | -13.0 LUFS |
| True peak | -2.6 dBTP | -2.5 dBTP |
| Final 10 ms sample peak | -93.050 dBFS | -93.257 dBFS |
| Final quarter-second RMS | -50.107 dBFS | -50.216 dBFS |

H.264, yuv420p, stereo AAC, fast-start MP4. The downloaded Drive phone file
was checked against the local export by SHA256 and matched exactly.

Full-resolution SHA256:
`a1dc4d717bb007159a14195cf6a16747e400edbb272d1c7e6a3e6c06dc935c6d`

Phone SHA256:
`d76093230e7a1adf2779f90e065cc16525c01ffb5d84d4261d79ae0e6ac79a2c`

## Reference fidelity and order independence

- All 601 camera-position and target samples from original time 0 to 49.46 s
  match render 1 exactly. Rechecked after the final source corrections.
  The intentional replacement finale starts at original time 49.47 s.
- The approved `concert-medley-leadin.mp3` retains the original eight-song edit,
  quiet lead-in, entry fade and final musical accent. Alignment with the r1
  share audio at +2 s gives correlation 0.99902 after the entry fade. These
  are lossy encodes, so this is not a claim of PCM equality.
- Before final visual corrections, all 23 sampled raw 1080p frames matched
  between separate processes rendering sequentially and in shuffled order.
- The opening, Apology transition, Gratitude transition and finale corrections
  passed supplemental sequential/reverse raw-frame checks with 8, 9, 7 and
  10 samples respectively. Unaffected samples matched the previous render.
- Five raw frames from the final committed configuration matched the reviewed
  correction configurations exactly, covering all four corrections.
- Eight local parts were assembled at the original frame timestamps. Reviewed
  corrections replaced complete encoded segments without re-encoding the
  retained segments. Source manifests and decoded part counts were checked.
  The completed file has no missing timestamps, consecutive duplicate frames or freeze.

## Visual and audio review

Reviewed full-size 1080p stills, 10 fps strips across the entire film, and
native-frame strips through the 15.5 s part boundary and the fast final braid.
The boundary alert is a blue comet passing the lens during the original scene
transition; it is not a missing or repeated frame. The energetic half-loop and
corkscrew remain intentional parts of the selected reference.

Corrections made during inspection: remove a flash covering the opening card;
prevent overlapping Apology/Inclusiveness and Consideration/Gratitude text;
bring the globe closer for the match cut after the spiral. All nine phrases
hold fully readable for at least 2.5 s. The opening is whole from frame zero
through 7 s, and the official end card is whole from 55 s to the final frame.
The end card continues to move through the final musical accent.

The original medley's dynamics are preserved. The largest quarter-second
level change near each join, in the full-resolution export, is:

| Join, final film seconds | Largest change, dB |
|---:|---:|
| 8.84 | 2.676 |
| 15.30 | 3.445 |
| 21.85 | 3.801 |
| 28.79 | 1.663 |
| 35.36 | 4.253 |
| 42.21 | 5.645 |
| 51.47 | 4.936 |

These are measurements around the preferred soundtrack's existing joins,
not a claim that every join meets the older 3 dB criterion. The final second
is -23.389 dBFS RMS because the musical release is retained; it reaches
-93.050 dBFS peak in the final 10 ms. The final accent is not silenced to
satisfy the older last-second threshold. No clipping or audio truncation was
found. Visual and signal inspection does not replace a human listening audition.

Run `tools/nine_colours/verify.py` on the two delivered files to reproduce
frame, timestamp, motion, join and audio measurements. Private diagnostic
reports and media are under `work/nine_colours/` and `out/nine_colours/` and
are not committed. No paid service, GitHub Render workflow or merge was used.
