import {createElement} from 'react';
import {DemoCard,FinishingComposition} from './Composition';
import {DEMO,DEMO_SHOTS} from './timeline';

export const WORKBENCH={
  name:'Concert finishing study',fps:DEMO.fps,width:DEMO.width,height:DEMO.height,total:DEMO.durationInFrames,background:'#e9d7bb',
  shots:DEMO_SHOTS.map(shot=>({id:shot.id,label:shot.label,from:shot.from,duration:shot.duration,component:DemoCard,props:{title:shot.title,subtitle:shot.subtitle,durationInFrames:shot.duration},schema:[{type:'text',key:'title',label:'Title',default:shot.title},{type:'text',key:'subtitle',label:'Subtitle',default:shot.subtitle}]})),
  transitions:[],captions:[],overlays:[],sfx:[],bgm:[],
  original:()=>createElement(FinishingComposition,DEMO),
};
