# Design review: clarity, movement and beauty

20 November 2026. This review explains why the previous 30-second example did not meet the creative standard, and documents the completed replacement study and the next acting improvements. [VERIFICATION.md](VERIFICATION.md) records the actual export checks and review scope. Creative approval remains the owner's decision.

## Evidence and scope

The review used the complete Song 11 production account, selected decoded frames from the approved 66-second promo, the delivered 30-second people example, and its source. Observations about composition refer to those actual images. Conclusions about choreography also use the source and the owner's recorded directions; contact sheets alone cannot establish fluid acting or musical synchronization.

Three immutable source versions anchor this review:

- [Song 11 account][account], commit `34f835206dcb26cfa0bd7e321171d3d224e3aa7d`.
- [Previous people example][previous], commit `e46c149fb50908e7f5e87832701346f67b5f0201`.
- [Approved promo implementation][approved], commit `46df53b98a43f58e51a78d40ee5794108a68e13c`.

The approved creative cut is the reference for its luminous world, traveling light, emotional warmth and composition. Song 11 adds the owner's later direction for grand performance, stronger musical editing, flowing flight and a conductor whose gestures appear to affect the whole world. These are related references with different purposes, not interchangeable timelines.

## Why resolution did not solve the problem

The previous example delivered native 1080p60 and improved the legibility of bodies, garments and typography. Its verification distinguishes completed output from still checks and explicitly says numerical continuity cannot prove natural acting or creative approval. [Previous verification][verification]

Resolution determines how clearly an idea is represented. It does not choose the idea, stage a meaningful gesture, create a musical climax or give the camera a reason to move. Increasing the same quiet composition to 4K would preserve its limitations more precisely. A GPU can make iteration and dense rendering faster; it cannot supply choreography.

The replacement should keep the technical gains while recovering the reference's relationships: human intention, movement through space, a visible response from light, and a larger emotional destination.

## What was lost in the previous example

### The setting became a presentation platform

At 0, 5 and 15 seconds, the purple floor, gold perimeter and amber radial sky dominate similar compositions. At 23 to 30 seconds, the camera reveals the whole circular platform. The people shrink, but no larger meaningful world is uncovered. The image reads as a group displayed on a floating disk.

The approved promo's pair at approximately 40 to 44 seconds belongs to a mirror landscape with lantern-like lights continuing into depth, distant silhouettes and reflections. The approved implementation specifically preserves a moving lantern-lake shot for this interaction. [Approved promo][approved]

The contact surface should ground the performers while continuing visually into water, terraces or deliberately shaped cloud banks. A wide reveal should expose relationships and scale, rather than the boundary of a small set. The previous disk and perimeter are explicit geometry choices, not an unavoidable limitation of the renderer. [Previous environment][environment]

### The acting was too small for its framing

The previous edit holds the pair until 10.2 seconds, the conductor and choir until about 19.47 seconds, then retreats. The choir often reads as a posed group in the contact sheet. [Previous example][previous]

Its conductor uses a repeated 2.18-second hand pattern. The main lateral and vertical oscillations are approximately 6 cm and 10.5 cm, with smaller secondary terms; torso lean is zero. The choir's late hand lift adds 9 percent of body height while the camera moves away. These are restrained choices, even if their interpolation is smooth. [Previous people source][people]

A principal action must be large enough to read at the intended screen size. Close framing can reveal a tender gesture. A wider conductor shot needs a stronger silhouette, supported by the chest, shoulders and weight of the body.

### Light lost its journey

The approved promo around 32 seconds presents a bright purple head with a long directional trail. Around 52 seconds, colored trajectories cross and converge; the finale resolves their movement into the luminous Earth and orbiting symbols. The implementation explicitly connects comets to that destination. [Approved finale][finale]

The previous example introduces its canopy after 20 seconds. Three families of arches gradually appear, then move only slightly. Their position behind the choir protects the people, but their dramatic role is weak: the audience cannot readily see who creates them, where they travel or what they change. [Previous environment][environment]

Use moving heads, tapering trails, purposeful destinations and visible consequences. A conductor's sweep can release a stream through the ensemble; the stream can awaken a wave of lights or lead the camera into a larger reveal. Mere visibility growth along a fixed arch is insufficient as the principal event.

### The edit did not express the requested energy

Three quiet shots provide little variation in scale, viewing direction or momentum. The Song 11 account records the rejection of 21 slow shots, followed by a request for music-video pacing, strong intensity, banking flight and cloud passages. Its final structure contains 70 camera blocks. That is evidence about the owner's taste, not a compulsory cut count for every excerpt. [Account, phases E to G and code map][account]

The new sequence needs purposeful shot changes: intimate preparation, readable performance, ensemble response, traveling light and a larger arrival. One short breath will make the strongest event more effective. Constant cutting or constant speed would erase that contrast.

