# Authoring the next concert film

The shared system provides native models, reference identities, audio verification, planning, frame recovery, encoding and technical review. As of November 23, 2026, [projects/](../../projects/) contains eighteen concert project manifests and four technical demos, covering the approved clarity study, Consideration revisions, dance/fan studies, Cinematic Ten and Advanced Dance. The completed **275-second renewed Song 11** uses the dedicated [s11_renewed](../../tools/s11_renewed/README.md), [s11_cloud](../../tools/s11_cloud/README.md) and [s11_delivery](../../tools/s11_delivery/README.md) route. Registration and a configured preset are distinct from a completed or approved output.

Read [root AGENTS.md](../../AGENTS.md), [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md) and [STATE.json](STATE.json) before choosing new work. There is no unfinished production queue. The current Song 11 is a completed 1080p60 design/review delivery, without exact-output owner approval or a rendered 4K show master. Improve the existing system and keep its added tools reusable. Work at 1080p until design/timing/content approval, then produce the final show at 4K60. Make no new phone copies. CPU work stays in the cloud; needed GPU work uses the owner's Mac under the root rules. This guide applies when a current request actually calls for another song or revision.

## 1. Start from the actual song record

Read `START-HERE.md`, `CREATIVE-RULES.md`, the latest owner direction and the selected song's catalog entry. Use an isolated branch from current `main`:

```bash
./scripts/concert song s07
./scripts/concert plan s07 --out work/plans/s07-upgrade.json
./scripts/concert verify-audio s07 --decode
```

Replace `s07` only after selecting a different cataloged song. A second plan at the same path fails intentionally; inspect the existing plan instead of overwriting another chat's work. The generic plan carries source identities and historical caveats, but does not discover every dedicated production route. An empty render command or `authored_scene_required` in that older planning interface must not be taken as evidence that the completed renewed Song 11 scene is missing. Consult current state and the actual module before authoring a replacement.

Keep four clocks explicit: original recording time, any approved live arrangement time, authored scene time, and output frame number. Record every crop, fade, gain adjustment or retiming. Do not infer a rehearsal arrangement from a title or silently stretch an original recording to an older stage duration.

## 2. Write the performance before the environment

For each major passage, write a short sentence describing what someone notices, chooses, does, receives and changes. Tie that action to the selected campaign expression, using the exact wording and color already in `engine/p3d/words.py`. The historical expression mapping is in the song catalog. A new mapping is a deliberate design change, not an automatic consequence of changing the soundtrack.

Apply the owner's modesty correction before reusing a body or dance layer: independent, generous garment geometry, with no visible nipple/breast outlines, buttock clefts or exposed cheeks. Opaque body-fitting color is not enough. Review all figure roles and camera directions. Historical fan/anatomy studies are not approved defaults; in Song 11, Heavenly Mother is represented only by light.

The Consideration study demonstrates the sequence: notice a seated person, offer a hand, establish shared contact, brace and rise, release, acknowledge, then let the caring action illuminate the shore. Its timing is specific to that study. Do not paste an identical 18-second performance through all eleven songs.

For dance, begin with a complete inspected phrase and its support changes, turn, travel and settlement. The reusable `people.natural-dance` entry installs `tools.concert_dance.performance.install_dance` on a Body before sampling it or its cloth. It keeps the captured final location, calculates stable support intervals and evaluates poses at absolute time. Read [NATURAL-PERFORMANCE.md](NATURAL-PERFORMANCE.md), the [source and licensing research](NATURAL-PERFORMANCE-RESEARCH.md), and [the study README](../../tools/concert_dance/README.md) before reusing it. The current duet uses the same captured phrase twice with a 0.6-second offset. A new song or a complementary duet needs new authored phrasing and review; no additional capture collection is implied.

Record these decisions in the ignored work plan:

| Decision | Required detail |
| --- | --- |
| Human action | Participants, casting, preparation, action, response and final pose |
| Contact | Which feet or hands are planted, which shared prop or target is used, and when contact releases |
| Song cue | Exact recording hash and source time; mark manually checked cues separately from estimates |
| Camera | Subject, shot bounds, path, direction, focus and an intentional ending |
| World response | What changes because of the action, its origin, travel time and destination |
| Reading time | Exact expression wording, its reveal and a sufficiently long hold |
| Reuse | Existing model IDs and versions; scene-bound components that need extraction |
| Review | Close action frame, widest frame, ending and moving proof boundaries |

## 3. Reuse native geometry through its real interface

The first kit uses metres, Y up and the mirror surface at Y = 0. Its builders expose `sample(t)` and can be added inside a native scene's `setup(scene)` function. This is an actual model API example; it is not a standalone movie renderer:

```python
from tools.concert_kit.models import build_model

def setup(scene):
    scene.add("shore_flowers", build_model(
        "flowers", variant="lotus", at=(-3.0, 0.0, -2.0),
        count=15, radius=0.8, height=0.35, bloom=12.0, seed=32,
    ))
    scene.add("garden_lantern", build_model(
        "lantern", variant="cup", at=(2.0, 0.3, -3.0),
        size=0.22, lit=12.5, seed=5,
    ))
```

See `tools/concert_kit/MODEL-CATALOG.md` for all six families and twelve variants. The separate `tools/concert_addons/` package extends the available prototypes; read its own catalog and verification before using one. A geometry preview is evidence of that model at the tested size and camera, not approval for every close-up or performance.

Place important geometry around the final solved actor pose. Drive a carried object, baton, book, contact light or shared target from the final hand anchor. A rigid object that looks attached in a rest pose can miss after the body, cloth or hand layers finish evaluating. Keep paired target calculations non-recursive.

