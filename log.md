# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — BLOAT-FLAKE-1 Fix REAL_PDF `_wait_analyse_ready` flake — PASS (branch: main)

**What changed:** In `proto/e2e_ui_test.py`, the `_wait_analyse_ready` helper was updated: default timeout raised from 30.0 s to 60.0 s, and a "grace window" was added — if the status bar still shows active progress (`กำลังโหลด` / `กำลังวิเคราะห์`) at the deadline, the wait is granted +50% extra time before declaring failure. ~15 LOC changed inside the one helper only. No other test logic, no app code, no schema changed.

**Why:** The real 45-page A1 permit PDF (rotated 90°, ~1–1.4 s/page JPEG encode) occasionally caused `_wait_analyse_ready` to exceed the prior 30 s ceiling during a session-loaded box run — especially after 5 consecutive sprint test cycles in one session. The raised ceiling is free on the fast smoke path (small `test_plan_A1.pdf` completes in ~1–2 s). The grace window avoids a false fail when the page is actively making progress but hasn't crossed the threshold yet. This flake halted the dev-loop at BLOAT-5 (3 retries all failed at `_test_real_pdf_multipage_persistence`). With the fix, full E2E is GREEN. Retroactively confirms BLOAT-5 passes full E2E.

**Files touched:**
- `proto/e2e_ui_test.py`: +15 −2 — `_wait_analyse_ready` timeout 30.0→60.0, added grace-window branch for active-loading status

