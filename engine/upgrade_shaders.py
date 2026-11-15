"""GLSL programs for the upgrade layers: people of light, snow, net, beam, bubbles, leaves and the fragment styles.

Scene plates, ice, shards and the golden field live in the composite pass (shaders.COMP_FS) because they change
the picture behind the light; everything here is light that is added on top (and so glows and reflects).
"""
from shaders import NOISE

HASH2 = """
vec2 hash22(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*vec3(0.1031,0.1030,0.0973));
  p3 += dot(p3, p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
"""

# ------------------------------------------------------------------ people of light: the spark body
FIGP_VS = """
#version 330
in vec2 aP0; in vec2 aP1; in vec2 aP2; in vec2 aP3; in vec4 aSeed;
uniform float uT, uPx;
uniform vec4 uRect;          // x0, y0 (feet line), width, height in screen fractions
uniform float uFlip;
uniform int uPoseA, uPoseB;  // morphing from pose A to pose B
uniform float uMorph;        // 0..1 progress of that morph
uniform float uGather, uGatherDur;   // seconds since the figure began to gather, gathering time
uniform float uDiss, uDissDur;       // seconds since it began to dissolve (<0 before), dissolving time
uniform vec2 uTo;            // where the sparks fly when the figure dissolves upward
uniform int uMode;           // 0 rise to uTo, 1 drift away upward
uniform float uBright, uSize;
out float vA; out float vK; out float vHot;
vec2 pose(int k){ if(k==0) return aP0; if(k==1) return aP1; if(k==2) return aP2; return aP3; }
vec2 toScreen(vec2 l){ float x = uFlip>0.5 ? 1.0-l.x : l.x; return vec2(uRect.x+x*uRect.z, uRect.y+l.y*uRect.w); }
void main(){
  // morph: each spark leaves a little earlier or later so the motion ripples through the body
  float delay = aSeed.y*0.38;
  float m = clamp((uMorph*1.38 - delay), 0.0, 1.0);
  m = m*m*(3.0-2.0*m);
  vec2 la = pose(uPoseA), lb = pose(uPoseB);
  vec2 loc = mix(la, lb, m);
  vec2 tg = toScreen(loc);
  // during the morph the sparks lift and curl a little, like breath
  float arc = sin(3.14159*m);
  tg += arc*vec2((aSeed.z-0.5)*0.018, 0.010+0.012*aSeed.w)*uRect.w*2.2;
  // living shimmer
  tg += 0.0011*vec2(sin(uT*1.3+aSeed.x*40.0), cos(uT*1.1+aSeed.y*40.0));
  // gather: sparks spiral in out of the air
  float gd = aSeed.x*0.5*uGatherDur;
  float s = clamp((uGather-gd)/(uGatherDur*0.5), 0.0, 1.0);
  float e = 1.0-pow(1.0-s,3.0);
  float ang = aSeed.z*6.2832 + 2.4*(1.0-e);
  float rad = (0.06+0.30*aSeed.w)*(1.0-e);
  vec2 start = vec2(cos(ang)*rad/1.7778, sin(ang)*rad*0.8 + 0.18*(1.0-e)*aSeed.y);
  vec2 pos = tg + start;
  float landed = step(1.0, s);
  float since = uGather-(gd+uGatherDur*0.5);
  float sparkle = exp(-max(since,0.0)*2.2)*landed;
  float tw = 0.65+0.35*sin(uT*(1.8+3.2*aSeed.y)+aSeed.z*50.0);
  float alpha = smoothstep(0.0,0.10,s)*(0.30+0.70*s);
  alpha *= mix(1.0, 0.36*tw, landed) + 0.9*sparkle + 0.40*arc;
  float size = (1.1 + 2.5*aSeed.w*aSeed.w*aSeed.w)*uSize + 2.2*sparkle + 2.0*(1.0-s) + 1.2*arc;
  float hot = sparkle + arc*0.6;
  // dissolve
  if(uDiss>0.0){
    float rel = (1.0-loc.y)*0.45 + aSeed.x*0.30;            // the feet let go first, the head last
    float f = clamp((uDiss - rel*uDissDur*0.55)/(uDissDur*0.55), 0.0, 1.0);
    float fe = f*f*(3.0-2.0*f);
    if(uMode==0 && aSeed.w<0.55){
      vec2 mid = mix(tg, uTo, 0.5) + vec2((aSeed.x-0.5)*0.30, 0.06+0.14*aSeed.y);
      vec2 a = mix(tg, mid, fe), b = mix(mid, uTo, fe);
      pos = mix(a, b, fe);
      alpha = mix(alpha, 0.9, smoothstep(0.0,0.15,f))*(1.0-smoothstep(0.92,1.0,f));
      size = mix(size, 3.4, fe);
      hot = 0.6*(1.0-f);
    } else {
      pos = tg + vec2((aSeed.x-0.5)*0.10*f + 0.010*sin(uT*1.7+aSeed.y*30.0)*f, (0.05+0.22*aSeed.y)*f*f);
      alpha *= (1.0-f)*(1.0+0.6*sin(3.14159*f));
    }
  }
  vA = alpha*uBright; vK = aSeed.y; vHot = hot;
  gl_Position = vec4(pos*2.0-1.0, 0.0, 1.0);
  gl_PointSize = size*uPx;
}
"""
FIGP_FS = """
#version 330
in float vA; in float vK; in float vHot; out vec4 o;
uniform vec3 uColA, uColB;
void main(){ vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  vec3 c = mix(uColA, uColB, vK);
  c = mix(c, vec3(1.0,0.97,0.9), clamp(vHot*0.6,0.0,0.8));
  o = vec4(c*exp(-r2*3.4)*vA, 1.0); }
"""

