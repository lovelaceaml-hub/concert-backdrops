# Approved delivery: Film 10, Nine Colours, Revision 3

The owner approved this delivered cut on 2026-11-16: "thats so good. save this and update all docs and upload". Preserve these exact files and source when making future alternatives. Video approval does not authorize a merge; the implementation and documentation PRs remain draft and unmerged.

## Watch and download

| Copy | Link | Exact size | Format |
|---|---|---:|---|
| Phone | [Watch or download](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view) | 22,278,585 bytes | 1280x720, 60 fps, H.264/AAC |
| Master | [Download master](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view) | 94,541,396 bytes | 1920x1080, 60 fps, H.264/AAC |

Both files are 66.000 seconds, 3,960 frames, stereo 48 kHz audio, and support progressive MP4 playback. They are saved in the project's [Videos folder](https://drive.google.com/drive/folders/1oNl_-SVqTwrYzqT87JQ3Om9HQFrcMOkz). The phone copy was downloaded back from Drive and delivered as a chat attachment; its SHA-256 matches the local output exactly. Keep the existing file IDs and links when referring to this approval.

| Artifact | SHA-256 |
|---|---|
| Master MP4 | `508c5518bced94b21f96e8727d2b7ffd0da0ee69de9da164e7e5e824e80eda7b` |
| Phone MP4 | `ad4b4e7fe861ae34eb80e8b921ee747efc477c08bb89ec981f1b588a0b3c0af5` |
| Approved PCM score | `524f0d14abafd517335c87049e59a2538c0b560cf04b26828463707790c31d6e` |

## What the owner approved

- The Film 10 concept, music, light direction and energetic travelling camera remain the foundation.
- Extended opening card over the night lake, sparkles bursting behind the words, then the first expression. Six-second lead-in and 66-second total duration are intentional.
- All nine expressions use Claude Final v1's luminous cream serif phrases and colored glowing capsule labels. The signature remains discreet at the bottom left.
- Respect uses the reference's two golden women, refined offer/listen gestures and lantern-lake setting. Its light thread moves above the faces and softens during reading.
- The nine swirling light trails flow into Earth. Each comet joins its expression symbol's three-dimensional orbit. The symbols pass around the globe, then the world becomes the official logo and leads into the pastel closing card.
- The original eight-song Film 10 medley and strong final musical accent are retained. This is not the earlier seven-song masterpiece edit. The score is byte-identical to Revision 2.
- Both the master and the phone copy are native 60 fps. No paid service was used.

## Exact source and references

- Approved delivery commit: `46df53b98a43f58e51a78d40ee5794108a68e13c`.
- Saved tag: [`film10-revision3-approved-2026-11-16`](https://github.com/lovelaceaml-hub/concert-backdrops/tree/film10-revision3-approved-2026-11-16).
- Implementation branch: `creative/nine-colours-spiral-and-expression`.
- Implementation: [draft PR #71](https://github.com/lovelaceaml-hub/concert-backdrops/pull/71), based on Revision 2 draft PR #70 (`creative/nine-colours-opening-and-world`, commit `3c88a7942c381d07e77d1ff9f89dfb920200910d`). Neither is merged.
- Original Film 10 render 1: commit `d928ff9eafe02ac3150f0c646bdcc497fe5a7278`, run `43726203825`.
- Claude Nine Colours Final v1 reference: commit `f43f4514e4bc42dc25166e90160d98219f5a0db4`, run `43855882765`, share artifact `14222872749`.
- Coordination: [PR #55 thread](https://github.com/lovelaceaml-hub/concert-backdrops/pull/55).

Only `tools/nine_colours_minor/` contains implementation changes. The original engine and selected Claude components are restored to private, pinned snapshots under `work/`. No protected song, master, acting, music or workflow source was edited. No generated media, caches or audio features are committed. The render ran in the cloud execution workspace; the paid GitHub Render workflow was not triggered.

## Validation and known scope

All 28 sampled raw 1080p frames are pixel-identical in fresh forward and reverse processes. Both encoded copies have zero adjacent repeated frames, exact 60 fps timing, and 66.000-second video/audio duration. Full-film sheets, dense Respect/Earth/card sequences and native 1080p/720p frames were visually inspected. The master measures -12.94 LUFS integrated and -2.68 dBTP. Its final quarter-second is -49.35 dBFS RMS, retaining the strong accent and then releasing quietly.

This is a creative revision, not a claim of identical pixels to an earlier video. Original fast flight and medley joins remain. Five original joins have quarter-second level changes above 3 dB, documented rather than silently remixed. Approval preserves this cut; it is not a claim that every earlier issue across other versions is resolved.

Reproduction and measurements are pinned with the source: [README](https://github.com/lovelaceaml-hub/concert-backdrops/blob/film10-revision3-approved-2026-11-16/tools/nine_colours_minor/README.md), [VALIDATION](https://github.com/lovelaceaml-hub/concert-backdrops/blob/film10-revision3-approved-2026-11-16/tools/nine_colours_minor/VALIDATION.md). Private generated evidence is under `work/nine_colours_revision3/`; local exports are under `out/nine_colours_revision3/`. These local folders are rebuildable working data. The approved uploads and source tag are the durable delivery record.

## Continue from this version

Start from the approved tag on a new branch. Read this record and the latest handbook before changing anything. Preserve the approved videos and use a new revision name for further changes. Do not start new renders or paid services just to archive this version. Never merge on the owner's behalf.
