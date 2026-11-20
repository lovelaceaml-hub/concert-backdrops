# Handoff: full-length concert backdrops (start locally)

Written 2026-11-18 by a Claude Code cloud session, at the owner's request ("Give me handoff to start locally"). Nothing has been built or rendered for this phase yet. Read this whole file, then the files it points to, before starting.

## 1. The task

The promo is finished (Film 10, Nine Colours, Revision 3, approved 2026-11-16). The owner now wants the **backdrop videos for the live performances** of the concert on Sunday, December 6, 4:30 PM (The World Mission Society Church of God, 6720 W Sahara Ave, Las Vegas).

Song list: Google Doc "LV 12/6 Concert", id `1QqIlOkc0JnPj8Zyy2TYA0OMmMj9-Tonksg3Ngi01rJ0`. It has 12 items. Item 1 is an existing sing-along video. Items 2 to 12 are the same 11 songs that already have design docs in `project-docs/designs/` (numbered 01 to 11 there), now with new reference links and notes:

| Doc item | Song (repo number) | Reference link in the doc | Note in the doc |
|---|---|---|---|
| 2 | 01 All You Stars of Zion | youtu.be/YuBYZDgmf0I | Introduction: our heart to shine Mother's glory to the earth |
| 3 | 02 The Rose | Drive 1UoGwToBnpl-jlEJDRfqMnHMfluupGOhO | Love hidden like a seed in winter, blooms again |
| 4 | 03 I Reminisce About Your Love | youtu.be/TH_p9g7Eu30 | Mother prayed, encouraged, comforted first |
| 5 | 04 I'm Sorry, Please Forgive Me | youtu.be/43seZJ9fTgw | Choir only, a cappella variation; expressions 3, 2, 4 |
| 6 | 05 God Bless You! | Drive 1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D | Expressions 7 and 8 |
| 7 | 06 Heavenly Mother Tells Us to Be Grains | Drive 1YqFkD3lQprvotC32xRfC8Dqno0I24hqs | (no note) |
| 8 | 07 May No One Ever Feel Lonely | youtu.be/7piuHaCYnFM | Mother's wish that no one is lonely |
| 9 | 08 Out of Heaven, Favor From God | youtu.be/veJ7ra4Fjck | Orchestra only |
| 10 | 09 Let's Save the World | youtu.be/O_Ym8-sy9xo | Piano solo |
| 11 | 10 Our Mother Saves the World | Drive 1NbsvsPQO_wMWEl9OzJNFH6ZQAs_qg6WG | Mother's love embraces the whole world |
| 12 | 11 Almighty God Who Knows the Future | youtu.be/tdiD_qDWuWI | Gratitude and hope, move forward together |

Songs 02 and 10 now have audio links (before, they had no recording).

## 2. Owner decisions (2026-11-18)

1. **Pilot first:** build one full-length backdrop, **All You Stars of Zion**, get approval, then do the other 10.
2. **Look:** the approved promo style, Nine Colours Revision 3 (warm gold glitter people, cream Cormorant serif phrases with colored capsule labels, nine colored comets, warm heavenly light), applied to the song's existing design (`project-docs/designs/01 All You Stars of Zion.md`: starry night lake turning to a golden sunrise, Compliment in verse 1, Encouragement at the last chorus, "Arise" from the lake, arch of nine lights).
3. **Playback:** one continuous video per song (not operator-cued sections).
4. **Timing audio:** the YouTube version, youtu.be/YuBYZDgmf0I. Not the 4:03 studio MP3 in Drive. Note the design doc says live is about 3:08 brass, no singing; check the YouTube length and say how it compares.
5. **Render:** 30 fps, 1920x1080 (DESIGN-SYSTEM.md stage spec), split across parallel cloud machines.
6. **Item 1** (sing-along video): nothing to make; it plays as is.

## 3. Blocker: the audio

The cloud session could not get the audio:
- Drive connector returns files as text; a 5.9 MB MP3 is too large. drive.google.com direct download needs the file shared by link.
- YouTube refused cloud downloads ("Sign in to confirm you're not a bot"). Bypass attempts were blocked as unauthorized; do not try to defeat YouTube's protection.

