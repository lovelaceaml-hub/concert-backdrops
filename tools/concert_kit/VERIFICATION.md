# Consideration proof: recorded verification

This record separates evidence that exists from work still in progress. The twelve-model atlas, final native key frames and a one-second native motion benchmark have been rendered and inspected. The complete eighteen-second master is being rendered through the registered production pipeline; this document does not yet claim its completion, continuous playback review or final approval.

## Frozen picture identity

The final picture source identity is `2fa9e0fce212be765d639fbb85acf8cdb755e5a92d995dae418fa66fbd7eae6e`, calculated from the sorted compact JSON returned by `render.source_hashes()`. It covers 190 source, body-asset and font entries. The complete manifest is `work/concert-kit/render-freeze.json`. Documentation, derived caches and separately prepared audio are not picture source entries.

The body asset is `assets/p3d/body_v1.npz`, SHA-256 `0a72159f84b7008dcb135c79f82ae3b05df5f7361197e99ab9ca4af148c91189`. Both paired motion arrays contain 196 poses at 30 Hz, giving a 6.5-second interval from first to last pose. Sixty-fps delivery evaluates interpolated bone motion at sixty different times per second. It does not turn the source into a sixty-Hz capture.

The source identity was checked again after the final atlas and stills. Production `engine/` and the committed body asset were not modified by this kit. See [MODEL-CATALOG.md](MODEL-CATALOG.md) for geometry, motion, font and campaign provenance.

## Model verification

All twelve named variants were rendered individually at 960x540. Their labeled overview is `work/concert-kit/atlas/model-atlas.jpg`, 1920x1200; individual pictures and `atlas-manifest.json` are in the same folder. The atlas manifest matches the final picture source exactly.

The atlas exposed an actual cup-lantern defect: its upper rim did not meet its shortened ribs. The rim now uses the same terminal height and radius as the ribs. The corrected native image was inspected after regeneration. The paths intentionally emit less light than the hero figures, so their atlas tiles are quiet. These are stylized motifs, not botanical or structural reconstructions.

A geometry-level check sampled every variant at 12.75 seconds, sought back to 2.1 seconds, and sampled 12.75 again. It also rebuilt each variant with the same seed. All twelve produced the same batch bytes for the same requested time, with finite numeric arrays. Each of the six builders rejected an invalid variant name. The result is recorded in `work/concert-kit/model-verification.json`.

Those checks establish the procedural builders' finite output and repeatability under random access. They do not prove that the entire renderer, cloth simulation, encoding, or artistic result is correct.

## Final native key frames

The final source was used for `work/concert-kit/stills-v04/t000.00.png`, `t011.00.png`, and `t017.50.png`. All are native 1920x1080 with two HDR shutter samples, not enlarged draft pictures.

| Picture time | Observed composition and pose |
| --- | --- |
| 0.0 seconds | The seated person, helper and shore establish the intended human scale; the corner carries only the existing logo. |
| 11.0 seconds | The pair has finished rising. Both are standing, the recipient's hand-to-chest response reads, and the faded seat recedes. Faces and hands have clearer background space than the first still pass. |
| 17.5 seconds | The completed pink garden, illuminated canopy and traveling ribbon form the payoff. The pair remains identifiable in the wider world. The canonical Consideration label and phrase are legible and clear of the figures. |

An independent reviewer inspected these frames and the three decoded contact frames described below. No visual blocker was identified in those sampled pictures. This was a composition and pose review, not a claim of real-time playback or final-film approval. Some vegetation can still be seen through the emitted-point bodies, particularly around the left figure's outline; the image style remains translucent.

The final still process initialized in 7.794 seconds. Its measured frame times were 6.531 seconds at 0.0, 53.900 seconds at 11.0, and 20.846 seconds at 17.5, including any required simulation warmup. Total process time was 93.464 seconds. Peak resident memory was 832,468 KiB, about 813 MiB. Another production render shared the machine, so these are observed timings, not a dedicated-machine benchmark.

## Contact and movement evidence

