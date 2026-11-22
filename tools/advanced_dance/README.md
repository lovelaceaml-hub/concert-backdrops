# Advanced Dance

Two complete 32-second dance performances for the existing luminous concert
world. The solo revises Film 01, Silk in Light. The five-person ensemble revises
Film 02, Petals in Motion. Their projects are `advanced-dance-solo` and
`advanced-dance-ensemble`.

The other eight Cinematic Ten movies retain their delivered pictures. The
delivery helper replaces only the first two movie slots in a newly named
ten-film package and verifies the retained eight against their original hashes.

## Performance and musical clock

Each performer has eight eight-count phrases, 96 explicit step events and two
turning runs containing three full step turns each. The 64-count body phrase
follows the source-specific estimated beats in `clock.json`; an active coda
continues the arm opening and breathing over a settled double support until
32.000 seconds. The dance does not acquire its pace by speeding up a previous
movie or its recording.

| Counts | Phrase | Visible action |
| --- | --- | --- |
| 0 to 8 | Launch and opening fans | Preparation, rising arms, complementary fan levels |
| 8 to 16 | Diagonal traveling sweeps | Quicker alternating steps and sweeps through depth |
| 16 to 24 | Three traveling step turns | Sixteen steps carry three turns, with high and low fans |
| 24 to 32 | Low circles and rebound | Plie, torso phrasing, compact low arcs and recovery |
| 32 to 40 | Quick side chasses | Faster lateral stepping and alternating directional accents |
| 40 to 48 | Answering fan canon | Distinct outer and inner roles, timed answers, shared phrase arrival |
| 48 to 56 | Turning crescendo | A second three-turn run with rising light accents |
| 56 to 64 | Expanding flower and offering | Shared fan opening and a controlled arrival |

The ensemble's left pair turns in the opposite direction from the other
performers. Its local hand canon occurs only in the answering phrase, rather
than offsetting the entire movie. Roles meet the phrase boundaries and finish
together. Traveling paths, level changes, fan folding, grip-bound light trails,
landing accents and stage lighting use the same absolute clock.

The supplied close and ensemble fan recordings informed pacing and gesture.
This is original authored choreography. Feet hidden by skirts and finger motion
were authored, not recovered as reliable motion capture. Beat estimates remain
machine-derived; the project does not claim live rehearsal conformance or
instrument-by-instrument hit approval.

## Corrections in the actual rig

`score.py` authors support intervals, path, pelvis, torso, head, palms and feet.
The foot lands facing the middle of its upcoming support interval. This avoids
leaving a flat support foot far behind a rapidly turning pelvis. Each knee's
solve follows the actual foot direction, distributing the turn through the hip.
The posed sole geometry is checked when setting swing-foot clearance.

Breathing is applied before final hand and foot placement. The actor's later
automatic breathing pass is disabled for these scores, so it cannot move an
already solved palm or planted foot. Torso preparation leads the upper-body
phrase; it is not independent camera or sparkle motion.

Directional palm cues are fitted smoothly to each posed shoulder and actual arm
length with a bent-elbow margin. `gesture_fit_report(t)` records the raw cue,
fitted target and fitting distance separately. `anatomy_report(t)` reports the
final hand solve against that fitted target. A large cue-fitting distance is a
reason to revisit the phrase, even when the final IK residual is small.

`anatomy.py` addresses two observed defects in the earlier hand path:

- The old helper could overwrite a solved wrist with an unrelated world-space
  hand orientation. The new hand follows the solved forearm, with smoothly
  bounded wrist flexion, deviation and twist.
- A palm-normal preference nearly parallel to the forearm could be normalized
  into a rapid pronation flip. Its projected magnitude now decreases smoothly
  near that ambiguity, and the pronation preference is bounded without a
  previous-frame state.

Finger groups curl progressively around the fan handle. The thumb uses an
authored opposition and abduction fit toward the index side. An unheld hand has
a separate released shape. The rendered fan, handle and effects all use
`grip_frame(body, t, side)`, which is derived from the final posed hand. They do
not follow a second animation target that could drift away from the grip.

The anatomy report's `target_error_m` is the actual measured palm residual.
`reach_correction_m` describes projection of the iterative virtual wrist goal;
it is not the physical displacement of the hand. Use the separate raw-cue fit
report and actual palm residual when reviewing a reach.

The costume remains native geometry with fitted clothing beneath a pleated,
flared skirt. The fixed-step solver and body collision proxies handle its
motion. Exact solver snapshots can be reused through `cache.py`; loading them
does not resample the pose, approximate the cloth or lower render resolution.
The current costume code and its frozen receipts define the actual settings.

## Reproduce a production round

