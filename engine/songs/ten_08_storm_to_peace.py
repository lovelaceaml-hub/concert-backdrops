"""Film 08 of ten: STORM TO PEACE. A 60 second promo for the Healing Concert "The Words of Mother's Love".

PHASE A: a skeleton. This text is the treatment; the data below is the timeline (sections, camera keys in
metres, the calm field, the storm, palettes, the nine words, the people, the end card). It is written against
engine/p3d (api.py on origin/engine-p3d, words.py on origin/engine-p3d-words) and does not render yet.
`python engine/songs/ten_08_storm_to_peace.py` checks the plan (reading times, word sizes on a phone, camera
speeds, Heavenly Mother only from behind, walking speeds, the end card, no long dashes).

LOGLINE
  A storm at sea is unmade one word at a time. Each of the nine Words of Mother's Love takes one piece of the
  storm (rain, lightning, the great wave, the wind, the spray, the cloud) and turns it into still light, until
  the whole sea is a mirror at sunrise and everyone stands on it together.

THE IDEA, IN FOUR RULES
  The concert's message is that the Words of Mother's Love bring peace. This film shows that and nothing else.
  1. One field rules the world: calm(x, z, t), from 0 (storm) to 1 (peace). Where it is 0 the sea heaves, rain
     slants, wind tears, lightning strikes. Where it is 1 the sea is glass with a true mirror image, the air is
     still and the light is warm. Its edge is a line of light on the water that you can watch travel. Each
     word opens a disc of calm; the discs grow, meet, and at the end run to the horizon.
  2. Every word is made out of the storm itself. Raindrops stop in the air and draw together into letters. A
     lightning bolt freezes and bends into handwriting. A wave lowers like a curtain and the words stand
     behind it. The wind's own streaks curl into letters and lie still. The storm is not chased away: it is
     turned into the words.
  3. People carry the weather in their bodies. In the storm a person is a dark shape with a burning rim
     (refs 01, 16) whose light is being torn away downwind (ref 15). In the calm the light flows back and the
     body fills with warm glitter (refs 09, 10). Nobody needs a face for us to see what the word did.
  4. The camera feels it too. Its shake, roll and speed follow the storm at the place where it flies: violent
     sweeps through rain and spray, and the moment it crosses into a calm the horizon levels and it glides.

THE MAP (metres, y up, the water is y = 0, engine/p3d conventions)
  The film travels about 125 m in a straight line toward the dawn. It starts far out at z = 132 and ends where
  the arch of nine lights stands over the origin, with the sun rising behind it at azimuth 180 (toward -z).
  The storm wind blows toward +x (screen right). Site 1 (Greeting) z 132, site 2 (Apology) z 104, site 3
  (Inclusiveness) z 78, site 4 (Concession, Respect) z 47, site 5 (Consideration) z 30, the eye of the storm
  (Encouragement, Heavenly Mother) z 12, the gathering (Gratitude, Compliment) z 4 to 38.

SHOT BY SHOT (seconds on the eight provisional sections; every time below is SECTIONS[k] + an offset)
  1  0.0 to 7.5   THE STORM. Slate and violet.
     0.0   No fade: frame one is lit by lightning. A woman's head and shoulders in profile fill the frame, a
           dark shape rimmed in fire gold, her scarf and her own light streaming off her in the wind. The
           camera is 1.2 m from her and is torn away downwind with her light.
     1.3   A fast low sweep over wave crests, rolling 16 degrees: people stand far apart on the heaving sea,
           each braced alone, each losing light.
     2.6   The camera tilts up. One coral drop falls out of the cloud, slower than the rain. We dive with it.
     3.6   It lands between two strangers. A disc of glass races out from it, 18 m across within a second.
           Inside it the rain hangs in the air. The camera's shake stops. The two turn to face each other.
     4.5   GREETING. The hanging drops between them draw together into the words. The camera glides in a
           slow arc at their shoulder height. The first circle of peace is two people wide.
  2  7.5 to 15.0  THE LIGHTNING. Deep violet, electric white, then apricot.
     7.5   Lightning hits the water at the circle's edge. The camera is thrown back out into the storm, low
           and fast, toward a man walking into the wind (shedding light at every step) to someone who kneels
           hunched under the rain.
     9.5   A bolt comes down over them and stops. It hangs in the air, a still tree of light, and its
           branches soften from violet to apricot and bend into handwriting.
     10.3  APOLOGY. The words stand above them; he kneels beside her, both in profile, and at 11.0 his hand
           rests on her shoulder. The sea goes to glass round them. Slow push in.
     13.3  The letters cool to embers and settle on her shoulders like a blanket. Close two shot, 2.6 m: she
           lifts her head.
  3  15.0 to 22.5 THE RAIN. Steel blue, pearl, pink.
     15.0  WOW 1. On the downbeat all the rain stops in mid air. The camera does not stop: it flies on through
           thousands of hanging drops, each one a bead of light, huge soft discs of bokeh sliding past the
           lens. Behind us the wall of falling rain still stands.
     16.6  INCLUSIVENESS. The beads ahead draw together into the words. Under them stands the outsider, half
           of her light blown away into a long stream; the stream hangs, then flows back into her until she
           is whole. Two people walk to her; at 19.2 an arm goes round her shoulder.
     19.6  The beads let go and fall slowly, like warm snow, each leaving one soft ring on the glass.
     20.6  The light dims. The camera whips round and races over 20 m to stand low behind three small backs: a
           man, a mother and her child. Beyond them the sea is standing up.
  4  22.5 to 30.0 THE WAVE AND THE WIND. Storm green, foam white, the first pale line of sky, sky blue, clay.
     22.5  WOW 2. The wave is 9 m high over them, lit from behind by lightning. On the downbeat it does not
           break. Its crest lowers like a bowed head, the whole wall sinks and spreads into glass, and the
           camera tilts down with it.
     23.3  CONCESSION. Where the wave stood, the words stand, the first pale line of the horizon drawn under
           them. The man turns to the mother and child, steps aside and opens his palm toward the way ahead.
     25.9  The words part in the middle and swing open like a gate. The mother walks through.
     27.0  RESPECT. The child runs back to the man and lifts her face; a small breath of light leaves her.
           He goes down on one knee to her height and leans in. So that she can be heard, the wind dies: its
           long streaks slow, curl like handwriting and settle into the words above the two of them.
     29.6  He nods. The letters lean and flow into his chest: he has heard her.
  5  30.0 to 37.5 THE EDGE. Indigo, storm blue against rose and gold.
     30.0  A lightning flash cuts us to the edge of the calm. A runner of points and lines (ref 12) sprints
           along the glass, the camera racing beside him. Out in the swell someone is on hands and knees.
     31.7  He drops to one knee at the very edge and reaches across it. Two hands in close up (ref 04): his
           gold, on the still side; the other storm blue, on the heaving side. The edge of the calm runs
           down the middle of the frame, between the fingertips.
     32.6  They grip. A rose flare; the calm bursts outward from the grip and gold runs up the blue arm.
     33.4  CONSIDERATION. The spray thrown up by the last wave hangs in an arc and settles into the words.
           He pulls her to her feet and keeps hold of her arm until she is steady.
     36.4  The letters fall as fine spray. The camera rises: all the circles are running together.
  6  37.5 to 45.0 THE EYE (the breath in the music). Deep blue glass, warm white and gold, soft violet.
     37.5  Silence. A disc of glass 190 m wide; the storm wall turns far off, its lightning without sound.
           Toward the dawn the storm has opened a door: the cloud has lifted off the horizon and rays fan
           low across the glass to one place. Lights glide under the glass toward it. There Heavenly Mother
           gathers out of the rays, seen only from behind, veiled, her veil hanging perfectly still.
     39.1  The camera comes down to half body behind her. Rays fan from behind her head (ref 10). She opens
           her arms low. People come walking over the glass from every side, their mirror images under them.
     40.5  ENCOURAGEMENT. Motes drifting in the rays above her gather into the words, in the violet of the
           lightning made gentle. The camera circles slowly behind her, never past her shoulder.
     43.5  The letters stream down into her open right hand. Close on the hand from behind (ref 14): drops of
           light lie in the palm. She lifts it.
  7  45.0 to 52.5 SUNRISE (the biggest passage). Violet cloud above, a band of gold, then lavender.
     45.0  WOW 3. The light leaves her hand and the calm bursts to the horizon in a second and a half: the
           storm wall is blown open like a curtain, the sea becomes one mirror, the cloud lifts off the whole
           horizon and the sun's edge breaks in a line of gold. The camera pulls back and up at 19 m/s. She
           dissolves upward where she stands, into gold flakes (ref 05): only the light rises.
     46.5  GRATITUDE. The camera swoops down over the crowd's heads. The sun's glitter lifts off the water
           and stands up as the words on the dark cloud, above the gold band. Below, people turn to one
           another and bow, a hand on the heart.
     49.2  The words bow too: they lean forward and sink into the water. Light begins to lift off everyone,
           from shoulders and raised hands.
     49.9  COMPLIMENT. That light gathers above the crowd into the words. The camera revolves a sixth of a
           turn round them, low over a field of raised arms, the sun sweeping past behind.
  8  52.5 to 60.0 THE BOW AFTER THE STORM, and the end card. Pearl, sky blue, gold: the campaign day.
     52.5  The final hit, made of colour and motion: the words burst into sparks, nine lights rise out of
           the mirror in the nine colours of the words and take their places in the arch, like a bow in the
           cloud after the storm, the cloud thins to a pearl morning, and the camera pulls back 50 m through
           the falling sparks to the last picture.
     54.4  "The Words of Mother's Love" (coral) with the label "Healing Concert" is whole; by 55.2 the lines
           "Sunday, December 6 · 4:30 PM", "World Mission Society Church of God", "6720 W Sahara Ave,
           Las Vegas" (navy) have risen out of the water. All of it holds to the last frame (4.8 s for the
           lines, 5.6 s for the title) in the existing end card style, over the mirror with the crowd small
           and bright on it. A few doves cross low. The camera keeps easing back. No fade to black.

HOW EACH EXPRESSION ARRIVES, IS READ AND LEAVES (exact campaign wording and labels: EXPRESSIONS below)
  Greeting       hanging raindrops gather; read 4.5 to 7.4; the letters fall as drops into the glass.
  Apology        a frozen bolt of lightning bends into the words; read 10.3 to 13.3; embers on her shoulders.
  Inclusiveness  the whole stopped rain gathers; read 16.6 to 19.6; the beads fall again, slowly.
  Concession     the bowing wave uncovers the words; read 23.3 to 25.9; they open like a gate.
  Respect        the dying wind writes the words; read 27.0 to 29.6; they flow into the listener.
  Consideration  the hanging spray of the last wave settles; read 33.4 to 36.4; it falls as fine spray.
  Encouragement  motes in the rays above Heavenly Mother; read 40.5 to 43.5; they stream into her hand.
  Gratitude      the sun's glitter lifts off the water; read 46.5 to 49.2; the words bow and sink.
  Compliment     light rising off everyone gathers; read 49.9 to 52.5; they burst and the nine lights rise.
  After a word leaves, its colour rests as a light under the glass. During the breath the lights glide under
  the mirror to Heavenly Mother; on the final hit all nine rise into the arch.

THE PEOPLE (lifelike bodies of points, clothed in garments of light, no faces: PEOPLE below)
  Twelve named people in the storm (a watcher and a stranger, the weary one and the one who is sorry, the
  outsider and two who welcome her, the man who gives way, a mother and her child, the one in the swell and
  the runner), each seen close and each touched by someone: a hand on a shoulder, an arm round a shoulder, a
  knee bent to a child, a grip across the edge. Three more stand alone where the first sweeps pass. Then
  about forty people of every height, children among them, walking in over the glass. Heavenly Mother
  appears once, for 8 s, from behind, veiled, and as one open hand. She is the still centre of the storm: the
  place the calm comes from.

THREE WOW MOMENTS
  1. 15.0  All the rain stops in mid air and we fly on through it; the drops become the words.
  2. 22.5  The 9 m wave bows instead of breaking and lies down as glass, uncovering "Please, after you."
  3. 45.0  From one open hand the calm bursts to the horizon: the whole storm sea becomes a mirror at sunrise.
  (Also: the frozen lightning at 9.5 and the two hands across the edge of the calm at 32.6.)

WHAT KEEPS IT DIFFERENT FROM THE OTHER NINE
  It is the only film with weather and the only one whose subject is turbulence becoming stillness. Its words
  are made from the storm's own matter, its people change look with the weather, and its camera is rough
  where the world is rough. It shares the sea with film 01 (there a wave of light wakes a still sea; here
  stillness spreads over a wild one, and the camera never rides a front). No lines join people (film 03), no
  silhouettes are windows (04), nothing rises for its own sake (06), no flame is carried (07), Heavenly Mother
  is not followed (09) and the nine colours stay under the glass until the last hit (10).

LESSONS FROM THE FIRST FILM, APPLIED
  Opens on a lit close up, not black. Five close contact beats. Walkers walk (no sliding: asked of BODY).
  Heavenly Mother dissolves in place with no scaling. The loudest moment is colour and motion (burst, nine
  lights, the sky changes), not a brightness change on a pale sky. Words are read against the dark cloud,
  never against the sun: the sun stays at least 5 degrees under any word. The end card holds to the last
  frame.

RE-TIMING IN PHASE B
  Every time hangs off SECTIONS. MED2's commit 45017af (origin/epic-medley2) reports the real medley cut at
  about 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 (a breath, then a hit at 42.5) and 49.47 (final chorus,
  final hit at 58.1), songs 08, 01, 04, 11, 05, 06, 07, 03. Not yet confirmed by ear or by the coordinator. On
  that map the rain stops on 6.84 or 13.30 (song 04 is the apology song, so Apology and Inclusiveness may swap
  sections), the wave bows on 19.85, the breath is the eye, the burst lands on 42.5 or 49.47, the end card is
  whole by 56.0 and the final hit at 58.1 lands on the nine lights of the arch.

WHAT THIS FILM NEEDS FROM THE 3D LAYER BEYOND THE BRIEF: see NEEDS at the end of the file.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
AUDIO_FILE = "audio/promo/concert-medley.mp3"   # the new medley of branch epic-medley2

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
TOTAL = 60.0
SONG_END = 60.0
NFRAMES = int(round(TOTAL * FPS))

# ------------------------------------------------------------------------------------------------- sections
# Provisional starts of the eight song sections (TEN-FILMS.md). Phase B replaces these with the measured
# section map of the medley and nudges the offsets onto its downbeats; nothing else holds an absolute time.
SECTIONS = [0.0, 7.5, 15.0, 22.5, 30.0, 37.5, 45.0, 52.5]
SECTION_NAMES = ["the storm", "the lightning", "the rain", "the wave and the wind", "the edge", "the eye",
                 "sunrise", "the bow after the storm"]
S1, S2, S3, S4, S5, S6, S7, S8 = SECTIONS

# ---- the moments everything else hangs off
DROP_FALL = S1 + 2.6      # the first drop leaves the cloud
DROP_LAND = S1 + 3.6      # ... and lands between two strangers: the first circle of calm
STRIKE = S2 + 0.0         # lightning at the circle's edge throws the camera back into the storm
BOLT_FREEZE = S2 + 2.0    # the bolt over the kneeling one stops in the air
SHOULDER = S2 + 3.5       # a hand on a shoulder
RAIN_STOP = S3 + 0.0      # WOW 1: all the rain hangs
WELCOME = S3 + 4.2        # an arm round the outsider's shoulder
WAVE_UP = S3 + 5.4        # the sea begins to stand up
WAVE_BOW = S4 + 0.0       # WOW 2: the wave bows
GATE = S4 + 3.4           # the words open like a gate
LISTEN = S4 + 4.5         # a knee bent to a child; the wind dies
RUN = S5 + 0.0            # the runner (after a flash cut)
GRIP = S5 + 2.6           # two hands grip across the edge
MERGE = S5 + 6.0          # the circles run together into the eye
EYE = S6 + 0.0            # the breath: Heavenly Mother, from behind
PALM = S6 + 6.9           # close on her open hand; she lifts it
BURST = S7 + 0.0          # WOW 3: the calm runs to the horizon; sunrise
BOWS = S7 + 1.6           # people bow to one another
LIFT = S7 + 4.6           # arms rise; light lifts off everyone
FINAL_HIT = S8 + 0.0      # the nine lights rise into the arch
CARD_WHOLE = S8 + 2.7     # the last line of the end card is formed (55.2): 4.8 s to the last frame

# ------------------------------------------------------------------------------- the nine expressions
# Exact campaign wording, labels and colours: project-docs/DESIGN-SYSTEM.md section 5. Line breaks and
# typographic quotes as in PHRASES of engine/songs/epic_concert.py and EXPRESSIONS of engine/p3d/words.py.
# The order is the order of the nine lights in the arch.
EXPRESSIONS = [
    dict(label="Greeting", lines=["“How are you?”"], color="#FF977C"),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"],
         color="#FFD05F"),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], color="#FFAD69"),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], color="#F582AF"),
    dict(label="Concession", lines=["“Please, after you.”"], color="#82B0ED"),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], color="#CE927E"),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
         color="#B293E7"),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], color="#EF7A96"),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], color="#BE9CEB"),
]
LABELS = [e["label"] for e in EXPRESSIONS]

# ------------------------------------------------------------------------------------------------ the map
SUN_AZ = 180.0                       # the dawn is toward -z, behind the arch as the default camera sees it
WIND_DIR = (0.93, 0.0, 0.36)         # the storm wind blows toward +x and a little toward the lens
SITES = {                            # where each word falls (on the water, y = 0)
    1: (-8.0, 0.0, 132.0),           # Greeting
    2: (12.0, 0.0, 103.8),           # Apology
    3: (-6.0, 0.0, 78.0),            # Inclusiveness
    4: (0.0, 0.0, 47.0),             # Concession and Respect
    5: (-17.5, 0.0, 30.5),           # Consideration
    6: (0.0, 0.0, 12.0),             # the eye: Heavenly Mother, Encouragement
    7: (0.0, 0.0, 20.0),             # the gathering: Gratitude, Compliment
}
MOTHER_POS = SITES[6]
MOTHER_FACING = 180.0                # she faces the dawn, so every camera that sees her is behind her

# ---------------------------------------------------------------------------------------- the calm field
# calm(x, z, t) in 0..1. Each entry is a disc on the water whose radius grows over time; the field is the
# largest of them. Sea height, rain, wind, lightning, the mirror, camera shake and each person's look all
# read this one field. `edge` is the width in metres over which storm turns to glass; `ring` is the colour
# of the line of light that travels with the edge.
CALM = [
    dict(name="greeting", center=SITES[1], ring="#FF977C", edge=0.8,
         radius=[(DROP_LAND, 0.0), (DROP_LAND + 0.7, 9.0), (S2, 11.0), (S3, 13.0)]),
    dict(name="apology", center=SITES[2], ring="#FFAD69", edge=0.8,
         radius=[(BOLT_FREEZE + 0.1, 0.0), (BOLT_FREEZE + 0.8, 9.0), (S2 + 4.0, 11.0), (S3, 12.0)]),
    dict(name="inclusiveness", center=SITES[3], ring="#F582AF", edge=0.8,
         radius=[(RAIN_STOP, 0.0), (RAIN_STOP + 1.6, 14.0), (S4, 16.0)]),
    # its edge is crisp and holds at 24 m until the grip: it passes exactly through the place where the two
    # hands meet at site 5, so the runner kneels on glass and the other one is still in the swell
    dict(name="concession", center=SITES[4], ring="#82B0ED", edge=0.5,
         radius=[(WAVE_BOW, 0.0), (WAVE_BOW + 1.5, 18.0), (S5, 24.0), (GRIP, 24.0)]),
    dict(name="consideration", center=SITES[5], ring="#EF7A96", edge=0.8,
         radius=[(GRIP, 0.0), (GRIP + 1.4, 28.0), (MERGE, 32.0)]),
    # the eye: the circles run together (MERGE), hold through the breath, then run to the horizon (BURST)
    dict(name="eye", center=SITES[7], ring="#ffe2b0", edge=4.0,
         radius=[(MERGE - 0.4, 0.0), (EYE + 1.0, 95.0), (BURST, 95.0), (BURST + 1.6, 8000.0)]),
]
# The rain hangs in a dome that is wider than the glass under it (the drops stop before the sea does). At
# `until` the drops let go: over glass they fall slowly, like warm snow; over the storm sea it rains again.
RAIN_HOLD = [
    dict(center=SITES[1], radius=[(DROP_LAND, 0.0), (DROP_LAND + 0.6, 12.0)], until=S2 + 1.0),
    dict(center=SITES[3], radius=[(RAIN_STOP, 0.0), (RAIN_STOP + 0.3, 60.0)], until=S3 + 5.6),
]


def _ss(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _keys(keys, t):
    """Eased value of [(t, v), ...] at t (the same easing as engine/track.py's Track)."""
    ts = [k[0] for k in keys]
    if t <= ts[0]:
        return float(keys[0][1])
    if t >= ts[-1]:
        return float(keys[-1][1])
    i = int(np.searchsorted(ts, t, side="right")) - 1
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    u = u * u * (3.0 - 2.0 * u)
    return float(keys[i][1] * (1.0 - u) + keys[i + 1][1] * u)


def calm_at(x, z, t):
    """The calm field at points (x, z) on the water at time t: 0 storm, 1 peace. x and z may be arrays."""
    x, z = np.asarray(x, np.float64), np.asarray(z, np.float64)
    out = np.zeros(np.broadcast(x, z).shape)
    for c in CALM:
        if t < c["radius"][0][0]:
            continue
        r = _keys(c["radius"], t)
        d = np.hypot(x - c["center"][0], z - c["center"][2])
        out = np.maximum(out, 1.0 - _ss(r - c["edge"], r + c["edge"], d) if r > 0.0 else 0.0)
    return out


# ---------------------------------------------------------------------------------------------- the storm
# Each amount is for the open storm; the engine multiplies it by (1 - calm) at every place.
STORM = dict(
    swell=[(0.0, 2.2), (S3, 2.4), (S5, 2.0), (BURST, 1.6), (BURST + 1.6, 0.0)],   # wave height, metres
    swell_length=(18.0, 31.0, 47.0),         # three trains of waves, metres crest to crest
    spray=[(0.0, 1.0), (S6, 0.7), (BURST + 1.6, 0.0)],                             # spume off the crests
    rain=[(0.0, 1.0), (S6, 0.8), (BURST, 0.8), (BURST + 1.6, 0.0)],                # streaks of cold sparks
    rain_slant=22.0,                          # degrees from the vertical, downwind
    wind=[(0.0, 18.0), (S4, 20.0), (S6, 12.0), (BURST + 1.6, 0.5)],                # metres per second
    wind_streaks=[(0.0, 1.0), (S6, 0.6), (BURST + 1.6, 0.0)],                      # long ribbons racing past
    cloud_base=[(0.0, 60.0), (S6, 90.0), (BURST + 1.6, 400.0), (S8 + 1.9, 3000.0)],   # metres: the lid lifts
    # the clear band between the horizon and the cloud, degrees of sky, widest toward the dawn
    horizon_gap=[(0.0, 0.0), (WAVE_BOW, 0.0), (WAVE_BOW + 1.1, 0.4), (EYE, 1.4), (BURST, 2.0),
                 (BURST + 1.6, 5.0), (FINAL_HIT, 9.0), (S8 + 1.9, 90.0)],
    door=(SUN_AZ, 25.0),                      # the eye's wall is open toward the dawn, half width in degrees
)
# Lightning: (time, kind, where). Never two in one second, never a white frame: the cloud lights from inside
# and the people get a rim. "freeze" is the bolt that stops in the air and becomes the Apology.
LIGHTNING = [
    (S1 + 0.0, "sheet", (-30.0, 55.0, 105.0)),      # frame one is lit
    (S1 + 0.9, "sheet", (26.0, 50.0, 96.0)),
    (STRIKE, "bolt", (-1.0, 0.0, 126.0)),           # at the edge of the first circle
    (BOLT_FREEZE, "freeze", (12.0, 6.5, 103.4)),    # its lowest branch stops 6.5 m over the kneeling one
    (S2 + 6.9, "sheet", (-20.0, 60.0, 70.0)),
    (WAVE_UP + 0.3, "sheet", (0.0, 30.0, 20.0)),    # behind the rising sea: it is seen against the light
    (WAVE_BOW - 0.4, "sheet", (6.0, 34.0, 16.0)),   # ... and again behind the wave at its full height
    (RUN, "sheet", (-30.0, 50.0, 10.0)),            # hides the one cut of the film
    (S5 + 1.2, "sheet", (-45.0, 45.0, 30.0)),
    (S6 + 1.1, "far", (-90.0, 40.0, 60.0)),         # in the wall, without sound
    (S6 + 4.0, "far", (95.0, 40.0, 40.0)),
    (S6 + 6.3, "far", (-70.0, 40.0, 90.0)),
]
# The great wave: a wall of water across the path that rears and then bows down into glass.
WAVE = dict(
    half_width=23.0,
    line_z=[(WAVE_UP - 0.4, 34.0), (WAVE_BOW, 43.5)],                    # it comes toward the people
    height=[(WAVE_UP - 0.4, 2.0), (WAVE_BOW - 0.1, 9.0), (WAVE_BOW + 1.1, 0.0)],
    lean=[(WAVE_UP, 0.0), (WAVE_BOW, 14.0), (WAVE_BOW + 0.5, 34.0)],     # degrees: the crest bows forward
    crest="#d8f0ff", body="#143f50",
)

# ----------------------------------------------------------------------------------------------- palettes
# Display colours. sky: zenith, middle, horizon, light. sea: trough, crest or foam, glass (the calm water).
# rim: the burning edge of people in the storm. fill: the warm body light of people in the calm.
PAL = {
    "storm":     dict(sky=("#141a2c", "#232b44", "#33305a", "#cdbfff"), sea=("#16324a", "#b9d2ff", "#1f4c5c"),
                      rain="#cfe0ff", rim="#ffb066", fill="#ffe0b0"),
    "lightning": dict(sky=("#1a1638", "#2a2356", "#40347a", "#b9a4ff"), sea=("#1b2a52", "#c8c0ff", "#27406a"),
                      rain="#d6ccff", rim="#ffb066", fill="#ffd9a8"),
    "rain":      dict(sky=("#1c2740", "#31456a", "#4a6488", "#dfe9ff"), sea=("#1d4660", "#cfe6f6", "#24586a"),
                      rain="#ffe9f0", rim="#ffc08a", fill="#ffe4c4"),
    "wave":      dict(sky=("#1b2a3e", "#2d4a60", "#7e98b8", "#e6f2ff"), sea=("#143f50", "#d8f0ff", "#2a6478"),
                      rain="#dcecff", rim="#ffc08a", fill="#ffe2bc"),
    "edge":      dict(sky=("#181d44", "#2a2f6a", "#5a4a86", "#ffd9c8"), sea=("#1a2c5c", "#c9d4ff", "#2c4f80"),
                      rain="#d4dcff", rim="#6fb4ff", fill="#ffc56e"),
    "eye":       dict(sky=("#0c1f4a", "#1d3b78", "#c9a070", "#ffd08a"), sea=("#0a1a3c", "#9fb4e8", "#0e2450"),
                      rain="#c8d4ff", rim="#ffd08a", fill="#ffe6bc"),
    "sunrise":   dict(sky=("#2b2a5e", "#6f62a8", "#ffc56e", "#fff0c8"), sea=("#1c2a5a", "#ffe0a8", "#27356e"),
                      rain="#ffe9c8", rim="#ffd27a", fill="#ffe9c4"),
    "lavender":  dict(sky=("#4a4590", "#a892d0", "#ffd49a", "#fff4d8"), sea=("#3a4486", "#ffe9c0", "#5a64a8"),
                      rain="#fff0d8", rim="#ffd27a", fill="#fff0d0"),
    # the campaign day of engine/theme.py (PAL["day"] and the cream end): the end card stands on this
    "day":       dict(sky=("#86c6f0", "#cfe8fa", "#fff4e4", "#fffaee"), sea=("#8ecdf4", "#fff6e6", "#bfe0f6"),
                      rain="#ffffff", rim="#ffd27a", fill="#fff6e6"),
}
PALETTE_KEYS = [(S1, "storm"), (S2 - 0.3, "storm"), (S2 + 0.4, "lightning"), (S3 - 0.3, "lightning"),
                (S3 + 0.6, "rain"), (S3 + 5.4, "rain"), (S4, "wave"), (S5 - 0.1, "wave"), (S5, "edge"),
                (MERGE, "edge"), (EYE + 0.6, "eye"), (BURST, "eye"), (BURST + 1.4, "sunrise"),
                (LIFT, "sunrise"), (FINAL_HIT, "lavender"), (S8 + 1.9, "day"), (TOTAL, "day")]
# the sun: under the horizon through the breath (its rays fan through the door in the storm), up on the burst;
# kept modest while words are read above it, full for the end card
SUN_ELEV = [(0.0, -6.0), (EYE, -1.5), (BURST, -0.3), (BURST + 1.0, 0.5), (FINAL_HIT, 2.5), (TOTAL, 4.5)]
SUN_GAIN = [(0.0, 0.0), (MERGE, 0.0), (EYE, 0.25), (BURST, 0.4), (BURST + 1.0, 0.6), (FINAL_HIT, 0.6),
            (S8 + 1.2, 1.0), (TOTAL, 1.0)]
RAYS = [(0.0, 0.0), (EYE - 0.5, 0.0), (EYE + 1.5, 0.9), (PALM, 0.8), (BURST + 1.0, 1.0), (FINAL_HIT, 0.6),
        (S8 + 2.0, 0.35), (TOTAL, 0.3)]
MIST = [(0.0, 0.0), (DROP_LAND, 0.0), (S3, 0.2), (EYE, 0.5), (BURST + 2.0, 0.3), (S8 + 2.0, 0.15), (TOTAL, 0.15)]
EXPOSURE = [(0.0, 1.0), (FINAL_HIT - 0.1, 1.0), (FINAL_HIT + 0.1, 1.25), (FINAL_HIT + 0.9, 1.0), (TOTAL, 1.0)]

# ------------------------------------------------------------------------------------------------- camera
# Shots: (name, why the camera moves, keys). A key: (t, position, target, vertical field of view in degrees,
# roll in degrees, focus distance in metres or None for the distance to the target, aperture in metres,
# shake 0..1). Shots follow one another without a break except where `cut` is set (one flash cut, at RUN).
# shake and roll are the storm at the camera's own place: 0 inside every calm (two shakes are the camera's
# own: the jolt of the strike at the first circle's edge, and its running beside the runner). check()
# compares them with the calm field.


def K(t, pos, target, fov, roll=0.0, focus=None, aperture=0.03, shake=0.0):
    return dict(t=float(t), pos=pos, target=target, fov=float(fov), roll=float(roll), focus=focus,
                aperture=float(aperture), shake=float(shake))


SHOTS = [
    dict(name="torn away", why="the wind takes her light and the camera with it", keys=[
        K(S1 + 0.00, (-9.72, 1.60, 133.15), (-10.02, 1.50, 132.00), 30, -6, 1.25, 0.035, 0.8),
        K(S1 + 0.55, (-8.90, 1.75, 133.30), (-9.20, 1.62, 131.90), 38, -9, 1.7, 0.035, 0.9),
        K(S1 + 1.30, (-3.00, 4.60, 132.20), (16.0, 1.5, 120.0), 50, -16, 12.0, 0.02, 1.0)]),
    dict(name="apart", why="thrown over the crests: everyone stands alone", keys=[
        K(S1 + 1.95, (6.0, 5.0, 127.0), (4.0, 1.0, 119.5), 54, 9, 8.2, 0.03, 1.0)]),
    dict(name="the first drop", why="it looks up at the one thing that falls slowly, and dives with it", keys=[
        K(DROP_FALL, (4.0, 9.0, 137.5), (-8.0, 26.0, 132.0), 50, 4, 25.0, 0.02, 0.8),
        K(DROP_LAND, (-3.6, 2.3, 138.6), (-8.0, 0.4, 132.0), 46, 0, 8.0, 0.025, 0.7)]),
    dict(name="How are you?", why="inside the calm it glides: a slow arc at shoulder height", keys=[
        K(S1 + 4.50, (-5.6, 1.7, 137.6), (-8.0, 1.75, 131.8), 42),
        K(S1 + 7.40, (-10.2, 1.9, 137.2), (-8.0, 1.75, 131.8), 42)]),
    dict(name="into the lightning", why="the strike throws it back out, toward the one who kneels", keys=[
        K(S2 + 0.80, (2.5, 3.2, 124.0), (10.0, 1.2, 108.0), 52, -12, 14.0, 0.02, 1.0),
        K(BOLT_FREEZE, (10.5, 2.6, 114.5), (12.0, 5.5, 103.6), 48, 6, 11.0, 0.02, 0.8)]),
    dict(name="I'm sorry", why="it comes down and pushes in as he kneels beside her", keys=[
        K(S2 + 2.80, (12.9, 1.5, 111.2), (12.0, 2.2, 103.6), 40),
        K(S2 + 5.80, (11.5, 1.45, 110.5), (12.0, 2.2, 103.6), 40)]),
    dict(name="a hand on a shoulder", why="it follows the embers down to the two of them", keys=[
        K(S2 + 6.50, (11.9, 1.15, 106.6), (11.95, 1.05, 104.0), 38, 0, 2.6, 0.045),
        K(S2 + 6.90, (12.2, 1.20, 106.4), (11.95, 1.10, 104.0), 38, 0, 2.5, 0.045)]),
    dict(name="the rain stops", why="it flies on through the hanging drops (bullet time), slowing", keys=[
        K(RAIN_STOP, (8.5, 3.6, 103.0), (-3.0, 2.0, 84.0), 50, -5, 9.0, 0.06, 0.1),
        K(S3 + 0.90, (1.5, 3.0, 93.5), (-5.5, 2.0, 78.0), 48, -3, 9.0, 0.06, 0.3)]),
    dict(name="It's okay. I understand.", why="a slow glide while her light flows back", keys=[
        K(S3 + 1.60, (-3.6, 1.9, 84.9), (-6.0, 1.95, 77.3), 40, 0, None, 0.035),
        K(S3 + 4.60, (-8.2, 1.7, 84.6), (-6.0, 1.95, 77.3), 40, 0, None, 0.035)]),
    dict(name="brought in", why="it sinks to the three of them as the arm goes round her", keys=[
        K(S3 + 5.30, (-8.6, 1.55, 81.4), (-6.2, 1.45, 78.1), 40, 0, 4.1, 0.045),
        K(S3 + 5.60, (-7.0, 1.60, 80.4), (-5.2, 1.60, 76.0), 42, 0, 4.5, 0.04)]),
    dict(name="the sea stands up", why="they look round, and so does the camera: it races to the wave", keys=[
        K(S3 + 6.50, (-1.5, 2.4, 61.5), (0.0, 4.0, 46.0), 52, 10, 16.0, 0.02, 0.4),
        K(S4 - 0.20, (0.9, 1.45, 59.4), (0.0, 6.4, 43.0), 50, 2, 9.5, 0.025, 0.9)]),
    dict(name="the wave bows", why="it tilts down with the crest as the wall lies down", keys=[
        K(WAVE_BOW, (0.9, 1.45, 59.0), (0.0, 6.2, 43.2), 50, 0, 9.5, 0.025, 0.9),
        K(S4 + 0.80, (0.8, 1.55, 57.6), (0.0, 2.0, 44.5), 42)]),
    dict(name="Please, after you.", why="a slow step forward and across, between the two backs", keys=[
        K(GATE, (-0.2, 1.75, 56.8), (0.0, 2.0, 44.5), 40)]),
    dict(name="I'd love to hear more", why="it goes down to the child's height with him and arcs round them",
         keys=[
        K(LISTEN, (-0.9, 1.30, 54.7), (-2.65, 1.95, 49.1), 40, 0, None, 0.04),
        K(S4 + 7.10, (-5.2, 1.40, 54.3), (-2.65, 1.95, 49.1), 40, 0, None, 0.04),
        K(S5 - 0.03, (-5.5, 1.40, 54.3), (-2.65, 1.95, 49.1), 40, 0, None, 0.04)]),
    dict(name="the runner", why="it runs beside him along the glass", cut="lightning flash", keys=[
        K(RUN, (-4.6, 1.25, 36.6), (-6.3, 1.15, 33.0), 46, -4, 4.0, 0.04, 0.35),
        K(S5 + 1.70, (-15.2, 1.15, 33.9), (-16.9, 0.95, 30.6), 44, -2, 3.7, 0.04, 0.3)]),
    dict(name="two hands", why="it closes on the place where the calm ends", keys=[
        K(S5 + 2.20, (-16.7, 0.90, 32.0), (-17.5, 0.75, 30.5), 36, 0, 1.7, 0.05, 0.15),
        K(GRIP, (-17.1, 0.85, 31.7), (-17.5, 0.75, 30.5), 34, 0, 1.27, 0.05, 0.05)]),
    dict(name="Can I give you a hand", why="the burst pushes it back and up as she is pulled to her feet", keys=[
        K(S5 + 3.40, (-19.2, 1.6, 37.3), (-17.3, 2.15, 30.2), 40),
        K(S5 + 6.40, (-15.4, 2.0, 37.9), (-17.3, 2.15, 30.2), 40)]),
    dict(name="the eye", why="it rises to see the circles run together, then comes down to her", keys=[
        K(EYE, (-9.0, 9.0, 36.0), (0.0, 1.2, 13.0), 46, 0, 26.0, 0.02),
        K(S6 + 1.60, (1.9, 1.9, 16.8), (0.1, 1.6, 12.0), 40, 0, 5.0, 0.045)]),
    dict(name="from behind", why="a slow push to half body: rays behind her head", keys=[
        K(S6 + 2.40, (1.25, 1.8, 15.1), (0.1, 1.6, 12.0), 38, 0, 3.3, 0.05)]),
    dict(name="Everything will go well.", why="a slow circle behind her, never past her shoulder", keys=[
        K(S6 + 3.00, (1.6, 2.2, 17.6), (0.0, 3.0, 9.8), 40, 0, None, 0.035),
        K(S6 + 6.00, (-1.5, 2.6, 17.3), (0.0, 3.0, 9.8), 40, 0, None, 0.035)]),
    dict(name="the open hand", why="it follows the letters down into her palm", keys=[
        K(PALM, (1.25, 1.42, 13.3), (0.42, 1.28, 11.75), 34, 0, 1.76, 0.045),
        K(BURST, (1.3, 1.5, 13.6), (0.3, 1.5, 10.5), 38, 0, 3.2, 0.04)]),
    dict(name="to the horizon", why="the burst throws it back and up: the whole sea goes to glass", keys=[
        K(S7 + 0.90, (0.0, 6.5, 30.0), (0.0, 2.2, 4.0), 50, 0, 26.0, 0.02)]),
    dict(name="Thank you.", why="it swoops down over the heads and glides while they bow", keys=[
        K(S7 + 1.50, (1.2, 2.6, 16.4), (0.0, 3.5, 4.0), 44, 0, None, 0.035),
        K(S7 + 4.20, (-1.0, 2.8, 15.6), (0.0, 3.5, 4.0), 44, 0, None, 0.035)]),
    dict(name="You're amazing.", why="it follows the lifting light up and revolves round the words", keys=[
        K(S7 + 4.90, (-6.0, 3.0, 20.4), (0.0, 4.7, 10.0), 46, 0, None, 0.035),
        K(S7 + 6.20, (0.0, 3.15, 22.0), (0.0, 4.7, 10.0), 46, 0, None, 0.035),
        K(FINAL_HIT, (6.0, 3.3, 20.4), (0.0, 4.7, 10.0), 46, 0, None, 0.035)]),
    # The end wide is framed for the end card: the horizon at about a third of the height, the arch's lights
    # near the top above the title. Phase B fits the two keys to the arch that CORE builds.
    dict(name="the bow after the storm", why="it pulls back through the falling sparks and keeps easing back",
         keys=[
        K(S8 + 2.00, (0.0, 6.0, 70.0), (0.0, 14.3, 0.0), 40, 0, 70.0, 0.01),
        K(TOTAL, (0.0, 6.6, 76.0), (0.0, 15.6, 0.0), 40, 0, 76.0, 0.01)]),
]


def _runs():
    """The shots joined into runs of keys with no cut inside (one run before the flash cut, one after)."""
    runs, cur = [], []
    for s in SHOTS:
        if s.get("cut") and cur:
            runs.append(cur)
            cur = []
        cur.extend(s["keys"])
    runs.append(cur)
    return runs


def _pchip(ts, vs, t):
    """A smooth curve through keys that never overshoots (monotone cubic), so a slow glide after a fast flight
    starts gently and stays inside its two keys."""
    ts = np.asarray(ts, np.float64)
    vs = np.asarray(vs, np.float64).reshape(len(ts), -1)
    n = len(ts)
    if n == 1 or t <= ts[0]:
        return vs[0]
    if t >= ts[-1]:
        return vs[-1]
    h = np.diff(ts)
    d = np.diff(vs, axis=0) / h[:, None]
    m = np.zeros_like(vs)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        w1, w2 = 2.0 * h[i] + h[i - 1], h[i] + 2.0 * h[i - 1]
        ok = d[i - 1] * d[i] > 0.0
        with np.errstate(divide="ignore", invalid="ignore"):
            m[i] = np.where(ok, (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]), 0.0)
    i = int(np.searchsorted(ts, t, side="right")) - 1
    u = (t - ts[i]) / h[i]
    h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
    h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return h00 * vs[i] + h10 * h[i] * m[i] + h01 * vs[i + 1] + h11 * h[i] * m[i + 1]


