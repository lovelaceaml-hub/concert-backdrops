#!/usr/bin/env bash
# Render song 10's full backdrop in parallel ranges in THIS cloud session (never the paid Render workflow),
# then join with the soundtrack: tools/s10_full/finish.py.
#   bash tools/s10_full/render_all.sh [jobs] [chunk_frames]
# Parts go to out/s10_full/parts/ (ignored by git); a part that already exists is skipped (resumable).
set -u
cd "$(dirname "$0")/../.."
JOBS=${1:-$(nproc)}
CHUNK=${2:-300}
NF=6799
mkdir -p out/s10_full/parts out/s10_full/logs
seq 0 $CHUNK $((NF - 1)) | xargs -P "$JOBS" -I{} bash -c '
  a={}; b=$((a + '"$CHUNK"')); [ $b -gt '"$NF"' ] && b='"$NF"'
  f=$(printf "out/s10_full/parts/p%05d.mp4" $a)
  [ -s "$f" ] && exit 0
  python tools/s10_full/render.py --range $a $b --out "$f.tmp.mp4" > out/s10_full/logs/$(basename $f).log 2>&1 \
    && mv "$f.tmp.mp4" "$f" || echo "FAILED $a $b"
'
ls out/s10_full/parts/*.mp4 | grep -vc tmp
