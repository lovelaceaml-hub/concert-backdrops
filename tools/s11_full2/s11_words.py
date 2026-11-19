"""Song 11 v2 round 7: the words redesigned (Anthony: "The words that appear can definitely enter and be designed
way better with way better effects and thoughts to them").

Every phrase of the core's PHRASE_LIST takes one of four entrances, chosen for its music and its picture:

    light    written by light: a comet sweeps in, writes the letters stroke by stroke (the ink runs from its
             head, the trail glows), then shoots away up and out before the reading starts
    people   formed by people: lights in the nine colours walk in from both sides like the streams of the
             nations, stand under the words and rise into the letters; they leave by scattering back down into
             a crowd below the words ("scatter"), or flow on into the next phrase ("morph")
    blaze    blaze and shockwave: the slam's own flash lands first; the word burns in out of the light about
             0.4 s later (rays from behind, letters white hot cooling to gold), with a ring of light that runs
             out across the sea and a spray of sparks flying outward, away from the letters
    fly      flown through in 3D: large letters come out of the far distance toward the camera, stand ahead
             while they are read, then part like a pair of doors as the camera flies through them

Every phrase has a dark glow behind it while it is read (a soft dark silhouette 2 m behind the letters): the
light behind the text box is held down so the words stay readable on the white stage and the blazing terraces,
and nothing bright crosses them (the reviewer's rule, finding f19). Owned by the words thread; the core keeps
PHRASE_LIST (and its reading windows) and calls specs() and add(). No em dash or en dash anywhere in this file.
"""
import numpy as np

from songs.s11_full2 import *  # noqa: F401,F403
import songs.s11_full2 as H
from p3d.api import Mask

SHOTS = []
STYLES = ("light", "people", "blaze", "fly")
FLY_FAR, FLY_READ0, FLY_READ1 = 170.0, 34.0, 27.0       # metres ahead of the camera: arriving, read, read end
Y_READ = 0.62                                            # where the words are read (0..1 from the bottom)


def _e(a, b, x):
    return float(H._ss(a, b, x))


def _fly_ride(ti, r0, r1, to):
    def ride(t):
        if t < r0:
            a = _e(ti, r0, t)
            d = FLY_READ0 + (FLY_FAR - FLY_READ0) * (1.0 - a) ** 2
        elif t <= r1:
            d = FLY_READ0 + (FLY_READ1 - FLY_READ0) * (t - r0) / max(r1 - r0, 1e-6)
        else:
            l = float(np.clip((t - r1) / max(to - r1, 1e-6), 0.0, 1.0))
            d = 0.6 + (FLY_READ1 - 0.6) * (1.0 - l) ** 2           # the camera flies through the parting letters
        return (0.5, Y_READ, d)
    return ride


def _scatter(name):
    """Where the letters of a 'people' phrase scatter to: a wide crowd of places below the words."""
    rng = np.random.default_rng(len(name) * 31 + 7)
    h = rng.random((2400, 3))

    def to(t):
        w = H.WORDS[name]
        w._build()
        o, r, u, nrm = w.frame(t)
        W = w.W
        x = (h[:, 0] - 0.5) * 2.6 * W
        y = w.ybot - (0.25 + 0.55 * h[:, 1]) * W * 0.45
        z = (h[:, 2] - 0.5) * 0.6 * W
        return (o[None, :] + x[:, None] * r[None, :] + y[:, None] * u[None, :] + z[:, None] * nrm[None, :])
    return to