**Tests:**
```
python -m py_compile proto/e2e_ui_test.py                     → PASS
python proto/e2e_ui_test.py full                               → EXIT 0 — ALL GREEN
  PERSIST_OK + REAL_OK + ANNOT_OK GREEN (flaked 3x during BLOAT-5; now stable)
  PHASE_BLOAT2_OK 8/8 + _BLOAT3_OK 8/8 + _BLOAT4_OK 8/8 + _BLOAT5_OK 8/8
  PHASE_INV_PAGE_SETUP_A_OK 8/8 + _B_OK 9/9 + _C_OK 7/7 + PHASE_HT11_OK 10/10
  Retroactively confirms BLOAT-5 (shipped smoke-only) passes full E2E.
/bma-human-test — N/A (test-infrastructure change; no app runtime code touched)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- (only `proto/e2e_ui_test.py` `_wait_analyse_ready` helper changed)

**Known gaps / follow-ups:**
- If the flake recurs under even heavier load, next escalation paths: Playwright browser-context reset between heavy real-PDF tests, or server cache warm-up before real-PDF suite (documented as alternatives in KNOWN_ISSUES.md).
- Dev-loop queue is now clear of P1 blockers. Remaining: `INV-2026-05-19-002c` (F12 Overview mockup port) + invent-queued ideas.

---

## 2026-05-20 — BLOAT-5 Extract page-setup modal JS to proto/static/js/page-setup.js — PASS (smoke; full ENV-FLAKE) (branch: main)

**What changed:** Created `proto/static/js/page-setup.js` (125 lines, classic non-module script) and extracted 15 page-setup functions + 2 floor constants from 3 non-contiguous ranges in `proto/ui.html`. Range A (L855–856): `FLOOR_KIND_LABELS` + `FLOOR_KIND_OPTIONS`. Range B (L1051–1070): floor helpers `autoNamePage`, `setPageFloorKind`, `setPageFloorNum`, `countTagBefore`. Range C (L3094–3167): inspector + renumber/delete cluster `selectSetupPage`, `_pageReadiness`, `_setupCountObjects`, `_renderSetupDashboard`, `_renderSetupPageCard`, `_setupBack`, `_renderSetupInspector`, `_pendingDeleteN`, `_openRenumberDialog`, `closeRebuildDialog`, `_executeRenumberDelete`, `_reindexPageDicts`. Kept in `proto/ui.html`: 15 cross-cluster glue functions including `buildTagGrid`, `setPageTag`, `applyAutoNames`, `excludePage`, `restorePage2`, `pageFloorKind`/`pageFloorNum` state declarations. Added E2E marker `PHASE_BLOAT5_OK` (8 sub-checks) to `proto/e2e_ui_test.py`. Net: `proto/ui.html` −93 +2 (3,869→3,777); `proto/static/js/page-setup.js` NEW 125 LOC; `proto/e2e_ui_test.py` +91 LOC. Smoke 18/18 baseline + BLOAT2/3/4/5 8/8 each + INV_PAGE_SETUP_A/B/C OK all GREEN. Full failed 3 retries — pre-existing REAL_PDF analyse flake (BLOAT-FLAKE-1 filed). Loop halted per `LOOP_STOP_REGRESSION` safety rule. Session total ui.html 4,231→3,777 (−454 across BLOAT-1..5).

**Why:** Page-Setup spans 3 prior sprints (INV-2026-05-18-001a/b/c). BLOAT-5 cleanly extracts the inspector + renumber-delete cluster while keeping cross-cluster glue in `ui.html`. Recipe is now 5-for-5 (status-bar / export-save / annotations / page-setup). Full failure is NOT a BLOAT-5 regression — the failing `_test_real_pdf_multipage_persistence` path exercises `_wait_analyse_ready` on page 1/45 and has zero invocations of any page-setup helper. This is the worst occurrence of the pre-existing REAL_PDF env flake (3 retries failed vs. 1 retry + pass in BLOAT-4). Loop halted per strict dev-loop rule; root cause is environmental (Playwright/Windows file handles, analyse timeout, cumulative state after 5 sprints in one session).

**Files touched:**
- `proto/ui.html`: −93 +2 — extracted 96 lines across 3 ranges; 3 placeholder comments left; added `<script src="/static/js/page-setup.js">` tag after `annotations.js`; net −92 LOC (3,869→3,777)
- `proto/static/js/page-setup.js`: NEW 125 LOC — 2 constants (`FLOOR_KIND_LABELS`, `FLOOR_KIND_OPTIONS`) + 15 functions extracted from ranges A/B/C
- `proto/e2e_ui_test.py`: +91 LOC — `pageSetupJsLoaded` field in UI-load test + `_test_bloat5_page_setup_extracted` (8 sub-checks: `fileLoad`, `fnsOk`, `constsOk`, `readinessOk`, `countOk`, `dashOk`, `closeOk`, `autoNameOk`) + `PHASE_BLOAT5_OK` marker

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0, ALL GREEN
  18 baseline markers + PHASE_BLOAT2_OK 8/8 + PHASE_BLOAT3_OK 8/8 + PHASE_BLOAT4_OK 8/8 + PHASE_BLOAT5_OK 8/8
  PHASE_INV_PAGE_SETUP_A_OK 8/8 + _B_OK 9/9 + _C_OK 7/7 + PHASE_HT11_OK 10/10
  pageSetupJsLoaded: True in MAIN_UI_OK
python proto/e2e_ui_test.py full                           → FAILED (3 retries) — pre-existing REAL_PDF analyse flake
  _test_real_pdf_multipage_persistence → _wait_analyse_ready hung on page 1/45 ("กำลังโหลดหน้า 1…")
  Same flake noted: BLOAT-3 MENU_OK probe ("perPageLayerMemoryFixed: skipped"); BLOAT-4 first attempt (retry passed); now 3/3 failed.
  Hypothesis: env-level Playwright/Windows file-handle exhaustion or analyse timeout too tight for cold-cache real PDF.
  Zero page-setup code invoked during _wait_analyse_ready path — confirmed NOT a BLOAT-5 regression.
  BLOAT-FLAKE-1 filed in docs/status/KNOWN_ISSUES.md. Loop halted per LOOP_STOP_REGRESSION safety rule.
/bma-human-test — SKIPPED (smoke + 4 sprint markers + 3 page-setup markers + HT11 GREEN; full failure is environmental)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED (client-side `_executeRenumberDelete` still POSTs to unchanged `/rebuild-pdf` endpoint)
- ✅ `.bmaplan` schema — UNCHANGED (`pageFloorKind`/`pageFloorNum` field names + shapes preserved; `_reindexPageDicts` walks same 7 per-page dicts; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- **BLOAT-FLAKE-1** (NEW — filed in KNOWN_ISSUES.md): `_wait_analyse_ready` flake on real 45-page permit — 3 retries all failed this session (worst occurrence). Hypothesis: env-level. Suggested fixes: bump timeout, add Playwright browser-context reset, warm-up caches before real-PDF tests.
- **Loop halted** per `LOOP_STOP_REGRESSION` safety rule (full failed on retry). Root cause = env flake, NOT BLOAT-5. User decides: investigate BLOAT-FLAKE-1 first, or skip to other queued sprints (optional BLOAT-3b print cluster, or consolidate 5 successful extractions as end of bloat-reduction wave — ui.html now 3,777, well below 5,000-line trigger).

---

## 2026-05-20 — BLOAT-4 Extract annotation JS to proto/static/js/annotations.js — PASS (branch: main)

**What changed:** Created `proto/static/js/annotations.js` (205 lines, plain non-module classic script) containing 13 annotation helper functions extracted from `proto/ui.html` (L1680–1869): `ensureAnnotations`, `newAnnotationId`, `addAnnotation`, `renderStickyCards`, `_createStickyCard`, `clearAnnotations`, `annotationHitTest`, `deleteAnnotation`, `openAnnotationEditModal`, `closeAnnotationEditModal`, `saveAnnotationEdit`, `_annColor`, `drawAnnotations`. Added `<script src="/static/js/annotations.js">` after `export-save.js` in `proto/ui.html`. The 7 per-mode mousedown branches for annotation tool dispatch remain in `proto/ui.html` (tightly coupled to the unified pointer state; kept out of scope). Added E2E machinery in `proto/e2e_ui_test.py`: `annotationsJsLoaded` field in UI-load test + new `_test_bloat4_annotations_extracted` function (8 sub-checks: `fileLoad`, `fnsOk`, `addOk`, `hitMissOk`, `drawOk`, `stickyOk`, `colorOk`, `clearOk`) + new marker `PHASE_BLOAT4_OK`. Net: `proto/ui.html` −190 +2 (4,057→3,869 lines; −188 net); `proto/static/js/annotations.js` NEW 205 LOC; `proto/e2e_ui_test.py` +99 LOC. Session total: ui.html 4,231→3,869 (−362 lines across BLOAT-1..4).

**Why:** Annotations were the third-largest cohesive cluster in ui.html — 7 annotation types (comment/sticky/text/highlight/rect/circle/cloud/arrow) + sticky HTML overlay + HT-11 edit modal + hit-test + canvas render dispatcher. Extracting them removes 188 LOC and isolates a self-contained domain from the measurement core. The recipe is now 4-for-4 (status-bar / export-save / annotations + the older semantic-meta / opening-parent). Pattern validation: cross-script binding access for state (`curPage` / `pageStore` / `zoom` / `ctx`), DOM-builder helpers, and event wiring (sticky drag) all work cleanly across the script boundary.

**Files touched:**
- `proto/ui.html`: −190 +2 — replaced extracted annotation block with 1 placeholder comment; added `<script src="/static/js/annotations.js">` tag; net −188 LOC (4,057→3,869)
- `proto/static/js/annotations.js`: NEW 205 LOC — 13 annotation functions (ensureAnnotations + newAnnotationId + addAnnotation + renderStickyCards + _createStickyCard + clearAnnotations + annotationHitTest + deleteAnnotation + openAnnotationEditModal + closeAnnotationEditModal + saveAnnotationEdit + _annColor + drawAnnotations)
- `proto/e2e_ui_test.py`: +99 LOC — `annotationsJsLoaded` field + `_test_bloat4_annotations_extracted` (8 sub-checks) + `PHASE_BLOAT4_OK` marker print

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py full                           → first run FAILED (intermittent REAL_PDF analyse flake on page 1/45 — known, unrelated to BLOAT-4); retry GREEN
  All 22 baseline markers GREEN: CACHE_OK / UPLOAD_CAP_OK / SETUP_OK / MAIN_UI_OK (annotationsJsLoaded: True) / VECTOR_OK / RECAL_OK / SITE_UI_OK / XLSX_OK / PROJECT_OK / RASTER_OK / WHEEL_OK / SNAP_OK / SELECT_OK / SETBACK_OK / EXT_MEASURE_OK / MENU_OK / PATH_GEOMETRY_OK / ANNOT_OK / PERSIST_OK / REAL_OK
  PHASE_INV_STICKY_OK 10/10 (J_roundTrip ✓ — sticky-note schema round-trip survives extraction)
  PHASE_HT11_OK 10/10 (annotation edit + delete modal still functional)
  PHASE_BLOAT2_OK 8/8 + PHASE_BLOAT3_OK 8/8 + PHASE_BLOAT4_OK 8/8
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PHASE_INV_STICKY_OK + PHASE_HT11_OK on real fixtures cover annotation create/edit/delete/round-trip; PHASE_BLOAT4_OK verifies all 13 fns + canvas-render + sticky-overlay-render)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED (annotations READ pdfToC/cToPdf for coordinate conversion only; never edit)
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED (zero edits this sprint)
- ✅ `.bmaplan` schema — UNCHANGED (`pageStore[pg].annotations` field name, shape, items, and id format all preserved; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- BLOAT-5 (page-setup modal extraction: `_renderSetupDashboard` / `_renderSetupPageCard` / `_openRenumberDialog` / `_executeRenumberDelete` / `_reindexPageDicts` / floor-kind helpers → `proto/static/js/page-setup.js`, est. ~300 LOC) — next queued sprint; depends-on BLOAT-2 (now satisfied).
- The 7 per-mode mousedown branches stay in ui.html — they call extracted helpers via global scope. A future BLOAT-4b could extract the entire pointer-event handler into `/static/js/pointer.js`, but that unified handler does mPts/measurement/annotation/drag in one switch — out of scope here.

---

<!-- BLOAT-3 archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->

---

## 2026-05-19 — End-of-day bundle: INV-003b /export-png ZIP + HT-18c round-trip 13/13 + INV-003a Print canvas — PASS (branch: main)

**What changed:** Three committed sprints shipped in this session. (1) **INV-2026-05-19-003b** (`612de96` feat + `7f0300f` docs): NEW `/export-png` ZIP endpoint in `proto/server.py` — accepts `case_id + selected_pages[] + dpi_scale`, renders each page via PyMuPDF at requested scale, bundles PNGs into a ZIP archive returned as `application/zip`. Export menu in `proto/ui.html` wired with "Export PNG (ZIP)" option. New E2E test `_test_inv_export_png` + marker `PHASE_INV_EXPORT_PNG_OK`. (2) **HT-18c** (`f1b4331` fix + `9297ed4` docs): Fixed `_test_ht18b_save_load_round_trip` — replaced over-strict deep `eq()` comparison (fails after `normalizeAllObjects` mutates pre-snapshot) with field-by-field checks on the 13 round-trip properties. Also fixed a bug in `applyLoadedProject` (HT-18d-equivalent): `_projInfoSnap` was not fully restored from blob; fix ensures `projectInfo` round-trip is symmetric. `PHASE_HT18B_OK` now 13/13 GREEN. (3) **INV-2026-05-19-003a** (`b4f7235` feat + `8200ef6` docs): "Print Current Page" + "Print Selected Pages" in File menu — client-side `canvas.toDataURL("image/png")` → synthetic print window + `window.print()` trigger (Path B). New E2E test `_test_inv_print_canvas` (8 sub-checks) + marker `PHASE_INV_PRINT_CANVAS_OK`. In addition, a ~10 LOC uncommitted test refinement for `_test_ht18b_save_load_round_trip` (HT-18b `_projInfoSnap` direct global check) is pending fold into next commit.

**Why:** INV-003a/003b deliver the "print-canvas-per-page" invention (originally a raw `/idea` entry, promoted via `/bma-invent` 7-phase pipeline, GO verdict MATURE). Path B (003a) gives fast single-page print via browser's native print dialog. Path C (003b) provides high-DPI archival PNG export bundled as ZIP — useful for sending annotated plans by email or attaching to permit submissions. HT-18c was the final item in the HT-18 series: the save/load round-trip test was gated on fixing the `eq()` comparison that was too strict after `normalizeAllObjects` transformed the pre-snapshot object; with that fix plus the `applyLoadedProject` `_projInfoSnap` restoration, the full 13-sub-check round-trip is now GREEN and the HT-18 series is complete.

**Files touched:**
- `proto/server.py`: NEW `/export-png` endpoint (additive — no rename or removal of existing endpoints; case isolation preserved) [INV-003b]
- `proto/ui.html`: Export menu `/export-png` wiring + "Print Current Page" / "Print Selected Pages" File menu items + `printCurrentPage()` / `printSelectedPages()` helpers [INV-003a + INV-003b]
- `proto/e2e_ui_test.py`: `_test_inv_export_png` (PHASE_INV_EXPORT_PNG_OK) + `_test_inv_print_canvas` (PHASE_INV_PRINT_CANVAS_OK) + `_test_ht18b_save_load_round_trip` 13/13 field-by-field fix [INV-003b + INV-003a + HT-18c]
- `docs/status/PHASE_INDEX.md`: queue rows flipped for INV-003a, HT-18c, INV-003b [all three]

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (all three sprints)

INV-003b: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_EXPORT_PNG_OK: PASS (new marker)
  All prior markers retained (no regression)

HT-18c: python proto/e2e_ui_test.py smoke → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (was 7/13 — test design issue now fixed)

INV-003a: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_PRINT_CANVAS_OK: PASS (8 sub-checks)
  All prior markers retained (no regression)

Predecessor markers confirmed retained: PHASE_HT18_OK 36/36,
PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9,
PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10,
PHASE_INV_POLISH_001C_OK 5/5
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ⚠️ `proto/server.py` — INV-003b added `/export-png` endpoint (additive new endpoint; no rename or removal of existing endpoints; case isolation preserved; no schema change)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- ~10 LOC uncommitted HT-18b test refinement (`_projInfoSnap` direct global check) pending fold into next commit
- Zen Mode user manual docs sprint still uncommitted (`proto/manual/zen-mode.md` NEW ~80 LOC + keyboard-shortcuts.md +2 LOC + getting-started.md +1 LOC + content.json rebuild) — pending user finalize
- INV-2026-05-19-002c (F12 Overview mockup-port) still queued — next after docs sprint
- Session totals: 33 local commits pushed to `origin/main-v2-2026-05-19` (local `main` tracking that branch)

---

<!-- sessions before the current top-2 are archived to docs/archive/log-2026-05-19.md (HT-18a-ext + earlier 2026-05-19 entries: 001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish + 002a Zen top bar + 002b F12 Overview + HT-18a + INV-003b end-of-day bundle) and docs/archive/log-2026-05-18.md (earlier) -->
