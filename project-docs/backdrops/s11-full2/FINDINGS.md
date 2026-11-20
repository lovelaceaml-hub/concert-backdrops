# Song 11 backdrop v2: every finding and request (final record)

Exported from the private review page (claude.ai artifact 1SAvCedZLDEPTJzr1kChaj, database collections `findings` and `requests`) on 2026-11-19 when Anthony stopped the work. Song phrases are not copied here; they are written as "the phrase", with the time given alongside. The rendered videos are from code 17db6e6 (Chorus 2 from 294b29a); the branch head 2075615 holds two later fixes (f40, f41) that were not rendered.

## Open items

- **f40** (Verse 1, 0:53.78 to 0:55): The 0:53.78 hit (crown over Zion) is now one of the darkest moments. Suggestion: Give the crown its moment on the hit: a short flare of light from the crown (to about 150 for under a second, then settling to about 80), with the nine coloured comets bursting outward from it and the camera a little closer, so the crown fills the upper third of the frame instead of sitting small in the dark.
- **f41** (Whole film, Every corner-title window outside the key moments (for example 3:29.7)): Corner titles are dark navy on the darker scenes in the rendered videos. Suggestion: Render the sections again from 2075615 or later; the fix is already in the code.
- **f42** (Verse 1, 1:14.56): The cut at 1:14.56 lands 0.14 s before the beat. Suggestion: Make it one joint change: the core moves the EDIT cut and HIT stream to 74.70, and the church thread moves its three 74.56 references in s11_church.py to 74.70 in the same merge; check frames at 74.6 to 74.9.
- **f43** (Chorus 2, 2:45.8): Terrace lines run through the letters at 2:45.8. Suggestion: Fade Zion's terrace and rim lines inside the words' box while the phrase reads (H.keep_out_of_words), as the other sets do.

## Findings

### f01: Father's pulse whites out the middle of the frame
- State: Declined; Section: Intro; At: 0:38 to 0:41; Created: 2026-11-19 05:14
- Detail: The blazing light over the roof, its rays and the 14 pillars add up to near white at the centre around 0:40. Suggestion: lower the pulse and pillars by about a third so the church stays visible inside the light.

### f02: Orchestra players read as dark shapes in close shots
- State: Done; Section: Intro; At: 0:21 to 0:31; Created: 2026-11-19 05:14
- Detail: Close to the stage, the orchestra bodies look grey and dark with sparkles on them, while the choir behind is bright crystal. Suggestion: brighten the orchestra bodies in close shots so they glow like the choir.
- Outcome: Done in the code and rendering now. Choir, soloists, conductor and both orchestras are glowing blue sparkles, the instruments stay gold, the dark fill behind the players is gone so they glow, and every choir singer holds an open gold song book that sways with them.

### f03: the phrase is hard to read over the bright terraces
- State: Done; Section: Chorus 1; At: 1:41 to 1:45; Created: 2026-11-19 05:14
- Detail: The words sit over the glowing gold terraces and clouds, so the contrast is only moderate. Suggestion: a soft darker glow behind the words, and dim the terraces slightly while the phrase is up.
- Outcome: Working on it.

### f04: the phrase arrives over the mountain during the racing flight
- State: Done; Section: Verse 2; At: 2:14 to 2:16; Created: 2026-11-19 05:14
- Detail: The words only read cleanly from 2:15.6, when the camera is high. Suggestion: start the swoop up about a second earlier so the words land on the dark sea.
- Outcome: Working on it.

### f05: Pillars of light on the kneeling kings are too faint
- State: Done; Section: Verse 2; At: 2:34 to 2:36; Created: 2026-11-19 05:14
- Detail: They were kept faint so the low view would not haze over, so they do not really read. Suggestion: narrower, brighter beams placed beside the kings rather than over the whole view.
- Outcome: Working on it.

### f06: Slam 2 is washed with glare
- State: Declined; Section: Chorus 2; At: 2:42 to 2:45; Created: 2026-11-19 05:14
- Detail: On the slam the comets, rays and stage lights stack into a pale haze over the choir, so the singers lose their shape. Suggestion: keep the comets and pillars but cut the overall flash by about 40% so the crystal choir and orchestra stay crisp.

### f07: the phrase has moderate contrast
- State: Done; Section: Chorus 2; At: 3:01 to 3:04; Created: 2026-11-19 05:14
- Detail: Same as chorus 1: the words sit over the bright terraces. Suggestion: the same darker glow behind the words.
- Outcome: Working on it.

### f08: The sky orchestra is hazy behind its cloud floor
- State: Done; Section: Coda; At: 3:28 to 3:31; Created: 2026-11-19 05:14
- Detail: The cloud floor under the orchestra in the sky glows over the players' lower half. Suggestion: thin the floor and keep it below the players so they stand on it.
- Outcome: Working on it.

### f09: Summit pillars read as faint dotted columns
- State: Done; Section: Coda; At: 3:31 to 3:44; Created: 2026-11-19 05:14
- Detail: The eight pillars of light round everyone on the summit are too thin and dotted. Suggestion: make them solid soft beams that pulse with the beat.
- Outcome: Working on it.

