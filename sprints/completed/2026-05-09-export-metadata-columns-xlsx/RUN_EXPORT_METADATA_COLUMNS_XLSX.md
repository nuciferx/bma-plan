# RUN_EXPORT_METADATA_COLUMNS_XLSX.md

## 0. Sprint Identity

Sprint Name: Export Metadata Columns XLSX
Sprint Type: Implementation / Export Extension
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits e736491 (proto) / f79df59 (root).

Existing state:
- JSON/CSV export already includes all 5 measurement metadata fields: `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`
- XLSX export does NOT include these 5 fields — gap left from previous sprint

XLSX export sheets in server.py:
- Cover (no per-object rows)
- Warnings (no per-object rows)
- Page Scales (no per-object rows)
- Site Facts (per-object rows, no metadata columns)
- Audit Log (no per-object rows)
- สรุปพื้นที่ — has `semanticTag`, `useCategory` at cols 8,9 → need 5 new cols at 10-14
- ความยาวเส้น Polygon — has `semanticTag`, `useCategory` at cols 6,7 → need 5 new cols at 8-12
- สรุปตามชั้น (aggregate only)
- สรุปตามประเภท (aggregate only)
- ที่จอดรถ — has `semanticTag`, `useCategory` at cols 5,6 → need 5 new cols at 7-11
- ระยะอ้างอิง — has `semanticTag`, `useCategory` at cols 6,7 → need 5 new cols at 8-12

---

## 2. Goal

Add 5 measurement metadata columns to XLSX export sheets that have per-object rows.
XLSX output becomes consistent with JSON/CSV measurement export.

---

## 3. Approach

- Add `SEMANTIC_*_MAP` constants to server.py mirroring ui.html JavaScript maps exactly
- Add `_derive_measurement_meta(tag)` helper in server.py
- Add `_get_meta(obj, semantic_tag)` helper — reads from object fields first, falls back to derived
- Update 4 XLSX sheets: สรุปพื้นที่, ความยาวเส้น Polygon, ที่จอดรถ, ระยะอ้างอิง
- Update E2E test to verify column headers appear in XLSX shared strings

---

## 4. Files Allowed

- `proto/server.py` — add constants, helpers, update 4 sheets
- `proto/e2e_ui_test.py` — extend XLSX_OK assertions for 5 new column headers

## 5. Files Forbidden

- `proto/ui.html` (JSON/CSV export already done; no UI change needed)
- `proto/requirements.txt`
- Any legal/OCR/AI/Rule Engine logic

---

## 6. Acceptance Criteria

- [ ] XLSX สรุปพื้นที่ sheet contains columns: `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`
- [ ] XLSX ความยาวเส้น Polygon sheet contains same 5 columns
- [ ] XLSX ที่จอดรถ sheet contains same 5 columns
- [ ] XLSX ระยะอ้างอิง sheet contains same 5 columns
- [ ] No existing XLSX columns removed or reordered
- [ ] JSON/CSV export behavior unchanged
- [ ] py_compile PASS
- [ ] smoke PASS
- [ ] full PASS

---

## 7. Stop Conditions

- XLSX rewrite would be required beyond appending columns
- Save/load migration becomes breaking
- Legal pass/fail logic would be needed
- Any change calculates from layer names
