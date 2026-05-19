# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — INV-2026-05-19-002a F11 Zen top bar (A+D additive bundled) — PASS (branch: main)

**What changed:** Additive `#zen-topbar` overlay (40px) that appears inside `body.zen` without touching 001a's `toggleZen()`. The bar contains 6 dropdowns (File / Page / Measure / Annotate / View / Help) wired to existing handlers, plus 4 icon chips (search / Zen palette / circle/ellipse shape picker / rectangle shape picker). New functions: `toggleZenFocus()` (F key in zen = Focus sub-mode, hides all HUDs via `body.zen.focus`), `_ztbToggleMenu(id, btn)` (dropdown open/close for topbar menus), `_setupZenEdgePeek()` (thin invisible strip at top of viewport triggers `body.zen.focus.peek` to temporarily restore HUDs while focused). `toggleZenMode` extended with v2 onboarding toast (green tint, shown once, stored in `PREFS.layout.zenV2Onboarded`). F-key scope guard: F key inside text inputs is blocked to prevent accidental focus toggle. `proto/static/css/app.css`: `.zen-topbar` + `.ztb-*` rules; `body.zen.focus` HUD hide with `!important` + transition suppressed for reliable Playwright testing; `.zen-focus-edge` 4 rules; 001a HUDs shifted top: 34→50px to make room; `.zen-v2-toast` green tint. New E2E function `_test_inv_zen_v2_topbar()` with 9 sub-checks + `PHASE_INV_ZEN_V2_OK` marker. Initial run had focusHidesHuds FAIL (transition delay); fixed with `!important` + removing transition on `.hud` during focus; retry → 9/9 PASS. TEST-H: `bma-human-journey-tester` HUMAN_TEST_PASS — 13/13 journey steps + 45/45 pages measured + .bmaplan round-trip OK; 1 minor FRICTION (test-infra only, not user-facing, not filed).

**Why:** Original INV-002a plan was a breaking change to 001a `toggleZen()`. User redirected during /bma-dev-loop SCOPE: "ทำแยกจากของ v1 ไปเลยจะดีกว่า" — non-breaking additive approach chosen. The 001a minimap, 3 HUDs, and hide-menubar behavior all remain unchanged. The new top bar gives Zen Mode users access to all major menu actions without exiting Zen (a key gap identified in the 001a human-test journey). F12 Overview stub is defined in this sprint but the actual Overview implementation is deferred to INV-002b.

**Files touched:**
- `proto/ui.html`: +133 LOC — `#zen-topbar` HTML (6 dropdowns + 4 chips + edge triggers + v2 toast); `toggleZenFocus`, `_ztbToggleMenu`, `_setupZenEdgePeek`; F-key scope guard; `toggleZenMode` v2 onboarding logic
- `proto/static/css/app.css`: +40 LOC — `.zen-topbar` + `.ztb-*` rules; `body.zen.focus` HUD hide (`!important`); `body.zen.focus.peek` restore; 4 `.zen-focus-edge` rules; 001a HUDs shifted top:34→50px; `.zen-v2-toast` green tint
- `proto/e2e_ui_test.py`: +128 LOC — `_test_inv_zen_v2_topbar()` (9 sub-checks); `PHASE_INV_ZEN_V2_OK` print line; registered in main() pipeline

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_ZEN_V2_OK 9/9 PASS (topbarExistsAndShort, sixDropdownsExpectedLabels,
  fourChips, focusHidesHuds, peekRestoresHuds, fKeyScopeGuard, v2OnboardingToastShown,
  no001aRegression, paletteAboveTopbar)
  PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10, PHASE_INV_POLISH_001C_OK 5/5 — no regression
python proto/e2e_ui_test.py full                           → EXIT 0
  ANNOT_OK / PERSIST_OK / REAL_OK — all PASS
  Pre-existing non-regressions (not caused by this sprint): PHASE_HT8C_OK 3/5,
  PHASE_HT8D1_OK 8/9, PHASE_HT10_OK 8/10, PHASE_HT12H_OK 4/5, PHASE_I_D_OK 7/8
TEST-H: HUMAN_TEST_PASS — 13/13 journey steps; measure 45/45 pages; .bmaplan round-trip OK;
  1 FRICTION (test-infra only: lbl-scale doesn't update on programmatic calibScale inject;
  real calib dialog calls updateAnalyseUI correctly — not user-facing, not filed)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — UNCHANGED (`PREFS.layout.zenV2Onboarded` is session pref, not project schema; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Layer model: no name-based calculation introduced

**Known gaps / follow-ups:**
- INV-2026-05-19-002b: F12 Overview spatial map standalone mode — next queue item; depends-on 002a `#zen-topbar` chrome
- Top bar dropdown items use direct onclick wiring to existing handlers (no `ZEN_MENU_ITEMS` shared array yet — deferred to polish sprint if duplication grows)
- Onboarding toast text simplification could be a future UX polish item

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

<!-- sessions before 2026-05-19 INV-001c are archived to docs/archive/log-2026-05-19.md (001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish) and docs/archive/log-2026-05-18.md (earlier) -->
