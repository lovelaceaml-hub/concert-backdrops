"""GLSL programs of the 3D layer (engine/p3d).

Every sprite is an instanced quad drawn additively into the engine's HDR light buffer. The light of a point
is kept whatever its footprint: a point smaller than a pixel goes through a small fixed gaussian (sigma
SIG_MIN pixels, whose sampled sum does not change as the point moves across the pixel grid), a point out of
focus is spread over its circle of confusion, a moving point over its streak. Footprint: a flat plateau of
radius R (the bokeh disc) with a gaussian skirt of sigma S, drawn out along one axis by a stretch factor
(motion during the shutter, or a reflection on restless water).
"""

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

# Shared by the sprites (vertex) and the background (fragment): the lake's ripples, the hills, the clouds.
WORLD = """
const float PI = 3.14159265;
uniform vec3 uCamPos;
uniform float uT;
uniform vec4 uHillP;      // visibility, height scale, -, -
uniform vec4 uCloudP;     // amount, drift x, drift z, scale
uniform vec3 uSunDir;
uniform vec4 uLakeP;      // reflectivity looking down, mirror gain, ripple amount, shore radius
uniform int uNCalm; uniform vec4 uCalmA[4]; uniform vec4 uCalmB[4];   // discs (x, z, radius, soft) with their own (ripple, mirror)
// the lake at p: (ripple amount, mirror gain); a disc of calm (or storm) can lie anywhere on it
vec2 lakeAt(vec2 p){
  vec2 v = vec2(uLakeP.z, uLakeP.y);
  for(int i=0;i<uNCalm;i++){
    float w = 1.0 - smoothstep(uCalmA[i].z - uCalmA[i].w, uCalmA[i].z + uCalmA[i].w, length(p - uCalmA[i].xy));
    v = mix(v, uCalmB[i].xy, w);
  }
  return v;
}
const vec3 HILL_D = vec3(1400.0, 2600.0, 5200.0);
const vec3 HILL_H = vec3(150.0, 420.0, 950.0);

// slope of the water surface at p (metres) and time t: a few crossing swells. foot: metres of water under one
// pixel along the view; a swell fades where it is only a few pixels long (far out the lake is a still mirror)
vec2 rip(vec2 p, float t, float foot){
  vec2 g = vec2(0.0);
  g += vec2( 0.80, 0.60)*0.012*cos(dot(p, vec2( 0.80, 0.60))*0.90 - t*0.90)*smoothstep(3.0*foot, 9.0*foot, 6.98);
  g += vec2(-0.45, 0.89)*0.010*cos(dot(p, vec2(-0.45, 0.89))*1.90 - t*1.35 + 1.7)*smoothstep(3.0*foot, 9.0*foot, 3.31);
  g += vec2( 0.97,-0.24)*0.008*cos(dot(p, vec2( 0.97,-0.24))*3.70 - t*1.90 + 4.1)*smoothstep(3.0*foot, 9.0*foot, 1.70);
  g += vec2( 0.31, 0.95)*0.006*cos(dot(p, vec2( 0.31, 0.95))*7.00 - t*2.60 + 2.3)*smoothstep(3.0*foot, 9.0*foot, 0.90);
  return g;
}
float ridge(vec2 c, float f, float seed){
  float s = 0.0, a = 0.5; vec2 p = c*f + seed;
  for(int i=0;i<5;i++){ float n = vnoise(p); s += a*(1.0-abs(2.0*n-1.0)); p = p*2.03 + 17.1; a *= 0.5; }
  return s;
}
// tangent of the elevation of ring k's ridge, seen along the horizontal unit direction c
float hillTan(vec2 c, int k){
  float f = k==0 ? 5.0 : (k==1 ? 3.4 : 2.3);
  float seed = 3.7 + 9.1*float(k);
  vec2 ck = normalize(c*HILL_D[k] + uCamPos.xz);
  float h = pow(ridge(ck, f, seed), 1.8)*(0.30+0.70*vnoise(ck*1.3+seed*1.7));
  return (h*HILL_H[k]*uHillP.y - uCamPos.y)/HILL_D[k];
}
// how much cloud stands in direction d (0..1), and how lit it is from the sun side
float cloudDens(vec3 d, out float lit){
  lit = 0.5;
  if(uCloudP.x < 0.001 || d.y < 0.0) return 0.0;
  vec2 uv = d.xz/(d.y+0.14)*uCloudP.w + uT*uCloudP.yz;
  float n = fbm(uv) + 0.25*fbm3(uv*2.9+7.3);
  float th = mix(1.02, 0.38, uCloudP.x);
  float dens = smoothstep(th, th+0.30, n);
  if(dens > 0.001){
    vec2 su = normalize(uSunDir.xz+vec2(1e-4))*0.16;
    float ns = fbm(uv+su) + 0.25*fbm3((uv+su)*2.9+7.3);
    lit = clamp(0.5+(n-ns)*2.4, 0.0, 1.0);
  }
  return dens*smoothstep(0.0, 0.10, d.y);
}
"""

SPRITE_COMMON = """
uniform mat4 uView, uProj, uPrevVP;
uniform vec2 uRes;
uniform float uFocal, uFocus, uAperture, uNear;
uniform vec4 uFogP;       // haze per metre, mist density at the water, mist scale height, dome extinction
uniform float uFogAmt, uDofAmt, uGain, uTwinkle, uBack;
uniform float uMirror, uDome, uDomeDist, uLod, uLodR, uCocMax, uSigMin;
uniform float uPaint;     // 0: the light pass. 1: the paint pass (true colour over the scene)
uniform vec2 uBirth;      // seconds a point takes to appear at its birth, flash when just born
uniform mat3 uDomeRot; uniform float uTurn;
uniform vec4 uSplit; uniform float uSplitStars;
uniform int uNLights; uniform vec4 uLightP[4]; uniform vec3 uLightC[4]; uniform float uLit;
uniform float uBlur, uShutterDt, uMaxStreak, uSmear, uPx;

float ihash(int id){
  uint h = uint(id); h ^= h >> 16; h *= 0x7feb352dU; h ^= h >> 15; h *= 0x846ca68bU; h ^= h >> 16;
  return float(h & 0xffffffU)/16777216.0;
}
// the mirror image of a world point in the lake: position, strength, and the smear of the ripples (metres)
vec3 mirrored(vec3 wp, out float k, out float smear){
  vec3 wm = vec3(wp.x, -wp.y, wp.z);
  float f = uCamPos.y/max(uCamPos.y - wm.y, 1e-4);
  vec3 s = uCamPos + (wm - uCamPos)*f;                       // where the reflection is seen on the water
  float path = length(wm - s);
  float ds = length(s - uCamPos);
  float foot = ds*ds/(0.5*uRes.y*uFocal*max(uCamPos.y, 0.05));
  vec2 lk = lakeAt(s.xz);
  wm.xz += 2.0*rip(s.xz, uT, foot)*lk.x*path;
  vec3 vd = normalize(s - uCamPos);
  k = lk.y*mix(uLakeP.x, 1.0, pow(1.0-clamp(-vd.y, 0.0, 1.0), 4.0))
      *(1.0 - smoothstep(uLakeP.w*0.80, uLakeP.w, length(s.xz))*step(0.001, uHillP.x))*step(0.0, wp.y);
  smear = lk.x*uSmear*path;
  return wm;
}
float fogTrans(vec3 wp, float dist){
  float tau = uFogP.x*dist;
  float y0 = uCamPos.y, y1 = abs(wp.y);
  float dy = max(abs(y1-y0), 0.02);
  tau += uFogP.y*uFogP.z*abs(exp(-y0/uFogP.z)-exp(-y1/uFogP.z))/dy*dist;
  return exp(-tau);
}
// how visible a point born at `birth` is now (0 before), with the flare of a point just born
float born(float birth){
  float age = uT - birth;
  return smoothstep(0.0, max(uBirth.x, 1e-4), age)*(1.0 + uBirth.y*exp(-max(age, 0.0)/0.25));
}
// the colour a point takes from the world's moving lights
vec3 lights(vec3 base, vec3 wp, vec3 nrm, float hasN){
  if(uLit <= 0.0 || uNLights == 0) return base;
  vec3 sum = vec3(0.0); float w = 0.0;
  float lum = dot(base, vec3(0.3, 0.6, 0.1));
  for(int i=0;i<uNLights;i++){
    vec3 d = uLightP[i].xyz - wp;
    float f = uLightP[i].w*uLightP[i].w/(dot(d, d) + uLightP[i].w*uLightP[i].w);
    if(hasN > 0.5) f *= 0.15 + 0.85*max(dot(normalize(nrm), normalize(d)), 0.0);
    sum += uLightC[i]*f; w += f;
  }
  return mix(base, base*(1.0-clamp(w, 0.0, 1.0)) + sum*max(lum, 0.15), uLit);
}
float twinkle(float seed){
  return 1.0 + uTwinkle*(1.6*pow(0.5+0.5*sin(uT*(1.7+5.3*seed)+seed*97.0), 3.0) - 0.5);
}
"""

