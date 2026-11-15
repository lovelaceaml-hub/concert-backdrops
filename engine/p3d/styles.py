"""Style presets for the people of the 3D layer: one call gives a person (or a face) in a finished artistic look
(engine/UPGRADE-HOWTO.md, section Y). Built on the bodies, looks and effects of engine/p3d/body.py,
engine/p3d/effects.py and engine/p3d/looks.py, the faces and hair of engine/p3d/faces.py and the pieces of
engine/p3d/stylekit.py.

    from p3d import styles as ST

    def build(scene):
        ST.add(scene, "gold_glitter", name="hero", at=(0, 0), facing=30, sky="day", t=4.0, show=(2, 10))
        ST.add(scene, "spark_profile", name="face", at=(3, 1.6, 0), facing=-90, height=0.6)

Every preset takes:
  name      the scene name of its main part (its other parts are name + "_hair", name + "_glow", ...)
  sky       "night" (default) or "day": the palette and the way the figure is drawn (light alone on a night
            sky; on a bright sky the figure is also painted or given a dark silhouette, so it never washes out)
  show      (t_in, t_out); fade: seconds; seed: another person
  t         when the preset's own effect starts (shatter, dissolve, butterflies leaving...); dur: how long
  color, color2, ink   to change the palette (display hex); bright: overall brightness
  and the keys of the figure it is made of: for a body (Body of engine/p3d/body.py) shape, at, facing,
  motion, gesture, garment, veil, hair, points, scale, wind, light, plus body=dict(...) for any other Body key;
  for a face (Profile of engine/p3d/faces.py) shape, at (the middle of the head), facing, height, tilt, turn,
  hair, features, plus face=dict(...) for any other Profile key.
add() returns a Styled: .main (the Body or Profile), .parts (scene name -> point set), .where(t, place).

The presets (see STYLES, and section Y for what each looks like and its limits):
  constellation, spark_profile, sky_window, gold_glitter, ember_dancer, ash_dissolve, mist_figure,
  star_silhouette, glass_shatter, butterflies, dark_silhouette, nebula_figure, nebula_profile,
  glitter_profile, constellation_profile

Faces are for ordinary people only. Heavenly Mother is never shown with a face: give her a body preset seen
from behind (facing away from the camera) or her hands, never a *_profile preset.
"""
import numpy as np

from . import faces as FC
from . import stylekit as K
from .api import Mask, lin, show
from .body import Body, _Shape
from track import Track

DAY = ("day", "bright", "light")


class Styled:
    """What a preset made: .main (the Body or Profile), .parts (scene name -> point set), .style, .sky."""

    def __init__(self, style, sky, main, parts):
        self.style, self.sky, self.main, self.parts = style, sky, main, parts

    def where(self, t, place="chest"):
        """A named place of the main figure (Body.where or Profile.where names)."""
        if isinstance(self.main, FC.Profile):
            place = {"chest": "heart", "head": "head"}.get(place, place)
        return self.main.where(t, place)

    def __getitem__(self, k):
        return self.parts[k]


def _day(sky):
    return str(sky) in DAY


def _pick(kw, key, night, day, sky):
    v = kw.pop(key, None)
    return v if v is not None else (day if _day(sky) else night)


_BODY_KEYS = ("shape", "height", "at", "facing", "motion", "gesture", "garment", "veil", "hair", "points", "scale",
              "wind", "light", "detail", "stoop", "frame", "part", "hand", "gust", "size")
_FACE_KEYS = ("shape", "at", "facing", "height", "tilt", "turn", "hair", "features", "points", "garment", "breathe",
              "stream", "eye_glow", "size")


def _split(kw, keys):
    out = {k: kw.pop(k) for k in keys if k in kw}
    return out


def _body(kw, sky, look, color, color2, effects=(), **defaults):
    """A Body from the preset's defaults and the caller's keys."""
    bk = dict(defaults)
    bk.update(_split(kw, _BODY_KEYS))
    bk.update(kw.pop("body", None) or {})
    bk.setdefault("shape", "woman")
    bk["look"] = bk.get("look", look)
    bk["color"] = color
    bk["color2"] = color2
    for k in ("show", "fade", "seed"):
        if k in kw:
            bk[k] = kw[k]
    bk["bright"] = bk.get("bright", 1.0) * float(kw.get("bright", 1.0))
    bk["effects"] = list(effects) + list(kw.pop("effects", None) or [])
    return Body(**bk)


