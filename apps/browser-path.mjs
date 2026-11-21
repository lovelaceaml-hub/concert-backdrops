import {existsSync,readFileSync} from 'node:fs';
import {homedir,platform} from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const require=createRequire(import.meta.url);
export function browserPath() {
  if(process.env.CHROMIUM_PATH) {
    if(!existsSync(process.env.CHROMIUM_PATH))throw new Error('CHROMIUM_PATH does not point to an existing executable');
    return process.env.CHROMIUM_PATH;
  }
  const playwrightDir=path.dirname(require.resolve('playwright-core/package.json'));
  const manifest=JSON.parse(readFileSync(path.join(playwrightDir,'browsers.json'),'utf8'));
  const shell=manifest.browsers.find(entry=>entry.name==='chromium-headless-shell');
  const defaultCache=platform()==='darwin'?path.join(homedir(),'Library/Caches/ms-playwright'):platform()==='win32'?path.join(process.env.LOCALAPPDATA??homedir(),'ms-playwright'):path.join(process.env.XDG_CACHE_HOME??path.join(homedir(),'.cache'),'ms-playwright');
  const configuredCache=process.env.PLAYWRIGHT_BROWSERS_PATH;
  const cache=configuredCache==='0'?path.join(playwrightDir,'.local-browsers'):configuredCache?path.resolve(configuredCache):defaultCache;
  const revisionDir=path.join(cache,`chromium_headless_shell-${shell.revision}`);
  const candidates=['chrome-headless-shell-linux64/chrome-headless-shell','chrome-linux/headless_shell','chrome-headless-shell-mac-arm64/chrome-headless-shell','chrome-headless-shell-mac-x64/chrome-headless-shell','chrome-mac/headless_shell','chrome-headless-shell-win64/chrome-headless-shell.exe','chrome-win/headless_shell.exe'];
  for(const rel of candidates){const executable=path.join(revisionDir,rel);if(existsSync(executable))return executable;}
  throw new Error('No pinned headless browser is installed. Run npx playwright install chromium --only-shell, or set CHROMIUM_PATH to an approved compatible browser.');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {console.log(browserPath());}catch(error){console.error(error.message);process.exitCode=1;}
}
