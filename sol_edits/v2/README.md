# The Light We Pass, GPT-6.1 Sol V2

Independent creative video and music edit from v6,
`b7895aef771f4dcdbb7a3383afeab235fd945b6e`.
Branch: `compare/sol61-concert-v2`. The owner selected this scope explicitly.
All added code is under `sol_edits/`. No protected engine, song, acting,
workflow or source audio file is edited. Bootstrap loads the new treatment
from this directory and configures the baseline in its own Python process.
Claude's and Astra's worktrees and branches are untouched.

## Creative treatment

A shared light passes through nine small human encounters into a luminous
world. Warm gold bodies, campaign colours, the approved expressions, official
logo, opening, signature and event card come from the shared v6 design.

Twelve gently moving compositions replace v6's whips and dives. Complete
picture dissolves last 0.90 seconds. Both views are sampled at the same global
time and the renderer's camera cache is invalidated between them. Apology
and Inclusiveness share an unbroken shot: low open hands, a modest bow, a
small step, and a same-gender embrace. Greeting uses two shallow bows;
Gratitude uses hand on heart; Concession steps aside with a reachable open
palm; Respect uses two standing listeners; Encouragement combines prayer
and a companion; Consideration shows a gradual assisted rise; Compliment
pairs a modest bow with small chest-height applause. Hearts originate at
actual body anchors. Wider framing keeps the performed bodies whole. Contact references explicitly
omit secondary hand motion in this treatment. The baseline raw-reference path
otherwise re-enters the partner's gestures through living-hand history. The
performed hands keep their normal secondary animation.

Scenery glints and shader twinkle are suppressed, the dense river and crowd
are removed, and rain behind the apology is softened. Nine authored currents
carry the campaign colours around a gradual arc into the globe. The card is
fully readable from 54.95 seconds through the final frame. A two percent
complete-picture push settles at 61.4 seconds; the card has deliberate exit
timing beyond the film. It never fades away.

## Seven-song score

Order: 07, 03, 04, 05, 08, 01, 11. Source offsets and deterministic transforms
are in `build_score.py`. Sources use measured local beat groups, not arbitrary
short time cuts. The first three share B flat; the following four share C.
Those key estimates are computational guidance and need an ear review.
Pitch changes are limited to two semitones with formants preserved. The first
six excerpts map local groups to a 156/104 bpm common pulse. The last excerpt
keeps the original recording's cadence, sustained chord and room decay.
Every overlap lasts 2.3077 seconds with equal-power envelopes. The opening
two seconds are exactly quiet. No new music or synthetic reverb is generated.

