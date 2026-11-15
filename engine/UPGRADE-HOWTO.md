# How a song file uses the engine upgrade

Built 2026-11-13 for Anthony's request: "make sure the full expressions a created and used beyond only using current engine effects. Do not be lazy. Make these videos magnificint. They shouldnt just look like one scene but multiple things should go based on the theme".

Everything below is optional. A song file that sets none of it renders exactly as before. The working example that uses every feature is `engine/songs/demo_upgrade.py` (60 seconds, rendered with the song 04 promo clip).

Section E lists the shared fixes from Astra round 1 (text protection, calm lower third, ring history, strict Tracks, the three-line end card) and the share copy.

Times are seconds into the video. A "Track" is the timeline helper (new files: `from track import Track`): `Track([(t, value), ...])` eases smoothly between keys. Any setting below that takes a number or a pair can also be a Track or a function of time. Colors are `"#rrggbb"`.

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

## J. Text animations (2026-11-15)

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
- Engine test song: `engine/songs/test_text_anims.py` (song 03 timeline, every animation once; stills with `audio/test/silent-60s.mp3`).
- Code: `engine/text_anims.py` (shaders and preparation); `engine/render.py` only hands such texts to it.

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

**`SKY_THEME`** (default none = the original world): `"campaign_day"` (or a number 0..1, or a Track) makes the procedural world bright: the far and near hills turn a pale blue-peach haze instead of dark ridges, the lake stays light toward the bottom, and the vignette is much lighter (corners 0.90 instead of 0.62). Plates (SCENES) are not changed by it.

**Per-text colour.** Add `color="#rrggbb"` to any PHRASES entry, the `TITLE`, the `TAGLINE` (end card lines), any FRAGMENTS entry (every style) or `CREDIT`. The letters are then painted in exactly that colour on top of the finished picture, revealed and dissolved with the same timing as the light words, and the light layer carries only a soft glow round them (and the forming sparks take the glow colour). Extra keys: `glow="#rrggbb"` (that text's glow; default `GLOW_COLOR`, else the warm #ffc48c), `glow_strength` (default `GLOW_STRENGTH`, else 1.0), `color_alpha` (0..1, default 1). Without `color`, a text keeps its light letters; `glow` and `GLOW_COLOR` then only change the glow colour.

- `GLOW_COLOR` (a hex, or a function of time): the glow colour of every text that does not set its own `glow`. Navy words: a soft white glow (#fff8ec). Coral words: gold (#ffd27a).
- `GLOW_STRENGTH` (default 1.0): how strong the glow round coloured words is.
- Dark words need a bright sky behind them: use them with `SKY_THEME` or bright plates. Leave the light words on night scenes.

**`TEXT_SHADOW = 0` is now truly zero.** Before, 0 still capped bright scenery behind the text and darkened round the corner credit. Now, at 0 there is no cap, no veil and no dark round the credit. From 0.05 up the result is exactly as before (every existing song uses 1.0 or more); between 0 and 0.05 it eases, so a Track can fade the protection out without a jump. `TEXT_PROTECT` (dimming the light layers behind the letters, so no bubble, leaf or spark crosses a word) is separate and stays on.

**`BUBBLES`** (Track, 0 = off; the number is the share of about 140 bubbles shown): iridescent soap bubbles rise slowly, wobbling, each with a thin bright rim, a rainbow sheen that swirls round the rim, a faint film and two soft highlights. Far bubbles are small, near ones large. They thin out in the calm lower third under `BOTTOM_CALM`, and text protection keeps them out of the letters. Settings: `BUBBLES_COLOR` (rim and film, default #f4fbff), `BUBBLES_SIZE` (default 1.0; 1.0 is 26 to 118 px at 1080p), `BUBBLES_SPEED` (default 1.0), `BUBBLES_SHEEN` (rainbow strength, default 1.0), `BUBBLES_COUNT` (default 140, a plain number).

**`LEAVES`** (Track, 0 = off; share of about 48 leaves): a few leaves of light drift down slowly, swinging, turning and tumbling edge-on and back, with a bright rim, a pale vein and a glint as they face us. Settings: `LEAVES_COLORS` (pair, default green #5fd040 to gold #d8e860), `LEAVES_SIZE` (default 1.0: 30 to 92 px), `LEAVES_SPEED` (default 1.0), `LEAVES_WIND` (sideways drift, default 0.4), `LEAVES_COUNT` (default 48). Calm lower third and text protection as for bubbles.

## Rendering

Unchanged: commit and push the song file and its assets (plates and figures are in the repo under `assets/`, so the cloud workflow has them), then run the Render workflow (stills first, then video). See docs/HANDOFF.md.

The video run's finish job uploads three artifacts: "<name>" (the full 1920x1080 video plus a silent copy), "<name> frames" (4 frame sheets of 8 frames each, for checking without downloading the video) and "<name> (share)" (the file "<name> (share).mp4": 1280x720, H.264 with AAC sound, always under 25 MB, for phones and messages; the job fails if it would be larger).
