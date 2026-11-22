> Superseded in part (2026-11-19): Anthony later asked for the church name and the church emblem on the building, the choir and orchestra as blue sparkles with gold instruments, and calmer, deliberately placed clouds. See DESIGN.md in this folder for the current design.

# Song 11 backdrop v2: brief shared by every scene thread

You are one of five threads working at the same time on one concert backdrop video, each on its own scene file.
The coordinator (the session that started you) merges, commits and reports to Anthony, the owner.

## The film
- Song 11, "Almighty God Who Knows the Future" (the concert finale). 4:20 of music plus a 15 s calm hold:
  275.0 s at 60 fps, 1920x1080. The song is about God the Mother being preached and the whole world coming to
  the World Mission Society Church of God.
- The journey: the waiting heavenly city on Mount Zion at pre-dawn, out over the Earth, back to Mount Zion
  (climbing higher at each "standing firm" line: 1:30.72, 2:51.48, 3:32), the sun rising over Zion, the whole
  world, then home to everyone on Mount Zion. Light: pre-dawn to full sunrise.
- Fully rendered with code, like the approved promo (the Film 10 Revision 3 engine): points, particles, light.
  **No AI-generated images, no painted plates, no generated figures.**
- People of light: whole and clothed, glittering, faceless. Heavenly Mother is never shown as a figure (light only).
- Hearts are in the nine campaign colours (`COL9`). Expressions are subtle only (hearts or lights).
- Use the whole frame (no calm bottom band). The words (phrases) ride near the middle-upper part of the frame
  (screen y about 0.6, depth 30 m in front of the camera); the small signature lockup sits top-left all film.
  Keep the area behind a phrase calm enough to read while it is on screen, and never white it out.
- Camera: promo-like, flowing, cinematic, cut on the music's hits (each cut hidden in a soft flash).
- Music drive: loudness (`loud(t)` 0..1), hits (`hit_pulse`), a soft pulse on every beat (`beat_pulse`).

## Hard rules
- **Never commit, push, or `git add`.** The coordinator does all git. Never `git add -A` (fonts is a symlink).
- **Edit only your own files** (named in your task). Never edit `tools/s11_full2/s11_full2.py` (the core),
  `render.py`, `s11_cards.py`, `s11_prepare.py`, or another thread's file. If you need a change in the core or
  in another thread's file, say so in your report.
- **Cut times are locked to the music.** In your `SHOTS` change keys (camera positions and targets), fov,
  aperture and focus, but never `t0` or `t1`, and never add or remove shots, unless your task says so.
- No em dash or en dash anywhere (in code, comments, reports). Use commas, colons or "to".
- No lettering or logos on buildings. No lyrics files, no media in the repo.
- Render only half size for checks (`--scale 0.5`). Never render video ranges. Never run "playwright install".
- Never use Sonnet; never start other agents.

## How to render and look
- Stills: `cd /home/user/concert-backdrops && S11_CACHE=/home/user/work/s11v2/cache_<thread> timeout 600 python3 tools/s11_full2/render.py --stills 25,84.5 --scale 0.5 --outdir /home/user/work/s11v2/<thread>/r1`
  Each still is named `tNNNN.NN.png`. Use your own cache folder (`cache_church`, `cache_stage`, `cache_zion`,
  `cache_procession`, `cache_coda`; already filled) so threads never write the same cache file.
- Shell commands time out after 2 minutes: run longer renders with `run_in_background` and wait for the
  notification. The first frame of each run loads and may bake new crowd bodies (30 s to 2 min); after that a
  still costs about 1 to 4 CPU s. Five threads share 4 cores: render small batches (at most 6 stills), one
  render at a time per thread.
- Look at the stills with the Read tool (PNG). A contact sheet helps:
  `python3 -c "from PIL import Image;import glob;fs=sorted(glob.glob('DIR/t*.png'));ims=[Image.open(f) for f in fs];w,h=ims[0].size;S=Image.new('RGB',(w*2,h*((len(ims)+1)//2)));[S.paste(im,((i%2)*w,(i//2)*h)) for i,im in enumerate(ims)];S.save('DIR/sheet.png')"`
