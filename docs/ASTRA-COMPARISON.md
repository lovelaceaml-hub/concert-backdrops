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
and a taper only over the final tail. Original source audio is unchanged.

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

Validation results will be added after the complete render. Preliminary frames and
motion excerpts are under `out/astra/`; logs and measurements are under `work/astra/`.
