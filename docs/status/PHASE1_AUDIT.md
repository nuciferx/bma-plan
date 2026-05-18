# BMA-Plan Phase 1 Audit

> Updated: 2026-05-06 10:19 +07:00
> Scope: Phase 1 = Raster PDF Measurement Assistant / Mini-CAD for Area Measurement

## Scope Gate

Phase 1 remains measurement-only:

- No legal checker
- No FAR/OSR pass/fail
- No Rule Engine
- No AI/OCR/auto boundary detection
- No K.1 generation
- No assumption that real PDFs expose vector geometry

## Current Baseline

Backend:

- Uses per-case `CASES[case_id]` instead of global `SESSION`
- Upload checks include size cap, empty file, invalid PDF, and encrypted PDF
- Page, thumbnail, analyse, project, XLSX, and PDF export routes require valid `case_id`
- Render/analyse caches are bounded per case

Frontend:

- PDF canvas workflow supports pan, wheel zoom, page navigation, rotation, manual calibration, area/opening drawing, line/path/reference geometry, parking markers, save/load, and export
- Scale is recalculated from raw geometry through the current page scale
- Raster/no-vector pages fall back to manual measurement mode
- Overlapping picker, layer visibility/lock, loupe, Shift-constrain, orthogonal mode, draw bar, object tree, and selected-object properties are present

## Changes In This Audit Pass

- Converted the visible topbar action from legal-style "check" to a Phase 1 measurement report
- Replaced `openCheckPanel()` output with measurement-only summaries and QA warnings
- Removed the visible legal pass/fail flow from the normal UI
- Removed hardcoded runtime legal rule data from `ui.html`
- Hid advanced land-edge and setback controls from the normal toolbar
- Left low-level helper geometry functions in place to avoid unnecessary regression while they are not exposed as Phase 1 UI
- Added a right panel with layer controls, selected-object properties, object metrics, and a current-page object tree grouped by measurement layer
- Wired object-tree selection to the existing canvas selection/focus flow and reused existing layer visibility/lock state
- Updated E2E expectations so advanced setback controls are hidden and not enabled by default
- Added E2E coverage for right-panel rendering, object-tree selection, and property rename

## AGENT 1 Minimal Sprint Patch - 2026-05-06

- Added object ID normalization for areas, openings, reference lines, dimension/path lines, and parking markers while preserving existing IDs.
- Added opening parent auto-link by containment when an opening is inside exactly one user-drawn closed area on the same page.
- Extended the compact layer system with `reference_geometry` visibility/lock in the right panel; locked references remain visible but are skipped by canvas hit testing, nearest selection, and the overlapping picker.
- Added minimal label mode editing for selected objects: `auto` and `hidden`.
- Upgraded Phase 1 QA warnings to structured records with `id`, `severity`, `page_index`, `object_id`, `message`, and `suggested_action`.
- Added XLSX foundation sheets: `Cover`, `Warnings`, `Page Scales`, and `Audit Log`, while preserving existing report sheets.
- Extended E2E smoke/full coverage for stable IDs, parent-linked openings, structured warnings, reference layer lock, hidden labels, and new XLSX sheets.

## AGENT 2 Review Result - 2026-05-06

- Reviewed `PATCH_SUMMARY.md`, `PATCH.diff`, and the implementation surface for layer lock, overlapping selection, object tree/properties, draw controls, export/UI data consistency, and Phase 1 scope.
- Found no blocking findings.
- Confirmed locked `reference_geometry` remains visible but is unselectable.
- Confirmed overlapping picker behavior, right panel edits, parent-linked opening, label hidden mode, structured warnings, stable IDs, and XLSX audit sheets through smoke/full tests.
- Recorded non-blocking cleanup debt: duplicate legacy helper declarations in `proto/ui.html` are overridden by newer definitions and should be removed in a small follow-up cleanup.

## AGENT 3 Docs + Second Code Check - 2026-05-06

- Updated audit/test/docs artifacts only; no source code changes were made in AGENT 3.
- Re-ran the second scope check against runtime source and found no legal/OCR/AI/rule-engine strings.
- Re-ran `py_compile`, smoke, and full tests after AGENT 2 review; all passed.
- Created `TEST_RESULT.md` and `DOCS_SUMMARY.md` for handoff into AGENT 4.

## Gemini Patch Review

Files reviewed from `F:\My Drive\01 project\ai\bma-plan`:

- `context.txt`
- `patch_sprint2.py`
- `patch_picker.py`
- `patch_hit_test.py`
- `patch_tree.py`
- `patch_props.py`

Decision:

- Did not run the patch scripts because they are string-replace patches targeting older UI structure such as `layerState` and `rp-content`
- Kept the already-present newer implementations for loupe, Shift-constrain, bigger handles, and overlapping picker
- Manually integrated the useful object tree/properties direction from `patch_tree.py` and `patch_props.py` into the current `ui.html`

## Preserved Contracts

- `case_id` isolation: not changed
- Raw geometry recalculation from current scale: preserved
- Export/UI data source: shared through normalized `pageStore`, current scale metadata, and structured warning records
- CAD-like interactions: overlapping picker, zoom, snap, Shift/ortho, layer lock, and draw bar preserved

## Remaining Phase 1 Gaps

- Layer system is still a compact UI mapping, not the full 10-layer model from the Phase 1 context
- Reference lines are closer to first-class objects, but reference arcs/circles are not implemented yet
- Opening auto-link covers unambiguous containment only; manual parent reassignment UI is still future work
- Label modes support `auto` and `hidden`; full manual movable labels and leader lines are still future work
- Object tree is current-page/layer grouped, not a full all-page/floor hierarchy
- Scale record export is a foundation sheet, not yet the full point1/point2/pixels_per_meter/status model from Sprint 3
- `Page Scales` is an export foundation; expand it later if every page from `1..pageCount` must be listed even when no object/scale exists
- `proto/ui.html` has duplicate legacy report/export helper declarations that are overridden by newer definitions; tests pass, but cleanup is recommended
- Curved path and iPad work are later sprints

## Tests

Run on 2026-05-06 during AGENT 3:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

Result:

- `py_compile`: passed
- `smoke`: passed
- `full`: passed
- scope grep for legal/OCR/AI/rule-engine terms: no matches

Key regression points from the run:

- Cache limits and invalid render scale rejection passed
- Vector area, manual recalibration, JSON/CSV/XLSX export, save/load, raster mode, wheel zoom, snap helpers, selection/color/opacity, annotation PDF export, real permit multipage persistence, rotation, and subset export passed
- Advanced setback controls are hidden in Phase 1 and the legacy helper overlay is not enabled by default
- Right panel/object tree selection, property rename, stable IDs, parent-child opening auto-link, structured QA warnings, reference layer lock, label hidden mode, and XLSX audit sheets passed in smoke and full runs
