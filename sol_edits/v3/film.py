"""When Love Becomes Light: Sol V3's independent creative treatment from v6.

One standing apology grows into an embrace; a gentle camera carries the light
through listening, prayer and practical kindness into the world. All approved
campaign copy and brand geometry comes from the untouched v6 engine.
"""
import types
import numpy as np
from songs import master_peace as film
from p3d.api import CameraState
from p3d.body import Body
from p3d import pairs

CUTS = [8.35, 12.30, 15.65, 22.25, 25.75, 29.10, 35.40, 39.00, 42.35, 44.55, 49.1]
DISSOLVE = 0.65
SHOT = None
v = film._v


def shot_at(t):
    return int(np.searchsorted(CUTS, t, side='right'))


def orbit(o,t,a,b,az0,az1,r0,r1,y0,y1,sx=.64,sy=.65,height=1.03,fov=43):
    u=film.sc(a,b,t)
    az=np.radians(az0+(az1-az0)*u)
    radius=r0+(r1-r0)*u
    p=o+v(np.sin(az)*radius,y0+(y1-y0)*u,np.cos(az)*radius)
    return p,film._aim(p,o+v(0,height,0),sx,sy,fov),fov


def rise_y(t):
    return 5+145*film.sc(44.35,49.15,t)


def pose(t,j):
    if j==0:
        u=film.sc(0,8.6,t)
        p=film.C0+v(-1.05+2.1*u,.20+.55*u,.6-.9*u)
        return p,film.H0+v(0,1.9,-34),49
    if j==1:
        return orbit(film.P1,t,8.05,12.6,-31,11,6.0,4.9,2.2,1.5,sx=.66,sy=.65)
    if j==2:
        return orbit(film.P1b,t,11.95,16.0,-26,19,5.8,4.5,2.3,1.45,sx=.68,sy=.65)
    if j==3:
        # The approach and embrace gain intimacy without a camera cut.
        return orbit(film.P2,t,15.2,22.7,-37,32,5.0,3.15,1.9,1.55,sx=.64,sy=.63,height=1.12,fov=43)
    if j==4:
        return orbit(film.P3,t,21.85,26.15,-25,21,8.4,6.3,2.6,1.4,sx=.62,sy=.64)
    if j==5:
        return orbit(film.P3b,t,25.3,29.6,29,-19,5.8,4.4,2.1,1.5,sx=.63,sy=.64)
    if j==6:
        return orbit(film.P4,t,28.65,35.8,-33,18,9.6,5.5,4.3,1.8,sx=.64,sy=.66,height=.95,fov=48)
    if j==7:
        return orbit(film.P5,t,34.95,39.5,-61,-12,6.5,4.8,2.4,1.45,sx=.64,sy=.65,height=.95,fov=47)
    if j==8:
        return orbit(film.P5b,t,38.55,42.8,-26,24,6,4.6,1.8,2.35,sx=.64,sy=.65,height=1.0,fov=45)
    if j==9:
        u=film.sc(41.9,44.8,t)
        p=film.A7+v(8-3*u,3+2*u,18-6*u)
        return p,film.PEARL+v(0,.4,0),52
    if j==10:
        u=film.sc(44.35,49.15,t)
        az=np.radians(48+18*u)
        p=film.A7+v(np.sin(az)*(18+10*u),rise_y(t),np.cos(az)*(18+10*u))
        inward=film._unit(film.A7+v(0,p[1]+5,0)-p)
        sun=film._unit(film.HV+v(0,.10,0))
        q=p+80*film._unit(inward*(1-film.sc(46.4,49.0,t))+sun*film.sc(46.4,49.0,t))
        return p,q,57
    u=film.sc(48.65,53.85,t)
    p=film._fin_cam(-26+42*u,-8+14*u,(4.45-.55*u)*film.FIN_R)
    drop=film._LOGO_DROP*film.sc(51.9,53.85,t)
    return p-v(0,drop,0),film.FIN_C-v(0,film.FIN_LIFT+drop,0),48


