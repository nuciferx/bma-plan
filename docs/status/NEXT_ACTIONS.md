# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-22 (updated: LITE-REPORT PASS — editable web report page for lite; LITE-7 or LITE-REPORT v2 optional follow-ups are next)

## Immediate Next

**LITE-REPORT done. /lite/ epic INV-2026-05-21-001 + INV-2026-05-21-002 is now feature-complete (all user-facing outputs: measure + export XLSX/PDF + save/load + web report). Only LITE-7 packaging remains (deferred).**

- **(PRIORITY 1) LITE-7 PyInstaller .exe** — deferred by user; package lite as a standalone Windows executable. The only unfinished item of the LITE epic's 10 locked scope groups. Requires PyInstaller + run.bat changes; zero proto/ edits.

- **(a) LITE-REPORT v2 optional follow-ups** — out of scope for the current sprint; queued as backlog:
  - Custom branding (logo/project name header customisation)
  - Cross-page roll-up summary sheet (total by category across all pages)
  - Persist header/notes edits to .bmaplan (additive schema field `reportEdits{}`)

- **(b) "Lock the site-plan line" E2E guard** — queued, optional. Adds an E2E assertion that no FAR/OSR/setback verdict UI renders anywhere in lite. Currently out of scope for the LITE-REPORT sprint.

- **(c) Lite per-page rotation parity with proto** — optional follow-up. Lite uses a single global V.rot while proto persists per-page server-side rotation. Porting this is a deeper save-format/server change — defer until explicitly requested.

- **(d) Proto backlog — Verify Scale follow-on E** — fold `calibScale.verifyResult` into `phase1Warnings` (amber warning when verify not run or %dev >= 2%) + export note in XLSX/CSV. Additive only; no forbidden surface.

- **(e) Run `/bma-sandbox-test`** — pre-release stress test on large real Downloads PDFs (589 MB BKM, 59 MB RM1). Valid when proto sprint is ready for pre-release.

## Recently Done

