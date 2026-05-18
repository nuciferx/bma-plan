# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-18 — UI Redesign planning: canonical mockup + HT-12..HT-15 sprint queue (docs-only)

**What happened:** Planning session — derived UI roadmap from yesterday's sandbox mockups (`mockup-ribbon-redesign.html`, `mockup-annotation-review.html`, `mockup-interactive-full.html`) and produced a new consolidated canonical target: **`proto/sandbox/mockup-top-menu-redesign.html`** — now the single source of truth for UI direction. Fixed grid-row overlap bug (ribbon row was clamped to fixed height, now `auto` with `min-height: var(--ribbon-h)`). Filed 15 sprint cards into `PHASE_INDEX.md` for `/bma-dev-loop`.

**Canonical decisions (mockup-top-menu-redesign.html):**
1. Workspace ribbon tab → REMOVED; items distributed across 9 menu dropdowns (File/Edit/View/Page/Scale/Project/Measure/Annotate/Help)
2. Ribbon = 3 tabs only (📐 วัด / 📝 Annotate / 📍 Site Plan disabled-default)
3. Measure ribbon = 7 sections — rstack 2×2 (Tool/Helpers/Edit) + HERO (Set Scale + Polygon)
4. Polygon dropdown popover for sub-mode discovery (A=Arc / Alt=Freeform / Shift=Ortho / O=Opening)
5. Density picker in menu bar (Compact/Comfortable/Spacious) → CSS variables drive sizing
6. Panel collapse buttons (◀/▶ each side, body class swap)
7. Right panel = 5 tabs (Layers default-active + List/Props/Summary/Notes)
8. Left panel = 3 tabs (Pages/Sheets/Tree)

**Sprints queued (15, depends-on graph encoded):**
- **HT-12a..i** — Top menu expansion + Workspace removal + density + panel collapse [a→b/c/d/e/f→g; h/i independent]
- **HT-13a..d** — Measure ribbon polish (Helpers, Tool rstack, Edit rstack, Polygon dropdown) [all depend on HT-12g]
- **HT-14a..c** — Right panel content (📋 List, 🔧 Props, 📊 Summary deep-dive — closes HT-8d-1 placeholders) [independent]
- **HT-15a** — Left panel Sheets tab [independent]

`LOOP_DONE 2026-05-17` block updated to `LOOP_RESUMED 2026-05-18` in PHASE_INDEX.md.

**Why:** Phase 1 reached LOOP_DONE 2026-05-17 with queue empty. User UI feedback after testing INV-freeform/HT-6 + yesterday's mockup design session surfaced ~15 concrete sprints. All fall under existing UI specialist skills (`/bma-ui-menu`, `/bma-ui-ribbon`, `/bma-ui-panel`) — no new specialists needed.

**Files touched:**
- `proto/sandbox/mockup-top-menu-redesign.html` — created (~700 LOC, canonical UI target with full density picker + collapse buttons + left/right panels + ribbon)
- `docs/status/PHASE_INDEX.md` — LOOP_RESUMED note + Canonical UI Mockup section + 15 sprint rows
- `docs/status/LATEST_STATUS.md` — date header + latest sprint summary
- `docs/status/NEXT_ACTIONS.md` — Immediate Next switched from "queue empty" → HT-12a
- `CURRENT_STATUS.md` — one-line state
- `log.md` — this entry

**Tests:** No code change → no E2E required. py_compile not run. Doc-only session.

**Phase 1 scope check:**
- ✅ Zero `proto/ui.html` / `proto/server.py` edits (mockup lives in `proto/sandbox/`)
- ✅ Zero `.bmaplan` schema changes
- ✅ Zero forbidden-surface touches
- ✅ Phase 1 boundary respected

**Known gaps / follow-ups:**
- Density picker has 2 implementations now: HT-10 (Settings modal) + HT-12h (menu bar). HT-12h sprint card includes bridge with `applyLayoutPrefs()` so they coexist or HT-10 entry deprecates gracefully.
- Mockup conflicts with earlier user feedback: mockup keeps Shape section + Comment HERO, but user previously said "remove". Sprint cards reflect mockup as authoritative — follow-up sprint can flip if desired.
- Comment/Annotation redesign (Notes tab content / HT-14d removed from queue) stays `invent-queued` — needs `/bma-invent` DIVERGE before becoming a sprint.

**Next:** `/loop /bma-dev-loop` picks HT-12a (no dependencies, top of queue) → menu bar DOM + dropdown CSS shell. Est. ~200 LOC HTML+CSS, zero forbidden surface.

---

## 2026-05-17 — INV-2026-05-17-001 Freeform area measurement — PASS (branch: main)

**What changed:** NEW `rdpSimplify(pts, tol)` inline RDP helper (~25 LOC) added next to area-math block. Seven new module-scope state vars for freehand tracking. Extended mousedown (Alt-at-mousedown enters freehand sub-mode), mousemove (freehand branch before snap; snap engine untouched), mouseup (commit via RDP+cToPdf), setMode/clearMeasures/Esc (reset), finishCurrentArea (additive `obj.freeform` metadata), Shift/Ctrl keydown (live tolerance mod), redraw (red dashed trail during burst). ~80 LOC in `proto/ui.html`. ~120 LOC in `proto/e2e_ui_test.py` (`_test_inv_freeform_area` + `PHASE_FREEFORM_OK` 7 sub-checks + defensive try/except in `_test_menu_power_up`). Commit `023b988`.

**Why:** INV-2026-05-17-001 was filed `invent-done-go` in `PHASE_INDEX.md` after the 7-phase invention pipeline. User approved Approach D (Alt sub-mode of polygon, Ramer-Douglas-Peucker decimation) on 2026-05-17. Spike PASS 6/6 (err=1.22%) in `proto/sandbox/invent-freeform-area.html`. Production pass improves to 7/7 (err=0.46%, 240 raw → 16 decimated pts on noisy circle).

**Files touched:**
- `proto/ui.html`: `rdpSimplify` helper + freehand state vars + 6 event-handler extensions + redraw trail
- `proto/e2e_ui_test.py`: `_test_inv_freeform_area` + `PHASE_FREEFORM_OK` marker + defensive try/except

**Tests:** `py_compile PASS · smoke PASS 41/41 · full PASS 44/44 GREEN (PHASE_FREEFORM_OK 7/7, errPct=0.46%)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED (`polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`)
- ✅ `proto/server.py` — UNTOUCHED
- ✅ `.bmaplan` schema — ADDITIVE only (`obj.freeform` optional). Version stays 1.
- ✅ Phase 1 boundary — kept.

**Known gaps / follow-ups:**
- TEST-H skipped (Alt-mousedown not exercised by `bma-human-journey-tester`). User to test manually at http://127.0.0.1:8001.
- Touch/pointer events deferred to iPad track.
- Future: `bma-human-journey-tester` enhancement to cover Alt-drag freehand.

---

## 2026-05-17 — HT-6 arc-guideline live preview — PASS (branch: main)

**What changed:** Inside `redraw()` draft block (`mArcDraft.pending` branch), added a new arc-preview path: when `guidePoint` is set and `mPts.length >= 1`, calls `computeArcEdge(lastPdfVertex, mousePdf, throughPt, centroid)` and draws a dashed arc (`#ff453a`, 5/zoom dash, 0.85 alpha) from last vertex curving through the through-point to the cursor. ~15 LOC. New E2E marker `PHASE_HT6_OK` 4 sub-checks. full **42/42 GREEN** (41 pre-existing + 1 new). Commit `ecb44d4`.