def state(self, t, aspect=16/9, ref=None):
    p, q, fov = pose(t, shot_at(t) if SHOT is None else SHOT)
    return CameraState(pos=p, target=q, fov=fov, aspect=aspect, aperture=0.015 if 8<t<42.5 else 0, focus=np.linalg.norm(q-p))


# Preserve object identity: words, logo, world and renderer share these rigs.
for rig in (film.CAMERA, film._LAYOUT):
    rig.state = types.MethodType(state, rig)
    rig.handheld = 0
    rig.cuts = lambda: list(CUTS)

GOLD = dict(look=dict(name='glitter', glints=0.00025, seams=0.25, size=0.95), color='#f2a640', color2='#ffdc96', bright=0.45)
IVORY = dict(look=dict(name='glitter', glints=0.00025, seams=0.25, size=0.95), color='#efb75d', color2='#ffe5af', bright=0.45)


def person(o, x, z=0, facing=0, shape='woman', show=(0,62), gesture=(), motion='stand', seed=1, ivory=False, **kw):
    return Body(shape, at=(o[0]+x, o[2]+z), facing=facing, garment='dress' if shape=='woman' else 'tunic',
                hair='bun' if shape=='woman' else 'short', points=95000, show=show, fade=0.65,
                gesture=gesture, motion=motion, seed=seed, wind=None, **(IVORY if ivory else GOLD), **kw)


