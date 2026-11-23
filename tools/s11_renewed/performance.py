"""Song 11's renewed, clothed conductor performance.

Install after loading the original film and before building its Scene. The
original score, native blue orchestra, gold instruments and all scene modules
remain source references. This revision authors the hero's whole-body phrasing
and clothing, then derives every baton/stream contact from his evaluated rig.
"""
from __future__ import annotations

from functools import lru_cache
import types

import numpy as np

from .garment import dress, dress_crowd


class _InnerSilhouette:
    """Occlusion pulled inside the sparkling garment, without a dark outline."""

    def __init__(self, body):
        self.body = body
        self.idx = np.flatnonzero(body.cloud['seed'] < 60000.0 / body.cloud['n'])

    def sample(self, t):
        body = self.body
        if body.show is not None and not body.show[0] <= t <= body.show[1]:
            return []
        pos, normals = body.points_at(t, self.idx)
        on = body._on(t)[self.idx]
        keep = on > .25
        if not keep.any():
            return []
        # The pinned renderer's default body mask expands all sampled points.
        # Contract ours along its own surface normals before drawing the discs.
        pos = pos[keep] - normals[keep] * (.024 * body.k)
        return dict(pos=body._w(pos, t), size=.018 * body.k * body.scale,
                    alpha=on[keep], kind='soft')


def _finish_hero_costume(body):
    """Readable tailored piping, independent of the crowd garment geometry."""
    from p3d.api import lin
    scale = body.rig.height / 1.86
    p = body.cloud['rest'] / scale
    x, y, z = p.T
    front = z > .10
    lapel_x = np.interp(y, [1.15, 1.47, 1.56], [.025, .15, .09])
    lapels = front & (y > 1.15) & (y < 1.56) & (abs(abs(x) - lapel_x) < .012)
    seam = front & (abs(x) < .008) & (y > .55) & (y < 1.16)
    ii = np.flatnonzero(lapels | seam)
    # Dense dim fabric is already first. Raise only that base gently so the
    # middle of the coat retains its sapphire color under its subdued sparkle.
    body.layers[0]['color'] *= 1.40
    body.layers[0]['alpha'] *= 1.15
    body.layers.append(dict(kind='soft', idx=ii,
        size=np.full(len(ii), .007 * body.k, np.float32),
        color=np.broadcast_to(lin('#e7bd72') * 1.2, (len(ii), 3)).astype(np.float32),
        alpha=np.full(len(ii), .90, np.float32), emit=np.full(len(ii), 1.5, np.float32),
        seed=body.cloud['seed'][ii], twinkle=.03, rim=(.0, 2.0),
        backlight=0.0, lit=0.0, weight=1.0, after=None, before=None, detail=None))


def _continuous_hand_score(source):
    """Continuous version of the original musical score, without stepped taps.

    The source's thirteen discrete Gaussian taps each jump when they cross a
    phrase boundary, particularly the breath-to-strings cue. Blur the actual
    240 Hz score as one continuous trajectory, then interpolate it with a cubic
    spline. The measured beats, hand roles, cues and 25 ms follow-through remain.
    """
    from scipy.interpolate import CubicSpline
    from scipy.ndimage import gaussian_filter1d
    hz = 240.0
    times = np.arange(int(93 * hz), int(254 * hz) + 1, dtype=float) / hz
    raw = np.asarray([source._hands_raw(float(t)) for t in times])
    soft = gaussian_filter1d(raw, .070 * hz, axis=0, mode='nearest', truncate=3.5)
    crisp = gaussian_filter1d(raw, .045 * hz, axis=0, mode='nearest', truncate=3.5)

    def ease(a, b):
        u = np.clip((times - a) / (b - a), 0, 1)
        return u * u * (3 - 2 * u)

    fast = 1 - ease(109.7, 110.3) + ease(121.15, 121.50) * (1 - ease(139.7, 140.3))
    fast = np.clip(fast, 0, 1)[:, None, None]
    return CubicSpline(times, soft * (1 - fast) + crisp * fast, axis=0,
                       bc_type='natural')


