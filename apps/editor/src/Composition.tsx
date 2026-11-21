import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Audio,OffthreadVideo,Sequence,staticFile,useCurrentFrame,useVideoConfig,delayRender,continueRender} from 'remotion';
import '@fontsource/cormorant-garamond/400.css';
import '@fontsource/jost/400.css';
import type {FinishProps} from './types';
import {DEMO_SHOTS} from './timeline';
import {frameSeconds,secondaryMotion,smootherstep,titleSettle} from '../../shared/motion.mjs';

export const DemoCard:React.FC<{title:string;subtitle:string;durationInFrames?:number}>=({title,subtitle,durationInFrames=90})=>{
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const seconds=frameSeconds(frame,fps);
  const settle=titleSettle(seconds,{duration:Math.min(1.2,durationInFrames/fps*.5)});
  const motionTime=durationInFrames/fps*smootherstep(frame/durationInFrames);
  return <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 35%, #fff6d9, #e9d7b7 55%, #b7c5c5)',alignItems:'center',justifyContent:'center',fontFamily:'Cormorant Garamond, serif',color:'#504632'}}>
    {[0,1,2,3].map(i=><div key={i} style={{position:'absolute',width:570+i*145,height:570+i*145,border:'1px solid rgba(255,246,211,0.75)',borderRadius:'50%',transform:`translateY(${190+secondaryMotion(motionTime,2026,`title-ring-${i}`,3)}px) scaleY(0.32) rotate(${motionTime*1.5+i*12}deg)`,boxShadow:'0 0 12px rgba(255,228,172,.18)'}}/>)}
    <div style={{fontSize:16,letterSpacing:7,color:'#a68b52',marginBottom:25}}>CONCERT SCENE STUDIO</div>
    <div style={{fontSize:72,fontWeight:400,transform:`translateY(${settle.offset}px)`,opacity:settle.opacity}}>{title}</div>
    <div style={{fontFamily:'Jost, sans-serif',fontSize:20,letterSpacing:2,marginTop:24,color:'#81765f'}}>{subtitle}</div>
  </AbsoluteFill>;
};

export const FinishingComposition:React.FC<FinishProps>=props=>{
  const [fontHandle]=useState(()=>delayRender('Loading pinned local fonts'));
  useEffect(()=>{document.fonts.ready.then(()=>continueRender(fontHandle));},[fontHandle]);
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const titleOpacity=smootherstep(frameSeconds(frame,fps)/.8);
  return <AbsoluteFill style={{backgroundColor:'#e9d7bb'}}>
    {props.clips.length?props.clips.map((clip,i)=><Sequence key={`${i}-${clip.start_frame}`} from={clip.start_frame} durationInFrames={clip.end_frame_exclusive-clip.start_frame}>
      <OffthreadVideo src={staticFile(clip.src)} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/>
    </Sequence>):DEMO_SHOTS.map(shot=><Sequence key={shot.id} from={shot.from} durationInFrames={shot.duration}><DemoCard title={shot.title} subtitle={shot.subtitle} durationInFrames={shot.duration}/></Sequence>)}
    {props.audio_src?<Audio src={staticFile(props.audio_src)}/>:null}
    {props.show_title&&props.clips.length>0?<AbsoluteFill style={{alignItems:'center',paddingTop:props.height*.14,pointerEvents:'none'}}><div style={{fontFamily:'Cormorant Garamond, serif',fontSize:props.height*.07,color:'#fff5df',textShadow:'0 0 16px #d2ac65',opacity:titleOpacity}}>{props.title}</div></AbsoluteFill>:null}
    {(props.captions??[]).map((caption,i)=><Sequence key={i} from={caption.start_frame} durationInFrames={caption.end_frame_exclusive-caption.start_frame}>
      <AbsoluteFill style={{alignItems:'center',justifyContent:'flex-start',paddingTop:props.height*.25,paddingLeft:props.width*.10,paddingRight:props.width*.10,textAlign:'center',fontFamily:'Cormorant Garamond, serif',fontSize:props.height*.065,color:'#fff5df',textShadow:'0 0 14px #c89c58'}}><div>{caption.text}</div></AbsoluteFill>
    </Sequence>)}
  </AbsoluteFill>;
};
