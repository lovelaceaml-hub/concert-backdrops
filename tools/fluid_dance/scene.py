"""One complete flowing fan phrase, shown clearly in the concert's light world.

The proof uses the identical rig/motion with a static full-body camera and
quiet material.  Beauty has one continuous, gently eased camera move.  Motion,
costume and prop attachments are evaluated before any decorative light.
"""
from __future__ import annotations

import os

import numpy as np

from p3d.api import lin, ribbon
from p3d.camera import Rig, dolly, hold
from tools.advanced_dance.props import PerformanceFan
from tools.concert_kit.models import Willow, Lantern, segments
from .costume import make_body

DURATION = 12.0
FPS = 60
CUTS = ()


class PearlFan(PerformanceFan):
    """The same finite gripped fan with a quiet, more legible silk surface."""

    def sample(self, t):
        batches = super().sample(t)
        face = batches[0]
        face["alpha"] = np.full(len(face["pos"]), 1.60, np.float32)
        face["size"] = .0105
        face["kind"] = "disc"
        face["emit"] = .12
        face["rim"] = (0.0, 1.5)
        face["paint"] = 1.0
        face["paint_light"] = .06
        # Layering points from an edge-on fan should reveal its finite silk
        # thickness without accumulating a saturated streak of light.
        batches[1]["alpha"] = np.asarray(batches[1]["alpha"])*.80
        batches[1]["emit"] = np.asarray(batches[1]["emit"])*.70
        batches[3]["alpha"] = np.asarray(batches[3]["alpha"])*.70
        batches[3]["emit"] = np.asarray(batches[3]["emit"])*.65
        batches[3]["size"] = np.asarray(batches[3]["size"])*.85
        return batches


class QuietStage:
    static = True

    def __init__(self, proof=False):
        self.proof = proof
        rng = np.random.default_rng(62211)
        count = 15000 if not proof else 21000
        a = rng.uniform(0, 2*np.pi, count)
        r = np.sqrt(rng.random(count))*2.10
        self.points = np.stack([r*np.cos(a), np.full(count, .003),
                                .70*r*np.sin(a)], axis=1)
        self.sizes = rng.uniform(.008, .016, count)

    def sample(self, t):
        out = [dict(pos=self.points, size=self.sizes,
                    color=lin("#68798c" if self.proof else "#776985"),
                    alpha=.15 if self.proof else .052,
                    kind="soft", emit=.3, twinkle=0, reflect=False)]
        a = np.linspace(0, 2*np.pi, 360)
        curves = [np.stack([2.1*k*np.cos(a), np.full(len(a), .008),
                            1.47*k*np.sin(a)], axis=1) for k in (1.0, 1.025)]
        out.append(segments(curves, "#b7b2c8", width=.0035,
                            alpha=.16 if self.proof else .20, emit=.5,
                            reflect=False))
        if self.proof:
            grid = []
            for z in np.arange(-1.0, 1.01, .5):
                grid.append(np.array([[-1.8,.005,z],[1.8,.005,z]]))
            for x in np.arange(-1.5, 1.51, .5):
                grid.append(np.array([[x,.005,-1.2],[x,.005,1.2]]))
            out.append(segments(grid, "#75889d", width=.0025,
                                alpha=.15, emit=.25, reflect=False))
        return out


class DistantPetals:
    """Sparse framing arcs behind and above the full performance envelope."""
    static = True

    def sample(self, t):
        curves = []
        u = np.linspace(.06, np.pi-.06, 220)
        for side in (-1,1):
            for k in range(3):
                x = side*(3.5 + .25*k + .85*np.cos(u))
                y = .10 + (2.9+.16*k)*np.sin(u)
                z = -5.5 - .25*k + .16*np.sin(2*u)
                curves.append(np.stack([x,y,z], axis=1))
        return [segments(curves, "#bba1d5", width=.005,
                         alpha=.085, emit=.55, twinkle=0)]


class FanAfterglow:
    """Short paths from actual solved fan tips; no generated movement cues."""

    def __init__(self, fans):
        self.fans = fans
        self.times = np.linspace(0.0, DURATION, int(DURATION*FPS)+1)
        self.tracks = np.asarray([
            [fan.tip(float(t)) for t in self.times] for fan in fans
        ], dtype=np.float64)
        self.velocity = np.gradient(self.tracks, 1/FPS, axis=1)

    def sample(self, t):
        out = []
        ages = np.linspace(.20, 0, 32)
        stamps = np.clip(t-ages, 0, DURATION)
        for k, fan in enumerate(self.fans):
            path = np.stack([np.interp(stamps, self.times, self.tracks[k,:,a])
                             for a in range(3)], axis=1)
            speed = np.linalg.norm([np.interp(t, self.times, self.velocity[k,:,a])
                                    for a in range(3)])
            gain = np.clip((speed-.30)/1.6, 0.0, 1.0)
            if gain > .01:
                fade = (1-ages/.20)**1.8
                out.append(ribbon(path, width=.004+.005*fade,
                                  color=fan.color*.6+lin("#f0cf99")*.4,
                                  alpha=.14*fade*gain, emit=.7,
                                  twinkle=0))
        return out


