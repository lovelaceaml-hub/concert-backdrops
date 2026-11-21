# Consideration: camera plan for the next revision

## Current creative issue

**The current movie is still a performance proof, not a polished hero shot. Around 7.2 to 8.1 seconds, the two translucent gold figures overlap so strongly that their torsos, heads and arms briefly read as one figure. The release becomes hard to follow.** This is a projected silhouette and camera-coverage problem. The reviewed images do not establish a physical body collision.

The frozen current movie remains unchanged. Two private native stills test other camera positions at the same scene time, with the same authored poses, timing and lighting inputs. They are planning evidence for a new revision, not replacement frames or an approved fix.

## Evidence and identity

The action review inspected 43 actual production PNGs from frame 300 to 552, every six frames, covering 5.0 to 9.2 seconds at 60 fps. Additional native hand/foot crops followed the approach, grip, rise and release. The 5.0 to 5.6-second foot/shin overlap clears in projection by 6.0 as the helper steps back. The held grip reads from 5.3 through 7.0; the main readability failure comes as the bodies overlap during the rise and release. The authored standing settle starts at 9.5 seconds, outside that sampled interval.

The camera tests use **frame 450, 7.500 seconds**, native **1920x1080**, two temporal samples and one llvmpipe thread. Base picture-source identity:

`2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e`

The [machine-readable evidence](evidence/consideration-camera-plan.json) records exact rigs, image and override-script hashes, sample settings, numerical diagnostics and the next validation requirements. The alternate-camera scripts live in ignored work space and are separate from canonical production inputs. No kit, engine or pipeline source was changed.

This remains sampled image review. It is not real-time playback, an audio/synchronization assessment or full-shot acceptance.

## The two candidate views

Positions and targets are world metres, with Y upward. All three views use a 35-degree vertical field of view, 0.009 m aperture, target focus, zero roll, zero handheld motion and 0.1 m near plane.

| View at 7.500 seconds | Camera position | Look target | Head-center horizontal separation | Pelvis-center horizontal separation |
| --- | --- | --- | --- | --- |
| Current baseline | `(1.35, 1.50, 5.90)` | `(-0.09, 1.025, 1.685)` | 59.2 px | 77.3 px |
| Proposed west45 | `(-3.20, 1.65, 5.10)` | `(0.002, 1.02, 1.944)` | 177.1 px | 264.8 px |
| Proposed west69 | `(-4.25, 1.85, 3.60)` | `(0.002, 1.02, 1.944)` | 170.1 px | 256.7 px |

The baseline is the moving 3.0 to 12.0-second dolly, sampled at 7.5 seconds. Each candidate is a constant camera used only to test this one frame. Its full hold interval in the test script is not a proposed final shot design.

**West45 is the preferred starting point for the next revision.** In the actual still it shows two distinct heads and torsos, a readable shared-hand region and the willow framing. West69 also separates the bodies, but plants intrude more through the lower torso region. Both still need background clearance work. The pixel separations quantify this one view; they do not certify natural acting, contact or good coverage at other times.

The labeled comparison is saved at `work/concert-kit/camera-planning/Consideration-Camera-Planning-Frame450.png`. It shows the actual baseline and proposed west45 source images, each native 1920x1080 and scaled equally to 960x540 on the sheet. The proposed view is explicitly labeled as a single-frame plan, not the current movie or an approved fix. Media remains outside the committed source tree.

## Strict guard limitation

The first script wrote west45, then stopped because a strict before/after marker-list equality check failed. That first run did not save the numerical difference, so it must not be described as having passed that guard.

The second and final render, west69, recorded the full diagnostic. Both actors' complete bone matrices were exactly equal before and after the render, with maximum difference **0.0**. Only the helper's `foot.L` marker differed, by **7.771561172376096e-16 m**. That measured difference is floating-point recomputation, not an authored pose change. The frozen source identity remained unchanged. No additional movie or extra camera-test frames were rendered to prepare this document.

## Required next coverage pass

1. Create an explicit camera revision starting from west45. Review the entire approach, grip, rise, release and settle, especially 5.0 to 9.5 seconds. Preserve the action and verify that a better 7.5-second view does not hide another essential moment.
2. Check the 3.0 and 12.0-second shot boundaries, gaze direction, full-body framing, hand contact and planted feet. Move or dim background plants and the stool only after reviewing their relationship to the chosen complete camera path.
3. Render and inspect the revised motion with the prepared audio, then check the encoded result. Keep the current baseline and this planning evidence separately identifiable until the new revision is reviewed. A pleasing still alone is insufficient to call the problem fixed.
