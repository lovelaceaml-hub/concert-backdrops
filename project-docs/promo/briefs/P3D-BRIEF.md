# New direction: lifelike people made of particles, a moving camera, more energy

Repo: lovelaceaml-hub/concert-backdrops. Mechanics and rules (cloud renders, one gh run watch per run, REST only, no em or en dash, commit trailers): /tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/EPIC-BRIEF.md

## What Anthony said (after watching the first epic promo)
"Make it even more epic. This needs to excite people. Also the people and heavenly mother all look weird. It's also not what I expected. I attached photos that give an idea of the effects I want but I want the people and effects to be more interpretive. Separately, you can test run another video that has the camera angle moving, revolving around, etc."

His answers to follow-up questions:
- Ordinary people may appear in side profile as featureless silhouettes made of particles. Heavenly Mother only from behind or as hands.
- Build real 3D particle bodies in the engine (not AI-generated clips).
- Music: big energy from the start.

## The reference photos (look at every one before designing)
Folder: /tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/refs/ref01.jpg to ref16.jpg
| Ref | What it shows | What to take from it |
|---|---|---|
| 01 | A head in profile, dark, its outline traced by fire-gold particles that stream off into the air | Rim of particles on the silhouette edge, dispersion off one side, dark body against a deep sky |
| 02 | Pastel profile with long flowing hair, butterflies and stars | Soft dreamy day palette, flowing hair lines, small bright stars |
| 03 | A whole body made of points joined by fine lines (a plexus), bright on black | Plexus body: points plus nearest-neighbour lines, brighter where lit |
| 04 | Two hands of particles reaching toward each other, one gold, one blue | Hands close-up, two colours meeting, trails behind each hand |
| 05 | A person from behind breaking into flakes that rise into light | Dissolve upward from the head and shoulders into flakes and sparks |
| 06 | Two people in mist, one breaking apart | Two figures, mist, one dispersing |
| 07 | A figure with red petals swirling off her | Petals streaming off a body in a spiral |
| 08 | Double exposure: a profile filled with clouds, sunrise and stars; birds flying | Silhouette used as a window onto clouds and sky; birds leaving it |
| 09 | A figure from behind in a field of glittering mist and bokeh | Small figure, huge soft field of bokeh light, haze |
| 10 | A golden figure with rays of light fanning from behind the head | Strong back light, rays radiating, heavy bokeh |
| 11 | A figure rising apart into flakes | As 05 |
| 12 | A running body made of points and lines with golden bokeh | Motion, plexus, depth of field |
| 13 | A golden figure from behind dissolving upward in a blue shaft of light | A shaft of light from above, flakes rising in it |
| 14 | A woman of coloured dots in profile blowing particles from her open hand | Particles blown from a hand as a gift |
| 15 | A glitter figure walking, half dispersing, big bokeh | Walking while dispersing, shallow focus |
| 16 | A profile with particles streaming off the back of the head, light rays from the top right | Profile close-up, back-lit rays, warm bokeh |

Common to all: lifelike human proportions, the body is a cloud of points (not an outline drawing, not a robed doll), big in frame, shallow depth of field with large bokeh, strong back light and rays, particles that form the body and stream away from it. "Interpretive" means a person is suggested by light that gathers and scatters; never a literal cartoon figure.

## House rules that still hold
- No facial features, ever. A profile is a featureless silhouette of particles. Heavenly Mother only from behind or as hands.
- Everyone clothed: bodies wear simple flowing garments of light (a long dress or robe, a veil for Mother, loose tunic and trousers or a long coat for others). Never a bare anatomical body.
- No lyrics on screen. No em or en dash. Nothing dark behind text (text is drawn by the existing 2D text system on top).
- Never commit videos, frames, lyrics or personal data.

## The system to build: engine/p3d (two helpers)
A true 3D layer inside the existing engine, switched on by a song key (`P3D = dict(...)`); songs without the key render exactly as before. World units are metres, y up, the lake surface is y = 0, a person is about 1.7 m tall.

