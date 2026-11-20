import {useCallback,useEffect,useLayoutEffect,useMemo,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Canvas,useThree} from '@react-three/fiber';
import {Bloom,EffectComposer} from '@react-three/postprocessing';
import * as THREE from 'three';
import {Heavenly} from './scenes/Heavenly';
import type {RenderJob,RendererInfo} from './types';
import {compileMusicEvents,createCameraTrack,frameSeconds,sampleCameraTrack} from '../../shared/motion.mjs';
import type {CameraPathSpec,MusicEvent} from '../../shared/motion.mjs';
import {CAMERA_PRESET_NAMES,cameraPreset,createPhraseEvents,createShotTemplate} from '../../shared/shot-templates.mjs';
import type {CameraPresetName} from '../../shared/shot-templates.mjs';
import '@fontsource/cormorant-garamond/400.css';
import '@fontsource/jost/400.css';
import './studio.css';

const demo:RenderJob={project_id:'celestial-study',shot:createShotTemplate('reveal',{id:'light-study',duration_frames:360,fps:60}),video:{width:1280,height:720,fps:60},seed:2026,frames:[],out_dir:'',timing:{events:createPhraseEvents({start_frame:30,peak_frame:190,end_frame_exclusive:345,fps:60})}};
const capture=new URLSearchParams(location.search).has('capture');
const job=window.__RENDER_JOB__??demo;

type CameraPath=CameraPresetName|'custom';
const duration=(job.shot.end_frame_exclusive-job.shot.start_frame)/job.video.fps;
const initialCamera:CameraPath=job.shot.params?.camera_path?'custom':CAMERA_PRESET_NAMES.includes(job.shot.params?.camera as CameraPresetName)?job.shot.params?.camera as CameraPresetName:'orbit';
const events=compileMusicEvents((job.timing?.events??[]) as MusicEvent[],job.video.fps);
function Draw({frame,token,bloom,cameraPath,onDraw}:{frame:number;token:number;bloom:boolean;cameraPath:CameraPath;onDraw:(info:RendererInfo)=>void}) {
  const {gl,camera,advance}=useThree();
  const track=useMemo(()=>createCameraTrack(cameraPath==='custom'?job.shot.params?.camera_path as CameraPathSpec:cameraPreset(cameraPath,duration),duration),[cameraPath]);
  useLayoutEffect(()=>{
    const pose=sampleCameraTrack(track,frameSeconds(frame,job.video.fps,job.shot.start_frame));
    camera.position.set(...pose.position);
    camera.up.set(...pose.up);
    camera.lookAt(...pose.target);
    camera.updateMatrixWorld();
    let a=0,b=0;
    a=requestAnimationFrame(()=>{
      b=requestAnimationFrame(()=>{
        advance(frame/job.video.fps,true);
        advance(frame/job.video.fps,true);
        const ctx=gl.getContext();
        ctx.finish();
        const extension=ctx.getExtension('WEBGL_debug_renderer_info');
        const renderer=extension?String(ctx.getParameter(extension.UNMASKED_RENDERER_WEBGL)):String(ctx.getParameter(ctx.RENDERER));
        const vendor=extension?String(ctx.getParameter(extension.UNMASKED_VENDOR_WEBGL)):String(ctx.getParameter(ctx.VENDOR));
        onDraw({vendor,renderer,webglVersion:String(ctx.getParameter(ctx.VERSION)),software:/swiftshader|llvmpipe|software/i.test(renderer),frame,seed:job.seed,fps:job.video.fps});
      });
    });
    return ()=>{cancelAnimationFrame(a);cancelAnimationFrame(b);};
  },[frame,token,bloom,track,gl,camera,advance,onDraw]);
  return <>
    <Heavenly frame={frame} fps={job.video.fps} seed={job.seed} startFrame={job.shot.start_frame} endFrame={job.shot.end_frame_exclusive} events={events} motionAmount={Number(job.shot.params?.motion_amount??1)} musicAmount={Number(job.shot.params?.music_amount??0.15)}/>
    <EffectComposer multisampling={0}>
      <Bloom intensity={bloom?0.32:0} luminanceThreshold={1.1} luminanceSmoothing={0.35} mipmapBlur/>
    </EffectComposer>
  </>;
}