# ------------------------------------------------------------------ people of light: outline and glassy inner glow
FIGT_VS = """
#version 330
in vec2 aPos;
uniform vec4 uRect; uniform float uFlip;
out vec2 vL; out vec2 vS;
void main(){
  vec2 u = aPos*0.5+0.5;
  vL = vec2(uFlip>0.5 ? 1.0-u.x : u.x, u.y);
  vec2 s = vec2(uRect.x+u.x*uRect.z, uRect.y+u.y*uRect.w);
  vS = s;
  gl_Position = vec4(s*2.0-1.0, 0.0, 1.0);
}
"""
FIGT_FS = "#version 330\n" + NOISE + """
in vec2 vL; in vec2 vS; out vec4 o;
uniform sampler2D uTexA, uTexB;
uniform float uMix, uAlpha, uT, uGlass;
uniform vec3 uLine, uBody, uHalo;
void main(){
  vec3 a = texture(uTexA, vL).rgb, b = texture(uTexB, vL).rgb;
  vec3 tx = mix(a, b, uMix);
  // inner light that flows slowly upward through the body
  float flow = fbm3(vec2(vL.x*7.0, vL.y*5.0 - uT*0.22)) ;
  float shine = 0.55 + 0.9*flow*flow;
  vec3 c = uLine*tx.r*1.05 + uBody*tx.g*uGlass*shine + uHalo*tx.b*0.40;
  o = vec4(c*uAlpha, 1.0);
}
"""

