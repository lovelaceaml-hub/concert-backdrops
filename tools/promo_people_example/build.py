"""Build a repeatable thirty-second people proposal without paid rendering."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.promo_people_example.render import source_hashes, runtime_identity, FPS, FRAMES
from tools.promo_people_example.people import PeopleScene
from pipeline.delivery import get_profile, stream_validation_errors
from pipeline.media import probe


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2)+"\n")
    temporary.replace(path)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers",type=int,choices=range(1,5),default=3)
    ap.add_argument("--width",type=int,default=1920)
    ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--samples",type=int,default=2)
    ap.add_argument("--directory",default="work/promo-people-example/final")
    args=ap.parse_args()
    if sys.platform=="darwin":ap.error("Cloud CPU rendering only.")
    if min(args.width,args.height)<32 or args.width%2 or args.height%2 or args.samples<1:ap.error("Invalid render settings")
    folder=Path(args.directory).resolve();folder.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    inputs=source_hashes();runtime=runtime_identity()
    print(json.dumps({"event":"preparing_people_cache"}),flush=True)
    people=PeopleScene();people.prepare_cache(duration=31.)
    del people
    print(json.dumps({"event":"render_started","frames":FRAMES,"fps":FPS,"size":[args.width,args.height],"workers":args.workers}),flush=True)
    def render_part(part):
        start,end=part*300,(part+1)*300
        movie=folder/f"part-{part}.mp4";receipt=movie.with_suffix(".json")
        if movie.is_file() and receipt.is_file():
            try:old=json.loads(receipt.read_text())
            except (ValueError,OSError):old={}
            if (old.get("source_sha256")==inputs and old.get("runtime")==runtime
                and old.get("sha256")==digest(movie)
                and old.get("width")==args.width and old.get("height")==args.height
                and old.get("temporal_samples")==args.samples
                and old.get("start")==start and old.get("end")==end):
                return {"part":part,"reused":True}
        cmd=[sys.executable,str(Path(__file__).with_name("render.py")),"--width",str(args.width),
            "--height",str(args.height),"--samples",str(args.samples),"--start",str(start),"--end",str(end),"--out",str(movie)]
        env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",LIBGL_ALWAYS_SOFTWARE="1",LP_NUM_THREADS="2")
        with movie.with_suffix(".log").open("w") as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        return {"part":part,"reused":False}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(render_part,i) for i in range(6)]):
            print(json.dumps(future.result()),flush=True)
    if source_hashes()!=inputs:raise RuntimeError("Source inputs changed during this render round")
    source=ROOT/"audio/promo/concert-medley.mp3";source_digest=digest(source)
    audio=folder/"score-30s.wav"
    audio_tmp=folder/"score-30s.assembling.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(source),"-af",
        "atrim=start=30:end=60,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.35",
        "-ar","48000","-ac","2","-c:a","pcm_s24le",str(audio_tmp)],check=True)
    audio_tmp.replace(audio)
    playlist=folder/"concat.txt";playlist.write_text("".join(f"file 'part-{i}.mp4'\n" for i in range(6)))
    quality="4K60" if (args.width,args.height)==(3840,2160) else f"{args.height}p60"
    output=folder/f"Mothers-Love-People-Animation-30s-{quality}.mp4"
    temporary=output.with_name(output.stem+".assembling.mp4")
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(playlist),"-i",str(audio),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","320k","-ar","48000","-t","30",
        "-movflags","+faststart",str(temporary)],check=True)
    metadata=probe(temporary)
    errors=stream_validation_errors(metadata,get_profile("h264"),width=args.width,height=args.height,fps=FPS,frames=FRAMES,wanted_audio=True)
    if digest(source)!=source_digest:raise RuntimeError("Source music changed")
    if errors:raise RuntimeError("; ".join(errors))
    report={"output":str(output),"sha256":digest(temporary),"bytes":temporary.stat().st_size,
        "frames":FRAMES,"fps":FPS,"duration_seconds":30.,"width":args.width,"height":args.height,
        "source_sha256":inputs,"runtime":runtime,"cuts_frames":[612,1168],
        "audio":{"source":"audio/promo/concert-medley.mp3","source_sha256":source_digest,"trim":[30,60],
            "entry_fade_seconds":.35,"source_unchanged":True,"wav_sha256":digest(audio)},
        "errors":errors,"technical_passed":True,"creative_approval":"not_recorded",
        "elapsed_seconds":time.monotonic()-started,"metadata":metadata}
    temporary.replace(output);atomic_json(folder/"delivery.json",report)
    print(json.dumps({k:report[k] for k in ["output","bytes","width","height","frames","fps","technical_passed","elapsed_seconds"]}),flush=True)


if __name__=="__main__":main()
