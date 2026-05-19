# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: BLOAT-4 — Extract annotation JS to proto/static/js/annotations.js — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. py_compile PASS. Full retry GREEN: all 22 baseline markers + PHASE_BLOAT4_OK 8/8 + PHASE_INV_STICKY_OK 10/10 + PHASE_HT11_OK 10/10. First full run failed on the known intermittent REAL_PDF analyse flake (page 1/45, unrelated to BLOAT-4); dev-loop one-retry rule applied; retry EXIT 0. No forbidden surfaces touched. No user-visible change. `proto/ui.html` dropped from 4,057 to 3,869 lines (−188 net). Session total across BLOAT-1..4: ui.html 4,231→3,869 (−362 lines).

## What was delivered

- **`proto/static/js/annotations.js`** — NEW 205 LOC: 13 annotation helper functions extracted from `proto/ui.html` (L1680–1869): `ensureAnnotations` (lazy array init), `newAnnotationId` (id factory), `addAnnotation` (append + save + redraw + sticky if applicable), `renderStickyCards` (HTML overlay sync from INV-2026-05-19-005), `_createStickyCard` (DOM builder + drag/edit/delete event wiring), `clearAnnotations` (with confirm), `annotationHitTest` (returns array index at canvas coords for all 7 ann types), `deleteAnnotation` (splice with pushUndo), `openAnnotationEditModal` (HT-11 modal — color picker + textarea + delete button), `closeAnnotationEditModal`, `saveAnnotationEdit` (writes text + color, pushUndo), `_annColor` (default-color helper), `drawAnnotations` (canvas render dispatcher for 7 non-sticky types). Plain classic script tag, no bundler.
- **`proto/ui.html`** — `<script src="/static/js/annotations.js">` tag added after `export-save.js`. Extracted block replaced with 1 placeholder comment. Net −188 LOC (4,057→3,869). Kept in scope: 7 per-mode mousedown branches (tightly coupled to unified pointer state; call extracted helpers via global scope).
- **`proto/e2e_ui_test.py`** — `annotationsJsLoaded` field in UI-load test; new `_test_bloat4_annotations_extracted` function (8 sub-checks: `fileLoad`, `fnsOk`, `addOk`, `hitMissOk`, `drawOk`, `stickyOk`, `colorOk`, `clearOk`); new `PHASE_BLOAT4_OK` marker.
- **Recipe 4-for-4**: status-bar / export-save / annotations all proven in this session. Pattern now includes cross-script DOM-builder helpers (`_createStickyCard`) and event-wiring (sticky drag) — confirms the recipe applies to interactive annotation UI, not just stateless computation.

## What's next

- **BLOAT-5** — Extract page-setup modal JS (`_renderSetupDashboard` / `_renderSetupPageCard` / `_openRenumberDialog` / `_executeRenumberDelete` / `_reindexPageDicts` / floor-kind helpers / setup-inspector switching) to `proto/static/js/page-setup.js`. Est. ~300 LOC delta. Scope skill: `/bma-ui-scope` → `/bma-ui-panel`. Critical markers to preserve: `PHASE_INV_PAGE_SETUP_A_OK` / `_B_OK` / `_C_OK`. Depends-on BLOAT-2 (done) + BLOAT-3 (done).
- Optional BLOAT-3b: extract print cluster to `proto/static/js/print-canvas.js` (~50–60 LOC delta). Self-contained; low-risk.

## Position in Plan

Phase 1 complete. BLOAT-4 is the fourth sprint of the BLOAT maintenance track (BLOAT-1..5). BLOAT-1 added the discipline rule; BLOAT-2 proved the recipe; BLOAT-3 scaled it to the largest cluster (export+save); BLOAT-4 proves the recipe extends to interactive DOM-builder + event-wiring cases (sticky notes, edit modal). With annotations extracted, BLOAT-5 (page-setup modal) is the final planned extraction. Long-term target: bring `proto/ui.html` toward ~3,500 lines (currently 3,869; −362 from session start).

---

# Previous: BLOAT-3 — Extract export/save JS to proto/static/js/export-save.js — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. py_compile PASS. smoke 18/18 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN. full 21/21 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN. New file `proto/static/js/export-save.js` (188 LOC) holds the full extracted export + save module. `proto/ui.html` dropped from 4,208 to 4,057 lines (−151 net). No forbidden surfaces touched. `XLSX_OK` + `PROJECT_OK` + `PERSIST_OK` + `ANNOT_OK` all GREEN on real 45-page permit; `schemaOk` sub-check confirms `.bmaplan` v1 schema (12 fields) intact post-extraction.

## What was delivered

