# Fluid fan performance

This module produces **The Flow of Light**, a continuous 12-second solo on the
existing luminous concert character. It has its own choreography, frozen
performance bundle, costume cache, plain movement proof and concert presentation.
The registered final format is 1920 × 1080 at 60 fps, with 720 output frames.

## What is implemented

`score.py` authors root travel, foot support, whole-body poses, hands and fan
opening through Python controls and IK. `bundle.py prepare` samples the solved
phrase at 120 Hz. `blender_bridge.py` builds an actual 74-bone Blender armature
with the original modeled mesh and skin weights, writes editable bone keys,
evaluates that armature, saves `authoring.blend`, and exports the resulting
performance. The native renderer consumes the evaluated bundle for body skinning
and attachments. Native cloth is baked separately against that exact performance.

This is authored animation, not motion recovered from the reference videos.
The Blender file contains a deforming armature and dense bone keys; it does not
provide a newly built animator control-rig UI, new articulated toe bones, or a
Blender cloth exchange. Its simple preview material is not the concert look.
The CLI can either build keys from Python-authored input or evaluate an existing
saved Blender animation without replacing its keys. Both routes export a separate
numeric bundle; a saved Blender edit becomes renderer input after that export.

## Environment and inputs

Run these commands from the repository root on Linux. The measured environment
is recorded in `work/fluid-dance/environment.json`: Python 3.12.14, Blender 4.3.2,
FFmpeg 7.1.5 and Mesa llvmpipe through EGL. It has nine logical CPUs, about 10 GB
of RAM, and no dedicated GPU. The configured pipeline uses four render workers
with one thread each. These are the observed resources, not a minimum hardware
specification or a render-time guarantee. No paid service is required.

For a fresh network-enabled environment, install the host tools required by
`scripts/bootstrap.py`, then prepare the locked Python dependencies and exact
reference fonts:

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
```

This mode does not install Blender. Provide **Blender 4.3.2** separately and ensure
`blender`, `ffmpeg` and `ffprobe` are on `PATH`. Existing environments may use
`uv sync --frozen --extra legacy` and restore the recorded project fonts. The
current isolated environment was recovered from a compatible existing runtime
after an offline wheel-cache miss; its exact package versions are in the receipt.

Retain these inputs with the source checkout:

| Input | Identity and purpose |
| --- | --- |
| `assets/p3d/body_v1.npz` | Original body, topology and skin weights; exact SHA-256 is in the performance manifest. |
| `fonts/` and `assets/p3d/brand/land_2048.png` | Existing typography and concert assets, hashed by the renderer. |
| `work/fluid-dance/performance/` | Editable source and frozen motion; see its `ASSETS_README.md`. |
| `work/fluid-dance/cloth.npy` and `cloth.json` | Matching native costume snapshots and identity receipt. |
| `work/fluid-dance/audio.wav` and `audio.json` | First 12 seconds of the user-provided Petals recording, at original speed. |

The exact audio SHA-256 is
`61f91f23d2a16fa487576687b007852c3f6c19f753e129e61b7bb3f6fb5d7a37`.
Restore those audio bytes from the saved assets: the commands below do not fetch
or recreate the private soundtrack. Exact beat/choreographic hit matching has
not been established. Reserve disk space for the PNG sequence as well as movies.

## Reproduce the performance and costume

Set the shared environment once in the current shell:

```bash
export PYTHONPATH=engine:.
export PYTHONHASHSEED=0
export OPENBLAS_NUM_THREADS=1
unset FLUID_DANCE_BUNDLE FLUID_DANCE_CLOTH
```

To reuse the saved bake, retain `performance.npz` and its matching JSON and skip
the first two commands. Run validation when the authoring input is available.
To deliberately rebuild from the checked-out score:

```bash
.venv/bin/python -m tools.fluid_dance.bundle prepare \
  --out work/fluid-dance/performance/authoring-input.npz --sample-hz 120

blender -b --factory-startup -t 2 --python-exit-code 1 \
  --python tools/fluid_dance/blender_bridge.py -- \
  --input work/fluid-dance/performance/authoring-input.npz \
  --output work/fluid-dance/performance/performance.npz \
  --blend work/fluid-dance/performance/authoring.blend

.venv/bin/python -m tools.fluid_dance.bundle validate \
  --bundle work/fluid-dance/performance/performance.npz \
  --source work/fluid-dance/performance/authoring-input.npz \
  --out work/fluid-dance/performance/validation.json

