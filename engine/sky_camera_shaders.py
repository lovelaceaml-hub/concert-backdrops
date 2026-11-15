"""GLSL for the sky and camera layers (engine/sky_camera.py): moving 3D clouds, god rays, the camera background
with parallax, and near motes. Nothing here runs unless a song sets one of the keys (see UPGRADE-HOWTO.md, I7)."""
from shaders import NOISE

# ---------------------------------------------------------------- camera
# A layer of depth w (0 = infinitely far, 1 = the shore of the lake, above 1 = nearer than the lake) moves with
# the camera by w (PARALLAX = 1) or all layers move as one (PARALLAX = 0). Screen <-> layer coordinates.
CAM = """
uniform vec4 uCam;     // zoom, pan, crane, parallax
uniform vec2 uCamC;    // the point the camera pushes in on
uniform float uBaseZ, uHorizon, uAspect;
const float W_SKY = 0.12, W_CLOUD_HI = 0.24, W_CLOUD_LO = 0.40;
const float W_FAR = 0.45, W_MID = 0.62, W_NEAR = 0.80, W_LAKE = 1.15, W_MOTE = 1.45;
float camK(float w){ return 1.0+(w-1.0)*uCam.w; }
vec2 toLayer(vec2 sv, float w){
  vec2 u = vec2((sv.x-0.5)*uBaseZ+0.5, (sv.y-uHorizon)*uBaseZ+uHorizon);
  float k = camK(w); float z = max(1.0+(uCam.x-1.0)*k, 0.2);
  return uCamC+(u-uCamC)/z+uCam.yz*k;
}
vec2 toScreen(vec2 q, float w){
  float k = camK(w); float z = max(1.0+(uCam.x-1.0)*k, 0.2);
  vec2 u = uCamC+(q-uCamC-uCam.yz*k)*z;
  return vec2((u.x-0.5)/uBaseZ+0.5, (u.y-uHorizon)/uBaseZ+uHorizon);
}
"""

# the soft field round any text (same veil timing as the composite): clouds thin out there, nothing dark appears
TEXTF = """
uniform sampler2D uTextA, uTextB, uTextC;
uniform vec2 uShade; uniform vec4 uTxA, uTxB, uCredit; uniform vec2 uBndA, uBndB, uOffA, uOffB, uC0;
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
float textF(vec2 q){
  float m = max(veilAt(uTextA, q, uTxA, uBndA, uOffA)*uShade.x, veilAt(uTextB, q, uTxB, uBndB, uOffB)*uShade.y);
  vec2 cuv = (q-uCredit.xy)/uCredit.z + uC0;
  if(cuv.x>0.0 && cuv.x<1.0 && cuv.y>0.0 && cuv.y<1.0) m = max(m, texture(uTextC, cuv).b*min(uCredit.w*1.7, 1.0));
  return smoothstep(0.0, 0.6, m);
}
"""

RIDGES = """
uniform sampler2D uRidge;
float ridged1(float x, float seed){
  float sum=0.0, a=0.5, f=1.0;
  for(int i=0;i<5;i++){
    float n = vnoise(vec2(x*f+seed*(1.0+float(i)), seed*3.1+float(i)*7.0));
    sum += a*(1.0-abs(2.0*n-1.0)); a*=0.5; f*=2.13;
  }
  return sum;
}
float ridgeFar(float x){ return uHorizon + texture(uRidge, vec2(x,0.5)).r; }
float ridgeMid(float x){ return uHorizon + 0.010 + 0.105*pow(ridged1(x*2.1, 11.0), 1.7); }
float ridgeNear(float x){ return uHorizon + 0.003 + 0.070*pow(ridged1(x*3.3+5.0, 3.7), 2.0) + 0.0022*vnoise(vec2(x*520.0,1.0)); }
"""

