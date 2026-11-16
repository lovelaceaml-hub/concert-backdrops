"""Nine Colours render 1, with refined people, clear text and current cards."""
import numpy as np
from songs.s03_original import *  # noqa: F401,F403
from tools.nine_colours import original as O
from tools.nine_colours.original import *  # noqa: F401,F403
from tools.nine_colours.cast import build
from tools.radiance.celebration import Celebration
from p3d import brand as BR
from p3d import master_brand as MB

TOTAL = SONG_END = MUSIC_END = 62.0
NFRAMES = int(TOTAL*FPS)
O._base.TOTAL=TOTAL
O._base.NFRAMES=NFRAMES
O._bodies=lambda:build(O)

# Only these first readings move to accommodate the seven-second opening.
O._SPECS[0].update(t_in=5.1,t_read0=5.4,t_read1=7.9,t_out=8.05)
O._SPECS[1].update(t_in=8.05,t_read0=8.4,t_read1=10.95,t_out=11.2)
for spec in O._SPECS:
    spec.update(pill=True,sharp=1,bright=.9,halo=.3,sparkle=.025,leave='fade')
    spec['t_out']=min(spec['t_out'],spec['t_read1']+.30)
    if spec.get('arrive')=='morph':
        spec.update(arrive='reveal')
        spec.pop('source',None)


def clean_leave(t,info):
    if info['state']=='leave':return dict(pos=info['home'],assist=1)


O.WORDS=O.PW.Words(O._SPECS,camera=O._LAYOUT,reflect=False,drive=clean_leave)
for k,a,b in ((O.GREET,5.1,5.4),(O.CONC,8.05,8.4)):
    old=O.HEADS[k].legs[0]
    O.HEADS[k].legs[0]=(a,b,old[2],min(old[3],.5),old[4])


def focus(t,default):
    """Rack focus only toward a phrase in front of this shot's camera."""
    d=np.asarray(default(t) if callable(default) else default,np.float64)
    cut=max([c for c in [0,*O.SEC[3:]] if c<=t]+[-1e9])
    st=O._LAYOUT_SIMPLE.state(t)
    fwd=O._unit(np.asarray(st.target)-st.pos)
    acc=np.zeros(3);total=top=0
    for w in O.WORDS:
        if w.t_in<cut-.01:continue
        k=O._sc(w.t_read0-.8,w.t_read0,t)*(1-O._sc(w.t_read1,w.t_read1+.8,t))
        if k<=0:continue
        c=np.asarray(w.centre(t))
        if np.dot(c-st.pos,fwd)<.5:continue
        acc+=k*c;total+=k;top=max(top,k)
    return d if total<=0 else d+(acc/total-d)*top


CAMERA=O._rig(focus)
CAMERA.free=True
CAMERA.shutter=.6
# Keep every original flight through the spiral. The requested world-to-logo
# finale replaces only the old morning arch, beginning on the same music cue.
CENTER=np.array([0.,18.,0.])
CAMERA.moves[-1]=O.fly([(49.47,(0,62,100),CENTER),(50.5,(9,24,34),CENTER),
                       (51.5,(5,20,24),CENTER),(53,(0,18,23),CENTER),
                       (60,(-1,18.3,24),CENTER)],blend=0,ease='out',fov=50,aperture=0,focus=24)
O.CAMERA=CAMERA
FINALE=BR.Finale(pos=tuple(CENTER),radius=4.2,camera=CAMERA,look='night',
    t_world=49.47,spin=5,front=-40,shrink=.52,
    hearts=dict(t0=49.8,t1=51.8,n=27),t_settle=(50.8,52),t_logo=(51.3,52.8),
    bloom=dict(t=52.7,strength=.10,glow=.6),look_after='pastel',blend=1.2,
    end=dict(t=(52.8,53.4),ride=(.5,.862,14),frac=.157),
    logo=dict(reflect=False),n=60000)


class ScreenClear:
    """Keep moving lights behind the words and away from the camera lens."""
    wants_camera=True
    def __init__(self,inner):self.inner=inner
    def sample(self,t,cam=None):
        ps=self.inner
        res=ps.sample(t,cam) if getattr(ps,'wants_camera',False) else ps.sample(t)
        if res is None or cam is None:return res
        boxes=[]
        for w in O.WORDS:
            if w.t_in-.2<=t<=w.t_out:
                b=O.PW.screen_box(w,cam,t)
                if b[4]:boxes.append((b[0]-.025,b[1]+.025,b[2]-.03,b[3]+.035))
        if t<5.1:boxes.append((.12,.88,.4,.97))
        elif t<52.8:boxes.append((.015,.36,.015,.15))
        out=[]
        for batch in res if isinstance(res,(list,tuple)) else [res]:
            if batch is None:continue
            b=dict(batch)
            for pk,ak in [('pos','alpha'),('pos2','alpha2')]:
                if b.get(pk) is None:continue
                p=np.asarray(b[pk]).reshape(-1,3)
                xy,z=cam.project(p)
                f=O._ss(.2,1.5,np.linalg.norm(p-np.asarray(cam.pos),axis=1))
                for x0,x1,y0,y1 in boxes:
                    inside=O._ss(x0-.02,x0,xy[:,0])*(1-O._ss(x1,x1+.02,xy[:,0]))*O._ss(y0-.02,y0,xy[:,1])*(1-O._ss(y1,y1+.02,xy[:,1]))
                    f=np.minimum(f,1-.94*inside*(z>0))
                b[ak]=np.asarray(b.get(ak,1))*f
            out.append(b)
        return out


