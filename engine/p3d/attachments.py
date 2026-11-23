"""Prop grip frames sampled from final posed hands, not authored cue targets."""
import math

import numpy as np


def _unit(value, fallback):
    a = np.asarray(value, np.float64)
    if a.shape != (3,) or not np.isfinite(a).all():
        raise ValueError("hand frame vectors must be finite 3-vectors")
    length = float(np.linalg.norm(a))
    return a / length if length > 1e-9 else np.asarray(fallback, np.float64)


def final_hand_frame(body, t, side="R", *, forward_offset=0.018, normal_offset=0.006,
                     roll=0.0, tilt=0.0):
    """Return final world (pivot, across, outward, normal) for a held prop.

    Sample Body.where and Actor.palm after all pose, grounding and hand placement.
    Offsets are metres along the final fingers and palm normal. roll and tilt are
    fixed grip angles in radians about the palm pivot, not another animation path.
    Defaults reproduce the fan trio's grip math. No rig or body state is changed.
    """
    if side not in ("L", "R"):
        raise ValueError("hand side must be L or R")
    if not all(math.isfinite(v) for v in (t, forward_offset, normal_offset, roll, tilt)):
        raise ValueError("hand frame time and grip offsets must be finite")
    p, normal = body.where(float(t), "palm." + side, normal=True)
    p = np.asarray(p, np.float64)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError("final palm position must be a finite 3-vector")
    normal = _unit(normal, (0, 0, 1))
    actor = getattr(body, "actor", None)
    if actor is not None and hasattr(actor, "palm"):
        forward = actor.palm(float(t), side)[2]
        if hasattr(body, "_wdir"):
            forward = body._wdir(forward, float(t))
    else:
        forward = body.where(float(t), "fingertips." + side) - p
    forward = _unit(forward - normal * np.dot(forward, normal), (0, 1, 0))
    across = _unit(np.cross(forward, normal), (1, 0, 0))
    normal = _unit(np.cross(across, forward), (0, 0, 1))
    pivot = p + forward * forward_offset + normal * normal_offset
    tilted = forward * np.cos(tilt) + normal * np.sin(tilt)
    normal = _unit(np.cross(across, tilted), (0, 0, 1))
    outward = tilted * np.cos(roll) + across * np.sin(roll)
    across = across * np.cos(roll) - tilted * np.sin(roll)
    return pivot, across, outward, normal
