"""Text animations (UPGRADE-HOWTO section H2): other ways for the words to appear than the classic sparks.

A PHRASES entry, the closing TITLE, the TAGLINE (end card lines) and a FRAGMENTS entry may set anim= (or ANIM=):

  "sparks" (default)  the classic: sparks gather into the words, hold, fly to the star
  "ink"               light flows along each letter's strokes, as if written, with a hot wet nib
  "bloom"             each letter opens from a seed of light at its centre, staggered left to right
  "rise"              the letters float up out of the water, with their rippling reflection
  "ribbon"            a twisting ribbon of light sweeps across and leaves the words behind it
  "constellation"     stars appear on the letters, lines join them, then the letters fill with light
  "petal" / "snow"    falling petals (or flakes) settle into the letters
  "wave"              the classic gathering, then ripples of brightness run through the held words

A song may set TEXT_ANIM = "ink" (for example) as the default for every expression and the title.

Every animation keeps the timing contract of the classic sparks: a letter at a given place is fully formed at the
same moment as before (so `form`, `hold` and the 6 second reading time are unchanged, and the veil behind the words
stays in step), and at `hold` the words dissolve and their sparks fly to the star exactly as before. Songs that set
no anim never reach this module's drawing code, so they render pixel for pixel as before.
"""
import numpy as np
import moderngl

import song as S
from shaders import NOISE, QUAD_VS

ANIMS = {"sparks": 0, "ink": 1, "bloom": 2, "rise": 3, "ribbon": 4, "constellation": 5, "petal": 6, "snow": 7,
         "wave": 8}
TAU = 1.35
CALM_Y = 0.335


def anim_of(meta, default=None):
    """The animation an entry asks for (0 = the classic sparks). Unknown names stop the render with a clear error."""
    name = meta.get("anim", meta.get("ANIM", default)) if isinstance(meta, dict) else default
    if name is None:
        return 0
    if name not in ANIMS:
        raise ValueError(f"unknown text anim {name!r} (use one of {', '.join(ANIMS)})")
    return ANIMS[name]


# ------------------------------------------------------------------ GLSL
COMMON = """
uniform float uFormT, uFormDur, uFlyT, uT, uLine, uCalm, uCalmY;
uniform vec2 uBounds, uYB;
const float TAU = 1.35;
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
float odx(float x){ return clamp((x-uBounds.x)/(uBounds.y-uBounds.x), 0.0, 1.0); }
float arriveAt(float od){ return od*(uFormDur-TAU)+TAU; }
// the ribbon's centre line at line order u (0 left edge of the words, 1 right edge) and time tt
float ribbonY(float u, float tt){
  float yc = 0.5*(uYB.x+uYB.y), amp = 0.30*(uYB.y-uYB.x)+0.012;
  return yc + amp*sin(u*9.0-tt*1.3) + 0.25*amp*sin(u*23.0+tt*0.7);
}
// rise: how far below its place the column at line order od still is
float riseDrop(float od){
  float e0 = clamp((uFormT-(arriveAt(od)-1.75))/2.15, 0.0, 1.0);
  float e = e0*e0*(3.0-2.0*e0);
  return (1.0-e)*max(uYB.y-uLine+0.012, 0.0);
}
float riseIn(float od){ return clamp((uFormT-(arriveAt(od)-1.75))/2.15, 0.0, 1.0); }
// wave: a ripple of brightness that runs through the held words every few seconds
float waveBand(float od, float y){
  float hw = uFormT-uFormDur-0.5;
  if(hw<0.0 || uFlyT>0.0) return 0.0;
  float wp = fract(hw/3.6)*1.7-0.35;
  float yy = (y-uYB.x)/max(uYB.y-uYB.x, 0.01);
  return exp(-pow((od-wp-0.08*(yy-0.5))/0.075, 2.0))*smoothstep(0.0, 0.8, hw);
}
"""

