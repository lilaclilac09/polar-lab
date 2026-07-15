#!/usr/bin/env python3
"""DPO stage — preference tuning on top of the base or SFT checkpoint."""

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Polar Lab DPO")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--model", default=None, help="Override model or SFT adapter path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path if cfg_path.is_file() else ROOT / args.config)
    dpo_cfg = cfg.get("dpo", {})
    if not dpo_cfg.get("enabled", False) and not args.dry_run:
        # Allow explicit run even if disabled — print a notice.
        print("Note: dpo.enabled is false in config; running anyway because script was invoked.")

    device = resolve_device(cfg.get("device", "auto"))
    dtype = resolve_dtype(cfg.get("dtype", "auto"), device)
    train_path = resolve_path(cfg, cfg["data"]["dpo_train"])
    out_dir = resolve_path(cfg, cfg["project"]["output_dir"]) / "dpo"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_jsonl(train_path)

    model_name = args.model or cfg["model"]["name_or_path"]
    print(
        json.dumps(
            {
                "stage": "dpo",
                "device": device,
                "model": model_name,
                "train_rows": len(rows),
                "beta": dpo_cfg.get("beta", 0.1),
                "output_dir": str(out_dir),
            },
            indent=2,
        )
    )
    if args.dry_run:
        return

    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOConfig, DPOTrainer

    tokenizer = AutoTokenizer.from_pretrained(
        cfg["model"]["name_or_path"],
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        trust_remote_code=cfg["model"].get("trust_remote_code", True),
    )
    model.to(device)

    lora_cfg = cfg.get("lora", {})
    peft_config = LoraConfig(
        r=int(lora_cfg.get("r", 8)),
        lora_alpha=int(lora_cfg.get("alpha", 16)),
        lora_dropout=float(lora_cfg.get("dropout", 0.05)),
        bias=lora_cfg.get("bias", "none"),
        target_modules=list(lora_cfg.get("target_modules") or ["q_proj", "v_proj"]),
        task_type="CAUSAL_LM",
    )

    # TRL DPO expects prompt / chosen / rejected columns.
    dataset = Dataset.from_list(
        [
            {
                "prompt": r["prompt"],
                "chosen": r["chosen"],
                "rejected": r["rejected"],
            }
            for r in rows
        ]
    )

    train_args = DPOConfig(
        output_dir=str(out_dir),
        num_train_epochs=float(dpo_cfg.get("num_train_epochs", 1)),
        per_device_train_batch_size=int(dpo_cfg.get("per_device_train_batch_size", 1)),
        gradient_accumulation_steps=int(dpo_cfg.get("gradient_accumulation_steps", 4)),
        learning_rate=float(dpo_cfg.get("learning_rate", 5e-6)),
        beta=float(dpo_cfg.get("beta", 0.1)),
        logging_steps=int(dpo_cfg.get("logging_steps", 5)),
        max_steps=int(dpo_cfg.get("max_steps", 20)),
        bf16=dtype == torch.bfloat16,
        fp16=dtype == torch.float16 and device != "cpu",
        report_to=["none"],
        seed=int(cfg.get("project", {}).get("seed", 42)),
    )

    trainer = DPOTrainer(
        model=model,
        args=train_args,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(str(out_dir / "adapter"))
    tokenizer.save_pretrained(str(out_dir / "adapter"))
    print(f"saved adapter → {out_dir / 'adapter'}")


if __name__ == "__main__":
    main()
