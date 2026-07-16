#!/usr/bin/env python3
"""LoRA SFT entrypoint — runnable smoke test on MacBook MPS/CPU."""

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


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _to_messages(row: dict) -> dict:
    instruction = row.get("instruction") or row.get("prompt") or ""
    response = row.get("response") or row.get("output") or ""
    return {
        "messages": [
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": response},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Polar Lab SFT (LoRA)")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Load data/config only")
    args = parser.parse_args()

    cfg = load_config(ROOT / args.config if not Path(args.config).is_file() else args.config)
    sft_cfg = cfg.get("sft", {})
    if not sft_cfg.get("enabled", True):
        print("SFT disabled in config; exiting.")
        return

    train_path = resolve_path(cfg, cfg["data"]["sft_train"])
    eval_path = resolve_path(cfg, cfg["data"]["sft_eval"])
    out_dir = resolve_path(cfg, cfg["project"]["output_dir"]) / "sft"
    out_dir.mkdir(parents=True, exist_ok=True)

    train_rows = [_to_messages(r) for r in _read_jsonl(train_path)]
    eval_rows = [_to_messages(r) for r in _read_jsonl(eval_path)]

    try:
        device = resolve_device(cfg.get("device", "auto"))
        dtype = resolve_dtype(cfg.get("dtype", "auto"), device)
        dtype_name = str(dtype).replace("torch.", "")
    except ImportError:
        device, dtype_name = "unknown (install torch)", "unknown"

    print(
        json.dumps(
            {
                "stage": "sft",
                "device": device,
                "dtype": dtype_name,
                "model": cfg["model"]["name_or_path"],
                "train_rows": len(train_rows),
                "eval_rows": len(eval_rows),
                "output_dir": str(out_dir),
            },
            indent=2,
        )
    )
    if args.dry_run:
        return

    device = resolve_device(cfg.get("device", "auto"))
    dtype = resolve_dtype(cfg.get("dtype", "auto"), device)

    from datasets import Dataset
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer

    from utils.hub import load_causal_lm, load_tokenizer

    model_name = cfg["model"]["name_or_path"]
    trust = cfg["model"].get("trust_remote_code", True)
    tokenizer = load_tokenizer(model_name, trust_remote_code=trust)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = load_causal_lm(model_name, dtype=dtype, trust_remote_code=trust)
    model.to(device)

    lora_cfg = cfg.get("lora", {})
    peft_config = None
    if lora_cfg.get("enabled", True):
        peft_config = LoraConfig(
            r=int(lora_cfg.get("r", 8)),
            lora_alpha=int(lora_cfg.get("alpha", 16)),
            lora_dropout=float(lora_cfg.get("dropout", 0.05)),
            bias=lora_cfg.get("bias", "none"),
            target_modules=list(lora_cfg.get("target_modules") or ["q_proj", "v_proj"]),
            task_type="CAUSAL_LM",
        )

    max_steps = int(sft_cfg.get("max_steps", -1))
    train_args = SFTConfig(
        output_dir=str(out_dir),
        num_train_epochs=float(sft_cfg.get("num_train_epochs", 1)),
        per_device_train_batch_size=int(sft_cfg.get("per_device_train_batch_size", 1)),
        gradient_accumulation_steps=int(sft_cfg.get("gradient_accumulation_steps", 4)),
        learning_rate=float(sft_cfg.get("learning_rate", 2e-4)),
        logging_steps=int(sft_cfg.get("logging_steps", 5)),
        save_steps=int(sft_cfg.get("save_steps", 50)),
        eval_strategy="steps" if eval_rows else "no",
        eval_steps=int(sft_cfg.get("eval_steps", 50)) if eval_rows else None,
        warmup_ratio=float(sft_cfg.get("warmup_ratio", 0.03)),
        max_steps=max_steps,
        bf16=dtype == __import__("torch").bfloat16,
        fp16=dtype == __import__("torch").float16 and device != "cpu",
        report_to=["wandb"] if cfg.get("wandb", {}).get("enabled") else ["none"],
        seed=int(cfg.get("project", {}).get("seed", 42)),
        max_length=int(cfg["model"].get("max_seq_length", 512)),
        packing=bool(sft_cfg.get("packing", False)),
    )

    trainer = SFTTrainer(
        model=model,
        args=train_args,
        train_dataset=Dataset.from_list(train_rows),
        eval_dataset=Dataset.from_list(eval_rows) if eval_rows else None,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(str(out_dir / "adapter"))
    tokenizer.save_pretrained(str(out_dir / "adapter"))
    print(f"saved adapter → {out_dir / 'adapter'}")


if __name__ == "__main__":
    main()
