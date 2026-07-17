# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Report: [logs/REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · Run: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot:** Machina v4 (CPU+Mac) **`exact_match = 1.000`**. New separate domain: **space-engineering** short-fact pack (`data/space/` ~348 train / 10 eval) via `configs/space_sft.yaml`.

---

## A. Ship / sync

- [x] Merge PR #1–#9 into `main`
- [ ] Merge space pack PR; on Mac: `git pull`

---

## B. Mac local run

- [x] Machina v4 → LoRA **1.000** / base **0.200**
- [ ] Optional — train space pack:

```bash
cd ~/polar-lab && git pull
POLAR_CONFIG=configs/space_sft.yaml ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

---

## C. Domains / data

- [x] Machina short-fact v4 (450/10)
- [x] Wash space-engineering-skills evals → `data/space/` (disjoint, short golds)
- [ ] Holdout on space pack ≥ 0.60 (CPU or Mac)
- [ ] Do not mix space + Machina into one JSONL unless intentional

---

## D. Hygiene

- [x] `scripts/check_data.py --train … --eval …`
- [x] Machina + space overlap = 0
- [ ] Never commit `outputs/`

---

## E. Codex CI

Docs: [docs/CODEX_CI.md](docs/CODEX_CI.md)

- [x] Workflow + prompt on `main`
- [ ] Optional: secret `OPENAI_API_KEY` + variable `ENABLE_CODEX_CI=true`