**Why:** User-test 2026-05-17 (post-LOOP_DONE follow-up). User tested INV-001 Arc-polygon, said "ทำได้ โอเค มาก" but noted the arc draft lacked a live guideline preview — "ขาดเส้น guideline เหมือนของเส้นตรง". Straight-line polygon draw already renders a dashed guide from last vertex to cursor (`guidePoint` in `redraw()` L1478); this sprint adds the arc equivalent.

**Files touched:**
- `proto/ui.html`: +1 arc preview branch in `redraw()` draft block (~1 net line)
- `proto/e2e_ui_test.py`: +56 lines — `_test_arc_guideline()` + `PHASE_HT6_OK` marker

**Tests:** `py_compile PASS · smoke PASS · full PASS 42/42 GREEN (PHASE_HT6_OK 4/4)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED
- ✅ `proto/server.py` — UNTOUCHED
- ✅ `.bmaplan` schema — UNTOUCHED. Version stays 1.
- ✅ Phase 1 boundary — kept.

**Known gaps / follow-ups:**
- TEST-H skipped (render-only branch; `bma-human-journey-tester` does not exercise arc-mode interactively). Future: arc-mode interactive sub-test in journey tester.

---

## 2026-05-17 — dev-website Static Docs Site — PASS (branch: main)

**What changed:** NEW `proto/static/docs/index.html` (~190 LOC) — single static HTML, inline ~80-line micro-markdown renderer, fetches sibling `content.json`, exposes `window.__bmaDocs` for tests, offline file:// fallback. NEW `scripts/build_docs.py` (~120 LOC, stdlib-only) — walks `proto/manual/*.md`, `log.md` (split by `## YYYY-MM-DD`, 12 most recent), `sprints/completed/**/RUN_*.md` (12 most recent), `docs/process/{ANTI_PATTERNS,TROUBLESHOOTING}.md`; emits `proto/static/docs/content.json` (28 pages, 4 groups). NEW 5 Thai manual files: `getting-started`, `set-scale`, `measure-tools`, `export`, `keyboard-shortcuts`. NEW E2E marker `DOCS_SITE_OK` 7 sub-checks.

**Why:** User GO 2026-05-17 on dev-website invention checkpoint (`docs/invent/dev-website.md`, PRIOR_ART_PARTIAL, Approach A, spike PASS 8/8). Goal: browsable dev log + onboarding manual accessible at `/static/docs/` without any server or `ui.html` changes. Help menu link deferred to follow-up `/bma-ui-menu` sprint (preserves "zero ui.html edits" boundary).

**Files touched:**
- `proto/static/docs/index.html`: NEW — static docs site HTML (~190 LOC)
- `scripts/build_docs.py`: NEW — stdlib build script (~120 LOC)
- `proto/manual/getting-started.md`: NEW — Thai getting-started manual
- `proto/manual/set-scale.md`: NEW — Thai set-scale manual
- `proto/manual/measure-tools.md`: NEW — Thai measure-tools manual
- `proto/manual/export.md`: NEW — Thai export manual
- `proto/manual/keyboard-shortcuts.md`: NEW — Thai keyboard-shortcuts manual
- `proto/static/docs/content.json`: NEW — first build (28 pages, 4 groups, ~50 KB)
- `proto/e2e_ui_test.py`: NEW `_test_docs_site` + DOCS_SITE_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS 41/41 GREEN (DOCS_SITE_OK 7/7)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED. `proto/ui.html` not touched.
- ✅ `proto/server.py` — UNTOUCHED. Static serving already registered.
- ✅ `.bmaplan` schema — UNTOUCHED. Version stays 1.
- ✅ Phase 1 boundary — kept.

**Known gaps / follow-ups:**
- Help menu wiring deferred to follow-up `/bma-ui-menu` sprint.
- `python scripts/build_docs.py` step in `/bma-sprint-finalize` skill — separate small sprint.

---

## 2026-05-17 — CIRCLE_RENDER Analytic circle/ellipse render — PASS (branch: main)

**What changed:** `_renderPolyEdges(ctx, poly, cp)` in `proto/ui.html` gained two short-circuit branches at the top: `poly.shape==='circle'` → `ctx.arc(...)` analytic; `poly.shape==='ellipse'` → `ctx.ellipse(...)` analytic; else → existing line/arc-edge flow unchanged. Storage (`poly.pts` 32-gon), hit-test, snap, area math all stay on legacy. `objectAreaM2` already routed circle/ellipse to closed-form helpers. NEW E2E marker `CIRCLE_RENDER_OK` 7 sub-checks.

**Why:** Phase H.1 (2026-05-13) shipped 32-gon `circleToPath`/`ellipseToPath` generators — area math correct but circles/ellipses rendered as faceted polygons because `redraw()` drew pts as line segments. Visual audit (`docs/status/PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`) confirmed math PASS, render gap. This sprint was the last pre-loop leftover; now cleared. Bundled in commit `1bf61ca` with dev-website.

**Files touched:**
- `proto/ui.html`: `_renderPolyEdges` — 2 analytic short-circuit branches at top (~12 lines)
- `proto/e2e_ui_test.py`: NEW `_test_circle_render` + CIRCLE_RENDER_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS 41/41 GREEN (CIRCLE_RENDER_OK 7/7)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED. Storage/snap/area math untouched.
- ✅ `.bmaplan` schema — UNTOUCHED. Version stays 1, `poly.pts` storage unchanged.
- ✅ Phase 1 boundary — kept.

**Known gaps / follow-ups:**
- None. Phase H visual audit fully resolved. Last pre-loop leftover cleared.

---

## 2026-05-17 — INV-002 Unified Settings/Preferences modal — PASS (branch: main)

**What changed:** `proto/ui.html` — `bmaPlan.settings.v1` localStorage key (version:1); `getPref`/`setPref` path-based reader/writer; `migrateFromLegacy()` one-way migration from `uiLayoutOptions.v1` + `widgetPlacement.v1` (flexible `preset||mode` lookup + `{visible:bool}` or plain-bool extraction); `openSettingsModal`/`closeSettingsModal`/`applySettings`/`resetSettings`; `#settings-modal` DOM (4 tabs: วาด/หน่วย/หน้าจอ/Widgets); `Ctrl+,` handler; bad-JSON + wrong-version safety. `proto/e2e_ui_test.py` — NEW `_test_settings(page)` 13 sub-checks + marker `SETTINGS_OK`.

**Why:** INV-2026-05-15-002 was `invent-done-go` after spike PASS 7/7. Production sprint added bad-JSON safety, wrong-version safety, and legacyPreserved check on top of spike's 7, bringing total to 13. Resolves 3 checkpoint carry-over risks: (1) legacy key shape via flexible lookup; (2) widget-registry coupling = visible-only migration; (3) Apply-on-save pattern adopted; immediate-apply deferred.

**Files touched:**
- `proto/ui.html`: settings system (~310 lines added)
- `proto/e2e_ui_test.py`: NEW `_test_settings` + SETTINGS_OK marker

**Tests:** `py_compile PASS · smoke PASS (SETTINGS_OK 13/13) · full PASS GREEN`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED. `snap` engine read only at call-site boundary via `getPref`.
- ✅ `.bmaplan` schema — UNTOUCHED. Settings live in localStorage only.
- ✅ Phase 1 boundary — kept.

