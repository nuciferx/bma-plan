# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix

Branch: main

Date: 2026-05-20

## Outcome: PASS — Right panel is now always recoverable after Zen Mode. F11 reliably exits Zen, F9/F10 toggle panels, restore tab no longer depends on a dead CSS selector. Full E2E EXIT 0, 101 _OK markers. NEW BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN.

## Summary

Defensive fix for a user-reported bug where the right-panel restore tab (`#rp-restore-tab`) disappeared after Zen Mode exit, making the right panel irrecoverable. Root cause: native-browser F11 fullscreen could collide with the app's F11 `!anyModal && !mPts.length` guard, leaving `body.zen` stuck and the CSS rule `body.zen .panel-restore-tab{display:none}` hiding the tab. Additionally, the restore-tab visibility CSS used a dead sibling combinator (`#right-panel.collapsed~#workspace #rp-restore-tab`) that never matched because workspace precedes panel in DOM. Fix is defensive: F11 always calls `preventDefault()`; F9/F10 keyboard recovery added; dead CSS selector replaced with `:has()`.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | F11 handler: unconditional `preventDefault()` + widened exit condition (`body.zen \|\| (!anyModal && !mPts.length)`); F9→`toggleLeftPanel` + F10→`toggleRightPanel` added |
| `proto/static/css/app.css` | Dead `#right-panel.collapsed~#workspace #rp-restore-tab` rule replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`; attribute fallback + zen/overview overrides kept |
| `proto/e2e_ui_test.py` | `_test_bug_zen_exit_rp_restore` (6 sub-checks) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive only (untouched)

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py            → PASS
proto/e2e_ui_test.py full                                   → EXIT 0
  101 _OK markers, 0 E2E_FAIL
  NEW: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks:
       inZen, zenExitedMidDraw, f10Toggled, tabVisibleWhenCollapsed,
       tabHiddenInZen, tabVisibleAfterZenExit)
  CACHE_OK, MAIN_UI_OK (cssLinkPresent + cssVarLoaded true) confirm CSS serves
  All prior 100 markers retained. Zero regression.
  Static-asset safety: NO_BOM on app.css. UI_REGRESSION_PASS.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3

Branch: main

Date: 2026-05-20

## Outcome: PASS — Page-scoped layer is now the single authoritative source for render/hit/visibility/lock. Site-plan overlap bug fixed. Full E2E EXIT 0, 100 _OK markers. NEW INV_LAYER_L1/L2/L3_OK GREEN.

## Summary

Three-commit layer-model rebuild resolving a user-reported bug where objects on ผังบริเวณ (site plan) pages landed in the wrong layer and overlapped with no way to separate or toggle them. Root cause: two competing layer systems coexisted — page-scoped `pageStore[n].layers` (authoritative by design) vs. legacy global `areaTypeLayer`/`layerVis`/`layerLock` (still read by render/hit paths). Site objects with `areaType="room"` collapsed to slug `"sub_area"` which does not exist in the site preset, producing `layerId = undefined`. L1 establishes slug-guarantee + new render/hit helpers. L2 adds Bluebeam-style reassign-layer UI. L3 demotes global maps to a non-authoritative synced mirror — page-scoped authority proved by E2E (page locked + global unlocked → app follows page).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | Layer helpers (`validLayerSlugForPage`, `getObjectLayerSlug`, `_slugVisible`, `_slugLocked`, `_objLayerVisible`, `_objLayerLocked`); slug assignment at object creation; render/hit/label/lock-gate paths updated (L1); `reassignSelectedObjectLayer` + Layer `<select>` in properties panels (L2); global `layerVis`/`layerLock` demoted to mirror role (L3) |
| `proto/e2e_ui_test.py` | +3 test functions (`_test_inv_layer_l1/l2/l3`) + 3 markers + HT8D5A repointed |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `layerSlug`/`layerId` fields already existed; additive only

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py  → PASS
proto/e2e_ui_test.py full                         → EXIT 0
  100 _OK markers, 0 E2E_FAIL
  NEW: INV_LAYER_L1_OK GREEN
  NEW: INV_LAYER_L2_OK GREEN
  NEW: INV_LAYER_L3_OK GREEN (page locked + global unlocked → app follows page)
  HT8D5A all:True restored
  Pre-existing cosmetic all:False markers (HT8C/HT8D1/HT10/HT12H/PHASE_I_D) — unchanged
  Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`layerSlug`/`layerId` already existed; no renames; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- Older entries archived to docs/archive/patch-history-2026-05-09.md -->
