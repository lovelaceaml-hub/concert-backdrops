"""Materialize private production assets locally, with exact source checks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]


def verify(data,expected,name):
    actual=hashlib.sha256(data).hexdigest()
    if actual!=expected:raise ValueError(f'{name}: source hash mismatch: {actual}')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--recording',type=Path,required=True)
    p.add_argument('--environment-archive',type=Path,required=True)
    a=p.parse_args()
    manifest=json.loads(Path(__file__).with_name('assets.json').read_text())
    recording=a.recording.read_bytes()
    verify(recording,manifest['recording']['sha256'],a.recording.name)
    out=ROOT/'work/sol3';(out/'environments').mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.environment_archive) as z:
        for asset in manifest['environments']:
            data=z.read(asset['name']);verify(data,asset['sha256'],asset['name'])
            (out/'environments'/asset['name']).write_bytes(data)
    target=out/'source11-full.mp3'
    if a.recording.resolve()!=target.resolve():shutil.copyfile(a.recording,target)
    print('Verified the original recording and four exact environment paintings.')

if __name__=='__main__':main()
