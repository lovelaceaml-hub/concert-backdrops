"""A readable pearl-and-rose treatment of the established luminous dancer.

The geometry and rig match the existing advanced costume exactly.  This layer
changes material presentation only: a quiet coherent surface supports the
fine particles, instead of an almost empty silhouette filled with twinkle.
"""
from __future__ import annotations

import numpy as np

from p3d import looks
from p3d.api import lin
from tools.advanced_dance.costume import make_body as _make_body


def make_body(*, points: int = 140000, proof: bool = False):
    body = _make_body(at=(0.0, 0.0, 0.0), role=0, ensemble=False,
                      points=points)
    cloud = body.cloud
    ids = np.arange(cloud["n"])
    part = cloud["part"]
    h = cloud["h"]
    cloth = part == looks.CLOTH
    skirt = body.src_of == body.advanced_costume["skirt_source"]
    hand = part == looks.HAND
    foot = part == looks.FOOT
    hair = part == looks.HAIR
    under = cloth & ~skirt & (h < .61)

    # A long rose-to-lavender color transition and a quiet pearl bodice.
    # Ornament belongs to the cloth, so it follows the same simulated cells.
    u = np.clip((h - .27) / .36, 0.0, 1.0)
    u = u * u * (3.0 - 2.0 * u)
    garment = lin("#e9aebf")[None] * (1.0-u[:, None]) + lin("#c5b8e8")[None] * u[:, None]
    rest = cloud["rest"]
    angle = np.arctan2(rest[:, 0], rest[:, 2]-body.rig.neutral_pos[0, 2])
    pleat = .91 + .09*np.cos(angle*10.0)**2
    garment[skirt] *= pleat[skirt, None]
    waist = np.exp(-((h-.616)/.012)**2)
    hem = np.clip((.254-h)/.025, 0.0, 1.0) * skirt
    # Thin repeated petal curves suggest embroidery without noisy sparkle.
    ornament = np.exp(-((h-(.33+.020*np.cos(angle*10.0)))/.006)**2)*skirt
    gold_mix = np.clip(.48*waist + .34*hem + .24*ornament, 0.0, .65)
    garment = garment*(1-gold_mix[:, None]) + lin("#efcb8e")[None]*gold_mix[:, None]
    color = np.broadcast_to(lin("#ecc996"), (len(ids), 3)).copy()
    color[cloth] = garment[cloth]
    color[under] = lin("#c3b4d1")
    color[hair] = lin("#d8ac75")

    sizes = np.full(len(ids), .0060*body.k, np.float32)
    # A broad, low-energy cloth layer supplies coverage.  The fine luminous
    # grains above it now describe the surface instead of being the surface.
    if not proof:
        sizes[cloth & ~under] = .0114*body.k
    sizes[hand] *= .60
    sizes[foot] *= .76
    alpha = np.full(len(ids), .16 if not proof else .38, np.float32)
    if not proof:
        alpha[cloth] = 1.60
    alpha[hand] *= .75 if not proof else .88
    alpha[foot] *= .78 if not proof else .90
    alpha[hair] *= .80 if not proof else 1.0
    alpha[under] *= .42 if not proof else 1.05
    alpha[skirt] *= 1.1 if not proof else .23
    if proof:
        color[cloth] = lin("#c2cbd5")
        color[~cloth] = lin("#ead1aa")

    fill = dict(kind="soft", idx=ids, size=sizes,
                color=color.astype(np.float32), alpha=alpha,
                emit=np.full(len(ids), .48, np.float32),
                seed=cloud["seed"].copy(), twinkle=0.0, rim=(.08, 1.5),
                backlight=.02, lit=.34, weight=1.0,
                after=None, before=None, detail=None)
    if proof:
        body.layers = [fill]
    else:
        for layer in body.layers:
            ii = layer["idx"]
            layer["color"] = color[ii].astype(np.float32)
            layer["alpha"] *= .055
            layer["alpha"] *= np.where(cloth[ii], 1.0, .66)
            # The closed skirt owns the beauty surface.  Its fitted diagnostic
            # trousers must not paint pale islands through moving folds.
            layer["alpha"][under[ii]] = 0.0
            layer["emit"] *= np.where(cloth[ii], .58, .64)
            layer["twinkle"] = .035
            if layer["kind"] == "spark":
                layer["alpha"] *= .20
            # Reduce the old bright-outline/dark-interior contrast.
            layer["rim"] = (.68, 2.4)
        surface, skin_fill = dict(fill), dict(fill)
        visible_cloth = cloth & ~under
        for key in ("idx", "size", "color", "alpha", "emit", "seed"):
            surface[key] = fill[key][visible_cloth]
            skin_fill[key] = fill[key][~cloth]
        bodice = ~skirt[visible_cloth]
        surface.update(kind="disc", rim=(0.0, 1.5), backlight=0.0, lit=0.0)
        surface["emit"] = np.full(len(surface["idx"]), .12, np.float32)
        body.layers[0:0] = [surface, skin_fill]

        # Body layers deliberately expose a small portable set of controls.
        # Add the renderer's existing paint setting to the first returned
        # material batch only; sampled positions, normals and rig are exact.
        sample = body.sample

        def pearl_sample(t, cam=None):
            batches = sample(t, cam)
            if batches:
                silk = batches[0]
                # Full paint avoids reintroducing a fraction of this dense
                # coverage as additive light, which washes its colour out.
                silk["paint"] = 1.0
                silk["paint_light"] = .06
                # A mirrored alpha-composited disc cloud requires its own
                # depth ordering.  The quiet light layers supply the lake
                # reflection; omit this opaque paint layer from that pass.
                silk["reflect"] = False
                light = np.asarray(body.light)[None] - silk["pos"]
                light /= np.maximum(np.linalg.norm(light, axis=1, keepdims=True), 1e-9)
                diffuse = np.clip((silk["normal"]*light).sum(1), 0.0, 1.0)
                shade = np.where(bodice, .44 + .27*diffuse, .28 + .55*diffuse)
                silk["color"] = silk["color"]*shade[:, None]
                if cam is not None:
                    # Painting is alpha composited.  Order the existing
                    # samples so the nearest cloth owns each visible pixel.
                    distance = ((silk["pos"]-np.asarray(cam.pos)[None])**2).sum(1)
                    order = np.argsort(distance, kind="stable")[::-1]
                    for key in ("pos", "normal", "size", "color", "alpha", "emit", "seed"):
                        silk[key] = silk[key][order]
            return batches

        body.sample = pearl_sample
    body.light = (-2.6, 3.8, 3.4)
    body.fluid_appearance = dict(
        name="pearl lavender and rose, with restrained gold embroidery",
        revision=4, proof=bool(proof), rig_geometry_changed=False,
        base_points=int(cloud["n"]), material_only=True,
    )
    return body