def specs(plist, width):
    """The particle word settings of every phrase. width(ts, depth, frac): metres across at a frame share."""
    out = []
    prev_leave, prev_name = None, None
    for i, (lines, (ti, r0, r1, to), strong, style, leave) in enumerate(plist):
        if style not in STYLES:
            raise ValueError(f"phrase {i}: style must be one of {STYLES}, got {style!r}")
        name = f"phrase{i:02d}"
        depth = 30.0
        long = max(len(s) for s in lines)
        if strong:
            frac = 0.66 if long > 30 else min(0.66, 0.040 * long + 0.06)
        else:
            frac = min(0.56, 0.026 * long + 0.05)
        y = Y_READ if len(lines) == 1 else 0.60
        if len(lines) == 1 and H.globe_view(r0):
            y = 0.78        # over the Earth: above the glare where the rivers of light meet
        ride = (0.5, y, depth)
        ts = np.linspace(ti, to, 12)
        if style == "fly":
            ride = _fly_ride(ti, r0, r1, to)
            depth, ts, frac = FLY_READ1, np.linspace(r0, r1, 8), min(frac + 0.04, 0.70)
        spec = dict(label="", lines=lines, ride=ride, face="screen", width=width(ts, depth, frac),
                    t_in=ti, t_read0=r0, t_read1=r1, t_out=to, name=name, leave=leave,
                    color=H.GOLD if strong else "#ffe6c0", glow=H.GOLD if strong else "#ffd59a",
                    tint=0.75 if strong else 0.35, bright=1.15 if strong else 1.0,
                    halo=1.3 if strong else 1.0, n=90000 if strong else 60000, reflect=False)
        if strong or style in ("blaze", "fly"):
            spec["font"] = "title"
        if style == "light":
            spec.update(arrive="pen", nib=False, flow=0.09)
        elif style == "people":
            # the walkers' ground: a little under the words on screen, whatever the view
            spec.update(arrive="gather", water=0.0, carry=0.0)
            spec["_ground"] = True
        elif style == "blaze":
            spec.update(arrive="rays", color=H.GOLD, glow="#ffb347", tint=0.8, n=90000)
            if _stage_read(r0, r1):
                # over the white stage the shade is light (see add()): a deeper, warmer gold carries the contrast
                spec.update(color="#f5a02a", glow="#d8661a", tint=1.0, halo=1.0, bright=1.0)
        else:
            spec.update(arrive="reveal", edge="out", soft=0.10, edge_glow=2.2)
        if prev_leave == "morph":
            spec.update(arrive="morph", source=prev_name)
        if leave == "scatter":
            spec.update(leave="give", to=_scatter(name))
        if leave == "doors":
            spec.update(swing=95.0, inward=False)
        out.append(spec)
        prev_leave, prev_name = leave, name
    return out


def fix_ground(words, specs_):
    """The walkers of a 'people' phrase walk on a floor a little under the words (in the word's own frame
    at the start of its reading, so it suits the globe and the mountain alike)."""
    for w, s in zip(words, specs_):
        if not s.get("_ground"):
            continue
        cam = w._cam(w.t_read0)
        o, r, u, nrm = w.frame(w.t_read0, cam)
        w._build()
        w.opts["water"] = float(o[1] + w.ybot - 0.55 * w.W * 0.35)


def _style(i):
    return H.PHRASE_LIST[i][3]


def _stage_read(r0, r1):
    ts = np.linspace(r0, r1 - 0.1, 7)          # (a reading often ends right on the next cut)
    return sum(H.shot_kind(float(x)) == "stage" for x in ts) >= 5


def _on_stage(i):
    """True when phrase i is read over the white stage (the choir and orchestra shots)."""
    a, b, c, d = H.PHRASE_LIST[i][1]
    return _stage_read(b, c)


