# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-21 — BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite — PASS (branch: main)

**What changed:** Forked proto's entire view/navigation control system into `lite/ui-lite.html` — adapted to lite's `V={k,ox,oy,rot}` single-canvas transform model (not proto's CSS-transform). Added: spacebar-hold pan + middle-mouse-button pan work in ANY mode including while a draw tool is selected (the headline bug); sticky H pan-tool (`state.panTool`); `setCursor()` helper (grab/grabbing/crosshair/default); smooth exponential wheel zoom (`exp(-deltaY*0.0015)`) clamped to `[ZMIN=0.02, ZMAX=40]` (anti-runaway); `zoomCenter(f)` (zoom about viewport center); `actualSize()` (reset to 1:1); keyboard shortcuts F/Ctrl+0 = fit, Ctrl+1 = actual size, Ctrl+=/Ctrl+- = zoom in/out; enriched canvas hint text. New Playwright regression guard `lite/tests/test_pan_controls.py` (13/13 checks GREEN, `BUG_20260521_LITE_PAN_OK`). ZERO edits to any file under `proto/`. `MEASURE_PARITY_OK` unchanged (ptToScreen/screenToPt/RS untouched).

**Why:** User directive via `/bma-bug-report`: "fork ระบบการควบคุมทั้งหมด มาจาก proto". Lite's view controls were impoverished: pan only worked in select/empty mode (any draw tool blocked mousedown early); no spacebar or middle-mouse pan at all; no zoom clamp (runaway to infinity/zero); no fit/actual-size keyboard shortcuts. These are table-stakes interactions for any CAD-like tool.

**Files touched:**
- `lite/ui-lite.html`: mousedown/mousemove/mouseup/wheel/keydown/keyup handlers + setTool + new zoomCenter/actualSize/setCursor helpers + hint text + state.panTool default (~39 insertions / 12 deletions)
- `lite/tests/test_pan_controls.py`: NEW Playwright regression guard (13 checks: midPan, spaceArmed, spacePanMidDraw, panToolOn/Drag/Off, selectPan, clampMax, clampMin, wheelZoomIn, actualSize, fit, ctrlZoomIn)
- `docs/status/PHASE_INDEX.md`: bug filed at top of Active queue then marked done

**Tests:**
```
py -3 -m py_compile lite/server_lite.py lite/tests/test_pan_controls.py lite/tests/test_menu_clickable.py  → PYCOMPILE_OK
lite/tests/test_pan_controls.py  → BUG_20260521_LITE_PAN_OK GREEN (13/13)
lite/tests/test_menu_clickable.py  → BUG_20260521_LITE_MENU_CLIP_OK GREEN (no regression)
lite/tests/test_measure_parity.py  → MEASURE_PARITY_OK GREEN (ptToScreen/screenToPt/RS untouched)
proto E2E: NOT run — zero edits to any file under proto/; lite tree isolated, no proto regression risk.
```

**Phase 1 scope check:**
- ✅ polyAreaM2 / polyMetrics / polySelfIntersects unchanged (lite vendors them in measure-engine.js — untouched)
- ✅ pdfToC / cToPdf / RS / scale math unchanged (lite ptToScreen/screenToPt/RS untouched)
- ✅ proto/server.py core endpoints unchanged (no proto edits at all)
- ✅ .bmaplan schema additive only (not touched)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Rotation parity intentionally omitted: lite uses a single global V.rot while proto persists per-page server-side rotation into the saved file — porting that is a deeper save-format/server change, out of view-control scope.
- Middle-button autoscroll suppression relies on preventDefault in mousedown; verified fine on canvas in headless — note for manual cross-browser check.

---

## 2026-05-21 — BUG-20260521-lite-menu-clip — lite top-bar dropdowns unclickable — PASS (branch: main)

**What changed:** One-line CSS fix in `lite/ui-lite.html` `#topbar` rule (L22-24): `overflow:hidden` → `overflow:visible` + added `position:relative;z-index:60`. Via `/bma-bug-report` (intake → file → scope `/bma-ui-menu` → fix → test → ship).

**Bug / root cause:** User reported "top เมนู lite กดไม่ทำงาน". Diagnosed live with Playwright: all 4 dropdowns (File/Measure/Page/Annotate) had every item correctly wired (no missing handler, no JS error). Real cause was pure CSS — `#topbar` is a fixed 42px-high flex bar with `overflow:hidden`; the `.dd` dropdown is `position:absolute; top:32px` so it hangs **below** the bar into `#stage` and was clipped away. Compounded by `#topbar` establishing no stacking context, so dropdowns sat under `#stage` content. `elementFromPoint` at a dropdown item returned `.empty`/canvas, not the item → opens but invisible & unclickable.

**Why this fix:** `overflow:visible` lets the dropdown escape the bar; `position:relative;z-index:60` makes `#topbar` a stacking context above `#stage` (canvas/`.empty` z-5) but still below the full-screen overlays (palette/overview/summary z-80, modal z-90, loading z-95) so a stray open dropdown can't cover those. Menu-bar scope only; **no forbidden surface, zero `proto/` edits, vendored `measure-engine.js` untouched.**

**Files touched:** `lite/ui-lite.html` (1 CSS line); NEW `lite/tests/test_menu_clickable.py` (Playwright regression guard); `docs/status/PHASE_INDEX.md` (bug filed + done). **Tests:** `lite/tests/test_menu_clickable.py` → `BUG_20260521_LITE_MENU_CLIP_OK` (4/4 menus' first item is topmost element); `lite/tests/test_measure_parity.py` → `MEASURE_PARITY_OK` (16 fns + 2 consts byte-identical, area math unaffected). Proto E2E n/a — lite tree is isolated, no proto files changed. **Known gap:** Esc-to-close menus still not bound (minor, separate item).

---

## 2026-05-21 — LITE-5 — /lite/ .bmaplan cross-opens with proto — 10/10 scope groups — PASS (branch: main)

**What changed:** Switched `/lite/` save/load to proto's exact `.bmaplan` schema (96f61b8). Lite now writes the 13 top-level keys + `pageStore[n].{lines,polys,openings,refs,parking,counts,calibScale,annotations}` with proto-shaped objects (poly: id/pts/closed/areaType/semanticTag/color/opacity; line: x0/y0/x1/y1/kind; ref: refType; opening for `ded`). Annotation `type` is mapped both ways (ann_arrow↔arrow, ann_rect↔rect_frame, …). Count objects go in an additive `pageStore[n].counts[]` array that proto ignores. Lite's loader reads proto `pageStore` (and falls back to legacy lite `pages{}`), reverse-mapping semanticTag→category and flattening any `geometryType:'path'` polys via the vendored `flattenPathToPoints`.

**Why:** LITE-5 of the standalone-lite epic — the differentiator of Approach A (vendored math + shared file format). **Verified BOTH directions with Playwright (lite on 8123, proto on 8124, same test_plan_A1.pdf):** (1) lite draws a 66.6667 m² polygon + a count + an arrow annotation → saves → proto's `applyLoadedProject` loads it → proto's own `polyAreaM2` returns 66.6667 (identical), count kept in additive array, annotation present, 0 proto errors. (2) the proto-schema file re-opens in lite with identical area + annotation round-trip. This closes group 6 → all 10 locked scope groups done. Only LITE-7 (PyInstaller `.exe`) remains, deferred by the user.

**Files touched:** `lite/ui-lite.html` (save/load rewrite). Tests: Playwright cross-open both directions (areas identical, 0 errors); `MEASURE_PARITY_OK` unchanged.

---

## 2026-05-21 — LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP — /lite/ to 9/10 scope groups — PASS (branch: main)

**What changed:** Five dev-loop iterations on the standalone `/lite/` tree (each its own commit, all zero proto edits): **LITE-SNAP** (21a8a8e) lite-native snap — endpoint/intersection/nearest, 11px, yellow indicator, G toggle; intersections via the vendored `segIntersect`. **LITE-REVIEW** (f61f7b5) Σ Summary overlay — area totals by category (current page + all pages, per-page scale via vendored `polyMetrics`), net building area (GFA−deduction), open-space ratio. **LITE-ANNOT** (bdc9ef0) 7 annotation tools (text/comment/arrow/highlight/rect/circle/cloud), per-page `annotations[]`, right-click delete, save/load. **LITE-6 EXPORT** (b309813) `/export-xlsx` (openpyxl, Measurements+Summary) + `/export-pdf-overlay` (PyMuPDF draw on a PDF copy); run.bat now installs openpyxl. **LITE-PAGESETUP** (d3644cc) Page Setup dialog (Ctrl+,) — project name + per-page tag + manual scale; tags in F12 overview; projectInfo+pageTags in save/load. Each verified end-to-end with Playwright on test_plan_A1.pdf, 0 console errors; `MEASURE_PARITY_OK` unchanged throughout.

**Why:** User directed `/loop /bma-dev-loop` to take `/lite/` from runnable foundation to full locked scope (10 groups). After these 5 iterations: 9/10 groups complete (tools, snap, layer+semantic, pages incl. setup, export, annotation, review, chrome, dimension). Remaining: group 6's cross-open byte-parity with proto's exact `.bmaplan` schema (LITE-5 — needs a design decision: adopt proto's pageStore schema in lite's save format) and packaging to a standalone `.exe` (LITE-7 — heavy PyInstaller build). Halted at this checkpoint for those two, per dev-loop design-ambiguity stop.

**Files touched:** `lite/ui-lite.html` (snap/review/annot/export-UI/pagesetup), `lite/server_lite.py` (export endpoints), `lite/run.bat` (openpyxl), `docs/status/PHASE_INDEX.md`. Tests: per-sprint Playwright journeys (snap exact-vertex, review net 55.56, annot 6-types+delete+persist, export XLSX 66.667 + overlay PDF, pagesetup project/tag/scale) — all 0 errors; `MEASURE_PARITY_OK`.

---

## 2026-05-21 — LITE-1+2+3+4 — make /lite/ runnable (per /goal "ทำให้ครบถ้วน จน run ได้") — PASS (branch: main)

**What changed:** Extended the LITE-0 scaffold into a runnable lite app. (1) LITE-1 backend: `server_lite.py` now has real `/upload` (per-case PyMuPDF open, case_id isolation), `/page/{n}` (JPEG render at RS=1.5, prerotate, image cache), `/pageinfo/{n}` (PDF-point page size), `/thumb/{n}`. (2) LITE-2 chrome: `ui-lite.html` rebuilt as the full single-row top bar (File/Measure/Page + ⌘K/Overview/Focus), floating "กำลังวัดอะไร" category picker, 4 corner HUDs, ⌘K page search, F12 overview with real thumbnails. (3) LITE-3 tools: scale-calibration modal + polygon/distance/path/reference/count, all areas via the vendored `polyAreaM2`; geometry stored in PDF points, canvas view handles rotate/zoom/pan. (4) LITE-4 dimension labels render at constant screen size with declutter + right-click per-object show/hide. Save/load `.bmaplan` (lite-native, version 1) round-trips. **Verified end-to-end with Playwright on `proto/test_plan_A1.pdf`:** PDF rendered (3576×2526), scale set (79.27 pt/m), polygon area = **66.67 m² (exact)**, distance + count drawn, save round-trip OK, **0 console errors**. Fixed a dblclick stray-point bug (the double-click's two mousedowns were adding duplicate polygon vertices → wrong area). Still zero edits under `proto/`; `MEASURE_PARITY_OK` still green.

**Why:** User set `/goal "ทำให้ครบถ้วน จน run ได้"` — push the lite tree from scaffold to a genuinely runnable measurement app. Core workflow (open PDF → set scale → measure → save) now works. Remaining: LITE-5 cross-open byte-parity + count additive, LITE-6 export (needs openpyxl), LITE-7 PyInstaller packaging.

**Files touched:** `lite/server_lite.py` (real endpoints), `lite/ui-lite.html` (full UI), `lite/static/js/measure-engine.js` (unchanged — vendored), `docs/status/PHASE_INDEX.md` (LITE-1..4 done). Tests: `python lite/tests/test_measure_parity.py` → MEASURE_PARITY_OK; py_compile OK; Playwright journey 0 errors.

---

## 2026-05-21 — LITE-0 — scaffold standalone /lite/ tree — PASS (branch: main)

**What changed:** Scaffolded a new `/lite/` sibling directory tree — a standalone build of BMA-Plan Lite (epic INV-2026-05-21-001, Approach A: vendored-copy + contract-test). The measurement engine (`RS`, `pdfToC`, `cToPdf`, `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pathAreaM2`, and 6 path helpers) was vendored byte-identical from `proto/ui.html` into `lite/static/js/measure-engine.js`, with a new lite-only wrapper `objectAreaM2Lite` (polygon+path only). An anti-drift parity gate (`lite/tests/test_measure_parity.py`) verifies both source byte-identity (10 fns + 2 consts) and numeric parity via Node.js on 5 polys, 2 paths, and 4 coordinate pairs. A skeleton FastAPI app (`lite/server_lite.py`), free-port launcher (`lite/launch_lite.py`), and minimal UI shell (`lite/ui-lite.html`) complete the scaffold. The shell runs a self-test on load (unit square = 25.00 m2) with 0 console errors. Zero edits to any file under `proto/`.

**Why:** The invent pipeline (`/bma-invent` GO on idea INV-2026-05-21-001 "BMA-Plan Lite standalone build") concluded Approach A (vendored copy + parity gate) is the lowest-risk path for a distributable lite variant — the contract test enforces byte-identity so any upstream change to the engine immediately breaks the gate, preventing silent drift. LITE-0 is the foundation sprint; LITE-1..7 will add backend render endpoints, UI chrome, tools, export, and packaging without any proto/ coupling.

**Files touched:**
- `lite/static/js/measure-engine.js` (NEW): vendored verbatim from `proto/ui.html` — `RS`, `_PATH_FLATTEN_TOL`, `segIntersect`, `_flattenCubicSeg`, `flattenPathToPoints`, `polySelfIntersects`, `origSize`, `pdfToC`, `cToPdf`, `polyAreaM2`, `polyMetrics`, `pathAreaM2`; plus lite-only `objectAreaM2Lite`
- `lite/tests/test_measure_parity.py` (NEW): anti-drift gate — source byte-identity + numeric parity via Node
- `lite/tests/fixtures/measure_parity_v1.json` (NEW): 5 polys / 2 paths / 4 coords test vectors
- `lite/server_lite.py` (NEW): skeleton FastAPI (static mount + /health + /); endpoints deferred to LITE-1
- `lite/launch_lite.py` (NEW): free-port (8100+) launcher
- `lite/ui-lite.html` (NEW): LITE-0 shell — host globals + engine load + self-test (unit square = 25.00 m2)
- `lite/README.md` (NEW): vendoring contract + version-sync policy
- `docs/invent/bma-plan-lite-standalone.md` (NEW): invent research + approach decision record
- `proto/sandbox/invent-bma-plan-lite-standalone.html` (NEW): invention spike
- `docs/status/PHASE_INDEX.md` (MODIFIED): sprint card LITE-0 added + status flipped to done

**Tests:**
```
python lite/tests/test_measure_parity.py
  -> MEASURE_PARITY_OK (10 fns + 2 consts byte-identical; 5 polys/2 paths/4 coords numeric parity; unit square = 25.00 m2 verified)
python3.11 -m py_compile lite/server_lite.py lite/launch_lite.py  -> PASS
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py     -> PASS (proto regression guard)
Playwright render lite/ui-lite.html -> self-test "engine wired", 0 console errors

No-test rationale for proto full E2E + human-journey: LITE-0 is purely additive in the new /lite/ tree.
ZERO changes to proto/ — proto runtime unchanged, no regression risk. Proto py_compile is the guard.
Reference baseline: proto full E2E = 21 markers / 102 _OK as of HT-ACC 2026-05-20.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (vendored copy byte-identical, enforced by parity gate)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (count objects deferred to LITE-5 as additive `store.counts`; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `/bma-check-forbidden` = OK (read-only vendoring; hard constraint = byte-identical enforced by parity gate)

**Known gaps / follow-ups:**
- LITE-1: backend endpoints (`/upload`, `/page/{n}`, `/thumb`) reusing PyMuPDF for the raster render path.
- Epic LITE-1..7 remains (chrome, tools, dimension rendering, save/load+count, export, packaging).
- `lite/` tree is gitignored-candidate until LITE-3 chrome lands; confirm with user before first commit of `lite/`.

---

## 2026-05-20 — HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — PASS (branch: main)

**What changed:** Fixed the calibration UX gap that caused the user to measure title-deed land (โฉนด 2 ไร่ 2 งาน = 4,000 m²) ~1% smaller than the deeded area. The investigation confirmed the area math is exact (shoelace with precise pts_per_m float, 0.08% error on reference geometry); the loss came from snap silently capturing a different — longer — reference line than the one the user intended to click. Four coordinated changes: (1) HT-ACC-1: `calibRaw[]` captures the raw pre-snap click points alongside `calibPts`; after the 2nd click, if snap moved the captured line >5% from the user's click the calib panel shows an orange warning with raw→snapped coordinates and a reminder to zoom in before re-clicking — this was the root cause of the systematic measurement loss. (2) HT-ACC-2: Verify Scale promoted to a ribbon button beside Set Scale; longest-baseline tip added to calib panel; `finishCalib` status nudges to Verify; `activateAreaTool('land')` hints to use arc edges on curved boundaries. (3) HT-ACC-3: `status-bar.js` `updateAnalyseUI` sets a tooltip on `#lbl-scale` and `#scale-badge` showing exact `pts_per_m` and precise `1:N.x` — the visible label stays rounded, area computation uses the full float, so there is no measurement change. (4) HT-NAV-1: navigation root-cause investigation concluded — no code fix required; `getNextPage`/`loadPage` logic is sound; exception observed by journey-tester was a Playwright timing artifact. New E2E marker `HT_ACC_OK` (5 sub-checks). Total full E2E: EXIT 0, 102 _OK markers.

**Why:** `/bma-human-test` 2026-05-20 on real Downloads PDFs (SCR_Permit_Layout, raster ข.4) returned JOURNEY_OK with no CRASH/BROKEN. However, the user subsequently reported measuring title-deed land at ~1% less than the deeded 4,000 m². Journey-tester analysis isolated the discrepancy: area math is EXACT (verified analytically); the only plausible source is the calibration step itself — snap grabbing a longer nearby vector line drives pts_per_m too high, making all derived areas proportionally smaller. The orange snap-deviation warning (HT-ACC-1) directly surfaces this failure mode to the user at the moment of calibration.

**Files touched:**
- `proto/ui.html`: `calibRaw[]` state + snap-deviation warning in calib panel; Verify ribbon button (`#btn-scale-verify`); longest-baseline tip; `finishCalib` Verify nudge; `activateAreaTool('land')` arc hint
- `proto/static/js/status-bar.js`: `updateAnalyseUI` adds tooltip to `#lbl-scale` and `#scale-badge` (pts_per_m + precise 1:N.x)
- `proto/e2e_ui_test.py`: `_test_ht_acc_calibration` (5 sub-checks) + `HT_ACC_OK` marker

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py                   → PASS
proto/e2e_ui_test.py full                                          → EXIT 0 (102 _OK markers, 0 E2E_FAIL)
  NEW: HT_ACC_OK GREEN (5 sub-checks:
       verifyBtnExists, verifyBtnWired, longestTip,
       calibRawExists, devWarnsWrongLine, devQuietWhenClose)
  Static-asset safety: NO_BOM on app.css + status-bar.js
  CACHE_OK + MAIN_UI_OK (cssLinkPresent/statusBarJsLoaded true) — assets serve
  All prior 101 markers retained. Zero regression.
UI_REGRESSION_PASS. Forbidden-surface diff scan CLEAN.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (area math proven exact; this series fixes calibration UX, not the formula)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED (calibRaw captures pre-snap raw clicks; snap logic itself not modified)
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibRaw` is in-memory only, not persisted; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Static JS touched (`status-bar.js`) → `UI_MANUAL_TEST.md` updated with 6-check HT-ACC calibration accuracy manual checklist.
- `calibRaw` reset is confirmed in `cancelCalib` / `finishCalib` / `loadPage` — no stale state across pages.
- HT-NAV-1 closed as no-fix: `getNextPage`/`loadPage` nav logic is sound; `REAL_OK` already exercises real multi-page navigation.
- Next: `/bma-sandbox-test` on large Downloads PDFs (589 MB BKM, 59 MB RM1) for pre-release stress, or Discovered backlog items.
- Commit: `c0834f0` on main.

---

<!-- LITE-0 (2026-05-21) and HT-ACC series (2026-05-20) are the 2 sessions kept in this file -->
<!-- BUG-20260520-zen-exit-rp-restore archived to docs/archive/log-2026-05-20.md (already present) -->
<!-- INV-2026-05-20-002/003/004 Layer L1+L2+L3 and earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
