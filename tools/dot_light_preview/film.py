"""The Light We Share: independent abstract-light interpretation, no human cast."""
import numpy as np
from songs.demo_titles import *
from p3d.camera import Rig, hold
from p3d import words as PW, brand as BR
from p3d.api import lin
from track import Track
TOTAL=62.; FPS=60; NFRAMES=3720; MUSIC_END=62.; SONG_END=62.
FADE=Track([(0,1),(62,1)])
EXPOSURE=Track([(0,1),(62,1)])
from songs import s03_original as ORIGINAL
ORIGINAL.FADE=FADE; ORIGINAL.EXPOSURE=EXPOSURE
ORIGINAL.TOTAL=TOTAL; ORIGINAL.NFRAMES=NFRAMES; ORIGINAL.MUSIC_END=MUSIC_END; ORIGINAL.FPS=FPS
CAMERA=Rig([hold((0,3.8,12),(0,3.0,-2),0,62,drift=(.15,.02,-.08))],fov=42,handheld=0,aperture=.01)
TITLES=dict(opening=dict(t_end=8.,dissolve=1.,y=.30,palette='day'),
    signature=dict(windows=[(7.4,54.5,'bl','day')],fade=.4),
    end_card=dict(t_in=54.2,fade=.7,backdrop='pastel'),logo=None)
SPECS=[dict(expr=label,t_in=8+4*i,t_read0=8.4+4*i,t_read1=11.5+4*i,t_out=11.98+4*i,
    ride=(.5,.66,10),em=PW.em_for(CAMERA,10+4*i,10,86),face='screen',arrive='reveal',edge='out',
    leave='rise',speed=.35,paint='#272751',color=PW.COLORS[label],bright=.5,halo=.12,pill=True,n=120000)
    for i,label in enumerate(PW.LABELS)]
WORDS=PW.Words(SPECS,camera=CAMERA)
def smooth(a,b,t):
    u=np.clip((t-a)/(b-a),0,1);return u*u*(3-2*u)
