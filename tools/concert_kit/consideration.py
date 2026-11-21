"""Eighteen-second authored scene: a shared human effort opens a living shore.

This module is loaded as songs.consideration in an isolated renderer process.
It does not mutate any production file or replace a delivered song.
"""
import os
import numpy as np
import songs.s03_original as _base

_base.FPS = int(os.environ.get("OUT_FPS", "60"))
_base.TOTAL = 18.0
_base.NFRAMES = int(round(_base.TOTAL * _base.FPS))
_base.MUSIC_END = 18.0
_base.FADE = _base.Track([(0,1),(18,1)])
_base.EXPOSURE = _base.Track([(0,1),(18,1)])
for _p in _base.PHRASES:
    _p["form"] = _p["hold"] = _p["star"] = 1e9
_base.TITLE["form"] = 1e9
_base.TITLE_HIT = _base.NINTH = 1e9
_base.TAGLINE = dict(text=" ",t0=1e9,t1=1e9+1)
_base.CREDIT["t_in"], _base.CREDIT["t_full"] = 1e9,1e9+1
_base.WAVES = []
from songs.s03_original import *  # noqa: E402,F401,F403

from p3d.api import lin, ribbon
from p3d.camera import Rig, dolly
from tools.concert_kit.models import Seat, Path, Reeds, Flowers, Willow, Lantern, smooth
from tools.concert_kit.people import ConsiderationPair

BOTTOM_CALM = 0.0
TEXT_SHADOW = 0.0
TOTAL = 18.0
CUTS = (3.0,12.0)
_PAIR = None


class Song:
    """Neutral preview envelope. It is not represented as analyzed instrument data."""
    def __init__(self):
        self.env=np.full(NFRAMES,.40)
        self.env_slow=np.full(NFRAMES,.40)
        self.hi=np.full(NFRAMES,.20)
        self.pulse=np.zeros(NFRAMES)
        self.ridge=np.full(2048,.02,dtype="f4")
    def lantern(self,t):
        return .5,.3
    def rings_at(self,t):
        return []


class SharedLight:
    """The hand event becomes one traveling path, then a canopy of light."""
    def __init__(self,pair):
        self.pair=pair
        self.last_contact=pair.grip(7.0)

    def sample(self,t):
        out=[]
        contact=float(smooth(4.9,5.3,t)*(1-smooth(7.3,7.8,t)))
        if contact>.001:
            p=self.pair.grip(t)
            out.extend([dict(pos=p[None],size=.045,color=lin("#ee62a6"),alpha=.65*contact,kind="spark",emit=1.2),
                        dict(pos=p[None],size=.2,color=lin("#ee62a6"),alpha=.018*contact)])
        if t<11.5:
            return out or None
        # Starts at a real posed hand, reaches the shore, travels to the tree.
        start=self.pair.b.where(11.5,"palm.L")
        u=np.linspace(0,1,180)
        a=start
        b=np.array([-1.6,.18,.1])
        c=np.array([-3.7,.25,-2.3])
        d=np.array([-3.8,3.7,-2.4])
        path=((1-u)**3)[:,None]*a+3*((1-u)**2*u)[:,None]*b+3*((1-u)*u*u)[:,None]*c+(u**3)[:,None]*d
        progress=float(smooth(11.5,14.6,t))
        k=max(2,int(progress*(len(path)-1))+1)
        p=path[:k]
        gain=.75*(1-.55*float(smooth(15.5,17.5,t)))
        out.append(ribbon(p,width=.025,color=lin("#ee62a6"),alpha=gain,emit=1.4))
        out.append(ribbon(p,width=.13,color=lin("#ee62a6"),alpha=.045*gain))
        out.append(dict(pos=p[-1:],size=.10,color=lin("#ffbdde"),alpha=.7*gain,kind="spark",emit=1.8))
        # A broad rose-gold arc above the tree is a consequence, after the intimate action.
        if t>14:
            v=np.linspace(0,1,120)
            reveal=float(smooth(14,16.5,t))
            arc=np.stack([-4.7+10*v,3.1+3*np.sin(np.pi*v),-4.0-2.5*np.sin(np.pi*v)],1)
            n=max(2,int(reveal*(len(arc)-1))+1)
            out.append(ribbon(arc[:n],width=.018,color=lin("#f0acb8"),alpha=.46,emit=1.1))
            out.append(dict(pos=arc[::4][:max(1,n//4)],size=.07,color=lin("#f7cf9c"),alpha=.25,kind="petal",rot=t*.25))
        return out


def pair():
    global _PAIR
    if _PAIR is None:
        _PAIR=ConsiderationPair()
    return _PAIR


def setup(scene):
    pair().add(scene)
    scene.add("shore_path",Path(length=22,width=3.6))
    seat=Seat()
    seat.gain=lambda t:1-.88*float(smooth(8.2,10.7,t))
    scene.add("offered_rest",seat)
    scene.add("shared_light",SharedLight(pair()))
    scene.add("hero_willow",Willow(at=(-3.8,0,-2.4),height=4.5,spread=3.0,bloom=13.8,seed=31))
    scene.add("distant_willow",Willow(at=(5.8,0,-14),height=5.4,spread=3.1,bloom=14.2,seed=47))
    for i,(x,z) in enumerate([(-3.1,3.7),(2.9,1.0),(-4.0,-.6),(4.0,-3.6),(-4.5,-5.0),(4.4,-8.0)]):
        scene.add(f"shore_reeds_{i}",Reeds(at=(x,0,z),count=26,radius=.75,height=.52 if i<2 else .9,seed=12+i))
        scene.add(f"shore_flowers_{i}",Flowers(at=(x,0,z),count=15,radius=.75,height=.28 if i<2 else .42,
            seed=32+i,bloom=12.0+.18*i))
    for i,(x,y,z) in enumerate([(-2.5,2.1,-1.8),(-4.6,2.5,-2.8),(-5.0,1.6,-1.1),(3.2,.4,-6),(-1.8,.28,-8)]):
        scene.add(f"lantern_{i}",Lantern(at=(x,y,z),size=.22,seed=i,lit=12+.25*i,
            variant="hanging" if i<3 else "cup"))


CAMERA=Rig([
    dolly((4.4,2.3,9.7),(2.3,1.8,7.5),0,3,look=(-.25,.95,1.4),fov=39,aperture=.012,ease="smooth",blend=0),
    dolly((1.6,1.45,5.8),(1.1,1.55,6.0),3,12,look=[(-.18,1.0,1.52),(.0,1.05,1.85)],
          fov=35,aperture=.009,ease="smooth",blend=0),
    dolly((2.0,2.5,7.8),(6.6,5.3,14.5),12,18,look=[(-1.1,1.5,.3),(-1.2,2.0,-.5)],
          fov=42,aperture=.008,ease="smooth",blend=0),
],blend=0,shutter=.30,handheld=0,near=.1)

P3D=dict(camera=CAMERA,setup=setup,motion_samples=2,bokeh_max=.04,world=dict(
    look="night",sky_top="#02040d",sky_mid="#10192e",sky_hor="#46354d",
    sun_int=.09,sun_el=-7,sun_az=170,sun_glow=.35,sun_disc=0,
    stars=.72,milky=.30,clouds=.14,haze=.10,mist=.08,mist_height=.6,
    water="#030610",mirror=.76,mirror_min=.20,ripple=.23,
    dust=.08,bokeh=.05,lanterns=0,floats=.1,hills=1,hill_height=.8,
    exposure=.94,keep_hue=.58,dust_field=dict(n=900,n_bokeh=20),
    float_field=dict(count=110,center=(0,-10),radius=(6,60)),lights=[]))