TEXT_FS = "#version 330\n" + NOISE + COMMON + """
in vec2 vUV; out vec4 o;
uniform sampler2D uTex, uAux;   // aux: r stroke order in the letter, g distance from the letter's centre, ba centre
uniform int uAnim;
uniform float uAspect, uAlpha, uPulse;
uniform vec3 uCol, uGlowCol, uHot;
void main(){
  vec2 uv = vUV;
  float od = odx(uv.x);
  float a = arriveAt(od);
  float er = vnoise(uv*vec2(uAspect,1.0)*70.0);
  float dis = 1.0-smoothstep(0.0, 1.0, (uFlyT-er*0.9)/0.8);
  float held = smoothstep(uFormDur+0.6, uFormDur+1.6, uFormT)*(uFlyT>0.0 ? 0.0 : 1.0);
  vec2 suv = uv;
  float drop = 0.0, band = 0.0;
  if(uAnim==3){ drop = riseDrop(od); suv.y += drop; }
  if(uAnim==8){ band = waveBand(od, uv.y); suv.y -= 0.0022*band; }
  vec3 tx = texture(uTex, suv).rgb;
  vec4 ax = texture(uAux, suv);
  float rev = smoothstep(-0.25, 0.75, uFormT-a);
  float gain = 1.0, ggain = 1.0;
  vec3 add = vec3(0.0);
  if(uAnim==1){
    // ink: each letter is written along its strokes; a hot nib leads, the fresh ink cools
    float co = odx(ax.b);
    float ti = co*(uFormDur-TAU)+TAU-0.75+ax.r*0.95;
    float dt = uFormT-ti;
    rev = smoothstep(-0.04, 0.05, dt);
    float nib = exp(-dt*dt/0.006);
    float wet = exp(-max(dt,0.0)*2.6)*rev;
    add = uHot*(tx.r*1.4+tx.g*0.9)*nib + uHot*tx.r*0.45*wet;
    // while held, light keeps flowing slowly along the strokes
    float fl = fract(ax.r*0.8-uT*0.30+co*1.9);
    add += uHot*tx.r*0.28*exp(-pow((fl-0.5)/0.07, 2.0))*held;
  } else if(uAnim==2){
    // bloom: a seed of light at the letter's centre, then the letter opens outward from it
    float co = odx(ax.b);
    float op = co*(uFormDur-TAU)+TAU-0.55;
    float k = (uFormT-op)/0.85;
    float d = ax.g;
    rev = smoothstep(d-0.20, d+0.02, k*1.25);
    float seed = exp(-d*d*30.0)*smoothstep(-1.0, -0.35, uFormT-op)*(1.0-smoothstep(0.25, 1.0, k));
    float rim = exp(-pow((k*1.25-d)/0.09, 2.0))*step(0.0, k)*(1.0-smoothstep(1.0, 1.4, k*1.25-d+1.0));
    add = uHot*seed*1.3 + uHot*(tx.r*1.0+tx.g*0.6)*rim;
  } else if(uAnim==3){
    // rise: the letters come up through the water line; their reflection ripples below it, then fades
    float e0 = riseIn(od);
    float above = smoothstep(uLine-0.002, uLine+0.010, uv.y);
    rev = above*smoothstep(0.0, 0.22, e0);
    add = uHot*tx.r*0.35*exp(-pow((uv.y-uLine)/0.008, 2.0))*above*step(0.001, drop);
    if(uv.y<uLine){
      float dd = uLine-uv.y;
      float wob = (vnoise(vec2(uv.x*uAspect*26.0, uv.y*190.0-uT*1.1))-0.5)*0.010*(0.3+dd*6.0)
                + sin(uv.y*260.0+uT*2.4)*0.0016;
      vec3 rt = texture(uTex, vec2(uv.x+wob, 2.0*uLine-uv.y+drop)).rgb;
      float ra = smoothstep(0.0, 0.25, e0)*(1.0-smoothstep(0.55, 1.0, e0))*exp(-dd*14.0)*calmK(uv.y);
      add += (uCol*rt.r*0.50 + uGlowCol*rt.g*0.45)*ra*0.8;
    }
  } else if(uAnim==4){
    // ribbon: a twisting band of light sweeps left to right; the words appear where it has passed
    float span = uBounds.y-uBounds.x;
    float f = (uFormT-TAU)/(uFormDur-TAU);
    float u = (uv.x-uBounds.x)/span;
    rev = smoothstep(u-0.01, u+0.05, f);
    add = uHot*(tx.r*0.9+tx.g*0.7)*exp(-pow((f-u-0.02)/0.035, 2.0));
    float ry = ribbonY(u, uT);
    float hw = 0.0040+0.0095*abs(cos(u*4.6-uT*0.9));
    float dy = abs(uv.y-ry);
    float core = exp(-pow(dy/hw, 2.0)*1.3), halo = exp(-dy/(hw*3.5));
    float behind = f-u;
    float env = behind>0.0 ? exp(-behind/0.24) : exp(behind/0.012);
    env *= smoothstep(-0.14, -0.02, u)*(1.0-smoothstep(1.02, 1.16, u));
    float life = 1.0-smoothstep(1.05, 1.40, f);
    float edge = 0.75+0.25*sin(u*40.0-uT*3.0);
    add += uHot*(core*0.85*edge+halo*0.22)*env*life*calmK(uv.y);
  } else if(uAnim==5){
    // constellation: the letters fill with light after their stars and lines (drawn separately)
    rev = smoothstep(-0.10, 0.65, uFormT-a);
    add = uHot*tx.r*0.10*held*(0.5+0.5*sin(uT*2.2+ax.b*60.0));
  } else if(uAnim==6 || uAnim==7){
    // petals or flakes settle into the letters: they fill in specks, not as a sweep
    float n = vnoise(uv*vec2(uAspect,1.0)*150.0);
    rev = smoothstep(n*0.7-0.35, n*0.7+0.25, uFormT-a);
  } else if(uAnim==8){
    gain = 1.0+0.55*band; ggain = 1.0+1.6*band;
    add = uHot*tx.r*0.25*band;
  }
  vec3 c = uCol*tx.r*0.92*gain + uGlowCol*tx.g*(0.15+0.06*uPulse)*ggain;
  o = vec4((c*rev + add)*dis*uAlpha, 1.0);
}
"""