# ------------------------------------------------------------------------------------------- point sprites
SPRITE_VS = "#version 330\n" + NOISE + WORLD + SPRITE_COMMON + """
in vec2 aCorner;
in vec3 aPos; in float aSize; in vec3 aColor; in float aAlpha; in float aEmit; in float aSeed; in vec2 aRot;
in vec3 aNormal; in vec3 aVel; in float aBirth;
uniform float uHasN;
uniform int uKind;        // 0 soft, 1 spark, 2 disc, 3 flake, 4 petal, 5 bird
uniform vec2 uRim;
uniform vec2 uBokeh;
flat out vec4 vCol;       // rgb light, glint strength
flat out vec4 vGeo;       // R, S, Lh, r0 (pixels)
flat out vec4 vShape;     // cos, sin, squash, how much of the true shape shows
flat out vec3 vMisc;      // seed, depth (m), glint length (px)
flat out float vStretch;  // a reflection on restless water: the footprint drawn out along its axis
out vec2 vLocal;

void cull(){ gl_Position = vec4(2.0, 2.0, 2.0, 1.0); }

void main(){
  vec3 wp = aPos, vel = aVel, nrm = aNormal;
  float mk = 1.0, smear = 0.0, ext = 1.0, size = aSize;
  float bk = born(aBirth);
  if(bk <= 0.0){ cull(); return; }
  if(uDome > 0.5){
    size *= uDomeDist;                                   // on the dome a size is an angle
    vec3 dir = normalize(aPos);
    if(uTurn > 0.5) dir = uDomeRot*dir;                  // the star dome can turn about its pole
    if(uSplit.w > 0.0)                                   // a sky of two looks: the stars follow their side
      ext *= mix(1.0, uSplitStars, uSplit.w*smoothstep(-uSplit.z, uSplit.z, dot(normalize(dir.xz+vec2(1e-5)), uSplit.xy)));
    // stars: dimmed by the air near the horizon, hidden by hills and clouds
    ext *= exp(-uFogP.w/(max(dir.y, 0.0)+0.06));
    float te = dir.y/max(length(dir.xz), 1e-4);
    if(uHillP.x > 0.001 && te < 0.5){
      vec2 c = normalize(dir.xz);
      float ht = max(hillTan(c, 0), max(hillTan(c, 1), hillTan(c, 2)));
      ext *= 1.0 - uHillP.x*smoothstep(ht+0.004, ht-0.002, te);
    }
    float lit; ext *= 1.0 - 0.92*cloudDens(dir, lit);
    wp = uCamPos + dir*uDomeDist;
    vel = vec3(0.0);
  }
  if(uMirror > 0.5){
    wp = mirrored(wp, mk, smear);
    vel.y = -vel.y; nrm.y = -nrm.y;
    if(mk < 0.0005){ cull(); return; }
  }
  vec4 vp = uView*vec4(wp, 1.0);
  float depth = -vp.z;
  if(depth < uNear){ cull(); return; }
  vec4 cp = uProj*vp;
  vec2 ndc = cp.xy/cp.w;
  if(abs(ndc.x) > 1.6 || abs(ndc.y) > 1.6){ cull(); return; }
  float pxm = 0.5*uRes.y*uFocal/depth;                 // pixels per metre at this depth

  // the footprint in focus
  float r0 = 0.5*size*pxm, sig0 = 0.0, area0, squash = 1.0, flash = 1.0;
  if(uKind <= 1){ sig0 = 0.44*r0; area0 = 2.0*PI*sig0*sig0; r0 = 0.0; }
  else if(uKind == 2){ area0 = PI*r0*r0; }
  else {
    float c = abs(cos(aRot.y));
    squash = max(c, 0.14);
    flash = uKind == 5 ? 1.0 : 0.40 + 1.25*pow(c, 6.0);    // a flake flashes when it faces the camera
    area0 = (uKind == 3 ? 1.9 : (uKind == 4 ? 1.25 : 0.55))*r0*r0*squash;
  }
  float req = sqrt(area0/PI);

  // depth of field: circle of confusion in pixels (exactly zero on the focus plane)
  float coc = 0.25*uAperture*uFocal*abs(1.0/uFocus - 1.0/depth)*uRes.y*uDofAmt;
  coc = min(coc, uCocMax);
  float keep = 1.0;
  if(uLod > 0.5 && coc > uLodR){
    // far out of focus: draw a share of the points, each brighter (the same light, far fewer big discs)
    float q = (uLodR*uLodR)/(coc*coc);
    float h = ihash(gl_InstanceID);
    float w = clamp((1.25*q - h)/(0.25*q), 0.0, 1.0);
    if(w <= 0.0){ cull(); return; }
    float top = min(1.25*q, 1.0);
    float mean = q + ((1.25*q)*(top-q) - 0.5*(top*top-q*q))/(0.25*q);
    keep = w/mean;
  }
  float R = uKind <= 1 ? coc : sqrt(req*req + coc*coc);
  float S = sqrt(sig0*sig0 + uSigMin*uSigMin);

  // motion blur: the sprite is stretched along its path on screen during the shutter
  vec2 axis = vec2(1.0, 0.0); float Lh = 0.0;
  if(uBlur > 0.0){
    vec4 pc = uPrevVP*vec4(wp - vel*uShutterDt, 1.0);
    if(pc.w > uNear){
      vec2 mv = (ndc - pc.xy/pc.w)*0.5*uRes;
      float L = length(mv);
      if(L*uBlur > 0.75){
        axis = mv/L;
        // a sharp point streaks freely; a bokeh disc stays close to a disc (a short oval at most)
        Lh = min(0.5*L*uBlur, mix(uMaxStreak, 0.9*R + 6.0*uPx, smoothstep(1.5*uPx, 6.0*uPx, R)));
      }
    }
  }
  if(uMirror > 0.5){
    // ripples draw a reflection out along the line of sight: a soft upright oval
    float sp = smear*pxm*(uDome > 0.5 ? 0.08 : 1.0);     // the stars' images stay points: a sea of stars
    sp = min(sp, 2.5*R + 22.0*uPx);
    if(sp > Lh){ axis = vec2(0.0, 1.0); Lh = sp; }
  }
  float stretch = 1.0 + Lh/(R + 2.0*S);

  // (the disc's brighter edge lifts its skirt too: counted here, so the light stays the same)
  float areaF = (PI*R*R + (1.90*PI*S*S + 7.72*R*S)*(1.0 + 0.75*uBokeh.x*smoothstep(3.0, 9.0, R)))*stretch;
  float amp = min(area0/areaF, 1.0);

  float b = aAlpha*aEmit*uGain*keep*amp*mk*ext*flash*twinkle(aSeed)*bk;
  vec3 vdir = normalize(wp - uCamPos);
  if(uRim.x > 0.0){
    float f = pow(clamp(1.0-abs(dot(normalize(nrm), vdir)), 0.0, 1.0), uRim.y);
    b *= mix(1.0, f, uRim.x);
  }
  if(uBack > 0.0) b *= 1.0 + uBack*4.0*pow(max(dot(vdir, uSunDir), 0.0), 6.0);
  if(uDome < 0.5) b *= mix(1.0, fogTrans(wp, length(wp - uCamPos)), uFogAmt);
  b *= smoothstep(uNear, uNear*5.0, depth);
  // a sprite that would fill much of the picture (a point right at the lens) fades away instead
  b *= 1.0 - smoothstep(0.12*uRes.y, 0.30*uRes.y, (max(R, r0) + 3.0*S)*stretch);
  vec3 col = lights(aColor, wp, nrm, uHasN)*b;
  if(uPaint > 0.5) col = vec3(clamp(b/max(aEmit, 1e-4), 0.0, 1.0));     // paint: coverage, not light
  if(max(col.r, max(col.g, col.b)) < 0.00012){ cull(); return; }

  // spark: a fine four-point glint while the point is sharp
  float glint = 0.0, glen = 0.0;
  if(uKind == 1){
    glint = (1.0 - smoothstep(0.6, 2.5, coc/max(S, 0.01)))*(0.35+0.65*pow(0.5+0.5*sin(uT*(2.3+6.1*aSeed)+aSeed*51.0), 2.0));
    glen = glint > 0.01 ? (4.0 + 9.0*sig0) : 0.0;
  }
  float kshape = 0.0;
  if(uKind >= 3) kshape = (1.0 - smoothstep(0.35, 1.2, max(coc, Lh)/max(r0, 1e-3)))*smoothstep(1.0, 2.5, r0);
  float ex = uKind >= 3 ? max(R, r0*kshape*1.05) : R;
  float hx = max((ex + 3.0*S)*stretch, glen*1.42), hy = max(ex + 3.0*S, glen*1.42);
  if(kshape > 0.0){ hx = max(hx, hy); hy = hx; }
  vec2 loc = aCorner*vec2(hx, hy);
  vec2 off = axis*loc.x + vec2(-axis.y, axis.x)*loc.y;
  vLocal = loc;
  vCol = uPaint > 0.5 ? vec4(aColor, col.r) : vec4(col, glint);
  vGeo = vec4(R, S, 0.0, r0);
  // the shape's own turn is measured in the picture, so undo the streak axis
  float ang = aRot.x - atan(axis.y, axis.x);
  vShape = vec4(cos(ang), sin(ang), squash, kshape);
  vMisc = vec3(aSeed, depth, glen);
  vStretch = stretch;
  gl_Position = vec4(ndc + off*2.0/uRes, 0.0, 1.0);
}
"""

