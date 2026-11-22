# Ten cinematic films

## Active owner direction

The owner rejected the unrelated 2D recovery sketches and requested the ten final cinematic films in the actual concert project. This work returns to the original native 3D renderer, using the approved Song11 beauty study and Nine Colours Revision3 as visual references. The ten films each run twenty seconds.

## Source ownership

| Area | Writer |
| --- | --- |
| Film1 solo, film2 ensemble, film4 calligraphy; dancers.py and dancers_motion.py | recover_history |
| Film3 world-to-people, film9 orrery; cosmos.py and cosmic_models.py | cosmic_films |
| Film6 garden, film7 birds, film8 underwater; nature.py and nature_models.py | nature_films |
| Film5 procession, film10 reunion; people_worlds.py | root |
| Shared song clock, render adapter, scene registry, project manifests, delivery, QA and source freeze | root |

Existing approved engine, figures, camera rigs, geometry, brand and words modules remain intact. This suite adds isolated authored scenes and an explicit registration for every film. The source branch is `creative/cinematic-ten-films`.

## Films

| Film | Title | Visible action and camera |
| --- | --- | --- |
| 1 | Silk in Light | Close solo performance, traveling supported steps, turns, substantial pleated fans and finite silk |
| 2 | Petals in Motion | Five full-body dancers, staggered travel, fan petals and changing ensemble composition |
| 3 | One World, Many Hearts | Real land-mask Earth, Africa illumination, traveling camera, cut to a moving human welcome |
| 4 | The Written Light | Distinct robed performer drawing sustained strokes from the solved hand |
| 5 | Procession of Lanterns | Traveling full-body procession through deep vaulted architecture, hand-held and rising lanterns |
| 6 | A Garden Awakens | Flowers opening in depth, butterflies and a moving camera into a growing luminous garden |
| 7 | Wings of Peace | Jointed bird flight, articulated feathers, banking, flock motion and a mirror lake |
| 8 | Ocean of Light | Pulsing dimensional jellyfish, fish schooling, currents and a traveling underwater camera |
| 9 | Celestial Clockwork | Layered kinetic rings, planets, orbiting lights and an architectural observatory |
| 10 | Together in the Light | Greeting, arrival, reciprocal gestures, community response, expanding light and a final message |

## Reference provenance

Three owner-supplied continuous screen recordings are now available and inspected for broad movement and staging. The dances are original authored choreography, not recovered motion capture. Automatic pose estimates from covered feet remain unreliable; the authored support paths have their own bounded contact check. A contact check does not establish physical balance or source choreography fidelity.

Recovered actual approved media:

- Song11 beauty study: SHA256 `6e4533c4527dfb81c750f8ba907e86392f0c87dca638c3daac768ece8edae82a`.
- Nine Colours Revision3 phone comparison: SHA256 `ad4b4e7fe861ae34eb80e8b921ee747efc477c08bb89ec981f1b588a0b3c0af5`.
- Earlier fan-silk trio, retained as prior unapproved performance evidence: SHA256 `36166e43ae67a0ea9e7d52313bf223ca0ee373ed555c69728ccab0e3cfb62afe`.

## Rendering and recovery

All films target native1920x1080 at60fps, two temporal samples, RGB8 SDR under the existing legacy_display_gamma convention. The engine-supported half-resolution sky pass affects only the soft procedural background; subjects, text, geometry and composite are native full size. Cloud CPU only. No paid generation, downloaded visual assets or local Mac GPU.

Prepare source audio and manifests with `python -m tools.cinematic_ten.prepare_projects`. The original Song07 and Song11 recordings must match the current production catalog. Other selected music comes from the inherited short promo excerpts. Every twenty-second excerpt preserves source speed, records the source hash, and receives an80ms opening fade,700ms ending fade and-1dB gain. Authored action does not claim precise instrument synchronization.

Render a native keyframe with `PYTHONHASHSEED=0 python -m tools.cinematic_ten.render --film 1 --stills 2,8,16 --out work/cinematic-ten/qa/film01`.

Render and assemble the explicit projects with `python -m tools.cinematic_ten.run_suite --projects 2`. Each film uses two single-thread workers and300-frame chunks. The existing pipeline checks source identities, writes atomic PNGs, resumes matching frames, assembles audio, checks technical delivery and builds a gallery. Use the existing STOP markers to stop between frames. Do not mutate picture dependencies during a final round.

Technical checks, sampled visual review and exact-output owner approval are recorded separately. New outputs do not inherit approval from the reference films. Final media, receipts and review images stay outside Git; source and reproducible instructions remain in the project repository.
