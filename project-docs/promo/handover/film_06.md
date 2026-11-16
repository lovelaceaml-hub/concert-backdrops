# Film 06 Ascension: hand-over (branch ten/06-ascension, head 667e58b; song engine/songs/ten_06_ascension.py)

## Best moments (run id, seconds)
- 43729225319 (full render 3), the night half 0 to 36 s: a gold glitter traveller in a narrow blue shaft under stars; rings of light hung in the air under each pair; the wide reveal of hundreds of coloured pillars on the black mirror lake (15 to 16.5 s); the old man kneeling on the glowing gold ring (17 to 19.5 s); the two hands reaching in deep violet fog, gold from above and blue from below (39.5 to 42 s).
- 43732983879 (render 4): the embrace on the glowing ring (12.5 to 14.5 s); kneeling prayer beside a child in the shaft (35 to 38 s); the hands (39.5 to 42 s); Mother from behind, veiled, holding the traveller's hand against a gold sunrise over a rose sea of cloud (44 to 46.5 s); the Compliment with people raising hands (47.5 to 49.5 s). The two large rim-lit profiles (29 to 31.5 s) were called the best image, but the dark rim look is now banned: redo them in gold or crystal.
- Local stills (no run): scratchpad/tenB/06/st10/ (TITLES opening over the shaft, "December 6" in light above the reaching hands at 40.9 and 42.3 s, the bloom at 54.5 s, the new end card on a pastel day from 55 s).
- 43737452632 (render 5, dispatched before UPDATE 12, still running at hand-over, not reviewed): first full render with TITLES and the climb finale.

## The code (all in the song file)
- Camera: `CAM_KEYS` (t, azimuth, distance from the shaft, height, look at, fov, aperture) interpolated by `curve()` (monotone cubic, Fritsch and Carlson) separately in azimuth, distance and height, so the path is a true spiral and the height never falls; `class Spiral(Move)` feeds it to `Rig`. `_far()` puts a near look target far along the same line (no violent view swing into a macro); `_focus()` then focuses on the real subject (the hands) separately.
- Staging: `pair(k, gap)` puts two people face to face across the shaft, square to the camera at `C[k]`, both in profile; `near_side()` picks the hand on the camera's side; `_facing_check()` proves nobody is seen from the front.
- People rise whole: `_ascend(y0, t_up)` is a Body `frame` (moving ground) that lifts off; `_streams(t_up)` is a "shed" effect streaming light upward. `LiftStream` is a spiral of sparks that climbs with the camera on each launch (the hero of the fast rise). `_hand()` is Hands with a show window and keyed finger poses (relaxed, open, spread, hold at the touch).
- Contact workarounds: `_embrace()` and `_hands_held()` copy p3d.pairs.embrace/hands. Engine bugs worked round: pairs.embrace's walk-in placed people about 8 m apart; both pairs helpers raise KeyError when a body's effects ask its pose while it is built (gesture targets read the other body before it exists): `_safe()` returns a guess until the body exists.
- World: `LOOKS` lake, mist, pillars, gate, violet, cloud, cloudlit, above (deep sunrise), high, card (pastel day); the cloud passage is the ground mist with `mist_height` 150 then 26 (a whip through fog, not a solid cloud); `SUN_AZ_TRUE/SUN_EL_TRUE` put the sun exactly behind Mother's head at `T_ECLIPSE`, with the world `light` there for rays. Point sets: `Pillars` (columns of rising flakes plus soft ribbon cores, lit in a wave outward), `Rings`, `ShaftFlakes` (window round the camera height), `RingWave` (frame 0 hit), `Fountains`, `Hearts` (heart outlines in the nine website colours, billboarded), `CloudTop`.
- Words: `_w()` sizes each word by pixels at mid reading (`PW.em_for`); `_IN` = reveal along the reading line, `_UP` = fade with the `_sharp` drive (letters stay put and sharp while they thin out). These were the only arrivals and leavings with no garbled frames. `layout()` checks screen boxes. `PW.KeepClear` wraps flakes, pillars and fountains. `WORDS.add_to(scene, reflect=False)`.
- `TITLES`: opening t_end 3.8 y 0.28; signature in calm stretches (15.95 to 16.75, 25.8 to 27.6, 32.75 to 34.4, top right); date_light 39.45 to 42.51 above the hands; end_card t_in 55.0 on the pastel "card" look.

## Camera moves worth reusing
- The continuous crane up: one unbroken spiral, about 70 degrees of turn per level, slow rise during each reading, then on the hit hold 0.35 s on the people rising, then an "elevator whip" of 0.6 s straight up 18 to 20 m to the next level, landing level and already framed (keys around 7.2, 20.35, 27.15, 33.8, 38.65 s).
- The wide swing out over the pillars and swoop back in (15.1 to 17.3 s).
- The macro orbit on the two hands at 1.15 to 1.25 m, with the date in the sky above them, held in focus through the touch.
- Out of the cloud straight to the two from behind, the sun on Mother's head (42.95 to 45.6 s); then the climb high over the sea of cloud and the bloom into a pastel day (50.6 to 55 s).

## Avoid
- Word arrivals palm, shaft, rays, stars and morph, and leavings rise, wind and arch: scrambled or smeared letters in sheet frames.
- Dissolve and form effects on people, rim (dark) looks, dots (blow out white), plexus: all banned or ugly now.
- Big soft wisp sprites near the camera (purple blobs), a Flare or burst plus exposure above about 1.1 at a touch (white-out), launch frames with only sky (fill them with the risen people's light).
- A focus window that ends before the subject leaves (the hands became bokeh at the touch).
- Building Body objects at import: the workflow's prepare job imports the song with numpy only; build the cast in setup (`_cast()`).
- The QA "calm bottom third" flags every frame with people at the bottom while the camera moves; the old TITLE/TAGLINE legibility checks misfire once TITLES has an end card.