class PassingReflection:
    wants_camera=True
    def __init__(self,word):self.word=word
    def sample(self,t,cam):
        w=self.word
        if not w.t_read1<t<w.t_out:return None
        got=w.sample(t,cam);out=[]
        for b in got if isinstance(got,list) else [got]:
            if b is not None:
                d=dict(b);d['alpha']=np.asarray(d.get('alpha',1))*.45*O._ss(w.t_read1,w.t_read1+.08,t)
                out.append(d)
        return out


def setup(scene):
    scene.add('seed',ScreenClear(O.Seed()))
    scene.add('hoops',ScreenClear(O.PW.KeepClear(O.Hoops(),O.WORDS)))
    scene.add('lanterns',ScreenClear(O.PW.KeepClear(O.Lanterns(),O.WORDS)))
    for name,body in O._bodies().items():body.add(scene,name,mask=False)
    scene.add('flares',ScreenClear(O.Flares()))
    scene.add('comets',ScreenClear(O.PW.KeepClear(O.Comets(),O.WORDS)))
    O.WORDS.add_to(scene)
    for word in O.WORDS:
        scene.add('passing reflection '+word.name,PassingReflection(word),reflect=True)
    FINALE.add_to(scene)
    scene.add('nine symbols illuminate the world',MB.SymbolSwirl(tuple(CENTER),4.2,
        O.PW.LABELS,[O.PW.COLORS[k] for k in O.PW.LABELS],49.5,52.5,CAMERA,
        scale=FINALE.scale,size=.42,orbit=(1.9,1.65),turns=.55,n=600,life=1.4,
        bright=.65,glow_world=.4),reflect=False)
    O.WORDS.check(CAMERA)


def reading_clear(t):
    # Fragment-level protection also catches a long ribbon crossing a phrase
    # when both of its endpoints happen to lie outside that phrase's box.
    cam=CAMERA.state(t)
    boxes=[]
    for word in O.WORDS:
        if word.t_in<=t<=word.t_out:
            x0,x1,y0,y1,front,*_=O.PW.screen_box(word,cam,t)
            if front:
                amount=.96*O._ss(word.t_in,word.t_in+.12,t)*(1-O._ss(word.t_read1,word.t_out,t))
                boxes.append(dict(box=(x0-.015,y0-.02,x1+.015,y1+.025),amount=amount,soft=.025))
    if t<5.1:
        boxes.append(dict(box=(.12,.40,.88,.97),amount=.95,soft=.04))
    elif len(boxes)<2 and t<52.8:
        boxes.append(dict(box=(.015,.015,.36,.15),amount=.8,soft=.02))
    return boxes


WORLD=dict(O.WORLD)
WORLD.pop('arch',None)
# The seed remains visible, but its screen-wide rays cannot wash out the card.
WORLD['light']=dict(O.WORLD['light'],rays=.06,
    strength=lambda t:.15*O.WORLD['light']['strength'](t))
WORLD['look']=[k for k in O.WORLD['look'] if k[0]<49.47]
P3D=dict(O.P3D,camera=CAMERA,world=FINALE.world(O.WORDS.world(WORLD)),
    setup=setup,clear=reading_clear,motion_blur=.6,motion_samples=1,
    bursts=[dict(b,strength=min(b['strength'],.6)) for b in O.P3D['bursts'][:-1]]+FINALE.bursts())
TITLES=dict(opening=dict(t_end=7.1,dissolve=.1,y=.30,palette='night'),
    signature=dict(windows=[(7.1,54.8,'bl','night')],fade=.25,protect=dict(keep=0)),
    end_card=dict(t_in=54.5,fade=.5,scale=1,backdrop=True,veil=.65,ambient_motes=True))
CREDIT=dict(O.CREDIT,t_in=1e9,t_full=1e9,t_move=1e9,t_rest=1e9)


def smooth(a,b,t):return O._ss(a,b,t)
