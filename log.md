# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — INV-2026-05-19-002b F12 Overview standalone (C) — PASS (branch: main)

**What changed:** F12 Overview mode implemented as approach C standalone. `body.overview` class hides canvas, ribbon, panels, status bar, and all HUDs; shows `#overview-content` grid grouped by 6 discipline categories (site/plan/elev/section/detail/none). Shared `#zen-topbar` from 002a remains visible as navigation chrome. New functions: `toggleOverview()`, `closeOverview()`, `_ovBuildGrid()`, `_ovCountObjects()`, `_ovCardClick()`. Card click is atomic: `closeOverview()` + `loadPage(n)` in one call. Lazy IntersectionObserver per card reuses the 001a `thumbUrl()` + IO pattern (no new server endpoint; `/page/{n}` hot path untouched). `#ztb-chip-overview` in top bar unstubbed — now calls `toggleOverview()`. Esc handler updated: overview takes priority over zen (overview → close overview; zen → exit zen; else → default). F12 keydown registered. 6 discipline group label colors: site=green, plan=blue, elev=amber, section=purple, detail=cyan, none=gray.

**Why:** INV-002b is the second and final sprint of the 002 sub-series (Zen chrome upgrade). 002a delivered the shared top bar chrome. 002b delivers the Overview spatial map that the `#ztb-chip-overview` stub in 002a was reserved for. Together, 001a/b/c + 002a/b complete the Zen Mode feature set: focus-mode distraction-free canvas + palette jump + friction polish + top bar chrome + spatial sheet overview. Approach C (standalone, no coupling to Zen Mode's existing `toggleZen()`) was chosen per the invent doc recommendation v2 — additive, non-breaking, easy to test.

**Files touched:**
- `proto/ui.html`: +~135 LOC — `#overview-content` HTML block, `_OV_GROUPS` config (6 discipline groups), `toggleOverview` + `closeOverview` + `_ovBuildGrid` + `_ovCountObjects` + `_ovCardClick` + IntersectionObserver lazy thumb load; F12 hotkey; Esc priority guard; `#ztb-chip-overview` unstubbed
- `proto/static/css/app.css`: +~50 LOC — `.overview-content` grid (replaces canvas at top:40), `body.overview` hide rules (canvas/ribbon/panels/status/HUDs), `.ov-group` + `.ov-card` + `.ov-thumb`, 6 discipline group label colors
- `proto/e2e_ui_test.py`: +~80 LOC — `_test_inv_overview_mode()` with 9 sub-checks + `PHASE_INV_OVERVIEW_OK` marker registered in pipeline

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_OVERVIEW_OK 9/9 PASS (initial: cardClickExitOverview + cardClickSetCurPage FAIL
  because test PDF had <3 pages so data-page="3" selector returned null; surgical retry using
  first available card + direct _ovCardClick(targetPage) → 9/9 PASS)
  PHASE_INV_ZEN_V2_OK 9/9 + PHASE_INV_ZEN_OK 10/10 + PHASE_INV_PALETTE_OK 10/10 +
  PHASE_INV_POLISH_001C_OK 5/5 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_INV_OVERVIEW_OK 9/9; ANNOT_OK / PERSIST_OK / REAL_OK all PASS
  Pre-existing non-regressions unchanged: HT8C 3/5, HT8D1 8/9, HT10 8/10, HT12H 4/5, I_D 7/8
TEST-H: SKIPPED — 002b is additive NEW MODE, doesn't touch measurement / canvas drawing;
  9 sub-checks cover entry (F12 hotkey), exit (Esc/chip), atomic page-sync, DOM render, lazy IO;
  thumb-cache pattern reuses 001a (already journey-tested). Per AGENTS.md no-test rationale applies.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — UNCHANGED (no server edit; reused existing `/thumb` via `thumbUrl()`)
- ✅ `.bmaplan` schema — UNCHANGED
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Layer model: no name-based calculation introduced

**Known gaps / follow-ups:**
- 001a/b/c + 002a/b Zen Mode suite now complete; next options: (a) hook Help → คู่มือ in `#zen-topbar` to `/static/docs/`; (b) `ZEN_MENU_ITEMS` refactor (deferred from 002a); (c) F12 Overview onboarding toast (first-entry hint); (d) resume invent-queued backlog (Mobile/iPad rewrite)

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

<!-- sessions before 2026-05-19 INV-002a are archived to docs/archive/log-2026-05-19.md (001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish + 002a Zen top bar) and docs/archive/log-2026-05-18.md (earlier) -->
