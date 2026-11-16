# A World Made Gentle: delivery checks

Checked locally on 2026-11-16 using software OpenGL. Film and music inputs were
frozen at commit 3d8bc6e. The handbook was rechecked before final validation and
remained at 2db9544ccdc6de8d83fd4acd0b6fe0a18bc6cee5.

## Delivered files

| Check | Master | Phone copy |
|---|---:|---:|
| Resolution | 1920 x 1080 | 1280 x 720 |
| Frame rate | 60 fps | 60 fps |
| Video and audio duration | 62.000 s | 62.000 s |
| Frames | 3,720 | 3,720 |
| File bytes | 24,553,283 | 5,289,715 |
| Repeated adjacent native frames | 0 | 0 |
| Largest timestamp step error | 0.667 microseconds | 0.667 microseconds |
| Audio peak | -4.664 dBFS | -4.603 dBFS |
| Largest quarter-second join change | 2.361 dB | 2.387 dB |
| Final second audio RMS | -66.674 dBFS | -66.783 dBFS |

Both files pass verify.py. Audio is stereo, 48 kHz. The first 1.9 seconds decode
to silence. All six joins are below the 3 dB envelope limit. The recorded final
chord is placed at 57.5 s and decays through 61.8 s.

The 160 x 90 motion scan found no frozen run in the master. The phone copy has
21 identical adjacent pairs at that very small analysis resolution, with a
longest run of two frame intervals. Its native 720p frames are all distinct.
The end card's motion is deliberately subtle.

The largest half-second jitter is during the logo-to-card transition at 54 s:
2.584 luma levels in the master and 2.539 in the phone copy. Dense strips show
the intended transition, without a camera whip. At quiet render-part joins,
the master has a 0.30 to 0.31 luma-level mean change versus roughly 0.04 to 0.05
nearby. These ratios look large because the scene barely moves. The raw-order
checks and adjacent encoded-frame inspection distinguish this small encoding
boundary change from a jump in scene state. No claim of lossless MP4 encoding
is made.

## Pixel and visual review

- probe.py passed all 15 raw 1080p frame comparisons between fresh sequential
  and shuffled processes. Frames cover three render boundaries and both newly
  staged standing scenes. This is a sampled order check, not an exhaustive
  proof for every possible time sequence.
- All nine previous probe frames outside the corrections also retained exactly
  the same SHA-256 hashes. Four unaffected parts were retained; parts 0, 1, 4
  and 5 were rebuilt for the opening dust/ripple and standing-pose corrections.
  Every part has 465 frames. Input hashes were checked before assembly.
- Full-size stills were inspected for all nine expressions, the opening, and
  the end card. Dense strips sampled every six frames, or 10 fps, through all
  eight final parts. The busiest motion intervals are included in that review.
- The opening is fully readable from frame zero through 7 s. Opening dust is
  gone by 8 s. Each expression has 3.18 s of settled reading, with measured
  x-height at least 35 pixels at 1080p. The end card is fully visible from
  55 s through the last frame.
- Two source poses were replaced after inspection: encouragement now uses two
  standing women, and consideration uses two standing men. The revised stills
  and strips show whole figures without the previous exposed shin or extended
  leg. Shared acting code was not edited.

Private evidence is in work/gentle/: encoded-validation.json, order/report.json,
partial-reuse-validation.json, visual-review.json and strips/. No images,
videos, audio, features or caches are committed.

## Review limits and delivery

This session reviewed images and measured audio; it did not listen to the edit
or watch real-time playback. Anthony should audition the seven-song flow and
judge the acting on a phone before selecting this alternative. Automated level
checks cannot establish musical phrasing or emotional effect. The tempo grid's
compound-pulse interpretation is an analysis-based creative choice.

- [Phone video in Drive](https://drive.google.com/file/d/1jrYBQi2ZHGigh1TV266hXfjWD-Tq-o2k/view)
- [1080p master in Drive](https://drive.google.com/file/d/1qJ8VvPweLeydfUiN59XPMrFQw64gdHIR/view)
- [Draft PR59](https://github.com/lovelaceaml-hub/concert-backdrops/pull/59)

Drive metadata confirms both filenames, sizes and the Videos destination. The
phone video was fetched back from Drive and its SHA-256 matches the local file.
A copy of that fetched file is also attached in the chat for direct download.

The videos contain the complete new music edit. A separate audio-only file
exists locally, but its Drive upload was blocked by automatic approval review
pending explicit owner authorization. No paid workflow was triggered and
nothing was merged. All changes in this PR are under tools/gentle/.
