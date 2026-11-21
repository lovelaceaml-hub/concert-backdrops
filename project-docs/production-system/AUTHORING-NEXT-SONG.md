# Authoring the next concert film

The shared system can reproduce two registered studies and can provide native models, reference identities, audio verification, planning, frame recovery, encoding and technical review. A new complete song still needs authored acting, cameras, musical cues and scene integration. This guide explains where that work belongs without changing an approved reference.

## 1. Start from the actual song record

Read `START-HERE.md`, `CREATIVE-RULES.md`, the latest owner direction and the selected song's catalog entry. Use an isolated branch from current `main`:

```bash
./scripts/concert song s07
./scripts/concert plan s07 --out work/plans/s07-upgrade.json
./scripts/concert verify-audio s07 --decode
```

Replace `s07` only after selecting a different cataloged song. A second plan at the same path fails intentionally; inspect the existing plan instead of overwriting another chat's work. The plan carries source identities and historical caveats, but its render command remains empty until an actual scene exists.

Keep four clocks explicit: original recording time, any approved live arrangement time, authored scene time, and output frame number. Record every crop, fade, gain adjustment or retiming. Do not infer a rehearsal arrangement from a title or silently stretch an original recording to an older stage duration.

## 2. Write the performance before the environment

For each major passage, write a short sentence describing what someone notices, chooses, does, receives and changes. Tie that action to the selected campaign expression, using the exact wording and color already in `engine/p3d/words.py`. The historical expression mapping is in the song catalog. A new mapping is a deliberate design change, not an automatic consequence of changing the soundtrack.

The Consideration study demonstrates the sequence: notice a seated person, offer a hand, establish shared contact, brace and rise, release, acknowledge, then let the caring action illuminate the shore. Its timing is specific to that study. Do not paste an identical 18-second performance through all eleven songs.

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

The two current registered projects are `approved-light-s11` and `concert-kit-consideration`. The approved adapter rejects a different recording or source identity. The current kit adapter accepts only the Consideration scene, empty shot parameters and its 18-second, 60-fps bounds. Renaming a project or replacing its audio does not author another song.

For a new production, add a separate scene module and project directory. Use the current Consideration source and `docs/PIPELINE-INTEGRATION.md` as implementation references, while preserving their existing registered behavior. Extend the adapter's explicit scene registration, validation and dependency collection to cover the new module. Keep the following contracts intact:

- `make_renderer` creates an explicit native size, frame rate, temporal sample count and isolated cache identity.
- `frame` evaluates the requested absolute output time, with shutter samples confined to its current shot.
- Source identity includes every imported scene/model module, relevant assets and fonts. A new module outside the existing source directories must be added to dependency discovery.
- Project shot bounds and scene cut times agree exactly. A visual source clock and an audio offset are separate values.
- The selected color contract describes the actual rendered bytes. The approved light route is RGB8 SDR with its established display treatment.
- Prepare, render, assemble, QA and review continue through the existing scheduler. Do not create a second untracked frame cache or bypass stale-frame checks.

Test a meaningful new adapter boundary with a small real render: wrong source rejection, correct time forwarding, out-of-order frame evaluation, cut handling and resume. Preserve the native approved-reference comparison when changing shared pipeline behavior. The existing pipeline tests are a starting point, not a substitute for inspecting the new performance.

Do not edit any dependency while a frozen production round is rendering. A source change should invalidate output honestly. Finish or stop that round, record why, and begin a new identity when the picture changes.

## 5. Review motion at the scale where it matters

First render native 1080p close, wide and ending frames. Then render the complete human exchange at 60 fps. Evaluate anticipation, hand approach, shared grip, balance, foot planting, weight transfer, release, cloth overlap and settling. Review camera acceleration and the moment at which the world responds.

Use consecutive temporal samples as well as spaced keyframes. Spaced stills can hide a sliding foot, a sudden wrist change, a repeated pose or a flash at a batch boundary. Inspect frames immediately before and after every cut and renderer chunk boundary. Review the encoded result as well as the source PNGs.

Machine evidence should name what it actually measured. Palm-center distance does not certify finger interlock. Stable wing length does not certify aerodynamic realism. A sixty-fps file does not prove sixty distinct evaluated poses. A motion-capture source sampled at 30 Hz can be interpolated at output times, but should not be described as a native 60-Hz capture.

For the established style, protect one important action at a time. Keep the hands and faces clear of reeds, bright trajectories and text. Reserve larger light travel for a visible consequence. Let the final response finish before the scene ends.

## 6. Freeze, deliver and continue

After the moving proof passes review, record the source identity and use the registered production command for the complete scene. Verify dimensions, exact frame count, frame times, color tags, audio duration and decoded peaks, cuts, chunk boundaries and all QA findings. A warning can be understood and documented; it must not be hidden by changing thresholds after the fact.

Save media and its checksums in the existing shared folders. Keep full recordings, lyrics, rendered frames and movies out of Git. Update the model/song/reference catalogs, current state, verification and append-only production log. Upload the portable handoff with its code revision, push and merge the isolated work under the current user's authorization.

Mark a new output as awaiting owner review until that particular output is approved. At session end, leave one concrete next task, the exact resume command if needed, and any uncertainty about rehearsal arrangements. A saved improvement queue continues in the next chat; it does not run itself after the session ends.
