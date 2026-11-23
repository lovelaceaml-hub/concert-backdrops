"""Art direction for the full Song 11 recreation.

The original Song 11 scene remains the source of the story, real architecture,
emblem, musical clock and words. This revision changes the cinematography,
light hierarchy, water detail and performance without modifying that source.
"""
from __future__ import annotations

import numpy as np

REVISION = "s11-renewed-v1"


class Graded:
    """Keep original geometry and timing, with a specific lighting role."""

    def __init__(self, source, song, role):
        self.source, self.song, self.role = source, song, role
        self.static = bool(getattr(source, "static", False))
        self.wants_camera = bool(getattr(source, "wants_camera", False))

    def sample(self, t, cam=None):
        if self.wants_camera:
            return self.source.sample(t, cam)
        return self.source.sample(t)

    def gain(self, t):
        h = self.song
        original = float(self.source.gain(t)) if hasattr(self.source, "gain") else 1.0
        if original <= 0.0:
            return 0.0
        key = h.key_moment(t)
        factors = {
            "architecture": 0.72 + 0.12 * key,
            "rim": 0.66 + 0.14 * key,
            "mist": 0.58,
            "garden": 0.97,
            "glory": 0.67 + 0.14 * key,
            "sparkle": 0.70,
            "sea": 0.78,
            "flare": 0.40 + 0.12 * key,
            "sun": 0.62,
        }
        k = factors[self.role]
        # Existing finding f43: the bright terrace edges cross a reading line.
        # Fade the architectural layer gently; no panel or rectangular mask.
        if self.role in ("architecture", "rim"):
            reading = h._sc(164.8, 165.4, t) * (1.0 - h._sc(169.7, 170.8, t))
            k *= 1.0 - 0.42 * reading
        return original * k


class WaterPaths:
    """Fine cyan tributaries and travelling points over the sea before Zion.

    These are actual three-dimensional curves. Their slow counter-motion gives
    the new low camera flights foreground parallax without covering the sky.
    """

    def __init__(self, song):
        from p3d import lin
        self.h = song
        self.rng = np.random.default_rng(112226)
        self.samples = self.rng.random((3600, 4))
        self.colors = [lin(c) for c in ("#3a8fbe", "#54cdbd", "#8a91d8")]

    def gain(self, t):
        h = self.h
        if h.globe_view(t) or h.stage_view(t) or t >= 254.07:
            return 0.0
        start = h._sc(11.6, 20.0, t)
        return start * (0.20 + 0.15 * h.glory(t))

    def _curve(self, u, side, t):
        h = self.h
        z = -112.0 + 800.0 * u
        spread = 34.0 + 158.0 * u
        x = side * spread + (12.0 + 8.0 * abs(side)) * np.sin(2.1 * np.pi * u + side)
        y = 0.15 + 0.06 * np.sin(10.0 * u - 0.28 * t + side)
        return np.stack([x, y, z], axis=1)

    def sample(self, t):
        if self.gain(t) <= 0.0:
            return []
        from p3d.api import ribbon
        out = []
        u = np.linspace(0.0, 1.0, 160)
        for i, side in enumerate((-1.9, -1.15, -0.50, 0.50, 1.15, 1.9)):
            p = self._curve(u, side, t)
            col = self.colors[i % len(self.colors)]
            fade = np.sin(np.pi * u) ** 0.7
            out.append(ribbon(p, width=0.55 + 1.15 * u, color=col,
                              alpha=0.22 * fade, emit=1.15, dof=0.4))
            r = self.samples[i * 600:(i + 1) * 600]
            v = np.mod(r[:, 0] - t * (0.006 + 0.003 * r[:, 1]), 1.0)
            q = self._curve(v, side, t)
            q[:, 0] += (r[:, 2] - 0.5) * 3.0
            q[:, 1] += r[:, 3] * 0.25
            out.append(dict(pos=q, size=0.12 + 0.20 * r[:, 1], color=col,
                            alpha=np.sin(np.pi * v) ** 0.7 * 0.55,
                            emit=1.3, kind="spark", twinkle=0.12,
                            seed=r[:, 2]))
        return out


def _role(name):
    if name == "epic sun":
        return "sun"
    if name in ("sound answers", "music comet flares") or name.startswith("stage comet "):
        return "flare"
    if name in ("zion walls", "zion dim", "zion gold", "zion gates", "zion towers", "city dim", "city gold"):
        return "architecture"
    if name in ("zion rim", "zion gates rim", "zion beat"):
        return "rim"
    if name in ("zion mist",) or "pour clouds" in name:
        return "mist"
    if name in ("zion gardens", "zion plot gardens"):
        return "garden"
    if name in ("church glory", "church beacon"):
        return "glory"
    if name == "constellations":
        return "sparkle"
    if name == "sea glitter":
        return "sea"
    return None


