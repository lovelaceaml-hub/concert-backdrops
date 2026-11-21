#!/bin/sh
# Full render in parallel parts (cloud only): tools/s07_full/render_parts.sh OUTDIR [PARTS] [JOBS]
out=$1; parts=${2:-8}; jobs=${3:-4}
total=7846
mkdir -p "$out"
i=0
while [ $i -lt $parts ]; do
  a=$((total * i / parts)); b=$((total * (i + 1) / parts))
  echo "$i $a $b"
  i=$((i + 1))
done | xargs -P "$jobs" -L 1 sh -c 'python tools/s07_full/render.py --range $1 $2 --crf 12 --out '"$out"'/part$0.mp4 > '"$out"'/part$0.log 2>&1'
