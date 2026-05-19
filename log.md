# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup + 001c FRICTION polish + 002a Zen top bar + INV-003b end-of-day bundle)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — BLOAT-1 CLAUDE.md LOC drift fix + consolidation trigger rule (docs-only) — DOCS-ONLY (branch: main)

**What changed:** Corrected stale LOC baselines in `CLAUDE.md` (Architecture section + bma-explorer subagent table) — `proto/ui.html` was recorded as ~1,700 lines but had grown to ~4,230 (+149%); `proto/server.py` was recorded as ~1,370 but had grown to ~1,750. Added a new "Size discipline" paragraph after the architecture block documenting the drift history and a hard rule: if `proto/ui.html` crosses 5,000 lines the next sprint MUST be a consolidation sprint extracting one cohesive JS region to `static/js/<region>.js` (following the existing `semantic-meta.js` / `opening-parent.js` pattern). Inserted BLOAT-1..5 sprint rows into `docs/status/PHASE_INDEX.md` active queue and a `### bloat-audit 2026-05-19` block in the Discovered backlog.

**Why:** Pre-loop bloat audit (user-initiated, 2026-05-19): "โปรแกรม เริ่ม ทำงานได้ช้าไหม ไฟล์อ้วนไหม". Manual analysis found `proto/ui.html` at 4,231 lines / 360 KB / 483 functions — 2.5× the baseline recorded in `CLAUDE.md`. The `/bma-dev-loop` has no consolidation phase (always adds, never re-flattens), so drift will continue. Correcting the baseline prevents future agents from anchoring size-budget decisions on a stale number. The consolidation trigger rule (>5,000 lines → must extract) creates a self-enforcing size discipline without requiring manual oversight every sprint.

**Files touched:**
- `CLAUDE.md`: +21 −2 — LOC correction in Architecture section (3 edits: server.py ~1370→~1750, ui.html ~1700→~4230) + new Size discipline paragraph + bma-explorer subagent row LOC correction
- `docs/status/PHASE_INDEX.md`: +26 −0 — BLOAT-1..5 active-queue rows + `### bloat-audit 2026-05-19` Discovered-backlog block

**Tests:**
```
python -m py_compile proto/server.py  → PASS (sanity baseline only)
/bma-e2e skipped — docs-only sprint; CLAUDE.md is not imported by any runtime; no code path touched.
/bma-human-test skipped — docs-only sprint.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- BLOAT-2..5 queued in active queue. BLOAT-2 (status-bar JS extraction to `static/js/status-bar.js`) is next; `/loop /bma-dev-loop` will pick it automatically.
- Target: bring `proto/ui.html` back under 5,000-line trigger after BLOAT-2..5; long-term goal ~3,000 lines.

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
