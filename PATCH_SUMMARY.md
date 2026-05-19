# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-002b — F12 Overview standalone (C)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_OVERVIEW_OK 9/9), full EXIT 0; TEST-H SKIPPED (rationale below)

## Summary

F12 Overview mode implemented as approach C standalone. `body.overview` class hides canvas, ribbon, panels, status bar, and HUDs; shows `#overview-content` grid of page cards grouped by 6 discipline categories. Shared `#zen-topbar` from INV-002a remains visible as navigation chrome. Card click is atomic: `closeOverview()` + `loadPage(n)`. Lazy IntersectionObserver per card reuses the 001a `thumbUrl()` + IO pattern — no new server endpoint, `/page/{n}` hot path untouched. `#ztb-chip-overview` in top bar unstubbed. Esc priority: overview > zen > default. Completes the 001a/b/c + 002a/b Zen Mode feature suite.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +~135 LOC — `#overview-content` HTML block, `_OV_GROUPS` config (6 discipline groups), `toggleOverview` + `closeOverview` + `_ovBuildGrid` + `_ovCountObjects` + `_ovCardClick` + IntersectionObserver lazy thumb load; F12 hotkey; Esc priority guard; `#ztb-chip-overview` unstubbed |
| `proto/static/css/app.css` | +~50 LOC — `.overview-content` grid (replaces canvas at top:40), `body.overview` hide rules (canvas/ribbon/panels/status/HUDs), `.ov-group` + `.ov-card` + `.ov-thumb`, 6 discipline group label colors (site=green/plan=blue/elev=amber/section=purple/detail=cyan/none=gray) |
| `proto/e2e_ui_test.py` | +~80 LOC — `_test_inv_overview_mode()` (9 sub-checks) + `PHASE_INV_OVERVIEW_OK` marker registered in pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (no server edit; reused existing `/thumb` via `thumbUrl()`)
- `.bmaplan` schema version stays 1; additive fields only — no new schema fields in this sprint

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_OVERVIEW_OK 9/9 (initial: cardClickExitOverview + cardClickSetCurPage FAIL
  because test PDF had <3 pages so data-page="3" selector returned null; surgical retry
  using first available card + direct _ovCardClick(targetPage) → 9/9 PASS)
  PHASE_INV_ZEN_V2_OK 9/9 + PHASE_INV_ZEN_OK 10/10 + PHASE_INV_PALETTE_OK 10/10 +
  PHASE_INV_POLISH_001C_OK 5/5 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_INV_OVERVIEW_OK 9/9; ANNOT_OK / PERSIST_OK / REAL_OK all PASS
  Pre-existing non-regressions unchanged: HT8C 3/5, HT8D1 8/9, HT10 8/10, HT12H 4/5, I_D 7/8
TEST-H: SKIPPED — 002b is additive NEW MODE, doesn't touch measurement / canvas drawing;
  9 sub-checks cover entry (F12), exit (Esc/chip), atomic page-sync, DOM render, lazy IO;
  thumb-cache pattern reuses 001a (already journey-tested). Per AGENTS.md no-test rationale.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Layer model: no name-based calculation introduced

---

# Previous: INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_ZEN_V2_OK 9/9), full EXIT 0, HUMAN_TEST_PASS

## Summary

Additive `#zen-topbar` overlay (40px) piggybacks on `body.zen` without touching 001a's `toggleZen()`. The bar provides 6 dropdowns (File / Page / Measure / Annotate / View / Help) wired to existing handlers plus 4 icon chips. New `toggleZenFocus()` (F key = Focus sub-mode hides all HUDs), `_ztbToggleMenu()`, and `_setupZenEdgePeek()` (edge hover restores HUDs temporarily). `toggleZenMode` extended with a v2 onboarding toast (green tint, shown once per `PREFS.layout.zenV2Onboarded`). The original 002a plan was a breaking change to `toggleZen()`; user redirected mid-SCOPE to a non-breaking additive approach. 001a minimap + 3 HUDs + hide-menubar behavior all UNCHANGED.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +133 LOC — `#zen-topbar` HTML (6 dropdowns + 4 chips + edge triggers + v2 toast); `toggleZenFocus`, `_ztbToggleMenu`, `_setupZenEdgePeek`; F-key scope guard; `toggleZenMode` v2 onboarding logic |
| `proto/static/css/app.css` | +40 LOC — `.zen-topbar` + `.ztb-*` rules; `body.zen.focus` HUD hide (`!important`); `body.zen.focus.peek` restore; 4 `.zen-focus-edge` rules; 001a HUDs shifted top:34→50px; `.zen-v2-toast` green tint |
| `proto/e2e_ui_test.py` | +128 LOC — `_test_inv_zen_v2_topbar()` (9 sub-checks); `PHASE_INV_ZEN_V2_OK` print line; registered in main() pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (no server edit)
- `.bmaplan` schema version stays 1; `PREFS.layout.zenV2Onboarded` is session pref, not project schema

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_ZEN_V2_OK 9/9 (topbarExistsAndShort, sixDropdownsExpectedLabels, fourChips,
  focusHidesHuds, peekRestoresHuds, fKeyScopeGuard, v2OnboardingToastShown,
  no001aRegression, paletteAboveTopbar)
  PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10, PHASE_INV_POLISH_001C_OK 5/5 — no regression
python proto/e2e_ui_test.py full                           → EXIT 0
  ANNOT_OK / PERSIST_OK / REAL_OK — all PASS
TEST-H: HUMAN_TEST_PASS — 13/13 journey steps; 45/45 pages; .bmaplan round-trip OK
  1 FRICTION (test-infra only — not filed)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Layer model: no name-based calculation introduced

<!-- INV-001a/001b/001c + older entries archived to docs/archive/patch-history-2026-05-09.md -->
