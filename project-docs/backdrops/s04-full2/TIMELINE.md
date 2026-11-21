# Song 04, I'm Sorry, Please Forgive Me: full backdrop, version 2, timeline

Concert item 5, Sunday, December 6. Design: `project-docs/designs/04 I'm Sorry, Please Forgive Me.md` ("The Thaw"). Code: `tools/s04_full2/` (song04.py the world, camera, arch and effects; people.py the people of light; cards04.py the opening, the signature and the words; render.py the loader; prepare.sh and export.py). Replaces the first run (branch `backdrop/s04-full`), which was timed to the reference instead of the live length, rendered 30 fps, used the nine comets, showed GRATITUDE (star 2 is first lit in song 08) and had no arch.

## The music

- Reference: the church's upload youtu.be/43seZJ9fTgw, kept as `s04.mp3` on Anthony's private Artifact page (SHA-256 a1fa529d6f6dd5f477a429f7c8587c017ed94efebabe669fa8e05e1dd32e7220). Never committed. Decoded length 219.435 s (10,532,864 samples at 48 kHz).
- Live length (DESIGN-SYSTEM 4): 3:40 = 220.0 s. The reference is within 1 s, so it is used as it is and only conformed: ffmpeg `atempo=0.997430` (pitch kept) to exactly 220.0 s. Every time below is stage time on that conformed music. It stays an estimate until a rehearsal recording exists (the live performance is choir only, a cappella).
- Stage video: 220.0 s of music, then a 15 s calm hold = 235.0 s = 14,100 frames at 60 fps, 1920x1080.
- Measured here: `engine/analyze.py` on the conformed music (features `work/s04v2/features.npz`, SHA-256 7abb811c...0146), a one second loudness pass, onset peaks, and a word level transcript made in this session with a speech model (faster-whisper small.en) to place every lyric moment. The transcript stays in `work/` (never committed); only cue words appear here.

### Sections (loudness in dB below the loudest second)

| Stage time | Section | Loudness |
|---|---|---|
| 0:00 to 0:27.4 | introduction, soft | -20 to -11 |
| 0:27.4 to 1:17.5 | verse 1 (sung by both sisters: the apology, then the forgiving answer) | -16 to -8 |
| 1:17.5 to 1:42.8 | chorus 1, full; loudest 1:25 (0 dB) | -9 to 0 |
| 1:42.8 to 2:09 | interlude, instrumental (the music breathes, then builds) | -16 to -9 |
| 2:09 to 2:35.5 | verse 3 ("we all practice ... with compassion") | -15 to -9 |
| 2:35.5 to 2:59 | chorus 2, full; peaks 2:42 to 2:43 | -7 to -1 |
| 3:00 to 3:33.4 | final chorus ("beautiful unity ... one in your love", twice) | -7 to -1 |
| 3:33.4 to 3:40.0 | the last chord dies away | -11 to -55 |

Note: the design (revision 3) estimated verse 2 and a long final chorus from the studio take. This choir version sings verse 1 with both sisters' lines, an instrumental interlude, and verse 3. The picture follows the measured words.

### Lyric moments used (stage seconds, cue words only)

