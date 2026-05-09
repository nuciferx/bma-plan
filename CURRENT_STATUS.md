# CURRENT_STATUS.md - BMA-Plan Current Status

Date: 2026-05-09

## One-Line Status

BMA-Plan Phase 1 is a Raster PDF Measurement Assistant with working scale calibration, area/opening drawing, overlapping object selection, layer lock, properties editing, save/load, export foundations, semantic metadata foundation across JSON/CSV/XLSX, a summary-by-reportTarget XLSX sheet, restored direct header/Area/Land toolbar access, an accepted Page/Layer Measurement Model architecture, cleaned project document structure, a locked primary workflow UI, and a right panel that is explicitly Layers-first.

## Latest Implementation State

- Page Scales Audit: PASS
- Report Target Summary XLSX: PASS
- Export Metadata Columns XLSX: PASS
- Measurement Profile Metadata Foundation: PASS
- Right Panel Organization After Mockup V3: PASS
- Mockup V3 Scale + Page Workflow UI: PASS
- Primary workflow order is `Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export`.
- `Set Scale` is visible before `Page Setup` and uses the existing calibration mode.
- `Page Setup` is now the primary visible setup label; internal setup function names remain unchanged for compatibility.
- Left panel labels are `Sheets`, `Objects`, and `Properties`.
- Right panel is explicitly Layers-first with layer counts and visibility/lock controls.
- Existing right-panel Properties/Object Tree remain accessible below Layers as labeled `Legacy / Compatibility` sections.
- Status bar includes `Tool`, `Scale`, `Objects`, `Warnings`, `Layer`, `Save`, and `Page`.
- All runtime objects carry 5 measurement metadata fields: `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule` — derived from `semanticTag` via mapping tables, normalized backward-compatibly.
- Properties panel shows these 5 fields as read-only labels below Semantic Tag / Use Category.
- JSON/CSV export includes the 5 new fields per row.
- XLSX export now includes the 5 new fields as columns in สรุปพื้นที่, ความยาวเส้น Polygon, ที่จอดรถ, and ระยะอ้างอิง sheets.
- XLSX export includes a new sheet `สรุปตาม Report Target` grouping all objects by (reportTarget, objectCategory, countingRule) with area/length/parking totals and a grand total row.
- XLSX Page Scales sheet now has 10 columns: added `scale_state` (derived, mirrors JS scaleState()), `object_count` (objects on page), `needs_attention` (True if objects present and scale unconfirmed).
- server.py SEMANTIC_*_MAP constants and _derive_measurement_meta/_get_meta helpers mirror ui.html mapping tables.
- No full mockup, draggable workspace, full autosave/recovery, full Scale Manager, copy-scale, legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail, or save/load model changes.

## Project Organization Status

- Project Housekeeping V2: PASS
- Post-Baseline Workspace Housekeeping: PASS
- Root folder target: only current status files plus source/docs/sprints/reports/artifacts/sample_projects/archive folders.
- Run prompts moved under `sprints/`.
- Design/process/status docs moved under `docs/`.
- Old reports and handoffs moved under `reports/archive/`.
- Manual test artifacts moved under `artifacts/manual_test/`.
- Real/private `.bmaplan` moved under `archive/user_projects/` and remains ignored by Git.
- PDF references moved under `docs/references/` or `archive/references/` and remain ignored by Git.
- UI mockup HTML references moved under `docs/design/`.
- Root exception: `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` remains in root because current full E2E tests expect that path. It is ignored and must not be committed.
- `.gitignore` updated: `.claude/`, `opencode.json`, `*.docx`, `*.doc` patterns added.

Current development policy:
- no new feature until Git baseline and stabilization are confirmed
- one sprint = one branch = one problem
- source code changes require a dedicated implementation sprint

## Latest Documentation State

- Measurement Profile Metadata Foundation: PASS (implemented in code, not docs-only)
- Page/Layer Measurement Model documentation: PASS
- Architecture file: `docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md`
- Accepted hierarchy: Page -> Layer -> Object Type -> Object Category -> Semantic Tag -> Measurement Profile -> Report Target
- Core rule: do not calculate from layer name
- Layer means workflow/visibility/lock/organization
- Semantic Tag, Measurement Profile, and Report Target define measured meaning and report placement
- Docs-only: no source code, tests, save/load, export, PDF, XLSX, `.bmaplan`, or manual artifact changes

## Latest Verified State

- Export Metadata Columns XLSX: PASS
- XLSX สรุปพื้นที่ / ความยาวเส้น Polygon / ที่จอดรถ / ระยะอ้างอิง sheets have 5 new columns: PASS
- XLSX column headers verified in E2E test shared strings: PASS
- Right Panel Organization After Mockup V3: PASS
- Mockup V3 Scale + Page Workflow UI: PASS
- Direct Open PDF / Open Project / sample PDF remains visible in header: PASS
- Set Scale before Page Setup: PASS
- Page Setup primary workflow label: PASS
- Left panel `Sheets / Objects / Properties`: PASS
- Right panel Layers-first with layer counts before Properties/Object Tree: PASS
- Status bar labels for Scale, Objects, Warnings, Layer, Tool, Save/Page: PASS
- Area/Opening/Land active state still reflects actual mode: PASS
- More menu secondary tools still accessible: PASS
- Advanced land-edge/setback helpers hidden by default: PASS
- `py_compile`, `smoke`, `full`: PASS on 2026-05-09
- Forbidden active UI wording check: no legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail/copy-scale/autosave/debug feature wording visible

## Current Product Scope

Phase 1 remains measurement-only:
- open PDF
- set scale
- draw area
- draw opening/deduction
- calculate gross/opening/net
- select overlapping objects with picker
- edit names/types/colors/opacity/labels and semantic metadata
- export auditable measurement data

Not in scope:
- legal checker
- OCR
- AI checker
- Rule Engine
- K.1 generation
- FAR/OSR/legal setback validation
- new drawing tools such as arc, rectangle, circle, dimension arrows, or callouts

## Runtime Source Files

Do not edit without implementation scope:
- `proto/server.py`
- `proto/ui.html`
- `proto/e2e_ui_test.py`
- `proto/requirements.txt`
- `proto/STATUS.md`

## Agent Operating Method

All future agents must follow `AGENTS.md` section `BMA-Plan Agent Operating Loop - GTM Infinite Loop`:
- understand current condition
- restore broken core workflow first
- identify defect factors
- eliminate root causes with regression guards where possible
- set condition through reports/docs/tests
- improve only within sprint scope
- manage PASS/FAIL, known gaps, and next action

Phase 1 remains usable measurement/output workflow first. Phase 2 legal/building-control skill is manual review support only, not automatic legal pass/fail.

## Latest Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py smoke
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py full
```

Latest result: PASS on 2026-05-09.

## Next Recommended Sprint

Choose one:
- Smart export/report: use `reportTarget` grouping to add a summary-by-report-target sheet to XLSX.
- Dedicated left Properties migration sprint, if desired, to move the full object editor out of the right panel safely.
- Sprint 3B Page Scales audit.
- Manual opening parent reassignment.
- Git baseline commit if a review confirms the current state is stable.
- Smart export/report use of semantic metadata.
- Sprint 3B Page Scales audit.
- Manual opening parent reassignment.

Keep the next sprint narrow and avoid adding legal/OCR/AI/Rule Engine scope.
