# The Flow of Light: fluid fan performance

Updated November 22, 2026, America/Los_Angeles.

The owner asked for more graceful movement, better character presentation and a
repeatable cloud workflow, then explicitly asked to build the environment and
make the video. This increment creates a new continuous 12-second solo for
**The Words of Mother's Love**, with a separate fixed-camera movement proof.
The earlier delivered films retain their original identities and review records.

## Completed delivery

| Saved file | Contents |
| --- | --- |
| [The_Flow_of_Light_1080p60.mp4](https://chatgpt.com/library?file_id=libfile_95c6ea34d15881918c2f4a05d8a2db31&account_id=personal) | Complete 12-second native 1080p60 presentation with soundtrack; 7,870,567 bytes. |
| [Fluid_Fan_Movement_Proof_540p60.mp4](https://chatgpt.com/library?file_id=libfile_9e52c503c5c08191aec5effb482dbd7a&account_id=personal) | Same 720-frame motion in a fixed-camera 540p60 review view. |
| [Fluid_Fan_Editable_Assets.zip](https://chatgpt.com/library?file_id=libfile_2702039560a08191bdf1f1497759b6d4&account_id=personal) | Editable Blender body animation, exact motion/cloth/audio inputs, manifests and asset handoff. |

Both movies passed full technical decoding and timing checks with no errors or
warnings. Visual review covered 122 distinct proof PNGs and 28 distinct decoded
presentation frames; it was ordered-frame inspection, not real-time playback.
Exact checksums, review scope and remaining visual limits are preserved in
[the delivery record](evidence/fluid-fan-delivery.json). Source and handoff are in
[PR #111](https://github.com/lovelaceaml-hub/concert-backdrops/pull/111), opened as a
draft. Owner creative approval is not recorded.

## What changed

Seven deliberate steps, a continuous pelvis path, coordinated torso and fan
arcs, a prepared full turn, recovery and an offering finish replace the earlier
repeating support-side weight pulse. The current performer keeps the existing
74-bone character asset. The turn uses rigid-foot toe pivots, not new toe joints
or a force-based balance simulation. The motion is original authored animation;
the supplied performance recording was visual guidance, not extracted mocap.

The new pearl, lavender and rose costume uses a continuous shaded color surface
with restrained luminous detail. The skirt is simulated against the exact baked
performance. The camera keeps the full body and fans visible in a single gentle
move. The proof uses the same motion with a fixed camera and visible lower-body
structure so support and timing can be inspected.

## Working authoring and rendering path

The new Python controls and IK are transferred to a real deforming Blender
armature and editable bone animation. Blender evaluates that animation and
exports a motion bundle consumed by the native concert renderer. A saved Blender
revision can also be exported without rebuilding its keys or overwriting it.

The saved-animation route validates the original rest structure and timing,
includes rigid armature-object travel, and rejects unsupported bone stretching
or scale. Its new evaluation reference allows the native adapter to be checked
against the edited animation. Inherited support annotations become unknown and
must be reviewed; fan-opening timing still comes from the original input.
Mesh/material edits and Blender cloth are outside this animation exchange.

The `.blend` contains the editable body animation and a simple preview, not the
complete concert scene or a new animator control-rig interface. The concert
materials, held fans, stage, lights, camera and native cloth remain in the source
checkout. See the [executable guide](../../tools/fluid_dance/README.md) for exact
setup, export, validation, cloth, preview and delivery commands.

## Resources used

This production uses the available Linux cloud environment: Blender 4.3.2,
Python 3.12.14 with the project dependency lock, FFmpeg 7.1.5, Mesa software EGL,
the existing body/brand assets and project fonts. It reports nine logical CPUs
and about 10 GB RAM, with no dedicated GPU. Four bounded workers render each
project. No paid API, new subscription or Mac rendering was used.

The presentation target is native 1920 × 1080 at 60 fps, 720 frames, with two
temporal samples per frame. The fixed-camera review preset is 960 × 540 at the
same 60 fps. It is a review view, not an upscaled production master.

Sound is a 12-second excerpt from the supplied Petals recording at its original
speed, with short entrance/exit fades. Exact beat matching has not been claimed.
Private input and output media are recovered from the saved asset package, not
from the public source repository.

## Verification and review boundaries

The original bridge was checked across all 1,441 samples at 120 Hz. Native joint
differences were below 0.00051 mm and selected skinned-point differences below
0.00075 mm. These numbers measure preservation through the bridge, not physical
realism or grace. The saved-file path was checked with both the untouched file
and a separately saved wrist-key edit; the untouched motion arrays matched
exactly, while the edited version changed and passed against its own evaluation.

The cloth audit checks all 362 saved states. The solver includes body collision
but no cloth self-collision or cloth interaction between separate performers.
Native still review caught and corrected garment grain, excessive gold glare,
trouser material showing through the skirt and poor painted reflections.

Technical delivery and encoded-frame review are recorded against the exact
finished files in the delivery evidence. Owner creative approval remains a
separate decision. This increment is one authored solo, not an automatic
five-person retargeting system or a complete replacement of the earlier show.

## Reuse without repeating the brief

Retain the score, rig and rest identity, performance bundle, editable Blender
file, costume snapshots, soundtrack, runtime versions and render receipts as
one version. Change one authored performance revision at a time; export it,
validate it against the matching evaluation, bake its costume and inspect the
whole movement before recording a creative decision.

For ensemble work, author spacing, individual roles, timing and interactions
explicitly. The present cloth and bundle checks do not establish group
collision safety, natural formation changes or artistic ensemble quality.

Source branch: `creative/fluid-fan-performance-20261122`.
Source commit: `dd38d291fb7c548f82732b6bff94c0eca02748b2`.
Its tree `e83ffd14631b06387eb044de6ffa8123fb632f8b` is identical to the local
picture-source commit `bf66832b224a87e490cf1610bd3dd14db4b27331` recorded by the
render environment. Later handoff-only commits do not change these pictures.
