# Consideration revision: recorded verification

The registered fifteen-second movie has completed from frozen source and passed the independent technical audit. This record includes numerical checks, native probes, and sampled review of the actual encoded action, cuts and ending. These checks do not establish owner approval.

## Exact scope and identity

The revision maps output frames 0 through 899 to original Consideration scene frames 180 through 1079. Both clocks run at 60 fps. Output duration is 15 seconds; the original scene interval is 3 to 18 seconds. The registered project is `concert-kit-consideration-v2`, using the existing `p3d-kit` scheduler and the new wrapper `tools/concert_motion_revision/render.py`.

The original kit remains pinned to `2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e`. Its engine, body asset, models, paired capture, right-hand contact and original eighteen-second scene source are unchanged. The revision changes one renderer instance's cameras and one actor instance's left-hand response. It does not claim new motion capture, physical simulation of a shared load, or new human geometry.

The frozen wrapper manifest contains 194 entries, with identity `8b091b1940221a8f21a4bd2f8a7ab0cdd1510a90ea559c6ded9afdaf0f5e8876`. It is saved in `work/concert-motion-revision/freeze.json`. The independent auditor's complete registered input mapping contains 202 entries, identity `34bcaa95787e030d817f96d0280bf721545397ca04aa60ab97e2373bb894f46a`. These cover different declared scopes and should not be confused. The source checkpoint is commit `33a7d87e2848bf8a42e6d8132c34544d61259350`.

A fresh-checkout audit found that ordinary deterministic conversion produced different font-header timestamps despite matching glyph data. The bounded setup repair reconstructs all 74 historical TTF files exactly from pinned WOFF2 inputs and recorded header metadata. It leaves the active fonts and the scene guard unchanged. Use `python3 scripts/bootstrap.py --p3d-only --reference-fonts`; see [REFERENCE-FONTS.md](../../docs/REFERENCE-FONTS.md). The setup checkpoint is `3aaa7c5d75a01704c984b60c33cfc2a0bb807b5f`. This is exact dependency reconstruction, not acceptance of a different font set under an old fingerprint.

An independent detached checkout then reconstructed its own exact fonts and derived caches, rendered registered native output frame 0, and matched the primary PNG byte-for-byte and pixel-for-pixel. All 202 registered inputs and the receipt fingerprint matched. The test reused the locked Python environment, host FFmpeg/Mesa and pinned WOFF2 inputs; it did not reinstall an entire machine or render a second complete movie. The durable receipt is `project-docs/production-system/evidence/fresh-checkout-reference.json`.

## What was wrong with the hand

Dense review of the original production PNGs identified a sharp excursion during the return from the chest. Between original frames 691 and 692, at 11.5167 and 11.5333 seconds, the palm rose beside the face. This was an actual change in the posed arm, rather than a camera crossing or a bright particle mistaken for the hand.

An independent numerical check used the actual original and revised actor skeletons. Only the unused surface point count was reduced, to avoid constructing large clouds for a bone-position check. Disabling the living-wrist layer left the elbow and wrist discontinuities essentially unchanged. This isolated the defect to the gesture posing path, rather than subtle finger motion or the original captured rise.

The original gesture feeds a fractional weight into repeated endpoint corrections. The actor then combines bone groups evaluated at different lead and lag weights. The revised instance solves a complete hand-on-heart endpoint and blends complete poses with an explicit quintic envelope. The test establishes that this alternative removes the observed jump; it does not independently attribute every part of the old defect to one individual engine statement.

### Actual release measurements

These values cover original time 11.5 to 12.4 seconds, sampled at 60 Hz, with living hands enabled:

| Measure | Original response | Revised response |
| --- | ---: | ---: |
| Largest palm movement between adjacent frames | 0.343610 m | 0.023870 m |
| Largest elbow movement between adjacent frames | 0.216608 m | 0.008667 m |
| Largest wrist movement between adjacent frames | 0.314787 m | 0.019358 m |
| Largest discrete palm acceleration | 1537.601 m/s2 | 9.437 m/s2 |

The 120 Hz check corroborated the improvement between output samples. Across the complete revised arrival, hold and return from 9.3 to 12.5 seconds, the largest 60 Hz palm step was about 0.02763 m, during arrival. Eight sampled right-hand contact positions before the new gesture began were unchanged exactly. Repeated palm evaluations after seeking to other times were bit-identical. A second attempt to install the response into the same actor instance correctly rejected the duplicate operation.

