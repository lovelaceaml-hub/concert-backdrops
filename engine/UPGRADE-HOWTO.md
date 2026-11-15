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
- `lift` (default True, or a time): once all are lit, everyone lifts their light. `rise` (default True): then each light rises to the nearest light of the arch. `arch` (default 1.0, 0 = off): the arch brightens as they arrive (a band of light through the nine lights). To also switch on the nine lights themselves, give PHRASES `star` times around then (the demo does).
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
- **Not moved by the camera**: text of any kind, the arch of nine lights, and the drifting air layers (the song's motes, lanterns and petals, SNOW, BUBBLES, LEAVES, the beat sparkles). The effect layers that are painted in the composite or fill the frame (ICE, SHARDS, GOLDEN_FIELD, NET, BEAM) are not moved either: do not combine them with a camera move.
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

**Order of drawing** (render.py, one frame): sky, 3D clouds; then light: stars, motes, lanterns, petals, effect layers (snow, bubbles, leaves, beam, net), nature, creatures, beat sparkles, people of light, the crowd, ripple light, falling stars and symbols, god rays and near motes; then the text protection dims all of that behind the words; then the words, the credit and the arch; glow; the camera background; the composite (plates, ripples bending the lake, ice, shards, field, nature paint, leaf tint, coloured letters).

**What stays exactly as before.** A song file that uses none of the new keys renders bit for bit as on main: `s03_original` on its promo clip was compared pixel by pixel at 25 and 45 seconds. For that, each optional block of the composite shader (`SKY_THEME`, `TEXT_SHADOW` below 0.05, per-text colour, leaf tint, lake ripples, nature paint, camera background) is compiled in only for a song that uses it (`render.comp_blocks()`, `shaders.comp_fs()`). When you add a block to the composite, add it the same way: the same maths written with a uniform in place of a constant is rounded differently by the shader compiler, which changes a few pixels by one level.

**Texture units of the composite**: 0 to 9 the engine's own (sky, light, four glow levels, ridge, text A, text B, credit), 10 and 11 scene plates, 12 leaf tint, 13 nature paint, 15 the camera background. 14 is free. Every other pass binds its own textures from unit 0 just before it draws.

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
