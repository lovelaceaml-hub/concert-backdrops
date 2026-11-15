"""Film 09 of ten: THE VEIL. A 60 second promo for the Healing Concert "The Words of Mother's Love".

PHASE A: direction, not rendering. This file holds the treatment (this text) and the timeline as data, in the
conventions of the 3D layer engine/p3d: metres, y up, the lake is the plane y = 0, a person is about 1.7 m
tall, the arch of nine lights stands over the origin in the plane z = 0 and faces +z, azimuth 0 looks along
+z. Nothing is drawn yet: build() at the end says what phase B has to make.
`python engine/songs/ten_09_the_veil.py` prints the timeline and checks the film's own rules; with engine/p3d
on the path it also runs the particle words' own check (helper WORDS) through this camera.

LOGLINE
  We follow Heavenly Mother from behind as she walks over a night lake toward the first light. Her veil
  streams back across the water as a river of light. Wherever it reaches, people rise out of it, say the nine
  Words of Mother's Love to one another and go on in its light behind her, until at sunrise she lifts her arms
  and the veil rises to become the dawn sky and the arch of nine lights.
  The spine is the campaign's own line, "Where a mother's love reaches, peace settles": the veil is that
  reach. (It is the thought of the film, not text on screen.)

WHAT MAKES THIS FILM ITS OWN (against the other nine)
  World    One cloth. The veil is river, road, roof, loom and at last the sky. No wave to surf, no comets, no
           garden, no storm: everything on screen is Mother's veil or what it touches.
  Camera   A needle. She is always ahead of us, toward the light; we never overtake her and never see her
           from the front. The camera rides the cloth, goes under it, bursts up through it and passes through
           the words themselves (every song change is a pass through cloth: a wash of huge soft discs); it
           rolls through the loom like a shuttle; it ends in a slow half circle behind her.
  Words    Embroidery. Each expression is sewn into a fold of the veil that opens flat toward us, in warm
           white and gold only (nine colours are film 10's idea), and leaves as thread or as that wash.
  People   Made of the veil's own particles, their hems still joined to it. They act each word in pairs,
           close to the camera, with real contact; then their light goes back into the veil and travels on
           in it after her (two more glints at her hem each time), and at sunrise it gives them all back.
  Palette  Warm white and gold on deep blue; one cool silver blue for "the other person" (ref 04); rose only
           from the breath onward; the campaign day for the end card.

HEAVENLY MOTHER (present in every section; rules, checked in code where they can be)
  Only from behind, veiled, or as a hand. The camera stays behind her and within 60 degrees of straight behind
  (REAR_LIMIT, checked on every frame). Her head veil is deep and hangs forward of the face, so at any allowed
  angle only veil is seen. She is never scaled, never dissolved, never flown about, never hidden by words.
  When the day comes she is not taken apart: she walks on into the brightness of the sun.
  How she is seen, section by section: half body with rays (1); the small figure the whole road runs to (2);
  framed in the bright mouth of the canopy, then the light behind an embrace (3); the head of the river, then
  seen through a doorway (4); between two people who listen (5); her hand, then her whole figure waiting
  (6); half body with a child, the sun behind her head (7); walking into the sun under the arch (8).

THE FILM, SHOT BY SHOT (times on the provisional section map 0, 7.5, 15 ... 52.5; every time in the data
below hangs off SECTIONS, so the map can be swapped when the medley is final)

 1  0.0 to 7.5   THE CAST. Night water, Milky Way.                                      Words: Greeting
    0.00  Eye: no black, no fade. Frame one is Heavenly Mother from behind, veiled, half body, filling the
          frame; the one warm star of the horizon is hidden behind her head and its rays fan round her
          (ref 10). Camera: 2.4 m behind her at shoulder height, creeping in. Light: gold rim on indigo.
    0.55  THE CAST (first hit): she opens both arms low and the veil leaves her shoulders toward us. Sheets
          of gold points rush over the lens and we are carried backward with its hem, low over the water,
          44 m in two seconds, while the veil unrolls across the lake like a road of light, mirrored.
          Camera: pulled back and up, lens opening from 38 to 62 degrees, motion blur.
    2.60  Wide for one breath: a small bright figure at the head of an immense shining veil, stars above
          and below. Then we swoop down along it. Two people gather out of its light, one on each bank, and
          walk toward each other; between them the hem curls up like a turning page.
    4.2 to 6.8  GREETING is read on that fold, above Mother's distant figure; the walkers are soft rim-lit
          profiles coming in from the frame edges (ref 01, 16). Camera: creeps forward at head height.
    6.8 to 7.5  Focus falls to the walkers: one lifts an open hand, they clasp hands, her small bright
          figure between their two profiles. We rise over the joined hands; the fold sweeps over the lens.
 2  7.5 to 15.0  THE ROAD. Blue mist.                                 Words: Consideration, then Gratitude
    7.5   New: speed. Out of the wash we are far back in a bank of mist, skimming half a metre above the
          veil, a road now: 40 m in 0.9 s, banking through its bends, the cloth streaming against us, her
          light ahead growing.
    8.7 to 11.3  The road is closed by a sheer curtain with CONSIDERATION sewn on it. Through the cloth,
          soft: someone kneeling, spent, beside a burden of dim light; someone bending to them. Slow push.
    11.3 to 12.3  We pass through the curtain and arrive as two hands, one gold, one silver blue, meet and
          flare (ref 04, at arm's length, not a macro: film 02 owns the macro). The kneeling one is lifted.
    12.3 to 15.0  The flare runs up the next fold and sews GRATITUDE above Mother's figure; in front, soft,
          the one who was helped bows with a hand on the heart. Camera: a slow crane up.
 3  15.0 to 22.5 THE CANOPY. Inside the veil.                  Words: Apology, which becomes Inclusiveness
    15.0  New: on the downbeat the Gratitude fold sweeps over us and the whole veil heaves up over our
          heads. We are under it: a long roof of warm amber cloth, light falling through the weave in soft
          shafts, violet night outside, Mother walking in the bright mouth of it ahead.
    16.2 to 19.0  One person sits turned away, head bowed, coming apart: particles stream off one side
          (ref 06). Another comes, kneels, lays a hand on the shoulder. APOLOGY hangs on a swag of the roof
          above them, its stitches loose. Camera: a slow low arc round the pair.
    19.0 to 19.85  THE MENDING: the hurt one turns, they embrace, and her light is exactly behind them: its
          rays break round the two. Every particle that left flies back; the body is whole (a healing
          concert). The loose stitches pull tight and are sewn again...
    19.85 to 22.4  ...as INCLUSIVENESS on the same swag. Camera: draws back and rises a little: the embrace
          low in the picture, Mother small beyond it, the words above her.
 4  22.5 to 30.0 THE RIVER AND THE NARROWS. High clear air.                              Words: Concession
    22.5  New: height. We burst up through the roof and climb 36 m in a second and a half. The veil is a
          river of light with braided arms across the whole lake, mirrored, people along every arm, the far
          hills on a first line of rose, and she at its head.
    24.0 to 25.4  The camera noses over and dives, rolling, to where two arms join in a strait one person
          wide. A wall of cloth with a doorway stands there; through the door, Mother and her light.
    25.6 to 28.3  Two people reach the door together. CONCESSION is sewn across the wall above it. One
          stops, steps back and opens a palm toward the door.
    28.3 to 30.0  The other bows the head and walks through into the light; a thread of the words follows.
          Then the first; then we do.
 5  30.0 to 37.5 THE LOOM. Strings of light.                                               Words: Respect
    30.0  New: the veil unwoven. Thousands of taut threads run across the lake to her and sound with the
          music like harp strings. The camera is the shuttle: 40 m through the warp in one full roll.
    32.8 to 35.5  Two people face each other in profile, Mother between them in the distance. One gives
          thoughts as a stream of gold from an open palm (ref 14); the other has turned fully toward them,
          leaning in, and answers in silver blue. The two streams cross the warp and weave a panel of
          fresh cloth above them: RESPECT, two different threads in one cloth.
    35.5 to 37.5  The listener cups the other's light in both hands and holds it to the chest. The loom
          falls silent thread by thread until one is left. We rush along it, and the rush ends, on the
          breath, at a hand.
 6  37.5 to 45.0 THE THREAD. The breath; still water.                                Words: Encouragement
    37.5  New: stillness. Heavenly Mother has stopped. Her left hand, from behind, held low and a little
          back, closed lightly on the one thread. Macro, very shallow focus, the first thin line of rose on
          the horizon. The camera only breathes.
    39.0 to 40.0  We draw back along the thread, over the head of a child who is stepping onto it, arms out
          for balance (it lies on the water, a line to walk). Close to us someone kneels, hands clasped.
    40.0 to 43.0  ENCOURAGEMENT hangs in the still air above the child, sewn from the thread's slow sparks.
          The child wobbles, steadies, walks on toward her, who waits. Camera: stays with the one who
          roots, a handheld breath.
    43.0 to 45.0  We go the last steps with the child. A small hand reaches up into hers: contact, a flare
          (seen from behind and below). The words go up as flakes. The thread bursts back into the veil.
 7  45.0 to 52.5 THE LIFTING. Sunrise.                                   Words: Compliment, then all nine
    45.0  New: the sun, straight ahead of her; the veil floods back in rose gold. The camera begins a slow
          half circle behind her and the child, hand in hand, from 55 degrees left to 55 degrees right of
          straight behind. Halfway the sun goes behind her head and its rays break round it. The veil gives
          back everyone it gathered: they rise out of it on both sides, at many depths, arms lifting.
    46.5 to 49.2  COMPLIMENT, the largest words of the film, burnt out of the lifting veil above them by
          the rays, turning with us.
    49.2 to 52.5  She raises both arms, the child's hand in hers. The whole veil peels off the lake from the
          far end toward us (its mirror image parts from it), streams over our heads and spreads across the
          sky. For one breath all nine expressions are written small across it; their threads run to nine
          pearls on the arc of veil between her raised hands; the arc lifts off, grows and stands over the
          lake as the arch of nine lights. Rose, then day. Camera: to straight behind, back and up.
 8  52.5 to 60.0 THE CONCERT. The campaign day.                                                 End card
    A last fold of the veil crosses the sky and the title stands behind it: the existing end card, its style
    untouched: "The Words of Mother's Love" (coral, anim "ribbon"), "Healing Concert", and in navy "Sunday,
    December 6 (middle dot) 4:30 PM", "World Mission Society Church of God", "6720 W Sahara Ave, Las Vegas".
    All five whole by 55.05 and held to the last frame (4.95 s). On the last hit the nine lights flare and a
    ripple of rose gold runs through the sky's weave (colour and motion, exposure 1.0 to 1.22 and back: it
    shows on a pale sky). Under the arch Mother and the child walk on into the sun and its brightness takes
    them; the procession follows as soft lights. The camera keeps craning up and back. No fade to black.

THE NINE EXPRESSIONS (exact campaign wording and labels: NINE below; how each arrives, is read, leaves)
  Greeting       sewn on the first fold that curls up from the unrolled hem; read 4.2 to 6.8 over two
                 walkers who meet; leaves as a wash of bokeh when the fold sweeps over us.
  Consideration  on a sheer curtain across the road, the helper seen through it; read 8.7 to 11.3; we pass
                 through it to the joined hands.
  Gratitude      sewn by the flare of those hands on the next fold; read 12.3 to 14.95 while the helped one
                 bows; sweeps over us on the downbeat.
  Apology        on a swag of the canopy, stitches loose; read 16.2 to 19.0; does not leave: it is pulled
                 tight and sewn again as the next (the same particles).
  Inclusiveness  made of the Apology's thread at the embrace; read 19.85 to 22.4; rushes past as we burst up
                 through the roof.
  Concession     across the cloth wall above a doorway; read 25.6 to 28.3; leaves as a thread that follows
                 the one who is let through first.
  Respect        woven, not sewn: gold weft and blue weft cross the loom's warp; read 32.8 to 35.5; unravels
                 until one thread is left.
  Encouragement  hangs above a child walking the one thread held in Mother's hand; read 40.0 to 43.0; goes
                 up as flakes when the small hand reaches hers.
  Compliment     largest, burnt out of the lifting veil by the sunrise during the half circle; read 46.5 to
                 49.2; then all nine return small across the sky and their threads become the nine lights.

THREE WOW MOMENTS
  1  0.55  The cast: from a close, back-lit view of her shoulders the veil bursts over the lens and unrolls
           across the mirror lake while we are swept 44 m back with its hem.
  2  19.4  The mending: under the canopy a person who is coming apart is embraced, her light breaks round
           the two, and every scattered particle flies home.
  3  45 to 52.5  The lifting: the half circle behind her as the sun passes behind her head; she raises her
           arms with the child's hand in hers and the whole veil leaves the lake, becomes the sky with all
           nine words in it, and the arc between her hands becomes the arch.
  And the quiet one: 37.5, a rush that ends at her hand holding the single thread a child will walk.

WHAT IS PROVISIONAL
  The section map. MED2's current cut (origin/epic-medley2 45017af) has six sections of about 6.6 s, then
  a long one from 40.2 (its breath, into a hit at 42.5) and the final chorus from 49.5 to a last hit at 58.1
  (SECTIONS_MED2_DRAFT). Refit plan: movements 1 to 5 take the six short sections with the two pairs
  straddling a song change (the reply lands on the new song's downbeat); the hand macro sits on 40.2 and the
  child steps onto the thread on 42.5; the lifting starts on 49.5; the end card is whole by 55.5 and the
  last hit at 58.1 flares the arch.
  The names of CORE's world keys and of BODY's motions (BODY's branch is not on origin yet).
  ENGINE_NEEDS below lists what this film needs beyond the brief, most important first.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.dirname(HERE)                      # this file is engine/songs/
ROOT = os.path.dirname(ENGINE)                      # repository root
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from track import Track   # noqa: E402
import theme   # noqa: E402

SONG_ID = os.environ.get("SONG", os.path.splitext(os.path.basename(__file__))[0])
FEATURES = os.environ.get("FEATURES", os.path.join(ROOT, "work", SONG_ID, "features.npz"))
AUDIO_FILE = "audio/promo/concert-medley.mp3"       # the new medley (branch epic-medley2)

FPS = 30
W, H = 1920, 1080
ASPECT = W / H
TOTAL = 60.0
SONG_END = 60.0
MUSIC_END = 59.6
NFRAMES = int(round(TOTAL * FPS))

# ---------------------------------------------------------------------------------------------- the sections
# Section starts in seconds. Provisional (TEN-FILMS.md) until MED2's map is final; every time below hangs
# off S, so swapping the map moves the whole film with it.
SECTIONS = (0.0, 7.5, 15.0, 22.5, 30.0, 37.5, 45.0, 52.5)
SECTIONS_MED2_DRAFT = (0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 49.47)   # breath 40.2, hit 42.5, last 58.1
SECTION_NAMES = ("The Cast", "The Road", "The Canopy", "The River and the Narrows", "The Loom", "The Thread",
                 "The Lifting", "The Concert")
S = SECTIONS

CAST = S[0] + 0.55          # the first hit: she opens her arms, the veil leaves her shoulders
MEND = S[2] + 4.40          # the embrace under the canopy: the scattered particles fly home
BREATH = (S[5], S[5] + 2.5)   # the music's one short breath: her hand on the single thread
TOUCH = S[5] + 6.80         # the child's hand reaches hers
SUNBREAK = S[6]             # the biggest passage begins
ECLIPSE = S[6] + 2.60       # the sun passes behind her head, halfway round the half circle
LIFT = S[6] + 4.20          # she raises both arms; the veil leaves the lake
OVERHEAD = S[6] + 5.60      # the veil passes over our heads into the sky
ARCH_UP = S[7] - 0.10       # the arc between her hands stands as the arch; its nine lights wake to S[7] + 0.7
FORM_DUR = 2.4              # the end card's title takes this long to form (plus 0.75 s, as the engine does)
TITLE_HIT = S[7] + 2.55     # 55.05: the title is whole; held to the end (4.95 s)
T_FORM = TITLE_HIT - FORM_DUR - 0.75   # 51.9: the last fold of the veil starts across the sky
TAG_T0, TAG_T1 = S[7] + 1.4, TITLE_HIT - 0.05   # the three navy lines rise
FINAL_HIT = TITLE_HIT       # provisional: the medley's last accent (58.1 in MED2's draft): arch flare, sky ripple


def lin(hexs):
    """A display hex colour as linear light (the same curve as the other song files and p3d.api.lin)."""
    h = hexs.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float64) ** 2.2


# ------------------------------------------------------------------------------------- Heavenly Mother's path
# She walks along the line x = 0 toward -z (toward the arch at the origin and the light beyond it, azimuth
# 180), from z = 62 at a serene 1.05 m/s. She stops for the breath (the hand, the child) and stands through
# the lifting, then walks on under the arch into the sun. A pure function of t.
MOTHER_Z0 = 62.0
MOTHER_PACE = 1.05          # metres per second
MOTHER_FACING = 180.0       # azimuth she faces (p3d.at convention: 0 is +z)
MOTHER_HEIGHT = 1.70
_PACE = ((0.0, 1.0), (S[5] - 0.6, 1.0), (S[5] + 0.4, 0.0), (S[7] + 0.3, 0.0), (S[7] + 1.3, 1.0), (TOTAL, 1.0))


def _walked(t):
    """Seconds of walking done by t (the integral of the pace keys, which are joined by straight lines)."""
    t = float(min(max(t, 0.0), TOTAL))
    s = 0.0
    for (ta, va), (tb, vb) in zip(_PACE[:-1], _PACE[1:]):
        if t <= ta:
            break
        u = min(t, tb)
        vu = va + (vb - va) * (u - ta) / (tb - ta)
        s += 0.5 * (va + vu) * (u - ta)
    return s


def mother_pos(t):
    """Where Heavenly Mother's feet are at t (metres)."""
    return np.array([0.0, 0.0, MOTHER_Z0 - MOTHER_PACE * _walked(t)])