# ------------------------------------------------------------------ snow
SNOW_VS = """
#version 330
in vec4 aSeed;
uniform float uT, uAmount, uPx, uWind, uSpeed;
uniform float uCalm, uCalmY;
out float vA; out float vSoft;
void main(){
  float depth = aSeed.x;                       // 0 far and small, 1 near and large
  float sp = mix(0.020, 0.080, depth)*uSpeed;
  float ph = fract(uT*sp/1.12 + aSeed.y);
  float y = 1.06 - ph*1.12;
  float sway = (0.006+0.016*depth)*(sin(uT*(0.35+0.5*aSeed.w)+aSeed.y*30.0) + 0.5*sin(uT*(0.9+0.7*aSeed.z)+aSeed.w*17.0));
  float x = fract(aSeed.z + uWind*uT*sp*0.6 + sway);
  float on = step(aSeed.w, uAmount);
  float tw = 0.80+0.20*sin(uT*(1.5+2.0*aSeed.y)+aSeed.z*60.0);
  vA = on*tw*mix(0.30, 0.70, depth)*smoothstep(0.0,0.04,ph);
  vA *= 1.0-uCalm*0.75*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y));   // calm lower third: fewer flakes there
  vSoft = depth;
  gl_Position = vec4(vec2(x,y)*2.0-1.0, 0.0, 1.0);
  gl_PointSize = mix(1.4, 7.5, pow(depth, 2.6))*uPx;
}
"""
SNOW_FS = """
#version 330
in float vA; in float vSoft; out vec4 o;
uniform vec3 uCol;
void main(){ vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  float core = exp(-r2*mix(4.5,1.4,vSoft));
  float disc = smoothstep(1.0,0.55,r2)*0.25*vSoft;
  o = vec4(uCol*(core+disc)*vA, 1.0); }
"""

# ------------------------------------------------------------------ net of light
NET_FS = "#version 330\n" + NOISE + HASH2 + """
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uAmt, uScale, uY0, uBright;
uniform vec2 uOrigin; uniform vec3 uCol, uColB;
vec2 node(vec2 g){ return g+0.5+(hash22(g)-0.5)*0.72; }
float reveal(vec2 nd){
  vec2 q = nd/uScale - vec2(uOrigin.x*uAspect, uOrigin.y);
  return length(q)/1.9 + 0.04*hash21(nd*3.1);
}
void main(){
  vec2 p = vec2(vUV.x*uAspect, vUV.y)*uScale;
  vec2 c = floor(p);
  float A = uAmt*1.12;
  float lines = 0.0, glow = 0.0, nodes = 0.0, pulses = 0.0;
  for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
    vec2 g = c+vec2(float(i),float(j));
    vec2 na = node(g);
    float ra = reveal(na);
    // knots of light
    float dn = length(p-na)/uScale;
    float on = smoothstep(ra, ra+0.02, A);
    nodes += on*(exp(-dn/0.0016)*1.4 + exp(-dn/0.006)*0.25);
    for(int k=0;k<4;k++){
      vec2 off = k==0 ? vec2(1.0,0.0) : (k==1 ? vec2(0.0,1.0) : (k==2 ? vec2(1.0,1.0) : vec2(1.0,-1.0)));
      float hk = hash21(g*1.7+off*5.3);
      if(k>=2 && hk<0.55) continue;
      vec2 nb = node(g+off);
      float rb = reveal(nb);
      vec2 s0 = ra<rb ? na : nb, s1 = ra<rb ? nb : na;
      float r0 = min(ra,rb), r1 = max(ra,rb);
      float grow = clamp((A-r0)/max(r1-r0,0.015), 0.0, 1.0);
      if(grow<=0.0) continue;
      // the thread sags a little and shimmers
      vec2 ab = s1-s0;
      float tt = clamp(dot(p-s0,ab)/dot(ab,ab), 0.0, grow);
      vec2 nrm = normalize(vec2(-ab.y, ab.x));
      vec2 pt = s0+ab*tt + nrm*0.10*sin(3.14159*tt)*(hk-0.5);
      float d = length(p-pt)/uScale;
      float sh = 0.75+0.25*sin(tt*18.0-uT*2.0+hk*20.0);
      lines += sh*exp(-d/0.0008);
      glow += exp(-d/0.005)*0.6;
      float pl = fract(uT*0.35+hk*7.0);
      pulses += exp(-pow((tt-pl)/0.035,2.0))*step(pl,grow)*exp(-d/0.0018);
    }
  }
  float mask = smoothstep(uY0, uY0+0.10, vUV.y);
  vec3 col = uCol*(lines*0.55 + glow*0.10 + nodes) + uColB*pulses*1.2;
  o = vec4(col*mask*uBright, 1.0);
}
"""

