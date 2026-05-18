# PHASE_INDEX.md — Canonical Phase & Sprint Roadmap

> **The Autonomous Dev Loop (`/bma-dev-loop`) reads the next `queued` sprint from here and writes status back.**
> Single source of truth for what is done / queued / discovered. Created 2026-05-14 to fix the scattered-phase problem
> (phase letters had been used loosely across `plans/`, `LATEST_STATUS`, and design docs with no master list).

## LOOP_DONE 2026-05-18 — UI redesign complete (15 sprints shipped in one day)

All 15 HT-12..HT-15 sprints **shipped and tested**. 52 smoke markers GREEN (was 41 at start of day, +11 new markers all PASS). 2 pre-existing failures unchanged (HT-8D1.placeholderHasMessage, HT-8D5A.footerHas2Buttons — to file as separate cleanup sprint). 22 commits total. Zero forbidden-surface touches across all sprints.

**Completed today (2026-05-18):**
- HT-12a-i: Top menu redesign (density picker, File/View/Page/Scale/Project menus wired, Workspace ribbon tab hidden, panel collapse buttons)
- HT-13a-d: Measure ribbon polish (Helpers section + Polygon dropdown popover — critical UX for sub-mode discoverability)
- HT-14a-c: Right panel content (List/Props/Summary all functional — placeholders closed)
- HT-15a: Sheets tab verified

`/loop /bma-dev-loop` would halt with LOOP_DONE — queue exhausted.

**Update 2026-05-18 evening:** `INV-2026-05-18-001 Page Setup Redesign` added to queue (status `queued`) after `/bma-invent` GO checkpoint. `/bma-dev-loop` next pickup.

Previously (LOOP_DONE 2026-05-17): 10 sprints landed in one session + HT-6 (`ecb44d4`) + INV-2026-05-17-001 (`023b988` freeform). Phase 1 = complete (all Phase I sub-sprints + INV-001 + INV-002 + dev-website + CIRCLE_RENDER + HT-6 + INV-freeform). Full 44/44 GREEN.

## Canonical UI Mockup (target design)

**File:** `proto/sandbox/mockup-top-menu-redesign.html` (2026-05-18, derived from `mockup-interactive-full.html` 2026-05-17 22:24)

**Key changes vs live app:**
1. **Top menu = 9 dropdowns** (File / Edit / View / Page / Scale / Project / Measure / Annotate / Help) + density picker
2. **Workspace ribbon tab REMOVED** — items distributed into menu dropdowns
3. **Tab strip = 3 tabs** (📐 วัด / 📝 Annotate / 📍 Site Plan disabled-default)
4. **Measure ribbon = 7 sections** with rstack 2×2 for Tool/Helpers/Edit, HERO for Set Scale + Polygon
5. **Polygon dropdown popover** — sub-modes hint (A=Arc / Alt=Freeform / Shift=Ortho / O=Opening)
6. **Left panel = 3 tabs** (📑 Pages / 📚 Sheets / 🌳 Tree) — Layers moved to right (HT-8d-1 ✅ done)
7. **Right panel = 5 tabs** (📋 List / 🗂 Layers ★default / 🔧 Props / 📊 Summary / 💬 Notes)
8. **Panel collapse buttons** (◀ / ▶ on each panel edge)
9. **Density picker** in menu bar (Compact / Comfortable / Spacious) + CSS variables drive ribbon/button sizing
10. **Status bar** unchanged structurally — 7 fields

## Phase overview

| Phase | What | Status |
|---|---|---|
| A–F | Mockup V3 Alignment (6 implementation steps of one plan) | ✅ done |
| G | Menu Wiring + Measure/Layer Power-up | ✅ done |
| H.0 | 45° angle lock | ⛔ deferred — blocks the 2h rule (มร.55 ข้อ 44) |
| H.1 | Path Geometry (unified line/cubic model) | ✅ done |
| I | Site Plan Measurement (I-A … I-E) | ✅ done (I-A through I-E complete 2026-05-17) |
| INV-001 | Arc-polygon hybrid measurement | ✅ done `b89e206` |
| INV-002 | Unified Settings/Preferences modal | ✅ done `b6856df` |
| dev-website | Static docs site at `/static/docs/` | ✅ done `1bf61ca` |
| CIRCLE_RENDER | Analytic circle/ellipse render | ✅ done `1bf61ca` |

Project = **Phase 1** (Raster PDF Measurement). Phase 2+ (legal checker / OCR / AI / Rule Engine / FAR-OSR verdict) is permanently out of scope.

## Active sprint queue

> The loop picks the **topmost `queued`** item whose `depends-on` is satisfied.