def install(film):
    if getattr(film, '_renewed_performance_installed', False):
        return
    film._renewed_performance_installed = True
    D = film.S_DANCE
    from p3d import bodymath as bm
    from p3d.body import Body
    DEG = np.pi / 180
    # Separate every newly baked crowd from the frozen approved reference cache.
    # Both namespaces use their own Body class but share the authored clothing.
    import hashlib
    import importlib
    import os
    from pathlib import Path
    payload = Path(__file__).with_name('garment.py').read_bytes() + b'crowd-fps=30;modest-sources-v1'
    cache_tag = hashlib.sha256(payload).hexdigest()[:20]
    previous_cache = Path(os.environ.get('P3D_CACHE', 'work/s11_renewed/cache'))
    os.environ['P3D_CACHE'] = str(previous_cache / ('modest-figures-' + cache_tag))
    for namespace in ('p3d', 'nine_reference_p3d'):
        module = importlib.import_module(namespace + '.body')
        cls = module.Body
        if getattr(cls, '_s11_modest_sources', False):
            continue
        original_init = cls.__init__
        def modest_init(self, *args, _init=original_init, **kwargs):
            _init(self, *args, **kwargs)
            if self.garment is not None and self.part is None:
                dress_crowd(self)
        cls.__init__ = modest_init
        cls._s11_modest_sources = True
        # Thirty pose samples each second for the new crowd prototypes; the
        # frame renderer still evaluates and exposes at native delivery time.
        crowd = importlib.import_module(namespace + '.crowd')
        crowd.FPS = 30.0
    D._BODIES.clear()
    neutral_ankles = {}
    hand_curve = [None]

    def score_hands(t):
        if hand_curve[0] is None:
            hand_curve[0] = _continuous_hand_score(D)
        r, l = hand_curve[0](float(t) - .025)
        return r, l

    def safe_hand(actor, P, side, point):
        _, joints, _ = actor.mo.local_fk(P)
        shoulder = joints[actor.rig.idx['upperarm01.' + side]]
        delta = point - shoulder
        radius = np.linalg.norm(delta)
        reach = sum(actor.mo.arm_len[side]) * .94 + .045
        if radius > reach:
            # Smoothly keep a little elbow bend; no hyperextended held poses.
            delta *= reach / max(radius, 1e-8)
        return shoulder + delta

    def authored_pose(actor, t):
        mo, rig = actor.mo, actor.rig
        P = mo.identity()
        r, l = score_hands(t)
        lead_r, lead_l = score_hands(t + .11)
        trail_r, _ = score_hands(t - .09)
        center = .5 * (lead_r + lead_l)
        calm = 1.0 - .70 * D._sc(116.6, 117.2, t) * (1 - D._sc(121.0, 121.6, t))
        held = D._sc(247.0, 247.5, t) * (1 - D._sc(248.9, 249.35, t))
        energy = (.52 + .48 * film.loud(t)) * (1 - .55 * held)
        # The torso anticipates the hand phrase; the head settles a little later.
        side = np.tanh(center[0] * 3.0)
        forward = np.tanh((center[2] - .42) * 3.5)
        lift = np.clip((center[1] - 1.27) / .7, -.6, 1)
        P.pos = np.array([.025 * side, -.014, .014 * forward])
        P.rot = bm.qmul(bm.qy(3.5 * side * DEG), bm.qz(-1.4 * side * DEG))
        twist = 6.5 * np.tanh((lead_r[0] + .22) * 2.8) * energy
        reach = 2.2 * forward - 3.0 * lift
        for bone, amount in [('spine05', .16), ('spine04', .23), ('spine03', .25), ('spine02', .22), ('spine01', .14)]:
            mo._set(P, bone, bm.qeuler(reach * amount * DEG, twist * amount * DEG,
                                      -2.2 * side * amount * DEG))
        # Stable soles through weight shifts, without introducing walking or a bounce.
        for side_name, sg in [('L', 1), ('R', -1)]:
            target = neutral_ankles[side_name]
            mo.leg_to(P, side_name, target, knee=np.array([sg * .14, .05, 1.0]),
                      foot=bm.qy(sg * 6.0 * DEG))
            mo._set(P, 'clavicle.' + side_name,
                    bm.qeuler(0.0, -sg * (2.5 + 2.0 * energy) * DEG, sg * (1.0 + 1.5 * lift) * DEG))
        # Each arm receives an independent musical purpose. Target arcs retain the
        # source's measured beat grid and its summons, breath, strings and fermata.
        velocity = np.clip((r - trail_r) / .09, -2, 2)
        r = safe_hand(actor, P, 'R', r)
        l = safe_hand(actor, P, 'L', l)
        palm_r = np.array([-.10 - .06 * velocity[0], -.58, .76 + .05 * velocity[1]])
        hush = D._sc(115.7, 116.25, t) * (1 - D._sc(120.95, 121.65, t))
        palm_l = np.array([.04, .12 - .77 * hush, .74])
        mo.arm_reach(P, 'R', r, end='palm', palm=palm_r, wrist=-5.0,
                     pole=np.array([-1.0, -.28, .18]))
        mo.arm_reach(P, 'L', l, end='palm', palm=palm_l, wrist=-4.0,
                     pole=np.array([1.0, -.30, .12]))
        mo.hand_pose(P, 'R', 'pinch')
        mo.hand_pose(P, 'L', ('open', 'relaxed', .2 + .25 * held))
        gaze = np.tanh((trail_r[0] + .22) * 2.0)
        mo._set(P, 'neck02', bm.qeuler((-1.2 - 2.2 * lift) * DEG, -2.5 * gaze * DEG, -.8 * side * DEG))
        mo._set(P, 'head', bm.qeuler((-2.8 * lift + .7 * np.sin(t * 1.4) * calm) * DEG,
                                   -3.5 * gaze * DEG, -.8 * side * DEG))
        P.ground = 1.0
        return P

    def bodies():
        if D._BODIES:
            return D._BODIES
        c = D.COND_C
        b = Body('man', height=D.HEIGHT, at=(c[0], c[2]), facing=180., motion='stand', gesture=(),
                 garment='coat', hair=False,
                 look=[dict(name='rim', bright=.90, power=2.2),
                       dict(name='glitter', bright=.65, glints=.0004)],
                 color='#3b83c8', color2='#d6e9ff', points=90000, bright=1.8,
                 size=1.1, light=D.LIGHT_AT, show=(94., 252.), fade=.15, seed=8.)
        for side_name, sg in [('L', 1), ('R', -1)]:
            neutral_ankles[side_name] = b.rig.neutral_pos[b.rig.idx['foot.' + side_name]] + np.array([sg * .025, 0, 0])
        b.actor.base_pose = types.MethodType(authored_pose, b.actor)
        # The score already authors the wrist and fingers, so the generic hand
        # inertia pass is disabled; final contacts use this evaluated pose.
        b.actor.life = False
        b.actor._cache.clear()
        dress(b)
        _finish_hero_costume(b)
        D._BODIES['cond'] = b
        return D._BODIES

    @lru_cache(maxsize=48000)
    def attachment(t):
        b = bodies()['cond']
        r = b.where(t, 'pinch.R')
        _, normal, fingers = b.actor.palm(t, 'R')
        direction = -normal * .90 + fingers * .25
        direction /= max(np.linalg.norm(direction), 1e-8)
        tip = r + direction * D.BATON
        left = b.where(t, 'fingertips.L')
        return r, tip, b.where(t, 'palm.L'), left

    history_clock = [None]

    def history_contacts(t):
        # Delayed sweeps used to create many independently shifted 480 Hz FK
        # grids. Their luminous histories can share one 120 Hz trajectory. The
        # current baton and each comet's launch anchor still evaluate exactly.
        sample = float(t) * 120.0
        index = int(np.floor(sample))
        fraction = sample - index
        a = attachment(round(index / 120.0, 6))
        if fraction < 1e-8:
            return a
        b = attachment(round((index + 1) / 120.0, 6))
        return tuple(x + (y - x) * fraction for x, y in zip(a, b))

    def contacts(t):
        exact = history_clock[0]
        if exact is not None and all(value is None or abs(float(t) - value) > 1e-7 for value in exact):
            return history_contacts(t)
        return attachment(round(float(t), 6))

    stream_sample = D.Stream.sample

    def stream_with_shared_history(stream, t):
        previous = history_clock[0]
        history_clock[0] = (float(t), stream.ts)
        try:
            return stream_sample(stream, t)
        finally:
            history_clock[0] = previous

    D.Stream.sample = stream_with_shared_history

    D._bodies = bodies
    D.hand_R = lambda t: contacts(t)[0]
    D.tip = lambda t: contacts(t)[1]
    D.hand_L = lambda t: contacts(t)[2]
    D.tip_L = lambda t: contacts(t)[3]
    original_add = D.add

    def add(scene):
        original_add(scene)
        body = bodies()['cond']
        # A dim opaque silhouette inside the independently modelled coat prevents
        # stars/buildings from shining through it and resembling naked anatomy.
        for entry in scene.entries():
            if entry.name == 'conductor of light':
                mask = body.mask(strength=lambda t: .85 * D.dance_k(t), grow=0.0,
                                 soft=.45, source=_InnerSilhouette(body))
                entry.mask = mask
                break
    D.add = add
    # Broader musical phrasing in the choir: reduce the old per-beat sideways
    # rock while retaining every singer's pose and gold book alignment.
    S = film.S_STAGE
    old_sway = S.choir_sway
    S.choir_sway = lambda t: old_sway(t) * .55
    film._renewed_performance = dict(version=1,
        hero='continuous measured-beat conductor with anticipatory torso, fixed soles and independently solved hands',
        hand_score='240 Hz raw score, smoothly blended Gaussian phrasing, continuous cubic interpolation',
        clothing='independent closed knee-length sapphire coat; every crowd torso/seat surface simplified',
        props='baton base at evaluated thumb/index pinch; streams from evaluated tip/fingertips',
        trail_sampling='shared 120 Hz interpolated history; current contacts and launch anchors exact',
        ensemble='30 Hz prototype poses, 55 percent lateral sway; original instrument score retained',
        source_motion='authored performance, not motion capture')
