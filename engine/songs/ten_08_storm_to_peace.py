"""Film 08 of ten: STORM TO PEACE. A 60 second promo for the Healing Concert "The Words of Mother's Love".

LOGLINE
  A storm at sea is unmade one word at a time. Each of the nine Words of Mother's Love falls like a drop of
  calm: where it lands the heaving sea goes still as glass, the rain stops in the air, the people there turn
  toward each other. The calm spreads section by section until the whole sea is one mirror at sunrise.

THE RULES OF THIS WORLD
  One field rules everything: calm(x, z, t), 0 storm, 1 peace (CALM below: discs that open where a word falls).
  The sea of points heaves only where it is 0; the rain falls only there; at the edge of a calm the water burns
  as a line of light. People in the storm are dark shapes with a burning rim whose light is torn away downwind;
  in the calm they fill with warm glitter. The words are made from the storm's own matter: hanging raindrops,
  a frozen bolt of lightning, the great wave, the touch of two hands, the rays through the eye of the storm.

SHOT BY SHOT (the medley's sections: 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21 breath, 42.51 the biggest
hit, 49.47 finale, 58.11 final hit)
  0.0   THE STORM. Frame one is lit by lightning: a woman in profile, close, a dark shape rimmed in fire, her
        light streaming away in the wind. The camera is torn away downwind over the crests: two people stand
        apart on the heaving sea, braced. It looks up: one coral drop falls slowly out of the cloud.
  3.27  It lands between them. A disc of glass races out; the rain stops falling there; the two turn to each
        other. The hanging drops draw together: GREETING (read 4.3 to 6.95). They fall into the glass.
  6.84  Lightning far off; the camera rises out into the storm. 7.56: a bolt comes down over someone kneeling
        alone and STOPS in the air, turning from violet to apricot. A man kneels beside her, his hand on her
        shoulder. The bolt bends into APOLOGY (read 9.6 to 12.3); its embers settle on her.
  13.30 WOW 1. All the rain stops in mid air. The camera flies on through thousands of hanging beads of light to
        an outsider whose light is blown away in a long stream; the stream hangs, then flows back into her. The
        beads gather: INCLUSIVENESS (read 15.0 to 17.7). Someone comes and puts a hand on her shoulder.
  18.4  The sea stands up. Rain again. Three backs, a man, a mother, her child, and a wave 9 m high over them.
  19.85 WOW 2. The wave does not break: it bows and lies down as glass, uncovering CONCESSION (read 21.0 to 23.7).
        The man steps aside with an open palm; the words open like a gate and the mother walks through.
  24.3  The child turns to the man; he kneels to her height and listens. RESPECT is written by the dying wind
        (read 26.0 to 28.7) while the camera circles them; the words flow into him.
  29.79 Two hands across the edge of the calm, one gold on the glass, one storm blue in the swell. They touch
        (30.4); a flare; the calm bursts from the touch: CONSIDERATION (read 31.8 to 34.5).
  33.36 The camera rises: the circles of calm run together into one great eye. Down in it, seen only from
        behind, veiled, Heavenly Mother, rays fanning behind her head. She opens her arms low. ENCOURAGEMENT
        burns out of the rays (read 37.6 to 40.3) and streams down into her open hand.
  40.21 The breath: close on her open hand from behind; the light lies in her palm.
  42.51 WOW 3, the biggest hit. The light leaves her hand and the calm runs to the horizon: the storm is blown
        open, the whole sea becomes one mirror, the sun breaks. She rises away into gold flakes where she stood.
        People stand on the mirror and bow to each other: GRATITUDE rises out of the sun's glitter on the water
        (read 45.3 to 48.0).
  49.47 Arms rise. Lights gather from everyone into COMPLIMENT (read 50.0 to 52.4), which streams into the arch
        of nine lights. The sky opens into the campaign day; the end card (title whole about 55, the date,
        church and address from 54.7) holds to the last frame over the mirror. No fade to black.

Everything here is my own: the storm (engine/p3d/ten_08_storm.py), people (engine/p3d body), words
(engine/p3d words), the end card is the existing 2D end card of epic_concert.py. No lyrics, no faces, no long
dashes, Heavenly Mother only from behind or as a hand.
"""
import numpy as np

import songs.epic_concert as _base
from track import Track

# ---- the medley's sections (scratchpad medley2/SECTION-MAP.md)
A, B, C, D, E, F, G, HIT, H, FIN = 0.25, 6.84, 13.30, 19.85, 26.79, 33.36, 40.21, 42.51, 49.47, 58.11

# ---- the end card in the existing style (coral title, navy lines on the campaign day), nothing else 2D
TITLE_WHOLE = 55.6
_base.FADE = Track([(0.0, 1.0), (60.0, 1.0)])          # frame 0 is lit; no fade to black at the end
_base.EXPOSURE = Track([(0.0, 1.0), (60.0, 1.0)])
for _p in _base.PHRASES:                                 # the expressions are particles here, never flat text
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = TITLE_WHOLE - _base.FORM_DUR - 0.75
_base.TITLE["y"] = 0.25
_base.TITLE_HIT = TITLE_WHOLE
_base.NINTH = 1e9
_base.TAGLINE["t0"], _base.TAGLINE["t1"] = 53.4, 54.7
_base.FRAGMENTS = []
_base.SYMBOLS = []
_base.FIGURES = []
_base.GATHERING = None
_base.PASS_LIGHT = None
_base.WAVES = []
_base.FALLING_STARS = []
_base.RIPPLES = []
_base.RIPPLES_AUTO = Track([(0.0, 0.0), (60.0, 0.0)])
_base.DOVES = Track([(0.0, 0.0), (60.0, 0.0)])
_base.BUBBLES = Track([(0.0, 0.0), (60.0, 0.0)])
_base.LEAVES = Track([(0.0, 0.0), (60.0, 0.0)])
from songs.epic_concert import *  # noqa: E402,F401,F403

from p3d import words as PW  # noqa: E402
from p3d.body import Body, Hands  # noqa: E402
from p3d.camera import Rig, dolly, fly, orbit  # noqa: E402
from p3d.effects import Wind  # noqa: E402
from p3d.api import Mask, lin  # noqa: E402
from p3d.ten_08_storm import Beads, Bolt, Drop, Glow, Rain, Sea, flash_level  # noqa: E402
from p3d.world import arch_points  # noqa: E402

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0

