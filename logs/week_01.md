# Weekly report — Week 01

## Goals

- [x] Smoke SFT on CPU with Qwen2.5-0.5B-Instruct
- [x] Confirm train / eval JSONL are disjoint
- [ ] Decide whether DPO data is ready (`dpo.enabled`)

## Runs

| Date | Stage | Config | Model | Steps / epochs | Device | Notes |
|------|-------|--------|-------|----------------|--------|-------|
| 2026-07-15 | sft | configs/base.yaml | Qwen2.5-0.5B-Instruct | max_steps=40 | cpu | train_loss≈3.0 → eval_loss≈1.88 |

## Metrics

| Split | Metric | Value | Effect reading |
|-------|--------|-------|----------------|
| sft train | train_loss | ~3.01 | decreasing across steps |
| sft_eval | eval_loss | ~1.88 | lower than early train loss |
| chat spot | `What is 7 * 6?` | `42` | intended gain on math-style item |
| chat spot | raw Slack policy | mixed / verbose | need more preference or clearer SFT rows |

Record four lines: **#train=10**, **#holdout=3**, **steps=40**, **eval_loss≈1.88**.

## Failures / surprises

- Tiny SFT moved arithmetic answers quickly; policy/style prompts still drift — expected at 0.5B + 10 rows.

## Next week

1. Add more policy-style SFT rows or a small DPO set for Slack hygiene
2. Create public GitHub repo and push this tree (no `outputs/` in git)
3. Optional: bump to 1.5B only after holdout behavior is stable

## Links

- Outputs (local only): `outputs/`
- Upstream inspiration (math RL): https://github.com/ChenxinAn-fdu/POLARIS
- Forgetting benchmark: https://github.com/paradigmxyz/sfp
