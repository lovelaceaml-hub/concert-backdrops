# Phase B: build and render your film, fast

Anthony: "I need the videos as quickly as possible." Speed is now the first priority. A complete, beautiful, watchable 60 s film delivered soon beats a perfect one later. Get a first full video out, then improve it.

## Read
- Your film's phase A plan: scratchpad/ten/NN-*.md, and the treatment and timeline in your song file on your branch `ten/NN-...` (engine/songs/ten_NN_*.py).
- scratchpad/P3D-BRIEF.md (direction, reference photos in refs/, house rules, Anthony's words, camera approval, model rule), scratchpad/EPIC-BRIEF.md (mechanics), scratchpad/TEN-FILMS.md (all ten ideas and the rules every film keeps).
- The engine as it is today: engine/UPGRADE-HOWTO.md sections V (3D layer), W (particle bodies), X and X2 (particle words) on origin/engine-p3d-words, plus the module docstrings in engine/p3d/. The handover notes in scratchpad/handover/ (CORE.md, BODY.md, WORDS.md) say what works, what is untested and the traps. Read the traps.
- The medley: audio/promo/concert-medley.mp3 on origin/epic-medley2; section map in scratchpad/medley2/SECTION-MAP.md. Sections start at 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 (breath to 42.51, then the biggest hit), 49.47; final hit 58.11. Time your film to these.

## Setup
`git fetch origin`. Check out your branch `ten/NN-...` in your worktree. Merge `origin/epic-medley2` (the medley) and `origin/engine-p3d-words`. The words branch is kept up to date with the 3D layer and the bodies merged in, so it is the one engine branch you need. Re-merge it whenever it moves (`git fetch origin` then `git merge origin/engine-p3d-words`); three Opus helpers are improving the engine right now and push often. Never `git add -A` (`fonts` is an untracked symlink). Run git as separate plain commands.

## Build
- Make your plan real in your song file, using what the engine has today. Where your plan needs something the engine does not have yet, build a simple version of it yourself inside your own files (your song file, or engine/p3d/ten_NN_*.py for helpers of your own) rather than waiting. Do not edit shared engine files; if you find a real engine bug, work around it in your files and say so in your report.
- Keep every house rule: no facial features (profiles are featureless silhouettes), everyone clothed in garments of light, Heavenly Mother only from behind or as hands, all nine expressions with exact wording (use `words.EXPRESSIONS` by name, never retype), each with a clear reading moment of about 2.5 s or more and legible on a phone, the end card with the concert details readable at least 4 s, nothing dark behind text, no lyrics, no em or en dash anywhere, no fade to black at the end, frame 0 not black.

## Render (fast path)
1. Stills here, with the shared script: `/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/tools/local_render.sh WORKTREE SONG audio/promo/concert-medley.mp3 stills "list" OUTDIR` (OUTDIR in your scratch folder, e.g. scratchpad/tenB/NN/...). About 12 to 20 moments per round; look at every still at full size. At most two still rounds before your first draft.
2. Drafts on GitHub (faster than the shared machine for whole songs): push, then `gh workflow run render.yml --ref ten/NN-... -f song=ten_NN_... -f audio=audio/promo/concert-medley.mp3 -f mode=draft -f name="Film NN draft K"`. Get the run id with `gh api "repos/lovelaceaml-hub/concert-backdrops/actions/runs?branch=ten/NN-...&event=workflow_dispatch&per_page=1" --jq '.workflow_runs[0].id'`, then exactly one `gh run watch <id> --exit-status --interval 60`. Download the draft artifact into your scratch folder; check motion with dense frame strips (ffmpeg) and the QA report. Usually one or two drafts.
3. Full video on GitHub: `-f mode=video -f name="Film NN, <Title>"` (no parentheses in names). One `gh run watch`. Then look at every frame sheet and read the QA report.
4. Report right away (see below). Do not wait to polish before reporting your first full video. After reporting, stop; I will send notes for a second pass.

If the GitHub workflow refuses because the 3D layer is not on the workflow's branch: it runs from your branch, so it has whatever you merged. If a run fails, read the log (`gh run view <id> --log-failed`), fix and re-run once.

## Commit and report
Commit messages end with:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01DSHsMeB7ain7qg3RYXYMEW

Report as text (no report files), concise: branch head; the full video run id and artifact names (full, share, frames, QA); the QA result; three things you are proud of and three you would fix next; any engine bug you worked around.

## UPDATE from Anthony: "Make the renders first"
Render first, polish after. New order, replacing the render steps above:
1. As soon as your song file imports and covers the whole 60 s (every section, all nine expressions, the end card), even roughly: one quick local still at 3 or 4 moments only to catch a crash or a black frame (no full stills round).
2. Push and dispatch the full video on GitHub right away (mode=video, name "Film NN, <Title>"), and report its run id to the coordinator as soon as it is dispatched (SendMessage is not available to you, so put it in your report; see below).
3. While it renders, keep improving. When it finishes, look at the frame sheets and QA, then report. Do not run a draft before the first full video.
Report as soon as the first full video is done; the coordinator sends it to Anthony at once. Then stop; a second pass comes after his reaction.

## UPDATE 2 from Anthony: "I want the final versions, not rough in places"
This replaces "report as soon as the first full video is done". Rendering first stays: the early full video is how you SEE the film fast. But you report only a FINAL version.
Loop until final:
1. Render the full video early (as in UPDATE 1).
2. Study it hard: every frame sheet, dense frame strips (ffmpeg, 10 to 15 frames a second) across every move, every word's arrival, reading moment and leaving, every body, every section change, the end card; the QA report. Be your own harshest critic against the reference photos and the quality bar: is every second beautiful, clear, alive and exciting? Anything stiff, blobby, cluttered, washed out, unreadable, jittery, popping, sliding, empty or cheap is a flaw.
3. Fix every flaw you found; check the fixes with local stills (and short local frame chunks for motion); re-merge origin/engine-p3d-words to pick up engine fixes; render the full video again.
4. Repeat until you find no flaw worth fixing. Aim for two or three full renders; take more only if it is clearly not yet final.
Then report the final version only, with: run id and artifact names; what you checked; and any remaining imperfection you know of (be honest; the coordinator also reviews every final before it goes to Anthony).

## UPDATE 3 from Anthony: "The concert title and the date should show from the beginning and throughout the videos"
Every film shows a concert badge from frame 0 to the end card, the same in all ten films. Use the engine's existing corner credit (CREDIT plus credit_state, as in engine/songs/demo_gathering.py; it is drawn by the 2D text pass on top of the 3D layer):
```
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0,          # fully visible on frame 0 (it is the thumbnail)
              t_move=1.6, t_rest=2.8,         # starts large in the centre, settles into the corner by 2.8 s
              scale=0.48, alpha_rest=0.92,    # large enough to read on a phone; nearly full strength
              margin_x=0.035, margin_top=0.05)
```
plus the credit_state function copied from demo_gathering.py. Rules:
- Corner: top left by default. If your film's expressions or hero images sit there, put it bottom left instead (add your own variant of credit_state that anchors to the bottom margin), but keep one corner for the whole film.
- It must never be covered: keep every expression's reading box, every person and every burst clear of the badge. Text protection keeps light out of its letters; check it in stills. Nothing dark behind it (TEXT_SHADOW = 0).
- Readable on a phone: in a 1080p still the date line's capital letters must be at least about 22 px tall. If your font fit makes it smaller, raise scale up to 0.6.
- From the moment the end card starts forming, fade the badge out over about 1 s (the end card carries the same information). Do this by ending alpha in your credit_state at the end card's start time.
- Colour: the default warm white glow on night skies; on bright day skies use color navy (#1f2a6b) with a soft white glow, as for words (CREDIT accepts color and glow like other texts).
- Frame 0 must show the badge large and readable over a striking first image.

## UPDATE 4: the flaws the coordinator keeps finding (check every one before you render)
Seen in renders of several films. Check your film for each, with dense local frame strips (10 to 15 frames a second) around every word, flare, burst and sky change:
1. White-outs: no frame near full white, ever (flares, sunrises, suns, orbs, bursts, transitions). Keep highlights under clipping; a bright moment is warm gold or a bloom on a still-visible scene, not a white screen.
2. Words on bright skies: white text on a pale, gold or cream sky is unreadable on a phone. Use navy #1f2a6b with a soft white glow there (the badge too), or deepen the sky behind the words.
3. Things crossing words: no person, ribbon, streak, lightning bolt, burst, flare or particle cloud inside an expression's reading box (label included) during its reading moment, and nothing over the badge, ever.
4. Two expressions at once: only one expression reads at a time, unless they are clearly apart and each still has its own clean reading moment.
5. Garbled glyphs: a word forming or leaving must never show scrambled or distorted letter shapes, or a row of broken letters, in a sheet frame.
6. Mirrored text: no words reflected in water.
7. People: every person is a luminous particle body; never dark, brown, bronze, solid or mannequin-like, and big enough to read.
8. Empty frames: no frame of only sky or a lone streak in the high-energy medley; every section keeps a hero image.
9. Blur: a quick motion blur is fine, but no frame reads as mush.
10. Keep a gap of at least about 40 px at 1080p between every expression box and the badge.

## UPDATE 5 (HOLD): Anthony on the people, new direction coming
Anthony: "make the people look less weird. Hands were too stiff. Model expressions were weird or out of place like running when it says I'll pray for you or just random poses. They need to be related and showing the expression. There needs more diversity, even within the people's designs. You need to get way more creative with showing the expressions in act and how the people are designed. Use different types of artistic expression for the people. ... Do not bind yourself to one way of showing people. Half, full, partial, far, close, many, few, none, etc."
New references: scratchpad/refs2/p01 to p09 (constellation wireframe body, star-filled silhouette with butterflies, figure dissolving into ash, dancer bursting into embers, figure shattering into glass shards, profile outlined in sparks, profile filled with clouds and nebula, figure of gold glitter dissolving, small sparkling figure in mist).
Until the coordinator sends the full direction: keep fixing UPDATE 3 and 4 items, but do not polish people, poses or hands, and do not dispatch a new full render.

## UPDATE 6: the new direction for the people (replaces the HOLD in UPDATE 5)
Anthony chose to go deeper on five films: 04 Windows, 06 Ascension, 07 The Relay, 08 Storm to Peace, 10 Nine Colours. Films 01, 02, 03, 05 and 09 are parked.

### What Anthony asked for
- People that do not look weird; natural, living hands (not stiff presets).
- Every pose must ACT OUT the expression on screen. No random poses, no running while "I'll pray for you" reads.
- Much more diversity, also within one film: different artistic styles of people, different framings and numbers. "Do not bind yourself to one way of showing people. Half, full, partial, far, close, many, few, none."
- New references: scratchpad/refs2/p01 to p09 (as well as the original refs/).

### Rule change: artistic faces are now allowed
Anthony: artistic faces are OK (his earlier "no faces" was about photorealistic AI images). Features may show in artistic form: a profile edge with nose, lips and closed eyes (p06, p07), a face of stars, glitter, cloud or embers. Never photorealistic. Heavenly Mother is unchanged: only from behind or as hands.

### Act out each expression (pick and vary; make your own if better)
The person or people on screen DO the expression while it reads, and their style and framing change from one expression to the next.
| Expression | Acted as (ideas) |
|---|---|
| Greeting "How are you?" | someone turns at a touch on the shoulder; a warm wave across a distance; two people meet and one leans in; close-up of a face lighting up |
| Gratitude | hand on heart and a bow; clasping another's hands in both of yours; offering a small light as a gift; a whole crowd bowing |
| Apology | head bowed with open hands low; a hand laid gently on a back; one person kneels beside another who sits |
| Inclusiveness "It's okay. I understand." | an embrace; an arm round the shoulders; a circle opening to take someone in |
| Concession "Please, after you." | stepping aside with an open palm toward a path or a door of light; a line of people parting to let one through |
| Respect "I'd love to hear more about your thoughts." | two people seated, leaning in, listening; a nod; a profile turned attentively toward another |
| Encouragement "I'll pray (or root) for you." | kneeling with hands joined in prayer; a hand on the shoulder of someone kneeling; a crowd raising lights for one person |
| Consideration "Can I give you a hand with anything?" | helping someone up from the ground; carrying a load together; reaching down to lift a child |
| Compliment "You're amazing. You're doing great!" | applause; lifting someone up; a joyful jump or twirl; a crowd cheering |
"None" is allowed too: an expression may be acted by light alone (two lights meeting and merging, a door of light opening) if the moment is clear.

### Styles of people (mix them; no film uses only one)
constellation or plexus wireframe (p01, refs 03 and 12); a profile outlined in sparks (p06); a profile or body filled with a sky, nebula, sea or sunrise (p07, refs 08 and 02); a star-filled silhouette with butterflies or birds (p02); gold glitter dissolving (p08); a figure dispersing into embers mid-dance (p04); a figure dissolving into ash or flakes (p03, ref 13); a figure shattering into glass shards (p05); a small sparkling figure in mist (p09); hands of light (refs 04 and 14).
Framings: extreme close-up (a face in profile, two hands), half figure, full figure, partial (shoulders and a hand), far (tiny figures on a vast shore), few, many (a crowd), none.

### Engine support (coming on origin/engine-p3d-words; re-merge often)
- BODY2: natural animated fingers and wrists, acted gestures with anticipation and follow-through instead of crossfades, and an expression-to-performance library (engine/p3d/acting.py) with the table above as ready-made solo and pair performances.
- STYLES (new helper): named style presets for all the styles above, including glass shards, butterflies, dark painted silhouettes on bright skies, true nebula fill and artistic faces in profile.
Until they land, use what exists (gestures: pray, bow, embrace, offer, hand_on_shoulder, kneel with hands="pray", helped_up and pull_up, clap, listen; looks: plexus, rim, window fill, glitter, disperse, dissolve, birds) and swap in the new ones as they arrive.

### Process
Rewrite your film's acting plan first: for each expression, write what is acted, by whom, in which style and framing. Then build and render. Check every person in dense frame strips: hands alive, pose clearly tied to the words, no odd in-between frames. Keep every earlier rule and UPDATE 3 and 4. Loop until final (UPDATE 2) and report the final only.

## UPDATE 7: title and date, designed (REPLACES UPDATE 3; remove the CREDIT corner badge)
Anthony on the corner badge: "You just put the title in the left corner. You put no effort or thought into it. It looks out of place and distracting. You also didn't put the date. It doesn't need to always show the title and date. But it should be thoughtfully placed. It can be discreet."
He chose all three of these (mockups: scratchpad/titlemock/title_options.jpg, A_opening.png, B_signature.png, C_date_in_sky.png; the exact type sizes are in scratchpad/titlemock/mock.py):
- A, opening title (0 to about 4 s): centred lockup over the first image. "HEALING CONCERT" (Jost 500, tracked caps, gold) / "The Words of Mother's Love" (Cormorant Garamond 500, large) / a short gold hairline / "SUNDAY, DECEMBER 6 · 4:30 PM" (Jost 500 tracked caps, clearly readable) / "LAS VEGAS" (Jost 400, gold). Fully visible on frame 0 (the thumbnail), then it dissolves into the scene. Place it where the first image is empty (usually the sky); the first image is composed around it.
- B, discreet signature: small lockup in a quiet corner, right-aligned with a thin gold vertical hairline: "The Words of Mother's Love" (Cormorant italic) / "DEC 6 · 4:30 PM" (Jost 500 caps, the brightest line) / "HEALING CONCERT · LAS VEGAS" (Jost 400 gold). Shown ONLY in calm stretches between expressions, fading in and out over about 0.6 s; never at the same time as an expression, never over a person, a hero image or a burst. Choose its corner per stretch so it sits on calm sky or water. Two or three stretches per film.
- C, the date in light: "December 6" written in particles of light across the sky during the breath (40.21 to 42.51 s), with "HEALING CONCERT · 4:30 PM" small beneath; it forms in the quiet, holds readable for at least about 1.5 s, and bursts apart on the biggest hit at 42.51.
- The end card stays as it is.
Colours: warm white with gold accents and a soft warm glow on night skies; on bright day skies navy #1f2a6b with gold accents and a soft white glow. Nothing dark behind any of it.
WORDS2 builds this once in the engine (song key TITLES, see below) so all five films match. Until it lands on origin/engine-p3d-words, keep your film's times and positions in a TITLES dict and remove CREDIT when you switch over:
TITLES = dict(
    opening=dict(t_end=4.0, y=0.20, palette="night"),          # y: centre of the lockup, fraction of frame height from the top
    signature=dict(windows=[(a, b, "br", "night"), ...]),      # seconds, corner tl/tr/bl/br, palette
    date_light=dict(t_form=40.21, t_burst=42.51, y=0.30, palette="night"),
)

## UPDATE 8: the five films changed
Anthony: "Stop the relay and storm to peace. Use the waves and petals." The five films now are: 01 The Wave, 04 Windows, 05 Petals, 06 Ascension, 10 Nine Colours. 07 The Relay and 08 Storm to Peace are parked. UPDATE 6 (people) and UPDATE 7 (title and date) apply to all five.

## UPDATE 9: the title, the logo, hearts, the expression symbols and the world (Anthony approved the design)
Design sheet: scratchpad/titlemock/brand_design.jpg (full size: N4_opening, N1_expression, N2_world, N3_endcard, N5_signature, N0_symbols). Brand references: scratchpad/brand/ (logo_clean.jpg, logo_on_leaves.jpg, world_ref.jpg, icon_*.png, app_cards_*.png).
1. The concert title is "The Words of Mother's Love That Bring Peace", with the small HEALING CONCERT label above it. Set as two lines: "The Words of Mother's Love" / "That Bring Peace" (italic). Use it in the opening title, the signature, the date line and the end card.
2. The logo (two hearts, gold-orange and rose, with a white-gridded globe and two white olive branches) is shown: above the opening title, as a small mark in the discreet signature, and above the end card title. It also forms in the finale (point 5).
3. The expression colours are now the website's (they replace words.COLORS): Greeting #EA5A5E, Gratitude #F2B25E, Apology #F6CE46, Inclusiveness #5ABA5A, Concession #62B2FA, Respect #667AF6, Encouragement #9E6AF6, Consideration #EE62A6, Compliment #364E96. Labels may sit in a soft pill of their colour, as on the website.
4. The nine expression symbols (waving hand, bowing person, face with a tear, hugging face, "after you" gesture, listening hand at the ear, praying hands, two hands holding a heart, clapping hands) are redrawn as light. Anthony: "the expression symbols don't need to be prominent. They can be part of the scenery as effects." So never an icon over the words: the symbol appears IN the world, in its colour, briefly and subtly, around its expression: traced by fireflies or sparks, a constellation among the stars, a shape of petals on the wind, a ripple pattern on the water, a light trail drawing it, birds wheeling into it, glints in a window. Vary the way per expression.
5. More hearts: heart-shaped bokeh and sparks, hearts drifting off each expression in its colour, hearts formed by lights or by people's hands, hearts in the petals.
6. The world: the finale shows the Earth. The camera pulls back (each film in its own way: rising out of the scene, the wave reaching the horizon, ribbons wrapping the globe, petals carried across it, the last window opening onto it) to a luminous globe where hearts in the nine colours light up across the continents, joined by arcs of light. Then the globe settles between two hearts that sweep in, its grid lines and the olive branches draw themselves, and it becomes the logo, which rises into the end card. Time it to the music: last section from 49.47, peak image at about 54.3 to 55 (the logo forming), the end card readable from about 55 s to the end.
Engine support: a new helper, BRAND, builds the logo (vector and particle), the nine symbols as light (line sets you can place as scenery effects), heart sprites and shapes, the globe of light and the world-to-logo transformation, on branch engine-p3d-brand. WORDS2 merges it into engine-p3d-words and wires the logo and the new title into TITLES and the end card, and switches words.COLORS to the website colours. Plan your scenes now; use the pieces as they land.

## UPDATE 10: the end card follows the official campaign design (approved)
Mockup: scratchpad/titlemock/N6_endcard_official.png (beside the official poster: N6_side_by_side.jpg). Font Outfit (bold rounded, like the official poster), official colours: navy "The Words of", coral "Mother's Love", deep blue "That Bring Peace", a coral ribbon with "Sunday, December 6 · 4:30 PM", then the church and address. WORDS2 builds it into the engine's end card; just keep your end card stretch (about 55 s to the end) clear and calm behind it. The opening title and the signature stay in the elegant serif (N4, N5).

## UPDATE 11: TITLES has landed (origin/engine-p3d-words at 6abfb0f or later; keys in HOWTO section Y)
Switch now: remove CREDIT and use TITLES (opening, signature, date_light) and the new end card. The logo slot fills automatically when BRAND's logo lands. Rules from the coordinator's review:
- The end card needs a BRIGHT pastel sky behind it (it is navy, coral and blue type). Your finale must end in light: after world to logo (about 54.3 to 55 s) the frame blooms into a soft pastel day (cream, peach, sky blue), and the end card sits on it from about 55 s. Never put the end card over a night or space sky.
- Keep the opening lockup's area calm: no glitter bands, bursts or people behind the title letters.
- Use palette "day" on bright skies for the signature and the date in light.

## UPDATE 12 (HOLD on people styles): Anthony on the Styles proof: "Those look terrible and scary."
Until new direction: do NOT use dark painted silhouettes, glass shatter, ash dissolve, dissolving or breaking heads, glowing eyes, or any person that falls apart. Do not adopt engine-p3d-styles presets. Keep working on everything else (TITLES, acting, words, the world finale, fixes); people stay warm, luminous and whole.

## UPDATE 13: the true bar (replaces the HOLD in UPDATE 12 and the style list in UPDATE 6)
Anthony: "The point is the entire thing is supposed to look majestic, beautiful, awesome, brilliant, extravagant, beyond imagination, heavenly, expressive. The designs, art and animation should be so breathtakingly beautiful that emotions are felt."
He found the dark, breaking-apart styles "terrible and scary". Closest to what he wants: the glass-like light people (The Relay's crystal people handing on the light), warm gold glitter people, and "fewer people, more light".

The bar for every second:
- Heavenly and majestic: vast radiant skies, cathedral shafts of light, golden and rose clouds lit from within, rivers and oceans of light, aurora curtains, blossoming light, prismatic glints, a sense of glory and wonder. Rich warm colour, depth and grandeur. Never dark, cold, empty, eerie or decaying.
- People: only two looks, both radiant and WHOLE. (a) Crystal light people: clear glass-like bodies with inner light, prismatic edges and sparkle. (b) Warm gold glitter people: bodies of glowing gold particles. Light may stream from them as trails, sparkles or blooms, but a body never shatters, crumbles, turns to ash, goes dark or falls apart. No dark silhouettes, no glowing eyes. Faces stay soft and luminous.
- Fewer people, more light: people appear in a few meaningful, tender, acted moments (an embrace bathed in gold, a hand lifting someone up, a kneeling prayer under falling light). Hands, lights, hearts, the symbols, nature and the sky carry the rest.
- Emotion: every moment should move the viewer: tenderness, joy, awe. Graceful, flowing animation; sweeping camera; slow-motion majesty that still rides the medley's energy.
- Everything else in UPDATES 2 to 11 stands (acting, the nine expressions, titles, the logo, hearts, symbols as scenery, the world finale, the end card on a bright pastel sky, no white-outs).
Do not adopt engine-p3d-styles until the coordinator says so; STYLES is now perfecting just the two approved looks.

## UPDATE 14: one masterpiece; the five films stop
Anthony chose: engine only (no AI video), and ONE masterpiece first: a new film built around the theme, taking the best of all five. The five film builders stop now. Before stopping, each pushes its branch and writes scratchpad/handover/film_NN.md: what on your branch is worth reusing in the new film (scenes, helpers, effects, camera moves, tricks; file and function names; the exact moments in your renders that look best, with times) and what to avoid.

## UPDATE 15: Anthony on who acts the greeting and the embrace
"Male & male for greeting by slightly bowing to each other. Female & female for embracing."
- Greeting ("How are you?"): two men facing each other, each giving a slight, warm bow (a gentle nod of the head and shoulders), not a handshake or an embrace.
- Embraces (Inclusiveness and any other embrace): two women only.
- Every touching moment is between two people of the same gender (woman with woman, man with man): hand on the shoulder, helping up, holding hands, clasping hands, embraces. The only exception is family: a parent with a child (for example lifting a child into arms). Mixed groups are fine when no one touches.

## UPDATE 16: Anthony on the masterpiece (v3): word position, concert info at least 7 s, quiet start
- Expression words sit in the upper middle (block centred about a third of the way down), people below them.
- Concert information never flashes: every appearance holds at least 7 s. Opening title holds 7 s or more from frame 0; a discreet signature (logo mark, title, DEC 6 · 4:30 PM, HEALING CONCERT · LAS VEGAS) stays on continuously from the opening's end to the end card; the end card holds 7 s or more to the last frame. The 2 s "December 6" date in the sky is dropped.
- Sound: about 2 s of near-silence over the opening image, then the medley fades in over about 1.5 s; the film becomes about 62 s (audio/promo/concert-medley-leadin.mp3).
- Finale (Anthony): the hands holding the Earth "look extremely weird". No hands at the end. Instead the nine expression symbols, as light in their website colours, swirl around the Earth as a build-up, illuminating the world, then disperse for the final scene (world to logo, bloom, end card). The opening hands holding the golden drop stay.

## UPDATE 17: Anthony on v6: abrupt songs and transitions, choppy animation, abrupt end
Plan (approved): new 7-song medley with 2 to 3 s phrase-aligned, tempo-matched blends and a natural 4 s+ ring-out (audio/promo/concert-medley7.mp3, MEDLEY3); then MASTER3 re-times the film to it, keeps the energy but smooths every fast whip and dive (eased, longer, more motion blur, speed cap), fixes the Respect sparkle flicker, keeps the end card alive (slow push-in, drifting sparkles, glow on the final chord, easing to stillness), and renders at 60 fps with a 60 fps share copy.
- Anthony on the people: "The people movement and their expressions need to be much more refined. Some look very weird like #3 putting arms on the other and #9 arms bent weird." (Apology: a stiff straight arm thrust at the other's head and a stray foot; Compliment: hand on hip, angular elbows.) All nine acted moments get refined: natural, graceful, eased; tender and simple over complex and wrong.

## UPDATE 18 (2026-11-16): Anthony after v7: theatrical, mix with Nine Colours
"It's perfectly fine for the effects to show behind the signature. The scenes should transition more and more theatrical. Mixing the style with the attached video would be best. Not every scene needs people. And I really like the traveling effect and the style and effects for the text." (Attached: Film 10 Nine Colours render 1, run 43726203825.)
v9: the nine comet ribbons are the film's travelling thread (rollercoaster run, hoop gates, helix, braking spiral, dancer loop, hyperspace braid at the lift, globe wrap); transitions escalate in theatre through the film; words written by their comet pens in Film 10's text style; two or three expressions carried by light alone; effects may pass behind the signature. All smoothness, acting, timing, titles and end-card rules stay.

## UPDATE 19 (2026-11-16): Anthony after v9: "It needs to flow more like" Nine Colours render 1
He chose: never stop moving (one continuous ride; every acted moment and its words happen as we fly past, alongside or around them; no stop-and-hold) and faster, more energy (pace near Nine Colours, still smooth). The 7 s opening hold stays. Targets: mean frame diff per 1 s about 7 to 9 (v9 5.3, Nine Colours 8.3), near-still windows under 10% between 7 and 55 s, peaks only on hits. Plus the v9 polish list.

## UPDATE 20 (2026-11-16): Anthony: remake Nine Colours render 1 with every improvement
"The video concept and song for Nine Colours is the best. Basically make the same video but with all the improvements such as better models and animation, the text additions, beginning and ending cards, etc."
Choices: the original 8-song medley with the 2 s quiet lead-in (audio/promo/concert-medley-leadin.mp3, 62 s); Nine Colours' moving opening with the full title readable on top for 7 s; v10 finishes as a comparison. Build: engine/songs/nine_colours_final.py on master/words-that-bring-peace, porting Film 10 r1 (run 43726203825, ten/10-nine-colours d928ff9) cue for cue (+2.0 s), plus gold glitter refined acting and casting rules, comet-pen words with pills, the signature, symbols, hearts, BRAND finale, the official end card, 60 fps and smoothness.

Status: Nine Colours Final v1 rendered (run 43855882765, master/words-that-bring-peace f43f451). Coordinator review: title over the moving opening 0 to 7 s, signature on, pills and words upper middle, end card whole 55 to 62 s, never still from 7 to 55 s (mean 6.7, median 5.1 per 1 s; 6 jump frames against 96 in r1). Open items: the Concession hoop crosses "Please, after you." at about 12.6 s; Greeting men, Consideration pair and the praying figure too small; the Apology pair cut off at the bottom edge; the world sits in the lower left on the signature at about 52 s; the song still ends with a 1 s fade (no ring-out); the end card motion is very low.
