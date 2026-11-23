# Song 07 May No One Ever Feel Lonely: status (backdrop v2)

For the coordinator to copy to Drive Status/07.md.

## Board fields
- Live length: 3:58 (238.0 s), male duet or quartet, choir and orchestra. Stage video 253.0 s (music 238.0 s + 15 s calm hold), 1920x1080, native 60 fps, 15,180 frames. Timed to the church's recording (youtu.be/7piuHaCYnFM, 246.53 s) conformed evenly to 238.0 s: an estimate until a rehearsal recording exists.
- Stars lit at start: 3, 4, 5, 6, 7, 8, 9 (1 and 2 dark).
- Lit in this song: star 1 Greeting, lit for the first time in the concert (1:03.3); star 8 Consideration relit with a brief flare and one new thin ring (1:16.0).
- Stars lit at end: 1 and 3 to 9 (2 Gratitude dark, for song 08).
- Opening frame: song 06's warm amber evening (low gold light, camera low and wide at the near shore, arch 3 to 9) with the opening card (logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace, May No One Ever Feel Lonely), cooling into blue dusk over 12 s.
- Closing frame: deep navy night lake (#0B1530 at the top of the sky), perfectly still, warm horizon star at the centre, camera wide at eye level just above the water, arch 1 and 3 to 9 lit, star 2 dark, signature top left, nothing carried (the gate has faded out). Song 08 opens on it.
- Branch backdrop2/s07-full (from tag film10-revision3-approved-2026-11-16); code tools/s07_full2/; docs project-docs/backdrops/s07-full2/ (TIMELINE.md, CUES.md, CHECKLIST.md).

## Log
- 2026-11-18: v2 started after Anthony's "Just do a new one". Read the Drive rule files (AGENTS, DESIGN-SYSTEM, VIDEO-HANDOFF, AUTONOMOUS-RUN, CONCERT-OVERVIEW, Status/07, PHASEB through Update 25, PROJECT-HANDBOOK) and the song 07 design.
- Audio downloaded from Drive outside the repo (SHA-256 checked); measured again (sections and hits agree with the first run within 0.1 s except two hits, corrected); conformed 0 to 243.5 s onto 238.0 s.
- Built a new song module on the first run's scenes with every v2 fix: 60 fps, live length plus 15 s hold, no comets (first stars instead), the opening card and the top-left signature, website colours, Greeting acted by two men each giving a slight bow, Consideration acted as helping a man up from one knee, symbols in the sky and hearts in the expression colours, the arch held in one place in the picture so no star ever passes behind the signature, the bottom third kept calm (the first run's people in the lower third from 1:38 to 2:17 fixed), no white-outs.
- Stills checked in four rounds (contact sheets at half size, read at full and quarter size); layout checked every 0.25 s by check_layout.py.
- Full render in this cloud session (16 parts on 4 cores). No GitHub Render workflow, nothing paid, nothing on the Mac.
- 2026-11-19: Full render done and checked (verify.py on all three files): exactly 253.000 s, 15,180 frames at 60 fps; no black, repeated or frozen frames; no white-out (at most 1.4 % near-white pixels); signature present on every frame after the opening; audio peak -1.4 dBFS, silent hold; sync within 0.06 s on hits 52.2 and 226.4 s (the 127.6 s hit has a near-equal neighbour attack in the encode). The first render showed Heavenly Mother in the bottom third during the search, so the camera was lowered and those parts rendered again (check_people.py now checks every person's feet every 0.25 s).
- Delivered set (in this cloud session, not in git):
  - stage `07 May No One Ever Feel Lonely - Backdrop v2 - stage 1080p60.mp4` SHA-256 2ae667a714d65bf68c458161a1f8b4840bbbc3b8262d5fd1d99b278c175622bb
  - review `... - review 1080p60.mp4` SHA-256 7f87fcc6e503e2bd919716099d0b2cfee914985a3e47887c87e7e071fcef9996
  - phone `... - phone 720p60.mp4` (22.2 MB) SHA-256 77604c4275fff5036c3a468423eea7e38ae098538ac1ab0092728db7d8df162d
- Stopped here on Anthony's instruction to all concert chats (relayed by the song 11 session): completed video in hand, no new revisions. Known weak point in this set: from 1:09 to 1:14 the traveler's head touches the bottom of "with anything?" (Consideration stays readable). A fix (camera farther back, commit 57b2714) is on this branch but was NOT rendered, so the branch code is one commit ahead of the delivered video; render parts 3 to 5 (frames 2847 to 5694) to apply it. Contact sheet, Drive upload and the draft PR were not done.
