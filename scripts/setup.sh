#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ is required"'
python3 -m venv .venv-modern
.venv-modern/bin/python -m pip install -r backend/requirements.txt -r backend/requirements-separation.txt
.venv-modern/bin/python -m pip check
.venv-modern/bin/python -c 'import torch, transformers, faster_whisper, demucs'
printf 'Project runtime validated\n' > .venv-modern/.moodscope-validated
npm ci
npm run build