# ------------------------------------------------------------------ beam of light
BEAM_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uAmt;
uniform vec2 uFrom, uTo, uW;
uniform vec3 uCol;
void main(){
  vec2 p = vUV*vec2(uAspect,1.0), a = uFrom*vec2(uAspect,1.0), b = uTo*vec2(uAspect,1.0);
  vec2 ab = b-a; float L = length(ab); vec2 dir = ab/max(L,1e-5); vec2 nrm = vec2(-dir.y, dir.x);
  float along = dot(p-a, dir); float tt = clamp(along/L, 0.0, 1.0);
  float side = dot(p-a, nrm);
  float w = mix(uW.x, uW.y, tt);
  float inside = smoothstep(-0.02, 0.02, along)*smoothstep(L+0.03, L-0.01, along);
  float u = side/w;
  float core = exp(-u*u*2.6);
  float halo = exp(-abs(side)/(w*2.6));
  // god rays: streaks that slide slowly along the beam
  float rays = 0.55+0.45*vnoise(vec2(u*5.0, tt*2.5 - uT*0.12)) * vnoise(vec2(u*11.0+3.0, tt*1.3 + uT*0.05));
  // dust of light drifting up inside the beam
  float dust = pow(vnoise(vec2(side*900.0, along*140.0 - uT*2.2)), 14.0)*core;
  // a soft source and a pool of light where it lands
  float src = exp(-length(p-a)/(uW.x*2.0))*0.8;
  vec2 q = (p-b); q.y *= 3.6;
  float pool = exp(-length(q)/(uW.y*1.4));
  float fadeEnds = smoothstep(0.0, 0.10, tt)*0.6+0.4;
  // a gentle column (demo check 2026-11-14: it was too strong): soft core, light rays, a quiet pool
  vec3 c = uCol*(inside*(core*rays*0.26*fadeEnds + halo*0.06) + dust*1.6*inside + src*0.6 + pool*0.32);
  o = vec4(c*uAmt, 1.0);
}
"""

# ------------------------------------------------------------------ styled lyric fragments
# styles: 1 write (drawn by a pen of light), 2 reflection (appears in the water, then rises),
#         3 petals (petals fall and settle into the words), 4 engrave (carved in gold with sparks)
FRAGT_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform int uMode;
uniform float uLocal, uDur, uOut, uAspect, uHz, uAlpha, uTop, uBot;
uniform vec2 uBounds; uniform vec3 uCol, uGlowCol, uHot;
float ordAt(vec2 uv){
  float ox = clamp((uv.x-uBounds.x)/(uBounds.y-uBounds.x), 0.0, 1.0);
  return ox*0.96 + 0.04*vnoise(uv*vec2(uAspect,1.0)*90.0);
}
void main(){
  float er = vnoise(vUV*vec2(uAspect,1.0)*70.0);
  float dis = uOut>0.0 ? 1.0-smoothstep(0.0, 1.0, (uOut-er*0.9)/0.8) : 1.0;
  vec3 c = vec3(0.0);
  if(uMode==1 || uMode==4){
    vec3 tx = texture(uTex, vUV).rgb;
    float p = uLocal/max(uDur,0.1)*1.04;
    float od = ordAt(vUV);
    float rev = smoothstep(od-0.004, od+0.004, p);
    float nib = exp(-pow((p-od)/0.012, 2.0))*step(p,1.02);
    if(uMode==1){
      c = (uCol*tx.r*0.95 + uGlowCol*tx.g*0.22)*rev + uHot*(tx.g*1.6+tx.r*1.2)*nib;
    } else {
      // gold engraving: light from the upper left on the bevel of each letter
      vec2 e = vec2(1.0/1920.0, 1.0/1080.0)*2.0;
      float gx = texture(uTex, vUV+vec2(e.x,0.0)).g - texture(uTex, vUV-vec2(e.x,0.0)).g;
      float gy = texture(uTex, vUV+vec2(0.0,e.y)).g - texture(uTex, vUV-vec2(0.0,e.y)).g;
      vec3 n = normalize(vec3(-gx*5.0, -gy*5.0, 1.0));
      float lit = clamp(dot(n, normalize(vec3(-0.5,0.6,0.62))), 0.0, 1.0);
      float spec = pow(lit, 18.0);
      float heat = exp(-max(p-od,0.0)*uDur*1.4);
      vec3 gold = (mix(vec3(0.55,0.24,0.03), vec3(1.25,0.82,0.30), lit) + vec3(1.0,0.92,0.7)*spec*1.6)*1.35;
      gold = mix(gold, uHot*1.6, heat*0.75);
      float sheen = 0.85+0.3*smoothstep(0.92,1.0,sin(vUV.x*6.0-uLocal*0.9));
      c = (gold*tx.r*sheen + uGlowCol*tx.g*0.18)*rev + uHot*(tx.g*1.8+tx.r)*nib;
    }
  } else if(uMode==2){
    // the words first appear in the water as a rippling reflection, then rise out of it
    float rise = smoothstep(0.30, 1.0, uLocal/max(uDur,0.1));
    float drop = (1.0-rise)*(uBot-uHz+0.03);          // how far below its place the line still is
    vec2 suv = vUV + vec2(0.0, drop);
    vec3 tx = texture(uTex, suv).rgb;
    float above = smoothstep(uHz-0.004, uHz+0.012, vUV.y);
    float fr = smoothstep(0.0, 0.5, uLocal);
    c = (uCol*tx.r*0.92 + uGlowCol*tx.g*0.20)*above*smoothstep(0.15,0.9,rise)*fr;
    if(vUV.y<uHz){
      float d = uHz-vUV.y;
      float wob = (vnoise(vec2(vUV.x*uAspect*26.0, vUV.y*190.0-uLocal*1.1))-0.5)*0.010*(0.3+d*6.0)
                + sin(vUV.y*260.0+uLocal*2.4)*0.0016;
      vec2 ruv = vec2(vUV.x+wob, 2.0*uHz - vUV.y + drop);
      vec3 rt = texture(uTex, ruv).rgb;
      float ra = fr*(1.0-0.97*rise)*exp(-d*9.0);   // the mirror image stays near the line and leaves as the words rise
      c += (uCol*rt.r*0.55 + uGlowCol*rt.g*0.45)*ra*0.85;
    }
  } else if(uMode==3){
    vec3 tx = texture(uTex, vUV).rgb;
    float a = smoothstep(0.55, 1.0, uLocal/max(uDur,0.1));
    c = (uCol*tx.r*0.85 + uGlowCol*tx.g*0.30)*a;
    dis = uOut>0.0 ? 1.0-smoothstep(0.0, 0.6, uOut-er*0.4) : 1.0;
  }
  o = vec4(c*dis*uAlpha, 1.0);
}
"""

