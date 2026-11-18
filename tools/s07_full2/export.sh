#!/bin/bash
# Song 07 v2: render the stage video in parallel parts (this cloud session only), join them and make the three
# delivery files. Nothing here goes in git.  No em dash or en dash in this file.
#   tools/s07_full2/export.sh render <partdir> [workers] [parts]
#   tools/s07_full2/export.sh finish <partdir> <outdir>
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
total=15180            # 253.0 s at 60 fps
name="07 May No One Ever Feel Lonely - Backdrop v2"
if [ "$1" = render ]; then
  dir=$2; workers=${3:-$(nproc)}; parts=${4:-16}; mkdir -p "$dir"
  step=$(( (total + parts - 1) / parts ))
  for ((k=0; k<parts; k++)); do
    a=$((k * step)); b=$(( a + step < total ? a + step : total ))
    f=$(printf "%s/part%02d.mp4" "$dir" $k)
    [ -s "$f.done" ] && continue
    echo "python $here/render.py --range $a $b --out $f > $f.log 2>&1 && echo ok > $f.done"
  done | xargs -P "$workers" -I{} bash -c "{}"
  ls "$dir"/*.done | wc -l
elif [ "$1" = finish ]; then
  dir=$2; out=$3; mkdir -p "$out"
  ls "$dir"/part*.mp4 | sort | sed "s/^/file '/; s/$/'/" > "$out/list.txt"
  # stage: silent, H.264 CRF 16, yuv420p, faststart
  ffmpeg -v error -y -f concat -safe 0 -i "$out/list.txt" -map 0:v -c:v libx264 -preset slow -crf 16 \
    -pix_fmt yuv420p -r 60 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
    -movflags +faststart "$out/$name - stage 1080p60.mp4"
  # review: same picture with the reference music conformed to the live length (atempo, pitch kept)
  ffmpeg -v error -y -i "$out/$name - stage 1080p60.mp4" -i "$root/work/s07v2/review.wav" -map 0:v -map 1:a \
    -af "volume=-1.5dB" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 320k -ar 48000 \
    -t 253.0 -movflags +faststart "$out/$name - review 1080p60.mp4"
  # phone: 720p60 with music, under 25 MB
  ffmpeg -v error -y -i "$out/$name - stage 1080p60.mp4" -i "$root/work/s07v2/review.wav" -map 0:v -map 1:a \
    -af "volume=-1.5dB" -vf scale=1280:720 -c:v libx264 -preset slow -b:v 600k -maxrate 900k -bufsize 1800k \
    -pix_fmt yuv420p -r 60 -c:a aac -b:a 96k -ar 48000 -t 253.0 -movflags +faststart "$out/$name - phone 720p60.mp4"
  ls -l "$out"/*.mp4
  (cd "$out" && sha256sum *.mp4)
fi
