#!/usr/bin/env python3
"""RL stage scaffold (PPO / GRPO).

This is intentionally a stub: full online RL needs a reward server, rollout
loop, and usually multi-GPU infra (see VeRL / POLARIS for production-scale math RL).
Here we validate prompts, define a toy reward, and document the hook points.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.config import load_config, resolve_path
from utils.device import resolve_device


def exact_match_reward(completion: str, gold: str) -> float:
    return 1.0 if completion.strip().lower() == gold.strip().lower() else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Polar Lab RL scaffold")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true", help="Opt-in when a trainer is wired")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path if cfg_path.is_file() else ROOT / args.config)
    rl_cfg = cfg.get("rl", {})
    try:
        device = resolve_device(cfg.get("device", "auto"))
    except ImportError:
        device = "unknown (install torch)"
    prompts_path = resolve_path(cfg, cfg["data"]["rl_prompts"])
    out_dir = resolve_path(cfg, cfg["project"]["output_dir"]) / "rl"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with prompts_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # Demonstrate the reward contract on gold == gold (identity smoke).
    demo_scores = [
        {
            "prompt": r.get("prompt"),
            "gold": r.get("gold"),
            "reward_if_perfect": exact_match_reward(str(r.get("gold", "")), str(r.get("gold", ""))),
        }
        for r in rows
    ]
    manifest = {
        "stage": "rl",
        "algo": rl_cfg.get("algo", "grpo"),
        "device": device,
        "reward": rl_cfg.get("reward", "exact_match"),
        "n_prompts": len(rows),
        "status": "scaffold",
        "next_steps": [
            "Plug TRL PPO/GRPO or VeRL trainer here",
            "Replace identity demo with real rollouts",
            "Log mean reward per step to wandb when enabled",
        ],
        "demo_scores": demo_scores,
        "output_dir": str(out_dir),
    }
    (out_dir / "scaffold_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))

    if args.execute:
        raise SystemExit(
            "RL execute path is not wired yet. Use POLARIS/VeRL for multi-node math RL, "
            "or extend this file with TRL GRPOTrainer once rewards + rollouts are ready."
        )


if __name__ == "__main__":
    main()
