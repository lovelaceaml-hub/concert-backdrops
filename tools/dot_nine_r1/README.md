# Nine Colours, faithful render-1 restoration

This is a separate Dot version. It does not modify another contributor's song or any shared engine file.

## Provenance

- Reference: `Film 10, Nine Colours (share).mp4` from run `43726203825`.
- Original choreography: `engine/songs/promo_nine_colours.py` at `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, preserved in `original.py` (typographic dash characters normalized).
- Modern engine dependency: `engine-p3d-words` at `afd2bd34cfe08e0b3fa9eead636776bf706eb7c3`.
- This is deliberately NOT the later v5 choreography from `3d8dbc4`.

The original camera ride, eight musical sections, nine comet paths, lake, hoops, hand dive, prayer orbit and dawn arch remain. Changes are local: modern gold point-body geometry, standing same-gender embrace, calmer gestures and prayer, sharper pill labels, gentler transition flashes, seven-second opening and final cards, and signature branding. No hard cuts or inserted freeze-frame montage. The source timeline begins after a two-second quiet lead-in.

## Audio

Use the original reference soundtrack, not new or generated music. The recovery render uses PCM decoded from the reference MP4's existing AAC stream; it is not a claim to possess the original lossless master. `original-score.wav` is the unshifted 60-second soundtrack used for music analysis. `score.wav` adds two seconds of silence without rearranging or changing the music. All media stays outside Git.

## Local rendering

Install the repository's normal Python rendering requirements plus `moderngl`, `glcontext`, `numba`, `librosa`, and `brotli`. Set up repository fonts with `tools/setup_fonts.py`. Supply the engine's `assets/p3d/body_v1.npz` and brand land mask normally. Place the reference score and features under `work/dot_nine_r1/`.

```sh
python engine/analyze.py --help
python tools/dot_nine_r1/render.py --stills '0,8,19.4,31,43,53,57' --scale 0.5 --outdir work/dot_nine_r1/checks
python tools/dot_nine_r1/render.py --range 0 3720 --scale 0.666666667 --out work/dot_nine_r1/silent.mp4
ffmpeg -i work/dot_nine_r1/silent.mp4 -i work/dot_nine_r1/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -t 62 -movflags +faststart work/dot_nine_r1/nine-colours-r1-dot.mp4
```

Native design is 1920x1080. Scale 2/3 is a 1280x720 review export, at true 60 fps. The adapter does not interpolate the old film. It re-renders every 3D frame. It forces software EGL only when no explicit override was supplied.

## Verification and boundaries

Local review export completed: 62.000 seconds, 1280x720, true 60 fps, 3720 frames, H.264 with stereo AAC. Full decode passed. Completed-film contact sheet and selected frames reviewed across all nine expressions and event cards. Original PCM music samples are unchanged after the two-second lead-in (16 samples of container padding trimmed at the 62-second boundary); AAC correlation is 0.999975, peak 0.737. Opening and final cards each have seven seconds of fully readable hold. The 120 Hz hand-anchor cache was checked against direct skeletal solves: maximum sampled position deviation 0.037 mm. Paired live-hand lag is disabled locally to avoid recursive raw-target evaluation; the explicit embrace remains. This is a 720p review export, not a 4K master. No full-suite tests, paid GitHub Render workflow, merges or protected-file modifications were performed.
