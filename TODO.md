# Polar Lab — TODO

Check in order. Analysis: [logs/WHY_GOOD_WHY_BAD.md](logs/WHY_GOOD_WHY_BAD.md) · Readable report: [logs/REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · Run path: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status snapshot:** CPU v4 → LoRA **`exact_match = 1.000`** (base 0.200). Mac first run (36-row) = **0.200**. Mac pulled v4 then hit **HF ConnectTimeout**. PR #6 + #7 are on `main` — finish Mac with offline Hub env.

---

## A. Ship / sync

- [x] Merge PR #1–#7 into `main`
- [ ] On Mac: `git pull` (includes v4 + HF fallback)

---

## B. Mac local run

- [x] First Mac `./run_next.sh` on **36-row** pack → LoRA = base **0.200** (mps OK)
- [x] Pull v4 (`train_rows: 450`) — then HF tokenizer timeout
- [ ] Finish v4 with offline cache (or retry Hub):

```bash
cd ~/polar-lab
git checkout main && git pull
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

- [ ] Confirm device `mps` + `train_rows: 450`
- [ ] Log row in `logs/week_01.md`
- [ ] Compare vs CPU v4 **1.000** / old baseline **0.200**

---

## C. Fix what is NOT good (data first)

- [x] Expand short-fact paraphrases (train **36 → 79 → 450**)
- [x] Align eval prompts to ask for short answers (still disjoint)
- [x] Bump `configs/machina_sft.yaml` to `max_steps: 400`
- [x] CPU retrain + holdout on v4 → **`exact_match = 1.000`**
- [ ] Mac / GPU confirm on v4
- [x] Target ≥ 0.60 and ≥ base + 0.20 (hit on CPU)
- [x] Do not jump to 1.5B until bar moves (bar moved)

---

## D. Keep what is already good

- [x] Pipeline: data → LoRA SFT → holdout eval
- [x] Train/eval overlap = 0
- [x] `outputs/` gitignored
- [x] Washed Machina data (not raw Slack)
- [ ] Each Mac run: `python scripts/check_data.py` after data edits
- [ ] Never commit `outputs/`

---

## E. Codex CI

Docs: [docs/CODEX_CI.md](docs/CODEX_CI.md)

- [x] Workflow + prompt on `main`
- [x] Enable checklist documented
- [ ] You: secret **`OPENAI_API_KEY`**
- [ ] You: variable **`ENABLE_CODEX_CI`** = `true`
- [ ] Confirm Actions: hygiene + dry-run + `codex inspector`

---

## F. Done looks like

1. Mac `./run_next.sh` on **v4** + report  
2. Week log updated  
3. Holdout ≥ 0.60 — **CPU already 1.000**  
4. Codex CI optional  
