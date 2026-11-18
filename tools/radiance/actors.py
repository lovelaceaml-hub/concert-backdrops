"""Standing performances from the earlier independent Astra treatment."""

def standing_encouragement():
    """A quiet same-gender prayer, with both feet planted and one-way contact.

    The source kneel exposed a shin beyond its skirt in this camera angle.
    These whole standing figures use the existing Body API without editing it.
    """
    from p3d.body import Body
    common=dict(motion='stand',garment='dress',hair='tied',points=70000,
                show=(31.8,36.2),fade=.5,look='glitter',bright=1.45)
    praying=Body('woman',at=(.38,0),facing=-16,seed=47,
        color='#ffc664',color2='#fff0c8',
        gesture=[(32.15,35.85,'pray',dict(ease=.8,over=0,antic=0)),
                 (32.5,35.8,'bow',dict(amount=5,ease=.9,over=0,antic=0))],**common)
    beside=Body('woman',at=(-.25,-.04),facing=20,seed=48,
        color='#f2a640',color2='#ffdc96',
        gesture=[(32.4,35.7,'hand_on_shoulder',
                  dict(side='L',to=lambda t: praying.where(t,'shoulder.R',raw=True),
                       ease=.85,over=0,antic=0)),
                 (32.8,35.6,'bow',dict(amount=5,ease=.9,over=0,antic=0))],**common)
    return [beside,praying]


def standing_consideration():
    """An offered hand and a grateful acknowledgement, with planted feet."""
    from p3d.body import Body
    people=[]
    for j,(x,facing) in enumerate(((-.38,65),(.38,-65))):
        gestures=[(36.35,39.65,'handshake',dict(side='R',to=(0,1.02,.10),
                    grip=.3,ease=.9,over=0,antic=0)),
                  (36.8,39.4,'nod',dict(period=2.8,amount=4,ease=.9))]
        if j:
            gestures.append((37.0,39.4,'hand_on_heart',dict(side='L',bow=3,ease=.9,over=0,antic=0)))
        people.append(Body('man',at=(x,0),facing=facing,seed=51+j,
            motion='stand',garment='tunic',points=70000,show=(35.8,40.2),fade=.5,
            look='glitter',color='#f2a640' if j==0 else '#ffc664',
            color2='#ffdc96' if j==0 else '#fff0c8',bright=1.45,gesture=gestures))
    return people
