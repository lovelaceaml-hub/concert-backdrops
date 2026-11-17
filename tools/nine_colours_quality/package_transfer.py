"""Package the exact UHD master for a connector with a per-file upload limit."""
import hashlib
import json
from deliver import OUT, WORK

CHUNK_SIZE = 80_000_000
PACKAGE = WORK / 'exact-transfer'

HTML = '''<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Save your Nine Colours 4K60 video</title>
<style>
body{font:18px/1.6 system-ui,sans-serif;background:#f5f5fa;color:#202139;margin:0}
main{max-width:620px;margin:8vh auto;padding:32px;background:white;border-radius:18px}
h1{font-size:30px;line-height:1.2}button,input{font:inherit;max-width:100%}
button{padding:14px 20px;background:#263bb2;color:white;border:0;border-radius:9px;cursor:pointer}
button:disabled{background:#a0a4bc;cursor:default}label{display:block;font-weight:600}
input{margin:12px 0}small{color:#55586b}#status{min-height:3em}
@media(max-width:700px){main{margin:15px;padding:24px}}
</style>
<main><p>NINE COLOURS / ORIGINAL 4K60 MASTER</p>
<h1>Save your full-quality video</h1>
<p>Select the four files ending in <b>.part01</b> to <b>.part04</b> from the
downloaded folder. They will become one original MP4, with its quality unchanged.</p>
<label for="parts">1. Choose all four parts</label>
<input id="parts" type="file" multiple accept=".part01,.part02,.part03,.part04">
<p id="status" role="status" aria-live="polite">Ready for your four files.</p>
<button id="save" disabled>2. Save the 4K60 video</button>
<p><small>Use Chrome, Edge, or Safari on your computer. The video saves to your
browser's Downloads location. All checks run locally on your computer.</small></p>
</main>
<script>
const manifest = __MANIFEST__;
const picker = document.querySelector('#parts');
const save = document.querySelector('#save');
const status = document.querySelector('#status');
let downloadUrl = null;
picker.addEventListener('change', async () => {
  save.disabled = true;
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = null;
  picker.disabled = true;
  try {
    if (!crypto.subtle) throw new Error('Please open this downloaded HTML file in Chrome, Edge, or Safari on your computer.');
    const selected = Array.from(picker.files);
    const ordered = [];
    for (const [index, expected] of manifest.parts.entries()) {
      const matches = selected.filter(file => file.name === expected.name);
      if (matches.length !== 1) throw new Error('Select exactly one copy of ' + expected.name + ' together with the other three parts.');
      const file = matches[0];
      if (file.size !== expected.size) throw new Error(expected.name + ' is incomplete. Download that part again.');
      status.textContent = 'Checking part ' + (index + 1) + ' of ' + manifest.parts.length + '...';
      const bytes = await file.arrayBuffer();
      const digest = await crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
      if (hex !== expected.sha256) throw new Error(expected.name + ' did not match the original. Download that part again.');
      ordered.push(file);
    }
    const video = new Blob(ordered, {type:'video/mp4'});
    if (video.size !== manifest.size) throw new Error('The assembled file has the wrong size.');
    downloadUrl = URL.createObjectURL(video);
    save.disabled = false;
    status.textContent = 'All four parts verified. Your original 319 MB video is ready to save.';
  } catch (error) {
    status.textContent = error.message;
  } finally {
    picker.disabled = false;
  }
});
save.addEventListener('click', () => {
  if (!downloadUrl) return;
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = manifest.file;
  document.body.append(link);
  link.click();
  link.remove();
});
</script></html>
'''


def run():
    qa = json.loads((WORK / 'final-qa.json').read_text())
    source = OUT / qa['file']
    PACKAGE.mkdir(parents=True, exist_ok=True)
    parts = []
    whole = hashlib.sha256()
    with source.open('rb') as stream:
        while data := stream.read(CHUNK_SIZE):
            name = f'Nine-Colours-4K60.part{len(parts)+1:02d}'
            (PACKAGE / name).write_bytes(data)
            whole.update(data)
            parts.append(dict(name=name, size=len(data),
                              sha256=hashlib.sha256(data).hexdigest()))
    if whole.hexdigest() != qa['sha256'] or source.stat().st_size != qa['size_bytes']:
        raise RuntimeError('The master does not match its completed QA record')
    if len(parts) != 4:
        raise RuntimeError('This delivery helper expects four parts')
    manifest = dict(file=source.name, size=source.stat().st_size,
                    sha256=whole.hexdigest(), parts=parts)
    (PACKAGE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (PACKAGE / 'Open-to-save-video.html').write_text(
        HTML.replace('__MANIFEST__', json.dumps(manifest)))
    (PACKAGE / 'START-HERE.txt').write_text(
        'ONE ORIGINAL 4K60 VIDEO, TRANSFERRED WITHOUT RE-ENCODING\n\n'
        'Use a computer for these steps.\n'
        '1. Download this entire folder from Google Drive. Unzip the download.\n'
        '2. Open Open-to-save-video.html in Chrome, Edge, or Safari.\n'
        '3. Choose all four Nine-Colours-4K60.part files together.\n'
        '4. After the checks finish, click Save the 4K60 video.\n\n'
        'Your browser saves one original MP4 to Downloads (or asks where to save it).\n'
        'The four parts are pieces of one file, not alternative video versions.\n'
        'No app installation, account connection or video conversion is needed.\n\n'
        f'Original file: {source.name}\n'
        f'Original size: {manifest["size"]} bytes\n'
        f'SHA-256: {manifest["sha256"]}\n')
    print(PACKAGE)


if __name__ == '__main__':
    run()
