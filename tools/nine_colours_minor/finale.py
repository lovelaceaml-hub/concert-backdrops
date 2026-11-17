"""Carry the original nine comet trails into the luminous Earth and its symbols."""
import numpy as np
from p3d import brand as B
import reference  # noqa: F401
from nine_reference_p3d import brand as reference_brand  # noqa: F401
from nine_reference_p3d.master_brand import SymbolSwirl


def ease(a,b,t):
    u=np.clip((t-a)/(b-a),0,1)
    return u*u*(3-2*u)


def unit(v):
    return v/max(np.linalg.norm(v),1e-9)


def hermite(p0,v0,p1,v1,d,u):
    return (2*u**3-3*u*u+1)*p0+(u**3-2*u*u+u)*d*v0+(-2*u**3+3*u*u)*p1+(u**3-u*u)*d*v1


class Fade:
    wants_camera=True
    def __init__(self,inner,a,b):self.inner,self.a,self.b=inner,a,b
    def sample(self,t,cam):
        k=1-ease(self.a,self.b,t)
        if k<=0:return None
        rows=self.inner.sample(t,cam)
        if rows is None:return None
        return [dict(b,alpha=np.asarray(b.get('alpha',1))*k) for b in rows if b is not None]


def install(film,camera):
    join=49.47
    p0,q0=film._s7_braid(join)
    v0=(p0-film._s7_braid(join-.01)[0])/.01
    f0=unit(q0-p0)
    center=p0+42*f0
    radius=7.0
    end=center+np.array([8.,3.,33.])
    up0=film._s7_up(join)

    def pose(t):
        x=float(np.clip((t-join)/(51.25-join),0,1))
        p=hermite(p0,v0,end,np.array([1.,0.,0.]),51.25-join,x)
        if t>51.25:p=end+np.array([.4,.15,-.25])*min(t-51.25,8)
        target=center-np.array([0,1.0,0])*ease(50.8,51.7,t)
        # The globe starts on the braid's sightline. Keep following that same
        # point while the camera arcs around it, without dropping it below frame.
        f=unit(target-p)
        return p,p+30*f

    def up(t):
        p,q=pose(t); f=unit(q-p)
        u=unit(up0*(1-ease(join,51.1,t))+np.array([0,1,0])*ease(join,51.1,t))
        return unit(u-f*(u@f))

    camera.moves[-1]=film.Path(pose,join,61,blend=0,up=up,
        fov=lambda t:94+(50-94)*ease(join,51.1,t),aperture=0,focus=35)
    fin=B.Finale(pos=tuple(center),radius=radius,camera=camera,look='night',
        t_world=49.05,spin=6,front=-110,shrink=.78,hearts=False,
        t_settle=(50.9,51.65),t_logo=(51.5,52.4),bloom=False,
        end=dict(t=(52.4,52.7),ride=(.5,.8542,20),frac=.148),
        logo=dict(reflect=False),n=50000)
    normal_scale=fin.scale
    fin.globe.scale=lambda t:normal_scale(t)*(.04+.96*ease(48.9,50.0,t))
    swirl=SymbolSwirl(center,radius,B.LABELS,[B.EXPRESSION_COLORS[n] for n in B.LABELS],
        49.1,51.65,camera,scale=normal_scale,size=.52,orbit=(1.95,1.65),
        rise=(-.12,.40),turns=.72,n=700,life=.85,bright=.8,glow_world=.55)
    old_heads=list(film.HEADS)

    class JoinedHead:
        def __init__(self,k):
            self.k=k; self.legs=old_heads[k].legs
        def __call__(self,t):
            if t<=48.75:return old_heads[self.k](t)
            if t>=50.15:return swirl.centre(self.k,t)
            a,b=48.75,50.15; d=b-a; x=(t-a)/d
            p=old_heads[self.k](a)
            v=(old_heads[self.k](a+.01)-old_heads[self.k](a-.01))/.02
            q=swirl.centre(self.k,b)
            w=(swirl.centre(self.k,b+.01)-swirl.centre(self.k,b-.01))/.02
            return hermite(p,v,q,w,d,x)

    film.HEADS[:]=[JoinedHead(k) for k in range(9)]
    original_alpha=film.Comets._alpha
    def alpha(self,k,t):
        result=original_alpha(self,k,t) if t<48.75 else 1-ease(50.55,51.3,t)
        if k!=film.RESP:
            result*=1-ease(33.36,33.8,t)*(1-ease(40.05,40.21,t))
        return result
    film.Comets._alpha=alpha
    return fin,swirl
