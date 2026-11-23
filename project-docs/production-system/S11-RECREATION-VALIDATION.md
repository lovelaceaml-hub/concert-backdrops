# Song 11 recreation: validation evidence

Recorded November 23, 2026 UTC. **The complete film and its delivery copies are checked and saved.** This is a new recreation
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

## Completed final delivery QA

The exact final identities and saved links are in
[the delivery record](evidence/s11-renewed-final-delivery.json). The original
native master is 911,865,528 bytes, SHA256
`c553b2a51f3917d389adc51ee6dc97c96e6b6e9e306a9bfd2bfbe38a89b34c55`.
Its exact bytes are preserved in two verified ZIP archives. The full-HD
delivery and 720p review copy have separate encoded identities.

- All three complete files passed full video/audio decoding, 275-second duration,
  16,500-frame count, 60 fps cadence, color and presentation timestamp checks.
- Three original-score windows have zero measured sample lag at 8 kHz and
  correlation above 0.9999. The closing hold decodes to silence.
- A 1 dB audio-only gain adjustment was encoded directly from the unchanged
  prepared score. The final decoded stereo sample peaks are 0.940574 and
  0.928012, with no samples at or above full scale. These are sample peaks,
  not oversampled true peaks. All picture packet hashes and timestamps remain
  identical to the visually reviewed assembled master.
- All 311 selected assembled-master story frames were visually reviewed,
  including every edit, shot middle, all 39 render joins and selected ending
  compositions. All 20 cross-host joins additionally received 12 consecutive
  frame reviews, totaling 240 unique boundary frames.
- The complete 117.1–123.1-second conducting gesture received 61 native crops
  at 10 fps, alongside dense shorter motion intervals. No within-shot lurch,
  detached baton, foot slide or unwanted anatomical detail was observed.
- Strong authored light cues can temporarily reduce fine detail. A small roof
  touches the lower edge of the phrase near 165.8 seconds, and a light ribbon
  crosses part of “love” at 187.2 seconds; both phrases remain readable.

[The final QA receipt](evidence/s11-renewed-final-qa.json) binds the complete
scope and supporting evidence. Sampled visual review is not uninterrupted
playback. Exact-output owner creative approval remains unrecorded.

## Completed native encoded motion proof

The internal 6-second passage at picture seconds 117.1–123.1 is complete. It contains 360 frames at native 1920×1080 and 60fps with two temporal samples. The exact file SHA256 is `daa1aed1bb9e489425867678d2e027e0a26f328b4dee0fb98e4729e29a2ce440`. Complete video/audio decoding passed; all presentation timestamps are continuous. The decoded AAC and original prepared score had zero measured sample lag in all three sampled windows at 8 kHz, with correlation at least 0.999978. See [the encoded receipt](evidence/s11-renewed-motion-proof.json).

Two independent consecutive-frame inspections covered the repaired musical transition. The wider inspection viewed all 36 frames 7260–7295: hands, baton and torso advance gradually within each shot, feet remain planted, and the coat/trousers maintain coverage. The large screen-space change at picture 121.4333 seconds is the planned camera cut and light cue. These are encoded-frame inspections, not uninterrupted real-time playback or owner approval. [The preflight record](evidence/s11-renewed-preflight.json) retains the scope and measurements.

The later complete master is recorded above; this six-second proof retains its separate development identity.

## Completed remote native probe

The GitHub probe run `45106842150` completed successfully from commit `8a2ddad71eba2a8c85b49484acd554ead39484a9`. Exact dependencies, pinned models/fonts and all 343 picture-source identities passed restoration and validation. The encrypted artifact was authenticated and inspected at 58, 105.7, 118.8, 186 and 205 seconds; the final composition and modesty fixes remain visible. Root and independent visual inspection found no new blocker in these frames.

The remote runtime differs from the local Mesa runtime. The movie uses the complete remote request and does not mix local fallback pictures into it. The full request uses two Mesa threads per worker, following the verified local setting; the remote probe used one. [The native-probe record](evidence/s11-cloud-native-probe.json) preserves the actual runtime, source identity, frame hashes and review scope. The later full encoded-film results are recorded above.

## Reviewed hosted-worker metadata variation

Full run `45108198761` is bound to producing commit `eec8d16519ea82309ef851975792e9dfc548da03`. Its hosted workers exposed two exact full fingerprints, differing only in GitHub image version and kernel/platform labels. The recorded source, request, Python dependencies, Mesa packages, encoder version, sample count and thread controls match. Existing logs from both host types report `llvmpipe (LLVM 20.1.2, 256 bits)`.

The original strict assembler remains unchanged. A separate, narrowly scoped [reviewed assembler](../../tools/s11_delivery/README.md) checks both original fingerprints against [the persisted per-request policy](evidence/s11-host-cohort-policy.json), reads frozen inputs from the producing commit, and retains each part's exact identity. Unknown fingerprints, changed dependencies or changed source remain rejected. Its 16 acceptance tests passed. [The independent review](evidence/s11-host-cohort-review.md) documents the evidence and remaining limits; cross-host pixel identity is not claimed.

Assembly permission is only for completing final QA. The later final QA record above resolves the required joins, complete decode, timestamps, original audio and sampled visual checks. The historical policy remains unchanged.
