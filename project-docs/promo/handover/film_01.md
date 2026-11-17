# Film 01 The Wave: handover (branch ten/01-the-wave)

Song: engine/songs/ten_01_the_wave.py. Film helpers: engine/p3d/ten_01_wave.py (pure numpy). Head 33ad28e.
Full renders, newest first: v5 43736976097 (head 20f48a9: TITLES, acting, finale not yet in; finished successfully, not reviewed),
v4 43734143630 (acting v1), v3 43732759920, v2 43728929332. Frame sheets are in each run's "frames" artifact.

## Best moments (run, time)
- Frame 0 and the drop (v4, 0 to 1.2 s): a spark with a comet tail falls down a thin shaft onto a black mirror of
  stars; it meets its own reflection on the opening hit.
- The ride along the crest (v4, 1.6 to 3.8 s): camera 30 cm above the water beside a rope of gold light that
  arcs away into the dark. Night ahead, lit wake behind.
- The barrel tunnel (v3 and v4, 20.6 to 24.4 s): a tunnel of streaming gold line segments, curtain on one side,
  the mouth as a door of light ahead. This was the most exciting image.
- The look back at dawn (v4, 9 to 12 s): violet glass, a rose dawn horizon, gold glitter people with long
  reflections, the crest running across the frame.
- The lanterns (v4, 15 to 19 s): hundreds of floating lanterns light in a sweep as the crest passes. Warm bokeh.
- The helped-up pair on the crest top (v4, 34 to 37 s) against the dawn split sky.
- The wall of light (v4, 41 to 46 s): the wave stands 24 m high; kneeling people in front. It reads as a starry
  curtain more than a wall.
- A warm sunrise over the mirror lake with the arch lights (v3 and v4, 50 to 52 s). No white-out.

## Code that makes them
- Kinematics(speed keys, height keys, curl keys, drop, t_impact): the wave is a ring round the drop point. The
  radius is the integral of the speed (so speed keys are easy to time to the music). wp(u, b, h, t) puts things in
  the wave frame (u along the crest, b behind it, h above the water). KIN.time_at(x, z) gives when the crest
  reaches a place. Everything that wakes uses that time as its birth time.
- Wave: particles flow around the cross-section profile(s, H, curl): up the face, then over the back (swell) or
  out along the lip (barrel). It also has a spark rope on the crest, a back glow and spray. The mouth(t) key
  ends the curl along the crest. A size and fade limit near the lens (_lens) stops huge discs at the camera.
  The two density centres (centers=) keep it dense where the camera rides.
- Tube: short line segments along the same flow, dense over a stretch of u. This makes the barrel.
- Field (static points with birth = crest time + delay, flash): wake glints, lanterns, sea lights.
- Ignite: wraps a Body. Cold, sparse blue dust before the crest reaches it, then gold from the feet up.
- Clear: wraps any point set so it dims inside every expression's reading box (and a badge box). It fixed every
  "something crosses the words" note. Use pad 1.6 for big bright sets.
- Hearts: heart outlines of sparks that drift off a person in the expression colour (website colours, HEX).
- FarRing and disc_glints (finale, committed, not rendered yet): the whole ring and the whole sea lit gold,
  seen from 600 m up.
- At the head, dry run only and not rendered (UPDATE 13 look): Aurora (waving curtains, rose and gold at the
  foot, violet above), GlowClouds (cloud banks lit from within), Blossoms (flowers of light that open where
  the crest passes), prismatic spray (_hsv), CRYSTAL look (glitter plus rim, no mask), shafts over each act.
- Words: every expression rides with the camera (ride=(x, y, depth), em from PW.em_for at mid-reading,
  reflect=False). Leaving uses wind plus a fade drive (_fade), so no broken letters show. Apology becomes
  Inclusiveness by morph.

## Camera moves worth reusing (all Path(f, t0, t1) moves: f(t) returns pos and target, usually in wave frame)
- cam_ride: low beside the crest, looking along it (night on one side, wake on the other).
- cam_barrel: punch through the face (blend 0.5, burst 0.55), then glide along +u inside the tube at
  b = -0.66 H, h = 0.42 H, then out of the mouth turning back.
- cam_face, then cam_orbit_w1: a half-figure profile as the light climbs a person, then a slow swing out to
  a two-shot in profile, so a bow reads.
- cam_run: level with the crest top just ahead of it (b -4.9), people on the crest, dawn behind them.
- cam_break (finale, not rendered yet): climb to 640 m with the ring, then lift the view to the pastel sky.

## Avoid
- Mirrored words, a corner badge, and white bursts (keep strength at or below 0.6 and use keep_hue).
- Bright streaks or the crest behind a word: wrap every moving set in Clear.
- Two expressions read at once. A reveal or rise in a sheet frame shows broken letters.
- pairs.embrace with a late walk-in: it measures the walk from t = 0 and puts the two people about 30 m apart.
  Place them yourself (see _performances).
- Window and rim looks (dark blobs and statues), crowds of sleepers (too many small people), people falling
  apart. Big gold glitter bodies close to the camera read best.
- Empty frames when the camera rises above the crest and looks at the sky. Keep the crest or people in frame.
- Body-heavy parts take about 20 minutes per part on GitHub. Give every body show=(t_in, t_out).