def install(song):
    """Install once after the pinned loader, before Renderer construction."""
    if getattr(song, "_renewed_scene_installed", False):
        raise RuntimeError("The renewed scene must be installed exactly once.")
    from tools.s11_renewed import cinematography
    cinematography.install(song)

    # A quieter, deeper atmosphere lets the existing architecture show its
    # materials. Sunrise stays a deliberate change across the full recording.
    looks = song.S_LIGHT.LOOKS
    for name, look in looks.items():
        if name == "pastel_card":
            continue
        look["dust"] = 0.44
        look["bokeh"] = 0.42
        if "haze" in look:
            look["haze"] *= 0.78
        if "mist" in look:
            look["mist"] *= 0.74
        if "milky" in look:
            look["milky"] *= 0.74
        if "stars" in look:
            look["stars"] *= 0.82
        if "sun_glow" in look:
            look["sun_glow"] *= 0.78
    looks["city"].update(sky_top="#020714", sky_mid="#0b1635", sky_hor="#49324e", water="#020810")
    looks["zion"].update(sky_top="#040a20", sky_mid="#202348", sky_hor="#855779", water="#030a14")
    looks["sunrise"].update(sky_top="#060d29", sky_mid="#25264e", sky_hor="#af7083", water="#040b18")
    looks["golden"].update(sky_top="#080e2d", sky_mid="#342955", sky_hor="#c08084", water="#050c1b")

    song.WORLD["looks"] = looks
    song.WORLD["look"] = song.S_LIGHT._look_keys()
    song.WORLD["float_field"] = dict(song.WORLD["float_field"], count=2300, size=0.78)
    song.WORLD["hill_height"] = 0.92
    song.WORLD["lantern_field"] = dict(song.WORLD["lantern_field"], count=250)
    source_light = dict(song.WORLD["light"])
    source_strength = source_light["strength"]
    source_light["strength"] = lambda t: (
        source_strength(t) if callable(source_strength) else source_strength
    ) * (0.64 + 0.12 * song.key_moment(t))
    source_light["rays"] = float(source_light.get("rays", 1.0)) * 0.72
    song.WORLD["light"] = source_light

    # The sunrise has a place in the composition. Keep the large disc beside
    # the reading area instead of letting it bleach the words and the church.
    light = song.S_LIGHT
    old_az, old_el = light.sun_az, light.sun_el
    camera = song.CAMERA.state(203.9)
    right, up, forward = camera.basis()
    half = np.tan(np.radians(camera.fov) * 0.5)
    direction = forward + right * half * camera.aspect * 0.70 + up * half * 0.62
    direction /= np.linalg.norm(direction)

    def sun_direction(t):
        az, el = np.radians(old_az(t)), np.radians(old_el(t))
        base = np.array([np.sin(az) * np.cos(el), np.sin(el), np.cos(az) * np.cos(el)])
        amount = song._sc(200.6, 201.73, t) * (1.0 - song._sc(205.98, 206.7, t))
        d = base * (1.0 - amount) + direction * amount
        return d / np.linalg.norm(d)

    light.sun_az = lambda t: float(np.degrees(np.arctan2(sun_direction(t)[0], sun_direction(t)[2])))
    light.sun_el = lambda t: float(np.degrees(np.arcsin(sun_direction(t)[1])))
    song.WORLD["sun_az"] = light.sun_az
    song.WORLD["sun_el"] = light.sun_el

    # Phrase geometry is composed for the new cameras. Wording and music
    # timings come unchanged from the existing film, never retyped here.
    song._WBOX.clear()
    song._SPECS = song._phrase_specs()
    song.WORDS = song.PW.Words(song._SPECS, camera=song.CAMERA)
    song.P3D["camera"] = song.CAMERA
    song.P3D["world"] = song.WORDS.world(song.WORLD)
    song.P3D["bursts"] = song._bursts()
    # Keep the biggest music accents. Most cuts no longer need a white flash.
    for burst in song.P3D["bursts"]:
        if not any(abs(burst["t"] - hit) < 0.06 for hit in song.SLAMS):
            burst["strength"] *= 0.74

    original_setup = song.P3D["setup"]

    def setup(scene):
        original_setup(scene)
        for entry in scene.entries():
            role = _role(entry.name)
            if role:
                entry.pointset = Graded(entry.pointset, song, role)
        scene.add("renewed water tributaries", WaterPaths(song), reflect=False)

    song.P3D["setup"] = setup
    song._renewed_scene_installed = True


def finish_renderer(renderer, song):
    """Control the lens glow after the established beauty finishing pass."""
    original_adjust = renderer.p3d.adjust

    def adjust(t, parameters):
        p = original_adjust(t, parameters)
        # Light still radiates, but its core remains visibly colored.
        p["bloom_gain"] = p.get("bloom_gain", 1.0) * (0.84 if song.globe_view(t) else 0.77)
        return p

    renderer.p3d.adjust = adjust

