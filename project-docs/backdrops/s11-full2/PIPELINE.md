# Song 11 v2: how the film is rendered and reviewed (reusable for every song)

## Render
- Engine: the pinned Film 10 R3 snapshot (`tools/nine_colours_minor/prepare.py` restores it under `work/`), song code in `tools/s11_full2/`. Prepare once: `S11_AUDIO=<song file outside the repo> python tools/s11_full2/s11_prepare.py` (writes features.npz and score.wav under work/, never in git).
- Stills: `python tools/s11_full2/render.py --stills 95,120.5 --scale 0.25 --outdir <dir>` (first frame of a process bakes crowds and cloth: 1 to 3 minutes; then about 1 to 3 CPU s a frame at quarter size, 2 to 7 at half).
- Parts: the film is 55 parts of 5 s (`render_chunks.py --order <list> --parts work/s11_full2/<tag> --scale 0.5 --fps 30`). One worker per core; workers share a queue through lock folders in `<parts>/locks/cNN` (creating a lock folder hands that part to another machine).
- A section video: `tools/s11_full2/section_preview.sh <tag> <name> <t0> <t1>` joins the parts, trims and adds the recording's audio (into work/s11_full2/deliver/, never in git).
- Each join writes its own private part list (mktemp). Never build sections from one shared list: on 2026-11-19 parallel builds sharing `<tag>/sec.txt` gave every h8 section another section's pictures over its own music. After any join, check a frame sheet (the right scenes at the right times) and that a known hit's flash lands on the audio onset.
- Freeze code for an in-flight render with a separate worktree (`git worktree add ../wt-render <sha>`, then symlink `work` and `fonts` into it) so edits in the main tree do not change parts mid-render. A part picks up new code only when its process starts.

## The render fleet (cloud machines)
- Each machine is a Claude Code cloud session with 4 cores, created with the prompt in MACHINE-PROMPT.md (replace {NAME}). Setup takes about 15 minutes once; machines stay up between renders.
- Orders: `RENDER X commit=<sha> fps=30 scale=0.5 chunks=<list> tag=<tag>`. Machines upload each part to the drop page as soon as it finishes and send `PART X tag=<tag> cNN=<asset id>`; `DONE X ...` at the end. `CODE UPDATE` switches commit without stopping workers; lock-folder handoffs move parts between machines.
- Song 11 fleet (2026-11-19): A, B, C, D, E, F, G plus the coordinator's own 4 cores: about 32 cores, a full pass in roughly 12 to 15 minutes.
- The coordinator downloads each asset (Artifact read with `path` = asset id, one per call), copies it into the parts folder (`tools/s11_full2/live/place.sh`), joins sections as they complete and publishes them.

## One section per machine (Anthony, 2026-11-19, from round 6 on)
"Make it so that each of those machines has specific parts that they work on, and then they can have the audio. That way, you don't have to keep splicing it and cutting it. You just have to put it together."
- Standing assignment: A Intro (parts 0 to 7), B Verse 1 (8 to 16), C Chorus 1 (16 to 24), D Verse 2 (24 to 31), E Chorus 2 (32 to 40), F Coda (40 to 47), G Ending (47 to 54). A pass is ordered with `SECTION X commit=<sha> tag=<tag>`.
- Each machine renders its own parts on its 4 cores, then `tools/s11_full2/section_build.sh <tag> <name> <t0> <t1> <clip>` joins them, cuts exactly t0..t1 and adds that section's own audio clip (crf 25, ready for the page). It uploads the section video to the review page and writes its progress itself to the page's `fleet/<letter>` doc (section, state, done, total, url, updated); the page shows the progress live and swaps in the new video the moment it is ready.
- The audio clips (one per section, cut from the recording) and the music analysis (music_fx.npz, as base64 text) are private assets on the review page, listed in its `keep/now` doc. Never in git.
- The coordinator only checks each finished section, assembles the full film, answers Anthony's requests and keeps the records.
- Storage: the review page keeps only the newest section videos and the files in `keep/now`; its "Clear old files" button removes the rest (old versions are not archived: Drive uploads from a session are limited to about 3 MB).

## The reviewer (Anthony, 2026-11-19: "create another thread that's specifically for reviewing and giving suggestions and findings")
- A dedicated cloud session (the "Song 11 reviewer") reviews every pass against DESIGN.md and Anthony's requests: frames every 1 to 2 s, every phrase and hit, sync, glare, clutter, colour, cinematic quality. It posts its findings and creative suggestions straight to the review page (`findings/*`, state open, by "reviewer") for Anthony to approve or decline, then tells the coordinator `REVIEW DONE pass=<tag> findings=<ids>`. It never edits code or renders.
- The coordinator orders a review with `REVIEW pass=<tag>` after each pass and acts on approved findings in the next round.

## The review page (Anthony's live dashboard)
- A private claude.ai artifact (source `tools/s11_full2/live/review_page.html`) with the `db` and `assets` capabilities.
- Shows: each section's newest video in order with "Updated # minutes ago" and play straight through; live status (overall progress, a card per machine, what each is rendering); findings and suggestions with Approve and Decline; request boxes per section and for the whole film. Compact; findings and requests fold.
- Data: `status/now` (written by the coordinator from `tools/s11_full2/live/status_gen.py`, which reads the parts folder, the running renders and sections.json / machines.json), `findings/*` (coordinator writes; Anthony approves or declines on the page), `requests/*` (Anthony writes on the page; the coordinator replies and sets Working on it / Done).
- Cadence (Anthony's choice): status updated on every finished part during a render (`live/wait_change.sh` wakes the coordinator), requests and decisions picked up at each update.
- Section videos are re-encoded smaller (crf 25) and uploaded as assets; their urls go in sections.json.