# ---------------------------------------------------------------------------------------------- the stations
# A station is a fixed place on the lake where the veil gathers two people and a word. Each is set a number
# of metres behind where Mother is at its reference time; she walks on, so she is a little farther ahead at
# the end of a station than at its start. Offsets from a station are in world axes: +x is screen right for a
# camera that looks toward her, +z is away from her (toward the veil's tail), -z is toward her.
_STATION_SPEC = dict(
    st_greet=(S[0] + 4.2, 13.0),     # the two who greet stand here; the fold with the words is 3 m nearer her
    st_help=(S[1] + 1.2, 9.2),       # the kneeling one and the helper
    st_mend=(S[2] + 1.2, 13.0),      # the one who sits, under the canopy
    st_gate=(S[3] + 3.1, 9.5),       # the doorway in the cloth wall at the narrows
    st_loom=(S[4] + 2.8, 11.0),      # midway between the two who talk
)
STATIONS = {k: np.array([0.0, 0.0, mother_pos(tr)[2] + d]) for k, (tr, d) in _STATION_SPEC.items()}


def anchor(name, t):
    """World position of an anchor at t: "W" the world origin, "M" Mother's feet, or a station."""
    if name == "W":
        return np.zeros(3)
    if name == "M":
        return mother_pos(t)
    return STATIONS[name]


def place(spec, t):
    """A (anchor, (x, y, z)) pair as a world point at t."""
    return anchor(spec[0], t) + np.asarray(spec[1], np.float64)


# ------------------------------------------------------------------------------------------------ the camera
# Keyframes: where the camera is (`at`), what it looks at (`look`), each as (anchor, offset in metres), the
# vertical field of view in degrees, roll in degrees, what is in focus, the lens opening in metres (p3d:
# 0.05 is a strong blur) and motion blur 0..1. `cut` marks a relocation that is hidden in a pass through
# cloth (a wash of bokeh): the camera does not travel between that key and the one before it.
# Between keys the path is a smooth curve that does not overshoot and does not stop at a key (monotone
# cubic, see _pchip); CORE's fly() and orbit() replace it in phase B.
REAR_LIMIT = 60.0           # degrees off "straight behind her" the camera may reach
MIN_SPEED = 0.10            # metres per second: the camera is never still


def _k(t, at, look, fov, roll=0.0, focus=None, ap=0.03, blur=0.0, cut=False, note=""):
    return dict(t=float(t), at=at, look=look, fov=float(fov), roll=float(roll), focus=focus, ap=float(ap),
                blur=float(blur), cut=bool(cut), note=note)


def _orbit(t0, t1, a0, a1, radius, h0, h1, look, fov, n=5, note="", **kw):
    """Keys on a circle about Mother: a is the angle off straight behind her (degrees, negative: her left)."""
    out = []
    for i in range(n):
        u = i / (n - 1.0)
        deg = a0 + (a1 - a0) * u
        a = np.radians(deg)
        out.append(_k(t0 + (t1 - t0) * u, ("M", (radius * np.sin(a), h0 + (h1 - h0) * u, radius * np.cos(a))),
                      look, fov, note=note if i == 0 else f"... the half circle, {deg:+.0f} degrees", **kw))
    return out


_HAND = ("M", (-0.33, 0.80, 0.05))            # her left hand, held low and a little back
_HANDS = ("M", (-0.40, 0.84, 0.14))           # where the child's hand meets it
_PAIR = ("M", (-0.20, 1.75, 0.0))             # between her head and the child's, at the height of her crown

