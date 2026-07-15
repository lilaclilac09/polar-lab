# Concepts & caveats (plain English)

For operators who are new to Transformers / fine-tuning.  
Pairs with [REPORT_2026-07-15.md](../logs/REPORT_2026-07-15.md) and [GPU_RUNBOOK.md](GPU_RUNBOOK.md).

---

## 1. What is a Transformer?

A **Transformer** is the neural-network design behind most modern language models (GPT-style models, Qwen, etc.).

In plain terms it:

1. Turns text into numbers (tokens → vectors).
2. Uses **attention** so each token can “look at” other tokens that matter for the next word.
3. Stacks many such layers so the model learns patterns of language and instructions.

**You do not need to implement a Transformer** to use Polar Lab. You only need to know that:

| Term | What it means for you |
|------|------------------------|
| **Base model** | A pretrained Transformer checkpoint (here: `Qwen/Qwen2.5-0.5B-Instruct`) |
| **0.5B** | Roughly 500 million parameters — a small, laptop/GPU-friendly model |
| **Token** | A piece of text the model reads/writes (not always a full word) |
| **Context / KV cache** | How much recent text the model keeps “in mind”; longer = more memory/compute |
| **SFT (fine-tuning)** | Teaching with `(instruction, response)` pairs |
| **LoRA** | Train a small adapter “patch” instead of updating every parameter |
| **Holdout / eval** | Questions the trainer never saw; used to score real change |
| **exact_match** | Prediction equals gold after strip + case-fold (strict but automatic) |

**Polar Lab in one line:** LoRA-fine-tune a small open Transformer on *your* washed data, then prove behavior change with holdout `exact_match`.

Memory (Aileena Markdown / Redis) is **retrieval**. Polar Lab is **weight updates**. Do not confuse the two.

---

## 2. Points to watch (priority order)

### 2.1 Data beats model size

- Keep **train and eval prompts disjoint** (`python scripts/check_data.py`).
- Prefer **short, checkable gold answers** (`Reply with only …`) when you care about `exact_match`.
- Never dump raw Slack or the whole `aileena_second_brain/**` tree into LoRA.
- Wash facts from Machina into JSONL by hand (or a careful export) — see `data/README.md`.

### 2.2 Eval is the scoreboard

- Chat “feels better” is not enough.
- Always compare **base vs LoRA** on the same holdout file.
- Freeze decoding (`temperature=0` / greedy) when scoring.
- CPU baseline (2026-07-15, short-fact v2): **exact_match = 0.200**.
- Suggested GPU “useful” bar: **≥ 0.60** and **≥ base + 0.20**.

### 2.3 Change one knob family at a time

Default order:

1. Data (`data/*.jsonl`)
2. Steps / epochs (`sft.max_steps`)
3. Batch size / LoRA rank (GPU)
4. Model size (only after short-fact holdout moves)

If holdout does not move, **do not** jump to `Qwen2.5-1.5B-Instruct`.

### 2.4 GPU-specific

- Install a **CUDA** PyTorch wheel (`cu124` / `cu121`), not the CPU wheel.
- Confirm `resolve_device("auto") == "cuda"` and watch `nvidia-smi` during training.
- On OOM: batch size `1`, keep gradient accumulation, stay on 0.5B.
- Full checklist: [GPU_RUNBOOK.md](GPU_RUNBOOK.md).

### 2.5 Boundaries

| System | Job |
|--------|-----|
| **Aileena Machina** | Site agent + file/Redis memory (retrieve, don’t invent) |
| **Polar Lab** | Owned-weight SFT / eval playground |
| **Centaur** | Agent runtime to *study* and document — not this repo’s trainer |
| **SFP / POLARIS** | Separate research tracks (forgetting / math RL) |

### 2.6 Hygiene & safety

- English-only committed docs and training rows in this repo.
- Do not commit `outputs/` (adapters, preds).
- A smoke win ≠ production persona weights; export needs an explicit gate.
- Follow `SPEC.md` and `CLAUDE.md` when agents touch the tree.

---

## 3. Minimal mental model of today’s pipeline

```text
washed JSONL (train)
        │
        ▼
 Qwen Transformer + LoRA SFT   ← “fine-tuning”
        │
        ▼
   adapter weights
        │
        ▼
 holdout JSONL (never trained)
        │
        ▼
   exact_match score   ← “benchmark”
```

If the score is flat, fix **data and answer format** first. The Transformer skeleton is already there inside Qwen.

---

## 4. Glossary (short)

| Word | One-line gloss |
|------|----------------|
| Pretraining | Expensive general training done by the model vendor |
| Post-training | Your SFT / DPO / RL stages after you download weights |
| Adapter | LoRA files under `outputs/sft/adapter` |
| Generalization | Doing well on holdout, not memorizing train rows |
| Overfit | Great on train, weak on holdout |
| Hallucination | Fluent but wrong (common when data is tiny) |