# ---- the concert badge (PHASEB UPDATE 3, the same in all ten films): large on frame 0, in the top left corner
# by 2.8 s, gone as the end card starts to form (the end card carries the same words)
CREDIT = dict(song="The Words of Mother’s Love",
              concert="Healing Concert · Sunday, December 6 · 4:30 PM",
              t_in=-1.0, t_full=0.0,
              t_move=1.6, t_rest=2.8,
              scale=0.55, alpha_rest=0.92,
              margin_x=0.035, margin_top=0.05)
BADGE_OUT = TITLE_WHOLE - _base.FORM_DUR - 0.75      # the end card's title starts to form


def credit_state(t, bbox):
    """Centre, scale and strength of the badge; bbox is its size at full card size (demo_gathering.py), and it
    fades out over 1 s from BADGE_OUT."""
    c = CREDIT
    x0, x1, y0, y1 = bbox

    def ss(a, b, x):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    a_in = ss(c["t_in"], c["t_full"], t)
    m = ss(c["t_move"], c["t_rest"], t)
    scale = c["scale"] ** m
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = c["margin_x"] + c["scale"] * (x1 - x0) / 2.0
    ty = 1.0 - c["margin_top"] - c["scale"] * (y1 - y0) / 2.0
    cx, cy = cx0 * (1 - m) + tx * m, cy0 * (1 - m) + ty * m
    alpha = a_in * (1.0 + (c["alpha_rest"] - 1.0) * m) * (1.0 - ss(BADGE_OUT, BADGE_OUT + 1.0, t))
    return (cx, cy, scale, alpha), (cx0, cy0)


def params(song, t):
    """epic_concert's params, here so that it finds star_state and link_state, which engine/song.py installs
    into this module (the base module's own copy cannot see them)."""
    f = min(int(round(t * FPS)), NFRAMES - 1)
    env, envs, hi, pulse = song.env[f], song.env_slow[f], song.hi[f], song.pulse[f]
    lx, ly = song.lantern(t)
    z = ZOOM(t)
    lsx, lsy = (lx - 0.5) / z + 0.5, (ly - HORIZON) / z + HORIZON
    return dict(
        t=t, env=float(env), env_slow=float(envs), hi=float(hi), pulse=float(pulse),
        sky_top=SKY_TOP(t), sky_mid=SKY_MID(t), sky_hor=SKY_HOR(t), glow=GLOW(t),
        sun_int=SUN_INT(t) * (0.92 + 0.20 * envs), sun_y=SUN_Y(t), sun_size=SUN_SIZE(t),
        stars=STARS(t), milky=MILKY(t), clouds=CLOUDS(t), aurora=AURORA(t), rain=RAIN(t),
        motes=MOTES(t) * (0.75 + 0.5 * envs), lanterns=LANTERNS(t), petals=PETALS(t),
        trail=TRAIL(t), exposure=EXPOSURE(t), fade=FADE(t), rays=RAYS(t), part=PART(t), zoom=ZOOM(t),
        lantern=(lsx, lsy), prog=lx, rings=[], waves=[],
        star=[(s[0], -1.0, 0.0) for s in star_state(t)],   # noqa: F821  (installed by engine/song.py from arch.py)
        link=link_state(t),   # noqa: F821
    )


def _ss(a, b, x):
    u = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _ramp(keys):
    tr = Track([(float(k[0]), float(k[1])) for k in keys])
    return lambda t: float(tr(t))


# ------------------------------------------------------------------------------------------------ places
G1 = (0.0, 0.0, 80.0)          # the first drop: Greeting
G2 = (12.5, 0.0, 60.0)         # the frozen bolt: Apology
G3 = (-6.0, 0.0, 44.0)         # the stopped rain: Inclusiveness
G4 = (0.0, 0.0, 28.0)          # the three before the wave: Concession, Respect
WAVE_Z = 18.5
G5 = (-24.3, 0.0, 15.6)        # two hands across the edge, one pulls the other up: Consideration
G6 = (0.0, 0.0, 0.0)           # the eye: Heavenly Mother (she faces the dawn, toward -z)
SUN_AZ = 180.0
DROP_LAND = 3.27
STRIKE = 7.56
TOUCH = 30.4

# ---------------------------------------------------------------------------------------------- the calm
# discs on the water: centre, radius keys, edge width (metres)
CALM = [
    dict(c=G1, r=[(DROP_LAND, 0.0), (DROP_LAND + 0.8, 11.0), (B, 13.0)], e=1.2),
    dict(c=G2, r=[(STRIKE + 0.3, 0.0), (STRIKE + 1.3, 10.0), (C, 12.0)], e=1.2),
    dict(c=G3, r=[(C, 0.0), (C + 1.3, 15.0), (D - 1.0, 16.0)], e=1.2),
    # its edge passes through the place where the two hands meet (25.13 m from its centre) until the touch
    dict(c=(0.0, 0.0, 22.0), r=[(D, 0.0), (D + 1.1, 20.0), (E, 22.0), (E + 0.8, 25.13), (TOUCH, 25.13), (F, 34.0)],
         e=0.7),
    dict(c=G5, r=[(TOUCH, 0.0), (TOUCH + 1.2, 30.0), (F, 34.0), (F + 2.6, 70.0)], e=1.5),
    dict(c=G6, r=[(F, 0.0), (F + 2.6, 62.0), (HIT, 62.0), (HIT + 1.6, 3000.0)], e=4.0),
]
for _c in CALM:
    _c["tr"] = Track(_c["r"])


def calm_at(x, z, t):
    x, z = np.asarray(x, np.float64), np.asarray(z, np.float64)
    out = np.zeros(np.broadcast(x, z).shape)
    for c in CALM:
        if t <= c["r"][0][0]:
            continue
        r = float(c["tr"](t))
        if r <= 0.0:
            continue
        d = np.hypot(x - c["c"][0], z - c["c"][2])
        out = np.maximum(out, 1.0 - _ss(r - c["e"], r + c["e"], d))
    return out