The detailed independent evidence is `project-docs/production-system/evidence/consideration-v2-response-continuity.json`. A compact release comparison is saved at `work/concert-motion-revision/numeric-summary.json`. These are continuity measurements, not measurements of force, muscle behavior or emotional naturalness.

## Camera coverage and native images

The initial attempt to use a western view throughout the excerpt placed the standing helper behind the seated person at original time 3 seconds. That view was rejected before a full render. The selected treatment preserves the original front contact shot, cuts to the western view as the recipient rises, then reveals the garden from the same side.

| Output interval | Original scene interval | Purpose |
| --- | --- | --- |
| 0 to 3.9 seconds | 3 to 6.9 seconds | Preserve the clear approach and shared grip. |
| 3.9 to 9 seconds | 6.9 to 12 seconds | Separate the bodies during rise and release, then show the chest response. |
| 9 to 15 seconds | 12 to 18 seconds | Reveal the complete garden, light path and closing expression. |

The helper remains on the same side of the recipient across the new cut. At source time 7.5, the measured horizontal head separation increases from about 59 pixels in the original camera to 177 pixels in the revision. The camera moves farther west during the settlement so the two standing figures continue to separate. These center distances supplement the images; they do not substitute for a complete silhouette review.

An independent check sampled all 55 frames from source 7.2 through 8.1 seconds. Minimum horizontal head separation was 173.04 pixels, and minimum pelvis separation was 236.12 pixels at native 1080p. The helper stayed screen-right throughout, and all sampled anchors remained in front of the camera. The receipt is `work/concert-motion-review/projected-separation-7p2-8p1.json`. This checks projected anchors, not every surface silhouette or prop occlusion. A separate sampled review of 19 actual production PNGs, every three frames across this interval, confirmed distinct heads and torsos, consistent left/right geography, progressive hand release, and feet inside the picture. Output frame 270 matched the previously reviewed native source-frame-450 probe byte-for-byte. Plants remained visible through the left figure. The sampled PNG evidence is `work/concert-motion-revision/source-review/rise-source-temporal.jpg` with a per-frame hash receipt beside it; encoded motion review is recorded below.

Eleven native 1920x1080 probes in `work/concert-motion-revision/probes-v02` covered the approach, grip, both sides of the 6.9-second cut, rise, settlement, former hand defect, both sides of the 12-second cut, and ending. They used two temporal samples. This pass took 102.196 seconds including initialization and skipped-time simulation warmup. The rise and response were readable, with hands, heads and feet inside the picture. The inherited small foot/shin overlap around 5.3 seconds remained visible.

The ending probe exposed a new camera obstruction: a flower patch covered one person's head. The final camera endpoint moves farther west and stays lower. `probes-v03` confirms both heads clear, the full phrase readable, and the complete garden present at source 17.5. Flowers still overlap some lower-body regions in projection. The dense point style also allows plants behind people to remain visible through the bodies; this has not been presented as resolved.

The final native sequence was 11.5333, 12.3, 17.5, then 11.5333 seconds again. It took 77.718 seconds. The first and last source-frame-692 PNGs are byte-identical, SHA-256 `aa9799de1323152d041a74cf70d95dea2845d52fa197575a35f9f0edcd5a3f33`. At that former failure instant, the hand stays at the chest and the pink path starts from the actual palm position.

A later review used 29 actual production PNGs, every two frames from source 11.4 through 12.333 seconds, including unscaled hand/torso crops before the cut. The hand held at the chest and then lowered progressively, without the old excursion beside the face. The pink light left the palm as a deliberate world-space departure. The 12-second wide cut retained person ordering and continued light travel, without a visible mixture of camera views in one frame. Actual output frame 512 matched the final source-frame-692 probe byte-for-byte. Evidence is `work/concert-motion-revision/source-review/response-source-temporal.jpg`, `response-source-native-crops.jpg` and the per-frame receipt. This remains a sampled source-frame review, with encoded-film review separate.

After these probes, only the audio verifier's PCM decoding was corrected before the final freeze. No picture evaluation code changed. The registered native output frame 0 was then rendered from the final freeze and matched the direct source-frame-180 PNG exactly, with zero changed pixel channels. Its SHA-256 is `0ebe8ac843959fd842cab8a964cb251548270eb8924a059ddf43141a88dc9e40`. This checks the wrapper's output-to-source mapping on actual rendered media.

## Audio and final checks

