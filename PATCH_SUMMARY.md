# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BLOAT-2 — Extract status-bar JS to proto/static/js/status-bar.js

Branch: main
Date: 2026-05-20

## Outcome: PASS — py_compile PASS, smoke 18/18 + PHASE_BLOAT2_OK, full 21/21 + PHASE_BLOAT2_OK GREEN

## Summary

Extracted 8 status-bar functions (`updateAnalyseUI`, `activeLayerLabel`, `currentObjectCount`, `currentWarningCount`, `updateBottomBar`, `updateModeLabel`, `_markSaved`, `_setDirty`) and 2 constants (`MODE_BASE_LABELS`, `SITE_TAG_THAI_LABELS`) from `proto/ui.html`'s inline `<script>` block into a new file `proto/static/js/status-bar.js` (49 LOC, plain non-module classic script). `proto/ui.html` shrunk from 4,231 to 4,208 lines (−23). Proves the no-bundler extraction recipe: cross-script binding access works; `PERSIST_OK` on real 45-page permit confirms `_setDirty`/`_markSaved` extraction is safe. New E2E marker `PHASE_BLOAT2_OK` added. BLOAT-3..5 are now unblocked.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | −29 +6 — removed 8 fns + 2 consts from inline `<script>`; added `<script src="/static/js/status-bar.js">` tag (line 822); 3 one-line comment placeholders remain |
| `proto/static/js/status-bar.js` | NEW 49 LOC — 8 status-bar functions + 2 constants (plain non-module classic script) |
| `proto/e2e_ui_test.py` | +95 LOC — `statusBarJsLoaded` field + `_test_bloat2_status_bar_extracted` (8 sub-checks) + `PHASE_BLOAT2_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — UNCHANGED (zero edits this sprint)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no field added, renamed, or removed

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0, 18/18 + PHASE_BLOAT2_OK GREEN
python proto/e2e_ui_test.py full                           → EXIT 0, 21/21 + PHASE_BLOAT2_OK GREEN
  (PERSIST_OK on real 45-page permit — proves _setDirty/_markSaved extraction safe across save/reload)
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PERSIST_OK covers most sensitive surface)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: BLOAT-1 — CLAUDE.md LOC drift fix + consolidation trigger rule (docs-only)

Branch: main
Date: 2026-05-19

## Outcome: DOCS-ONLY — py_compile PASS (sanity baseline); no E2E tests run (docs-only sprint, no code path touched)

## Summary

Pre-loop bloat audit sprint. Corrected stale LOC baselines in `CLAUDE.md`: `proto/ui.html` had drifted from ~1,700 to ~4,230 lines (+149%), and `proto/server.py` from ~1,370 to ~1,750. Added a "Size discipline" paragraph with a hard rule: if `proto/ui.html` crosses 5,000 lines the next sprint MUST extract one cohesive JS region to `static/js/<region>.js` (following the `semantic-meta.js` / `opening-parent.js` pattern). Queued BLOAT-2..5 sprint cards in `docs/status/PHASE_INDEX.md` active queue; added a `### bloat-audit 2026-05-19` block to the Discovered backlog. No code, schema, or runtime files were changed.

## Files Changed

| File | Change |
|---|---|
| `CLAUDE.md` | +21 −2 — LOC corrections in Architecture section (ui.html ~1700→~4230, server.py ~1370→~1750) + new Size discipline paragraph + bma-explorer subagent row LOC correction |
| `docs/status/PHASE_INDEX.md` | +26 −0 — BLOAT-1..5 active-queue rows + `### bloat-audit 2026-05-19` Discovered-backlog block |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — UNCHANGED
- `proto/ui.html` — UNCHANGED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no field added, renamed, or removed

## Tests Run

None. Docs-only sprint. `python -m py_compile proto/server.py` → PASS (sanity baseline only). Per AGENTS.md §1, docs-only sprints record a no-test rationale: this sprint changed only `CLAUDE.md` and `docs/status/PHASE_INDEX.md`. No source code, UI, test code, or schema changed. `/bma-e2e` and `/bma-human-test` not run.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous (older): INV-2026-05-19-003b — /export-png ZIP endpoint (Path C)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, full EXIT 0; PHASE_INV_EXPORT_PNG_OK (new marker); all predecessor markers retained

## Summary

