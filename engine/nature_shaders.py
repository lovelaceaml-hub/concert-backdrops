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
