"""Warm luminous people for the isolated thirty-second promo example.

The existing MakeHuman/CMU asset, articulated fingers, planted-foot walking and
garments are reused without changing the approved engine. Public coordinates
are metres, Z-up, with a frontal person facing -Y. Every sample depends on time,
the fixed cast and the existing asset; no previous rendered frame is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.p3d.actor import Actor
from engine.p3d.body import Body
from engine.p3d import cloth


CACHE_DIRECTORY = ROOT / "work/promo-people-example/people/cache"
_CONDUCTOR_ORIGIN = np.array([2.5, 0.0, -1.1], dtype=np.float64)
_NAMES = ("head", "palm.L", "palm.R", "ankle.L", "ankle.R", "toe.L", "toe.R", "ground")


def _zup(value):
    out = np.asarray(value)[..., [0, 2, 1]].copy()
    out[..., 1] *= -1
    return out


def _smoother(value):
    u = float(np.clip(value, 0.0, 1.0))
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def _conducting_target(t, side):
    """A gentle asymmetric beat pattern, expressed as a world palm target."""
    sign = 1.0 if side == "L" else -1.0
    # The support hand follows the leading hand and describes a smaller arc.
    lag = 0.18 if side == "L" else 0.075
    phase = 2.0 * math.pi * (float(t) - 10.2 - lag) / 2.18
    finish = 1.0 - 0.75 * _smoother((float(t) - 28.75) / 1.25)
    amount = (0.74 if side == "L" else 1.0) * finish
    accent = (0.055 * math.exp(-((float(t) - 12.51) / 0.42) ** 2)
              + 0.075 * math.exp(-((float(t) - 28.11) / 0.58) ** 2))
    local = np.array([
        sign * (0.285 + amount * (0.060 * math.cos(phase) + 0.018 * math.sin(2.0 * phase)) + accent),
        1.235 + amount * (0.105 * math.sin(phase) + 0.025 * math.sin(2.0 * phase - 0.5)) + accent,
        0.350 + amount * (0.025 * math.cos(phase - 0.7) + 0.020 * math.sin(phase)),
    ])
    # The conductor faces 180 degrees in the old Y-up engine, toward the choir.
    return _CONDUCTOR_ORIGIN + local * np.array([-1.0, 1.0, -1.0])


def _choir_palm_target(t, side, index, height):
    """Lift open hands within each singer's own space, without neighboring arms crossing."""
    sign = 1.0 if side == "L" else -1.0
    lift = _smoother((float(t) - 20.9 - index * 0.42) / 2.8)
    breath = 0.006 * math.sin(float(t) * 1.2 + index * 1.7)
    return np.array([sign * height * (0.125 + 0.008 * lift),
                     height * (0.69 + 0.09 * lift) + breath,
                     height * (0.145 + 0.035 * lift)])


def _cache_fingerprint():
    paths = [Path(__file__), ROOT / "assets/p3d/body_v1.npz", ROOT / "uv.lock", ROOT / "pyproject.toml"]
    paths += [ROOT / "engine/p3d" / name for name in
              ("actor.py", "assets.py", "body.py", "bodymath.py", "cloth.py", "motion.py",
               "gestures.py", "looks.py", "effects.py", "api.py")]
    payload = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    payload["numpy_version"] = np.__version__
    payload["cache_format"] = 1
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest, payload


def _walking_person(target, facing, phase, **kwargs):
    motions = [(0.0, "walk", dict(speed=0.28, phase=phase)),
               (1.3, "stand", dict(blend=1.0))]
    probe = Actor("man", height=kwargs.get("height"), facing=facing, motion=motions, start=0.0)
    displacement = probe.travel(3.0)[1]
    at = np.array([target[0], target[2], -target[1]]) - displacement
    return Body("man", at=tuple(at), facing=facing, motion=motions, **kwargs)


