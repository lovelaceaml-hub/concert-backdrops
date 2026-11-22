# Natural performance: research and production direction

## Decision and evidence boundary

Improve the performance while preserving the approved native p3d visual language: warm luminous people, a readable human intention, mirror water and a larger world responding to that intention. The immediate engineering direction is an isolated conditioning wrapper around existing captured motion. It must preserve root travel, complete solved poses and stable support contacts. A new renderer alone would not supply choreography.

This document records research and the integration contract. It does **not** certify a completed dance render, natural acting, contact accuracy or owner approval. Use current `STATE.json`, the delivery catalog and the new performance's actual verification for those outcomes. Preserve the approved promo, Song 11 study and earlier Consideration sources.

## What the available motion really contains

The current source audit reports that `assets/p3d/body_v1.npz` contains CMU `05_02`, a roughly 9.333-second dance represented by 281 poses at 30 Hz, and a separate shorter twirl. The official CMU catalog describes `05_02` as expressive arms and pirouette and lists the original capture at 120 Hz. These describe different stages of the data pipeline. Rendering the stored poses at 60 fps interpolates their motion; it does not recover the discarded capture samples. See the [official dance catalog](https://mocap.cs.cmu.edu/search.php?subjectnumber=5).

CMU also warns that hand and toe channels can be noisy, and that finger and thumb channels were added for editing convenience rather than measured finger performance. Hero hand articulation therefore needs an authored layer with its own review. Do not call it captured finger motion. CMU cautions that its earliest sessions may be lower quality, so clip labels alone cannot select the best performance. See the [official database notes](https://mocap.cs.cmu.edu/).

## Required performance contract

### Preserve root travel through the ending

The source audit identifies a dance-to-stand path that resets root travel and a stance search whose limited lookback can change anchors during long holds. The wrapper should preserve the dance's final world transform and blend toward a standing pose at that location. It must not pull a performer back toward the clip's starting point.

Keep body travel and the captured leg motion on the same time mapping. A placement transform must move the whole performance, including contact anchors. This recommendation follows the distinction between character travel and animation travel in [Code vs Data Driven Displacement](https://theorangeduck.com/page/code-vs-data-driven-displacement). Independent movement of the body across the stage can introduce sliding even if individual joints appear smooth.

### Separate flat support, toe pivots and flight

Store explicit support intervals. A flat foot, a pivot on the forefoot, a raised balance and a jump require different constraints. Holding a toe position can still allow the heel to turn or rise. Locking the entire foot orientation during a pirouette would damage the intended action.

Use speed and height to propose contacts, then inspect the labels. A stationary foot held above the floor is not support. Treat brief contact changes and capture noise carefully. [Inverse Kinematics and Foot Locking](https://theorangeduck.com/page/inverse-kinematics-foot-locking) describes contact detection, leg-chain correction, softened extension and offline correction across a complete clip. Its accompanying [implementation](https://github.com/orangeduck/GenoView-InverseKinematics) has an [MIT license](https://github.com/orangeduck/GenoView-InverseKinematics/blob/main/LICENSE); retain that notice if adapting its code.

A support anchor should belong to the entire reviewed contact interval, rather than depend on how much history a rendering worker happened to visit. Retargeting and blending can create footskate after capture; the [original footskate-cleanup paper](https://research.cs.wisc.edu/graphics/Papers/Gleicher/Mocap/cleanup.pdf) explains why contact constraints must survive editing.

### Evaluate the final solved pose at absolute time

Prepare or bake corrections once, with source hashes and recipe parameters. Evaluate root position, joint rotations, support state and transition offsets from absolute time. Rendering frame 600 first must give the same pose as reaching it sequentially.

Blend complete solved endpoints, with coherent root motion, instead of repeatedly applying a fractional arm or leg solve. Preserve velocity across transitions where possible. [Propagating Velocities through Animation Systems](https://theorangeduck.com/page/propagating-velocities-through-animation-systems) provides a useful basis for sampling motion and its derivatives without relying on the previously rendered frame. This is particularly relevant to parallel ranges and subframe shutter samples.

Attach hands, props and effect origins after the final pose is solved. Future Blender authoring needs the same ordering discipline: its [official IK documentation](https://docs.blender.org/manual/en/4.5/animation/constraints/tracking/ik_solver.html) explains chain length, pole targets, stretching and the special constraint evaluation order. Blender is a possible authoring route; this research does not establish a new verified Blender render runtime.

## Make movement readable and expressive

Begin with a full-body performance on a plain, contrasting floor. Keep feet, knees, hands and the space between limbs visible. Review anticipation, the supporting leg, changes of direction, landing compression and the final settlement. Add the heavenly setting after the action reads clearly.

Do not add unrelated oscillation to every joint. The capture already contains movement. An authored answer should have a reason: noticing another person, opening toward them, offering or receiving, and settling. The [Lasseter animation paper](https://users.cs.northwestern.edu/~animation/Lasseter_1987.pdf) connects staging, anticipation, arcs, timing and follow-through to convincing 3D performance. The project's [reference motion review](REFERENCE-MOTION-REVIEW.md) independently emphasizes a visible human release before a large world reveal.

The next model improvements should support that reading:

- Refine shoulder, elbow, knee and ankle silhouettes under the actual poses, including turned and extended views.
- Author restrained wrist rotation and finger groups, with clear relaxed, open, gathered and offering shapes.
- Make garment movement respond to body acceleration and direction changes, then settle after the body. Keep it deterministic through a baked or analytically evaluated response.
- Check garment and limb intersections in close motion. More cloth detail does not compensate for penetration or incorrect attachments.
- Use a quiet region behind translucent performers so flowers and highlights do not cut through their silhouettes.

These are proposed extensions. They are not completed model or cloth claims.

## Proposed study and review gates

An eighteen-second phrase can begin with preparation, develop through a traveling arm arc and supported turn, introduce an answering performer, and finish with a shared opening before the world responds. Adapt its duration to an inspected phrase and the selected recording; do not splice unrelated captures solely to hit a target length.

| Passage | Main proof |
| --- | --- |
| Preparation and first step | Attention, support and visible weight transfer |
| Turn and extended line | Stable contact type, continuous root travel and readable silhouette |
| Answering performer | Related action with deliberate timing rather than a duplicate loop |
| Opening and settlement | Complete physical arrival before a larger light or camera response |

Measure contact drift only during deliberately stationary support intervals. A 5 mm maximum is a proposed starting target for hero contacts, not a published universal threshold. Review intended pivots separately. Check floor penetration, segment-length preservation, knee flips, root discontinuities and shuffled-frame equality. Inspect densely around transitions and review the actual encoded ending. Technical measurements cannot certify beauty.

## Expansion and provenance

Retain the existing CMU/NSF acknowledgement and source hashes. CMU's [published terms](https://mocap.cs.cmu.edu/) permit inclusion in commercially sold products but prohibit selling the motion data itself; its [FAQ](https://mocap.cs.cmu.edu/faqs.php) permits copying, modification and redistribution. Respect its request against crawling the database. Acquire only selected files through a documented recipe.

For later variety, inspect `05_03`, `05_11`, `05_12` and modern-dance material from subject 49 before adding them to a reusable library. Record original capture rate separately from prepared rate and render fps. A future reimport at higher source rate is a new asset revision that requires fresh comparison.

[Bandai Namco's official motion dataset](https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset) offers professional-actor BVH data, but its datasets use CC BY-NC 4.0 while its Blender visualization code uses MIT. Do not inherit the script license for the motion data. It is a research option, not the default production source for this increment.

Continue through bounded reviewed examples: one strong solo, one meaningful duet, then varied ensemble timing and new garments. Keep cloud CPU rendering usable throughout; the Mac and an external GPU provider are not prerequisites for this performance work.
