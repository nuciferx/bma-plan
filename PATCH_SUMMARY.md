# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled)

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

---

# Previous: INV-2026-05-19-001c — Zen+Palette FRICTION polish (HT-Z-1 + HT-Z-2 + HT-Z-3 bundle)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_POLISH_001C_OK 5/5), full EXIT 0

## Summary

Polish sprint clearing all 3 FRICTION findings from the 001a/001b human-test journey. `_zenSyncHud()` now reads page names directly from `pageNames[curPage]` (HT-Z-1 timing fix) and colors the Scale chip amber when scale is auto-unverified or absent (HT-Z-2 visual fix). `filterPalette()` empty branch appends a Thai-language hint when a Thai tag word is typed but no pages are tagged yet (HT-Z-3 discoverability fix). ~20 LOC total across two files. Completes the Zen+Palette feature trilogy from idea `2026-05-19-01-36`.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | ~15 LOC — `_zenSyncHud()` direct page-name read + amber scale chip; `filterPalette()` Thai-tag empty-state hint |
| `proto/e2e_ui_test.py` | +65 LOC — `_test_inv_polish_001c` (5 sub-checks), `PHASE_INV_POLISH_001C_OK` marker |

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_POLISH_001C_OK 5/5 (hudReadsPageNamesDirectly, unverifiedScaleAmber,
  manualScaleNotAmber, thaiTagHintShown, hintAbsentWhenTaggedOrNoThai)
  PHASE_INV_ZEN_OK 10/10 + PHASE_INV_PALETTE_OK 10/10 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
TEST-H: SKIPPED — sub-200-LOC polish; all changed branches covered by PHASE_INV_POLISH_001C_OK
```

<!-- INV-001a/001b Zen Mode + Command Palette + older entries archived to docs/archive/patch-history-2026-05-09.md -->
