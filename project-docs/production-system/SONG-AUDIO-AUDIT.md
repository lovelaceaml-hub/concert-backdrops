# Song and audio audit

Updated 2026-11-21. This audit reconciles the repository snapshot `23c9307608291a99702d687933c8d2092d1fd01d`, newer Drive status records, current song branches, the concert program and the actual selected audio files. Later integration of the repository does not change these media identities.

## Result

**All 11 selected full reference recordings are now available locally, hashed and fully decoded without FFmpeg errors.** No song is blocked by a confirmed missing reference recording. The remaining audio decisions concern the live arrangement and timing.

The machine-readable record is [catalogs/songs.json](catalogs/songs.json). It stores source IDs, full SHA-256 values, bytes, original and decoded duration, local paths, prior delivery fingerprints, source-document references and explicitly labelled creative proposals. Original files are unchanged under ignored `work/song-sources/`; their combined size is 66,451,078 bytes. The local probe receipt is `work/song-sources/probe-results.json`.

The first ten songs have full backdrop v2 deliveries reported in their updated status records. Song 11 has a completed 540p music-video draft reported in its later account, plus the independently verified and owner-approved 30-second 1080p60 study. This audit did not retrieve or watch the ten prior full masters or the complete Song 11 draft. A reported delivery is not a new artistic approval.

## The selected recordings

