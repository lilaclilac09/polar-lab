#!/usr/bin/env python3
"""Chat with base Qwen or a saved LoRA adapter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.config import load_config
from utils.device import resolve_device, resolve_dtype


def main() -> None:
    parser = argparse.ArgumentParser(description="Polar Lab chat / generate")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--adapter", default="outputs/sft/adapter", help="LoRA dir or empty for base")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    args = parser.parse_args()

    import torch
    from peft import PeftModel

    from utils.hub import load_causal_lm, load_tokenizer

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path if cfg_path.is_file() else ROOT / args.config)
    device = resolve_device(cfg.get("device", "auto"))
    dtype = resolve_dtype(cfg.get("dtype", "auto"), device)
    model_name = cfg["model"]["name_or_path"]
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

    messages = [{"role": "user", "content": args.prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Decode only newly generated tokens
    gen = out[0][inputs["input_ids"].shape[-1] :]
    print(tokenizer.decode(gen, skip_special_tokens=True).strip())


if __name__ == "__main__":
    main()
