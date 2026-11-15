"""PETALS: film 05 of the ten concert promos for the Healing Concert "The Words of Mother's Love" (60 seconds).

PHASE A SKELETON. This file holds the treatment (this text) and the film's timeline as data, written against
the conventions of the new 3D layer (engine/p3d/api.py on branch engine-p3d: metres, y up, the lake at y = 0,
azimuth in degrees from +z toward +x, everything a pure function of song time). It does not render yet: the
3D layer, the particle people, the particle words and the new medley are still being built. Phase B turns the
data below into point sets and a camera, and renders in the cloud. Check the data with
`PYTHONPATH=engine python engine/songs/ten_05_petals.py` (no graphics needed).

LOGLINE
A kind word is a petal: you cannot keep it, you can only open your hand. The wind takes it, and wherever it
lands someone blossoms. We are one petal. Blown from an open palm in the first second, we ride nine words
round a flooded spring meadow, from person to person, home to the tree every petal came from.

THE IDEA, DEEPENED (five rules the whole film obeys)
1. The camera is a petal. It never cuts and never stands still on a tripod. Gusts land on the music's section
   starts and throw it (a tumble, a skim, a dive, a barrel roll, a climb); in a lull it hangs and rocks like a
   falling petal; for each reading moment it hovers, drifting slowly. Every move is the wind's.
2. A word makes someone bloom. A person nobody has spoken to yet is winter: a pale rim of cool dust, thin,
   barely there (the rim look, refs 01 and 16). When a word reaches them, petals and colour spread over them
   from the place it touched (a hand, a shoulder), and their garment becomes blossom (refs 07 and 15). Then
   they open a hand and pass it on.
3. Petals land as letters, and each word lands on a different ground: in the air between two people, on the
   water, in the crown of a tree, above a path, on the wind ahead of a runner, out of two clasped hands. They
   arrive with the wind, left to right, in reading order, so a word is read as it is written.
4. Every word goes home. When a word leaves, its petals fly to the great tree in the middle of the lake and
   one of its nine boughs buds in that word's colour. The tree is this film's arch of nine lights.
5. The wind is a wheel. It blows round the tree in one inward spiral, so the petals that leave the tree come
   home to it. At the end we see where they came from: Heavenly Mother, only from behind, at the foot of the
   tree, her veil fraying into petals on the wind. From above, the whole meadow is one flower.

THE WORLD
A water meadow in full spring daylight: the lake is a mirror a hand deep, with tufts of grass and small
flowers of light standing in it, so everything (people, petals, grass, sky) is doubled. In the middle (the
origin, where the arch stands in other films) a great bare tree, 16 m tall, on a low hummock. The route is one
turn of a spiral round it, from 60 m out to its foot (STATIONS, r_of). The sun stays low (16 to 22 degrees) at
azimuth 200, so as we travel round the tree the light itself turns: back light, side light, the deep blue sky
opposite the sun, side light, and gold back light again at the end. No night, no stars, no lanterns.

TIMELINE (seconds; the eight section starts are provisional, about 0, 7.5, 15, 22.5, 30, 37.5, 45, 52.5, until
the new medley's map exists; every time in the data hangs off SEC)

 1  0.0 to 7.5   THE FIRST WORD (Greeting). Back light, pearl blue and gold.
    0.00  Frame 0 is already a picture: a young woman of cream and coral petals in close profile (head,
          shoulders, an open palm raised before her), the low sun right behind her head, rays fanning round it,
          deep spring blue above. Petals are already leaving her palm and her scarf. 85 mm look, shallow focus.
    0.45  First downbeat: the gust. She breathes across her palm (ref 14) and her whole figure unwinds into a
          spiral of petals (ref 07). The camera is one of them: torn off sideways, tumbling (roll to 200
          degrees), the lens opening from 27 to 68 degrees.
    1.55  Righted, skimming 40 cm over the mirror at 17 m/s inside the stream, grass streaking under us, the
          bare tree far ahead on the left. A lone man stands on the water, back to the wind, head low, a pale
          outline of dust.
    2.20  The stream overtakes us, winds once round him and settles in the air before him as letters.
    2.6 to 5.6  READ "How are you?" (coral, 2.8 m wide). He lifts his head, turns his palm up and reaches
          into the first letters. The camera hovers, drifting right.
    5.6   The letters let go: half fall on him and he blooms from the hand, up the arm, across the chest
          (push in on the arm); the rest fly to the tree, where the first bough buds coral.
    6.9   He raises an open palm and breathes across it.

 2  7.5 to 15    THANKS WRITTEN ON WATER (Gratitude). Side light, gold on blue; the meadow turns green.
    7.5   Gust: a banked skim, the fastest low flight yet, his petals round us.
    9.0   Beside a running child (bloomed, gold and cream) at her own height. She runs to a woman kneeling at
          work in the shallows (pale, sleeves of dust), stops, and throws both arms up.
    9.7   Close: a burst of gold petals; one lands in the woman's opening hand (a flare: contact). The burst
          lifts the camera.
   10.6 to 14.2  READ, straight down from 9.5 m: the lake is a blue page and the gold petals write on it,
          floating: "Thank you. It's all thanks to you. You've worked hard." (11 m wide), the spiral of petals
          still feeding the last letters from the child's hands, the woman rising, blooming, drawing the
          child to her side. Each letter rocks on its own ripple. The camera keeps rising and turning slowly.

 3  15 to 22.5   THE ANSWER (Apology, then Inclusiveness). A veil of cloud: pearl. Then blush.
   15.0   Gust: the gold letters lift off the water in one sheet and we dive with them, spinning down like a
          falling petal, under the boughs of a small bare tree.
   15.9   Two friends stand four metres apart. One (dim) holds both open hands low, head bowed; the other
          (pale) has her back to him. Petals do not fly from his hands, they fall.
   16.5 to 19.2  READ "I'm sorry. It must have been hard on you." (apricot), hung low between them, shedding
          petals that ring the water. The camera circles slowly at chest height.
   19.2   She turns and walks THROUGH the words; they part round her like a curtain.
   19.5   Macro: their hands meet (ref 04), a flare, and on that touch the scattered petals turn in the air,
          flush pink and rise, the cloud leaves the sun, and the bare tree above them bursts into blossom.
   19.85 to 22.5  READ "It's okay. I understand." (pink) from below, in a clear opening of the new blossom,
          the two of them hand in hand under it, both in bloom, blossom raining. The camera is blown back
          and low by the burst, then drifts.

 4  22.5 to 30   THE NARROW WAY (Concession, then Respect). The blue sky opposite the sun: clear azure.
   22.5   Gust: up and out through the falling blossom, banking, down to a line of stepping stones that
          leads across the water to the great tree.
   23.0   Two people reach the first stone at the same moment. One steps back and sweeps an open arm toward
          the stones; white and sky blue petals follow the arm, run out along the stones, and rise.
   23.6 to 26.3  READ "Please, after you." (white petals edged sky blue on deep azure) above the path. The
          other walks under the words and away along the stones toward the tree, shedding light (ref 15),
          blooming as she goes. The camera pushes in between where they stood.
   26.3   It slips through the gap and veers to two people on a grassy hummock: an older woman speaking, a
          thin stream of petals leaving her (her thoughts), and a young man who kneels down facing her,
          leans in and catches every petal in cupped hands.
   27.0 to 29.8  READ "I'd love to hear more about your thoughts." (clay) between them. Listening is shown
          with the lens: the aperture opens through the shot until the whole world behind them has melted
          into soft discs and only these two are sharp. She blooms as she is heard.

 5  30 to 37.5   THE RUN (Encouragement). The gale; violet and white; long clouds racing.
   30.0   The hardest gust: flung up and outward, one full barrel roll, and down behind a runner (ref 12)
          who is tiring, pale, shedding dim dust.
   30.9   Five people at different depths line her way. As she passes, each raises an open palm and breathes
          across it (one stands with hands together, praying); their petals arc over her into a tunnel.
          She blooms and finds her stride.
   31.9 to 35.9  READ "I'll pray (or root) for you. Everything will go well." (violet, 9 m wide), carried on
          the wind ahead of her at her own speed, so the words stand steady in the frame while the world
          streaks past: the film's fastest shot, with its longest reading moment. Chase camera low behind her
          shoulder, creeping up beside her.
   36.5   She reaches the words and runs through them; they burst into violet blossom; she leaps and unwinds
          upward into petals (ref 07). We go through the burst.

 6  37.5 to 45   THE BREATH (Consideration, then Compliment). Warm haze, huge soft bokeh; then radiance.
   37.3   The wind drops (the music's breath falls in this section). We hang, rock, and sink like a falling
          petal toward an older man who has gone down on one knee by the water, and a young man who bends to
          him.
   38.2   Macro: an open palm, offered, fills the frame. We settle toward it.
   38.5   The other hand takes it (a flare).
   38.9 to 41.6  READ "Can I give you a hand with anything?" (rose), blooming out of the clasp above the two
          hands. The older man is drawn up to standing and blooms from the held hand.
   41.6   Standing, he opens his other palm and breathes across it: the rose letters go with the breath and
          we go with them.
   42.3 to 45.0  READ "You're amazing. You're doing great!" (lavender), opening like a blossom over the child
          from section 2, who jumps, both arms up, twirling in falling petals. Low hero angle into the light:
          the sun sits beside her raised hands, rays round her, the words above in the brightest frame so far.

 7  45 to 52.5   HOME. Gold back light; all nine colours.
   45.0   The great gust: every petal on the meadow rises into one flock, and we bank round the tree inside
          it at about 25 m/s. Everyone we met is walking to the tree, in bloom; we weave between their shoulders.
   46.7   Ahead, at the foot of the tree, the flock parts, and someone is standing there.
   47.6   SLOW. Close behind Heavenly Mother (from the hips up, veiled, only from behind). The sun is behind
          her head, rays fanning round it (refs 10 and 13); her veil streams to the right across the light
          and frays into petals: every petal we rode came from here.
   48.8   She opens both arms low. The child reaches her side and her near arm comes round the child.
   49.8   The flock pours past on both sides and winds up the trunk; the camera rises over her head (never
          turning back) and spirals up round the tree with it. The nine boughs are a spiral stair: as we pass
          each one it bursts from bud to full blossom in its own colour, coral, gold, apricot, pink, sky blue,
          clay, violet, rose, lavender: the nine words again, in order, in two and a half seconds.

 8  52.5 to 60   FULL BLOOM, and the concert. The campaign day: sky blue to cream.
   52.5   The biggest downbeat: we break out of the top of the crown and the tree lets go of everything at
          once. Thrown up by the blast, the camera turns over and looks straight down.
   53.4   From above: a dome of petals in nine colours opens outward over the water at 14 m/s, the spiral
          arms of the wind round it, everyone in a ring with arms lifted: the whole meadow is one flower.
          The blossom reaches the far hills and they flush.
   54.6   Pulling back and down, behind Heavenly Mother's side of the tree; the upper sky clears to cream.
          Petals from the blast rain into the title's letters.
   55.2 to 60.0  THE CONCERT (see THE ENDING).

THE NINE EXPRESSIONS (exact campaign wording and labels: EXPRESSIONS; where and when: WORDS)
 1 Greeting       arrives on the first breath, as a stream that winds round a stranger; read in the air in front
                  of him, 2.6 to 5.6; leaves by falling on him (he blooms) and flying to the tree.
 2 Gratitude      arrives as a spiral thrown up by a child, raining onto the lake; read floating on the water
                  from straight above, 10.6 to 14.2; leaves by lifting off the water in one sheet on the gust.
 3 Apology        arrives falling from two open hands; read low between two friends, 16.5 to 19.2; leaves when
                  the friend walks through it.
 4 Inclusiveness  IS the Apology answered: the same petals turn, flush pink and rise; read in the opening of a
                  tree that blossoms at that moment, 19.85 to 22.5; leaves upward with the falling blossom.
 5 Concession     arrives from the sweep of an arm, along the stepping stones; read above the path, 23.6 to
                  26.3; leaves by following the one who was let through, toward the tree.
 6 Respect        arrives from petals caught in a listener's cupped hands; read between two people while the
                  world behind them melts out of focus, 27.0 to 29.8; leaves on the gale.
 7 Encouragement  arrives from five open palms as a tunnel over a runner; read carried ahead of her at running
                  speed, 31.9 to 35.9; leaves when she runs through it and it bursts.
 8 Consideration  arrives out of two clasped hands; read above them, 38.9 to 41.6; leaves on a breath across an
                  open palm and BECOMES the next word.
 9 Compliment     arrives from that breath, opening like a blossom over a jumping child; read 42.3 to 45.0;
                  leaves on the great gust, first into the flock.
 All nine return as the nine boughs that bloom in order, 49.9 to 52.2 (colour only, no second reading).
 Letters on bright ground are painted in a deep blossom tone of the word's own colour with a light rim; letters
 on deep ground (the lake from above, the azure opposite the sun) are light. Nothing dark is put behind them.

THE PEOPLE (PEOPLE; lifelike bodies of points from helper BODY, all clothed in garments of light, no faces;
ordinary people in featureless profile, Heavenly Mother only from behind)
 the giver (a young woman, long dress, a scarf that streams), the stranger (a man in a long coat), the worker
 (a woman kneeling at work) and the child (who returns for the Compliment and is first to Heavenly Mother),
 two friends, the one who yields and the one who passes, the one who speaks and the one who listens, the
 runner and five who cheer and pray, the one who has gone down on a knee and the one who helps, and Heavenly
 Mother, veiled, from behind. Before a word reaches them: the rim look, cool and thin. After: glitter bodies
 whose garments are petals, hems fraying on the wind. Every person is seen in profile, from behind or from
 above; no shot looks at the front of a head. Motions and effects are named in PEOPLE; the ones the brief does
 not promise are marked NEW and listed in ENGINE_NEEDS.

PALETTE BY SECTION (PALETTES; display colours)
 1 pearl blue and pale gold, coral and cream petals      5 azure with a violet breath, violet and white
 2 clear blue and gold, the first fresh green            6 warm cream haze and rose; then radiance and lavender
 3 pearl grey blue and apricot; then blush pink, white   7 gold back light, all nine colours
 4 deep azure, white and sky blue; then clay and peach   8 the campaign day: sky blue to cream, coral and navy

THREE WOW MOMENTS
 A  10.6  THE LAKE IS A PAGE. Lifted on a burst of gold, we look straight down: thanks written in floating
          blossom, eleven metres wide, on deep blue water, two small people beside the words they made.
 B  19.5  THE ANSWER. Two hands meet; the falling Apology turns in the air, flushes pink and rises as its own
          answer, and the bare tree over them bursts into blossom round it.
 C  47.6 to 54.6  HOME. Behind Heavenly Mother, the sun through her veil; the spiral climb past nine boughs
          that burst into nine colours; the tree lets go; from above the meadow is one flower; its petals fall
          into the title.
 (Runner up: 31.9, the run, the words steady while the world streaks.)

THE ENDING
 The camera settles behind Heavenly Mother's side of the tree, far enough back that the tree in nine colours
 stands small in the lower third, mirrored in the lake, with the ring of people round it and the hills in
 blossom. Above it the sky is the campaign day (cream in the middle, sky blue at the top). Petals from the
 blast settle into the end card, in the existing end card style: "The Words of Mother's Love" (coral), the
 label "Healing Concert", then "Sunday, December 6 · 4:30 PM", "World Mission Society Church of God",
 "6720 W Sahara Ave, Las Vegas" (navy). Whole by 55.2, held to the last frame (4.8 s). No fade to black: the
 camera keeps drifting back, petals keep rising behind the text box, and on the music's last hit a gust shakes
 colour through the whole crown.

HOW IT STAYS DIFFERENT FROM THE OTHER NINE
 Full spring daylight from the first frame (no night, no stars, no dawn arc); the petal is the only particle
 that matters; the camera tumbles, banks and floats like one; words lie on water, hang in a tree, travel at
 running speed; people change from winter to bloom; the arch of nine lights is a tree of nine boughs.
"""
import os

