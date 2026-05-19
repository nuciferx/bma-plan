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

**Update 2026-05-19:** Page Setup Redesign sprint trilogy COMPLETE. 001a `e85a5ce` (inspector + chips), 001b `798e5c3` (floor sub-types: basement/normal/mechanical/rooftop/custom), 001c `ebb521c` (permanent delete + `/rebuild-pdf` + renumber-map). Markers `PHASE_INV_PAGE_SETUP_{A,B,C}_OK` all GREEN. Research done before 001c (`afd4e71`) — incumbents survey locked Q1-Q4 design.

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
| INV-2026-05-18-001a | **Page Setup Redesign Part A — Context-sensitive inspector + status chips** — Replaces `#proj-form-panel` content with `#setup-inspector-content` (dashboard ⇄ page-card switch). Project-info form moved into `<details id="setup-pi-accordion">` (open-by-default for E2E compat). `#tag-grid` thumbnails now emit per-cell traffic-light dot (green=tagged+manual / amber=auto-unverified / red=untagged or unknown) + object-count chip. New helpers: `_pageReadiness`, `_setupCountObjects`, `_renderSetupDashboard`, `_renderSetupPageCard`, `_setupBack`, `_renderSetupInspector`. `selectSetupPage`/`setPageName`/`buildTagGrid` hooked to inspector refresh. `PHASE_INV_PAGE_SETUP_A_OK` 8/8 PASS in smoke. No regression caused by this sprint (3 pre-existing failures unchanged: HT-8C/HT-10/HT-12H). Zero forbidden-surface. Zero schema change. TEST-H deferred to 001b/c. Source: `docs/invent/page-setup-redesign.md` + spike `proto/sandbox/invent-page-setup-redesign.html` (7/7 PASS + 1 bonus). | `/bma-ui-scope` → `/bma-ui-panel` (modal region) | UI / page-setup modal | ✅ done `e85a5ce` | — |
| INV-2026-05-18-001b | **Page Setup Redesign Part B — Floor sub-types for plan tag** — Scope narrowed to user's stated requirement. New per-page schema `pageFloorKind ∈ {basement|normal|mechanical|rooftop|custom}` + `pageFloorNum` (additive, optional). New helpers `setPageFloorKind`/`setPageFloorNum`. `autoNamePage` floor-aware for `tag=plan`: basement N → "ชั้นใต้ดิน N", normal N → "ชั้น N", mechanical → "ชั้นห้องเครื่อง", rooftop → "ชั้นดาดฟ้า", custom → user-typed (no overwrite). Save/load round-trip + tag-change clear. Floor-kind picker in page-card (visible when tag=plan). Token-engine refactor DEFERRED — current prefix inputs preserved for backward compat. `PHASE_INV_PAGE_SETUP_B_OK` 9/9 PASS. Zero forbidden-surface. | `/bma-ui-scope` | UI / template + schema additive | ✅ done `798e5c3` | INV-2026-05-18-001a |
| INV-2026-05-18-001c | **Page Setup Redesign Part C — Permanent delete + renumber-map + `/rebuild-pdf`** — ✅ shipped `ebb521c` 2026-05-19. Server: new `/rebuild-pdf` POST (PyMuPDF `doc.delete_page()` reverse order, flush caches, returns `renumberMap`). Client: `_openRenumberDialog` preview table → `_executeRenumberDelete` → `_reindexPageDicts` walks 7 per-page dicts. Hard-block during draw + last-page guard + Foxit-style warning. `PHASE_INV_PAGE_SETUP_C_OK` 7/7 PASS. | `/bma-ui-scope` + `/bma-check-forbidden` | UI / delete + server / `/rebuild-pdf` | ✅ done `ebb521c` | INV-2026-05-18-001a |
| INV-2026-05-18-002 | **Settings/Preferences panel v2 — Export Defaults + Loupe Prefs** — Extends `bmaPlan.settings.v1` with 4 new PREFS paths (additive). `export.csvSeparator` + `export.includeLawBasis` in **หน่วย** tab. `loupe.radius` + `loupe.zoomFactor` in **วาด** tab. `exportCSV` reads both export prefs; `updateLoupe` uses `loupeZoomFactor` for constant magnification. `_applyLoupePrefs()` syncs on boot + after Apply (clamps before fallback). `SETTINGS_V2_OK` 6/6 PASS. Zero forbidden-surface. v1 untouched (`SETTINGS_OK` still GREEN). | `/bma-ui-scope` (modal region) | UI / settings modal | ✅ done `3e71865` | INV-002 ✅ |
| INV-2026-05-19-001a | **Zen Mode + Sheet Minimap** — body.zen CSS class hides ribbon/lp/rp/status/topbar (canvas measured at 94.4% vh on 900px test viewport, exceeds 92% target). 3 corner HUDs replace status bar: TL (Scale + Tool), TR (Page + Exit Zen chip), BL (Layer + Save + Obj + ⚠). #zen-minimap 260×200 bottom-right with 5-col grid of pages, IntersectionObserver lazy-load. F11 toggle + Esc exit + visible chip. `PREFS.layout.zenMode` + `zenOnboarded` additive. MutationObserver on #bottombar mirrors status-bar updates → HUD. HT-10 `applyLayoutPrefs()` restores prior panel state on zen exit. `PHASE_INV_ZEN_OK` 10/10 PASS. smoke + full GREEN. JOURNEY_OK on 45-page permit (0 CRASH/BROKEN, 2 FRICTION → HT-Z-1/HT-Z-2 filed). +180 LOC ui.html / +50 CSS / +110 e2e. Also fixed 2 pre-existing baseline test drifts from polish `0e4e851`. Zero forbidden-surface. Schema additive. Source: `docs/invent/fullscreen-canvas-ui.md` (Approach A, 27/30) + spike `proto/sandbox/invent-fullscreen-canvas-ui.html` (6/6 PASS). | `/bma-ui-scope` → `/bma-ui-canvas` + `/bma-ui-status` | UI / canvas overlay + HUDs + new zen-mode surface | ✅ done `20e2548` | HT-10 ✅ |
| INV-2026-05-19-001c | **Zen+Palette FRICTION polish (HT-Z-1/2/3 bundle)** — 3 small fixes from journey tests on 001a/b. (1) `_zenSyncHud()` reads `pageNames[curPage]` directly instead of `bb-page-name` element — kills MutationObserver lag during fast nav. (2) HUD Scale chip amber when scale state is `auto-unverified`/`unknown`, default white when manual — fixes "is my scale calibrated?" confusion. (3) `filterPalette()` empty branch adds `💡 แท็กภาษาไทยใช้ได้หลังตั้งค่าหน้าใน Page Setup` hint when Thai tag word queried + no pages tagged. `PHASE_INV_POLISH_001C_OK` 5/5 PASS. smoke + full GREEN (no regression on 001a/b markers). +15 LOC ui.html / +65 e2e. TEST-H skipped per AGENTS.md no-test rationale. Zero forbidden-surface. Schema unchanged. | `/bma-ui-scope` → `/bma-ui-canvas` + `/bma-ui-menu` | UI / HUD + palette | ✅ done `f7d64b8` | INV-001a ✅ + INV-001b ✅ |
| INV-2026-05-19-001b | **⌘K Command Palette (page jump)** — `#cmd-palette` floating modal. Filters pages by number/name/tag slug/Thai tag label (TAG_LABELS: ผังบริเวณ/ชั้น/รูปด้าน/รูปตัด/รายละเอียด). ↑↓ nav, Enter = `loadPage(n)` + close, Esc = cancel. Bound to Ctrl+K/Cmd+K with `mPts.length===0 && !anyModal` guard. Key handlers placed BEFORE inInput guard so palette input doesn't swallow nav keys. Works in classic + zen (z-index 9500 > zen 1500). Pre-filter shows 12 default rows on empty input. `PHASE_INV_PALETTE_OK` 10/10 PASS. smoke + full GREEN (no regression on 001a). JOURNEY_OK on 45-page permit (13/13 steps, 1 FRICTION HT-Z-3 filed). +120 LOC ui.html / +35 CSS / +95 e2e. Zero forbidden-surface. Schema unchanged. Source: `docs/invent/fullscreen-canvas-ui.md` (Approach B, 28/30) + spike same file. | `/bma-ui-scope` → `/bma-ui-menu` (palette modal) | UI / modal + keyboard | ✅ done `a51207f` | — |
| INV-2026-05-19-003a | **Print to printer button (Path B)** — File-menu items "🖨 Print Current Page" + "🖨 Print Selected Pages" → captures canvas via `toDataURL('image/png')` → opens synthetic print window with `<img>` + `@media print` page-break CSS + `window.print()` trigger. Two modes: single page + iterate selected/all-non-excluded with `loadPage(n)` + `_waitForRedraw` (2 RAF). Original `curPage` restored after multi-page. DPR captured in synth metadata. **Note:** sprint card originally said "Export panel" — actual placement is File menu dropdown (Export panel doesn't exist as a separate widget; exports live in File menu post-HT-12). Removed `Ctrl+P` shortcut to avoid conflict with existing `togglePerp()` snap toggle. `PHASE_INV_PRINT_OK` 8/8 PASS. smoke + full GREEN (no new regressions; 6 pre-existing failures unchanged). +72 LOC ui.html / +83 LOC e2e. TEST-H skipped per AGENTS.md no-test rationale (additive menu sprint, journey doesn't exercise print). Zero forbidden-surface. Schema unchanged. Source: `docs/invent/print-canvas-per-page.md` (Path B). | `/bma-ui-scope` → `/bma-ui-canvas` | UI / File menu + canvas snapshot | ✅ done `b4f7235` | — |
| INV-2026-05-19-003b | **`/export-png` ZIP endpoint (Path C)** — New POST `/export-png` returns ZIP of PyMuPDF-rendered PNGs (one per requested page) with overlays drawn via the **exact same helpers** as `/export-pdf` (no overlay-math reimpl). DPI clamped 72..300 (default 200). `MAX_EXPORT_PAGES` env-overridable (default 200) → 413 with `max` field. `ZIP_STORED` (PNG already compressed). File menu "🖼 Export PNG (ZIP, 200 DPI)" + `exportPngZip()` POSTs current `selectedPages` or all non-excluded pages. **Shipped manually** (not via /bma-dev-loop — server.py edit outside loop's safe scope per step-3 guardrail; /bma-check-forbidden returned WARN→OK). `PHASE_INV_PNG_EXPORT_OK` 11/11 PASS. smoke 33/34 + full 37/37 (1 pre-existing PHASE_I_D_OK unrelated). +130 LOC server.py / +25 LOC ui.html / +130 LOC e2e. Zero forbidden-surface (no edit to /upload, /page, /analyse, /export-pdf, CASES, RS, render cache, .bmaplan). Schema unchanged. Source: `docs/invent/print-canvas-per-page.md` (Path C). | `/bma-check-forbidden` (WARN — additive endpoint) | export / server endpoint + client menu | ✅ done `612de96` | INV-003a ✅ |
| BLOAT-1 | **CLAUDE.md ui.html LOC drift fix + consolidation trigger rule** — Updated CLAUDE.md baseline `~1,700 lines` → current `~4,231 lines` for `proto/ui.html` (and `proto/server.py` ~1,370 → ~1,750), and added a discipline rule: "if `ui.html` crosses **5,000 lines**, the next sprint MUST be a consolidation sprint that extracts a JS region to `static/js/*`." Pure documentation; no code path touched. py_compile PASS; `/bma-e2e` + `/bma-human-test` skipped per AGENTS no-test rationale. Source: manual bloat audit 2026-05-19 (see Discovered backlog → bloat-audit). | `/bma-check-forbidden` (docs-only) | docs / discipline | ✅ done `4dcf5cf` | — |
| BLOAT-2 | **Extract status-bar JS to `static/js/status-bar.js`** — Moved 8 functions (`updateAnalyseUI`, `activeLayerLabel`, `currentObjectCount`, `currentWarningCount`, `updateBottomBar`, `updateModeLabel`, `_markSaved`, `_setDirty`) + 2 constants (`MODE_BASE_LABELS`, `SITE_TAG_THAI_LABELS`) from `proto/ui.html` to new classic non-module script `proto/static/js/status-bar.js` (49 LOC). `<script src>` inserted between `opening-parent.js` and main inline `<script>`. ui.html: 4,231 → 4,208 lines (-23 net; placeholders left in). `_fallbackDownload` (L3389) kept in ui.html (part of save chain, will move with BLOAT-3). NEW marker `PHASE_BLOAT2_OK` 8/8 PASS. smoke 18/18 + full 21/21 GREEN (PERSIST_OK round-trip on real 45-page permit confirms `_setDirty`/`_markSaved` extraction safe). `/bma-human-test` skipped per AGENTS no-test rationale. Zero forbidden-surface. | `/bma-ui-scope` → `/bma-ui-status` | UI / extraction | ✅ done `ce87f47` | BLOAT-1 ✅ |
| BLOAT-3 | **Extract export/save JS to `static/js/export-save.js`** — Moved 14 functions (`dlBlob`, `exportJSON`, `exportCSV`, `exportSummaryXLSX`, `exportXLSX`, `exportAllPagesAnnotatedPDF`, `exportCurrentPageAnnotatedPDF`, `exportPngZip`, `_makeProjBlob`, `_writeToHandle`, `_fallbackDownload`, `saveProjectAs`, `saveProject`, `saveSourcePdfInPlace`) + 13 constants (6 COL_* + 7 TYPE_*) + `rowBase` + `buildRows` to new classic non-module script (188 LOC). ui.html: 4,208 → 4,057 lines (-151 net). `<script src>` inserted after `status-bar.js`. NEW marker `PHASE_BLOAT3_OK` 8/8 PASS (fileLoad / 14 fnsOk / 13 constsOk / dlBlobOk / buildRowsOk / blobIsBlob / schemaOk all 12 v1 fields / asyncOk). smoke 18/18 + full 21/21 GREEN. XLSX_OK + PROJECT_OK + PERSIST_OK + ANNOT_OK + REAL_OK all GREEN on real 45-page permit — proves save/.bmaplan/export extraction safe. `/bma-human-test` skipped (full E2E + schemaOk cover risk). Zero forbidden-surface. `.bmaplan` schema unchanged (version 1, same 12 fields). Kept in ui.html (out of scope): pgmgrExportPDF + print cluster + applyLoadedProject + load helpers + shared helpers. | `/bma-ui-scope` → `/bma-check-forbidden` | UI / extraction | ✅ done `e524488` | BLOAT-2 ✅ |
| BLOAT-4 | **Extract annotation JS to `static/js/annotations.js`** — Move 7 annotation tool handlers (`ann_text`/`ann_highlight`/`ann_rect`/`ann_circle`/`ann_cloud`/`ann_arrow`/`ann_sticky`) + render + hit-test to external file. Acceptance: `ui.html` LOC -300, annotation E2E markers retained (incl. `PHASE_INV_STICKY_OK`, `PHASE_HT11_OK`). | `/bma-ui-scope` | UI / extraction | queued | BLOAT-2 |
| BLOAT-5 | **Extract page-setup modal JS to `static/js/page-setup.js`** — Move INV-2026-05-18-001a/b/c helpers (`_renderSetupDashboard`/`_renderSetupPageCard`/`_openRenumberDialog`/floor-kind) to external file. Acceptance: `ui.html` LOC -300, `PHASE_INV_PAGE_SETUP_*_OK` markers retained. | `/bma-ui-scope` → `/bma-ui-panel` | UI / extraction | queued | BLOAT-2 |

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

### bloat-audit 2026-05-19 (user-initiated, manual analysis pre-loop)

User asked for a size/speed analysis before launching the loop. Findings:

- `proto/ui.html` = **4,231 lines / 432 KB**, of which **360 KB (83%) inline `<script>`** with **483 functions** in one global scope
- CLAUDE.md baseline says `~1,700 lines` for ui.html — accurate as of when it was written; today it has drifted **+149%**
- Startup: `server.py` first-import ~8.2s (mostly PyMuPDF + uvicorn deps, not our code); `ui.html` cold-read ~307 ms — user load time is fine
- Pain is developer-facing: `bma-explorer` subagent was created specifically because `ui.html` is too big to read directly
- No consolidation phase in `/bma-dev-loop` — every iteration only adds, never re-flattens
- Prior art for extraction exists: `static/js/semantic-meta.js` (4 KB) + `static/js/opening-parent.js` (1.5 KB) shipped earlier — pattern proven, no bundler needed

Filed as **BLOAT-1..5** in active queue. Sequencing: BLOAT-1 (docs + trigger rule) first → BLOAT-2 (status-bar extraction, smallest module, proves pattern) → BLOAT-3..5 (parallel after BLOAT-2 establishes the extraction recipe).

| id | severity | category | scope skill |
|---|---|---|---|
| BLOAT-1 | FRICTION (developer) | docs / discipline | `/bma-check-forbidden` (docs-only) |
| BLOAT-2 | FRICTION (developer) | UI / status-bar JS extraction | `/bma-ui-scope` → `/bma-ui-status` |
| BLOAT-3 | FRICTION (developer) | UI / export-save JS extraction | `/bma-ui-scope` → `/bma-check-forbidden` |
| BLOAT-4 | FRICTION (developer) | UI / annotation JS extraction | `/bma-ui-scope` |
| BLOAT-5 | FRICTION (developer) | UI / page-setup modal extraction | `/bma-ui-scope` → `/bma-ui-panel` |

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
| HT-8 | FRICTION → ✅ done `b1665f5` 2026-05-19 | drawing-tool menu clarity — **AUDIT:** (a) ribbon dividers + 6 labeled sections (TOOL/SCALE/พื้นที่/LINES/MARKER/HELPERS) ALREADY DONE in prior sprints. (c) status bar prefix `📐 วัด` ALREADY DONE (`#status-mode-prefix` via _RIBBON_TAB_PREFIX). (b) **NEW:** Area sub-mode badge — `_updateAreaSubmodeBadge()` shows red "A" when `mArcDraft.pending`, purple "✎" when `mFreehandActive`; hooked into setMode + keydown('A') + Alt+mousedown + mouseup + Esc. (d) **NEW:** btn-area tooltip rewritten (both inline + initTooltips() override) to mention A=Arc / Alt=Freeform / Shift=Ortho / O=Opening shortcuts. `PHASE_HT8_OK` 8/8 GREEN. | user-test 2026-05-17 | `/bma-ui-scope` |

### zen-mode 2026-05-19 (post INV-2026-05-19-001a/b human-tests) — ALL DONE in INV-001c

Three FRICTION items from journey tests on 001a Zen + 001b Palette, all fixed in INV-2026-05-19-001c polish bundle:

| id | severity | finding | fix shipped in |
|---|---|---|---|
| HT-Z-1 | FRICTION → DONE | Transient stale HUD page name during fast minimap nav (MutationObserver timing) | `_zenSyncHud` now reads `pageNames[curPage]` directly — INV-001c |
| HT-Z-2 | FRICTION → DONE | Auto-unverified scale not visually distinguished in HUD | HUD Scale chip amber for auto-unverified/unknown; manual = default — INV-001c |
| HT-Z-3 | FRICTION → DONE | Palette Thai-tag query empty-state lacked Page Setup hint | `filterPalette()` empty branch adds 💡 hint when Thai tag word + no tags exist — INV-001c |

### user-test 2026-05-17 (post-loop, on INV-001 Arc-polygon)

User tested arc-polygon drawing, reported "ทำได้ โอเค มาก" (works well). One UX gap noted:

| id | severity | category | source | scope skill |
|---|---|---|---|---|
| HT-7 | FRICTION | per-page scale not enforced before measurement — **✅ done `a3e45c5` 2026-05-17**. Hybrid (a+b) implemented: hard-block + auto-redirect to calib + bounce-back. `_SCALE_REQUIRED_MODES` set + `_scaleGateBeforeMode()`. `PHASE_HT7_OK` 6 sub-checks. full 44/44 GREEN. | user-test 2026-05-17 | `/bma-measure-ux` |
| HT-6 | FRICTION | arc draft missing live guideline preview — **✅ done `ecb44d4` 2026-05-17**. Added dashed arc preview in `redraw()` draft block: `computeArcEdge(lastVertex, mousePos, throughPt, centroid)` → `ctx.arc(...)` with `setLineDash`. `PHASE_HT6_OK` 4 sub-checks. full 42/42 GREEN. | user-test 2026-05-17 | `/bma-measure-ux` |

### ideas 2026-05-20

- [x] **Focus-mode lite-version spinoff with single-row menu bar** — `invent-done-nogo` 2026-05-20. Research verdict PRIOR_ART_PARTIAL. 5 v1 approaches scored (A 27/30 top). After RESHAPE: 5 v2 approaches scored (D-v2 27/30 top — snap-chip strip + 19-item Measure + fullscreen pill). After 2nd RESHAPE: user pointed to existing `invent-zen-mode-v2-topbar.html` — v3 converged on adopting INV-002 layout as default via ~30 LOC delta in `proto/ui.html`. **User NOGO**: prefers building a standalone `/lite/` folder (true sibling of `/proto/`, not a feature-flag inside it). Artifact + 3 spike iterations + 12-assertion v3 sandbox kept as reference for the future `/lite/` build. See `docs/invent/focus-mode-lite-spinoff.md` ## Decision. **Follow-up recommended**: file fresh `/idea` for "BMA-Plan Lite — standalone `/lite/` folder build" (raises NEW questions: packaging shape, code-sharing policy, version-sync policy, `.bmaplan` cross-compat rules — not covered here).
    - Source: /idea 2026-05-20 00-12
    - Tags: bma-plan, ui, focus-mode, fullscreen, lite-version, research-needed, p-med
    - Invent artifact: `docs/invent/focus-mode-lite-spinoff.md` (845 lines, v3 + v2 + v1 history)
    - Sandbox: `proto/sandbox/invent-focus-mode-lite-spinoff.html` (570 lines, INV-002 layout + lite-default adapter — reusable starting point for `/lite/` build)

- [ ] **BMA-Plan Lite — standalone /lite/ folder build** — `invent-queued` — from /idea 2026-05-20 (follow-up from 2026-05-20-00-12 NOGO; user explicitly prefers a separate `/lite/` directory as true sibling of `/proto/`, not a feature-flag inside it)
    - Source: user 2026-05-20, "BMA-Plan Lite — standalone /lite/ folder build"
    - Tags: bma-plan, lite-version, packaging, spinoff, standalone, follow-up, p-med
    - Direction: (unframed — pending /bma-invent FRAME phase; predecessor invent established UX target = INV-002 zen-top-bar layout; THIS idea = packaging shape decision, not UI design)
    - Open questions: (pending /bma-invent — packaging shape (PyInstaller .exe / web subdomain / Electron / all three?), code-sharing policy (copy-and-fork measurement engine OR re-implement?), version-sync policy (when proto/ ships engine bugfix, how does /lite/ learn?), .bmaplan cross-compat (hard constraint same as proto, or relaxed?))
    - Scope skill: pending (`/bma-invent` decides after research; likely new packaging/distribution scope)
    - Forbidden-surface profile: NONE in `/proto/` — by design, `/lite/` does not touch existing measurement engine; needs to define its OWN forbidden surfaces once built

### ideas 2026-05-19

- [x] **Sticky-note annotations per PDF page** — `invent-done-go (→ INV-2026-05-19-005)` 2026-05-19. Research verdict PRIOR_ART_PARTIAL. 5 approaches scored; top = B (new `ann_sticky` type + HTML div overlay, 25/30). Spike 8/8 PASS in `proto/sandbox/invent-post-it-page-notes.html`. User standing-order GO. Open Qs resolved by research: (1) page-coord (matches all incumbents + existing 7 ann types), (2) include in PDF export (already implemented for ann_comment path). See `docs/invent/post-it-page-notes.md`.
    - Source: /idea 2026-05-19 19:30
    - Tags: bma-plan, annotation, p-med
    - Invent artifact: docs/invent/post-it-page-notes.md
    - Sandbox: proto/sandbox/invent-post-it-page-notes.html

#### INV-2026-05-19-005 — Sticky-note (post-it) annotations — `done 7c4f96a` 2026-05-19 (invent 789ee6b → impl 7c4f96a)

- **scope skill:** `/bma-ui-scope` (UI region: canvas overlay + annotate ribbon — additive, no measurement-math touch)
- **depends-on:** none (additive — existing 7 annotation types unaffected)
- **est LOC:** ~150-200 (proto/ui.html ~100 / app.css ~40 / e2e_ui_test.py ~50)
- **success markers needed:** `PHASE_INV_STICKY_OK` with 10 sub-checks:
  1. New mode `ann_sticky` registered in setMode handler
  2. Toolbar/menu entry calls `setMode("ann_sticky")` (Annotate ribbon or menu)
  3. Click on canvas in sticky mode → creates annotation with `type: "sticky"` in `pageStore[curPage].annotations[]`
  4. Sticky card renders as HTML div positioned via `pdfToC()` — left/top match page-coord
  5. Card body is `<textarea>` (or contenteditable) — type updates `ann.text`
  6. Drag by header → `ann.pts[0]` updates; DOM position syncs
  7. Delete button removes annotation + DOM element
  8. Save .bmaplan → reload → sticky re-renders at same page-coord with same text
  9. Existing `ann_comment` annotations still render via canvas (no regression)
  10. Export to annotated PDF → sticky text appears on exported page (via existing ann pipeline OR explicit handler in server.py if needed — verify in test)
- **forbidden surfaces:** NONE — schema additive only (new optional fields on annotation: `width`, `height`, `stickyStyle`); reads `pdfToC`/`cToPdf` only (no edit); does not touch polyAreaM2/snap/RS/measurement math.
- **scope plan:**
  1. Add toolbar button + menu entry that calls `setMode("ann_sticky")`
  2. Register `ann_sticky` mode in `setMode()` mode list + cursor handling
  3. In mousedown handler (mode==="ann_sticky" branch), create annotation `{id, type:"sticky", pts:[clickCoord], text:"", color:"#fef3a6", width:120, height:80, createdAt}` and call new `renderStickyCard(ann)` helper
  4. New `renderStickyCard(ann)` — creates `.sticky-card` div, positioned absolute via `pdfToC`, header (drag) + textarea (edit) + delete button
  5. `drawAnnotations()` skips `type==="sticky"` (HTML layer handles render)
  6. New `rerenderStickyCards()` called from `redraw()`, `loadPage()`, `applyLoadedProject()` — syncs HTML cards to current pageStore + current zoom/pan transform
  7. On pageStore mutations from drag, push to undo stack via `pushUndo()` (HT-18 invariant)
  8. E2E test `_test_inv_sticky_notes` + `PHASE_INV_STICKY_OK` marker covering 10 sub-checks
- **link:** `docs/invent/post-it-page-notes.md` (research + spike)
- **manual UI test required:** YES — verify Thai IME works in textarea (research resolved this as B's main UX advantage)
- **carry-over from spike:** sandbox proves all 8 success criteria; production needs to handle zoom-scaling (card size: fixed pixel vs scales with zoom?) and rotation (rotate HTML overlay container?).

- [x] **F12 Overview — Excluded pages as separate group** — `invent-done-nogo (superseded by f12-overview-mockup-port)` 2026-05-19. Spike 7/7 PASS, but user decided to scrap incremental gap-by-gap approach in favor of a single faithful mockup port. Approach A (bottom-band atomic-restore, 26/30) design feeds into the port sprint's implementation.
    - Source: user 2026-05-19 (NOGO)
    - Tags: bma-plan, ui, zen, overview, excluded-pages, p-med
    - Artifact retained for future reference: `docs/invent/f12-excluded-group.md`

- [x] **F12 Overview — Mockup-spatial-sheet-map faithful port** — `invent-done-go (→ INV-2026-05-19-002c)` 2026-05-19. Verdict `PRIOR_ART_MATURE` (mockup is the in-repo, user-blessed spec); diverge/score/spike SKIPPED per /bma-invent MATURE-path rule. Single sprint card filed. User GO 2026-05-19. See `docs/invent/f12-overview-mockup-port.md` + spec `proto/sandbox/mockup-spatial-sheet-map.html`.
    - Source: user 2026-05-19 — "ทำแบบนี้ใหม่ทั้งหมด เอาตามนี้เลยไม่ต้องเปลี่ยน"
    - Tags: bma-plan, ui, zen, overview, mockup-port, p-high
    - Implementation guide: § Research → "Mockup → Live-app delta map" (row-by-row port plan)
    - Supersedes: f12-excluded-group (NOGO — folded into this port)

- [ ] **Save state out of sync with canvas visual state** — `queued (→ HT-18)` — from /idea 2026-05-19, filed direct without invent (bug, not feature)
    - Source: ~/.claude/ideas/IDEAS.md @ 2026-05-19 16:08
    - Tags: bma-plan, save, p-high, data-integrity
    - Open Qs: (1) canvas แสดงของที่ยังไม่ save (isDirty ไม่ trigger) หรือ load กลับมาแล้ว render ไม่ครบ? (2) object ประเภทไหน — poly / path / annotation / rotation?

- [x] **Print canvas view with measurement overlays per page** — `invent-done-go (→ INV-2026-05-19-003a + 003b)` 2026-05-19. Verdict `PRIOR_ART_MATURE` (`/export-pdf` already flattens overlays + handles rotation + per-page selection). Diverge/score/spike SKIPPED per /bma-invent MATURE-path rule. 3 paths surfaced (A=educate / B=printer button / C=PNG endpoint). User chose **B + C** — 2 sprint cards filed (003a printer button, 003b PNG ZIP endpoint with depends-on 003a). See `docs/invent/print-canvas-per-page.md`.
    - Source: ~/.claude/ideas/IDEAS.md @ 2026-05-19 17:15
    - Tags: bma-plan, export, print, p-med
    - Open Qs resolved at checkpoint: (1) ทั้งคู่ — Path B = direct printer, Path C = PNG file. (2) ทั้งคู่ — current page + all-selected modes both supported in 003a.
    - Invent artifact: `docs/invent/print-canvas-per-page.md`

#### HT-18 — Save state out of sync with canvas visuals (audit + fix) — `superseded — split into HT-18a/b/c` (audit complete, bma-explorer drift map showed `JSON.stringify(pageStore)` already round-trips all fields; real bug = pushUndo leaks)

#### HT-18a — pushUndo leak fixes on 6 mutations — `done 895a9d7` 2026-05-19

- **commit:** (pending — see commit after this line in `git log`)
- **scope:** Added pushUndo() to toggleScaleLine + showLayer/hideLayer/lockLayer/unlockLayer/soloLayer + applyLandEdgeTag. Purely additive; no schema touch.
- **marker:** PHASE_HT18_OK 7/7 (smoke EXIT 0)
- **forbidden surfaces touched:** NONE — change is additive call insertion only
- **predecessors retained:** PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9, all earlier markers GREEN

#### HT-18a-ext — Extended pushUndo coverage to 22 more mutation sites — `done b2d37af` 2026-05-19

- **scope:** After HT-18a's 6 sites, audit (`sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md`) found 22 additional mutation sites missing pushUndo. Added pushUndo() to: layer reorder (moveLayerUp/Down) + rename + color + toggleLayerLock + bulk vis/lock (setAllLayersVisible / hideOtherLayers / lockOtherLayers / setAllLayersLocked) + toggleLayer / layerHideOthers / layerShowAll + page metadata (setQuickTag / setPageTag / setPageFloorKind / setPageFloorNum / applyAutoNames / excludePage / restorePage2 / hideSelectedPages / rotatePage / resetPageScale + autoNamePage inline) — total 22 sites. Also added 29 sub-checks to `_test_ht18_pushundo_leaks` (now 36/36 GREEN; was 7/7).
- **bulk handling:** `excludePage` / `restorePage2` accept optional `_skipUndo` param so bulk callers (hideSelectedPages loop) push once instead of N times.
- **marker:** PHASE_HT18_OK 36/36 — full E2E 21/21 core markers GREEN, smoke 16/16 GREEN.
- **forbidden surfaces touched:** NONE — additive only.
- **human-test verified:** `/bma-human-test` 2026-05-19 found 3 sites I initially missed (toggleLayer / layerHideOthers / layerShowAll — distinct from toggleLayerLock / hideOtherLayers); fixed inline same iteration. setQuickTag and resetPageScale leak-reports turned out to be early-exit paths (correct behavior: no mutation = no dirty).
- **artifact:** `sprints/active/2026-05-19-ht-18-save-load-audit-fix/`

#### HT-18b — Save/load round-trip E2E coverage — `done-with-test-design-caveat` 2026-05-19 (depends-on HT-18a ✅)

- **scope skill:** `/bma-check-forbidden` (still touches save/load test code)
- **scope:** Write `_test_ht18b_save_load_round_trip` — Playwright: draw 1 of each object type (poly area/opening/line/ref/parking + annotation each kind) + set page tags/floor/north angle/excluded + layer color/lock/vis + projectInfo → invoke saveProject() → reload page → re-load .bmaplan → diff every field against pre-save snapshot. ≥12 per-object-type sub-checks. NEW marker `PHASE_HT18B_OK`. No code change in proto/ui.html expected (HT-18a audit confirmed all fields auto-serialize).
- **est LOC:** ~150 (mostly E2E test)
- **success criterion:** if any field doesn't round-trip → file HT-18c with that specific field fix; if all round-trip → HT-18b PASS and HT-18 series complete

#### HT-18d — applyLoadedProject wipes projectInfo on load — `done` 2026-05-19 ⚠️ **data-integrity** (real user-data-loss fix)

- **scope skill:** `/bma-check-forbidden` (touches `applyLoadedProject` in `proto/ui.html` — save/load surface)
- **discovered by:** HT-18c's `_test_ht18b_save_load_round_trip` diagnostic. `stepTrace.before_apply: '{}'` (cleared) → `stepTrace.after_apply: '{"reqNo":"","cls":""}'` (still empty strings after applyLoadedProject completes). Blob HAS the values (`projectInfo_blob_reqNo: 'HT18B-TEST-001'`) so save side works. Load side wipes them — likely a syncProjectInfoFromForm call inside applyLoadedProject's call chain (buildSidebar / buildTagGrid / buildRightPanel) reads empty form fields back into projectInfo, undoing the `projectInfo=proj.projectInfo||{}` assignment.
- **user-visible symptom:** Open .bmaplan → projectInfo fields (reqNo, buildingType, gfa, classification, userDefinedLimits etc.) lose their saved values silently.
- **scope:** Locate the syncProjectInfoFromForm call in applyLoadedProject's downstream and either (a) re-populate form FROM projectInfo BEFORE that call fires, or (b) defer the syncing.
- **est LOC:** ~10-30 (additive; locate + reorder)
- **success criterion:** HT-18b L_projectInfo can revert from blob-check back to post-load global check + still PASS.

#### HT-18c — `_test_ht18b_save_load_round_trip` eq() comparison fix — `done f1b4331` 2026-05-19

- **scope skill:** `/bma-measure-scope` (touches E2E test only, not app code)
- **diagnosis from HT-18b run 2026-05-19:** 7/13 sub-checks PASS (F-K + M = pageTags / pageNames / pageRotations / floorKind / excludedPages / siteOrientation / layerState). 6 FAIL (A-E + L = poly / opening / line / ref / parking / projectInfo). Failure mode is **test design**, not schema drift — `eq(polyL, tpoly)` uses full JSON equality but `normalizeAllObjects()` runs during save AFTER pre-snapshot is captured (adds `measurementProfile` / `objectCategory` / `reportTarget` / `lawBasis` / `countingRule` / `layerId` / linked-opening parent fields). So `tpoly` ≠ `polyL` even with perfect round-trip. The schema IS symmetric (HT-18a audit confirmed); the test is too strict.
- **scope:** rewrite the 6 failing checks to compare **subset of fields the user explicitly set** rather than full JSON equality. OR move pre-snapshot to AFTER `normalizeAllObjects()` so it captures the post-normalize shape that round-trips.
- **est LOC:** ~30-50 (test-only)
- **success criterion:** PHASE_HT18B_OK 13/13 GREEN with no app code changes.



> **Note 2026-05-19:** A duplicate INV-2026-05-19-002c entry was filed here with HT-18's scope content (misfile). Cleaned up. The authoritative INV-002c card is the next entry below.

#### INV-2026-05-19-002c — F12 Overview mockup-port (faithful) — `done c9b8aa9` (depends-on 002b ✅ — replaces in-place)

- **scope skill:** `/bma-ui-scope` (UI region: canvas-ui standalone mode — same surface as 002b)
- **depends-on:** **002b** (in-place replacement of `_OV_GROUPS`, `_ovBuildGrid` chip logic, `.ov-*` CSS; F12 hotkey + body.overview class kept)
- **est LOC:** ~240 (proto/ui.html ~90, app.css ~120, e2e_ui_test.py ~30)
- **success markers needed:** `PHASE_INV_OVERVIEW_PORT_OK` (10-11 sub-checks supersedes 002b's PHASE_INV_OVERVIEW_OK 9/9 with port-specific assertions: 7 groups present per mockup label list, banner element rendered, white-card bg, scale-1.04 hover, status chips with text labels พร้อม/ตรวจ scale/ยังไม่วัด/auto scale/ยกเว้น, excluded pages flow into title group not filtered, 002a top bar + 001a HUDs not regressed)
- **scope:** Port mockup-spatial-sheet-map.html verbatim. (1) Replace `_OV_GROUPS` 6→7 entries: site/title/plan/elev/section/detail/sys with mockup Thai labels verbatim. (2) Rewrite `.ov-card`/`.ov-thumb`/`.ov-group-grid` CSS to match mockup: 180px white cards on dark grid bg, 124px thumb height, scale-1.04 hover, 16px gap, 54px between groups. (3) Replace status dot with chip-and-dot combo: `<div class="chip"><div class="dot dot-X"></div>LABEL</div>` where LABEL ∈ {พร้อม / ตรวจ scale / ยังไม่วัด / auto scale / ยกเว้น}. (4) Add banner above grid: "💡 45 หน้าทั้งโครงการบน infinite canvas เดียว · คลิก sheet ใดก็ได้เพื่อ zoom เข้า · กด ⌘K เพื่อค้นหา". (5) Remove `excludedPages.has(i) continue` filter — excluded pages flow into title group (per mockup), chip = "ยกเว้น". (6) Group label colors (7 disciplines, per mockup CSS). (7) Card click → existing `_ovCardClick(n)` behavior preserved.
- **forbidden surfaces touched:** NONE (no polyAreaM2/pdfToC/RS/snap/server.py/.bmaplan rename; pure UI port)
- **link:** `docs/invent/f12-overview-mockup-port.md` (§ Research → Delta map is the row-by-row guide)
- **hard rules:** Do NOT redesign — port verbatim. Any deviation requires user check-in. Banner text exact. 7 groups in mockup section order. No separate "excluded group" (that was f12-excluded-group NOGO; mockup integrates into title group).

- [x] **Zen Mode v2 — swap menu bar for spatial-sheet-map top bar** — `invent-done-go (→ INV-2026-05-19-002a + 002b)` 2026-05-19. Verdict `PRIOR_ART_PARTIAL` (top-bar + dropdowns + ⌘K mature individually; composition novel for PDF). 5 approaches on 5 axes; **2 attempts** — v1 framed as extension (rejected), **v2 RESHAPED** as dual-mode (F11+F12 separate). Top approach v2: F11 = A (top bar) + D (Focus) bundled; F12 = C (standalone spatial grid). Spike v2 PASS 8/8 (top bar 40px, F11 actions ≤2 clicks, 7 HUD fields visible, F12 per-card status + lazy load, F12↔F11 roundtrip page sync, Focus + edge peek, HT-7 gate, onboarding toast). 001a F11 behavior deprecated (breaking change + mandatory onboarding). User GO 2026-05-19. 2 sprint cards in active queue (002a→002b). See `docs/invent/zen-mode-v2-topbar.md` + spike `proto/sandbox/invent-zen-mode-v2-topbar.html`.
    - Source: user 2026-05-19 11:39 + screenshot `proto/ui/Screenshot 2026-05-18 221940.png`
    - Tags: bma-plan, ui, zen, top-bar, overview, focus, p-med
    - Sprint split rationale: ~410 total LOC at upper boundary → 002a (F11 ~230 LOC, breaking change) + 002b (F12 ~180 LOC, depends-on 002a)
    - Carry-over: 001a minimap deprecated; ZEN_MENU_ITEMS shared handler array; F-key scope guard; onboarding `PREFS.layout.zenV2Onboarded`; modal z-index audit

#### INV-2026-05-19-002a — F11 Zen + top bar (additive layer over v1) — `done 0915ab5`

> **Reshape 2026-05-19 (user during dev-loop SCOPE):** Original framing = replace 001a `toggleZen()` (breaking). User redirected: "ทำแยกจากของ v1 ไปเลยจะดีกว่า" → **non-breaking additive** approach. 001a `toggleZen()` UNTOUCHED. Add `#zen-topbar` as a new overlay that renders when `body.zen` is active. 001a minimap, 3 HUDs, hide-menubar behavior all UNCHANGED.

- **scope skill:** `/bma-ui-scope` → UI_SCOPE_OK (canvas-ui primary + menu-bar dropdown wiring)
- **depends-on:** 001a (additive — does not modify; reads `body.zen` class set by `toggleZen()`)
- **est LOC:** ~180 (HTML ~40, CSS ~50, JS ~50, E2E test ~40) — reduced from 230 (no `toggleZen()` refactor)
- **success markers needed:** `PHASE_INV_ZEN_V2_OK` (8 sub-checks: top bar present + height ≤44px when zen / 6 dropdowns wired / Focus toggle + edge peek / F-key scope guard / onboarding toast first F11 / 3 HUDs still visible / ⌘K palette composes / no minimap regression); `PHASE_INV_ZEN_OK` 10/10 retained UNCHANGED; `PHASE_INV_PALETTE_OK` 10/10 + `PHASE_INV_POLISH_001C_OK` 5/5 no regression
- **scope:** **Additive layer only.** New `#zen-topbar` overlay (display:none default; `body.zen #zen-topbar { display:flex }`) with 6 dropdowns (File/Page/Measure/Annotate/View/Help, wired to existing handlers by reference) + right-side 4 chips (🔍 ⌘K / 🐦 Overview / ◯ Focus / ◻ Exit). Annotate dropdown stub "Coming soon". F = Focus sub-mode (`body.zen.focus` hides 3 HUDs + 4 edge-trigger strips for hover-peek with 800ms debounce). F-key scope guard (F = Fit outside Zen, F = Focus inside Zen). Onboarding toast on first F11 (gated by `PREFS.layout.zenV2Onboarded` additive bool). 001a minimap, hide-menubar, HUDs, toggleZen() ALL UNCHANGED. F12 Overview button = stub in this sprint (002b separately).
- **forbidden surfaces touched:** NONE
- **link:** `docs/invent/zen-mode-v2-topbar.md` (§ Decision: 002a, reshape note added)

#### INV-2026-05-19-002b — F12 Overview standalone (C) — `done d59a782` (depends-on 002a ✅)

- **scope skill:** `/bma-ui-scope` (UI region: new full-canvas mode + shared top bar from 002a)
- **depends-on:** **002a** (shares `#zen-topbar` chrome; cannot ship before)
- **est LOC:** ~180 (HTML ~30, CSS ~50, JS ~70, E2E test ~30)
- **success markers needed:** `PHASE_INV_OVERVIEW_OK` (criteria 4 + 5 per spike: per-card status dot + object count chip + page name + tag; lazy IntersectionObserver < 45 on init; F12 ↔ F11 atomic roundtrip with `curPage` sync); 002a markers retained
- **scope:** `body.overview` class. `#overview-content` replaces `#canvas` (display:none on canvas when overview). Spatial grid grouped by `pageTags` discipline (site/title/plan/elev/sec/detail/sys) with color-coded group labels. 45 `.ov-card` with status dot (green/amber/red per scale state) + object-count chip + page name + tag. Lazy IntersectionObserver per card; reuses 001a thumb-cache pattern (no new server endpoint — `/page/{n}` not edited). F12 hotkey + `#tb-overview` button. Card click → atomic exit + `loadPage(n)` → land in 002a F11. No measurement / no editing in F12 grid (out-of-scope).
- **forbidden surfaces touched:** NONE (no server endpoint changes; reuses cached pixmap)
- **link:** `docs/invent/zen-mode-v2-topbar.md` (§ Decision: 002b)

    - Source: user 2026-05-19, ชอบ top bar ของ `proto/sandbox/mockup-spatial-sheet-map.html` (logo + 6 dropdowns File/Page/Measure/Annotate/View/Help + ขวามือ 🔍 ค้นหาหน้า ⌘K / 🐦 Overview / ◯ Focus F) — เอามาใช้แทน menu bar เก่าใน Zen Mode
    - Tags: bma-plan, ui, zen, top-bar, overview, focus, p-med
    - Open behavior decisions (to be resolved by `/bma-invent`):
        - 3 corner HUDs ของ INV-001a → merge เข้า top bar / คงลอย / ลบทิ้ง?
        - "Overview" button → spatial sheet map overlay (Approach D ที่แพ้ใน 2026-05-19-01-36)?
        - "Focus" `F` button → ซ่อนแม้แต่ top bar เหลือ canvas อย่างเดียว?
        - "Annotate" dropdown → สร้างใหม่ หรือ trim ออก (current app ไม่มี Annotate menu)?
    - Related: `docs/invent/fullscreen-canvas-ui.md` (Approach D fallback ที่ตัดทิ้ง), INV-2026-05-19-001a/b/c (Zen+Palette trilogy ที่ลงแล้ว), `proto/sandbox/mockup-spatial-sheet-map.html`
    - Scope skill: pending (`/bma-invent` decides after research)
    - Forbidden-surface profile: unknown — `/bma-invent` checks during RESEARCH

- [x] **Fullscreen canvas-only UI + researched sheet navigator** — `invent-done-go (→ INV-2026-05-19-001a + 001b)` 2026-05-19. Verdict `PRIOR_ART_PARTIAL` (Bluebeam F11/AutoCAD Clean Screen/VSCode Zen mature; spatial-map novel for PDF measurement). 5 approaches diverged on different axes (chrome-elim / interaction / persistence / sheet-surface / data-model). Approach A zen+minimap (27/30) selected as top after P5 override (inventor's B-first reco missed criterion #1 "canvas≥92%vh"); B ⌘K palette (28/30) bundled as companion. Spike PASS 6/6 (canvas 96.7% vh, jump in 2 keys, lazy-load 20-25/45 thumbs, F11/Esc/chip exit, HT-7 gate survived). User GO 2026-05-19. Sprint cards in active queue. See `docs/invent/fullscreen-canvas-ui.md` + spike `proto/sandbox/invent-fullscreen-canvas-ui.html` + mockup `proto/sandbox/mockup-spatial-sheet-map.html`.
    - Source: user 2026-05-19, "ทำ ui แบบ fullscreen ให้เหลือแต่ canva และมีแค่ top เมนู ( เมนูที่จำเป็น ) ในแคนว่าเท่านั้น ส่วนเนวิเกต แผ่นงาน ลองทำวิจัยดู"
    - Tags: bma-plan, ui, fullscreen, layout, navigation, p-med
    - Top approach: A zen-mode hard-hide + minimap corner. Composes with B (⌘K palette) inside zen.
    - Carry-over for production sprint: zen onboarding toast (first F11), modal-positioning audit in zen, export-progress in HUD area, selection-panel handling in zen (floating card vs slide-out)
    - 4 fallbacks documented if A fails (D spatial-map full-overlay 25/30 → E ribbon-collapse+page-strip 26/30 → C hover-chrome 24/30 → revisit frame)

- [ ] **iPad rewrite — GoodNotes-style UX** — `invent-queued (parked — Phase 2 candidate)` — from /idea 2026-05-19 (narrowed from mobile-port after bma-researcher feasibility pass)
    - Source: user 2026-05-19, "ลองดูความน่าจะเป็นของโปรแกรมนี้ลง ipad สิ เอา goodnote เป็น ต้นแบบ"
    - Tags: bma-plan, ipad, mobile, ui, architecture, phase-2, p-low
    - Prior analysis: `FEASIBLE_BUT_REWRITE` (bma-researcher 2026-05-19) — 5 blockers: FastAPI no iOS host, PyMuPDF no iOS build, FSA unsupported on Safari iPadOS, zero touch events in current code, GoodNotes is annotation-not-CAD; practical path = native SwiftUI rewrite ~6-12mo → product fork
    - Direction: (unframed — pending /bma-invent FRAME phase; researcher's recommended near-term alternative = make desktop touch-friendly first, then PWA wrapper as 1-week cosmetic pass)
    - Open questions: (pending /bma-invent if revisited)
    - Scope skill: pending (`/bma-invent` decides after research) — note: parked until Phase 1 is fully stable
    - Forbidden-surface profile: unknown — `/bma-invent` checks during RESEARCH

- [ ] **Mobile port — entire program** — `invent-queued` — from /idea 2026-05-19 (user wants all of BMA-Plan available on mobile)
    - Source: user 2026-05-19, "พัฒนาโปรแกรมทั้งหมดลง mobile"
    - Tags: bma-plan, mobile, ui, architecture, p-med
    - Direction: (unframed — pending /bma-invent FRAME phase)
    - Open questions: (pending /bma-invent)
    - Scope skill: pending (`/bma-invent` decides after research)
    - Forbidden-surface profile: unknown — `/bma-invent` checks during RESEARCH

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

INV-2026-05-19-001c `f7d64b8` · INV-2026-05-19-001b `a51207f` · INV-2026-05-19-001a `20e2548` · INV-002 `b6856df` · I-E `504b993` · I-D `dc96f62` · I-C `a490c1e` · I-B4 `91fede9` · I-B3 `c011c4e` · SB-002 `33577b7` · INV-001 `<COMMIT_HASH_PENDING>` · HT-5 `89074cb` · HT-4 `a6973ef` · HT-3 `0900e0a` · HT-2 `acd8636` · HT-1 `e21ca98` · U2 `4bcacc6` · U1 `2101dfe` · SB-2026-05-15-001 `fabc2e9` · Pack G `5dc5dd3` · I-B2b `5c76708` · I-B2a `b9f9132` · I-B1 `c38c3e6` · I-A `984eb7e`

## Stop conditions (loop halts, reports to user, waits)

1. `/bma-check-forbidden` or a scope skill returns **BLOCKED** — a forbidden surface is needed
2. E2E **marker regression** that survives one auto-retry
3. `/bma-human-test` returns **HUMAN_TEST_CRASH**
4. A scope skill returns SPLIT_REQUIRED or design ambiguity needing a **human design choice**
5. The only way forward crosses the **Phase 1 scope boundary**
6. Active queue **and** discovered backlog both empty → clean stop `LOOP_DONE`

## Phase 1 scope boundary (permanent — the loop never auto-adds these)

legal checker · OCR · AI · Rule Engine · FAR/OSR/setback pass-fail verdict · K.1 generator · auto boundary detection · multi-user / SaaS
