#!/usr/bin/env python3
"""Data hygiene gates for Polar Lab (no torch required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _prompt(row: dict) -> str:
    text = row.get("instruction") or row.get("prompt") or ""
    return str(text).strip()


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{i}: invalid JSON: {exc}") from exc
    return rows


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Polar Lab data hygiene gates")
    parser.add_argument(
        "--train",
        default="data/sft_train.jsonl",
        help="Train JSONL (default: Machina pack)",
    )
    parser.add_argument(
        "--eval",
        default="data/sft_eval.jsonl",
        help="Holdout JSONL (default: Machina pack)",
    )
    parser.add_argument(
        "--dpo",
        default="data/dpo_train.jsonl",
        help="Optional DPO JSONL",
    )
    args = parser.parse_args()

    train_path = Path(args.train)
    if not train_path.is_absolute():
        train_path = ROOT / train_path
    eval_path = Path(args.eval)
    if not eval_path.is_absolute():
        eval_path = ROOT / eval_path
    dpo_path = Path(args.dpo)
    if not dpo_path.is_absolute():
        dpo_path = ROOT / dpo_path

    train = _load_jsonl(train_path)
    held = _load_jsonl(eval_path)
    dpo = _load_jsonl(dpo_path) if dpo_path.is_file() else []

    errors: list[str] = []

    for name, rows, required in (
        (train_path.name, train, ("instruction", "prompt")),
        (eval_path.name, held, ("instruction", "prompt")),
    ):
        for i, row in enumerate(rows, 1):
            if not any(row.get(k) for k in required):
                errors.append(f"{name}:{i}: missing instruction/prompt")
            if not (row.get("response") or row.get("output")):
                errors.append(f"{name}:{i}: missing response/output")

    train_prompts = {_prompt(r) for r in train if _prompt(r)}
    eval_prompts = {_prompt(r) for r in held if _prompt(r)}
    overlap = sorted(train_prompts & eval_prompts)
    if overlap:
        errors.append(f"train/eval prompt overlap ({len(overlap)}): {overlap[:5]!r}")

    empty_train = [i for i, r in enumerate(train, 1) if not _prompt(r)]
    empty_eval = [i for i, r in enumerate(held, 1) if not _prompt(r)]
    if empty_train:
        errors.append(f"sft_train empty prompts at rows {empty_train[:5]}")
    if empty_eval:
        errors.append(f"sft_eval empty prompts at rows {empty_eval[:5]}")

    for i, row in enumerate(dpo, 1):
        for key in ("prompt", "chosen", "rejected"):
            if not row.get(key):
                errors.append(f"dpo_train:{i}: missing {key}")

    report = {
        "train_rows": len(train),
        "eval_rows": len(held),
        "dpo_rows": len(dpo),
        "overlap": len(overlap),
        "ok": not errors,
    }
    print(json.dumps(report))
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