_RUNS = _runs()


def camera_values(t):
    """The camera at t as plain numbers: pos, target, fov, roll, focus, aperture, shake."""
    run = _RUNS[0]
    for r in _RUNS:
        if t >= r[0]["t"]:
            run = r
    ts = [k["t"] for k in run]
    pos = _pchip(ts, [k["pos"] for k in run], t)
    target = _pchip(ts, [k["target"] for k in run], t)
    nums = _pchip(ts, [[k["fov"], k["roll"], k["aperture"], k["shake"],
                        k["focus"] if k["focus"] is not None else
                        float(np.linalg.norm(np.subtract(k["target"], k["pos"])))] for k in run], t)
    return dict(pos=pos, target=target, fov=float(nums[0]), roll=float(nums[1]), aperture=float(nums[2]),
                shake=float(nums[3]), focus=float(nums[4]))


def camera_at(t):
    """The camera at t for the 3D layer (a p3d CameraState). Shake is added by the engine from `shake`."""
    from p3d.api import CameraState
    v = camera_values(t)
    return CameraState(pos=v["pos"], target=v["target"], fov=v["fov"], roll=v["roll"], focus=v["focus"],
                       aperture=v["aperture"], aspect=ASPECT)


# -------------------------------------------------------------------------------------------------- words
# Settings for engine/p3d/words.py (Word): pos is the centre of the phrase block, width the widest line, both
# in metres. label_size (em of the phrase face) is set per word so that every label's capitals are about 1 mm
# tall on a phone (the first film's labels, at 0.65 mm, were too small). arrive and leave are names that
# words.py has today; `made_of` and `wish` say what this film wants in their place (see NEEDS). Every word is
# read alone: no two reading moments overlap, and no word begins to arrive while another is still being read.
WORDS = [
    dict(expr="Greeting", pos=(-8.0, 2.55, 131.7), width=5.2, label_size=0.30, face="camera",
         t_in=DROP_LAND + 0.1, t_read0=S1 + 4.5, t_read1=S1 + 7.4, t_out=S2 + 0.9,
         arrive="gather", leave="sink", made_of="the raindrops that hang inside the first circle",
         wish=dict(arrive="the drops stop first, then draw in", leave="each letter falls as a drop: one ring")),
    dict(expr="Apology", pos=(12.0, 3.15, 103.6), width=7.6, label_size=0.40, face="camera",
         t_in=BOLT_FREEZE + 0.05, t_read0=S2 + 2.8, t_read1=S2 + 5.8, t_out=S2 + 6.9,
         arrive="stars", leave="give", to="the weary one", made_of="a bolt of lightning that stops in the air",
         wish=dict(arrive="the bolt's branches bend into the strokes of the letters, violet to apricot",
                   leave="embers settle on her shoulders")),
    dict(expr="Inclusiveness", pos=(-6.0, 3.0, 77.3), width=8.4, label_size=0.32, face="camera",
         t_in=RAIN_STOP + 0.2, t_read0=S3 + 1.6, t_read1=S3 + 4.6, t_out=S3 + 5.6,
         arrive="gather", leave="sink", made_of="all the stopped rain within 60 m",
         wish=dict(arrive="beads from the whole dome, the nearest passing the lens",
                   leave="the beads fall again, slowly, like warm snow")),
    dict(expr="Concession", pos=(0.0, 2.25, 44.5), width=8.0, label_size=0.42, face="fixed", facing=0.0,
         t_in=WAVE_BOW + 0.1, t_read0=S4 + 0.8, t_read1=GATE, t_out=S4 + 4.2,
         arrive="lake", leave="wind", made_of="the great wave, which uncovers them as it bows",
         wish=dict(arrive="letters already standing, shown from the top down as the crest lowers",
                   leave="a gate: split between “Please,” and “after you.”, the halves swing open")),
    dict(expr="Respect", pos=(-2.65, 2.8, 49.0), width=5.4, label_size=0.32, face="camera",
         t_in=S4 + 3.7, t_read0=LISTEN, t_read1=S4 + 7.1, t_out=S5 - 0.03,
         arrive="gather", leave="give", to="the man who gives way", made_of="the wind's own streaks as it dies",
         wish=dict(arrive="ribbons slow, curl like handwriting and settle", leave="into the listener's chest")),
    dict(expr="Consideration", pos=(-17.3, 3.05, 30.0), width=6.4, label_size=0.36, face="camera",
         t_in=GRIP + 0.1, t_read0=S5 + 3.4, t_read1=S5 + 6.4, t_out=S5 + 7.4,
         arrive="gather", leave="sink", made_of="the spray of the last wave, hanging in an arc",
         wish=dict(arrive="the arc of spray settles", leave="it falls as fine spray")),
    dict(expr="Encouragement", pos=(0.0, 4.1, 9.5), width=8.2, label_size=0.38, face="camera",
         t_in=S6 + 1.4, t_read0=S6 + 3.0, t_read1=S6 + 6.0, t_out=S6 + 7.1,
         arrive="shaft", leave="give", to=(0.45, 1.25, 11.7), made_of="motes in the rays above Heavenly Mother",
         wish=dict(arrive="motes drifting in low rays, not a shaft from straight above",
                   leave="a stream down into her open right palm")),
    dict(expr="Gratitude", pos=(0.0, 6.0, 4.0), width=12.6, label_size=0.44, face="camera",
         t_in=S7 + 0.3, t_read0=S7 + 1.5, t_read1=S7 + 4.2, t_out=S7 + 4.9,
         arrive="lake", leave="sink", made_of="the sun's glitter, lifting off the water",
         wish=dict(arrive="glints rise from the sun's path", leave="the words bow (lean forward) and sink")),
    dict(expr="Compliment", pos=(0.0, 6.4, 10.0), width=9.2, label_size=0.42, face="camera",
         t_in=S7 + 4.2, t_read0=S7 + 4.9, t_read1=FINAL_HIT, t_out=S8 + 0.8,
         arrive="gather", leave="arch", made_of="light lifting off everyone's shoulders and raised hands",
         wish=dict(arrive="streams rise from the crowd", leave="a burst, then up to the arch")),
]
# After a word has left, its colour rests as a light under the glass at its site. When the circles run together
# the lights glide under the mirror to a ring of 9 m round Heavenly Mother's place (`angles`: degrees from +z,
# so they lie behind and beside her), and on the final hit they rise from there into the arch.
LIGHTS_UNDER_GLASS = dict(ring=9.0, center=MOTHER_POS, travel=(MERGE, EYE + 5.0),
                          rise=(FINAL_HIT, FINAL_HIT + 1.5), stagger=0.09,
                          angles={l: -100.0 + 25.0 * i for i, l in enumerate(LABELS)})