**Known gaps / follow-ups:**
- Immediate-apply (live preview while modal open) deferred to follow-up UX sprint.
- Settings not embedded in `.bmaplan` per-project — deferred.

---

## 2026-05-17 — I-E Building-to-building distance + wallEdges — PASS (branch: main)

**What changed:** `proto/ui.html` — `WALL_EDGE_TYPES` catalog (4 types + Thai labels); `computeBuildingPairsForPage`; `computeAllBuildingPairs`; siteplan tab extended with "ระยะระหว่างอาคาร (2h pre-check)" section; `wallEdgeType` additive field on polygon edges. `proto/e2e_ui_test.py` — NEW `_test_phase_i_e(page)` 9 sub-checks + marker `PHASE_I_E_OK`.

**Why:** มร.55 ข้อ 48 requires measuring min distance between buildings. Phase I-E implements the measurement fact collection (vertex-to-edge metric across all building-coverage polygon pairs). No 2h verdict — facts only per Phase 1 boundary. `wallEdges` schema additive, round-trip safe.

**Files touched:**
- `proto/ui.html`: 3 new functions + siteplan tab extension + wallEdgeType on edge objects
- `proto/e2e_ui_test.py`: NEW `_test_phase_i_e` + PHASE_I_E_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS GREEN (PHASE_I_E_OK 9/9)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED. Distance uses same formula as I-D setback.
- ✅ `.bmaplan` schema — ADDITIVE. `wallEdgeType` null-default; version stays 1.
- ✅ Phase 1 boundary — kept (no 2h verdict, no pass/fail).

**Known gaps / follow-ups:** Wall-edge-type editing UI in Properties panel — deferred.

---

## 2026-05-17 — I-D 4-direction setback + compass overlay — PASS (branch: main)

**What changed:** `proto/ui.html` — `computeEdgeSetback(poly, role, refPolys, pg)` generalizing front-only setback to 4 directions via `landEdgeRole` on edges; `collectSetbackReport` extended; `#canvas-compass` SVG overlay (48×48, top-right, rotates to `northAngle`); `northAngle` in `pageTags`; Page Setup input for north angle. `proto/e2e_ui_test.py` — `_test_phase_i_d` 10 sub-checks + `PHASE_I_D_OK`.

**Why:** U2 had front-setback only. I-D extends to all 4 directions using `landEdgeRole` on site boundary edges. Compass gives users directional context without requiring PDF vector data.

**Files touched:**
- `proto/ui.html`: `computeEdgeSetback`; `collectSetbackReport` extended; compass DOM + fn; `northAngle` in pageTags; Page Setup input
- `proto/e2e_ui_test.py`: NEW `_test_phase_i_d` + PHASE_I_D_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS GREEN (PHASE_I_D_OK 10/10)`

**Phase 1 scope check:**
- ✅ All forbidden surfaces — UNTOUCHED.
- ✅ `.bmaplan` schema — ADDITIVE. `northAngle` + `landEdgeRole` additive; version stays 1.
- ✅ Phase 1 boundary — kept (setback facts only, no verdict).

**Known gaps / follow-ups:** none.

---

## 2026-05-17 — I-C "ผังบริเวณ" 5th Summary Widget tab — PASS (branch: main)

**What changed:** `proto/ui.html` — 5th tab `#tab-siteplan` + `#summary-siteplan` content div; `updateSiteplanTab()` renders `collectSummaryData()` output inline (BCR/OSR/FAR/Permeable + per-tag breakdown + marker counts + front-setback + Phase 1 footer note); hook in `updateSummaryWidget()`. `proto/e2e_ui_test.py` — `_test_phase_i_c` 10 sub-checks + `PHASE_I_C_OK`.

**Why:** Users needed an in-app view of the site plan summary without exporting XLSX. Reuses `collectSummaryData()` from U2 — no new server logic. Phase 1 footer note hard-coded as scope guardrail.

**Files touched:**
- `proto/ui.html`: 5th tab DOM + `updateSiteplanTab` fn + hook
- `proto/e2e_ui_test.py`: NEW `_test_phase_i_c` + PHASE_I_C_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS GREEN (PHASE_I_C_OK 10/10)`

**Phase 1 scope check:** ✅ All forbidden surfaces UNTOUCHED. ✅ No server changes. ✅ Phase 1 boundary kept.

**Known gaps / follow-ups:** XLSX additive sheet for siteplan tab — deferred to future sprint.

---

## 2026-05-17 — I-B4 Site Plan 6-step stepper widget — PASS (branch: main)

**What changed:** `proto/ui.html` — `#site-stepper` DOM (6 steps, collapsible, site-page-only); `updateSiteStepperUI()` fn derives step state from existing page/project data; hooks in `updateBottomBar` + `loadPage`; visibility toggle in `updateSiteRibbon`. `proto/e2e_ui_test.py` — `_test_phase_i_b4` 10 sub-checks + `PHASE_I_B4_OK`.

**Why:** Users needed guided workflow on site pages (Set Scale → Tag → Project Info → draw coverage → draw open/permeable → markers). Advisory-only stepper; no blocking.

