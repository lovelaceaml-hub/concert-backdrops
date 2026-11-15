"""GLSL programs for the backdrop renderer."""

NOISE = """
float hash11(float p){ p = fract(p*0.1031); p *= p+33.33; p *= p+p; return fract(p); }
float hash21(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*0.1031); p3 += dot(p3, p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); vec2 u=f*f*(3.0-2.0*f);
  return mix(mix(hash21(i),hash21(i+vec2(1.0,0.0)),u.x), mix(hash21(i+vec2(0.0,1.0)),hash21(i+vec2(1.0,1.0)),u.x), u.y); }
float fbm(vec2 p){ float a=0.5, s=0.0; mat2 m=mat2(1.6,1.2,-1.2,1.6);
  for(int i=0;i<5;i++){ s+=a*vnoise(p); p=m*p; a*=0.5; } return s; }
float fbm3(vec2 p){ float a=0.5, s=0.0; mat2 m=mat2(1.6,1.2,-1.2,1.6);
  for(int i=0;i<3;i++){ s+=a*vnoise(p); p=m*p; a*=0.5; } return s; }
"""

QUAD_VS = """
#version 330
in vec2 aPos;
out vec2 vUV;
uniform float uFlip;
void main(){ vUV = aPos*0.5+0.5; gl_Position = vec4(aPos.x, aPos.y*uFlip, 0.0, 1.0); }
"""

# ------------------------------------------------------------------ sky
SKY_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uHorizon;
uniform vec3 uSkyTop, uSkyMid, uSkyHor, uGlow, uAurA, uAurB;
uniform vec2 uSun; uniform float uSunInt, uSunSize;
uniform float uClouds, uAurora, uRain, uMilky, uEnv, uRays, uPart;
void main(){
  vec2 uv = vUV;
  float h = clamp((uv.y-uHorizon)/(1.0-uHorizon), 0.0, 1.0);
  vec3 c = mix(uSkyHor, uSkyMid, smoothstep(0.0,0.42,h));
  c = mix(c, uSkyTop, smoothstep(0.26,0.95,h));
  vec2 d = (uv-uSun)*vec2(uAspect,1.0);
  float r = length(d);
  float g = exp(-r*r/(uSunSize*uSunSize)) + 0.27*exp(-r/(uSunSize*2.3));
  c += uGlow*uSunInt*g*0.9;
  c += uGlow*uSunInt*0.20*exp(-h*7.5);
  if(uRays>0.001){
    float ang = atan(d.y, d.x);
    float rays = vnoise(vec2(ang*8.0, uT*0.045))*vnoise(vec2(ang*21.0+4.0, uT*0.07+2.0));
    c += uGlow*uSunInt*uRays*rays*exp(-r*2.2)*0.55*smoothstep(0.0,0.14,r);
  }
  // milky band of faint light for the night scenes
  if(uMilky>0.001){
    float band = exp(-pow((uv.y-(0.98-0.30*uv.x))/0.15, 2.0));
    float mw = fbm(vec2(uv.x*uAspect*3.4+3.0, uv.y*3.4)+7.0);
    c += uMilky*vec3(0.30,0.38,0.70)*band*(0.18+1.1*mw*mw)*0.16;
  }
  // clouds: shade a little, catch the light a lot near the sun
  vec2 q = vec2(uv.x*uAspect*1.25 + uT*0.006, uv.y*3.3);
  vec2 w = vec2(fbm3(q*1.3+vec2(0.0,uT*0.011)), fbm3(q*1.3+vec2(5.2,1.3)));
  float n = fbm(q*1.7 + 1.5*w + vec2(uT*0.012,0.0));
  float dens = smoothstep(0.50,0.86,n)*uClouds*(0.30+0.70*exp(-pow((h-0.24)/0.27,2.0)));
  float lane = exp(-pow((uv.x-0.5)*uAspect/0.30,2.0));
  dens *= 1.0-0.85*uPart*lane;
  c += uGlow*uSunInt*uPart*lane*0.10*exp(-h*1.8);
  vec3 lit = mix(uSkyHor*1.5+uGlow*0.12, uGlow*1.5, exp(-r*2.4)*clamp(uSunInt,0.0,1.6)/1.6);
  c = mix(c, c*0.74 + lit*0.42, dens);
  // ribbons of light that move with the music
  if(uAurora>0.001){
    vec2 pa = vec2(uv.x*uAspect, uv.y);
    float amp = 0.35+uEnv;
    vec3 au = vec3(0.0);
    for(int i=0;i<3;i++){
      float fi = float(i);
      float x = pa.x + fi*0.37;
      float y0 = 0.715 + 0.062*fi + 0.050*sin(x*1.25+uT*0.13+fi*2.1) + amp*0.034*sin(x*3.3-uT*0.31+fi*4.7) + 0.011*sin(x*8.0+uT*0.6+fi);
      float dd = pa.y-y0;
      float body = exp(-max(dd,0.0)*(6.5+2.0*fi))*smoothstep(-0.03,0.0,dd);
      float stri = 0.45+0.55*vnoise(vec2(x*40.0+fi*17.0, uT*0.33+fi));
      float fold = 0.55+0.45*sin(x*4.6+uT*0.27+fi*3.0);
      au += mix(uAurA,uAurB,0.5+0.5*sin(x*2.0+fi*1.9+uT*0.1))*body*stri*fold;
    }
    c += au*uAurora*(0.50+0.75*uEnv);
  }
  // a quiet rain of light
  if(uRain>0.001){
    float colx = (uv.x+uv.y*0.035)*uAspect*250.0;
    float ci = floor(colx); float fx = fract(colx);
    float hc = hash11(ci*1.37+2.0);
    float sp = 0.16+0.22*hash11(ci*7.7+1.0);
    float ph = fract(uv.y*(1.6+1.2*hash11(ci*3.1)) + uT*sp + hc*10.0);
    float head = pow(1.0-ph, 16.0);
    float xp = smoothstep(1.0,0.0,abs(fx-0.5)*4.2);
    c += uRain*vec3(0.78,0.84,1.0)*step(0.62,hc)*(0.3+0.7*hash11(ci*9.3))*head*xp*0.50*smoothstep(0.0,0.08,h);
  }
  o = vec4(c,1.0);
}
"""

# ------------------------------------------------------------------ points
STAR_VS = """
#version 330
in vec2 aPos; in vec2 aSeed;
uniform float uT, uStars, uHi, uPx;
out float vA; out float vK;
void main(){
  float tw = 0.62+0.38*sin(uT*(0.7+2.6*aSeed.x)+aSeed.y*60.0);
  float sp = pow(0.5+0.5*sin(uT*(1.5+4.0*aSeed.y)+aSeed.x*90.0), 6.0)*uHi;
  float b = aSeed.x*aSeed.x*aSeed.x;
  vA = uStars*(0.16+0.84*b)*(tw+1.2*sp)*smoothstep(0.44,0.62,aPos.y);
  vK = aSeed.y;
  gl_Position = vec4(aPos*2.0-1.0,0.0,1.0);
  gl_PointSize = (1.7+4.2*b)*uPx;
}
"""
STAR_FS = """
#version 330
in float vA; in float vK; out vec4 o;
void main(){ vec2 p=gl_PointCoord*2.0-1.0; float r2=dot(p,p); if(r2>1.0) discard;
  vec3 c = mix(vec3(0.72,0.82,1.0), vec3(1.0,0.90,0.78), vK);
  o = vec4(c*exp(-r2*4.0)*vA,1.0); }