- **LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite** — 2026-05-22. PASS. A4-landscape `lite/lite-report.html` opened from File menu via sessionStorage handoff. Plan image + SVG polygon overlay (left); area table grouped by semanticTag with per-group subtotals + page net (right); contenteditable header/row-name/note; read-only area cells; @page print-to-PDF. `GET /report` route added (+9 lines). LITE_REPORT_OK GREEN (17/17). REALFLOW_OK on real 562 MB permit (net 222.22). ZERO proto/ edits. MEASURE_PARITY_OK unchanged.
- **BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite** — 2026-05-21. PASS. Spacebar/middle-mouse pan in any mode (including mid-draw); H sticky pan-tool; setCursor helper; smooth exponential wheel zoom clamped [0.02, 40]; zoomCenter/actualSize; F/Ctrl+0/Ctrl+1/Ctrl+=/Ctrl+- shortcuts; enriched hint text. BUG_20260521_LITE_PAN_OK GREEN (13/13). ZERO proto/ edits. MEASURE_PARITY_OK unchanged.
- **BUG-20260521-lite-menu-clip — lite top-bar dropdowns unclickable** — 2026-05-21. PASS. #topbar overflow:hidden→visible + position:relative;z-index:60. BUG_20260521_LITE_MENU_CLIP_OK GREEN (4/4). ZERO proto/ edits.
- **LITE-0 — scaffold standalone /lite/ tree (epic INV-2026-05-21-001 sub-sprint 1)** — 2026-05-21. PASS. `/lite/` sibling tree scaffolded. `measure-engine.js` vendored byte-identical from `proto/ui.html`. Anti-drift parity gate MEASURE_PARITY_OK (10 fns + 2 consts byte-identical; 5 polys/2 paths/4 coords numeric parity; unit square = 25.00 m2). Skeleton `server_lite.py`, `launch_lite.py`, `ui-lite.html` shell. ZERO proto/ edits. Proto 102 _OK baseline unchanged.
- **HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX** — 2026-05-20. PASS. Area math proven exact (0.08% error). HT-ACC-1: `calibRaw[]` + snap-deviation >5% orange warning (root cause of user's ~1% measurement loss). HT-ACC-2: Verify ribbon button + longest-baseline tip + Verify nudge + land-tool arc hint. HT-ACC-3: exact pts_per_m tooltip on scale status (no measurement change). HT-NAV-1: no code fix. HT_ACC_OK GREEN (5 sub-checks). Full E2E EXIT 0 (102 markers). Commit `c0834f0`. Static-asset safety: NO_BOM on app.css + status-bar.js, CACHE_OK, MAIN_UI_OK. UI_MANUAL_TEST.md updated.
- **BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix** — 2026-05-20. PASS. F11 always exits Zen (unconditional preventDefault, no native-fullscreen desync); F9/F10 keybindings added; dead CSS `~` sibling selector replaced with `:has()`. BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks). Full E2E EXIT 0 (101 markers). Commit `9453777`. Static-asset safety: NO_BOM, CACHE_OK, MAIN_UI_OK. UI_MANUAL_TEST.md updated.
- **INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3** — 2026-05-20. PASS. Page-scoped layer system is now the single authoritative source for render/hit/visibility/lock. Fixes site-plan object overlap bug (objects with `areaType="room"` → slug `"sub_area"` absent from site preset → `layerId=undefined` → overlap). L1: slug-guarantee + render/hit helpers repointed. L2: reassign-layer UI + `objLayerKey` real slug. L3: global `layerVis`/`layerLock` demoted to mirror. INV_LAYER_L1/L2/L3_OK GREEN. HT8D5A restored. 100 _OK markers. Commits: `93c512f` / `1301a12` / `2e6b2f9`.
- **INV-2026-05-20-001 — Verify Scale tool** — 2026-05-20. PASS. Verify Scale flow (approach A): `verifyFinish()` %dev + `openVerifyModal()` green/yellow/red band + Accept/Re-calibrate/Average. `calibPanelOk()` router; `finishCalib()` unchanged. `calibScale.verifyResult` additive schema. `proto/e2e_ui_test.py` +124 lines; INV_VERIFY_SCALE_OK 9/9 all:True. Full E2E EXIT 0. `proto/server.py` NOT TOUCHED.
- **BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode** — 2026-05-20. PASS. +1 line guard in `mode==="sel"` mousedown branch. NEW BUG_20260520_SEL_MIDPAN_OK GREEN. Full E2E EXIT 0 (22 markers). Pipeline: `/bma-bug-report` one-shot.
- **BLOAT-FLAKE-1 — Fix REAL_PDF `_wait_analyse_ready` flake** — 2026-05-20. PASS. `_wait_analyse_ready` timeout 30→60 s + grace window (+50% if still loading). Full E2E EXIT 0: PERSIST_OK/REAL_OK/ANNOT_OK stable. LOOP_STOP_REGRESSION halt cleared. BLOAT-5 retroactively full-validated. Dev-loop unblocked. ~15 LOC in `proto/e2e_ui_test.py` only.
- **BLOAT-5 — Extract page-setup modal JS to `proto/static/js/page-setup.js`** — 2026-05-20. PASS (smoke; full retroactively validated by BLOAT-FLAKE-1). NEW `proto/static/js/page-setup.js` (125 LOC): 15 fns + 2 consts extracted from 3 non-contiguous ranges in `proto/ui.html`. ui.html 3,869→3,777 lines (−92 net). Smoke 18/18 + PHASE_BLOAT5_OK 8/8 + INV_PAGE_SETUP_A/B/C GREEN. Recipe 5-for-5. Session total ui.html 4,231→3,777 (−454 across BLOAT-1..5).
- **BLOAT-4 — Extract annotation JS to `proto/static/js/annotations.js`** — 2026-05-20. PASS. NEW `proto/static/js/annotations.js` (205 LOC): 13 fns extracted from `proto/ui.html` (L1680–1869). ui.html 4,057→3,869 lines (−188 net). full 22/22 + PHASE_BLOAT4_OK 8/8 + PHASE_INV_STICKY_OK 10/10 + PHASE_HT11_OK 10/10 GREEN. Sticky-note round-trip + annotation edit/delete modal verified. Recipe 4-for-4.
- **BLOAT-3 — Extract export/save JS to `proto/static/js/export-save.js`** — 2026-05-20. PASS. NEW `proto/static/js/export-save.js` (188 LOC): 14 fns + 13 consts extracted from `proto/ui.html` inline `<script>`. ui.html 4,208→4,057 lines (−151 net). smoke 18/18 + full 21/21 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN. XLSX_OK + PROJECT_OK + PERSIST_OK + ANNOT_OK all GREEN on real 45-page permit. `schemaOk` verifies 12-field `.bmaplan` v1 schema intact.
- **BLOAT-2 — Extract status-bar JS to `proto/static/js/status-bar.js`** — 2026-05-20. PASS. NEW `proto/static/js/status-bar.js` (49 LOC): 8 status-bar functions + 2 constants extracted from `proto/ui.html` inline `<script>`. ui.html 4,231→4,208 lines (−23). smoke 18/18 + full 21/21 + PHASE_BLOAT2_OK GREEN. PERSIST_OK on real 45-page permit confirms save/load integrity. Recipe proven: cross-script `let`/`const` binding access works in classic non-module scripts.
- **BLOAT-1 — CLAUDE.md LOC drift fix + consolidation trigger rule** — 2026-05-19. DOCS-ONLY. Corrected `proto/ui.html` LOC in `CLAUDE.md` (~1,700→~4,230) and `proto/server.py` (~1,370→~1,750). Added Size discipline trigger rule (>5,000 lines → must extract). BLOAT-2..5 queued in PHASE_INDEX.md active queue. py_compile PASS; no E2E.
- **INV-2026-05-19-003b — /export-png ZIP endpoint (Path C)** — 2026-05-19. NEW `/export-png` POST endpoint in `proto/server.py` (additive). PyMuPDF render per selected page at requested DPI scale. ZIP bundle. Export menu wired. `PHASE_INV_EXPORT_PNG_OK` PASS. full EXIT 0. Commits: `612de96` feat + `7f0300f` docs.
- **HT-18c — Save/load round-trip 13/13 GREEN** — 2026-05-19. Fixed `_test_ht18b_save_load_round_trip` eq() over-strict comparison + `applyLoadedProject` `_projInfoSnap` restoration bug. `PHASE_HT18B_OK` 13/13 GREEN. **HT-18 series complete.** Commits: `f1b4331` fix + `9297ed4` docs.
- **INV-2026-05-19-003a — Print canvas per page (Path B)** — 2026-05-19. "Print Current Page" + "Print Selected Pages" File menu items. `canvas.toDataURL + window.print`. `PHASE_INV_PRINT_CANVAS_OK` 8/8 PASS. full EXIT 0. Commits: `b4f7235` feat + `8200ef6` docs.
- **HT-18a-ext — Extended pushUndo() coverage to 22 more mutation sites** — 2026-05-19. `pushUndo()` inserted at 22 additional mutation sites (layer reorder/rename/color/lock/visibility helpers, page tag/floor/name/exclude/restore/rotate/reset helpers, `pageCtxMenu` inline `autoNamePage` call). `_test_ht18_pushundo_leaks` expanded 7 → 36 sub-checks. `PHASE_HT18_OK` 36/36 = `{'all': True}`. full EXIT 0. HUMAN_TEST_PASS (3 sites found inline: `toggleLayer`, `layerHideOthers`, `layerShowAll`). `proto/server.py` NOT touched. No schema change.
- **INV-2026-05-19-002b — F12 Overview standalone (C)** — 2026-05-19. `body.overview` class; `#overview-content` 6-discipline card grid; lazy IO thumbs; `_ovBuildGrid`/`_ovCountObjects`/`_ovCardClick` atomic page-sync; F12 hotkey; Esc priority guard; `#ztb-chip-overview` unstubbed. `PHASE_INV_OVERVIEW_OK` 9/9; smoke + full EXIT 0; TEST-H SKIPPED (additive new mode). Zero forbidden-surface edits. Zen Mode suite complete.
- **INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled)** — 2026-05-19. `#zen-topbar` 40px overlay (6 dropdowns + 4 chips); `toggleZenFocus()` Focus sub-mode; `_setupZenEdgePeek()`; v2 onboarding toast. `PHASE_INV_ZEN_V2_OK` 9/9; smoke + full EXIT 0; HUMAN_TEST_PASS. 001a `toggleZen()` UNTOUCHED. Zero forbidden-surface edits.
- **INV-2026-05-19-001c — Zen+Palette FRICTION polish** — 2026-05-19. HT-Z-1: `_zenSyncHud()` direct `pageNames[curPage]` read (no MutationObserver lag). HT-Z-2: amber Scale chip when auto-unverified/no scale + tooltip. HT-Z-3: Thai-tag empty-state hint in palette. `PHASE_INV_POLISH_001C_OK` 5/5; smoke + full EXIT 0; TEST-H SKIPPED (sub-200-LOC, all branches marker-covered). Zero forbidden-surface edits. Trilogy complete.
- **INV-2026-05-19-001b — ⌘K Command Palette** — 2026-05-19. Ctrl+K fuzzy page jump modal; 5 helpers (`togglePalette`/`closePalette`/`filterPalette`/`_palJumpToIdx`/`_palMoveSel`); ArrowDown/Up/Enter/Esc nav; mid-draw guard; Zen Mode compose (z-index 9500); color-coded tag chips. `PHASE_INV_PALETTE_OK` 10/10; smoke + full EXIT 0; JOURNEY_OK 13/13 steps; 0 JS errors. HT-Z-3 filed. Idea `2026-05-19-01-36`, sprint 001b of 3.
- **INV-2026-05-19-001a — Zen Mode + Sheet Minimap** — 2026-05-19. `body.zen` chrome-hide; 3 corner HUDs; lazy minimap (IntersectionObserver, malloc-safe); F11/Esc toggle; PREFS additive; `PHASE_INV_ZEN_OK` 10/10; smoke + full EXIT 0; JOURNEY_OK (45-page permit). HT-Z-1/HT-Z-2 filed. Idea `2026-05-19-01-36`, sprint 001a of 3.
- **Ribbon Cleanup Polish** — 2026-05-19. `body { font-size }` 16px → 14px (revert after Chrome layout shift). `#scale-badge` hidden from ribbon. `#active-layer-select` ribbon-group hidden (preserved in DOM). `#btn-report` rewrapped in `.rsection` + `.rlbl` + `.rrow` (uniform 60px height). py_compile PASS, smoke PASS (all pre-existing markers GREEN). Zero forbidden-surface edits.
- **INV-2026-05-18-002 — Settings v2: export defaults + loupe prefs** — 2026-05-19. 4 new PREFS additive in settings.v1: csvSeparator / includeLawBasis / loupe.radius / loupe.zoomFactor. exportCSV separator-aware; updateLoupe zoom-factor-driven. SETTINGS_V2_OK 6/6; SETTINGS_OK (v1) still GREEN. Commit `3e71865`.
- **INV-2026-05-18-001c — Page delete + renumber-map + /rebuild-pdf** — 2026-05-19. NEW /rebuild-pdf endpoint. PyMuPDF doc.delete_page() reverse-order. _reindexPageDicts across 7 per-page dicts. Hard-block during draw, last-page guard, pushUndo(), Foxit-style warning. PHASE_INV_PAGE_SETUP_C_OK 7/7. Commit `ebb521c`. Research: `afd4e71` Q1-Q4 locked in `docs/invent/page-setup-redesign.md`.
- **INV-2026-05-18-001b — Floor sub-types for plan pages** — 2026-05-19. pageFloorKind/pageFloorNum additive schema. autoNamePage floor-aware. Save/load round-trip. PHASE_INV_PAGE_SETUP_B_OK 9/9. Commit `798e5c3`.
- **INV-2026-05-18-001a — Page Setup left inspector + traffic-light chips** — 2026-05-18. Dashboard ⇄ page-card switch. Traffic-light dot (green/amber/red). Object-count chip. PHASE_INV_PAGE_SETUP_A_OK 8/8. Commit `e85a5ce` (initial repo commit).
- **UI Redesign Batch HT-12..HT-15** — 2026-05-18. 15 sprints, 22 commits, smoke 54/54 GREEN. Top menu absorbs Workspace ribbon. Polygon dropdown popover. Right panel renderers. Density picker. Panel collapse buttons.
- **INV-2026-05-17-001 — Freeform area measurement** — 2026-05-17. Alt-at-mousedown enters streaming freehand sub-mode (distance-bin sampling 6 px gate). Mixed click+drag in one polygon. Shift/Ctrl live tolerance modulation. rdpSimplify RDP helper (~25 LOC, inline). obj.freeform additive metadata. PHASE_FREEFORM_OK 7 sub-checks (errPct=0.46%, 240 raw → 16 decimated). polyAreaM2/snap/server all untouched. full 44/44 GREEN. Commit 023b988. TEST-H skipped (Alt-mousedown not exercised by bma-human-journey-tester).
- **HT-6 — arc-guideline live preview** — 2026-05-17. Live arc preview in `redraw()` draft block: dashed arc from last vertex curving through through-point to cursor when `guidePoint` set + `mArcDraft.pending`. `computeArcEdge` reused. `PHASE_HT6_OK` 4 sub-checks. full 42/42 GREEN. Zero forbidden-surface edits. Source: user-test 2026-05-17 "ขาดเส้น guideline เหมือนของเส้นตรง". Commit `ecb44d4`. TEST-H skipped (render-only branch; journey tester does not exercise arc-mode interactively).
- **CIRCLE_RENDER — Analytic circle/ellipse render** — 2026-05-17. `_renderPolyEdges` short-circuit branches: `ctx.arc` for circle, `ctx.ellipse` for ellipse; else legacy flow unchanged. Storage/snap/area math untouched. `CIRCLE_RENDER_OK` 7 sub-checks. full 41/41 GREEN. Last pre-loop leftover cleared. Refs: `docs/status/PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`. Commit `1bf61ca`.
- **dev-website — Static docs site** — 2026-05-17. `proto/static/docs/index.html` + `scripts/build_docs.py` + 5 Thai manual files + `content.json` (28 pages, 4 groups). `DOCS_SITE_OK` 7 sub-checks. full 41/41 GREEN. User GO 2026-05-17 (invent-pending-checkpoint → done). `proto/ui.html` UNTOUCHED. Commit `1bf61ca`.
- **INV-002 — Unified Settings/Preferences modal** — 2026-05-17. `bmaPlan.settings.v1` localStorage key (version:1); `getPref`/`setPref`; `migrateFromLegacy()` (flexible `preset||mode` lookup + visible extraction); 4-tab modal (วาด/หน่วย/หน้าจอ/Widgets); Draft/Apply/Cancel/Reset; `Ctrl+,` shortcut; bad-JSON + wrong-version safety. `SETTINGS_OK` 13 sub-checks. Resolves 3 checkpoint carry-overs (legacy key shape / widget coupling / Apply-on-save). full 38/38 GREEN. Commit `b6856df`.
- **I-E — Building-to-building distance + wallEdges** — 2026-05-17. `WALL_EDGE_TYPES` catalog (4 types); `wallEdgeType` additive on edges; `computeBuildingPairsForPage`; "ระยะระหว่างอาคาร (2h pre-check)" in siteplan tab (facts only, no verdict). `PHASE_I_E_OK` 9 sub-checks. full GREEN. Commit `504b993`.
- **I-D — 4-direction setback + compass overlay** — 2026-05-17. `landEdgeRole` on edges; `computeEdgeSetback` generalizing front-only setback to 4 directions; `#canvas-compass` SVG + `northAngle` in pageTags; Page Setup input. `PHASE_I_D_OK` 10 sub-checks. full GREEN. Commit `dc96f62`.
- **I-C — "ผังบริเวณ" 5th Summary Widget tab** — 2026-05-17. `updateSiteplanTab()` renders `collectSummaryData()` inline; BCR/OSR/FAR/Permeable + per-tag breakdown + markers + setback + Phase 1 footer note. `PHASE_I_C_OK` 10 sub-checks. full GREEN. Commit `a490c1e`.
- **I-B4 — Site Plan 6-step stepper widget** — 2026-05-17. `#site-stepper` collapsible advisory; `updateSiteStepperUI()` reads existing page/project state; hooks in `updateBottomBar`/`loadPage`. `PHASE_I_B4_OK` 10 sub-checks. full GREEN. Commit `91fede9`.
- **I-B3 — Properties panel site fields** — 2026-05-17. `isBuildingTag` helper; `buildingHeight_m` editable input in Properties; 7 site tags appended to Semantic Tag dropdown on site pages. `PHASE_I_B3_OK` 10 sub-checks. full GREEN. Commit `c011c4e`.
- **SB-002 — Upload-cap UX modal** — 2026-05-17. `currentUploadCapMB` from `/upload` echo; `showUploadCapModal`; `updateCapBadge` cold-start hint; 413 suggestions. `SB002_UPLOAD_UX_OK` 8 sub-checks. full GREEN. Commit `33577b7`.
- **INV-001 — Arc-polygon hybrid measurement** — 2026-05-17. 3-click inline arc; `polyMetricsAnyShape` shim; `ARC_POLYGON_OK` 7 sub-checks (err=0.000000%). smoke 29/29 + full 32/32 GREEN. Bug fixed mid-sprint: `replace_all` → infinite recursion → targeted Edit fix. Commit `b89e206`.
- **HT-5 — `.dd-submenu` overflow on short viewports** — 2026-05-15. CSS-only fix: `.dd-submenu` += `max-height:calc(100vh - 120px); overflow-y:auto; overflow-x:hidden; scrollbar-width:thin` ใน `proto/static/css/app.css:25`. Measure site submenu (15 items) ที่ล้น viewport สั้น (412 px tall) scroll ได้แล้ว. NEW marker `PHASE_HT5_OK` 3 sub-checks. py_compile PASS + full **31/31 GREEN**. Same CSS rule ที่เคย bundle กับ HT-1 แต่ revert ตาม one-sprint-one-commit rule — มาแล้วใน iteration นี้แทน. Autonomous Dev Loop iteration 10. **All HT-1..5 human-test findings cleared.**
- **HT-4 — Name panel dismissal paths** — 2026-05-15. NEW `autoCloseNamePanel()` helper + 3 dismissal paths ใน `proto/ui.html`: (1) document `mousedown` listener — auto-close panel เมื่อคลิกนอก, 300ms grace ป้องกัน click ที่เพิ่งเปิด panel นั่นเองมาปิดทันที, auto-confirm ถ้า input มีค่า / cancel ถ้าว่าง; (2) `loadPage()` เรียก `autoCloseNamePanel()` ก่อนทำงานเพื่อ commit ค่าก่อน navigate; (3) global Esc handler intercept `if (namePanel open) cancelName()` ก่อน fall through ไป Esc logic อื่น — เดิมแค่ set `display="none"` ทำให้ callback ไม่ fire object ไม่ได้ชื่อ. NEW `namePanelOpenedAt` timestamp. NEW marker `PHASE_HT4_OK` 9 sub-checks (cancel-on-empty, finish-on-value, loadPage source check, Esc dispatchEvent callback fire). py_compile PASS + full **30/30 GREEN**. Autonomous Dev Loop iteration 9.
- **HT-3 — `lbl-mode` site-tag context** — 2026-05-15. Extracted `updateModeLabel(m)` helper จาก inline setMode logic + เพิ่ม `SITE_TAG_THAI_LABELS` map (7 ป้าย Thai สำหรับ site tags — `SEMANTIC_TAG_LABELS` ใน semantic-meta.js เป็น key→key ไม่ใช่ Thai) + extracted `MODE_BASE_LABELS` const. `lbl-mode` ใน status bar แสดง `วัดพื้นที่ ⬡ (ผังบริเวณ — ปกคลุมอาคาร)` ตอน site area tool active; suffix update เมื่อ switch site tag; clear ตอน `finishCurrentArea` (เพิ่ม `updateModeLabel()` call หลัง `curSiteSemanticTag=null`). Marker tools ที่ `curMarkerType !== "parking"` ก็ได้ `(<markerLabel>)` suffix ด้วย. NEW marker `PHASE_HT3_OK` 7 sub-checks. py_compile PASS + full **29/29 GREEN**. Autonomous Dev Loop iteration 8.
- **HT-2 — `⬡ NaN ตร.ม.` display guard** — 2026-05-15. เพิ่ม consumer-layer helpers `fmtAreaM2(v, hint)` + `fmtDistM(v, hint)` ใน `proto/ui.html` ข้าง `polyAreaM2` (additive — `polyAreaM2` เป็น forbidden surface ไม่แตะ). คืน "—" สำหรับ `null`/`NaN`/`undefined`/`Infinity`, รับ hint string ได้ (เช่น "ตั้ง scale ก่อน"). แทน guard `area != null ? area.toFixed(2)+" ตร.ม." : "—"` ที่ 10 display sites: measure-result × 2 paths, summary widget (area/floor/site tabs + breakdown by type), objMetricText (poly/opening/line/ref), rp-metric Gross/Opening/Net ใน buildLeftProperties + buildRightPanel, drawPolyLabel area row. NEW marker `PHASE_HT2_OK` 12 sub-checks incl. live-DOM scan สำหรับ "NaN ตร.ม." substring. py_compile PASS + full **28/28 GREEN**. Pre-existing formats unchanged (VECTOR_OK 305.56 / RECAL_OK 0.75 / XLSX_OK 0.16 / ANNOT_OK / PERSIST_OK / REAL_OK ทั้งหมด normal). Autonomous Dev Loop iteration 7.
- **HT-1 — `.dd-submenu` z-index 1→201** — 2026-05-15. แก้ `.dd-submenu` z-index `1` → `201` ใน `proto/static/css/app.css:25` (1 บรรทัด). Submenu ใน Measure / Project / Snap-modes / Layer-set-active render เหนือ sibling overlay ได้แล้ว (เหนือ `.dropdown:200` ใน same stacking context; `.menu-bar:9000` ครอบทั้งหมดอีกชั้น). NEW marker `PHASE_HT1_OK` 3 sub-checks (`found`, `aboveSiblingThreshold ≥201`, `ruleZ matches computedZ`). py_compile PASS + full **27/27 GREEN**. HT-5 (`.dd-submenu` overflow on short viewports) **ไม่ bundle** กับสปรินต์นี้ — รอ next iteration. Autonomous Dev Loop iteration 6.
- **U2 — 1-Page Excel Summary** — 2026-05-15. เพิ่มปุ่ม "⬇ Export Summary (1 หน้า)" ในแผง Export ข้าง Export Excel เดิม. NEW endpoint `/export-xlsx-summary` ใน `proto/server.py` (~165 บรรทัด) render 1-sheet "สรุปผังบริเวณ" บน A4 landscape `fit_to_pages(1,1)`. Client `collectSummaryData()` รวม area ตาม 7 site `semanticTag` + คำนวณ BCR/OSR/FAR/Permeable% (plain numbers, ไม่มี verdict) + front-setback (min dist to road ref) + marker counts (via markerType จาก I-B1). Server echo limits จาก projectInfo.userDefinedLimits ข้างค่าจริงโดยไม่ตัดสิน. Footer note: "ไม่มีการพิจารณาผ่าน/ไม่ผ่านตามกฎหมาย". NEW marker `PHASE_U2_OK` 16 sub-checks (9 structural + 7 live server: 7354-byte XLSX returned, PK magic, custom `X-Bma-Summary-Mode: 1-page` header, `_summary.xlsx` filename). py_compile PASS + full **26/26 GREEN**. Zero forbidden-surface / `.bmaplan` schema / `/export-xlsx` (เดิม) edits. setback v1 covers only front; back/side1/side2 deferred to Phase I-D. Autonomous Dev Loop iteration 5.
- **U1 — Save Annotated PDF in-place** — 2026-05-15. เพิ่มเมนู `📄 Save PDF (ทับไฟล์เดิม)` ใน Project dropdown + ปุ่มลัด `Ctrl+Shift+S`. ปุ่ม "📂 เปิด PDF" intercept click → ลอง `showOpenFilePicker()` ก่อน (Option B จาก SCOPE checkpoint), ถ้าได้ readwrite handle จะเก็บใน `currentSourcePdfHandle` ผ่าน `uploadPdfFile(file, sourceHandle)` 2-arg. `saveSourcePdfInPlace()` POST `/export-pdf` (ทุกหน้า + annotations) แล้วเขียนทับด้วย `handle.createWritable()`/`write`/`close` หรือ fallback `dlBlob(blob, <safe>_annotated.pdf)`. ~50 บรรทัดใน `proto/ui.html` + `_test_u1_save_pdf_in_place` 9 sub-checks + marker `PHASE_U1_OK`. py_compile PASS + full **25/25 GREEN**. Zero forbidden-surface edits, zero `.bmaplan` schema change, zero `proto/server.py` edits. Autonomous Dev Loop iteration 4. Manual UI verification of FSA permission prompt deferred to `UI_MANUAL_TEST.md` housekeeping.
- **SB-2026-05-15-001 — Raise MAX_UPLOAD_BYTES** — 2026-05-15. `MAX_UPLOAD_BYTES` ยกจาก 80 MB เป็น 256 MB ใน `proto/server.py:51` พร้อม env-var override `BMA_MAX_UPLOAD_MB` (default 256). `/upload` echoes `max_upload_mb` ใน response. เพิ่ม `_test_upload_cap()` + marker `UPLOAD_CAP_OK` ใน `proto/e2e_ui_test.py`. smoke 21/21 + full 24/24 GREEN. HUMAN_TEST_PASS. SB-002 upload-cap UX unblocked. Autonomous Dev Loop iteration 3.
- **Pack G — Sandbox Test Pre-Release Gate** — 2026-05-15. สร้าง pre-release gate 3 ชิ้น: skill `/bma-sandbox-test` + subagent `bma-sandbox-journey-tester` + subagent `bma-issue-triager` ใน `.claude/`. รัน first-run กับ `sandbox/251121_CHH_Submission_REV2 - Copy.pdf` (90.8 MB) — Tier 1 FAIL (HTTP 413, `MAX_UPLOAD_BYTES=80 MB`), Tier 2 skipped, verdict = SANDBOX_TEST_ISSUES. Triage filed SB-2026-05-15-001 (BROKEN, top of queue) + SB-2026-05-15-002 (FRICTION, after SB-001). ปรับ `CLAUDE.md`, `AGENTS.md`, `PHASE_INDEX.md`. ไม่มี app code เปลี่ยน. Subagents ต้อง session restart ก่อน invoke โดยตรง.
- **Phase I-B2b — Measure menu submenu (site plan)** — 2026-05-15. เพิ่ม `dd-site-submenu-trigger` + `dd-site-submenu` (7 area + 8 marker items) ใต้ Measure menu — visibility tracks `pageTags[curPage]==="site"`, dispatch ตรงไปยัง `activateSiteAreaTool`/`setMarkerType` (shared handlers จาก I-B2a 100%). แก้ bug explicit `closeAllMenus()` collision กับ bubble-up `toggleMenu` → remove, bubble-up จัดการเอง. E2E marker `PHASE_I_B2B_OK` PASS. smoke 20/20 + full 22/22 GREEN. Filed 5 HT findings (HT-1/HT-2 BROKEN, HT-3/HT-4 FRICTION, HT-5 COSMETIC) ลงใน `PHASE_INDEX.md`.
- **Phase I-B2a — Site Plan ribbon group + shared handlers** — 2026-05-14. เพิ่ม `#ribbon-site` DOM group (7 area + 8 marker buttons, site-page-only) + state `curSiteSemanticTag`/`curMarkerType` + 4 functions (`activateSiteAreaTool`, `setMarkerType`, `updateSiteRibbon`, `updateSiteRibbonActive`) + areaType↔semanticTag bridge ใน `finishCurrentArea` (consume-and-clear). E2E marker `PHASE_I_B2A_OK` (7 sub-checks) PASS. smoke 19/19 + full 22/22 GREEN. Sprint card: `sprints/completed/2026-05-14-phase-i-b2a-site-ribbon/`. รันโดย Autonomous Dev Loop iteration 1 (supervised).
- **Phase I-B1 — markerType additive field** — 2026-05-14. เพิ่ม `MARKER_TYPE_LABELS` registry 9 ประเภท + field `markerType:"parking"` ใน marker creation literal (ข้าง `parkingType` เดิม — additive, ไม่ rename) + backfill loop ใน `applyLoadedProject` สำหรับ marker เก่า; E2E marker `PHASE_I_B1_OK` (3 sub-checks: registryComplete, markerTypeRoundTrips, backfillWorks). smoke 18/18 + full 21/21 GREEN. เป็น sub-sprint แรกจากการ SPLIT Phase I-B → I-B1/I-B2/I-B3. Sprint card: `sprints/completed/2026-05-14-phase-i-b1-marker-type/`.
- **Phase I-A — Site Plan Schema + Project Setup** — 2026-05-14. เพิ่ม 7 area semanticTags (`building_coverage`, `open_space`, `permeable_area`, `hardscape`, `softscape`, `parking_area_outdoor`, `internal_road`) ใน `semantic-meta.js` (5 maps) + `SEMANTIC_TAG_LABELS`; Project Setup "ผังบริเวณ" section 11 inputs (buildingClassification, buildingUseType, zoneCode, siteAccessRoadWidth_m, 6 userDefinedLimits); `buildingHeight_m:null` บน poly literal; E2E marker `PHASE_I_A_OK` (7 sub-checks). smoke 17/17 + full 20/20 GREEN. Sprint card ย้ายไป `sprints/completed/2026-05-14-phase-i-a-schema/`.
- **Measure Pack Skills + Subagents (Pack E)** — 2026-05-14. Added 4 skills (`/bma-measure-scope`, `/bma-measure-ux`, `/bma-measure-geometry`, `/bma-measure-regression`) + 3 subagents (`bma-path-geometry-reviewer`, `bma-measure-ux-specialist`, `bma-measure-regression-guardian`) under `.claude/`. **Slim** pack chosen after a size review of the original 7+6 spec — geometry/shape/curve consolidated into one skill (shared path model), validation folded into the regression skill, snap-conflict review folded into the UX specialist, `bma-measure-architect` + `bma-snap-interaction-reviewer` dropped. Safe section-by-section workflow for Measure features without destabilizing the area-math contract. Docs-only — no app code touched. First Measure sprint to exercise Pack E: `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER` or Phase I-B.
- **Menu Bar / Canvas Overlay Z-Index Fix** — 2026-05-14. แก้ `.menu-bar` `position:static` → `position:relative` + z-index 9000; แก้ `#check-panel` `top` offset ให้เริ่มที่ 94px (ต่ำจาก topbar+menu+ribbon); raise modal ทุกตัวเป็น 9001–9002; lower loupe/recent-dropdown เป็น 8998–8999. smoke 16/16 GREEN. **`UI_MANUAL_TEST.md` ยังค้าง** — ต้องเปิด Chrome จริงยืนยัน dropdown z-index + close behavior.
- **UI Specialist Skills + Subagents (Pack D)** — 2026-05-14. Added 7 skills (`/bma-ui-scope`, `/bma-ui-menu`, `/bma-ui-ribbon`, `/bma-ui-panel`, `/bma-ui-canvas`, `/bma-ui-status`, `/bma-ui-regression`) and 8 subagents (`bma-menu-bar-specialist`, `bma-ribbon-specialist`, `bma-left-panel-specialist`, `bma-right-panel-specialist`, `bma-canvas-ui-specialist`, `bma-summary-widget-specialist`, `bma-status-bar-specialist`, `bma-ui-regression-guardian`) under `.claude/`. Section-by-section UI workflow for any future UI sprint without destabilizing measurement core. Docs-only — no app code touched.

