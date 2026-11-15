"""Shaders for the living nature layers (engine/nature.py): one soft glow point, and the falling water sheet."""
from shaders import NOISE

# every flower petal, stem, branch, leaf, blossom, droplet and stream glint is a soft point of light;
# positions are fractions of the screen (y from the bottom), sizes are pixels at 1080p
GLOW_VS = """
#version 330
in vec2 aPos; in float aSize; in vec3 aCol; in float aSharp;
uniform float uPx;
out vec3 vCol; out float vSharp;
void main(){
  vCol = aCol; vSharp = aSharp;
  gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0);
  gl_PointSize = max(aSize*uPx, 1.0);
}
"""
GLOW_FS = """
#version 330
in vec3 vCol; in float vSharp; out vec4 o;
void main(){
  vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p,p); if(r2>1.0) discard;
  float a = (exp(-r2*vSharp)-exp(-vSharp))/(1.0-exp(-vSharp));
  o = vec4(vCol*a, 1.0);
}
"""

# a quad drawn only over the waterfall's box; vUV is the screen position (y from the bottom)
RECT_VS = """
#version 330
in vec2 aPos;
uniform vec4 uRect;   // x0, y0, x1, y1 in screen fractions
out vec2 vUV;
void main(){ vUV = mix(uRect.xy, uRect.zw, aPos*0.5+0.5); gl_Position = vec4(vUV*2.0-1.0, 0.0, 1.0); }
"""

