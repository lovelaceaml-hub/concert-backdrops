"""Flowing, fully clothed dance costumes on the existing native body rig.

Only this factory's instance is changed. The archived Body defaults, rig and
earlier films stay untouched. The factory never samples a posed body, leaving
the caller free to install its choreography before cloth or skin is evaluated.
"""
from __future__ import annotations

import math
import numpy as np

from p3d import bodymath as bm
from p3d import assets, cloth, looks
from p3d.api import lin
from p3d.body import Body, _ClothSource, _SkinSource, _RigidSource


PALETTES = (
    ("#bca6df", "#e5a0b7"),
    ("#a6c4df", "#ceb2df"),
    ("#e2bd91", "#e6b0bb"),
    ("#b3a8df", "#ddb0d4"),
    ("#abd1c8", "#dbc5bc"),
)
CLOTH_ROWS = 20
CLOTH_COLUMNS = 32
PLEATS = 10


class DanceClothSystem(cloth.ClothSystem):
    """More constraint work for fast dance, keeping the same cloth dynamics.

    The inherited three projection passes are sufficient for the earlier slow
    scores but leave elongated cells during repeated turns and quick travel.
    This instance retains the same 120 Hz clock, gravity, air, pinning and body
    colliders. Extra projections reduce stretch instead of reducing animation
    speed or replacing cloth movement with a rigid skirt.
    """

    minimum_iterations = 8
    shape_iterations = 8
    maximum_iterations = 128

    def _stretch(self, positions):
        ratios = [
            np.linalg.norm(positions[b] - positions[a], axis=1) / length
            for a, b, length, _wa, _wb in self.batches
        ]
        return np.concatenate(ratios)

    def _step(self):
        # The integration is deliberately the same as ClothSystem._step; only
        # the number and ordering of constraint/collision projections differ.
        t = self.t0 + (self.steps + 1) * cloth.DT
        matrices, joints, ground_y = self._body(t)
        x, previous = self.x, self.xp
        velocity = (x - previous) / cloth.DT
        if self.wind_obj is not None:
            wind = self.wind_obj.at(t)
        else:
            wind = self.wind * (
                1.0 + self.gust * bm.wobble(t, self.seed + 0.5, 0.9)
            )
        eddies = bm.flow(x, t, scale=1.3, speed=0.7, seed=self.seed) * (
            (0.25 + 0.6 * np.linalg.norm(wind)) * self.gust
        )
        acceleration = (wind + eddies - velocity) * self.air
        acceleration[:, 1] -= 9.81 * self.weight
        xn = x + (x - previous) * 0.996 + acceleration * cloth.DT ** 2
        pins = self._pins(matrices)
        xn[self.pin_idx] = pins
        ca, cb = self.col.at(matrices)
        floor = (ground_y if self.ground is None else self.ground) + 0.012
        touched = np.zeros(self.n, dtype=bool)

        for iteration in range(self.maximum_iterations):
            # Apply the soft shape forces a fixed number of times per physical
            # step. Repeating them on every convergence pass makes stiffness
            # depend on the solver budget and keeps reopening short waist edges
            # during fast turns. Remaining passes solve edge lengths and body
            # collision together while the soft folds retain their influence.
            if iteration < self.shape_iterations:
                delta = xn[self.sb] - xn[self.sa]
                distance = np.linalg.norm(delta, axis=1)
                xn += self.G @ (
                    ((distance - self.sL) / np.maximum(distance, 1e-9))[:, None] * delta
                )
            for a, b, length, wa, wb in self.batches:
                delta = xn[b] - xn[a]
                distance = np.linalg.norm(delta, axis=1)
                correction = (
                    (distance - length) / np.maximum(distance, 1e-9)
                )[:, None] * delta
                xn[a] += correction * wa
                xn[b] -= correction * wb
            anchor = xn[self.lra_anc]
            delta = xn[self.lra_idx] - anchor
            distance = np.linalg.norm(delta, axis=1)
            over = distance > self.lra_d
            if over.any():
                xn[self.lra_idx[over]] = anchor[over] + delta[over] * (
                    self.lra_d[over] / distance[over]
                )[:, None]
            # Repeated collision/projection rounds converge together. Checking
            # only the final collision can reopen the just-solved edge lengths.
            if iteration % 2 == 1:
                self._collide(xn, ca, cb, floor, joints, matrices, touched)
            low = self.free & (xn[:, 1] < floor)
            if low.any():
                xn[low, 1] = floor
                touched |= low
            xn[self.pin_idx] = pins
            if iteration + 1 >= self.minimum_iterations and iteration % 4 == 3:
                ratio = self._stretch(xn)
                if np.percentile(ratio, 99) <= 1.10 and ratio.max() <= 1.25:
                    break

        if touched.any():
            x = x.copy()
            x[touched] += (xn[touched] - x[touched]) * 0.35
        self.xp, self.x = x, xn
        self.steps += 1


