# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Run path: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot:** CPU short-fact boost (79 train / 10 eval, 200 steps) still **`exact_match = 0.200`** LoRA = base. Near-misses improved (`visitor:soft:memory`, `paradigm/centaur`) but not exact. Mac run can retry the same pack.

---

## A. Ship / sync

- [x] Merge PR #1–#5 into `main`
- [ ] On Mac: `git pull` latest `main` (includes short-fact boost when this PR merges)

---

## B. Mac local run

- [ ] `git pull` then `./run_next.sh`
- [ ] Open `logs/LATEST_RUN_REPORT.md`
- [ ] Confirm device `mps`
- [ ] Log row in `logs/week_01.md`
- [ ] Compare vs baseline **0.200**

```bash
cd polar-lab
git checkout main && git pull
chmod +x run_next.sh && ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

---

## C. Fix what is NOT good (data first) — in progress

- [x] Expand short-fact paraphrases for miss targets (train **36 → 79**)
- [x] Align eval prompts to ask for short answers (still disjoint)
- [x] Bump `configs/machina_sft.yaml` to `max_steps: 200`
- [x] CPU retrain + holdout (result still **0.200**; near-misses closer)
- [ ] Mac / GPU re-run on this pack (`./run_next.sh`)
- [ ] If still flat: add **more** identical short golds (hundreds), especially:
  - `aileena_second_brain/memories/semantic/`
  - `visitor:soft:`
  - `paradigmxyz/centaur`
  - `NetworkPolicy`, `90`, `AGENTS.md`, `iron-proxy`, `sandbox pods`
- [ ] Target: holdout **≥ 0.60** and **≥ base + 0.20**
- [ ] Do **not** jump to 1.5B until that bar moves

---

## D. Keep what is already good

- [x] Pipeline: data → LoRA SFT → holdout eval
- [x] Train/eval overlap = 0 (`scripts/check_data.py`)
- [x] `outputs/` gitignored (incl. `logs/LATEST_RUN_REPORT.md`)
- [x] Washed Machina data (not raw Slack)
- [ ] Each Mac run: re-run `python scripts/check_data.py` after any data edit
- [ ] Never commit `outputs/`

---

## E. Codex CI

Docs: [docs/CODEX_CI.md](docs/CODEX_CI.md) · Workflow: `.github/workflows/ci.yml`

- [x] Workflow + prompt committed on `main`
- [ ] You: add secret **`OPENAI_API_KEY`**
- [ ] You: add variable **`ENABLE_CODEX_CI`** = `true`
- [ ] Confirm Actions shows: hygiene + dry-run + `codex inspector`
- [ ] Open Codex log — follows `.github/codex/prompts/ci-check.md`

Disable: set `ENABLE_CODEX_CI=false`.

---

## F. Done looks like

1. Mac `./run_next.sh` + `LATEST_RUN_REPORT.md`  
2. Week log updated  
3. Short-fact holdout **≥ 0.60** (or next data edit queued)  
4. Codex CI on only if you want it  