### Color and brightness became nearly constant

The previous example remains largely purple and amber. The approved reference alternates deep indigo space with warm and colored events. Song 11's later direction explicitly rejected a washed-out image and required key moments to carry the brightest peaks. Its shared light budget reduced the base between those moments. [Account, phase K][account]

Color should identify roles and depth. For a Song 11 scene, blue ensembles with gold instruments and books are documented choices. For a promo interaction, warm gold people remain the established reference. Choose the palette according to the scene's purpose instead of silently applying either rule everywhere. [Song 11 stage][stage] [Approved promo][approved]

## How to author natural, meaningful motion

### Give each action a meaning

Write the action as a verb and consequence: gather the ensemble, invite a response, release a swell, listen, reassure, or complete a phrase. Then design preparation, action, arrival, follow-through and recovery. Breathing and small sways can be procedural; the principal performance needs authored intention.

A conductor should prepare before an attack and arrive decisively on it. Smooth does not mean uniformly slow. A quick beat arrival can flow into a slower recovery without a hard positional jump. The supporting hand should sustain or release a phrase, rather than duplicate the leading hand's loop.

### Preserve silhouette, contacts and joint overlap

Check the pose at the final camera distance. The hand should separate from the torso, the baton should remain identifiable and the gesture's direction should be clear without relying on particles. Avoid a bright background that merges every limb into one luminous mass.

Large arm actions need support from the pelvis, chest and shoulders. Let the shoulder lead, the elbow follow, and the hand and baton arrive last. Small timing differences create follow-through; independent oscillation on every joint creates noise. Blend gestures through their shared body pose so a new action does not reset the previous one.

Foot planting, hand placement and prop attachment are part of acting. A planted foot should not skate while the torso turns. Knees and elbows should bend consistently, hands should not pass through garments, and an instrument or baton should remain attached to its intended grip. Inspect these contacts during transitions as well as at the nicest pose.

### Make the ensemble respond together without becoming identical

Use a shared musical event with controlled differences in anticipation, amplitude and recovery. A wave can travel by row or across a terrace. Adjacent performers should not reveal an obvious repeated prototype, but arbitrary jitter is not expressive variation.

Cloth and trailing light should follow the body's momentum. Compute trails from past positions at known times so their origin remains attached to the gesture. Preserve deterministic sampling and consistent simulation caches across render chunks; a cut or worker boundary should not restart breathing, cloth or a light path.

### Choreograph the camera and light together

Each camera move should reveal, follow or emphasize something. Near particles, performers and distant clouds should move differently across the frame to establish parallax. Keep the principal action readable while foreground objects pass. A bank should belong to a curved flight, with a smooth entry and exit, rather than serve as an arbitrary roll.

Give light an origin, trajectory, speed change and destination. Distinguish sustained currents from brief percussive rings and high sparks. Allow a primary event to dominate while smaller activity continues beneath it. The existing Song 11 conductor and music-effects modules provide reusable examples of baton streams, braids, swells and differentiated responses. [Conductor][conductor] [Music effects][effects]

Reserve brightness for those events. Establish a darker base, preserve colored cores and dark separation, then let the strongest cue rise and release. Review people, reflections, sky, rays and bloom together: each layer can appear reasonable alone while their sum washes out the picture. Numeric brightness limits must be calibrated to the actual color pipeline and composition, not copied as universal aesthetic scores.

## Specific acting improvements for the existing engine

The following are **future improvements**, outside this render's frozen scope. The present study reuses existing performances. Its clearer image helps expose where a future original sequence could gain more believable intention, weight and contact.

First distinguish the two animation routes. The foreground gold conductor in `s11_dance._bodies()` imports the older frozen `p3d.body.Body`. `Gate.sample(t)`, `_hands_s()` and `tip()` evaluate the requested time; this hero is not a 15 fps crowd instance. His cloth simulates at 120 steps per second, stores snapshots at 30 Hz and interpolates between them. [Conductor][conductor] [Frozen actor][frozenactor] [Frozen cloth][frozencloth]

The separate podium conductor, choir, orchestra, three featured singers and responding crowds use the newer `f43f451` crowd package. `crowd._Proto._bake()` records local point positions at 15 fps; `_at()` interpolates those positions. Even `_heroes()` creates crowd instances with more points. The newer actor used during baking includes overlapping action and motion-capture foot locking, but the older foreground actor does not automatically inherit those features. [Stage][stage] [Crowd engine][crowdengine] [Newer actor][referenceactor]

### 1. Author a complete bodily intention for the principal performer

The foreground conductor uses `motion="stand"`, hand targets with `look=False`, and modest generic lean. His base body already breathes and shifts slightly, but those movements are largely independent of what he is communicating. [Conductor][conductor] [Frozen actor][frozenactor]

