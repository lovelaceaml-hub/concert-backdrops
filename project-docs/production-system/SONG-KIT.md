# Song kit: full-length songs built from Almighty God Knows the Future

Owner direction (Anthony, 2026-11-23): "Forget all of those previous plans. Starting new based on since almighty
God knows the future." Build a reusable kit from the Song 11 recreation, "but expect to add more to the kit that
represents mothers words of love closer". Then make Song 7, "May No One Ever Feel Lonely", on it, and check in.

The older full-length versions (branches `backdrop/sNN-full` and `backdrop2/sNN-full`) are not the starting point.
The delivered Song 11 source (`tools/s11_full2`, `tools/s11_renewed`, `tools/s11_cloud`, `tools/s11_delivery`)
is not changed: its producing identity is recorded and must stay reproducible. The kit is a generalized copy.

## 1. What Song 11 is made of

Song 11 is one core file (`tools/s11_full2/s11_full2.py`) plus "sets" (threads). The core holds the song's
timing (hits, slams, key moments, the edit list), the shared helpers and the assembly; each set owns some edit
blocks and supplies its own camera shots (`SHOTS`) and scene objects (`add(scene)`). Sets read the core by
`from songs.s11_full2 import *` at load time, so every helper is tied to Song 11's numbers. The renewed pass
(`tools/s11_renewed`) then installs a steadier camera, the continuous conductor, separate modest garments and
graded light and water over the loaded film.

| Part | Song 11 file | In the kit |
| --- | --- | --- |
| Timing: loudness, beats, hits, key moments, light budget, music pace, camera shake, lens punch | `s11_full2.py` | `core.py`, read from the song's data |
| Light: ray lights, light slots, comets, cloud banks, pillars, sea glitter, constellations, sky ribbons, glory | `s11_full2.py`, `s11_light.py` | `light.py` |
| Edit: blocks with owners, shot gathering, the music rig, cut flashes and hit bursts, exposure that follows the light budget | `s11_full2.py` | `core.py` |
| Words: phrase entrances (light, people, blaze, fly) and exits, kept out of people | `s11_words.py` | `words.py` |
| Corner signature, opening title, end card | `s11_cards.py`, `titles_s11v2.py` | `cards.py` |
| Music effects and the measured music map | `s11_music_fx.py`, `s11_music_map.py`, `s11_prepare.py` | `music.py` |
| Stage: choir and orchestra as blue sparkle with gold instruments and song books | `s11_stage.py` | set `stage` |
| Ribbon dancers and the conductor | `s11_dance.py`, renewed `performance.py` | set `dance` |
| Crowds with waves of raised arms | `s11_zion.py` (`Arms`, `WaveCrowd`) | set `crowd` |
| Church of light with the traced emblem | `s11_church.py` | set `church` (optional) |
| Earth of light, night to day | `s11_full2.py` (`GlobeFX`, `earth_day`) | set `earth` (optional) |
| Steadier camera, modest garments, graded light and water | `tools/s11_renewed` | `renewed.py`, applied to every song |
| Native chunked render, cloud fleet, assembly, delivery checks | `tools/s11_renewed/render.py`, `tools/s11_cloud`, `tools/s11_delivery` | `render.py`, one workflow, `deliver.py` |
| Song 11 story: Zion city, procession, the 226 churches, coda | `s11_zion.py`, `s11_procession.py`, `s11_churches.py`, `s11_coda.py` | stays Song 11's own |

## 2. The new part: the Words of Mother's Love (`love.py`)

Anthony's request is that the kit show the Words of Mother's Love more closely. Every song carries some of the
nine expressions (`engine/p3d/words.py` `EXPRESSIONS`, exact wording and website colours), and the concert's arch
of nine lights carries over from song to song (DESIGN-SYSTEM section 5). The kit gives them one shared home so
each song can stage them richly and new ideas can be added once and used everywhere:

- **The arch of nine lights**: lit at the start, lit in this song, lit at the end (from the song's data).
- **The words**: the expression's exact wording in its colour and capsule label, upper middle of the picture,
  read at least 2.5 s, never over a person; it collapses into its star in the arch.
- **The act**: people of light act the expression out, by the rules of PHASEB UPDATE 15 (greeting: two men each
  give a slight bow; embraces: two women; every touch between people of the same gender, except a parent and
  child). Acts are registered by name (`love.ACTS["greeting"]`, `love.ACTS["consideration"]`, ...), so a new
  act or a better one is added in one place and every song can use it.
- **The answer of light**: what the world does in reply (for example Song 7's peace ring spreading across the
  lake), also registered by name.

Version 1 covers the arch, the words and the acts Song 7 needs (Greeting, Consideration). The other seven acts
are added as songs need them.

## 3. A song on the kit

`songs/<id>/song.json` holds the data: recording (catalog id, hash), music end and the 15 s calm hold (no time
stretching), measured hits and key moments, the edit list (block start, owning set, note), phrases (lines,
times, entrance, exit), expressions (label, times, act, answer), arch state, palette and look (from the
DESIGN-SYSTEM look table, so every song still looks different), corner signature windows. `songs/<id>/world.py`
holds anything only that song has (its own set).

## 4. Order of work

1. Kit core, light, words, cards, music, render and delivery, generalized from Song 11 (Song 11 itself is not
   moved). Check: the kit renders a short test song with stage, dancers and an expression.
2. `love.py` version 1 (arch, words, Greeting and Consideration acts).
3. Song 7 data and world from its design (`project-docs/designs/07 May No One Ever Feel Lonely.md`): blue dusk
   path home, lanterns, the lost lights found, Mother's lamp (as light), the gate and the bridge of light home.
4. Song 7 review stills, then section drafts, then the native 1080p60 film in the cloud, saved to Drive.
5. Check in with Anthony.

Rendering is cloud CPU only. No phone copies. Final 4K only after the song is approved.

## Status (November 23, 2026)

- The kit renders end to end in the cloud (`.github/workflows/song-kit.yml`: draft or film, parts passed between machines
  through the private Drive folder, film checked, then saved to the song's Drive folder with its section cues).
- Song 7 version 1 is delivered and awaits Anthony's review; see [DELIVERIES.md](DELIVERIES.md). His answers on the Song 7
  Design Planner page (https://claude.ai/artifact/3eNMdaQ8S7jSSqx8hx5ByF, stores "choices" and "phrases") drive version 2.
- Other songs get their own walkthrough page only when Anthony asks (his choice on 2026-11-23: "Only Song 7 for now").
