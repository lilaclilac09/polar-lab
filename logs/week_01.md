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

## Next week

1. Add more policy-style SFT rows or a small DPO set for style control
2. Optional: bump to 1.5B only after holdout behavior is stable
3. Wire `utils.eval` predictions JSONL for a formal exact_match score

## Links

- Outputs (local only): `outputs/`
- Upstream inspiration (math RL): https://github.com/ChenxinAn-fdu/POLARIS
- Forgetting benchmark: https://github.com/paradigmxyz/sfp
