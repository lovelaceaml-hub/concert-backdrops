"""The original Film 10 ride, upgraded without replacing its concept or soundtrack."""
import types
import numpy as np
from sol_edits.v4 import original as O
from sol_edits.v4.original import *
from p3d.body import Body,Hands
from p3d import pairs,bodymath as bm

TOTAL=62.0
NFRAMES=round(TOTAL*FPS)
O._base.NFRAMES=NFRAMES
O._base.TOTAL=TOTAL
O._base.MUSIC_END=60.0
O._base.SONG_END=62.0

# Keep the original scene clock. The output adds two quiet seconds in render.py.
O.TITLES.clear()
O.TITLES.update(opening=dict(t_end=5.2,dissolve=.2,build=0,y=.30,palette='night'),
    signature=dict(windows=[(5.2,52.6,'bl','night')],fade=.3),
    end_card=dict(t_in=52.6,t_out=63,fade=.4,reveal='fade',veil=.85))
TITLES=O.TITLES

# Let the new opening read for seven seconds before the first main phrase.
for label,times in [('Greeting',(5.2,5.55,8.05,8.25)),('Concession',(8.25,8.65,11.2,11.5))]:
    word=O.WORDS[label]
    word.t_in,word.t_read0,word.t_read1,word.t_out=times
    for spec in O._SPECS:
        if spec.get('expr')==label:
            spec.update(zip(('t_in','t_read0','t_read1','t_out'),times))
    k=O.GREET if label=='Greeting' else O.CONC
    old=O.HEADS[k].legs[0]
    O.HEADS[k].legs[0]=(times[0],times[1],old[2],.35,.4)
for word in O.WORDS:
    word.sparkle=.06
    word.halo=.55
    if word.name!='Date':
        assert word.t_read1-word.t_read0>=2.5-1e-6
O.WORDS['Date'].t_in=39.5
O.WORDS['Date'].t_read0=40.0
O.WORDS['Date'].width*=.76
O.WORDS['Date'].bright=.75
O.WORDS['Date'].halo=.35
O.WORDS['Date']._g=None
O._DATE_SHIFT.clear()

GOLD=dict(look=dict(name='glitter',glints=.00028,seams=.42,size=.90),
          color='#efb75d',color2='#ffe5af',bright=.58,detail=dict(head=3,hand=2))

def person(shape,at,show,seed,facing=0,gesture=(),motion='stand',**kw):
    return Body(shape,at=at,show=show,seed=seed,facing=facing,gesture=gesture,motion=motion,
        garment='dress' if shape=='woman' else 'tunic',hair='tied' if shape=='woman' else 'short',
        points=85000,fade=.55,wind=(.08,0,-.04),**GOLD,**kw)

