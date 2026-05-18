# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-18

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

2026-05-18 — UI Redesign planning DOC-ONLY. Canonical mockup `proto/sandbox/mockup-top-menu-redesign.html` written + 15 sprint cards filed in PHASE_INDEX (HT-12a..i top menu + Workspace removal; HT-13a..d Measure ribbon polish; HT-14a..c right panel content; HT-15a Sheets tab). LOOP_RESUMED 2026-05-18. Next: `/bma-dev-loop` picks HT-12a (no deps). Zero code change today. | Prior: INV-2026-05-17-001 Freeform area PASS (commit 023b988, full 44/44 GREEN) · HT-6 arc-guideline · LOOP_DONE 10-sprint batch 2026-05-17.

## Latest Sprint

- INV-2026-05-17-001 — Freeform area (Alt sub-mode): PASS (2026-05-17) — rdpSimplify + Alt-mousedown freehand burst + Shift/Ctrl tolerance + obj.freeform additive; PHASE_FREEFORM_OK 7 sub-checks errPct=0.46%; full 44/44 GREEN [commit 023b988]
- HT-6 — arc-guideline live preview: PASS (2026-05-17) — dashed arc preview in redraw() draft block when guidePoint set + mArcDraft.pending; computeArcEdge reused; PHASE_HT6_OK 4 sub-checks; full 42/42 GREEN [commit ecb44d4]
- CIRCLE_RENDER — Analytic circle/ellipse render: PASS (2026-05-17) — _renderPolyEdges short-circuit branches ctx.arc/ctx.ellipse; storage unchanged; CIRCLE_RENDER_OK 7 sub-checks; last pre-loop leftover cleared [commit 1bf61ca]
- dev-website — Static docs site: PASS (2026-05-17) — proto/static/docs/index.html + scripts/build_docs.py + 5 Thai manuals + content.json (28 pages); DOCS_SITE_OK 7 sub-checks; user GO 2026-05-17 [commit 1bf61ca]
- INV-002 — Unified Settings modal: PASS (2026-05-17) — bmaPlan.settings.v1; getPref/setPref; migrateFromLegacy; 4-tab modal (วาด/หน่วย/หน้าจอ/Widgets); Ctrl+,; bad-JSON + wrong-version safety; SETTINGS_OK 13 sub-checks [session 2026-05-17]
- I-E — Building-distance + wallEdges: PASS (2026-05-17) — WALL_EDGE_TYPES catalog (4 types); computeBuildingPairsForPage; "ระยะระหว่างอาคาร (2h pre-check)" in siteplan tab; round-trip-safe; PHASE_I_E_OK 9 sub-checks [session 2026-05-17]
- I-D — 4-direction setback + compass: PASS (2026-05-17) — landEdgeRole on edges; computeEdgeSetback; #canvas-compass SVG + northAngle in pageTags; PHASE_I_D_OK 10 sub-checks [session 2026-05-17]
- I-C — "ผังบริเวณ" 5th Summary Widget tab: PASS (2026-05-17) — in-app collectSummaryData view; BCR/OSR/FAR/Permeable + per-tag + markers + setback; Phase 1 footer note; PHASE_I_C_OK 10 sub-checks [session 2026-05-17]
- I-B4 — Site Plan stepper widget: PASS (2026-05-17) — #site-stepper 6-step advisory; updateSiteStepperUI; PHASE_I_B4_OK 10 sub-checks [session 2026-05-17]
- I-B3 — Properties panel site fields: PASS (2026-05-17) — buildingHeight_m input + isBuildingTag + 7 site tags in dropdown; PHASE_I_B3_OK 10 sub-checks [session 2026-05-17]
- SB-002 — Upload-cap UX: PASS (2026-05-17) — pre-flight modal + cold-start hint + currentUploadCapMB from /upload echo + 413 suggestions; SB002_UPLOAD_UX_OK 8 sub-checks [session 2026-05-17]
- INV-001 — Arc-polygon hybrid measurement: PASS (2026-05-17) — 3-click inline arc; polyMetricsAnyShape shim; ARC_POLYGON_OK 7 sub-checks (err=0.000000%) [session 2026-05-17]

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS GREEN
python proto/e2e_ui_test.py full                           # PASS 44/44 GREEN
```

Last run: 2026-05-17 (full 44/44 GREEN). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: `d5ec6a8` chore: update proto submodule — e2e smoke tests pass for ribbon UI
- root: `2af21a5` ui: Phase D — Summary Widget 4 tabs + drag (mockup v3 alignment)
- root: `614714e` ui: Phase B+C — title-bar + menu-bar + ribbon + panel restructure
- root: `76977ff` ui: Phase A subtractive removal (mockup v3 alignment)

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
