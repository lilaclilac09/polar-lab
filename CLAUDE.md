# CLAUDE.md — Polar Lab

Instructions for coding agents (Claude, Codex, Cursor, etc.) working in this repo.

## What this project is

**Polar Lab** — owned-weight post-training playground on open models:

```text
SFT (LoRA) → DPO → RL scaffold → Eval → chat
```

Public repo: `lilaclilac09/polar-lab`  
Default smoke model: `Qwen/Qwen2.5-0.5B-Instruct`

Read **[SPEC.md](SPEC.md)** for hard contracts. This file is the operator manual.

## Stack

- Python 3.10+
- `torch`, `transformers`, `peft`, `trl`, `datasets`, `pyyaml`
- No Rust in this tree. Do not add a proxy/harness layer unless explicitly asked.
- Docs and committed logs: **English only**

## Non-negotiable

- Keep `data/sft_train.jsonl` and `data/sft_eval.jsonl` **disjoint** by prompt text.
- Never train on holdout rows.
- Never commit `outputs/` (adapters, caches, metrics with secrets).
- Never paste raw Slack / memory-stack dumps into training JSONL.
- Do not rename this into POLARIS or SFP; link out instead.
- Prefer small diffs. Do not rewrite the training stack “for cleanliness” without a failing test or explicit ask.

## How to run (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
# Mac MPS: pip install torch && pip install -r requirements.txt
# Linux CPU: pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt

python scripts/01_sft.py --dry-run
python scripts/01_sft.py --config configs/base.yaml
python scripts/04_chat.py --adapter outputs/sft/adapter --prompt "What is 7 * 6?"
```

Data hygiene + fixture eval (no GPU):

```bash
python scripts/check_data.py
python -m utils.eval --predictions tests/fixtures/eval_predictions.jsonl --out /tmp/metrics.json
```

Full walkthrough: [HANDS_ON.md](HANDS_ON.md).

## What “eval” means here

1. Holdout lives in `data/sft_eval.jsonl`.
2. Generate predictions (chat script or a small loop) into a predictions JSONL with `prediction` + `gold`.
3. Score: `python -m utils.eval --predictions path.jsonl`
4. Read `exact_match` in the metrics JSON.

Trainer `eval_loss` is a rough fit signal only. Chat “feels better” is not enough.

## When changing code

| Touching | Also update |
|----------|-------------|
| Data schema / metrics | `SPEC.md` |
| How agents should operate | `CLAUDE.md` (this file) |
| User quickstart | `README.md` / `HANDS_ON.md` |
| CI gates | `.github/workflows/ci.yml` |

## CI expectations

- Default CI: data checks + fixture `exact_match` + optional SFT `--dry-run`.
- Codex in CI (if enabled) must follow `SPEC.md` + this file; quote full Python tracebacks on failure.
- Codex is an inspector / optional fixer — not a substitute for deterministic checks.

## Out of scope

- Replacing Centaur / file memory with LoRA
- AIME-scale math RL (see POLARIS)
- Continual-FT forgetting benchmarks (see SFP)
- Shipping persona weights without an explicit export gate
