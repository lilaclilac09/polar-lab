# Cafe Cursor + SEMIS short-fact pack

Washed **2026-07-22** from fresh `lilaclilac09/aileen_machina_01` commits (Cafe Cursor Shanghai, contact panel, tools hub / SEMIS).

| File | Rows | Role |
|------|-----:|------|
| `sft_train.jsonl` | **554** | Short-gold paraphrases (miss-boosted) |
| `sft_eval.jsonl` | 10 | Holdout (disjoint) |

CPU holdout (2026-07-22): LoRA **0.700** / base **0.100** — see [REPORT_CAFE_2026-07-22.md](../../logs/REPORT_CAFE_2026-07-22.md).

## Provenance (new info)

- Cafe Cursor redeem: `https://cursor-cafe.aileena.xyz/` (EVENT tile on `/tools`)
- Event: **Cafe Cursor Shanghai**; default redeem **allowlist**; door-day **Clear + Sync Checked-in**
- Contact: always-on **contact panel** (no public personal email)
- **SEMIS** = Chip Guess tools hub tag; SemiAnalysis → `https://www.semianalysis.com`
- Privacy: organizer contact hidden; notify via Resend; Special user ↔ `isVolunteer`

Not raw Slack / guest CSV PII.

## Run

```bash
python scripts/check_data.py --train data/cafe/sft_train.jsonl --eval data/cafe/sft_eval.jsonl
POLAR_CONFIG=configs/cafe_sft.yaml ./run_next.sh
```

Machina + space packs unchanged.