PART_VS = "#version 330\n" + COMMON + """
in vec3 aTarget; in vec4 aSeed;
uniform sampler2D uAux;
uniform int uAnim, uNode, uDrift;
uniform float uFlyDur, uPx, uPulse;
uniform vec2 uStar;
out float vA; out float vK; out float vRot; out float vFlip; out float vShape;
void main(){
  vec2 tg = aTarget.xy;
  float odt = odx(tg.x);
  float od = clamp(aTarget.z*0.84 + aSeed.x*0.16, 0.0, 1.0);
  float dep = od*(uFormDur-TAU);
  float tw = 0.70+0.30*sin(uT*(2.0+3.0*aSeed.y)+aSeed.z*50.0);
  vec2 pos = tg; float alpha = 0.0; float size = 2.4+4.6*aSeed.w*aSeed.w*aSeed.w;
  vShape = 0.0; vRot = 0.0; vFlip = 1.0;
  vec2 hj = 0.0008*vec2(sin(uT*1.3+aSeed.x*40.0), cos(uT*1.1+aSeed.y*40.0));
  if(uNode==1){
    // a star of the constellation: it appears with a flash, then twinkles softly
    float ta = arriveAt(odt)-1.30+0.25*aSeed.x;
    float s = uFormT-ta;
    float on = smoothstep(0.0, 0.25, s);
    float flash = exp(-max(s,0.0)*2.2)*on;
    float fade = mix(1.0, 0.45, smoothstep(1.6, 3.2, s));
    alpha = on*(0.55*fade+0.9*flash)*(0.65+0.35*sin(uT*(2.5+2.0*aSeed.y)+aSeed.z*40.0));
    size = 6.0+5.0*aSeed.w+6.0*flash;
    vShape = 3.0;
  } else if(uAnim==1){
    // ink: sparks spring from the nib as it passes, a few drip down and fade
    vec4 ax = texture(uAux, tg);
    float ti = odx(ax.b)*(uFormDur-TAU)+TAU-0.75+ax.r*0.95;
    float dt = uFormT-ti;
    float on = step(0.0, dt);
    float sp = exp(-max(dt,0.0)*3.0)*on;
    alpha = on*(0.085+0.95*sp);
    alpha *= mix(1.0, tw*(1.0+0.5*uPulse), 1.0-sp);
    if(aSeed.w>0.88){ pos.y -= 0.030*(1.0-exp(-max(dt,0.0)*1.1)); alpha *= exp(-max(dt,0.0)*0.6); }
    pos += hj*on;
    size += 2.5*sp;
  } else if(uAnim==2){
    // bloom: a few sparks gather as the seed, then all burst outward into the letter
    vec4 ax = texture(uAux, tg);
    vec2 c = ax.ba;
    float op = odx(c.x)*(uFormDur-TAU)+TAU-0.55;
    float k = (uFormT-op)/0.85;
    float s = clamp(k*1.25-ax.g*0.6, 0.0, 1.0);
    float e = 1.0-pow(1.0-s, 3.0);
    vec2 jit = 0.0035*aSeed.w*vec2(sin(uT*3.0+aSeed.x*40.0), cos(uT*2.6+aSeed.y*40.0));
    pos = mix(c+jit, tg, e);
    float pre = smoothstep(-1.0, -0.35, uFormT-op)*(aSeed.y<0.10 ? 0.45 : 0.0);
    float since = (k*1.25-ax.g*0.6-1.0)*0.85;
    float landed = step(0.0, since);
    float sparkle = exp(-max(since,0.0)*2.4)*landed;
    alpha = s>0.0 ? (0.25+0.75*s)*mix(1.0, 0.085, smoothstep(0.0, 1.3, since))+sparkle : pre;
    alpha *= mix(1.0, tw*(1.0+0.5*uPulse), landed);
    pos += hj*landed;
    size += 3.0*sparkle+1.5*(1.0-s)*step(0.0, k);
  } else if(uAnim==3){
    // rise: the sparks ride up with the letters and glint as they settle
    float drop = riseDrop(odt);
    pos = tg-vec2(0.0, drop);
    float e0 = riseIn(odt);
    float since = uFormT-(arriveAt(odt)+0.40);
    float landed = step(0.0, since);
    float sparkle = exp(-max(since,0.0)*2.4)*landed;
    alpha = smoothstep(0.0, 0.2, e0)*(landed>0.5 ? 0.085+sparkle : 0.22);
    alpha *= smoothstep(uLine-0.002, uLine+0.010, pos.y);
    alpha *= mix(1.0, tw*(1.0+0.5*uPulse), landed);
    pos += hj*landed;
    size += 2.5*sparkle;
  } else if(uAnim==4){
    // ribbon: sparks shed from the ribbon as it passes and settle into the letters
    float span = uBounds.y-uBounds.x;
    float u = (tg.x-uBounds.x)/span;
    float tp = u*(uFormDur-TAU)+TAU;
    float s = clamp((uFormT-tp+0.05)/0.75, 0.0, 1.0);
    float e = 1.0-pow(1.0-s, 3.0);
    vec2 start = vec2(tg.x+0.03*(aSeed.x-0.5), ribbonY(u, uT-(uFormT-tp)));
    pos = mix(start, tg, e) + sin(e*3.14159)*vec2(0.04*(aSeed.w-0.5), 0.02*(aSeed.x-0.5));
    float since = uFormT-tp-0.70;
    float landed = step(0.0, since);
    float sparkle = exp(-max(since,0.0)*2.4)*landed;
    alpha = step(0.0001, s)*(0.30+0.70*s)*mix(1.0, 0.085, smoothstep(0.0, 1.3, since))+sparkle;
    alpha *= mix(1.0, tw*(1.0+0.5*uPulse), landed);
    pos += hj*landed;
    size += 3.0*sparkle+1.5*(1.0-s);
  } else if(uAnim==5){
    // constellation: the letter's own sparks only show once it is filled
    float a = arriveAt(odt);
    alpha = 0.085*smoothstep(a, a+0.9, uFormT)*tw;
    pos += hj;
  } else if(uAnim==6 || uAnim==7){
    // petals or flakes fall from above and settle into the letters; the rest of the sparks glint as they land
    float s = clamp((uFormT-dep+1.5)/(TAU+1.5), 0.0, 1.0);
    float e = 1.0-(1.0-s)*(1.0-s);
    float since = uFormT-(dep+TAU);
    bool vis = aSeed.w>(uAnim==6 ? 0.90 : 0.86);
    vec2 start = tg+vec2((aSeed.y-0.5)*0.30, 0.26+0.30*aSeed.z);
    float sw = (uAnim==6 ? 0.035 : 0.020)*(1.0-e);
    if(vis){
      pos = mix(start, tg, e)+vec2(sw*sin(uT*1.3+aSeed.x*30.0), 0.0);
      alpha = smoothstep(0.0, 0.6, uFormT)*smoothstep(0.0, 0.12, s)*(1.0-smoothstep(0.0, 0.8, since))*0.9;
      size = uAnim==6 ? (12.0+12.0*aSeed.y*aSeed.y) : (5.0+7.0*aSeed.y*aSeed.y);
      vShape = uAnim==6 ? 1.0 : 2.0;
      vRot = uT*(0.6+1.2*aSeed.y)*(aSeed.x>0.5 ? 1.0 : -1.0)+aSeed.z*6.283;
      vFlip = 0.3+0.7*abs(cos(uT*(0.9+1.3*aSeed.z)+aSeed.w*9.0));
      if(since>0.0){ alpha = 0.0; }
    } else {
      float landed = step(0.0, since);
      float sparkle = exp(-max(since,0.0)*2.4)*landed;
      alpha = landed*(0.085*smoothstep(0.0, 0.6, since)+0.8*sparkle)*mix(1.0, tw*(1.0+0.5*uPulse), 1.0-sparkle);
      pos += hj*landed;
      size += 2.0*sparkle;
    }
  } else {
    // the classic gathering (used by wave), as in shaders.TEXTP_VS
    float s = clamp((uFormT-dep)/TAU, 0.0, 1.0);
    float e = 1.0-pow(1.0-s,3.0);
    vec2 start = vec2(tg.x+(aSeed.y-0.5)*0.55, -0.06+0.24*aSeed.z*aSeed.z);
    start.y = mix(start.y, uCalmY+0.02+0.12*aSeed.z*aSeed.z, uCalm);
    pos = mix(start, tg, e);
    float arc = sin(e*3.14159);
    pos += arc*vec2((aSeed.w-0.5)*0.17, (aSeed.x-0.5)*0.05);
    float landed = step(1.0, s);
    float since = uFormT-(dep+TAU);
    alpha = (0.22+0.78*s)*smoothstep(0.0,0.06,s);
    float sparkle = exp(-max(since,0.0)*2.4)*landed;
    alpha *= mix(1.0, 0.085, smoothstep(0.0,1.3,since)) + sparkle;
    alpha *= mix(1.0, tw*(1.0+0.5*uPulse), landed);
    alpha *= 1.0+3.0*waveBand(odt, tg.y)*landed;
    pos += landed*hj;
    size += 3.0*sparkle + 2.4*(1.0-s);
  }
  if(uFlyT>0.0){
    float rel = aSeed.z*0.8;
    float f = clamp((uFlyT-rel)/(uFlyDur-0.95), 0.0, 1.0);
    float lift = smoothstep(0.0,0.2,f);
    float base = uNode==1 ? 0.25 : 0.085;
    if(aSeed.w<0.42 && uDrift==0){
      float fe = f*f*(3.0-2.0*f);
      vec2 mid = mix(tg,uStar,0.45)+vec2((aSeed.x-0.5)*0.24, 0.02+0.10*aSeed.y);
      vec2 a = mix(tg,mid,fe), b = mix(mid,uStar,fe);
      pos = mix(a,b,fe);
      alpha = mix(base,1.0,lift)*(1.0-smoothstep(0.94,1.0,f));
      size = mix(size, 4.0, fe);
    } else {
      pos = tg + vec2((aSeed.x-0.5)*0.08*f + 0.008*sin(uT*2.0+aSeed.y*30.0)*f, (0.04+0.24*aSeed.y)*f*f);
      alpha = mix(base,0.85,lift)*(1.0-f);
    }
    vShape = uNode==1 ? 3.0 : 0.0;
  }
  vA = alpha; vK = aSeed.y;
  gl_Position = vec4(pos*2.0-1.0,0.0,1.0);
  gl_PointSize = size*uPx;
}
"""

