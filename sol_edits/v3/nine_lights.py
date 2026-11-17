"""One light, nine colours, one peace: an independent comet choreography.

Film 10 is the owner's visual reference. These paths are authored for Sol's
current cast, timing and emotional arc, from the unchanged v6 engine.
"""
import numpy as np
from p3d.api import ribbon,lin
from .effects import envelope

TAU=2*np.pi
WHITE=lin('#fff7e6')

class NineLights:
    wants_camera=True
    def __init__(self,film,cast,rise):
        self.f=film;self.cast=cast;self.rise=rise
        self.colors=[lin(e['color']) for e in film.PW.EXPRESSIONS]
        self.colors[8]=lin('#5872d2')
        self.stages=[(8.1,12.7,film.P1,0),(12.0,15.9,film.P1b,1),(15.3,22.6,film.P2,2),
            (21.9,26.1,film.P3,4),(25.4,29.45,film.P3b,5),(28.8,35.75,film.P4,6),
            (35.05,39.35,film.P5,7),(38.65,42.7,film.P5b,8)]
        r=np.random.default_rng(613);self.dust=r.random((9,44,4));self.anchors={}
    def point(self,k,t,stage):
        f=self.f
        if stage==-1:
            u=f.sc(2.65,4.4,t);a=TAU*k/9+.20*u+.22*max(t-4.4,0)
            return f.H0+f._v(np.sin(a)*4.3*u,.12+.40*u*np.cos(a),-.3+np.cos(a)*3.4*u)
        if stage==8:
            u=f.sc(42.2,44.6,t);a=TAU*k/9+.45*t;r=6*(1-u)+.6
            return f.A7+f._v(r*np.sin(a),3.3+1.0*u,r*np.cos(a))
        if stage==9:
            a=TAU*k/9+4.4*(t-44.45)+.015*self.rise(t)
            gather=f.sc(47.65,49.05,t)
            radius=(5.8+.6*np.sin(.9*(t-44.45)+k*.13))*(1-gather)+.12
            destination=f.HV*(90*f.sc(47.8,49.1,t))
            return f.A7+destination+f._v(radius*np.sin(a),self.rise(t)+22,radius*np.cos(a))
        if stage==10:
            a=TAU*k/9+1.15*(t-49.1);lat=.55*np.sin(a*.7+k)
            return f.FIN_C+1.22*f.FIN_R*f._v(np.cos(lat)*np.sin(a),np.sin(lat),np.cos(lat)*np.cos(a))
        a,b,o,leader=self.stages[stage];u=t-a
        angle=.75*u+TAU*k/9
        if k!=leader and not(stage==2 and k==3):
            radius=10+1.4*k
            return o+f._v(radius*np.sin(angle),.5+.18*k+.6*np.sin(angle*.7),-10+radius*.4*np.cos(angle))
        if stage==0:
            return o+f._v(2.0*np.sin(1.0*u-.8),.5+.85*np.sin(.55*u)**2,1.3*np.cos(u*.8))
        if stage==1:
            heart=self.anchors[1]
            return heart+f._v(1.2*np.sin(1.45*u),.20+.55*u,1.0*np.cos(1.45*u))
        if stage==2:
            phase=1.10*u+(0 if k==2 else np.pi)
            return o+f._v(1.35*np.sin(phase),.38+.29*u,1.1*np.cos(phase))
        if stage==3:
            return o+f._v(2.3*np.sin(2.9*u),2.3*np.cos(2.9*u)+2.35,-10+3.4*u)
        if stage==4:
            return o+f._v(2.0*np.sin(.95*u),1.05+.85*np.sin(.7*u),-1.7+1.0*np.cos(.95*u))
        if stage==5:
            return o+f._v(2.2*np.sin(1.25*u),.35+.65*u,2.2*np.cos(1.25*u))
        if stage==6:
            anchor=self.anchors[6]
            return anchor+f._v(1.3*np.sin(1.45*u),.35+.16*u,1.2*np.cos(1.45*u))
        return o+f._v(2.8*np.sin(1.2*u),.65+.40*u,2.4*np.cos(1.2*u))
    def trail(self,k,t,stage,g,cam,lead=True):
        if g<.002:return []
        f=self.f
        tail=1.15 if stage==9 else .85 if lead else 1.8
        start=t-tail
        if 0<=stage<8:start=max(start,self.stages[stage][0]-.15)
        if stage==-1:start=max(start,2.65)
        tt=np.linspace(start,t,72 if stage==9 else 44)
        p=np.array([self.point(k,float(q),stage) for q in tt])
        taper=np.linspace(.02,1,len(tt))**.7
        near=np.linalg.norm(p-np.asarray(cam.pos),axis=1)
        safe=np.clip((near-1.3)/1.4,0,1);safe=safe*safe*(3-2*safe)
        xy,z=cam.project(p)
        # The output-space phrases occupy the upper left; light flows around them.
        inside=(xy[:,0]>.07)&(xy[:,0]<.49)&(xy[:,1]>.40)&(xy[:,1]<.77)&(z>0)
        clear=np.where(inside,.045,1.0)
        if 0<=stage<8:
            xx,yy=xy[:,0],xy[:,1]
            def soft(a,b,x):
                u=np.clip((x-a)/(b-a),0,1);return u*u*(3-2*u)
            people=soft(.48,.55,xx)*(1-soft(.80,.87,xx))*soft(.06,.14,yy)*(1-soft(.61,.68,yy))
            clear*=1-.90*people
        alpha=g*taper*safe*clear*np.clip((z-.4)/.8,0,1)
        c=self.colors[k];core=.68*WHITE+.32*c
        width=.13 if stage==9 else .055 if lead else .08
        strength=1.0 if lead or stage in (-1,8,9,10) else .20
        alpha*=strength
        out=[ribbon(p,width=width*3.2*taper,color=c,alpha=.40*alpha,emit=1.6,twinkle=0),
             ribbon(p,width=width*taper,color=core,alpha=.65*alpha,emit=1.8,twinkle=0),
             ribbon(p,width=width*8*taper,color=c,alpha=.015*alpha,emit=1.2,twinkle=0)]
        head=p[-1:];h=float(alpha[-1])
        out += [dict(pos=head,size=width*1.7,color=core,alpha=h,emit=2.4,kind='spark',twinkle=0),
                dict(pos=head,size=width*9,color=c,alpha=.12*h,emit=1.2,kind='soft',twinkle=0)]
        # Stable shed sparks carry the colour, with continuous lifetimes and no twinkle.
        s=self.dust[k];ages=s[:,0]*tail
        q=np.array([self.point(k,float(t-age),stage) for age in ages])
        q+=(s[:,1:]-0.5)*(.15+.28*ages[:,None])
        gain=.26*g*strength*(1-ages/tail)**2
        out.append(dict(pos=q,size=.015,color=.5*WHITE+.5*c,alpha=gain,emit=1.6,kind='spark',twinkle=0))
        return out
    def sample(self,t,cam):
        f=self.f;out=[]
        if 11.8<t<16.1:self.anchors[1]=self.cast['gratitude'][0].where(t,'heart')
        if 34.9<t<39.5:self.anchors[6]=self.cast['consideration'][0].where(t,'heart')
        if t<8.6:
            seed=f.H0+f._v(0,.12,-.3)
            glow=1-f.sc(3.8,4.6,t)
            out += [dict(pos=seed[None],size=.055,color=WHITE,alpha=.8*glow,emit=2.5,kind='spark',twinkle=0),
                    dict(pos=seed[None],size=.32,color=lin('#ffdc9c'),alpha=.10*glow,kind='soft',twinkle=0)]
            g=f.sc(2.65,3.3,t)*(1-f.sc(8.0,8.6,t))
            for k in range(9):out+=self.trail(k,t,-1,g,cam)
        for j,(a,b,o,lead) in enumerate(self.stages):
            g=envelope(t,a,b,.45)
            if g<.002:continue
            for k in range(9):
                active=k==lead or(j==2 and k==3)
                out+=self.trail(k,t,j,g,cam,active)
        for stage,a,b in [(8,42.15,44.85),(9,44.25,49.45),(10,49.15,53.25)]:
            g=envelope(t,a,b,.55)
            if g>.002:
                for k in range(9):out+=self.trail(k,t,stage,g,cam)
        # A soft shared light marks acceptance of the embrace, without a frame flash.
        g=envelope(t,19.85,20.8,.38)
        if g>.002:
            p=np.mean([b.where(t,'heart') for b in self.cast['embrace']],axis=0)
            out += [dict(pos=p[None],size=.065,color=WHITE,alpha=.6*g,emit=2.5,kind='spark',twinkle=0),
                    dict(pos=p[None],size=.6,color=lin('#ffdc9e'),alpha=.08*g,kind='soft',twinkle=0)]
        return out

class LightGate:
    def __init__(self,origin):self.o=np.array(origin)
    def sample(self,t):
        g=envelope(t,22.1,26.0,.6)
        if g<.002:return None
        th=np.linspace(0,np.pi,100);out=[];color=lin('#62b2fa')
        for j in range(6):
            born=22.2+.24*j;gain=g*np.clip((t-born)/.6,0,1)
            p=self.o+np.stack([2.45*np.cos(th),2.45*np.sin(th),np.full(len(th),-j*3.7-2)],1)
            out += [ribbon(p,width=.055,color=color,alpha=.42*gain,emit=1.8,twinkle=0),
                    ribbon(p,width=.016,color=WHITE*.65+color*.35,alpha=.72*gain,emit=1.8,twinkle=0)]
        return out