def _engine_calm(t):
    """The engine's glass discs (four at most): the four most recent calms."""
    live = [c for c in CALM if t > c["r"][0][0]]
    out = []
    for c in live[-4:]:
        out.append(dict(center=(c["c"][0], c["c"][2]), radius=max(float(c["tr"](t)), 0.0), soft=c["e"],
                        ripple=0.0, mirror=1.0))
    return out


STORM = _ramp([(0.0, 1.0), (F, 1.0), (G, 0.85), (HIT, 0.85), (HIT + 1.4, 0.0), (60.0, 0.0)])
WARM = _ramp([(0.0, 0.0), (HIT, 0.0), (HIT + 2.0, 1.0), (60.0, 1.0)])
GLASS = _ramp([(0.0, 0.10), (HIT, 0.10), (HIT + 1.5, 0.22), (52.0, 0.18), (55.0, 0.10), (60.0, 0.10)])

# ------------------------------------------------------------------------------------------ the lightning
# (time, place in the cloud, strength): the cloud flashes, the sea and the people take the light
FLASHES = [
    (0.0, (-30.0, 40.0, 44.0), 0.45), (0.95, (36.0, 40.0, 48.0), 0.5), (2.1, (-45.0, 55.0, 55.0), 0.5),
    (B, (25.0, 50.0, 55.0), 0.6), (STRIKE, (11.0, 45.0, 52.0), 0.7), (11.0, (-50.0, 40.0, 30.0), 0.35),
    (18.6, (0.0, 35.0, -8.0), 0.45), (19.5, (8.0, 38.0, -6.0), 0.55), (22.8, (-60.0, 40.0, -10.0), 0.3),
    (E, (-40.0, 45.0, 0.0), 0.5), (29.6, (-60.0, 40.0, -10.0), 0.5), (F, (30.0, 50.0, -20.0), 0.6),
    (35.6, (-90.0, 40.0, -50.0), 0.3), (38.4, (90.0, 40.0, -70.0), 0.25),
]


def flash(t):
    return flash_level(FLASHES, t)


def _flash_place(t):
    """Where the latest flash is (the cloud light that colours the mist and the water)."""
    best = FLASHES[0][1]
    for tf, p, _ in FLASHES:
        if tf <= t:
            best = p
    return best


BOLT_A = Bolt((9.0, 38.0, 52.0), (12.2, 5.8, 59.4), STRIKE, seed=11, freeze=STRIKE + 0.24, fade=9.3,
              color="#e8dcff", color2="#ffbf86", width=0.09, turn=1.4)
BOLT_B = Bolt((-31.0, 38.0, 44.0), (-27.0, 0.0, 51.0), 0.0, seed=4, color="#e0d8ff", width=0.16)
BOLT_D = Bolt((34.0, 42.0, 48.0), (28.0, 0.0, 56.0), 0.95, seed=9, color="#e0d8ff", width=0.14)
BOLT_C = Bolt((6.0, 36.0, -4.0), (3.0, 0.0, 8.0), 19.5, seed=7, color="#e0e8ff", width=0.14)
DROP = Drop((0.4, 26.0, 79.0), (0.0, 0.05, 80.0), 1.9, DROP_LAND)

RAIN_SPEED = _ramp([(0.0, 1.0), (C - 0.05, 1.0), (C + 0.35, 0.0), (18.2, 0.0), (19.2, 1.0), (60.0, 1.0)])
RAIN_AMOUNT = _ramp([(0.0, 1.0), (17.7, 1.0), (18.6, 0.3), (19.3, 1.0), (F, 0.9), (36.5, 0.35), (HIT, 0.2),
                     (HIT + 0.4, 0.0), (60.0, 0.0)])

# ------------------------------------------------------------------------------------------------ the wave
WAVE_H = _ramp([(17.8, 0.0), (18.6, 2.5), (D - 0.1, 9.0), (D + 0.4, 7.5), (D + 1.3, 0.0)])


def wave_points(t, n_x=420, n_s=70):
    """A wall of water across the path at WAVE_Z: crest height WAVE_H(t); as it bows the crest leans toward the
    camera and sinks."""
    h = WAVE_H(t)
    if h <= 0.02:
        return None
    lean = float(_ss(D, D + 1.0, t)) * 0.6
    x = np.linspace(-30.0, 30.0, n_x)
    s = np.linspace(0.0, 1.0, n_s)
    X, S = np.meshgrid(x, s, indexing="ij")
    taper = np.clip(1.0 - (np.abs(X) / 30.0) ** 3, 0.0, 1.0)
    hh = h * taper
    ripple = 0.25 * np.sin(X * 0.7 + t * 2.0) * hh / 9.0
    Y = hh * np.sin(S * np.pi * 0.5) + ripple
    Z = WAVE_Z - (1.0 - S) * hh * 0.8 + (S ** 3) * hh * (0.35 + lean)
    return X.ravel(), Y.ravel(), Z.ravel(), S.ravel(), hh.ravel()


class Wave:
    def __init__(self):
        rng = np.random.default_rng(21)
        self.j = rng.uniform(-0.5, 0.5, (420 * 70, 3))
        self.seed = rng.uniform(0.0, 1.0, 420 * 70)

    def sample(self, t):
        w = wave_points(t)
        if w is None:
            return []
        X, Y, Z, S, hh = w
        pos = np.stack([X + self.j[:, 0] * 0.14, Y + self.j[:, 1] * 0.10, Z + self.j[:, 2] * 0.10], axis=1)
        crest = S ** 6 * _ss(2.0, 5.0, hh)
        fl = flash(t)
        col = (lin("#1b4a60") * 0.35)[None, :] * (1.0 - crest[:, None]) + (lin("#e2f2ff") * 1.1)[None, :] * \
            crest[:, None]
        col = col * (1.0 + 2.0 * fl)
        a = 0.85 * _ss(1.2, 3.0, hh)
        return [dict(pos=pos, size=0.07 + 0.08 * crest, color=col, alpha=a, kind="soft", seed=self.seed,
                     twinkle=0.4, emit=1.0 + 2.0 * crest, reflect=True)]


def _crest_y(t):
    return WAVE_H(t) * (1.0 - 0.0) - 0.4


