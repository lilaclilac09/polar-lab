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

Reading: loss keeps falling; short-fact pack nudged exact_match 0.125 → 0.200 (both yes/no). Paths / TTL / repo strings still miss. Full write-up: [DAY_REPORT_2026-07-15.md](DAY_REPORT_2026-07-15.md).

## Next week

1. Scale short-fact JSONL toward hundreds before larger models
2. Optional softer metric for long answers; keep exact_match for short golds
3. GPU re-run with `configs/machina_sft.yaml`

## Links

- Outputs (local only): `outputs/`
- Upstream inspiration (math RL): https://github.com/ChenxinAn-fdu/POLARIS
- Forgetting benchmark: https://github.com/paradigmxyz/sfp
