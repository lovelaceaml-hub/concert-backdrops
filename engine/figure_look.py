"""The silk look for people of light (2026-11-15, branch engine-figure-look).

look="silk" on a rigged FIGURES entry (kind="rig") or on GATHERING, or FIGURE_LOOK = "silk" for the whole song,
draws a person as a body of light instead of sparks:

  body     a smooth luminous silhouette computed from the posed skeleton (engine/rig.py): rounded cones strung
           along the bones, added up like light through frosted glass. A warm core at the heart and the head, soft
           edges, a robe that breaks into mist toward the hem (no hard feet, no outline), and a thin rim of light
           on the side that faces the scene's light (light_from).
  cloth    the veil, the sleeves and the lower robe are sheets of fine threads of light. They are spring chains
           pulled by the body and blown by a layered wind, so they billow, trail and settle with real lag.
  strands  a few dozen long fine streamlines that run down the body and trail behind a moving figure; a few
           bright motes rise off the shoulders and hands.
  water    each figure is mirrored and rippled in the lake at its feet.
  day      on a bright sky the body gets a faint cool tint of the same brightness (never a dark patch).

Everything is a pure function of time. The cloth is simulated afresh for every frame over the last 1.5 seconds
(from a hanging start), so any frame can be drawn on its own and the cloud workers that render a video in parts
agree with each other. A song that does not ask for the look renders exactly as before.
How a song uses it: engine/UPGRADE-HOWTO.md section U.
"""
import math

import numpy as np
import moderngl

import song as S
import rig as RG
import shaders as G

TAU = 2.0 * math.pi
MAXSEG = 48          # rounded cones per body
ROWS = 320           # bodies per frame (a crowd, its mirror images and the single figures)
FIG_UNIT = 14        # texture unit of the tint in the composite (free: UPGRADE-HOWTO section S)

# ---------------------------------------------------------------- settings


def look_of(m):
    return (m or {}).get("look", getattr(S, "FIGURE_LOOK", None))


def is_silk(m):
    return look_of(m) == "silk"


def wanted():
    """True when the song draws anyone in the silk look (decided once, when the song loads)."""
    figs = [f for f in (getattr(S, "FIGURES", None) or []) if f.get("kind", "pose") == "rig"]
    g = getattr(S, "GATHERING", None)
    return any(is_silk(f) for f in figs) or (g is not None and is_silk(g))


def opt(m, key, default):
    """A look setting: the figure's own key, else the song's FIGURE_SILK dict, else the default."""
    if m is not None and key in m:
        return m[key]
    return (getattr(S, "FIGURE_SILK", None) or {}).get(key, default)


def _lin(c):
    return S.lin(c) if isinstance(c, str) else np.asarray(c, dtype=np.float64)


def _f(v, t):
    return float(v(t)) if callable(v) else float(v)


def ss(a, b, x):
    x = np.asarray(x, dtype=np.float64)
    if b == a:
        return (x >= a) * 1.0
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def _ssf(a, b, x):
    return float(ss(a, b, x))


def gust(t, x, base):
    """The shared wind (the same gusts as engine/nature.py, rolling left to right)."""
    return base * (0.62 + 0.38 * math.sin(0.42 * t - 3.1 * x) + 0.22 * math.sin(1.17 * t - 7.3 * x + 1.3)
                   + 0.10 * math.sin(2.9 * t - 13.0 * x))


# ---------------------------------------------------------------- shaders
BODY_VS = """
#version 330
in vec2 aQ;
in vec4 iRect; in vec4 iOrg; in vec4 iInfo; in vec4 iColA; in vec4 iColB; in vec4 iPts; in vec4 iLight;
in vec4 iFx; in vec4 iPar;
out vec2 vP;
flat out vec4 fInfo; flat out vec4 fColA; flat out vec4 fColB; flat out vec4 fPts; flat out vec4 fLight;
flat out vec4 fFx; flat out vec4 fPar;
void main(){
  vec2 p = mix(iRect.xy, iRect.zw, aQ);
  vP = p; fInfo = iInfo; fColA = iColA; fColB = iColB; fPts = iPts; fLight = iLight; fFx = iFx; fPar = iPar;
  gl_Position = vec4((iOrg.xy + p*iOrg.zw)*2.0-1.0, 0.0, 1.0);
}
"""

# One body: rounded cones (texels of uSeg) added up as a soft volume. Coordinates are the figure's own: feet on
# y = 0, the head top near y = 1, x to the right of the screen.
BODY_FS = "#version 330\n" + G.NOISE + """
in vec2 vP;
flat in vec4 fInfo; flat in vec4 fColA; flat in vec4 fColB; flat in vec4 fPts; flat in vec4 fLight;
flat in vec4 fFx; flat in vec4 fPar;
uniform sampler2D uSeg;
uniform float uT, uSoft, uDens, uGain, uDay;
uniform vec3 uMist, uLightCol, uFlameCol;
out vec4 o;
void main(){
  int row = int(fInfo.x+0.5), n = int(fInfo.y+0.5);
  float px = fInfo.z, seed = fInfo.w, detail = fPar.x, mistK = fPar.z;
  float soft = mix(0.75, uSoft, detail), dens = mix(2.6, uDens, detail);   // small bodies are firmer
  vec2 p = vP;
  // the hem is seen through a slow swirl, so the lower robe breaks into wisps of mist
  float low = (1.0-smoothstep(0.02, 0.25, p.y))*mistK;
  if(low>0.001){
    vec2 w = vec2(vnoise(vec2(p.x*6.0+seed*17.0, p.y*7.0-uT*0.13)),
                  vnoise(vec2(p.x*6.0-uT*0.09+3.1, p.y*7.0+seed*9.0)))-0.5;
    p += w*0.075*low*low;
  }
  float T = 0.0, cur = 0.0, part = -1.0, sd = 1e3, robeK = 0.0, robeU = 0.0, sm = 0.016, wsd = 0.0;
  vec2 g = vec2(0.0, 1.0);
  for(int i=0;i<n;i++){
    vec4 s0 = texelFetch(uSeg, ivec2(3*i, row), 0);
    vec4 s1 = texelFetch(uSeg, ivec2(3*i+1, row), 0);
    vec4 s2 = texelFetch(uSeg, ivec2(3*i+2, row), 0);
    vec2 pa = p-s0.xy, ba = s0.zw-s0.xy;
    float h = clamp(dot(pa,ba)/max(dot(ba,ba),1e-8), 0.0, 1.0);
    vec2 q = pa-ba*h;
    float dist = length(q), r = mix(s1.x, s1.y, h), w = mix(s1.z, s1.w, h);
    float x = dist/max(r,1e-5);
    float kern = x<1.0 ? pow(1.0-x*x, soft) : 0.0;
    float e = w*kern;
    if(s2.x!=part){ T += cur; cur = 0.0; part = s2.x; }     // parts add up, the cones of one part only join
    cur = max(cur, e);
    if(s2.y>0.5 && s2.y<1.5 && kern>robeK){
      robeK = kern; robeU = (ba.x*pa.y-ba.y*pa.x)/(max(length(ba),1e-5)*max(r,1e-5));
    }
    float di = dist-r;
    float hh = clamp(0.5+0.5*(sd-di)/sm, 0.0, 1.0);
    sd = mix(sd, di, hh)-sm*hh*(1.0-hh);
    g = mix(g, q/max(dist,1e-5), hh);
    wsd = mix(wsd, w, hh);
  }
  T += cur;
  if(T<=0.0 && sd>0.004){ o = vec4(0.0); return; }
  // wisps at the hem, long soft pleats in the robe, a slow current of light inside
  float wisp = fbm3(vec2(p.x*5.0+seed*31.0, p.y*4.0-uT*0.11));
  T *= mix(1.0, 0.10+1.9*wisp*wisp, low);
  if(detail>0.01 && robeK>0.0){
    float a = asin(clamp(robeU, -1.0, 1.0));
    float pl = 0.5+0.5*cos(a*9.0 + 1.5*sin(p.y*7.0+uT*0.55+seed*40.0) + seed*20.0);
    T *= 1.0+0.55*detail*(pl-0.45)*smoothstep(0.0, 0.35, robeK);
  }
  T *= 0.86+0.28*vnoise(vec2(p.x*8.0+seed*5.0, p.y*3.5-uT*0.25));
  float body = 1.0-exp(-T*dens);
  // the warm core: heart and head
  vec2 dh = vP-fPts.xy, dd = vP-fPts.zw;
  float heart = exp(-dot(dh,dh)/(2.0*0.085*0.085));
  float headg = exp(-dot(dd,dd)/(2.0*0.045*0.045));
  float core = heart + headg*fPar.w;
  // form: the side that faces the light is warmer and brighter, the far side cooler (all round when the light
  // stands behind the figure); on that side a soft band of light just inside the edge, and a fine line
  vec2 nrm = normalize(g+vec2(1e-6));
  vec2 ld = normalize(fLight.xy-vP);
  float side = dot(nrm, ld);
  float fac = max(side, 0.0);
  fac = mix(fac*fac, 1.0, fLight.z);
  float form = mix(0.5+0.5*side, 0.8, fLight.z);
  float w0 = max(1.6*px, 0.0032);
  float line = exp(-pow((sd+w0)/w0, 2.0));
  float band = exp(-pow((sd+0.011)/0.011, 2.0));
  float up = mix(1.0, smoothstep(0.20, 0.66, vP.y), step(0.001, mistK));   // it fades down the robe: no rim on the mist
  float wav = mix(1.0, 0.55+0.45*vnoise(vec2(vP.x*13.0+seed*7.0, vP.y*13.0-uT*0.30)), detail);   // not a wire
  float edge = line;
  float rim = (band*0.60 + line*0.40*wav)*fac*up*fLight.w*smoothstep(0.10, 0.50, wsd);
  // a held flame or an offered light warms what is near it
  vec2 df = vP-fFx.xy;
  float fl = fFx.z*exp(-dot(df,df)/(2.0*0.105*0.105));
  // warm at the heart, cooler toward the hem, at the thin edges and on the far side
  float hemK = 1.0-smoothstep(0.03, 0.42, vP.y);
  vec3 warm = fColA.rgb, cool = mix(fColA.rgb, uMist, 0.55);
  vec3 tone = mix(mix(cool, warm, form), uMist, hemK*0.60*step(0.001, mistK));
  vec3 c = mix(uMist, tone, smoothstep(0.04, 0.50, body))*body*uGain*(0.70+0.60*form)*(1.0-0.40*uDay);
  c += fColB.rgb*core*body*fColB.a;
  c += uLightCol*rim;
  c += uFlameCol*fl*(body*1.25 + edge*up*0.6);
  // gather and dissolve: the body blooms out of its heart, and returns to it
  float rv = 1.0;
  if(fFx.w<9.0){
    float dist = length(dh)+0.12*(vnoise(vP*9.0+seed*3.0)-0.5);
    rv = 1.0-smoothstep(fFx.w-0.24, fFx.w, dist);
  }
  float a = fColA.a*rv;
  o = vec4(c*a, body*a*fPar.y);
}
"""