- The words check prints "PROBLEM: phraseNN read for ..." lines; those are the coordinator's, ignore them.
- Keep the cost of a full-size frame reasonable (about 3 CPU s or less at full size, so under 1.5 at half size
  after the first frame). 16,500 frames must render in a few hours.

## The code
- Core: `tools/s11_full2/s11_full2.py` (read it, do not edit). Your file starts with
  `from songs.s11_full2 import *`, which brings in everything the core defines before the thread imports:
  - music: `HIT` dict of hit times, `SLAM1/2/3` = 82.08, 162.86, 201.73, `DROP1/2/3`, `CODA`, `STEP_DOWN`,
    `HELD`, `LAST_CHORD` = 254.07, `FULFIL`, `STRINGS`, `BEATS`, `loud(t)`, `beat_pulse(t)`, `hit_pulse(t, times)`,
    `PHRASE_LIST` is defined later in the core (read it for when words are on screen);
  - colours: `COL9`, `GOLD`, `GOLD2`, `WHITE`, `CRYSTAL`, `ROSE`, `VIOLET`, `lin(hex)` (to linear rgb);
  - places (metres, y up, the sea of glass is y = 0, the camera mostly looks toward -z): `ZC` (foot of Mount
    Zion, (0, 0, -420)), `N_TIER` 7 terraces, `tier_r(k)`, `tier_y(k)`, `SUMMIT` 70 (plateau height), `R_TOP` 92,
    `CHURCH`, `FACADE_Z` (the church front's middle, z = -417; keep it there), `SQUARE` (the square before it, where the orchestra
    plays), `CHOIR_STEPS` [(y, z) of each step the choir stands on], `GLOBE_C`, `GLOBE_R`, `ZION_LL`,
    `SKY_STAGE`, `globe_point(t, lat, lon)`;
  - helpers: `_v(x,y,z)`, `_unit`, `_ss`, `_sc(a,b,x)` (smoothstep), `_win`, `_env(t, a, b, fade_in, fade_out)`,
    `_seg(a, b, step)` points along a line, `_ring(c, r, y, step)`, `_box(c, w, d, h, step)` (edges),
    `_windows`, `_dome`, `_batch(pos, size, color, alpha, kind, emit, **kw)`, `Static(batches, gain_fn)`
    (static point sets, sent to the GPU once), `GCrowd(gain=fn, **Crowd keys)`;
  - shot lookups (valid at render time): `shot_name(t)`, `shot_kind(t)` ("local", "stage", "sky", "globe"),
    `globe_view(t)`, `stage_view(t)`, `local_k(t)`, `city_k(t)`.
- Point set protocol (engine p3d): an object with `sample(t)` (or `sample(t, cam)` with `wants_camera = True`)
  returning a dict or list of dicts (batches), optional `gain(t)`, `static = True` for unchanging sets.
  Batch keys: `pos` (N,3), `size` (metres, scalar or N), `color` (linear rgb, 3 or N,3), `alpha`, `kind`
  ("spark" sharp point, "soft" glow disc, "line" with `pos2`), `emit` (brightness), `birth`/`fade`/`flash`
  (appear at a time), `twinkle`, `seed`, `dof` (lens blur share), `reflect` (mirror in the sea).
  Engine source: `/home/user/concert-backdrops/work/nine_colours_minor/render1/engine/p3d/` (api.py, world.py,
  camera.py). People: `Crowd` from `work/nine_colours_revision3/claude-final/engine/p3d/crowd.py` (read its
  docstring for kinds: stand, walk, run, sit, raise, clap, bow, pray, open, wave, heart, cheer, light, nod,
  kneel, child; `act` times; `points` per person; `start` waves). Bodies: `.../claude-final/engine/p3d/body.py`.
  Brand hearts: `/home/user/concert-backdrops/engine/p3d/brand_hearts.py` (`heart_points`).
- Camera: each shot is `dict(name, kind, t0, t1, fov, aperture, focus (optional), keys=[(t, pos, target), ...])`;
  moves are linear between keys within a shot. The camera state at render: `CameraState` (pos, target, fov,
  `basis()` gives right, up, forward).
- Bursts of light hide each cut (core). Phrases are drawn by the core.

## Your report (keep it short, under 300 words)
What you changed, the stills to look at (full paths of your best final set at half size), what you could not
fix, and any change you need from the core or another thread. Plain words, no dashes.
