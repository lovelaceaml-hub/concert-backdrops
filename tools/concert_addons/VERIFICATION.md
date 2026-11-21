# Native prototype verification

This pack is **awaiting owner review**. Technical checks and assistant visual inspection do not approve it for a concert song. Only the isolated `tools/concert_addons/` files were added for this work. The approved scene sources, existing engine, pipeline projects and Consideration renderer stayed unchanged.

## Frozen source and runtime

**Appearance v2 is the current pack**, with constructor API revision 1. Its canonical source-map SHA256 is:

`b5f44f3626d1bf6685dbe24cbf1e20b3bc31759e99d9983b28a2beba0d4710f2`

This is the SHA256 of the sorted compact JSON source map in `work/concert-addons/art-v2/render-freeze.json`. It includes this pack's Python files, existing engine Python, lock files and actual pinned font bytes. Documentation changes do not enter the picture identity.

**Rig baseline v1 is preserved privately as superseded evidence.** Its source-map SHA256 is `96254c1535a952629efde164f3fb254a826649ba3b520ba6594369c0db598d36`. Its original Python files and receipts are archived in `work/concert-addons/rig-baseline-v1/rig-baseline-source-and-receipts.zip`. Its movie is tied to that old source identity, not to the modified current constructors. The Rose and Wheat appearance stayed unchanged in v2; the Dove and flight camera were refined after review.

The observed runtime was cloud CPU software rendering through `llvmpipe (LLVM 19.1.7, 256 bits)`. Native stills used 1920 by 1080 pixels, 60 fps time evaluation and two temporal samples with the existing 0.30-frame shutter. No frames were upscaled. The source is display RGB8 through the established p3d filmic curve, not an HDR or 16-bit delivery.

## Geometry and contact checks

The executable check is `python -m tools.concert_addons.verify`. The current v2 record is `work/concert-addons/art-v2/geometry-verification.json`; the earlier baseline record is retained separately.

| Check | Observed result |
| --- | --- |
| All six constructor/variant combinations normalize through native p3d | Passed |
| Finite positions and unit surface normals at eight times | Passed |
| Sampling a later time and returning to the same earlier time | Identical full batch hashes |
| Evaluating an additional 1/120 second | Actual positions change for every variant |
| Dove planted-foot drift before release and after touchdown | 0 metres |
| Largest foot-position jump across either event, sampling 1 microsecond before and after | About 1.1e-16 metres |
| Largest shoulder/elbow or elbow/wrist length deviation over 31 poses | About 2.8e-16 metres |

The current default Dove has 11,125 surface points and line segments, a Rose has 8,806 and the 11-stem Wheat has 8,679. These counts include line segments and are not triangle mesh counts. Fixed bone lengths and foot locks establish specific geometric constraints; they do not establish biological flight accuracy.

## Native stills

The current final round is `work/concert-addons/art-v2/final-native/`. Its three receipts include exact source hashes and every image SHA256. `native-v4/` is the old rig baseline's final still round, not the current appearance. Other probe folders are diagnostic history.

| Family | Actual rendered times | Variants shown |
| --- | --- | --- |
| Dove flight | 0, 1.65, 2.8, 4.55, 5.7 seconds | Ivory |
| Layered rose | 4.5 seconds | Blush, crimson, golden |
| Wheat clumps | 2.8 seconds | Ripe and green |

The final v2 round took about 1.21 to 1.64 seconds per native still after initialization in this shared cloud environment. The flight still process reported a peak resident set of 487,824 KiB, about 476 MiB. These are observations from this small proof, not a performance estimate for the full concert scenes. The final receipts provide the exact measured run values.

The current overview sheet is `work/concert-addons/art-v2/model-contact-sheet-v2.png`, SHA256 `10f9fff181445728fb9dd4e84818130b63650b0a0fbd19555c26c63c234ec231`. Its 1920 by 1224 layout contains reduced, uncropped copies of separately preserved native stills and labels itself as a prototype. The accompanying JSON records all input hashes. The old root-level `model-contact-sheet.png` depicts the superseded baseline and is kept as private review history.

## Visual findings and next artistic work

Two assistants inspected the baseline native stills and identified a material dove silhouette problem. The bounded v2 correction narrowed and lengthened the torso, reduced the head, exposed the neck and beak, introduced small painted eye points, dimmed inner feather contours and chose a three-quarter camera. A further native perched check caught flat feather planes standing away from the body; the folded wing base now rotates down the flank while preserving the tested bone lengths and foot contacts. The fully open glide remains unchanged by that fold correction.

