#!/usr/bin/env bash
# Polar Lab — one-shot next run (CPU / CUDA / MPS)
# Usage:
#   ./run_next.sh                         # Machina pack (default)
#   POLAR_CONFIG=configs/space_sft.yaml ./run_next.sh   # space-engineering pack
#   ./run_next.sh --config=configs/space_sft.yaml
#   ./run_next.sh --setup-only
#   ./run_next.sh --eval-only

set -euo pipefail
cd "$(dirname "$0")"

SETUP_ONLY=0
EVAL_ONLY=0
CFG="${POLAR_CONFIG:-configs/machina_sft.yaml}"
for arg in "$@"; do
  case "$arg" in
    --setup-only) SETUP_ONLY=1 ;;
    --eval-only) EVAL_ONLY=1 ;;
    --config=*) CFG="${arg#--config=}" ;;
    -h|--help)
      echo "Usage: $0 [--setup-only|--eval-only] [--config=configs/....yaml]"
      echo "  or:  POLAR_CONFIG=configs/space_sft.yaml $0"
      exit 0
      ;;
  esac
done

echo "[config] $CFG"

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

# Resolve train/eval paths from the chosen YAML (no torch)
TRAIN_EVAL="$(python - <<PY
from utils.config import load_config
cfg = load_config("$CFG")
print(cfg["data"]["sft_train"])
print(cfg["data"]["sft_eval"])
PY
)"
TRAIN_PATH="$(echo "$TRAIN_EVAL" | sed -n '1p')"
EVAL_PATH="$(echo "$TRAIN_EVAL" | sed -n '2p')"
python scripts/check_data.py --train "$TRAIN_PATH" --eval "$EVAL_PATH"

if [[ "$EVAL_ONLY" -eq 0 ]]; then
  python scripts/01_sft.py --dry-run --config "$CFG"
  python scripts/01_sft.py --config "$CFG"
fi

python scripts/05_eval_holdout.py --config "$CFG" --adapter outputs/sft/adapter --max-new-tokens 48
python scripts/05_eval_holdout.py --config "$CFG" --adapter "" --metrics-out outputs/eval/metrics_base.json --max-new-tokens 48
python scripts/write_run_report.py

echo
echo "[done] LoRA metrics:  outputs/eval/metrics.json"
echo "[done] Base metrics:  outputs/eval/metrics_base.json"
echo "[done] Human report:  logs/LATEST_RUN_REPORT.md"
echo "[done] Log a row in:  logs/week_01.md"
echo "[done] Config used:   $CFG"
echo
echo "Open the report:"
echo "  open logs/LATEST_RUN_REPORT.md    # macOS"
echo "  xdg-open logs/LATEST_RUN_REPORT.md  # Linux"
echo "  Or just open that file in your editor."
