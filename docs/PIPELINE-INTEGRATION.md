# Production commands for the approved light system

The shared `video` command runs the frozen Song 11 beauty reference, the
historical Consideration baseline and its separate camera and response revision
through the existing frame checkpoint pipeline.
It preserves the historical study scripts and production engine. It adds no GPU
provider, paid dispatch, GitHub render dispatch, or automatic user approval.

## Registered projects

| Project ID | Renderer | Picture clock | Native review |
| --- | --- | --- | --- |
| `approved-light-s11` | `p3d-approved` | Original source scene 97.7 to 127.7 seconds, with the existing 0.1 second picture delay applied once | 1920 x 1080, 60 fps, 2 temporal samples |
| `concert-kit-consideration` | `p3d-kit` | Historical 18 second authored visual scene, from output frame zero | 1920 x 1080, 60 fps, 2 temporal samples |
| `concert-kit-consideration-v2` | `p3d-kit` | 15 seconds, output frames 0..899 map to original scene frames 180..1079 | 1920 x 1080, 60 fps, 2 temporal samples |
| `concert-dance-study` | `p3d-kit` | 18 seconds, one continuous captured dance and settlement, output frames 0..1079 | 1920 x 1080, 60 fps, 2 temporal samples |
| `concert-dance-study-4k` | `p3d-kit` | Same continuous eighteen-second clock, with a lower CPU worker count | 3840 x 2160, 60 fps, 2 temporal samples; full movie not yet rendered |

The first project retains the established choreography. The historical kit study
contains models and performance work in `tools/concert_kit`. The revision wraps
that source in `tools/concert_motion_revision`, preserving the original engine
and baseline. Its output cuts are frames 234 and 540, at 3.9 and 9.0 seconds.
Both kit scenes use a prepared Song 7 excerpt and neutral analysis controls.
The revision consumes seconds 3 to 18 of that canonical WAV, corresponding to
original recording time 140.5 to 155.5 seconds. It adds no fade or time stretch.
Attaching that recording does not automatically create instrument-specific
gestures or certify musical synchronization.

The dance study uses the same canonical eighteen-second score at offset zero.
Its new performance wrapper preserves captured travel and measured sole support;
its scene and renderer live in `tools/concert_dance`. See that directory's README
for reproduction, capture provenance and explicit motion limits. It retains the
approved engine and earlier scene modules unchanged.

All listed projects produce RGB8 SDR frames using the established filmic display treatment.
They explicitly select `delivery.source_transfer="legacy_display_gamma"`.
FFmpeg therefore preserves the original RGB-to-YUV matrix/range conversion.
The separate sRGB conversion used by Blender and browser projects remains intact.
These registered paths do not claim 16-bit source precision, 10-bit delivery or HDR.

## Environment and inputs

Use the existing cloud Linux bootstrap and locked dependencies. For the registered
studies, run `python3 scripts/bootstrap.py --p3d-only --reference-fonts` in an
isolated checkout. [REFERENCE-FONTS.md](REFERENCE-FONTS.md) explains the exact
74-font reconstruction and runtime qualification. Install fonts inside this checkout. The pipeline hashes the actual font bytes and rejects
dependencies that resolve outside the checkout. See `VIDEO-PIPELINE.md` for the
complete bootstrap and supported system dependencies.

Check only the selected backend:

```bash
./scripts/video doctor --project approved-light-s11
./scripts/video doctor --project concert-kit-consideration-v2
```

These p3d checks require the Python renderer, fonts and FFmpeg. They do not require
Blender, Node or a browser. `video doctor --backend blender` checks Blender, and
`--backend threejs --probe-browser` checks the browser path. A dependency check
does not claim that a scene has been rendered or visually approved.

The frozen project expects the private original at
`work/song-inputs/s11-original.mp3`, SHA256
`70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004`.
The kit project expects `work/concert-kit/consideration-score.wav`, SHA256
`0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b`.
Run `./scripts/concert prepare-study-audio` after acquiring Song07. It verifies
the exact PCM24 payload and writes a canonical WAV header without a
host-specific FFmpeg encoder tag. The sample payload SHA256 is
`493d1fa5efeaea437edcfecb241fb536439ec832d6f899750c4282c0d6895f84`.
The project manifests identify these inputs; neither recording is committed.
The successful canonical preparation used FFmpeg 7.1.5-0+deb13u1. The observed
host and package versions are recorded in the production-system environment
evidence. If a different decoder or filter build produces different PCM, keep
the rejected output and investigate the environment; do not replace the expected
hash merely to make a new file pass.

Before the first frozen preparation, the two original Git objects must exist:

```bash
git fetch origin d928ff9eafe02ac3150f0c646bdcc497fe5a7278
git fetch origin f43f4514e4bc42dc25166e90160d98219f5a0db4
```

Preparation invokes the original `tools/promo_beauty_example/prepare.py` only
when needed. Existing analysis is reused only with matching recording, derived
file checksums and preparation provenance. Unreceipted or changed analysis fails
with a repair instruction; it is not silently adopted or replaced with silence.
Keep prior work before preparing into a clean ignored work directory.