def _face(kw, look, color, color2, **defaults):
    fk = dict(defaults)
    fk.update(_split(kw, _FACE_KEYS))
    fk.update(kw.pop("face", None) or {})
    for k in ("show", "fade", "seed"):
        if k in kw:
            fk[k] = kw[k]
    fk["bright"] = fk.get("bright", 1.0) * float(kw.get("bright", 1.0))
    fk.setdefault("look", look)
    fk["color"] = color
    fk["color2"] = color2
    return FC.Profile(**fk)


def _ink(c):
    """A display hex as the light that the finished picture shows as exactly that colour (paint, flat fills)."""
    return np.asarray(show(c), np.float64) if isinstance(c, str) else np.asarray(c, np.float64)


def _flat(source, ink, soft=1.6, grow=0.006, strength=1.0):
    """A silhouette filled with one exact colour: a dark painted shape on any sky."""
    return Mask("sky", sky="flat", color=ink, source=source, soft=soft, grow=grow, strength=strength)


def _dark(source, grow=0.006, soft=2.0, strength=0.95):
    return Mask("dark", source=source, grow=grow, soft=soft, strength=strength)


def _t(kw, default):
    v = kw.pop("t", None)
    return float(default if v is None else v)


def _target(fig, place):
    return lambda t: fig.where(t, place)


def _hair_for_body(scene, name, body, kw, sky, color, color2, ink, **defaults):
    """Long flowing hair (a mass of locks) on a Body that has hair=False."""
    hk = dict(defaults)
    hk.update(kw.pop("flowing_hair", None) or {})
    hk.setdefault("color", color)
    hk.setdefault("color2", color2)
    hk.setdefault("ink", ink)
    hk.setdefault("look", "ink" if _day(sky) else "glow")
    hk.setdefault("seed", float(kw.get("seed", 1.0)))
    hair = FC.Hair(FC.BodyHead(body), **hk)
    scene.add(name + "_hair", hair)
    return hair


# ================================================================================================ the presets
def constellation(scene, name, sky, kw):
    """p01: a body of stars joined by fine lines, brighter toward the light, specks drifting off."""
    day = _day(sky)
    color = _pick(kw, "color", "#fff2dc", "#22357e", sky)
    color2 = _pick(kw, "color2", "#bcd8ff", "#c38a1e", sky)
    detail = kw.pop("detail_track", None)
    look = dict(name="plexus", share=0.075, links=3, reach=0.10, haze=0.35, bright=1.15 if not day else 1.0)
    if detail is not None:
        look["detail"] = detail
    at = kw.get("at", (0.0, 0.0))
    fc = float(kw.get("facing", 90.0))
    a = np.radians(fc)
    light = kw.pop("light", None)
    if light is None:
        p = np.array([at[0], 0.0, at[-1]], np.float64)
        light = (p[0] + np.sin(a) * 0.9, 2.4, p[2] + np.cos(a) * 0.9)
    b = _body(kw, sky, look, color, color2, light=light, points=70000,
              effects=[dict(kind="shed", n=1800, life=4.5, speed=0.10, rise=0.06, spread=0.08, size=0.8,
                            color=color2 if not day else color)],
              gesture=[(-1.0, 1e6, "look_up", dict(amount=16))])
    parts = {}
    if day:
        main = K.Dressed(b, paint=1.0, paint_light=0.55)
    else:
        main = b
    scene.add(name, main)
    parts[name] = main
    sp = K.Sparkles(_target(b, "chest"), box=(0.9, 1.0, 0.5), n=500, stars=22, size=0.035,
                    color=color if not day else "#2a3a80", color2=color2, bright=0.8, paint=1.0 if day else 0.0,
                    show=kw.get("show"), seed=float(kw.get("seed", 1.0)))
    scene.add(name + "_stars", sp)
    parts[name + "_stars"] = sp
    return Styled("constellation", sky, b, parts)


def spark_profile(scene, name, sky, kw):
    """p06: a face in profile whose edge is traced by fine sparks, embers streaming off the top of the head,
    the inside dark (a dark silhouette at night, a deep navy painted one on a day sky)."""
    day = _day(sky)
    color = _pick(kw, "color", "#ff8a2a", "#ff9a30", sky)
    color2 = _pick(kw, "color2", "#ffd27a", "#ffe1a0", sky)
    ink = _pick(kw, "ink", "#0a0d18", "#1b2238", sky)
    kw.setdefault("hair", dict(look="sparks", length=1.25, locks=55, wind=(-1.0, 0.35), alpha=0.8))
    prof = _face(kw, "sparks", color, color2, height=0.40, tilt=8.0, eye_glow=kw.pop("eye_glow", 0.0),
                 stream=dict(n=2600, dir=(0.30, 1.0), speed=0.32, life=3.4))
    src = prof.shape_set()
    mk = _flat(src, ink, soft=1.6) if day else _dark(src, grow=0.0, soft=1.6)
    scene.add(name, prof, mask=mk)
    return Styled("spark_profile", sky, prof, {name: prof})