CAMERA_KEYS = [
    # 1 THE CAST
    _k(S[0] + 0.00, ("M", (0.45, 1.55, 2.4)), ("M", (0.0, 1.60, 0.0)), 38, focus=("mother",), ap=0.05,
       note="frame one: close behind her, half body, veiled, the horizon star behind her head, rays round her"),
    _k(CAST, ("M", (0.40, 1.56, 2.0)), ("M", (0.0, 1.62, 0.0)), 38, focus=("mother",), ap=0.05,
       note="THE CAST: arms open low, the veil leaves her shoulders toward the lens"),
    _k(S[0] + 1.50, ("M", (-1.2, 1.0, 16.0)), ("M", (0.0, 1.4, 0.0)), 56, roll=-6, focus=("mother",), blur=1.0,
       note="swept backward with the hem, low over the water"),
    _k(S[0] + 2.60, ("M", (-3.0, 7.0, 46.0)), ("M", (0.0, 1.0, 0.0)), 62, focus=("mother",), blur=0.4,
       note="wide: a small bright figure at the head of an immense veil, mirrored"),
    _k(S[0] + 3.60, ("st_greet", (0.0, 1.55, 4.6)), ("M", (0.0, 2.0, 0.0)), 36, focus=("word", "Greeting"),
       blur=0.6, note="swoop down along the veil to the two who gather on its banks"),
    _k(S[0] + 4.20, ("st_greet", (0.0, 1.50, 4.0)), ("M", (0.0, 2.0, 0.0)), 34, focus=("word", "Greeting"),
       ap=0.035, note="READ Greeting on the curled hem; the walkers are soft profiles coming in from the edges"),
    _k(S[0] + 6.80, ("st_greet", (0.15, 1.42, 3.3)), ("M", (0.0, 2.0, 0.0)), 34, focus=("word", "Greeting"),
       ap=0.035, note="end of reading; focus falls to the walkers, she is the small bright figure between them"),
    _k(S[0] + 7.05, ("st_greet", (0.2, 1.50, 2.8)), ("M", (0.0, 1.8, 0.0)), 35, focus=("person", "greet_a"),
       ap=0.05, note="they clasp hands (contact)"),
    _k(S[0] + 7.46, ("st_greet", (0.3, 2.30, 0.6)), ("M", (0.0, 1.9, 0.0)), 42, focus=("person", "greet_a"),
       note="rise over the joined hands; the fold sweeps over the lens"),
    # 2 THE ROAD
    _k(S[1] + 0.00, ("M", (2.5, 0.45, 62.0)), ("M", (0.0, 1.2, 0.0)), 60, roll=14, focus=("mother",), blur=1.0,
       cut=True, note="NEW: speed. Far back in the mist, half a metre above the veil road"),
    _k(S[1] + 0.45, ("M", (-2.8, 0.50, 42.0)), ("M", (0.0, 1.3, 0.0)), 58, roll=-16, focus=("mother",), blur=1.0,
       note="banking through the bends, the cloth streaming against us"),
    _k(S[1] + 0.90, ("st_help", (1.2, 0.90, 12.4)), ("M", (0.0, 1.7, 0.0)), 46, roll=6,
       focus=("word", "Consideration"), blur=0.6, note="a sheer curtain closes the road ahead"),
    _k(S[1] + 1.20, ("st_help", (0.6, 1.40, 8.3)), ("M", (0.0, 2.0, 0.0)), 36, focus=("word", "Consideration"),
       ap=0.035, note="READ Consideration on the curtain; the helper and the kneeling one seen through it"),
    _k(S[1] + 3.80, ("st_help", (-0.3, 1.35, 7.5)), ("M", (0.0, 1.9, 0.0)), 36, focus=("word", "Consideration"),
       ap=0.035, note="end of reading; through the curtain"),
    _k(S[1] + 4.22, ("st_help", (-0.5, 1.20, 1.5)), ("st_help", (0.95, 1.0, 0.05)), 34,
       focus=("point", ("st_help", (0.95, 1.0, 0.05))), ap=0.05, note="two hands meet and flare (contact)"),
    _k(S[1] + 4.80, ("st_help", (-1.0, 1.30, 3.4)), ("st_help", (0.0, 2.6, -4.7)), 36,
       focus=("word", "Gratitude"), ap=0.035, note="READ Gratitude on the next fold; the helped one bows"),
    _k(S[1] + 7.46, ("st_help", (-0.6, 1.60, 3.0)), ("st_help", (0.0, 2.7, -4.7)), 36,
       focus=("word", "Gratitude"), ap=0.035, note="slow crane up; the fold comes at us on the downbeat"),
    # 3 THE CANOPY
    _k(S[2] + 0.00, ("st_mend", (-2.2, 0.9, 6.0)), ("st_mend", (0.4, 1.75, -2.2)), 44,
       focus=("word", "Apology"), cut=True,
       note="NEW: under the veil. A roof of amber cloth, her light in its mouth"),
    _k(S[2] + 1.20, ("st_mend", (-1.6, 1.0, 4.4)), ("st_mend", (0.4, 1.8, -2.2)), 40, focus=("word", "Apology"),
       ap=0.035, note="READ Apology on a swag of the roof; one sits coming apart, one kneels beside"),
    _k(S[2] + 4.00, ("st_mend", (1.0, 1.1, 4.1)), ("st_mend", (0.4, 1.8, -2.2)), 40, focus=("word", "Apology"),
       ap=0.035, note="end of the low arc: the pair is now exactly in front of her light"),
    _k(MEND + 0.05, ("st_mend", (1.1, 1.15, 2.3)), ("st_mend", (0.9, 1.15, 0.0)), 36,
       focus=("point", ("st_mend", (0.9, 1.15, 0.0))), ap=0.05,
       note="THE MENDING: the embrace (contact); rays break round the two; the particles fly home"),
    _k(S[2] + 4.85, ("st_mend", (0.5, 1.6, 4.6)), ("st_mend", (0.4, 1.9, -2.2)), 40,
       focus=("word", "Inclusiveness"), ap=0.035, note="READ Inclusiveness, sewn again from the Apology's thread"),
    _k(S[2] + 7.40, ("st_mend", (-0.2, 1.9, 4.2)), ("st_mend", (0.4, 2.1, -2.2)), 40,
       focus=("word", "Inclusiveness"), ap=0.035, note="draw back and rise a little: the embrace low, she beyond it"),
    # 4 THE RIVER AND THE NARROWS (no cut: we really do burst up through the roof)
    _k(S[3] + 0.30, ("M", (-5.0, 10.0, 27.0)), ("M", (0.0, 1.0, 0.0)), 54, focus=("mother",), blur=1.0,
       note="NEW: height. Up through the cloth"),
    _k(S[3] + 1.50, ("M", (-14.0, 38.0, 64.0)), ("M", (0.0, 0.0, -20.0)), 62, roll=-8, focus=("mother",),
       note="the veil is a river of light with braided arms across the whole lake; she is its head"),
    _k(S[3] + 2.10, ("M", (-6.0, 28.0, 46.0)), ("st_gate", (0.0, 1.5, 0.0)), 54, roll=-28,
       focus=("word", "Concession"), blur=1.0, note="nose over and dive, rolling"),
    _k(S[3] + 2.90, ("st_gate", (1.0, 1.9, 8.0)), ("M", (0.0, 2.3, 0.0)), 38, focus=("word", "Concession"),
       blur=0.5, note="pull out at the narrows: a wall of cloth with a doorway, her light through it"),
    _k(S[3] + 3.10, ("st_gate", (0.9, 1.85, 7.7)), ("M", (0.0, 2.3, 0.0)), 38, focus=("word", "Concession"),
       ap=0.035, note="READ Concession above the door; one steps back and opens a palm"),
    _k(S[3] + 5.80, ("st_gate", (-0.4, 1.6, 6.9)), ("M", (0.0, 2.4, 0.0)), 38, focus=("word", "Concession"),
       ap=0.035, note="end of reading"),
    _k(S[3] + 6.80, ("st_gate", (-0.2, 1.4, 3.2)), ("M", (0.0, 1.8, 0.0)), 38, focus=("person", "gate_first"),
       ap=0.05, note="the other walks through into the light; then the one who gave way"),
    _k(S[3] + 7.47, ("st_gate", (0.0, 1.45, -0.4)), ("M", (0.0, 1.7, 0.0)), 44, focus=("mother",),
       note="we follow through the door"),
    # 5 THE LOOM (roll 360 is level again; the keys after the barrel roll keep 360 so nothing unwinds)
    _k(S[4] + 0.00, ("M", (0.6, 2.4, 55.0)), ("M", (0.0, 1.6, 0.0)), 60, roll=0, focus=("mother",), blur=1.0,
       cut=True, note="NEW: the veil unwoven into taut threads; the camera is the shuttle"),
    _k(S[4] + 1.20, ("M", (-0.8, 2.8, 34.0)), ("M", (0.0, 1.7, 0.0)), 54, roll=180, focus=("mother",), blur=1.0,
       note="through the warp, upside down for an instant"),
    _k(S[4] + 2.40, ("st_loom", (0.8, 2.2, 6.6)), ("st_loom", (0.0, 2.0, 0.0)), 42, roll=360,
       focus=("word", "Respect"), blur=0.4, note="level; two people in profile, she between them far ahead"),
    _k(S[4] + 2.80, ("st_loom", (0.7, 1.9, 6.4)), ("st_loom", (0.0, 2.0, 0.0)), 40, roll=360,
       focus=("word", "Respect"), ap=0.035, note="READ Respect, woven of a gold and a blue thread above them"),
    _k(S[4] + 5.50, ("st_loom", (-0.8, 1.7, 5.8)), ("st_loom", (0.0, 2.0, 0.0)), 40, roll=360,
       focus=("word", "Respect"), ap=0.035, note="end of reading"),
    _k(S[4] + 6.60, ("st_loom", (1.0, 1.35, 2.0)), ("st_loom", (1.6, 1.2, 0.1)), 32, roll=360,
       focus=("point", ("st_loom", (1.6, 1.2, 0.1))), ap=0.05,
       note="the listener cups the other's light in both hands; the loom falls silent to one thread"),
    # 6 THE THREAD (the rush along the last thread ends, on the breath, at her hand)
    _k(S[5] + 0.00, ("M", (-0.50, 0.80, 0.62)), _HAND, 26, roll=360, focus=("point", _HAND), ap=0.06,
       note="NEW: stillness. Her left hand from behind, closed lightly on the one thread (macro)"),
    _k(S[5] + 1.50, ("M", (-0.62, 0.84, 1.40)), _HAND, 26, roll=360, focus=("point", _HAND), ap=0.06,
       note="the camera only breathes; a thin line of rose on the horizon"),
    _k(S[5] + 2.00, ("M", (0.10, 1.65, 4.6)), ("M", (-0.25, 1.2, 0.0)), 30, roll=360,
       focus=("person", "child"), ap=0.05, note="back along the thread, over the head of a child stepping onto it"),
    _k(S[5] + 2.50, ("M", (0.70, 0.95, 8.4)), ("M", (-0.20, 1.75, 0.0)), 34, roll=360,
       focus=("word", "Encouragement"), ap=0.035,
       note="READ Encouragement above the child; close to us someone kneels with clasped hands"),
    _k(S[5] + 5.50, ("M", (0.45, 1.10, 8.9)), ("M", (-0.20, 1.80, 0.0)), 34, roll=360,
       focus=("word", "Encouragement"), ap=0.035, note="end of reading; we stay with the one who roots"),
    _k(TOUCH, ("M", (-0.42, 0.66, 1.15)), _HANDS, 28, roll=360, focus=("point", _HANDS), ap=0.06,
       note="the last steps with the child: a small hand reaches up into hers (contact, flare)"),
    # 7 THE LIFTING
    _k(S[6] + 0.00, ("M", (-0.60, 0.80, 1.25)), ("M", (-0.38, 0.9, 0.1)), 30, roll=360, focus=("mother",),
       note="NEW: the sun breaks the horizon straight ahead of her; the veil floods back in rose gold"),
] + _orbit(S[6] + 0.8, S[6] + 4.4, -55.0, 55.0, 3.66, 1.3, 2.2, _PAIR, 46, roll=360, focus=("mother",), ap=0.04,
           note="the half circle behind her and the child; READ Compliment above them (46.5 to 49.2); "
                "halfway the sun passes behind her head") + [
    _k(S[6] + 5.80, ("M", (1.6, 2.6, 6.5)), ("M", (0.0, 2.6, -6.0)), 50, roll=360, focus=("mother",),
       note="arms raised; the veil streams over our heads into the sky; all nine words small across it"),
    # 8 THE CONCERT
    _k(S[7] + 0.00, ("M", (0.0, 4.6, 12.5)), ("W", (0.0, 7.0, 0.0)), 54, roll=360, focus=("mother",),
       note="NEW: the arch of nine lights stands over the lake; the title's fold crosses the sky"),
    _k(S[7] + 3.50, ("M", (0.0, 6.6, 17.0)), ("W", (0.0, 7.5, 0.0)), 52, roll=360, focus=("mother",),
       note="end card whole; she and the child walk on under the arch into the sun"),
    _k(TOTAL, ("M", (0.0, 8.6, 21.0)), ("W", (0.0, 8.0, 0.0)), 50, roll=360, focus=("mother",),
       note="still craning up and back on the last frame; no fade"),
]

