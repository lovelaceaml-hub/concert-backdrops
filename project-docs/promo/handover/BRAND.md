# Hand-over from helper BRAND (Opus)

## Branch
`engine-p3d-brand`, from origin/engine-p3d-words (f392c40) with origin/epic-medley2 merged. Pushed. No PR (WORDS2 merges
the branch). Documentation: engine/UPGRADE-HOWTO.md section Z (every call, key and recipe, with timings and limits).

## Files
- engine/p3d/brand.py: the logo (geometry, 2D picture, points, the `Logo` point set), `Place` (placing any flat piece,
  incl. riding the camera and gliding between places), colours; re-exports everything below (`from p3d import brand as BR`).
- engine/p3d/brand_hearts.py: `Hearts` (bokeh, sparkle, petal fields), `HeartDrift`, `HeartForm`, `arrange_heart`,
  `heart_places`, `heart_points`.
- engine/p3d/brand_symbols.py: the nine symbols as hand-drawn strokes, and six recipes `Traced`, `Constellation`,
  `PetalShape`, `LightTrail`, `Ripples`, `Flock`.
- engine/p3d/brand_world.py: `Globe` (night, space, day), `Finale` (world to logo, bloom into the pastel day, the logo
  into the end card place), `PASTEL` look, `land()`.
- engine/songs/demo_brand.py: the proof song (60 s on the medley); its world and finale are built by
  `world_moves(o)`, `world_pieces(camera, o)`, `world_p3d(camera, fin, looks, o)` (o: a time offset).
- engine/songs/demo_brand_finale.py: demo_brand 40 to 60 s as a 20 s song (the v2 proof).
- assets/p3d/brand/land_2048.png + README.md (Natural Earth 1:50m land, public domain), tools/build_brand_land.py.
- Shared files, tiny and backward compatible: a new sprite kind "heart" (api.py KINDS and its doc line, layer.py
  KIND_ID, shaders.py: sdHeart, the heart shape when sharp, the heart bokeh, flash and area for kind 8). Every other
  kind computes exactly as before.

## Done and seen (full-size 1080p stills here, scratchpad/brand/out/final2 (v1) and scratchpad/brand/out/v2d, v2s (v2); GitHub proof videos, see the report)
- Logo 2D: matched against logo_on_leaves.jpg and logo_clean.jpg by overlay (scratchpad/brand/work/compare.png,
  diff_leaves.png): hearts exact (classic construction, 45 degree sides), globe centre/radius measured, grid fitted
  (84 percent pixel agreement), branches placed from measured leaves. Palettes brand (default), web, poster.
- Logo 3D: build (hearts sweep, globe fill, ring and grid draw, branches grow), gather, fade; light or paint; leave
  rise/scatter/fade. Painted logo measured within about 15 levels of the brand colours on the pastel sky.
- Hearts: heart sprite kind (crisp and heart bokeh), fields, drift off a light, fireflies gathering into a heart.
- Symbols: all nine recipes rendered once each in the demo (16 to 40 s).
- World (v2, after the coordinator's review of proof v1): night globe with golden continents over a dark amber
  base, cloud wisps, a soft atmosphere, painted hearts that bloom with a pulse, arcs with a glowing head; day
  globe painted in the soft pastel clay colours of world_ref (no wash). v3: `cradle=dict(t0, t1, at=None)` on
  Globe and Finale, a warm light rising from below the globe where hands cradle it; MASTER's hands go at
  `FINALE.globe.cradle_at(t)` (or MASTER passes its hands' place as `at`).
- Finale (v2): painted in its exact colours from the first frame (no light mode, no halo); the ring draws round the
  Earth as its air fades, the grid draws over the Earth, the logo's globe spreads over it from the middle, the
  branches grow last (Finale timing=...); bloom into PASTEL at 54.3, warm pastel and capped (flash at most
  Finale.MAX_FLASH 0.3, peach and gold sparks): it can never white out; logo glides to ride=(0.5, 0.74, 14),
  frac 0.27, held to 60 s. Proof v2 approved by the coordinator (run 43746746484).
- Symbols (v2): Ripples stands upright just above the water and only its reflection wavers (flat only when
  seen from above); no rings; Encouragement's cuffs are forearms (rings and boxes read as UI). Rule from the
  coordinator: a symbol always reads as its shape, upright and facing the camera.

## Traps
- The render workflow's prepare job imports the song WITHOUT PIL: nothing in a song may need PIL or heavy work at
  import. brand.py loads PIL lazily (`_LazyPIL`) and `Logo`/`Globe` build their points on first use (`__getattr__`).
  If you add a piece, keep it lazy.
- Painting: a painted point set is composited over the 3D background only; P3D bursts and any light (L buffer) add on
  top of it and pale it. Hence: the logo's light alpha is multiplied by (1 - paint); paint batches use kind "disc"
  with alpha 1.6 (the shader clamps cover to 1; a disc keeps a third of its energy in its skirt, so alpha 1 leaves the
  fill translucent); the bloom's burst is small (strength 0.12, radius 0.25).
- Light colours: `show()` gives exact colours only on black; bloom and sky add. Light mode uses colours deepened
  (exponent 1.15) and white parts at 2.0 * white (0.35 default) to keep the brand hue.
- The left heart has no inner lobe in 2D (it would peek past the globe); in 3D the hearts are whole and their inner
  lobes go when the globe arrives (`inner` flag); the right heart is covered dynamically by the left heart's mask at
  its current offset (light mode). `globe_cover` (the Finale's Earth) hides the hearts behind a circle tested where
  each point is now.
- Place keys interpolate centre, axes and size linearly between two placements (a world place and a ride); a key's
  values may be functions of t.
- Python 3.11 on GitHub, 3.13 here.

## What is weak / next
- The bloom moment (54.1 to 54.6) is a brief dusk blue between night and pastel with sparks over the logo; the logo
  stays exact through it. Keep large P3D bursts away from the finale (a burst adds light over everything; the
  demo's cuts now blend the looks over 0.8 s instead of flashing).
- The cradle light was shaped without hands in the picture: alone it reads as a warm glow under the globe; check it
  with MASTER's hands and tune `width`, `glow`, `rise`.
- A soft halo round the painted hearts (Logo paint_glow) always read as a neon or burnt edge in tests: off.
- The light-mode logo's white parts read grey-ish at night; paint is the brand-true look.
- Gratitude (bowing person, side view) and Respect are the least obvious symbols at small sizes; the Compliment's navy
  is faint as light at night.
- Globe arcs are a short Python loop (one vector slerp per arc).
- No GitHub stills of the films using these yet; WORDS2 has not wired TITLES/end card to `logo_image` yet (as of this
  hand-over).
