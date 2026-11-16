# A World Made Gentle

An independent 62-second creative alternative for Anthony's concert promo.
This is a new visual treatment and seven-recording edit, separate from Claude's
masterpiece and from the earlier Astra comparison in PR57. Anthony decides what
is used. This branch is a draft and must not be merged automatically.

The owner explicitly selected a new independent video and seven-song edit after
clarifying that the pasted speed/QA assignment was not the scope of this turn.
The shared handbook was checked on docs/promo-handbook at
2db9544ccdc6de8d83fd4acd0b6fe0a18bc6cee5.

## Creative treatment

A fixed, gently breathing viewpoint watches a garden of light grow through nine
kind exchanges. Each expression awakens a coloured petal. The petals gather
around the Earth, the nine campaign symbols orbit it, and it resolves into the
official logo. The closing card rests on a warm cream and peach field.

- 0 to 8 s: the full opening title is readable from frame zero, holding for
  seven seconds. Mother's hands hold a drop of light. The drop falls and starts
  a ripple as the title leaves.
- 8 to 44 s: the nine expressions each have a four-second scene and 3.18 seconds
  of settled reading. The lettering uses the campaign colour definitions. People
  stand below the words, clear of the lower-left concert signature.
- 44 to 48 s: the illuminated petals lift toward the world.
- 47 to 54 s: the Earth forms, the nine symbols circle it, then the globe becomes
  the campaign logo.
- 55 to 62 s: the full official-style end card remains readable. Gentle motes
  keep it alive while the final musical chord decays. No fade to black.

The camera, garden, light paths, drop, scene timing and score are new. The
encouragement scene uses two newly staged standing women to avoid the source
kneel exposing a disconnected-looking shin. Consideration uses two standing men
with an offered hand, avoiding an awkward leg extension in the helping-up pose. Reviewed
performances from songs.master_astra are reused as cast assets, transformed and
retimed without changing the shared acting implementation. This is not a claim
that the engine, brand assets or human performances were created from scratch.

## Music

Only the existing concert recordings are used. There is no generated music.
The order is 09, 08, 04, 05, 11, 01, 03. The 112 bpm editing grid uses a
compound-pulse interpretation for 09, 08 and 04. That interpretation comes from
beat analysis and still needs a human listening review. Pitch is preserved with
ffmpeg atempo. Six equal-power 2.143-second blends use a bass handoff and local
level matching. The last source's closing chord lands at 57.5 s; its decay
continues to 61.8 s. The first two seconds are silent.

The generated score-report.json records source positions, tempo factors,
normalisation and measured levels. It remains private with the generated audio.
Level and chroma measurements do not establish that a musical transition sounds
natural; Anthony should listen before choosing this version.

## Isolation and reproduction

This branch is based on compare/astra6-concert at 10e347f. The draft PR targets
that branch to show only the new treatment. It relies on PR57's opt-in end-card
motes and reusable cast. No existing song, master effect, acting, audio or
workflow file is changed here. The entry point loads film.py in memory as a song
module, without creating anything under engine/songs/. A process-local Titles subclass
fades the opening dust out by 8 s so it cannot cross the first expression. The
opening remains fully readable for seven seconds.

Use the normal engine dependencies and fonts from the handbook. From the repo
root:

```sh
python tools/gentle/music.py
ffmpeg -v error -y -i work/gentle/score.wav -ac 1 -ar 22050 work/gentle/audio.wav
NUMBA_CACHE_DIR="$PWD/work/gentle/numba" OPENBLAS_NUM_THREADS=1 python engine/analyze.py work/gentle/audio.wav work/gentle/features.npz
python tools/gentle/render.py --stills 0,6.9,10,14,18,22,26,30,34,38,42,46,49,52,54,57,61 --outdir out/gentle/stills
python tools/gentle/probe.py
python tools/gentle/export.py --workers 4 --parts 8
python tools/gentle/verify.py out/gentle/A-World-Made-Gentle-1080p60.mp4 out/gentle/A-World-Made-Gentle-review-720p60.mp4
```

Everything renders locally in the execution environment using software OpenGL.
Do not dispatch the paid GitHub Render workflow. Both exports are native 60 fps,
3720 frames, 62 seconds. The review copy remains 60 fps at 1280x720.

Generated files stay in work/gentle/ and out/gentle/. Those directories include
source analyses, the edited PCM score, features, body/cloth and shader caches,
raw-frame hashes, render parts, logs and finished videos. They may be deleted to
clear this film's private outputs and caches. Do not commit them or fonts.
The exporter refuses to reuse parts after its source manifest changes. Move the
old parts and manifest aside together before regenerating changed input.

## Checks and limits

The raw frame probe compares fifteen 1080p frames near three part boundaries and
within both new standing scenes in
sequential and shuffled fresh processes. The encoded-file checker inspects all
frame timestamps and native frame hashes, half-second motion differences and
jitter, the seven part joins, audio clipping, lead silence, six quarter-second
join envelopes and the final second's level. It reports the busiest motion
intervals for visual inspection. These metrics cannot certify natural acting or
musical flow.

Full-size stills and dense strips are reviewed before delivery. Output-specific
numbers and any remaining concerns are recorded in VALIDATION.md after export.
