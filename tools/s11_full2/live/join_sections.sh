#!/bin/bash
# Join section videos (in film order) into one full film, without re-rendering.
# Usage: join_sections.sh <out.mp4> <intro.mp4> <verse1.mp4> ... <ending.mp4>
# The inputs must share codec, size, frame rate and pixel format (the section_build.sh outputs do).
# The video stream is copied unchanged (no quality loss); the audio is re-encoded once so the joins are seamless.
# Never commit the result: finished videos stay out of git.
set -euo pipefail
out="$1"; shift
[ "$#" -ge 2 ] || { echo "need the output and at least two sections" >&2; exit 1; }
list=$(mktemp)
trap 'rm -f "$list"' EXIT
first=""
for f in "$@"; do
  p=$(realpath "$f")
  sig=$(ffprobe -v error -select_streams v -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt -of csv=p=0 "$p")
  [ -z "$first" ] && first="$sig"
  [ "$sig" = "$first" ] || { echo "format differs: $f ($sig vs $first)" >&2; exit 1; }
  printf "%s %s\n" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$p")" "$f"
  printf "file '%s'\n" "$p" >> "$list"
done
ffmpeg -v error -y -f concat -safe 0 -i "$list" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$out"
echo "out: $(ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$out")"
echo "frames: $(ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$out")"
# Gaps at the joins show up here as silences in the middle of the film:
ffmpeg -v info -i "$out" -af silencedetect=n=-55dB:d=0.15 -f null - 2>&1 | grep -o "silence_[a-z]*: [0-9.]*" || true
