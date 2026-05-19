# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-20 (updated: BLOAT-2)

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

2026-05-20 — BLOAT-2 shipped: status-bar JS extracted to /static/js/status-bar.js. ui.html 4231→4208 (-23). smoke + full GREEN + PHASE_BLOAT2_OK. BLOAT-3..5 queued.

## Latest Sprint

- BLOAT-2 — Extract status-bar JS to proto/static/js/status-bar.js: PASS (2026-05-20) — NEW status-bar.js 49 LOC (8 fns + 2 consts); ui.html −23 LOC (4231→4208); smoke 18/18 + full 21/21 + PHASE_BLOAT2_OK GREEN; PERSIST_OK on real 45-page permit (proves _setDirty/_markSaved safe). BLOAT-3..5 unblocked.
- BLOAT-1 — CLAUDE.md LOC drift fix + consolidation trigger rule: DOCS-ONLY (2026-05-19) — corrected ui.html ~1700→~4230 + server.py ~1370→~1750 in CLAUDE.md; added Size discipline trigger rule (>5,000 lines → extract); BLOAT-2..5 queued in PHASE_INDEX.md. py_compile PASS; no E2E (docs-only).
- INV-2026-05-19-003b — /export-png ZIP endpoint (Path C): PASS (2026-05-19) — NEW /export-png server endpoint; PyMuPDF per-page render + ZIP bundle; Export menu wired; PHASE_INV_EXPORT_PNG_OK PASS; full EXIT 0; server.py additive (no existing endpoint modified). Commits: 612de96 + 7f0300f
- HT-18c — Save/load round-trip 13/13 GREEN: PASS (2026-05-19) — fixed _test_ht18b_save_load_round_trip eq() over-strict comparison + applyLoadedProject _projInfoSnap bug; PHASE_HT18B_OK 13/13; HT-18 series complete. Commits: f1b4331 + 9297ed4
- INV-2026-05-19-003a — Print canvas per page (Path B): PASS (2026-05-19) — "Print Current Page" + "Print Selected Pages" in File menu; canvas.toDataURL + window.print; 8 E2E sub-checks; PHASE_INV_PRINT_CANVAS_OK PASS. Commits: b4f7235 + 8200ef6
- HT-18a-ext — Extended pushUndo() coverage (22 more sites): PASS (2026-05-19) — +22 pushUndo() insertions; PHASE_HT18_OK 36/36; full EXIT 0; HUMAN_TEST_PASS (3 sites found + fixed inline)
- INV-2026-05-19-002b — F12 Overview standalone (C): PASS (2026-05-19) — `body.overview` 6-discipline card grid, lazy IntersectionObserver thumbs, atomic card-click + loadPage, F12 hotkey, Esc priority, `#ztb-chip-overview` unstubbed; PHASE_INV_OVERVIEW_OK 9/9; full EXIT 0; TEST-H SKIPPED (additive new mode, no measurement/canvas touch)
- INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled): PASS (2026-05-19) — `#zen-topbar` 40px overlay, 6 dropdowns, 4 chips, Focus sub-mode (F key), edge peek, v2 onboarding toast; PHASE_INV_ZEN_V2_OK 9/9; full EXIT 0; HUMAN_TEST_PASS; 001a UNCHANGED
- INV-2026-05-19-001c — Zen+Palette FRICTION polish: PASS (2026-05-19) — HT-Z-1 page-name direct read; HT-Z-2 amber scale chip; HT-Z-3 Thai-tag hint; PHASE_INV_POLISH_001C_OK 5/5; full EXIT 0; trilogy done
- INV-2026-05-19-001b — ⌘K Command Palette: PASS (2026-05-19) — Ctrl+K fuzzy page jump modal; 5 helpers; ArrowDown/Up/Enter/Esc nav; mid-draw guard; Zen Mode compose; PHASE_INV_PALETTE_OK 10/10; full EXIT 0; JOURNEY_OK; HT-Z-3 filed
- INV-2026-05-19-001a — Zen Mode + Sheet Minimap: PASS (2026-05-19) — body.zen chrome-hide, 3 HUDs, lazy minimap, F11/Esc, PHASE_INV_ZEN_OK 10/10, full EXIT 0, JOURNEY_OK; forbidden-surface scan CLEAN
- INV-2026-05-18-002 — Settings v2 export defaults + loupe prefs: PASS (2026-05-19) — 4 new PREFS (csvSeparator/includeLawBasis/loupe.radius/loupe.zoomFactor) additive in settings.v1; SETTINGS_V2_OK 6/6; v1 SETTINGS_OK still GREEN [commit 3e71865]
- INV-2026-05-18-001c — Page delete + renumber-map + /rebuild-pdf: PASS (2026-05-19) — NEW /rebuild-pdf endpoint; _openRenumberDialog preview table; _reindexPageDicts across 7 dicts; hard-block during draw; last-page guard; PHASE_INV_PAGE_SETUP_C_OK 7/7 [commit ebb521c]
- INV-2026-05-18-001b — Floor sub-types for plan pages: PASS (2026-05-19) — pageFloorKind/pageFloorNum additive schema; autoNamePage floor-aware; PHASE_INV_PAGE_SETUP_B_OK 9/9 (incl. save/load round-trip, tag-change clear) [commit 798e5c3]
- INV-2026-05-18-001a — Page Setup left inspector + traffic-light chips: PASS (2026-05-18) — dashboard/page-card switch; _pageReadiness; traffic-light dot (green/amber/red); PHASE_INV_PAGE_SETUP_A_OK 8/8 [commit e85a5ce]
- UI Redesign Batch HT-12..HT-15 — 15 sprints 22 commits: PASS (2026-05-18) — smoke 54/54 GREEN; 9 top-menu sprints + 4 ribbon + 3 right-panel + 1 Sheets tab; Polygon dropdown popover critical UX win
- INV-2026-05-17-001 — Freeform area (Alt sub-mode): PASS (2026-05-17) — rdpSimplify; PHASE_FREEFORM_OK 7/7; full 44/44 GREEN [commit 023b988]
- HT-6 — arc-guideline live preview: PASS (2026-05-17) — PHASE_HT6_OK 4/4; full 42/42 GREEN [commit ecb44d4]
- CIRCLE_RENDER — Analytic circle/ellipse render: PASS (2026-05-17) — CIRCLE_RENDER_OK 7/7 [commit 1bf61ca]
- dev-website — Static docs site: PASS (2026-05-17) — DOCS_SITE_OK 7/7 [commit 1bf61ca]
- INV-002 — Unified Settings modal: PASS (2026-05-17) — SETTINGS_OK 13/13 [commit b6856df]

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS EXIT 0 (18/18 + PHASE_BLOAT2_OK)
python proto/e2e_ui_test.py full                           # PASS EXIT 0 (21/21 + PHASE_BLOAT2_OK; PERSIST_OK on real 45-page permit)
```

Last full run: 2026-05-20 (BLOAT-2; new marker PHASE_BLOAT2_OK; all 21 core markers + prior sprint markers retained). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- `7f0300f` — docs(INV-003b): record commit hash 612de96 + flip queue row
- `612de96` — feat(INV-003b): /export-png ZIP endpoint (Path C)
- `9297ed4` — docs(HT-18c): record commit hash f1b4331 + flip queue row
- `f1b4331` — fix(HT-18c): save/load round-trip 13/13 GREEN
- `8200ef6` — docs(INV-003a): record commit hash b4f7235 + flip queue row
- `b4f7235` — feat(INV-003a): Print canvas per page (Path B)
- `032a53e` — docs(INV-2026-05-19-001c): record commit hash f7d64b8 + flip queue row

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