SPRITE_FS = """
#version 330
in vec2 vLocal;
flat in vec4 vCol; flat in vec4 vGeo; flat in vec4 vShape; flat in vec3 vMisc; flat in float vStretch;
uniform int uKind;
uniform float uT;
uniform vec2 uRes;
uniform vec2 uBokeh;      // bright rim of the bokeh disc, how hexagonal it is
uniform float uMaskOn, uMaskBias;
uniform vec2 uMaskK;      // how strongly dark silhouettes and sky silhouettes hide the light behind them
uniform sampler2D uMaskTex;
uniform float uPaint, uWindow;
uniform vec4 uClear[2]; uniform vec4 uClearK;     // keep-clear boxes (x0, y0, x1, y1), their (amount, soft) pairs
out vec4 o;

// what is left of a sprite at this pixel after the silhouettes, the windows and the keep-clear boxes
float keepAt(float depth){
  float k = 1.0;
  if(uMaskOn > 0.5){
    vec4 m = texture(uMaskTex, gl_FragCoord.xy/uRes);
    if(uWindow > 0.5) k *= smoothstep(0.25, 0.80, m.g);
    else k *= 1.0 - max(smoothstep(0.25, 0.80, m.r)*uMaskK.x, smoothstep(0.25, 0.80, m.g)*uMaskK.y)
                    *smoothstep(0.0, 0.12, depth - m.a - uMaskBias);
  } else if(uWindow > 0.5) k = 0.0;
  vec2 uv = gl_FragCoord.xy/uRes;
  for(int i=0;i<2;i++){
    float a = uClearK[2*i], sft = max(uClearK[2*i+1], 1e-4);
    if(a > 0.0){
      vec2 d = min(uv - uClear[i].xy, uClear[i].zw - uv);
      k *= 1.0 - a*smoothstep(0.0, sft, min(d.x, d.y));
    }
  }
  return k;
}

float sdBox(vec2 p, vec2 b){ vec2 d = abs(p)-b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
float sdVesica(vec2 p, float r, float d){
  p = abs(p); float b = sqrt(r*r-d*d);
  return ((p.y-b)*d > p.x*b) ? length(p-vec2(0.0, b)) : length(p-vec2(-d, 0.0))-r;
}
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa = p-a, ba = b-a; return length(pa - ba*clamp(dot(pa, ba)/dot(ba, ba), 0.0, 1.0)); }

void main(){
  float R = vGeo.x, S = vGeo.y, r0 = vGeo.w;
  vec2 q = vec2(vLocal.x/vStretch, vLocal.y);
  float d = length(q);
  if(uBokeh.y > 0.0 && R > 3.0*S){
    vec2 a = abs(q);
    float dh = max(a.x*0.866+a.y*0.5, a.y)*1.05;        // a soft hexagon
    d = mix(d, dh, uBokeh.y*smoothstep(3.0*S, 8.0*S, R));
  }
  float sd = d - R;
  if(vShape.w > 0.001){
    vec2 pr = vec2(vShape.x*vLocal.x + vShape.y*vLocal.y, -vShape.y*vLocal.x + vShape.x*vLocal.y)/r0;
    pr.y /= vShape.z;
    float ss;
    if(uKind == 3){
      float a = vMisc.x*6.2832;
      ss = max(sdBox(pr, vec2(0.88, 0.60)), dot(pr, vec2(cos(a), sin(a))) - 0.52);
    } else if(uKind == 4){
      ss = sdVesica(pr.yx, 1.25, 0.80);
    } else {
      float fl = 0.25 + 0.75*sin(uT*(7.0+3.0*vMisc.x) + vMisc.x*40.0);     // the wings beat
      vec2 tip = vec2(cos(fl*0.8), sin(fl*0.8));
      ss = min(sdSeg(pr, vec2(0.0), tip), sdSeg(pr, vec2(0.0), vec2(-tip.x, tip.y))) - 0.11*(1.0-0.6*length(pr));
    }
    sd = mix(sd, ss*r0*min(vShape.z, 1.0), vShape.w);
  }
  float prof = sd <= 0.0 ? 1.0 : exp(-sd*sd/(2.0*S*S));
  prof = max(prof - 0.0111, 0.0)/0.9889;
  if(R > 2.0*S && vShape.w < 0.5){
    float e = clamp(d/R, 0.0, 1.0); e = e*e*e; e = e*e;
    prof *= 1.0 + uBokeh.x*(e - 0.25)*smoothstep(3.0, 9.0, R);   // a slightly brighter edge, the same light in all
  }
  if(uPaint > 0.5){
    float a = clamp(vCol.a*prof, 0.0, 1.0)*keepAt(vMisc.y);
    o = vec4(vCol.rgb*a, a);
    return;
  }
  vec3 c = vCol.rgb*prof;
  if(vCol.a > 0.01){
    float gl = vMisc.z*0.30, sg = max(0.75*S, 0.55);
    vec2 g = vec2(vShape.x*vLocal.x + vShape.y*vLocal.y, -vShape.y*vLocal.x + vShape.x*vLocal.y);
    float cross = exp(-abs(g.x)/gl)*exp(-g.y*g.y/(2.0*sg*sg)) + exp(-abs(g.y)/gl)*exp(-g.x*g.x/(2.0*sg*sg));
    float edge = 1.0 - smoothstep(0.7, 1.0, max(abs(g.x), abs(g.y))/vMisc.z);
    c += vCol.rgb*cross*0.55*vCol.a*edge;
  }
  o = vec4(c*keepAt(vMisc.y), 0.0);
}
"""