# ------------------------------------------------------------------------------------------- companions
class _Shade:
    """The dark glow behind a phrase: its letters (a share of them), 2 m behind, never drawn as light; their
    silhouette, grown and softened, holds the light behind the text box down while the phrase is read."""
    wants_camera = True

    def __init__(self, word, k=1.0, size=0.10, veil=False):
        self.w = word
        self.sub = None
        self.k, self.size, self.veil = float(k), float(size), bool(veil)

    def gain(self, t):
        return 1.0 if self.veil else 0.0      # the veil is painted, never light (paint_light 0)

    def strength(self, t):
        w = self.w
        # behind the letters only once they are (nearly) whole, gone early in the leaving (a flown-through
        # word comes right up to the lens: its shade must not), the comet's writing is shaded as it goes
        a0 = w.t_in if w.arrive == "pen" else max(w.t_in, w.t_read0 - 0.3)
        return self.k * _e(a0, w.t_read0, t) * (1.0 - _e(w.t_read1, w.t_read1 + 0.3, t))

    def sample(self, t, cam=None):
        w = self.w
        if self.strength(t) <= 0.001:
            return None
        tg = w.targets(t, cam)
        if self.sub is None:
            self.sub = np.arange(0, len(tg), max(len(tg) // 1500, 1))
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
        p = eye[None, :] + d * ((dist + 2.0) / np.maximum(dist, 1e-3))     # 2 m further along each ray
        if self.veil:       # a painted veil: dims only what lies behind the letters, not every dark mask in view
            return [dict(pos=p.astype(np.float32), size=np.full(len(p), self.size * w.metres_per_em(), np.float32),
                         color=np.array([0.03, 0.018, 0.045], np.float32), alpha=0.10 * self.strength(t),
                         kind="disc", paint=1.0, paint_light=0.0, emit=1.0, dof=0.0, fog=0.0, streak=0.0)]
        return [dict(pos=p.astype(np.float32), size=np.full(len(p), self.size * w.metres_per_em(), np.float32),
                     color=np.zeros(3, np.float32), alpha=1.0, kind="soft")]


class _Shock:
    """Blaze: the ring of light across the sea and a spray of sparks flying out from the word, on the hit."""
    wants_camera = True

    def __init__(self, word, hit, seed):
        self.w, self.hit = word, float(hit)
        r = np.random.default_rng(seed)
        self.h = r.random((520, 4))
        self.ang = np.linspace(0.0, 2.0 * np.pi, 720, endpoint=False)

    def sample(self, t, cam=None):
        dt = t - self.hit
        if dt < 0.0 or dt > 2.4:
            return None
        w = self.w
        w._build()
        cam = w._cam(t, cam)
        o, r, u, nrm = w.frame(t, cam)
        W = w.W
        out = []
        gold, white = lin(H.GOLD), lin(H.WHITE)
        # the ring over the sea: from under the words outward, fast then slowing, fading as it goes
        if not H.globe_view(t) and float(cam.pos[1]) < 400.0:
            c = np.array([o[0], 0.25, o[2]])
            rad = 4.0 + 260.0 * (1.0 - np.exp(-dt / 0.55))
            a = (1.0 - _e(0.15, 2.4, dt)) * _e(0.0, 0.05, dt)
            p = np.stack([c[0] + rad * np.cos(self.ang), np.full_like(self.ang, c[1]), c[2] + rad * np.sin(self.ang)], 1)
            sz = 0.6 + 0.012 * rad
            out.append(dict(pos=p, size=np.full(len(p), sz * 3.0), color=gold, alpha=0.10 * a, kind="soft", emit=1.5))
            out.append(dict(pos=p, size=np.full(len(p), sz), color=white * 0.6 + gold * 0.4, alpha=0.55 * a,
                            kind="spark", emit=2.5, twinkle=0.4))
        # the halo ring in the word's own plane, starting outside the letters so it never crosses them
        a2 = (1.0 - _e(0.0, 0.9, dt)) * _e(0.0, 0.04, dt)
        if a2 > 0.01:
            rr = (0.62 + 1.6 * (1.0 - np.exp(-dt / 0.35))) * W
            q = (o[None, :] - nrm[None, :] * 1.0 + rr * np.cos(self.ang)[:, None] * r[None, :]
                 + 0.55 * rr * np.sin(self.ang)[:, None] * u[None, :])
            out.append(dict(pos=q, size=np.full(len(q), 0.006 * W), color=white * 0.5 + gold * 0.5, alpha=0.6 * a2,
                            kind="spark", emit=2.0))
        # sparks: thrown outward from the word's edge, gone in a second
        h = self.h
        a3 = (1.0 - _e(0.1, 1.1, dt)) * _e(0.0, 0.03, dt)
        if a3 > 0.01:
            ang = h[:, 0] * 2.0 * np.pi
            d0 = np.stack([np.cos(ang), 0.45 * np.sin(ang)], 1)
            d0 /= np.linalg.norm(d0, axis=1, keepdims=True)
            dist = (0.58 + (0.9 + 1.6 * h[:, 1]) * (1.0 - np.exp(-dt / 0.4))) * W
            dist = dist * np.maximum(np.abs(d0[:, 0]), 0.6)
            x, y = d0[:, 0] * dist, d0[:, 1] * dist - 0.25 * W * dt * dt
            q = (o[None, :] + x[:, None] * r[None, :] + y[:, None] * u[None, :]
                 + ((h[:, 2] - 0.5) * 0.4 * W)[:, None] * nrm[None, :])
            out.append(dict(pos=q, size=(0.003 + 0.004 * h[:, 3]) * W, color=white * 0.4 + gold * 0.6,
                            alpha=a3, kind="spark", emit=2.6, twinkle=0.6, seed=h[:, 3]))
        return out


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
                 sparks=True, seed=hash(word.name) % 97)


def add(scene):
    """The words' companions (the core's _setup runs this after H.WORDS exists)."""
    fix_ground(H.WORDS, H._SPECS)
    for i, w in enumerate(H.WORDS):
        st = _style(i)
        if _on_stage(i):
            # round 7 (task: "Devotion" at 1:46, its dark glow read as a rounded plate on the white stage): over
            # the stage the shade hugs the letters (smaller, tighter, much softer edge) and holds the light down
            # by about half, a dark breath round the word rather than a plate
            # (the engine shares one dark strength per frame among all dark masks: the choir's own silhouettes,
            # off in the wide stage shots, darken with it, which is what read as a plate; so the shade stays light)
            # so here the shade is a soft painted veil instead of a dark mask
            sh = _Shade(w, k=1.0, size=0.30, veil=True)
            mask = None
        else:
            sh = _Shade(w)
            mask = Mask("dark", strength=sh.strength, grow=0.8 if st in ("blaze", "fly") else 0.5, soft=4.0)
        if mask is None:
            scene.add(f"word shade {w.name}", sh, reflect=False)
        else:
            scene.add(f"word shade {w.name}", sh, reflect=False, mask=mask)
        if st == "light":
            scene.add(f"word comet {w.name}", _writer(w), reflect=False)
        elif st == "blaze":
            scene.add(f"word shock {w.name}", _Shock(w, w.t_in, 11 + i), reflect=False)