import numpy as np

import theme   # engine/theme.py: the campaign colours (the engine loads song files with engine/ on the path)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root (this file is engine/songs/)
SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
AUDIO_FILE = "audio/promo/concert-medley.mp3"   # the NEW medley (branch epic-medley2), not on this branch yet

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
TOTAL = 60.0
SONG_END = 60.0
MUSIC_END = 59.6          # provisional
NFRAMES = int(round(TOTAL * FPS))

# ---------------------------------------------------------------------------------------------------------
# The medley. PROVISIONAL: the eight section starts the brief says to plan with. Phase B replaces SEC, BREATH,
# FINAL_HIT and BEATS with the measured map of the new medley; every time below hangs off them.
# ---------------------------------------------------------------------------------------------------------
SEC = [0.0, 7.5, 15.0, 22.5, 30.0, 37.5, 45.0, 52.5]
S1, S2, S3, S4, S5, S6, S7, S8 = SEC
BREATH = 40.0             # the short breath, about two thirds through (inside the Consideration)
FINAL_HIT = 57.6          # the last hit of the biggest passage
BEATS = []                # downbeats, when measured: gusts and contacts snap to the nearest one

# Key moments (seconds). Each snaps to the nearest downbeat once the medley's beats are measured.
LET_GO = S1 + 0.45        # the first downbeat: the giver lets go, the camera is torn off
THROW = S2 + 2.0          # the child throws both arms up
LANDS = S2 + 2.2          # a gold petal lands in the worker's opening hand
TOUCH = S3 + 4.5          # the friends' hands meet: the Apology becomes its answer, the tree blossoms
SWEEP = S4 + 0.5          # the yielder's arm sweeps toward the stepping stones
BURST = S5 + 6.5          # the runner runs through the words
CLASP = S6 + 1.0          # the offered hand is taken
BREATHE = S6 + 4.1        # a breath across a palm carries the rose letters on to the child
MOTHER_SEEN = S7 + 1.7    # the flock parts: Heavenly Mother is there (the camera is already behind her)
BEHIND_MOTHER = S7 + 2.6  # the camera settles close behind her
ARMS_OPEN = S7 + 3.6      # she opens both arms low
CLIMB = S7 + 5.2          # the spiral climb past the nine boughs begins
RELEASE = S8              # the biggest downbeat: the tree lets go
# The reading moments: (first, last) second in which each wording is whole, sharp and legible.
READ = dict(
    Greeting=(S1 + 2.6, S1 + 5.6), Gratitude=(S2 + 3.1, S2 + 6.7), Apology=(S3 + 1.5, S3 + 4.2),
    Inclusiveness=(TOUCH + 0.35, S3 + 7.5), Concession=(S4 + 1.1, S4 + 3.8), Respect=(S4 + 4.5, S4 + 7.3),
    Encouragement=(S5 + 1.9, S5 + 5.9), Consideration=(CLASP + 0.4, BREATHE), Compliment=(S6 + 4.8, S6 + 7.5),
)

# ---------------------------------------------------------------------------------------------------------
# Space. The same conventions as engine/p3d/api.py (phase B imports at and lin from p3d instead).
# ---------------------------------------------------------------------------------------------------------
SUN_AZ = 200.0            # the sun's azimuth, fixed; the route goes once round the tree, so the light turns


def at(az, dist, height=0.0):
    """The point at azimuth az (degrees from +z toward +x), dist metres from the y axis, height metres up."""
    a = np.radians(az)
    return np.array([np.sin(a) * dist, height, np.cos(a) * dist], dtype=np.float64)


# The route: one turn of an inward spiral round the great tree (the origin). The wind blows along it, toward
# growing azimuth. A camera that stands outside the route and looks at the tree sees the wind blow from left to
# right, which is why words are written in reading order.
SPIRAL = dict(az0=15.0, r0=60.0, k=0.15)      # radius = r0 - k * (az - az0) metres


def r_of(az):
    return SPIRAL["r0"] - SPIRAL["k"] * (az - SPIRAL["az0"])


def on_path(az, up=0.0, out=0.0):
    """A point on the route at azimuth az, `up` metres above the water, `out` metres further from the tree."""
    return at(az, r_of(az) + out, up)


# Where things happen: the azimuth of each station on the route (its radius comes from the spiral).
STATIONS = dict(
    A=15.0,     # the giver                                   r 60.0   back light
    B=37.0,     # the stranger: Greeting                      r 56.7   back light, the sun at the frame's left
    C=64.0,     # the worker and the child: Gratitude         r 52.7   side light
    D=95.0,     # two friends under a small bare tree         r 48.0   side light
    E=122.0,    # the stepping stones: Concession             r 44.0   the blue sky opposite the sun
    F=136.0,    # the two who talk: Respect                   r 41.9   the blue sky opposite the sun
    H=220.0,    # the one who knelt and the helper            r 29.3   front light, warm haze
    I=243.0,    # the child again: Compliment                 r 25.8   shot into the light
)
RUN = dict(az0=152.0, az1=207.0, t0=S5 + 0.4, t1=S5 + 7.0)   # the runner's way, about 34 m at 5.2 m/s
MOTHER_AZ, MOTHER_R = 20.0, 7.0               # Heavenly Mother stands here, facing the tree (toward the sun)


def rel(st, out=0.0, along=0.0, up=0.0):
    """A point near a station (a name in STATIONS, or an azimuth on the route): `out` metres further from the
    tree, `along` metres downwind (screen right for a camera outside the route that looks at the tree), `up`
    metres above the water."""
    az = STATIONS[st] if isinstance(st, str) else float(st)
    a = np.radians(az)
    radial = np.array([np.sin(a), 0.0, np.cos(a)])
    wind = np.array([np.cos(a), 0.0, -np.sin(a)])
    return radial * (r_of(az) + out) + wind * along + np.array([0.0, up, 0.0])