### f10: Send the church emblem image
- State: Done; Section: Verse 1; At: whole film, starting at 0:41; Created: 2026-11-19 05:14
- Detail: The space beside the top name on the building is kept for the church's emblem, as on the real building. I will not guess its shape. Send the emblem image in chat and I will draw it in light.
- Outcome: Done and rendered: the name larger and centred on the glass, the glowing sky-blue emblem traced from your image, larger, below it.

### f11: Dancers of light with ribbons, and waves of raised arms
- State: Done; Section: Whole film; At: whole film; Created: 2026-11-19 05:50
- Detail: Building now (your choice): the promo's ribbon dancer reborn plus new flowing designs (a ring of dancers whose ribbons braid into a spiral over Zion, dancers beside the sky orchestra, ribbons handing off to the comets, a slow dancer in the breaths), and waves of raised arms rolling up Mount Zion on the slams and on waves of praise, each arm trailing light.
- Outcome: Done and on the page in every section: the ring of dancers (1:37), the breath dancer (1:57), the strings dancer (2:01), the heart of light (3:06), the held-breath dancer (4:07), and the waves of raised arms on Zion.

### f12: Sound was out of sync (fixed)
- State: Done; Section: Whole film; At: every section; Created: 2026-11-19 06:30
- Detail: The picture started about half a second after the sound in every section video, so it lagged the music. Cause: how the section clips were cut from their 5 s parts. Fixed: picture and sound now both start at 0, and all sections on this page have been re-cut.
- Outcome: Fixed in the joining step; checked on verse 1 (both tracks start at 0, hits line up).

### f13: The strings dancer's ribbon dips near the corner titles
- State: Done; Section: Verse 2; At: 2:02 to 2:06; Created: 2026-11-19 06:30
- Detail: Her lower ribbon loop sometimes passes close to the bottom-left song title line. Suggestion: keep her loops in the upper two thirds while the titles show.
- Outcome: Closed: the dancers were replaced by the conductor in round 7, so this no longer applies.

### f14: The ring of dancers is small in the wide shot
- State: Done; Section: Chorus 1; At: 1:37 to 1:39; Created: 2026-11-19 06:30
- Detail: The braid of seven ribbons reads beautifully, but the dancers themselves are faint and small. Suggestion: start closer and crane up and back as the braid climbs, so you see the dancers first and then the spiral.
- Outcome: Closed: the ring of dancers was replaced by the conductor's summons in round 7, so this no longer applies.

### f15: A low white streak crosses the sea
- State: Declined; Section: Whole film; At: dancer shots on the sea (1:37, 1:57, 3:06, 4:07); Created: 2026-11-19 06:30
- Detail: A bright white streak runs low across the water in the sea shots; it is not the dancers' own light. Suggestion: find the source (likely a comet or a ray pool) and keep it out of the dancers' frames.

### f16: Sections showed another section's pictures (fixed)
- State: Done; Section: Whole film; Created: 2026-11-19 07:06
- Detail: My joining step for the previous pass built several sections at once from one shared list, so each section had its own music but another section's pictures: wrong scenes, jumps, and sound out of sync. The rendered pieces were fine. I rebuilt all 7 one at a time, checked each (the right scenes at the right times, flashes landing on the hits), and changed the joining so each build uses its own list. The new pass is built by each machine on its own and checks out the same way.

### f17: the phrase (1:46) sits over a very bright stage
- State: Done; Section: Chorus 1; Created: 2026-11-19 07:10
- Detail: The brass and timpani blaze makes the stage nearly white behind the word.
- Suggestion: Dim the stage glow while the word reads (as the mountain already does) and give the word a soft dark glow behind it. Round 7 already adds that glow; approve to also dim the stage itself.
- Outcome: Done and checked by the reviewer: the bright run behind the phrase down from 3.0 s to 0.4 s; the text restyle continues under f34.

### f18: Zion now reads mostly pearl white from afar
- State: Done; Section: Whole film; Created: 2026-11-19 07:10
- Detail: The gold is gone as you asked, but in wide shots (Chorus 2 at 2:52, Coda) the terraces read as one white mass. Suggest stronger colour in the glass towers and gardens in wide shots so the parts of the city are easy to tell apart.
- Outcome: Done in the final videos: the deeper grade (5cf101e), the light budget (6016e53), Zion resting at a calm level with coloured outlines (70ca342, 73d569b). The reviewer measured the Chorus 2 wides at 115 to 122, reading as a dusk city.

