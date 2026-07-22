# Cafe / SEMIS pack run — 2026-07-22

**Config:** `configs/cafe_sft.yaml`  
**Data:** `data/cafe/` (**554** train / **10** eval after miss boost; was 286)  
**Device:** cpu · **Steps:** 360 · **train_loss ≈ 1.15**

Provenance: washed from fresh `lilaclilac09/aileen_machina_01` Cafe Cursor Shanghai + tools hub / SEMIS / contact panel (2026-07-22).

## Scoreboard

| Metric | Value |
|--------|------:|
| LoRA `exact_match` | **0.700** (7/10) |
| Base `exact_match` | **0.100** (1/10) |
| Delta | **+0.600** |
| Useful bar (≥ 0.60) | **YES** |
| Clear win vs base (≥ +0.20) | **YES** |

Earlier 300-step run on 286 rows scored **0.500** / base **0.100**. Miss boost + drop conflicting `tbc` golds + 360 steps crossed the useful bar.

## Hits (LoRA)

- `https://cursor-cafe.aileena.xyz/`
- `/tools`
- `SEMIS`
- `allowlist`
- `Clear + Sync Checked-in`
- `no`
- `live`

## Misses (final run)

| Gold | Pred | Note |
|------|------|------|
| `Cafe Cursor Shanghai` | `Shanghai Cursor Credits Sale` | paraphrase drift |
| `contact panel` | `contact hub` | near synonym |
| `https://www.semianalysis.com` | `https://www.semianalysis.com/` | **trailing slash** near-miss |

## Mac next

```bash
cd ~/polar-lab && git pull
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
POLAR_CONFIG=configs/cafe_sft.yaml ./run_next.sh
open logs/LATEST_RUN_REPORT.md
```

## Next data knobs

1. More identical short golds for `Cafe Cursor Shanghai` and `contact panel`
2. Optional: strip trailing `/` in eval normalize (not done — keeps exact_match strict)
3. Keep Machina pack as default (`./run_next.sh`)
