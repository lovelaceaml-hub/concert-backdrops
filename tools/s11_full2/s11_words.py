"""Song 11 v2: the words (round 8: the approved promo's word style; Anthony: "The text looks terrible.").

Every phrase of the core's PHRASE_LIST shows the promo look: white letter cores with a crisp edge and a
coloured neon glow (one of the nine colours per phrase, PHRASE_GLOW), the promo's italic, large, in the upper
middle of the frame. Nothing dark is drawn behind the words: the core calms the scene behind each phrase
instead (P3D "clear": the frame region the words occupy, feathered, everything behind it at about half, and
comets kept out of it). The style field of PHRASE_LIST picks a graceful entrance:

    light    written by light: a comet writes the letters stroke by stroke, as in the promo
    people   glitter: flakes of light come down and settle into the letters
    blaze    a subtle warm burn out of the slam's light, 0.4 s after the flash
    fly      a soft sweep of light reveals the letters from the left

and every phrase leaves by dissolving upward into sparkles. The core keeps PHRASE_LIST (its 5-field tuples and
reading windows) and calls specs() and add(). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H

SHOTS = []
STYLES = ("light", "people", "blaze", "fly")
Y_READ = 0.62                                            # where the words are read (0..1 from the bottom)


def _e(a, b, x):
    return float(H._ss(a, b, x))


# Round 8 (Anthony: "The text looks terrible."; he chose the approved promo's word style): white letter cores with
# a crisp edge and a coloured neon glow, one of the nine colours per phrase, the promo's italic, larger, set in
# the upper middle on a calm darkened region (core: P3D "clear"), no dark plate behind. Entrances simplified to
# graceful promo-like ones; every phrase dissolves upward into sparkles.
NEON = dict(crimson="#EA5A5E", gold="#F2B25E", sky="#62B2FA", lavender="#9E6AF6", rose="#EE62A6",
            violet="#667AF6", green="#5ABA5A")
# the neon glow round the white cores: the same hues, deeper and more saturated so they read as colour
NEON_GLOW = dict(crimson="#ff1438", gold="#ff8a00", sky="#1478ff", lavender="#7a2cff", rose="#ff2288",
                 violet="#3a3cff", green="#14c040")
PHRASE_GLOW = ["gold", "sky", "lavender", "gold", "crimson", "violet", "sky", "gold", "lavender",
               "gold", "crimson", "rose", "gold", "rose", "crimson", "lavender", "gold", "sky"]
# style (PHRASE_LIST field 4, kept for the other threads) -> the promo-like entrance
ARRIVE = dict(light="pen", people="shaft", blaze="rays", fly="reveal")


def specs(plist, width):
    """The particle word settings of every phrase. width(ts, depth, frac): metres across at a frame share."""
    out = []
    for i, (lines, (ti, r0, r1, to), strong, style, leave) in enumerate(plist):
        if style not in STYLES:
            raise ValueError(f"phrase {i}: style must be one of {STYLES}, got {style!r}")
        name = f"phrase{i:02d}"
        depth = 30.0
        long = max(len(s) for s in lines)
        if strong:
            frac = min(0.72, 0.05 * long + 0.12)          # "Devotion" about half the frame, the grand ones wide
        else:
            frac = min(0.64, 0.032 * long + 0.10)
        y = Y_READ if len(lines) == 1 else 0.63
        if len(lines) == 1 and H.globe_view(r0):
            y = 0.76        # over the Earth: above the globe, on the dark sky
        ride = (0.5, y, depth)
        ts = np.linspace(ti, to, 12)
        key = PHRASE_GLOW[i % len(PHRASE_GLOW)]
        hexc, hexg = NEON[key], NEON_GLOW[key]
        spec = dict(label="", lines=lines, ride=ride, face="screen", width=width(ts, depth, frac),
                    t_in=ti, t_read0=r0, t_read1=r1, t_out=to, name=name, leave="rise",
                    color=hexc, glow=hexg, tint=0.22, bright=1.2 if strong else 1.1,
                    halo=4.6 if strong else 4.0, sparkle=1.2, n=110000 if strong else 80000, reflect=False)
        if _bright(r0, r1):
            # over a bright scene (the lit terraces, the white stage): a purer white core, a brighter word
            spec.update(tint=0.12, bright=1.3 if strong else 1.2)
        arr = ARRIVE[style]
        if arr == "pen":
            spec.update(arrive="pen", nib=False, flow=0.09)
        elif arr == "rays":
            spec.update(arrive="rays")                     # a subtle warm burn on the slams, 0.4 s after the flash
        elif arr == "reveal":
            spec.update(arrive="reveal", edge="right", soft=0.18, edge_glow=1.6)    # a soft sweep of light
        else:
            spec.update(arrive="shaft")                    # glitter flakes come down and settle into the letters
        out.append(spec)
    return out


def _bright(r0, r1):
    """A phrase read over a bright scene: any local shot from the first slam on (not the Earth, not space)."""
    return r0 >= 82.0 and not H.globe_view(0.5 * (r0 + r1))


def _style(i):
    return H.PHRASE_LIST[i][3]


def _writer(word):
    """The comet that writes a 'light' phrase: in from the upper left, along the writing, away up right."""
    word._build()
    W = word.W
    ti, r0 = word.t_in, word.t_read0

    def head(t):
        if t <= ti:
            o, r, u, nrm = word.frame(t)
            p1 = word.pen(ti)
            p0 = p1 - r * (0.85 * W) + u * (0.55 * W) + nrm * (0.25 * W)
            a = _e(ti - 0.55, ti, t)
            m = p0 + (p1 - p0) * a
            return m + u * (0.12 * W * np.sin(np.pi * a))
        if t <= r0:
            return word.pen(t)
        o, r, u, nrm = word.frame(t)
        a = float(np.clip((t - r0) / 0.4, 0.0, 1.0))
        return word.pen(r0) + (r * (0.55 * W) + u * (0.75 * W) + nrm * (0.2 * W)) * (a * a)

    return Comet(head, "#ffe2a8", ti - 0.55, r0 + 0.4, trail=0.5, width=0.012 * W, bright=0.9, fade=0.25, n=70,
                 sparks=True, seed=hash(word.name) % 97, clear=False)


class _GlyphShadow:
    """Round 8 (Anthony: "The texts should not have a box covering up what's behind it"): a tight glow-shadow
    hugging each letter's own shape, a few pixels wide, painted (it darkens only what lies right behind the
    strokes, never a region, and never touches anyone else's dark mask). No box, band or panel."""
    wants_camera = True

    def __init__(self, word, k=1.0, size=0.055):
        self.w, self.k, self.size = word, float(k), float(size)
        self.sub = None

    def gain(self, t):
        return 1.0

    def strength(self, t):
        w = self.w
        a0 = w.t_in if w.arrive == "pen" else max(w.t_in, w.t_read0 - 0.3)
        return self.k * _e(a0, w.t_read0, t) * (1.0 - _e(w.t_read1, w.t_read1 + 0.3, t))

    def sample(self, t, cam=None):
        k = self.strength(t)
        if k <= 0.001:
            return None
        w = self.w
        tg = w.targets(t, cam)
        if self.sub is None:
            self.sub = np.arange(0, len(tg), max(len(tg) // 6000, 1))
        sub = self.sub
        if w.arrive == "pen" and t < w.t_read0:          # only behind what the comet has written so far
            a = (t - w.t_in) / max(w.t_read0 - w.t_in, 1e-6)
            sub = sub[(0.04 + 0.88 * w.worder[sub]) < a]
            if not len(sub):
                return None
        cam = w._cam(t, cam)
        eye = np.asarray(cam.pos, np.float32)
        d = tg[sub] - eye[None, :]
        dist = np.linalg.norm(d, axis=1, keepdims=True)
        p = eye[None, :] + d * ((dist + 1.0) / np.maximum(dist, 1e-3))     # 1 m behind each stroke
        return [dict(pos=p.astype(np.float32), size=np.full(len(p), self.size * w.metres_per_em(), np.float32),
                     color=np.array([0.02, 0.012, 0.035], np.float32), alpha=min(0.16 * k, 0.6), kind="disc", paint=1.0,
                     paint_light=0.0, emit=1.0, dof=0.0, fog=0.0, streak=0.0)]


def add(scene):
    """The words' companions (the core's _setup runs this after H.WORDS exists). Round 8: no box, plate or
    veil behind a phrase; a tight glow-shadow follows each letter's shape; the writing comet stays for the pen
    entrances."""
    for i, w in enumerate(H.WORDS):
        b = _bright(w.t_read0, w.t_read1)
        # in bright frames only: a slightly stronger, slightly wider shadow hugging the letter edges
        scene.add(f"word glyph shadow {w.name}", _GlyphShadow(w, k=2.4 if b else 1.0, size=0.075 if b else 0.055),
                  reflect=False)
        if _style(i) == "light":
            scene.add(f"word comet {w.name}", _writer(w), reflect=False)
