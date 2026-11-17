# Revision 3 validation

Owner approved the delivered video on 2026-11-16 and requested preservation, documentation and upload. The approved source is `46df53b98a43f58e51a78d40ee5794108a68e13c`, archived by tag `film10-revision3-approved-2026-11-16`. Subsequent approval-documentation commits do not change the video or its checksums. PR #71 remains draft and unmerged.

## Provenance and scope

Film 10 render 1 remains the base: d928ff9eafe02ac3150f0c646bdcc497fe5a7278, run 43726203825. The targeted reference is Claude Nine Colours Final v1, f43f4514e4bc42dc25166e90160d98219f5a0db4, run 43855882765, share artifact 14222872749. The actual share video was downloaded and inspected, including the typography, Respect pair and finale motion.

All 82 original-engine Python files and all 108 Claude-reference Python files in the private snapshots match their Git blobs. The new source is isolated under tools/nine_colours_minor. No protected or shared source was edited. No paid service, workflow dispatch or merge occurred.

The owner requested a creative revision, so these outputs intentionally change pixels. The reference typography and body/symbol components run through the original renderer; this is not a claim that the whole film matches Claude's encoded pixels. The rest of the original people, fast aerial flight and musical joins remain. Respect's original chapter cuts remain; the new continuous camera join is specifically the spiral-to-Earth transition.

## Raw-frame checks

All 28 sampled 1920x1080 frames are pixel-identical in separate fresh processes rendering forward and reverse. Final-clock samples:

`0, 6.3, 7.2, 8, 10, 16, 21, 24.5, 29, 34.5, 38, 40, 41.5, 43, 44.5, 46.3, 49, 54.5, 54.75, 55.46, 55.48, 55.8, 56.4, 57.2, 57.8, 58.4, 59, 65.98`.

The original-to-new camera join at final 55.47 s has a 0.01244 m position step and 0.00253 degree viewing-direction step across 0.0002 seconds, consistent with continuing motion. Earth's projected center remains inside x=0.4996..0.5002, y=0.4997..0.5283 during the new arc. The initial close pass intentionally brings some orbiting symbols near the frame edge before the full orbit settles into view.

The opening layout is unchanged. Raw frames at 0 and 6.3 s exactly match Revision 2. At 7.2 s the light path has started responding to the updated Greeting pen, so that frame differs. The card timing remains the same.

## Picture review

Full-resolution stills cover the opening, every expression, Respect, Earth formation, world-to-logo and final card. A dense finale strip was inspected during development. This caught and corrected an Earth framing dip and the original renderer's large triangular ribbon shapes where a segment straddled the camera lens. Near-lens segments now fade in the revised finale while the rest of the ribbon path continues.

The near-lens correction itself is eased over 0.8 seconds. At the previously hard switch, adjacent-frame RGB differences on a 960x540 review fell from 49.72 then 13.31 to 19.65 then 18.87. This removes the isolated brightness pop rather than claiming the original fast flight has been slowed.

The two Respect figures use the exact reference models, garments, hair, seed values and refined offer/listen gestures. They remain whole. The nine phrases use the reference's cream serif treatment, colored capsule labels, screen-facing placement and clean departures. Small timing corrections prevent consecutive phrases from overlapping. Comets and hoops dim within phrase bounds, including segments with endpoints outside a word box.

Respect's light thread now follows the reference's higher path and softens during the reading interval, keeping it above the faces and listening gesture. The affected production parts were replaced in full after this final adjustment. Earlier partial encodes are private rejected drafts and are excluded from delivery.

## Soundtrack

The 66-second PCM score is byte-identical to Revision 2: SHA-256 `524f0d14abafd517335c87049e59a2538c0b560cf04b26828463707790c31d6e`. It is the approved lead-in medley with four additional seconds of opening silence. The original final musical accent and release are retained. No generated music or paid audio service was used.

## Encoded delivery

Both exports pass `verify.py`. Each has exactly 3,960 frames, video and audio duration 66.000 s, 60/1 frame rate, stereo 48 kHz audio, and zero consecutive duplicate frames. Every video timestamp advances by 1/60 s, within 0.000000667 s of container rounding. Both files have the MP4 metadata before media data for progressive playback.

| Measurement | Master | Phone |
|---|---|---|
| Resolution | 1920x1080 | 1280x720 |
| File bytes | 94,541,396 | 22,278,585 |
| Audio sample peak | -2.682 dBFS | -2.317 dBFS |
| Final accent RMS, 63.5 to 64.7 s | -13.670 dBFS | -13.759 dBFS |
| Final quarter-second RMS | -49.349 dBFS | -49.329 dBFS |
| Last 10 ms peak | -92.949 dBFS | -92.080 dBFS |

The master measures -12.94 LUFS integrated and -2.68 dBTP true peak. The score deliberately retains the approved final accent: its last full second is -23.09 dBFS RMS, followed by the quiet release. It does not meet the older masterpiece brief's quiet-last-second policy, which would remove that requested accent. Five original medley joins retain quarter-second level changes above 3 dB; the largest is 5.67 dB near 46.21 s. They are reported, not silently remixed. These are objective measurements, not a claim of a human listening review.

The full encoded timeline was inspected at 2 fps, Respect at 10 fps, Earth formation and its orbit at 15 fps, and the closing-card transition at 10 fps. Selected encoded frames were inspected at native 1080p and 720p. The new globe remains visible through the approach; orbiting symbols pass in front of and behind it. The Respect light clears the faces and the hand gesture. Original pre-finale flight remains energetic: the largest half-second motion/jitter interval is 54.0 s, in the retained spiral flight. The automatic motion report is a review aid, not a claim that every original whip has been redesigned.

All seven main render-part boundaries have frame differences within 1.41 times their surrounding median. The two additional corrected-Respect chunk boundaries at frames 2227 and 2722 have ratios 1.057 and 1.021. The closing card keeps moving through the last frame; there are no repeated-frame freezes.

## Delivery links and integrity

- [Phone 720p60](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view)
- [Master 1080p60](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view)

Both uploads are in the designated video folder `1oNl_-SVqTwrYzqT87JQ3Om9HQFrcMOkz`, and Drive reports the expected names and byte counts. The phone file was downloaded back from Drive for the chat attachment; its SHA-256 exactly matches the local deliverable.

| File | SHA-256 |
|---|---|
| Master | `508c5518bced94b21f96e8727d2b7ffd0da0ee69de9da164e7e5e824e80eda7b` |
| Phone, local and Drive download | `ad4b4e7fe861ae34eb80e8b921ee747efc477c08bb89ec981f1b588a0b3c0af5` |

Private evidence is under work/nine_colours_revision3: source-check.json, fidelity-report.json, finale-continuity.json, opening-preserved.json, encoded-qa.json, additional-part-joins.json, drive-roundtrip.json, the source-transition audit records, and the raw/encoded review frames. The final 344-file render manifest matches every current input. Earlier draft parts were replaced only where the two final fixes can affect the timeline; those time bounds are recorded in the source-transition audit. No frames, videos or caches are committed.