def cast():
    if film._CAST:
        return film._CAST
    C = film._CAST
    C['hands0'] = []
    C['greeting'] = [person(film.P1, -0.52 if k==0 else 0.52, shape='man', facing=78 if k==0 else 282,
        show=(8.1,13), seed=21+k, ivory=bool(k), gesture=[
            (9.1+0.35*k,12.7,'bow',dict(amount=12, ease=1.15)),
            (10.2+0.35*k,12.7,'nod',dict(amount=3,period=3))]) for k in range(2)]
    C['gratitude'] = [person(film.P1b,0, facing=25, show=(11.8,16.2), seed=33,
        gesture=[(12.3,16,'hand_on_heart',dict(bow=6,ease=1.05)),(12.9,16,'bow',dict(amount=11,ease=1.1))])]
    # A low-handed apology, then a small step into a true same-gender embrace.
    o=film.P2
    a=dict(shape='woman',facing=90,garment='dress',hair='bun',height=1.64,
        at=[(0,(o[0]-0.48,o[2]-0.09)),(18.9,(o[0]-0.48,o[2]-0.09)),(19.65,(o[0]-0.19,o[2]-0.09))],
        motion=[(-1e9,'stand'),(18.85,'shuffle',dict(blend=0.3)),(19.7,'stand',dict(blend=0.4))],
        points=110000,show=(15.0,22.9),fade=0.75,seed=61,**GOLD,
        gesture=[(15.6,19.2,'open_hands',dict(bow=9,ease=1.15)),(16.1,19.2,'bow',dict(amount=8,ease=1.2))])
    b=dict(shape='woman',facing=270,garment='dress',hair='tied',height=1.60,
        at=[(0,(o[0]+0.48,o[2]+0.09)),(18.9,(o[0]+0.48,o[2]+0.09)),(19.65,(o[0]+0.19,o[2]+0.09))],
        motion=[(-1e9,'stand'),(18.85,'shuffle',dict(blend=0.3)),(19.7,'stand',dict(blend=0.4))],
        points=110000,show=(15.0,22.9),fade=0.75,seed=62,**IVORY,
        gesture=[(16.1,19.4,'listen',dict(amount=0.45,ease=1.2)),(16.8,19.5,'nod',dict(amount=3,period=3.2))])
    C['embrace']=list(pairs.embrace(19.35,at=(o[0],o[2]),facing=90,a=a,b=b,until=22.8,gap=0.38,side=0.09,ease=1.15))
    o=film.P3
    C['concession']=[Body('man',at=[(0,(o[0]-1.0,o[2]+2)),(22.6,(o[0]-1.0,o[2]+2)),(23.5,(o[0]-1.45,o[2]+2.05))],
        facing=[(22.6,5),(23.5,15)],garment='tunic',hair='short',points=110000,show=(21.6,26.3),fade=0.7,seed=51,**GOLD,
        motion=[(-1e9,'stand'),(22.55,'shuffle',dict(blend=0.35)),(23.6,'stand',dict(blend=0.45))],
        gesture=[(22.8,26.1,'after_you',dict(side='L',bow=7,ease=1.3,to=o+v(-1.0,0.90,2.35)))])]
    # Standing listeners read clearly above their reflections; small, slow nods avoid bobbing.
    refs2=pairs.Refs()
    ra=dict(shape='man',at=(film.P3b[0]-0.43,film.P3b[2]),facing=72,garment='tunic',hair='short',
        points=95000,show=(25.1,29.5),fade=0.7,seed=71,**IVORY,
        gesture=[(25.6,29.4,'listen',dict(amount=0.55,ease=1.1)),(26.3,29.4,'nod',dict(amount=3,period=3.1))])
    rb=dict(shape='man',at=(film.P3b[0]+0.43,film.P3b[2]),facing=288,garment='tunic',hair='short',
        points=95000,show=(25.1,29.5),fade=0.7,seed=72,**GOLD,
        gesture=[(25.6,29.4,'explain',dict(side='R',period=3.2,ease=1.3))])
    C['respect']=refs2.build(('a','b'),a=ra,b=rb)
    C['encouragement']=[person(film.P4,0.25,facing=35,show=(28.3,35.9),seed=81,ivory=True,
        motion=[(-1e9,'kneel',dict(dur=0.01,sit=0.75,hands='pray'))],
        gesture=[(29.4,35.8,'bow',dict(amount=7,ease=1.5))]),
        person(film.P4,-0.40,-0.16,facing=45,show=(28.3,35.9),seed=82,
        gesture=[(29.2,35.8,'hand_on_heart',dict(bow=6,ease=1.5))])]
    ka=dict(shape='man',points=110000,show=(34.8,39.5),fade=0.7,seed=91,**GOLD)
    kb=dict(shape='man',points=110000,show=(34.8,39.5),fade=0.7,seed=92,**IVORY)
    C['consideration']=list(pairs.helped_up(36.2,at=(film.P5[0],film.P5[2]),facing=67,
        a=ka,b=kb,rise=1.9,reach=1.1,apart=0.70))
    # The praised person receives the compliment; the second person applauds at chest height.
    C['compliment']=[person(film.P5b,0.25,facing=335,show=(38.3,42.8),seed=101,ivory=True,
        gesture=[(39.0,42.7,'hand_on_heart',dict(bow=4,ease=1.2)),(39.8,42.7,'bow',dict(amount=6,ease=1.2))]),
        person(film.P5b,-0.65,-0.10,facing=65,show=(38.3,42.8),seed=102,
        gesture=[(38.9,42.7,'clap',dict(period=0.78,height=0,width=0.10,ease=1.0))])]
    # Contact references must omit secondary hand motion as well as gestures.
    # The baseline raw reference calls living hands, which re-enters the other
    # person's gestures at earlier times. Keep ordinary performed hands alive.
    for group in ('embrace','consideration'):
        for body in C[group]:
            original=body.actor.frame
            def frame(self,t,lock=True,gest=True,life=True,original=original):
                return original(t,lock=lock,gest=gest,life=life if gest else False)
            body.actor.frame=types.MethodType(frame,body.actor)
            body.actor._cache.clear()
    return C