# ------------------------------------------------------------------------------------------- line segments
SEG_VS = "#version 330\n" + NOISE + WORLD + SPRITE_COMMON + """
in vec2 aCorner;
in vec3 aPos; in float aSize; in vec3 aColor; in float aAlpha; in float aEmit; in float aSeed; in vec2 aUV;
in float aBirth; in vec4 aPos2A2; in float aSize2;
uniform int uKind;        // 6 line, 7 ribbon
uniform float uHair;
flat out vec4 vEnd;       // length on screen (px), S, cap (1 line, 0 ribbon), depth
out vec4 vCol;            // light (or, in the paint pass, colour and coverage)
out vec4 vLoc;            // along (px, 0 at pos), across (px), plateau radius here, place along the path

void cull(){ gl_Position = vec4(2.0, 2.0, 2.0, 1.0); }

void main(){
  float bk = born(aBirth);
  if(bk <= 0.0){ cull(); return; }
  vec3 w1 = aPos, w2 = aPos2A2.xyz;
  float mk1 = 1.0, mk2 = 1.0, sm;
  if(uMirror > 0.5){ w1 = mirrored(w1, mk1, sm); w2 = mirrored(w2, mk2, sm); if(mk1+mk2 < 0.001){ cull(); return; } }
  vec4 v1 = uView*vec4(w1, 1.0), v2 = uView*vec4(w2, 1.0);
  float d1 = -v1.z, d2 = -v2.z;
  if(d1 < uNear && d2 < uNear){ cull(); return; }
  // cut cleanly where the segment passes the camera
  if(d1 < uNear){ float f = (uNear - d1)/(d2 - d1); v1 = mix(v1, v2, f); d1 = uNear; }
  if(d2 < uNear){ float f = (uNear - d2)/(d1 - d2); v2 = mix(v2, v1, f); d2 = uNear; }
  vec4 c1 = uProj*v1, c2 = uProj*v2;
  vec2 s1 = c1.xy/c1.w*0.5*uRes, s2 = c2.xy/c2.w*0.5*uRes;      // pixels from the centre
  vec2 dv = s2 - s1; float len = length(dv);
  vec2 dir = len > 1e-4 ? dv/len : vec2(1.0, 0.0);
  vec2 nrm = vec2(-dir.y, dir.x);
  bool first = aCorner.x < 0.0;
  float depth = first ? d1 : d2;
  float sz = first ? aSize : aSize2;
  float pxm = 0.5*uRes.y*uFocal/depth;
  float wpx = max(sz*pxm, uHair);                     // width on screen, never under a hairline
  float coc = min(0.25*uAperture*uFocal*abs(1.0/uFocus - 1.0/depth)*uRes.y*uDofAmt, uCocMax);
  float R, S, e;
  if(uKind == 6){ R = sqrt(0.25*wpx*wpx + coc*coc); S = uSigMin; e = sz*pxm; }
  else { R = coc; S = sqrt(0.09*wpx*wpx + uSigMin*uSigMin); e = 0.752*sz*pxm; }
  float amp = min(e/(2.0*R + 2.5066*S), 1.0);
  float a = first ? aAlpha : aPos2A2.w;
  float b = a*aEmit*uGain*amp*(first ? mk1 : mk2)*twinkle(aSeed)*bk;
  vec3 wp = first ? w1 : w2;
  b *= mix(1.0, fogTrans(wp, length(wp - uCamPos)), uFogAmt);
  b *= smoothstep(uNear, uNear*5.0, depth);
  b *= 1.0 - smoothstep(0.12*uRes.y, 0.30*uRes.y, R + 3.0*S);
  float h = R + 3.0*S;
  float cap = uKind == 6 ? 1.0 : 0.0;                 // a ribbon's pieces meet end to end: no caps, no beads
  vec2 p = (first ? s1 - dir*h*cap : s2 + dir*h*cap) + nrm*aCorner.y*h;
  vLoc = vec4(first ? -h*cap : len + h*cap, aCorner.y*h, R, first ? aUV.x : aUV.y);
  vEnd = vec4(len, S, cap, depth);
  vCol = uPaint > 0.5 ? vec4(aColor, clamp(b/max(aEmit, 1e-4), 0.0, 1.0)) : vec4(lights(aColor, wp, vec3(0.0), 0.0)*b, 0.0);
  gl_Position = vec4(p*2.0/uRes, 0.0, 1.0);
}
"""

