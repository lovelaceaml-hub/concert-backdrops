"""Film 07 of ten: THE RELAY. One light, carried by many.
A 60 second promo for the Healing Concert "The Words of Mother's Love", on the 3D layer (engine/p3d).

PHASE A: DIRECTION, NOT A FILM YET. This file holds the treatment (this text) and the whole timeline as data:
section times, the road, the carriers and where each one is at every moment, the hand-overs, the palettes, the
nine expressions as settings for the particle words (engine/p3d/words.py), and the camera as keyframes in
metres. It imports with numpy alone and checks itself:

    python engine/songs/ten_07_the_relay.py        (prints the timeline and every problem it finds)

With engine/p3d on the path the same check also runs the words' own test against this camera: every
expression inside the picture, facing the lens and large enough for a phone through its whole reading moment.
(Run that way against branch engine-p3d-words at 0ed3cd7 it finds no problem. Sizes there are estimates,
because the fonts are fetched only at render time.)

What the engine still needs before it can render this (the Song class, params(), the sky Tracks, the real
point sets for bodies, flame, weather and crowd) comes in phase B, when engine-p3d, engine-p3d-bodies and
engine-p3d-words have landed. Nothing here is rendered or proven yet.

LOGLINE
  A flame leaves a pair of open hands and is carried flat out through seven worlds by seven ordinary people.
  Every time it changes hands, a Word of Mother's Love bursts from the touch. Then the fastest runner falls
  and the flame is scattered, and the three words that follow (I'm sorry, can I give you a hand, it's okay)
  put it back together larger than it was, in the hands of a child. She carries it home to the hands it came
  from, and from those hands the day breaks.

WHAT MAKES THIS FILM ITSELF (and keeps it apart from the other nine)
  1. It is shot like a sports film. The camera runs beside the carrier at her speed, so she holds her place
     in the frame, large, while the world streaks past with motion blur. In the close work people fill half
     the height of the frame or more. Twice it goes wide on purpose for about two seconds (a small runner
     under huge words; the wave across the field), and there the flame keeps the eye on the carrier.
  2. One rule, repeated and varied: hand-over = contact = a word = a new world. Seven times two hands meet,
     close to the lens, and each meeting is a different human act, because it is an expression acted out.
  3. Gold belongs to the flame. Every world before the last is cool (indigo, storm violet, steel blue, sea
     green, royal blue, ash blue, plum); gold is only the flame, what it sheds on the road and what it
     touches. So the gold grows through the film, and full warm daylight is kept for the end.
     The words are the flame's own colour, never colour coded (that is film 10's idea).
  4. The words are things in the race, not captions: the first is carried above the sprinter, two are finish
     tapes that a carrier breaks, one is what a spent runner turns into, one hangs in sea spray while time
     slows, one is written across the sky over a rooting crowd, three are a conversation over a fall.
  5. A circle. The hands that give the flame in the first second are the hands that receive it at the end:
     Heavenly Mother's, seen only as hands, and later only from behind. The words come from her, pass through
     everyone, and come home as the day.
  6. It has a fall in it. The relay fails at the loudest point of the middle, and the failure is what turns
     the watching crowd into carriers. The message is acted, not stated: these words bring peace.

THE MUSIC (the real section map of the new medley, branch epic-medley2, commit 45017af)
  Eight songs: 0.00, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47. Opening hit 0.25. Slow songs first, fast
  ones from 19.85 to 40.21, a breath from 40.21 to 42.51, the biggest jump of the mix at 42.51, the finale
  from 49.47 with its loudest passage at 54.3 to 55.0 and a last hit at 58.11. Every time in this file hangs
  off the list S and the dictionary HIT below, so a new cut of the medley is one edit. (The brief's stand-in
  grid of 7.5 s sections was replaced by this map as soon as it existed.)

THE ROAD
  One straight causeway of light on the lake, 230 m long, running toward the arch of nine lights (toward -z in
  the world of engine/p3d/api.py). The carriers run from z = 262 m to z = 31 m. Near the end it climbs 20 m
  up a hill 6 m high, and Heavenly Mother stands on the level brow, facing away from us toward the arch and
  the place where the sun will rise. Every carrier sheds light as she runs (ref 15) and the light stays on
  the road, so the road behind the flame is a line of gold. In the last shot we see all of it at once.

THE PEOPLE (lifelike bodies of points, clothed in garments of light, no faces; looks and effects from the
brief; seen from the side, from behind or from above, never from the front)
  the giving hands  Heavenly Mother, hands only: warm white, a sleeve of veil. First second, and the end.
  sprinter          a young woman. Plexus of gold points and lines (refs 12, 3), tunic, a head scarf that
                    streams behind. Sprints. After her leg she slows, stands and breaks upward into flakes.
  coat              a man in a long coat. Cool blue white glitter (ref 15) that turns gold on the side of the
                    flame. Runs bent over the flame in the rain. Spent, he becomes his thanks (ref 5, 11, 13).
  shawl             a woman with a shawl. Dotted body in sea green and pearl (ref 14); the shawl is a cloth of
                    light she wraps round the flame. Runs the shore; particles stream off the back of her
                    head (ref 16); birds lift where she passes (ref 8).
  elder             an old man, a little stooped, long coat. A dark body with a gold rim (refs 1, 16). He does
                    not sprint: he walks, then strides. Nobody hurries him.
  youth             a lanky boy. Electric blue white plexus (ref 3). The fastest. He falls.
  helper            a young mother out of the crowd. Warm rose gold glitter (refs 9, 15), long dress. Runs in,
                    kneels in profile facing him, holds out an open palm, grips his hand (ref 4), lifts him.
  child             her daughter, 1.15 m tall. The brightest body in the film. Kneels to gather embers in
                    cupped hands, runs, walks the last steps, lifts the flame with both hands.
  the crowd         ten thousand small lights in a field, the nearest sixty of them people with a dark body
                    and a rim of light (ref 1), each holding one light. They lift it as the flame passes.
  Heavenly Mother   on the brow of the hill from 44 s, only ever from behind: veiled, robed, the veil a
                    stream of particles in the wind, rays behind her head (ref 10). She lowers an open hand to
                    meet the child's hands, gathers the flame, raises it, opens her arms.

TIMELINE (what the eye sees; where the camera is; what the light does)
  0.00 to 6.84   NIGHT ROAD. Black lake, star dome, Milky Way. Frame 0 is already bright: a flame between two
     hands, huge and close, in gold bokeh. On the opening hit (0.25) the hands touch, the flare whites the
     frame warm, and the camera whips back to find the sprinter in full stride, in profile, 4.4 m away, her
     feet striking rings of gold out of the black road. THE GREETING bursts from the touch and travels above
     her (1.2 to 3.75). Push in to head, shoulders and flame arm (ref 16), then fall back behind her: the road
     ahead, a man looking back with an open hand, and far off one light of the arch waking.
  6.84 to 13.30  RAIN OF SPARKS. Hand-over 1, at full speed: the camera loops over the top of the two hands
     at the flare and comes down behind the man. She sweeps her arm forward, falls back and breaks into flakes
     that pass the lens. The sky is now storm violet and raining white gold sparks, every drop a ring on the
     black mirror. Ahead a tape of light hangs across the road with THE CONCESSION above it (7.4 to 9.9): the
     camera drops far back so he runs small toward huge words, then rushes in as he breaks the tape on the hit
     (10.44) and the letters burst past us. Close profile: the rain is beating the flame flat, he bends over it.
  13.30 to 19.85 THE SHORE OF BIRDS. Hand-over 2: a woman wraps her shawl round the flame as she takes it. At
     the touch the rain stops in the air; on the hit (14.14) every drop turns and climbs as a bird, into a
     steel blue hour with a band of pearl on the horizon. The camera stays with the man, rising round him as
     he slows, bows and breaks upward into flakes that settle as THE GRATITUDE (14.3 to 17.9), while the flame
     goes on along the wet sand. On the hit (18.20) the birds carry the letters away down the shore and
     the camera dives after them, half a metre above the sand, to a profile close-up of the woman running.
  19.85 to 26.79 THE SEA WALL. Hand-over 3, as the bass slams in: the sea leaps on both sides of the road and
     hangs there, because time has slowed to a quarter. An old man is waiting. She does not pass the flame and
     go: four hands hold it, and they walk it together, in step, at his pace. THE RESPECT gathers out of
     the hanging spray above them (20.6 to 23.9). Low side camera at walking pace, drops as big as lamps in
     the foreground. At 24.45 time snaps back, the sea falls, and the camera corkscrews up and over the old
     man as he strides the wall alone with the flame held high.
  26.79 to 33.36 THE FIELD OF LIGHTS. Hand-over 4, on the 8 dB jump: the boy takes it and is gone. The camera
     whips to look down the road and the field wakes in front of us row on row to the horizon, ten thousand
     cool lights, each one held by a person. The touch throws a comet up the sky that writes THE
     ENCOURAGEMENT there, the size of a hill (29.0 to 31.6). Crane up: wherever the flame is, the lights go up
     overhead and turn gold, a stadium wave that races the runner. Then down into the crowd, rims of gold
     passing as bokeh, then right behind his heels at 8.4 m/s, lens wide, the stride starting to break.
  33.36 to 40.21 THE SCATTERED FLAME. On the 10 dB jump he falls. The flame hits the road and bursts into a
     thousand embers that skitter away into the field; the wave stops; every lifted light sinks and cools.
     The camera overshoots him, swings back and comes down onto the road beside him. THE APOLOGY rises out of
     the dark mirror he is kneeling on (34.4 to 36.95). The music is at its fastest and so is everyone else:
     people run in from all sides. A young mother kneels facing him, profile to profile, and from her open
     palm come the words of THE CONSIDERATION, whole on the hit (37.42) as her hand grips his, gold on blue,
     and flares (to 39.95). On the next hit (39.12) she has him on his feet. All round them people are lifting
     embers off the ground: the dark fills with small gold lights held in open hands.
  40.21 to 42.51 THE STILL CIRCLE (the breath). Hush, ground mist, one pale shaft from above (ref 13). A child
     kneels in the middle with empty cupped hands. Every palm in the circle gives up its ember (ref 14): the
     streams cross above her and for one breath they are THE INCLUSIVENESS (39.95 to 42.51). The camera
     drifts in. Then the words pour down into her hands.
  42.51 to 49.47 THE HILL OF LANTERNS. On the biggest jump of the mix the flame is whole, three times the size
     it was. Lanterns lift off the ground on every side into a plum sky, and she runs. The camera whips in
     behind her, low, and everyone runs with her: the boy, the mother, the sprinter, the man, the woman, the
     old man last. Two people of the field run ahead holding a tape across the road, THE COMPLIMENT above it
     (43.0 to 45.64; the camera hangs back so the words stay whole in the frame). She breaks it on the hit.
     Its sparks climb to the arch and the nine lights wake in a run. On the brow a veiled figure stands with
     her back to us. The company stops below the brow; the child walks the last steps alone. Close: an open
     hand comes down, two small hands lift the flame into it.
  49.47 to 60.00 DAY. Behind Heavenly Mother, half body, veil streaming. She gathers the light in front of her
     and raises it; rays fan round her head (ref 10); a first band of rose gold opens on the horizon. On the
     bar (52.26) she opens her arms and the day leaves her hands as a ring that crosses lake, hills and sky,
     night on one side of it and the campaign day on the other. It throws the camera back over the lifted arms
     of the company and up, until the whole road they ran lies under us, gold from end to end, in full
     daylight. The title is whole on the loudest passage (54.3); date and place by 55.2; the card holds to
     the last frame (4.8 s), still drifting. On the last hit (58.11) the nine lights flare and leaves and soft
     bubbles burst in from the edges. No fade.

THE NINE EXPRESSIONS (exact campaign wording, label above; all in the flame's warm white and gold, but
the Apology, which is cold white because the flame is out)
  Greeting        1.2 to 3.75   bursts from the first touch; carried above the sprinter at her speed; then
                                stretches back along the road into her wake.
  Concession      7.4 to 9.9    thrown ahead by hand-over 1, stands over a finish tape; the man breaks it and
                                the letters rush past the lens.
  Gratitude       14.3 to 17.9  the spent man's own flakes settle as the words; birds carry them away.
  Respect         20.6 to 23.9  gathers from sea spray that hangs while time is slowed; falls as water when
                                time returns.
  Encouragement   29.0 to 31.6  written on the sky by a comet from hand-over 4, above the wave of lifted
                                lights; closes into a spark that flies to the arch.
  Apology         34.4 to 36.95 rises out of the dark mirror where he fell, cold white (the flame is out);
                                sinks back.
  Consideration   37.4 to 39.95 poured from the helper's open palm, whole as the hands grip; breaks into the
                                embers that the people lift.
  Inclusiveness   39.95 to 42.5 the embers from every palm gather into it above the child; it pours into her
                                hands and is the flame.
  Compliment      43.0 to 45.64 a tape held up by two people running ahead of her; she breaks it; nine sparks
                                go up to the arch.
  After its reading moment each word closes into a spark that flies ahead to its light on the far arch, so the
  goal we are running toward gets brighter all film, and is whole when the child reaches it.

PALETTE (sky top, middle, horizon; then the light)
  night road       #02030f #070d2e #141c4a   flame gold #ffc24a, stars, Milky Way
  rain of sparks   #0b0820 #1c1440 #3a2a66   rain #ffe9c0, rings on the mirror
  shore of birds   #0c1a3a #2a4470 #8fa3c0   pearl band, pale birds, mist
  sea wall         #031a22 #0a3d48 #1f6e72   spray #e8fff8
  field of lights  #060a3a #10206e #2a3fa0   lights #bcd0ff turning #ffd27a under the wave
  scattered flame  #06080f #10141f #232a3a   embers #ff9a4a, then held gold
  still circle     #101624 #232c40 #465066   one shaft #dfe8ff
  hill of lanterns #0a0830 #241a5c #6a3a78   lanterns #ffb45a and #ff8f6e, a seam of amber ahead
  day              the campaign day of engine/theme.py (sky blue, cream, white gold); coral title, navy lines

THREE WOW MOMENTS
  1. 13.30 to 14.14: the rain stops in mid air at the touch of two hands, and every drop turns and rises as a
     bird, while a man becomes the words that thank him.
  2. 26.79 to 33.36: a field of ten thousand people lifts its lights in a wave that races the runner under
     words as wide as the sky; then he falls, the flame bursts into a thousand embers, and the field goes dark.
  3. 52.26 to 54.3: the day leaves Heavenly Mother's hands as a ring across the whole world and throws the
     camera back down the lit road.

THE ENDING
  The existing end card (title TITLE with its label, three lines TAGLINE), unchanged in style, over the
  bright day: "The Words of Mother's Love", "Healing Concert", "Sunday, December 6 · 4:30 PM", "World Mission
  Society Church of God", "6720 W Sahara Ave, Las Vegas". Whole from 55.2 to 60.0. Under it, small: the arch,
  Heavenly Mother from behind with the company round her, and the gold road.

WHAT THIS FILM NEEDS FROM THE 3D LAYER BEYOND THE BRIEF (most important first)
  1. Hands that really meet. An arm that can be told "this hand is at this point in space at this time" while
     the body runs, walks or kneels, and a way to ask a body where its hand, head and chest are at t (for the
     flame, the flare, the focus and the camera). Without it there is no relay.
  2. Bodies that travel along a path without sliding: stride matched to speed, speeding up and slowing down,
     up a slope; and a clock of their own (a function from song time to body time) for the quarter speed
     passage and for carried momentum.
  3. Motion blur that includes the camera's own movement, with the shutter as a setting over time (whip pans
     and speed need it; reading moments need it off for the words).
  4. Motions not in the brief: a stumble into a fall on hands and knees, rising by a pulled hand, running bent
     over a flame, wrapping a cloth round a hand, two people carrying one thing in step, lifting a light
     overhead, a child (child proportions) who kneels with cupped hands, runs and reaches up with both
     hands, and Heavenly Mother from behind lowering one open hand, then raising both hands, then opening
     her arms.
  5. A change of world as a moving front: night to day as a sphere that grows from a point in space (the
     hands), and quick cuts of the whole world state (sky, weather, haze, water) inside a whip pan.
  6. A light that lives in the scene: the flame as a point that brightens and warms the particles near it and
     casts rays that bodies block (the hands at the end), not only the sun in the sky.
  7. A cheap crowd: one body repeated many times at low point counts with its own place, height, phase and
     colour, plus a "lift" amount per person that can travel as a wave.
  8. For the words: a tape under a word that breaks when a body crosses it; a word made out of another point
     set's own particles (a dissolving body, hanging spray); a far arrival (a comet that travels 200 m before
     it unfolds); words that keep sharp and unblurred while they move at running speed.
  9. Water and weather as point sets that obey the clock: rain that can stop and reverse and become birds,
     spray that hangs, a rough sea instead of the mirror, rings on the lake at given points and times,
     lanterns that lift on a cue, a shaft of light from straight above at a chosen place.
  10. Ground that is not flat: a road that climbs, which bodies, reflections, mist and the camera respect.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
try:
    from track import Track
except ImportError:                             # run on its own: python engine/songs/ten_07_the_relay.py
    import sys
    sys.path.insert(0, os.path.dirname(HERE))
    from track import Track

SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))
AUDIO_FILE = "audio/promo/concert-medley.mp3"   # the NEW medley (branch epic-medley2), same path as the old

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
MUSIC_END = 59.6
SONG_END = 60.0
TOTAL = 60.0
NFRAMES = int(round(TOTAL * FPS))
TEXT_SHADOW = 0.0      # nothing dark behind any text

# =====================================================================================================
# THE MUSIC: section starts and hits of the new medley (measured by the helper who cut it). Everything
# below hangs off these two tables.
# =====================================================================================================
S = [0.00, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47]
SECTIONS = ["night road", "rain of sparks", "shore of birds", "sea wall", "field of lights",
            "scattered flame", "still circle, then hill of lanterns", "day"]
HIT = dict(
    open=0.25,      # the opening hit: the first touch
    tape1=10.44,    # song 01: the first tape breaks
    birds=14.14,    # song 04: the rain has turned to birds
    swoop=18.20,    # song 04: the birds carry the thanks away, the camera dives after them
    hang=20.43,     # song 11: the leaping sea hangs
    snap=24.45,     # song 11, a bar start: time returns
    wave1=27.97,    # song 05: the first wave of lifted lights
    wave2=29.79,    # song 05: the wave overtakes the runner
    dive=31.62,     # song 05, a bar start: the camera dives into the crowd
    grip=37.42,     # song 06: the helper's hand grips his
    up=39.12,       # song 06: he is on his feet
    jump=42.51,     # song 07: the biggest jump of the mix. The flame is whole; the child runs
    tape9=45.64,    # song 07: the last tape breaks
    release=52.26,  # song 03, a bar start: the day leaves Heavenly Mother's hands
    peak=54.30,     # song 03: the loudest passage (to 55.0): the title is whole
    final=58.11,    # the last hit: the nine lights flare over the finished card
)
T0 = HIT["open"]                      # touch 0: the flame is given
T1, T2, T3, T4, T5 = S[1], S[2], S[3], S[4], S[5]   # hand-overs 1 to 4, and the fall
BREATH = S[6]                         # the hush
T6 = HIT["jump"]                      # the flame is whole again, in the child's hands
T7 = S[7]                             # the child gives it to Heavenly Mother's hands
LAUNCH = T0 + 0.90                    # the sprinter is at full speed
CHILD_RUNS = T6 + 0.39
CHILD_WALKS = T7 - 1.57
MOTHER_IN = T6 + 1.5                  # Heavenly Mother has gathered out of the lanterns' light on the brow

# =====================================================================================================
# THE ROAD. World of engine/p3d/api.py: metres, y up, the lake is y = 0, the arch stands over the origin
# in the plane z = 0. The road is the z axis; the carriers run toward -z. "Travel frame" of anything on
# the road: (r, u, a) = metres to the right of travel (+x), up (+y), ahead (-z).
# =====================================================================================================
MOTHER_Z = 31.0        # where Heavenly Mother stands, facing -z (azimuth 180), her back to the road
HILL_TOP = 6.0         # height of the brow above the lake
HILL_RUN = 20.0        # length of the climb
V = dict(sprinter=7.6, coat=6.2, shawl=6.4, elder_slow=0.9, elder=3.4, youth=8.4, child=5.2, child_walk=1.25)

# Positions worked backward from Heavenly Mother, so that the hands meet where the music says.
_z_child_end = MOTHER_Z + 0.5
_z_child_walk = _z_child_end + V["child_walk"] * (T7 - CHILD_WALKS)
Z_CIRCLE = _z_child_walk + V["child"] * (CHILD_WALKS - CHILD_RUNS)   # the child's place: the centre of the circle
Z_FALL = Z_CIRCLE + 1.9                                               # where the youth comes to rest
HILL_FOOT = Z_CIRCLE - 1.5
HILL_BROW = HILL_FOOT - HILL_RUN
_z_youth_t5 = Z_FALL + 0.7
_z_youth_t4 = _z_youth_t5 + V["youth"] * (T5 - T4)
_z_elder_t4 = _z_youth_t4 + 0.9
_z_elder_snap = _z_elder_t4 + V["elder"] * (T4 - HIT["snap"])
_z_elder_t3 = _z_elder_snap + V["elder_slow"] * (HIT["snap"] - T3)
_z_shawl_t2 = _z_elder_t3 + V["shawl"] * (T3 - T2)
_z_coat_t2 = _z_shawl_t2 + 0.8
_z_coat_t1 = _z_coat_t2 + V["coat"] * (T2 - T1)
_z_spr_t1 = _z_coat_t1 + 0.9
_z_spr_go = _z_spr_t1 + V["sprinter"] * (T1 - LAUNCH)
_z_spr_t0 = _z_spr_go + 4.8 * (LAUNCH - T0)
Z_START = _z_spr_t0 + 3.2 * T0


def road_y(z):
    """Height of the road above the lake at z: flat on the water, then the climb to the brow."""
    u = float(np.clip((HILL_FOOT - z) / HILL_RUN, 0.0, 1.0))
    return HILL_TOP * u * u * (3.0 - 2.0 * u)


def _company(place_z, behind, speed=None, lag=0.3):
    """Keys for running up the hill with the child: from a place in the circle to a halt at the brow."""
    speed = speed or V["child"]
    stop = HILL_BROW + 2.0 + behind
    t_go = CHILD_RUNS + lag
    return [(t_go, place_z), (t_go + (place_z - stop) / speed, stop)]


# =====================================================================================================
# THE CARRIERS. z: where the feet are along the road over time (piecewise, straight between keys).
# x: the lane. life: (appears, gone, how it gathers, how it leaves). look, garment, refs: for helper BODY.
# moves: the performance, (from, to, motion, note). Motions marked * are not in the brief (see NEEDS).
# =====================================================================================================
_ring = dict(sprinter=4.2, coat=2.8, shawl=0.4, elder=5.4, youth=1.9, helper=1.0)   # metres behind the child
CARRIERS = dict(
    sprinter=dict(
        who="a young woman, the first carrier", height=1.68, look="plexus", color="#ffcf7a", refs=(12, 3),
        garment="tunic and trousers of light, a head scarf that streams behind",
        z=[(0.0, Z_START), (T0, _z_spr_t0), (LAUNCH, _z_spr_go), (T1, _z_spr_t1), (T1 + 1.4, _z_spr_t1 - 6.6),
           (T1 + 2.8, _z_spr_t1 - 9.9), (T1 + 3.6, _z_spr_t1 - 10.4), (T5 + 1.49, _z_spr_t1 - 10.4),
           (T5 + 1.5, Z_CIRCLE + _ring["sprinter"] + 9.0), (T5 + 3.6, Z_CIRCLE + _ring["sprinter"])]
        + _company(Z_CIRCLE + _ring["sprinter"], _ring["sprinter"]),
        x=[(0.0, 0.0), (T1, 0.0), (T1 + 1.4, 0.9), (T5 + 1.49, 0.9), (T5 + 1.5, 1.4), (TOTAL, 1.4)],
        life=[(-1.0, T1 + 4.2, "in full stride at frame 0", "breaks upward into flakes (ref 5)"),
              (T5 + 1.4, TOTAL, "gathers out of dust behind the fall", "stays")],
        moves=[(0.0, T0, "run, reach up*", "her hand rises into the giving hand"),
               (T0, LAUNCH, "sprint start*", "the launch"), (LAUNCH, T1, "run", "flat out, shedding light (ref 15)"),
               (T1, T1 + 0.6, "reach a hand forward", "the pass, then her arm sweeps forward: after you"),
               (T1 + 0.6, T1 + 3.6, "walk", "slows, stops, looks after him"),
               (T5 + 1.5, T5 + 3.6, "run", "runs in to help"), (T5 + 3.6, BREATH, "kneel", "lifts an ember"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives her ember to the child (ref 14)"),
               (CHILD_RUNS, T7, "run", "with the company, to the brow"), (T7, TOTAL, "arms lifted*", "the day")]),
    coat=dict(
        who="a man in a long coat", height=1.80, look="glitter", color="#bcd4ff", refs=(15,),
        garment="a long coat of light, open, flying behind him",
        z=[(T1 - 3.24, _z_coat_t1 + 4.2), (T1 - 1.25, _z_coat_t1 + 4.2), (T1, _z_coat_t1), (T2, _z_coat_t2),
           (T2 + 1.3, _z_coat_t2 - 5.2), (T2 + 2.6, _z_coat_t2 - 7.6), (T2 + 3.2, _z_coat_t2 - 8.0),
           (T5 + 1.89, _z_coat_t2 - 8.0),
           (T5 + 1.9, Z_CIRCLE + _ring["coat"] + 8.0), (T5 + 3.8, Z_CIRCLE + _ring["coat"])]
        + _company(Z_CIRCLE + _ring["coat"], _ring["coat"]),
        x=[(0.0, 0.0), (T5 + 1.89, 0.0), (T5 + 1.9, -2.2), (TOTAL, -2.2)],
        life=[(T1 - 3.24, T2 + 5.6, "gathers out of drifting dust on the road ahead",
               "dissolves upward into flakes, which become the Gratitude (refs 5, 11, 13)"),
              (T5 + 1.8, TOTAL, "gathers out of dust behind the fall", "stays")],
        moves=[(T1 - 3.24, T1 - 1.25, "stand, look back, reach a hand back", "waits with an open hand"),
               (T1 - 1.25, T1, "run", "the run-up; the hands meet at speed"),
               (T1, HIT["tape1"], "run", "through the first tape"),
               (HIT["tape1"], T2, "run bent over the flame*", "the rain beats the flame flat; he shields it"),
               (T2, T2 + 3.2, "walk", "slows, stops, bows his head"),
               (T2 + 0.6, T2 + 5.6, "stand; dissolve upward", "he becomes his thanks"),
               (T5 + 1.9, T5 + 3.8, "run", "runs in"), (T5 + 3.8, BREATH, "kneel", "lifts an ember"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives it"),
               (CHILD_RUNS, T7, "run", "with the company"), (T7, TOTAL, "arms lifted*", "the day")]),
    shawl=dict(
        who="a woman with a shawl", height=1.64, look="dots", color="#9fe8dc", refs=(14, 16, 8),
        garment="a long dress and a wide shawl, a cloth of light she can open and wrap",
        z=[(T2 - 3.5, _z_shawl_t2 + 2.2), (T2 - 1.1, _z_shawl_t2 + 2.2), (T2, _z_shawl_t2), (T3, _z_elder_t3),
           (T3 + 3.6, _z_elder_t3 - V["elder_slow"] * 3.6), (T3 + 4.4, _z_elder_t3 - V["elder_slow"] * 3.6 - 0.4),
           (T5 + 2.19, _z_elder_t3 - V["elder_slow"] * 3.6 - 0.4),
           (T5 + 2.2, Z_CIRCLE + _ring["shawl"] + 7.0), (T5 + 4.2, Z_CIRCLE + _ring["shawl"])]
        + _company(Z_CIRCLE + _ring["shawl"], _ring["shawl"]),
        x=[(0.0, -0.1), (T2, -0.1), (T3, 0.35), (T3 + 4.4, 0.6), (T5 + 2.19, 0.6), (T5 + 2.2, -2.6),
           (TOTAL, -2.6)],
        life=[(T2 - 3.5, T4 + 1.5, "gathers at the edge of the rain",
               "disperses to one side on the sea wind (ref 16)"),
              (T5 + 2.1, TOTAL, "gathers out of dust behind the fall", "stays")],
        moves=[(T2 - 3.5, T2 - 1.1, "stand, shawl held open*", "a windbreak at the end of the rain"),
               (T2 - 1.1, T2, "run", "the run-up"), (T2, T2 + 0.5, "wrap a cloth round a hand*", "the caring pass"),
               (T2, T3, "run", "the shore; birds lift where she passes"),
               (T3, T3 + 3.6, "two carry one thing in step*", "four hands on the flame, at his pace"),
               (T3 + 3.6, T4, "stand and breathe", "lets go, watches him"),
               (T5 + 2.2, T5 + 4.2, "run", "runs in"), (T5 + 4.2, BREATH, "kneel", "lifts an ember"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives it"),
               (CHILD_RUNS, T7, "run", "with the company"), (T7, TOTAL, "arms lifted*", "the day")]),
    elder=dict(
        who="an old man", height=1.70, look="rim", color="#ffd9a0", refs=(1, 16),
        garment="a long coat and a scarf; a little stooped",
        z=[(T3 - 4.35, _z_elder_t3), (T3, _z_elder_t3), (HIT["snap"], _z_elder_snap), (T4, _z_elder_t4),
           (T4 + 0.9, _z_elder_t4 - 1.2), (T5 + 0.4, _z_elder_t4 - 1.2),
           (T5 + 0.5, Z_CIRCLE + _ring["elder"] + 6.0), (T5 + 6.0, Z_CIRCLE + _ring["elder"])]
        + _company(Z_CIRCLE + _ring["elder"], _ring["elder"], speed=V["elder"], lag=0.6),
        x=[(0.0, -0.35), (HIT["snap"], -0.35), (T4, 0.0), (T5 + 0.5, -1.2), (TOTAL, -1.2)],
        life=[(T3 - 4.35, T5 + 0.3, "gathers on the sea wall, waiting", "fades as the field goes dark"),
              (T5 + 0.5, TOTAL, "gathers out of dust behind the fall", "stays")],
        moves=[(T3 - 4.35, T3, "stand and breathe", "waits"),
               (T3, HIT["snap"], "two carry one thing in step*", "his pace; time at a quarter"),
               (HIT["snap"], T4, "walk, long strides", "alone on the wall, the flame held high"),
               (T4, T4 + 0.9, "reach a hand forward", "the pass"),
               (T4 + 0.9, T5, "lift a light overhead*", "he turns and is the first to root"),
               (T5 + 0.5, T5 + 6.0, "walk, long strides", "comes last, at his own pace"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives it"),
               (CHILD_RUNS, T7, "walk, long strides", "last"), (T7, TOTAL, "arms lifted*", "the day")]),
    youth=dict(
        who="a lanky boy, the fastest", height=1.76, look="plexus", color="#bfe0ff", refs=(3, 12),
        garment="a loose tunic and trousers",
        z=[(T4 - 4.29, _z_youth_t4 + 2.6), (T4 - 0.9, _z_youth_t4 + 2.6), (T4, _z_youth_t4), (T5, _z_youth_t5),
           (T5 + 0.5, Z_FALL), (CHILD_RUNS + 0.2, Z_FALL)] + _company(Z_FALL, _ring["youth"], lag=0.25)[1:],
        x=[(0.0, 0.0), (TOTAL, 0.0)],
        life=[(T4 - 4.29, TOTAL, "gathers at the end of the sea wall, bouncing on his toes", "stays")],
        moves=[(T4 - 4.29, T4 - 0.9, "stand", "restless"), (T4 - 0.9, T4, "run", "the run-up"),
               (T4, T5 - 1.2, "run", "8.4 m/s, the fastest in the film"), (T5 - 1.2, T5, "run", "the stride breaks"),
               (T5, T5 + 0.5, "stumble and fall on hands and knees*", "the flame leaves his hand"),
               (T5 + 0.5, HIT["grip"], "kneel", "head bowed"),
               (HIT["grip"] - 0.5, HIT["grip"], "two people reaching hands", "blue hand, gold hand, the flare (ref 4)"),
               (HIT["grip"], HIT["up"], "rise by a pulled hand*", "on his feet on the hit"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives his ember"),
               (CHILD_RUNS, T7, "run", "beside the child"), (T7, TOTAL, "arms lifted*", "the day")]),
    helper=dict(
        who="a young mother out of the crowd", height=1.66, look="glitter", color="#ffc9a8", refs=(9, 15, 4),
        garment="a long dress, hair covered",
        z=[(T5 - 4.86, Z_FALL + 5.5), (T5 + 1.6, Z_FALL + 5.5), (T5 + 3.2, Z_FALL - 0.9),
           (CHILD_RUNS + 0.2, Z_FALL - 0.9),
           (CHILD_RUNS + 0.2 + (Z_FALL - 0.9 - (HILL_BROW + 2.0 + _ring["helper"])) / V["child"],
            HILL_BROW + 2.0 + _ring["helper"])],
        x=[(0.0, 3.2), (T5 + 1.6, 3.2), (T5 + 2.6, 0.9), (T5 + 3.2, 0.0), (CHILD_RUNS, 0.0), (CHILD_RUNS + 1.0, 0.9),
           (TOTAL, 0.9)],
        life=[(T5 - 4.86, TOTAL, "one of the people of the field, holding a light", "stays")],
        moves=[(T5 - 4.86, T5, "lift a light overhead*", "rooting, the child at her side"),
               (T5 + 1.6, T5 + 3.2, "run", "the first to reach him; she runs round to face him"),
               (T5 + 3.2, HIT["grip"], "kneel, reach a hand forward", "open palm (ref 14): the words come from it"),
               (HIT["grip"], HIT["up"], "kneel to standing, pulling*", "lifts him"),
               (BREATH, T6, "kneel; raise an open palm and blow", "gives her ember"),
               (CHILD_RUNS, T7, "run", "behind her child"), (T7, TOTAL, "arms lifted*", "the day")]),
    child=dict(
        who="her daughter, the last carrier", height=1.15, look="glitter", color="#fff0c4", refs=(9, 15),
        garment="a dress; the brightest body in the film",
        z=[(T5 - 4.86, Z_FALL + 5.2), (T5 + 1.9, Z_FALL + 5.2), (T5 + 3.9, Z_CIRCLE), (CHILD_RUNS, Z_CIRCLE),
           (CHILD_WALKS, _z_child_walk), (T7, _z_child_end), (TOTAL, _z_child_end)],
        x=[(0.0, 3.8), (T5 + 1.9, 3.8), (T5 + 3.9, -0.7), (CHILD_RUNS, -0.7), (CHILD_WALKS, 0.55), (TOTAL, 0.55)],
        life=[(T5 - 4.86, TOTAL, "at her mother's side in the field", "stays")],
        moves=[(T5 - 4.86, T5, "stand", "holds her mother's hand"),
               (T5 + 1.9, T5 + 3.9, "run (a child's run)*", "runs in"),
               (T5 + 3.9, T6, "kneel, hands cupped*", "gathers the first embers; then holds out empty hands"),
               (T6, CHILD_RUNS, "stand up", "the flame is whole in her hands"),
               (CHILD_RUNS, CHILD_WALKS, "run (a child's run)*", "5.2 m/s, up the hill, through the last tape"),
               (CHILD_WALKS, T7, "walk", "the last steps, alone"),
               (T7 - 0.9, T7, "reach up with both hands*", "lifts the flame into the open hand"),
               (T7, TOTAL, "stand, look up", "at Heavenly Mother's side")]),
)
MOTHER = dict(
    who="Heavenly Mother: only from behind, veiled and robed; or as hands", height=1.72, look="glitter",
    color="#fff3d6", refs=(10, 13, 16), pos=(0.0, HILL_TOP, MOTHER_Z), facing=180.0,
    garment="a long robe and a long veil, the veil a stream of particles in the wind",
    life=[(MOTHER_IN, TOTAL, "gathers out of the light of the rising lanterns", "stays")],
    moves=[(-1.0, T0 + 0.6, "HANDS ONLY: an open hand gives the flame", "the first second"),
           (MOTHER_IN, T7 - 1.2, "open both arms low", "stands facing the dark horizon, her back to us"),
           (T7 - 1.2, T7, "lower one open hand to the side*", "her right hand comes down to meet the child's"),
           (T7, T7 + 0.7, "gather with both hands*", "the flame is in front of her; light spills round her"),
           (T7 + 0.7, HIT["release"], "raise both hands forward and up*", "rays fan round her head (ref 10)"),
           (HIT["release"], TOTAL, "open both arms wide*", "the day leaves her hands")])
CROWD = dict(
    lights=10000, bodies=60, look="rim", color_cold="#bcd0ff", color_lit="#ffd27a",
    z=(Z_FALL - 4.0, _z_youth_t4 + 6.0), depth=70.0, gap=2.4,
    wave=dict(lead=6.0, width=16.0, lift=0.55, note="a light goes up overhead and turns gold while the flame "
              "is within `width` metres along the road, peaking `lead` metres ahead of it"),
    goes_dark=T5, lifts_embers=(T5 + 2.6, BREATH), gives=(BREATH - 0.9, T6), runs=CHILD_RUNS)


# Everyone faces the way the road runs (-z), except: (who, from, to) faces back along it (+z)
FACES_BACK = [("helper", T5 + 3.2, CHILD_RUNS)]      # she kneels facing the fallen youth, profile to profile


def _interp(keys, t):
    return float(np.interp(t, [k[0] for k in keys], [k[1] for k in keys]))


def root(name, t):
    """Where a carrier's feet are at t (world metres). Heavenly Mother: name "mother"."""
    if name == "mother":
        return np.array(MOTHER["pos"], np.float64)
    c = CARRIERS[name]
    z = _interp(c["z"], t)
    return np.array([_interp(c["x"], t), road_y(z), z], np.float64)


