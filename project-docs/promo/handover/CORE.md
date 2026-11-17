# Hand-over from helper CORE (Fable) to its Opus successor

## Branch and PR
Branch `engine-p3d`, head a1262fe. PR #53 "Engine: 3D layer (camera, particles, world)" into epic-promo, open, not merged; text updated to this head.

## Done and proven
- Camera test video, approved by Anthony: run 43720966507 at commit 02466ae. Artifacts "Camera test, revolving" (full and silent), "(share)", "frames", "QA". Song engine/songs/p3d_camera_test.py, 28.5 s on audio/test/camera-test-28s.mp3 (cut from the s01 promo clip from 31 s; committed).
- Base layer (at 02466ae), engine/p3d/: api.py, camera.py, layer.py, shaders.py, world.py, plus five guarded hooks in engine/render.py. Song key P3D = dict(camera, world, setup, sets, bursts, motion_blur, motion_samples, keep, lod, bokeh_max, clear). HOWTO section V documents every key.
- Cloud runs viewed at full size: stills 43719032668, 43719478691, 43720572352 (camera test); 43720050702 (test_p3d: dark mask with rim, rays behind a head, sky-fill mask, shaft, burst, every sprite kind, 2D words on top); draft 43720064786.
- Songs without P3D unchanged: t_short_test and epic_concert byte-identical against base 20b4f6e; t_short_test re-checked at head.
- Frames independent of render order: camera test, test_p3d, test_p3d_ten at head.
- Speed at 1080p on GitHub: camera test 0.41 to 0.78 s a frame; feature test about 0.93 s; one video part of 86 frames took 79 s.
- Reading moments (measured at an earlier commit): 40000 points 0.2 px wide keep total light within 0.003 percent across a one-pixel slide; a point on the focus plane identical at aperture 0 and 0.2; dof=0, fog=0 equals a sharp clear batch; blurred against sharp light within 4 percent.

## Half done (all in commit a1262fe, "for the ten films"); proof only half-size frames of engine/songs/test_p3d_ten.py rendered locally plus the order check
- Seen working: paint (coral petals stay coral on a day sky), window world (Mask("sky", sky="world", look=...) with window=True sets), split sky, arch in nine colours with travel and yaw, birth times on a static set, continuous ribbons with pulses (ribbon, Trail), Rig(free=True) with righting, moving light pools on the water.
- Runs but not judged: keep-clear boxes, calm discs, lit, star_turn, pulses on lines, dolly zoom (keep_width), rack focus, near plane 0.02, shake, pace, Rig(parent=), Parented (self-check only).
- Never rendered: motion_samples (layer.draw), bokeh_hex, keep, 4K, 60 fps. Draft mode not re-run since the layer rewrite.
- Looks golden, day, cream retuned and the sky gradient changed (skyBase in shaders.py, LOOKS in world.py); only day seen afterwards; test_p3d_looks.py not re-rendered.
- Cloud run 43720981639 (test_p3d stills with the whip) finished; its stills never opened.
- Where: camera in camera.py (_Pace, Rig._carried_up, Rig.state); passes in layer.py (_draw_sets(paint=True), _sky, _clear_boxes); world in world.py (calm_at, lights_at, split_at, dome_rot, state_of, Arch); shaders lakeAt, born, lights, keepAt, SEG_VS/SEG_FS.

## Remaining needs, in order
1. Camera: all items exist in some form. Untested: motion blur at 40 m/s, pull-backs across kilometres (shore fixed at 1400 m, hill rings at 1.4 to 5.2 km, dome at 3000 m), passing through a real dense sheet (the giant-sprite fade is built).
2. Lines and ribbons: motion blur for segments not built; tens of thousands of segments not load-tested.
3. Points: hue-preserving highlights not built. Fast path for 2 to 3 million points not built: every sprite is an instanced quad, about 0.1 s per 200 thousand small points on four cores, doubled by the mirror pass. Exposure Track and bursts exist.
4. World: mirror and ripple by place is four discs only, not a field. Skies by place only the two-look split by azimuth (sun and lake colour stay the main look's). One window world per frame, not nested; all "sky" sets share one mask. Moving lights have no rays of their own; only the single light= does.
5. Arch: built, unproven beyond half-size frames.
Plus from WORDS: CORE's mask is half size and blurs at least 3 px (layer.py starts soft at 3.0 and takes the max), holds one sky and one tint per frame, and has no flat fill. Asks: a flat fill, soft below 3 honoured, fill state per mask.

## Traps
- The approved video is not head: after 02466ae the sky gradient, day looks and default near plane (0.08 to 0.05) changed. Render 02466ae for an exact match.
- Buffer layout must stay in sync across layer._slot, layer._vao (CORE_FMT, 13 floats; the mask VAO skips bytes with padding) and the shaders. Segments reuse the rot slot as aUV.
- moderngl raises on unused attributes: every declared attribute must stay used.
- The mask pass sets a MIN blend equation and resets it afterwards; an exception in between leaks state.
- A whip blends two set-ups through space, so the camera can fly through objects for a few frames.
- free=True builds a 120 Hz table of the whole rig at first use; an expensive pace or look function slows start-up.
- Texture unit 15 is shared with the 2D camera of section O; a song uses one or the other. (Silk figure tint uses unit 14, symbol paint unit 16.)
- Local worktree clutter ignored by git: fonts/ copied from the scratchpad; work/<song>/features.npz for test songs are copies of the camera test's analysis.
- The shell refused compound commands containing git and most heredocs: separate plain git commands and script files.
- CORE's own quick check script: scratchpad/core/local_check.py (half size, two threads).
