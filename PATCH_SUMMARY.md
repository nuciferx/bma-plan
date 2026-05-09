# PATCH_SUMMARY.md - Post-Baseline Workspace Housekeeping

Date: 2026-05-09

## Outcome

PASS

## What Changed

- Updated `.gitignore`: added `.claude/`, `opencode.json`, `*.docx`, `*.doc`.
- Moved `bma-plan-mockup-v3.html` → `docs/design/`.
- Moved `bma-plan-mockup.html` → `docs/design/`.
- Moved `humancheck.md` → `docs/process/`.
- Updated `index.md`, `CURRENT_STATUS.md`, `log.md`.

## What Did Not Change

- No source code changes (proto/ui.html, proto/server.py, proto/e2e_ui_test.py, proto/requirements.txt).
- No test changes.
- No data model, save/load, export, or backend changes.
- No new features.

## Files Touched

- `.gitignore`
- `docs/design/bma-plan-mockup-v3.html`
- `docs/design/bma-plan-mockup.html`
- `docs/process/humancheck.md`
- `CURRENT_STATUS.md`, `index.md`, `log.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`

## Known Issues

None.

---

# Previous: Right Panel Organization After Mockup V3

Date: 2026-05-09

## Outcome

PASS

## What Changed

- Organized the existing right panel so `Layers` is the clear first section.
- Replaced the right-panel pseudo-tabs with `Layers / Visibility / Lock` labels focused on layer operations.
- Added visible object counts to each right-panel layer row.
- Kept the existing Properties editor and Object Tree accessible below Layers.
- Marked those lower sections as `Legacy / Compatibility` to avoid presenting them as peer primary right-panel tabs.
- Updated E2E assertions for right-panel section order, layer counts, layer controls, workflow order, left labels, status labels, and forbidden Phase 1 feature wording.

## What Did Not Change

- No backend changes.
- No save/load model changes.
- No export model changes.
- No data migration.
- No full mockup implementation.
- No draggable workspace.
- No full autosave/recovery, full Scale Manager, or copy-scale features.
- No legal/OCR/AI/Rule Engine/FAR/OSR/setback pass-fail work.
- No broad JS rewrite to move the full property editor into the left panel.

## Files Touched

- `proto/ui.html`
- `proto/e2e_ui_test.py`
- `PATCH_SUMMARY.md`
- `TEST_RESULT.md`
- `UI_MANUAL_TEST.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `CURRENT_STATUS.md`
- `index.md`
- `log.md`

## Known Issues

- The right panel still contains existing Properties and Object Tree sections after Layers. This is intentional compatibility, now clearly labeled.
- Moving full object properties into the left `Properties` panel still needs a dedicated sprint because doing it safely would require broader JS behavior work.
- Save state is intentionally neutral/manual; no autosave or recovery engine was implemented.
