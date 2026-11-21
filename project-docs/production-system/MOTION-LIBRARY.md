# Motion library and intake workflow

## What is available now

The committed body asset contains **eight prepared motion clips from seven CMU captures**. It already provides walking, running, a jump, a full expressive dance, a shorter turn, a paired assisted rise and a rise from the floor. The machine-readable inventory is [catalogs/motions.json](catalogs/motions.json). Use it with the [model catalog](catalogs/models.json), [natural performance handoff](NATURAL-PERFORMANCE.md) and [current delivery catalog](catalogs/deliveries.json).

This inventory was read directly from `assets/p3d/body_v1.npz` at source commit `0c42f4422a6b67464cb9cd84aac32008d45d4f4c` on November 21, 2026. The asset is 777,053 bytes and has SHA256:

```text
0a72159f84b7008dcb135c79f82ae3b05df5f7361197e99ab9ca4af148c91189
```

Every clip's declared frame count matches its rotation, root and contact arrays. All motion arrays are finite, and the two contact confidence channels stay within 0 to 1. These checks establish inventory integrity. They do not certify the beauty, physical balance, floor contact or owner approval of every use.

### Prepared clips

All eight are stored at **30 Hz**. Durations below follow the runtime's actual convention in [motion.py](../../engine/p3d/motion.py): a single performance spans `(N - 1) / fps`, while a repeating cycle has period `N / fps`. The cycle includes the interval from its last stored sample to the next cycle's first sample.

| Prepared name | Source capture | Poses | Runtime duration | Playback | Useful action |
| --- | --- | ---: | ---: | --- | --- |
| `walk` | CMU `35_01` | 34 | 1.133333 s | Repeating cycle | Processions, approaches and departures |
| `run` | CMU `35_17` | 22 | 0.733333 s | Repeating cycle | Running or jogging travel |
| `jump` | CMU `13_11` | 104 | 3.433333 s | Once | A forward jump from standing |
| `dance` | CMU `05_02` | 281 | 9.333333 s | Once | Large arm arcs, whole-body expression and a traveling turn |
| `twirl` | CMU `05_02`, cropped | 96 | 3.166667 s | Once | A shorter raised-arm turn |
| `pull_up` | CMU `22_01` | 196 | 6.500000 s | Paired, once | Helping a seated person rise |
| `helped_up` | CMU `23_01` | 196 | 6.500000 s | Paired, once | Receiving that help |
| `get_up` | CMU `140_08` | 225 | 7.466667 s | Once | Rising from lying on the back |

The descriptions and source identities above come from the committed [import recipe](../../tools/build_p3d_motion.py) and [asset provenance](../../assets/p3d/README.md). They are useful action categories, not a claim that every clip suits every song or costume. The JSON includes exact unrounded timing, loop travel, source URLs, crop settings and limitations for each clip.

`twirl` selects source seconds 3.0 to 6.2 after the source T-pose. Its stored span is 95/30 seconds, so do not use the crop's nominal 3.2 seconds as its runtime duration. The two assistance clips were imported with a shared relationship. Preserve their synchronization and relative placement, then check the actual grip at the chosen body proportions. The existing constructor is `p3d.pairs.pull_up`; its source-ready model entry is `people.paired-help`.

The compatibility names `spin`, `dance_a` and `dance_b` add no new capture. They resolve to `twirl`, `dance` and `dance`; `dance_b` defaults to phase **0.45 of the clip duration**, not a 0.45-second delay. The authored states `stand`, `kneel`, `sit`, `shuffle`, `rise` and `held`, along with gesture and hand-pose libraries, are a separate procedural layer. See [motion.py](../../engine/p3d/motion.py), [actor.py](../../engine/p3d/actor.py) and [gestures.py](../../engine/p3d/gestures.py).

## What this data can and cannot establish

The asset stores local rotations for 25 driven bones as float16 quaternions in `wxyz` order. Whole-root rotation, translation and foot confidence are float32. Prepared coordinates use metres, +Y up and +Z forward. Root translation is expressed for a reference leg chain of approximately 0.853783 metres and scales with the runtime body's leg length. The import also adjusts repeat cycles and estimates floor placement. This is a retargeted performance representation.

Rendering at native 60 fps interpolates the stored 30 Hz poses. The original CMU subject 5 catalog lists `05_02` at 120 Hz, as documented in [the research handoff](NATURAL-PERFORMANCE-RESEARCH.md). The bundle does not retain a verified original frame rate and raw BVH hash for every clip. This inventory did not reacquire the original files. A future import at higher rate is a new asset revision requiring comparison and review.