# continuous runs of keys (a cut starts a new run)
_RUNS = []
for _key in CAMERA_KEYS:
    if _key["cut"] or not _RUNS:
        _RUNS.append([])
    _RUNS[-1].append(_key)


def _pchip(ts, ys, t):
    """Monotone cubic through (ts, ys) at t: smooth, never overshoots a key, keeps moving through a key when
    the motion goes on in the same direction. ys is (n, d)."""
    ts, ys = np.asarray(ts, np.float64), np.asarray(ys, np.float64)
    n = len(ts)
    if n == 1:
        return ys[0]
    h = np.diff(ts)
    d = np.diff(ys, axis=0) / h[:, None]
    m = np.zeros_like(ys)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        w1, w2 = 2.0 * h[i] + h[i - 1], h[i] + 2.0 * h[i - 1]
        same = d[i - 1] * d[i] > 0.0
        with np.errstate(divide="ignore", invalid="ignore"):
            m[i] = np.where(same, (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]), 0.0)
    i = int(np.clip(np.searchsorted(ts, t, side="right") - 1, 0, n - 2))
    u = min(max((t - ts[i]) / h[i], 0.0), 1.0)
    h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
    h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]


def _focus_point(spec, t):
    """The world point a focus setting names, or None for a camera-locked word (its distance is fixed)."""
    kind = spec[0]
    if kind == "mother":
        return mother_pos(t) + np.array([0.0, 1.45, 0.0])
    if kind == "point":
        return place(spec[1], t)
    if kind == "person":
        return person_pos(spec[1], t) + np.array([0.0, 1.2, 0.0])
    if kind == "word":
        w = WORD_PLACES[spec[1]]
        return None if w.get("lock") else place(w["at"], t)
    raise ValueError(f"unknown focus {spec!r}")


def camera_at(t):
    """The camera at t: dict(pos, target, fov, roll, focus, aperture, blur), metres and degrees, world axes."""
    t = float(min(max(t, 0.0), TOTAL))
    run = _RUNS[0]
    for r in _RUNS:
        if r[0]["t"] <= t:
            run = r
    ts = [k["t"] for k in run]
    pos = _pchip(ts, [place(k["at"], t) for k in run], t)
    target = _pchip(ts, [place(k["look"], t) for k in run], t)
    num = _pchip(ts, [[k["fov"], k["roll"], k["ap"], k["blur"]] for k in run], t)
    foc = []
    for k in run:
        p = _focus_point(k["focus"], t) if k["focus"] else place(k["look"], t)
        foc.append([LOCK_DIST if p is None else float(np.linalg.norm(p - place(k["at"], t)))])
    roll = (float(num[1]) + 180.0) % 360.0 - 180.0
    return dict(pos=pos, target=target, fov=float(num[0]), roll=roll, focus=float(_pchip(ts, foc, t)[0]),
                aperture=float(num[2]), blur=float(num[3]))


def camera_world_keys():
    """The keyframes as plain world coordinates at their own times: (t, position, target, fov, roll, note)."""
    return [(k["t"], place(k["at"], k["t"]), place(k["look"], k["t"]), k["fov"], k["roll"], k["note"])
            for k in CAMERA_KEYS]


def frame_width(dist, fov):
    """Width in metres of the picture at a distance in front of the camera (vertical field of view fov)."""
    return 2.0 * dist * np.tan(np.radians(fov) / 2.0) * ASPECT


def _basis(cam):
    f = cam["target"] - cam["pos"]
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0.0, 1.0, 0.0])
    r = r / np.linalg.norm(r)
    return r, np.cross(r, f), f


def project(cam, p):
    """A world point on screen: (x, y) in 0..1 with y up, and its depth in metres (roll ignored)."""
    r, u, f = _basis(cam)
    d = np.asarray(p, np.float64) - cam["pos"]
    z = float(d @ f)
    k = 1.0 / np.tan(np.radians(cam["fov"]) / 2.0)
    zz = z if abs(z) > 1e-9 else 1e-9
    return 0.5 + 0.5 * float(d @ r) * k / (ASPECT * zz), 0.5 + 0.5 * float(d @ u) * k / zz, z


# -------------------------------------------------------------------------------------- the nine expressions
# Exact campaign wording, labels and line breaks: project-docs/DESIGN-SYSTEM.md section 5 and the PHRASES of
# engine/songs/epic_concert.py (the same text is p3d.words.EXPRESSIONS on branch engine-p3d-words). In
# campaign order, which is also the order of the arch's nine lights. The film itself names an expression by
# its label (`expr=`) and never retypes it; this table is here for the check and for the old 2D keys.
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
LABELS = [n[0] for n in NINE]
ORDER_IN_FILM = ["Greeting", "Consideration", "Gratitude", "Apology", "Inclusiveness", "Concession", "Respect",
                 "Encouragement", "Compliment"]

LOCK_DIST = 5.2             # metres in front of the lens for a word that turns with the camera
LOCK_ELEV = 12.0            # ... and degrees above the middle of the picture

# Where each expression stands and when. `at`: the centre of the phrase block (anchor, offset in metres).
# `frac`: the share of the picture's width its widest line takes when its reading moment starts (its width in
# metres follows from the camera, see word_width). Times are (t_in, t_read0, t_read1, t_out), the four times
# of p3d.words. `fold`: the part of the veil that carries it. `arrive` and `leave` name the styles helper
# WORDS has today; `wish` is what this film asks WORDS for instead (ENGINE_NEEDS 4).
WORD_PLACES = dict(
    Greeting=dict(
        at=("st_greet", (0.0, 2.45, -3.0)), frac=0.50, tilt=-6.0,
        times=(S[0] + 2.6, S[0] + 4.2, S[0] + 6.8, S[0] + 7.6), fold="the hem that curls up like a page",
        arrive="morph", source="veil", fallback="touch", leave="bokeh",
        wish=("stitch", "bokeh"), acted_by=("greet_a", "greet_b")),
    Consideration=dict(
        at=("st_help", (0.0, 2.15, 2.3)), frac=0.60, tilt=-6.0,
        times=(S[1] + 0.2, S[1] + 1.2, S[1] + 3.8, S[1] + 4.4), fold="a sheer curtain across the road",
        arrive="morph", source="veil", fallback="palm", leave="bokeh",
        wish=("stitch", "bokeh"), acted_by=("helper", "weary")),
    Gratitude=dict(
        at=("st_help", (0.0, 3.3, -4.7)), frac=0.80, tilt=-12.0,
        times=(S[1] + 4.2, S[1] + 4.8, S[1] + 7.45, S[2] + 0.4), fold="the next fold, lit by the flare of two hands",
        arrive="touch", source=("point", ("st_help", (0.95, 1.0, 0.05))), fallback="touch", leave="bokeh",
        wish=("stitch", "bokeh"), acted_by=("weary", "helper")),
    Apology=dict(
        at=("st_mend", (0.4, 2.8, -2.2)), frac=0.74, tilt=-12.0,
        times=(S[2] + 0.3, S[2] + 1.2, S[2] + 4.0, S[2] + 4.85), fold="a hanging swag of the canopy, stitches loose",
        arrive="morph", source="veil", fallback="lake", leave="morph", to="Inclusiveness",
        wish=("stitch", "morph"), acted_by=("sorry", "hurt")),
    Inclusiveness=dict(
        at=("st_mend", (0.4, 2.8, -2.2)), frac=0.66, tilt=-8.0,
        times=(S[2] + 4.0, S[2] + 4.85, S[2] + 7.4, S[3] + 0.35), fold="the same swag, sewn again",
        arrive="morph", source="Apology", fallback="morph", leave="bokeh",
        wish=("morph", "bokeh"), acted_by=("hurt", "sorry")),
    Concession=dict(
        at=("st_gate", (0.0, 2.9, 0.0)), frac=0.58, tilt=-8.0,
        times=(S[3] + 1.6, S[3] + 3.1, S[3] + 5.8, S[3] + 7.2), fold="the cloth wall above the doorway",
        arrive="morph", source="veil", fallback="flock", leave="give", to=("person", "gate_first"),
        wish=("stitch", "unravel"), acted_by=("gate_yield", "gate_first")),
    Respect=dict(
        at=("st_loom", (0.0, 2.9, 0.0)), frac=0.60, tilt=-8.0,
        times=(S[4] + 1.3, S[4] + 2.8, S[4] + 5.5, S[4] + 6.9), fold="fresh cloth woven of a gold and a blue weft",
        arrive="palm", source=("person", "speaker"), fallback="stars", leave="give", to="veil",
        wish=("weave", "unravel"), acted_by=("listener", "speaker")),
    Encouragement=dict(
        at=("M", (0.1, 2.6, 2.0)), frac=0.72, tilt=-12.0,
        times=(S[5] + 1.0, S[5] + 2.5, S[5] + 5.5, S[5] + 7.0), fold="a sheer banner in still air over the thread",
        arrive="morph", source="veil", fallback="shaft", leave="rise",
        wish=("stitch", "rise"), acted_by=("rooter", "child")),
    Compliment=dict(
        lock=True, frac=0.58, tilt=0.0,
        times=(S[6] + 0.1, S[6] + 1.5, S[6] + 4.2, S[6] + 5.0), fold="the veil lifting above her, turning with us",
        arrive="rays", source=None, fallback="rays", leave="rise",
        wish=("rays", "rise"), acted_by=("everyone", "child")),
)
# At the lifting all nine return small across the sky for one breath (not a reading moment), then each
# streams into its light of the arch (p3d.words leave "arch").
REPRISE = dict(t_in=S[6] + 4.8, t_whole=S[6] + 5.6, t_leave=S[6] + 6.4, t_out=ARCH_UP + 0.8, frac=0.20,
               arrive="rays", leave="arch", rows=((0, 1, 2), (3, 4, 5), (6, 7, 8)))
