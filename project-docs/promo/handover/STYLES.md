# Hand-over from helper STYLES (Opus)

## Branch
`engine-p3d-styles` (pushed), from origin/engine-p3d-words, with origin/epic-medley2, origin/engine-p3d-bodies (6b3a65e) and origin/engine-p3d (8902405) merged in. No PR (the coordinator or WORDS2 merges it into engine-p3d-words).

## What it adds
- `engine/p3d/styles.py`: `ST.add(scene, "<preset>", name=, sky="night"|"day", **keys)`. Fifteen presets: constellation, spark_profile, sky_window, gold_glitter, ember_dancer, ash_dissolve, mist_figure, star_silhouette, glass_shatter, butterflies, dark_silhouette, nebula_figure, nebula_profile, glitter_profile, constellation_profile. `ST.listing()` prints them.
- `engine/p3d/faces.py`: `Profile` (a drawn head and shoulders in profile: brow, nose, lips, chin, closed eye with lashes, ear, jaw, neckline; looks sparks, glitter, constellation, rim, ink, fill) and `Hair` (long hair as a mass of flowing locks; `BodyHead(body)` lets a Body wear it). Own geometry, no third party asset.
- `engine/p3d/stylekit.py`: Dressed, Backdrop, Butterflies, Sparkles, GlitterMist, CloudPuffs, Flock, Billows, PaintedShape, Nothing.
- Engine changes (small, backward compatible): sprite kinds "shard" and "butterfly" (api, layer, shaders); a "nebula" window fill with a light placed at a world point (`Mask(sky="nebula", color=, glow=dict(at=, strength, density, scale))`); effects take `batch=` (dict or list of dicts merged into their batches); the mask pass no longer gives a sky layer to a masked set that draws no shape this frame (that was a real bug: in a song with several masked figures at different times, a figure not yet on screen pushed a visible one's window out).
- `engine/songs/demo_styles.py`: every preset in turn, 3.75 s each, 60 s on the concert medley. `STYLES_FLIP=1` flips every stage's sky (checks the other palette).
- HOWTO section Y2, "People styles" (section Y is TITLES on engine-p3d-words): every preset, its keys and limits.

## Checked
- Local stills (1080p, shared script) of all 16 stages over six rounds, the last in scratchpad/styles/st6 (as designed) and scratchpad/styles/flip2 (each stage on the other sky). Earlier rounds st1 to st5, flip1.
- Byte-identical frames for an existing song: test_p3d_bodies at 2.5, 6.5, 34.5, 42.5, 50.5, 70.5 s with and without the shared-file changes (scratchpad/styles/cmp_base, cmp_mine).
- Proof video: GitHub run 43736317327 at commit 47af161, artifacts "Styles proof", "Styles proof (share)", "Styles proof frames", "Styles proof QA" (QA fails only on the test song's missing end card and a busy bottom third), parts part0 to part9. Frames sheets in scratchpad/styles/proof1/frames.
- Branch head after the proof: 1fff458 (day palettes for constellation and mist_figure, not rendered: the last local render was stopped on the coordinator's word).

## Anthony's reaction to the proof, and the stop
- Coordinator first: the best four were spark_profile, nebula_profile, the starry profile with flowing hair (butterflies preset) and ember_dancer. Fixes asked (not done): glass shards bigger and angular, from the body; the starry hair softer and finer with stars in it, butterflies clearly visible; the eye glow small and warm; gold_glitter's pale sky under clipping; constellation and mist figure also at half-figure size; every style checked for men and women of different ages (a child and an elder profile drawing are not built).
- Then Anthony: "Those look terrible and scary." The coordinator's reading: dark featureless silhouettes, bodies and heads breaking apart (shatter, ash, dissolving heads), the glowing eye, stark empty backgrounds. All work stopped; new direction pending.

## Traps
- Light only adds: on a bright sky every preset uses `sky="day"` (painted grains, or a flat dark silhouette). A night preset on a day sky washes out.
- One dark layer and two sky layers a frame. Flat silhouettes of the same colour share a layer. With more different fills use `silhouette="paint"` (PaintedShape) for the extra figures.
- The nebula and star fills are screen space, placed by the shape's box: two figures sharing one fill share one box.
- Profiles read best within about 35 degrees of side on.
- World dust shows as white specks over dark fills on a bright sky; lower `dust` in that look.
- `_body` pops the body keys out of the preset's kw: read `at` before it (mist_figure once placed its mist at the origin because of this).
- Shell: heredocs with git are refused; patch files with small Python scripts in the scratchpad (scratchpad/styles/tools/patch*.py show the pattern).

## Weak, in order
1. Faces: profile only, eyes always closed, two drawn heads (no child). The nebula face's billows can read as round bubbles.
2. Butterflies are small and soft; at 1080p their wings read but not their pattern.
3. ember_dancer uses the CMU "jump" clip; a real leap with a pointed foot (p04) is not in the motion library.
4. gold_glitter's dispersal eats one side of the head first, which can make the head look pointed for a moment.
5. Hair on a Body follows a circle round the skull and does not collide with the shoulders.
6. No preset for hands in close-up (Hands of section W already does refs 04 and 14).

Scratch: scratchpad/styles (renders, tools, refs crops), scratchpad/styles/base_wt (a copy of the engine with the shared files from before this branch, for byte comparisons).

## UPDATE 13: two approved looks (crystal_light, gold_glitter)
- New direction after Anthony's reaction: perfect two looks only. `ST.person(scene, "crystal_light" | "gold_glitter", name, **body_keys)`, or `ST.keys(style, **body_keys)` for pairs then `ST.dress(scene, name, body, style)`. The fifteen old presets are parked: `ST.add_parked` (demo_styles.py uses it), `ST.add` refuses them; the old gold_glitter (which blew apart) is now `gold_dispersal`.
- Body looks `"crystal"` (prismatic fresnel edge, cut-glass facets that shimmer together and fine light on their cuts, luminous clear body warm at the heart, inner light, glints) and `"gold"` (deep amber, gold and champagne grains, inner light, glints) in engine/p3d/looks.py.
- stylekit: Glow, LightTrails (past poses on a fixed time grid, reused), Bloom, HandLight, LightRiver, Aurora (smooth curtains), CloudBank.
- Engine: batch setting `front` (far side of a body dims; shader uniform uFront, default 0 = unchanged); a look layer may carry its own `seed`.
- Proof song: engine/songs/demo_heavenly.py (five tableaux on the medley sections, 34.9 s). Commit dc7dce8. GitHub run 43741980999 ("Heavenly proof").
- Local stills: scratchpad/styles/hv1 (white wash) to hv5 (final); face lab in scratchpad/styles/lab1, lab2.
- Faces: the body's face is a smooth mannequin; looks.face_marks paints gentle features (closed eyes, brow, nose, lips) as light and shade, and crystal has an even soft face layer so the face is luminous, never hollow. Long hair (hair=True) hangs over a clear face seen from the front: keep the bun or a cap.
- Byte check: test_p3d_bodies at six moments identical to the baseline with the front setting in (scratchpad/styles/cmp_mine2).
- Trap: light only adds. The first round of stills (scratchpad/styles/hv1) was a white wash: big CloudBank sprites, mist and a light straight behind the people. Skies must stay deep (dawn, dusk, predawn, night bases); CloudBank far and high at alpha 0.012.
- Trap: pairs.embrace(approach=...) starts each person about 7 m out (BODY2's _walk_in returns a time as a distance). Use approach=0.
- Trap: a dress on a woman kneeling then helped up left a floating piece of hem; tunic is clean.

## Proof v2 (coordinator review of v1: not yet breathtaking)
- Merged origin/engine-p3d-words afd2bd3 (BODY2 fixed embraces: cheek past shoulder, mixed holds, walk-in fixed; hair "short", "bob", "tied", "covered"; build).
- Anthony's rule: every touching moment between two people of the same gender (parent and child the exception). v2: the embrace is two women (gold and rose gold), the lift two women (gold lifts crystal).
- New in stylekit: GodRays (far sun behind a CloudBank gap gives slanting rays; near source + small tail gives a beam on someone; sprites dipping into the ground fade), CloudBank rewritten (billows with crisp shells, gold lining, rose and violet shade; no lens blur, out of the mirror), Aurora rewritten (fine vertical rays, bright lower edge, folding curtains). LightTrails memoises past places.
- Crystal: thin rainbow bands along the silhouette (hue runs up the body, so colours are seen), weaker white edge, clearer heart light.
- Framing: full figures 60 to 80 percent of the height, slow orbits.
- Traps found: places beyond the lake shore (1400 m from the middle) stand on a flat plain (it read as a pink or orange floor); GodRays sprites crossing the water plane made a hard pink plane; pairs render at 30 to 60 s a frame (cloth stepped with the embrace solved against the partner).
- Local stills: scratchpad/styles/v2a to v2h.
- Proof v2: commit 8840e51, GitHub run 43751661203 ("Heavenly proof v2").
- v2 run 43751661203: all ten render parts finished; the finish job (join, music, QA, share copy) was refused by GitHub billing ("recent account payments have failed or your spending limit needs to be increased"), also on re-run. Parts joined locally the same way: scratchpad/styles/proof3 (Heavenly proof v2.mp4, (share).mp4, sheets/). No QA report.
