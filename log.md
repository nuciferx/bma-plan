# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-06-05 — SLICE report-edit-1 — Editable lite report — PASS (branch: main)

**What changed:** Shipped the editable lite report feature — the BUILD of invent Approach D3 from `docs/invent/lite-editable-report.md`. A new module `lite/static/js/report-edit.js` (404 LOC) wraps jspreadsheet-ce community edition with three sub-systems: (a) a custom Excel-style cell-click formula picker (~70 LOC) that hooks `oneditionstart`+`oncreateeditor`, activates picker mode on a leading "=", and injects `B<n>` refs via capture-phase mousedown; (b) a stable-row-id subtotal mapper (~60 LOC) — `rowIds[]` parallel array + `subMeta` semantic capture + `rebuildSubtotals()` re-projects formulas after structural mutations so deleting a row drops the term and raises a red flag rather than silently shifting references; (c) render/persist/provenance helpers (~160 LOC) — `baseline[]` for computed-vs-override stale detection (orange warning), NaN-guard that rejects non-numeric input and reverts to the previous value, and localStorage v1 persistence keyed by payload hash. `lite/lite-report.html` gained 46 lines of override-overlay toggle markup, grid mount, and four vendor `<script>`/`<link>` tags. jspreadsheet-ce + jsuites vendored offline (~440 KB minified, MIT) into `lite/static/js/vendor/` — CDN use forbidden after the pdfjs-cdn bug. A new skill `.claude/skills/lite-spike-iterate/SKILL.md` codifies the SPIKE→EVAL→fix loop after the sprint hit the 3rd-RESHAPE memory-escalation trigger. All prior tests GREEN; zero proto/ edits.

**Why:** The existing `lite/lite-report.html` report shipped read-only area cells (raw-geometry contract). Users need to add custom subtotals and override values for plan-submission documents. The /lite-invent pipeline went through 3 RESHAPE rounds (B raw contenteditable → D jspreadsheet CE → D2 custom cell-click picker → D3 stable-row-id mapper) before arriving at an approach that satisfied both the live-cell-click UX requirement (PRO-only in jss-CE → solved with custom picker) and the structural-mutation correctness requirement (positional B-refs → solved with rowIds[]).

**Files touched:**
- `lite/static/js/report-edit.js`: NEW 404 LOC — formula picker + stable-row-id mapper + render/persist/provenance + NaN-guard
- `lite/lite-report.html`: +46 lines — override-overlay toggle, grid mount, 4 vendor tags
- `lite/static/js/vendor/jspreadsheet.min.js`: NEW vendored MIT (jspreadsheet-ce)
- `lite/static/js/vendor/jspreadsheet.min.css`: NEW vendored MIT
- `lite/static/js/vendor/jsuites.min.js`: NEW vendored MIT (jsuites peer dep)
- `lite/static/js/vendor/jsuites.min.css`: NEW vendored MIT
- `lite/tests/test_report_edit.py`: NEW 245 LOC — 7-case Playwright marker LITE_REPORT_EDIT_OK
- `docs/invent/lite-editable-report.md`: NEW — full invent record (PICK/RESEARCH/FRAME/DIVERGE/SCORE/SPIKE + 3 RESHAPE sections)
- `.claude/skills/lite-spike-iterate/SKILL.md`: NEW — SPIKE→EVAL→fix iteration loop skill
- `docs/status/PHASE_INDEX.md`: +11 lines — 2 idea entries under ### ideas 2026-06-04
- `lite/sandbox/invent-lite-editable-report*.{html,py}`: NEW spike artifacts (5 HTML + 5 eval scripts)
- `lite/sandbox/vendor/*`: NEW vendor copies for sandbox reproducibility