def bodies():
    if O._BODIES:return O._BODIES
    B=O._BODIES
    # A small same-gender greeting retains the original flight's staging.
    for k in range(2):
        B['welcome'+str(k)]=person('man',(2.1+1.0*k,193.0),(4.6,8.4),12+k,facing=72 if k==0 else 288,
            gesture=[(5.1+.2*k,8.1,'bow',dict(amount=11,ease=.9))])
    for i in range(6):
        side=-1 if i%2==0 else 1;z=O.TUNNEL_Z0-O.HOOP_GAP*(.25+.55*i)
        B['gate'+str(i)]=person('woman' if i%3!=1 else 'man',(side*3.3,z),(6.9+.15*i,12),20+i,
            facing=90 if side<0 else 270,
            gesture=[(7.3+.2*i,12,'after_you',dict(side='L' if side<0 else 'R',bow=4,ease=1.2))])
    o=O.C3
    a=dict(shape='woman',height=1.64,garment='dress',hair='bun',points=110000,seed=3,
        at=[(0,(o[0]-.5,o[2]-.09)),(16.3,(o[0]-.5,o[2]-.09)),(17.4,(o[0]-.19,o[2]-.09))],
        show=(13,20.4),fade=.65,motion=[(-1e9,'stand'),(16.3,'shuffle',dict(blend=.5)),(17.5,'stand',dict(blend=.6))],
        gesture=[(13.4,17.3,'open_hands',dict(bow=8,ease=1.1)),(13.8,17.3,'bow',dict(amount=9,ease=1.1))],**GOLD)
    b=dict(shape='woman',height=1.60,garment='dress',hair='tied',points=110000,seed=4,
        at=[(0,(o[0]+.5,o[2]+.09)),(16.3,(o[0]+.5,o[2]+.09)),(17.4,(o[0]+.19,o[2]+.09))],
        show=(13,20.4),fade=.65,motion=[(-1e9,'stand'),(16.3,'shuffle',dict(blend=.5)),(17.5,'stand',dict(blend=.6))],
        gesture=[(13.8,17.3,'listen',dict(amount=.35,ease=1.2))],**GOLD)
    B['sorry'],B['kind']=pairs.embrace(17.1,at=(o[0],o[2]),facing=90,a=a,b=b,
        until=20.4,gap=.38,side=.09,ease=1.15)
    B['dancer']=person('woman',(O.D4[0],O.D4[2]),(19.6,27.1),6,facing=30,motion=[(17.5,'dance')])
    for i,(az,r) in enumerate(((205,7.5),(235,8.5),(262,7.8))):
        p=O.D4+O.at3(az,r)
        B['fan'+str(i)]=person('woman' if i==1 else 'man',(p[0],p[2]),(19.8,25.8),30+i,facing=(az+180)%360,
            gesture=[(20.6+.2*i,25.8,'clap',dict(period=.78+.05*i,height=0,width=0,ease=.8))])
    hs=Hands(meet=tuple(O.H5),t_touch=O.HANDS_T,axis=90,color='#f2bc71',color2='#ffe0a2',
        look=GOLD['look'],shapes=('man','man'),approach=2.6,apart=.55,tilt=18,points=95000,bright=.65,shed=False)
    B['hand_gold'],B['hand_rose']=hs['left'],hs['right']
    for body in (hs['left'],hs['right']):body.show=(26.6,30.4);body.fade=.4
    O._REFS['hands_flare']=hs['flare']
    B['bower']=person('woman',(O.E5[0],O.E5[2]),(29.9,33.6),7,facing=6,
        gesture=[(30.3,33.7,'hand_on_heart',dict(bow=7,ease=1.0)),(30.8,33.7,'bow',dict(amount=11,ease=1.15))])
    O._REFS['bower']=B['bower']
    B['speaker']=person('woman',(O.F6[0]-.45,O.F6[2]),(33.1,40.4),9,facing=90,
        gesture=[(34.1,40.3,'explain',dict(side='L',period=3,ease=1.2))])
    B['listener']=person('man',(O.F6[0]+.45,O.F6[2]),(33.1,40.4),10,facing=270,
        gesture=[(34.5,40.3,'listen',dict(amount=.5,ease=1.1)),(35.1,40.3,'nod',dict(period=3,amount=4))])
    B['praying']=person('woman',(O.G7[0],O.G7[2]),(40,47.4),11,facing=180,
        motion=[(-1e9,'kneel',dict(dur=.01,sit=.75,hands='pray'))],
        gesture=[(40.1,47.3,'bow',dict(amount=6,ease=1.5))])
    for j in range(8):
        az=118+124*j/7;p=O.G7+O.at3(az,10.5+.8*(j%2))
        B['prayer_witness'+str(j)]=person('woman' if j%2==0 else 'man',(p[0],p[2]),(42.2,46.7),40+j,
            facing=(az+180)%360,gesture=[(42.7+.08*j,46.6,'hand_on_heart',dict(bow=5,ease=1.2))])
    for name,body in B.items():
        # Pure raw references prevent history recursion in contact gestures.
        original=body.actor.frame
        def frame(self,t,lock=True,gest=True,life=True,original=original):
            return original(t,lock=lock,gest=gest,life=life if gest else False)
        body.actor.frame=types.MethodType(frame,body.actor)
        if name=='dancer':
            original_pose=body.actor.base_pose
            def base_pose(self,t,original_pose=original_pose):
                p=original_pose(t).copy();a=original_pose(t-1/60);b=original_pose(t+1/60)
                upper=self.rig.bone_region<6
                p.q[upper]=bm.qslerp(p.q[upper],bm.qslerp(a.q[upper],b.q[upper],.5),.35)
                return p
            body.actor.base_pose=types.MethodType(base_pose,body.actor)
        body.actor._cache.clear()
    return B