def alive(name, t, fade=0.5):
    """0..1: how much of a carrier is there at t (1 inside a life, easing over `fade` seconds at its ends)."""
    lives = MOTHER["life"] if name == "mother" else CARRIERS[name]["life"]
    a = 0.0
    for t0, t1, _, _ in lives:
        a = max(a, min(np.clip((t - t0) / fade, 0, 1), np.clip((t1 - t) / fade, 0, 1) if t1 < TOTAL else 1.0))
    return float(a)


def hand(name, t):
    """PROVISIONAL place of the carrying hand: chest height, a forearm ahead. Phase B asks the body itself."""
    h = MOTHER["height"] if name == "mother" else CARRIERS[name]["height"]
    return root(name, t) + np.array([0.0, 0.78 * h, -0.38])


# who holds the flame, and when. Between holders it crosses over 0.12 s.
HOLDERS = [(-1.0, "sprinter"), (T1, "coat"), (T2, "shawl"), (T3 + 3.6, "elder"), (T4, "youth"), (T6, "child"),
           (T7, "mother")]
EMBERS_AT = np.array([-0.7, 0.05, Z_CIRCLE + 0.45])     # where the scattered flame comes to rest
FLAME_SIZE = Track([(0.0, 0.11), (T1, 0.14), (T2, 0.17), (T3, 0.21), (T4, 0.26), (T5 - 0.1, 0.30), (T5 + 0.4, 0.04),
                    (BREATH, 0.05), (T6 - 0.05, 0.08), (T6 + 0.25, 0.90), (T7, 1.00), (HIT["release"], 2.2),
                    (TOTAL, 2.2)], name="FLAME_SIZE")   # metres across: it grows with every hand


