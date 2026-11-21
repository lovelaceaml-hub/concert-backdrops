# 03 I Reminisce About Your Love: status (backdrop v2)

For the coordinator to copy into Drive Status/03.md.

- Live length: 5:13 (313.0 s). Stage video: 5:28.00 (328.000 s) = the live length + a 15 second calm hold. 1920x1080, 60 fps, 19,680 frames.
- Stars lit at start: 7 and 9 (7 with its ring from song 02).
- Stars lit in this song: lights 3 (Apology, 0:40.6); relights 7 (Encouragement, 3:57.0, a brief flare and one new thin ring).
- Stars lit at end: 3, 7, 9.
- Opening frame: the home night lake from song 02 (deep indigo, a rose-violet glow on the horizon, the home star just left of centre, arch 7 and 9), with the opening lockup whole on frame 0: the campaign logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, "I Reminisce About Your Love" large (held to 0:08.6).
- Closing frame: the rose dawn lake, the sun over the mountains where the home star rested, the pale moon upper right, rose petals, arch 3, 7, 9 (3 slightly brighter), the signature top left; no other text. This is song 04's opening.
- Timing: the reference upload (5:55.1) fitted to 5:13 by removing one repeated passage of chorus 2 (4:32.74 to 5:14.79, 42.05 s, on the beat; nothing sped up). An estimate until a rehearsal recording exists (TIMELINE.md, CUES.md).
- Expressions: APOLOGY readable 0:28.6 to 0:38.0 (acted by two women of warm gold light: a hand laid gently on the back of one sitting with her head bowed); ENCOURAGEMENT readable 3:44.4 to 3:53.8 (two women: one kneeling in prayer, the other's hand on her shoulder). Fragments: "engraved deep in my heart", "Her warm hands", "I love You Mother".
- Files (attached in the coordinator chat; never in git):
  - "03 I Reminisce About Your Love - Backdrop v2 - stage 1080p60.mp4": silent, H.264 CRF 16, 199.2 MB, SHA-256 7c389faf8b5e6cbc14fd53d9d6058149fd7e9bb113be55535a4014aa3bff7f25 (fix 1)
  - "03 I Reminisce About Your Love - Backdrop v2 - review 1080p60.mp4": with the conformed reference music, AAC 320k, CRF 20, 120.3 MB, SHA-256 c8832427d55953c383e6f9b9f9a20fbc8b29944ed8322f8c7aed2aed071d2403 (fix 1)
  - "03 I Reminisce About Your Love - Backdrop v2 - phone 720p60.mp4": with music, 23.5 MB, SHA-256 f7437ad64798e83d8819f2792b26aadef3966fb527941f312721f4b9ed7a529e (fix 1)
  - Contact sheets: Drive Status/"03 backdrop v2 stills.jpg" (first delivery) and "03 backdrop v2 stills fix1.jpg" (fix 1, new file; 15 stills with times).
- Checks (tools/s03_full2/verify.py): all three files 19,680 frames, 328.000 s, 60 fps; no black frames (darkest frame mean 32 of 255); no identical consecutive frames; longest near-still stretch 0.02 s; brightest pixel 251 (no white-out); the signature present at every whole second from 0:12; music in sync at 0:26.63, 3:01.35 and 4:02.21 (0.0 ms).

## Log

- 2026-11-18: version 2 built from the tag film10-revision3-approved-2026-11-16 after reading the Drive rule files. Reference measured and conformed to 5:13. Scene module on the pinned engine (plates of this song only, no comets, compact arch clear of the signature); 3D people pass with the tag's acting.py; overlay with the opening lockup, signature, expressions, symbols, hearts and the three fragments. Stills checked at about 40 landmarks over four rounds (fixes: a raised shin outside a gown; a glowing hem ring; the comforter standing up into the words; doubled letters while leaving; the sparks streaming like a comet; the Encouragement pair lost in the prayer column; rings and bright reflections in the lower third). Motion strips at 12 frames a second through the opening, both expressions' arrival and departure and all three fragments. Full render in this session (24 parts on 4 cores, about 70 minutes), delivered and checked.
- 2026-11-18, fix 1 (coordinator notes from the contact sheet): (1) under the mended moon (1:34 to 2:58) the rings painted on the plate's water are stilled below two thirds of the frame; (2) the Apology and Encouragement symbols are no longer line drawings that read as icons: each is a faint constellation in its colour (#F6CE46, #9E6AF6), traced by one spark, stars joined by hair-thin lines. Re-rendered only the 11 parts these touch (frames 1640 to 2460, 4920 to 11480, 13120 to 14760), rejoined, re-encoded; verify.py passed again (19,680 frames, 328.000 s, no black or repeated frames, signature every second from 12 s, sync 0.0 ms at three hits). The three files were sent again.