SEG_FS = """
#version 330
in vec4 vCol; in vec4 vLoc; flat in vec4 vEnd;
uniform vec2 uRes;
uniform float uT;
uniform vec4 uPulse;      // speed, length, gain, period: a brighter stretch travelling along the path
uniform float uMaskOn, uMaskBias;
uniform vec2 uMaskK;
uniform sampler2D uMaskTex;
uniform float uPaint, uWindow;
uniform vec4 uClear[2]; uniform vec4 uClearK;
out vec4 o;
float keepAt(float depth){
  float k = 1.0;
  if(uMaskOn > 0.5){
    vec4 m = texture(uMaskTex, gl_FragCoord.xy/uRes);
    if(uWindow > 0.5) k *= smoothstep(0.25, 0.80, m.g);
    else k *= 1.0 - max(smoothstep(0.25, 0.80, m.r)*uMaskK.x, smoothstep(0.25, 0.80, m.g)*uMaskK.y)
                    *smoothstep(0.0, 0.12, depth - m.a - uMaskBias);
  } else if(uWindow > 0.5) k = 0.0;
  vec2 uv = gl_FragCoord.xy/uRes;
  for(int i=0;i<2;i++){
    float a = uClearK[2*i], sft = max(uClearK[2*i+1], 1e-4);
    if(a > 0.0){
      vec2 d = min(uv - uClear[i].xy, uClear[i].zw - uv);
      k *= 1.0 - a*smoothstep(0.0, sft, min(d.x, d.y));
    }
  }
  return k;
}
void main(){
  float along = (vLoc.x - clamp(vLoc.x, 0.0, vEnd.x))*vEnd.z;
  float sd = length(vec2(along, vLoc.y)) - vLoc.z;
  float S = vEnd.y;
  float prof = sd <= 0.0 ? 1.0 : exp(-sd*sd/(2.0*S*S));
  prof = max(prof - 0.0111, 0.0)/0.9889;
  if(uPulse.z > 0.0){
    float x = vLoc.w - uPulse.x*uT;
    if(uPulse.w > 0.0) x = (fract(x/uPulse.w + 0.5) - 0.5)*uPulse.w;
    prof *= 1.0 + uPulse.z*exp(-x*x/(uPulse.y*uPulse.y));
  }
  float k = keepAt(vEnd.w);
  if(uPaint > 0.5){ float a = clamp(vCol.a*prof, 0.0, 1.0)*k; o = vec4(vCol.rgb*a, a); return; }
  o = vec4(vCol.rgb*prof*k, 0.0);
}
"""

# ------------------------------------------------------------------------------------------- silhouette mask
# Red: coverage of "dark" sets, green: coverage of "sky" sets (both added up), alpha: the nearest depth (MIN).
MASK_VS = """
#version 330
in vec2 aCorner; in vec3 aPos; in float aSize; in float aAlpha; in float aBirth;
uniform mat4 uView, uProj;
uniform vec2 uRes;
uniform float uFocal, uNear, uGrow, uT;
out vec2 vLocal; flat out vec3 vP;    // radius px, weight, depth
void main(){
  vec4 vp = uView*vec4(aPos, 1.0);
  float depth = -vp.z;
  float w = smoothstep(0.02, 0.20, aAlpha)*step(aBirth, uT);
  if(depth < uNear || w <= 0.0){ gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }
  vec4 cp = uProj*vp;
  float r = max((0.5*aSize + uGrow)*0.5*uRes.y*uFocal/depth, 1.2);
  vLocal = aCorner*(r + 1.0);
  vP = vec3(r, w, depth);
  gl_Position = vec4(cp.xy/cp.w + vLocal*2.0/uRes, 0.0, 1.0);
}
"""

MASK_FS = """
#version 330
in vec2 vLocal; flat in vec3 vP;
uniform int uSel;
out vec4 o;
void main(){
  float c = (1.0 - smoothstep(vP.x-1.0, vP.x+1.0, length(vLocal)))*vP.y;
  if(c < 0.02) discard;
  o = uSel == 0 ? vec4(c, 0.0, 0.0, vP.z) : vec4(0.0, c, 0.0, vP.z);
}
"""

QUAD_VS = """
#version 330
in vec2 aPos;
out vec2 vUV;
void main(){ vUV = aPos*0.5+0.5; gl_Position = vec4(aPos, 0.0, 1.0); }
"""

MASKBLUR_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex; uniform vec2 uDir;
void main(){
  vec4 c0 = texture(uTex, vUV);
  vec4 a1 = texture(uTex, vUV+uDir*1.3846), a2 = texture(uTex, vUV-uDir*1.3846);
  vec4 b1 = texture(uTex, vUV+uDir*3.2308), b2 = texture(uTex, vUV-uDir*3.2308);
  vec2 c = c0.rg*0.2270 + (a1.rg+a2.rg)*0.3162 + (b1.rg+b2.rg)*0.0703;
  float dmin = min(c0.a, min(min(a1.a, a2.a), min(b1.a, b2.a)));
  o = vec4(c, 0.0, dmin);
}
"""

# ------------------------------------------------------------------------------------------- the background
# Sky dome with sun, clouds and the Milky Way's glow, three rings of hills, the mirror lake, haze, ground mist
# and shafts of light. rgb: the picture (linear light). alpha: how much of the sun's light passes here (for
# the ray pass).
BG_FS = "#version 330\n" + NOISE + WORLD + """
in vec2 vUV; out vec4 o;
uniform vec3 uCamR, uCamU, uCamF;
uniform float uFocal, uAspect;
uniform vec2 uRes;
uniform vec3 uSkyTop, uSkyMid, uSkyHor, uSunCol, uHazeCol, uHillCol, uWater, uMilkyN, uMistCol;
uniform vec4 uSunP;       // strength, cos of the disc's radius, disc strength, glow width
uniform vec4 uAirP;       // haze per metre, mist density at the water, mist scale height, milky way glow
uniform int uNShaft; uniform vec4 uShA[4]; uniform vec4 uShB[4];
uniform vec4 uSplit; uniform vec3 uSkyTopB, uSkyMidB, uSkyHorB, uHazeColB;    // a second look on one side of the sky
uniform int uNLights; uniform vec4 uLightP[4]; uniform vec3 uLightC[4];
float splitW(vec2 dxz){ return uSplit.w*smoothstep(-uSplit.z, uSplit.z, dot(normalize(dxz+vec2(1e-5)), uSplit.xy)); }