def flame(t):
    """Where the flame is at t (world metres)."""
    if T5 <= t < T6:                                   # fallen: it skitters to rest, then lies as embers
        u = float(np.clip((t - T5) / 0.9, 0.0, 1.0))
        p0 = hand("youth", T5)
        hop = np.array([0.0, 0.5 * abs(np.sin(u * np.pi * 3.0)) * (1.0 - u), 0.0])
        held = _ss(BREATH - 1.0, T6, t)                # the embers are gathered into the child's hands
        rest = EMBERS_AT * (1.0 - held) + (root("child", t) + [0.0, 0.50, -0.2]) * held
        return p0 * (1.0 - u) + rest * u + hop
    k = max(i for i, (t0, _) in enumerate(HOLDERS) if t >= t0)
    p = hand(HOLDERS[k][1], t)
    if T3 <= t < T3 + 3.6:                             # four hands: it is between the two of them
        p = 0.5 * (p + hand("elder", t))
    if k > 0 and t - HOLDERS[k][0] < 0.12 and HOLDERS[k][1] != "child":
        u = (t - HOLDERS[k][0]) / 0.12
        p = hand(HOLDERS[k - 1][1], t) * (1.0 - u) + p * u
    if HOLDERS[k][1] == "mother":                      # gathered, then raised forward and up
        got, lift = _ss(T7, T7 + 0.7, t), _ss(T7 + 0.7, HIT["release"], t)
        p = root("mother", t) + np.array([0.40 * (1.0 - got), 0.98 + 0.75 * lift, 0.15 - 0.30 * got - 0.40 * lift])
    return p