# When each light wakes (campaign order): a pearl on the hem of her veil while the film runs (a soft warm
# white point on her back that the viewer may count: 1, 3, 5, 6, 7, 8, 9), a light of the arch at the end.
PEARL_LIT = {lab: WORD_PLACES[lab]["times"][3] + 0.3 for lab in LABELS}
ARCH_LIT = [ARCH_UP + 0.09 * i for i in range(9)]


def word_pos(label, t):
    """Centre of an expression's phrase block at t (world metres)."""
    w = WORD_PLACES[label]
    if w.get("lock"):
        cam = camera_at(t)
        _, u, f = _basis(cam)
        e = np.radians(LOCK_ELEV)
        return cam["pos"] + LOCK_DIST * (f * np.cos(e) + u * np.sin(e))
    return place(w["at"], t)


def word_width(label):
    """Width in metres of an expression's widest line: `frac` of the picture when its reading starts."""
    w = WORD_PLACES[label]
    t0 = w["times"][1]
    cam = camera_at(t0)
    f = cam["target"] - cam["pos"]
    f = f / np.linalg.norm(f)
    depth = float((word_pos(label, t0) - cam["pos"]) @ f)
    return w["frac"] * frame_width(depth, cam["fov"])


def word_specs(veil=None, people=None):
    """The nine words as settings for p3d.words.Words. With the veil and the people of phase B the words are
    made of the veil's own particles and leave into people; without them each uses a style WORDS has today."""
    people = people or {}
    out = []
    for lab in ORDER_IN_FILM:
        w = WORD_PLACES[lab]
        t_in, t0, t1, t_out = w["times"]
        arrive, source = w["arrive"], w["source"]
        if source == "veil":
            arrive, source = ("morph", veil.fold(lab)) if veil is not None else (w["fallback"], None)
        elif isinstance(source, tuple) and source[0] == "point":
            source = (lambda t, s=source[1]: place(s, t))
        elif isinstance(source, tuple) and source[0] == "person":
            source = people.get(source[1])
            arrive = arrive if source is not None else w["fallback"]
        leave, to = w["leave"], w.get("to")
        if to == "veil":
            leave, to = ("give", veil) if veil is not None else ("wind", None)
        elif isinstance(to, tuple) and to[0] == "person":
            to = people.get(to[1])
            leave = leave if to is not None else "wind"
        spec = dict(expr=lab, pos=(lambda t, k=lab: word_pos(k, t)), width=word_width(lab),
                    face="screen" if w.get("lock") else "camera", tilt=w["tilt"], t_in=t_in, t_read0=t0,
                    t_read1=t1, t_out=t_out, arrive=arrive, leave=leave)
        if source is not None:
            spec["source"] = source
        if to is not None:
            spec["to"] = to
        out.append(spec)
    return out


# warm white and gold only: the letters keep a quarter of the gold, the halo is gold (p3d.words common keys)
WORD_LOOK = dict(color="#ffd27a", glow="#ffcf7a", tint=0.25, sharp=1.0)

# ------------------------------------------------------------------------------------------------- palettes
# Display hex. Sky: (top, middle, horizon, colour of the light on the horizon). One palette per section; the
# sky changes on every song change, from deep blue through rose to the campaign day.
PAL = {
    "night":  ("#03061c", "#0a1546", "#1d2c6e", "#ffd9a0"),   # 1 night water, Milky Way
    "mist":   ("#050a2a", "#11205a", "#33488f", "#ffe0b0"),   # 2 a bank of blue silver mist
    "canopy": ("#07082a", "#1a1850", "#3a2c6a", "#ffc880"),   # 3 violet outside, amber under the cloth
    "high":   ("#07103a", "#16307a", "#6a5a9e", "#ffd0a0"),   # 4 clear air, the first dusty line of rose
    "loom":   ("#0a1648", "#1f3a8c", "#9a6aa8", "#ffd6a8"),   # 5 royal blue, the rose line wider
    "hush":   ("#0e1a4e", "#2a3f8a", "#c0809c", "#ffe2c0"),   # 6 the breath: pearl blue, a thin line of rose
    "dawn":   ("#1c3f96", "#7f8fd8", "#f2a0b4", "#ffe6c0"),   # 7 sunbreak: blue above rose and gold
    "rose":   ("#5b8fd8", "#f4b6c4", "#ffd9b8", "#fff0d8"),   # 7 the veil is the sky
    "day":    ("#9cc8ec", "#fbe3de", "#fff4e8", "#ffffff"),   # 8 the campaign day with a breath of rose
}
SKY_KEYS = [(0.0, "night"), (S[1] - 0.2, "night"), (S[1] + 0.3, "mist"), (S[2] - 0.2, "mist"),
            (S[2] + 0.3, "canopy"), (S[3] - 0.1, "canopy"), (S[3] + 0.8, "high"), (S[4], "high"),
            (S[4] + 0.8, "loom"), (S[5] - 0.5, "loom"), (S[5] + 0.6, "hush"), (S[6] - 0.2, "hush"),
            (S[6] + 0.6, "dawn"), (LIFT, "dawn"), (S[6] + 6.4, "rose"), (S[7] + 1.2, "day"), (TOTAL, "day")]
SKY_TOP, SKY_MID, SKY_HOR, SKY_LIGHT = (Track([(t, lin(PAL[p][i])) for t, p in SKY_KEYS]) for i in range(4))

GOLD, WHITE_GOLD, AMBER = "#ffd27a", "#fff3da", "#ffb860"
COOL = "#a9c8ff"            # the one cool colour: "the other person", the blue weft, the child
ROSE, ROSE_WHITE = "#ffc2cf", "#ffe9e4"
# the veil: (core, edge, thread lines) per section
VEIL_COLORS = {
    0: (WHITE_GOLD, "#ffcf7a", "#ffe6b8"), 1: ("#fff6e4", "#ffd88a", "#dfe6ff"), 2: ("#ffe2b0", AMBER, "#ffd9a0"),
    3: (WHITE_GOLD, GOLD, "#ffe6b8"), 4: ("#ffe9c0", "#ffc45e", "#86b8ff"), 5: ("#fff4dc", "#ffe2b0", "#fff4dc"),
    6: (ROSE_WHITE, ROSE, "#fff0d0"), 7: ("#ffffff", ROSE_WHITE, "#fff6ee"),
}
MOTHER_COLORS = dict(body="#ffe2a8", rim="#fff6e0", veil=WHITE_GOLD, hand="#ffdf9e")

# ---------------------------------------------------------------------------------------------- the world
# For CORE's `world` key (names to be matched to its HOWTO section V when it lands). The one light of the
# film stands on the horizon straight ahead of her (azimuth 180): a warm star all night, the sun from the
# sunbreak. Because the camera is behind her, she is back-lit in every shot and the light is the place the
# whole veil runs to.
WORLD = dict(
    light=dict(azimuth=180.0, color=SKY_LIGHT,
               elevation=Track([(0.0, -0.4), (S[6] - 0.3, -0.3), (S[6] + 0.2, 0.5), (LIFT, 0.7), (S[7], 3.5),
                                (TOTAL, 6.0)]),          # degrees: on the horizon, crowning her head at the eclipse
               size=Track([(0.0, 0.25), (S[6] - 0.3, 0.3), (S[6] + 0.3, 1.0), (TOTAL, 1.3)]),   # star, then sun
               strength=Track([(0.0, 0.8), (S[5], 0.6), (S[6] - 0.2, 0.7), (S[6] + 0.3, 1.6), (S[7] + 2.5, 1.2),
                               (TOTAL, 1.1)])),
    # rays from that light, eclipsed by whatever stands in front of it (her head; the embracing pair at MEND)
    rays=Track([(0.0, 0.9), (CAST, 1.0), (S[0] + 2.6, 0.5), (S[1], 0.35), (S[2] + 0.3, 0.55), (MEND, 0.9),
                (S[3], 0.3), (S[4], 0.35), (S[5], 0.15), (S[6] - 0.2, 0.2), (S[6] + 0.3, 1.0), (ECLIPSE, 1.2),
                (LIFT, 0.9), (S[7] + 2.5, 0.35), (TOTAL, 0.3)]),
    shafts=Track([(0.0, 0.0), (S[2] - 0.1, 0.0), (S[2] + 0.4, 0.8), (S[3] - 0.1, 0.8), (S[3] + 0.3, 0.0),
                  (TOTAL, 0.0)]),                        # light through the weave of the canopy
    stars=Track([(0.0, 1.0), (S[3], 0.9), (S[4], 0.7), (S[5], 0.55), (S[6], 0.35), (S[6] + 5.0, 0.05),
                 (S[7], 0.0), (TOTAL, 0.0)]),
    milky_way=Track([(0.0, 0.9), (S[3] + 1.5, 1.0), (S[4], 0.6), (S[5], 0.3), (S[6], 0.1), (S[6] + 3.0, 0.0),
                     (TOTAL, 0.0)]),
    mist=Track([(0.0, 0.10), (S[1] - 0.3, 0.12), (S[1] + 0.2, 0.75), (S[2] - 0.3, 0.6), (S[2] + 0.3, 0.2),
                (S[3], 0.1), (S[4], 0.15), (S[5], 0.25), (S[6], 0.3), (S[7], 0.15), (TOTAL, 0.1)]),
    lake=dict(mirror=Track([(0.0, 1.0), (S[5], 1.0), (S[7], 0.8), (TOTAL, 0.7)]),
              ripple=Track([(0.0, 0.35), (S[5] - 0.5, 0.35), (S[5] + 0.5, 0.02), (S[6] - 0.2, 0.02),
                            (S[6] + 0.5, 0.30), (TOTAL, 0.25)])),     # glass for the breath
    hills=Track([(0.0, 0.3), (S[3], 0.3), (S[3] + 1.5, 0.8), (S[4], 0.6), (S[6], 0.8), (TOTAL, 0.6)]),
    motes=Track([(0.0, 0.3), (S[2] + 0.3, 0.6), (S[3], 0.2), (S[5], 0.1), (S[6], 0.4), (TOTAL, 0.2)]),
    exposure=Track([(0.0, 1.0), (FINAL_HIT - 0.1, 1.0), (FINAL_HIT + 0.15, 1.22), (FINAL_HIT + 0.9, 1.0),
                    (TOTAL, 1.0)]),
    # the arch: hidden until the arc between her raised hands rises into it; then its lights wake left to
    # right, each over 5 frames (no one-frame pops), and flare together on the last hit
    arch=dict(visible_from=ARCH_UP, lit=ARCH_LIT, attack=5.0 / FPS, flare=FINAL_HIT),
    sky=SKY_KEYS, palettes=PAL,
)

