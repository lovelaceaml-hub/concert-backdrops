#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {existsSync,readFileSync,unlinkSync,writeFileSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const upstream=join(root,'.tools','video-shotcraft');
const workbench=join(upstream,'workbench');
const versions=JSON.parse(readFileSync(join(root,'integrations','versions.json'),'utf8'));
const pidFile=join(workbench,'.dev.pid');
const stateFile=join(root,'.tools','workbench-launch.json');
const viteBin=join(workbench,'node_modules','vite','bin','vite.js');
const args=process.argv.slice(2);

function fail(message){throw new Error(message);}
function usage(){
  console.log(`Usage: node scripts/launch-workbench.mjs [--project apps/editor] [--port 5198]
       node scripts/launch-workbench.mjs --check
       node scripts/launch-workbench.mjs --stop [--port 5198]

Starts the pinned Video Shotcraft Workbench in the cloud workspace on localhost.
No browser is opened. Use the printed URL through your workspace's port forwarding.
--check validates versions and the project manifest without starting a service.
--stop stops only this Workbench's verified Vite process.
Default startup stays in the foreground. Ctrl-C stops its managed server.
--background detaches only when your terminal supports persistent child processes.
--no-import opens the library without importing the linked project.`);
}
function options(){
  const result={project:join(root,'apps','editor'),port:5198,explicitPort:false,check:false,stop:false,noImport:false,background:false};
  for(let i=0;i<args.length;i++){
    const value=args[i];
    if(value==='--help'||value==='-h'){usage();process.exit(0);}
    if(value==='--check'){result.check=true;continue;}
    if(value==='--stop'){result.stop=true;continue;}
    if(value==='--background'){result.background=true;continue;}
    if(value==='--no-import'){result.noImport=true;continue;}
    if(value==='--port'){
      result.port=Number(args[++i]);result.explicitPort=true;
      if(!Number.isInteger(result.port)||result.port<1024||result.port>65535)fail('--port must be an integer from 1024 to 65535.');
      continue;
    }
    if(value==='--project'){
      if(!args[i+1]||args[i+1].startsWith('--'))fail('--project requires a directory.');
      result.project=resolve(process.cwd(),args[++i]);continue;
    }
    fail(`Unknown argument: ${value}`);
  }
  if(result.check&&result.stop)fail('Use either --check or --stop.');
  return result;
}
function readJson(path){return JSON.parse(readFileSync(path,'utf8'));}
function capture(command,argv,cwd=root){
  const result=spawnSync(command,argv,{cwd,encoding:'utf8'});
  if(result.error||result.status!==0)fail(`${command} failed: ${result.error?.message??result.stderr?.trim()}`);
  return result.stdout.trim();
}
function check(project){
  if(!existsSync(join(upstream,'SKILL.md'))||!existsSync(viteBin))fail('Run python3 scripts/install-integrations.py before starting Workbench.');
  const commit=capture('git',['rev-parse','HEAD'],upstream);
  if(commit!==versions.video_shotcraft.commit)fail(`Unexpected Shotcraft revision: ${commit}`);
  const manifest=join(project,'src','workbench.ts');
  if(!existsSync(manifest))fail(`This project needs a src/workbench.ts manifest: ${project}`);
  const packageJson=readJson(join(project,'package.json'));
  const installed=readJson(join(workbench,'node_modules','remotion','package.json')).version;
  if(installed!==versions.video_shotcraft.remotion_version)fail(`Workbench Remotion ${installed} differs from the pinned version.`);
  const remotion=packageJson.dependencies?.remotion;
  if(remotion!==installed)fail(`Project Remotion ${remotion} must match Workbench ${installed}.`);
  return {shotcraft_commit:commit,remotion_version:installed,project_manifest:manifest,host:'localhost',server_started:false};
}
function managedProcess(port){
  if(!existsSync(pidFile))return null;
  const pid=Number(readFileSync(pidFile,'utf8').trim());
  if(!Number.isInteger(pid)||pid<2)fail('Workbench PID file is invalid; no process was stopped.');
  try{process.kill(pid,0);}catch(error){
    if(error.code==='ESRCH'){unlinkSync(pidFile);return null;}
    throw error;
  }
  const command=capture('ps',['-o','command=','-p',String(pid)]);
  if(!command.includes(viteBin)||!command.includes(`--port ${port}`))fail('PID belongs to a different process; no process was stopped.');
  return pid;
}
async function stop(settings){
  const saved=existsSync(stateFile)?readJson(stateFile):null;
  const port=settings.explicitPort?settings.port:(saved?.port??settings.port);
  const pid=managedProcess(port);
  if(pid===null){
    if(existsSync(stateFile))unlinkSync(stateFile);
    console.log('No managed Workbench server is running.');return;
  }
  process.kill(pid,'SIGTERM');
  for(let i=0;i<40;i++){
    const result=spawnSync('ps',['-o','stat=','-p',String(pid)],{encoding:'utf8'});
    if(result.status!==0||result.stdout.trim().startsWith('Z')){
      if(existsSync(pidFile)&&Number(readFileSync(pidFile,'utf8').trim())===pid)unlinkSync(pidFile);
      if(existsSync(stateFile))unlinkSync(stateFile);
      console.log(`Stopped Workbench on localhost:${port}.`);return;
    }
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  fail('Workbench did not stop within four seconds. Its PID file is preserved.');
}
async function main(){
  const settings=options();
  if(settings.stop){await stop(settings);return;}
  const result=check(settings.project);
  if(settings.check){console.log(JSON.stringify(result,null,2));return;}
  if(process.platform==='darwin')fail('This workflow runs in the cloud. Start Workbench in the Linux workspace, not on the Mac.');
  const script=join(workbench,'scripts','open.mjs');
  const command=[script,settings.project,'--port',String(settings.port),'--no-open'];
  if(settings.noImport)command.push('--no-import');
  const opened=spawnSync(process.execPath,command,{cwd:workbench,stdio:'inherit',env:{...process.env,LIBGL_ALWAYS_SOFTWARE:'1'}});
  if(opened.error||opened.status!==0)fail(`Workbench startup failed. See ${join(workbench,'.dev.log')}`);
  const pid=managedProcess(settings.port);
  if(pid===null)fail('Workbench did not record a live managed server.');
  writeFileSync(stateFile,JSON.stringify({pid,port:settings.port,project:settings.project,commit:result.shotcraft_commit},null,2)+'\n');
  console.log(`Workbench ready: http://localhost:${settings.port}/${settings.noImport?'':'?import=project'}`);
  console.log('Stop with: node scripts/launch-workbench.mjs --stop');
  if(!settings.background){
    console.log('Foreground session active. Press Ctrl-C to stop.');
    await new Promise((done,reject)=>{
      let stopping=false;
      const monitor=setInterval(()=>{
        try{process.kill(pid,0);}catch(error){
          clearInterval(monitor);
          reject(new Error(`Workbench process ended: ${error.message}`));
        }
      },2000);
      const cleanup=async()=>{
        if(stopping)return;
        stopping=true;
        clearInterval(monitor);
        try{await stop(settings);done();}catch(error){reject(error);}
      };
      process.once('SIGINT',cleanup);
      process.once('SIGTERM',cleanup);
    });
  }
}
main().catch(error=>{console.error(`Workbench: ${error.message}`);process.exitCode=1;});
