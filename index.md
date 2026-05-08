# BMA-Plan - Project Index

> Updated: 2026-05-08 00:45 +07:00  
> Current phase: **Phase 1 = Raster PDF Measurement Assistant / Mini-CAD for Area Measurement**

## Current Latest Status

- Latest pipeline: **Rollback UI Pack 1 + Targeted Toolbar Fix**
- Result: PASS
- Direct Open PDF / Open Project / sample PDF restored in the header
- UI Pack 1 Open dropdown neutralized
- Export remains visible and unchanged
- Area toolbar click now activates normal room/sub_area drawing directly
- Land toolbar click now activates land/base_area drawing directly
- Opening remains direct and does not require a follow-up Area click
- `MAIN_UI_OK` now guards restored direct header/Area/Land toolbar behavior
- More menu remains for secondary tools
- Measurement geometry, layer model, semantic metadata model, save/load, and export endpoints untouched
- `py_compile` / `smoke` / `full`: PASS
- Targeted no-new-tool grep and forbidden scope grep: PASS/no matches

## Phase 1 Scope Warning

Phase 1 is **not**:
- legal checker
- OCR
- AI checker
- Rule Engine
- FAR / OSR / setback law validator
- K.1 generator
- new CAD drawing tool sprint

Phase 1 is only:
- open PDF
- set/verify scale
- draw area and opening
- manage layers and overlapping objects
- edit object properties and semantic metadata
- export auditable measurement data

Real PDFs may be raster/scanned images, so the product must not depend on PDF vector geometry.

## Project Purpose

BMA-Plan is a browser-based Mini-CAD measurement assistant for construction PDFs. It uses a local FastAPI backend and an HTML Canvas UI to render PDF pages, let users calibrate scale, draw measured geometry, manage overlap selection, and export measurement reports.

## Current Status

The prototype is usable for Phase 1 measurement workflows:
- per-case PDF upload/rendering with `case_id`
- wheel zoom and pan
- manual scale calibration and auto-unverified scale display
- polygon area and opening/deduction measurement
- reference lines, distance/path lines, parking markers
- object tree and properties panel
- semantic metadata fields on measurement objects
- layer visibility/lock, including locked layers staying visible but unselectable
- overlapping object picker
- JSON/CSV/XLSX/PDF/PDF+annotations export
- `.bmaplan` save/load
- restored direct top header file actions
- responsive main measurement toolbar with primary tools visible, secondary tools in More menu, and fixed Area/Land direct access

## Latest Completed Sprint

Latest pipeline: **Rollback UI Pack 1 + Targeted Toolbar Fix**

Result:
- direct Open PDF, Open Project, and sample actions are restored
- UI Pack 1 Open dropdown is neutralized
- Export remains prominent and unchanged
- Area direct access resets stale opening/land state and selects room/sub_area mode
- Land direct access resets stale opening state and selects land/base_area mode
- toolbar primary row remains visible at 1440px
- advanced land-edge/setback helpers remain hidden by default
- no new drawing tools or measurement geometry changes
- latest tests passed

Immediately before that:
- UI Pack 1 Header + Toolbar passed but was rolled back/neutralized for usability
- Sprint A Semantic Tag Foundation passed
- approved Measurement Main UI alignment passed
- site sides/orientation UI passed
- Sprint 3A duplicate helper verification passed
- overlapping picker lifecycle and layer lock were verified

## Latest Passing Tests

Latest recorded passing commands:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py smoke
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py full
```

Key confirmations:
- `MAIN_UI_OK`
- `SITE_UI_OK`
- `XLSX_OK`
- `PROJECT_OK`
- `SELECT_OK`
- `EXT_MEASURE_OK`
- `ANNOT_OK`
- `PERSIST_OK`
- `REAL_OK`

Targeted no-new-tool grep and forbidden scope grep found no matches.

## Important Files

| File | Purpose |
|---|---|
| `AGENTS.md` | Agent rules and non-negotiable Phase 1 scope |
| `BMA_PLAN_PHASE1_CONTEXT.md` | Full Phase 1 product/architecture context |
| `index.md` | This project map and current status |
| `CURRENT_STATUS.md` | Short current handoff state |
| `SPRINT_INDEX.md` | Sprint/pipeline history and next sprint options |
| `FILE_STRUCTURE_PLAN.md` | Proposed organization plan; no files moved yet |
| `HOUSEKEEPING_REPORT.md` | Latest housekeeping report |
| `log.md` | Required chronological activity log |
| `PHASE1_AUDIT.md` | Phase 1 audit and remaining gaps |
| `TEST_RESULT.md` | Latest test result artifact |
| `UI_MANUAL_TEST.md` | Latest focused UI/manual notes |
| `proto/server.py` | FastAPI backend/API/render/export/session logic |
| `proto/ui.html` | Canvas frontend and measurement UI |
| `proto/e2e_ui_test.py` | Smoke/full regression tests |
| `proto/requirements.txt` | Runtime/test dependencies |
| `proto/STATUS.md` | Proto-specific handoff/status |

## File Organization Notes

Root currently mixes core docs, sprint artifacts, prompt files, historical files, PDFs, and patch scripts. No files were moved or deleted in this sprint.

## Agent Operating Protocol

`AGENTS.md` requires the `BMA-Plan Agent Operating Loop - GTM Infinite Loop` for every future sprint:
Understanding Condition -> Restoration -> Defect Factors Analysis -> Eliminating Factors of Defect -> Setting Condition -> Condition Kaizen -> Condition Management.

Phase 1 remains usable measurement/output workflow first. Phase 2 legal/building-control skill is manual review support only, not automatic pass/fail.

## Current Sprint Roadmap

### Completed / Verified

- Sprint 1: layer lock, overlapping picker, object tree/properties foundation
- Sprint 2: raster measurement UX, loupe, bigger handles, Shift/ortho, draw bar
- Sprint 3: parent opening auto-link, structured QA warnings, XLSX audit foundation
- Sprint 3A: duplicate helper verification, Page Scales coverage, picker regression preserved
- Sprint A: semantic metadata foundation (`semanticTag`, nullable `useCategory`)
- UI Pack 1: header + toolbar visual/organizational cleanup
- Rollback UI Pack 1 targeted fix: direct header actions restored; Area/Land toolbar access fixed

### Recommended Next Sprint Options

1. **Point-by-point toolbar/workflow defect fixes only if reported**
   - Continue restoration style; avoid broad redesign.

2. **Smart export/report use of semantic metadata**
   - Use the new metadata foundation in reporting without legal conclusions.

3. **Sprint 3B Page Scales audit**
   - Polish scale record reporting toward `point1`, `point2`, `pixels_per_meter`, and `status`.

4. **Manual opening parent reassignment**
   - Add UX to resolve ambiguous/unlinked opening parent relationships.

Do not start legal/OCR/AI/Rule Engine work before Phase 1 measurement stability is complete.
