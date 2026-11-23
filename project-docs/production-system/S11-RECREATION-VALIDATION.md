# Song 11 recreation: validation evidence

Recorded November 23, 2026 UTC. **Pre-master checks are complete; final encoded
master, complete decode and audio QA remain pending.** This is a new recreation
for owner review. Approval of the earlier beauty study does not approve this film.

Scope and reproduction: [creative direction](S11-RECREATION.md) and
[executable workflow](../../tools/s11_renewed/README.md). Evidence paths under
`work/` identify production files, not files included in a clean Git checkout.
The measured results are summarized here; retain the receipts with delivery.

## Source and audio identity

| Item | Verified identity or intended clock |
| --- | --- |
| Baseline commit | `e8022e51ae859a683b83ce24d5ae3810a4c5488d` |
| New branch and implementation | `creative/s11-renewed-20261122`; `tools/s11_renewed` |
| Existing full-song source | `tools/s11_full2`; project title **Almighty God Who Knows the Future** |
| Engine pin | `d928ff9eafe02ac3150f0c646bdcc497fe5a7278` |
| People/words pin | `f43f4514e4bc42dc25166e90160d98219f5a0db4` |
| Original recording | Drive `108zDtdB4X189DOwsZn-K9p548nERubLG`; 9,073,677 bytes |
| Original MP3 SHA256 | `70464dff370f7187d12029970c1fa1ef3e91c6957180aa685b64cead830f7004` |
| Prepared score SHA256 | `fa488e4805cdc43b1f0f38915d67044ef92a9e659a59ac916d4b75b4cbb6d29b` |
| Film clock | Source audio 0-260 seconds, final 0.05-second fade, 15-second silent hold; 275 seconds total |
| Intended master | Native 1920 x 1080, 60 fps, two temporal samples, 16,500 frames; 0.1-second picture delay applied once |

The MP3 and prepared WAV hashes above were recomputed from the actual files.
Preparation provenance is `work/s11_full2/provenance.json`. The recovered source,
verified recording and saved approved 30-second beauty study informed the work;
the historical complete draft movie was not available for direct comparison.

## Completed visual review

Nineteen 960 x 540 first-pass stills were inspected across the complete story:
12, 28, 45, 58, 70, 86, 99, 105.7, 118.8, 123.2, 140, 155, 167, 186, 205,
221, 240, 250 and 260 seconds. The files and timing receipt are in
`work/s11_renewed/renewed-stills/`.

This review covered the Earth, Zion progression, church architecture, procession,
orchestra, conductor, words and closing event card. It found three specific
composition issues, followed by targeted native 1920 x 1080 verification:

| Time | Fix and actual rendered finding |
| --- | --- |
| 58.0 | Crown moved below both phrase lines. Clear sky separates the words from the crown; the church remains visible. |
| 105.7 and 186.0 | Reduced stage effects allow blue performers, gold instruments and bows to read across the ensemble. Local white-purple flares still overlap a few lower-left players. |
| 205.0 | Sunrise moved to the upper-right, away from the phrase and church center. Words are readable; church linework and dark terrace faces remain visible. Broad pale bloom remains during this bright climax. |
| 118.8 | Native costume check shows the full conductor in a separate, closed blue coat with gold trim and covered pelvis/legs. No nipples, breast/chest sculpting or buttock detail was observed. |

The initial targeted pictures are in `targeted-native/`; corrected optimization
pictures are in `targeted-native-v2/`, both under `work/s11_renewed/`.
The v2 images at 58, 205 and 118.8 were independently re-inspected. These specific
fixes were considered suitable to freeze for rendering. This does not certify
every frame or eliminate all highlight clipping.

## Camera and performance checks

- Camera validation found 70 contiguous shot blocks and 490 finite sampled
  camera states. The original camera object and phrase list/times were retained.
  Repeated installation was idempotent. Twenty-four selected paths were newly
  authored; no random global offset was used.
- The documented early joint cut was corrected from 74.56 to 74.70 seconds in
  the coupled runtime edit/shot boundaries. Musical and phrase cues were unchanged.
- Projected conductor envelopes stayed inside the intended hero views. The final
  crown correction was checked at 54.2, 55.8, 57, 58 and 58.39 seconds: crown
  bounds were approximately y303-367 and church bounds y396-528 on a 540-pixel
  frame. Native pictures subsequently confirmed the intended separation.
- `performance-check.json` records 897 samples across four conductor windows.
  Maximum ankle displacement was about `2.8e-17 m`, grip error `1.3e-7 m`, and
  baton length error `1.4e-14 m`. Its clothing receipt identifies an independent
  closed long coat and confirms that underlying torso/seat surfaces are not drawn.
- `trail-grid-check.json` records five history windows using 120 Hz history and
  a 240 Hz raw score. Maximum sampled history error was `0.000336 m`; current
  tip, grip and launch-anchor errors were zero. The checked strings transition
  had a maximum tip step of `0.003498 m` at 480 Hz.

Mechanical checks support planted feet and prop attachment. They do not establish
natural acting, graceful motion or owner approval. Stills cannot assess fluidity.
The conducting is authored animation; musical features are band/onset estimates,
not isolated instrument stems or newly captured human motion.

## Runtime verification

`work/s11_renewed/environment.json` records Python 3.12.14, FFmpeg 7.1.5 and
software llvmpipe rendering. No native GPU was used for these checks.

The first visibility optimization comparison had mismatches and was superseded.
`targeted-native-v2/visibility-comparison.json` records byte-identical optimized
and reference images at all five tested times: 58, 105.7, 186, 205 and 118.8.
That is sampled picture equivalence, not proof of whole-film equivalence.

These development checks retain their own evidence scope. The assembled master
must be bound to its own frozen source/input manifest and output checksum.

## Pending final delivery QA

- **Pending:** completed master filename, byte count, SHA256, frozen source/input
  fingerprint, exact runtime, chunk receipts and saved delivery identity.
- **Pending:** full-file decode; confirmed native dimensions, 60 fps cadence,
  16,500 frames, presentation timestamps and 275-second duration.
- **Pending:** encoded review of every shot, cut, chunk join, word entrance/exit,
  conductor gesture, modest costume view and closing hold; moving review of
  foot contact, baton contact, garment motion and camera acceleration.
- **Pending:** final encoded audio duration, original timing/alignment, picture
  delay, peaks/clipping, end fade and 15-second silent hold.
- **Pending:** exact-output owner creative review. Technical checks do not supply it.

Complete these entries with observed results and receipt paths after assembly;
do not infer completion from a render command, a still or an earlier film.
