# Polar Lab — TODO

Reports: [REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · [REPORT_SPACE_2026-07-22.md](logs/REPORT_SPACE_2026-07-22.md) · Run: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status:** Machina **1.000** · Space **0.500** · New **cafe/SEMIS** pack (~286/10) from 2026-07-22 Machina commits — pending train.

---

## Packs

| Pack | Path | Train/eval | Config | Holdout |
|------|------|------------|--------|---------|
| Machina | `data/sft_*.jsonl` | 450/10 | `machina_sft.yaml` | **1.000** |
| Space | `data/space/` | 498/10 | `space_sft.yaml` | **0.500** |
| **Cafe/SEMIS** | `data/cafe/` | **286/10** | `cafe_sft.yaml` | pending |

```bash
# Cafe / SEMIS (new)
POLAR_CONFIG=configs/cafe_sft.yaml ./run_next.sh
```

---

## C. Next

- [ ] CPU/Mac train cafe pack → target ≥ 0.60
- [ ] Push space number misses toward ≥ 0.60
- [ ] Optional Codex CI secrets

---

## E. Codex CI

- [x] Docs + workflow
- [ ] `OPENAI_API_KEY` + `ENABLE_CODEX_CI=true`
