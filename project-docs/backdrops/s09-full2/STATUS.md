# Song 09 "Let's Save the World": backdrop version 2 status

Delivered 2026-11-18; fix 1 delivered 2026-11-19. Rendered only in this cloud session (no Render workflow, no paid service). Supersedes the first run (branch `backdrop/s09-full`).

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
| 09 Let's Save the World - Backdrop v2 - stage 1080p60.mp4 (silent, H.264 CRF 16, yuv420p, faststart) | 194,685,985 bytes | 9056bad49e853be44f9f2333842c931787422407dde158722d6222e05e8be378 |
| 09 Let's Save the World - Backdrop v2 - review 1080p60.mp4 (reference music untouched, AAC, CRF 20) | 111,835,133 bytes | ffb26d69b640663bfd2a116ec577c5e1ec4502609e83ab3aae8275e06ff78297 |
| 09 Let's Save the World - Backdrop v2 - phone 720p60.mp4 (with music, two-pass) | 24,634,574 bytes | b96d61f32813d952eb7943ece7bee82419da8e1ab84e259c16a037549e4a205e |
| 09 backdrop v2 stills fix1.jpg (20 labelled landmark stills, new file in Drive "Concert Backdrops - Songs/Status"; the first sheet is kept) | 359,626 bytes | 172649ca4966444e26b320031f71ab3a1aa14db65a413bab5bd0d99e1716be6b |

## Render checks (tools/s09_full2/verify.py)

| Check | Stage | Review | Phone |
|---|---|---|---|
| Frames / duration | 17,460 / 291.0 s | 17,460 / 291.0 s | 17,460 / 291.008 s |
| 60 fps, size | 1920x1080 | 1920x1080 | 1280x720 |
| Black frames | 0 | 0 | 0 |
| Repeated neighbour frames | 1 (3:38.27, see below) | 1 (same frame) | 38 (encoder holds in the quietest passages) |
| Longest near-frozen run | 2 frames | 3 frames | 30 frames (0.5 s, under the 1 s limit) |
| Darkest / brightest frame mean (0 to 255) | 125 / 174 | 125 / 174 | 125 / 174 |
| Signature present on every frame after the opening | yes (0 missing) | yes (0 missing) | not measured (720p) |
| Sync at 0:59.5, 2:28.8, 4:02 | silent | 0 ms each | 0 ms each |
| Silence after the music | n/a | yes | yes |

verify.py reports ok false for all three files after fix 1, for one reason in stage and review: frames 13095 and 13096 (3:38.27, the first two frames of part 18) differ by a mean of 0.018 of 255, just under the 0.02 repeat limit (before fix 1 the smallest change was 0.0204). The frames are distinct renders, the difference cannot be seen, and the engine is deterministic, so a re-render gives the same frames; the fainter shore removed a little movement from this quiet moment. The coordinator accepted it with no re-render (2026-11-19). The phone copy also holds a few blocks still at under 25 MB; it is a preview copy only.

## Motion strips

Looked at at 5 fps around every word arrival and departure (1:21.5, 1:53.5, 2:35.5, 2:56.5, 3:07.5, 3:49.5) and the net cast. Letters form cleanly and hand over to navy; the Encouragement collapses into star 7 without letters breaking apart on screen for more than a moment. One fault found and fixed before delivery: the cast net flew up as a large soft white blob (3:49 to 3:51); it is now a faint gold bundle that opens into the mesh (parts 18 and 19 re-rendered).

## Fix 1 (coordinator notes, 2026-11-18)

1. The Encouragement (3:02 to 3:12) is now navy #1f2a6b with a soft white glow, drawn exactly over the particle letters; the navy stays until the letters have broken up (fade 3:08.5 to 3:09.6), so cream letters never sit whole on the pale sky.
2. The camera at the Encouragement is raised so the pair stands below the reading box (heads at about 0.55 to 0.63 of the frame height).
3. The gold line of grains on the shore (about 55% down, from 1:25) is dimmed to faint and no longer flickers.
4. The signature's last line (HEALING CONCERT · LAS VEGAS) is navy.

The signature is on screen from 7.9 s, so the whole film was re-rendered, then part 15 again for the later navy fade. Motion strips at 1 fps over 2:55 to 3:11 and 5 fps over 3:08 to 3:10.4 checked.

## Log

- 2026-11-18: brief received; branch from tag film10-revision3-approved-2026-11-16; reference measured 275.736 s (used as is).
- Stills rounds: comets removed, night brightened to twilight, signature moved top left, white-out at 0:59.5 removed, bottom third calmed, people reflections removed, net redrawn as a cast diamond mesh.
- Full render in this session (24 parts, 4 workers), then parts 18 and 19 re-rendered for the net fix; phone copy re-encoded two-pass.
- Delivered stage, review and phone files; contact sheet uploaded to Drive Status as a new file.
- 2026-11-19: fix 1 (four coordinator notes) re-rendered in this session, verified, files sent again; "09 backdrop v2 stills fix1.jpg" uploaded to Drive Status as a new file.

## Weak points

- One near-repeated frame pair at 3:38.27 (invisible; below the automatic check's limit).
- With the camera raised, the pair's feet reach into the top of the bottom third during the Encouragement.

- The ending is a warm low rose-gold sun, not the agreed deep blue dusk hand-off to song 10 (never dark); song 10 should open on the warm sun.
- Distant people (saints, the waking world) are small and pale at stage distance.
- During formation the particle words show broken letters for about half a second before they settle.
- Timing follows the reference recording until a rehearsal recording exists.