Source clips 01 through 08 are the existing repository promo clips. The final
source is the original Song 11 recording in the owner's Drive:
[11 Almighty God Who Knows the Future.mp3](https://drive.google.com/file/d/1tESu4rGGlTJwVpiMXiEA2UC0wA6r2Rf7/view).
Save it as `work/sol2/source11-full.mp3`. It is an input, never a git file.
The final fifty milliseconds only taper the already decayed recording noise.
The Song 11 input SHA-256 is
`a58b5c1498e2712992c89239bc6806dc04aecfcd65bef8ba85a7a0408981c327`.

## Reproduce locally

Python dependencies: numpy, scipy, librosa, moderngl, pillow, fonttools,
brotli and soundfile. ffmpeg must include `rubberband` and libx264. Software
OpenGL uses EGL and llvmpipe. No GPU or paid Render workflow is needed.

Download with `npm pack @fontsource/cormorant-garamond@5.3.0`,
`npm pack @fontsource/jost@5.3.0` and `npm pack @fontsource/outfit@5.3.0`.
Unpack each package under its own directory inside `/tmp/fs`, then run
`python tools/setup_fonts.py /tmp/fs fonts`.

From the repository root, after saving the original Song 11 input:

```sh
python sol_edits/v2/build_score.py
ffmpeg -y -i work/sol2/sol-v2-score.wav -ac 1 -ar 22050 work/sol2/audio.wav
python engine/analyze.py work/sol2/audio.wav work/sol2/features.npz
export AUDIO="$PWD/work/sol2/sol-v2-score.wav"
export FEATURES="$PWD/work/sol2/features.npz"
export P3D_CACHE="$PWD/work/sol2/cache"
export OUT_RES=1080p OUT_FPS=60 LIBGL_ALWAYS_SOFTWARE=1
export LP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python sol_edits/v2/render_all.py
python sol_edits/v2/check_media.py work/sol2/Sol-V2-The-Light-We-Pass-1080p60.mp4 work/sol2/Sol-V2-The-Light-We-Pass-review-720p60.mp4 work/sol2/sol-v2-score.wav
python sol_edits/v2/check_audio.py --video work/sol2/Sol-V2-The-Light-We-Pass-1080p60.mp4
python sol_edits/v2/check_seams.py
```

The renderer derives 3720 frames from the song's 62 seconds and 60 fps.
Five exclusive global ranges cover the film exactly. Each is encoded at its
native 1920 by 1080, 60 fps resolution with CRF 16 and BT.709 metadata. Muxing
copies the video and adds 320 kbps AAC. The smaller 720p review uses CRF 23,
160 kbps AAC and frame-rate passthrough. No frames are generated by interpolation.

To render one range, use `render.py --range START END --out PATH`. The end
is exclusive. `--stills 17.5,21,40.5 --out DIRECTORY` renders inspection frames.
`--step 4 --scale 0.3333334` samples 15 fps motion previews with the same
60 fps shutter timing; never use those options for the delivered master.
All generated media, audio, features, inspection sheets and costs stay under
`work/sol2/`, which the baseline already ignores. No media is committed.

## Finished files and validation

| File | Bytes | Picture | Duration and frame count |
| --- | ---: | --- | --- |
| [Sol V2 master](https://drive.google.com/file/d/1QRjwbXl2djON0Vz9rxJvzkHi0JADosz4/view) | 88,627,934 | 1920 x 1080, 60/1 fps | 62.000 s, 3720 |
| [Sol V2 phone review](https://drive.google.com/file/d/1E4GN8t8kyGsbA6lmOGiTIIEfGIojTpCk/view) | 18,742,630 | 1280 x 720, 60/1 fps | 62.000 s, 3720 |

Both files are in the project's existing Videos folder in Drive. Metadata was
read back after upload and byte counts match the local files. Downloads are
also attached in the owner conversation. No video is stored in git.

The completed files were decoded and checked: every one of 3719 timestamp
intervals is 1/60 second. Both audio streams start at zero; the master audio
lasts 62.000 seconds, and the review has 16 ms of AAC padding at its end, less
than one video frame. The final frame contains the complete official card. Sixteen raw frame hashes, two on each
side of every split, match one continuous sampling pass exactly. All five
ranges contain 744 frames, with no omitted or duplicated range indices.

Reviewed native stills and 10 to 15 fps dense frame sequences of the baseline,
all nine new performances, all six musical overlap windows, the opening,
the new currents, globe and final eight seconds. The apology keeps its hands
low and feet connected, then moves into an embrace; the compliment's arms
form a small natural applause gesture. Whole bodies remain inside the frame.
The main visual defect in v6's Respect scene, the sparkling river carpet, is
removed. Remaining star shimmer and fine body grain are part of the look.

At a common 15 fps and 160 x 90 grayscale sample, p95 absolute frame change
falls from 25.61 in v6 to 7.96; p95 second difference falls from 39.00 to 9.34
(8-bit grayscale units). These describe reduced overall agitation, not a
proof of beauty or absence of flicker. The static-hold detector reports no
hold above 1.5 seconds in either film; it cannot identify v6's perceptually
static card when tiny particles keep changing. Sol's deliberate complete-
picture push and settle were also checked visually.

The source score measures -17.0 LUFS, -1.1 dBFS true peak and a 0.8800 sample
peak. Adjacent 250 ms windows at overlap centres differ by -2.16, -1.26,
-2.35, +1.49, -0.50 and +0.66 dB. The encoded master peaks at 0.8797; the
review peaks at 0.8698. At every join, correlation with the source exceeds 0.99998 for the master
and 0.99859 for the review, with zero measured lag on a 0.25 ms sampling grid.
Their final seconds measure -70.43 and -70.51 dBFS respectively. The source's
last eight seconds measure -18.82, -17.95, -18.31, -19.12, -33.88, -52.77,
-63.29 and -70.36 dBFS: sustained music followed by the recorded release.

## Cost and limits

The final native render used five exclusive range processes on a workspace
with a four-CPU quota, llvmpipe and no GPU. Wall time including segment setup
and encoding was 1749.45 seconds (29.16 minutes); summed render and segment
encoder CPU time was 6513.80 seconds (108.56 CPU minutes). Peak resident
memory per process was 1.51 GiB. Muxing, review encoding, preview experiments,
a canceled early attempt, seam re-sampling and validation are additional to
these native-render numbers. No paid Render workflow was invoked.

Audio cannot be heard by this session. Every overlap was checked with the
picture, RMS and alignment measurements, but an ear review is explicitly
unverified. Tonality and pulse estimates can miss orchestral rubato or chord
clashes. Fine point grain can still crawl on small screens. The bodies remain
stylized: cloth and feet can slide slightly during the embrace approach and
assisted rise, and hand contact is less nuanced than live performance. This
is an independent finished comparison edit, not a claim of flawless acting
or a replacement for the owner's listening and creative review.
