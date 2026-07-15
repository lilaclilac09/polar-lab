# Polar Lab — Day Report (2026-07-15)

## One sentence

LoRA fine-tune `Qwen/Qwen2.5-0.5B-Instruct` on washed Aileena Machina / Centaur facts, then score holdout `exact_match` to see if behavior actually changed.

## What we shipped today

| Item | Status |
|------|--------|
| Initialize `lilaclilac09/polar-lab` from `centaur-analysis` orphan `publish/polar-bear` | Done (on `main`) |
| Rename docs to `polar-lab`; repo renamed on GitHub | Done |
| `SPEC.md` / `CLAUDE.md` / `AGENTS.md` + CI hygiene | On PR `#1` |
| Holdout eval script `scripts/05_eval_holdout.py` | Done |
| GPU (CUDA) docs in `HANDS_ON.md` | Done |
| Machina-washed data pack (`data/sft_*.jsonl`) | Done |
| CPU LoRA smoke + machina training runs | Done |

PR: https://github.com/lilaclilac09/polar-lab/pull/1

## Data

| Pack | Train | Eval | DPO | Source |
|------|------:|-----:|----:|--------|
| demo (archived under `data/demo/`) | 10 | 3 | — | arithmetic / hello smoke |
| machina-wash v1 | 24 | 8 | 5 | washed from `aileen_machina_01` |
| machina-wash v2 (end of day) | **36** | **10** | 5 | + short “reply with only …” facts |

Rules enforced: English-only, train/eval prompt overlap = 0 (`scripts/check_data.py` OK).  
Not a live sync to Machina; not a raw Slack / second_brain dump.

## Training setup

- Model: `Qwen/Qwen2.5-0.5B-Instruct`
- Method: LoRA SFT (`peft` + `trl`)
- Device today: **CPU** (no GPU in this cloud runner)
- Adapter path (local only): `outputs/sft/adapter`

## Runs & metrics

| Run | Config | Steps | Train rows | train_loss | eval_loss | Holdout exact_match |
|-----|--------|------:|-----------:|-----------:|----------:|--------------------:|
| A | `configs/base.yaml` (demo arith) | 40 | 10 | ~2.95 | ~1.78 | 0.667 (2/3) on demo holdout |
| B | `base.yaml` + machina v1 | 40 | 24 | 4.11 | 3.03 | 0.125 (1/8) |
| C | `configs/machina_sft.yaml` (r=16) | 120 | 24 | 2.41 | 1.96 | 0.125 (1/8) |
| D | `machina_sft.yaml` + short-fact v2 | 120 | 36 | 2.35 | 1.64 | **0.200 (2/10)** |

### Holdout reading (Run D)

**Hits (2):** yes/no questions — LoRA vs Markdown memory; Centaur MCP default.  
**Misses (8):** paths (`aileena_second_brain/...`), Redis prefix, `paradigmxyz/centaur`, `NetworkPolicy`, TTL `90`, `AGENTS.md`, `iron-proxy`, warm-pool “sandbox pods” — model still paraphrases or invents.

**Interpretation:** Pipeline works (loss falls; chat/eval scripts run). Domain `exact_match` stays low because 0.5B + ~36 rows is too small for brittle string golds. Arithmetic demo previously proved the loop can move short answers when data is simple.

## What worked

1. End-to-end owned-weight loop: data → LoRA SFT → holdout eval.
2. Clear separation: Machina memory ≠ Polar Lab weights.
3. Agent contracts + CI gates so Codex/Claude follow the same rules.
4. Honest metric: flat `exact_match` is a real signal, not a silent failure.

## What did not work yet

1. Domain fact memorization under strict `exact_match`.
2. Long gold answers punish paraphrase even when direction is right.
3. No GPU run today (CPU only in this environment).

## Recommended next steps (tomorrow+)

1. Grow to **hundreds** of short “reply with only …” pairs before chasing 1.5B.
2. Keep `exact_match` for short golds; optional softer score for long answers.
3. Re-run on **CUDA** with `configs/machina_sft.yaml` (see `HANDS_ON.md#gpu-nvidia-cuda`).
4. Only then consider DPO (`dpo.enabled: true`) for style — not for facts.
5. Merge PR `#1` when ready; keep `centaur-analysis` private.

## Artifacts

| Artifact | Location |
|----------|----------|
| Code / docs | `lilaclilac09/polar-lab` (`main` + PR branch) |
| Day metrics log | `logs/week_01.md` |
| Predictions (local) | `outputs/eval/holdout_preds.jsonl` |
| Metrics (local) | `outputs/eval/metrics.json` |
| Adapter (local, gitignored) | `outputs/sft/adapter` |