vec3 skyBase(vec3 d){
  float e = max(d.y, 0.0);
  float sw = uSplit.w > 0.0 ? splitW(d.xz) : 0.0;
  vec3 c = mix(mix(uSkyHor, uSkyHorB, sw), mix(uSkyMid, uSkyMidB, sw), smoothstep(0.0, 0.16, e));
  c = mix(c, mix(uSkyTop, uSkyTopB, sw), smoothstep(0.07, 0.55, e));
  float a = max(1.0 - dot(d, uSunDir), 0.0);
  float w = uSunP.w;
  vec3 g = uSunCol*uSunP.x*(0.42*exp(-a*42.0/w) + 0.20*exp(-a*9.0/w) + 0.07*exp(-a*2.2/w));
  // the glow hugs the horizon on the sun's side (the band of dawn)
  float az = dot(normalize(d.xz+vec2(1e-5)), normalize(uSunDir.xz+vec2(1e-5)));
  g += uSunCol*uSunP.x*0.22*exp(-e*7.0)*pow(max(az, 0.0), 3.0)*smoothstep(-0.45, 0.05, uSunDir.y);
  c += g;
  if(uAirP.w > 0.001){
    float m = dot(d, uMilkyN);
    c += vec3(0.085, 0.100, 0.190)*uAirP.w*exp(-m*m/0.030)*(0.25+1.10*fbm(d.xz*5.0+d.y*3.0+2.0))*smoothstep(0.0, 0.25, e);
  }
  return c;
}

// the sky, the clouds and the hills in direction d (d.y >= 0); vis: the share of sunlight that passes
vec3 shade(vec3 d, float te, float disc, float aa, out float vis){
  vec3 c = skyBase(d);
  vis = 1.0;
  float cs = dot(d, uSunDir);
  float lit; float dens = cloudDens(d, lit);
  if(dens > 0.001){
    vec3 dark = mix(uSkyMid, uSkyTop, 0.5)*0.50 + uSkyHor*0.16;
    vec3 light = uSkyHor*0.55 + uSunCol*uSunP.x*(0.30+0.95*pow(max(cs, 0.0), 4.0));
    vec3 cc = mix(dark, light, lit);
    cc += uSunCol*uSunP.x*pow(max(cs, 0.0), 12.0)*(1.0-dens)*2.0;      // a silver lining toward the sun
    c = mix(c, cc, dens*0.92);
    vis *= 1.0 - 0.85*dens;
  }
  c += uSunCol*uSunP.x*uSunP.z*disc*smoothstep(uSunP.y-0.00006, uSunP.y+0.00006, cs)*(1.0-dens);
  if(uHillP.x > 0.001){
    float lxz = max(length(d.xz), 1e-5);
    if(te < 0.55){
      vec2 cxz = d.xz/lxz;
      vec3 hz = mix(uHazeCol, uHazeColB, uSplit.w > 0.0 ? splitW(cxz) : 0.0)
                + uSunCol*uSunP.x*0.22*pow(max(dot(cxz, normalize(uSunDir.xz+vec2(1e-5))), 0.0), 3.0)
                *smoothstep(-0.45, 0.05, uSunDir.y);
      for(int k=2;k>=0;k--){
        float ht = hillTan(cxz, k);
        float m = smoothstep(ht+aa, ht-aa, te)*uHillP.x;
        if(k == 2 && te < 0.0) m = uHillP.x;               // beyond the lake: land out to the horizon
        if(m > 0.0){
          float far = k==2 ? 0.80 : (k==1 ? 0.56 : 0.30);
          float low = clamp((ht-te)/max(ht+uCamPos.y/HILL_D[k], 0.02), 0.0, 1.0);   // toward the foot, into the mist
          float foot = max(far+0.25, 1.0 - exp(-uLakeP.w*uAirP.x*1.6));       // the lake's haze at the shore
          vec3 hc = mix(uHillCol, hz, clamp(mix(far, foot, low*low), 0.0, 0.97));
          hc += uSunCol*uSunP.x*0.10*exp(-max(ht-te, 0.0)*90.0)*pow(max(cs, 0.0), 4.0);   // a lit ridge
          c = mix(c, hc, m);
          vis *= 1.0 - m;
        }
      }
    }
  }
  return c;
}

float erfa(float x){ float x2 = x*x; return sign(x)*sqrt(1.0-exp(-x2*(1.2732+0.147*x2)/(1.0+0.147*x2))); }
// light scattered toward the camera by shaft i along the ray o + d t, 0 < t < tMax (metres of full density)
float shaft(vec3 ro, vec3 d, vec4 a, float spread, float tMax){
  vec2 oc = ro.xz - a.xy; float dl = length(d.xz);
  if(dl < 1e-4) return 0.0;
  vec2 dn = d.xz/dl;
  float tc = -dot(oc, dn);
  float rho2 = max(dot(oc, oc) - tc*tc, 0.0);
  float yc = ro.y + d.y*(tc/dl);
  float r = a.z*(1.0 + spread*clamp(yc/a.w, 0.0, 1.0));
  float I = sqrt(PI)*r/dl*exp(-rho2/(r*r))*0.5*(erfa((tMax*dl - tc)/r) - erfa(-tc/r));
  return I*smoothstep(-0.5, 0.5, yc)*(1.0 - smoothstep(a.w*0.70, a.w, yc))*(0.55+0.75*clamp(yc/a.w, 0.0, 1.0));
}