# ------------------------------------------------------------------------------------------------- people
# Lifelike bodies of points from helper BODY. `path` is where the feet are, `facing` the azimuth the body
# faces (degrees, 0 faces +z, 270 faces into the wind). `fill` is the look: 0 the storm look (a dark body with
# a burning rim, its light tearing away downwind), 1 the calm look (a full body of warm glitter). `motion`
# names are wishes for BODY's motion set; `touch` marks real contact between two bodies.
PEOPLE = [
    dict(name="the watcher", site=1, height=1.66, garment="long coat, head scarf",
         path=[(0.0, (-10.2, 0.0, 132.0))],
         facing=[(0.0, 270.0), (DROP_LAND + 0.1, 270.0), (S1 + 4.6, 90.0)],
         fill=[(0.0, 0.0), (DROP_LAND, 0.0), (S1 + 5.2, 1.0)],
         disperse=[(0.0, 0.55), (DROP_LAND, 0.55), (S1 + 5.0, 0.0)],
         motion=[(0.0, "brace"), (DROP_LAND + 0.1, "turn"), (S1 + 4.6, "stand"), (S1 + 5.2, "bow_head")]),
    dict(name="the stranger", site=1, height=1.80, garment="long coat",
         path=[(0.0, (-5.8, 0.0, 132.0))], facing=[(0.0, 270.0)],
         fill=[(0.0, 0.0), (DROP_LAND, 0.0), (S1 + 5.2, 1.0)],
         disperse=[(0.0, 0.45), (DROP_LAND, 0.45), (S1 + 5.0, 0.0)],
         motion=[(0.0, "brace"), (DROP_LAND + 0.3, "stand"), (S1 + 5.0, "raise_hand_greet"),
                 (S1 + 5.9, "stand")]),
    dict(name="the weary one", site=2, height=1.62, garment="robe and shawl",
         path=[(0.0, (11.4, 0.0, 104.0))], facing=[(0.0, 90.0)],
         fill=[(0.0, 0.0), (BOLT_FREEZE + 0.3, 0.0), (S2 + 4.5, 1.0)],
         disperse=[(0.0, 0.5), (BOLT_FREEZE, 0.5), (S2 + 4.0, 0.0)],
         motion=[(0.0, "kneel_hunched"), (S2 + 4.1, "lift_head"), (S2 + 5.9, "rise_helped")]),
    dict(name="the one who is sorry", site=2, height=1.76, garment="long coat",
         path=[(STRIKE, (16.2, 0.0, 104.8)), (S2 + 2.5, (12.55, 0.0, 104.1))], facing=[(0.0, 270.0)],
         fill=[(0.0, 0.0), (BOLT_FREEZE + 0.3, 0.0), (S2 + 4.5, 1.0)],
         disperse=[(0.0, 0.4), (S2 + 2.5, 0.4), (S2 + 4.0, 0.0)],
         motion=[(STRIKE, "walk_into_wind"), (S2 + 2.5, "kneel_one_knee"), (S2 + 3.1, "bow_head"),
                 (SHOULDER, "hand_on_shoulder"), (S2 + 5.9, "help_up")],
         touch=[(SHOULDER, "the weary one", "his hand on her shoulder")]),
    dict(name="the outsider", site=3, height=1.64, garment="long dress and shawl",
         path=[(0.0, (-6.0, 0.0, 78.0)), (S3 + 4.0, (-6.0, 0.0, 78.0)), (S3 + 4.6, (-6.3, 0.0, 78.1))],
         facing=[(0.0, 270.0)],
         fill=[(0.0, 0.0), (S3 + 2.0, 0.0), (S3 + 4.0, 1.0)],
         # her light is a long stream downwind; it hangs when the rain stops and then flows back into her
         disperse=[(0.0, 0.7), (S3 + 2.0, 0.7), (S3 + 4.0, 0.0)], disperse_hangs=(RAIN_STOP, S3 + 2.0),
         motion=[(0.0, "brace_arms_wrapped"), (S3 + 3.6, "look_up"), (S3 + 4.0, "step"),
                 (S3 + 4.6, "stand")]),
    dict(name="the first who welcomes", site=3, height=1.72, garment="tunic and trousers",
         path=[(S3 + 0.4, (-9.6, 0.0, 79.2)), (S3 + 3.8, (-7.0, 0.0, 78.3))], facing=[(0.0, 90.0)],
         fill=[(0.0, 0.0), (RAIN_STOP, 0.0), (S3 + 1.2, 1.0)],
         disperse=[(0.0, 0.3), (S3 + 1.0, 0.0)],
         motion=[(S3 + 0.4, "walk"), (S3 + 3.4, "open_arm"), (WELCOME, "arm_round_shoulder")],
         touch=[(WELCOME, "the outsider", "an arm round her shoulder")]),
    dict(name="the second who welcomes", site=3, height=1.58, garment="long coat",
         path=[(S3 + 0.8, (-2.6, 0.0, 79.4)), (S3 + 4.0, (-5.0, 0.0, 78.4))], facing=[(0.0, 270.0)],
         fill=[(0.0, 0.0), (RAIN_STOP, 0.0), (S3 + 1.2, 1.0)],
         disperse=[(0.0, 0.3), (S3 + 1.0, 0.0)],
         motion=[(S3 + 0.8, "walk"), (S3 + 4.3, "hand_on_back")],
         touch=[(S3 + 4.3, "the outsider", "a hand at her back")]),
    # the three of site 4 stand left and right of the place where the words will stand, backs to the camera
    dict(name="the man who gives way", site=4, height=1.82, garment="long coat",
         path=[(0.0, (-3.2, 0.0, 49.6))],
         facing=[(0.0, 180.0), (S4 + 1.1, 180.0), (S4 + 1.6, 90.0)],
         fill=[(0.0, 0.0), (WAVE_BOW, 0.0), (S4 + 1.6, 1.0)],
         disperse=[(0.0, 0.4), (WAVE_BOW, 0.4), (S4 + 1.4, 0.0)],
         motion=[(0.0, "brace"), (S4 + 1.1, "turn"), (S4 + 1.4, "step_aside_open_palm"),
                 (S4 + 4.0, "kneel_one_knee"), (S4 + 4.7, "lean_in_listen"), (S4 + 6.9, "nod")]),
    dict(name="the mother", site=4, height=1.68, garment="long dress",
         path=[(0.0, (3.1, 0.0, 49.9)), (S4 + 3.1, (3.1, 0.0, 49.9)), (S4 + 6.5, (0.6, 0.0, 45.4))],
         facing=[(0.0, 180.0)],
         fill=[(0.0, 0.0), (WAVE_BOW, 0.0), (S4 + 1.6, 1.0)],
         disperse=[(0.0, 0.35), (WAVE_BOW, 0.35), (S4 + 1.4, 0.0)],
         motion=[(0.0, "brace_shield_child"), (S4 + 0.6, "stand"), (S4 + 2.1, "bow_head"),
                 (S4 + 3.1, "walk")],
         touch=[(0.0, "the child", "she holds the child's hand until the child runs back")]),
    dict(name="the child", site=4, height=1.15, garment="tunic dress", child=True, gait="run",
         path=[(0.0, (2.5, 0.0, 50.0)), (S4 + 3.1, (2.5, 0.0, 50.0)), (S4 + 4.5, (-2.1, 0.0, 49.4))],
         facing=[(0.0, 180.0), (S4 + 3.1, 180.0), (S4 + 3.4, 270.0)],
         fill=[(0.0, 0.0), (WAVE_BOW, 0.0), (S4 + 1.6, 1.0)],
         disperse=[(0.0, 0.3), (WAVE_BOW, 0.3), (S4 + 1.4, 0.0)],
         motion=[(0.0, "hold_hand"), (S4 + 3.1, "run"), (S4 + 4.5, "stand"),
                 (S4 + 4.8, "speak_breath_of_light")]),
    dict(name="the one in the swell", site=5, height=1.74, garment="tunic and trousers", rim="#6fb4ff",
         rides_swell=True,
         path=[(0.0, (-18.5, 0.0, 30.5)), (GRIP + 0.4, (-18.5, 0.0, 30.5)), (GRIP + 1.6, (-18.0, 0.0, 30.5))],
         facing=[(0.0, 90.0)],
         fill=[(0.0, 0.0), (GRIP, 0.0), (GRIP + 2.4, 1.0)],
         disperse=[(0.0, 0.6), (GRIP, 0.6), (GRIP + 2.0, 0.0)],
         motion=[(0.0, "hands_and_knees"), (S5 + 1.9, "reach_up"), (GRIP, "grip"), (GRIP + 0.4, "pulled_up"),
                 (GRIP + 2.0, "hand_to_heart")]),
    dict(name="the runner", site=5, height=1.78, garment="tunic and trousers", look="plexus", gait="run",
         color="#ffc56e",
         path=[(RUN, (-5.5, 0.0, 33.2)), (S5 + 1.7, (-16.6, 0.0, 30.6))], facing=[(0.0, 270.0)],
         fill=[(0.0, 1.0)], disperse=[(0.0, 0.15), (S5 + 1.7, 0.0)],
         motion=[(RUN, "run"), (S5 + 1.7, "kneel_one_knee"), (S5 + 2.0, "reach_forward"), (GRIP, "grip"),
                 (GRIP + 0.4, "pull_up"), (GRIP + 1.6, "hand_on_shoulder")],
         touch=[(GRIP, "the one in the swell", "two hands grip at (-17.5, 0.75, 30.5)")]),
]
# Three more who stand alone in the storm; the sweeps of the first two sections pass close by them.
for _i, (_pos, _h, _g) in enumerate([((4.0, 0.0, 119.5), 1.74, "long coat"),
                                     ((6.5, 0.0, 117.5), 1.60, "long dress and shawl"),
                                     ((-3.5, 0.0, 113.0), 1.84, "long coat")]):
    PEOPLE.append(dict(name=f"alone {_i + 1}", site=0, height=_h, garment=_g, path=[(0.0, _pos)],
                       facing=[(0.0, 270.0)], fill=[(0.0, 0.0), (BURST + 0.2, 0.0), (BURST + 1.6, 1.0)],
                       disperse=[(0.0, 0.5), (BURST + 0.2, 0.5), (BURST + 1.6, 0.0)],
                       motion=[(0.0, "brace")]))

