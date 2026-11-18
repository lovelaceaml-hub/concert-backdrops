# Song 09 "Let's Save the World": backdrop version 2 status

Delivered 2026-11-18. Rendered only in this cloud session (no Render workflow, no paid service). Supersedes the first run (branch `backdrop/s09-full`).

## Board fields

| Field | Value |
|---|---|
| Stars lit at the start | all nine |
| Stars lit at the end | all nine; star 7 (Encouragement) relit with a brief flare and one new thin ring at 3:10 |
| Opening frame | song 08's closing look: still rose-gold dawn lake, wide eye level, full arch, no people, with the opening lockup (logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, "Let's Save the World") readable from frame 0 |
| Closing frame | the calm mirror morning: boats with a figure at each bow, faint city of light, full arch, warming to a low rose-gold sun; signature top left |
| Live length | 4:36 (276.0 s) of music plus a 15 s calm hold = 4:51 (291.0 s, 17,460 frames at 60 fps) |

## Files (not in git; sent to Anthony in the session; stills in Drive Status)

| File | Size | SHA-256 |
|---|---|---|
| 09 Let's Save the World - Backdrop v2 - stage 1080p60.mp4 (silent, H.264 CRF 16, yuv420p, faststart) | 195,447,050 bytes | a197e04ad6e2dc12d22360b2ee162b8d4ad62590397766727d267a19aee5160d |
| 09 Let's Save the World - Backdrop v2 - review 1080p60.mp4 (reference music untouched, AAC, CRF 20) | 112,229,497 bytes | 6ffdf40fa4de923d8df9bfc04b7c2dd20f2caa9fc3f54e18a808e9ed335c6cf9 |
| 09 Let's Save the World - Backdrop v2 - phone 720p60.mp4 (with music, two-pass) | 24,631,315 bytes | 4611aabb2e48ae7738ba48ecd0c8781ce84fbd392179ae51f418f425c10d6ea4 |
| 09 backdrop v2 stills.jpg (18 labelled landmark stills, Drive "Concert Backdrops - Songs/Status") | 475,896 bytes | af5493769ab992518b675b64754e01fa29f68214d7985ec14c74cc1b2b97e907 |

## Render checks (tools/s09_full2/verify.py)

| Check | Stage | Review | Phone |
|---|---|---|---|
| Frames / duration | 17,460 / 291.0 s | 17,460 / 291.0 s | 17,460 / 291.008 s |
| 60 fps, size | 1920x1080 | 1920x1080 | 1280x720 |
| Black frames | 0 | 0 | 0 |
| Repeated neighbour frames | 0 | 0 | 33 (encoder holds in the quietest interlude near 2:11) |
| Longest near-frozen run | 2 frames | 3 frames | 35 frames (0.6 s, under the 1 s limit) |
| Darkest / brightest frame mean (0 to 255) | 125 / 174 | 125 / 174 | 125 / 174 |
| Signature present on every frame after the opening | yes (0 missing) | yes (0 missing) | not measured (720p) |
| Sync at 0:59.5, 2:28.8, 4:02 | silent | 0 ms each | 0 ms each |
| Silence after the music | n/a | yes | yes |

The phone copy is the only file that does not pass every automatic check: at under 25 MB the encoder holds a few blocks still in the slowest calm passage. It is a preview copy only; the stage file is clean.

## Motion strips

Looked at at 5 fps around every word arrival and departure (1:21.5, 1:53.5, 2:35.5, 2:56.5, 3:07.5, 3:49.5) and the net cast. Letters form cleanly and hand over to navy; the Encouragement collapses into star 7 without letters breaking apart on screen for more than a moment. One fault found and fixed before delivery: the cast net flew up as a large soft white blob (3:49 to 3:51); it is now a faint gold bundle that opens into the mesh (parts 18 and 19 re-rendered).

## Log

- 2026-11-18: brief received; branch from tag film10-revision3-approved-2026-11-16; reference measured 275.736 s (used as is).
- Stills rounds: comets removed, night brightened to twilight, signature moved top left, white-out at 0:59.5 removed, bottom third calmed, people reflections removed, net redrawn as a cast diamond mesh.
- Full render in this session (24 parts, 4 workers), then parts 18 and 19 re-rendered for the net fix; phone copy re-encoded two-pass.
- Delivered stage, review and phone files; contact sheet uploaded to Drive Status as a new file.

## Weak points

- The Encouragement phrase is cream on a mid teal sky: readable, but not high contrast.
- The ending is a warm low rose-gold sun, not the agreed deep blue dusk hand-off to song 10 (never dark); song 10 should open on the warm sun.
- Distant people (saints, the waking world) are small and pale at stage distance.
- During formation the particle words show broken letters for about half a second before they settle.
- The fourth signature line (HEALING CONCERT · LAS VEGAS) is gold and faint on the brightest skies.
- Timing follows the reference recording until a rehearsal recording exists.