FRAGP_VS = """
#version 330
in vec3 aTarget; in vec4 aSeed;
uniform int uMode;
uniform float uT, uLocal, uDur, uOut, uPx, uHz;
out float vA; out float vK; out float vRot; out float vFlip; out float vHot;
void main(){
  vec2 tg = aTarget.xy;
  float od = aTarget.z*0.96;
  vec2 pos = tg; float a = 0.0; float size = 2.0; vHot = 0.0;
  vRot = 0.0; vFlip = 1.0;
  float p = uLocal/max(uDur,0.1)*1.04;
  if(uMode==1 || uMode==4){
    float since = (p-od)*uDur;
    if(since>0.0){
      float flash = exp(-since*3.2);
      a = 0.07 + 1.1*flash;
      size = 1.8 + 5.5*flash*aSeed.w;
      vHot = flash;
      if(uMode==1 && aSeed.w<0.25){
        pos += vec2((aSeed.x-0.5)*0.03, 0.03*aSeed.y)*(1.0-exp(-since*1.6));
        a = 0.9*exp(-since*1.4);
      }
      if(uMode==4 && aSeed.w<0.55){
        float s = min(since, 1.4);
        vec2 v = vec2((aSeed.x-0.5)*0.34, 0.10+0.30*aSeed.y);
        pos += v*s - vec2(0.0, 0.42*s*s);
        a = 1.6*exp(-since*2.6);
        size = 2.2 + 4.0*aSeed.z;
        vHot = 1.0;
      }
    }
  } else if(uMode==3){
    // petals fall from above and settle into the letters
    float arr = aSeed.z*0.78*uDur;
    float s = clamp((uLocal-arr)/1.8, 0.0, 1.0);
    float e = 1.0-pow(1.0-s, 2.0);
    vec2 start = tg + vec2((aSeed.x-0.5)*0.22 + 0.10, 0.30 + 0.35*aSeed.y);
    pos = mix(start, tg, e) + (1.0-e)*vec2(0.025*sin(uT*1.4+aSeed.w*20.0), 0.0);
    a = smoothstep(0.0, 0.12, s)*(0.55 + 0.30*aSeed.w);
    size = 11.0 + 12.0*aSeed.w*aSeed.w;
    vRot = uT*(0.6+1.2*aSeed.y)*(1.0-e)*(aSeed.x>0.5?1.0:-1.0) + aSeed.z*6.283;
    vFlip = mix(0.25+0.75*abs(cos(uT*(0.9+1.2*aSeed.z)+aSeed.w*9.0)), 0.85, e);
    if(uOut>0.0){
      float f = clamp((uOut - aSeed.x*0.6)/2.2, 0.0, 1.0);
      pos += vec2(0.30*f + 0.05*sin(uT+aSeed.y*9.0)*f, 0.05*f - 0.30*f*f);
      vRot += f*8.0*(aSeed.y-0.5);
      a *= 1.0-smoothstep(0.6, 1.0, f);
    }
  } else if(uMode==2){
    // a few sparks rise from the reflection with the words
    float rise = smoothstep(0.30, 1.0, uLocal/max(uDur,0.1));
    vec2 start = vec2(tg.x, 2.0*uHz - tg.y);
    float r = clamp(rise*1.3 - aSeed.y*0.3, 0.0, 1.0);
    pos = mix(start, tg, r*r*(3.0-2.0*r)) + vec2(0.0, 0.004*sin(uT*2.0+aSeed.x*30.0));
    a = (0.25+0.5*aSeed.w)*sin(3.14159*r) + 0.06*step(1.0, r);
    size = 2.0 + 3.0*aSeed.w;
    vHot = sin(3.14159*r);
    if(uOut>0.0){ a *= 1.0-smoothstep(0.0, 1.2, uOut); pos.y += 0.05*uOut*aSeed.y; }
  }
  if(uMode!=3 && uOut>0.0){
    float f = clamp(uOut/1.6, 0.0, 1.0);
    pos += vec2((aSeed.x-0.5)*0.05*f, (0.03+0.10*aSeed.y)*f*f);
    a *= 1.0-f;
  }
  vA = a; vK = aSeed.y;
  gl_Position = vec4(pos*2.0-1.0, 0.0, 1.0);
  gl_PointSize = size*uPx;
}
"""
FRAGP_FS = """
#version 330
in float vA; in float vK; in float vRot; in float vFlip; in float vHot; out vec4 o;
uniform int uMode; uniform vec3 uColA, uColB, uHot;
void main(){
  vec2 p = gl_PointCoord*2.0-1.0;
  if(uMode==3){
    float c = cos(vRot), s = sin(vRot);
    p = vec2(c*p.x-s*p.y, s*p.x+c*p.y);
    p.x /= vFlip;
    float w = 0.46*sqrt(max(0.0,1.0-p.y*p.y))*(1.0-0.35*p.y);
    float a = smoothstep(w, w-0.14, abs(p.x))*smoothstep(0.98,0.80,abs(p.y));
    vec3 col = mix(uColA, uColB, vK)*(0.55+0.45*(p.y*0.5+0.5));
    o = vec4(col*a*vA, 1.0);
    return;
  }
  float r2 = dot(p,p); if(r2>1.0) discard;
  vec3 col = mix(mix(uColA, uColB, vK), uHot, clamp(vHot,0.0,1.0));
  o = vec4(col*exp(-r2*3.6)*vA, 1.0);
}
"""

