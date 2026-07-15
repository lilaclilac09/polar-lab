# Hands-on: run Qwen locally with Polar Lab

Verified smoke path: **Qwen2.5-0.5B-Instruct + LoRA SFT** on CPU (also works on MacBook MPS / CUDA).

Repo: [`lilaclilac09/polar-lab`](https://github.com/lilaclilac09/polar-lab)

## 0) One-time setup

```bash
git clone https://github.com/lilaclilac09/polar-lab.git
cd polar-lab

python3 -m venv .venv
source .venv/bin/activate

# CPU (Linux / cloud without GPU)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# MacBook Apple Silicon (MPS) — install default torch from PyPI instead:
#   pip install torch
#   pip install -r requirements.txt

# Optional Hugging Face token (higher rate limits)
#   export HF_TOKEN=hf_xxx
```

Check device:

```bash
python3 - <<'PY'
from utils.device import resolve_device
print(resolve_device("auto"))  # mps | cuda | cpu
PY
```

## 1) Dry-run (no download / no train)

```bash
python3 scripts/01_sft.py --dry-run
```

You should see `model: Qwen/Qwen2.5-0.5B-Instruct` and train/eval row counts.

## 2) Train LoRA SFT (smoke)

`configs/base.yaml` sets a short `max_steps` for a laptop/CPU run.

```bash
python3 scripts/01_sft.py --config configs/base.yaml
# → writes outputs/sft/adapter
```

Longer run — edit `configs/base.yaml`:

```yaml
sft:
  max_steps: -1          # full epochs
  num_train_epochs: 3
model:
  name_or_path: Qwen/Qwen2.5-1.5B-Instruct   # heavier; needs more RAM/VRAM
```

## 3) Chat with the adapter

```bash
python3 scripts/04_chat.py \
  --adapter outputs/sft/adapter \
  --prompt "What is 7 * 6?"
```

Base model only (no LoRA):

```bash
python3 scripts/04_chat.py --adapter "" --prompt "Say hello in one short sentence."
```

## 4) Holdout eval (do this after SFT)

Eval answers: *did the adapter change answers on prompts it never trained on?*

```bash
# Generates predictions for data/sft_eval.jsonl and writes exact_match
python3 scripts/05_eval_holdout.py --adapter outputs/sft/adapter
# → outputs/eval/holdout_preds.jsonl
# → outputs/eval/metrics.json
```

Read `exact_match` in `metrics.json`:

| Reading | Meaning |
|---------|---------|
| Goes up vs base | Intended gain — data moved behavior |
| Flat | Bad/too-little data, or pipeline bug — fix data before bigger models |
| Other skills drop | Early forgetting signal — escalate to SFP only if that is the research question |

Compare base vs LoRA:

```bash
python3 scripts/05_eval_holdout.py --adapter "" --metrics-out outputs/eval/metrics_base.json
python3 scripts/05_eval_holdout.py --adapter outputs/sft/adapter --metrics-out outputs/eval/metrics_lora.json
```

Or score an existing predictions file:

```bash
python3 -m utils.eval --predictions outputs/eval/holdout_preds.jsonl
```

## 5) Optional next stages

```bash
# Preference tuning (needs data/dpo_train.jsonl + dpo.enabled: true)
python3 scripts/02_dpo.py --config configs/base.yaml

# RL is scaffold only today
python3 scripts/03_rl.py --config configs/base.yaml
```

## MacBook tips

| Setting | Recommendation |
|---------|----------------|
| `device` | `auto` (picks `mps`) |
| First model | keep `Qwen2.5-0.5B-Instruct` |
| RAM | close browsers if swapping; 1.5B needs more headroom |
| dtype | leave `auto` (`float16` on MPS) |
| Hub | `huggingface-cli login` if downloads throttle |

## Your own data

Edit JSONL (one object per line):

```json
{"instruction": "…", "response": "…"}
```

Point `data.sft_train` / `data.sft_eval` in `configs/base.yaml`. Keep eval out of train.

## Verified smoke (CPU)

On a 4-vCPU Linux host (no GPU):

- Installed CPU torch + requirements
- `01_sft.py` completed a short step budget
- Adapter saved to `outputs/sft/adapter`
- Chat smoke: `7 * 6` → `42`

Same commands work on Mac with MPS.