## One command to produce a project

Inspect the plan first. This command does not prepare, render or write files and
can describe the project before its private recording has been restored:

```bash
./scripts/video produce concert-kit-consideration-v2 --quality review --plan
./scripts/video produce approved-light-s11 --quality review --plan
```

Render selected native frames for visual inspection:

```bash
./scripts/video produce concert-kit-consideration-v2 --quality review --frames 0,138,233,234,270,512,539,540,870
./scripts/video produce approved-light-s11 --quality review --frames 45,501,900,1236,1476,1740
```

A selected-frame command prepares inputs, renders or reuses those frames and
writes the gallery. It does not assemble an incomplete movie. For a complete
production round:

```bash
./scripts/video produce concert-kit-consideration-v2 --quality review
./scripts/video produce approved-light-s11 --quality review
```

This composes preparation, the existing resumable renderer, FFmpeg assembly,
technical QA and the review gallery. It does not introduce a second scheduler.
The outputs live under `work/pipeline/PROJECT/QUALITY/`, including `master.mp4`,
`master.json`, `qa.json`, `review.html`, shot receipts and atomic PNG frames.
Use `./scripts/video archive PROJECT --quality QUALITY --destination PATH`
after the current delivery has passed its checks. It copies an archive to local
or mounted storage; the connected Drive tool performs the separate upload.
`scripts/concert export-handoff` packages instructions and catalogs, while
`scripts/concert restore-master` verifies and restores split reference media.

The registered presets use `temporal_samples`, from 1 to 4. This is the number of
motion samples in the p3d light pass, not a Cycles sampling budget. Supplying a
Blender `samples` field to these projects fails validation. The project frame
rate stays 60 across quality presets. `4k-check` allocates 3840 x 2160 frames;
the default final preset stays 1080p until a full 4K round is requested and reviewed.

## Recovery and identity

One process owns a project/quality directory at a time. The examples use one
worker and 120-frame batches, which avoids assuming that CPU core count equals
available render memory. Python workers receive `PYTHONHASHSEED=0` before process
startup, with explicit software-rendering and thread settings.

Every completed PNG is written atomically and checksummed. If a worker fails,
valid completed frames are retained in its receipt. Run the same command again
to repair missing or changed frames. Source edits invalidate their affected
fingerprints. Finishing changes are tracked separately from scene pixels.
The kit's attached audio and the approved excerpt's fades/gain are finishing
inputs; changing them does not require recomputing those registered scenes.

Place a file named `STOP` in the project/quality output directory to stop new
batches and registered workers between frames. Completed frames remain reusable.
Remove it only when intentionally resuming. Stop the coordinating process too
when cancellation must interrupt an active encoder or initialization immediately.

`pipeline/references/song11-beauty-v1.json` records 257 exact source/static-file
hashes from the approved source and its pinned engine archives. The adapter
checks them, the original recording and prepared analysis before rendering.
It retains the beauty tool's body-specific derived-cache identity. Derived cache
files themselves are not source inputs. Changed reference source requires a new
registration instead of silently claiming the old approved identity.

The review gallery displays a frame only when its current source fingerprint,
dimensions, bit depth and checksum match. Missing, stale and unverified frames
are labeled. It includes selected current review frames, and it embeds a master
only when the master, project, scene receipts and finishing sources match.

## Verification boundaries

The integration tests exercise selected-backend diagnostics, fresh-process hash
determinism, stale-image and stale-master rejection, partial-frame recovery,
wrong recording/model/map rejection, temporal-sample dispatch, source-clock
forwarding, orchestration and the legacy color convention. The color check uses
a real small FFmpeg encode and decode; it is not a flag-only assertion.

```bash
uv run --frozen --extra legacy python -m unittest discover -s tests/pipeline -v
```

The tests do not claim that the actual scene has better acting or that every
possible frame history is pixel-identical. Native comparison renders and motion
inspection provide that separate visual evidence. New song production still
requires an authored scene and cue file; the registered Song 11 adapter refuses
to substitute another recording or silently retime its choreography.

The deeper, separately implemented auditor for the explicit Consideration registrations is
documented in [tools/concert_review/README.md](../tools/concert_review/README.md).
It records a source baseline after a selected native frame, then checks the final
movie's full decode, presentation times, audio alignment and peaks, color tags,
source identity and encoded cut/batch boundary pictures. It writes only ignored
audit evidence and never re-renders or alters a production output. Its explicit
18-second and 15-second profile contracts must not be advertised as an all-song audit.

## Historical receipt compatibility

The complete 18-second baseline was finished and independently verified at
commit `673f68785c36b57d55d05129ee5549efe6352c60`. Registering the later wrapper
changes the kit adapter hash, so older working receipts become stale on current
source even though the original scene is preserved. Reproduce that historical
receipt with its exact checkpoint, recorded runtime and original font bytes.
The explicit reference-font mode reconstructs those bytes. A fresh checkout still
creates and verifies its own render receipts and audit baseline. Do not edit
fingerprints or reuse the old receipt under a newer adapter identity. A fresh render of the
historical project on current source must receive a new honest receipt.