CLOTH_VS = """
#version 330
in vec2 aPos; in vec2 aUV; in vec4 aK; in vec3 aCol;
out vec2 vUV; out vec4 vK; out vec3 vCol;
void main(){ vUV = aUV; vK = aK; vCol = aCol; gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0); }
"""
# vK: alpha, fold density, number of threads, kind (0 a sheet of threads, 1 a single streamline)
CLOTH_FS = "#version 330\n" + G.NOISE + """
in vec2 vUV; in vec4 vK; in vec3 vCol;
uniform float uT, uDay;
out vec4 o;
void main(){
  float I;
  if(vK.w>0.5 && vK.w<1.5){
    I = vK.x*exp(-vUV.x*vUV.x*3.2);
  } else {
    float fu = vUV.x*vK.z;
    float id = floor(fu), f = fract(fu)-0.5;
    float h = hash11(id*1.37+3.1);
    float aa = fwidth(fu);
    float lw = 0.16+0.16*h;
    float line = exp(-pow(f/max(lw, aa*0.9), 2.0))*(0.30+0.70*h);
    line *= 0.60+0.40*sin(vUV.y*8.0-uT*1.1+h*40.0);
    line = mix(line, 0.30, smoothstep(0.30, 0.90, aa));      // far away the threads melt into one sheet
    // folds: bands of sheen that run down the cloth and wander as it billows
    float fold = 0.5+0.5*sin(vUV.x*15.0+2.4*vnoise(vec2(vUV.x*3.0+uT*0.16, vUV.y*2.2-uT*0.21))*6.283);
    fold = fold*fold;
    float side = min(vUV.x, 1.0-vUV.x);
    float du = max(fwidth(vUV.x)*1.6, 0.012), dv = max(fwidth(vUV.y)*1.6, 0.016);
    float tip = 1.0-smoothstep(0.62, 1.0, vUV.y);
    float sel = exp(-pow(side/du, 2.0));
    float hem = exp(-pow((1.0-vUV.y)/dv, 2.0))*smoothstep(0.0, 0.10, side);
    float body = (0.20+0.42*line+0.40*fold)*(0.30+0.70*tip);
    if(vK.w>2.5) I = vK.x*vK.y*(body*smoothstep(0.0, 0.10, side) + 0.20*sel);   // a sleeve: soft, hardly an edge
    else if(vK.w>1.5) I = vK.x*vK.y*body*smoothstep(0.0, 0.22, side);     // the lower robe: only threads
    else I = vK.x*vK.y*(body + 0.42*sel*(0.35+0.65*tip) + 0.50*hem);
  }
  o = vec4(vCol*I*(1.0-0.40*uDay), I*0.70);
}
"""

PT_VS = """
#version 330
in vec2 aPos; in vec2 aSz; in vec3 aCol;
uniform float uPx;
out vec3 vCol; out float vSharp;
void main(){ vCol = aCol; vSharp = aSz.y; gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0); gl_PointSize = aSz.x*uPx; }
"""
PT_FS = """
#version 330
in vec3 vCol; in float vSharp; out vec4 o;
void main(){ vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  o = vec4(vCol*exp(-r2*vSharp)*(1.0-r2*r2*0.15), 0.0); }
"""

# The figure layer is added to the light (uMode 0), and its mirror image to the lake (uMode 1): rippled like the
# engine's own reflections, fading with depth and calm in the lower third.
RESOLVE_FS = "#version 330\n" + G.NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uFig;
uniform float uT, uAspect, uWL, uRefl, uCalm, uCalmY, uKnee, uShare;
uniform int uMode;
vec3 shoulder(vec3 c){ float l = max(c.r, max(c.g, c.b)); return c/(1.0+l/uKnee); }
void main(){
  vec2 uv = vUV; vec3 c = vec3(0.0);
  if(uMode==0){
    c = shoulder(texture(uFig, uv).rgb)*uShare;
  } else if(uv.y<uWL){
    float d = (uWL-uv.y)/max(uWL, 0.05);
    float wob = (vnoise(vec2(uv.x*uAspect*24.0, uv.y*210.0-uT*0.85))-0.5)*0.011*(0.22+d)
              + sin(uv.y*240.0+uT*1.2)*0.0010;
    vec2 r = vec2(uv.x+wob, uv.y+wob*0.4);
    vec3 f = texture(uFig, r).rgb*0.5 + 0.25*(texture(uFig, r+vec2(0.0, 0.003)).rgb
                                              + texture(uFig, r-vec2(0.0, 0.003)).rgb);
    float ck = 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, uv.y));
    c = shoulder(f)*uRefl*(1.0-d)*(1.0-d)*mix(0.30, 1.0, ck);
  }
  o = vec4(c, 1.0);
}
"""


# ---------------------------------------------------------------- the body: rounded cones from the skeleton
SILK_ADULT = dict(neck=0.842, head=0.928, head_r=0.052, shoulder_y=0.812, shoulder_z=0.074, upper=0.168,
                  fore=0.152, hip_z=0.044, chest=0.705)
SILK_CHILD = dict(head_r=0.068, shoulder_z=0.080, hip_z=0.046)

# graceful versions of the open poses: the arms open low, 35 to 45 degrees below the horizontal, elbows soft,
# palms forward (arms="high" on the figure keeps the engine's wide poses)
SILK_POSES = {
    "open": dict(lean=-0.015, tilt=0.10, arm_r=(0.82, 1.34, 0.94, 1.16), arm_l=(0.82, 1.34, 0.94, 1.16)),
    "bless": dict(lean=-0.02, tilt=0.17, arm_r=(0.93, 1.30, 1.07, 1.10), arm_l=(0.93, 1.30, 1.07, 1.10)),
}


def _n3(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def stack_joints(J, z0=0.0):
    """A single body's joints (engine/rig.py) as arrays with one row, as the crowd has them."""
    dz = np.array([0.0, 0.0, z0])

    def a(v):
        return (np.asarray(v, dtype=np.float64) + dz)[None, :]

    out = dict(hip=a(J["hip"]), chest=a(J["chest"]), neck=a(J["neck"]), head=a(J["head"]))
    out["legs"] = {s: tuple(a(v) for v in J["legs"][s]) for s in (1.0, -1.0)}
    out["arms"] = {s: (a(J["arms"][s][0]), a(J["arms"][s][1]), a(J["arms"][s][2]),
                       np.asarray(J["arms"][s][3], dtype=np.float64)[None, :]) for s in (1.0, -1.0)}
    return out


class Frame2D:
    """Local 3D (x forward, y up, z sideways) to the figure's flat frame (x to the right of the screen)."""

    def __init__(self, cy, sy, sgn, off):
        self.cy, self.sy, self.sgn, self.off = (np.atleast_1d(np.asarray(v, dtype=np.float64))
                                                for v in (cy, sy, sgn, off))

    def pt(self, p):
        return np.stack([self.sgn * (p[:, 0] * self.cy + p[:, 2] * self.sy) + self.off, p[:, 1]], 1)

    def rad(self, rx, rz):
        return np.hypot(rx * self.cy, rz * self.sy)


def _leg_at(legs, side, y):
    H, K, A_, _ = legs[side]
    f = np.clip((H[:, 1] - y) / np.maximum(H[:, 1] - A_[:, 1], 1e-3), 0.0, 1.0)[:, None]
    return np.where(f < 0.5, H + (K - H) * (2 * f), K + (A_ - K) * (2 * f - 1))


def robe_at(J, F, lag, v, hem=0.035, k=1.0):
    """Centre (N,2) and half width (N,) of the robe at the share v of the way from the hip (0) to the hem (1)."""
    hip = J["hip"]
    y = hip[:, 1] + (hem - hip[:, 1]) * v
    a, b = _leg_at(J["legs"], 1.0, y), _leg_at(J["legs"], -1.0, y)
    c = 0.5 * (a + b)
    c[:, 0] += lag * v ** 1.6
    c2 = F.pt(c)
    c2[:, 1] = y
    half = 0.5 * np.abs(F.pt(a)[:, 0] - F.pt(b)[:, 0])
    rx = np.interp(v, [0.0, 0.33, 0.66, 1.0], [0.047, 0.055, 0.066, 0.090])
    rz = np.interp(v, [0.0, 0.33, 0.66, 1.0], [0.062, 0.069, 0.082, 0.106])
    return c2, F.rad(rx * k, rz * k) + np.minimum(0.50 * half, 0.05)


def hand_dir(d2):
    """Where the hand points: it follows the forearm, lifts at the wrist as the arm rises (palms forward) and
    curls a little while it hangs."""
    opn = np.clip((d2[:, 1] + 0.95) / 0.6, 0.0, 1.0)[:, None]
    return _n3(d2 + np.array([0.0, 0.30, 0.0]) * opn + np.array([0.12, 0.0, 0.0]) * (1 - opn))