Give each major cue a preparation, directed action, arrival and recovery. A small weight transfer and look toward the ensemble can precede the chest turn, elbow, wrist and baton. Preserve a brief completed pose before the next instruction. Use the newer actor's overlapping-action approach as a model, with timing authored for the phrase. The gain is a person who visibly causes the musical event, with light following that intention. [Newer actor, `Actor.frame()`][referenceactor]

### 2. Give close performers a dedicated animation tier

Increasing a singer's point count changes detail, while `s11_stage._heroes()` still uses the same cached motion route. Point-position interpolation also follows straight paths between samples rather than preserving every joint's curved movement. [Stage][stage] [Crowd engine, `_at()`][crowdengine]

Keep cached prototypes for distant figures. Promote the nearest singer, musician or responding person to a live actor, or cache root motion and bone rotations before posing their geometry. Keep wrist, palm and foot anchors attached to that skeleton. This concentrates work where the camera exposes anatomy and contact. Raising every crowd's bake frequency would cost more without supplying a better performance.

### 3. Make visible feet agree with travel and weight

The newer actor already has `contact()` and `_lock_feet()`. However, `Crowd._place()` translates an instance using `walk * age`, while cached playback has separate rate and phase, and the figure has its own scale. Those relationships must agree after instancing. `MarchBeat.sample()` also positions foot sparks from beat phase and approximate root offsets, rather than a sampled sole contact. [Newer actor][referenceactor] [Crowd engine][crowdengine] [Procession][procession]

Couple travel speed, stride, playback rate and scale. Preserve contact intervals and foot anchors in a prototype, or solve the featured walker's planted foot directly. Trigger a landing spark from the resulting touchdown. This is a concrete alignment risk to check in a future approach, stop or kneel, not a measured sliding defect in the present study.

### 4. Attach props and light to the final posed hands

`s11_dance.tip()` follows an intended hand target. Stage bows, mallets and slides evaluate their paths continuously, while their players follow cached poses. `SongBooks.sample()` uses fixed offsets and approximate sway. The engine already exposes palm, pinch, wrist and mouth anchors through `Actor.where()`. [Conductor][conductor] [Stage][stage] [Frozen actor][frozenactor]

After solving the body, attach the baton to its actual grip and emit the trail from the resulting tip. Solve both hands around one book transform. Establish explicit instrument contacts, such as bow to string plane, mouthpiece to lips and cello endpin to floor. One consistent attachment system will survive close framing better than separately matching several approximations.

### 5. Let musical articulation change the performance

`s11_stage.play_ph()` advances a shared loop, switching between four-beat and two-beat speed according to intensity. `Bowing.s()` repeats strokes and `_mallet()` alternates periodic strikes; instrument-channel measurements strongly affect their light. [Stage][stage]

Add a small authored performance track for featured bow changes, held notes, breaths, rests and drum strikes. A mallet should prepare before a chosen attack, touch on it and rebound while the light ring expands. Keep movement continuous through tempo changes and give the recovery room to settle. Use measured hits as candidates, then check the important contacts against the recording. Louder sound should produce a different physical intention as well as stronger illumination.

### 6. Direct an attentive ensemble response

The choir already varies sway, and `WaveCrowd._acts()` supplies travel delays, jitter and smooth response transitions. Additional randomness alone would add little. [Stage, `Choir.sample()`][stage] [Zion, `WaveCrowd`][zioncrowd]

Choose a few foreground people who visibly notice and answer the conductor. One catches the cue, draws breath and lifts their head; a neighboring singer follows before the larger group responds. Give these figures skeletal chest, shoulder and hand actions, while retaining economical waves in the distance. Frame the cue and response so their relationship can be read. A few convincing reactions can make the whole gathering feel connected.

## Repeatable review gates

| Gate | Required evidence and decision |
| --- | --- |
| Meaning | State what changes emotionally and visually across the excerpt. Every principal shot must advance that change. |
| Composition | Review native-size frames for preparation, release and culmination. They must have distinct focal points and a readable depth hierarchy. |
| Acting | Watch a short motion pilot with restrained effects. The action must read from the body silhouette; feet, hands and props must maintain credible contacts. |
| Musical arrival | Review the exact audio excerpt with the pilot. Check preparation, arrival and recovery around major cues rather than aligning everything to a generic beat grid. |
| Cause and effect | Add light and camera. The source of a stream and the response it produces must be understandable. Effects should feel misplaced if moved to an arbitrary time. |
| Full sequence | Watch the complete animatic for changing scale, a deliberate breath, a strongest event and a graceful release. Check continuity across all cuts. |
| Light and delivery | Review native frames and the encoded movie for clipped areas, lost color, obscured bodies, flicker, timing, frame count and joins. Record aesthetic judgments separately from numerical results. |