# ---------------------------------------------------------------- clouds
CLOUDD = """
uniform float uT, uCloudSpd, uCloudAmt;
// density of one cloud layer at layer coordinates p: a sky plane seen in perspective (small and many near the
// horizon, big overhead), drifting with the wind and slowly changing shape (domain warp that moves in time)
float cloudD(vec2 p, float layer){
  float hh = p.y-uHorizon;
  if(hh<=0.0) return 0.0;
  float z = 1.0/(hh+0.075);
  vec2 P = vec2((p.x-0.5)*uAspect*z*0.55, z*0.85) + vec2(layer*13.7, layer*5.1);
  float s = uT*uCloudSpd;
  vec2 q = P + vec2(s*0.030*(1.0+0.7*layer), -s*0.010);
  vec2 wv = vec2(fbm3(q*0.75+vec2(0.0, s*0.021)), fbm3(q*0.75+vec2(5.2, 1.3-s*0.017)));
  float n = fbm(q*vec2(0.85,1.35)*mix(1.0,1.6,layer) + 1.8*wv + vec2(s*0.012, 0.0));
  float cov = mix(0.66, 0.42, clamp(uCloudAmt, 0.0, 1.5)/1.5) + 0.04*layer;
  float d = smoothstep(cov, cov+mix(0.24,0.15,layer), n);
  d *= smoothstep(0.0, 0.035, hh);
  d *= 1.0-0.6*layer*smoothstep(0.45, 0.70, hh);   // the low layer thins out overhead
  return d;
}
"""

CLOUDS_FS = "#version 330\n" + NOISE + CAM + TEXTF + CLOUDD + """
in vec2 vUV;
layout(location=0) out vec4 o;    // premultiplied cloud colour, laid over the sky
layout(location=1) out vec4 o2;   // r: raw density (no text thinning), for the god rays
uniform vec3 uSkyTop, uSkyMid, uSkyHor, uGlow;
uniform vec2 uSunS; uniform float uSunInt, uLight, uSilver;
vec4 layerC(vec2 sv, float wc, float layer, out float dens){
  vec2 p = toLayer(sv, wc);
  float d = cloudD(p, layer);
  dens = d;
  if(d<=0.001) return vec4(0.0);
  vec2 toS = uSunS-sv;
  float rs = length(toS*vec2(uAspect,1.0));
  vec2 dir = toS/max(length(toS), 1e-4);
  float d2 = cloudD(toLayer(sv+dir*0.016, wc), layer);
  float facing = clamp(0.5+(d-d2)*2.8, 0.0, 1.0);          // the side that faces the sun
  float hh = clamp((p.y-uHorizon)/(1.0-uHorizon), 0.0, 1.0);
  vec3 skyc = mix(uSkyHor, uSkyMid, smoothstep(0.0,0.42,hh));
  skyc = mix(skyc, uSkyTop, smoothstep(0.26,0.95,hh));
  // the body is never much darker than the sky behind it (no dark shapes), a little lighter in a dark sky
  vec3 body = skyc*0.80 + uSkyHor*0.20 + uSkyMid*0.08;
  float sunK = clamp(uSunInt, 0.0, 1.6);
  vec3 lit = uGlow*sunK*(0.06+0.55*exp(-rs*2.0))*facing*uLight;
  float edge = smoothstep(0.02,0.28,d)*(1.0-smoothstep(0.28,0.85,d));
  vec3 rim = uGlow*sunK*edge*(0.30*exp(-rs*1.2)+2.4*exp(-rs*4.0))*uLight*uSilver*(0.4+0.6*facing);
  vec3 c = body*(0.86+0.28*(1.0-d)) + lit + rim;
  float a = d*clamp(uCloudAmt, 0.0, 1.0)*0.92;
  return vec4(c*a, a);
}
void main(){
  vec2 s = vUV;                          // sky texture coordinates
  vec2 sv = toScreen(s, W_SKY);          // where that is on screen
  float dh, dl;
  vec4 hi = layerC(sv, W_CLOUD_HI, 0.0, dh);
  vec4 lo = layerC(sv, W_CLOUD_LO, 1.0, dl);
  vec4 c = lo + hi*(1.0-lo.a);
  c *= 1.0-0.90*textF(sv);               // clouds thin out round the words
  o = c;
  float amt = clamp(uCloudAmt, 0.0, 1.0);
  o2 = vec4(1.0-(1.0-dh*amt)*(1.0-dl*amt), 0.0, 0.0, 1.0);
}
"""

