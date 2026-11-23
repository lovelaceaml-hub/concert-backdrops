# Upgrade: magnificent promos with scenes, people of light and signature effects

## Current continuation — November 22, 2026

Start with [the Claude handoff](production-system/CLAUDE-HANDOFF.md),
[current state](production-system/STATE.json) and the standing owner directions
in [root AGENTS.md](../AGENTS.md). The sections below retain their earlier
production/design context. Dated instructions about queues, phone copies,
missing song recordings or cloud-only GPU use do not override the current
handoff and owner directions. All eleven original song recordings are retained;
older full-song movie recovery gaps are documented separately. The completed
renewed Song 11 movie is a 1080p60 design/review delivery; final4K60 requires
owner approval of design, timing and content. There is no unattended render queue.

Anthony, 2026-11-13: "make sure the full expressions a created and used beyond only using current engine effects. Do not be lazy. Make these videos magnificint. They shouldnt just look like one scene but multiple things should go based on the theme, make sure the full expressions a created and used beyond only using current engine effects."

What this means for every promo (and later the full videos):
1. Several scenes, not one. Each one-minute promo moves through 3 to 6 distinct scenes that follow the song's theme and the design doc (for example song 04: the frozen lake, the hidden pain seen in the reflection, the sister walking across the ice, the embrace, the thaw at sunrise). Scenes change with purposeful transitions on musical moments (dissolve, light bloom, camera push through, ripple wipe), never hard cuts.
2. The expressions are acted out, in full. Every expression that appears is shown as people of light doing that exact everyday act (greeting a lonely person, thanking, apologizing and reaching out first, embracing and forgiving, letting another go first, listening carefully, praying for someone, offering a hand, praising), with the full campaign words appearing as the act happens, then rising into its star.
3. Signature effects. Each song's design has its own effects (snow and the rose, the shattered sky and mended moon, the thaw, the tree of blessing, the wheat field, the lantern procession, the embroidered sky, the net of light, the great lamp, the city and gate). The promo must show at least two of them for real.
4. Magnificent: rich depth, light, motion and feeling in every second; the look stays the song's own (DESIGN-SYSTEM.md section 6); THE MESSAGE stays at the center.

## New engine features (built by the engine builder session, in the repo, merged before songs use them)
A. Scene plates. A song file can list SCENES: dict(image="assets/plates/sNN/name.jpg", t0, t1, fade_in, fade_out, zoom=(start, end), pan=((x0, y0), (x1, y1)), water=True|False, opacity=1.0). A plate is a painted 1920x1080 picture drawn behind all the engine's light (sparks, motes, lanterns, petals, rays, words, arch). Between plates the engine crossfades; where no plate is active the engine's own sky, mountains and lake show. Plates move slowly (zoom and pan) so they never look like still photos. Optional water shimmer on the lower part of a plate (water=True) so the lake ripples and glitters.
B. People of light. A song file can list FIGURES: dict(poses=["assets/figures/name_a.png", "assets/figures/name_b.png", ...], t0, t1, pose_times=[...], x, y, height, color, glow). Each pose image is a white line-art silhouette on black. The engine turns it into thousands of golden sparks (like the words), gathers them out of the air at t0, morphs the sparks from pose to pose at pose_times (so the figure moves: a hand reaches out, two people embrace, someone kneels), adds a soft outline and glassy inner glow, and at t1 dissolves the figure into sparks that rise to the arch (or drift away). Figures are clothed, faceless, Heavenly Mother only from behind or as hands.
C. Effect layers that songs switch on with Tracks: SNOW (falling snow, separate from petals), ICE (a frost and ice sheet over the lake with an amount that thaws), SHARDS (the sky broken into floating glass pieces that can reassemble), GOLDEN_FIELD (waves of light grain across the lower land), NET (glowing threads spreading across the frame), BEAM (a column or path of light from a point), plus existing effects. Each is optional and off by default.
D. Fragment styles: FRAGMENTS gain style= "sparks" (default), "write" (drawn stroke by stroke), "reflection" (appears in the water first and rises), "petals" (made of falling petals), "engrave" (gold engraving with sparks). Different songs use different styles.

## Assets (generated with the media-studio make_image tool: gpt-image through Codex; one generation at a time per session)
- Plates (each song session makes its own, 4 to 6): a painted scene in the song's look, matching the engine's luminous digital painting style (see Storyboards/03 I Reminisce About Your Love/ and Design Reference.png), 16:9, no text, no people (people come from FIGURES), the bottom third calm (the lake or dark ground). Ask for 1536x1024 and the session crops and scales it to 1920x1080 (ffmpeg crop and scale, light). Save to the repo at assets/plates/sNN/<name>.jpg (JPEG quality 88, under 1.5 MB each).
- Figure poses (the engine builder makes the shared library of all nine expressions, 2 to 4 poses each; songs make only their special figures, at most 3 poses each): clean white line-art silhouette of the person or pair on pure black, soft single-weight lines and a light inner fill, clearly clothed (robes or modest clothes), smooth head with no face, full body, centered, no text. Saved as assets/figures/<name>.png (1024 pixels tall, grayscale).
- Never put text in images. Check every image before using it; redo once if it has a face, text, a bad hand or immodest clothing.

## Order of work
1. Engine builder: features A to D, the shared figure library, docs, one test promo, merged. Then messages the coordinator.
2. Meanwhile each song session plans its scenes and generates its plates and special figures (not committed until its branch is made from the new main).
3. When the engine is ready, each song session rebuilds its promo with scenes, figures and its signature effects, renders in the cloud, checks every still and the video, and opens a pull request.
4. Astra attacks the results; owners fix; the coordinator merges and delivers.
