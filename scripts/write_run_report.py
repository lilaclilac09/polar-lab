#!/usr/bin/env python3
"""Write logs/LATEST_RUN_REPORT.md from holdout metrics (English)."""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))
OUT = ROOT / "logs" / "LATEST_RUN_REPORT.md"
BASELINE = 0.200


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _device() -> str:
    try:
        from utils.device import resolve_device
        import torch

        d = resolve_device("auto")
        if d == "cuda":
            return f"cuda ({torch.cuda.get_device_name(0)})"
        return d
    except Exception as exc:  # noqa: BLE001
        return f"unknown ({exc})"


def _git_head() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
            .decode()
            .strip()
        )
    except Exception:  # noqa: BLE001
        return "n/a"


def main() -> None:
    lora = _load(ROOT / "outputs" / "eval" / "metrics.json")
    base = _load(ROOT / "outputs" / "eval" / "metrics_base.json")
    lora_em = float(lora.get("exact_match", 0.0) or 0.0)
    base_em = float(base.get("exact_match", 0.0) or 0.0) if base else None
    n = int(lora.get("n", 0) or 0)
    delta = (lora_em - base_em) if base_em is not None else None
    beat_baseline = lora_em > BASELINE
    useful = lora_em >= 0.60
    clear_win = delta is not None and delta >= 0.20

    samples = lora.get("samples") or []
    hits = [s for s in samples if s.get("exact_match")]
    misses = [s for s in samples if not s.get("exact_match")]

    lines = [
        "# Latest local run report",
        "",
        f"Generated: **{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}**  ",
        f"Host: `{platform.node()}` · Python `{platform.python_version()}`  ",
        f"Git: `{_git_head()}` · Device: **{_device()}**",
        "",
        "## Scoreboard",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Holdout n | {n} |",
        f"| LoRA `exact_match` | **{lora_em:.3f}** |",
    ]
    if base_em is not None:
        lines.append(f"| Base `exact_match` | {base_em:.3f} |")
        lines.append(f"| Delta (LoRA − base) | {delta:+.3f} |")
    lines += [
        f"| CPU baseline (2026-07-15) | {BASELINE:.3f} |",
        "",
        "## Gates",
        "",
        f"- Beat CPU baseline (> {BASELINE:.2f}): **{'YES' if beat_baseline else 'NO'}**",
        f"- Useful bar (≥ 0.60): **{'YES' if useful else 'NO'}**",
        f"- Clear win vs base (≥ +0.20): **{'YES' if clear_win else 'NO / n/a'}**",
        "",
        "## Files",
        "",
        "| Artifact | Path |",
        "|----------|------|",
        "| LoRA metrics | `outputs/eval/metrics.json` |",
        "| Base metrics | `outputs/eval/metrics_base.json` |",
        "| Predictions | `outputs/eval/holdout_preds.jsonl` |",
        "| Adapter | `outputs/sft/adapter/` |",
        "| This report | `logs/LATEST_RUN_REPORT.md` |",
        "",
        "## Hits",
        "",
    ]
    if hits:
        for s in hits:
            lines.append(f"- Q: {s.get('prompt')}")
            lines.append(f"  - A: `{s.get('prediction')}`")
    else:
        lines.append("- _(none)_")
    lines += ["", "## Misses", ""]
    if misses:
        for s in misses[:12]:
            lines.append(f"- Q: {s.get('prompt')}")
            lines.append(f"  - pred: `{s.get('prediction')}`")
            lines.append(f"  - gold: `{s.get('gold')}`")
    else:
        lines.append("- _(none)_")
    lines += [
        "",
        "## Next",
        "",
        "1. Copy one row into `logs/week_01.md`.",
        "2. If score is flat, add more short “reply with only …” rows (see `data/README.md`).",
        "3. Re-run: `./run_next.sh`",
        "",
        "Do not commit `outputs/`.",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[report] wrote {OUT}")
    print(
        json.dumps(
            {
                "lora_exact_match": lora_em,
                "base_exact_match": base_em,
                "beat_baseline": beat_baseline,
                "useful": useful,
                "report": str(OUT),
            }
        )
    )


if __name__ == "__main__":
    main()
