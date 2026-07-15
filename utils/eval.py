"""Holdout evaluation helpers + CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def exact_match(pred: str, gold: str) -> bool:
    return pred.strip().lower() == gold.strip().lower()


def score_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"n": 0, "exact_match": 0.0, "samples": []}
    hits = 0
    samples = []
    for row in records:
        pred = str(row.get("prediction") or row.get("output") or "")
        gold = str(row.get("gold") or row.get("response") or row.get("chosen") or "")
        ok = exact_match(pred, gold)
        hits += int(ok)
        samples.append(
            {
                "prompt": row.get("prompt") or row.get("instruction"),
                "prediction": pred,
                "gold": gold,
                "exact_match": ok,
            }
        )
    return {
        "n": len(records),
        "exact_match": hits / len(records),
        "samples": samples[:20],
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Score prediction JSONL")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--predictions", required=True, help="JSONL with prediction + gold")
    parser.add_argument("--out", default=None, help="Write metrics JSON here")
    args = parser.parse_args()

    from utils.config import load_config, resolve_path

    cfg = load_config(args.config)
    pred_path = Path(args.predictions)
    if not pred_path.is_file():
        pred_path = resolve_path(cfg, args.predictions)
    records = load_jsonl(pred_path)
    report = score_records(records)

    reports_dir = resolve_path(cfg, cfg.get("eval", {}).get("reports_dir", "outputs/eval"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else reports_dir / "metrics.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"n": report["n"], "exact_match": report["exact_match"], "out": str(out_path)}))


if __name__ == "__main__":
    main()