def person_segments(J, F, lag, veil=False, full=True, wide=1.0, head_r=0.052):
    """The rounded cones of N people: array (N, n, 12) of ax, ay, bx, by, ra, rb, wa, wb, part, kind, 0, 0,
    and the heart and head centres (N, 2). full=False is the light version for a crowd."""
    N = len(J["hip"])
    segs = []

    def add(A_, B_, ra, rb, wa, wb, part, kind=0.0):
        segs.append((A_, B_, ra, rb, wa, wb, part, kind))

    hip, chest, neck, head = J["hip"], J["chest"], J["neck"], J["head"]
    arms = J["arms"]
    k = wide
    ush = chest + (neck - chest) * 0.62
    waist = hip + (chest - hip) * 0.34
    if full:
        r_ush, r_ch, r_wa, r_hip = (F.rad(0.034 * k, 0.050 * k), F.rad(0.045 * k, 0.062 * k),
                                    F.rad(0.036 * k, 0.047 * k), F.rad(0.047 * k, 0.062 * k))
        sa, sb = arms[1.0][0], arms[-1.0][0]
    else:
        # a crowd wears cloaks: one soft bell from sloping shoulders to the ground, the hanging arms inside it
        r_ush, r_ch, r_hip = F.rad(0.050 * k, 0.092 * k), F.rad(0.056 * k, 0.098 * k), F.rad(0.062 * k, 0.104 * k)
        ush = ush - np.array([0.0, 0.028, 0.0])
        sa = sb = ush
    # part 0: neck, shoulders, torso and robe, one flowing shape
    add(F.pt(neck + (head - neck) * 0.50), F.pt(neck), 0.0185, 0.0215, 1.0, 1.0, 0)
    add(F.pt(neck), F.pt(ush), 0.022, r_ush, 1.0, 1.0, 0)
    add(F.pt(sa), F.pt(sb), 0.0245, 0.0245, 1.0, 1.0, 0)
    if full:
        add(F.pt(ush), F.pt(chest), r_ush, r_ch, 1.0, 1.0, 0)
        add(F.pt(chest), F.pt(waist), r_ch, r_wa, 1.0, 0.95, 0)
        add(F.pt(waist), F.pt(hip), r_wa, r_hip, 0.95, 0.86, 0)
        vs, ws, kr = (0.0, 0.33, 0.66, 1.0), (0.90, 0.84, 0.68, 0.28), k
    else:
        add(F.pt(ush), F.pt(chest), r_ush, r_ch, 1.0, 1.0, 0)
        add(F.pt(chest), F.pt(hip), r_ch, r_hip, 1.0, 0.92, 0)
        vs, ws, kr = (0.0, 0.5, 1.0), (0.95, 0.86, 0.56), k * 1.55
    prev = (F.pt(hip), r_hip)
    for v, w0, w1 in zip(vs[1:], ws[:-1], ws[1:]):
        c2, r = robe_at(J, F, lag, v, k=kr)
        add(prev[0], c2, prev[1], r, w0, w1, 0, 1.0)
        prev = (c2, r)
    # part 1: the head, a soft oval glow under hair or a veil (no face)
    up = np.array([0.0, 1.0, 0.0])
    add(F.pt(head - up * 0.015), F.pt(head + up * 0.016), head_r * 0.90, head_r * 0.86, 1.25, 1.25, 1, 2.0)
    if not full:
        # in a crowd some wear a veil or a hood (the head flows into the shoulders), the others show hair
        vv = np.broadcast_to(np.asarray(veil, dtype=np.float64), (N,))
        add(F.pt(head + np.array([-0.004, 0.020, 0.0])), F.pt(ush + np.array([-0.012, 0.0, 0.0])),
            (head_r + 0.004) * vv + 0.001, r_ush * 0.92 * vv + 0.001, 0.90 * vv, 0.70 * vv, 1, 2.0)
        add(F.pt(head + np.array([-0.015, 0.006, 0.0])), F.pt(neck + np.array([-0.030, -0.034, 0.0])),
            head_r * 0.88 * (1 - vv) + 0.001, 0.026 * (1 - vv) + 0.001, 0.95 * (1 - vv), 0.50 * (1 - vv), 1, 2.0)
    elif veil:
        add(F.pt(head + np.array([-0.006, 0.018, 0.0])), F.pt(ush + np.array([-0.022, -0.012, 0.0])),
            head_r + 0.002, F.rad(0.050, 0.088), 0.80, 0.50, 1, 2.0)
    else:
        add(F.pt(head + np.array([-0.015, 0.006, 0.0])), F.pt(neck + np.array([-0.030, -0.034, 0.0])),
            head_r * 0.88, 0.026, 0.95, 0.50, 1, 2.0)
    # parts 2 and 3: the arms, the bell of each sleeve and the hands
    for part, side in ((2, 1.0), (3, -1.0)):
        S0, E, W, d2 = arms[side]
        hd = hand_dir(d2)
        if full:
            add(F.pt(S0), F.pt(E), 0.0225, 0.0195, 0.9, 0.9, part, 3.0)
            add(F.pt(E), F.pt(W), 0.0195, 0.0160, 0.9, 0.9, part, 3.0)
            add(F.pt(E + (W - E) * 0.12), F.pt(W - d2 * 0.006), 0.024, 0.037, 0.36, 0.46, part, 3.0)
            add(F.pt(W), F.pt(W + hd * 0.034), 0.0150, 0.0140, 1.0, 1.0, part, 3.0)
            add(F.pt(W + hd * 0.030), F.pt(W + hd * 0.072), 0.0128, 0.0062, 1.0, 0.55, part, 3.0)
            td = _n3(hd * 0.6 + np.array([0.5, 0.35, 0.0]))
            add(F.pt(W + hd * 0.014), F.pt(W + hd * 0.014 + td * 0.030), 0.0075, 0.0050, 0.9, 0.8, part, 3.0)
        else:
            # an arm shows only when it reaches, holds or lifts; hanging, it is inside the cloak
            rf = 1.0 + d2[:, 1]
            ru = np.maximum(1.0 + _n3(E - S0)[:, 1], 0.7 * rf)
            wu, wf = 0.12 + 0.88 * ss(0.12, 0.55, ru), 0.12 + 0.88 * ss(0.12, 0.55, rf)
            add(F.pt(S0), F.pt(E), 0.0235, 0.0210, 0.9 * wu, 0.9 * wf, part, 3.0)
            add(F.pt(E), F.pt(W), 0.0210, 0.0180, 0.9 * wf, 0.9 * wf, part, 3.0)
            add(F.pt(W), F.pt(W + hd * 0.045), 0.0180, 0.0115, wf, wf, part, 3.0)
    out = np.zeros((N, len(segs), 12), np.float32)
    for i, (A_, B_, ra, rb, wa, wb, part, kind) in enumerate(segs):
        out[:, i, 0:2], out[:, i, 2:4] = A_, B_
        out[:, i, 4], out[:, i, 5], out[:, i, 6], out[:, i, 7] = ra, rb, wa, wb
        out[:, i, 8], out[:, i, 9] = part, kind
    heart = F.pt(chest + (neck - chest) * 0.36)
    return out, heart, F.pt(head)


def hands_segments(J):
    """Two hands (engine/rig.py Hands.joints): palms, fingers that curl, thumbs and the sleeves below."""
    segs = []

    def add(A_, B_, ra, rb, wa, wb, part):
        segs.append((np.asarray(A_, float), np.asarray(B_, float), ra, rb, wa, wb, part))

    for hi, side in enumerate((1.0, -1.0)):
        h = J[side]
        W, palm, up = h["W"], h["palm"], h["up"]
        part = hi * 2
        add(W + up * 0.030, palm + up * 0.050, 0.050, 0.056, 1.0, 1.0, part)
        add(W - up * 0.01, W + up * 0.04, 0.036, 0.046, 0.95, 1.0, part)
        for fi, ch in enumerate(h["fingers"]):
            rr = (0.0172, 0.0160, 0.0145, 0.0118) if fi in (1, 2) else (0.0160, 0.0148, 0.0132, 0.0105)
            for j in range(3):
                add(ch[j], ch[j + 1], rr[j], rr[j + 1], 1.0, 1.0, part)
        tb, t1, t2 = h["thumb"]
        add(tb, t1, 0.0200, 0.0170, 1.0, 1.0, part)
        add(t1, t2, 0.0170, 0.0125, 1.0, 1.0, part)
        # the sleeve: wide at the wrist, fading out below
        el = h["elbow"]
        add(el + (W - el) * 0.22, W - up * 0.015, 0.034, 0.074, 0.0, 0.50, part + 1)
        add(el + (W - el) * 0.45, W + up * 0.005, 0.022, 0.030, 0.08, 0.85, part + 1)
    out = np.zeros((1, len(segs), 12), np.float32)
    for i, (A_, B_, ra, rb, wa, wb, part) in enumerate(segs):
        out[0, i, 0:2], out[0, i, 2:4] = A_, B_
        out[0, i, 4:8] = (ra, rb, wa, wb)
        out[0, i, 8], out[0, i, 9] = part, 3.0
    return out


def seg_rect(segs, n=None, pad=0.03):
    """The box (N,4) round each body's cones."""
    s = segs if n is None else segs[:, :n]
    r = np.maximum(s[..., 4], s[..., 5])
    x0 = np.minimum(s[..., 0], s[..., 2]) - r
    x1 = np.maximum(s[..., 0], s[..., 2]) + r
    y0 = np.minimum(s[..., 1], s[..., 3]) - r
    y1 = np.maximum(s[..., 1], s[..., 3]) + r
    return np.stack([x0.min(1) - pad - 0.05, y0.min(1) - pad - 0.03, x1.max(1) + pad + 0.05, y1.max(1) + pad], 1)


# ---------------------------------------------------------------- cloth: spring chains in the wind
def catmull(P, f):
    """Smooth a polyline along its last-but-one axis: (..., K, 2) -> (..., (K-1)*f+1, 2)."""
    if f <= 1:
        return P
    K = P.shape[-2]
    Pm = np.concatenate([2 * P[..., :1, :] - P[..., 1:2, :], P, 2 * P[..., -1:, :] - P[..., -2:-1, :]], axis=-2)
    p0, p1, p2, p3 = Pm[..., :-3, :], Pm[..., 1:-2, :], Pm[..., 2:-1, :], Pm[..., 3:, :]
    out = []
    for j in range(f):
        u = j / f
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    body = np.stack(out, axis=-2)                        # (..., K-1, f, 2)
    body = body.reshape(P.shape[:-2] + ((K - 1) * f, 2))
    return np.concatenate([body, P[..., -1:, :]], axis=-2)


_GRID_IDX = {}


def grid_tris(R, C):
    """Triangle indices of a grid of R rows by C columns of vertices (row-major)."""
    key = (R, C)
    if key not in _GRID_IDX:
        i = np.arange(R - 1)[:, None] * C + np.arange(C - 1)[None, :]
        a, b, c, d = i, i + 1, i + C, i + C + 1
        _GRID_IDX[key] = np.stack([a, b, c, b, d, c], -1).reshape(-1)
    return _GRID_IDX[key]