def run_az(t):
    u = min(max((t - RUN["t0"]) / (RUN["t1"] - RUN["t0"]), 0.0), 1.0)
    return RUN["az0"] + (RUN["az1"] - RUN["az0"]) * u


def run_point(t, ahead=0.0, out=0.0, up=0.0):
    """Where the runner is at t, moved `ahead` metres along her way, `out` metres from the tree, `up` metres."""
    return rel(run_az(t), out=out, along=ahead, up=up)


def facing(st, way):
    """The azimuth a person at a station faces: 'down' (downwind), 'up' (upwind), 'tree' or 'out'."""
    az = STATIONS[st] if isinstance(st, str) else float(st)
    return (az + dict(down=90.0, up=-90.0, tree=180.0, out=0.0)[way]) % 360.0


# ---------------------------------------------------------------------------------------------------------
# The nine Words of Mother's Love: exact campaign wording, labels and colours (project-docs/DESIGN-SYSTEM.md
# section 5; line breaks as in engine/songs/epic_concert.py). Never shortened. "(or root)" stays.
#   ink     the deep blossom tone the letters are painted in on a bright ground (None: the letters are light)
#   bough   which of the tree's nine boughs is this word's (0 the lowest, 8 the highest)
# ---------------------------------------------------------------------------------------------------------
EXPRESSIONS = [
    dict(label="Greeting", lines=["“How are you?”"], color="#FF977C", ink="#D9432F", bough=0),
    dict(label="Gratitude", lines=["“Thank you. It’s all thanks to you.", "You’ve worked hard.”"],
         color="#FFD05F", ink=None, bough=1),
    dict(label="Apology", lines=["“I’m sorry.", "It must have been hard on you.”"], color="#FFAD69",
         ink="#C2560E", bough=2),
    dict(label="Inclusiveness", lines=["“It’s okay. I understand.”"], color="#F582AF", ink="#C92C74", bough=3),
    dict(label="Concession", lines=["“Please, after you.”"], color="#82B0ED", ink=None, bough=4),
    dict(label="Respect", lines=["“I’d love to hear more", "about your thoughts.”"], color="#CE927E",
         ink="#A8553C", bough=5),
    dict(label="Encouragement", lines=["“I’ll pray (or root) for you.", "Everything will go well.”"],
         color="#B293E7", ink="#7248C8", bough=6),
    dict(label="Consideration", lines=["“Can I give you a hand", "with anything?”"], color="#EF7A96",
         ink="#C92A54", bough=7),
    dict(label="Compliment", lines=["“You’re amazing.", "You’re doing great!”"], color="#BE9CEB",
         ink="#7A43CC", bough=8),
]
GREETING, GRATITUDE, APOLOGY, INCLUSIVENESS, CONCESSION, RESPECT, ENCOURAGEMENT, CONSIDERATION, COMPLIMENT = range(9)

# ---------------------------------------------------------------------------------------------------------
# Palettes, one per look (display colours, as seen on screen). sky = top, middle, horizon, glow of the sun.
# winter = the dust of someone not yet spoken to; bloom = bodies and garments after; petals = the wind.
# ---------------------------------------------------------------------------------------------------------
CREAM, WHITE = theme.CREAM, "#ffffff"
PALETTES = dict(
    first_light=dict(sky=("#2f7fd8", "#9fcdf2", "#fff0d8", "#fff6e0"), sun=("#fff1cf", 1.00),
                     haze=("#fff2dc", 0.35), lake="#2a66c4", meadow=("#b7d9c2", "#dfeedd"),
                     petals=("#FF977C", theme.CORAL, CREAM), winter="#b9cdea", bloom=("#ff977c", "#ffd9b8", CREAM)),
    gold_on_blue=dict(sky=("#2a78d6", "#8ec6f2", "#ffe9bf", "#ffe7a6"), sun=("#ffe9b0", 1.05),
                      haze=("#ffeccc", 0.25), lake="#1c5fc0", meadow=("#8fd27a", "#d6ee9a"),
                      petals=("#FFD05F", "#ffe9a8", CREAM), winter="#b9cdea", bloom=("#ffd05f", "#ffe9b8", CREAM)),
    pearl=dict(sky=("#6f9fd6", "#c9d8ea", "#eef0f0", "#fff4ea"), sun=("#fff6ee", 0.60),
               haze=("#e6ebf2", 0.50), lake="#4f7fc0", meadow=("#9ccf8c", "#d2e6c0"),
               petals=("#FFAD69", "#f6c9a0", WHITE), winter="#b4c4de", bloom=("#ffad69", "#ffd9b8", CREAM)),
    blush=dict(sky=("#4f93e0", "#f4d3dc", "#ffe6d8", "#fff0dc"), sun=("#ffe8d0", 1.00),
               haze=("#ffe9e4", 0.35), lake="#3f78c8", meadow=("#7fd060", "#d6ee9a"),
               petals=("#F582AF", "#ffd0e0", WHITE), winter="#b4c4de", bloom=("#f582af", "#ffd6e4", WHITE)),
    azure=dict(sky=("#1f6ad2", "#6fb2ee", "#e6f3fb", "#f4fbff"), sun=("#fffbe8", 1.00),
               haze=("#e9f4fb", 0.15), lake="#1857b8", meadow=(theme.LEAF_GREEN, "#c8ea78"),
               petals=("#82B0ED", "#cfe4fb", WHITE), winter="#a9c2e8", bloom=("#82b0ed", "#dcecff", WHITE)),
    azure_clay=dict(sky=("#1f6ad2", "#6fb2ee", "#e6f3fb", "#f4fbff"), sun=("#fffbe8", 1.00),
                    haze=("#f4efe6", 0.20), lake="#1857b8", meadow=(theme.LEAF_GREEN, "#c8ea78"),
                    petals=("#CE927E", "#f2c9b4", CREAM), winter="#a9c2e8", bloom=("#ce927e", "#f6d6c4", CREAM)),
    gale=dict(sky=("#2b70d8", "#a9bff4", "#f1e6f6", "#fbf2ff"), sun=("#fff6f0", 1.00),
              haze=("#efe6f8", 0.20), lake="#2a5cc4", meadow=(theme.LEAF_GREEN, "#c8ea78"),
              petals=("#B293E7", "#dccbf8", WHITE), winter="#b0bce6", bloom=("#b293e7", "#e4d8fb", WHITE)),
    breath=dict(sky=("#79b2ea", "#ffdfd0", "#fff0df", "#fff6e6"), sun=("#ffe6c8", 0.90),
                haze=("#fff0e0", 0.60), lake="#5f95d8", meadow=("#8fd27a", "#e0f0a8"),
                petals=("#EF7A96", "#ffc4cf", CREAM), winter="#c2cde6", bloom=("#ef7a96", "#ffd2da", CREAM)),
    radiance=dict(sky=("#3d86e2", "#bcd9f6", "#fff2cf", "#fffbe6"), sun=("#fff0c0", 1.20),
                  haze=("#fff4dc", 0.30), lake="#3d7fd8", meadow=(theme.LEAF_GREEN, "#e0f0a8"),
                  petals=("#BE9CEB", "#e6d6fb", WHITE), winter="#c2cde6", bloom=("#be9ceb", "#eadffc", WHITE)),
    gold_home=dict(sky=("#4b8fe0", "#ffd7a2", "#ffe7b4", "#fff2c4"), sun=("#ffe2a0", 1.30),
                   haze=("#ffe9c0", 0.45), lake="#4a86d8", meadow=(theme.LEAF_GREEN, theme.LEAF_GOLD),
                   petals=tuple(e["color"] for e in EXPRESSIONS), winter="#d8d2c8",
                   bloom=(theme.GOLD, "#fff0cc", WHITE)),
    campaign_day=dict(sky=theme.PAL["day"], sun=("#fffaee", 0.80), haze=("#fff6ea", 0.25), lake=theme.SKY_BLUE,
                      meadow=(theme.LEAF_GREEN, theme.LEAF_GOLD), petals=tuple(e["color"] for e in EXPRESSIONS),
                      winter="#d8d2c8", bloom=(theme.GOLD, "#fff0cc", WHITE)),
    campaign_cream=dict(sky=theme.PAL["cream"], sun=("#ffffff", 0.70), haze=("#fffaf2", 0.30),
                        lake=theme.SKY_BLUE, meadow=(theme.LEAF_GREEN, theme.LEAF_GOLD),
                        petals=(theme.CORAL, theme.PEACH, CREAM), winter="#d8d2c8",
                        bloom=(theme.GOLD, "#fff0cc", WHITE)),
)
# which look when: each change starts on a gust or a contact and takes about a second
PALETTE_KEYS = [
    (0.0, "first_light"), (S2 - 0.3, "first_light"), (S2 + 1.2, "gold_on_blue"),
    (S3 - 0.2, "gold_on_blue"), (S3 + 0.9, "pearl"), (TOUCH - 0.1, "pearl"), (TOUCH + 0.7, "blush"),
    (S4 - 0.2, "blush"), (S4 + 0.9, "azure"), (S4 + 3.8, "azure"), (S4 + 4.6, "azure_clay"),
    (S5 - 0.2, "azure_clay"), (S5 + 0.9, "gale"), (S6 - 0.4, "gale"), (S6 + 0.7, "breath"),
    (S6 + 4.0, "breath"), (S6 + 4.9, "radiance"), (S7 - 0.1, "radiance"), (S7 + 1.5, "gold_home"),
    (S8 - 0.1, "gold_home"), (S8 + 1.0, "campaign_day"), (S8 + 2.9, "campaign_cream"), (TOTAL, "campaign_cream"),
]

# ---------------------------------------------------------------------------------------------------------
# The world (helper CORE's world, switched to full day). Key names follow the brief's nouns; phase B matches
# them to engine/UPGRADE-HOWTO.md section V when it exists.
# ---------------------------------------------------------------------------------------------------------
WORLD = dict(
    time="day",
    stars=0.0, milky=0.0, lanterns=0.0,              # no night in this film
    arch=0.0,                                        # the great tree stands where the arch stands
    sun=dict(az=SUN_AZ, height=[(0.0, 16.0), (S8, 22.0), (TOTAL, 28.0)]),    # degrees above the horizon
    sky=PALETTE_KEYS,                                # with PALETTES[name]["sky"], ["sun"], ["haze"]
    lake=dict(level=0.0, mirror=1.0, ripple=0.25, color=PALETTE_KEYS,   # deep and blue seen from straight above
              sun_glitter=0.6),
    hills=dict(ring=True, dist=900.0, height=120.0, haze=0.7,
               blossom=[(S8 + 0.8, 0.0), (S8 + 3.2, 1.0)]),   # the hills flush with blossom from the tree outward
    mist=[(0.0, 0.30), (S3 + 1.0, 0.45), (S4 + 1.0, 0.10), (S6 + 1.0, 0.50), (S7 + 1.0, 0.35), (TOTAL, 0.20)],
    shafts=[(0.0, 0.7), (S2 + 1.0, 0.25), (S4, 0.0), (S6 + 4.5, 0.6), (S7 + 2.0, 1.0), (S8 + 1.0, 0.5),
            (TOTAL, 0.25)],                          # rays from the sun: strongest in the back lit shots
    motes=[(0.0, 0.5), (TOTAL, 0.5)],                # pollen: fine gold dust in the whole volume
    clouds=[(0.0, 0.10), (S3 + 0.9, 0.55), (TOUCH + 0.7, 0.15), (S5 + 0.9, 0.35), (S6 + 0.7, 0.15), (TOTAL, 0.08)],
    cloud_speed=[(0.0, 1.0), (S5, 1.0), (S5 + 0.9, 4.0), (S6, 4.0), (S6 + 0.8, 0.6), (TOTAL, 0.8)],
)