void main(){
  vec2 ndc = vUV*2.0-1.0;
  vec3 d = normalize(uCamF*uFocal + uCamR*ndc.x*uAspect + uCamU*ndc.y);
  float aa = 1.6/(uRes.y*uFocal);
  float vis = 0.0, dist = 1e5;
  vec3 col;
  vec3 hazeC = uHazeCol;
  bool water = d.y < 0.0 && (uCamPos.y/(-d.y) < uLakeP.w || uHillP.x < 0.001);
  vec3 rr = d; vec3 hit = uCamPos; float fres = 0.0;
  if(water){
    dist = uCamPos.y/(-d.y);
    hit = uCamPos + d*dist;
    float foot = dist*dist/(0.5*uRes.y*uFocal*max(uCamPos.y, 0.05));
    vec2 lk = lakeAt(hit.xz);
    vec2 g = rip(hit.xz, uT, foot)*lk.x;
    if(lk.x > 0.0){
      float nf = lk.x/(1.0 + dist/22.0);
      g += (vec2(vnoise(hit.xz*4.7+uT*vec2(0.31, 0.47)), vnoise(hit.xz*4.7+31.7-uT*vec2(0.43, 0.23)))-0.5)*0.045*nf
           *smoothstep(3.0*foot, 9.0*foot, 0.45);
      g += (vec2(vnoise(hit.xz*17.0+uT*vec2(0.9, 0.6)), vnoise(hit.xz*17.0+11.3-uT*vec2(0.7, 1.1)))-0.5)*0.030*nf*nf
           *smoothstep(3.0*foot, 9.0*foot, 0.12);
      // a slow broad swell so the surface never looks ruled
      g += (vec2(vnoise(hit.xz*0.21+uT*vec2(0.05, 0.03)), vnoise(hit.xz*0.21+7.7-uT*vec2(0.04, 0.06)))-0.5)*0.020*lk.x
           *smoothstep(3.0*foot, 9.0*foot, 9.0);
    }
    vec3 n = normalize(vec3(-g.x, 1.0, -g.y));
    rr = reflect(d, n);
    rr.y = max(rr.y, 0.003); rr = normalize(rr);
    float v;
    vec3 c = shade(rr, rr.y/max(length(rr.xz), 1e-5), 0.0, aa*3.0, v);
    float cs = max(dot(rr, uSunDir), 0.0);
    c += uSunCol*uSunP.x*v*(pow(cs, 1500.0)*uSunP.z*0.7 + pow(cs, 260.0)*0.7 + pow(cs, 40.0)*0.16)
         *smoothstep(-0.03, 0.02, uSunDir.y);
    fres = mix(uLakeP.x, 1.0, pow(1.0-clamp(-d.y, 0.0, 1.0), 4.0))*lk.y;
    col = mix(uWater, c, fres);
    for(int i=0;i<uNLights;i++){                                       // each moving light lays a pool on the water
      vec2 q = hit.xz - uLightP[i].xz; float r = uLightP[i].w*(1.0 + 0.5*uLightP[i].y);
      col += uLightC[i]*0.35*r*r/(dot(q, q) + r*r);
    }
    // far water melts into the haze of the horizon
    float lxz = max(length(d.xz), 1e-5);
    hazeC = mix(uHazeCol, uHazeColB, uSplit.w > 0.0 ? splitW(d.xz) : 0.0)
            + uSunCol*uSunP.x*0.22*pow(max(dot(d.xz/lxz, normalize(uSunDir.xz+vec2(1e-5))), 0.0), 3.0)
            *smoothstep(-0.45, 0.05, uSunDir.y);
    col = mix(col, hazeC, 1.0 - exp(-dist*uAirP.x*1.6));
  } else {
    vec3 dd = d; if(dd.y < 0.0005){ dd.y = 0.0005; dd = normalize(dd); }
    col = shade(dd, d.y/max(length(d.xz), 1e-5), 1.0, aa, vis);
  }
  // ground mist: fog that thins with height, lit by the sun, in drifting patches
  if(uAirP.y > 0.0001){
    float H = uAirP.z, y0 = uCamPos.y;
    float dy = abs(d.y) < 1e-4 ? 1e-4 : d.y;
    float T = min(dist, uLakeP.w);
    float tau = uAirP.y*H*(exp(-y0/H) - exp(-max(y0 + dy*T, 0.0)/H))/dy;
    tau = clamp(tau, 0.0, uAirP.y*exp(-y0/H)*T);
    float tm = clamp((H - y0)/dy, 4.0, 160.0);                       // where the ray is deep in the mist
    vec2 mp = (uCamPos + d*tm).xz;
    tau *= 0.45 + 1.1*fbm3(mp*0.035 + uT*vec2(0.012, 0.007));
    float cs = max(dot(d, uSunDir), 0.0);
    vec3 mc = uMistCol + uSunCol*uSunP.x*0.35*pow(cs, 5.0);
    col = mix(col, mc, 1.0 - exp(-tau));
  }
  // the moving lights glow in the air round them (more in mist and haze)
  for(int i=0;i<uNLights;i++){
    vec3 oc = uLightP[i].xyz - uCamPos;
    float tc = clamp(dot(oc, d), 0.0, dist);
    vec3 q = oc - d*tc; float r = uLightP[i].w;
    col += uLightC[i]*(0.10 + 0.9*uAirP.y*50.0*exp(-max(uLightP[i].y, 0.0)/uAirP.z) + uAirP.x*300.0)*0.5*r*r/(dot(q, q) + r*r);
  }
  // shafts of light, and their image in the water
  for(int i=0;i<uNShaft;i++){
    vec3 sc = uShB[i].rgb;
    float I = shaft(uCamPos, d, uShA[i], uShB[i].a, dist);
    if(water){
      I += shaft(hit, rr, uShA[i], uShB[i].a, 1e5)*fres*0.7;
      vec2 q = hit.xz - uShA[i].xy;
      I += 1.6*exp(-dot(q, q)/(uShA[i].z*uShA[i].z));                  // the pool of light on the water
    }
    col += sc*I*0.22;
  }
  o = vec4(col, vis);
}
"""

# ------------------------------------------------------------------------------------------- rays of light
# Quarter size. The source: the sun's bright surround where the sky is open, and the world's own light,
# both cut out by the silhouettes in front. Then two radial blurs toward the light.
RAYSRC_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform vec2 uCenter; uniform float uFan, uT;
uniform sampler2D uBg, uMask;
uniform vec3 uCamR, uCamU, uCamF, uSunDir, uSunCol, uLightCol;
uniform float uFocal, uAspect, uSunInt, uMaskOn, uMode;
uniform vec4 uLight;      // screen x, y, radius (share of the height), depth in metres
void main(){
  vec2 ndc = vUV*2.0-1.0;
  vec3 d = normalize(uCamF*uFocal + uCamR*ndc.x*uAspect + uCamU*ndc.y);
  vec4 m = uMaskOn > 0.5 ? texture(uMask, vUV) : vec4(0.0, 0.0, 0.0, 1e5);
  float cov = smoothstep(0.25, 0.80, max(m.r, m.g));
  vec3 c;
  if(uMode < 0.5){
    float a = max(1.0 - dot(d, uSunDir), 0.0);
    float src = exp(-a*260.0)*3.2 + exp(-a*30.0)*0.75 + exp(-a*6.0)*0.14;
    vec2 qf = (vUV-uCenter)*vec2(uAspect, 1.0);
    float ang = atan(qf.y, qf.x);
    float fan = 0.45 + 0.85*vnoise(vec2(ang*5.0, 2.3+uT*0.05)) + 0.50*vnoise(vec2(ang*17.0, 7.1-uT*0.08));
    c = uSunCol*uSunInt*src*texture(uBg, vUV).a*(1.0-cov)*mix(1.0, fan, uFan);
  } else {
    vec2 q = (vUV-uLight.xy)*vec2(uAspect, 1.0);
    float ang = atan(q.y, q.x);
    float fan = 0.40 + 0.90*vnoise(vec2(ang*5.0, 4.1+uT*0.07)) + 0.55*vnoise(vec2(ang*19.0, 9.3-uT*0.10));
    c = uLightCol*exp(-dot(q, q)/(uLight.z*uLight.z))*(1.0 - cov*step(m.a, uLight.w))*mix(1.0, fan, uFan);
  }
  o = vec4(c, 1.0);
}
"""

RADIAL_FS = """
#version 330
in vec2 vUV; out vec4 o;
uniform sampler2D uTex; uniform vec2 uCenter; uniform float uLen, uDecay;
void main(){
  vec2 st = (uCenter - vUV)*uLen/14.0;
  vec3 acc = vec3(0.0); float w = 1.0, ws = 0.0;
  for(int i=0;i<14;i++){
    acc += texture(uTex, vUV + st*float(i)).rgb*w; ws += w; w *= uDecay;
  }
  o = vec4(acc/ws, 1.0);
}
"""

