"""Restore the exact Film 10 shot design, with current cast and information."""
import numpy as np
from songs.s03_original import *  # noqa: F401,F403
from tools.nine_colours import original as O
from tools.nine_colours.original import *  # noqa: F401,F403
from tools.nine_colours.cast import build
from tools.radiance.celebration import Celebration

TOTAL = SONG_END = MUSIC_END = 62.0
NFRAMES = int(TOTAL*FPS)
O._base.TOTAL=TOTAL
O._base.NFRAMES=NFRAMES
O._bodies = lambda: build(O)

# Opening remains whole through 7 seconds. Move just the first two readings
# into the free space before the original embrace, retaining their order.
O._SPECS[0].update(t_in=5.1,t_read0=5.4,t_read1=7.9,t_out=8.05)
O._SPECS[1].update(t_in=8.05,t_read0=8.4,t_read1=10.95,t_out=11.2)
for spec in O._SPECS:
    spec.update(pill=spec.get('name')!='Date',sharp=1,bright=.9,halo=.3,sparkle=.025)
O.WORDS=O.PW.Words(O._SPECS,camera=O._LAYOUT,reflect=False,drive=O._clean_leave)
# Head legs use closures that resolve the current WORDS, so the pen still writes
# each phrase. Only the opening and blue pen timing moves for the longer card.
for k,a,b in ((O.GREET,5.1,5.4),(O.CONC,8.05,8.4)):
    legs=O.HEADS[k].legs
    old=legs[0]
    legs[0]=(a,b,old[2],min(old[3],.5),old[4])
O.TITLES['opening'].update(t_end=5.1,y=.30)
O.TITLES['signature']=dict(windows=[(5.1,52.8,'bl','night')])


def badge_box(t):
    if t<5.1:
        return (.12,.88,.4,.97)
    if t<52.8:
        return (.015,.36,.015,.15)
    return None


O._badge_box=badge_box
O.CAMERA.free=True
O.CAMERA.shutter=.6


class PassingReflection:
    """A reflection arrives after reading, as the camera leaves the words."""
    wants_camera=True

    def __init__(self,word):self.word=word

    def sample(self,t,cam):
        w=self.word
        if not w.t_read1<t<w.t_out or w.name=='Date':return None
        got=w.sample(t,cam)
        amount=.45*float(O._ss(w.t_read1,w.t_read1+.08,t))
        out=[]
        for b in got if isinstance(got,list) else [got]:
            if b is not None:
                d=dict(b)
                d['alpha']=np.asarray(d.get('alpha',1))*amount
                out.append(d)
        return out


def setup(scene):
    scene.add('seed',O.ScreenClear(O.Seed()))
    scene.add('hoops',O.ScreenClear(O.PW.KeepClear(O.Hoops(),O.WORDS)))
    scene.add('lanterns',O.ScreenClear(O.PW.KeepClear(O.Lanterns(),O.WORDS)))
    for name,body in O._bodies().items():
        body.add(scene,name,mask=False)
    scene.add('flares',O.ScreenClear(O.Flares()))
    scene.add('comets',O.ScreenClear(O.PW.KeepClear(O.Comets(),O.WORDS)))
    O.WORDS.add_to(scene)
    for word in O.WORDS:
        scene.add('passing reflection '+word.name,PassingReflection(word),reflect=True)
    O.WORDS.check(O.CAMERA)


WORLD=dict(O.WORLD)
# Retain the original night-to-morning progression; remove the source's full
# screen flash while keeping the same accent timing and coloured light.
P3D=dict(O.P3D,setup=setup,motion_blur=.6,motion_samples=1,
         bursts=[dict(b,strength=min(b['strength'],.6)) for b in O.P3D['bursts']])
TITLES=dict(opening=dict(t_end=7.1,dissolve=.1,y=.30,palette='night'),
            signature=dict(windows=[(7.1,54.8,'bl','night')],fade=.25,protect=dict(keep=0)),
            end_card=dict(t_in=54.5,fade=.5,scale=1,backdrop=True,veil=.65,ambient_motes=True))
# The original particle date remains in its musical breath; do not draw a
# second TITLES date over it. Current TITLES suppresses the legacy end text.
CREDIT=dict(O.CREDIT,t_in=1e9,t_full=1e9,t_move=1e9,t_rest=1e9)


def smooth(a,b,t):
    return O._ss(a,b,t)
