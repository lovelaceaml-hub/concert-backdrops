# Song 05 "God Bless You!": full-length concert backdrop

One continuous 30 fps 1920x1080 video: the song (153.15 s) and a 15 s calm hold, 5045 frames. Timeline and reasons: `project-docs/backdrops/s05-full/TIMELINE.md`.

Built on the approved Revision 3 look: the pinned Film 10 engine (commit d928ff9) with Claude Final v1 words and bodies (commit f43f451), restored privately by `tools/nine_colours_minor/prepare.py`. Nothing in the approved promo or in other songs' files is changed.

| File | What it is |
|---|---|
| `song05.py` | the engine song module: camera, world looks, arch, timing, what goes in the scene |
| `cast05.py` | the four people of light and everything they do (touch only between people of the same gender) |
| `words05.py` | the words: title, three short fragments, Encouragement and Consideration twice each and together in the hold (adapted from the song 01 words lane) |
| `effects05.py` | the light of the story: tree of blessing, seed, stepping stones, waves of peace, prayer light, petals, far shores, road of light |
| `render05.py` | stills, or one range of frames to a video part |
| `export05.py` | parallel parts, join, music plus 15 s of silence, master and share copy |

## Run (cloud only, never on the Mac)

```sh
# setup as in project-docs/backdrops/HANDOFF-FULL-BACKDROPS.md section 4 (apt, pip, fonts)
python tools/nine_colours_minor/prepare.py
curl -L -o ../s05.m4a "https://drive.usercontent.google.com/download?id=1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D&export=download&confirm=t"
python tools/s05_full/render05.py --audio ../s05.m4a --stills 30,66,100,136,149 --scale .5 --outdir out/s05_full/stills
python tools/s05_full/export05.py --audio ../s05.m4a --workers 4 --parts 12
```

The song audio stays outside the repo. Outputs go to `out/s05_full/` (untracked). Each part warms up its people's cloth from the last still moment (cast05.SEG), so a part costs a minute or two more than its frames.
