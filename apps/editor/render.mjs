import {readFile,writeFile,mkdtemp,copyFile,mkdir,rename,rm} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {tmpdir,platform} from 'node:os';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia} from '@remotion/renderer';
import {browserPath} from '../browser-path.mjs';
import {deliveryFfmpegArgs} from './delivery.mjs';

const appRoot=path.dirname(fileURLToPath(import.meta.url));
const option=name=>{const index=process.argv.indexOf(name);return index>=0?process.argv[index+1]:undefined;};
function requireInt(value,name,min=0) {if(!Number.isInteger(value)||value<min)throw new Error(`${name} must be an integer >= ${min}`);}
function validate(props) {
  for(const name of ['width','height','fps','durationInFrames'])requireInt(props[name],name,1);
  if(props.width%2||props.height%2)throw new Error('H.264 width and height must be even');
  if(!Array.isArray(props.clips))throw new Error('clips must be an array');
  if(typeof props.title!=='string')throw new Error('title must be a string');
  let end=0;
  for(const clip of props.clips) {
    requireInt(clip.start_frame,'clip start_frame');requireInt(clip.end_frame_exclusive,'clip end_frame_exclusive',1);
    if(clip.start_frame!==end||clip.end_frame_exclusive<=clip.start_frame)throw new Error('Clips must be contiguous and ordered');
    if(typeof clip.src!=='string'||!clip.src)throw new Error('Clip source is required');
    end=clip.end_frame_exclusive;
  }
  if(props.clips.length&&end!==props.durationInFrames)throw new Error('Clips must fill durationInFrames exactly');
  for(const caption of props.captions??[]) {
    requireInt(caption.start_frame,'caption start_frame');requireInt(caption.end_frame_exclusive,'caption end_frame_exclusive',1);
    if(typeof caption.text!=='string'||caption.end_frame_exclusive<=caption.start_frame||caption.end_frame_exclusive>props.durationInFrames)throw new Error('Invalid caption');
  }
}
function verifyClip(filename,clip,props) {
  const result=spawnSync('ffprobe',['-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames','-of','json',filename],{encoding:'utf8'});
  if(result.status!==0)throw new Error(`Cannot inspect clip ${filename}: ${result.stderr}`);
  const stream=JSON.parse(result.stdout).streams?.[0];
  const [n,d]=String(stream?.avg_frame_rate).split('/').map(Number);
  if(!stream||stream.width!==props.width||stream.height!==props.height||Math.abs(n/d-props.fps)>1e-6||Number(stream.nb_read_frames)!==clip.end_frame_exclusive-clip.start_frame)throw new Error(`Clip dimensions, frame rate, or length do not match the timeline: ${filename}`);
}

export async function finish(inputPath,outputPath,{allowLocalRender=false}={}) {
  if(platform()==='darwin'&&!allowLocalRender)throw new Error('Local Mac rendering is disabled. Use --allow-local-render for an intentional local run.');
  const props=JSON.parse(await readFile(inputPath,'utf8'));
  validate(props);
  const scratch=await mkdtemp(path.join(tmpdir(),'concert-finish-'));
  const publicDir=path.join(scratch,'public');
  await mkdir(publicDir);
  let serveUrl;
  try {
    const mapFile=async (src,prefix)=>{
      if(/^[a-z]+:\/\//i.test(src))throw new Error('Download authorized media locally before finishing; remote media is not fetched automatically.');
      const source=path.isAbsolute(src)?src:path.resolve(path.dirname(inputPath),src);
      if(!existsSync(source))throw new Error(`Missing media: ${source}`);
      const dest=`${prefix}${path.extname(source).toLowerCase()}`;
      await copyFile(source,path.join(publicDir,dest));
      return {source,dest};
    };
    const clips=[];
    for(let i=0;i<props.clips.length;i++) {
      const clip=props.clips[i];
      const file=await mapFile(clip.src,`clip-${String(i).padStart(4,'0')}`);
      verifyClip(file.source,clip,props);
      clips.push({...clip,src:file.dest});
    }
    const inputProps={...props,clips};
    if(props.audio_src)inputProps.audio_src=(await mapFile(props.audio_src,'soundtrack')).dest;
    serveUrl=await bundle({entryPoint:path.join(appRoot,'src/index.ts'),publicDir,outDir:path.join(scratch,'bundle')});
    const browserExecutable=browserPath();
    const chromiumOptions={gl:'swiftshader',disableWebSecurity:false};
    const composition=await selectComposition({serveUrl,id:'ConcertFilm',inputProps,browserExecutable,chromiumOptions});
    await mkdir(path.dirname(outputPath),{recursive:true});
    const partial=`${outputPath}.partial.mp4`;
    await renderMedia({serveUrl,composition,inputProps,outputLocation:partial,codec:'h264',crf:18,pixelFormat:'yuv420p',colorSpace:'bt709',imageFormat:'png',hardwareAcceleration:'disable',...(props.audio_src?{audioCodec:'aac',sampleRate:48000,audioBitrate:'320k'}:{muted:true}),ffmpegOverride:deliveryFfmpegArgs,concurrency:1,browserExecutable,chromiumOptions,overwrite:true,logLevel:'warn'});
    await rename(partial,outputPath);
    await writeFile(`${outputPath}.json`,JSON.stringify({renderer:'remotion',version:'4.0.484',width:props.width,height:props.height,fps:props.fps,durationInFrames:props.durationInFrames,clips:props.clips.length,audio:Boolean(props.audio_src),color_space:'rec709',pixel_format:'yuv420p',profile:'High',audio_sample_rate:props.audio_src?48000:null,output:outputPath},null,2)+'\n');
    return outputPath;
  } finally {await rm(scratch,{recursive:true,force:true});}
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(!option('--input')||!option('--output')){console.error('Usage: node apps/editor/render.mjs --input /absolute/props.json --output /absolute/master.mp4');process.exitCode=2;}
  else {try {console.log(await finish(path.resolve(option('--input')),path.resolve(option('--output')),{allowLocalRender:process.argv.includes('--allow-local-render')}));}catch(error){console.error(error.stack??error);process.exitCode=1;}}
}