def sky_window(scene, name, sky, kw):
    """p07, flat: the body is a window onto a sunrise (night) or a cloud sky (day), birds leaving it."""
    day = _day(sky)
    color = _pick(kw, "color", "#ffd9b0", "#ffffff", sky)
    color2 = _pick(kw, "color2", "#ffffff", "#ffe6c8", sky)
    t0 = _t(kw, 1.0)
    fill = kw.pop("fill", "clouds" if day else "sunrise")
    birds = kw.pop("birds", "#22242e" if day else "#ffe9c4")
    fx = [dict(kind="birds", t=t0, dur=2.6, n=38, color=birds, dir=kw.pop("birds_dir", (1.0, 0.45, 0.2)),
               speed=1.6, size=0.07)] if birds else []
    b = _body(kw, sky, dict(name="window", bright=0.8), color, color2, effects=fx, facing=90.0, points=60000)
    b.add(scene, name, mask=dict(sky=fill, edge=0.55 if not day else 0.35))
    return Styled("sky_window", sky, b, {name: b})


def gold_glitter(scene, name, sky, kw):
    """p08: a figure of gold glitter, dark grains among bright ones, blowing apart from one side into flying
    glitter (on a day sky the grains are also painted, so the figure is gold and bronze, never washed out)."""
    day = _day(sky)
    color = _pick(kw, "color", "#e0a245", "#b07a2a", sky)
    color2 = _pick(kw, "color2", "#fff0c8", "#ffe7b0", sky)
    t0 = _t(kw, 1.0)
    dur = float(kw.pop("dur", 6.0))
    fc = float(kw.get("facing", 0.0))
    a = np.radians(fc)
    side = kw.pop("dir", (np.cos(a), 0.25, -np.sin(a)))
    fx = [dict(kind="disperse", t=t0, dur=dur, share=float(kw.pop("share", 0.45)), dir=side, speed=0.7,
               sprites=(("soft", 0.45, 1.3, 0.9), ("spark", 0.04, 1.6, 1.6))),
          dict(kind="shed", n=3000, life=3.0, speed=0.25, dir=side, rise=0.05)]
    b = _body(kw, sky, dict(name="glitter", glints=0.0016, bright=1.15), color, color2, effects=fx, points=95000,
              facing=0.0, garment="dress")
    if day:
        main = K.Dressed(b, paint=0.85, paint_light=1.0)
    else:
        main = b
    scene.add(name, main)
    sp = K.Sparkles(_target(b, "chest"), box=(0.9, 1.0, 0.6), n=700, stars=26, size=0.04, color=color2,
                    color2=color, bright=0.9, paint=0.6 if day else 0.0, show=kw.get("show"))
    scene.add(name + "_glitter", sp)
    return Styled("gold_glitter", sky, b, {name: main, name + "_glitter": sp})


def ember_dancer(scene, name, sky, kw):
    """p04: a dancer whose body is embers, bursting apart behind her into a long stream of orange sparks. On a day
    sky the body is a deep ember red silhouette with glowing grains, the stream painted dark red and gold."""
    day = _day(sky)
    color = _pick(kw, "color", "#ff7a1e", "#ff8a2a", sky)
    color2 = _pick(kw, "color2", "#ffd36a", "#ffcf6a", sky)
    ink = _pick(kw, "ink", "#2a0d06", "#6a2208", sky)
    t0 = _t(kw, 0.6)
    dur = float(kw.pop("dur", 5.0))
    fc = float(kw.get("facing", 90.0))
    a = np.radians(fc)
    back = kw.pop("dir", (-np.sin(a), 0.15, -np.cos(a)))
    ways = None
    if day:
        ways = [dict(paint=1.0, paint_light=0.0, color=_ink(ink)), dict(paint=0.0)]
    fx = [dict(kind="disperse", t=t0, dur=dur, share=float(kw.pop("share", 0.55)), dir=back, speed=1.3,
               spread=0.25, turb=0.5, sprites=(("soft", 0.55, 1.5, 1.0), ("spark", 0.06, 1.4, 2.0)),
               color=color, color2=color2, batch=ways)]
    hair = kw.pop("hair", None)
    b = _body(kw, sky, dict(name="glitter", glints=0.003, bright=1.2 if not day else 0.9), color, color2, effects=fx,
              motion=kw.pop("motion", "dance"), garment="dress", hair=False if hair is None else hair, points=80000,
              facing=fc)
    parts = {}
    if day:
        b.add(scene, name, mask=_flat(_Shape(b), _ink(ink), soft=1.6, grow=0.004))
    else:
        b.add(scene, name, mask=False)
    parts[name] = b
    if hair is None:
        parts[name + "_hair"] = _hair_for_body(scene, name, b, kw, sky, color, color2, ink, length=1.6, locks=60,
                                               wind=(-1.0, 0.45), look="ink" if day else "sparks", alpha=0.9)
    return Styled("ember_dancer", sky, b, parts)


