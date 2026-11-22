# Handoff for a new AI or chat

Copy the following instruction into a new working chat. The files it references carry the actual state; this prompt is an entry point, not a substitute for reading them.

> Work on the concert-backdrops project for The Words of Mother's Love. Read root AGENTS.md, project-docs/production-system/START-HERE.md and STATE.json. Finish the current Cinematic Ten render and delivery round before starting the older improvement queue. Its picture source is frozen at df4fc478116d3f0e34a85d2166097fbda55911bf, branch creative/cinematic-ten-films, PR #108. Preserve the approved 66-second Nine Colours Revision3 creative reference and the 30-second Song11 clarity reference. Use the ten explicit cinematic-ten-01 through cinematic-ten-10 projects, retain valid checkpoints, inspect native encoded output and save exact media identities. Films 01, 05, 06, 07, 08 and 09 are complete, technically passed, visually sampled and saved. Films 02, 03, 04 and 10 remain in production. No Cinematic Ten owner approval is recorded. Use cloud CPU workers and one coordinator for the bounded queue. Keep full songs, lyrics, frames and videos out of Git. Apply the current user's authorization without repeating permission questions. Report completed work and remaining work separately, with exact links and review limits.

## Current work: Cinematic Ten

Handoff date: November 21, 2026, America/Los_Angeles. The owner requested ten final cinematic quality films and rejected the earlier rough studies. The ten new registered projects each render twenty seconds at native 1920 x 1080, 60 fps, 1,200 frames and two temporal samples. Their native geometry covers solo fan dance, a five-person ensemble, globe-to-people transition, wrist-origin light writing, lantern processions, growing garden, articulated birds, ocean, kinetic orrery and a gathering. Use the project/title table in [START-HERE.md](START-HERE.md), [CINEMATIC-TEN-MOTION.md](CINEMATIC-TEN-MOTION.md), and the actual manifests under `projects/cinematic-ten-*`.