## Immediate Next

**INV-freeform-area cleared. Active queue is now empty (freeform-area was the only `invent-done-go` item). Invent backlog empty. Next `/loop /bma-dev-loop` iteration would halt with LOOP_DONE stop-condition immediately.**

Eligible work remaining:
- **(a)** `bma-human-journey-tester` enhancement to cover Alt-drag freehand + arc-mode interactive sub-tests (TEST-H skipped for INV-freeform and HT-6; file as small sprint if user wants automated coverage)
- **(b)** `build_docs.py` hook into `/bma-sprint-finalize` skill — small sprint to prevent stale docs bundle drift
- **(c)** `/bma-ui-menu` sprint to wire Help dropdown to `/static/docs/` (deferred from dev-website sprint to preserve "zero ui.html edits" boundary)
- **(d)** Capture new `/idea` entries from continued user testing of freeform + arc tools

---

**Two design docs ready for review — implementation order is user's choice:**

### A. `SITE_PLAN_MEASUREMENT_PLAN_IMPLEMENTATION` — queued (Phase I pre-planning done 2026-05-13)

Specs (both DONE 2026-05-13):
- [`docs/design/SITE_PLAN_MEASUREMENT_PLAN.md`](../design/SITE_PLAN_MEASUREMENT_PLAN.md) — what to measure
- [`docs/design/SITE_PLAN_UI_MOCKUP.md`](../design/SITE_PLAN_UI_MOCKUP.md) — UI mockups + programme guideline (user journey, screen ASCII mockups, component specs, data flow, where in `proto/ui.html`)

