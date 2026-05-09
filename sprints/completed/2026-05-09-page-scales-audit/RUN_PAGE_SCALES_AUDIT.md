# RUN_PAGE_SCALES_AUDIT.md

## 0. Sprint Identity

Sprint Name: Page Scales Audit
Sprint Type: Implementation / Export Extension
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits 5835fc7 (proto) / 77069ca (root).

Existing Page Scales XLSX sheet: 7 columns (page, page_name, label, pts_per_m, source, verified, status).
These columns are raw data passed through from pageScales request body.
No derived state column. No object count. No "needs attention" flag.
An auditor cannot tell at a glance which pages have measurement issues.

---

## 2. Goal

Add 3 derived audit columns to the XLSX Page Scales sheet:
- `scale_state`: server-side computation mirroring JS `scaleState()` → "missing" / "warn" / "manual" / "ok"
- `object_count`: number of measured objects on the page (all types, from pageStore)
- `needs_attention`: True if object_count > 0 AND scale_state is not "ok" or "manual"

---

## 3. Approach

- Add `_scale_state_py(sc)` helper to server.py mirroring JS scaleState() exactly.
- In the Page Scales sheet loop, compute object_count from page_store[pg_str] and append the 3 new cells.
- Extend E2E _test_cache to verify the 3 new headers appear in the sharedStrings.xml of the XLSX.

---

## 4. Files Allowed

- `proto/server.py` — add helper, extend Page Scales sheet
- `proto/e2e_ui_test.py` — extend CACHE_OK assertion

## 5. Files Forbidden

- `proto/ui.html`
- `proto/requirements.txt`
- Legal/OCR/AI/Rule Engine logic

---

## 6. Acceptance Criteria

- [x] Page Scales XLSX sheet has 10 columns (7 existing + scale_state + object_count + needs_attention)
- [x] scale_state mirrors JS scaleState() logic: calibrated/source==manual → "manual", verified → "ok", label → "warn", else → "missing"
- [x] object_count = polys(closed) + openings(closed) + lines + refs + parking for the page
- [x] needs_attention = True iff object_count > 0 AND scale_state not in ("ok", "manual")
- [x] E2E CACHE_OK asserts all 3 new header strings appear in sharedStrings.xml
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

---

## 7. Stop Conditions

- Legal interpretation required
- Scale calculation from layer name
- Save/load migration needed
- Tests fail outside this sheet
