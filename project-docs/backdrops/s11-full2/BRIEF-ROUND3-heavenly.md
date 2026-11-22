# Round 3: heavenly, like the approved promo

Anthony watched the music-video draft: "It's still not epic. It needs to be beautiful, gracious, and heavenly. It needs to match the promo video with the lights and has to be very, very interactive and feel that way. We should be able to feel how amazing it is and its power, which the song is trying to express through rays of light, performances, and dynamic cinematic shots."

He chose, from the promo (the approved Film 10 R3, source: /home/user/concert-backdrops/work/nine_colours_minor/render1/engine/songs/ten_10_nine_colours.py, read its header and how it uses comets, lights, rays, lanterns, bursts and glitter bodies):
1. Dark misty heavenly sky (done in the core: deep night blues and violets with glowing mist until the coda's sunrise at 201.73; light now blazes against it).
2. Rays and shafts of light.
3. Nine comets of light in the nine colours that fly through every scene, wrap the subjects and lead the camera.
4. Lanterns rising on the thanks lines, huge coloured bursts on the slams, close-ups of finely detailed glittering performers with gestures on the hits.
Camera: flowing flight plus cuts. Long sweeping graceful flights chasing the comets (through the choir, up the church, over Zion), cuts on the big downbeats hidden in flashes.

## What changed in the core (tools/s11_full2/s11_full2.py; read it)
- **The edit is now 70 blocks** (longer flowing flights). `blocks_of(owner)` gives yours; each needs one shot with exactly that t0 and t1. Re-key all your shots: make each block one graceful, dynamic flight with several keys (spline), sweeping, craning, orbiting, flying through or past the subject, often chasing your comets; the core still applies the music pace (faster on hits and loud passages), shake on slams and a lens punch on hits. Cuts are on big downbeats only.
- **`Comet(head, color, t0, t1, trail=1.4, width=0.35, bright=1.0, fade=0.6, light=False, seed=...)`**: a comet of light with a glowing trail along head(t) (a function giving a position at any time). Add your comets as point sets in add(scene). Use 3 to 9 comets per scene in `COL9` colours; make them wrap your subject (helices round the church, weaving through the orchestra and choir, streaming up Zion's stairways and round the terraces, leading the procession, spiralling with the hearts and round the sun and the Earth). The camera should chase them in some blocks. `light=True` makes the comet also a moving coloured light that tints the mist and lays a pool on the sea: use it on at most two comets at any moment (the world shows the 4 strongest lights film-wide).
- **`add_light(pos, color, strength, radius)`**: a moving coloured light (e.g. Mother's light, a glowing harp). **`add_rays(pos, strength, color, size)`**: a great light whose rays fan out over everything; the world shows the strongest ray source at each moment. Register ray sources for your big moments (strength 0 when not yours): e.g. the church's crown light and Father's pulse, the choir and orchestra blazing on the slams, Mother's light, the crown on Zion, the sun and the Earth's edge. Keep rays behind or beside the words, not burning through them.
- Lanterns rise round Zion on 109.8 to 117.5, 188.27 to 197.2, 238.8 to 254.07 (core; frame them beautifully if your blocks are there). Slam bursts are now promo-strength.

## Your job this round
1. Re-key every block you own (exact t0/t1) as flowing, gracious, dynamic flights.
2. Add your comets, ray sources and (if useful) moving lights, all reacting to the music (`beat_pulse`, `hit_pulse(t, KICKS)`, `intensity(t)`).
3. Make your subject glow beautifully against the dark sky: rich colour, glitter, no flat grey, no white-out; phrases readable.
4. Keep frame cost about as now (Comet is cheap; keep n modest).
5. Only your own file; no git; s11_light.py belongs to the core (ask in your report if you need a light change).
6. Check with quarter-size stills at the middle of each of your blocks (one background batch), then a few at half size.
7. Be quick: Anthony wants to see each section as soon as it is ready. Aim to report within about 25 minutes. Report briefly with still paths.
