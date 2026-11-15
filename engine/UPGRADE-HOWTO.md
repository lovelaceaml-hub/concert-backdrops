# How a song file uses the engine upgrade

Built 2026-11-13 for Anthony's request: "make sure the full expressions a created and used beyond only using current engine effects. Do not be lazy. Make these videos magnificint. They shouldnt just look like one scene but multiple things should go based on the theme".

Everything below is optional. A song file that sets none of it renders exactly as before. The working example that uses every feature is `engine/songs/demo_upgrade.py` (60 seconds, rendered with the song 04 promo clip).

Section E lists the shared fixes from Astra round 1 (text protection, calm lower third, ring history, strict Tracks, the three-line end card) and the share copy.

Times are seconds into the video. A "Track" is the timeline helper (new files: `from track import Track`): `Track([(t, value), ...])` eases smoothly between keys. Any setting below that takes a number or a pair can also be a Track or a function of time. Colors are `"#rrggbb"`.

**Contents**

- A. Scenes (painted plates)
- B. Figures (people of light)
- C. Effect layers (each is a Track, 0 = off)
- D. Fragment styles
- E. Shared fixes from Astra round 1 (2026-11-14)
- F. Fixes from the round 2 attack reviews (2026-11-14, branch engine-fix-r2)
- G. Moving figures (round 3, 2026-11-14)
- H. Living figures (2026-11-15, branch engine-living-figures)
  - H5. The silk look: bodies of light instead of sparks (2026-11-15, branch engine-figure-look)
- I. Theme colours, bubbles, leaves (2026-11-15, branch engine-theme)
- J. Text animations (2026-11-15, branch engine-text-anims)
- K. Gathering and the passed light (2026-11-15, branch engine-gathering)
- L. Water ripples and campaign symbols (2026-11-15, branch engine-water-symbols)
- M. Creatures of light: doves, butterflies, fireflies (2026-11-15, branch engine-creatures)
- N. Living nature: flowers, tree, blossoms, waterfall, stream (2026-11-15, branch engine-nature)
- O. Sky and camera (2026-11-15, branch engine-sky-camera)
- P. Music reactivity and automatic timing (2026-11-15, branch engine-audio)
- Q. Output: 4K, 60 fps, pre-show loop, live cue mode (2026-11-15, branch engine-output)
- R. Draft mode and the automatic quality check (2026-11-15, branch engine-qa)
- S. Everything together (2026-11-15, branch engine-epic)
- T. Rendering
- U. Small optional keys added for the epic promo (2026-11-15, branch epic-promo)
- V. The 3D layer: camera, point sets, world (2026-11-15, branch engine-p3d)

## A. Scenes (painted plates)

```python
SCENES = [
    dict(image="assets/plates/s04/frozen_lake.jpg", t0=0.0, t1=20.0, fade_in=1.0, fade_out=3.0,
         zoom=(1.12, 1.04), pan=((0.0, 0.02), (0.0, 0.0)), water=True, water_line=0.36),
    dict(image="assets/plates/s04/thaw.jpg", t0=17.0, t1=40.0, fade_in=3.0, fade_out=3.0,
         transition="dissolve", zoom=(1.04, 1.12), water=True, water_line=0.36),
]
```

- A plate is drawn behind all the light (sparks, motes, words, figures, the arch). Where no plate is active the engine's own sky, mountains and lake show.
- `t0`, `t1`: when the plate is on screen. `fade_in` runs from `t0`; `fade_out` ends at `t1`.
- Crossfade: start the next plate before this one ends (`next t0 = this t1 - fade_out`, and give the next plate the same `fade_in`). The earlier plate stays whole underneath while the next one comes in. At most two plates overlap at any moment.
- `transition` (how the plate comes in): `"fade"` (default), `"dissolve"` (an organic dissolve with a glowing edge), `"bloom"` (the change hides inside a flash of warm light; `flash=0.9` sets its strength), `"ripple"` (a ring spreads from `ripple_from=(x, y)` and wobbles the picture like water), `"push"` (the camera moves forward: the old plate grows past the viewer while the new one grows into place; give both plates a zoom of at least 1.08).
- `zoom=(start, end)`: 1.0 shows the whole picture; 1.05 to 1.15 is a slow, living push. A single number holds still. `pan=((x0, y0), (x1, y1))`: the centre of view moves by these fractions of the picture (small numbers, 0.01 to 0.04).
- `water=True` makes everything below `water_line` (a fraction of the picture's height from its bottom, default the song's HORIZON) ripple and glitter, and reflects the engine's lights (words, figures, the arch) in it. `water_strength` (default 1.0) scales it.
- `gain` (default 1.0) brightens or darkens the plate; `opacity` (default 1.0) lets the procedural sky show through.
- Plates come out with their own colours: the engine undoes its tone curve for them, then adds its glow, vignette and grain.
- Set `SKYLINE_LANTERN = 0.0` in a song that is all plates: it hides the small light that travels along the drawn skyline.

Preparing a plate: make it with the media-studio `make_image` tool at 1536x1024 in the song's look (luminous digital painting like Design Reference.png and the song 03 storyboards; 16:9 framing; no text; no people; the bottom third calm, usually the lake). Then crop and scale it to 1920x1080 and save as JPEG quality 88 under 1.5 MB:

```
nice -n 19 ffmpeg -v error -y -i in.png -vf "crop=1536:864:0:(ih-864)/2,scale=1920:1080:flags=lanczos" -q:v 3 assets/plates/sNN/name.jpg
```

Then look at where the lake meets the shore and set `water_line` to that height (fraction from the bottom of the picture).

## B. Figures (people of light)

```python
FIGURES = [
    dict(poses=["assets/figures/apology_a.png", "assets/figures/apology_b.png", "assets/figures/apology_c.png"],
         t0=4.0, t1=19.0, pose_times=[8.5, 13.0], x=0.5, y=0.24, height=0.33, to_star=2, color="#ffc78f"),
]
```