"""

MOTE_VS = """
#version 330
in vec4 aSeed;
uniform float uT, uAmount, uPx, uSizeMin, uSizeMax, uPeriod, uY0, uY1, uSway, uBright;
uniform float uCalm, uCalmY;
out float vA; out float vK; out float vSoft;
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  float per = uPeriod*(0.7+0.8*aSeed.x);
  float ph = fract(uT/per + aSeed.y*7.31);
  float y = mix(uY0, uY1, ph) + 0.02*sin(uT*0.31+aSeed.z*40.0);
  float x = aSeed.z + uSway*(sin(uT*0.23+aSeed.w*30.0)+0.5*sin(uT*0.61+aSeed.x*50.0)) + (aSeed.x-0.5)*0.05*ph;
  float life = sin(3.14159*ph);
  float tw = 0.7+0.3*sin(uT*(1.0+2.5*aSeed.w)+aSeed.y*40.0);
  float on = smoothstep(uAmount, uAmount-0.08, aSeed.w*0.999);
  float s = aSeed.x*aSeed.y; s = fract(s*91.7);
  float sz = mix(uSizeMin, uSizeMax, s*s*s);
  vSoft = s;
  vA = uBright*on*life*tw*mix(1.0, 0.22, s*s)*calmK(y);
  vK = aSeed.y;
  gl_Position = vec4(vec2(x,y)*2.0-1.0,0.0,1.0);
  gl_PointSize = sz*uPx;
}
"""
MOTE_FS = """
#version 330
in float vA; in float vK; in float vSoft; out vec4 o;
uniform vec3 uColA, uColB;
void main(){ vec2 p=gl_PointCoord*2.0-1.0; float r2=dot(p,p); if(r2>1.0) discard;
  float core = exp(-r2*mix(5.0,1.6,vSoft));
  float disc = smoothstep(1.0,0.75,r2)*0.35*vSoft;
  o = vec4(mix(uColA,uColB,vK)*(core+disc)*vA,1.0); }
"""

PETAL_VS = """
#version 330
in vec4 aSeed;
uniform float uT, uAmount, uPx;
uniform float uCalm, uCalmY;
out float vA; out float vRot; out float vFlip; out float vK;
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  float per = 15.0+12.0*aSeed.x;
  float ph = fract(uT/per + aSeed.y*5.77);
  float y = 1.06 - ph*1.02;
  float x = fract(aSeed.z + 0.22*ph + 0.035*sin(uT*0.5+aSeed.w*30.0) + 0.02*sin(uT*1.1+aSeed.x*17.0));
  float on = smoothstep(uAmount, uAmount-0.1, aSeed.w*0.999);
  vA = on*smoothstep(0.0,0.08,ph)*smoothstep(1.0,0.75,ph)*calmK(y);
  vRot = uT*(0.5+1.4*aSeed.y)*(aSeed.x>0.5?1.0:-1.0) + aSeed.z*6.283;
  vFlip = 0.25+0.75*abs(cos(uT*(0.9+1.3*aSeed.z)+aSeed.w*9.0));
  vK = aSeed.x;
  gl_Position = vec4(vec2(x,y)*2.0-1.0,0.0,1.0);
  gl_PointSize = (20.0+34.0*aSeed.y*aSeed.y)*uPx;
}
"""
PETAL_FS = """
#version 330
in float vA; in float vRot; in float vFlip; in float vK; out vec4 o;
uniform vec3 uColA, uColB;
void main(){
  vec2 p = gl_PointCoord*2.0-1.0;
  float c=cos(vRot), s=sin(vRot);
  p = vec2(c*p.x-s*p.y, s*p.x+c*p.y);
  p.x /= vFlip;
  // a petal: rounded at one end, pointed at the other
  float w = 0.46*sqrt(max(0.0,1.0-p.y*p.y))*(1.0-0.35*p.y);
  float a = smoothstep(w, w-0.14, abs(p.x))*smoothstep(0.98,0.80,abs(p.y));
  float vein = 0.75+0.25*smoothstep(0.0,0.3,abs(p.x));
  vec3 col = mix(uColA,uColB,vK)*(0.55+0.45*(p.y*0.5+0.5));
  o = vec4(col*a*vein*vA,1.0);
}
"""

TEXTP_VS = """
#version 330
in vec3 aTarget; in vec4 aSeed;
uniform float uT, uFormT, uFormDur, uFlyT, uFlyDur, uPx, uPulse;
uniform vec2 uStar;
uniform float uCalm, uCalmY;
out float vA; out float vK;
const float TAU = 1.35;
void main(){
  vec2 tg = aTarget.xy;
  float od = clamp(aTarget.z*0.84 + aSeed.x*0.16, 0.0, 1.0);
  float dep = od*(uFormDur-TAU);
  float s = clamp((uFormT-dep)/TAU, 0.0, 1.0);
  float e = 1.0-pow(1.0-s,3.0);
  vec2 start = vec2(tg.x+(aSeed.y-0.5)*0.55, -0.06+0.24*aSeed.z*aSeed.z);
  // with a calm lower third the sparks come out of the air just above it, not up from the stage
  start.y = mix(start.y, uCalmY+0.02+0.12*aSeed.z*aSeed.z, uCalm);
  vec2 pos = mix(start, tg, e);
  float arc = sin(e*3.14159);
  pos += arc*vec2((aSeed.w-0.5)*0.17, (aSeed.x-0.5)*0.05);
  float landed = step(1.0, s);
  float since = uFormT-(dep+TAU);
  float alpha = (0.22+0.78*s)*smoothstep(0.0,0.06,s);
  float sparkle = exp(-max(since,0.0)*2.4)*landed;
  float hold = mix(1.0, 0.085, smoothstep(0.0,1.3,since));
  alpha *= hold + 1.0*sparkle;
  float tw = 0.70+0.30*sin(uT*(2.0+3.0*aSeed.y)+aSeed.z*50.0);
  alpha *= mix(1.0, tw*(1.0+0.5*uPulse), landed);
  pos += landed*0.0008*vec2(sin(uT*1.3+aSeed.x*40.0), cos(uT*1.1+aSeed.y*40.0));
  float size = 2.4 + 4.6*aSeed.w*aSeed.w*aSeed.w + 3.0*sparkle + 2.4*(1.0-s);
  if(uFlyT>0.0){
    float rel = aSeed.z*0.8;
    float f = clamp((uFlyT-rel)/(uFlyDur-0.95), 0.0, 1.0);
    float lift = smoothstep(0.0,0.2,f);
    if(aSeed.w<0.42){
      float fe = f*f*(3.0-2.0*f);
      vec2 mid = mix(tg,uStar,0.45)+vec2((aSeed.x-0.5)*0.24, 0.02+0.10*aSeed.y);
      vec2 a = mix(tg,mid,fe), b = mix(mid,uStar,fe);
      pos = mix(a,b,fe);
      alpha = mix(0.085,1.0,lift)*(1.0-smoothstep(0.94,1.0,f));
      size = mix(size, 4.0, fe);
    } else {
      pos = tg + vec2((aSeed.x-0.5)*0.08*f + 0.008*sin(uT*2.0+aSeed.y*30.0)*f, (0.04+0.24*aSeed.y)*f*f);
      alpha = mix(0.085,0.85,lift)*(1.0-f);
    }
  }
  vA = alpha; vK = aSeed.y;
  gl_Position = vec4(pos*2.0-1.0,0.0,1.0);
  gl_PointSize = size*uPx;
}
"""
TEXTP_FS = """
#version 330
in float vA; in float vK; out vec4 o;
uniform vec3 uColA, uColB;
void main(){ vec2 p=gl_PointCoord*2.0-1.0; float r2=dot(p,p); if(r2>1.0) discard;
  o = vec4(mix(uColA,uColB,vK)*exp(-r2*3.6)*vA,1.0); }