# Point sets this film builds itself in phase B (PointSet protocol), unless CORE offers them:
GREAT_TREE = dict(
    pos=(0.0, 0.0, 0.0), height=16.0, crown_radius=9.5, hummock=(11.0, 0.5),   # radius and height of its mound
    trunk_color="#e9dcc8", bare_color="#cfd8e6",
    # nine boughs, a spiral stair round the trunk: the camera's last climb passes them in campaign order.
    #   bud    a soft light of the word's colour wakes in the bare bough when the word comes home
    #   bloom  the bough bursts into full blossom as the flock and the camera pass it
    boughs=[dict(i=i, label=e["label"], color=e["color"], az=28.0 + 21.5 * i, height=5.6 + 1.25 * i,
                 length=8.5 - 0.35 * i, bud=None, bloom=CLIMB - 0.3 + 0.29 * i) for i, e in enumerate(EXPRESSIONS)],
)
SMALL_TREES = [
    dict(id="tree_d", pos=rel("D", out=-2.6, along=0.2), height=6.5, crown_radius=3.6,
         bare_until=TOUCH, blossom=("#ffffff", "#ffd0e0", "#F582AF"),
         keep_clear=dict(center=rel("D", up=3.05), size=(4.4, 1.3))),   # the opening the pink words stand in
]
STONES = dict(start=rel("E", out=-0.6), toward="tree", count=14, pitch=0.8, size=0.55, color="#f4fbff")
MEADOW = dict(r_in=9.0, r_out=85.0, tufts=2600, tuft_height=(0.18, 0.55), flowers=900,
              # the meadow greens and flowers as the words pass: the bloom front follows the route
              bloom_front=[(0.0, 15.0), (S2, 37.0), (S3, 64.0), (S4, 95.0), (S5, 136.0), (S6, 207.0),
                           (S7, 243.0), (S8, 375.0)],   # azimuth reached on the route at each time
              clear_path=1.2)                           # metres of open water along the route's centre line

# ---------------------------------------------------------------------------------------------------------
# The camera: one petal's flight. Positions and targets in metres, fov the vertical field of view in degrees,
# roll in degrees and CUMULATIVE (360 is one full barrel roll; positive tilts the horizon clockwise, which is
# also the way the petal banks, because the tree is always on its left). focus is the sharp distance in
# metres or the name of what it follows; aperture is the lens opening in metres (0.05 is a strong blur close
# up; the far tree needs 0.12 or more to melt). move names the kind of motion between this key and the next.
# ---------------------------------------------------------------------------------------------------------
def K(t, pos, target, fov, roll=0.0, focus=None, aperture=0.02, move="fly", note=""):
    return dict(t=round(float(t), 3), pos=np.round(np.asarray(pos, float), 3),
                target=np.round(np.asarray(target, float), 3), fov=float(fov), roll=float(roll), focus=focus,
                aperture=float(aperture), move=move, note=note)


_M = at(MOTHER_AZ, MOTHER_R)                 # Heavenly Mother's feet
_I = rel("I")                                # the child, for the Compliment
_T_ENC = READ["Encouragement"]

