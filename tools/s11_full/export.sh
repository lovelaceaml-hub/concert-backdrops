#!/bin/bash
# Render song 11's full backdrop in parallel chunks on this machine, then join with the score.
#   bash tools/s11_full/export.sh [workers]
# Parts go to work/s11_full/parts (untracked); finished files to out/s11_full (untracked).
set -e
cd "$(dirname "$0")/../.."
W=${1:-4}
N=8496            # frames: (268.18 + 15) s at 30 fps
STEP=300
mkdir -p work/s11_full/parts out/s11_full
seq 0 $STEP $((N - 1)) | xargs -P "$W" -I{} bash -c '
  a={}; b=$((a + '$STEP')); [ $b -gt '$N' ] && b='$N'
  f=work/s11_full/parts/p$(printf %05d $a).mp4
  if [ -f "$f.ok" ]; then exit 0; fi
  python tools/s11_full/render.py --range $a $b --out "$f" > "$f.log" 2>&1 && touch "$f.ok"
'
ls work/s11_full/parts/*.mp4 | sort | sed "s/^/file '\.\.\/\.\.\//; s/$/'/" > work/s11_full/parts/list.txt
