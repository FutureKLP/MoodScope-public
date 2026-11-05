#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${1:-}" == "--desktop" ]]; then
  .venv/bin/python -m scripts.service --port 8765 &
  backend_pid=$!
  trap 'kill "$backend_pid" 2>/dev/null || true' EXIT
  npm run tauri dev
else
  [[ -f dist/index.html ]] || npm run build
  echo 'MoodScope: http://127.0.0.1:8765'
  exec .venv/bin/python -m scripts.service --port 8765
fi
