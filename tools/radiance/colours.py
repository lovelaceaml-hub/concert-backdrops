"""Film 10 inspired light choreography, rebuilt for the updated independent film.

The white core, saturated ribbon, soft sheath and shedding sparks follow the
visual grammar documented in docs/handover/film_10.md. Paths and timings here
are original to this staging. All samples depend only on absolute film time.
"""
import numpy as np
from scipy.interpolate import PchipInterpolator
from p3d.api import lin, ribbon


def smooth(a,b,t):
    u=np.clip((np.asarray(t)-a)/(b-a),0,1)
    return u*u*u*(u*(u*6-15)+10)


class NineColours:
    """One light visits the encounters; all nine gather into a rising braid."""
    def __init__(self,centers,starts,colors,flight):
        self.centers,self.starts=centers,starts
        self.flight=flight
        self.colors=[lin(c) for c in colors]
        self.colors[8]=lin('#5872d2')
        keys=[0,6.3]
        positions=[[0,.7,2],[0,.7,2]]
        for c,a in zip(centers,starts):
            keys.extend([float(a),float(a+3.0)])
            positions.extend([c+[0,.8,0],c+[0,.8,0]])
        keys.extend([45,47.5,50.5,54.3,62])
        positions.extend([[0,3,-170],[0,32,-174],[0,50,-174],[0,50,-174],[0,50,-174]])
        self.path=PchipInterpolator(keys,np.array(positions),axis=0)
        self.spark=np.random.default_rng(810).random((9,180,4))

    def head(self,k,ts):
        ts=np.asarray(ts)
        c=self.path(np.clip(ts+.45,0,62))
        a=self.starts[k]
        own=smooth(a-.8,a+.2,ts)*(1-smooth(a+3.05,a+4.0,ts))
        gathered=smooth(42.6,45,ts)
        opening=1-smooth(6.3,8.5,ts)
        angle=ts*.95+k*2*np.pi/9
        radius=(7.5-3.6*own)*(1-opening)+(1+5*smooth(2,6.3,ts))*opening
        offset=np.stack([radius*np.cos(angle),
                         1.1+1.0*np.sin(angle*.8),
                         radius*.6*np.sin(angle)],axis=-1)
        # The nine fan low beneath the full opening information.
        offset[...,1]*=1-.85*opening
        offset*=smooth(1.9,4,ts)[...,None]
        p=c+offset
        # The finale carries the eye upward through a nine-colour column.
        phase=k*2*np.pi/9+ts*1.3
        y=3+57*smooth(43.3,49.0,ts)
        rad=7.5-2.8*smooth(46.7,49.5,ts)
        braid=np.stack([rad*np.cos(phase),y,-174+rad*np.sin(phase)],axis=-1)
        p=p*(1-gathered[...,None])+braid*gathered[...,None]
        globe=smooth(49,50.5,ts)
        orbit=np.stack([4.3*np.cos(phase),50+4.0*np.sin(phase),
                        -174+1.7*np.cos(phase*.7+k)],axis=-1)
        return p*(1-globe[...,None])+orbit*globe[...,None]

    def sample(self,t):
        if t>=54.4:return None
        out=[]
        end=1-float(smooth(52.8,54.4,t))
        for k,c in enumerate(self.colors):
            own=float(smooth(self.starts[k]-.8,self.starts[k]+.2,t)*
                      (1-smooth(self.starts[k]+3.05,self.starts[k]+4,t)))
            group=float(1-smooth(6.3,8.5,t)+smooth(42.6,45,t))
            alpha=(.26+.74*max(own,group))*end
            ts=np.linspace(max(0,t-2.6),t,130)
            pts=self.head(k,ts)
            v=np.linspace(0,1,len(ts))
            width=.15+.09*own+.10*group
            core=.35*c+.65*lin('#fff6ee')
            out.extend([
                dict(pos=pts,size=width*2.4*(.15+.85*v),color=c,
                     alpha=alpha*.055*v,kind='soft',dof=0),
                ribbon(pts,width=width*(.12+.88*v),color=c,
                       alpha=alpha*.85*v,emit=2),
                ribbon(pts,width=width*.20*(.15+.85*v),color=core,
                       alpha=alpha*.9*v,emit=2.6),
                dict(pos=pts[-1:],size=width*.8,color=core,alpha=alpha,
                     emit=4,kind='spark',twinkle=0),
                dict(pos=pts[-1:],size=width*5.5,color=c,alpha=alpha*.13,kind='soft')])
            sp=self.spark[k]
            f=(sp[:,0]+t*.4)%1
            idx=f*(len(pts)-1)
            low=np.floor(idx).astype(int);high=np.minimum(low+1,len(pts)-1)
            q=pts[low]*(1-(idx-low)[:,None])+pts[high]*(idx-low)[:,None]
            q+=(sp[:,1:4]-.5)*(.5*(1-f))[:,None]
            out.append(dict(pos=q,size=.025+.025*sp[:,2],color=core,
                            alpha=alpha*.8*f**1.5,emit=1.7,kind='disc',twinkle=0))
        # A gate of standing blue half hoops, completed in the mirror lake.
        gate=float(smooth(21.5,23,t)*(1-smooth(27,28.2,t)))
        if gate>0:
            c=self.centers[4]
            theta=np.linspace(0,np.pi,180)
            for j in range(6):
                z=c[2]+12-j*5
                p=np.stack([c[0]+5.5*np.cos(theta),.04+5.5*np.sin(theta),
                            np.full(len(theta),z)],1)
                col=lin('#62b2fa')
                out.append(ribbon(p,width=.075,color=col,alpha=.55*gate,emit=2))
                out.append(ribbon(p,width=.015,color=lin('#e2f5ff'),alpha=.8*gate,emit=2))
        # A tall braid remains behind its heads, so the ascent has real depth.
        braid=float(smooth(42.8,45,t)*(1-smooth(49,51,t)))
        if braid>0:
            u=np.linspace(0,1,650)
            for k,c in enumerate(self.colors):
                theta=k*2*np.pi/9+u*10.0+t*.12
                r=7.5-2.0*u
                p=np.stack([r*np.cos(theta),.1+62*u,-174+r*np.sin(theta)],1)
                out.append(ribbon(p,width=.15,color=c,alpha=.7*braid,emit=1.8))
                out.append(ribbon(p,width=.035,color=.4*c+.6,
                                  alpha=.6*braid,emit=2))
        # Two fine helices embrace the two women without filling their faces.
        helix=float(smooth(16.2,17.2,t)*(1-smooth(23.2,24.2,t)))
        if helix>0:
            center=self.path(t)-[0,.8,0]
            u=np.linspace(0,1,260)
            for k in [2,3]:
                angle=u*2*np.pi+t*.45+(k-2)*np.pi
                p=center+np.stack([2.2*np.cos(angle),.12+u*2.7,2.2*np.sin(angle)],1)
                out.append(ribbon(p,width=.045,color=self.colors[k],alpha=.6*helix,emit=1.8))
        return out


class StarGarden:
    """Fine stars at real depths reveal travel, with warm lanterns at gratitude."""
    def __init__(self):
        rng=np.random.default_rng(818)
        self.pos=rng.uniform([-42,.1,-214],[42,75,8],(11000,3))
        self.seed=rng.random(len(self.pos))
        self.size=.015+.035*self.seed**4
        self.color=lin('#d7ddff')[None]*(1-self.seed[:,None])+.9*self.seed[:,None]

    def sample(self,t):
        a=1-float(smooth(50.5,54.3,t))
        if a<=0:return None
        return dict(pos=self.pos,size=self.size,color=self.color,alpha=.65*a,
                    kind='disc',dof=.1,fog=.015,twinkle=0,seed=self.seed)
