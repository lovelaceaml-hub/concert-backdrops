# 11 Almighty God Who Knows the Future: status (backdrop version 2)

Updated 2026-11-19 15:40 UTC by the coordinating Claude Code session.

## Where it is: stopped at Anthony's request
On 2026-11-19 Anthony asked to "finish up all the videos with all the updates from here to come to a stopping point", then "Stop all of them. I don't want you to make any more ... No more reviews." All render machines, builders and the reviewer are stopped. Nothing is rendering.

- Branch `backdrop2/s11-full`. Code head **2075615**.
- Drafts at 960x540, 30 fps. The newest video of each section is on the private review page (claude.ai artifact 1SAvCedZLDEPTJzr1kChaj, owner only; database `fleet/A` to `fleet/G`):

| Section | Time | Asset | Code it was rendered from |
|---|---|---|---|
| Intro | 0:00 to 0:40 | 00b8ff753ed6bf78a1dee20c43873e76 | 17db6e6 |
| Verse 1 | 0:40 to 1:22.08 | 4f4e7bb2dd51658e6f3f11948d0b5f65 | 17db6e6 |
| Chorus 1 | 1:22.08 to 2:01.32 | a394c7739932676815ced512e3e0cbe5 | 17db6e6 |
| Verse 2 | 2:01.32 to 2:40 | ad9713d435bb18d64a0debb6c8a7a3e3 | 17db6e6 |
| Chorus 2 | 2:40 to 3:21.73 | f556b4f004a43260aa623b126673d94f | 294b29a (one pass earlier) |
| Coda | 3:21.73 to 3:58.8 | b5f1167b732465751d6190430872ded5 | 17db6e6 |
| Ending | 3:58.8 to 4:35 | a7ff23d32a03a2279c31dd6bdacb5664 | 17db6e6 |

- **The full film as one video**: these seven were joined (video stream copied, audio re-encoded once, 4:35, 66 MB; `tools/s11_full2/live/join_sections.sh`) and given to Anthony in the coordinating chat on 2026-11-19. It is not stored in git (finished videos never are), on the page (asset limit) or on Drive (session uploads are limited to about 3 MB).
- **In code 2075615 but not in the rendered videos**: the corner titles readable in warm white on the darker scenes (e18616c, f41) and the 0:53.78 crown hit as a key moment (2075615, f40).

## What the final film has
See DESIGN.md (every decision with Anthony's words). In short:
- Light as an event: a calm, darker base with real colour, and full light only on the key moments (`light_budget`, `KEY_MOMENTS`).
- More and more people going to Zion: rivers of people, waves of newcomers, the city growing on the beats.
- 226 real WMSCOG buildings: 140 Korean churches as the heavenly city on Zion's terraces and summit (no emblem above them), the international churches on the sea rings and in towns outside the mountain (with emblems).
- The emerald Earth lit from Korea; the conductor with neon streams of colour; the blue choir and orchestra with gold; an effect for each sound; blue rivers.
- Verse 2: everyone walking to Mother, twelve kings, 44 flag bearers, the real church of light at 2:36 to 2:42.
- Coda: no bowing, emblems rising in place of the hearts, an epic sun; the film ends on the emblem alone on the night sky.
- Promo-style words with no box; the concert title first, then the two-line song title.

## Open items (FINDINGS.md has every finding and request)
- f40, f41: fixed in code 2075615; need a render.
- f42: the cut at 1:14.56 is 0.14 s early (one joint change in `s11_full2.py` and `s11_church.py`).
- f43: Zion's terrace lines cross the words at 2:45.8.

## Next (only when Anthony asks)
1. Render the seven sections from 2075615 or later (one section per machine, see PIPELINE.md), then join them with `join_sections.sh`.
2. Fix f42 and f43 if wanted.
3. The final master at 1920x1080, 60 fps across the fleet; deliverables (video with the recording, silent stage file, 720p phone copy); checks (frame count, sync on three hits, no black or frozen frames).
4. Merge the pull request from `backdrop2/s11-full`.

## Threads used (all stopped)
Cloud sessions created by the coordinator (session_01DSHsMgq59yAPPQ2ZCifhgv), all children of it:
- Render machines A to G (one section each).
- Reviewer.
- Builders and their branches (all merged into `backdrop2/s11-full`):
  - CORE: words, light, music, Earth (`backdrop2/s11-b-core`);
  - STAGE: stage and conductor (`backdrop2/s11-b-stage`);
  - ZION: Zion and people (`backdrop2/s11-b-zion`);
  - ENDS: opening and closing (`backdrop2/s11-r7-ends`);
  - MARCH: march and kings (`backdrop2/s11-b-march`);
  - MODELS: real churches (`backdrop2/s11-models`).

## History
- 2026-11-18: planned with Anthony in the planner artifact (music measured, lyrics as sung on the recording, phrase list, 85 design questions answered).
- 2026-11-18 to 19: built on the promo engine by scene threads, passes: music-video pace, heavenly, references, grand, requests, dancers and arms (h8), music-driven light (h9).
- 2026-11-19: one section per machine with its own audio; the reviewer thread; standing builder threads in continuous mode; rounds 7 to 10 (Zion and the churches, the words, the conductor, Verse 2, the coda, light as an event); final pass and stop.
