# RUN_MEASUREMENT_PROFILE_METADATA_FOUNDATION.md

## 0. Sprint Identity

Sprint Name: Measurement Profile Metadata Foundation
Sprint Type: Implementation / Backward-Compatible Metadata
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits d4dce83 (root) / c92f1d8 (proto).

Existing in ui.html:
- `semanticTag` on all objects
- `useCategory` on area objects
- `normalizeSemanticFields(obj, type)` — normalizes semanticTag + useCategory on load
- `defaultSemanticTag(type, obj)` — computes default semanticTag
- Properties panel shows editable Semantic Tag + Use Category dropdowns

NOT existing anywhere:
- `measurementProfile`
- `objectCategory`
- `reportTarget`
- `lawBasis`
- `countingRule`

---

## 2. Goal

Add 5 new metadata fields to all runtime objects in a backward-compatible way:

```text
measurementProfile  — why/how object is measured (e.g. "legal_building_area")
objectCategory      — functional family (e.g. "area", "site_fact", "deduction")
reportTarget        — export/report destination (e.g. "Building Area Summary")
lawBasis            — descriptive label only, not pass/fail (e.g. "พื้นที่อาคาร")
countingRule        — how object is counted (e.g. "included", "deducted", "classified")
```

All 5 are derived from `semanticTag` via lookup tables. No legal pass/fail logic.

---

## 3. Approach

### Derivation (not recalculation)

All 5 fields are deterministic from `semanticTag`:
- New mapping constants: `SEMANTIC_PROFILE_MAP`, `SEMANTIC_CATEGORY_MAP`, `SEMANTIC_REPORT_TARGET_MAP`, `SEMANTIC_LAW_BASIS_MAP`, `SEMANTIC_COUNTING_RULE_MAP`
- Helper: `deriveMeasurementMeta(tag)` → returns all 5

### Backward Compatibility

- Old objects (loaded from .bmaplan without the 5 fields) are normalized via `normalizeSemanticFields()` which is already called on all objects at load/save
- Fields are only set if not already present (except lawBasis which uses `hasOwnProperty`)
- No migration script needed

### rpSetSemanticTag update

When user changes semanticTag, the 5 derived fields update automatically.

### Properties Panel

Show 5 fields as read-only labels (not editable) in the existing `.rp-prop-grid` below Use Category.

### Export

Add 5 fields to measurements JSON rows (ui.html export path).
server.py XLSX export is NOT changed in this sprint (deferred — additive column changes need their own audit).

---

## 4. Files Allowed

- `proto/ui.html` — constants, helpers, normalization, panel, export rows
- `proto/e2e_ui_test.py` — add metaOk, metaPanelVisible, strippedMetaOk assertions

## 5. Files Forbidden

- `proto/server.py` (no XLSX change in this sprint)
- `proto/requirements.txt`
- Any legal/OCR/AI/Rule Engine logic

---

## 6. Acceptance Criteria

- [ ] `SEMANTIC_PROFILE_MAP`, `SEMANTIC_CATEGORY_MAP`, `SEMANTIC_REPORT_TARGET_MAP`, `SEMANTIC_LAW_BASIS_MAP`, `SEMANTIC_COUNTING_RULE_MAP` defined
- [ ] `deriveMeasurementMeta(tag)` helper works
- [ ] `normalizeSemanticFields` adds 5 fields backward-compatibly
- [ ] `rpSetSemanticTag` updates 5 derived fields
- [ ] Properties panel shows 5 fields read-only
- [ ] measurements.json rows include 5 new fields
- [ ] py_compile PASS
- [ ] smoke PASS
- [ ] full PASS

---

## 7. Stop Conditions

- Any test fails that can't be fixed within normalizeSemanticFields / deriveMeasurementMeta scope
- Backend rewrite is needed
- Save/load migration becomes breaking
- Legal pass/fail logic would be needed