def _replace_skirt(body: Body, role: int) -> int:
    """Replace the initial coat skirt and rebuild its unsampled cloud."""
    sources = [
        (i, source) for i, source in enumerate(body.sources)
        if isinstance(source, _ClothSource) and source.cp.name == "skirt"
    ]
    if len(sources) != 1 or len(body.cloth.pieces) != 1:
        raise ValueError("The performance costume requires one unsampled skirt")
    if body.actor._cache or body.cloth.x is not None:
        raise ValueError("Construct the performance costume before pose sampling")

    index, original = sources[0]
    total_points = body.cloud["n"]
    trouser = [
        (j, source) for j, source in enumerate(body.sources)
        if isinstance(source, _SkinSource) and source.part == looks.CLOTH
        and set(np.unique(source.surf.region)).issubset({6, 7, 8})
    ]
    if len(trouser) != 1:
        raise ValueError("The dance costume requires its complete trouser underlayer")
    trouser_index, underlayer = trouser[0]
    under_points = max(800, underlayer.n // 2)
    skirt_points = original.n + underlayer.n - under_points
    hip_y = body.rig.head[body.rig.idx["upperleg01.L"]][1]

    def trouser_offset(rest):
        return body.k * (0.014 + 0.022 * np.clip(1.0 - rest[:, 1] / hip_y, 0.0, 1.0) ** 1.3)

    # Spend the same particle budget on the visible flared surface. The full
    # trouser geometry remains sampled and clothed under it, including ankles.
    surface = assets.Surface(
        body.rig, under_points, keep=["hips", "leg", "shin"], salt=42,
    )
    body.sources[trouser_index] = _SkinSource(body, surface, looks.CLOTH, trouser_offset)
    piece = cloth.skirt(
        body.rig, top=0.625, hem=0.22, flare=2.85, bell=0.72,
        cols=CLOTH_COLUMNS, rows=CLOTH_ROWS, margin=0.014, air=1.45,
        name="skirt", open_front=False,
    )
    # Shallow radial pleats provide cloth volume and readable moving folds.
    # Their top row stays unchanged, so the fitted waist retains its bind.
    center = piece.rest[0].mean(axis=0)
    radial = piece.rest[:, :, [0, 2]] - center[[0, 2]]
    angle = np.arctan2(radial[:, :, 0], radial[:, :, 1])
    length = np.linspace(0.0, 1.0, piece.rows)[:, None]
    pleat = 1.0 + 0.045 * length ** 1.4 * np.cos(PLEATS * angle)
    piece.rest[:, :, 0] = center[0] + radial[:, :, 0] * pleat
    piece.rest[:, :, 2] = center[2] + radial[:, :, 1] * pleat

    system = DanceClothSystem(
        body.actor, [piece], t_start=body.t_start,
        wind=body.wind if body.wind is not None else (0.0, 0.0, 0.0),
        gust=0.045, seed=body.seed,
    )
    points = cloth.ClothPoints(system, "skirt", skirt_points, salt=431 + 17 * role)
    replacement = _ClothSource(body, points, looks.CLOTH)
    body.cloth = system
    body.sources[index] = replacement

    # Rebuild attributes derived from source geometry before building looks.
    # No posed frame, effects, mask or outside consumer has retained old indices.
    body.offs = np.cumsum([0] + [source.n for source in body.sources])
    body.src_of = np.concatenate([
        np.full(source.n, j) for j, source in enumerate(body.sources)
    ])
    body.cloud["n"] = int(body.offs[-1])
    body.cloud["part"] = np.concatenate([
        np.full(source.n, source.part) for source in body.sources
    ])
    body.skinlike = np.concatenate([
        np.full(source.n, isinstance(source, (_SkinSource, _RigidSource)))
        for source in body.sources
    ])
    if body.cloud["n"] != total_points:
        raise AssertionError("The performance costume preserves the full point budget")
    body.cloud["rest"] = np.concatenate([s.rest for s in body.sources]).astype(np.float32)
    body.cloud["h"] = np.clip(
        np.concatenate([s.h for s in body.sources]), 0.0, 1.0
    ).astype(np.float32)
    body.cloud["seed"] = np.concatenate([s.seed for s in body.sources]).astype(np.float32)
    body.cloud["edge"] = body._edges(body.cloud["rest"], body.cloud["part"], body.k)
    body.cloud["size"] = (
        (0.003 + 0.008 * body.cloud["seed"].astype(np.float64) ** 4)
        * body.k * body.grain * 0.9
    ).astype(np.float32)
    return index


def _dress_layers(body: Body, skirt_source: int, role: int, ensemble: bool) -> None:
    """Color the actual garment pieces without replacing anatomical surfaces."""
    upper, lower = PALETTES[role % len(PALETTES)] if ensemble else PALETTES[0]
    upper, lower, gold = lin(upper), lin(lower), lin("#e8bf7a")
    cloud = body.cloud
    rest, part = cloud["rest"], cloud["part"]
    is_skirt = body.src_of == skirt_source
    is_cloth = part == looks.CLOTH
    # Visible trousers continue to the ankle under the full closed skirt.
    # Their quieter color leaves the brighter hem and feet easy to read.
    is_trouser = is_cloth & ~is_skirt & (cloud["h"] < 0.61)
    cloth_mix = bm.smooth((cloud["h"] - 0.28) / 0.37)
    base = lower[None] * (1.0 - cloth_mix[:, None]) + upper[None] * cloth_mix[:, None]
    theta = np.arctan2(rest[:, 0], rest[:, 2] - body.rig.neutral_pos[0, 2])
    pleats = 0.84 + 0.16 * np.cos(theta * PLEATS) ** 2
    base[is_skirt] *= pleats[is_skirt, None]

    # A restrained waistband and seam edge define construction at full size.
    waist = np.exp(-((cloud["h"] - 0.616) / 0.010) ** 2)
    trim = np.clip(0.72 * cloud["edge"] + 0.70 * waist, 0.0, 0.85)
    trim[~is_cloth] = 0.0
    base = base * (1.0 - trim[:, None]) + gold[None] * trim[:, None]
    base[is_trouser] = lin("#aaa0c0")

    specs = (
        dict(name="glitter", bright=1.0, size=0.9, seams=0.30, glints=0.00013),
        dict(name="rim", bright=0.25, size=0.9, power=3.8, seams=0.22),
    )
    body.layers = []
    body.look_names = [spec["name"] for spec in specs]
    for spec in specs:
        for layer in looks.build(
            spec, cloud, body.color, body.color2, body.bright,
            body.k * body.grain,
        ):
            ids = layer["idx"]
            codes = part[ids]
            color = np.asarray(layer["color"]).copy()
            cloth_here = is_cloth[ids]
            color[cloth_here] = base[ids[cloth_here]]
            # High-density hand points use smaller grains. Dimming whole hands
            # alone obscures fingers; these grains preserve a clean silhouette.
            hand = codes == looks.HAND
            foot = codes == looks.FOOT
            layer["size"] = np.asarray(layer["size"]) * np.where(hand, 0.66, np.where(foot, 0.82, 1.0))
            layer["alpha"] = np.asarray(layer["alpha"]) * np.where(hand, 0.70, np.where(foot, 0.77, 1.0))
            under_gain = np.where(cloud["h"][ids] < 0.24, 0.83, 0.46)
            layer["alpha"] *= np.where(is_trouser[ids], under_gain, 1.0)
            layer["alpha"] *= np.where(is_skirt[ids], 1.15, 1.0)
            layer["color"] = color.astype(np.float32)
            layer.update(weight=1.0, after=None, before=None, detail=None)
            body.layers.append(layer)


def make_body(*, at, role: int = 0, ensemble: bool = False, points: int = 82000) -> Body:
    """Return an unsampled dressed Body, ready for the caller's score install.

    A closed, pleated, flared skirt ends about 23 cm above the nominal floor on
    a 1.66 m performer. Full fitted trousers remain underneath; feet and ankles
    can read through the choreography. Clothing follows the existing 120 Hz
    cloth solver with body collision, not a separate rendered skirt plate.
    """
    if isinstance(role, bool) or int(role) != role or role < 0:
        raise ValueError("role must be a nonnegative integer")
    if isinstance(points, bool) or not math.isfinite(points) or points < 12000:
        raise ValueError("points must be a finite count of at least 12000")
    role, points = int(role), int(points)
    body = Body(
        "woman", height=1.66 + 0.012 * (role % 3), at=at, facing=0,
        garment="coat", hair="bun", points=points,
        detail=dict(hand=3.6, head=1.8, foot=2.3),
        color="#e0b777", color2="#f6d9a5", bright=1.13, size=0.9,
        wind=(0.055, 0.0, 0.018), gust=0.045,
        build=0.96 + 0.008 * (role % 5), seed=2401 + 41 * role,
        look=[],
    )
    skirt = _replace_skirt(body, role)
    _dress_layers(body, skirt, role, ensemble)
    body.advanced_costume = {
        "name": "pleated performance skirt over fitted trousers",
        "hem_reference_m": 0.22,
        "flare": 2.85,
        "bell": 0.72,
        "closed_skirt": True,
        "skirt_source": skirt,
        "skirt_points": body.sources[skirt].n,
        "total_points": body.cloud["n"],
        "cloth_grid": [CLOTH_ROWS, CLOTH_COLUMNS],
        "constraint_projection_iterations": [8, 128],
        "soft_shape_iterations_per_step": 8,
        "role": role,
    }
    if body.actor._cache or body.cloth.x is not None:
        raise AssertionError("Costume creation must not evaluate choreography")
    return body


def audit_cloth(body: Body) -> dict:
    """Review every saved cloth snapshot without starting a new simulation.

    Extension limits are authoring tolerances chosen for these two films, not
    claims about a physical textile. Each stored 30 Hz state is inspected,
    including the final interpolation guard state after the declared endpoint.
    The dense rendered point cloud continues to sample these simulated cells.
    """
    system = body.cloth
    score = body.actor.advanced_score
    expected = int(np.ceil(score.duration / (cloth.DT * cloth.SNAP))) + 2
    if len(system.snaps) != expected:
        raise ValueError("Complete the declared cloth bake before auditing snapshots")
    samples = []
    failures = []
    floor = float(body.actor.origin[1] if system.ground is None else system.ground)
    for index, snapshot in enumerate(system.snaps):
        positions = np.asarray(snapshot)
        t = system.t_start + index * cloth.DT * cloth.SNAP
        if positions.shape != (system.n, 3) or not np.isfinite(positions).all():
            failures.append(dict(index=index, time_seconds=t, reason="nonfinite or invalid cloth state"))
            continue
        extension = np.maximum(system._stretch(positions) - 1.0, 0.0)
        p99 = float(np.percentile(extension, 99))
        maximum = float(extension.max())
        minimum_height = float(positions[:, 1].min())
        sample = dict(
            index=index, time_seconds=float(t), p99_edge_extension=p99,
            maximum_edge_extension=maximum, minimum_height_m=minimum_height,
        )
        samples.append(sample)
        if p99 > 0.15 or maximum > 0.35 or minimum_height < floor - 0.001:
            failures.append(sample)
    return dict(
        scope="Every saved 30 Hz cloth state, including endpoint interpolation guard; no new simulation.",
        status="passed" if not failures else "review_required",
        performance=score.name,
        snapshot_count=len(system.snaps), valid_snapshot_count=len(samples),
        simulated_vertices=system.n, rendered_body_points=body.cloud["n"],
        limits=dict(p99_edge_extension=0.15, maximum_edge_extension=0.35,
                    minimum_height_m=floor - 0.001),
        maximum_p99_extension=max((x["p99_edge_extension"] for x in samples), default=None),
        maximum_extension=max((x["maximum_edge_extension"] for x in samples), default=None),
        minimum_height_m=min((x["minimum_height_m"] for x in samples), default=None),
        failure_count=len(failures), failures=failures, samples=samples,
        limitations=[
            "The solver has body collision but no cloth self-collision or cloth interaction between performers.",
            "These are geometric checks; continuous native visual review and final encoded review remain separate.",
        ],
    )