def make_performer(*, proof=False, points=140000, install_performance=None,
                   cloth_cache=None):
    """Construct an unsampled matching rig, then install its final performance."""
    from .score import install
    body = make_body(points=points, proof=proof)
    install(body)
    bundle = os.environ.get("FLUID_DANCE_BUNDLE")
    if install_performance is not None:
        install_performance(body)
    elif bundle:
        from .bundle import install_bundle
        install_bundle(body, bundle)
    cache = cloth_cache or os.environ.get("FLUID_DANCE_CLOTH")
    if cache:
        from .prepare import load_cloth
        load_cloth(body, cache)
    return body


def build(mode="beauty", *, install_performance=None, cloth_cache=None):
    if mode not in ("beauty", "proof"):
        raise ValueError("Fluid scene mode must be beauty or proof")
    proof = mode == "proof"
    if proof:
        camera = Rig([hold((.62,1.58,5.10), (.08,1.03,0),
                           0,DURATION,fov=33,blend=0)],
                     aperture=0, shutter=.32, near=.1)
    else:
        camera = Rig([dolly((.50,1.62,5.08),(-.18,1.70,4.95),
                            0,DURATION,look=(.05,1.04,0),fov=33,
                            blend=0,ease="smooth")],
                     aperture=.0015, shutter=.36, near=.1)

    def setup(scene):
        body = make_performer(proof=proof, install_performance=install_performance,
                              cloth_cache=cloth_cache)
        scene.fluid_body = body
        scene.advanced_bodies = [body]
        scene.add("quiet_performance_floor", QuietStage(proof))
        body.add(scene,"pearl_and_rose_dancer",mask=dict(strength=.66,grow=0))
        fans = [PearlFan(body,side,radius=.38,
                        color=color,seed=722+(side=="L"),points=11000)
                for side,color in (("R","#d3ace3"),("L","#e9b4bf"))]
        scene.fluid_fans = fans
        for j,fan in enumerate(fans):
            scene.add("pleated_fan_"+str(j),fan)
        if not proof:
            scene.add("subtle_fan_afterglow",FanAfterglow(fans))
            scene.add("distant_petal_architecture",DistantPetals())
            for j,side in enumerate((-1,1)):
                tree = Willow(at=(side*4.9,0,-6.8),height=3.6,spread=2.0,
                              variant="blossom",bloom=-3,seed=952+j)
                tree.gain=lambda t: .20
                scene.add("framing_blossom_"+str(j),tree)
            for j,(x,z) in enumerate(((-2.7,-2.9),(2.8,-3.1),(-4.8,-5.8),(4.8,-6.0))):
                scene.add("shore_lantern_"+str(j),
                          Lantern(at=(x,.17,z),size=.10,seed=710+j,
                                  lit=-2,variant="cup"))

    world=dict(look="night",sky_top="#10182d",sky_mid="#26314d",
               sky_hor="#887b91",sun_int=.12,sun_el=-3,sun_az=-35,
               sun_glow=.18,sun_disc=0,stars=.12,milky=.045,clouds=.045,
               haze=.018,mist=.002,mist_height=.05,
               water="#132131",mirror=.56,mirror_min=.12,ripple=.045,
               dust=.002,bokeh=0,lanterns=0,floats=.004,hills=1,
               hill_height=.42,exposure=1.01,keep_hue=.78,
               dust_field=dict(n=95,n_bokeh=0),
               float_field=dict(count=12,center=(0,-12),radius=(8,40)),
               lights=[])
    if proof:
        world.update(sky_top="#192432",sky_mid="#243344",sky_hor="#3e4c5e",
                     water="#1b2938",stars=0,milky=0,clouds=0,haze=0,mist=0,
                     mirror=.05,mirror_min=0,ripple=0,dust=0,floats=0,hills=0,
                     float_field=dict(count=0,center=(0,-12),radius=(8,40)))
    return dict(camera=camera,setup=setup,world=world,motion_samples=2,
                bokeh_max=.01,sky_res=.65,cuts=())