CAMERA_KEYS = [
    # ---- 1 the first word
    K(S1 + 0.00, rel("A", out=1.70, along=-0.25, up=1.40), rel("A", along=0.10, up=1.55), 26, roll=-4,
      focus="giver", aperture=0.05, move="hover",
      note="frame 0: close profile, palm raised, petals leaving, the sun behind her head"),
    K(LET_GO, rel("A", out=1.60, along=0.15, up=1.43), rel("A", along=0.40, up=1.50), 27, roll=0,
      focus="giver", aperture=0.05, move="tumble", note="first downbeat: the gust; she unwinds into petals"),
    K(S1 + 1.00, rel("A", out=0.80, along=5.0, up=0.90), on_path(35.0, up=1.0), 58, roll=200, focus=14.0,
      aperture=0.01, move="fly", note="torn off sideways, tumbling inside the stream"),
    K(S1 + 1.55, on_path(28.5, up=0.40, out=0.3), rel("B", along=-1.1, up=1.2), 68, roll=360, focus=9.0,
      aperture=0.01, move="fly", note="righted: skimming 40 cm over the mirror; the stranger ahead"),
    K(S1 + 2.20, rel("B", out=3.6, along=-3.2, up=1.00), rel("B", along=-0.2, up=1.35), 46, roll=360,
      focus="stranger", aperture=0.03, move="hover", note="the stream overtakes us and winds round him"),
    K(READ["Greeting"][0], rel("B", out=4.7, along=-1.0, up=1.30), rel("B", along=0.45, up=1.45), 32, roll=360,
      focus="word:Greeting", aperture=0.14, move="hover", note="READ Greeting: he at the left, the tree behind him"),
    K(READ["Greeting"][1], rel("B", out=4.4, along=-0.4, up=1.36), rel("B", along=0.55, up=1.45), 32, roll=360,
      focus="word:Greeting", aperture=0.14, move="fly", note="end of the reading moment"),
    K(S1 + 6.50, rel("B", out=2.4, along=-0.6, up=1.30), rel("B", along=-0.55, up=1.25), 30, roll=360,
      focus="stranger", aperture=0.07, move="hover", note="he blooms: colour runs from the hand up the arm"),
    K(S1 + 7.40, rel("B", out=1.5, along=-1.5, up=1.50), rel("B", along=-0.4, up=1.45), 34, roll=360,
      focus="stranger", aperture=0.06, move="fly", note="his open palm rises; he breathes across it"),
    # ---- 2 thanks written on water
    K(S2 + 0.00, rel("B", out=1.3, along=-1.2, up=1.45), on_path(52.0, up=0.6), 44, roll=360, focus=12.0,
      aperture=0.01, move="fly", note="gust: blown off his palm"),
    K(S2 + 0.75, on_path(51.0, up=0.35, out=0.4), on_path(62.0, up=0.8), 72, roll=382, focus=10.0,
      aperture=0.01, move="fly", note="a banked skim, grass streaking under the lens"),
    K(S2 + 1.50, rel("C", out=2.4, along=-4.6, up=0.85), rel("C", along=-2.0, up=0.85), 48, roll=360,
      focus="child", aperture=0.04, move="fly", note="beside the running child, at her height"),
    K(LANDS, rel("C", out=2.3, along=-1.4, up=1.25), rel("C", along=-0.5, up=0.95), 36, roll=360,
      focus="worker", aperture=0.06, move="crane",
      note="the throw; a gold petal lands in the worker's opening hand: flare"),
    K(READ["Gratitude"][0], rel("C", out=-2.2, along=1.0, up=9.5), rel("C", out=-4.4, along=1.0, up=0.0), 56,
      roll=360,
      focus="word:Gratitude", aperture=0.0, move="hover",
      note="READ Gratitude: lifted on the burst, straight down on the lake (WOW A)"),
    K(READ["Gratitude"][1], rel("C", out=-1.7, along=2.4, up=10.8), rel("C", out=-4.2, along=1.8, up=0.0), 56,
      roll=366,
      focus="word:Gratitude", aperture=0.0, move="fly", note="still rising, turning slowly"),
    # ---- 3 the answer
    K(S3 + 0.00, rel("C", out=-1.2, along=4.0, up=9.0), on_path(80.0, up=1.5), 60, roll=372, focus=14.0,
      aperture=0.01, move="fly", note="gust: the gold letters lift off the water; we dive with them"),
    K(S3 + 0.90, rel("D", out=5.5, along=-6.0, up=1.60), rel("D", along=-1.0, up=1.3), 52, roll=360,
      focus="friend_a", aperture=0.03, move="fly", note="spinning down under the bare boughs"),
    K(READ["Apology"][0], rel("D", out=5.0, along=-0.9, up=1.25), rel("D", along=0.0, up=1.28), 36, roll=360,
      focus="word:Apology", aperture=0.10, move="orbit", note="READ Apology: low between the two friends"),
    K(READ["Apology"][1], rel("D", out=4.3, along=-0.2, up=1.30), rel("D", along=0.0, up=1.25), 36, roll=360,
      focus="word:Apology", aperture=0.10, move="fly", note="she turns and walks through the words"),
    K(TOUCH, rel("D", out=2.2, along=-0.1, up=1.15), rel("D", along=0.0, up=1.10), 30, roll=360,
      focus="hands:friends", aperture=0.08, move="fly", note="macro: their hands meet, a flare (WOW B)"),
    K(READ["Inclusiveness"][0], rel("D", out=6.0, along=-0.8, up=0.85), rel("D", along=0.0, up=2.45), 34, roll=360,
      focus="word:Inclusiveness", aperture=0.06, move="hover",
      note="READ Inclusiveness: blown back and low; the tree bursts into blossom round the words"),
    K(READ["Inclusiveness"][1], rel("D", out=5.2, along=0.9, up=1.20), rel("D", along=0.1, up=2.50), 34, roll=360,
      focus="word:Inclusiveness", aperture=0.06, move="fly", note="blossom raining"),
    # ---- 4 the narrow way
    K(S4 + 0.50, on_path(109.0, up=2.6, out=1.5), rel("E", up=1.6), 56, roll=380, focus=10.0, aperture=0.01,
      move="fly", note="gust: out through the falling blossom, banking"),
    K(READ["Concession"][0], rel("E", out=5.2, along=-0.6, up=0.95), rel("E", along=0.0, up=1.95), 38, roll=360,
      focus="word:Concession", aperture=0.05, move="hover",
      note="READ Concession: the stones lead away to the tree; white words on deep azure"),
    K(READ["Concession"][1], rel("E", out=4.2, along=-0.1, up=1.05), rel("E", along=0.0, up=2.00), 38, roll=360,
      focus="word:Concession", aperture=0.05, move="fly", note="pushing in between where they stood"),
    K(S4 + 4.15, rel("E", out=0.5, along=3.5, up=1.30), rel("F", along=-0.4, up=1.2), 50, roll=366,
      focus=6.0, aperture=0.02, move="fly", note="through the gap, veering downwind"),
    K(READ["Respect"][0], rel("F", out=4.0, along=-0.9, up=1.05), rel("F", along=0.0, up=1.40), 40, roll=360,
      focus="word:Respect", aperture=0.03, move="hover", note="READ Respect: the two who talk"),
    K(READ["Respect"][1], rel("F", out=3.4, along=-0.3, up=1.10), rel("F", along=0.0, up=1.40), 40, roll=360,
      focus="word:Respect", aperture=0.16, move="fly",
      note="the aperture has opened through the shot: only these two are sharp"),
    # ---- 5 the run
    K(S5 + 0.00, rel("F", out=2.0, along=1.5, up=1.40), on_path(148.0, up=1.2), 55, roll=360, focus=10.0,
      aperture=0.01, move="fly", note="the gale"),
    K(S5 + 0.45, on_path(146.0, up=3.0, out=5.0), run_point(S5 + 0.45, ahead=4.0, up=1.2), 62, roll=540,
      focus=10.0, aperture=0.01, move="fly", note="flung up and outward, half way through a barrel roll"),
    K(S5 + 0.90, run_point(S5 + 0.90, ahead=-4.5, out=1.2, up=1.10), run_point(S5 + 0.90, ahead=9.0, up=3.4), 60,
      roll=720, focus="runner", aperture=0.02, move="chase", note="down behind the runner"),
    K(_T_ENC[0], run_point(_T_ENC[0], ahead=-3.4, out=1.0, up=1.00), run_point(_T_ENC[0], ahead=10.5, up=3.8),
      33, roll=720, focus="word:Encouragement", aperture=0.03, move="chase",
      note="READ Encouragement: the words fly ahead of her at her speed, steady in frame"),
    K(_T_ENC[1], run_point(_T_ENC[1], ahead=-2.8, out=1.0, up=1.10), run_point(_T_ENC[1], ahead=10.5, up=3.9),
      33, roll=720, focus="word:Encouragement", aperture=0.03, move="chase", note="creeping up beside her"),
    K(S5 + 6.80, run_point(S5 + 6.80, ahead=1.0, out=0.3, up=2.0), run_point(S5 + 6.80, ahead=9.0, up=6.0), 60,
      roll=720, focus=3.0, aperture=0.05, move="float",
      note="through the violet burst (she ran through the words at BURST)"),
    # ---- 6 the breath
    K(S6 - 0.20, on_path(211.0, up=3.0, out=1.2), rel("H", along=0.0, up=0.9), 46, roll=730, focus="helper",
      aperture=0.04, move="float", note="the wind drops: hanging, rocking, sinking like a falling petal"),
    K(S6 + 0.70, rel("H", out=0.75, along=-0.55, up=1.00), rel("H", along=-0.2, up=0.86), 30, roll=713,
      focus="hands:help", aperture=0.06, move="float", note="macro: an offered open palm fills the frame"),
    K(CLASP, rel("H", out=0.62, along=-0.35, up=0.93), rel("H", along=-0.1, up=0.86), 30, roll=720,
      focus="hands:help", aperture=0.06, move="fly", note="the other hand takes it: flare"),
    K(READ["Consideration"][0], rel("H", out=3.3, along=-0.7, up=1.05), rel("H", along=0.0, up=1.50), 40, roll=720,
      focus="word:Consideration", aperture=0.12, move="float",
      note="READ Consideration: the words bloom out of the clasp (the music's breath)"),
    K(READ["Consideration"][1], rel("H", out=3.5, along=-0.2, up=1.25), rel("H", along=0.0, up=1.55), 40, roll=720,
      focus="word:Consideration", aperture=0.12, move="fly", note="he is drawn up; he breathes across his palm"),
    K(READ["Compliment"][0], _I + at(34.0, 3.6, 0.45), _I + at(0, 0, 2.00), 38, roll=720, focus="word:Compliment",
      aperture=0.04, move="hover",
      note="READ Compliment: low, into the light; the sun beside the child's raised hands"),
    K(READ["Compliment"][1], _I + at(42.0, 3.2, 0.70), _I + at(0, 0, 2.05), 38, roll=720, focus="word:Compliment",
      aperture=0.04, move="fly", note="end of the reading moment; the great gust takes the words"),
    # ---- 7 home
    K(S7 + 0.65, at(290.0, 21.5, 2.2), at(330.0, 15.0, 1.6), 62, roll=742, focus=8.0, aperture=0.02,
      move="fly", note="banking round the tree inside the flock"),
    K(S7 + 1.30, at(335.0, 16.5, 1.5), at(8.0, 10.0, 1.6), 56, roll=738, focus=4.0, aperture=0.04, move="fly",
      note="weaving between the walkers' shoulders"),
    K(BEHIND_MOTHER, at(22.0, 10.6, 0.90), _M + at(0, 0, 1.72), 32, roll=720, focus="mother", aperture=0.05,
      move="orbit", note="SLOW: close behind Heavenly Mother, the sun behind her head (WOW C begins)"),
    K(ARMS_OPEN + 0.2, at(25.0, 10.2, 1.30), at(MOTHER_AZ, 6.5, 2.4), 34, roll=720, focus="mother", aperture=0.05,
      move="crane", note="she opens her arms low; the child reaches her side"),
    K(CLIMB, at(27.0, 9.6, 3.6), (0.0, 8.5, 0.0), 44, roll=722, focus=9.0, aperture=0.03, move="orbit",
      note="rising over her head, never turning back; the flock winds up the trunk"),
    K(CLIMB + 0.8, at(80.0, 8.2, 7.5), (0.0, 11.0, 0.0), 50, roll=728, focus=7.0, aperture=0.04, move="orbit",
      note="spiralling up round the tree: boughs burst into blossom as we pass"),
    K(CLIMB + 1.6, at(140.0, 6.5, 12.5), (0.0, 13.5, 0.0), 56, roll=728, focus=6.0, aperture=0.04, move="orbit",
      note="inside the opening crown"),
    # ---- 8 full bloom, and the concert
    K(RELEASE, at(200.0, 3.0, 19.0), at(SUN_AZ, 14.0, 30.0), 64, roll=720, focus=30.0, aperture=0.01,
      move="tumble", note="out of the top of the crown on the biggest downbeat: the tree lets go"),
    K(S8 + 0.90, at(MOTHER_AZ, 2.0, 36.0), (0.0, 0.0, 0.0), 62, roll=745, focus=36.0, aperture=0.0,
      move="fly", note="thrown up, turned over: straight down, the meadow is one flower"),
    K(S8 + 2.10, at(MOTHER_AZ, 26.0, 30.0), (0.0, 12.0, 0.0), 52, roll=720, focus=40.0, aperture=0.0,
      move="fly", note="pulling back and down on Heavenly Mother's side; the hills flush"),
    K(S8 + 3.10, at(MOTHER_AZ, 46.0, 15.0), (0.0, 20.5, 0.0), 50, roll=720, focus=48.0, aperture=0.0,
      move="hover", note="the end card frame: the tree in the lower third, cream sky above"),
    K(TOTAL, at(MOTHER_AZ, 50.0, 14.0), (0.0, 21.0, 0.0), 50, roll=720, focus=52.0, aperture=0.0,
      move="hover", note="still drifting back at the last frame"),
]
# How the petal moves between keys: gusts ease out hard and settle softly; "float" adds the falling petal's
# rocking (a slow side slip with roll); "hover" keeps a small drift so no frame is ever still.
CAMERA = dict(
    keys=CAMERA_KEYS,
    blend="smooth",
    float=dict(sway=0.22, roll=11.0, rate=0.8),      # metres, degrees, cycles per second, for move="float"
    hover=dict(sway=0.03, roll=0.6, rate=0.35),      # the breath of a petal held in still air
    shutter=[(0.0, 0.5), (TOTAL, 0.5)],              # motion blur by time sampling: half the frame time
)

# ---------------------------------------------------------------------------------------------------------
# The people. look0 is the look before a word reaches them, look1 after; bloom = (start, end, from where).
# motions: (start, end, name); effects: (start, end, name, note). Names follow P3D-BRIEF.md (helper BODY);
# NEW marks what the brief does not promise (see ENGINE_NEEDS).
# ---------------------------------------------------------------------------------------------------------
def _person(pid, who, pos, face, height, garment, look0, look1, bloom, motions, effects, note=""):
    return dict(id=pid, who=who, pos=np.round(np.asarray(pos, float), 3), facing=face, height=height,
                garment=garment, look0=look0, look1=look1, bloom=bloom, motions=motions, effects=effects,
                note=note)


