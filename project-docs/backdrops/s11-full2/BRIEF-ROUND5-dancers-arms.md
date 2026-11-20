# Round 5: dancers of light and waves of raised arms (Anthony, 2026-11-19)

Anthony loved the promo's DANCER scene: "a figure of light turning on the black mirror, leading a ribbon of light from her hand like a gymnast's ribbon; it flicks up and writes in the air". He wants "animations that move like the dancer with ribbon but it can be new fresh designs", and "waves of raised arms".

## Where things are
- Song 11 v2 code: /home/user/concert-backdrops/tools/s11_full2/ (core s11_full2.py: EDIT blocks with owners, SHOTS per thread, intensity, KICKS, beat_pulse, hit_pulse, Comet, CloudBank, Pillars, add_light, add_rays, COL9; thread files s11_church/stage/zion/procession/coda.py; s11_light.py looks). Read the core's header, EDIT and the helpers first.
- The promo's dancer (approved Film 10 R3): /home/user/concert-backdrops/work/nine_colours_minor/render1/engine/songs/ten_10_nine_colours.py (header lines 1 to 50; dancer D4 near line 142; Body("woman", motion=[(t, "dance_a")], garment="dress") near line 388; _dancer_hand / _ribbon_from_hand near line 530; the ribbons near lines 650 to 760 using p3d.api ribbon). Body motions, gestures and acting are in work/nine_colours_minor/render1/engine/p3d/ (body.py, motion.py, gestures.py, actor.py). The s11 crowds use GCrowd/Crowd with `kinds` and gestures (see s11_stage.py _SING, _gest, CHOIR_KINDS, and how zion/coda build their crowds).
- Reference frames: /tmp/claude-0/-home-user-concert-backdrops/284ecd5f-63c5-587c-9ba6-baa226fb663e/scratchpad/threads/refs/ promo_11.png and promo_12.png (the dancer with her ribbon), promo_09 (comet ribbons drawing loops round a figure). Read them.
- Look of the film now: dark misty heavenly night until the coda's sunrise (201.73), glowing clouds placed deliberately (Anthony found random clouds crowded: do not add clutter), choir and orchestra are glowing BLUE sparkles (#6cb2ff) with GOLD instruments and gold song books, people of light on Zion in many colours.
- Render a still: `cd /home/user/concert-backdrops && python3 tools/s11_full2/render.py --stills 120.0,250.1 --scale 0.25 --outdir /home/user/work/s11v2/<you>/<name>` (quarter size ~1-3 CPU s a frame plus a minute to load). This machine is also rendering the film on its 4 cores, so keep still batches small.

## Rules
- Only the files you are given; no git; no em or en dashes anywhere (code or comments); house rules: no facial features, everyone clothed in garments of light, Heavenly Mother never appears as a figure (only as light). Phrases on screen must stay readable (nothing bright crossing a phrase while it reads); no white-out; frame cost within about 2x of now.
- Everything moves with the music: beat_pulse, hit_pulse(t, KICKS), intensity(t).
- Check with quarter-size stills of each moment you touch (several times across each move, to see the motion), then a few at half size. Report within about 30 minutes: what you made, at which times, still paths, anything you could not do.
