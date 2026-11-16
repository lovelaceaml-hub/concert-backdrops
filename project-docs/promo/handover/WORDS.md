# Hand-over from helper WORDS (Fable) to its Opus successor

## Branch head
`engine-p3d-words` at b90cea5 (pushed). From origin/epic-promo 20b4f6e, with origin/engine-p3d merged at 5227b45 and origin/engine-p3d-bodies at a51583b. Both have moved since (engine-p3d to a1262fe or later, engine-p3d-bodies to a80d409 or later, and a new Opus helper BODY2 now pushes engine-p3d-bodies) and are NOT merged.
Files: engine/p3d/words.py, engine/songs/demo_p3d_words.py (35.5 s proof), engine/songs/demo_p3d_words_kit.py (directors' kit, 30.5 s), engine/UPGRADE-HOWTO.md sections X and X2.

## The nine expressions (words.EXPRESSIONS; a song names one with expr="Gratitude" or 1 to 9)
1 Greeting "How are you?" #FF977C
2 Gratitude "Thank you. It's all thanks to you. / You've worked hard." #FFD05F
3 Apology "I'm sorry. / It must have been hard on you." #FFAD69
4 Inclusiveness "It's okay. I understand." #F582AF
5 Concession "Please, after you." #82B0ED
6 Respect "I'd love to hear more / about your thoughts." #CE927E
7 Encouragement "I'll pray (or root) for you. / Everything will go well." #B293E7
8 Consideration "Can I give you a hand / with anything?" #EF7A96
9 Compliment "You're amazing. / You're doing great!" #BE9CEB
(curly quotes and apostrophes in the code). Sources: project-docs/DESIGN-SYSTEM.md section 5 (lines 49 to 57; "Full wording, never shortened. (or root) stays"); line breaks and quotes from PHRASES in engine/songs/epic_concert.py (490 to 509), matching s01_stars_of_zion.py (271 to 287). The proof also shows "Healing Concert" over "The Words of Mother's Love" from TITLE in epic_concert.py.

## Done and proven
- Cloud stills run 43720110929, artifact "p3d words stills 1-stills", commit 0175a70: 30 stills, all viewed at full size: crisp letters with coloured halo and label; two expressions read at once at two depths with lake mirror; nine arrivals (touch, palm, flock, petals, lake, shaft, gather, stars, rays); nine leavings (flock, petals, wind, arch, sink, rise, give, stars, bokeh) plus morph into the title; the nine arch lights waking as each expression becomes whole.
- No proof video exists.
- Motion checked only by a frame-difference scan at 480x270: one jump at the morph (28.77 s) and a flash at the end, both fixed; rescan clean. Nobody has watched it move.
- Since that run, local stills only: proof song 8 moments scratchpad/words/proof2/sheet.jpg; kit song about 25 moments over four rounds scratchpad/words/kit1 to kit4.
- Legibility: WORDS.check(camera) on the proof: smallest x-height 0.92 mm (Gratitude) to 1.44 mm on a 6 cm wide phone; label caps 0.58 to 0.91 mm; facing 0.95 or better; the two pairs read together stay apart.
- Numeric: scratchpad/words/t_cont.py confirms every arrival ends exactly on the letters and every leaving starts there (14 and 14 OK). Sampling 4 to 16 ms per word per frame.

## Keys (full tables in HOWTO X and X2)
Times t_in, t_read0, t_read1, t_out. Place pos, em or width, facing, face (fixed, camera, screen, flat), tilt, roll, curve, ride, bind. Motion arrive, leave, source, to, wind plus per-style options. Look color, glow, tint, bright, halo, sparkle, sharp, fog, n, n_label, label_size, font, window, ink, paint. Control drive, avoid, camera, name.
Helpers: PW.Words(specs, camera=, **common), .add_to(scene), .check(camera), .focus_point(t, default), .world(dict), .clear(points, t, cam), .keep_clear(t); PW.place, PW.em_for, PW.KeepClear, PW.COLORS; word.home(), .targets(), .frame(), .pen(t), .keep_clear(), .shaft(), .light().

## Half done
1. Proof video: demo_p3d_words.py ready for a video with audio/promo/s01.mp3; never rendered.
2. Star lines: last tweak (width 0.002 w, alpha 0.6, in _arr_stars) not rendered. Before (0.003, 0.9) was a heavy white scribble at 21.6 s; first state (0.0015, 0.55) too faint.
3. Kit features each seen in one or two stills, never in motion. Never rendered: reveal with gate=, carry="petal", "bird" and "soft" (only flake), windows other than "stars", tilt / facing / roll over time, a hand-sized word. Never exercised: drive= (end of Word.sample). Approximate: an external pen on a bind word (_pen_times).
4. BODY: only the skeleton merged. touch and palm use own emitters (two small comets, a spark), the person is CORE's StandIn. Hooks exist: source= takes a point, a function of t or a point set, so actor.palm(t)[0] works.
5. Window, ink and paint (_emit, mask(), _Lights) work but are bounded by CORE's mask: half size, blurs at least 3 px (layer.py starts soft at 3.0 and takes the max), one sky and one tint per frame; no flat fill, so paint is a dark base plus the word's own light, tuned to the day look only (paint_base). Asks for CORE: a flat fill, soft below 3 honoured, fill state per mask.
6. n is not chosen from on-screen size; HOWTO gives the rule by hand.
7. HOWTO: CORE's section V not in the file at the merge; X and X2 at the end; expect a conflict there, keep both sides.

## Needs list status
1 Home places: done (order within a glyph is left to right, not pen strokes). 2 Sharp mode: done and default (sharp=1, fog=0, no motion blur); remaining automatic n and a hand-sized test. 3 Anchors: rendered fixed, camera, ride, flat on the lake, bound to a moving wave; code only tilt / facing / roll over time; "beside a runner" is pos= a function of t, untried with a body; a veil fold needs BODY's cloth surface passed as bind. 4 Arrivals: pen (own and someone else's), reveal, stitch, weave, palm, petals and hanging rain rendered; flock from a given field (carry="bird") code only. 5 Departures: stream to a moving point, along a curve, into a body (StandIn), morph, doors, unravel and flock rendered. 6 Window words rendered within the limits above. 7 Colour: campaign colours done (tint=1.0); paint approximate. 8 Keep-clear box: done (a rectangle that dims to 12 percent); CORE's own stars and dust not wrapped.

