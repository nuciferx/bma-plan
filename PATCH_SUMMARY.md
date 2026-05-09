# PATCH_SUMMARY.md - Report Target Summary XLSX

Date: 2026-05-09

## Outcome

PASS

## What Changed

- Added `from collections import defaultdict` import to `proto/server.py`.
- Added new XLSX sheet `สรุปตาม Report Target` to `proto/server.py` (Sheet 7, before `wb.close()`).
  - Collects all objects from all pages grouped by (reportTarget, objectCategory, countingRule).
  - Rows sorted by RT_ORDER: Building Area Summary → Use Category Summary → Open Space Summary → Deduction Summary → Parking Summary → Site Facts → Distance Facts → Height Facts → Audit Log → Unclassified.
  - Columns: Report Target, Object Category, Counting Rule, Pages, Objects, Area (m²), Length (m), Parking.
  - Grand total row at bottom.
  - Unknown reportTarget → "Unclassified".
- Updated E2E sheet name assertion in `proto/e2e_ui_test.py` to include `สรุปตาม Report Target`.

## What Did Not Change

- No `proto/ui.html` changes.
- No save/load format changes.
- No legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail logic.
- No existing XLSX columns removed or reordered.

## Files Touched

- `proto/server.py`
- `proto/e2e_ui_test.py`
- `sprints/active/RUN_REPORT_TARGET_SUMMARY_XLSX.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`

## Known Issues

None.

---

# Previous: Export Metadata Columns XLSX

Date: 2026-05-09

## Outcome

PASS

## What Changed

- Added 5 `SEMANTIC_*_MAP` constants to `proto/server.py`: `SEMANTIC_PROFILE_MAP`, `SEMANTIC_CATEGORY_MAP`, `SEMANTIC_REPORT_TARGET_MAP`, `SEMANTIC_LAW_BASIS_MAP`, `SEMANTIC_COUNTING_RULE_MAP` — exact mirrors of the JavaScript constants in `proto/ui.html`.
- Added `_derive_measurement_meta(tag)` helper to `proto/server.py`: returns all 5 metadata fields from a semanticTag.
- Added `_get_meta(obj, semantic_tag)` helper to `proto/server.py`: reads from object fields first, falls back to derived values.
- Updated 4 XLSX sheets to include the 5 new metadata columns after `useCategory`:
  - `สรุปพื้นที่` — cols 10-14: measurementProfile, objectCategory, reportTarget, lawBasis, countingRule
  - `ความยาวเส้น Polygon` — cols 8-12
  - `ที่จอดรถ` — cols 7-11
  - `ระยะอ้างอิง` — cols 8-12
- Updated title merge_range to span all columns in each updated sheet.
- Added E2E assertion to `_test_opening_and_xlsx_export`: verifies all 5 column headers appear in XLSX shared strings XML.

## What Did Not Change

- No `proto/ui.html` changes (JSON/CSV export was already complete from previous sprint).
- No save/load format changes.
- No legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail logic.
- No new drawing tools, UI redesign, draggable workspace, or autosave engine.
- No existing XLSX columns removed or reordered.

## Files Touched

- `proto/server.py`
- `proto/e2e_ui_test.py`
- `sprints/active/RUN_EXPORT_METADATA_COLUMNS_XLSX.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`

## Known Issues

None. JSON/CSV and XLSX exports are now consistent for the 5 metadata fields.

---

# Previous: Measurement Profile Metadata Foundation

Date: 2026-05-09

## Outcome

PASS

## What Changed

- Added 5 measurement metadata mapping constants to `proto/ui.html`: `SEMANTIC_PROFILE_MAP`, `SEMANTIC_CATEGORY_MAP`, `SEMANTIC_REPORT_TARGET_MAP`, `SEMANTIC_LAW_BASIS_MAP`, `SEMANTIC_COUNTING_RULE_MAP`.
- Added `deriveMeasurementMeta(tag)` helper: returns all 5 metadata fields from a semanticTag.
- Extended `normalizeSemanticFields(obj, type)` to backward-compatibly add all 5 fields to existing objects.
- Updated `rpSetSemanticTag(v)` to also update all 5 derived fields when user changes semanticTag.
- Added read-only display of 5 fields in Properties panel (`.rp-meta-value`, gray italic) below Use Category.
- Added CSS class `.rp-meta-value`.
- Added all 5 fields to measurements JSON/CSV export rows.
- Added E2E assertions: `metaOk`, `metaPanelVisible`, `strippedMetaOk` to SELECT_OK test.

## What Did Not Change

- No server.py changes (XLSX column addition deferred).
- No save/load format breaking changes (additive normalization only).
- No legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail logic.
- No new drawing tools, major UI redesign, draggable workspace, or autosave engine.

## Files Touched

- `proto/ui.html`
- `proto/e2e_ui_test.py`
- `sprints/active/RUN_MEASUREMENT_PROFILE_METADATA_FOUNDATION.md`
- `CURRENT_STATUS.md`, `index.md`, `log.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`

## Known Issues

- XLSX export does not yet include the 5 new columns — next sprint.
- `lawBasis` is null for most object types (by design, only set for area/site objects with known legal basis labels).

---

# Previous: Post-Baseline Workspace Housekeeping

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
