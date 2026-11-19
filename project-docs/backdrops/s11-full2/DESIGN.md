# Song 11 "Almighty God Who Knows the Future": the design as built (backdrop v2)

The living record of every design decision for this video, with Anthony's own words where he gave them. Read this before changing the film, and reuse what fits for the other songs (the reusable kit is at the end). Lyrics are not copied here; phrases are named by their time.

## 1. The film in one paragraph
A journey through a waiting heavenly city, the Earth, Mount Zion and the whole world, ending at the Church of God. Fully rendered on the approved promo engine (Film 10 R3, `engine/p3d`), no AI-generated images. 260.0 s of music plus a 15 s hold (275.0 s). Drafts at 960x540, 30 fps; the final is 1920x1080, 60 fps. The look follows the approved 60 s promo: dark misty heavenly night with light blazing against it, nine comets in the nine colours, rays and shafts, clouds and pillars of light, a rollercoaster camera, and everything moving with the music. Anthony: "beautiful, gracious, and heavenly ... match the promo video with the lights ... very, very interactive ... feel how amazing it is and its power ... through rays of light, performances, and dynamic cinematic shots." Then: "It needs to be grand. Do not bound yourself or limit yourself."

## 2. Structure (sections and owners)
| Section | Time | What happens |
|---|---|---|
| Intro | 0:00 to 0:40 | Title over the mirror sea; the church of light; the flight down a canyon of clouds; the choir forms; Father's pulse with pillars of light |
| Verse 1 | 0:40 to 1:22 | The Earth opens on its night side and lights up; the crown over Zion; the city fills with gold; the nations stream in |
| Chorus 1 | 1:22 to 2:01 | Slam 1 with comets out of the orchestra; waves of praise; the first climb; the ring of dancers; the column of thanks |
| Verse 2 | 2:01 to 2:40 | The breath dancer; Mother's light falls to the sea; the march; hearts lit in nine colours; the kings lay down their crowns |
| Chorus 2 | 2:40 to 3:21 | Slam 2; the shockwave over the sea; the second climb; the heart of light drawn by two dancers |
| Coda | 3:21 to 3:59 | Sunrise over Zion; hearts and lanterns; the canyon flight; the orchestra on the clouds; the world finale |
| Ending | 3:59 to 4:35 | Back to Zion; the held-breath dancer; the end card on the last chord; the hold |

The edit is 70 blocks in `tools/s11_full2/s11_full2.py` (EDIT, exact t0/t1). Each block has one owner thread: church, stage, zion, procession, coda, dance, core.

