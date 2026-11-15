"""GLSL programs for the creatures of light (engine/creatures.py): soft strokes and soft points.

Every shape of a dove or a butterfly is a soft tapered stroke (a capsule from a to b whose half width eases from
wa to wb), lit as a glassy fill, a bright rim and a faint halo. Sparks and fireflies are soft points. All of it is
light added to the glow layer, so the engine's bloom, text protection and water reflections apply as usual.
"""

STROKE_VS = """
#version 330
in vec2 aCorner;
in vec2 aA; in vec2 aB; in vec2 aW; in vec4 aStyle; in vec3 aCol;
uniform vec2 uRes;
out vec2 vP;
flat out vec2 vA; flat out vec2 vB; flat out vec2 vW; flat out vec4 vS; flat out vec3 vC;
void main(){
  vec2 a = aA*uRes, b = aB*uRes;
  vec2 d = b-a; float L = length(d);
  vec2 dir = L > 1e-4 ? d/L : vec2(1.0, 0.0);
  vec2 n = vec2(-dir.y, dir.x);
  float w = max(aW.x, aW.y);
  float m = w*(1.0 + 3.0*step(0.001, aStyle.z)) + 3.0;   // room for the soft edge and the halo
  vec2 p = mix(a - dir*m, b + dir*m, aCorner.x*0.5+0.5) + n*m*aCorner.y;
  vP = p; vA = a; vB = b; vW = aW; vS = aStyle; vC = aCol;
  gl_Position = vec4(p/uRes*2.0-1.0, 0.0, 1.0);
}
"""

STROKE_FS = """
#version 330
in vec2 vP;
flat in vec2 vA; flat in vec2 vB; flat in vec2 vW; flat in vec4 vS; flat in vec3 vC;
out vec4 o;
void main(){
  vec2 pa = vP-vA, ba = vB-vA;
  float h = clamp(dot(pa, ba)/max(dot(ba, ba), 1e-6), 0.0, 1.0);
  float d = length(pa - ba*h);
  float w = max(mix(vW.x, vW.y, h), 0.6);
  float fill = 1.0 - smoothstep(w-0.8, w+0.8, d);
  float rw = max(0.9, 0.22*w);
  float rim = exp(-pow((d - w + 0.5*rw)/rw, 2.0));
  float halo = exp(-max(d - w, 0.0)/(1.4*w + 1.0)) * (1.0 - 0.6*fill);
  // the glassy fill is brighter toward the stroke's axis, like light inside a shape
  float inner = fill*(0.55 + 0.45*(1.0 - d/w));
  o = vec4(vC*(vS.x*inner + vS.y*rim + vS.z*halo), 1.0);
}
"""

POINT_VS = """
#version 330
in vec2 aPos; in float aSize; in vec3 aCol;
uniform float uPx;
out vec3 vC;
void main(){
  vC = aCol;
  gl_Position = vec4(aPos*2.0-1.0, 0.0, 1.0);
  gl_PointSize = aSize*uPx;
}
"""

POINT_FS = """
#version 330
in vec3 vC; out vec4 o;
void main(){
  vec2 p = gl_PointCoord*2.0-1.0; float r2 = dot(p, p); if(r2 > 1.0) discard;
  float k = exp(-r2*7.0) + 0.28*exp(-r2*2.2)*(1.0 - r2);
  o = vec4(vC*k, 1.0);
}
"""
