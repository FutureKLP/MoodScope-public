#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--cpu" ) ]]; then
  echo 'Usage: bash scripts/setup.sh [--cpu]' >&2
  exit 2
fi
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ is required"'
python3 -m venv .venv-modern
rm -f .venv-modern/.moodscope-validated
# Demucs pulls torchaudio as well. Select both from the same CPU wheel index;
# a PyPI torchaudio wheel can otherwise require CUDA beside a CPU-only torch.
if [[ "${1:-}" == "--cpu" ]]; then
  .venv-modern/bin/python -m pip install --force-reinstall torch torchaudio --index-url https://download.pytorch.org/whl/cpu
fi
.venv-modern/bin/python -m pip install -r backend/requirements.txt -r backend/requirements-separation.txt
.venv-modern/bin/python -m pip check
.venv-modern/bin/python -c 'import torch, torchaudio, transformers, faster_whisper, demucs; from transformers import ClapModel, ClapProcessor, pipeline'
printf 'Project runtime validated\n' > .venv-modern/.moodscope-validated
npm ci
npm run build
