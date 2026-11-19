# Song 10 backdrop version 2: checklist (every rule in the binding brief)

Checked before the full render on landmark stills (full size and quarter size) and low resolution motion tests; render checks are filled in from tools/s10_full2/finish.py (out/s10_full2/CHECKS.txt). "Yes" means met; any "no" is explained.

## Hard limits
| Rule | Met | Where checked |
|---|---|---|
| Render only in this cloud session; no Render workflow; no paid service; not on the Mac | yes | tools/s10_full2/render_all.sh runs locally in the session |
| No song audio, lyrics, videos or frames in git | yes | git status; .gitignore covers work/ and out/; only code and docs committed |
| No em dash or en dash anywhere | yes | scanned tools/s10_full2 and project-docs/backdrops/s10-full2 for U+2013 and U+2014 |
| Nothing deleted in Drive; MP3s, Lyrics doc, Visual Plan doc untouched | yes | Drive only read; one new contact sheet file added |
| Helpers: Haiku only | yes | two Haiku helpers (Drive rule files, campaign pages) |
| Branch backdrop2/s10-full from tag film10-revision3-approved-2026-11-16; code in tools/s10_full2/, docs in project-docs/backdrops/s10-full2/; no approved promo, engine or other songs' files edited | yes | git diff --stat against the tag |
| Commit trailer; never git add -A | yes | git log |

## Length and timing
| Rule | Met | Where checked |
|---|---|---|
| Music part exactly the live length 3:31 (211.0 s) then a 15 s calm hold; total 226.0 s | yes | render.py clock; prepare provenance.json; finish.py frame count |
| Reference measured; mapped onto the live length (within 1 s: conformed by atempo, sections scaled proportionally) and marked as an estimate | yes | TIMELINE.md "Length and timing" |
| CUES.md with every section start, what is on screen and the calm moment that ends it | yes | CUES.md |
| 60 fps native, 1920x1080 | yes | render.py OUT_FPS 60; finish.py ffprobe |

## Look
| Rule | Met | Where checked |
|---|---|---|
| Pre-dawn under a great lamp; midnight blue and deep gold; one golden horizon light; quiet stars; still, centred | yes | stills 0, 12, 20, 45, 109, 140, 222 |
| No comets | yes | no comet code (s10v2_song.py); stills |
| Own signature effects (rescue threads, rings of still water, gold web); no effect reused from another song | yes | s10v2_song.py; stills 54, 109, 140, 152 |
| First-run weak points fixed: lamp section no longer all-over gold; Heavenly Mother larger; no busy comets 2:11 to 2:40 | yes | stills 45 (Mother about 45 percent of the height, midnight blue sky), 140, 152 |
| Craft kept from Revision 3: word style, people quality, warmth, eased motion, no grain | yes | stills; Revision 3 word and body modules unchanged |

## Expressions and arch
| Rule | Met | Where checked |
|---|---|---|
| Exact wording from words.EXPRESSIONS; website colours | yes | words come from the tag's module (diffed against engine/p3d/words.py at the tag) |
| Expressions only where a lyric line is that act | no lyrics: marked ILLUSTRATIVE | TIMELINE.md "No lyrics yet"; to recheck when lyrics exist |
| Each readable 8 to 10 s with nothing competing; upper middle; people below | yes | 9.3, 9.3, 9.4, 9.0, 9.0 s; stills 62, 79, 96, 123, 198; Clear dims all light inside the reading box |
| Words collapse into their star in the arch | yes | leave="arch" to the star; motion test of Inclusiveness leaving |
| Arch: all nine lit at the start, relights only (brief flare and one new thin ring), all nine at the end | yes | _arch_lit, Relight; stills 12, 96 (ring), 222 |
| People DO the expression (acting table) | yes | ACTING plan in TIMELINE.md; stills |
| Symbols in the world, subtle, in colour, never over the words; hearts drift off each expression | yes | Traced symbols beside the pair after reading, intensity 0.26; spark hearts; still 102.6 |

## People
| Rule | Met | Where checked |
|---|---|---|
| Radiant and whole, gold glitter (crystal not used: PHASEB says only gold is approved); clothed; never dark | yes | stills |
| Fewer people, more light | yes | five pairs, Mother, six on the shore |
| Every touch same gender | yes | Greeting and Consideration two men; Inclusiveness, Encouragement, Gratitude two women |
| Refined movement (Revision 3 gestures, eased) | yes | motion tests |
| Heavenly Mother only from behind or as hands, never a face | yes | still 45 |

## Words on screen
| Rule | Met | Where checked |
|---|---|---|
| Opening readable from frame 0, at least 7 s: logo, HEALING CONCERT, The Words of Mother's Love / That Bring Peace (italic), title large; on calm sky | yes | still 0 and 8 (readable to 8.4 s); lockup above the horizon |
| Signature top left from the end of the opening to the last frame, never flashing, 40 px clear, date capitals about 22 px or more | yes | stills; finish.py signature check on every frame; date line Jost 31 px (capitals about 22 px) |
| Lyric fragments | none: the design names none (no lyrics) | TIMELINE.md |
| Warm white with gold on night skies; nothing dark behind text | yes | stills |
| No end card (song 11 only); ends on the calm hold with the signature | yes | still 222 |

## Never list
| Rule | Met | Where checked |
|---|---|---|
| 1 No white-outs | yes | brightest stills 45, 140; finish.py frame means |
| 2 No white text on pale skies | yes | all skies are night skies |
| 3 Nothing crossing a reading box or the signature | yes | Clear on every light source and on leaving words |
| 4 One expression at a time | yes | TIMELINE.md table |
| 5 No garbled or broken letters while words form or leave | yes | pen arrival and arch leave (approved); opening dissolve shortened to the approved 0.5 s |
| 6 No words mirrored in water | yes | words added with reflect=False |
| 7 No dark, brown, solid or mannequin people; big enough | yes | people about 30 percent of the height in medium shots |
| 8 No mushy blur, jitter, popping or sliding | yes | motion tests; eased camera |
| 9 Bottom third calm | yes | star, arch, people, lantern, dust and lake-light reflections off; lights, rings, threads fade out below a third of the height; feet of people sit near the line |
| 10 Calm camera, never frozen | yes | slow eased moves, breathing drift; finish.py frozen check |
| 11 Only the campaign logo; no realistic faces | yes | stills |

## Render checks (from out/s10_full2/CHECKS.txt, version 2 as first delivered, 2026-11-19)
| Check | Result |
|---|---|
| Frames and length | 13,560 frames decoded in each of the three files; 226.000 s; audio 226.005 s |
| Parts joined without gap or overlap | yes (finish.py asserts every part starts where the last ended) |
| Black frames | 0 (darkest frame mean 31.7 of 255, at 0:54.1) |
| Repeated or frozen frames | 0 identical neighbours; longest frozen run 0.0 s |
| First and last frame | frame 0 is the whole opening lockup (mean 38.2); last frame is the calm hold with the signature (mean 36.7), never black |
| Signature on every frame after the opening | yes: its brightest pixel stays at 255 on every frame from 0:10 (0 dim frames) |
| Sync on 3 hits | 0:25.26 found 0:25.09; 0:51.89 found 0:51.58; 3:24.52 found 3:24.57 (onset of the conformed music; the picture is timed to the same clock) |
| Phone file under 25 MB | 22.6 MB |

Fix 1 render checks are added below when it is delivered.