# ------------------------------------------------------------------ iridescent soap bubbles (theme, H3)
BUB_VS = """
#version 330
in vec4 aSeed;
uniform float uT, uAmount, uPx, uSize, uSpeed;
uniform float uCalm, uCalmY;
out float vA; out float vHue; out float vSpin; out float vDepth;
void main(){
  float depth = aSeed.x;                                 // 0 far and small, 1 near and large
  float sp = mix(0.010, 0.030, depth)*uSpeed;            // screens per second: a slow, floating rise
  float ph = fract(uT*sp/1.30 + aSeed.y);
  float y = -0.15 + ph*1.30;
  float wob = (0.010+0.020*depth)*(sin(uT*(0.21+0.25*aSeed.w)+aSeed.y*40.0) + 0.6*sin(uT*(0.53+0.3*aSeed.z)+aSeed.w*23.0));
  float x = fract(aSeed.z + wob + 0.012*sin(ph*6.2832+aSeed.w*9.0));
  float on = smoothstep(uAmount, uAmount-0.06, aSeed.w*0.999);
  float life = smoothstep(0.0, 0.10, ph)*smoothstep(1.0, 0.86, ph);
  vA = on*life*mix(0.55, 1.0, depth);
  vA *= 1.0-uCalm*0.85*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.06, y));   // calm lower third
  vHue = aSeed.y*7.0 + uT*0.05;
  vSpin = uT*(0.10+0.15*aSeed.z) + aSeed.w*6.2832;
  vDepth = depth;
  gl_Position = vec4(vec2(x,y)*2.0-1.0, 0.0, 1.0);
  float sz = mix(26.0, 118.0, pow(depth, 2.2))*uSize;
  gl_PointSize = min(sz*uPx, 250.0);
}
"""
BUB_FS = """
#version 330
in float vA; in float vHue; in float vSpin; in float vDepth; out vec4 o;
uniform vec3 uCol;
uniform float uSheen;
vec3 rainbow(float h){ return 0.5+0.5*cos(6.2832*(h+vec3(0.0,0.33,0.67))); }
void main(){
  vec2 p = gl_PointCoord*2.0-1.0; p.y = -p.y;
  float r = length(p); if(r>1.0) discard;
  // a thin bright rim, a faint film, a rainbow sheen that swirls round the rim, two soft highlights
  float rim = exp(-pow((r-0.90)/0.055, 2.0)) + 0.35*exp(-pow((r-0.80)/0.11, 2.0));
  float film = 0.045*smoothstep(0.2, 0.95, r);
  float ang = atan(p.y, p.x) + vSpin;
  float thick = 0.5+0.5*sin(ang*2.0 + r*5.0 + vHue) + 0.3*sin(ang*3.0 - vHue*0.7);
  vec3 irid = rainbow(vHue*0.13 + thick*0.55 + r*0.4);
  float band = smoothstep(0.35, 0.98, r)*(0.55+0.45*sin(ang + vHue));
  vec2 h1 = p - vec2(-0.40, 0.42); vec2 h2 = p - vec2(0.38, -0.40);
  float spec = exp(-dot(h1,h1)/0.020)*0.85 + exp(-dot(h1*vec2(1.0,2.6),h1*vec2(1.0,2.6))/0.08)*0.25 + exp(-dot(h2,h2)/0.010)*0.35;
  vec3 c = uCol*(rim*0.55 + film) + irid*uSheen*(rim*0.75 + band*0.22) + vec3(1.0,0.99,0.96)*spec;
  float edge = smoothstep(1.0, 0.96, r);
  o = vec4(c*vA*edge, 1.0);
}
"""

