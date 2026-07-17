# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Readable report: [logs/REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · Run path: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot:** **Mac MPS v4 + CPU v4** both **`exact_match = 1.000`** LoRA vs base **0.200**. Week holdout goal met.

---

## A. Ship / sync

- [x] Merge PR #1–#8 into `main`
- [ ] On Mac (when GitHub reachable): `git pull` to get updated report

---

## B. Mac local run

- [x] First Mac run (36-row) → **0.200**
- [x] Pull v4; HF timeout once; then offline Hub retry
- [x] Mac v4 `./run_next.sh` → LoRA **1.000** / base **0.200** (mps, ~7 min, train_loss ≈ 1.16)
- [x] `train_rows: 450` confirmed
- [ ] When online: `git pull` + open `logs/REPORT_2026-07-16.md`
- [x] Compare vs baseline 0.200 / CPU 1.000 — **matched CPU**

---

## C. Fix what is NOT good (data first)

- [x] Expand short-fact pack to **450** rows
- [x] `max_steps: 400`
- [x] CPU v4 → **1.000**
- [x] Mac v4 → **1.000**
- [x] Target ≥ 0.60 and ≥ base + 0.20
- [x] Do not jump to 1.5B until bar moves (bar moved)

---

## D. Keep what is already good

- [x] Pipeline end-to-end
- [x] Train/eval overlap = 0
- [x] `outputs/` gitignored
- [x] Washed Machina data
- [ ] Never commit `outputs/`

---

## E. Codex CI

- [x] Docs + workflow on `main`
- [ ] Optional: `OPENAI_API_KEY` + `ENABLE_CODEX_CI=true`

---

## F. Done looks like

1. [x] Mac `./run_next.sh` on v4 + local `LATEST_RUN_REPORT.md`  
2. [x] Holdout ≥ 0.60 — **1.000 on Mac and CPU**  
3. [ ] Week log row committed (this PR)  
4. Codex CI optional  