**Tests:**
```
python lite/tests/test_report_edit.py  →  LITE_REPORT_EDIT_OK 7/7  PASS
```
Cases: PICKER regression =B1+B2→86.93 DOM-driven / STABLE delete-unreferenced re-projects =B1+B3→=B1+B2 value 76.61 / STABLE delete-referenced term dropped 50.45 red flag / STABLE multi-op =B1+B2+B3-B4 delete-ref re-project 66.61 / GUARD label-col click no A2 injection / PERSIST semantic subMeta survives save-reopen / NaN-GUARD "abc" reverts to 50.45. Zero page errors.
Proto py_compile + smoke + full NOT re-run: lite-only sprint, zero proto/ edits, no forbidden-trigger surface touched.

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto untouched entirely)
- ✅ `lite/static/js/measure-engine.js` (drift-locked vendored copy) unchanged
- ✅ `.bmaplan` schema — no change at all; persistence = localStorage v1 only
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR
- ✅ `lite/ui-lite.html` untouched (stays at cap)
- ✅ Size caps: report-edit.js 404/1000 ✅

**Known gaps / follow-ups:**
- Print-to-PDF CSS needs re-validation: grid replaces the contenteditable report wholesale so `@page` CSS for the jss grid renderer needs a dedicated print sprint
- ~440 KB vendored payload doubles lite static size (accepted cost per invent doc, but should be noted for future LITE-7 PyInstaller build)
- jss-CE positional NaN-eval is guarded at the input layer only, not at the library layer — if jss internally coerces a formula to NaN, the guard may not catch it
- Grid is currently behind the `#re-toggle` dev gate; needs a production wire-up sprint before shipping to users

---

## 2026-05-28 (continued) — invent `lite-pdf-render-quality` — RESUMED + COMPLETED — 4 commits shipped — [decision + code]

**What changed:** Resumed from the pause checkpoint and shipped the full invent → 2 sprints in one session. 4 commits land on `main`:

1. **`b9cda6c` — invent docs + spike v1/v2/v3 artifacts**. Committed previously-uncommitted `docs/invent/lite-pdf-render-quality.md` (frame + 5-step Decision resume plan) + 3 spike HTML files + 4 Python scripts + results JSON. Skipped 9 MB of reproducible raster cache + screenshots (`v3-results/`, `phang_p01_*.{jpg,png}`).
2. **`f53d239` — Sprint #1 PDFJS-PREP-EXTRACT-RENDERER**. Pure refactor — function bodies byte-identical to pre-Sprint state. `lite/ui-lite.html` 1195 → 1100, `lite/static/js/page-renderer.js` NEW 98 LOC, `lite/static/js/export-annotate.js` NEW 87 LOC. ui-lite.html headroom restored before Sprint #2's ~200-LOC growth in page-renderer.js.
3. **`8fca51a` — spike v4 (PDF.js ↔ lite's ptToScreen contract)**. New de-risk spike NOT in the original pause plan but required after reviewing v3 — v3 used its own coord convention (panX/panY/curZoom/curRot), not lite's V.ox/V.oy/V.k/V.rot. v4 vendors `ptToScreen` byte-identical from `ui-lite.html:258` (CW rotation matrix `rx=ix*c-iy*s`), derives transform `T = [cR*dpr, sR*dpr, sR*dpr, -cR*dpr, (V.ox - pageH*s*sR)*dpr, (V.oy + pageH*s*cR)*dpr]` analytically, and proves 24/24 contract PASS (C1Δ = 0.000000) via Playwright sweep `drive_v4.py` across 6 zooms × 4 rotations. First iteration of v4 used the WRONG (CCW) formula and passed only because self-consistent; caught via grep on real `ptToScreen` and corrected — reviewer trust-but-verify ⇒ caught.
4. **`382b30a` — Sprint #2 PDFJS-VIEWPORT-CLIPPED-INTEGRATION**. `/bma-lite-dev` orchestration → `lite-builder` (sonnet) wrote diff, Opus reviewed line-by-line. NEW `@app.get("/raw")` in `server_lite.py` (case-id-validated, no path traversal). `page-renderer.js` 98 → 305 LOC — lazy-imports PDF.js 4.0.379 from jsDelivr, replaces JPEG-raster path with `getViewport({scale:RS*V.k, rotation:0}) + render({transform:T})` using spike v4's formula. pageRot folded into `θ_total = pgRot + V.rot` (option B); `pageH_tx` swaps to PDF native width when pgRot is 90/270 to mirror old prerotated-raster coord origin. `drawImage()` keeps sync signature — schedules async render via microtask, cancels in-flight, monotonic `_renderToken` prevents infinite-loop. `ui-lite.html` 12 × `curImg` → `PageRenderer.ready()` (lines 272, 396, 463, 483, 489, 593, 639, 776, 800-801, 1080-1081); ptToScreen / screenToPt at 257-260 byte-identical UNCHANGED. ui-lite.html stays 1100/1200.

**Verification (Opus, not delegated):**
- All 6 named tests PASS — re-ran each: MEASURE_PARITY_OK / LITE_PF_KIND_OK 11/11 / LITE_LAYER_DND_OK / LITE_EXPORT_SUBMENU_OK / LITE_OVERVIEW_SETUP_OK / + bonus BUG_20260521_LITE_PAN_OK / LITE_ANNOT_LABEL_OK
- NEW `lite/sandbox/invent-lite-pdf-render-quality/smoke_pdfjs_live.py` boots real `server_lite.py`, uploads RAMA4 PDF in headless Chromium, exercises real PDF.js path (no `curImg` shim): SMOKE_PDFJS_LIVE_OK 8/8 — PDF.js loads, PageRenderer.ready() true, canvas has rendered content (9/9 non-bg pixels), V.rot=90 works, pageRot=90 works, pageRot=270 works, V.k=5 zoom works, 0 console errors
- Forbidden-surface grep on full diff: `ptToScreen` / `screenToPt` / `polyAreaM2` / `polyMetrics` / `RS` / `pdfToC` / `cToPdf` / `.bmaplan` schema — ALL untouched (comment lines reference them; function bodies unchanged)
- Size caps: ui-lite.html 1100/1200 ✓ page-renderer.js 305/1000 ✓ export-annotate.js 87/1000 ✓
- arcHUDText debt that the pause-state log predicted: **resolved pre-resume** — `draw-arc.js` is in the working tree (193 LOC), script tag at `ui-lite.html:221` still loads it. `test_pf_kind_folders` passed without intervention. Likely fixed by another session between the pause and this resume

**Files touched (committed):**
- `docs/invent/lite-pdf-render-quality.md` (frame doc, status section now historical)
- `lite/sandbox/invent-lite-pdf-render-quality.html` / `-pdfjs.html` / `-pdfjs-v3.html` / `-pdfjs-v4.html` (4 spike HTMLs)
- `lite/sandbox/invent-lite-pdf-render-quality/render_variants.py` / `drive_v3.py` / `drive_v3_all_pages.py` / `drive_v4.py` / `smoke_pdfjs_live.py` / `stats.json` / `v3-all-pages-results/results.json` / `v4_sweep_results.txt`
- `lite/server_lite.py` (+10 — `/raw` endpoint)
- `lite/static/js/page-renderer.js` (NEW 305 LOC — PDF.js renderer)
- `lite/static/js/export-annotate.js` (NEW 87 LOC — XLSX + PDF overlay + report)
- `lite/static/js/page-rotate.js` (+2/-1 — pageCache invalidation)
- `lite/static/js/empty-hub.js` (+1/-1 — PageRenderer.ready() guard)
- `lite/ui-lite.html` (-95 in Sprint #1, +0 net in Sprint #2, final 1100/1200)

**Files NOT touched (verified):**
- `proto/**` — Sprint touched only lite/
- `lite/static/js/measure-engine.js` — vendored math intact
- `.bmaplan` schema — additive-only check passes; no new fields added

**Tests run:**
```
python -m py_compile lite/server_lite.py                       → OK
python lite/tests/test_measure_parity.py                        → MEASURE_PARITY_OK
python lite/tests/test_pf_kind_folders.py                       → LITE_PF_KIND_OK 11/11
python lite/tests/test_layer_dnd.py                             → LITE_LAYER_DND_OK
python lite/tests/test_export_submenu.py                        → LITE_EXPORT_SUBMENU_OK
python lite/tests/test_overview_setup.py                        → LITE_OVERVIEW_SETUP_OK
python lite/tests/test_pan_controls.py                          → BUG_20260521_LITE_PAN_OK
python lite/tests/test_annot_label.py                           → LITE_ANNOT_LABEL_OK
python lite/sandbox/invent-lite-pdf-render-quality/drive_v4.py  → 24/24 PASS (spike contract)
python lite/sandbox/invent-lite-pdf-render-quality/smoke_pdfjs_live.py → SMOKE_PDFJS_LIVE_OK 8/8
```

**Tech debt filed for follow-up sprint (not blocking):**
1. **`curImg` compat shim** — `var curImg = null` retained in `page-renderer.js` so 6 test files (`test_pan_controls`, `test_live_overlay`, `test_hardening`, `test_annot_style`, `test_annot_label`, `test_layer_zorder_lock`) that set `window.curImg = dummy` continue passing without rewrites. Cleanup = migrate test mocks to `PageRenderer.ready()` stub.
2. **Placeholder rect** painted during first render is NOT rotation-aware (axis-aligned at V.ox/V.oy). Cosmetic — overwritten by PDF.js within ~50 ms.
3. **pageRot=90/270 spatial alignment** verified only by smoke probe content-presence, not pixel-perfect overlap. If a user reports misalignment on a rotated PDF, investigate `pageH_tx` swap in `_render()` first.
4. **PDF CropBox origin-shift** edge case — `page.view[0/1]` may be non-zero on PDFs with shifted CropBox; current code uses `view[2]-view[0]` and `view[3]-view[1]` for dims but assumes origin (0,0) in transform. Rare but possible bug.

**Lessons / decision-log entries:**
- **lite-builder shortcut caught**: builder kept `curImg` as global despite spec saying "REMOVED". Reviewer accepted as interim (test cost vs benefit) but flagged tech debt. Pattern continues from 2026-05-22 log — workers favor low-effort test paths; Opus must read diff carefully.
- **spike v4 first-pass error caught**: initial v4 vendored ptToScreen with CCW rotation matrix (`u=ix*c+iy*s`) — internally consistent but WRONG relative to ui-lite.html:258 CW formula (`rx=ix*c-iy*s`). 24/24 PASS hid the bug. Caught by grep'ing the real source. Lesson: when vendoring math, paste the exact formula and verify byte-by-byte against the source line, don't transcribe by hand.
- **smoke probe pattern**: when unit tests use mocks (`curImg=dummy`), integration probes that drive the real server + real PDF + real PDF.js are required to verify the actual path. `smoke_pdfjs_live.py` is now the template for future render-path sprints.

**Resume:** invent CLOSED. Status `invent-paused` → `done` in PHASE_INDEX. No follow-up sprint queued by default — the tech debt items above are filed but low priority. Next slice can be the cross-floor-shared-shape idea queued in `IDEAS.md` (2026-05-25) or a fresh `/idea`.

---

## 2026-05-28 — invent `lite-pdf-render-quality` (id 2026-05-27-23-05) — PAUSED at spike-PASS / sprint-1-WIP-uncommitted — [decision]

**What changed:** ผู้ใช้ตั้งคำถาม "lite เปิด PDF ไม่ชัดเท่า Foxit ทำไง" → /idea capture → /bma-invent 7-phase pipeline เดิน 6 เฟส:
- Phase 2 RESEARCH (bma-researcher) verdict `PRIOR_ART_PARTIAL` — Bluebeam iterated-draw mature, PDF.js/PDFium-WASM/mupdf-wasm rejected เพราะ coord-math divergence risk
- Phase 4-5 DIVERGE (bma-inventor) 5 approaches: A DPR-aware scale=3.0 / B PNG lossless / C zoom-triggered re-render / D viewport crop / E WebP gate. Top score A=26, fallback B=25
- Phase 6 SPIKE v1 — `lite/sandbox/invent-lite-pdf-render-quality.html` + `render_variants.py` rendered 5 variants of RAMA4 + ผัง.pdf. Finding: PNG smaller+faster than JPEG on dense line-art (RAMA4) แต่ใหญ่ 6×+ บน A3 coloured fill (ผัง.pdf), A+B violated SC-4 encode-time-≤4× budget on ผัง (4.45×)
- User reframe mid-checkpoint: "Concept: เปิดไฟล์ใน Chrome zoom 500% ยังคม" → server-side fixed-resolution raster (A/B/F) cannot match. Only C/G/D match concept
- Phase 2-extension RESEARCH (focused on PDFium/PDF.js) verdict `SPIKE_PDFJS_NOW` — Chrome PDF viewer = PDFium + tile-based LOD, PDF.js mature but DPR double-apply + async-cancel gotchas known
- Phase 6 SPIKE v2 — `invent-lite-pdf-render-quality-pdfjs.html` — single-canvas PDF.js. User tested zoom 5× → กระตุก. Confirmed memory blow-up: 8932×6315 CSS×DPR=2 = ~900 MB canvas allocation. PDF.js single-canvas fundamentally cannot match Chrome at zoom ≥3× on A1+retina
- User explicitly stated use case "lite zoom ประมาณ 1000%" → Tier 2 viewport-clipped required
- Phase 6 SPIKE v3 — `invent-lite-pdf-render-quality-pdfjs-v3.html` (417 LOC) — viewport-clipped via PDF.js `render({transform})`, fixed canvas dimensions, mouse-drag pan. Playwright sweep `drive_v3.py` on ผัง.pdf 14/14 combos PASS (zoom 1×/2×/5×/10×/20×/50×/100× × rotation 0°/90°/180°/270°); memory CONSTANT 13.6 MB at all zoom; contract delta=0.000 all combos. Full-document sweep `drive_v3_all_pages.py` on 90.8 MB / 95-page A1 CHH submission: zoom 1× median 590 ms / p95 3658 ms / max 4186 ms (5 complex pages 3.6-4.2s tail), zoom 5× sampled 29-125 ms across pages (faster than zoom 1× because viewport-clip cuts data)
- Sprint #1 PDFJS-PREP-EXTRACT-RENDERER via /bma-lite-dev (lite-builder sonnet, 2 round-trips 1a+1b): ui-lite.html 1195→1100 (-95 lines), NEW `lite/static/js/page-renderer.js` 98 LOC (owns imgCache/curImg/pageRot/loadPage/fit/resize/drawImage), NEW `lite/static/js/export-annotate.js` 87 LOC (owns exportXlsx/exportPdfOverlay/openReport + payload builders + reportPageTitle/buildReportPayload). PURE REFACTOR — function bodies byte-identical, forbidden surfaces (RS at line 220 measure-engine.js script tag intact, screenToPt body at line 260, areaOf at line 327, polyMetrics({pts:o.pts}) at line 999) verified by grep. py_compile PASS
- Sprint #2 PDFJS-VIEWPORT-CLIPPED-INTEGRATION designed not started — ~250 LOC into page-renderer.js (PDF.js loader, render-with-transform, mouse pan, loading indicator), expected ~30 LOC ui-lite.html (canvas swap, script tags). Reference impl = v3 spike. Test gate awaits arcHUDText debt fix

**Why PAUSED:** User said "เก็บไว้ทำต่อ" + "จากเครื่องอื่น". Google Drive sync of working tree covers cross-machine transfer — no commit/push required. State documented in `docs/invent/lite-pdf-render-quality.md` § Decision (full 5-step resume), `docs/status/PHASE_INDEX.md` Discovered backlog (status `invent-paused`), `docs/status/NEXT_ACTIONS.md` (Immediate Next), `CURRENT_STATUS.md` (One-Line Status updated), and `~/.claude/ideas/IDEAS.md` (user-level, status invent-paused). Pre-existing housekeeping debt blocks lite test infra: `arcHUDText is not defined` at runtime because `draw-arc.js` deleted from disk (git status: D) but still `<script src="…draw-arc.js">` referenced at `ui-lite.html:221`. ~5-line cleanup outside this invent scope but ungates Playwright regression for Sprint #2

**Files touched (all uncommitted WIP):**
- NEW `docs/invent/lite-pdf-render-quality.md`
- NEW `lite/sandbox/invent-lite-pdf-render-quality.html` (spike v1, 5-cell visual comparison)
- NEW `lite/sandbox/invent-lite-pdf-render-quality-pdfjs.html` (spike v2, single-canvas PDF.js)
- NEW `lite/sandbox/invent-lite-pdf-render-quality-pdfjs-v3.html` (spike v3, viewport-clipped, 417 LOC, reference for Sprint #2)
- NEW `lite/sandbox/invent-lite-pdf-render-quality/` dir — `render_variants.py`, `drive_v3.py`, `drive_v3_all_pages.py`, `stats.json`, `v3-results/` (14 PNG screenshots), `v3-all-pages-results/results.json`, 5 pre-rendered raster variants (.jpg + .png)
- NEW `lite/static/js/page-renderer.js` (Sprint #1 extract, 98 LOC)
- NEW `lite/static/js/export-annotate.js` (Sprint #1 extract, 87 LOC)
- MODIFIED `lite/ui-lite.html` (Sprint #1 refactor, -95 lines)
- MODIFIED `docs/status/PHASE_INDEX.md` (added `### ideas 2026-05-27` block + sprint plan)
- MODIFIED `docs/status/NEXT_ACTIONS.md` (Immediate Next = resume instructions)
- MODIFIED `CURRENT_STATUS.md` (date + One-Line Status updated to 2026-05-28)
- MODIFIED `~/.claude/ideas/IDEAS.md` (user-level, status invent-paused) — NOT in repo

**Tests:**
```
python -m py_compile lite/server_lite.py          → PASS
forbidden-surface grep (RS/polyAreaM2/polyMetrics/ptToScreen/screenToPt/pdfToC/cToPdf/measure-engine.js) on git diff → no removals (context shift only); script tag intact at ui-lite.html:220
size cap (ui-lite.html ≤1200, others ≤1000) → ui-lite.html 1100 ✓ / page-renderer.js 98 ✓ / export-annotate.js 87 ✓
spike Playwright (CLIPPED mode, 14 combos zoom×rotation on ผัง.pdf) → 14/14 PASS, mem constant 13.6 MB
spike Playwright (full-document sweep 95 pages × A1 CHH) → median 590ms / p95 3658ms / max 4186ms at zoom 1×, 29-125ms at zoom 5×
lite/tests/test_pf_kind_folders.py → FAIL pre-existing (arcHUDText not defined; unrelated to this slice)
```

**Resume:** see `docs/invent/lite-pdf-render-quality.md` § Decision for 5-step plan: (1) git status (2) fix arcHUDText debt (3) re-run test_pf_kind_folders (4) commit Sprint #1 (5) `/bma-lite-dev` for Sprint #2 (PDFJS-VIEWPORT-CLIPPED-INTEGRATION; spec lives in same artifact's Spike v3 section).

---

## 2026-05-26 — BUG-20260526-lite-stale-pf-folder-cleanup — PASS (branch: main)

**What changed:** แก้บั๊กที่ `seedPageFolders()` ใน `lite/static/js/page-folder-layers.js` ไม่เคยลบ PF folder เก่าที่หายออกไปจาก map — `removeFolder` ถูก import ที่ line 8 แต่ไม่เคยถูกเรียก. ผล: ทุกครั้งที่ user re-tag floor page ให้ไม่ใช่ floor, `PF_floor_N` folder + 3 seed layers ("GFA ชั้น N", "หักช่องลิฟต์", "หักช่องบันได") ค้างอยู่เป็น ghost row. Fix เพิ่ม `_pflFolderHasUserDrawnObjects(folderId)` + `_pflPrunePF(activeFolderIds)` internal helpers; `seedPageFolders` เรียก `_pflPrunePF` หลัง add/update loop (ก่อน LFOC-ORDER-A re-rank). Safety guard: folder ที่ยังมี user-drawn objects ในตัว (objects ที่ `catId` ตรงกับ descendant layer) จะไม่ถูก prune — ป้องกันลบงานผู้ใช้โดยไม่ตั้งใจ. Return shape เพิ่ม field `pruned` (additive, in-memory เท่านั้น, ไม่ serialize). Discovery ผ่าน `/bma-simulate` run `basement-order-exclude-stale-20260526T173000` (BUG-HYP-2: `stale_PF_floor_1_exists=true`, 3 lingering layers ยืนยัน CONFIRMED). BUG-HYP-1 (basement-before-floor order) was NOT a bug — `_rankPFFolder` ให้ B1=95, floor1=110 ถูกต้องตาม LFOC-ORDER-A design.

**Why:** ผู้ใช้รายงาน "layer กับ pagesetup น่าจะมีปัญหา กับชั้นใต้ดินใน layer" → `/bma-simulate` ยืนยัน stale PF folder หลัง exclude page. Stale folders ทำให้ UI layer panel เต็มด้วย ghost rows, catlist มี "ชั้น 1" ทั้งที่ page ถูก exclude แล้ว, และอาจ confuse summary/export ที่ iterate layers. Root cause ชัดเจน: `removeFolder` imported แต่ไม่เคย called ทุก sprint ที่ผ่านมาตั้งแต่ LPFL-1.

**Files touched:**
- `lite/static/js/page-folder-layers.js`: +47/-2 (743→790 lines, ≤1000 cap) — added `_pflFolderHasUserDrawnObjects`, `_pflPrunePF`, wired into `seedPageFolders`, return shape adds `pruned`
- `lite/tests/test_pf_cleanup_on_exclude.py`: NEW 168 lines — 4-case Playwright, marker `PF_CLEANUP_OK` (case A basic cleanup / case B safety preservation / case C idempotency / case D PF_excluded never pruned)
- `.claude/skills/bma-simulate/regression_probes.json`: setup_js for LITE-BUG-DBLCLICK-OVER-POP probe updated to call `_lwizAutoLiftLock()` + clear `ov.show` class (partial fix; full probe rewrite deferred to LITE-PROBE-DBLCLICK-REWRITE)

**Tests:**
```
python -m py_compile lite/server_lite.py          → OK
python lite/tests/test_pf_cleanup_on_exclude.py   → PF_CLEANUP_OK 4/4
python lite/tests/test_page_folder_model.py       → LITE_PAGE_FOLDER_MODEL_OK
python lite/tests/test_page_folder_persist.py     → LITE_PAGE_FOLDER_PERSIST_OK
python lite/tests/test_pf_kind_folders.py         → LITE_PF_KIND_OK 11/11
python lite/tests/test_custom_layer_persist.py    → LITE_LAYER_PERSIST_OK
python lite/tests/test_tree_persist.py            → LITE_TREE_PERSIST_OK
/bma-simulate verify re-run                       → PF cleanup VERIFIED PASS (stale_PF_floor_1_exists=false)
Manual e2e verify_dblclick_manual.py              → DBLCLICK_OK (objects=1, pts=4)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema additive only (return-value field `pruned` is in-memory, not serialized)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` UNCHANGED (at 1200/1200 cap)

**Known gaps / follow-ups:**
- LITE-PROBE-DBLCLICK-REWRITE (medium priority): Rewrite `LITE-BUG-DBLCLICK-OVER-POP` probe from `mouse_sequence` to `evaluate`-only — directly inject `state.draft` points then dispatch synthetic dblclick event on `cv`. Makes probe robust against future UI workflow changes (wizard auto-open, modal overlays) that block real mouse events.

---

## 2026-05-25 (LOVS-1) — Lite Overview Setup wizard — DONE — branch: main

**Trigger**: user followed up on LPFL-1 — "ในหน้า overview ทำให้ setup page ได้ เหมือน sandbox [wizard-H]" → 1st spike `invent-overview-setup.html` (inline edit only) → user added "ทำ multi-select และทำ tab Number Floors + Review" → spike v2 (3-tab wizard + multi-select) → user `/goal ทำให้เรียบร้อย` → ship LOVS-1.

**What shipped (1 atomic slice)**:
- NEW `lite/static/js/overview-setup.js` (668/900) — 3-tab wizard wraps live `openOv()`:
  - **Step 1 Classify**: tile grid with inline tag-chip cycle + floor-input + **multi-select** (shift+click range / ctrl+click toggle / drag-rectangle box-select / Ctrl+A) → bulk-bar applies tag to all / exclude-toggle. Right-click context menu (multi-select aware). Keyboard 1-6 (bulk if multi), 0 clear, ←→ focus (Shift extends), Enter navigate, X exclude.
  - **Step 2 Number Floors**: floor pages as draggable HTML5 chips → swap floor# on drop. Sequential auto-assigns 1→N (last = `roof` if ≥4 floors). clear.
  - **Step 3 Review**: mock BCR/FAR/OSR report + traceability + warnings.
- EDIT `lite/static/js/page-folder-layers.js` (547 → 557) — 9-line IIFE injects `<script src="static/js/overview-setup.js">` into `document.head` (idempotent via `#__lovs_script__` guard).
- NEW `lite/tests/test_overview_setup.py` — 8 sub-checks Playwright, marker `LITE_OVERVIEW_SETUP_OK`.

**Tests run** (all GREEN):
- `LITE_OVERVIEW_SETUP_OK` 8/8
- `LITE_PAGE_FOLDER_UI_OK` 7/7
- `LITE_PAGE_FOLDER_MODEL_OK` 12/12
- `LITE_PAGE_FOLDER_PERSIST_OK` 6/6
- `LITE_TREE_UI_OK` 9/9
- `LITE_LAYER_DND_OK` 4/4
- `MEASURE_PARITY_OK`

**Forbidden surfaces**: NONE touched (measure-engine.js, RS, pdfToC, cToPdf, area math, semanticTag, snap, .bmaplan schema, layer-system/tree/panel/dnd internals — all UNTOUCHED).

**Size discipline**: `ui-lite.html` STAYED at 1200/1200 (UNTOUCHED). `page-folder-layers.js` 547 → 557 (still <1000). New module 668/900. Cap held cleanly.

**Files**:
- NEW `lite/static/js/overview-setup.js` (668)
- NEW `lite/tests/test_overview_setup.py` (469)
- NEW `lite/sandbox/invent-overview-setup.html` (calibrated spike, 2 iterations — kept as design ref)
- MODIFIED `lite/static/js/page-folder-layers.js` (+9 lines IIFE)
- MODIFIED `lite/sandbox/invent-page-folder-layers.html` (earlier rewrite — workbench loading live modules; kept as canonical LPFL workbench)
- UPDATED `docs/design/LITE_LAYER_ROADMAP.md` (LOVS section)
- UPDATED `docs/status/PHASE_INDEX.md` (LOVS-1 marked done)
- UPDATED `log.md` (this entry)

**Known gaps / follow-ups:**
- none

---

<!-- BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 are the 2 sessions kept in this file -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