# ------------------------------------------------------------------------------------------------- people
WIND = Wind(base=(4.5, 0.0, 0.6), gusts=[(0.5, 0.6, 1.5), (B, 0.5, 1.5), (D - 0.5, 0.8, 1.5), (E, 0.4, 1.2)])
CALMWIND = Wind(base=(0.4, 0.0, 0.1))


def _fill(t_calm, dur=1.4):
    """0 the storm light, 1 the calm light from t_calm on."""
    return lambda t: float(_ss(t_calm, t_calm + dur, t))


def _looks(t_calm, warm="#ffd39a", rim="#9fc4ff"):
    """Everyone is a body of light (glitter, never a dark shape): in the storm a cool, restless light that the
    wind tears away; in the calm it warms to gold and grows brighter."""
    f = _fill(t_calm)
    return [dict(name="glitter", weight=lambda t: 1.0 - f(t), color=rim, color2="#eef4ff", bright=1.7),
            dict(name="glitter", weight=f, color=warm, color2="#fff4e2", bright=2.0)]


def _storm_shed(t0, t1, dir=(1.0, 0.18, 0.15)):
    return dict(kind="shed", t=t0, until=t1, dir=dir, speed=1.6, n=7000, life=2.6, color="#cfe0ff")


BODIES = {}


class _Person:
    """A body built when it is first needed (the workflow's first step imports the song with numpy only, and
    a body's garments need scipy)."""

    def __init__(self, shape, kw):
        self.shape, self.kw, self._b = shape, kw, None

    @property
    def b(self):
        if self._b is None:
            self._b = Body(self.shape, **self.kw)
        return self._b

    wants_camera = True

    def sample(self, t, cam=None):
        return self.b.sample(t, cam)

    def where(self, t, place, **kw):
        return self.b.where(t, place, **kw)


def _person(name, shape, **kw):
    kw.setdefault("points", 42000)
    kw.setdefault("fade", 0.4)
    b = _Person(shape, kw)
    BODIES[name] = b
    return b


# the first two: apart in the storm, the drop lands between them
_person("w1", "woman", at=(-1.7, 80.0), facing=[(0.0, 270.0), (DROP_LAND + 0.5, 270.0), (DROP_LAND + 1.6, 90.0)],
        motion=[(0.0, "stand"), (DROP_LAND + 0.4, "shuffle"), (DROP_LAND + 1.7, "stand")],
        gesture=[(1.3, DROP_LAND + 0.4, "brace"), (DROP_LAND + 2.2, 9.0, "listen")],
        garment="dress", look=_looks(DROP_LAND + 0.4), wind=WIND, show=(0.0, 8.6), seed=1,
        detail=dict(head=2.5), effects=[_storm_shed(0.0, DROP_LAND + 0.8)])
_person("m1", "man", at=(1.8, 80.3), facing=270.0,
        gesture=[(0.0, DROP_LAND + 0.4, "brace"), (DROP_LAND + 2.4, 6.4, "raise_hand", dict(side="R"))],
        garment="coat", look=_looks(DROP_LAND + 0.5), wind=WIND, show=(0.0, 8.6), seed=2,
        effects=[_storm_shed(0.0, DROP_LAND + 0.8)])
# the frozen bolt: someone kneels alone; a man comes, kneels beside her and rests a hand on her shoulder
_person("kneel", "woman", at=(12.3, 60.0), facing=270.0, motion=[(6.0, "kneel")],
        gesture=[(6.0, 10.6, "bow", dict(amount=34.0)), (10.6, 14.0, "look_up", dict(amount=8))],
        garment="robe", look=_looks(STRIKE + 1.2), wind=WIND, show=(6.2, 13.9), seed=3,
        effects=[_storm_shed(6.2, STRIKE + 1.0)])
_person("sorry", "man", at=[(6.3, (16.5, 61.2)), (8.9, (13.25, 60.3))], facing=[(6.3, 250.0), (8.9, 255.0)],
        motion=[(6.3, "walk"), (8.9, "kneel", dict(blend=0.6))],
        gesture=[(9.7, 14.0, "hand_on_shoulder", dict(side="R", to=lambda t: BODIES["kneel"].where(t, "shoulder.R")))],
        garment="coat", look=_looks(STRIKE + 1.4), wind=WIND, show=(6.3, 13.9), seed=4,
        effects=[_storm_shed(6.3, STRIKE + 1.2)])
# the stopped rain: an outsider whose light is blown away; it hangs and flows back; a friend comes
_person("outsider", "woman", at=(-6.0, 44.0), facing=270.0,
        gesture=[(12.6, 15.0, "brace"), (15.4, 19.8, "look_up", dict(amount=6))],
        garment="dress", look=_looks(C + 1.6), wind=WIND, show=(12.6, 19.8), seed=5,
        effects=[dict(kind="disperse", t=12.6, amount=_ramp([(12.6, 0.30), (13.2, 0.42), (C + 1.2, 0.42),
                                                              (C + 3.0, 0.0), (20.0, 0.0)]), reach=2.4,
                      dir=(1.0, 0.15, 0.1), share=0.45)])
_person("friend", "man", at=[(13.2, (-10.8, 45.6)), (16.0, (-7.0, 44.3))], facing=[(13.2, 110.0), (16.0, 100.0)],
        motion=[(13.2, "walk"), (16.0, "stand", dict(blend=0.5))],
        gesture=[(16.3, 19.8, "hand_on_shoulder", dict(side="L", to=lambda t: BODIES["outsider"].where(t, "shoulder.L")))],
        garment="tunic", look=_looks(13.0), wind=CALMWIND, show=(13.2, 19.8), seed=6)
# the three before the wave
_person("giver", "man", at=[(17.6, (-2.3, 28.0)), (21.4, (-2.3, 28.0)), (22.6, (-3.4, 27.7))],
        facing=[(17.6, 180.0), (21.2, 180.0), (21.9, 120.0), (24.2, 120.0), (24.8, 90.0)],
        motion=[(17.6, "stand"), (21.3, "shuffle"), (22.7, "stand"), (24.6, "kneel", dict(blend=0.6))],
        gesture=[(17.6, D, "brace"), (21.8, 23.8, "offer", dict(side="R")), (25.4, 30.0, "listen")],
        garment="coat", look=_looks(D + 0.6), wind=WIND, show=(17.6, 29.9), seed=7,
        effects=[_storm_shed(17.6, D + 0.5)])