WINTER = dict(look="rim", dust=0.25)                         # a pale outline of cool dust, barely there
BLOOM = dict(look="glitter", garment="petal", twinkle=0.7)   # a glitter body in a garment of petals
PEOPLE = [
    _person("giver", "a young woman", rel("A"), facing("A", "down"), 1.66, "long dress, a scarf that streams",
            BLOOM, BLOOM, None,
            [(-1.0, S1 + 0.9, "palm_blow")],
            [(S1 - 1.0, S1 + 2.6, "palm_stream", "coral petals from her palm, to the stranger"),
             (LET_GO, S1 + 1.9, "petal_spiral", "her whole figure unwinds into the stream (ref 07)"),
             (S7 + 0.6, S7 + 1.8, "form_from_petals", "NEW: she gathers again out of the flock, walking")]),
    _person("stranger", "a man", rel("B", along=-1.1), facing("B", "down"), 1.78, "long coat", WINTER, BLOOM,
            (S1 + 5.6, S1 + 6.9, "right hand"),
            [(S1 + 1.0, S1 + 2.9, "stand"), (S1 + 2.9, S1 + 4.4, "look_up"),
             (S1 + 4.4, S1 + 6.6, "reach_forward"), (S1 + 6.6, S2 + 1.2, "palm_blow")],
            [(S1 + 1.0, S1 + 2.2, "form_from_dust", "pale, head low, back to the wind"),
             (S1 + 5.6, S1 + 6.9, "bloom_from", "NEW: petals and colour spread from the hand that touched the word"),
             (S1 + 6.9, S2 + 1.6, "palm_stream", "his petals, gold now, run ahead with the child")]),
    _person("child", "a child", rel("C", along=-1.6, out=0.2), facing("C", "down"), 1.15, "loose tunic", BLOOM,
            BLOOM, None,
            [(S2 + 0.6, THROW, "run"), (THROW, S2 + 4.2, "lift_arms"), (S2 + 4.2, S3, "stand")],
            [(THROW, S2 + 4.4, "palm_stream",
              "NEW from both lifted hands: a spiral of gold that writes on the lake")],
            note="runs in from 9 m upwind; she returns for the Compliment and at Heavenly Mother's side"),
    _person("worker", "a woman at work", rel("C", along=-0.3), facing("C", "up"), 1.64,
            "tunic and trousers, sleeves rolled", WINTER, BLOOM, (LANDS, S2 + 3.6, "left hand"),
            [(S2 - 2.0, S2 + 1.9, "kneel"), (S2 + 1.9, S2 + 2.6, "look_up"),
             (S2 + 2.6, S2 + 4.4, "rise"), (S2 + 4.4, S3, "arm_round_child")],
            [(LANDS, LANDS + 0.3, "hands_touch_flare", "a gold petal lands in her opening hand"),
             (LANDS, S2 + 3.6, "bloom_from", "NEW")]),
    _person("friend_a", "a man", rel("D", along=-2.1), facing("D", "down"), 1.76, "long coat",
            dict(look="glitter", dim=0.5), BLOOM, (TOUCH, TOUCH + 1.0, "both hands"),
            [(S3 + 0.5, TOUCH - 0.3, "open_arms_low"), (TOUCH - 0.3, TOUCH, "walk"),
             (TOUCH, S4, "reach_hands_pair")],
            [(S3 + 0.9, TOUCH - 0.3, "palm_stream", "NEW variant: petals FALL from his open hands, they do not fly"),
             (TOUCH, TOUCH + 0.35, "hands_touch_flare", "ref 04: two colours meet")],
            note="head bowed; steps to along -0.45"),
    _person("friend_b", "a woman", rel("D", along=2.1), facing("D", "down"), 1.63, "long dress", WINTER, BLOOM,
            (TOUCH, TOUCH + 1.0, "both hands"),
            [(S3 + 0.5, TOUCH - 0.6, "stand"), (TOUCH - 0.6, TOUCH - 0.3, "turn"), (TOUCH - 0.3, TOUCH, "walk"),
             (TOUCH, S4, "reach_hands_pair")],
            [(TOUCH - 0.3, TOUCH, "part_words", "NEW: the letters part round her body as she walks through")],
            note="her back to him until she turns; walks to along +0.45"),
    _person("yielder", "a man", rel("E", along=-1.7), facing("E", "down"), 1.74, "loose tunic and trousers",
            BLOOM, BLOOM, None,
            [(S4 + 0.3, SWEEP, "walk"), (SWEEP, SWEEP + 0.8, "step_aside_sweep"), (SWEEP + 0.8, S5, "stand")],
            [(SWEEP, SWEEP + 0.7, "palm_stream", "NEW from the sweeping arm: white and sky blue, along the stones")]),
    _person("passer", "a woman", rel("E", along=1.7), facing("E", "up"), 1.60, "long coat", WINTER, BLOOM,
            (S4 + 1.6, S4 + 3.4, "head and shoulders"),
            [(S4 + 0.3, S4 + 0.5, "walk"), (S4 + 0.5, S4 + 1.5, "stand"), (S4 + 1.5, S5, "walk")],
            [(S4 + 1.5, S5, "walk_shed", "ref 15: away along the stones toward the tree, under the words")],
            note="walks to rel('E', out=-9) along the stones"),
    _person("speaker", "an older woman", rel("F", along=-0.95), facing("F", "down"), 1.58, "robe", WINTER, BLOOM,
            (S4 + 5.0, S4 + 7.0, "heart"),
            [(S4 + 2.0, S5, "kneel")],
            [(S4 + 3.5, S4 + 7.3, "palm_stream", "a thin stream of clay and peach petals: her thoughts")],
            note="seated on a grassy hummock"),
    _person("listener", "a young man", rel("F", along=0.95), facing("F", "up"), 1.77, "loose tunic", BLOOM,
            BLOOM, None,
            [(S4 + 3.6, S4 + 4.3, "walk"), (S4 + 4.3, S4 + 4.8, "kneel"), (S4 + 4.8, S5, "cup_hands_lean_in")],
            [(S4 + 4.6, S4 + 7.3, "catch", "NEW: he catches every petal in cupped hands; the words rise from them")]),
    _person("runner", "a young woman", run_point(RUN["t0"]), "along the run", 1.68,
            "tunic and trousers, a scarf that streams", WINTER, BLOOM, (S5 + 1.3, S5 + 2.6, "shoulders"),
            [(RUN["t0"], BURST, "run")],
            [(RUN["t0"], S5 + 1.5, "walk_shed", "tiring: dim dust falls from her"),
             (S5 + 1.3, S5 + 2.6, "bloom_from", "NEW: where the tunnel of petals lands on her"),
             (BURST, BURST + 0.9, "petal_spiral", "she runs through the words, leaps and unwinds upward (ref 07)")],
            note="follows the path RUN"),
] + [
    _person("cheer_%d" % (k + 1), who, rel(az, out=side), facing(az, "tree" if side > 0 else "out"), h, g,
            BLOOM, BLOOM, None,
            [(S5 + 0.2, t_blow, "stand"), (t_blow, t_blow + 1.6, "hands_together" if pray else "palm_blow")],
            [] if pray else [(t_blow, t_blow + 1.8, "palm_stream", "an arc of violet and white over the runner")],
            note="NEW motion hands_together (prayer)" if pray else "")
    for k, (az, side, h, who, g, t_blow, pray) in enumerate([
        (163.0, 2.4, 1.72, "a man", "long coat", S5 + 1.2, False),
        (172.0, -2.6, 1.20, "a child", "loose tunic", S5 + 2.2, False),
        (181.0, 2.2, 1.60, "an older woman", "robe", S5 + 3.2, True),
        (190.0, -2.4, 1.80, "a man", "loose tunic and trousers", S5 + 4.3, False),
        (199.0, 2.6, 1.64, "a woman", "long dress", S5 + 5.3, False)])
] + [
    _person("knelt", "an older man", rel("H", along=0.55), facing("H", "up"), 1.70, "long coat", WINTER, BLOOM,
            (CLASP, S6 + 3.6, "right hand"),
            [(S6 - 1.5, S6 + 3.0, "kneel"), (S6 + 3.0, S6 + 4.0, "rise_helped"), (S6 + 4.0, S6 + 5.2, "palm_blow")],
            [(CLASP, CLASP + 0.4, "hands_touch_flare", "ref 04: the clasp"),
             (CLASP, S6 + 3.6, "bloom_from", "NEW: from the held hand"),
             (BREATHE, BREATHE + 0.9, "palm_stream", "the rose letters go with his breath, to the child")]),
    _person("helper", "a young man", rel("H", along=-0.75), facing("H", "down"), 1.79, "loose tunic", BLOOM,
            BLOOM, None,
            [(S6 - 0.6, S6 + 0.5, "walk"), (S6 + 0.5, S6 + 3.0, "reach_forward"), (S6 + 3.0, S6 + 4.0, "pull_up")],
            [], note="bends to offer an open palm; NEW motions rise_helped and pull_up are one pair"),
    _person("child_again", "the child", _I, SUN_AZ, 1.15, "loose tunic", BLOOM, BLOOM, None,
            [(S6 + 4.3, S7, "jump_arms_up_twirl"), (S7, ARMS_OPEN, "run")],
            [(S6 + 4.4, S7, "petal_fall", "petals fall round her; the words open over her like a blossom")],
            note="the same child as in section 2, seen from behind, arms up to the light; she runs on to "
                 "Heavenly Mother"),
    _person("mother", "Heavenly Mother, only from behind", _M, (MOTHER_AZ + 180.0) % 360.0, 1.80,
            "robe and a long veil from head to hem", dict(look="glitter", garment="veil", color=("#fff0cc", WHITE)),
            dict(look="glitter", garment="veil", color=("#fff0cc", WHITE)), None,
            [(MOTHER_SEEN, ARMS_OPEN, "stand"), (ARMS_OPEN, ARMS_OPEN + 1.0, "open_arms_low"),
             (ARMS_OPEN + 1.0, TOTAL, "arm_round_child")],
            [(MOTHER_SEEN, BEHIND_MOTHER, "form_from_dust",
              "the flock parts and she is there, gathered out of light"),
             (MOTHER_SEEN, TOTAL, "veil_fray",
              "NEW: the veil streams downwind and its hem frays into petals without end"),
             (BEHIND_MOTHER, RELEASE, "rays", "the sun behind her head, rays fanning (refs 10, 13)")],
            note="never seen from the front: she is not drawn before MOTHER_SEEN (until then the camera is on "
                 "her front side, 20 m off); from then on the camera stays behind her or straight above "
                 "(checked below)"),
]
# Everyone walks to the tree in bloom from S7 (walk_shed), is passed by the camera at shoulder height, and
# stands in a ring behind Heavenly Mother, facing the tree, so the last frames see them all from behind; arms
# lift on RELEASE. The giver and the runner, who let themselves go, gather again out of the flock.
GATHER = dict(t0=S7 - 1.0, arrive=RELEASE - 1.0, lift=RELEASE,
              who=[p["id"] for p in PEOPLE if p["id"] not in ("mother", "child", "child_again")],
              ring=dict(az=(MOTHER_AZ - 48.0, MOTHER_AZ + 48.0), r=(11.0, 15.0)),
              # three of them brush past the lens on the way in: (when, where they are then)
              near_camera=[(S7 + 1.05, at(336.0, 15.6, 0.0)), (S7 + 1.45, at(350.0, 14.0, 0.0)),
                           (S7 + 1.9, at(4.0, 12.9, 0.0))])

# ---------------------------------------------------------------------------------------------------------
# The words (helper WORDS): each expression as letters made of petals in the world.
#   center, right, up, width   the plane the letters stand in: its middle, its reading direction, the
#                              direction of the letters' tops (unit vectors), and the block's width in metres
#   arrive, read, leave        petals begin to land; (first, last) second the whole wording is sharp and
#                              legible; the last petal has left
#   ground                     what is behind the letters during the reading moment
#   letters                    "paint": petals painted in the ink (a deep tone of the colour) with a light rim;
#                              "light": petals of light (cream and the colour), for deep grounds
# ---------------------------------------------------------------------------------------------------------
def _lerp_cam(t):
    """The camera at t by straight lines between keys (enough to place the words and to check framing)."""
    ks = CAMERA_KEYS
    if t <= ks[0]["t"]:
        return ks[0]
    for a, b in zip(ks, ks[1:]):
        if a["t"] <= t <= b["t"]:
            u = (t - a["t"]) / max(b["t"] - a["t"], 1e-9)
            return dict(t=t, pos=a["pos"] + (b["pos"] - a["pos"]) * u,
                        target=a["target"] + (b["target"] - a["target"]) * u,
                        fov=a["fov"] + (b["fov"] - a["fov"]) * u)
    return ks[-1]


def _facing_plane(center, t):
    """An upright plane at center that faces the camera of time t: (right, up)."""
    f = np.asarray(center, float) - _lerp_cam(t)["pos"]
    f[1] = 0.0
    f /= np.linalg.norm(f)
    return np.round(np.array([-f[2], 0.0, f[0]]), 4), np.array([0.0, 1.0, 0.0])