# ------------------------------------------------------------------------------------------------- the veil
# One point set, built in phase B in this file (pure numpy, a function of t): a sheet of points on a centre
# line that starts at her crown and shoulders and runs back behind her, with warp threads as "line" batches.
# s is metres along it from her, v is across it (-1..1). Points flow along s away from her (a current), so
# the cloth streams against a camera that flies toward her. Folds are travelling waves; their height follows
# the music's loudness. Each section gives the same cloth another shape (`mode`).
VEIL = dict(
    length=420.0, points=360000, threads=6000, flow=14.0,          # metres, counts, metres per second
    width=((0.4, 0.9), (3.0, 2.2), (12.0, 6.0), (40.0, 14.0), (150.0, 30.0), (420.0, 80.0)),   # (s, metres)
    height=((0.0, 1.55), (1.5, 1.10), (5.0, 0.45), (12.0, 0.30)),  # (s, metres above the water)
    fold=dict(amp=(0.15, 1.4), wavelength=(2.5, 18.0), speed=6.0, audio=0.6),
    pearls=dict(count=9, on="the back hem of her head veil, across her shoulders", lit=PEARL_LIT),
    modes=[
        (S[0], "on her shoulders"), (CAST, "cast: unrolls 46 m in 2 s, the camera on its hem"),
        (S[0] + 2.6, "river"), (S[1], "road: narrow, firm, low over the water, bends to bank through"),
        (S[2], "canopy: lifts overhead from 8 m behind her to 30 m, 3 to 4.6 m high, a swag for the words"),
        (S[3], "river with five braided arms; at the narrows a wall of cloth with a doorway 1.2 m wide"),
        (S[4], "loom: unwoven into taut warp threads 0.2 to 6 m above the water, sounding with the music"),
        (S[5] - 0.9, "one thread: from her left hand back along the water, a line to walk"),
        (S[6], "river again, wider and brighter, rose gold"),
        (LIFT, "sky: peels off the lake from the tail toward her, passes overhead, spreads over the dome"),
        (ARCH_UP - 0.6, "the arc between her raised hands lifts off and grows into the arch"),
    ],
)
# every pass through cloth: (time, what passes, whether the camera is moved under cover of the wash)
PIERCES = [
    (S[0] + 7.46, "the Greeting's fold sweeps over the lens", True),
    (S[1] + 4.0, "we go through the Consideration's curtain", False),
    (S[2], "the Gratitude's fold sweeps over the lens and the veil heaves overhead", True),
    (S[3], "we burst up through the roof of the canopy", False),
    (S[3] + 7.47, "we follow the two through the doorway", True),
    (OVERHEAD, "the whole veil passes over our heads into the sky", False),
]

# ----------------------------------------------------------------------------------------------- the people
# Everyone is a lifelike body of particles (helper BODY) in garments of light, without features, gathered out
# of the veil's own points (`form`: start, seconds) and still joined to it at the hem. Positions are offsets
# in metres from the person's station (or from Mother for the last three). `facing` is an azimuth: 90 faces
# +x (screen right for a camera that looks toward her), 270 faces -x, 180 faces the way she walks.
# `motion` and `gesture` use BODY's draft names where they exist; the others are in ENGINE_NEEDS.
MOTIONS_PROMISED = {"walk", "stand", "run", "kneel", "look_up", "reach", "open_arms", "blow", "reach_hands"}
MOTIONS_IN_BODY_DRAFT = {"raise", "pray", "bow"}


def _p(pid, body, clothes, look, color, at, path, facing, motion, gesture=(), form=None, effect=(), contact=None,
       leave=None, lane=None):
    return dict(id=pid, body=body, clothes=clothes, look=look, color=color, at=at, path=path, facing=facing,
                motion=list(motion), gesture=list(gesture), form=form, effect=list(effect), contact=contact,
                leave=leave, lane=lane)


PEOPLE = [
    # 1 Greeting: two strangers cross the veil from its two banks and meet (rim-lit profiles, ref 01, 16)
    _p("greet_a", "woman", "a long coat of light", "rim", GOLD, "st_greet",
       [(S[0] + 3.4, (-3.4, 0.0, 0.3)), (S[0] + 6.6, (-0.42, 0.0, 0.0))], 90,
       [(S[0] + 3.4, "walk"), (S[0] + 6.6, "stand")],
       [(S[0] + 5.4, S[0] + 6.7, "raise"), (S[0] + 6.7, S[0] + 7.6, "reach_hands")],
       form=(S[0] + 2.7, 1.1), effect=["walk_shed"], contact=(S[0] + 6.9, "clasp hands", "greet_b"),
       leave=(S[1] - 0.05, S[1] + 0.3), lane=(-5.2, 1.9)),
    _p("greet_b", "man", "a loose tunic and trousers of light", "rim", COOL, "st_greet",
       [(S[0] + 3.4, (3.4, 0.0, -0.3)), (S[0] + 6.6, (0.42, 0.0, 0.0))], 270,
       [(S[0] + 3.4, "walk"), (S[0] + 6.6, "stand")], [(S[0] + 6.5, S[0] + 7.6, "reach_hands")],
       form=(S[0] + 2.7, 1.1), effect=["walk_shed"], contact=(S[0] + 6.9, "clasp hands", "greet_a"),
       leave=(S[1] - 0.05, S[1] + 0.3), lane=(5.2, 1.9)),
    # 2 Consideration, Gratitude: one is spent, kneeling beside a burden of dim light; one stops to help
    _p("weary", "man", "a long coat of light", "glitter", COOL, "st_help",
       [(S[1] + 0.2, (1.3, 0.0, 0.0))], 270,
       [(S[1] + 0.2, "kneel"), (S[1] + 4.3, "rise"), (S[1] + 5.2, "stand")],
       [(S[1] + 0.2, S[1] + 3.6, "head_bowed"), (S[1] + 3.6, S[1] + 5.0, "reach_hands"),
        (S[1] + 5.4, S[1] + 7.5, "bow")],
       form=(S[1] + 0.2, 0.9), contact=(S[1] + 4.22, "hand in hand, lifted", "helper"),
       leave=(S[2] - 0.05, S[2] + 0.3), lane=(6.9, 1.2)),
    _p("helper", "woman", "a long dress of light", "glitter", GOLD, "st_help",
       [(S[1] + 0.6, (-1.4, 0.0, 1.5)), (S[1] + 3.4, (0.6, 0.0, 0.1))], 90,
       [(S[1] + 0.6, "walk"), (S[1] + 3.4, "stand")],
       [(S[1] + 3.4, S[1] + 5.0, "reach_hands"), (S[1] + 5.2, S[1] + 7.5, "nod")],
       form=(S[1] + 0.2, 0.9), contact=(S[1] + 4.22, "hand in hand, lifts", "weary"),
       leave=(S[2] - 0.05, S[2] + 0.3), lane=(5.5, 2.9)),
    # 3 Apology, Inclusiveness: one sits turned away and is coming apart (ref 06); the other kneels beside
    _p("hurt", "woman", "a long dress of light", "glitter", COOL, "st_mend",
       [(S[2], (0.6, 0.0, 0.0))], 270,
       [(S[2], "sit_bowed"), (S[2] + 4.0, "turn"), (S[2] + 4.3, "embrace")], [],
       form=(S[2], 0.5),
       effect=[("disperse", S[2] + 0.2, MEND - 0.2, 0.45, "from the side turned away"),
               ("mend", MEND - 0.2, MEND + 0.8, "every particle that left flies back; the body is whole")],
       contact=(MEND, "embrace", "sorry"), leave=(S[3] + 0.6, S[3] + 2.0), lane=(-5.5, 2.9)),
    _p("sorry", "man", "a loose tunic and trousers of light", "glitter", GOLD, "st_mend",
       [(S[2] + 0.4, (2.6, 0.0, 0.3)), (S[2] + 2.4, (1.45, 0.0, 0.1))], 270,
       [(S[2] + 0.4, "walk"), (S[2] + 2.4, "kneel"), (S[2] + 4.3, "embrace")],
       [(S[2] + 3.0, S[2] + 4.2, "hand_on_shoulder")],
       form=(S[2], 0.5), contact=(S[2] + 3.2, "a hand on the shoulder, then the embrace", "hurt"),
       leave=(S[3] + 0.6, S[3] + 2.0), lane=(-6.9, 1.2)),
    # 4 Concession: two reach a door one person wide at the same moment (rim-lit against her light)
    _p("gate_yield", "man", "a long coat of light", "rim", GOLD, "st_gate",
       [(S[3] + 2.4, (-2.6, 0.0, 2.4)), (S[3] + 3.7, (-1.3, 0.0, 1.2)), (S[3] + 4.3, (-1.6, 0.0, 1.5)),
        (S[3] + 6.8, (-1.6, 0.0, 1.5)), (S[3] + 7.6, (0.0, 0.0, -0.5))], 135,
       [(S[3] + 2.4, "walk"), (S[3] + 3.7, "step_aside"), (S[3] + 4.3, "stand"), (S[3] + 6.8, "walk")],
       [(S[3] + 4.1, S[3] + 6.6, "after_you"), (S[3] + 4.4, S[3] + 5.2, "nod")],
       form=(S[3] + 1.8, 0.9), leave=(S[3] + 7.6, S[4] + 0.3), lane=(-8.2, 2.4)),
    _p("gate_first", "woman", "a long dress of light", "rim", COOL, "st_gate",
       [(S[3] + 2.4, (2.6, 0.0, 2.4)), (S[3] + 3.7, (1.2, 0.0, 1.2)), (S[3] + 5.6, (1.2, 0.0, 1.2)),
        (S[3] + 6.9, (0.0, 0.0, -0.6))], 225,
       [(S[3] + 2.4, "walk"), (S[3] + 3.7, "stand"), (S[3] + 5.6, "walk")], [(S[3] + 5.0, S[3] + 5.7, "nod")],
       form=(S[3] + 1.8, 0.9), leave=(S[3] + 6.9, S[4] + 0.3), lane=(8.2, 2.4)),
    # 5 Respect: one speaks thoughts as a stream of light from an open palm (ref 14), one listens (plexus, ref 03)
    _p("speaker", "man", "a loose tunic and trousers of light", "plexus", GOLD, "st_loom",
       [(S[4] + 1.0, (-1.7, 0.0, 0.0))], 90, [(S[4] + 1.0, "stand")],
       [(S[4] + 1.2, S[4] + 3.4, "blow"), (S[4] + 3.4, S[4] + 6.6, "lean_in")],
       form=(S[4] + 0.6, 0.9), effect=[("palm_stream", S[4] + 1.2, S[4] + 3.6, GOLD)],
       leave=(S[5] - 0.6, S[5] + 0.3), lane=(-4.4, 3.4)),
    _p("listener", "woman", "a long dress of light", "plexus", COOL, "st_loom",
       [(S[4] + 1.0, (1.7, 0.0, 0.0))], 270, [(S[4] + 1.0, "stand")],
       [(S[4] + 1.2, S[4] + 3.2, "lean_in"), (S[4] + 3.2, S[4] + 5.4, "blow"),
        (S[4] + 5.5, S[4] + 7.2, "cup_hands")],
       form=(S[4] + 0.6, 0.9), effect=[("palm_stream", S[4] + 3.2, S[4] + 5.4, COOL)],
       leave=(S[5] - 0.6, S[5] + 0.3), lane=(4.4, 3.4)),
    # 6 Encouragement: a child walks the thread to her; the one who roots kneels behind (seen from behind)
    _p("child", "child", "a tunic of light", "glitter", "#e4eeff", "M",
       [(S[5] + 1.2, (-0.36, 0.0, 4.6)), (S[5] + 2.0, (-0.36, 0.0, 4.6)), (S[5] + 5.6, (-0.50, 0.0, 1.2)),
        (S[5] + 6.6, (-0.62, 0.0, 0.28))], 180,
       [(S[5] + 1.2, "stand"), (S[5] + 2.0, "balance_walk"), (S[5] + 6.6, "stand")],
       [(S[5] + 3.6, S[5] + 4.1, "wobble"), (S[5] + 6.1, TOTAL, "hand_up")],
       form=(S[5] + 1.1, 0.8), contact=(TOUCH, "the child's right hand in her left", "Mother")),
    _p("rooter", "woman", "a long dress of light", "rim", GOLD, "M",
       [(S[5] + 1.2, (1.5, 0.0, 5.7)), (S[6] + 1.4, (1.5, 0.0, 5.7)), (S[6] + 3.6, (2.9, 0.0, 4.4))], 180,
       [(S[5] + 1.2, "kneel"), (S[6] + 0.5, "rise"), (S[6] + 1.4, "walk")],
       [(S[5] + 1.6, S[5] + 7.0, "pray"), (S[6] + 2.0, S[7], "raise")],
       form=(S[5] + 1.1, 0.8)),
]
# After its word each pair turns to walk on after her and, under cover of the next pass through cloth, their
# light sinks back into the veil and travels on in it as two glints toward her hem (`leave`: from when, and
# when the body is gone). 7 Everyone: at the sunbreak the veil gives them all back: each gathers again out of
# it and walks up to a place beside and a little behind her (`lane`: metres to her right, metres behind her;
# all outside the camera's half circle), lifts both arms as the veil lifts, and their hems stream upward into
# it (ref 05).
WALK_ON = 1.2               # metres per second
PROCESSION = dict(arrive=(S[6] + 0.4, S[6] + 3.6), gesture=[(S[6] + 2.0, S[7], "raise"), (LIFT, S[7], "look_up")],
                  effect=[("hem_stream_up", LIFT, S[7] + 1.0)], fade_into_day=(S[7] + 0.5, S[7] + 3.0))