_person("mother", "woman", at=[(17.6, (2.0, 28.3)), (22.9, (2.0, 28.3)), (26.4, (0.9, 23.0))],
        facing=[(17.6, 180.0), (22.9, 190.0)], motion=[(17.6, "stand"), (22.9, "walk"), (26.4, "stand")],
        gesture=[(17.6, D, "brace")], garment="dress", veil=False, look=_looks(D + 0.6), wind=WIND,
        show=(17.6, 27.4), seed=8, effects=[_storm_shed(17.6, D + 0.5)])
_person("child", "child", at=(-1.25, 28.1), facing=[(17.6, 180.0), (23.8, 180.0), (24.5, 270.0)],
        motion=[(17.6, "stand"), (23.8, "shuffle"), (24.6, "stand")],
        gesture=[(25.0, 28.5, "look_up", dict(amount=10))],
        garment="dress", look=_looks(D + 0.6, warm="#ffe0b8"), wind=WIND, show=(17.6, 29.9), seed=9,
        effects=[_storm_shed(17.6, D + 0.5)])
# one on the glass pulls the other, who sits in the swell, up by the hands (the clips are a captured pair:
# both bodies share one place and facing; at clip time 2.5 s their hands meet, at 3.4 to 4.8 s she rises)
PULL_T0 = TOUCH - 2.0
_person("puller", "man", at=(-24.0, 14.04), facing=0.0, motion=[(PULL_T0, "pull_up", dict(phase=0.32)), (34.9, "stand", dict(blend=0.8))],
        garment="tunic", look=dict(name="glitter", color="#ffc56e", color2="#fff0d0", bright=2.0), wind=CALMWIND,
        show=(30.7, 35.2), fade=0.15, seed=12)
_person("helped", "woman", at=(-24.0, 14.04), facing=0.0, motion=[(PULL_T0, "helped_up", dict(phase=0.32)), (34.9, "stand", dict(blend=0.8))],
        garment="dress", look=_looks(31.6, rim="#8fbcff"), wind=WIND, show=(30.7, 35.2), fade=0.15, seed=13)
# two hands across the edge of the calm in close up (gold on the glass, storm blue in the swell)
MEET = (G5[0], 0.92, G5[2])
HANDS = dict(meet=MEET, t_touch=TOUCH, axis=270.0, color="#ffc56e", color2="#7fb6ff", apart=0.6, approach=2.4,
             points=50000)
# Heavenly Mother, only from behind: she faces the dawn (-z); every camera that sees her is behind her
MOTHER = _person("mother_hm", "woman", at=(0.0, 0.0), facing=180.0, garment="robe", veil=dict(length=1.4),
                 gesture=[(36.2, 44.0, "open_arms")],
                 look=dict(name="glitter", color="#f6c27a", color2="#fff0d2", bright=1.15), points=70000,
                 wind=CALMWIND, show=(34.2, 46.0), seed=10,
                 effects=[dict(kind="form", t=34.2, dur=2.2), dict(kind="dissolve", t=HIT + 0.1, dur=2.6)])
# people on the mirror at sunrise: in pairs, they bow to each other, then raise their arms
CROWD = []
_PAIRS = [((-4.2, 9.0), 75.0), ((-2.7, 9.4), 255.0), ((2.6, 10.6), 95.0), ((4.0, 10.3), 275.0),
          ((-0.8, 14.2), 70.0), ((0.7, 14.6), 250.0), ((-7.5, 15.5), 120.0), ((7.4, 16.5), 230.0)]
_SHAPES = ["woman", "man", "man", "woman", "child", "woman", "man", "woman"]
for _k, ((_x, _z), _f) in enumerate(_PAIRS):
    CROWD.append(_person("crowd%d" % _k, _SHAPES[_k], at=(_x, _z), facing=_f, points=34000,
                         gesture=[(45.4 + 0.15 * (_k % 3), 48.0, "bow", dict(amount=30.0)),
                                  (49.6 + 0.12 * _k, 60.0, "raise")],
                         garment=["dress", "coat", "tunic", "robe", "dress", "robe", "coat", "dress"][_k],
                         look=dict(name="glitter", color=["#ffd9a6", "#ffcf8a", "#ffe2b8", "#ffd2a0"][_k % 4],
                                   color2="#fff2dc", bright=2.1), wind=CALMWIND, show=(42.0, 60.0), seed=20 + _k,
                         effects=[dict(kind="form", t=42.6 + 0.2 * _k, dur=2.0)]))

