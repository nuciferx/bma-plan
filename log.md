# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-22 — LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite — PASS (branch: main)

**What changed:** Added a standalone editable web-report page (`lite/lite-report.html`) to the lite tree. The report opens in a new window via a File-menu item "ส่งออกรายงาน (แก้ไขได้)…" in `lite/ui-lite.html`. Payload (geometry metadata + page info, not images) is handed off through `sessionStorage["bmaReportPayload"]`; plan images reference `/page/{n}` URLs directly so sessionStorage stays under 5 MB. The page renders one A4-landscape sheet per measured page: left half = plan image + SVG polygon overlay + numbered badges; right half = area table grouped by semanticTag category with per-group subtotals + page net (deductions sign −1) + header (project/page#/tag/scale-state/date). Header fields, row labels, and a per-row note column are `contenteditable`; area number cells are read-only gray (raw-geometry contract preserved). `@page` CSS + `@media print page-break-after:always` per sheet → WYSIWYG browser-print-to-PDF. A sample standalone fallback renders when opened with no payload. `lite/server_lite.py` gained a `GET /report` route (+9 lines, additive). New Playwright test `lite/tests/test_report.py` validates the full flow (LITE_REPORT_OK, 17/17). A `realflow_check.py` real-PDF acceptance test verified: real permit upload → openReport → popup caught → plan image naturalWidth 3576, viewBox "0 0 3576 2526" → overlay polygon → net 222.22.

**Why:** INV-2026-05-21-002 invention verdict: PRIOR_ART_PARTIAL → Approach A (sessionStorage + new-window contenteditable) chosen over Approach B (postMessage+Blob). This delivers the "editable report" user story — the user can annotate measurement results in a Word-like web page and print to PDF — without touching the measurement engine, save format, or proto runtime. The sprint closes the last user-facing output gap in the lite epic (the only missing output was a human-readable, printable, editable document).

**Files touched:**
- `lite/lite-report.html`: NEW — standalone editable report page (A4 landscape, plan+SVG overlay, area table, contenteditable, @page print CSS, sample fallback)
- `lite/server_lite.py`: +9 lines — `_REPORT_FILE` const + `GET /report` FileResponse route (additive)
- `lite/ui-lite.html`: +52 lines — File-menu item #mi-report + `reportPageTitle()` / `buildReportPayload()` / `openReport()` functions (reads polyMetrics/PS/catOf READ-ONLY; hands off via sessionStorage + window.open)
- `lite/tests/test_report.py`: NEW — LITE_REPORT_OK Playwright guard (17 checks)
- `docs/status/PHASE_INDEX.md`: LITE-REPORT marked done

**Tests:**
```
py_compile lite/server_lite.py lite/launch_lite.py  → PY_COMPILE_OK
lite/tests/test_report.py  → LITE_REPORT_OK GREEN (17/17)
lite/tests/test_measure_parity.py  → MEASURE_PARITY_OK GREEN (16 fns + 2 consts unchanged)
lite/tests/test_menu_clickable.py  → BUG_20260521_LITE_MENU_CLIP_OK GREEN
lite/tests/test_pan_controls.py  → BUG_20260521_LITE_PAN_OK GREEN
artifacts/realflow_check.py  → REALFLOW_OK (real PDF → openReport → popup → naturalWidth 3576 → polygon overlay → net 222.22)
Proto E2E: n/a — lite-only tree; zero proto/ edits.
```
New E2E marker: LITE_REPORT_OK

**Phase 1 scope check:**
- ✅ polyAreaM2 / polyMetrics / polySelfIntersects unchanged (read-only consumer)
- ✅ pdfToC / cToPdf / RS / scale math unchanged (measure-engine.js untouched; MEASURE_PARITY_OK)
- ✅ proto/server.py core endpoints unchanged (zero proto edits)
- ✅ .bmaplan schema additive only (no schema touch — report reads in-memory PS, ephemeral edits)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (area facts only)

**Known gaps / follow-ups:**
- sessionStorage 5 MB quota: images pass as /page URLs so only geometry+metadata are serialised — not hit in practice, but documented in code.
- Fallback B (postMessage+Blob) documented in code comments if the quota is ever hit.
- LITE-REPORT v2 ideas (custom branding, cross-page roll-up summary, persist edits to .bmaplan) are out of scope for this sprint.
- LITE-7 PyInstaller .exe still deferred.

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

<!-- LITE-REPORT (2026-05-22) and BUG-20260521-lite-pan-controls (2026-05-21) are the 2 sessions kept in this file -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
