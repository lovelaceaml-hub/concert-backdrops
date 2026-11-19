#!/bin/bash
# section_build.sh TAG NAME T0 T1 CLIP : on a render machine, join the 5 s parts covering T0..T1 from
# work/s11_full2/TAG, cut exactly T0..T1 (frame-accurate trim, timestamps reset to 0) and add the section's
# own audio clip CLIP (which already starts at T0). Writes work/s11_full2/deliver/NAME.mp4, small enough for the
# review page (crf 25). The audio clip never goes into git.
set -e
TAG=$1; NAME=$2; T0=$3; T1=$4; CLIP=$(realpath "$5")   # resolve before changing folder, so a relative path works
cd "$(git rev-parse --show-toplevel)/work/s11_full2"
A=$(python3 -c "print(int($T0//5))"); B=$(python3 -c "import math;print(min(54,int(math.ceil($T1/5))-1))")
mkdir -p deliver; L=$(mktemp -p "$PWD/$TAG" sec_XXXXXX.txt)   # a private list per run: parallel builds must never share one
trap 'rm -f "$L"' EXIT
for c in $(seq $A $B); do f=$(printf "c%02d.mp4" $c); [ -f $TAG/$f ] || { echo "missing $TAG/$f"; exit 1; }; echo "file '$PWD/$TAG/$f'" >> "$L"; done
OFF=$(python3 -c "print($T0-$A*5)"); DUR=$(python3 -c "print($T1-$T0)")
ffmpeg -v error -y -f concat -safe 0 -i "$L" -i "$CLIP" \
  -filter_complex "[0:v]setpts=PTS-STARTPTS,trim=start=$OFF:duration=$DUR,setpts=PTS-STARTPTS[v];[1:a]apad,atrim=start=0:duration=$DUR,asetpts=PTS-STARTPTS[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -c:a aac -b:a 128k \
  -movflags +faststart "deliver/$NAME.mp4"
ls -la "deliver/$NAME.mp4"