# ------------------------------------------------------------------------------------------------ camera
CAMERA = Rig([
    # torn away from her profile downwind, over the crests; look up at the drop; it lands; glide
    fly([(0.0, (-1.95, 1.56, 81.45), (-2.15, 1.66, 80.0)),
         (0.7, (-1.35, 1.66, 81.8), (-1.85, 1.55, 79.9)),
         (1.7, (4.6, 2.5, 85.5), (0.0, 1.2, 79.0)),
         (2.5, (5.4, 2.0, 88.6), (0.6, 4.5, 79.0)),
         (DROP_LAND, (4.0, 1.9, 89.4), (0.0, 1.8, 80.0)),
         (5.0, (2.0, 1.85, 89.9), (0.0, 2.3, 80.0)),
         (B, (-2.2, 1.95, 89.8), (0.0, 2.3, 80.0))],
        fov=lambda t: float(np.interp(t, [0.0, 0.7, 1.7, 3.3, 6.8], [40.0, 40.0, 52.0, 46.0, 44.0])),
        roll=lambda t: float(np.interp(t, [0.0, 0.8, 1.6, 2.4, 3.3], [0.0, -3.0, -12.0, 5.0, 0.0])),
        aperture=lambda t: float(np.interp(t, [0.0, 1.2, 2.0], [0.03, 0.03, 0.015]))),
    # out into the storm; the strike; down to the two
    fly([(B, (-2.2, 1.95, 89.8), (0.0, 2.3, 80.0)),
         (7.5, (2.0, 4.8, 90.0), (9.5, 6.0, 62.0)),
         (8.6, (14.8, 2.6, 71.0), (12.5, 3.0, 60.0)),
         (12.2, (13.6, 1.9, 68.6), (12.4, 2.8, 60.0)),
         (C, (13.0, 1.3, 64.6), (12.4, 1.2, 60.0))],
        fov=lambda t: float(np.interp(t, [B, 7.5, 8.6, 12.2, C], [44.0, 52.0, 44.0, 42.0, 40.0])),
        roll=lambda t: float(np.interp(t, [B, 7.2, 7.9, 8.6], [0.0, 10.0, -8.0, 0.0])), aperture=0.02, blend=0.5),
    # WOW 1: through the hanging beads to the outsider, a glide while her light flows back
    fly([(C, (13.0, 1.3, 64.6), (12.4, 1.2, 60.0)),
         (14.4, (2.0, 2.6, 56.0), (-6.0, 2.4, 44.0)),
         (15.0, (-2.6, 2.1, 53.0), (-6.0, 2.5, 44.0)),
         (17.7, (-9.0, 2.0, 52.6), (-6.0, 2.5, 44.0)),
         (18.6, (-4.0, 2.2, 42.0), (0.0, 4.0, 22.0))],
        fov=lambda t: float(np.interp(t, [C, 14.4, 15.0, 17.7, 18.6], [40.0, 56.0, 46.0, 46.0, 52.0])),
        aperture=lambda t: float(np.interp(t, [C, 14.4, 15.0], [0.02, 0.09, 0.035])), blend=0.6),
    # the sea stands up behind the three; the wave bows; a step forward between them
    fly([(18.6, (-4.0, 2.2, 42.0), (0.0, 4.0, 22.0)),
         (D - 0.4, (0.6, 1.35, 36.6), (0.0, 6.8, 18.0)),
         (D + 1.0, (0.5, 1.5, 36.0), (0.0, 3.2, 18.5)),
         (23.7, (-0.1, 1.75, 34.2), (0.0, 3.0, 18.5)),
         (24.8, (-0.4, 1.5, 33.0), (-1.9, 2.3, 27.6))],
        fov=lambda t: float(np.interp(t, [18.6, D, 21.0, 24.8], [52.0, 54.0, 46.0, 44.0])),
        roll=lambda t: float(np.interp(t, [18.6, 19.4, D, 20.6], [6.0, -4.0, 3.0, 0.0])), aperture=0.02, blend=0.6),
    # round the man and the child while the wind writes
    orbit((-1.9, 0.0, 27.8), radius=(6.2, 6.6), height=(1.35, 1.5), a0=18.0, a1=-26.0, t0=24.8, t1=29.3,
          look=(-1.9, 1.75, 27.6), fov=44.0, aperture=0.02, blend=0.6),
    # whip to the two hands at the edge of the calm; the touch; back to see the word
    fly([(29.3, (-22.4, 1.25, 17.6), (-24.3, 0.92, 15.6)),
         (30.2, (-23.5, 1.06, 16.75), (-24.3, 0.92, 15.6)),
         (30.85, (-23.75, 1.02, 16.45), (-24.3, 0.92, 15.6))],
        fov=lambda t: float(np.interp(t, [29.3, 30.2, 30.85], [40.0, 34.0, 32.0])), aperture=0.03, blend=0.4),
    # the flash of the touch hides a cut: the two of them, she is pulled to her feet; the camera drifts in
    fly([(30.85, (-24.6, 1.45, 21.9), (-24.3, 1.6, 15.6)),
         (F, (-24.4, 1.5, 21.1), (-24.3, 1.65, 15.6)),
         (34.5, (-25.0, 3.0, 22.0), (-24.3, 1.95, 15.6))],
        fov=lambda t: float(np.interp(t, [30.85, F, 34.5], [44.0, 44.0, 47.0])), aperture=0.015, blend=0.0),
    # the circles run together: up and over the sea, down behind Heavenly Mother
    fly([(34.5, (-25.0, 3.0, 22.0), (-24.3, 1.95, 15.6)),
         (35.4, (-18.0, 8.5, 25.0), (-4.0, 1.0, 4.0)),
         (36.5, (-5.0, 4.6, 13.0), (0.0, 1.6, 0.0)),
         (37.6, (1.3, 1.85, 3.6), (0.0, 1.75, -2.0))],
        fov=lambda t: float(np.interp(t, [34.5, 35.4, 36.5, 37.6], [44.0, 56.0, 46.0, 42.0])), aperture=0.015,
        blend=0.6),
    orbit((0.0, 0.0, 0.0), radius=(3.85, 3.5), height=(1.8, 1.75), a0=20.0, a1=-12.0, t0=37.6, t1=40.4,
          look=(0.0, 1.75, -2.0), fov=46.0, aperture=0.02, blend=0.8),
    # the breath: close on her open hand from behind; the hit throws the camera back and up
    dolly((1.5, 1.55, 2.5), (1.08, 1.22, 1.05), 40.4, HIT, look=((0.46, 0.98, -0.2), (0.46, 0.95, -0.25)),
          fov=(42.0, 36.0), aperture=0.022, blend=0.8),
    fly([(HIT, (1.1, 1.3, 1.2), (0.46, 0.95, -0.25)),
         (HIT + 0.5, (0.9, 2.2, 5.0), (0.3, 1.6, -3.0)),
         (HIT + 1.6, (0.0, 6.5, 24.0), (0.0, 3.0, -10.0)),
         (44.6, (-2.0, 3.6, 25.0), (0.0, 4.2, 2.0))],
        fov=lambda t: float(np.interp(t, [HIT, HIT + 1.6, 44.6], [36.0, 50.0, 46.0])),
        aperture=lambda t: float(np.interp(t, [HIT, HIT + 1.0], [0.02, 0.012])), blend=0.15),
    fly([(44.6, (-2.0, 3.6, 25.0), (0.0, 4.2, 2.0)),
         (48.0, (2.2, 3.4, 24.6), (0.0, 4.2, 2.0)),
         (H, (4.0, 3.2, 23.0), (0.0, 4.0, 5.0)),
         (52.4, (-1.5, 3.0, 23.5), (0.0, 4.0, 5.0)),
         (56.0, (0.0, 4.0, 46.0), (0.0, 5.2, -60.0)),
         (60.0, (0.0, 4.3, 54.0), (0.0, 5.4, -60.0))],
        fov=lambda t: float(np.interp(t, [44.6, 52.4, 56.0, 60.0], [46.0, 46.0, 44.0, 44.0])), aperture=0.012,
        blend=1.0),
], blend=0.5, fov=45.0, aperture=0.02, handheld=0.25, min_height=0.4,
    shake=Track([(0.0, 0.55), (3.1, 0.6), (3.6, 0.0), (B, 0.0), (7.0, 0.6), (8.4, 0.25), (9.2, 0.0), (18.4, 0.0),
                 (19.0, 0.5), (D, 0.8), (20.4, 0.2), (21.0, 0.0), (E, 0.0), (E + 0.15, 0.3), (27.4, 0.0),
                 (29.3, 0.0), (TOUCH, 0.25), (30.8, 0.0), (F, 0.0), (F + 0.15, 0.45), (34.4, 0.0), (HIT, 0.0),
                 (HIT + 0.1, 0.6), (43.4, 0.0), (60.0, 0.0)]))

