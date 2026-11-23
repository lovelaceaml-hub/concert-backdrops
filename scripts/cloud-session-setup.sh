#!/usr/bin/env bash
# Prepares a Claude Code cloud session for the concert project.
# Runs only in cloud sessions (CLAUDE_CODE_REMOTE=true). Never renders anything.
# Best effort: it always exits 0 so a setup problem never blocks the session;
# read work/cloud-setup.log for the outcome.
set -u
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || exit 0
mkdir -p work
log=work/cloud-setup.log
marker=work/.cloud-setup-done
if [ -f "$marker" ] && [ -d .venv ] && [ -d node_modules ]; then
  echo "Concert cloud setup: already prepared (see $log)."
  exit 0
fi
{
  echo "== cloud setup $(date -u +%FT%TZ)"
  # FFmpeg may already be present while the software EGL libraries the renderer needs are not.
  if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1 \
     || ! ldconfig -p 2>/dev/null | grep -q 'libEGL\.so'; then
    if command -v apt-get >/dev/null 2>&1; then
      SUDO=""; [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1 && SUDO="sudo"
      # The package mirror sometimes times out through the sandbox proxy; retry before giving up.
      for attempt in 1 2 3; do
        $SUDO apt-get update -qq && $SUDO apt-get install -y -qq ffmpeg libegl1 libegl-mesa0 libgl1 libgles2 && break
        echo "WARN: apt install attempt $attempt failed"; sleep 20
      done
    fi
  fi
  if ! command -v uv >/dev/null 2>&1; then
    python3 -m pip install --quiet --user uv || pip install --quiet uv || echo "WARN: uv install failed"
    export PATH="$HOME/.local/bin:$PATH"
  fi
  if python3 scripts/bootstrap.py --p3d-only --reference-fonts; then
    touch "$marker"
    echo "== cloud setup finished OK"
  else
    echo "== cloud setup FAILED; rerun: bash scripts/cloud-session-setup.sh"
  fi
} >>"$log" 2>&1
if [ -f "$marker" ]; then
  echo "Concert cloud setup: p3d runtime and reference fonts ready."
else
  echo "Concert cloud setup did not finish. Read $log before rendering."
fi
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
exit 0
