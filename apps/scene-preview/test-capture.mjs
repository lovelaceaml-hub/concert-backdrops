import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJob} from './capture.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'work/pipeline/browser-test');
await mkdir(out,{recursive:true});
const job={project_id:'browser-test',shot:{id:'light',name:'Frame determinism check',renderer:'threejs',start_frame:0,end_frame_exclusive:60,scene:'apps/scene-preview/src/scenes/Heavenly.tsx'},video:{width:320,height:180,fps:30},seed:2026,frames:[0,30,0,15],out_dir:out};
const jobPath=path.join(out,'job.json');
await writeFile(jobPath,JSON.stringify(job));
const report=await captureJob(jobPath);
assert.equal(report.frames[0].sha256,report.frames[2].sha256,'Repeated frame changed after rendering another time');
assert.notEqual(report.frames[0].sha256,report.frames[1].sha256,'Animation did not move');
assert.equal(report.device.software,true,'CPU test unexpectedly used hardware');
console.log('PASS: out-of-order frame identity, real animation, CPU WebGL capture');
