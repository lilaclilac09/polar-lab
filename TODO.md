# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Run path: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot (CPU 2026-07-15):** domain holdout `exact_match = 0.200` (2/10). Arithmetic smoke was **good** (0.667); Machina paths/names still **not good**.

---

## A. Ship / sync

- [x] Merge PR https://github.com/lilaclilac09/polar-lab/pull/1 (SPEC / CI / docs)
- [x] Merge PR https://github.com/lilaclilac09/polar-lab/pull/2 (`run_next.sh`, Codex CI docs)
- [x] Merge PR https://github.com/lilaclilac09/polar-lab/pull/3 (`LATEST_RUN_REPORT` writer)
- [ ] Merge PR https://github.com/lilaclilac09/polar-lab/pull/4 (`WHY_GOOD_WHY_BAD.md`)
- [ ] On Mac: `git clone` / `git pull` **main** so you have `run_next.sh` + reports

---

## B. Mac local run (do this next)

- [ ] Clone or update:
  ```bash
  git clone https://github.com/lilaclilac09/polar-lab.git
  cd polar-lab
  # if PR #4 not merged yet:
  # git fetch origin cursor/why-good-why-bad-9940 && git checkout cursor/why-good-why-bad-9940
  ```
- [ ] Run:
  ```bash
  chmod +x run_next.sh
  ./run_next.sh
  ```
- [ ] Confirm device prints **`mps`** (Apple Silicon) or `cpu`
- [ ] Open **`logs/LATEST_RUN_REPORT.md`**
- [ ] Also check `outputs/eval/metrics.json` vs `outputs/eval/metrics_base.json`
- [ ] Read **`logs/WHY_GOOD_WHY_BAD.md`** (why hits vs misses)
- [ ] Append one row to `logs/week_01.md` (device, exact_match LoRA, exact_match base)
- [ ] Compare to CPU baseline **0.200** — note if Mac MPS beat / tied / worse

---

## C. Fix what is NOT good (data first)

From WHY report: yes/no works; paths / TTL / repo names fail under `exact_match`.

- [ ] Add more **short** train rows: `Reply with only …` → identical short gold
  - paths: `aileena_second_brain/memories/semantic/`
  - Redis: `visitor:soft:`
  - repo: `paradigmxyz/centaur`
  - `NetworkPolicy`, `90`, `AGENTS.md`, `iron-proxy`, `sandbox pods`
- [ ] Keep holdout **disjoint** (`python scripts/check_data.py`)
- [ ] Prefer many paraphrased **questions**, same **answer string**
- [ ] Re-run `./run_next.sh` after data edit
- [ ] Target: holdout `exact_match` **≥ 0.60** and **≥ base + 0.20**
- [ ] Do **not** jump to 1.5B until that bar moves

Optional later:

- [ ] Softer metric for long answers (keep `exact_match` for short golds)
- [ ] Raise `max_steps` / batch on MPS or cloud GPU
- [ ] Enable DPO only for style — not for facts

---

## D. Keep what is already good

- [x] Pipeline: data → LoRA SFT → holdout eval
- [x] Train/eval overlap = 0
- [x] Washed Machina data (not raw Slack dump)
- [x] Arithmetic smoke proved short answers can stick
- [ ] On each run: still refuse to commit `outputs/`
- [ ] On each data change: still run `scripts/check_data.py`

---

## E. Codex CI (optional)

- [ ] Secret `OPENAI_API_KEY` (repo Settings → Actions secrets)
- [ ] Variable `ENABLE_CODEX_CI` = `true`
- [ ] Confirm Actions jobs: hygiene + dry-run + `codex inspector`
- [ ] Details: [docs/CODEX_CI.md](docs/CODEX_CI.md)

---

## F. Done looks like

1. Mac `./run_next.sh` finishes; `logs/LATEST_RUN_REPORT.md` exists  
2. Week log updated; you know LoRA vs base vs 0.200 baseline  
3. Short-fact holdout **≥ 0.60** (or a clear next data edit if not)  
4. PR #4 merged; Codex CI on only if you want it  

---

## Quick map

| Goal | Command / file |
|------|----------------|
| Run | `./run_next.sh` |
| See results | `logs/LATEST_RUN_REPORT.md` |
| Why good/bad | `logs/WHY_GOOD_WHY_BAD.md` |
| Fix score | edit `data/sft_train.jsonl` + `data/sft_eval.jsonl` |
| Gate data | `python scripts/check_data.py` |
