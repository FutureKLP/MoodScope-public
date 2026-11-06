#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
project_python=".venv/bin/python"
if [[ -f .venv-modern/.moodscope-validated && -x .venv-modern/bin/python ]]; then project_python=".venv-modern/bin/python"; fi
if [[ "${1:-}" == "--desktop" ]]; then
  "$project_python" -m scripts.service --port 8765 &
  backend_pid=$!
  trap 'kill "$backend_pid" 2>/dev/null || true' EXIT
  npm run tauri dev
else
  [[ -f dist/index.html ]] || npm run build
  echo 'MoodScope: http://127.0.0.1:8765'
  exec "$project_python" -m scripts.service --port 8765
fi