def _ss(a, b, x):
    u = float(np.clip((x - a) / (b - a), 0.0, 1.0))
    return u * u * (3.0 - 2.0 * u)


def rel(on, offset):
    """A point that travels with something: `on` is a carrier, "mother", "flame" or "world"; offset is
    (right, up, ahead) in metres in the travel frame (for "world": plain x, y, z). Returns a function of t."""
    o = np.asarray(offset, np.float64)
    if on == "world":
        return lambda t: o.copy()
    base = flame if on == "flame" else (lambda t: root(on, t))
    return lambda t: base(t) + np.array([o[0], o[1], -o[2]])


def fixed(on, offset, t_ref):
    """The same, frozen where it is at t_ref (a place in the world)."""
    p = rel(on, offset)(t_ref)
    return lambda t: p.copy()


# =====================================================================================================
# THE HAND-OVERS: each is a different human act, a word, a camera move and a change of world.
# =====================================================================================================
HANDOVERS = [
    dict(t=T0, give="the giving hands", take="sprinter", word="Greeting",
         act="an open hand of warm white light lowers the flame into a hand that reaches up",
         camera="macro on the two hands, then a whip back to her profile as she launches",
         world="night road: the first footfall strikes the first ring of gold"),
    dict(t=T1, give="sprinter", take="coat", word="Concession",
         act="a pass at full speed; then she sweeps her arm forward and lets him go: after you",
         camera="a loop over the top of the two hands at the flare, down behind the new carrier",
         world="rain of sparks, cut inside the loop"),
    dict(t=T2, give="coat", take="shawl", word="Gratitude",
         act="she wraps her shawl round the flame as she takes it; he bows his head",
         camera="close on the hands, then a fast tilt up with the sparks",
         world="the rain stops in the air and rises as birds: the shore"),
    dict(t=T3, give="shawl", take="elder", word="Respect",
         act="she does not let go: four hands, one flame, and they walk in step at his pace",
         camera="no whip: the picture snaps back to a low two shot and time drops to a quarter",
         world="the sea leaps on both sides and hangs"),
    dict(t=T4, give="elder", take="youth", word="Encouragement",
         act="the old man hands it on, turns, and is the first to lift a light for the boy",
         camera="a whip pan from the hands to straight down the road",
         world="the field wakes row on row to the horizon"),
    dict(t=T5, give="youth", take="the road", word="Apology",
         act="THE FALL: no hand is there; the flame hits the road and bursts into embers",
         camera="overshoots him, swings round and comes down onto the road at his side",
         world="every light in the field sinks and cools; only embers"),
    dict(t=HIT["grip"], give="helper", take="youth", word="Consideration",
         act="not the flame but a hand: she grips his, gold on blue, and pulls him up",
         camera="a slow push in on two kneeling profiles; the flare is in the middle of the frame",
         world="the dark fills with embers lifted in open hands"),
    dict(t=T6, give="everyone", take="child", word="Inclusiveness",
         act="every open palm gives up its ember; the streams meet in a child's cupped hands",
         camera="drifts in on the child; on the jump it whips in behind her as she stands and runs",
         world="lanterns lift off the ground on every side: the hill"),
    dict(t=T7, give="child", take="Heavenly Mother's hands", word=None,
         act="an open hand comes down to meet two small hands that lift the flame into it",
         camera="macro on the hands from her right side; then an arc to straight behind her",
         world="the day: first a band on the horizon, then (HIT release) a ring across everything"),
]

