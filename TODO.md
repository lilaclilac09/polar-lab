# Polar Lab — TODO

Reports: [REPORT_2026-07-16.md](logs/REPORT_2026-07-16.md) · [REPORT_SPACE_2026-07-22.md](logs/REPORT_SPACE_2026-07-22.md) · [REPORT_CAFE_2026-07-22.md](logs/REPORT_CAFE_2026-07-22.md) · Run: [docs/NEXT_RUN.md](docs/NEXT_RUN.md)

**Status:** Machina **1.000** · Space **0.500** · Cafe/SEMIS **0.700** (useful bar met)

---

## Packs

| Pack | Path | Train/eval | Config | Holdout |
|------|------|------------|--------|---------|
| Machina | `data/sft_*.jsonl` | 450/10 | `machina_sft.yaml` | **1.000** |
| Space | `data/space/` | 498/10 | `space_sft.yaml` | **0.500** |
| Cafe/SEMIS | `data/cafe/` | **554/10** | `cafe_sft.yaml` | **0.700** |

```bash
# Cafe / SEMIS
POLAR_CONFIG=configs/cafe_sft.yaml ./run_next.sh
```

---

## C. Next

- [x] CPU train cafe pack → **0.700** (≥ 0.60)
- [ ] Mac cafe pack confirm (offline HF)
- [ ] Push space number misses toward ≥ 0.60
- [ ] Optional: cafe miss polish (`Cafe Cursor Shanghai`, `contact panel`, trailing `/`)
- [ ] Optional Codex CI secrets

---

## E. Codex CI

- [x] Docs + workflow
- [ ] `OPENAI_API_KEY` + `ENABLE_CODEX_CI=true`