**Locally:** the owner saves the audio of youtu.be/YuBYZDgmf0I by an allowed means (for example, from a copy the church already has), then:
- Do NOT commit the full song (AGENTS.md: only short clips under `audio/`). Whether a full song may go to `audio/` for the cloud render is the same open question as Astra round 0, finding 6; ask the owner.
- Safer route: put the file in Drive "Concert Backdrops - Songs" and share it by link, so a cloud render machine can download it.

## 4. What is verified to work (cloud, 2026-11-18)

The Revision 3 renderer runs on a CPU-only Linux machine:

```sh
git fetch origin ten/10-nine-colours tag film10-revision3-approved-2026-11-16
git fetch origin f43f4514e4bc42dc25166e90160d98219f5a0db4
git worktree add ../r3 film10-revision3-approved-2026-11-16
apt-get install -y libegl1 libgles2 libgl1-mesa-dri libegl-mesa0 ffmpeg
pip install numpy scipy librosa moderngl pillow fonttools brotli soundfile
# fonts, as in .github/workflows/render.yml
npm pack @fontsource/cormorant-garamond @fontsource/jost @fontsource/outfit  # unpack each .tgz
python tools/setup_fonts.py <unpacked dir> fonts
cd ../r3 && ln -s ../concert-backdrops/fonts fonts
python tools/nine_colours_minor/prepare.py
python tools/nine_colours_minor/render.py --stills 20,43 --outdir <dir>
```

Measured speed: **about 12 CPU seconds per 1080p frame** (software OpenGL). Pilot estimate for a 3 to 4 minute song at 30 fps: 5,600 to 7,300 frames, about 6 hours on one 4-core machine, about 1 to 2 hours split across 4 to 6.

Rule: **render only in the cloud, never on the Mac** (AGENTS.md). Locally, write code, check small stills at low scale only if the owner allows, and send the full render to the cloud (the Render workflow in `.github/workflows/render.yml`, or cloud sessions). Earlier records treat the GitHub Render workflow as paid; get the owner's OK before dispatching it.

## 5. Where the building blocks are

- Approved promo source: tag `film10-revision3-approved-2026-11-16`, folder `tools/nine_colours_minor/` (render.py layers Claude Final v1 words, cards, finale and Respect over the pinned Film 10 engine). Record: `project-docs/promo/APPROVED-NINE-COLOURS-R3.md`.
- Pinned engine: commit `d928ff9` (branch `ten/10-nine-colours`). It contains `engine/songs/ten_10_nine_colours.py` (the 60 s film, 42 KB, good model for camera, comets, particle people and words) and `engine/songs/s01_stars_of_zion.py` (the older 60 s Stars of Zion promo v2: scenes, timings, torch bearers, Encouragement).
- Claude words, bodies, symbol orbits: commit `f43f451` (`engine/p3d/words.py` and friends).
- Song design and status: `project-docs/designs/01 All You Stars of Zion.md`, `project-docs/status/01.md` (section timings measured from the studio recording; they must be re-measured on the YouTube audio with `engine/analyze.py`).
- Owner rules for look and people: `project-docs/promo/PROJECT-HANDBOOK.md` section 4 (warm, never dark; gold glitter people only; same-gender touching except parent and child; refined natural movement; no faces in detail, no realistic faces).

## 6. Suggested plan for the pilot

1. Get the audio (section 3). Measure it: length, sections, loud hits.
2. New branch from the approved tag, e.g. `backdrop/s01-full`. Add a song module for the full song that reuses the Revision 3 look; keep the approved promo files untouched.
3. Backdrop rules that differ from the promo: calmer camera (performers stand in front), bottom third calm, the expression phrases readable from the back of the hall for 8 to 10 seconds, small signature, ends on a calm hold (no black).
4. Stills at section landmarks, owner review, then the full 30 fps render in parallel cloud parts, join, check length, sync and frames.
5. Deliver to Drive "Videos/01 All You Stars of Zion/", update status docs, open a PR (the coordinator merges).

## 7. Housekeeping

- The cloud environment "Church media" was switched to **unrestricted network** for the YouTube attempt. Switch it back to limited (its earlier allowlist: heavenlymotherslove.org hosts and the productionresultssa*.blob.core.windows.net hosts) once no cloud download needs it.
- No em dash or en dash anywhere. No lyrics in new files beyond short on-screen fragments. No full songs, finished videos or frames in the repo.
