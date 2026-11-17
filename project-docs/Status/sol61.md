# GPT-6.1 Sol independent concert comparison

Branch: `compare/sol61-concert`. Starting point: v6, `b7895aef771f4dcdbb7a3383afeab235fd945b6e`.

This is an independent creative edit. It reuses the v6 scenery and brand assets, with a new song module that changes the composition only inside its own Python process. It does not change the baseline module on disk. Neither competitor's work nor PR #55 is part of this change.

## Creative treatment

The musical arc is welcome, reconciliation, memory, blessing, generosity, conviction, celebration. Seven sources in order: 07, 04, 03, 05, 06, 11, 01. The first three share B flat; the final four share C, with a tonal lift at the blessing. Small formant-preserving pitch adjustments and local tempo adjustments join measured beat groups. The first six excerpts share a 3:2 pulse between faster and slower groups; the final orchestral coda keeps its faster cadence and release. All six music overlaps are about 2.31 seconds. These are edited excerpts, not complete songs or a live concert arrangement.

The soundtrack starts after exactly two seconds of digital silence. The final selected orchestral attack feeds early reflections and a decaying hall response. It stops introducing attacks at 57.38 seconds and resonates through the close. A 0.3 second taper removes only the residual floor at the file boundary.

The pictures use thirteen gently moving views. Complete pictures dissolve over 0.8 seconds, rather than rapidly flying the camera between distant stages. Words stay anchored in the frame during the dissolves. The ascent opens onto a golden panorama before the globe and campaign logo.

All nine performances are adapted: reciprocal shallow bows; a measured hand-on-heart bow; a standing low-handed apology; a welcoming arm round a shoulder; a low open palm at the doorway; quiet standing conversation; prayer with a companion; a slower supported rise; and chest-level applause received with a hand on the heart. No twirl or kneeling apology is used. Golden grain remains, while scenery glints become soft points and shader twinkle is disabled for the added scenery and people. The sparkle carpet behind Respect is removed.

The approved copy, true campaign logo, event date, time, venue and palette remain. The closing card receives a slow 2.5 percent push. Its explicit exit and a complete-picture release to cream finish with the music. The cream lasts only the final nine frames; it is an intentional punctuation, not a frozen seven-second card. The Sol label is in filenames and MP4 title metadata, not over the campaign design.

## Reproduce locally

Requirements: Python with numpy, scipy, librosa, moderngl, pillow, fonttools, brotli and soundfile; ffmpeg with `rubberband`; npm for the fonts. Software OpenGL via EGL and llvmpipe. No additional Python dependency is introduced.

From the isolated worktree root:

```sh
mkdir -p /tmp/fs
cd /tmp/fs
npm --cache /tmp/npm-sol61 pack @fontsource/cormorant-garamond@5.3.0 @fontsource/jost@5.3.0 @fontsource/outfit@5.3.0
for f in /tmp/fs/*.tgz; do
  d=/tmp/fs/$(basename "$f" .tgz)
  mkdir -p "$d"
  tar xzf "$f" -C "$d"
done
cd /absolute/path/to/sol61-concert
python tools/setup_fonts.py /tmp/fs fonts
python tools/sol61/build_medley.py
ffmpeg -y -i work/sol61/sol61-medley.wav -ac 1 -ar 22050 work/sol61/audio.wav
python engine/analyze.py work/sol61/audio.wav work/sol61/features.npz
export SONG=sol61_peace
export AUDIO="$PWD/work/sol61/sol61-medley.wav"
export FEATURES="$PWD/work/sol61/features.npz"
export P3D_CACHE="$PWD/work/sol61/cache"
export OUT_RES=1080p OUT_FPS=60 LIBGL_ALWAYS_SOFTWARE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 LP_NUM_THREADS=1
export MESA_SHADER_CACHE_DIR=/tmp/mesa-sol61
python tools/sol61/render_all.py
python tools/sol61/check_media.py work/sol61/Sol61-Concert-1080p60.mp4 work/sol61/Sol61-Concert-review-720p60.mp4 work/sol61/sol61-medley.wav
```

Use `tools/sol61/render.py` for the intended edit: it composites both moving views at a dissolve and applies the closing push and release after the titles. A direct `engine/render.py` invocation can inspect the song, but omits those complete-picture finishing operations. Range indices are global and end-exclusive. The full range is recomputed from the song and checked as 3720 frames at 60 fps. Five parts cover `[0,744)`, `[744,1488)`, `[1488,2232)`, `[2232,2976)`, `[2976,3720)` with no overlap or gap. Review scaling preserves every temporal sample.