def _word(i, center, width, arrive, read, leave, ground, letters, arrives, leaves, plane=None, center1=None,
          right1=None, carried=None):
    right, up = plane if plane is not None else _facing_plane(center, read[0])
    e = EXPRESSIONS[i]
    return dict(i=i, label=e["label"], lines=e["lines"], color=e["color"], ink=e["ink"], bough=e["bough"],
                center=np.round(np.asarray(center, float), 3), right=right, up=up, width=float(width),
                center1=None if center1 is None else np.round(np.asarray(center1, float), 3), right1=right1,
                carried=carried,
                arrive=arrive, read=read, leave=leave, ground=ground, letters=letters, arrives=arrives,
                leaves=leaves, label_shown=True)


_C_IN = -rel("C") / np.linalg.norm(rel("C"))           # toward the tree at C: the top of the letters on the lake
_C_WIND = np.array([np.cos(np.radians(STATIONS["C"])), 0.0, -np.sin(np.radians(STATIONS["C"]))])
WORDS = [
    _word(GREETING, rel("B", along=1.0, up=1.55), 2.8, S1 + 1.9, READ["Greeting"], S1 + 6.6,
          ground="pale gold haze toward the sun, clear of the far tree", letters="paint",
          arrives="the giver's stream winds once round the stranger and settles left to right",
          leaves="half fall on him (he blooms), half fly to the tree: bough 0 buds"),
    _word(GRATITUDE, rel("C", out=-5.2, along=1.2, up=0.02), 11.0, THROW + 0.1, READ["Gratitude"], S3 + 0.9,
          ground="the lake from straight above: deep blue", letters="light", plane=(_C_WIND, _C_IN),
          arrives="a spiral from the child's lifted hands rains onto the water; each petal lands with a ring "
                  "and floats",
          leaves="the gust lifts the letters off the water in one sheet: bough 1 buds"),
    _word(APOLOGY, rel("D", up=1.25), 3.5, S3 + 0.9, READ["Apology"], TOUCH + 0.35,
          ground="pearl haze over the water", letters="paint",
          arrives="petals fall from the friend's open hands and drift into the letters; the letters keep "
                  "shedding petals that ring the water",
          leaves="the other friend walks through them; at the touch they turn into the Inclusiveness"),
    _word(INCLUSIVENESS, rel("D", up=3.05), 3.9, TOUCH, READ["Inclusiveness"], S4 + 0.8,
          ground="blush sky in a clear opening of the blossoming crown", letters="paint",
          arrives="the Apology's own petals turn in the air, flush pink and rise (a morph, about 0.4 s)",
          leaves="upward with the falling blossom: boughs 2 and 3 bud together"),
    _word(CONCESSION, rel("E", up=2.6), 3.8, SWEEP, READ["Concession"], S4 + 4.6,
          ground="the deep azure opposite the sun", letters="light",
          arrives="from the sweep of the yielder's arm: out along the stepping stones, then up",
          leaves="the petals follow the passer along the stones to the tree: bough 4 buds"),
    _word(RESPECT, rel("F", up=2.0), 3.0, S4 + 3.9, READ["Respect"], S5 + 0.5,
          ground="cream discs: the world melted out of focus", letters="paint",
          arrives="the speaker's petals, caught in the listener's cupped hands, rise from them",
          leaves="on the gale: bough 5 buds"),
    _word(ENCOURAGEMENT, run_point(_T_ENC[0], ahead=10.5, up=5.4), 9.0, S5 + 1.0, _T_ENC, BURST + 0.7,
          ground="pale racing haze above the horizon", letters="paint",
          plane=(np.round(rel(run_az(_T_ENC[0])) / np.linalg.norm(rel(run_az(_T_ENC[0]))), 4),
                 np.array([0.0, 1.0, 0.0])),
          center1=run_point(_T_ENC[1], ahead=10.5, up=5.4),      # it travels: where it is when the reading ends
          right1=np.round(rel(run_az(_T_ENC[1])) / np.linalg.norm(rel(run_az(_T_ENC[1]))), 4),
          carried=dict(path="RUN", ahead=[(S5 + 1.0, 10.5), (_T_ENC[1], 10.5), (BURST, 0.0)], up=5.4),
          arrives="five arcs from five open palms join over the runner and run ahead of her",
          leaves="she catches the words up, runs through them, and they burst into blossom: bough 6 buds"),
    _word(CONSIDERATION, rel("H", up=2.1), 2.5, CLASP, READ["Consideration"], BREATHE + 0.7,
          ground="warm cream discs", letters="paint",
          arrives="blooming out of the two clasped hands, upward",
          leaves="on a breath across an open palm; the same petals become the Compliment: bough 7 buds"),
    _word(COMPLIMENT, _I + at(0, 0, 2.75), 2.8, BREATHE + 0.2, READ["Compliment"], S7 + 0.9,
          ground="the bright sky above the sun", letters="paint",
          arrives="the rose petals turn lavender and open outward from the middle like a blossom",
          leaves="the great gust takes them first into the flock: bough 8 buds"),
]
for _w in WORDS:     # a bough buds when its word comes home (the flight to the tree takes about a second)
    GREAT_TREE["boughs"][_w["bough"]]["bud"] = round(_w["leave"] + 1.0, 2)
GREAT_TREE["boughs"][APOLOGY]["bud"] = GREAT_TREE["boughs"][INCLUSIVENESS]["bud"]   # they come home together

# ---------------------------------------------------------------------------------------------------------
# The wind and the petals.
# ---------------------------------------------------------------------------------------------------------
WIND = dict(
    field="wheel",            # round the tree toward growing azimuth, drifting inward along the spiral
    base=[(0.0, 0.35), (S6 - 0.3, 0.35), (S6 + 0.6, 0.05), (S6 + 4.0, 0.10), (S7, 0.6), (S8, 0.5), (TOTAL, 0.2)],
    # gusts: (time, strength, what the camera does with it). Garments, veil, grass, boughs and petals all lean
    # with the same gust.
    gusts=[(LET_GO, 1.0, "torn off, tumbling"), (S2, 0.8, "a banked skim"), (S3, 0.9, "a spinning dive"),
           (TOUCH, 0.5, "blown back by the blossom"), (S4, 0.7, "a banked swoop"),
           (S5, 1.0, "flung outward, a full barrel roll"), (BURST, 0.6, "through the burst"),
           (BREATHE, 0.5, "a breath across a palm"), (S7, 1.0, "banking round the tree in the flock"),
           (RELEASE, 1.2, "thrown up and turned over"), (FINAL_HIT, 0.5, "the crown shakes behind the end card")],
)
PETALS = [   # every stream of petals: who lets them go, where they land (counts are first guesses)
    dict(id="giver_stream", t=(S1 - 1.0, S1 + 2.6), start="giver", end="word:Greeting", n=9000, look="first_light"),
    dict(id="greeting_home", t=(S1 + 5.6, S1 + 7.6), start="word:Greeting", end=("stranger", "bough:0"), n=9000),
    dict(id="stranger_breath", t=(S1 + 6.9, S2 + 1.6), start="stranger", end="child", n=5000, look="gold_on_blue"),
    dict(id="child_spiral", t=(THROW, S2 + 4.4), start="child", end="word:Gratitude", n=26000, floats=True),
    dict(id="gratitude_sheet", t=(S3, S3 + 1.9), start="word:Gratitude", end=("tree_d", "bough:1"), n=26000),
    dict(id="apology_fall", t=(S3 + 0.9, TOUCH - 0.3), start="friend_a", end="word:Apology", n=8000, falls=True),
    dict(id="the_answer", t=(TOUCH - 0.3, TOUCH + 0.35), start="word:Apology", end="word:Inclusiveness", n=8000,
         morph=True),
    dict(id="tree_d_blossom", t=(TOUCH, S5), start="tree_d", end="water", n=30000, falls=True),
    dict(id="inclusiveness_home", t=(S4, S4 + 1.8), start="word:Inclusiveness", end=("bough:2", "bough:3"), n=8000),
    dict(id="the_sweep", t=(SWEEP, SWEEP + 0.6), start="yielder", end="word:Concession", n=7000, via="stones"),
    dict(id="concession_home", t=(S4 + 3.8, S4 + 5.6), start="word:Concession", end=("passer", "bough:4"), n=7000),
    dict(id="thoughts", t=(S4 + 3.5, S4 + 7.3), start="speaker", end=("listener", "word:Respect"), n=6000),
    dict(id="respect_home", t=(S4 + 7.3, S5 + 1.5), start="word:Respect", end="bough:5", n=6000),
    dict(id="cheer_tunnel", t=(S5 + 1.0, BURST), start="cheer_1..5", end="word:Encouragement", n=40000,
         carried="RUN"),
    dict(id="encouragement_burst", t=(BURST, S6 + 1.5), start="word:Encouragement", end=("air", "bough:6"),
         n=40000, hangs=True),     # in the lull these petals hang in the air and sink slowly: the breath
    dict(id="clasp_bloom", t=(CLASP, CLASP + 0.4), start="hands:help", end="word:Consideration", n=6000),
    dict(id="the_breath", t=(BREATHE, BREATHE + 0.7), start="word:Consideration", end="word:Compliment", n=6000,
         morph=True),
    dict(id="compliment_home", t=(S7, S7 + 1.9), start="word:Compliment", end="bough:8", n=6000),
    dict(id="flock", t=(S7, S7 + 5.6), start="meadow", end="tree", n=120000, arms=4),   # every petal of the meadow
    dict(id="veil_fray", t=(MOTHER_SEEN, TOTAL), start="mother", end="downwind", n=14000),
    dict(id="helix", t=(CLIMB - 0.4, RELEASE), start="flock", end="boughs 0..8 in order", n=60000),
    dict(id="release", t=(RELEASE, RELEASE + 4.5), start="tree", end="dome", n=300000, speed=14.0, radius=60.0,
         colors="nine sectors, one per bough"),
    dict(id="title_rain", t=(S8 + 0.5, S8 + 2.7), start="release", end="end card title", n=0,
         note="the 2D title's own petal animation; the 3D petals stay behind the text box"),
    dict(id="end_drift", t=(S8 + 2.0, TOTAL), start="dome", end="rising slowly", n=20000,
         keep_out="the end card's text box"),
]

