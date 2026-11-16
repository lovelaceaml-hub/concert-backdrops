"""Smooth camera and ribbon anchors from the same captured dancer performance."""
import numpy as np
from scipy.interpolate import CubicSpline

def install(film,cast):
    dancer=cast['dancer']
    ts=np.arange(19.3,27.5,1/60)
    hands=np.array([dancer.where(float(t),'palm.R') for t in ts])
    pelvis=np.array([dancer.where(float(t),'pelvis') for t in ts])
    hand_curve=CubicSpline(ts,hands)
    pelvis_curve=CubicSpline(ts,pelvis)
    film._dancer_hand=lambda t:hand_curve(np.clip(t,film.SEC[3],film.LOOP_T1+.2))
    def ground(t):
        p=np.mean([pelvis_curve(np.clip(t+dt,film.SEC[3]-.2,27)) for dt in [-.4,-.2,0,.2,.4]],axis=0)
        p[1]=0
        return p
    film._dancer_ground=ground