# ------------------------------------------------------------------------------------------- resolve
# The background as the composite takes it: motion blur of the camera, dark bodies and double exposures from
# the mask, rays, bursts of light.
RESOLVE_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform sampler2D uBg, uRayA, uRayB, uMask, uPaintT, uBg2;
uniform float uPaintOn;
uniform vec3 uCamR, uCamU, uCamF, uCamPos;
uniform mat4 uPrevVP;
uniform float uFocal, uAspect, uT, uBlur, uShore;
uniform vec2 uRes;
uniform vec4 uRayK;       // sun rays strength, light rays strength, -, -
uniform float uMaskOn, uDarkK, uSkyK, uFillEdge;
uniform int uFillKind;    // 0 clouds, 1 sunrise, 2 stars, 3 day, 4 the same world in another look
uniform vec4 uFillBox;    // centre x, y and half height of the shape on screen; drift
uniform vec3 uFillTint, uDarkTint;
uniform int uNBurst; uniform vec4 uBurst[4]; uniform vec3 uBurstCol[4];

vec3 fill(vec2 uv){
  vec2 q = (uv - uFillBox.xy)/max(uFillBox.z, 0.02);
  q.x *= uAspect;
  float t = uT*0.03 + uFillBox.w;
  vec3 c;
  if(uFillKind == 2){
    c = mix(vec3(0.004, 0.006, 0.020), vec3(0.020, 0.018, 0.070), smoothstep(-1.0, 1.0, q.y));
    float neb = fbm(q*1.3 + vec2(t, 3.0));
    c += vec3(0.10, 0.05, 0.22)*smoothstep(0.42, 0.85, neb) + vec3(0.02, 0.07, 0.16)*smoothstep(0.5, 0.9, fbm(q*2.1+9.0));
    vec2 g = q*26.0; vec2 id = floor(g); vec2 f = fract(g)-0.5;
    float h = hash21(id);
    vec2 off = (vec2(hash21(id+3.1), hash21(id+7.7))-0.5)*0.7;
    float s = exp(-dot(f-off, f-off)*(60.0+200.0*h))*step(0.55, h);
    c += vec3(1.0, 0.95, 0.85)*s*(0.6+3.0*h*h)*(0.7+0.3*sin(uT*(1.0+3.0*h)+h*40.0));
    return c;
  }
  float n = fbm(q*1.6 + vec2(t, 0.0)) + 0.30*fbm3(q*4.3 + vec2(-t, 2.0));
  float n2 = fbm(q*1.6 + vec2(t, 0.0) + vec2(0.05, -0.10)) + 0.30*fbm3((q+vec2(0.05, -0.10))*4.3 + vec2(-t, 2.0));
  float dens = smoothstep(0.44, 0.80, n);
  float lit = clamp(0.5 + (n - n2)*3.0, 0.0, 1.0);        // lit from below, where the sun is
  if(uFillKind == 1){
    float y = clamp(q.y*0.5+0.5, 0.0, 1.0);
    c = mix(vec3(0.80, 0.27, 0.07), vec3(0.34, 0.085, 0.15), smoothstep(0.0, 0.40, y));
    c = mix(c, vec3(0.018, 0.035, 0.14), smoothstep(0.26, 0.90, y));
    vec2 sq = q-vec2(0.12, -0.62);
    c += vec3(1.6, 0.85, 0.28)*(exp(-dot(sq, sq)*9.0) + 0.35*exp(-dot(sq, sq)*1.8));
    float under = clamp(0.5 + (n - n2)*4.5, 0.0, 1.0);
    vec3 cc = mix(vec3(0.016, 0.018, 0.060), vec3(1.05, 0.34, 0.10), under*under*smoothstep(0.9, -0.4, q.y));
    c = mix(c, cc, smoothstep(0.50, 0.66, n)*0.95);
  } else if(uFillKind == 3){
    float y = clamp(q.y*0.5+0.5, 0.0, 1.0);
    c = mix(vec3(0.80, 0.70, 0.55), vec3(0.14, 0.36, 0.78), smoothstep(0.0, 0.8, y));
    c = mix(c, mix(vec3(0.36, 0.42, 0.58), vec3(1.15, 1.08, 0.98), lit), dens*0.9);
  } else {
    float y = clamp(q.y*0.5+0.5, 0.0, 1.0);
    c = mix(vec3(0.30, 0.38, 0.55), vec3(0.060, 0.095, 0.22), y);
    c = mix(c, mix(vec3(0.05, 0.06, 0.12), vec3(0.95, 0.90, 0.88), lit*lit), dens*0.95);
  }
  return c;
}

void main(){
  vec3 col = texture(uBg, vUV).rgb;
  if(uBlur > 0.5){
    // where this piece of the world was at the start of the shutter
    vec2 ndc = vUV*2.0-1.0;
    vec3 d = normalize(uCamF*uFocal + uCamR*ndc.x*uAspect + uCamU*ndc.y);
    float dist = (d.y < 0.0 && uCamPos.y/(-d.y) < uShore) ? uCamPos.y/(-d.y) : 2.0e4;
    vec4 pc = uPrevVP*vec4(uCamPos + d*dist, 1.0);
    if(pc.w > 0.0){
      vec2 mv = vUV - (pc.xy/pc.w*0.5+0.5);
      float L = length(mv*uRes);
      if(L > 1.5){
        mv *= min(1.0, 0.22*uRes.y/L);
        vec3 acc = col;
        for(int i=1;i<8;i++){
          acc += texture(uBg, vUV - mv*(float(i)/7.0)).rgb;
        }
        col = acc/8.0;
      }
    }
  }
  if(uMaskOn > 0.5){
    vec4 m = texture(uMask, vUV);
    float cd = smoothstep(0.25, 0.80, m.r)*uDarkK;
    col = mix(col, col*0.06 + uDarkTint, cd);
    float cs = smoothstep(0.25, 0.80, m.g);
    if(cs > 0.001){
      vec3 f = (uFillKind == 4 ? texture(uBg2, vUV).rgb : fill(vUV))*uFillTint;
      col = mix(col, f, cs*uSkyK);
      col += f*uFillEdge*4.0*cs*(1.0-cs)*uSkyK;          // a light rim along the edge of the shape
    }
  }
  if(uPaintOn > 0.5){                                  // painted points: true colour over the scene, under the light
    vec4 pt = texture(uPaintT, vUV);
    col = col*(1.0 - clamp(pt.a, 0.0, 1.0)) + pt.rgb;
  }
  col += texture(uRayA, vUV).rgb*uRayK.x + texture(uRayB, vUV).rgb*uRayK.y;
  for(int i=0;i<uNBurst;i++){
    vec2 q = (vUV - uBurst[i].xy)*vec2(uAspect, 1.0);
    float r = length(q);
    float ang = atan(q.y, q.x);
    float streak = 0.75 + 0.25*vnoise(vec2(ang*9.0, 1.7+float(i))) + 0.20*vnoise(vec2(ang*31.0, 5.1));
    float g = exp(-r*r/(uBurst[i].z*uBurst[i].z))*1.6 + 0.55*exp(-r/(uBurst[i].z*2.2))*streak;
    col += uBurstCol[i]*uBurst[i].w*(g + 0.40*smoothstep(0.5, 3.0, uBurst[i].w));
  }
  o = vec4(col, 1.0);
}
"""
