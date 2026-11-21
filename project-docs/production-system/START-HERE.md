# Concert production system

Current handoff: November 20, 2026, America/Los_Angeles. Machine observations dated November 21 in the source catalog use UTC.

**The Words of Mother's Love bring peace.** Build every film around that message. The owner approved the sharper Song 11 beauty study and requested that its setup, source, instructions and references be saved, uploaded and merged for every AI to reuse. The owner also authorized continued model, acting and workflow improvement across the concert songs.

## The shared starting point

The code, reusable scene tools and versioned instructions are in [concert-backdrops](https://github.com/lovelaceaml-hub/concert-backdrops). The shared project home remains [Concert Backdrops - Songs](https://drive.google.com/drive/folders/1xyNZn4ZA6bjPcvKjGfgSWQIs9aAp2PPd). Its [Production System folder](https://drive.google.com/drive/folders/1QDGGqqkJlbovBLCthX-QChqfD8zSmK8X) carries a portable handoff for chats without a checkout. Media is in [Videos / Production Studies](https://drive.google.com/drive/folders/1hrk62bFIOHv2NwXvYl2bNSmp0cwBoXrr).

Read this file, [AI-HANDOFF.md](AI-HANDOFF.md), [CREATIVE-RULES.md](CREATIVE-RULES.md), and the current song record before changing anything. Read the current Drive AGENTS, DESIGN-SYSTEM, VIDEO-HANDOFF, AUTONOMOUS-RUN and November 19 lessons addendum. Older instructions remain historical evidence; the latest owner's directions and later dated corrections govern current work.

| Source of truth | Purpose |
| --- | --- |
| [Reference catalog](catalogs/references.json) | Exact approved films, hashes, pinned source and durable media links |
| [Song catalog](catalogs/songs.json) | All 11 verified full recording identities, timing caveats, previous deliveries and proposed improvements |
| [Model catalog](catalogs/models.json) | Existing native models and performances, new model families, eligibility and limitations |
| [Audio audit](SONG-AUDIO-AUDIT.md) | What was independently downloaded/decoded, what earlier builders reported, and stale records corrected |
| [Improvement queue](IMPROVEMENT-QUEUE.md) | Concrete next work by model family and song, with evidence required for completion |
| [Pipeline integration](../../docs/PIPELINE-INTEGRATION.md) | Registered renderers, source clocks, color handling, resume and CLI commands |
| [Current state](STATE.json) | Delivery, integration and open work status; never substitute it for a render receipt |

## Two approved references, with different jobs

**Film 10, Nine Colours, Revision 3, 66 seconds** is the creative reference. Preserve the warm people, mirror lake, expression colors, meaningful gestures, light traveling through depth, camera flights and designed ending. The exact campaign wording and colors come from `engine/p3d/words.py`; do not retype or paraphrase them in a new renderer.

**Song 11 beauty study, 30 seconds, native 1080p60** is the clarity and production reference. It preserves the original Song 11 world and choreography, with better focus, controlled brightness, native detail and two temporal samples. The owner approved its appearance in the current conversation. Its original picture source, audio clock and identity are recorded separately from the finished master. It is an excerpt, not a replacement full-song film.

The earlier 30-second people demonstration remains an engineering experiment. The owner found it sharper but less beautiful than the promo. Do not promote that example into the creative baseline merely because its checks passed. The 10-second design example proves native 4K delivery; it does not prove all concert scenes have been rendered in 4K.

## First commands in a fresh chat

Work in an isolated branch and worktree based on current `main`. Each builder owns a distinct set of files. Do not dispatch paid workflows or use the Mac as a default render worker.

```bash
git fetch origin
git worktree add -b creative/song07-next ../concert-song07 origin/main
cd ../concert-song07
./scripts/concert status
./scripts/concert song s07
./scripts/concert plan s07
```

`plan` saves an ignored work plan and refuses to replace an existing one. It brings forward the recording identity, expression continuity, current world, known issues and proposed improvements. It deliberately leaves the full-song render command empty until an actual scene is authored. An audio file and an asset list cannot by themselves specify a finished film.

Recreate dependencies with the existing pinned bootstrap:

```bash
python3 scripts/bootstrap.py --p3d-only
```

For a p3d worker, install the host tools and software EGL/Mesa libraries documented in the pipeline guide, then use this mode to recreate locked Python packages and pinned fonts. It skips Blender, browser installation, app builds and optional integrations. The backend-specific doctor checks the requested route. The optional browser/Blender/Shotcraft integrations retain their own readiness states; use the full bootstrap when those are needed. See the installation and environment limits in [VIDEO-PIPELINE.md](../../docs/VIDEO-PIPELINE.md) and [VIDEO-PIPELINE-VALIDATION.md](../../docs/VIDEO-PIPELINE-VALIDATION.md).

Full recordings are private inputs. Use the connected Drive tool to download each cataloged file into its specified `work/song-sources/` path, then verify the bytes:

```bash
./scripts/concert verify-audio all
./scripts/concert verify-audio s07 --decode
```

All eleven selected originals were downloaded, hashed and decoded in this setup. A new checkout must reacquire them. Songs 02 and 10 now have full recordings; their historical `audio/promo/` clips remain silent placeholders. Never use those clips as a substitute.

## Reproduce the approved Song 11 reference

Place the verified original also at `work/song-inputs/s11-original.mp3`, as required by the registered reference project. The source catalog provides its Drive ID and full SHA256. Do not replace it with another encoding of the same song.

```bash
./scripts/video doctor --project approved-light-s11
./scripts/video produce approved-light-s11 --quality review --plan
./scripts/video produce approved-light-s11 --quality review --frames 45,501,900,1236,1476,1740
./scripts/video produce approved-light-s11 --quality review
```

The registered adapter checks the historical source and assets, prepares the known Song 11 audio, and uses the existing frame checkpoint scheduler. It rejects unsupported recording or scene identities. The original historical script remains available in `tools/promo_beauty_example/`; its own README and verification describe the delivered movie exactly.

## Build and review the new Consideration study

The reusable scene connects helping someone stand to a wave of light opening the shore. It uses two warm gold men, a captured paired action, explicit hand contact, native 3D shore models and an authored ending. It is a new study awaiting the owner's creative review, not an automatically approved extension of the reference film.

```bash
./scripts/concert verify-audio s07
./scripts/concert prepare-study-audio
./scripts/video doctor --project concert-kit-consideration
./scripts/video produce concert-kit-consideration --quality review --plan
./scripts/video produce concert-kit-consideration --quality review --frames 0,180,450,720,1000
./scripts/video produce concert-kit-consideration --quality review
```

The audio is the original Song 07 interval 137.5 to 155.5 seconds, without time stretching. The preparation command verifies the original hash and produces the recorded 18-second WAV. It includes a small gain reduction and short fades. The world response at study time 11.5 seconds follows the documented transition out of a quiet passage; an exact ear-verified transient alignment is not claimed.

Check `projects/concert-kit-consideration/project.json` for the current frame rate, samples and frame count before choosing a frame number. The direct scene tool also offers second-based still selection. Every rendered variant must carry its own source fingerprint; changing the camera, action, audio, fonts or model invalidates affected output.

## The production cycle for every song

1. **Read and claim.** Read the latest owner direction, shared records, song status and current references. Claim one area. Record the commit, chosen source audio and intended change.
2. **Author the human story.** State what someone notices, chooses, does and changes. Choose an expression performance and a song-specific world. Keep the people readable before adding the large effects.
3. **Make full-size frames.** Review a close action, a wide world and the ending at native 1080p. A 540p draft cannot approve facial silhouettes, fingers, emblems or type.
4. **Make a short moving proof.** Inspect approach, contact, release, foot placement, garment motion, camera acceleration and the response of the world. Use authored cue times tied to the exact recording.
5. **Freeze the scene.** One coordinator integrates changes. Freeze shared lighting and source identity for a render round. Use explicit temporal samples and cut-safe shutter times.
6. **Render and resume.** Start with one or two measured workers. Reuse only valid receipts. Preserve partial verified frames after an interruption. Check source identity again before assembly.
7. **Review the finished output.** Inspect all shots and boundaries, not only a middle frame. Check durations, native size, frame cadence, audio peaks, sync, brightness reversals, freezes and text. Keep machine findings separate from aesthetic approval.
8. **Save and hand off.** Save the master, compact viewing copy, keyframes, QA, source hashes and links in the shared media folder. Update catalogs, status and append-only production log. Push the isolated work and use a normal PR merge with expected-head checks.

## Native 4K and smooth motion

Native 4K is supported where the selected adapter exposes a 3840 by 2160 quality preset. It requires new native frames, fonts and render receipts. Do not rename an upscaled 1080p output as native 4K. The approved 30-second beauty study is 1080p60; its conductor still is native 4K. A full 4K version of that excerpt has not been delivered.

Smooth animation comes from authored acceleration, weight, contact, overlap, camera paths and subframe evaluation. More frames do not fix skating feet or hands that miss. Keep close figures evaluated at the real output times; do not mistake a lower-rate crowd cache for a hero performance. Keep motion blur within a shot and preserve the final pose long enough to read.

## Recover the exact approved master

The Drive connector accepted files up to 100 MiB in this session. The 110,865,643-byte approved master is preserved as two binary parts, with a separate normal viewing MP4. Download both parts and the parts manifest from Production Studies, then run:

```bash
./scripts/concert restore-master \
  --manifest project-docs/production-system/catalogs/song11-master-parts.json \
  --parts /absolute/path/to/downloaded-parts \
  --out /absolute/path/to/Song11-Beauty-Study-30s-1080p60.mp4
```

The command verifies both part hashes and the complete original SHA256 before naming the result. It refuses to replace a different existing output. The restored master is the original approved file; the viewing copy is a separately fingerprinted encode.

## Portable handoff

```bash
./scripts/concert export-handoff --out work/handoffs/concert-system-handoff.zip
```

This collects instructions and catalogs, with no full audio, lyrics, videos or credentials. The Git repository remains the source for executable code. A Drive copy must state which code revision it accompanies. Do not treat this system as an unattended background service: progress continues when a chat or an explicitly configured job runs it.
