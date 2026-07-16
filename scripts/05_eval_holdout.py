#!/usr/bin/env python3
"""Generate holdout predictions with a LoRA adapter (or base) and score exact_match."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.config import load_config, resolve_path
from utils.device import resolve_device, resolve_dtype
from utils.eval import load_jsonl, score_records


def _prompt(row: dict) -> str:
    return str(row.get("instruction") or row.get("prompt") or "").strip()


def _gold(row: dict) -> str:
    return str(row.get("response") or row.get("output") or row.get("gold") or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Polar Lab holdout eval")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--adapter", default="outputs/sft/adapter", help="LoRA dir or empty for base")
    parser.add_argument("--eval-data", default=None, help="Override holdout JSONL")
    parser.add_argument("--predictions-out", default="outputs/eval/holdout_preds.jsonl")
    parser.add_argument("--metrics-out", default="outputs/eval/metrics.json")
    parser.add_argument("--max-new-tokens", type=int, default=None)
    args = parser.parse_args()

    import torch
    from peft import PeftModel

    from utils.hub import load_causal_lm, load_tokenizer

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path if cfg_path.is_file() else ROOT / args.config)
    device = resolve_device(cfg.get("device", "auto"))
    dtype = resolve_dtype(cfg.get("dtype", "auto"), device)
    model_name = cfg["model"]["name_or_path"]
    max_new = args.max_new_tokens or int(cfg.get("eval", {}).get("max_new_tokens", 128))

    eval_path = Path(args.eval_data) if args.eval_data else resolve_path(cfg, cfg["data"]["sft_eval"])
    rows = load_jsonl(eval_path)
    if not rows:
        raise SystemExit(f"no eval rows in {eval_path}")

    trust = cfg["model"].get("trust_remote_code", True)
    tokenizer = load_tokenizer(model_name, trust_remote_code=trust)
    model = load_causal_lm(model_name, dtype=dtype, trust_remote_code=trust)

    adapter = Path(args.adapter)
    if not adapter.is_absolute():
        adapter = ROOT / adapter
    if args.adapter and adapter.is_dir():
        model = PeftModel.from_pretrained(model, str(adapter))
        print(f"[loaded adapter] {adapter}", file=sys.stderr)
    else:
        print("[base model only]", file=sys.stderr)

    model.to(device)
    model.eval()

    preds_path = Path(args.predictions_out)
    if not preds_path.is_absolute():
        preds_path = ROOT / preds_path
    preds_path.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    with preds_path.open("w", encoding="utf-8") as out_fh:
        for row in rows:
            prompt = _prompt(row)
            gold = _gold(row)
            messages = [{"role": "user", "content": prompt}]
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(text, return_tensors="pt").to(device)
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=max_new,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )
            gen = out[0][inputs["input_ids"].shape[-1] :]
            prediction = tokenizer.decode(gen, skip_special_tokens=True).strip()
            rec = {
                "instruction": prompt,
                "prediction": prediction,
                "gold": gold,
            }
            records.append(rec)
            out_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"Q: {prompt}\nA: {prediction}\nG: {gold}\n", file=sys.stderr)

    report = score_records(records)
    metrics_path = Path(args.metrics_out)
    if not metrics_path.is_absolute():
        metrics_path = ROOT / metrics_path
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    # Drop bulky samples for the summary file; keep n + exact_match + short samples
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "n": report["n"],
                "exact_match": report["exact_match"],
                "predictions": str(preds_path),
                "metrics": str(metrics_path),
            }
        )
    )


if __name__ == "__main__":
    main()