function Studio() {
  const [frame,setFrame]=useState(job.shot.start_frame);
  const [token,setToken]=useState(0);
  const [bloom,setBloom]=useState(job.shot.params?.bloom!==false);
  const [cameraPath,setCameraPath]=useState<CameraPath>(initialCamera);
  const [info,setInfo]=useState<RendererInfo>();
  const pending=useRef<((info:RendererInfo)=>void)|null>(null);
  const onDraw=useCallback((result:RendererInfo)=>{setInfo(result);window.__SCENE_READY__=true;pending.current?.(result);pending.current=null;},[]);
  useEffect(()=>{
    window.renderFrame=async next=>{
      if(!Number.isInteger(next)||next<job.shot.start_frame||next>=job.shot.end_frame_exclusive)throw new Error('Frame outside shot bounds');
      if(pending.current)throw new Error('A frame is already pending');
      await document.fonts.ready;
      return new Promise<RendererInfo>(resolve=>{
        pending.current=resolve;
        flushSync(()=>{setFrame(next);setToken(v=>v+1);});
      });
    };
    return ()=>{delete window.renderFrame;};
  },[]);
  const jump=(next:number)=>{setFrame(Math.max(job.shot.start_frame,Math.min(next,job.shot.end_frame_exclusive-1)));setToken(v=>v+1);};
  const viewport=<div className="viewport" style={capture?{width:job.video.width,height:job.video.height}:{aspectRatio:`${job.video.width}/${job.video.height}`}}>
    <Canvas frameloop="never" dpr={1} camera={{fov:43,near:0.1,far:150}} gl={{antialias:true,preserveDrawingBuffer:true,powerPreference:'low-power'}} onCreated={({gl})=>{gl.toneMapping=THREE.ACESFilmicToneMapping;gl.toneMappingExposure=0.9;}}>
      <Draw frame={frame} token={token} bloom={bloom} cameraPath={cameraPath} onDraw={onDraw}/>
    </Canvas>
  </div>;
  if(capture)return viewport;
  return <main className="studio">
    <header><div className="wordmark">CONCERT <span>/</span> SCENE STUDIO</div><span className="mode">{info?.software?'SOFTWARE PREVIEW':info?'DEVICE PREVIEW':'CHECKING DEVICE'}</span></header>
    <section className="heading"><div><p className="eyebrow">LIGHT STUDY 01</p><h1>Pavilion of light</h1><p className="intro">Shape the movement. Preserve the moment.</p></div><div className="spec"><strong>{job.video.width} x {job.video.height}</strong><span>{job.video.fps} fps / seed {job.seed}</span></div></section>
    <section className="canvas-card">{viewport}<div className="canvas-note"><span>Procedural geometry / no external imagery</span><span>Three.js + React Postprocessing</span></div></section>
    <section className="transport"><button onClick={()=>jump(frame-1)} aria-label="Previous frame">Previous</button><input aria-label="Timeline frame" type="range" min={job.shot.start_frame} max={job.shot.end_frame_exclusive-1} value={frame} onChange={e=>jump(Number(e.target.value))}/><button onClick={()=>jump(frame+1)} aria-label="Next frame">Next</button><output>{String(frame).padStart(5,'0')} <small>/ {job.shot.end_frame_exclusive-1}</small></output></section>
    <section className="details"><div><h2>Look controls</h2><label><input type="checkbox" checked={bloom} onChange={e=>{setBloom(e.target.checked);setToken(v=>v+1);}}/> Soft bloom</label><label className="camera-control">Camera <select value={cameraPath} onChange={e=>{setCameraPath(e.target.value as CameraPath);setToken(v=>v+1);}}>{job.shot.params?.camera_path?<option value="custom">Authored path</option>:null}<option value="orbit">Gentle orbit</option><option value="push-in">Slow push in</option><option value="fly-through">Gliding fly through</option><option value="locked">Locked</option></select></label><p>Camera and ribbons ease through the phrase. Scrubbing always preserves the same motion.</p></div><div><h2>Rendering device</h2><p className="device">{info?.renderer??'Initializing WebGL...'}</p><p>{info?.software?'Software rendering detected. Final rendering uses the configured pipeline.':'Hardware status comes from the active WebGL context.'}</p></div><div><h2>Production status</h2><p className="status">Cloud GPU provider unconfigured</p><p>This original study tests the tools. It is separate from approved concert films.</p></div></section>
  </main>;
}

createRoot(document.getElementById('root')!).render(<Studio/>);