class Cloth:
    """The cloth of one body: sheets (veil, two sleeves, the lower robe) and free streamlines, all spring chains.

    Each chain hangs from a point of the body. simulate() runs them for the last WARM seconds up to t: gravity,
    air that drags against the motion (so the cloth trails behind a walk and swings on when she stops), the
    shared wind with gusts and travelling ripples, and neighbours in a sheet that hold their spacing loosely."""
    WARM = 3.2          # seconds simulated before each frame (several times the cloth's own settling time)
    EVERY = 2           # the skeleton is posed every second step, anchors are interpolated between
    GROUND = True
    ITERS = 5           # passes of the link lengths per step

    def __init__(self, veil, rng, m, child=False):
        self.veil = bool(veil)
        K = self.K = 14
        self.groups = []
        C = 0
        ln = dict(veil=float(opt(m, "veil_length", 1.0)), sleeve=float(opt(m, "sleeve_length", 1.0)),
                  strand=float(opt(m, "strand_length", 1.0)))
        self.len_k = ln
        n_str = int(opt(m, "strands", 27))
        spec = []
        if self.veil:
            spec.append(("veil", 11, 13, dict(g=1.5, km=3.2, kw=2.2, lines=44, alpha=0.34)))
        spec.append(("sleeve_r", 6, 8, dict(g=2.0, km=3.0, kw=1.4, lines=20, alpha=0.44)))
        spec.append(("sleeve_l", 6, 8, dict(g=2.0, km=3.0, kw=1.4, lines=20, alpha=0.44)))
        spec.append(("hem", 9, 9, dict(g=2.6, km=3.0, kw=0.9, lines=40, alpha=0.17)))
        if n_str > 0:
            spec.append(("strand", n_str, 14, dict(g=0.9, km=3.6, kw=1.5, lines=0, alpha=0.62)))
        for name, M, Kg, par in spec:
            self.groups.append(dict(name=name, c0=C, M=M, K=Kg, **par))
            C += M
        self.C = C
        self.g = np.zeros(C)
        self.km = np.zeros(C)
        self.kw = np.zeros(C)
        self.ph = np.zeros(C)
        self.kmax = np.zeros(C, int)
        for gr in self.groups:
            sl = slice(gr["c0"], gr["c0"] + gr["M"])
            self.g[sl], self.km[sl], self.kw[sl] = gr["g"], gr["km"], gr["kw"]
            self.kmax[sl] = gr["K"]
            if gr["name"] == "strand":
                self.ph[sl] = rng.random(gr["M"]) * TAU
                gr["len"] = (0.26 + 0.40 * rng.random(gr["M"])) * ln["strand"]
                gr["seed"] = rng.random((gr["M"], 3))
                self.g[sl] *= 0.75 + 0.5 * rng.random(gr["M"])
                self.kw[sl] *= 0.8 + 0.5 * rng.random(gr["M"])
            else:
                self.ph[sl] = 0.55 * np.linspace(-1, 1, gr["M"]) + rng.random() * TAU
        self.node = np.arange(K)[None, :]                      # (1, K)
        self.live = self.node < self.kmax[:, None]             # (C, K) nodes in use
        self.m = m

    # ------------------------------------------------------------ where each chain hangs, and how long it is
    def anchors(self, J, F, lag, hr):
        """Root points (C,2) and chain lengths (C,) from one body's joints (arrays with one row)."""
        A_ = np.zeros((self.C, 2))
        L = np.zeros(self.C)
        hip, chest, neck, head = J["hip"], J["chest"], J["neck"], J["head"]
        arms = J["arms"]
        ush = chest + (neck - chest) * 0.62
        for gr in self.groups:
            c0, M = gr["c0"], gr["M"]
            name = gr["name"]
            if name == "veil":
                u = np.linspace(-1, 1, M)
                th = np.clip(np.abs(u) / 0.5, 0, 1) * 1.75 * np.sign(u)
                hp = head + np.stack([np.full(M, -0.010), hr * 1.07 * np.cos(th), hr * 1.03 * np.sin(th)], 1)
                sp = np.where((u > 0)[:, None], arms[1.0][0], arms[-1.0][0]) + \
                    np.stack([np.full(M, -0.012), np.full(M, 0.016), 0.014 * np.sign(u)], 1)
                b = ss(0.5, 1.0, np.abs(u))[:, None]
                P = hp * (1 - b) + sp * b
                P2 = F.pt(P)
                A_[c0:c0 + M] = P2
                L[c0:c0 + M] = np.maximum(P2[:, 1] - (0.25 + 0.10 * u * u), 0.15) * self.len_k["veil"]
            elif name in ("sleeve_r", "sleeve_l"):
                side = 1.0 if name == "sleeve_r" else -1.0
                S0, E, W, d2 = arms[side]
                q = np.array([0.34, 0.50, 0.64, 0.78, 0.90, 1.0])[:M]
                P = np.where((q < 0.5)[:, None], S0 + (E - S0) * (q / 0.5)[:, None],
                             E + (W - E) * ((q - 0.5) / 0.5)[:, None]) + np.array([0.0, -0.010, 0.0])
                A_[c0:c0 + M] = F.pt(P)
                L[c0:c0 + M] = (0.022 + 0.165 * ((q - 0.30) / 0.70) ** 1.8) * self.len_k["sleeve"]
            elif name == "hem":
                c2, r = robe_at(J, F, lag, 0.60)
                u = np.linspace(-1, 1, M)
                A_[c0:c0 + M, 0] = c2[0, 0] + u * 0.93 * r[0]
                A_[c0:c0 + M, 1] = c2[0, 1]
                L[c0:c0 + M] = np.maximum(c2[0, 1] - 0.035 - 0.03 * np.abs(u), 0.05)
            else:
                sd = gr["seed"]
                waist = hip + (chest - hip) * 0.34
                P = np.zeros((M, 3))
                for i in range(M):
                    j = i % 9
                    a, b_ = sd[i, 0], sd[i, 1]
                    if j in (0, 5):          # the back of the head
                        th = (a * 2 - 1) * 1.4
                        P[i] = head[0] + np.array([-0.012, hr * 0.9 * math.cos(th), hr * math.sin(th)])
                    elif j in (1, 6):        # the shoulders
                        s_ = 1.0 if j == 1 else -1.0
                        P[i] = arms[s_][0][0] + np.array([-0.010, 0.012 - 0.02 * a, s_ * 0.012 * b_])
                    elif j in (2, 7):        # elbow and wrist of one arm, then the other
                        s_ = 1.0 if j == 2 else -1.0
                        S0, E, W, d2 = arms[s_]
                        P[i] = E[0] + (W[0] - E[0]) * a
                    elif j == 3:             # the back, at the waist
                        P[i] = waist[0] + np.array([-0.030, 0.06 * a, (b_ * 2 - 1) * 0.045])
                    elif j == 4:             # the heart
                        P[i] = ush[0] + np.array([-0.01, -0.05 * a, (b_ * 2 - 1) * 0.04])
                    else:                    # the upper back
                        P[i] = ush[0] + np.array([-0.028, 0.01 - 0.08 * a, (b_ * 2 - 1) * 0.05])
                A_[c0:c0 + M] = F.pt(P)
                L[c0:c0 + M] = gr["len"]
        return A_, L

    def wind(self, X, Y, t, base, ph):
        """Air speed (figure heights per second) at the nodes: the shared gusts and travelling ripples."""
        a = 0.10 + 0.40 * abs(base)
        wx = base * (1.0 + 0.25 * np.sin(3.1 * Y - 1.1 * t + ph)) + a * (
            0.55 * np.sin(5.3 * Y - 2.3 * t + 1.7 * X + ph) + 0.35 * np.sin(11.0 * Y + 3.4 * t - 2.6 * X + 2 * ph))
        wy = a * (0.40 * np.sin(4.1 * X + 1.9 * t + 2.2 * Y + ph) + 0.30 * np.sin(8.3 * Y - 2.9 * t + 1.3 * ph))
        return wx, wy

    def simulate(self, t, anchor_fn, origin_fn, base_fn):
        """Chain nodes (C,K,2) at t, in the figure's own frame at t.
        anchor_fn(t) -> (roots (C,2) in the figure's frame, lengths (C,)); origin_fn(t) -> where the figure
        stands, in figure heights (so the cloth feels the walk); base_fn(t) -> the wind's push at the figure."""
        dt = 1.0 / 60.0 if int(round(getattr(S, "FPS", 30))) > 30 else 1.0 / 30.0   # a whole step per frame
        ev = self.EVERY
        n = int(round(self.WARM / dt / ev)) * ev
        C, K = self.C, self.K
        ks = np.arange(0, n + 1, ev)
        samp, Ls, org, base = [], None, [], []
        for kk in ks:
            tk = t - (n - kk) * dt
            a, L = anchor_fn(tk)
            o = np.asarray(origin_fn(tk), dtype=np.float64)
            samp.append(a + o[None, :])
            org.append(o)
            base.append(base_fn(tk))
            Ls = L
        samp = np.array(samp)                                   # (len(ks), C, 2) in the world
        base = np.array(base)
        seg = (Ls / np.maximum(self.kmax - 1, 1))[:, None] * self.live      # (C, K) length of the link above
        seg[:, 0] = 0.0
        cum = np.cumsum(seg, 1)
        ground = org[0][1] + 0.010

        def at(j):
            f = j / ev
            i = min(int(f), len(ks) - 2)
            u = f - i
            return samp[i] * (1 - u) + samp[i + 1] * u, base[i] * (1 - u) + base[i + 1] * u

        # the start: every chain hangs the way the wind and the figure's own walk would leave it (the steps and
        # the breathing are left out, so this start changes smoothly from one frame to the next)
        A0, b0 = at(0)
        k1 = min(len(ks) - 1, max(1, int(round(0.5 / dt / ev))))
        V0 = np.tile((org[k1] - org[0]) / (k1 * ev * dt), (C, 1))
        ph = self.ph[:, None]
        wx, wy = self.wind(A0[:, :1], A0[:, 1:2], t - n * dt, b0, ph)
        f0 = np.stack([self.kw * wx[:, 0] - self.km * V0[:, 0], -self.g + self.kw * wy[:, 0] - self.km * V0[:, 1]], 1)
        d0 = f0 / np.maximum(np.linalg.norm(f0, axis=1, keepdims=True), 1e-6)
        X = A0[:, None, :] + cum[:, :, None] * d0[:, None, :]
        Xp = X - V0[:, None, :] * dt
        km, kw = self.km[:, None], self.kw[:, None]
        sheets = [(gr["c0"], gr["M"]) for gr in self.groups if gr["name"] != "strand"]
        segl = seg[:, 1:]                                         # (C, K-1) length of each link
        for j in range(1, n + 1):
            tj = t - (n - j) * dt
            Aj, bj = at(j)
            V = (X - Xp) / dt
            wx, wy = self.wind(X[..., 0], X[..., 1], tj, bj, ph)
            # gravity and the wind push; the air drags against the motion (implicit, so it cannot overshoot)
            V[..., 0] = (V[..., 0] + kw * wx * dt) / (1.0 + km * dt)
            V[..., 1] = (V[..., 1] + (kw * wy - self.g[:, None]) * dt) / (1.0 + km * dt)
            Xn = X + V * dt
            Xn[:, 0] = Aj
            for _ in range(self.ITERS):       # links keep their length: every other link, then the ones between
                for o in (0, 1):
                    pa, pb = Xn[:, o:K - 1:2], Xn[:, o + 1:K:2]
                    d = pb - pa
                    l = np.maximum(np.hypot(d[..., 0], d[..., 1]), 1e-7)
                    corr = d * (0.5 * (1.0 - segl[:, o::2] / l))[..., None]
                    pb -= corr
                    pa += corr
                    if o == 0:                                    # the root is held: the first node gives way alone
                        Xn[:, 1] -= corr[:, 0]
                        Xn[:, 0] = Aj
            for c0, M in sheets:                                  # neighbours in a sheet keep a loose spacing
                a, b = Xn[c0:c0 + M - 1], Xn[c0 + 1:c0 + M]
                d = b - a
                l = np.maximum(np.hypot(d[..., 0], d[..., 1]), 1e-7)
                w0 = (l[:, :1] * (1.0 + 0.55 * cum[c0:c0 + M - 1] / np.maximum(Ls[c0:c0 + M - 1, None], 1e-6))
                      + 0.004)
                tgt = np.clip(l, 0.30 * w0, 1.5 * w0)
                corr = (d * ((l - tgt) / l)[..., None]) * 0.25
                corr[:, 0] = 0.0
                Xn[c0:c0 + M - 1] += corr
                Xn[c0 + 1:c0 + M] -= corr
            if self.GROUND:
                low = Xn[..., 1] < ground                         # the ground: cloth comes to rest on it
                Xn[..., 1] = np.where(low, ground, Xn[..., 1])
                X[low] = Xn[low]
            Xp, X = X, Xn
        return X - org[-1][None, None, :], Ls


