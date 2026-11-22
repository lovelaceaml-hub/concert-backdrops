# Cinematic Ten authored motion

<!-- cinematic-ten-final-movie-evidence:begin -->
## Final movie evidence addendum

All ten twenty-second films are complete, technically passed, reviewed within the recorded sample scope, and saved. The overview, README, technical records, checksums and complete ZIP are also saved. No Cinematic Ten owner approval is recorded.

Exact identities are in [the final delivery evidence](evidence/cinematic-ten-final-delivery.json); actual per-film scope and findings are in [the complete review evidence](evidence/cinematic-ten-complete-review.json).

The motion catalog now has a separate `authored_scores.final_movie_evidence` map for all ten registered films. The original inventory below and each entry's dated `review` remain unchanged. Whole-movie technical evidence does not extend the earlier numerical contact, costume, flight or biomechanical verification scope.
<!-- cinematic-ten-final-movie-evidence:end -->

Recorded November 21, 2026, America/Los_Angeles. This is a reusable source and partial-review inventory. It does not certify completion, encoded final QA or owner approval of any whole film. Those milestones remain in [STATE.json](STATE.json) and the [delivery catalog](catalogs/deliveries.json).

The `authored_scores` section of [catalogs/motions.json](catalogs/motions.json) records six new score/integration entries, exact source-file SHA256 values, supplied recording identities and scoped review findings. The existing eight prepared clips, seven capture identities, candidate statuses and earlier inventory date are unchanged.

## Provenance

The new solo and ensemble choreography consists of original authored curves, support targets and inverse-kinematic poses. The supplied moving recordings informed fan sweeps, levels and ensemble canon. They were decoded and visually inspected in this round; earlier repository notes about unavailable moving footage describe an earlier state.

| Supplied recording | Verified use in this round |
| --- | --- |
| `ScreenRecording_11-21-2026 12-19-51_1.mp4` | Close solo fan reference, one foreground performer in a green top and red skirt |
| `ScreenRecording_11-21-2026 12-20-32_1.mp4` | Wider ensemble fan reference |
| `ScreenRecording_11-21-2026 12-24-09_1.mp4` | Illuminated globe reference for film 3; no dancer choreography assignment |

The catalog retains their SHA256 values and supplied Library file IDs. The calligraphy score was independently authored for the brief; no supplied recording demonstrated that wrist score. The flight scores are authored procedural motion. None of these new scores is a new motion-capture recording or a reconstruction of the supplied performers. **The earlier automatic estimates of feet hidden by skirts were not verified in this round and were not used as measured support contacts.**

The human form still uses the existing MakeHuman-derived `body_v1.npz` asset and native rig. Walking scenes retain the existing prepared `walk` clip, CMU **35_01**, plus authored staging and procedural gestures. Their underlying gait therefore retains the provenance documented in [MOTION-LIBRARY.md](MOTION-LIBRARY.md), [the import recipe](../../tools/build_p3d_motion.py) and [asset README](../../assets/p3d/README.md).

## Human score API

[dancers_motion.py](../../tools/cinematic_ten/dancers_motion.py) defines `DanceScore(TrioPerformance)` and `install(body, mode="solo", role=0, delay=0.0)`. It reuses the existing [fan performance](../../tools/concert_fan/performance.py) `Step`, support interpolation and diagnostics. The new score supplies palm paths, body levels, torso/head gestures, heading, travel and **24 explicit alternating steps**. Legs are solved after upper-body acting; the score disables the automatic ground/contact correction for those authored targets.

| Mode | Registered integration | Scope |
| --- | --- | --- |
| `solo` | `dancers.build(1)` / `cinematic-ten-01` | Two held fans; rising spiral, lateral opening and offering; finite silk on the solo props |
| `ensemble` | `dancers.build(2)` / `cinematic-ten-02` | Five role-dependent paths and ten fans; roles 0 to 4 use delays 0.42, 0.20, 0, 0.32 and 0.60 seconds |
| `script` | `dancers.build(4)` / `cinematic-ten-04` | Expressive right-palm writing with a balancing left hand and grounded travel |

Each score covers 20 seconds and holds its resolved endpoint rather than looping. `delay` is in seconds: `score_time` clamps `(t - delay) * 20 / (20 - delay)` to 0..20, compressing delayed performers to finish together. The current scene bodies are approximately 1.66 to 1.684 metres tall; targets scale from the inherited 1.65-metre reference. Other proportions, arbitrary delays, durations or external gesture overrides need a new proof.

Install before `Body.where`, joint/body sampling, cloth sampling or effect-track construction:

```python
from p3d.body import Body
from tools.cinematic_ten.dancers_motion import install

body = Body("woman", height=1.66, garment="dress", hair="bun")
score = install(body, mode="solo", role=0, delay=0.0)
# Configure the costume, attach props and add the body using dancers.py's setup.
# score.contact_report(samples=81) is a diagnostic API, not an approval gate.
```

[dancers.py](../../tools/cinematic_ten/dancers.py) supplies `PleatedFan(grip, ...)` and `SilkOnly`, which inherits [FanSilk](../../tools/concert_fan/props.py). Their frame comes from the final solved palm through `hand_frame(t)`. Only the solo adds the finite silk sheets. Its inherited deterministic simulation includes body-capsule collision; it does not provide cloth self-collision or collision with other performers.

