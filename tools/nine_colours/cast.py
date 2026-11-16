"""Whole, warmly lit people for the original Nine Colours staging."""
import numpy as np
from p3d.body import Body
from p3d import pairs


def build(film):
    B = film._BODIES
    if B:
        return B
    common = dict(look='glitter', color='#f6bc62', color2='#fff0cf',
                  bright=1.3, wind=(.08, 0, -.06), gust=.08,
                  detail=dict(head=2, hand=2), fade=.45)

    def person(name, shape='woman', **kw):
        cfg = dict(common, points=110000, garment='dress' if shape=='woman' else 'tunic')
        cfg.update(kw)
        B[name] = Body(shape, **cfg)
        return B[name]

    # Two men acknowledge each other alongside the original low lake chase.
    z = film.zcam(6.8)-11
    for j in range(2):
        person('greeting'+str(j), 'man', at=(2.4+.65*j,z), facing=90 if j==0 else 270,
               points=70000, show=(5.05,8.2), seed=12+j,
               gesture=[(5.4,8.1,'bow',dict(amount=9,ease=.9,over=0,antic=0))])
    # The pair starts together: no hand-authored walk can overshoot the embrace.
    a=dict(common,shape='woman',garment='dress',hair='tied',points=135000,
           show=(13.0,20.4),seed=3,
           gesture=[(13.5,16.5,'bow',dict(amount=10,ease=.85,over=0,antic=0))])
    b=dict(common,shape='woman',garment='dress',hair='long',points=135000,
           show=(13.0,20.4),seed=4,color='#ffcf86',color2='#fff5df')
    B['sorry'],B['kind']=pairs.embrace(16.6,at=(film.C3[0],film.C3[2]),
          facing=90,a=a,b=b,approach=0,gap=.38,side=.10,ease=1.25,until=20.4)

    person('dancer', at=(film.D4[0],film.D4[2]), facing=30,
           motion=[(19.35,'dance_a')], points=140000,show=(19.7,27.1),seed=6,
           wind=(0,0,0),hair='tied')
    person('child','child',at=(film.E5[0]-.35,film.E5[2]+.1),facing=120,
           points=90000,show=(27.39,33.66),seed=7,
           gesture=[(27.39,30.3,'offer',dict(side='R',ease=.9,over=0,antic=0)),
                    (30.4,34,'blow',dict(side='R',ease=.8,over=0,antic=0))])
    person('helper','man',at=(film.E5[0]+.55,film.E5[2]-.15),facing=300,
           points=120000,show=(27.39,33.66),seed=8,
           gesture=[(27.79,30.9,'touch',dict(side='R',to=film._touch5,palm='down',ease=1,over=0,antic=0))])
    person('speaker',at=(film.F6[0]-.45,film.F6[2]),facing=90,show=(33.16,40.41),seed=9,
           gesture=[(34.2,40,'explain',dict(side='L',ease=1,over=0,antic=0))])
    person('listener','man',at=(film.F6[0]+.45,film.F6[2]),facing=270,
           show=(33.16,40.41),seed=10,
           gesture=[(34.6,40,'lean_in',dict(to=lambda t: film.F6+np.array([-.45,1.55,0]),amount=.18,ease=1)),
                    (35.2,40,'nod',dict(period=2.6,amount=4,ease=.9))])
    # A whole standing prayer avoids the older kneel's skirt and shin intersection.
    person('praying',at=(film.G7[0],film.G7[2]),facing=180,
           show=(40.11,47.0),seed=11,hair='tied',points=120000,
           gesture=[(40.1,47,'pray',dict(ease=1,over=0,antic=0)),
                    (40.4,47,'bow',dict(amount=5,ease=1,over=0,antic=0))])
    return B
