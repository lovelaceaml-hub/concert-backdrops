"""Native p3d views of the twelve implemented model variants."""
from songs.consideration import *  # noqa: F401,F403
from p3d.camera import Rig, hold
from tools.concert_kit.models import build_model

CATALOG=[
    ("seat","stone",dict(width=1.0,depth=.8)),
    ("seat","garden",dict(width=1.0,depth=.8)),
    ("path","shore",dict(length=5,width=1.7)),
    ("path","bridge",dict(length=5,width=1.7)),
    ("reeds","reed",dict(count=22,radius=.65,height=1.15)),
    ("reeds","grain",dict(count=22,radius=.65,height=1.15)),
    ("flowers","lotus",dict(count=15,radius=.75,height=.5,bloom=0)),
    ("flowers","star",dict(count=15,radius=.75,height=.5,bloom=0)),
    ("willow","willow",dict(height=3,spread=1.6,bloom=0)),
    ("willow","blossom",dict(height=3,spread=1.6,bloom=0)),
    ("lantern","hanging",dict(size=.65,lit=0)),
    ("lantern","cup",dict(size=.65,lit=0)),
]
CUTS=tuple(2.0*i for i in range(1,len(CATALOG)))


class Slot:
    def __init__(self,model,index):self.model,self.index=model,index
    def sample(self,t):
        return self.model.sample(20+t) if self.index*2<=t<(self.index+1)*2 else None


def setup(scene):
    for i,(family,variant,kw) in enumerate(CATALOG):
        y=1.0 if family=="lantern" else 0.0
        scene.add(f"{family}_{variant}",Slot(build_model(family,variant=variant,at=(i*15,y,0),seed=20+i,**kw),i))


MOVES=[]
for i,(family,variant,kw) in enumerate(CATALOG):
    x=i*15
    if family=="willow":pos=(x+2.6,2.8,6.7);target=(x,1.4,0);fov=35
    elif family=="path":pos=(x+3.8,3.4,5.5);target=(x,.2,0);fov=40
    elif family=="seat":pos=(x+1.2,1.3,2.4);target=(x,.4,0);fov=34
    else:pos=(x+1.3,1.6,3.0);target=(x,.7 if family!="lantern" else 1.1,0);fov=36
    MOVES.append(hold(pos,target,2*i,2*i+2,fov=fov,aperture=0,blend=0))

P3D=dict(P3D,camera=Rig(MOVES,blend=0,shutter=0),setup=setup,motion_samples=1,
    world={**P3D["world"],"stars":.15,"dust":0,"bokeh":0,"floats":0,"hills":0,"clouds":0,"mirror":.38})