def ash_dissolve(scene, name, sky, kw):
    """p03: a figure crumbling into ash: dark flakes tearing off and blowing away, red embers glowing in the
    breaks. Day or mist: a charcoal silhouette; night: grey ash lit from behind by a soft glow."""
    day = _day(sky)
    color = _pick(kw, "color", "#ff4a2a", "#ff3a1a", sky)
    color2 = _pick(kw, "color2", "#ffb07a", "#ff9060", sky)
    ink = _pick(kw, "ink", "#0b0c10", "#24272e", sky)
    ash = _pick(kw, "ash", "#9aa0aa", "#2a2d33", sky)
    t0 = _t(kw, 0.5)
    dur = float(kw.pop("dur", 5.0))
    fc = float(kw.get("facing", 0.0))
    a = np.radians(fc)
    wind = kw.pop("dir", (np.cos(a) * 1.0, 0.35, -np.sin(a) * 1.0))
    flakes = [dict(paint=1.0, paint_light=0.0, color=_ink(ash))] if day else [dict(color=lin(ash))]
    fx = [dict(kind="dissolve", t=t0, dur=dur, share=float(kw.pop("share", 0.6)), order="down", rise=0.35,
               speed=0.9, dir=wind, turb=0.45, swirl=0.15,
               sprites=(("flake", 0.10, 5.5, 1.0), ("flake", 0.08, 2.5, 1.0)), batch=flakes),
          dict(kind="disperse", t=t0 + 0.3, dur=dur, share=0.25, dir=wind, speed=0.5,
               sprites=(("soft", 0.30, 1.2, 1.6),), color=color, color2=color2)]
    b = _body(kw, sky, dict(name="glitter", bright=0.35, glints=0.0005), color, color2, effects=fx, points=70000,
              garment="coat", shape=kw.pop("shape", "man"), facing=fc)
    parts = {name: b}
    if day:
        b.add(scene, name, mask=_flat(_Shape(b), _ink(ink), soft=1.8))
    else:
        b.add(scene, name, mask=_dark(_Shape(b), grow=0.004, soft=2.0, strength=1.0))
        g = K.Backdrop(_target(b, "chest"), radius=1.3, behind=3.0, color="#ffb08a", color2="#6f7fa8", bright=1.0,
                       show=kw.get("show"))
        scene.add(name + "_glow", g)
        parts[name + "_glow"] = g
    return Styled("ash_dissolve", sky, b, parts)


def mist_figure(scene, name, sky, kw):
    """p09: a small figure of fine sparkling light standing in a wide field of glittering mist, warm light on
    one side and cool on the other. Frame it far: the figure a fifth of the picture high or less."""
    day = _day(sky)
    color = _pick(kw, "color", "#ffe2b8", "#f0c890", sky)
    color2 = _pick(kw, "color2", "#ffffff", "#fff4e0", sky)
    b = _body(kw, sky, dict(name="glitter", bright=1.3, glints=0.004, size=1.2), color, color2, points=50000,
              facing=180.0, garment="dress",
              effects=[dict(kind="shed", n=2500, life=4.0, speed=0.15, rise=0.12, spread=0.2)])
    main = K.Dressed(b, paint=0.5, paint_light=1.0) if day else b
    scene.add(name, main)
    at = kw.get("at", (0.0, 0.0))
    c = np.array([at[0], 1.0, at[-1]], np.float64)
    mist = K.GlitterMist(c, size=tuple(kw.pop("field", (16.0, 3.4, 12.0))), n=int(kw.pop("n_mist", 30000)),
                         color="#ffcf8a" if not day else "#e8b070", color2="#b8d0ff" if not day else "#9ab4e0",
                         toward=kw.pop("toward", (1.0, 0.0)), bright=0.9 if not day else 0.7, show=kw.get("show"))
    scene.add(name + "_mist", mist)
    return Styled("mist_figure", sky, b, {name: main, name + "_mist": mist})


