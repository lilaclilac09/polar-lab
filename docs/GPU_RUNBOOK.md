# GPU runbook — Polar Lab

Copy-paste path for **NVIDIA CUDA** hosts (cloud or local).  
CPU results from 2026-07-15 are the baseline to beat.

## 0) Prerequisites

```bash
nvidia-smi
# Expect: a listed GPU + Driver Version. If this fails, stop — you are on CPU-only.
```

**You do not need an RTX 4090.** Polar Lab smoke (`Qwen2.5-0.5B` + LoRA) is intentionally small.

| Hardware | OK for 0.5B LoRA? | Notes |
|----------|-------------------|-------|
| Cloud T4 / L4 / A10 (16GB) | Yes — preferred if you have no local GPU | Rent hourly (RunPod, Vast, Lambda, etc.) |
| Laptop 8GB (e.g. 3070 laptop, 4060) | Usually yes | Use batch size 1; watch OOM |
| 6–8GB consumer cards | Often yes at batch 1 | Keep `max_seq_length` 512; stay on 0.5B |
| Mac Apple Silicon | Use **MPS**, not CUDA | `pip install torch` (default); `device: auto` → `mps` |
| CPU only | Yes (slower) | Already verified 2026-07-15; fine for learning the loop |
| Jump to 1.5B | Needs more VRAM | Only after short-fact `exact_match` is useful |

Recommended for comfortable smoke: **≥8GB VRAM**. A 4090 is optional speed, not a requirement.

## 1) Checkout

```bash
git clone https://github.com/lilaclilac09/polar-lab.git
cd polar-lab

# Until PR #1 is merged, use the working branch:
# git fetch origin cursor/polar-lab-agent-ci-9940
# git checkout cursor/polar-lab-agent-ci-9940
```

## 2) Environment (CUDA torch — do not install CPU wheels)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu124
# Older stacks: .../whl/cu121
pip install -r requirements.txt

# Optional
# export HF_TOKEN=hf_xxx
```

## 3) Device check

```bash
python - <<'PY'
import torch
from utils.device import resolve_device
assert torch.cuda.is_available(), "CUDA not visible — check driver / torch wheel"
print("gpu:", torch.cuda.get_device_name(0))
print("device:", resolve_device("auto"))  # must be cuda
print("bf16:", torch.cuda.is_bf16_supported())
PY
```

Force GPU in config if needed:

```yaml
device: cuda
dtype: auto
```

## 4) Data gate

```bash
python scripts/check_data.py
# expect: ok true, overlap 0
```

Current pack: Machina-washed facts in `data/sft_train.jsonl` / `data/sft_eval.jsonl`  
(see `data/README.md`).

## 5) Train on GPU

```bash
python scripts/01_sft.py --dry-run
# JSON should show "device": "cuda"

python scripts/01_sft.py --config configs/machina_sft.yaml
# → outputs/sft/adapter
```

While training, in another shell:

```bash
watch -n 1 nvidia-smi
```

### Optional knobs (edit `configs/machina_sft.yaml`)

| Knob | Start | If VRAM OK | If OOM |
|------|-------|------------|--------|
| `sft.per_device_train_batch_size` | 1 | 2–4 | stay 1; keep grad accum 4 |
| `sft.max_steps` | 120 | 200–400 | — |
| `lora.r` | 16 | 16–32 | lower to 8 |
| `model.name_or_path` | `Qwen2.5-0.5B-Instruct` | try `1.5B` only after short-fact score moves | revert to 0.5B |

## 6) Holdout benchmark

```bash
python scripts/05_eval_holdout.py --adapter outputs/sft/adapter --max-new-tokens 48
cat outputs/eval/metrics.json
```

Compare against **base** (no adapter):

```bash
python scripts/05_eval_holdout.py --adapter "" \
  --metrics-out outputs/eval/metrics_base.json --max-new-tokens 48
```

### Benchmark must satisfy

1. Train/eval prompts disjoint (`check_data.py`)
2. Eval never used in training
3. Fixed decode: `temperature=0` / greedy (script default)
4. Primary metric: **`exact_match`** on holdout
5. Report **base vs LoRA** side by side

### Suggested pass bar (GPU re-run)

| Gate | Target |
|------|--------|
| Smoke | job finishes; `device=cuda`; metrics JSON written |
| Useful | holdout `exact_match` **≥ 0.60** on short-fact eval |
| Clear win | LoRA **≥ base + 0.20** absolute |
| Do not claim win | chat vibes only, or train/eval overlap |

CPU baseline (2026-07-15, short-fact v2): **exact_match = 0.200 (2/10)**.

## 7) Log the run

Append a row to `logs/week_01.md`:

```text
| date | gpu name | config | steps | train_rows | train_loss | eval_loss | exact_match | notes |
```

Copy `outputs/eval/metrics.json` numbers into the day note (do not commit adapters).

## 8) Common failures

| Symptom | Fix |
|---------|-----|
| `CUDA requested but not available` | Wrong torch wheel (CPU) or no driver |
| OOM during SFT | batch=1, shorter `max_seq_length`, stay on 0.5B |
| Slow download from Hub | `huggingface-cli login` / `HF_TOKEN` |
| exact_match stuck ~0.2 | add more short “reply with only …” pairs — not a bigger model first |
