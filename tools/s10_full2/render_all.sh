#!/usr/bin/env bash
# Render song 10's full backdrop, version 2, in parallel ranges in THIS cloud session (never the Render
# workflow, never a paid service), then join and check: tools/s10_full2/finish.py.
#   bash tools/s10_full2/render_all.sh [jobs] [chunk_frames]
# Parts go to out/s10_full2/parts/ (ignored by git); a part that already exists is skipped (resumable).
# No em dash or en dash anywhere in this file.
set -u
cd "$(dirname "$0")/../.."
JOBS=${1:-$(nproc)}
CHUNK=${2:-360}
NF=13560
mkdir -p out/s10_full2/parts out/s10_full2/logs
seq 0 $CHUNK $((NF - 1)) | xargs -P "$JOBS" -I{} bash -c '
  a={}; b=$((a + '"$CHUNK"')); [ $b -gt '"$NF"' ] && b='"$NF"'
  f=$(printf "out/s10_full2/parts/p%05d.mp4" $a)
  [ -s "$f" ] && exit 0
  python3 tools/s10_full2/render.py --range $a $b --out "$f.tmp.mp4" > out/s10_full2/logs/$(basename $f).log 2>&1 \
    && mv "$f.tmp.mp4" "$f" || echo "FAILED $a $b"
'
ls out/s10_full2/parts/*.mp4 | grep -vc tmp
