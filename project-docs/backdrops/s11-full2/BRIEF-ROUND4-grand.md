# Round 4: GRAND (Anthony's words: "It needs to be grand. Do not bound yourself or limit yourself. As amazing and powerful the song is, the video should match.")

## Look at the references first (Read each image)
Folder: /tmp/claude-0/-home-user-concert-backdrops/284ecd5f-63c5-587c-9ba6-baa226fb663e/scratchpad/threads/refs/
- promo_01 to promo_13: frames from the approved promo and its sister films (phone screenshots; ignore the black bars and the player bar). What they show:
  - 01: a huge glittering title in the sky over a mirror sea, a lone figure of light, glowing clouds of light along the horizon.
  - 02: comets shooting up out of the sea into the sky through billowing clouds of light; a golden horizon; rainbow arcs on the water.
  - 03: a blazing white sun with great rays; comets fanning out from it; clouds of light on the horizon.
  - 04: a fly-through tunnel between two towering walls of glowing cloud, coloured light streaks racing on the water toward the vanishing point.
  - 05: pillars of light falling from clouds of light onto the sea, a starfield above.
  - 06 to 08: banking camera (the horizon TILTS), comets crossing the lens, a constellation drawn by a comet.
  - 09: comet ribbons drawing huge loops round a figure.
  - 10: racing low over a warm orange sea with comets streaking past.
  - 11, 12: a figure of light dancing with a ribbon of light, comets flying in.
  - 13: looking up into a starfield, a comet sweeping past.
- other_*: other concert backdrops (Anthony's earlier references): misty mountains, mirror sea full of floating lights, lavender skies, expression symbols as constellations.

## What "grand" means here
- **Camera like the promo's rollercoaster**: banking turns with the horizon tilting (shot key `roll`: degrees, a number, a pair (start, end) or a function of time; now supported by the core), low fast flights skimming the mirror sea, swoops up and over, flying through canyons of cloud, spirals and corkscrews round subjects, dives, looking straight up into the stars. Big, confident moves that follow the music (the core music pace still applies). Cuts stay on the edit blocks (exact t0/t1).
- **Clouds of light**: the core now has `CloudBank(center, size=(w, h, d), puffs, seed, gain, bright, colors)`: billowing glowing clouds with glitter inside (gold below, rose and lavender above). Place your own: canyons to fly through, banks behind your subject, clouds the comets burst through. The core keeps banks on the horizon all film.
- **Pillars of light**: `Pillars(bases=[(x, z), ...], top, color, width, gain)`: columns of light falling from the sky onto the sea, pulsing with the beat. Use them for the holy moments.
- **Comets**: bigger and bolder: shooting up out of the sea, sweeping close past the lens, drawing loops and helixes round your subject, fanning out of a blazing light, leaving trails across the whole frame. `Comet(..., width=...)` can be much wider (1 to 3 m near the camera).
- **Rays**: a blazing light with great rays at the peak moments (`add_rays`).
- Everything still reacts to the music: beat, hits (`KICKS`), intensity.

## Rules (unchanged)
Your own file only; no git; s11_light.py and the core belong to the coordinator (ask for changes in your report); phrases must stay readable; no white-out; keep frame cost within about 2x of now (clouds are static point sets, cheap; keep comet n modest). Check with quarter-size stills of each block's middle and a few at half size. Report briefly with still paths, within about 25 minutes.
