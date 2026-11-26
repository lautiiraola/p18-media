#!/usr/bin/env bash
# Instala lo necesario para las skills P18 (idempotente: si ya está, no hace nada).
set -euo pipefail
VENV="${P18_VENV:-$HOME/.local/share/p18/venv}"

if [[ "$(uname)" == "Darwin" ]] && command -v brew >/dev/null; then
  for f in ffmpeg-full yt-dlp deno python@3.12; do
    brew list --formula "$f" >/dev/null 2>&1 || brew install "$f"
  done
  PY=/opt/homebrew/bin/python3.12
  [[ -x "$PY" ]] || PY="$(brew --prefix)/bin/python3.12"
else
  # Linux (p. ej. el entorno de Cowork): ffmpeg del sistema suele traer libass.
  command -v ffmpeg >/dev/null || { sudo apt-get update -y && sudo apt-get install -y ffmpeg; } || true
  PY="$(command -v python3)"
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/python" -c "import faster_whisper, playwright, PIL, yt_dlp" 2>/dev/null || \
  "$VENV/bin/pip" install -q faster-whisper playwright pillow yt-dlp
"$VENV/bin/python" -m playwright install chromium >/dev/null
echo "OK: entorno P18 listo en $VENV"