MOTHER = dict(
    body="woman", height=MOTHER_HEIGHT, facing=MOTHER_FACING, colors=MOTHER_COLORS,
    clothes="a long robe of light and a deep head veil that hangs forward of the face and down her back",
    look=[(0.0, "glitter with a bright rim, a dark body against the light (ref 10, 13)"),
          (SUNBREAK, "the same in rose gold; the sun does not shine through her")],
    motion=[(0.0, "stand"), (S[0] + 2.3, "walk"), (S[5] - 0.6, "slow to a stand"), (S[5] + 0.4, "stand"),
            (S[7] + 0.3, "walk")],
    gesture=[(CAST, S[0] + 2.3, "open_arms"), (S[5] - 0.4, TOUCH, "hold_thread: left hand low and back, closed"),
             (TOUCH, S[7] + 0.3, "take_hand: the child's right hand in her left"),
             (LIFT, S[7] + 0.3, "raise: both arms, slowly, over 2 s, the child's hand in hers"),
             (S[7] + 0.3, TOTAL, "walk hand in hand")],
    rules=dict(rear_limit=REAR_LIMIT, never=("front", "face", "scaled", "dissolved", "behind words")),
    end="she is not taken apart: she walks on under the arch and the sun's brightness takes her "
        f"({S[7] + 0.5:g} to {S[7] + 4.0:g} s)",
)


def person_present(pid, t):
    """Whether a person stands as a body at t (between their word and the sunbreak they are light in the veil)."""
    p = next(q for q in PEOPLE if q["id"] == pid)
    if t < p["form"][0]:
        return False
    return p["leave"] is None or t <= p["leave"][1] or t >= PROCESSION["arrive"][0]


def person_pos(pid, t):
    """Where a person's feet are at t (world metres): along their path, walking on after her, or, from the
    sunbreak, coming up to their place beside her."""
    p = next(q for q in PEOPLE if q["id"] == pid)
    ts = [k[0] for k in p["path"]]
    pts = np.array([anchor(p["at"], t) + np.asarray(k[1], np.float64) for k in p["path"]])
    a0, a1 = PROCESSION["arrive"]
    if p["leave"] is not None and t >= a0:
        u = min(max((t - a0) / (a1 - a0), 0.0), 1.0)
        home = np.array([p["lane"][0], 0.0, p["lane"][1]])
        return mother_pos(t) + home * (1.6 - 0.6 * u * u * (3 - 2 * u))      # gathers farther out, walks in
    if p["leave"] is not None and t > p["leave"][0]:
        return pts[-1] + np.array([0.0, 0.0, -WALK_ON * (min(t, p["leave"][1]) - p["leave"][0])])
    if len(ts) == 1 or t <= ts[0]:
        return pts[0]
    if t >= ts[-1]:
        return pts[-1]
    i = int(np.searchsorted(ts, t, side="right")) - 1
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    return pts[i] * (1 - u) + pts[i + 1] * u


# ----------------------------------------------------------------------- the end card (existing style, 2D text)
TEXT_SHADOW = 0.0      # nothing dark behind any text
TITLE = dict(label="Healing Concert", lines=["The Words of Mother’s Love"], size=150, y=0.27, label_size=48,
             form=T_FORM, hold=1e9, star=1e9, color=theme.CORAL, glow=theme.WHITE_GLOW, anim="ribbon")
TAGLINE = dict(text="Sunday, December 6 · 4:30 PM\nWorld Mission Society Church of God\n"
                    "6720 W Sahara Ave, Las Vegas",
               sizes=(78, 77), t0=TAG_T0, t1=TAG_T1, color=theme.NAVY, glow=theme.WHITE_GLOW, anim="rise")
CREDIT = dict(song="The Words of Mother’s Love", concert="Healing Concert",
              t_in=1e9, t_full=1e9 + 1.0, t_move=1e9 + 2.0, t_rest=1e9 + 3.0, scale=0.34, alpha_rest=0.0,
              margin_x=0.030, margin_top=0.048)
FRAGMENTS = []         # no lyrics and no other lines on screen
FADE = Track([(0.0, 1.0), (TOTAL, 1.0)])   # the first frame is a picture and the last frame is the card
# The old 2D expressions stay off: the nine are particle words in the world (word_specs). Kept in campaign
# order because engine/arch.py reads PHRASES; the 2D arch is not lit (CORE's arch in space carries the lights).
_SIZES = (150, 118, 124, 150, 164, 128, 100, 128, 140)
PHRASES = [dict(label=lab, lines=lines, size=sz, form=1e9, hold=1e9, star=1e9)
           for (lab, lines), sz in zip(NINE, _SIZES)]
NINTH = 1e9

# ------------------------------------------------------------------------------------------- engine needs
# What this film needs from the 3D layer beyond what P3D-BRIEF.md promises, most important first.
ENGINE_NEEDS = [
    ("BODY", "Heavenly Mother as a rear-only figure: walking and standing from behind in a long robe and a deep "
             "head veil that hangs forward of the face (only veil shows from any angle within 60 degrees of "
             "straight behind); joints readable every frame (crown, shoulders, wrists, palms) and the veil's "
             "back hem as points, so the veil river and its nine pearls join her without a seam; gestures: one "
             "hand held low and back, lightly closed; take a child's hand; raise both arms slowly; hands dense "
             "enough for a macro (about 20 thousand points a hand)."),
    ("CORE", "The camera can pass THROUGH a dense sheet of points: near points open into very large soft discs "
             "with a size cap, an energy cap and a near fade, with no white-out, no popping and no slow frame. "
             "Every song change in this film is such a pass."),
    ("BODY", "Contact by targets: a hand that reaches a given point in space (another hand, a shoulder), an "
             "embrace of two bodies, a child's hand in an adult's; and a child body with a child's proportions."),
    ("WORDS", "Words that belong to a cloth: `surface=` (a function that carries the word's plane, so a word "
              "rides and ripples in a fold and lies flat while it is read); arrive `stitch` (a point of light "
              "sews the letters along their strokes, a thread behind it) and `weave` (two colours of thread); "
              "leave `unravel` (the letters pull out into threads that run along a given path to a point)."),
    ("BODY", "Gather from and return to a point field the song gives (people rise out of the veil's own points; "
             "hems that stay joined to a given curve), and `mend`: the disperse effect run backward on cue until "
             "the body is whole."),
    ("BODY", "Motions beyond the brief: sit with the head bowed; kneel beside someone with a hand on the "
             "shoulder; rise from kneeling; bow with a hand on the heart; step aside and sweep an open palm "
             "(after you); a nod; lean in to listen; cup both hands; a child's careful walk with arms out and a "
             "wobble; lift both arms; walk hand in hand."),
    ("CORE", "Camera: roll along a flown path including one full barrel roll; focus distance and lens opening "
             "as tracks (rack focus from a word to a person); motion blur per shot; a subtle handheld breath."),
    ("CORE", "World: one light on the horizon at a fixed azimuth, raised from star to sun, whose rays are "
             "eclipsed by a head in front of it; sky from the song's own palette keys (deep blue, rose, campaign "
             "day); shafts through a cloth overhead; the nine arch light positions, and the arch hidden until "
             "the song hands it its own arc."),
    ("CORE", "Speed: a veil of about 360 thousand points and 6000 thread lines with its mirror image, plus up "
             "to 12 bodies at many depths (detail by distance)."),
    ("MED2", "The medley's map as data: section starts, downbeats, the breath, the last hit; loudness as a "
             "function of t for the veil's folds and the loom's strings."),
]


