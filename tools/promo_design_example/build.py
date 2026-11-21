"""Render and assemble the isolated ten-second design proposal on cloud CPUs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.promo_design_example.render import source_hashes
from pipeline.delivery import get_profile, stream_validation_errors
from pipeline.media import probe


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--workers",type=int,choices=range(1,5),default=2)
    ap.add_argument("--width",type=int,default=1920)
    ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--samples",type=int,default=2)
    ap.add_argument("--directory",default="work/promo-design-example/final")
    args=ap.parse_args()
    if sys.platform=="darwin":ap.error("Cloud CPU rendering only.")
    folder=Path(args.directory).resolve();folder.mkdir(parents=True,exist_ok=True)
    inputs=source_hashes()
    started=time.monotonic()
    def render_part(part):
        start,end=part*150,(part+1)*150
        movie=folder/f"part-{part}.mp4";receipt=movie.with_suffix(".json")
        if movie.is_file() and receipt.is_file():
            old=json.loads(receipt.read_text())
            if (old.get("source_sha256")==inputs and old.get("sha256")==digest(movie)
                and old.get("width")==args.width and old.get("height")==args.height
                and old.get("temporal_samples")==args.samples and old.get("start")==start and old.get("end")==end):
                return {"part":part,"reused":True}
        command=[sys.executable,str(Path(__file__).with_name("render.py")),"--width",str(args.width),
                 "--height",str(args.height),"--samples",str(args.samples),"--start",str(start),"--end",str(end),"--out",str(movie)]
        with movie.with_suffix(".log").open("w") as log:
            subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        return {"part":part,"reused":False}
    print(json.dumps({"event":"render_started","frames":600,"fps":60,"size":[args.width,args.height],"workers":args.workers}),flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(render_part,i) for i in range(4)]
        for f in as_completed(futures):print(json.dumps(f.result()),flush=True)
    if source_hashes()!=inputs:raise RuntimeError("Source inputs changed during this render round.")
    source=ROOT/"audio/promo/concert-medley.mp3"
    source_digest=digest(source)
    audio=folder/"score-10s.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(source),"-af",
        "atrim=start=50:end=60,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.08",
        "-ar","48000","-ac","2","-c:a","pcm_s24le",str(audio)],check=True)
    playlist=folder/"concat.txt"
    playlist.write_text("".join(f"file 'part-{i}.mp4'\n" for i in range(4)))
    output=folder/"Mothers-Love-Promo-Design-Example-1080p60.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(playlist),"-i",str(audio),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","320k","-ar","48000","-t","10",
        "-movflags","+faststart",str(output)],check=True)
    metadata=probe(output)
    errors=stream_validation_errors(metadata,get_profile("h264"),width=args.width,height=args.height,fps=60,frames=600,wanted_audio=True)
    if digest(source)!=source_digest:raise RuntimeError("Original music changed.")
    report={"output":str(output),"sha256":digest(output),"bytes":output.stat().st_size,"frames":600,"fps":60,
        "width":args.width,"height":args.height,"duration_seconds":10,"source_sha256":inputs,
        "audio":{"source":"audio/promo/concert-medley.mp3","source_sha256":source_digest,"trim":[50,60],
                 "entry_fade_seconds":.08,"source_unchanged":True,"wav_sha256":digest(audio)},
        "errors":errors,"technical_passed":not errors,"creative_approval":"not_recorded",
        "elapsed_seconds":time.monotonic()-started,"metadata":metadata}
    (folder/"delivery.json").write_text(json.dumps(report,indent=2)+"\n")
    if errors:raise RuntimeError("; ".join(errors))
    print(json.dumps({k:report[k] for k in ("output","bytes","frames","fps","width","height","technical_passed","elapsed_seconds")}),flush=True)


if __name__=="__main__":main()