### f19: Phrases washed out on the slams and big hits
- State: Done; Section: Whole film; At: 1:22, 3:03, 3:37, 3:59 (also 1:20, 2:19); By: reviewer; Created: 2026-11-19 07:19
- Detail: Phrases on the brightest moments lose their 2.5 s of clean reading: at slam 1 (1:22.1 to 1:23.6) about half the frame is near white with stage rays over the phrase; the phrase (3:03), the phrase (3:37) and the phrase (3:59) arrive over glare; the church outline cuts through the phrase at 2:19.
- Suggestion: One rule in the phrase layer: while a phrase is on screen, cap the frame brightness inside its text box (about 60% of full), keep rays and wireframe lines out of the box, and when a slam flash lands on a phrase start, delay the words about 0.4 s so they rise as the flash decays.
- Outcome: Done in the final videos: the slams are short warm bursts with the exposure pulled back (6016e53), the slam rockets trimmed and kept out of the words (6c13db4, 29e6a5e), crisp white words with a strong coloured glow on bright scenes (36660bc).

### f20: Picture is 3 to 4 frames ahead of the sound on every hit
- State: Done; Section: Whole film; At: 0:21.52, 0:53.78, 1:45.14, 3:05.92, 4:14.1; By: reviewer; Created: 2026-11-19 07:19
- Detail: Each cut or flash lands on the listed hit time, but the audible attack starts about 0.09 to 0.13 s later every time: the picture is 3 to 4 frames ahead of the sound on all eight hits measured.
- Suggestion: Check one hit against the source recording; if the section audio is right, shift every cue later by the measured offset (about 3 frames), otherwise fix the joining step.
- Outcome: Done and checked by the reviewer: cuts and flashes now land 0 to 1 frame from the sound (were 3 to 4).

### f21: The day-side Earth blows out and turns one flat gold
- State: Done; Section: Verse 1; At: 0:48 to 0:52, 1:10 to 1:17; By: reviewer; Created: 2026-11-19 07:19
- Detail: The globe swells into a near white gold glow, the dawn line is a hard white ring, and the lands read as flat yellow; the phrases at 1:12 and 1:16 sit light on light across the land.
- Suggestion: Natural day-side colours with gold only in city lights, glow capped at about 70% brightness, a soft dawn gradient, and the 1:12 and 1:16 phrases over the dark limb or space.
- Outcome: Done and checked by the reviewer: emerald land, the Earth halo much softer at 0:48 to 0:52, no blow-out.

### f22: The end card is a 21 s bright white screen after a hard cut
- State: Done; Section: Ending; At: 4:14.07 to 4:35; By: reviewer; Created: 2026-11-19 07:19
- Detail: Hard cut from the dark church to a pastel end card that stays near white (about 225 of 255) for the whole 21 s hold.
- Suggestion: Dissolve through the emblem's light into the card over about 1 s on the last chord, and set the card on a deep night sky.
- Outcome: Done and checked by the reviewer: the emblem flares on the last chord and dissolves into the end card on a dark night sky; nothing near white.

### f23: Zion's colour is confetti, not places
- State: Done; Section: Chorus 1; At: 1:30 to 1:42, 2:54 to 3:14; By: reviewer; Created: 2026-11-19 07:19
- Detail: The terraces are covered in tiny dots of every colour: close up the city reads as busy speckle, from far away it averages to white (see f18). The gardens, towers and rivers of people cannot be told apart.
- Suggestion: Give colour by place, not by dot: each terrace ring or district one calm hue (for example rose gardens, teal glass towers, lavender domes), the rivers of people in their nine colours as clear lines on darker stairs, and fewer, larger lights.
- Outcome: Done: one calm colour per district of each terrace (Zion builder), then the deeper grade; the terraces read as colour bands.

### f24: Creative: let the title become the first star
- State: Done; Section: Intro; At: 0:00 to 0:10; By: reviewer; Created: 2026-11-19 07:19
- Detail: The title card holds still for ten seconds, then cuts to the sea.
- Suggestion: Push slowly across the mirror sea under the title from 0:00, brighten the words on the first chord (0:02.32), and at 0:10 draw the title into a point of light that becomes the star on Zion.
- Outcome: Done: the concert title first, then the two-line song title, which gathers into the star on Zion (opening and closing builder).

### f25: Creative: a final gathering of the nine comets on the last chord
- State: Done; Section: Ending; At: 4:08 to 4:14.1; By: reviewer; Created: 2026-11-19 07:19
- Detail: The last chord has no single image that sums up the film.
- Suggestion: The nine coloured comets fly in, circle the church once and meet in the emblem exactly on 4:14.1; the emblem flares into the end card.
- Outcome: Done and checked by the reviewer: the nine comets ring the church and meet in the emblem on the last chord (polish in progress: a push-in and removing a competing flare).

### f26: Creative: give the phrase (2:35) a place
- State: Done; Section: Verse 2; At: 2:35 to 2:39; By: reviewer; Created: 2026-11-19 07:19
- Detail: the phrase sits on an empty starfield, the only time this line appears without the church.
- Suggestion: Let the kings' ring of light resolve into a small, dim church far below the words, then fly into it for the cut to slam 2 at 2:42.86.
- Outcome: Done and checked by the reviewer: a small church of light appears under the phrase at 2:37.