An independent second assistant inspected the actual v2 native still and confirmed that it reads immediately as a bird. The remaining concern was the translucent, patterned overlap at the wing/body junction and a subtle tail. The pack demonstrates attached three-dimensional surfaces, repeatable motion, readable color variants and basic event contacts. The following limits remain visible and are not hidden behind the technical checks.

- **Dove anatomy.** The new three-quarter profile separates the head, neck and beak from the body. It remains a stylized point surface with visible regular sampling, simple ellipsoid anatomy and overlapping feather light. Wing silhouettes and the final folded contour still need a closer artistic pass before a large hero portrait. It is not a validated anatomical or aerodynamic model.
- **Flight staging.** The two bare angular branch forms are deliberate launch and landing supports for the foot-contact proof. They need an authored plant, shore or architectural context in a real song. The curve is expressive procedural motion, not an aerodynamic simulation or a complete flock system.
- **Rose identity.** The three palettes and attached leaves read clearly, but the repeated narrow petal loops and bright centre still resemble tiered lace flowers more than a distinctive rose. A stronger spiral, broader overlapping petals, less repetitive edges and improved inner contrast are the next modeling work. The current code should not be represented as a botanically accurate rose.
- **Wheat detail.** This is the most immediately recognizable family at middle and distant scale. Closely spaced glowing heads, similar upright proportions and straight stick-like leaves remain synthetic. Hero use needs more varied curvature, broader leaves and less overlapping head brightness.

The recommended use at this stage is a reviewable model prototype and an animation/contact example. Integrating any family into a complete song needs its own art direction, exact audio cues, native close-up and motion review, followed by owner approval of that output.

## Motion proofs and source separation

The current visual proof is `work/concert-addons/art-v2/dove-flight-v2-6s-1080p60.mp4`, rendered from source `b5f44f3626d1bf6685dbe24cbf1e20b3bc31759e99d9983b28a2beba0d4710f2`.

- **Movie SHA256:** `d213912ae9321b5bb43cc941eb570ece9f369ca605647b901bedeb7f598835a7`.
- **Exact size:** 1,211,878 bytes.
- **Decoded delivery:** 1920 by 1080, 60/1 fps, 360 unique frames, 6.000 seconds.
- **Timing:** first PTS 0.000000, last PTS 5.983333; all 359 intervals equal 1/60 second within the reported timestamp precision.
- **Color:** limited range, BT.709 matrix, BT.709 primaries and BT.709 transfer tag. The established display curve is preserved; there is no second transfer conversion.
- **Full decode:** no errors. The actual source map still matches both the freeze and render receipt.
- **Runtime:** 434.182 seconds, with renderer peak resident set 479,148 KiB, about 468 MiB, while the main production study also used the cloud machine.

The proof is silent and makes no audio-synchronization claim. Its complete machine record is `dove-flight-v2-6s-1080p60-qa.json` beside the movie. The full decoded-frame MD5 list is also retained. A decoded frame at 2.8 seconds was compared with the separately rendered native PNG: full-frame RGB8 RMSE was 1.305 values and PSNR was 45.82 dB after the lossy H.264 encode.

Fourteen decoded native frames were extracted across preparation, release, wing beats, glide, approach, touchdown and the settled ending. The assistant inspected those actual decoded frames in the cropped `decoded-motion-contact-sheet.png`; uncropped native decoded PNGs remain in `decoded-motion/`. This is sampled visual inspection plus full technical decoding, not a claim that every frame received an independent aesthetic review. The preparation view still overlaps the rose with the bird's head in projection, and the bare contact branches still need a designed environment. Those staging limits remain part of this prototype.

The earlier baseline movie remains `work/concert-addons/dove-flight-6s-1080p60.mp4`, SHA256 `c548f4030416023815a44e862f2ffe30b10e4f11d755ee47d39a7718c4bbd810`, tied only to source `96254c1535a952629efde164f3fb254a826649ba3b520ba6594369c0db598d36`. It rendered in 346.268 seconds with peak resident set 478,952 KiB. Its full decode passed with 360 unique frames, 1920 by 1080 pixels, 60/1 fps, 6.000 seconds, strictly advancing 1/60-second timestamps, limited range and all BT.709 color tags. This preserves a working rig reference while keeping the superseded visual design out of the current presentation.
