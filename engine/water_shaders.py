"""GLSL for the lake ripples, the campaign symbols drawn in light and falling stars (engine/water.py).

The ripples bend the lake itself in the composite pass (shaders.COMP_FS, the guarded uNRip block, which uses the
same formula as RIP_GLSL below). Everything here is light added on top, before the text protection pass.
"""

# the shared ripple formula: a ring on the water in perspective (rings near the far shore are small and flat)
# uRip[i] = (x, y, age in seconds, strength); uRipWL = the water line on screen
RIP_GLSL = """
uniform int uNRip; uniform vec4 uRip[24]; uniform float uRipWL;
float ripK(float y){ return 0.35+1.6*clamp((uRipWL-y)/max(uRipWL,0.05), 0.0, 1.0); }
float ripEnv(vec4 r){ return r.w*exp(-r.z/1.6)*smoothstep(0.0, 0.15, r.z); }
vec2 ripDisp(vec2 p){
  vec2 ds = vec2(0.0);
  for(int i=0;i<uNRip;i++){
    vec4 r = uRip[i];
    float k = ripK(r.y);
    vec2 q = vec2((p.x-r.x)*uAspect, (p.y-r.y)*3.2)/k;
    float rr = length(q);
    float e = (rr-r.z*0.075)/0.03;
    vec2 dir = q/max(rr, 1e-4);
    ds += vec2(dir.x, dir.y*0.6)*k*0.006*ripEnv(r)*exp(-e*e)*sin(e*4.0);
  }
  return ds*smoothstep(0.0, 0.012, uRipWL-p.y);
}
"""

# ------------------------------------------------------------------ ripple light: soft rings on the lake
RING_VS = """
#version 330
in vec2 aPos;
uniform vec4 uRect;   // centre x, y and half width, half height in screen fractions
out vec2 vS;
void main(){ vS = uRect.xy + aPos*uRect.zw; gl_Position = vec4(vS*2.0-1.0, 0.0, 1.0); }
"""
RING_FS = """
#version 330
in vec2 vS; out vec4 o;
uniform float uAspect, uCalm, uCalmY, uBright;
uniform vec3 uCol;
""" + RIP_GLSL + """
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  vec2 p = vS;
  float l = 0.0;
  for(int i=0;i<uNRip;i++){
    vec4 r = uRip[i];
    float k = ripK(r.y);
    vec2 q = vec2((p.x-r.x)*uAspect, (p.y-r.y)*3.2)/k;
    float rr = length(q);
    float R = r.z*0.075;
    float ring = exp(-pow((rr-R)/0.007, 2.0)) + 0.45*exp(-pow((rr-R*0.62)/0.007, 2.0))
               + 0.20*exp(-pow((rr-R*0.30)/0.006, 2.0));
    float splash = exp(-rr*rr/0.00015)*exp(-r.z*4.0)*0.35;   // the touch itself: a small flash
    l += (ring+splash)*ripEnv(r);
  }
  l *= smoothstep(0.0, 0.010, uRipWL-p.y)*mix(0.25, 1.0, calmK(p.y));
  o = vec4(uCol*l*uBright, 1.0);
}
"""