def star_silhouette(scene, name, sky, kw):
    """A silhouette filled with a starry night, a fine edge of light, stars scattered round it (p02's star-filled
    figure). Strongest on a pastel day sky; at night the edge and a soft glow behind carry it."""
    day = _day(sky)
    color = _pick(kw, "color", "#cfd8ff", "#ffe8c8", sky)
    color2 = _pick(kw, "color2", "#ffffff", "#ffffff", sky)
    tint = kw.pop("tint", (1.25, 0.95, 1.6))
    b = _body(kw, sky, dict(name="window", bright=1.0, stars=0.02), color, color2, points=60000, facing=90.0)
    b.add(scene, name, mask=dict(sky="stars", edge=0.7, tint=tint))
    parts = {name: b}
    sp = K.Sparkles(_target(b, "chest"), box=(0.9, 1.1, 0.5), n=400, stars=40, size=0.05, color="#fff2d8",
                    color2="#ffc8a8", bright=1.0, show=kw.get("show"))
    scene.add(name + "_stars", sp)
    parts[name + "_stars"] = sp
    if not day:
        g = K.Backdrop(_target(b, "chest"), radius=1.2, behind=3.0, color="#8a7ad8", color2="#2a3a80", bright=0.8,
                       show=kw.get("show"))
        scene.add(name + "_glow", g)
        parts[name + "_glow"] = g
    return Styled("star_silhouette", sky, b, parts)


def glass_shatter(scene, name, sky, kw):
    """p05: a figure that shatters into shards of glass flying off one side: dark pieces of the silhouette
    with bright edges and a sweep of reflection (day), or glassy pieces of light (night)."""
    day = _day(sky)
    color = _pick(kw, "color", "#d8ecff", "#ffffff", sky)
    color2 = _pick(kw, "color2", "#ffffff", "#cfe6ff", sky)
    ink = _pick(kw, "ink", "#0c0f16", "#14191e", sky)
    t0 = _t(kw, 0.8)
    dur = float(kw.pop("dur", 2.6))
    fc = float(kw.get("facing", 0.0))
    a = np.radians(fc)
    away = kw.pop("dir", (np.cos(a) * 1.0, 0.45, -np.sin(a) * 1.0 + 0.3))
    if day:
        ways = [dict(paint=1.0, paint_light=0.0, color=_ink(ink)), dict(paint=0.0, color=lin(color))]
    else:
        ways = [dict(color=lin(color))]
    fx = [dict(kind="disperse", t=t0, dur=dur, share=float(kw.pop("share", 0.55)), dir=away, speed=1.6, burst=0.7,
               spread=0.30, turb=0.20, order="side", noise=0.5, life=4.0,
               sprites=(("shard", 0.030, 9.0, 1.0), ("shard", 0.025, 4.5, 1.0), ("soft", 0.05, 0.8, 0.5)),
               batch=ways)]
    hair = kw.pop("hair", None)
    b = _body(kw, sky, dict(name="rim", bright=0.45 if day else 0.8, power=6.0), color, color2, effects=fx,
              points=70000, garment="dress", hair=False if hair is None else hair, facing=fc,
              gesture=[(-1.0, 1e6, "open_arms", dict(lift=0.35))])
    parts = {name: b}
    if day:
        b.add(scene, name, mask=_flat(_Shape(b), _ink(ink), soft=1.6, grow=0.004))
    else:
        b.add(scene, name, mask=_dark(_Shape(b), grow=0.004, soft=2.0, strength=1.0))
        g = K.Backdrop(_target(b, "chest"), radius=1.3, behind=3.0, color="#cfe0ff", color2="#4a6a9a", bright=0.9,
                       show=kw.get("show"))
        scene.add(name + "_glow", g)
        parts[name + "_glow"] = g
    if hair is None:
        parts[name + "_hair"] = _hair_for_body(scene, name, b, kw, sky, color, color2, ink, length=1.4, locks=60,
                                               wind=(-0.6, 0.7), look="ink" if day else "glow", alpha=0.8)
    return Styled("glass_shatter", sky, b, parts)