.venv/bin/python -m tools.fluid_dance.prepare
```

Keep `FLUID_DANCE_CLOTH` unset during preparation. The last command reuses a
matching cache or bakes it again; it validates its source identity, byte hash,
shape and finite values. The 120 Hz native cloth solver stores 362 snapshots of
640 vertices at 30 Hz, including an endpoint interpolation guard. Changing the
performance, body or costume requires the matching new cache.

## Export saved Blender edits

Open `authoring.blend` in Blender 4.3.2, edit the bone animation, and save a copy
as `work/fluid-dance/edited-authoring.blend`. Retain the original armature name,
bone names, hierarchy and rest pose. This export keeps the original 12-second
timing: frame 1 is t=0 and frame 721 is t=12. It supports rigid object travel and
evaluated bone rotations; scale, shear, stretching, changed rest structure and
linked libraries are rejected. Use a new output directory for each revision:

```bash
blender -b --factory-startup -t 2 --python-exit-code 1 \
  --python tools/fluid_dance/blender_bridge.py -- \
  --input work/fluid-dance/performance/authoring-input.npz \
  --from-blend work/fluid-dance/edited-authoring.blend \
  --output work/fluid-dance/edited-performance/performance.npz

.venv/bin/python -m tools.fluid_dance.bundle validate \
  --bundle work/fluid-dance/edited-performance/performance.npz \
  --source work/fluid-dance/edited-performance/performance-evaluated.npz \
  --out work/fluid-dance/edited-performance/validation.json
```

The saved file is opened with embedded scripts disabled and is not overwritten.
The new manifest records its exact hash. Validation compares the native adapter
to the **edited Blender evaluation**, not the previous Python poses. Old foot
support labels become `unknown`; `contact=false` means no support is asserted,
not that the foot was verified airborne. Fan-opening channels retain their source
timing and require review alongside edited hands. There is no annotation editor
in this first bridge. Review contacts and grip in the full movement proof.
This route exports animation; Blender mesh and material edits do not replace
the native character or its concert materials.

After validation, set `FLUID_DANCE_BUNDLE=work/fluid-dance/edited-performance`,
keep `FLUID_DANCE_CLOTH` unset, and run `tools.fluid_dance.prepare` again before
rendering. The current registered renderer uses `work/fluid-dance/cloth.npy`;
preserve the original cache pair before deliberately replacing that working cache.

## Review and render

Inspect full-body stills in a fresh output directory:

```bash
.venv/bin/python -m tools.fluid_dance.render --mode proof \
  --stills 0,2.5,6,9.5,11.8 --out work/fluid-dance/proof-stills
```

The direct still command skips existing filenames, so choose a new directory
after changing inputs. For a complete movie, the registered pipeline prepares
its identity, renders, assembles the soundtrack, runs technical QA and creates
a contact sheet:

```bash
.venv/bin/python -m pipeline.cli produce fluid-dance-solo --quality final --plan
.venv/bin/python -m pipeline.cli produce fluid-dance-proof --quality final
.venv/bin/python -m pipeline.cli produce fluid-dance-solo --quality final
```

The plan command is read-only. Outputs and receipts are under
`work/pipeline/<project-id>/<quality>/`. Use `--quality draft` for a 960 × 540
preview; `review` and `final` use native 1080p with two temporal samples per frame.
Watch the complete encoded proof and presentation at normal speed before
recording a creative decision. A finished technical job is not owner approval.

## Reuse and limits

`scene.make_performer()` installs the score and then
`install_bundle(body, bundle_path)` **before** any skin, prop or cloth sampling.
The adapter requires the matching woman rig, height 1.66 m, build 0.96 and original
asset. It supplies the final `actor.frame`; fan openings come from the bake too.
The bundle has explicit metre units, native +Y up / +Z forward, absolute root
motion, parent-relative neutral-frame rotations, and recorded rest corrections.
It interpolates quaternions with shortest-path slerp and holds both endpoints;
this phrase is not a loop. Support labels are authored annotations, not force data.

For a new phrase, edit the controls in `score.py`, export and validate a new
bundle, bake its costume, then review the whole movement proof before rendering
the presentation. If duration, performer proportions or soundtrack changes,
update the score, preparation limits, render/project timing and asset identities
together. The present registration is deliberately one 12-second solo; it is not
an automatic retargeter or an ensemble generator. For direct Blender revisions,
use the saved-animation export and its matching evaluated reference above.

The saved numerical receipt compares all 1,441 body samples, selected full-skin
samples and a same-instance shuffled seek probe. Maximum native joint error is
about 0.00051 mm; selected skin error is about 0.00074 mm. The cloth receipt checks
all 362 stored states against its geometric limits. These checks establish the
bridge and cache correspondence, not grace, plausible balance, musical phrasing,
or freedom from every visible intersection. Continuous visual review, fresh-worker
render checks and owner approval must be recorded against the exact resulting
movie. No creative approval is implied by these asset receipts.

The saved-Blender export was exercised separately in
`work/fluid-dance/reexport-check/`: exporting the untouched file reproduced its
motion arrays exactly, and a saved copy with one deliberate wrist-key edit
produced changed motion that passed comparison with its own Blender evaluation.
Both exports correctly invalidated inherited support annotations. The production
performance, source Blender file and costume were not changed by those checks.
