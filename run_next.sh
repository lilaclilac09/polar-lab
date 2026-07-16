#!/usr/bin/env bash
# Polar Lab — one-shot next run (CPU / CUDA / MPS)
# Usage:
#   ./run_next.sh              # train + holdout eval
#   ./run_next.sh --setup-only # install deps + device check
#   ./run_next.sh --eval-only  # score existing adapter only

set -euo pipefail
cd "$(dirname "$0")"

SETUP_ONLY=0
EVAL_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --setup-only) SETUP_ONLY=1 ;;
    --eval-only) EVAL_ONLY=1 ;;
    -h|--help)
      echo "Usage: $0 [--setup-only|--eval-only]"
      exit 0
      ;;
  esac
done

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip

# Pick torch wheel: CUDA > default (MPS/mac) > CPU
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  echo "[setup] NVIDIA GPU detected → CUDA torch (cu124)"
  pip install -q torch --index-url https://download.pytorch.org/whl/cu124
else
  echo "[setup] No nvidia-smi → default torch (MPS on Apple Silicon, else CPU)"
  pip install -q torch
fi
pip install -q -r requirements.txt

python - <<'PY'
from utils.device import resolve_device
import torch
d = resolve_device("auto")
print(f"[device] {d}")
if d == "cuda":
    print(f"[gpu] {torch.cuda.get_device_name(0)}")
PY

if [[ "$SETUP_ONLY" -eq 1 ]]; then
  echo "[done] setup-only"
  exit 0
fi

python scripts/check_data.py

if [[ "$EVAL_ONLY" -eq 0 ]]; then
  python scripts/01_sft.py --dry-run --config configs/machina_sft.yaml
  python scripts/01_sft.py --config configs/machina_sft.yaml
fi

python scripts/05_eval_holdout.py --adapter outputs/sft/adapter --max-new-tokens 48
python scripts/05_eval_holdout.py --adapter "" --metrics-out outputs/eval/metrics_base.json --max-new-tokens 48

echo
echo "[done] LoRA metrics:  outputs/eval/metrics.json"
echo "[done] Base metrics:  outputs/eval/metrics_base.json"
echo "[done] Log a row in:  logs/week_01.md"
echo "[done] Baseline to beat: exact_match 0.200 (CPU 2026-07-15)"
