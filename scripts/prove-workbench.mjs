#!/usr/bin/env node
// Proves the Video Shotcraft Workbench in a real browser: the page opens without
// errors, pressing Play moves the preview, and its "Render to MP4" button produces
// a real video. Starts and stops its own Workbench server. Cloud CPU only.
//
//   node scripts/prove-workbench.mjs [--out work/proofs/workbench] [--keep-server]
//
// Writes <out>/workbench-proof.json, before/after preview stills and the exported MP4.
import {spawn, execFileSync} from 'node:child_process';
import {copyFileSync, existsSync, mkdirSync, writeFileSync} from 'node:fs';
import {platform} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {browserPath} from '../apps/browser-path.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = (k, d) => (args.includes(`--${k}`) ? args[args.indexOf(`--${k}`) + 1] : d);
const out = path.resolve(root, opt('out', 'work/proofs/workbench'));
const port = Number(process.env.WORKBENCH_PORT ?? 5198);
const base = `http://localhost:${port}`;
const workbench = path.join(root, '.tools/video-shotcraft/workbench');
mkdirSync(out, {recursive: true});

if (platform() === 'darwin' && !args.includes('--allow-local-render'))
  throw new Error('Workbench proofs run on cloud CPU. Pass --allow-local-render for an intentional Mac run.');

const result = {page_loaded: false, page_errors: [], playback_advanced: false, export: null, ok: false};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const up = async () => {
  try { return (await fetch(`${base}/`)).ok; } catch { return false; }
};

let server = null;
if (!(await up())) {
  server = spawn(process.execPath, ['scripts/launch-workbench.mjs'], {cwd: root, stdio: 'ignore'});
  for (let i = 0; i < 120 && !(await up()); i++) await sleep(1000);
  if (!(await up())) throw new Error('Workbench server did not answer within 120 seconds');
}

let browser;
try {
  browser = await chromium.launch({executablePath: browserPath(), headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage', '--no-sandbox']});
  const page = await browser.newPage({viewport: {width: 1600, height: 1000}});
  page.on('pageerror', (e) => result.page_errors.push(String(e.message).slice(0, 300)));
  await page.goto(`${base}/?import=project`, {waitUntil: 'networkidle', timeout: 120000});
  if (await page.locator('vite-error-overlay').count())
    throw new Error('Workbench shows a build error: ' + (await page.locator('vite-error-overlay').innerText()).slice(0, 400));
  const player = page.locator('.__remotion-player').first();
  await player.waitFor({timeout: 60000});
  result.page_loaded = true;

  // Playback: the frame counter must advance and the preview picture must change.
  const stage = page.locator('.preview-stage').first();
  const timecode = page.locator('.transport .timecode').first();
  await page.locator('button[title^="Go to start"]').click();
  await sleep(500);
  const startCode = (await timecode.innerText()).trim();
  const before = await stage.screenshot({path: path.join(out, 'preview-before.png')});
  await page.locator('button[title^="Play / Pause"]').click();
  await sleep(2500);
  const after = await stage.screenshot({path: path.join(out, 'preview-after.png')});
  const playingCode = (await timecode.innerText()).trim();
  await page.locator('button[title^="Play / Pause"]').click();
  result.playback = {timecode_before: startCode, timecode_after: playingCode, picture_changed: !before.equals(after)};
  result.playback_advanced = startCode !== playingCode && !before.equals(after);

  // Export: the Workbench's own Render button, followed through its export API.
  const posted = page.waitForResponse((r) => r.url().endsWith('/api/export') && r.request().method() === 'POST', {timeout: 60000});
  await page.locator('button[title^="Render the current project to MP4"]').click();
  const start = await (await posted).json();
  if (!start.id) throw new Error('Export did not start: ' + JSON.stringify(start).slice(0, 300));
  let job;
  for (let i = 0; i < 900; i++) {
    job = await (await fetch(`${base}/api/export/${start.id}`)).json();
    if (job.status !== 'running') break;
    await sleep(2000);
  }
  if (job?.status !== 'done') throw new Error('Export did not finish: ' + JSON.stringify(job).slice(0, 600));
  const source = path.join(workbench, job.output);
  const mp4 = path.join(out, 'workbench-export.mp4');
  copyFileSync(source, mp4);
  const [codec, width, height, frames] = execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0',
    '-show_entries', 'stream=codec_name,width,height,nb_read_frames', '-of', 'csv=p=0', mp4]).toString().trim().split(',');
  result.export = {file: path.relative(root, mp4), codec, width: +width, height: +height, frames: +frames};
  result.ok = result.page_errors.length === 0 && result.playback_advanced && +frames > 0;
} catch (error) {
  result.error = String(error.message ?? error).slice(0, 800);
} finally {
  if (browser) await browser.close().catch(() => {});
  if (server && !args.includes('--keep-server')) {
    execFileSync(process.execPath, ['scripts/launch-workbench.mjs', '--stop'], {cwd: root, stdio: 'ignore'});
    server.kill();
  }
}
writeFileSync(path.join(out, 'workbench-proof.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exitCode = 1;