# ------------------------------------------------------------------ leaves of light (theme, H3)
LEAF_VS = """
#version 330
in vec4 aSeed;
uniform float uT, uAmount, uPx, uSize, uSpeed, uWind;
uniform float uCalm, uCalmY;
out float vA; out float vK; out float vRot; out float vFlip; out float vGlint;
void main(){
  float depth = aSeed.x;
  float sp = mix(0.016, 0.040, depth)*uSpeed;
  float ph = fract(uT*sp/1.25 + aSeed.y);
  float y = 1.10 - ph*1.25;                                  // drift down slowly
  float sway = (0.030+0.040*depth)*sin(uT*(0.32+0.30*aSeed.w)+aSeed.y*30.0);
  float x = fract(aSeed.z + uWind*ph*0.35 + sway);
  float on = smoothstep(uAmount, uAmount-0.05, aSeed.w*0.999);
  float life = smoothstep(0.0, 0.08, ph)*smoothstep(1.0, 0.90, ph);
  vA = on*life*mix(0.60, 1.0, depth);
  vA *= 1.0-uCalm*0.80*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.06, y));
  vK = fract(aSeed.y*13.7);
  vRot = 0.9*sin(uT*(0.40+0.35*aSeed.z)+aSeed.w*20.0) + aSeed.z*6.2832;     // turning as it swings
  float fl = cos(uT*(0.55+0.6*aSeed.x)+aSeed.y*17.0);
  vFlip = 0.45+0.55*abs(fl);                                  // tumbling: the leaf turns edge-on and back
  vGlint = pow(max(fl, 0.0), 8.0);                            // catches the light as it faces us
  gl_Position = vec4(vec2(x,y)*2.0-1.0, 0.0, 1.0);
  gl_PointSize = min(mix(30.0, 92.0, pow(depth, 1.6))*uSize*uPx, 250.0);
}
"""
LEAF_FS = """
#version 330
in float vA; in float vK; in float vRot; in float vFlip; in float vGlint; out vec4 o;
uniform vec3 uColA, uColB;
uniform int uMask;   // 1: the tint pass (premultiplied leaf colour and coverage), 0: the light
uniform float uTintK;   // how strongly the tint pass paints the leaf: the light then keeps mostly the rim and glint
void main(){
  vec2 p = gl_PointCoord*2.0-1.0;
  float c = cos(vRot), s = sin(vRot);
  p = vec2(c*p.x-s*p.y, s*p.x+c*p.y);
  p.x /= vFlip;
  // a pointed leaf: widest a little below the middle, a tip at the top, a short stem at the bottom
  float yy = p.y;
  float w = 0.42*sqrt(max(0.0, 1.0-yy*yy))*(1.0-0.30*yy);
  float body = smoothstep(w, w-0.12, abs(p.x))*smoothstep(0.98, 0.84, abs(yy));
  float stem = exp(-p.x*p.x/0.0012)*smoothstep(-0.80, -1.0, yy)*step(yy, -0.80)*0.6;
  float vein = exp(-p.x*p.x/0.0018)*smoothstep(0.9, -0.6, yy)*0.55;
  vec3 col = mix(uColA, uColB, vK*0.6 + 0.4*(yy*0.5+0.5));
  float edge = body*(1.0-smoothstep(w-0.12, w-0.30, abs(p.x)))*0.6;   // a brighter rim of light
  if(uMask==1){
    float a = body*clamp(vA*1.6, 0.0, 1.0);
    vec3 tc = col*(0.80+0.25*(yy*0.5+0.5)) + vec3(0.15,0.18,0.06)*vein;
    o = vec4(tc*a, a);
    return;
  }
  vec3 cc = col*(body*1.05*(1.0-0.85*uTintK) + edge*0.80*(1.0-0.5*uTintK)) + vec3(1.0,0.98,0.85)*(vein*body + stem)*0.45 + vec3(1.0,0.96,0.80)*vGlint*body*0.55;
  o = vec4(cc*vA, 1.0);
}
"""