PART_FS = """
#version 330
in float vA; in float vK; in float vRot; in float vFlip; in float vShape; out vec4 o;
uniform vec3 uColA, uColB;
void main(){
  vec2 p = gl_PointCoord*2.0-1.0;
  float a;
  vec3 col = mix(uColA, uColB, vK);
  if(vShape>0.5 && vShape<1.5){
    // a petal: rounded at one end, pointed at the other
    float c=cos(vRot), s=sin(vRot);
    p = vec2(c*p.x-s*p.y, s*p.x+c*p.y);
    p.x /= vFlip;
    float w = 0.46*sqrt(max(0.0,1.0-p.y*p.y))*(1.0-0.35*p.y);
    a = smoothstep(w, w-0.14, abs(p.x))*smoothstep(0.98,0.80,abs(p.y));
    a *= 0.55+0.45*(p.y*0.5+0.5);
  } else if(vShape>1.5 && vShape<2.5){
    // a snowflake: a soft disc with a faint six-fold glint
    float r = length(p);
    float ang = atan(p.y, p.x)+vRot;
    a = exp(-r*r*5.0) + 0.35*exp(-r*3.0)*pow(abs(cos(ang*3.0)), 12.0);
  } else if(vShape>2.5){
    // a star: a bright core and a thin cross
    float r2 = dot(p,p);
    a = exp(-r2*9.0) + 0.55*(exp(-abs(p.x)*16.0)*exp(-abs(p.y)*2.2) + exp(-abs(p.y)*16.0)*exp(-abs(p.x)*2.2));
  } else {
    float r2 = dot(p,p);
    if(r2>1.0) discard;
    a = exp(-r2*3.6);
  }
  o = vec4(col*a*vA, 1.0);
}
"""