Goal: Add measurement support for site plan (ผังบริเวณ) per กฎกระทรวง 33 + 55. **No legal pass/fail — capture facts only, user-defined limits.**

Recommended implementation phases (each = separate sprint):
- **I-A** (lowest risk, additive only): semanticTag enum additions + AREA_LABELS + Project Setup `buildingClassification`/`buildingUseType`/`userDefinedLimits`/`zoneCode` fields + applyLoadedProject backward-compat
- **I-B**: Site Plan toolbar buttons + new marker types (parking_fire, parking_ambulance, entrance, aed, sign)
- **I-C**: Summary Widget tab "ผังบริเวณ" + BCR/OSR/FAR/%permeable display + 4-direction setback grouping + XLSX sheet additive
- **I-D** (highest risk for scope creep): "measured X / user-limit Y" side-by-side display — **must remain neutral facts, no verdict UI**
- **I-E** (most complex): Building-to-building distance (มร.55 ข้อ 48) — wallType per edge + distance pair measurement

~~5 open questions in `SITE_PLAN_MEASUREMENT_PLAN.md §16` must be decided before I-A.~~ ✅ **DECIDED 2026-05-13** — Q1=A (user-defined limits, no Rule Engine), Q2=A (`building_coverage` polygon + `buildingHeight_m` field), Q3=A (separate polygon per building), Q4=Defer (2h rule waits for Phase H.0), Q5=A+B without link (marker + polygon both, auto-count link deferred to I-C+). **Phase I-A unblocked.** See `SITE_PLAN_MEASUREMENT_PLAN.md §16` (DECIDED) for full rationale and Phase I-A scope summary.

