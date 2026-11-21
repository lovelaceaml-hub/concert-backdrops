# Original fan and silk performance

November 21, 2026, America/Los_Angeles.

## Owner direction

The owner asked to try the three supplied dance/theatre references as well as possible, continuing in the approved Mother's Words of Love style. This supersedes the earlier instruction to wait for source files before doing useful original work. Accurate source choreography still requires inspected moving footage, but that missing input does not block an explicitly original study.

## What is built

`concert-fan-trio` is a twenty-second continuous scene with three distinct authored roles, two open fans with finite silk sheets, a changing formation and an ending over the mirror lake. It uses the existing approved rig, garment engine and native p3d renderer without modifying their files.

The lead opens a fan phrase, the answer follows with a different hand/turn score, and the welcome performer advances through the formation. The outside dancers carry their own fans throughout. No prop handover, partner lift or aerial act is present. Head, torso, free fingers, fan grip and stepping are authored together. The final light response begins from actual silk-edge positions.

The [module README](../../tools/concert_fan/README.md) gives exact commands. `projects/concert-fan-trio/project.json` registers 1,200 output frames at 60 fps. The selected music is the verified original Song 07 interval from 137.5 to 157.5 seconds, with unchanged playback speed and recorded gain/fades.

## What the references actually supplied

The cloud browser retry again stalled at time zero with no decoded video frame. The first two posters could be inspected. The third reference supplied title/channel metadata only. No sign-in wall or explicit bot denial was encountered; the player simply did not deliver usable motion.

| Reference | Usable observation | Use in this study |
| --- | --- | --- |
| Fei Tian Dancers, Upwards to the Moon | Three performers in asymmetrical triangular staging; open fans carrying broad attached fabric; lavender outer layers and flowing white lower garments; black backdrop | Three distinct roles and broad held fan fabric, redesigned as code-drawn light. The modest long skirts are this production's design choice, not a claim about every source garment. |
| Cirque du Soleil, The Beatles LOVE trailer | Bright yellow car, ensemble at multiple elevations, saturated stage light and separated silhouettes | A reminder to use deliberate ensemble depth and a clear visual hierarchy. No trailer action, car, lift or aerial apparatus is recreated. |
| Pilinh Dance, Song Dien Yen Tuan | Metadata only | No costume, prop or choreography detail is attributed to this video. |

The approved promo was reacquired and verified against its cataloged SHA256, then sampled at nine times for the luminous body, colored light, dark-sky and mirror-water language. These comparison samples are still-frame review, not new real-time playback evidence.

## Improvements that matter visually

1. Each performer has a separate score instead of sharing the same short capture with a time offset.
2. Twelve explicit steps per person carry the root motion. Planted feet retain world position and orientation; the body does not slide over them.
3. Fingers, free wrists and torso/head direction support the phrase. The free hands extend diagonally while the fans rise, avoiding a repeated both-elbows-up silhouette.
4. Fans follow the final solved hand. Their bank is staggered between lead and answer, so the fabric changes plane with the gesture.
5. Each finite silk sheet has a 319-node physical approximation, saved at 60 Hz from a 120 Hz solve. Its surface is drawn as translucent light, with restrained ribs and hems.
6. The camera was brought closer after the first review. Reduced body-mask strength removed the heavy dark halo, while selective body light restored the promo's focus without lifting the whole sky.
7. Actual cloth caches are reused across camera iterations. Six longer CPU chunks avoid repeatedly restarting the garment history for fourteen short jobs.

## Evidence and limits

The final delivery and audit records are added to the shared catalogs when their exact outputs are complete. Technical checks, sampled visual review and owner creative approval must remain separate.

The seven focused motion/prop checks cover deterministic final skinning matrices, stable support, foot clearance, wrist continuity, immediate entry, ending pose, arbitrary prop seeking, finite cloth, floor contact and cache reuse. Full-motion cache measurements record submicrometre pin residuals and no free-node floor penetration. They also record approximately 11 to 12 percent 99th-percentile structural strain and larger local maxima. These are solver diagnostics, not a claim that this represents a measured silk fabric.

This is authored kinematic dance with IK. It does not use a new motion-capture library, physical whole-body balance, automatic professional choreography or reconstructed YouTube motion. The cloth has body capsule and floor contact, but no self collision, partner collision or exact costume-surface collision. The hands and hems still require visual judgment in the rendered film.

## Next quality work

Use the delivered study as the next concrete comparison. The highest-value continuation is a richer complete dance phrase: an expressive turn, deliberate arrival, changed level and clear recovery, with the camera keeping feet and fan shapes readable. Refine the real skirt silhouette and silk during reversal before adding crowd scale. For faithful adaptations, ingest source videos through the existing reference tool and annotate support, grip, rhythm and recovery from actual footage.

To take this across all concert songs, preserve the division between an authored performance score, the final solved body/contact state, its cached garment/prop response, the campaign's light style and the song-specific camera/music edit. A reusable rig or constructor is only a starting point; every new phrase still needs an actual moving review.
