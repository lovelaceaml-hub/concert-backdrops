#!/bin/bash
# place.sh MACHINE cNN=id ... : copy downloaded parts into h7, check them, note the machine's last report
D=/tmp/claude-0/-home-user-concert-backdrops/284ecd5f-63c5-587c-9ba6-baa226fb663e/scratchpad/artifact-files/0383b4ba-d953-4c4b-bd67-8541038a046c
H=/home/user/concert-backdrops/work/s11_full2/${TAG:-h8}
M=$1; shift
for kv in "$@"; do c=${kv%%=*}; id=${kv#*=}; cp $D/$id.mp4 $H/$c.mp4; e=$(ffmpeg -v error -i $H/$c.mp4 -f null - 2>&1 | wc -l); echo "$c errors=$e"; done
python3 - "$M" <<PY
import json,sys,datetime
p="$(dirname $0)/machines.json"; m=json.load(open(p))
for r in m.get("roster",[]):
    if r["name"].startswith("Machine "+sys.argv[1]): r["last"]=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
json.dump(m,open(p,"w"),indent=1)
PY