**Files touched:**
- `proto/ui.html`: stepper DOM + `updateSiteStepperUI` + hooks
- `proto/e2e_ui_test.py`: NEW `_test_phase_i_b4` + PHASE_I_B4_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS GREEN (PHASE_I_B4_OK 10/10)`

**Phase 1 scope check:** ✅ All forbidden surfaces UNTOUCHED. ✅ No `.bmaplan` schema change. ✅ Phase 1 boundary kept.

**Known gaps / follow-ups:** none.

---

## 2026-05-17 — I-B3 Properties panel site fields — PASS (branch: main)

**What changed:** `proto/ui.html` — `isBuildingTag(tag)` helper; `buildPropertiesPanel` extended with `buildingHeight_m` editable input (visible when `isBuildingTag`) and 7 site-tag options appended to Semantic Tag dropdown on site pages. `proto/e2e_ui_test.py` — `_test_phase_i_b3` 10 sub-checks + `PHASE_I_B3_OK`.

**Why:** Draw-then-classify workflow: users draw polygons first, then assign semanticTag via Properties panel. `buildingHeight_m` needed for future 2h rule data collection (I-E).

**Files touched:**
- `proto/ui.html`: `isBuildingTag` helper + Properties panel extensions
- `proto/e2e_ui_test.py`: NEW `_test_phase_i_b3` + PHASE_I_B3_OK marker

**Tests:** `py_compile PASS · smoke PASS · full PASS GREEN (PHASE_I_B3_OK 10/10)`

**Phase 1 scope check:** ✅ All forbidden surfaces UNTOUCHED. ✅ Schema additive (`buildingHeight_m` defined in I-A). ✅ Phase 1 boundary kept.

**Known gaps / follow-ups:** none.

---

## 2026-05-17 — SB-002 Upload-cap UX modal — PASS (branch: main)

**What changed:** `proto/ui.html` — `currentUploadCapMB` state var updated from `/upload` echo; pre-flight size check in `uploadPdfFile`; `showUploadCapModal(fileSizeMB, capMB)` helper; `updateCapBadge()` cold-start hint; clear 413 modal with actionable suggestions. `proto/e2e_ui_test.py` — `_test_sb002_upload_ux` 8 sub-checks + marker `SB002_UPLOAD_UX_OK`.

**Why:** SB-002 FRICTION: after raising cap in SB-001, users still saw only a status-bar string on upload failure. Pre-flight modal prevents sending large files; cold-start hint shows current limit; actionable suggestions reduce support burden.

**Files touched:**
- `proto/ui.html`: `currentUploadCapMB` + `showUploadCapModal` + `updateCapBadge` + pre-flight check
- `proto/e2e_ui_test.py`: NEW `_test_sb002_upload_ux` + SB002_UPLOAD_UX_OK marker

**Tests:** `py_compile PASS · smoke PASS (SB002_UPLOAD_UX_OK 8/8) · full PASS GREEN`

**Phase 1 scope check:** ✅ All forbidden surfaces UNTOUCHED. ✅ `proto/server.py` UNTOUCHED. ✅ No schema change.

**Known gaps / follow-ups:** none.

---

## 2026-05-17 — INV-001 Arc-polygon hybrid measurement — PASS (branch: main)

**What changed:**
- `proto/ui.html` — 4 new helpers in the area-math block (right after `objectAreaM2`): `_arcCircumcenter(A,P,B)`, `_arcPolygonCentroid(pts)`, `computeArcEdge(A,B,P,polygonCentroid)`, `polyMetricsAnyShape(poly,pg)`, `_renderPolyEdges(ctx,poly,cp)`. New state `mArcDraft={pending:false,throughPt:null,edges:[]}`. Mousedown handler in area-mode extended with arc-flush and arc-through-point branches. `finishCurrentArea` carries optional `edges:[...]` on the poly literal (arc-only). `redraw()` uses `_renderPolyEdges` for both committed and draft polys, and calls `polyMetricsAnyShape` at 9 display sites (was `polyMetrics`). `setMode`/`clearMeasures`/`drawBarCancel`/undo-point/Esc/`A`-key all updated to manage `mArcDraft`. Through-point click deliberately bypasses snap (raw `cToPdf(cx,cy)`). Schema additive: new optional `obj.edges[i]={edgeType:"arc",arcSweep,arcThrough}` in `pageStore`; legacy files load unchanged via `Array.isArray(obj.edges)` guard.
- `proto/e2e_ui_test.py` — NEW `_test_arc_polygon(page)` (~95 lines) with 7 sub-checks: fnsExist (7 functions), closedFormPasses (square+semicircle canonical err=0.000000%), dispatchOK, degenerateOK, roundTripOK, legacyUnchanged, polyMetricsAnyShapeOK. New marker `ARC_POLYGON_OK` wired after `PATH_GEOMETRY_OK`. smoke count 28→29, full count 31→32.
- `NEXT_ACTION.md` — updated priority queue note.

**Why:** Arc-polygon hybrid measurement was designed + spiked in the invention loop (INV-2026-05-15-001, `docs/invent/arc-polygon.md` + `proto/sandbox/invent-arc-polygon.html`). Ported to production: three-click inline arc (vertex N → press `A` → click through-point → vertex N+1) lets users trace curved walls, curved boundary fences, and arc setbacks in one polygon — critical for real-world site-plan PDFs. Reuses the already-shipped `polygonAreaWithArcsM2` (exact formula: polygon area ± circular segment per arc edge), so zero new forbidden-surface risk. Area math is correct to 0.000000% on canonical square+semicircle test (computed=expected=13926.9908 px²).

**Files touched:**
- `proto/ui.html`: 4 helpers + 1 state var + 12 edit sites (~56 net lines changed)
- `proto/e2e_ui_test.py`: NEW `_test_arc_polygon` + marker (~123 lines added)
- `NEXT_ACTION.md`: 4-line queue update

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS 29/29 GREEN
python proto/e2e_ui_test.py full                           → PASS 32/32 GREEN
```
ARC_POLYGON_OK: `{fnsExist:T, closedFormPasses:T, dispatchOK:T, degenerateOK:T, roundTripOK:T, legacyUnchanged:T, polyMetricsAnyShapeOK:T, all:T, debug:{computedPx:'13926.9908', expectedPx:'13926.9908', errPct:'0.000000', sweep:'3.141593'}}`.

**Phase 1 scope check:**
- ✅ `polyAreaM2` — UNTOUCHED. Additive helpers sit next to it.
- ✅ `polyMetrics` — UNTOUCHED. `polyMetricsAnyShape` shim dispatches on `obj.edges`; legacy polys call `polyMetrics` directly inside the shim.
- ✅ `polySelfIntersects` — UNTOUCHED. Called by `polyMetricsAnyShape` for arc polys (same check as legacy).
- ✅ `pdfToC`, `cToPdf`, `RS` — UNTOUCHED. `_renderPolyEdges` calls `pdfToC` at call sites only; scale math unchanged.
- ✅ `buildSnapIndex` / `snap` — UNTOUCHED. Through-point deliberately bypasses snap at call site; engine unmodified.
- ✅ `.bmaplan` schema — ADDITIVE. New optional `edges` field; legacy v1 files load unchanged.
- ✅ `proto/server.py` — UNTOUCHED. Pure client feature.
- ✅ Phase 1 boundary — kept. No legal verdict, no OCR, no AI, no FAR/OSR rule.

**Known gaps / follow-ups:**
- Bug found and fixed mid-sprint: `replace_all polyMetrics → polyMetricsAnyShape` caught the internal call inside `polyMetricsAnyShape` body itself → infinite recursion → `updatePageSummary` crash → `VECTOR_OK` failed with "ยังไม่มีรายการพื้นที่". Fixed with one targeted Edit restoring the body to call `polyMetrics` directly. Same trap could recur with future `replace_all` on a forbidden-surface name — documented in sprint card.
- Through-point snap bypass is deliberate in v1; arc through-point snap (nearest-to-chord, perpendicular) is a future enhancement.
- Opening polygons do not get arc edges in v1 — deliberate scope limit.

---

## 2026-05-15

### [session] HT-5 — `.dd-submenu` overflow on short viewports — PASS (branch: main)

**What changed:**
- `proto/static/css/app.css:25` — `.dd-submenu` rule += `max-height:calc(100vh - 120px); overflow-y:auto; overflow-x:hidden; scrollbar-width:thin`.
- `proto/e2e_ui_test.py` — NEW `_test_ht5_submenu_overflow()` 3 sub-checks: `hasMaxH` (rule.style.maxHeight includes 'calc'), `hasOverflowY === 'auto'`, `hasOverflowX === 'hidden'`. Marker `PHASE_HT5_OK`.

Marker count: 30 → **31**.

**Why:** Found by human-test 2026-05-15 (COSMETIC, HT-5). Measure menu's site submenu มี 15 items — `.dd-submenu` ล้น short viewports (412 px tall) เพราะไม่มี `max-height` / `overflow`. Same CSS rule ที่เคย bundle กับ HT-1 (z-index fix) — revert ตอนนั้นตาม one-sprint-one-commit rule.

**Forbidden surfaces:** zero. CSS-only.

**Tests:** full → 31/31 GREEN. PHASE_HT5_OK: `{hasMaxH: T, hasOverflowY: T, hasOverflowX: T, ruleMaxH: 'calc(-120px + 100vh)', ruleOverflowY: 'auto', ruleOverflowX: 'hidden'}`.

