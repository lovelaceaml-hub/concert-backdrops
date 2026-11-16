"""Faithful render-1 restoration. Shared and protected source files are unchanged."""
import importlib.util
import pathlib
import sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dot_nine_r1_original', HERE / 'original.py')
O = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = O
spec.loader.exec_module(O)

# Keep the r1 geography, paths, section timing and comet choreography. Replace
# only its historical cast through a local factory, using the modern engine.
import p3d.body as body_module
BaseBody = body_module.Body
original_bodies = O._bodies

def modern_body(shape, **kw):
    seed = float(kw.get('seed', 0))
    kw.update(look='glitter', color='#ffcf7a', color2='#fff1d6', bright=1.12)
    kw['points'] = max(60000, int(kw.get('points', 60000)))
    kw['detail'] = dict(head=3, hand=4)
    kw['effects'] = [x for x in kw.get('effects', []) if x.get('kind') == 'shed']
    if seed == 3:
        shape = 'woman'
        kw.update(garment='dress', hair='bob', build=0.94)
        kw['motion'] = 'stand'
        kw['gesture'] = [(13.1, 17.0, 'open_hands', dict(bow=0.15, ease=1.3, antic=0, over=0))]
    elif seed == 4:
        kw.update(hair='tied', build=1.04)
    elif seed == 6:
        kw.update(hair='tied', motion=[(19.35, 'twirl', dict(rate=0.75))])
    elif seed == 11:
        kw.update(motion='stand', hair='covered')
        kw['gesture'] = [(39.5, 49.0, 'pray', dict(ease=1.5, antic=0, over=0))]
    gestures=[]
    for entry in kw.get('gesture', []):
        opts=dict(entry[3]) if len(entry)>3 else {}
        opts.update(ease=1.3, antic=0, over=0)
        gestures.append(tuple(entry[:3])+(opts,))
    kw['gesture']=gestures
    return BaseBody(shape, **kw)

def bodies():
    if O._BODIES:
        return O._BODIES
    body_module.Body = modern_body
    try:
        result=original_bodies()
    finally:
        body_module.Body=BaseBody
    from p3d import pairs
    common=dict(shape='woman',garment='dress',look='glitter',color='#ffcf7a',
        color2='#fff1d6',bright=0.9,points=65000,detail=dict(head=3,hand=4),
        show=(O.SEC[2]-0.3,20.6),fade=0.4)
    result['sorry'],result['kind']=pairs.embrace(16.8,at=(O.C3[0],O.C3[2]),
        facing=0,gap=0.40,a=dict(common,hair='bob',seed=3),b=dict(common,hair='tied',seed=4),
        until=20.6,ease=1.4,approach=0,hold='mixed')
    # Same-gender gentle greeting, seen during the original low chase.
    for i in range(2):
        result['greeting_'+str(i)]=BaseBody('man', at=(-2.0+i*1.1,155.0),
            facing=90 if i==0 else 270, garment='coat', hair='short',
            look='glitter', color='#ffcf7a', color2='#fff1d6', points=65000,
            show=(4.6,8.0), fade=0.6, seed=21+i,
            gesture=[(5.4,7.7,'bow',dict(amount=0.13,ease=1.2,antic=0,over=0))])
    return result
O._bodies=bodies
O.AUDIO_FILE=str(HERE.parents[1]/'work/dot_nine_r1/original-score.wav')

# The first reading moves within the continuing chase to clear the full title.
for cfg in O._SPECS:
    cfg.update(pill=True, sharp=1.0)
    if cfg['expr']=='Greeting':
        cfg.update(t_in=5.0,t_read0=5.6,t_read1=8.1,t_out=8.5,leave='fade')
    elif cfg['expr']=='Concession':
        cfg.update(t_in=8.3,t_read0=8.7,t_read1=11.2,t_out=12.3)
O.HEADS[O.GREET].legs[0]=(5.0,5.6,O._pen('Greeting'),0.25,0.25)
O.HEADS[O.CONC].legs[0]=(8.3,8.7,O._pen('Concession'),0.2,0.2)
O.WORDS=O.PW.Words(O._SPECS,camera=O._LAYOUT)
O.CAMERA=O._rig(O._focus)
O.P3D['camera']=O.CAMERA
O.P3D['world']=O.WORDS.world(O.WORLD)
# Keep cue locations but remove the original near-white transition flashes.
for burst in O.P3D['bursts']:
    burst['strength']=min(burst['strength'],0.85)
O.P3D['motion_blur']=0.75
O.P3D['world']['look'][-1]=(O.SEC[7],'morning',0.9)

globals().update({k:v for k,v in vars(O).items() if not k.startswith('__')})
TOTAL=62.0
FPS=60
NFRAMES=3720
TITLES=dict(
    opening=dict(t_end=7.6,dissolve=0.6,y=0.29,palette='night'),
    signature=dict(windows=[(7.0,51.5,'bl','night'),(51.5,55.0,'bl','day')],fade=0.4),
    end_card=dict(t_in=54.3,fade=0.7,backdrop='pastel'))
