# Codex CI — enable checklist

Workflow: `.github/workflows/ci.yml`  
Prompt: `.github/codex/prompts/ci-check.md`

## What runs without Codex

On every push/PR to `main`:

1. **hygiene** — `scripts/check_data.py` + fixture `exact_match`
2. **dry-run** — `scripts/01_sft.py --dry-run` (CPU torch)

These are the source of truth.

## What Codex adds

When enabled, a third job runs `openai/codex-action@v1` as an **inspector**:

- Reads `SPEC.md` + `CLAUDE.md`
- Re-runs the same lightweight gates
- Reviews the diff for SPEC violations
- Must paste full Python tracebacks on failure

Codex does **not** download large models or run full SFT.

## Enable (GitHub UI)

1. Open https://github.com/lilaclilac09/polar-lab/settings/secrets/actions  
2. **New repository secret** → name `OPENAI_API_KEY` → paste key → Save  
3. Open https://github.com/lilaclilac09/polar-lab/settings/variables/actions  
4. **New repository variable** → name `ENABLE_CODEX_CI` → value `true` → Save  
5. Actions → **ci** → Run workflow, or push any commit  

## Disable

- Set variable `ENABLE_CODEX_CI` to `false`, or delete it.

## Verify

| Check | Expected |
|-------|----------|
| Actions tab | Workflow `ci` on latest commit |
| Jobs | hygiene + dry-run always; `codex inspector` only if variable true |
| Codex log | Mentions SPEC/CLAUDE; gate pass/fail; `PASS` or `FAIL` verdict |

## Cost / safety notes

- Uses your OpenAI quota via `OPENAI_API_KEY`
- `safety-strategy: drop-sudo`, permission profile `:workspace`
- Restrict who can run Actions if the repo is public
