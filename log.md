# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — INV-2026-05-19-001c Zen+Palette FRICTION polish — PASS (branch: main)

**What changed:** Polish sprint bundling 3 FRICTION findings from INV-001a/001b human-tests (~20 LOC total). `proto/ui.html`: (1) HT-Z-1 — `_zenSyncHud()` now reads `pageNames[curPage]` directly instead of via the `#bb-page-name` element, which lagged during fast minimap navigation; HUD displays "ชื่อหน้า (N/total)" format. (2) HT-Z-2 — `_zenSyncHud()` now colors the Scale HUD chip amber (`var(--orange)`) when `getScaleForPage(curPage).state === 'auto-unverified'` or when no scale is set; manual scale uses default white; a `title` tooltip explains the state. (3) HT-Z-3 — `filterPalette()` empty-results branch detects a Thai page-type word query (ผังบริเวณ|ชั้น|รูปด้าน|รูปตัด|รายละเอียด|ตาราง) AND no pages tagged, and appends a hint: "💡 แท็กภาษาไทยใช้ได้หลังตั้งค่าหน้าใน Page Setup". `proto/e2e_ui_test.py`: new `_test_inv_polish_001c(page)` with 5 sub-checks + `PHASE_INV_POLISH_001C_OK` marker (+65 LOC).

**Why:** HT-Z-1/HT-Z-2/HT-Z-3 were all FRICTION findings filed from the 001a/001b human-test journey. Batched as one small polish sprint per "one problem set" principle (all three touch the same two files, all three are sub-10-LOC edits, none require forbidden-surface changes). Clears the HT-Z queue and completes the Zen+Palette feature trilogy.

**Files touched:**
- `proto/ui.html`: ~15 LOC — 3 small edits in `_zenSyncHud()` (page-name direct read, amber scale chip) + `filterPalette()` empty branch Thai-tag hint
- `proto/e2e_ui_test.py`: +65 LOC — `_test_inv_polish_001c` (5 sub-checks), `PHASE_INV_POLISH_001C_OK` marker

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_POLISH_001C_OK 5/5 PASS (hudReadsPageNamesDirectly, unverifiedScaleAmber,
  manualScaleNotAmber, thaiTagHintShown, hintAbsentWhenTaggedOrNoThai)
  PHASE_INV_ZEN_OK 10/10 — no regression; PHASE_INV_PALETTE_OK 10/10 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
TEST-H: SKIPPED — 3 fixes are tiny visual/UX tweaks; all changed branches covered by
  PHASE_INV_POLISH_001C_OK markers. No new interactive flow requiring journey-level validation.
  Per AGENTS.md: sub-200-LOC polish with full marker coverage of all changed branches.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- none — HT-Z-1/HT-Z-2/HT-Z-3 all cleared; Zen+Palette trilogy complete

---

## 2026-05-19 — INV-2026-05-19-001b ⌘K Command Palette — PASS (branch: main)

**What changed:** Additive ⌘K Command Palette feature across three files. `proto/static/css/app.css`: `.cmd-palette` fixed-center modal (z-index 9500, above zen overlays at 1500), input field, results list, hint bar, color-coded tag chips (site/plan/elev/section/detail) — ~35 LOC appended. `proto/ui.html`: 5 new helpers (`togglePalette`, `closePalette`, `filterPalette`, `_palJumpToIdx`, `_palMoveSel`, `_palEsc`); `Ctrl+K`/`Cmd+K` keybind with mid-draw guard (`mPts.length===0`); ArrowDown/Up/Enter/Esc keydown branch placed BEFORE inInput guard so palette input does not swallow nav keys; View menu "🔍 ค้นหาหน้า (Command Palette) Ctrl+K" item; `#cmd-palette` modal HTML block — ~120 LOC additive. `proto/e2e_ui_test.py`: new `_test_inv_palette(page)` with 10 sub-checks + `PHASE_INV_PALETTE_OK` marker registered in main() — ~95 LOC.

**Why:** Companion sprint to INV-2026-05-19-001a (Zen Mode). The original idea `2026-05-19-01-36` was SPLIT_REQUIRED at the invent checkpoint into 001a (canvas chrome-hide + HUDs + minimap) and 001b (quick page search/jump). In Zen Mode the left-panel Sheets tab is hidden, so a keyboard-first page-jump mechanism becomes essential for high-density multi-page workflows. The palette is purely transient UI state — no schema changes, no server changes, composes cleanly above the zen z-index layer.

**Files touched:**
- `proto/static/css/app.css`: ~35 LOC — `.cmd-palette` modal, input, results list, hint bar, tag-chip colors
- `proto/ui.html`: ~120 LOC — `togglePalette`, `closePalette`, `filterPalette`, `_palJumpToIdx`, `_palMoveSel`, `_palEsc`, Ctrl+K keybind, ArrowDown/Up/Enter/Esc palette input handlers, View menu item, `#cmd-palette` DOM
- `proto/e2e_ui_test.py`: ~95 LOC — `_test_inv_palette` (10 sub-checks), `PHASE_INV_PALETTE_OK` marker

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_PALETTE_OK 10/10 PASS (helpersAndDomExist, paletteShownAndFocused,
  defaultPrefilterShows, numberFilterWorks, nameFilterWorks, tagFilterWorks,
  moveSelWorks, jumpClosesPalette, midDrawGuard, escClosesPalette)
  PHASE_INV_ZEN_OK still 10/10 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)             → JOURNEY_OK
  13/13 spec steps PASS; 0 JS errors
  HT-Z-3 filed: empty-state when filtering by Thai tag on untagged PDF
    lacks hint that Page Setup tagging is needed first (FRICTION)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — UNCHANGED (palette is purely transient UI state; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-Z-3: empty-state hint missing when filtering by Thai tag on an untagged PDF; filed to `PHASE_INDEX.md`
- HT-Z-1 + HT-Z-2 (from 001a) still open — can batch into a Zen polish sprint

<!-- sessions before 2026-05-19 INV-001b are archived to docs/archive/log-2026-05-19.md (001a Zen Mode + Ribbon Cleanup) and docs/archive/log-2026-05-18.md (earlier) -->
