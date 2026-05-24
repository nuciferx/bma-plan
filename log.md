# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-24 — LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop) — PASS (branch: main)

**What changed:** Fixed two `lite/ui-lite.html` bugs surfaced by the Opus-4.7-self-drive multi-model simulator on 2026-05-24. LITE-BUG-MODAL-NEST (BROKEN): `<div id="modal">` at line 191 was missing its closing `</div>`, causing `#setupModal` (line 195) to be nested inside `#modal` (calibration modal). Because `#modal` defaults to `display:none`, `#setupModal` was invisible regardless of `openSetup()` setting `style.display='flex'` — `getBoundingClientRect()=0×0`, `offsetParent=null`. Fix: added the missing `</div>` at end of line 194 to properly close `#modal` before `#setupModal`. LITE-BUG-DBLCLICK-OVER-POP (FRICTION): `cv.addEventListener("dblclick", ...)` had an unbounded `while` loop popping trailing pts within 6 screen-px of the dblclick spot. Intended to remove 2 stray points from dblclick's two mousedowns, but without an upper bound it also ate any intentional vertex placed within 6 px, causing saved polygons to be triangles (confirmed: 4 pts → 3 pts, area 713 m² → 356 m²). Fix: replaced with bounded `for(_np<2)`. Zero net lines across both patches. `lite/ui-lite.html` stays at 1197 lines (cap 1200).

**Why:** The Opus-4.7 multi-model simulator (Pack J, `/bma-simulate`) ran a full lite workflow on `lite/test.pdf` and identified both regressions as BROKEN/FRICTION severity. LITE-BUG-MODAL-NEST blocked the Page Setup flow entirely — users clicking Page → Page Setup saw nothing. LITE-BUG-DBLCLICK-OVER-POP silently corrupted polygon vertex counts, causing wrong areas in saved projects. Both were silent bugs (no console error) that standard py_compile/smoke did not surface — proving the value of the multi-model simulator as a finding mechanism.

**Files touched:**
- `lite/ui-lite.html`: Added missing `</div>` at line 194 end (closes `#modal`); replaced unbounded `while` with bounded `for(_np<2)` at lines 502-503 (0 net lines)
- `sprints/completed/2026-05-24-lite-bug-2-opus47-findings/LITE-BUG-2-OPUS47-FINDINGS-2026-05-24.md`: NEW sprint card (moved from active/)

**Tests:**
```
python -c "open('lite/ui-lite.html', encoding='utf-8').read()"  → parseable PASS
wc -l lite/ui-lite.html                                          → 1197 (≤1200 cap) PASS
<div> vs </div> regex balance: opens=92 closes=92 delta=0        PASS (was delta=1)
cd lite && python -m py_compile server_lite.py                   → PASS
cd lite && python tests/test_pan_controls.py                     → BUG_20260521_LITE_PAN_OK PASS

Live Playwright verify (artifacts/sim/lite/test-pdf-opus47-direct-20260524T194000/verify_bug_fixes.py):
  BUG_A_modal_rect_nonzero:     PASS — #setupModal now renders 1600×958, parent=#stage
  BUG_A_calib_modal_still_works: PASS — no regression, 1600×958
  BUG_B_dblclick_preserves_vertex: PASS — 4 pts saved, area=714.07 m² (drift 0.13% from screen-to-pt rounding — acceptable)

No proto/ E2E run (lite-only sprint, zero proto/ edits).
```

**Phase 1 scope check:**
- ✅ polyAreaM2 / polyMetrics / polySelfIntersects unchanged
- ✅ pdfToC / cToPdf / RS / scale math unchanged
- ✅ proto/server.py core endpoints unchanged (zero proto edits — lite-only sprint)
- ✅ .bmaplan schema additive only (untouched)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ lite/static/js/measure-engine.js (drift-locked vendored copy) unchanged
- ✅ Size cap honored — lite/ui-lite.html still 1197 ≤ 1200

**Known gaps / follow-ups:**
- Simulator reflection-loop hardening: read last 1-3 history.jsonl entries in Phase A and add closed bugs as regression checks so they are not re-found.
- Snap-to-walls polygon strategy: replace synthetic 80%-quad placeholder with real measurement (read PDF vector edges, snap to walls).
- Lite PDF page classifier: auto-tag floor/site/cover from title block OCR or layout hints, eliminating the manual tagging step.

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

<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) and LITE-REPORT (2026-05-22) are the 2 sessions kept in this file -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
