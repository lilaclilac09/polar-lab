# Polar Lab — TODO

Check in order. Reports: [REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · [REPORT_SPACE_2026-07-22.md](logs/REPORT_SPACE_2026-07-22.md) · Run: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status:** Machina v4 = **1.000** (CPU+Mac). Space pack CPU = LoRA **0.500** / base **0.000** (Δ +0.500; useful bar not yet).

---

## A. Ship / sync

- [x] PR #1–#10 on `main` (incl. space pack files)
- [ ] Merge space CPU-run report PR; Mac `git pull`

---

## B. Mac

- [x] Machina v4 → **1.000**
- [ ] Space pack:

```bash
cd ~/polar-lab && git pull
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
POLAR_CONFIG=configs/space_sft.yaml ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

---

## C. Domains

- [x] Machina short-fact v4
- [x] Space wash + CPU run (348→**498** train, 400 steps) → **0.500**
- [ ] Push space holdout ≥ **0.60** (more golds for number misses / optional soft numeric)
- [ ] Keep packs separate unless intentional mix

---

## D. Hygiene

- [x] `check_data.py --train/--eval` · space overlap 0
- [ ] Never commit `outputs/`

---

## E. Codex CI

- [x] Docs + workflow on `main`
- [ ] Optional: `OPENAI_API_KEY` + `ENABLE_CODEX_CI=true`
