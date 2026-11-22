"""Two complete dance films in the established luminous concert world."""
from __future__ import annotations
import os
import numpy as np

from p3d.camera import Rig,dolly,hold,orbit
from tools.cinematic_ten.dancers import Stage
from tools.concert_kit.models import Willow,Flowers,Lantern
from .costume import make_body
from .score import install,CLOCKS,DURATION
from .props import PerformanceFan,GestureLight
from .lights import LightArchitecture,LandingLight
from .cache import load_cloth

PLACEMENTS=((-3.3,0,-2.9),(-1.65,0,-1.1),(0,0,.40),(1.65,0,-1.1),(3.3,0,-2.9))
CAST_POINTS=(46000,62000,92000,62000,46000)
SOLO_POINTS=105000
SOLO_PLACEMENT=(0,0,.14)
FAN_COLORS=("#ca8fcf","#9cbfdf","#e2b879","#b39edc","#9ecdc2")


def cuts(mode):
    return tuple(round(CLOCKS[mode]["beat_seconds"][b]*60)/60 for b in (16,32,48))


def make_cast(ensemble=False):
    positions=PLACEMENTS if ensemble else (SOLO_PLACEMENT,)
    bodies,fans=[],[]
    for role,at in enumerate(positions):
        points=CAST_POINTS[role] if ensemble else SOLO_POINTS
        body=make_body(at=at,role=role,ensemble=ensemble,points=points)
        install(body,ensemble=ensemble,role=role)
        load_cloth(body)
        bodies.append(body)
        for side in ("R","L"):
            color=FAN_COLORS[role] if ensemble else ("#c78ad2" if side=="R" else "#e3a0bd")
            fans.append(PerformanceFan(body,side,radius=.42,color=color,
                seed=240+role*17+(side=="L"),points=6500 if ensemble else 10500))
    return bodies,fans


def build(ensemble=False):
    mode="ensemble" if ensemble else "solo"
    a,b,c=cuts(mode)
    if not ensemble:
        camera=Rig([
            dolly((.55,1.73,4.85),(-.15,1.72,4.72),0,a,look=(-.12,1.14,.04),fov=37,blend=0,ease="smooth"),
            hold((.08,1.72,4.96),(.08,1.12,-.03),a,b,fov=37,blend=0),
            dolly((1.70,1.80,4.55),(.40,1.74,4.82),b,c,look=(-.05,1.13,.08),fov=37,blend=0,ease="smooth"),
            dolly((.06,1.76,4.95),(.06,1.94,5.10),c,DURATION,look=(.05,1.19,.11),fov=37,blend=0,ease="smooth")
        ],blend=0,aperture=.003,shutter=.35,near=.1)
    else:
        camera=Rig([
            dolly((-.45,2.10,7.1),(.20,2.18,7.00),0,a,look=(0,1.14,-1.10),fov=39,blend=0,ease="smooth"),
            hold((0,2.16,7.15),(0,1.10,-1.12),a,b,fov=39,blend=0),
            orbit((0,1.1,-1.1),radius=8.2,height=(2.20,2.65),a0=-9,a1=8,
                  t0=b,t1=c,look=(0,1.13,-1.1),fov=39,blend=0,ease="smooth"),
            dolly((0,2.20,7.1),(0,2.38,7.35),c,DURATION,look=(0,1.15,-1.05),fov=39,blend=0,ease="smooth")
        ],blend=0,aperture=.002,shutter=.35,near=.1)

    def setup(scene):
        bodies,fans=make_cast(ensemble)
        scene.advanced_bodies=bodies
        scene.advanced_fans=fans
        scene.add("performance_stage",Stage(radius=5.1 if ensemble else 2.3,
                  center=(0,0,-.4),color="#a89ac9",seed=333))
        for j,body in enumerate(bodies):
            body.add(scene,"performer_"+str(j),mask=dict(strength=.28,grow=0))
        for j,fan in enumerate(fans):
            scene.add("held_fan_"+str(j),fan)
        scene.add("concert_light_architecture",LightArchitecture(bodies[len(bodies)//2].actor.advanced_score,wide=ensemble))
        scene.add("contact_light",LandingLight(bodies))
        scene.add("choreographed_fan_light",GestureLight(fans,ensemble=ensemble))
        width=8.0 if ensemble else 5.7
        for j,side in enumerate((-1,1)):
            tree=Willow(at=(side*width,0,-6.3),height=4.9,spread=2.5,
                        variant="blossom",bloom=-3,seed=810+j)
            tree.gain=lambda t:.32
            scene.add("flowering_shore_"+str(j),tree)
        for j,(x,z) in enumerate(((-3.5,-3),(3.8,-3.5),(-6.0,-7),(6.3,-8))):
            if ensemble:
                x*=1.6
            scene.add("shore_lantern_"+str(j),Lantern(at=(x,.24,z),size=.12,seed=902+j,lit=-2,variant="cup"))
    world=dict(look="night",sky_top="#030718",sky_mid="#101d36",sky_hor="#614b63",
        sun_int=.11,sun_el=-5,sun_az=175,sun_glow=.30,sun_disc=0,
        stars=.22,milky=.11,clouds=.10,haze=.035,mist=.013,mist_height=.12,
        water="#060c20",mirror=.83,mirror_min=.24,ripple=.085,
        dust=.010,bokeh=.003,lanterns=0,floats=.017,hills=1,hill_height=.55,
        exposure=.94,keep_hue=.68,dust_field=dict(n=320,n_bokeh=5),
        float_field=dict(count=42,center=(0,-12),radius=(9,60)),lights=[])
    if ensemble:
        world.update(sky_top="#061121",sky_mid="#1b2b45",sky_hor="#876b83",
                     water="#0c172b",sun_int=.15,sun_el=-1,sun_az=-40)
    return dict(camera=camera,setup=setup,world=world,motion_samples=2,bokeh_max=.02,
                sky_res=.5,cuts=cuts(mode))