Some existing models are explicitly `scene_bound` in the shared catalog. The Song 11 choir, orchestra, Zion and church builders retain their original dependencies and timing. Extract them into an isolated wrapper, test it, and update the catalog before describing them as reusable in any song.

## 4. Register a new scene deliberately

Earlier registration examples are `approved-light-s11`, `concert-kit-consideration`, `concert-kit-consideration-v2`, `concert-dance-study` and `concert-dance-study-4k`; later manifests add `concert-fan-trio`, `cinematic-ten-01` through `cinematic-ten-10`, and `advanced-dance-solo`/`advanced-dance-ensemble`. The two dance-study resolutions share one scene registration and authored clock. The approved adapter rejects a different recording or source identity. The kit adapter has an explicit scene registry: the historical Consideration scene has 18-second bounds; its revision has 15-second bounds and a three-second source offset; the dance scene covers 18 seconds from source time zero in one uninterrupted 1,080-frame shot. Those kit studies require 60 fps, empty shot parameters and their exact authored cuts. Renaming a project or replacing its audio does not author another song. The full renewed Song 11 is accessed through its dedicated modules rather than one of these generic study names.

For a new production, add a separate scene module and project directory. Use `tools/concert_motion_revision/README.md`, `tools/concert_dance/README.md`, their isolated renderer wrappers and `docs/PIPELINE-INTEGRATION.md` as implementation references, while preserving the existing registered behavior. Extend the adapter's explicit scene registration, validation and dependency collection to cover the new module. Keep the following contracts intact:

- `make_renderer` creates an explicit native size, frame rate, temporal sample count and isolated cache identity.
- `frame` evaluates the requested absolute output time, with shutter samples confined to its current shot.
- Source identity includes every imported scene/model module, relevant assets and fonts. A new module outside the existing source directories must be added to dependency discovery.
- Project shot bounds and scene cut times agree exactly. A visual source clock and an audio offset are separate values.
- The selected color contract describes the actual rendered bytes. The approved light route is RGB8 SDR with its established display treatment.
- Prepare, render, assemble, QA and review continue through the existing scheduler. Do not create a second untracked frame cache or bypass stale-frame checks.

Test a meaningful new adapter boundary with a small real render: wrong source rejection, correct time forwarding, out-of-order frame evaluation, cut handling and resume. Preserve the native approved-reference comparison when changing shared pipeline behavior. The existing pipeline tests are a starting point, not a substitute for inspecting the new performance.

Do not edit any dependency while a frozen production round is rendering. A source change should invalidate output honestly. Finish or stop that round, record why, and begin a new identity when the picture changes.

Use the pipeline's optional `production.render_workers` for bounded CPU parallelism. One coordinator validates staged frames and writes receipts; worker count does not change the picture identity. Select concurrency from measured memory at the intended resolution, keeping room for variation and other jobs. The 1080p dance configuration uses six single-thread workers and 90-frame chunks; the separate native 4K project uses three workers. The representative 876.9 MiB 1080p measurement covered two native frames and observed a source change, so it is not a frozen full-film maximum. The actual native 4K frame worker subsequently peaked at 1,734,260 KiB, about 1.65 GiB. Neither short-run measurement establishes a whole-film maximum. The complete 4K study project is an archived configuration whose full movie remains unrendered, not an unfinished queue. Any new 4K production must follow the current approval rule; [NATURAL-PERFORMANCE.md](NATURAL-PERFORMANCE.md) preserves the historical commands and measurements. Remeasure for another scene or host. See [VIDEO-PIPELINE.md](../../docs/VIDEO-PIPELINE.md).

## 5. Review motion at the scale where it matters

First render native 1080p close, wide and ending frames. Then render the complete human exchange at 60 fps. Evaluate anticipation, hand approach, shared grip, balance, foot planting, weight transfer, release, cloth overlap and settling. Review camera acceleration and the moment at which the world responds.

Use consecutive temporal samples as well as spaced keyframes. Spaced stills can hide a sliding foot, a sudden wrist change, a repeated pose or a flash at a batch boundary. Inspect frames immediately before and after every cut and renderer chunk boundary. Review the encoded result as well as the source PNGs.

Machine evidence should name what it actually measured. Palm-center distance does not certify finger interlock. Stable wing length does not certify aerodynamic realism. A sixty-fps file does not prove sixty distinct evaluated poses. A motion-capture source sampled at 30 Hz can be interpolated at output times, but should not be described as a native 60-Hz capture.

For the dance layer, inspect toe pivots separately from stationary flat support, retain intended airborne intervals, and review landing compression and costume turns. The bounded support correction is kinematic cleanup, not a force or balance simulation. Fingers require their own authored layer and close review. A native 4K frame checks composition and detail at that resolution; a full 4K movie requires its complete frame sequence, assembly and encoded review.

For the established style, protect one important action at a time. Keep the hands and faces clear of reeds, bright trajectories and text. Reserve larger light travel for a visible consequence. Let the final response finish before the scene ends.

## 6. Freeze, deliver and continue

After the moving proof passes review, record the source identity and use the registered production command for the complete scene. Verify dimensions, exact frame count, frame times, color tags, audio duration and decoded peaks, cuts, chunk boundaries and all QA findings. A warning can be understood and documented; it must not be hidden by changing thresholds after the fact.

Save media and its checksums in the existing shared folders. Keep full recordings, lyrics, rendered frames and movies out of Git. Update the model/song/reference catalogs, current state, verification and append-only production log. Upload the portable handoff with its code revision, push and merge the isolated work under the current user's authorization.

Mark a new output as awaiting owner review until that particular output is approved. At session end, record whether the authorized task is complete and any uncertainty about rehearsal arrangements. If work is actually unfinished, leave its exact resume command and concrete next action. A historical improvement backlog is not authorization to resume or expand a completed production in the next chat.