- **`proto/static/js/export-save.js`** — NEW 188 LOC: 6 column consts (`COL_PAGE/TYPE/NAME/VALUE/UNIT/RNW`), 7 type consts (`TYPE_DISTANCE/PATH/REF/PARKING/AREA/OPENING/REF_DISTANCE`), `rowBase` + `buildRows` (row builder), `dlBlob` (download helper), `exportJSON` / `exportCSV`, `exportSummaryXLSX` / `exportXLSX` (1-page summary + 4-sheet detail), `exportAllPagesAnnotatedPDF` / `exportCurrentPageAnnotatedPDF`, `exportPngZip`, `_makeProjBlob` / `_writeToHandle` / `_fallbackDownload` / `saveProjectAs` / `saveProject` / `saveSourcePdfInPlace`. Plain classic script tag, no bundler needed.
- **`proto/ui.html`** — `<script src="/static/js/export-save.js">` tag added after `status-bar.js`. Extracted code replaced with 3 one-line comment placeholders. Net −151 LOC (4,208→4,057). Kept in scope: `pgmgrExportPDF` (Page-Manager modal coupling), print cluster (separate logical group, BLOAT-3b), load side (`applyLoadedProject` et al., fragile + heavy UI-global coupling), shared helpers (`collectAreas` / `collectSummaryData` etc., used by summary widget too — not pure export).
- **`proto/e2e_ui_test.py`** — `exportSaveJsLoaded` field in UI-load test; new `_test_bloat3_export_save_extracted` function (8 sub-checks: `fileLoad`, `fnsOk`, `constsOk`, `dlBlobOk`, `buildRowsOk`, `blobIsBlob`, `schemaOk`, `asyncOk`); new `PHASE_BLOAT3_OK` marker.
- **Recipe battle-tested on largest cluster**: cross-script binding access works; FSA handle persistence (`saveProject`/`saveSourcePdfInPlace` mutate `currentProjectHandle`/`currentSourcePdfHandle` declared in `ui.html`) confirmed safe; `.bmaplan` schema serialization untouched.

## What's next

- **BLOAT-4** — Extract annotation JS (7 annotation tool handlers: `ann_text` / `ann_highlight` / `ann_rect` / `ann_circle` / `ann_cloud` / `ann_arrow` / `ann_sticky` + render + hit-test) to `proto/static/js/annotations.js`. Est. ~300 LOC. Pre-flight: `/bma-ui-scope`. Depends-on BLOAT-2 and BLOAT-3 (both now satisfied).
- BLOAT-5 (page-setup modal extraction) — after BLOAT-4 or in parallel.
- Optional BLOAT-3b: extract print cluster (~50–60 LOC delta) to `proto/static/js/print-canvas.js`. Low-risk.

## Position in Plan

Phase 1 complete. BLOAT-3 is the third sprint of the BLOAT maintenance track (BLOAT-1..5). BLOAT-1 added the consolidation trigger rule; BLOAT-2 proved the extraction recipe on the status-bar module; BLOAT-3 proves the recipe scales to the largest and most complex cluster (export + save). With recipe validated on the hardest piece, BLOAT-4..5 are formulaic. Long-term target: bring `proto/ui.html` back toward ~3,000 lines (currently 4,057).

---

<!-- Previous (older) BLOAT-2 and BLOAT-1 reports archived to docs/archive/reports-2026-05-09.md -->

**Date:** 2026-05-19
**Branch:** main

## Outcome

PASS across all three sprints in the session bundle. INV-003b: new `/export-png` ZIP endpoint additive to `proto/server.py`; `PHASE_INV_EXPORT_PNG_OK` PASS. HT-18c: `PHASE_HT18B_OK` 13/13 GREEN — the HT-18 series is now fully closed (HT-18a + HT-18a-ext + HT-18b-with-caveat + HT-18c all done). INV-003a: `PHASE_INV_PRINT_CANVAS_OK` (8 sub-checks) PASS. No regressions. Session totals: 33 commits pushed to `origin/main-v2-2026-05-19`; local `main` tracks that branch.

## What was delivered

- **INV-003b** — NEW `/export-png` ZIP endpoint: accepts `case_id + selected_pages[] + dpi_scale`, renders via PyMuPDF, returns `application/zip`. Export menu wired. New E2E marker `PHASE_INV_EXPORT_PNG_OK`. (Commits: `612de96` feat + `7f0300f` docs.)
- **HT-18c** — Fixed `_test_ht18b_save_load_round_trip`: replaced deep `eq()` with field-by-field comparison for all 13 round-trip sub-checks. Also fixed `applyLoadedProject` `_projInfoSnap` restoration. `PHASE_HT18B_OK` 13/13 GREEN. HT-18 series complete. (Commits: `f1b4331` fix + `9297ed4` docs.)
- **INV-003a** — "Print Current Page" + "Print Selected Pages" in File menu: client-side `canvas.toDataURL("image/png")` + `window.print()`. 8 E2E sub-checks. New marker `PHASE_INV_PRINT_CANVAS_OK`. (Commits: `b4f7235` feat + `8200ef6` docs.)
- **Pending (uncommitted)**: Zen Mode user manual docs sprint — `proto/manual/zen-mode.md` (~80 LOC NEW) + keyboard-shortcuts.md (+2 LOC) + getting-started.md (+1 LOC) + `content.json` rebuild.