| Time | Cue | Picture |
|---|---|---|
| 27.4 | "I'm sorry" | the first sister turns to her sister |
| 41.5 | "held her hands" | she takes her sister's hand |
| 44.5 | "truly humbled" | she kneels; fragment |
| 46.8 to 50.8 | "Father and Mother ... opened her heart" | the warm beam; the flower at the heart; fragment |
| 52.6 | "I thank you" | acted only: a hand on her heart (Gratitude's words never appear: star 2 belongs to song 08) |
| 54.7 to 57.3 | "came to me first" | she lifts her sister up |
| 59.3 | "embrace" | the embrace; INCLUSIVENESS |
| 68.1 to 70.1 | "truly humbled herself" | the embrace holds; the line in the ice turns gold |
| 77.5 | chorus 1 | the golden breath |
| 146.1 | "with compassion" | fragment |
| 188.0 | "beautiful unity" | the ring closes |
| 202.7 and 207.4 | "one in your love" | fragment |

## The picture

| Stage time | Picture |
|---|---|
| 0:00 to 0:08.4 | Opening lockup, whole from frame 0: logo, HEALING CONCERT, The Words of Mother's Love / *That Bring Peace*, the song title large, all navy and gold on the calm pale sky. Below: the frozen lake, pearl ice, ice blue sky, a low cold sun in haze at the left; song 03's rose petals lie frozen faintly in the ice. |
| 0:08.4 to 0:10 | The lockup crumbles into frost dust; the camera tilts down to the ice. |
| 0:09.4 to the end | The signature fades in, top left, and stays to the last frame. |
| 0:14 to 0:17 | Two sisters of warm gold light gather out of sparks, far apart, half turned from each other; a thin cold line of light divides the ice between them. |
| 0:26.4 | The first sister turns to her sister. |
| **0:28.0 to 0:40.2** | **APOLOGY** (star 3): arrives 28.0, reads **29.0 to 38.6 (9.6 s)**, then its letters crumble into yellow sparks that fly into star 3 (relit 39.9: a flare and one new thin ring). She bows her head with open hands held low. The Apology symbol (a bowing figure) is traced faintly in yellow stars high on the left; small yellow hearts drift up off the words as they leave. |
| 0:39.4 to 0:41.4 | She crosses first; each step melts a warm glowing pool in the ice. |
| 0:41 to 0:42 | She offers her hand; her sister takes it. |
| 0:43.4 | She kneels, still holding the hand, head bowed. **"truly humbled"** reads 43.4 to 47.0: the letters bow down from above as they appear and sink into the ice as they go. |
| 0:46.4 to 0:53 | A low warm beam runs from the sun across the ice to them. |
| 0:47 to 0:49.4 | Her sister turns to her and lays a hand on her bowed head. |
| 0:47.4 to 0:56 | A small flower of light opens at the hurt sister's heart, ice blue turning rose. **"opened her heart"** reads 49.8 to 53.4: the letters open from the middle outward and leave as rose petals of light. |
| 0:52.8 | A hand on her own heart ("I thank you", acted only, no words). |
| 0:54.8 | She lifts her sister to her feet. |
| 0:56.0 to 0:57.6 | The pair shimmers and re-forms for the embrace. |
| 0:59.0 | The embrace. |
| **0:57.8 to 1:09.2** | **INCLUSIVENESS** (star 4, lit for the first time): arrives 57.8, reads **58.8 to 67.8 (9.0 s)** while they hold each other and sway a little, then green sparks fly into star 4 (lit 68.9; a line of light grows between stars 3 and 4). The Inclusiveness symbol (a hugging face) forms in green petals of light to the right; small green hearts drift up off the words. |
| 1:06 to 1:17 | The line in the ice fills with gold from the middle out, like mended pottery. |
| 1:11.5 to 1:21 | The warm beam returns, softer. |
| 1:17.5 | Chorus 1: the sky starts to warm. |
| 1:21 to 1:42 | The golden breath of Heavenly Mother's love (light only, never a figure) rolls low across the ice from the sun and gathers round the sisters like a hearth (loudest 1:25), then rises and thins. Inside it the two turn to the sun and hold hands (re-formed 1:24 to 1:26). The ice melts in a widening circle; a gold path runs from them to the sun (1:30 to 1:41) and stays. |
| 1:43 to 2:04.5 | Interlude: the two stand hand in hand on the gold path; the camera glides slowly round; song 03's rose petals, freed from the ice, lift off the water and drift up. |
| 2:04.5 to 2:08.5 | The sisters dissolve into rising sparks. |
| 2:11 to 2:32 | Verse 3: people of light form one by one round the lake's centre (the far half of a ring, open toward the audience): a mother with a child, an older couple standing near each other, friends. Only a parent holds a child's hand. |
| 2:25.2 to 2:32.2 | **"with compassion"** reads 146.4 to 151.0: the letters appear like ripples spreading upward from the water. |
| 2:35.5 to 2:50 | Chorus 2: the full thaw. The last ice melts from the middle outward, the line stays gold for good, lanterns rise, warm rays, apricot and rose sky (brightest moment about 2:42). |
| 3:00 to 3:17 | Final chorus: the two sisters form again at the centre, hand in hand; more people join until the ring is closed (3:03 to 3:17). |
| 3:20.6 to 3:29.4 | **"one in your love"** reads 202.0 to 208.0: sparks rise from the ring and settle into the letters; they leave rising. |
| 3:30.5 to 3:36.5 | Everyone dissolves into rising sparks from the outer ring inward, the sisters last; one small warm light rests on the water at the centre and sends a gentle ripple every few seconds. |
| 3:40 to 3:55 | Calm warm hold: the thawed lake in apricot morning light, the low sun, the gold path, the small light, the arch with 3, 4, 7 and 9 lit; slow drift; never black. |

Only one text is on screen at a time; the gaps are at least 0.4 s (Apology out 40.2, "truly humbled" in 42.4; "opened her heart" out 54.4, Inclusiveness in 57.8).

## The arch of nine lights

Across the top of the sky, right of the signature (the engine's shared arch, `engine/arch.py`). Start: 3, 7 and 9 lit (star 7 carries the two thin rings of its relights in songs 02 and 03). 39.9 s: star 3 relit (flare and one new thin ring). 68.9 s: star 4 lit for the first time; the line between 3 and 4 grows. End: 3, 4, 7 and 9 lit. No other star is ever lit.

## Hand-offs

- **From song 03** (design, agreed by message; CONCERT-OVERVIEW): 03 closes on a soft morning lake, sun low at the left, rose petals on the water, arch 3, 7 and 9. Song 04 opens on its own pale frozen version of that morning: same lake and sun place, the petals frozen faintly in the ice, the same arch state. The colours are paler from frame 0 (the opening lockup needs calm sky), not drained during the introduction as the design planned. Song 03's version 2 may have changed its closing frame; the coordinator should compare the two.
- **To song 05:** 04 ends on the agreed frame: a thawed lake in warm apricot morning light, low bright sun, a thin gold path across the water, one small warm light at the centre, no figures, camera level and centred a little above the water, arch 3, 4, 7 and 9.

## Acting plan (who, what, which look, which framing)

| Moment | Acted by | What | Look | Framing |
|---|---|---|---|---|
| Apology 29.0 to 38.6 | the first sister (a woman, left) | head bowed, both hands open and low toward her sister (the PHASEB 6 Apology pose: open_hands with a bow, plus a slow bow) | warm gold glitter, long dress of light, hair in a bun | medium wide from behind her side, both sisters in the middle band below the words |
| going first 39.4 to 43.4 | the first sister | crosses the ice, warm pools under her steps, offers her hand palm up; her sister takes it; she kneels on one knee, head bowed | gold glitter | slow push in |
| her heart opens 47 to 53 | the second sister (a woman, right) | turns to her kneeling sister and lays a hand gently on her head; a rose flower of light opens at her heart; then a hand on her own heart | slightly deeper gold glitter | medium |
| lifted up 54.8 | the second sister | lifts her sister to her feet with the joined hand (forgiveness without embarrassment, the campaign's Inclusiveness) | gold glitter | medium |
| Inclusiveness 58.8 to 67.8 | both sisters (two women) | the embrace, held, swaying very slightly (PHASEB 6: an embrace of two women); the hurt sister's light warms toward rose | gold glitter | medium, the closest framing of the song |
| chorus 1 and interlude | both | side by side facing the low sun, holding hands | gold glitter | wider, the breath and the gold path |
| verse 3 and final | 10 people (4 women, 4 men, 2 children) and the two sisters | stand in a ring facing the centre, swaying gently; a mother and a father each hold a child's hand; nobody else touches | gold glitter, smaller | wide, higher, the ring's open side toward the audience |

Heavenly Mother appears only as the low sun and the golden breath of light.

## Lyric fragments (4, each its own effect, never with an expression)

1. "truly humbled" (43.4 to 47.0): the letters bow down into place from above and sink into the ice as they leave (humility goes lower).
2. "opened her heart" (49.8 to 53.4): the letters open from the middle outward like a flower and leave as rose petals of light.
3. "with compassion" (146.4 to 151.0): the letters appear like ripples spreading up from the water.
4. "one in your love" (202.0 to 208.0): sparks rise from the ring of people and settle into the letters; they leave rising.

## Choices made in this session (Anthony was not available; recorded here)

1. The live length rules: the reference (219.435 s) is conformed to exactly 220.0 s; 15 s calm hold; 60 fps.
2. Lyric times come from a word level transcript of the reference made in this session, not the design's estimates (which assumed a different song structure).
3. GRATITUDE is not shown ("I thank you" is acted only, as the brief allows). Respect is not placed in verse 3 (it stays in song 05).
4. The look is the design's frozen pale winter morning (DESIGN-SYSTEM 6), so all text is navy with a soft white glow (DESIGN-SYSTEM 7), including the expressions: drawn as crisp lettering in the approved Cormorant Garamond italic with the coloured capsule label (the pinned engine cannot paint particle words navy).
5. No comets (song 01 only). Signature effects of this song: the ice and its thaw, the melted footprints, the cold line that turns gold, the warm beam, the heart flower, the golden breath, the freed petals.
6. Both sisters are warm gold glitter people (only two looks are allowed; the design's silver sister would read as cold).
7. Verse 2 of the design (the hurt sister's side) is not in this choir version; her forgiveness happens in verse 1, where the words are.
8. The ending ring is the far half of a circle, open toward the audience, so nobody stands in the bottom third; the heavenly city in the water is not built (no reflections in the bottom third, and it would compete with the people).

## If a rehearsal recording arrives

Stretchable without harm, in order: the introduction (the lockup needs 0 to 10 s; any length from 20 s works), the interlude (1:43 to 2:09), chorus 2, the final ring, and the hold. Harder: verse 1 (the walk, the kneel, the heart and the embrace follow the words) and the two reading windows (keep each at least 8 s). Change the times in `T` at the top of `tools/s04_full2/song04.py`.