def butterflies(scene, name, sky, kw):
    """p02: a figure filled with a starry night (a face in profile with long flowing hair by default, or a whole
    body with figure="body"), small glowing butterflies leaving it and fluttering round it, stars about."""
    day = _day(sky)
    color = _pick(kw, "color", "#ffe6b8", "#fff0d0", sky)
    color2 = _pick(kw, "color2", "#ffb8d8", "#ffc8a0", sky)
    ink = _pick(kw, "ink", "#2a2060", "#5a4a9c", sky)
    t0 = _t(kw, 0.8)
    figure = kw.pop("figure", "profile")
    n = int(kw.pop("n", 11))
    parts = {}
    if figure == "profile":
        kw.setdefault("hair", dict(look="ink" if day else "glow", ink=ink, length=1.9, locks=80, per_lock=16,
                                   curl=0.9, wave=1.3, wind=(-1.0, -0.15), color="#c8b0ff", color2="#ffd8f0",
                                   alpha=0.9))
        main = _face(kw, "fill", "#ffe8d0", "#ffffff", height=0.5, tilt=4.0, features=0.8)
        H = float(main.height(0.0)) if callable(main.height) else float(main.height)
        src = main.shape_set()
        mk = (Mask("sky", sky="stars", source=src, soft=1.8, grow=0.0, tint=(1.6, 1.15, 2.2), edge=0.25) if not day
              else Mask("sky", sky="stars", source=src, soft=1.8, grow=0.0, tint=(4.5, 3.2, 6.0), edge=0.0))
        scene.add(name, main, mask=mk)
        around = _target(main, "head")
        rad, hgt, size = (0.35 * H / 0.5, 1.1 * H / 0.5), (-0.5 * H, 0.45 * H), 0.075 * H
    else:
        main = _body(kw, sky, dict(name="window", bright=0.9), "#ffe8d0", "#ffffff", points=60000, facing=90.0)
        main.add(scene, name, mask=dict(sky="stars", tint=(1.6, 1.15, 2.2) if not day else (4.5, 3.2, 6.0), edge=0.3))
        around = _target(main, "chest")
        rad, hgt, size = (0.35, 0.95), (-0.6, 0.7), 0.06
    parts[name] = main
    bf = K.Butterflies(around, radius=rad, height=hgt, n=n, size=size, speed=0.35 * rad[1], t=t0,
                       spread=float(kw.pop("dur", 2.5)), color=color, color2=color2, bright=1.1,
                       paint=0.35 if day else 0.0, show=kw.get("show"), seed=float(kw.get("seed", 1.0)))
    scene.add(name + "_butterflies", bf)
    parts[name + "_butterflies"] = bf
    sp = K.Sparkles(around, box=(rad[1] * 1.3, rad[1] * 1.2, rad[1] * 0.6), n=300, stars=34, size=size * 0.8,
                    color="#fff4dc", color2="#ffd0b8", bright=1.0, paint=0.3 if day else 0.0, show=kw.get("show"))
    scene.add(name + "_stars", sp)
    parts[name + "_stars"] = sp
    return Styled("butterflies", sky, main, parts)


def dark_silhouette(scene, name, sky, kw):
    """p03, p04, p05: a person as a dark painted shape against a bright or misty sky, the edge fraying into dark
    particles that drift off. At night the same shape stands against a soft glow behind it, with a thin rim."""
    day = _day(sky)
    color = _pick(kw, "color", "#ffd6a0", "#ffe6c0", sky)
    color2 = _pick(kw, "color2", "#ffffff", "#ffffff", sky)
    ink = _pick(kw, "ink", "#06080e", "#1a1f2b", sky)
    t0 = _t(kw, 0.0)
    fc = float(kw.get("facing", 0.0))
    a = np.radians(fc)
    away = kw.pop("dir", (np.cos(a) * 0.8, 0.35, -np.sin(a) * 0.8))
    edge = kw.pop("edge", "flakes")
    fx = []
    if edge:
        sprites = (("flake", 0.10, 3.0, 1.0), ("soft", 0.25, 1.6, 0.8)) if edge == "flakes" else (("soft", 0.5, 1.6, 0.8),)
        fx.append(dict(kind="shed", n=5000, life=3.4, speed=0.30, dir=away, rise=0.10, spread=0.08, turb=0.30,
                       sprite="flake" if edge == "flakes" else "soft", size=2.6 if edge == "flakes" else 1.4,
                       batch=[dict(paint=1.0, paint_light=0.0, color=_ink(ink))] if day else None,
                       color=None if day else color))
        fx.append(dict(kind="disperse", t=t0, dur=30.0, share=float(kw.pop("share", 0.18)), dir=away, speed=0.45,
                       sprites=sprites,
                       batch=[dict(paint=1.0, paint_light=0.0, color=_ink(ink))] if day else [dict(color=lin(ink) * 0.0 + lin(color) * 0.5)]))
    b = _body(kw, sky, dict(name="rim", bright=0.30 if day else 0.75, power=6.0), color, color2, effects=fx,
              points=70000, facing=fc)
    parts = {name: b}
    if day:
        b.add(scene, name, mask=_flat(_Shape(b), _ink(ink), soft=1.6, grow=0.004))
    else:
        b.add(scene, name, mask=_dark(_Shape(b), grow=0.004, soft=1.8, strength=1.0))
        g = K.Backdrop(_target(b, "chest"), radius=float(kw.pop("glow", 1.4)), behind=3.0, color="#ffd2a0",
                       color2="#5a6a9a", bright=1.1, show=kw.get("show"))
        scene.add(name + "_glow", g)
        parts[name + "_glow"] = g
    return Styled("dark_silhouette", sky, b, parts)


