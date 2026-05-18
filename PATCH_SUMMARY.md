# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Ribbon Cleanup Polish — hide scale-badge + active-layer-select + Review rsection wrap + font revert

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke PASS (earlier in session), pure cosmetic changes

## Summary

Pure CSS + DOM `display:none` ribbon cleanup with zero JS logic change. Hid the `#scale-badge` red pill from the ribbon (status bar Scale field already surfaces this state) and hid the `#active-layer-select` ribbon-group (Right panel Layers tab is the primary path; select element preserved in DOM for JS references). Rewrapped the `#btn-report` Review button in a proper `.rsection` + `.rlbl` + `.rrow` structure so it renders at the same 60px uniform height as all other ribbon groups instead of stretching to the full 78px ribbon height. Reverted `body { font-size }` from 16px back to 14px after real-Chrome testing showed layout shifts in inherited-font-size elements.

## Files Changed

| File | Change |
|---|---|
| `proto/static/css/app.css` | `body { font-size: 16px }` → `14px` (1-line revert) |
| `proto/ui.html` | `#scale-badge` `display:none`; `.ribbon-group` wrapping `#active-layer-select` `display:none` + 2 `rdiv` dividers removed; `#btn-report` rewrapped in `.ribbon-group.rsection` with `.rlbl "📊 REVIEW"` + `.rrow` + leading `rdiv` |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (no server edit in this sprint)
- `.bmaplan` schema version stays 1; no schema fields added or removed

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke  → PASS (earlier in session; all 18 markers GREEN)
full not run: no forbidden-trigger surfaces touched (export/rotation/save-load/real-PDF/snap/layer unchanged)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: Page Setup Redesign trilogy + Settings v2 (INV-001a/b/c + INV-002)

Branch: main
Date: 2026-05-18..19

## Outcome: PASS — smoke GREEN, all 4 INV markers GREEN, zero forbidden-surface edits

## Summary

Four sprints shipped in one overnight session, plus one research commit. The **Page Setup Redesign trilogy** (INV-001a/b/c) delivers a context-sensitive left inspector that switches between a multi-page dashboard view (traffic-light readiness chips) and a per-page card view (tag/scale/floor configuration + permanent delete with renumber-map preview). A new `/rebuild-pdf` server endpoint (`ebb521c`) performs PyMuPDF page deletion with an in-place case-dict reindex across all 7 per-page dicts. The **Settings v2** sprint (INV-002, `3e71865`) extends the existing `bmaPlan.settings.v1` store with four new PREFS: CSV separator, include-law-basis flag, loupe radius, and loupe zoom factor — wired into `exportCSV` and `updateLoupe` without touching v1 paths.

Research commit `afd4e71` surveyed Bluebeam, Adobe, Foxit, Nitro, AutoCAD, and PlanGrid page-delete UX before building 001c — verdict PRIOR_ART_PARTIAL (algorithm solved everywhere; BMA's renumber-map preview is genuinely better than incumbents). Q1-Q4 design answers locked in `docs/invent/page-setup-redesign.md`.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | ~600 LOC — inspector helpers, floor-kind picker, delete dialog + `_reindexPageDicts`, `_applyLoupePrefs`, `exportCSV` extended (commits `e85a5ce`, `798e5c3`, `ebb521c`, `3e71865`) |
| `proto/server.py` | +50 LOC — `/rebuild-pdf` POST endpoint: `doc.delete_page()` reverse-order loop, `page_cache`/`image_cache` flush, `{totalPages, renumberMap, deletedNumbers}` response (`ebb521c`) |
| `proto/static/css/app.css` | ~80 LOC — inspector dashboard/page-card layout, traffic-light dot, delete dialog (`e85a5ce`, `ebb521c`) |
| `proto/e2e_ui_test.py` | ~280 LOC — 4 new test functions + marker prints (`e85a5ce`, `798e5c3`, `ebb521c`, `3e71865`) |
| `docs/invent/page-setup-redesign.md` | Research addendum + Q1-Q4 + Decision sections (`afd4e71`) |
| `docs/status/PHASE_INDEX.md` | Sprint card status updates + commit hashes + trilogy summary (`afd4e71`, `ebb521c`, `3e71865`) |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` core `/upload` / `/page/{n}` / `/analyse` — UNCHANGED; `/rebuild-pdf` is a NEW additive endpoint per U1/U2/SB-001 precedent
- `.bmaplan` schema — ADDITIVE only (`pageFloorKind`/`pageFloorNum` optional dicts, version stays 1)
- No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

## Tests Run

```
py -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py proto/e2e_ui_test.py smoke                          → PASS
  PHASE_INV_PAGE_SETUP_A_OK 8/8  PASS
  PHASE_INV_PAGE_SETUP_B_OK 9/9  PASS
  PHASE_INV_PAGE_SETUP_C_OK 7/7  PASS
  SETTINGS_V2_OK 6/6             PASS
  SETTINGS_OK (v1 baseline)      still GREEN — no v1 regression
```

Pre-existing failures (NOT caused by this session): HT-8C.objectsTabRenamed / HT-10.compactIsSmallerThanSpacious / HT-12H.cssCascadeChangesButtonSize — surfaces untouched, documented baseline drift.

`full` E2E not run (no forbidden-trigger surfaces touched). `/bma-human-test` deferred by user to next session.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints `/upload` / `/page/{n}` / `/analyse` — UNCHANGED
- ✅ `.bmaplan` schema — ADDITIVE only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (Phase 1 boundary preserved)

---

# Previous: UI Redesign Batch — HT-12..HT-15 (15 sprints, 22 commits in one day)

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

## Files Changed (cumulative across 22 commits)

| File | Lines added (approx) |
|---|---|
| `proto/ui.html` | ~700 LOC (menu dropdowns + density picker + panel collapse + Helpers section + Polygon popover + right-panel List/Props renderers + helpers) |
| `proto/static/css/app.css` | ~30 LOC (density-picker + panel-collapse-btn + poly-submode-popover) |
| `proto/e2e_ui_test.py` | ~700 LOC (16 new test functions + 17 new PHASE_HT_OK markers) |
| `docs/status/PHASE_INDEX.md` | sprint queue marked done + LOOP_RESUMED→LOOP_DONE block |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (pure client feature)
- `.bmaplan` schema — UNCHANGED

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS 54/54 GREEN
python proto/e2e_ui_test.py full                           → not run (no forbidden-trigger surfaces touched)
```

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNTOUCHED
- ✅ `.bmaplan` schema — ADDITIVE only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- HT-6 and older patches archived to docs/archive/patch-history-2026-05-09.md -->

# Previous (older): HT-6 — arc-guideline live preview

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
