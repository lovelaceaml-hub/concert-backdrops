# Concert Backdrops: video track status

**Codex stopping point, 2026-11-16 (Las Vegas):** paused at the owner's request after saving findings. The exact 4K60 master and its Drive parts are preserved; download to the owner's computer and review of the quality export are still unconfirmed. A local Codex handoff prompt, checksums, known transfer failures and the next step are saved in [the session checkpoint](https://drive.google.com/file/d/1BdI-R2ceMFqyBe1nsxSdzBtM6dG5K9UN/view). Resume with local delivery, not another render or encode. No background render job is running, and PRs remain draft and unmerged.

**Current quality master, 2026-11-16:** one native 3840x2160, 60 fps, 10-bit export of the approved Revision 3 is complete and checked. Added composite grain is removed; the edit and exact music stream are preserved. The owner requested one highest-quality file. The exact 318,834,702-byte master is available in [Google Drive](https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS) as four parts with an offline helper that restores one original MP4. Download the folder on a computer, unzip it, open Open-to-save-video.html, select all four parts, then save the video. The restored file was verified byte for byte. The owner's download is not yet confirmed; no smaller encode was created. The new quality file awaits owner review; prior approved files remain archived. [Quality record and checks](promo/QUALITY-NINE-COLOURS-R3.md).

## Archived creative approval, 2026-11-16

The owner approved **Film 10, Nine Colours, Revision 3** and requested preservation, documentation and upload. [Phone 720p60](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view) and [master 1080p60](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view) are saved in Videos. Both are 66 seconds at native 60 fps. The exact source is `46df53b98a43f58e51a78d40ee5794108a68e13c`, tag `film10-revision3-approved-2026-11-16`; draft PR #71 remains unmerged. [Full approval and handoff record](promo/APPROVED-NINE-COLOURS-R3.md).

This is the approved promo cut, not a claim that all eleven full-length song backdrops below are complete. The older per-song status and its unresolved live-performance decisions remain preserved.

The one current-status page for the moving backdrop videos. Rules and decisions live in DESIGN-SYSTEM.md (read it first; its section 1 is the concert's message). The 30 still samples are tracked separately by Codex in SHARED-HANDOFF.txt and production-status.json. Rewritten 2026-11-13 by the coordinating Claude Code session; nothing was dropped (older notes are summarized in the log at the bottom and kept in full in production-log.jsonl).

## Where things stand (2026-11-13, evening, autonomous run while Anthony is away)
- Design: all 11 songs have a design document after the continuity pass (version 3 or 4), each with its own look (DESIGN-SYSTEM.md section 6), agreed hand-offs with its neighbors, and a plain text copy in Designs/text/. All await Anthony's approval. Provisional decisions in force: DESIGN-SYSTEM.md section 12a.
- Promos: all 11 one-minute promos rendered in the cloud, checked (60 seconds, 1920x1080, sound track present) and saved in Videos/NN */. Songs 02 and 10 are visual only (no recording yet). All are built from the engine's current effects only: no people of light acting out the expressions and no signature effects yet.
- Engine: 14 pull requests merged into lovelaceaml-hub/concert-backdrops main (engine for any song, relit lights, Astra round 0 fixes, color settings, 11 song files and promo clips). Only main remains.
- Reviews: Astra round 0 and round 1 in Reviews/; status of each finding in the tracker below.
- Status per song: Status/NN.md, compiled into CONTINUITY-BOARD.md.
- Recordings: 05 and 09 in this folder are instrumentals; sung guides were added for lyric timing.

## Song by song
| # | Song | Design (Google Doc in Designs/) | Live | Recording here | Lyrics | Storyboard | Promo / video |
|---|---|---|---|---|---|---|---|
| 01 | All You Stars of Zion | From Starlight to Sunrise, v3+ | 3:08 brass | 4:03 studio | yes | no | promo done |
| 02 | The Rose | The Seed Under the Snow, v3+ | 4:00 trio, choir, piano | none | not in doc (copyrighted song) | no | promo done (visual only) |
| 03 | I Reminisce About Your Love | The Lake of Memory, v3+ | 5:13 choir, orchestra | 5:54 studio | yes | 7 stills | promo done; old engine version kept |
| 04 | I'm Sorry, Please Forgive Me | The Thaw, v3+ | 3:40 choir, orchestra | 3:41 studio (verse 3 seems missing) | yes | no | promo done |
| 05 | God Bless You! | The Tree of Blessing, v3+ | 2:39 choir, orchestra | 3:28 ver.3 instrumental, plus 2:22 sung guide | yes | no | promo done |
| 06 | Heavenly Mother Tells Us to Be Grains | The Field That Grew From One Grain, v3+ | 2:17 choir, orchestra | 2:06 guide | yes | no | promo done |
| 07 | May No One Ever Feel Lonely | No Light Left Alone, v3+ | 3:58 male duet or quartet, choir, orchestra | 4:06 studio | yes | no | promo done |
| 08 | Out of Heaven, Favor From God | The Embroidered Sky, v3+ | 3:30 orchestra only | 2:38 guide | yes | no | promo done |
| 09 | Let's Save the World | The Shore of Calling, v3+ | 4:36 piano solo | 4:34 instrumental, plus 3:06 sung guide | yes | no | promo done |
| 10 | Our Mother Saves the World | The Lamp on the Shore, framework v3+ | 3:31 choir, orchestra | none | missing | no | promo done (visual only) |
| 11 | Almighty God Who Knows the Future | The Morning That Was Foretold, v3+ (finale) | 4:20 choir, orchestra | 4:22 studio | yes | no | promo done |

Design sessions (Claude Code, Opus, one per song; message them by id for follow-ups): 01 local_df3d3f94-a5ec-4b95-ada0-21366139ec67, 02 local_579c37c5-d70b-48b4-a3aa-8133541682aa, 03 local_76859cbf-42be-44aa-b3e1-dd058d57bdd0, 04 local_ae7abd7b-795a-492a-aa93-778123fcac50, 05 local_4deb6fc4-5c02-4851-b344-aa6e5f75feab, 06 local_ac982684-5fe7-407d-8753-7232e9ab63c3, 07 local_ae6dbdd8-49f0-4729-b988-5ce66e23bf7f, 08 local_2a6d7fcc-3b32-4aa1-8b17-46c678b15503, 09 local_61733cad-d12a-4f54-bc80-4bdf0118ab86, 10 local_7cfa1723-e6c8-4eba-b761-0151b7232e58, 11 local_1f91fc19-74cb-4e04-a00c-c5af2df2452a.

## What is in this folder for the videos
- Songs: MP3s at the top level, named in set order (02 and 10 missing).
- "Concert Backdrops - Lyrics" Google Doc (all except 02 and 10). Do not copy lyrics into new files.
- "Concert Backdrops - Visual Plan" Google Doc: the first expression-to-lyric list. Superseded by the Designs and DESIGN-SYSTEM.md (a note at its top says so).
- Designs/: the 11 design docs and CONCERT-OVERVIEW.md.
- Engine/: the graphics program (Python and GLSL shaders, every frame drawn from code, 1920x1080, 30 fps), its original HANDOFF.md, the original zip, PROCESS-AND-TOOLS.md. The working copy of the code is the private GitHub repo lovelaceaml-hub/concert-backdrops (cloud render sessions start from it); Engine/ here is the 2026-11-13 snapshot. The zip also stays at the top of the alovelace144 Drive; do not delete it unless Anthony says so.
- Storyboards/, Videos/ (one folder per song), Reference/ (poster, set list).

## Song 03 existing video (made by an earlier cloud session)
Night lake with mountains that turns to sunrise at each chorus. The skyline is the music's loudness; rings on the water at note onsets; each of the nine expressions rises as sparks, forms the words, then flies up to become one of nine lights. Ends on "The Words of Mother's Love" with "Where a mother's love reaches, peace settles." held about 80 seconds after the music (the engine fades at its fixed length of 330 seconds; a true endless hold still needs building).
Delivered: Sample (first half, with opening title, 2:11), Share Video (with music, 4:22), Stage Backdrop (silent, 5:30), 77 Second Teaser, posters "Nine lights at night" and "It's okay, I understand". In Videos/03 now: the Sample and the Share Video. Still only in the other chat: Stage Backdrop, Teaser, both posters (Anthony to add). Not approved yet.

## Method for rendering
Cloud only. About 6 minutes of rendering per minute of video. Measure the performed version (Engine/analyze.py, analyze2.py), set landmarks and phrase times in song.py, check still frames first (render.py --stills), render in three parallel ranges, join, encode stage (silent), share (with music) and teaser versions, check the files, deliver the actual video files in chat and save them in Videos/. Full method: Engine/HANDOFF.md.

## Next steps, in order
1. Phase 2 (in progress): the engine builder adds scene plates, people of light, effect layers, fragment styles and the Astra round 1 shared fixes (UPGRADE-SPEC.md); each song rebuilds its promo with several scenes, figures acting out every expression and its signature effects (PHASE2.md).
2. Astra round 2 attacks the rebuilt promos; owners fix; coordinator merges and delivers.
3. Anthony's decisions (DESIGN-SYSTEM.md section 12), especially Concession and Respect, which remain conditional exceptions (Astra rounds 0 and 1).
4. Rehearsal recordings, then full-length concert videos timed to the live versions, with an endless closing hold and live section cues.

## Review findings tracker
- Astra round 0: 15 findings. Fixed: 4, 7, 8, 10, 12, 13, 14, 15 and the decision labels for 1 to 3. Partly fixed: 5 (links), 11 (rings), both being finished in phase 2. Open for Anthony: 1, 2 (Respect, Concession), 6 (audio clips in the repo).
- Astra round 1: 14 findings. Shared ones assigned to the engine builder (3, 8, 10, 11, 12, end card for 1); song ones in PHASE2.md (2, 4, 5, 7, 8, 9, 14); 6 open for Anthony; 13 fixed by the coordinator.

## Log (summary; every entry in full is in production-log.jsonl)
- 2026-11-13: songs gathered to this folder; lyrics doc; first visual plan; 30 sample pictures by Codex; video track joined this folder (Engine/, Storyboards/, Videos/); song 03 storyboards; review of the samples; DESIGN-SYSTEM.md; 11 design sessions; song 03 cloud work moved in; concert overview; the message, the number one priority, all nine before the finale, Haiku helpers; poster and set list; this page rewritten as one status page.