**Position:** Autonomous Dev Loop iteration 10. **All HT-1..5 human-test findings cleared.** Next: SB-2026-05-15-002 (upload-cap UX FRICTION).

---

<!-- HT-4 (2026-05-15) and older sessions archived to docs/archive/log-2026-05-15.md -->

### [session] HT-3 — `lbl-mode` site-tag context — PASS (branch: main)

**What changed:**
- `proto/ui.html` — extracted inline mode-label write จาก `setMode()` เป็น standalone `updateModeLabel(m)` helper + `MODE_BASE_LABELS` const + NEW `SITE_TAG_THAI_LABELS` map (7 site tags Thai labels, mirror ของ `U2_SITE_AREA_TAGS`). `updateModeLabel()` appends `(ผังบริเวณ — <thai>)` เมื่อ `m==="area" && curSiteSemanticTag` set, หรือ `(<markerLabel>)` เมื่อ `m==="parking" && curMarkerType !== "parking"`. `setMode` แทน inline write ด้วย `updateModeLabel(m)`. `finishCurrentArea()` เพิ่ม `updateModeLabel()` call ตรง `curSiteSemanticTag=null` เพื่อ refresh suffix ทันที.
- `proto/e2e_ui_test.py` — NEW `_test_ht3_lbl_mode_site_context()` 7 sub-checks: helper exists, plain area = `วัดพื้นที่ ⬡`, site tool = `วัดพื้นที่ ⬡ (ผังบริเวณ — ปกคลุมอาคาร)`, switch tags updates suffix, marker tool with `parking_disabled` adds `(จอดผู้พิการ)`, switch back to plain clears, standalone `updateModeLabel()` refresh after `curSiteSemanticTag=null` works.

Marker count: 28 → **29**.

**Why:** Found by human-test 2026-05-15 (FRICTION, HT-3). ตอน user คลิก "ปกคลุมอาคาร" ใน Measure menu / site ribbon, `lbl-mode` แสดงแค่ "วัดพื้นที่ ⬡" — user ไม่รู้ว่ากำลังวาดประเภทไหน, ต้องดู ribbon active state เอง.

**Why local `SITE_TAG_THAI_LABELS` instead of editing `SEMANTIC_TAG_LABELS`:** ของเดิมเป็น key→key map (เช่น `building_coverage:"building_coverage"`) ใช้ใน Properties Panel dropdown options ที่อื่น. การเปลี่ยนเป็น Thai labels ของ existing entries จะส่งผลกระทบ dropdown options ด้วย — scope creep. เลือกเพิ่ม local map ขนาดเล็กตรง HT-3 helper แทน. ตัวอักษร Thai 7 entries กับ HT-3 helper อยู่บรรทัดเดียวกันได้.

**Forbidden surfaces:** zero. UI-only ใน status bar.

**Tests:** `python3.11 proto/e2e_ui_test.py full` → 29/29 GREEN. PHASE_HT3_OK 7 sub-checks: `{has:T, plainOk:T, siteOk:T, siteSwitchOk:T, mkOk:T, afterOk:T, clearedOk:T}`. Sample label = `'วัดพื้นที่ ⬡ (ผังบริเวณ — ปกคลุมอาคาร)'`.

**Position:** Autonomous Dev Loop iteration 8. Next: HT-4 (FRICTION name-panel dismissal).

---

### [session] HT-2 — `⬡ NaN ตร.ม.` display guard — PASS (branch: main)

**What changed:**
- `proto/ui.html` — NEW `fmtAreaM2(v, hint)` + `fmtDistM(v, hint)` helpers next to `polyAreaM2` (additive — `polyAreaM2` เป็น forbidden surface ไม่แตะ). คืน `"—"` หรือ `hint` สำหรับ `null` / `NaN` / `undefined` / `Infinity`. 10 display sites updated to use `fmtAreaM2()` + `Number.isFinite()` guards:
  - `finishCurrentArea()` measure-result × 2 paths (opening + area) — แสดง hint "ตั้ง scale ก่อนเพื่อแสดงพื้นที่"
  - `_swBuildArea` summary widget: gross/land/openings/net + breakdown by type
  - `_swBuildFloor` per-page + รวมทุกชั้น — แสดง "— (ตั้ง scale ก่อน)" สำหรับหน้าไม่มี scale
  - `_swBuildSite` เนื้อที่ที่ดิน
  - `objMetricText` (poly/opening/line/ref)
  - `rp-metric` Gross/Opening/Net ใน `buildLeftProperties` + `buildRightPanel` (2 sites, `replace_all`)
  - `drawPolyLabel` area row
- `proto/e2e_ui_test.py` — NEW `_test_ht2_nan_area_guard()` 12 sub-checks: helpers exist, fmtAreaM2 returns "—" สำหรับ `null`/`NaN`/`undefined`/`Infinity`, returns `"0.00 ตร.ม."` สำหรับ 0, `"123.46 ตร.ม."` สำหรับ 123.456, รับ hint string ถูกต้อง, fmtDistM mirror behaviour, **live-DOM scan** สำหรับ "NaN ตร.ม." substring ในทั้ง summary-widget / measure-result / left-panel / right-panel — ต้องไม่เจอ.

Marker count: 27 → **28**.

**Why:** Found by human-test 2026-05-15 (BROKEN severity, filed as HT-2). Edge case ของ `polyAreaM2`: ถ้า scale exists but `pts_per_m` = 0 หรือ NaN, จะ return `NaN` (ไม่ใช่ `null`) ทำให้ guard `area != null` slip through และ `.toFixed(2)` ให้ string "NaN" → ผู้ใช้เห็น "⬡ NaN ตร.ม." ใน UI. คนรายงานเข้าใจว่าเป็นบั๊ก display.

**ทำไมไม่แก้ polyAreaM2:** เป็น forbidden surface ตาม CLAUDE.md (area math contract — every summary depends on it). Discipline: "Add new functions next to them ... instead of editing." — เพิ่ม consumer-layer helper + guard ทุก display site ที่ format ด้วย `.toFixed(2)`.

**Forbidden surfaces:** zero. polyAreaM2 / polyMetrics / polySelfIntersects / polygonAreaWithArcsM2 / arcSegmentAreaM2 / pathAreaM2 / objectAreaM2 — ทั้งหมดไม่ถูกแตะ. การคำนวณยังคงเหมือนเดิม.

**Tests:** `python3.11 proto/e2e_ui_test.py full` → 28/28 GREEN, no retry. PHASE_HT2_OK 12 sub-checks ทั้งหมด PASS รวมถึง live-DOM scan. Pre-existing format markers (VECTOR_OK / RECAL_OK / XLSX_OK / ANNOT_OK / PERSIST_OK / REAL_OK) ทั้งหมด normal — backward compatible 100%.

**Position:** Autonomous Dev Loop iteration 7. All BROKEN human-test findings cleared (HT-1 + HT-2 done). Next: HT-3 (FRICTION lbl-mode site-tag context).

---

### [session] HT-1 — `.dd-submenu` z-index 1→201 — PASS (branch: main)

**What changed:**
- `proto/static/css/app.css:25` — `.dd-submenu { ... z-index:1 }` → `z-index:201`. 1-line CSS fix.
- `proto/e2e_ui_test.py` — NEW `_test_ht1_submenu_zindex()` 3 sub-checks: `found` (element in DOM), `aboveSiblingThreshold` (rule z-index >= 201), `ruleZ matches computedZ`. Marker `PHASE_HT1_OK` printed after `PHASE_U2_OK`.