# ------------------------------------------------------------------ symbols: points along bezier strokes
SYM_VS = """
#version 330
in vec4 aP;        // x, y (unit coords), draw order 0..1, group (0 fixed, 1 left door, 2 right door)
in vec3 aCol;
in vec4 aSeed;
uniform float uT, uPx, uAspect, uSize, uStretch, uLocal, uDur, uOut, uLeaveDur, uBright, uPt, uHead;
uniform vec2 uCenter, uTo;
uniform int uLeave;            // 0 sparks, 1 to a star
uniform float uOpen;           // gate doors 0 closed .. 1 open
uniform vec3 uDoor;            // half width, spring line, bottom (unit coords)
uniform float uMirror;         // 1: draw the reflection in the lake
uniform float uCalm, uCalmY;
out vec3 vCol; out float vA;
""" + RIP_GLSL + """
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  vec2 p = aP.xy;
  int g = int(aP.w+0.5);
  if(g>0 && uOpen>0.0){
    float hx = g==1 ? -uDoor.x : uDoor.x;
    float a = uOpen*1.32;
    float f = abs(p.x-hx)/uDoor.x;
    p.x = hx+(p.x-hx)*cos(a);
    float cy = 0.5*(uDoor.y+uDoor.x+uDoor.z);
    p.y = cy+(p.y-cy)*(1.0+0.14*sin(a)*f);   // the near edge of the swinging door looks a little taller
  }
  vec2 s = uCenter + vec2(p.x*uSize*uStretch/uAspect, p.y*uSize);
  // the pen draws the stroke: each point appears when the pen passes, with a bright head
  float age = uDur>0.0 ? uLocal-aP.z*uDur : 1e3;
  float on = smoothstep(-0.02, 0.06, age);
  float head = age>=0.0 ? exp(-age/0.22) : 0.0;
  float settled = smoothstep(uDur, uDur+1.2, uLocal);
  float breath = 1.0+0.16*settled*sin(uT*1.6+aP.z*9.0+aSeed.x*2.0);
  float tw = 1.0+0.10*sin(uT*(2.0+3.0*aSeed.y)+aSeed.z*40.0);
  float a = on*breath*tw;
  float size = uPt*(1.0+1.4*head*uHead);
  if(uOut>=0.0){
    if(uLeave==0){   // dissolve into sparks that drift up and away
      float d = aSeed.x*0.9;
      float u = clamp((uOut-d)/uLeaveDur, 0.0, 1.0);
      vec2 v = vec2((aSeed.y-0.5)*0.12, 0.03+0.11*aSeed.z);
      s += v*u*uLeaveDur*0.6 + vec2(0.012*sin(uT*2.0+aSeed.w*30.0), 0.0)*u;
      float spark = smoothstep(0.0, 0.08, u)*(1.0-u);
      a *= (1.0-smoothstep(0.0, 1.0, u))*(1.0+1.6*spark*step(0.55, aSeed.w));
      size *= 1.0+0.8*spark*step(0.55, aSeed.w);
    } else {         // gather and fly to a light on the arch
      float d = aP.z*0.35+aSeed.x*0.15;
      float u = clamp((uOut-d)/uLeaveDur, 0.0, 1.0);
      float e = u*u*(3.0-2.0*u);
      vec2 side = vec2((aSeed.y-0.5)*0.035, 0.02+0.03*aSeed.z);
      s = mix(s, uTo, e) + side*sin(3.14159*e);
      a *= 1.0-smoothstep(0.80, 1.0, u)*0.95;
      size *= 1.0-0.35*e;
    }
  }
  if(uMirror>0.5){
    if(s.y<uRipWL) a = 0.0;            // below the water line: nothing to mirror
    s.y = 2.0*uRipWL-s.y;
    float dd = clamp((uRipWL-s.y)/max(uRipWL,0.05), 0.0, 1.0);
    s += ripDisp(s) + vec2(0.0011*sin(s.y*190.0+uT*1.3)+0.0003*sin(s.y*520.0-uT*2.1), 0.0);
    a *= 0.40*pow(1.0-dd, 1.3);
  }
  a *= mix(0.35, 1.0, calmK(s.y));
  vCol = mix(aCol, vec3(1.0, 0.97, 0.90)*1.4, min(head*uHead, 1.0)*0.75);
  vA = a*uBright*(1.0+2.2*head*uHead);
  gl_Position = vec4(s*2.0-1.0, 0.0, 1.0);
  gl_PointSize = size*uPx;
}
"""
SYM_FS = """
#version 330
in vec3 vCol; in float vA; out vec4 o;
void main(){
  vec2 q = gl_PointCoord*2.0-1.0;
  float g = exp(-dot(q,q)*4.0)*smoothstep(1.0, 0.7, length(q));
  o = vec4(vCol*vA*g, 1.0);
}
"""

# ------------------------------------------------------------------ a symbol's soft aura, and the gate's open doorway
GLOW_VS = """
#version 330
in vec2 aPos;
uniform vec2 uCenter; uniform float uSize, uAspect, uStretch;
uniform vec4 uBox;       // local box in unit coords: x0, y0, x1, y1
out vec2 vL;
void main(){
  vL = mix(uBox.xy, uBox.zw, aPos*0.5+0.5);
  vec2 s = uCenter + vec2(vL.x*uSize*uStretch/uAspect, vL.y*uSize);
  gl_Position = vec4(s*2.0-1.0, 0.0, 1.0);
}
"""
GLOW_FS = """
#version 330
in vec2 vL; out vec4 o;
uniform int uMode;          // 0 aura, 1 open doorway
uniform float uAmt, uOpen, uT;
uniform vec3 uCol, uColHot, uDoor;
void main(){
  if(uMode==0){
    vec2 q = vL/vec2(0.55, 0.50);
    float g = exp(-dot(q,q)*2.2);
    o = vec4(uCol*g*uAmt, 1.0);
    return;
  }
  float hw = uDoor.x, sp = uDoor.y, bt = uDoor.z;
  vec2 p = vL;
  // signed distance to the arched doorway
  float dx = abs(p.x)-hw;
  float sd = p.y<sp ? max(dx, bt-p.y) : length(vec2(p.x, p.y-sp))-hw;
  float inside = smoothstep(0.012, -0.004, sd);
  float gap = hw*(1.0-cos(uOpen*1.32));
  float through = mix(0.12, 1.0, smoothstep(gap+0.01, gap-0.03, abs(p.x)));
  float rays = 0.75+0.25*sin(atan(p.x, p.y-bt)*26.0+uT*0.7);
  vec3 c = mix(uCol, uColHot, smoothstep(gap*1.2, 0.0, abs(p.x)))*inside*through*(0.85+0.15*rays)*1.4;
  c += uCol*exp(-max(sd,0.0)/0.06)*0.30*(1.0-inside);           // the glow round the doorway
  // light spills forward over the steps and onto the water
  float below = bt-p.y;
  if(below>0.0){
    float wdt = gap+below*0.9;
    c += uCol*smoothstep(wdt, wdt*0.4, abs(p.x))*exp(-below/0.20)*0.55;
  }
  o = vec4(c*uAmt*uOpen, 1.0);
}
"""

# ------------------------------------------------------------------ simple sparks placed on the CPU (falling stars)
DOT_VS = """
#version 330
in vec2 aP; in float aB; in float aS;
uniform float uPx;
out float vB;
void main(){ vB = aB; gl_Position = vec4(aP*2.0-1.0, 0.0, 1.0); gl_PointSize = aS*uPx; }
"""
DOT_FS = """
#version 330
in float vB; out vec4 o;
uniform vec3 uCol;
void main(){
  vec2 q = gl_PointCoord*2.0-1.0;
  float g = exp(-dot(q,q)*4.0)*smoothstep(1.0, 0.7, length(q));
  o = vec4(uCol*vB*g, 1.0);
}
"""
