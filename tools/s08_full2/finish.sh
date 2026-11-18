#!/bin/bash
# Join the rendered parts of song 08's version 2 backdrop and make the three deliveries:
#   stage  silent, H.264 CRF 16, yuv420p, faststart, 225.0 s (live length 210.0 s plus the 15 s calm hold)
#   review the same picture with the reference recording (209.08 s, within 1 s of the live length, so used as
#          is, padded with silence), AAC 320k, CRF 20
#   phone  1280x720 at 60 fps with the music, under 25 MB (two-pass)
#   tools/s08_full2/finish.sh <parts dir> <recording.mp3> <out dir>
# Parts are p00000.mp4, p03375.mp4 ... from tools/s08_full2/render.py --range. Nothing here goes in git.
# No em dash or en dash anywhere in this file.
set -euo pipefail
P=$(realpath "$1"); A=$(realpath "$2"); mkdir -p "$3"; O=$(realpath "$3")
TOTAL=225.0
N="08 Out of Heaven, Favor From God - Backdrop v2"
ls "$P"/p*.mp4 | sort | sed "s|^|file '|; s|$|'|" > "$O/parts.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$O/parts.txt" -c copy "$O/joined.mp4"
COLOR="-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv"
ffmpeg -v error -y -i "$O/joined.mp4" -map 0:v -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 60 \
  $COLOR -movflags +faststart -t $TOTAL "$O/$N - stage 1080p60.mp4"
# the music from 0, padded with silence to the end of the picture
ffmpeg -v error -y -i "$A" -af "apad=whole_dur=$TOTAL" -t $TOTAL -ar 48000 -ac 2 -c:a pcm_s24le "$O/score.wav"
ffmpeg -v error -y -i "$O/joined.mp4" -i "$O/score.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 \
  -pix_fmt yuv420p -r 60 $COLOR -c:a aac -b:a 320k -movflags +faststart -t $TOTAL "$O/$N - review 1080p60.mp4"
VB=$(python3 -c "print(int((23.5*8*1000*1000/$TOTAL - 128000)/1000))")
ffmpeg -v error -y -i "$O/joined.mp4" -vf scale=1280:720:flags=lanczos -r 60 -c:v libx264 -preset slow -b:v ${VB}k \
  -pass 1 -passlogfile "$O/x264" -an -f mp4 /dev/null
ffmpeg -v error -y -i "$O/joined.mp4" -i "$O/score.wav" -map 0:v -map 1:a -vf scale=1280:720:flags=lanczos -r 60 \
  -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile "$O/x264" -pix_fmt yuv420p $COLOR \
  -c:a aac -b:a 128k -movflags +faststart -t $TOTAL "$O/$N - phone 720p60.mp4"
ls -l "$O"/*.mp4