# ------------------------------------------------------------------------------------------------- words
ARCH = dict(span=140.0, height=40.0, z=-60.0)    # a bow over the whole sea after the storm
LIGHTS = arch_points(ARCH["span"], ARCH["height"], ARCH["z"])
_LAB = [e["label"] for e in PW.EXPRESSIONS]

BEADS_G = Beads((0.0, 0.0, 80.0), 5.0, 0.8, 4.6, DROP_LAND + 0.05, 4.4, n=2600, color="#ffe9e2", seed=31)
BEADS_I = Beads((-6.0, 0.0, 46.0), 6.0, 0.8, 5.5, C, 15.2, n=3200, color="#ffeef4", seed=32)

_SPECS = [
    dict(expr="Greeting", pos=(0.0, 2.75, 80.0), width=4.6, t_in=DROP_LAND + 0.15, t_read0=4.3, t_read1=6.95,
         t_out=7.9, arrive="morph", source=BEADS_G, carry="soft", leave="sink"),
    dict(expr="Apology", pos=(12.4, 3.35, 60.0), width=7.0, t_in=STRIKE + 0.5, t_read0=9.6, t_read1=12.3,
         t_out=13.2, arrive="morph", source=BOLT_A, carry="flake", leave="give", to=BODIES["kneel"]),
    dict(expr="Inclusiveness", pos=(-6.0, 3.3, 44.0), width=7.4, t_in=C + 0.3, t_read0=15.0, t_read1=17.7,
         t_out=18.7, arrive="morph", source=BEADS_I, carry="soft", leave="sink"),
    dict(expr="Concession", pos=(0.0, 3.1, WAVE_Z + 0.4), width=8.4, face="fixed", facing=0.0, t_in=D + 0.05,
         t_read0=21.0, t_read1=23.7, t_out=24.7, arrive="reveal",
         gate=lambda P, t: _ss(-0.3, 0.3, P[:, 1] - (WAVE_H(t) - 0.2)), leave="rise"),
    dict(expr="Respect", pos=(-1.9, 2.3, 27.6), width=4.0, t_in=24.6, t_read0=26.0, t_read1=28.7, t_out=29.6,
         arrive="pen", leave="give", to=BODIES["giver"]),
    dict(expr="Consideration", pos=(-24.3, 2.3, 15.6), width=3.5, t_in=TOUCH - 0.2, t_read0=31.8, t_read1=34.5,
         t_out=35.4, arrive="reveal", edge="up", leave="rise"),
    dict(expr="Encouragement", pos=(0.0, 2.5, -3.0), width=4.9, t_in=36.2, t_read0=37.6, t_read1=40.3,
         t_out=41.4, arrive="rays", source=(0.0, 1.62, -1.0), leave="stream",
         to=lambda t: MOTHER.where(t, "palm.R"), star=True),
    dict(expr="Gratitude", pos=(0.0, 4.7, 7.0), width=15.0, t_in=43.6, t_read0=45.3, t_read1=48.0, t_out=49.0,
         arrive="reveal", edge="up", leave="rise"),
    dict(expr="Compliment", pos=(0.0, 3.4, 6.0), width=8.6, t_in=48.3, t_read0=49.6, t_read1=52.2, t_out=53.0,
         arrive="gather", leave="arch", to=tuple(LIGHTS[8])),
]
WORDS = PW.Words(_SPECS, face="camera")

# the arch's lights wake in the nine colours as the finale builds, the last on the loudest moment
_LIT = [51.6 + 0.35 * k for k in range(9)]


class _Window:
    """A point set seen only from t0 to t1 (it costs nothing outside)."""

    def __init__(self, inner, t0, t1):
        self.inner, self.t0, self.t1 = inner, t0, t1
        self.wants_camera = getattr(inner, "wants_camera", False)

    def sample(self, t, cam=None):
        if t < self.t0 or t > self.t1:
            return []
        return self.inner.sample(t, cam) if self.wants_camera else self.inner.sample(t)


def _setup(scene):
    def kc(ps):                           # nothing of the storm inside a word's reading box
        return PW.KeepClear(ps, WORDS, floor=0.0)

    scene.add("sea", kc(Sea(calm_at, STORM, flash, glass=GLASS, warm=WARM)), reflect=False)
    scene.add("rain", kc(Rain(calm_at, RAIN_SPEED, RAIN_AMOUNT)), reflect=False)
    scene.add("glow", kc(Glow(FLASHES)))
    scene.add("bolt_a", kc(BOLT_A))
    scene.add("bolt_b", kc(BOLT_B))
    scene.add("bolt_c", kc(BOLT_C))
    scene.add("bolt_d", kc(BOLT_D))
    scene.add("drop", kc(DROP))
    scene.add("wave", Wave(), mask=Mask("dark", grow=0.22, strength=lambda t: float(_ss(1.2, 3.0, WAVE_H(t)))))
    scene.add("beads_g", kc(BEADS_G))
    scene.add("beads_i", kc(BEADS_I))
    for name, b in BODIES.items():
        b.b.add(scene, name)
    for k, v in Hands(**HANDS).items():
        if k != "flare":
            scene.add("hand_" + k, _Window(v, 28.6, 30.9))
    WORDS.add_to(scene)
    for n in scene.names():               # the words are never mirrored in the water (no text upside down)
        if n.startswith("word "):
            scene._entries[n].reflect = False
    WORDS.check(CAMERA)


