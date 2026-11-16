"""Whole, warmly lit people for the original Nine Colours staging."""
import numpy as np
from p3d.body import Body, Hands
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
    for i in range(6):
        side = -1 if i%2==0 else 1
        z = film.TUNNEL_Z0-film.HOOP_GAP*(.25+.55*i)
        person('gate'+str(i), 'woman' if i%3!=1 else 'man',
               at=(side*3.3,z), facing=90 if side<0 else 270, points=45000,
               show=(6.9+.15*i,11.9), seed=20+i,
               gesture=[(7.2+.25*i,11.8,'offer',
                         dict(side='L' if side<0 else 'R',ease=1,over=0,antic=0))])

    # The pair starts together: no hand-authored walk can overshoot the embrace.
    a=dict(common,shape='woman',garment='dress',hair='tied',points=135000,
           show=(13.0,20.4),seed=3,
           gesture=[(13.5,16.5,'bow',dict(amount=10,ease=.85,over=0,antic=0))])
    b=dict(common,shape='woman',garment='dress',hair='long',points=135000,
           show=(13.0,20.4),seed=4,color='#ffcf86',color2='#fff5df')
    B['sorry'],B['kind']=pairs.embrace(16.6,at=(film.C3[0],film.C3[2]),
          facing=90,a=a,b=b,approach=0,gap=.38,side=.10,ease=1.25,until=20.4)

    person('dancer', at=(film.D4[0],film.D4[2]), facing=30,
           motion=[(17.5,'dance')], points=140000,show=(19.7,27.1),seed=6,
           wind=(0,0,0),hair='tied')
    for i,(az,r) in enumerate(((205,7.5),(235,8.5),(262,7.8))):
        p=film.D4+film.at3(az,r)
        person('fan'+str(i), 'man' if i!=1 else 'woman',at=(p[0],p[2]),
               facing=(az+180)%360,points=45000,show=(19.85,25.5),seed=30+i,
               gesture=[(20.6+.2*i,26,'clap',dict(period=.8+.05*i,height=.5,ease=.8))])

    hands=Hands(meet=tuple(film.H5),t_touch=film.HANDS_T,axis=90,
                color='#f6bc62',color2='#ffe1a3',shapes=('woman','woman'),
                approach=2.6,apart=.55,tilt=18,points=105000,bright=1.3,
                shed=False,flare=.45)
    B['hand_gold'],B['hand_rose']=hands['left'],hands['right']
    for hand in (hands['left'],hands['right']):
        hand.show=(26.79,30.35)
    film._REFS['hands_flare']=hands['flare']
    film._REFS['bower']=person('bower',at=(film.E5[0],film.E5[2]),facing=6,
        show=(29.9,33.56),seed=7,hair='tied',
        gesture=[(30.4,33.5,'hand_on_heart',dict(side='R',bow=9,ease=.9,over=0,antic=0))])
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
    others=[k for k in range(9) if k!=film.ENC]
    for j,k in enumerate(others):
        az=118+124*j/7
        p=film.G7+film.at3(az,10.5+.8*(j%2))
        person('crowd'+str(j),'woman' if j%2==0 else 'man',at=(p[0],p[2]),
               facing=(az+180)%360,points=40000,show=(42.26,46.65),seed=40+j,
               gesture=[(42.8+.08*j,46.7,'raise_hand',dict(side='R' if j%2 else 'L',ease=1.2,over=0,antic=0))])
    return B