BLIT_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex;
void main(){ o = texture(uTex, vUV); }
"""

# ---------------------------------------------------------------- god rays
OCC_FS = "#version 330\n" + NOISE + CAM + RIDGES + """
in vec2 vUV; out vec4 o;
uniform sampler2D uCloudD; uniform float uCloudOn;
uniform vec2 uSrc; uniform float uSrcSize;
void main(){
  vec2 sv = vUV;
  float r = length((sv-uSrc)*vec2(uAspect,1.0));
  float e = exp(-r*r/(uSrcSize*uSrcSize)) + 0.55*exp(-r/(uSrcSize*3.2));
  if(uCloudOn>0.5) e *= 1.0-clamp(texture(uCloudD, toLayer(sv, W_SKY)).r*1.6, 0.0, 1.0);
  vec2 uf = toLayer(sv, W_FAR), um = toLayer(sv, W_MID), un = toLayer(sv, W_NEAR);
  float open = smoothstep(ridgeFar(uf.x)-0.003, ridgeFar(uf.x)+0.003, uf.y);
  open *= smoothstep(ridgeMid(um.x)-0.003, ridgeMid(um.x)+0.003, um.y);
  open *= smoothstep(ridgeNear(un.x)-0.003, ridgeNear(un.x)+0.003, un.y);
  o = vec4(e*open, 0.0, 0.0, 1.0);
}
"""

RADIAL_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uOcc; uniform vec2 uSrc; uniform float uDecay, uAspect;
const int N = 96;
void main(){
  vec2 dl = (vUV-uSrc)*(0.96/float(N));
  vec2 p = vUV - dl*hash21(gl_FragCoord.xy*0.731);
  float ill = 1.0, acc = 0.0;
  for(int i=0;i<N;i++){ acc += texture(uOcc, p).r*ill; ill *= uDecay; p -= dl; }
  float r = length((vUV-uSrc)*vec2(uAspect,1.0));
  o = vec4(acc*(1.0-uDecay)*mix(0.35, 1.0, smoothstep(0.02, 0.22, r)), 0.0, 0.0, 1.0);
}
"""

