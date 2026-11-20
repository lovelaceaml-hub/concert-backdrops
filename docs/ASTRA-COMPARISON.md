# Independent Astra concert comparison

Source baseline: v6, `b7895aef771f4dcdbb7a3383afeab235fd945b6e`.
Branch: `compare/astra6-concert`. Song: `master_astra`.
This treatment is independent of Claude's subsequent changes and the render-speed draft.

## Creative treatment

Keep the 62 second journey, two second musical lead-in, all nine approved expressions,
opening title held whole for seven seconds, and full event card from 55 to 62 seconds.
The energetic river flight and ascent remain. Wider, longer camera transitions around
the human moments replace whip pans; less handheld movement keeps the words stable.

Greeting becomes a modest reciprocal bow. All nine performances receive softer gesture
arrivals, releases, and contact settling. Apology is re-staged as two standing women:
one acknowledges the hurt with a hand to her heart and a small bow; the other responds
with a nod and open hands. They pause, approach, and embrace for Inclusiveness. Their
camera keeps the full figures visible. This replaces the inherited kneeling performance,
whose rise and shuffle overlapped and whose contact pose folded the torso.

Compliment receives the applause with a grounded hand-to-heart acknowledgement, then
opens her arms back to the crowd. A wider frame leaves room for the whole figure. The
heart burst follows the acknowledgement instead of covering it. The ending retains a
stable event card, drifting pastel atmosphere, and optional faint golden motes at the
outer margins, clear of all text. There is no fade to black or duplicated still hold.

## Seven-song score

`tools/astra_medley.py` selects these excerpts from the existing recordings, in order:

| Source | Song | Film start |
| --- | --- | --- |
| s08 | Out of Heaven, Favor From God | 2.00 |
| s01 | All You Stars of Zion | 8.84 |
| s04 | I'm Sorry, Please Forgive Me | 15.30 |
| s11 | Almighty God Who Knows the Future | 21.85 |
| s05 | God Bless You! | 28.79 |
| s07 | May No One Ever Feel Lonely | 35.36 |
| s03 | I Reminisce About Your Love | 51.47 |

The continuous s07 passage connects the human gestures to the ascent. The final s03
excerpt starts later than the v6 excerpt so its resolving chord has time to decay within
62 seconds. The mix uses 0.9 second equal-power overlaps, a gentle musical entrance,
and a taper only over the final tail. Per-excerpt RMS matching and a gradual 2 dB
relaxation before the final handoff keep measured join contrast under 1.91 dB.
The final visual glow follows the resolving chord at 58.11 seconds. Original source
audio is unchanged.

## Reproduction

Fonts must be available under `fonts/`. Python requires numpy, scipy, librosa,
moderngl, pillow and soundfile; ffmpeg and ffprobe must be on PATH. Use private output
and cache directories. No media, features or caches belong in a commit.

```bash
python tools/astra_medley.py
ffmpeg -v error -y -i work/astra/astra-medley.wav -ac 1 -ar 22050 work/astra/audio.wav
NUMBA_CACHE_DIR="$PWD/work/astra/numba" python engine/analyze.py work/astra/audio.wav work/astra/features.npz
python tools/astra_render.py --workers 4 --parts 8
```

The runner verifies every part's frame count, concatenates 3720 native frames, adds
stereo audio and creates both a 1920x1080 60 fps master and a 1280x720 60 fps review.
It records the source and audio hashes, supports resuming completed matching parts,
and refuses to reuse parts after its inputs change. No hosted render workflow is used.

## Validation

Before the complete render, full-resolution stills were inspected for every acted
scene and title framing. Native 60 fps excerpts covered Apology and Compliment;
sequential-frame inspection and frame differences found no adjacent duplicate frames
or isolated frame jumps in these excerpts. The two second lead-in is digital silence.
The source mix peaks at -4.65 dBFS; its final quarter-second RMS is -59.33 dBFS.
These are measured audio checks, not a listening audition.

The final-glow timing was amended before the last render part launched. Only its
start time changed from 60.11 to 58.11 seconds. Both versions return no geometry
before 57.96 seconds, so parts 0 through 6 (all before 54.25 seconds) are unaffected.
The updated input manifest and before/after hashes are recorded with the local logs.

Both final encoded deliverables passed an independent technical scan:

| Check | Master | Review |
| --- | --- | --- |
| Resolution | 1920x1080 | 1280x720 |
| Frame rate and count | 60 fps, 3720 | 60 fps, 3720 |
| Video duration | 62.000 s | 62.000 s |
| Audio duration | 62.000 s | 62.016 s |
| Decoded AAC peak | -4.708 dBFS | -4.636 dBFS |
| Final quarter-second RMS | -60.755 dBFS | -60.804 dBFS |
| Exact adjacent duplicate frames | 0 | 0 |

All presentation timestamps are correctly spaced to within timestamp rounding.
The closing seven seconds change on every frame. Frame differences at the seven
render-part joins are within 0.618 to 1.169 times their local median, with no join
spike. The review's 16 ms of AAC padding is less than one 60 fps frame. The first
1.9 seconds of each decoded audio track are exactly silent.

The completed master was also inspected in sequential frames through the approach
and embrace, ascent, world-to-logo transition, and final card. Its opening title is
intact at 6.9 seconds; the complete end card is readable at 55.0 through the last
frame. This review uses images and sequential frames, not an audiovisual audition.

Deliverables are `out/astra/Astra-independent-concert-1080p60.mp4`,
`out/astra/Astra-independent-concert-review-720p60.mp4`, and
`out/astra/Astra-independent-score.wav`. The independent technical results are in
`work/astra/encoded-validation.json`; preview frames, motion excerpts, logs and
measurements remain local and are not committed.