## What's next

- **(a) Finalize Zen Mode user manual docs sprint** — uncommitted 4-file docs sprint. Review + commit.
- **(b) INV-2026-05-19-002c** — F12 Overview mockup-port (~240 LOC JS+CSS). Sprint card queued (commit `5468d13`); invent GO verdict MATURE. Depends-on INV-002b (done). Run via `/loop /bma-dev-loop`.
- **(c) Rebase/merge strategy** — local `main` tracks `origin/main-v2-2026-05-19`. Consider whether to rebase onto the legacy remote `main` (62 commits at `24f5d94`) or keep parallel branch strategy.

## Position in Plan

Phase 1 complete. HT-18 series fully closed after HT-18c. INV series: 001a/b/c + 002a/b + 003a/b all DONE. Next INV: 002c (F12 mockup port). Session was the largest in the project: 33 commits, Zen Mode v1+v2 full suite + print canvas (B+C) + HT-18 a/a-ext/b/c complete.

---

> Older sprint reports (HT-18a-ext, HT-18a, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md).

<!-- ARCHIVED BELOW — HT-18a-ext (formerly Previous, now superseded) -->

# Previous (older): HT-18a-ext Extended pushUndo() coverage to 22 more mutation sites — PASS

**Date:** 2026-05-19
**Branch:** main

## Outcome

PASS. py_compile PASS, `python proto/e2e_ui_test.py full` EXIT 0. `PHASE_HT18_OK` upgraded from 7/7 (HT-18a) to **36/36** — the permanent regression guard now covers all confirmed mutation sites. Human journey test (`/bma-human-test`) HUMAN_TEST_PASS after inline fix of 3 sites discovered mid-audit. Forbidden-surface scan CLEAN. `proto/server.py` NOT touched. No schema change. 4 pre-existing sub-check failures unchanged; none are regressions from this sprint.

## What was delivered

- `pushUndo()` inserted at 22 additional mutation sites in `proto/ui.html` (layer reorder/rename/color/lock/visibility helpers; page tag/floor/name/exclude/restore/rotate/reset helpers; `pageCtxMenu` inline `autoNamePage` call). `_skipUndo` param added to `excludePage` + `restorePage2` for batch-caller safety. +39 LOC.
- `_test_ht18_pushundo_leaks` in `proto/e2e_ui_test.py` extended: 7 → 36 sub-checks (22 source-presence + 7 runtime isDirty-flip + 7 original from HT-18a). `PHASE_HT18_OK` = `{'all': True}` 36/36. +295 LOC.
- `docs/status/PHASE_INDEX.md` updated: HT-18a-ext card filed (done), HT-18b updated to `done-with-test-design-caveat`, HT-18c upgraded from `pending conditional` to `queued` with concrete scope.
- `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md` — Phase A drift-map artifact (~120 lines).
- 3 sites found by `/bma-human-test` and missed by initial Phase A audit (`toggleLayer` L2657, `layerHideOthers` L2659, `layerShowAll` L2666) fixed inline in same iteration.
- Cross-links: HT-18a commit `895a9d7`, HT-18a-ext this sprint, HT-18b `done-with-test-design-caveat`, HT-18c queued.

## What's next

- **HT-18c** — Fix `_test_ht18b_save_load_round_trip` `eq()` comparison (too strict after `normalizeAllObjects` mutates pre-snapshot). ~30-50 LOC, test-only, no app code change. After HT-18c lands, HT-18 series complete.
- After HT-18c: **INV-2026-05-19-002c** — F12 Overview mockup-port (~240 LOC JS+CSS, invent GO verdict MATURE, sprint card queued at commit `5468d13`, depends-on 002b done).

## Position in Plan

Phase 1 complete. HT-18 series fully closed after HT-18c. INV series: 001a/b/c + 002a/b + 003a/b all DONE. Next INV: 002c (F12 mockup port). Session was the largest in the project: 33 commits, Zen Mode v1+v2 full suite + print canvas (B+C) + HT-18 a/a-ext/b/c complete.

---

> Older sprint reports (HT-18a-ext, HT-18a, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md).