# ---------------------------------------------------------------- a single figure (kind="rig")
def silk_actions(actions, m):
    """The figure's actions with the graceful open poses in place of the wide ones."""
    if opt(m, "arms", "low") != "low":
        return actions
    k = math.radians(float(opt(m, "open_angle", 42.0)) - 42.0)   # degrees below the horizontal (default 42)
    out = []
    for a in actions:
        if isinstance(a[1], str) and a[1] in SILK_POSES:
            tgt = dict(RG.POSES[a[1]])
            sp = dict(SILK_POSES[a[1]])
            for key in RG.ARMS:
                v = sp[key]
                sp[key] = (v[0] - k, v[1], v[2] - k, v[3])
            tgt.update(sp)
            if len(a) > 2 and isinstance(a[2], dict):
                tgt.update(a[2])
            out.append((a[0], tgt))
        else:
            out.append(a)
    return out


class SilkRig:
    """One FIGURES entry in the silk look: the rig's skeleton, with a body of light and cloth on it."""

    def __init__(self, m, k, fig_value):
        mm = dict(m)
        mm["particles"] = 256                       # the rig's sparks are not drawn
        mm["blend"] = float(m.get("blend", 1.4))    # poses flow into each other more slowly
        self.m = m
        R = self.rig = RG.Rig(mm, S.ASPECT, fig_value, seed=k)
        self.is_hands = R.hands is not None
        self.seed = (k * 0.6180339 + 0.137) % 1.0
        rng = np.random.default_rng(7700 + k)
        self.cloth = []
        if not self.is_hands:
            R.actions = silk_actions(R.actions, m)
            for b in R.bodies:
                child = R.preset == "child"
                keep = b.P["stride"]
                b.P.update(SILK_CHILD if child else SILK_ADULT)
                b.P["stride"] = keep
                self.cloth.append(Cloth(b.veil, rng, m, child) if opt(m, "cloth", True) else None)
        nm = int(opt(m, "motes", 30))
        self.mote = rng.random((nm, 6))
        self.elbow_lag = float(opt(m, "elbow_lag", 0.30))
        self.draft_keep = True

    # ------------------------------------------------------------ the posed skeleton, moving with more grace
    def skeleton(self, t):
        R = self.rig
        p = R.pose(t)
        if self.is_hands:
            return p, [R.hands.joints(t, p)]
        pl = R.pose(t - self.elbow_lag)             # soft elbows: the forearms follow the upper arms a little late
        for key in RG.ARMS:
            a, b = p.get(key, RG.HANG), pl.get(key, RG.HANG)
            p[key] = (a[0], a[1], b[2], b[3])
        v, vs = R.vel(t)
        walk = p.get("walk", 0.0)
        if R.auto_walk:
            walk = max(walk, RG._ssf(0.05, 0.16, abs(vs)), RG._ssf(0.05, 0.16, abs(v)))
        d = R.dist(t) / max(math.cos(p.get("yaw", R.bodies[0].yaw0)), 0.35)
        out = []
        for b in R.bodies:
            J = b.joints(t, p, d, walk, (v, vs))
            # the spine and the head sway a little, the arms ride on the shoulders
            ph = b.phase * 5.0 + self.seed * 9.0
            k = 1.0 - 0.6 * walk
            w = TAU * t / 7.3 + ph
            dz = (0.006 * math.sin(w) * k, 0.011 * math.sin(w - 0.7) * k, 0.015 * math.sin(w - 1.3) * k)
            dx = 0.004 * math.sin(TAU * t / 9.1 + ph) * k
            J["hip"] = J["hip"] + np.array([0.0, 0.0, dz[0]])
            J["chest"] = J["chest"] + np.array([dx, 0.0, dz[1]])
            J["neck"] = J["neck"] + np.array([dx * 1.3, 0.0, dz[1] * 1.15])
            J["head"] = J["head"] + np.array([dx * 1.6, 0.0, dz[2]])
            sh = np.array([dx * 1.1, 0.0, dz[1] * 1.05])
            J["arms"] = {s: (a[0] + sh, a[1] + sh, a[2] + sh, a[3]) for s, a in J["arms"].items()}
            out.append(J)
        return p, out

    def _lag(self, t):
        v, vs = self.rig.vel(t)
        return max(-0.08, min(0.08, -0.09 * vs - 0.12 * (v - vs)))

    def frames(self, t, p):
        """The flat frame of each body at t."""
        R = self.rig
        yaw = p.get("yaw", R.bodies[0].yaw0)
        out = []
        for b in R.bodies:
            if R.preset == "pair" and not R.together:
                b.x0 = -b.facing * p.get("gap", R.gap) / 2
            out.append(Frame2D(math.cos(yaw), math.sin(yaw), R.face * b.facing, R.face * b.x0))
        return out

    def bodies_at(self, t):
        """Per body: joints (arrays of one row), flat frame, robe lag."""
        R = self.rig
        p, Js = self.skeleton(t)
        Fs = self.frames(t, p)
        lag = self._lag(t)
        out = []
        for b, J, F in zip(R.bodies, Js, Fs):
            z0 = b.z0 if (R.preset == "pair" and R.together) else 0.0
            out.append((stack_joints(J, z0), F, lag))
        return p, out


# ---------------------------------------------------------------- the crowd (engine/gathering.py)
def cluster_x(tx, cx, amount, seed):
    """Moves a crowd's standing places into small groups with gaps between, so it reads as people, not a fence."""
    if amount <= 0 or len(tx) < 4:
        return tx
    rng = np.random.default_rng(seed + 991)
    order = np.argsort(tx)
    out = tx.copy()
    i = 0
    xs = tx[order]
    while i < len(xs):
        n = int(rng.integers(1, 5))
        idx = order[i:i + n]
        c = xs[i:i + n].mean()
        out[idx] = c + (tx[idx] - c) * (1.0 - 0.45 * amount) + (rng.random() - 0.5) * 0.004
        i += n
    return out