Generated soundtrack, features, frames, videos, logs and caches belong under `work/sol61/`; fonts remain under ignored `fonts/`. Commit only construction code and this account. No workflow is invoked by these instructions.

## Validation record

Baseline artifact 14183747908 from run 43769618192 was downloaded without a workflow invocation. Its encoded review is 1280x720, 30 fps, 1860 frames and 62 seconds. Dense frame sequences show the kneeling apology's extended arm, the fast changes of viewpoint and the contorted twirl. Baseline and revised short motion clips were extracted/rendered for inspection, alongside the full-film framing contact sheets.

The preliminary raw-frame split check at frame 1488 matched SHA-256 for both compared frames against continuous evaluation of frames 1486 through 1489. This verifies a fresh renderer's deterministic evaluation at that boundary, beyond checking only encoded part lengths.

Final encode checks, render cost and remaining limitations are recorded after the completed local render below.

## Log

- 2026-11-16: isolated v6 worktree created; notice posted on PR #55; baseline downloaded; campaign copy and repository design guidance read.
- 2026-11-16: independent score construction, moving-shot edit, all nine acting changes and complete-picture finish implemented. Framing stills, a 60 fps Apology clip and a 1080p60 Compliment clip rendered locally. A first render pass was stopped to improve tonal compatibility before the final run.

- 2026-11-16: final audit found that the finale helper copied the world look list. Corrected the two remaining zero-duration colour switches in the actual P3D world configuration. The current local run replaces those two 84-frame windows; a fresh render uses the corrected configuration directly.

## Limits of this review

Visual inspection used dense frame sequences extracted from short encoded motion previews, including Apology, Compliment, the opening transition, the colour correction and the final eight seconds. This is stronger than isolated framing stills, but it is not a real-time playback review. The session explicitly rejected audio input, so listening to the six joins with their pictures was not possible. Musical flow, vocal phrase continuity and Rubber Band pitch-shift artifacts remain listening checks for the comparison, rather than claimed successes from envelope or key metrics.

The people remain stylized particles. Small hand contacts are approximate. Cloth still interpolates 30 Hz snapshots; outputting 60 distinct camera and effect samples does not turn that into a 60 Hz simulation. Some natural star shimmer remains. The moving end card is deliberately calm.

For this local delivery, two middle parts are reassembled with corrected colour and Concession windows at CRF 16, which adds encode generations to retained middle frames. A clean run of the committed script draws the corrected timeline directly and does not need that repair.

- 2026-11-16: full-size final inspection found the doorway and petals obscuring Concession. Their light now eases down while the phrase is read and returns as it leaves. Re-rendered global frames 1344 through 1538 for the local delivery.

## Finished local delivery

Final master: `work/sol61/Sol61-Concert-1080p60.mp4` (86,952,868 bytes). Review: `work/sol61/Sol61-Concert-review-720p60.mp4` (19,268,386 bytes). Both have audio, 62.000 seconds, 3720 decoded frames and 60/1 fps. Every one of the 3719 presentation intervals in each file is one 60 fps sample. Master audio and video both start at 0.000 and end at 62.000 seconds. The final encoded frame was inspected and is the deliberate cream release.

All six join picture sequences, the revised Concession view and the final eight seconds were inspected after assembly. The original Apology reach and stray kneeling foot are avoided by the new standing performance. Compliment uses the quieter paired response. Listening remains unverified for the reasons above.

Main render: 33.6 minutes wall time; 104.9 summed worker-minutes including startup. Runtime: llvmpipe (LLVM 19.1.7), Mesa 25.0.7, Python 3.12, ffmpeg 7.1.5, five available CPU cores, four concurrent main render jobs. Previews, targeted repairs and encoding are additional.

The source ranges and all replacement windows cover `[0,3720)` without overlap or gap. Raw checks at frames 1488/1489 and 2976/2977 matched fresh independent renderer evaluation; the actual part headers were checked too. Final timing checks were repeated after the last repair.

The master SHA-256 is `61b573651f22c25a996298a3655263c1ba613b16075dafd6584c197c02f63607`. The review SHA-256 is `7ff358f57593d10a158584d81ea201f7642ae273edb1d7aa3bfad07af028d0f2`.

Draft PR: https://github.com/lovelaceaml-hub/concert-backdrops/pull/56 . Findings posted on the coordination thread. A private draft release upload returned HTTP 401 at GitHub's upload host; no media was uploaded, and the empty draft release was removed. The finished files remain in the task workspace and are linked in the chat delivery. No media is committed. No workflow was invoked or anything merged.
