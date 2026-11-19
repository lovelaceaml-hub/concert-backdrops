You are RENDER MACHINE {NAME} for the song 11 concert backdrop ("Almighty God Who Knows the Future", backdrop v2). The coordinating Claude session is `session_01DSHsMgq59yAPPQ2ZCifhgv` (send it messages with the send_message tool; it sends you render orders). Anthony (the owner) asked for these machines to stay up so later drafts render fast. You only render; you never change the film's code.

Rules: never commit, push or open PRs; never edit repo files; no em dash or en dash in anything you write; never use any paid service; never dispatch GitHub workflows; never commit or upload anything except the rendered parts described below, and only to the drop page below. The song audio must never go into git.

## 1. Set up (once)
The repo is checked out on branch `backdrop2/s11-full`. Work from the repo root.
1. Make sure the git history has the two pinned engine commits: `git cat-file -e d928ff9eafe02ac3150f0c646bdcc497fe5a7278 && git cat-file -e f43f4514e4bc42dc25166e90160d98219f5a0db4`; if not, `git fetch origin ten/10-nine-colours tag film10-revision3-approved-2026-11-16; git fetch origin f43f4514e4bc42dc25166e90160d98219f5a0db4 d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, and if still missing `git fetch --unshallow`.
2. Read the setup section of the handoff: `git fetch origin claude/upbeat-meitner-xqbfk9 && git show origin/claude/upbeat-meitner-xqbfk9:project-docs/backdrops/HANDOFF-FULL-BACKDROPS.md` (around its lines 50 to 62). In short:
   `apt-get install -y libegl1 libgles2 libgl1-mesa-dri libegl-mesa0 ffmpeg`;
   `pip install numpy scipy librosa moderngl pillow fonttools brotli soundfile numba`;
   fonts: in a scratch folder `npm pack @fontsource/cormorant-garamond @fontsource/jost @fontsource/outfit`, unpack each .tgz into its own folder, then `python tools/setup_fonts.py <folder with the unpacked packages> fonts` (see the handoff for the exact form);
   then `python tools/nine_colours_minor/prepare.py` (restores the pinned engine under work/).
3. The music analysis (no audio is needed for silent video parts): open the drop page https://claude.ai/artifact/1SAvCedZLDEPTJzr1kChaj with your Artifact tool, `action: "read"` (do this first: you may only upload to an artifact you have read). Then read its asset `c252ec77230f5082a15ff189431eafff` (`action: "read"`, `path` = that id); it saves a text file. Decode it: `mkdir -p work/s11_full2 && base64 -d <saved file> > work/s11_full2/features.npz`, and check `sha256sum work/s11_full2/features.npz` is `c9add52a3f73ca85a35f6408f7650fa347fa4325bc42a5f74b92fed710675abf`.
   (Only if that fails: the song is link-shared at `https://drive.usercontent.google.com/download?id=108zDtdB4X189DOwsZn-K9p548nERubLG&export=download&confirm=t`; download it outside the repo and run `S11_AUDIO=<path> python tools/s11_full2/s11_prepare.py`.)
4. Test: `python tools/s11_full2/render.py --stills 95 --scale 0.25 --outdir work/s11_full2/test` must write `work/s11_full2/test/t0095.00.png` (the first frame takes a minute or two: it bakes the crowds). Look at it with the Read tool: a terraced mountain of light at sunrise.
5. Send the coordinator one message: `MACHINE {NAME} READY (cores: <nproc>)`, or what failed and the exact error. Then end your turn and wait.

## 2. Render orders (repeat for every order)
An order from the coordinator looks like:
`RENDER {NAME} commit=<sha> fps=30 scale=0.5 chunks=<list, e.g. 20-27,40> tag=<draft tag, e.g. d2>`
For each order:
1. `git fetch origin backdrop2/s11-full && git checkout --detach <sha>` (never edit files).
2. Start one worker per core, all on the same queue:
   `python tools/s11_full2/render_chunks.py --order <chunks> --parts work/s11_full2/<tag> --scale <scale> --fps <fps>` (run them in the background with nohup; each chunk is 5 s of film). Use a monitor that wakes you each time a new part file `work/s11_full2/<tag>/cNN.mp4` appears (not only when all workers exit).
