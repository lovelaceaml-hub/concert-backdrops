# Concert promo project handbook (shared instructions for Claude and Codex)

**Codex stopping point, 2026-11-16 (Las Vegas):** paused at the owner's request after saving findings. The exact 4K60 master and its Drive parts are preserved; download to the owner's computer and review of the quality export are still unconfirmed. A local Codex handoff prompt, checksums, known transfer failures and the next step are saved in [the session checkpoint](https://drive.google.com/file/d/1BdI-R2ceMFqyBe1nsxSdzBtM6dG5K9UN/view). Resume with local delivery, not another render or encode. No background render job is running, and PRs remain draft and unmerged.

**Current quality master, 2026-11-16:** one native 3840x2160, 60 fps, 10-bit export of the approved Revision 3 is complete and checked. Added composite grain is removed; the edit and exact music stream are preserved. The owner requested one highest-quality file. The exact 318,834,702-byte master is available in [Google Drive](https://drive.google.com/drive/folders/1_m5HLeo8brJgZMgdXleEbY7klrAGaxgS) as four parts with an offline helper that restores one original MP4. Download the folder on a computer, unzip it, open Open-to-save-video.html, select all four parts, then save the video. The restored file was verified byte for byte. The owner's download is not yet confirmed; no smaller encode was created. The new quality file awaits owner review; prior approved files remain archived. [Quality record and checks](QUALITY-NINE-COLOURS-R3.md).

Last updated 2026-11-16 by Codex to save the stopping point, local delivery handoff and exact UHD transfer package, preserving the coordinator's earlier history below. This handbook is the single source of truth for every AI agent (Claude sessions, Claude helpers, Codex, or any other) working on this project. If you are an agent starting work, read this whole file first, then the files it points to. If anything here conflicts with an older brief, this file wins, and the newest owner direction (section 4) wins over everything.

**Approved creative cut: Film 10, Nine Colours, Revision 3.** On 2026-11-16 the owner said "thats so good. save this and update all docs and upload" after viewing this cut. Read [APPROVED-NINE-COLOURS-R3.md](APPROVED-NINE-COLOURS-R3.md) for the exact videos, source tag, hashes, reproduction and scope. The approved cut is 66 seconds at native 60 fps, with the original Film 10 medley. Older 62-second/seven-song plans below describe earlier versions. This approval does not authorize any merge.

---

## 1. What the project is

- **Owner:** Anthony. He decides everything and merges nothing he has not seen. Agents never merge pull requests.
- **The event.**
  - Healing Concert, "The Words of Mother's Love That Bring Peace".
  - Sunday, December 6, 4:30 PM.
  - World Mission Society Church of God, 6720 W Sahara Ave, Las Vegas.
  - It is part of the church's campaign "The Words of Mother's Love" (the 2026 Mother's Love Preaching Festival; theme: the Art of Happy Communication), with the logo of two hearts, a globe and olive branches.
- **Current quality export:** one 66-second native 4K60 master of the approved Film 10 Revision 3, complete and checked. The exact master is uploaded as four byte parts with a restore helper; see the quality record above. The earlier masterpiece work and alternatives remain preserved below.
- **The bar (Anthony's words):** "majestic, beautiful, awesome, brilliant, extravagant, beyond imagination, heavenly, very expressive ... so breathtakingly beautiful that emotions are felt." Express the words of Mother's love that bring peace.
- **Earlier phases, kept for reference:**
  - 11 per-song backdrop promos (main branch);
  - an epic promo;
  - ten parallel promo films.

  These were superseded by the one masterpiece (sections 7 and 8).

## 2. Where everything is saved

### 2.1 The GitHub repo: lovelaceaml-hub/concert-backdrops (private)

The engine code, song files, short audio clips and these docs.

- **main:** the stable base (11 song promos, older engine). The docs folder `project-docs/` mirrors Anthony's Drive folder. This handbook lives at `project-docs/promo/PROJECT-HANDBOOK.md`.
- **project-docs/promo/:** everything from the promo phase, copied out of the Claude session scratch space:
  - `PROJECT-HANDBOOK.md`: this file.
  - `briefs/`: the working briefs.
    - `PHASEB.md` records the owner directions through UPDATE 24, the stopping point and local delivery handoff. Read UPDATES 13 to 24 at least.
    - `P3D-BRIEF.md`: direction for the 3D particle engine and the house rules.
    - `EPIC-BRIEF.md`: mechanics.
    - `MASTER-TREATMENT.md`: the approved masterpiece treatment.
    - `TEN-FILMS.md` and `ten/`: the ten parked film ideas.
  - `handover/`: handovers from each helper, saying what was built, the calls, and what is weak.
    - Engine: `CORE.md` (3D layer and camera), `BODY.md` (particle people, acting, hands), `WORDS.md` (particle words, TITLES, end card), `BRAND.md` (logo, hearts, symbols, globe, world to logo), `STYLES.md` (people looks; the dark styles were rejected).
    - Films: `film_01.md`, `film_04.md`, `film_05.md`, `film_06.md`, `film_10.md` (best moments of the parked films).
  - `medley/`: the section maps of the music (where every song, beat and hit falls).
  - `tools/`: the session's shell tools (`local_render.sh`, `local_full.sh`, `watch_ten_videos.sh`). Their paths are session specific: edit the BASE and TOOLS paths before use.
  - `design/`: the scripts that made the approved title and end-card mockups (`mock.py`, `mock2.py`, `mock3.py`). The mockup images are in Drive.
- **engine/UPGRADE-HOWTO.md** on each engine branch: the technical manual. Section letters:
  - V: 3D layer, camera, world, motion blur, masks, windows.
  - W: particle bodies, acting.py, gestures, pairs, crowds, living hands.
  - X: particle words, website colours, label pills.
  - Y: TITLES (opening, signature, date_light, end_card).
  - Y2: people styles (parked).
  - Z: BRAND (logo, hearts, symbols, Globe, Finale).
  - AA: render speed, from Codex.
  - Q: output, 4K and 60 fps.
- **audio/promo/:** short clips the render needs.
  - `s01.mp3` to `s11.mp3`: 60 s clips of the 11 concert songs. s02 and s10 have no music.
  - `concert-medley.mp3`: the old 8-song 60 s medley.
  - `concert-medley-leadin.mp3`: the same with a 2 s quiet lead-in, 62 s.
  - `concert-medley7.mp3`: the new 7-song medley (branch `medley7`, map in `project-docs/promo/medley/SECTION-MAP-medley7.md`).

### 2.2 Anthony's Google Drive: folder "Concert Backdrops - Songs"

The project's home for media and documents.

- Older docs: the visual plan, lyrics (never commit lyrics), the shot list, and the 2026-11-13 engine zip.
- The subfolder **"Promo masterpiece (2026-11-16)"** holds:
  - this handbook and the briefs;
  - the reference images: Anthony's inspiration photos and people-style references;
  - brand material: the logo, the official poster, the expression icons and website screenshots;
  - the approved design mockups.
- Archived approved Revision 3 exports are saved in the project's Videos folder: [phone 720p60](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view) and [master 1080p60](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view). The phone copy was also delivered in the Codex chat. Older render artifacts remain in GitHub Actions (section 2.3); they are not this approved cut.

### 2.3 GitHub Actions: the "Render" workflow (.github/workflows/render.yml)

Renders in the cloud and stores videos as run artifacts: `<name>`, `<name> (share)`, `<name> frames`, `<name> QA`, and `part0` and up.

Runs of the masterpiece so far, all on branch `master/words-that-bring-peace`:

| Version | Run id | Notes |
|---|---|---|
| v1 | 43744483677 | |
| v2 | 43751947743 | |
| v3 | 43754886880 | |
| v4 | 43761338964 | |
| v5 | 43767697863 | |
| v6 | 43769618192 | Historical 62 s version at 30 fps |
| v7 test 1 | 43785749994 | Work in progress, 60 fps, old medley |
| v7 | 43800824532 | 60 fps, medley7, refined acting, smooth carries |
| v8 | 43806325783 | v7 plus two small fixes |
| v9 | 43810639666 | Historical v9 (head 58ec94f): Nine Colours comets as the travelling thread, words written by comet pens, Gratitude, Concession and Respect in light only, escalating theatrical transitions |
| Nine Colours Final v1 | 43855882765 | Claude reference, f43f451, 62 s / 60 fps; source for Revision 3's typography, Respect and orbiting symbols |

The approved 66-second Revision 3 was rendered in the cloud execution workspace, not by dispatching GitHub Actions. Its source tag and Drive files are recorded above.

### 2.4 The Claude session scratch space (ephemeral)

The working copy of everything above lives at `/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/`. It is lost when the session ends, so anything that matters must be copied into the repo or Drive.

## 3. Branches and pull requests (state on 2026-11-16)

| Branch | Head | What it is |
|---|---|---|
| `master/words-that-bring-peace` | 58ec94f (v9; v6 is b7895ae) | THE MASTERPIECE. Song `engine/songs/master_peace.py`, plus its own effects in `engine/p3d/master_sky.py`, `master_fx.py` and `master_brand.py`. PR #54 into engine-p3d-words. Claude's helper MASTER3 is the only writer. |
| `creative/nine-colours-spiral-and-expression` | approved source `46df53b`, tag `film10-revision3-approved-2026-11-16` | Owner-approved Film 10 Revision 3, 66 s / 60 fps. Draft PR #71 based on draft #70, unmerged. Implementation only under `tools/nine_colours_minor/`. |
| `quality/nine-colours-clean-master` | renderer `2c95ee0`, delivery/QA `dd8f0f5`, transfer helper `5858307` | One clean UHD60 master, draft PR #73. Complete and checked; exact master transferred to Drive as four byte parts with a restore helper. New quality file awaits owner review. |
| `medley7` | 19f2c83 | The new 7-song medley `audio/promo/concert-medley7.mp3` (order 03, 04, 01, 08, 11, 06, 07; 62.000 s; map in `project-docs/promo/medley/SECTION-MAP-medley7.md`). Built by MEDLEY3; MASTER3 merges it into the masterpiece. |
| `engine-p3d-words` | afd2bd3 | The integrated engine the masterpiece builds on (3D layer + bodies + words + TITLES + brand merged). |
| `engine-p3d` | 8902405 | 3D layer (CORE2 final). PR #53. |
| `engine-p3d-bodies` | 436057d | Particle people and acting (BODY2 final). |
| `engine-p3d-brand` | d2ae3c3 | Logo, hearts, symbols, globe, world to logo (BRAND final). |
| `engine-p3d-styles` | 8840e51 | People styles: PARKED, not merged (Anthony found the dark and breaking-apart styles scary). |
| `epic-medley2` | 45017af | The old 8-song medley. |
| `perf/render-speed` | 5ac9979 | Codex: render speed. Draft PR #55; about 7% faster, pixel identical. |
| `compare/sol61-concert` | | Draft PR #56: an independent comparison version (GPT 6.1 "Sol"), from v6. |
| `compare/astra6-concert` | | Draft PR #57: an independent comparison version ("Astra"), from v6; edits `engine/titles.py`. |
| `ten/01-the-wave` to `ten/10-nine-colours` | | The ten parked films (handovers in `project-docs/promo/handover/film_NN.md`). |
| `epic-promo`, `engine-epic`, `engine-*` | | Earlier phases; PRs #42 to #53 open, unmerged. |
| `main` | 599b1b9 | Stable base; PRs #18 to #41 (older song promos) open. |

Nothing is merged without Anthony's explicit approval. Comparison PRs #56 and #57 are alternatives for Anthony to judge; do not merge them into the masterpiece without his decision.

## 4. Owner directions (all still in force unless replaced)

The newest are in `project-docs/promo/briefs/PHASEB.md`, through UPDATE 24.

**Approved Revision 3, 2026-11-16:** preserve the extended opening/burst, original eight-song Film 10 medley and final accent, cream serif expression text with capsule labels, golden listening pair for Respect, swirling light becoming Earth with orbiting expression symbols, signature and official pastel closing card. The approved timeline is 66 seconds with a six-second lead-in, and both exports are 60 fps. These specific approved choices supersede the earlier duration, seven-song and quiet-last-second proposals for this cut only. No new creative change or render was requested with the save instruction. [Exact approval record](APPROVED-NINE-COLOURS-R3.md).

**Look and feeling**
- Majestic, heavenly, breathtaking. Warm radiant light: golden clouds lit from within, cathedral shafts of light, rivers and seas of light, prismatic sparkle.
- Never dark, cold, empty, eerie or decaying. No white-outs: keep highlights under clipping.

**People**
- Only warm gold glitter people. A crystal look was explored but is not yet approved.
- Whole and radiant: nobody shatters, crumbles, turns to ash or goes dark. No dark silhouettes, no glowing eyes.
- Faces soft and luminous; artistic faces are allowed, never photorealistic.
- Fewer people, more light. Tender, clearly acted moments.
- Movement must be refined and anatomically natural (Anthony, 2026-11-16): relaxed shoulders, softly bent elbows, gentle hands, weight shifts, eased transitions. No stiff straight arms, no limbs through bodies, no stray feet, no snapping.

**Casting**
- Greeting: two men, each bowing slightly to the other.
- Embraces: two women only.
- Every touching moment is between two people of the same gender. The only exception is parent and child.

**Heavenly Mother**
- Only as hands of light holding the golden drop at the opening, or seen from behind. Never a face.
- No hands at the end: Anthony found the cradling hands "extremely weird".

**The nine expressions** (exact wording from `words.EXPRESSIONS`, website colours)

| Expression | Wording | Colour |
|---|---|---|
| Greeting | "How are you?" | #EA5A5E |
| Gratitude | "Thank you. It's all thanks to you. You've worked hard." | #F2B25E |
| Apology | "I'm sorry. It must have been hard on you." | #F6CE46 |
| Inclusiveness | "It's okay. I understand." | #5ABA5A |
| Concession | "Please, after you." | #62B2FA |
| Respect | "I'd love to hear more about your thoughts." | #667AF6 |
| Encouragement | "I'll pray (or root) for you. Everything will go well." | #9E6AF6 |
| Consideration | "Can I give you a hand with anything?" | #EE62A6 |
| Compliment | "You're amazing. You're doing great!" | #364E96 |

- Each is acted while it reads and read for 2.5 s or more.
- Words sit in the upper middle of the frame (centred about 0.33 to 0.36 of the height), legible on a phone. Nothing ever crosses a word, and no word is mirrored in water.

**Expression symbols, hearts and the world**
- The nine expression symbols (waving hand, bowing person, face with a tear, hugging face, "after you" gesture, hand at the ear, praying hands, two hands holding a heart, clapping hands) appear subtly as scenery effects, never as icons over the words.
- Hearts come from the action.
- In the finale, the nine symbols swirl round the luminous Earth in their colours, light up the world, then disperse as the world becomes the logo.

**Concert information** (Anthony: never flash it; each appearance at least 7 s)
- **Opening title:** fully readable from frame 0 for at least 7 s. Logo, HEALING CONCERT, "The Words of Mother's Love" / "That Bring Peace", SUNDAY, DECEMBER 6 · 4:30 PM, LAS VEGAS. Set in elegant serif type (Cormorant Garamond and Jost).
- **Signature:** always on, discreet, bottom left, from the end of the opening to the end card. Logo mark, title, DEC 6 · 4:30 PM, HEALING CONCERT · LAS VEGAS.
- **End card:** at least 7 s, to the last frame, in the official campaign style.
  - Font Outfit.
  - Navy #272751 "The Words of"; coral #F35763 "Mother's Love"; deep blue #0345A5 to #032D81 "That Bring Peace".
  - A coral ribbon with "Sunday, December 6" in yellow and "4:30 PM" in white.
  - Then the church name and address.
  - The logo in its exact true colours, on a soft peach and cream sky.
  - Approved mockup: Drive `design/N6_endcard_official.png`.

**Sound**
- The film opens with about 2 s of quiet, then the music fades in. The film is 62 s.
- Song changes must be smooth musical blends, never abrupt. Anthony: "the songs and transitions seem off and so abrupt".
- The ending must resolve gently, never stop abruptly.
- No AI-generated music (Anthony declined ElevenLabs music); re-edit the concert clips only.

**Motion**
- Keep the energy, but smoother: no strobing whips. Fast moves are eased, 0.8 s or longer, with motion blur.
- 60 fps output, and the copy Anthony watches is 60 fps too.
- The end card stays gently alive (a slow push-in, drifting sparkles, a glow on the final chord) and eases to stillness. No freeze, never a fade to black.

**Renders and costs**
- Render in the cloud with the GitHub "Render" workflow only. Anthony fixed a billing stop on 2026-11-15.
- Local stills and short frame chunks in the cloud session are fine for checks. Codex: do NOT trigger Render; it costs Anthony money.

## 5. House rules (every agent, every commit)

- No em dash or en dash characters anywhere: code, comments, docs, commit messages, PR text. Grep your diff.
- Never commit full songs, lyrics, finished videos, frames, stills, caches or personal data. Short promo audio clips under `audio/` are the only media allowed.
- Never `git add -A`: `fonts` is an untracked symlink. Stage files by name. Run git as separate plain commands.
- Work on your own branch and open a draft PR. Never merge; Anthony decides.
- Commit messages from Claude end with:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01DSHsMeB7ain7qg3RYXYMEW
  ```
  Codex uses its own attribution.
- Text on screen: nothing dark behind any text, frame 0 never black, no lyrics on screen.

## 6. How the engine works (short)

- Python plus moderngl, software OpenGL (`LIBGL_ALWAYS_SOFTWARE=1`, llvmpipe). Everything drawn is a function of time, so 60 fps is the same motion at twice the smoothness.
- `engine/render.py` renders frames: `--range A B --out file.mp4 --crf 16` or `--stills "1,5.5" --outdir DIR`.
- It is driven by environment variables:
  - `SONG`: a song file in `engine/songs/`, without `.py`
  - `AUDIO`: absolute path to the audio
  - `FEATURES`: the analysed audio, `.npz`, from `engine/analyze.py`
  - `OUT_RES`: 1080p or 4k
  - `OUT_FPS`: 30 or 60
- A song file declares keys such as `P3D` (the 3D world: camera, point sets, bodies, effects), `TITLES`, words and timing. The masterpiece is `engine/songs/master_peace.py`.
- Fonts: `npm pack @fontsource/cormorant-garamond @fontsource/jost @fontsource/outfit`, then `python tools/setup_fonts.py <packdir> fonts`.
- **Cloud render:**
  - Dispatch: `gh workflow run render.yml --ref <branch> -f song=master_peace -f audio=<audio path> -f mode=video -f fps=60 -f name="Masterpiece vN"`. No parentheses in names.
  - Results arrive as run artifacts.
  - The share copy is 1280x720 and under 25 MB.
- **Checks:**
  - `tools/qa_check.py` runs in every render. Today it misreads TITLES and gives false "no end card" warnings; Codex is upgrading it.
  - `tools/check_p3d_pairs.py`: pair contact geometry.
  - `tools/check_identical.py` and `tools/profile_render.py`: Codex, on perf/render-speed.

## 7. The masterpiece: what it is now (v6, run 43769618192)

The 62 s timeline on the lead-in medley:

| Time | What happens |
|---|---|
| 0 to 7 s | Quiet, then the music fades in; the opening title over a twilight sea of golden clouds; Mother's hands of light hold a golden drop. |
| About 7 to 9 s | The drop falls, the camera dives, a fountain of light lands, and a golden ring races out. |
| Middle | The nine acted expressions in order: Greeting (two men bow), Gratitude (a woman with a hand on her heart, hearts rising), Apology (two women, comfort), Inclusiveness (the embrace), Concession (a doorway of light, "after you"), Respect (two listening in profile), Encouragement (prayer with a hand on the shoulder), Consideration (two men, a helping hand), Compliment (a dancer and a joyful crowd). |
| Breath | A still moment of light, then the big hit and the ascent through clouds, with nine coloured streams rising to a glorious sun. |
| Finale | The luminous Earth; the nine symbols swirl round it, light it, then burst; the world becomes the logo; a bloom into a pastel day. |
| About 55 to 62 s | The end card, held to the end. |

**Anthony's open notes on v6, being fixed in v7:**
1. Songs and transitions abrupt: a new 7-song medley with smooth blends.
2. Choppy animation: fast whips and dives strobe at 30 fps (around 7 to 8.5, 15, 19, 21.5, 26, 28.5, 35, 38.5 and 44 to 47.5 s), and sparkles flicker at 26.5 to 28.5 s.
3. An abrupt ending: the end card is a frozen image, and the music decays in 1 s.
4. People need much more refined movement. #3 Apology had a stiff arm thrust at the other's head and a stray foot; #9 Compliment had awkward bent arms.

## 8. Who is doing what right now (avoid conflicts)

**Claude coordinator (this session)**
- Directs, reviews every render at full size, talks to Anthony, and keeps this handbook updated.

**MEDLEY3 (Claude helper)**
- Builds `audio/promo/concert-medley7.mp3` on branch `medley7`, 62.0 s:
  - a 2 s quiet lead-in and fade-in;
  - 7 songs chosen for flow from 01, 03, 04, 05, 06, 07, 08, 09 and 11;
  - 2 to 3 s phrase-aligned, tempo-matched blends with EQ hand-off;
  - one "lift" join;
  - a natural ring-out of 4 s or more.
- DONE (2026-11-16): order 03, 04, 01, 08, 11, 06, 07; six 2.3 to 3 s blends at 7.99, 13.97, 22.94, 31.46, 40.81 (midpoints) and the lift 46.69 to 49.69 (breath 47.19, hit 49.69); final chord 56.75, ring-out to silence by about 59.5. Map: `project-docs/promo/medley/SECTION-MAP-medley7.md`; build scripts beside it. Measured, not yet heard by Anthony.

**MASTER3 (Claude helper)**
- The only writer of `master/words-that-bring-peace`. Makes v7:
  - refines all nine acted moments;
  - smooths the motion;
  - keeps the end card alive;
  - changes render.yml so the share copy keeps 60 fps;
  - re-times the film to medley7;
  - renders at 60 fps.

**Codex**
- Paused for today at the owner's request. Resume only when the owner returns; the next task is saving the exact master to the actual local Downloads folder and confirming playback. The ready-to-use prompt is in the session checkpoint above.
- The new owner-authorized quality export is complete and checked in draft PR #73; the exact video is uploaded to Drive as four byte parts with a tested restore helper. The owner's download is not yet confirmed. No smaller encode was made. The approved creative work is complete: Film 10 Revision 3 in draft PR #71, saved under its approval tag. Shared records and Drive copies have been updated for handoff. The engineering tasks below are earlier assignments, not permission to alter the approved video while archiving it.
- **Own branches only** (perf/render-speed, and a new QA branch). Does not trigger Render and does not merge.
- **Hands off:**
  - `engine/songs/*`
  - `engine/p3d/master_*.py`
  - `.github/workflows/render.yml`
  - `audio/promo/*`
  - `engine/p3d/acting.py`, `pairs.py`, `gestures.py`, `motion.py`, `body.py`
- **Task A, render speed** (more important now that 60 fps doubles the frames):
  - Zero changed pixels on the 30-moment suite (`tools/check_identical.py`).
  - Leads: cloud sprite overdraw in `engine/p3d/layer.py` and the common sprite shader.
  - Disk caching of first-visit cloth and crowd bakes across render parts, with identical results.
- **Task B, upgrade `tools/qa_check.py`** on its own branch:
  - recognise TITLES (opening of 7 s or more, end card of 7 s or more);
  - add motion checks (strobing via mean frame difference and jitter per 0.5 s at the real fps, frozen stretches over 1.5 s, jumps);
  - add audio checks (level dips or jumps over 3 dB, intended silence at the start, an abrupt end above -45 dB in the last second, clipping);
  - stay backward compatible;
  - validate against the v6 share copy (artifact "Masterpiece v6 (share)", run 43769618192).
- **Channel:** the PR #55 thread. Post findings and PR links there; Claude reads it directly.

**Other agents (Sol, Astra)**
- Independent comparison versions in PRs #56 and #57. Do not edit Claude's or Codex's branches.

## 9. How to check your work (what "done" means)

**Stills**
- View at full size (1920x1080). Check:
  - legibility on a phone;
  - nothing crossing words;
  - natural poses with no stray limbs;
  - no white-outs;
  - true logo colours;
  - the signature and end card.

**Motion**
- Dense frame strips at 10 to 20 fps through every move, word arrival and transition.
- A frame-difference scan: mean absolute difference per frame on a 160x90 grey copy, aggregated per 0.5 s, plus jitter (the second difference). No sustained strobing, and no frozen stretch except the intended final easing.

**Audio**
- A 0.25 s RMS envelope: no dips or jumps over 3 dB at joins, silence for 0 to 2 s, under -45 dB in the last second, no clipping.
- File length exactly 62.0 s.

**Before anything goes to Anthony**
- The Claude coordinator reviews every render first and sends it with an honest list of what is left.

## 10. History in one paragraph

Per-song promos (main) were followed by an epic promo on an 8-song medley. Anthony then asked for a new 3D particle engine with lifelike people of light, which became engine-p3d plus bodies, words and brand. Ten parallel films followed, then five, then one masterpiece built from the best of all five. Rejected along the way:
- the corner title badge ("no effort or thought");
- dark and shattering people styles ("terrible and scary");
- cradling hands at the end ("extremely weird");
- flashing the concert info;
- words too near the top;
- an abrupt start, medley and end.

Approved:
- the opening, signature and official-style end card;
- the logo, hearts, subtle symbols and the world finale;
- warm gold people with tender, same-gender acting.