# =====================================================================================================
# THE WORLDS: one per section, and the hill of lanterns inside section 7. sky = (top, middle, horizon),
# display hex. Amounts are 0..1. These keys are this film's own words until helper CORE documents its own.
# The world is cut inside the whip at each hand-over (CUT seconds); the last change is a ring that grows
# from Heavenly Mother's hands (DAY_RING).
# =====================================================================================================
CUT = 0.35
FLAME_GOLD, FLAME_CORE = "#ffc24a", "#fff4dc"
WORLDS = [
    dict(name="night road", t=S[0], sky=("#02030f", "#070d2e", "#141c4a"), light="#8ea4ff",
         stars=1.0, milky=0.9, hills=0.5, mist=0.05, haze=0.08, mirror=1.0, rough=0.0,
         weather=None,
         extra="posts of light at the roadside every 6 m whip past; a ring of gold under each step"),
    dict(name="rain of sparks", t=S[1], sky=("#0b0820", "#1c1440", "#3a2a66"), light="#b8a8ff",
         stars=0.0, milky=0.0, hills=0.3, mist=0.15, haze=0.30, mirror=0.9, rough=0.1,
         weather=dict(kind="rain of sparks", color="#ffe9c0", amount=1.0, rings=True, slant=12.0,
                      stops=T2, birds=HIT["birds"]),
         extra="streaks fall 9 m/s; each lands as a ring on the mirror; the rain beats the flame flat"),
    dict(name="shore of birds", t=S[2], sky=("#0c1a3a", "#2a4470", "#8fa3c0"), light="#dfe6f5",
         stars=0.15, milky=0.0, hills=0.8, mist=0.35, haze=0.25, mirror=1.0, rough=0.0,
         weather=dict(kind="birds", color="#eef2ff", amount=1.0, from_rain=True),
         extra="wet sand: a perfect mirror; a band of pearl on the horizon; birds lift where she passes"),
    dict(name="sea wall", t=S[3], sky=("#031a22", "#0a3d48", "#1f6e72"), light="#9fe8dc",
         stars=0.0, milky=0.0, hills=0.4, mist=0.10, haze=0.35, mirror=0.25, rough=1.0,
         weather=dict(kind="spray", color="#e8fff8", amount=1.0, clock="quarter speed until HIT snap"),
         extra="two walls of spray stand up at the touch and hang; drops as big as lamps in the foreground"),
    dict(name="field of lights", t=S[4], sky=("#060a3a", "#10206e", "#2a3fa0"), light="#9fb4ff",
         stars=0.5, milky=0.2, hills=0.7, mist=0.20, haze=0.15, mirror=0.6, rough=0.0,
         weather=None, extra="the CROWD: lights wake in a front that runs away from us at 150 m/s"),
    dict(name="scattered flame", t=S[5], sky=("#06080f", "#10141f", "#232a3a"), light="#6c7a99",
         stars=0.2, milky=0.0, hills=0.3, mist=0.45, haze=0.30, mirror=0.7, rough=0.0,
         weather=dict(kind="embers", color="#ff9a4a", amount=1.0, count=1000),
         extra="the embers skitter out from the fall and die to red; then they are lifted, and gold again"),
    dict(name="still circle", t=S[6], sky=("#101624", "#232c40", "#465066"), light="#dfe8ff",
         stars=0.1, milky=0.0, hills=0.2, mist=0.70, haze=0.40, mirror=0.8, rough=0.0,
         weather=dict(kind="shaft from above", color="#dfe8ff", amount=0.8, at="the child"),
         extra="hush: nothing moves but the streams of embers and the mist"),
    dict(name="hill of lanterns", t=T6, sky=("#0a0830", "#241a5c", "#6a3a78"), light="#ffb070",
         stars=0.6, milky=0.3, hills=0.8, mist=0.25, haze=0.20, mirror=0.9, rough=0.0,
         weather=dict(kind="lanterns", color=("#ffb45a", "#ff8f6e"), amount=1.0, lift=T6),
         extra="lanterns lift off the ground on the jump; a seam of amber on the horizon ahead"),
    dict(name="day", t=S[7], sky=("#86c6f0", "#cfe8fa", "#fff4e4"), light="#fffaee",
         stars=0.0, milky=0.0, hills=1.0, mist=0.10, haze=0.10, mirror=1.0, rough=0.0,
         weather=dict(kind="leaves and soft bubbles", amount=0.4, burst=HIT["final"]),
         extra="engine/theme.py campaign day (day, then cream); the sun at azimuth 180, beyond the arch"),
]
DAY_RING = dict(centre="the flame in Heavenly Mother's hands", first_band=(T7 + 0.7, HIT["release"]),
                t0=HIT["release"], speed=(60.0, 900.0), t_full=HIT["peak"] - 0.3,
                note="inside the ring the campaign day, outside it the night; a rim of white gold on the front")
SUN = dict(azimuth=180.0, height=Track([(0.0, -12.0), (T7, -6.0), (HIT["release"], 1.0), (HIT["peak"], 9.0),
                                         (TOTAL, 11.0)], name="SUN height"))
EXPOSURE = Track([(0.0, 1.5), (T0 + 0.01, 2.0), (T0 + 0.35, 1.0), (T1 - 0.05, 1.0), (T1, 1.6), (T1 + 0.25, 1.0),
                  (T2 - 0.05, 1.0), (T2, 1.6), (T2 + 0.25, 1.0), (T3 - 0.05, 1.0), (T3, 1.5), (T3 + 0.3, 1.0),
                  (T4 - 0.05, 1.0), (T4, 1.7), (T4 + 0.25, 1.0), (T5 - 0.05, 1.0), (T5, 1.8), (T5 + 0.3, 0.9),
                  (HIT["grip"] - 0.05, 0.9), (HIT["grip"], 1.5), (HIT["grip"] + 0.3, 1.0), (T6 - 0.05, 1.0),
                  (T6, 1.9), (T6 + 0.4, 1.0), (T7 - 0.05, 1.0), (T7, 1.6), (T7 + 0.5, 1.1), (HIT["release"], 1.25),
                  (HIT["release"] + 0.15, 2.0), (HIT["peak"], 1.0), (HIT["final"] - 0.05, 1.0),
                  (HIT["final"], 1.25), (HIT["final"] + 0.6, 1.0), (TOTAL, 1.0)], name="EXPOSURE")
FADE = Track([(0.0, 1.0), (TOTAL, 1.0)], name="FADE")    # never black: not at the start, not at the end
# the far arch: which lights are lit (each word's spark arrives there after its reading moment)
ARCH = dict(radius=34.0, note="a guess until helper CORE gives the arch its size; lights 1 to 9, left to right")
ARCH_WAKES = dict(Greeting=T0 + 4.75, Concession=HIT["tape1"] + 0.76, Gratitude=HIT["swoop"] + 1.2,
                  Respect=HIT["snap"] + 0.75, Encouragement=HIT["dive"] + 1.38,
                  Apology=T6 + 0.4, Consideration=T6 + 0.55, Inclusiveness=T6 + 0.7, Compliment=HIT["tape9"] + 0.9)