### B. `PHASE_H_PATH_GEOMETRY_IMPLEMENTATION` — **DONE (2026-05-13)**

Sprint complete. PATH_GEOMETRY_OK passes all 5 tests A–E. All 19 E2E markers PASS. See `sprints/completed/2026-05-13-path-geometry/RUN_PATH_GEOMETRY.md`.

**Visual audit complete (2026-05-14):** Phase H.1 math is fully correct. Circle/ellipse "polygonal" symptom = UI wiring gap (not a regression). See [`docs/status/PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`](PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md). Fix = `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER` (see §0 above).

---

## Prior Status (2026-05-11)

**`RUN_WIDGET_MENU_PLACEMENT_SYSTEM` DONE (2026-05-11)** — `docs/status/WIDGET_MENU_PLACEMENT_SYSTEM.md`. Added `WIDGET_MENU_REGISTRY`, localStorage key `bmaPlan.widgetPlacement.v1`, Widget/Menu UI in Layout Options panel (search, category filter, visibility toggle, region/order/size controls, reset), `.widget-size-*` CSS, and E2E coverage. Movable widgets: `workflow`, `reviewWarnings`, `exportReady`. Other widgets locked-by-region to keep current page layers / sheets / objects / properties workflow intact. No backend, save/load, schema, or coordinate math changes. py_compile + smoke + full PASS.