## 3. Decisions (Anthony's directions, in order)
- **Church of light** modelled on the main temple in Korea from Anthony's photographs, highly detailed (curved blue glass, floor bands, teal base, stone portal, ladder blade, fins, roof canopy, mast, white tower, pines).
- **Church name and emblem** (2026-11-19): "World Mission Society Church of God" large in two lines across the top two floors of the glass, centred; the church emblem below it, larger (9 m), glowing sky-blue like Anthony's reference (blue ring with the white lettering, blue globe with white lines, soft white ring between), traced exactly from the image he sent (stored in code as EMBLEM_MASK; never redraw it by guess). The small name stays across the top of the portal.
- **Choir and orchestra**: "Choir can be the same color as orchestra"; then "Make the choir and orchestra glowing blue sparkles. Keep instruments gold. Have choir have a song book open that is also gold like the instruments." Colours: figures #6cb2ff with #d2e8ff glints; instruments and books gold (#ffc76e family); the dark body mask is off for the players so they glow.
- **Corner text**: "The logo should remain in the bottom left. All the extra words don't need to be there." The logo alone stays bottom left all film; the song title and the event title ("The Words of Mother's Love That Bring Peace") fade in beside it for 8 s about every 40 s (0:41, 1:26, 2:02, 2:46, 3:25, 4:00). No date, time or place in the corner (the end card keeps them).
- **Pace and energy**: "music video pace", strong intensity: camera cuts on big downbeats hidden in flashes, flowing flights between them, faster on hits and loud passages, shake on slams, a lens punch on hits, colour and brightness following the measured loudness levels.
- **Background**: dark misty heavenly sky that grows more glorious at the song's turning points; mountains, a mirror sea with floating lights, stars, the nine expression symbols as small constellations. No arch of nine stars. Colours that fit the song (lavender, rose, gold horizon).
- **Clouds**: "The clouds can be placed more thoughtfully instead of just taking up the screen randomly. It makes it look crowded." Each cloud is one shaped bank (flat base, tallest in the middle, tapering ends); horizon banks in symmetric pairs framing Zion with its sky clear; no clouds at the stage; canyons only in the flights that fly through them, dimmed so they frame rather than white out.
- **The Earth**: "The earth view can start as night tune and then being lightening up." It opens on its night side (dark navy oceans, dim gold land, city lights) and daylight sweeps across: half lit by 0:53.78, fully lit by 1:17.46; the world finale stays lit.
- **Dancers** (Anthony loved the promo's dancer with her ribbon; "animations that move like the dancer with ribbon but it can be new fresh designs"): five moments in `s11_dance.py`: the ring of seven whose ribbons braid into a spiral (1:37.7), the slow breath dancer (1:57), the same dancer with the strings (2:01), two dancers drawing a beating heart of light (3:05.9), the held-breath dancer whose ribbon shoots up like a comet (4:07.5).
- **Waves of raised arms** (`ARM_WAVES`, `Arms`, `WaveCrowd` in `s11_zion.py`): waves roll up Zion terrace by terrace on the slams and big hits, stadium waves every 4 beats on the waves-of-praise lines, the procession lifts its arms toward Mother's light; arms down in the quiet passages.
- **Grand pass** (promo frames as reference): banking camera with roll, clouds of light, pillars of light falling onto the sea, comets shooting out of the sea and fanning from a blazing light, comets drawing loops round figures, flights low over the sea and through cloud canyons.

## 4. Rules kept
No lyrics, songs, finished videos or frames in git (short audio clips under audio/ excepted). Render only in the cloud. No em dash or en dash anywhere. No AI-generated images. No facial features; everyone clothed in light; Heavenly Mother never as a figure (only as light). Phrases on screen must read for at least 2.5 s with nothing bright crossing them. No white-out.

## 5. Open findings (also on the review page)
- Father's pulse at 0:40 near white in the centre.
- Phrase contrast over bright terraces at 1:41 and 3:01.
- The words at 2:14 arrive over the mountain during the racing flight.
- The kings' pillars at 2:34 are faint.
- Slam 2 at 2:42 is washed with glare.
- The sky orchestra at 3:28 is hazy behind its cloud floor; the summit pillars at 3:31 read as dotted columns.
- Arm waves on the small summit and procession figures show mostly as hand sparks; the ring dancers are faint in their wide shot.

## 6. The reusable kit (for the other songs)
All in `tools/s11_full2/` on branch `backdrop2/s11-full`:
- `CloudBank` (shaped banks of cloud of light), `Pillars` (pillars of light onto the sea), `Comet` (comets with trails, optional moving light), `add_light`, `add_rays` (ray sources; the strongest wins), sky helpers (`glory`, constellations of the nine symbols, sea glitter): `s11_full2.py`.
- Banking camera (`roll` on any shot), `music_pace`, `cam_shake`, `fov_punch`, slam bursts: `s11_full2.py`.
- The night-to-day wrapper for the Earth (`_night_side`, `earth_day`): `s11_full2.py`.
- Ribbon dancers (`s11_dance.py`): bodies with dance motion, ribbons led from the hand with core, glow, head and sparks.
- Waves of raised arms for any crowd (`Arms`, `WaveCrowd`, `ARM_WAVES` in `s11_zion.py`).
- Blue-sparkle performers with gold instruments and gold song books (`SongBooks`, `FIG_BLUE` in `s11_stage.py`).
- Corner signature: logo alone plus periodic titles (`s11_cards.py` `_signature`/`_sig_windows`).
- The church of light with the name and the traced emblem (`s11_church.py`).
- The render fleet, the live review page and the helper scripts: see PIPELINE.md.

## Light as an event, not a constant (Anthony, 2026-11-19)
"Not everything needs to be so washed out and bright all the time. Key timings should be highlighted. Do not saturate everything. Do not wash out."
- A darker, calmer base everywhere: deep near-black violet between the lights, blacks not lifted, little bloom or haze at rest, colour restrained.
- Full light and full colour only on the key moments: Father's pulse 0:40.54, slam 1 1:22.08, Sacrifice 1:40.26, Devotion 1:45.14, thanks to Father 1:49.8, the church of God 2:39 to 2:42.86 and slam 2, Sacrifice 3:00.7, Wondrous love 3:04.65, slam 3 3:21.73, Sacrifice 3:38.1, Devotion 3:44, "Oh, the Church of God" 3:58.9, the comets meeting the emblem 4:14.
- The core provides one shared light-budget helper; every set scales its resting light by it.
