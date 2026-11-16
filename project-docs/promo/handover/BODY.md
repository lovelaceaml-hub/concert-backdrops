# Hand-over from helper BODY (Fable) to its Opus successor

## Branch head
`engine-p3d-bodies` at a80d409, pushed. Contains origin/engine-p3d merged at fda3c4d; CORE has since moved (025bcd0 or later), not merged yet. No PR.

## The human asset
- What: MakeHuman "hm08" base mesh with default skeleton and skin weights, plus shape targets for a woman, a man and a child. Motion clips (walk, run, jump, spin, two dances) are the DeepMimic reference motions.
- Licence: mesh, rig, weights and targets CC0 1.0 (anny/data/mpfb2/LICENSE.md, mesh header, weights file). Motion clips: zlib per Bullet SDK LICENSE.txt; DeepMimic repo MIT. DeepMimic clips derive from CMU and SFU motion capture; SFU's own terms were not verified (see the coordinator's decision below).
- Fetch: from PyPI only. tools/build_p3d_body.py downloads wheel anny==0.6.2 and sdist pybullet==3.2.7 and bakes assets/p3d/body_v1.npz (687 KB). Committed with a .gitignore exception and assets/p3d/README.md (sources, licences). Nothing downloaded at render time.
- Bake: mouth bag and eye sockets removed and closed, face smoothed to a mannequin (a profile keeps only its outline), face and toe bones folded into head and feet, metres with soles at y = 0. The bake's own download step (no arguments) has not been run; the committed file was built from already-extracted packages with --smooth 160 (now the default).

## Rendered (no GitHub runs; all here)
- Shared-script stills (real renderer, 1080p), song p3d_dev, audio audio/promo/s01.mp3: scratchpad/body/prev/dev1 (before the last rewrite) and scratchpad/body/prev/dev2 (current code): t = 4.0, 8.0, 12.5, 13.2, 18.0.
- Numpy preview contact sheets in scratchpad/body/prev/: m_walk, m_run, m_poses, m_kneel, c_walk, c_hair, g_more, g_body, g_contact (.png).

## Done and seen working
- Form and skinning (engine/p3d/assets.py): three shapes at 1.59, 1.73, 1.31 m; neutral pose; area-weighted surface points.
- Motion (motion.py, actor.py): walk and run are retargeted mocap (walk foot slide about 5% of a step); posed by hand: stand and breathe, look up, reach, open arms (low to raised), blow, raise, pray, bow, kneel (two or one knee). actor.py blends motions and gestures on a timeline, with travel and turning.
- Cloth (cloth.py): skirt, wide sleeves, veil and hair strands; deterministic whatever frames are asked. Seen on walking then standing, and running.
- Real renderer (dev2): veiled robed figure from behind, arms open, rays behind the head; a man walking in tunic and trousers shedding light with lake reflection; two hands with trails approaching; a rim-lit profile with a dark body and particles streaming off the back.
- Contact (preview only): hand on shoulder within 1.6 cm; two handshakes at a shared point within 2 mm; embrace with targets on the other body's shoulder blades.
- Gesture library (preview only, gestures.py): touch, hand_on_shoulder, handshake, high_five, embrace, arm_round, cup, offer, listen, raise_hand, clap, throw, wave, brace, hold_thread; motions sit and shuffle; elder stoop; deep bow; child running and jumping.

## Half done
- Written but never run (engine/p3d/): effects.py (form, dissolve, petals, birds, blow, disperse; hand-over to targets: to=, Body.handover, Takeover, Body.free; reversible amount; Wind; hang); only shed and Flare rendered. looks.py: plexus (with constellation LOD), dots, window; only glitter and rim rendered. body.py: scale, frame, wash, sweeps, look weight/after/before, parts bust / hand.X / hands, where, constellation, shape_points; exact hand placement (hand=dict(...)) rendered through Hands. actor.py: at as keys or a function; hand pose keys.
- Look tuning from dev2: glitter has too many four-point glints; rim line too thick and the dark mask leaves a halo (Body.mask, grow); hair lines drawn through the head; Flare far too bright and large for a hands close-up; veil faint and the head shows through it.
- Not started: proof stills of five framings with two looks each, 0.25 s motion pairs; the 20 s proof video; HOWTO section W (module docstrings are the only reference); engine/songs/p3d_dev.py is a scratch stage, not a proof song.

## Remaining needs, in order
1. Contact: embrace, pull up and child lift only as building blocks (to=other.where(...), at= as a function). No paired "be helped up" or "child into arms". Anchors and joint readout exist. Foot slide while turning or stepping aside unsolved; shuffle is the stopgap.
2. Motion library missing: turn on the spot, step aside, kneel and listen or reach down as named motions, be helped up, raise joined hands as a pair, turning dance beyond the raw spin clip, sitting-to-standing.
3. Sizes: scale, frame and feet at any height written but unverified. A giant's cloth moves at life-size speed.
4. Hands for macro: one placed hand works. Missing: instanced crowd of hands, a check at 40 to 80 thousand points per hand, a review of the pose library.
5. Reversible effects: written, untested. Gather from and return to a point field is form with source= plus amount, untested.
6. Looks: constellation, storm-to-calm blend (two looks with weight), wash, bloom sweep, igniting sleepers: written, untested.
7. Heavenly Mother: long veil is veil=dict(length=1.5), untested; hold_thread and arm_round exist; the very large veil sheet others ride and gather from not started.
8. Crowds: not started. Plan: baked prototype bodies, instanced with rolling start times.

## Traps
- The shell refused compound git commands and long heredocs for BODY; run git one command at a time; patch files with Write plus a small script.
- `fonts` in the worktree root is an untracked symlink to the scratchpad fonts. Never `git add -A`.
- Body.anchor is the effects' internal lookup, not the named places. Named places are Body.where (world) and Actor.where (own space).
- Own space vs world: everything inside Body is own space; only sample, where, joint, free, constellation and shape_points convert. New output paths must go through _w or _out.
- Cloth cost about 1.2 s compute per simulated second for a full outfit, from the body's start (show[0], else t = 0) up to the frame asked. Give late bodies show=(t_in, t_out).
- Grain size normalised by point density (Body.grain). Brightness very sensitive: glitter blew out until grains about 3 mm.
- In effects.py, share is the portion affected and amount is the reversible Track. Hand-over combined with amount not handled.
- Kneeling passes through a one-legged pose for about half a second; sitting through a floating one.
- Plexus needs scipy cKDTree; cloth needs scipy.sparse.
- Scratch tools in scratchpad/body/tools/; extracted PyPI packages in scratchpad/body/dl_anny and scratchpad/body/dl_pb.
