#!/usr/bin/env bash
# Render stills or a draft in this cloud session, with the same recipe as .github/workflows/render.yml.
# Anthony approved a mixed set-up: stills and drafts here, final full videos on GitHub Actions.
#
# Usage (run from anywhere; WORKTREE is the root of your git worktree):
#   local_render.sh WORKTREE SONG AUDIO stills "3,7.5,12" OUTDIR
#   local_render.sh WORKTREE SONG AUDIO draft OUTDIR
#   local_render.sh WORKTREE SONG AUDIO frames A B OUTDIR      (full quality frames A..B-1 as an mp4, for short motion checks only)
# SONG is the song file name without .py; AUDIO is a path inside the worktree (audio/...mp3).
# OUTDIR must be outside the repo (use your scratchpad folder).
#
# This machine has 4 cores shared by every helper. The script queues: at most two renders run at once,
# each on two threads. Keep jobs small: stills lists of up to about 30 moments, one draft at a time,
# "frames" for at most about 150 frames. Full videos go through the GitHub workflow.
set -euo pipefail
WT=$(cd "$1" && pwd); SONG=$2; AUDIO=$3; MODE=$4; shift 4
BASE=/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/localrender
mkdir -p "$BASE/fs" "$BASE/locks"
[[ "$SONG" =~ ^[a-z0-9_]+$ ]] || { echo "bad song name"; exit 1; }
[[ -f "$WT/engine/songs/$SONG.py" ]] || { echo "no such song file in $WT"; exit 1; }
[[ -f "$WT/$AUDIO" ]] || { echo "no such audio file in $WT"; exit 1; }

export LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=2 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export SONG AUDIO="$WT/$AUDIO" FEATURES="$WT/work/$SONG/features.npz" OUT_RES=1080p OUT_FPS=30

# fonts (shared download, converted once per worktree)
(
  flock 9
  cd "$BASE/fs"
  ls ./*.tgz >/dev/null 2>&1 || npm pack -q @fontsource/cormorant-garamond @fontsource/jost >/dev/null
  ls ./fontsource-outfit-*.tgz >/dev/null 2>&1 || npm pack -q @fontsource/outfit >/dev/null
  for f in ./*.tgz; do d="${f%.tgz}"; [[ -d "$d" ]] || { mkdir -p "$d"; tar xzf "$f" -C "$d"; }; done
) 9>"$BASE/locks/fonts.lock"
[[ -d "$WT/fonts" && -n "$(ls -A "$WT/fonts" 2>/dev/null)" && -f "$WT/fonts/outfit-latin-800-normal.ttf" ]] || (cd "$WT" && python3 tools/setup_fonts.py "$BASE/fs" fonts >/dev/null)

# measure the music (once per song and audio file)
mkdir -p "$WT/work/$SONG"
stamp="$WT/work/$SONG/.audio_src"
if [[ ! -f "$FEATURES" || ! -f "$stamp" || "$(cat "$stamp")" != "$AUDIO $(stat -c %Y "$AUDIO")" ]]; then
  ffmpeg -v error -y -i "$AUDIO" -ac 1 -ar 22050 "$WT/work/$SONG/audio.wav"
  (cd "$WT" && python3 engine/analyze.py "work/$SONG/audio.wav" "work/$SONG/features.npz" >/dev/null)
  echo "$AUDIO $(stat -c %Y "$AUDIO")" > "$stamp"
fi

# queue: take one of two slots
exec 8>"$BASE/locks/slot1.lock"
if ! flock -n 8; then
  exec 8>"$BASE/locks/slot2.lock"
  if ! flock -n 8; then
    echo "both render slots are busy; waiting in the queue..."
    exec 8>"$BASE/locks/slot$(( (RANDOM % 2) + 1 )).lock"
    flock 8
  fi
fi
t0=$(date +%s)

case "$MODE" in
  stills)
    STILLS=$1; OUT=$2
    [[ "$STILLS" =~ ^[0-9.,]*$ ]] || { echo "bad stills list"; exit 1; }
    mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
    (cd "$WT/engine" && python3 render.py --stills "$STILLS" --outdir "$OUT")
    if [[ -f "$WT/tools/qa_check.py" ]]; then
      (cd "$WT" && python3 tools/qa_check.py --song "$SONG" --stills "$OUT" --out "$OUT" --name local) || true
    fi
    ;;
  draft)
    OUT=$1; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
    [[ -f "$WT/engine/draft.py" ]] || { echo "this branch has no engine/draft.py"; exit 1; }
    N=$(cd "$WT/engine" && python3 draft.py --frames)
    (cd "$WT/engine" && python3 draft.py --range 0 "$N" --out "$OUT/silent.mp4")
    ffmpeg -v error -y -i "$OUT/silent.mp4" -i "$AUDIO" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart "$OUT/draft.mp4"
    d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/silent.mp4")
    r=$(python3 -c "print(round(30/$d, 5))")
    ffmpeg -v error -y -i "$OUT/silent.mp4" -vf "fps=$r,scale=320:-2,tile=6x5" -frames:v 1 -q:v 4 "$OUT/contact_sheet.jpg" || true
    if [[ -f "$WT/tools/qa_check.py" ]]; then
      (cd "$WT" && python3 tools/qa_check.py --song "$SONG" --video "$OUT/silent.mp4" --out "$OUT" --name local-draft) || true
    fi
    ;;
  frames)
    A=$1; B=$2; OUT=$3; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
    (( B - A <= 240 )) || [[ "${LOCAL_FULL:-}" == 1 ]] || { echo "at most 240 full quality frames here; use the GitHub workflow for more"; exit 1; }
    (cd "$WT/engine" && python3 render.py --range "$A" "$B" --out "$OUT/frames_${A}_${B}.mp4" --crf 16)
    ;;
  *) echo "mode must be stills, draft or frames"; exit 1;;
esac
echo "done in $(( $(date +%s) - t0 )) s: $MODE -> ${OUT}"