def _cast():
    shared = dict(look=dict(name="glitter", seams=0.75, glints=0.00055),
                  color="#ffd092", color2="#fff0cd", bright=1.0,
                  wind=(0.045, 0.0, 0.025), gust=0.16, detail=dict(head=1.6, hand=2.2))
    a = _walking_person((-2.7, 0.0, 0.0), 70.0, 0.08,
        height=1.75, build=1.04, garment="coat", hair="short", points=30000, seed=11.0,
        gesture=[
            (2.85, 5.35, "bow", dict(amount=17.0, ease=0.95, over=0.015)),
            (5.8, 9.05, "offer", dict(side="R", ease=1.1, over=0.015)),
            (8.45, 12.8, "listen", dict(side="L", amount=0.62, ease=1.0)),
            (13.2, 17.9, "explain", dict(side="R", period=3.5, ease=1.3)),
            (21.8, 26.2, "hand_on_heart", dict(side="R", bow=5.0, ease=1.5)),
        ], **shared)
    b = _walking_person((-1.3, 0.0, 0.0), -70.0, 0.53,
        height=1.68, build=0.96, garment="tunic", hair="cap", points=30000, seed=24.0,
        gesture=[
            (3.2, 5.75, "bow", dict(amount=15.0, ease=0.95, over=0.015)),
            (5.9, 8.8, "listen", dict(side="R", amount=0.55, ease=1.0)),
            (8.05, 11.5, "hand_on_heart", dict(side="R", bow=7.0, ease=1.1)),
            (8.2, 10.6, "nod", dict(amount=4.0, period=2.1, turn=-7.0, ease=0.9)),
            (13.7, 18.3, "listen", dict(side="R", amount=0.5, ease=1.3)),
            (22.2, 26.7, "open_hands", dict(bow=2.0, ease=1.6)),
        ], **shared)
    conduct_gestures = []
    for side in ("L", "R"):
        conduct_gestures.append((9.35, 31.1, "touch", dict(
            side=side, to=lambda t, side=side: _conducting_target(t, side),
            end="palm", palm="in", fingers="relaxed", look=False,
            lean=0.0, wrist=-7.0, ease_in=1.35, ease_out=1.7, antic=0.0, over=0.01)))
    conductor = Body("man", height=1.80, build=0.94, at=tuple(_CONDUCTOR_ORIGIN),
        facing=180.0, garment="coat", hair="short", points=25000, seed=38.0,
        gesture=conduct_gestures, **shared)
    choir = []
    for j, (shape, height, garment, hair) in enumerate([
        ("woman", 1.64, "dress", "bun"),
        ("man", 1.74, "tunic", "short"),
        ("woman", 1.69, "robe", "tied"),
    ]):
        start = 20.9 + j * 0.42
        lifted_hands = [(start, 27.5 + j * 0.15, "touch", dict(
            side=side, to=lambda t, side=side, j=j, height=height: _choir_palm_target(t, side, j, height),
            end="palm", palm="up", fingers="offer", look=False, lean=0.0, wrist=-5.0,
            pole=((0.20 if side == "L" else -0.20), -1.0, -0.10),
            ease_in=2.15, ease_out=1.7, antic=0.0, over=0.01)) for side in ("L", "R")]
        choir.append(Body(shape, height=height, build=0.97 + j * 0.035,
            at=(0.0, 0.0, 0.0), facing=0.0, garment=garment, hair=hair,
            points=8000, seed=51.0 + j * 13.0,
            gesture=[
                (11.0 + j * 0.3, 16.6 + j * 0.2, "open_hands", dict(bow=0.0, ease=1.6)),
                (start + 0.8, 27.0, "look_up", dict(amount=5.0, ease=1.7)),
            ] + lifted_hands, **shared))
    return {"pair_a": a, "pair_b": b, "conductor": conductor,
            "choir_0": choir[0], "choir_1": choir[1], "choir_2": choir[2]}