### Helper CORE (branch `engine-p3d`, from origin/epic-promo 20b4f6e)
- Camera: position, target, field of view and roll as Tracks or functions of time, with helpers `orbit(center, radius, height, a0, a1, t0, t1)`, `dolly`, `crane`, `fly(path)` and smooth blending between moves. Subtle handheld drift option. Motion is a pure function of t.
- Renderer: additive point sprites into the engine's HDR light buffer with perspective, per-point depth of field (circle of confusion from focus distance and aperture, energy conserving, soft hexagon or round bokeh), optional motion blur by time sampling, fog and haze by depth. Kinds of sprite: soft round, sparkle star, flake or petal (rotating quad with a shape), line segments (for plexus), ribbon.
- World: star dome (thousands of stars and a Milky Way band on a sphere), a lake plane at y = 0 with a true mirrored reflection of all points (rippled, attenuated), a 360 degree ring of far hills, a sky gradient dome with a sun or light source at a chosen azimuth and height (night, dawn, day palettes; campaign day colours from engine/theme.py), ground mist, volumetric light shafts and rays from a light (screen-space radial scattering that respects what is in front), the arch of nine lights as a real arc in space standing over the lake (each light can be lit at a time), floating lanterns and dust motes in volume.
- API for others (push this file first, within your first half hour, so helper BODY can build against it): `engine/p3d/api.py` with a `PointSet` protocol: `sample(t) -> dict(pos (N,3), size (N,) metres, color (N,3) linear, alpha (N,), kind, optional pos2 for line segments, optional rot, optional emit)` and `Scene.add(name, pointset, reflect=True, depth_of_field=True)`. Also a mask pass: a PointSet can be rendered into a silhouette mask, and the scene can fill that mask with a sky texture (clouds, sunrise, stars) for double exposures (ref 08).
- Integration: the 3D picture replaces or sits under the 2D sky and lake for songs that set `P3D`; the existing text system (expressions, end card, text animations), bloom, tone curve, audio reactivity, draft mode, parts rendering and QA keep working. Rendering must be deterministic and give identical frames whichever part renders them.
- Proof 1 (Anthony's separate request): a camera test video, about 25 s, named "Camera test, revolving": skim low over the lake toward the arch, rise and revolve a full turn around it as its lights wake, fly through it, crane up through rising lanterns into the stars, then pull back wide at sunrise. Use a stand-in figure of points until BODY lands. Set it to an energetic music clip (audio/promo/s01.mp3 from 31 s is the fullest; any clip is fine).

### Helper BODY (branch `engine-p3d-bodies`, from origin/epic-promo 20b4f6e; merge origin/engine-p3d as soon as its api.py exists)
- A lifelike human form as a cloud of points: get a rigged human mesh with natural proportions and real motion (walk, stand and breathe, look up, reach a hand forward, open both arms low, raise an open palm and blow, run, kneel, two people reaching hands). Look for an openly licensed asset: first inside package registries reachable here (PyPI, npm); if none bundles one, have the render workflow fetch one on the GitHub runner at render time (cached) and bring it here through a workflow artifact for development. Prefer CC0 or CC-BY (for example MakeHuman's CC0 base mesh and rig, or a Khronos sample figure); a faceless mannequin is ideal. Do not commit a third-party asset unless its licence clearly allows it; say exactly what you used, from where and under which licence. If no asset can be had, build the body as a smooth implicit surface (blended ellipsoids on a correctly proportioned skeleton) driven by real motion data; it must still read as a lifelike person in silhouette from behind, in profile and walking.
- Skin the mesh in numpy, sample 30 to 120 thousand surface points with fixed barycentric coordinates, and add garments of light simulated as cloth (long dress or robe, veil, hair or head covering) so nobody is bare. Deterministic.
- Looks (each a setting, combinable): glitter body (ref 15), plexus (ref 03, 12), bright rim on the silhouette edge seen from the camera with a dark body (ref 01, 16), dotted colour body (ref 14), double exposure fill through CORE's mask pass (ref 08).
- Effects, all driven by time and noise fields: form from drifting dust; disperse into the air from one side (ref 01, 16); dissolve upward from the head into flakes (ref 05, 11, 13); turn to petals in a spiral (ref 07); release birds or doves from the silhouette (ref 08); blow a stream of particles from an open palm (ref 14); two hands of different colours reaching until they touch and flare (ref 04); walking while shedding particles (ref 15).
- Framings to prove with stills: profile head and shoulders close-up; a figure from behind at half body with rays behind the head (as Heavenly Mother, veiled, from behind); two hands close-up; a full figure walking; three to five people at different depths with shallow focus.

### After both land: the film (a third helper, directed by the coordinator)
A new 60 s concert promo, energetic from the first second, on a new high-energy medley, with the camera always moving. Sketch (to be refined): cold open on particles rushing in to form a profile that bursts apart on the first downbeat; two hands of light reaching and touching, the flare becoming the first expression; people forming from dust at many depths, joined by lines of light as words pass between them; Heavenly Mother from behind, veiled, rays behind her head, a stream of light from her open hand; everyone dissolving upward into a column that the camera spirals around, forming the arch and then the campaign emblem; day breaks through a double exposure; the poster-style end card. Build what this needs.

## Quality bar
Every proof still should look as good as the reference photos. Be your own harshest critic; iterate with cloud stills (and drafts for motion) until it does.

## Added by Anthony afterwards (applies to the film and to everything built for it)
- "Displaying all 9 expressions creatively throughout the video." Asked about pacing he said: "It doesn't need to [be] just one expression at a [time]. They just need to show and appear and transition artistically." So all nine campaign expressions appear, may overlap, and arrive, transform and leave in artistic ways. The old rule of one expression at a time held 6 s does not apply to this promo; each still gets a clear reading moment of about 2.5 s or more. Helper WORDS (branch `engine-p3d-words`) builds words made of particles in the 3D world.
- "Also previewing most of the songs for the event." The 60 s medley uses 7 or 8 of the 9 recorded songs, each for about 7 to 8 s on its strongest passage, energy high from the start (helper MED2, branch `epic-medley2`). The film changes look and place with each song section.
- The emblem and the poster-style end card rework is on hold ("Not yet"). Do not work on them.

## Rendering is now mixed (Anthony approved)
Stills, drafts and short motion checks are rendered here in this cloud session; only final full videos go through the GitHub workflow. A frame rendered here matches the same frame from GitHub (checked: 0 pixels differ against two GitHub runs).
Use the shared script, which copies the workflow's recipe and queues jobs (the machine has 4 cores shared by every helper; two renders run at once):
`/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/tools/local_render.sh WORKTREE SONG AUDIO stills "3,7.5,12" OUTDIR`
`... draft OUTDIR` (whole song at draft quality, with music, a contact sheet and the QA report)
`... frames A B OUTDIR` (up to 240 full quality frames as an mp4, for motion checks)
OUTDIR must be outside the repo. Keep jobs small and do not start several at once. Do not use the GitHub workflow for stills or drafts any more; use it only for a final full video (mode=video), and only when told to render one.

## Camera test approved
Anthony on the camera test (run 43720966507, "Camera test, revolving"): "It's great. It can adjust speed accordingly." The camera language is approved. Speed is free per film and per moment: match it to the music and the idea (fast whips, dives and rolls on the hard cuts, slower revolves on the breath and the reading moments).

## Model
Anthony: "Make sure you use opus." Every helper from now on runs on Opus. Commit messages end with:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01DSHsMeB7ain7qg3RYXYMEW