ARCH_RUN = (HIT["tape9"] + 0.5, HIT["tape9"] + 1.7)      # all nine flare one after another


def arch_light(i):
    """PROVISIONAL place of light i (1..9) of the arch over the origin."""
    a = np.radians(160.0 - 140.0 * (i - 1) / 8.0)
    return np.array([ARCH["radius"] * np.cos(a), ARCH["radius"] * np.sin(a), 0.0])


# =====================================================================================================
# THE NINE EXPRESSIONS, as settings for engine/p3d/words.py (Word): exact campaign wording and labels
# (project-docs/DESIGN-SYSTEM.md section 5; line breaks and quotes as in engine/songs/epic_concert.py).
# facing: azimuth the words face (90: toward a camera on the right of the road; 0: back along the road).
# width: metres across the widest line. The four times: first particle, reading starts, reading ends, gone.
# =====================================================================================================
NINE = [
    ("Greeting", ["“How are you?”"]),
    ("Gratitude", ["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"]),
    ("Apology", ["“I’m sorry.", "It must have been hard on you.”"]),
    ("Inclusiveness", ["“It’s okay. I understand.”"]),
    ("Concession", ["“Please, after you.”"]),
    ("Respect", ["“I’d love to hear more", "about your thoughts.”"]),
    ("Encouragement", ["“I’ll pray (or root) for you.", "Everything will go well.”"]),
    ("Consideration", ["“Can I give you a hand", "with anything?”"]),
    ("Compliment", ["“You’re amazing.", "You’re doing great!”"]),
]
WORD_COLOR, WORD_GLOW = FLAME_CORE, FLAME_GOLD      # one family for all nine: the flame's own light
LABEL_SIZE = 0.42      # the label, in em of the phrase (at the engine's 0.30 it is under 0.6 mm on a phone here)
COLD_COLOR, COLD_GLOW = "#e6ecff", "#9fb4ff"        # the Apology: the flame is out

Z_TAPE1 = _interp(CARRIERS["coat"]["z"], HIT["tape1"])     # where the man breaks the first tape
Z_TAPE9 = _interp(CARRIERS["child"]["z"], HIT["tape9"])    # where the child breaks the last one
TAPE9_GAP = 9.0                                            # the last tape starts this far ahead of her


def _banner(t):
    """The last tape is carried: two of the company run ahead with it, and she gains on them."""
    z0 = _interp(CARRIERS["child"]["z"], T6 + 0.49) - TAPE9_GAP
    z = z0 + (Z_TAPE9 - z0) * float(np.clip((t - (T6 + 0.49)) / (HIT["tape9"] - (T6 + 0.49)), 0.0, 1.0))
    return np.array([0.0, road_y(z) + 2.7, z])


_coat_rest = T2 + 3.2      # the man has stopped
WORDS = [
    dict(expr="Greeting", pos=rel("sprinter", (-5.0, 3.25, 1.4)), width=4.6, facing=90.0,
         t_in=T0, t_read0=T0 + 0.95, t_read1=T0 + 3.50, t_out=T0 + 4.45, arrive="touch",
         source=fixed("flame", (0, 0, 0), T0),
         leave="wind", wind=(0.0, 0.12, 1.0),
         note="carried: it travels with her at 7.6 m/s, 5 m beyond her, above her head; leaves stretched back "
              "along the road into her wake"),
    dict(expr="Concession", pos=fixed("world", (0.0, 3.7, Z_TAPE1), 0.0), width=10.0, facing=0.0,
         t_in=T1, t_read0=T1 + 0.56, t_read1=HIT["tape1"] - 0.50, t_out=HIT["tape1"] + 0.5, arrive="touch",
         source=fixed("flame", (0, 0, 0), T1), leave="bokeh",
         tape=dict(y=1.25, half_width=5.5, breaks=HIT["tape1"], by="coat"),
         note="a finish tape of light across the road at chest height, the words above it; he breaks it on the "
              "hit and the letters rush past the lens"),
    dict(expr="Gratitude", pos=fixed("coat", (-8.0, 5.6, 6.6), _coat_rest), width=14.5, face="camera",
         t_in=T2 + 0.3, t_read0=HIT["birds"] + 0.16, t_read1=HIT["swoop"] - 0.30, t_out=HIT["swoop"] + 0.8,
         arrive="petals",
         source=rel("coat", (0.0, 1.5, 0.0)), leave="flock",
         note="source in phase B: the man's own body as it dissolves upward; his flakes turn and settle as the "
              "letters. The birds that were rain carry them away down the shore, and the camera follows"),
    dict(expr="Respect", pos=fixed("elder", (-8.0, 6.0, 0.6), T3 + 2.0), width=8.0, face="camera",
         t_in=T3 + 0.05, t_read0=HIT["hang"] + 0.17, t_read1=HIT["snap"] - 0.55, t_out=HIT["snap"] + 0.4,
         arrive="gather",
         source=fixed("elder", (-5.0, 3.5, 0.6), T3 + 2.0), leave="sink",
         note="source in phase B: the hanging spray (a point set). Read in quarter speed; falls as water when "
              "time returns on the bar"),
    dict(expr="Encouragement", pos=fixed("youth", (-88.0, 45.0, 240.0), T4 + 3.5), width=250.0, face="camera",
         t_in=T4, t_read0=HIT["wave1"] + 1.03, t_read1=HIT["dive"], t_out=HIT["dive"] + 1.08, arrive="touch",
         source=fixed("flame", (0, 0, 0), T4), leave="arch", to=arch_light(7),
         note="a comet from the touch climbs the sky and writes it 260 m away, as wide as the hills, over the "
              "wave of lifted lights"),
    dict(expr="Apology", pos=fixed("world", (-1.2, 1.95, Z_FALL - 0.3), 0.0), width=2.9, facing=90.0,
         t_in=T5 + 0.45, t_read0=T5 + 1.04, t_read1=HIT["grip"] - 0.47, t_out=HIT["grip"] + 0.28, arrive="lake",
         leave="sink",
         color=COLD_COLOR, glow=COLD_GLOW,
         note="rises out of the dark mirror he kneels on, cold white; sinks back as the hand reaches him"),
    dict(expr="Consideration", pos=fixed("world", (-0.9, 2.05, Z_FALL - 0.75), 0.0), width=2.0, facing=90.0,
         t_in=HIT["grip"] - 0.82, t_read0=HIT["grip"], t_read1=BREATH - 0.26, t_out=BREATH + 0.59, arrive="palm",
         source=fixed("helper", (0.0, 0.85, -0.45), HIT["grip"]), leave="give", to=EMBERS_AT + [0.0, 0.6, 0.0],
         note="poured from her open palm, whole on the hit as the hands grip. to in phase B: the open palms of "
              "the circle (it breaks into the embers they lift)"),
    dict(expr="Inclusiveness", pos=fixed("world", (-0.7, 1.62, Z_CIRCLE), 0.0), width=1.9, face="camera",
         t_in=BREATH - 1.01, t_read0=BREATH - 0.26, t_read1=T6, t_out=T6 + 0.6, arrive="gather", leave="give",
         to=fixed("child", (0.0, 0.55, 0.2), T6),
         note="the embers from every palm gather into it above the child; on the jump it pours into her hands "
              "and is the flame"),
    dict(expr="Compliment", pos=_banner, width=7.8, facing=0.0, tilt=6.0,
         t_in=T6, t_read0=T6 + 0.54, t_read1=HIT["tape9"], t_out=HIT["tape9"] + 0.7, arrive="touch",
         source=fixed("child", (0.0, 0.6, 0.2), T6), leave="bokeh",
         tape=dict(y=0.85, half_width=4.0, breaks=HIT["tape9"], by="child", held_by="two people of the field"),
         note="a tape carried ahead of her up the hill by two people of the field, who turn to cheer her; she "
              "gains on it and breaks it on the hit; its nine sparks climb to the arch"),
]


def word_specs():
    """The settings as engine/p3d/words.py takes them (direction notes and tapes left out)."""
    out = []
    for w in WORDS:
        s = {k: v for k, v in w.items() if k not in ("note", "tape")}
        s.setdefault("color", WORD_COLOR)
        s.setdefault("glow", WORD_GLOW)
        s.setdefault("sharp", 1.0)
        s.setdefault("label_size", LABEL_SIZE)
        out.append(s)
    return out


# =====================================================================================================
# THE CAMERA: keyframes in metres. on: what the key travels with (a carrier, "flame", "mother", "world").
# pos and look are (right, up, ahead) of that thing in its travel frame; for "world" they are plain
# (x, y, z). Between two keys both are followed and blended, so a tracking shot keeps tracking.
# fov: vertical, degrees. ap: lens opening in metres (0.05 is a strong blur). shutter: 0..1 of the frame
# time (1 is a full, smeared shutter for whips and speed; 0.5 the default). ease: how the key is reached.
# =====================================================================================================
def K(t, on, pos, look, fov, roll=0.0, ap=0.03, shutter=0.5, ease="smooth", note=""):
    return dict(t=t, on=on, pos=pos, look=look, fov=fov, roll=roll, ap=ap, shutter=shutter, ease=ease,
                note=note)