P3D = dict(
    camera=CAMERA,
    world=WORDS.world(dict(
        looks=dict(
            storm=dict(base="night", sky_top="#0a0d1a", sky_mid="#1a2036", sky_hor="#2c2d4c", sun_int=0.0,
                       stars=0.0, milky=0.0, clouds=1.0, cloud_speed=4.0, hills=0.0, haze=0.85,
                       haze_color="#2a2e4c", mist=0.45, mist_color="#2c3456", water="#04070f", mirror=0.45,
                       ripple=1.0, dust=0.3, dust_color="#cfe0ff", dust_color2="#9fb4ff", bokeh=0.4),
            pearl=dict(base="night", sky_top="#121a30", sky_mid="#2e3c5e", sky_hor="#5a6a8e", sun_int=0.0,
                       stars=0.0, milky=0.0, clouds=0.9, cloud_speed=0.6, hills=0.0, haze=0.75,
                       haze_color="#4a5a80", mist=0.5, mist_color="#5a6a92", water="#060a14", mirror=0.6,
                       ripple=0.8, dust=0.6, dust_color="#ffe6ee", dust_color2="#cfe0ff", bokeh=0.7),
            wave=dict(base="night", sky_top="#0a1418", sky_mid="#16303a", sky_hor="#5e7e90", sun_int=0.0,
                      stars=0.0, milky=0.0, clouds=1.0, cloud_speed=4.0, hills=0.0, haze=0.8, haze_color="#2e4a58",
                      mist=0.45, mist_color="#2e4a56", water="#03090c", mirror=0.45, ripple=1.0, dust=0.3),
            edge=dict(base="night", sky_top="#0c0e26", sky_mid="#22265a", sky_hor="#6a4e82", sun_int=0.2,
                      sun_el=-6.0, sun_color="#ffb48c", stars=0.0, milky=0.0, clouds=0.9, cloud_speed=3.0,
                      hills=0.0, haze=0.75, haze_color="#4a3a6a", mist=0.4, mist_color="#3c3466", water="#04050f",
                      mirror=0.55, ripple=1.0, dust=0.4),
            eye=dict(base="dawn", sky_top="#060f30", sky_mid="#14265c", sky_hor="#8a5e58", sun_el=-3.0,
                     sun_int=0.35, stars=0.25, milky=0.0, clouds=0.5, hills=0.0, haze=0.5, haze_color="#5a4060",
                     mist=0.25, mist_color="#4a3a60", water="#030816", mirror=1.0, ripple=0.4, rays=0.3,
                     exposure=0.9),
            dawnsea=dict(base="sunrise", sky_top="#0a1440", sky_mid="#30245e", sky_hor="#b4664a", sun_el=2.0,
                         sun_int=0.5, sun_glow=0.45, hills=0.0, clouds=0.4, haze=0.45, haze_color="#7a4a50",
                         mist=0.2, ripple=0.0, mirror=1.0, rays=0.3, exposure=0.82),
            daysea=dict(base="day", hills=0.0, ripple=0.0, mirror=1.0, sun_el=20.0, clouds=0.25),
        ),
        look=[(0.0, "storm"), (C, "pearl", 0.6), (18.4, "wave", 1.0), (E, "edge", 1.2), (F + 1.0, "eye", 2.5),
              (HIT, "dawnsea", 0.0), (52.6, "daysea", 2.6)],
        # the sun rises off to the right of the words, never behind them (cut inside the burst of the hit)
        sun_az=lambda t: SUN_AZ if t < HIT else SUN_AZ + 30.0,
        calm=_engine_calm,
        ripple=_ramp([(0.0, 1.0), (C, 1.0), (C + 0.5, 0.7), (18.4, 1.0), (F, 1.0), (F + 2.5, 0.6), (HIT, 0.6),
                      (HIT + 1.2, 0.0), (60.0, 0.0)]),
        arch=dict(lit=_LIT, colors=tuple(e["color"] for e in PW.EXPRESSIONS), **ARCH),
        light=dict(pos=(0.0, 1.62, -1.3), color="#ffd29a",
                   strength=_ramp([(0.0, 0.0), (34.6, 0.0), (36.4, 0.55), (40.3, 0.55), (HIT, 0.9), (HIT + 0.6, 0.0),
                                   (60, 0.0)]),
                   size=0.5, rays=1.0),
        lights=[dict(pos=_flash_place, color="#cbbcff", strength=lambda t: 1.1 * flash(t), radius=60.0)],
        react=dict(beat=0.3, level=0.25),
    )),
    bursts=[dict(t=DROP_LAND, at=(0.0, 0.3, 80.0), strength=0.6, radius=0.08, color="#ffb39a", rise=0.08, fall=0.5),
            dict(t=STRIKE, at=(12.2, 6.0, 59.4), strength=0.5, radius=0.12, color="#e6dcff", rise=0.05, fall=0.4),
            dict(t=C, strength=0.25, radius=0.25, color="#ffe6ee", rise=0.1, fall=0.6),
            dict(t=TOUCH, at=MEET, strength=0.35, radius=0.08, color="#ffc9a8", rise=0.08, fall=0.5),
            dict(t=30.85, at=(-24.3, 1.0, 15.6), strength=0.45, radius=0.18, color="#fff0e0", rise=0.12, fall=0.45),
            dict(t=HIT, at=(0.46, 0.95, -0.2), strength=0.8, radius=0.16, color="#fff0d0", rise=0.06, fall=0.7),
            dict(t=TITLE_WHOLE - 0.6, at=tuple(LIGHTS[4]), strength=0.25, radius=0.2, color="#fff6e0", rise=0.2,
                 fall=0.9)],
    setup=_setup,
    motion_blur=0.25,
    clear=[dict(box=(0.015, 0.82, 0.485, 0.975), t0=2.6, t1=BADGE_OUT + 1.0, soft=0.03, amount=0.85)],
)
