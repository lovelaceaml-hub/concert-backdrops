#!/usr/bin/env bash
# Full video render in this cloud session, used while GitHub Actions is blocked (billing).
# Same recipe as .github/workflows/render.yml: parts at crf 16, concat, mux the audio, 1280x720 share copy, contact sheet, QA.
# Usage: local_full.sh WORKTREE SONG AUDIO NAME OUTDIR [PARTS]
#   NAME has no parentheses (e.g. "Masterpiece v4"); OUTDIR outside the repo (scratchpad).
# Parts render two at a time (the shared machine has 4 cores); expect roughly 1.5 to 3 hours for 60 s.
set -euo pipefail
WT=$(cd "$1" && pwd); SONG=$2; AUDIO=$3; NAME=$4; OUT=$5; PARTS=${6:-8}
TOOLS=/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/tools
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
N=$(cd "$WT/engine" && SONG=$SONG AUDIO="$WT/$AUDIO" FEATURES="$WT/work/$SONG/features.npz" OUT_RES=1080p OUT_FPS=30 python3 draft.py --frames 2>/dev/null || echo 1800)
step=$(( (N + PARTS - 1) / PARTS ))
echo "frames $N in $PARTS parts of $step"
pids=()
for ((p=0; p<PARTS; p++)); do
  A=$(( p * step )); B=$(( A + step )); (( B > N )) && B=$N
  ( LOCAL_FULL=1 "$TOOLS/local_render.sh" "$WT" "$SONG" "$AUDIO" frames "$A" "$B" "$OUT/p$p" > "$OUT/p$p.log" 2>&1 && mv "$OUT/p$p/frames_${A}_${B}.mp4" "$OUT/part$p.mp4" ) &
  pids+=($!)
done
fail=0; for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
(( fail == 0 )) || { echo "a part failed; see $OUT/p*.log"; exit 1; }
cd "$OUT"
: > list.txt; for ((p=0; p<PARTS; p++)); do echo "file 'part$p.mp4'" >> list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy silent.mp4
ffmpeg -v error -y -i silent.mp4 -i "$WT/$AUDIO" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart "$NAME.mp4"
fd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$NAME.mp4")
vb=$(python3 -c "print(int(min(2600, 24e6*8/1000/$fd - 160)))")
ffmpeg -v error -y -i "$NAME.mp4" -vf "fps=30,scale=1280:720:flags=lanczos" -c:v libx264 -preset slow \
  -crf 21 -maxrate "${vb}k" -bufsize "$(( vb * 2 ))k" -pix_fmt yuv420p -g 60 \
  -c:a aac -b:a 160k -movflags +faststart "$NAME (share).mp4"
ffmpeg -v error -y -i silent.mp4 -vf "fps=1,scale=256:-2,tile=10x6" -frames:v 1 -q:v 3 sheet1s.jpg || true
if [[ -f "$WT/tools/qa_check.py" ]]; then (cd "$WT" && python3 tools/qa_check.py --song "$SONG" --video "$OUT/$NAME (share).mp4" --out "$OUT/qa" --name "$NAME") || true; fi
echo "done: $OUT/$NAME.mp4 and $OUT/$NAME (share).mp4 ($fd s)"