# ---------------------------------------------------------------------------------------------------------
# The end card: the existing end card style (same wording, sizes, colours and layout as the first film's;
# not redesigned). Drawn by the 2D text system on top of the 3D picture. Only the way the title forms is this
# film's: the engine's existing "petal" text animation instead of "ribbon" (phase B checks it in stills and
# goes back to "ribbon" if it reads less well). The nine expressions are NOT drawn by the 2D system in this
# film: PHRASES lists them all as off.
# ---------------------------------------------------------------------------------------------------------
TEXT_SHADOW = 0.0                 # nothing dark behind any text
FORM_DUR = 1.5                    # the title forms faster than an expression would (only the title uses it)
TITLE_HIT = S8 + 2.7              # 55.2: the title is whole
T_FORM = TITLE_HIT - FORM_DUR - 0.75
TAG_T0, TAG_T1 = S8 + 1.6, TITLE_HIT - 0.05     # the three lines are whole just before the title
OFF = dict(form=1e9, hold=1e9, star=1e9)
PHRASES = [dict(label=e["label"], lines=e["lines"], size=120, **OFF) for e in EXPRESSIONS]
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="petal",
             colors=(theme.CORAL, theme.PEACH))
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
FRAGMENTS = []                    # no other words on screen: no lyrics, no opening line
END_CARD = dict(readable=(TITLE_HIT, TOTAL), fade_out=None,      # held to the last frame, never to black
                last_hit=dict(t=FINAL_HIT, what="a gust shakes colour through the crown, petals sweep behind "
                                                "the text, exposure 1.0 to 1.15 and back in 0.8 s"))
EXPOSURE_KEYS = [(0.0, 1.0), (S8 - 0.05, 1.0), (S8 + 0.10, 1.30), (S8 + 0.9, 1.0), (FINAL_HIT - 0.05, 1.0),
                 (FINAL_HIT + 0.08, 1.15), (FINAL_HIT + 0.8, 1.0), (TOTAL, 1.0)]

# ---------------------------------------------------------------------------------------------------------
# What this film needs from the 3D layer beyond what P3D-BRIEF.md promises, most important first.
# ---------------------------------------------------------------------------------------------------------
ENGINE_NEEDS = [
    "PAINT for point sets: petals, letters and garments that are their own colour on a bright day sky (drawn "
    "over the picture by depth with a share of their own light, like the 2D engine's nature paint and "
    "coloured letters). Additive light alone pales to white on cream and to pink on blue; this is a day film.",
    "WORDS as petals with open targets: letters filled with petal sprites; each word hands out its target "
    "points so the film's own streams can land in them left to right; a word to word morph with a colour "
    "change (Apology to Inclusiveness, Consideration to Compliment); any plane, including flat on the lake "
    "(floating, bobbing, a ring where each petal lands, no mirror image) and a plane that travels along a "
    "path (the runner's banner); leaving as a sheet, as a burst, onto a body; a clear box other petals avoid.",
    "BLOOM on a body: one setting 0..1 that sweeps from a contact point (a hand) across the body, changing "
    "the winter rim look into a glitter body in a garment of petals; the body's surface points and normals "
    "at t handed out, so petals can land on it and leave it; hems, scarves and the veil that fray into "
    "petals; a body that gathers from a stream of petals (the reverse of the petal spiral).",
    "MOTIONS beyond the brief: step aside with a sweeping arm; lift both arms (throw); cupped hands and lean "
    "in to listen; hands together in prayer; kneel at work and rise; one person drawing another up from a "
    "knee by the hand (a pair); a child (1.15 m) who runs, jumps with arms up and twirls; turn on the spot; "
    "Heavenly Mother's near arm coming round a child at her side; walking along a given path with feet "
    "that stay on the water.",
    "ONE WIND for everything: wind(pos, t) with gust fronts on given times, driving cloth, veil, hair, grass, "
    "boughs and petals alike, and readable by the song file (the camera rides it).",
    "CAMERA: roll through full turns (cumulative degrees); a float mode (a falling petal's rocking: side "
    "slip tied to roll) besides the handheld drift; focus that follows a named point set; speed ramps on a "
    "path; motion blur with a shutter Track; a view straight down that keeps its heading.",
    "PETAL LIGHT: petals that glow warm when the sun is behind them and glint when they tumble flat to it; "
    "petal shaped bokeh; 300 to 500 thousand petals in one frame for the release.",
    "LAKE: deep and blue seen from straight above (less mirror, more depth), sun glitter, a layer of things "
    "that float on the surface, rings where petals land.",
    "DAY WORLD pieces (I can build these as point sets myself if CORE has no time): a great tree with nine "
    "boughs that bud and bloom one at a time, small blossom trees, a water meadow of grass tufts and flowers "
    "that greens along a front, stepping stones, far hills that can flush with blossom, racing clouds.",
    "SHAFTS through a crown: rays of the sun that the boughs, the veil and the petals break up.",
]


def build(scene):
    """Phase B: fills the 3D scene (the great tree, the meadow, the petals, the people, the words).
    P3D-BRIEF.md: a song reaches the scene through P3D = dict(camera=..., world=..., setup=build)."""
    raise NotImplementedError("ten_05_petals is the phase A skeleton: the 3D layer is not on this branch yet")


P3D = dict(camera=CAMERA, world=WORLD, setup=build)


# ---------------------------------------------------------------------------------------------------------
# A check of the data without graphics: PYTHONPATH=engine python engine/songs/ten_05_petals.py
# ---------------------------------------------------------------------------------------------------------
def _project(cam, pts):
    """Screen x, y in 0..1 (y up) of world points for a camera dict (the maths of p3d.api.CameraState)."""
    f = cam["target"] - cam["pos"]
    f = f / np.linalg.norm(f)
    r = np.cross(f, np.array([0.0, 1.0, 0.0]))
    r = r / np.linalg.norm(r) if np.linalg.norm(r) > 1e-6 else np.array([1.0, 0.0, 0.0])
    u = np.cross(r, f)
    d = np.asarray(pts, float) - cam["pos"]
    z = d @ f
    fl = 1.0 / np.tan(np.radians(cam["fov"]) * 0.5)
    return np.stack([(d @ r) * fl / (ASPECT * z) * 0.5 + 0.5, (d @ u) * fl / z * 0.5 + 0.5], axis=1), z


def _block_height(w):
    """A rough height in metres of a word's block (label and lines) from its width and longest line."""
    cap = w["width"] / (0.52 * max(len(s) for s in w["lines"]))
    return cap * (1.45 * len(w["lines"]) + 1.0)


def _check():
    problems = []
    ts = [k["t"] for k in CAMERA_KEYS]
    if any(b <= a for a, b in zip(ts, ts[1:])):
        problems.append("camera key times are not strictly increasing")
    print("camera: %d keys, 0 to %.1f s" % (len(ts), ts[-1]))
    for a, b in zip(CAMERA_KEYS, CAMERA_KEYS[1:]):
        v = np.linalg.norm(b["pos"] - a["pos"]) / (b["t"] - a["t"])
        if a["pos"][1] < 0.3 or b["pos"][1] < 0.3:
            problems.append("camera under 0.3 m at %.2f" % a["t"])
        print("  %5.2f to %5.2f  %-6s %5.1f m/s  fov %2.0f to %2.0f  %s" % (
            a["t"], b["t"], a["move"], v, a["fov"], b["fov"], a["note"][:58]))
        if v > 32.0:
            problems.append("camera faster than 32 m/s from %.2f to %.2f (%.1f)" % (a["t"], b["t"], v))
    print("words:")
    last = -1.0
    for w in WORDS:
        dur = w["read"][1] - w["read"][0]
        hgt = _block_height(w)
        shares = []
        for t, c, rt in ((w["read"][0], w["center"], w["right"]),
                         (w["read"][1], w["center"] if w["center1"] is None else w["center1"],
                          w["right"] if w["right1"] is None else w["right1"])):
            corners = [c + rt * sx * w["width"] / 2 + w["up"] * sy * hgt / 2 for sx in (-1, 1) for sy in (-1, 1)]
            xy, z = _project(_lerp_cam(t), corners)
            shares.append((xy[:, 0].max() - xy[:, 0].min(), xy[:, 0].min(), xy[:, 0].max(), xy[:, 1].min(),
                           xy[:, 1].max(), z.min()))
        s0, s1 = shares
        print("  %-13s read %5.2f to %5.2f (%.1f s)  width %2.0f%% to %2.0f%% of the frame  x %.2f..%.2f "
              "y %.2f..%.2f" % (w["label"], w["read"][0], w["read"][1], dur, 100 * s0[0], 100 * s1[0], s0[1],
                               s0[2], s0[3], s0[4]))
        if dur < 2.5:
            problems.append("%s is readable for only %.2f s" % (w["label"], dur))
        for s in shares:
            if s[0] < 0.45:
                problems.append("%s fills only %.0f%% of the frame width" % (w["label"], 100 * s[0]))
            if s[1] < 0.03 or s[2] > 0.97 or s[3] < 0.04 or s[4] > 0.97 or s[5] <= 0:
                problems.append("%s is not inside the frame" % w["label"])
        if not (w["arrive"] < w["read"][0] < w["read"][1] <= w["leave"]):
            problems.append("%s: arrive, read, leave are out of order" % w["label"])
        if w["read"][0] < last - 1e-6:
            problems.append("%s reads before the word before it has been read" % w["label"])
        last = w["read"][1]
    if [w["label"] for w in WORDS] != [e["label"] for e in EXPRESSIONS] or len(WORDS) != 9:
        problems.append("the nine expressions are not all placed, in campaign order")
    if WORDS[-1]["leave"] > S8:
        problems.append("an expression is still on screen in the last section")
    # Heavenly Mother only from behind: while she can be in frame the camera is behind her or far above
    m_face = at(MOTHER_AZ + 180.0, 1.0)
    for t in np.arange(MOTHER_SEEN, TOTAL + 1e-6, 0.05):
        cam = _lerp_cam(float(t))
        xy, z = _project(cam, [_M + np.array([0.0, 1.6, 0.0])])
        seen = z[0] > 0 and 0.0 <= xy[0, 0] <= 1.0 and 0.0 <= xy[0, 1] <= 1.0
        d = cam["pos"] - _M
        above = d[1] > 3.0 * np.hypot(d[0], d[2])
        if seen and not above and float(d @ m_face) > 0.0:
            problems.append("the camera is in front of Heavenly Mother at %.1f s" % t)
    if TOTAL - END_CARD["readable"][0] < 4.0:
        problems.append("the end card is readable for under 4 s")
    for name, keys in (("PALETTE_KEYS", PALETTE_KEYS), ("EXPOSURE_KEYS", EXPOSURE_KEYS)):
        if any(b[0] <= a[0] for a, b in zip(keys, keys[1:])):
            problems.append("%s times are not strictly increasing" % name)
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    if chr(0x2013) in src or chr(0x2014) in src:
        problems.append("an en dash or em dash is in this file")
    print("people: %d; petal streams: %d; boughs bud at %s" % (
        len(PEOPLE), len(PETALS), ", ".join("%.1f" % b["bud"] for b in GREAT_TREE["boughs"])))
    print("end card: whole at %.1f s, held %.1f s" % (TITLE_HIT, TOTAL - TITLE_HIT))
    print("\n".join("PROBLEM: " + p for p in problems) if problems else "ok")
    return not problems


if __name__ == "__main__":
    raise SystemExit(0 if _check() else 1)
