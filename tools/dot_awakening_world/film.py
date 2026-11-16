"""A loving word awakens a world: complete local procedural 3D creative draft."""
import os,sys,time,json,subprocess,argparse,math
from pathlib import Path
os.environ.update(LIBGL_ALWAYS_SOFTWARE='1',LP_NUM_THREADS='2',MESA_SHADER_CACHE_DIR='/tmp/dot-awakening-world/mesa')
import moderngl as gl
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(os.environ.get('DOT_ENGINE_ROOT','/tmp/concert-dot-render'));OUT=Path(os.environ.get('DOT_FILM_OUT','/tmp/dot-awakening-world'));OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'engine'))
from p3d import words as PW,brand as BR
W,H,FPS=960,540,60
RW,RH=(1920,1080) if os.environ.get("DOT_RES")=="1080p" else (W,H)
ctx=gl.create_standalone_context(backend='egl');ctx.enable(gl.PROGRAM_POINT_SIZE)
ct=ctx.texture((RW,RH),3);dt=ctx.depth_renderbuffer((RW,RH));fb=ctx.framebuffer([ct],dt);fb.use()
landim=Image.open(ROOT/'assets/p3d/brand/land_2048.png').convert('L').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
land=ctx.texture(landim.size,1,landim.tobytes());land.filter=(gl.LINEAR,gl.LINEAR)
VS='''#version 330
in vec2 pos;out vec2 uv;void main(){uv=pos*.5+.5;gl_Position=vec4(pos,0,1);}'''
COMMON='''
float ease(float a,float b,float t){float u=clamp((t-a)/(b-a),0.,1.);return u*u*(3.-2.*u);}
float river(float z){return 2.*sin(z*.10)+.65*sin(z*.27);}
float terrain(vec2 p){float d=abs(p.x-river(p.y));float b=ease(.95,5.8,d);return b*(3.1+1.1*sin(p.x*.31)*sin(p.y*.21)+.65*sin(p.x*.71+p.y*.33)+.11*d);}
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
vec3 sky(vec3 rd,float T){float h=clamp(rd.y*.7+.35,0.,1.);vec3 c=mix(vec3(.98,.66,.34),vec3(.45,.43,.65),h);float cloud=noise(rd.xz/max(.15,rd.y+.5)*3.+T*.008);cloud=.65*cloud+.35*noise(rd.xz/max(.15,rd.y+.5)*7.-T*.006);c=mix(c,vec3(1.,.80,.63),smoothstep(.38,.72,cloud)*.65);float sun=pow(max(0.,dot(rd,normalize(vec3(-.5,.7,-.4)))),65.);return c+sun*vec3(.22,.16,.07);}
'''
FS='''#version 330
in vec2 uv;out vec4 frag;uniform float T;uniform vec2 resolution;uniform vec3 eye,fw,rt,up;uniform sampler2D earth;
'''+COMMON+'''
void main(){vec2 xy=(uv*2.-1.)*vec2(resolution.x/resolution.y,1.);vec3 rd=normalize(fw+rt*xy.x*.48+up*xy.y*.48);vec3 col=sky(rd,T);float depth=130.;
float t=.1;vec3 p;bool hit=false;
for(int k=0;k<105;k++){p=eye+rd*t;float h=p.y-terrain(p.xz);if(h<.025){hit=true;break;}t+=max(.09,h*.48);if(t>120.)break;}
if(hit){depth=t;float h=terrain(p.xz);vec2 e=vec2(.035,0);vec3 n=normalize(vec3(terrain(p.xz-e.xy)-terrain(p.xz+e.xy),.07,terrain(p.xz-e.yx)-terrain(p.xz+e.yx)));float dist=abs(p.x-river(p.z));float sun=max(0.,dot(n,normalize(vec3(-.5,.8,.3))));float detail=noise(p.xz*7.);float softshadow=1.;
for(int k=1;k<7;k++){vec3 q=p+normalize(vec3(-.5,.8,.3))*float(k)*.5;if(q.y<terrain(q.xz)+.05)softshadow*=.86;}
vec3 ground=mix(vec3(.47,.35,.54),vec3(.88,.57,.52),.4+.4*noise(p.xz*.35));ground*=.56+.44*sun*softshadow;ground+=detail*.035;
if(dist<1.05){vec3 refl=sky(reflect(rd,vec3(0,1,0)),T);float ribbon=pow(.5+.5*sin(p.z*.8-T*1.2+sin(p.x*2.)),4.);float wave=1.-ease((T-7.1)*1.8,(T-7.1)*1.8+2.,5.-p.z);float water=.008*sin(p.z*2.+T*.7)+.005*sin(p.x*4.-T*.4);
ground=mix(vec3(.35,.37,.43),refl,.65)+vec3(.5,.30,.06)*wave*(.25+.65*ribbon)+water;
float ripple=exp(-pow((length(p.xz-vec2(river(5.),5.))-(T-7.2)*3.)*4.,2.))*ease(7.2,7.4,T)*(1.-ease(9.,10.,T));ground+=ripple*vec3(.6,.35,.1);}
float mist=1.-exp(-t*.018);col=mix(ground,sky(rd,T),mist*.66);}
// A real sphere of the world rises beyond the awakening garden.
if(T>44.){vec3 center=vec3(river(-44.),12.,-48.);float radius=6.5*ease(44.,47.,T);vec3 oc=eye-center;float b=dot(oc,rd),c=dot(oc,oc)-radius*radius,disc=b*b-c;
if(disc>0.){float d=-b-sqrt(disc);if(d>0.&&d<depth){vec3 n=normalize(eye+rd*d-center);vec2 st=vec2(atan(n.z,n.x)/6.283185+.5+T*.003,asin(n.y)/3.141592+.5);float l=texture(earth,st).r;float lit=.48+.52*max(0.,dot(n,normalize(vec3(-.4,.7,.4))));vec3 ec=mix(vec3(.24,.55,.75),vec3(.94,.75,.36),l);float grid=pow(.5+.5*cos(st.x*6.283185*18.),80.)+pow(.5+.5*cos(st.y*3.141592*18.),80.);col=ec*lit+grid*.035;col+=pow(1.-max(0.,dot(-rd,n)),3.)*vec3(.20,.23,.22);depth=d;}}}
// Small gold drop: ray-sphere with warm reflective shading, descending to the river.
if(T<7.35){float y=1.9-1.75*ease(5.5,7.3,T);vec3 center=vec3(river(5.),y,5.);float r=.16;vec3 oc=eye-center;float b=dot(oc,rd),c=dot(oc,oc)-r*r,dis=b*b-c;if(dis>0.){float d=-b-sqrt(dis);if(d>0.&&d<depth){vec3 n=normalize(eye+rd*d-center);col=vec3(.98,.69,.22)*(.55+.45*max(0.,dot(n,normalize(vec3(-.3,.7,.7)))));col+=pow(max(0.,dot(reflect(rd,n),normalize(vec3(-.3,.7,.7)))),20.)*.3;depth=d;}}}
// Depth fog is spatial: near banks retain contrast, the distant valley stays luminous.
float beam=pow(max(0.,sin((eye.x+rd.x*depth*.45)*.55+(eye.z+rd.z*depth*.45)*.14)),16.);
col+=beam*.035*vec3(1.,.72,.4)*(1.-exp(-depth*.04));
col=clamp(col,0.,.99);frag=vec4(col,1.);float z=depth*dot(rd,fw);gl_FragDepth=min(.99999,.5*((150.+.08)/(150.-.08)-2.*150.*.08/(150.-.08)/max(z,.08))+.5);
}'''
pr=ctx.program(vertex_shader=VS,fragment_shader=FS);quad=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],np.float32).tobytes());qvao=ctx.simple_vertex_array(pr,quad,'pos')
PVS='''#version 330
in vec4 in_pos;in vec4 in_color;uniform float T;uniform vec2 resolution;uniform vec3 eye,fw,rt,up;out vec4 color;
void main(){vec3 p=in_pos.xyz;vec3 r=p-eye;float d=dot(r,fw);gl_Position=vec4(dot(r,rt)/(.48*resolution.x/resolution.y),dot(r,up)/.48,((150.+.08)/(150.-.08))*d-2.*150.*.08/(150.-.08),d);gl_PointSize=clamp(in_pos.w*resolution.y/(max(d,.1)*.48),1.,70.);color=in_color;color.a*=smoothstep(.15,.6,d);}'''
PFS='''#version 330
in vec4 color;out vec4 frag;void main(){vec2 q=gl_PointCoord*2.-1.;float r=dot(q,q);if(r>1.)discard;float a=exp(-r*5.)*color.a;frag=vec4(color.rgb*a,a);}'''
pp=ctx.program(vertex_shader=PVS,fragment_shader=PFS);buf=ctx.buffer(reserve=30000*8*4);pvao=ctx.vertex_array(pp,[(buf,'4f 4f','in_pos','in_color')])
rng=np.random.default_rng(52)
ambient=np.c_[rng.uniform(-14,14,2200),rng.uniform(.5,14,2200),rng.uniform(-62,14,2200)];seeds=rng.random(2200)
leafseed=rng.random((2800,4))
garden=rng.random((4000,4))
COL=np.array([[int(PW.COLORS[k].lstrip('#')[j:j+2],16)/255 for j in (0,2,4)] for k in PW.LABELS])
def ease(a,b,x):
 u=np.clip((x-a)/(b-a),0,1);return u*u*(3-2*u)
