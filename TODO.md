# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Run path: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot:** Short-fact **v4** (450 train / 10 eval, 400 steps) CPU holdout **`exact_match = 1.000`** LoRA vs base **0.200** (Δ +0.800). Mac MPS on old **36-row** pack still **0.200** — pull this PR and re-run.

---

## A. Ship / sync

- [x] Merge PR #1–#5 into `main`
- [ ] On Mac: `git pull` latest `main` (includes short-fact **v4** when this PR merges)

---

## B. Mac local run

- [x] First Mac `./run_next.sh` on **36-row** pack → LoRA = base **0.200** (mps OK, loss fell)
- [ ] After this PR merges: `git pull` then `./run_next.sh` (expect `train_rows: 450`)
- [ ] Open `logs/LATEST_RUN_REPORT.md`
- [ ] Confirm device `mps`
- [ ] Log row in `logs/week_01.md`
- [ ] Compare vs baseline **0.200** / CPU v4 **1.000**

```bash
cd polar-lab
git checkout main && git pull
chmod +x run_next.sh && ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

---

## C. Fix what is NOT good (data first)

- [x] Expand short-fact paraphrases (train **36 → 79 → 450**)
- [x] Align eval prompts to ask for short answers (still disjoint)
- [x] Bump `configs/machina_sft.yaml` to `max_steps: 400`
- [x] Mass identical short golds for miss targets
- [x] CPU retrain + holdout on v4 → **`exact_match = 1.000`** (base 0.200)
- [ ] Mac / GPU re-run on v4 (`./run_next.sh`) to confirm
- [x] Target: holdout **≥ 0.60** and **≥ base + 0.20** (hit on CPU)
- [x] Do **not** jump to 1.5B until that bar moves (bar moved — optional next)

---

## D. Keep what is already good

- [x] Pipeline: data → LoRA SFT → holdout eval
- [x] Train/eval overlap = 0 (`scripts/check_data.py`) — v4 still **0**
- [x] `outputs/` gitignored (incl. `logs/LATEST_RUN_REPORT.md`)
- [x] Washed Machina data (not raw Slack)
- [ ] Each Mac run: re-run `python scripts/check_data.py` after any data edit
- [ ] Never commit `outputs/`

---

## E. Codex CI

Docs: [docs/CODEX_CI.md](docs/CODEX_CI.md) · Workflow: `.github/workflows/ci.yml`

- [x] Workflow + prompt committed on `main`
- [x] Enable checklist documented (secret + variable steps)
- [ ] You: add secret **`OPENAI_API_KEY`**
- [ ] You: add variable **`ENABLE_CODEX_CI`** = `true`
- [ ] Confirm Actions shows: hygiene + dry-run + `codex inspector`
- [ ] Open Codex log — follows `.github/codex/prompts/ci-check.md`

Disable: set `ENABLE_CODEX_CI=false`.

---

## F. Done looks like

1. Mac `./run_next.sh` on **v4** + `LATEST_RUN_REPORT.md`  
2. Week log updated  
3. Short-fact holdout **≥ 0.60** — **CPU v4 hit 1.000**  
4. Codex CI on only if you want it  