CAMERA = [
    # ---- night road
    K(0.0, "flame", (0.50, 0.10, 0.28), (0.0, 0.02, 0.0), 30, roll=-7, ap=0.06,
      note="frame 0: the flame between two hands, bright, big bokeh"),
    K(T0 + 0.30, "flame", (0.44, 0.06, 0.16), (0.0, 0.0, 0.0), 30, roll=-3, ap=0.06,
      note="the touch (0.25), the flare"),
    K(T0 + 0.95, "sprinter", (4.4, 0.9, 0.9), (-0.6, 1.9, 1.0), 38, ease="whip", shutter=1.0,
      note="whip back: she is in full stride, in profile, 4.4 m away, her feet striking light out of the road"),
    K(T0 + 2.15, "sprinter", (3.8, 1.0, 1.0), (-0.6, 1.9, 1.0), 38, note="at her speed; the Greeting above her"),
    K(T0 + 3.25, "sprinter", (2.3, 1.4, 1.0), (0.0, 1.75, 0.8), 34, ap=0.05,
      note="push in: head, shoulders, flame arm"),
    K(T0 + 4.25, "sprinter", (2.4, 1.5, 0.2), (0.0, 1.5, 1.4), 36, note="the words stream back into her wake"),
    K(T1 - 1.44, "sprinter", (0.9, 2.1, -4.2), (0.0, 1.3, 14.0), 46,
      note="behind her: the road, the man, one far light"),
    K(T1 - 0.39, "sprinter", (0.5, 1.7, -2.6), (0.0, 1.35, 6.0), 44, note="closing on the exchange"),
    # ---- rain of sparks
    K(T1 - 0.12, "flame", (0.25, 0.35, -1.1), (0.0, 0.0, 0.0), 36, ease="whip", shutter=1.0,
      note="in on the two hands"),
    K(T1 + 0.14, "flame", (0.15, 1.6, -0.6), (0.0, 0.0, 0.1), 42, roll=35, ease="whip", shutter=1.0,
      note="over the top of the hands at the flare; the road streaks below; the world is cut here"),
    K(T1 + 0.56, "coat", (-0.6, 2.4, -3.5), (0.0, 2.6, 12.0), 40, ease="whip",
      note="down behind him; the tape ahead"),
    K(HIT["tape1"] - 0.54, "coat", (-0.4, 2.6, -9.0), (0.0, 2.6, 6.0), 40, ease="linear",
      note="the camera lets him go ahead: a small runner, huge words"),
    K(HIT["tape1"], "coat", (-0.2, 1.8, -2.6), (0.0, 1.9, 8.0), 50, ease="whip", shutter=1.0,
      note="rush in as he breaks the tape: letters past the lens"),
    K(HIT["tape1"] + 0.40, "coat", (1.6, 1.5, -1.2), (0.0, 1.4, 0.8), 44, ease="linear",
      note="swinging out to his side"),
    K(HIT["tape1"] + 0.86, "coat", (2.6, 1.3, 0.8), (0.0, 1.35, 0.5), 36, ap=0.06,
      note="profile: he bends over the flame in the rain"),
    K(T2 - 0.90, "coat", (2.2, 1.3, -2.6), (0.0, 1.3, 5.0), 40,
      note="from behind his shoulder: ahead, at the edge of the rain, a woman with a shawl held open"),
    K(T2 - 0.15, "flame", (0.9, 0.15, -0.3), (0.0, 0.0, 0.0), 32, ap=0.06, note="in on the hands"),
    # ---- shore of birds
    K(T2 + 0.10, "flame", (0.8, 0.1, -0.15), (0.0, 0.05, 0.0), 32, ap=0.06,
      note="the shawl wraps the flame; the rain stops"),
    K(HIT["birds"], "coat", (3.4, 1.2, -2.4), (-2.0, 3.2, 3.5), 44, ease="whip", shutter=1.0,
      note="tilt up with the sparks: every drop is a bird"),
    K(HIT["birds"] + 2.06, "coat", (4.2, 1.5, -1.5), (-2.0, 3.0, 3.5), 44,
      note="rising round him as he becomes his thanks; the flame leaves along the shore at the right edge"),
    K(HIT["swoop"], "coat", (4.6, 1.9, -0.4), (-2.2, 3.0, 4.0), 44, ease="linear",
      note="the birds take the letters"),
    K(HIT["swoop"] + 1.00, "shawl", (1.6, 0.5, -1.2), (0.0, 1.3, 2.0), 54, ease="whip", shutter=1.0,
      note="dive after the birds, half a metre over the wet sand, to her side"),
    K(T3 - 0.20, "shawl", (1.5, 1.5, 0.5), (0.0, 1.5, 0.3), 30, ap=0.07, note="profile close-up (ref 16)"),
    # ---- sea wall
    K(T3, "flame", (0.7, 0.05, -0.1), (0.0, 0.0, 0.0), 30, ap=0.07,
      note="four hands, one flame; the bass; the sea leaps"),
    K(HIT["hang"], "elder", (4.2, 0.7, 0.6), (0.0, 1.65, 0.5), 44, ease="whip", ap=0.05,
      note="snap back to a low two shot, feet and all; time at a quarter; the spray hangs"),
    K(HIT["snap"] - 0.15, "elder", (4.1, 0.8, 0.9), (0.0, 1.75, 0.7), 44, ease="linear", ap=0.05,
      note="walking pace, in step"),
    K(HIT["snap"] + 0.65, "elder", (1.2, 3.4, -2.6), (0.0, 1.5, 4.0), 46, ease="whip", shutter=1.0,
      note="time returns (24.45), the sea falls; corkscrew up and behind him"),
    K(T4 - 0.69, "elder", (-1.0, 2.6, -4.5), (0.0, 1.6, 14.0), 50,
      note="over his shoulder: the boy at the end of the wall"),
    K(T4 - 0.17, "youth", (2.6, 1.2, -1.4), (0.0, 1.3, 0.2), 38, note="ahead of him to the exchange"),
    # ---- field of lights
    K(T4 + 0.07, "flame", (0.9, 0.1, -0.3), (0.0, 0.0, 0.1), 34, note="the touch"),
    K(T4 + 0.66, "youth", (1.6, 1.7, -2.2), (-3.0, 6.0, 40.0), 50, ease="whip", shutter=1.0,
      note="whip to look down the road: the field wakes to the horizon; the comet writes"),
    K(HIT["wave1"] + 1.03, "youth", (7.0, 6.0, -10.0), (-10.0, 3.0, 40.0), 48,
      note="crane up: the wave of lifted lights races him"),
    K(HIT["dive"] - 0.12, "youth", (6.0, 5.0, -10.0), (-8.0, 3.0, 40.0), 48, ease="linear",
      note="under words as wide as the sky"),
    K(HIT["dive"] + 0.68, "youth", (5.5, 1.1, 0.6), (0.0, 1.2, 1.2), 36, ease="whip", ap=0.06, shutter=1.0,
      note="down into the crowd: rims of gold pass as bokeh"),
    K(T5 - 0.16, "youth", (0.6, 0.5, -1.6), (0.0, 0.9, 5.0), 62, shutter=1.0,
      note="at his heels, lens wide; the stride breaks"),
    # ---- scattered flame
    K(T5 + 0.84, "youth", (2.7, 0.35, 0.9), (-0.1, 1.2, 0.2), 38, ease="whip", shutter=1.0,
      note="he falls (33.36); the camera overshoots, swings round, comes down onto the road"),
    K(T5 + 2.24, "youth", (2.9, 0.55, 0.0), (-0.2, 1.3, 0.25), 36, ap=0.07,
      note="a low arc round him; feet run past the lens"),
    K(HIT["grip"] - 0.52, "youth", (2.5, 0.8, 0.3), (-0.2, 1.35, 0.45), 34, ap=0.07,
      note="she kneels facing him; her open palm"),
    K(HIT["grip"], "youth", (2.3, 0.85, 0.4), (-0.2, 1.4, 0.45), 33, ap=0.07, note="the grip: gold on blue, the flare"),
    K(HIT["up"], "youth", (2.6, 1.1, 0.5), (-0.3, 1.6, 0.6), 34, ap=0.06,
      note="he is on his feet; embers lift all round"),
    # ---- still circle
    K(BREATH, "child", (3.6, 1.5, -1.0), (0.1, 1.45, -0.4), 36, ap=0.06, note="the hush: drift toward the child"),
    K(BREATH + 1.39, "child", (3.2, 1.3, -0.3), (0.0, 1.3, 0.0), 34, ap=0.07,
      note="every palm gives; the streams meet above her"),
    K(T6, "child", (2.6, 1.1, 0.2), (0.0, 1.35, 0.1), 34, ap=0.07, note="the jump: the words pour into her hands"),
    # ---- hill of lanterns
    K(T6 + 0.54, "child", (0.5, 0.8, -1.9), (0.0, 3.6, 10.0), 52, ease="whip", shutter=1.0,
      note="she stands and runs; whip in behind her, low; lanterns lift on every side"),
    K(T6 + 2.09, "child", (-0.4, 1.2, -3.0), (0.0, 3.8, 9.0), 50,
      note="the company runs with her; the tape ahead"),
    K(HIT["tape9"], "child", (0.3, 1.9, -5.5), (0.0, 3.4, 6.0), 50, ease="linear", note="she breaks it on the hit"),
    K(HIT["tape9"] + 0.56, "child", (0.2, 1.6, -2.4), (0.0, 2.2, 10.0), 52, ease="whip", shutter=1.0,
      note="through the burst"),
    K(HIT["tape9"] + 1.56, "child", (0.3, 1.5, -3.2), (0.0, 1.6, 12.0), 46,
      note="the nine lights wake; over her shoulder, on the brow, a veiled figure with her back to us"),
    K(T7 - 1.07, "mother", (1.4, 1.25, -1.0), (0.45, 0.98, -0.1), 30, ap=0.07,
      note="the last steps, at a walk; to the hands"),
    K(T7 - 0.07, "mother", (1.0, 1.05, -0.5), (0.45, 0.98, -0.15), 28, ap=0.08,
      note="two small hands lift the flame into one"),
    # ---- day
    K(T7 + 0.73, "mother", (0.25, 1.75, -2.4), (0.0, 1.55, 6.0), 40, ease="whip",
      note="an arc to straight behind her, half body; she gathers the light"),
    K(HIT["release"], "mother", (0.0, 1.9, -3.2), (0.0, 2.0, 8.0), 40,
      note="she raises it; rays round her head (ref 10)"),
    K(HIT["release"] + 0.74, "mother", (0.6, 3.2, -7.5), (0.0, 2.4, 10.0), 42, ease="whip", shutter=1.0,
      note="the ring of day throws the camera back over the lifted arms"),
    K(HIT["peak"], "world", (3.0, 16.0, 112.0), (0.0, 30.0, 0.0), 46, ease="whip",
      note="up and back along the whole road, gold from end to end; the title is whole"),
    K(TOTAL, "world", (8.0, 18.0, 128.0), (0.0, 33.0, 0.0), 46, ease="linear",
      note="the end card: a slow drift to the last frame, which is this bright picture"),
]


def _ease(u, how):
    if how == "linear":
        return u
    if how == "whip":
        return u * u * u * (u * (6.0 * u - 15.0) + 10.0)
    return u * u * (3.0 - 2.0 * u)


