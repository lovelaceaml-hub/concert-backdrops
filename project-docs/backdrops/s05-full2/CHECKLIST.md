# 05 God Bless You!: version 2 checklist

Every rule of the version 2 brief, yes or no, and where it was checked. Written before the full render; the render checks at the end are filled in from `verify05.py` and the delivered files.

## Reading and sources
| Rule | Yes/No | Where checked |
|---|---|---|
| Drive AGENTS.md, DESIGN-SYSTEM.md read | yes | read in this session (Drive) |
| VIDEO-HANDOFF, AUTONOMOUS-RUN, PHASEB (through Update 25), PROJECT-HANDBOOK, Status/05, design text, campaign pages | yes | read and summarised by a Haiku helper this session; quotes checked against this brief |
| Designs/CONCERT-OVERVIEW.md | yes | read in this session |
| Renderer handoff, first-run branch and TIMELINE reused | yes | `backdrop/s05-full` code copied into `tools/s05_full2/` and changed |

## The message, the bar, the look
| Rule | Yes/No | Where checked |
|---|---|---|
| Every scene serves the Words of Mother's Love bringing peace | yes | TIMELINE: every section is a word practised (prayer, a hand, listening) and its peace (waves, blossom, fruit) |
| Heavenly, warm, never dark, cold, empty or eerie | yes | stills (contact sheet); the brother and sister are paler gold, never dark |
| Song 05 look: spring afternoon, fresh green gold, cream, soft rose, bright daylight, blossom petals, warm haze, open and airy | yes | `song05.py` LOOKS; stills |
| No comets (song 01 only) | yes | no comet layer in `song05.py` (the base song's comets are not used) |
| Signature effects of this song (tree of blessing, stepping stones, prayer light, waves of peace, ripening fruit) not reused from other songs | yes | `effects05.py`, from the song 05 design |

## Length and timing
| Rule | Yes/No | Where checked |
|---|---|---|
| Music part exactly the live length 159.0 s, then a 15 s calm hold; total 174.0 s | yes | `timing.py`; verify05 frame count |
| Reference measured (analyze.py, loudness, hits, repeats) | yes | TIMELINE "Measurements" |
| Reference not within 1 s, so scaled section by section, marked as an estimate | yes | TIMELINE "Length" (one factor for every section, said why) |
| CUES.md with section starts, picture and calm end of each | yes | CUES.md |

## Expressions and the arch
| Rule | Yes/No | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS, "(or root)" kept | yes | `words2d.expressions()` reads engine/p3d/words.py at the tag; stills |
| Website colours | yes | capsule colours and arch colours from the same table (dark Respect and Compliment use their GLOWS for the arch lights only) |
| Placed only where the lyric is that act | yes, with Respect a provisional exception as instructed | TIMELINE; DESIGN-SYSTEM 12a.2 |
| Readable 8 to 10 s with nothing competing | yes | 9.3, 9.3, 9.3, 8.9, 9.1 s (TIMELINE); Clear wrapper dims all scene light inside the boxes; hearts skip the boxes |
| Upper middle, block centred about a third down, people below | yes | centre 0.38 of the height (box 286 to about 530 px); people from about 554 px down |
| Words collapse into their star | yes | overlay05 `_out_star`; stills at 0:38 |
| Star history: starts 3, 4, 7, 9; relights 7; lights 8 and 6; ends 3, 4, 6, 7, 8, 9 | yes | `song05._arch_lit` |
| Relight is a brief flare and one new ring | yes | the engine arch's relight (age resets) |
| The person or people do the expression while it reads | yes | ACTING.md; stills 0:30, 1:06, 1:44, 1:58, 2:21 |
| Symbols in the world, subtly, in the expression colour, never over the words | yes | `song05._symbols` (fireflies, petals, light trail, flock, sparks), each wrapped in Clear |
| Hearts in the expression colours drift off each expression | yes | `song05.HEARTS`, drawn by overlay05 from the acting hands |
| Only one expression reads at a time | yes | `Words.check()` asserts no overlap |

## People
| Rule | Yes/No | Where checked |
|---|---|---|
| Only gold glitter (or crystal) people, whole and radiant, never shattering, ash, dark, glowing eyes | yes | gold glitter bodies, painted gold, a warm inner light; no break-up effects |
| Fewer people, more light | yes | four people in a few tender moments |
| Touch only between two people of the same gender | yes | two men clasp hands (verse 1), two women (verse 2); brother and sister never touch |
| Refined natural movement, no random poses | partly | library motions and gestures with eased blends; checked in stills and the motion strip; the sister's get-up while holding a hand is the weakest move |
| Heavenly Mother only from behind or as hands | yes | not shown in this song |
| Faces soft, no realistic faces | yes | bodies have no facial features; the Respect symbol is a simple line drawing |

## Words on screen
| Rule | Yes/No | Where checked |
|---|---|---|
| Opening readable from frame 0, at least 7 s: logo, HEALING CONCERT, title lines (second italic), song title large | yes | overlay05 `_opening`, whole until 7.4 s; still at 0:00 |
| Opening on calm sky | yes | still at 0:00 |
| Signature top left from the end of the opening to the last frame, all five parts | yes | overlay05 `_signature`; verify05 signature match on every frame |
| Concert information never flashes | yes | constant after a single fade-in |
| Signature never covered; 40 px from any expression box | yes | signature ends about y 200; expression boxes start at y 286; arch lights searched to stay clear |
| Date capitals at least about 22 px | yes | 24 px (measured) |
| Lyric fragments 3 to 6, short, each its own effect, never with an expression | yes | 4 moments: petals, sunbeam, ripening fruit, seeds of light |
| Navy #1f2a6b with soft white glow on bright skies, nothing dark behind text | yes | words2d NAVY; overlay white glow |
| No end card (song 11 only) | yes | ends on the calm hold with the signature |

## Never
| Rule | Yes/No | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest frame mean from verify05 (see results) |
| 2 No white text on pale skies | yes | all text navy |
| 3 Nothing crossing a reading box or the signature | yes | Clear wrapper, heart skip, arch search |
| 4 One expression at a time | yes | Words.check |
| 5 No garbled or broken letters while forming or leaving | yes | crisp text with smooth wipes and fades only (no pixel dissolves); motion strip |
| 6 No words mirrored in water | yes | words are a 2D layer above the picture |
| 7 No dark, brown, solid or mannequin people; big enough | partly | gold glitter with painted grains; about 170 px tall standing; they read, but can look soft at the back of a hall |
| 8 No mushy blur, jitter, popping or sliding | yes | motion strip |
| 9 Bottom third calm | yes | overlay05 `_calm` (soft water, highlights held) |
| 10 Calm camera, never frozen | yes | slow drifts (KEYS), verify05 identical-frame count |
| 11 No other logos or watermarks, no realistic faces | yes | only the campaign logo |

## Process and delivery
| Rule | Yes/No | Where checked |
|---|---|---|
| Render only in this cloud session; no Render workflow; no paid service | yes | rendered here, 12 parts on 4 cores |
| No song audio, lyrics, videos or frames in git | yes | git status; outputs outside the repo |
| No em dash or en dash anywhere | yes | grep of every new file |
| Branch backdrop2/s05-full from the approved tag; code and docs in the given folders; approved, engine and other songs' files untouched | yes | git diff --stat against the tag |
| 60 fps 1920x1080 | yes | verify05 (see results) |

## Render results (verify05.py on the delivered files, 2026-11-19)
| Check | Result |
|---|---|
| Length | stage, review and phone all 174.000 s, 10,440 frames, 60/1 fps; stage and review 1920x1080 yuv420p, phone 1280x720 |
| Dropped, repeated, frozen frames | 0 identical neighbouring frames; smallest change between frames 0.024 (always gently alive) |
| Black frames | none (darkest frame mean 185.6/255) |
| White-out | brightest frame (2:35.85, climax) mean 213/255, only 0.16 percent of pixels near white: a warm gold bloom on a visible scene |
| Sync, music against the conformed music at the three hits | 53.39 s, 115.74 s, 142.93 s: offset 0.0 ms each |
| Picture reacting to the music near the hits | best lag -250, -83 and -450 ms (a soft measure: the scene reacts gently to loudness; the scene is driven by the same reference analysis at r = t / K by construction) |
| Silence after the music | -120 dBFS from 159.4 s |
| Signature | present from frame 541 (9.0 s) to the last frame, lowest match 0.931 after 10.0 s: never covered, never flashing |
| First and last frames | first: the whole opening card on the spring sky; last: the calm late afternoon hold with the signature (contact sheet) |
| Phone file under 25 MB | 23.2 MB |
| No em or en dash in new files | checked by grep |
