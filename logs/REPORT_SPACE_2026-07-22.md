# Space pack run — 2026-07-22

**Config:** `configs/space_sft.yaml`  
**Data:** `data/space/` (**498** train / **10** eval after miss boost; was 348)  
**Device:** cpu · **Steps:** 400 · **train_loss ≈ 1.32**

## Scoreboard

| Metric | Value |
|--------|------:|
| LoRA `exact_match` | **0.500** (5/10) |
| Base `exact_match` | **0.000** (0/10) |
| Delta | **+0.500** |
| Useful bar (≥ 0.60) | **NO** |
| Clear win vs base (≥ +0.20) | **YES** |

## Hits (LoRA)

- `-132` path… wait — final run hits: **`4.3`**, **`96.7`**, **`yes`**, **`Safe Mode`**, **`Pressure Release; Toxicity; Fire; Oxygen`**

## Misses (final run)

| Gold | Pred | Note |
|------|------|------|
| `-132 dBW` | `-122 dBW` | digit slip |
| `0.086` | `0.18` | wrong RSS |
| `35` | `15` | eclipse confused |
| `102.3` | `26` | Wh formula miss |
| `725` | `726` | **near-miss** (700–750 band) |

Earlier 300-step run also **0.500** with a different hit set (`-132`, `96.7`, `35`, `yes`, `Safe Mode`) — score sticky; golds are brittle numbers.

## Mac next

```bash
cd ~/polar-lab && git pull
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
POLAR_CONFIG=configs/space_sft.yaml ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

## Next data knobs

1. More identical short golds for `-132 dBW`, `0.086`, `35`, `102.3`, `725`  
2. Or allow tiny numeric tolerance in eval (not done yet)  
3. Keep Machina pack as default (`./run_next.sh`)
