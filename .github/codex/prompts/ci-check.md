# Codex CI check — Polar Lab

Follow **SPEC.md**, **CLAUDE.md**, and **TODO.md** strictly. English only.

## Tasks

1. Read `SPEC.md`, `CLAUDE.md`, and `TODO.md` section C (Codex CI).
2. Run deterministic gates (do not skip):
   - `python scripts/check_data.py`
   - `python -m utils.eval --predictions tests/fixtures/eval_predictions.jsonl --out /tmp/polar-metrics.json`
   - Expect fixture `exact_match` ≈ 0.666… (2/3 hits).
3. If any command fails, paste the **full Python traceback / stderr** in your final message. Do not summarize away the error.
4. Review the PR / push diff for SPEC violations:
   - train/eval overlap
   - committing `outputs/`
   - Chinese docs in committed files
   - training on holdout
5. Confirm `run_next.sh` and `docs/NEXT_RUN.md` exist when present in the tree (warn if missing on `main` after merge).
6. Do not start full SFT training or download large models. Dry-run / hygiene only.

## Output

- List pass/fail for each gate.
- Quote errors verbatim on failure.
- End with a short verdict: `PASS` or `FAIL` plus the top issue.