RAYS_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uRays; uniform vec3 uCol; uniform float uAmt, uHorizon, uCalm, uCalmY;   // uHorizon: on screen now
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  float r = texture(uRays, vUV).r;
  float low = mix(0.06, 1.0, smoothstep(uHorizon-0.01, uHorizon+0.10, vUV.y));   // shafts live in the air above the land
  o = vec4(uCol*uAmt*r*low*calmK(vUV.y), 1.0);
}
"""

# ---------------------------------------------------------------- the camera background (parallax)
# The engine's own sky, three mountain ranges and lake (shaders.py scene() and procedural()), each layer seen
# through the camera at its own depth. The composite uses this picture in place of procedural() when uCamOn is 1.
CAMBG_FS = "#version 330\n" + NOISE + CAM + RIDGES + """
in vec2 vUV; out vec4 o;
uniform sampler2D uSky, uB2, uB3, uB4, uTextA, uTextB, uTextC;
uniform float uT, uProg, uTrail, uHi, uSunInt;
uniform vec3 uMtn, uGlow, uTrailCol;
uniform vec2 uSunS;
uniform vec2 uShade; uniform vec4 uCredit; uniform vec2 uC0;
uniform int uNRings; uniform vec4 uRings[16];
uniform float uCalm, uCalmY;
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
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
vec3 sceneCam(vec2 sv){
  float aa = 0.0010;
  vec2 us = toLayer(sv, W_SKY);
  vec3 c = texture(uSky, us).rgb;
  vec3 hz = texture(uSky, vec2(us.x, uHorizon+0.012)).rgb;
  // the far range (the loudness of the whole song)
  vec2 uf = toLayer(sv, W_FAR);
  float hh = max(uf.y-uHorizon, 0.0);
  float ry = ridgeFar(uf.x);
  float m1 = smoothstep(ry+aa, ry-aa, uf.y);
  float lit = smoothstep(uProg+0.003, uProg-0.014, uf.x);
  float depth = clamp(hh/0.17, 0.0, 1.0);
  vec3 far = mix(uMtn*1.5, hz, 0.74-0.30*depth);
  far += uTrailCol*uTrail*lit*0.030*depth;
  c = mix(c, far, m1);
  float dr = uf.y-ry;
  float rim = exp(-abs(dr)*900.0)*0.85 + exp(-max(dr,0.0)*95.0)*0.13*step(0.0,dr);
  c += uTrailCol*uTrail*lit*rim;
  c += uTrailCol*0.03*exp(-abs(dr)*900.0)*(1.0-lit);
  c = mix(c, hz*1.04, exp(-hh/0.030)*0.30);
  // the middle range
  vec2 um = toLayer(sv, W_MID);
  float y2 = ridgeMid(um.x);
  float m2 = smoothstep(y2+aa, y2-aa, um.y);
  float d2 = clamp((y2-um.y)/0.07, 0.0, 1.0);
  c = mix(c, mix(uMtn*0.85, hz, 0.20+0.22*d2), m2);
  c = mix(c, hz*1.02, exp(-max(um.y-uHorizon, 0.0)/0.016)*0.26);
  // the near range
  vec2 un = toLayer(sv, W_NEAR);
  float y3 = ridgeNear(un.x);
  float m3 = smoothstep(y3+aa, y3-aa, un.y);
  c = mix(c, mix(uMtn*0.30, hz, 0.05), m3);
  return c;
}
void main(){
  vec2 sv = vUV;
  float ds = clamp((uHorizon-sv.y)/uHorizon, 0.0, 1.0);
  float wl = mix(W_NEAR, W_LAKE, ds);              // the lake comes nearer towards the bottom of the screen
  vec2 lu = toLayer(sv, wl);
  vec3 col;
  if(lu.y>=uHorizon){
    col = sceneCam(sv);
  } else {
    vec3 hz = texture(uSky, vec2(toLayer(sv, W_SKY).x, uHorizon+0.012)).rgb;
    float d = (uHorizon-lu.y)/uHorizon;
    float wob = (vnoise(vec2(lu.x*uAspect*24.0, lu.y*210.0-uT*0.85))-0.5)*0.011*(0.22+d)
              + sin(lu.y*240.0+uT*1.2)*0.0010;
    vec2 lr = vec2(lu.x+wob, uHorizon+(uHorizon-lu.y)*1.22+wob*0.4);
    vec2 svR = toScreen(lr, W_NEAR);
    col = sceneCam(svR);
    col *= mix(0.82, 0.30, pow(d,0.75));
    float rf = (1.0-d)*(1.0-d);
    float ck = calmK(sv.y);
    col += (texture(uB2, svR).rgb*0.16 + texture(uB3, svR).rgb*0.26 + texture(uB4, svR).rgb*0.30)*rf*mix(0.25, 1.0, ck)
           *(1.0-textField(svR));
    float sunL = toLayer(vec2(uSunS.x, sv.y), wl).x;
    float sx = (lu.x-sunL)*uAspect;
    float path = exp(-sx*sx/(0.004+0.09*d*d));
    float gl = pow(vnoise(vec2(lu.x*uAspect*260.0, lu.y*900.0+uT*2.6)), 7.0);
    col += uGlow*uSunInt*path*(0.10+2.6*gl*ck)*(0.5+0.8*uHi)*smoothstep(0.0,0.05,d)*0.55;
    for(int i=0;i<uNRings;i++){
      vec4 rg = uRings[i];
      vec2 q = vec2((lu.x-rg.x)*uAspect, (lu.y-rg.y)*3.6);
      float rr = length(q);
      float rad = 0.012+rg.z*0.055;
      float ring = exp(-pow((rr-rad)/0.0035,2.0)) + 0.5*exp(-pow((rr-rad*0.55)/0.0035,2.0));
      col += (uGlow*0.6+hz*0.8)*ring*rg.w*exp(-rg.z*1.25)*0.40*smoothstep(0.0,0.12,rg.z)*ck;
    }
    col = mix(col, hz*0.9, exp(-d*42.0)*0.55);
  }
  o = vec4(col, 1.0);
}
"""

# ---------------------------------------------------------------- near motes (the nearest layer)
NMOTE_VS = "#version 330\n" + CAM + """
in vec4 aSeed;
uniform float uT, uAmt, uPx, uCalm, uCalmY;
out float vA;
float calmK(float y){ return 1.0-uCalm*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, y)); }
void main(){
  float per = 46.0*(0.7+0.6*aSeed.x);
  float ph = fract(uT/per + aSeed.y*5.31);
  vec2 q = vec2(aSeed.z*1.4-0.2 + 0.025*sin(uT*0.17+aSeed.w*20.0),
                mix(-0.08, 1.08, ph) + 0.015*sin(uT*0.23+aSeed.x*30.0));
  vec2 s = toScreen(q, W_MOTE);
  float on = smoothstep(uAmt, uAmt-0.1, aSeed.w);
  vA = on*sin(3.14159*ph)*(0.10+0.16*aSeed.y)*calmK(s.y);
  gl_Position = vec4(s*2.0-1.0, 0.0, 1.0);
  gl_PointSize = mix(16.0, 54.0, aSeed.x*aSeed.x)*uPx;
}
"""
NMOTE_FS = """
#version 330
in float vA; out vec4 o;
uniform vec3 uCol;
void main(){ vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  o = vec4(uCol*vA*(exp(-r2*2.2)*0.8+0.2*smoothstep(1.0,0.7,r2)), 1.0); }
"""