# falling light-water: streaks that pour down and speed up, a bright lip at the top, foam and mist at the foot
FALL_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uAmt, uX, uTop, uBot, uW, uCalm, uCalmY;
uniform vec3 uColA, uColB;
void main(){
  float H = max(uTop-uBot, 0.02);
  float v = clamp((uTop-vUV.y)/H, 0.0, 1.4);        // 0 at the lip, 1 at the foot
  float hw = uW*(0.5+0.35*v);                       // half width, widening as it falls
  float sway = 0.004*sin(uT*0.7+v*5.0)*v;
  float dx = (vUV.x-uX-sway)*uAspect;
  float u = dx/hw;                                  // -1..1 across the fall
  float body = smoothstep(1.0, 0.6, abs(u))*smoothstep(-0.02, 0.06, v)*smoothstep(1.06, 0.98, v);
  // the light pours in from the top as uAmt rises
  float pour = smoothstep(uAmt*1.25, uAmt*1.25-0.12, v);
  float spd = 0.55+1.4*v;                           // accelerating
  float s1 = vnoise(vec2(u*9.0, (vUV.y+uT*0.62*spd)*7.0/H));
  float s2 = vnoise(vec2(u*23.0+3.1, (vUV.y+uT*0.95*spd)*15.0/H));
  float s3 = vnoise(vec2(u*41.0+7.7, (vUV.y+uT*1.30*spd)*26.0/H));
  float streak = pow(s1,3.0)*0.9 + pow(s2,4.0)*1.2 + pow(s3,6.0)*1.6;
  float edge = smoothstep(0.55, 1.0, abs(u))*0.6;
  float lip = exp(-pow((v-0.03)/0.035,2.0))*smoothstep(1.0,0.3,abs(u))*(0.45+0.35*vnoise(vec2(u*6.0, uT*1.5)));
  vec3 col = mix(uColA, uColB, clamp(s2*1.3-0.2,0.0,1.0));
  vec3 fall = col*(0.035 + streak*0.60 + edge*0.25)*body + uColB*lip;
  // foam and mist at the foot: soft billows that rise and drift outward
  vec2 q = vec2((vUV.x-uX)*uAspect, vUV.y-uBot);
  float r = length(q*vec2(0.55, 1.0));
  float bill = fbm3(vec2(q.x*14.0 - sign(q.x)*uT*0.25, q.y*14.0 - uT*0.45));
  float mist = exp(-r/0.040)*(0.35+0.9*bill)*smoothstep(-0.03, 0.01, q.y + 0.02)*smoothstep(0.15, 0.06, r);
  float foam = exp(-pow(q.y/0.010,2.0))*exp(-abs(q.x)/(uW*1.6))*(0.5+0.8*vnoise(vec2(q.x*60.0-uT*2.0, uT*3.0)))*smoothstep(0.25, 0.12, abs(q.x));
  float calm = 1.0-uCalm*0.6*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, vUV.y));
  vec3 c = fall*pour + (uColA*mist*0.30 + uColB*foam*0.45)*smoothstep(0.85, 1.0, uAmt*1.25);
  o = vec4(c*uAmt*calm, 1.0);
}
"""


# ------------------------------------------------------------------ paint (tint) layers
# The nature paint buffer holds premultiplied colour and coverage; the composite lays it over the scene before the
# light is added (uNatT, uNatK in shaders.COMP_FS), so flowers, water and the cliff read as colour on bright skies.

# flower petals as real petal shapes: one sprite per petal, rotated along the petal
PETAL_VS = """
#version 330
in vec2 aPos; in float aSize; in float aRot; in vec3 aCol; in float aA; in float aW;
uniform float uPx;
out float vRot; out vec3 vCol; out float vA; out float vW;
void main(){
  vRot = aRot; vCol = aCol; vA = aA; vW = aW;
  gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0);
  gl_PointSize = max(aSize*uPx, 1.0);
}
"""
PETAL_FS = """
#version 330
in float vRot; in vec3 vCol; in float vA; in float vW; out vec4 o;
uniform int uMask;   // 1: paint (premultiplied colour, coverage), 0: light (a bright rim and vein)
void main(){
  vec2 p = gl_PointCoord*2.0-1.0; p.y = -p.y;
  float c = cos(vRot), s = sin(vRot);
  p = vec2(c*p.x+s*p.y, -s*p.x+c*p.y);       // p.x along the petal (base -1, tip 1), p.y across
  float x = p.x;
  float w = vW*sqrt(max(0.0, 1.0-x*x))*(1.0+0.35*x)*(1.0-0.25*smoothstep(0.75,1.0,x));
  float body = smoothstep(w+0.02, w-0.10, abs(p.y))*smoothstep(1.0, 0.90, x)*smoothstep(-1.0, -0.88, x);
  float rim = body*(1.0-smoothstep(w-0.04, w-0.20, abs(p.y)));
  float vein = exp(-p.y*p.y/0.002)*smoothstep(1.0, -0.6, x)*body;
  float base = smoothstep(0.2, -0.9, x)*body;
  if(uMask==1){
    float a = body*vA;
    vec3 tc = vCol*(0.78+0.30*(x*0.5+0.5))*(1.0-0.25*base);
    o = vec4(tc*a, a);
    return;
  }
  o = vec4((vCol*0.25+vec3(0.20,0.18,0.14))*(rim*0.9 + vein*0.35 + base*0.25)*vA, 1.0);
}
"""

# the stream as one continuous ribbon: flowing bands and streaks, glints moving downstream, banks catching light
RIBBON_VS = """
#version 330
in vec2 aPos; in float aS; in float aU; in float aW;
out float vS; out float vU; out float vW; out float vY;
void main(){ vS = aS; vU = aU; vW = aW; vY = aPos.y; gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0); }
"""
RIBBON_FS = "#version 330\n" + NOISE + """
in float vS; in float vU; in float vW; in float vY; out vec4 o;
uniform float uT, uSpeed, uFront, uAmt, uCalm, uCalmY;
uniform vec3 uColA, uColB, uPaint;
uniform int uMask;
void main(){
  float au = abs(vU);
  float body = smoothstep(1.12, 0.86, au);
  float reach = smoothstep(uFront, uFront-0.12, vW);
  float calm = 1.0-uCalm*0.6*(1.0-smoothstep(uCalmY-0.07, uCalmY+0.05, vY));
  float k = reach*calm*uAmt;
  float tt = uT*uSpeed;
  if(uMask==1){
    float depth = 1.0-au*au*0.55;
    float a = body*0.62*k;
    o = vec4(uPaint*depth*a, a);
    return;
  }
  // flow: long streaks and broad bands carried downstream, the middle faster than the edges
  float sp = 1.0-0.45*au*au;
  float streak = pow(vnoise(vec2(vS*14.0 - tt*2.4*sp, vU*7.0)), 3.0);
  float band = pow(vnoise(vec2(vS*5.0 - tt*1.3*sp, vU*1.6 + 3.0)), 2.0);
  float ripple = 0.5+0.5*sin(vS*120.0 - tt*9.0*sp + vU*3.0 + 2.0*vnoise(vec2(vS*30.0, vU*4.0)));
  float glint = pow(vnoise(vec2(vS*160.0 - tt*7.0*sp, vU*22.0 + uT*0.7)), 12.0)*7.0;
  float bank = exp(-pow((au-0.93)/0.07, 2.0))*(0.55+0.45*vnoise(vec2(vS*50.0 - tt*1.2, 1.0)));
  vec3 c = uColA*(0.06 + streak*0.55 + band*0.30 + ripple*streak*0.25)*body + uColB*(bank*0.55 + glint*body);
  o = vec4(c*k, 1.0);
}
"""

# a soft cliff of light and shadow behind the waterfall (paint only; the composite keeps it off the text)
CLIFF_FS = "#version 330\n" + NOISE + """
in vec2 vUV; out vec4 o;
uniform float uT, uAspect, uAmt, uX, uTop, uBot, uW;
uniform vec3 uLit, uShade, uRim;
void main(){
  float H = max(uTop-uBot, 0.02);
  float v = (vUV.y-uBot)/H;                          // 0 at the foot, 1 at the lip
  float dx = (vUV.x-uX)*uAspect;
  float hw = uW*(2.4 + 1.6*(1.0-clamp(v,0.0,1.0)));  // wider at the foot
  float rough = fbm3(vec2(vUV.y*18.0, sign(dx)*3.0))*0.9 - 0.45;
  float u = dx/hw;
  float side = smoothstep(1.0+0.30*rough, 0.70+0.30*rough, abs(u));
  float topE = smoothstep(1.10+0.05*vnoise(vec2(dx*30.0,2.0)), 1.00, v);
  float foot = smoothstep(-0.12, 0.10, v);
  float a = side*topE*foot*0.80*uAmt;
  // rock: facets and ledges, lit from the open sky on the right, the wet face by the water a little darker
  float n = fbm(vec2(dx*10.0, vUV.y*14.0));
  float ledge = smoothstep(0.45, 0.62, fbm3(vec2(dx*4.0, vUV.y*30.0)));
  float light = clamp(0.40 + 0.55*u + 0.55*(n-0.5) + 0.25*ledge, 0.0, 1.0);
  float wet = exp(-pow(dx/(uW*1.2), 2.0));
  vec3 c = mix(uShade, uLit, light)*(1.0-0.20*wet);
  c = mix(c, uRim, smoothstep(0.93, 1.03, v)*0.6);   // the lit brow of the cliff
  o = vec4(c*a, a);
}
"""