# Heavenly Mother: once, from behind, veiled, and as one open hand. She gathers out of the rays with her hands
# together, in a full robe from the shoulders; she dissolves upward where she stands, with no scaling.
MOTHER = dict(pos=MOTHER_POS, facing=MOTHER_FACING, height=1.85, garment="long robe and a long veil",
              color="#ffe6bc", rim="#ffd08a", veil_wind=0.0,
              gather=(EYE, EYE + 1.4), dissolve=(PALM + 0.1, BURST + 0.9), dissolve_kind="upward flakes",
              motion=[(EYE, "stand_hands_together"), (S6 + 1.9, "open_arms_low"), (S6 + 5.7, "raise_open_palm"),
                      (PALM, "release_light")],
              palm=(0.45, 1.25, 11.7), camera_stays_behind=125.0)
# Everyone: they walk in over the glass during the breath and stand in a wide crescent behind and beside her,
# leaving the way to the dawn open and an aisle behind her for the camera. After she is gone they step
# forward; nobody stands on her place, which keeps a soft gold light.
CROWD = dict(count=40, heights=(1.05, 1.88), children=0.2, clusters=(2, 4), look="glitter",
             arrive=(EYE + 0.3, BURST - 0.5), walk_speed=1.3, from_radius=60.0,
             stand=dict(center=MOTHER_POS, radius=(5.0, 24.0), azimuths=(-110.0, 110.0), aisle=3.2),
             step_forward=dict(t0=BURST + 1.0, t1=BURST + 2.6, metres=3.0), front_row_z=(7.4, 10.4),
             motion=[(EYE + 0.3, "walk"), (BURST - 0.5, "stand"), (BOWS, "turn_and_bow_hand_on_heart"),
                     (LIFT - 0.3, "look_up"), (LIFT, "raise_both_arms"), (S8 + 1.5, "stand_together")],
             stagger=0.8, rim="#ffd27a", fill="#ffe9c4")