# ---------------------------------------------------------------- the layer, drawn by render.py
class FigureLook:
    def __init__(self, R):
        self.R = R
        self.on = wanted()
        self.used = False
        if not self.on:
            return
        ctx = self.ctx = R.ctx
        w, h = R.w, R.h
        self.t_fig = ctx.texture((w, h), 4, dtype="f2")
        self.t_fig.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.t_fig.repeat_x = self.t_fig.repeat_y = False
        self.f_fig = ctx.framebuffer([self.t_fig])
        self.t_ref = ctx.texture((max(w // 2, 8), max(h // 2, 8)), 4, dtype="f2")
        self.t_ref.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.t_ref.repeat_x = self.t_ref.repeat_y = False
        self.f_ref = ctx.framebuffer([self.t_ref])
        self.t_seg = ctx.texture((MAXSEG * 3, ROWS), 4, dtype="f4")
        self.t_seg.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.p_body = ctx.program(vertex_shader=BODY_VS, fragment_shader=BODY_FS)
        self.p_cloth = ctx.program(vertex_shader=CLOTH_VS, fragment_shader=CLOTH_FS)
        self.p_pt = ctx.program(vertex_shader=PT_VS, fragment_shader=PT_FS)
        self.p_res = ctx.program(vertex_shader=G.QUAD_VS, fragment_shader=RESOLVE_FS)
        if "uFlip" in self.p_res:
            self.p_res["uFlip"].value = 1.0
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        unit = ctx.buffer(np.array([0, 0, 1, 0, 0, 1, 1, 1], "f4").tobytes())
        self.b_inst = ctx.buffer(reserve=ROWS * 36 * 4, dynamic=True)
        self.gl = dict(draft_keep=True)   # ordered buffers: a draft draws them whole (engine/draft.py)
        self.gl["res"] = ctx.vertex_array(self.p_res, [(quad, "2f", "aPos")])
        self.gl["body"] = ctx.vertex_array(
            self.p_body, [(unit, "2f", "aQ"),
                          (self.b_inst, "4f 4f 4f 4f 4f 4f 4f 4f 4f/i", "iRect", "iOrg", "iInfo", "iColA", "iColB",
                           "iPts", "iLight", "iFx", "iPar")], skip_errors=True)
        self.cap_c = self.cap_p = 0
        self.b_cloth = self.b_pt = None
        self._reset()

    def _reset(self):
        self.q_inst, self.q_seg, self.q_cloth, self.q_pt = [], [], [], []
        self.q_inst_m, self.q_cloth_m, self.q_pt_m = [], [], []
        self.used = False

    # ------------------------------------------------------------ what the figures hand over
    def light(self, m, t, P):
        """Where the scene's light is on screen, and its colour."""
        spec = opt(m, "light_from", "sun")
        if callable(spec):
            spec = spec(t)
        pos = None
        if isinstance(spec, str) and spec.startswith("star"):
            sp = getattr(S, "STAR_POS", None) or [(0.5, 0.9)]
            k = int(spec.split(":")[1]) if ":" in spec else len(sp) // 2
            pos = sp[min(max(k, 0), len(sp) - 1)]
        elif isinstance(spec, (tuple, list)):
            pos = (float(spec[0]), float(spec[1]))
        if pos is None:
            pos = (0.5, max(float(P["sun_y"]), S.HORIZON + 0.03))
            sky = getattr(self.R, "sky", None)
            if sky is not None and getattr(sky, "_state", None) is not None:
                try:
                    q = sky.sun_screen(t, P)
                    pos = (float(q[0]), max(float(q[1]), S.HORIZON + 0.03))
                except Exception:
                    pass
        c = opt(m, "light_color", None)
        if c is None:
            g = np.asarray(P["glow"], dtype=np.float64)
            g = g / max(float(g.max()), 1e-6)
            c = _lin("#fff6e6") * 0.72 + g * 0.28
        else:
            c = _lin(c)
        return pos, c

    def add_bodies(self, segs, nseg, rect, org, scale, colA, colB, pts, light, fx, par, px, seed, mirror=None):
        """Queues N bodies. segs (N, n, 12); rect (N,4) own frame; org (N,2) and scale (N,2) on screen; colA
        (N,4) body colour and alpha; colB (N,4) core colour and gain; pts (N,4) heart and head; light (N,4) the
        light in the body's frame, how far it stands behind the body, rim strength; fx (N,4) flame place,
        strength, reveal radius (99 = whole); par (N,4) detail, tint share, mist, head glow.
        mirror: None, or (water line y (N,), squeeze) to also queue the mirror image in the lake."""
        N = len(segs)
        row0 = len(self.q_seg)
        for i in range(N):
            self.q_seg.append(segs[i, :nseg])
        rows = row0 + np.arange(N)
        info = np.stack([rows, np.full(N, nseg), px, seed], 1)
        inst = np.concatenate([rect, org, scale, info, colA, colB, pts, light, fx, par], 1).astype("f4")
        self.q_inst.append(inst)
        if mirror is not None:
            wl, sq = mirror
            im = inst.copy()
            im[:, 5] = wl - (org[:, 1] - wl) * sq
            im[:, 7] = -scale[:, 1] * sq
            im[:, 10] = px * 2.0
            self.q_inst_m.append(im)
        self.used = True

    def add_cloth(self, verts, mirror=None):
        """Queues cloth triangles: rows of x, y (screen), u, v, alpha, fold, threads, kind, r, g, b."""
        if len(verts) == 0:
            return
        self.q_cloth.append(verts.astype("f4"))
        if mirror is not None:
            wl, sq = mirror
            vm = verts.astype("f4").copy()
            vm[:, 1] = wl - (vm[:, 1] - wl) * sq
            self.q_cloth_m.append(vm)
        self.used = True

    def add_points(self, pts, mirror=None):
        """Queues soft points: rows of x, y, size (px at 1080p), sharpness, r, g, b."""
        if len(pts) == 0:
            return
        self.q_pt.append(pts.astype("f4"))
        if mirror is not None:
            wl, sq = mirror
            pm = pts.astype("f4").copy()
            pm[:, 1] = wl - (pm[:, 1] - wl) * sq
            self.q_pt_m.append(pm)
        self.used = True

    # ------------------------------------------------------------ a single figure
    def draw_rig(self, sr, up, t, P):
        m, R = sr.m, sr.rig
        gat, dis = float(m.get("gather", 3.0)), float(m.get("dissolve", 3.5))
        if not (R.t0 <= t < R.t1 + dis):
            return
        x, y, h = R.place(t)
        to = S.STAR_POS[m["to_star"]] if "to_star" in m else m.get("to", (0.5, 0.90))
        aff, _ = up._camera(m, t, y, to)   # the arch does not move with the camera: `to` stays a screen point
        asp = S.ASPECT
        glow = float(m.get("glow", 1.0))
        col = _lin(m.get("color", "#ffcf8a"))
        col = col * (0.45 + 0.60 * col)          # a deeper gold for the body: the white is kept for the heart
        core = _lin(opt(m, "core", "#ffe9c4"))
        g = (t - R.t0) / max(gat, 1e-3)
        dd = (t - R.t1) / max(dis, 1e-3) if t >= R.t1 else -1.0
        rise = m.get("leave", "rise") == "rise"
        alpha, reveal, lift = 1.0, 99.0, 0.0
        if g < 1.0:
            reveal = 0.02 + 1.55 * _ssf(0.0, 1.0, g) ** 1.4
            alpha = _ssf(0.0, 0.35, g)
        if dd >= 0.0:
            if rise:
                reveal = 1.5 * (1.0 - _ssf(0.0, 0.62, dd)) ** 1.3
                alpha = 1.0 - _ssf(0.55, 0.70, dd)
            else:
                alpha = 1.0 - _ssf(0.0, 1.0, dd)
                lift = 0.07 * dd * dd
        alpha *= glow
        y += lift * h
        # screen placement, camera included: s = org + local * scale
        zz = 1.0 + aff[0]
        org = np.array([zz * x + aff[1], zz * y + aff[2]])
        scale = np.array([zz * h / asp, zz * h])
        hpx = max(zz * h * self.R.h, 8.0)                         # the figure's height in pixels
        px = 1.0 / hpx
        detail = _ssf(110.0, 380.0, hpx)
        lpos, lcol = self.light(m, t, P)
        self.lcol = lcol
        ll = np.array([(lpos[0] - org[0]) / scale[0], (lpos[1] - org[1]) / scale[1]])
        back = 1.0 - _ssf(0.35, 1.1, math.hypot(ll[0], ll[1] - 0.55))
        rimk = float(opt(m, "rim", 1.0)) * (0.75 + 0.25 * detail)
        wl = self._water(m, y, aff)
        mirror = None if wl is None else (np.array([wl]), 1.0 / 1.22)
        tint = float(opt(m, "day_tint", 1.0)) * 1.4
        if sr.is_hands:
            self._draw_hands(sr, t, org, scale, px, col, core, alpha, reveal, ll, back, rimk, tint, mirror, dd,
                             rise, to, hpx)
            return
        p, bodies = sr.bodies_at(t)
        heart0 = None
        for bi, (b, (J, F, lag)) in enumerate(zip(R.bodies, bodies)):
            child = R.preset == "child"
            hr = b.P["head_r"]
            segs, heart, head = person_segments(J, F, lag, veil=b.veil, full=True, wide=1.08 if child else 1.0,
                                                head_r=hr)
            if heart0 is None:
                heart0 = heart[0]
            n = segs.shape[1]
            rect = seg_rect(segs)
            breath = 1.0 + 0.07 * math.sin(TAU * t / 4.3 + b.phase * 3.0)
            self.add_bodies(
                segs, n, rect, org[None, :], scale[None, :],
                np.array([[col[0], col[1], col[2], alpha]]),
                np.array([[core[0], core[1], core[2], float(opt(m, "core_glow", 0.90)) * breath]]),
                np.array([[heart[0, 0], heart[0, 1], head[0, 0], head[0, 1]]]),
                np.array([[ll[0], ll[1], back, rimk]]),
                np.array([[0.0, 0.0, 0.0, reveal]]),
                np.array([[detail, tint, float(opt(m, "mist", 1.0)), float(opt(m, "head_glow", 0.70))]]),
                np.array([px]), np.array([(sr.seed + 0.31 * bi) % 1.0]), mirror)
            cl = sr.cloth[bi]
            if cl is not None and alpha > 0.003:
                self._draw_cloth(sr, bi, cl, t, org, scale, hpx, col, lcol, alpha, reveal, heart[0], ll, mirror)
            if alpha > 0.003 and reveal > 1.0:
                self._motes(sr, bi, J, F, t, org, scale, hpx, col, alpha, mirror)
        if dd >= 0.0 and rise and heart0 is not None:
            self._fly(sr, t, dd, org + heart0 * scale, to, hpx, col, glow)

    def _water(self, m, y, aff):
        """The line a figure is mirrored in: its feet when it stands on the lake, else the water line."""
        r = opt(m, "reflect", None)
        if r is None:
            r = not (getattr(S, "SCENES", None) or [])
        if r is False:
            return None
        zz = 1.0 + aff[0]
        hz = zz * S.HORIZON + aff[2]
        if r is not True:
            return zz * float(r) + aff[2]
        return min(zz * (y - 0.004) + aff[2], hz)

    def _draw_cloth(self, sr, bi, cl, t, org, scale, hpx, col, lcol, alpha, reveal, heart, ll, mirror):
        R = sr.rig
        b = R.bodies[bi]
        m = sr.m
        asp = S.ASPECT
        wdir = float(opt(m, "wind_dir", 1.0))

        def base_fn(tk):
            wv = opt(m, "wind", getattr(S, "WIND", 0.35))
            wv = float(wv(tk)) if callable(wv) else float(wv)
            xk = R.place(tk)[0]
            return wdir * gust(tk, xk, wv) * float(opt(m, "wind_gain", 0.9))

        def anchor_fn(tk):
            _, bodies = sr.bodies_at(tk)
            J, F, lag = bodies[bi]
            return cl.anchors(J, F, lag, b.P["head_r"])

        hn = R.place(t)[2]

        def origin_fn(tk):
            xk, yk, hk = R.place(tk)
            return (xk * asp / hn, yk / hn)

        X, Ls = cl.simulate(t, anchor_fn, origin_fn, base_fn)        # (C, K, 2) in the figure's frame
        out = []
        cool = _lin(opt(m, "cloth_color", "#fff1e0"))
        ccol = col * 0.62 + cool * 0.38
        cfar = ccol * 0.55 + self.mist_now * 0.45                 # the far side of a sheet is cooler
        lsgn = 1.0 if ll[0] >= heart[0] else -1.0

        def lit_col(P2):
            f = np.clip(0.5 + 0.5 * lsgn * (P2[..., 0] - heart[0]) / 0.11, 0.0, 1.0)[..., None]
            return (cfar * (1 - f) + ccol * f) * (0.78 + 0.44 * f)

        ca = float(opt(m, "cloth_glow", 1.0)) * alpha
        W_, H_ = self.R.w, self.R.h

        def reveal_k(P2):
            if reveal >= 9.0:
                return 1.0
            d = np.hypot(P2[..., 0] - heart[0], P2[..., 1] - heart[1])
            return 1.0 - ss(reveal - 0.24, reveal, d)

        for gr in cl.groups:
            c0, M, Kg = gr["c0"], gr["M"], gr["K"]
            Pg = X[c0:c0 + M, :Kg]
            if gr["name"] == "strand":
                f = 3
                Ps = catmull(Pg, f)                                  # (M, n, 2)
                n = Ps.shape[1]
                s = np.linspace(0, 1, n)[None, :]
                sd = gr["seed"]
                # a fine waviness, growing toward the free end
                tl = np.gradient(Ps, axis=1)
                tl /= np.maximum(np.linalg.norm(tl, axis=2, keepdims=True), 1e-6)
                wv = (np.sin(s * (7.0 + 6.0 * sd[:, :1]) + sd[:, 1:2] * 40.0 - t * (0.7 + 0.8 * sd[:, 2:3]))
                      + 0.5 * np.sin(s * (15.0 + 9.0 * sd[:, 1:2]) + sd[:, :1] * 70.0 + t * 1.3))
                Ps = Ps + np.stack([-tl[..., 1], tl[..., 0]], 2) * (0.011 * wv * s ** 1.3)[..., None]
                scr = org[None, None, :] + Ps * scale[None, None, :]
                pxy = scr * np.array([W_, H_])
                tg = np.gradient(pxy, axis=1)
                tg /= np.maximum(np.linalg.norm(tg, axis=2, keepdims=True), 1e-6)
                nr = np.stack([-tg[..., 1], tg[..., 0]], 2)
                wpx = (1.0 + 0.8 * (1 - s) * sd[:, 2:3]) * max(self.R.px, 0.5) * (0.75 + 0.25 * min(hpx / 400.0, 1.6))
                a = ca * gr["alpha"] * (0.25 + 0.75 * sd[:, 1:2] ** 1.5) * ss(0.0, 0.34, s) * (1 - s) ** 1.1
                a = a * reveal_k(Ps) * (0.70 + 0.30 * np.sin(s * 9.0 - t * 1.4 + sd[:, :1] * 40.0))
                off = nr * wpx[..., None] / np.array([W_, H_])
                va = np.concatenate([scr - off, np.broadcast_to(-1.0, (M, n, 1)), np.broadcast_to(s[..., None], (M, n, 1)),
                                     a[..., None], np.ones((M, n, 1)), np.zeros((M, n, 1)), np.ones((M, n, 1))], 2)
                vb = np.concatenate([scr + off, np.broadcast_to(1.0, (M, n, 1)), np.broadcast_to(s[..., None], (M, n, 1)),
                                     a[..., None], np.ones((M, n, 1)), np.zeros((M, n, 1)), np.ones((M, n, 1))], 2)
                grid = np.stack([va, vb], 2).reshape(M, n * 2, 8)   # per strand: rows of (left, right)
                idx = grid_tris(n, 2)
                tri = grid[:, idx, :].reshape(-1, 8)
                c3 = np.broadcast_to((ccol * 0.5 + lcol * 0.5)[None, :], (len(tri), 3))
                out.append(np.concatenate([tri, c3], 1))
            else:
                Pu = catmull(Pg, 3)                                  # along each chain
                Pu = np.swapaxes(catmull(np.swapaxes(Pu, 0, 1), 2), 0, 1)   # and across the sheet
                Mu, n = Pu.shape[0], Pu.shape[1]
                u = np.linspace(0, 1, Mu)[:, None]
                v = np.linspace(0, 1, n)[None, :]
                # folds: where neighbours crowd together the cloth is denser and brighter
                dx = np.linalg.norm(np.gradient(Pu, axis=0), axis=2)
                ref = np.maximum(np.median(dx[:, :2]), 1e-5) * (1.0 + 0.55 * v)
                fold = np.clip(ref / np.maximum(dx, 1e-5), 0.55, 2.6) ** 0.7
                a = ca * gr["alpha"] * reveal_k(Pu) * ss(0.0, 0.05, v)
                if gr["name"] == "hem":      # the lower robe fades out before the ground: no hard feet
                    a = a * ss(0.0, 0.45, v) * (1.0 - ss(0.55, 1.0, v))
                elif gr["name"] != "veil":   # a sleeve ends in a soft fade
                    a = a * (1.0 - 0.85 * ss(0.50, 1.0, v))
                a = np.broadcast_to(a, (Mu, n))
                scr = org[None, None, :] + Pu * scale[None, None, :]
                lines = gr["lines"] * (0.6 + 0.4 * min(hpx / 420.0, 1.6))
                vert = np.concatenate([scr, np.broadcast_to(u[..., None], (Mu, n, 1)),
                                       np.broadcast_to(v[..., None], (Mu, n, 1)), a[..., None], fold[..., None],
                                       np.full((Mu, n, 1), lines),
                                       np.full((Mu, n, 1), dict(hem=2.0, veil=0.0).get(gr["name"], 3.0))],
                                      2).reshape(Mu * n, 8)
                vert = np.concatenate([vert, lit_col(Pu).reshape(Mu * n, 3)], 1)
                out.append(vert[grid_tris(Mu, n)])
        self.add_cloth(np.vstack(out), mirror)

    def _motes(self, sr, bi, J, F, t, org, scale, hpx, col, alpha, mirror):
        """A few bright motes lift off the shoulders, the hands and the head and drift up."""
        sd = sr.mote
        n = len(sd)
        if n == 0:
            return
        R = sr.rig
        arms = J["arms"]
        src = np.concatenate([arms[1.0][0], arms[-1.0][0], arms[1.0][2], arms[-1.0][2],
                              J["head"] + np.array([0.0, 0.05, 0.0])], 0)
        src2 = F.pt(src)
        per = 2.8 + 2.4 * sd[:, 0]
        u = (t / per + sd[:, 1] + 0.37 * bi) % 1.0
        em = src2[(sd[:, 2] * 5).astype(int) % 5]
        # a mote stays where it was let go while the figure walks on
        tb = t - u * per
        x_now, _, hn = R.place(t)
        xb = np.array([R.place(float(v))[0] for v in tb]) if abs(R.vel(t)[1]) > 1e-4 else np.full(n, x_now)
        lx = em[:, 0] + (xb - x_now) * S.ASPECT / hn + (sd[:, 3] - 0.5) * 0.05 \
            + 0.035 * np.sin(u * 6.0 + sd[:, 4] * 30.0) * u + 0.10 * u * (sd[:, 5] - 0.3)
        ly = em[:, 1] + (0.07 + 0.30 * sd[:, 4]) * u ** 1.3 + (sd[:, 5] - 0.5) * 0.03
        a = np.sin(math.pi * u) ** 0.8 * (0.55 + 0.45 * np.sin(t * (2.0 + 3.0 * sd[:, 3]) + sd[:, 0] * 50.0))
        a = a * alpha * float(opt(sr.m, "mote_glow", 1.0))
        sx, sy = org[0] + lx * scale[0], org[1] + ly * scale[1]
        k = math.sqrt(min(max(hpx / 390.0, 0.25), 1.6))
        size = (3.0 + 5.0 * sd[:, 2] ** 2) * k
        warm = _lin("#fff0d0") * 0.6 + col * 0.4
        rows = [np.column_stack([sx, sy, size, np.full(n, 3.4), warm[None, :] * (a * 1.5)[:, None]]),
                np.column_stack([sx, sy, size * 4.5, np.full(n, 2.6), warm[None, :] * (a * 0.10)[:, None]])]
        self.add_points(np.vstack(rows), mirror)

    def _fly(self, sr, t, dd, start, to, hpx, col, glow):
        """Dissolve: the body's light gathers into one small light that rises to its place in the arch."""
        k = math.sqrt(min(max(hpx / 390.0, 0.3), 1.6))
        a_in = _ssf(0.0, 0.30, dd)
        u = _ssf(0.30, 1.0, dd)
        a = np.asarray(start, float)
        b = np.asarray(to, float)
        d = math.hypot((b[0] - a[0]) * S.ASPECT, b[1] - a[1])
        side = (sr.seed - 0.5) * 0.10

        def at(uu):
            e = uu * uu * (3 - 2 * uu)
            return (a[0] + (b[0] - a[0]) * e + side * math.sin(math.pi * uu),
                    a[1] + (b[1] - a[1]) * e + 0.14 * d * math.sin(math.pi * uu))

        warm = _lin("#fff3da") * 0.7 + col * 0.3
        out_k = glow * a_in * (1.0 - _ssf(0.93, 1.0, dd))
        px_, py_ = at(u)
        rows = [np.array([[px_, py_, 9.0 * k, 2.4, *(warm * 2.2 * out_k)]]),
                np.array([[px_, py_, 34.0 * k, 3.0, *(warm * 0.55 * out_k)]]),
                np.array([[px_, py_, 120.0 * k, 2.8, *(warm * 0.10 * out_k)]])]
        n = 22
        us = np.clip(u - np.arange(1, n + 1) * 0.016, 0.0, 1.0)
        tr = np.array([at(float(q)) for q in us])
        fade = (1 - np.arange(n) / n) ** 1.6 * out_k * (us > 0)
        rows.append(np.column_stack([tr[:, 0], tr[:, 1], np.full(n, 7.0) * k, np.full(n, 3.0),
                                     warm[None, :] * (fade * 0.6)[:, None]]))
        sd = sr.mote
        if len(sd):
            ph = (t * 0.9 + sd[:, 0]) % 1.0
            uu = np.clip(u - ph * 0.30, 0.0, 1.0)
            sp = np.array([at(float(q)) for q in uu])
            jx = (sd[:, 1] - 0.5) * 0.030 * ph
            jy = (sd[:, 2] - 0.5) * 0.045 * ph
            am = out_k * (1 - ph) * (uu > 0) * 0.9
            rows.append(np.column_stack([sp[:, 0] + jx, sp[:, 1] + jy, (2.5 + 3.0 * sd[:, 3]) * k,
                                         np.full(len(sd), 3.2), warm[None, :] * am[:, None]]))
        self.add_points(np.vstack(rows), None)

    def _draw_hands(self, sr, t, org, scale, px, col, core, alpha, reveal, ll, back, rimk, tint, mirror, dd, rise,
                    to, hpx):
        m = sr.m
        p, Js = sr.skeleton(t)
        J = Js[0]
        segs = hands_segments(J)
        if sr.rig.face < 0:
            segs[..., 0] *= -1.0
            segs[..., 2] *= -1.0
        n = segs.shape[1]
        rect = seg_rect(segs, pad=0.04)
        orb = np.array(J["orb"], dtype=np.float64)
        orb_r, light = float(J["orb_r"]), float(J["light"])
        mid = 0.5 * (np.asarray(J[1.0]["palm"]) + np.asarray(J[-1.0]["palm"]))
        heart = orb if light > 0.3 else mid
        self.add_bodies(
            segs, n, rect, org[None, :], scale[None, :],
            np.array([[col[0], col[1], col[2], alpha]]),
            np.array([[core[0], core[1], core[2], 0.25]]),
            np.array([[mid[0], mid[1] + 0.05, mid[0], -5.0]]),
            np.array([[ll[0], ll[1], back, rimk]]),
            np.array([[orb[0], orb[1], 1.6 * light, reveal]]),
            np.array([[1.0, tint, 0.0, 0.0]]),
            np.array([px]), np.array([sr.seed]), mirror)
        if light > 0.01 and alpha > 0.003:
            k = hpx / 430.0
            c = _lin(opt(m, "flame", "#ffe2a0"))
            w = _lin("#fff6e4")
            s = org + orb * scale
            br = alpha * light * (1.0 + 0.06 * math.sin(t * 2.3))
            rr = max(orb_r, 0.02) * hpx
            rows = [[s[0], s[1], rr * 0.9, 2.6, *(w * 1.8 * br)], [s[0], s[1], rr * 2.6, 3.0, *(c * 0.75 * br)],
                    [s[0], s[1], rr * 7.0, 2.8, *(c * 0.14 * br)]]
            self.add_points(np.array(rows), None)
        if dd >= 0.0 and rise:
            self._fly(sr, t, dd, org + heart * scale, to, hpx, col, float(m.get("glow", 1.0)))

    # ------------------------------------------------------------ the crowd
    def draw_crowd(self, c, t, aff):
        """Queues the gathering's people as bodies of light. Returns the flame sprites (drawn by the crowd)."""
        m = c.m
        N = c.N
        J = c.skeleton(t)
        a_in = ss(0.0, 0.8, t - c.Te) * (t >= c.Te)
        fdis = ss(0.0, c.dis, t - c.leave)
        alive = a_in * (1 - fdis)
        lit = J["lit"] if c.has_pass else np.ones(N)
        sgn = c.fw
        F = Frame2D(J["cy"], J["sy"], sgn, np.zeros(N))
        Jc = dict(hip=J["hip"], chest=J["chest"], neck=J["neck"], head=J["head"], legs=J["legs"], arms=J["arms"])
        small = c.h < 0.80 * np.median(c.h)                       # the children
        veiled = (c.off[:, 3] < float(opt(m, "veiled", 0.55))) & ~small
        segs, heart, head = person_segments(Jc, F, J["lag"], veil=veiled * 1.0, full=False,
                                            wide=0.92 + 0.22 * c.off[:, 2], head_r=np.where(small, 0.064, 0.056))
        n = segs.shape[1]
        rect = seg_rect(segs, pad=0.02)
        asp = S.ASPECT
        zz = 1.0 + aff[0]
        y = c.fy + (0.06 * fdis * fdis) * c.h
        org = np.stack([zz * J["x"] + aff[1], zz * y + aff[2]], 1)
        scale = np.stack([zz * c.h / asp, zz * c.h], 1)
        hpx = np.maximum(zz * c.h * self.R.h, 8.0)
        px = 1.0 / hpx
        P = self.P
        lpos, lcol = self.light(m, t, P)
        self.lcol = lcol
        ll = np.stack([(lpos[0] - org[:, 0]) / scale[:, 0], (lpos[1] - org[:, 1]) / scale[:, 1]], 1)
        back = 1.0 - ss(0.35, 1.1, np.hypot(ll[:, 0], ll[:, 1] - 0.55))
        glow = float(m.get("glow", 1.0))
        # those who wait are cooler and dimmer; the flame warms each one it reaches
        cool = _lin(opt(m, "unlit", "#9fb4ff"))
        dim = float(opt(m, "unlit_glow", 0.55)) if c.has_pass else 1.0
        col = c.col * lit[:, None] + (c.col * 0.45 + cool * 0.55) * (1 - lit)[:, None]
        al = alive * c.bright * glow * (dim + (1.15 - dim) * lit) * (1.0 + 0.5 * self.day * lit)
        core = _lin(opt(m, "core", "#fff3dc"))
        coreg = float(opt(m, "core_glow", 0.90)) * (0.20 + 0.80 * lit)
        fxp = np.zeros((N, 4))
        fxp[:, 3] = 99.0
        flames = []
        if c.has_pass:
            fx_, fy_, rx_, ry_ = c.hands_screen(J)
            held = (t >= c.Tr) & (alive > 0.01)
            risen = ss(0.0, 0.6, t - c.Trise)
            fxp[:, 0] = (fx_ - J["x"]) * asp / c.h
            fxp[:, 1] = (fy_ - c.fy) / c.h
            fxp[:, 2] = held * ss(0.0, 0.5, t - c.Tr) * (1 - 0.6 * risen) * float(opt(m, "flame_light", 1.0))
            flames = c._flames(t, J, alive)
            cand = fxp[:, 2] * alive * (1 - 0.25 * c.r)
        rimk = float(opt(m, "rim", 1.0)) * (0.45 + 0.55 * lit) * (0.30 + 0.70 * ss(110.0, 380.0, hpx))
        tint = float(opt(m, "day_tint", 1.0)) * 1.8
        wl = None
        r = opt(m, "reflect", None)
        if r is None:
            r = not (getattr(S, "SCENES", None) or [])
        if r:
            hz = zz * S.HORIZON + aff[2]
            wl = np.minimum(zz * (c.fy - 0.003) + aff[2], hz)
        mir = None if wl is None else 1.0 / 1.22
        if c.has_pass and (cand > 0.01).any():
            # each held light: a small bright point at the chest, like a candle (it rises when they lift it)
            i = np.nonzero(cand > 0.01)[0]
            sc = np.sqrt(hpx[i] / 140.0)
            sx, sy = zz * fx_[i] + aff[1], zz * fy_[i] + aff[2]
            fcol = _lin(opt(m, "flame", "#ffd08a"))
            fk = 0.85 + 0.15 * np.sin(t * 11.0 + c.ph[i] * 40.0) * np.sin(t * 6.3 + c.ph[i] * 17.0)
            rows = [np.column_stack([sx, sy, 8.0 * sc, np.full(len(i), 2.2),
                                     _lin("#fff8ea")[None, :] * (2.6 * cand[i] * fk)[:, None]]),
                    np.column_stack([sx, sy, 26.0 * sc, np.full(len(i), 3.0),
                                     fcol[None, :] * (0.90 * cand[i] * fk)[:, None]]),
                    np.column_stack([sx, sy, 76.0 * sc, np.full(len(i), 2.8),
                                     fcol[None, :] * (0.15 * cand[i] * fk)[:, None]])]
            self.add_points(np.vstack(rows), None if wl is None else (np.tile(wl[i], 3), mir))
        keep = al > 0.004
        if keep.any():
            k = np.nonzero(keep)[0][:ROWS // 2 - 16]
            self.add_bodies(
                segs[k], n, rect[k], org[k], scale[k],
                np.column_stack([col[k], al[k]]),
                np.column_stack([np.tile(core, (len(k), 1)), coreg[k]]),
                np.column_stack([heart[k], head[k]]),
                np.column_stack([ll[k], back[k], rimk[k]]),
                fxp[k],
                np.column_stack([ss(110.0, 380.0, hpx[k]), np.full(len(k), tint),
                                 np.full(len(k), float(opt(m, "mist", 0.30))),
                                 np.full(len(k), float(opt(m, "head_glow", 1.25)))]),
                px[k], c.ph[k], None if wl is None else (wl[k], 1.0 / 1.22))
        return np.vstack(flames).astype("f4") if flames else np.zeros((0, 7), "f4")

    # ------------------------------------------------------------ the frame
    def begin(self, t, P):
        """Called by render.py before the figures are drawn."""
        if not self.on:
            return
        self._reset()
        self.P = P
        self.lcol = _lin("#fff6e6")
        # how bright the sky is (0 night, about 0.4 dawn, 1 the bright day): light adds little on a bright sky,
        # so there the bodies glow less and carry the composite's cool tint instead
        lum = [float(np.dot(np.asarray(P[k_], dtype=np.float64), [0.2126, 0.7152, 0.0722]))
               for k_ in ("sky_hor", "sky_mid", "sky_top")]
        d = opt(None, "daylight", None)
        self.day = _ssf(0.08, 0.50, 0.25 * lum[0] + 0.35 * lum[1] + 0.40 * lum[2]) if d is None else _f(d, t)
        self.mist_now = self._mist(P)

    def _run(self, fbo, inst, cloth, pts, t, pxk):
        ctx = self.ctx
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 0.0)
        if inst:
            data = np.vstack(inst)[:ROWS]
            self.b_inst.write(data.tobytes())
            self.t_seg.use(location=0)
            p = self.p_body
            p["uSeg"].value = 0
            for k_, v_ in (("uT", float(t)), ("uSoft", float(opt(None, "soft", 1.4))),
                           ("uDens", float(opt(None, "density", 1.35))), ("uGain", float(opt(None, "body_glow", 0.36))),
                           ("uDay", float(self.day))):
                if k_ in p:
                    p[k_].value = v_
            for k_, v_ in (("uMist", self.mist), ("uLightCol", self.lcol * float(opt(None, "rim_glow", 0.8))),
                           ("uFlameCol", self.flame)):
                if k_ in p:
                    p[k_].value = tuple(float(x) for x in v_)
            self.gl["body"].render(moderngl.TRIANGLE_STRIP, vertices=4, instances=len(data))
        if cloth:
            data = np.vstack(cloth)
            if len(data) > self.cap_c:
                self.cap_c = int(len(data) * 1.3) + 256
                self.b_cloth = ctx.buffer(reserve=self.cap_c * 11 * 4, dynamic=True)
                self.gl["cloth"] = ctx.vertex_array(self.p_cloth, [(self.b_cloth, "2f 2f 4f 3f", "aPos", "aUV", "aK",
                                                                    "aCol")], skip_errors=True)
            self.b_cloth.write(data.tobytes())
            if "uT" in self.p_cloth:
                self.p_cloth["uT"].value = float(t)
            if "uDay" in self.p_cloth:
                self.p_cloth["uDay"].value = float(self.day)
            self.gl["cloth"].render(moderngl.TRIANGLES, vertices=len(data))
        if pts:
            data = np.vstack(pts)
            if len(data) > self.cap_p:
                self.cap_p = int(len(data) * 1.3) + 64
                self.b_pt = ctx.buffer(reserve=self.cap_p * 7 * 4, dynamic=True)
                self.gl["pt"] = ctx.vertex_array(self.p_pt, [(self.b_pt, "2f 2f 3f", "aPos", "aSz", "aCol")],
                                                 skip_errors=True)
            self.b_pt.write(data.tobytes())
            self.p_pt["uPx"].value = float(self.R.px * pxk)
            self.gl["pt"].render(moderngl.POINTS, vertices=len(data))

    def _mist(self, P):
        """The colour of the mist and of the far side: violet under a night sky, pale and neutral in the day."""
        mist = opt(None, "mist_color", None)
        if mist is not None:
            return _lin(mist)
        sky_mid = np.asarray(P["sky_mid"], dtype=np.float64)
        return (_lin("#b9a8ff") * 0.42 + sky_mid * 0.8 + 0.02) * (1 - self.day) + _lin("#e6e2f4") * 0.62 * self.day

    def resolve(self, t, P):
        """Called by render.py after the figures and the crowd: draws everything queued into the figure layer,
        then adds the layer and its mirror image in the lake to the light."""
        if not self.on or not self.used:
            self.used = False
            return
        ctx, R = self.ctx, self.R
        self.mist = self.mist_now
        self.flame = _lin(opt(None, "flame", "#ffd08a"))
        # the cones of every body, one row each
        rows = self.q_seg[:ROWS]
        seg = np.zeros((ROWS, MAXSEG * 3, 4), np.float32)
        for i, s in enumerate(rows):
            n = min(len(s), MAXSEG)
            seg[i, :n * 3] = s[:n].reshape(n * 3, 4)
        nr = max(len(rows), 1)
        self.t_seg.write(seg[:nr].tobytes(), viewport=(0, 0, MAXSEG * 3, nr))
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        has_m = bool(self.q_inst_m or self.q_cloth_m or self.q_pt_m)
        if has_m:
            self._run(self.f_ref, self.q_inst_m, self.q_cloth_m, self.q_pt_m, t, 0.5)
        self._run(self.f_fig, self.q_inst, self.q_cloth, self.q_pt, t, 1.0)
        R.f_L.use()
        p = self.p_res
        sky = getattr(R, "sky", None)
        wl = float(S.HORIZON)
        if sky is not None:
            try:
                wl = float(sky.place((0.5, S.HORIZON), sky.ground_depth(S.HORIZON))[1])
            except Exception:
                pass
        calm = getattr(S, "BOTTOM_CALM", 0.0)
        calm = float(calm(t)) if callable(calm) else float(calm or 0.0)
        for k_, v_ in (("uT", float(t)), ("uAspect", float(S.ASPECT)), ("uWL", wl),
                       ("uRefl", float(opt(None, "reflect_glow", 0.62))), ("uCalm", calm), ("uCalmY", 0.335),
                       ("uKnee", float(opt(None, "knee", 1.8))), ("uShare", float(opt(None, "bloom", 0.45)))):
            if k_ in p:
                p[k_].value = v_
        p["uFig"].value = 0
        if has_m:
            self.t_ref.use(location=0)
            p["uMode"].value = 1
            self.gl["res"].render(moderngl.TRIANGLE_STRIP)
        self.t_fig.use(location=0)
        p["uMode"].value = 0
        self.gl["res"].render(moderngl.TRIANGLE_STRIP)
        self.drawn = True

    def comp_uniforms(self, prog, t, P):
        """The composite's tint: on a bright sky the bodies get a faint cool tint of the same brightness."""
        if "uFigK" not in prog:
            return
        if not self.on or not self.used:
            prog["uFigK"].value = -1.0
            return
        self.t_fig.use(location=FIG_UNIT)
        prog["uFigT"].value = FIG_UNIT
        prog["uFigK"].value = float(opt(None, "day_tint_strength", 0.92))
        lvl = float(opt(None, "day_tint_level", 0.78))
        for key, name, default in (("uFigTint", "day_tint_color", "#b8b4ff"), ("uFigTintB", "day_tint_warm", "#ffd9b4")):
            c = _lin(opt(None, name, default))
            c = c / max(float(np.dot(c, [0.2126, 0.7152, 0.0722])), 1e-6) * lvl
            if key in prog:
                prog[key].value = tuple(float(x) for x in c)
        if "uFigGate" in prog:
            g = opt(None, "day_tint_gate", (0.10, 0.42))
            prog["uFigGate"].value = (float(g[0]), float(g[1]), float(opt(None, "knee", 1.8)),
                                      1.0 - float(opt(None, "bloom", 0.45)))
