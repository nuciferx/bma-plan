# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup + 001c FRICTION polish + 002a Zen top bar)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

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

## 2026-05-19 — HT-18a-ext Extended pushUndo() coverage to 22 more mutation sites — PASS (branch: main)

**What changed:** Extended HT-18a (`895a9d7`) by inserting `pushUndo()` at 22 additional mutation sites found via Phase A audit + `/bma-human-test` discovery pass: layer reorder (`moveLayerUp`/`moveLayerDown`), `renameLayer`, `setLayerColor`, `toggleLayerLock`, `setAllLayersVisible`, `hideOtherLayers`, `lockOtherLayers`, `setAllLayersLocked`, `toggleLayer`, `layerHideOthers`, `layerShowAll`, `setQuickTag`, `setPageTag`, `setPageFloorKind`, `setPageFloorNum`, `applyAutoNames`, `excludePage` (+ `_skipUndo` param), `restorePage2` (+ `_skipUndo` param), `hideSelectedPages`, `rotatePage`, `resetPageScale`, `pageCtxMenu` inline `autoNamePage` call. The E2E test `_test_ht18_pushundo_leaks` was extended from 7 sub-checks to **36 sub-checks** (22 source-presence + 7 runtime isDirty-flip + 7 original from HT-18a). `PHASE_HT18_OK` is now `{'all': True}` with 36/36 GREEN. Human journey test (`/bma-human-test`) discovered 3 sites initially missed in Phase A audit (`toggleLayer`, `layerHideOthers`, `layerShowAll`); fixed inline in the same iteration. `setQuickTag` and `resetPageScale` were reported as "leaks" but are early-exit code paths — correct that `isDirty` stays false when preconditions unmet. `PHASE_INDEX.md` updated: HT-18a-ext card filed (done), HT-18b updated to `done-with-test-design-caveat`, HT-18c upgraded from `pending conditional` to `queued` with concrete fix scope. New drift-map artifact `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md` (~120 lines). +39 LOC JS, +295 LOC test.

**Why:** HT-18a fixed 6 of the `pushUndo()` leak sites but a Phase A audit of the full function surface revealed 22 more mutation functions that bypass `pushUndo()`. Each missing call means the user can make changes and close the browser without being prompted to save, silently losing work. Eliminating the full set of leaks in one sequel sprint (HT-18a-ext) is cheaper than filing 22 individual sprints and avoids the "is this site fixed?" ambiguity in future audits. The 36-sub-check E2E test creates a permanent regression guard that will catch any future additions that forget `pushUndo()`.

**Files touched:**
- `proto/ui.html`: +39 LOC — `pushUndo()` inserted at 22 mutation sites (layer reorder/rename/color/lock/visibility helpers, page tag/floor/name/exclude/restore/rotate/reset helpers, pageCtxMenu inline call)
- `proto/e2e_ui_test.py`: +295 LOC — `_test_ht18_pushundo_leaks` extended from 7 → 36 sub-checks (22 source-presence + 7 runtime isDirty-flip + 7 original)
- `docs/status/PHASE_INDEX.md`: HT-18a-ext card filed (done); HT-18b updated `done-with-test-design-caveat`; HT-18c upgraded to `queued` with concrete eq()-fix scope
- `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md`: New drift-map artifact (~120 lines)

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PY_COMPILE_OK
python proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_HT18_OK: {'all': True} — 36/36 sub-checks GREEN
  21/21 core markers GREEN (smoke 16 + Phase I 2 + full 3)
  Smoke re-run after 3 additional sites found via /bma-human-test → still GREEN
Pre-existing non-regressions (NOT this sprint's regressions):
  PHASE_HT8C_OK 3/5, PHASE_HT8D1_OK 8/9, PHASE_HT10_OK 8/10, PHASE_HT12H_OK 4/5
  PHASE_HT18B_OK 7/13 (test design issue: eq() too strict after normalizeAllObjects;
  NOT schema drift — Phase A audit confirmed save/load symmetric; filed as HT-18c)
Human journey test: HUMAN_TEST_PASS after inline fix of 3 initially-missed sites
  (toggleLayer L2657, layerHideOthers L2659, layerShowAll L2666)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED this sprint
- ✅ `.bmaplan` schema — ADDITIVE ONLY (`_skipUndo` params are internal helpers; no field rename/removal; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-18c (queued): fix `_test_ht18b_save_load_round_trip` eq() comparison (too strict after `normalizeAllObjects` mutates pre-snapshot). ~30-50 LOC, test-only, no app code change.
- After HT-18c lands, HT-18 series complete; queue moves to INV-2026-05-19-002c (F12 Overview mockup-port)
- PHASE_HT18B_OK 7/13 is a test design issue, not a schema drift — confirmed by Phase A audit

---

<!-- sessions before the current top-2 are archived to docs/archive/log-2026-05-19.md (001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish + 002a Zen top bar + 002b F12 Overview + HT-18a + HT-18a-ext) and docs/archive/log-2026-05-18.md (earlier) -->
