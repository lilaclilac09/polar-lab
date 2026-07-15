# Polar Lab — Specification

**Version:** 0.1  
**Status:** Active  
**Language:** English only in this repository

---

## 1. Purpose

Polar Lab is an **owned-weight post-training playground**:

```text
SFT (LoRA) → DPO → RL scaffold → Eval → chat
```

It exists to make **data → behavior → score** visible on a laptop or single GPU.
It is not a production persona store, not a memory layer, and not POLARIS/SFP.

---

## 2. Hard rules (non-negotiable)

1. **Train / holdout must be disjoint.** No `instruction` (or equivalent prompt text) may appear in both `data/sft_train.jsonl` and `data/sft_eval.jsonl`.
2. **Eval does not train.** Holdout rows are never passed into the SFT/DPO optimizer as training examples.
3. **English-only content** for docs, logs, prompts shipped in this repo.
4. **No raw Slack dumps** as training data. Only washed, reviewed exports when an explicit gate approves.
5. **`outputs/` is local-only** — never commit adapters, checkpoints, or prediction dumps that contain secrets.
6. **Do not claim production readiness** from a smoke run. Exporting weights that might feed personas needs an explicit review gate.

---

## 3. Data contracts

### 3.1 SFT JSONL

Each line is one JSON object:

| Field | Required | Notes |
|-------|----------|-------|
| `instruction` | yes* | User prompt. Alias: `prompt` |
| `response` | yes* | Gold assistant text. Alias: `output` |

\*Scripts accept the aliases above; prefer `instruction` + `response`.

### 3.2 DPO JSONL

| Field | Required |
|-------|----------|
| `prompt` | yes |
| `chosen` | yes |
| `rejected` | yes |

### 3.3 Eval predictions JSONL

Used by `python -m utils.eval`:

| Field | Required | Notes |
|-------|----------|-------|
| `prediction` or `output` | yes | Model answer |
| `gold` or `response` or `chosen` | yes | Expected answer |
| `prompt` or `instruction` | optional | For reports |

**Primary metric:** `exact_match` = case-insensitive strip equality, mean over rows.

---

## 4. Pipeline stages

| Stage | Entry | Success signal |
|-------|-------|----------------|
| Config | `configs/base.yaml` | Loads; `device: auto` resolves |
| SFT | `scripts/01_sft.py` | Adapter under `outputs/sft/adapter` |
| DPO | `scripts/02_dpo.py` | Only when preference JSONL + `dpo.enabled` |
| RL | `scripts/03_rl.py` | Scaffold only until reward is wired |
| Chat | `scripts/04_chat.py` | Spot-check; not a formal score |
| Holdout eval | `scripts/05_eval_holdout.py` | Predict on holdout → `exact_match` |
| Eval score | `python -m utils.eval` | Score an existing predictions JSONL |

Default smoke model: `Qwen/Qwen2.5-0.5B-Instruct`.

---

## 5. CI contract

CI must:

1. Parse all demo JSONL files.
2. Fail if train/eval prompt sets overlap.
3. Score a tiny fixture with `utils.eval` (no GPU required).
4. Optionally run `scripts/01_sft.py --dry-run` (installs deps; no training).

CI must **not** download large checkpoints for full training on every PR unless explicitly opted in.

Optional Codex job may review diffs against this SPEC and `CLAUDE.md`; it is an inspector, not the trainer.

---

## 6. Knob order

Change **one** family at a time:

1. Data (`data/*.jsonl`)
2. Steps / epochs (`sft.max_steps`)
3. Model size (`model.name_or_path`)
4. DPO / RL

If holdout `exact_match` (or honest eval_loss) does not move, do not jump model size.