"""

# ------------------------------------------------------------------ solid words
TEXT_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
uniform float uFormT, uFormDur, uFlyT, uAspect, uAlpha, uPulse;
uniform vec2 uBounds; uniform vec3 uCol, uGlowCol;
const float TAU = 1.35;
void main(){
  vec3 tx = texture(uTex, vUV).rgb;
  float od = clamp((vUV.x-uBounds.x)/(uBounds.y-uBounds.x), 0.0, 1.0);
  float arrive = od*(uFormDur-TAU)+TAU;
  float rev = smoothstep(-0.25, 0.75, uFormT-arrive);
  float er = vnoise(vUV*vec2(uAspect,1.0)*70.0);
  float dis = 1.0-smoothstep(0.0, 1.0, (uFlyT-er*0.9)/0.8);
  float a = rev*dis*uAlpha;
  vec3 c = uCol*tx.r*0.92 + uGlowCol*tx.g*(0.15+0.06*uPulse);
  o = vec4(c*a,1.0);
}
"""

# ------------------------------------------------------------------ title block (card, then corner)
CREDIT_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex; uniform vec4 uCredit; uniform vec2 uC0;
uniform vec3 uCol, uGlowCol;
void main(){
  vec2 tuv = (vUV-uCredit.xy)/uCredit.z + uC0;
  if(tuv.x<0.0||tuv.x>1.0||tuv.y<0.0||tuv.y>1.0){ o = vec4(0.0); return; }
  vec3 tx = texture(uTex, tuv).rgb;
  o = vec4((uCol*tx.r*0.95 + uGlowCol*tx.g*0.13)*uCredit.w, 1.0);
}
"""

# ------------------------------------------------------------------ the nine lights
LIGHTS_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uHi;
uniform vec2 uStarPos[9]; uniform vec2 uStarI[9]; uniform float uLink[8];
uniform float uStarR[9];   // thin rings that stay round a light, one per relight (fractional while one settles)
uniform vec3 uColA, uColB;
uniform int uMode; uniform vec2 uLantern; uniform float uLanternI;
vec3 flare(vec2 uv, vec2 c, float I, float age, float seed, float nr){
  vec2 d = (uv-c)*vec2(uAspect,1.0);
  float r = length(d);
  float core = exp(-r*r/(0.0030*0.0030));
  float glow = exp(-r/0.011)*0.55 + exp(-r/0.040)*0.13;
  float ang = atan(d.y,d.x);
  float rp = 0.0165*(0.50+0.50*pow(abs(cos(2.5*ang+seed+uT*0.05)),0.8));
  float petal = smoothstep(rp, rp*0.25, r)*0.42;
  float cross = exp(-abs(d.x)/0.0011)*exp(-abs(d.y)/0.034) + exp(-abs(d.y)/0.0011)*exp(-abs(d.x)/0.056);
  float tw = 0.86+0.14*sin(uT*(1.3+seed*0.4)+seed*5.0)+0.25*uHi*sin(uT*7.0+seed*9.0);
  vec3 col = mix(uColA,uColB,0.5+0.5*sin(seed*2.3));
  vec3 outc = col*I*tw*(core*2.2+glow+petal+cross*0.5);
  if(age>=0.0 && age<3.0){
    float ring = exp(-pow((r-age*0.16)/0.005,2.0))*exp(-age*1.6);
    outc += col*ring*0.9;
  }
  // the history of the light: one thin, faint ring for every time it was lit again
  for(int k=0;k<6;k++){
    float on = clamp(nr-float(k), 0.0, 1.0);
    if(on<=0.0) break;
    float rad = 0.021+0.0062*float(k);
    float th = exp(-pow((r-rad)/0.00085,2.0));
    float sh = 0.80+0.20*sin(ang*3.0+uT*0.4+seed+float(k));
    outc += col*th*on*sh*0.55*min(I+0.25, 1.0);
  }
  return outc;
}
void main(){
  vec3 c = vec3(0.0);
  if(uMode==0){
    for(int i=0;i<9;i++){
      if(uStarI[i].x>0.001) c += flare(vUV, uStarPos[i], uStarI[i].x, uStarI[i].y, float(i)*1.7+0.6, uStarR[i]);
    }
    for(int i=0;i<8;i++){
      float g = uLink[i];
      if(g>0.001){
        vec2 a = uStarPos[i]*vec2(uAspect,1.0), b = uStarPos[i+1]*vec2(uAspect,1.0);
        vec2 p = vUV*vec2(uAspect,1.0);
        vec2 ab = b-a; float tt = clamp(dot(p-a,ab)/dot(ab,ab), 0.0, 1.0);
        float dist = length(p-(a+ab*tt));
        float vis = smoothstep(g+0.02, g-0.02, tt);
        float shimmer = 0.75+0.25*sin(tt*30.0-uT*2.2+float(i));
        float ends = smoothstep(0.0,0.08,tt)*smoothstep(1.0,0.92,tt);
        c += mix(uColA,uColB,0.5)*vis*ends*shimmer*(exp(-dist/0.0013)*0.50+exp(-dist/0.007)*0.10);
      }
    }
    c *= smoothstep(0.735,0.78,vUV.y);
  } else {
    vec2 d = (vUV-uLantern)*vec2(uAspect,1.0);
    float r = length(d);
    float core = exp(-r*r/(0.0034*0.0034))*2.4;
    float glow = exp(-r/0.010)*0.6 + exp(-r/0.034)*0.16;
    float cross = exp(-abs(d.y)/0.0012)*exp(-abs(d.x)/0.06)*0.6 + exp(-abs(d.x)/0.0012)*exp(-abs(d.y)/0.03)*0.4;
    c = uColA*uLanternI*(core+glow+cross)*smoothstep(0.095,0.045,r);
  }
  o = vec4(c,1.0);
}
"""