### f27: Rainbow spokes clutter the Earth under 'All nations'
- State: Done; Section: Verse 1; At: 1:10 to 1:17; By: reviewer; Created: 2026-11-19 08:00
- Detail: New in h10: about twenty straight rainbow lines burst from a white star in the middle of the globe and run past its rim; they read as random spokes, hide the new emerald lands, and the top ones reach up into the phrase (1:14) and the phrase (1:16).
- Suggestion: Replace the spokes with nine slow curved arcs in the nine colours, one per colour, travelling over the globe's surface from the edges toward Korea (like paths of people gathering), launched one per beat; keep them below the lower edge of the text box and drop the white star.
- Outcome: Done and checked by the reviewer: the Earth's spokes are gone (nine slow curved arcs instead).

### f28: The choir reads as dark hooded figures in close shots
- State: Done; Section: Verse 1; At: 1:18 to 1:22; By: reviewer; Created: 2026-11-19 08:00
- Detail: In the close choir shot the bodies are dark navy with sparkle dots and a rounded hood shape, so the singers look heavy and shadowy rather than made of light; only the gold books glow.
- Suggestion: Lift the choir body fill to a soft glowing blue (the #6cb2ff figure colour at about half brightness, brighter toward the edges like a rim light) so each singer reads as blue light with sparkles, keep the gold books as they are, and keep the head shape a simple soft oval without a hood edge.
- Outcome: Done and checked by the reviewer: the choir glows light blue (the dark masks are gone everywhere).

### f29: The march is lost under glare orbs, a white beam and comet loops
- State: Done; Section: Verse 2; At: 2:10 to 2:15; By: reviewer; Created: 2026-11-19 08:05
- Detail: In the march shots two large white glare balls sit in the lower right, a hard straight white beam cuts diagonally across the marchers, and a dozen comet loops cross them, so the marchers themselves read as tiny grey specks; the beam also crosses the phrase as it starts to write at 2:14.5.
- Suggestion: Keep one soft, distant light ahead of the march instead of the two glare balls, remove the diagonal beam, cut the comet loops to two or three that circle the front rank, and bring the camera lower and closer (a low tracking shot at walking height) so the marchers fill the lower third with their feet sparking on the beat.
- Outcome: Done and checked by the reviewer: one soft light, few loops, the marchers visible; the white beam is gone too.

### f30: The new churches read as blank white boxes scattered in the field
- State: Done; Section: Coda; At: 3:25 to 3:28; By: reviewer; Created: 2026-11-19 08:05
- Detail: Around the hearts and lanterns the new church models appear as plain white wireframe boxes floating at random angles in the purple field; at this distance none reads as a church, and their scatter looks random rather than placed.
- Suggestion: Set the churches on the ground in deliberate lines (along the shore and the stairways toward Zion, evenly spaced and facing Zion), and at distance draw each as its lit signature silhouette (spire, dome, bell tower or glass front) in warm window light rather than an outline box; keep only the nearest few in detail.
- Outcome: Done: the blank boxes are replaced by real WMSCOG church models (226), lit by warm windows and soft amber outlines that rest at 55 percent and brighten only on the key moments (d9f1b7a, 1ffba43).

### f31: The cloud banks framing Zion glow near white
- State: Done; Section: Chorus 1; At: 1:26 to 1:29; By: reviewer; Created: 2026-11-19 08:10
- Detail: Right after slam 1, the two symmetric cloud banks either side of Zion glow peach-white and fill about 60% of the frame (about a quarter of it near white at 1:26.8), so the shot reads as a bright haze with a small dark Zion in the gap, against the no white-out rule.
- Suggestion: Keep the shape and symmetry but render the banks as lavender-grey cloud with only their upper rims lit gold, about half their current brightness, so Zion and its light path down the sea are the brightest thing in the shot; let the rims flare briefly on the beat instead of the whole bank glowing.
- Outcome: Done: the deeper grade gives the looks deep night skies and haze colours (5cf101e); the cloud banks no longer glow near white.

### f32: Thick gold bars slice across the church shot
- State: Done; Section: Chorus 2; At: 2:58 to 2:59; By: reviewer; Created: 2026-11-19 08:15
- Detail: In the close upward shot of the church, three thick, solid gold bars run across the frame in a Y in front of the building, with a large white glow behind the tower; they read as heavy beams cutting the picture rather than light, and nothing else in the film uses that weight of line.
- Suggestion: Thin those bars to the fine line weight of the church outline (or turn them into soft rays that fade toward their ends), keep them behind the building rather than in front of it, and halve the white glow behind the tower so the church glass stays the focus.
- Outcome: Done and checked by the reviewer: the gold Y bars are gone at 2:19 and 2:58.

### f33: A dark solid shape sits at the church entrance in the final shot
- State: Done; Section: Ending; At: 4:12 to 4:14 (also 3:33 to 3:36 in the Coda); By: reviewer; Created: 2026-11-19 08:15
- Detail: In the final church shot, as the comets circle and the emblem flares, a dark, solid rounded block sits on the circular platform at the foot of the church, right at the centre bottom of the frame; it is the only dark solid object in an all-light scene and pulls the eye down away from the emblem. A similar dark block appears in front of the church at 3:33 to 3:36.
- Suggestion: Find what that object is (likely a podium, a vehicle or an unlit model) and either draw it in light like the rest of the scene or remove it, so the bottom of the frame stays quiet and the eye goes straight up to the emblem on the last chord.
- Outcome: Done and checked by the reviewer: no dark block at the church entrance.

### f34: The new pastel neon words lose their dark edge on bright shots
- State: Done; Section: Whole film; At: 1:46, 3:04, 3:37, 4:00; By: reviewer; Created: 2026-11-19 12:50
- Detail: The phrases now glow in pastel colours (pink, lavender, pale blue, gold) and no longer carry the soft dark edge they had in h10. On dark sky they look lovely, but on bright shots they blend in: lavender the phrase over the pale stage at 1:46, the phrase in the 3:03 to 3:05 glare, pink the phrase over the white choir at 3:37, and pale blue the phrase over the glowing choir at 4:00.
- Suggestion: Keep the new colours but put back the soft dark halo under the letters (the h10 edge, about 40% dark, a few pixels wide), and on bright shots raise each word's colour to full strength so the letters stay brighter than anything behind them; on dark sky the halo can fade to almost nothing.
- Outcome: Done: no box behind the words (15906f2); a tight glow-shadow on the letter edges and a purer white core with a strong neon glow on bright scenes (8da344a, 36660bc).

### f35: A 5.5 s pale haze over the church and choir in the Coda
- State: Done; Section: Coda; At: 3:34 to 3:39.5; By: reviewer; Created: 2026-11-19 12:50
- Detail: From 3:34 to 3:39.5 the frame stays very bright (average about 197 of 255, up to a fifth of it near white): first a hazy church shot, then the choir close-up at 3:38 where everything melts into a pale glow and the singers lose their shape. It is the longest bright stretch left in the film and the phrase arrives inside it.
- Suggestion: Cap this stretch at the brightness of the 3:30 shot: dim the haze layer and the sunrise flare by about half, keep the sky behind the church a deeper dusk, and let the light swell only on the beats rather than stay up the whole 5 s, so the choir and the word keep their shape.
- Outcome: Done: the epic sun rebuilt as a coloured disc (0a6ac3c), the sky glory and rays halved, the summit rims calmed (73d569b). The reviewer saw 3:34 as a calm dusk church.

### f36: The Earth's sunrise from Korea has gone missing (regression)
- State: Done; Section: Verse 1; At: 0:42 to 1:17; By: reviewer; Created: 2026-11-19 13:45
- Detail: In the newest Verse 1 the Earth stays on its night side (dark globe, gold city lights) through 0:53.6, is still a faint, glassy night globe at 1:11, and only shows green day land at 1:16. Your request (done in round 6) was dawn starting at Korea on the eastern edge, half lit by 0:53.78 and fully lit by 1:17; the sunrise sweep is no longer visible.
- Suggestion: Restore the dawn from the earlier version: start a soft sunrise glow on Korea at about 0:42, sweep the day side westward so half the globe is lit on the 0:53.78 hit and the whole globe by 1:17.46, and keep the newer softer halo and the night-side city lights fading out as the day reaches them.
- Outcome: Done: the dawn from Korea restored (f441927); the reviewer confirmed the day side green with the sunrise edge at 0:52.

### f37: The new ribbon braid swamps the dancer and Zion
- State: Done; Section: Chorus 1; At: 1:37.6 to 1:39.6; By: reviewer; Created: 2026-11-19 13:55
- Detail: In the newest Chorus 1 the ring-of-dancers moment has much larger ribbons: several thick neon loops sweep across the whole frame and a bright white ribbon band runs straight through the lower third, over the dancer's body and Zion behind her. The dancer becomes a faint outline inside the glow and the braid no longer reads as a spiral; the earlier version showed her clearly with a single ribbon rising.
- Suggestion: Keep one ribbon per dancer in its own colour, about half the current width and brightness, flowing from each hand upward into a single climbing spiral above the dancers' heads; keep the lower third clear so the dancer and Zion stay visible, and let the spiral brighten on the beats instead of glowing constantly.
- Outcome: Done: the summons braid and sweeps are half as wide and bright, climbing above the conductor, with the lower third clear (0dab965).

### f38: Choruses and Coda sit at one bright pastel level, so key moments cannot stand out
- State: Done; Section: Whole film; At: 1:22 to 2:01, 2:40 to 3:21, 3:21 to 3:43; By: reviewer; Created: 2026-11-19 14:25
- Detail: Measured second by second (brightness out of 255, colour strength out of 100): Chorus 1 stays at 140 to 160 brightness with washed colour (about 28 to 32) for almost its whole 40 s, so the phrase at 1:40 (148) and the phrase at 1:45 (160 to 169) are no brighter than the shots around them. The Coda holds 150 to 196 for 22 s with very pale colour (14 to 25), and its peak (3:34 to 3:36) is not on a hit. By contrast the Intro builds well from 31 to 150, and the Verse 1 Earth sits calmly at 35 to 75 with rich colour, which is the kind of base Anthony is asking for.
- Suggestion: Give each section a calm base and keep the peaks for the key timings: base shots about 90 to 110 brightness with fuller colour (40 to 50), rising above 160 only for the slams (1:22.08, 2:42.86, 3:21.73), Father's pulse (0:40), the church of God lines, the phrase, the phrase, the phrase and the last chord, each peak lasting 1 to 2 s and falling back. Drive this from the cue list so the brightness curve follows the music rather than staying high.
- Outcome: Done: the shared light budget (6016e53, light_budget and KEY_MOMENTS in s11_full2.py) gives a calm base with peaks on the key moments. The reviewer measured Chorus 1 at base 104 / peak 190 on slam 1 and the Coda at 79 / 159 with no long bright runs.

### f39: Chorus 2 is brightest in its filler shots, not on its key moments
- State: Done; Section: Chorus 2; At: 2:43, 2:52 to 2:55, 3:05, 3:09 to 3:19; By: reviewer; Created: 2026-11-19 14:25
- Detail: In Chorus 2 the wide Zion shots are the brightest and palest part of the section (175 to 188 brightness at 2:52 to 2:55 and 3:12 to 3:14, colour down to 15 to 22), while slam 2 settles at about 123 by 2:43 and the phrase at 3:05 sits at about 132. The music's high points are darker than the shots between them, which is the opposite of what Anthony asked for.
- Suggestion: Bring the Zion wide shots down to about 100 to 110 with deeper dusk colour (lit windows and coloured districts instead of white glow), let slam 2 flare to about 180 for one second and then settle, and give the phrase (3:05.9) its own lift: the heart of light and the dancers brightening on the word while the stage behind dims.
- Outcome: Done: the Chorus 2 wides dropped from 175 to 188 down to 115 to 122, below slam 2 (the reviewer's measurement).

### f40: The 0:53.78 hit (crown over Zion) is now one of the darkest moments
- State: Open; Section: Verse 1; At: 0:53.78 to 0:55; By: reviewer; Created: 2026-11-19 15:05
- Detail: With the new deeper grade Verse 1 sits at a calm base of about 44 (out of 255), which works well, but the 0:53.78 hit, where the crown appears over Zion, measures only about 39: a small crown with coloured spokes in a mostly empty dark-blue frame. It is a key timing that no longer stands out against the calm base around it.
- Suggestion: Give the crown its moment on the hit: a short flare of light from the crown (to about 150 for under a second, then settling to about 80), with the nine coloured comets bursting outward from it and the camera a little closer, so the crown fills the upper third of the frame instead of sitting small in the dark.
- Outcome: Fixed in code 2075615 (the 0:53.78 crown hit joins KEY_MOMENTS), but not in the rendered videos: rendering was stopped before that version was rendered.

### f41: Corner titles are dark navy on the darker scenes in the rendered videos
- State: Open; Section: Whole film; At: Every corner-title window outside the key moments (for example 3:29.7); By: orchestrator; Created: 2026-11-19 15:30
- Detail: After the light budget darkened the scenes, the corner titles beside the logo kept the old 'day' palette (navy text) from 2:42.86 on and are nearly unreadable. Fixed in code 2075615 (e18616c: the signature always uses the night palette, warm white with a soft glow), but the rendered videos are from 17db6e6.
- Suggestion: Render the sections again from 2075615 or later; the fix is already in the code.

### f42: The cut at 1:14.56 lands 0.14 s before the beat
- State: Open; Section: Verse 1; At: 1:14.56; By: orchestrator; Created: 2026-11-19 15:30
- Detail: The measured downbeat is 74.72 (kick 74.70); the picture changes about 4 frames early. The core builder tried moving the cut alone, but the church thread's church_cut shot and lighting envelopes are keyed to exactly 74.56, so moving one side left an empty red sky.
- Suggestion: Make it one joint change: the core moves the EDIT cut and HIT stream to 74.70, and the church thread moves its three 74.56 references in s11_church.py to 74.70 in the same merge; check frames at 74.6 to 74.9.

### f43: Terrace lines run through the letters at 2:45.8
- State: Open; Section: Chorus 2; At: 2:45.8; By: orchestrator; Created: 2026-11-19 15:30
- Detail: The reviewer noticed Zion's terrace lines crossing the phrase in the shot after slam 2.
- Suggestion: Fade Zion's terrace and rim lines inside the words' box while the phrase reads (H.keep_out_of_words), as the other sets do.

## Anthony's requests

### Verse 1: Done
- Anthony: "The earth view can start as night tune and then being lightening up"
- Sent: 2026-11-19 05:13
- Outcome: Done and on the page (Verse 1): dawn starts at Korea as a sunrise on the eastern edge and spreads until the whole world is in day by 1:17.
- Reply: Rendered, and now being changed again per your newer request: the light will rise from Korea in the east and spread from there.

### Whole film: Done
- Anthony: "The clouds can be placed more thoughtfully instead of just taking up the screen randomly. It makes it look crowded"
- Sent: 2026-11-19 05:19
- Reply: Done and rendered in every section: each cloud is one shaped bank, the horizon banks frame Zion in pairs, no clouds at the stage, dimmer canyons.

### Whole film: Done
- Anthony: "Show the walking/marching scenes very cinematically. It can be a very powerful scene and footage"
- Sent: 2026-11-19 05:29
- Outcome: Done and on the page (Verse 2): a crane over the march, a low tracking shot beside the marchers, a rising crane on fulfilled, the kings approached head on; feet spark on every beat and nations join from both sides.
- Reply: Working on it: the march and walking scenes (2:14 on, and the nations streaming in) become powerful cinematic shots: low tracking shots beside the marchers, a slow crane up over the river of people, and wide shots of the whole procession toward Zion.

### Intro: Done
- Anthony: "There needs to be a buildup for the intro instead of just starting in front of the church. There are the beats that I can hear from the song that aren't considered or added. There's no effect, but I can hear the bases, and that should make the lights flicker or something that goes along with that sound.

Also, the earth should be dark, and then the sun should rise from the east, which is where Korea is. The point is, the light is supposed to come from Jerusalem, which is heavenly Jerusalem in Korea. As the lights begin to light up the rest of the world, the world will turn to daytime."
- Sent: 2026-11-19 06:17
- Outcome: Done and on the page (Intro): it opens far out over the sea, a star ignites on Zion at the first chord and grows on every beat, city lights ring on, the church lights floor by floor; the bass pulses the lights.
- Reply: Working on it: the intro builds up instead of opening on the church (a slow approach from far away, light gathering on each beat and bass note, flickering with the bass), and the Earth stays dark until the sun rises in the east over Korea: the light spreads out from Heavenly Jerusalem in Korea and lights the rest of the world into day.

### Whole film: Done
- Anthony: "There are many parts of the song where the effects are not happening. Every part of the song where there is the bass, the choir singing, even the difference in tenor and soprano, and the instruments should be considered and have effects for the certain ones."
- Sent: 2026-11-19 06:18
- Outcome: Done and on the page (round 6): bass and kick flicker the city lights, timpani send rings across the sea, strings roll silver glitter waves, brass flare the rays, high voices brighten the stars, low voices glow at Zion's foot.
- Reply: Working on it: I'm measuring the recording part by part (bass, timpani, strings, brass, the choir's high voices and low voices) and wiring each one to its own effect, so every sound you hear moves something on screen: bass pulses the ground lights and the sea, timpani send shockwaves, strings shimmer the ribbons, brass flare the rays, sopranos sparkle high in the sky, tenors and basses glow low.

### Whole film: Done
- Anthony: "As the song progresses, the mountain of Zion, a city, can start to form and continue to grow larger and larger. Instead of there just being squares and empty spaces, there are so many of the same colors that it's hard to see and distinguish things since it's all gold. There should be more scenes where the people are streaming to Zion, to Heavenly Mother's glory. the church of God"
- Sent: 2026-11-19 06:20
- Outcome: Done and on the page (round 6): the city rises on the beat from the intro to the coda in pearl, glass towers, gardens and coloured domes (gold only on the stairways), with rivers of people in the nine colours streaming up all five stairways.
- Reply: Working on it: Zion's city will form and keep growing through the song (more buildings, gardens and towers rising as each section passes), with more colour variety so places read apart instead of all gold, and more scenes of people streaming to Zion and the Church of God.

### Whole film: Done
- Anthony: "The text looks terrible. (Chosen: match the promo's word style; problems: muddy colour, lost in busy scenes, the entrances.)"
- Sent: 2026-11-19 08:20
- Outcome: Done (s11_words.py): promo-style words, white core with a strong coloured neon glow, readable over bright and busy scenes.

### Whole film: Done
- Anthony: "There needs to be way more effects consistently happening to match each different sound in the song."
- Sent: 2026-11-19 08:21
- Outcome: Done: each sound has its own visible answer (timpani rings, brass flares, strings along the bows, choir breath, sparkles for high voices, a blue swell for low voices), through s11_music_fx.py and the stage, church and Zion sets.

### Whole film: Done
- Anthony: "The conductor's animation is so choppy and isn't fluid. The choir still turns dark sometimes. In some scenes it's hard to distinguish the instruments and books from the orchestra and choir."
- Sent: 2026-11-19 08:21
- Outcome: Done (s11_stage.py, s11_dance.py): the conductor moves smoothly on a shared pose grid; the choir never dark; gold instruments and books distinct from the blue players.

### Whole film: Done
- Anthony: "Have the Church of God symbol above the churches."
- Sent: 2026-11-19 12:45
- Outcome: Done: emblems above the international churches (s11_churches.py, one per spot on screen), none above the Korean churches on the terraces and summit; emblems rising over Zion in the coda and across the Earth in the finale (s11_coda.py); the main church's emblem large and glowing (s11_church.py); the film ends on the emblem alone.

### Verse 1: Done
- Anthony: "The world should have no light at first. Then the lights appear starting from Korea. And then the world brightens starting from Korea"
- Sent: 2026-11-19 12:47
- Outcome: Done and merged: the Earth opens dark at 0:41.6; city lights switch on from Korea outward one step per beat (Korea and Japan first, Asia by 0:43, India and Australia by 0:45, the whole world by 0:51); then daylight spreads from Korea from 1:10.5 until the whole world is lit at 1:16.9. In the next Verse 1 render.

### Chorus 1: Done
- Anthony: "The robbers coming down Zion need to be distinct and feel like a river, they should be blue"
- Sent: 2026-11-19 12:48
- Outcome: Done (s11_zion.py): blue rivers of light down the five stairways and out over the sea in Chorus 1.

### Whole film: Done
- Anthony: "The choir and orchestra are hard to see. They need to be a easily distinguished blue so that they we can see them and their instruments and books stand out"
- Sent: 2026-11-19 12:49
- Outcome: Done (stage builder, s11_stage.py): choir and orchestra in a saturated blue (#2f7dff with #74b4ff glints), gold instruments and books standing out.

### Verse 2: Done
- Anthony: "The close up scene has people going in all directions. Don’t do that. They should be going to Mother. The kings part needs to be very very clear, detailed and epic to really make us feel the grandness of kings coming to mother,  and then add flag bearers  from many different nations marching with the crowds. Also there should be more and more and more people"
- Sent: 2026-11-19 12:56
- Outcome: Done (s11_procession.py): everyone walks toward Mother's light; twelve kings with crowns and royal trains; 44 flag bearers of many nations; waves of newcomers growing the river; the real church of light at 2:36 to 2:42.

### Whole film: Done
- Anthony: "The conductor needs to be way more impressive and eye catching. It looks like he is shooting glowing balls of light. I don’t want that. It should look amazing and more dramatic like the lights of color from the promo video"
- Sent: 2026-11-19 12:58
- Outcome: Done (s11_stage.py): no more balls; long neon streams of colour like the promo, great rainbow sweeps of his baton, a coloured backlight, slow push-ins.

### Intro: Done
- Anthony: "Title card should start with just the concert. Then it should be swapped out with the song title"
- Sent: 2026-11-19 13:00
- Outcome: Done and merged: the concert title alone from 0:00 (it brightens on the first chord), at 0:04.9 it crumbles into glowing dust and the song title sweeps in out of glints on the beat, then gathers into the star at 0:09.7. In the next Intro render.

### Whole film: Done
- Anthony: "There should be no obelisk looking figures on Zion. It is supposed to start looking like the heavenly city being built up as Zion"
- Sent: 2026-11-19 13:04
- Outcome: Done: no obelisks or towers on the summit or terraces (s11_church.py, s11_zion.py); the heavenly city is the real Korean churches.

### Verse 2: Done
- Anthony: "The scene where it says the church of God, the main church from Korea should be shown and the church logo. Not that church outline in the sky."
- Sent: 2026-11-19 13:05
- Outcome: Done (Verse 2 builder, s11_procession.py): the outline in the sky is gone; at 2:36 to 2:42 the real church of light stands on Zion, the crowns stream into its emblem, and the camera flies to the church with the name and the sky-blue emblem.

### Whole film: Done
- Anthony: "For building up Zion, have more and more churches from Korea appear. Find real churches and their designs . WMSCOG official churches in Korea"
- Sent: 2026-11-19 13:06
- Outcome: Done: 226 real WMSCOG buildings from official dedication posts, no building reused (models/wmscog_churches.py), 141 of them Korean.

### Coda: Done
- Anthony: "There’s a scene where the orchestra is playing but also bowing down. Do not have them bow. Instead of having hearts use the church logo. And the sun needs to be way more epic looking"
- Sent: 2026-11-19 13:09
- Outcome: Done (s11_coda.py): the sky orchestra plays upright, no bowing; emblems rise in place of the hearts at 3:09.5 to 3:21 and cover the Earth in the finale; an epic sunrise over Zion, calmed so it never whites out.

### Whole film: Done
- Anthony: "The heavenly city buildings are the real church buildings in Korea. The international churches should be scattered throughout, outside of the mountain."
- Sent: 2026-11-19 13:25
- Outcome: Done: 140 real Korean churches on Zion's terrace and summit plots (CITY_SLOTS, SUMMIT_SLOTS); the international churches on the sea rings and in towns outside the mountain; empty plots are gardens of light.

### Whole film: Done
- Anthony: "The texts should not have a box covering up what's behind it."
- Sent: 2026-11-19 13:45
- Outcome: Fixed and checked (merged 85c25e1): no box behind any phrase; the blaze words now hold over bright scenes with a crisp white core and a strong coloured glow (the phrase gold on the stage, the phrase crimson). The machines are re-rendering with it.

### Whole film: Done
- Anthony: "Final note for these last videos: not everything needs to be so washed out and bright all the time. Key timings should be highlighted. Do not saturate everything. Do not wash out."
- Sent: 2026-11-19 14:17
- Outcome: Done in the final videos: one shared light budget (about half at rest, full on the key moments) drives the exposure and the music effects; every set rests calm and swells on the key moments; the slams are bursts of colour, not white frames.