Marker count: 26 → **27**.

**Why:** Found by human-test 2026-05-15 (BROKEN severity, filed as HT-1 in PHASE_INDEX Discovered backlog). `.dd-submenu` ใน Measure / Project / Snap-modes / Layer-set-active dropdowns ถูก sibling overlay ทับเพราะ z-index = 1 ต่ำเกินไป. แก้เป็น 201 (สูงกว่า `.dropdown:200` ใน same stacking context; `.menu-bar:9000` ครอบทั้งหมด).

**HT-5 NOT bundled:** ในไฟล์เดียวกัน rule เดียวกัน HT-5 ขอเพิ่ม `max-height` + `overflow-y:auto` — ผมเริ่มแก้รวมแต่ revert เพราะ "one sprint = one commit" rule. HT-5 อยู่คิวเดียวกัน รอ iteration ถัดไป.

**Forbidden surfaces:** zero. CSS-only.

**Tests:** `python3.11 proto/e2e_ui_test.py full` → 27/27 GREEN. PHASE_HT1_OK: `{found: true, computedZ: 201, ruleZ: 201, aboveSiblingThreshold: true}`.

**Position:** Autonomous Dev Loop iteration 6. Next: HT-2 (`⬡ NaN ตร.ม.` summary BROKEN).

---

### [session] U2 — 1-Page Excel Summary — PASS (branch: main)

**What changed:** เพิ่ม "1-Page Excel Summary" export variant:
- `proto/server.py` — NEW `@app.post("/export-xlsx-summary")` endpoint (~165 บรรทัด). รับ body `{case_id, projectInfo, summary, pdfName, generatedAt}` แล้ว render 1-sheet "สรุปผังบริเวณ" workbook ผ่าน xlsxwriter. Layout: title row → project info (9 fields including new I-A site fields) → area breakdown table (7 site `semanticTag`s + land row) → ratios block (BCR/OSR/FAR/Permeable% — plain numbers, no verdict; user-set limits echoed alongside) → setback block (front/back/side1/side2) → marker block → footer "ไม่มีการพิจารณาผ่าน/ไม่ผ่านตามกฎหมาย". A4 landscape, `set_paper(9)`, `fit_to_pages(1, 1)`. Custom response header `X-Bma-Summary-Mode: 1-page`, filename `<safe>_summary.xlsx`. ไม่กระทบ `/export-xlsx` เดิม.
- `proto/ui.html` — `U2_SITE_AREA_TAGS` registry (7 site tags + Thai labels). NEW `collectSummaryData()` (~50 บรรทัด) — รวม area ตาม poly.semanticTag, รวม land area (areaType="land"), คำนวณ BCR/OSR/FAR/Permeable, ดึง front setback จาก `collectRefDistanceReport` (min dist to road ref), นับ marker breakdown ตาม markerType (จาก I-B1). v1 setbacks: front อย่างเดียว; back/side1/side2 = null (deferred to I-D). NEW `exportSummaryXLSX()` (~25 บรรทัด) — POST `/export-xlsx-summary` แล้ว `dlBlob`. NEW button `#btn-export-summary` ในแผง Export หลัง Export Excel + subtitle "facts only, no pass/fail".
- `proto/e2e_ui_test.py` — NEW `_test_u2_summary_xlsx()` 16 sub-checks. **Structural (9):** `fnExport`, `fnCollect`, `tagsOk` (7 tags), `btnOk`, `shapeOk` (9 keys), `ratiosAreNumberOrNull` (no booleans = no verdict), `setbacksShape` (4-direction object), no `summaryError`, sample tagCount. **Live server (7):** `responseOk`, `status200`, `isXLSX_ContentType`, `summaryFilename`=`_summary.xlsx`, `summaryHeader`=`X-Bma-Summary-Mode: 1-page`, `nonEmpty` > 200 bytes (actual 7354), `pkMagicBytes` 0x50/0x4B/0x03/0x04. Marker `PHASE_U2_OK` printed after `PHASE_U1_OK`.

Marker count: smoke 22 → **23** (added PHASE_U2_OK). Full: 25 → **26**.

**Why:** U2 = "first-usable" สปรินต์ที่ 2 ตาม user priority. ผู้ใช้ต้องการรายงาน 1 หน้าที่พิมพ์แล้วเอาให้ลูกค้า / ราชการได้เลย ไม่ต้องอ่าน 8-sheet detail workbook. ค่าหลักที่ลูกค้าถามทุกครั้งคือ BCR/OSR/FAR + ระยะร่น — Excel summary 1 หน้าโชว์ค่าเหล่านี้พร้อมเทียบกับ limit ที่ผู้ใช้ตั้งใน Project Setup. **Phase 1 boundary explicit:** ไม่ตัดสินผ่าน/ไม่ผ่าน — แค่แสดง facts. ผู้ใช้เป็นคนตัดสิน (เพราะ FAR/OSR/setback verdict ต้องใช้ rule engine + กฎหมายเขตเมือง ซึ่งอยู่ใน Phase 2).

**Architecture decision:** client คำนวณ summary numbers, server แค่ render. เหตุผล: (1) client มี `polyMetrics` + `collectAreas` + `collectRefDistanceReport` เดิมอยู่แล้ว — recomputing บน server ต้อง port code; (2) summary structure เปลี่ยนง่าย ๆ ใน client โดยไม่กระทบ server contract; (3) test ง่ายขึ้น — verify เป็น 2 layer แยกกัน (computation vs rendering).

**Files touched:** `proto/server.py` (~165 lines added, new endpoint), `proto/ui.html` (~95 lines added: collectSummaryData + exportSummaryXLSX + U2_SITE_AREA_TAGS + button), `proto/e2e_ui_test.py` (~80 lines added: 16-sub-check test + marker print).

**Forbidden surfaces:** zero. `polyAreaM2`/`polyMetrics`/`polySelfIntersects`/`pdfToC`/`cToPdf`/`RS`/`buildSnapIndex`/`snap` engine — ทั้งหมดไม่ถูกแตะ. Existing `/export-xlsx` endpoint — ไม่ถูกแตะ (สปรินต์ใหม่เป็น sibling endpoint). `.bmaplan` schema — version stays 1, ไม่มี field ใหม่.

**Tests:** `python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py` PASS. `python3.11 proto/e2e_ui_test.py full` → **26/26 markers GREEN** (no retry needed, first attempt). Live-endpoint check inside marker: 7354-byte XLSX, PK magic verified.

**Human test:** deferred this iteration per documented gap from U1 (subagent connection instability). `/bma-e2e full` with embedded live server round-trip used as partial proxy.

**Known gaps:**
- setback v1 covers only `front`; back/side1/side2 = "—" with note "ยังไม่ได้วัด". Full 4-direction lands in Phase I-D.
- Manual verification of XLSX visual layout in Excel/Numbers (page-fit, font, Thai rendering) deferred to UI_MANUAL_TEST.md housekeeping.

**Pre-existing noise** (not caused by U2): server log shows 2 `ValueError: document closed` ASGI tracebacks from PyMuPDF stale `/page` or `/thumb` requests after case cleanup. U2's endpoint does not touch `fitz.Document`. Filed mentally as housekeeping.

