#!/usr/bin/env bash
# Song 04 full backdrop, version 2: everything a fresh cloud machine needs before render.py runs.
#   bash tools/s04_full2/prepare.sh /path/to/s04.mp3
# The reference audio is the church's upload, kept on Anthony's private Artifact page (never in git); this
# script checks its SHA-256, conforms it to the live length (220.0 s, pitch kept) and measures it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${1:?give the path of s04.mp3}"
WORK="$ROOT/work/s04v2"
mkdir -p "$WORK"
echo "a1fa529d6f6dd5f477a429f7c8587c017ed94efebabe669fa8e05e1dd32e7220  $SRC" | sha256sum -c -
cp -f "$SRC" "$WORK/s04.mp3"

# system and Python packages, fonts (as .github/workflows/render.yml)
if ! python -c "import moderngl, librosa" 2>/dev/null; then
  pip install -q numpy scipy librosa moderngl pillow fonttools brotli soundfile
fi
if ! ldconfig -p | grep -q libEGL.so.1; then
  apt-get update -q && apt-get install -y -q libegl1 libgles2 libgl1-mesa-dri libegl-mesa0 ffmpeg
fi
if [ ! -d "$ROOT/fonts" ] || [ -z "$(ls -A "$ROOT/fonts" 2>/dev/null)" ]; then
  mkdir -p /tmp/fs && (cd /tmp/fs && npm pack -q @fontsource/cormorant-garamond @fontsource/jost @fontsource/outfit >/dev/null \
    && for f in *.tgz; do d="${f%.tgz}"; mkdir -p "$d"; tar xzf "$f" -C "$d"; done)
  (cd "$ROOT" && python tools/setup_fonts.py /tmp/fs fonts)
fi

# the pinned Film 10 engine and Claude Final v1 snapshots
(cd "$ROOT" && git fetch -q origin ten/10-nine-colours 2>/dev/null || true)
(cd "$ROOT" && git fetch -q origin f43f4514e4bc42dc25166e90160d98219f5a0db4 2>/dev/null || true)
(cd "$ROOT" && python tools/nine_colours_minor/prepare.py)

# the music: decode, conform 219.435 s -> exactly 220.0 s (atempo, pitch kept), measure
cd "$WORK"
ffmpeg -v error -y -i s04.mp3 -c:a pcm_s24le -ar 48000 ref.wav
R=$(python -c "import soundfile as sf; i = sf.info('ref.wav'); print(repr(i.frames / i.samplerate / 220.0))")
ffmpeg -v error -y -i ref.wav -af "atempo=$R,apad" -t 220.0 -ar 48000 -c:a pcm_s24le live.wav
ffmpeg -v error -y -i live.wav -af "apad" -t 235.0 -ar 48000 -c:a pcm_s24le live_hold.wav
ffmpeg -v error -y -i live.wav -ac 1 -ar 22050 audio.wav
NUMBA_CACHE_DIR="$WORK/numba" python "$ROOT/work/nine_colours_minor/render1/engine/analyze.py" audio.wav features.npz >/dev/null
sha256sum features.npz
echo "prepared: $WORK (tempo factor $R)"