Freeze one coherent version after these gates. Render from the recorded source, dependencies, assets, music and cue map. Compare against the reference at equal display size. If a check fails, revise the responsible gesture, shot or layer; avoid unrelated global changes that invalidate approved scenes.

## Limits of the evidence and music analysis

The Song 11 account is a valuable production record with stated limits. Its coordinator reconstructed personal work from a condensed session log and checked repository history. Earlier engine work and other workers' internal activity were reconstructed from commits and reports. This review should not present that second-hand material as independently witnessed history. [Account, section 0][account]

The music map also needs accurate language. Channels named strings, brass, choir, high and low voices are estimates built from a mixed recording using frequency bands, harmonic/percussive separation and pitch or voiced-probability analysis. They are not isolated instrument stems or a complete transcription of every note. Separate stem processing mentioned elsewhere in the account does not make these map channels ground truth. [Music-map implementation][musicmap]

Use those channels to suggest texture and emphasis. Verify major attacks, phrase boundaries and tempo changes by listening and measuring the exact excerpt. The account records an unresolved early cut of about 0.14 seconds; automatic timing therefore cannot be treated as exact. Neither this review nor a still comparison proves synchronization of the replacement video.

## Rendered demonstration and observed limits

The selected study uses picture time 97.7 to 127.7 seconds and audio time 97.8 to 127.8 seconds from Song 11, retaining the production's 0.1-second relationship. Its nine existing shot blocks show the conductor's braid, two Zion views, the ensemble, the church, a rising light column, the conductor's breath, his string response and the beginning of the sky-light procession. The original performance, world, camera trajectories and musical responses are reused. This is not newly authored human animation.

The isolated lens adjustment keeps the conductor framing but focuses on his chest with aperture 0.012. Native still comparisons at source times 98.45 and 118.3 show clearer body points, head contours and garment edges while preserving the surrounding scene. A bounded stage adjustment reduces sun and rays to 65 percent, sun glow and bloom to 75 percent, and caps aperture at 0.008. At source 106.05, this reduces the warm veil and improves blue-body and gold-instrument separation while retaining the bright musical crest.

The complete encoded movie contains 1,800 native 1080p frames at 60 fps. Every frame and presentation timestamp was decoded and checked. The coordinator and an independent reviewer inspected the full-sequence contact sheet, native frames and neighboring frames at six within-shot render joins. Those joins showed no visible camera, geometry, exposure or performer reset. The automated cut-aware scan found no large-jump, brightness-reversal or prolonged-static candidates under its stated thresholds. These are bounded continuity findings, not proof of natural acting.

The images retain clear limits. The stage's pale entrance veil recedes in the sampled sequence, but large source text and warm haze still compete with the choir. The authored architectural flash around output 12.1 seconds strongly veils the building. Bright ribbon intersections sometimes obscure fine hand detail. This contiguous excerpt starts within the song and ends during a procession entry, so it does not provide a newly designed conclusion.

The focused conductor, traveling light and changes of scale make the source's cinematic structure more readable than the previous sparse platform. A more expressive new performance still requires the acting work described above. Real-time playback, complete perceptual musical synchronization and aesthetic approval are not claimed by the image review or numerical checks.

[account]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/project-docs/backdrops/s11-full2/HOW-IT-WAS-MADE.md
[previous]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/e46c149fb50908e7f5e87832701346f67b5f0201/tools/promo_people_example/README.md
[verification]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/e46c149fb50908e7f5e87832701346f67b5f0201/tools/promo_people_example/VERIFICATION.md
[people]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/e46c149fb50908e7f5e87832701346f67b5f0201/tools/promo_people_example/people.py
[environment]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/e46c149fb50908e7f5e87832701346f67b5f0201/tools/promo_people_example/environment.py
[approved]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/46df53b98a43f58e51a78d40ee5794108a68e13c/tools/nine_colours_minor/README.md
[finale]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/46df53b98a43f58e51a78d40ee5794108a68e13c/tools/nine_colours_minor/finale.py
[stage]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_stage.py
[conductor]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_dance.py
[effects]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_music_fx.py
[musicmap]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_music_map.py
[frozenactor]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/d928ff9eafe02ac3150f0c646bdcc497fe5a7278/engine/p3d/actor.py
[frozencloth]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/d928ff9eafe02ac3150f0c646bdcc497fe5a7278/engine/p3d/cloth.py
[crowdengine]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/f43f4514e4bc42dc25166e90160d98219f5a0db4/engine/p3d/crowd.py
[referenceactor]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/f43f4514e4bc42dc25166e90160d98219f5a0db4/engine/p3d/actor.py
[procession]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_procession.py
[zioncrowd]: https://github.com/lovelaceaml-hub/concert-backdrops/blob/34f835206dcb26cfa0bd7e321171d3d224e3aa7d/tools/s11_full2/s11_zion.py
