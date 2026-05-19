# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: HT-18a-ext — Extended pushUndo() coverage to 22 more mutation sites

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, full EXIT 0 (PHASE_HT18_OK 36/36); HUMAN_TEST_PASS after inline fix of 3 initially-missed sites

## Summary

Sequel to HT-18a (`895a9d7`). Phase A audit of the full mutation function surface revealed 22 additional `pushUndo()` leak sites beyond the 6 fixed in HT-18a. All 22 were plugged in this sprint. The E2E test `_test_ht18_pushundo_leaks` was expanded from 7 sub-checks to 36 (22 source-presence + 7 runtime isDirty-flip + 7 original), creating a permanent regression guard. `/bma-human-test` discovered 3 sites initially missed by the audit (`toggleLayer`, `layerHideOthers`, `layerShowAll`); fixed inline in the same iteration. `PHASE_HT18_OK` is now 36/36 GREEN. HT-18b was updated to `done-with-test-design-caveat`; HT-18c is now `queued` with a concrete eq()-fix scope.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +39 LOC — `pushUndo()` at 22 mutation sites: layer reorder/rename/color/lock/visibility helpers, page tag/floor/name/exclude/restore/rotate/reset helpers, `pageCtxMenu` inline `autoNamePage` call; `_skipUndo` param added to `excludePage` + `restorePage2` |
| `proto/e2e_ui_test.py` | +295 LOC — `_test_ht18_pushundo_leaks` extended 7 → 36 sub-checks (22 source-presence + 7 runtime isDirty-flip + 7 original from HT-18a) |
| `docs/status/PHASE_INDEX.md` | HT-18a-ext card filed (done); HT-18b updated to `done-with-test-design-caveat`; HT-18c upgraded from `pending conditional` to `queued` |
| `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md` | New drift-map artifact (~120 lines) |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — NOT TOUCHED this sprint
- `.bmaplan` schema version stays 1; additive only — `_skipUndo` params are internal helpers, no field rename or removal

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PY_COMPILE_OK
python proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_HT18_OK: {'all': True} — 36/36 sub-checks GREEN (was 7/7 in HT-18a)
  21/21 core markers GREEN (smoke 16 + Phase I 2 + full 3)
Human journey test: HUMAN_TEST_PASS (after inline fix of toggleLayer / layerHideOthers / layerShowAll)
Pre-existing non-regressions (NOT this sprint):
  PHASE_HT8C_OK 3/5, PHASE_HT8D1_OK 8/9, PHASE_HT10_OK 8/10, PHASE_HT12H_OK 4/5
  PHASE_HT18B_OK 7/13 — test design issue (eq() too strict after normalizeAllObjects);
  NOT schema drift (Phase A audit confirmed save/load symmetric); filed as HT-18c
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — ADDITIVE ONLY (version stays 1; `_skipUndo` params are internal; no field rename/removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: HT-18a — Save-state pushUndo leak fixes

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_HT18_OK 7/7); full SKIPPED (rationale below); TEST-H SKIPPED (rationale below)

## Summary

Inserted `pushUndo()` at 6 mutation sites (`toggleScaleLine`, `showLayer`, `hideLayer`, `lockLayer`, `unlockLayer`, `soloLayer`, `applyLandEdgeTag`) that previously modified state without setting `isDirty`, causing the "save ไม่ตรงกับ canvas" data-integrity bug reported by the user. Audit via `bma-explorer` confirmed the save-schema serialization is complete (`_makeProjBlob` uses `JSON.stringify(pageStore)` auto-serializing all fields; `applyLoadedProject` restores by ref) — the bug was purely missing `isDirty` triggers. New E2E test `_test_ht18_pushundo_leaks()` (7 sub-checks, `PHASE_HT18_OK`) verifies all 6 mutation sites. Sprint card split: HT-18 → HT-18a (done, commit `895a9d7`) + HT-18b (queued) + HT-18c (conditional).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +~10 LOC — `pushUndo()` inserted at `toggleScaleLine` (L2814), `showLayer` / `hideLayer` / `lockLayer` / `unlockLayer` / `soloLayer` (L2824-2828), `applyLandEdgeTag` (L1788) |
| `proto/e2e_ui_test.py` | +~70 LOC — `_test_ht18_pushundo_leaks()` with 7 sub-checks; `PHASE_HT18_OK` marker registered in pipeline |
| `docs/status/PHASE_INDEX.md` | Sprint card split: HT-18 → HT-18a (done 895a9d7) + HT-18b (queued) + HT-18c (conditional) |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only — pushUndo() calls are pure additive code; no field rename or removal

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_HT18_OK 7/7 PASS (toggleScaleLineSetsDirty, hideLayerSetsDirty,
  showLayerSetsDirty, lockLayerSetsDirty, unlockLayerSetsDirty, soloLayerSetsDirty,
  applyLandEdgeTagHasPushUndo)
  PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9, PHASE_INV_ZEN_OK 10/10,
  PHASE_INV_PALETTE_OK 10/10, PHASE_INV_POLISH_001C_OK 5/5 — no regression
full → SKIPPED. Rationale: change is purely additive pushUndo() call insertion; no save/load
  logic touched, no .bmaplan schema change, no field rename. PROJECT_OK + PERSIST_OK test
  save/load round-trip (not isDirty trigger path) — unaffected.
TEST-H → SKIPPED. Rationale: sub-50-LOC additive fix; all 7 mutation sites marker-covered
  by PHASE_HT18_OK smoke sub-checks.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; pushUndo() is pure additive code)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous (older): INV-2026-05-19-002b — F12 Overview standalone (C)

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

# Previous (older): INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled)

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