class Steady:
    """Keep the golden grain, remove shader twinkle and hard glints from scenery."""
    def __init__(self,inner):
        self.inner=inner
        self.wants_camera=getattr(inner,'wants_camera',False)
        if hasattr(inner,'gain'): self.gain=inner.gain
    def sample(self,t,cam=None):
        res=self.inner.sample(t,cam) if self.wants_camera else self.inner.sample(t)
        if res is None: return None
        out=[]
        for b in res if isinstance(res,(tuple,list)) else [res]:
            if b is None: continue
            b=dict(b,twinkle=0)
            if b.get('kind')=='spark': b.update(emit=np.minimum(b.get('emit',1),2.4))
            out.append(b)
        return out


class Stage:
    def __init__(self,scene):self.scene=scene
    def add(self,name,ps,**kw):
        # Replace the repeated foreground cloud curtain with authored depth.
        if name.startswith('word ') or name.startswith('clouds_') or name in ('river','crowd5','hearts5','tree','ahead','streaks') or name.startswith('hearts_'):return
        if name in ('nave','door','petals3','palm_light0','pour0','trail0'):return
        if name=='rain': ps=film._Fade(ps,lambda t:.48)
        if name=='pillar7':ps=film._Fade(ps,lambda t:.65)
        if name=='door':ps=film._Fade(ps,lambda t:.55)
        if name=='petals3':ps=film._Fade(ps,lambda t:.45)
        self.scene.add(name,Steady(ps),**kw)


_original_setup=film._setup
film._cast=cast

def setup(scene):
    _original_setup(Stage(scene))
    from sol_edits.v3.effects import Arcade,Lotus,HeartPass,PrayerLights,LivingCanopy,Constellation,envelope
    from p3d import master_sky as MS
    C=cast()
    scene.add('cathedral of light',film.Clear(Arcade(film.P4,28.3,30.0,count=4,span=5.7,height=8.5)),reflect=True)
    scene.add('open way',film.Clear(Arcade(film.P3,21.7,26.5,count=4,span=3.6,height=5.8)),reflect=True)
    scene.add('love canopy',film.Clear(LivingCanopy(film.P5b+v(-3,0,-3),38.1,43.4)),reflect=True)
    scene.add('listening tree',film.Clear(LivingCanopy(film.P3b+v(-3,0,-4),25.2,29.7)),reflect=True)
    for name,o,a,b,r in [('welcome',film.P1,8.3,13,1.4),('forgiveness',film.P2,19.4,23,1.4),
                          ('prayer',film.P4,30.0,35.8,1.9),('joy',film.P5b,39.2,43,1.6)]:
        scene.add('lotus '+name,Lotus(o,a,b,radius=r),reflect=True)
    src=lambda t:C['embrace'][0].where(t,'heart')
    dst=lambda t:C['embrace'][1].where(t,'heart')
    scene.add('the light is accepted',film.Clear(HeartPass(src,dst,17.1,18.8)),reflect=True)
    scene.add('prayers rise',film.Clear(PrayerLights(film.P4,29.9,36.2)),reflect=True)
    scene.add('ascent currents',Constellation(film.A7,rise_y,film.NINE_GLOW),reflect=False)
    # Each setting has its own banks, scale and light; foreground geometry gives parallax.
    stages=[(film.H0+v(0,-12,-35),-1,8.7),(film.P1,7.9,15.8),(film.P2,14.8,23.1),
            (film.P3,21.5,29.4),(film.P4,28.1,36.0),(film.P5,34.8,42.8),(film.A7,41.8,50.0)]
    for k,(o,a,b) in enumerate(stages):
        banks=[]
        for side in [-1,1]:
            for j in range(3):
                banks.append(dict(center=tuple(o+v(side*(13+14*j),1+2*j,-18-24*j)),width=14+11*j,
                                  height=4.5+3*j,n=180,bright=.70))
        ps=MS.Billows(banks,gain=lambda t,a=a,b=b:envelope(t,a,b,1),seed=341+k,
                      top='#ffe9bd',warm='#efc284',rose='#dba7a0',lilac='#8b9fbd',core='#fff1d0',
                      alpha=.006,body=.15,shade=.85,drift=(.22,0,0),sun_az=228)
        scene.add('cloud garden '+str(k),film.Clear(Steady(ps)),depth_of_field=True)
    # Golden silk paths lead into each encounter and carry it toward the next.
    from p3d.api import ribbon,lin
    class GardenPaths:
        def sample(self,t):
            out=[]
            for o,a,b in stages[1:-1]:
                g=envelope(t,a,b)
                if g<.001:continue
                for side in [-1,1]:
                    z=np.linspace(-34,10,180);x=side*(2.7+.035*(z+8)**2)
                    p=o+np.stack([x,np.full(len(z),.04),z],1)
                    out.append(ribbon(p,width=.012,color=lin('#ffdca0'),alpha=.20*g,emit=1.2,twinkle=0))
            return out
    scene.add('the way of light',film.Clear(GardenPaths()),reflect=True)