EDGE_VS = "#version 330\n" + COMMON + """
in vec2 aPos; in vec4 aE;   // aE: along the line 0..1, across -1..1, line order, seed
out vec4 vE;
void main(){ vE = aE; gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0); }
"""
EDGE_FS = "#version 330\n" + COMMON + """
in vec4 vE; out vec4 o;
uniform vec3 uColA, uHot;
void main(){
  float te = arriveAt(vE.z)-0.85+0.25*vE.w;
  float g = clamp((uFormT-te)/0.45, 0.0, 1.0);
  float on = smoothstep(g+0.002, g-0.03, vE.x)*step(0.0001, g);
  float tip = exp(-pow((vE.x-g)/0.06, 2.0))*(1.0-step(0.999, g));
  float prof = exp(-vE.y*vE.y*3.2);
  float lvl = mix(0.85, 0.16, smoothstep(0.5, 2.6, uFormT-arriveAt(vE.z)));
  float fly = uFlyT>0.0 ? 1.0-smoothstep(0.0, 0.7, uFlyT-vE.w*0.3) : 1.0;
  o = vec4((uColA*on*lvl + uHot*tip*on*1.2)*prof*fly, 1.0);
}
"""


# ------------------------------------------------------------------ preparing a text
def build_aux(sharp):
    """Per pixel guides for the animations, at half size (sharp: HxW uint8, bottom row first).

    Returns float16 HxWx4 (bottom row first): r how far along its letter's strokes the pixel is (0 where the pen
    starts, the leftmost point of the letter, 1 where it ends), g distance from the letter's centre (1 at its
    farthest point), b, a the letter's centre (screen fractions). Pixels between letters take the nearest letter's
    values, so the glow round a letter moves with it. Also returns the half-size mask."""
    from scipy import ndimage as ndi
    h, w = sharp.shape
    a = sharp[: h - h % 2, : w - w % 2].reshape(h // 2, 2, w // 2, 2).max(axis=(1, 3))
    mask = a > 90
    hh, ww = mask.shape
    out = np.zeros((hh, ww, 4), np.float32)
    if not mask.any():
        return out.astype(np.float16), mask
    ones = np.ones((3, 3), bool)
    lab, n = ndi.label(mask, structure=ones)
    idx = np.arange(1, n + 1)
    rows = np.nonzero(mask.any(axis=1))[0]
    r0, r1 = max(rows.min() - 2, 0), min(rows.max() + 3, hh)
    sub = mask[r0:r1]
    sl = lab[r0:r1]
    # the pen starts at each letter's leftmost point and flows through the stroke (a walk inside the letter)
    ys, xs = np.nonzero(sub)
    ls = sl[ys, xs]
    order = np.lexsort((ys, xs, ls))
    first = np.ones(len(order), bool)
    first[1:] = ls[order][1:] != ls[order][:-1]
    seeds = np.zeros_like(sub)
    seeds[ys[order][first], xs[order][first]] = True
    dist = np.full(sub.shape, np.inf, np.float32)
    dist[seeds] = 0.0
    visited, front, k = seeds.copy(), seeds, 0
    while front.any() and k < 2000:
        k += 1
        front = ndi.binary_dilation(front, structure=ones) & sub & ~visited
        dist[front] = k
        visited |= front
    dist[~visited] = 0.0
    dmax = np.asarray(ndi.maximum(dist, sl, idx), np.float32)
    dn = np.zeros(sub.shape, np.float32)
    dn[sub] = dist[sub] / np.maximum(dmax[sl[sub] - 1], 1.0)
    stroke = np.zeros((hh, ww), np.float32)
    stroke[r0:r1] = dn
    com = np.asarray(ndi.center_of_mass(mask, lab, idx), np.float32).reshape(-1, 2)   # (row, col) per letter
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    lm = lab[mask] - 1
    dpix = np.hypot(yy[mask] - com[lm, 0], xx[mask] - com[lm, 1])
    rad = np.zeros(n, np.float32)
    np.maximum.at(rad, lm, dpix)
    # nearest letter for every pixel (inside letters: itself)
    ind = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
    near = lab[ind[0], ind[1]] - 1
    out[..., 0] = stroke[ind[0], ind[1]]
    out[..., 1] = np.hypot(yy - com[near, 0], xx - com[near, 1]) / np.maximum(rad[near], 1.0)
    out[..., 2] = (com[near, 1] + 0.5) / ww
    out[..., 3] = (com[near, 0] + 0.5) / hh
    return out.astype(np.float16), mask


def sample_targets(sharp, bounds, seed, nmin=6000, nmax=16000):
    """Spark targets on the letters (like text.render): Nx7 float32 (x, y, line order, four seeds), bottom-up y."""
    a = sharp.astype(np.float64)
    h, w = a.shape
    n = int(np.clip((a > 128).sum() / 2.0, nmin, nmax))
    rng = np.random.default_rng(seed)
    idx = rng.choice(a.size, size=n, p=(a / a.sum()).ravel())
    ys, xs = np.divmod(idx, w)
    px, py = xs + rng.random(n), ys + rng.random(n)
    x0, x1 = bounds[0] * w, bounds[1] * w
    order = (px - x0) / max(x1 - x0, 1.0)
    pts = np.stack([px / w, py / h, order], axis=1).astype("f4")
    return np.hstack([pts, rng.random((n, 4)).astype("f4")])


def constellation(mask, bounds, seed, spacing=11.0):
    """Stars on the letters (about every 22 px) and the lines between near neighbours that stay on the strokes.
    Returns star points (Nx7 like sample_targets) and the line quads (Mx6 vertices of x, y, along, across, order,
    seed), all in screen fractions with y from the bottom."""
    from scipy.spatial import cKDTree
    hh, ww = mask.shape
    ys, xs = np.nonzero(mask)
    if len(xs) < 4:
        return np.zeros((0, 7), "f4"), np.zeros((0, 6), "f4")
    rng = np.random.default_rng(seed)
    cell = np.floor(np.stack([xs / spacing, ys / spacing], 1)).astype(np.int64)
    key = cell[:, 0] * 100000 + cell[:, 1]
    jit = rng.random((2,)) * 0.0
    cx, cy = (cell[:, 0] + 0.5 + jit[0]) * spacing, (cell[:, 1] + 0.5 + jit[1]) * spacing
    d = (xs - cx) ** 2 + (ys - cy) ** 2 + rng.random(len(xs)) * 4.0
    o = np.lexsort((d, key))
    first = np.ones(len(o), bool)
    first[1:] = key[o][1:] != key[o][:-1]
    sel = o[first]
    P = np.stack([xs[sel] + 0.5, ys[sel] + 0.5], 1).astype(np.float64)
    tree = cKDTree(P)
    pairs = np.array(sorted(tree.query_pairs(spacing * 1.75)), dtype=np.int64).reshape(-1, 2)
    keep = []
    for i, j in pairs:
        ok = True
        for f in (0.25, 0.5, 0.75):
            q = P[i] * (1 - f) + P[j] * f
            if not mask[min(int(q[1]), hh - 1), min(int(q[0]), ww - 1)]:
                ok = False
                break
        if ok:
            keep.append((i, j))
    # at most three lines per star, shortest first, so the drawing stays light
    keep.sort(key=lambda e: np.sum((P[e[0]] - P[e[1]]) ** 2))
    deg = np.zeros(len(P), int)
    edges = []
    for i, j in keep:
        if deg[i] < 3 and deg[j] < 3:
            edges.append((i, j))
            deg[i] += 1
            deg[j] += 1
    U = P / np.array([ww, hh])
    x0, x1 = bounds
    od = np.clip((U[:, 0] - x0) / max(x1 - x0, 1e-3), 0, 1)
    stars = np.hstack([U, od[:, None], rng.random((len(U), 4))]).astype("f4")
    hw = 2.6 / 1080.0
    verts = []
    for i, j in edges:
        a, b = U[i], U[j]
        dv = (b - a) * np.array([S.ASPECT, 1.0])
        L = np.hypot(*dv)
        if L < 1e-6:
            continue
        nrm = np.array([-dv[1], dv[0]]) / L * hw
        nrm = nrm / np.array([S.ASPECT, 1.0])
        o_ = min(od[i], od[j])
        sd = rng.random()
        if od[j] < od[i]:
            a, b = b, a
        quad = [(a - nrm, 0, -1), (a + nrm, 0, 1), (b - nrm, 1, -1), (b - nrm, 1, -1), (a + nrm, 0, 1),
                (b + nrm, 1, 1)]
        for p, u, v in quad:
            verts.append((p[0], p[1], u, v, o_, sd))
    return stars, np.array(verts, "f4").reshape(-1, 6)


class TextAnims:
    """Draws texts that ask for an animation other than the classic sparks. Built once by the renderer."""

    def __init__(self, R):
        self.R = R
        self.items = {}
        default = getattr(S, "TEXT_ANIM", None)
        want = []
        for i, wd in enumerate(R.words):
            k = anim_of(wd["meta"], default)
            if k:
                want.append((("w", i), wd["tex"], wd["bounds"], wd["meta"], k, True))
        k = anim_of(S.TAGLINE)
        if k:
            want.append((("tag",), R.tag["tex"], R.tag["bounds"], S.TAGLINE, k, False))
        for j, fr in enumerate(R.frags):
            k = anim_of(fr["meta"])
            if k and fr["meta"].get("style", "sparks") == "sparks":
                want.append((("f", j), fr["tex"], fr["bounds"], fr["meta"], k, True))
        if not want:
            return
        ctx = self.ctx = R.ctx
        self.p_txt = ctx.program(vertex_shader=QUAD_VS, fragment_shader=TEXT_FS)
        self.p_txt["uFlip"].value = 1.0
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        self.v_txt = ctx.vertex_array(self.p_txt, [(quad, "2f", "aPos")])
        self.p_part = ctx.program(vertex_shader=PART_VS, fragment_shader=PART_FS)
        self.p_edge = ctx.program(vertex_shader=EDGE_VS, fragment_shader=EDGE_FS)
        for n, (key, tex, bounds, meta, k, parts) in enumerate(want):
            self.items[key] = self._prepare(tex, bounds, meta, k, parts, 9100 + n)

    def _prepare(self, tex, bounds, meta, k, parts, seed):
        ctx = self.ctx
        arr = np.frombuffer(tex.read(), np.uint8).reshape(tex.height, tex.width, 3)   # bottom row first
        sharp = arr[:, :, 0]
        aux, mask = build_aux(sharp)
        t_aux = ctx.texture((aux.shape[1], aux.shape[0]), 4, data=aux.tobytes(), dtype="f2")
        t_aux.filter = (moderngl.LINEAR, moderngl.LINEAR)
        t_aux.repeat_x = t_aux.repeat_y = False
        rows = np.nonzero(sharp.max(axis=1) > 40)[0]
        yb = (rows.min() / tex.height, (rows.max() + 1) / tex.height) if len(rows) else (0.5, 0.6)
        it = dict(anim=k, tex=tex, aux=t_aux, bounds=tuple(float(v) for v in bounds), yb=yb, meta=meta)
        if parts:
            pts = sample_targets(sharp, bounds, seed)
            it["vao"] = ctx.vertex_array(self.p_part, [(ctx.buffer(pts.tobytes()), "3f 4f", "aTarget", "aSeed")])
            it["n"] = len(pts)
        if k == ANIMS["constellation"]:
            stars, quads = constellation(mask, bounds, seed)
            if len(stars):
                it["v_star"] = ctx.vertex_array(self.p_part, [(ctx.buffer(stars.tobytes()), "3f 4f", "aTarget",
                                                               "aSeed")])
            if len(quads):
                it["v_edge"] = ctx.vertex_array(self.p_edge, [(ctx.buffer(quads.tobytes()), "2f 4f", "aPos", "aE")])
        return it

    def _colors(self, it):
        k, m = it["anim"], it["meta"]
        L = S.lin
        if k == ANIMS["petal"]:
            pc = m.get("colors") or getattr(S, "PETAL_COLORS", None) or ("#ff9fb2", "#ffe0d2")
            return L(pc[0]) * 0.95, L(pc[1]) * 0.75, L("#ffe8ee")
        if k == ANIMS["snow"]:
            sc = m.get("colors") or (getattr(S, "SNOW_COLOR", None) or "#eef4ff",) * 2
            return L(sc[0]), L(sc[1]) * 0.85, L("#f2f7ff")
        hot = {1: "#fff4dc", 2: "#fff0d0", 3: "#e6f0ff", 4: "#ffe6b8", 5: "#fff6e2", 8: "#fff2d8"}.get(k, "#fff4dc")
        return L("#fff0cc"), L("#ffb070") * 1.15, L(m.get("hot", hot))

    def _draw(self, it, t, form_t, form_dur, fly_t, fly_dur, star, pulse, calm, alpha, col, glow, drift):
        R = self.R
        line = float(it["meta"].get("line", S.HORIZON))
        line = line + (max(line, CALM_Y + 0.015) - line) * min(max(calm, 0.0), 1.0)
        ca, cb, hot = self._colors(it)
        com = dict(uT=t, uFormT=float(form_t), uFormDur=float(form_dur), uFlyT=float(fly_t), uLine=line,
                   uCalm=float(calm), uCalmY=CALM_Y, uBounds=it["bounds"], uYB=tuple(float(v) for v in it["yb"]))
        it["aux"].use(location=1)
        if "v_edge" in it:
            _setu(self.p_edge, uColA=S.lin("#ffe9c4") * 0.9, uHot=hot, **com)
            it["v_edge"].render(moderngl.TRIANGLES)
        part = dict(uAux=1, uFlyDur=float(fly_dur), uPx=R.px, uPulse=float(pulse), uStar=tuple(star),
                    uDrift=int(drift), **com)
        if "vao" in it:
            _setu(self.p_part, uAnim=it["anim"], uNode=0, uColA=ca, uColB=cb, **part)
            it["vao"].render(moderngl.POINTS)
        if "v_star" in it:
            _setu(self.p_part, uAnim=it["anim"], uNode=1, uColA=S.lin("#fff6e2"), uColB=S.lin("#ffd9a0"), **part)
            it["v_star"].render(moderngl.POINTS)
        it["tex"].use(location=0)
        _setu(self.p_txt, uTex=0, uAux=1, uAnim=it["anim"], uAspect=S.ASPECT, uAlpha=float(alpha),
              uPulse=float(pulse), uCol=col, uGlowCol=glow, uHot=hot, **com)
        self.v_txt.render(moderngl.TRIANGLE_STRIP)

    # the renderer's hooks: each returns False (and draws nothing) for a text that keeps the classic sparks
    def draw_word(self, i, t, form_t, fly_t, fly_dur, star, P, calm):
        it = self.items.get(("w", i))
        if it is None:
            return False
        self._draw(it, t, form_t, S.FORM_DUR, fly_t, fly_dur, star, P["pulse"], calm, 1.0, S.lin("#fff5df"),
                   S.lin("#ffc48c"), False)
        return True

    def draw_tagline(self, t, calm=0.0):
        it = self.items.get(("tag",))
        if it is None:
            return False
        tg = S.TAGLINE
        self._draw(it, t, (t - tg["t0"]) + 1.35, tg["t1"] - tg["t0"], -1.0, 1.0, (0.5, 0.9), 0.0, calm, 0.92,
                   S.lin("#fff1d6"), S.lin("#ffc48c"), True)
        return True

    def draw_frag(self, j, t, calm=0.0):
        it = self.items.get(("f", j))
        if it is None:
            return False
        m = it["meta"]
        fly = (t - m["out"]) if t > m["out"] else -1.0
        self._draw(it, t, (t - m["t0"]) + 1.35, max(m["t1"] - m["t0"], 0.5), fly, 1.6, (0.5, 0.9), 0.0, calm,
                   m.get("alpha", 0.95), S.lin("#fff1d6"), S.lin(m.get("glow", "#ffc48c")), True)
        return True


def _setu(prog, **kw):
    for k, v in kw.items():
        if k in prog:
            if isinstance(v, np.ndarray):
                v = tuple(float(x) for x in v.ravel())
            prog[k].value = v