PyMuPDF render audit complete (2026-05-11) — `RUN_PYMUPDF_RENDER_REGRESSION_COMPARE` PASS.

**Finding: NO code regression.** Old and current `/page/{n}` render path are identical.
Measured bottleneck: **JPEG encode (`tobytes`) takes 93% of render time** at scale=1.5.
- Test PDF at 1.5×: `get_pixmap=110ms  encode=1366ms  total=1476ms`
- Real 45-page permit PDF at 1.5×: ~15 000ms — legitimate cost of large complex page, not a bug.

**Instrumentation added:** `[BMA_PAGE_RENDER_PERF]` server log line on every `/page/{n}` request.
Check server terminal for: `session=Xms cache=Xms get_pixmap=Xms encode=Xms bytes=N total=Xms MISS/HIT`

**`RUN_RENDER_SCALE_REDUCE` BLOCKED** — attempted 2026-05-11. Changing render scale from 1.5→1.2 causes coordinate math regression (setback distances shift by factor 1.5/1.2 = 1.25). `RS` is deeply embedded in `pdfToC()`, `cToPdf()`, and E2E `raw()` helper. Cannot reduce render scale without refactoring all coordinate-dependent code — out of current sprint scope.

**`RUN_MAIN_PAGE_RENDER_PRIORITY_FIX` DONE** — 2026-05-11. Removed `buildSidebar()` from `startCheck()` before `loadPage()`; thumbnails now load only after main page is visible. Added `BMA_THUMB_RENDER_PERF` logging. Cache keys improved for thumb/thumb-md. All tests PASS.

