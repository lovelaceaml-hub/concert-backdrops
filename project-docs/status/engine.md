# Engine upgrade: status and handoff (engine builder session)

Updated 2026-11-13, stopped on the coordinator's instruction (Anthony: "This is loading my laptop too much. All of this needs to be run in the cloud"). The work continues in a cloud session that starts from the GitHub repo.

## Where everything is
- Repo lovelaceaml-hub/concert-backdrops, branch `engine-scenes-figures`, last commit 921bf74, everything committed and pushed. Pull request: https://github.com/lovelaceaml-hub/concert-backdrops/pull/15 (open, mergeable, not merged; the coordinator merges).
- Code: engine/upgrade.py (Python side of the new layers), engine/upgrade_shaders.py (people of light, snow, net, beam, fragment styles), engine/shaders.py composite pass (plates, ice, shards, golden field, text shadow strength), small hooks in engine/render.py and engine/text.py.
- Docs: engine/UPGRADE-HOWTO.md (how a song file uses everything), docs/HANDOFF.md, assets/figures/README.md (figure list), shared notes folder file engine-upgrade-ready.md.

## Done
- A. SCENES (plates, crossfade styles fade/dissolve/bloom/ripple/push, zoom, pan, water shimmer with reflections, water_bottom, gain as number or Track).
- B. FIGURES (people of light from pose pictures: gather, morph between poses, dissolve into a star of the arch).
- C. Effect Tracks: SNOW, ICE (+ICE_FRAME), SHARDS, SHARDS_MEND, GOLDEN_FIELD, NET, BEAM, FLASH.
- D. FRAGMENTS style: write, reflection, petals, engrave (sparks default).
- Extras: PHRASES y=, TEXT_SHADOW, SKYLINE_LANTERN.
- Existing songs render unchanged (cloud run 43547805175, song 04).
- Render workflow: the video finish job also uploads small frame sheets ("<name> frames", 4 pictures of 8 frames) so a video can be checked without downloading it.
- Demo: engine/songs/demo_upgrade.py with assets/plates/demo/winter_lake.jpg, thaw_dawn.jpg, golden_morning.jpg. Stills checked over four rounds (runs 43549055025, 43549544371, 43549950542) and fixed. Write and petals styles checked with engine/songs/t_fragment_styles.py (run 43550481023).
- Figure library, all in the repo at assets/figures/ (1536x1024 grayscale): greeting_a, greeting_b; gratitude_a, gratitude_b; apology_a, apology_b, apology_c; inclusiveness_a, inclusiveness_b, inclusiveness_c; concession_a, concession_b; respect_a, respect_b; encouragement_a, encouragement_b, encouragement_c; consideration_a, consideration_b; compliment_a, compliment_b (21 poses, all checked). The originals are in ~/Pictures/AI Images/concert-backdrops-figures/ on the Mac.

## Not done
1. Final demo video check. Run 43553805648 (demo video with the frame sheets) was still rendering when I stopped. Earlier full renders 43549943362 and 43552396199 succeeded but were never looked at (the Mac's connection was too slow to download them). Next: when 43553805648 finishes, download only the artifact "Engine Upgrade Demo frames" and look at the 4 sheets. If 43553805648 failed, rerun: gh workflow run render.yml --ref engine-scenes-figures -f song=demo_upgrade -f audio=audio/promo/s04.mp3 -f mode=video -f name="Engine Upgrade Demo".
2. Astra round 1 shared-engine findings (Reviews/ASTRA-ROUND-1.md), assigned by the coordinator to this pull request, none started:
   - Finding 3: protect every text rectangle (expression words, labels, end card) from particles, petals, rays and bright scenery; dim behind text; check the label texture for a malformed H in HEALING (text.py `_tracked` label drawing).
   - Finding 8: `Track` must reject keys that are not strictly increasing with a clear error (Track is copied into each song file; add a shared check, for example in song.py after import, or a shared Track in engine/).
   - Finding 10: arch links must not start growing until both end stars are visible (engine/arch.py `link_state` starts at t1 - 1.2; start at or after the later star's arrival).
   - Finding 11: relit stars keep a thin persistent ring per relight within a song; new setting RINGS_AT_START lets a song start a star with extra rings carried from earlier songs (engine/arch.py and LIGHTS_FS in shaders.py).
   - Finding 12: optional BOTTOM_CALM setting (on by default for new song files) that fades particles, rings and reflections in the lower third and makes words form above it.
   - End card must fit three lines (PHASE2.md item 7: TAGLINE and TITLE layout in text.py).
   - Then add these to engine/UPGRADE-HOWTO.md and docs/HANDOFF.md, render a stills check in the cloud, push to the same branch.
3. After the demo is checked and the Astra fixes are in: tell the coordinator (local_d2d9d717-0b5c-469f-978c-b7c2344d33a7), and send each of the eleven song sessions: "Engine ready (pull request 15, to be merged by the coordinator shortly). Read PHASE2.md in the shared folder and do phase 2 for your song once main contains the new engine." Session ids: 01 local_df3d3f94-a5ec-4b95-ada0-21366139ec67, 02 local_579c37c5-d70b-48b4-a3aa-8133541682aa, 03 local_76859cbf-42be-44aa-b3e1-dd058d57bdd0, 04 local_ae7abd7b-795a-492a-aa93-778123fcac50, 05 local_4deb6fc4-5c02-4851-b344-aa6e5f75feab, 06 local_ac982684-5fe7-407d-8753-7232e9ab63c3, 07 local_ae6dbdd8-49f0-4729-b988-5ce66e23bf7f, 08 local_2a6d7fcc-3b32-4aa1-8b17-46c678b15503, 09 local_61733cad-d12a-4f54-bc80-4bdf0118ab86, 10 local_7cfa1723-e6c8-4eba-b761-0151b7232e58, 11 local_1f91fc19-74cb-4e04-a00c-c5af2df2452a.

## Lessons for whoever continues
- Bright dawn plates wash out white words: raise TEXT_SHADOW (1.5 to 1.7) and lower the plate's gain under the words.
- Figures read best at height 0.33, feet y 0.24, words y 0.30 with size 90 to 112.
- ICE_LINE and a reflection fragment's line= are screen heights: where the plate's lake meets the shore after its zoom.
- A test song that imports another song must reinstall the arch into that module (see t_fragment_styles.py).
- Shader compile check without rendering: compile every program in shaders.py and upgrade_shaders.py with moderngl (a standalone context); this was done on the Mac and should move to the cloud.

## Log
- 2026-11-13: engine features built and checked in the cloud (runs listed above); pull request 15 opened; stopped at a safe point on the coordinator's instruction.
