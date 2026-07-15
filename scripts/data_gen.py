#!/usr/bin/env python3
"""Lightweight domain data builders for Polar Lab demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.config import load_config, resolve_path


TEMPLATES = {
    "general": [
        ("Summarize the idea of {topic} in one sentence.", "{topic} is a focused technique used to improve a specific model behavior."),
        ("Give one risk of poor {topic} data hygiene.", "Leaky or low-quality {topic} data can teach the wrong behavior and waste compute."),
    ],
    "math": [
        ("What is {a} + {b}?", "{sum}"),
        ("What is {a} * {b}?", "{prod}"),
    ],
    "ops": [
        ("How should agents call an org tool in Centaur?", "Prefer the direct CLI `<tool> --help` / typed commands installed via tool shims."),
        ("Where should API secrets live for Centaur tools?", "Declare them for iron-proxy injection; never bake raw keys into the overlay image."),
    ],
}


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def gen_sft(domain: str, n: int) -> list[dict]:
    rows: list[dict] = []
    if domain == "math":
        for i in range(n):
            a, b = (i % 9) + 1, (i % 7) + 1
            rows.append({"instruction": f"What is {a} + {b}?", "response": str(a + b)})
        return rows
    templates = TEMPLATES.get(domain, TEMPLATES["general"])
    topics = ["LoRA", "DPO", "eval holdouts", "preference data", "reward design"]
    for i in range(n):
        instr_t, resp_t = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        rows.append(
            {
                "instruction": instr_t.format(topic=topic, a=1, b=1, sum=2, prod=1),
                "response": resp_t.format(topic=topic, a=1, b=1, sum=2, prod=1),
            }
        )
    return rows


def gen_dpo(domain: str, n: int) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append(
            {
                "prompt": f"[{domain}] Give safe guidance item #{i + 1}.",
                "chosen": "Prefer verified data, hold out an eval slice, and avoid training on private raw chat.",
                "rejected": "Merge all private logs into training for maximum coverage.",
            }
        )
    return rows


def gen_rl(n: int) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append({"prompt": f"Return the number {i}.", "gold": str(i)})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Polar Lab demo datasets")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--kind", choices=["sft", "dpo", "rl", "all"], default="all")
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--domain", default=None)
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path if cfg_path.is_file() else ROOT / args.config)
    domain = args.domain or cfg.get("data", {}).get("domain", "general")

    written = []
    if args.kind in {"sft", "all"}:
        path = resolve_path(cfg, cfg["data"]["sft_train"])
        # Keep eval file untouched; write a generated train sidecar.
        gen_path = path.with_name("sft_train.generated.jsonl")
        write_jsonl(gen_path, gen_sft(domain, args.n))
        written.append(str(gen_path))
    if args.kind in {"dpo", "all"}:
        path = resolve_path(cfg, cfg["data"]["dpo_train"]).with_name("dpo_train.generated.jsonl")
        write_jsonl(path, gen_dpo(domain, args.n))
        written.append(str(path))
    if args.kind in {"rl", "all"}:
        path = resolve_path(cfg, cfg["data"]["rl_prompts"]).with_name("rl_prompts.generated.jsonl")
        write_jsonl(path, gen_rl(args.n))
        written.append(str(path))

    print(json.dumps({"domain": domain, "written": written}, indent=2))


if __name__ == "__main__":
    main()
