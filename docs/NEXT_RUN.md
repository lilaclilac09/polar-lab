# Next run — copy this path

Use this the next time you open Polar Lab (GPU, Mac MPS, or CPU).  
Do not improvise file locations; everything below is the canonical path.

---

## 0) Repo & branch

```bash
git clone https://github.com/lilaclilac09/polar-lab.git
cd polar-lab

# Until PR #1 is merged:
git fetch origin cursor/polar-lab-agent-ci-9940
git checkout cursor/polar-lab-agent-ci-9940

# After merge, just use main:
# git checkout main && git pull
```

| What | Path / URL |
|------|------------|
| Repo | https://github.com/lilaclilac09/polar-lab |
| Working branch (now) | `cursor/polar-lab-agent-ci-9940` |
| PR | https://github.com/lilaclilac09/polar-lab/pull/1 |

---

## 1) Read first (English)

| Doc | Path |
|-----|------|
| Day report | `logs/REPORT_2026-07-15.md` |
| GPU / no-4090 runbook | `docs/GPU_RUNBOOK.md` |
| Transformer + caveats | `docs/CONCEPTS_AND_CAVEATS.md` |
| Data provenance | `data/README.md` |
| Spec | `SPEC.md` |

CPU baseline to beat: holdout **`exact_match = 0.200`** (short-fact v2).

---

## 2) Data (do not move)

| Role | Path |
|------|------|
| Train | `data/sft_train.jsonl` |
| Holdout eval | `data/sft_eval.jsonl` |
| DPO (optional later) | `data/dpo_train.jsonl` |
| Old arithmetic demo | `data/demo/sft_train.jsonl`, `data/demo/sft_eval.jsonl` |

Gate:

```bash
python scripts/check_data.py
# expect: "ok": true, "overlap": 0
```

---

## 3) Config

| Role | Path |
|------|------|
| Machina LoRA run (use this) | `configs/machina_sft.yaml` |
| Short smoke defaults | `configs/base.yaml` |

Optional edits inside `configs/machina_sft.yaml` only:

- `device: cuda` (or leave `auto`)
- `sft.per_device_train_batch_size` (try `2` on GPU)
- `sft.max_steps` (120 start)

---

## 4) Environment

### NVIDIA GPU (any small card / cloud T4 — no 4090 needed)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
nvidia-smi
python -c "from utils.device import resolve_device; print(resolve_device('auto'))"
# expect: cuda
```

### Mac (Apple Silicon)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch
pip install -r requirements.txt
# expect resolve_device(auto) → mps
```

### CPU

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

---

## 5) Train → eval (canonical commands)

```bash
python scripts/01_sft.py --dry-run --config configs/machina_sft.yaml
python scripts/01_sft.py --config configs/machina_sft.yaml
```

| Output | Path |
|--------|------|
| LoRA adapter | `outputs/sft/adapter/` |
| Holdout predictions | `outputs/eval/holdout_preds.jsonl` |
| Metrics | `outputs/eval/metrics.json` |

```bash
python scripts/05_eval_holdout.py --adapter outputs/sft/adapter --max-new-tokens 48
python scripts/05_eval_holdout.py --adapter "" --metrics-out outputs/eval/metrics_base.json --max-new-tokens 48
```

Chat spot-check (optional):

```bash
python scripts/04_chat.py --adapter outputs/sft/adapter --prompt "Reply with only the TTL days for Aileena visitor soft memory."
```

---

## 6) Scripts map

| Step | Script |
|------|--------|
| Data hygiene | `scripts/check_data.py` |
| SFT | `scripts/01_sft.py` |
| DPO (later) | `scripts/02_dpo.py` |
| Chat | `scripts/04_chat.py` |
| Holdout benchmark | `scripts/05_eval_holdout.py` |
| Score preds only | `python -m utils.eval --predictions outputs/eval/holdout_preds.jsonl` |

---

## 7) After the run — log here

Append one row to **`logs/week_01.md`**:

```text
| date | device (cuda/mps/cpu + GPU name) | config | steps | train_n | train_loss | eval_loss | exact_match LoRA | exact_match base | notes |
```

Pass bar reminder:

- Useful: LoRA holdout `exact_match` **≥ 0.60**
- Clear win: LoRA **≥ base + 0.20**
- Do **not** commit `outputs/`

---

## 8) Do not

- Mix CPU and CUDA torch wheels in the same venv  
- Train on `data/sft_eval.jsonl`  
- Dump Machina `aileena_second_brain/**` raw into JSONL  
- Jump to 1.5B before short-fact score moves  
- Change the eval set mid-comparison with an old baseline  
