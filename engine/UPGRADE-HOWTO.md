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

## Rendering

Unchanged: commit and push the song file and its assets (plates and figures are in the repo under `assets/`, so the cloud workflow has them), then run the Render workflow (stills first, then video). See docs/HANDOFF.md.

The video run's finish job uploads three artifacts: "<name>" (the full 1920x1080 video plus a silent copy), "<name> frames" (4 frame sheets of 8 frames each, for checking without downloading the video) and "<name> (share)" (the file "<name> (share).mp4": 1280x720, H.264 with AAC sound, always under 25 MB, for phones and messages; the job fails if it would be larger).

## I11 Draft mode and the automatic quality check (branch engine-qa)

**Draft mode** renders the whole song fast, to judge timing, layout and motion before a full render. It is not for showing anyone.

- Run the Render workflow with `mode=draft` (same song, audio and name inputs). It renders 640x360 at 15 fps in 8 parallel parts, with half the particles, then joins them with the music.
- Artifacts: "<name> (draft)" holds "<name> (draft).mp4" (a few MB) and "<name> (draft contact sheet).jpg" (30 frames over the whole song, each labelled with its time); "<name> QA" holds the quality report.
- Engine: `engine/draft.py`. `DRAFT=1` in the environment is the flag; `import draft` then `draft.DRAFT` (true in a draft) and `draft.n(count)` (a particle count cut to the draft share, `DRAFT_PARTICLES`, default 0.5) let any layer draw less. Without any change in a layer, the draft already draws only that share of every particle buffer (stars, motes, lanterns, petals, words, figures, snow, fragment sparks and any new layer hung off the renderer), and every full-screen shader does a ninth of the work at 640x360. Normal renders are untouched: no engine file outside `engine/draft.py` changed.
- By hand: `cd engine && DRAFT=1 python draft.py --range 0 900 --out draft.mp4`, and `python draft.py --sheet draft.mp4 --out sheet.jpg`.

**Quality check** (`tools/qa_check.py`) runs on every stills run (report inside the stills artifact), at the end of every video run (on the share copy, artifact "<name> QA") and on every draft. It writes `qa-report.md` (plain words, a table of issues with HIGH, MEDIUM, LOW) and `qa.json`, adds the report to the run's summary page, and marks HIGH issues as errors and MEDIUM as warnings in the run. The workflow input `qa` is `flag` (default: report only), `fail` (the run fails on any HIGH issue, after the artifacts are saved) or `off`.

It uses the engine's own text layout (it imports the song file and engine/text.py), so it knows where every word sits and when it is fully formed. What it checks:

- Dark behind text: the sky in a ring 30 to 130 px round the letters against the sky 140 to 260 px out, in the same rows, open sky only (above the ridge), using the darker quarter of each ring so stars do not count. Under 0.85 is MEDIUM, under 0.70 HIGH (tuned: the v4 songs 04 and 07 measure 0.88 or more; the song 08 end card veil measures 0.60).
- Legibility: the letters against the brightest tenth of the light round them; under 2.2 is MEDIUM, under 1.6 HIGH.
- Reading time (from the song file): each expression fully formed (form + FORM_DUR + 0.75 s) for at least 6 s; fragments 3 s; no fragment over an expression; a 0.5 s gap between texts.
- End card: three lines under the title, whole for at least 4 s before the fade.
- Calm bottom third: frame differences in the bottom third against the rest, per 2 s (people of light left out).
- Static figures: a painted figure with one picture and no warp that moves across the screen is HIGH (it slides as one rigid picture); living figures (kind="rig") and warped ones (warp=True) are never called rigid. Frames inside each figure's box confirm it moves; a still painted figure frozen for 4 s or more is MEDIUM. Checked on the living figures test (run 43692681296): no rigid flags; the rigid walker of song 04 and the swan of song 08 are flagged.
- Dashes: no em or en dash in the song file or its status file (project-docs/status/NN.md).
- Length: the video is as long as the song file says.

By hand (repository root, fonts from tools/setup_fonts.py, ffmpeg): `python tools/qa_check.py --song s08_favor_from_god --video "<file>.mp4" --out qa` (or `--stills <folder>`, or neither for the song-file checks only). It takes under half a minute.