The registered audio is the canonical eighteen-second Song 07 WAV, offset by three seconds at unchanged speed. The resulting original recording interval is 140.5 to 155.5 seconds. No new fade is added; the existing canonical ending fade remains. The canonical source is packed PCM24, not PCM16. The verifier's corrected signed 24-bit decoder was compared against FFmpeg float64 decoding over all 720,000 stereo sample frames of this crop and matched exactly.

The completed primary is `Consideration-Revised-15s-1080p60.mp4`, 29,912,818 bytes, SHA-256 `ab25085451f99ac8c674fa4e9bd03824d45747855707e5962e91fab7a6f8527f`. Its delivery copy is byte-identical to the registered `master.mp4`.

The independent audit passed with no errors or warnings. It decoded all 900 frames at 1920x1080, verified every presentation timestamp from 0 through 14.983333333 seconds, and confirmed 60/1 fps, a 15-second program, and BT.709 primaries, transfer, matrix and limited-range tags. All 202 frozen input hashes and the picture contract remained unchanged. Forty native-to-encoded comparisons had a maximum RGB mean absolute error of 1.789666 on the 0 to 255 scale and a minimum PSNR of 37.731902 dB. These detect encoding or identity problems; they are not beauty scores.

The AAC stream is 48 kHz stereo. Its logical program contains 720,000 samples per channel; the decoder's additional 896 tail-padding samples are identified separately. Three alignment windows matched the canonical crop at zero lag, with correlation at least 0.999768. The decoded peak was -1.0242 dBFS, with no samples at or above full scale. The unchanged independent report is `project-docs/production-system/evidence/consideration-v2-delivery-qa.json`.

## Actual encoded visual review

The separate artistic review extracted 67 unique native frames from the completed revision and two matching frames from the historical eighteen-second baseline. The decode inverted BT.709 matrix/range only, with no extra transfer conversion. Both source movies retained the same hashes before and after extraction.

| Review | Output frames | Original scene time | Observation |
| --- | --- | --- | --- |
| Rise and release | 252 to 306, every third frame | 7.2 to 8.1 seconds | Separate heads and torsos throughout the samples; progressive hand release and visible feet. |
| Hand return | 504 to 560, every second frame | 11.4 to 12.333 seconds | Chest hold followed by progressive lowering; the old face-side excursion is absent. Unscaled crops retain the hand detail before the wide cut. |
| Both cuts | Every frame 230 to 238 and 536 to 544 | Around 6.9 and 12 seconds | Person ordering, continuing action and light travel are coherent; no blank or mixed-camera frame is visible. |
| Garden and ending | 600, 690, 780, 840, 870, 899 | 13 to 17.983 seconds | The flowers and willow open along the light path; the complete expression and logo remain present, with both heads clear. |

The delivered comparison image, `Consideration-Motion-Before-After.png`, uses actual encoded baseline frame 450 beside revision frame 270 at the same original time 7.5 seconds, and baseline frame 692 beside revision frame 512 at 11.5333 seconds. It labels both original scene time and each movie's output time. All four native 1920x1080 frames are scaled equally to 960x540 panels. The 1920x1276 PNG is 2,268,796 bytes, SHA-256 `ed78ac05a88e612b54c1340d1bc05c2da83285a2e6940d3ad18a471a2b0043e4`.

The two targeted failures are visibly improved in this sampled encoded review. Plants still show through the luminous bodies, and a flower patch crosses the recipient's torso and some hand/lower-body area in the garden. The next composition pass should clear that plant region across the complete camera path. No new material blocker was observed in the reviewed samples. This review does not claim real-time playback, ear-verified musical hits, or owner approval of the acting. Frame mappings, media identities, observations and remaining issues are saved in `project-docs/production-system/evidence/consideration-v2-visual-review.json`.

## Completed native 4K ending check

The registered `4k-check` preset rendered output frame 870, corresponding to source time 17.5 seconds, at 3840x2160 with two temporal samples. It is RGB8, not an enlarged 1080p image or an HDR output. The delivered PNG is `Consideration-Revised-Garden-Native-4K.png`, SHA-256 `1ac66c796b1c9a732de252532eae90c9e55242a55033bd91cdd363cdb089422b`, 5,048,251 bytes.

The command completed in 76.311 seconds, including initialization and timeline warmup, while the main render shared the machine. Largest-child peak resident memory was 1,485,916 KiB. The source identity remained the final `8b091b19...` freeze. The independent native image review confirmed clear heads and legible complete title and logo; flowers still overlap one torso below the face. The detailed receipt and review are in `work/concert-motion-review/4k-native-qa.json`. This is one reviewed 4K still, not a completed 4K movie or owner approval.