Start at the repository root and follow `AGENTS.md` and the production-system
handoff. Use an isolated branch. Install the locked CPU environment and exact
reference fonts if they are absent:

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
```

Prepare the two music excerpts from their hash-verified source recordings:

```bash
.venv/bin/python -m tools.advanced_dance.prepare audio --mode all
```

This creates stereo 48 kHz PCM24 masters at original playback speed, with
constant gain `0.630957`, a 60 ms fade-in and a 750 ms fade-out. Adjacent receipts
record the source, offset, resulting hash and decoded peak. A changed existing
output pin fails unless `--update-manifest` is explicitly supplied after review.

Run the dense movement audit against final FK, not just authored target curves:

```bash
PYTHONPATH=engine:. .venv/bin/python -m tools.advanced_dance.qa \
  --mode solo --out work/advanced-dance/qa/final
PYTHONPATH=engine:. .venv/bin/python -m tools.advanced_dance.qa \
  --mode ensemble --out work/advanced-dance/qa/final
PYTHONPATH=engine:. .venv/bin/python -m tools.advanced_dance.cast_qa \
  --captures work/advanced-dance/qa/final \
  --out work/advanced-dance/qa/final/cast.json
```

The defaults match 60 fps, two temporal samples, the actual shutter and camera
cuts. `--role 2`, for example, selects one ensemble performer for a worker.
`solo0.json` and `ensemble0.json` through `ensemble4.json` record actor identity,
source hashes, measurements, issues and targeted review times. The accompanying
numeric captures allow inexpensive cast checks. The separate `cast_qa` command
checks the exact captured body proxies and actual fans against other performers
without repeating the FK solve, with source and actor-identity guards. Delivery
includes the JSON evidence, not intermediate NPZ captures.

The audit separates `blocked`, `review_required` and `numeric_pass`. Errors stop
the command with exit code 2. Review flags remain visible and return exit code
0 so that deliberate fast movement can receive visual assessment. Neither
status establishes artistic approval.

After correcting the reported motions and reviewing a continuous performance
proof, freeze the picture inputs. Then bake the exact costumes:

```bash
.venv/bin/python -m tools.advanced_dance.prepare bake --mode solo
.venv/bin/python -m tools.advanced_dance.prepare bake --mode ensemble
```

For separate bounded workers, use `--mode ensemble --role 0` through `--role 4`.
Each command constructs only the selected performer. A changed score, rig or
costume invalidates its cache. The bake checks for source changes during work
and writes a content receipt beside each completed cache.

Audit the completed cloth caches at every saved state and every exact
render/shutter/boundary time before using them for final production:

```bash
PYTHONPATH=engine:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m tools.advanced_dance.cloth_qa \
  --out work/advanced-dance/cloth-qa/final
```

The default audits all six performers without starting a new cloth simulation.
Final production requires `summary.json` to report `passed` with all six
performers complete. `--mode solo`, `--mode ensemble`, or
`--mode ensemble --role 2` narrows the audit. `--summary-only` omits per-time
rows while preserving the same checks. `--allow-missing` is only for observing
unfinished bakes; an incomplete report is not a final pass. Saved 30 Hz states
and their actual 60 fps render interpolations are checked separately, using the
same source hashes and the renderer's real shutter schedule.

Prepare the exact light trails from the completed, hash-bound final-FK
captures after the picture inputs are frozen:

```bash
.venv/bin/python -m tools.advanced_dance.prepare trails --mode all \
  --captures work/advanced-dance/qa/final
```

This command runs each film in a fresh process. It requires all 1,921 canonical
60 Hz states, including the 32-second endpoint, matching kinematic source
hashes and the actual cast identity. It injects those recorded final states into
isolated actor caches and calls the unchanged real fan model for every tip.
Live checks compare final FK, grip frames, fan surfaces and tips byte-for-byte
at recorded probes. The actual `GestureLight` consumer must load the resulting
track bytes with live fallback disabled before the cache is installed. No
trajectory interpolation or substituted hand target is introduced. The
adjacent JSON records all capture hashes and the current picture identity.

Verify a representative native frame in separate fresh and cached processes:

```bash
PYTHONHASHSEED=0 .venv/bin/python -m tools.advanced_dance.prepare \
  verify-frame --mode solo --frame 891