DOVES = dict(count=9, t0=S8 + 2.0, t1=TOTAL, path=[(-46.0, 3.0, -30.0), (0.0, 7.0, -60.0), (50.0, 5.0, -40.0)],
             color="#fff1da")

# ------------------------------------------------------------------- the end card (the existing 2D text system)
# The existing end card style is kept: coral title, the label above it, three navy lines (theme.CORAL
# "#f0566a", theme.NAVY "#1f2a6b", theme.WHITE_GLOW "#fff8ec"). Nothing dark behind any text.
TEXT_SHADOW = 0.0
FORM_DUR = 1.0                        # a text is whole at form + FORM_DUR + 0.75
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=FINAL_HIT + 0.15, hold=1e9, star=1e9, color="#f0566a", glow="#fff8ec", anim="rise")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=S8 + 1.5, t1=CARD_WHOLE, color="#1f2a6b", glow="#fff8ec", anim="rise")
TITLE_WHOLE = TITLE["form"] + FORM_DUR + 0.75
# The expressions are particle words in the world (WORDS), so the 2D expressions stay off; `star` is when
# each light takes its place in the arch.
PHRASES = [dict(label=e["label"], lines=e["lines"], form=1e9, hold=1e9,
                star=FINAL_HIT + 1.5 + LIGHTS_UNDER_GLASS["stagger"] * i) for i, e in enumerate(EXPRESSIONS)]

