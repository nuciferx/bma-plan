# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-19

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Ribbon cleanup polish — scale-badge + active-layer-select hidden, Review wrapped in rsection, font reverted 16→14. Ready to commit.

## Latest Sprint

- Ribbon Cleanup Polish — scale-badge/layer-select hidden + Review rsection + font 16→14px: PASS (2026-05-19) — pure CSS+DOM cosmetic; py_compile PASS; smoke PASS; no JS logic change; no forbidden surfaces
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
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python3.11 proto/e2e_ui_test.py smoke                          # PASS GREEN (18 markers)
python3.11 proto/e2e_ui_test.py full                           # PASS (last full run: 2026-05-17, 44/44)
```

Last smoke run: 2026-05-19 (Ribbon Cleanup Polish; all 18 markers GREEN). `full` not run since 2026-05-17 (no forbidden-trigger surfaces touched in subsequent sprints). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- `3e71865` — INV-002 Settings v2: export defaults + loupe prefs
- `ebb521c` — INV-001c: permanent delete + renumber-map + /rebuild-pdf
- `afd4e71` — INV-001c research: page-delete UX survey + Q1-Q4 design answers
- `798e5c3` — INV-001b: floor sub-types for plan pages (pageFloorKind/pageFloorNum)
- `e85a5ce` — INV-001a: Page Setup left inspector + traffic-light chips (initial repo commit)

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