Frozen picture source: `df4fc478116d3f0e34a85d2166097fbda55911bf`. Integration: [PR #108](https://github.com/lovelaceaml-hub/concert-backdrops/pull/108), branch `creative/cinematic-ten-films`. Films 01, 05, 06, 07, 08 and 09 have complete final masters, passing pipeline and independent technical checks, and exact saved versions. Resolve their identities through [the delivery checkpoint](evidence/cinematic-ten-library-delivery.json) and their sampled visual findings through [the review checkpoint](evidence/cinematic-ten-final-review.json). Films 02, 03, 04 and 10 remain in production. These technical and sampled visual checks do not establish owner approval.

The working queue is `work/cinematic-ten/active-render-queue.json`. The nature lane (06, 08, 07) is finished; the remaining base lanes are 02 then 04, and 03 then 10. Most full jobs use two single-thread workers; film10 uses three with 50-frame chunks to balance its remaining work without changing the picture fingerprint. One extra film10 worker earlier exited -9; the pipeline preserved 47 verified frames. That bounded resume completed and preserved 197 frames. Further 50-frame single-worker blocks are running with an available-memory guard; they stop starting new blocks when film3 reaches 1,000 written frames. Check its actual receipt before another resume. Avoid adding another heavy character worker while memory is constrained. Do not duplicate a coordinator over an existing job. Final masters are `work/pipeline/cinematic-ten-XX/final/master.mp4`, with `master.json`, `qa.json` and checksummed frame receipts. The shared `run-receipt.json` is overwritten by each coordinator; per-film receipts and logs are authoritative.

Working saved-file identities are in `work/cinematic-ten/library-delivery.json`. They record actual completed saves, not the status of unfinished films. The coordinator must finish each remaining master, inspect the encoded pictures and boundaries, save the exact bytes, and update current state, delivery catalog and production log. No new picture edits are part of this frozen round, and owner approval remains unrecorded.

## Historical fan and silk increment, PR #106

The earlier `concert-fan-trio` has a twenty-second clock, distinct lead/answer/welcome roles and two held fans with finite silk. Picture source: `dffe8f165944c627ae39a8bb7d47bc5a9e703305`. Read [FAN-SILK-PERFORMANCE.md](FAN-SILK-PERFORMANCE.md) and [tools/concert_fan/README.md](../../tools/concert_fan/README.md). Only the first two reference posters were inspected for that increment; its missing-moving-footage note is historical. Preserve its completed delivery and review records.

## Read order and precedence

1. Current user directions and current session corrections.
2. Root `AGENTS.md` and this production system's current records.
3. Live Drive rules, latest dated addenda and per-song status. Historical comments can be stale; preserve them but resolve conflicts explicitly.
4. The exact approved media and immutable source records.
5. The selected song's original recording identity, continuity and known unrendered changes.
6. Implementation documentation for the chosen adapter and models.

Do not restart the old promo, regenerate approved art or re-open a completed repair because an old handoff says it is pending. The source catalog records that all eleven recordings exist. Several full-song delivery records refer to prior chats and have not been independently watched in this audit; do not claim those videos were visually verified just because their status pages were read.

Use [AUTHORING-NEXT-SONG.md](AUTHORING-NEXT-SONG.md) when moving from a study to a new complete song. The kit adapter now explicitly registers all ten Cinematic Ten scenes alongside the historical Consideration scene, its separate camera and response revision, the natural dance scene, and the original fan and silk trio. The approved Song 11 adapter remains separate; the two natural dance projects share one registration. Read `pipeline/kit.py` and the project manifests for the current inventory. A new audio source or a renamed project is not a new authored film. Prefer `concert-kit-consideration-v2` when studying the earlier corrected hand return and clearer rise; retain the original 18-second file as evidence of what needed repair.

## Reference intake and faithful adaptation

The older YouTube reference intake is retained in `catalogs/performance-references.json`. Its poster-only findings describe the earlier fan-trio round. Three actual supplied recordings have since been recovered and inspected: `ScreenRecording_11-21-2026 12-19-51_1.mp4` is the close solo fan reference, `ScreenRecording_11-21-2026 12-20-32_1.mp4` is the wider ensemble reference, and `ScreenRecording_11-21-2026 12-24-09_1.mp4` is the illuminated globe reference. [CINEMATIC-TEN-MOTION.md](CINEMATIC-TEN-MOTION.md) and the motion catalog record exact filenames, hashes and saved identities. The third recording is not a dance source. No specific calligraphy performance was demonstrated by these recordings.

The new solo, ensemble and calligraphy scores are original authored kinematics. Viewing the dance references informed the solo and ensemble upper-body sweeps, levels and timing; calligraphy was independently authored from its brief. No captured or reconstructed choreography was produced. Feet hidden by skirts were authored independently. Previous automatic covered-foot estimates were not verified by this round. The optional Blender performance exporter remains unimplemented.

The local-video intake utility in `tools/performance_reference/` preserves source hashes, requested ranges and actual decoded timestamps, then creates review samples and an annotation manifest. The earlier [sixteen-second treatment](REFERENCE-CREATIVE-TREATMENT.md) is planning history, superseded first by the implemented fan trio and now by the separate Cinematic Ten work. [PERFORMANCE-AUTHORING.md](PERFORMANCE-AUTHORING.md) remains the authoring contract. Keep [NEXT-PERFORMANCE-UPGRADES.md](NEXT-PERFORMANCE-UPGRADES.md) as later quality work after the current final delivery.

## Previous delivered work: natural dance, PR #104

That earlier dance picture is frozen at `0c42f4422a6b67464cb9cd84aac32008d45d4f4c`. Its full eighteen-second native 1080p60 movie is complete, saved and copied to Production Studies with verified raw bytes. Both technical auditors passed; targeted visual inspection found no confirmed blocker, while preserving the slow preparation and prolonged settling as creative issues. Owner approval remains unrecorded. Read [STATE.json](STATE.json), [DELIVERIES.md](DELIVERIES.md) and their evidence before starting another coordinator or changing picture inputs.

Use [NATURAL-PERFORMANCE.md](NATURAL-PERFORMANCE.md) for reproduction and the reusable conditioning layer. Use [MOTION-LIBRARY.md](MOTION-LIBRARY.md) and [catalogs/motions.json](catalogs/motions.json) for actual compiled clips and clearly separate proposed additions. `concert-dance-study` uses six single-thread CPU workers for 1080p; `concert-dance-study-4k` uses three for native 4K. A single native 4K frame has rendered, but the configured full 4K movie remains unrendered at this handoff.

That earlier duet repeats one existing CMU 05_02 phrase with a 0.6-second offset. Its stored whole-body poses are 30 Hz and are interpolated at 60 fps. The source phrase and pacing constrain sustained flow and variety; stronger complementary choreography remains next work. Fingers and thumbs were not captured, and bounded contact cleanup does not simulate physical balance. Preserve these distinctions when reporting movement quality. The earlier Consideration and model deliveries below remain completed previous-increment records.

## Coordination

- One scene/model writer per file group. One coordinator owns shared lighting, timing, status and final assembly.
- Record file ownership in the work plan before parallel edits. Helpers may read shared sources; they must not overwrite another builder's changes.
- Freeze a round before final rendering. Hashes should reject mixed versions, not be edited to hide a mismatch.
- Keep deterministic scene state at absolute song time. Random seeds, delayed effects and trails must not depend on visit order or worker history.
- Keep an append-only log entry per integrated change. Distinguish planned, source-ready, rendered, technically checked, visually reviewed and owner-approved.
- Do not mark a new model approved because an older film using the same renderer was approved.

## Session closeout

Leave a self-contained record of the branch/commit, owned files, selected audio hash, render command, output paths and hashes, last completed frames, current visual finding, archive links and the next bounded task. If a process was interrupted, preserve verified partial frames and explain how to resume. If no process or automation is running, say so; a saved backlog does not run itself.

## Required distinctions

| Distinction | Why it matters |
| --- | --- |
| Original recording versus guide versus stage conformance | The same title can have different timing, instrumentation and source bytes |
| Current source versus delivered picture | Some historical fixes were committed but never rendered |
| Reference approval versus new study | Aesthetic approval belongs to a specific output, not every future use of the code |
| Model source versus reviewed model | An existing constructor may still have contact, silhouette or integration defects |
| Native 4K versus upscaling | Detail must be rendered at the claimed size |
| RGB8 versus RGB16/HDR | Higher dimensions do not change the source precision or color contract |
| Installed tool versus verified runtime | Browser, GUI and GPU capabilities need actual execution evidence |

## What should stay out of Git

Full audio, copied lyrics, finished videos, frames, generated caches, temporary downloads, access tokens, signed download links and personal data. Short historical repo clips remain as inherited exceptions; do not extend that exception to the full concert. Store durable media in the existing shared Drive home. The `.gitignore` work paths are intended for reacquirable private working copies.

## Completed previous increment and prior Drive delivery

Read [DELIVERIES.md](DELIVERIES.md) and `catalogs/deliveries.json` for the eight saved media files and their verified Drive links. All eight exact files were uploaded after the owner confirmed the named files and destination, then checked by raw-byte readback. The requested delivery event was appended once to the existing Drive log, preserving its 106 original entries and producing 107 entries. Its original event timestamp and historical statuses were retained as requested. Current transfer completion is established by `evidence/drive-delivery-completion.json`; do not repeat these completed operations because the historical event or earlier rejection records say pending. The five existing Drive instruction updates remain complete.

The corrected fifteen-second movie has independent technical QA and sampled encoded review. The new studies and models still await their own creative approval; copying them to Drive does not confer that approval.

The original handoff ZIP was not retained in a recoverable form when its workspace expired. Its historical size, SHA256 and source checkpoint remain in `evidence/handoff-export.json`. A replacement was reconstructed from the same clean source checkpoint `94dd897c6fdeb287561c5dd2772b770c43ab94b7`; all 89 source-document payloads match the Git blobs exactly. The new ZIP timestamps and export receipt change the archive bytes, as recorded in `evidence/handoff-reconstruction.json`.

**All three prior Drive operations are complete.** After the owner confirmed the exact saved replacement, the ZIP was uploaded to Production System and verified against the original saved source by downloading the Drive bytes. The delivered identity is:

- Filename: `Concert-Production-System-Handoff-2026-11-20.zip`.
- Verified Drive file: [open the ZIP](https://drive.google.com/file/d/1gp0x2dnj06eIPDuq6vSGpGtKn_bvKrML/view), file ID `1gp0x2dnj06eIPDuq6vSGpGtKn_bvKrML`.
- Destination: Production System, folder `1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X`.
- Size: 350,534 bytes.
- SHA256: `eb8bba933a37179fa970c84aecc67cbc0b493809d1e2b2e7863c3900b9606537`.
- Saved backup: [exact version 0](https://chatgpt.com/library?file_id=libfile_0d7ab1c2d83c8191a3badd389c6dc483&account_id=personal), backing file `file_00000000356481fd982a7d39a046118f`.

Read `evidence/drive-handoff-completion.json` for the actual outcome. The earlier replacement rejection in `evidence/drive-handoff-replacement-block.json` and original archive SHA256 `605b7be8ca59987651a642727a9babef88e01986c87d8ea7e3ca076e84a2e158` remain historical evidence. Do not repeat the eight media copies, log append or archive upload, or request their confirmation again. Recover the delivered archive from the recorded Drive file or pinned backup if needed; verify its hash before use.

The confirmed ZIP is an immutable historical snapshot. PR #106 records the earlier fan-trio delivery; current Git source, this handoff and PR #108 carry the Cinematic Ten round. A future deliberately versioned export includes later documentation and manifests without replacing the confirmed archive.

For every future pending delivery, preserve the exact payload bytes durably before ending the turn and record the saved file identity, version, size and SHA256. A source commit can reproduce document contents while a new ZIP container and receipt have different bytes. Recover the saved approved version on a retry instead of creating a new package.