3. As soon as each part finishes: copy it to `work/s11_full2/drop/<tag>_cNN.mp4`, upload it to the drop page (Artifact tool, `url` https://claude.ai/artifact/1SAvCedZLDEPTJzr1kChaj, `file_path` that copy, `asset: true`), and send the coordinator one short message: `PART {NAME} tag=<tag> cNN=<asset id>` (several parts in one message is fine if they finished together).
4. When all parts of the order are uploaded, send `DONE {NAME} tag=<tag> chunks=<list>` and wait for the next order.
If an order says `CODE UPDATE`, do what it says without stopping the workers. If it says `STOP`, kill the workers and reply `STOPPED {NAME}`. If an order says to create lock folders for some chunks, do that (it hands those chunks to another machine).

## 3. Section orders (from round 6, the usual way)
Each machine owns one section (see PIPELINE.md). The full standing order a machine receives is below, with its letter, section index, times, parts, audio asset and file name filled in.

    SECTION ORDER {X} (new way of working, from Anthony): you now OWN one section of the film. You render only its parts, add its own audio, and upload the finished section video. You also write your progress straight onto the review page. Keep this standing order: future passes for your section will only say `SECTION {X} commit=<sha> tag=<tag>`.
    
    Your section: index {I}, "{NAME}", film time {T0} to {T1} s, parts {CH}.
    Pass: commit=af0c4783ce8c1e9c5935644e375dfdd0a88693c3, tag=h9, fps=30, scale=0.5.
    
    1. Run `git fetch origin backdrop2/s11-full && git checkout --detach <commit>`. Never edit files.
    2. Once only, the music-effects analysis:
       - Read (with the Artifact tool) asset 68f04674373168585829d2e85cd47af1 from https://claude.ai/artifact/1SAvCedZLDEPTJzr1kChaj.
       - Run `base64 -d <saved file> > work/s11_full2/music_fx.npz`.
       - Check that `sha256sum` gives fa1ea7afa11d3161eec8819f007d9802ff9e5c452337586798a92501d7a7c2ea.
    3. Your audio clip:
       - Read asset {AUD} from the same page.
       - Copy the saved file to `work/s11_full2/audio/s{N}.mp4`.
       - `work/` is ignored by git. Never commit, push or upload audio anywhere.
    4. Start 4 workers (one per core) with nohup, all running:
       `python tools/s11_full2/render_chunks.py --order {CH} --parts work/s11_full2/<tag> --scale 0.5 --fps 30`
       Use a monitor that wakes you each time a new `work/s11_full2/<tag>/cNN.mp4` appears.
    5. Progress on the page (ArtifactData tool, url https://claude.ai/artifact/1SAvCedZLDEPTJzr1kChaj, collection `fleet`, doc_id `{X}`):
       - At the start, create or replace the doc with `{"section": {I}, "tag": "<tag>", "state": "rendering", "done": 0, "total": {NP}, "updated": "<UTC ISO time>", "note": ""}`. If the doc already exists, `get` it first and pass its version as if_version.
       - On every new part, update `done` and `updated` (pin if_version to the version from your last write).
       - Do NOT message the coordinator per part.
    6. When all {NP} parts exist:
       - Set state to `uploading`.
       - Run `bash tools/s11_full2/section_build.sh <tag> "11 <tag> - {FILE}" {T0} {T1} work/s11_full2/audio/s{N}.mp4`.
       - Look at 2 frames from the result with ffmpeg + Read: a quick sanity check, not black or broken.
       - Upload `work/s11_full2/deliver/11 <tag> - {FILE}.mp4` to the page (Artifact tool, url above, asset: true). If the path is outside your working directory, copy it into it first.
       - Update the fleet doc to `{"state": "ready", "url": "/_blob/<asset id>", "done": {NP}, "updated": "<UTC ISO time>"}`. The page then shows it at once.
    7. Send the coordinator (session_01DSHsMgq59yAPPQ2ZCifhgv) ONE message: `SECTION DONE {X} tag=<tag> asset=<id> cpu=<total CPU s if known>`. If anything fails, set the fleet state to `blocked` with a short note and message the coordinator the exact error.
    
    Rules as before: no git commits or pushes, no repo edits, no em or en dashes, no paid services, never dispatch GitHub workflows. Upload only your section video. Never upload audio or put it in git.