## Traps
- The workflow's prepare job imports the song with numpy only: words.py must stay free of PIL and scipy at import; both, and text.py, load lazily; importing text early breaks on a circular import with song.
- ride and focus_point need a camera: build two rigs, one without the words' focus for layout and one with it (_LAYOUT and CAMERA in both demos).
- A common face="camera" in Words(...) overrides the ride default of "screen"; set face="screen" on the riding word.
- leave="morph": t_out ignored; the word is held until its successor's t_in.
- avoid=True is default: an arrival crossing a word being read is dimmed there; set avoid=False if wanted.
- Masked words return letters only with tiny alpha and raised emit on purpose; the rest comes from word.lights, which add_to adds.
- The shaft from WORDS.world() reaches down to the lake and stands behind any word read below it.
- The check knows only the words' boxes, not petals, birds or dust crossing them.
- Draft mode draws every second point of sets over 30000, so letters look thinner there.
- QA always reports 2 HIGH "no end card" on these test songs; expected.
- fonts in the worktree is an untracked symlink; never git add -A. Commands mixing a heredoc with git are refused; edit first, then run git on its own.

## Weaknesses
No video seen; flocks are a dense patch of chevrons; the opening two lights are plain compared with real hands; the petal storm is beautiful but very busy; the stars arrival has a blobby second before it clears; Gratitude sits at the phone limit (0.92 mm); lavender paint on cream has low contrast.
Scratch tools in scratchpad/words/: t_cont.py (continuity), pops.py (jump scan).