class PeopleScene:
    """Eleven visible people, backed by six independent clothed performances.

    sample(t) returns float32 columns:
    XYZ, normal XYZ, linear RGB with emission, size in metres, alpha, seed.
    anchors(t) supplies world-space interaction locations and floor contacts.
    """

    def __init__(self, cache_directory=CACHE_DIRECTORY, use_cache=True):
        self.bodies = _cast()
        self.cache_directory = Path(cache_directory)
        self.cache_key, self.cache_sources = _cache_fingerprint()
        self.cache_loaded = []
        self.placements = []
        heights = (0.98, 1.025, 0.96, 1.015, 1.00, 0.975, 1.03, 0.99)
        for row in range(2):
            for col, dx in enumerate((-1.4, -0.47, 0.47, 1.4)):
                idx = row * 4 + col
                x, y, z = 2.5 + dx, (3.2 if row == 0 else 4.35) + 0.07 * abs(dx), 0.0 if row == 0 else 0.18
                delta = np.array([2.5 - x, 1.1 - y])
                yaw = math.atan2(delta[0], -delta[1])
                cs, sn = math.cos(yaw), math.sin(yaw)
                rotation = np.array([[cs, -sn, 0.0], [sn, cs, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
                self.placements.append(dict(name=f"choir_person_{idx}", prototype=idx % 3,
                    translation=np.array([x, y, z], dtype=np.float32), rotation=rotation,
                    scale=heights[idx], gain=0.97 + (idx % 4) * 0.022))
        if use_cache:
            for name, body in self.bodies.items():
                if self._load_cloth(name, body):
                    self.cache_loaded.append(name)

    @staticmethod
    def _ground_correction(body, t):
        """Keep the captured approach's true skinned soles above the stage.

        The legacy actor grounds a few probes before its foot-lock adjustment.
        The full mesh can therefore extend a few millimetres below the floor.
        Correct only the presentation of the two walking heroes, moving their
        clothing and anchors with them. Horizontal planting stays unchanged.
        The blend to standing completes at2.3s; the cutoff then eases to zero.
        """
        if t >= 2.5:
            return 0.0
        vertices = body._skinned(float(t))[0]
        lift = max(0.0, -float(vertices[:, 1].min()))
        return lift * (1.0 - _smoother((float(t) - 2.3) / 0.2))

    @staticmethod
    def _body_array(body, t, ground_correct=False):
        arrays = []
        for batch in body.sample(float(t)):
            if batch.get("kind") not in ("soft", "spark"):
                continue
            n = len(batch["pos"])
            out = np.empty((n, 12), dtype=np.float32)
            out[:, :3] = _zup(batch["pos"])
            out[:, 3:6] = _zup(batch["normal"])
            emit = np.asarray(batch.get("emit", 1.0), dtype=np.float32)
            out[:, 6:9] = np.asarray(batch["color"], dtype=np.float32) * (emit[:, None] if emit.ndim else emit)
            out[:, 9] = batch["size"]
            out[:, 10] = batch["alpha"]
            out[:, 11] = batch["seed"]
            arrays.append(out)
        combined = np.ascontiguousarray(np.concatenate(arrays), dtype=np.float32)
        if ground_correct:
            combined[:, 2] += PeopleScene._ground_correction(body, t)
        return combined

    def sample(self, t):
        t = float(t)
        if not math.isfinite(t):
            raise ValueError("Time must be finite.")
        t = max(0.0, t)
        result = [self._body_array(self.bodies[name], t, ground_correct=name.startswith("pair_"))
                  for name in ("pair_a", "pair_b", "conductor")]
        prototypes = [self._body_array(self.bodies[f"choir_{j}"], t + j * 0.20) for j in range(3)]
        for placement in self.placements:
            a = prototypes[placement["prototype"]].copy()
            rotation, scale = placement["rotation"], placement["scale"]
            a[:, :3] = (a[:, :3] @ rotation.T) * scale + placement["translation"]
            a[:, 3:6] = a[:, 3:6] @ rotation.T
            a[:, 6:9] *= placement["gain"]
            a[:, 9] *= scale
            result.append(a)
        return np.ascontiguousarray(np.concatenate(result), dtype=np.float32)

    def anchors(self, t):
        t = max(0.0, float(t))
        result = {}
        contacts = []
        for name in ("pair_a", "pair_b", "conductor"):
            body = self.bodies[name]
            places = {place.replace(".", "_"): _zup(body.where(t, place)).astype(np.float32) for place in _NAMES}
            if name.startswith("pair_"):
                lift = self._ground_correction(body, t)
                for value in places.values():
                    value[2] += lift
            result[name] = places
            result.update({f"{name}_{key}": value for key, value in places.items()})
            for side in ("L", "R"):
                centre = 0.5 * (places[f"ankle_{side}"] + places[f"toe_{side}"])
                centre[2] = 0.012
                contacts.append(centre)
        prototype_feet = {}
        for j in range(3):
            body = self.bodies[f"choir_{j}"]
            prototype_feet[j] = [0.5 * (_zup(body.where(t + j * 0.20, f"ankle.{side}"))
                                       + _zup(body.where(t + j * 0.20, f"toe.{side}"))) for side in ("L", "R")]
        for p in self.placements:
            for foot in prototype_feet[p["prototype"]]:
                centre = (foot @ p["rotation"].T) * p["scale"] + p["translation"]
                centre[2] = p["translation"][2] + 0.012
                contacts.append(centre.astype(np.float32))
        result["floor_contacts"] = contacts
        result["contacts"] = contacts
        result["conductor_hands"] = [result["conductor_palm_L"], result["conductor_palm_R"]]
        result["pair_palms"] = [result["pair_a_palm_R"], result["pair_b_palm_R"]]
        return result

    def _cache_paths(self, name):
        path = self.cache_directory / f"{name}-{self.cache_key[:20]}.npz"
        return path, path.with_suffix(".json")

    def _load_cloth(self, name, body):
        path, receipt = self._cache_paths(name)
        if body.cloth is None or not path.is_file() or not receipt.is_file():
            return False
        meta = json.loads(receipt.read_text())
        if meta.get("fingerprint") != self.cache_key or meta.get("name") != name:
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest() != meta.get("sha256"):
            return False
        c = body.cloth
        with np.load(path, allow_pickle=False) as saved:
            snaps = saved["snapshots"]
            if snaps.ndim != 3 or snaps.shape[1:] != (c.n, 3) or not np.isfinite(snaps).all():
                raise ValueError(f"Invalid cloth snapshot geometry: {name}")
            if abs(float(saved["t_start"]) - c.t_start) > 1e-9:
                raise ValueError(f"Cloth snapshot start mismatch: {name}")
            c.snaps = list(snaps)
            c.x = saved["x"].copy()
            c.xp = saved["xp"].copy()
            c.steps = int(saved["steps"])
            c.t0 = float(saved["t0"])
        return True

    def prepare_cache(self, duration=31.0, progress=None):
        """Bake each small cloth system once, with verified atomic cache writes."""
        duration = float(duration)
        if duration < 30.5 or not math.isfinite(duration):
            raise ValueError("Cache duration must cover at least 30.5 seconds.")
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        reports = []
        for name, body in self.bodies.items():
            c = body.cloth
            started = time.monotonic()
            path, receipt = self._cache_paths(name)
            if name in self.cache_loaded:
                existing = json.loads(receipt.read_text())
                if existing["duration"] >= duration:
                    reports.append(existing)
                    if progress is not None:
                        progress(dict(name=name, duration=existing["duration"], reused=True))
                    continue
            c.positions(duration)
            if _cache_fingerprint()[0] != self.cache_key:
                raise RuntimeError("People source changed while baking cloth.")
            temp = path.with_suffix(f".tmp-{os.getpid()}.npz")
            with temp.open("wb") as output:
                np.savez_compressed(output, snapshots=np.asarray(c.snaps, dtype=np.float32),
                    x=c.x, xp=c.xp, steps=np.int64(c.steps), t0=np.float64(c.t0), t_start=np.float64(c.t_start))
            digest = hashlib.sha256(temp.read_bytes()).hexdigest()
            os.replace(temp, path)
            info = dict(name=name, fingerprint=self.cache_key, sources=self.cache_sources, sha256=digest,
                duration=duration, nodes=c.n, snapshots=len(c.snaps), fixed_step=cloth.DT,
                snapshot_step=cloth.DT * cloth.SNAP, seconds=time.monotonic() - started,
                bytes=path.stat().st_size)
            temp_receipt = receipt.with_suffix(f".tmp-{os.getpid()}.json")
            temp_receipt.write_text(json.dumps(info, indent=2) + "\n")
            os.replace(temp_receipt, receipt)
            reports.append(info)
            if progress is not None:
                progress({key: info[key] for key in ("name", "duration", "nodes", "snapshots", "seconds", "bytes")})
        return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bake", action="store_true")
    parser.add_argument("--duration", type=float, default=31.0)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    scene = PeopleScene()
    print(json.dumps({"unique_performances": len(scene.bodies), "visible_people": 11,
                      "loaded_cloth_caches": scene.cache_loaded}), flush=True)
    if args.bake:
        scene.prepare_cache(args.duration, progress=lambda value: print(json.dumps(value), flush=True))
    if args.benchmark:
        for t in (3.0, 8.0, 15.0, 24.0):
            started = time.monotonic()
            points = scene.sample(t)
            print(json.dumps({"time": t, "points": len(points), "seconds": time.monotonic() - started,
                              "finite": bool(np.isfinite(points).all())}), flush=True)


if __name__ == "__main__":
    main()
