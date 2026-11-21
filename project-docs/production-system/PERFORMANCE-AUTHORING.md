# Performance authoring contract

## Status and purpose

Design contract, November 21, 2026. **The Blender exporter, portable performance bundle and renderer adapter described here are proposed work.** This document does not establish a Blender installation, a tested Blender CPU runtime, extracted motion from the linked videos, or a completed new performance. Keep implementation evidence, rendered output, visual review and owner approval separate.

Preserve the approved luminous people, mirror water, expressive colors and meaningful human action. Mother's Words of Love remain the message. Read [START-HERE.md](START-HERE.md), [CREATIVE-RULES.md](CREATIVE-RULES.md) and the selected song record first. Do not alter approved snapshots or replace captured motion with unrelated procedural oscillation.

## Verified starting point

The [motion catalog](catalogs/motions.json) records eight prepared clips from seven source captures. The current dance uses CMU 05_02, stored as 281 poses at 30 Hz. Both performers reuse that phrase with a 0.6-second offset. Sixty-frame-per-second output interpolates those samples; fingers and thumbs were not captured. This is an available phrase, not a complementary duet or a general motion importer.

[NATURAL-PERFORMANCE.md](NATURAL-PERFORMANCE.md) records the completed eighteen-second native 1080p60 movie, technical audits and sampled visual review. Creative approval remains unrecorded. One native 4K frame was delivered; the configured full 4K movie remains unrendered.

The isolated [performance layer](../../tools/concert_dance/performance.py) preserves root travel, estimates stable heel/toe support intervals and applies bounded kinematic correction. It evaluates absolute time and attaches trails to solved wrists. It does not simulate balance or force. Existing [cloth](../../engine/p3d/cloth.py) advances in fixed 1/120-second steps and stores 1/30-second snapshots. That implementation is not evidence of a verified Blender cloth exchange or physically simulated long silk.

## Reference intake and authority

Keep three inputs distinct: geometry references describe silhouette and garment construction; movement references describe timing, weight transfer and relationships; reusable motion assets contain transforms, skeleton identity and usable provenance.

For every source record its author/dataset, URL, exact file hash when acquired, original rate, selected time range, shot boundaries, known camera movement, performer IDs, terms, attribution and authorized use. Use licensed captures, authorized footage or authored animation. A public video link does not itself establish permission to redistribute its footage or extracted data. Keep full songs, copied lyrics, footage and caches outside Git.

Review a continuous phrase including preparation and recovery. Mark hidden joints, uncertain contacts and camera changes. Monocular references do not uniquely determine occluded limbs, body scale or a shared stage path. Multiple overlapping performers and loose costumes increase that uncertainty. Do not promise exact extraction from a YouTube video. Additional full-body and costume references can improve decisions without blocking the initial analysis.

## Proposed production boundary

Use Blender for control-rig authoring, retargeting, IK correction, phrase assembly and optional costume simulation. Export the evaluated performance as an immutable bundle. An isolated adapter then supplies the existing luminous renderer with final body poses, attachment positions and cached garment geometry.

Blender's [visual-key bake API](https://docs.blender.org/api/5.3/bpy.ops.nla.html) records final transformations with constraints applied. Baking is the boundary: render workers must not depend on a live Blender control rig, interactive state or earlier frames rendered by another worker. NLA assembly does not remove the need to author valid weight-transfer transitions.

The proposed bundle contains a versioned JSON manifest, numeric pose arrays, contact annotations, optional garment caches and QA receipts. Record every member's hash, exporter and engine versions, source commit, source assets and recipe. Use explicit numeric arrays without executable serialization. These filenames and schema fields require implementation before any bundle can be called supported.

### Skeleton, spaces and transforms

The first schema must specify all of the following:

| Item | Required convention |
| --- | --- |
| Skeleton | Stable joint names, anatomical left/right, one root, parent indices, topology hash and retarget map |
| Geometry | Mesh/skin-weight identity, body dimensions, bind transforms, inverse binds and rest-pose hash |
| Coordinates | Right-handed, metres, +Y up, +Z prepared forward; the current body's +X is its anatomical left |
| Matrices | Column-vector transforms; row-major serialized matrices; composition applies the rightmost transform first |
| Rotations | Unit Hamilton quaternions in `wxyz` order; active rotations; radians for angle metadata |
| Pose data | Full parent-relative posed transforms for non-root joints; complete stage-space root transform in a separate channel |
| Scale | Unit runtime bone scale; apply a documented uniform conversion once to translations and geometry |

