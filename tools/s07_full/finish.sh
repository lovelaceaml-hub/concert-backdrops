#!/bin/sh
# Join the rendered parts with the music (then 15 s of silence), make the master and the share copy, check them.
# Usage: tools/s07_full/finish.sh PARTDIR AUDIO.mp3 OUTDIR     (cloud only; nothing here goes in git)
set -e
parts=$1; audio=$2; out=$3
mkdir -p "$out"
ls "$parts"/*.mp4 | sort -V | sed "s/^/file '/; s/$/'/" > "$out/list.txt"
name="07 May No One Ever Feel Lonely Backdrop"
dur=261.533333
ffmpeg -v error -y -f concat -safe 0 -i "$out/list.txt" -i "$audio" -map 0:v -map 1:a \
  -af "volume=-1.5dB,apad=whole_dur=$dur" -t $dur -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart "$out/$name 1080p30.mp4"
ffmpeg -v error -y -i "$out/$name 1080p30.mp4" -vf scale=1280:720 -c:v libx264 -preset slow -b:v 560k \
  -maxrate 900k -bufsize 1800k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart \
  "$out/$name share 720p.mp4"
ls -l "$out"/*.mp4
