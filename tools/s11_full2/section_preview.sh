#!/bin/bash
# section_preview.sh TAG NAME T0 T1 : join the 5 s draft parts covering T0..T1 from work/s11_full2/TAG,
# trim to the section, add the recording's audio, write deliver/<NAME>.mp4
set -e
cd /home/user/concert-backdrops/work/s11_full2
TAG=$1; NAME=$2; T0=$3; T1=$4
A=$(python3 -c "print(int($T0//5))"); B=$(python3 -c "import math;print(min(54,int(math.ceil($T1/5))-1))")
rm -f $TAG/sec.txt
for c in $(seq $A $B); do f=$(printf "c%02d.mp4" $c); [ -f $TAG/$f ] || { echo "missing $TAG/$f"; exit 1; }; echo "file '$f'" >> $TAG/sec.txt; done
OFF=$(python3 -c "print($T0-$A*5)"); DUR=$(python3 -c "print($T1-$T0)")
ffmpeg -v error -y -ss $OFF -t $DUR -f concat -safe 0 -i $TAG/sec.txt -ss $T0 -t $DUR -i score.wav \
  -map 0:v -map 1:a -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest \
  -movflags +faststart "deliver/$NAME.mp4" 2>&1 | grep -v "^$" || true
ls -la "deliver/$NAME.mp4"
