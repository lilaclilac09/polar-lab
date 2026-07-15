# Polar Lab

**In one sentence:** LoRA fine-tune [`Qwen/Qwen2.5-0.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) on your own data, then evaluate on holdout prompts to check that the model’s behavior actually changed.

**Owned-weight post-training playground:** SFT (LoRA) → DPO → RL scaffold → eval → chat.

Public repo: [`lilaclilac09/polar-lab`](https://github.com/lilaclilac09/polar-lab)

```text
SFT (LoRA) → DPO → RL (PPO/GRPO stub) → Eval → chat
```

## Fine-tuning in plain English

| Word | Meaning here |
|------|----------------|
| **Base model** | Open weights you can change (`Qwen2.5-0.5B-Instruct`) |
| **Fine-tuning / SFT** | Teach with `(instruction, response)` pairs |
| **LoRA** | Train a small adapter “patch”, not the full model |
| **Holdout / eval** | Score prompts the trainer never saw (`exact_match`) |
| **DPO / RL** | Optional later stages for preference / reward |

Without eval, you only have a vibe. With holdout scores, you have evidence.

## Why

API models (Claude, Codex, Amp, DeepSeek) are great for agents — but you do **not** own those weights. You cannot LoRA them, run DPO on them, or honestly measure “did *our* data change behavior?”

Polar Lab fills that gap on a laptop or single GPU:

1. **Own the weights** — tiny open models so data → behavior → score is visible.
2. **Fail cheap** — short smoke runs first; grow model size only after data and eval hygiene work.
3. **Keep memory separate** — team knowledge stays in files / Postgres; this lab is for gated weight experiments, not dumping Slack into LoRA.
4. **Build habits** — train/holdout split, preference JSONL, exact-match eval, short weekly notes.
5. **Optional bridge to SFP** — when forgetting across sequential fine-tunes matters, take methods to [paradigmxyz/sfp](https://github.com/paradigmxyz/sfp) (or your fork). Do not confuse the two.

**Pitch:** change an open model under control. Memory in files; weights behind a gate.

## What this is / is not

| | |
|--|--|
| **Is** | Local SFT → DPO → RL scaffold → eval → chat on open weights |
| **Is** | MacBook MPS / CUDA / CPU smoke path ([HANDS_ON.md](HANDS_ON.md)) |
| **Is not** | A fork of [POLARIS](https://github.com/ChenxinAn-fdu/POLARIS) (math RL / AIME) |
| **Is not** | [SFP](https://github.com/paradigmxyz/sfp) (continual-FT forgetting benchmark) |
| **Is not** | A replacement for Centaur or a way to “permanently memorize” Slack into a harness |
| **Is not** | Production persona weights — any export needs explicit review |

## When to use it

| Use Polar Lab when… | Example |
|---------------------|---------|
| You need to *see* data → behavior | “If I add 50 FAQ pairs, does the model answer them?” |
| You are practicing LoRA gates | Train/holdout discipline before any weight discussion |
| You want post-training literacy | Learn SFT vs DPO vs eval without a cluster |
| You may later study forgetting | Smoke LoRA here, then take a serious method to **SFP** |
| You only have a laptop / single GPU | 0.5B + short `max_steps` is enough to validate the pipeline |

**Do not** use Polar Lab when the job is:

- answering team questions live → use your agent + file memory stack
- chasing AIME / long-CoT RL at scale → study **POLARIS / VeRL**
- measuring multi-task catastrophic forgetting properly → run **SFP**
- “make the harness permanently remember Slack” → **out of scope**

## Agent / CI contracts

- **[SPEC.md](SPEC.md)** — hard rules (train/holdout, metrics, CI)
- **[CLAUDE.md](CLAUDE.md)** / **[AGENTS.md](AGENTS.md)** — how agents should operate
- CI: `.github/workflows/ci.yml` (data hygiene + fixture eval + SFT dry-run; optional Codex)

## Quick start

Full walkthrough: **[HANDS_ON.md](HANDS_ON.md)**.

```bash
git clone https://github.com/lilaclilac09/polar-lab.git
cd polar-lab

python3 -m venv .venv
source .venv/bin/activate

# NVIDIA GPU (CUDA):
#   pip install torch --index-url https://download.pytorch.org/whl/cu124
#   pip install -r requirements.txt
# Mac (MPS): pip install torch && pip install -r requirements.txt
# CPU Linux: pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt

python scripts/check_data.py
python scripts/01_sft.py --dry-run
python scripts/01_sft.py --config configs/base.yaml
python scripts/04_chat.py --adapter outputs/sft/adapter --prompt "What is 7 * 6?"
python scripts/05_eval_holdout.py --adapter outputs/sft/adapter
# → outputs/eval/holdout_preds.jsonl + outputs/eval/metrics.json (exact_match)
```

`device: auto` in `configs/base.yaml` picks `mps` → `cuda` → `cpu`.  
GPU walkthrough (batch size, OOM, force `device: cuda`): **[HANDS_ON.md](HANDS_ON.md)#gpu-nvidia-cuda**  
Full cloud/local CUDA checklist: **[docs/GPU_RUNBOOK.md](docs/GPU_RUNBOOK.md)**  
Latest experiment report: **[logs/REPORT_2026-07-15.md](logs/REPORT_2026-07-15.md)**

## Data pack (current)

Washed English Q&A from **`lilaclilac09/aileen_machina_01`** (memory stack + Centaur research notes) → `data/sft_*.jsonl`.  
Not a live sync and not a raw dump — see [data/README.md](data/README.md). Original arithmetic smoke set is under `data/demo/`.

## What to adjust (one knob at a time)

Default order: **data → steps → model size → DPO/RL**.

| Knob | Where | Why | When |
|------|--------|-----|------|
| Train / eval JSONL | `data/*.jsonl`, `configs/base.yaml` | Behavior only moves if data moves | Always first |
| `sft.max_steps` / epochs | `configs/base.yaml` | More steps ≠ better on dirty data | After smoke works |
| `model.name_or_path` | `configs/base.yaml` | 0.5B validates plumbing; 1.5B+ needs RAM/VRAM | After data + eval hygiene |
| LoRA `r` / `alpha` | `lora:` | Capacity vs overwrite risk | If under/over-fitting on holdout |
| `device` / `dtype` | top-level config | Stability on MPS/CUDA/CPU | OOM or NaNs |
| DPO JSONL + `dpo.enabled` | data + config | Preference style, not facts | After an SFT baseline |
| RL scaffold | `scripts/03_rl.py` | Needs a **verifiable** reward | Last |

**Rule:** if the holdout score does not move, do **not** jump to a bigger Qwen — fix data or the metric first.

## Eval: what “effect” means

Eval does **not** train. It answers: *did this adapter change answers on held-out prompts the way we intended?*

| Piece | Role |
|-------|------|
| `data/sft_eval.jsonl` | Holdout prompts **never** used in `sft_train` |
| Trainer `eval_loss` during SFT | Rough fit signal — not the product metric |
| `utils/eval.py` | Scores a predictions JSONL (`exact_match` today) |
| `scripts/04_chat.py` | Qualitative spot-check |
| Weekly four numbers | rows, steps, **one** eval score, one failure |

Effects that matter:

1. **Intended gain** — holdout items that match new data improve.
2. **Collateral damage** — unrelated holdout gets worse (early forgetting signal → escalate to SFP if that is the research question).
3. **No change** — pipeline or data is wrong; more steps will not magically help.
4. **Chat-only “feels better”** — not enough; write predictions and score them.

```bash
python3 -m utils.eval --predictions outputs/sft/eval_preds.jsonl
# → outputs/eval/metrics.json  (n + exact_match)
```

Until that number is honest, Polar Lab is a trainer demo — not a learning loop.

## After you train — what next?

1. **Local A/B** — same prompts against your production API model vs this LoRA.
2. **Small personal benchmark** — holdout JSONL with expect/forbid checks.
3. **Optional experimental provider** — serve the adapter OpenAI-compat and opt-in only (do not replace production by default).
4. **Grow only after the gate** — holdout stable → larger base; sequential FT forgetting → SFP.

Never use this lab to replace a memory layer, and never train on raw Slack.

## Pipeline status

| Stage | Script | Status |
|-------|--------|--------|
| Config | `configs/base.yaml` | Ready (MPS / CPU / CUDA) |
| SFT | `scripts/01_sft.py` | Runnable LoRA SFT via TRL |
| DPO | `scripts/02_dpo.py` | Runnable when preference JSONL exists |
| RL | `scripts/03_rl.py` | Stub scaffold (wire reward + trainer later) |
| Chat | `scripts/04_chat.py` | Generate with base or LoRA adapter |
| Holdout eval | `scripts/05_eval_holdout.py` | Predict on `sft_eval` → `exact_match` |
| Data | `scripts/data_gen.py` | Synthetic / template builders |
| Data gate | `scripts/check_data.py` | Parse JSONL + train/eval overlap |
| Eval score | `utils/eval.py` | Score a predictions JSONL |
| Orchestration | `run_all.sh` | Runs stages you enable (`RUN_SFT=1`, …) |

## Layout

```text
polar-lab/                  # clone directory (project name: Polar Lab)
├── README.md
├── HANDS_ON.md
├── requirements.txt
├── run_all.sh
├── configs/base.yaml
├── data/                   # tiny demo JSONL
├── scripts/
│   ├── 01_sft.py
│   ├── 02_dpo.py
│   ├── 03_rl.py
│   ├── 04_chat.py
│   ├── 05_eval_holdout.py
│   ├── check_data.py
│   └── data_gen.py
├── utils/
│   ├── config.py
│   ├── device.py
│   └── eval.py
├── tests/fixtures/         # CI exact_match fixture
├── logs/week_01.md
└── outputs/                # runtime (gitignored)
```

## Weekly report

Copy `logs/week_01.md` each week. Keep it short and factual (English only):

- train / holdout row counts
- steps or epochs
- one eval number
- one failure or surprise

Skip vision-speak (“will beat POLARIS”, “permanent memory”).

## Related projects

| Project | Job |
|---------|-----|
| **This repo (Polar Lab)** | Owned-weight practice: SFT / DPO / eval on a laptop |
| **Centaur** | How the team *uses* agents (rented harnesses) |
| **ReMeLight / centaur-analysis** | Team memory in files + Postgres — not weight updates |
| **SFP** | Does sequential fine-tuning *forget*? |
| **POLARIS** | How to scale *math RL* on strong reasoners |

## Safety / hygiene

- Never train on raw Slack dumps from a memory stack.
- Keep train / holdout JSONL disjoint.
- Gate any weight export that might feed production personas.
- Prefer washed, reviewed training exports only when an explicit LoRA / L6 gate is approved.

## License

Code in this repository is provided as-is for research and personal experimentation. Model weights remain under their upstream licenses (e.g. Qwen).
