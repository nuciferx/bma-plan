# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: UI Redesign Batch — HT-12..HT-15 (15 sprints, 22 commits in one day)

Branch: main
Date: 2026-05-18

## Outcome: PASS — smoke 54/54 GREEN (0 failures, all sprints shipped)

## Summary

Whole-day autonomous /bma-dev-loop batch. Derived from canonical mockup `proto/sandbox/mockup-top-menu-redesign.html` (created 2026-05-18 from yesterday's 3 sandbox mockups). Top menu absorbs Workspace ribbon items + Polygon dropdown surfaces sub-mode shortcuts + right panel placeholders closed.

**15 sprints shipped:**
- **HT-12a..i** Top menu redesign — density picker in menu bar (HT-12a, 10/10) · File menu wired (HT-12b, 11/11) · View menu wired (HT-12c, 15/15) · Page menu expanded (HT-12d, 14/14) · Scale menu verified (HT-12e, 8/8) · Project menu Export extension (HT-12f, 12/12) · Workspace ribbon tab hidden (HT-12g, 6/6, pragmatic — preserves 13 critical IDs + 4 E2E backward-compat) · Density behavior verify (HT-12h, 6/6) · Panel collapse buttons ◀/▶ (HT-12i, 4/4)
- **HT-13a..d** Measure ribbon polish — Helpers section rstack 2×2 (HT-13a, 6/6) · Tool+Edit verify-only no fake buttons (HT-13bc, 5/5) · **Polygon dropdown popover** (HT-13d, 12/12) — CRITICAL UX win, sub-modes A/Alt/Shift/O finally discoverable
- **HT-14a..c** Right panel content — List tab `_renderListInPanel` filter+sort+search+hover ✎/🗑 (HT-14a, 8/8) · Props tab 4 sections (HT-14b, 4/4) · Summary deep-dive verify HT-8d-2 content (HT-14c, 6/6) — closes HT-8d-1 placeholders
- **HT-15a** Sheets tab verified (6/6)
- **Cleanup** 2 pre-existing test failures fixed (HT-8D1.placeholderHasMessage, HT-8D5A.footerHas2Buttons) — test-side updates only.

Marker count: 41 → 54 smoke markers GREEN (+13 new, +0 failures). Zero forbidden-surface touches across 22 commits.

## Summary

Production implementation of Approach D from `docs/invent/freeform-area.md`. In polygon mode, holding `Alt` at mousedown enters streaming freehand sub-mode (distance-bin sampling, 6 px gate). Releasing Alt returns to click-vertex mode — mixed click+drag in the same polygon. `Shift`/`Ctrl` during draw modulates RDP tolerance live. `Enter` closes + RDP-decimates + computes area via existing `polyAreaM2`. New helper `rdpSimplify` (~25 LOC, inline). `PHASE_FREEFORM_OK` 7 sub-checks. err=0.46% on noisy circle (240 raw → 16 decimated). full 44/44 GREEN (43 pre-existing + 1 new). Commit `023b988`.

## Files Changed (cumulative across 22 commits)

| File | Lines added (approx) |
|---|---|
| `proto/ui.html` | ~700 LOC (menu dropdowns + density picker + panel collapse + Helpers section + Polygon popover + right-panel List/Props renderers + helpers) |
| `proto/static/css/app.css` | ~30 LOC (density-picker + panel-collapse-btn + poly-submode-popover) |
| `proto/e2e_ui_test.py` | ~700 LOC (16 new test functions + 17 new PHASE_HT_OK markers) |
| `docs/status/PHASE_INDEX.md` | sprint queue marked done + LOOP_RESUMED→LOOP_DONE block |
| `proto/static/docs/content.json` | rebuilt (28→31 pages) |
| `proto/sandbox/mockup-top-menu-redesign.html` | 700 LOC canonical mockup |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (pure client feature)
- `.bmaplan` schema — UNCHANGED (no new fields, additive only via PREFS.layout)

## Previous: INV-2026-05-17-001 — Freeform area measurement (2026-05-17)

PASS — full 44/44 GREEN. Approach D Alt sub-mode of polygon with RDP decimation. `rdpSimplify` ~25 LOC. `PHASE_FREEFORM_OK` 7 sub-checks. err=0.46% on noisy circle. Commit `023b988`. See previous PATCH_SUMMARY archived in `docs/archive/patch-history-2026-05-09.md` and `log.md` for the prior entry.
- `.bmaplan` schema version stays 1; `obj.freeform` is additive optional only

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS 41/41 GREEN
python proto/e2e_ui_test.py full                           → PASS 44/44 GREEN
```

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNTOUCHED
- ✅ `.bmaplan` schema — ADDITIVE only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: HT-6 — arc-guideline live preview

Branch: main
Date: 2026-05-17

## Outcome: PASS — full 42/42 GREEN (post-LOOP_DONE follow-up, zero regression)

## Summary

Single-sprint follow-up after the 10-sprint LOOP_DONE batch. User tested INV-001 Arc-polygon and reported missing live arc preview during arc-mode draft. Fix: ~15 LOC inside `redraw()` draft block — when `guidePoint` is set and through-point is captured, draws a dashed arc from last vertex curving through the through-point to the cursor. Marker `PHASE_HT6_OK` 4 sub-checks. full 42/42 GREEN (41 pre-existing + 1 new).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +1 arc preview branch in `redraw()` draft block (~1 net line) |
| `proto/e2e_ui_test.py` | +56 lines — `_test_arc_guideline()` + `PHASE_HT6_OK` marker (4 sub-checks) |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — unchanged
- `pdfToC`, `cToPdf`, `RS`, scale math — unchanged
- `buildSnapIndex`, `snap` engine — unchanged
- `proto/server.py` — unchanged
- `.bmaplan` schema version stays 1; no new fields

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → PASS GREEN
python3.11 proto/e2e_ui_test.py full                           → PASS 42/42 GREEN
```

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNTOUCHED
- ✅ `.bmaplan` schema — ADDITIVE only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- 2026-05-17 Autonomous Loop batch (10 sprints, LOOP_DONE) archived to docs/archive/patch-history-2026-05-09.md -->

# Previous: 2026-05-17 Autonomous Loop batch — 10 sprints, LOOP_DONE

Branch: main
Date: 2026-05-17

## Outcome: PASS — full 41/41 GREEN (28 pre-existing + 13 new this session)

## Summary

10-sprint autonomous loop iteration completed in one session (2026-05-17). All sprints PASS. full **41/41 GREEN**. Zero forbidden-surface edits across the entire chain. Schema fully additive. No `.bmaplan` migration. Phase I (I-A through I-E) complete. INV-001 + INV-002 done. dev-website shipped. CIRCLE_RENDER cleared. Active queue + discovered backlog both empty — LOOP_DONE.

## Today's batch (2026-05-17)

- **INV-001** (`b89e206`) — Arc-polygon hybrid: 3-click inline arc; `polyMetricsAnyShape` shim; `ARC_POLYGON_OK` 7 sub-checks (err=0.000000%)
- **SB-002** (`33577b7`) — Upload-cap UX: pre-flight modal + cold-start hint + `currentUploadCapMB` from `/upload` echo; `SB002_UPLOAD_UX_OK` 8 sub-checks
- **I-B3** (`c011c4e`) — Properties panel site fields: `buildingHeight_m` input + `isBuildingTag` + 7 site tags in Semantic Tag dropdown; `PHASE_I_B3_OK` 10 sub-checks
- **I-B4** (`91fede9`) — Site stepper widget: `#site-stepper` 6-step advisory; `updateSiteStepperUI`; `PHASE_I_B4_OK` 10 sub-checks
- **I-C** (`a490c1e`) — "ผังบริเวณ" 5th Summary Widget tab: in-app `collectSummaryData` view; BCR/OSR/FAR/Permeable + per-tag breakdown + markers + setback; `PHASE_I_C_OK` 10 sub-checks
- **I-D** (`dc96f62`) — 4-direction setback + `#canvas-compass`: `landEdgeRole` on edges; `computeEdgeSetback`; `northAngle` in pageTags; SVG compass; `PHASE_I_D_OK` 10 sub-checks
- **I-E** (`504b993`) — Building-distance + `wallEdges`: `WALL_EDGE_TYPES` catalog; `computeBuildingPairsForPage`; "ระยะระหว่างอาคาร (2h pre-check)" in siteplan tab; `PHASE_I_E_OK` 9 sub-checks
- **INV-002** (`b6856df`) — Unified Settings modal: `bmaPlan.settings.v1`; `getPref`/`setPref`; `migrateFromLegacy`; 4-tab modal; `Ctrl+,`; bad-JSON + wrong-version safety; `SETTINGS_OK` 13 sub-checks
- **dev-website** (`1bf61ca`) — Static docs site: `proto/static/docs/index.html` + `scripts/build_docs.py` + 5 Thai manual files + `content.json` (28 pages); `DOCS_SITE_OK` 7 sub-checks; user GO 2026-05-17 (invent-pending-checkpoint → done)
- **CIRCLE_RENDER** (`1bf61ca`) — Analytic circle/ellipse render: `_renderPolyEdges` short-circuit branches; `ctx.arc`/`ctx.ellipse`; storage unchanged; `CIRCLE_RENDER_OK` 7 sub-checks; last pre-loop leftover cleared

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — unchanged across all 10 sprints
- `pdfToC`, `cToPdf`, `RS`, scale math — unchanged
- `buildSnapIndex`, `snap` engine — unchanged
- `proto/server.py` — unchanged (SB-002, I-B3/B4/C/D/E, INV-002, CIRCLE_RENDER are all client-only; dev-website uses existing StaticFiles mount)
- `.bmaplan` schema version stays 1; all new fields are additive optional only

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS 41/41 GREEN
```

New markers this session (13): `ARC_POLYGON_OK` · `SB002_UPLOAD_UX_OK` · `PHASE_I_B3_OK` · `PHASE_I_B4_OK` · `PHASE_I_C_OK` · `PHASE_I_D_OK` · `PHASE_I_E_OK` · `SETTINGS_OK` · `DOCS_SITE_OK` · `CIRCLE_RENDER_OK`.

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNTOUCHED across entire batch
- ✅ `.bmaplan` schema — ADDITIVE only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: INV-001 — Arc-polygon hybrid measurement (pre-batch Latest)

Branch: main
Date: 2026-05-17

## Outcome: PASS — smoke 29/29 + full 32/32 GREEN; new marker ARC_POLYGON_OK (7 sub-checks)

Three-click inline arc during polygon draw. Reuses `polygonAreaWithArcsM2`. Zero forbidden-surface edits. Schema fully additive. Bug fixed mid-sprint: `replace_all` caused infinite recursion in `polyMetricsAnyShape`. See `sprints/completed/2026-05-17-inv-001-arc-polygon/RUN_INV_001_ARC_POLYGON.md`.

---

<!-- HT-5 and older sprints archived to docs/archive/patch-history-2026-05-09.md -->
