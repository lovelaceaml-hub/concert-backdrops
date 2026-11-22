"""Run the registered production pipeline with bounded, resumable film jobs."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time

from tools.cinematic_ten.render import ROOT


def run_one(film_id, quality):
    log = ROOT / f"work/cinematic-ten/logs/film{film_id:02d}-{quality}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "pipeline.cli", "--root", str(ROOT),
               "produce", f"cinematic-ten-{film_id:02d}", "--quality", quality]
    began = time.monotonic()
    with log.open("a") as stream:
        stream.write("COMMAND " + json.dumps(command) + "\n")
        stream.flush()
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    record = dict(film=film_id, quality=quality, exit_code=result.returncode,
                  elapsed_seconds=round(time.monotonic()-began, 2), log=str(log))
    print(json.dumps(record), flush=True)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--films", default="1,2,3,4,5,6,7,8,9,10")
    p.add_argument("--projects", type=int, default=2, choices=(1, 2))
    p.add_argument("--quality", default="final", choices=("draft", "review", "final"))
    a = p.parse_args()
    ids = [int(x) for x in a.films.split(",")]
    if not ids or any(i < 1 or i > 10 for i in ids) or len(set(ids)) != len(ids):
        p.error("Choose distinct film numbers1..10")
    with ThreadPoolExecutor(max_workers=a.projects) as pool:
        futures = [pool.submit(run_one, i, a.quality) for i in ids]
        records = [f.result() for f in as_completed(futures)]
    path = ROOT / "work/cinematic-ten/run-receipt.json"
    path.write_text(json.dumps(records, indent=2) + "\n")
    if any(r["exit_code"] for r in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