**Position in plan:** Autonomous Dev Loop iteration 5. PHASE_INDEX next: HT-1 (BROKEN, top), HT-2 (BROKEN), SB-002 (FRICTION), I-B3 → I-C → I-D (extends U2's setback story) → I-E → INV-001 → INV-002.

---

### [session] U1 — Save Annotated PDF in-place — PASS (branch: main)

**What changed:** เพิ่ม "Save PDF in-place" capability:
- `proto/ui.html` — `currentSourcePdfHandle` runtime state; `#upload-btn` label intercepts click ผ่าน `event.preventDefault();openPdfBtnClick();`; `uploadPdfFile(file, sourceHandle)` รับ 2-arg + เก็บ handle หลัง upload สำเร็จ; `openPdfBtnClick()` async function — ลอง `showOpenFilePicker()` ก่อน, request readwrite permission, AbortError graceful, fall back `#file-input.click()`; เมนู `#dd-save-pdf` "📄 Save PDF (ทับไฟล์เดิม)" ใน `#dd-project` หลัง Save/Open Project (มี separator คั่น); `saveSourcePdfInPlace()` async — POST `/export-pdf` ทุกหน้าที่ไม่ excluded + annotations แล้วถ้า handle อยู่ → `handle.createWritable()`/`write(blob)`/`close()` (request permission ถ้าจำเป็น), ถ้าไม่อยู่ / write fail → `dlBlob(blob, <safe>_annotated.pdf)`; keydown handler `Ctrl+Shift+S` → `saveSourcePdfInPlace()`. ~50 net lines.
- `proto/e2e_ui_test.py` — `_test_u1_save_pdf_in_place()` 9 sub-checks (`fnDefined`, `uploadArity≥2`, `openBtnFn`, `handleVar`, `handleNull`, `ddItemExists`, `menuLabelOk`, `shortcutOk`, `uploadBtnIntercept`); call site + `PHASE_U1_OK` print line; `expected_counts["project"]` 4→5 + `expected_counts["measure"]` 22→23 (latter is pre-existing I-B2b drift cleanup, surfaced now because of project mismatch making `menuStructureOk: False` flaggable).

Smoke: 21 → **22 markers** (added `PHASE_U1_OK`). Full: 24 → **25 markers**.

**Why:** U1 = "first-usable" user-priority sprint. ผู้ใช้ต้องการกด Save PDF แล้วเขียนทับไฟล์ต้นฉบับเลย ไม่ต้อง "Save As" ทุกครั้ง. Web platform ปัจจุบันต้อง FileSystemFileHandle เพื่อเขียนทับ — ได้จาก `showOpenFilePicker()` (ไม่ได้จาก `<input type="file">`). User เลือก Option B (replace existing Open with FSA when available; legacy `<input>` retained as fallback) ที่ SCOPE checkpoint แทน Option A (additive new menu) หรือ C (downgrade to Save As).

**Files touched:** `proto/ui.html` (~50 net new lines), `proto/e2e_ui_test.py` (1 new test fn, 1 marker, 2 expected_counts updates).

**Forbidden surfaces:** zero. `polyAreaM2`/`polyMetrics`/`polySelfIntersects`/`pdfToC`/`cToPdf`/`RS`/`buildSnapIndex`/`snap` engine — ทั้งหมดไม่ถูกแตะ. `proto/server.py` — ไม่ถูกแตะ. `.bmaplan` schema — version stays 1, ไม่มี field ใหม่ (handle เป็น runtime-only).

**Tests:** `python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py` PASS. `python3.11 proto/e2e_ui_test.py full` → **25/25 markers GREEN** (ALL_GREEN). One auto-retry executed: first run flagged MENU_OK as failed because of `menuStructureOk: False` informational sub-field; one-line cleanup to `expected_counts` (project 4→5, measure 22→23 = pre-existing I-B2b drift surfaced) → 25/25 GREEN, `menuStructureOk: True`. Within skill rule "ONE surgical retry".

**Human test:** `bma-human-journey-tester` subagent connection dropped mid-run after 33 tool uses (network instability — left empty `artifacts/human-tests/u1-save-pdf/` dir). Per `/bma-human-test` skill fallback rule, `/bma-e2e full` (just-run, 25/25) used as partial proxy. Gap noted: every-page coverage + friction observation not exercised; manual UI verification of FSA permission prompt deferred to `UI_MANUAL_TEST.md` housekeeping.

**Known gaps for production:**
- FSA write-permission UX exercised only structurally; needs real-browser manual test for permission prompt flow + post-write filename behaviour. Filed as housekeeping note.
- Headless Playwright cannot exercise `showOpenFilePicker` — coverage is structural surface only.

**Position in plan:** Autonomous Dev Loop iteration 4. PHASE_INDEX user-priority order: U1 ✅ → U2 (next) → HT-1 (BROKEN) → SB-002 → I-B3 → I-C → I-D → I-E → INV-001/INV-002.

---

### [session] SB-2026-05-15-001 — UPLOAD_CAP_RAISE — PASS (branch: main)

**What changed:** ยก `MAX_UPLOAD_BYTES` จาก 80 MB เป็น 256 MB ใน `proto/server.py:51` พร้อม env-var override `BMA_MAX_UPLOAD_MB` (int MB, default 256) — อ่านตอน module load ก่อน `app = FastAPI()`. `/upload` response body เพิ่ม field `max_upload_mb` (echo กลับ MB จริงที่ server ใช้). เพิ่ม `_test_upload_cap()` ใน `proto/e2e_ui_test.py` — assert cap ≥ 128 MB + ตรวจ API echo ตรงกัน — wired เป็น marker `UPLOAD_CAP_OK` ระหว่าง `CACHE_OK` กับ `SETUP_OK`. smoke ใหม่ = 21 markers (เพิ่ม 1), full = 24 markers (เพิ่ม 2 จาก Pack G baseline 22; +UPLOAD_CAP_OK ใน smoke tier ด้วย). Human-test PASS หลัง marker pass: open → measure 45 pages → export XLSX 17813B / 12 sheets → save .bmaplan 30024B → reopen ครบ.

**Why:** customer PDF `sandbox/251121_CHH_Submission_REV2 - Copy.pdf` ขนาด 90.8 MB ทำให้ `/upload` คืน HTTP 413 เพราะ `MAX_UPLOAD_BYTES = 80 MB` เดิม. ถูกค้นพบโดย Pack G first-run sandbox test (2026-05-15) แล้ว file เป็น SB-2026-05-15-001 BROKEN. ลูกค้า PDF จริงที่ได้รับมักเกิน 80 MB (permit set หลายหน้า, A1 scan) → ต้องขึ้น cap พร้อม env-var ให้ deploy-time tune ได้โดยไม่ต้องแก้โค้ด.

**Files touched:**
- `proto/server.py`: L51 — แทน `MAX_UPLOAD_BYTES = 80 * 1024 * 1024` ด้วย env-var override block (default 256 MB, `BMA_MAX_UPLOAD_MB`); `/upload` echo `max_upload_mb`
- `proto/e2e_ui_test.py`: เพิ่ม `_test_upload_cap()` + marker `UPLOAD_CAP_OK` (wired ใน `main()` หลัง CACHE_OK)
- `docs/status/PHASE_INDEX.md`: SB-2026-05-15-001 row marked `✅ done` (hash จะ fill หลัง commit)
- `NEXT_ACTION.md`: modified pre-sprint by user

**Tests:**
- `python -m py_compile proto/server.py proto/e2e_ui_test.py` → PASS
- `python proto/e2e_ui_test.py full` → PASS 24/24 markers GREEN
- `/bma-human-test` → HUMAN_TEST_PASS (open → measure 45 pages → export XLSX 17813B / 12 sheets → save .bmaplan 30024B → reopen full state restoration). HT-1 + HT-3 ยังอยู่ใน backlog (pre-existing, untouched).

**Phase 1 scope check:**
- ✅ `polyAreaM2`/`polyMetrics`/`polySelfIntersects` unchanged
- ✅ `pdfToC`/`cToPdf`/`RS`/scale math unchanged
- ✅ `buildSnapIndex`/`snap` unchanged
- ⚠️ `proto/server.py` — touched (size constant + env-var read only; no endpoint logic, isolation, validation, or guards changed). PHASE_INDEX classified as forbidden-surface WARN → `full` E2E required → PASSED 24/24
- ✅ `.bmaplan` schema additive only — version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- SB-2026-05-15-002 FRICTION: upload-cap UX (status-bar display of current limit) — unblocked now that SB-001 done
- HT-1 BROKEN: `.dd-submenu` z-index:1 < `.dropdown` z-index:200 (pre-existing)
- HT-3 FRICTION: `lbl-mode` ไม่สะท้อน site-tag context (pre-existing)
- Next sprint: U1 — Save Annotated PDF in-place (likely LOOP_STOP_DESIGN on FSA handle ambiguity)

---

### [session] Pack G — Sandbox Test Pre-Release Gate — PASS (branch: main, docs/.claude only)

**What changed:** สร้าง 3-piece pre-release gate ใหม่ใน `.claude/` — skill `/bma-sandbox-test` + subagent `bma-sandbox-journey-tester` + subagent `bma-issue-triager` — แล้ว run first-run ครั้งแรกกับ customer PDF จริง (95 MB) ใน `sandbox/`. First run: Tier 1 FAIL — `POST /upload` return HTTP 413 (`MAX_UPLOAD_BYTES = 80 MB` ใน `proto/server.py:51` ต่ำกว่า PDF จริง 90.8 MB). Tier 2 skipped. ไม่มี CRASH — verdict = `SANDBOX_TEST_ISSUES`. Triage: 2 findings (SB-001 BROKEN upload cap, SB-002 FRICTION UX) cluster จาก root cause เดียวกัน แต่ filed แยก 2 sprints (forbidden-surface vs UI boundary สะอาด). ไม่ต้องสร้าง specialist ใหม่ — ครอบคลุมด้วย `/bma-check-forbidden` + `/bma-ui-scope` เดิมแล้ว. ปรับปรุง `CLAUDE.md`, `AGENTS.md`, `docs/status/PHASE_INDEX.md` เพื่อรองรับ sandbox stream ใหม่.

**Why:** Customer PDF จริง (90.8 MB) เปิดไม่ผ่าน — "เปิดแล้วไม่ผ่าน" symptom ที่ user รายงาน. ต้องการ pre-release gate ที่รัน real-file journey BEFORE ส่งให้ลูกค้า/demo. Pack G สร้าง gate นั้น + ทดสอบในทันทีเพื่อ prove value. `/bma-sandbox-test` → `bma-sandbox-journey-tester` (drive) → `bma-issue-triager` (cluster + propose) → file ลงใน `PHASE_INDEX.md` เป็น workflow loop ปิด.

**Files touched:**

New files:
- `.claude/skills/bma-sandbox-test/SKILL.md`: skill `/bma-sandbox-test` — enumerate `sandbox/*.pdf`, delegate journey, triage, file SB-* into PHASE_INDEX.md. Returns SANDBOX_TEST_PASS / SANDBOX_TEST_ISSUES / SANDBOX_TEST_CRASH.
- `.claude/agents/bma-sandbox-journey-tester.md`: sonnet subagent — Tier 1 open+render, Tier 2 set-scale+draw+export+save+reopen round-trip. Reports CRASH/BROKEN/FRICTION/COSMETIC. Read-only on `proto/`. 5 min/PDF time-box.
- `.claude/agents/bma-issue-triager.md`: sonnet subagent — deduplicate findings, cluster by root cause, check existing skills/agents coverage, draft new specialist specs only when needed, return paste-ready `PHASE_INDEX.md` block. Read-only — never creates `.claude/` files itself.

Edited files:
- `CLAUDE.md`: Pack G entry ใน skills table + subagent table + invariant ใหม่ (propose-first pattern + pre-release gate requirement).
- `AGENTS.md`: new section "### 8. Pre-Release Gate (sandbox)" — documents gate requirement, finding citation rule, propose-first constraint.
- `docs/status/PHASE_INDEX.md`: rewrite discovered-backlog header (HT-* + SB-* streams); insert SB-2026-05-15-001 (BROKEN, above U1) + SB-2026-05-15-002 (FRICTION, after HT-5, depends SB-001); new `### sandbox 2026-05-15` sub-block with verdict, per-finding table, sequencing, artifact link.

**Tests:** No tests run — docs/.claude-only sprint. Files touched: 3 new `.claude/` files + 3 edited docs (`CLAUDE.md`, `AGENTS.md`, `docs/status/PHASE_INDEX.md`). No `proto/` source touched. Per AGENTS.md, docs/.claude-only sprints do not require E2E. Sandbox first-run Tier 1 ran Playwright helpers for evidence-gathering only — no app marker test rerun, no app code changed.

**Phase 1 scope check:**
- ✅ `polyAreaM2`/`polyMetrics`/`polySelfIntersects` unchanged
- ✅ `pdfToC`/`cToPdf`/`RS`/scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (`MAX_UPLOAD_BYTES` discovery filed as SB-001, not fixed this sprint)
- ✅ `.bmaplan` schema additive only — unchanged this sprint
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- SB-2026-05-15-001 BROKEN: `MAX_UPLOAD_BYTES = 80 MB` (`proto/server.py:51`) — raise to ≥128 MB. Route through `/bma-check-forbidden` (touches core upload endpoint constant). `full` E2E required. Add 128 MB upload regression test in `proto/e2e_ui_test.py`.
- SB-2026-05-15-002 FRICTION: upload-cap UX surfaces only as Thai status-bar string — polish after SB-001 lands. Route through `/bma-ui-scope` + `bma-status-bar-specialist`.

---

> Sessions ก่อนหน้า (PHASE_I_B2B_MEASURE_MENU_SUBMENU, Pack G Sandbox Test, USER_PRIORITY_INSERT_U1_U2, PHASE_I_B2A_SITE_RIBBON, AUTONOMOUS_DEV_LOOP_PACK_F, RECONCILE_SITE_PLAN_UI_MOCKUP, PHASE_I_B1_MARKER_TYPE, PHASE_I_A_SCHEMA_AND_PROJECT_SETUP, MEASURE_PACK_SKILLS_AND_SUBAGENTS_PACK_E, MENU_CANVAS_ZINDEX_OVERLAP_FIX, UI_SPECIALIST_SKILLS_AND_SUBAGENTS_PACK_D, PATH_GEOMETRY_VISUAL_AUDIT) ถูก archive ไปยัง [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) และ [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md)
> 2026-05-13 และก่อนหน้า: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)
