# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: BLOAT-3 — Extract export/save JS to proto/static/js/export-save.js — PASS

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

# Previous: BLOAT-2 — Extract status-bar JS to proto/static/js/status-bar.js — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. py_compile PASS. smoke 18/18 + PHASE_BLOAT2_OK GREEN. full 21/21 + PHASE_BLOAT2_OK GREEN. New file `proto/static/js/status-bar.js` (49 LOC) holds the extracted status-bar module. `proto/ui.html` dropped from 4,231 to 4,208 lines (−23). No forbidden surfaces touched. `PERSIST_OK` on real 45-page permit confirms save/load round-trip integrity after the `_setDirty`/`_markSaved` extraction.

## What was delivered

- **`proto/static/js/status-bar.js`** — NEW 49 LOC file containing: `updateAnalyseUI`, `activeLayerLabel`, `currentObjectCount`, `currentWarningCount`, `updateBottomBar` (L1095–1099 cluster); `MODE_BASE_LABELS` const, `SITE_TAG_THAI_LABELS` const, `updateModeLabel` (L2378–2399 cluster); `_markSaved`, `_setDirty` (L3388/L3390). Plain classic script tag, no bundler needed.
- **`proto/ui.html`** — `<script src="/static/js/status-bar.js">` tag inserted at line 822 between `opening-parent.js` and the main inline `<script>` block. Extracted code replaced with 3 one-line comment placeholders. Net −23 LOC (4,231→4,208).
- **`proto/e2e_ui_test.py`** — `statusBarJsLoaded` field in UI-load test; new `_test_bloat2_status_bar_extracted` function (8 sub-checks: fileLoad, fnsOk, constsOk, modeLabelOk, bottomBarOk, setDirtyOk, markSavedOk, crossScriptOk); new `PHASE_BLOAT2_OK` marker.
- **Recipe proven**: cross-script `let`/`const` binding access works in classic non-module scripts; `_setDirty` from external file correctly mutates `let isDirty=false` declared in ui.html.

## What's next

- **BLOAT-3** — Extract export/save JS (`saveProject` / `saveProjectAs` / `exportCSV` / `exportJSON` / `exportXLSX` / `exportPngZip` / `saveSourcePdfInPlace` / `_makeProjBlob` / `_writeToHandle` / `_fallbackDownload`) to `proto/static/js/export-save.js`. Largest single module; est −400 to −500 LOC from ui.html. Pre-flight: `/bma-ui-scope` → `/bma-check-forbidden` (save format unchanged — additive extraction only). Depends-on BLOAT-2 (now satisfied).
- BLOAT-4 (annotations) + BLOAT-5 (page-setup) also unblocked; can run after BLOAT-3.

## Position in Plan

Phase 1 complete. BLOAT-2 is the second sprint of the BLOAT maintenance track (BLOAT-1..5). BLOAT-1 added the consolidation trigger rule; BLOAT-2 proves the extraction recipe works on the first non-trivial module (status bar). With the recipe validated, BLOAT-3..5 can proceed. Long-term target: bring `proto/ui.html` back toward ~3,000 lines.

---

# Previous (older): BLOAT-1 — CLAUDE.md LOC drift fix + consolidation trigger rule — DOCS-ONLY

**Date:** 2026-05-19
**Branch:** main

## Outcome

DOCS-ONLY sprint. No code, tests, or schema changed. Sprint result is PASS by no-test rationale. Two files touched: `CLAUDE.md` and `docs/status/PHASE_INDEX.md`. This sprint was triggered by a manual bloat audit performed before invoking `/bma-dev-loop` — user asked "โปรแกรม เริ่ม ทำงานได้ช้าไหม ไฟล์อ้วนไหม", which surfaced that `proto/ui.html` had grown 149% above its documented baseline without any consolidation mechanism in place.

## What was delivered

- Corrected `CLAUDE.md` Architecture section LOC numbers: `proto/ui.html` ~1,700 → ~4,230 lines; `proto/server.py` ~1,370 → ~1,750 lines.
- Added "Size discipline" paragraph to `CLAUDE.md`: documents drift history (360 KB inline JS, 483 functions) and establishes a hard trigger rule — if `proto/ui.html` crosses 5,000 lines, the next sprint MUST be a consolidation sprint extracting one cohesive JS region to `static/js/<region>.js`. Pattern already proven by `semantic-meta.js` and `opening-parent.js`.
- Corrected LOC numbers in the `bma-explorer` subagent table row in `CLAUDE.md`.
- Inserted BLOAT-1..5 sprint cards into `docs/status/PHASE_INDEX.md` active queue (after INV-2026-05-19-003b). Sequence: BLOAT-1 (this, docs-only) → BLOAT-2 (status-bar JS extraction, proves pattern) → BLOAT-3..5 (export-save / annotations / page-setup extraction, can parallel after BLOAT-2).
- Added `### bloat-audit 2026-05-19 (user-initiated, manual analysis pre-loop)` block to the PHASE_INDEX.md Discovered backlog explaining findings and sequencing rationale.

## What's next

- After BLOAT-2 (now done): BLOAT-3..5 (export-save / annotations / page-setup modules).

## Position in Plan

Phase 1 complete. First sprint of the BLOAT maintenance track (BLOAT-1..5). The 5,000-line consolidation trigger rule acts as a self-enforcing guard going forward.

---

> Older sprint reports archived to [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md).

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