# ------------------------------------------------------------------ blur
BLUR_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex; uniform vec2 uDir;
void main(){
  vec3 c = texture(uTex, vUV).rgb*0.2270270270;
  c += texture(uTex, vUV+uDir*1.3846153846).rgb*0.3162162162;
  c += texture(uTex, vUV-uDir*1.3846153846).rgb*0.3162162162;
  c += texture(uTex, vUV+uDir*3.2307692308).rgb*0.0702702703;
  c += texture(uTex, vUV-uDir*3.2307692308).rgb*0.0702702703;
  o = vec4(c,1.0);
}
"""

# ------------------------------------------------------------------ text protection (Astra round 1, finding 3)
# Drawn into the light buffer with blend (ZERO, SRC_COLOR) after the decorative light and before the words:
# it multiplies motes, petals, snow, beams, nets and figures by (1 - field) behind every piece of text.
PROTECT_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTexA, uTexB, uTexC;
uniform vec2 uShade; uniform float uK;
uniform vec4 uCredit; uniform vec2 uC0;
uniform vec4 uTxA, uTxB; uniform vec2 uBndA, uBndB, uOffA, uOffB;

// The veil and the shadow behind a text slot follow the letters themselves (attack round 2): per pixel, they
// appear as the letters arrive left to right, leave as the letters dissolve, scale with the letters' opacity
// (p.w), and move with them (off: where the letters are drawn now, e.g. a reflection still rising).
float veilVis(vec2 uv, vec4 p, vec2 bnd){
  float od = clamp((uv.x-bnd.x)/(bnd.y-bnd.x), 0.0, 1.0);
  float arrive = od*(p.y-1.35)+1.35;
  float rev = smoothstep(-0.30, 0.55, p.x-arrive);
  float dis = p.z>0.0 ? 1.0-smoothstep(0.05, 1.45, p.z) : 1.0;
  return rev*dis*clamp(p.w, 0.0, 1.0);
}
float veilAt(sampler2D tx, vec2 uv, vec4 p, vec2 bnd, vec2 off){
  vec2 q = uv+off;
  if(q.y<0.0 || q.y>1.0) return 0.0;
  return texture(tx, q).b*veilVis(q, p, bnd);
}
void main(){
  float m = max(veilAt(uTexA, vUV, uTxA, uBndA, uOffA)*uShade.x, veilAt(uTexB, vUV, uTxB, uBndB, uOffB)*uShade.y);
  vec2 cuv = (vUV-uCredit.xy)/uCredit.z + uC0;
  if(cuv.x>0.0 && cuv.x<1.0 && cuv.y>0.0 && cuv.y<1.0) m = max(m, texture(uTexC, cuv).b*uCredit.w);
  m = smoothstep(0.0, 0.75, m);
  o = vec4(vec3(1.0-uK*m), 1.0);
}
"""

# ------------------------------------------------------------------ composite
COMP_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uSky, uL, uB1, uB2, uB3, uB4, uRidge, uTextA, uTextB;
uniform float uT, uAspect, uHorizon, uProg, uTrail, uExposure, uFade, uFrame, uBloom, uHi, uEnv, uSunInt;
uniform vec3 uMtn, uSkyHor, uGlow, uTrailCol;
uniform vec2 uSun;
uniform vec2 uShade;   // strength of the soft shadow behind text A and B
uniform vec4 uTxA, uTxB;   // form time, form duration, fly time, alpha
uniform vec2 uBndA, uBndB; uniform float uZoom;
uniform vec2 uOffA, uOffB;   // where slot A and B's letters are drawn now, relative to their texture (rising text)
uniform sampler2D uTextC; uniform vec4 uCredit; uniform vec2 uC0;
uniform int uNRings; uniform vec4 uRings[16];
uniform int uNWaves; uniform vec4 uWaves[4];
// upgrade layers (all zero, and so switched off, unless a song asks for them)
uniform int uPlN; uniform sampler2D uPlA, uPlB;
uniform vec4 uPlAView, uPlBView, uPlAWat, uPlBWat, uPlATr, uPlBTr;
uniform float uPlAAlpha, uPlBAlpha, uFlash;
uniform float uPlACalm, uPlBCalm;   // plate gain at the very bottom under BOTTOM_CALM (ramps to 1 at 0.30 height)
uniform vec4 uShards; uniform vec3 uShardCol;
uniform vec4 uIce; uniform vec3 uIceCol, uThawCol;
uniform vec4 uField; uniform vec3 uFieldCol;
uniform float uShadeK;
uniform vec4 uInkA, uInkB, uInkC;   // per-text colour (display rgb, strength) for slot A, slot B and the credit
uniform float uTheme;
uniform sampler2D uLeafT; uniform float uLeafK;   // LEAVES tint: leaf colour (premultiplied) and coverage               // SKY_THEME: 0 the original night-to-dawn world, 1 a bright day (lighter lake, vignette)
uniform int uNRip; uniform vec4 uRip[24]; uniform float uRipWL;   // lake ripples (engine/water.py)
uniform float uCalm, uCalmY;   // calm lower third: rings, glitter, reflections and thaw edges fade there
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
vec2 hash22(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*vec3(0.1031,0.1030,0.0973));
  p3 += dot(p3, p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
float voro(vec2 x, out vec2 cell, out vec2 toC){
  vec2 n = floor(x), f = fract(x); vec2 mg = vec2(0.0), mr = vec2(0.0); float md = 8.0;
  for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
    vec2 g = vec2(float(i),float(j)); vec2 r = g+hash22(n+g)-f; float d = dot(r,r);
    if(d<md){ md = d; mr = r; mg = g; }
  }
  md = 8.0;
  for(int j=-2;j<=2;j++) for(int i=-2;i<=2;i++){
    vec2 g = mg+vec2(float(i),float(j)); vec2 r = g+hash22(n+g)-f;
    if(dot(mr-r,mr-r)>0.00001) md = min(md, dot(0.5*(mr+r), normalize(r-mr)));
  }
  cell = n+mg; toC = mr;
  return md;
}
vec3 invTone(vec3 y){
  y = clamp(y, 0.0, 0.975);
  vec3 a = 2.43*y-2.51, b = 0.59*y-0.03, c = 0.14*y;
  return (-b - sqrt(max(b*b-4.0*a*c, 0.0)))/(2.0*a);
}
float ridged1(float x, float seed){
  float sum=0.0, a=0.5, f=1.0;
  for(int i=0;i<5;i++){
    float n = vnoise(vec2(x*f+seed*(1.0+float(i)), seed*3.1+float(i)*7.0));
    sum += a*(1.0-abs(2.0*n-1.0)); a*=0.5; f*=2.13;
  }
  return sum;
}
vec3 scene(vec2 uv){
  vec3 c = texture(uSky, uv).rgb;
  vec3 hz = texture(uSky, vec2(uv.x, uHorizon+0.012)).rgb;
  float aa = 0.0010;
  float hh = max(uv.y-uHorizon, 0.0);
  // the far range: the loudness of the whole song, left to right
  float ry = uHorizon + texture(uRidge, vec2(uv.x,0.5)).r;
  float m1 = smoothstep(ry+aa, ry-aa, uv.y);
  // SKY_THEME: the far range fades into the haze before its ends, so no hard step shows on a bright sky
  float ef = mix(1.0, smoothstep(0.035, 0.11, uv.x)*smoothstep(0.965, 0.89, uv.x), uTheme);
  m1 *= ef;
  float lit = smoothstep(uProg+0.003, uProg-0.014, uv.x);
  float depth = clamp(hh/0.17, 0.0, 1.0);
  vec3 far = mix(uMtn*1.5, hz, 0.74-0.30*depth);
  far += uTrailCol*uTrail*lit*0.030*depth;
  c = mix(c, far, m1);
  float dr = uv.y-ry;
  float rim = (exp(-abs(dr)*900.0)*0.85 + exp(-max(dr,0.0)*95.0)*0.13*step(0.0,dr))*ef;
  c += uTrailCol*uTrail*lit*rim;
  c += uTrailCol*0.03*exp(-abs(dr)*900.0)*(1.0-lit)*ef;
  // mist, then two nearer ranges
  c = mix(c, hz*1.04, exp(-hh/0.030)*0.30);
  float y2 = uHorizon + 0.010 + 0.105*pow(ridged1(uv.x*2.1, 11.0), 1.7);
  float m2 = smoothstep(y2+aa, y2-aa, uv.y);
  float d2 = clamp((y2-uv.y)/0.07, 0.0, 1.0);
  c = mix(c, mix(uMtn*0.85, hz, 0.20+0.22*d2), m2);
  c = mix(c, hz*1.02, exp(-hh/0.016)*0.26);
  float y3 = uHorizon + 0.003 + 0.070*pow(ridged1(uv.x*3.3+5.0, 3.7), 2.0) + 0.0022*vnoise(vec2(uv.x*520.0,1.0));
  float m3 = smoothstep(y3+aa, y3-aa, uv.y);
  c = mix(c, mix(uMtn*mix(0.30, 0.78, uTheme), hz, mix(0.05, 0.30, uTheme)), m3);
  return c;
}