The two stored foot curves are automatic estimates from low, slow foot trajectories. They are not measured pressure, ground-reaction forces or reviewed support labels. Hand, pelvis, knee and other floor contacts are not separately annotated. Finger and thumb performance was not captured; current hand detail is authored or procedural. In addition, runtime arm clearance, body proportions, poses and costumes can change the visible result. Review those choices on the actual performer.

### Review status

| Item | Established here | Still determined elsewhere |
| --- | --- | --- |
| All eight clips | Present, identified, dimensionally consistent and finite | Isolated motion quality, costume behavior and suitability for a shot |
| `dance` | Integrated through `install_dance`, with focused contact and transition tests | Completion, encoded visual review and owner approval of each versioned delivery |
| `pull_up` and `helped_up` | Existing paired constructor and Consideration study integrations | Grip, overlap, body scaling and final settlement in the selected scene |
| Other prepared clips | Available through the existing `p3d` motion runtime | A new use needs its own moving proof |
| Proposed candidates below | Research identifiers only | Acquisition, retargeting, contacts, tests and creative review |

This audit did not create a standalone plain-floor proof for all eight clips. Historical appearances in films also do not confer general approval on every future retarget or costume. Consult [STATE.json](STATE.json) and the versioned delivery catalog for actual completed media, technical QA, visual findings and owner review.

## Reuse the current dance safely

The registered `concert-dance-study` uses the existing `dance` capture through the instance-local [performance layer](../../tools/concert_dance/performance.py). It retains the captured travel and facing through settlement, builds stable support intervals once, distinguishes heel or toe support from free motion, and bounds the correction. Its full example and commands are in [the study README](../../tools/concert_dance/README.md).

Configure body placement and heading, then install the performance before sampling the actor or cloth:

```python
from tools.concert_dance.performance import install_dance

performance = install_dance(
    body,
    start=2.0,
    rate=1.0,
    prepare_seconds=2.0,
    settle_seconds=2.5,
)
hand = body.where(8.0, "palm.R")
support_report = performance.contact_report([2.0, 4.0, 6.0, 8.0, 10.0])
```

Use a dense timeline for actual QA; the five report times above only demonstrate the API. `diagnostics(t)` reports phase, source time, pelvis, support mode, weight, anchor, horizontal residual and minimum sole height. `contact_report(times)` includes support intervals and the maximum sampled horizontal residual at support weights of at least 0.95. A report with no strong supports can return a null maximum, so retain its sample counts and inspect the intervals.

The default dance adds a 0.24-second clock envelope to the 9.333333-second prepared phrase. At start 2.0 and rate 1.0, captured playback ends at approximately 11.573333 and settlement ends at 14.073333. `clip_start` and `clip_end` select source seconds within this one dance; they do not choose another clip or make a seamless loop. Rates outside 0.75 to 1.25 are rejected.

Support detection currently combines stored confidence, low height, low horizontal speed and bounded spatial spread. It selects a heel or toe anchor while retaining foot rotation. The default correction limit is 0.075 metres for a 1.7-metre body, scaled by height. This is a bounded kinematic treatment. It does not prove physical balance or guarantee that every foot is always on the floor. Genuine free and airborne phases must stay free.

Both study performers use the same capture with a 0.6-second offset. A complementary duet needs a separately chosen answering action and a new proof. The wrapper currently targets `dance` explicitly; it is not a general new-clip loader. Preserve its complete torso, root and leg motion before adding gestures, and attach ribbons or props to the final solved palm positions. Do not install it after body or cloth caches have been sampled, or alter placement behind already computed support anchors.

## Candidates for a future library expansion

These sources have **not been acquired or prepared by this increment**. Their identifiers must not appear in a ready-to-render list.