def nebula_figure(scene, name, sky, kw):
    """p07 for a whole figure: the body filled with deep clouds lit from inside by a warm light, stars in the
    gaps, billows spilling over its shoulders, birds leaving it."""
    day = _day(sky)
    color = _pick(kw, "color", "#ff9440", "#ff8a30", sky)
    color2 = _pick(kw, "color2", "#ffe0b0", "#ffe6c0", sky)
    t0 = _t(kw, 1.2)
    glow = kw.pop("glow", (0.10, 0.55, 1.3, 0.55))
    birds = kw.pop("birds", "#1c1e2a" if day else "#ffe2c0")
    fx = [dict(kind="birds", t=t0, dur=2.6, n=30, color=birds, dir=kw.pop("birds_dir", (1.0, 0.5, 0.2)), speed=1.5,
               size=0.07)] if birds else []
    b = _body(kw, sky, dict(name="window", bright=0.35, stars=0.004), color2, color2, effects=fx, points=60000,
              facing=90.0)
    b.add(scene, name, mask=dict(sky="nebula", color=color, glow=glow, edge=0.15, soft=2.0))
    parts = {name: b}
    puffs = K.CloudPuffs(lambda t: b.shape_points(t)[0][::40], _target(b, "chest"), n=500, size=0.16, spread=0.10,
                         color=color, shade="#2e3850" if day else "#1a2034", paint=0.75 if day else 0.55,
                         show=kw.get("show"))
    scene.add(name + "_clouds", puffs)
    parts[name + "_clouds"] = puffs
    return Styled("nebula_figure", sky, b, parts)


def nebula_profile(scene, name, sky, kw):
    """p07: a face in profile whose head, hair and shoulders are deep clouds lit from inside by a warm light,
    stars in the gaps, the profile's edge clear (brow, nose, lips, chin, the closed eye), billows spilling
    off the back of the head and birds leaving it."""
    day = _day(sky)
    color = _pick(kw, "color", "#ff9038", "#ff8a30", sky)
    color2 = _pick(kw, "color2", "#ffe2bc", "#fff0dc", sky)
    t0 = _t(kw, 1.0)
    glow = kw.pop("glow", (-0.15, 0.25, 1.35, 0.55))
    kw.setdefault("hair", dict(look="glow", length=0.9, locks=40, per_lock=8, alpha=0.0, wave=0.8, curl=0.3,
                               wind=(-1.0, 0.6), volume=0.10))
    prof = _face(kw, "fill", color, color2, height=0.5, tilt=6.0, features=1.0)
    src = prof.shape_set()
    scene.add(name, prof, mask=Mask("sky", sky="nebula", color=color, glow=glow, source=src, soft=1.8, grow=0.0,
                                    edge=0.12))
    H = float(prof.height)
    hd = prof.hair

    def back(t):
        P, _fr = hd._world(t)
        return P[:, ::4].reshape(-1, 3)
    puffs = K.CloudPuffs(back, _target(prof, "head"), n=650, size=0.10 * H, spread=0.12 * H, color=color,
                         shade="#2e3850" if day else "#161c30", paint=0.8 if day else 0.6, show=kw.get("show"))
    scene.add(name + "_clouds", puffs)
    birds = kw.pop("birds", "#1c1e2a" if day else "#ffe2c0")
    parts = {name: prof, name + "_clouds": puffs}
    if birds:
        fl = K.Flock(_target(prof, "forehead"), dir=kw.pop("birds_dir", (1.0, 0.35, 0.0)), n=26, t=t0, dur=2.5,
                     speed=0.9 * H / 0.5, size=0.035 * H / 0.5, spread=0.4, color=birds, scatter=0.25 * H)
        scene.add(name + "_birds", fl)
        parts[name + "_birds"] = fl
    return Styled("nebula_profile", sky, prof, parts)


