#!/bin/bash
# section_preview.sh TAG NAME T0 T1 : join the 5 s draft parts covering T0..T1 from work/s11_full2/TAG,
# cut exactly T0..T1 (frame-accurate trim filters, timestamps reset so picture and sound both start at 0),
# add the recording's audio for the same span, write deliver/<NAME>.mp4
set -e
cd /home/user/concert-backdrops/work/s11_full2
TAG=$1; NAME=$2; T0=$3; T1=$4
A=$(python3 -c "print(int($T0//5))"); B=$(python3 -c "import math;print(min(54,int(math.ceil($T1/5))-1))")
L=$(mktemp -p "$PWD/$TAG" sec_XXXXXX.txt)   # a private list per run: parallel builds must never share one
trap 'rm -f "$L"' EXIT
for c in $(seq $A $B); do f=$(printf "c%02d.mp4" $c); [ -f $TAG/$f ] || { echo "missing $TAG/$f"; exit 1; }; echo "file '$PWD/$TAG/$f'" >> "$L"; done
OFF=$(python3 -c "print($T0-$A*5)"); DUR=$(python3 -c "print($T1-$T0)")
ffmpeg -v error -y -f concat -safe 0 -i "$L" -i score.wav \
  -filter_complex "[0:v]setpts=PTS-STARTPTS,trim=start=$OFF:duration=$DUR,setpts=PTS-STARTPTS[v];[1:a]atrim=start=$T0:duration=$DUR,asetpts=PTS-STARTPTS[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k \
  -movflags +faststart "deliver/$NAME.mp4"
ls -la "deliver/$NAME.mp4"
