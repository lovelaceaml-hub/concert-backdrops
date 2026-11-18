# Song 07 backdrop v2: checklist (every rule of the v2 brief)

Written before the full render, then completed with the checks of the finished video. "Where" says how it was checked: `check_layout.py` (geometry every 0.25 s over the whole video), `verify.py` (the finished files), stills (contact sheets, looked at full size and at quarter size), or the code.

## Hard limits
| Rule | Yes/No | Where |
|---|---|---|
| Rendered only in this cloud session; no GitHub Render workflow; no paid service; nothing on the Mac | yes | tools/s07_full2/export.sh run here |
| No song audio, lyrics, videos or frames in git | yes | git: only code and docs; audio, stills and parts under work/, scratchpad, out/ |
| No em dash or en dash anywhere | yes | grep of every committed file (see STATUS log) |
| No Drive deletions; MP3s, Lyrics doc and Visual Plan untouched | yes | Drive was only read (and one new contact sheet file added, if the upload works) |
| Helpers: Haiku only | yes | one Haiku agent read the Drive rule files |
| Branch backdrop2/s07-full from tag film10-revision3-approved-2026-11-16; code in tools/s07_full2/, docs in project-docs/backdrops/s07-full2/; approved promo, engine and other songs' files untouched; no `git add -A` | yes | git log and diff against the tag |

## Length and timing
| Rule | Yes/No | Where |
|---|---|---|
| Music part exactly the live length 238.0 s, then a 15 s calm hold: 253.0 s | yes | clock.py; verify.py on the stage file |
| Reference measured (analyze.py, loudness, hits) and mapped onto the live length; estimate noted | yes | TIMELINE.md sections 1 and 2 |
| CUES.md: every section start, what is on screen, the calm moment that ends it | yes | CUES.md |
| Hold gently alive, never black | yes | stills 245 and 252.9; verify.py darkest frame |

## Look
| Rule | Yes/No | Where |
|---|---|---|
| Song 07's own look: blue dusk on a long path home; twilight blue, coral, lantern gold; lanterns, first stars, mist; deep perspective | yes | stills; LOOKS in the song module |
| No comets (song 01 only) | yes | code: no comet sets (grep) |
| Own signature effects: footprints of light, peace rings, first stars, lost lights found, Mother's lamp, gate of the kingdom, bridge of light | yes | song module; stills |
| Approved craft kept: cream Cormorant phrases with coloured capsule labels, upper middle; people quality; smooth eased motion; no grain | yes | stills 57 and 69.5; words from Claude Final v1 |
| Majestic, warm, never dark, cold, empty, eerie or decaying | yes (blue dusk kept warm: coral horizon, gold light) | stills |

## Expressions and arch
| Rule | Yes/No | Where |
|---|---|---|
| Exact wording from words.EXPRESSIONS; website colours (Greeting #EA5A5E, Consideration #EE62A6) | yes | expr= in the word specs (text and colour come from the module) |
| Only where the lyric is that exact act: Greeting at the answer to Mother's first wish, Consideration at the promise to care (design section 9) | yes | TIMELINE.md |
| Readable 8 to 10 s: Greeting 9.0 s, Consideration 9.2 s | yes | check_layout.py |
| Nothing competing inside the reading box (no other text, person, burst or particle) | yes | Clear() dims every light inside the reading boxes; people stand below; check_layout.py: one expression at a time |
| Block upper middle (centre about a third down), people below | yes | WORD_Y 0.345 from the top (Consideration 0.37); stills |
| Words collapse into their star: Greeting into star 1, Consideration into star 8 | yes | leave="stream" to the star; arch timing |
| Star history: 3 to 9 lit at start; 1 lit (63.3 s); 8 relit with a brief flare and one new ring (76.0 s); 2 never lit; end 1 and 3 to 9 | yes | _arch_lit; stills 9.5, 89, 252.9 |
| People DO the expression while it reads: Greeting two men each giving a slight warm bow (no handshake or embrace); Consideration helping someone up | yes | stills 57, 62.5, 69.5; TIMELINE section 5 |
| Symbols in the world, subtle, in colour, never over the words: Greeting constellation among the stars, Consideration traced by fireflies | yes | stills 57, 69.5 |
| Hearts in the expression colours drift off each expression | yes | HeartDrift (brand_hearts.py), drawn as spark hearts |

## People
| Rule | Yes/No | Where |
|---|---|---|
| Only warm gold glitter people (crystal not used: the handbook says it is not yet approved), whole, radiant, clothed in light, soft faces | yes | look="glitter" everywhere |
| Fewer people, more light | yes | 2 people for the expressions; small crowds (10, 24, 26) as lights |
| Touching only same gender, or parent and child | yes | two men (greeting, help up, search hands), two women (embrace), mother and child |
| Refined natural movement | yes (engine's eased acting) | motion strip |
| Heavenly Mother only from behind | yes | facing 180 (away from the camera) throughout |

## Words on screen
| Rule | Yes/No | Where |
|---|---|---|
| Opening readable from frame 0, at least 7 s: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), song title large; calm sky | yes (whole to 7.3 s) | cards07.py; stills 0 and 7 |
| Signature top left from the end of the opening to the last frame; never flashes; nothing covers it; 40 px clear of expression boxes; date capitals at least about 22 px | yes (date capitals about 23 px; closest word 49 px; closest arch star 37 px) | cards07.py; check_layout.py; verify.py (date line present on every frame after 9 s) |
| Lyric fragments: 5 short ones from the design, each with its own effect, never with an expression | yes | TIMELINE section 6; check_layout.py |
| Warm white with gold on night skies; no white on pale skies; nothing dark behind text | yes | stills |
| No end card (song 11 only); ends on the calm hold with the signature | yes | TITLES has no end_card |

## Never
| Rule | Yes/No | Where |
|---|---|---|
| 1 No white-outs | yes | verify.py near-white pixels; stills 211.5 |
| 2 No white text on pale skies | yes | stills |
| 3 Nothing crossing a reading box or the signature | yes | Clear(); text protection; check_layout.py |
| 4 One expression at a time | yes | check_layout.py |
| 5 No garbled letters while forming or leaving | yes | approved word engine; motion strip |
| 6 No words mirrored in water | yes | reflect=False on every word |
| 7 No dark, brown, solid or mannequin people; big enough | yes | stills (people about a quarter of the frame height at the expressions) |
| 8 No mushy blur, jitter, popping or sliding | yes | motion strip |
| 9 Bottom third calm: no people, bright reflections, rings or particles | yes | Clear(calm) dims light effects below 0.37 of the height; people, crowds, arch, bridge and lights not mirrored; verify.py bottom third brightness |
| 10 Calm camera, never frozen | yes | camera keys; verify.py longest frozen stretch |
| 11 No other logos or watermarks; no realistic faces | yes | stills |