# Gentle colour transitions instead of the two zero-duration look switches in v6.
film.LOOK_KEYS[:]=[(a,b,1.4 if len(k)<3 or k[2]==0 else k[2]) for k in film.LOOK_KEYS for a,b in [k[:2]]]
film.P3D['world']['look']=[(k[0],k[1],1.4) if len(k)>2 and k[2]==0 else k
                            for k in film.P3D['world']['look']]
film.TITLES['signature']['windows']=[
    (film.OPEN_FULL+.7,50.2,film.SIG_CORNER,'day'),
    (49.6,film.BLOOM_T+.65,film.SIG_CORNER,'night'),
    (film.BLOOM_T+.05,film.SIG_END,film.SIG_CORNER,'day')]

film.TITLES['end_card'].update(t_out=63.0,backdrop=None,veil=0.65)
film.FINAL_HIT=55.65
film.P3D.update(setup=setup,motion_blur=0.75)
# Deep blue and champagne replace the uniform violet cloud wash.
for name,colors in {'opening':('#223b68','#8c9cae','#efc894'),
                    'shore':('#335c80','#9bb9c4','#f3d3a0'),
                    'rain':('#293f70','#718da9','#cbbeb1'),
                    'sunrise':('#54778d','#d7c8ae','#f5ce8a'),
                    'river':('#426a84','#b5c9c7','#f0d4a5'),
                    'cathedral':('#254d72','#6e99ae','#e9cca5'),
                    'rivers':('#3a6682','#a9c8ca','#f6d8ab'),
                    'breath':('#234c70','#7ca4ba','#f1d8b5')}.items():
    look=film.P3D['world']['looks'][name]
    look.update(sky_top=colors[0],sky_mid=colors[1],sky_hor=colors[2],stars=.06,milky=.02,bokeh=.10,dust=.12,water='#355d72',haze=.08,mist=.04,mirror=.5,rays=.08)
film.P3D['world']['react']=dict(beat=.12,level=.12)
# Words become intimate phrases rather than repeated category cards.
specs=[]
for old,e in zip(film._SPECS,film.PW.EXPRESSIONS):
    d=dict(old);d.pop('expr',None)
    d.update(label='',lines=e['lines'],name=e['label'],pill=False,n_label=0,
             ride=(.29,.70,7),width=film._width(10,7,.36),arrive='reveal',leave='fade',
             color=e['color'],halo=.16,sparkle=.05,bright=.7)
    specs.append(d)
film.WORDS=film.PW.Words(specs,camera=film._LAYOUT,reflect=False,drive=film._clean_leave)
# The baseline setup builds all Body layers before returning. Retain the soft body grain with no twinkle.
for name,value in vars(film).items():
    if not name.startswith('__'): globals().setdefault(name,value)
AUDIO_FILE='work/sol3/sol-v3-score.wav'
