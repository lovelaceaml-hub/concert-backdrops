#!/bin/bash
# Join the rendered parts of song 08's full backdrop, add the music (then 15 s of silence) and make the
# master (H.264 CRF 18, yuv420p, AAC 320k, faststart) and the share copy (1280x720, under 25 MB).
#   tools/s08_full/finish.sh <parts dir> <recording.mp3> <out dir>
# Parts are p0000.mp4, p0840.mp4 ... from tools/s08_full/render.py --range. Nothing here goes in git.
set -euo pipefail
P=$(realpath "$1"); A=$(realpath "$2"); O=$3; mkdir -p "$O"; O=$(realpath "$O")
TOTAL=224.1
mkdir -p "$O"
ls "$P"/p*.mp4 | sort | sed "s|^|file '|; s|$|'|" > "$O/parts.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$O/parts.txt" -c copy "$O/joined.mp4"
# the music from 0, padded with silence to the end of the picture
ffmpeg -v error -y -i "$A" -af "apad=whole_dur=$TOTAL" -t $TOTAL -ar 48000 -ac 2 -c:a pcm_s24le "$O/score.wav"
M="$O/08 Out of Heaven, Favor From God - Backdrop.mp4"
S="$O/08 Out of Heaven, Favor From God - Backdrop (share 720p).mp4"
ffmpeg -v error -y -i "$O/joined.mp4" -i "$O/score.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 320k -movflags +faststart -t $TOTAL "$M"
# share copy: two-pass at a bitrate that keeps it under 25 MB
VB=$(python3 -c "print(int((24.0*8*1000*1000/$TOTAL - 128000)/1000))")
ffmpeg -v error -y -i "$M" -vf scale=1280:720 -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile "$O/x264" -an -f mp4 /dev/null
ffmpeg -v error -y -i "$M" -vf scale=1280:720 -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile "$O/x264" \
  -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$S"
ls -l "$M" "$S"
