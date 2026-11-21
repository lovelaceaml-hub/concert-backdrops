import {useMemo} from 'react';
import * as THREE from 'three';
import {frameSeconds,sampleMusicEnvelope,secondaryMotion,smootherstep} from '../../../shared/motion.mjs';
import type {CompiledMusicEvent} from '../../../shared/motion.mjs';

function seeded(seed: number) {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let t = Math.imul(value ^ (value >>> 15), 1 | value);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const colors = ['#eaa66c', '#efd18b', '#9bbacb', '#c1afd6', '#e9b8be', '#c9d7bd'];

function Pillar({x, z}: {x: number; z: number}) {
  return <group position={[x, 0, z]}>
    <mesh position={[0, 2.1, 0]}><cylinderGeometry args={[0.16, 0.22, 3.5, 20]}/><meshStandardMaterial color="#fff2dc" roughness={0.28} metalness={0.12}/></mesh>
    {[0.32, 3.88].map(y => <mesh key={y} position={[0,y,0]}><cylinderGeometry args={[0.31,0.31,0.2,24]}/><meshStandardMaterial color="#e7c780" roughness={0.3} metalness={0.5}/></mesh>)}
    <mesh position={[0,4.08,0]}><sphereGeometry args={[0.14,12,8]}/><meshStandardMaterial color="#ffe4b3" emissive="#f9c577" emissiveIntensity={2.1}/></mesh>
  </group>;
}

function Pavilion() {
  return <group position={[0,0,-1.3]}>
    {[0,1,2].map(level => <mesh key={level} position={[0,0.04+level*0.10,0]}>
      <cylinderGeometry args={[3.85-level*0.3,3.85-level*0.3,0.12,64]}/>
      <meshStandardMaterial color={level===2 ? '#fcf1d9' : '#ddd3bb'} roughness={0.3} metalness={0.12}/>
    </mesh>)}
    {[-2.45,0,2.45].map(x => [-1.45,1.45].map(z => <Pillar key={`${x}-${z}`} x={x} z={z}/>))}
    {[-1.45,1.45].map(z => [-1.225,1.225].map(x => <mesh key={`${z}-${x}`} position={[x,3.18,z]}>
      <torusGeometry args={[1.225,0.115,10,40,Math.PI]}/>
      <meshStandardMaterial color="#e6c98c" roughness={0.3} metalness={0.45}/>
    </mesh>))}
    <mesh position={[0,4.55,0]} rotation={[0,0,Math.PI/2]}><torusGeometry args={[3.05,0.065,8,96]}/><meshStandardMaterial color="#ffcf80" emissive="#ffcc7f" emissiveIntensity={1.2}/></mesh>
  </group>;
}

function Ribbon({time,index,seed,motionAmount,accent}:{time:number;index:number;seed:number;motionAmount:number;accent:number}) {
  const curve=useMemo(() => {
    const points=Array.from({length:65}, (_,i)=>{
      const u=i/64;
      const follow=secondaryMotion(time-u*0.65,seed,`ribbon-${index}`,0.09*motionAmount);
      const theta=u*Math.PI*2.5+index*Math.PI/3+time*0.12*motionAmount+follow;
      const radius=4.1+Math.sin(u*Math.PI)*0.8+index*0.18;
      return new THREE.Vector3(Math.cos(theta)*radius,0.9+u*4.2+Math.sin(theta*1.8+time*0.2)*0.15*motionAmount+accent*Math.sin(u*Math.PI)*0.22,Math.sin(theta)*radius-1.5);
    });
    return new THREE.CatmullRomCurve3(points);
  },[time,index,seed,motionAmount,accent]);
  return <mesh><tubeGeometry args={[curve,96,0.018+index*0.002,5,false]}/><meshStandardMaterial color={colors[index]} emissive={colors[index]} emissiveIntensity={1.8} roughness={0.4} toneMapped={false}/></mesh>;
}

function Stars({time,seed,motionAmount}:{time:number;seed:number;motionAmount:number}) {
  const base=useMemo(()=>{
    const rand=seeded(seed);
    return Array.from({length:260},()=>({x:(rand()-0.5)*26,y:0.6+rand()*11,z:(rand()-0.5)*20,phase:rand()*Math.PI*2}));
  },[seed]);
  const positions=useMemo(()=>new Float32Array(base.flatMap((p,i)=>[p.x+secondaryMotion(time,seed,`star-x-${i}`,0.12*motionAmount),p.y+secondaryMotion(time,seed,`star-y-${i}`,0.1*motionAmount),p.z])),[base,time,seed,motionAmount]);
  return <points>
    <bufferGeometry><bufferAttribute attach="attributes-position" args={[positions,3]}/></bufferGeometry>
    <pointsMaterial color="#ffe1a1" size={0.035} sizeAttenuation transparent opacity={0.7} depthWrite={false}/>
  </points>;
}

export function Heavenly({frame,fps,seed,startFrame=0,endFrame,events,motionAmount=1,musicAmount=0.15}:{frame:number;fps:number;seed:number;startFrame?:number;endFrame:number;events:CompiledMusicEvent[];motionAmount?:number;musicAmount?:number}) {
  const duration=frameSeconds(endFrame,fps,startFrame);
  const time=duration*smootherstep(frameSeconds(frame,fps,startFrame)/duration);
  const accent=musicAmount*sampleMusicEnvelope(events,frame,{kinds:['accent','phrase','swell'],cap:1});
  return <>
    <color attach="background" args={['#e9d7bb']}/>
    <fog attach="fog" args={['#ead9bf',16,56]}/>
    <ambientLight intensity={1.25} color="#fff3dd"/>
    <hemisphereLight args={['#fff3de','#91aab7',1.2]}/>
    <directionalLight position={[-5,9,4]} intensity={3.0} color="#ffe3ae"/>
    <directionalLight position={[5,4,-3]} intensity={1.8} color="#b8d5eb"/>
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,-0.04,0]}>
      <planeGeometry args={[180,180]}/><meshStandardMaterial color="#a4bec0" roughness={0.23} metalness={0.45}/>
    </mesh>
    {[5.2,7.3,9.6,12.0,15.4,19.2].map((radius,index)=><mesh key={radius} rotation={[-Math.PI/2,0,0]} position={[0,0,-1.5]} scale={1+secondaryMotion(time,seed,`ring-${index}`,0.012*motionAmount)+accent*0.012}>
      <torusGeometry args={[radius,0.019,6,120]}/><meshBasicMaterial color="#f9d48f" transparent opacity={0.3}/>
    </mesh>)}
    <mesh position={[0,6.5,-17]}><sphereGeometry args={[1.2,24,16]}/><meshBasicMaterial color="#ffe7ad" toneMapped={false}/></mesh>
    <Pavilion/>
    {colors.map((_,i)=><Ribbon key={i} time={time} index={i} seed={seed} motionAmount={motionAmount} accent={accent}/>)}
    <Stars time={time} seed={seed} motionAmount={motionAmount}/>
  </>;
}
