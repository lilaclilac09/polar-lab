# Polar Lab data

Training and holdout JSONL for LoRA SFT / DPO. **English only.**

## Provenance (current pack)

| File | Source | Notes |
|------|--------|-------|
| `sft_train.jsonl` | Washed Q&A from `lilaclilac09/aileen_machina_01` (second-brain memory docs + Centaur research note) | Not raw Slack; hand-curated short answers |
| `sft_eval.jsonl` | Same domain, **disjoint** prompts | Never used in SFT training |
| `dpo_train.jsonl` | Preference pairs (memory vs weight dump) | Enable with `dpo.enabled: true` |
| `rl_prompts.jsonl` | Tiny RL scaffold prompts | Optional |
| `demo/` | Original arithmetic/hello smoke set | Kept for regression |

## Schema

SFT line:

```json
{"instruction": "…", "response": "…"}
```

DPO line:

```json
{"prompt": "…", "chosen": "…", "rejected": "…"}
```

## Rules

1. Train and eval prompts must not overlap (`python scripts/check_data.py`).
2. Do not dump `aileena_second_brain/**` or Redis chat logs wholesale into these files.
3. Prefer short, checkable answers when you care about `exact_match`.

## Refresh from Machina

1. Pick facts from Machina Markdown / research notes.
2. Rewrite as short instruction/response pairs (do not paste long essays).
3. Split a few similar-but-different prompts into eval.
4. Run `python scripts/check_data.py`.