def window(a,b,t):return smooth(a,a+.6,t)*(1-smooth(b-.6,b,t))
class LightStory:
    wants_camera=True
    """Pairs of light meet, offer, shelter, yield, listen, lift and celebrate."""
    def __init__(self):self.u=np.linspace(0,1,700)
    def sample(self,t,cam):
        out=[];u=self.u
        if t<8:
            # A bright falling drop sends expanding rings over the warm lake.
            fall=smooth(2.0,5.5,t)
            out.append(dict(pos=np.array([[3.6,2.8-2.55*fall,-1.5]]),size=.18,color=lin('#ffc84f'),emit=2.5,alpha=1,kind='spark'))
            for n in range(4):
                age=max(t-4.8-n*.55,0);r=.2+age*.65;a=2*np.pi*u
                out.append(dict(pos=np.stack([3.6+r*np.cos(a),.13+0*u,-1.5+r*np.sin(a)],1),
                    size=.035,color=lin('#ffbe4a'),alpha=float(smooth(0,.3,age))*.65,emit=1.3,kind='soft'))
        elif t<44:
            i=min(8,int((t-8)//4));v=(t-8-i*4)/4;env=float(window(8+4*i,12+4*i,t))
            col=PW.COLORS[PW.LABELS[i]]
            # All actions stay below the reading box and above the signature.
            for side in (-1,1):
                a=2*np.pi*u
                r=.8+.08*np.sin(t*.8)
                sep=1.5-.7*np.sin(v*np.pi)**2
                x=side*sep+r*np.cos(a); y=.95+.62*np.sin(a)
                if i==1: y+=.35*np.sin(v*np.pi)*np.sin(a)**2
                if i==2: y+=side*.25*(1-smooth(.2,.8,v))
                if i==3: x=side*.5+1.15*np.cos(a);y=1+.7*np.sin(a)
                if i==4: x=side*(1+smooth(.1,.8,v))+.2*np.sin(a);y=.4+1.8*u
                if i==5: x=side*(1.2-.25*np.sin(v*np.pi))+.3*np.sin(a);y=.5+1.2*u
                if i==6: x=side*(.1+1.5*u);y=.45+1.5*(1-u)**2
                if i==7: x=side*(.9+.5*u);y=.45+u*(.7+smooth(.1,.8,v))
                if i==8: x=side*.75+1.1*np.cos(a);y=.9+.55*np.sin(a)+.25*np.sin(v*np.pi)
                out.append(dict(pos=np.stack([x,y,np.full_like(u,-1.5)],1),size=.045,
                    color=lin(col),alpha=env*.9,emit=1.6,kind='soft',reflect=True))
                k=np.arange(28)/28;aa=2*np.pi*k+t*.35
                out.append(dict(pos=np.stack([side*sep+.8*np.cos(aa),.95+.62*np.sin(aa),np.full_like(k,-1.5)],1),
                    size=.045,color=lin('#ffd77b'),alpha=env,emit=2,kind='spark'))
        if t<48:
            # Nine long gold petals carry a slowly breathing, luminous horizon.
            env=1-float(smooth(44,48,t))
            for i in range(9):
                a=i*2*np.pi/9;r=4*np.sin(np.pi*u)
                out.append(dict(pos=np.stack([r*np.cos(a),.1+.3*np.sin(np.pi*u),-2+r*np.sin(a)],1),
                    size=.035,color=lin('#e5a52d'),alpha=env*.65,emit=1.,kind='soft'))
        if 7.4<t<54.5:
            for b in out:
                xy,depth=cam.project(np.asarray(b['pos']))
                keep=1-(1-smooth(.52,.6,xy[:,0]))*(1-smooth(.23,.31,xy[:,1]))
                b['alpha']=np.asarray(b.get('alpha',1))*keep
        return out
FINALE=BR.Finale(pos=(0,2.5,-2),radius=2.2,camera=CAMERA,look='day',t_world=44.2,
    t_settle=(49.5,51.5),t_logo=(51,53.5),bloom=False,clouds=False,n=16000,
    end=dict(t=(53.5,54.2),ride=(.5,.84,14),frac=.13),cradle=None)
class OrbitSymbol:
    wants_camera=True
    def __init__(self,i,label):
        self.i=i
        self.symbol=BR.Constellation(label,pos=(0,0,0),size=.6,camera=CAMERA,t0=44.5,dur=1.2,hold=4.5,out=1.2,intensity=.8,reflect=False,n=350)
    def sample(self,t,cam):
        got=self.symbol.sample(t,cam)
        if got is None:return None
        angle=self.i*2*np.pi/9+.28*(t-44.5)
        offset=np.array([3.1*np.cos(angle),2.5+2.4*np.sin(angle),-1.7])
        result=[]
        for original in got if isinstance(got,list) else [got]:
            b=dict(original)
            for k in ('pos','pos2'):
                if k in b:b[k]=np.asarray(b[k])+offset
            result.append(b)
        return result

def setup(scene):
    scene.add('light story',LightStory())
    for w in WORDS.words:
        mask=w.mask();mask.strength=lambda t,w=w:float(w.t_in<=t<=w.t_out)
        scene.add('word '+w.name,w,reflect=False,mask=mask)
        scene.add('word '+w.name+' lights',w.lights,reflect=False)
    FINALE.add_to(scene)
    for i,label in enumerate(PW.LABELS):scene.add('orbit symbol '+label,OrbitSymbol(i,label),reflect=False)
P3D=dict(camera=CAMERA,setup=setup,world=dict(look='cream',arch=None,clouds=.3,stars=0,dust=.03,bokeh=.01,
    sky_top='#f8ddba',sky_mid='#ecc08d',sky_hor='#cf8f43',water='#b77b38',
    sun_int=.25,sun_disc=0,rays=.15,mirror=.4))