For calligraphy, construct `Calligraphy(body)` after installing `mode="script"`. It samples the right palm at 60 Hz over 0..20 seconds, smooths the historical track with a nine-sample Gaussian sigma, and corrects the live stroke tip back to `body.where(t, "palm.R")`. Three strokes retain, enlarge and rise after writing. They are abstract flourishes, with no claim of accurate lettering or reproduced handwriting.

## Walking and attached lanterns

[people_worlds.py](../../tools/cinematic_ten/people_worlds.py) exposes `build(5)` for five lantern bearers and eight following walkers, and `build(10)` for an arrival, a welcoming shuffle turn and joining people. [cosmos.py](../../tools/cinematic_ten/cosmos.py) `build(3)` supplies six walking arrivals after the globe transition. They use the existing `Body`/`Actor` travel and contact system, authored speeds/phases/stops, and gestures including `wave`, `raise_hand`, `hand_on_heart` and `open_arms`.

`HeldLantern(body, seed)` places the lantern below the solved right palm and joins it with a cord. Its sway is authored; this is not a simulated grasp or pendulum. Root and nature-agent reviews of films 5/10 found no blocking clipping, detached lanterns or missing bodies in the reviewed native stills. No new numerical planted-foot, stride-matching or physical-balance test was recorded for these walking integrations.

## Flight APIs

[nature_models.py](../../tools/cinematic_ten/nature_models.py) supplies:

- **`AirborneDove(index=0, scale=3.0, seed=7)`**, integrated by `nature.build(7)`. It subclasses the existing [Dove](../../tools/concert_addons/models.py), retaining fixed-length shoulder/elbow/wrist wing articulation and feather helpers. The new flight state, continuous torso-neck-head surface, beak/tail arrangement, eight-bird formation and glide phases are authored here. The bird stays airborne throughout 0..20 seconds; this round does not exercise or verify the base model's launch/landing contacts.
- **`WingWake(bird)`** samples root history at 110 times over 2.6 seconds, with two world-X offsets of +/-0.85 metres. These are artistic trails, not anatomical wingtip tracks.
- **`ButterflyFlight(count=11, seed=33)`**, integrated by `nature.build(6)`. Two paired fore/hind membranes articulate at an authored base flutter frequency of 3.1 Hz, with a traveling leader and delayed formation. The body, wings and antennae turn toward the path. The fixed garden path is not a validated general flight planner or seamless loop.

## Recorded verification and limits

The dancer implementation agent reported the following `contact_report(samples=81)` measurements, transcribed rather than rerun for this documentation. Samples span 0..20 seconds at **0.25-second intervals**; values are rounded.

| Score checked | Maximum ankle-target error, m | Maximum consecutive planted-ankle step, m | Minimum sampled foot-vertex height, m |
| --- | ---: | ---: | ---: |
| Solo, role 0 | 4.85e-16 | 5.67e-16 | 0 |
| Ensemble, role 2 | 3.56e-16 | 4.89e-16 | -2.91e-10 |
| Script, role 0 | 5.01e-16 | 8.94e-16 | 0 |

These small kinematic residuals do not establish force-driven balance, matching to reference feet, all five ensemble roles, every shutter subframe or costume collision freedom. Prop attachment was inspected visually; no independent numerical attachment residual was recorded.

Native evidence under `work/cinematic-ten/qa/` includes:

| Scope | Evidence and finding |
| --- | --- |
| Solo | `film01-native-final/` at 16 and 19.5 seconds: the lowered late fan clears the head and the final full body remains framed |
| Ensemble | `film02-native-final/` at 8 seconds: five complete bodies and ten readable held fans |
| Calligraphy | `film04-native-final/` at 8 and 19.5 seconds: substantial wrist-origin strokes and clear body/foot margins |
| Walking | `film05-native/` at 2/9 seconds; `film10-native/` at 2/9/18 seconds; `film03_final/` at 12 seconds. Film 3's registered frames 500..579 also verify the camera cut without shutter ghosting; the authored gold wipe clears by approximately 9.42 seconds |
| Dove | `nature07_native/` at 0/2/9/17/19.9 seconds. `nature07_motion_08s_report.json` records 72 unique decoded native frames over 8..9.2 seconds, with pipeline frame 540 pixel-identical to the reviewed 9-second still |
| Butterfly | Corrected `nature06_forward/t002.00.png`; leader forward/velocity alignment sampled 11 times over 0..20 seconds, minimum dot product 0.9982788. Earlier `nature06_native/` composition frames predate this orientation correction |

The dove proof predates the butterfly-only change in the shared module. Its exact earlier source hash is retained in the catalog/report; bird geometry is unchanged, but that short proof is not a final whole-film source-identity check. Bird batches were reported finite at 0/2/5/9/13/17/19.99 seconds; no separate numerical joint-length, aerodynamic or biomechanical test was recorded. The butterfly numerical direction check covers its leader only.

These working artifacts are ignored render outputs, not committed media or an archive receipt. The durable catalog preserves the scoped findings and source identities. Keep subsequent continuous costume review, final encoded movie review and exact-output owner approval separate from this motion inventory.