// The veil and the shadow behind a text slot follow the letters themselves (attack round 2): per pixel, they
// appear as the letters arrive left to right, leave as the letters dissolve, scale with the letters' opacity
// (p.w), and move with them (off: where the letters are drawn now, e.g. a reflection still rising).
float veilVis(vec2 uv, vec4 p, vec2 bnd){
  float od = clamp((uv.x-bnd.x)/(bnd.y-bnd.x), 0.0, 1.0);
  float arrive = od*(p.y-1.35)+1.35;
  float rev = smoothstep(-0.30, 0.55, p.x-arrive);
  float dis = p.z>0.0 ? 1.0-smoothstep(0.05, 1.45, p.z) : 1.0;
  return rev*dis*clamp(p.w, 0.0, 1.0);
}
float veilAt(sampler2D tx, vec2 uv, vec4 p, vec2 bnd, vec2 off){
  vec2 q = uv+off;
  if(q.y<0.0 || q.y>1.0) return 0.0;
  return texture(tx, q).b*veilVis(q, p, bnd);
}
float wordMask(sampler2D tx, vec2 uv, vec4 p, vec2 bnd, vec2 off){
  uv += off;
  if(uv.y<0.0 || uv.y>1.0) return 0.0;
  float od = clamp((uv.x-bnd.x)/(bnd.y-bnd.x), 0.0, 1.0);
  float arrive = od*(p.y-1.35)+1.35;
  float rev = smoothstep(-0.25, 0.75, p.x-arrive);
  float er = vnoise(uv*vec2(uAspect,1.0)*70.0);
  float dis = 1.0-smoothstep(0.0, 1.0, (p.z-er*0.9)/0.8);
  return texture(tx, uv).g*rev*dis*p.w;
}
// the letters themselves (sharp channel), revealed and dissolved exactly as TEXT_FS draws them: per-text colour
float inkMask(sampler2D tx, vec2 uv, vec4 p, vec2 bnd, vec2 off){
  uv += off;
  if(uv.y<0.0 || uv.y>1.0) return 0.0;
  float od = clamp((uv.x-bnd.x)/(bnd.y-bnd.x), 0.0, 1.0);
  float arrive = od*(p.y-1.35)+1.35;
  float rev = smoothstep(-0.25, 0.75, p.x-arrive);
  float er = vnoise(uv*vec2(uAspect,1.0)*70.0);
  float dis = 1.0-smoothstep(0.0, 1.0, (p.z-er*0.9)/0.8);
  return clamp(texture(tx, uv).r*1.04, 0.0, 1.0)*rev*dis*clamp(p.w, 0.0, 1.0);
}
// where any text (expression, title, end card, fragment, credit) lies: reflections and light waves skip it
float creditField(vec2 q){
  vec2 cuv = (q-uCredit.xy)/uCredit.z + uC0;
  if(cuv.x<=0.0 || cuv.x>=1.0 || cuv.y<=0.0 || cuv.y>=1.0) return 0.0;
  return texture(uTextC, cuv).b*min(uCredit.w*1.7, 1.0);
}
float textField(vec2 q){
  if(q.y<0.0 || q.y>1.0) return 0.0;
  float m = max(texture(uTextA, q).b*uShade.x, texture(uTextB, q).b*uShade.y);
  return smoothstep(0.0, 0.6, max(m, creditField(q)));
}
vec3 procedural(vec2 sv){
  vec2 uv = vec2((sv.x-0.5)*uZoom+0.5, (sv.y-uHorizon)*uZoom+uHorizon);
  vec3 col;
  vec3 hz = texture(uSky, vec2(uv.x, uHorizon+0.012)).rgb;
  if(uv.y>=uHorizon){
    col = scene(uv);
  } else {
    float d = (uHorizon-uv.y)/uHorizon;
    float wob = (vnoise(vec2(uv.x*uAspect*24.0, uv.y*210.0-uT*0.85))-0.5)*0.011*(0.22+d)
              + sin(uv.y*240.0+uT*1.2)*0.0010;
    vec2 ruv = vec2(uv.x+wob, uHorizon+(uHorizon-uv.y)*1.22+wob*0.4);
    col = scene(ruv);
    col *= mix(mix(0.82, 0.95, uTheme), mix(0.30, 0.74, uTheme), pow(d,0.75));
    // reflected lights
    float rf = (1.0-d)*(1.0-d);
    float ck = calmK(sv.y);
    col += (texture(uB2, ruv).rgb*0.16 + texture(uB3, ruv).rgb*0.26 + texture(uB4, ruv).rgb*0.30)*rf*mix(0.25, 1.0, ck)
           *(1.0-textField(ruv));   // words are not mirrored in the lake
    // glitter under the low sun
    float sx = (uv.x-uSun.x)*uAspect;
    float path = exp(-sx*sx/(0.004+0.09*d*d));
    float gl = pow(vnoise(vec2(uv.x*uAspect*260.0, uv.y*900.0+uT*2.6)), 7.0);
    col += uGlow*uSunInt*path*(0.10+2.6*gl*ck)*(0.5+0.8*uHi)*smoothstep(0.0,0.05,d)*0.55;
    // each note is a ring on the water
    for(int i=0;i<uNRings;i++){
      vec4 rg = uRings[i];
      vec2 q = vec2((uv.x-rg.x)*uAspect, (uv.y-rg.y)*3.6);
      float rr = length(q);
      float rad = 0.012+rg.z*0.055;
      float ring = exp(-pow((rr-rad)/0.0035,2.0)) + 0.5*exp(-pow((rr-rad*0.55)/0.0035,2.0));
      col += (uGlow*0.6+hz*0.8)*ring*rg.w*exp(-rg.z*1.25)*0.40*smoothstep(0.0,0.12,rg.z)*ck;
    }
    col = mix(col, hz*0.9, exp(-d*42.0)*0.55);
  }
  return col;
}
// ---- scene plates: a painted picture that slowly moves, with an optional shimmering lake
vec3 plateColor(sampler2D tx, vec2 sv, vec4 view, vec4 wat, float calmG){
  vec2 puv = view.xy + (sv-0.5)/view.z;
  float wl = wat.y;
  vec3 extra = vec3(0.0);
  float water = (wat.x>0.5 && puv.y<wl && puv.y>wat.w) ? 1.0 : 0.0;
  float d = clamp((wl-puv.y)/max(wl,0.05), 0.0, 1.0);
  if(water>0.5){
    float wob = (vnoise(vec2(puv.x*uAspect*30.0, puv.y*260.0-uT*0.9))-0.5)*0.008*(0.25+d)*wat.z
              + sin(puv.y*300.0+uT*1.3)*0.0008*wat.z;
    wob *= smoothstep(wat.w, wat.w+0.06, puv.y);       // calm again at the bottom of the water band
    puv += vec2(wob, wob*0.3);
    float wls = 0.5+(wl-view.y)*view.z;              // the water line on screen
    vec2 ruv = vec2(sv.x+wob*view.z, 2.0*wls-sv.y);
    float rf = (1.0-d)*(1.0-d)*mix(0.25, 1.0, calmK(sv.y));
    rf *= 1.0-textField(ruv);                           // words are not mirrored in the lake
    extra += (textureLod(uB2, ruv, 0.0).rgb*0.16 + textureLod(uB3, ruv, 0.0).rgb*0.26 + textureLod(uB4, ruv, 0.0).rgb*0.30)*rf*wat.z;
  }
  puv = clamp(puv, vec2(0.001), vec2(0.999));
  vec3 s = textureLod(tx, puv, 0.0).rgb;
  vec3 halo = textureLod(tx, puv, 5.5).rgb;
  float l = dot(s, vec3(0.2126,0.7152,0.0722));
  s = mix(vec3(l), s, 0.86);                          // the engine's colour lift is added back later
  vec3 lin = invTone(pow(s, vec3(2.2)))*view.w;
  lin += max(pow(halo, vec3(2.2))-0.22, 0.0)*0.40*view.w;   // soft halation round the bright parts
  if(water>0.5){
    float gl = pow(vnoise(vec2(puv.x*uAspect*170.0+uT*0.15, puv.y*900.0+uT*1.6)), 16.0);
    lin += vec3(1.0,0.93,0.8)*gl*smoothstep(0.50,0.95,l)*1.6*wat.z*(0.3+d)*mix(0.3, 1.0, calmK(sv.y));
  }
  // BOTTOM_CALM: the plate's own bright reflections in the lower third come down too (gain calmG at the bottom)
  lin *= mix(1.0, mix(calmG, 1.0, smoothstep(0.0, 0.30, sv.y)), uCalm);
  return lin+extra;
}
vec3 toneF(vec3 x){ x = max(x, 0.0); return (x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14); }
float trMask(vec4 tr, vec2 sv, out float edge){
  int m = int(tr.x+0.5); float p = tr.y; edge = 0.0;
  if(m==1){       // dissolve with a glowing edge
    float n = fbm(sv*vec2(uAspect,1.0)*2.6+3.7);
    float f = p*1.3-0.15;
    edge = exp(-pow((f-n)/0.004,2.0))*step(0.001,p)*step(p,0.999)*tr.z;
    return smoothstep(n-0.04, n+0.04, f);
  }
  if(m==3){       // a ripple that spreads from a point
    float r = length((sv-tr.zw)*vec2(uAspect,1.0));
    float f = p*2.3;
    edge = exp(-pow((r-f)/0.010,2.0))*(1.0-p)*0.45;
    return smoothstep(f, f-0.18, r);
  }
  if(m==2) return smoothstep(0.30, 0.70, p);   // bloom: the change hides inside a flash of light
  return p*p*(3.0-2.0*p);                       // fade and push
}
vec3 applyPlate(vec3 col, sampler2D tx, vec2 sv, vec4 view, vec4 wat, vec4 tr, float alpha, float calmG){
  float edge;
  float m = trMask(tr, sv, edge);
  vec2 s2 = sv;
  if(int(tr.x+0.5)==3){
    vec2 q = (sv-tr.zw)*vec2(uAspect,1.0); float r = length(q); float f = tr.y*2.3;
    s2 += (q/max(r,1e-4))/vec2(uAspect,1.0)*0.012*sin((r-f)*90.0)*exp(-pow((r-f)/0.07,2.0))*(1.0-tr.y);
  }
  float a = clamp(m*alpha, 0.0, 1.0);
  vec3 pc = plateColor(tx, s2, view, wat, calmG);
  if(a>=0.999) col = pc;
  else if(a>0.001) col = invTone(mix(toneF(col), toneF(pc), a));   // blend as seen, not in light units
  col += uGlow*edge*alpha*0.9;
  return col;
}
vec3 background(vec2 sv){
  vec3 col = procedural(sv);
  if(uPlN>0) col = applyPlate(col, uPlA, sv, uPlAView, uPlAWat, uPlATr, uPlAAlpha, uPlACalm);
  if(uPlN>1) col = applyPlate(col, uPlB, sv, uPlBView, uPlBWat, uPlBTr, uPlBAlpha, uPlBCalm);
  return col;
}
void main(){
  vec2 sv = vUV;
  // ---- shards: the sky breaks into floating pieces of glass (and can be mended with gold)
  vec2 bsv = sv;
  float shA = 0.0, shE = 1.0, shH = 0.0, shLow = 0.0;
  if(uShards.x>0.001 || uShards.y>0.001){
    vec2 q = vec2(sv.x*uAspect, sv.y)*uShards.z;
    vec2 cell, toC;
    shE = voro(q, cell, toC);
    shH = hash21(cell*1.31+0.7);
    shLow = smoothstep(uShards.w, uShards.w+0.16, sv.y);
    shA = uShards.x*shLow;
    if(shA>0.0){
      vec2 h2 = hash22(cell*2.17+1.3);
      float ang = ((shH-0.5)*0.50 + 0.07*sin(uT*0.45+h2.x*6.28))*shA;
      vec2 rel = -toC;
      float cs = cos(ang), sn = sin(ang);
      vec2 rr = vec2(cs*rel.x-sn*rel.y, sn*rel.x+cs*rel.y);
      vec2 drift = ((h2-0.5)*vec2(0.80,0.55) + 0.14*vec2(sin(uT*0.31+h2.y*9.0), cos(uT*0.27+h2.x*9.0)))*shA;
      vec2 qq = cell+hash22(cell)+rr+drift;
      bsv = vec2(qq.x/uAspect, qq.y)/uShards.z;
    }
  }
  // ---- lake ripples (engine/water.py, RIPPLES): rings bend the water and its reflections (water_shaders.RIP_GLSL)
  if(uNRip>0 && bsv.y<uRipWL){
    vec2 rd = vec2(0.0);
    for(int i=0;i<uNRip;i++){
      vec4 r = uRip[i];
      float k = 0.35+1.6*clamp((uRipWL-r.y)/max(uRipWL,0.05), 0.0, 1.0);
      vec2 q = vec2((bsv.x-r.x)*uAspect, (bsv.y-r.y)*3.2)/k;
      float rr = length(q), e = (rr-r.z*0.075)/0.03;
      vec2 dir = q/max(rr, 1e-4);
      rd += vec2(dir.x, dir.y*0.6)*k*0.006*r.w*exp(-r.z/1.6)*smoothstep(0.0, 0.15, r.z)*exp(-e*e)*sin(e*4.0);
    }
    bsv += rd*smoothstep(0.0, 0.012, uRipWL-bsv.y)*mix(0.35, 1.0, calmK(bsv.y));
  }
  vec3 col = background(bsv);
  if(shA>0.0){
    float gw = 0.0075*uShards.x;
    float gap = (1.0-smoothstep(gw*0.4, gw, shE))*shLow;
    float rim = exp(-max(shE-gw,0.0)/0.0045)*shA;
    vec2 cell2, toC2;
    voro(vec2(sv.x*uAspect, sv.y)*uShards.z, cell2, toC2);
    float facing = 0.5+0.5*dot(normalize(-toC2+1e-5), normalize(vec2(-0.6,0.8)));
    col *= mix(1.0, 0.80+0.45*shH, shA);
    col += uGlow*0.06*shA*smoothstep(0.6,1.0,shH);
    col = mix(col, col*0.45, gap);
    col += (uGlow*0.30 + vec3(0.55,0.65,0.90)*0.14)*rim*(0.25+0.75*facing)*(1.0-gap);
  }
  if(uShards.y>0.001){
    float seam = exp(-shE/0.0018)*1.0 + exp(-shE/0.010)*0.08;
    float glint = pow(vnoise(vec2(sv.x*uAspect, sv.y)*uShards.z*18.0+vec2(uT*0.6,0.0)), 8.0);
    col += uShardCol*uShards.y*shLow*seam*(0.55+4.0*glint);
  }
  // ---- ice over the lake, which can thaw
  if(uIce.x>0.001 && sv.y<uIce.y){
    float d = (uIce.y-sv.y)/uIce.y;
    float z = 1.0/(d+0.07);
    vec2 g = vec2((sv.x-0.5)*uAspect*z, z)*1.3;
    vec2 cc, tc;
    float e1 = voro(g, cc, tc);
    float e2 = voro(g*2.6+vec2(3.1,7.7), cc, tc);
    float crack = (exp(-e1/0.010)*0.55 + exp(-e2/0.006)*0.25)*(0.25+0.75*smoothstep(0.35,0.75,vnoise(g*2.2+7.0)));
    float frost = fbm(g*2.3)*0.65 + fbm(g*8.0+5.0)*0.35;
    float melt = fbm(g*0.55+vec2(9.0,2.0));
    float th = mix(0.95, -0.05, uIce.x);
    float near = smoothstep(0.0, 0.015, d);
    float iceM = smoothstep(th-0.025, th+0.025, melt)*near;
    float rimT = exp(-pow((melt-th)/0.018, 2.0))*step(0.02, 1.0-uIce.x)*near;
    vec3 iceC = col*0.42 + uIceCol*(0.05 + 0.22*frost*frost) + uIceCol*crack*0.24*(1.0-0.5*d);
    float sxx = (sv.x-uSun.x)*uAspect;
    iceC += uGlow*uSunInt*exp(-sxx*sxx/(0.01+0.05*d*d))*0.10*(0.5+frost);
    col = mix(col, iceC, iceM*uIce.z);
    col += uThawCol*rimT*0.9*mix(0.3, 1.0, calmK(sv.y));
  }
  if(uIce.w>0.001){
    vec2 q = (sv-0.5)*vec2(uAspect,1.0);
    float r = length(q)/length(vec2(uAspect*0.5,0.5));
    float fr = smoothstep(0.62, 1.0, r+0.22*(fbm(sv*vec2(uAspect,1.0)*6.0)-0.5));
    vec2 fq = sv*vec2(uAspect,1.0);
    float fea = fbm(fq*9.0+vec2(fbm3(fq*3.0)*2.0, 0.0));
    float crys = smoothstep(0.50, 0.85, fea) + 0.6*pow(vnoise(fq*140.0), 10.0);
    col = mix(col, col*0.70 + uIceCol*(0.06+0.30*crys), fr*uIce.w);
  }
  // ---- a golden field of light grain across the lower land: rows of glowing grain heads in perspective
  if(uField.x>0.001 && sv.y<uField.y){
    float d = (uField.y-sv.y)/uField.y;               // 0 at the far edge, 1 at the bottom of the screen
    float z = 1.0/(d+0.05);
    float wave = 0.5+0.5*sin(z*0.9 - uT*uField.z + sv.x*uAspect*2.2 + 1.4*fbm3(vec2(sv.x*3.0, z*0.2)+uT*0.04));
    wave = wave*wave*wave;
    float row = z*7.0;
    float rid = floor(row), rf = fract(row);
    float sway = (wave-0.3)*0.22 + 0.06*sin(uT*1.3+rid);
    float cx = sv.x*uAspect*36.0*z/7.0*3.0 + rid*0.37;
    float cid = floor(cx);
    float fx = fract(cx)-0.5 - sway*(1.0-rf);
    float h = hash21(vec2(cid, rid));
    float on = step(0.25, h);
    float head = exp(-fx*fx/0.035 - pow(rf-0.30,2.0)/0.050)*on;
    float stalk = exp(-fx*fx/0.0025)*smoothstep(0.30,0.95,rf)*on*0.35;
    float far = smoothstep(0.0, 0.25, d);
    vec3 fc = uFieldCol*((0.10+0.90*wave)*(head*(0.6+0.8*h)) + stalk*0.4)*far;
    fc += uFieldCol*(0.05+0.10*wave)*(1.0-far*0.5);   // a soft golden ground under the grain
    float cover = uField.x*smoothstep(0.0, 0.12, d);
    fc *= 1.0-0.50*smoothstep(0.55, 1.0, d);          // the bottom stays calmer for the performers
    fc = mix(fc, uFieldCol*0.06, (1.0-calmK(sv.y))*0.75);   // and calmer still with BOTTOM_CALM
    col = mix(col, col*0.30+fc, cover);
    col += uFieldCol*0.12*exp(-d*12.0)*uField.x;       // light haze along the far edge of the field
  }
  col += uGlow*uFlash*(0.55+0.45*exp(-length((sv-vec2(0.5,0.55))*vec2(uAspect,1.0))*1.6));
  vec2 uv = vec2((sv.x-0.5)*uZoom+0.5, (sv.y-uHorizon)*uZoom+uHorizon);
  // waves of light when a light is lit
  for(int i=0;i<uNWaves;i++){
    vec4 w = uWaves[i];
    vec2 q = (uv-w.yz)*vec2(uAspect,1.0);
    float rr = length(q);
    float front = exp(-pow((rr-w.x*0.42)/0.09,2.0))*exp(-w.x*0.75);
    float bloom = exp(-rr*rr/0.10)*exp(-w.x*1.3);
    col += uGlow*w.w*(front*0.50+bloom*0.30)*calmK(sv.y)*(1.0-textField(sv));
  }
  // soft shadows so the words stay readable against bright skies
  uv = sv;
  float sh = max(veilAt(uTextA, uv, uTxA, uBndA, uOffA)*uShade.x, veilAt(uTextB, uv, uTxB, uBndB, uOffB)*uShade.y);
  vec2 cuv = (uv-uCredit.xy)/uCredit.z + uC0;
  vec3 ct = vec3(0.0);
  if(cuv.x>0.0 && cuv.x<1.0 && cuv.y>0.0 && cuv.y<1.0) ct = texture(uTextC, cuv).rgb;
  col *= 1.0-min(0.56*uShadeK*sh, 0.92);
  // bright scenery (a dawn sky, a sunlit lake) is brought down to a fixed level behind all text, so white words
  // always stand on a calm, darker veil (Astra round 1, finding 3). The veil also loses most of its colour, so
  // a dimmed sun turns a quiet warm grey instead of olive or brown.
  float shAll = max(sh, ct.b*min(uCredit.w*1.7, 1.0));
  float lumB = dot(col, vec3(0.2126,0.7152,0.0722));
  float capB = 0.065/max(uShadeK, 0.5);
  // TEXT_SHADOW 0 is truly zero: no cap on bright scenery and no dark round the credit. zk is 1 (unchanged) from
  // TEXT_SHADOW 0.05 up, and fades to 0 below it so a Track can ease the protection away without a jump.
  float zk = clamp(uShadeK*20.0, 0.0, 1.0);
  float vk = smoothstep(0.0, 0.85, shAll)*zk;
  float sc = mix(1.0, min(capB/max(lumB,1e-5), 1.0), vk*0.92);
  col *= sc;
  float lumD = dot(col, vec3(0.2126,0.7152,0.0722));
  col = mix(col, vec3(lumD)*vec3(1.08,0.96,0.88), vk*min((1.0-sc)*2.2, 1.0)*0.85);
  float tight = max(wordMask(uTextA, uv, uTxA, uBndA, uOffA), wordMask(uTextB, uv, uTxB, uBndB, uOffB));
  col *= 1.0-min(0.50*uShadeK*tight, 0.92);
  col *= 1.0-(ct.g*0.50+ct.b*0.34)*uCredit.w*zk;
  if(uLeafK>0.0){   // leaves are painted green over the scene (light alone only brightens a bright sky)
    vec4 lf = texture(uLeafT, uv);
    float k = uLeafK*(1.0-textField(uv));
    col = col*(1.0-lf.a*k) + lf.rgb*k;
  }
  vec3 L = texture(uL, uv).rgb;
  vec3 bl = texture(uB1,uv).rgb*0.34 + texture(uB2,uv).rgb*0.28 + texture(uB3,uv).rgb*0.24 + texture(uB4,uv).rgb*0.22;
  col += L + bl*uBloom;
  // lens: vignette, exposure, filmic curve
  vec2 vq = (uv-0.5)*vec2(1.15,1.0);
  col *= mix(1.0, mix(0.62, 0.90, uTheme), smoothstep(0.30,1.0,length(vq)*1.35));
  col *= uExposure*uFade;
  col = (col*(2.51*col+0.03))/(col*(2.43*col+0.59)+0.14);
  col = pow(clamp(col,0.0,1.0), vec3(1.0/2.2));
  float luma = dot(col, vec3(0.2126,0.7152,0.0722));
  col = clamp(mix(vec3(luma), col, 1.18), 0.0, 1.0);
  col = mix(col, col*col*(3.0-2.0*col), 0.24);
  // per-text colour (navy, coral...): the letters are painted in exactly that colour over the scene and its glow
  if(uInkA.w>0.0) col = mix(col, uInkA.rgb*uFade, inkMask(uTextA, uv, uTxA, uBndA, uOffA)*uInkA.w);
  if(uInkB.w>0.0) col = mix(col, uInkB.rgb*uFade, inkMask(uTextB, uv, uTxB, uBndB, uOffB)*uInkB.w);
  if(uInkC.w>0.0) col = mix(col, uInkC.rgb*uFade, clamp(ct.r*1.04, 0.0, 1.0)*min(uCredit.w, 1.0)*uInkC.w);
  // fine grain keeps the dark gradients smooth on a big screen
  vec2 px = gl_FragCoord.xy;
  float n1 = hash21(px+vec2(uFrame*1.37, uFrame*0.73));
  float n2 = hash21(px.yx+vec2(uFrame*2.11+17.0, 5.0));
  col += (n1+n2-1.0)*(1.15/255.0);
  o = vec4(col,1.0);
}
"""
