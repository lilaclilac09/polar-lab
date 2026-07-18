# Space-engineering short-fact pack

Washed from [lilaclilac09/space-engineering-skills](https://github.com/lilaclilac09/space-engineering-skills)
(fork of LunCoSim). **Not** raw skill markdown — distilled into short, checkable golds for Polar Lab `exact_match`.

| File | Rows | Role |
|------|-----:|------|
| `sft_train.jsonl` | ~348 | Paraphrases + extra numeric facts |
| `sft_eval.jsonl` | 10 | Holdout (disjoint prompts) |

## Provenance

- Source evals: `skills/*/evals/evals.json` (link budgets, ΔV, eclipse, EPS Wh, lander Mp, FDIR, hazards, …)
- Long report-style expects → **short strings** (e.g. `-132 dBW`, `4.3`, `Safe Mode`)
- Machina pack under `data/sft_*.jsonl` is unchanged; this is a **separate domain**

## Run

```bash
python scripts/check_data.py --train data/space/sft_train.jsonl --eval data/space/sft_eval.jsonl
python scripts/01_sft.py --config configs/space_sft.yaml
python scripts/05_eval_holdout.py --config configs/space_sft.yaml --adapter outputs/sft/adapter --max-new-tokens 48
python scripts/05_eval_holdout.py --config configs/space_sft.yaml --adapter "" --metrics-out outputs/eval/metrics_base.json --max-new-tokens 48
```

Or one-shot (after `run_next.sh` supports config — see docs):

```bash
POLAR_CONFIG=configs/space_sft.yaml ./run_next.sh
```

## Pass bars (same as Machina)

- Useful: holdout `exact_match` ≥ 0.60  
- Clear win: ≥ base + 0.20  