def river(z):return 2*np.sin(z*.1)+.65*np.sin(z*.27)
def terrain(x,z):
 d=np.abs(x-river(z));return ease(.95,5.8,d)*(3.1+1.1*np.sin(x*.31)*np.sin(z*.21)+.65*np.sin(x*.71+z*.33)+.11*d)
def camera(t):
 if t<7.5:
  eye=np.array([3.2-.2*t,3.,12.-.1*t]);target=np.array([river(5.),1.35,5.])
 elif t<44:
  u=(t-7.5)/36.5;z=10-40*ease(0,1,u);x=river(z)+2*np.sin(t*.16);eye=np.array([x,2.4+.65*np.sin(t*.15),z]);target=np.array([river(z-9),1.2,z-9])
 else:
  e=ease(44,54,t);eye=np.array([river(-30)+5*(1-e),3+19*e,-30+23*e]);target=np.array([river(-44),3+9*e,-44])
 fw=target-eye;fw/=np.linalg.norm(fw);rt=np.cross(fw,[0,1,0]);rt/=np.linalg.norm(rt);up=np.cross(rt,fw);return eye,fw,rt,up

def points(t):
 out=[]
 def add(p,size,col,alpha):
  p=np.asarray(p);n=len(p);out.append(np.c_[p,np.broadcast_to(size,(n,)),np.broadcast_to(col,(n,3)),np.broadcast_to(alpha,(n,))])
 p=ambient.copy();p[:,0]+=.2*np.sin(t*.3+seeds*30);p[:,1]+=.15*np.sin(t*.7+seeds*22)
 add(p,.025+seeds*.02,[1,.72,.35],.4+.12*np.sin(t+seeds*19))
 # Flow follows the actual winding river and is revealed by the falling drop.
 z=np.linspace(8,-48,1400);x=river(z)+.65*np.sin(z*1.4+t*1.1);y=.12+.04*np.sin(z*3-t*2)
 alpha=(1-ease((t-7.1)*1.8,(t-7.1)*1.8+2,5-z))*.7
 add(np.c_[x,y,z],.035,[1,.72,.2],alpha)
 if 8<=t<44:
  i=min(8,int((t-8)//4));v=(t-8-4*i)/4;z=3-i*4.;cx=river(z);env=float(ease(0,.15,v)*(1-ease(.85,1,v)))
  u=np.linspace(0,1,500)
  for side in [-1,1]:
   sep=1.2-.65*np.sin(v*np.pi)**2;px=cx+side*sep;py=1.1
   if i==1:py+=.3*np.sin(v*np.pi)
   if i==2:py+=side*.3*(1-ease(.1,.8,v))
   if i==3:px=cx+side*.8
   if i==4:px=cx+side*(1.2+ease(.1,.8,v))
   if i==5:py+=.28*np.sin(v*2*np.pi+side*np.pi/2)
   if i==6:py+=.5*ease(.1,.8,v)
   if i==7:py+=.7*ease(.1,.8,v)
   if i==8:py+=.5*np.sin(v*np.pi)
   phase=u*2*np.pi*7
   cluster=np.c_[px+.12*np.cos(phase)*np.sin(u*np.pi),py+.16*np.sin(phase),np.full_like(u,z)+.12*np.cos(u*31)]
   add(cluster,.03,COL[i]*.4+np.array([.6,.45,.23]),env*.55)
  # A continuous ribbon changes its action: gift, shelter, yielding path, support.
  x=cx+(u-.5)*2.6;y=.35+np.sin(np.pi*u)*(1.2 if i in [3,6,7] else .35)
  if i==2:y+=.4*np.sin(u*16)*(1-ease(.1,.8,v))
  if i==4:x=cx+(u-.5)*(1+2*ease(.1,.8,v));y=.3+1.5*np.sin(np.pi*u)
  add(np.c_[x,y,np.full_like(u,z)],.028,COL[i]*.45+np.array([.55,.4,.2]),env*.65)
 # Nine planted blooms awaken sequentially along the river, all in real world coordinates.
 for k in range(18):
  z=-k*2.6+5;side=-1 if k%2 else 1;x=river(z)+side*(2.2+.4*np.sin(k));base=terrain(x,z)
  bloom=float(ease(7+k*1.9,9+k*1.9,t));u=np.linspace(0,1,90)
  for petal in range(5):
   a=petal*2*np.pi/5+.12*np.sin(t*.3+k);r=.65*np.sin(np.pi*u)*bloom
   pp0=np.c_[x+r*np.cos(a),base+.2+u*.7*bloom+.18*np.sin(np.pi*u),z+r*np.sin(a)]
   add(pp0,.035,COL[k%9]*.35+np.array([.65,.48,.27]),.7*bloom)
 # Spatial blossom masses cover the banks as the word passes them.
 z=8-58*garden[:,0];side=np.where(garden[:,1]<.5,-1,1);x=river(z)+side*(1.7+5*garden[:,2]);y=terrain(x,z)+.18+.3*garden[:,3]
 bloom=ease(7,10,t-(5-z)/1.8)
 color=np.c_[.82+.18*garden[:,1],.42+.26*garden[:,2],.55+.27*garden[:,3]]
 add(np.c_[x,y,z],.08+.09*garden[:,3],color,bloom*.75)
 # The lit river becomes a rooted branching tree, then carries light to the world.
 root=np.array([river(-42),0,-42]);grow=float(ease(39,47,t));u=np.linspace(0,1,450)
 for i in range(9):
  a=i*2*np.pi/9;r=5.5*u*u*grow
  p=np.c_[root[0]+r*np.cos(a),u*11*grow,root[2]+r*np.sin(a)]
  add(p,.055,COL[i]*.35+np.array([.65,.48,.25]),grow*.65)
 if grow>0:
  a=leafseed[:,0]*2*np.pi;r=(2+4*leafseed[:,1])*grow
  crown=np.c_[root[0]+r*np.cos(a),7.3*grow+3.8*grow*leafseed[:,2],root[2]+r*np.sin(a)]
  crown[:,1]+=.12*np.sin(t*.6+leafseed[:,3]*30)
  add(crown,.065+leafseed[:,3]*.06,np.array([1.,.68,.47]),grow*.35)
 if t>44:
  for i in range(9):
   a=i*2*np.pi/9+(t-44)*.18;r=7.4
   p=np.array([[river(-44)+r*np.cos(a),12+r*.75*np.sin(a),-46.]])
   add(p,.18,COL[i]*.4+.6,float(ease(44,47,t)*(1-ease(52,54,t))))
 return np.concatenate(out).astype('f4')
# Cache all typography and logo plates, independent of the expensive 3D pass.
FONT=ROOT/'fonts'
def font(name,size,weight=500,italic=False):return ImageFont.truetype(str(FONT/f'{name}-latin-{weight}-{"italic" if italic else "normal"}.ttf'),size)
logo=BR.logo_image(height=170).convert('RGBA')
def label(im,text,y,f,fill,anchor='mm',x=W/2):ImageDraw.Draw(im).text((x,y),text,font=f,fill=fill,anchor=anchor)
def plate():return Image.new('RGBA',(W,H),(0,0,0,0))
opening=plate();opening.alpha_composite(logo.resize((100,81)),(430,28))
label(opening,'HEALING CONCERT',126,font('jost',18), '#9f6827')
label(opening,"The Words of Mother's Love",174,font('cormorant-garamond',48),'#272751')
label(opening,'That Bring Peace',219,font('cormorant-garamond',39,500,True),'#272751')
label(opening,'SUNDAY, DECEMBER 6  ·  4:30 PM',269,font('jost',23),'#272751')
label(opening,'LAS VEGAS',300,font('jost',15),'#9f6827')
end=plate();end.alpha_composite(logo.resize((116,94)),(422,28))
label(end,'HEALING CONCERT',144,font('outfit',18,600),'#f35763');label(end,'The Words of',185,font('outfit',32,500),'#272751')
label(end,"Mother's Love",244,font('outfit',66,800),'#f35763');label(end,'That Bring Peace',309,font('outfit',50,800),'#0345a5')
ImageDraw.Draw(end).rounded_rectangle((172,352,788,398),radius=3,fill='#f35763')
label(end,'Sunday, December 6',374,font('outfit',26,600),'#ffe478',x=402)
label(end,'4:30 PM',374,font('outfit',26,600),'#ffffff',x=654)
label(end,'World Mission Society Church of God',436,font('outfit',23,500),'#272751')
label(end,'6720 W Sahara Ave, Las Vegas',471,font('outfit',23,500),'#272751')
sig=plate();sig.alpha_composite(logo.resize((50,41)),(24,459))
label(sig,"The Words of Mother's Love That Bring Peace",467,font('cormorant-garamond',19,500,True),'#272751',x=82,anchor='lm')
label(sig,'DEC 6 · 4:30 PM',488,font('jost',16),'#272751',x=82,anchor='lm')
words=[]
for e in PW.EXPRESSIONS:
 im=plate();name=e['label'];text=e.get('text',e.get('phrase',''))
 # Use the source phrase fields, not newly paraphrased wording.
 if not text:text=' '.join(e['lines'])
 f=font('cormorant-garamond',40,600,True);lines=[];line=''
 for w in text.split():
  trial=(line+' '+w).strip()
  if ImageDraw.Draw(im).textlength(trial,font=f)>780 and line:lines.append(line);line=w
  else:line=trial
 lines.append(line)
 label(im,name.upper(),125,font('jost',17,600),PW.COLORS[name])
 for j,line in enumerate(lines):label(im,line,167+j*43,f,'#272751')
 words.append(im)

def frame(t):
 fb.clear(0,0,0,1,depth=1);ctx.enable(gl.DEPTH_TEST);ctx.disable(gl.BLEND)
 eye,fw,rt,up=camera(t)
 for p in [pr,pp]:
  
  if 'T' in p:p['T'].value=t
  p['resolution'].value=(RW,RH)
  for key,value in [('eye',eye),('fw',fw),('rt',rt),('up',up)]:p[key].value=tuple(value)
 land.use(0);pr['earth'].value=0;qvao.render(gl.TRIANGLE_STRIP)
 data=points(t);buf.write(data.tobytes());ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);ctx.depth_mask=False;pvao.render(gl.POINTS,vertices=len(data));ctx.depth_mask=True
 image=Image.frombytes('RGB',(RW,RH),fb.read(components=3,alignment=1)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGBA')
 if t<8:
  amount=1-float(ease(7,8,t));layer=opening.copy();layer.putalpha(layer.getchannel('A').point(lambda x:int(x*amount)));image.alpha_composite(layer.resize((RW,RH),Image.Resampling.LANCZOS))
 elif t<54.8:image.alpha_composite(sig.resize((RW,RH),Image.Resampling.LANCZOS))
 if 8<=t<44:
  i=min(8,int((t-8)//4));v=t-8-i*4;amount=float(ease(0,.3,v)*(1-ease(3.6,4,v)));layer=words[i].copy();layer.putalpha(layer.getchannel('A').point(lambda x:int(x*amount)));image.alpha_composite(layer.resize((RW,RH),Image.Resampling.LANCZOS))
 if t>=54:
  amount=float(ease(54,54.8,t));yy,xx=np.mgrid[:RH,:RW];sway=.025*np.sin(t*.28);c=np.empty((RH,RW,4),np.uint8);c[:,:,0]=np.clip(249-12*xx/RW+5*yy/RH,0,255);c[:,:,1]=np.clip(230+9*xx/RW+5*np.sin(t*.3),0,255);c[:,:,2]=np.clip(217+28*xx/RW+4*np.cos(t*.2),0,255);c[:,:,3]=round(255*amount);image.alpha_composite(Image.fromarray(c))
  card=end.copy();card.putalpha(card.getchannel('A').point(lambda x:int(x*amount)));image.alpha_composite(card.resize((RW,RH),Image.Resampling.LANCZOS))
  scale=1+.006*float(ease(55,61,t));ww,hh=RW/scale,RH/scale;image=image.transform((RW,RH),Image.Transform.EXTENT,((RW-ww)/2,(RH-hh)/2,(RW+ww)/2,(RH+hh)/2),Image.Resampling.BICUBIC)
 return image.convert('RGB')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills');ap.add_argument('--range',nargs=2,type=int,default=[0,3720]);ap.add_argument('--name',default='silent');a=ap.parse_args()
 if a.stills:
  for t in map(float,a.stills.split(',')):frame(t).save(OUT/f'frame-{t:.2f}.png')
 else:
  ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{RW}x{RH}','-r',str(FPS),'-i','-','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/(a.name+'.mp4'))],stdin=subprocess.PIPE)
  start=time.monotonic()
  for i in range(*a.range):
   ff.stdin.write(frame(i/FPS).tobytes())
   if i%120==0:print(i,round(time.monotonic()-start,2),flush=True)
  ff.stdin.close();assert ff.wait()==0
  (OUT/(a.name+'.json')).write_text(json.dumps(dict(first=a.range[0],last=a.range[1],frames=a.range[1]-a.range[0],seconds=time.monotonic()-start)))
