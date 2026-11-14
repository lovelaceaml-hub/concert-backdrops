# Shared figure library: people of light for the nine Words of Mother's Love

Each picture is one pose of a pair of people: clean white line art on black, 1536x1024 grayscale, the drawing 940 pixels tall with the feet on the line 24 pixels above the bottom (prepared with tools/prepare_figure.py). The engine turns each pose into golden sparks with a soft outline and inner light (engine/UPGRADE-HOWTO.md, section B). Use the poses of one expression in order in a figure's `poses` list; the sparks move from one to the next.

The same two people appear in every pose: on the left, a person in a long robe with a soft hooded cowl collar; on the right, a person in a long robe with a head veil over the shoulders. Faceless, fully clothed, seen from the side. Use `flip=True` to swap sides.

Made 2026-11-13 with the media-studio make_image tool (gpt-image-2 through Codex), checked one by one (no face, no text, good hands, modest clothing). The original pictures are in ~/Pictures/AI Images/concert-backdrops-figures/ on Anthony's Mac.

## Poses

| Expression | Pose files (in order) | What happens |
|---|---|---|
| 1 Greeting | greeting_a, greeting_b | a: the left person walks up and waves to the right person, who stands alone, head lowered. b: they face each other and the lonely one places their hands in the offered hands. |
| 2 Gratitude | gratitude_a, gratitude_b | a: the left person bows deeply, hand on heart; the right person opens their hands. b: the left person offers a small gift in both hands; the right person reaches to receive it. |
| 3 Apology | apology_a, apology_b, apology_c | a: the right person stands withdrawn, arms folded; the left hesitates, hand on chest. b: the left steps forward first and reaches for the other's shoulder; they begin to turn back. c: they face each other and the hurt one takes the offered hand. |
| 4 Inclusiveness | inclusiveness_a, inclusiveness_b, inclusiveness_c | a: the left person kneels, sorry, hands together; the right reaches down kindly. b: the right person lifts them up by both hands. c: a warm embrace of forgiveness. |
| 5 Concession | concession_a, concession_b | a: both step toward the same spot at the same moment and pause. b: the left steps aside with an open arm ("please, after you"); the right walks ahead with a small grateful bow. |
| 6 Respect | respect_a, respect_b | a: the right person speaks with an open gesture; the left leans in to listen, hand at chin. b: the listener places a hand on heart and nods; the speaker rests, at peace. |
| 7 Encouragement | encouragement_a, encouragement_b, encouragement_c | a: the right person kneels, exhausted; the left prays over them. b: the left rests a hand on their back and raises the other in cheer; they begin to rise. c: both stand and lift their joined hands in hope. |
| 8 Consideration | consideration_a, consideration_b | a: the right person bends under a heavy bundle; the left approaches with open hands. b: they carry the bundle together, steps lighter. |
| 9 Compliment | compliment_a, compliment_b | a: the right person holds a basket after finishing a task; the left claps in praise. b: the left rests a hand on their shoulder and raises the other in praise; the right stands taller, hands at heart. |

Notes from the check: every pose is faceless and fully clothed. Encouragement b was made twice (the first try showed a facial profile; the redo with smooth heads is the one saved). A few poses have very slight profile shapes in the head outline (gratitude_a's bowing head, encouragement_c's right figure); in sparks of light they read as smooth heads.

## Prompt pattern (for new special figures in the same style)

"Minimal line art illustration: clean white single-weight contour lines on a pure black background, very faint inner fill. Two people, full body, seen from the side ... Left person wears a long robe with a soft hooded cowl collar; right person wears a long robe with a head veil draped over the shoulders. <the act> Heads are smooth plain ovals with NO facial features at all (no eyes, no nose, no mouth). Both clearly clothed, modest, soft folds. Both fill about 85 percent of the image height, feet near the bottom edge. No ground line, no floor, no text, no letters, no background, no shadows, nothing else." Size 1536x1024.
