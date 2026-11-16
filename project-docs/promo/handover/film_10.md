# Film 10, Nine Colours: handover

**Current quality master, 2026-11-16:** one native 3840x2160, 60 fps, 10-bit export of the approved Revision 3 is complete and checked. Added composite grain is removed; the edit and exact music stream are preserved. The owner requested one highest-quality file. The 318,834,702-byte MP4 exceeds this connector's 104,857,600-byte Drive upload limit, so video transfer is pending and no smaller copy was created. The original is available in the Codex workspace and chat. The new quality file awaits owner review; prior approved files remain archived. [Quality record and checks](../QUALITY-NINE-COLOURS-R3.md).

## Approved creative cut, 2026-11-16

The owner approved **Revision 3**, 66 seconds at native 60 fps, and requested that it be saved, documented and uploaded. The exact source is `46df53b98a43f58e51a78d40ee5794108a68e13c`, tag `film10-revision3-approved-2026-11-16`, draft PR #71. [Approval record, video links, hashes and reproduction](../APPROVED-NINE-COLOURS-R3.md).

It builds from Film 10 render 1 (`d928ff9`, run 43726203825), with an extended opening, signature, updated expression capsules and serif text, Claude Final v1's golden listening pair for Respect, and a continuous swirling-light approach to Earth with orbiting expression symbols. The original medley and final accent are preserved. Its implementation is isolated under `tools/nine_colours_minor/`; do not overwrite shared song/acting files to reproduce it. No merge is authorized.

## Historical ten-film handover

The notes below describe the older ten-film development branch and remain as history. Its later passes and 62-second alternatives are not the approved Revision 3 delivery.

The branch is ten/10-nine-colours at 5a4b936, and the song file is engine/songs/ten_10_nine_colours.py.
- Last full cloud render: run 43734065813 (v5, before the finale and UPDATE 13).
- Pass 9 local stills (finale, TITLES): scratchpad/ten10b/s9a/ (open4.jpg, fin1.jpg, fin2.jpg, logo_zoom.png).
- Pass 10 (UPDATE 13 people, rivers, aurora, dawn skies) is pushed but was never rendered.

## Best moments
- 0.0 to 1.0 s, the prism: the seed blazes low over the mirror lake under the opening title, and on the hit it bursts flat into nine comets. Run 43734065813 at 0 to 1 s, and s9a/t0000.00 and t0001.00 for the calm-title version.
- The comet ribbons in every section. The best are the blue hoop gate at 8 to 12 s, the double helix round the embrace at 15 to 19 s, and the dancer's navy ribbon at 20 to 24 s. A white core with a coloured glow and shed sparks reads as pure energy.
- 45.65 to 49.47 s, the braid: the nine colours spiral round one column while the camera corkscrews straight up inside them (s9a/t0047.80). This is the hyperspace swirl, and it is the most thrilling shot.
- 40.25 to 42.51 s, "December 6" in light: TITLES date_light over the violet breath, bursting on 42.51 (s9a/t0041.60).
- 49.47 to 53 s, the world: the ribbons wrap a blue globe of light with continents, leaving hearts in their colours and arcs (s9a/t0051.50, t0053.00).
- 53.4 to 55 s, world to logo: the ribbons braid along two heart outlines round the globe, the grid and olive sprigs draw themselves, then a dawn bloom (s9a/t0053.90, t0054.50).
- From 55.6 s, the end card on a pastel day: the logo made of particles lands exactly in the TITLES end card logo slot, with its two flat colours (s9a/t0057.50, logo_zoom.png). After the slot fix, the shapes read as the real logo.

## The code that makes them (functions in ten_10_nine_colours.py)
- Comet ribbons are in `Comets._one`:
  - a white core ribbon, a deep-colour ribbon (`deepen`) and, in pass 10, a broad glow ribbon;
  - a head spark, a soft bloom, and 140 shed sparks per comet;
  - tails are limited at cuts (`CUTS`), dimmed inside word boxes (`_boxes`, `_dim`), and faded near the lens.