# ------------------------------------------------------------------------------------------ the P3D key
WORLD = dict(
    stars=[(0.0, 0.0), (TOTAL, 0.0)],             # no stars: cloud, then day
    lake=dict(mirror="calm", storm=STORM, calm=calm_at, wave=WAVE, rain_hold=RAIN_HOLD),
    hills=[(0.0, 0.0), (BURST + 1.6, 0.0), (S8 + 1.9, 0.5), (TOTAL, 0.5)],   # pale far hills only by day
    sky=dict(palettes=PAL, keys=PALETTE_KEYS, sun_az=SUN_AZ, sun_elev=SUN_ELEV, sun_gain=SUN_GAIN),
    rays=RAYS, mist=MIST, exposure=EXPOSURE, lightning=LIGHTNING, wind=WIND_DIR,
    arch=dict(lit_from=FINAL_HIT, rise=LIGHTS_UNDER_GLASS, colors=[e["color"] for e in EXPRESSIONS]),
    motes=[(0.0, 0.0), (EYE, 0.6), (BURST + 2.0, 0.4), (TOTAL, 0.3)],
)


def word_specs():
    """The WORDS as settings for p3d.words.Word (only the keys it knows; a `to` that names a person is left
    for phase B, when the people are point sets)."""
    known = ("expr", "pos", "width", "label_size", "face", "facing", "t_in", "t_read0", "t_read1", "t_out",
             "arrive", "leave")
    out = []
    for w in WORDS:
        s = {k: w[k] for k in known if k in w}
        if isinstance(w.get("to"), tuple):
            s["to"] = w["to"]
        out.append(s)
    return out


