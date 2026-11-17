# Film 05 Petals: hand-over for the new film

Branch `ten/05-petals`, head 09f700a. The only full render is run 43726415467: the first pass at 1b95fb4, made before any notes. Later states were checked in local stills only, in scratchpad/tenB/05/st2 to st5. The head (TITLES, acting library, website colours) was never rendered; the stills round that would have checked it was stopped.

## Moments that look best
- Run 43726415467, 9 to 12 s: the lake page. We look straight down on deep sapphire water, with "Gratitude" lying flat on it in light. In st5/t0010.50 a ring of small gold people round the words bows to them (Crowd kinds "bow").
- Run 43726415467, 19.5 to 24 s: the small tree bursts into pink and white blossom at the touch (the coordinator liked this). Petal words arrive and leave too ("petals" arrive and leave in words.py).
- st2/t0000.00: frame 0. A coral glitter woman in profile with a translucent coral coat, petals streaming from her open palm, the low sun. st2/t0004.50: "How are you?" on a dawn sky, with a small man shedding petals.
- st2/t0035.50 and st3: the violet gale with racing clouds and rain of petals behind light words. One look per section reads clearly (sunrise, sapphire, pearl, blush, azure, ivory, gale, breath, radiance, gold, cream).
- st2/t0058.00: the end card on a cream sky, with the tree of light low in the frame.

## The code (all in engine/p3d/ten_05_petals.py unless noted)
- `PetalWind(wind, n, box, amount)`: painted petals in a box that travels with the lens (wants_camera). They are carried by one `effects.Wind` with a gust on every section start, wrap only far away and fade at the box walls. Wrap it in `PW.KeepClear(..., WORDS)`. Amount in the song: `0.8*PETAL_AMOUNT(t) + 0.12*WIND.gust(t)`, so gusts fill the air.
- `Tree(colors, bough_az, bud, bloom, crown_t, petal_light, bloom_glow)`: a static set. It has a painted trunk, nine boughs winding up like a stair, and petal blossom whose `birth` times do the budding and the blooming per bough on the GPU. `glow_set(gain)` is its light as a separate set; the song fades it with camera distance (`tree_glow`).
- `Release(starts, t0, wind, colors)`: the crown lets go as a dome of petals. `Stream(source, target, t0, t1)`: petals blown from a palm to a target. `Rain`: blossom falling round a place. `PetalPath`: a carpet of petals unrolling on the water. `Meadow`: flowers on the mirror (too small to notice so far).
- `Painted(inner, fill=, fill_alpha=, words=)`:
  - paints a body's petal sprites in their colour;
  - lays a translucent coat of colour under the glitter, so a person holds form on a bright sky;
  - keeps shed petals out of a word being read.
  - `paint_word_petals(WORDS)` paints the words' flying petals.
- Song file engine/songs/ten_05_petals.py:
  - `St(x, z, view)` places stations relative to the view (forward, screen right, up).
  - `_w(...)` lays a word out by screen place and pixels per em on the layout rig.
  - `_L(...)` builds looks from display colours with `theme.display`; `LOOK_KEYS` blends one look per section.
  - `_gate_masks` switches each mask off outside its set's show time; without it, painted words were left out (two sky fills per frame).
  - `_clear` gives the keep-clear box for the end card. `TITLES` holds the opening, signature, date in light and end card.

## Camera moves worth reusing (`_moves` in the song)
- Up and over: a `fly` from eye level to about 10 m above the lake, looking down about 73 degrees (target 3 m ahead, so it never flips), then a slow rising dolly. The flat word reads from above.
- A spinning dive: the roll keys run 0, -36, -6, 0 over 1.7 s while flying down to half figures.
- A full barrel roll into the gale: `ROLL` goes 0 to 360 over 1 s on the section start (shutter 0.35, so it does not turn to mush).
- A whip that follows the petals to the next person (`blend` 0.3, a short bank).
- The climb: an `orbit` at radius 16 to 20 m, height 2 to 12 m, with the look rising. Each bough's azimuth matches where the camera passes, so the boughs bloom one by one in front of it. Then a pull back to the end card, with the tree in the lower third (camera about 41 m out, 3 m up, looking at a point 21 m high).

## What to avoid
- Blossom or crowds drawn as light from afar: thousands of overlapping glows add up to a white blob. Paint blossom with `paint=1, paint_light=0` and give the glow a gain by camera distance.
- `sun_glow` above about 0.4 turns a blue day sky lilac or pink. Keep it at 0.35 and choose sky_mid in clean blues.
- White words on pale skies. Paint them in a deep shade of their colour, or keep deep skies behind them.
- Never mirror words (`add_to(scene, reflect=False)`). The "lake" arrival shows mirrored text.
- Stepping stones seen edge on read as a glowing white bar.
- An open aperture looking toward a far bright tree puts white bokeh blobs on the words. Turn the shot away from it.
- Engine traps:
  - pairs.embrace with `show` placed bodies about 18 m away; fixed later on engine-p3d-bodies.
  - The gold_glitter preset disperses from t=1.0 by default (pass t, share).
  - Presets crash on facing or at keys given as lists.
  - Crowds bake for 20 to 50 s per render process.
- A person facing into the wind gets hair blown over the face; turn her so it streams back.
- From UPDATES 12 and 13: no window, star or dark silhouettes and nothing that dissolves (Mother's and the dancer's petal effects must go). Only crystal or gold glitter people, few of them.