The newer [concert program](https://docs.google.com/document/d/1bRl4WbeKucr-EUpEhe_9uVop0C-ozCMRxiPmzFvCoD0) and each song's current branch timeline identify these sources. All links below were resolved through the Drive connector. The files were then downloaded through fresh authenticated download references, except Song 11, whose previously verified original was copied and checked again.

Container duration and decoded sample duration are deliberately separate. Codec priming and container timing account for differences of a few tens of milliseconds; beat alignment should use the decoded waveform and explicit anchors.

| Song | Selected full source | Live target | Container seconds | Decoded seconds | Local file |
| --- | --- | ---: | ---: | ---: | --- |
| 01 All You Stars of Zion | [Brass ensemble](https://drive.google.com/file/d/1wmWrkUIuIU_zE1Hogp_hPUFYBH0J5YJR/view) | 188 | 187.992000 | 187.965542 | `s01.mp3` |
| 02 The Rose | [Organisers' recording](https://drive.google.com/file/d/1UoGwToBnpl-jlEJDRfqMnHMfluupGOhO/view) | 240 | 212.288000 | 212.244000 | `s02.m4a` |
| 03 I Reminisce About Your Love | [Current reference](https://drive.google.com/file/d/1XMKLgAG0s22AbWpo5nruwEQ-DPRQH8PM/view) | 313 | 355.128000 | 355.091167 | `s03.mp3` |
| 04 I'm Sorry, Please Forgive Me | [Current melody reference](https://drive.google.com/file/d/1zdEjaTvRAA-Xvx5TxAKZRd-cxgCId-Fr/view) | 220 | 219.480000 | 219.434667 | `s04.mp3` |
| 05 God Bless You! | [Organisers' recording](https://drive.google.com/file/d/1sc19zSxMPDEI5bxaaoiCVx7rndRY-F_D/view) | 159 | 153.152000 | 153.108000 | `s05.m4a` |
| 06 Heavenly Mother Tells Us to Be Grains | [Concert reference](https://drive.google.com/file/d/1YqFkD3lQprvotC32xRfC8Dqno0I24hqs/view) | 137 | 134.890667 | 134.846667 | `s06.m4a` |
| 07 May No One Ever Feel Lonely | [Current reference](https://drive.google.com/file/d/1wL9dyLETDn3q9ECkIXKrDb3UIt_eAgEA/view) | 238 | 246.552000 | 246.528000 | `s07.mp3` |
| 08 Out of Heaven, Favor From God | [Ensemble reference](https://drive.google.com/file/d/11x03zfwMq51wk7T8Z6sL25QGlrunU1Xn/view) | 210 | 209.112000 | 209.084083 | `s08.mp3` |
| 09 Let's Save the World | [Soloist reference](https://drive.google.com/file/d/1u4LgRODeqrMaKpdMDjkAVinLjF9QW2-l/view) | 276 | 275.736000 | 275.712000 | `s09.mp3` |
| 10 Our Mother Saves the World | [Shared recording](https://drive.google.com/file/d/1NbsvsPQO_wMWEl9OzJNFH6ZQAs_qg6WG/view) | 211 | 211.605333 | 211.605333 | `s10.m4a` |
| 11 Almighty God Who Knows the Future | [Choir reference](https://drive.google.com/file/d/108zDtdB4X189DOwsZn-K9p548nERubLG/view) | 260 | 268.224000 | 268.181333 | `s11.mp3` |

All files are 48 kHz. Songs 05, 06 and 10 are mono AAC; 02 is stereo AAC; the remaining files are stereo MP3. Every full reported source checksum matched; the previously abbreviated checksums for 02, 05 and 07 also match their prefix and suffix and are now recorded in full. In particular, the Drive copies of 03 and 04 match the exact fingerprints of the private Artifact sources used for their v2 films.

The eleven files in `audio/promo/` are historical 60-second excerpts. Songs 02 and 10 there decode to complete silence. They must not be used to conclude that the full recordings are missing or to analyse full-song timing. The old 05 and 09 MP3s are instrumental guides; separate sung guides and newer concert references have distinct IDs in the catalog.

## Timing that still needs a performance decision

The live targets total 2,452 seconds, or 40:52. The historical v2 policy adds 15 seconds of calm hold per song, producing 2,617 seconds, or 43:37. These are production targets from the records, not independently verified rehearsal lengths.

| Song | Historical v2 treatment | Remaining decision |
| --- | --- | --- |
| 01 | Original speed, tiny silence pad to 188 seconds | Confirm rehearsal accents. |
| 02 | Uniform stretch to 240 seconds, about 13.05 percent longer | Establish where the live trio actually adds time. |
| 03 | Remove source 272.74 to 314.79 seconds with a 40 ms crossfade; trim silent tail | Confirm that the live arrangement omits that repeated passage. |
| 04 | Very small conform to 220 seconds | Resolve instrumentation: older set list says choir and orchestra; current timeline says a cappella choir. |
| 05 | Uniform scale from reported 153.152 to 159 seconds | Confirm sections and meaning cues against the performed version. |
| 06 | Uniform scale from decoded 134.847 to 137 seconds | The reference stops abruptly; confirm the real ending. |
| 07 | Map source 0 to 243.5 onto 238 seconds | Confirm timing and duet versus quartet. |
| 08 | Original speed, silence pad to 210 seconds | Confirm orchestra rehearsal timing. |
| 09 | Original speed, silence pad to 276 seconds | Confirm piano solo phrasing and flexible holds. |
| 10 | Very small conform to 211 seconds | Verify the illustrative expression placements against the song's meaning. |
| 11 | Current preparation preserves source 0 to 260 seconds, then 15-second hold | Preserve this current clock; the earlier paused-build conform is superseded. |

These rows document existing choices. They do not authorize a new agent to apply a time stretch or delete a repeated passage without recording the chosen arrangement and its approval scope. For an excerpt study, declare its original-source start and duration and preserve that clock.

## Existing full-film baselines

The [Drive Status folder](https://drive.google.com/drive/folders/1MLgeSeYNvV8Zwqh_YksAwLrZvjfKCSzi) was updated on November 19. Its per-song v2 entries are newer than the repository's old `project-docs/status/01.md` through `10.md`. The catalog links each status record and the corresponding branch timeline.

| Song | Reported delivered baseline | Material qualification |
| --- | --- | --- |
| 01 | v2, 203 seconds, 1080p60 | Complete master fingerprint recorded. |
| 02 | v2, 255 seconds, 1080p60 | Full recording now exists; old silent promo status is obsolete. |
| 03 | v2 fix 1, 328 seconds, 1080p60 | Complete master fingerprint recorded. |
| 04 | v2 fix 1, 235 seconds, 1080p60 | Current reference includes verse 3 according to its builder. |
| 05 | v2, 174 seconds, 1080p60 | Delivered code `106c2b8`; fix `faf3009` was not rendered. |
| 06 | v2 fix 1, 152 seconds, 1080p60 | Complete master fingerprint recorded. |
| 07 | v2, 253 seconds, 1080p60 | Framing fix `57b2714` is ahead of the delivered picture and was not rendered. |
| 08 | v2 fix 1, 225 seconds, 1080p60 | Status/checklist report delivery; exact master hash still needs retrieval. |
| 09 | v2 fix 1, 291 seconds, 1080p60 | Repeat heuristic returned a failure near 218.27 seconds; coordinator accepted that exception. |
| 10 | v2, 226 seconds, 1080p60 | Fix 1 stopped after 13 of 53 ranges; the earlier delivered v2 remains the baseline. |
| 11 | Joined music-video draft, 275 seconds, 540p30 | Mixed rendered section commits; later code-only fixes must not be claimed as present. |

The catalog preserves available stage and review SHA-256 values as **reported** values. They become independently verified only after the actual prior masters are retrieved and hashed. Song 09's phone preview also has additional encoder holds; it should not be used as a quality master. Its warm dawn ending differs from the older dark transition planned for Song 10.

For Song 11, the later [how-it-was-made account at the pinned source](https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/project-docs/backdrops/s11-full2/HOW-IT-WAS-MADE.md) supersedes the paused early build still described in Drive Status/11. The approved study is separately documented in [VERIFICATION.md](../../tools/promo_beauty_example/VERIFICATION.md); it is 30 seconds, not the entire song.

## Durable approved visual references

Use [Film 10, Nine Colours, Revision 3 master](https://drive.google.com/file/d/1gcxnb4Oyexq5Kbb8LvFWqOrikF-BVSht/view) as the canonical original promo. Its approved source is `46df53b98a43f58e51a78d40ee5794108a68e13c`, tag `film10-revision3-approved-2026-11-16`. It is intentionally 66 seconds including the six-second lead-in, 3,960 native frames at 60 fps.

The master is 94,541,396 bytes; the [approval record](https://drive.google.com/file/d/1IwhQMsGrQTG9I5wMCIgSRTPtM8jkdcTL/view) reports SHA-256 `508c5518bced94b21f96e8727d2b7ffd0da0ee69de9da164e7e5e824e80eda7b`. Its Drive metadata was verified in this audit.

The [approved 720p60 copy](https://drive.google.com/file/d/1CBQ4OtpLW3Kp3zBWsEMkjXYiAWUwhDQw/view) is 22,278,585 bytes. The existing local comparison copy was independently hashed and probed: 66.000 seconds, 3,960 frames, SHA-256 `ad4b4e7fe861ae34eb80e8b921ee747efc477c08bb89ec981f1b588a0b3c0af5`, matching the approval record exactly.

The new approved Song 11 study has SHA-256 `6e4533c4527dfb81c750f8ba907e86392f0c87dca638c3daac768ece8edae82a`, 110,865,643 bytes and picture commit `a7d68836c4fdc7156bbc9b839380cd65180ca2bb`. Its original source interval is 97.8 to 127.8 seconds. It establishes the current quality target while the full concert films retain their own review state.

## Campaign meaning and visual opportunities

The [official campaign overview](https://heavenlymotherslove.org/en/about) and [nine-practice checklist](https://heavenlymotherslove.org/en/checklist) make everyday understanding, patience, support and practical care central. A beautiful effect should follow a readable act of care. The catalog paraphrases the nine practices and gives each song a proposed performance, camera and model direction without copying lyrics.

The historical concert continuity introduces Compliment and Encouragement in 01, Apology in 03, Inclusiveness in 04, Consideration and Respect in 05, Concession in 06, Greeting in 07 and Gratitude in 08. All nine are then present before the finale. Respect in 05 and Concession in 06 remain explicitly provisional thematic exceptions. Song 10's five placements remain illustrative. Do not promote those labels into confirmed meaning matches.

The highest-value shared model work is a natural two-person interaction rig: planted feet, weight shift, hand contact, anticipation and recovery. It serves seven songs. Next come performer-specific motion, a varied walking and community system, and each song's hero object: rose, thawing ice, blessing tree, wheat, embroidered curtain, boat/net and lamp. Existing Zion, conductor, crowd and 226-church assets should be reused and selectively refined.

For Song 07, the measured original-source structure has a hush at 137.5 to 149 seconds and a build at 149 to 174.5 seconds. A proposed 18-second helping scene at 137.5 to 155.5 seconds can place noticing and approach in the hush, the offered hand near the transition, and balanced recovery in the build. This is a structural proposal, not an ear-verified meaning alignment.

## Rule versions that future chats must distinguish

Current Drive AGENTS and AUTONOMOUS-RUN preserve the November 13 instructions. DESIGN-SYSTEM and VIDEO-HANDOFF have November 16 approval and 4K frontmatter but retain old 30 fps, no-logo and missing-recording tables. Their history must not override newer owner decisions or be treated as a current inventory.

The separate [November 19 Song 11 lessons addendum](https://drive.google.com/file/d/1Q6ilWF8TtZRaltZZNzhtUXCsLOISHLS8/view) applies to every song unless its own design says otherwise. It restores music-led flights and downbeat cuts, coloured comets, ribbon dancers, raised-arm waves, deliberate clouds and the bottom-left logo with periodically shown titles. Its blue sparkling treatment is specifically for choir and orchestra, with gold instruments and books. Ordinary people remain warm gold, whole, clothed and naturally moving.

This differs from the earlier v2 no-comets and top-left signature specifications. Keep the delivered v2 films as historical baselines while using the newer addendum and scoped owner approvals for new work. New generation proposals default to code-drawn worlds and rigged/procedural assets. They do not imply a switch to realistic faces, AI-restyled footage or replacement music.

## Next gates

1. Preserve the original sources and fingerprints; prepare analysis and timing derivatives into ignored work folders.
2. Confirm each performance arrangement and select either rehearsal timing or an explicit operator-cue map.
3. Retrieve the existing full master when evaluating whether a proposed change improves that specific film.
4. Approve representative human action and wide-scene tests, then freeze the source and render parameters for a production round.
5. Verify both picture and sound, including readable expressions, contact/foot motion, exact excerpt alignment and the live playback hold.

No recordings, full lyrics, rendered media, source assets or original documents were edited during this audit. Only the catalog and this audit document are intended for git; acquired source media and probe receipts stay ignored.