O._BODIES.clear();O._bodies=bodies

class Steady:
    def __init__(self,inner):
        self.inner=inner;self.wants_camera=True
        self.inner_camera=getattr(inner,'wants_camera',False)
        if hasattr(inner,'gain'):self.gain=inner.gain
    def sample(self,t,cam=None):
        res=self.inner.sample(t,cam) if self.inner_camera else self.inner.sample(t)
        if res is None:return None
        out=[]
        for batch in res if isinstance(res,(list,tuple)) else [res]:
            if batch is None:continue
            b=dict(batch,twinkle=0,flash=min(float(batch.get('flash',0)),.4))
            if cam is not None and b.get('pos2') is not None:
                p=np.asarray(b['pos']);q=np.asarray(b['pos2']);forward=O._unit(cam.target-cam.pos)
                depth=np.minimum((p-cam.pos)@forward,(q-cam.pos)@forward)
                near=O._ss(.8,2.8,depth)
                b['alpha']=np.asarray(b.get('alpha',1))*near
                b['alpha2']=np.asarray(b.get('alpha2',b.get('alpha',1)))*near
                b['size']=np.minimum(b.get('size',.02),np.maximum(depth,0)*.10)
                b['size2']=np.minimum(b.get('size2',b['size']),np.maximum(depth,0)*.10)
            out.append(b)
        return out

class SceneProxy:
    def __init__(self,scene):self.scene=scene
    def add(self,name,pointset,**kw):
        kw.pop('mask',None)
        return self.scene.add(name,Steady(pointset),**kw)

def setup(scene):
    proxy=SceneProxy(scene)
    from sol_edits.v4.paths import install
    install(O,bodies())
    for name,ps in [('seed',O.ScreenClear(O.Seed())),('hoops',O.ScreenClear(O.PW.KeepClear(O.Hoops(),O.WORDS))),
                    ('lanterns',O.ScreenClear(O.PW.KeepClear(O.Lanterns(),O.WORDS)))]:proxy.add(name,ps)
    for name,body in bodies().items():body.add(proxy,name,mask=False)
    proxy.add('flares',O.ScreenClear(O.Flares()))
    proxy.add('comets',O.PW.KeepClear(O.Comets(),O.WORDS))
    echo=O.PW.Word(label='',lines=['Please, after you.'],pos=(0,1.25,36),width=6.2,
        face='fixed',facing=0,t_in=11.45,t_read0=11.8,t_read1=12.55,t_out=13.1,
        arrive='reveal',leave='fade',color='#62b2fa',bright=.7,halo=.4,sparkle=0,
        reflect=True,n=32000,n_label=0)
    proxy.add('passing words reflected in the gate',echo,reflect=True)
    O.WORDS.add_to(proxy)
    O.WORDS.check(O.CAMERA)

# Preserve the ride, including its half loop and rising corkscrew.
O.CAMERA.handheld=0
O._LAYOUT.handheld=0
WORLD=dict(O.WORLD)
WORLD['look']=[(x[0],x[1],max(.65,x[2] if len(x)>2 else .65)) for x in O.WORLD['look']]
WORLD['keep_hue']=.75
WORLD['react']=dict(beat=.2,level=.18)
P3D=dict(O.P3D,setup=setup,world=dict(WORLD,shafts=O.P3D['world']['shafts']),motion_blur=.8)
P3D['bursts']=[dict(b,strength=min(b['strength'],.7),rise=.14,fall=.4) for b in O.P3D['bursts']]

# No old title can remain on top of the updated official end card.
CREDIT=dict(O.CREDIT,t_in=1e9,t_full=1e9+1)