The root channel includes root height, travel and facing. Do not add rest height or travel again in the adapter. An optional staging transform moves the whole solved performance, contacts and props together exactly once. For non-root joint `i`, `world[i] = world[parent[i]] @ local[i]`; the root world transform comes from its explicit root channel.

Preserve both bind and neutral-pose definitions. Current [Rig.fk](../../engine/p3d/assets.py) consumes rotations in neutral frames and separately applies its modeled-rest corrections. Blender bone-local rotations cannot be copied directly into that API. The adapter must derive the equivalent target transforms and demonstrate rest, neutral and asymmetric posed round trips. Source and target joint names alone are insufficient.

Record an explicit basis-conversion matrix, including the author's chosen forward direction. Convert translations and rotations consistently; never guess from Blender's up axis alone. Reject reflections, unsupported bone stretching or nonuniform animated scale. The first adapter should require fixed bone lengths and constant non-root translations; unsupported input must fail visibly rather than lose channels.

Normalize quaternions, maintain sign continuity and use shortest-path interpolation where appropriate. Record interpolation and endpoint rules. Preserve source precision; begin with at least float32 pose arrays, then measure any later quantization against the approved bake. Existing float16 capture arrays do not justify reducing new hand or contact data without comparison.

### Timing and evaluation

Record original capture rate, prepared rate and output rate separately. Store rational frame rates, an integer timebase and one explicit rounding policy shared by exporter and adapter. Every sample has an absolute timestamp. Map source time to scene time and scene time to song time explicitly; musical events reference the exact recording hash.

Declare clip endpoints, loop periods, hold behavior, blend intervals, pre-roll and permitted retiming. A loop requires reviewed pose and travel closure. Retiming must move body motion, contact annotations, props and attention together, followed by a new cloth bake. Faster playback does not automatically preserve a plausible step.

Bake enough temporal detail for the chosen motion and shutter samples, then compare interpolation with direct evaluated poses. Do not claim that resampling 30 Hz capture recovers missing motion. Shutter samples must stay within their shot, and caches must cover every requested subframe. Integer frame counts, sample timestamps and actual encoded presentation times are acceptance evidence.

## Choreography, contact and uncertainty

Each performer has a role record: intention, source phrase, entry/exit support, stage path, facing, attention target, gesture, interaction partner, costume and cue clock. A lead may initiate; another performer may receive or answer; ensemble groups may develop that response through deliberate formation changes. A timed canon is valid when intentional. Repeating one phrase with offsets does not establish varied ensemble choreography.

Build a complete solo before a duet, then expand reviewed interactions into groups. Preserve anticipation, weight shift, torso arcs, turning support, landing compression and recovery. Camera moves and world effects should reveal those events. They should not conceal an unfinished grip or unstable landing.

Use explicit contact vocabulary:

| Label | Meaning |
| --- | --- |
| `flat_support` | Reviewed stationary sole region; constrain its identified contact geometry |
| `heel_pivot` / `toe_pivot` | Named support point stays anchored while permitted foot rotation continues |
| `rolling_contact` | Support migrates across the foot; not one stationary anchor |
| `free` / `airborne` | No floor constraint for that effector |
| `hand_support` / `partner_contact` / `prop_contact` | Named surface or partner target with a defined relative transform |
| `unknown` | Insufficient evidence; requires review before a support constraint is asserted |

Every event includes performer/effector, source and scene intervals, surface/partner, anchor frame, permitted degrees of freedom, constraint weight, correction bound and annotation origin. Distinguish `observed`, `inferred`, `authored` and `unresolved`; retain confidence and reviewer notes separately. Estimated confidence is not physical force or creative approval.

Do not infer support from low speed alone. A raised foot may be motionless. Partner constraints require an acyclic evaluation order or one coupled offline solve, with approach, contact, release and recovery baked together. Aerial or lifted performance needs its own support/path model and proof, not reuse of floor-foot rules.

## Hands, attention and flowing materials

Add authored finger groups, thumb opposition, wrist orientation and palm targets. Start with relaxed, gathered, open, offering and receiving shapes, with deliberate transition timing and anatomical limits. Distinguish authored fingers from measured finger capture. Attention records identify a partner, hand, prop or destination; coordinate head and torso response rather than adding independent eye/head noise. Preserve established luminous-face and portrayal rules.

Keep three material systems distinct:

- **Light trails:** emissive history following final solved attachment points. The current analytic wrist trails belong here.
- **Long silk props:** finite length and width, grip locations, leading/tail response, self/body contact assumptions and possible slack or tension. Prototype explicitly as a constrained strip or authored deforming surface, then review its silhouette and turns.
- **Garments:** cloth attached to the body with specific seam/pin groups and collision proxies. A sleeve is not a decorative trail pasted over an arm.

