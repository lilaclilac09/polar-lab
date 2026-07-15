#!/usr/bin/env bash
# Run enabled Polar Lab stages. From polar-lab/: ./run_all.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

CFG="${1:-configs/base.yaml}"
PYTHON="${PYTHON:-python3}"

echo "== dry-run SFT =="
"$PYTHON" scripts/01_sft.py --config "$CFG" --dry-run

if [[ "${RUN_SFT:-0}" == "1" ]]; then
  echo "== SFT =="
  "$PYTHON" scripts/01_sft.py --config "$CFG"
fi

if [[ "${RUN_DPO:-0}" == "1" ]]; then
  echo "== DPO =="
  "$PYTHON" scripts/02_dpo.py --config "$CFG"
fi

if [[ "${RUN_RL:-0}" == "1" ]]; then
  echo "== RL scaffold =="
  "$PYTHON" scripts/03_rl.py --config "$CFG"
fi

echo "== data_gen (optional sidecar files) =="
"$PYTHON" scripts/data_gen.py --config "$CFG" --kind all --n 8

echo "Done. Set RUN_SFT=1 RUN_DPO=1 to execute trainers."
