# AGENTS.md

Coding agents working in this repository must follow:

1. **[SPEC.md](SPEC.md)** — hard contracts (data, eval, CI)
2. **[CLAUDE.md](CLAUDE.md)** — how to run and what not to do

One-line project intent:

> LoRA fine-tune `Qwen2.5-0.5B-Instruct` on your own data, then evaluate on holdout prompts to check that behavior actually changed.

Do not invent a Rust middle layer. Prefer deterministic CI gates over model-only judgment.