| id | name | scope skill | region / category | status | depends-on |
|---|---|---|---|---|---|
| I-A | Site Plan schema + Project Setup | — | measure / schema | ✅ done `984eb7e` | — |
| I-B1 | markerType additive field | — | measure / schema | ✅ done `c38c3e6` | I-A |
| I-B2a | Site Plan ribbon group + shared handlers | `/bma-ui-scope` | ribbon | ✅ done `b9f9132` | I-B1 |
| SB-2026-05-15-001 | `/upload` 413 for real permit PDFs ≥ 80 MB — raised `MAX_UPLOAD_BYTES` 80 MB → 256 MB + env-var `BMA_MAX_UPLOAD_MB`; new `UPLOAD_CAP_OK` marker; smoke 21/21 + full 24/24 GREEN | `/bma-check-forbidden` | server / upload | ✅ done `fabc2e9` | — |
| U1 | Save Annotated PDF in-place — Option B (FSA-first Open). New `currentSourcePdfHandle`, `openPdfBtnClick()` FSA-first, `saveSourcePdfInPlace()`, `#dd-save-pdf` menu item + Ctrl+Shift+S, `PHASE_U1_OK` 9 sub-checks. Zero forbidden-surface, zero schema, zero server. | `/bma-ui-scope` + `/bma-check-forbidden` | menu / export (client-only) | ✅ done `2101dfe` | — |
| U2 | 1-Page Excel Summary — NEW `/export-xlsx-summary` endpoint + client `collectSummaryData()` + Export panel button. 1-sheet A4 landscape `fit_to_pages(1,1)`. Aggregates BCR/OSR/FAR/Permeable (plain numbers, no verdict) + front-setback + marker counts. Phase 1 boundary: facts only. `PHASE_U2_OK` 16 sub-checks (9 structural + 7 live server). Setback v1 = front only (back/side1/side2 deferred to I-D). Zero forbidden-surface, zero schema. | `/bma-measure-scope` (export-impact) + `/bma-check-forbidden` | export (server `/export-xlsx-summary` + client menu) | ✅ done `4bcacc6` | I-A |
| I-B2b | Measure menu submenu (site plan) | `/bma-ui-scope` | menu-bar | ✅ done `5c76708` | I-B2a |
| HT-1 | `.dd-submenu` z-index 1→201 — 1-line CSS fix in `proto/static/css/app.css:25`; submenu now stacks above sibling overlays in dropdowns. PHASE_HT1_OK marker 3 sub-checks. | `/bma-ui-scope` | menu-bar (CSS) | ✅ done `e21ca98` | — |
| HT-2 | `⬡ NaN ตร.ม.` display guard — NEW `fmtAreaM2`/`fmtDistM` consumer-layer helpers + `Number.isFinite()` guards at 10 display sites. polyAreaM2 untouched. PHASE_HT2_OK 12 sub-checks incl. live-DOM scan. | `/bma-measure-scope` | summary-widget + canvas-ui | ✅ done `acd8636` | — |
| HT-3 | `lbl-mode` site-tag context — extracted `updateModeLabel(m)` helper + `SITE_TAG_THAI_LABELS` map; shows `วัดพื้นที่ ⬡ (ผังบริเวณ — ปกคลุมอาคาร)` when site tool active; marker tools get suffix too. PHASE_HT3_OK 7 sub-checks. | `/bma-ui-scope` | status-bar | ✅ done `0900e0a` | I-B2a |
| HT-4 | Name panel dismissal paths — NEW `autoCloseNamePanel()` helper + 3 dismissal paths: click outside (300ms grace, auto-confirm if value), `loadPage()` auto-commit, global Esc proper `cancelName()`. PHASE_HT4_OK 9 sub-checks. | `/bma-ui-scope` | modal/dialog | ✅ done `a6973ef` | — |
| HT-5 | `.dd-submenu` overflow on short viewports — CSS-only += `max-height:calc(100vh - 120px); overflow-y:auto; overflow-x:hidden; scrollbar-width:thin`. PHASE_HT5_OK 3 sub-checks. | `/bma-ui-scope` | menu-bar (CSS) | ✅ done `89074cb` | — |
| SB-2026-05-15-002 | Upload-cap error UX — pre-flight modal + cold-start hint + `currentUploadCapMB` from `/upload` echo + 413 suggestions. `SB002_UPLOAD_UX_OK` 8 sub-checks. | `/bma-ui-scope` | upload UI / status bar / modal | ✅ done `33577b7` | SB-2026-05-15-001 |
| I-B3 | Properties panel site fields (height + draw-then-classify) — `isBuildingTag` helper + `buildingHeight_m` input + 7 site tags in Semantic Tag dropdown on site pages. `PHASE_I_B3_OK` 10 sub-checks. | `/bma-ui-scope` | left-panel | ✅ done `c011c4e` | I-B1 |
| I-B4 | Site stepper widget — `#site-stepper` 6-step advisory; `updateSiteStepperUI`. `PHASE_I_B4_OK` 10 sub-checks. | `/bma-ui-scope` | left-panel | ✅ done `91fede9` | I-B1 |
| I-C | Summary "ผังบริเวณ" 5th tab — `updateSiteplanTab()` renders `collectSummaryData()` inline; BCR/OSR/FAR/Permeable + per-tag + markers + setback + Phase 1 footer note. `PHASE_I_C_OK` 10 sub-checks. | `/bma-measure-scope` | summary-widget | ✅ done `a490c1e` | I-B3 |
| I-D | 4-direction setback + compass — `landEdgeRole` on edges; `computeEdgeSetback`; `#canvas-compass` SVG; `northAngle` in pageTags. `PHASE_I_D_OK` 10 sub-checks. | `/bma-measure-scope` | summary-widget + canvas-ui | ✅ done `dc96f62` | I-C |
| I-E | Building-to-building distance + wallEdges — `WALL_EDGE_TYPES` catalog; `computeBuildingPairsForPage`; "ระยะระหว่างอาคาร (2h pre-check)" in siteplan tab. `PHASE_I_E_OK` 9 sub-checks. | `/bma-measure-scope` | canvas-ui + schema | ✅ done `504b993` | I-D |
| INV-2026-05-15-001 | Arc-polygon hybrid area measurement — three-click inline arc during polygon draw. `polyMetricsAnyShape` shim. `ARC_POLYGON_OK` 7 sub-checks (err=0.000000%). Zero forbidden-surface edits. Schema additive. | `/bma-measure-scope` (sub-area: generator + ux) | measure / generator + ux | ✅ done `b89e206` | H.1 ✅ |
| INV-2026-05-15-002 | Unified Settings/Preferences modal (Approach A) — `bmaPlan.settings.v1`; `getPref`/`setPref`; `migrateFromLegacy`; 4-tab modal; `Ctrl+,`; bad-JSON + wrong-version safety. `SETTINGS_OK` 13 sub-checks. Zero forbidden-surface, zero `.bmaplan` schema. | `/bma-ui-scope` (modal region) | UI / modal + preferences layer | ✅ done `b6856df` | — |
| HT-6 | Live arc guideline preview during arc-mode draft — when `guidePoint` set and `mArcDraft.pending`, draws dashed arc from last vertex curving through through-point to cursor. ~15 LOC in `redraw()` draft block. `computeArcEdge` reused. `PHASE_HT6_OK` 4 sub-checks. full 42/42 GREEN. Zero forbidden-surface edits. Source: user-test 2026-05-17 "ขาดเส้น guideline เหมือนของเส้นตรง". TEST-H skipped (render-only branch; journey tester does not exercise arc-mode). | `/bma-measure-ux` | measure / render | ✅ done `ecb44d4` | INV-001 ✅ |
| HT-7 | Per-page scale enforcement (hybrid hard-block + auto-redirect) — `_SCALE_REQUIRED_MODES` set + `_scaleGateBeforeMode()` interceptor in `setMode()`. Hard-block when no scale + auto-flip to calib + bounce-back to original mode. `PHASE_HT7_OK` marker. | `/bma-measure-ux` | measure / mode-gate | ✅ done `a3e45c5` | — |
| HT-8 | Drawing-tool menu clarity — SUPERSEDED. Split into HT-8a/b/c/d after 2026-05-17 mockup design session at `proto/sandbox/mockup-interactive-full.html`. User feedback: Shape section unused (remove), Set Scale missing from Measure tab (move from Workspace), Hard/Soft TH unclear, Sheets concept unwanted, Layers should be RIGHT not LEFT, Comment HERO unnecessary, Cloud needs preview guide, every annot must be editable. Subagents (`bma-right-panel-specialist` + `bma-summary-widget-specialist`) deep-dived Layers + Summary, found 4 critical Summary bugs to fix in HT-8d. | — | — | superseded — see HT-8a/b/c/d | — |
| HT-8a | Tab Strip 4 tabs + ribbon restructure — tabs (📐 วัด / 📝 Annotate / 📍 ผังบริเวณ / ⚙ Workspace, ผังบริเวณ disabled-default dbl-click to enable). Measure tab = Select + Polygon HERO (+ Opening/Land/Building) + Lines (Dist/Path/Ref) + Marker (North/Parking) + Set Scale HERO (moved from Workspace) + Helpers (use existing) + Edit mini-stack. **Remove Shape section** (Rect/Circle/Ellipse unused per user). Status bar prefix `[📐 วัด]` colored. `PHASE_HT8A_OK` 16 sub-checks. full 45/45 GREEN. Zero forbidden-surface. Mockup ref: `proto/sandbox/mockup-interactive-full.html`. | `/bma-ui-scope` → `/bma-ui-ribbon` + `/bma-ui-status` | UI / ribbon + status-bar | ✅ done `ef0944b` | HT-7 ✅ |
| HT-8b | Foxit 3 ribbon patterns + TH labels — Pattern 2 (label-2line) applied to 7 site buttons; Pattern 3 mini-stack CSS infrastructure + marker grid 4×2; HERO confirmed on Polygon + Set Scale (from HT-8a). TH labels verified พื้นแข็ง/สนามหญ้า. `PHASE_HT8B_OK` 11 sub-checks. full 46/46 GREEN. List→รายการ, Tree→รายการบนหน้า labels are right/left panel work (HT-8c/d). | `/bma-ui-scope` → `/bma-ui-ribbon` | UI / ribbon | ✅ done `a8d4e6e` | HT-8a ✅ |
| HT-8c | Left panel tab clarity renames — "Sheets"→"📑 หน้า", "Objects"→"🌳 รายการบนหน้า", "Properties"→"🔧 Properties". Pages-by-tag grouping (existing functionality) preserved — user confusion was about the English label only. Properties stays in left panel until HT-8d moves it right. `PHASE_HT8C_OK` 8 sub-checks. full 47/47 GREEN. | `/bma-ui-scope` → `/bma-ui-panel` | UI / left-panel | ✅ done `6d1b289` | HT-8a ✅ |
| HT-8d | Right panel 4 tabs + Summary bugs + Layers move — SUPERSEDED. Split into HT-8d-1/2/3/4/5 below (was too broad for one iteration). | — | — | superseded — see HT-8d-1..5 | — |
| HT-8d-1 | Right panel tab-strip structure — 4 tabs above existing content. Layers default-active showing buildRightPanel output unchanged; others show placeholders pointing to HT-8d-2..5. localStorage persist. `PHASE_HT8D1_OK` 11 sub-checks. full 49/49 GREEN. | `/bma-ui-scope` → `/bma-ui-panel` | UI / right-panel | ✅ done `10cb6ec` | HT-8a ✅ |
| HT-8d-2 | Summary widget in right panel + auto-refresh — `_renderSummaryInPanel()` builds 5 sections (hero Net GFA / Land+ratios / semanticTag breakdown / object counts / warnings) reusing collectAreas + phase1Warnings + collectSummaryData. `updatePageSummary` now calls both `_refreshPanelSummaryIfActive` and `updateSummaryWidget` so live mutations refresh both the new panel view AND the legacy floating widget. HT-8d-3 (auto-refresh fix) folded in. Floating widget DOM kept for legacy compat. Phase 1 boundary preserved (no verdict color). `PHASE_HT8D2_OK` 10 sub-checks. full 50/50 GREEN. | `/bma-measure-scope` (summary) | UI / summary + reactive | ✅ done `8fd9629` | HT-8d-1 ✅ |
| HT-8d-3 | Summary auto-refresh — **MERGED into HT-8d-2** (`8fd9629`). The 1-line fix was naturally bound to the panel renderer wiring. `updatePageSummary` now calls `_refreshPanelSummaryIfActive` AND `updateSummaryWidget` at the end. | — | — | ✅ merged with HT-8d-2 | HT-8d-2 |
| HT-8d-4 | Warnings click-to-jump — `navigateToWarning(pg, objId)` helper wired on both legacy widget `_swBuildWarn` AND new panel `_renderSummaryInPanel`. loadPage(pg) + lookup object by id across (poly/opening/line/ref/parking) + select + redraw. Status bar reports outcome. `PHASE_HT8D4_OK` 7 sub-checks. full 51/51 GREEN. | `/bma-measure-scope` (summary) | summary / navigation | ✅ done `cc6bf63` | HT-8d-2 ✅ |
| HT-8d-5 | Layers polish — SUPERSEDED. Split into HT-8d-5a/b/c/d (8 features too broad for one iteration). | — | — | superseded — see HT-8d-5a..d | — |
| HT-8d-5a | Layers polish wave 1 — Hide-Others/Show-All footer + canvas top-bar layer swatch indicator + lock-while-draw gate. `_layerLockGateBeforeMode` hooked into setMode after scale gate. Annotation modes bypass. `PHASE_HT8D5A_OK` 8 sub-checks. full 54/54 GREEN. | `/bma-ui-panel` (right) | UI / layers | ✅ done `917ac23` | HT-8d-1 ✅ |
| HT-8d-5b | Layers polish wave 2 — search input (filter by name/slug) + per-layer color picker (swatch becomes <input type=color>). Focus preserved across re-render. `setLayerColor` writes to per-page object + saves + redraws. `PHASE_HT8D5B_OK` 8 sub-checks. full 55/55 GREEN. | `/bma-ui-panel` (right) | UI / layers | ✅ done `df8172c` | HT-8d-5a ✅ |
| HT-8d-5c | Layers polish wave 3 — move-up/down arrow buttons + right-click rename (oncontextmenu → renameLayer). Real drag-reorder deferred (buttons are simpler + more reliable). Duplicate/delete deferred to HT-8d-5d if needed. `PHASE_HT8D5C_OK` 10 sub-checks. full 56/56 GREEN. | `/bma-ui-panel` (right) | UI / layers | ✅ done `9063a0b` | HT-8d-5b ✅ |
| HT-8d-5d | Layers polish wave 4 — `+ New Layer` button + creation modal with 6-preset dropdown (building/land/deduction/reference/markup/custom). `addCustomLayer` writes to per-page layers[] with `semanticTagPreset` hint. Schema additive. `PHASE_HT8D5D_OK` 13 sub-checks. full 57/57 GREEN. **LAST sprint of HT-8d-5 series.** | `/bma-ui-panel` (right) | UI / layers | ✅ done `4d63323` | HT-8d-5c ✅ |
| HT-9 | Rubber-band preview for all 2-click tools — guidePoint condition extended to include rect/circle/ellipse/ann_rect/ann_highlight/ann_circle/ann_arrow/ann_cloud + special calib branch (calibPts.length===1). redraw() got 2 new branches: shape preview (dashed outline) for shape modes, calib mid-flow guide line + live distance label for Set Scale between click 1 and click 2. Ann_cloud uses the existing path-style segment guide (sufficient for Phase 1). `PHASE_HT9_OK` 10 sub-checks. full 48/48 GREEN. Zero forbidden-surface (render-only). | `/bma-measure-ux` | measure + annotate / preview rendering | ✅ done `b574f7f` | HT-8a ✅ |
| HT-10 | Options modal additions — extends INV-002 settings: density (Compact/Comfortable/Spacious, default Comfortable), hide-left-panel toggle, hide-right-panel toggle. CSS `body.density-X` overrides .rbtn sizing. New `applyLayoutPrefs()` wired into loadPrefs + applySettingsDraft. Persists via `bmaPlan.settings.v1` (additive). `PHASE_HT10_OK` 10 sub-checks. full 52/52 GREEN. | `/bma-ui-scope` (modal region) | UI / modal + ribbon CSS | ✅ done `acee13c` | HT-8b ✅ |
| HT-11 | Annotation edit + individual delete — `annotationHitTest` + `deleteAnnotation` + edit modal (text + color + 🗑) for all 7 ann types. dblclick on canvas → opens modal. Right-panel List row hover ✎/🗑 deferred to HT-8d list-tab sprint. `PHASE_HT11_OK` 10 sub-checks. full 53/53 GREEN. Zero forbidden-surface (schema additive — reuses existing text/color fields). | `/bma-ui-scope` → `/bma-ui-panel` | UI / annotation | ✅ done `01d923c` | HT-8d-1 ✅ |
| INV-2026-05-17-001 | Freeform area measurement (Approach D — Alt sub-mode of polygon) — In polygon mode, holding `Alt` during `mousedown` flips to streaming freehand sub-mode with distance-bin sampling (≥ 6 px). Release Alt → return to click-vertex mode (mixed click+drag in same polygon). `Shift`/`Ctrl` during draw → live tolerance modulation (badge on canvas). `Enter` → RDP-decimate + `polyAreaM2` + close. New helper `rdpSimplify` (~25 LOC, inline). Reuses existing `polyAreaM2` + `polySelfIntersects` unchanged. Output is `obj.type='polygon'` + optional `obj.freeform={tolerance,originalCount,freehandSegments}`. `PHASE_FREEFORM_OK` marker (6 sub-checks: closed-form area err < 5%, decimation reduces 500→≤150, save/reload round-trip, self-intersection detection, ≤ 1 s draw, mixed-mode coexistence). Carry-over risks: Alt-mid-stroke guard, snap bypass during freehand, touch input deferred to iPad track. **Zero forbidden-surface edits. Schema additive only.** Est ~150 LOC. Source: `docs/invent/freeform-area.md` + `proto/sandbox/invent-freeform-area.html` (spike PASS 6/6 first attempt, err = 1.22%). User GO 2026-05-17. | `/bma-measure-scope` (sub-area: ux + state-machine) | measure / ux + generator | ✅ done 023b988 | INV-001 ✅ |
| HT-12a | **Density picker in menu bar** — `.density-picker` DOM (3 buttons compact/comfortable/spacious) + `setDensityFromMenu()` bridge to existing HT-10 `PREFS.layout.density` infrastructure + extended `applyLayoutPrefs()` to sync picker button active state (works for boot, modal save, and direct menu click). `.density-picker` CSS (margin-left:auto, button states inc. .active). Adjusted `.menu-item.phase-badge` to give up `margin-left:auto` to density-picker. **Scope narrowed from original sprint card** — most of the "menu bar 9-item shell" work is already in live (`Project`/`Scale`/`Page`/`Measure`/`Object`/`Layer`/`Annotate` dropdowns exist via HT-8 series). HT-12a delivered the only missing piece: visible density toggle. Marker `PHASE_HT12A_OK` 10/10 PASS. smoke 42/42 GREEN. Zero forbidden-surface. | `/bma-ui-scope` → `/bma-ui-menu` | UI / menu bar | ✅ done `e65adc1` | — |
| HT-12b | **File menu wired** — activated dead `File` menu-item with `onclick="toggleMenu(this)"` + inline `#dd-file` dropdown with 6 items: Open PDF (openPdfBtnClick), Open Project (openProjectBtnClick), Sample PDF (openSamplePdf), Save Project (saveProject), Save Project As (saveProjectAs), Save Annotated PDF (saveSourcePdfInPlace). All onclick dispatchers reference existing handlers. Co-exists with Project menu items (no removal yet — HT-12g handles that). Recent submenu deferred. Close item deferred (no `closePdf` handler exists). PHASE_HT12B_OK 11/11 PASS. smoke 43/43 GREEN. Zero forbidden-surface. | `/bma-ui-menu` | UI / menu bar | ✅ done `cf910d8` | HT-12a ✅ |
| HT-12c | **View menu wired** — activated dead `View` menu-item with onclick=toggleMenu + #dd-view dropdown (10 items + Density submenu): Zoom In/Out (adjustZoom), Fit to Window (fitToWindow), Actual Size (setActualSize new), Rotate L/R (rotatePage), Toggle Left/Right Panel (toggleLeftPanel/toggleRightPanel new), UI Density submenu (setDensityFromMenu), Settings (openSettings). 3 new helpers bridge to PREFS.layout.* (HT-10). **Fit Golden φ deferred** (mockup-only experimental feature, no live impl). PHASE_HT12C_OK 15/15 PASS. smoke ALL GREEN. **Discovered:** pre-existing failures PHASE_HT8D1_OK.placeholderHasMessage and PHASE_HT8D5A_OK.footerHas2Buttons (NOT regressions from HT-12c — to file separately). Zero forbidden-surface. | `/bma-ui-menu` | UI / menu bar | ✅ done `6cad87e` | HT-12a ✅ |
| HT-12d | **Page menu expanded** — Page menu already existed (Prev/Next/Rotate). Added: First/Last (loadFirstPage/loadLastPage new), Page Setup (reorganized item), Set Page Tag submenu via setPageTagCurrent (new, 5 items site/plan/elev/section/none), Toggle Exclude via toggleExcludeCurrentPage (new, bridges to toggleExcludePage), Set North / Compass (setMode('north')). PHASE_HT12D_OK 14/14 PASS. smoke ALL green (same 2 pre-existing failures unchanged). Zero forbidden-surface. | `/bma-ui-menu` | UI / menu bar | ✅ done `694bc59` | HT-12a ✅ |
| HT-12e | **Scale menu verified** — No DOM change (Scale menu already had 7 items from prior sprints: Set Scale / Scale Manager / Verify / Reset / Status / Show Line / Warning). PHASE_HT12E_OK 8/8 marker added to lock contract. Zero forbidden-surface. | `/bma-ui-menu` | UI / menu bar | ✅ done `b12ab52` (bundled with HT-12f) | HT-12a ✅ |
| HT-12f | **Project menu extended** — Added 6 Export items to existing Project dropdown (after Save PDF separator): Export XLSX (exportXLSX), Export XLSX Summary (exportSummaryXLSX), Annotated PDF current/all (exportCurrentPageAnnotatedPDF/exportAllPagesAnnotatedPDF), Export CSV (exportCSV), Export JSON (exportJSON). Existing items preserved. PHASE_HT12F_OK 12/12 PASS. Zero forbidden-surface. | `/bma-ui-menu` | UI / menu bar | ✅ done `b12ab52` | HT-12a ✅ |
| HT-12g | **Workspace ribbon tab hidden** — Pragmatic implementation: `style="display:none"` on workspace tab (not full DOM delete) to preserve (a) 4 existing E2E tests (HT-8a series) that call `switchRibbonTab('workspace')` programmatically, and (b) 13 critical element IDs inside ribbon-workspace that are JS-referenced (file-input, proj-input, page-lbl, zoom-val, rot-badge, btn-prev/next, btn-setup, etc.). `_restoreRibbonTab` updated to fall back to 'measure' if saved 'workspace'. ribbon-tab-content div untouched. User sees 3-tab ribbon. PHASE_HT12G_OK 6/6 PASS. HT-8A_OK preserved. Zero forbidden-surface. | `/bma-ui-scope` → `/bma-ui-ribbon` + `/bma-ui-menu` | UI / ribbon + menu | ✅ done `db2ddd7` | HT-12b ✅ + HT-12c ✅ + HT-12d ✅ + HT-12e ✅ + HT-12f ✅ |
| HT-12h | **Density picker behavior** — chain already complete via HT-10 (CSS classes + applyLayoutPrefs) + HT-12a (setDensityFromMenu bridge). Marker PHASE_HT12H_OK 6/6 locks the end-to-end contract (click → body class → CSS cascade → button sizes → persist). | `/bma-ui-scope` | UI / menu + CSS vars | ✅ done `4ecef2f` | HT-12a ✅ + HT-10 ✅ |
| HT-12i | **Panel collapse buttons** — Added ◀ on left panel + ▶ on right panel + CSS .panel-collapse-btn. Wired to toggleLeftPanel/toggleRightPanel (HT-12c helpers). PHASE_HT12I_OK 4/4 PASS. | `/bma-ui-scope` → `/bma-ui-panel` | UI / left+right panels | ✅ done `4ecef2f` | HT-10 ✅ |
| HT-13a | **Helpers section in Measure ribbon** — new ribbon-group #ribbon-helpers with rstack 2×2 (Loupe/Ortho/Perp/Snap-off) dispatching existing toggleLoupe/toggleOrtho/togglePerp/toggleSnap. Surfaces 4 hidden helper toggles. PHASE_HT13A_OK 6/6 PASS. | `/bma-ui-ribbon` | UI / ribbon | ✅ done `787a5d5` | HT-12g ✅ |
| HT-13b+c | **Tool + Edit sections (verify-only)** — Vertex/Front/Copy placeholders skipped per anti-fake-button rule. Current Select/Pan + Undo/Redo/Delete kept. PHASE_HT13BC_OK 5/5 marker locks contract. | `/bma-ui-ribbon` | UI / ribbon | ✅ done `787a5d5` | HT-12g ✅ |
| HT-13d | **Polygon dropdown popover** — added ▾ caret button next to Polygon HERO; click opens popover with sub-mode hints (A=Arc/Alt=Freeform/Shift=Ortho/O=Opening) + sub-type list (Land/Building/Room). Right-click on Polygon HERO also opens. togglePolygonSubmodePopover/hidePolygonSubmodePopover helpers + outside-click close. PHASE_HT13D_OK 12/12 PASS. **Critical UX win** — sub-modes discoverable now. | `/bma-measure-ux` | UI / ribbon + measure | ✅ done `61b9965` | HT-12g ✅ |
| HT-14a | **📋 List tab content** — closes HT-8d-1 placeholder. `_renderListInPanel` with filter (6 types) + sort (time/type/name) + search + per-row hover ✎/🗑 + click-to-select. PHASE_HT14A_OK 8/8 PASS. | `/bma-ui-panel` | UI / right panel | ✅ done `1d3117e` | — |
| HT-14b | **🔧 Props tab content** — closes HT-8d-1 placeholder. `_renderPropsInPanel` with 4 sections (Selected/Semantic/Style/History) + empty-state. PHASE_HT14B_OK 4/4 PASS. | `/bma-ui-panel` | UI / right panel | ✅ done `1d3117e` | — |
| HT-14c | **📊 Summary tab deep-dive** — `_renderSummaryInPanel` (HT-8d-2 baseline) verified to include Hero GFA + Land/ratios (BCR/OSR/FAR/Permeable) + per-tag breakdown + object list + Warnings + Phase 1 note. PHASE_HT14C_OK 6/6 marker locks contract. | `/bma-measure-scope` (summary) | UI / right panel | ✅ done `1d3117e` | — |
| HT-15a | **📚 Sheets tab verify** — left panel Sheets tab (HT-8c renamed "📑 หน้า") already exists with pages list. Mockup's A/S/M/E/P discipline grouping skipped — pageTags (site/plan/elev/section) already groups. PHASE_HT15A_OK 6/6 marker locks contract. | `/bma-ui-panel` | UI / left panel | ✅ done `1d3117e` | — |
| HT-16 | **Panel ◀▶ collapse button trap fix** — found by `/bma-human-test` 2026-05-18. Added 2 restore tabs (#lp-restore-tab, #rp-restore-tab) inside #workspace, visible only when corresponding panel collapsed (via data-left/right-collapsed attrs set by applyLayoutPrefs). Position:absolute on canvas edges. Click restores panel. PHASE_HT16_OK 6/6 PASS. | `/bma-ui-scope` → `/bma-ui-panel` | UI / panel collapse | ✅ done `db59cca` | HT-12i ✅ |
| HT-17 | **Enter in area mode finishes polygon** — found by `/bma-human-test` 2026-05-18. Added `if(e.key==='Enter' && mode==='area' && mPts.length>=3){e.preventDefault();finishCurrentArea();}` to document keydown handler alongside existing path/ref case. Matches Measure menu "Finish Drawing — Enter" hint. PHASE_HT17_OK 2/2 PASS. | `/bma-measure-ux` | measure / keyboard | ✅ done `db59cca` | — |
| INV-2026-05-18-001 | **Page Setup Redesign — SUPERSEDED** — Split 2026-05-18 by `/bma-dev-loop` SCOPE step into 001a/b/c. 780 LOC across 4 files was too broad for one iteration; same pattern as HT-8d → HT-8d-1..5 split. | — | — | superseded — see INV-2026-05-18-001a/b/c | — |
| INV-2026-05-18-001a | **Page Setup Redesign Part A — Context-sensitive inspector + status chips** — Replace `#proj-form-panel` (left form) with new `#setup-inspector` that switches between Dashboard (nothing selected — 4 progress bars: categorized/named/scaled/measured + Top Issues click-to-jump list) and Page Card (page selected — preview, tag picker, name input, rotation+scale+objects+layers meta cells, placeholder Danger Zone). Move project-info form into collapsible accordion at bottom of inspector (default-collapsed). Update `#tag-grid` thumbnails to render: tag pill + traffic-light dot (green=tagged+manual scale / amber=auto-unverified / red=untagged or unknown) + object-count chip. New helpers: `_pageReadiness(pn)`, `_renderSetupDashboard()`, `_renderSetupPageCard(pn)`, `_setupSelectPage(pn)`. Keep existing `applyAutoNamesFromSetup`/`setPageTag`/`setPageName`/`toggleExcludePage` unchanged — call them from new UI. Marker: `PHASE_INV_PAGE_SETUP_A_OK` 8 sub-checks. Zero forbidden-surface. Zero schema. Source: `docs/invent/page-setup-redesign.md` + spike `proto/sandbox/invent-page-setup-redesign.html`. | `/bma-ui-scope` → `/bma-ui-panel` (modal region) | UI / page-setup modal | queued | — |
| INV-2026-05-18-001b | **Page Setup Redesign Part B — Token-based template engine + floor sub-types** — Replace current 6 prefix inputs with token-based template engine: `{n}` placeholder per tag, stored `projectInfo.autoNameTemplates: Record<string,string>` (additive schema). For `tag=plan` add floor sub-types: per-page `floorKind ∈ {basement|normal|mechanical|rooftop|custom}` + `floorNum` (basement/normal only), drives auto-name → ชั้นใต้ดิน N / ชั้น N / ชั้นห้องเครื่อง / ชั้นดาดฟ้า / (custom = user input). Per-page custom name override always wins; "↺ ใช้ template" button resets. Live template preview in page-card. Marker: `PHASE_INV_PAGE_SETUP_B_OK` 7 sub-checks. Schema additive only. | `/bma-ui-scope` + `/bma-check-forbidden` (schema additive verify) | UI / template engine + schema | queued | INV-2026-05-18-001a |
| INV-2026-05-18-001c | **Page Setup Redesign Part C — Permanent delete with renumber-map + `/rebuild-pdf` server endpoint** — Activate Danger Zone in page-card → renumber-map preview dialog (old → new page mapping table with deleted row crossed-out) → confirm calls new `/rebuild-pdf` POST endpoint server-side. Server: `PyMuPDF doc.delete_page()` in reverse order to keep indices stable, save trimmed PDF to new temp path for case, re-run `/analyse`. Client: update `pageStore`/`pageTags`/`pageNames`/`excludedPages` indexing using returned map. Schema additive: `deletedPageNumbers: number[]` (cleared after rebuild). Marker: `PHASE_INV_PAGE_SETUP_C_OK` 9 sub-checks. New endpoint adds next to existing (does not edit `/upload`, `/page/{n}`, `/analyse`). | `/bma-ui-scope` + `/bma-check-forbidden` (server endpoint addition) | UI / delete + server / `/rebuild-pdf` | queued | INV-2026-05-18-001a |
| INV-2026-05-18-002 | **Settings/Preferences panel v2 — Export Defaults + Loupe Prefs (Approach A)** — Extends shipped `bmaPlan.settings.v1` with 4 new PREFS paths inside existing modal (no new tab): `export.csvSeparator` (`,` / `;` / `\t`, default `,`) + `export.includeLawBasis` (bool, default true) slot into existing **หน่วย** tab; `loupe.radius` (50-160 px, default 80) + `loupe.zoomFactor` (2-8×, default 4) slot into existing **วาด** tab. Callsite wiring: `exportCSV()` reads `getPref('export.csvSeparator', ',')` + `getPref('export.includeLawBasis', true)`; `toggleLoupe()` / `resizeLoupe()` reads `getPref('loupe.radius', 80)` + `getPref('loupe.zoomFactor', 4)`. Kernel touch = 4 LOC (2 new sub-objects in `PREF_DEFAULTS` + 2 new shallow-merge entries in `loadPrefs()`); UI = ~75 LOC; callsite reads ~10 LOC. Marker: `SETTINGS_V2_OK` 6 sub-checks (no v1 regression + new prefs affect behavior + schema additive + ≤2-click reach + reset includes v2 + v1-save → v2 default injection). Zero forbidden-surface. Zero `.bmaplan` schema change. Source: `docs/invent/settings-panel-v2.md` + spike `proto/sandbox/invent-settings-panel-v2.html` (8/8 PASS incl. 2 robustness bonuses) + headless verifier `artifacts/invent/settings-panel-v2/verify-spike.mjs`. Production risk notes: verify `exportCSV()` callsite shape at ~line 2683 before commit; verify `toggleLoupe()` callsite shape at ~line 2027; choose Apply-vs-live per-pref UX (spike uses Apply-on-save for v1 consistency). | `/bma-ui-scope` (modal region) + `/bma-check-forbidden` (verify zero forbidden-surface touch) | UI / settings modal | queued | INV-002 ✅ |

## User priority notes

> Sprints **U1** and **U2** above are user-direct priority — requested 2026-05-14 after iteration 1 (I-B2a) succeeded. The user wants these as the **"first-usable" feature set** before the rest of Phase I-B/C/D/E. They are inserted at the TOP of the active queue. The loop picks U1 first, then U2, then returns to I-B2b.

- **U1 — Save Annotated PDF in-place.** Goal: pressing "Save PDF" overwrites the source PDF file (the one the user opened), with all annotations / measurements baked in. Every subsequent save updates the same file — no "Save As" dance each time. Implementation hint: capture a `FileSystemFileHandle` for the source PDF when opened via `showOpenFilePicker()`, store as `currentSourcePdfHandle` (mirror of `currentProjectHandle`), use it to write the annotated-PDF bytes back. Existing annotated-PDF export endpoint stays unchanged. Fallback to download when no handle (browser without FSA, or upload via `<input type="file">`). **Likely design ambiguity:** how to acquire an FSA handle on PDFs opened by the current `<input type="file">` upload — may trigger `LOOP_STOP_DESIGN` on scope; user will resolve.
- **U2 — 1-Page Excel Summary.** Goal: one Excel sheet that fits on one printable page with the headline measurement facts — total areas by category, BCR / OSR / FAR ratios, 4-direction setback summary, marker counts. Existing 4-sheet XLSX stays as the "detail" export; add an "Export Summary" entry that produces a single-sheet "สรุปผังบริเวณ" workbook. **No verdict / pass-fail UI** — facts only (Phase 1 boundary).

## Discovered backlog

> `/bma-human-test` and `/bma-sandbox-test` append issues here.
> CRASH/BROKEN → insert near the TOP of the active queue. FRICTION → end of queue. COSMETIC → low priority below.
> Two streams use distinct id prefixes:
> - `HT-*` = found by `bma-human-journey-tester` (synthetic + real 45-page permit journey)
> - `SB-YYYY-MM-DD-NNN` = found by `bma-sandbox-journey-tester` (PDFs dropped in `sandbox/`)

**2026-05-15 (post I-B2b human-test):** filed as `HT-1` … `HT-5` directly into the active queue above (BROKEN at top, FRICTION/COSMETIC after Phase I row). Source: `bma-human-journey-tester` after iteration 2 (I-B2b). XLSX 404 noted by tester was a script-side endpoint mismatch (it is POST, tester used GET) — NOT an app issue, not filed.

### sandbox 2026-05-15

First run of `/bma-sandbox-test`. 1 file tested: `251121_CHH_Submission_REV2 - Copy.pdf` (90.8 MB).
Verdict: `SANDBOX_TEST_ISSUES` — Tier 1 failed on `/upload` with HTTP 413 (server cap 80 MB), Tier 2 SKIPPED. No CRASH. The user's reported symptom "เปิดแล้วไม่ผ่าน" is a deliberate `MAX_UPLOAD_BYTES = 80 * 1024 * 1024` constant in `proto/server.py:51`, not a render OOM.

| id | severity | category | source PDF(s) | scope skill | new specialist? |
|---|---|---|---|---|---|
| SB-2026-05-15-001 | BROKEN | upload cap 80 MB blocks real permit PDFs | `251121_CHH_Submission_REV2 - Copy.pdf` (90.8 MB) | `/bma-check-forbidden` | none (one-constant fix) |
| SB-2026-05-15-002 | FRICTION | upload-cap UX is a status-bar string only — no modal, no pre-flight, no limit on cold-start | `251121_CHH_Submission_REV2 - Copy.pdf` | `/bma-ui-scope` | none (existing `bma-status-bar-specialist` + UI work) |

Sequencing: SB-001 first (raises the cap → unblocks the user complaint), SB-002 second (UX polish uses the new constant). Triager rationale: both findings are well-covered by existing skills; a new specialist would be overkill for a one-constant fix that is unlikely to recur once sized for the real-customer envelope.

Per-file artifacts: `artifacts/sandbox-tests/251121_CHH_Submission_REV2/journey.{py,log}`.

### user-test 2026-05-17 (post-loop, menu clarity feedback)

User noted that drawing tools have many variants (Area, Rectangle, Circle, Ellipse, Path, Arc-edge sub-mode, Freeform sub-mode, Opening toggle, etc.) but "วาดได้หลายรูปแบบแต่กดได้ครั้งเดียว" — i.e. the variety is hidden in a flat ribbon + a long Measure menu, so users don't see the family at a glance and don't know about sub-modes (Arc / Freeform) until they discover them by accident.

User direction: "ทำระบบเมนูให้ชัดเจนก่อน" — clarify menu BEFORE adding more tools. Annotation/comment system is "ยังไม่การพัฒนาเลย" — defer to `/bma-invent` (treat as a redesign, not a tweak).

| id | severity | category | source | scope skill |
|---|---|---|---|---|
| HT-8 | FRICTION | drawing-tool menu clarity — ribbon has 13 flat measure buttons, Measure menu has 23 items, sub-modes (Arc via 'A', Freeform via Alt-drag, Opening toggle) are invisible until discovered. **Fix:** (a) ribbon split into labeled sections with visual dividers: 🔍Select · 🟩พื้นที่ (Area/Rect/Circle/Ellipse/Opening) · 📏เส้น/ระยะ (Distance/Path/Ref) · 📍Marker (Parking/North) · 📐Calibrate · ↩Edit; (b) Area button shows sub-mode badge when Arc-pending or Freeform-active; (c) status bar `lbl-mode` prefix `[📐 วัด]` so user sees they're in measure layer; (d) tooltip rewrite mentioning sub-mode shortcuts (e.g. Area tooltip: "A — กด 'A' ระหว่างวาด=Arc edge, Alt+drag=Freeform"). ~120 LOC + CSS dividers + PHASE_HT8_OK marker. | user-test 2026-05-17 | `/bma-ui-scope` → `/bma-ui-ribbon` + `/bma-ui-menu` + `/bma-ui-status` |

### user-test 2026-05-17 (post-loop, on INV-001 Arc-polygon)

User tested arc-polygon drawing, reported "ทำได้ โอเค มาก" (works well). One UX gap noted:

| id | severity | category | source | scope skill |
|---|---|---|---|---|
| HT-7 | FRICTION | per-page scale not enforced before measurement — **✅ done `a3e45c5` 2026-05-17**. Hybrid (a+b) implemented: hard-block + auto-redirect to calib + bounce-back. `_SCALE_REQUIRED_MODES` set + `_scaleGateBeforeMode()`. `PHASE_HT7_OK` 6 sub-checks. full 44/44 GREEN. | user-test 2026-05-17 | `/bma-measure-ux` |
| HT-6 | FRICTION | arc draft missing live guideline preview — **✅ done `ecb44d4` 2026-05-17**. Added dashed arc preview in `redraw()` draft block: `computeArcEdge(lastVertex, mousePos, throughPt, centroid)` → `ctx.arc(...)` with `setLineDash`. `PHASE_HT6_OK` 4 sub-checks. full 42/42 GREEN. | user-test 2026-05-17 | `/bma-measure-ux` |

### ideas 2026-05-18

- [x] **Settings/Preferences panel — v2 extension** — `invent-done-go (→ INV-2026-05-18-002)` 2026-05-18. Approach A (Narrow-Deep: Export + Loupe) 26/30. Spike PASS 8/8 (6 acceptance + 2 robustness bonuses). User GO 2026-05-18. Sprint card written. See `docs/invent/settings-panel-v2.md` + `proto/sandbox/invent-settings-panel-v2.html` + `artifacts/invent/settings-panel-v2/verify-spike.mjs`.
    - Source: user 2026-05-18 via /bma-invent on `proto/sandbox/invent-settings-panel.html` — "ปรับแก้ให้ตรงกับโปรแกรมปัจจุบันว่าควรมี อะไรเพิ่ม"
    - Tags: bma-plan, ui, settings, preferences, p-med, v2
    - Currently shipped foundation (INV-2026-05-15-002 + HT-10 + HT-12a/c/h/i): 4-tab modal (วาด/หน่วย/หน้าจอ/Widgets), Ctrl+, shortcut, snap{enabled,threshold}, tool.default, unit{area,decimals}, layout{preset,density,hideLeft/RightPanel}, widgets.visible{5}
    - Direction: identify which preferences are natural next-extensions — candidates include snap-targets toggles, export defaults, theme/dark-mode, per-project overlay, JSON import/export, keyboard remap, loupe/cursor-guide settings, recent-files limit
    - Open questions: (1) scope cut for v2 — high-frequency only vs broad sweep? (2) per-project overlay yes/no? (3) JSON portability yes/no? (4) which "second-tier" prefs to surface vs leave hard-coded?
    - Scope skill: `/bma-invent` then likely `/bma-ui-scope` (modal region) for production sprint after invent passes checkpoint
    - Forbidden-surface profile: zero — purely additive PREFS fields; `getPref` boundary already exists; spike lives in `proto/sandbox/`
- [x] **Redesign หน้า Page Setup UI** — `invent-done-go (→ INV-2026-05-18-001)` 2026-05-18. Approach D smart-left-pane-inspector (26/30) + C's renumber-map dialog embedded + floor sub-types. Spike PASS 7/7 + bonus. User GO 2026-05-18 with refinement: "ต้องมีชั้นใต้ดิน ชั้นห้องเครื่อง ชั้นดาดฟ้า + ตั้งชื่อเองได้". Sprint card written. See `docs/invent/page-setup-redesign.md` + `proto/sandbox/invent-page-setup-redesign.html`.
    - Source: user 2026-05-18, "redesign หน้า Page Setup ui ... ชอบระบบตั้งชื่อหน้าอัตโนมัต และ ควรมีการตัดหน้า pdf ถาวร ส่วยในรายละเอียดด้านซ้าย ควรมีข้อมมูลจริงๆอะไรบ้าง"
    - Tags: bma-plan, ui, page-setup, page-naming, pdf-edit, p-med
    - Verdict: PRIOR_ART_PARTIAL — algorithms mature (Bluebeam/Foxit/Adobe hard-delete patterns, sequential-prefix naming) but composition for BMA-Plan workflow is new. 5 approaches scored — D won 26/30 on different axes (info-arch / workflow-pos / lifecycle / left-pane-inventory / auto-name).
    - Top approach: D context-sensitive left inspector (dashboard ⇄ page-card) with C's renumber-map dialog embedded as Danger Zone action + floor sub-type tokens (basement/normal/mechanical/rooftop/custom) per user feedback
    - Carry-over for production sprint: new `/rebuild-pdf` server endpoint (PyMuPDF `doc.delete_page()` reverse order); schema additive (`projectInfo.autoNameTemplates`, `deletedPageNumbers`, per-page `floorKind`/`floorNum`); traffic-light readiness rule should be configurable via Settings (ties to INV-2026-05-15-002)

### ideas 2026-05-17

- [ ] **Comment/Annotation system redesign** — `invent-queued` — from /idea 2026-05-17 (user-test feedback during menu-clarity discussion)
    - Source: user 2026-05-17, "การคอมเมนต์ตอนนี้ยังไม่การพัฒนาเลย น่าจะต้องเข้าสู่ในโหมดไอเดียก่อน"
    - Tags: bma-plan, ui, annotation, p-med
    - Current state: 7 annotation tools (Comment / Text / Highlight / Rect-Frame / Circle-Frame / Cloud-Frame / Arrow) work individually but lack workflow — no individual delete (only clear-all), no inline edit after creation, no reply/thread, no user attribution, no batch ops, no separation from measurement objects in Properties panel
    - Direction: possibly needs annotation panel pane (similar to Bluebeam Markups List); may or may not include collaborative comments (Phase 1 stays single-user)
    - Open questions: (1) single-user persistence-only vs minimum multi-user attribution? (2) flat list vs threaded replies? (3) integrate with annotated-PDF export workflow? (4) annotation = its own layer in Layers panel, or stays separate? (5) edit-after-create — inline vs Properties panel? (6) batch operations — select multiple, delete/move/recolor?
    - Scope skill: `/bma-invent` (needs RESEARCH + DIVERGE — Bluebeam Markups List vs Foxit comments vs Adobe Acrobat threaded vs PlanGrid markups; multiple viable architectures) → likely `/bma-ui-scope` + `/bma-ui-panel` for production sprint after invent passes checkpoint
    - Forbidden-surface profile: zero — annotation already lives in `ann_*` overlay separate from measurement schema (polyAreaM2 untouched). Schema additive (new optional fields on existing ann objects)

- [x] **Freeform area measurement** — `invent-done-go (→ INV-2026-05-17-001)` 2026-05-17. Approach D (Alt sub-mode of polygon) selected by user. Spike PASS 6/6 (err=1.22% on noisy circle, 500 raw → 14 decimated, 0 ms RDP). Sprint card written into active queue. See `docs/invent/freeform-area.md` + `proto/sandbox/invent-freeform-area.html`.
    - Source: user 2026-05-17, verbatim "ทำการวัดพื้นที่รูป freeform"
    - Tags: bma-plan, measure, p-med
    - Verdict: GREENFIELD — no PDF tool ships freehand area (Bluebeam/Foxit/Acrobat = click-polygon only; QGIS/ArcGIS have it but for stream-digitize GIS workflow, not single-shape PDF measurement)
    - 5 approaches scored — 3-way tie at 26/30 (A separate lasso, D Alt sub-mode, E live preview). User GO on D (highest UX, mixed click+drag in one polygon)
    - Carry-over for production sprint: Alt-mid-stroke guard, snap bypass during freehand (`if(altDown&&dragging) return early` in mousemove snap branch), touch input deferred to iPad track

- [x] **Dev-website สำหรับ developer + onboarding** — `invent-done-go → done` — commit `1bf61ca` 2026-05-17. `proto/static/docs/index.html` + `scripts/build_docs.py` + 5 Thai manuals + `content.json` (28 pages, 4 groups). `DOCS_SITE_OK` 7 sub-checks. full 41/41 GREEN. User GO 2026-05-17.
    - Source: user 2026-05-17, verbatim "ทำเว็บสำหรับการพัฒนาเช่น log การพัฒนาต่างๆ คู่มือการใช้งานเบื้องต้น และอื่นๆ"
    - Tags: bma-plan, docs, p-med
    - Status: PENDING-CHECKPOINT (invent done, awaiting user GO/NOGO/RESHAPE)
    - Verdict: PRIOR_ART_PARTIAL. Top approach: A — single static HTML + inline-JS micro-renderer in `proto/static/docs/`. Spike PASS 8/8 incl. 2 robustness bonuses. Est ~500 LOC + ~300 lines Thai content + 1 marker `DOCS_SITE_OK`.

### ideas 2026-05-15

- [x] **Arc-polygon hybrid area measurement** — `invent-done-go (→ INV-2026-05-15-001)` — from /idea 2026-05-15 → docs/invent/arc-polygon.md
    - Source: `~/.claude/ideas/IDEAS.md` @ 2026-05-15 17:59 (refined 18:02)
    - Tags: bma-plan, measure, p-med
    - Direction: shape = polygon edges mixed with arc segments in ONE measurable object. Area = polygon area ± circular-segment area per arc. NOT full Bezier, NOT circle-only. Curve drawing exists but is decorative — this adds a measurable counterpart.
    - Open question: same area-summary row as polygon, or separate "curved shapes" row?
    - Scope skill: `/bma-measure-scope` → likely `/bma-measure-geometry` (sub-area: generator + core). Note `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER` is render-only smoothing — different concern.
- [x] **User-configurable settings/preferences panel** — `invent-done-go (→ INV-2026-05-15-002)` — from /idea 2026-05-15 → docs/invent/settings-panel.md
    - Source: `~/.claude/ideas/IDEAS.md` @ 2026-05-15 18:26
    - Tags: bma-plan, ui, p-med
    - Direction: settings UI to customize various parts of BMA-Plan. Scope still open — could span snap/scale defaults, default layer, export format, UI layout presets (already partially via `bmaPlan.uiLayoutOptions.v1` localStorage).
    - Open questions: (1) which area first — snap/scale defaults vs UI layout vs export format? (2) persist in localStorage or also embed in `.bmaplan` per-project?
    - Scope skill: `/bma-ui-scope` (likely modal region) — but real scope decision waits on follow-up answers. May warrant `/bma-invent` first if user wants a holistic settings architecture rather than incremental options.

## Known leftovers (predate the loop)

| item | type | note |
|---|---|---|
| `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER` | sprint | ✅ done `1bf61ca` 2026-05-17 — render-only smoothing in `_renderPolyEdges`; `ctx.arc`/`ctx.ellipse` analytic branches; `CIRCLE_RENDER_OK` 7 sub-checks; last pre-loop leftover cleared |
| Z-Index Fix `UI_MANUAL_TEST.md` | manual verify | needs a human in a real browser; `bma-human-journey-tester` partially covers it |
| H.0 — 45° angle lock | deferred phase | unblocks the 2h rule; not in the Phase I queue |
| `plans/*.md` ×3 | housekeeping | completed historical plans — archive to `sprints/archive/` |
| 4 uncommitted files (`NEXT_ACTION.md`, `opus4.7/`, `archive/old_docs/.claude/`, `PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`) | housekeeping | pre-session leftovers — user decides |

## Completed (recent — full history in `sprints/completed/`)

INV-002 `b6856df` · I-E `504b993` · I-D `dc96f62` · I-C `a490c1e` · I-B4 `91fede9` · I-B3 `c011c4e` · SB-002 `33577b7` · INV-001 `<COMMIT_HASH_PENDING>` · HT-5 `89074cb` · HT-4 `a6973ef` · HT-3 `0900e0a` · HT-2 `acd8636` · HT-1 `e21ca98` · U2 `4bcacc6` · U1 `2101dfe` · SB-2026-05-15-001 `fabc2e9` · Pack G `5dc5dd3` · I-B2b `5c76708` · I-B2a `b9f9132` · I-B1 `c38c3e6` · I-A `984eb7e`

## Stop conditions (loop halts, reports to user, waits)

1. `/bma-check-forbidden` or a scope skill returns **BLOCKED** — a forbidden surface is needed
2. E2E **marker regression** that survives one auto-retry
3. `/bma-human-test` returns **HUMAN_TEST_CRASH**
4. A scope skill returns SPLIT_REQUIRED or design ambiguity needing a **human design choice**
5. The only way forward crosses the **Phase 1 scope boundary**
6. Active queue **and** discovered backlog both empty → clean stop `LOOP_DONE`

## Phase 1 scope boundary (permanent — the loop never auto-adds these)

legal checker · OCR · AI · Rule Engine · FAR/OSR/setback pass-fail verdict · K.1 generator · auto boundary detection · multi-user / SaaS
