# CURRENT_STATUS.md - BMA-Plan Current Status

Date: 2026-05-08 00:45 +07:00

## One-Line Status

BMA-Plan Phase 1 is a Raster PDF Measurement Assistant with working scale calibration, area/opening drawing, overlapping object selection, layer lock, properties editing, save/load, export foundations, semantic metadata foundation, and restored direct header/Area/Land toolbar access.

## Latest Verified State

- Rollback UI Pack 1 + Targeted Toolbar Fix: PASS
- Direct Open PDF / Open Project / sample PDF restored in header: PASS
- UI Pack 1 Open dropdown neutralized: PASS
- Export remains visible and unchanged: PASS
- Area toolbar direct access fixed: PASS
- Land toolbar direct access fixed: PASS
- Area/Opening/Land active state reflects actual mode: PASS
- More menu secondary tools still accessible: PASS
- Advanced land-edge/setback helpers hidden by default: PASS
- `py_compile`, `smoke`, `full`: PASS
- Targeted no-new-tool grep: no matches
- Forbidden scope grep: no law/OCR/AI/Rule Engine/Project PDF Save-Load strings

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

Latest result: PASS.

## Next Recommended Sprint

Choose one:
- Continue UI fixes point-by-point only if a concrete toolbar/workflow defect is reported.
- Smart export/report use of semantic metadata.
- Sprint 3B Page Scales audit.
- Manual opening parent reassignment.

Keep the next sprint narrow and avoid adding legal/OCR/AI/Rule Engine scope.