| Candidate | Source catalog | Required next action |
| --- | --- | --- |
| CMU `05_03` | [Subject 5](https://mocap.cs.cmu.edu/search.php?subjectnumber=5) | Inspect the original performance, entry and exit before assigning a use |
| CMU `05_11` | [Subject 5](https://mocap.cs.cmu.edu/search.php?subjectnumber=5) | Inspect the original performance, entry and exit before assigning a use |
| CMU `05_12` | [Subject 5](https://mocap.cs.cmu.edu/search.php?subjectnumber=5) | Inspect the original performance, entry and exit before assigning a use |
| CMU subject 49, including candidate `49_09` | [Subject 49](https://mocap.cs.cmu.edu/search.php?subjectnumber=49) | Select and inspect individual modern dance phrases; a subject collection is not one clip |

No precise movement description, runtime, frame count, quality ranking or song assignment is asserted for these unprepared candidates. Prioritize a distinct answering phrase with usable entry and exit support over adding many similar turns. Keep song-specific decisions in [the improvement queue](IMPROVEMENT-QUEUE.md).

## A repeatable path for every new performance

### 1. Choose an action and record its provenance

Start with the human intention in the chosen song: offering help, receiving it, opening toward another person, listening, celebration or release. Select a short source phrase that expresses the action. Review its complete start, development and ending before choosing a crop. Record the exact source ID, author or dataset, URL, terms, original rate, units, coordinate conventions, capture description and retrieval date.

Acquire only the selected files through a documented recipe. Keep original bytes immutable in the selected asset store and record their SHA256 and durable location. Retain the source terms and requested attribution. The [research handoff](NATURAL-PERFORMANCE-RESEARCH.md) links the primary CMU terms and FAQ; consult them when acquiring data. A repository's script license does not establish the license of motion data contained in it.

### 2. Retarget into a new asset revision

Work in an isolated branch with one owner for the import recipe and motion asset. Preserve the approved `body_v1.npz` and source snapshots. Use a separately named candidate asset, then retain its geometry identity, source hashes, joint mapping, rest pose, units, heading adjustment, crop, prepared rate and quaternion convention. Keep root travel and whole-body orientation with the pose. Record any filtering, cycle closure, foot leveling or authored correction.

The existing importer exposes `--bvh`, `--asset` and `--only`, but its `CLIPS` table defines the accepted prepared names and source IDs. `--only 05_03` does not import a new candidate. The `--asset` target must already contain the body data because the importer merges motion into it, and the default target is the shared `body_v1.npz`. Extend and review a new recipe and asset-loading path before publishing additional captures. Do not run a default rebuild against a frozen picture source.

### 3. Annotate and inspect contact

Calculate heel and toe positions in world space, then inspect candidate intervals against the original action. Distinguish flat support, a heel or toe pivot, a lifted balance and flight. Keep the whole reviewed support interval tied to one source clock and anchor. An unsupported foot can remain still in the air; low velocity alone does not establish contact. Grounded hand or body contact needs its own annotation for floor actions.

Record detector thresholds, body scale, correction limits and any manual interval edits. The current dance wrapper's heel or toe estimator is a useful starting implementation, not a blanket guarantee for new motion. Preserve real rotation through a pivot and real travel between supports. Review transitions around every support change instead of forcing the feet down during a jump.

### 4. Make a plain-floor motion proof

Render the complete phrase with simple lighting, a contrasting floor and visible feet, hands and joint silhouettes. Use front, side and three-quarter views where needed. Evaluate at absolute song or scene time, including shutter subframes. Compare shuffled frame requests with sequential requests to establish deterministic playback.

Measure root continuity, finite poses, segment lengths, excessive joint changes, whole-sole floor clearance and anchor drift during deliberately stationary support. Report the measured interval and support weight with every drift number. The research handoff's 5 mm hero-contact target is a proposed starting threshold, not a universal motion rule. Review intended pivots and flight separately. Watch the encoded proof for anticipation, weight transfer, torso arcs, turn, landing compression and settlement. Sparse stills cannot establish natural movement.

### 5. Make a costume proof

Repeat the motion with the exact body height, build and garment intended for the shot. Inspect shoulders, knees, elbows, fingers, soles, silhouette and garment intersections during the turn and landing. Cloth must use the same final actor and performance that produce the visible body. Warm or rebuild its deterministic bake only after that performance is installed. Props and effect origins must follow the final solved pose.

Retain a short continuous proof with the final costume. A passing skeleton test does not establish a passing dress or coat. If the shot includes a partner, review their shared contacts, projection overlap and timing together.

### 6. Register the scene and freeze a picture round

Connect the reviewed performance to an isolated scene and renderer adapter, with a registered project manifest. Record source dependencies, asset hashes, body parameters, placement, clock, seeds, audio identity and authored cues. Follow [AUTHORING-NEXT-SONG.md](AUTHORING-NEXT-SONG.md), [the native dance handoff](NATURAL-PERFORMANCE.md) and the existing `scripts/video produce` workflow.

Check native full-size frames, then render and inspect the continuous sequence. Keep movement readable before enlarging the environment or adding trails. Freeze the picture source during a round so independent CPU workers evaluate the same motion and support anchors. Preserve frame receipts and encoded QA. Promote the clip from candidate to prepared only when the asset and recipe exist; record motion proof, costume proof, scene review and owner approval as separate milestones. Publish exact source and delivery identities for the next AI to reuse.

## Preserve the visual and motion distinction

The pictures are drawn by the project's code from geometry, particles, lines and light. The body uses documented MakeHuman assets, and these performances use documented CMU capture transforms. Code-drawn imagery does not mean all geometry and choreography were created from scratch by project code. Keep that distinction in new handoffs and public descriptions, and preserve the [existing asset provenance](../../assets/p3d/README.md).

Retain CMU's requested acknowledgement:

> The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.

This inventory added documentation only. It did not download candidate motion, replace the body asset, modify the frozen renderer, or confer creative approval on a new delivery.