# ---------------------------------------------------------------------------------------------- phase B
class Veil:
    """The veil as a p3d point set (phase B). sample(t) gives its batches from VEIL; fold(label) gives the
    point set of the fold that carries an expression (the source its letters are made of)."""

    def sample(self, t):
        raise NotImplementedError("phase B: the veil's points from VEIL (sheet, warp threads, pearls)")

    def fold(self, label):
        raise NotImplementedError("phase B: the points of the fold that carries " + label)


def camera_state(t):
    """camera_at(t) as a p3d CameraState (for p3d.words' check and for CORE)."""
    from p3d.api import CameraState
    c = camera_at(t)
    return CameraState(pos=c["pos"], target=c["target"], fov=c["fov"], roll=c["roll"], focus=c["focus"],
                       aperture=c["aperture"], aspect=ASPECT)


def build(scene):
    """P3D["setup"]: fills the 3D scene. Phase B, in this order:
      1 the veil (class Veil above) with its mirror image, its pearls and its mode per section;
      2 Heavenly Mother (BODY) on mother_pos(t), from MOTHER; the veil joins her hem;
      3 the people (BODY) from PEOPLE: gathered out of the veil, acting in pairs, then the procession;
      4 the nine words: p3d.words.Words(word_specs(veil, people), **WORD_LOOK), checked with camera_state,
        and the nine small ones of REPRISE that stream into the arch;
      5 the old 2D keys the engine still reads (Song, params, credit_state), as in engine/songs/epic_concert.py.
    """
    raise NotImplementedError("ten_09_the_veil is a phase A skeleton: the treatment and the timeline as data")


P3D = dict(camera=camera_at, world=WORLD, setup=build)


# ------------------------------------------------------------------------------------------- the self check
def selfcheck(verbose=True):
    """Checks the timeline against the film's rules. Returns the list of problems (empty when all is well)."""
    problems, notes = [], []
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    bad = sorted({hex(ord(c)) for c in src if 0x2010 <= ord(c) <= 0x2015 or ord(c) == 0x2212})
    if bad:
        problems.append(f"dash characters in this file: {bad}")
    # the nine: exact wording (against p3d.words when it is at hand), all placed, each read for 2.5 s or more
    try:
        from p3d import words as PW
    except Exception:
        PW = None
    if PW is not None:
        theirs = [(e["label"], e["lines"]) for e in PW.EXPRESSIONS]
        if theirs != NINE:
            problems.append("NINE differs from p3d.words.EXPRESSIONS")
    plain = ["How are you?", "Thank you. It's all thanks to you. You've worked hard.",
             "I'm sorry. It must have been hard on you.", "It's okay. I understand.", "Please, after you.",
             "I'd love to hear more about your thoughts.", "I'll pray (or root) for you. Everything will go well.",
             "Can I give you a hand with anything?", "You're amazing. You're doing great!"]
    for (lab, lines), want in zip(NINE, plain):
        got = " ".join(lines).replace("“", "").replace("”", "").replace("’", "'")
        if got != want:
            problems.append(f"{lab}: wording {got!r} is not the campaign's {want!r}")
    if sorted(WORD_PLACES) != sorted(LABELS) or sorted(ORDER_IN_FILM) != sorted(LABELS):
        problems.append("not all nine expressions are placed")
    for lab in ORDER_IN_FILM:
        t_in, t0, t1, t_out = WORD_PLACES[lab]["times"]
        to = WORD_PLACES[lab].get("to")
        end = WORD_PLACES[to]["times"][0] if isinstance(to, str) and to in WORD_PLACES else t1
        if not (0.0 <= t_in < t0 < t1 <= t_out <= TOTAL):
            problems.append(f"{lab}: times out of order {WORD_PLACES[lab]['times']}")
        if end - t0 < 2.5 - 1e-6:
            problems.append(f"{lab}: read for {end - t0:.2f} s, less than 2.5 s")
        if t1 > T_FORM:
            problems.append(f"{lab}: still being read when the end card forms")
        notes.append(f"{lab:14s} arrives {t_in:5.2f}  read {t0:5.2f} to {end:5.2f} ({end - t0:.2f} s)  "
                     f"gone {t_out:5.2f}  width {word_width(lab):4.1f} m  on {WORD_PLACES[lab]['fold']}")
    # the end card: all five lines whole for 4 s or more, to the last frame
    if TOTAL - max(TITLE_HIT, TAG_T1) < 4.0:
        problems.append(f"end card whole for only {TOTAL - max(TITLE_HIT, TAG_T1):.2f} s")
    # the camera: key times in order, always behind her, above the water, never still
    for run in _RUNS:
        ts = [k["t"] for k in run]
        if any(b <= a for a, b in zip(ts[:-1], ts[1:])):
            problems.append(f"camera keys out of order in the run that starts at {ts[0]:g}")
    cut_times = [r[0]["t"] for r in _RUNS[1:]]
    worst_rear, slowest, lowest, seen, big = 0.0, (1e9, 0.0), (1e9, 0.0), 0, 0
    prev = None
    for f in range(NFRAMES):
        t = f / FPS
        cam = camera_at(t)
        d = cam["pos"] - mother_pos(t)
        rear = float(np.degrees(np.arctan2(abs(d[0]), d[2])))
        worst_rear = max(worst_rear, rear)
        if d[2] <= 0.3 or rear > REAR_LIMIT:
            problems.append(f"camera not behind Heavenly Mother at {t:.2f} s ({rear:.0f} degrees off, "
                            f"{d[2]:.1f} m behind)")
            break
        if cam["pos"][1] < lowest[0]:
            lowest = (float(cam["pos"][1]), t)
        if prev is not None and not any(t - 1.5 / FPS < c <= t + 1e-9 for c in cut_times):
            v = float(np.linalg.norm(cam["pos"] - prev)) * FPS
            if v < slowest[0]:
                slowest = (v, t)
        prev = cam["pos"]
        xf, yf, zf = project(cam, mother_pos(t))
        xh, yh, zh = project(cam, mother_pos(t) + [0.0, MOTHER_HEIGHT, 0.0])
        if zh > 0 and 0.0 < xh < 1.0 and 0.0 < yh < 1.0:
            seen += 1
            big += (yh - yf) > 0.15
    if lowest[0] < 0.25:
        problems.append(f"camera {lowest[0]:.2f} m above the water at {lowest[1]:.2f} s")
    if slowest[0] < MIN_SPEED:
        problems.append(f"camera nearly still at {slowest[1]:.2f} s ({slowest[0]:.2f} m/s)")
    notes.append(f"camera: at most {worst_rear:.0f} degrees off straight behind her (limit {REAR_LIMIT:g}); slowest "
                 f"{slowest[0]:.2f} m/s at {slowest[1]:.2f} s; lowest {lowest[0]:.2f} m at {lowest[1]:.2f} s")
    notes.append(f"Heavenly Mother: her head is in the picture for {100.0 * seen / NFRAMES:.0f} percent of the film "
                 f"({seen / FPS:.1f} s), taller than 15 percent of the picture for {big / FPS:.1f} s")
    # words through this camera: in the picture, facing us, large enough for a phone (helper WORDS' own check)
    if PW is not None:
        ws = PW.Words(word_specs(), **WORD_LOOK)
        probs, wnotes = PW.check(ws, camera_state, quiet=True)
        problems += ["words: " + s for s in probs]
        notes += ["words: " + s for s in wnotes if "smallest" in s]
        for w in ws:           # never over Heavenly Mother while it is read
            for t in np.arange(w.t_read0, w.t_read1 + 1e-6, 0.25):
                x0, x1, y0, y1 = PW.screen_box(w, camera_state(float(t)), float(t))[:4]
                xh, yh, zh = project(camera_at(float(t)), mother_pos(float(t)) + [0.0, MOTHER_HEIGHT, 0.0])
                if zh > 0 and x0 < xh < x1 and y0 < yh < y1:
                    problems.append(f"{w.name}: over Heavenly Mother's head at {t:.2f} s")
                    break
    else:
        notes.append("words: engine/p3d is not on the path, so the particle words' own check did not run")
    used = set()
    for p in PEOPLE:
        used |= {m[1] for m in p["motion"]} | {g[2] for g in p["gesture"]}
    notes.append("motions used beyond the brief: "
                 + ", ".join(sorted(used - MOTIONS_PROMISED - MOTIONS_IN_BODY_DRAFT)))
    if verbose:
        print(f"THE VEIL: {TOTAL:g} s, {len(CAMERA_KEYS)} camera keys in {len(_RUNS)} runs, {len(PEOPLE)} people "
              f"and Heavenly Mother, {len(WORD_PLACES)} expressions")
        for i, (a, b) in enumerate(zip(S, S[1:] + (TOTAL,))):
            print(f"\n {i + 1}  {a:5.2f} to {b:5.2f}  {SECTION_NAMES[i].upper()}")
            for t, pos, tgt, fov, roll, note in camera_world_keys():
                if a <= t < b or (i == 7 and t == TOTAL):
                    print(f"    {t:5.2f}  at ({pos[0]:6.1f} {pos[1]:5.1f} {pos[2]:6.1f})  looks at "
                          f"({tgt[0]:5.1f} {tgt[1]:4.1f} {tgt[2]:6.1f})  fov {fov:2.0f}  {note}")
        print()
        for s in notes:
            print("note:", s)
        for s in problems:
            print("PROBLEM:", s)
        print("ok" if not problems else f"{len(problems)} problems")
    return problems


if __name__ == "__main__":
    sys.exit(1 if selfcheck() else 0)