def build(scene):
    """Fills the 3D scene. Phase A: the nine words, and stand-in figures at each person's first place, enough
    for framing stills once CORE lands. Phase B: the storm sea, rain, wind, lightning, the wave, real bodies."""
    from p3d.api import StandIn
    from p3d.words import Words
    Words(word_specs()).add_to(scene)
    for p in PEOPLE:
        scene.add(p["name"], StandIn(pos=p["path"][0][1], height=p["height"], facing=p["facing"][0][1],
                                     look="rim" if p["fill"][0][1] < 0.5 else "glitter"))
    scene.add("Heavenly Mother", StandIn(pos=MOTHER["pos"], height=MOTHER["height"], facing=MOTHER["facing"],
                                         color=MOTHER["color"]))


P3D = dict(camera=camera_at, world=WORLD, setup=build)

# ------------------------------------------------------------------------------------------------- needs
# What this film needs from the 3D layer beyond what P3D-BRIEF.md promises, most important first.
NEEDS = [
    ("CORE", "A storm sea with a calm field. The lake as a heaving surface of points (three trains of swell up "
             "to 2.5 m, spray off the crests) whose height, mirror strength and ripples follow a field "
             "calm(x, z, t) of growing discs, with a soft line of light on the travelling edge. A true mirror "
             "only where it is calm. One rearing wave up to 9 m that can bow down into the plane."),
    ("CORE", "Rain and wind that can stop. Streaks of rain and long wind ribbons in a volume round the camera, "
             "slanted by a wind vector, with a local time scale from the calm field (drops hang, then fall "
             "slowly), offered as point sets so a word can gather its letters from them."),
    ("BODY", "A look that blends over time from the storm look (dark body, burning rim, light tearing away "
             "downwind) to the calm look (full glitter), with the dispersal able to hang and run backwards "
             "(the light flows back into the body), and wind strength per person for coat, scarf and veil."),
    ("BODY", "Motions with contact: brace against wind, turn in place, bow with a hand on the heart, kneel on "
             "one knee and lean in to listen, a hand on another's shoulder, step aside with an open palm, on "
             "hands and knees, grip and pull up (two bodies, hands meeting at a given point), raise both arms. "
             "A child's proportions. Walking and running locked to the ground (no sliding)."),
    ("CORE", "A storm sky: a low cloud lid that lifts off the horizon (a clear band that widens, widest "
             "toward the sun) and opens a door in the storm wall; lightning as a branching bolt of line "
             "segments plus a short light that glows inside the cloud and rims the bodies; one bolt that can "
             "stop in the air and hand its points to a word."),
    ("WORDS", "Per word: shown from the top down behind a lowering height (the wave); leaving as a gate "
              "(split at a chosen gap, the halves swing open); tilt as a function of time (the words bow); "
              "leaving into a moving point (a palm, a chest); a mirror image only where the water is calm."),
    ("CORE", "Camera: shake and roll as Tracks, focus and aperture as Tracks, motion blur on fast flights, "
             "and a flash cut between two shots."),
    ("CORE", "Lights that glide under the glass and rise out of it into the nine places of the arch, each in "
             "its own colour; an exposure Track for the final hit."),
]


# ---------------------------------------------------------------------------------------- the plan's check
class _Cam:
    """A small camera for the checks below (the same projection as p3d.api.CameraState)."""

    def __init__(self, v):
        self.pos, self.target = np.asarray(v["pos"], np.float64), np.asarray(v["target"], np.float64)
        self.fov, self.roll = v["fov"], v["roll"]

    def basis(self):
        f = self.target - self.pos
        f = f / np.linalg.norm(f)
        r = np.cross(f, [0.0, 1.0, 0.0])
        r = r / np.linalg.norm(r)
        return r, np.cross(r, f), f

    def project(self, pts):
        r, u, f = self.basis()
        d = np.asarray(pts, np.float64).reshape(-1, 3) - self.pos
        z = d @ f
        fl = 1.0 / np.tan(np.radians(self.fov) * 0.5)
        return np.stack([(d @ r) * fl / (ASPECT * z) * 0.5 + 0.5, (d @ u) * fl / z * 0.5 + 0.5], axis=1), z


def _word_box(w, cam):
    """Corners of a word (label included) and the height of one em, from the rough extents of words.py."""
    e = EXPRESSIONS[LABELS.index(w["expr"])]
    em = w["width"] / (0.40 * max(len(l) for l in e["lines"]))
    half_w, block = w["width"] / 2.0, 1.08 * len(e["lines"]) * em
    y0, y1 = -block / 2.0, block / 2.0 + (0.30 + 0.70 * w.get("label_size", 0.30)) * em
    o = np.asarray(w["pos"], np.float64)
    if w.get("face") == "camera":
        d = cam.pos - o
        a = np.arctan2(d[0], d[2])
    else:
        a = np.radians(w.get("facing", 0.0))
    right, normal = np.array([np.cos(a), 0.0, -np.sin(a)]), np.array([np.sin(a), 0.0, np.cos(a)])
    corners = [o + right * sx * half_w + np.array([0.0, sy, 0.0]) for sx in (-1, 1) for sy in (y0, y1)]
    view = cam.pos - o
    return np.array(corners), em, abs(float(view @ normal)) / float(np.linalg.norm(view))


