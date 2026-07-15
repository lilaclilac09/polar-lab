# Codex CI check — Polar Lab

Follow **SPEC.md** and **CLAUDE.md** strictly. English only.

## Tasks

1. Read `SPEC.md` and `CLAUDE.md`.
2. Run deterministic gates (do not skip):
   - `python scripts/check_data.py`
   - `python -m utils.eval --predictions tests/fixtures/eval_predictions.jsonl --out /tmp/polar-metrics.json`
   - Expect fixture `exact_match` ≈ 0.666… (2/3 hits).
3. If any command fails, paste the **full Python traceback / stderr** in your final message. Do not summarize away the error.
4. Review the PR diff for SPEC violations:
   - train/eval overlap
   - committing `outputs/`
   - Chinese docs in committed files
   - training on holdout
5. Do not start full SFT training or download large models unless the workflow already installed deps and asked for `--dry-run` only.

## Output

- List pass/fail for each gate.
- Quote errors verbatim on failure.
- End with a short verdict: `PASS` or `FAIL` plus the top issue.
