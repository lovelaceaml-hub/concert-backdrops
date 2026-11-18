# 01 All You Stars of Zion: backdrop version 2, checklist

Every rule of the version 2 brief (coordinator, 2026-11-18, quoting AGENTS.md, DESIGN-SYSTEM.md, VIDEO-HANDOFF.md, AUTONOMOUS-RUN.md, PHASEB) with yes or no and where it was checked. "Stills" means the landmark stills (half size, looked at full size and at quarter size); "strip" the dense motion strips; "render" the checks on the finished files (export.py --check).

## Hard limits

| Rule | Yes/No | Where checked |
|---|---|---|
| Render only in this cloud session; no GitHub Render workflow, nothing paid, never on the Mac | yes | all renders ran in this session (render.py, export.py) |
| No song audio, lyrics, videos or frames in git | yes | audio, stills and videos only under work/ (ignored); `git ls-files` |
| Only the three short fragments on screen, no lyrics copied into files | yes | words.py TEXT; TIMELINE |
| No em dash or en dash anywhere | yes | scripted scan of every new file, commit and on-screen string |
| Nothing deleted in Drive; MP3s, Lyrics and Visual Plan docs not edited | yes | Drive was only read |
| Helpers: Haiku only, never Sonnet | yes | one Haiku agent read the Drive rule files |
| Branch backdrop2/s01-full from tag film10-revision3-approved-2026-11-16; code in tools/s01_full2/, docs in project-docs/backdrops/s01-full2/; no approved promo, engine or other song files edited; never `git add -A` | yes | `git diff --stat film10-revision3-approved-2026-11-16` |

## The message and the bar

| Rule | Yes/No | Where checked |
|---|---|---|
| The mother's words of love that bring peace are the main theme: the two expressions are the heart of the piece, read alone for 10 s each, acted by the people, then rise into the arch | yes | TIMELINE; stills 0:46, 2:46 |
| Majestic, heavenly, warm; never dark, cold, empty, eerie or decaying | yes | stills (starry night in navy and violet, rose gold, blue hour, golden sunrise) |

## Length and timing

| Rule | Yes/No | Where checked |
|---|---|---|
| Music part exactly the live length 188.0 s, then a 15 s calm hold: 203.0 s | yes | export.py constants; render check (duration, 12180 frames) |
| Reference measured; within 1 s of the live length, so used as is, stated in TIMELINE | yes | TIMELINE "Length and the time map" |
| CUES.md with every section start, what is on screen and its calm ending | yes | CUES.md |
| 60 fps native, 1920x1080 | yes | render.py FPS = 60; render check |

## Look

| Rule | Yes/No | Where checked |
|---|---|---|
| Song 01 look: clear starry night to golden sunrise; navy, violet, then gold; Milky Way, falling stars, sunrise rays; wide, horizon low, big sky | yes | stills 0:00 to 3:15 |
| The nine coloured comets (song 01 only) | yes | 0:19.6 to 0:30 |
| R3 craft kept: cream Cormorant phrases with coloured capsule labels upper middle, gold glitter people, warm, eased motion, no grain | yes | stills 0:46, 2:46 |

## The nine expressions and the arch

| Rule | Yes/No | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS, "(or root)" kept | yes | expr="Compliment"/"Encouragement" take the text from the words module; stills |
| Website colours (Compliment #364E96, Encouragement #9E6AF6) | yes | the words module's COLORS; arch ARCH_COL lifts them toward white for the lit star only |
| Only where the lyric is that act (design: Compliment verse 1 "faithful and beautiful work", Encouragement "Now let us arise") | yes | design 01 placement kept |
| Arch: none lit at the start; lights 9 and 7; ends with 7 and 9; no other star | yes | arch_states, LIT_AT; stills 0:46 (none), 0:56, 2:55, 3:15 |
| Each expression readable 8 to 10 s with nothing competing in its reading box | yes | 42 to 52 and 161 to 171 (10 s each); Clear() dims every light set inside the box; stills and strips |
| Block centred about a third of the way down, people below | yes | centre_y .36; stills |
| The words then collapse into their star | yes | leave="star" to the real arch places; strips 52 to 58, 171 to 177 |
| People DO the expression while it reads: Compliment applause (two young women), Encouragement a hand on the shoulder of someone kneeling, then helped up (two young men) | yes | ACTING plan in TIMELINE; stills; strips |
| Symbols IN the world, subtle, in the expression colour, never over the words | yes | Compliment traced in sparks high right in the night sky; Encouragement a flock of morning birds; stills |
| Hearts in the expression colour drift off each expression | yes | ExprHearts; stills 0:56, 2:55 |

## People

| Rule | Yes/No | Where checked |
|---|---|---|
| Warm gold glitter people, whole, clothed in light; no shattering, ash, dark silhouettes, glowing eyes | yes | stills |
| Fewer people, more light | yes | six in the verse, the pair plus four in the morning |
| Touching only between same gender | yes | the two women; the two young men |
| Refined, eased, natural movement | yes | Claude Final v1 refined gestures; strips |
| Heavenly Mother only from behind | yes | facing 180 (away from the camera), veiled, 60 to 113 |

## Words on screen

| Rule | Yes/No | Where checked |
|---|---|---|
| Opening readable from frame 0, held at least 7 s: logo, HEALING CONCERT, the title in two lines (second italic), the song title large, on calm sky | yes | still 0:00; render first frame |
| Signature from the end of the opening to the last frame, top left: logo mark, song title, concert title, DEC 6 · 4:30 PM brightest, HEALING CONCERT · LAS VEGAS; never flashes | yes | render.py; stills 0:08 on; render last frame |
| 40 px clear between the signature and any expression box; nothing covers the signature | yes | stills 0:46 and 2:46 measured |
| Date line capitals at least about 22 px at 1080p | yes | Jost 500 at 32 px: capitals about 23 px |
| Fragments 3 to 6, short, each with its own effect, never with an expression | yes | "like a torch" (fire), "dew of the dawn" (silk thread), "Arise" (stands out of the lake) |
| Warm white with gold on night skies; navy on bright skies; nothing dark behind text | yes | night palette; the morning sky behind the signature stays deep blue (#12306c to #173a74) |
| No end card (song 11 only) | yes | ends on the calm hold |

## Never

| Rule | Yes/No | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest moment stills (1:40, 2:27.8); render peak check |
| 2 No white text on pale skies | yes | stills |
| 3 Nothing crossing a reading box or the signature | yes | Clear(); stills and strips |
| 4 One expression at a time | yes | TIMELINE |
| 5 No broken letters while forming or leaving | yes | strips |
| 6 No words mirrored in water | yes | reflect=False on every word |
| 7 No dark, brown, solid or mannequin people; big enough | yes | stills |
| 8 No mushy blur, jitter, popping, sliding | yes | strips |
| 9 Bottom third calm: no bright reflections, rings or particles | yes | v2: no reflections of people, torches, comets, hearts; ring removed; BOTTOM_CALM 0.7 |
| 10 Calm camera, never frozen | yes | slow drifts only; render freeze check |
| 11 No other logos or watermarks; no realistic faces | yes | stills |

## Deliveries

| Rule | Yes/No | Where checked |
|---|---|---|
| Stage: silent, H.264 CRF 16, yuv420p, faststart, 203.0 s | see STATUS.md | export.py --check |
| Review: the same picture with the reference music (untouched, within 1 s), AAC 320k, CRF 20 | see STATUS.md | export.py --check |
| Phone: 720p60 with music, under 25 MB | see STATUS.md | export.py --check |
| No dropped, repeated, frozen or black frames; sync on 3 hit points | see STATUS.md | export.py --check |
