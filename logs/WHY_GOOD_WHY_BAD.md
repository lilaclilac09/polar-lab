# Why this is good / why this is not good

**Date:** 2026-07-16 (analysis of CPU runs from 2026-07-15)  
**Repo:** https://github.com/lilaclilac09/polar-lab  
**Final holdout:** `exact_match = 0.200` (2/10) on Machina short-fact pack  
**Compare:** arithmetic demo earlier hit `0.667` (2/3)

This note explains **what worked**, **what failed**, and **why** — so a Mac/GPU re-run knows what to fix.

---

## 1. Bottom line

| Area | Verdict | Why |
|------|---------|-----|
| Training **pipeline** | **Good** | Data → LoRA SFT → holdout eval runs end-to-end; loss falls |
| Arithmetic **smoke** | **Good** | Short numeric answers moved (`7*6`→`42`, holdout 0.667) |
| Machina/Centaur **facts** | **Not good yet** | Strict string match mostly fails; model paraphrases or invents |
| Eval **honesty** | **Good** | Flat score is a real signal, not a silent fake win |
| Data **volume / format** | **Not good enough** | ~36 train rows; many golds are brittle paths/names |

**Polar Lab is doing its job:** it showed that the loop works, and that current domain data is too weak for `exact_match`.

---

## 2. What is good (and why)

### 2.1 The loop is real

We can:

1. Wash JSONL (`data/sft_train.jsonl` / `sft_eval.jsonl`)
2. LoRA-tune `Qwen2.5-0.5B-Instruct`
3. Score never-seen prompts with `scripts/05_eval_holdout.py`

`train_loss` fell (e.g. ~4.1 → ~2.3 across Machina runs). That means the adapter is fitting *something*.

**Why that matters:** if the plumbing were broken, loss would not move and chat/eval would crash. They did not.

### 2.2 Disjoint holdout (hygiene)

`scripts/check_data.py` reported **overlap = 0**. Eval rows were not trained on.

**Why good:** a high score under leakage would be fake. A low honest score is more useful than a high dirty one.

### 2.3 Arithmetic demo proved “short answers can stick”

On the tiny demo pack, holdout `exact_match` reached **0.667**. Chat showed base verbose vs LoRA short `42`.

**Why good:** same model, same LoRA method — so the method can change behavior when the target is **simple and repeated**.

### 2.4 Hits on the Machina holdout (2/10)

| Prompt type | Pred | Gold | Why it hit |
|-------------|------|------|------------|
| LoRA replace Markdown? yes/no | `no` | `no` | Binary choice; train had similar “no” rows |
| Centaur default MCP? yes/no | `no` | `no` | Same pattern — short closed-set answer |

**Why these are good:** closed yes/no questions match how small models learn fastest under tiny data.

### 2.5 Process / docs are good

- Washed Machina facts (not raw Slack dump)
- Clear separation: memory retrieval ≠ weight updates
- CI, SPEC, NEXT_RUN, Mac/GPU paths documented
- Auto report path: `logs/LATEST_RUN_REPORT.md` after `./run_next.sh`

---

## 3. What is not good (and why)

### 3.1 Domain `exact_match` stuck at 0.200

Eight of ten holdout items failed. Examples:

| Gold (wanted) | Model said | Failure mode |
|---------------|------------|--------------|
| `aileena_second_brain/memories/semantic/` | “In the Aileena memory store.” | **Paraphrase** — meaning-ish, string fail |
| `visitor:soft:` | long waffle about visitor IDs | **Ignored “reply with only”** |
| `paradigmxyz/centaur` | wrong org URL (`paradigm-cloud/...`) | **Near-miss hallucination** |
| `NetworkPolicy` | story about ingress controller | **Invented sysadmin story** |
| `90` | `100` | **Wrong numeral** |
| `sandbox pods` | “first two bots…” | **Wrong concept** |
| `AGENTS.md` | `centaur-embed.json` | **Plausible-looking fake filename** |
| `iron-proxy` | `centaur-proxy-egress` | **Made-up adjacent name** |

**Why this is bad for the goal:** the goal is “did *our* facts stick?” Under strict `exact_match`, paraphrases and near-misses count as zero — so the scoreboard says the domain pack did not land.

### 3.2 Why the misses happen (root causes)

1. **Too little data** — dozens of rows cannot pin many brittle identifiers into a 0.5B model.
2. **Gold format is harsh** — paths and exact names leave no room for wording change.
3. **Base model priors are strong** — Qwen still prefers fluent essays over “only the token”.
4. **Train/eval paraphrases differ** — train may teach the fact in one wording; eval asks another; tiny LoRA does not transfer cleanly.
5. **More steps alone did not fix it** — 40 → 120 steps lowered loss but exact_match stayed ~0.125–0.200 → underfitting the *strings*, not “needs infinite steps only”.

### 3.3 What is *not* the problem

- Not “Transformer is broken”
- Not “Mac vs CPU” as the main issue (CPU already ran; Mac MPS uses the same scripts)
- Not “eval script lying” — predictions clearly show paraphrase/hallucination
- Not “must have 4090 / H100” to *learn the loop* (GPU helps speed/scale later)

---

## 4. Good vs bad at a glance

```text
GOOD                          NOT GOOD (yet)
─────────────────────────     ─────────────────────────────
Pipeline runs                 Domain exact_match 0.20
Loss decreases                Paths / names / TTL wrong
Yes/no questions stick        Long fluent wrong answers
Demo arithmetic works         Only ~36 train facts
Honest disjoint eval          Brittle string metric vs paraphrase
Docs + ./run_next.sh          Not enough “reply with only” volume
```

---

## 5. What to do on the Mac run

1. Run `./run_next.sh` → open **`logs/LATEST_RUN_REPORT.md`**.
2. Compare LoRA vs base on the same holdout.
3. If still ~0.2:
   - **Add many more short gold rows** (same fact, varied prompts, identical short answers)
   - Keep yes/no + single-token / single-path answers
   - Do **not** jump to 1.5B first
4. Only after short-fact `exact_match` rises (≥ 0.60 useful bar) increase steps/batch or model size.

---

## 6. One-sentence summary

**Good:** the fine-tuning loop works and yes/no behavior can move.  
**Not good:** with ~36 Machina rows, the model still won’t reliably emit exact paths and names under `exact_match` — because data is too small and golds are too brittle, not because the repo is broken.

---

Action checklist: [TODO.md](../TODO.md)