def camera_at(t):
    """The camera at t as plain numbers: pos, target (world metres), fov, roll, aperture, focus, shutter."""
    t = float(np.clip(t, CAMERA[0]["t"], CAMERA[-1]["t"]))
    i = max(k for k, c in enumerate(CAMERA) if c["t"] <= t)
    a = CAMERA[i]
    b = CAMERA[min(i + 1, len(CAMERA) - 1)]
    u = 0.0 if b is a else _ease((t - a["t"]) / (b["t"] - a["t"]), b["ease"])

    def mix(key):
        pa, pb = rel(a["on"], a[key])(t), rel(b["on"], b[key])(t)
        return pa * (1.0 - u) + pb * u

    pos, target = mix("pos"), mix("look")
    num = {k: a[k] * (1.0 - u) + b[k] * u for k in ("fov", "roll", "ap", "shutter")}
    return dict(pos=pos, target=target, fov=num["fov"], roll=num["roll"], aperture=num["ap"],
                focus=float(np.linalg.norm(target - pos)), shutter=num["shutter"])


def camera(t):
    """The camera for the 3D layer: a p3d CameraState when engine/p3d is there, plain numbers otherwise."""
    c = camera_at(t)
    try:
        from p3d.api import CameraState
    except ImportError:
        return c
    return CameraState(pos=c["pos"], target=c["target"], fov=c["fov"], roll=c["roll"], focus=c["focus"],
                       aperture=c["aperture"], aspect=ASPECT)


# =====================================================================================================
# THE END CARD: the existing style (as in engine/songs/epic_concert.py), not redesigned.
# =====================================================================================================
CORAL, NAVY, WHITE_GLOW = "#f0566a", "#1f2a6b", "#fff8ec"        # engine/theme.py
T_FORM = HIT["peak"] - 1.1                                       # the title's ribbon starts
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=CORAL, glow=WHITE_GLOW, anim="ribbon")
TAG_T0, TAG_T1 = HIT["peak"], HIT["peak"] + 0.9
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=NAVY, glow=WHITE_GLOW, anim="rise")
PHRASES = []          # the nine expressions are particle words in the world (WORDS), not 2D text
FRAGMENTS = []        # no lyrics, no extra line


# =====================================================================================================
# THE 3D LAYER
# =====================================================================================================
class _StandIn:
    """PHASE A ONLY: a carrier as the stand-in figure of engine/p3d/api.py, moved along the road, so that
    framing, focus and the words can be looked at before the real bodies exist."""

    def __init__(self, name):
        from p3d.api import StandIn
        c = MOTHER if name == "mother" else CARRIERS[name]
        self.name = name
        self.fig = StandIn(pos=(0.0, 0.0, 0.0), height=c["height"], n=12000, color=c["color"], facing=180.0,
                           look="rim" if c["look"] == "rim" else "glitter", seed=sum(map(ord, name)))

    def sample(self, t):
        b = self.fig.sample(t)
        b["pos"] = b["pos"] + root(self.name, t).astype(np.float32)
        return b

    def gain(self, t):
        return alive(self.name, t)


def build(scene):
    """Fills the 3D scene. PHASE A: stand-in figures and the nine words. PHASE B replaces the stand-ins with
    helper BODY's people and adds the flame, the road of shed light, the tapes, the weather of each world,
    the crowd and Heavenly Mother."""
    from p3d.words import Words
    for name in list(CARRIERS) + ["mother"]:
        scene.add(name, _StandIn(name))
    Words(word_specs()).add_to(scene)


P3D = dict(camera=camera, world=dict(states=WORLDS, cut=CUT, day_ring=DAY_RING, sun=SUN, arch=ARCH), setup=build)


# =====================================================================================================
# SELF CHECK: python engine/songs/ten_07_the_relay.py
# =====================================================================================================
def check(verbose=True):
    """Looks for mistakes in the direction itself. Returns the list of problems (empty when all is well)."""
    bad = []
    say = print if verbose else (lambda *a, **k: None)

    # 1. the nine expressions: each once, read for 2.5 s or more, all before the day
    if sorted(w["expr"] for w in WORDS) != sorted(label for label, _ in NINE):
        bad.append("the nine expressions are not each there exactly once")
    for w in WORDS:
        if not (w["t_in"] < w["t_read0"] < w["t_read1"] <= w["t_out"]):
            bad.append(f"{w['expr']}: its four times are out of order")
        if w["t_read1"] - w["t_read0"] < 2.5 - 1e-6:
            bad.append(f"{w['expr']}: read for only {w['t_read1'] - w['t_read0']:.2f} s")
        if w["t_out"] > T7:
            bad.append(f"{w['expr']}: still there when the day breaks")
        say(f"  {w['expr']:14s} arrives {w['t_in']:5.2f} ({w['arrive']:6s})  read {w['t_read0']:5.2f} to "
            f"{w['t_read1']:5.2f} ({w['t_read1'] - w['t_read0']:.2f} s)  gone {w['t_out']:5.2f} ({w['leave']})")

    # 2. the camera: keys in order, the whole film covered, always moving, always behind Heavenly Mother
    ts = [c["t"] for c in CAMERA]
    if any(b <= a for a, b in zip(ts, ts[1:])) or ts[0] > 0.0 or ts[-1] < TOTAL:
        bad.append("camera keys must be in order and cover 0 to 60 s")
    still = []
    for t in np.arange(0.0, TOTAL - 0.5, 0.25):
        if np.linalg.norm(camera_at(t + 0.5)["pos"] - camera_at(t)["pos"]) < 0.02:
            still.append(round(float(t), 2))
    if still:
        bad.append(f"the camera stands still at {still}")
    front = [round(float(t), 2) for t in np.arange(MOTHER_IN, TOTAL, 0.05) if camera_at(t)["pos"][2] < MOTHER_Z + 0.3]
    if front:
        bad.append(f"the camera is beside or in front of Heavenly Mother at {front[:6]}")

    # 2b. nobody is seen from the front: for every figure that is there, within 15 m and with its head in the
    #     picture, the camera is at least 55 degrees round from head-on (90 is a pure profile, 180 from behind)
    head_on = {}
    for t in np.arange(0.0, TOTAL, 0.05):
        c = camera_at(t)
        fwd = (c["target"] - c["pos"]) / np.linalg.norm(c["target"] - c["pos"])
        right = np.cross(fwd, [0.0, 1.0, 0.0])
        right /= max(np.linalg.norm(right), 1e-9)
        up = np.cross(right, fwd)
        k = 1.0 / np.tan(np.radians(c["fov"]) * 0.5)
        for name in list(CARRIERS) + ["mother"]:
            if alive(name, t) < 0.5:
                continue
            h = MOTHER["height"] if name == "mother" else CARRIERS[name]["height"]
            d = root(name, t) + [0.0, 0.93 * h, 0.0] - c["pos"]
            z = float(d @ fwd)
            if not 0.1 < z < 15.0 or abs(d @ right) * k / ASPECT > z or abs(d @ up) * k > z:
                continue
            turned = any(n == name and t0 <= t < t1 for n, t0, t1 in FACES_BACK)
            flat = np.array([-d[0], 0.0, -d[2]]) / max(np.hypot(d[0], d[2]), 1e-9)
            angle = float(np.degrees(np.arccos(np.clip(flat @ [0.0, 0.0, 1.0 if turned else -1.0], -1.0, 1.0))))
            if angle < 55.0:
                head_on.setdefault(name, round(float(t), 2))
    for name, t in head_on.items():
        bad.append(f"{name} is seen from the front at {t} s")

    # 3. the hands meet: giver and receiver within a metre and a half at every hand-over
    for t, g, r in [(T1, "sprinter", "coat"), (T2, "coat", "shawl"), (T3, "shawl", "elder"), (T4, "elder", "youth"),
                    (HIT["grip"], "helper", "youth"), (T7, "child", "mother")]:
        d = float(np.linalg.norm(root(g, t) - root(r, t)))
        if d > 1.5:
            bad.append(f"at {t:.2f} s {g} and {r} are {d:.2f} m apart: their hands cannot meet")
        if min(alive(g, t), alive(r, t)) < 1.0:
            bad.append(f"at {t:.2f} s {g} or {r} is not wholly there")
    for name, c in CARRIERS.items():
        for key in ("z", "x"):
            kt = [k[0] for k in c[key]]
            if any(b <= a for a, b in zip(kt, kt[1:])):
                bad.append(f"{name}: {key} keys out of order: {[round(x, 2) for x in kt]}")

    # 4. the end card: readable for 4 s or more, and never black
    if TOTAL - TAG_T1 < 4.0:
        bad.append(f"the end card is whole for only {TOTAL - TAG_T1:.2f} s")
    if min(FADE(0.0), FADE(TOTAL)) < 1.0:
        bad.append("the film must not start or end on black")

    # 5. no em dash or en dash anywhere in this file
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        src = f.read()
    if chr(0x2014) in src or chr(0x2013) in src:
        bad.append("an em dash or en dash is in this file")

    # 6. with engine/p3d/words.py at hand: the same wording as the engine's, and every word inside the picture,
    #    facing the camera and large enough for a phone during its reading moment
    try:
        import p3d.words as pw
    except ImportError:
        say("  (engine/p3d/words.py is not on this branch yet: the on-screen check of the words is skipped)")
    else:
        theirs = [(e["label"], e["lines"]) for e in pw.EXPRESSIONS]
        if theirs != NINE:
            bad.append("the wording here differs from engine/p3d/words.py")
        problems, _ = pw.check(pw.Words(word_specs()), camera, quiet=not verbose)
        bad += ["words: " + p for p in problems]
    return bad


if __name__ == "__main__":
    print(f"THE RELAY: road from z = {Z_START:.1f} m to Heavenly Mother at z = {MOTHER_Z:.1f} m; the fall at "
          f"{Z_FALL:.1f}, the circle at {Z_CIRCLE:.1f}, the hill from {HILL_FOOT:.1f} to {HILL_BROW:.1f} "
          f"(top {HILL_TOP:.0f} m); tapes at {Z_TAPE1:.1f} and {Z_TAPE9:.1f}")
    print("camera keys (world metres):")
    for c in CAMERA:
        s = camera_at(c["t"])
        print(f"  {c['t']:5.2f}  pos ({s['pos'][0]:7.2f} {s['pos'][1]:6.2f} {s['pos'][2]:7.2f})  target "
              f"({s['target'][0]:7.2f} {s['target'][1]:6.2f} {s['target'][2]:7.2f})  fov {c['fov']:2.0f}  "
              f"on {c['on']:8s}  {c['note']}")
    print("the nine expressions:")
    problems = check()
    print("\n".join("PROBLEM: " + p for p in problems) if problems else "no problems found")