def check(quiet=False):
    """Checks the plan and returns the list of problems (empty when all is well)."""
    problems, notes = [], []
    if any(b <= a for a, b in zip(SECTIONS, SECTIONS[1:])) or len(SECTIONS) != 8:
        problems.append("SECTIONS must be eight rising times")
    # every list of keys rises in time (the engine's Track refuses anything else)
    lists = dict(PALETTE_KEYS=PALETTE_KEYS, SUN_ELEV=SUN_ELEV, SUN_GAIN=SUN_GAIN, RAYS=RAYS, MIST=MIST,
                 EXPOSURE=EXPOSURE, LIGHTNING=LIGHTNING, crowd=CROWD["motion"], mother=MOTHER["motion"])
    lists.update({"STORM " + k: v for k, v in STORM.items() if isinstance(v, list)})
    lists.update({"WAVE " + k: v for k, v in WAVE.items() if isinstance(v, list)})
    lists.update({"CALM " + c["name"]: c["radius"] for c in CALM})
    lists.update({f"WORLD {k}": v for k, v in WORLD.items() if isinstance(v, list) and k != "lightning"})
    for q in PEOPLE:
        lists.update({f"{q['name']} {k}": q[k] for k in ("path", "facing", "fill", "disperse", "motion")})
    for i, r in enumerate(_RUNS):
        lists[f"camera run {i + 1}"] = [(k["t"],) for k in r]
    for name, keys in lists.items():
        if any(b[0] <= a[0] for a, b in zip(keys, keys[1:])):
            problems.append(f"{name}: its key times do not rise")
    # the nine expressions: all there, exact wording, in order, read long enough, never two read at once
    if [w["expr"] for w in WORDS] != ["Greeting", "Apology", "Inclusiveness", "Concession", "Respect",
                                      "Consideration", "Encouragement", "Gratitude", "Compliment"]:
        problems.append("WORDS: the nine expressions are not all there in the film's order")
    if sorted(w["expr"] for w in WORDS) != sorted(LABELS):
        problems.append("WORDS: not exactly the nine campaign labels")
    last_end = -1.0
    for w in WORDS:
        if not (w["t_in"] < w["t_read0"] < w["t_read1"] <= w["t_out"]):
            problems.append(f"{w['expr']}: its four times are out of order")
        read = w["t_read1"] - w["t_read0"]
        if read < 2.5:
            problems.append(f"{w['expr']}: read for {read:.2f} s, less than 2.5 s")
        if w["t_in"] < last_end:
            problems.append(f"{w['expr']}: it begins to arrive while the word before it is still being read")
        last_end = w["t_read1"]
        worst_x, worst_cap, worst_w, worst_face, inside, sun_gap = 1e9, 1e9, 1e9, 1.0, True, 90.0
        for t in np.linspace(w["t_read0"], w["t_read1"], 13):
            cam = _Cam(camera_values(float(t)))
            corners, em, facing = _word_box(w, cam)
            xy, z = cam.project(corners)
            em_px = em / (2.0 * float(np.mean(z)) * np.tan(np.radians(cam.fov) * 0.5)) * 1080.0
            worst_x = min(worst_x, 0.40 * em_px)
            worst_cap = min(worst_cap, 0.70 * w.get("label_size", 0.30) * em_px)
            worst_w = min(worst_w, float(xy[:, 0].max() - xy[:, 0].min()))
            worst_face = min(worst_face, facing)
            inside = inside and bool(z.min() > 0 and xy.min() > 0.02 and xy.max() < 0.98)
            # the sun (or its glow under the horizon) must not sit close under the letters
            if _keys(SUN_GAIN, float(t)) > 0.05:
                a, e = np.radians(SUN_AZ), np.radians(max(_keys(SUN_ELEV, float(t)), 0.0))
                far = cam.pos + 1e6 * np.array([np.sin(a) * np.cos(e), np.sin(e), np.cos(a) * np.cos(e)])
                sxy, sz = cam.project(far)
                if sz[0] > 0 and xy[:, 0].min() - 0.03 < sxy[0, 0] < xy[:, 0].max() + 0.03:
                    sun_gap = min(sun_gap, float(xy[:, 1].min() - sxy[0, 1]) * cam.fov)
        if sun_gap < 5.0:
            problems.append(f"{w['expr']}: the sun is only {sun_gap:.1f} degrees under the letters")
        notes.append(f"{w['expr']:14s} read {w['t_read0']:5.2f} to {w['t_read1']:5.2f} ({read:.1f} s), "
                     f"{100 * worst_w:3.0f} percent of the width, x-height {worst_x:3.0f} px at 1080p "
                     f"({worst_x / 32.0:.2f} mm on a 6 cm phone), label {worst_cap / 32.0:.2f} mm, "
                     f"facing {worst_face:.2f}")
        if not inside:
            problems.append(f"{w['expr']}: not wholly inside the picture while it is read")
        if worst_x < 28.8:
            problems.append(f"{w['expr']}: too small to read on a phone (x-height {worst_x:.0f} px at 1080p)")
        if worst_cap < 0.85 * 32.0:
            problems.append(f"{w['expr']}: its label is too small on a phone ({worst_cap / 32.0:.2f} mm)")
        if worst_face < 0.72:
            problems.append(f"{w['expr']}: seen too much from the side while read")
    # the camera: always moving, never absurdly fast, the horizon level inside a calm
    ts = np.arange(0.0, TOTAL, 1.0 / FPS)
    cut_t = [r[0]["t"] for r in _RUNS[1:]]
    pos = np.array([camera_values(float(t))["pos"] for t in ts])
    tgt = np.array([camera_values(float(t))["target"] for t in ts])
    speed = np.linalg.norm(np.diff(pos, axis=0), axis=1) * FPS
    turn = np.linalg.norm(np.diff(tgt, axis=0), axis=1) * FPS
    for c in cut_t:
        speed[np.abs(ts[1:] - c) < 1.5 / FPS] = np.nan
    still = ts[1:][(speed < 0.12) & (turn < 0.12)]
    if still.size:
        problems.append(f"the camera stands still at {still[0]:.2f} s ({still.size} frames in all)")
    if np.nanmax(speed) > 45.0:
        problems.append(f"the camera reaches {np.nanmax(speed):.0f} m/s at {ts[1:][np.nanargmax(speed)]:.2f} s")
    notes.append(f"camera: slowest {np.nanmin(speed):.2f} m/s, fastest {np.nanmax(speed):.1f} m/s at "
                 f"{ts[1:][np.nanargmax(speed)]:.2f} s, one cut at {cut_t[0]:.2f} s")
    for i, name in enumerate(SECTION_NAMES):
        a = SECTIONS[i]
        b = SECTIONS[i + 1] if i < 7 else TOTAL
        m = (ts[1:] >= a) & (ts[1:] < b)
        notes.append(f"section {i + 1} ({name}): camera travels {np.nansum(speed[m]) / FPS:5.1f} m, "
                     f"mean {np.nanmean(speed[m]):4.1f} m/s")
    # the camera's shake against the calm field at its own place (two shakes are the camera's own: the jolt
    # of the strike at the first circle's edge, and its running beside the runner)
    for t in ts:
        v = camera_values(float(t))
        c = float(calm_at(v["pos"][0], v["pos"][2], float(t)))
        own = RUN <= t <= GRIP or STRIKE <= t <= STRIKE + 0.8
        if c > 0.95 and v["shake"] > 0.45 and not own:
            problems.append(f"the camera shakes ({v['shake']:.2f}) inside a calm at {t:.2f} s")
            break
        if c < 0.05 and v["shake"] < 0.1 and 0.5 < t < RAIN_STOP:
            problems.append(f"the camera is steady ({v['shake']:.2f}) in the open storm at {t:.2f} s")
            break
    # nobody fills with light while still in the storm
    for p in PEOPLE:
        for t in np.arange(0.0, TOTAL, 0.25):
            if _keys(p["fill"], float(t)) > 0.6 and p.get("look") != "plexus":
                pa = p["path"]
                xz = [np.interp(t, [k[0] for k in pa], [k[1][i] for k in pa]) for i in (0, 2)]
                if float(calm_at(xz[0], xz[1], float(t))) < 0.5:
                    problems.append(f"{p['name']}: full of light at {t:.2f} s while still in the storm")
                    break
    # Heavenly Mother: whenever she is in the picture the camera is behind her
    mf = np.array([np.sin(np.radians(MOTHER_FACING)), 0.0, np.cos(np.radians(MOTHER_FACING))])
    chest = np.asarray(MOTHER_POS) + np.array([0.0, 1.3, 0.0])
    worst = 180.0
    for t in np.arange(MOTHER["gather"][0], MOTHER["dissolve"][1] + 1e-6, 1.0 / FPS):
        cam = _Cam(camera_values(float(t)))
        xy, z = cam.project(chest)
        if z[0] > 0 and -0.2 < xy[0, 0] < 1.2 and -0.2 < xy[0, 1] < 1.2:
            d = cam.pos - chest
            d[1] = 0.0
            ang = float(np.degrees(np.arccos(np.clip(d @ mf / np.linalg.norm(d), -1.0, 1.0))))
            worst = min(worst, ang)
    notes.append(f"Heavenly Mother: the camera is never less than {worst:.0f} degrees round from her front")
    if worst < MOTHER["camera_stays_behind"]:
        problems.append(f"Heavenly Mother is seen from {worst:.0f} degrees round, which is not from behind")
    # people: walking speeds
    for p in PEOPLE:
        for (ta, a), (tb, b) in zip(p["path"], p["path"][1:]):
            v = float(np.linalg.norm(np.subtract(b, a))) / (tb - ta)
            top = 7.5 if p.get("gait") == "run" else 1.9
            if v > top:
                problems.append(f"{p['name']}: {v:.1f} m/s between {ta:.1f} and {tb:.1f} s is too fast")
    # the end card: readable for at least 4 s, to the last frame
    notes.append(f"end card: title whole at {TITLE_WHOLE:.2f} s, lines at {CARD_WHOLE:.2f} s, "
                 f"{TOTAL - CARD_WHOLE:.1f} s to the last frame")
    if TOTAL - max(CARD_WHOLE, TITLE_WHOLE) < 4.0:
        problems.append("the end card is readable for less than 4 s")
    if WORDS[-1]["t_out"] > TITLE_WHOLE:
        problems.append("the last expression is still leaving when the title is whole")
    # lightning: never two in one second
    lt = sorted(l[0] for l in LIGHTNING)
    if any(b - a < 0.85 for a, b in zip(lt, lt[1:])):
        problems.append("two lightning flashes within one second")
    # no long dashes anywhere in this file
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        src = f.read()
    if any(ch in src for ch in (chr(0x2013), chr(0x2014))):
        problems.append("a long dash in this file")
    # the particle words' own check, when the 3D layer is at hand
    try:
        from p3d.words import Words
        from p3d.words import check as words_check
        more, _ = words_check(Words(word_specs()), camera_at, quiet=True)
        problems.extend("words.py: " + s for s in more)
        notes.append("words.py check ran: " + ("no problems" if not more else f"{len(more)} problems"))
    except ImportError:
        notes.append("words.py is not on the path: its own check was skipped")
    if not quiet:
        for s in notes:
            print(s)
        for s in problems:
            print("PROBLEM:", s)
        print("ok" if not problems else f"{len(problems)} problems")
    return problems


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(HERE))   # engine/, so that p3d is found when the 3D layer is merged
    raise SystemExit(1 if check() else 0)
