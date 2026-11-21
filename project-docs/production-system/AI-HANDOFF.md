# Handoff for a new AI or chat

Copy the following instruction into a new working chat. The files it references carry the actual state; this prompt is an entry point, not a substitute for reading them.

> Work on the concert-backdrops project for The Words of Mother's Love. Read root AGENTS.md and project-docs/production-system/START-HERE.md, then the current Drive rules, the exact song catalog entry, the approved reference catalog and the latest production log. The central message is that Mother's Words of Love bring peace. The approved 66-second Nine Colours Revision3 promo is the creative baseline, and the owner-approved 30-second Song11 beauty study is the clarity and production baseline. Continue the concrete next item in IMPROVEMENT-QUEUE.md using an isolated branch and one writer per area. Reuse reviewed native p3d models and performances, preserve the approved snapshots, verify the selected recording by SHA256, and author a readable human action before expanding its environment. Render native full-size keyframes and a short motion proof, inspect the actual output, then save media, receipts, source hashes and shared status. Use scripts/concert for catalog/audio/handoff tasks and scripts/video produce for registered render projects. Keep full songs, lyrics, frames and videos out of Git. Use cloud CPU workers; the cloud GPU provider remains unconfigured. Apply the current user's authorization, and do not repeat permission questions for work already authorized. Report what was actually rendered, reviewed, uploaded and merged, with direct links and remaining limitations.

## Latest owner direction and active performance

The owner said to try the supplied references as well as possible without waiting for new files. Start with [FAN-SILK-PERFORMANCE.md](FAN-SILK-PERFORMANCE.md) and [tools/concert_fan/README.md](../../tools/concert_fan/README.md). The new original `concert-fan-trio` has a twenty-second clock, distinct lead/answer/welcome roles and two held fans with finite silk. Picture source: `dffe8f165944c627ae39a8bb7d47bc5a9e703305`. Resolve exact delivery and review status through the current catalogs. Moving reference footage has not been inspected; the first two posters are the visual evidence. Preserve that provenance boundary while continuing useful original work.

## Read order and precedence

1. Current user directions and current session corrections.
2. Root `AGENTS.md` and this production system's current records.
3. Live Drive rules, latest dated addenda and per-song status. Historical comments can be stale; preserve them but resolve conflicts explicitly.
4. The exact approved media and immutable source records.
5. The selected song's original recording identity, continuity and known unrendered changes.
6. Implementation documentation for the chosen adapter and models.

Do not restart the old promo, regenerate approved art or re-open a completed repair because an old handoff says it is pending. The source catalog records that all eleven recordings exist. Several full-song delivery records refer to prior chats and have not been independently watched in this audit; do not claim those videos were visually verified just because their status pages were read.

Use [AUTHORING-NEXT-SONG.md](AUTHORING-NEXT-SONG.md) when moving from a study to a new complete song. The current kit adapter explicitly accepts the historical Consideration scene, its separate camera and response revision, the natural dance scene, and the original fan and silk trio. Together with the approved Song 11 adapter, the system has five scene registrations across six configured projects; the two natural dance projects share one registration. A new audio source or a renamed project is not a new authored film; add and verify its explicit scene registration while preserving the approved projects. Prefer `concert-kit-consideration-v2` when studying the corrected hand return and clearer rise; retain the original 18-second file as evidence of what needed repair.

## Reference intake and faithful adaptation

The owner's three YouTube references are cataloged in `catalogs/performance-references.json`. The later best-effort attempt inspected the first two posters, but actual moving footage remained unavailable. The delivered fan and silk trio is an original twenty-second performance, not source pose extraction or a reconstruction of those three choreographies. The optional Blender performance exporter remains unimplemented.

The working local-video intake utility in `tools/performance_reference/` preserves source hashes, requested ranges and actual decoded timestamps, then creates review samples and an annotation manifest. Use it when continuous source footage becomes accessible. The earlier [sixteen-second treatment](REFERENCE-CREATIVE-TREATMENT.md) is planning history, superseded by the implemented twenty-second study. [PERFORMANCE-AUTHORING.md](PERFORMANCE-AUTHORING.md) remains the authoring contract. Continue richer whole-body phrases and costume response through [NEXT-PERFORMANCE-UPGRADES.md](NEXT-PERFORMANCE-UPGRADES.md) without blocking useful original work on another upload request.

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

The confirmed ZIP is an immutable historical snapshot, not a rolling copy of the newest dance work. Current Git source and versioned handoffs are authoritative for later setup; use PR #106 for the latest source and delivery integration record. A future deliberately versioned export includes the new dance documentation and manifests without replacing the confirmed archive.

For every future pending delivery, preserve the exact payload bytes durably before ending the turn and record the saved file identity, version, size and SHA256. A source commit can reproduce document contents while a new ZIP container and receipt have different bytes. Recover the saved approved version on a retry instead of creating a new package.
