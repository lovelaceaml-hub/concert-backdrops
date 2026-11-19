#!/usr/bin/env bash
# Render song 10's full backdrop, version 2, in parallel ranges in THIS cloud session (never the Render
# workflow, never a paid service), then join and check: tools/s10_full2/finish.py.
#   bash tools/s10_full2/render_all.sh [jobs] [chunk_frames]
#   S10_OUT=out/s10_full2/fix1 bash tools/s10_full2/render_all.sh 4 360     (fix 1 goes to its own folder)
# Parts go to $S10_OUT/parts/ (ignored by git); a part that already exists is skipped (resumable).
# The slow touching scenes (Consideration, Inclusiveness, Gratitude: two bodies holding each other) are cut
# into short ranges and started first, so they do not hold up the end.
# No em dash or en dash anywhere in this file.
set -u
cd "$(dirname "$0")/../.."
JOBS=${1:-$(nproc)}
CHUNK=${2:-360}
OUTDIR=${S10_OUT:-out/s10_full2}
NF=13560
SLOW="4320:4680 5400:6120 11520:12240"
SHORT=90
mkdir -p "$OUTDIR/parts" "$OUTDIR/logs"
ranges() {
  for s in $SLOW; do
    a=${s%:*}; b=${s#*:}
    for ((x = a; x < b; x += SHORT)); do echo "$x $((x + SHORT < b ? x + SHORT : b))"; done
  done
  a=0
  for s in $SLOW; do
    s0=${s%:*}; s1=${s#*:}
    for ((x = a; x < s0; x += CHUNK)); do echo "$x $((x + CHUNK < s0 ? x + CHUNK : s0))"; done
    a=$s1
  done
  for ((x = a; x < NF; x += CHUNK)); do echo "$x $((x + CHUNK < NF ? x + CHUNK : NF))"; done
}
ranges | xargs -P "$JOBS" -L 1 bash -c '
  a=$0; b=$1
  f=$(printf "'"$OUTDIR"'/parts/p%05d.mp4" $a)
  [ -s "$f" ] && exit 0
  python3 tools/s10_full2/render.py --range $a $b --out "$f.tmp.mp4" > "'"$OUTDIR"'/logs/$(basename $f).log" 2>&1 \
    && mv "$f.tmp.mp4" "$f" || echo "FAILED $a $b"
'
ls "$OUTDIR"/parts/*.mp4 | grep -vc tmp
