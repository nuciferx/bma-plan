# RUN_REPORT_TARGET_SUMMARY_XLSX.md

## 0. Sprint Identity

Sprint Name: Report Target Summary XLSX
Sprint Type: Implementation / Export Feature
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits 6197985 (proto) / dc64fdd (root).

Existing state:
- All XLSX sheets already write `reportTarget` per object row.
- `reportTarget` values are derived from `semanticTag` via `SEMANTIC_REPORT_TARGET_MAP`.
- No aggregated view by `reportTarget` exists yet.

---

## 2. Goal

Add a new XLSX sheet `สรุปตาม Report Target` that groups all measured objects by their `reportTarget` and shows:
- object count per group
- area total (m²) for area/site_fact/deduction objects
- length total (m) for dimension/reference objects
- parking count for parking objects
- list of pages that contribute to each group

---

## 3. Approach

- Collect all objects from all pages in pageStore.
- For each object, get reportTarget from object fields (via `_get_meta(obj, semantic_tag)`).
- Group by (reportTarget, objectCategory, countingRule) — the combination gives a meaningful, non-redundant row.
- Rows sorted by canonical RT_ORDER: Building Area Summary → Use Category Summary → Open Space Summary → Deduction Summary → Parking Summary → Site Facts → Distance Facts → Height Facts → Audit Log → Unclassified.
- No legal logic, no pass/fail, no calculation from layer name.
- `from collections import defaultdict` added to top-level imports.

---

## 4. Files Allowed

- `proto/server.py` — add new sheet, add `defaultdict` import
- `proto/e2e_ui_test.py` — extend XLSX sheet name check for new sheet

## 5. Files Forbidden

- `proto/ui.html`
- `proto/requirements.txt`
- Legal/OCR/AI/Rule Engine logic

---

## 6. Acceptance Criteria

- [x] New XLSX sheet "สรุปตาม Report Target" exists
- [x] Sheet has columns: Report Target, Object Category, Counting Rule, Pages, Objects, Area (m²), Length (m), Parking
- [x] Rows grouped and sorted by RT_ORDER
- [x] Unknown reportTarget → "Unclassified"
- [x] Grand total row at bottom
- [x] E2E sheet name assertion includes new sheet
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

---

## 7. Stop Conditions

- Legal interpretation required
- Export requires broad rewrite
- Save/load migration needed
- Tests fail outside local export code