```

The cached process requires every selected film performer to load its cache;
the fresh process disables cache loading. Both render native 1920 x 1080 with
two shutter samples. The command saves the two images, source identities,
observed cache loads and exact RGB comparison. This is a same-environment frame
comparison, not a claim that every GPU or operating system renders identically.

Produce the finished films through their explicit registrations:

```bash
./scripts/video produce advanced-dance-solo --quality final
./scripts/video produce advanced-dance-ensemble --quality final
```

Each project specifies 1,920 output frames, three CPU workers and bounded chunks.
The registration fixes the camera cuts and rejects a changed clock or hidden
speed parameter. Completed frames are reused only when the declared inputs
match. Do not restart a completed queue because an older handoff mentions it.

### Review the full performance using final even frames

To inspect continuous motion before spending the second half of the final
render budget, first request the 960 even frames at the unchanged final quality:

```bash
.venv/bin/python - <<'PYCODE'
import subprocess
subprocess.run([
    "./scripts/video", "produce", "advanced-dance-solo", "--quality", "final",
    "--frames", ",".join(map(str, range(0, 1920, 2)))
], check=True)
PYCODE
.venv/bin/python -m tools.advanced_dance.prepare proof --mode solo
```

Repeat with `advanced-dance-ensemble` and `--mode ensemble` for the other film.
The proof helper verifies every PNG against the current pipeline receipt and
encodes those exact native frames with pinned music into a separate 1080p30
review movie. It checks all 960 timestamps, the exact 32-second duration and a
complete audio/video decode, and preserves the original PNGs. Its JSON makes
the sampling scope explicit: source 60 fps shutter samples are retained; odd
frames and any camera cuts landing on odd frames are absent. It does not
interpolate images, retime the performance or claim final 60 fps approval.

After inspecting the proof, run the ordinary full `produce --quality final`
command above. Matching even frames are reused, missing odd frames are
rendered, and the pipeline assembles and checks the complete 1,920-frame
master. A selected-frame `produce` invocation ends with a review gallery; only
a complete invocation assembles the final master and runs its technical QA.

## Repeatable repair loop

1. Find the exact reported time, performer and body part. Compare the final
   skeleton, the source cue, the support labels and the rendered result.
2. Repair the cause in the appropriate layer. Correct a low or distant cue in
   the score, a wrist singularity in anatomy, a heading mismatch in foot support,
   and cloth collapse in costume or solver settings. Keep the thresholds and
   reference evidence intact.
3. Rerun the same dense audit and inspect the previous failure interval at
   ordinary playback speed. Include preparation and recovery. Check hands and
   feet in native crops; verify that prop roots follow the final hand.
4. Inspect turns, low poses, joins, landings, canon boundaries and the ending in
   a continuous encoded proof. `qa.render_review_sheet` can extract ordered
   native crops and returns the actual decoded frame indices and timestamps.
   A contact sheet alone is not continuous playback review.
5. Freeze the corrected source, rebake affected costumes, verify cache reuse,
   and render the final output. Run encoded-media checks against the actual
   delivered file, retaining its hash with the scoped visual findings.

The audit checks finite transforms, normalized quaternions, bone lengths, joint
hinges, final ankle targets, planted-foot drift and rotation, skinned sole
clearance, local wrist angles, rotation speed and acceleration, prop attachment,
body-proxy proximity, planted-foot/pelvis heading and foot-to-shin axial twist.
Cast checks use conservative body proxies. Fan-to-fan overlap, fine garment
intersections and the artistic reading of a gesture still require visual review.
The authoring limits are project repair tolerances. They do not simulate force,
muscle loading, balance or clinical human joint ranges.

Focused regressions are available without rendering full films:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover \
  -s tests -p 'test_advanced_dance_*.py' -v
```

## Deliver the revised collection

Do this only after both final movies and their review evidence exist. The prior
ten-film archive must be the saved original with SHA-256
`7bd5e9f32f4a40150cba39c00bda8cd9959768bb837e448c80b482877e84b0b2`.

```bash
.venv/bin/python -m tools.advanced_dance.delivery \
  --old-archive /absolute/path/Ten_Cinematic_Films_1080p60.zip \
  --solo work/pipeline/advanced-dance-solo/final/master.mp4 \
  --ensemble work/pipeline/advanced-dance-ensemble/final/master.mp4 \
  --source-commit FULL_FROZEN_PICTURE_COMMIT \
  --qa solo_motion=work/advanced-dance/qa/final/solo0.json \
  --qa ensemble_0=work/advanced-dance/qa/final/ensemble0.json \
  --qa ensemble_1=work/advanced-dance/qa/final/ensemble1.json \
  --qa ensemble_2=work/advanced-dance/qa/final/ensemble2.json \
  --qa ensemble_3=work/advanced-dance/qa/final/ensemble3.json \
  --qa ensemble_4=work/advanced-dance/qa/final/ensemble4.json \
  --qa cast=work/advanced-dance/qa/final/cast.json \
  --out work/advanced-dance/delivery
```

Add further `--qa label=path.json` entries for final visual, pipeline, assembly
and render records. Supplied review flags are retained. The helper performs full
new-movie video/audio decoding, exact frame-clock checks and decoded audio peak
checks. It verifies the eight retained movies against the saved delivery
evidence and copies every movie without re-encoding.

The result includes the two separately named revised movies, the other eight
original movies, a ten-row overview with four actual decoded samples per film,
technical and QA JSON, a plain-text README, SHA-256 checksums and
`Ten_Cinematic_Films_Advanced_Dance_1080p60.zip`. New films are 32 seconds; retained
films are 20 seconds. The complete collection is 224 seconds. The new output
directory is installed only after all packaging checks pass. Archive creation
does not publish, upload, merge or imply owner approval.