End-of-day bundle headline sprint. NEW `/export-png` ZIP endpoint in `proto/server.py` (additive — no existing endpoint modified): accepts `case_id + selected_pages[] + dpi_scale`, renders each selected page via PyMuPDF at the requested DPI scale, bundles PNGs into a ZIP archive returned as `application/zip`. Export menu in `proto/ui.html` wired with "Export PNG (ZIP)" option. This is Path C of the print-canvas-per-page invent (INV-003), providing high-DPI archival PNG export as a complement to Path B (INV-003a, fast browser-print). Together 003a + 003b close the invention. Also in this session bundle: HT-18c fixed save/load round-trip test to 13/13 GREEN (closing the HT-18 series), and INV-003a delivered browser-side "Print Current Page" + "Print Selected Pages" via `canvas.toDataURL + window.print()`. Session totals: 33 commits pushed to `origin/main-v2-2026-05-19`.

## Files Changed

| File | Change |
|---|---|
| `proto/server.py` | NEW `/export-png` endpoint — additive; accepts case_id + page list + dpi_scale; PyMuPDF render per page; ZIP bundle; case isolation preserved |
| `proto/ui.html` | Export menu `/export-png` wiring; "Print Current Page" + "Print Selected Pages" File menu items; `printCurrentPage()` + `printSelectedPages()` helpers |
| `proto/e2e_ui_test.py` | `_test_inv_export_png` (PHASE_INV_EXPORT_PNG_OK); `_test_inv_print_canvas` (PHASE_INV_PRINT_CANVAS_OK, 8 sub-checks); `_test_ht18b_save_load_round_trip` 13/13 field-by-field fix |
| `docs/status/PHASE_INDEX.md` | Queue rows flipped for INV-003a, HT-18c, INV-003b |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — additive NEW endpoint only; no rename or removal of existing endpoints; case isolation preserved
- `.bmaplan` schema version stays 1; no field rename or removal

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (all three sprints in bundle)

INV-003b: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_EXPORT_PNG_OK: PASS (new marker)

HT-18c: python proto/e2e_ui_test.py smoke → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (was 7/13; eq() over-strict comparison fixed + applyLoadedProject _projInfoSnap fix)

INV-003a: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_PRINT_CANVAS_OK: PASS (8 sub-checks)

Predecessor markers confirmed retained: PHASE_HT18_OK 36/36,
PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9,
PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10,
PHASE_INV_POLISH_001C_OK 5/5
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ⚠️ `proto/server.py` — INV-003b added `/export-png` (additive new endpoint; no rename/removal of existing endpoints; case isolation preserved; no schema change)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

> Older sprints (HT-18c, HT-18a-ext, HT-18a, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) and git commit log.

<!-- ARCHIVED BELOW — HT-18c (formerly Previous, now superseded) -->

# Previous (older): HT-18c — Save/load round-trip E2E test 13/13 GREEN

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0; PHASE_HT18B_OK 13/13 GREEN (closes HT-18 series)

## Summary

Fixed `_test_ht18b_save_load_round_trip` 13-sub-check round-trip test. Root cause: deep `eq()` comparison was too strict — `normalizeAllObjects` mutated the pre-snapshot object before the comparison, making legitimately equal fields appear different. Fix: replaced deep `eq()` with field-by-field checks on the 13 specific fields a save/load round-trip should preserve. Also fixed a bug in `applyLoadedProject` (HT-18d-equivalent): `_projInfoSnap` was not being correctly restored from blob — confirmed by the test reading `_projInfoSnap` from post-load global state rather than just the blob. After both fixes, `PHASE_HT18B_OK` = 13/13 GREEN. The HT-18 series (HT-18a + HT-18a-ext + HT-18b-with-caveat + HT-18c) is now complete.

## Files Changed

| File | Change |
|---|---|
| `proto/e2e_ui_test.py` | `_test_ht18b_save_load_round_trip` — deep `eq()` replaced by field-by-field checks for 13 sub-checks (A poly / B opening / C line / D ref / E parking / F-M page metadata + projectInfo + layer state); `_projInfoSnap` post-load global read |
| `proto/ui.html` | `applyLoadedProject` — `_projInfoSnap` restoration fix (HT-18d-equivalent) |
| `docs/status/PHASE_INDEX.md` | HT-18c card flipped to done |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no field rename or removal

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (A poly round-trip, B opening, C line, D ref, E parking,
  F-M page metadata / projectInfo / layer state — all PASS)
  All predecessor markers retained: PHASE_HT18_OK 36/36 + INV markers all GREEN
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; fix is in `applyLoadedProject` restore logic, not schema fields)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

> Older sprints (HT-18a, HT-18a-ext, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) and git commit log.
