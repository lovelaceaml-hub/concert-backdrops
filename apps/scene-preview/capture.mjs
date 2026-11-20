import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {platform} from 'node:os';
import {createServer} from 'vite';
import {chromium} from 'playwright';
import {browserPath} from '../browser-path.mjs';
import {compileMusicEvents,createCameraTrack} from '../shared/motion.mjs';
import {CAMERA_PRESET_NAMES} from '../shared/shot-templates.mjs';

const appRoot=path.dirname(fileURLToPath(import.meta.url));
export async function captureJob(jobPath,{allowLocalRender=false}={}) {
  if(platform()==='darwin'&&!allowLocalRender)throw new Error('Local Mac rendering is disabled. Use --allow-local-render for an intentional local run.');
  const job=JSON.parse(await readFile(jobPath,'utf8'));
  if(job.shot?.renderer!=='threejs')throw new Error('Capture requires a threejs shot');
  const knownScenes=new Set(['apps/scene-preview/src/scenes/Heavenly.tsx','light-ribbons','pavilion']);
  if(!knownScenes.has(job.shot.scene))throw new Error(`No browser scene registered for ${job.shot.scene}`);
  if(!Number.isInteger(job.shot.start_frame)||!Number.isInteger(job.shot.end_frame_exclusive)||job.shot.start_frame<0||job.shot.end_frame_exclusive<=job.shot.start_frame)throw new Error('Invalid shot frame bounds');
  if(job.shot.params?.camera&&!CAMERA_PRESET_NAMES.includes(job.shot.params.camera))throw new Error('Unknown camera path');
  const {width,height,fps}=job.video??{};
  if(![width,height,fps].every(Number.isInteger)||width<16||height<16||width>7680||height>4320||fps<1||fps>120)throw new Error('Invalid video dimensions or fps');
  if(job.shot.params?.camera_path)createCameraTrack(job.shot.params.camera_path,(job.shot.end_frame_exclusive-job.shot.start_frame)/fps);
  for(const [name,max] of [['motion_amount',2],['music_amount',1]]) {
    const value=job.shot.params?.[name];
    if(value!==undefined&&(!Number.isFinite(value)||value<0||value>max))throw new Error(`${name} must be between 0 and ${max}`);
  }
  if(job.timing?.fps!==undefined&&job.timing.fps!==fps)throw new Error('Timing fps must match video fps');
  compileMusicEvents(job.timing?.events??[],fps);
  if(!Number.isInteger(job.seed)||!Array.isArray(job.frames)||!job.frames.length)throw new Error('Seed and frame list are required');
  if(!job.frames.every(f=>Number.isInteger(f)&&f>=job.shot.start_frame&&f<job.shot.end_frame_exclusive))throw new Error('Frame outside shot bounds');
  if(!path.isAbsolute(job.out_dir))throw new Error('out_dir must be absolute');
  await mkdir(job.out_dir,{recursive:true});
  const server=await createServer({root:appRoot,configFile:false,server:{host:'127.0.0.1',port:0,strictPort:false},logLevel:'error'});
  let browser;
  try {
    await server.listen();
    const address=server.httpServer.address();
    const executablePath=browserPath();
    browser=await chromium.launch({executablePath,headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--force-color-profile=srgb','--disable-dev-shm-usage','--no-sandbox']});
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'});
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.addInitScript(value=>{window.__RENDER_JOB__=value;},job);
    await page.goto(`http://127.0.0.1:${address.port}/?capture=1`,{waitUntil:'networkidle'});
    await page.waitForFunction(()=>window.__SCENE_READY__&&typeof window.renderFrame==='function',null,{timeout:60000});
    const captures=[];
    let renderer;
    for(const frame of job.frames) {
      renderer=await page.evaluate(f=>window.renderFrame(f),frame);
      if(!renderer.software)throw new Error(`Software WebGL could not be confirmed: ${renderer.renderer}`);
      if(errors.length)throw new Error(errors.join('\n'));
      const filename=`frame_${String(frame).padStart(6,'0')}.png`;
      const buffer=await page.screenshot({type:'png',animations:'disabled'});
      const temp=path.join(job.out_dir,`${filename}.partial`);
      await writeFile(temp,buffer);
      await rename(temp,path.join(job.out_dir,filename));
      captures.push({frame,file:filename,sha256:createHash('sha256').update(buffer).digest('hex')});
    }
    const report={renderer:'threejs',browser:browser.version(),device:renderer,video:job.video,seed:job.seed,frames:captures};
    await writeFile(path.join(job.out_dir,'renderer.json'),JSON.stringify(report,null,2)+'\n');
    return report;
  } finally {
    if(browser)await browser.close();
    await server.close();
  }
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const index=process.argv.indexOf('--job');
  if(index<0||!process.argv[index+1]){console.error('Usage: node apps/scene-preview/capture.mjs --job /absolute/job.json');process.exitCode=2;}
  else {try {const report=await captureJob(path.resolve(process.argv[index+1]),{allowLocalRender:process.argv.includes('--allow-local-render')});console.log(JSON.stringify({frames:report.frames.length,device:report.device}));}catch(error){console.error(error.stack??error);process.exitCode=1;}}
}
