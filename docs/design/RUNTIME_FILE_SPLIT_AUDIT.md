# RUNTIME_FILE_SPLIT_AUDIT.md — BMA-Plan Runtime File Size Audit

Date: 2026-05-09

## Baseline File Sizes (start of sprint)

| File | Lines | Status |
|------|-------|--------|
| proto/ui.html | 1437 | Monolith — no split implemented |
| proto/server.py | 1451 | Partially split (see Part C below) |
| proto/e2e_ui_test.py | 1525 | Monolith — split deferred (see Part E) |

## Part C — Server Export Module Split (DONE)

**Implemented:** proto/export/ package created.

| New File | Lines | Contents |
|----------|-------|----------|
| export/__init__.py | 0 | Package init |
| export/semantic_metadata.py | ~80 | SEMANTIC_*_MAPs, AREA_SEMANTIC_TAGS, _derive_measurement_meta, _get_meta |
| export/xlsx_helpers.py | ~75 | _hex_to_rgb, _poly_area_pt2, _line_points, _line_length_pt, _nearest_on_segment, _object_points_for_ref_report, _distance_to_ref, _m2_to_rwu |

**Result:** server.py reduced from 1451 → ~1290 lines. All names re-imported at module level. Tests PASS.

**NOT extracted (too risky):**
- TAG_LABELS + _scale_state_py + _semantic_tag + _use_category: these reference each other and server state.
- export_xlsx (lines 826–1412): 586-line monolith using local variables shared across 7 XLSX sheet builders. Safe extraction would require a large refactor — stop condition applies.

## Part D — Frontend JS Split (DEFERRED)

**Status:** Not implemented.

**Reason:** Server does not mount a StaticFiles endpoint. ui.html is served via `_load_html()` inline. Adding StaticFiles requires:
1. Backend change: `app.mount("/static", StaticFiles(directory="static"), name="static")`
2. HTML change: replace inline `<script>` blocks with `<script src="/static/js/...">` tags
3. Split 1437-line ui.html into multiple JS files — browser load order matters for global event handlers

Risk: Any error in the split breaks the entire UI. Stop condition: "Frontend split breaks global event handlers."

**Recommended approach (future sprint):**
1. Add StaticFiles mount to server.py
2. Extract one self-contained module at a time (e.g., snap.js, export.js)
3. Test after each extraction

## Part E — E2E Test Split (DEFERRED)

See `docs/design/E2E_SPLIT_PLAN.md` for proposed structure.

**Reason not implemented:** Tests share browser/page/context state and run sequentially. Splitting into multiple files breaks the shared-state model and requires a test runner or pytest-playwright integration.
