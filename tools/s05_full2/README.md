# Song 05 "God Bless You!": full-length concert backdrop, version 2

One continuous 60 fps 1920x1080 video: the live length 159.0 s and a 15 s calm hold, 174.0 s, 10,440 frames. Timeline and reasons: `project-docs/backdrops/s05-full2/TIMELINE.md`; cues, acting plan, checklist and status beside it.

Built on the approved Revision 3 craft: the pinned Film 10 engine (commit d928ff9) with Claude Final v1 bodies (commit f43f451), restored privately by `tools/nine_colours_minor/prepare.py`. Nothing in the approved promo, the engine or other songs' files is changed.

| File | What it is |
|---|---|
| `timing.py` | stage time and reference time: the live length, the hold, 60 fps, the conform factor K |
| `song05.py` | the engine song module: camera, spring looks, the arch (and its lit history), the scene, symbols, hearts list |
| `cast05.py` | the four people of light (gold glitter, painted gold for the bright sky) and everything they do |
| `effects05.py` | the light of the story: tree of blessing, seed, stepping stones, waves of peace, prayer light, voice, petals, far shores, road of light |
| `words2d.py` | the words' layout and times (exact campaign wording from engine/p3d/words.py), the Clear wrapper |
| `overlay05.py` | the 2D layer: calm bottom third, opening card, top-left signature, the navy words and their effects, hearts |
| `render05.py` | stills, or one range of frames to a video part |
| `export05.py` | parallel parts, join, the stage, review and phone files |
| `verify05.py` | length, sync, frames, signature, first and last frames |

## Run (cloud only, never on the Mac)

```sh
# setup as in project-docs/backdrops/HANDOFF-FULL-BACKDROPS.md section 4 (apt, pip incl. scipy, fonts)
python tools/nine_colours_minor/prepare.py
curl -L -o ../s05.m4a "https://drive.usercontent.google.com/download?id=1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D&export=download&confirm=t"
python tools/s05_full2/render05.py --audio ../s05.m4a --stills 0,30,118 --scale .5 --outdir out/s05_full2/stills
python tools/s05_full2/export05.py --audio ../s05.m4a --workers 4 --parts 12 --outdir out/s05_full2
python tools/s05_full2/verify05.py --video "out/s05_full2/05 God Bless You! - Backdrop v2 - review 1080p60.mp4" \
    --audio out/s05_full2/music_conformed.wav --frames out/s05_full2/check
```

`--stills` takes stage times in seconds. The song audio stays outside the repo; outputs go to the outdir (untracked). About 2.2 CPU seconds per 1080p frame on the busiest stretches, plus a minute or two of cloth warm-up per part.
