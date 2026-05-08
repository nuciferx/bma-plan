# FILE_STRUCTURE_PLAN.md

## Purpose

Explain where each type of BMA-Plan project file should live after Project Housekeeping V2.

The goal is to keep the root folder small, predictable, and safe for Git work while preserving all historical context in organized folders.

## Root Files

Keep only current high-value navigation/status files in root:

- `AGENTS.md`
- `README.md`
- `index.md`
- `CURRENT_STATUS.md`
- `log.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `TEST_RESULT.md`
- `PATCH_SUMMARY.md`
- `UI_MANUAL_TEST.md`
- `.gitignore`
- `.gitmodules`

Root folders:

- `proto/`
- `docs/`
- `sprints/`
- `reports/`
- `artifacts/`
- `sample_projects/`
- `archive/`

Root exception:

- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` may remain in root while `proto/e2e_ui_test.py` expects that exact parent-folder path. It is ignored by Git and must not be staged.

## Source

Runtime source stays in `proto/`.

Do not move or edit without a dedicated implementation sprint:

- `proto/ui.html`
- `proto/server.py`
- `proto/e2e_ui_test.py`
- `proto/requirements.txt`
- `proto/STATUS.md`

Root repo note:

- `proto/` is a nested Git repository/gitlink.
- Housekeeping does not flatten or absorb `proto/.git`.

## Docs

Use `docs/` for durable project knowledge.

### `docs/design/`

Architecture, product scope, model decisions, and design references:

- `PAGE_LAYER_MEASUREMENT_MODEL.md`
- `BMA_PLAN_PHASE1_CONTEXT.md`
- `BMA_PLAN_V2_SCOPE.md`
- `DEVELOPMENT_PLAN.md`
- `idea-cards.md`

### `docs/process/`

Process documents and navigation:

- `FILE_STRUCTURE_PLAN.md`
- `SPRINT_INDEX.md`
- `HOUSEKEEPING_REPORT.md`
- `DOCS_SUMMARY.md`
- `TASK_PACKET.md`
- `REVIEW_RESULT.md`

### `docs/status/`

Durable status/audit docs:

- `PHASE1_AUDIT.md`

### `docs/references/`

Reference files that may be useful but should not be committed if large/generated/private. PDF files remain ignored by `.gitignore`.

## Sprints

Use `sprints/` for run prompts.

### `sprints/active/`

Current or next planned sprint prompts. If unsure whether a sprint is active, put it here and mark `PENDING` in `SPRINT_INDEX.md`.

### `sprints/completed/`

Completed sprint prompts, one folder per sprint:

```text
sprints/completed/YYYY-MM-DD-short-name/RUN_*.md
```

### `sprints/archive/`

Superseded, obsolete, or generic old prompts.

## Reports

Latest report files remain in root for handoff:

- `FINAL_REPORT_FOR_CHATGPT.md`
- `TEST_RESULT.md`
- `PATCH_SUMMARY.md`
- `UI_MANUAL_TEST.md`

Older reports go to:

- `reports/archive/`

`reports/latest/` is reserved for future copied latest report sets if a sprint needs an immutable report snapshot.

## Artifacts

Generated files go under `artifacts/` and are ignored by Git.

- `artifacts/manual_test/` - manual UI screenshots, downloaded XLSX, roundtrip test files
- `artifacts/screenshots/` - loose screenshots
- `artifacts/exports/` - future generated exports

Do not stage artifacts unless explicitly requested.

## Archive

Use `archive/` for useful but non-current material:

- `archive/old_docs/` - old context, assistant notes, legacy source copies, patch scripts
- `archive/old_reports/` - reserved for older report sets
- `archive/old_run_prompts/` - reserved for historical prompts if not represented in `sprints/archive/`
- `archive/references/` - large/private reference PDFs
- `archive/user_projects/` - real/private `.bmaplan` files

## Files That Must Not Be Committed

- PDFs
- XLSX exports
- `.bmaplan` files
- `.bmaplan.pdf` files
- screenshots/artifacts
- secrets
- `.env` files
- credential/token/key files
- generated runtime logs
- `desktop.ini`
