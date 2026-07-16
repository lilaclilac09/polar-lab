# Weekly report — Week 01

## Goals

- [x] Smoke SFT on CPU with Qwen2.5-0.5B-Instruct
- [x] Confirm train / eval JSONL are disjoint
- [ ] Decide whether DPO data is ready (`dpo.enabled`)

## Runs

| Date | Stage | Config | Model | Steps / epochs | Device | Notes |
|------|-------|--------|-------|----------------|--------|-------|
| 2026-07-15 | sft | configs/base.yaml | Qwen2.5-0.5B-Instruct | max_steps=40 | cpu | train_loss 4.67→2.26; final train_loss≈2.95; eval_loss≈1.78 |

## Metrics

| Split | Metric | Value | Effect reading |
|-------|--------|-------|----------------|
| sft train | #rows | 10 | demo JSONL |
| sft_eval | #rows | 3 | holdout disjoint |
| sft train | train_loss (final) | 2.946 | decreasing across steps |
| sft_eval | eval_loss | 1.777 | lower than late train loss |
| chat base | `What is 7 * 6?` | `The result of multiplying 7 and 6 is 42.` | verbose |
| chat LoRA | `What is 7 * 6?` | `42` | intended gain — short answer |
| chat LoRA | `What is 4 + 4?` | `8` | holdout hit |
| chat LoRA | `What is 5 * 5?` | `25` | holdout hit |
| chat LoRA | train/eval separate (policy) | paraphrased, not exact | style not locked yet |
| holdout script | `exact_match` via `05_eval_holdout.py` | **0.667 (2/3)** | arithmetic hits; policy miss |

Four lines: **#train=10**, **#holdout=3**, **steps=40**, **exact_match≈0.67**.

## Failures / surprises

- Tiny SFT moved arithmetic answers quickly (exact short answers on holdout).
- Policy/style prompt still drifts from the gold sentence — expected at 0.5B + 10 rows.

## Data refresh

| Date | Pack | Train / eval / dpo | Source |
|------|------|--------------------|--------|
| 2026-07-15 | machina-wash v1 | 24 / 8 / 5 | Washed from `aileen_machina_01` memory + Centaur notes (`data/README.md`) |

## Machina-wash SFT runs

| Date | Config | Steps | Device | train_rows | train_loss | eval_loss | holdout exact_match |
|------|--------|-------|--------|------------|------------|-----------|---------------------|
| 2026-07-15 | `configs/base.yaml` | 40 | cpu | 24 | 4.11 | 3.03 | **0.125** (1/8) |
| 2026-07-15 | `configs/machina_sft.yaml` (r=16) | 120 | cpu | 24 | 2.41 | 1.96 | **0.125** (1/8) |
| 2026-07-15 | `machina_sft.yaml` + short-fact v2 | 120 | cpu | 36 | 2.35 | 1.64 | **0.200** (2/10) |
| 2026-07-16 | `machina_sft.yaml` short-fact v3 (79 rows) | 200 | cpu | 79 | 1.81 | 1.17 | **0.200** (2/10); base also 0.200; near-misses closer |
| 2026-07-16 | `machina_sft.yaml` short-fact v4 (450 rows) | 400 | cpu | 450 | _(pending)_ | _(pending)_ | _(pending CPU retrain)_ |

Reading: v3 loss fell but exact_match stuck at 0.200. **v4** adds ~371 identical short-gold paraphrases (450 train / 10 eval, overlap 0) and bumps `max_steps` to 400. See [TODO.md](../TODO.md).

## Next week

1. Finish v4 CPU holdout; if still flat, Mac/GPU retry same pack
2. Optional softer metric for long answers; keep exact_match for short golds
3. Enable Codex CI only if you set `OPENAI_API_KEY` + `ENABLE_CODEX_CI`

## Links

- Outputs (local only): `outputs/`
- Upstream inspiration (math RL): https://github.com/ChenxinAn-fdu/POLARIS
- Forgetting benchmark: https://github.com/paradigmxyz/sfp