- The pose pictures become about 12,000 golden sparks plus a soft outline and a glassy inner light that flows slowly upward.
- `t0`: the sparks gather out of the air and spiral into the first pose (`gather`, default 3.0 seconds).
- `pose_times`: when the move into each following pose starts (one time per pose after the first). Each move takes `morph` seconds (default 1.8); the sparks ripple through the body so it looks like movement, not a cut.
- `t1`: the figure dissolves (`dissolve`, default 3.5 seconds), feet first. With `to_star=i` (0 Greeting to 8 Compliment) half the sparks fly in an arc into that light of the arch; or `to=(x, y)` for any point; `leave="drift"` makes them drift upward and fade instead.
- Placement: `x` is the centre, `y` the bottom of the pose picture (the feet stand on it), `height` the picture's height, all as fractions of the screen. The library pictures are 1536x1024 with the people about 92 percent of the height, centred. Height 0.30 to 0.36 suits a pair; keep the feet at about 0.22 to 0.28 so the words fit above and the bottom third stays calm.
- Look: `color` (the warm tint, default "#ffcf8a"; use the expression's own color softened), `glow` (overall strength, default 1.0), `glass` (inner light, default 1.0), `sparks` (spark brightness, default 1.0), `spark_size` (default 1.0), `particles` (default 12000), `flip=True` mirrors the pictures.
- Timing with the words: let the act play for 5 to 8 seconds, form the expression's words (PHRASES `form`) as the key gesture happens, set the figure's `t1` about half a second before the words' `hold`, and the words and the figure's sparks reach the light together.
- PHRASES can now take `y=` (the centre of the words as a fraction from the TOP of the screen, default 0.392). With figures on screen use about 0.29 to 0.31 and a smaller `size` (90 to 112) so the words sit between the people and the arch.

Shared library: `assets/figures/README.md` lists every pose. Song sessions may add special figures (at most 3 poses each): make them with `make_image` using the same prompt pattern as the README, check them (no face, no text, good hands, modest clothing), then prepare each one:

```
nice -n 19 python3 tools/prepare_figure.py "<generated picture>" assets/figures/<name>.png
```

That removes drawn ground lines, scales the drawing to the same size and puts the feet on the same line, so the poses line up when the sparks move between them.

## C. Effect layers (each is a Track, 0 = off)

| Setting | What it draws | Extra settings (defaults) |
|---|---|---|
| `SNOW` | falling snow in depth: tiny far flakes, large soft near ones, swaying | `SNOW_WIND` (0.35), `SNOW_SPEED` (1.0), `SNOW_COLOR` ("#eef4ff"); amount 0 to 1 is the share of flakes |
| `ICE` | a sheet of frost and ice over the lake with cracks and a glint; lowering it thaws the ice in organic pools with glowing warm edges | `ICE_LINE` (HORIZON: where the ice ends), `ICE_OPACITY` (0.92), `ICE_COLOR` ("#cfe2ff"), `THAW_COLOR` ("#ffbf8a"), `ICE_FRAME` (0: frost creeping in from the corners of the frame) |
| `SHARDS` | the sky above `SHARDS_Y` breaks into floating, slowly turning pieces of glass with bright rims; back to 0 and they reassemble | `SHARDS_Y` (HORIZON + 0.015), `SHARDS_SCALE` (4.2 pieces per screen height) |
| `SHARDS_MEND` | golden seams along the same cracks, glinting, like a mended moon | `SHARDS_COLOR` ("#ffd27a") |
| `GOLDEN_FIELD` | a field of light grain over the land below `FIELD_LINE`, with waves of light rolling through it in the wind; the bottom stays darker for the performers | `FIELD_LINE` (HORIZON), `FIELD_SPEED` (1.1), `FIELD_COLOR` ("#ffc35a") |
| `NET` | threads of light spreading from `NET_ORIGIN` knot by knot, with pulses travelling along them; the value is how far it has spread (1 = whole frame) | `NET_ORIGIN` ((0.5, 0.45)), `NET_SCALE` (7 knots per screen height), `NET_Y0` (0.30: nothing below), `NET_BRIGHT` (1.0, a Track can fade it), `NET_COLOR`, `NET_PULSE` |
| `BEAM` | a column or path of light with slow god rays, rising dust and a pool where it lands | `BEAM_FROM` ((0.5, 1.02)), `BEAM_TO` ((0.5, HORIZON)), `BEAM_WIDTH` ((0.03, 0.08): width at each end), `BEAM_COLOR` ("#ffe2a8") |
| `FLASH` | a soft warm flash over the whole picture (for a big musical moment) | |

Example:

```python
SNOW = Track([(0, 0.55), (20, 0.6), (27, 0.2), (30, 0.0)])
ICE = Track([(0, 1.0), (28, 1.0), (44, 0.0)])
ICE_LINE = 0.30
SHARDS = Track([(0, 0.0), (17.5, 0.0), (20.5, 1.0), (26.0, 1.0), (31.0, 0.0)])
SHARDS_MEND = Track([(0, 0.0), (28.0, 0.0), (31.0, 1.0), (45.0, 0.0)])
BEAM = Track([(0, 0.0), (31.0, 0.0), (34.0, 0.85), (44.0, 0.85), (48.0, 0.0)])
BEAM_TO = (0.5, 0.26)
```

Remember DESIGN-SYSTEM.md section 6: each special effect belongs to one song. Agree with the coordinator before two songs use the same one.

## D. Fragment styles

Add `style=` to any entry in FRAGMENTS. `t0` is when it starts, `t1` when it is complete, `out` when it begins to leave.

| style | What happens | Good length (t1 - t0) |
|---|---|---|
| `"sparks"` (default) | the classic reveal, left to right | 2.5 |
| `"write"` | written by a pen of light: a bright nib travels along the words and sparks fall from it | 2.5 to 3.5 |
| `"reflection"` | appears first as a rippling reflection in the water, then rises out of the lake to its place (`line=` the water line, default HORIZON) | 3.5 to 4.5 |
| `"petals"` | petals drift down and settle into the letters; at `out` the wind blows them away (`colors=("#ff9fb2", "#ffe0d2")`, default the song's PETAL_COLORS) | 3.0 to 4.0 |
| `"engrave"` | carved in gold: a hot point cuts the letters, sparks fly from it, then the gold cools and catches the light | 2.5 to 3.5 |

```python
FRAGMENTS = [
    dict(text="the pain you held inside", t0=22.5, t1=26.5, out=30.0, size=88, glow="#bcd6ff", style="reflection"),
    dict(text="truly humbled", t0=31.0, t1=33.8, out=37.2, dy=0.02, size=96, style="engrave"),
]
```

Styled fragments also get a soft shadow behind them so they read on bright plates.

## E. Shared fixes from Astra round 1 (2026-11-14)

All of these are in the engine; a phase 2 song file mostly gets them for free.

- **Track** (finding 8): new song files use the shared one: `from track import Track` (delete the old `class Track` copy). Key times must be strictly increasing; a Track with keys out of order or two keys at the same time stops the render with an error that names the setting and the times. song.py also checks every Track in an older song file when it loads (songs 09 and 11 are refused until their keys are put in order).
- **Text protection** (finding 3), on for every song: behind every expression, the closing title, the end card lines, lyric fragments of every style and the corner credit, a wide soft veil (a) dims all light drawn behind the words (motes, lanterns, petals, snow, beam, net, figure sparks) before the words are drawn, so nothing crosses a letter, and (b) brings bright scenery down to a fixed calm level and takes most of its colour out, so white words always stand on a quiet warm grey. `TEXT_SHADOW` (default 1.0, a number or Track) makes the veil deeper; `TEXT_PROTECT` (default 1.0; 0 switches off part (a)) is rarely needed. Bright plates still read best with `gain` lowered a little under long text.
- **Calm lower third** (finding 12): `BOTTOM_CALM` (0 to 1, a number or Track). It defaults to 1.0 in any song file that has `SCENES` or `FIGURES` (so every phase 2 promo), 0.0 in older files. Below about 0.33 of the screen height it fades motes, lanterns, petals and most snow, water rings, sun glitter, reflections of the lights, plate water glints, thaw edges and the golden field's rows, and the expression's sparks come out of the air just above it instead of rising from the stage. People of light are not affected: they stand where you put them.
- **Arch lines** (finding 10): a line between two lights starts to grow only when both lights are visible (at the later `star` time), and takes 1.4 seconds.
- **Ring history** (finding 11): every relight (`arrive`) leaves a thin ring that stays round the light for the rest of the minute (after the expanding ring settles, about 2.6 seconds later). `arrive` can be one time or a list of times. `RINGS_AT_START` gives a light rings it already earned in earlier songs: a list of nine numbers, or a dict such as `RINGS_AT_START = {6: 2}` (light 6 starts with two rings). At most 6 rings show.
- **Three-line end card** (PHASE2.md item 7): give TAGLINE three lines. The title rises to 0.315 of the screen from the top (`TITLE` may set its own `y=`), the first line (the peace tagline) sits under it a little larger, and the date and the place come beneath, all above the lower third:

```python
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9)
TAGLINE = dict(text="Where a mother’s love reaches, peace settles.\nSunday, December 6 · 4:30 PM\n"
                    "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas",
               t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0)
```

  One or two tagline lines keep the old layout.
- **Look changes** from the demo check: shard lines are thin glass edges now, the beam is a gentle column (raise `BEAM` above 0.5 only for a single big moment), and people of light are brighter. The demo uses figures at `height=0.40`, feet `y=0.20`, with two-line words at `y=0.30` (size 96) or one line at `y=0.29` (size 112).
- **Reading time** (PHASE2.md item 4) is not enforced by the engine; plan it: formation takes about 3.75 seconds from `form`, so `hold` at least `form + 9.75` gives 6 seconds fully formed.

## F. Fixes from the round 2 attack reviews (2026-11-14, branch engine-fix-r2)

Nothing to change in a song file; all song files load as before. What changed, and the new optional settings:

- The veil and shadow behind text now follow the letters per pixel: they appear as the letters arrive (left to right for sparks, write and engrave), scale with their opacity (petals, reflection), move with a rising reflection and leave as the letters dissolve. No dark ghost before the words, no smudge after them.
- `transition="dissolve"`: its glowing edge is thin and faint by default. New scene key `edge_glow` (default 0.06; the old look was about 0.45; 0 turns it off).
- BOTTOM_CALM now also darkens a plate's own painted lower third: the plate's gain ramps from `calm_gain` at the bottom of the screen to 1.0 at 0.30 of the height. New scene key `calm_gain` (default 0.55; 1.0 turns it off for that scene).
- Plates crossfade in tone space, so a bright painted sun stays soft at partial opacity (no hard blob or spiky rim).
- Text (expressions, title, end card, fragments, the corner credit) is not mirrored in the lake any more.
- The light waves when a star lights stay above the calm lower third and off the text and credit.
- The reflection fragment style's own mirror image stays close to its line.
- tools/prepare_figure.py removes only thin floor lines (at most 10 rows thick), so filled figures and wide groups survive; add `--keep-lines` to skip the step entirely.

## G. Moving figures (round 3, 2026-11-14)

People of light are now rare and always moving (project-docs: DIRECTION-R3). A FIGURES entry's `x`, `y` and `height` can each be:

- a number (still, as before),
- a Track or any function of time, for example `x=Track([(20.0, 0.20), (25.0, 0.60)])`,
- a pair `(start, end)`, eased over `move=(ta, tb)` (default: the figure's `t0` to `t1`) with `ease="smooth"` (default), `"linear"`, `"in"` or `"out"`.

`bob=1.0` adds a gentle walking bob (a small lift per step, only while the figure moves sideways; 0, the default, is off). Use `flip=True` so the pose faces the way it walks. The sparks, the outline and the dissolve all move with the figure.

```python
FIGURES = [
    dict(poses=["assets/song_figures/s04/traveler_a.png", "assets/song_figures/s04/traveler_b.png"],
         t0=20.0, t1=25.5, pose_times=[22.5], x=(0.18, 0.42), ease="linear", bob=1.0,
         y=0.22, height=0.30, leave="drift"),
]
```

## H. Living figures (2026-11-15, branch engine-living-figures)

Anthony: "why are the people still images? Why aren't they fluid and moving like the sparkles and text?" A painted pose used to slide across as one rigid picture. Now a figure can be built on a moving skeleton, and an existing painted figure can be brought alive. A FIGURES entry that sets none of the keys below renders exactly as before.

### H1. Rigged figures: `kind="rig"`

```python
FIGURES = [
    dict(kind="rig", preset="person", t0=0.6, t1=9.0, gather=1.6, dissolve=2.6,
         x=(0.10, 0.58), move=(1.8, 8.0), ease="linear", y=0.345, height=0.36,
         actions=[(0.6, "stand"), (1.5, "walk"), (8.0, "stand"), (8.1, "turn", {"yaw": 0.95}), (8.2, "rise")],
         color="#ffcf9a", to_star=6),
    dict(kind="rig", preset="person_back", t0=9.0, t1=18.2, x=0.84, y=0.345, height=0.38,
         actions=[(9.0, "stand"), (11.4, "open", {"blend": 1.6}), (14.6, "bless")], to_star=6),
    dict(kind="rig", preset="hands", t0=18.6, t1=24.0, x=0.5, y=0.335, height=0.40,
         actions=[(18.6, "cup"), (20.2, "open"), (21.8, "offer"), (23.2, "release")], to_star=7),
]
```

- The body is about 12,000 sparks bound to a skeleton (engine/rig.py). Every frame the skeleton is posed and the sparks follow it, so limbs stride, arms swing, the robe and sleeves sway and lag behind the motion, the veil ripples in the wind, fingers curl and open, and a current of light keeps rising through the body. Fast-moving sparks leave short trails; a few sparks lift off and drift up. The soft outline and glassy inner light are drawn from where the sparks are in that frame, not from a picture.
- Faceless and clothed by construction: the head is a soft ball of light, everyone wears a long robe.
- `preset`:
  - `"person"`: a robed person, seen three-quarter (`yaw` 0.45 by default; 0 is a pure side view). `veil=True` adds a head veil.
  - `"person_back"`: the same body seen from behind (`yaw` pi/2) with a long veil that flows. Use it for Heavenly Mother (never from the front).
  - `"child"`: child proportions (larger head, shorter limbs).
  - `"pair"`: two people. `together=True` (default) side by side, walking in step but not in lockstep; `together=False` facing each other (use `"embrace"`; the key `gap` in an action, for example `(t, "embrace", {"gap": 0.16})`, brings them closer). `gap` (default 0.30) sets the distance.
  - `"hands"`: two hands with sleeves rising from below; fingers move in a gentle wave all the time.
- `actions`: a list of `(time, name)` or `(time, name, {overrides})`. Each action eases in over `blend` seconds (default 0.9; per action `{"blend": 1.6}`; per figure `blend=`) from its time, so poses flow into each other.
  - body: `stand`/`idle` (breathing, weight shift, never fully still), `walk` (legs stride, arms swing; also automatic while `x` moves, `auto_walk=False` turns that off), `offer` (both arms forward, palms up), `reach` (one arm forward), `open` (arms wide), `bless` (arms open and raised), `rise` (arms lifted up), `pray`, `embrace`, `bow`, `kneel`, `wave`, `turn` (turns toward the viewer; set the angle with `{"yaw": 1.2}`), `face` (back to the side).
  - hands: `cup`, `closed`, `open`, `offer` (palms tip out and a soft light grows above them), `release` (the light rises), `clasp`.
  - overrides may set `walk`, `lean`, `tilt` (head), `yaw`, `light`, or an arm as `arm_r`/`arm_l` = (upper arm elevation, upper arm azimuth, forearm elevation, forearm azimuth) in radians (elevation 0 hangs down, pi/2 forward or sideways, pi up; azimuth 0 forward, pi/2 out to the side, negative across the body).
- Walking: the stride is tied to how fast `x` moves, so the feet stay planted on the ground (they do not slide). `stride` sets the length of one full step cycle in figure heights (default 0.62; 0.55 for a child). `speed` (figure heights per second) makes it walk on the spot. `facing="left"`/`"right"` (default: the way it moves; `flip=True` reverses it).
- Placement and timing are as in section B and G: `x`, `y` (the feet line), `height` (head top to feet), each a number, Track, function or `(start, end)` pair with `move` and `ease`; `t0`, `t1`, `gather`, `dissolve`, `to_star`, `to`, `leave="drift"`.
- Look: `color`, `glow`, `glass`, `sparks`, `spark_size`, `particles` (default 12000), `trails` (default 1.0; 0 turns the trails off).
- Size: limbs read well at `height` 0.30 or more. Keep the feet at about 0.33 to 0.35 so the lower third stays calm.

### H2. Painted figures come alive: `warp`

Add `warp=True` to an ordinary FIGURES entry (painted poses). The drawing and its sparks bend with a slow sway from the feet up, breathe at the chest, the hem ripples, and while the figure moves across (`x` a pair or Track) its robe swings with each step (use with `bob=1.0`). A current of light rises through the body and a few sparks lift off it. For finer control give strengths: `warp=dict(sway=1.0, breath=1.0, lilt=1.0, stream=1.0)` (0 turns one part off).

### H3. Test clip

engine/songs/test_living.py (30 seconds, audio/test/s03-newsong-first-60s.mp3) shows a walking person, Heavenly Mother from behind with her veil flowing, hands that open and offer a light, and a painted pair warped alive, moving from a deep dusk into the bright campaign daylight.

### H4. Video in 10 parts

The Render workflow now renders a video in 10 parallel parts (was 4), so a minute renders in well under half the time. Nothing changes for a song file.

### H5. The silk look: bodies of light instead of sparks (2026-11-15, branch engine-figure-look)

Anthony asked for "something magnificent that would blow our mind. Ground breaking artistry." The people of light used to be dense sparks with a dotted fill: they moved well, but read as sparkly cut-outs, and a crowd as a glitter fence. The silk look draws the same skeletons (H1) and the same crowd (section K) as bodies of light. It is an option: a song that does not ask for it renders exactly as before. Code: `engine/figure_look.py` (one new file), with small guarded hooks in render.py, upgrade.py, gathering.py and one optional block of the composite (`FIGURE_TINT`). Test: `engine/songs/test_figure_look.py` (20 seconds on audio/test/silent-60s.mp3: a walker, a medium figure, Heavenly Mother from behind, two hands and a crowd of 24, from night through dawn into the bright day).

**Switching it on**

```python
FIGURE_LOOK = "silk"                      # every rigged figure (kind="rig") and the GATHERING crowd
FIGURE_SILK = dict(light_from="sun")      # optional: settings for all of them (the keys below)
# or one at a time:
FIGURES = [dict(kind="rig", preset="person_back", look="silk", veil_length=1.1, ...)]
GATHERING = dict(look="silk", ...)
```

`look="silk"` on one FIGURES entry or on GATHERING switches only that one; `look="sparks"` keeps the old look for one entry under `FIGURE_LOOK = "silk"`. Painted figures (`poses=`) are not changed.

**What is drawn**

- Body: a smooth luminous shape computed from the posed skeleton every frame (rounded cones along the bones, added up like light through frosted glass; no sparks, no outline). A warm heart and head, soft edges, a robe that breaks into mist toward the hem (no hard feet). The side that faces the light is warmer and brighter, the far side cooler, and a soft rim of light runs along the lit side (all round when the light stands behind the figure).
- Proportions: slender, about 8 heads tall, narrow shoulders, a long robe that flares softly. The head is a soft oval glow under hair or a veil. No face, ever; everyone is clothed. Heavenly Mother is `preset="person_back"` only (from behind, with a long veil).
- Cloth of light: the veil, both sleeves and the lower robe are sheets of fine threads of light; a few dozen long streamlines run down the body and trail behind a moving figure. All of them are spring chains: gravity, air that drags against the motion (so they trail behind a walk and swing on when she stops), and the shared wind (`WIND`, section N) with gusts and travelling ripples. The cloth is simulated afresh for every frame over the 3.2 seconds before it, so every frame can be drawn on its own and the 10 cloud workers agree.
- A few bright motes rise off the shoulders, the hands and the head.
- Water: each figure is mirrored and rippled in the lake (at its feet when it stands on the water, else at the water line); the mirror image fades with depth and stays calm in the lower third.
- Bright skies: light adds little on a bright sky, so there the bodies glow a little less and the composite gives them a faint tint of about the same brightness as the sky behind them (lilac on a warm sky, a warm pearl on a blue one). It is never darker than about four fifths of the sky: no dark patch, no shadow.
- Motion: poses flow into each other more slowly (`blend` defaults to 1.4 s instead of 0.9), the forearms follow the upper arms a little late (soft elbows), the wrist lifts as the arm rises, the spine and the head sway a little. `"open"` and `"bless"` are a low, graceful opening by default (the upper arms about 42 and 37 degrees below the horizontal, the forearms a little higher, palms forward).
- Gather and dissolve work as before (`gather`, `dissolve`, `to_star`, `to`, `leave="drift"`): the body blooms out of its heart; at the end it returns to its heart and one small light rises to its place in the arch.
- The crowd: each person is a small body of light in a cloak, some veiled or hooded, some bare headed, unevenly spaced (`spacing`). Those who wait are cooler and dimmer; once the passed flame reaches someone, they turn warm, glow from the heart and hold a small bright point of light at the chest, like a candle. When they lift their lights, the points rise.
- Hands (`preset="hands"`): palms, fingers that curl and sleeves as one soft shape; the offered light warms the palms.

**Keys of a figure** (each also works in `FIGURE_SILK` as the default for all; the usual keys of section H stay: `preset`, `actions`, `x`, `y`, `height`, `color`, `glow`, `t0`, `t1`, `gather`, `dissolve`, `to_star`, `veil`, `yaw`, `stride` ...)

| Key | Default | Meaning |
|---|---|---|
| `light_from` | `"sun"` | where the scene's light is: `"sun"` (the sun, or the glow on the horizon at night), `"star"` or `"star:3"` (a light of the arch), a screen point `(x, y)`, or a function of time |
| `light_color` | warm white | colour of the rim light |
| `rim` | 1.0 | strength of the rim light (0 = none) |
| `core`, `core_glow`, `head_glow` | `"#ffe9c4"`, 0.9, 0.7 | the heart's colour and strength, and the head's share of it |
| `mist` | 1.0 | how much the lower robe breaks into mist (0 = a firm hem) |
| `cloth` | True | False draws the body only (no veil, sleeves, streamlines) |
| `veil_length`, `sleeve_length`, `strand_length` | 1.0 | lengths of the cloth |
| `strands`, `motes` | 27, 30 | how many streamlines and motes |
| `cloth_color`, `cloth_glow`, `mote_glow` | `"#fff1e0"`, 1.0, 1.0 | the cloth's own tint and brightness |
| `wind`, `wind_dir`, `wind_gain` | the song's `WIND` (0.35), 1, 0.9 | wind on the cloth (a number or a Track); direction 1 = left to right, -1 the other way |
| `arms` | `"low"` | `"high"` keeps the engine's wide `open` and `bless` |
| `open_angle` | 42 | degrees below the horizontal of the open arms |
| `elbow_lag` | 0.30 | seconds the forearms follow behind |
| `reflect` | automatic | True, False, or a water line y. Automatic: on, unless the song uses scene plates |
| `day_tint` | 1.0 | this figure's share of the tint on bright skies |

Not used in this look: `particles`, `sparks`, `spark_size`, `trails`, `glass`.

**Keys of the crowd** (in GATHERING, next to the keys of section K): `look="silk"`, `spacing` (default 1.0: how unevenly people stand, in loose twos and threes with gaps; 0 = the even rows; it is skipped when the song groups the crowd itself with a `cluster` key), `veiled` (0.55: the share who wear a veil or hood), `unlit` (`"#9fb4ff"`) and `unlit_glow` (0.55): colour and brightness of those who wait, `flame_light` (1.0: how much a held light warms its holder), and `rim`, `core_glow`, `head_glow`, `mist`, `reflect`, `day_tint` as above.

**Keys for the whole song** (only in `FIGURE_SILK`): `body_glow` (0.36), `density` (1.35) and `soft` (1.4): how bright, how solid and how soft-edged the bodies are; `rim_glow` (1.0); `bloom` (0.45: the share of the bodies' light that goes through the engine's glow; the rest is added sharp, so a body is not washed white); `knee` (1.8: where bright overlaps roll off); `mist_color`; `flame` (`"#ffd08a"`); `reflect_glow` (0.62); `daylight` (automatic from the sky colours; or 0 to 1, or a Track); `day_tint_color` (`"#c4c0ff"`), `day_tint_warm` (`"#ffd9b4"`), `day_tint_strength` (0.92), `day_tint_level` (0.80: brightness of the tint against the sky behind it), `day_tint_gate` ((0.10, 0.42): how bright the sky must be before the tint starts and is full).

**Sizes and skies.** Checked large (half the screen height), medium (a fifth) and crowd size (a tenth) on a night, a dawn and a bright day sky: stills runs 43702504749, 43703267673, 43703857106 and later ones on `test_figure_look`. At crowd size the pleats, the wandering rim and the cloth are left out or melt into the body. On the bright day sky the figures stay visible but are quiet; they are at their best at night, dusk and dawn.

**Cost.** About 0.75 s per 1080p frame for the whole test scene in the cloud (two large figures with cloth, one medium, 24 people), of which the cloth is about 60 ms per figure.

**Order of drawing.** `figure_look.begin` before the figures, the figures and the crowd queue their bodies, `figure_look.resolve` draws them into their own layer, adds a share of it and the mirror images to the light (before the text protection), and the composite adds the rest sharp and the tint (texture unit 14).

## I. Theme colours, bubbles, leaves (2026-11-15, branch engine-theme)

Anthony's blend of the luminous original world with the campaign colours: cream and white light, soft sky blue, warm yellow and peach, coral pink and navy accents, fresh green leaves and iridescent soap bubbles. No dark patch behind any text, ever. A song that sets none of these keys renders exactly as before. Working example: `engine/songs/test_theme.py`.

**The quick way: one line.** After `TOTAL` (and your PHRASES, TITLE, TAGLINE, CREDIT, FRAGMENTS) are defined:

```python
import theme
theme.campaign_day(globals(), [(0.0, "dawn"), (14.0, "day"), (30.0, "golden"), (42.0, "peach"), (TOTAL, "cream")])
```

It sets the day sky Tracks (`SKY_TOP`, `SKY_MID`, `SKY_HOR`, `GLOW`), `SKY_THEME = "campaign_day"`, `TEXT_SHADOW = 0`, faint `STARS` (0.10), no milky band, aurora or rain, white and gold motes, coral and peach petals, `BUBBLES` 0.55, `LEAVES` 0.35, `GLOW_COLOR` and `color="#1f2a6b"` (navy) on every text that has no colour yet. Options: `text="navy"` (default: navy words, soft white glow), `text="coral"` (coral words, gold glow) or `text=None` (keep the light words); `bubbles=0`, `leaves=0` switch a layer off. Set any key again after the call to override it. Your own `params()` must read the module's `SKY_TOP` etc. at call time (every song file does). If your file patches another song module (like `test_theme.py`), pass that module's `vars(...)`.

Sun, clouds, rays, lanterns, petals and the arch stay as your song sets them. The arch and its rings read as faint glints on a bright sky; that is intended. On bright days keep `SUN_INT` around 0.5 to 0.8.

**Palette names** (`theme.PAL`, each top, middle, horizon, sun glow, as seen on screen): `dawn` (soft blue over peach and warm cream), `day` (clear sky blue to a cream horizon), `golden` (warm yellow and peach), `peach` (peach with a pink touch), `cream` (almost white, the luminous end). A key may also be a tuple of four hex colours. `theme.sky_tracks(keys)` returns just the four sky Tracks. `theme.display("#rrggbb")` gives the linear light the engine needs to show exactly that colour (it undoes the filmic curve). Campaign colours as constants: `theme.NAVY` #1f2a6b, `NAVY_BRIGHT` #12358f, `CORAL` #f0566a, `CORAL_SOFT` #d9606a, `GOLD` #ffd27a, `CREAM`, `WHITE_GLOW` #fff8ec, `SKY_BLUE`, `PEACH`, `LEAF_GREEN` #5fd040, `LEAF_GOLD` #d8e860.

**`SKY_THEME`** (default none = the original world): `"campaign_day"` (or a number 0..1, or a Track) makes the procedural world bright: the far and near hills turn a pale blue-peach haze instead of dark ridges, the lake stays light toward the bottom, and the vignette is much lighter (corners 0.90 instead of 0.62). The far mountain range also fades into the haze before its ends (no hard step at the right edge). Plates (SCENES) are not changed by it.

**Per-text colour.** Add `color="#rrggbb"` to any PHRASES entry, the `TITLE`, the `TAGLINE` (end card lines), any FRAGMENTS entry (every style) or `CREDIT`. The letters are then painted in exactly that colour on top of the finished picture, revealed and dissolved with the same timing as the light words, and the light layer carries only a soft glow round them (and the forming sparks take the glow colour). Extra keys: `glow="#rrggbb"` (that text's glow; default `GLOW_COLOR`, else the warm #ffc48c), `glow_strength` (default `GLOW_STRENGTH`, else 1.0), `color_alpha` (0..1, default 1). Without `color`, a text keeps its light letters; `glow` and `GLOW_COLOR` then only change the glow colour.

- `GLOW_COLOR` (a hex, or a function of time): the glow colour of every text that does not set its own `glow`. Navy words: a soft white glow (#fff8ec). Coral words: gold (#ffd27a).
- `GLOW_STRENGTH` (default 1.0): how strong the glow round coloured words is.
- Dark words need a bright sky behind them: use them with `SKY_THEME` or bright plates. Leave the light words on night scenes.

**`TEXT_SHADOW = 0` is now truly zero.** Before, 0 still capped bright scenery behind the text and darkened round the corner credit. Now, at 0 there is no cap, no veil and no dark round the credit. From 0.05 up the result is exactly as before (every existing song uses 1.0 or more); between 0 and 0.05 it eases, so a Track can fade the protection out without a jump. `TEXT_PROTECT` (dimming the light layers behind the letters, so no bubble, leaf or spark crosses a word) is separate and stays on.

**`BUBBLES`** (Track, 0 = off; the number is the share of about 140 bubbles shown): iridescent soap bubbles rise slowly, wobbling, each with a thin bright rim, a rainbow sheen that swirls round the rim, a faint film and two soft highlights. Far bubbles are small, near ones large. They thin out in the calm lower third under `BOTTOM_CALM`, and text protection keeps them out of the letters. Settings: `BUBBLES_COLOR` (rim and film, default #f4fbff), `BUBBLES_SIZE` (default 1.0; 1.0 is 26 to 118 px at 1080p), `BUBBLES_SPEED` (default 1.0), `BUBBLES_SHEEN` (rainbow strength, default 1.0), `BUBBLES_COUNT` (default 140, a plain number).

**`LEAVES`** (Track, 0 = off; share of about 48 leaves): a few leaves of light drift down slowly, swinging, turning and tumbling edge-on and back, with a bright rim, a pale vein and a glint as they face us. Settings: `LEAVES_COLORS` (pair, default green #5fd040 to gold #d8e860), `LEAVES_SIZE` (default 1.0: 30 to 92 px), `LEAVES_SPEED` (default 1.0), `LEAVES_WIND` (sideways drift, default 0.4), `LEAVES_COUNT` (default 48). Calm lower third and text protection as for bubbles. Because light alone can only brighten a bright sky, the leaves are also painted over the scene in their own colours (a tint pass, off when LEAVES is 0), so they read truly green on a day sky; `LEAVES_TINT` (default 0.85, 0 = light only) sets how strongly.

## J. Text animations (2026-11-15, branch engine-text-anims)

Anthony: "I also want different animations for the text instead of just the same one." Add `anim=` to an entry in PHRASES, to `TITLE`, to `TAGLINE` (the end card lines) or to a FRAGMENTS entry. A song may set `TEXT_ANIM = "ink"` (for example) as the default for every expression and the title; an entry's own `anim=` wins. Without any of these nothing changes: the classic sparks render pixel for pixel as before.

| anim | What happens |
|---|---|
| `"sparks"` (default) | the classic: sparks gather into the words left to right, hold, fly to the star |
| `"ink"` | each letter is written along its own strokes by a hot nib of light; the fresh ink cools, and while held a soft light keeps flowing along the strokes |
| `"bloom"` | a seed of light glows at the centre of each letter, then the letter opens outward from it, staggered left to right |
| `"rise"` | the letters float up through the water line, left to right, with a rippling reflection below the line that fades as they reach their place (`line=` the water line, default HORIZON; raised above the calm third when BOTTOM_CALM is on) |
| `"ribbon"` | a twisting ribbon of light sweeps across from the left; the words appear behind it and sparks shed from it settle into the letters; the ribbon leaves past the last letter |
| `"constellation"` | stars appear on the letters, lines of light grow between them, then the letters fill with light; the lines fade to a faint trace while held |
| `"petal"` | petals fall from above and settle into the letters, which fill in specks where they land (`colors=` a pair, default the song's PETAL_COLORS) |
| `"snow"` | the same with snowflakes (`colors=`, default the song's SNOW_COLOR) |
| `"wave"` | the classic gathering, then a ripple of brightness runs through the held words every 3.6 seconds |

```python
PHRASES = [
    dict(label="Greeting", lines=["“How are you?”"], size=176, form=5.6, hold=12.0, star=VOICE_IN, anim="ink"),
    dict(label="Gratitude", lines=["“Thank you.”"], size=150, form=18.4, hold=28.0, star=31.14, anim="bloom"),
]
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150,
             form=TITLE_HIT - FORM_DUR, hold=1e9, star=1e9, anim="constellation")
TAGLINE = dict(text="...", t0=TITLE_HIT + 1.4, t1=TITLE_HIT + 4.0, anim="ink")
FRAGMENTS = [dict(text="a quiet word of light", t0=100.0, t1=103.0, out=110.0, anim="petal")]
```

- Timing is unchanged for every animation: each part of the words is fully formed at the same moment as with the classic sparks (so `form`, `hold`, FORM_DUR and the 6 second reading time work as before, and the veil behind the words stays in step), and at `hold` the words dissolve and their sparks fly to the star exactly as before. Fragments dissolve at `out` as before; their sparks drift up.
- `anim=` on a fragment works only with the default fragment `style` (sparks); the styles in section D keep their own look.
- Nothing dark is drawn by the animations; the calm lower third stays calm (petals and flakes fall from above the words, the rise starts above the calm third).
- Choose one animation per expression to suit its words; vary them through a song rather than using one for all. Good matches: `ink` for a promise or prayer, `bloom` for gratitude or a compliment, `rise` over water scenes, `ribbon` for an energetic moment, `constellation` for the title or a night scene, `petal` or `snow` where the song already has petals or snow, `wave` for a long hold on a strong line.
- An unknown name stops the render with an error that lists the valid names.
- Engine test song: `engine/songs/test_living.py` uses ink, bloom, constellation, ribbon and rise (section H3).
- Code: `engine/text_anims.py` (shaders and preparation); `engine/render.py` only hands such texts to it.

## K. Gathering and the passed light (2026-11-15, branch engine-gathering)

A crowd of small people of light walks in from the sides and gathers in one place; then a small flame passes from hand to hand through them (the peace message spreading) and the arch brightens. Code: engine/gathering.py, drawn by one guarded call in render.py right after the figures, so text protection and the glow apply to it as to every other light. A song that sets neither key renders exactly as before. Demo: engine/songs/demo_gathering.py (44 seconds, dusk).

```python
GATHERING = dict(t0=1.0, count=96, center=(0.5, 0.343), spread=(0.40, 0.05), rows=3, hole=0.035,
                 height=(0.125, 0.10), speed=1.0, arrive_by=13.5, sides=("left", "right"),
                 colors=("#ffcf9a", "#ffd9b8", "#ffe6c4", "#ffc6a0", "#f2d0ff", "#cfe0ff"))
PASS_LIGHT = dict(t0=13.5, speed=0.15, path="crowd", start="center", source="arch", color="#ffe2a0",
                  lift=True, rise=True, arch=1.0)
```

GATHERING (all keys optional):
- `t0`: when the first people step in. `arrive_by`: when the last ones arrive (default `t0` + 14). The people bound for the middle come first, the outer ones last. `t1` (default never): when they leave; each person's sparks rise and fade over `dissolve` seconds (default 3).
- `count` (default 80; 50 to 200 stay fast: about 20 ms of numpy per frame for 100 people). `detail`: sparks per person (default 420).
- `center` = (x, feet line y). Keep y about 0.34 to 0.35: the crowd stands on the far shore and the lower third stays calm. `spread` = (half width, depth) in screen fractions; back rows stand up to `depth` higher, smaller and dimmer. `rows` (default 3, staggered so people behind stand in the gaps). `hole` (0 to 1): an open space in the middle (for a light, or the flame coming down).
- `height` = base figure height or (height, variation), default (0.13, 0.12). `children` (default 0.12): share of smaller people. `speed`: walking speed in figure heights per second (default 1.0, each person 0.8 to 1.2 times that). `colors`: robe colours, one per person at random. `glow`: overall brightness. `seed`.
- `sides`: ("left", "right") (default: each comes in from its own side), or "left" / "right" only.
- Each person is a light version of the rig (section H): the same proportions and walk cycle, planted feet, swinging arms, a robe that follows the legs and lags behind. They slow down on the last steps, turn toward the centre and settle into breathing, weight shift and small hand motion (never frozen). Heads are soft glows (no faces); everyone wears a long robe.

PASS_LIGHT (needs GATHERING):
- `t0`: when the flame starts. `source`: None (the first person simply lights), "arch" (it comes down from the middle light of the arch, over `descent` seconds, default 2.5, and the first person reaches up for it) or a screen point (x, y).
- `start`: "center" (default), "left", "right" or a person index. `path`: "crowd" (default: every lit person passes it on to near neighbours who still wait, one after another, so it spreads out like a wave), "line" (a single chain along the crowd from the start side), or a list of screen points (the people nearest them, in order).
- `speed`: how fast the flame hops, in screen widths per second (default 0.15). `reach` (default 0.40 s): how long before the hop the hands reach out; `hold` (0.25 s): pause before a new receiver passes it on; `reach_far` (2.2): how far (in neighbour spacings) a hand-over may reach.
- Each hand-over: the giver turns toward the receiver (turning round if needed) and reaches out with one hand; the receiver reaches with both hands; the flame hops across with a spark trail; the receiver then holds it in cupped hands and begins to glow (the unlit crowd is dimmer). `color`: the flame colour.
- `lift` (default True, or a time): once all are lit, everyone lifts their light. Timing of the ending, all optional (defaults are the original numbers): `lift_spread` (0.9 s: how long the lifts are staggered over), `rise_delay` (1.0 s between a lift and its rise), `rise_spread` (1.4 s stagger of the rises), `rise_dur` (3.0 s: shortest flight to the arch). `rise` (default True): then each light rises to the nearest light of the arch. `arch` (default 1.0, 0 = off): the arch brightens as they arrive (a band of light through the nine lights). To also switch on the nine lights themselves, give PHRASES `star` times around then (the demo does).
- A 100 person crowd lit from the centre takes about 15 seconds to light completely at the default pace; the demo prints nothing, but `gathering.Crowd(...).Tend` gives the exact time.

## L. Water ripples and campaign symbols (2026-11-15, branch engine-water-symbols)

Code: `engine/water.py`, `engine/water_shaders.py`, `engine/symbols.py`, plus one guarded block in the composite pass (`shaders.COMP_FS`, `uNRip`). Demo: `engine/songs/demo_water_symbols.py`. A song that sets none of these keys renders exactly as before.

### Ripples: the lake responds

```python
RIPPLES = [(10.8, 0.50, 1.0), (11.6, 0.42, 0.7), (13.2, 0.50, 0.6, 0.15)]   # (t, x, strength) or (t, x, strength, y)
RIPPLES_AUTO = 1.0                                                          # number or Track, 0 = off
FALLING_STARS = [(9.2, 0.24), (15.0, 0.80, 0.18)]                          # (t lands, x) or (t, x, y)
```

- A ripple is a ring that spreads from where something touched the water, in perspective (small and flat near the far shore, wider near the bottom). It bends the lake and everything mirrored in it (plates with `water=True` and the engine's own lake), and adds soft rings of light. It lasts 5 seconds.
- `x`, `y` are screen fractions; `y` must be below the water line. Without `y` a ripple sits at `RIPPLE_Y` (default 0.78 of the water line height).
- `RIPPLES_AUTO`: petals (`PETALS`) landing on the lake, falling stars, and the feet of figures standing on the water (a figure whose `y` is at most 0.02 above the water line: one ripple as it gathers, one per step while it walks) add ripples. The value scales their strength. Every ripple is a pure function of t, so the cloud's video parts match.
- `FALLING_STARS`: a star streaks down from the sky and lands at `t` (drawn whether or not `RIPPLES_AUTO` is on; it ripples only when it is).
- Optional: `RIPPLE_COLOR` (default `"#ffe6c4"`), `RIPPLE_BRIGHT` (default 1.0), `RIPPLE_Y`, `RIPPLE_LINE` (override the water line; default: the active water plate's line, else `HORIZON`).
- BOTTOM_CALM softens ripple light and bending in the lower third; text protection keeps ripple light out of the letters.

### Campaign symbols drawn in light

```python
SYMBOLS = [
    dict(kind="emblem", t0=4.5, t1=10.5, out=14.0, x=0.50, y=0.53, size=0.36, leave="to_star", star=4),
    dict(kind="heart", t0=6.0, t1=10.0, out=13.5, x=0.17, y=0.62, size=0.15, leave="sparks"),
    dict(kind="bridge", t0=13.0, t1=18.0, out=28.5, x=0.50, y=0.36, size=0.20, stretch=1.6),
    dict(kind="gate", t0=18.0, t1=23.0, out=29.0, x=0.50, y=0.575, size=0.34, open=23.8, open_dur=2.6),
]
```

- `kind`: `"emblem"` (the Mother's Love and Peace Day emblem: two overlapping hearts, coral and orange, a sky blue globe with latitudes and longitudes, a green olive sprig), `"heart"` (one coral heart), `"gate"` (a gate or temple of light, Zion, drawn line by line from the steps up; its two doors then swing open and gold light pours out over the steps and the water), `"bridge"` (a bridge of light drawn left to right, about 4 times as wide as it is high).
- Shapes are procedural bezier paths (`engine/symbols.py`), drawn by a pen of light: each line appears as the pen passes, with a bright head.
- `t0` the pen starts, `t1` the symbol is complete (then it glows and breathes with a soft aura), `out` it leaves. `x`, `y` the centre (screen fractions), `size` its height (fraction of the screen height). `stretch` widens it (default 1.0).
- `leave="sparks"` (default): it dissolves into sparks that drift up. `leave="to_star", star=N`: it gathers and flies into light N of the arch (0 to 8) over `leave_dur` seconds (default 2.6); give that light's PHRASE a `star` time about 2.6 s after `out` so it lights as the symbol arrives.
- `color`: one hex colour for every line, or a dict by role (`coral`, `orange`, `sky`, `olive`, `gold`, `goldw`, `bridge`). Defaults: hearts `#F0566A` and `#F39A3A`, globe sky blue, olive green, gate gold. Every colour is lifted toward white so it always glows, never dark.
- `glow` (default 1.0) scales the brightness. `reflect` (default True): the symbol is mirrored in the lake, and the ripples bend that reflection. Gate only: `open` (time the doors start to open; default `t1 + 0.8`; `None` keeps them shut), `open_dur` (default 2.5), `light` (colour of the light through the doors, default `"#ffcf7a"`).
- Symbols are light drawn before the text protection pass, so they never cross the letters. Keep them clear of an expression's place on screen anyway.

## M. Creatures of light: doves, butterflies, fireflies (2026-11-15, branch engine-creatures)

Built 2026-11-15 (branch engine-creatures, code in `engine/creatures.py`). Demo: `engine/songs/demo_creatures.py` (36 seconds, song 03 recording). All three are light drawn before the text protection pass, so the words dim them like any other light, and they reflect in the lake. In the calm lower third (BOTTOM_CALM) they are dimmed, the fireflies thinned, and the flock steers up out of it.

Doves: a flock with separation, alignment and cohesion. Each dove beats its wings (a few beats, then a glide; climbing birds keep flapping), the wing tip lags the arm so the beat ripples outward, the body lifts on each downstroke, and the bird banks into its turns (it shows its back or belly and spreads its wings across the screen as it turns). Faint sparks fall from its path.

```python
DOVES = Track([(0, 0.0), (2.0, 0.0), (4.0, 1.0), (30.0, 1.0), (33.0, 0.0)])   # 0..1: share of the flock shown
DOVES_COUNT = 14                 # flock size (a constant), default 14
DOVES_FROM = (-0.04, 0.40)       # where the flock comes from when DOVES first rises above 0 (screen fractions)
DOVES_TARGET = 4                 # a star index of the arch, or a point (x, y), or a function of time; default (0.5, 0.8)
DOVES_PATH = [(0.0, (0.4, 0.6)), (8.0, (0.8, 0.75)), (14.0, STAR_POS[4])]   # or follow a moving goal (overrides TARGET)
DOVES_ORBIT = 0.14               # the flock wheels round the goal at about this radius; 0 = just chase it
DOVES_SIZE = 0.03                # body length as a fraction of the screen height (wingspan is about twice that)
DOVES_SPEED = 1.0                # speed multiplier (cruise is about 0.22 screen heights per second)
DOVES_COLOR = "#fff1da"          # also DOVES_SPARK_COLOR (default "#ffd9a0")
DOVES_TRAIL = 1.0                # spark trail strength, 0 = none
DOVES_BRIGHT = 1.0
```

Every key except DOVES_COUNT and DOVES_FROM may be a Track. The flock is simulated in fixed 1/60 s steps from the moment DOVES first rises above 0, with a fixed seed, so every still and every video part shows the same birds (a part that starts later replays the steps from the start, which takes well under a second per minute of flight). Changing any dove setting changes the flight from that moment on.

Butterflies: fast irregular flutter with short open-winged glides, a bobbing meander, and now and then a landing where they slowly fan their wings before taking off again.

```python
BUTTERFLIES = Track([(0, 0.0), (8.0, 0.0), (12.0, 1.0)])   # 0..1: share of them shown
BUTTERFLIES_COUNT = 4
BUTTERFLIES_COLOR = ("#ffd7ef", "#bfe3ff")    # forewing, hindwing (or one color)
BUTTERFLIES_SIZE = 0.022                      # wing length as a fraction of the screen height
BUTTERFLIES_AREA = (0.08, 0.92, 0.40, 0.68)   # x0, x1, y0, y1 where they meander
BUTTERFLIES_LAND = [(0.06, 0.335), (0.94, 0.34)]   # landing spots (default: the shore at both sides)
BUTTERFLIES_BRIGHT = 1.0
```

Fireflies: soft points that wander low and blink (a flash every few seconds, some flash twice, a faint glow between).

```python
FIREFLIES = Track([(0, 0.0), (20.0, 0.0), (26.0, 1.0)])   # 0..1: share of 160 fireflies shown
FIREFLIES_Y = (0.05, 0.40)       # the band they live in (default: from the bottom to just above the horizon)
FIREFLIES_COLOR = "#e4ff9c"
FIREFLIES_BRIGHT = 1.3
```

## N. Living nature: flowers, tree, blossoms, waterfall, stream (2026-11-15, branch engine-nature)

Living nature made of light, always moving (engine/nature.py, engine/nature_shaders.py). Each layer is switched on by its main setting (a number or a Track, 0 = off); a song that sets none of them renders exactly as before. All of it is drawn as light before the text protection, so the veil behind the words dims it like every other light, and all of it honours `BOTTOM_CALM` (the stream, the waterfall's mist and the tree's trunk are softened in the lower third, not removed; flowers there stay soft and the bottom-centre is kept clear). Working example: `engine/songs/demo_nature.py` (30 seconds, a dawn).

| Setting | What it draws | Extra settings (defaults) |
|---|---|---|
| `FLOWERS` | a field of flowers of light: as the value goes 0 to 1 the stems rise, buds form and the petals unfurl, in a wave that travels across the field; stems, leaves and heads sway in the wind and the petals breathe | `FLOWERS_LINE` (0.34: the far edge of the field, a fraction of the height from the bottom), `FLOWERS_DEPTH` (0.16: how far the field reaches down toward the viewer), `FLOWERS_COLOR` (a list; default cream, peach, coral, sky blue, soft peach), `FLOWERS_WAVE` (0.0: the x where the blooming starts; 0.5 blooms from the centre outward, 1.0 from the right), `FLOWERS_COUNT` (64), `FLOWERS_SPAN` ((0.0, 1.0): the x range), `FLOWERS_BRIGHT` (1.0), `FLOWERS_SEED` (5) |
| `TREE` | one tree of light with procedural branches: a bright thin core and a soft halo per branch, fresh green-gold leaves that flutter and catch the light, and layered wind (a slow gust that reaches the outer branches later, a sway per branch and a flutter in the twigs). The value is its brightness | `TREE_GROW` (1.0; a Track from 0 to 1 grows it from a seed: the growth front travels out along every branch with glowing buds at the tips, the leaves come last), `TREE_X` (0.80: the trunk's foot), `TREE_Y` (0.30: the ground under it), `TREE_HEIGHT` (0.52), `TREE_COLOR` ("#ffdcaa"), `TREE_BRIGHT` (1.0), `TREE_SEED` (21: a balanced crown with no long low arm; a different number grows a different tree), `TREE_DEPTH` (7), `TREE_LEAVES` (1100) |
| `BLOSSOM` | blossoms open on the tree's twigs (0 to 1, staggered); from about 0.35 petals start to fall, tumbling and carried on the wind, and fade before the ground | `BLOSSOM_COLOR` (blush, peach, cream, coral), `BLOSSOM_COUNT` (150), `BLOSSOM_PETALS` (260) |
| `WATERFALL` | falling light-water: streaks that pour and speed up, a bright lip, droplets, foam, splashes and rising mist at the foot; as the value rises from 0 the water pours in from the top | `WATERFALL_X` (0.20), `WATERFALL_TOP` (0.62), `WATERFALL_BOTTOM` (0.375), `WATERFALL_WIDTH` (0.040), `WATERFALL_COLOR` (["#bfe3ff", "#fff4e0"]) |
| `STREAM` | a flowing stream of light along a winding path: a soft body, shimmering banks and glints carried downstream (faster in the middle); as the value rises from 0 the light flows in along the path | `STREAM_PATH` (a list of (x, y) points from the source to the lake; a smooth curve is drawn through them; it widens toward the end), `STREAM_WIDTH` (0.010), `STREAM_SPEED` (1.0), `STREAM_COLOR` (["#9fd0ff", "#fff1d6"]) |
| `WIND` | shared by all of the above: a steady push plus gusts that roll across the screen from left to right | default 0.35; 0 is still air (the flowers and branches still breathe), 0.7 a strong gust |

```python
WIND = Track([(0, 0.25), (17, 0.70), (22, 0.45), (TOTAL, 0.35)])
TREE = 1.0
TREE_GROW = Track([(0, 0.0), (1.0, 0.0), (13.0, 1.0)])
TREE_X, TREE_Y, TREE_HEIGHT = 0.82, 0.335, 0.44
BLOSSOM = Track([(0, 0.0), (12.0, 0.0), (19.0, 1.0)])
FLOWERS = Track([(0, 0.0), (4.0, 0.0), (18.0, 1.0)])
FLOWERS_LINE = 0.36
WATERFALL = Track([(0, 0.0), (0.5, 0.0), (4.5, 1.0)])
WATERFALL_X, WATERFALL_TOP, WATERFALL_BOTTOM = 0.17, 0.66, 0.40
STREAM = Track([(0, 0.0), (3.0, 0.0), (9.0, 1.0)])
STREAM_PATH = [(0.17, 0.40), (0.25, 0.385), (0.21, 0.365), (0.31, 0.348), (0.40, 0.334), (0.47, 0.312)]
```

Tips: keep the tree and the waterfall to the sides, clear of the expression (centre, about 0.61 from the bottom) and the arch. Start a stream at the foot of a waterfall by giving them the same point. Remember DESIGN-SYSTEM.md section 6: agree with the coordinator before two songs use the same signature effect.

Paint (round 2): light alone only brightens a bright sky, so the flowers' petals, the stream's water and a cliff behind the waterfall are also painted in colour over the scene (a half-size paint buffer that the composite lays down before the light, never over the text, and only while one of these layers is on). Flowers are drawn as real petal shapes in saturated campaign colours (coral, peach, cream, sky blue) with a rim of light; the stream is one continuous ribbon of water with flowing bands, glints moving downstream and banks that catch the light. Extra settings: `WATERFALL_CLIFF` (1.0: strength of the rock face of light and shadow behind the fall; 0 turns it off), `CLIFF_LIT` ("#c9a3a4"), `CLIFF_SHADE` ("#5d6690"), `STREAM_PAINT` ("#7fb2e0": the water's colour), `NATURE_PAINT` (1.0: strength of all the paint).

## O. Sky and camera (2026-11-15, branch engine-sky-camera)

Time of day, moving 3D clouds, god rays and slow camera moves with depth. All optional: a song that sets none of these keys renders exactly as before. Code: `engine/sky_camera.py` and `engine/sky_camera_shaders.py`. Working example: `engine/songs/demo_sky_camera.py` (30 seconds, night to dawn, god rays through clouds, a slow crane up).

```python
from track import Track
TIME_OF_DAY = Track([(0.0, 0.02), (20.0, 0.48), (30.0, 0.66)])   # night to just after dawn
CLOUDS3D = 0.8            # cover, 0 = off
CLOUDS_SPEED = 1.6        # drift and change of shape (1 = gentle)
CLOUDS_LIGHT = 1.1        # how strongly the sun lights them (and their silver linings)
GOD_RAYS = Track([(0.0, 0.0), (9.0, 0.0), (19.0, 0.85)])
RAYS_FROM = "sun"         # or a point in the sky, (x, y) in screen fractions
RAYS_COLOR = "#ffe6c0"    # default: the colour of the light at that time of day
RAYS_DECAY = 0.985        # how far the shafts reach: 0.95 short, 0.995 long (default 0.985)
CAMERA_CRANE = Track([(0.0, -0.03), (30.0, 0.09)])   # + rises: the land sinks, more sky
CAMERA_ZOOM = Track([(0.0, 1.0), (30.0, 1.07)])      # > 1 pushes in
CAMERA_PAN = Track([(0.0, -0.015), (30.0, 0.02)])    # + moves right: the land slides left
PARALLAX = 1.0            # 1 = full depth, 0 = everything moves as one flat picture
CAMERA_MOTES = 0.6        # a few large soft motes on the nearest layer, so the depth reads
```

- **TIME_OF_DAY** (number or Track): 0 night, 0.3 before dawn, 0.5 dawn (sun on the horizon), 0.7 sunrise, 1 day, 1.25 golden hour, 1.5 dusk (sun on the horizon), 1.75 late dusk, 2 night again. It replaces the song's sky colours, glow (the colour of the light), sun height, sun strength and size and the stars, eased smoothly. The sun's strength still breathes with the music. Leave it out to keep the song's own palette.
- **CLOUDS3D**: two layers of soft clouds on a sky plane in perspective (small and many near the horizon, large overhead). They drift with the wind and keep changing shape; never frozen. The side facing the sun is lit with the glow colour, and thin edges near a low sun get silver linings (strongest at dawn and dusk). A cloud is never much darker than the sky behind it, and clouds thin out round any text (expressions, title, end card, fragments, credit), so no dark shape sits behind words. With `TEXT_SHADOW = 0` (nothing dark behind any text) the clouds are not thinned: a hole in bright clouds would itself read as a darker patch behind the words (`CLOUDS_TEXT_CLEAR`, 0 to 0.9, sets the thinning by hand). They are reflected in the lake. The old flat `CLOUDS` of the song is turned mostly down while CLOUDS3D is on.
- **GOD_RAYS** (0 = off): shafts of light from the sun, or from `RAYS_FROM`, scattered in screen space. The moving clouds and the three mountain ranges block the light, so the shafts move with the clouds. They are drawn as light (nothing dark), fade below the horizon, follow BOTTOM_CALM and are dimmed behind words by the text protection like every other light. With `TEXT_SHADOW = 0` they are not dimmed behind the words: the shafts are a haze over the whole sky, and a hole in it would read as a darker patch behind the text. A sun below the horizon (night) gives no rays.
- **CAMERA_ZOOM, CAMERA_PAN, CAMERA_CRANE** (numbers or Tracks; any one of them turns the camera on), **PARALLAX** (default 1), **CAMERA_CENTER** (default `(0.5, HORIZON + 0.12)`, the point a push in goes towards). Depths: far sky 0.12, high clouds 0.24, low clouds 0.40, far range 0.45, middle range 0.62, near range 0.80, lake 0.80 at the shore to 1.15 at the bottom of the screen, near motes 1.45. The skyline lantern rides the far range. Good ranges for slow, calm moves: zoom 1.0 to 1.15, pan within plus or minus 0.05, crane within plus or minus 0.12, over 20 seconds or more.
- **Moved by the camera** (engine-epic): everything that stands in the world follows the scenery of its depth, so feet stay on their ground and nothing slides. A point is given exactly as without a camera (where it would be with the camera at rest) and the engine moves it.

  | Layer | Depth it moves at | Override |
  |---|---|---|
  | Stars | the sky, 0.12 | |
  | People of light, painted and rigged (FIGURES) | the ground under the feet: 0.80 on the far shore and above, up to 1.15 at the bottom of the lake | `depth=` in the entry |
  | The gathering crowd, its flames | the ground under its feet line (`center` y) | `depth=` in GATHERING |
  | Doves, butterflies, fireflies | 0.80 | `CREATURES_DEPTH` |
  | Tree, blossom, flowers, waterfall, stream (light and paint) | the ground at `TREE_Y`, else at `FLOWERS_LINE`, else the far shore | `NATURE_DEPTH` |
  | Symbols and their reflections | 0.80 | `depth=` in the entry |
  | Ripples and falling stars | the lake under each one | |

  Flights to the arch (a figure's sparks, a symbol, the crowd's lights, the flame from the arch) still land exactly on their light.
- **Not moved by the camera**: text of any kind, the arch of nine lights, and the drifting air layers (the song's motes, lanterns and petals, SNOW, BUBBLES, LEAVES, the beat sparkles). The effect layers that are painted in the composite or fill the frame (ICE, SHARDS, GOLDEN_FIELD, NET) are not moved either: do not combine them with a camera move. A BEAM keeps its top where the song puts it and its foot (`BEAM_TO`) on its spot of the ground.
- `CAMERA_FOLLOW = 0` (default 1; a Track can ease it) lets the layers go: the scenery still moves, the layers stay where the song file puts them.
- Plan the move so the far shore stays out of the calm lower third. A crane up or a push in moves the ground down the screen: with the default centre, zoom 1.06 and crane 0 put a shore at 0.343 on 0.337; crane +0.05 and zoom 1.09 would put it on 0.29. Start with a negative crane (the land a little high) and end at 0.
- The camera's picture is the same world as without a camera, including the day sky of `SKY_THEME` (section I).
- The camera moves the engine's own sky, ranges and lake. A scene plate (SCENES) keeps its own `zoom` and `pan` and covers the camera background while it is on screen; the camera lets the layers go as a plate comes in, so the people stay on the painted ground.
- For a new layer: wrap its vertex shader with `sky_camera.cam_vs(...)` and set the uniform `uCamAff` to `R.sky.aff(depth)` before drawing (`R.sky.ground_depth(y)` gives the depth of the ground; `R.sky.place(p, depth)` and `R.sky.unplace(p, depth)` move single points). In a song without a camera the shader is untouched.

## P. Music reactivity and automatic timing (2026-11-15, branch engine-audio)

The engine analyses the song's audio once, when it loads (numpy and an ffmpeg decode, in `engine/audio_react.py`): a slow loudness envelope, onsets and beats (a fast pulse is counted in half time, so a ballad pulses at about 70 to 90 bpm), downbeats, a spectral brightness and section starts from a novelty curve. The results are cached as arrays on a 100 per second grid (and on disk under `work/audio_react/`). The audio is the Render workflow's `audio` input; locally set the environment variable `AUDIO`, or `AUDIO_FILE = "audio/promo/sNN.mp3"` in the song file.

Song keys (all optional, all off by default; each a number 0 to 1 or a Track):

| Key | What it does |
|---|---|
| `AUDIO_REACT` | Master amount for all of the keys below. Defaults to 1 once any REACT_* key is set; 0 turns everything off. |
| `REACT_GLOW` | The sky glow and the rays swell with loudness. |
| `REACT_SPARKLE` | Small warm sparkles breathe on each beat (above the calm lower third, and kept out of the letters by text protection); a few more motes on the beat. |
| `REACT_ARCH` | The lit lights of the arch pulse gently on the beat (unlit lights stay dark). |
| `REACT_AURORA` | The aurora, the Milky Way and the upper sky follow loudness (and a little brightness). |
| `REACT_CHORUS` | A bigger bloom (and a little more glow) in the loud sections, crossfaded over about 1.5 s. |

Taste is built in: the loudness follower is slow (0.5 s up, 1.6 s down), each beat pulse rises over 0.07 s and decays over 0.45 s, quiet beats are small, and no reaction lifts anything by more than 25 percent. The reaction only ever adds light: the designed look is the floor in quiet passages. A song that sets none of these keys renders exactly as before.

```python
AUDIO_REACT = 1.0
REACT_GLOW = 0.8
REACT_AURORA = 1.0
REACT_ARCH = Track([(0, 0.0), (14, 0.0), (16, 1.0)])   # pulse only once the first light is lit
REACT_CHORUS = 1.0
```

Helpers for timelines (any song setting that is a function of time):

```python
from audio_react import audio
RAYS = lambda t: _rays(t) + 0.3 * audio.chorus(t)
audio.level(t)        # slow loudness, 0..1
audio.beat(t)         # smooth beat pulse, 0..1
audio.brightness(t)   # spectral brightness, 0..1
audio.chorus(t)       # how loud the current section is, 0..1
audio.section_starts(), audio.beats(), audio.downbeats(), audio.strong_beats(), audio.tempo
```

When a song file changes a setting of a base song it imports (as `engine/songs/demo_audio.py` does with `s03_original`), set it on the base module, because the base's `params()` reads its own globals.

Automatic timing: `python tools/suggest_timing.py audio/promo/sNN.mp3 -n 4 --start 6 --end 46` prints the section starts, the strong beats, and form, hold, out (dissolve end) and star times for 4 expressions. It always honours the reading time contract (formation 3.75 s, then at least 6 s solid, so hold >= form + 9.75; dissolve 1.6 s; 0.5 s gap before the next text), spreads the expressions evenly, places hold on section starts and strong beats where it can, starts each form on the first strong beat after the gap, and lights each star on a strong beat about 3 s after hold. `--solid 8` asks for longer reading time; `--json` gives machine readable output. Treat it as a first draft: the lyrics and the scenes still decide.

Demo: `engine/songs/demo_audio.py` (the original song 03 look over the first minute of the recording, every key at full amount).

## Q. Output: 4K, 60 fps, pre-show loop, live cue mode (2026-11-15, branch engine-output)

### 4K and 60 fps

Two new choices on the Render workflow, for any song file (nothing to change in the song):

- `resolution`: `1080p` (the default) or `4k` (3840x2160). The song keeps its 1920x1080 design: positions, text sizes and the glow look the same, only sharper. 4K video runs with twice as many parallel parts. The words are drawn at 4K too (text.py multiplies its 1080p sizes and distances by 2), so they are as sharp as the scenery; at 1080p the text is exactly as before.
- `fps`: `30` (the default) or `60`. Everything the engine draws is a function of the time in seconds, so 60 fps is the same motion, twice as smooth. 60 fps video also runs with twice as many parts (4K at 60 fps: four times, at most 40).
- The share copy is always 1280x720 at 30 fps and under 25 MB.

```
gh workflow run render.yml --ref <branch> -f song=s03_original -f audio=audio/test/s03-newsong-first-60s.mp3 \
  -f mode=video -f name="s03 4k60" -f resolution=4k -f fps=60
```

A song file that does its own frame maths should read `FPS` and `NFRAMES` at call time (as every song's `Song` and `params` already do), never copy them into other numbers when the file loads.

### Pre-show and intermission loop

A song file with `LOOP_SECONDS` is a seamless loop: the video is exactly that long and its first frame is the frame that would come after its last, so a player set to repeat shows no seam. Keys:

- `LOOP_SECONDS = 120.0`: the loop length (for example 120 or 300). `TOTAL` and `NFRAMES` follow it.
- `LOOP_XFADE = 6.0` (optional): the first seconds of the loop fade from the picture one loop later into the picture now. This hides what still drifts (cloud noise, twinkles, motes) at the seam. Keep the song's own settings periodic so the fade has nothing to hide but drift: use `from output import loop_wave` and `loop_wave(t, LOOP_SECONDS, cycles, phase)`, a sine that repeats a whole number of times per loop, and wrap `t % LOOP_SECONDS` in `params()`. Avoid anything that only grows (the skyline lantern, a trail that advances, one-off waves, figures that walk in).
- `EVENT_CARD = dict(lines=[...], ...)`: a calm card in the middle band, protected like every other text. `lines`: campaign title (drawn in small spaced capitals), concert title (large serif), then the date and time, then the place (italic). Optional: `t_show` and `t_hide` (seconds into the loop it fades in and out; None means always on), `fade` (2.0 s), `y` (centre from the top, default 0.40, stays above the lower third), `sizes` (default (34, 104, 54, 44) px; long lines shrink to fit), `alpha` (0.95), `color`, `glow`, `breathe` (True: a slow breath of the glow, whole cycles per loop). The card works in any song file, not only loops.
- No music is needed: the workflow lays an exact-length silent track under a loop video. Pass any audio file in the repo (for example `audio/test/silent-60s.mp3`); it is only measured.
- The video run checks the seam: the finish job log prints the difference (PSNR) between the last and the first frame next to the difference between the first two frames; the two should be close. `loop_first.png` and `loop_last.png` are in the "<name> frames" artifact.

Example: engine/songs/demo_loop.py (two minutes, the luminous original look in the campaign colours, no light on the arch yet).

```python
from output import loop_wave
LOOP_SECONDS = 120.0
EVENT_CARD = dict(lines=["The Words of Mother’s Love That Bring Peace",
                         "The Words of Mother’s Love Healing Concert",
                         "Sunday, December 6 · 4:30 PM",
                         "The World Mission Society Church of God · 6720 W Sahara Ave, Las Vegas"])
```

### Live cue mode

`engine/live.py` plays a song file in real time, fullscreen, so the picture can follow the live performance cue by cue. It needs a computer with a graphics card (the cloud render is far too slow for real time). Running it at the venue is Anthony's decision; it has not been run on any computer yet.

Cues come from the song file: `CUES = [(name, start seconds, loop end seconds or None), ...]`, for example

```python
CUES = [("Opening", 0.0, None), ("Verse 1, hold", 12.0, 40.0), ("Chorus", 40.0, None), ("End card hold", 236.0, 250.0)]
```

A cue with a loop end holds: when it reaches the loop end it crossfades back to its own start and keeps doing so until the next cue. A cue without one plays on through the song (and holds the very last frame at the end). A song without `CUES` gets one cue from the start; a `LOOP_SECONDS` song loops forever.

How to start it, step by step:

1. On the venue computer, install Python 3.11 and ffmpeg, then, in a terminal inside the repository folder: `pip install numpy scipy librosa moderngl pillow fonttools brotli soundfile pygame`
2. Get the fonts once: run the commands of the "Fonts" step in .github/workflows/render.yml (they need Node's npm; they put the fonts in the `fonts` folder).
3. Start the song: `python engine/live.py s03_original --audio audio/promo/s03.mp3` (the audio file is measured once so the lights follow the song; there is no sound, the musicians play live). For a rehearsal in a window add `--windowed`; to fill the second screen (the projector) add `--display 1`.
4. Keys: space or right arrow for the next cue, left arrow for the previous one, 1 to 9 (and 0 for 10) to jump to a cue, b to fade to black and back, Esc to quit. Every jump is a 2 second crossfade (change it with `--xfade 3`). The window title and the terminal show the current cue.
5. The terminal prints the frames per second every 300 frames. Below about 30, use a stronger graphics card, or a song with fewer effects.

## R. Draft mode and the automatic quality check (2026-11-15, branch engine-qa)

**Draft mode** renders the whole song fast, to judge timing, layout and motion before a full render. It is not for showing anyone.

- Run the Render workflow with `mode=draft` (same song, audio and name inputs). It renders 640x360 at 15 fps in 8 parallel parts, with half the particles, then joins them with the music.
- Artifacts: "<name> (draft)" holds "<name> (draft).mp4" (a few MB) and "<name> (draft contact sheet).jpg" (30 frames over the whole song, each labelled with its time); "<name> QA" holds the quality report.
- Engine: `engine/draft.py`. `DRAFT=1` in the environment is the flag; `import draft` then `draft.DRAFT` (true in a draft) and `draft.n(count)` (a particle count cut to the draft share, `DRAFT_PARTICLES`, default 0.5) let any layer draw less. Without any change in a layer, the draft already draws only that share of every particle buffer (stars, motes, lanterns, petals, words, figures, snow, fragment sparks and any new layer hung off the renderer), and every full-screen shader does a ninth of the work at 640x360. A layer whose buffer is in a meaningful order (a rigged figure's body parts, a symbol's strokes) keeps it whole with `draft_keep=True` in the dict that holds its vertex array. Normal renders are untouched.
- By hand: `cd engine && DRAFT=1 python draft.py --range 0 900 --out draft.mp4`, and `python draft.py --sheet draft.mp4 --out sheet.jpg`.

**Quality check** (`tools/qa_check.py`) runs on every stills run (report inside the stills artifact), at the end of every video run (on the share copy, artifact "<name> QA") and on every draft. It writes `qa-report.md` (plain words, a table of issues with HIGH, MEDIUM, LOW) and `qa.json`, adds the report to the run's summary page, and marks HIGH issues as errors and MEDIUM as warnings in the run. The workflow input `qa` is `flag` (default: report only), `fail` (the run fails on any HIGH issue, after the artifacts are saved) or `off`.

It uses the engine's own text layout (it imports the song file and engine/text.py), so it knows where every word sits and when it is fully formed. What it checks:

- Dark behind text: the sky in a ring 30 to 130 px round the letters against the sky 140 to 260 px out, in the same rows, open sky only (above the ridge), using the darker quarter of each ring so stars do not count. Under 0.85 is MEDIUM, under 0.70 HIGH (tuned: the v4 songs 04 and 07 measure 0.88 or more; the song 08 end card veil measures 0.60).
- Legibility: the letters against the brightest tenth of the light round them; under 2.2 is MEDIUM, under 1.6 HIGH.
- Reading time (from the song file): each expression fully formed (form + FORM_DUR + 0.75 s) for at least 6 s; fragments 3 s; no fragment over an expression; a 0.5 s gap between texts.
- End card: three lines under the title, whole for at least 4 s before the fade.
- Calm bottom third: frame differences in the bottom third against the rest, per 2 s (people of light left out).
- Static figures: a painted figure with one picture and no warp that moves across the screen is HIGH (it slides as one rigid picture); living figures (kind="rig") and warped ones (warp=True) are never called rigid. Frames inside each figure's box confirm it moves; a still painted figure frozen for 4 s or more is MEDIUM. Checked on the living figures test (run 43692681296): no rigid flags; the rigid walker of song 04 and the swan of song 08 are flagged.
- Coloured words (`color=`, section I): legibility is measured either way (light letters on a darker sky, dark letters on a bright one). The report names each text's colour and animation; dark letters that are hard to read are flagged with the reminder that they need a bright sky, and dark letters that measure lighter than the sky round them get a LOW note.
- The gathering crowd (section K) counts as people of light: it is left out of the calm check and is never called rigid. Figure boxes follow a camera move (section O) the way the engine moves the people.
- Dashes: no em or en dash in the song file or its status file (project-docs/status/NN.md).
- Length: the video is as long as the song file says.

By hand (repository root, fonts from tools/setup_fonts.py, ffmpeg): `python tools/qa_check.py --song s08_favor_from_god --video "<file>.mp4" --out qa` (or `--stills <folder>`, or neither for the song-file checks only). It takes under half a minute.

## S. Everything together (2026-11-15, branch engine-epic)

One engine holds every section above, and one song file can use them all. Test song: `engine/songs/demo_all.py` (30 seconds on audio/test/s03-newsong-first-60s.mp3): a rigged walker, Heavenly Mother from behind, a painted pair warped alive, a crowd that gathers and passes a flame, doves, a growing tree in blossom, clouds with god rays, one slow camera move, the emblem drawn over a rippling lake, bubbles and leaves on the campaign day sky, coral and navy words with text animations, and music reactivity. It is a test, not a design: a real film gives each moment one hero image.

**Song keys by feature**

| Feature | Keys | Section |
|---|---|---|
| Scenes | `SCENES` | A |
| People of light, painted | `FIGURES` (poses, `warp=`) | B, G, H2 |
| People of light, rigged | `FIGURES` with `kind="rig"`, `preset`, `actions` | H1 |
| Effect layers | `SNOW`, `ICE`, `SHARDS`, `SHARDS_MEND`, `GOLDEN_FIELD`, `NET`, `BEAM`, `FLASH` | C |
| Fragment styles | `FRAGMENTS` with `style=` | D |
| Text protection, calm third, end card | `TEXT_PROTECT`, `TEXT_SHADOW`, `BOTTOM_CALM`, `RINGS_AT_START`, three-line `TAGLINE` | E |
| Theme | `theme.campaign_day(...)`, `SKY_THEME`, `color=`, `glow=`, `GLOW_COLOR`, `GLOW_STRENGTH`, `BUBBLES`, `LEAVES` | I |
| Text animations | `anim=` on PHRASES, TITLE, TAGLINE, FRAGMENTS; `TEXT_ANIM` | J |
| Gathering | `GATHERING`, `PASS_LIGHT` | K |
| Water and symbols | `RIPPLES`, `RIPPLES_AUTO`, `FALLING_STARS`, `SYMBOLS` | L |
| Creatures | `DOVES`, `BUTTERFLIES`, `FIREFLIES` (and their `_COUNT`, `_PATH`, `_COLOR` ...) | M |
| Nature | `TREE`, `TREE_GROW`, `BLOSSOM`, `FLOWERS`, `WATERFALL`, `STREAM`, `WIND` | N |
| Sky | `TIME_OF_DAY`, `CLOUDS3D`, `GOD_RAYS`, `RAYS_FROM` | O |
| Camera | `CAMERA_ZOOM`, `CAMERA_PAN`, `CAMERA_CRANE`, `PARALLAX`, `CAMERA_CENTER`, `CAMERA_MOTES`, `CAMERA_FOLLOW`, depths | O |
| Music reactivity | `AUDIO_REACT`, `REACT_GLOW`, `REACT_SPARKLE`, `REACT_ARCH`, `REACT_AURORA`, `REACT_CHORUS`; `audio.level(t)` ... | P |
| Output | workflow inputs `resolution`, `fps`; `LOOP_SECONDS`, `EVENT_CARD`; `engine/live.py` | Q |
| Draft and quality check | workflow `mode=draft`, input `qa` | R |
| The silk look for people of light | `FIGURE_LOOK`, `FIGURE_SILK`, `look="silk"` on a rigged figure or on `GATHERING` | H5 |
| The 3D layer (camera in space, point sets, world with a mirror lake) | `P3D` | V |

**Order of drawing** (render.py, one frame): sky, 3D clouds; then light: stars, motes, lanterns, petals, effect layers (snow, bubbles, leaves, beam, net), nature, creatures, beat sparkles, people of light, the crowd, ripple light, falling stars and symbols, god rays and near motes; then the text protection dims all of that behind the words; then the words, the credit and the arch; glow; the camera background; the composite (plates, ripples bending the lake, ice, shards, field, nature paint, leaf tint, coloured letters).

**What stays exactly as before.** A song file that uses none of the new keys renders bit for bit as on main: `s03_original` on its promo clip was compared pixel by pixel at 25 and 45 seconds, and `s03_lake_of_memory` (scenes, painted figures, fragment styles) at 3.2, 14.5 and 42 seconds. For that, each optional block of the composite shader (`SKY_THEME`, `TEXT_SHADOW` below 0.05, per-text colour, leaf tint, lake ripples, nature paint, camera background) is compiled in only for a song that uses it (`render.comp_blocks()`, `shaders.comp_fs()`). When you add a block to the composite, add it the same way: the same maths written with a uniform in place of a constant is rounded differently by the shader compiler, which changes a few pixels by one level. When you compare stills pixel by pixel, run each side at least twice: the cloud machines are not all alike, and about one run in three of the very same commit (on main too) differs from the others in about 3 pixels by one level.

**Texture units of the composite**: 0 to 9 the engine's own (sky, light, four glow levels, ridge, text A, text B, credit), 10 and 11 scene plates, 12 leaf tint, 13 nature paint, 14 the figure layer of the silk look (H5), 15 the camera background, 16 a symbol's paint (section U). Every other pass binds its own textures from unit 0 just before it draws.

**Working together, in short**
- With `TIME_OF_DAY` the sky colours come from it; music reactivity then swells them. Without it the song's own palette (or `theme.campaign_day`) stays.
- `GOD_RAYS` need the sun above the horizon and read best through `CLOUDS3D`.
- A camera move needs room: keep people near the far shore, and see section O for where the shore ends up.
- People, crowd and creatures are light: on a bright day sky they read weakly. Use them at night, dusk and dawn, or over a saturated blue; nature paint, leaf tint and coloured letters are the layers made for bright skies.
- A song file that builds on another one (as `demo_all` does on `test_living`) needs its own `params()` that hands the arch to the base file: see the top of `engine/songs/demo_all.py`.

## T. Rendering

Commit and push the song file and its assets (plates and figures are in the repo under `assets/`, so the cloud workflow has them), then run the Render workflow: a draft or stills first, then the video. See docs/HANDOFF.md.

The Render workflow's inputs (one workflow for everything, 8 inputs):

| Input | Values | Meaning |
|---|---|---|
| `song` | a file in engine/songs, without .py | the song file |
| `audio` | a path under audio/ | the clip the video follows |
| `mode` | `stills`, `video`, `draft` | stills at chosen seconds; the full video; or the whole song small and fast (section R) |
| `stills` | seconds, comma separated | which stills to draw (stills mode) |
| `name` | letters, digits, spaces, `_ . , ! ' -` | name of the output files (no parentheses) |
| `resolution` | `1080p` (default), `4k` | section Q |
| `fps` | `30` (default), `60` | section Q |
| `qa` | `flag` (default), `fail`, `off` | the automatic quality check (section R) |

A video renders in 10 parallel parts at 1080p and 30 fps, 20 parts at 4K or at 60 fps, 40 parts at 4K and 60 fps together. A draft always renders in 8 parts.

The video run's finish job uploads: "<name>" (the full video plus a silent copy), "<name> frames" (4 frame sheets of 8 frames each, for checking without downloading the video), "<name> (share)" (the file "<name> (share).mp4": 1280x720, 30 fps, H.264 with AAC sound, always under 25 MB, for phones and messages; the job fails if it would be larger) and "<name> QA" (the quality report). A stills run uploads "<name>-stills" (the stills and their quality report). A draft run uploads "<name> (draft)" and "<name> QA".

## U. Small optional keys added for the epic promo (2026-11-15, branch epic-promo)

Each is optional. A song file that sets none of them runs the same code as before. Working example: `engine/songs/epic_concert.py`.

- **`LAKE_STARS`** (a number or a Track, 0 = off, 1 = as bright as the stars above): the engine's own stars are drawn a second time, mirrored in the lake, so a night lake is a sea of stars. Code: `engine/lake_stars.py`, one guarded call in `render.py` right after the stars. BOTTOM_CALM dims the mirror in the lower third like every other light there, so a song that wants the mirror lowers BOTTOM_CALM for its night (BOTTOM_CALM may be a Track). With a camera move the mirror follows the lake.
- **`FALLING_STARS`** items may carry the star's own path: `(t lands, x, y, from x, from y, seconds, trail points)`. Without the last four numbers the star falls as before (a short steep fall of 1.1 s). A long diagonal streak: `(10.24, 0.50, 0.315, 0.04, 1.03, 2.6, 180)`.
- **`RIPPLES`** items may carry a fifth number, `(t, x, strength, y, spread)`: the ring spreads that many times as fast and fades as slowly as any other ring. A ring that starts near the far shore then reaches far across the lake toward the camera (try 4 to 5 with a strength of 1.5 to 2.2).
- **`GATHERING`**: `cluster=(2, 3)` makes the people stand in groups of that many with gaps between the groups; a group walks in at one pace and arrives together (`cluster_tight`, default 0.5: how close the people of a group stand). `side_delay=(left, right)`: seconds by which the people from that side come later (for example while a figure still stands on that side). `PASS_LIGHT`: `flame=1.7` makes every flame (coming down, held, passed, rising) that many times as large (default 1.0).
- **`TAGLINE["sizes"] = (first line, other lines)`**: the sizes of a three-line end card's lines in 1080p pixels (default 64 and 48). Larger lines need a higher title (`TITLE["y"]`, default 0.315 from the top) so that the last line still ends above the far shore.
- **`MOTE_SIZE = (smallest, largest)`**: the sizes of the song's floating motes in 1080p pixels (default 2.4 and 24).
- **A symbol's `stroke`, `mirror` and `halo`** (SYMBOLS entry, each default 1.0): `stroke` is the thickness of the drawn line (1.8 for a large emblem that has to carry a scene), `mirror` the strength of its mirror image in the lake, `halo` the strength of the soft glow round the line.
- **A symbol's `paint`** (SYMBOLS entry, default off): a line of light pales to pink or white on a blue sky whatever its colour, because light can only be added to the blue behind it (the epic promo's orange and coral hearts both read pink). `paint=1.0` also paints the lines in exactly their colour over the scene, under the light, so an orange line is orange on any sky. `paint_roles=("coral", "orange")` paints only the lines with those colour roles (default: all of them; the others stay pure light), `paint_light` (default 0.3) is the share of their own light the painted lines keep (more light is paler), `paint_width` (default 1.7) the width of the painted line against the line of light. The mirror image in the lake stays light alone, at its full strength (painted, it was heavier than the symbol above it). When the symbol leaves (`out`) the paint fades in `paint_out` seconds (default 0.9) and the lines fly as light. Code: `engine/water.py` (`_draw_symbol`), `SYM_PAINT_FS` in `water_shaders.py`, the composite block `SYMBOL_PAINT` (compiled in only for a song with a painted symbol; texture unit 16). The emblem's builder gives the left heart the role `coral` and the right one `orange`; the real emblem has the orange heart on the left, so a song swaps the two with `color=dict(coral="#F39A3A", orange="#F0566A")`.
- **`TITLE["label_size"]`** (default 32, in 1080p pixels): the size of the small label above the end card's title; its letter spacing grows with it.
- A note on section I: `glow=` in a PHRASES entry has no effect while the entry has `anim=` (`engine/text_anims.py` draws animated expressions with fixed colours); it works for expressions with the classic sparks and for fragments. When the automatic check calls an expression weak, look at what is bright near the letters in the still before changing the text: in the epic promo it was the sun's bloom under the second line, not the text's own glow.

## V. The 3D layer: camera, point sets, world (2026-11-15, branch engine-p3d)

**Changes for song files since a1262fe (helper CORE2).** Every old key keeps its meaning; these behave differently:
- A set with `window=True` (or a window name) is mirrored only inside its window's reflection; masked silhouettes are now mirrored in the lake (a dark body's reflection is dark).
- `Mask(soft=...)` below 3 is now honoured (it used to be raised to 3); below 2.5 the silhouettes of that frame are drawn at full size. The default soft=3 renders as before.
- Motion blur never reaches across a hard cut (blend 0) any more: the first frame after a cut is clean.
- The lake mirror of a set of 300 thousand points or more draws every second point (every third from 1.2 million), each brighter; a static set of 60 thousand or more is drawn in spatial cells. Same look, less work.
- Moving lines and ribbons now take motion blur (they were drawn sharp in whips and fast moves).
- The lake and the hill rings stand round the world's origin instead of round the camera. Near the origin the picture is as before; a camera hundreds of metres away now sees real parallax, and from high up the lake is a disc.
New keys (details below in "Added by CORE2"): a move's `whip=`, P3D `motion_samples` as a Track, P3D `sky_res`, world `lake=dict(field=...)`, `shore`, `keep_hue`, `split` with `toward=` a world point and `cover=`, `lights=[dict(..., rays=, size=)]`, `Mask("sky", sky="flat", color=...)`, `Mask(slot=...)`, `window="<masked set>"` (nested windows), segment `vel`.

A true 3D layer inside the engine: a camera that moves through space, point sprites with depth of field and bokeh, and a world with a mirror lake. One song key switches it on, `P3D = dict(...)`. A song without the key never loads the package (`engine/p3d/`) and renders exactly as before (checked: `t_short_test` and `epic_concert` give the same frames, byte for byte, with and without the hooks).

Working examples: `engine/songs/p3d_camera_test.py` (the camera test: one unbroken move of 28.5 s) and `engine/songs/test_p3d.py` (every part once: masks, a shaft, a light with rays, a burst, a whip, every kind of sprite, the 2D words on top).

**Conventions.** Metres, y up, right handed. The lake is the plane y = 0. The arch of nine lights stands over the origin in the plane z = 0 with its front toward +z; the default camera stands at positive z and looks toward negative z. Azimuth angles are degrees from +z toward +x. A person is about 1.7 m tall. Everything is a pure function of the time t (and the camera at t), so any part of a video renders the same frames in any order (checked).

```python
from track import Track
from p3d import Mask, StandIn
from p3d.camera import Rig, orbit, dolly, crane, fly, hold

def build(scene):
    scene.add("figure", StandIn(pos=(0, 0, 0)), mask=Mask("dark"))

P3D = dict(
    camera=Rig([...], blend=1.5, fov=45, aperture=0.06, handheld=0.3),
    world=dict(look=[(0, "night"), (20, "dawn", 4.0)], arch=dict(lit=[...]), lanterns=Track([...])),
    setup=build,                 # fills the scene with the song's own point sets
    bursts=[dict(t=8.0, strength=6.0)],
)
```

| P3D key | Meaning |
|---|---|
| `camera` | a `Rig` (or a list of moves): see Camera |
| `world` | the sky, light, air, water and the world's own dressing: see World |
| `setup` | a function `setup(scene)` that adds the song's point sets (`scene.add(name, pointset, ...)`) |
| `sets` | the same as a list of dicts with the arguments of `scene.add` |
| `bursts` | bursts of light, `[dict(t, strength=4, rise=0.25, fall=0.7, color="#fff3d6", at=None, radius=0.35)]`: the picture flares to white at `t` (from the world point `at`, or the middle of the screen) and clears again; cut the world and the camera inside it |
| `motion_blur` | shutter as a share of the frame time (default the rig's `shutter`, 0.4; 0 = off). Each sprite is drawn out along its path on screen during the shutter (a batch's `streak` scales it), and the background is smeared the same way |
| `motion_samples` | default 1. With n above 1 the point sets are drawn at n moments inside the shutter, each a share of the light (true motion blur by time sampling, n times the work of the light pass): for a hero whip or points that curve fast |
| `keep` | flat layers of the 2D sky to keep: any of `"stars", "motes", "lanterns", "petals", "arch", "skyline", "rings", "waves"` (default none: the 3D world replaces them) |
| `lod`, `bokeh_max` | speed and look of very large bokeh: the blur radius in 1080p pixels above which only a share of a set's points is drawn, each brighter (default 7); the largest blur radius as a share of the picture height (default 0.20) |

### Camera (`engine/p3d/camera.py`)

A `Rig` is a list of moves, each owning a stretch of time. Between two moves the rig blends from one into the next over `blend` seconds; both keep moving while it blends, so speed carries through and nothing jerks.

| Move | What it does |
|---|---|
| `orbit(center, radius, height, a0, a1, t0, t1, look=None)` | revolve round `center` from azimuth a0 to a1; `radius` and `height` are numbers or (start, end) pairs |
| `dolly(p0, p1, t0, t1, look="ahead")` | travel in a straight line; `look` is a point, a pair of points (the gaze travels), or `"ahead"` |
| `crane(pos, height, t0, t1, look)` | rise or sink from `pos` to a height |
| `fly([(t, pos, target), ...])` | a smooth curve through keys |
| `hold(pos, target, t0, t1, drift=(0, 0, 0))` | stand still (or float a little) |

Every move takes `fov`, `roll`, `focus`, `aperture` (a number, a (start, end) pair or a function of time), `ease` (`"linear"` default, `"smooth"`, `"in"`, `"out"`) and `blend` (the length of the blend INTO this move). The rig's own `fov`, `roll`, `focus`, `aperture` are the defaults, with `handheld` (a subtle drift, 0 to 1), `shutter` and `min_height` (the camera never goes under the water).

- `focus`: metres, `"target"` (default: the distance to what the camera looks at) or a world point. `aperture`: the lens opening in metres: 0 everything sharp, 0.05 a clear blur, 0.15 big dreamy bokeh. A point exactly on the focus plane is perfectly sharp.
- A whip: give the next move `blend=0.3` to `0.5`; the motion blur streaks the picture. A hard cut: `blend=0` (hide it in a burst).
- `python` check of a path before rendering: `rig.speed(t)` gives (metres per second, degrees per second). The camera test turns at 34 degrees a second in its orbit; much above 45 feels hurried on a big screen.
- Other layers can ask for the camera of the frame: `R.p3d.camera(t)` is a `CameraState` with `project(points)` (screen positions 0..1 and depths).

### World (`engine/p3d/world.py`)

`world=dict(look=..., <setting>=..., arch=..., ...)`. A look is a complete set of settings (sky colours, where the sun stands and its colour, stars, haze, mist, water, rays). Looks blend setting by setting, so a section change moves the sky, the light direction and the air together.

- `look`: a name, or `[(t, name), (t, name, blend seconds), ...]`: at each time the world changes to that look over `blend` seconds (default 1.5, centred on t; 0 is a cut). Built in: `night`, `dusk`, `predawn`, `dawn`, `sunrise`, `golden`, `day` (the campaign day colours of `engine/theme.py`), `cream`.
- `looks=dict(name=dict(base="night", sky_top="#...", sun_el=4, ...))`: your own looks.
- Any setting may also be given directly as a number, a colour, a Track or a function of time; it then replaces the look's value: `sun_az=lambda t: 180 + 3 * t`, `stars=Track([...])`.

| Setting | Meaning |
|---|---|
| `sky_top`, `sky_mid`, `sky_hor` | the sky from the zenith to the horizon |
| `sun_az`, `sun_el`, `sun_color`, `sun_int`, `sun_size`, `sun_disc`, `sun_glow` | the sun (or moon): azimuth and elevation in degrees, colour, strength (0 = none), disc radius in degrees, disc strength, width of the glow |
| `stars`, `milky` | the star dome (14000 stars, the brightest with a fine glint) and the Milky Way |
| `clouds`, `cloud_speed` | clouds (0..1), lit from the sun side, and their drift |
| `hills`, `hill_height`, `hill_color` | three rings of far hills right round the lake (0 hides them: the lake then runs to the horizon) |
| `haze`, `haze_color`, `mist`, `mist_height`, `mist_color` | the air: fading into the horizon, and ground mist over the water |
| `water`, `mirror`, `mirror_min`, `ripple` | the lake: its own colour, the strength of the mirror, the mirror when looking straight down, the restlessness of the surface (0 = a perfect mirror) |
| `rays` | rays from the sun past hills, clouds and silhouettes, fanning out in shafts |
| `dust`, `bokeh`, `dust_color`, `dust_color2` | fine dust round the camera and larger soft lights among it (the foreground bokeh) |
| `lanterns`, `floats`, `lantern_color`, `lantern_color2` | lanterns rising into the sky; small lights floating on the water |
| `exposure`, `bokeh_ring`, `bokeh_hex` | exposure; the look of out-of-focus discs (a brighter edge; 0 round to 1 hexagonal) |

World dressing (keys of `world`, beside the settings):

- `arch=dict(lit=[t1, ..., t9], span=22, height=13, z=0, colors=(...), bright=1.0)`: the arch of nine lights as a real arc in space (a half ellipse 22 m wide and 13 m high, a ghost of dust that glows where its lights are lit, sparks circling each light, lines between lit neighbours, all mirrored in the lake). `lit` gives each light's time (None: never, negative: lit from the start) or a function `t -> nine (brightness, age)` pairs; without `lit` the song's own PHRASES timing lights it, as it lights the flat arch. `True` gives the default arch. `p3d.world.arch_points()` gives the nine positions.
- `lantern_field=dict(count, center=(x, z), radius=(r0, r1), height, speed, size)`, `float_field=dict(count, center, radius, size)`, `dust_field=dict(n, n_bokeh, box, bokeh_box)`: where and how many.
- `shafts=[dict(base=(x, z), radius=1.5, top=40, spread=0.0, color="#cfe0ff", strength=1.0)]`: up to four shafts of light standing on the water (a soft column; `spread` widens it upward; `strength` and `base` may be functions of time). Drawn with its image in the lake and a pool of light at its foot.
- `light=dict(pos=(x, y, z), color, strength, size=0.6, rays=1.0)`: one light in the world whose rays fan out round whatever stands in front of it (put it behind a head: the masked body cuts the rays).
- `react=dict(beat=0.5, level=0.3)`: the music moves the world (dust, bokeh and the arch pulse on the beat; the sun and its rays swell with loudness). The audio helpers of section P work in any setting that is a function of time.

### Point sets (`engine/p3d/api.py`): the API for bodies, words and effects

A point set is any object with `sample(t)` returning a batch (a dict) or a list of batches. A batch: `pos (N, 3)` metres, `size` (diameter in metres), `color` (linear light, `p3d.lin("#hex")`), `alpha`, `kind`, and optionally `pos2`, `alpha2` (segments), `rot` (flakes, petals, birds), `emit` (HDR glints), `normal` (for `rim`), `seed`, `vel`; with the settings `twinkle`, `rim=(strength, power)`, `dof`, `fog`, `reflect`, `lod`, `backlight`, `streak`. The module's own text is the reference; `python engine/p3d/api.py` runs a self check without graphics. `p3d.normalize(batch)` checks a batch and names what is wrong.

| Kind | Drawn as |
|---|---|
| `soft` | a round soft point of light (out of focus: a bokeh disc) |
| `spark` | a bright core with a fine four-point glint that twinkles |
| `disc` | a flat dot with a crisp edge |
| `flake`, `petal` | a shard, a petal: turns in the picture (`rot[:, 0]`) and tumbles (`rot[:, 1]`), flashing as it faces the camera |
| `bird` | a small pair of beating wings |
| `line` | a segment from `pos` to `pos2` (plexus); never thinner than a hairline |
| `ribbon` | a soft band from `pos` to `pos2`, `alpha` to `alpha2` (trails, streams) |

`scene.add(name, pointset, reflect=True, depth_of_field=True, mask=None, fog=True, lod=True)`. A set may have `wants_camera = True` (then `sample(t, cam)` gets the `CameraState`), `static = True` (sampled once, kept on the graphics card), `dome = True` (positions are directions on the sky), and `gain(t)`.

- **Light is kept.** A point's light is the same whether it is sharp, spread by the lens, or drawn out by motion; a size is physical (metres), so a set looks the same at 1080p, 4K and in a draft.
- **Reading moments.** A point on the focus plane has no blur at all, and a point smaller than a pixel goes through a fixed small footprint whose light does not change as it crosses the pixel grid (measured: 0.003 percent over a slide of one pixel for 40000 points 0.2 px wide). Words made of tens of thousands of points therefore hold still. For words that must be sharp wherever the focus is, give their batch `dof=0` (and `fog=0`); both are amounts 0..1 that may change over time, so words can come out of bokeh, hold, and go back.
- **The mask pass.** `mask=Mask("dark")`: the set's silhouette dims the sky and every light behind it by depth, so the body is dark with whatever rim its own points give (and its far side is hidden by its near side). `mask=Mask("sky", sky="sunrise")` (or `"clouds"`, `"stars"`, `"day"`): the silhouette is a window onto a sky picture, a double exposure; `edge` adds a light rim. `Mask.grow` (metres) closes the cloud of points into a solid shape; `Mask.source` takes the shape from another point set (the whole body while the visible points disperse); `Mask.strength` may be a function of time. All "dark" sets share one mask and all "sky" sets another.
- `p3d.StandIn(pos, height, color, facing, look="glitter" | "rim")` is a placeholder figure of points for tests.

### Section changes: a new look and place every few seconds

```python
P3D = dict(
    camera=Rig([orbit(..., t0=0, t1=7.5), dolly(..., t0=7.5, t1=15.0, blend=0.0), hold(..., t0=15.0, t1=22.0, blend=0.4)]),
    world=dict(look=[(0, "night"), (7.5, "dawn", 0.0), (15.0, "day", 0.8)], sun_az=Track([(0, 180), (15, 180), (15.5, 140)])),
    bursts=[dict(t=7.5, strength=6.0, at=(0, 6, 0))],
)
```

At 7.5 s the picture flies into a burst of light; inside it the world cuts to dawn and the camera to its second set-up (`blend=0`). At 15 s the camera whips to the third set-up in 0.4 s with motion blur while the sky blends to day and the sun swings round.

### How it sits in the engine

- Frame order: `adjust` (after the song's params and the music reactivity), `draw` (in the light pass, before the effect layers: silhouette masks, then every set with its mirror image), `background` (before the composite: sky dome, hills, lake, mist, shafts, rays, masks, bursts). The 3D picture is the composite's background (texture unit 15, the camera background's unit: a song uses either the 2D camera of section O or P3D). The points are light in the engine's HDR light buffer, so the glow, the tone curve, the fade and the exposure treat them like every other light.
- The 2D text system works unchanged on top: expressions, fragments, end card, credit, text animations and per-text colour. Text protection dims the 3D lights behind the letters like any other light. On a bright 3D sky use `color=` and `TEXT_SHADOW = 0` as on any bright sky.
- The flat sky's stars, motes, lanterns, petals, arch, skyline light, rings and waves are switched off (see `keep`). Effect layers, creatures, nature, figures and symbols of the 2D engine still draw, flat, over the 3D picture: mix with care.
- Draft mode: the world's own sets draw half their points, a set of more than 30000 points draws every second point (twice as bright). The quality check runs as on any song (a camera that moves the whole picture will be called busy in the bottom third; a test without an end card is told so).
- Speed on the cloud machines at 1080p: the camera test 0.4 to 0.7 s a frame, the feature test (close bokeh, masks, rays) 0.9 s. Costs to know: very large bokeh over much of the screen, and many big soft points near the lens.

### Added for the ten films (same branch; working example `engine/songs/test_p3d_ten.py`)

State of proof: every item below runs in `test_p3d_ten.py` and has been viewed as full-size stills (1.5 to 14.5 s, helper CORE2) with the local render script; the free camera's righting was checked in numbers (upside down at 6.6 s, level again by 8 s). The looks reference is `engine/songs/test_p3d_looks.py` (eight looks, two seconds each).

**Camera** (`engine/p3d/camera.py`, the module text lists every setting)

- `pace=`: the speed of a move from the music: a list of (time, progress) keys or a function of time. Steep keys are fast, flat keys slow: `pace=[(7.5, 0.0), (8.0, 0.45), (12.0, 0.6), (15.0, 1.0)]` dives on the cut at 7.5 s, drifts through a breath, and finishes by 15 s. Works on every move (for `fly` it says when the camera is where along the curve). `ease="out"` still eases into a still reading set-up; `blend` sets how fast one move takes over from the last (0.3 to 0.5 a whip, 0 a cut).
- `Rig(free=True)`: the camera carries its own up along its path, so loops and looks straight up or down never flip. It rights itself toward the world's up while near level (`right`, default 3 per second; 0 never) and starts level after a hard cut. A move's own `up=` (a vector or a function of time) holds any attitude, for example a long upside down ride. `roll` may be a Track running past 360 degrees (a barrel roll).
- `Rig(shake=...)`: a number, Track or function of time: a hard fast shake. `handheld` stays the slow drift.
- `Rig(parent=Frame(...))`: the whole rig rides a moving frame. `near=` (rig or move): the nearest distance drawn, down to 0.02 m for macro shots. `focus` and `aperture` take Tracks (rack focus).
- `dolly(..., keep_width=W)`: a dolly zoom: the field of view follows the distance so a subject W metres wide keeps its size. `orbit` takes `center` and `look` as functions of time (revolve round someone who moves).
- A sprite that would fill much of the picture (a point right at the lens) fades away instead, so the camera can pass through a dense sheet of points.

**Points, lines and ribbons** (`engine/p3d/api.py`)

- `birth` (N,) with the settings `fade` and `flash`: each point appears at its own time (and can flare as it does). It runs on the graphics card, so it works on `static` sets: a million points can light up in any order without resending them.
- Ribbons are continuous: `ribbon(points, width, color, alpha, **settings)` builds one band from a line of points (widths and alphas per point taper it); `Trail(path, length, width, color, ...)` is a ribbon that follows a moving point (a comet, a stream from a hand). Segments take `size2` (the width at the far end) and `u`, `u2` (the place along the path); `pulse=(speed, length, gain, period)` sends a brighter stretch along `u` (lines and ribbons). Lines and ribbons take the lens blur and are cut cleanly where they pass the camera.
- `paint` (0..1) with `paint_light`: the batch is also painted in its true colour over the scene, under its own light, so a coral petal is coral on a day sky (give the colour with `p3d.show("#f0566a")`). Painted points are drawn over each other in batch order, without sorting; their mirror images are painted too.
- `lit` (0..1): the points take the colour of the world's moving lights (with `normal`, only the side turned toward a light).
- `P3D["clear"] = [dict(box=(x0, y0, x1, y1), t0, t1, soft=0.03, amount=1.0)]` (screen fractions, y up; up to two; the list may be a function of time): no sprite and no paint falls inside the box. A batch with `clear=False` is let in (the words the box was made for).
- `Frame(origin, yaw | basis, scale, parent)` and `Parented(pointset, frame)`: a point set rides a frame that travels, turns and grows.

**Windows onto another world**

- `Mask("sky", sky="world", look="day")`: the silhouette shows the same world on the same camera in another look (its own sky, sun, hills and lake; `look` is a name, a dict `dict(base=..., <settings>)`, or a function of time). `scene.add(name, set, window=True)`: the set lives inside the windows and is drawn only where a "sky" silhouette is. One window world per frame, not nested.

**World** (`engine/p3d/world.py`)

- `split=dict(look=..., toward=azimuth, soft=0.35, amount=1.0)`: a sky of two looks, the other look on the half of the dome toward that azimuth (sky colours, haze, hills and the stars' brightness), with a soft seam: night ahead, dawn behind. `toward` and `amount` may be functions of time. The sun and the lake's own colour stay those of the main look.
- `calm=[dict(center=(x, z), radius, soft, ripple=0.0, mirror=1.0)]` (up to four; values or the whole list may be functions of time): discs of the lake with their own ripple and mirror, for glass inside a storm or the other way round. The world's `ripple` and `mirror` hold everywhere else.
- `lights=[dict(pos, color, strength=1.0, radius=3.0)]` (up to four, values or functions of time): moving coloured lights that glow in the mist, lay a pool on the water and colour `lit` batches. The single `light=` with rays (which a masked body eclipses) is unchanged.
- `star_turn` (degrees, a setting like any other) turns the star dome about `star_pole=(azimuth, elevation)`. `hills=0` removes the hills (the lake and its mirror then run to the horizon).
- The arch: `center`, `yaw`, `span`, `height` and `line` may be functions of time; `colors` may be nine colours, one for each light; `line` (0..1) draws the arc and the links separately from the lights; `travel=dict(start=point or nine points, t=nine arrival times, dur=1.4)` makes the lights fly to their places. A song file reads the geometry with `Arch(None, **settings).positions(t)` (the nine lights now), `.homes(t)` (their places) and `.point(u, t)`, or `arch_points(span, height, z, center=, yaw=)`.
- The sky now reaches its upper colours lower down (a level camera sees the blue of a day sky); the looks `golden`, `day` and `cream` were retuned for it.

Everything that was still missing here is now built: see the next part.

### Added by CORE2 (same branch; proof songs `test_p3d_motion`, `test_p3d_windows`, `test_p3d_scale`, `test_p3d_checks`, `test_p3d_load`)

**Speed and the camera.** Speed is free per film and per moment (Anthony on the camera test: "It's great. It can adjust speed accordingly."): fast whips, dives and rolls on the hard cuts, slow revolves on the breath.

- `whip=True` (or a number of degrees, default 70) on a move: a whip pan INTO that move over its `blend` (0.3 to 0.6 s). The view swings away from the old set-up toward the new one, faster and faster, cuts at the middle of the swing (hidden in the motion blur), then swings into the new view and comes to rest. It turns about the vertical when the two views differ more in heading than in pitch (the horizon stays level), else it tilts. It never flies through what stands between the two set-ups. Without `whip` a blend is the old blend through space.
  ```python
  orbit((0, 1.2, -2), radius=7, height=2, a0=200, a1=440, t0=4.0, t1=8.0, whip=True, blend=0.5)
  ```
- Motion blur never reaches across a cut: every sample of a frame's shutter is taken on the frame's side of each hard cut (`blend=0`) and of the cut inside each whip. A hard cut without a burst is clean from its first frame.
- The background's motion blur takes up to 40 shifted samples on a long streak (a whip, a dive, 40 m/s low over the water), so the picture melts into one smooth smear instead of showing stepped copies. Short streaks keep the old 8 samples.
- `P3D["motion_samples"]` may be a Track: `Track([(0, 1), (8.0, 1), (8.01, 4), (9.99, 4), (10, 1)])` draws the point sets at four moments of the shutter only during a fast turn (four times the light-pass work there, none elsewhere).
- Proven in `test_p3d_motion`: a skim at 40 m/s 1.2 m over a storm lake (radial streaks on the near water, far hills crisp), a whip pan into an orbit (level, one smooth smear, cut invisible), a fast revolve, a hard cut with a clean first frame, a turn at 120 degrees a second with four moments, and a flight straight through a curtain of 300 thousand points (a clean warp of streaks, no flash).

**Kilometres.**

- The lake and the hills now stand round the world's origin, not round the camera: a camera that climbs or flies far sees the lake shrink to a disc, the rings of hills come nearer and pass below it, and the plain round the lake shaded by its real distance (dark close below, hazy far off). For a camera near the origin the picture is as before.
- World setting `shore` (default 1400): metres from the origin to the lake's shore. `shore=350` makes the lake a disc 700 m across that lies whole in the picture from 2 km up (the hills keep their distance, with a plain between); a shore beyond 1400 moves the hills out with it.
- Proven in `test_p3d_scale`: a pull-back by a constant factor per second from 8 m to 2.4 km above the lake (written as `fly` keys at `d = 8 * 300 ** (t / 4)`), and a flight in from 3 km outside the shore.

**Lines and ribbons.** Segments take motion blur (camera and their own `vel` per segment): each segment is drawn over the whole band it sweeps during the shutter, with the exact time average of its profile there (it slides as one piece, by the mean motion of its two ends), so a streak is smooth at any length. Ribbons keep their joins (faint seams can show where a ribbon bends sharply). Load: 60 thousand long moving lines with pulses cost about 2.6 s of processor time a frame in `test_p3d_load` (an averaging by 48 samples cost 9 s; real plexus lines are much shorter).

**Points, speed.**

- A static set of 60 thousand points or more is sorted once into spatial cells; each frame only the cells in view are drawn (one indirect draw). The picture is the same (max difference 2 of 255 on the 2.4 million point load test).
- In the lake mirror a set of 300 thousand points or more draws every second point (every third from 1.2 million), each brighter. Bodies and words stay whole.
- Measured: point sprites as GL points were only 20 percent faster on the render machines (their cost is per primitive, not per vertex), so sprites stay instanced quads.
- `P3D["sky_res"] = 0.5`: the sky, hills, lake and mist are drawn at half size (they are soft light; stars and every point set stay full size). Halves the background's cost (0.36 to 0.19 s of processor time a 1080p frame). Default 1.0.
- `keep_hue` (world setting 0..1, a Track): bright lights keep their hue instead of bleaching to white (the tone curve is applied to the brightest channel above the mid tones). Let it fall to 0 for a whiteout into the sun. The key must be in `P3D["world"]` (the composite then compiles the block; songs without it are untouched).

**The lake as a field.** `lake=dict(field=f, center=(x, z), size=200, res=96)`: `f(x, z, t)` gets two arrays of places (metres) and returns `(ripple, mirror)` there (arrays or numbers). Over the square of `size` metres round `center` the field replaces the world's `ripple` and `mirror` (with a soft edge), for the water's colour, its reflections and the mirror images of every point set. The calm discs still apply on top. Example (a storm with glass that widens round a place):
```python
def _lake(X, Z, t):
    r = np.sqrt(X ** 2 + (Z + 2.0) ** 2)
    calm = 1.0 - np.clip((r - (6.0 + 2.0 * t)) / 3.0, 0.0, 1.0)
    return 2.6 * (1.0 - calm), 0.55 + 0.45 * calm
world=dict(..., lake=dict(field=_lake, center=(0.0, -2.0), size=60.0))
```

**Skies by place.** `split` now also gives the other look's own sun (glow, disc and its glint on the water), water colour and hill colour on its side. `toward` may be a world point `(x, y, z)` or `(x, z)`: the sky toward that place takes the other look wherever the camera flies (the dawn left behind a moving front: `toward=` the place the wave started). `cover` (0..1, default 0.5) is how much of the sky the other look takes: 1 sweeps it over the whole sky (night swept off as the front reaches the horizon). Both may be functions of time.

**Masks and windows.**

- Two sky layers per frame, each with its own fill, look, tint, edge and softness: two different windows at once (a night window beside a flat coral word), or a window inside a window. Masks with the same fill share a layer; `Mask(slot=0 or 1)` picks one. A third different fill in the same frame is left out (a warning is printed once).
- `Mask("sky", sky="flat", color="#f0566a")`: the shape is filled with exactly that colour (a hex is shown exactly, as `paint`; a triple is linear light; may be a function of t). The flat fill WORDS asked for.
- `Mask.soft` below 3 is honoured; below 2.5 the silhouettes of that frame are drawn at full size (crisp letters). The default soft 3 renders as before.
- `window="<masked set>"`: the set lives in that set's window (`window=True` is the first window, as before). A set that lives in a window and has its own `Mask("sky")` is a window inside the window:
  ```python
  scene.add("tall", body, mask=Mask("sky", sky="world", look="night"))
  scene.add("birds", flock, window="tall")                       # live in the night world
  scene.add("inner", child, window="tall", mask=Mask("sky", sky="flat", color="#ffd060", soft=1.5))
  ```
- A window onto another world shows that world's own stars.
- Silhouettes are mirrored in the lake: a dark body is dark in the water too (its reflection no longer shows both its sides, and the reflections of lights behind it are hidden), a window's reflection shows its world, and sets living in a window are mirrored inside the window's reflection only. A set with `reflect=False` casts no mirrored silhouette.
- A point right at the lens no longer blacks out the picture through the mask.

**Rays from moving lights.** `lights=[dict(pos, color, strength, radius, rays=1.0, size=0.6)]`: a moving light with `rays` above 0 throws its own rays round whatever stands in front of it (cut by the silhouettes), like the single `light=`. Each costs three quarter-size passes.

**Checked as full-size stills** (`test_p3d_checks`, one set-up per two seconds): a keep-clear box (lights, lines, ribbons and stars all kept out), hexagonal bokeh (`bokeh_hex=1`), a figure coloured by two moving lights (`lit`) with rays from one, a macro 5.5 cm from a fingertip-sized cluster (`near=0.02`), lines with strong pulses under a turning star dome with a set and the camera riding one `Frame`, `keep_hue` on against off, the arch close up in nine colours, and a split toward a world point.

**Also checked** (helper CORE2): `test_p3d_ten` as full-size stills at fourteen moments (paint, the window world, the split sky, the arch in nine colours with travel and yaw, birth times, ribbons with pulses, the free camera through a loop, light pools, calm discs, shake, dolly zoom, rack focus); the eight looks of `test_p3d_looks` (golden, day and cream as retuned); a draft of `test_p3d_ten` (draft mode works with every new part); `keep=("stars", "motes")` brings the flat 2D layers back; frames do not depend on render order (`test_p3d_windows`, `test_p3d_motion`, `test_p3d_checks`, two orders, the same bytes); the camera test at head keeps the approved composition and feel (the far hills now shift a little with real parallax); `t_short_test` and `epic_concert` are byte-identical to epic-promo (12 stills).

### What is weak

- Points are light only: they cannot cover each other. Solid bodies come from the mask pass: one "dark" layer and two "sky" layers per frame, not one per figure.
- The silhouettes' mirror images are the shapes turned upside down below the water, without the ripples' smear.
- Hills, clouds and lake are drawn by formula, not from points: no shadows, and a dark body does not shade the water. Clouds are a sky at infinity (the camera cannot fly into them). The plain round a small lake is a plain textured colour.
- Sprite motion blur is a stretch along each sprite's path, not a true time average (use `motion_samples` for points that turn sharply inside one frame); lines and ribbons take a true average of their positions.
- Speed on the render machines is mostly the number of sprites drawn (about 0.5 s of processor time per million drawn quads, the mirror doubling it); see the load test.
- A plain blend between two camera set-ups (no `whip`) still flies through the space between them.
- The look `golden` reads silver-white rather than gold when its rays face the camera.
- With more than two different window fills in one frame the third is left out.

## W. Particle bodies (2026-11-15, branch engine-p3d-bodies)

People made of points for the 3D layer of section V: a lifelike human form (the MakeHuman CC0 body) moved by motion capture (CMU) and gestures, dressed in simulated garments of light, drawn in looks, with effects that gather the body out of light and scatter it back. The module texts of `engine/p3d/body.py`, `effects.py`, `looks.py`, `actor.py` and `motion.py` are the full reference; this section lists every key a director needs. Working examples: `engine/songs/test_p3d_bodies.py` (one stage per look, effect and motion; `listing()` prints the stage times).

### Changes for song files (newest first)

- Motion capture is now CMU only (the DeepMimic clips are gone, see `assets/p3d/README.md`). New motions: "jump", "dance", "twirl", "get_up", "pull_up", "helped_up". The old names still play: "spin" plays "twirl", "dance_a" and "dance_b" play "dance". Walk and run keep their names; the walk is a little slower by default (1.26 m/s for the man) and its steps are planted: a foot on the ground stays where it was set down, also while the walker turns.
- `Flare` (and the flash of `Hands`) is smaller: sized for two hands in close-up. `Flare(..., scale=2.5)` gives the old size; `Hands(..., flare=0)` leaves it out.
- `Hands`: each hand's second colour is now a pale tint of its own colour (it was white), so gold and blue stay apart as in ref 04.
- `hair` now defaults to "bun" for a woman and "cap" for a man or a child (hair worn close, no simulation), so no head is bare. `hair=False` gives the old bald head; `hair=True` the long simulated strands, which now hang from the back of the head only.
- Garments read as garments: hems, cuffs and necklines glow (`look=dict(name=..., seams=0)` turns it off), a "tunic" reaches to mid thigh over loose trousers, a "robe" has an under-sleeve on the forearm (a raised arm no longer leaves its hand floating), and the veil drapes over the head and shoulders as its own pale sheer fabric (`veil=True` or `veil=dict(length=1.5)` for a veil to the ground).
- Looks: glitter has far fewer four-point glints (`glints=`, default 0.0007 of the points); the rim line is thinner (`power=`, default 5) and the dark body no longer leaves a dark halo round it.

### A body

```python
from p3d.body import Body, Hands
from p3d import pairs
from p3d.crowd import Crowd

def build(scene):
    Body("woman", at=(0, 0), facing=180, garment="robe", veil=dict(length=1.5), look="glitter",
         gesture=[(1.0, 30.0, "open_arms", dict(lift=0.25))], wind=(0.4, 0, -0.6)).add(scene, "mother")
```

`body.add(scene, name)` adds the body with the mask its look needs (a dark body for "rim", a window for "window"); `mask=False` leaves it out, `mask=dict(sky="clouds")` sets it.

| Key | Meaning |
|---|---|
| `shape`, `height` | "woman", "man", "child"; metres (default 1.59, 1.73, 1.31) |
| `at` | where the feet stand: (x, z), (x, y, z), keys [(t, place), ...] or a function of time (carried) |
| `facing` | degrees (0 faces +z, 90 faces +x), or keys [(t, degrees), ...]: the figure turns, a walker follows |
| `motion` | a name or keys [(t, name), (t, name, dict(...)), ...]; each eases in over `blend` (default 0.9 s). Names below |
| `gesture` | keys [(t_on, t_off, name), (t_on, t_off, name, dict(...))]: the upper body eases in and out (`ease`, default 1.2 s). Names below. `to`/`to2` are world points or functions of time |
| `garment` | "dress", "robe", "tunic", "coat" (default dress for a woman, tunic otherwise), None for none |
| `veil` | True, or dict(length=1.0, wide=1.0): over the head and shoulders and down the back (1.5: to the ground) |
| `hair` | "bun" (woman default), "cap" (man and child default), True or dict(length=0.42) (long strands), False |
| `look` | a name, a dict(name=..., bright, size, color, color2, seams, glints, power, detail, share, links, reach, stars), or a list; each may carry weight=<number or function of t>, after="sweep" or before="sweep" |
| `color`, `color2`, `bright`, `size` | the two colours the look mixes, brightness, grain size |
| `points`, `detail` | 30 to 120 thousand points; dict(head=3, hand=4) for close-ups |
| `part` | "bust", "arm.L", "arm.R", "hand.L", "hand.R", "hands": only that part (fading toward the elbow) |
| `hand` | dict(side, at, aim, palm, pose, anchor="palm" or "fingertips" or "wrist"): the figure is moved so that this hand is exactly there |
| `scale`, `frame` | any size (100 a giant; everything grows about `at`); a moving ground: a function of t giving (x, y, z) or ((x, y, z), yaw) |
| `light` | a world point the body is lit from (plexus and glitter brighten toward it) |
| `wash`, `sweeps` | dict(color, amount=<number or function>); dict(name=dict(t, at=<place name, point or function>, speed=3, width=0.3, flash=2)) |
| `effects` | a list of dict(kind=..., t=..., ...): see Effects |
| `show`, `fade` | (t_in, t_out): the body exists only then; seconds of fade. Give late bodies `show` so their garments do not simulate from 0 |
| `wind`, `gust` | a `Wind` shared by the scene (effects.Wind(base, gusts=[(t, strength, seconds)])) or (x, y, z) m/s |
| `stoop`, `seed` | an elder's posture 0..1; another person (stance, timing, noise) |

Looks: "glitter" (refs 15, 10, 09; p08), "plexus" (refs 03, 12; p01; with `detail` 0..1 a few stars and lines that fill into the whole web), "rim" (refs 01, 16; p06: a dark body with a thin bright edge), "dots" (ref 14), "window" (ref 08; p07: the silhouette is a window onto a sky; `mask=dict(sky="clouds" | "sunrise" | "stars" | "world", look=...)`).

Motions: "stand", "walk" and "run" (`speed` in m/s, `phase`; the steps follow the speed, feet stay planted), "kneel" (`sit`, `one`, `hands`="lap" | "pray" | "free", `dur`), "rise" (up from kneeling, `dur`, `one`), "sit", "shuffle" (small steps on the spot), "held" (a child carried), and the captured "jump", "dance", "twirl", "get_up" (from lying), "pull_up" and "helped_up" (`rate`, `phase`).

Gestures: "look_up" (amount), "reach" (side, to, palm, height, far, lead), "open_arms" (lift 0 low to 1 raised), "raise", "blow" (side), "pray", "bow" (amount; from 30 degrees the body bows from the hips), "touch" (side, to, end, palm, fingers), "hand_on_shoulder", "handshake" (grip), "high_five", "embrace" (to, to2, head), "arm_round", "cup" (height, out), "offer", "listen", "raise_hand" (side, to), "clap" (period, height), "throw", "wave", "brace", "hold_thread" (place "pinch.R"). Any gesture takes `fingers=` a hand pose: open, relaxed, flat, spread, cup, fist, point, pinch, offer, hold.

For other point sets (world coordinates, any time, any order): `body.where(t, name, normal=False, raw=False)` (head, crown, mouth, neck, heart, chest, back, pelvis, ground; with .L or .R: shoulder, blade, elbow, wrist, palm, fingertips, index, thumb, pinch, hip, knee, ankle, toe, side; `raw=True`: without the body's own gestures), `body.joint(t, bone)`, `body.constellation(t)`, `body.free(t)` (every particle off the body), `body.handover(effect, t, targets)`, `body.shape_points(t)`.

### Effects (`effects=[dict(kind=..., t=..., ...)]`)

| Kind | What it does, main keys |
|---|---|
| "form" | the body gathers out of drifting dust: dur, travel, order ("noise", "up", "down", "out"), share (part that flies visibly), source=<points or function> (gather from given places: a word, a veil) |
| "dissolve" | rises apart from the head into flakes (refs 05, 11, 13): dur, share, rise, swirl, color, color2 |
| "disperse" | blows away from one side (refs 01, 06, 16): dir, dur, share, speed |
| "petals" | turns to petals that leave in a spiral (ref 07): color, color2 |
| "birds" | birds leave the silhouette (ref 08): n, dir, speed, size, color (dark birds are painted) |
| "blow" | a stream from the open palm (ref 14; give the body the "blow" gesture): side, dur, reach, color, color2 |
| "shed" | sheds light while it stands or walks (ref 15): n, life, where ("back", "top", or part codes), dir, speed |

The Release effects (form, dissolve, disperse, petals) take `amount=<Track or function 0..1>` instead of their clock: forward, hold (`hang=` seconds: the particles slow and stay in the air) and backward (every particle flies home to where the body is now). Every effect takes a hand-over: `to=dict(t, targets=<(K, 3) or function>, arrive=1.5, stagger=0.5, until=None)` (the free particles fly to the targets; many particles on few targets are dimmed so the targets do not blaze), or later `body.handover(...)`. `Flare(at, t, scale=1)` is the flash of a touch (scale 2.5 for a wide shot); `Takeover(state, t, targets)` flies plain particles to places.

### Pairs in contact (`engine/p3d/pairs.py`)

Each returns two Bodies (add both); `a` and `b` are dicts of Body keys. Contact is solved every frame (measured: 1 to 4 mm).

| Function | What |
|---|---|
| `pairs.embrace(t, at, facing, a, b, until=None, gap=0.34, approach=0.0)` | they walk in over `approach` seconds and hold each other from t |
| `pairs.hands(a, b, t0, t1, raised=False, sides=None)` | hand in hand (standing or walking side by side; the inner hands are found), or joined hands raised high |
| `pairs.helped_up(t, at, facing, a, b, rise=1.7)` | b kneels; a reaches down, takes b's hand and pulls b up to standing |
| `pairs.child_into_arms(t, at, facing, adult, child, lift=1.0)` | the adult bends, takes the child under the arms and lifts it into a hold; the child's arms round the adult's neck |
| `pairs.pull_up(t, at, facing, a, b)` | the captured pair: b sits on a low seat and is pulled up by the right hand |

Two bodies of your own can reach for each other the same way: give each a gesture whose `to` is `lambda t: other.where(t, "blade.R", raw=True)`.

### Crowds (`engine/p3d/crowd.py`)

`Crowd(n, places=None, area=dict(center, radius=(r0, r1), arc), facing=<degrees, (K,), function (x, z), "center" or "out">, kinds=("stand", "raise", "clap", "walk", "run", "bow", "pray", "open", "sit", "child", "child_run"), start=<t, (K,), dict(t, center, speed) for a wave, or dict(t, dur)>, until, fade, flash, walk=<m/s>, points=2600, scale, color, color2)`. Hundreds of people from a few baked prototypes; each appears at its own time with a flash. The first frame of a render process bakes the prototypes (about 10 s each); a frame of 300 people then costs about 0.2 s. `crowd.where(t, k)` gives person k's place.

## X. Particle words: the nine expressions as light in the 3D world (2026-11-15, branch engine-p3d-words)

For songs that use the 3D layer (`P3D`, section V). The Words of Mother's Love become point sets (`engine/p3d/api.py`): each expression is about fifty thousand points on a plane (or a gentle curve) standing anywhere in space, made of the same light as the people, mirrored in the lake, blurred by the lens when it is not being read. They arrive and leave in nine ways each, may hand their particles to each other, and several can be on screen at once at different depths. Code: `engine/p3d/words.py` (pure numpy, no graphics needed). Working example: `engine/songs/demo_p3d_words.py` (all nine expressions and a title in 31.5 seconds, with helper BODY's hands and people and a camera that never stops moving).

The words themselves live in `words.EXPRESSIONS`: the nine labels with the full campaign wording (DESIGN-SYSTEM section 5; "(or root)" stays), their line breaks and their colours. A song never retypes them: it names an expression with `expr="Gratitude"` (or 1 to 9).

```python
from p3d import words as PW

WORDS = PW.Words([
    dict(expr="Greeting", pos=(-6.0, 5.0, 12.0), em=1.4,
         t_in=0.0, t_read0=2.4, t_read1=5.3, t_out=7.3, arrive="touch", leave="flock"),
    dict(expr="Gratitude", pos=(0.0, 12.0, -4.0), em=2.2,       # arrives while the Greeting is read
         t_in=4.4, t_read0=6.6, t_read1=9.5, t_out=11.4, to=(-39.0, 18.0, -45.0)),
    dict(expr="Apology", pos=(-1.0, 3.3, 8.0), em=1.5,
         t_in=8.6, t_read0=11.0, t_read1=13.9, t_out=15.8),
], face="camera")                     # settings after the list hold for every word

CAMERA = Rig([...  focus=lambda t: WORDS.focus_point(t, (0.0, 6.0, 10.0)) ...])

def build(scene):                     # the song's P3D["setup"]
    WORDS.add_to(scene)
    WORDS.check(CAMERA)               # prints what it finds

P3D = dict(camera=CAMERA, world=WORDS.world(dict(look="night", ...)), setup=build)
```

**The four times of a word** (seconds of song time): `t_in` the first particle appears; `t_read0` the word is whole and the reading moment starts; `t_read1` the reading moment ends; `t_out` the last particle is gone. Give every expression a reading moment of at least 2.5 s (the example uses 2.9 s, six beats). Arrivals look best with 2 to 2.5 s, leavings with about 2 s. Words may overlap freely in time: the example reads one expression while the next forms at another depth, and twice reads two at once.

**Keys of one word** (a dict in `PW.Words([...])`, or `PW.Word(...)`):

| Key | Default | Meaning |
|---|---|---|
| `expr` | | one of the nine labels or 1 to 9: fills label, lines and colour. Or `label=`, `lines=[...]` for any other text (one or two lines) |
| `pos` | `(0, 3, 0)` | the centre of the phrase block in metres (y up, the lake is y = 0), or a function of t |
| `em` | | metres per em of the phrase face (the same letter size on every word); or `width=` (default 8.0): metres across the widest line of the phrase |
| `facing` | 0 | the azimuth the words face, degrees (0 faces +z, as `p3d.at`) |
| `face` | `"fixed"` | `"camera"` turns the plane about the vertical so it always faces the camera; `"screen"` keeps it flat to the picture |
| `tilt`, `curve` | 0 | degrees the plane leans back; radius in metres of a gentle curve (positive bends the ends toward the reader) |
| `t_in`, `t_read0`, `t_read1`, `t_out` | | the four times |
| `arrive`, `leave` | by expression | names from the two tables below; without them each expression uses its own pair (`PW.DEFAULT_STYLE`) |
| `source` | | where the arrival comes from: a point, a function of t, a point set (a hand, a body), or the name of another word (`arrive="morph"`) |
| `to` | | where the leaving goes: a point (a light of the arch), a point set (a person), or the name of another word |
| `color`, `glow` | the expression's colour | display hex of the letters' colour and of the halo; `tint` (0.45): how much of the colour the letters keep (the rest is warm white, which reads best) |
| `bright`, `halo`, `sparkle` | 1.0 | brightness of the letters, of the coloured halo round them, of the glints on them |
| `sharp` | 1.0 | how far the settled letters ignore the lens blur: 1 keeps a word sharp for its whole reading moment whatever the camera focuses on; 0 leaves it to the lens. Flying particles always blur with the lens |
| `fog` | 0.0 | how much of the world's haze the settled letters take (flying particles take all of it) |
| `n`, `n_label` | `"auto"` | points of the phrase and of the label. `"auto"` chooses them from the word's largest size on screen while it is read (42000 and 6000 at an em of 85 px, growing with the square of the size, 12000 to 240000), so the edge of a letter stays about one pixel soft; it needs the camera (`Words(..., camera=)` or the word's `camera=`), else 42000. A number fixes it |
| `label_size` | 0.36 | size of the label in em of the phrase |
| `font` | the expressions' italic | `"title"` (the end card's upright bold), `"tag"` (the lighter italic) or a font file |
| `wind` | `(1, 0.22, 0.1)` | the direction the air moves (leavings `wind`, `petals`, `flock`) |
| `water` | 0.0 | height of the water for `lake`, `sink`, `gather` |
| `name` | the label | the name other words and the scene use |

**Nine ways of arriving** (`arrive=`), from `t_in` to `t_read0`:

| Name | What happens | Made for | Options |
|---|---|---|---|
| `touch` | two lights, gold and blue, come together; where they touch a flare is born and writes the words outward (ref 04) | Greeting | `source` the point of the touch (two hands; then the two lights are not drawn unless `comets=True`), `touch_at` (0.10: the share of the arrival before the touch; set it so the touch falls on a beat), `flare_size` (metres; default 0.55 of the word's width: give about 0.2 for hands in close-up) |
| `petals` | petals spiral in as one stream and land; each lights its part of the letters (ref 07). They stay well away from the lens | Gratitude | `arm` (radians: where the stream comes from), `swirl` (turns), `petal_size`, `petals` (0.6: the share of the carriers seen as petals), `source` a body or hand |
| `lake` | the words lie in the water as a reflection of words not yet there; then, column by column, the letters come up the last stretch into their places out of the water's light, shedding drops that fall back into the lake | Apology | `water`; stand the word low over the lake and far enough for its mirror image to be in the picture |
| `gather` | many small lights in the nine colours walk in over the water from the sides and from behind, stand under the words and rise into them | Inclusiveness | `carry` (height the lights are carried, 1.15 m), `water`, `source` |
| `flock` | a long loose stream of birds comes in from far away, wheels round, and feeds into the words front first: each bird peels off to its place and lights the letters round it (ref 08) | Concession | `turns` (1.0), `flock_from` (radians: where the flock is first seen), `flock_lift`, `stream` (0.22: how long the stream is), `birds` (how many; default about four for each square em of the text, 44 to 200), `bird_size` |
| `stars` | small sharp stars come out one by one in the sky behind the words and drift onto the letters; a fine line joins two neighbours once both have landed (a constellation drawing itself in reading order); then the letters fill and the lines go (ref 03) | Respect | `stars` (0.5: the share of the carriers seen as stars) |
| `shaft` | flakes come down a shaft of light from above and assemble (ref 13 reversed); the shaft stays, fainter, while the words are read | Encouragement | `flake_size` |
| `palm` | a stream of dust blown from an open palm settles into the letters in reading order (ref 14) | Consideration | `source` the palm (a point, a function of t, or a hand's point set), `blow` the direction of the breath, `palm_light=True` draws a small light at the source |
| `rays` | rays from a light burn the words out of mist, along the rays first (ref 10, 16) | Compliment | `source` where the light stands (behind a person's head); default behind the words |
| `morph` | the particles of another word (or of any point set: a person) fly over and become this word | any | `source` (required) |

**Nine ways of leaving** (`leave=`), from `t_read1` to `t_out`:

| Name | What happens | Options |
|---|---|---|
| `wind` | the wind takes the words from the downwind side; they stream off as dust (ref 01, 16) | `wind`, `speed` |
| `rise` | they dissolve upward from the top into flakes and sparks (ref 05, 11, 13) | `speed`, `flake_size` |
| `arch` | they stream into one light of the arch and wake it | `to` the light's place in the world (`p3d.world.arch_points(...)[i]`) |
| `flock` | the letters lift off as birds in reading order and draw together into one loose stream that flies away on a gentle curve; the rest of the letters fall to a little dust | `away` (direction), `speed`, `birds`, `bird_size` |
| `petals` | the letters turn to petals that spiral away on the wind (ref 07) | `reach` (0.4: how wide the spiral opens, in widths of the word), `speed`, `petal_size`, `petals`, `wind` |
| `sink` | they fall like rain into the lake and spread over it as rings of light | `water` |
| `bokeh` | they rush toward the camera, opening into great soft discs, and are gone before they reach the lens | |
| `give` | the particles fly to another body of light and become part of it | `to` a point set (a person) |
| `stars` | the letters thin to stars joined by lines; the lines go before the stars drift back into the sky | |
| `morph` | the word is held until the next word (`to`, or the word whose `source` it is) starts, which takes over its particles; its own shaft or rays go out just before | |

**Handing particles on.** `dict(expr="Apology", arrive="morph", source="Gratitude", ...)` with `leave="morph"` on the Gratitude: the Gratitude is held until the Apology's `t_in`, then its particles fly to the Apology's letters (place, colour, halo, size and count blend over without a jump). `leave="give", to=<a body's point set>` turns a word into a person; `arrive="morph", source=<a body's point set>` makes a word out of a person. `arrive="palm", source=lambda t: body.where(t, "palm.R")` takes the open palm of one of helper BODY's people (the example's woman in profile raises it with the gesture `"blow"`), and `arrive="touch", source=<the point where two hands meet>` the touch of BODY's `Hands(meet=..., t_touch=...)` (add only their `left` and `right` to the scene: the word draws the flare itself, sized by `flare_size`); without a source the word draws small lights of its own. A word becomes a real person with `leave="give", to=<the Body>` while the Body forms out of the word's letters: `effects=[dict(kind="form", t=<the word's t_read1>, dur=2.2, source=lambda t: WORDS["Inclusiveness"].targets(t))]`; the example then lets the Compliment's rays come from behind her head (`source=lambda t: body.where(t, "head")`). Leavings and arrivals also pair without any setting when they are staged together, as in the example: the Greeting's birds fly to where the Concession's flock is first seen; the Consideration's petals leave as the Gratitude's arrive; the Gratitude streams into a light of the arch and the Encouragement's shaft comes down; its flakes rise where the Respect's stars come out; the Apology sinks into the lake and the lights of the Inclusiveness walk over that water; the Inclusiveness becomes a person and the Compliment's rays come from behind that person.

**Laying words out by the picture.** `PW.place(camera, t, x, y, depth)` gives the world point seen at the screen place (x, y) (0..1 from the left and from the bottom) `depth` metres in front of the camera at time t; `PW.em_for(camera, t, depth, px)` gives the metres per em that make one em `px` pixels of a 1080p picture there. The example lays every word out at the middle of its reading moment with these two (its `_word` helper), in three bands at three depths: the sky (y 0.75 to 0.80, 32 to 34 m), the sides (y 0.58 to 0.63, 11.5 to 20 m), the lake (y 0.47 to 0.50, 22 to 24 m). Its camera never stops (a pull back that rises, then a revolve of 40 degrees that climbs, then a push in), and every word faces it (`face="camera"`): a word that is read keeps its place within a few percent of the picture, the other bands drift against it, which is what shows the depth. Lay a word out with a copy of the camera that has no focus pull (the example's `_LAYOUT`), since the real camera's focus asks the words where they are.

**Reading on a phone.** Imagine the frame 6 cm wide: 1 mm is 32 px of a 1080p picture. A word is easy to read when the x-height of its phrase is about 1 mm or more (an em of 80 px), so the longest expression (the Gratitude, 15.5 em wide) wants about two thirds of the picture's width while it is read, a short one (the Greeting, 6 em) a quarter. Settled letters are an even lattice of points with antialiased edges, sharp whatever the lens does (`sharp`), clear of the haze (`fog`) and of the motion blur, with a coloured halo. They are light: on a night, dusk or deep blue sky they read strongly, and still well on the pink of a predawn sky; on a pale day sky light reads weakly (section S), so keep reading moments in front of the darker parts of the picture. Keep what leaves and what arrives away from a word that is being read: petals, birds, dust and a shaft of light are bright, and the check below only knows about the words' own boxes. In the example the leaving effects are aimed out of the picture (`wind`, `away`, `reach`) and a shaft stands behind the band it belongs to.

**The check** `WORDS.check(camera=None, min_read=2.5, need_all=True, min_x_mm=0.9, min_cap_mm=0.55, calm=None, raise_on_error=False)` returns `(problems, notes)` and prints them. Always: the four times are in order; every word is read for at least `min_read` seconds; all nine expressions are there. With a camera (the song's `Rig`, or a function of t that gives the camera state): during every reading moment the word is wholly inside the picture, faces the camera, and is large enough for a phone (x-height at least `min_x_mm`, the label's capitals at least `min_cap_mm`, of a 6 cm wide frame); and two words that are read at the same time never cover each other on screen. `calm=0.335` also refuses a reading word that reaches into the calm lower third. Run it in the song's `setup` (or from a shell: `python -m p3d.words` in `engine/` runs a small self check).

**Focus, shafts, rays.** `WORDS.focus_point(t, default)` gives a world point that travels to the word being read and back to `default` (a point or a function of t): give it to a camera move as `focus=lambda t: WORDS.focus_point(t, (0, 6, 10))` and the lens racks to each word as it is read while the other depths go soft. `WORDS.world(dict(...))` returns the song's world settings with the words' own light added: a real shaft of light (section V, `shafts`) for every word that arrives by `shaft` (gentle on purpose: it also stands behind whatever is read below it), and the world's `light` with rays for the word that arrives by `rays`. `word.shaft(color, strength)` and `word.light(color, strength, size)` give the two entries one at a time.

**Cost.** Sampling one word takes 4 to 16 ms a frame in numpy at 50 thousand points (more for a large word with `n="auto"`: about 0.3 ms per thousand points); a word outside its four times costs nothing. A draft draws every second point. The example renders at about 1 s a frame at 1080p on two threads here (2 s while the people's garments are simulated).

### X2. The directors' kit (added for the ten films, 2026-11-15)

Working example: `engine/songs/demo_p3d_words_kit.py` (every item below in 30 seconds; it needs only one expression at a time, so it calls the check with `need_all=False`). All of it is optional: the keys of section X work as before. Part two, `engine/songs/demo_p3d_words_kit2.py` (24 seconds), shows the rest: a word in a fold of a veil written by someone else's pen, a word the size of a hand rising from a palm, a reveal behind an edge of the song's own (`gate=`), turning, tilting and rolling over time, `drive=`, the three other carried morphs, and windows onto clouds and a sunrise.

**Home places.** `word.home()` gives every point's fixed place in the word, label included, as arrays in an order that never changes: `x, y, z` (metres on the word's plane from the centre of the phrase block), `line` (-1 for the label), `word`, `glyph`, `order` (0..1 along the writing of the phrase; for label points along the label), `write` (0..1 along the writing of everything, the label first), `label`, `weight`, `size`; and per glyph `chars`, `glyph_line`, `glyph_word`. `word.targets(t, cam)` gives the same points in the world at t, `word.frame(t, cam)` the plane (centre, right, up, normal). To drive the points yourself give the word `drive=f`: `f(t, info)` gets `info = dict(state, pos, home, frame, cam, word)` (state is "arrive", "read" or "leave"; pos is where the built-in effect puts the points, home their settled places) and returns a dict with any of `pos` (replaces), `alpha` and `emit` (multiply), `assist` (0 flying and blurred by the lens, 1 settled and sharp), `color`.

**A sharp reading mode** is the default: settled letters ignore the lens (`sharp=1.0`), the haze (`fog=0.0`) and the motion blur, at any physical size (the effects scale with the word: paths with its width, petals, flakes and birds with its em). The letters are a lattice of `n` points; the softness of their edge is about one lattice step, which is 1 pixel when an em is 85 px at 42000 points. `n="auto"` (the default) chooses the count from the word's largest size on screen while it is read, so a word that fills the picture gets more points and a small one fewer (12000 to 240000; give a number above that for a word larger still). A word the size of a hand works (`demo_p3d_words_kit2.py`: an em of 26 mm 0.45 m from the lens); for such macro shots give the camera move `near=0.02`, else the renderer fades points nearer than about 0.4 m.

**Anchors.**

| Wanted | Setting |
|---|---|
| fixed in space | `pos=(x, y, z)`, `facing=` degrees |
| facing the camera | `face="camera"` (turns about the vertical) or `face="screen"` (flat to the picture) |
| ride ahead of the camera | `ride=(x, y, depth)`: the word keeps that place of the picture (0..1 from the left and the bottom) `depth` metres ahead of the lens, through any camera move; it lies flat to the picture unless `face=` says otherwise. May be a function of t. Needs the camera: `PW.Words(specs, camera=CAMERA)` |
| beside a runner | `pos=lambda t: runner_place(t) + offset` (any function of t; with helper BODY, `actor.joint(t, "head")`) |
| tilting, turning, rolling over time | `tilt=`, `facing=`, `roll=`: numbers or functions of t |
| lying flat on the lake, read from above | `face="flat"` with `pos=(x, 0.03, z)`; `facing` turns it (0: read from the +z side). No mirror image is drawn |
| bound to a surface that moves | `bind=f`: `f(x, y, t)` takes arrays of places on the word's plane (metres) and returns their places in the world (N, 3): a veil's fold, the face of a wave. Every arrival and leaving follows the surface |
| in the folds of a garment | `bind=PW.on_cloth(body, "veil", u=0.5, v=0.4)`: the word lies on a piece of a Body's cloth (`"veil"`, `"skirt"`, `"sleeve.L"`, `"sleeve.R"`) and moves with it. `u` across the piece (for a veil 0.5 is the middle of the back), `v` down it (0 at the top edge), `lift` (0.012 m) off the cloth, `smooth` (3: the word follows the drape and the large folds, not every small wrinkle; 0 follows every wrinkle), `flip` (which side reads; chosen by itself: from outside). Metres on the word are metres along the cloth |

**More arrivals.**

| `arrive=` | What happens | Options |
|---|---|---|
| `pen` | written in order by a pen: the ink leaves the nib and runs to its place. `word.pen(t)` is the nib's place in the world, for a comet head or a fingertip to be put there | `nib=False` hides the word's own nib; `flow` (0.06) |
| `pen` with `source=f` | someone else moves the pen (`f(t)` gives its place: a comet, a fingertip): each letter is written at the moment the pen passes nearest to it, wherever it flies. On a word bound to a moving surface (`bind=`) the pen is followed over the surface itself | |
| `reveal` | revealed behind a moving edge that glows | `edge=` "right", "left", "up", "down" (a lowering height), "out", "in"; or `gate=f`: `f(places (N, 3), t)` gives 0..1 for an edge of your own (a crest, a hem); `soft`, `edge_glow` |
| `stitch` | a needle runs along the writing, short stitches show under the letters, the letters are pulled tight behind it | |
| `weave` | threads run across and down; a letter shows where both have passed | `rows` (14), `cols` (34) |
| `morph` with `carry=` | born from someone else's point field (`source=` any point set): its points fly in as "petal", "bird", "flake" or "soft" lights and land as letters; each lights its part of the word. Hanging rain, drifting petals, a flock landing ("bird" uses fewer, larger birds, `birds=`, each lighting the letters round its place) | `carry_colors`, `petal_size`, `bird_size`, `flake_size`, `birds` |

**More leavings.**

| `leave=` | What happens | Options |
|---|---|---|
| `stream` | one stream to a point that may move (`to=` a point or a function of t), or along a curve | `path=` points (K, 3) or a function of t that gives them; `star=True` lights a star at the goal |
| `doors` | the word parts like a pair of doors that swing open on their outer edges | `split` (0.5), `swing` (100 degrees), `inward=False` opens toward the reader |
| `unravel` | the end of the writing is pulled away as a thread and everything before it runs after it | `to=` where the thread is pulled to |

**Window words, ink and paint** (through the mask pass of section V; `Words.add_to` sets the mask up and adds the word's glints as a second set named "word <name> light"). The masks of words are crisp (drawn at full size, `mask_soft` 1.0; 3 or more gives the old soft half size edge):

- `window="stars"` (or "clouds", "sunrise", "day", "world" with `window_look=`): the letters are a window onto that sky. `window_edge`, `window_tint`.
- `ink=True`: dark letters for bright skies (the renderer's dark tint: a deep blue grey on a day sky); the strongest contrast on a pale sky.
- `paint=True` (or a hex colour): the letters filled with exactly their colour on any sky (CORE's flat fill, `Mask("sky", sky="flat")`), with a little of their own light over it (`paint_light`, 0.12) and few glints. True colour also means the campaign's pale colours (lavender, the pinks) stay pale on a pale sky: for a reading moment on a bright sky give a deeper shade of the colour (`paint="#8a63d2"` for the Compliment) or use `ink=True`.
- A frame holds two different sky fills (two window skies, or a window and a paint colour); a third is left out with a warning. Words with the same window sky or paint colour share one. `mask_weight` thickens or thins the letters.

**Colour.** `PW.EXPRESSIONS[i]["color"]` is each expression's campaign colour (DESIGN-SYSTEM section 5); a word takes it by itself. `tint=1.0` makes the letters fully that colour (the default 0.45 keeps them warm white with a coloured halo, which reads best).

**Keep clear.** Other layers can ask what to stay out of: `word.keep_clear(t, cam)` gives (strength 0..1, the box's four corners in the world, the plane's normal) for a word in its reading moment; `WORDS.keep_clear(t)` lists all such boxes; `WORDS.clear(points, t, cam)` gives, for any world points, how much of each may show (1 everywhere, down to 0.12 in front of and behind a word being read). `PW.KeepClear(pointset, WORDS)` wraps any point set so that it does this by itself: `scene.add("petals", PW.KeepClear(petals, WORDS))`. The words' own flying particles, birds, petals, threads, shafts and rays already keep clear of every other word that is being read (`avoid=False` on a word switches that off).

**What is weak** (seen in the proof, watched as motion, and in stills of the two kit songs):

- The check knows only the words' own boxes; a petal storm, a flock or a body crossing a word being read is not reported (the words' own flying particles dim there by themselves).
- A word lying on cloth reads only as well as the cloth faces the camera: keep it on the back of a veil seen from behind and give the body a lower `bright` so the letters stand out (the kit uses 0.45).
- Window words and painted words share CORE's two sky fills a frame. Pale campaign colours painted on a pale sky are true but faint: give a deeper shade.
- The palm's stream (`palm`) is dense near the hand when the hand is close to the camera; the gathering lights (`gather`) still make a wide carpet of coloured points over the water.
- Flying letters take half the motion blur; under a fast camera turn they still streak.


## Y2. People styles: many artistic looks for the people (2026-11-15, branch engine-p3d-styles)

Anthony: "Use different types of artistic expression for the people ... Do not bind yourself to one way of showing people." Artistic faces are allowed (never photorealistic); Heavenly Mother is still only from behind or as hands. Section Y2 gives each look of the references (scratchpad refs2 p01 to p09, refs 01 to 16) as a named preset: one call puts a finished figure (a body, or a face in profile) into a 3D scene, in a night or a day palette. Code: `engine/p3d/styles.py` (the presets), `engine/p3d/faces.py` (faces in profile and flowing hair), `engine/p3d/stylekit.py` (the small point sets the presets dress a figure with). Working example: `engine/songs/demo_styles.py` (every preset in turn, 3.75 s each, on the concert medley; `STYLES_FLIP=1` in the environment swaps every stage's sky to check the other palette).

```python
from p3d import styles as ST

def build(scene):
    ST.add(scene, "gold_glitter", name="giver", sky="day", at=(0, 0), facing=-10, t=4.0, show=(2.0, 10.0))
    ST.add(scene, "spark_profile", name="face", at=(3, 1.7, 0), facing=90, height=0.4, show=(10.0, 16.0))
P3D = dict(camera=..., world=..., setup=build)
```

`ST.add(scene, style, name=None, sky="night", **keys)` returns a `Styled`: `.main` (the Body or Profile), `.parts` (scene name to point set; extra parts are named `name + "_hair"`, `"_glow"`, `"_stars"`, `"_butterflies"`, `"_birds"`, `"_clouds"`, `"_mist"`, `"_glitter"`, `"_ink"`), `.where(t, place)`. `ST.listing()` prints the presets.

**Keys every preset takes.**

| Key | Meaning |
|---|---|
| `name` | the scene name of the main part (default: the style's name) |
| `sky` | `"night"` (default) or `"day"`. On a night sky the figure is light. On a bright sky light alone washes out, so the day palette also paints the figure (true colour over the sky) or gives it a dark silhouette of one exact colour (see "Dark silhouettes"). Pick the one that matches the world's look |
| `show`, `fade`, `seed` | when the figure exists (t_in, t_out), seconds of fade, another person |
| `t`, `dur` | when the preset's own effect starts (shatter, dissolve, dispersal, butterflies or birds leaving) and how long it runs |
| `color`, `color2`, `ink` | the palette (display hex); `ink` is the colour of a dark silhouette |
| `bright` | overall brightness |
| body keys | for body presets: `shape`, `height`, `at`, `facing`, `motion`, `gesture`, `garment`, `veil`, `hair`, `points`, `scale`, `wind`, `light`, `detail`, `stoop`, `frame`, `part`, `hand`, `size`, `effects` (added to the preset's own), and `body=dict(...)` for any other key of section W |
| face keys | for face presets: `shape` ("woman", "man"), `at` (the middle of the head), `facing`, `height` (chin to crown, metres), `tilt`, `turn`, `hair`, `features`, `points`, `garment`, `breathe`, `stream`, `eye_glow`, and `face=dict(...)` for any other key of `Profile` |
| `silhouette` | presets with a dark silhouette by day: `"mask"` (default, crisp, hides the lights behind it, uses one of the frame's two sky layers) or `"paint"` (painted discs, no layer used: for a frame with more dark figures of different colours than there are layers) |

**The presets.** Each is named after its look; the reference it answers is given. "Night" and "day" say how it is drawn on each sky.

| Preset | Looks like | Night / day | Own keys |
|---|---|---|---|
| `constellation` (p01, refs 03, 12) | a body of stars joined by fine lines, brighter toward a light above and in front, a few specks drifting off, small stars round it | white gold light / navy and gold, painted | `detail_track` (a Track 0..1: a few stars that fill into the whole web); `light` (a world point) |
| `spark_profile` (p06, ref 01) | a face in profile, the edge from brow to chin and down the throat traced by fine orange sparks that fray outward, embers streaming up off the top of the head, the inside dark, swept back hair of dim strands | dark silhouette on the night / deep navy silhouette | `eye_glow` (0..1: a small warm star at the closed eye), `stream` |
| `sky_window` (p07 flat, ref 08) | the body is a window onto a sunrise (night) or a cloud sky (day), a fine edge of light, birds rising out of it | sunrise, light birds / clouds, dark painted birds | `fill` (any Mask sky), `birds` (a colour, or None), `birds_dir` |
| `gold_glitter` (p08, refs 15, 10) | gold glitter with dark grains among bright ones, blowing apart from one side into flying glitter, glints round it | light / a bronze silhouette under painted gold grains | `dir`, `share` |
| `ember_dancer` (p04) | a dancer whose body is embers, bursting into a long stream of sparks behind her, long hair streaming | glowing embers / a deep ember red silhouette, the stream painted dark red with glowing grains | `dir`, `share`, `motion` (default "dance"), `flowing_hair=dict(...)` |
| `ash_dissolve` (p03, refs 05, 11) | a figure crumbling from the head into ash flakes blown to one side, red embers in the breaks | grey ash flakes, a dark body against a soft glow behind / a charcoal silhouette, dark painted flakes | `dir`, `share`, `ash` (the flakes' colour) |
| `mist_figure` (p09, ref 09) | a small figure of fine sparkling light in a wide slab of glittering mist, warm on one side and cool on the other; frame it far | light / painted pale gold | `field` (width, height, depth of the mist), `n_mist`, `toward` |
| `star_silhouette` (p02, ref 02) | a silhouette filled with a starry night (a violet tint), a fine edge of light, stars scattered round it | edge and a soft violet glow behind / strongest on pastel skies | `tint` |
| `glass_shatter` (p05) | a figure (arms opening) that shatters on one side into shards of glass: sharp triangles and quads with bright edges and a sweep of reflection, tumbling away; long hair; the hair leaves with the head | glassy shards of light, a dark body against a cool glow / a near black silhouette, dark painted shards with light on their edges | `dir`, `share` |
| `butterflies` (p02, ref 02) | a face in profile (or a body with `figure="body"`) filled with a starry night, long flowing hair in the same sky, small glowing butterflies leaving it and fluttering round it with trails of dust, stars about | starry violet / starry violet on pastel, butterflies also painted | `figure`, `n`, `dur` (how long they take to leave) |
| `dark_silhouette` (p03, p04, p05) | a person as a dark painted shape, the edge fraying into dark particles that drift off | a dark shape against a soft warm glow behind it, with a thin rim / one exact colour on the bright sky | `edge` ("flakes", "dust" or None), `share`, `dir`, `glow` (metres: the glow behind, night) |
| `nebula_figure` (p07) | the body filled with deep clouds lit from inside by a warm light at the chest, stars in the gaps, billows over the shoulders, birds leaving | the same clouds on both skies (slate shadows, warm light) | `glow` (Mask glow, below), `birds`, `birds_dir` |
| `nebula_profile` (p07) | a face in profile whose back of the head and shoulders turn into a cumulus of deep clouds lit from inside the skull, the face a smooth painted slate skin with brow, nose, lips, chin and the closed eye clear, birds leaving | as left | `glow`, `skin` (0..1), `birds`, `birds_dir` |
| `glitter_profile` | a face in profile made of gold glitter, the closed eye, brow and lips in brighter grains, glitter blowing off the back of the head, hair of fine gold strands | light / a bronze silhouette under painted gold grains | `stream` |
| `constellation_profile` | a face drawn as a constellation: stars on the skin joined by fine lines, the edge a chain of bright stars, the closed eye and lips small constellations | white blue and gold light / navy and gold, painted | |

**Faces in profile** (`engine/p3d/faces.py`, `Profile`). The MakeHuman body of section W is not enough for a 1080p close-up: its mesh has about 3 mm between vertices on the face, but the bake smooths the face to a mannequin on purpose (the nose and lips are soft bumps, there is no eye), and a whole body spreads its points so thinly that a head gets a few thousand. The faces are therefore drawn: a hand drawn profile curve for a woman and a man (forehead, brow, nose, lips, chin, throat, neck, the back of the skull and the shoulders), turned into a solid with a rounded cross section at every height, plus the lines of the features (the closed eye where the lids meet, its lashes, the crease of the lid, the brow, the parting of the lips, the nostril, the ear, the jaw, a neckline: everyone is clothed). Own geometry, written for this engine; no third party asset. Head units: chin to crown = 1; `height` gives metres (0.23 life size; a giant head in the sky: 3 to 8).

- `Profile(shape, at, facing, height, tilt, turn, look, color, color2, features, garment, hair, stream, eye_glow, bright, size, points, show, fade, breathe, seed)`. `at` is the middle of the head at eye level (a point or a function of t); `facing` the direction the face looks; `tilt` lifts the chin and `turn` turns the head (numbers or functions of t; only the head and neck move, the shoulders breathe).
- Looks: "sparks", "glitter", "constellation", "rim", "ink" (only a fine edge of light, for a dark mask), "fill" (a faint edge and the features over a window fill; `skin` paints a smooth face over it), or a list; each may be a dict with `bright`, `size`, `features`.
- `profile.where(t, name)`: "eye", "nose", "lips", "chin", "forehead", "crown", "nape", "ear", "throat", "heart", "head", "occiput" in the world.
- `profile.shape_set(hair=True, extra=[...])`: the solid head and shoulders (and the hair mass, and any extra shapes such as `stylekit.Billows`) as the source of a Mask: a dark head at night, a flat colour by day, a window onto a nebula or a starry sky. The bust's lower edge frays into dots instead of a cut.
- Seen best within about 35 degrees of side on: it is a drawing given depth, not a sculpted head.

**Flowing hair** (`faces.Hair`): long hair as a mass of locks (refs p02, p04, p05), procedural (a pure function of time, no simulation): every lock lies over the skull from the hairline and leaves it somewhere between the crown and the nape, then streams with the wind and waves, its tip curling. Keys: `length` (head heights, 1.0 to the shoulders, 2.0 long), `locks`, `per_lock`, `n`, `wind` ((u, v) in head units, or a function of t), `gust`, `wave`, `curl`, `volume`, `exit` (degrees on the skull where locks leave it), `fan`, `spread`, `roots`, `scalp` (how bright the hair lying on the skull is), `mass` (strand thickness in a silhouette), `look` ("glow" strands of light, "ink" a painted dark mass with a sheen, "sparks"), `color`, `color2`, `ink`, `bright`, `alpha`. A Profile wears it with `hair=dict(...)`; a Body wears it as its own set: `scene.add("hair", Hair(BodyHead(body), ...))` with the Body's own `hair=False` (the body presets with long hair do this, and the hair leaves with the head when an effect takes the head apart).

**Dark silhouettes on bright skies** (p03, p04, p05). Light can only brighten, so a dark figure on a day sky is made two ways, both in the existing passes: a flat fill of the figure's silhouette (`Mask("sky", sky="flat", color=<display hex>)`, crisp below `soft` 2.5, hiding the lights behind it), and painted particles for everything that leaves it (`paint=1`, the batch colour shown exactly). Effects take `batch=` for this (below). At night the same silhouette stands against `stylekit.Backdrop`, a soft glow kept behind the figure as the camera sees it, with a thin rim.

**Engine changes for this section** (all backward compatible: a song that uses none of them renders as before; `test_p3d_bodies` gives the same bytes at six moments with and without them):

- Two new sprite kinds (`engine/p3d/api.py` KINDS): `"shard"` (a sharp triangle or quad, a different one per seed: a faint body, bright edges and a reflection that sweeps across as it turns; `rot` turns and tumbles it, it flares when it faces the camera; painted it is a dark piece of glass) and `"butterfly"` (a butterfly seen from above, two pairs of wings beating; `rot[:, 0]` its heading in the picture, `rot[:, 1]` tilts it).
- A new window fill `Mask("sky", sky="nebula", color=<the light's colour>, glow=dict(at=<world point or function of t>, strength=1.0, density=0.5, scale=1.0))`: deep billowing clouds, slate in shadow, lit from a light inside them (placed at a world point and followed on screen), hot round it, a dark blue gulf with a few stars between the clouds. `scale` 2 gives clouds twice as fine (use about 2.4 for a whole body, 1 for a head). `glow` may also be `(x, y, strength, density)` in half heights of the shape from its centre.
- The mask pass: a masked set that draws no shape this frame (not on screen yet, or gone) no longer takes one of the frame's two sky layers (before, a figure that had not appeared yet could push a visible one out).
- Effects (`engine/p3d/effects.py`): any effect takes `batch=dict(...)` merged into every batch it draws (`paint=1` for dark painted flakes), or a list of dicts to draw each batch once per dict (a dark painted shard and its edge of light); Release effects take `sprites=(("shard", share, size, emit), ...)`; shards and butterflies tumble like flakes.
- New point sets in `engine/p3d/stylekit.py`: `Dressed` (a set with settings on every batch), `Backdrop`, `Butterflies`, `Sparkles`, `GlitterMist`, `CloudPuffs`, `Flock` (birds for a figure that is not a Body), `Billows` (a cumulus round the back of a head, for a silhouette only), `PaintedShape` (a silhouette of painted discs), `Nothing`.

**Limits** (what is weak):

- Faces are in profile only and read best side on; there is no front or three-quarter face. The eyes are always closed. Only two drawn heads (a woman, a man); a child's profile is not drawn.
- A frame holds one dark silhouette layer and two sky layers. Presets with a flat silhouette of the same colour share a layer; different colours, a nebula and a starry window together exceed it (the third is left out with a warning): use `silhouette="paint"` for the extra figures. Painted silhouettes do not hide the lights behind them.
- The nebula and the starry window are screen-space fills (they follow the figure but do not turn with it); the clouds have no real depth. Billows round a head are round blobs and can look like a bunch of bubbles from far.
- Flowing hair lies on a circle round the skull: on a Body seen from the front or behind it can stand off the head. It does not collide with the shoulders.
- Body presets inherit the body's motions: the "dance" clip of `ember_dancer` is a sway, not a leap.
- On a bright sky the world's own dust shows as white specks over a dark fill: lower `dust` in that look.
- `mist_figure` needs the world's mist and a warm light on one side (world keys) to look like p09; the preset only brings the figure and the glittering slab.