def glitter_profile(scene, name, sky, kw):
    """A face in profile made of gold glitter, the closed eye, brow and lips in brighter grains, glitter blowing
    off the back of the head and the hair (painted gold and bronze on a day sky)."""
    day = _day(sky)
    color = _pick(kw, "color", "#e8a848", "#b98030", sky)
    color2 = _pick(kw, "color2", "#fff0c8", "#ffe2a0", sky)
    kw.setdefault("hair", dict(look="glow", length=1.3, locks=60, alpha=0.9, wind=(-1.0, 0.25)))
    prof = _face(kw, "glitter", color, color2, height=0.45, tilt=5.0,
                 stream=dict(n=3000, dir=(-1.0, 0.45), speed=0.30, life=3.0, where=(0.2, 1.0), spread=0.14))
    main = K.Dressed(prof, paint=0.8, paint_light=1.0) if day else prof
    scene.add(name, main)
    return Styled("glitter_profile", sky, prof, {name: main})


def constellation_profile(scene, name, sky, kw):
    """A face in profile drawn as a constellation: stars on the skin joined by fine lines, the profile's edge a
    chain of bright stars, the closed eye and lips small constellations (navy and gold on a day sky)."""
    day = _day(sky)
    color = _pick(kw, "color", "#dce8ff", "#22357e", sky)
    color2 = _pick(kw, "color2", "#fff2d0", "#b8861e", sky)
    kw.setdefault("hair", dict(look="glow", length=1.2, locks=36, per_lock=5, alpha=0.7))
    prof = _face(kw, "constellation", color, color2, height=0.45, tilt=4.0)
    main = K.Dressed(prof, paint=1.0, paint_light=0.5) if day else prof
    scene.add(name, main)
    sp = K.Sparkles(_target(prof, "head"), box=(0.5, 0.5, 0.3), n=300, stars=18, size=0.02, color=color,
                    color2=color2, paint=1.0 if day else 0.0, show=kw.get("show"))
    scene.add(name + "_stars", sp)
    return Styled("constellation_profile", sky, prof, {name: main, name + "_stars": sp})


STYLES = dict(
    constellation=(constellation, "p01: a body of stars joined by fine lines"),
    spark_profile=(spark_profile, "p06: a face in profile traced by sparks, embers streaming off"),
    sky_window=(sky_window, "p07 flat: the body a window onto a sunrise or clouds, birds leaving"),
    gold_glitter=(gold_glitter, "p08: gold glitter blowing apart from one side"),
    ember_dancer=(ember_dancer, "p04: a dancer of embers bursting into a stream of sparks"),
    ash_dissolve=(ash_dissolve, "p03: a figure crumbling into ash with red embers"),
    mist_figure=(mist_figure, "p09: a small sparkling figure in a field of glittering mist"),
    star_silhouette=(star_silhouette, "a silhouette filled with a starry night, stars about"),
    glass_shatter=(glass_shatter, "p05: a figure shattering into shards of glass"),
    butterflies=(butterflies, "p02: a starry silhouette with long hair, glowing butterflies leaving it"),
    dark_silhouette=(dark_silhouette, "p03, p04, p05: a dark painted shape whose edge frays into particles"),
    nebula_figure=(nebula_figure, "p07: a body filled with deep clouds lit from inside"),
    nebula_profile=(nebula_profile, "p07: a face of deep clouds lit from inside, birds leaving"),
    glitter_profile=(glitter_profile, "a face of gold glitter"),
    constellation_profile=(constellation_profile, "a face drawn as a constellation"),
)


def add(scene, style, name=None, sky="night", **keys):
    """Adds a preset to the scene. Returns a Styled (see the module text)."""
    if style not in STYLES:
        raise ValueError("style must be one of %s, got %r" % (sorted(STYLES), style))
    kw = dict(keys)
    return STYLES[style][0](scene, name or style, sky, kw)


def listing():
    for k, (_fn, doc) in STYLES.items():
        print("%-22s %s" % (k, doc))