Blender's [cloth cache documentation](https://docs.blender.org/manual/en/latest/physics/cloth/settings/cache.html) describes baking and invalidation after relevant changes. A production cache identity must include the solved body bundle, body shape/scale, topology, rest shape, pins, collision geometry, material parameters, solver/version, substeps, seeds, wind, pre-roll, time range and sampling policy. Altering a dependency invalidates the cache. Freeze the cache before parallel rendering, and derive all effect origins from the same solved performance.

## Optional analysis tools and resource limits

[MediaPipe Pose Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker) offers 33 body landmarks. Its world landmarks are hip-relative per person, not absolute shared-stage root travel. [Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker?tab=Python) supplies 21 landmarks per hand. The [Python setup](https://developers.google.com/edge/mediapipe/solutions/setup_python) exposes a CPU delegate. Optional use here is measurement overlays and annotation assistance. Installation, speed, tracking continuity and useful accuracy on these references remain unverified.

WHAM and GVHMR remain research candidates. [WHAM's documented setup](https://github.com/yohanshin/WHAM/blob/main/docs/INSTALL.md) uses tested Ubuntu configurations and CUDA 11.3; its [code license](https://github.com/yohanshin/WHAM/blob/main/LICENSE) is MIT. [GVHMR requirements](https://github.com/zju3dv/GVHMR/blob/main/requirements.txt) pin CUDA 12.1 packages and a Linux CUDA wheel; its [license](https://github.com/zju3dv/GVHMR/blob/main/LICENSE) restricts use to educational, research and nonprofit purposes. Neither documented stack establishes a working CPU or Apple Metal route here.

Their body-model dependencies have separate terms. The [SMPL-X model license](https://smpl-x.is.tue.mpg.de/modellicense.html) includes noncommercial artistic projects but restricts model redistribution. Do not put those models into the shared handoff under an estimator's code license. Existing [CMU terms](https://mocap.cs.cmu.edu/) and [FAQ](https://mocap.cs.cmu.edu/faqs.php) remain relevant to selected captures; preserve attribution and acquisition records.

Cloud CPU is the default. This proposal installs no paid service, configures no GPU provider and uses no Mac worker. Blender solving/baking is the CPU-first implementation target, not a measured performance guarantee. Rendering speed and maximum memory require representative measurements.

## Implementation stages and acceptance

1. **Contract and fixture:** implement schema validation and one asymmetric rest/neutral/posed fixture. Verify joint mapping, basis, units, bind transforms and root placement before importing a whole phrase.
2. **Body exporter and adapter:** solve and export an 8 to 12-second continuous solo with an entry, travel/turn and complete recovery. Compare Blender evaluation and adapter joints/attachments at regular and adversarial timestamps. Keep approved assets unchanged.
3. **Hands and contact:** author attention, fingers and reviewed support events. Render a plain-floor proof showing the complete body from useful views. Resolve release, joint flips and root discontinuities before styling.
4. **Costume and partner:** bake the exact costume, then add a separately motivated answering phrase. Review intersections, shared targets, projection overlap and both performers' recovery together.
5. **Production registration:** register the isolated scene and immutable source/cache identities. Render native-size frames, a complete encoded motion proof and only then the intended delivery. Save receipts and update catalogs through the normal coordinated workflow.

Acceptance must report actual tests and scoped observations:

- Sequential, reverse and shuffled seeks must agree at every requested pose, attachment and cloth sample within declared tolerances. Repeat across worker boundaries and fresh worker initialization; inspect joins and shutter subframes. Same-environment frame equality and cross-environment numeric agreement are different claims.
- Validate finite data, normalized rotations, segment lengths, root continuity and timestamp coverage. Measure position/rotation and velocity changes around phrase joins against recorded limits chosen for that action.
- Measure planted-contact slip only inside labeled stationary support intervals, with anchor frame, sample count and constraint weight reported. Evaluate pivot anchors and rolling contacts separately. No eligible samples means `not evaluated`, not zero slip. A 5 mm hero-contact target is a proposed project starting point, not a universal rule.
- Verify source/scene/song mappings, cue events, frame count, encoded timestamps and audio alignment against the exact recording. Automatic timing checks do not establish that phrasing feels musical.
- Watch the actual continuous encoded motion at normal speed. Record silhouette, weight transfer, hands, costume behavior, interaction and ending findings. Sparse decoded frames are explicitly a limited review.

There is no universal naturalness score. Passing measurements, readable motion, artistic judgment and owner approval remain separate milestones, each attached to an exact source and output identity.