**`RUN_PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER` BLOCKED** — 2026-05-11. Attempted preview (quality 50) → full (quality 75) progressive rendering. Smoke test failed with `malloc (27MB) failed` due to concurrent renders (preview + full + thumbnails). Progressive rendering doubles server load, not suitable for single-process FastAPI + PyMuPDF with limited memory. Reverted.

**Alternative performance wins (safe, no coordinate impact):**
- Reduce `jpg_quality` (88 → 70) in `get_page` — cuts bytes without changing pixel dimensions
- Tune `MAX_IMAGE_CACHE_ENTRIES` / `MAX_IMAGE_CACHE_BYTES` for more cache hits
- Cache key improvement already done: format+quality now included in key

Pre-first-page JS fixed (2026-05-10) — `RUN_PRE_FIRST_PAGE_LOAD_REGRESSION_AUDIT` PASS.

**Open Bug:** TC-12-B1 (MINOR) — `lbl-save-state` stays "Manual save required" instead of "Unsaved changes" after `pushUndo()` when no prior save has occurred. Cosmetic only.

Performance sprints queue:
1. RUN_RENDER_SCALE_REDUCE.md — reduce default render scale 1.5→1.2 (fastest safe win)
2. RUN_SAVE_STATE_LABEL_FIX.md — fix TC-12-B1 save state label (MINOR)

