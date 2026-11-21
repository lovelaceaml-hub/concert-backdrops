#!/bin/sh
# Landmark stills in parallel (cloud only). Usage: tools/s07_full/stills.sh OUTDIR SCALE "t1,t2" "t3,t4" ...
out=$1; scale=$2; shift 2
for group in "$@"; do
  python tools/s07_full/render.py --stills "$group" --scale "$scale" --outdir "$out" > "$out.$(echo $group | cut -d, -f1).log" 2>&1 &
done
wait
