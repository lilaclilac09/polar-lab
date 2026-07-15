# Polar Lab — TODO

Check these off in order. Details: [docs/NEXT_RUN.md](docs/NEXT_RUN.md), [docs/GPU_RUNBOOK.md](docs/GPU_RUNBOOK.md).

## A. Ship the branch

- [ ] Merge PR https://github.com/lilaclilac09/polar-lab/pull/1 into `main`
- [ ] Ensure latest commits are on GitHub (`run_next.sh`, `docs/NEXT_RUN.md` — may need a local `git push` if agent token expired)
- [ ] Confirm root files on `main`: `run_next.sh`, `SPEC.md`, `CLAUDE.md`, `docs/NEXT_RUN.md`

## B. Next training run (your computer / H100 / any GPU / CPU)

- [ ] Clone / pull `main` (or `cursor/polar-lab-agent-ci-9940` if not merged)
- [ ] Run one-shot:
  ```bash
  cd polar-lab
  chmod +x run_next.sh
  ./run_next.sh
  ```
- [ ] Confirm device line prints `cuda` / `mps` / `cpu` as expected
- [ ] Open `outputs/eval/metrics.json` and `outputs/eval/metrics_base.json`
- [ ] Record a row in `logs/week_01.md` (device, steps, exact_match LoRA vs base)
- [ ] Beat CPU baseline **exact_match = 0.200** (useful bar ≥ **0.60**)

Optional:

- [ ] Grow short-fact rows in `data/sft_*.jsonl` if score still flat
- [ ] Only then raise `max_steps` / batch / try 1.5B

## C. Enable Codex CI (GitHub)

Deterministic jobs (`hygiene` + `dry-run`) already run on every push/PR.  
Codex is an **optional inspector** (does not replace those gates).

- [ ] Repo → **Settings → Secrets and variables → Actions → Secrets**  
      Add **`OPENAI_API_KEY`**
- [ ] Repo → **Settings → Secrets and variables → Actions → Variables**  
      Add **`ENABLE_CODEX_CI`** = `true`
- [ ] Push a small commit or re-run Actions on `main` / open a test PR
- [ ] Confirm workflow has three jobs when enabled:
  - `data hygiene + fixture eval`
  - `sft dry-run (CPU deps)`
  - `codex inspector (optional)`
- [ ] Open the Codex job log — it should follow `.github/codex/prompts/ci-check.md`  
      (run `check_data` + fixture eval; quote full Python tracebacks on failure)

Turn off anytime: set `ENABLE_CODEX_CI` to `false` or delete the variable.

## D. Hygiene reminders

- [ ] Do not commit `outputs/`
- [ ] Keep train/eval disjoint (`python scripts/check_data.py`)
- [ ] Keep `centaur-analysis` private if it was made public only for bootstrap
- [ ] Do not dump raw Machina `aileena_second_brain/**` into LoRA JSONL

## Done looks like

1. PR merged, `./run_next.sh` green on your machine  
2. Holdout metrics logged in `logs/week_01.md`  
3. Actions → CI green; Codex job visible when `ENABLE_CODEX_CI=true`  