Remaining UI polish sprints:
1. RUN_RIBBON_TOOLBAR_POLISH.md — mockup-style ribbon polish without fake actions
2. RUN_RIGHT_LAYERS_FINAL_POLISH.md — final Layers-first right panel polish
3. RUN_PAGE_FLOOR_SETUP_PANEL.md — page/floor setup usability polish
4. RUN_SCALE_MANAGER_FOUNDATION.md — audit-only scale overview
5. RUN_REVIEW_WARNING_PANEL_POLISH.md — grouped warning panel
6. RUN_EXPORT_READY_PANEL_POLISH.md — export readiness UI summary
7. RUN_UI_VISUAL_CONSISTENCY_PASS.md — final visual consistency pass

## Backlog (Longer Term)

- Left panel Properties refinement (scroll, focus, keyboard navigation)
- Parking-specific rows in สรุปตาม Report Target
- Reference arcs/circles (curved path Sprint 5)
- Manual opening parent reassignment further UX improvements
- iPad touch UX (Sprint 6)
- Full scale record with calibration endpoint storage
- Summary widget (tabbed: Area/Floor/Site/Warnings) — requires per-page backend summary

## Hard Forbidden (All Sprints)

- Legal checker, OCR, AI checker, Rule Engine
- FAR/OSR/setback pass-fail
- K.1 generator, auto boundary detection
- Draggable workspace, full autosave engine
- Large file mode engine
- Save/load breaking migration
- Export rewrite
- Calculating from layer names

## Policy

- One sprint = one problem
- PASS (py_compile + smoke + full) before commit
- PASS before starting next sprint
- Update status docs after every sprint
