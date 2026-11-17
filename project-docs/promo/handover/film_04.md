# Film 04 Windows: handover (branch ten/04-windows, head ff2d260; song engine/songs/ten_04_windows.py)

## Best moments (watch these)
Run 43734027135 (render 3, the acting version; artifact "Film 04, Windows (share)"):
- 0 to 6.8 s: a giant woman's profile (bust, scale 100) filled with a sunrise cloudscape, birds streaming in; at 6.84 we fly into her temple and come out inside that sunrise. Seamless.
- 7 to 13.3 s: a door of light standing on the water, its opening a window onto the teal sea; a man offers his open palm, a woman walks through first; we follow her through at 13.3.
- 15 to 18 s: a speaker's open hand sends an arc of light (a thought) to the listener's head (Respect).
- 20 to 26 s: the field of stars, the man thanked in the middle, a ring of gold glitter people bowing to him (Crowd).
- 28 to 32 s: two hands, gold from below and blue from above, clasp on 29.79 and lift (Consideration).
- 34 to 42.5 s: two kneel face to face in the rain; they rise and embrace; at 42.51 we fly into the embrace (best tender moment).
- 44 to 46 s: a woman kneeling in prayer, hands joined (glitter).
- 50 to 52 s: Heavenly Mother from behind, arms open, a silhouette full of stars with a globe inside her, birds pouring in.
Run 43738219489 (render 4, dispatched, NOT viewed): TITLES, the world finale (globe with hearts in nine colours, pastel day for the end card), crystal and gold people per UPDATE 13.
Local stills: scratchpad/tenB/04/r3b, r3c, r4a (globe at 52.8 to 54.6 s).

## The code (all in engine/songs/ten_04_windows.py)
- One unbroken flight through windows: each section has a local frame O_k = _after(crossing point, local start); keys via _keys(O, K). The camera's last key of a section sits INSIDE the person (head or chest, 1 to 3 m in front of its centre, measured with Body.where at X - 1/30 s; probe script scratchpad/tenB/04/probe_song.py). The next section starts at the same point, so the window (Mask "sky", sky="world", look=window_look) fills the frame at the cut and the world look cuts (blend 0) with no visible seam.
- window_look(t) / _WIN: the one world seen through every window in a frame (the next section's look). LOOKS: pearl, ember (sunrise clouds), sea, stars, stars_lit, harvest, rain (warm twilight), blossom, space, space_win, dayend (pastel).
- _Gate + _Lit: gate a Body to [t0, t1); its points fade 0.45 s before the crossing (no glitter blobs at the lens) while its window mask stays full (gate.gain drives Mask strength).
- _person / _add / _style: styles crystal (window + prismatic rim + glitter), crystal_light, gold, goldwin.
- Door: frame of light; its .fill is the Mask source (not drawn), so the opening is a clean window.
- Stream (thought of light between two moving points), Flock (birds from a field into one point, screen-heading rot), Motes (depth inside windows: add as window=True during the section before, normal after).
- _ground_point(t, sx, sy): place window-only actors so they appear inside a giant silhouette (the tiny greeting inside the profile).
- _hands_help(meet, lift, t_clasp): two Body arm parts on a diagonal, clasp then lift; read best from slightly below against a darker sky.
- _embrace_pair: kneel face to face, rise (motion "rise"), shuffle in, gesture "embrace" with to=other.where(t, "blade.R", raw=True).
- Rain with _rain_tau: falls, slows and hangs in the breath, then the drops turn to warm sparks and rise.
- Globe (placeholder for BRAND): white grid sphere, blue rim shell, 54 hearts in the website colours lighting 52.5 to 54.1, arcs between lit hearts; shrinks and rises at LOGO.
- WordHearts: small hearts in each expression's colour drift up off its letters, carried with the camera.
- Words: _ride (ride=(0.5, y, depth) close to the lens, depth 1 to 6 m) + drive=_clean (letters stay crisp and fade, birds land; leave="fade"). Never garbled glyphs.
- _clear_boxes(t): P3D clear as a function of t (opening lockup area, end card area).

## Camera moves worth reusing
- Surge into a person on the downbeat with a fov kick 42 to 54 (_kick), emerge inside the next world from the same point.
- Following one person through a door of light, the door filling the frame.
- Crane down from a flare into the rain onto a kneeling pair; glide to 4 m for the embrace, heads kept below the date line.
- Two moves with blend 1.6 to hold on actors, then rise and push toward a distant giant (the reveal).

## Avoid
- Bursts at crossings (white-outs); keep them under 0.5 and coloured.
- Riding words far ahead (40 m): a person near the lens hides them. Ride at 1 to 6 m.
- leave="flock" on riding words: big white ovals and broken letters.
- Spline keys with big speed changes: the camera overshoots (a dive that looked at the dark lake = empty frames). Add keys.
- P3D clear boxes over a crowd or a star field: they cut a visible hole.
- Windows onto night worlds read as dark cut-outs; use bright window looks (stars_lit, space_win) or crystal/gold looks.
- motion "run"/"walk" travel by themselves (speed x scale, counted from the show start); pairs and acting are life size only.
- All sky masks share one look and one tint per frame.