The original retargeted capture had a palm-center gap of roughly 0.1 to 0.27 m during parts of the shared effort. The isolated shared-target overlay reduced the sampled held-contact gaps as follows:

| Scene time | Palm-center distance |
| --- | --- |
| 5.3 seconds | 6.326 mm |
| 6.0 seconds | 10.778 mm |
| 6.5 seconds | 8.822 mm |
| 7.0 seconds | 3.522 mm |

Approach at 4.8 seconds remains 116.188 mm apart; release at 7.5 seconds is 89.057 mm; separation at 8.0 seconds is 826.894 mm. These values are consistent with contact being temporary. The raw evidence is `work/concert-kit/stills-v04/contact-evidence.json`.

The internal native benchmark is `work/concert-kit/pilot/contact-1s-1080p60.mp4`, covering scene times 6.0 to just before 7.0. Its SHA-256 is `57127069036d88fc80904f257bb6b945c7b4ae749bfd286aab571cc9ef3eed44`. This benchmark predates only the tiny cup-lantern rim correction; `models.py` is its sole source difference from the final freeze. It contains no sound and is not the full proof delivery.

Decoded frames at 6.000, 6.500 and 6.9833 seconds are in `work/concert-kit/pilot/qa/contact-01.png`, `contact-02.png` and `contact-03.png`. They were extracted using inverse BT.709 matrix and range conversion only, without an extra transfer conversion. They show the shared grip, the recipient leaning forward and rising, and the helper changing stance. Warm gold figures separate well from the dark lake, and plants leave the hands readable. The blue seat remains more conspicuous during the actual rise than in the settled ending.

Palm distance does not establish interlocked fingers, realistic muscle force, or good acting. The full motion still needs review across offer, grip, rise, release, the authored 1.2-second standing settle, and the two camera cuts. The settle follows the complete capture and is new scene work; it is not recorded performance from CMU.

Later dense review of the actual production frames identified a material creative
limitation: the two gold silhouettes overlap heavily around 7.2 to 8.1 seconds,
obscuring part of the release. This is an unfinished hero-shot issue, not a
technical pass or proof of a physical collision. A smaller foot/shin overlap
around 5.0 to 5.6 seconds clears in projection by 6.0. The held hand remains
readable from approximately 5.3 through 7.0. An isolated camera planning review
tests alternative views at 7.5 seconds without changing this frozen movie.
Its promising single-frame results still require complete shot and transition
review before becoming a new production version.

## Native render cost and delivery checks

The one-second benchmark decoded to exactly 60 frames, 1920x1080, at 60/1 fps, with duration 1.000 seconds and YUV420P output. It used llvmpipe LLVM 19.1.7 with one software graphics thread and two HDR samples. Initialization took 6.101 seconds, and total elapsed time was 184.336 seconds. The first frame completed at 33.84 seconds including warmup; subsequent frames averaged approximately 2.55 seconds each. This suggested roughly 45 minutes for 1080 frames on one comparable worker, before additional shared-machine effects.

The direct benchmark encoder reports limited range and BT.709 matrix, but its inspected stream did not report the primaries or transfer fields. It is therefore not evidence that the complete delivery color-tag requirement passed. The registered `p3d-kit` pipeline is used for the final master; its independent verification must check primaries, transfer, matrix and range, exact frame count and clock, joins, audio timing and decoded peak, and source identity.

The chosen sound is the original Song 07 interval 137.5 to 155.5 seconds, with no time stretch. The prepared canonical eighteen-second WAV has SHA-256 `0f43061d674dae3467a6a76867f8599d241532c131e7e7654502bc29f2d66f7b`. Its gain is reduced by 1 dB, with an 0.08-second entry fade and 0.35-second exit fade. Audio preparation and the private source manifest belong to the production package. The relative 11.5-second build cue is informed by the existing song timeline, not claimed as an ear-verified transient.

Native 4K frame dimensions are supported by the adapter. No complete 4K movie from this kit has been rendered or accepted. Native size, frame count and checksums establish delivery facts; the actual action, composition, restraint and emotional resolution remain artistic review questions.