- Paths are `Head` with legs `(t0, t1, f, blend in, blend out)` blended over a base path.
  - Leg makers: `_pen(word)` (the comet is the word's pen), `_screen`, `_tunnel` (the hoops), `_helix`, `_ribbon_from_hand`, `_circle7`, `_braid`, and `_finale(k)` (the globe wrap, then heart tracing).
- `Hoops` is a static set with `birth` times, so the trail stays standing as hoops.
- `Seed` is the frame-0 blaze and its flat burst (`d[:,1] *= 0.15`).
- The finale:
  - `_logo_frame` places the logo from the end camera so that it fills the TITLES slot (y 0.044 to 0.202). `_L(x, y, dz)` is in logo units.
  - The sets are `Globe` (`LANDS` polygons give the continents), `GlobeShadow` (a black-point `Mask("dark")` hides stars behind the globe), `GlobeHearts`, `Logo` (outlines born where the ribbons pass, fills rising, white ring and sprigs) and `LogoFill` (`Mask("sky", sky="flat", color=hex, slot=0/1)` gives exact logo colours on the day sky).
  - BRAND's `p3d/brand.py` (logo, land mask, world to logo) has now landed and should replace these hand-built shapes.
- Other sets:
  - `Hearts`: hearts of light drift off each expression in its colour.
  - `Aurora`: pass 10, not yet seen.
  - `_gold_shaft`: world shafts over tender moments.
  - `ScreenClear` and `PW.KeepClear`: keep sets out of the word boxes.
- Words: all leaves are "fade", kept sharp in place by the `_clean_leave` drive. `_focus` racks focus only to words of the current section that are in front of the camera.
- Looks switch at each section (`LOOKS`, `WORLD["look"]`): "space" for the globe, then "pastel" (base "cream") from `DAY_T`, blended over 1 s.

## Camera moves worth reusing (all `Path(f, t0, t1)` or `fly(keys)`)
- `_flight_keys`: a low rollercoaster run over the lake at 24 m/s with a gentle roll (`_roll_s12`).
- `_s3`: a braking spiral into a pair, `r = 4.35 - 0.11u + 20 exp(-u/0.34)`. It feels like landing.
- `_s4` and `_s4_up`: an orbit round the dancer, then a half loop over her (`_loop_phi`, with an `up` function).
- `_s7_braid` and `_s7_up`: a corkscrew up inside the braid, the view tilting to straight up, with fov 64 widening to 94.
- `_s8`:
  - an orbit round the globe that pulls back (`az` -75 to 0 degrees, distance 2 to 3.5 RG);
  - then back along the logo normal to frame the logo;
  - then a slide and tilt down to the end camera, so the logo rises into its slot while the day blooms.

## What to avoid (learned the hard way)
- Big bursts (strength 1.8 or more) and white blooms give white frames. The look blend alone is a good bloom.
- Sky masks hold their layer while a body is hidden. Gate and speaker windows stole the logo's flat colours until `_while_shown` gated their mask strength. Only two sky layers exist.
- A mask needs alpha 0.2 or more on its points. Use black points with alpha 1 to make a shape with no light.
- Racking focus to a word left behind at a cut gives huge bokeh discs. Filter by section and by the camera's forward direction.
- An S8 sun blending from -12 to 40 degrees crosses the frame. Keep `sun_el` the same in both looks.
- Comets bursting upward cross the opening title. Keep them low, and add `OPENING_BOX` dimming while the opening shows.
- Hands at 1 m read as thin wisps unless they are framed level and centred (lower half), with bright 1.6. The best close-up was demo_p3d_words's.
- Mannequin, dark rim, window, shard, disperse and dissolve people are all out (UPDATE 12 and 13). Use only crystal glitter (#d6eaff with white) or gold glitter (#ffcf7a with #fff1d6).
- Engine notes:
  - `pairs.embrace(approach)` was fixed in BODY2. I still give the walk-in by hand (approach=0).
  - The navy (#364E96) needs a lighter glow colour for light (`GLOW`).
