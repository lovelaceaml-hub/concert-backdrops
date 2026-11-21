"""One actor-instance response, with complete-pose interpolation.

The original shared capture and contact remain unchanged. This module does not
patch an engine class or modify the registered concert kit's source.
"""


def response_weight(t):
    """Quintic arrival, a readable hold, and a continuous return."""
    def smooth(a, b, x):
        u = max(0.0, min(1.0, (float(x) - a) / (b - a)))
        return u * u * u * (u * (6.0 * u - 15.0) + 10.0)
    return smooth(9.4, 10.2, t) * (1.0 - smooth(11.5, 12.3, t))


def install_response(pair):
    """Replace only the recipient's response, before any geometry is sampled.

    The full endpoint is solved at weight one. A quaternion interpolation of the
    complete poses then gives the gesture its weight. This avoids repeatedly
    solving a partly applied arm endpoint during the arrival or return.
    """
    from p3d import motion

    actor = pair.b.actor
    if getattr(actor, "concert_response_revision", False):
        raise RuntimeError("Response revision was already installed")
    original_base = actor.base_pose
    removed = [g for g in actor.gest if g[2] == "hand_on_heart"]
    if len(removed) != 1:
        raise RuntimeError("Expected the frozen kit's one hand-on-heart entry")
    actor.gest = [g for g in actor.gest if g[2] != "hand_on_heart"]

    def posed(t):
        neutral = original_base(t).copy()
        weight = response_weight(t)
        if weight <= 0.0:
            return neutral
        endpoint = neutral.copy()
        actor.mo.gesture("hand_on_heart", endpoint, 1.0, t,
                         max(0.0, t - 9.4), side="L", bow=10.0)
        return motion.blend(neutral, endpoint, weight)

    actor.base_pose = posed
    actor.concert_response_revision = True
    actor._cache.clear()
    for name in ("_sk", "_pts", "_anchors"):
        getattr(pair.b, name).clear()
    return {"removed_gesture": removed[0], "in": [9.4, 10.2],
            "hold": [10.2, 11.5], "out": [11.5, 12.3],
            "method": "solve complete endpoint then quaternion-blend complete poses",
            "living_hands_retained": True, "handshake_retained": True}
