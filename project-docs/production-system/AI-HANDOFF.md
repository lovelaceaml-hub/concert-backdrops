# Handoff for a new AI or chat

Copy the following instruction into a new working chat. The files it references carry the actual state; this prompt is an entry point, not a substitute for reading them.

> Work on the concert-backdrops project for The Words of Mother's Love. Read root AGENTS.md and project-docs/production-system/START-HERE.md, then the current Drive rules, the exact song catalog entry, the approved reference catalog and the latest production log. The central message is that Mother's Words of Love bring peace. The approved 66-second Nine Colours Revision3 promo is the creative baseline, and the owner-approved 30-second Song11 beauty study is the clarity and production baseline. Continue the concrete next item in IMPROVEMENT-QUEUE.md using an isolated branch and one writer per area. Reuse reviewed native p3d models and performances, preserve the approved snapshots, verify the selected recording by SHA256, and author a readable human action before expanding its environment. Render native full-size keyframes and a short motion proof, inspect the actual output, then save media, receipts, source hashes and shared status. Use scripts/concert for catalog/audio/handoff tasks and scripts/video produce for registered render projects. Keep full songs, lyrics, frames and videos out of Git. Use cloud CPU workers; the cloud GPU provider remains unconfigured. Apply the current user's authorization, and do not repeat permission questions for work already authorized. Report what was actually rendered, reviewed, uploaded and merged, with direct links and remaining limitations.

## Read order and precedence

1. Current user directions and current session corrections.
2. Root `AGENTS.md` and this production system's current records.
3. Live Drive rules, latest dated addenda and per-song status. Historical comments can be stale; preserve them but resolve conflicts explicitly.
4. The exact approved media and immutable source records.
5. The selected song's original recording identity, continuity and known unrendered changes.
6. Implementation documentation for the chosen adapter and models.

Do not restart the old promo, regenerate approved art or re-open a completed repair because an old handoff says it is pending. The source catalog records that all eleven recordings exist. Several full-song delivery records refer to prior chats and have not been independently watched in this audit; do not claim those videos were visually verified just because their status pages were read.

Use [AUTHORING-NEXT-SONG.md](AUTHORING-NEXT-SONG.md) when moving from a study to a new complete song. The current kit adapter explicitly accepts the historical Consideration scene and its separate camera and response revision. A new audio source or a renamed project is not a new authored film; add and verify its explicit scene registration while preserving the approved projects. Prefer `concert-kit-consideration-v2` when studying the corrected hand return and clearer rise; retain the original 18-second file as evidence of what needed repair.

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

## Current delivered media

Read [DELIVERIES.md](DELIVERIES.md) and `catalogs/deliveries.json` for the eight saved files from this increment. The corrected fifteen-second movie has independent technical QA and sampled encoded review; it has not inherited the owner approval of the two references. New private Drive media copies remain pending the recorded exact-file/destination confirmation. Do not retry that rejected transfer through a different route or substitute a media payload into an existing file. The permitted existing Drive instruction updates are already complete. Use current `STATE.json` and PR 102 for the later handoff archive and integration outcome.

The final Drive production-log append was separately rejected by automatic review. Its prepared delivery event is already in the repository log, with exact target and payload evidence in `evidence/drive-production-log-block.json`. Do not mark the Drive log updated or retry through another route without the required confirmation.

The versioned handoff ZIP was subsequently exported and verified from clean commit `94dd897c6fdeb287561c5dd2772b770c43ab94b7`; its new Drive upload was also rejected. Read `evidence/handoff-export.json` and `evidence/drive-handoff-upload-block.json`. The Git source and instructions are saved, and the eight new media files are saved. The outstanding Drive operations are the media copies, this exact archive and the log append. Do not describe any of them as uploaded.
