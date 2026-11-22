import path from 'node:path';
import {platform} from 'node:os';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {browserPath} from './browser-path.mjs';

// This probe never downloads a browser. It verifies the same software WebGL path
// used by capture, without building a scene or writing frames.
export async function probeBrowser({launch=false,allowLocalRender=false}={}) {
  const result={installed:false,runtime_validated:false,status:'not_installed',software:null,renderer:null,executable:null,error:null};
  let browser;
  try {
    result.executable=browserPath();
    result.installed=true;
    result.status='not_probed';
    if(!launch)return result;
    if(platform()==='darwin'&&!allowLocalRender)throw new Error('Local Mac rendering is disabled. Pass --allow-local-render for an intentional local browser probe.');
    browser=await chromium.launch({executablePath:result.executable,headless:true,timeout:20000,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage','--no-sandbox']});
    const page=await browser.newPage({viewport:{width:16,height:16}});
    const context=await page.evaluate(()=>{
      const gl=document.createElement('canvas').getContext('webgl2');
      if(!gl)throw new Error('WebGL2 is unavailable in this browser runtime');
      const extension=gl.getExtension('WEBGL_debug_renderer_info');
      const renderer=String(gl.getParameter(extension?extension.UNMASKED_RENDERER_WEBGL:gl.RENDERER));
      return {renderer,software:/swiftshader|llvmpipe|software/i.test(renderer),version:String(gl.getParameter(gl.VERSION))};
    });
    Object.assign(result,context,{runtime_validated:true,status:'validated',browser:browser.version()});
  } catch(error) {
    result.status=result.installed?'blocked':'not_installed';
    const lines=String(error.message??error).split('\n');
    result.error=[lines[0],...lines.filter(line=>/FATAL:|socket\(\) failed|WebGL2 is unavailable/.test(line)).slice(0,3)].join('\n').slice(0,1500);
  } finally {if(browser)await browser.close().catch(()=>{});}
  return result;
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const launch=process.argv.includes('--launch');
  const result=await probeBrowser({launch,allowLocalRender:process.argv.includes('--allow-local-render')});
  console.log(JSON.stringify(result));
  if(!result.installed||(launch&&!result.runtime_validated))process.exitCode=1;
}
